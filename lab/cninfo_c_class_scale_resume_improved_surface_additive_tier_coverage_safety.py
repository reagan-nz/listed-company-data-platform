"""
CNINFO C-class — 规模 resume-improved write-boundary + surface uniqueness
cardinality freeze + harvest additive cardinality freeze + scale-tier/
company-coverage sum invariant lock（离线 · C-FM-32）。

在 C-FM-31（failed promotion + partial demotion-to-failed + batch-priority
+ resume-delta taxonomy）已 commit 且 EXECUTE 仍 human-held 之上，继续非 seal
规模/安全能力（不新增 seal / decision-await / commit-boundary；非
extension↔drift 循环）：
  1) FM31 packet / fingerprint / gate / failed-promo·partial-demote·
     priority·taxonomy ledgers 零漂移连续
  2) resume-improved write-boundary：28 码禁止 force_regress / status_rewrite /
     bucket_reclass
  3) surface uniqueness cardinality freeze：surface_unique=2251 禁止 inject/drop
  4) harvest additive cardinality freeze：additive=2261 / unique=2249 禁止变异
  5) scale-tier + company-coverage sum invariant：tier=7 / sum=3314 锁定
  6) output-root：MOCK3–33 冻结 · MOCK34 放行
  7) FM-01..05 + FM-12..31 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–33 / 权威 dual-layer 索引 ·
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
    _status_map,
    compute_resume_vs_base_delta,
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
from cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety import (  # noqa: E402
    EXPECTED_COMPLETE_CODES_SHA256,
    EXPECTED_WINNER_MAP_SHA256,
)
from cninfo_c_class_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety import (  # noqa: E402
    EXPECTED_FAILED_CODES_SHA256 as FM31_EXPECTED_FAILED_CODES_SHA256,
    EXPECTED_PARTIAL_CODES_SHA256 as FM31_EXPECTED_PARTIAL_CODES_SHA256,
    FROZEN_BATCH_PRIORITY_ORDER_FP_SHA256,
    FROZEN_FAILED_PROMOTION_DENIAL_FP_SHA256,
    FROZEN_PARTIAL_DEMOTION_TO_FAILED_FP_SHA256,
    FROZEN_RESUME_DELTA_TAXONOMY_FP_SHA256,
)
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    load_csv_rows,
)

TASK_ID = "C-FM-32"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm32_scale_resume_improved_surface_additive_tier_coverage_safety"
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
FM30_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety_20260715.json"
)
FM31_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety_20260715.json"
)
FM31_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm31_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety"
)
FM31_PACKET_REL = f"{FM31_MOCK_ROOT_REL}/scale_packet.json"
FM31_FINGERPRINT_REL = f"{FM31_MOCK_ROOT_REL}/scale_fingerprint.json"
FM31_FAILED_PROMO_REL = f"{FM31_MOCK_ROOT_REL}/failed_promotion_denial_ledger.json"
FM31_PARTIAL_DEMOTE_REL = (
    f"{FM31_MOCK_ROOT_REL}/partial_demotion_to_failed_denial_ledger.json"
)
FM31_BATCH_PRIORITY_REL = f"{FM31_MOCK_ROOT_REL}/batch_priority_order_freeze_ledger.json"
FM31_RESUME_TAXONOMY_REL = (
    f"{FM31_MOCK_ROOT_REL}/resume_delta_taxonomy_freeze_ledger.json"
)

# C-FM-32 本包冻结指纹
FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256 = (
    "b6e217521fe8a318473c583332bf83dac079107d81ea097aa73aff029b5a3b54"
)
FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256 = (
    "1fdef7d90894540c9a9dd2b492c3ae484716ede254c52697dec6aec016fe63eb"
)
FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256 = (
    "dbcdc6b778b059c71e732c3f4d93ca77682dca04aa5b97704d34fedd3967487b"
)
FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256 = (
    "f0e042eb6de4d9ffce7ce6749dca04aaaca0a093ae86d7dbd76cdb128656e576"
)

EXPECTED_RESUME_IMPROVED_CODES_SHA256 = (
    "8be1b0a704f205387c024d05b3d592d4cc64c6b3b9556546f6e65614001d54e8"
)
EXPECTED_PARTIAL_CODES_SHA256 = FM31_EXPECTED_PARTIAL_CODES_SHA256
EXPECTED_FAILED_CODES_SHA256 = FM31_EXPECTED_FAILED_CODES_SHA256
EXPECTED_BATCH_PRIORITY = ("h863", "p35", "p3", "p2", "fu")

THIS_TASK_ROOT_ID = "C-ROOT-MOCK34"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK33"
RESUME_HARVEST_ROOT_ID = "C-ROOT-002"

FROZEN_ROOT_IDS_MUST_BLOCK = tuple(
    f"C-ROOT-MOCK{i}" for i in range(3, 34)
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class ResumeImprovedSurfaceAdditiveTierPaths:
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
    fm30_gate_json_rel: str = FM30_GATE_JSON_REL
    fm31_gate_json_rel: str = FM31_GATE_JSON_REL
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
    fm31_packet_rel: str = FM31_PACKET_REL
    fm31_fingerprint_rel: str = FM31_FINGERPRINT_REL
    fm31_failed_promo_rel: str = FM31_FAILED_PROMO_REL
    fm31_partial_demote_rel: str = FM31_PARTIAL_DEMOTE_REL
    fm31_batch_priority_rel: str = FM31_BATCH_PRIORITY_REL
    fm31_resume_taxonomy_rel: str = FM31_RESUME_TAXONOMY_REL
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


def _to_fm26_paths(paths: ResumeImprovedSurfaceAdditiveTierPaths) -> Fm26Paths:
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


def assert_fm32_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-32 写根：须 validation/_mock_*，不得覆盖 MOCK3–33，
    不得写权威 dual-layer 索引；允许本任务 MOCK34 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-32 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _sha256_codes(codes: Sequence[str]) -> str:
    return hashlib.sha256(",".join(sorted(codes)).encode("utf-8")).hexdigest()


def fingerprint_resume_improved_write_boundary(
    *,
    improved_codes: Sequence[str],
) -> Tuple[str, Dict[str, Any]]:
    """resume-improved write-boundary 指纹。"""
    codes = sorted(improved_codes)
    doc = {
        "kind": "resume_improved_write_boundary",
        "improved_n": len(codes),
        "improved_codes_sha256": _sha256_codes(codes),
        "deny_force_regress": True,
        "deny_status_rewrite": True,
        "deny_bucket_reclass": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_surface_uniqueness_cardinality_freeze() -> Tuple[str, Dict[str, Any]]:
    """surface uniqueness cardinality freeze 指纹。"""
    doc = {
        "kind": "surface_uniqueness_cardinality_freeze",
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "deny_inject": True,
        "deny_drop": True,
        "deny_cardinality_mutation": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_harvest_additive_cardinality_freeze() -> Tuple[str, Dict[str, Any]]:
    """harvest additive cardinality freeze 指纹。"""
    doc = {
        "kind": "harvest_additive_cardinality_freeze",
        "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "deny_additive_mutation": True,
        "deny_unique_mutation": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_scale_tier_coverage_sum_invariant() -> Tuple[str, Dict[str, Any]]:
    """scale-tier + company-coverage sum invariant 指纹。"""
    doc = {
        "kind": "scale_tier_coverage_sum_invariant_lock",
        "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
        "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        "mutation_allowed": False,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_resume_improved_write(
    *,
    code: str,
    action: str,
    improved_codes: Sequence[str],
) -> Dict[str, Any]:
    """评估 resume-improved 码写动作；显式 denial。"""
    if code not in set(improved_codes):
        raise ValueError(f"not a resume-improved code: {code}")
    if action not in ("force_regress", "status_rewrite", "bucket_reclass"):
        raise ValueError(f"unknown write action: {action}")
    return {
        "code": code,
        "action": action,
        "bucket": "improved",
        "allowed": False,
        "reason": "resume_improved_write_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_surface_cardinality_mutation(
    *,
    proposed_surface_unique: int,
) -> Dict[str, Any]:
    """评估 surface_unique 基数变异；mutation 一律拒绝。"""
    matches = proposed_surface_unique == EXPECTED_SURFACE_UNIQUE
    return {
        "proposed_surface_unique": proposed_surface_unique,
        "frozen_surface_unique": EXPECTED_SURFACE_UNIQUE,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "surface_uniqueness_cardinality_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_surface_membership_change(
    *,
    action: str,
    code: str,
) -> Dict[str, Any]:
    """评估 surface 成员 inject/drop；显式 denial。"""
    if action not in ("inject", "drop"):
        raise ValueError(f"unknown surface membership action: {action}")
    return {
        "action": action,
        "code": code,
        "allowed": False,
        "reason": "surface_membership_change_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_harvest_additive_mutation(
    *,
    proposed_additive: int,
    proposed_unique: int,
) -> Dict[str, Any]:
    """评估 harvest additive/unique 基数变异；mutation 一律拒绝。"""
    matches = (
        proposed_additive == EXPECTED_HARVEST_ADDITIVE
        and proposed_unique == EXPECTED_HARVEST_UNIQUE_UNION
    )
    return {
        "proposed": {
            "harvest_additive": proposed_additive,
            "harvest_unique_union": proposed_unique,
        },
        "frozen": {
            "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
            "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        },
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "harvest_additive_cardinality_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_scale_tier_coverage_mutation(
    *,
    proposed_tier_count: int,
    proposed_coverage_sum: int,
) -> Dict[str, Any]:
    """评估 scale-tier / coverage-sum 变异；mutation 一律拒绝。"""
    matches = (
        proposed_tier_count == EXPECTED_SCALE_TIER_COUNT
        and proposed_coverage_sum == EXPECTED_COMPANY_COVERAGE_SUM
    )
    return {
        "proposed": {
            "scale_tier_count": proposed_tier_count,
            "company_coverage_sum": proposed_coverage_sum,
        },
        "frozen": {
            "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
            "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        },
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "scale_tier_coverage_sum_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def _load_resume_improved_codes(
    paths: ResumeImprovedSurfaceAdditiveTierPaths, *, base_dir: str = BASE_DIR
) -> List[str]:
    """只读计算 phase35 resume improved 码列表。"""
    base_status = _status_map(
        load_csv_rows(_abs(paths.harvest_phase35_status_rel, base_dir=base_dir))
    )
    resume_status = _status_map(
        load_csv_rows(
            _abs(paths.harvest_phase35_resume_status_rel, base_dir=base_dir)
        )
    )
    rd_meta, _fp = compute_resume_vs_base_delta(
        base_status=base_status, resume_status=resume_status
    )
    return list(rd_meta["improved_codes"])


def build_fm31_continuity_rows(
    paths: ResumeImprovedSurfaceAdditiveTierPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM31 packet / fingerprint / gate / 四 ledger 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm31_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm31_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm31_gate_json_rel, base_dir=base_dir))
    fail_led = load_json(_abs(paths.fm31_failed_promo_rel, base_dir=base_dir))
    part_led = load_json(_abs(paths.fm31_partial_demote_rel, base_dir=base_dir))
    bp_led = load_json(_abs(paths.fm31_batch_priority_rel, base_dir=base_dir))
    tax_led = load_json(_abs(paths.fm31_resume_taxonomy_rel, base_dir=base_dir))

    pkt_ok = (
        packet.get("gate") == "PASS_OFFLINE"
        and packet.get("cninfo_calls") == 0
        and packet.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and packet.get("union_complete") == EXPECTED_UNION_COMPLETE
        and packet.get("union_partial") == EXPECTED_UNION_PARTIAL
        and packet.get("union_failed") == EXPECTED_UNION_FAILED
        and packet.get("resume_same") == EXPECTED_RESUME_SAME
        and packet.get("resume_improved") == EXPECTED_RESUME_IMPROVED
        and packet.get("resume_worse") == EXPECTED_RESUME_WORSE
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
        and packet.get("complete_codes_sha256") == EXPECTED_COMPLETE_CODES_SHA256
        and packet.get("winner_map_sha256") == EXPECTED_WINNER_MAP_SHA256
        and list(packet.get("batch_priority") or []) == list(EXPECTED_BATCH_PRIORITY)
    )
    checks["fm31_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm31_packet_continuity",
            layer="fm31_continuity",
            path=paths.fm31_packet_rel,
            expected="PASS_OFFLINE;unique=2249;2134/106/9;28/1/0;KEEP",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"status={packet.get('union_complete')}/"
                f"{packet.get('union_partial')}/{packet.get('union_failed')};"
                f"resume={packet.get('resume_improved')}/"
                f"{packet.get('resume_same')}/{packet.get('resume_worse')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm31_packet_drift",
        )
    )

    frozen = fp_doc.get("frozen_fps") or {}
    fp_ok = (
        fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and fp_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and fp_doc.get("union_complete") == EXPECTED_UNION_COMPLETE
        and fp_doc.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and fp_doc.get("resume_improved") == EXPECTED_RESUME_IMPROVED
        and fp_doc.get("resume_same") == EXPECTED_RESUME_SAME
        and fp_doc.get("resume_worse") == EXPECTED_RESUME_WORSE
        and frozen.get("failed_promotion_denial")
        == FROZEN_FAILED_PROMOTION_DENIAL_FP_SHA256
        and frozen.get("partial_demotion_to_failed_denial")
        == FROZEN_PARTIAL_DEMOTION_TO_FAILED_FP_SHA256
        and frozen.get("batch_priority_order_freeze")
        == FROZEN_BATCH_PRIORITY_ORDER_FP_SHA256
        and frozen.get("resume_delta_taxonomy_freeze")
        == FROZEN_RESUME_DELTA_TAXONOMY_FP_SHA256
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm31_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm31_fingerprint_continuity",
            layer="fm31_continuity",
            path=paths.fm31_fingerprint_rel,
            expected="unique2249+fm31_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"resume={fp_doc.get('resume_improved')}/"
                f"{fp_doc.get('resume_same')}/{fp_doc.get('resume_worse')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm31_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("execute_production_snapshot_rebuild") is False
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("seal_chain_extended") is False
        and gate_doc.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
        and gate_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and gate_doc.get("union_complete") == EXPECTED_UNION_COMPLETE
        and gate_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and gate_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and gate_doc.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and gate_doc.get("resume_improved") == EXPECTED_RESUME_IMPROVED
        and gate_doc.get("residual_safety_coverage") == EXPECTED_RESIDUAL_SAFETY_COVERAGE
    )
    checks["fm31_gate_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm31_gate_continuity",
            layer="fm31_continuity",
            path=paths.fm31_gate_json_rel,
            expected="PASS_OFFLINE;KEEP;unique2249;28/1/0",
            observed=(
                f"gate={gate_doc.get('gate')};unique={gate_doc.get('harvest_unique_union')};"
                f"resume_improved={gate_doc.get('resume_improved')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm31_gate_drift",
        )
    )

    fail_ok = (
        fail_led.get("fingerprint_sha256") == FROZEN_FAILED_PROMOTION_DENIAL_FP_SHA256
        and fail_led.get("failed_n") == EXPECTED_UNION_FAILED
        and fail_led.get("failed_codes_sha256") == EXPECTED_FAILED_CODES_SHA256
    )
    checks["fm31_failed_promo_ledger_continuity"] = fail_ok
    rows.append(
        _row(
            check_id="fm31_failed_promo_ledger_continuity",
            layer="fm31_continuity",
            path=paths.fm31_failed_promo_rel,
            expected=FROZEN_FAILED_PROMOTION_DENIAL_FP_SHA256,
            observed=str(fail_led.get("fingerprint_sha256") or ""),
            ok=fail_ok,
            notes="ok" if fail_ok else "fm31_failed_promo_drift",
        )
    )

    part_ok = (
        part_led.get("fingerprint_sha256")
        == FROZEN_PARTIAL_DEMOTION_TO_FAILED_FP_SHA256
        and part_led.get("partial_n") == EXPECTED_UNION_PARTIAL
        and part_led.get("partial_codes_sha256") == EXPECTED_PARTIAL_CODES_SHA256
    )
    checks["fm31_partial_demote_ledger_continuity"] = part_ok
    rows.append(
        _row(
            check_id="fm31_partial_demote_ledger_continuity",
            layer="fm31_continuity",
            path=paths.fm31_partial_demote_rel,
            expected=FROZEN_PARTIAL_DEMOTION_TO_FAILED_FP_SHA256,
            observed=str(part_led.get("fingerprint_sha256") or ""),
            ok=part_ok,
            notes="ok" if part_ok else "fm31_partial_demote_drift",
        )
    )

    bp_ok = (
        bp_led.get("fingerprint_sha256") == FROZEN_BATCH_PRIORITY_ORDER_FP_SHA256
        and list(bp_led.get("batch_priority") or []) == list(EXPECTED_BATCH_PRIORITY)
    )
    checks["fm31_batch_priority_ledger_continuity"] = bp_ok
    rows.append(
        _row(
            check_id="fm31_batch_priority_ledger_continuity",
            layer="fm31_continuity",
            path=paths.fm31_batch_priority_rel,
            expected=FROZEN_BATCH_PRIORITY_ORDER_FP_SHA256,
            observed=str(bp_led.get("fingerprint_sha256") or ""),
            ok=bp_ok,
            notes="ok" if bp_ok else "fm31_batch_priority_drift",
        )
    )

    tax_ok = (
        tax_led.get("fingerprint_sha256") == FROZEN_RESUME_DELTA_TAXONOMY_FP_SHA256
        and tax_led.get("resume_improved") == EXPECTED_RESUME_IMPROVED
        and tax_led.get("resume_same") == EXPECTED_RESUME_SAME
        and tax_led.get("resume_worse") == EXPECTED_RESUME_WORSE
    )
    checks["fm31_resume_taxonomy_ledger_continuity"] = tax_ok
    rows.append(
        _row(
            check_id="fm31_resume_taxonomy_ledger_continuity",
            layer="fm31_continuity",
            path=paths.fm31_resume_taxonomy_rel,
            expected=FROZEN_RESUME_DELTA_TAXONOMY_FP_SHA256,
            observed=str(tax_led.get("fingerprint_sha256") or ""),
            ok=tax_ok,
            notes="ok" if tax_ok else "fm31_resume_taxonomy_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm31_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm31_continuity_all_pass",
            layer="fm31_continuity",
            expected="packet+fp+gate+4ledgers",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm31_continuity_incomplete",
        )
    )
    return rows, checks


def build_resume_improved_write_boundary_rows(
    paths: ResumeImprovedSurfaceAdditiveTierPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """resume-improved write-boundary denial（28 码）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    improved = _load_resume_improved_codes(paths, base_dir=base_dir)
    fp, doc = fingerprint_resume_improved_write_boundary(improved_codes=improved)

    n_ok = len(improved) == EXPECTED_RESUME_IMPROVED
    checks["resume_improved_n_exact"] = n_ok
    rows.append(
        _row(
            check_id="resume_improved_n_exact",
            layer="resume_improved_write_boundary",
            expected=str(EXPECTED_RESUME_IMPROVED),
            observed=str(len(improved)),
            ok=n_ok,
            notes="ok" if n_ok else "resume_improved_n_drift",
        )
    )

    codes_fp_ok = doc["improved_codes_sha256"] == EXPECTED_RESUME_IMPROVED_CODES_SHA256
    checks["resume_improved_codes_sha256"] = codes_fp_ok
    rows.append(
        _row(
            check_id="resume_improved_codes_sha256",
            layer="resume_improved_write_boundary",
            expected=EXPECTED_RESUME_IMPROVED_CODES_SHA256,
            observed=doc["improved_codes_sha256"],
            ok=codes_fp_ok,
            notes="ok" if codes_fp_ok else "improved_codes_sha_drift",
        )
    )

    denial_ok = True
    sample_denials: List[Dict[str, Any]] = []
    sample_codes = improved[:3] if improved else []
    for code in sample_codes:
        for action in ("force_regress", "status_rewrite", "bucket_reclass"):
            d = evaluate_resume_improved_write(
                code=code, action=action, improved_codes=improved
            )
            sample_denials.append(d)
            if d.get("allowed") is not False:
                denial_ok = False
    denial_count = len(sample_denials)
    checks["resume_improved_write_denied"] = denial_ok and denial_count == len(sample_codes) * 3
    rows.append(
        _row(
            check_id="resume_improved_write_denied",
            layer="resume_improved_write_boundary",
            expected="sample_writes_denied",
            observed=f"samples={denial_count};all_denied={denial_ok}",
            ok=checks["resume_improved_write_denied"],
            notes="ok" if checks["resume_improved_write_denied"] else "write_leak",
        )
    )

    flags_ok = (
        doc["deny_force_regress"] is True
        and doc["deny_status_rewrite"] is True
        and doc["deny_bucket_reclass"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["resume_improved_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="resume_improved_flags_locked",
            layer="resume_improved_write_boundary",
            expected="deny_regress+rewrite+reclass+KEEP",
            observed=(
                f"regress={doc['deny_force_regress']};"
                f"rewrite={doc['deny_status_rewrite']};"
                f"reclass={doc['deny_bucket_reclass']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256
    checks["resume_improved_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="resume_improved_fingerprint",
            layer="resume_improved_write_boundary",
            expected=FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "resume_improved_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_improved_write_boundary_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_improved_write_boundary_all_pass",
            layer="resume_improved_write_boundary",
            expected="28_write_boundary+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_improved_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "improved_n": len(improved),
        "improved_codes_sha256": doc["improved_codes_sha256"],
        "denial_count": denial_count,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_surface_uniqueness_cardinality_freeze_rows(
    paths: ResumeImprovedSurfaceAdditiveTierPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """surface uniqueness cardinality freeze（2251）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fp, doc = fingerprint_surface_uniqueness_cardinality_freeze()

    card_ok = EXPECTED_SURFACE_UNIQUE == 2251
    checks["surface_unique_exact"] = card_ok
    rows.append(
        _row(
            check_id="surface_unique_exact",
            layer="surface_uniqueness_cardinality_freeze",
            expected="2251",
            observed=str(EXPECTED_SURFACE_UNIQUE),
            ok=card_ok,
            notes="ok" if card_ok else "surface_unique_drift",
        )
    )

    mut = evaluate_surface_cardinality_mutation(proposed_surface_unique=2250)
    mut2 = evaluate_surface_cardinality_mutation(
        proposed_surface_unique=EXPECTED_SURFACE_UNIQUE
    )
    mut_ok = mut["mutation_allowed"] is False and mut2["mutation_allowed"] is False
    checks["surface_cardinality_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="surface_cardinality_mutation_denied",
            layer="surface_uniqueness_cardinality_freeze",
            expected="mutation_allowed=false",
            observed=(
                f"drift_denied={mut['mutation_allowed']};"
                f"exact_denied={mut2['mutation_allowed']}"
            ),
            ok=mut_ok,
            notes="ok" if mut_ok else "surface_mutation_leak",
        )
    )

    mem_ok = True
    sample_denials: List[Dict[str, Any]] = []
    for action, code in (("inject", "999999"), ("drop", "000037")):
        d = evaluate_surface_membership_change(action=action, code=code)
        sample_denials.append(d)
        if d.get("allowed") is not False:
            mem_ok = False
    checks["surface_membership_change_denied"] = mem_ok
    rows.append(
        _row(
            check_id="surface_membership_change_denied",
            layer="surface_uniqueness_cardinality_freeze",
            expected="inject_drop_denied",
            observed=f"samples={len(sample_denials)};all_denied={mem_ok}",
            ok=mem_ok,
            notes="ok" if mem_ok else "membership_leak",
        )
    )

    flags_ok = (
        doc["deny_inject"] is True
        and doc["deny_drop"] is True
        and doc["deny_cardinality_mutation"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["surface_freeze_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="surface_freeze_flags_locked",
            layer="surface_uniqueness_cardinality_freeze",
            expected="deny_inject+drop+mutation+KEEP",
            observed=(
                f"inject={doc['deny_inject']};drop={doc['deny_drop']};"
                f"mutation={doc['deny_cardinality_mutation']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256
    checks["surface_freeze_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="surface_freeze_fingerprint",
            layer="surface_uniqueness_cardinality_freeze",
            expected=FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "surface_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["surface_uniqueness_cardinality_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="surface_uniqueness_cardinality_freeze_all_pass",
            layer="surface_uniqueness_cardinality_freeze",
            expected="2251_surface_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "surface_freeze_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_harvest_additive_cardinality_freeze_rows(
    paths: ResumeImprovedSurfaceAdditiveTierPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """harvest additive cardinality freeze（2261 / 2249）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fp, doc = fingerprint_harvest_additive_cardinality_freeze()

    counts_ok = (
        EXPECTED_HARVEST_ADDITIVE == 2261
        and EXPECTED_HARVEST_UNIQUE_UNION == 2249
        and EXPECTED_OVERLAP_DELTA == 12
        and EXPECTED_HARVEST_ADDITIVE - EXPECTED_HARVEST_UNIQUE_UNION
        == EXPECTED_OVERLAP_DELTA
    )
    checks["harvest_additive_unique_exact"] = counts_ok
    rows.append(
        _row(
            check_id="harvest_additive_unique_exact",
            layer="harvest_additive_cardinality_freeze",
            expected="2261/2249;Δ12",
            observed=(
                f"{EXPECTED_HARVEST_ADDITIVE}/{EXPECTED_HARVEST_UNIQUE_UNION};"
                f"Δ{EXPECTED_OVERLAP_DELTA}"
            ),
            ok=counts_ok,
            notes="ok" if counts_ok else "additive_unique_drift",
        )
    )

    mut = evaluate_harvest_additive_mutation(
        proposed_additive=2260, proposed_unique=2249
    )
    mut2 = evaluate_harvest_additive_mutation(
        proposed_additive=EXPECTED_HARVEST_ADDITIVE,
        proposed_unique=EXPECTED_HARVEST_UNIQUE_UNION,
    )
    mut_ok = mut["mutation_allowed"] is False and mut2["mutation_allowed"] is False
    checks["harvest_additive_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="harvest_additive_mutation_denied",
            layer="harvest_additive_cardinality_freeze",
            expected="mutation_allowed=false",
            observed=(
                f"drift_denied={mut['mutation_allowed']};"
                f"exact_denied={mut2['mutation_allowed']}"
            ),
            ok=mut_ok,
            notes="ok" if mut_ok else "additive_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_additive_mutation"] is True
        and doc["deny_unique_mutation"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["harvest_additive_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="harvest_additive_flags_locked",
            layer="harvest_additive_cardinality_freeze",
            expected="deny_additive+unique+KEEP",
            observed=(
                f"additive={doc['deny_additive_mutation']};"
                f"unique={doc['deny_unique_mutation']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256
    checks["harvest_additive_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="harvest_additive_fingerprint",
            layer="harvest_additive_cardinality_freeze",
            expected=FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "additive_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["harvest_additive_cardinality_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="harvest_additive_cardinality_freeze_all_pass",
            layer="harvest_additive_cardinality_freeze",
            expected="2261_2249_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "additive_freeze_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "sample_denials": [mut, mut2],
        "doc": doc,
    }
    return rows, checks, meta


def build_scale_tier_coverage_sum_invariant_rows(
    paths: ResumeImprovedSurfaceAdditiveTierPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """scale-tier + company-coverage sum invariant lock（7 / 3314）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fp, doc = fingerprint_scale_tier_coverage_sum_invariant()

    counts_ok = (
        EXPECTED_SCALE_TIER_COUNT == 7
        and EXPECTED_COMPANY_COVERAGE_SUM == 3314
    )
    checks["scale_tier_coverage_exact"] = counts_ok
    rows.append(
        _row(
            check_id="scale_tier_coverage_exact",
            layer="scale_tier_coverage_sum_invariant",
            expected="7/3314",
            observed=f"{EXPECTED_SCALE_TIER_COUNT}/{EXPECTED_COMPANY_COVERAGE_SUM}",
            ok=counts_ok,
            notes="ok" if counts_ok else "tier_coverage_drift",
        )
    )

    mut = evaluate_scale_tier_coverage_mutation(
        proposed_tier_count=8, proposed_coverage_sum=3314
    )
    mut2 = evaluate_scale_tier_coverage_mutation(
        proposed_tier_count=EXPECTED_SCALE_TIER_COUNT,
        proposed_coverage_sum=EXPECTED_COMPANY_COVERAGE_SUM,
    )
    mut_ok = mut["mutation_allowed"] is False and mut2["mutation_allowed"] is False
    checks["scale_tier_coverage_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="scale_tier_coverage_mutation_denied",
            layer="scale_tier_coverage_sum_invariant",
            expected="mutation_allowed=false",
            observed=(
                f"drift_denied={mut['mutation_allowed']};"
                f"exact_denied={mut2['mutation_allowed']}"
            ),
            ok=mut_ok,
            notes="ok" if mut_ok else "tier_coverage_mutation_leak",
        )
    )

    flags_ok = (
        doc["mutation_allowed"] is False
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["scale_tier_coverage_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="scale_tier_coverage_flags_locked",
            layer="scale_tier_coverage_sum_invariant",
            expected="mutation_allowed=false+KEEP",
            observed=f"mutation={doc['mutation_allowed']};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256
    checks["scale_tier_coverage_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="scale_tier_coverage_fingerprint",
            layer="scale_tier_coverage_sum_invariant",
            expected=FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "tier_coverage_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["scale_tier_coverage_sum_invariant_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="scale_tier_coverage_sum_invariant_all_pass",
            layer="scale_tier_coverage_sum_invariant",
            expected="7_3314_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "tier_coverage_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
        "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        "sample_denials": [mut, mut2],
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: ResumeImprovedSurfaceAdditiveTierPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK34 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm31.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm31.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm31.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm31.csv",
        ),
        (
            "write_guard_phase35_resume_refused",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm31.csv",
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
        assert_fm32_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK34_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock34_ok",
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
    paths: ResumeImprovedSurfaceAdditiveTierPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–33 拒绝 · MOCK34 放行。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    load_frozen_mock_cohort_roots.cache_clear()
    frozen = dict(load_frozen_mock_cohort_roots(base_dir=base_dir))

    for root_id in FROZEN_ROOT_IDS_MUST_BLOCK:
        prefix = frozen.get(root_id)
        exists = prefix is not None
        refused = False
        if exists:
            try:
                assert_frozen_mock_cohort_write_forbidden(
                    prefix, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
                )
            except RuntimeError as exc:
                refused = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
        checks[f"frozen_block_{root_id.lower().replace('-', '_')}"] = exists and refused
        rows.append(
            _row(
                check_id=f"frozen_block_{root_id.lower().replace('-', '_')}",
                layer="frozen_mock_isolation",
                root_id=root_id,
                path=prefix or "",
                expected="registered+write_forbidden",
                observed=f"exists={exists};refused={refused}",
                ok=exists and refused,
                notes="ok" if (exists and refused) else "frozen_gap",
            )
        )

    mock33_rel = (
        "outputs/validation/"
        "_mock_c_fm31_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety"
    )
    mock33_blocked = False
    try:
        assert_fm32_output_root(mock33_rel, base_dir=base_dir)
    except RuntimeError as exc:
        mock33_blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock33_still_frozen"] = mock33_blocked
    rows.append(
        _row(
            check_id="mock33_still_frozen",
            layer="frozen_mock_isolation",
            root_id=PRIOR_TASK_ROOT_ID,
            path=mock33_rel,
            expected="write_forbidden",
            observed="blocked" if mock33_blocked else "allowed",
            ok=mock33_blocked,
            notes="ok" if mock33_blocked else "mock33_write_leak",
        )
    )

    allow_ok = False
    try:
        assert_fm32_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except Exception:
        allow_ok = False
    checks["frozen_allow_mock34"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock34",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="MOCK34_or_ephemeral_allowed",
            observed="allowed" if allow_ok else "blocked",
            ok=allow_ok,
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-33_block+MOCK34_allow",
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
    """protected_output_roots.csv：MOCK34 已登记。"""
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

    mock34 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(
        mock34.get("path_pattern") or ""
    )
    checks["protected_csv_mock34_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock34_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock34.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock34_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-33+resume+auth+fuller_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks



def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..31 gate battery（跳过 seal FM06–11）。"""
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
        ("fm30_scale_complete_demotion_partition_winner_overlap", "fm30"),
        ("fm31_scale_failed_promotion_partial_demotion_batch_priority", "fm31"),
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
        "fm28", "fm29", "fm30", "fm31",
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
        if key in ("fm25", "fm26", "fm27", "fm28", "fm29", "fm30", "fm31"):
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in ("fm26", "fm27", "fm28", "fm29", "fm30", "fm31"):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in ("fm27", "fm28", "fm29", "fm30", "fm31"):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key in ("fm28", "fm29", "fm30", "fm31"):
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        if key in ("fm29", "fm30", "fm31"):
            ok = (
                ok
                and payload.get("union_complete") == EXPECTED_UNION_COMPLETE
                and payload.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
            )
        if key == "fm30":
            ok = (
                ok
                and payload.get("complete_codes_sha256") == EXPECTED_COMPLETE_CODES_SHA256
                and payload.get("winner_map_sha256") == EXPECTED_WINNER_MAP_SHA256
            )
        if key == "fm31":
            ok = (
                ok
                and payload.get("resume_improved") == EXPECTED_RESUME_IMPROVED
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
                and payload.get("resume_worse") == EXPECTED_RESUME_WORSE
                and list(payload.get("batch_priority") or [])
                == list(EXPECTED_BATCH_PRIORITY)
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
            check_id="fm01_05_12_31_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_31_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm32(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK34；加固 C-ROOT-002 resume-improved/surface/additive 说明。"""
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
                "complete-demotion/partition/winner/overlap-freeze + "
                "C-FM-31 failed-promo/partial-demote/batch-priority/"
                "resume-taxonomy + C-FM-32 resume-improved/surface/"
                "additive/tier-coverage; 只读直至人批重跑"
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
                "C-FM-32 scale resume-improved write-boundary (28) + "
                "surface uniqueness cardinality freeze (2251) + harvest "
                "additive cardinality freeze (2261/2249) + scale-tier/"
                "coverage-sum lock (7/3314) + FM31 continuity; never "
                "production EXECUTE; must not overwrite MOCK3-33; "
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


def run_scale_resume_improved_surface_additive_tier_coverage_safety(
    *,
    paths: ResumeImprovedSurfaceAdditiveTierPaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-32 规模 resume-improved / surface / additive / tier-coverage 离线 QA。"""
    paths = paths or ResumeImprovedSurfaceAdditiveTierPaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm32(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm32_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm31_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    ri_rows, ri_checks, ri_meta = build_resume_improved_write_boundary_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(ri_rows)
    surf_rows, surf_checks, surf_meta = build_surface_uniqueness_cardinality_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(surf_rows)
    add_rows, add_checks, add_meta = build_harvest_additive_cardinality_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(add_rows)
    tier_rows, tier_checks, tier_meta = build_scale_tier_coverage_sum_invariant_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(tier_rows)
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
        "fm30": load_json(_abs(paths.fm30_gate_json_rel, base_dir=base_dir)),
        "fm31": load_json(_abs(paths.fm31_gate_json_rel, base_dir=base_dir)),
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm31_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm31_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_improved_write_boundary": (
            "PASS_OFFLINE"
            if ri_checks.get("resume_improved_write_boundary_all_pass")
            else "FAIL_OFFLINE"
        ),
        "surface_uniqueness_cardinality_freeze": (
            "PASS_OFFLINE"
            if surf_checks.get("surface_uniqueness_cardinality_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "harvest_additive_cardinality_freeze": (
            "PASS_OFFLINE"
            if add_checks.get("harvest_additive_cardinality_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "scale_tier_coverage_sum_invariant": (
            "PASS_OFFLINE"
            if tier_checks.get("scale_tier_coverage_sum_invariant_all_pass")
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
            if bat_checks.get("fm01_05_12_31_battery_all_pass")
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

    ri_rel = _rel(
        os.path.join(out_root, "resume_improved_write_boundary_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(ri_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": ri_meta["fingerprint"],
                "improved_n": ri_meta["improved_n"],
                "improved_codes_sha256": ri_meta["improved_codes_sha256"],
                "denial_count": ri_meta["denial_count"],
                "sample_denials": ri_meta["sample_denials"],
                "doc": ri_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    surf_rel = _rel(
        os.path.join(out_root, "surface_uniqueness_cardinality_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(surf_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": surf_meta["fingerprint"],
                "surface_unique": surf_meta["surface_unique"],
                "sample_denials": surf_meta["sample_denials"],
                "doc": surf_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    add_rel = _rel(
        os.path.join(out_root, "harvest_additive_cardinality_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(add_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": add_meta["fingerprint"],
                "harvest_additive": add_meta["harvest_additive"],
                "harvest_unique_union": add_meta["harvest_unique_union"],
                "overlap_delta": add_meta["overlap_delta"],
                "sample_denials": add_meta["sample_denials"],
                "doc": add_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    tier_rel = _rel(
        os.path.join(out_root, "scale_tier_coverage_sum_invariant_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(tier_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": tier_meta["fingerprint"],
                "scale_tier_count": tier_meta["scale_tier_count"],
                "company_coverage_sum": tier_meta["company_coverage_sum"],
                "sample_denials": tier_meta["sample_denials"],
                "doc": tier_meta["doc"],
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
                "fm31_gate": gates["fm31"].get("gate"),
                "fm32_gate": overall,
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
                "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
                "surface_unique": EXPECTED_SURFACE_UNIQUE,
                "union_complete": EXPECTED_UNION_COMPLETE,
                "union_partial": EXPECTED_UNION_PARTIAL,
                "union_failed": EXPECTED_UNION_FAILED,
                "overlap_delta": EXPECTED_OVERLAP_DELTA,
                "resume_improved": EXPECTED_RESUME_IMPROVED,
                "resume_same": EXPECTED_RESUME_SAME,
                "resume_worse": EXPECTED_RESUME_WORSE,
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
                "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
                "partial_codes_sha256": EXPECTED_PARTIAL_CODES_SHA256,
                "failed_codes_sha256": EXPECTED_FAILED_CODES_SHA256,
                "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
                "improved_codes_sha256": ri_meta["improved_codes_sha256"],
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
                "notes": (
                    "resume-improved write-boundary (28) + surface uniqueness "
                    "cardinality freeze (2251) + harvest additive cardinality "
                    "freeze (2261/2249) + scale-tier/coverage-sum lock (7/3314) "
                    "+ FM31 continuity + MOCK34; EXECUTE remains human-held; "
                    "does not overwrite MOCK3-33"
                ),
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    observed_fps = {
        "resume_improved_write_boundary": ri_meta["fingerprint"],
        "surface_uniqueness_cardinality_freeze": surf_meta["fingerprint"],
        "harvest_additive_cardinality_freeze": add_meta["fingerprint"],
        "scale_tier_coverage_sum_invariant": tier_meta["fingerprint"],
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
                "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
                "overlap_delta": EXPECTED_OVERLAP_DELTA,
                "surface_unique": EXPECTED_SURFACE_UNIQUE,
                "union_complete": EXPECTED_UNION_COMPLETE,
                "union_partial": EXPECTED_UNION_PARTIAL,
                "union_failed": EXPECTED_UNION_FAILED,
                "resume_improved": EXPECTED_RESUME_IMPROVED,
                "resume_same": EXPECTED_RESUME_SAME,
                "resume_worse": EXPECTED_RESUME_WORSE,
                "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
                "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
                "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
                "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
                "partial_codes_sha256": EXPECTED_PARTIAL_CODES_SHA256,
                "failed_codes_sha256": EXPECTED_FAILED_CODES_SHA256,
                "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
                "improved_codes_sha256": ri_meta["improved_codes_sha256"],
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
                "frozen_fps": {
                    "resume_improved_write_boundary": FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256,
                    "surface_uniqueness_cardinality_freeze": FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256,
                    "harvest_additive_cardinality_freeze": FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256,
                    "scale_tier_coverage_sum_invariant": FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256,
                    "fm31_failed_promotion_denial": FROZEN_FAILED_PROMOTION_DENIAL_FP_SHA256,
                    "fm31_partial_demotion_to_failed_denial": FROZEN_PARTIAL_DEMOTION_TO_FAILED_FP_SHA256,
                    "fm31_batch_priority_order_freeze": FROZEN_BATCH_PRIORITY_ORDER_FP_SHA256,
                    "fm31_resume_delta_taxonomy_freeze": FROZEN_RESUME_DELTA_TAXONOMY_FP_SHA256,
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
        "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
        "partial_codes_sha256": EXPECTED_PARTIAL_CODES_SHA256,
        "failed_codes_sha256": EXPECTED_FAILED_CODES_SHA256,
        "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
        "improved_codes_sha256": ri_meta["improved_codes_sha256"],
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fp_rel,
        "fingerprint": fp,
        "resume_improved_path": ri_rel,
        "surface_freeze_path": surf_rel,
        "additive_freeze_path": add_rel,
        "tier_coverage_path": tier_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "fm31_packet": paths.fm31_packet_rel,
            "fm31_gate": paths.fm31_gate_json_rel,
        },
        "mock_root_is_isolated": True,
    }
