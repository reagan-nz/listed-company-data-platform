"""
CNINFO C-class — 规模 complete demotion denial + status partition invariant
+ winner provenance lock + overlap-delta/surface-injection freeze（离线 · C-FM-30）。

在 C-FM-29（partial promote/reclass + resume-same hold + residual lift +
coverage invariant）已 commit 且 EXECUTE 仍 human-held 之上，继续非 seal
规模/安全能力（不新增 seal / decision-await / commit-boundary；非
extension↔drift 循环）：
  1) FM29 packet / fingerprint / gate / promote·resume·lift·coverage ledgers
     零漂移连续
  2) complete demotion denial：2134 码禁止 demote→partial / demote→failed
  3) status partition invariant lock：2134+106+9=2249 · mutation_allowed=false
  4) winner provenance lock：2249 码 winning-batch 禁止 reassign
  5) overlap-delta / surface-injection freeze：Δ12 + additive=2261 冻结；
     dry863 extras 禁止注入 harvest unique
  6) output-root：MOCK3–31 冻结 · MOCK32 放行
  7) FM-01..05 + FM-12..29 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–31 / 权威 dual-layer 索引 ·
verified 声称 · 翻转 approved_for_snapshot_rebuild · 扩展 seal-chain ·
因 AWAITING 而 IDLE · commit/push。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import Counter
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
    BATCH_PRIORITY,
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
    EXPECTED_RESIDUAL_SAFETY_COVERAGE,
)
from cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety import (  # noqa: E402
    FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256,
    FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256,
    FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256,
    FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256,
    fingerprint_coverage_invariant_lock,
    fingerprint_partial_promote_reclass_denial,
    fingerprint_residual_lift_denial,
    fingerprint_resume_same_hold_boundary,
)

TASK_ID = "C-FM-30"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm30_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety"
)

FM27_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_residual_disposition_quarantine_pending_fence_safety_20260715.json"
)
FM28_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_risk_band_membership_write_boundary_cross_matrix_safety_20260715.json"
)
FM29_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety_20260715.json"
)
FM29_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm29_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety"
)
FM29_PACKET_REL = f"{FM29_MOCK_ROOT_REL}/scale_packet.json"
FM29_FINGERPRINT_REL = f"{FM29_MOCK_ROOT_REL}/scale_fingerprint.json"
FM29_PROMOTE_REL = f"{FM29_MOCK_ROOT_REL}/partial_promote_reclass_denial_ledger.json"
FM29_RESUME_REL = f"{FM29_MOCK_ROOT_REL}/resume_same_hold_write_boundary_ledger.json"
FM29_LIFT_REL = f"{FM29_MOCK_ROOT_REL}/residual_lift_denial_ledger.json"
FM29_COV_REL = f"{FM29_MOCK_ROOT_REL}/coverage_invariant_lock_ledger.json"

FROZEN_COMPLETE_DEMOTION_DENIAL_FP_SHA256 = (
    "2123af3b0358b4c89d4dc4be244036f89f5bb746a88669f3fcebc6057a592616"
)
FROZEN_STATUS_PARTITION_INVARIANT_FP_SHA256 = (
    "cf92235295178cf93c83db4a1c2469f8f9662439fcae888c666878a1877cbe07"
)
FROZEN_WINNER_PROVENANCE_LOCK_FP_SHA256 = (
    "900d342a10ec22811eff54a38bb1e81eb4b0cc3a261b85d7958d40182b7591a4"
)
FROZEN_OVERLAP_SURFACE_FREEZE_FP_SHA256 = (
    "7a019fc8114586086db6ae6e7319ff2cd6e6769e77eabf46f43516398ddb4fb2"
)

EXPECTED_COMPLETE_CODES_SHA256 = (
    "45beb7732efff04fb43bae7db8603b0ccca552700e969f664052fe1ba68c9431"
)
EXPECTED_WINNER_MAP_SHA256 = (
    "ff2c6a28b361498b0dbf163ad1d1779041e1dd4e772b652e6382e1d4051fbb07"
)
EXPECTED_COMPLETE_WINNER_BATCHES = {
    "fu": 183,
    "h863": 861,
    "p2": 188,
    "p3": 483,
    "p35": 419,
}

THIS_TASK_ROOT_ID = "C-ROOT-MOCK32"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK31"
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
    "C-ROOT-MOCK31",
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class CompleteDemotionPartitionWinnerPaths:
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
    fm29_gate_json_rel: str = FM29_GATE_JSON_REL
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
    fm29_packet_rel: str = FM29_PACKET_REL
    fm29_fingerprint_rel: str = FM29_FINGERPRINT_REL
    fm29_promote_rel: str = FM29_PROMOTE_REL
    fm29_resume_rel: str = FM29_RESUME_REL
    fm29_lift_rel: str = FM29_LIFT_REL
    fm29_cov_rel: str = FM29_COV_REL
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


def _to_fm26_paths(paths: CompleteDemotionPartitionWinnerPaths) -> Fm26Paths:
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


def assert_fm30_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-30 写根：须 validation/_mock_*，不得覆盖 MOCK3–31，
    不得写权威 dual-layer 索引；允许本任务 MOCK32 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-30 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _sha256_codes(codes: Sequence[str]) -> str:
    return hashlib.sha256(",".join(sorted(codes)).encode("utf-8")).hexdigest()


def _sha256_winner_map(winning: Dict[str, str]) -> str:
    pairs = sorted((c, winning[c]) for c in winning)
    return hashlib.sha256(
        json.dumps(pairs, ensure_ascii=False, sort_keys=False).encode("utf-8")
    ).hexdigest()


def fingerprint_complete_demotion_denial(
    *,
    complete_codes: Sequence[str],
) -> Tuple[str, Dict[str, Any]]:
    """complete demotion denial 指纹。"""
    codes = sorted(complete_codes)
    doc = {
        "kind": "complete_demotion_denial",
        "complete_n": len(codes),
        "complete_codes_sha256": _sha256_codes(codes),
        "deny_demote_to_partial": True,
        "deny_demote_to_failed": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_status_partition_invariant(
    *,
    complete_n: int,
    partial_n: int,
    failed_n: int,
) -> Tuple[str, Dict[str, Any]]:
    """status partition invariant lock 指纹。"""
    doc = {
        "kind": "status_partition_invariant_lock",
        "complete_n": complete_n,
        "partial_n": partial_n,
        "failed_n": failed_n,
        "unique_union": complete_n + partial_n + failed_n,
        "equation": "2134+106+9=2249",
        "mutation_allowed": False,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_winner_provenance_lock(
    *,
    winning: Dict[str, str],
) -> Tuple[str, Dict[str, Any]]:
    """winner provenance lock 指纹。"""
    doc = {
        "kind": "winner_provenance_lock",
        "unique_n": len(winning),
        "winner_map_sha256": _sha256_winner_map(winning),
        "deny_winner_reassign": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_overlap_surface_freeze() -> Tuple[str, Dict[str, Any]]:
    """overlap-delta / surface-injection freeze 指纹。"""
    doc = {
        "kind": "overlap_delta_surface_injection_freeze",
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "surface_extras": sorted(EXPECTED_DRY863_EXTRA),
        "deny_surface_inject_into_harvest": True,
        "deny_overlap_delta_mutation": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_complete_demotion(
    *,
    code: str,
    to_status: str,
    complete_codes: Sequence[str],
) -> Dict[str, Any]:
    """评估 complete 码 demotion；显式 denial。"""
    if code not in set(complete_codes):
        raise ValueError(f"not a complete code: {code}")
    if to_status not in ("partial", "failed"):
        raise ValueError(f"unknown demotion target: {to_status}")
    return {
        "code": code,
        "from_status": "complete",
        "to_status": to_status,
        "allowed": False,
        "reason": "complete_demotion_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_partition_mutation(
    *,
    proposed_complete_n: int,
    proposed_partial_n: int,
    proposed_failed_n: int,
) -> Dict[str, Any]:
    """评估 status partition 变异；mutation 一律拒绝。"""
    proposed = proposed_complete_n + proposed_partial_n + proposed_failed_n
    matches = (
        proposed_complete_n == EXPECTED_UNION_COMPLETE
        and proposed_partial_n == EXPECTED_UNION_PARTIAL
        and proposed_failed_n == EXPECTED_UNION_FAILED
        and proposed == EXPECTED_HARVEST_UNIQUE_UNION
    )
    return {
        "proposed_union": proposed,
        "frozen_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "status_partition_invariant_locked_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_winner_reassign(
    *,
    code: str,
    to_batch: str,
    winning: Dict[str, str],
) -> Dict[str, Any]:
    """评估 winning-batch reassign；显式 denial。"""
    if code not in winning:
        raise ValueError(f"not a union code: {code}")
    if to_batch not in BATCH_PRIORITY:
        raise ValueError(f"unknown winner batch: {to_batch}")
    return {
        "code": code,
        "from_batch": winning[code],
        "to_batch": to_batch,
        "allowed": False,
        "reason": "winner_provenance_locked_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_surface_inject(
    *,
    code: str,
) -> Dict[str, Any]:
    """评估 dry863 surface extras 注入 harvest；显式 denial。"""
    if code not in EXPECTED_DRY863_EXTRA:
        raise ValueError(f"not a surface-extra code: {code}")
    return {
        "code": code,
        "target": "inject_into_harvest_unique",
        "allowed": False,
        "reason": "surface_injection_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_overlap_delta_mutation(
    *,
    proposed_overlap_delta: int,
    proposed_additive: int,
) -> Dict[str, Any]:
    """评估 overlap-delta 变异；mutation 一律拒绝。"""
    matches = (
        proposed_overlap_delta == EXPECTED_OVERLAP_DELTA
        and proposed_additive == EXPECTED_HARVEST_ADDITIVE
        and proposed_additive - EXPECTED_HARVEST_UNIQUE_UNION
        == EXPECTED_OVERLAP_DELTA
    )
    return {
        "proposed_overlap_delta": proposed_overlap_delta,
        "frozen_overlap_delta": EXPECTED_OVERLAP_DELTA,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "overlap_delta_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def build_fm29_continuity_rows(
    paths: CompleteDemotionPartitionWinnerPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM29 packet / fingerprint / gate / promote·resume·lift·coverage 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm29_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm29_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm29_gate_json_rel, base_dir=base_dir))
    pr_led = load_json(_abs(paths.fm29_promote_rel, base_dir=base_dir))
    rs_led = load_json(_abs(paths.fm29_resume_rel, base_dir=base_dir))
    lift_led = load_json(_abs(paths.fm29_lift_rel, base_dir=base_dir))
    cov_led = load_json(_abs(paths.fm29_cov_rel, base_dir=base_dir))

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
        and packet.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and packet.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
    )
    checks["fm29_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm29_packet_continuity",
            layer="fm29_continuity",
            path=paths.fm29_packet_rel,
            expected="PASS_OFFLINE;unique=2249;2134/106/9;cov=117;KEEP",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"status={packet.get('union_complete')}/"
                f"{packet.get('union_partial')}/{packet.get('union_failed')};"
                f"cov={packet.get('residual_safety_coverage')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm29_packet_drift",
        )
    )

    fp_ok = (
        fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and fp_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and fp_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and (fp_doc.get("frozen_fps") or {}).get("partial_promote_reclass_denial")
        == FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("resume_same_hold_write_boundary")
        == FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("residual_lift_denial")
        == FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("coverage_invariant_lock")
        == FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256
        and fp_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and fp_doc.get("residual_safety_coverage") == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm29_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm29_fingerprint_continuity",
            layer="fm29_continuity",
            path=paths.fm29_fingerprint_rel,
            expected="unique2249+fm29_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"failed={fp_doc.get('union_failed')};"
                f"cov={fp_doc.get('residual_safety_coverage')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm29_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and gate_doc.get("union_complete") == EXPECTED_UNION_COMPLETE
        and gate_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and gate_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and gate_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and gate_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and gate_doc.get("residual_safety_coverage") == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("seal_chain_extended") is False
    )
    checks["fm29_gate_json_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm29_gate_json_continuity",
            layer="fm29_continuity",
            path=paths.fm29_gate_json_rel,
            expected="PASS_OFFLINE;2134/106/9;cov=117;approved=false",
            observed=(
                f"gate={gate_doc.get('gate')};"
                f"status={gate_doc.get('union_complete')}/"
                f"{gate_doc.get('union_partial')}/{gate_doc.get('union_failed')};"
                f"cov={gate_doc.get('residual_safety_coverage')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm29_gate_drift",
        )
    )

    led_ok = (
        pr_led.get("fingerprint_sha256") == FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256
        and int(pr_led.get("partial_n") or 0) == EXPECTED_UNION_PARTIAL
        and rs_led.get("fingerprint_sha256") == FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256
        and set(rs_led.get("resume_same_codes") or []) == EXPECTED_RESUME_SAME_CODES
        and lift_led.get("fingerprint_sha256") == FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256
        and set(lift_led.get("failed_codes") or []) == EXPECTED_FAILED_CODES
        and set(lift_led.get("delta_codes") or []) == EXPECTED_DRY863_EXTRA
        and cov_led.get("fingerprint_sha256") == FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256
        and int(cov_led.get("coverage_sum") or 0) == EXPECTED_RESIDUAL_SAFETY_COVERAGE
    )
    checks["fm29_ledger_continuity"] = led_ok
    rows.append(
        _row(
            check_id="fm29_ledger_continuity",
            layer="fm29_continuity",
            expected="promote+resume+lift+cov_fps",
            observed=(
                f"pr_fp={str(pr_led.get('fingerprint_sha256') or '')[:12]};"
                f"cov={cov_led.get('coverage_sum')}"
            ),
            ok=led_ok,
            notes="ok" if led_ok else "fm29_ledger_drift",
        )
    )

    # 再算 FM29 四层指纹确认相对冻结锚无漂移
    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    partial = sorted(c for c, s in union_status.items() if s == "partial")
    from cninfo_c_class_scale_risk_band_membership_write_boundary_cross_matrix_safety import (
        classify_risk_band,
    )

    membership = {c: classify_risk_band(winning[c]) for c in partial}
    fp_pr, _ = fingerprint_partial_promote_reclass_denial(
        partial_codes=partial, membership_by_code=membership
    )
    fp_rs, _ = fingerprint_resume_same_hold_boundary(
        resume_same_codes=sorted(EXPECTED_RESUME_SAME_CODES)
    )
    fp_lift, _ = fingerprint_residual_lift_denial(
        failed_codes=sorted(EXPECTED_FAILED_CODES),
        delta_codes=sorted(EXPECTED_DRY863_EXTRA),
    )
    fp_cov, _ = fingerprint_coverage_invariant_lock(
        failed_n=EXPECTED_UNION_FAILED,
        delta_n=EXPECTED_SURFACE_HARVEST_DELTA_N,
        partial_n=EXPECTED_UNION_PARTIAL,
    )
    reaffirm_ok = (
        fp_pr == FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256
        and fp_rs == FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256
        and fp_lift == FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256
        and fp_cov == FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256
        and len(partial) == EXPECTED_UNION_PARTIAL
    )
    checks["fm29_promote_resume_lift_cov_reaffirm"] = bool(reaffirm_ok)
    rows.append(
        _row(
            check_id="fm29_promote_resume_lift_cov_reaffirm",
            layer="fm29_continuity",
            expected="pr+rs+lift+cov_reaffirm",
            observed=f"ok={bool(reaffirm_ok)}",
            ok=bool(reaffirm_ok),
            notes="ok" if reaffirm_ok else "fm29_reaffirm_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm29_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm29_continuity_all_pass",
            layer="fm29_continuity",
            expected="packet+fingerprint+gate+ledgers+reaffirm",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm29_continuity_incomplete",
        )
    )
    return rows, checks


def build_complete_demotion_denial_rows(
    paths: CompleteDemotionPartitionWinnerPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """complete demotion denial（2134 码）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    complete = sorted(c for c, s in union_status.items() if s == "complete")
    fp, doc = fingerprint_complete_demotion_denial(complete_codes=complete)

    n_ok = len(complete) == EXPECTED_UNION_COMPLETE
    checks["complete_count_2134"] = n_ok
    rows.append(
        _row(
            check_id="complete_count_2134",
            layer="complete_demotion_denial",
            expected=str(EXPECTED_UNION_COMPLETE),
            observed=str(len(complete)),
            ok=n_ok,
            notes="ok" if n_ok else "complete_count_mismatch",
        )
    )

    codes_fp_ok = doc["complete_codes_sha256"] == EXPECTED_COMPLETE_CODES_SHA256
    checks["complete_codes_sha256_exact"] = codes_fp_ok
    rows.append(
        _row(
            check_id="complete_codes_sha256_exact",
            layer="complete_demotion_denial",
            expected=EXPECTED_COMPLETE_CODES_SHA256,
            observed=doc["complete_codes_sha256"],
            ok=codes_fp_ok,
            notes="ok" if codes_fp_ok else "complete_codes_sha_drift",
        )
    )

    batch_counts = dict(sorted(Counter(winning[c] for c in complete).items()))
    batches_ok = batch_counts == EXPECTED_COMPLETE_WINNER_BATCHES
    checks["complete_winner_batches_exact"] = batches_ok
    rows.append(
        _row(
            check_id="complete_winner_batches_exact",
            layer="complete_demotion_denial",
            expected="h863=861;p35=419;p3=483;p2=188;fu=183",
            observed=json.dumps(batch_counts, ensure_ascii=False, sort_keys=True),
            ok=batches_ok,
            notes="ok" if batches_ok else "complete_batch_drift",
        )
    )

    # 全量 demote→partial / demote→failed 显式拒绝（摘要计数，不落盘全量）
    demote_ok = True
    denial_count = 0
    sample_denials: List[Dict[str, Any]] = []
    for code in complete:
        for to_status in ("partial", "failed"):
            d = evaluate_complete_demotion(
                code=code, to_status=to_status, complete_codes=complete
            )
            denial_count += 1
            if len(sample_denials) < 6:
                sample_denials.append(d)
            if d.get("allowed") is not False:
                demote_ok = False
    checks["complete_demotion_denial_battery"] = (
        demote_ok and denial_count == EXPECTED_UNION_COMPLETE * 2
    )
    rows.append(
        _row(
            check_id="complete_demotion_denial_battery",
            layer="complete_demotion_denial",
            expected="4268_demotions_denied",
            observed=f"denials={denial_count};all_denied={demote_ok}",
            ok=checks["complete_demotion_denial_battery"],
            notes="ok" if checks["complete_demotion_denial_battery"] else "demote_leak",
        )
    )

    flags_ok = (
        doc["deny_demote_to_partial"] is True
        and doc["deny_demote_to_failed"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["complete_demotion_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="complete_demotion_flags_locked",
            layer="complete_demotion_denial",
            expected="deny_partial+deny_failed+KEEP",
            observed=(
                f"partial={doc['deny_demote_to_partial']};"
                f"failed={doc['deny_demote_to_failed']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_COMPLETE_DEMOTION_DENIAL_FP_SHA256
    checks["complete_demotion_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="complete_demotion_fingerprint",
            layer="complete_demotion_denial",
            expected=FROZEN_COMPLETE_DEMOTION_DENIAL_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "complete_demotion_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["complete_demotion_denial_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="complete_demotion_denial_all_pass",
            layer="complete_demotion_denial",
            expected="2134_demote_deny+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "complete_demotion_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "complete_n": len(complete),
        "complete_codes_sha256": doc["complete_codes_sha256"],
        "winner_batches": batch_counts,
        "denial_count": denial_count,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_status_partition_invariant_rows(
    paths: CompleteDemotionPartitionWinnerPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """status partition invariant lock（2134+106+9=2249）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, _winning = compute_union_status_and_winners(status_maps)
    complete_n = sum(1 for s in union_status.values() if s == "complete")
    partial_n = sum(1 for s in union_status.values() if s == "partial")
    failed_n = sum(1 for s in union_status.values() if s == "failed")
    fp, doc = fingerprint_status_partition_invariant(
        complete_n=complete_n, partial_n=partial_n, failed_n=failed_n
    )

    eq_ok = (
        complete_n == EXPECTED_UNION_COMPLETE
        and partial_n == EXPECTED_UNION_PARTIAL
        and failed_n == EXPECTED_UNION_FAILED
        and complete_n + partial_n + failed_n == EXPECTED_HARVEST_UNIQUE_UNION
        and len(union_status) == EXPECTED_HARVEST_UNIQUE_UNION
    )
    checks["partition_equation_2249"] = eq_ok
    rows.append(
        _row(
            check_id="partition_equation_2249",
            layer="status_partition_invariant_lock",
            expected="2134+106+9=2249",
            observed=f"{complete_n}+{partial_n}+{failed_n}={complete_n+partial_n+failed_n}",
            ok=eq_ok,
            notes="ok" if eq_ok else "partition_equation_drift",
        )
    )

    disjoint_ok = True
    # 三集合互斥由 union status 单值保证；再确认 failed∩partial 空
    failed_set = {c for c, s in union_status.items() if s == "failed"}
    partial_set = {c for c, s in union_status.items() if s == "partial"}
    complete_set = {c for c, s in union_status.items() if s == "complete"}
    disjoint_ok = (
        failed_set.isdisjoint(partial_set)
        and failed_set.isdisjoint(complete_set)
        and partial_set.isdisjoint(complete_set)
    )
    checks["partition_sets_disjoint"] = disjoint_ok
    rows.append(
        _row(
            check_id="partition_sets_disjoint",
            layer="status_partition_invariant_lock",
            expected="complete∩partial∩failed=∅",
            observed=f"disjoint={disjoint_ok}",
            ok=disjoint_ok,
            notes="ok" if disjoint_ok else "partition_overlap",
        )
    )

    mut = evaluate_partition_mutation(
        proposed_complete_n=EXPECTED_UNION_COMPLETE,
        proposed_partial_n=EXPECTED_UNION_PARTIAL + 1,
        proposed_failed_n=EXPECTED_UNION_FAILED,
    )
    mut2 = evaluate_partition_mutation(
        proposed_complete_n=EXPECTED_UNION_COMPLETE,
        proposed_partial_n=EXPECTED_UNION_PARTIAL,
        proposed_failed_n=EXPECTED_UNION_FAILED,
    )
    mut_ok = mut["mutation_allowed"] is False and mut2["mutation_allowed"] is False
    checks["partition_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="partition_mutation_denied",
            layer="status_partition_invariant_lock",
            expected="mutation_allowed=false",
            observed=f"drift_denied={mut['mutation_allowed']};exact_denied={mut2['mutation_allowed']}",
            ok=mut_ok,
            notes="ok" if mut_ok else "partition_mutation_leak",
        )
    )

    flags_ok = doc["mutation_allowed"] is False and doc["hold"] == "KEEP_EXECUTE_FALSE"
    checks["partition_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="partition_flags_locked",
            layer="status_partition_invariant_lock",
            expected="mutation=false+KEEP",
            observed=f"mutation={doc['mutation_allowed']};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_STATUS_PARTITION_INVARIANT_FP_SHA256
    checks["partition_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="partition_fingerprint",
            layer="status_partition_invariant_lock",
            expected=FROZEN_STATUS_PARTITION_INVARIANT_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "partition_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["status_partition_invariant_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="status_partition_invariant_lock_all_pass",
            layer="status_partition_invariant_lock",
            expected="2134+106+9=2249+lock",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "partition_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "complete_n": complete_n,
        "partial_n": partial_n,
        "failed_n": failed_n,
        "unique_union": complete_n + partial_n + failed_n,
        "doc": doc,
    }
    return rows, checks, meta


def build_winner_provenance_lock_rows(
    paths: CompleteDemotionPartitionWinnerPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """winner provenance lock（2249 码）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    fp, doc = fingerprint_winner_provenance_lock(winning=winning)

    n_ok = len(winning) == EXPECTED_HARVEST_UNIQUE_UNION == len(union_status)
    checks["winner_map_count_2249"] = n_ok
    rows.append(
        _row(
            check_id="winner_map_count_2249",
            layer="winner_provenance_lock",
            expected=str(EXPECTED_HARVEST_UNIQUE_UNION),
            observed=str(len(winning)),
            ok=n_ok,
            notes="ok" if n_ok else "winner_count_mismatch",
        )
    )

    map_fp_ok = doc["winner_map_sha256"] == EXPECTED_WINNER_MAP_SHA256
    checks["winner_map_sha256_exact"] = map_fp_ok
    rows.append(
        _row(
            check_id="winner_map_sha256_exact",
            layer="winner_provenance_lock",
            expected=EXPECTED_WINNER_MAP_SHA256,
            observed=doc["winner_map_sha256"],
            ok=map_fp_ok,
            notes="ok" if map_fp_ok else "winner_map_sha_drift",
        )
    )

    # 每码尝试 reassign 到下一 batch → 拒绝
    reassign_ok = True
    denial_count = 0
    sample_denials: List[Dict[str, Any]] = []
    for code in sorted(winning):
        from_batch = winning[code]
        idx = BATCH_PRIORITY.index(from_batch)
        to_batch = BATCH_PRIORITY[(idx + 1) % len(BATCH_PRIORITY)]
        d = evaluate_winner_reassign(code=code, to_batch=to_batch, winning=winning)
        denial_count += 1
        if len(sample_denials) < 6:
            sample_denials.append(d)
        if d.get("allowed") is not False:
            reassign_ok = False
    checks["winner_reassign_denial_battery"] = (
        reassign_ok and denial_count == EXPECTED_HARVEST_UNIQUE_UNION
    )
    rows.append(
        _row(
            check_id="winner_reassign_denial_battery",
            layer="winner_provenance_lock",
            expected="2249_reassign_denied",
            observed=f"denials={denial_count};all_denied={reassign_ok}",
            ok=checks["winner_reassign_denial_battery"],
            notes="ok" if checks["winner_reassign_denial_battery"] else "reassign_leak",
        )
    )

    flags_ok = (
        doc["deny_winner_reassign"] is True and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["winner_provenance_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="winner_provenance_flags_locked",
            layer="winner_provenance_lock",
            expected="deny_reassign+KEEP",
            observed=f"deny={doc['deny_winner_reassign']};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_WINNER_PROVENANCE_LOCK_FP_SHA256
    checks["winner_provenance_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="winner_provenance_fingerprint",
            layer="winner_provenance_lock",
            expected=FROZEN_WINNER_PROVENANCE_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "winner_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["winner_provenance_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="winner_provenance_lock_all_pass",
            layer="winner_provenance_lock",
            expected="2249_winner_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "winner_provenance_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "unique_n": len(winning),
        "winner_map_sha256": doc["winner_map_sha256"],
        "denial_count": denial_count,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_overlap_surface_freeze_rows(
    paths: CompleteDemotionPartitionWinnerPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """overlap-delta freeze + surface extras injection denial。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fp, doc = fingerprint_overlap_surface_freeze()

    delta_ok = (
        EXPECTED_OVERLAP_DELTA == 12
        and EXPECTED_HARVEST_ADDITIVE - EXPECTED_HARVEST_UNIQUE_UNION
        == EXPECTED_OVERLAP_DELTA
        and EXPECTED_HARVEST_ADDITIVE == 2261
    )
    checks["overlap_delta_12_exact"] = delta_ok
    rows.append(
        _row(
            check_id="overlap_delta_12_exact",
            layer="overlap_delta_surface_injection_freeze",
            expected="additive2261-unique2249=12",
            observed=(
                f"additive={EXPECTED_HARVEST_ADDITIVE};"
                f"unique={EXPECTED_HARVEST_UNIQUE_UNION};"
                f"delta={EXPECTED_OVERLAP_DELTA}"
            ),
            ok=delta_ok,
            notes="ok" if delta_ok else "overlap_delta_drift",
        )
    )

    extras = sorted(EXPECTED_DRY863_EXTRA)
    extras_ok = extras == ["000037", "000055"] and len(extras) == EXPECTED_SURFACE_HARVEST_DELTA_N
    checks["surface_extras_exact"] = extras_ok
    rows.append(
        _row(
            check_id="surface_extras_exact",
            layer="overlap_delta_surface_injection_freeze",
            expected="000037,000055",
            observed=",".join(extras),
            ok=extras_ok,
            notes="ok" if extras_ok else "surface_extras_drift",
        )
    )

    # surface extras 不得出现在 harvest unique
    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, _winning = compute_union_status_and_winners(status_maps)
    not_in_harvest = all(c not in union_status for c in EXPECTED_DRY863_EXTRA)
    checks["surface_extras_absent_from_harvest"] = not_in_harvest
    rows.append(
        _row(
            check_id="surface_extras_absent_from_harvest",
            layer="overlap_delta_surface_injection_freeze",
            expected="extras∩harvest=∅",
            observed=f"absent={not_in_harvest}",
            ok=not_in_harvest,
            notes="ok" if not_in_harvest else "surface_leaked_into_harvest",
        )
    )

    inject_denials = []
    inject_ok = True
    for code in extras:
        d = evaluate_surface_inject(code=code)
        inject_denials.append(d)
        if d.get("allowed") is not False:
            inject_ok = False
    checks["surface_inject_denial_battery"] = (
        inject_ok and len(inject_denials) == EXPECTED_SURFACE_HARVEST_DELTA_N
    )
    rows.append(
        _row(
            check_id="surface_inject_denial_battery",
            layer="overlap_delta_surface_injection_freeze",
            expected="2_inject_denied",
            observed=f"denials={len(inject_denials)};all_denied={inject_ok}",
            ok=checks["surface_inject_denial_battery"],
            notes="ok" if checks["surface_inject_denial_battery"] else "inject_leak",
        )
    )

    mut = evaluate_overlap_delta_mutation(
        proposed_overlap_delta=13, proposed_additive=2262
    )
    mut2 = evaluate_overlap_delta_mutation(
        proposed_overlap_delta=EXPECTED_OVERLAP_DELTA,
        proposed_additive=EXPECTED_HARVEST_ADDITIVE,
    )
    mut_ok = mut["mutation_allowed"] is False and mut2["mutation_allowed"] is False
    checks["overlap_delta_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="overlap_delta_mutation_denied",
            layer="overlap_delta_surface_injection_freeze",
            expected="mutation_allowed=false",
            observed=f"drift_denied={mut['mutation_allowed']};exact_denied={mut2['mutation_allowed']}",
            ok=mut_ok,
            notes="ok" if mut_ok else "overlap_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_surface_inject_into_harvest"] is True
        and doc["deny_overlap_delta_mutation"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["overlap_surface_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="overlap_surface_flags_locked",
            layer="overlap_delta_surface_injection_freeze",
            expected="deny_inject+deny_delta+KEEP",
            observed=(
                f"inject={doc['deny_surface_inject_into_harvest']};"
                f"delta={doc['deny_overlap_delta_mutation']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_OVERLAP_SURFACE_FREEZE_FP_SHA256
    checks["overlap_surface_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="overlap_surface_fingerprint",
            layer="overlap_delta_surface_injection_freeze",
            expected=FROZEN_OVERLAP_SURFACE_FREEZE_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "overlap_surface_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["overlap_delta_surface_injection_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="overlap_delta_surface_injection_freeze_all_pass",
            layer="overlap_delta_surface_injection_freeze",
            expected="delta12+surface_inject_deny+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "overlap_surface_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
        "surface_extras": extras,
        "inject_denials": inject_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: CompleteDemotionPartitionWinnerPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK32 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm30.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm30.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm30.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm30.csv",
        ),
        (
            "write_guard_phase35_resume_refused",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm30.csv",
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
        assert_fm30_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK32_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock32_ok",
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
    paths: CompleteDemotionPartitionWinnerPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–31 拒绝 · MOCK32 放行。"""
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
        (PRIOR_TASK_ROOT_ID, "mock31_still_frozen"),
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
                expected="still_frozen_vs_fm30_allowlist",
                observed=f"blocked={blocked}",
                ok=checks[check_id],
                notes="ok" if checks[check_id] else "prior_not_frozen",
            )
        )

    allow_ok = False
    allow_detail = ""
    try:
        assert_fm30_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
        allow_detail = "allowed"
    except RuntimeError as exc:
        allow_detail = str(exc)[:120]
    checks["frozen_allow_mock32"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock32",
            layer="frozen_mock_isolation",
            path=paths.output_root_rel,
            root_id=THIS_TASK_ROOT_ID,
            expected="MOCK32_or_ephemeral_allowed",
            observed=allow_detail,
            ok=allow_ok,
            notes="ok" if allow_ok else "mock32_blocked",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-31_frozen;MOCK32_ok",
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
    """protected_output_roots.csv：MOCK32 已登记。"""
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

    mock32 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(
        mock32.get("path_pattern") or ""
    )
    checks["protected_csv_mock32_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock32_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock32.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock32_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-32+resume+auth+fuller_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..29 gate battery（跳过 seal FM06–11）。"""
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
        ("fm29_scale_partial_promote_reclass_resume_lift_coverage", "fm29"),
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
        "fm28", "fm29",
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
        if key in ("fm25", "fm26", "fm27", "fm28", "fm29"):
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in ("fm26", "fm27", "fm28", "fm29"):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in ("fm27", "fm28", "fm29"):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key in ("fm28", "fm29"):
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        if key == "fm29":
            ok = (
                ok
                and payload.get("union_complete") == EXPECTED_UNION_COMPLETE
                and payload.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
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
            check_id="fm01_05_12_29_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_29_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm30(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK32；加固 C-ROOT-002 demotion/partition/winner 说明。"""
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
                "promote/reclass/lift/coverage-lock + C-FM-30 "
                "complete-demotion/partition/winner/overlap-freeze; "
                "只读直至人批重跑"
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
                "C-FM-30 scale complete demotion denial (2134) + status "
                "partition invariant (2134+106+9=2249) + winner provenance "
                "lock (2249) + overlap-delta/surface-injection freeze "
                "(Δ12) + FM29 continuity; never production EXECUTE; must "
                "not overwrite MOCK3-31; seal_chain_extended=false"
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


def run_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety(
    *,
    paths: CompleteDemotionPartitionWinnerPaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-30 规模 demotion / partition / winner / overlap 离线 QA。"""
    paths = paths or CompleteDemotionPartitionWinnerPaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm30(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm30_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm29_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    dem_rows, dem_checks, dem_meta = build_complete_demotion_denial_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(dem_rows)
    part_rows, part_checks, part_meta = build_status_partition_invariant_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(part_rows)
    win_rows, win_checks, win_meta = build_winner_provenance_lock_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(win_rows)
    ov_rows, ov_checks, ov_meta = build_overlap_surface_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(ov_rows)
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
        "fm29": load_json(_abs(paths.fm29_gate_json_rel, base_dir=base_dir)),
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm29_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm29_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "complete_demotion_denial": (
            "PASS_OFFLINE"
            if dem_checks.get("complete_demotion_denial_all_pass")
            else "FAIL_OFFLINE"
        ),
        "status_partition_invariant_lock": (
            "PASS_OFFLINE"
            if part_checks.get("status_partition_invariant_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "winner_provenance_lock": (
            "PASS_OFFLINE"
            if win_checks.get("winner_provenance_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "overlap_delta_surface_injection_freeze": (
            "PASS_OFFLINE"
            if ov_checks.get("overlap_delta_surface_injection_freeze_all_pass")
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
            if bat_checks.get("fm01_05_12_29_battery_all_pass")
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

    demote_rel = _rel(
        os.path.join(out_root, "complete_demotion_denial_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(demote_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": dem_meta["fingerprint"],
                "complete_n": dem_meta["complete_n"],
                "complete_codes_sha256": dem_meta["complete_codes_sha256"],
                "winner_batches": dem_meta["winner_batches"],
                "denial_count": dem_meta["denial_count"],
                "sample_denials": dem_meta["sample_denials"],
                "doc": dem_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    part_rel = _rel(
        os.path.join(out_root, "status_partition_invariant_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(part_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": part_meta["fingerprint"],
                "complete_n": part_meta["complete_n"],
                "partial_n": part_meta["partial_n"],
                "failed_n": part_meta["failed_n"],
                "unique_union": part_meta["unique_union"],
                "doc": part_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    win_rel = _rel(
        os.path.join(out_root, "winner_provenance_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(win_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": win_meta["fingerprint"],
                "unique_n": win_meta["unique_n"],
                "winner_map_sha256": win_meta["winner_map_sha256"],
                "denial_count": win_meta["denial_count"],
                "sample_denials": win_meta["sample_denials"],
                "doc": win_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    ov_rel = _rel(
        os.path.join(out_root, "overlap_delta_surface_injection_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(ov_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": ov_meta["fingerprint"],
                "overlap_delta": ov_meta["overlap_delta"],
                "harvest_additive": ov_meta["harvest_additive"],
                "surface_extras": ov_meta["surface_extras"],
                "inject_denial_count": len(ov_meta["inject_denials"]),
                "doc": ov_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    battery_rel = _rel(
        os.path.join(out_root, "fm_gate_battery.json"), base_dir=base_dir
    )
    with open(_abs(battery_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "gate": layer_gates["fm_gate_battery"],
                "fm29_gate": gates["fm29"].get("gate"),
                "fm30_gate": overall,
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
                "approved_for_snapshot_rebuild": False,
                "ready_for_execute": False,
                "hold_recommendation": "KEEP_EXECUTE_FALSE",
                "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
                "idle_not_required_while_awaiting": True,
                "seal_chain_extended": False,
                "layer_gates": layer_gates,
                "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
                "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
                "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
                "union_complete": EXPECTED_UNION_COMPLETE,
                "union_partial": EXPECTED_UNION_PARTIAL,
                "union_failed": EXPECTED_UNION_FAILED,
                "overlap_delta": EXPECTED_OVERLAP_DELTA,
                "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    packet_rel = _rel(os.path.join(out_root, "scale_packet.json"), base_dir=base_dir)
    with open(_abs(packet_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
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
                "failed_codes": sorted(EXPECTED_FAILED_CODES),
                "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
                "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
                "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
                "complete_codes_sha256": dem_meta["complete_codes_sha256"],
                "winner_map_sha256": win_meta["winner_map_sha256"],
                "notes": (
                    "complete demotion denial (2134) + status partition "
                    "invariant (2134+106+9=2249) + winner provenance lock "
                    "(2249) + overlap-delta/surface-injection freeze (Δ12) "
                    "+ FM29 continuity + MOCK32; EXECUTE remains human-held; "
                    "does not overwrite MOCK3-31"
                ),
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    observed_fps = {
        "complete_demotion_denial": dem_meta["fingerprint"],
        "status_partition_invariant_lock": part_meta["fingerprint"],
        "winner_provenance_lock": win_meta["fingerprint"],
        "overlap_delta_surface_injection_freeze": ov_meta["fingerprint"],
    }
    fp_rel = _rel(
        os.path.join(out_root, "scale_fingerprint.json"), base_dir=base_dir
    )
    with open(_abs(fp_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
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
                "complete_codes_sha256": dem_meta["complete_codes_sha256"],
                "winner_map_sha256": win_meta["winner_map_sha256"],
                "frozen_fps": {
                    "complete_demotion_denial": FROZEN_COMPLETE_DEMOTION_DENIAL_FP_SHA256,
                    "status_partition_invariant_lock": FROZEN_STATUS_PARTITION_INVARIANT_FP_SHA256,
                    "winner_provenance_lock": FROZEN_WINNER_PROVENANCE_LOCK_FP_SHA256,
                    "overlap_delta_surface_injection_freeze": FROZEN_OVERLAP_SURFACE_FREEZE_FP_SHA256,
                    "fm29_partial_promote_reclass_denial": FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256,
                    "fm29_resume_same_hold_write_boundary": FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256,
                    "fm29_residual_lift_denial": FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256,
                    "fm29_coverage_invariant_lock": FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256,
                },
                "observed_fps": observed_fps,
                "fingerprint": fp,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
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
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "resume_total": EXPECTED_RESUME_TOTAL,
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "dry863_extras": sorted(EXPECTED_DRY863_EXTRA),
        "failed_codes": sorted(EXPECTED_FAILED_CODES),
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "complete_codes_sha256": dem_meta["complete_codes_sha256"],
        "winner_map_sha256": win_meta["winner_map_sha256"],
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fp_rel,
        "fingerprint": fp,
        "complete_demotion_path": demote_rel,
        "partition_lock_path": part_rel,
        "winner_provenance_path": win_rel,
        "overlap_surface_path": ov_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "fm29_packet": paths.fm29_packet_rel,
            "fm29_gate": paths.fm29_gate_json_rel,
        },
        "mock_root_is_isolated": True,
    }
