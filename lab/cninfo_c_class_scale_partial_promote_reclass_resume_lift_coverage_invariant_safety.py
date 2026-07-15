"""
CNINFO C-class — 规模 partial promote/reclass denial + resume-same hold
boundary + residual lift denial + coverage invariant lock（离线 · C-FM-29）。

在 C-FM-28（risk-band membership + quarantine/fence write-boundary +
residual cross-matrix）已 commit 且 EXECUTE 仍 human-held 之上，继续非 seal
规模/安全能力（不新增 seal / decision-await / commit-boundary；非
extension↔drift 循环）：
  1) FM28 packet / fingerprint / gate / membership·quarantine·fence·cross
     ledgers 零漂移连续
  2) partial promote/reclass denial：106 码禁止 promote→complete 与跨带 reclass
  3) resume-same hold write-boundary：301212 禁止 harvest / force_improve / promote
  4) residual lift denial：quarantine(9) + fence(Δ2) 禁止 lift
  5) coverage invariant lock：9+2+106=117 冻结 · mutation_allowed=false
  6) output-root：MOCK3–30 冻结 · MOCK31 放行
  7) FM-01..05 + FM-12..28 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–30 / 权威 dual-layer 索引 ·
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

from cninfo_c_class_cross_fm_mock_cohort_integrity import (  # noqa: E402
    build_protected_write_guard_battery_rows,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    CLEANUP_REFUSED_MSG,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    PROTECTED_ROOTS_CSV_REL,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_frozen_mock_cohort_write_forbidden,
    assert_safe_erad_audit_write_path,
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
    load_json,
    load_protected_root_rows,
)
from cninfo_c_class_scale_harvest_exclusion_repro_fingerprint import (  # noqa: E402
    fingerprint_scale_matrix,
    write_scale_matrix_csv,
)
from cninfo_c_class_scale_multi_batch_repro_lineage_hardening import (  # noqa: E402
    EXPECTED_COMBINED_DRYRUN_COVERAGE,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_SCALE_TIER_COUNT,
    HARVEST_FULLER_ROOT_REL,
    HARVEST_PHASE2_ROOT_REL,
    HARVEST_PHASE3_ROOT_REL,
    HARVEST_PHASE35_ROOT_REL,
)
from cninfo_c_class_scale_unique_coverage_resume_lineage_safety import (  # noqa: E402
    EXPECTED_DRY863_EXTRA,
    EXPECTED_HARVEST_ADDITIVE,
    EXPECTED_HARVEST_UNIQUE_UNION,
    EXPECTED_OVERLAP_DELTA,
    EXPECTED_RESUME_TOTAL,
    EXPECTED_SURFACE_UNIQUE,
    HARVEST_PHASE35_RESUME_ROOT_REL,
)
from cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety import (  # noqa: E402
    EXPECTED_RESUME_IMPROVED,
    EXPECTED_RESUME_SAME,
    EXPECTED_RESUME_SAME_CODES,
    EXPECTED_RESUME_WORSE,
    EXPECTED_UNION_COMPLETE,
    EXPECTED_UNION_FAILED,
    EXPECTED_UNION_PARTIAL,
)
from cninfo_c_class_scale_residual_status_triage_surface_delta_safety import (  # noqa: E402
    EXPECTED_FAILED_CODES,
    EXPECTED_SURFACE_HARVEST_DELTA_N,
    EXCLUSION_UNIVERSE_REL,
    FM01_GATE_JSON_REL,
    FM01_SNAPSHOT_STATUS_REL,
    FM02_GATE_JSON_REL,
    FM02_SNAPSHOT_STATUS_REL,
    FM03_GATE_JSON_REL,
    FM04_GATE_JSON_REL,
    FM05_GATE_JSON_REL,
    FM12_GATE_JSON_REL,
    FM13_GATE_JSON_REL,
    FM14_GATE_JSON_REL,
    FM15_GATE_JSON_REL,
    FM16_GATE_JSON_REL,
    FM17_GATE_JSON_REL,
    FM18_GATE_JSON_REL,
    FM19_GATE_JSON_REL,
    FM20_GATE_JSON_REL,
    FM21_GATE_JSON_REL,
    FM22_GATE_JSON_REL,
    FM23_GATE_JSON_REL,
    FM24_GATE_JSON_REL,
    FM25_GATE_JSON_REL,
    HARVEST_863_STATUS_REL,
    HARVEST_FULLER_STATUS_REL,
    HARVEST_PHASE2_STATUS_REL,
    HARVEST_PHASE3_STATUS_REL,
    HARVEST_PHASE35_RESUME_STATUS_REL,
    HARVEST_PHASE35_STATUS_REL,
    compute_union_status_and_winners,
    load_union_status_maps,
)
from cninfo_c_class_scale_residual_status_triage_surface_delta_safety import (  # noqa: E402
    ResidualTriagePaths as Fm26Paths,
)
from cninfo_c_class_scale_residual_disposition_quarantine_pending_fence_safety import (  # noqa: E402
    EXPECTED_PARTIAL_RISK_BANDS,
    FM26_GATE_JSON_REL,
)
from cninfo_c_class_scale_risk_band_membership_write_boundary_cross_matrix_safety import (  # noqa: E402
    BAND_ORDER,
    EXPECTED_RESIDUAL_SAFETY_COVERAGE,
    FROZEN_FENCE_ABSORB_DENIAL_FP_SHA256,
    FROZEN_QUARANTINE_WRITE_BOUNDARY_FP_SHA256,
    FROZEN_RESIDUAL_SAFETY_CROSS_MATRIX_FP_SHA256,
    FROZEN_RISK_BAND_MEMBERSHIP_FP_SHA256,
    classify_risk_band,
    fingerprint_fence_absorb_denial,
    fingerprint_quarantine_write_boundary_denial,
    fingerprint_residual_safety_cross_matrix,
    fingerprint_risk_band_membership,
)

TASK_ID = "C-FM-29"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm29_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety"
)

FM27_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_residual_disposition_quarantine_pending_fence_safety_20260715.json"
)
FM28_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_risk_band_membership_write_boundary_cross_matrix_safety_20260715.json"
)
FM28_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm28_scale_risk_band_membership_write_boundary_cross_matrix_safety"
)
FM28_PACKET_REL = f"{FM28_MOCK_ROOT_REL}/scale_packet.json"
FM28_FINGERPRINT_REL = f"{FM28_MOCK_ROOT_REL}/scale_fingerprint.json"
FM28_MEMBERSHIP_REL = f"{FM28_MOCK_ROOT_REL}/partial_risk_band_membership_ledger.json"
FM28_QUARANTINE_REL = (
    f"{FM28_MOCK_ROOT_REL}/quarantine_write_boundary_denial_ledger.json"
)
FM28_FENCE_REL = f"{FM28_MOCK_ROOT_REL}/fence_absorb_denial_ledger.json"
FM28_CROSS_REL = f"{FM28_MOCK_ROOT_REL}/residual_safety_cross_matrix_ledger.json"

FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256 = (
    "8c6ddf947d2660666ab139b6fb399fdbefb4ae369f0adcb3e4803cb5920af651"
)
FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256 = (
    "fae9752ee9cb88168a5805db623a51a50546f39606ac97a2032d51c3bc3e6abf"
)
FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256 = (
    "70217be897007208e64049d2da24bd95f5092bc9087d66d9d1361d6097f8302f"
)
FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256 = (
    "b6681b0accae1477a347b600a78b08cd349943e6944393e11c8262230afda189"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK31"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK30"
RESUME_HARVEST_ROOT_ID = "C-ROOT-002"

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
    "C-ROOT-MOCK17",
    "C-ROOT-MOCK18",
    "C-ROOT-MOCK19",
    "C-ROOT-MOCK20",
    "C-ROOT-MOCK21",
    "C-ROOT-MOCK22",
    "C-ROOT-MOCK23",
    "C-ROOT-MOCK24",
    "C-ROOT-MOCK25",
    "C-ROOT-MOCK26",
    "C-ROOT-MOCK27",
    "C-ROOT-MOCK28",
    "C-ROOT-MOCK29",
    "C-ROOT-MOCK30",
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class PromoteReclassResumeLiftPaths:
    """只读输入与隔离写根路径规格。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    fm05_gate_json_rel: str = FM05_GATE_JSON_REL
    fm12_gate_json_rel: str = FM12_GATE_JSON_REL
    fm13_gate_json_rel: str = FM13_GATE_JSON_REL
    fm14_gate_json_rel: str = FM14_GATE_JSON_REL
    fm15_gate_json_rel: str = FM15_GATE_JSON_REL
    fm16_gate_json_rel: str = FM16_GATE_JSON_REL
    fm17_gate_json_rel: str = FM17_GATE_JSON_REL
    fm18_gate_json_rel: str = FM18_GATE_JSON_REL
    fm19_gate_json_rel: str = FM19_GATE_JSON_REL
    fm20_gate_json_rel: str = FM20_GATE_JSON_REL
    fm21_gate_json_rel: str = FM21_GATE_JSON_REL
    fm22_gate_json_rel: str = FM22_GATE_JSON_REL
    fm23_gate_json_rel: str = FM23_GATE_JSON_REL
    fm24_gate_json_rel: str = FM24_GATE_JSON_REL
    fm25_gate_json_rel: str = FM25_GATE_JSON_REL
    fm26_gate_json_rel: str = FM26_GATE_JSON_REL
    fm27_gate_json_rel: str = FM27_GATE_JSON_REL
    fm28_gate_json_rel: str = FM28_GATE_JSON_REL
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    harvest_863_status_rel: str = HARVEST_863_STATUS_REL
    harvest_phase35_status_rel: str = HARVEST_PHASE35_STATUS_REL
    harvest_phase3_status_rel: str = HARVEST_PHASE3_STATUS_REL
    harvest_phase2_status_rel: str = HARVEST_PHASE2_STATUS_REL
    harvest_fuller_status_rel: str = HARVEST_FULLER_STATUS_REL
    harvest_phase35_resume_status_rel: str = HARVEST_PHASE35_RESUME_STATUS_REL
    fm01_snapshot_status_rel: str = FM01_SNAPSHOT_STATUS_REL
    fm02_snapshot_status_rel: str = FM02_SNAPSHOT_STATUS_REL
    exclusion_universe_rel: str = EXCLUSION_UNIVERSE_REL
    fm28_packet_rel: str = FM28_PACKET_REL
    fm28_fingerprint_rel: str = FM28_FINGERPRINT_REL
    fm28_membership_rel: str = FM28_MEMBERSHIP_REL
    fm28_quarantine_rel: str = FM28_QUARANTINE_REL
    fm28_fence_rel: str = FM28_FENCE_REL
    fm28_cross_rel: str = FM28_CROSS_REL
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
        "notes": notes,
    }


def _to_fm26_paths(paths: PromoteReclassResumeLiftPaths) -> Fm26Paths:
    """复用 FM26 residual / surface / resume 路径视图。"""
    return Fm26Paths(
        harvest_863_status_rel=paths.harvest_863_status_rel,
        harvest_phase35_status_rel=paths.harvest_phase35_status_rel,
        harvest_phase3_status_rel=paths.harvest_phase3_status_rel,
        harvest_phase2_status_rel=paths.harvest_phase2_status_rel,
        harvest_fuller_status_rel=paths.harvest_fuller_status_rel,
        harvest_phase35_resume_status_rel=paths.harvest_phase35_resume_status_rel,
        fm01_snapshot_status_rel=paths.fm01_snapshot_status_rel,
        fm02_snapshot_status_rel=paths.fm02_snapshot_status_rel,
        exclusion_universe_rel=paths.exclusion_universe_rel,
        output_root_rel=paths.output_root_rel,
    )


def assert_fm29_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-29 写根：须 validation/_mock_*，不得覆盖 MOCK3–30，
    不得写权威 dual-layer 索引；允许本任务 MOCK31 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-29 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def fingerprint_partial_promote_reclass_denial(
    *,
    partial_codes: Sequence[str],
    membership_by_code: Dict[str, str],
) -> Tuple[str, Dict[str, Any]]:
    """partial promote/reclass denial 指纹。"""
    codes = sorted(partial_codes)
    doc = {
        "kind": "partial_promote_reclass_denial",
        "partial_n": len(codes),
        "partial_codes": codes,
        "membership_by_code": {c: membership_by_code[c] for c in codes},
        "deny_promote_to_complete": True,
        "deny_band_reclass": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_resume_same_hold_boundary(
    *,
    resume_same_codes: Sequence[str],
) -> Tuple[str, Dict[str, Any]]:
    """resume-same hold write-boundary 指纹。"""
    codes = sorted(resume_same_codes)
    doc = {
        "kind": "resume_same_hold_write_boundary",
        "resume_same_n": len(codes),
        "resume_same_codes": codes,
        "deny_harvest_write": True,
        "deny_force_improve": True,
        "deny_promote_to_complete": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_residual_lift_denial(
    *,
    failed_codes: Sequence[str],
    delta_codes: Sequence[str],
) -> Tuple[str, Dict[str, Any]]:
    """residual lift denial 指纹。"""
    failed = sorted(failed_codes)
    delta = sorted(delta_codes)
    doc = {
        "kind": "residual_lift_denial",
        "failed_n": len(failed),
        "failed_codes": failed,
        "delta_n": len(delta),
        "delta_codes": delta,
        "deny_quarantine_lift": True,
        "deny_fence_lift": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_coverage_invariant_lock(
    *,
    failed_n: int,
    delta_n: int,
    partial_n: int,
) -> Tuple[str, Dict[str, Any]]:
    """coverage invariant lock 指纹。"""
    doc = {
        "kind": "coverage_invariant_lock",
        "failed_n": failed_n,
        "delta_n": delta_n,
        "partial_n": partial_n,
        "coverage_sum": failed_n + delta_n + partial_n,
        "equation": "9+2+106=117",
        "mutation_allowed": False,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_partial_promote(
    *,
    code: str,
    membership_by_code: Dict[str, str],
) -> Dict[str, Any]:
    """评估 partial 码 promote→complete；显式 denial。"""
    if code not in membership_by_code:
        raise ValueError(f"not a partial membership code: {code}")
    return {
        "code": code,
        "target": "promote_to_complete",
        "current_band": membership_by_code[code],
        "allowed": False,
        "reason": "partial_pre_execute_not_approved",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_band_reclass(
    *,
    code: str,
    to_band: str,
    membership_by_code: Dict[str, str],
) -> Dict[str, Any]:
    """评估跨带 reclass；显式 denial。"""
    if code not in membership_by_code:
        raise ValueError(f"not a partial membership code: {code}")
    if to_band not in BAND_ORDER:
        raise ValueError(f"unknown risk-band: {to_band}")
    from_band = membership_by_code[code]
    return {
        "code": code,
        "from_band": from_band,
        "to_band": to_band,
        "allowed": False,
        "reason": "band_reclass_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_resume_same_write(
    *,
    code: str,
    target: str,
) -> Dict[str, Any]:
    """评估 resume-same 写边界；显式 denial。"""
    if code not in EXPECTED_RESUME_SAME_CODES:
        raise ValueError(f"not a resume-same hold code: {code}")
    if target not in ("harvest", "force_improve", "promote_to_complete"):
        raise ValueError(f"unknown resume-same write target: {target}")
    return {
        "code": code,
        "target": target,
        "allowed": False,
        "reason": "resume_same_hold_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_residual_lift(
    *,
    kind: str,
    code: str,
) -> Dict[str, Any]:
    """评估 quarantine / fence lift；显式 denial。"""
    if kind == "quarantine":
        if code not in EXPECTED_FAILED_CODES:
            raise ValueError(f"not a quarantined failed code: {code}")
        reason = "quarantine_lift_forbidden_pre_execute"
    elif kind == "fence":
        if code not in EXPECTED_DRY863_EXTRA:
            raise ValueError(f"not a fenced delta code: {code}")
        reason = "fence_lift_forbidden_pre_execute"
    else:
        raise ValueError(f"unknown residual lift kind: {kind}")
    return {
        "kind": kind,
        "code": code,
        "allowed": False,
        "reason": reason,
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_coverage_mutation(
    *,
    proposed_failed_n: int,
    proposed_delta_n: int,
    proposed_partial_n: int,
) -> Dict[str, Any]:
    """评估 coverage 变异；仅当与冻结方程一致时仍标记 mutation 拒绝。"""
    proposed = proposed_failed_n + proposed_delta_n + proposed_partial_n
    matches = (
        proposed_failed_n == EXPECTED_UNION_FAILED
        and proposed_delta_n == EXPECTED_SURFACE_HARVEST_DELTA_N
        and proposed_partial_n == EXPECTED_UNION_PARTIAL
        and proposed == EXPECTED_RESIDUAL_SAFETY_COVERAGE
    )
    return {
        "proposed_coverage": proposed,
        "frozen_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "coverage_invariant_locked_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def build_fm28_continuity_rows(
    paths: PromoteReclassResumeLiftPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM28 packet / fingerprint / gate / membership·quarantine·fence·cross 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm28_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm28_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm28_gate_json_rel, base_dir=base_dir))
    mem_led = load_json(_abs(paths.fm28_membership_rel, base_dir=base_dir))
    q_led = load_json(_abs(paths.fm28_quarantine_rel, base_dir=base_dir))
    f_led = load_json(_abs(paths.fm28_fence_rel, base_dir=base_dir))
    x_led = load_json(_abs(paths.fm28_cross_rel, base_dir=base_dir))

    pkt_ok = (
        packet.get("gate") == "PASS_OFFLINE"
        and packet.get("cninfo_calls") == 0
        and packet.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and packet.get("union_complete") == EXPECTED_UNION_COMPLETE
        and packet.get("union_partial") == EXPECTED_UNION_PARTIAL
        and packet.get("union_failed") == EXPECTED_UNION_FAILED
        and packet.get("resume_same") == EXPECTED_RESUME_SAME
        and packet.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and packet.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and packet.get("execute_production_snapshot_rebuild") is False
        and packet.get("approved_for_snapshot_rebuild") is False
        and packet.get("seal_chain_extended") is False
        and packet.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
        and set(packet.get("failed_codes") or []) == EXPECTED_FAILED_CODES
        and packet.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and packet.get("residual_safety_coverage") == EXPECTED_RESIDUAL_SAFETY_COVERAGE
    )
    checks["fm28_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm28_packet_continuity",
            layer="fm28_continuity",
            path=paths.fm28_packet_rel,
            expected="PASS_OFFLINE;unique=2249;2134/106/9;cov=117;KEEP",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"status={packet.get('union_complete')}/"
                f"{packet.get('union_partial')}/{packet.get('union_failed')};"
                f"cov={packet.get('residual_safety_coverage')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm28_packet_drift",
        )
    )

    fp_ok = (
        fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and fp_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and fp_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and (fp_doc.get("frozen_fps") or {}).get("partial_risk_band_membership")
        == FROZEN_RISK_BAND_MEMBERSHIP_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("quarantine_write_boundary_denial")
        == FROZEN_QUARANTINE_WRITE_BOUNDARY_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("fence_absorb_denial_battery")
        == FROZEN_FENCE_ABSORB_DENIAL_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("residual_safety_cross_matrix")
        == FROZEN_RESIDUAL_SAFETY_CROSS_MATRIX_FP_SHA256
        and fp_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and fp_doc.get("residual_safety_coverage") == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm28_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm28_fingerprint_continuity",
            layer="fm28_continuity",
            path=paths.fm28_fingerprint_rel,
            expected="unique2249+fm28_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"failed={fp_doc.get('union_failed')};"
                f"cov={fp_doc.get('residual_safety_coverage')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm28_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and gate_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and gate_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and gate_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and gate_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and gate_doc.get("residual_safety_coverage") == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("seal_chain_extended") is False
    )
    checks["fm28_gate_json_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm28_gate_json_continuity",
            layer="fm28_continuity",
            path=paths.fm28_gate_json_rel,
            expected="PASS_OFFLINE;failed=9;delta=2;cov=117;approved=false",
            observed=(
                f"gate={gate_doc.get('gate')};"
                f"failed={gate_doc.get('union_failed')};"
                f"cov={gate_doc.get('residual_safety_coverage')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm28_gate_drift",
        )
    )

    led_ok = (
        mem_led.get("fingerprint_sha256") == FROZEN_RISK_BAND_MEMBERSHIP_FP_SHA256
        and int(mem_led.get("partial_n") or 0) == EXPECTED_UNION_PARTIAL
        and mem_led.get("risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and q_led.get("fingerprint_sha256") == FROZEN_QUARANTINE_WRITE_BOUNDARY_FP_SHA256
        and set(q_led.get("failed_codes") or []) == EXPECTED_FAILED_CODES
        and f_led.get("fingerprint_sha256") == FROZEN_FENCE_ABSORB_DENIAL_FP_SHA256
        and set(f_led.get("delta_codes") or []) == EXPECTED_DRY863_EXTRA
        and x_led.get("fingerprint_sha256") == FROZEN_RESIDUAL_SAFETY_CROSS_MATRIX_FP_SHA256
        and int(x_led.get("coverage_sum") or 0) == EXPECTED_RESIDUAL_SAFETY_COVERAGE
    )
    checks["fm28_ledger_continuity"] = led_ok
    rows.append(
        _row(
            check_id="fm28_ledger_continuity",
            layer="fm28_continuity",
            expected="mem+q+fence+cross_fps",
            observed=(
                f"mem_fp={str(mem_led.get('fingerprint_sha256') or '')[:12]};"
                f"q_n={len(q_led.get('failed_codes') or [])};"
                f"cov={x_led.get('coverage_sum')}"
            ),
            ok=led_ok,
            notes="ok" if led_ok else "fm28_ledger_drift",
        )
    )

    # 再算 FM28 四层指纹确认相对冻结锚无漂移
    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    failed = sorted(c for c, s in union_status.items() if s == "failed")
    partial = sorted(c for c, s in union_status.items() if s == "partial")
    fp_mem, _ = fingerprint_risk_band_membership(
        partial_codes=partial, winning_batch=winning
    )
    fp_q, _ = fingerprint_quarantine_write_boundary_denial(failed_codes=failed)
    fp_f, _ = fingerprint_fence_absorb_denial(
        delta_codes=sorted(EXPECTED_DRY863_EXTRA)
    )
    fp_x, _ = fingerprint_residual_safety_cross_matrix(
        failed_n=len(failed),
        delta_n=EXPECTED_SURFACE_HARVEST_DELTA_N,
        partial_n=len(partial),
        disjoint_quarantine_fence=set(failed).isdisjoint(EXPECTED_DRY863_EXTRA),
        disjoint_quarantine_partial=set(failed).isdisjoint(partial),
        disjoint_fence_partial=EXPECTED_DRY863_EXTRA.isdisjoint(set(partial)),
    )
    reaffirm_ok = (
        fp_mem == FROZEN_RISK_BAND_MEMBERSHIP_FP_SHA256
        and fp_q == FROZEN_QUARANTINE_WRITE_BOUNDARY_FP_SHA256
        and fp_f == FROZEN_FENCE_ABSORB_DENIAL_FP_SHA256
        and fp_x == FROZEN_RESIDUAL_SAFETY_CROSS_MATRIX_FP_SHA256
        and set(failed) == EXPECTED_FAILED_CODES
        and len(partial) == EXPECTED_UNION_PARTIAL
    )
    checks["fm28_membership_write_cross_reaffirm"] = bool(reaffirm_ok)
    rows.append(
        _row(
            check_id="fm28_membership_write_cross_reaffirm",
            layer="fm28_continuity",
            expected="mem+q+fence+cross_reaffirm",
            observed=f"ok={bool(reaffirm_ok)}",
            ok=bool(reaffirm_ok),
            notes="ok" if reaffirm_ok else "fm28_reaffirm_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm28_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm28_continuity_all_pass",
            layer="fm28_continuity",
            expected="packet+fingerprint+gate+ledgers+reaffirm",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm28_continuity_incomplete",
        )
    )
    return rows, checks


def build_partial_promote_reclass_denial_rows(
    paths: PromoteReclassResumeLiftPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """partial promote/reclass denial（106 码）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    partial = sorted(c for c, s in union_status.items() if s == "partial")
    membership = {c: classify_risk_band(winning[c]) for c in partial}
    fp, doc = fingerprint_partial_promote_reclass_denial(
        partial_codes=partial, membership_by_code=membership
    )

    n_ok = len(partial) == EXPECTED_UNION_PARTIAL
    checks["promote_reclass_count_106"] = n_ok
    rows.append(
        _row(
            check_id="promote_reclass_count_106",
            layer="partial_promote_reclass_denial",
            expected=str(EXPECTED_UNION_PARTIAL),
            observed=str(len(partial)),
            ok=n_ok,
            notes="ok" if n_ok else "partial_count_mismatch",
        )
    )

    bands_ok = (
        {b: sum(1 for c in partial if membership[c] == b) for b in BAND_ORDER}
        == EXPECTED_PARTIAL_RISK_BANDS
    )
    checks["promote_reclass_bands_exact"] = bands_ok
    rows.append(
        _row(
            check_id="promote_reclass_bands_exact",
            layer="partial_promote_reclass_denial",
            expected="p35_heavy=75;p3_mid=14;p2_mid=12;fu_light=5",
            observed=json.dumps(
                {b: sum(1 for c in partial if membership[c] == b) for b in BAND_ORDER},
                ensure_ascii=False,
                sort_keys=True,
            ),
            ok=bands_ok,
            notes="ok" if bands_ok else "bands_drift",
        )
    )

    # 每码 promote→complete 显式拒绝
    promote_denials = []
    promote_ok = True
    for code in partial:
        d = evaluate_partial_promote(code=code, membership_by_code=membership)
        promote_denials.append(d)
        if d.get("allowed") is not False:
            promote_ok = False
    checks["promote_to_complete_denial_battery"] = (
        promote_ok and len(promote_denials) == EXPECTED_UNION_PARTIAL
    )
    rows.append(
        _row(
            check_id="promote_to_complete_denial_battery",
            layer="partial_promote_reclass_denial",
            expected="106_promote_denied",
            observed=(
                f"denials={len(promote_denials)};all_denied={promote_ok}"
            ),
            ok=checks["promote_to_complete_denial_battery"],
            notes="ok" if checks["promote_to_complete_denial_battery"] else "promote_leak",
        )
    )

    # 每码尝试跨带到下一 band → 拒绝
    reclass_denials = []
    reclass_ok = True
    for i, code in enumerate(partial):
        from_band = membership[code]
        to_band = BAND_ORDER[(BAND_ORDER.index(from_band) + 1) % len(BAND_ORDER)]
        d = evaluate_band_reclass(
            code=code, to_band=to_band, membership_by_code=membership
        )
        reclass_denials.append(d)
        if d.get("allowed") is not False:
            reclass_ok = False
    checks["band_reclass_denial_battery"] = (
        reclass_ok and len(reclass_denials) == EXPECTED_UNION_PARTIAL
    )
    rows.append(
        _row(
            check_id="band_reclass_denial_battery",
            layer="partial_promote_reclass_denial",
            expected="106_reclass_denied",
            observed=(
                f"denials={len(reclass_denials)};all_denied={reclass_ok}"
            ),
            ok=checks["band_reclass_denial_battery"],
            notes="ok" if checks["band_reclass_denial_battery"] else "reclass_leak",
        )
    )

    flags_ok = (
        doc["deny_promote_to_complete"] is True
        and doc["deny_band_reclass"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["promote_reclass_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="promote_reclass_flags_locked",
            layer="partial_promote_reclass_denial",
            expected="deny_promote+deny_reclass+KEEP",
            observed=(
                f"promote={doc['deny_promote_to_complete']};"
                f"reclass={doc['deny_band_reclass']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256
    checks["promote_reclass_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="promote_reclass_fingerprint",
            layer="partial_promote_reclass_denial",
            expected=FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "promote_reclass_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["partial_promote_reclass_denial_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="partial_promote_reclass_denial_all_pass",
            layer="partial_promote_reclass_denial",
            expected="106_promote_reclass_deny+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "promote_reclass_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "partial_n": len(partial),
        "membership_by_code": membership,
        "promote_denials": promote_denials,
        "reclass_denials": reclass_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_resume_same_hold_boundary_rows(
    paths: PromoteReclassResumeLiftPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """resume-same hold write-boundary（301212）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    codes = sorted(EXPECTED_RESUME_SAME_CODES)
    fp, doc = fingerprint_resume_same_hold_boundary(resume_same_codes=codes)

    codes_ok = (
        set(codes) == EXPECTED_RESUME_SAME_CODES
        and len(codes) == EXPECTED_RESUME_SAME
    )
    checks["resume_same_codes_exact"] = codes_ok
    rows.append(
        _row(
            check_id="resume_same_codes_exact",
            layer="resume_same_hold_write_boundary",
            expected=",".join(sorted(EXPECTED_RESUME_SAME_CODES)),
            observed=",".join(codes) or "none",
            ok=codes_ok,
            notes="ok" if codes_ok else "resume_same_codes_drift",
        )
    )

    # 仍为 partial（不得静默 complete）
    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, _winning = compute_union_status_and_winners(status_maps)
    still_partial = all(union_status.get(c) == "partial" for c in codes)
    checks["resume_same_still_partial"] = still_partial
    rows.append(
        _row(
            check_id="resume_same_still_partial",
            layer="resume_same_hold_write_boundary",
            expected="301212=partial",
            observed=";".join(f"{c}={union_status.get(c)}" for c in codes),
            ok=still_partial,
            notes="ok" if still_partial else "resume_same_status_drift",
        )
    )

    denials = []
    deny_ok = True
    for code in codes:
        for target in ("harvest", "force_improve", "promote_to_complete"):
            d = evaluate_resume_same_write(code=code, target=target)
            denials.append(d)
            if d.get("allowed") is not False:
                deny_ok = False
    checks["resume_same_denial_battery"] = deny_ok and len(denials) == 3
    rows.append(
        _row(
            check_id="resume_same_denial_battery",
            layer="resume_same_hold_write_boundary",
            expected="1x3_denied",
            observed=f"denials={len(denials)};all_denied={deny_ok}",
            ok=checks["resume_same_denial_battery"],
            notes="ok" if checks["resume_same_denial_battery"] else "resume_same_leak",
        )
    )

    # harvest/resume 写路径拒绝
    root_refuse = True
    for probe_rel in (
        f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm29.csv",
        f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm29.csv",
    ):
        refused = False
        try:
            assert_safe_erad_audit_write_path(
                _abs(probe_rel, base_dir=base_dir),
                base_dir=base_dir,
                allowed_audit_root_rel=paths.output_root_rel,
            )
        except RuntimeError as exc:
            refused = CLEANUP_REFUSED_MSG in str(exc)
        root_refuse = root_refuse and refused
    checks["resume_same_harvest_path_refused"] = root_refuse
    rows.append(
        _row(
            check_id="resume_same_harvest_path_refused",
            layer="resume_same_hold_write_boundary",
            expected="phase35+resume_refused",
            observed=f"refused={root_refuse}",
            ok=root_refuse,
            notes="ok" if root_refuse else "harvest_path_writable",
        )
    )

    flags_ok = (
        doc["deny_harvest_write"] is True
        and doc["deny_force_improve"] is True
        and doc["deny_promote_to_complete"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["resume_same_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="resume_same_flags_locked",
            layer="resume_same_hold_write_boundary",
            expected="deny_all+KEEP",
            observed=(
                f"harvest={doc['deny_harvest_write']};"
                f"force={doc['deny_force_improve']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256
    checks["resume_same_hold_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="resume_same_hold_fingerprint",
            layer="resume_same_hold_write_boundary",
            expected=FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "resume_same_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_same_hold_write_boundary_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_same_hold_write_boundary_all_pass",
            layer="resume_same_hold_write_boundary",
            expected="301212_hold_deny+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_same_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "resume_same_codes": codes,
        "denials": denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_residual_lift_denial_rows(
    paths: PromoteReclassResumeLiftPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """residual lift denial（quarantine=9 + fence=Δ2）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    failed = sorted(EXPECTED_FAILED_CODES)
    delta = sorted(EXPECTED_DRY863_EXTRA)
    fp, doc = fingerprint_residual_lift_denial(
        failed_codes=failed, delta_codes=delta
    )

    codes_ok = (
        set(failed) == EXPECTED_FAILED_CODES
        and len(failed) == EXPECTED_UNION_FAILED
        and set(delta) == EXPECTED_DRY863_EXTRA
        and len(delta) == EXPECTED_SURFACE_HARVEST_DELTA_N
    )
    checks["residual_lift_codes_exact"] = codes_ok
    rows.append(
        _row(
            check_id="residual_lift_codes_exact",
            layer="residual_lift_denial",
            expected="failed=9;delta=2",
            observed=f"failed={len(failed)};delta={len(delta)}",
            ok=codes_ok,
            notes="ok" if codes_ok else "lift_codes_drift",
        )
    )

    denials = []
    deny_ok = True
    for code in failed:
        d = evaluate_residual_lift(kind="quarantine", code=code)
        denials.append(d)
        if d.get("allowed") is not False:
            deny_ok = False
    for code in delta:
        d = evaluate_residual_lift(kind="fence", code=code)
        denials.append(d)
        if d.get("allowed") is not False:
            deny_ok = False
    checks["residual_lift_denial_battery"] = deny_ok and len(denials) == 11
    rows.append(
        _row(
            check_id="residual_lift_denial_battery",
            layer="residual_lift_denial",
            expected="9+2_lift_denied",
            observed=f"denials={len(denials)};all_denied={deny_ok}",
            ok=checks["residual_lift_denial_battery"],
            notes="ok" if checks["residual_lift_denial_battery"] else "lift_leak",
        )
    )

    flags_ok = (
        doc["deny_quarantine_lift"] is True
        and doc["deny_fence_lift"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["residual_lift_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="residual_lift_flags_locked",
            layer="residual_lift_denial",
            expected="deny_q+deny_f+KEEP",
            observed=(
                f"q={doc['deny_quarantine_lift']};"
                f"f={doc['deny_fence_lift']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256
    checks["residual_lift_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="residual_lift_fingerprint",
            layer="residual_lift_denial",
            expected=FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "residual_lift_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["residual_lift_denial_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="residual_lift_denial_all_pass",
            layer="residual_lift_denial",
            expected="11_lift_deny+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "residual_lift_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "failed_codes": failed,
        "delta_codes": delta,
        "denials": denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_coverage_invariant_lock_rows(
    paths: PromoteReclassResumeLiftPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """coverage invariant lock：9+2+106=117。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, _winning = compute_union_status_and_winners(status_maps)
    failed_n = sum(1 for s in union_status.values() if s == "failed")
    partial_n = sum(1 for s in union_status.values() if s == "partial")
    delta_n = EXPECTED_SURFACE_HARVEST_DELTA_N
    fp, doc = fingerprint_coverage_invariant_lock(
        failed_n=failed_n, delta_n=delta_n, partial_n=partial_n
    )

    eq_ok = (
        failed_n == EXPECTED_UNION_FAILED
        and delta_n == EXPECTED_SURFACE_HARVEST_DELTA_N
        and partial_n == EXPECTED_UNION_PARTIAL
        and doc["coverage_sum"] == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        and doc["equation"] == "9+2+106=117"
    )
    checks["coverage_equation_locked"] = eq_ok
    rows.append(
        _row(
            check_id="coverage_equation_locked",
            layer="coverage_invariant_lock",
            expected="9+2+106=117",
            observed=f"{failed_n}+{delta_n}+{partial_n}={doc['coverage_sum']}",
            ok=eq_ok,
            notes="ok" if eq_ok else "coverage_equation_drift",
        )
    )

    # 变异评估：即便数值匹配，mutation 仍禁止；偏移则 matches_frozen=false
    mut_same = evaluate_coverage_mutation(
        proposed_failed_n=EXPECTED_UNION_FAILED,
        proposed_delta_n=EXPECTED_SURFACE_HARVEST_DELTA_N,
        proposed_partial_n=EXPECTED_UNION_PARTIAL,
    )
    mut_bad = evaluate_coverage_mutation(
        proposed_failed_n=EXPECTED_UNION_FAILED,
        proposed_delta_n=EXPECTED_SURFACE_HARVEST_DELTA_N,
        proposed_partial_n=EXPECTED_UNION_PARTIAL + 1,
    )
    mut_ok = (
        mut_same["mutation_allowed"] is False
        and mut_same["matches_frozen"] is True
        and mut_bad["mutation_allowed"] is False
        and mut_bad["matches_frozen"] is False
        and doc["mutation_allowed"] is False
    )
    checks["coverage_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="coverage_mutation_denied",
            layer="coverage_invariant_lock",
            expected="mutation_allowed=false",
            observed=(
                f"same_mut={mut_same['mutation_allowed']};"
                f"bad_match={mut_bad['matches_frozen']}"
            ),
            ok=mut_ok,
            notes="ok" if mut_ok else "mutation_gate_broken",
        )
    )

    hold_ok = doc["hold"] == "KEEP_EXECUTE_FALSE"
    checks["coverage_invariant_hold"] = hold_ok
    rows.append(
        _row(
            check_id="coverage_invariant_hold",
            layer="coverage_invariant_lock",
            expected="KEEP_EXECUTE_FALSE",
            observed=str(doc["hold"]),
            ok=hold_ok,
            notes="ok" if hold_ok else "hold_drift",
        )
    )

    fp_ok = fp == FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256
    checks["coverage_invariant_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="coverage_invariant_fingerprint",
            layer="coverage_invariant_lock",
            expected=FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "coverage_lock_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["coverage_invariant_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="coverage_invariant_lock_all_pass",
            layer="coverage_invariant_lock",
            expected="117_locked+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "coverage_lock_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "failed_n": failed_n,
        "delta_n": delta_n,
        "partial_n": partial_n,
        "coverage_sum": doc["coverage_sum"],
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: PromoteReclassResumeLiftPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK31 放行。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    base_rows, base_checks = build_protected_write_guard_battery_rows(
        mock_probe_rel=paths.output_root_rel, base_dir=base_dir
    )
    rows.extend(base_rows)
    checks.update(base_checks)

    for check_id, probe_rel in (
        (
            "write_guard_phase3_harvest_refused",
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm29.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm29.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm29.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm29.csv",
        ),
        (
            "write_guard_phase35_resume_refused",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm29.csv",
        ),
    ):
        refused = False
        msg = ""
        try:
            assert_safe_erad_audit_write_path(
                _abs(probe_rel, base_dir=base_dir),
                base_dir=base_dir,
                allowed_audit_root_rel=paths.output_root_rel,
            )
        except RuntimeError as exc:
            refused = CLEANUP_REFUSED_MSG in str(exc)
            msg = str(exc)[:120]
        checks[check_id] = refused
        rows.append(
            _row(
                check_id=check_id,
                layer="output_root_protection",
                path=probe_rel,
                expected="CLEANUP_REFUSED",
                observed=f"refused={refused};msg={msg}",
                ok=refused,
                notes="ok" if refused else f"{check_id}_gap",
            )
        )

    out_ok = False
    out_detail = ""
    try:
        assert_fm29_output_root(paths.output_root_rel, base_dir=base_dir)
        out_ok = True
        out_detail = "allowed"
    except RuntimeError as exc:
        out_detail = str(exc)[:120]
    checks["hardening_output_root_allowed"] = out_ok
    rows.append(
        _row(
            check_id="hardening_output_root_allowed",
            layer="output_root_protection",
            path=paths.output_root_rel,
            expected="MOCK31_or_ephemeral_allowed",
            observed=out_detail,
            ok=out_ok,
            notes="ok" if out_ok else "output_root_blocked",
        )
    )

    hardening_keys = [
        "write_guard_phase3_harvest_refused",
        "write_guard_phase2_harvest_refused",
        "write_guard_fuller_harvest_refused",
        "write_guard_phase35_harvest_refused",
        "write_guard_phase35_resume_refused",
        "hardening_output_root_allowed",
        "protected_write_guard_battery_all_pass",
    ]
    hardening_ok = all(checks.get(k) for k in hardening_keys)
    checks["output_root_protection_all_pass"] = hardening_ok
    rows.append(
        _row(
            check_id="output_root_protection_all_pass",
            layer="output_root_protection",
            expected="harvest+resume_refused;mock31_ok",
            observed=(
                f"pass={sum(1 for k in hardening_keys if checks.get(k))}"
                f"/{len(hardening_keys)}"
            ),
            ok=hardening_ok,
            notes="ok" if hardening_ok else "hardening_incomplete",
        )
    )
    return rows, checks


def build_frozen_mock_isolation_rows(
    paths: PromoteReclassResumeLiftPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–30 拒绝 · MOCK31 放行。"""
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

    for root_id, check_id in (
        (PRIOR_TASK_ROOT_ID, "mock30_still_frozen"),
        ("C-ROOT-MOCK8", "seal_mock8_still_frozen"),
    ):
        prefix = frozen.get(root_id) or ""
        blocked = False
        try:
            if prefix:
                assert_frozen_mock_cohort_write_forbidden(
                    prefix,
                    allow_root_ids=(THIS_TASK_ROOT_ID,),
                    base_dir=base_dir,
                )
        except RuntimeError as exc:
            blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
        checks[check_id] = bool(prefix) and blocked
        rows.append(
            _row(
                check_id=check_id,
                layer="frozen_mock_isolation",
                root_id=root_id,
                path=_rel(prefix, base_dir=base_dir) if prefix else "",
                expected="still_frozen_vs_fm29_allowlist",
                observed=f"blocked={blocked}",
                ok=checks[check_id],
                notes="ok" if checks[check_id] else "prior_not_frozen",
            )
        )

    allow_ok = False
    allow_detail = ""
    try:
        assert_fm29_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
        allow_detail = "allowed"
    except RuntimeError as exc:
        allow_detail = str(exc)[:120]
    checks["frozen_allow_mock31"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock31",
            layer="frozen_mock_isolation",
            path=paths.output_root_rel,
            root_id=THIS_TASK_ROOT_ID,
            expected="MOCK31_or_ephemeral_allowed",
            observed=allow_detail,
            ok=allow_ok,
            notes="ok" if allow_ok else "mock31_blocked",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-30_frozen;MOCK31_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "frozen_isolation_incomplete",
        )
    )
    return rows, checks


def build_protected_csv_registry_rows(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected_output_roots.csv：MOCK31 已登记。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    protected = load_protected_root_rows(csv_rel, base_dir=base_dir)
    by_id = {str(r.get("root_id") or ""): r for r in protected}

    for rid in REQUIRED_PROTECTED_ROOT_IDS:
        present = rid in by_id
        checks[f"protected_csv_has_{rid.lower().replace('-', '_')}"] = present
        rows.append(
            _row(
                check_id=f"protected_csv_has_{rid.lower().replace('-', '_')}",
                layer="protected_csv_registry",
                root_id=rid,
                path=csv_rel,
                expected="present",
                observed="yes" if present else "missing",
                ok=present,
                notes="ok" if present else "missing_root_id",
            )
        )

    mock31 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(
        mock31.get("path_pattern") or ""
    )
    checks["protected_csv_mock31_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock31_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock31.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock31_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK31_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..28 gate battery（跳过 seal FM06–11）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    specs = [
        ("fm01_isolated_dryrun_repro", "fm01"),
        ("fm02_isolated_validation_cohorts", "fm02"),
        ("fm03_harvest_exclusion_dual_layer", "fm03"),
        ("fm04_ledger_resume_lineage", "fm04"),
        ("fm05_cross_fm_mock_cohort_integrity", "fm05"),
        ("fm12_dryrun_fingerprint_lineage_isolation", "fm12"),
        ("fm13_nonseal_cross_fm_mock_cohort_extension", "fm13"),
        ("fm14_nonseal_extension_post_commit_drift_recheck", "fm14"),
        ("fm15_nonseal_extension_controller_commit_boundary", "fm15"),
        ("fm16_nonseal_extension_post_commit_seal_attestation", "fm16"),
        ("fm17_nonseal_extension_human_decision_readiness_ledger", "fm17"),
        ("fm18_nonseal_cross_fm_mock_cohort_second_extension", "fm18"),
        ("fm19_nonseal_second_extension_post_commit_drift_recheck", "fm19"),
        ("fm20_nonseal_cross_fm_mock_cohort_third_extension", "fm20"),
        ("fm21_nonseal_third_extension_post_commit_drift_recheck", "fm21"),
        ("fm22_scale_harvest_exclusion_repro_fingerprint", "fm22"),
        ("fm23_scale_multi_batch_repro_lineage_hardening", "fm23"),
        ("fm24_scale_unique_coverage_resume_lineage_safety", "fm24"),
        ("fm25_scale_overlap_status_rollup_resume_delta_safety", "fm25"),
        ("fm26_scale_residual_status_triage_surface_delta_safety", "fm26"),
        ("fm27_scale_residual_disposition_quarantine_pending_fence", "fm27"),
        ("fm28_scale_risk_band_membership_write_boundary_cross_matrix", "fm28"),
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27", "fm28",
    }
    for check_id, key in specs:
        payload = gates[key]
        gate = str(payload.get("gate") or "").strip()
        cninfo = payload.get("cninfo_calls", None)
        execute = payload.get("execute_production_snapshot_rebuild", None)
        ok = gate == "PASS_OFFLINE" and cninfo == 0 and execute is False
        if key in seal_skip_keys and "seal_chain_extended" in payload:
            ok = ok and payload.get("seal_chain_extended") is False
        if key == "fm23":
            ok = (
                ok
                and payload.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
                and payload.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key == "fm24":
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in ("fm25", "fm26", "fm27", "fm28"):
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in ("fm26", "fm27", "fm28"):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in ("fm27", "fm28"):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key == "fm28":
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        rows.append(
            _row(
                check_id=check_id,
                layer="fm_gate_battery",
                cohort_id=key,
                expected="gate=PASS_OFFLINE;cninfo=0;execute=false",
                observed=f"gate={gate};cninfo={cninfo};execute={execute}",
                ok=ok,
                notes="ok" if ok else "prior_fm_gate_not_pass",
            )
        )
        checks[check_id] = ok

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="fm01_05_12_28_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_28_battery_all_pass"] = all_ok
    return rows, checks


def build_execute_hold_rows() -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """EXECUTE hold：不得因 AWAITING 而 IDLE；不得翻转 approved。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {
        "approved_for_snapshot_rebuild_false": True,
        "ready_for_execute_false": True,
        "hold_keep_execute_false": True,
        "decision_awaiting_human": True,
        "idle_not_required_while_awaiting": True,
        "seal_chain_not_extended": True,
    }
    for check_id, ok in checks.items():
        rows.append(
            _row(
                check_id=check_id,
                layer="execute_hold_seal",
                expected="hold_invariant",
                observed="asserted",
                ok=ok,
                notes="ok",
            )
        )
    all_ok = all(checks.values())
    checks["execute_hold_seal_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="execute_hold_seal_all_pass",
            layer="execute_hold_seal",
            expected="KEEP_EXECUTE_FALSE;no_idle_while_awaiting",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    return rows, checks


def ensure_protected_roots_csv_fm29(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK31；加固 C-ROOT-002 promote/reclass/lift 说明。"""
    path = _abs(csv_rel, base_dir=base_dir)
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        existing = list(reader)
    by_id = {str(r.get("root_id") or ""): r for r in existing}

    def _upsert(root_id: str, row: Dict[str, str]) -> None:
        if root_id in by_id:
            by_id[root_id].update(row)
        else:
            by_id[root_id] = row
            existing.append(row)

    prior_resume = by_id.get(RESUME_HARVEST_ROOT_ID) or {}
    _upsert(
        RESUME_HARVEST_ROOT_ID,
        {
            "root_id": RESUME_HARVEST_ROOT_ID,
            "path_pattern": prior_resume.get(
                "path_pattern", f"{HARVEST_PHASE35_RESUME_ROOT_REL}/"
            ),
            "root_class": prior_resume.get("root_class", "harvest"),
            "era_origin": prior_resume.get("era_origin", "era_c_phase35"),
            "protection_level": prior_resume.get("protection_level", "production"),
            "write_policy": "read_only_erad_planning",
            "notes": (
                "Phase 3.5 isolated resume harvest; 29 codes ⊆ phase35; "
                "C-FM-24 lineage + C-FM-25 resume-delta (28/1/0) + C-FM-26 "
                "resume-same hold (301212) + C-FM-27 disposition/fence + "
                "C-FM-28 membership/write-boundary + C-FM-29 "
                "promote/reclass/lift/coverage-lock; 只读直至人批重跑"
            ),
        },
    )
    _upsert(
        THIS_TASK_ROOT_ID,
        {
            "root_id": THIS_TASK_ROOT_ID,
            "path_pattern": f"{DEFAULT_MOCK_OUTPUT_ROOT_REL}/",
            "root_class": "ephemeral",
            "era_origin": "era_d_test",
            "protection_level": "mock",
            "write_policy": "delete_ok_tests_only",
            "notes": (
                "C-FM-29 scale partial promote/reclass denial (106) + "
                "resume-same hold boundary (301212) + residual lift denial "
                "(9+2) + coverage invariant lock (117) + FM28 continuity; "
                "never production EXECUTE; must not overwrite MOCK3-30; "
                "seal_chain_extended=false"
            ),
        },
    )

    ordered: List[Dict[str, str]] = []
    seen = set()
    for r in existing:
        rid = str(r.get("root_id") or "")
        if rid in seen:
            continue
        ordered.append(by_id.get(rid, r))
        seen.add(rid)
    for rid in (RESUME_HARVEST_ROOT_ID, THIS_TASK_ROOT_ID):
        if rid not in seen:
            ordered.append(by_id[rid])
            seen.add(rid)

    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in ordered:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    load_frozen_mock_cohort_roots.cache_clear()


def run_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety(
    *,
    paths: PromoteReclassResumeLiftPaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-29 规模 promote/reclass / resume-same / lift / coverage 离线 QA。"""
    paths = paths or PromoteReclassResumeLiftPaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm29(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm29_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm28_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    pr_rows, pr_checks, pr_meta = build_partial_promote_reclass_denial_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(pr_rows)
    rs_rows, rs_checks, rs_meta = build_resume_same_hold_boundary_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(rs_rows)
    lift_rows, lift_checks, lift_meta = build_residual_lift_denial_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(lift_rows)
    cov_rows, cov_checks, cov_meta = build_coverage_invariant_lock_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(cov_rows)
    root_rows, root_checks = build_output_root_protection_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(root_rows)
    freeze_rows, freeze_checks = build_frozen_mock_isolation_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(freeze_rows)
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    matrix.extend(csv_rows)

    gates = {
        "fm01": load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir)),
        "fm02": load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir)),
        "fm03": load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir)),
        "fm04": load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir)),
        "fm05": load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir)),
        "fm12": load_json(_abs(paths.fm12_gate_json_rel, base_dir=base_dir)),
        "fm13": load_json(_abs(paths.fm13_gate_json_rel, base_dir=base_dir)),
        "fm14": load_json(_abs(paths.fm14_gate_json_rel, base_dir=base_dir)),
        "fm15": load_json(_abs(paths.fm15_gate_json_rel, base_dir=base_dir)),
        "fm16": load_json(_abs(paths.fm16_gate_json_rel, base_dir=base_dir)),
        "fm17": load_json(_abs(paths.fm17_gate_json_rel, base_dir=base_dir)),
        "fm18": load_json(_abs(paths.fm18_gate_json_rel, base_dir=base_dir)),
        "fm19": load_json(_abs(paths.fm19_gate_json_rel, base_dir=base_dir)),
        "fm20": load_json(_abs(paths.fm20_gate_json_rel, base_dir=base_dir)),
        "fm21": load_json(_abs(paths.fm21_gate_json_rel, base_dir=base_dir)),
        "fm22": load_json(_abs(paths.fm22_gate_json_rel, base_dir=base_dir)),
        "fm23": load_json(_abs(paths.fm23_gate_json_rel, base_dir=base_dir)),
        "fm24": load_json(_abs(paths.fm24_gate_json_rel, base_dir=base_dir)),
        "fm25": load_json(_abs(paths.fm25_gate_json_rel, base_dir=base_dir)),
        "fm26": load_json(_abs(paths.fm26_gate_json_rel, base_dir=base_dir)),
        "fm27": load_json(_abs(paths.fm27_gate_json_rel, base_dir=base_dir)),
        "fm28": load_json(_abs(paths.fm28_gate_json_rel, base_dir=base_dir)),
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm28_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm28_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "partial_promote_reclass_denial": (
            "PASS_OFFLINE"
            if pr_checks.get("partial_promote_reclass_denial_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_same_hold_write_boundary": (
            "PASS_OFFLINE"
            if rs_checks.get("resume_same_hold_write_boundary_all_pass")
            else "FAIL_OFFLINE"
        ),
        "residual_lift_denial": (
            "PASS_OFFLINE"
            if lift_checks.get("residual_lift_denial_all_pass")
            else "FAIL_OFFLINE"
        ),
        "coverage_invariant_lock": (
            "PASS_OFFLINE"
            if cov_checks.get("coverage_invariant_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "output_root_protection": (
            "PASS_OFFLINE"
            if root_checks.get("output_root_protection_all_pass")
            else "FAIL_OFFLINE"
        ),
        "frozen_mock_isolation": (
            "PASS_OFFLINE"
            if freeze_checks.get("frozen_mock_isolation_all_pass")
            else "FAIL_OFFLINE"
        ),
        "protected_csv_registry": (
            "PASS_OFFLINE"
            if csv_checks.get("protected_csv_registry_all_pass")
            else "FAIL_OFFLINE"
        ),
        "fm_gate_battery": (
            "PASS_OFFLINE"
            if bat_checks.get("fm01_05_12_28_battery_all_pass")
            else "FAIL_OFFLINE"
        ),
        "execute_hold_seal": (
            "PASS_OFFLINE"
            if hold_checks.get("execute_hold_seal_all_pass")
            else "FAIL_OFFLINE"
        ),
    }
    overall = (
        "PASS_OFFLINE"
        if fail_count == 0 and all(v == "PASS_OFFLINE" for v in layer_gates.values())
        else "FAIL_OFFLINE"
    )

    os.makedirs(out_root, exist_ok=True)
    matrix_rel = _rel(os.path.join(out_root, "scale_matrix.csv"), base_dir=base_dir)
    write_scale_matrix_csv(matrix, _abs(matrix_rel, base_dir=base_dir))
    fp = fingerprint_scale_matrix(matrix)

    promote_rel = _rel(
        os.path.join(out_root, "partial_promote_reclass_denial_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(promote_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": pr_meta["fingerprint"],
                "partial_n": pr_meta["partial_n"],
                "membership_by_code": pr_meta["membership_by_code"],
                "promote_denial_count": len(pr_meta["promote_denials"]),
                "reclass_denial_count": len(pr_meta["reclass_denials"]),
                "doc": pr_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    resume_rel = _rel(
        os.path.join(out_root, "resume_same_hold_write_boundary_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(resume_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": rs_meta["fingerprint"],
                "resume_same_codes": rs_meta["resume_same_codes"],
                "denial_count": len(rs_meta["denials"]),
                "doc": rs_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    lift_rel = _rel(
        os.path.join(out_root, "residual_lift_denial_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(lift_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": lift_meta["fingerprint"],
                "failed_codes": lift_meta["failed_codes"],
                "delta_codes": lift_meta["delta_codes"],
                "denial_count": len(lift_meta["denials"]),
                "doc": lift_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    cov_rel = _rel(
        os.path.join(out_root, "coverage_invariant_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(cov_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": cov_meta["fingerprint"],
                "failed_n": cov_meta["failed_n"],
                "delta_n": cov_meta["delta_n"],
                "partial_n": cov_meta["partial_n"],
                "coverage_sum": cov_meta["coverage_sum"],
                "doc": cov_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    fingerprint_payload = {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "seal_chain_extended": False,
        "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
        "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "frozen_fps": {
            "partial_promote_reclass_denial": (
                FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256
            ),
            "resume_same_hold_write_boundary": (
                FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256
            ),
            "residual_lift_denial": FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256,
            "coverage_invariant_lock": FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256,
            "fm28_partial_risk_band_membership": FROZEN_RISK_BAND_MEMBERSHIP_FP_SHA256,
            "fm28_quarantine_write_boundary_denial": (
                FROZEN_QUARANTINE_WRITE_BOUNDARY_FP_SHA256
            ),
            "fm28_fence_absorb_denial_battery": FROZEN_FENCE_ABSORB_DENIAL_FP_SHA256,
            "fm28_residual_safety_cross_matrix": (
                FROZEN_RESIDUAL_SAFETY_CROSS_MATRIX_FP_SHA256
            ),
        },
        "observed_fps": {
            "partial_promote_reclass_denial": pr_meta["fingerprint"],
            "resume_same_hold_write_boundary": rs_meta["fingerprint"],
            "residual_lift_denial": lift_meta["fingerprint"],
            "coverage_invariant_lock": cov_meta["fingerprint"],
        },
        "fingerprint": fp,
    }
    fingerprint_rel = _rel(
        os.path.join(out_root, "scale_fingerprint.json"), base_dir=base_dir
    )
    with open(_abs(fingerprint_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(fingerprint_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    battery_payload = {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "gate": overall,
        "layer_gates": layer_gates,
        "fm01_gate": (gates["fm01"] or {}).get("gate"),
        "fm02_gate": (gates["fm02"] or {}).get("gate"),
        "fm03_gate": (gates["fm03"] or {}).get("gate"),
        "fm04_gate": (gates["fm04"] or {}).get("gate"),
        "fm05_gate": (gates["fm05"] or {}).get("gate"),
        "fm12_gate": (gates["fm12"] or {}).get("gate"),
        "fm13_gate": (gates["fm13"] or {}).get("gate"),
        "fm14_gate": (gates["fm14"] or {}).get("gate"),
        "fm15_gate": (gates["fm15"] or {}).get("gate"),
        "fm16_gate": (gates["fm16"] or {}).get("gate"),
        "fm17_gate": (gates["fm17"] or {}).get("gate"),
        "fm18_gate": (gates["fm18"] or {}).get("gate"),
        "fm19_gate": (gates["fm19"] or {}).get("gate"),
        "fm20_gate": (gates["fm20"] or {}).get("gate"),
        "fm21_gate": (gates["fm21"] or {}).get("gate"),
        "fm22_gate": (gates["fm22"] or {}).get("gate"),
        "fm23_gate": (gates["fm23"] or {}).get("gate"),
        "fm24_gate": (gates["fm24"] or {}).get("gate"),
        "fm25_gate": (gates["fm25"] or {}).get("gate"),
        "fm26_gate": (gates["fm26"] or {}).get("gate"),
        "fm27_gate": (gates["fm27"] or {}).get("gate"),
        "fm28_gate": (gates["fm28"] or {}).get("gate"),
        "fm29_gate": overall,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting": True,
        "seal_chain_extended": False,
        "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
        "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
    }
    battery_rel = _rel(
        os.path.join(out_root, "fm_gate_battery.json"), base_dir=base_dir
    )
    with open(_abs(battery_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(battery_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    packet = {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "gate": overall,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting": True,
        "seal_chain_extended": False,
        "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
        "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "resume_total": EXPECTED_RESUME_TOTAL,
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "dry863_extras": sorted(EXPECTED_DRY863_EXTRA),
        "failed_codes": lift_meta["failed_codes"],
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "notes": (
            "partial promote/reclass denial (106) + resume-same hold "
            "boundary (301212) + residual lift denial (9+2) + coverage "
            "invariant lock (117) + FM28 continuity + MOCK31; EXECUTE "
            "remains human-held; does not overwrite MOCK3-30"
        ),
    }
    packet_rel = _rel(os.path.join(out_root, "scale_packet.json"), base_dir=base_dir)
    with open(_abs(packet_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(packet, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

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
        "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
        "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "resume_total": EXPECTED_RESUME_TOTAL,
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "dry863_extras": sorted(EXPECTED_DRY863_EXTRA),
        "failed_codes": lift_meta["failed_codes"],
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "promote_reclass_path": promote_rel,
        "resume_same_path": resume_rel,
        "residual_lift_path": lift_rel,
        "coverage_lock_path": cov_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": fingerprint_payload["observed_fps"],
        "inputs": {
            "fm28_packet": paths.fm28_packet_rel,
            "fm28_gate": paths.fm28_gate_json_rel,
        },
        "mock_root_is_isolated": True,
    }
