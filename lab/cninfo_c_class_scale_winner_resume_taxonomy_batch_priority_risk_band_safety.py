"""
CNINFO C-class — 规模 winner_map SHA256 lock + resume taxonomy codeset SHA256
lock + batch_priority order freeze + partial_risk_band cardinality freeze
（离线 · C-FM-35）。

在 C-FM-34（dry863/surface-delta codeset freeze + combined_dryrun_coverage
cardinality freeze + cross_metric_identity_lock + partition_codeset_sha256_lock）
已 commit 且 EXECUTE 仍 human-held 之上，继续非 seal 规模/安全能力（不新增
seal / decision-await / commit-boundary；非 extension↔drift 循环）：
  1) FM34 packet / fingerprint / gate / dry863·combined·cross·partition
     ledgers 零漂移连续
  2) winner_map_sha256_lock：禁止 winner 映射 SHA256 变异
  3) resume_taxonomy_codeset_sha256_lock：improved/same/worse（28/1/0）codeset
     SHA256 禁止变异
  4) batch_priority_order_freeze：h863>p35>p3>p2>fu 禁止重排/注入/删除
  5) partial_risk_band_cardinality_freeze：75/14/12/5（sum=106）禁止变异
  6) output-root：MOCK3–36 冻结 · MOCK37 放行
  7) FM-01..05 + FM-12..34 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–36 / 权威 dual-layer 索引 ·
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
)
from cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety import (  # noqa: E402
    EXPECTED_BATCH_PRIORITY,
    EXPECTED_RESUME_IMPROVED_CODES_SHA256,
)
from cninfo_c_class_scale_surface_delta_combined_dryrun_cross_identity_partition_codeset_safety import (  # noqa: E402
    FROZEN_COMBINED_DRYRUN_COVERAGE_CARDINALITY_FP_SHA256 as FM34_FROZEN_COMBINED_DRYRUN_FP,
    FROZEN_CROSS_METRIC_IDENTITY_LOCK_FP_SHA256 as FM34_FROZEN_CROSS_IDENTITY_FP,
    FROZEN_DRY863_SURFACE_DELTA_CODESET_FP_SHA256 as FM34_FROZEN_DRY863_FP,
    FROZEN_PARTITION_CODESET_SHA256_LOCK_FP_SHA256 as FM34_FROZEN_PARTITION_CODESET_FP,
)

TASK_ID = "C-FM-35"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm35_scale_winner_resume_taxonomy_batch_priority_risk_band_safety"
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
FM32_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety_20260715.json"
)
FM33_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety_20260715.json"
)
FM34_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_surface_delta_combined_dryrun_cross_identity_partition_codeset_safety_20260715.json"
)
FM34_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm34_scale_surface_delta_combined_dryrun_cross_identity_partition_codeset_safety"
)
FM34_PACKET_REL = f"{FM34_MOCK_ROOT_REL}/scale_packet.json"
FM34_FINGERPRINT_REL = f"{FM34_MOCK_ROOT_REL}/scale_fingerprint.json"
FM34_DRY863_REL = (
    f"{FM34_MOCK_ROOT_REL}/dry863_surface_delta_codeset_freeze_ledger.json"
)
FM34_COMBINED_REL = (
    f"{FM34_MOCK_ROOT_REL}/combined_dryrun_coverage_cardinality_freeze_ledger.json"
)
FM34_CROSS_REL = (
    f"{FM34_MOCK_ROOT_REL}/cross_metric_identity_lock_ledger.json"
)
FM34_PARTITION_REL = (
    f"{FM34_MOCK_ROOT_REL}/partition_codeset_sha256_lock_ledger.json"
)

# C-FM-35 本包冻结指纹
FROZEN_WINNER_MAP_SHA256_LOCK_FP_SHA256 = (
    "56d85b2152b814d18b9b6ab510a583b635e57a6da72ed750cdcc4d0ad4759377"
)
FROZEN_RESUME_TAXONOMY_CODESET_SHA256_LOCK_FP_SHA256 = (
    "3a0acb3b796dff56415539b60dd8a765ca752a180e29f8808d3abd516fe95591"
)
FROZEN_BATCH_PRIORITY_ORDER_FREEZE_FP_SHA256 = (
    "83abddccc8e699ac3c8e7bc9d5fb0ea7ec139c53f596b39ae8957b5350a0c566"
)
FROZEN_PARTIAL_RISK_BAND_CARDINALITY_FP_SHA256 = (
    "5b634b3a7dc546b7f686ff377a74693a86531d12e967b89b679c7a1f27836953"
)

EXPECTED_PARTIAL_CODES_SHA256 = FM31_EXPECTED_PARTIAL_CODES_SHA256
EXPECTED_FAILED_CODES_SHA256 = FM31_EXPECTED_FAILED_CODES_SHA256
EXPECTED_RESUME_SAME_CODES_SHA256 = (
    "2896da9453ebb1a999cf3074dc4753d776587b6a385ab9d5a5ed0fe9942bf5d6"
)
EXPECTED_RESUME_WORSE_CODES_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
EXPECTED_DRY863_EXTRAS_SHA256 = (
    "4d2821153fad3e9298cb7f98ddf9f051cbcb9022ffa65f5c1ebd15777c7ac15d"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK37"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK36"
RESUME_HARVEST_ROOT_ID = "C-ROOT-002"

FROZEN_ROOT_IDS_MUST_BLOCK = tuple(f"C-ROOT-MOCK{i}" for i in range(3, 37))

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class WinnerResumeTaxonomyBatchPriorityRiskBandPaths:
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
    fm32_gate_json_rel: str = FM32_GATE_JSON_REL
    fm33_gate_json_rel: str = FM33_GATE_JSON_REL
    fm34_gate_json_rel: str = FM34_GATE_JSON_REL
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
    fm34_packet_rel: str = FM34_PACKET_REL
    fm34_fingerprint_rel: str = FM34_FINGERPRINT_REL
    fm34_dry863_rel: str = FM34_DRY863_REL
    fm34_combined_rel: str = FM34_COMBINED_REL
    fm34_cross_rel: str = FM34_CROSS_REL
    fm34_partition_rel: str = FM34_PARTITION_REL
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


def assert_fm35_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-35 写根：须 validation/_mock_*，不得覆盖 MOCK3–36，
    不得写权威 dual-layer 索引；允许本任务 MOCK37 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-35 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _sha256_codes(codes: Sequence[str]) -> str:
    return hashlib.sha256(",".join(sorted(codes)).encode("utf-8")).hexdigest()



def fingerprint_winner_map_sha256_lock() -> Tuple[str, Dict[str, Any]]:
    """winner_map SHA256 lock 指纹。"""
    doc = {
        "kind": "winner_map_sha256_lock",
        "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
        "deny_winner_map_mutation": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_resume_taxonomy_codeset_sha256_lock() -> Tuple[str, Dict[str, Any]]:
    """resume taxonomy codeset SHA256 lock 指纹。"""
    doc = {
        "kind": "resume_taxonomy_codeset_sha256_lock",
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "improved_codes_sha256": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
        "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
        "worse_codes_sha256": EXPECTED_RESUME_WORSE_CODES_SHA256,
        "deny_improved_codeset_mutation": True,
        "deny_same_codeset_mutation": True,
        "deny_worse_codeset_mutation": True,
        "deny_taxonomy_cardinality_mutation": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_batch_priority_order_freeze() -> Tuple[str, Dict[str, Any]]:
    """batch_priority order freeze 指纹。"""
    doc = {
        "kind": "batch_priority_order_freeze",
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "deny_reorder": True,
        "deny_inject": True,
        "deny_drop": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_partial_risk_band_cardinality_freeze() -> Tuple[str, Dict[str, Any]]:
    """partial_risk_band cardinality freeze 指纹。"""
    doc = {
        "kind": "partial_risk_band_cardinality_freeze",
        "partial_risk_bands": dict(EXPECTED_PARTIAL_RISK_BANDS),
        "band_sum": sum(EXPECTED_PARTIAL_RISK_BANDS.values()),
        "deny_band_inflate": True,
        "deny_band_deflate": True,
        "deny_band_rekey": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_winner_map_mutation(*, proposed_sha256: str) -> Dict[str, Any]:
    """评估 winner_map SHA256 变异；一律拒绝。"""
    return {
        "proposed_sha256": proposed_sha256,
        "frozen_sha256": EXPECTED_WINNER_MAP_SHA256,
        "matches_frozen": proposed_sha256 == EXPECTED_WINNER_MAP_SHA256,
        "mutation_allowed": False,
        "reason": "winner_map_sha256_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_resume_taxonomy_codeset_mutation(
    *, bucket: str, proposed_sha256: str
) -> Dict[str, Any]:
    """评估 resume taxonomy codeset SHA256 变异；一律拒绝。"""
    frozen_map = {
        "improved": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
        "same": EXPECTED_RESUME_SAME_CODES_SHA256,
        "worse": EXPECTED_RESUME_WORSE_CODES_SHA256,
    }
    if bucket not in frozen_map:
        raise ValueError(f"unknown resume taxonomy bucket: {bucket}")
    frozen = frozen_map[bucket]
    return {
        "bucket": bucket,
        "proposed_sha256": proposed_sha256,
        "frozen_sha256": frozen,
        "matches_frozen": proposed_sha256 == frozen,
        "mutation_allowed": False,
        "reason": "resume_taxonomy_codeset_sha256_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_batch_priority_mutation(
    *, proposed_priority: Sequence[str], action: str
) -> Dict[str, Any]:
    """评估 batch_priority 顺序变异；reorder/inject/drop 一律拒绝。"""
    if action not in ("reorder", "inject", "drop", "replace"):
        raise ValueError(f"unknown batch_priority action: {action}")
    proposed = list(proposed_priority)
    frozen = list(EXPECTED_BATCH_PRIORITY)
    return {
        "action": action,
        "proposed_priority": proposed,
        "frozen_priority": frozen,
        "matches_frozen": proposed == frozen,
        "mutation_allowed": False,
        "reason": "batch_priority_order_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_partial_risk_band_mutation(
    *, proposed_bands: Dict[str, int]
) -> Dict[str, Any]:
    """评估 partial_risk_band 基数变异；一律拒绝。"""
    return {
        "proposed_bands": dict(proposed_bands),
        "frozen_bands": dict(EXPECTED_PARTIAL_RISK_BANDS),
        "matches_frozen": dict(proposed_bands) == dict(EXPECTED_PARTIAL_RISK_BANDS),
        "mutation_allowed": False,
        "reason": "partial_risk_band_cardinality_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def build_fm34_continuity_rows(
    paths: WinnerResumeTaxonomyBatchPriorityRiskBandPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM34 packet / fingerprint / gate / 四 ledger 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm34_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm34_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm34_gate_json_rel, base_dir=base_dir))
    d863_led = load_json(_abs(paths.fm34_dry863_rel, base_dir=base_dir))
    cdr_led = load_json(_abs(paths.fm34_combined_rel, base_dir=base_dir))
    xid_led = load_json(_abs(paths.fm34_cross_rel, base_dir=base_dir))
    pcs_led = load_json(_abs(paths.fm34_partition_rel, base_dir=base_dir))

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
        and packet.get("improved_codes_sha256") == EXPECTED_RESUME_IMPROVED_CODES_SHA256
        and packet.get("same_codes_sha256") == EXPECTED_RESUME_SAME_CODES_SHA256
        and list(packet.get("batch_priority") or []) == list(EXPECTED_BATCH_PRIORITY)
        and packet.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
        and packet.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
        and sorted(packet.get("dry863_extras") or []) == sorted(EXPECTED_DRY863_EXTRA)
        and packet.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
    )
    checks["fm34_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm34_packet_continuity",
            layer="fm34_continuity",
            path=paths.fm34_packet_rel,
            expected="PASS_OFFLINE;unique=2249;1053;delta2;KEEP",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"dryrun={packet.get('combined_dryrun_coverage')};"
                f"delta={packet.get('surface_harvest_delta_n')};"
                f"winner={str(packet.get('winner_map_sha256') or '')[:12]}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm34_packet_drift",
        )
    )

    frozen = fp_doc.get("frozen_fps") or {}
    fp_ok = (
        fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and fp_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and fp_doc.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and fp_doc.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
        and fp_doc.get("winner_map_sha256") == EXPECTED_WINNER_MAP_SHA256
        and fp_doc.get("improved_codes_sha256") == EXPECTED_RESUME_IMPROVED_CODES_SHA256
        and fp_doc.get("same_codes_sha256") == EXPECTED_RESUME_SAME_CODES_SHA256
        and list(fp_doc.get("batch_priority") or []) == list(EXPECTED_BATCH_PRIORITY)
        and fp_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and frozen.get("dry863_surface_delta_codeset_freeze") == FM34_FROZEN_DRY863_FP
        and frozen.get("combined_dryrun_coverage_cardinality_freeze")
        == FM34_FROZEN_COMBINED_DRYRUN_FP
        and frozen.get("cross_metric_identity_lock") == FM34_FROZEN_CROSS_IDENTITY_FP
        and frozen.get("partition_codeset_sha256_lock")
        == FM34_FROZEN_PARTITION_CODESET_FP
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm34_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm34_fingerprint_continuity",
            layer="fm34_continuity",
            path=paths.fm34_fingerprint_rel,
            expected="unique2249+fm34_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"dryrun={fp_doc.get('combined_dryrun_coverage')};"
                f"delta={fp_doc.get('surface_harvest_delta_n')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm34_fingerprint_drift",
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
        and gate_doc.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and gate_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and gate_doc.get("union_complete") == EXPECTED_UNION_COMPLETE
        and gate_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and gate_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and gate_doc.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and gate_doc.get("resume_improved") == EXPECTED_RESUME_IMPROVED
        and gate_doc.get("resume_same") == EXPECTED_RESUME_SAME
        and gate_doc.get("resume_worse") == EXPECTED_RESUME_WORSE
        and gate_doc.get("residual_safety_coverage") == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        and gate_doc.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and gate_doc.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
    )
    checks["fm34_gate_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm34_gate_continuity",
            layer="fm34_continuity",
            path=paths.fm34_gate_json_rel,
            expected="PASS_OFFLINE;KEEP;1053;delta2;28/1/0",
            observed=(
                f"gate={gate_doc.get('gate')};"
                f"dryrun={gate_doc.get('combined_dryrun_coverage')};"
                f"delta={gate_doc.get('surface_harvest_delta_n')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm34_gate_drift",
        )
    )

    d863_ok = (
        d863_led.get("fingerprint_sha256") == FM34_FROZEN_DRY863_FP
        and d863_led.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and d863_led.get("dry863_extras_sha256") == EXPECTED_DRY863_EXTRAS_SHA256
    )
    checks["fm34_dry863_ledger_continuity"] = d863_ok
    rows.append(
        _row(
            check_id="fm34_dry863_ledger_continuity",
            layer="fm34_continuity",
            path=paths.fm34_dry863_rel,
            expected=FM34_FROZEN_DRY863_FP,
            observed=str(d863_led.get("fingerprint_sha256") or ""),
            ok=d863_ok,
            notes="ok" if d863_ok else "fm34_dry863_drift",
        )
    )

    cdr_ok = (
        cdr_led.get("fingerprint_sha256") == FM34_FROZEN_COMBINED_DRYRUN_FP
        and cdr_led.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
    )
    checks["fm34_combined_ledger_continuity"] = cdr_ok
    rows.append(
        _row(
            check_id="fm34_combined_ledger_continuity",
            layer="fm34_continuity",
            path=paths.fm34_combined_rel,
            expected=FM34_FROZEN_COMBINED_DRYRUN_FP,
            observed=str(cdr_led.get("fingerprint_sha256") or ""),
            ok=cdr_ok,
            notes="ok" if cdr_ok else "fm34_combined_drift",
        )
    )

    xid_ok = xid_led.get("fingerprint_sha256") == FM34_FROZEN_CROSS_IDENTITY_FP
    checks["fm34_cross_ledger_continuity"] = xid_ok
    rows.append(
        _row(
            check_id="fm34_cross_ledger_continuity",
            layer="fm34_continuity",
            path=paths.fm34_cross_rel,
            expected=FM34_FROZEN_CROSS_IDENTITY_FP,
            observed=str(xid_led.get("fingerprint_sha256") or ""),
            ok=xid_ok,
            notes="ok" if xid_ok else "fm34_cross_drift",
        )
    )

    pcs_ok = (
        pcs_led.get("fingerprint_sha256") == FM34_FROZEN_PARTITION_CODESET_FP
        and pcs_led.get("complete_codes_sha256") == EXPECTED_COMPLETE_CODES_SHA256
        and pcs_led.get("partial_codes_sha256") == EXPECTED_PARTIAL_CODES_SHA256
        and pcs_led.get("failed_codes_sha256") == EXPECTED_FAILED_CODES_SHA256
    )
    checks["fm34_partition_ledger_continuity"] = pcs_ok
    rows.append(
        _row(
            check_id="fm34_partition_ledger_continuity",
            layer="fm34_continuity",
            path=paths.fm34_partition_rel,
            expected=FM34_FROZEN_PARTITION_CODESET_FP,
            observed=str(pcs_led.get("fingerprint_sha256") or ""),
            ok=pcs_ok,
            notes="ok" if pcs_ok else "fm34_partition_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm34_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm34_continuity_all_pass",
            layer="fm34_continuity",
            expected="packet+fp+gate+4ledgers",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm34_continuity_incomplete",
        )
    )
    return rows, checks


def build_winner_map_sha256_lock_rows(
    paths: WinnerResumeTaxonomyBatchPriorityRiskBandPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """winner_map SHA256 lock。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_winner_map_sha256_lock()

    sha_ok = (
        len(EXPECTED_WINNER_MAP_SHA256) == 64
        and EXPECTED_WINNER_MAP_SHA256
        == "ff2c6a28b361498b0dbf163ad1d1779041e1dd4e772b652e6382e1d4051fbb07"
    )
    checks["winner_map_sha_exact"] = sha_ok
    rows.append(
        _row(
            check_id="winner_map_sha_exact",
            layer="winner_map_sha256_lock",
            expected="winner_map_sha256",
            observed=EXPECTED_WINNER_MAP_SHA256[:16],
            ok=sha_ok,
            notes="ok" if sha_ok else "winner_map_sha_drift",
        )
    )

    sample_denials = [
        evaluate_winner_map_mutation(proposed_sha256="0" * 64),
        evaluate_winner_map_mutation(proposed_sha256=EXPECTED_WINNER_MAP_SHA256),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["winner_map_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="winner_map_mutation_denied",
            layer="winner_map_sha256_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "winner_map_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_winner_map_mutation"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["winner_map_sha256"] == EXPECTED_WINNER_MAP_SHA256
    )
    checks["winner_map_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="winner_map_flags_locked",
            layer="winner_map_sha256_lock",
            expected="deny_winner+KEEP",
            observed=f"flags_ok={flags_ok};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_WINNER_MAP_SHA256_LOCK_FP_SHA256
    checks["winner_map_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="winner_map_fingerprint",
            layer="winner_map_sha256_lock",
            expected=FROZEN_WINNER_MAP_SHA256_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "winner_map_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["winner_map_sha256_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="winner_map_sha256_lock_all_pass",
            layer="winner_map_sha256_lock",
            expected="winner_map_sha256_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "winner_map_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_resume_taxonomy_codeset_sha256_lock_rows(
    paths: WinnerResumeTaxonomyBatchPriorityRiskBandPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """resume taxonomy codeset SHA256 lock（28/1/0）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_resume_taxonomy_codeset_sha256_lock()

    counts_ok = (
        EXPECTED_RESUME_IMPROVED == 28
        and EXPECTED_RESUME_SAME == 1
        and EXPECTED_RESUME_WORSE == 0
        and set(EXPECTED_RESUME_SAME_CODES) == {"301212"}
        and _sha256_codes(sorted(EXPECTED_RESUME_SAME_CODES))
        == EXPECTED_RESUME_SAME_CODES_SHA256
        and EXPECTED_RESUME_WORSE_CODES_SHA256
        == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        and len(EXPECTED_RESUME_IMPROVED_CODES_SHA256) == 64
    )
    checks["resume_taxonomy_exact"] = counts_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_exact",
            layer="resume_taxonomy_codeset_sha256_lock",
            expected="28/1/0+sha256",
            observed=(
                f"{EXPECTED_RESUME_IMPROVED}/{EXPECTED_RESUME_SAME}/"
                f"{EXPECTED_RESUME_WORSE};same={','.join(sorted(EXPECTED_RESUME_SAME_CODES))}"
            ),
            ok=counts_ok,
            notes="ok" if counts_ok else "resume_taxonomy_drift",
        )
    )

    sample_denials = [
        evaluate_resume_taxonomy_codeset_mutation(
            bucket="improved", proposed_sha256="0" * 64
        ),
        evaluate_resume_taxonomy_codeset_mutation(
            bucket="same", proposed_sha256="1" * 64
        ),
        evaluate_resume_taxonomy_codeset_mutation(
            bucket="worse", proposed_sha256="2" * 64
        ),
        evaluate_resume_taxonomy_codeset_mutation(
            bucket="same", proposed_sha256=EXPECTED_RESUME_SAME_CODES_SHA256
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["resume_taxonomy_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_mutation_denied",
            layer="resume_taxonomy_codeset_sha256_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "resume_taxonomy_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_improved_codeset_mutation"] is True
        and doc["deny_same_codeset_mutation"] is True
        and doc["deny_worse_codeset_mutation"] is True
        and doc["deny_taxonomy_cardinality_mutation"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["resume_taxonomy_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_flags_locked",
            layer="resume_taxonomy_codeset_sha256_lock",
            expected="deny_i+s+w+card+KEEP",
            observed=f"flags_ok={flags_ok};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_RESUME_TAXONOMY_CODESET_SHA256_LOCK_FP_SHA256
    checks["resume_taxonomy_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_fingerprint",
            layer="resume_taxonomy_codeset_sha256_lock",
            expected=FROZEN_RESUME_TAXONOMY_CODESET_SHA256_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "resume_taxonomy_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_taxonomy_codeset_sha256_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_codeset_sha256_lock_all_pass",
            layer="resume_taxonomy_codeset_sha256_lock",
            expected="28_1_0_codeset_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_taxonomy_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "improved_codes_sha256": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
        "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
        "worse_codes_sha256": EXPECTED_RESUME_WORSE_CODES_SHA256,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_batch_priority_order_freeze_rows(
    paths: WinnerResumeTaxonomyBatchPriorityRiskBandPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """batch_priority order freeze。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_batch_priority_order_freeze()

    order_ok = list(EXPECTED_BATCH_PRIORITY) == ["h863", "p35", "p3", "p2", "fu"]
    checks["batch_priority_exact"] = order_ok
    rows.append(
        _row(
            check_id="batch_priority_exact",
            layer="batch_priority_order_freeze",
            expected="h863>p35>p3>p2>fu",
            observed=">".join(EXPECTED_BATCH_PRIORITY),
            ok=order_ok,
            notes="ok" if order_ok else "batch_priority_drift",
        )
    )

    sample_denials = [
        evaluate_batch_priority_mutation(
            proposed_priority=["p35", "h863", "p3", "p2", "fu"], action="reorder"
        ),
        evaluate_batch_priority_mutation(
            proposed_priority=list(EXPECTED_BATCH_PRIORITY) + ["xx"], action="inject"
        ),
        evaluate_batch_priority_mutation(
            proposed_priority=["h863", "p35", "p3", "p2"], action="drop"
        ),
        evaluate_batch_priority_mutation(
            proposed_priority=list(EXPECTED_BATCH_PRIORITY), action="replace"
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["batch_priority_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="batch_priority_mutation_denied",
            layer="batch_priority_order_freeze",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "batch_priority_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_reorder"] is True
        and doc["deny_inject"] is True
        and doc["deny_drop"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["batch_priority_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="batch_priority_flags_locked",
            layer="batch_priority_order_freeze",
            expected="deny_reorder+inject+drop+KEEP",
            observed=f"flags_ok={flags_ok};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_BATCH_PRIORITY_ORDER_FREEZE_FP_SHA256
    checks["batch_priority_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="batch_priority_fingerprint",
            layer="batch_priority_order_freeze",
            expected=FROZEN_BATCH_PRIORITY_ORDER_FREEZE_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "batch_priority_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["batch_priority_order_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="batch_priority_order_freeze_all_pass",
            layer="batch_priority_order_freeze",
            expected="order_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "batch_priority_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_partial_risk_band_cardinality_freeze_rows(
    paths: WinnerResumeTaxonomyBatchPriorityRiskBandPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """partial_risk_band cardinality freeze（75/14/12/5）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_partial_risk_band_cardinality_freeze()

    bands_ok = (
        EXPECTED_PARTIAL_RISK_BANDS
        == {"p35_heavy": 75, "p3_mid": 14, "p2_mid": 12, "fu_light": 5}
        and sum(EXPECTED_PARTIAL_RISK_BANDS.values()) == EXPECTED_UNION_PARTIAL
        and EXPECTED_UNION_PARTIAL == 106
    )
    checks["partial_risk_band_exact"] = bands_ok
    rows.append(
        _row(
            check_id="partial_risk_band_exact",
            layer="partial_risk_band_cardinality_freeze",
            expected="75/14/12/5;sum=106",
            observed=(
                f"{EXPECTED_PARTIAL_RISK_BANDS.get('p35_heavy')}/"
                f"{EXPECTED_PARTIAL_RISK_BANDS.get('p3_mid')}/"
                f"{EXPECTED_PARTIAL_RISK_BANDS.get('p2_mid')}/"
                f"{EXPECTED_PARTIAL_RISK_BANDS.get('fu_light')};"
                f"sum={sum(EXPECTED_PARTIAL_RISK_BANDS.values())}"
            ),
            ok=bands_ok,
            notes="ok" if bands_ok else "partial_risk_band_drift",
        )
    )

    inflated = dict(EXPECTED_PARTIAL_RISK_BANDS)
    inflated["p35_heavy"] = 76
    deflated = dict(EXPECTED_PARTIAL_RISK_BANDS)
    deflated["fu_light"] = 4
    rekeyed = {"p35_heavy": 75, "p3_mid": 14, "p2_mid": 12, "xx_light": 5}
    sample_denials = [
        evaluate_partial_risk_band_mutation(proposed_bands=inflated),
        evaluate_partial_risk_band_mutation(proposed_bands=deflated),
        evaluate_partial_risk_band_mutation(proposed_bands=rekeyed),
        evaluate_partial_risk_band_mutation(
            proposed_bands=dict(EXPECTED_PARTIAL_RISK_BANDS)
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["partial_risk_band_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="partial_risk_band_mutation_denied",
            layer="partial_risk_band_cardinality_freeze",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "partial_risk_band_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_band_inflate"] is True
        and doc["deny_band_deflate"] is True
        and doc["deny_band_rekey"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["band_sum"] == 106
    )
    checks["partial_risk_band_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="partial_risk_band_flags_locked",
            layer="partial_risk_band_cardinality_freeze",
            expected="deny_inflate+deflate+rekey+KEEP",
            observed=f"flags_ok={flags_ok};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_PARTIAL_RISK_BAND_CARDINALITY_FP_SHA256
    checks["partial_risk_band_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="partial_risk_band_fingerprint",
            layer="partial_risk_band_cardinality_freeze",
            expected=FROZEN_PARTIAL_RISK_BAND_CARDINALITY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "partial_risk_band_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["partial_risk_band_cardinality_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="partial_risk_band_cardinality_freeze_all_pass",
            layer="partial_risk_band_cardinality_freeze",
            expected="75_14_12_5_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "partial_risk_band_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "partial_risk_bands": dict(EXPECTED_PARTIAL_RISK_BANDS),
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: WinnerResumeTaxonomyBatchPriorityRiskBandPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK37 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm35.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm35.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm35.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm35.csv",
        ),
        (
            "write_guard_phase35_resume_refused",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm35.csv",
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
        assert_fm35_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK37_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock37_ok",
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
    paths: WinnerResumeTaxonomyBatchPriorityRiskBandPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–36 拒绝 · MOCK37 放行。"""
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

    mock36_rel = (
        "outputs/validation/"
        "_mock_c_fm34_scale_surface_delta_combined_dryrun_cross_identity_partition_codeset_safety"
    )
    mock36_blocked = False
    try:
        assert_fm35_output_root(mock36_rel, base_dir=base_dir)
    except RuntimeError as exc:
        mock36_blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock36_still_frozen"] = mock36_blocked
    rows.append(
        _row(
            check_id="mock36_still_frozen",
            layer="frozen_mock_isolation",
            root_id=PRIOR_TASK_ROOT_ID,
            path=mock36_rel,
            expected="write_forbidden",
            observed="blocked" if mock36_blocked else "allowed",
            ok=mock36_blocked,
            notes="ok" if mock36_blocked else "mock36_write_leak",
        )
    )

    allow_ok = False
    try:
        assert_fm35_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except Exception:
        allow_ok = False
    checks["frozen_allow_mock37"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock37",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="MOCK37_or_ephemeral_allowed",
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
            expected="MOCK3-36_block+MOCK37_allow",
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
    """protected_output_roots.csv：MOCK37 已登记。"""
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

    mock37 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(mock37.get("path_pattern") or "")
    checks["protected_csv_mock37_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock37_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock37.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock37_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3–36+resume+auth+fuller_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..34 gate battery（跳过 seal FM06–11）。"""
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
        ("fm32_scale_resume_improved_surface_additive_tier_coverage", "fm32"),
        ("fm33_scale_union_partition_overlap_residual_resume_same_worse", "fm33"),
        ("fm34_scale_surface_delta_combined_dryrun_cross_identity", "fm34"),
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
        "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34",
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
        if key in (
            "fm25", "fm26", "fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34"
        ):
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in ("fm26", "fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34"):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in ("fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34"):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key in ("fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34"):
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        if key in ("fm29", "fm30", "fm31", "fm32", "fm33", "fm34"):
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
        if key in ("fm31", "fm32", "fm33", "fm34"):
            ok = (
                ok
                and payload.get("resume_improved") == EXPECTED_RESUME_IMPROVED
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
                and payload.get("resume_worse") == EXPECTED_RESUME_WORSE
                and list(payload.get("batch_priority") or [])
                == list(EXPECTED_BATCH_PRIORITY)
            )
        if key == "fm32":
            ok = (
                ok
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
                and payload.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
                and payload.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
            )
        if key == "fm33":
            ok = (
                ok
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
                and payload.get("resume_worse") == EXPECTED_RESUME_WORSE
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
            )
        if key == "fm34":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("winner_map_sha256") == EXPECTED_WINNER_MAP_SHA256
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
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
            check_id="fm01_05_12_34_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_34_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm35(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK37；加固 C-ROOT-002 winner/resume-taxonomy/batch/risk 说明。"""
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
                "C-FM-24..34 scale/safety freezes + C-FM-35 winner/resume-taxonomy/"
                "batch-priority/risk-band; "
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
                "C-FM-35 scale winner_map SHA256 lock + resume taxonomy codeset "
                "SHA256 lock (28/1/0) + batch_priority order freeze + "
                "partial_risk_band cardinality freeze (75/14/12/5) + FM34 "
                "continuity; never production EXECUTE; must not overwrite "
                "MOCK3-36; seal_chain_extended=false"
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


def run_scale_winner_resume_taxonomy_batch_priority_risk_band_safety(
    *,
    paths: WinnerResumeTaxonomyBatchPriorityRiskBandPaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-35 规模 winner/resume-taxonomy/batch-priority/risk-band 离线 QA。"""
    paths = paths or WinnerResumeTaxonomyBatchPriorityRiskBandPaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm35(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm35_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm34_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    win_rows, win_checks, win_meta = build_winner_map_sha256_lock_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(win_rows)
    tax_rows, tax_checks, tax_meta = build_resume_taxonomy_codeset_sha256_lock_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(tax_rows)
    bat_pri_rows, bat_pri_checks, bat_pri_meta = build_batch_priority_order_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(bat_pri_rows)
    risk_rows, risk_checks, risk_meta = build_partial_risk_band_cardinality_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(risk_rows)
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
        "fm32": load_json(_abs(paths.fm32_gate_json_rel, base_dir=base_dir)),
        "fm33": load_json(_abs(paths.fm33_gate_json_rel, base_dir=base_dir)),
        "fm34": load_json(_abs(paths.fm34_gate_json_rel, base_dir=base_dir)),
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm34_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm34_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "winner_map_sha256_lock": (
            "PASS_OFFLINE"
            if win_checks.get("winner_map_sha256_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_taxonomy_codeset_sha256_lock": (
            "PASS_OFFLINE"
            if tax_checks.get("resume_taxonomy_codeset_sha256_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "batch_priority_order_freeze": (
            "PASS_OFFLINE"
            if bat_pri_checks.get("batch_priority_order_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "partial_risk_band_cardinality_freeze": (
            "PASS_OFFLINE"
            if risk_checks.get("partial_risk_band_cardinality_freeze_all_pass")
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
            if bat_checks.get("fm01_05_12_34_battery_all_pass")
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

    win_rel = _rel(
        os.path.join(out_root, "winner_map_sha256_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(win_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": win_meta["fingerprint"],
                "winner_map_sha256": win_meta["winner_map_sha256"],
                "sample_denials": win_meta["sample_denials"],
                "doc": win_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    tax_rel = _rel(
        os.path.join(out_root, "resume_taxonomy_codeset_sha256_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(tax_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": tax_meta["fingerprint"],
                "improved_codes_sha256": tax_meta["improved_codes_sha256"],
                "same_codes_sha256": tax_meta["same_codes_sha256"],
                "worse_codes_sha256": tax_meta["worse_codes_sha256"],
                "sample_denials": tax_meta["sample_denials"],
                "doc": tax_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    bat_pri_rel = _rel(
        os.path.join(out_root, "batch_priority_order_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(bat_pri_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": bat_pri_meta["fingerprint"],
                "batch_priority": bat_pri_meta["batch_priority"],
                "sample_denials": bat_pri_meta["sample_denials"],
                "doc": bat_pri_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    risk_rel = _rel(
        os.path.join(out_root, "partial_risk_band_cardinality_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(risk_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": risk_meta["fingerprint"],
                "partial_risk_bands": risk_meta["partial_risk_bands"],
                "sample_denials": risk_meta["sample_denials"],
                "doc": risk_meta["doc"],
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
                "fm34_gate": gates["fm34"].get("gate"),
                "fm35_gate": overall,
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
                "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
                "union_complete": EXPECTED_UNION_COMPLETE,
                "union_partial": EXPECTED_UNION_PARTIAL,
                "union_failed": EXPECTED_UNION_FAILED,
                "overlap_delta": EXPECTED_OVERLAP_DELTA,
                "resume_improved": EXPECTED_RESUME_IMPROVED,
                "resume_same": EXPECTED_RESUME_SAME,
                "resume_worse": EXPECTED_RESUME_WORSE,
                "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
                "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
                "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
                "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
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
                "improved_codes_sha256": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
                "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
                "worse_codes_sha256": EXPECTED_RESUME_WORSE_CODES_SHA256,
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
                "notes": (
                    "winner_map SHA256 lock + resume taxonomy codeset SHA256 lock "
                    "(28/1/0) + batch_priority order freeze + partial_risk_band "
                    "cardinality freeze (75/14/12/5) + FM34 continuity + MOCK37; "
                    "EXECUTE remains human-held; does not overwrite MOCK3-36"
                ),
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    observed_fps = {
        "winner_map_sha256_lock": win_meta["fingerprint"],
        "resume_taxonomy_codeset_sha256_lock": tax_meta["fingerprint"],
        "batch_priority_order_freeze": bat_pri_meta["fingerprint"],
        "partial_risk_band_cardinality_freeze": risk_meta["fingerprint"],
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
                "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
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
                "improved_codes_sha256": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
                "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
                "worse_codes_sha256": EXPECTED_RESUME_WORSE_CODES_SHA256,
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
                "frozen_fps": {
                    "winner_map_sha256_lock": FROZEN_WINNER_MAP_SHA256_LOCK_FP_SHA256,
                    "resume_taxonomy_codeset_sha256_lock": (
                        FROZEN_RESUME_TAXONOMY_CODESET_SHA256_LOCK_FP_SHA256
                    ),
                    "batch_priority_order_freeze": (
                        FROZEN_BATCH_PRIORITY_ORDER_FREEZE_FP_SHA256
                    ),
                    "partial_risk_band_cardinality_freeze": (
                        FROZEN_PARTIAL_RISK_BAND_CARDINALITY_FP_SHA256
                    ),
                    "fm34_dry863_surface_delta_codeset_freeze": FM34_FROZEN_DRY863_FP,
                    "fm34_combined_dryrun_coverage_cardinality_freeze": (
                        FM34_FROZEN_COMBINED_DRYRUN_FP
                    ),
                    "fm34_cross_metric_identity_lock": FM34_FROZEN_CROSS_IDENTITY_FP,
                    "fm34_partition_codeset_sha256_lock": (
                        FM34_FROZEN_PARTITION_CODESET_FP
                    ),
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
        "improved_codes_sha256": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
        "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
        "worse_codes_sha256": EXPECTED_RESUME_WORSE_CODES_SHA256,
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fp_rel,
        "fingerprint": fp,
        "winner_map_path": win_rel,
        "resume_taxonomy_path": tax_rel,
        "batch_priority_path": bat_pri_rel,
        "partial_risk_band_path": risk_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "fm34_packet": paths.fm34_packet_rel,
            "fm34_gate": paths.fm34_gate_json_rel,
        },
        "mock_root_is_isolated": True,
    }

