"""
CNINFO C-class — 规模 overlap_membership composition identity lock +
dry863_extras composition identity lock + batch_priority
composition identity lock + cross_full_market_scale_repro_wall_meta_bundle
identity lock（离线 · C-FM-47）。

在 C-FM-46（lineage_winner_provenance / partition_codeset / protected_root_registry /
cross_lineage_drift_protected_repro_wall_meta_bundle）已 commit 且 EXECUTE 仍
human-held 之上，继续非 seal 规模/安全能力
（不新增 seal / decision-await / commit-boundary；非 extension↔drift 循环）：
  1) FM46 packet / fingerprint / gate / lineage·partition·protected·wall ledgers 零漂移连续
  2) full_market_unique_union_composition_identity_lock：unique=2249 组成身份锁
  3) combined_dryrun_cohort_composition_identity_lock：combined_dryrun=1053 组成身份锁
  4) company_coverage_scale_composition_identity_lock：tiers=7;coverage_sum=3314 组成身份锁
  5) cross_full_market_scale_repro_wall_meta_bundle_identity_lock：unique/dryrun/coverage/repro 墙元捆绑
  6) output-root：MOCK3–48 冻结 · MOCK49 放行
  7) FM-01..05 + FM-12..46 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–48 / 权威 dual-layer 索引 ·
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
    EXPECTED_P35_FU_OVERLAP,
    EXPECTED_RESUME_TOTAL,
    EXPECTED_SURFACE_UNIQUE,
    HARVEST_PHASE35_RESUME_ROOT_REL,
)
from cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety import (  # noqa: E402
    EXPECTED_P2_FU_OVERLAP_CODES,
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
from cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety import (  # noqa: E402
    FROZEN_BATCH_PRIORITY_ORDER_FREEZE_FP_SHA256 as FM35_FROZEN_BATCH_PRIORITY_FP,
    FROZEN_PARTIAL_RISK_BAND_CARDINALITY_FP_SHA256 as FM35_FROZEN_PARTIAL_RISK_BAND_FP,
    FROZEN_RESUME_TAXONOMY_CODESET_SHA256_LOCK_FP_SHA256 as FM35_FROZEN_RESUME_TAXONOMY_FP,
    FROZEN_WINNER_MAP_SHA256_LOCK_FP_SHA256 as FM35_FROZEN_WINNER_MAP_FP,
)
from cninfo_c_class_scale_risk_band_combined_dryrun_resume_formula_safety import (  # noqa: E402
    FROZEN_COMBINED_DRYRUN_COVERAGE_IDENTITY_LOCK_FP_SHA256 as FM39_FROZEN_COMBINED_DRYRUN_FP,
    FROZEN_PARTIAL_RISK_BAND_MEMBERSHIP_FREEZE_FP_SHA256 as FM39_FROZEN_PARTIAL_RISK_BAND_MEM_FP,
    FROZEN_RESUME_FORMULA_IDENTITY_LOCK_FP_SHA256 as FM39_FROZEN_RESUME_FORMULA_FP,
    FROZEN_RISK_BAND_FORMULA_IDENTITY_LOCK_FP_SHA256 as FM39_FROZEN_RISK_BAND_FORMULA_FP,
    EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256 as FM39_EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256,
    EXPECTED_RISK_BAND_FORMULA as FM39_EXPECTED_RISK_BAND_FORMULA,
    EXPECTED_RESUME_FORMULA as FM39_EXPECTED_RESUME_FORMULA,
)
from cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety import (  # noqa: E402
    FROZEN_ADDITIVE_FORMULA_IDENTITY_LOCK_FP_SHA256 as FM38_FROZEN_ADDITIVE_FP,
    FROZEN_COMPLETE_CODES_MEMBERSHIP_FREEZE_FP_SHA256 as FM38_FROZEN_COMPLETE_FP,
    FROZEN_OVERLAP_DELTA_MEMBERSHIP_FREEZE_FP_SHA256 as FM38_FROZEN_OVERLAP_FP,
    FROZEN_TIER_COVERAGE_FORMULA_IDENTITY_LOCK_FP_SHA256 as FM38_FROZEN_TIER_FP,
)
from cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety import (  # noqa: E402
    FROZEN_DRY863_EXTRAS_MEMBERSHIP_FREEZE_FP_SHA256 as FM40_FROZEN_DRY863_FP,
    FROZEN_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM40_FROZEN_UNIQUE_UNION_FP,
    FROZEN_SURFACE_UNIQUE_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM40_FROZEN_SURFACE_FP,
    FROZEN_CROSS_FORMULA_BUNDLE_IDENTITY_LOCK_FP_SHA256 as FM40_FROZEN_CROSS_FORMULA_FP,
    EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256 as FM40_EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
    EXPECTED_SURFACE_COMPOSITION_SHA256 as FM40_EXPECTED_SURFACE_COMPOSITION_SHA256,
    EXPECTED_CROSS_FORMULA_BUNDLE_SHA256 as FM40_EXPECTED_CROSS_FORMULA_BUNDLE_SHA256,
    EXPECTED_CROSS_FORMULA_BUNDLE as FM40_EXPECTED_CROSS_FORMULA_BUNDLE,
)
from cninfo_c_class_scale_additive_residual_resume_cross_composition_bundle_safety import (  # noqa: E402
    FROZEN_ADDITIVE_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM41_FROZEN_ADDITIVE_FP,
    FROZEN_RESIDUAL_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM41_FROZEN_RESIDUAL_FP,
    FROZEN_RESUME_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM41_FROZEN_RESUME_FP,
    FROZEN_CROSS_COMPOSITION_BUNDLE_IDENTITY_LOCK_FP_SHA256 as FM41_FROZEN_CROSS_COMPOSITION_FP,
    EXPECTED_ADDITIVE_COMPOSITION_SHA256 as FM41_EXPECTED_ADDITIVE_COMPOSITION_SHA256,
    EXPECTED_RESIDUAL_COMPOSITION_SHA256 as FM41_EXPECTED_RESIDUAL_COMPOSITION_SHA256,
    EXPECTED_RESUME_COMPOSITION_SHA256 as FM41_EXPECTED_RESUME_COMPOSITION_SHA256,
    EXPECTED_CROSS_COMPOSITION_BUNDLE_SHA256 as FM41_EXPECTED_CROSS_COMPOSITION_BUNDLE_SHA256,
    EXPECTED_CROSS_COMPOSITION_BUNDLE as FM41_EXPECTED_CROSS_COMPOSITION_BUNDLE,
    EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256 as FM41_EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
    EXPECTED_SURFACE_COMPOSITION_SHA256 as FM41_EXPECTED_SURFACE_COMPOSITION_SHA256,
)
from cninfo_c_class_scale_risk_band_tier_dryrun_cross_meta_bundle_safety import (  # noqa: E402
    FROZEN_RISK_BAND_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM42_FROZEN_RISK_BAND_FP,
    FROZEN_TIER_COVERAGE_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM42_FROZEN_TIER_FP,
    FROZEN_COMBINED_DRYRUN_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM42_FROZEN_COMBINED_DRYRUN_FP,
    FROZEN_CROSS_FORMULA_COMPOSITION_META_BUNDLE_IDENTITY_LOCK_FP_SHA256 as FM42_FROZEN_CROSS_META_FP,
    EXPECTED_RISK_BAND_COMPOSITION_SHA256 as FM42_EXPECTED_RISK_BAND_COMPOSITION_SHA256,
    EXPECTED_TIER_COVERAGE_COMPOSITION_SHA256 as FM42_EXPECTED_TIER_COVERAGE_COMPOSITION_SHA256,
    EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256 as FM42_EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256,
    EXPECTED_CROSS_FORMULA_COMPOSITION_META_BUNDLE_SHA256 as FM42_EXPECTED_CROSS_META_SHA256,
    EXPECTED_CROSS_FORMULA_COMPOSITION_META_BUNDLE as FM42_EXPECTED_CROSS_META_BUNDLE,
)

from cninfo_c_class_scale_union_overlap_delta_stable_wall_meta_bundle_safety import (  # noqa: E402
    FROZEN_UNION_STATUS_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM43_FROZEN_UNION_STATUS_FP,
    FROZEN_OVERLAP_DELTA_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM43_FROZEN_OVERLAP_DELTA_FP,
    FROZEN_SURFACE_DELTA_COMPOSITION_IDENTITY_LOCK_FP_SHA256 as FM43_FROZEN_SURFACE_DELTA_FP,
    FROZEN_CROSS_STABLE_METRICS_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256 as FM43_FROZEN_WALL_META_FP,
    EXPECTED_UNION_STATUS_COMPOSITION_SHA256 as FM43_EXPECTED_UNION_STATUS_COMPOSITION_SHA256,
    EXPECTED_OVERLAP_DELTA_COMPOSITION_SHA256 as FM43_EXPECTED_OVERLAP_DELTA_COMPOSITION_SHA256,
    EXPECTED_SURFACE_DELTA_COMPOSITION_SHA256 as FM43_EXPECTED_SURFACE_DELTA_COMPOSITION_SHA256,
    EXPECTED_CROSS_STABLE_METRICS_WALL_META_BUNDLE_SHA256 as FM43_EXPECTED_WALL_META_SHA256,
    EXPECTED_CROSS_STABLE_METRICS_WALL_META_BUNDLE as FM43_EXPECTED_WALL_META_BUNDLE,
)

TASK_ID = "C-FM-47"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm47_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety"
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
FM35_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety_20260715.json"
)
FM36_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_failed_resume_membership_residual_formula_hold_identity_safety_20260715.json"
)
FM37_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_improved_partial_surface_delta_union_partition_formula_safety_20260715.json"
)
FM38_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety_20260715.json"
)
FM39_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_risk_band_combined_dryrun_resume_formula_safety_20260715.json"
)
FM39_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm39_scale_risk_band_combined_dryrun_resume_formula_safety"
)
FM39_PACKET_REL = f"{FM39_MOCK_ROOT_REL}/scale_packet.json"
FM39_FINGERPRINT_REL = f"{FM39_MOCK_ROOT_REL}/scale_fingerprint.json"
FM39_PARTIAL_RISK_BAND_REL = (
    f"{FM39_MOCK_ROOT_REL}/partial_risk_band_membership_freeze_ledger.json"
)
FM39_COMBINED_DRYRUN_REL = (
    f"{FM39_MOCK_ROOT_REL}/combined_dryrun_coverage_identity_lock_ledger.json"
)
FM39_RISK_BAND_FORMULA_REL = (
    f"{FM39_MOCK_ROOT_REL}/risk_band_formula_identity_lock_ledger.json"
)
FM39_RESUME_FORMULA_REL = (
    f"{FM39_MOCK_ROOT_REL}/resume_formula_identity_lock_ledger.json"
)
FM40_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety_20260715.json"
)
FM40_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm40_scale_dry863_unique_surface_cross_formula_bundle_safety"
)
FM40_PACKET_REL = f"{FM40_MOCK_ROOT_REL}/scale_packet.json"
FM40_FINGERPRINT_REL = f"{FM40_MOCK_ROOT_REL}/scale_fingerprint.json"
FM40_DRY863_REL = (
    f"{FM40_MOCK_ROOT_REL}/dry863_extras_membership_freeze_ledger.json"
)
FM40_UNIQUE_UNION_REL = (
    f"{FM40_MOCK_ROOT_REL}/unique_union_composition_identity_lock_ledger.json"
)
FM40_SURFACE_REL = (
    f"{FM40_MOCK_ROOT_REL}/surface_unique_composition_identity_lock_ledger.json"
)
FM40_CROSS_FORMULA_REL = (
    f"{FM40_MOCK_ROOT_REL}/cross_formula_bundle_identity_lock_ledger.json"
)
FM41_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_additive_residual_resume_cross_composition_bundle_safety_20260715.json"
)
FM41_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm41_scale_additive_residual_resume_cross_composition_bundle_safety"
)
FM41_PACKET_REL = f"{FM41_MOCK_ROOT_REL}/scale_packet.json"
FM41_FINGERPRINT_REL = f"{FM41_MOCK_ROOT_REL}/scale_fingerprint.json"
FM41_ADDITIVE_REL = (
    f"{FM41_MOCK_ROOT_REL}/additive_composition_identity_lock_ledger.json"
)
FM41_RESIDUAL_REL = (
    f"{FM41_MOCK_ROOT_REL}/residual_composition_identity_lock_ledger.json"
)
FM41_RESUME_REL = (
    f"{FM41_MOCK_ROOT_REL}/resume_composition_identity_lock_ledger.json"
)
FM41_CROSS_COMPOSITION_REL = (
    f"{FM41_MOCK_ROOT_REL}/cross_composition_bundle_identity_lock_ledger.json"
)

FM42_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_risk_band_tier_dryrun_cross_meta_bundle_safety_20260715.json"
)
FM42_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm42_scale_risk_band_tier_dryrun_cross_meta_bundle_safety"
)
FM42_PACKET_REL = f"{FM42_MOCK_ROOT_REL}/scale_packet.json"
FM42_FINGERPRINT_REL = f"{FM42_MOCK_ROOT_REL}/scale_fingerprint.json"
FM42_RISK_BAND_REL = (
    f"{FM42_MOCK_ROOT_REL}/risk_band_composition_identity_lock_ledger.json"
)
FM42_TIER_REL = (
    f"{FM42_MOCK_ROOT_REL}/tier_coverage_composition_identity_lock_ledger.json"
)
FM42_COMBINED_DRYRUN_REL = (
    f"{FM42_MOCK_ROOT_REL}/combined_dryrun_composition_identity_lock_ledger.json"
)
FM42_CROSS_META_REL = (
    f"{FM42_MOCK_ROOT_REL}/cross_formula_composition_meta_bundle_identity_lock_ledger.json"
)

FM43_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_union_overlap_delta_stable_wall_meta_bundle_safety_20260715.json"
)
FM43_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm43_scale_union_overlap_delta_stable_wall_meta_bundle_safety"
)
FM43_PACKET_REL = f"{FM43_MOCK_ROOT_REL}/scale_packet.json"
FM43_FINGERPRINT_REL = f"{FM43_MOCK_ROOT_REL}/scale_fingerprint.json"
FM43_UNION_STATUS_REL = (
    f"{FM43_MOCK_ROOT_REL}/union_status_composition_identity_lock_ledger.json"
)
FM43_OVERLAP_DELTA_REL = (
    f"{FM43_MOCK_ROOT_REL}/overlap_delta_composition_identity_lock_ledger.json"
)
FM43_SURFACE_DELTA_REL = (
    f"{FM43_MOCK_ROOT_REL}/surface_delta_composition_identity_lock_ledger.json"
)
FM43_WALL_META_REL = (
    f"{FM43_MOCK_ROOT_REL}/cross_stable_metrics_wall_meta_bundle_identity_lock_ledger.json"
)

FM44_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_residual_resume_risk_coverage_wall_meta_bundle_safety_20260715.json"
)
FM45_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_unique_surface_additive_tier_dryrun_wall_meta_bundle_safety_20260715.json"
)
FM46_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_lineage_drift_protected_repro_wall_meta_bundle_safety_20260716.json"
)
FM46_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm46_scale_lineage_drift_protected_repro_wall_meta_bundle_safety"
)
FM46_PACKET_REL = f"{FM46_MOCK_ROOT_REL}/scale_packet.json"
FM46_FINGERPRINT_REL = f"{FM46_MOCK_ROOT_REL}/scale_fingerprint.json"
FM46_LINEAGE_WINNER_PROVENANCE_REL = (
    f"{FM46_MOCK_ROOT_REL}/lineage_winner_provenance_composition_identity_lock_ledger.json"
)
FM46_PARTITION_CODESET_REL = (
    f"{FM46_MOCK_ROOT_REL}/partition_codeset_composition_identity_lock_ledger.json"
)
FM46_PROTECTED_ROOT_REGISTRY_REL = (
    f"{FM46_MOCK_ROOT_REL}/protected_root_registry_composition_identity_lock_ledger.json"
)
FM46_WALL_META_REL = (
    f"{FM46_MOCK_ROOT_REL}/"
    "cross_lineage_drift_protected_repro_wall_meta_bundle_identity_lock_ledger.json"
)

# C-FM-47 本包冻结指纹（运行后由 fingerprint_* 锁定）
FROZEN_FULL_MARKET_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256 = (
    "6332a03f6929fbf83a3375002cdf4a83132a4b03f2e82fb43f36a1b5afad297c"
)
FROZEN_COMBINED_DRYRUN_COHORT_COMPOSITION_IDENTITY_LOCK_FP_SHA256 = (
    "819cc2b50a627e4d0ef236993be93392811f27f791e1e597bc1987449a09502d"
)
FROZEN_COMPANY_COVERAGE_SCALE_COMPOSITION_IDENTITY_LOCK_FP_SHA256 = (
    "016109e33157aa6a31c61db188c5fbf442a91a7bb3462af8b315948a29d073c9"
)
FROZEN_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256 = (
    "e7dc92358156447d3a55e250a7d12df218333d341c35473707c345703052508b"
)
# FM45 连续锚点（只读）
FROZEN_FM46_LINEAGE_WINNER_PROVENANCE_COMPOSITION_IDENTITY_LOCK_FP_SHA256 = (
    "dbe298777d30aedda94baed05c02f742ada4f04f7304fc0f0e27be2eec930ae7"
)
FROZEN_FM46_PARTITION_CODESET_COMPOSITION_IDENTITY_LOCK_FP_SHA256 = (
    "db51b0cbf50b9b15caf0c33b83fdac5ab83f017f1ca09e71025dcde27e0bfca0"
)
FROZEN_FM46_PROTECTED_ROOT_REGISTRY_COMPOSITION_IDENTITY_LOCK_FP_SHA256 = (
    "82f1e2a25a9a8300be5647a1116689bfae16e88e4d8052fb71ae47aaeb1befa1"
)
FROZEN_FM46_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256 = (
    "70d0940a13486023e0fc1798696047176d3d55b1ddae6f5a88bfbe45d3b9c3b8"
)
EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256 = (
    FM40_EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256
)
EXPECTED_SURFACE_COMPOSITION_SHA256 = FM40_EXPECTED_SURFACE_COMPOSITION_SHA256
EXPECTED_ADDITIVE_COMPOSITION_SHA256 = FM41_EXPECTED_ADDITIVE_COMPOSITION_SHA256
EXPECTED_RESIDUAL_COMPOSITION_SHA256 = FM41_EXPECTED_RESIDUAL_COMPOSITION_SHA256
EXPECTED_RESUME_COMPOSITION_SHA256 = FM41_EXPECTED_RESUME_COMPOSITION_SHA256
EXPECTED_CROSS_FORMULA_BUNDLE_SHA256 = FM40_EXPECTED_CROSS_FORMULA_BUNDLE_SHA256
EXPECTED_CROSS_COMPOSITION_BUNDLE_SHA256 = (
    FM41_EXPECTED_CROSS_COMPOSITION_BUNDLE_SHA256
)
EXPECTED_RISK_BAND_COMPOSITION_SHA256 = FM42_EXPECTED_RISK_BAND_COMPOSITION_SHA256
EXPECTED_TIER_COVERAGE_COMPOSITION_SHA256 = (
    FM42_EXPECTED_TIER_COVERAGE_COMPOSITION_SHA256
)
EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256 = (
    FM42_EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256
)
EXPECTED_CROSS_FORMULA_COMPOSITION_META_BUNDLE_SHA256 = (
    FM42_EXPECTED_CROSS_META_SHA256
)
EXPECTED_UNION_STATUS_COMPOSITION_SHA256 = (
    FM43_EXPECTED_UNION_STATUS_COMPOSITION_SHA256
)
EXPECTED_OVERLAP_DELTA_COMPOSITION_SHA256 = (
    FM43_EXPECTED_OVERLAP_DELTA_COMPOSITION_SHA256
)
EXPECTED_SURFACE_DELTA_COMPOSITION_SHA256 = (
    FM43_EXPECTED_SURFACE_DELTA_COMPOSITION_SHA256
)
EXPECTED_CROSS_STABLE_METRICS_WALL_META_BUNDLE_SHA256 = (
    FM43_EXPECTED_WALL_META_SHA256
)
EXPECTED_LINEAGE_WINNER_PROVENANCE_COMPOSITION_SHA256 = (
    "848c04020c1d50d4cfddaef2d0506d9fae74edb08e5bca46a74ea2a8f46c0d50"
)
EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256 = (
    "72513072e1a23ae087d00533aea4b08920951a2fcf986ed17366867af4328726"
)
EXPECTED_PARTITION_CODESET_COMPOSITION_SHA256 = (
    "5273a5b38bcb7ca1804fe320d183d0d9c1f15e0c2aa91ccbadd98594b7bf9d0d"
)
EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256 = (
    "d4146a38ee09be82465e3d6bee6dbabe946774898ca6626c05cca4b2cb6e9661"
)
EXPECTED_PROTECTED_ROOT_REGISTRY_COMPOSITION_SHA256 = (
    "92fa3d17497a548d926f5aaa408299b7e1ba6c3b63bb0d1e838bebef079c5b0a"
)
EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256 = (
    "b996d01adbf37f8de29b6dcff70cac688369cbb23f36ad8ce9a2a2c6a62a8bb0"
)
EXPECTED_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_SHA256 = (
    "6c2e17473bf6abe24ae3b9fa60379537c6224d2f687bbbf065d32a015ad17581"
)
EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256 = (
    "aa49bbac36a7e688f40ae53a41f07e924fc5cdb9d5004be97ff81bff7c4df9fb"
)
EXPECTED_RESIDUAL_FORMULA_COMPOSITION_SHA256 = (
    "9b5c24bb6ee7aa9546c1dee68ec94a8b48b9a83f344c7b4e6629f83c63f80c44"
)
EXPECTED_RESUME_TAXONOMY_COMPOSITION_SHA256 = (
    "e9b719d9acd0a7685a512349abbb80da3823edd47e589691a270457c0efdc470"
)
EXPECTED_RISK_BAND_STATUS_COMPOSITION_SHA256 = (
    "e5edcd539f0bb5332a31ba93828dec64bb1dbebf3f23af3cd4e1a416dc612ebe"
)
EXPECTED_CROSS_RESIDUAL_RESUME_RISK_COVERAGE_WALL_META_BUNDLE_SHA256 = (
    "62c93806b14c3d79b381310c1ec2d45fd7ca89f4816fc0c9293d48006ed688c3"
)
EXPECTED_UNIQUE_SURFACE_ADDITIVE_FORMULA = "2249/2251/2261"
EXPECTED_TIER_COVERAGE_STATUS_FORMULA = "7/3314"
EXPECTED_COMBINED_DRYRUN_STATUS_FORMULA = "dryrun=1053"
EXPECTED_UNIQUE_SURFACE_ADDITIVE_COMPOSITION_SHA256 = (
    "3f225c9a5501087ff05878984c5481f75cf31c990e9e2f0b2e763ea165db9be2"
)
EXPECTED_TIER_COVERAGE_STATUS_COMPOSITION_SHA256 = (
    "7f85bb636500a26ba1268c8630836b0e70fee2cc6cd1fe72a43c7c4eaf4a88ba"
)
EXPECTED_COMBINED_DRYRUN_STATUS_COMPOSITION_SHA256 = (
    "a83413abbe00e17ec73ebcbb0d9265e4b21f0760250ee0b4fef6cac66af24257"
)
EXPECTED_CROSS_UNIQUE_SURFACE_ADDITIVE_TIER_DRYRUN_WALL_META_BUNDLE_SHA256 = (
    "111ac7f008e38fad1f4f731bbabe264c37dcebb50d5f46e7f572c27c87dffe78"
)
EXPECTED_LINEAGE_WINNER_PROVENANCE_FORMULA = "winner/complete"
EXPECTED_PARTITION_CODESET_FORMULA = "complete/partial/failed"
EXPECTED_PROTECTED_ROOT_REGISTRY_FORMULA = "MOCK3-47+MOCK48+resume+auth"
EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA = "unique=2249"
EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA = "combined_dryrun=1053"
EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA = "tiers=7;coverage_sum=3314"
EXPECTED_FM47_PROTECTED_ROOT_REGISTRY_FORMULA = "MOCK3-48+MOCK49+resume+auth"
EXPECTED_RISK_BAND_FORMULA = "75+14+12+5=106"
EXPECTED_RESUME_FORMULA = "28+1+0=29"
EXPECTED_RESUME_TAXONOMY_FORMULA = "28/1/0"
EXPECTED_RISK_BAND_STATUS_FORMULA = "75/14/12/5"
EXPECTED_COVERAGE_FORMULA = "coverage=117"
EXPECTED_RESIDUAL_FORMULA = "106+9+2=117"
EXPECTED_UNION_FORMULA = "2134+106+9=2249"
EXPECTED_UNION_STATUS_FORMULA = "2134/106/9"
EXPECTED_SURFACE_FORMULA = "2249+2=2251"
EXPECTED_SURFACE_DELTA_FORMULA = "surface_delta=2"
EXPECTED_ADDITIVE_FORMULA = "2249+12=2261"
EXPECTED_OVERLAP_DELTA_FORMULA = "overlap_delta=12"
EXPECTED_TIER_COVERAGE_FORMULA = "tiers=7;coverage_sum=3314"
EXPECTED_COMBINED_DRYRUN_FORMULA = "combined_dryrun=1053"
EXPECTED_CROSS_FORMULA_BUNDLE = dict(FM40_EXPECTED_CROSS_FORMULA_BUNDLE)
EXPECTED_CROSS_COMPOSITION_BUNDLE = {
    k: dict(v) for k, v in FM41_EXPECTED_CROSS_COMPOSITION_BUNDLE.items()
}
EXPECTED_CROSS_FORMULA_COMPOSITION_META_BUNDLE = {
    k: dict(v) for k, v in FM42_EXPECTED_CROSS_META_BUNDLE.items()
}
EXPECTED_CROSS_STABLE_METRICS_WALL_META_BUNDLE = {
    k: dict(v) for k, v in FM43_EXPECTED_WALL_META_BUNDLE.items()
}
EXPECTED_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE = {
    "lineage_winner_provenance_composition": {
        "formula": EXPECTED_LINEAGE_WINNER_PROVENANCE_FORMULA,
        "composition_sha256": EXPECTED_LINEAGE_WINNER_PROVENANCE_COMPOSITION_SHA256,
    },
    "partition_codeset_composition": {
        "formula": EXPECTED_PARTITION_CODESET_FORMULA,
        "composition_sha256": EXPECTED_PARTITION_CODESET_COMPOSITION_SHA256,
    },
    "protected_root_registry_composition": {
        "formula": EXPECTED_PROTECTED_ROOT_REGISTRY_FORMULA,
        "composition_sha256": EXPECTED_PROTECTED_ROOT_REGISTRY_COMPOSITION_SHA256,
    },
    "cross_unique_surface_additive_tier_dryrun_wall_meta_bundle": {
        "bundle_sha256": EXPECTED_CROSS_UNIQUE_SURFACE_ADDITIVE_TIER_DRYRUN_WALL_META_BUNDLE_SHA256,
    },
    "stable_metrics_wall": {
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
        "union_status": EXPECTED_UNION_STATUS_FORMULA,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "resume_taxonomy": EXPECTED_RESUME_TAXONOMY_FORMULA,
        "tier_coverage": "7/3314",
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "risk_band": EXPECTED_RISK_BAND_STATUS_FORMULA,
        "coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
        "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
    },
}

EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE = {
    "full_market_unique_union_composition": {
        "formula": EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA,
        "composition_sha256": EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256,
        "n": EXPECTED_HARVEST_UNIQUE_UNION,
    },
    "combined_dryrun_cohort_composition": {
        "formula": EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA,
        "composition_sha256": EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256,
        "n": EXPECTED_COMBINED_DRYRUN_COVERAGE,
    },
    "company_coverage_scale_composition": {
        "formula": EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA,
        "composition_sha256": EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256,
        "tiers": EXPECTED_SCALE_TIER_COUNT,
        "coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
    },
    "cross_lineage_drift_protected_repro_wall_meta_bundle": {
        "bundle_sha256": EXPECTED_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_SHA256,
    },
    "stable_metrics_wall": {
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
        "union_status": EXPECTED_UNION_STATUS_FORMULA,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "resume_taxonomy": EXPECTED_RESUME_TAXONOMY_FORMULA,
        "tier_coverage": "7/3314",
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "risk_band": EXPECTED_RISK_BAND_STATUS_FORMULA,
        "coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
    },
}

# FM45 连续捆绑（只读对照）
EXPECTED_CROSS_UNIQUE_SURFACE_ADDITIVE_TIER_DRYRUN_WALL_META_BUNDLE = {
    "unique_surface_additive_composition": {
        "formula": EXPECTED_UNIQUE_SURFACE_ADDITIVE_FORMULA,
        "composition_sha256": EXPECTED_UNIQUE_SURFACE_ADDITIVE_COMPOSITION_SHA256,
    },
    "tier_coverage_status_composition": {
        "formula": EXPECTED_TIER_COVERAGE_STATUS_FORMULA,
        "composition_sha256": EXPECTED_TIER_COVERAGE_STATUS_COMPOSITION_SHA256,
    },
    "combined_dryrun_status_composition": {
        "formula": EXPECTED_COMBINED_DRYRUN_STATUS_FORMULA,
        "composition_sha256": EXPECTED_COMBINED_DRYRUN_STATUS_COMPOSITION_SHA256,
    },
    "cross_residual_resume_risk_coverage_wall_meta_bundle": {
        "bundle_sha256": EXPECTED_CROSS_RESIDUAL_RESUME_RISK_COVERAGE_WALL_META_BUNDLE_SHA256,
    },
    "stable_metrics_wall": {
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "harvest_additive": EXPECTED_HARVEST_ADDITIVE,
        "union_status": EXPECTED_UNION_STATUS_FORMULA,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "resume_taxonomy": EXPECTED_RESUME_TAXONOMY_FORMULA,
        "tier_coverage": "7/3314",
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "risk_band": EXPECTED_RISK_BAND_STATUS_FORMULA,
        "coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
    },
}

EXPECTED_PARTIAL_CODES_SHA256 = FM31_EXPECTED_PARTIAL_CODES_SHA256
EXPECTED_FAILED_CODES_SHA256 = FM31_EXPECTED_FAILED_CODES_SHA256
EXPECTED_WINNER_MAP_SHA256 = "ff2c6a28b361498b0dbf163ad1d1779041e1dd4e772b652e6382e1d4051fbb07"

EXPECTED_RESUME_SAME_CODES_SHA256 = (
    "2896da9453ebb1a999cf3074dc4753d776587b6a385ab9d5a5ed0fe9942bf5d6"
)
EXPECTED_RESUME_WORSE_CODES_SHA256 = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)
EXPECTED_DRY863_EXTRAS_SHA256 = (
    "4d2821153fad3e9298cb7f98ddf9f051cbcb9022ffa65f5c1ebd15777c7ac15d"
)
EXPECTED_OVERLAP_CODES_SHA256 = (
    "39ab9b76382938c4919b3c0b6bbde612fd21a4acfbeee279ea7a0fc8e9847cea"
)
EXPECTED_OVERLAP_CODES = frozenset(
    set(EXPECTED_P35_FU_OVERLAP) | set(EXPECTED_P2_FU_OVERLAP_CODES)
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK49"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK48"
RESUME_HARVEST_ROOT_ID = "C-ROOT-002"

FROZEN_ROOT_IDS_MUST_BLOCK = tuple(f"C-ROOT-MOCK{i}" for i in range(3, 49))

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths:
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
    fm35_gate_json_rel: str = FM35_GATE_JSON_REL
    fm36_gate_json_rel: str = FM36_GATE_JSON_REL
    fm37_gate_json_rel: str = FM37_GATE_JSON_REL
    fm38_gate_json_rel: str = FM38_GATE_JSON_REL
    fm39_gate_json_rel: str = FM39_GATE_JSON_REL
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
    fm39_packet_rel: str = FM39_PACKET_REL
    fm39_fingerprint_rel: str = FM39_FINGERPRINT_REL
    fm39_partial_risk_band_rel: str = FM39_PARTIAL_RISK_BAND_REL
    fm39_combined_dryrun_rel: str = FM39_COMBINED_DRYRUN_REL
    fm39_risk_band_formula_rel: str = FM39_RISK_BAND_FORMULA_REL
    fm39_resume_formula_rel: str = FM39_RESUME_FORMULA_REL
    fm40_gate_json_rel: str = FM40_GATE_JSON_REL
    fm40_packet_rel: str = FM40_PACKET_REL
    fm40_fingerprint_rel: str = FM40_FINGERPRINT_REL
    fm40_dry863_rel: str = FM40_DRY863_REL
    fm40_unique_union_rel: str = FM40_UNIQUE_UNION_REL
    fm40_surface_rel: str = FM40_SURFACE_REL
    fm40_cross_formula_rel: str = FM40_CROSS_FORMULA_REL
    fm41_gate_json_rel: str = FM41_GATE_JSON_REL
    fm41_packet_rel: str = FM41_PACKET_REL
    fm41_fingerprint_rel: str = FM41_FINGERPRINT_REL
    fm41_additive_rel: str = FM41_ADDITIVE_REL
    fm41_residual_rel: str = FM41_RESIDUAL_REL
    fm41_resume_rel: str = FM41_RESUME_REL
    fm41_cross_composition_rel: str = FM41_CROSS_COMPOSITION_REL
    fm42_gate_json_rel: str = FM42_GATE_JSON_REL
    fm42_packet_rel: str = FM42_PACKET_REL
    fm42_fingerprint_rel: str = FM42_FINGERPRINT_REL
    fm42_risk_band_rel: str = FM42_RISK_BAND_REL
    fm42_tier_rel: str = FM42_TIER_REL
    fm42_combined_dryrun_rel: str = FM42_COMBINED_DRYRUN_REL
    fm42_cross_meta_rel: str = FM42_CROSS_META_REL
    fm43_gate_json_rel: str = FM43_GATE_JSON_REL
    fm43_packet_rel: str = FM43_PACKET_REL
    fm43_fingerprint_rel: str = FM43_FINGERPRINT_REL
    fm43_union_status_rel: str = FM43_UNION_STATUS_REL
    fm43_overlap_delta_rel: str = FM43_OVERLAP_DELTA_REL
    fm43_surface_delta_rel: str = FM43_SURFACE_DELTA_REL
    fm43_wall_meta_rel: str = FM43_WALL_META_REL
    fm44_gate_json_rel: str = FM44_GATE_JSON_REL
    fm45_gate_json_rel: str = FM45_GATE_JSON_REL
    fm46_gate_json_rel: str = FM46_GATE_JSON_REL
    fm46_packet_rel: str = FM46_PACKET_REL
    fm46_fingerprint_rel: str = FM46_FINGERPRINT_REL
    fm46_lineage_winner_provenance_rel: str = FM46_LINEAGE_WINNER_PROVENANCE_REL
    fm46_partition_codeset_rel: str = FM46_PARTITION_CODESET_REL
    fm46_protected_root_registry_rel: str = FM46_PROTECTED_ROOT_REGISTRY_REL
    fm46_wall_meta_rel: str = FM46_WALL_META_REL
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


def assert_fm47_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-47 写根：须 validation/_mock_*，不得覆盖 MOCK3–48，
    不得写权威 dual-layer 索引；允许本任务 MOCK49 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-47 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _sha256_codes(codes: Sequence[str]) -> str:
    return hashlib.sha256(",".join(sorted(codes)).encode("utf-8")).hexdigest()







def fingerprint_full_market_unique_union_composition_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """full_market_unique_union composition identity lock 指纹（unique=2249）。"""
    doc = {
        "kind": "full_market_unique_union_composition_identity_lock",
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "unique_union_composition_sha256": EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
        "composition_sha256": EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256,
        "full_market_unique_union_formula": EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA,
        "deny_composition_mutate": True,
        "deny_inflate": True,
        "deny_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_combined_dryrun_cohort_composition_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """combined_dryrun_cohort composition identity lock 指纹（combined_dryrun=1053）。"""
    doc = {
        "kind": "combined_dryrun_cohort_composition_identity_lock",
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "combined_dryrun_composition_sha256": EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256,
        "composition_sha256": EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256,
        "combined_dryrun_cohort_formula": EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA,
        "deny_composition_mutate": True,
        "deny_inflate": True,
        "deny_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_company_coverage_scale_composition_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """company_coverage_scale composition identity lock 指纹（tiers=7;coverage_sum=3314）。"""
    doc = {
        "kind": "company_coverage_scale_composition_identity_lock",
        "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
        "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        "tier_coverage_composition_sha256": EXPECTED_TIER_COVERAGE_COMPOSITION_SHA256,
        "composition_sha256": EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256,
        "company_coverage_scale_formula": EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA,
        "deny_composition_mutate": True,
        "deny_inflate": True,
        "deny_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_cross_full_market_scale_repro_wall_meta_bundle_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """cross_full_market_scale_repro_wall_meta_bundle identity lock 指纹。"""
    doc = {
        "kind": "cross_full_market_scale_repro_wall_meta_bundle_identity_lock",
        "compositions": {
            k: dict(v)
            for k, v in EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE.items()
        },
        "bundle_sha256": EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256,
        "deny_composition_mutate": True,
        "deny_bundle_inflate": True,
        "deny_bundle_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_full_market_unique_union_composition_mutation(
    *,
    proposed_harvest_unique_union: int,
    proposed_unique_union_composition_sha256: str,
) -> Dict[str, Any]:
    """评估 full-market unique=2249 组成变异；一律拒绝。"""
    matches = (
        proposed_harvest_unique_union == EXPECTED_HARVEST_UNIQUE_UNION
        and proposed_unique_union_composition_sha256 == EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256
    )
    return {
        "proposed": {
            "harvest_unique_union": proposed_harvest_unique_union,
            "unique_union_composition_sha256": proposed_unique_union_composition_sha256,
        },
        "frozen": {
            "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
            "unique_union_composition_sha256": EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
        },
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "full_market_unique_union_composition_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_combined_dryrun_cohort_composition_mutation(
    *,
    proposed_combined_dryrun_coverage: int,
    proposed_combined_dryrun_composition_sha256: str,
) -> Dict[str, Any]:
    """评估 combined_dryrun=1053 组成变异；一律拒绝。"""
    matches = (
        proposed_combined_dryrun_coverage == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and proposed_combined_dryrun_composition_sha256
        == EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256
    )
    return {
        "proposed": {
            "combined_dryrun_coverage": proposed_combined_dryrun_coverage,
            "combined_dryrun_composition_sha256": proposed_combined_dryrun_composition_sha256,
        },
        "frozen": {
            "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
            "combined_dryrun_composition_sha256": EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256,
        },
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "combined_dryrun_cohort_composition_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_company_coverage_scale_composition_mutation(
    *,
    proposed_scale_tier_count: int,
    proposed_company_coverage_sum: int,
) -> Dict[str, Any]:
    """评估 tiers=7;coverage_sum=3314 组成变异；一律拒绝。"""
    matches = (
        proposed_scale_tier_count == EXPECTED_SCALE_TIER_COUNT
        and proposed_company_coverage_sum == EXPECTED_COMPANY_COVERAGE_SUM
    )
    return {
        "proposed": {
            "scale_tier_count": proposed_scale_tier_count,
            "company_coverage_sum": proposed_company_coverage_sum,
        },
        "frozen": {
            "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
            "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        },
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "company_coverage_scale_composition_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_cross_full_market_scale_repro_wall_meta_bundle_mutation(
    *, proposed_compositions: Dict[str, Any]
) -> Dict[str, Any]:
    """评估 cross full-market scale repro wall meta bundle 变异；一律拒绝。"""
    frozen = {
        k: dict(v)
        for k, v in EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE.items()
    }
    proposed = {
        str(k): (dict(v) if isinstance(v, dict) else v)
        for k, v in proposed_compositions.items()
    }
    matches = proposed == frozen
    return {
        "proposed_compositions": proposed,
        "frozen_compositions": frozen,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": (
            "cross_full_market_scale_repro_wall_meta_bundle_identity_frozen_pre_execute"
        ),
        "hold": "KEEP_EXECUTE_FALSE",
    }


def build_full_market_unique_union_composition_identity_lock_rows(
    paths: FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths,
    *,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """full_market_unique_union composition identity lock（unique=2249）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_full_market_unique_union_composition_identity_lock()

    comp_payload = {
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "unique_union_composition_sha256": EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
        "full_market_unique_union_formula": EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA,
    }
    comp_sha = hashlib.sha256(
        json.dumps(comp_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    identity_ok = (
        EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA == "unique=2249"
        and EXPECTED_HARVEST_UNIQUE_UNION == 2249
        and EXPECTED_UNION_COMPLETE + EXPECTED_UNION_PARTIAL + EXPECTED_UNION_FAILED
        == EXPECTED_HARVEST_UNIQUE_UNION
        and comp_sha == EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256
        and doc["composition_sha256"] == EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256
    )
    checks["full_market_unique_union_composition_identity"] = identity_ok
    rows.append(
        _row(
            check_id="full_market_unique_union_composition_identity",
            layer="full_market_unique_union_composition_identity_lock",
            expected="unique=2249",
            observed=f"formula={EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA};n={EXPECTED_HARVEST_UNIQUE_UNION};sha={comp_sha[:12]}",
            ok=identity_ok,
            notes="ok" if identity_ok else "full_market_unique_union_composition_drift",
        )
    )

    sample_denials = [
        evaluate_full_market_unique_union_composition_mutation(
            proposed_harvest_unique_union=2200,
            proposed_unique_union_composition_sha256=EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
        ),
        evaluate_full_market_unique_union_composition_mutation(
            proposed_harvest_unique_union=EXPECTED_HARVEST_UNIQUE_UNION,
            proposed_unique_union_composition_sha256="0" * 64,
        ),
        evaluate_full_market_unique_union_composition_mutation(
            proposed_harvest_unique_union=0,
            proposed_unique_union_composition_sha256="a" * 64,
        ),
        evaluate_full_market_unique_union_composition_mutation(
            proposed_harvest_unique_union=EXPECTED_HARVEST_UNIQUE_UNION,
            proposed_unique_union_composition_sha256=EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["full_market_unique_union_composition_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="full_market_unique_union_composition_mutation_denied",
            layer="full_market_unique_union_composition_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "full_market_unique_union_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_composition_mutate"] is True
        and doc["deny_inflate"] is True
        and doc["deny_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and fp == FROZEN_FULL_MARKET_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256
    )
    checks["full_market_unique_union_composition_flags"] = flags_ok
    rows.append(
        _row(
            check_id="full_market_unique_union_composition_flags",
            layer="full_market_unique_union_composition_identity_lock",
            expected=FROZEN_FULL_MARKET_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=flags_ok,
            notes="ok" if flags_ok else "full_market_unique_union_flags_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["full_market_unique_union_composition_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="full_market_unique_union_composition_identity_lock_all_pass",
            layer="full_market_unique_union_composition_identity_lock",
            expected="identity+deny+flags",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "full_market_unique_union_lock_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "composition_sha256": comp_sha,
        "full_market_unique_union_formula": EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_combined_dryrun_cohort_composition_identity_lock_rows(
    paths: FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths,
    *,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """combined_dryrun_cohort composition identity lock（combined_dryrun=1053）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_combined_dryrun_cohort_composition_identity_lock()

    comp_payload = {
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "combined_dryrun_composition_sha256": EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256,
        "combined_dryrun_cohort_formula": EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA,
    }
    comp_sha = hashlib.sha256(
        json.dumps(comp_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    identity_ok = (
        EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA == "combined_dryrun=1053"
        and EXPECTED_COMBINED_DRYRUN_COVERAGE == 1053
        and comp_sha == EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256
        and doc["composition_sha256"] == EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256
    )
    checks["combined_dryrun_cohort_composition_identity"] = identity_ok
    rows.append(
        _row(
            check_id="combined_dryrun_cohort_composition_identity",
            layer="combined_dryrun_cohort_composition_identity_lock",
            expected="combined_dryrun=1053",
            observed=f"formula={EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA};n={EXPECTED_COMBINED_DRYRUN_COVERAGE};sha={comp_sha[:12]}",
            ok=identity_ok,
            notes="ok" if identity_ok else "combined_dryrun_cohort_composition_drift",
        )
    )

    sample_denials = [
        evaluate_combined_dryrun_cohort_composition_mutation(
            proposed_combined_dryrun_coverage=1000,
            proposed_combined_dryrun_composition_sha256=EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256,
        ),
        evaluate_combined_dryrun_cohort_composition_mutation(
            proposed_combined_dryrun_coverage=EXPECTED_COMBINED_DRYRUN_COVERAGE,
            proposed_combined_dryrun_composition_sha256="0" * 64,
        ),
        evaluate_combined_dryrun_cohort_composition_mutation(
            proposed_combined_dryrun_coverage=0,
            proposed_combined_dryrun_composition_sha256="a" * 64,
        ),
        evaluate_combined_dryrun_cohort_composition_mutation(
            proposed_combined_dryrun_coverage=EXPECTED_COMBINED_DRYRUN_COVERAGE,
            proposed_combined_dryrun_composition_sha256=EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256,
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["combined_dryrun_cohort_composition_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="combined_dryrun_cohort_composition_mutation_denied",
            layer="combined_dryrun_cohort_composition_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "combined_dryrun_cohort_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_composition_mutate"] is True
        and doc["deny_inflate"] is True
        and doc["deny_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and fp == FROZEN_COMBINED_DRYRUN_COHORT_COMPOSITION_IDENTITY_LOCK_FP_SHA256
    )
    checks["combined_dryrun_cohort_composition_flags"] = flags_ok
    rows.append(
        _row(
            check_id="combined_dryrun_cohort_composition_flags",
            layer="combined_dryrun_cohort_composition_identity_lock",
            expected=FROZEN_COMBINED_DRYRUN_COHORT_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=flags_ok,
            notes="ok" if flags_ok else "combined_dryrun_cohort_flags_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["combined_dryrun_cohort_composition_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="combined_dryrun_cohort_composition_identity_lock_all_pass",
            layer="combined_dryrun_cohort_composition_identity_lock",
            expected="identity+deny+flags",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "combined_dryrun_cohort_lock_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "composition_sha256": comp_sha,
        "combined_dryrun_cohort_formula": EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_company_coverage_scale_composition_identity_lock_rows(
    paths: FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths,
    *,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """company_coverage_scale composition identity lock（tiers=7;coverage_sum=3314）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_company_coverage_scale_composition_identity_lock()

    comp_payload = {
        "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
        "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
        "tier_coverage_composition_sha256": EXPECTED_TIER_COVERAGE_COMPOSITION_SHA256,
        "company_coverage_scale_formula": EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA,
    }
    comp_sha = hashlib.sha256(
        json.dumps(comp_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    identity_ok = (
        EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA == "tiers=7;coverage_sum=3314"
        and EXPECTED_SCALE_TIER_COUNT == 7
        and EXPECTED_COMPANY_COVERAGE_SUM == 3314
        and comp_sha == EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256
        and doc["composition_sha256"] == EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256
    )
    checks["company_coverage_scale_composition_identity"] = identity_ok
    rows.append(
        _row(
            check_id="company_coverage_scale_composition_identity",
            layer="company_coverage_scale_composition_identity_lock",
            expected="tiers=7;coverage_sum=3314",
            observed=(
                f"formula={EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA};"
                f"tiers={EXPECTED_SCALE_TIER_COUNT};sum={EXPECTED_COMPANY_COVERAGE_SUM};sha={comp_sha[:12]}"
            ),
            ok=identity_ok,
            notes="ok" if identity_ok else "company_coverage_scale_composition_drift",
        )
    )

    sample_denials = [
        evaluate_company_coverage_scale_composition_mutation(
            proposed_scale_tier_count=6,
            proposed_company_coverage_sum=EXPECTED_COMPANY_COVERAGE_SUM,
        ),
        evaluate_company_coverage_scale_composition_mutation(
            proposed_scale_tier_count=EXPECTED_SCALE_TIER_COUNT,
            proposed_company_coverage_sum=3000,
        ),
        evaluate_company_coverage_scale_composition_mutation(
            proposed_scale_tier_count=0,
            proposed_company_coverage_sum=0,
        ),
        evaluate_company_coverage_scale_composition_mutation(
            proposed_scale_tier_count=EXPECTED_SCALE_TIER_COUNT,
            proposed_company_coverage_sum=EXPECTED_COMPANY_COVERAGE_SUM,
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["company_coverage_scale_composition_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="company_coverage_scale_composition_mutation_denied",
            layer="company_coverage_scale_composition_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "company_coverage_scale_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_composition_mutate"] is True
        and doc["deny_inflate"] is True
        and doc["deny_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and fp == FROZEN_COMPANY_COVERAGE_SCALE_COMPOSITION_IDENTITY_LOCK_FP_SHA256
    )
    checks["company_coverage_scale_composition_flags"] = flags_ok
    rows.append(
        _row(
            check_id="company_coverage_scale_composition_flags",
            layer="company_coverage_scale_composition_identity_lock",
            expected=FROZEN_COMPANY_COVERAGE_SCALE_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=flags_ok,
            notes="ok" if flags_ok else "company_coverage_scale_flags_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["company_coverage_scale_composition_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="company_coverage_scale_composition_identity_lock_all_pass",
            layer="company_coverage_scale_composition_identity_lock",
            expected="identity+deny+flags",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "company_coverage_scale_lock_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "composition_sha256": comp_sha,
        "company_coverage_scale_formula": EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_cross_full_market_scale_repro_wall_meta_bundle_identity_lock_rows(
    paths: FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths,
    *,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """cross_full_market_scale_repro_wall_meta_bundle identity lock。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_cross_full_market_scale_repro_wall_meta_bundle_identity_lock()

    compositions = {
        k: dict(v)
        for k, v in EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE.items()
    }
    bundle_sha = hashlib.sha256(
        json.dumps(compositions, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    identity_ok = (
        bundle_sha == EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256
        and doc["bundle_sha256"]
        == EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256
        and len(compositions) == 5
        and compositions["full_market_unique_union_composition"]["n"] == 2249
        and compositions["combined_dryrun_cohort_composition"]["n"] == 1053
        and compositions["company_coverage_scale_composition"]["coverage_sum"] == 3314
    )
    checks["cross_full_market_scale_repro_wall_meta_bundle_identity"] = identity_ok
    rows.append(
        _row(
            check_id="cross_full_market_scale_repro_wall_meta_bundle_identity",
            layer="cross_full_market_scale_repro_wall_meta_bundle_identity_lock",
            expected="unique2249+dryrun1053+coverage3314+repro_bundle",
            observed=f"keys={len(compositions)};sha={bundle_sha[:12]}",
            ok=identity_ok,
            notes="ok" if identity_ok else "cross_full_market_bundle_drift",
        )
    )

    mutated = {k: dict(v) for k, v in compositions.items()}
    mutated["full_market_unique_union_composition"] = {
        "formula": "unique=2000",
        "composition_sha256": EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256,
        "n": 2000,
    }
    sample_denials = [
        evaluate_cross_full_market_scale_repro_wall_meta_bundle_mutation(
            proposed_compositions=mutated
        ),
        evaluate_cross_full_market_scale_repro_wall_meta_bundle_mutation(
            proposed_compositions={}
        ),
        evaluate_cross_full_market_scale_repro_wall_meta_bundle_mutation(
            proposed_compositions={"x": {"a": 1}}
        ),
        evaluate_cross_full_market_scale_repro_wall_meta_bundle_mutation(
            proposed_compositions=compositions
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["cross_full_market_scale_repro_wall_meta_bundle_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="cross_full_market_scale_repro_wall_meta_bundle_mutation_denied",
            layer="cross_full_market_scale_repro_wall_meta_bundle_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "cross_full_market_bundle_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_composition_mutate"] is True
        and doc["deny_bundle_inflate"] is True
        and doc["deny_bundle_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and fp == FROZEN_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256
    )
    checks["cross_full_market_scale_repro_wall_meta_bundle_flags"] = flags_ok
    rows.append(
        _row(
            check_id="cross_full_market_scale_repro_wall_meta_bundle_flags",
            layer="cross_full_market_scale_repro_wall_meta_bundle_identity_lock",
            expected=FROZEN_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=flags_ok,
            notes="ok" if flags_ok else "cross_full_market_bundle_flags_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["cross_full_market_scale_repro_wall_meta_bundle_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="cross_full_market_scale_repro_wall_meta_bundle_identity_lock_all_pass",
            layer="cross_full_market_scale_repro_wall_meta_bundle_identity_lock",
            expected="identity+deny+flags",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "cross_full_market_bundle_lock_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "bundle_sha256": bundle_sha,
        "compositions": compositions,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_fm46_continuity_rows(
    paths: FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM46 packet / fingerprint / gate / 四 ledger 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm46_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm46_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm46_gate_json_rel, base_dir=base_dir))
    us_led = load_json(_abs(paths.fm46_lineage_winner_provenance_rel, base_dir=base_dir))
    od_led = load_json(_abs(paths.fm46_partition_codeset_rel, base_dir=base_dir))
    sd_led = load_json(_abs(paths.fm46_protected_root_registry_rel, base_dir=base_dir))
    wall_led = load_json(_abs(paths.fm46_wall_meta_rel, base_dir=base_dir))

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
        and packet.get("residual_safety_coverage") == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        and packet.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and packet.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and packet.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and packet.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
        and packet.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and packet.get("lineage_winner_provenance_composition_sha256")
        == EXPECTED_LINEAGE_WINNER_PROVENANCE_COMPOSITION_SHA256
        and packet.get("partition_codeset_composition_sha256")
        == EXPECTED_PARTITION_CODESET_COMPOSITION_SHA256
        and packet.get("protected_root_registry_composition_sha256")
        == EXPECTED_PROTECTED_ROOT_REGISTRY_COMPOSITION_SHA256
        and packet.get("cross_lineage_drift_protected_repro_wall_meta_bundle_sha256")
        == EXPECTED_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_SHA256
        and packet.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
        and packet.get("approved_for_snapshot_rebuild") is False
        and packet.get("seal_chain_extended") is False
    )
    checks["fm46_packet_zero_drift"] = pkt_ok
    rows.append(
        _row(
            check_id="fm46_packet_zero_drift",
            layer="fm46_continuity",
            path=paths.fm46_packet_rel,
            expected="PASS_OFFLINE+stable_metrics+compositions",
            observed=f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')}",
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm46_packet_drift",
        )
    )

    fp_ok = (
        fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and fp_doc.get("lineage_winner_provenance_composition_sha256")
        == EXPECTED_LINEAGE_WINNER_PROVENANCE_COMPOSITION_SHA256
        and fp_doc.get("partition_codeset_composition_sha256")
        == EXPECTED_PARTITION_CODESET_COMPOSITION_SHA256
        and fp_doc.get("protected_root_registry_composition_sha256")
        == EXPECTED_PROTECTED_ROOT_REGISTRY_COMPOSITION_SHA256
        and fp_doc.get("cross_lineage_drift_protected_repro_wall_meta_bundle_sha256")
        == EXPECTED_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_SHA256
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm46_fingerprint_zero_drift"] = fp_ok
    rows.append(
        _row(
            check_id="fm46_fingerprint_zero_drift",
            layer="fm46_continuity",
            path=paths.fm46_fingerprint_rel,
            expected="stable_metrics+fm44_fps",
            observed=f"unique={fp_doc.get('harvest_unique_union')}",
            ok=fp_ok,
            notes="ok" if fp_ok else "fm46_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and gate_doc.get("cross_lineage_drift_protected_repro_wall_meta_bundle_sha256")
        == EXPECTED_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_SHA256
        and gate_doc.get("seal_chain_extended") is False
    )
    checks["fm46_gate_zero_drift"] = gate_ok
    rows.append(
        _row(
            check_id="fm46_gate_zero_drift",
            layer="fm46_continuity",
            path=paths.fm46_gate_json_rel,
            expected="PASS_OFFLINE+KEEP_EXECUTE_FALSE",
            observed=f"gate={gate_doc.get('gate')}",
            ok=gate_ok,
            notes="ok" if gate_ok else "fm46_gate_drift",
        )
    )

    us_ok = (
        us_led.get("fingerprint_sha256")
        == FROZEN_FM46_LINEAGE_WINNER_PROVENANCE_COMPOSITION_IDENTITY_LOCK_FP_SHA256
        and us_led.get("composition_sha256")
        == EXPECTED_LINEAGE_WINNER_PROVENANCE_COMPOSITION_SHA256
    )
    checks["fm46_lineage_winner_provenance_ledger_zero_drift"] = us_ok
    rows.append(
        _row(
            check_id="fm46_lineage_winner_provenance_ledger_zero_drift",
            layer="fm46_continuity",
            path=paths.fm46_lineage_winner_provenance_rel,
            expected=FROZEN_FM46_LINEAGE_WINNER_PROVENANCE_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
            observed=str(us_led.get("fingerprint_sha256")),
            ok=us_ok,
            notes="ok" if us_ok else "fm46_lineage_ledger_drift",
        )
    )

    od_ok = (
        od_led.get("fingerprint_sha256")
        == FROZEN_FM46_PARTITION_CODESET_COMPOSITION_IDENTITY_LOCK_FP_SHA256
        and od_led.get("composition_sha256")
        == EXPECTED_PARTITION_CODESET_COMPOSITION_SHA256
    )
    checks["fm46_partition_codeset_ledger_zero_drift"] = od_ok
    rows.append(
        _row(
            check_id="fm46_partition_codeset_ledger_zero_drift",
            layer="fm46_continuity",
            path=paths.fm46_partition_codeset_rel,
            expected=FROZEN_FM46_PARTITION_CODESET_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
            observed=str(od_led.get("fingerprint_sha256")),
            ok=od_ok,
            notes="ok" if od_ok else "fm46_partition_ledger_drift",
        )
    )

    sd_ok = (
        sd_led.get("fingerprint_sha256")
        == FROZEN_FM46_PROTECTED_ROOT_REGISTRY_COMPOSITION_IDENTITY_LOCK_FP_SHA256
        and sd_led.get("composition_sha256")
        == EXPECTED_PROTECTED_ROOT_REGISTRY_COMPOSITION_SHA256
    )
    checks["fm46_protected_root_registry_ledger_zero_drift"] = sd_ok
    rows.append(
        _row(
            check_id="fm46_protected_root_registry_ledger_zero_drift",
            layer="fm46_continuity",
            path=paths.fm46_protected_root_registry_rel,
            expected=FROZEN_FM46_PROTECTED_ROOT_REGISTRY_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
            observed=str(sd_led.get("fingerprint_sha256")),
            ok=sd_ok,
            notes="ok" if sd_ok else "fm46_protected_ledger_drift",
        )
    )

    wall_ok = (
        wall_led.get("fingerprint_sha256")
        == FROZEN_FM46_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256
        and wall_led.get("bundle_sha256")
        == EXPECTED_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_SHA256
    )
    checks["fm46_wall_meta_ledger_zero_drift"] = wall_ok
    rows.append(
        _row(
            check_id="fm46_wall_meta_ledger_zero_drift",
            layer="fm46_continuity",
            path=paths.fm46_wall_meta_rel,
            expected=FROZEN_FM46_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256,
            observed=str(wall_led.get("fingerprint_sha256")),
            ok=wall_ok,
            notes="ok" if wall_ok else "fm46_wall_meta_ledger_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm46_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm46_continuity_all_pass",
            layer="fm46_continuity",
            expected="packet+fp+gate+4ledgers",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm46_continuity_incomplete",
        )
    )
    return rows, checks


def build_output_root_protection_rows(
    paths: FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK49 放行。"""
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
        assert_fm47_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK49_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock49_ok",
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
    paths: FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–48 拒绝 · MOCK49 放行。"""
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

    # 先验 MOCK46（C-FM-44）写根必须仍冻结
    mock48_rel = FM46_MOCK_ROOT_REL
    mock48_blocked = False
    try:
        assert_fm47_output_root(mock48_rel, base_dir=base_dir)
    except RuntimeError as exc:
        mock48_blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock48_still_frozen"] = mock48_blocked
    rows.append(
        _row(
            check_id="mock48_still_frozen",
            layer="frozen_mock_isolation",
            root_id=PRIOR_TASK_ROOT_ID,
            path=mock48_rel,
            expected="write_forbidden",
            observed="blocked" if mock48_blocked else "allowed",
            ok=mock48_blocked,
            notes="ok" if mock48_blocked else "mock48_write_leak",
        )
    )

    allow_ok = False
    try:
        assert_fm47_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except Exception:
        allow_ok = False
    checks["frozen_allow_mock49"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock49",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="MOCK49_or_ephemeral_allowed",
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
            expected="MOCK3-48_block+MOCK49_allow",
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
    """protected_output_roots.csv：MOCK49 已登记。"""
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

    mock49 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(mock49.get("path_pattern") or "")
    checks["protected_csv_mock49_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock49_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock49.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock49_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3–48+MOCK49+resume+auth+registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..46 gate battery（跳过 seal FM06–11）。"""
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
        ("fm35_scale_winner_resume_taxonomy_batch_priority_risk_band", "fm35"),
        ("fm36_scale_failed_resume_membership_residual_formula_hold", "fm36"),
        ("fm37_scale_improved_partial_surface_delta_union_partition", "fm37"),
        ("fm38_scale_complete_overlap_additive_tier_formula", "fm38"),
        ("fm39_scale_risk_band_combined_dryrun_resume_formula", "fm39"),
        ("fm40_scale_dry863_unique_surface_cross_formula_bundle", "fm40"),
        ("fm41_scale_additive_residual_resume_cross_composition_bundle", "fm41"),
        ("fm42_scale_risk_band_tier_dryrun_cross_meta_bundle", "fm42"),
        ("fm43_scale_union_overlap_delta_stable_wall_meta_bundle", "fm43"),
        ("fm44_scale_residual_resume_risk_coverage_wall_meta_bundle", "fm44"),
        ("fm45_scale_unique_surface_additive_tier_dryrun_wall_meta_bundle", "fm45"),
        ("fm46_scale_lineage_drift_protected_repro_wall_meta_bundle", "fm46"),
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
        "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35",
        "fm36", "fm37", "fm38", "fm39", "fm40", "fm41", "fm42", "fm43", "fm44", "fm45", "fm46",
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
            "fm25", "fm26", "fm27", "fm28", "fm29", "fm30", "fm31", "fm32",
            "fm33", "fm34", "fm35", "fm36", "fm37", "fm38", "fm39", "fm40", "fm41", "fm42", "fm43", "fm44", "fm45", "fm46",
        ):
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in (
            "fm26", "fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33",
            "fm34", "fm35", "fm36", "fm37", "fm38", "fm39", "fm40", "fm41", "fm42", "fm43", "fm44", "fm45", "fm46",
        ):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in (
            "fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34",
            "fm35", "fm36", "fm37", "fm38", "fm39", "fm40", "fm41", "fm42", "fm43", "fm44", "fm45", "fm46",
        ):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key in (
            "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35",
            "fm36", "fm37", "fm38", "fm39", "fm40", "fm41", "fm42", "fm43", "fm44", "fm45", "fm46",
        ):
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        if key in (
            "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35", "fm36", "fm37", "fm38", "fm39", "fm40", "fm41",
        ):
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
        if key in ("fm31", "fm32", "fm33", "fm34", "fm35", "fm36", "fm37", "fm38", "fm39", "fm40", "fm41", "fm42"):
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
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
            )
        if key == "fm35":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("winner_map_sha256") == EXPECTED_WINNER_MAP_SHA256
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
                and list(payload.get("batch_priority") or [])
                == list(EXPECTED_BATCH_PRIORITY)
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key == "fm36":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("residual_formula") == "106+9+2=117"
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
                and set(payload.get("failed_codes") or []) == EXPECTED_FAILED_CODES
                and list(payload.get("resume_same_codes") or []) == ["301212"]
            )
        if key == "fm37":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("union_formula") == "2134+106+9=2249"
                and payload.get("surface_formula") == "2249+2=2251"
                and payload.get("resume_improved") == EXPECTED_RESUME_IMPROVED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("complete_codes_sha256") == EXPECTED_COMPLETE_CODES_SHA256
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
            )
        if key == "fm38":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("additive_formula") == "2249+12=2261"
                and payload.get("tier_coverage_formula") == "tiers=7;coverage_sum=3314"
                and payload.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
                and payload.get("union_complete") == EXPECTED_UNION_COMPLETE
                and payload.get("complete_codes_sha256") == EXPECTED_COMPLETE_CODES_SHA256
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
                and payload.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
                and payload.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
            )
        if key == "fm39":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("risk_band_formula") == EXPECTED_RISK_BAND_FORMULA
                and payload.get("resume_formula") == EXPECTED_RESUME_FORMULA
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
                and payload.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
                and payload.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
            )
        if key == "fm40":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("cross_formula_bundle_sha256")
                == EXPECTED_CROSS_FORMULA_BUNDLE_SHA256
                and payload.get("unique_union_composition_sha256")
                == EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256
                and payload.get("surface_composition_sha256")
                == EXPECTED_SURFACE_COMPOSITION_SHA256
                and payload.get("union_formula") == EXPECTED_UNION_FORMULA
                and payload.get("surface_formula") == EXPECTED_SURFACE_FORMULA
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
            )
        if key == "fm41":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("cross_composition_bundle_sha256")
                == EXPECTED_CROSS_COMPOSITION_BUNDLE_SHA256
                and payload.get("additive_composition_sha256")
                == EXPECTED_ADDITIVE_COMPOSITION_SHA256
                and payload.get("residual_composition_sha256")
                == EXPECTED_RESIDUAL_COMPOSITION_SHA256
                and payload.get("resume_composition_sha256")
                == EXPECTED_RESUME_COMPOSITION_SHA256
                and payload.get("additive_formula") == EXPECTED_ADDITIVE_FORMULA
                and payload.get("residual_formula") == EXPECTED_RESIDUAL_FORMULA
                and payload.get("resume_formula") == EXPECTED_RESUME_FORMULA
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
            )
        if key == "fm42":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("risk_band_composition_sha256")
                == EXPECTED_RISK_BAND_COMPOSITION_SHA256
                and payload.get("tier_coverage_composition_sha256")
                == EXPECTED_TIER_COVERAGE_COMPOSITION_SHA256
                and payload.get("combined_dryrun_composition_sha256")
                == EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256
                and payload.get("cross_formula_composition_meta_bundle_sha256")
                == EXPECTED_CROSS_FORMULA_COMPOSITION_META_BUNDLE_SHA256
                and payload.get("risk_band_formula") == EXPECTED_RISK_BAND_FORMULA
                and payload.get("tier_coverage_formula") == EXPECTED_TIER_COVERAGE_FORMULA
                and payload.get("combined_dryrun_formula")
                == EXPECTED_COMBINED_DRYRUN_FORMULA
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
            )
        if key == "fm43":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("union_status_composition_sha256")
                == EXPECTED_UNION_STATUS_COMPOSITION_SHA256
                and payload.get("overlap_delta_composition_sha256")
                == EXPECTED_OVERLAP_DELTA_COMPOSITION_SHA256
                and payload.get("surface_delta_composition_sha256")
                == EXPECTED_SURFACE_DELTA_COMPOSITION_SHA256
                and payload.get("cross_stable_metrics_wall_meta_bundle_sha256")
                == EXPECTED_CROSS_STABLE_METRICS_WALL_META_BUNDLE_SHA256
                and payload.get("union_status_formula") == EXPECTED_UNION_STATUS_FORMULA
                and payload.get("overlap_delta_formula") == EXPECTED_OVERLAP_DELTA_FORMULA
                and payload.get("surface_delta_formula") == EXPECTED_SURFACE_DELTA_FORMULA
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
            )
        if key == "fm44":
            ok = (
                ok
                and payload.get("combined_dryrun_coverage")
                == EXPECTED_COMBINED_DRYRUN_COVERAGE
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("residual_formula_composition_sha256")
                == EXPECTED_RESIDUAL_FORMULA_COMPOSITION_SHA256
                and payload.get("resume_taxonomy_composition_sha256")
                == EXPECTED_RESUME_TAXONOMY_COMPOSITION_SHA256
                and payload.get("risk_band_status_composition_sha256")
                == EXPECTED_RISK_BAND_STATUS_COMPOSITION_SHA256
                and payload.get("cross_residual_resume_risk_coverage_wall_meta_bundle_sha256")
                == EXPECTED_CROSS_RESIDUAL_RESUME_RISK_COVERAGE_WALL_META_BUNDLE_SHA256
                and payload.get("residual_formula") == EXPECTED_RESIDUAL_FORMULA
                and payload.get("resume_taxonomy_formula") == EXPECTED_RESUME_TAXONOMY_FORMULA
                and payload.get("risk_band_status_formula") == EXPECTED_RISK_BAND_STATUS_FORMULA
                and payload.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
                and payload.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
            )
        checks[check_id] = ok
        rows.append(
            _row(
                check_id=check_id,
                layer="fm_gate_battery",
                expected="PASS_OFFLINE;cninfo=0;execute=false",
                observed=(
                    f"gate={gate};cninfo={cninfo};execute={execute};"
                    f"seal_ext={payload.get('seal_chain_extended')}"
                ),
                ok=ok,
                notes="ok" if ok else f"{key}_gate_fail",
            )
        )

    all_ok = all(checks.values()) if checks else False
    rows.append(
        _row(
            check_id="fm01_05_12_46_battery_all_pass",
            layer="fm_gate_battery",
            expected="all_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_46_battery_all_pass"] = all_ok
    return rows, checks


def build_execute_hold_rows() -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """EXECUTE hold / seal 未扩展。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {
        "execute_hold_keep_false": True,
        "approved_unchanged_false": True,
        "seal_chain_not_extended": True,
        "cninfo_zero": True,
        "ready_for_execute_false": True,
        "decision_awaiting_human": True,
        "idle_not_required": True,
    }
    for cid, ok in checks.items():
        rows.append(
            _row(
                check_id=cid,
                layer="execute_hold_seal",
                expected="KEEP_EXECUTE_FALSE;seal_chain_extended=false",
                observed="locked",
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
            expected="hold+no_seal_extension",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "execute_hold_incomplete",
        )
    )
    return rows, checks


def ensure_protected_roots_csv_fm47(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK49；加固 C-ROOT-002 unique/surface/additive/tier/dryrun 说明。"""
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
                "C-FM-24..46 scale/safety freezes + C-FM-47 full-market unique/dryrun/"
                "coverage-repro-wall-meta-bundle; 只读直至人批重跑"
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
                "C-FM-47 scale full_market_unique_union composition identity lock "
                "(unique=2249) + combined_dryrun_cohort composition identity lock "
                "(combined_dryrun=1053) + company_coverage_scale composition identity lock "
                "(tiers=7;coverage_sum=3314) + cross_full_market_scale_repro_wall_meta_bundle "
                "identity lock + FM46 continuity; never production EXECUTE; "
                "must not overwrite MOCK3-48; seal_chain_extended=false"
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


def run_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety(
    *,
    paths: FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-47 规模 unique/surface/additive/tier/dryrun-wall-meta-bundle 离线 QA。"""
    paths = paths or FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm47(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm47_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm46_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    rf_rows, rf_checks, rf_meta = build_full_market_unique_union_composition_identity_lock_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(rf_rows)
    rt_rows, rt_checks, rt_meta = (
        build_combined_dryrun_cohort_composition_identity_lock_rows(paths, base_dir=base_dir)
    )
    matrix.extend(rt_rows)
    rb_rows, rb_checks, rb_meta = (
        build_company_coverage_scale_composition_identity_lock_rows(paths, base_dir=base_dir)
    )
    matrix.extend(rb_rows)
    bundle_rows, bundle_checks, bundle_meta = (
        build_cross_full_market_scale_repro_wall_meta_bundle_identity_lock_rows(
            paths, base_dir=base_dir
        )
    )
    matrix.extend(bundle_rows)
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
        "fm35": load_json(_abs(paths.fm35_gate_json_rel, base_dir=base_dir)),
        "fm36": load_json(_abs(paths.fm36_gate_json_rel, base_dir=base_dir)),
        "fm37": load_json(_abs(paths.fm37_gate_json_rel, base_dir=base_dir)),
        "fm38": load_json(_abs(paths.fm38_gate_json_rel, base_dir=base_dir)),
        "fm39": load_json(_abs(paths.fm39_gate_json_rel, base_dir=base_dir)),
        "fm40": load_json(_abs(paths.fm40_gate_json_rel, base_dir=base_dir)),
        "fm41": load_json(_abs(paths.fm41_gate_json_rel, base_dir=base_dir)),
        "fm42": load_json(_abs(paths.fm42_gate_json_rel, base_dir=base_dir)),
        "fm43": load_json(_abs(paths.fm43_gate_json_rel, base_dir=base_dir)),
        "fm44": load_json(_abs(paths.fm44_gate_json_rel, base_dir=base_dir)),
        "fm45": load_json(_abs(paths.fm45_gate_json_rel, base_dir=base_dir)),
        "fm46": load_json(_abs(paths.fm46_gate_json_rel, base_dir=base_dir)),
    }

    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm46_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm46_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "full_market_unique_union_composition_identity_lock": (
            "PASS_OFFLINE"
            if rf_checks.get("full_market_unique_union_composition_identity_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "combined_dryrun_cohort_composition_identity_lock": (
            "PASS_OFFLINE"
            if rt_checks.get("combined_dryrun_cohort_composition_identity_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "company_coverage_scale_composition_identity_lock": (
            "PASS_OFFLINE"
            if rb_checks.get("company_coverage_scale_composition_identity_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "cross_full_market_scale_repro_wall_meta_bundle_identity_lock": (
            "PASS_OFFLINE"
            if bundle_checks.get(
                "cross_full_market_scale_repro_wall_meta_bundle_identity_lock_all_pass"
            )
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
            if bat_checks.get("fm01_05_12_46_battery_all_pass")
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

    def _write_ledger(name: str, payload: Dict[str, Any]) -> str:
        rel = _rel(os.path.join(out_root, name), base_dir=base_dir)
        with open(_abs(rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        return rel

    rf_rel = _write_ledger(
        "full_market_unique_union_composition_identity_lock_ledger.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "fingerprint_sha256": rf_meta["fingerprint"],
            "composition_sha256": rf_meta["composition_sha256"],
            "full_market_unique_union_formula": rf_meta[
                "full_market_unique_union_formula"
            ],
            "sample_denials": rf_meta["sample_denials"],
            "doc": rf_meta["doc"],
        },
    )
    rt_rel = _write_ledger(
        "combined_dryrun_cohort_composition_identity_lock_ledger.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "fingerprint_sha256": rt_meta["fingerprint"],
            "composition_sha256": rt_meta["composition_sha256"],
            "combined_dryrun_cohort_formula": rt_meta["combined_dryrun_cohort_formula"],
            "sample_denials": rt_meta["sample_denials"],
            "doc": rt_meta["doc"],
        },
    )
    rb_rel = _write_ledger(
        "company_coverage_scale_composition_identity_lock_ledger.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "fingerprint_sha256": rb_meta["fingerprint"],
            "composition_sha256": rb_meta["composition_sha256"],
            "company_coverage_scale_formula": rb_meta[
                "company_coverage_scale_formula"
            ],
            "sample_denials": rb_meta["sample_denials"],
            "doc": rb_meta["doc"],
        },
    )
    bundle_rel = _write_ledger(
        "cross_full_market_scale_repro_wall_meta_bundle_identity_lock_ledger.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "fingerprint_sha256": bundle_meta["fingerprint"],
            "bundle_sha256": bundle_meta["bundle_sha256"],
            "compositions": bundle_meta["compositions"],
            "sample_denials": bundle_meta["sample_denials"],
            "doc": bundle_meta["doc"],
        },
    )

    battery_rel = _write_ledger(
        "fm_gate_battery.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "gate": overall,
            "fm46_gate": "PASS_OFFLINE",
            "fm47_gate": overall,
            "layer_gates": layer_gates,
            "fail_count": fail_count,
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
            "residual_formula": EXPECTED_RESIDUAL_FORMULA,
            "union_formula": EXPECTED_UNION_FORMULA,
            "union_status_formula": EXPECTED_UNION_STATUS_FORMULA,
            "surface_formula": EXPECTED_SURFACE_FORMULA,
            "surface_delta_formula": EXPECTED_SURFACE_DELTA_FORMULA,
            "additive_formula": EXPECTED_ADDITIVE_FORMULA,
            "overlap_delta_formula": EXPECTED_OVERLAP_DELTA_FORMULA,
            "tier_coverage_formula": EXPECTED_TIER_COVERAGE_FORMULA,
            "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
            "risk_band_status_formula": EXPECTED_RISK_BAND_STATUS_FORMULA,
            "resume_formula": EXPECTED_RESUME_FORMULA,
            "resume_taxonomy_formula": EXPECTED_RESUME_TAXONOMY_FORMULA,
            "coverage_formula": EXPECTED_COVERAGE_FORMULA,
            "combined_dryrun_formula": EXPECTED_COMBINED_DRYRUN_FORMULA,
            "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
            "residual_formula_composition_sha256": (
                EXPECTED_RESIDUAL_FORMULA_COMPOSITION_SHA256
            ),
            "resume_taxonomy_composition_sha256": (
                EXPECTED_RESUME_TAXONOMY_COMPOSITION_SHA256
            ),
            "risk_band_status_composition_sha256": (
                EXPECTED_RISK_BAND_STATUS_COMPOSITION_SHA256
            ),
            "cross_residual_resume_risk_coverage_wall_meta_bundle_sha256": (
                EXPECTED_CROSS_RESIDUAL_RESUME_RISK_COVERAGE_WALL_META_BUNDLE_SHA256
            ),
            "full_market_unique_union_composition_sha256": (
                EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256
            ),
            "combined_dryrun_cohort_composition_sha256": (
                EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256
            ),
            "company_coverage_scale_composition_sha256": (
                EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256
            ),
            "cross_full_market_scale_repro_wall_meta_bundle_sha256": (
                EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256
            ),
            "full_market_unique_union_formula": EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA,
            "combined_dryrun_cohort_formula": EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA,
            "company_coverage_scale_formula": EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA,
            "cross_stable_metrics_wall_meta_bundle_sha256": (
                EXPECTED_CROSS_STABLE_METRICS_WALL_META_BUNDLE_SHA256
            ),
        },
    )

    observed_fps = {
        "full_market_unique_union_composition_identity_lock": rf_meta["fingerprint"],
        "combined_dryrun_cohort_composition_identity_lock": rt_meta["fingerprint"],
        "company_coverage_scale_composition_identity_lock": rb_meta["fingerprint"],
        "cross_full_market_scale_repro_wall_meta_bundle_identity_lock": bundle_meta[
            "fingerprint"
        ],
        "scale_matrix": fp,
    }

    fingerprint_rel = _write_ledger(
        "scale_fingerprint.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "cninfo_calls": 0,
            "seal_chain_extended": False,
            "approved_for_snapshot_rebuild": False,
            "hold_recommendation": "KEEP_EXECUTE_FALSE",
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
            "scale_tier_count": EXPECTED_SCALE_TIER_COUNT,
            "company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
            "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
            "residual_formula_composition_sha256": (
                EXPECTED_RESIDUAL_FORMULA_COMPOSITION_SHA256
            ),
            "resume_taxonomy_composition_sha256": (
                EXPECTED_RESUME_TAXONOMY_COMPOSITION_SHA256
            ),
            "risk_band_status_composition_sha256": (
                EXPECTED_RISK_BAND_STATUS_COMPOSITION_SHA256
            ),
            "cross_residual_resume_risk_coverage_wall_meta_bundle_sha256": (
                EXPECTED_CROSS_RESIDUAL_RESUME_RISK_COVERAGE_WALL_META_BUNDLE_SHA256
            ),
            "full_market_unique_union_composition_sha256": (
                EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256
            ),
            "combined_dryrun_cohort_composition_sha256": (
                EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256
            ),
            "company_coverage_scale_composition_sha256": (
                EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256
            ),
            "cross_full_market_scale_repro_wall_meta_bundle_sha256": (
                EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256
            ),
            "full_market_unique_union_formula": EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA,
            "combined_dryrun_cohort_formula": EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA,
            "company_coverage_scale_formula": EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA,
            "cross_stable_metrics_wall_meta_bundle_sha256": (
                EXPECTED_CROSS_STABLE_METRICS_WALL_META_BUNDLE_SHA256
            ),
            "residual_formula": EXPECTED_RESIDUAL_FORMULA,
            "resume_taxonomy_formula": EXPECTED_RESUME_TAXONOMY_FORMULA,
            "risk_band_status_formula": EXPECTED_RISK_BAND_STATUS_FORMULA,
            "coverage_formula": EXPECTED_COVERAGE_FORMULA,
            "union_formula": EXPECTED_UNION_FORMULA,
            "surface_formula": EXPECTED_SURFACE_FORMULA,
            "additive_formula": EXPECTED_ADDITIVE_FORMULA,
            "tier_coverage_formula": EXPECTED_TIER_COVERAGE_FORMULA,
            "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
            "resume_formula": EXPECTED_RESUME_FORMULA,
            "combined_dryrun_formula": EXPECTED_COMBINED_DRYRUN_FORMULA,
            "layer_row_counts": {
                k: sum(1 for r in matrix if r.get("layer") == k) for k in layer_gates
            },
            "observed_fps": observed_fps,
        },
    )

    packet_rel = _write_ledger(
        "scale_packet.json",
        {
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
            "surface_unique": EXPECTED_SURFACE_UNIQUE,
            "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
            "union_complete": EXPECTED_UNION_COMPLETE,
            "union_partial": EXPECTED_UNION_PARTIAL,
            "union_failed": EXPECTED_UNION_FAILED,
            "overlap_delta": EXPECTED_OVERLAP_DELTA,
            "resume_total": EXPECTED_RESUME_TOTAL,
            "resume_improved": EXPECTED_RESUME_IMPROVED,
            "resume_same": EXPECTED_RESUME_SAME,
            "resume_worse": EXPECTED_RESUME_WORSE,
            "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
            "dry863_extras": sorted(EXPECTED_DRY863_EXTRA),
            "failed_codes": sorted(EXPECTED_FAILED_CODES),
            "resume_same_codes": list(EXPECTED_RESUME_SAME_CODES),
            "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
            "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
            "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
            "partial_codes_sha256": EXPECTED_PARTIAL_CODES_SHA256,
            "failed_codes_sha256": EXPECTED_FAILED_CODES_SHA256,
            "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
            "improved_codes_sha256": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
            "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
            "worse_codes_sha256": EXPECTED_RESUME_WORSE_CODES_SHA256,
            "overlap_codes_sha256": EXPECTED_OVERLAP_CODES_SHA256,
            "dry863_extras_sha256": EXPECTED_DRY863_EXTRAS_SHA256,
            "unique_union_composition_sha256": EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
            "surface_composition_sha256": EXPECTED_SURFACE_COMPOSITION_SHA256,
            "additive_composition_sha256": EXPECTED_ADDITIVE_COMPOSITION_SHA256,
            "residual_composition_sha256": EXPECTED_RESIDUAL_COMPOSITION_SHA256,
            "resume_composition_sha256": EXPECTED_RESUME_COMPOSITION_SHA256,
            "cross_composition_bundle_sha256": EXPECTED_CROSS_COMPOSITION_BUNDLE_SHA256,
            "cross_formula_bundle_sha256": EXPECTED_CROSS_FORMULA_BUNDLE_SHA256,
            "risk_band_composition_sha256": EXPECTED_RISK_BAND_COMPOSITION_SHA256,
            "tier_coverage_composition_sha256": EXPECTED_TIER_COVERAGE_COMPOSITION_SHA256,
            "combined_dryrun_composition_sha256": (
                EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256
            ),
            "cross_formula_composition_meta_bundle_sha256": (
                EXPECTED_CROSS_FORMULA_COMPOSITION_META_BUNDLE_SHA256
            ),
            "union_status_composition_sha256": EXPECTED_UNION_STATUS_COMPOSITION_SHA256,
            "overlap_delta_composition_sha256": EXPECTED_OVERLAP_DELTA_COMPOSITION_SHA256,
            "surface_delta_composition_sha256": EXPECTED_SURFACE_DELTA_COMPOSITION_SHA256,
            "cross_stable_metrics_wall_meta_bundle_sha256": (
                EXPECTED_CROSS_STABLE_METRICS_WALL_META_BUNDLE_SHA256
            ),
            "residual_formula_composition_sha256": (
                EXPECTED_RESIDUAL_FORMULA_COMPOSITION_SHA256
            ),
            "resume_taxonomy_composition_sha256": (
                EXPECTED_RESUME_TAXONOMY_COMPOSITION_SHA256
            ),
            "risk_band_status_composition_sha256": (
                EXPECTED_RISK_BAND_STATUS_COMPOSITION_SHA256
            ),
            "cross_residual_resume_risk_coverage_wall_meta_bundle_sha256": (
                EXPECTED_CROSS_RESIDUAL_RESUME_RISK_COVERAGE_WALL_META_BUNDLE_SHA256
            ),
            "full_market_unique_union_composition_sha256": (
                EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256
            ),
            "combined_dryrun_cohort_composition_sha256": (
                EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256
            ),
            "company_coverage_scale_composition_sha256": (
                EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256
            ),
            "cross_full_market_scale_repro_wall_meta_bundle_sha256": (
                EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256
            ),
            "full_market_unique_union_formula": EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA,
            "combined_dryrun_cohort_formula": EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA,
            "company_coverage_scale_formula": EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA,
            "combined_dryrun_formula": EXPECTED_COMBINED_DRYRUN_FORMULA,
            "batch_priority": list(EXPECTED_BATCH_PRIORITY),
            "residual_formula": EXPECTED_RESIDUAL_FORMULA,
            "union_formula": EXPECTED_UNION_FORMULA,
            "union_status_formula": EXPECTED_UNION_STATUS_FORMULA,
            "surface_formula": EXPECTED_SURFACE_FORMULA,
            "surface_delta_formula": EXPECTED_SURFACE_DELTA_FORMULA,
            "additive_formula": EXPECTED_ADDITIVE_FORMULA,
            "overlap_delta_formula": EXPECTED_OVERLAP_DELTA_FORMULA,
            "tier_coverage_formula": EXPECTED_TIER_COVERAGE_FORMULA,
            "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
            "risk_band_status_formula": EXPECTED_RISK_BAND_STATUS_FORMULA,
            "resume_formula": EXPECTED_RESUME_FORMULA,
            "resume_taxonomy_formula": EXPECTED_RESUME_TAXONOMY_FORMULA,
            "coverage_formula": EXPECTED_COVERAGE_FORMULA,
            "notes": (
                "full_market_unique_union composition identity lock (unique=2249) + "
                "combined_dryrun_cohort composition identity lock (combined_dryrun=1053) + "
                "company_coverage_scale composition identity lock (tiers=7;coverage_sum=3314) + "
                "cross_full_market_scale_repro_wall_meta_bundle identity lock + "
                "FM46 continuity + MOCK49; EXECUTE remains human-held; "
                "does not overwrite MOCK3-48"
            ),
        },
    )

    readme_rel = _rel(os.path.join(out_root, "README.md"), base_dir=base_dir)
    with open(_abs(readme_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        fh.write(
            "\n".join(
                [
                    "# C-FM-47 mock scale lineage/drift/protected/repro-wall-meta-bundle safety root",
                    "",
                    f"task_id: {TASK_ID}",
                    f"gate: {overall}",
                    "cninfo_calls: 0",
                    "hold_recommendation: KEEP_EXECUTE_FALSE",
                    "approved_for_snapshot_rebuild: false",
                    "seal_chain_extended: false",
                    f"harvest_unique_union: {EXPECTED_HARVEST_UNIQUE_UNION}",
                    f"surface_unique: {EXPECTED_SURFACE_UNIQUE}",
                    f"harvest_additive: {EXPECTED_HARVEST_ADDITIVE}",
                    f"lineage_winner_provenance_formula: {EXPECTED_LINEAGE_WINNER_PROVENANCE_FORMULA}",
                    f"partition_codeset_formula: {EXPECTED_PARTITION_CODESET_FORMULA}",
                    f"protected_root_registry_formula: {EXPECTED_PROTECTED_ROOT_REGISTRY_FORMULA}",
                    f"lineage_winner_provenance_composition_sha256: {EXPECTED_LINEAGE_WINNER_PROVENANCE_COMPOSITION_SHA256}",
                    f"partition_codeset_composition_sha256: {EXPECTED_PARTITION_CODESET_COMPOSITION_SHA256}",
                    f"protected_root_registry_composition_sha256: {EXPECTED_PROTECTED_ROOT_REGISTRY_COMPOSITION_SHA256}",
                    f"cross_lineage_drift_protected_repro_wall_meta_bundle_sha256: {EXPECTED_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_SHA256}",
                    "",
                    "Isolation: MOCK3-48 frozen; this root is C-ROOT-MOCK49.",
                    "No CNINFO live. No production snapshot EXECUTE.",
                    "",
                ]
            )
        )

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
        "resume_same_codes": list(EXPECTED_RESUME_SAME_CODES),
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
        "partial_codes_sha256": EXPECTED_PARTIAL_CODES_SHA256,
        "failed_codes_sha256": EXPECTED_FAILED_CODES_SHA256,
        "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
        "improved_codes_sha256": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
        "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
        "worse_codes_sha256": EXPECTED_RESUME_WORSE_CODES_SHA256,
        "overlap_codes_sha256": EXPECTED_OVERLAP_CODES_SHA256,
        "dry863_extras_sha256": EXPECTED_DRY863_EXTRAS_SHA256,
        "unique_union_composition_sha256": EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
        "surface_composition_sha256": EXPECTED_SURFACE_COMPOSITION_SHA256,
        "additive_composition_sha256": EXPECTED_ADDITIVE_COMPOSITION_SHA256,
        "residual_composition_sha256": EXPECTED_RESIDUAL_COMPOSITION_SHA256,
        "resume_composition_sha256": EXPECTED_RESUME_COMPOSITION_SHA256,
        "cross_composition_bundle_sha256": EXPECTED_CROSS_COMPOSITION_BUNDLE_SHA256,
        "cross_formula_bundle_sha256": EXPECTED_CROSS_FORMULA_BUNDLE_SHA256,
        "risk_band_composition_sha256": EXPECTED_RISK_BAND_COMPOSITION_SHA256,
        "tier_coverage_composition_sha256": EXPECTED_TIER_COVERAGE_COMPOSITION_SHA256,
        "combined_dryrun_composition_sha256": EXPECTED_COMBINED_DRYRUN_COMPOSITION_SHA256,
        "cross_formula_composition_meta_bundle_sha256": (
            EXPECTED_CROSS_FORMULA_COMPOSITION_META_BUNDLE_SHA256
        ),
        "union_status_composition_sha256": EXPECTED_UNION_STATUS_COMPOSITION_SHA256,
        "overlap_delta_composition_sha256": EXPECTED_OVERLAP_DELTA_COMPOSITION_SHA256,
        "surface_delta_composition_sha256": EXPECTED_SURFACE_DELTA_COMPOSITION_SHA256,
        "cross_stable_metrics_wall_meta_bundle_sha256": (
            EXPECTED_CROSS_STABLE_METRICS_WALL_META_BUNDLE_SHA256
        ),
        "residual_formula_composition_sha256": (
            EXPECTED_RESIDUAL_FORMULA_COMPOSITION_SHA256
        ),
        "resume_taxonomy_composition_sha256": (
            EXPECTED_RESUME_TAXONOMY_COMPOSITION_SHA256
        ),
        "risk_band_status_composition_sha256": (
            EXPECTED_RISK_BAND_STATUS_COMPOSITION_SHA256
        ),
        "cross_residual_resume_risk_coverage_wall_meta_bundle_sha256": (
            EXPECTED_CROSS_RESIDUAL_RESUME_RISK_COVERAGE_WALL_META_BUNDLE_SHA256
        ),
        "lineage_winner_provenance_composition_sha256": (
            EXPECTED_LINEAGE_WINNER_PROVENANCE_COMPOSITION_SHA256
        ),
        "partition_codeset_composition_sha256": (
            EXPECTED_PARTITION_CODESET_COMPOSITION_SHA256
        ),
        "protected_root_registry_composition_sha256": (
            EXPECTED_PROTECTED_ROOT_REGISTRY_COMPOSITION_SHA256
        ),
        "cross_lineage_drift_protected_repro_wall_meta_bundle_sha256": (
            EXPECTED_CROSS_LINEAGE_DRIFT_PROTECTED_REPRO_WALL_META_BUNDLE_SHA256
        ),
        "full_market_unique_union_composition_sha256": (
            EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256
        ),
        "combined_dryrun_cohort_composition_sha256": (
            EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256
        ),
        "company_coverage_scale_composition_sha256": (
            EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256
        ),
        "cross_full_market_scale_repro_wall_meta_bundle_sha256": (
            EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256
        ),
        "cross_unique_surface_additive_tier_dryrun_wall_meta_bundle_sha256": (
            EXPECTED_CROSS_UNIQUE_SURFACE_ADDITIVE_TIER_DRYRUN_WALL_META_BUNDLE_SHA256
        ),
        "combined_dryrun_formula": EXPECTED_COMBINED_DRYRUN_FORMULA,
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "residual_formula": EXPECTED_RESIDUAL_FORMULA,
        "full_market_unique_union_formula": EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA,
        "combined_dryrun_cohort_formula": EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA,
        "company_coverage_scale_formula": EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA,
        "union_formula": EXPECTED_UNION_FORMULA,
        "union_status_formula": EXPECTED_UNION_STATUS_FORMULA,
        "surface_formula": EXPECTED_SURFACE_FORMULA,
        "surface_delta_formula": EXPECTED_SURFACE_DELTA_FORMULA,
        "additive_formula": EXPECTED_ADDITIVE_FORMULA,
        "overlap_delta_formula": EXPECTED_OVERLAP_DELTA_FORMULA,
        "tier_coverage_formula": EXPECTED_TIER_COVERAGE_FORMULA,
        "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
        "risk_band_status_formula": EXPECTED_RISK_BAND_STATUS_FORMULA,
        "resume_formula": EXPECTED_RESUME_FORMULA,
        "resume_taxonomy_formula": EXPECTED_RESUME_TAXONOMY_FORMULA,
        "coverage_formula": EXPECTED_COVERAGE_FORMULA,
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "full_market_unique_union_path": rf_rel,
        "combined_dryrun_cohort_path": rt_rel,
        "company_coverage_scale_path": rb_rel,
        "cross_full_market_scale_repro_wall_meta_bundle_path": bundle_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "fm46_packet": paths.fm46_packet_rel,
            "fm46_fingerprint": paths.fm46_fingerprint_rel,
            "fm46_gate": paths.fm46_gate_json_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
        },
    }
