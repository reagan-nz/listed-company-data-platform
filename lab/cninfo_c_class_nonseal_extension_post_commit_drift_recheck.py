"""
CNINFO C-class — 非 seal Cross-FM mock cohort 扩展 post-commit 漂移复核（离线 · C-FM-14）。

在 C-FM-13（non-seal cross-FM mock cohort extension）已 commit 且 EXECUTE 仍 human-held 之上，
补齐非 seal 能力（不新增 MOCK seal 层）：
  1) FM-01..05 + FM-12 + FM-13 gate battery 只读聚合
  2) C-FM-13 MOCK15 冻结产物存在性（矩阵 / 指纹 / registry / battery / packet）
  3) 扩展矩阵指纹零漂移：冻结 SHA256 对齐常量与 gate JSON（不覆盖 MOCK15）
  4) 冻结 mock 写隔离：MOCK3–15 拒绝；本任务 MOCK16 / ephemeral 放行
  5) harvest/exclusion dual-layer 一致性交叉指纹（FM-03）
  6) EXECUTE hold seal：KEEP_EXECUTE_FALSE · AWAITING · idle_not_required
  7) protected_output_roots.csv 注册一致性（含 MOCK16）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–15 / 权威 dual-layer 索引 ·
verified 声称 · 翻转 approved_for_snapshot_rebuild · 扩展 seal-chain。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Sequence, Tuple

from cninfo_c_class_cross_fm_mock_cohort_integrity import (  # noqa: E402
    build_mock_cohort_registry_rows,
    build_protected_write_guard_battery_rows,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    PROTECTED_ROOTS_CSV_REL,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_frozen_mock_cohort_write_forbidden,
    assert_safe_erad_audit_write_path,
    is_allowed_mock_test_cleanup_path,
    load_frozen_mock_cohort_roots,
    resolve_frozen_mock_cohort_root_id,
)
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    load_csv_rows,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
)
from cninfo_c_class_nonseal_cross_fm_mock_cohort_extension import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM13_MOCK_ROOT_REL,
    ExtensionPaths,
    build_extended_fingerprint_chain_rows,
    build_fm_gate_battery_rows as build_fm01_05_12_battery_rows,
    build_frozen_mock_isolation_rows as build_fm13_frozen_isolation_rows,
    build_harvest_exclusion_consistency_rows,
    build_protected_csv_registry_rows as build_fm13_protected_csv_rows,
    default_nonseal_cohort_specs,
    fingerprint_extension_matrix,
    load_json,
)

TASK_ID = "C-FM-14"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm14_nonseal_extension_post_commit_drift_recheck"
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
FM12_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_dryrun_fingerprint_lineage_isolation_20260715.json"
)
FM13_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_cross_fm_mock_cohort_extension_20260715.json"
)

FM13_EXTENSION_MATRIX_REL = f"{FM13_MOCK_ROOT_REL}/extension_matrix.csv"
FM13_EXTENSION_FINGERPRINT_REL = f"{FM13_MOCK_ROOT_REL}/extension_fingerprint.json"
FM13_REGISTRY_REL = f"{FM13_MOCK_ROOT_REL}/nonseal_mock_cohort_registry.json"
FM13_BATTERY_REL = f"{FM13_MOCK_ROOT_REL}/fm_gate_battery.json"
FM13_PACKET_REL = f"{FM13_MOCK_ROOT_REL}/extension_packet.json"

# C-FM-13 冻结扩展指纹常量（漂移复核锚点）
FROZEN_EXTENSION_FP_SHA256 = (
    "3d9354e2571b46b5d67787b43aada270882d827bf00d7f91f8d3154c6da5d8ff"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK16"
FROZEN_ROOT_IDS_MUST_BLOCK = (
    "C-ROOT-MOCK3",
    "C-ROOT-MOCK4",
    "C-ROOT-MOCK5",
    "C-ROOT-MOCK6",
    "C-ROOT-MOCK7",
    "C-ROOT-MOCK8",
    "C-ROOT-MOCK9",
    "C-ROOT-MOCK10",
    "C-ROOT-MOCK11",
    "C-ROOT-MOCK12",
    "C-ROOT-MOCK13",
    "C-ROOT-MOCK14",
    "C-ROOT-MOCK15",
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    "C-ROOT-AUTH1",
)

MATRIX_FIELDS = [
    "check_id",
    "layer",
    "cohort_id",
    "root_id",
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
    fm12_gate_json_rel: str = FM12_GATE_JSON_REL
    fm13_gate_json_rel: str = FM13_GATE_JSON_REL
    fm13_mock_root_rel: str = FM13_MOCK_ROOT_REL
    fm13_extension_matrix_rel: str = FM13_EXTENSION_MATRIX_REL
    fm13_extension_fingerprint_rel: str = FM13_EXTENSION_FINGERPRINT_REL
    fm13_registry_rel: str = FM13_REGISTRY_REL
    fm13_battery_rel: str = FM13_BATTERY_REL
    fm13_packet_rel: str = FM13_PACKET_REL
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    harvest_863_status_rel: str = (
        "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"
    )
    fm03_mock_root_rel: str = (
        "outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency"
    )
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


def _row(
    *,
    check_id: str,
    layer: str,
    cohort_id: str = "*",
    root_id: str = "",
    path: str = "",
    expected: str = "",
    observed: str = "",
    ok: bool = False,
    notes: str = "",
) -> Dict[str, str]:
    return {
        "check_id": check_id,
        "layer": layer,
        "cohort_id": cohort_id,
        "root_id": root_id,
        "path": path,
        "expected": expected,
        "observed": observed,
        "ok": "yes" if ok else "no",
        "notes": notes or ("ok" if ok else "fail"),
    }


def assert_fm14_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-14 写根：须 validation/_mock_*，不得覆盖 MOCK3–15（含 MOCK15），
    不得写权威 dual-layer 索引；允许本任务 MOCK16 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    out_rel = _rel(out, base_dir=base_dir).rstrip("/")
    fm13_rel = FM13_MOCK_ROOT_REL.rstrip("/")
    if out_rel == fm13_rel or out_rel.startswith(fm13_rel + "/"):
        raise RuntimeError(
            "C_FM14_MUST_NOT_OVERWRITE_FM13_EXTENSION: "
            f"output_root={out_rel} overlaps frozen MOCK15={fm13_rel}"
        )
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-14 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def load_protected_root_rows(
    csv_rel: str = PROTECTED_ROOTS_CSV_REL, *, base_dir: str = BASE_DIR
) -> List[Dict[str, str]]:
    path = _abs(csv_rel, base_dir=base_dir)
    with open(path, encoding="utf-8", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def build_fm01_05_12_13_gate_battery_rows(
    *,
    fm01: Dict[str, Any],
    fm02: Dict[str, Any],
    fm03: Dict[str, Any],
    fm04: Dict[str, Any],
    fm05: Dict[str, Any],
    fm12: Dict[str, Any],
    fm13: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12 + FM-13 既有 gate 只读聚合（跳过 seal FM06–11）。"""
    rows, checks = build_fm01_05_12_battery_rows(
        fm01=fm01, fm02=fm02, fm03=fm03, fm04=fm04, fm05=fm05, fm12=fm12
    )
    rows = [r for r in rows if r.get("check_id") != "fm01_05_12_battery_all_pass"]
    checks.pop("fm01_05_12_battery_all_pass", None)

    gate = str(fm13.get("gate") or "").strip()
    cninfo = fm13.get("cninfo_calls", None)
    execute = fm13.get("execute_production_snapshot_rebuild", None)
    approved = fm13.get("approved_for_snapshot_rebuild", None)
    seal_ext = fm13.get("seal_chain_extended", None)
    ok = (
        gate == "PASS_OFFLINE"
        and cninfo == 0
        and execute is False
        and approved is False
        and seal_ext is False
    )
    rows.append(
        _row(
            check_id="fm13_nonseal_cross_fm_mock_cohort_extension",
            layer="fm_gate_battery",
            cohort_id="fm13",
            expected=(
                "gate=PASS_OFFLINE;cninfo=0;execute=false;"
                "approved=false;seal_chain_extended=false"
            ),
            observed=(
                f"gate={gate};cninfo={cninfo};execute={execute};"
                f"approved={approved};seal_ext={seal_ext}"
            ),
            ok=ok,
            notes="ok" if ok else "fm13_gate_not_pass",
        )
    )
    checks["fm13_nonseal_cross_fm_mock_cohort_extension"] = ok

    prior_ok = all(checks.values()) if checks else False
    rows.append(
        _row(
            check_id="fm01_05_12_13_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_incl_fm13_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=prior_ok,
            notes="ok" if prior_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_13_battery_all_pass"] = prior_ok
    return rows, checks


def build_fm13_artifact_presence_rows(
    *,
    paths: DriftRecheckPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """C-FM-13 MOCK15 冻结产物存在性。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    specs = [
        ("fm13_mock_root_exists", paths.fm13_mock_root_rel, "dir"),
        ("fm13_extension_matrix_exists", paths.fm13_extension_matrix_rel, "file"),
        (
            "fm13_extension_fingerprint_exists",
            paths.fm13_extension_fingerprint_rel,
            "file",
        ),
        ("fm13_registry_exists", paths.fm13_registry_rel, "file"),
        ("fm13_battery_exists", paths.fm13_battery_rel, "file"),
        ("fm13_packet_exists", paths.fm13_packet_rel, "file"),
    ]
    for check_id, rel, kind in specs:
        abs_path = _abs(rel, base_dir=base_dir)
        present = os.path.isdir(abs_path) if kind == "dir" else os.path.isfile(abs_path)
        rows.append(
            _row(
                check_id=check_id,
                layer="fm13_artifact_presence",
                path=rel,
                expected=f"{kind}_present",
                observed=f"present={present}",
                ok=present,
            )
        )
        checks[check_id] = present

    root_abs = _abs(paths.fm13_mock_root_rel, base_dir=base_dir)
    isolated = is_allowed_mock_test_cleanup_path(root_abs, base_dir=base_dir)
    rows.append(
        _row(
            check_id="fm13_mock_root_isolated",
            layer="fm13_artifact_presence",
            path=paths.fm13_mock_root_rel,
            expected="isolated_mock",
            observed=f"isolated={isolated}",
            ok=isolated,
        )
    )
    checks["fm13_mock_root_isolated"] = isolated

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="fm13_artifact_presence_all_pass",
            layer="fm13_artifact_presence",
            expected="mock15_freeze_artifacts_present",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["fm13_artifact_presence_all_pass"] = all_ok
    return rows, checks


def recompute_extension_fingerprints(
    *,
    probe_output_root_rel: str,
    protected_csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    harvest_863_status_rel: str = (
        "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"
    ),
    base_dir: str = BASE_DIR,
) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """
    重算 C-FM-13 扩展矩阵指纹（不写 MOCK15）。

    使用与 C-FM-13 相同的七层 builder；probe 根仅用于 write-guard / frozen 抽检。
    """
    paths = ExtensionPaths(
        protected_roots_csv_rel=protected_csv_rel,
        harvest_863_status_rel=harvest_863_status_rel,
        output_root_rel=probe_output_root_rel,
    )
    specs = default_nonseal_cohort_specs()
    fm01 = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))
    fm05 = load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir))
    fm12 = load_json(_abs(paths.fm12_gate_json_rel, base_dir=base_dir))

    reg_rows, _ = build_mock_cohort_registry_rows(specs, base_dir=base_dir)
    fp_rows, _ = build_extended_fingerprint_chain_rows(
        specs, paths=paths, base_dir=base_dir
    )
    fr_rows, _ = build_fm13_frozen_isolation_rows(paths, base_dir=base_dir)
    he_rows, _ = build_harvest_exclusion_consistency_rows(paths, base_dir=base_dir)
    wg_rows, _ = build_protected_write_guard_battery_rows(
        mock_probe_rel=probe_output_root_rel, base_dir=base_dir
    )
    csv_rows, _ = build_fm13_protected_csv_rows(
        csv_rel=protected_csv_rel, base_dir=base_dir
    )
    bat_rows, _ = build_fm01_05_12_battery_rows(
        fm01=fm01, fm02=fm02, fm03=fm03, fm04=fm04, fm05=fm05, fm12=fm12
    )
    matrix = (
        reg_rows + fp_rows + fr_rows + he_rows + wg_rows + csv_rows + bat_rows
    )
    fp = fingerprint_extension_matrix(matrix)
    return fp, matrix


def build_fingerprint_drift_rows(
    *,
    paths: DriftRecheckPaths,
    recomputed_fp: Dict[str, Any],
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结扩展指纹 vs 重算指纹漂移复核。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    frozen_doc: Dict[str, Any] = {}
    fp_path = _abs(paths.fm13_extension_fingerprint_rel, base_dir=base_dir)
    if os.path.isfile(fp_path):
        frozen_doc = load_json(fp_path)

    frozen_sha = str(
        (frozen_doc.get("fingerprint") or {}).get("fingerprint_sha256") or ""
    )
    gate_doc: Dict[str, Any] = {}
    gate_path = _abs(paths.fm13_gate_json_rel, base_dir=base_dir)
    if os.path.isfile(gate_path):
        gate_doc = load_json(gate_path)
    gate_sha = str(
        (gate_doc.get("fingerprint") or {}).get("fingerprint_sha256") or ""
    )
    recomputed_sha = str(recomputed_fp.get("fingerprint_sha256") or "")

    const_ok = frozen_sha == FROZEN_EXTENSION_FP_SHA256
    checks["frozen_extension_sha_matches_constant"] = const_ok
    rows.append(
        _row(
            check_id="frozen_extension_sha_matches_constant",
            layer="fingerprint_drift",
            path=paths.fm13_extension_fingerprint_rel,
            expected=FROZEN_EXTENSION_FP_SHA256,
            observed=frozen_sha or "missing",
            ok=const_ok,
        )
    )

    gate_ok = gate_sha == FROZEN_EXTENSION_FP_SHA256
    checks["gate_json_sha_matches_constant"] = gate_ok
    rows.append(
        _row(
            check_id="gate_json_sha_matches_constant",
            layer="fingerprint_drift",
            path=paths.fm13_gate_json_rel,
            expected=FROZEN_EXTENSION_FP_SHA256,
            observed=gate_sha or "missing",
            ok=gate_ok,
        )
    )

    recompute_ok = recomputed_sha == FROZEN_EXTENSION_FP_SHA256
    checks["recomputed_extension_sha_no_drift"] = recompute_ok
    rows.append(
        _row(
            check_id="recomputed_extension_sha_no_drift",
            layer="fingerprint_drift",
            expected=FROZEN_EXTENSION_FP_SHA256,
            observed=recomputed_sha or "missing",
            ok=recompute_ok,
            notes="ok" if recompute_ok else "extension_fingerprint_drift",
        )
    )

    # 冻结矩阵文件结构指纹可复算
    matrix_path = _abs(paths.fm13_extension_matrix_rel, base_dir=base_dir)
    matrix_sha = ""
    matrix_ok = False
    if os.path.isfile(matrix_path):
        matrix_rows = load_csv_rows(matrix_path)
        matrix_fp = fingerprint_extension_matrix(matrix_rows)
        matrix_sha = str(matrix_fp.get("fingerprint_sha256") or "")
        matrix_ok = matrix_sha == FROZEN_EXTENSION_FP_SHA256
    checks["frozen_matrix_file_sha_no_drift"] = matrix_ok
    rows.append(
        _row(
            check_id="frozen_matrix_file_sha_no_drift",
            layer="fingerprint_drift",
            path=paths.fm13_extension_matrix_rel,
            expected=FROZEN_EXTENSION_FP_SHA256,
            observed=matrix_sha or "missing",
            ok=matrix_ok,
            notes="ok" if matrix_ok else "frozen_matrix_drift",
        )
    )

    raw_fail = recomputed_fp.get("fail_count")
    fail_ok = raw_fail is not None and int(raw_fail) == 0
    checks["recomputed_extension_fail_count_zero"] = fail_ok
    rows.append(
        _row(
            check_id="recomputed_extension_fail_count_zero",
            layer="fingerprint_drift",
            expected="fail_count=0",
            observed=f"fail_count={raw_fail}",
            ok=fail_ok,
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fingerprint_drift_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fingerprint_drift_all_pass",
            layer="fingerprint_drift",
            expected="fm13_extension_zero_drift",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "drift_detected",
        )
    )
    return rows, checks


def build_frozen_mock_isolation_rows(
    paths: DriftRecheckPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离 battery：MOCK3–15 拒绝 · MOCK16 放行。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    load_frozen_mock_cohort_roots.cache_clear()
    frozen = dict(load_frozen_mock_cohort_roots(base_dir=base_dir))

    for root_id in FROZEN_ROOT_IDS_MUST_BLOCK:
        prefix = frozen.get(root_id)
        exists = prefix is not None
        refused = False
        if prefix:
            try:
                assert_frozen_mock_cohort_write_forbidden(
                    prefix, allow_root_ids=(), base_dir=base_dir
                )
            except RuntimeError as exc:
                refused = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
        ok = exists and refused
        checks[f"frozen_block_{root_id}"] = ok
        rows.append(
            _row(
                check_id=f"frozen_block_{root_id}",
                layer="frozen_mock_isolation",
                root_id=root_id,
                path=_rel(prefix, base_dir=base_dir) if prefix else "",
                expected="write_refused",
                observed=f"listed={exists};refused={refused}",
                ok=ok,
                notes="ok" if ok else "freeze_guard_gap",
            )
        )

    mock16_prefix = frozen.get(THIS_TASK_ROOT_ID)
    mock16_listed = mock16_prefix is not None
    mock16_allowed = False
    if mock16_prefix:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock16_prefix,
                allow_root_ids=(THIS_TASK_ROOT_ID,),
                base_dir=base_dir,
            )
            mock16_allowed = True
        except RuntimeError:
            mock16_allowed = False
    checks["frozen_allow_mock16"] = mock16_listed and mock16_allowed
    rows.append(
        _row(
            check_id="frozen_allow_mock16",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=_rel(mock16_prefix, base_dir=base_dir) if mock16_prefix else "",
            expected="listed_and_allowed_when_in_allowlist",
            observed=f"listed={mock16_listed};allowed={mock16_allowed}",
            ok=mock16_listed and mock16_allowed,
            notes="ok" if mock16_listed and mock16_allowed else "mock16_allow_fail",
        )
    )

    out_ok = False
    out_detail = ""
    try:
        assert_fm14_output_root(paths.output_root_rel, base_dir=base_dir)
        out_ok = True
        out_detail = "allowed"
    except RuntimeError as exc:
        out_detail = str(exc)[:120]
    checks["frozen_output_root_allowed"] = out_ok
    rows.append(
        _row(
            check_id="frozen_output_root_allowed",
            layer="frozen_mock_isolation",
            path=paths.output_root_rel,
            expected="MOCK16_or_ephemeral_allowed",
            observed=out_detail,
            ok=out_ok,
        )
    )

    # MOCK15 即使在 allow MOCK16 时仍不可写
    mock15 = frozen.get("C-ROOT-MOCK15")
    mock15_still_frozen = False
    if mock15:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock15, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
            )
        except RuntimeError as exc:
            mock15_still_frozen = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock15_still_frozen"] = mock15_still_frozen
    rows.append(
        _row(
            check_id="mock15_still_frozen",
            layer="frozen_mock_isolation",
            root_id="C-ROOT-MOCK15",
            expected="fm13_mock15_not_writable_by_fm14",
            observed=f"refused={mock15_still_frozen}",
            ok=mock15_still_frozen,
            notes="ok" if mock15_still_frozen else "mock15_freeze_regressed",
        )
    )

    # seal 根仍冻结（抽样 MOCK8）
    mock8 = frozen.get("C-ROOT-MOCK8")
    seal_still_frozen = False
    if mock8:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock8, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
            )
        except RuntimeError as exc:
            seal_still_frozen = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["seal_mock8_still_frozen"] = seal_still_frozen
    rows.append(
        _row(
            check_id="seal_mock8_still_frozen",
            layer="frozen_mock_isolation",
            root_id="C-ROOT-MOCK8",
            expected="seal_chain_not_writable_by_fm14",
            observed=f"refused={seal_still_frozen}",
            ok=seal_still_frozen,
            notes="ok" if seal_still_frozen else "seal_freeze_regressed",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-15_blocked_MOCK16_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "frozen_isolation_fail",
        )
    )
    return rows, checks


def build_execute_hold_seal_rows(
    *,
    fm13: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """EXECUTE hold seal：不得因 awaiting 而 IDLE；不得翻转 approved。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    hold = str(fm13.get("hold_recommendation") or "")
    hold_ok = hold == "KEEP_EXECUTE_FALSE"
    checks["hold_keep_execute_false"] = hold_ok
    rows.append(
        _row(
            check_id="hold_keep_execute_false",
            layer="execute_hold_seal",
            expected="KEEP_EXECUTE_FALSE",
            observed=hold or "missing",
            ok=hold_ok,
        )
    )

    decision = str(fm13.get("decision_status") or "")
    decision_ok = decision == "AWAITING_HUMAN_EXECUTE_DECISION"
    checks["decision_awaiting_human"] = decision_ok
    rows.append(
        _row(
            check_id="decision_awaiting_human",
            layer="execute_hold_seal",
            expected="AWAITING_HUMAN_EXECUTE_DECISION",
            observed=decision or "missing",
            ok=decision_ok,
        )
    )

    idle_flag = fm13.get("idle_not_required_while_awaiting")
    idle_ok = idle_flag is True
    checks["idle_not_required_while_awaiting"] = idle_ok
    rows.append(
        _row(
            check_id="idle_not_required_while_awaiting",
            layer="execute_hold_seal",
            expected="true",
            observed=str(idle_flag),
            ok=idle_ok,
        )
    )

    ready_exec = fm13.get("ready_for_execute")
    ready_ok = ready_exec is False
    checks["ready_for_execute_false"] = ready_ok
    rows.append(
        _row(
            check_id="ready_for_execute_false",
            layer="execute_hold_seal",
            expected="false",
            observed=str(ready_exec),
            ok=ready_ok,
        )
    )

    approved = fm13.get("approved_for_snapshot_rebuild")
    approved_ok = approved is False
    checks["approved_still_false"] = approved_ok
    rows.append(
        _row(
            check_id="approved_still_false",
            layer="execute_hold_seal",
            expected="false",
            observed=str(approved),
            ok=approved_ok,
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["execute_hold_seal_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="execute_hold_seal_all_pass",
            layer="execute_hold_seal",
            expected="hold_continuity_while_awaiting",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    return rows, checks


def build_protected_csv_registry_rows(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected CSV：MOCK3–16 + AUTH1 注册一致性。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    csv_rows = load_protected_root_rows(csv_rel, base_dir=base_dir)
    by_id = {str(r.get("root_id") or ""): r for r in csv_rows}

    for root_id in REQUIRED_PROTECTED_ROOT_IDS:
        present = root_id in by_id
        checks[f"protected_csv_has_{root_id}"] = present
        rows.append(
            _row(
                check_id=f"protected_csv_has_{root_id}",
                layer="protected_csv_registry",
                root_id=root_id,
                path=csv_rel,
                expected="listed_in_protected_csv",
                observed="present" if present else "missing",
                ok=present,
                notes="ok" if present else "missing_root_id",
            )
        )

    auth = by_id.get("C-ROOT-AUTH1") or {}
    auth_ok = (auth.get("write_policy") or "") == "read_only_no_overwrite"
    checks["protected_csv_auth1_readonly"] = auth_ok
    rows.append(
        _row(
            check_id="protected_csv_auth1_readonly",
            layer="protected_csv_registry",
            root_id="C-ROOT-AUTH1",
            expected="write_policy=read_only_no_overwrite",
            observed=str(auth.get("write_policy") or ""),
            ok=auth_ok,
            notes="ok" if auth_ok else "auth_policy_drift",
        )
    )

    mock16 = by_id.get(THIS_TASK_ROOT_ID) or {}
    mock16_path = (mock16.get("path_pattern") or "").strip().rstrip("/")
    expected_path = DEFAULT_MOCK_OUTPUT_ROOT_REL
    mock16_ok = mock16_path.endswith(
        "_mock_c_fm14_nonseal_extension_post_commit_drift_recheck"
    ) or mock16_path == expected_path
    checks["protected_csv_mock16_path"] = mock16_ok
    rows.append(
        _row(
            check_id="protected_csv_mock16_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            path=mock16_path,
            expected=expected_path,
            observed=mock16_path or "missing",
            ok=mock16_ok,
            notes="ok" if mock16_ok else "mock16_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-16+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def write_drift_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in MATRIX_FIELDS})


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


def run_nonseal_extension_post_commit_drift_recheck(
    *,
    paths: DriftRecheckPaths = DriftRecheckPaths(),
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-14 非 seal 扩展 post-commit 漂移复核（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_fm14_output_root(paths.output_root_rel, base_dir=base_dir)

    fm01 = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))
    fm05 = load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir))
    fm12 = load_json(_abs(paths.fm12_gate_json_rel, base_dir=base_dir))
    fm13 = load_json(_abs(paths.fm13_gate_json_rel, base_dir=base_dir))

    bat_rows, bat_checks = build_fm01_05_12_13_gate_battery_rows(
        fm01=fm01,
        fm02=fm02,
        fm03=fm03,
        fm04=fm04,
        fm05=fm05,
        fm12=fm12,
        fm13=fm13,
    )
    art_rows, art_checks = build_fm13_artifact_presence_rows(
        paths=paths, base_dir=base_dir
    )

    # 重算须用未登记 ephemeral probe：MOCK16 已登记时 assert_fm13_output_root 会拒写
    probe_rel = "outputs/validation/_mock_c_fm14_recompute_probe"
    recomputed_fp, _recomputed_matrix = recompute_extension_fingerprints(
        probe_output_root_rel=probe_rel,
        protected_csv_rel=paths.protected_roots_csv_rel,
        harvest_863_status_rel=paths.harvest_863_status_rel,
        base_dir=base_dir,
    )
    drift_rows, drift_checks = build_fingerprint_drift_rows(
        paths=paths, recomputed_fp=recomputed_fp, base_dir=base_dir
    )
    fr_rows, fr_checks = build_frozen_mock_isolation_rows(paths, base_dir=base_dir)
    he_paths = ExtensionPaths(
        harvest_863_status_rel=paths.harvest_863_status_rel,
        fm03_mock_root_rel=paths.fm03_mock_root_rel,
        fm03_gate_json_rel=paths.fm03_gate_json_rel,
        output_root_rel=paths.output_root_rel,
    )
    he_rows, he_checks = build_harvest_exclusion_consistency_rows(
        he_paths, base_dir=base_dir
    )
    hold_rows, hold_checks = build_execute_hold_seal_rows(fm13=fm13)
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )

    matrix = (
        bat_rows
        + art_rows
        + drift_rows
        + fr_rows
        + he_rows
        + hold_rows
        + csv_rows
    )
    layer_gates = {
        "fm_gate_battery": (
            "PASS_OFFLINE" if all(bat_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "fm13_artifact_presence": (
            "PASS_OFFLINE" if all(art_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "fingerprint_drift": (
            "PASS_OFFLINE"
            if all(drift_checks.values())
            else "FAIL_REVIEW_REQUIRED"
        ),
        "frozen_mock_isolation": (
            "PASS_OFFLINE" if all(fr_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "harvest_exclusion_consistency": (
            "PASS_OFFLINE" if all(he_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "execute_hold_seal": (
            "PASS_OFFLINE" if all(hold_checks.values()) else "FAIL_REVIEW_REQUIRED"
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
    drift_detected = not all(drift_checks.values())

    os.makedirs(out_root, exist_ok=True)
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
                "seal_chain_extended": False,
                "frozen_extension_fp_sha256": FROZEN_EXTENSION_FP_SHA256,
                "recomputed_extension_fp_sha256": recomputed_fp.get(
                    "fingerprint_sha256"
                ),
                "drift_detected": drift_detected,
                "fingerprint": fp,
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
                "gate": overall,
                "layer_gates": layer_gates,
                "fm01_gate": fm01.get("gate"),
                "fm02_gate": fm02.get("gate"),
                "fm03_gate": fm03.get("gate"),
                "fm04_gate": fm04.get("gate"),
                "fm05_gate": fm05.get("gate"),
                "fm12_gate": fm12.get("gate"),
                "fm13_gate": fm13.get("gate"),
                "fm14_gate": overall,
                "cninfo_calls": 0,
                "seal_chain_extended": False,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    seal_packet = {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "gate": overall,
        "drift_detected": drift_detected,
        "frozen_extension_fp_sha256": FROZEN_EXTENSION_FP_SHA256,
        "recomputed_extension_fp_sha256": recomputed_fp.get("fingerprint_sha256"),
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting": True,
        "seal_chain_extended": False,
        "notes": (
            "non-seal post-commit drift recheck of C-FM-13 extension; "
            "EXECUTE remains human-held; does not overwrite MOCK3-15"
        ),
    }
    packet_path = os.path.join(out_root, "drift_seal_packet.json")
    with open(packet_path, "w", encoding="utf-8") as fh:
        json.dump(seal_packet, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    out_rel = _rel(out_root, base_dir=base_dir)
    return {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "gate": overall,
        "layer_gates": layer_gates,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting": True,
        "seal_chain_extended": False,
        "fail_count": fail_count,
        "matrix_rows": len(matrix),
        "output_root": out_rel,
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "fingerprint_path": _rel(fp_path, base_dir=base_dir),
        "fingerprint": fp,
        "battery_path": _rel(battery_path, base_dir=base_dir),
        "seal_packet_path": _rel(packet_path, base_dir=base_dir),
        "seal_packet": seal_packet,
        "frozen_extension_fp_sha256": FROZEN_EXTENSION_FP_SHA256,
        "recomputed_extension_fp_sha256": recomputed_fp.get("fingerprint_sha256"),
        "drift_detected": drift_detected,
        "mock_root_is_isolated": is_allowed_mock_test_cleanup_path(
            out_root, base_dir=base_dir
        ),
        "inputs": {
            "fm01_gate_json": paths.fm01_gate_json_rel,
            "fm02_gate_json": paths.fm02_gate_json_rel,
            "fm03_gate_json": paths.fm03_gate_json_rel,
            "fm04_gate_json": paths.fm04_gate_json_rel,
            "fm05_gate_json": paths.fm05_gate_json_rel,
            "fm12_gate_json": paths.fm12_gate_json_rel,
            "fm13_gate_json": paths.fm13_gate_json_rel,
            "fm13_mock_root": paths.fm13_mock_root_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
            "harvest_863_status": paths.harvest_863_status_rel,
        },
    }
