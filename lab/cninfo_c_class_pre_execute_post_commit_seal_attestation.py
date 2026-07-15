"""
CNINFO C-class — Pre-EXECUTE post-commit seal attestation / FM01–08 锁链（离线 · C-FM-09）。

在 C-FM-08（controller commit-boundary）已 commit 之上，补齐：
  1) FM-01..08 gate battery 只读聚合（含 FM-08 commit-boundary gate）
  2) seal-chain 连续性：MOCK8 墙 + MOCK9 漂移 seal + MOCK10 commit-boundary
  3) MOCK10 boundary 指纹零漂移复核（不覆盖 MOCK8/9/10）
  4) 三层 EXECUTE hold seal：FM06 人批包 · FM07 drift seal · FM08 boundary packet
  5) human EXECUTE decision handoff packet（证据汇总；不翻转 approved）
  6) protected_output_roots.csv 注册一致性（MOCK3–11 · AUTH1）

禁止：CNINFO live · production EXECUTE · 覆盖权威 dual-layer 索引 ·
      覆盖 MOCK8/MOCK9/MOCK10 · verified 声称 · 翻转 approved_for_snapshot_rebuild ·
      commit/push。
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
from cninfo_c_class_pre_execute_controller_commit_boundary import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM08_MOCK_ROOT_REL,
    BOUNDARY_MATRIX_FIELDS,
    build_fm01_to_07_gate_battery_rows,
    fingerprint_boundary_matrix,
)
from cninfo_c_class_pre_execute_safe_snapshot_wall import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM06_MOCK_ROOT_REL,
    load_json,
    load_protected_root_rows,
)
from cninfo_c_class_pre_execute_wall_freeze_drift_recheck import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM07_MOCK_ROOT_REL,
    FROZEN_EXCLUSION_FP_SHA256,
    FROZEN_WALL_FP_SHA256,
)

TASK_ID = "C-FM-09"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm09_pre_execute_post_commit_seal_attestation"
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
FM07_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_wall_freeze_drift_recheck_20260715.json"
)
FM08_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_controller_commit_boundary_20260715.json"
)

FM06_WALL_FINGERPRINT_REL = f"{FM06_MOCK_ROOT_REL}/wall_fingerprint.json"
FM06_EXCLUSION_FP_REL = f"{FM06_MOCK_ROOT_REL}/exclusion_universe_fingerprint.json"
FM06_PACKET_REL = f"{FM06_MOCK_ROOT_REL}/human_approval_packet.json"

FM07_DRIFT_SEAL_REL = f"{FM07_MOCK_ROOT_REL}/drift_seal_packet.json"
FM07_DRIFT_FP_REL = f"{FM07_MOCK_ROOT_REL}/drift_fingerprint.json"

FM08_BOUNDARY_MATRIX_REL = f"{FM08_MOCK_ROOT_REL}/boundary_matrix.csv"
FM08_BOUNDARY_FP_REL = f"{FM08_MOCK_ROOT_REL}/boundary_fingerprint.json"
FM08_BATTERY_REL = f"{FM08_MOCK_ROOT_REL}/fm_gate_battery.json"
FM08_PACKET_REL = f"{FM08_MOCK_ROOT_REL}/controller_commit_boundary_packet.json"

# C-FM-08 冻结 boundary 指纹常量（post-commit 漂移复核锚点）
FROZEN_BOUNDARY_FP_SHA256 = (
    "c9c00a38e3031b25c70bd462aea2a6bb5927f4acdc9cfc48fc4029e160a04db4"
)

REQUIRED_PROTECTED_ROOT_IDS = (
    "C-ROOT-MOCK3",
    "C-ROOT-MOCK4",
    "C-ROOT-MOCK5",
    "C-ROOT-MOCK6",
    "C-ROOT-MOCK7",
    "C-ROOT-MOCK8",
    "C-ROOT-MOCK9",
    "C-ROOT-MOCK10",
    "C-ROOT-MOCK11",
    "C-ROOT-AUTH1",
)

ATTESTATION_MATRIX_FIELDS = [
    "check_id",
    "layer",
    "path",
    "expected",
    "observed",
    "ok",
    "notes",
]


@dataclass(frozen=True)
class PostCommitAttestationPaths:
    """只读输入与隔离写根路径规格。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    fm05_gate_json_rel: str = FM05_GATE_JSON_REL
    fm06_gate_json_rel: str = FM06_GATE_JSON_REL
    fm07_gate_json_rel: str = FM07_GATE_JSON_REL
    fm08_gate_json_rel: str = FM08_GATE_JSON_REL
    fm06_mock_root_rel: str = FM06_MOCK_ROOT_REL
    fm06_wall_fingerprint_rel: str = FM06_WALL_FINGERPRINT_REL
    fm06_exclusion_fp_rel: str = FM06_EXCLUSION_FP_REL
    fm06_packet_rel: str = FM06_PACKET_REL
    fm07_mock_root_rel: str = FM07_MOCK_ROOT_REL
    fm07_drift_seal_rel: str = FM07_DRIFT_SEAL_REL
    fm07_drift_fp_rel: str = FM07_DRIFT_FP_REL
    fm08_mock_root_rel: str = FM08_MOCK_ROOT_REL
    fm08_boundary_matrix_rel: str = FM08_BOUNDARY_MATRIX_REL
    fm08_boundary_fp_rel: str = FM08_BOUNDARY_FP_REL
    fm08_battery_rel: str = FM08_BATTERY_REL
    fm08_packet_rel: str = FM08_PACKET_REL
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


def assert_post_commit_attestation_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """post-commit attestation 写根：须 validation/_mock_*，拒绝权威索引与 MOCK8/9/10。"""
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    out_rel = _rel(out, base_dir=base_dir).rstrip("/")
    for label, frozen_rel in (
        ("MOCK8", FM06_MOCK_ROOT_REL.rstrip("/")),
        ("MOCK9", FM07_MOCK_ROOT_REL.rstrip("/")),
        ("MOCK10", FM08_MOCK_ROOT_REL.rstrip("/")),
    ):
        if out_rel == frozen_rel or out_rel.startswith(frozen_rel + "/"):
            raise RuntimeError(
                f"C_FM09_MUST_NOT_OVERWRITE_{label}: "
                f"output_root={out_rel} overlaps frozen {label}={frozen_rel}"
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


def load_boundary_matrix_rows(
    path: str,
) -> List[Dict[str, str]]:
    """只读加载 FM08 boundary_matrix.csv。"""
    rows: List[Dict[str, str]] = []
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            rows.append({k: str(raw.get(k) or "") for k in BOUNDARY_MATRIX_FIELDS})
    return rows


def build_fm01_to_08_gate_battery_rows(
    *,
    fm01: Dict[str, Any],
    fm02: Dict[str, Any],
    fm03: Dict[str, Any],
    fm04: Dict[str, Any],
    fm05: Dict[str, Any],
    fm06: Dict[str, Any],
    fm07: Dict[str, Any],
    fm08: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..08 既有 gate 只读聚合（不重跑；含 FM-08 commit-boundary gate）。"""
    rows, checks = build_fm01_to_07_gate_battery_rows(
        fm01=fm01,
        fm02=fm02,
        fm03=fm03,
        fm04=fm04,
        fm05=fm05,
        fm06=fm06,
        fm07=fm07,
    )
    rows = [r for r in rows if r.get("check_id") != "fm01_to_07_battery_all_pass"]
    checks.pop("fm01_to_07_battery_all_pass", None)

    gate = str(fm08.get("gate") or "").strip()
    cninfo = fm08.get("cninfo_calls", None)
    execute = fm08.get("execute_production_snapshot_rebuild", None)
    approved = fm08.get("approved_for_snapshot_rebuild", None)
    ok = (
        gate == "PASS_OFFLINE"
        and cninfo == 0
        and execute is False
        and approved is False
    )
    rows.append(
        _row(
            check_id="fm08_pre_execute_controller_commit_boundary",
            layer="fm_gate_battery",
            path="fm08_pre_execute_controller_commit_boundary",
            expected="gate=PASS_OFFLINE;cninfo=0;execute=false;approved=false",
            observed=(
                f"gate={gate};cninfo={cninfo};execute={execute};approved={approved}"
            ),
            ok=ok,
            notes="ok" if ok else "fm08_gate_not_pass",
        )
    )
    checks["fm08_pre_execute_controller_commit_boundary"] = ok

    prior_ok = all(
        checks.get(k)
        for k in (
            "fm01_isolated_dryrun_repro",
            "fm02_isolated_validation_cohorts",
            "fm03_harvest_exclusion_dual_layer",
            "fm04_ledger_resume_lineage",
            "fm05_cross_fm_mock_cohort_integrity",
            "fm06_pre_execute_safe_snapshot_wall",
            "fm07_pre_execute_wall_freeze_drift_recheck",
            "fm08_pre_execute_controller_commit_boundary",
        )
    )
    rows.append(
        _row(
            check_id="fm01_to_08_battery_all_pass",
            layer="fm_gate_battery",
            expected="all_prior_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/8",
            ok=prior_ok,
            notes="ok" if prior_ok else "battery_incomplete",
        )
    )
    checks["fm01_to_08_battery_all_pass"] = prior_ok
    return rows, checks


def build_seal_chain_continuity_rows(
    *,
    paths: PostCommitAttestationPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[
    List[Dict[str, str]],
    Dict[str, bool],
    Dict[str, Any],
    Dict[str, Any],
    Dict[str, Any],
]:
    """MOCK8 + MOCK9 + MOCK10 seal-chain 连续性与 MOCK10 boundary 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    presence_specs = [
        ("fm06_mock_root_exists", paths.fm06_mock_root_rel, "dir"),
        ("fm06_wall_fingerprint_exists", paths.fm06_wall_fingerprint_rel, "file"),
        ("fm06_exclusion_fp_exists", paths.fm06_exclusion_fp_rel, "file"),
        ("fm06_packet_exists", paths.fm06_packet_rel, "file"),
        ("fm07_mock_root_exists", paths.fm07_mock_root_rel, "dir"),
        ("fm07_drift_seal_exists", paths.fm07_drift_seal_rel, "file"),
        ("fm07_drift_fp_exists", paths.fm07_drift_fp_rel, "file"),
        ("fm08_mock_root_exists", paths.fm08_mock_root_rel, "dir"),
        ("fm08_boundary_matrix_exists", paths.fm08_boundary_matrix_rel, "file"),
        ("fm08_boundary_fp_exists", paths.fm08_boundary_fp_rel, "file"),
        ("fm08_battery_exists", paths.fm08_battery_rel, "file"),
        ("fm08_packet_exists", paths.fm08_packet_rel, "file"),
    ]
    for check_id, rel, kind in presence_specs:
        abs_path = _abs(rel, base_dir=base_dir)
        present = os.path.isdir(abs_path) if kind == "dir" else os.path.isfile(abs_path)
        rows.append(
            _row(
                check_id=check_id,
                layer="seal_chain_continuity",
                path=rel,
                expected=f"{kind}_present",
                observed=f"present={present}",
                ok=present,
            )
        )
        checks[check_id] = present

    wall_fp: Dict[str, Any] = {}
    wall_path = _abs(paths.fm06_wall_fingerprint_rel, base_dir=base_dir)
    if os.path.isfile(wall_path):
        wall_fp = load_json(wall_path)
    wall_sha = str(
        (wall_fp.get("fingerprint") or {}).get("fingerprint_sha256")
        or wall_fp.get("fingerprint_sha256")
        or ""
    )
    wall_ok = wall_sha == FROZEN_WALL_FP_SHA256
    checks["seal_chain_wall_fp_anchor"] = wall_ok
    rows.append(
        _row(
            check_id="seal_chain_wall_fp_anchor",
            layer="seal_chain_continuity",
            path=paths.fm06_wall_fingerprint_rel,
            expected=FROZEN_WALL_FP_SHA256,
            observed=wall_sha or "missing",
            ok=wall_ok,
        )
    )

    excl_fp: Dict[str, Any] = {}
    excl_path = _abs(paths.fm06_exclusion_fp_rel, base_dir=base_dir)
    if os.path.isfile(excl_path):
        excl_fp = load_json(excl_path)
    excl_sha = str(
        (excl_fp.get("fingerprint") or {}).get("fingerprint_sha256")
        or excl_fp.get("fingerprint_sha256")
        or ""
    )
    excl_ok = excl_sha == FROZEN_EXCLUSION_FP_SHA256
    checks["seal_chain_exclusion_fp_anchor"] = excl_ok
    rows.append(
        _row(
            check_id="seal_chain_exclusion_fp_anchor",
            layer="seal_chain_continuity",
            path=paths.fm06_exclusion_fp_rel,
            expected=FROZEN_EXCLUSION_FP_SHA256,
            observed=excl_sha or "missing",
            ok=excl_ok,
        )
    )

    drift_seal: Dict[str, Any] = {}
    drift_path = _abs(paths.fm07_drift_seal_rel, base_dir=base_dir)
    if os.path.isfile(drift_path):
        drift_seal = load_json(drift_path)
    drift_detected = drift_seal.get("drift_detected", None)
    no_drift_ok = drift_detected is False
    checks["seal_chain_fm07_zero_drift"] = no_drift_ok
    rows.append(
        _row(
            check_id="seal_chain_fm07_zero_drift",
            layer="seal_chain_continuity",
            path=paths.fm07_drift_seal_rel,
            expected="drift_detected=false",
            observed=(
                f"drift_detected={drift_detected}"
                if drift_detected is not None
                else "missing"
            ),
            ok=no_drift_ok,
        )
    )

    boundary_fp_doc: Dict[str, Any] = {}
    boundary_fp_path = _abs(paths.fm08_boundary_fp_rel, base_dir=base_dir)
    if os.path.isfile(boundary_fp_path):
        boundary_fp_doc = load_json(boundary_fp_path)
    recorded_boundary_sha = str(
        (boundary_fp_doc.get("fingerprint") or {}).get("fingerprint_sha256") or ""
    )
    recorded_ok = recorded_boundary_sha == FROZEN_BOUNDARY_FP_SHA256
    checks["seal_chain_boundary_fp_anchor"] = recorded_ok
    rows.append(
        _row(
            check_id="seal_chain_boundary_fp_anchor",
            layer="seal_chain_continuity",
            path=paths.fm08_boundary_fp_rel,
            expected=FROZEN_BOUNDARY_FP_SHA256,
            observed=recorded_boundary_sha or "missing",
            ok=recorded_ok,
        )
    )

    # 从 MOCK10 boundary_matrix.csv 重算指纹，核对冻结常量（零漂移）
    recomputed_sha = ""
    matrix_path = _abs(paths.fm08_boundary_matrix_rel, base_dir=base_dir)
    if os.path.isfile(matrix_path):
        matrix_rows = load_boundary_matrix_rows(matrix_path)
        recomputed = fingerprint_boundary_matrix(matrix_rows)
        recomputed_sha = str(recomputed.get("fingerprint_sha256") or "")
    recompute_ok = recomputed_sha == FROZEN_BOUNDARY_FP_SHA256
    checks["seal_chain_boundary_fp_recompute"] = recompute_ok
    rows.append(
        _row(
            check_id="seal_chain_boundary_fp_recompute",
            layer="seal_chain_continuity",
            path=paths.fm08_boundary_matrix_rel,
            expected=FROZEN_BOUNDARY_FP_SHA256,
            observed=recomputed_sha or "missing",
            ok=recompute_ok,
            notes="ok" if recompute_ok else "boundary_fingerprint_drift",
        )
    )

    zero_drift = recorded_ok and recompute_ok
    checks["seal_chain_fm08_zero_drift"] = zero_drift
    rows.append(
        _row(
            check_id="seal_chain_fm08_zero_drift",
            layer="seal_chain_continuity",
            expected="recorded==recomputed==frozen",
            observed=(
                f"recorded={recorded_boundary_sha[:12]}…;"
                f"recomputed={recomputed_sha[:12]}…;"
                f"match={zero_drift}"
            ),
            ok=zero_drift,
        )
    )

    mock8_iso = is_allowed_mock_test_cleanup_path(
        _abs(paths.fm06_mock_root_rel, base_dir=base_dir), base_dir=base_dir
    )
    mock9_iso = is_allowed_mock_test_cleanup_path(
        _abs(paths.fm07_mock_root_rel, base_dir=base_dir), base_dir=base_dir
    )
    mock10_iso = is_allowed_mock_test_cleanup_path(
        _abs(paths.fm08_mock_root_rel, base_dir=base_dir), base_dir=base_dir
    )
    iso_ok = mock8_iso and mock9_iso and mock10_iso
    checks["seal_chain_mock8_9_10_isolated"] = iso_ok
    rows.append(
        _row(
            check_id="seal_chain_mock8_9_10_isolated",
            layer="seal_chain_continuity",
            expected="all_three_isolated_mock",
            observed=(
                f"mock8={mock8_iso};mock9={mock9_iso};mock10={mock10_iso}"
            ),
            ok=iso_ok,
        )
    )

    chain_fp_ok = wall_ok and excl_ok and zero_drift and no_drift_ok
    checks["seal_chain_fingerprint_continuity"] = chain_fp_ok
    rows.append(
        _row(
            check_id="seal_chain_fingerprint_continuity",
            layer="seal_chain_continuity",
            expected="wall+exclusion+boundary anchors continuous MOCK8/9/10",
            observed=(
                f"wall_ok={wall_ok};excl_ok={excl_ok};"
                f"fm07_zero={no_drift_ok};fm08_zero={zero_drift}"
            ),
            ok=chain_fp_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="seal_chain_continuity_all_pass",
            layer="seal_chain_continuity",
            expected="fm06+fm07+fm08_seal_continuous",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["seal_chain_continuity_all_pass"] = all_ok
    return rows, checks, wall_fp, drift_seal, boundary_fp_doc


def build_triple_hold_seal_rows(
    *,
    paths: PostCommitAttestationPaths,
    drift_seal: Dict[str, Any],
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any], Dict[str, Any]]:
    """FM-06 / FM-07 / FM-08 三层 KEEP_EXECUTE_FALSE。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    packet: Dict[str, Any] = {}
    fm08_packet: Dict[str, Any] = {}

    packet_path = _abs(paths.fm06_packet_rel, base_dir=base_dir)
    if os.path.isfile(packet_path):
        packet = load_json(packet_path)
    fm08_path = _abs(paths.fm08_packet_rel, base_dir=base_dir)
    if os.path.isfile(fm08_path):
        fm08_packet = load_json(fm08_path)

    def _hold_fields(src: Dict[str, Any], prefix: str, path: str) -> None:
        execute = src.get("execute_production_snapshot_rebuild", None)
        approved = src.get("approved_for_snapshot_rebuild", None)
        hold = str(src.get("hold_recommendation") or "").strip()
        human = src.get("human_action_required_for_execute", None)
        verified_forbid = src.get("verified_claim_forbidden", None)
        prod_forbid = src.get("production_ready_claim_forbidden", None)

        execute_ok = execute is False
        checks[f"{prefix}_execute_false"] = execute_ok
        rows.append(
            _row(
                check_id=f"{prefix}_execute_false",
                layer="execute_hold_seal",
                path=path,
                expected="false",
                observed=str(execute).lower() if execute is not None else "missing",
                ok=execute_ok,
            )
        )

        approved_ok = approved is False
        checks[f"{prefix}_approved_false"] = approved_ok
        rows.append(
            _row(
                check_id=f"{prefix}_approved_false",
                layer="execute_hold_seal",
                expected="false",
                observed=str(approved).lower() if approved is not None else "missing",
                ok=approved_ok,
            )
        )

        hold_ok = hold == "KEEP_EXECUTE_FALSE"
        checks[f"{prefix}_keep_execute_false"] = hold_ok
        rows.append(
            _row(
                check_id=f"{prefix}_keep_execute_false",
                layer="execute_hold_seal",
                expected="KEEP_EXECUTE_FALSE",
                observed=hold or "missing",
                ok=hold_ok,
            )
        )

        human_ok = human is True
        checks[f"{prefix}_human_action_required"] = human_ok
        rows.append(
            _row(
                check_id=f"{prefix}_human_action_required",
                layer="execute_hold_seal",
                expected="true",
                observed=str(human).lower() if human is not None else "missing",
                ok=human_ok,
            )
        )

        claims_ok = verified_forbid is True and prod_forbid is True
        checks[f"{prefix}_claims_forbidden"] = claims_ok
        rows.append(
            _row(
                check_id=f"{prefix}_claims_forbidden",
                layer="execute_hold_seal",
                expected="verified=true;production_ready=true",
                observed=(
                    f"verified={verified_forbid};production_ready={prod_forbid}"
                ),
                ok=claims_ok,
            )
        )

    _hold_fields(packet, "fm06_packet", paths.fm06_packet_rel)
    _hold_fields(drift_seal, "fm07_seal", paths.fm07_drift_seal_rel)
    _hold_fields(fm08_packet, "fm08_packet", paths.fm08_packet_rel)

    self_ok = True
    checks["fm09_self_constants_hold"] = self_ok
    rows.append(
        _row(
            check_id="fm09_self_constants_hold",
            layer="execute_hold_seal",
            expected="execute=false;approved=false",
            observed="execute=false;approved=false",
            ok=self_ok,
            notes="c_fm09_hard_constants",
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="execute_hold_seal_all_pass",
            layer="execute_hold_seal",
            expected="triple_KEEP_EXECUTE_FALSE_sealed",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["execute_hold_seal_all_pass"] = all_ok
    return rows, checks, packet, fm08_packet


def build_human_decision_handoff_rows(
    *,
    layer_gates_so_far: Dict[str, bool],
    fm06_packet: Dict[str, Any],
    drift_seal: Dict[str, Any],
    fm08_packet: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """
    Human EXECUTE decision handoff：

    - offline FM01–08 链 PASS
    - KEEP_EXECUTE_FALSE 仍成立（三层）
    - ready_for_commit（本包）≠ ready_for_execute
    - decision_status = AWAITING_HUMAN_EXECUTE_DECISION
    - 明确禁止 verified / production_ready / 翻转 approved
    """
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    offline_ok = all(layer_gates_so_far.values())
    checks["handoff_offline_chain_pass"] = offline_ok
    rows.append(
        _row(
            check_id="handoff_offline_chain_pass",
            layer="human_decision_handoff",
            expected="prior_layers_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in layer_gates_so_far.values() if v)}/"
            f"{len(layer_gates_so_far)}",
            ok=offline_ok,
        )
    )

    hold_ok = (
        str(fm06_packet.get("hold_recommendation") or "") == "KEEP_EXECUTE_FALSE"
        and str(drift_seal.get("hold_recommendation") or "") == "KEEP_EXECUTE_FALSE"
        and str(fm08_packet.get("hold_recommendation") or "") == "KEEP_EXECUTE_FALSE"
    )
    checks["handoff_hold_still_false"] = hold_ok
    rows.append(
        _row(
            check_id="handoff_hold_still_false",
            layer="human_decision_handoff",
            expected="KEEP_EXECUTE_FALSE",
            observed=(
                f"fm06={fm06_packet.get('hold_recommendation')};"
                f"fm07={drift_seal.get('hold_recommendation')};"
                f"fm08={fm08_packet.get('hold_recommendation')}"
            ),
            ok=hold_ok,
        )
    )

    execute_blocked = (
        fm06_packet.get("execute_production_snapshot_rebuild") is False
        and drift_seal.get("execute_production_snapshot_rebuild") is False
        and fm08_packet.get("execute_production_snapshot_rebuild") is False
        and fm06_packet.get("approved_for_snapshot_rebuild") is False
        and drift_seal.get("approved_for_snapshot_rebuild") is False
        and fm08_packet.get("approved_for_snapshot_rebuild") is False
    )
    checks["handoff_execute_still_blocked"] = execute_blocked
    rows.append(
        _row(
            check_id="handoff_execute_still_blocked",
            layer="human_decision_handoff",
            expected="execute=false;approved=false",
            observed="blocked" if execute_blocked else "NOT_BLOCKED",
            ok=execute_blocked,
        )
    )

    commit_ready = offline_ok and hold_ok and execute_blocked
    checks["handoff_commit_ready_execute_held"] = commit_ready
    rows.append(
        _row(
            check_id="handoff_commit_ready_execute_held",
            layer="human_decision_handoff",
            expected="ready_for_commit=true;ready_for_execute=false",
            observed=(
                f"ready_for_commit={str(commit_ready).lower()};"
                "ready_for_execute=false"
            ),
            ok=commit_ready,
        )
    )

    human_ok = (
        fm06_packet.get("human_action_required_for_execute") is True
        and drift_seal.get("human_action_required_for_execute") is True
        and fm08_packet.get("human_action_required_for_execute") is True
    )
    checks["handoff_human_gate_intact"] = human_ok
    rows.append(
        _row(
            check_id="handoff_human_gate_intact",
            layer="human_decision_handoff",
            expected="human_action_required_for_execute=true",
            observed=(
                f"fm06={fm06_packet.get('human_action_required_for_execute')};"
                f"fm07={drift_seal.get('human_action_required_for_execute')};"
                f"fm08={fm08_packet.get('human_action_required_for_execute')}"
            ),
            ok=human_ok,
        )
    )

    claims_ok = (
        fm06_packet.get("verified_claim_forbidden") is True
        and drift_seal.get("verified_claim_forbidden") is True
        and fm08_packet.get("verified_claim_forbidden") is True
        and fm06_packet.get("production_ready_claim_forbidden") is True
        and drift_seal.get("production_ready_claim_forbidden") is True
        and fm08_packet.get("production_ready_claim_forbidden") is True
    )
    checks["handoff_claims_still_forbidden"] = claims_ok
    rows.append(
        _row(
            check_id="handoff_claims_still_forbidden",
            layer="human_decision_handoff",
            expected="verified+production_ready forbidden",
            observed=f"claims_ok={claims_ok}",
            ok=claims_ok,
        )
    )

    decision_status = "AWAITING_HUMAN_EXECUTE_DECISION"
    # decision_ok：offline 链 PASS · hold 成立 · human gate · 禁声称
    decision_ok = commit_ready and human_ok and claims_ok
    checks["handoff_decision_status"] = decision_ok
    rows.append(
        _row(
            check_id="handoff_decision_status",
            layer="human_decision_handoff",
            expected="AWAITING_HUMAN_EXECUTE_DECISION",
            observed=decision_status if decision_ok else "NOT_READY",
            ok=decision_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="human_decision_handoff_all_pass",
            layer="human_decision_handoff",
            expected="handoff_ready_execute_held",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["human_decision_handoff_all_pass"] = all_ok

    packet = {
        "packet_kind": "pre_execute_post_commit_seal_attestation",
        "task_id": TASK_ID,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "cninfo_calls": 0,
        "human_action_required_for_execute": True,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "ready_for_commit": commit_ready,
        "ready_for_execute": False,
        "controller_action": "POST_COMMIT_ATTESTATION_ONLY",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "verified_claim_forbidden": True,
        "production_ready_claim_forbidden": True,
        "frozen_wall_fingerprint_sha256": FROZEN_WALL_FP_SHA256,
        "frozen_exclusion_fingerprint_sha256": FROZEN_EXCLUSION_FP_SHA256,
        "frozen_boundary_fingerprint_sha256": FROZEN_BOUNDARY_FP_SHA256,
        "notes": (
            "本包在 C-FM-08 commit 后做 post-commit seal attestation："
            "FM-01..08 battery · MOCK8/9/10 零漂移 · 三层 KEEP_EXECUTE_FALSE · "
            "human EXECUTE decision handoff；不覆盖 MOCK8/9/10；"
            "不翻转 approved_for_snapshot_rebuild；生产 snapshot EXECUTE 仍须独立人批；"
            "本 executor 不 commit/push。"
        ),
    }
    return rows, checks, packet


def build_protected_csv_registry_rows(
    *,
    csv_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected_output_roots.csv 注册一致性（含 MOCK11）。"""
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

    mock10 = by_id.get("C-ROOT-MOCK10") or {}
    mock10_path = str(mock10.get("path_pattern") or "").strip().rstrip("/")
    mock10_ok = mock10_path == FM08_MOCK_ROOT_REL
    checks["protected_csv_mock10_path"] = mock10_ok
    rows.append(
        _row(
            check_id="protected_csv_mock10_path",
            layer="protected_csv_registry",
            path=mock10_path,
            expected=FM08_MOCK_ROOT_REL,
            observed=mock10_path or "missing",
            ok=mock10_ok,
        )
    )

    mock11 = by_id.get("C-ROOT-MOCK11") or {}
    mock11_path = str(mock11.get("path_pattern") or "").strip().rstrip("/")
    mock11_ok = mock11_path == DEFAULT_MOCK_OUTPUT_ROOT_REL
    checks["protected_csv_mock11_path"] = mock11_ok
    rows.append(
        _row(
            check_id="protected_csv_mock11_path",
            layer="protected_csv_registry",
            path=mock11_path,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=mock11_path or "missing",
            ok=mock11_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-11+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["protected_csv_registry_all_pass"] = all_ok
    return rows, checks


def write_attestation_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=ATTESTATION_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in ATTESTATION_MATRIX_FIELDS})


def fingerprint_attestation_matrix(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    """post-commit attestation 矩阵结构指纹。"""
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


def run_pre_execute_post_commit_seal_attestation(
    *,
    paths: PostCommitAttestationPaths = PostCommitAttestationPaths(),
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-09 pre-EXECUTE post-commit seal attestation（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_post_commit_attestation_output_root(
        paths.output_root_rel, base_dir=base_dir
    )

    fm01 = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))
    fm05 = load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir))
    fm06 = load_json(_abs(paths.fm06_gate_json_rel, base_dir=base_dir))
    fm07 = load_json(_abs(paths.fm07_gate_json_rel, base_dir=base_dir))
    fm08 = load_json(_abs(paths.fm08_gate_json_rel, base_dir=base_dir))

    bat_rows, bat_checks = build_fm01_to_08_gate_battery_rows(
        fm01=fm01,
        fm02=fm02,
        fm03=fm03,
        fm04=fm04,
        fm05=fm05,
        fm06=fm06,
        fm07=fm07,
        fm08=fm08,
    )
    chain_rows, chain_checks, wall_fp, drift_seal, boundary_fp = (
        build_seal_chain_continuity_rows(paths=paths, base_dir=base_dir)
    )
    seal_rows, seal_checks, fm06_packet, fm08_packet = build_triple_hold_seal_rows(
        paths=paths, drift_seal=drift_seal, base_dir=base_dir
    )

    prior_layer_bools = {
        "fm_gate_battery": all(bat_checks.values()),
        "seal_chain_continuity": all(chain_checks.values()),
        "execute_hold_seal": all(seal_checks.values()),
    }
    handoff_rows, handoff_checks, handoff_packet = build_human_decision_handoff_rows(
        layer_gates_so_far=prior_layer_bools,
        fm06_packet=fm06_packet,
        drift_seal=drift_seal,
        fm08_packet=fm08_packet,
    )
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )

    matrix = bat_rows + chain_rows + seal_rows + handoff_rows + csv_rows
    layer_gates = {
        "fm_gate_battery": (
            "PASS_OFFLINE" if all(bat_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "seal_chain_continuity": (
            "PASS_OFFLINE" if all(chain_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "execute_hold_seal": (
            "PASS_OFFLINE" if all(seal_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "human_decision_handoff": (
            "PASS_OFFLINE" if all(handoff_checks.values()) else "FAIL_REVIEW_REQUIRED"
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

    matrix_path = os.path.join(out_root, "attestation_matrix.csv")
    write_attestation_matrix_csv(matrix, matrix_path)
    fp = fingerprint_attestation_matrix(matrix)
    fp_path = os.path.join(out_root, "attestation_fingerprint.json")
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
                "frozen_boundary_fingerprint_sha256": FROZEN_BOUNDARY_FP_SHA256,
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
                "fm07_gate": fm07.get("gate"),
                "fm08_gate": fm08.get("gate"),
                "fm09_gate": overall,
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    handoff_packet = dict(handoff_packet)
    handoff_packet["generated_at"] = generated_at
    handoff_packet["gate"] = overall
    handoff_packet["layer_gates"] = layer_gates
    handoff_packet["ready_for_commit"] = overall == "PASS_OFFLINE"
    handoff_path = os.path.join(out_root, "human_execute_decision_handoff_packet.json")
    with open(handoff_path, "w", encoding="utf-8") as fh:
        json.dump(handoff_packet, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # 显式 seal packet：记录零漂移与 hold
    seal_path = os.path.join(out_root, "post_commit_seal_packet.json")
    seal_packet = {
        "packet_kind": "pre_execute_post_commit_seal",
        "task_id": TASK_ID,
        "generated_at": generated_at,
        "gate": overall,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "human_action_required_for_execute": True,
        "drift_detected": False if overall == "PASS_OFFLINE" else True,
        "frozen_wall_fingerprint_sha256": FROZEN_WALL_FP_SHA256,
        "frozen_exclusion_fingerprint_sha256": FROZEN_EXCLUSION_FP_SHA256,
        "frozen_boundary_fingerprint_sha256": FROZEN_BOUNDARY_FP_SHA256,
        "layer_gates": layer_gates,
        "verified_claim_forbidden": True,
        "production_ready_claim_forbidden": True,
        "notes": (
            "本包仅复核 C-FM-08 commit-boundary 指纹零漂移并 seal KEEP_EXECUTE_FALSE；"
            "不覆盖 MOCK8/9/10；不翻转 approved_for_snapshot_rebuild；"
            "生产 snapshot EXECUTE 仍须独立人批。"
        ),
    }
    with open(seal_path, "w", encoding="utf-8") as fh:
        json.dump(seal_packet, fh, ensure_ascii=False, indent=2)
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
        "handoff_packet_path": _rel(handoff_path, base_dir=base_dir),
        "handoff_packet": handoff_packet,
        "seal_packet_path": _rel(seal_path, base_dir=base_dir),
        "seal_packet": seal_packet,
        "fm06_wall_fingerprint": wall_fp,
        "fm07_drift_seal": drift_seal,
        "fm08_boundary_fingerprint": boundary_fp,
        "fm06_human_approval_packet": fm06_packet,
        "fm08_commit_boundary_packet": fm08_packet,
        "frozen_wall_fingerprint_sha256": FROZEN_WALL_FP_SHA256,
        "frozen_exclusion_fingerprint_sha256": FROZEN_EXCLUSION_FP_SHA256,
        "frozen_boundary_fingerprint_sha256": FROZEN_BOUNDARY_FP_SHA256,
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
            "fm07_gate_json": paths.fm07_gate_json_rel,
            "fm08_gate_json": paths.fm08_gate_json_rel,
            "fm06_mock_root": paths.fm06_mock_root_rel,
            "fm07_mock_root": paths.fm07_mock_root_rel,
            "fm08_mock_root": paths.fm08_mock_root_rel,
            "fm06_wall_fingerprint": paths.fm06_wall_fingerprint_rel,
            "fm07_drift_seal": paths.fm07_drift_seal_rel,
            "fm08_boundary_fingerprint": paths.fm08_boundary_fp_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
        },
    }
