"""
CNINFO C-class — 非 seal Cross-FM 扩展 controller commit-boundary（离线 · C-FM-15）。

在 C-FM-14（non-seal extension post-commit drift recheck）已 commit 且 EXECUTE 仍
human-held 之上，补齐非 seal 能力（不新增 MOCK seal 层）：
  1) FM-01..05 + FM-12 + FM-13 + FM-14 gate battery 只读聚合
  2) nonseal-chain 连续性：MOCK15 扩展 + MOCK16 漂移 seal 指纹锚点对齐
  3) 双层 EXECUTE hold seal：FM-13 packet 与 FM-14 drift seal 均 KEEP_EXECUTE_FALSE
  4) controller commit-boundary readiness packet（offline 链 PASS · EXECUTE 仍阻断）
  5) 冻结 mock 写隔离：MOCK3–16 拒绝；本任务 MOCK17 / ephemeral 放行
  6) protected_output_roots.csv 注册一致性（含 MOCK17）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–16 / 权威 dual-layer 索引 ·
verified 声称 · 翻转 approved_for_snapshot_rebuild · 扩展 seal-chain ·
因 AWAITING 而 IDLE · commit/push。
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
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    PROTECTED_ROOTS_CSV_REL,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_frozen_mock_cohort_write_forbidden,
    assert_safe_erad_audit_write_path,
    is_allowed_mock_test_cleanup_path,
    load_frozen_mock_cohort_roots,
    resolve_frozen_mock_cohort_root_id,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
)
from cninfo_c_class_nonseal_cross_fm_mock_cohort_extension import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM13_MOCK_ROOT_REL,
    load_json,
)
from cninfo_c_class_nonseal_extension_post_commit_drift_recheck import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL as FM14_MOCK_ROOT_REL,
    FROZEN_EXTENSION_FP_SHA256,
    build_fm01_05_12_13_gate_battery_rows,
    load_protected_root_rows,
)

TASK_ID = "C-FM-15"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm15_nonseal_extension_controller_commit_boundary"
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
FM14_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_post_commit_drift_recheck_20260715.json"
)

FM13_EXTENSION_FINGERPRINT_REL = f"{FM13_MOCK_ROOT_REL}/extension_fingerprint.json"
FM13_EXTENSION_MATRIX_REL = f"{FM13_MOCK_ROOT_REL}/extension_matrix.csv"
FM13_PACKET_REL = f"{FM13_MOCK_ROOT_REL}/extension_packet.json"
FM13_BATTERY_REL = f"{FM13_MOCK_ROOT_REL}/fm_gate_battery.json"
FM13_REGISTRY_REL = f"{FM13_MOCK_ROOT_REL}/nonseal_mock_cohort_registry.json"

FM14_DRIFT_SEAL_REL = f"{FM14_MOCK_ROOT_REL}/drift_seal_packet.json"
FM14_DRIFT_MATRIX_REL = f"{FM14_MOCK_ROOT_REL}/drift_matrix.csv"
FM14_DRIFT_FP_REL = f"{FM14_MOCK_ROOT_REL}/drift_fingerprint.json"
FM14_BATTERY_REL = f"{FM14_MOCK_ROOT_REL}/fm_gate_battery.json"

# C-FM-14 漂移复核矩阵指纹常量（commit-boundary 连续性锚点）
FROZEN_DRIFT_FP_SHA256 = (
    "8ce3951c29881b114b5b315949d7564459ef8b78255cd4c18ca39784151b576b"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK17"
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
    "C-ROOT-MOCK16",
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    "C-ROOT-AUTH1",
)

BOUNDARY_MATRIX_FIELDS = [
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
class NonsealCommitBoundaryPaths:
    """只读输入与隔离写根路径规格。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    fm05_gate_json_rel: str = FM05_GATE_JSON_REL
    fm12_gate_json_rel: str = FM12_GATE_JSON_REL
    fm13_gate_json_rel: str = FM13_GATE_JSON_REL
    fm14_gate_json_rel: str = FM14_GATE_JSON_REL
    fm13_mock_root_rel: str = FM13_MOCK_ROOT_REL
    fm13_extension_fingerprint_rel: str = FM13_EXTENSION_FINGERPRINT_REL
    fm13_extension_matrix_rel: str = FM13_EXTENSION_MATRIX_REL
    fm13_packet_rel: str = FM13_PACKET_REL
    fm13_battery_rel: str = FM13_BATTERY_REL
    fm13_registry_rel: str = FM13_REGISTRY_REL
    fm14_mock_root_rel: str = FM14_MOCK_ROOT_REL
    fm14_drift_seal_rel: str = FM14_DRIFT_SEAL_REL
    fm14_drift_matrix_rel: str = FM14_DRIFT_MATRIX_REL
    fm14_drift_fp_rel: str = FM14_DRIFT_FP_REL
    fm14_battery_rel: str = FM14_BATTERY_REL
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


def assert_fm15_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-15 写根：须 validation/_mock_*，不得覆盖 MOCK3–16（含 MOCK15/16），
    不得写权威 dual-layer 索引；允许本任务 MOCK17 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    out_rel = _rel(out, base_dir=base_dir).rstrip("/")
    for label, frozen_rel in (
        ("MOCK15", FM13_MOCK_ROOT_REL.rstrip("/")),
        ("MOCK16", FM14_MOCK_ROOT_REL.rstrip("/")),
    ):
        if out_rel == frozen_rel or out_rel.startswith(frozen_rel + "/"):
            raise RuntimeError(
                f"C_FM15_MUST_NOT_OVERWRITE_{label}: "
                f"output_root={out_rel} overlaps frozen {label}={frozen_rel}"
            )
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-15 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def build_fm01_05_12_13_14_gate_battery_rows(
    *,
    fm01: Dict[str, Any],
    fm02: Dict[str, Any],
    fm03: Dict[str, Any],
    fm04: Dict[str, Any],
    fm05: Dict[str, Any],
    fm12: Dict[str, Any],
    fm13: Dict[str, Any],
    fm14: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12 + FM-13 + FM-14 既有 gate 只读聚合（跳过 seal FM06–11）。"""
    rows, checks = build_fm01_05_12_13_gate_battery_rows(
        fm01=fm01,
        fm02=fm02,
        fm03=fm03,
        fm04=fm04,
        fm05=fm05,
        fm12=fm12,
        fm13=fm13,
    )
    rows = [r for r in rows if r.get("check_id") != "fm01_05_12_13_battery_all_pass"]
    checks.pop("fm01_05_12_13_battery_all_pass", None)

    gate = str(fm14.get("gate") or "").strip()
    cninfo = fm14.get("cninfo_calls", None)
    execute = fm14.get("execute_production_snapshot_rebuild", None)
    approved = fm14.get("approved_for_snapshot_rebuild", None)
    seal_ext = fm14.get("seal_chain_extended", None)
    drift = fm14.get("drift_detected", None)
    ok = (
        gate == "PASS_OFFLINE"
        and cninfo == 0
        and execute is False
        and approved is False
        and seal_ext is False
        and drift is False
    )
    rows.append(
        _row(
            check_id="fm14_nonseal_extension_post_commit_drift_recheck",
            layer="fm_gate_battery",
            cohort_id="fm14",
            expected=(
                "gate=PASS_OFFLINE;cninfo=0;execute=false;"
                "approved=false;seal_chain_extended=false;drift_detected=false"
            ),
            observed=(
                f"gate={gate};cninfo={cninfo};execute={execute};"
                f"approved={approved};seal_ext={seal_ext};drift={drift}"
            ),
            ok=ok,
            notes="ok" if ok else "fm14_gate_not_pass",
        )
    )
    checks["fm14_nonseal_extension_post_commit_drift_recheck"] = ok

    prior_ok = all(checks.values()) if checks else False
    rows.append(
        _row(
            check_id="fm01_05_12_13_14_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_incl_fm14_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=prior_ok,
            notes="ok" if prior_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_13_14_battery_all_pass"] = prior_ok
    return rows, checks


def build_nonseal_chain_continuity_rows(
    *,
    paths: NonsealCommitBoundaryPaths,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any], Dict[str, Any]]:
    """MOCK15 扩展 + MOCK16 漂移 seal 连续性（不覆盖冻结根）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    presence_specs = [
        ("fm13_mock_root_exists", paths.fm13_mock_root_rel, "dir"),
        ("fm13_extension_fingerprint_exists", paths.fm13_extension_fingerprint_rel, "file"),
        ("fm13_extension_matrix_exists", paths.fm13_extension_matrix_rel, "file"),
        ("fm13_packet_exists", paths.fm13_packet_rel, "file"),
        ("fm13_battery_exists", paths.fm13_battery_rel, "file"),
        ("fm13_registry_exists", paths.fm13_registry_rel, "file"),
        ("fm14_mock_root_exists", paths.fm14_mock_root_rel, "dir"),
        ("fm14_drift_seal_exists", paths.fm14_drift_seal_rel, "file"),
        ("fm14_drift_matrix_exists", paths.fm14_drift_matrix_rel, "file"),
        ("fm14_drift_fp_exists", paths.fm14_drift_fp_rel, "file"),
        ("fm14_battery_exists", paths.fm14_battery_rel, "file"),
    ]
    for check_id, rel, kind in presence_specs:
        abs_path = _abs(rel, base_dir=base_dir)
        present = os.path.isdir(abs_path) if kind == "dir" else os.path.isfile(abs_path)
        rows.append(
            _row(
                check_id=check_id,
                layer="nonseal_chain_continuity",
                path=rel,
                expected=f"{kind}_present",
                observed=f"present={present}",
                ok=present,
            )
        )
        checks[check_id] = present

    ext_fp: Dict[str, Any] = {}
    ext_path = _abs(paths.fm13_extension_fingerprint_rel, base_dir=base_dir)
    if os.path.isfile(ext_path):
        ext_fp = load_json(ext_path)
    ext_sha = str(
        (ext_fp.get("fingerprint") or {}).get("fingerprint_sha256") or ""
    )
    ext_ok = ext_sha == FROZEN_EXTENSION_FP_SHA256
    checks["nonseal_extension_fp_anchor"] = ext_ok
    rows.append(
        _row(
            check_id="nonseal_extension_fp_anchor",
            layer="nonseal_chain_continuity",
            path=paths.fm13_extension_fingerprint_rel,
            expected=FROZEN_EXTENSION_FP_SHA256,
            observed=ext_sha or "missing",
            ok=ext_ok,
        )
    )

    drift_fp_doc: Dict[str, Any] = {}
    drift_fp_path = _abs(paths.fm14_drift_fp_rel, base_dir=base_dir)
    if os.path.isfile(drift_fp_path):
        drift_fp_doc = load_json(drift_fp_path)
    drift_sha = str(
        (drift_fp_doc.get("fingerprint") or {}).get("fingerprint_sha256") or ""
    )
    drift_ok = drift_sha == FROZEN_DRIFT_FP_SHA256
    checks["nonseal_drift_fp_anchor"] = drift_ok
    rows.append(
        _row(
            check_id="nonseal_drift_fp_anchor",
            layer="nonseal_chain_continuity",
            path=paths.fm14_drift_fp_rel,
            expected=FROZEN_DRIFT_FP_SHA256,
            observed=drift_sha or "missing",
            ok=drift_ok,
        )
    )

    drift_seal: Dict[str, Any] = {}
    seal_path = _abs(paths.fm14_drift_seal_rel, base_dir=base_dir)
    if os.path.isfile(seal_path):
        drift_seal = load_json(seal_path)

    seal_task = str(drift_seal.get("task_id") or "").strip()
    seal_gate = str(drift_seal.get("gate") or "").strip()
    drift_detected = drift_seal.get("drift_detected", None)
    seal_ext_fp = str(drift_seal.get("frozen_extension_fp_sha256") or "").strip()
    seal_re_ext = str(drift_seal.get("recomputed_extension_fp_sha256") or "").strip()
    seal_chain_ext = drift_seal.get("seal_chain_extended", None)

    task_ok = seal_task == "C-FM-14"
    checks["nonseal_fm14_task_id"] = task_ok
    rows.append(
        _row(
            check_id="nonseal_fm14_task_id",
            layer="nonseal_chain_continuity",
            path=paths.fm14_drift_seal_rel,
            expected="C-FM-14",
            observed=seal_task or "missing",
            ok=task_ok,
        )
    )

    gate_ok = seal_gate == "PASS_OFFLINE"
    checks["nonseal_fm14_gate"] = gate_ok
    rows.append(
        _row(
            check_id="nonseal_fm14_gate",
            layer="nonseal_chain_continuity",
            expected="PASS_OFFLINE",
            observed=seal_gate or "missing",
            ok=gate_ok,
        )
    )

    no_drift_ok = drift_detected is False
    checks["nonseal_zero_drift"] = no_drift_ok
    rows.append(
        _row(
            check_id="nonseal_zero_drift",
            layer="nonseal_chain_continuity",
            expected="drift_detected=false",
            observed=(
                f"drift_detected={drift_detected}"
                if drift_detected is not None
                else "missing"
            ),
            ok=no_drift_ok,
        )
    )

    chain_fp_ok = (
        seal_ext_fp == FROZEN_EXTENSION_FP_SHA256
        and seal_re_ext == FROZEN_EXTENSION_FP_SHA256
        and ext_sha == FROZEN_EXTENSION_FP_SHA256
        and drift_sha == FROZEN_DRIFT_FP_SHA256
        and seal_chain_ext is False
    )
    checks["nonseal_fingerprint_continuity"] = chain_fp_ok
    rows.append(
        _row(
            check_id="nonseal_fingerprint_continuity",
            layer="nonseal_chain_continuity",
            expected="extension+drift anchors continuous across MOCK15/MOCK16",
            observed=(
                f"ext={ext_sha[:12]}…;seal_ext={seal_ext_fp[:12]}…;"
                f"drift={drift_sha[:12]}…;seal_ext_flag={seal_chain_ext}"
            ),
            ok=chain_fp_ok,
        )
    )

    mock15_isolated = is_allowed_mock_test_cleanup_path(
        _abs(paths.fm13_mock_root_rel, base_dir=base_dir), base_dir=base_dir
    )
    mock16_isolated = is_allowed_mock_test_cleanup_path(
        _abs(paths.fm14_mock_root_rel, base_dir=base_dir), base_dir=base_dir
    )
    iso_ok = mock15_isolated and mock16_isolated
    checks["nonseal_mock15_16_isolated"] = iso_ok
    rows.append(
        _row(
            check_id="nonseal_mock15_16_isolated",
            layer="nonseal_chain_continuity",
            expected="both_isolated_mock",
            observed=f"mock15={mock15_isolated};mock16={mock16_isolated}",
            ok=iso_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="nonseal_chain_continuity_all_pass",
            layer="nonseal_chain_continuity",
            expected="fm13_extension+fm14_drift_continuous",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["nonseal_chain_continuity_all_pass"] = all_ok
    return rows, checks, ext_fp, drift_seal


def build_dual_hold_seal_rows(
    *,
    paths: NonsealCommitBoundaryPaths,
    drift_seal: Dict[str, Any],
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """FM-13 extension packet 与 FM-14 drift seal 双层 KEEP_EXECUTE_FALSE。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    packet: Dict[str, Any] = {}
    packet_path = _abs(paths.fm13_packet_rel, base_dir=base_dir)
    if os.path.isfile(packet_path):
        packet = load_json(packet_path)

    def _hold_fields(src: Dict[str, Any], prefix: str, path: str) -> None:
        execute = src.get("execute_production_snapshot_rebuild", None)
        approved = src.get("approved_for_snapshot_rebuild", None)
        hold = str(src.get("hold_recommendation") or "").strip()
        ready_exec = src.get("ready_for_execute", None)
        decision = str(src.get("decision_status") or "").strip()
        idle_flag = src.get("idle_not_required_while_awaiting", None)
        seal_ext = src.get("seal_chain_extended", None)

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

        ready_ok = ready_exec is False
        checks[f"{prefix}_ready_for_execute_false"] = ready_ok
        rows.append(
            _row(
                check_id=f"{prefix}_ready_for_execute_false",
                layer="execute_hold_seal",
                expected="false",
                observed=str(ready_exec).lower() if ready_exec is not None else "missing",
                ok=ready_ok,
            )
        )

        decision_ok = decision == "AWAITING_HUMAN_EXECUTE_DECISION"
        checks[f"{prefix}_decision_awaiting"] = decision_ok
        rows.append(
            _row(
                check_id=f"{prefix}_decision_awaiting",
                layer="execute_hold_seal",
                expected="AWAITING_HUMAN_EXECUTE_DECISION",
                observed=decision or "missing",
                ok=decision_ok,
            )
        )

        idle_ok = idle_flag is True
        checks[f"{prefix}_idle_not_required"] = idle_ok
        rows.append(
            _row(
                check_id=f"{prefix}_idle_not_required",
                layer="execute_hold_seal",
                expected="true",
                observed=str(idle_flag).lower() if idle_flag is not None else "missing",
                ok=idle_ok,
            )
        )

        seal_ok = seal_ext is False
        checks[f"{prefix}_seal_not_extended"] = seal_ok
        rows.append(
            _row(
                check_id=f"{prefix}_seal_not_extended",
                layer="execute_hold_seal",
                expected="false",
                observed=str(seal_ext).lower() if seal_ext is not None else "missing",
                ok=seal_ok,
            )
        )

    _hold_fields(packet, "fm13_packet", paths.fm13_packet_rel)
    _hold_fields(drift_seal, "fm14_seal", paths.fm14_drift_seal_rel)

    self_ok = True
    checks["fm15_self_constants_hold"] = self_ok
    rows.append(
        _row(
            check_id="fm15_self_constants_hold",
            layer="execute_hold_seal",
            expected="execute=false;approved=false;idle_not_required=true",
            observed="execute=false;approved=false;idle_not_required=true",
            ok=self_ok,
            notes="c_fm15_hard_constants",
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="execute_hold_seal_all_pass",
            layer="execute_hold_seal",
            expected="dual_KEEP_EXECUTE_FALSE_sealed",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["execute_hold_seal_all_pass"] = all_ok
    return rows, checks, packet


def build_controller_readiness_rows(
    *,
    layer_gates_so_far: Dict[str, bool],
    fm13_packet: Dict[str, Any],
    drift_seal: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """
    Controller commit-boundary readiness：

    - offline nonseal 链 PASS
    - KEEP_EXECUTE_FALSE 仍成立
    - ready_for_commit（本包）≠ ready_for_execute
    - 明确禁止 verified / production_ready / 翻转 approved / 因 AWAITING IDLE
    """
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    offline_ok = all(layer_gates_so_far.values())
    checks["readiness_offline_chain_pass"] = offline_ok
    rows.append(
        _row(
            check_id="readiness_offline_chain_pass",
            layer="controller_readiness",
            expected="prior_layers_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in layer_gates_so_far.values() if v)}/"
            f"{len(layer_gates_so_far)}",
            ok=offline_ok,
        )
    )

    hold_ok = (
        str(fm13_packet.get("hold_recommendation") or "") == "KEEP_EXECUTE_FALSE"
        and str(drift_seal.get("hold_recommendation") or "") == "KEEP_EXECUTE_FALSE"
    )
    checks["readiness_hold_still_false"] = hold_ok
    rows.append(
        _row(
            check_id="readiness_hold_still_false",
            layer="controller_readiness",
            expected="KEEP_EXECUTE_FALSE",
            observed=(
                f"fm13={fm13_packet.get('hold_recommendation')};"
                f"fm14={drift_seal.get('hold_recommendation')}"
            ),
            ok=hold_ok,
        )
    )

    execute_blocked = (
        fm13_packet.get("execute_production_snapshot_rebuild") is False
        and drift_seal.get("execute_production_snapshot_rebuild") is False
        and fm13_packet.get("approved_for_snapshot_rebuild") is False
        and drift_seal.get("approved_for_snapshot_rebuild") is False
        and fm13_packet.get("ready_for_execute") is False
        and drift_seal.get("ready_for_execute") is False
    )
    checks["readiness_execute_still_blocked"] = execute_blocked
    rows.append(
        _row(
            check_id="readiness_execute_still_blocked",
            layer="controller_readiness",
            expected="execute=false;approved=false;ready_for_execute=false",
            observed="blocked" if execute_blocked else "NOT_BLOCKED",
            ok=execute_blocked,
        )
    )

    commit_ready = offline_ok and hold_ok and execute_blocked
    checks["readiness_commit_boundary_ready"] = commit_ready
    rows.append(
        _row(
            check_id="readiness_commit_boundary_ready",
            layer="controller_readiness",
            expected="ready_for_commit=true;ready_for_execute=false",
            observed=(
                f"ready_for_commit={str(commit_ready).lower()};"
                "ready_for_execute=false"
            ),
            ok=commit_ready,
        )
    )

    await_ok = (
        str(fm13_packet.get("decision_status") or "")
        == "AWAITING_HUMAN_EXECUTE_DECISION"
        and str(drift_seal.get("decision_status") or "")
        == "AWAITING_HUMAN_EXECUTE_DECISION"
        and fm13_packet.get("idle_not_required_while_awaiting") is True
        and drift_seal.get("idle_not_required_while_awaiting") is True
    )
    checks["readiness_await_idle_not_required"] = await_ok
    rows.append(
        _row(
            check_id="readiness_await_idle_not_required",
            layer="controller_readiness",
            expected="AWAITING + idle_not_required=true",
            observed=(
                f"fm13_decision={fm13_packet.get('decision_status')};"
                f"fm14_idle={drift_seal.get('idle_not_required_while_awaiting')}"
            ),
            ok=await_ok,
        )
    )

    seal_ok = (
        fm13_packet.get("seal_chain_extended") is False
        and drift_seal.get("seal_chain_extended") is False
    )
    checks["readiness_seal_not_extended"] = seal_ok
    rows.append(
        _row(
            check_id="readiness_seal_not_extended",
            layer="controller_readiness",
            expected="seal_chain_extended=false",
            observed=f"fm13={fm13_packet.get('seal_chain_extended')};"
            f"fm14={drift_seal.get('seal_chain_extended')}",
            ok=seal_ok,
        )
    )

    claims_ok = True  # 本包硬常量禁止 verified / production_ready
    checks["readiness_claims_still_forbidden"] = claims_ok
    rows.append(
        _row(
            check_id="readiness_claims_still_forbidden",
            layer="controller_readiness",
            expected="verified+production_ready forbidden",
            observed="forbidden_by_hard_constants",
            ok=claims_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="controller_readiness_all_pass",
            layer="controller_readiness",
            expected="commit_boundary_ready_execute_held",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["controller_readiness_all_pass"] = all_ok

    packet = {
        "packet_kind": "nonseal_extension_controller_commit_boundary",
        "task_id": TASK_ID,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "cninfo_calls": 0,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting": True,
        "seal_chain_extended": False,
        "ready_for_commit": commit_ready,
        "controller_action": "COMMIT_BOUNDARY_ONLY",
        "verified_claim_forbidden": True,
        "production_ready_claim_forbidden": True,
        "frozen_extension_fp_sha256": FROZEN_EXTENSION_FP_SHA256,
        "frozen_drift_fp_sha256": FROZEN_DRIFT_FP_SHA256,
        "notes": (
            "本包聚合非 seal FM-01..05+FM-12..14 并产出 controller commit-boundary "
            "就绪账本；KEEP_EXECUTE_FALSE；不覆盖 MOCK15/MOCK16；不翻转 "
            "approved_for_snapshot_rebuild；不得因 AWAITING 而 IDLE；"
            "生产 snapshot EXECUTE 仍须独立人批；本 executor 不 commit/push。"
        ),
    }
    return rows, checks, packet


def build_frozen_mock_isolation_rows(
    paths: NonsealCommitBoundaryPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离 battery：MOCK3–16 拒绝 · MOCK17 放行。"""
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

    mock17_prefix = frozen.get(THIS_TASK_ROOT_ID)
    mock17_listed = mock17_prefix is not None
    mock17_allowed = False
    if mock17_prefix:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock17_prefix,
                allow_root_ids=(THIS_TASK_ROOT_ID,),
                base_dir=base_dir,
            )
            mock17_allowed = True
        except RuntimeError:
            mock17_allowed = False
    checks["frozen_allow_mock17"] = mock17_listed and mock17_allowed
    rows.append(
        _row(
            check_id="frozen_allow_mock17",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=_rel(mock17_prefix, base_dir=base_dir) if mock17_prefix else "",
            expected="listed_and_allowed_when_in_allowlist",
            observed=f"listed={mock17_listed};allowed={mock17_allowed}",
            ok=mock17_listed and mock17_allowed,
            notes="ok" if mock17_listed and mock17_allowed else "mock17_allow_fail",
        )
    )

    out_ok = False
    out_detail = ""
    try:
        assert_fm15_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK17_or_ephemeral_allowed",
            observed=out_detail,
            ok=out_ok,
        )
    )

    mock16 = frozen.get("C-ROOT-MOCK16")
    mock16_still_frozen = False
    if mock16:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock16, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
            )
        except RuntimeError as exc:
            mock16_still_frozen = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock16_still_frozen"] = mock16_still_frozen
    rows.append(
        _row(
            check_id="mock16_still_frozen",
            layer="frozen_mock_isolation",
            root_id="C-ROOT-MOCK16",
            expected="fm14_mock16_not_writable_by_fm15",
            observed=f"refused={mock16_still_frozen}",
            ok=mock16_still_frozen,
            notes="ok" if mock16_still_frozen else "mock16_freeze_regressed",
        )
    )

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
            expected="fm13_mock15_not_writable_by_fm15",
            observed=f"refused={mock15_still_frozen}",
            ok=mock15_still_frozen,
            notes="ok" if mock15_still_frozen else "mock15_freeze_regressed",
        )
    )

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
            expected="seal_chain_not_writable_by_fm15",
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
            expected="MOCK3-16_blocked_MOCK17_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "frozen_isolation_fail",
        )
    )
    return rows, checks


def build_protected_csv_registry_rows(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected CSV：MOCK3–17 + AUTH1 注册一致性。"""
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

    mock15 = by_id.get("C-ROOT-MOCK15") or {}
    mock15_path = (mock15.get("path_pattern") or "").strip().rstrip("/")
    mock15_ok = mock15_path.endswith(
        "_mock_c_fm13_nonseal_cross_fm_mock_cohort_extension"
    ) or mock15_path == FM13_MOCK_ROOT_REL
    checks["protected_csv_mock15_path"] = mock15_ok
    rows.append(
        _row(
            check_id="protected_csv_mock15_path",
            layer="protected_csv_registry",
            root_id="C-ROOT-MOCK15",
            path=mock15_path,
            expected=FM13_MOCK_ROOT_REL,
            observed=mock15_path or "missing",
            ok=mock15_ok,
            notes="ok" if mock15_ok else "mock15_path_mismatch",
        )
    )

    mock16 = by_id.get("C-ROOT-MOCK16") or {}
    mock16_path = (mock16.get("path_pattern") or "").strip().rstrip("/")
    mock16_ok = mock16_path.endswith(
        "_mock_c_fm14_nonseal_extension_post_commit_drift_recheck"
    ) or mock16_path == FM14_MOCK_ROOT_REL
    checks["protected_csv_mock16_path"] = mock16_ok
    rows.append(
        _row(
            check_id="protected_csv_mock16_path",
            layer="protected_csv_registry",
            root_id="C-ROOT-MOCK16",
            path=mock16_path,
            expected=FM14_MOCK_ROOT_REL,
            observed=mock16_path or "missing",
            ok=mock16_ok,
            notes="ok" if mock16_ok else "mock16_path_mismatch",
        )
    )

    mock17 = by_id.get(THIS_TASK_ROOT_ID) or {}
    mock17_path = (mock17.get("path_pattern") or "").strip().rstrip("/")
    expected_path = DEFAULT_MOCK_OUTPUT_ROOT_REL
    mock17_ok = mock17_path.endswith(
        "_mock_c_fm15_nonseal_extension_controller_commit_boundary"
    ) or mock17_path == expected_path
    checks["protected_csv_mock17_path"] = mock17_ok
    rows.append(
        _row(
            check_id="protected_csv_mock17_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            path=mock17_path,
            expected=expected_path,
            observed=mock17_path or "missing",
            ok=mock17_ok,
            notes="ok" if mock17_ok else "mock17_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-17+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def write_boundary_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=BOUNDARY_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in BOUNDARY_MATRIX_FIELDS})


def fingerprint_boundary_matrix(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    """commit-boundary 矩阵结构指纹。"""
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


def run_nonseal_extension_controller_commit_boundary(
    *,
    paths: NonsealCommitBoundaryPaths = NonsealCommitBoundaryPaths(),
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-15 非 seal 扩展 controller commit-boundary（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_fm15_output_root(paths.output_root_rel, base_dir=base_dir)

    fm01 = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))
    fm05 = load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir))
    fm12 = load_json(_abs(paths.fm12_gate_json_rel, base_dir=base_dir))
    fm13 = load_json(_abs(paths.fm13_gate_json_rel, base_dir=base_dir))
    fm14 = load_json(_abs(paths.fm14_gate_json_rel, base_dir=base_dir))

    bat_rows, bat_checks = build_fm01_05_12_13_14_gate_battery_rows(
        fm01=fm01,
        fm02=fm02,
        fm03=fm03,
        fm04=fm04,
        fm05=fm05,
        fm12=fm12,
        fm13=fm13,
        fm14=fm14,
    )
    chain_rows, chain_checks, ext_fp, drift_seal = build_nonseal_chain_continuity_rows(
        paths=paths, base_dir=base_dir
    )
    hold_rows, hold_checks, fm13_packet = build_dual_hold_seal_rows(
        paths=paths, drift_seal=drift_seal, base_dir=base_dir
    )
    fr_rows, fr_checks = build_frozen_mock_isolation_rows(paths, base_dir=base_dir)

    prior_layer_bools = {
        "fm_gate_battery": all(bat_checks.values()),
        "nonseal_chain_continuity": all(chain_checks.values()),
        "execute_hold_seal": all(hold_checks.values()),
        "frozen_mock_isolation": all(fr_checks.values()),
    }
    ready_rows, ready_checks, readiness_packet = build_controller_readiness_rows(
        layer_gates_so_far=prior_layer_bools,
        fm13_packet=fm13_packet,
        drift_seal=drift_seal,
    )
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )

    matrix = (
        bat_rows + chain_rows + hold_rows + fr_rows + ready_rows + csv_rows
    )
    layer_gates = {
        "fm_gate_battery": (
            "PASS_OFFLINE" if all(bat_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "nonseal_chain_continuity": (
            "PASS_OFFLINE" if all(chain_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "execute_hold_seal": (
            "PASS_OFFLINE" if all(hold_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "frozen_mock_isolation": (
            "PASS_OFFLINE" if all(fr_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "controller_readiness": (
            "PASS_OFFLINE" if all(ready_checks.values()) else "FAIL_REVIEW_REQUIRED"
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

    os.makedirs(out_root, exist_ok=True)
    matrix_path = os.path.join(out_root, "boundary_matrix.csv")
    write_boundary_matrix_csv(matrix, matrix_path)
    fp = fingerprint_boundary_matrix(matrix)
    fp_path = os.path.join(out_root, "boundary_fingerprint.json")
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
                "frozen_drift_fp_sha256": FROZEN_DRIFT_FP_SHA256,
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
                "fm14_gate": fm14.get("gate"),
                "fm15_gate": overall,
                "cninfo_calls": 0,
                "seal_chain_extended": False,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    readiness_packet = dict(readiness_packet)
    readiness_packet["generated_at"] = generated_at
    readiness_packet["gate"] = overall
    readiness_packet["layer_gates"] = layer_gates
    readiness_packet["ready_for_commit"] = overall == "PASS_OFFLINE"
    readiness_path = os.path.join(
        out_root, "controller_commit_boundary_packet.json"
    )
    with open(readiness_path, "w", encoding="utf-8") as fh:
        json.dump(readiness_packet, fh, ensure_ascii=False, indent=2)
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
        "readiness_packet_path": _rel(readiness_path, base_dir=base_dir),
        "readiness_packet": readiness_packet,
        "fm13_extension_fingerprint": ext_fp,
        "fm14_drift_seal": drift_seal,
        "fm13_extension_packet": fm13_packet,
        "frozen_extension_fp_sha256": FROZEN_EXTENSION_FP_SHA256,
        "frozen_drift_fp_sha256": FROZEN_DRIFT_FP_SHA256,
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
            "fm14_gate_json": paths.fm14_gate_json_rel,
            "fm13_mock_root": paths.fm13_mock_root_rel,
            "fm14_mock_root": paths.fm14_mock_root_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
        },
    }
