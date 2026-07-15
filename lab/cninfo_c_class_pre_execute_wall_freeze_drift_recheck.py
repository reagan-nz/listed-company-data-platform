"""
CNINFO C-class — Pre-EXECUTE 墙冻结漂移复核 / seal（离线 · C-FM-07）。

在 C-FM-06（pre-EXECUTE safe snapshot wall freeze）之上，补齐：
  1) FM-01..06 gate battery 只读聚合（含 FM-06 墙 gate JSON）
  2) C-FM-06 冻结产物存在性（MOCK8 矩阵 / 指纹 / battery / 人批包）
  3) 指纹漂移复核：exclusion + wall 重算 SHA256 对齐冻结值（不覆盖 MOCK8）
  4) EXECUTE hold seal：execute=false · approved=false · KEEP_EXECUTE_FALSE
  5) protected_output_roots.csv 注册一致性（MOCK3–9 · AUTH1）

禁止：CNINFO live · production EXECUTE · 覆盖权威 dual-layer 索引 ·
      覆盖 MOCK8 冻结墙 · verified 声称 · 翻转 approved_for_snapshot_rebuild。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence, Tuple

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    PROTECTED_ROOTS_CSV_REL,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_safe_erad_audit_write_path,
    is_allowed_mock_test_cleanup_path,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
)
from cninfo_c_class_pre_execute_safe_snapshot_wall import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM06_MOCK_ROOT_REL,
    EXCLUSION_UNIVERSE_CSV_REL,
    WallPaths,
    build_dual_layer_qa_freeze_rows,
    build_exclusion_universe_freeze_rows,
    build_execute_wall_rows,
    build_fm_gate_battery_rows as build_fm01_to_05_battery_rows,
    build_protected_csv_registry_rows as build_fm06_protected_csv_rows,
    fingerprint_wall_matrix,
    load_csv_rows,
    load_json,
    load_protected_root_rows,
)

TASK_ID = "C-FM-07"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm07_pre_execute_wall_freeze_drift_recheck"
)

FM01_GATE_JSON_REL = (
    "outputs/validation/cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.json"
)
FM02_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json"
)
FM03_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json"
)
FM04_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.json"
)
FM05_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_cross_fm_mock_cohort_integrity_20260715.json"
)
FM06_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_safe_snapshot_wall_20260715.json"
)

FM06_WALL_MATRIX_REL = f"{FM06_MOCK_ROOT_REL}/wall_matrix.csv"
FM06_WALL_FINGERPRINT_REL = f"{FM06_MOCK_ROOT_REL}/wall_fingerprint.json"
FM06_EXCLUSION_FP_REL = f"{FM06_MOCK_ROOT_REL}/exclusion_universe_fingerprint.json"
FM06_BATTERY_REL = f"{FM06_MOCK_ROOT_REL}/fm_gate_battery.json"
FM06_PACKET_REL = f"{FM06_MOCK_ROOT_REL}/human_approval_packet.json"

# C-FM-06 冻结指纹常量（漂移复核锚点）
FROZEN_WALL_FP_SHA256 = (
    "30ff8a3b3841aec0ac21374fcde0ad947fc84227f6e52b3828067d15b3c01ca3"
)
FROZEN_EXCLUSION_FP_SHA256 = (
    "e305e275b4b8e4e28ccd11a396cda5b93c6a3c99925a2956cba79386a08aa2ac"
)

REQUIRED_PROTECTED_ROOT_IDS = (
    "C-ROOT-MOCK3",
    "C-ROOT-MOCK4",
    "C-ROOT-MOCK5",
    "C-ROOT-MOCK6",
    "C-ROOT-MOCK7",
    "C-ROOT-MOCK8",
    "C-ROOT-MOCK9",
    "C-ROOT-AUTH1",
)

DRIFT_MATRIX_FIELDS = [
    "check_id",
    "layer",
    "path",
    "expected",
    "observed",
    "ok",
    "notes",
]


@dataclass(frozen=True)
class DriftRecheckPaths:
    """只读输入与隔离写根路径规格。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    fm05_gate_json_rel: str = FM05_GATE_JSON_REL
    fm06_gate_json_rel: str = FM06_GATE_JSON_REL
    fm06_mock_root_rel: str = FM06_MOCK_ROOT_REL
    fm06_wall_matrix_rel: str = FM06_WALL_MATRIX_REL
    fm06_wall_fingerprint_rel: str = FM06_WALL_FINGERPRINT_REL
    fm06_exclusion_fp_rel: str = FM06_EXCLUSION_FP_REL
    fm06_battery_rel: str = FM06_BATTERY_REL
    fm06_packet_rel: str = FM06_PACKET_REL
    exclusion_universe_csv_rel: str = EXCLUSION_UNIVERSE_CSV_REL
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    output_root_rel: str = DEFAULT_MOCK_OUTPUT_ROOT_REL


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: str, *, base_dir: str = BASE_DIR) -> str:
    if not os.path.isabs(path):
        return path.replace("\\", "/")
    return os.path.relpath(path, base_dir).replace("\\", "/")


def _abs(path: str, *, base_dir: str = BASE_DIR) -> str:
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(base_dir, path))


def assert_drift_recheck_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """漂移复核产物写根：必须 validation/_mock_*，并拒绝权威 dual-layer 与 MOCK8。"""
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    out_rel = _rel(out, base_dir=base_dir).rstrip("/")
    fm06_rel = FM06_MOCK_ROOT_REL.rstrip("/")
    if out_rel == fm06_rel or out_rel.startswith(fm06_rel + "/"):
        raise RuntimeError(
            "C_FM07_MUST_NOT_OVERWRITE_FM06_WALL: "
            f"output_root={out_rel} overlaps frozen MOCK8={fm06_rel}"
        )
    return out


def _row(
    *,
    check_id: str,
    layer: str,
    path: str = "",
    expected: str = "",
    observed: str = "",
    ok: bool = False,
    notes: str = "",
) -> Dict[str, str]:
    return {
        "check_id": check_id,
        "layer": layer,
        "path": path,
        "expected": expected,
        "observed": observed,
        "ok": "yes" if ok else "no",
        "notes": notes or ("ok" if ok else "fail"),
    }


def build_fm01_to_06_gate_battery_rows(
    *,
    fm01: Dict[str, Any],
    fm02: Dict[str, Any],
    fm03: Dict[str, Any],
    fm04: Dict[str, Any],
    fm05: Dict[str, Any],
    fm06: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..06 既有 gate 只读聚合（不重跑；含 FM-06 墙 gate）。"""
    rows, checks = build_fm01_to_05_battery_rows(
        fm01=fm01, fm02=fm02, fm03=fm03, fm04=fm04, fm05=fm05
    )
    # 去掉 FM-01..05 汇总行，改写为 FM-01..06 汇总
    rows = [r for r in rows if r.get("check_id") != "fm01_to_05_battery_all_pass"]
    checks.pop("fm01_to_05_battery_all_pass", None)

    gate = str(fm06.get("gate") or "").strip()
    cninfo = fm06.get("cninfo_calls", None)
    execute = fm06.get("execute_production_snapshot_rebuild", None)
    approved = fm06.get("approved_for_snapshot_rebuild", None)
    ok = (
        gate == "PASS_OFFLINE"
        and cninfo == 0
        and execute is False
        and approved is False
    )
    rows.append(
        _row(
            check_id="fm06_pre_execute_safe_snapshot_wall",
            layer="fm_gate_battery",
            path="fm06_pre_execute_safe_snapshot_wall",
            expected="gate=PASS_OFFLINE;cninfo=0;execute=false;approved=false",
            observed=(
                f"gate={gate};cninfo={cninfo};execute={execute};approved={approved}"
            ),
            ok=ok,
            notes="ok" if ok else "fm06_gate_not_pass",
        )
    )
    checks["fm06_pre_execute_safe_snapshot_wall"] = ok

    prior_ok = all(
        checks.get(k)
        for k in (
            "fm01_isolated_dryrun_repro",
            "fm02_isolated_validation_cohorts",
            "fm03_harvest_exclusion_dual_layer",
            "fm04_ledger_resume_lineage",
            "fm05_cross_fm_mock_cohort_integrity",
            "fm06_pre_execute_safe_snapshot_wall",
        )
    )
    rows.append(
        _row(
            check_id="fm01_to_06_battery_all_pass",
            layer="fm_gate_battery",
            expected="all_prior_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/6",
            ok=prior_ok,
            notes="ok" if prior_ok else "battery_incomplete",
        )
    )
    checks["fm01_to_06_battery_all_pass"] = prior_ok
    return rows, checks


def build_fm06_artifact_presence_rows(
    *,
    paths: DriftRecheckPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """C-FM-06 MOCK8 冻结产物存在性。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    specs = [
        ("fm06_mock_root_exists", paths.fm06_mock_root_rel, "dir"),
        ("fm06_wall_matrix_exists", paths.fm06_wall_matrix_rel, "file"),
        ("fm06_wall_fingerprint_exists", paths.fm06_wall_fingerprint_rel, "file"),
        ("fm06_exclusion_fp_exists", paths.fm06_exclusion_fp_rel, "file"),
        ("fm06_battery_exists", paths.fm06_battery_rel, "file"),
        ("fm06_packet_exists", paths.fm06_packet_rel, "file"),
    ]
    for check_id, rel, kind in specs:
        abs_path = _abs(rel, base_dir=base_dir)
        present = os.path.isdir(abs_path) if kind == "dir" else os.path.isfile(abs_path)
        rows.append(
            _row(
                check_id=check_id,
                layer="fm06_artifact_presence",
                path=rel,
                expected=f"{kind}_present",
                observed=f"present={present}",
                ok=present,
            )
        )
        checks[check_id] = present

    root_abs = _abs(paths.fm06_mock_root_rel, base_dir=base_dir)
    isolated = is_allowed_mock_test_cleanup_path(root_abs, base_dir=base_dir)
    rows.append(
        _row(
            check_id="fm06_mock_root_isolated",
            layer="fm06_artifact_presence",
            path=paths.fm06_mock_root_rel,
            expected="isolated_mock",
            observed=f"isolated={isolated}",
            ok=isolated,
        )
    )
    checks["fm06_mock_root_isolated"] = isolated

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="fm06_artifact_presence_all_pass",
            layer="fm06_artifact_presence",
            expected="mock8_freeze_artifacts_present",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["fm06_artifact_presence_all_pass"] = all_ok
    return rows, checks


def recompute_wall_fingerprints(
    *,
    probe_output_root_rel: str,
    exclusion_csv_rel: str = EXCLUSION_UNIVERSE_CSV_REL,
    protected_csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, str]]]:
    """
    重算 C-FM-06 墙指纹（不写 MOCK8）。

    使用与 C-FM-06 相同的五层 builder；probe 根仅用于 execute_wall mock 抽检。
    """
    wall_paths = WallPaths(
        exclusion_universe_csv_rel=exclusion_csv_rel,
        protected_roots_csv_rel=protected_csv_rel,
        output_root_rel=probe_output_root_rel,
    )
    fm01 = load_json(_abs(wall_paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(wall_paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(wall_paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(wall_paths.fm04_gate_json_rel, base_dir=base_dir))
    fm05 = load_json(_abs(wall_paths.fm05_gate_json_rel, base_dir=base_dir))

    bat_rows, _ = build_fm01_to_05_battery_rows(
        fm01=fm01, fm02=fm02, fm03=fm03, fm04=fm04, fm05=fm05
    )
    excl_rows, _, excl_fp = build_exclusion_universe_freeze_rows(
        csv_rel=wall_paths.exclusion_universe_csv_rel, base_dir=base_dir
    )
    dl_rows, _ = build_dual_layer_qa_freeze_rows(
        coverage_csv_rel=wall_paths.coverage_csv_rel,
        empty3_index_csv_rel=wall_paths.empty3_index_csv_rel,
        partial7_index_csv_rel=wall_paths.partial7_index_csv_rel,
        base_dir=base_dir,
    )
    # execute_wall 抽检用独立 probe 根，避免触碰 MOCK8
    wall_rows, _ = build_execute_wall_rows(
        mock_probe_rel=probe_output_root_rel, base_dir=base_dir
    )
    csv_rows, _ = build_fm06_protected_csv_rows(
        csv_rel=wall_paths.protected_roots_csv_rel, base_dir=base_dir
    )
    matrix = bat_rows + excl_rows + dl_rows + wall_rows + csv_rows
    wall_fp = fingerprint_wall_matrix(matrix)
    return wall_fp, excl_fp, matrix


def build_fingerprint_drift_rows(
    *,
    paths: DriftRecheckPaths,
    recomputed_wall_fp: Dict[str, Any],
    recomputed_excl_fp: Dict[str, Any],
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结指纹 vs 重算指纹漂移复核。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    frozen_wall_doc = {}
    frozen_excl_doc = {}
    wall_fp_path = _abs(paths.fm06_wall_fingerprint_rel, base_dir=base_dir)
    excl_fp_path = _abs(paths.fm06_exclusion_fp_rel, base_dir=base_dir)
    if os.path.isfile(wall_fp_path):
        frozen_wall_doc = load_json(wall_fp_path)
    if os.path.isfile(excl_fp_path):
        frozen_excl_doc = load_json(excl_fp_path)

    frozen_wall_sha = str(
        (frozen_wall_doc.get("fingerprint") or {}).get("fingerprint_sha256") or ""
    )
    frozen_excl_sha = str(
        (frozen_excl_doc.get("fingerprint") or {}).get("fingerprint_sha256")
        or (frozen_wall_doc.get("exclusion_universe_fingerprint") or {}).get(
            "fingerprint_sha256"
        )
        or ""
    )
    recomputed_wall_sha = str(recomputed_wall_fp.get("fingerprint_sha256") or "")
    recomputed_excl_sha = str(recomputed_excl_fp.get("fingerprint_sha256") or "")

    const_wall_ok = frozen_wall_sha == FROZEN_WALL_FP_SHA256
    checks["frozen_wall_sha_matches_constant"] = const_wall_ok
    rows.append(
        _row(
            check_id="frozen_wall_sha_matches_constant",
            layer="fingerprint_drift",
            path=paths.fm06_wall_fingerprint_rel,
            expected=FROZEN_WALL_FP_SHA256,
            observed=frozen_wall_sha or "missing",
            ok=const_wall_ok,
        )
    )

    const_excl_ok = frozen_excl_sha == FROZEN_EXCLUSION_FP_SHA256
    checks["frozen_exclusion_sha_matches_constant"] = const_excl_ok
    rows.append(
        _row(
            check_id="frozen_exclusion_sha_matches_constant",
            layer="fingerprint_drift",
            path=paths.fm06_exclusion_fp_rel,
            expected=FROZEN_EXCLUSION_FP_SHA256,
            observed=frozen_excl_sha or "missing",
            ok=const_excl_ok,
        )
    )

    wall_drift_ok = recomputed_wall_sha == FROZEN_WALL_FP_SHA256
    checks["recomputed_wall_sha_no_drift"] = wall_drift_ok
    rows.append(
        _row(
            check_id="recomputed_wall_sha_no_drift",
            layer="fingerprint_drift",
            expected=FROZEN_WALL_FP_SHA256,
            observed=recomputed_wall_sha or "missing",
            ok=wall_drift_ok,
            notes="ok" if wall_drift_ok else "wall_fingerprint_drift",
        )
    )

    excl_drift_ok = recomputed_excl_sha == FROZEN_EXCLUSION_FP_SHA256
    checks["recomputed_exclusion_sha_no_drift"] = excl_drift_ok
    rows.append(
        _row(
            check_id="recomputed_exclusion_sha_no_drift",
            layer="fingerprint_drift",
            expected=FROZEN_EXCLUSION_FP_SHA256,
            observed=recomputed_excl_sha or "missing",
            ok=excl_drift_ok,
            notes="ok" if excl_drift_ok else "exclusion_fingerprint_drift",
        )
    )

    # 冻结矩阵文件可指纹化（check_id 集合）
    matrix_path = _abs(paths.fm06_wall_matrix_rel, base_dir=base_dir)
    matrix_fp_ok = False
    matrix_sha = "missing"
    if os.path.isfile(matrix_path):
        matrix_rows = load_csv_rows(matrix_path)
        matrix_fp = fingerprint_wall_matrix(matrix_rows)
        matrix_sha = str(matrix_fp.get("fingerprint_sha256") or "")
        matrix_fp_ok = matrix_sha == FROZEN_WALL_FP_SHA256
    checks["frozen_matrix_file_sha_no_drift"] = matrix_fp_ok
    rows.append(
        _row(
            check_id="frozen_matrix_file_sha_no_drift",
            layer="fingerprint_drift",
            path=paths.fm06_wall_matrix_rel,
            expected=FROZEN_WALL_FP_SHA256,
            observed=matrix_sha,
            ok=matrix_fp_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="fingerprint_drift_all_pass",
            layer="fingerprint_drift",
            expected="zero_drift_vs_c_fm06_freeze",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["fingerprint_drift_all_pass"] = all_ok
    return rows, checks


def build_execute_hold_seal_rows(
    *,
    paths: DriftRecheckPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """EXECUTE hold seal：人批包与硬墙保持 KEEP_EXECUTE_FALSE。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    packet: Dict[str, Any] = {}
    packet_path = _abs(paths.fm06_packet_rel, base_dir=base_dir)
    if os.path.isfile(packet_path):
        packet = load_json(packet_path)

    execute = packet.get("execute_production_snapshot_rebuild", None)
    approved = packet.get("approved_for_snapshot_rebuild", None)
    hold = str(packet.get("hold_recommendation") or "").strip()
    human = packet.get("human_action_required_for_execute", None)
    verified_forbid = packet.get("verified_claim_forbidden", None)
    prod_forbid = packet.get("production_ready_claim_forbidden", None)

    execute_ok = execute is False
    checks["seal_execute_false"] = execute_ok
    rows.append(
        _row(
            check_id="seal_execute_false",
            layer="execute_hold_seal",
            path=paths.fm06_packet_rel,
            expected="false",
            observed=str(execute).lower() if execute is not None else "missing",
            ok=execute_ok,
        )
    )

    approved_ok = approved is False
    checks["seal_approved_false"] = approved_ok
    rows.append(
        _row(
            check_id="seal_approved_false",
            layer="execute_hold_seal",
            expected="false",
            observed=str(approved).lower() if approved is not None else "missing",
            ok=approved_ok,
        )
    )

    hold_ok = hold == "KEEP_EXECUTE_FALSE"
    checks["seal_hold_keep_execute_false"] = hold_ok
    rows.append(
        _row(
            check_id="seal_hold_keep_execute_false",
            layer="execute_hold_seal",
            expected="KEEP_EXECUTE_FALSE",
            observed=hold or "missing",
            ok=hold_ok,
        )
    )

    human_ok = human is True
    checks["seal_human_action_required"] = human_ok
    rows.append(
        _row(
            check_id="seal_human_action_required",
            layer="execute_hold_seal",
            expected="true",
            observed=str(human).lower() if human is not None else "missing",
            ok=human_ok,
        )
    )

    claims_ok = verified_forbid is True and prod_forbid is True
    checks["seal_verified_claims_forbidden"] = claims_ok
    rows.append(
        _row(
            check_id="seal_verified_claims_forbidden",
            layer="execute_hold_seal",
            expected="verified=true;production_ready=true",
            observed=(
                f"verified={verified_forbid};production_ready={prod_forbid}"
            ),
            ok=claims_ok,
        )
    )

    # 本包自身硬常量
    self_execute = False
    self_approved = False
    self_ok = self_execute is False and self_approved is False
    checks["seal_self_constants_hold"] = self_ok
    rows.append(
        _row(
            check_id="seal_self_constants_hold",
            layer="execute_hold_seal",
            expected="execute=false;approved=false",
            observed="execute=false;approved=false",
            ok=self_ok,
            notes="c_fm07_hard_constants",
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="execute_hold_seal_all_pass",
            layer="execute_hold_seal",
            expected="KEEP_EXECUTE_FALSE_sealed",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["execute_hold_seal_all_pass"] = all_ok
    return rows, checks, packet


def build_protected_csv_registry_rows(
    *,
    csv_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected_output_roots.csv 注册一致性（含 MOCK9）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    csv_rows = load_protected_root_rows(csv_rel, base_dir=base_dir)
    by_id = {
        str(r.get("root_id") or "").strip(): r
        for r in csv_rows
        if str(r.get("root_id") or "").strip()
    }

    for root_id in REQUIRED_PROTECTED_ROOT_IDS:
        present = root_id in by_id
        path = ""
        if present:
            path = str(by_id[root_id].get("path_pattern") or "").strip()
        check_id = f"protected_csv_has_{root_id}"
        rows.append(
            _row(
                check_id=check_id,
                layer="protected_csv_registry",
                path=path,
                expected="listed_in_protected_csv",
                observed=f"present={present}",
                ok=present,
                notes="ok" if present else "missing_root_id",
            )
        )
        checks[check_id] = present

    auth = by_id.get("C-ROOT-AUTH1") or {}
    auth_policy = str(auth.get("write_policy") or "").strip()
    auth_ok = auth_policy == "read_only_no_overwrite"
    checks["protected_csv_auth1_readonly"] = auth_ok
    rows.append(
        _row(
            check_id="protected_csv_auth1_readonly",
            layer="protected_csv_registry",
            path=str(auth.get("path_pattern") or ""),
            expected="write_policy=read_only_no_overwrite",
            observed=f"write_policy={auth_policy or 'missing'}",
            ok=auth_ok,
        )
    )

    mock8 = by_id.get("C-ROOT-MOCK8") or {}
    mock8_path = str(mock8.get("path_pattern") or "").strip().rstrip("/")
    mock8_ok = mock8_path == FM06_MOCK_ROOT_REL
    checks["protected_csv_mock8_path"] = mock8_ok
    rows.append(
        _row(
            check_id="protected_csv_mock8_path",
            layer="protected_csv_registry",
            path=mock8_path,
            expected=FM06_MOCK_ROOT_REL,
            observed=mock8_path or "missing",
            ok=mock8_ok,
        )
    )

    mock9 = by_id.get("C-ROOT-MOCK9") or {}
    mock9_path = str(mock9.get("path_pattern") or "").strip().rstrip("/")
    mock9_ok = mock9_path == DEFAULT_MOCK_OUTPUT_ROOT_REL
    checks["protected_csv_mock9_path"] = mock9_ok
    rows.append(
        _row(
            check_id="protected_csv_mock9_path",
            layer="protected_csv_registry",
            path=mock9_path,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=mock9_path or "missing",
            ok=mock9_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-9+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["protected_csv_registry_all_pass"] = all_ok
    return rows, checks


def write_drift_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=DRIFT_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in DRIFT_MATRIX_FIELDS})


def fingerprint_drift_matrix(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    """漂移复核矩阵结构指纹。"""
    ok_count = sum(1 for r in rows if r.get("ok") == "yes")
    fail_count = sum(1 for r in rows if r.get("ok") != "yes")
    layers: Dict[str, int] = {}
    for r in rows:
        layer = str(r.get("layer") or "")
        layers[layer] = layers.get(layer, 0) + 1
    canon = json.dumps(
        {
            "row_count": len(rows),
            "ok_count": ok_count,
            "fail_count": fail_count,
            "layers": dict(sorted(layers.items())),
            "check_ids": [str(r.get("check_id") or "") for r in rows],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return {
        "row_count": len(rows),
        "ok_count": ok_count,
        "fail_count": fail_count,
        "layers": layers,
        "fingerprint_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
    }


def build_drift_seal_packet(
    *,
    gate: str,
    layer_gates: Dict[str, str],
    frozen_wall_sha: str,
    frozen_excl_sha: str,
    recomputed_wall_sha: str,
    recomputed_excl_sha: str,
    generated_at: str,
) -> Dict[str, Any]:
    """漂移 seal 包：记录零漂移与 KEEP_EXECUTE_FALSE。"""
    return {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "packet_kind": "pre_execute_wall_freeze_drift_recheck_seal",
        "gate": gate,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "cninfo_calls": 0,
        "human_action_required_for_execute": True,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "layer_gates": layer_gates,
        "frozen_wall_fingerprint_sha256": frozen_wall_sha,
        "frozen_exclusion_fingerprint_sha256": frozen_excl_sha,
        "recomputed_wall_fingerprint_sha256": recomputed_wall_sha,
        "recomputed_exclusion_fingerprint_sha256": recomputed_excl_sha,
        "drift_detected": not (
            recomputed_wall_sha == frozen_wall_sha
            and recomputed_excl_sha == frozen_excl_sha
            and frozen_wall_sha == FROZEN_WALL_FP_SHA256
            and frozen_excl_sha == FROZEN_EXCLUSION_FP_SHA256
        ),
        "verified_claim_forbidden": True,
        "production_ready_claim_forbidden": True,
        "notes": (
            "本包仅复核 C-FM-06 墙冻结指纹零漂移并 seal KEEP_EXECUTE_FALSE；"
            "不覆盖 MOCK8；不翻转 approved_for_snapshot_rebuild；"
            "生产 snapshot EXECUTE 仍须独立人批。"
        ),
    }


def run_pre_execute_wall_freeze_drift_recheck(
    *,
    paths: DriftRecheckPaths = DriftRecheckPaths(),
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-07 pre-EXECUTE 墙冻结漂移复核（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_drift_recheck_output_root(
        paths.output_root_rel, base_dir=base_dir
    )

    fm01 = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))
    fm05 = load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir))
    fm06 = load_json(_abs(paths.fm06_gate_json_rel, base_dir=base_dir))

    bat_rows, bat_checks = build_fm01_to_06_gate_battery_rows(
        fm01=fm01, fm02=fm02, fm03=fm03, fm04=fm04, fm05=fm05, fm06=fm06
    )
    art_rows, art_checks = build_fm06_artifact_presence_rows(
        paths=paths, base_dir=base_dir
    )

    # 用本包 mock 根作 probe，避免写 MOCK8
    recomputed_wall_fp, recomputed_excl_fp, _matrix = recompute_wall_fingerprints(
        probe_output_root_rel=paths.output_root_rel,
        exclusion_csv_rel=paths.exclusion_universe_csv_rel,
        protected_csv_rel=paths.protected_roots_csv_rel,
        base_dir=base_dir,
    )
    drift_rows, drift_checks = build_fingerprint_drift_rows(
        paths=paths,
        recomputed_wall_fp=recomputed_wall_fp,
        recomputed_excl_fp=recomputed_excl_fp,
        base_dir=base_dir,
    )
    seal_rows, seal_checks, fm06_packet = build_execute_hold_seal_rows(
        paths=paths, base_dir=base_dir
    )
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )

    matrix = bat_rows + art_rows + drift_rows + seal_rows + csv_rows
    layer_gates = {
        "fm_gate_battery": (
            "PASS_OFFLINE" if all(bat_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "fm06_artifact_presence": (
            "PASS_OFFLINE" if all(art_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "fingerprint_drift": (
            "PASS_OFFLINE" if all(drift_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "execute_hold_seal": (
            "PASS_OFFLINE" if all(seal_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "protected_csv_registry": (
            "PASS_OFFLINE" if all(csv_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
    }
    overall = (
        "PASS_OFFLINE"
        if all(g == "PASS_OFFLINE" for g in layer_gates.values())
        else "FAIL_REVIEW_REQUIRED"
    )

    matrix_path = os.path.join(out_root, "drift_matrix.csv")
    write_drift_matrix_csv(matrix, matrix_path)
    fp = fingerprint_drift_matrix(matrix)
    fp_path = os.path.join(out_root, "drift_fingerprint.json")
    assert_safe_erad_audit_write_path(
        fp_path,
        base_dir=base_dir,
        allowed_audit_root_rel=paths.output_root_rel,
    )
    with open(fp_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
                "fingerprint": fp,
                "frozen_wall_fingerprint_sha256": FROZEN_WALL_FP_SHA256,
                "frozen_exclusion_fingerprint_sha256": FROZEN_EXCLUSION_FP_SHA256,
                "recomputed_wall_fingerprint": recomputed_wall_fp,
                "recomputed_exclusion_fingerprint": recomputed_excl_fp,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    battery_path = os.path.join(out_root, "fm_gate_battery.json")
    with open(battery_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fm01_gate": fm01.get("gate"),
                "fm02_gate": fm02.get("gate"),
                "fm03_gate": fm03.get("gate"),
                "fm04_gate": fm04.get("gate"),
                "fm05_gate": fm05.get("gate"),
                "fm06_gate": fm06.get("gate"),
                "fm07_gate": overall,
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    recomputed_wall_sha = str(recomputed_wall_fp.get("fingerprint_sha256") or "")
    recomputed_excl_sha = str(recomputed_excl_fp.get("fingerprint_sha256") or "")
    seal = build_drift_seal_packet(
        gate=overall,
        layer_gates=layer_gates,
        frozen_wall_sha=FROZEN_WALL_FP_SHA256,
        frozen_excl_sha=FROZEN_EXCLUSION_FP_SHA256,
        recomputed_wall_sha=recomputed_wall_sha,
        recomputed_excl_sha=recomputed_excl_sha,
        generated_at=generated_at,
    )
    seal_path = os.path.join(out_root, "drift_seal_packet.json")
    with open(seal_path, "w", encoding="utf-8") as fh:
        json.dump(seal, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    return {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "gate": overall,
        "layer_gates": layer_gates,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "fail_count": fail_count,
        "matrix_rows": len(matrix),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "fingerprint_path": _rel(fp_path, base_dir=base_dir),
        "fingerprint": fp,
        "battery_path": _rel(battery_path, base_dir=base_dir),
        "seal_packet_path": _rel(seal_path, base_dir=base_dir),
        "seal_packet": seal,
        "recomputed_wall_fingerprint": recomputed_wall_fp,
        "recomputed_exclusion_fingerprint": recomputed_excl_fp,
        "frozen_wall_fingerprint_sha256": FROZEN_WALL_FP_SHA256,
        "frozen_exclusion_fingerprint_sha256": FROZEN_EXCLUSION_FP_SHA256,
        "fm06_human_approval_packet": fm06_packet,
        "mock_root_is_isolated": is_allowed_mock_test_cleanup_path(
            out_root, base_dir=base_dir
        ),
        "inputs": {
            "fm01_gate_json": paths.fm01_gate_json_rel,
            "fm02_gate_json": paths.fm02_gate_json_rel,
            "fm03_gate_json": paths.fm03_gate_json_rel,
            "fm04_gate_json": paths.fm04_gate_json_rel,
            "fm05_gate_json": paths.fm05_gate_json_rel,
            "fm06_gate_json": paths.fm06_gate_json_rel,
            "fm06_mock_root": paths.fm06_mock_root_rel,
            "fm06_wall_fingerprint": paths.fm06_wall_fingerprint_rel,
            "exclusion_universe_csv": paths.exclusion_universe_csv_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
        },
    }
