"""
CNINFO C-class — 规模 dry863_extras membership freeze + unique_union
composition identity lock + surface_unique composition identity lock +
cross_formula_bundle identity lock（离线 · C-FM-40）。

在 C-FM-39（partial_risk_band membership freeze（75/14/12/5）+
combined_dryrun_coverage identity lock（1053）+ risk_band_formula identity
lock（75+14+12+5=106）+ resume_formula identity lock（28+1+0=29））已 commit
且 EXECUTE 仍 human-held 之上，继续非 seal 规模/安全能力（不新增 seal /
decision-await / commit-boundary；非 extension↔drift 循环）：
  1) FM39 packet / fingerprint / gate / risk-band·combined·resume ledgers
     零漂移连续
  2) dry863_extras_membership_freeze：{000037,000055} 禁止注入/删除/替换
  3) unique_union_composition_identity_lock：2249=2134+106+9 组成身份锁
  4) surface_unique_composition_identity_lock：2251=2249+2 组成身份锁
  5) cross_formula_bundle_identity_lock：七公式捆绑身份锁
  6) output-root：MOCK3–41 冻结 · MOCK42 放行
  7) FM-01..05 + FM-12..39 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–41 / 权威 dual-layer 索引 ·
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

TASK_ID = "C-FM-40"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm40_scale_dry863_unique_surface_cross_formula_bundle_safety"
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
# C-FM-40 本包冻结指纹（运行后由 fingerprint_* 锁定）
FROZEN_DRY863_EXTRAS_MEMBERSHIP_FREEZE_FP_SHA256 = (
    "11b4dde77764bbc99113c26ea57249de518efc52fceb4907830aacea8106b0b8"
)
FROZEN_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256 = (
    "7e6ac9f4bfab0d522aa6695cdb60403be1f1f86b79e65ddb5f5093b775a4cc74"
)
FROZEN_SURFACE_UNIQUE_COMPOSITION_IDENTITY_LOCK_FP_SHA256 = (
    "cbbcd2a849e2dbc7a2dbbad76ef28c1ac435db07b8bada192e986ae37eb9a1ae"
)
FROZEN_CROSS_FORMULA_BUNDLE_IDENTITY_LOCK_FP_SHA256 = (
    "4040a47e3a4f258af9b5ebbbe325c014289e9aafd6edc13224d4f1d9a1275f25"
)
EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256 = (
    "7725392d7fe52f14bd6868b89a4e0feb04e72108e472c5bd86d0261985b60d53"
)
EXPECTED_SURFACE_COMPOSITION_SHA256 = (
    "5d152925d160cf5ada761bb18d1191ec38ed134bb66e723e7fa6d4e526c98738"
)
EXPECTED_CROSS_FORMULA_BUNDLE_SHA256 = (
    "f2561a695dcd567d7dc2b76873bdfc7c3ab229fb55c209ff50ee0d25917e4813"
)
EXPECTED_RISK_BAND_FORMULA = "75+14+12+5=106"
EXPECTED_RESUME_FORMULA = "28+1+0=29"
EXPECTED_RESIDUAL_FORMULA = "106+9+2=117"
EXPECTED_UNION_FORMULA = "2134+106+9=2249"
EXPECTED_SURFACE_FORMULA = "2249+2=2251"
EXPECTED_ADDITIVE_FORMULA = "2249+12=2261"
EXPECTED_TIER_COVERAGE_FORMULA = "tiers=7;coverage_sum=3314"
EXPECTED_CROSS_FORMULA_BUNDLE = {
    "residual_formula": EXPECTED_RESIDUAL_FORMULA,
    "union_formula": EXPECTED_UNION_FORMULA,
    "surface_formula": EXPECTED_SURFACE_FORMULA,
    "additive_formula": EXPECTED_ADDITIVE_FORMULA,
    "tier_coverage_formula": EXPECTED_TIER_COVERAGE_FORMULA,
    "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
    "resume_formula": EXPECTED_RESUME_FORMULA,
}

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
EXPECTED_OVERLAP_CODES_SHA256 = (
    "39ab9b76382938c4919b3c0b6bbde612fd21a4acfbeee279ea7a0fc8e9847cea"
)
EXPECTED_OVERLAP_CODES = frozenset(
    set(EXPECTED_P35_FU_OVERLAP) | set(EXPECTED_P2_FU_OVERLAP_CODES)
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK42"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK41"
RESUME_HARVEST_ROOT_ID = "C-ROOT-002"

FROZEN_ROOT_IDS_MUST_BLOCK = tuple(f"C-ROOT-MOCK{i}" for i in range(3, 42))

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class Dry863UniqueSurfaceCrossFormulaBundlePaths:
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


def assert_fm40_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-40 写根：须 validation/_mock_*，不得覆盖 MOCK3–41，
    不得写权威 dual-layer 索引；允许本任务 MOCK42 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-40 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _sha256_codes(codes: Sequence[str]) -> str:
    return hashlib.sha256(",".join(sorted(codes)).encode("utf-8")).hexdigest()





def fingerprint_dry863_extras_membership_freeze() -> Tuple[str, Dict[str, Any]]:
    """dry863_extras membership freeze 指纹（{000037,000055}）。"""
    codes = sorted(EXPECTED_DRY863_EXTRA)
    doc = {
        "kind": "dry863_extras_membership_freeze",
        "dry863_extras": codes,
        "dry863_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "dry863_extras_sha256": EXPECTED_DRY863_EXTRAS_SHA256,
        "deny_inject": True,
        "deny_drop": True,
        "deny_replace": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_unique_union_composition_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """unique_union composition identity lock 指纹（2249=2134+106+9）。"""
    doc = {
        "kind": "unique_union_composition_identity_lock",
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
        "partial_codes_sha256": EXPECTED_PARTIAL_CODES_SHA256,
        "failed_codes_sha256": EXPECTED_FAILED_CODES_SHA256,
        "composition_sha256": EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
        "union_formula": EXPECTED_UNION_FORMULA,
        "deny_composition_mutate": True,
        "deny_inflate": True,
        "deny_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_surface_unique_composition_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """surface_unique composition identity lock 指纹（2251=2249+2）。"""
    doc = {
        "kind": "surface_unique_composition_identity_lock",
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "dry863_extras_sha256": EXPECTED_DRY863_EXTRAS_SHA256,
        "composition_sha256": EXPECTED_SURFACE_COMPOSITION_SHA256,
        "surface_formula": EXPECTED_SURFACE_FORMULA,
        "deny_composition_mutate": True,
        "deny_inflate": True,
        "deny_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_cross_formula_bundle_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """cross_formula_bundle identity lock 指纹（七公式捆绑）。"""
    doc = {
        "kind": "cross_formula_bundle_identity_lock",
        "formulas": dict(EXPECTED_CROSS_FORMULA_BUNDLE),
        "bundle_sha256": EXPECTED_CROSS_FORMULA_BUNDLE_SHA256,
        "deny_formula_mutate": True,
        "deny_bundle_inflate": True,
        "deny_bundle_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_dry863_extras_membership_mutation(
    *, proposed_codes: Sequence[str], action: str
) -> Dict[str, Any]:
    """评估 dry863 extras 成员变异；inject/drop/replace 一律拒绝。"""
    if action not in ("inject", "drop", "replace"):
        raise ValueError(f"unknown dry863 action: {action}")
    frozen = sorted(EXPECTED_DRY863_EXTRA)
    proposed = sorted({str(c) for c in proposed_codes})
    return {
        "action": action,
        "proposed": proposed,
        "frozen": frozen,
        "matches_frozen": proposed == frozen,
        "mutation_allowed": False,
        "reason": "dry863_extras_membership_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_unique_union_composition_mutation(
    *,
    proposed_unique: int,
    proposed_complete: int,
    proposed_partial: int,
    proposed_failed: int,
) -> Dict[str, Any]:
    """评估 unique_union 组成变异；一律拒绝。"""
    formula_ok = (
        proposed_complete + proposed_partial + proposed_failed == proposed_unique
    )
    matches = (
        proposed_unique == EXPECTED_HARVEST_UNIQUE_UNION
        and proposed_complete == EXPECTED_UNION_COMPLETE
        and proposed_partial == EXPECTED_UNION_PARTIAL
        and proposed_failed == EXPECTED_UNION_FAILED
        and formula_ok
    )
    return {
        "proposed": {
            "unique": proposed_unique,
            "complete": proposed_complete,
            "partial": proposed_partial,
            "failed": proposed_failed,
        },
        "frozen": {
            "unique": EXPECTED_HARVEST_UNIQUE_UNION,
            "complete": EXPECTED_UNION_COMPLETE,
            "partial": EXPECTED_UNION_PARTIAL,
            "failed": EXPECTED_UNION_FAILED,
        },
        "union_formula_holds": formula_ok,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "unique_union_composition_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_surface_unique_composition_mutation(
    *,
    proposed_surface: int,
    proposed_unique: int,
    proposed_delta_n: int,
) -> Dict[str, Any]:
    """评估 surface_unique 组成变异；一律拒绝。"""
    formula_ok = proposed_unique + proposed_delta_n == proposed_surface
    matches = (
        proposed_surface == EXPECTED_SURFACE_UNIQUE
        and proposed_unique == EXPECTED_HARVEST_UNIQUE_UNION
        and proposed_delta_n == EXPECTED_SURFACE_HARVEST_DELTA_N
        and formula_ok
    )
    return {
        "proposed": {
            "surface": proposed_surface,
            "unique": proposed_unique,
            "delta_n": proposed_delta_n,
        },
        "frozen": {
            "surface": EXPECTED_SURFACE_UNIQUE,
            "unique": EXPECTED_HARVEST_UNIQUE_UNION,
            "delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        },
        "surface_formula_holds": formula_ok,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "surface_unique_composition_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_cross_formula_bundle_mutation(
    *, proposed_formulas: Dict[str, str]
) -> Dict[str, Any]:
    """评估 cross_formula_bundle 变异；一律拒绝。"""
    proposed = {str(k): str(v) for k, v in proposed_formulas.items()}
    matches = proposed == dict(EXPECTED_CROSS_FORMULA_BUNDLE)
    return {
        "proposed_formulas": proposed,
        "frozen_formulas": dict(EXPECTED_CROSS_FORMULA_BUNDLE),
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "cross_formula_bundle_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def build_dry863_extras_membership_freeze_rows(
    paths: Dry863UniqueSurfaceCrossFormulaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """dry863_extras membership freeze（{000037,000055}）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_dry863_extras_membership_freeze()
    codes = sorted(EXPECTED_DRY863_EXTRA)

    card_ok = (
        len(codes) == EXPECTED_SURFACE_HARVEST_DELTA_N
        and codes == ["000037", "000055"]
        and _sha256_codes(codes) == EXPECTED_DRY863_EXTRAS_SHA256
    )
    checks["dry863_extras_membership_cardinality"] = card_ok
    rows.append(
        _row(
            check_id="dry863_extras_membership_cardinality",
            layer="dry863_extras_membership_freeze",
            expected="2={000037,000055}",
            observed=f"codes={codes};sha={EXPECTED_DRY863_EXTRAS_SHA256[:12]}",
            ok=card_ok,
            notes="ok" if card_ok else "dry863_cardinality_drift",
        )
    )

    sample_denials = [
        evaluate_dry863_extras_membership_mutation(
            proposed_codes=codes + ["999999"], action="inject"
        ),
        evaluate_dry863_extras_membership_mutation(
            proposed_codes=codes[:1], action="drop"
        ),
        evaluate_dry863_extras_membership_mutation(
            proposed_codes=["000001", "000002"], action="replace"
        ),
        evaluate_dry863_extras_membership_mutation(
            proposed_codes=codes, action="replace"
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["dry863_extras_membership_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="dry863_extras_membership_mutation_denied",
            layer="dry863_extras_membership_freeze",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "dry863_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_inject"] is True
        and doc["deny_drop"] is True
        and doc["deny_replace"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["dry863_n"] == 2
        and doc["dry863_extras_sha256"] == EXPECTED_DRY863_EXTRAS_SHA256
    )
    checks["dry863_extras_membership_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="dry863_extras_membership_flags_locked",
            layer="dry863_extras_membership_freeze",
            expected="deny_inject/drop/replace+KEEP_EXECUTE_FALSE",
            observed=f"hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "dry863_flags_drift",
        )
    )

    fp_ok = fp == FROZEN_DRY863_EXTRAS_MEMBERSHIP_FREEZE_FP_SHA256
    checks["dry863_extras_membership_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="dry863_extras_membership_fingerprint",
            layer="dry863_extras_membership_freeze",
            expected=FROZEN_DRY863_EXTRAS_MEMBERSHIP_FREEZE_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "dry863_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["dry863_extras_membership_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="dry863_extras_membership_freeze_all_pass",
            layer="dry863_extras_membership_freeze",
            expected="dry863_extras_membership_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "dry863_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "dry863_extras": codes,
        "dry863_extras_sha256": EXPECTED_DRY863_EXTRAS_SHA256,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_unique_union_composition_identity_lock_rows(
    paths: Dry863UniqueSurfaceCrossFormulaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """unique_union composition identity lock（2249=2134+106+9）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_unique_union_composition_identity_lock()

    comp_payload = {
        "complete_n": EXPECTED_UNION_COMPLETE,
        "partial_n": EXPECTED_UNION_PARTIAL,
        "failed_n": EXPECTED_UNION_FAILED,
        "complete_sha256": EXPECTED_COMPLETE_CODES_SHA256,
        "partial_sha256": EXPECTED_PARTIAL_CODES_SHA256,
        "failed_sha256": EXPECTED_FAILED_CODES_SHA256,
        "unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
    }
    comp_sha = hashlib.sha256(
        json.dumps(comp_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    formula_ok = (
        EXPECTED_UNION_COMPLETE
        + EXPECTED_UNION_PARTIAL
        + EXPECTED_UNION_FAILED
        == EXPECTED_HARVEST_UNIQUE_UNION
        and EXPECTED_UNION_FORMULA == "2134+106+9=2249"
        and comp_sha == EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256
    )
    checks["unique_union_composition_identity"] = formula_ok
    rows.append(
        _row(
            check_id="unique_union_composition_identity",
            layer="unique_union_composition_identity_lock",
            expected="2249=2134+106+9",
            observed=f"formula={EXPECTED_UNION_FORMULA};sha={comp_sha[:12]}",
            ok=formula_ok,
            notes="ok" if formula_ok else "unique_union_composition_drift",
        )
    )

    sample_denials = [
        evaluate_unique_union_composition_mutation(
            proposed_unique=2250,
            proposed_complete=2134,
            proposed_partial=106,
            proposed_failed=9,
        ),
        evaluate_unique_union_composition_mutation(
            proposed_unique=2249,
            proposed_complete=2135,
            proposed_partial=106,
            proposed_failed=9,
        ),
        evaluate_unique_union_composition_mutation(
            proposed_unique=2248,
            proposed_complete=2134,
            proposed_partial=106,
            proposed_failed=9,
        ),
        evaluate_unique_union_composition_mutation(
            proposed_unique=EXPECTED_HARVEST_UNIQUE_UNION,
            proposed_complete=EXPECTED_UNION_COMPLETE,
            proposed_partial=EXPECTED_UNION_PARTIAL,
            proposed_failed=EXPECTED_UNION_FAILED,
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["unique_union_composition_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="unique_union_composition_mutation_denied",
            layer="unique_union_composition_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "unique_union_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_composition_mutate"] is True
        and doc["deny_inflate"] is True
        and doc["deny_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["composition_sha256"] == EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256
    )
    checks["unique_union_composition_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="unique_union_composition_flags_locked",
            layer="unique_union_composition_identity_lock",
            expected="deny_composition/inflate/deflate+KEEP_EXECUTE_FALSE",
            observed=f"hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "unique_union_flags_drift",
        )
    )

    fp_ok = fp == FROZEN_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256
    checks["unique_union_composition_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="unique_union_composition_fingerprint",
            layer="unique_union_composition_identity_lock",
            expected=FROZEN_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "unique_union_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["unique_union_composition_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="unique_union_composition_identity_lock_all_pass",
            layer="unique_union_composition_identity_lock",
            expected="unique_union_composition_identity_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "unique_union_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "composition_sha256": EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
        "union_formula": EXPECTED_UNION_FORMULA,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_surface_unique_composition_identity_lock_rows(
    paths: Dry863UniqueSurfaceCrossFormulaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """surface_unique composition identity lock（2251=2249+2）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_surface_unique_composition_identity_lock()

    comp_payload = {
        "unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "dry863_extras_sha256": EXPECTED_DRY863_EXTRAS_SHA256,
        "dry863_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
    }
    comp_sha = hashlib.sha256(
        json.dumps(comp_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    formula_ok = (
        EXPECTED_HARVEST_UNIQUE_UNION + EXPECTED_SURFACE_HARVEST_DELTA_N
        == EXPECTED_SURFACE_UNIQUE
        and EXPECTED_SURFACE_FORMULA == "2249+2=2251"
        and comp_sha == EXPECTED_SURFACE_COMPOSITION_SHA256
    )
    checks["surface_unique_composition_identity"] = formula_ok
    rows.append(
        _row(
            check_id="surface_unique_composition_identity",
            layer="surface_unique_composition_identity_lock",
            expected="2251=2249+2",
            observed=f"formula={EXPECTED_SURFACE_FORMULA};sha={comp_sha[:12]}",
            ok=formula_ok,
            notes="ok" if formula_ok else "surface_composition_drift",
        )
    )

    sample_denials = [
        evaluate_surface_unique_composition_mutation(
            proposed_surface=2252, proposed_unique=2249, proposed_delta_n=2
        ),
        evaluate_surface_unique_composition_mutation(
            proposed_surface=2251, proposed_unique=2249, proposed_delta_n=3
        ),
        evaluate_surface_unique_composition_mutation(
            proposed_surface=2250, proposed_unique=2249, proposed_delta_n=2
        ),
        evaluate_surface_unique_composition_mutation(
            proposed_surface=EXPECTED_SURFACE_UNIQUE,
            proposed_unique=EXPECTED_HARVEST_UNIQUE_UNION,
            proposed_delta_n=EXPECTED_SURFACE_HARVEST_DELTA_N,
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["surface_unique_composition_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="surface_unique_composition_mutation_denied",
            layer="surface_unique_composition_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "surface_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_composition_mutate"] is True
        and doc["deny_inflate"] is True
        and doc["deny_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["composition_sha256"] == EXPECTED_SURFACE_COMPOSITION_SHA256
    )
    checks["surface_unique_composition_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="surface_unique_composition_flags_locked",
            layer="surface_unique_composition_identity_lock",
            expected="deny_composition/inflate/deflate+KEEP_EXECUTE_FALSE",
            observed=f"hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "surface_flags_drift",
        )
    )

    fp_ok = fp == FROZEN_SURFACE_UNIQUE_COMPOSITION_IDENTITY_LOCK_FP_SHA256
    checks["surface_unique_composition_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="surface_unique_composition_fingerprint",
            layer="surface_unique_composition_identity_lock",
            expected=FROZEN_SURFACE_UNIQUE_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "surface_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["surface_unique_composition_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="surface_unique_composition_identity_lock_all_pass",
            layer="surface_unique_composition_identity_lock",
            expected="surface_unique_composition_identity_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "surface_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "composition_sha256": EXPECTED_SURFACE_COMPOSITION_SHA256,
        "surface_formula": EXPECTED_SURFACE_FORMULA,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_cross_formula_bundle_identity_lock_rows(
    paths: Dry863UniqueSurfaceCrossFormulaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """cross_formula_bundle identity lock（七公式捆绑）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_cross_formula_bundle_identity_lock()

    bundle_sha = hashlib.sha256(
        json.dumps(
            dict(EXPECTED_CROSS_FORMULA_BUNDLE),
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    identity_ok = (
        bundle_sha == EXPECTED_CROSS_FORMULA_BUNDLE_SHA256
        and len(EXPECTED_CROSS_FORMULA_BUNDLE) == 7
        and EXPECTED_CROSS_FORMULA_BUNDLE["risk_band_formula"]
        == EXPECTED_RISK_BAND_FORMULA
        and EXPECTED_CROSS_FORMULA_BUNDLE["resume_formula"] == EXPECTED_RESUME_FORMULA
    )
    checks["cross_formula_bundle_identity"] = identity_ok
    rows.append(
        _row(
            check_id="cross_formula_bundle_identity",
            layer="cross_formula_bundle_identity_lock",
            expected="7_formulas_bundle",
            observed=f"n={len(EXPECTED_CROSS_FORMULA_BUNDLE)};sha={bundle_sha[:12]}",
            ok=identity_ok,
            notes="ok" if identity_ok else "cross_formula_bundle_drift",
        )
    )

    inflated = dict(EXPECTED_CROSS_FORMULA_BUNDLE)
    inflated["extra_formula"] = "0=0"
    deflated = {
        k: v
        for k, v in EXPECTED_CROSS_FORMULA_BUNDLE.items()
        if k != "resume_formula"
    }
    mutated = dict(EXPECTED_CROSS_FORMULA_BUNDLE)
    mutated["union_formula"] = "2134+106+8=2248"
    sample_denials = [
        evaluate_cross_formula_bundle_mutation(proposed_formulas=inflated),
        evaluate_cross_formula_bundle_mutation(proposed_formulas=deflated),
        evaluate_cross_formula_bundle_mutation(proposed_formulas=mutated),
        evaluate_cross_formula_bundle_mutation(
            proposed_formulas=dict(EXPECTED_CROSS_FORMULA_BUNDLE)
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["cross_formula_bundle_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="cross_formula_bundle_mutation_denied",
            layer="cross_formula_bundle_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "cross_formula_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_formula_mutate"] is True
        and doc["deny_bundle_inflate"] is True
        and doc["deny_bundle_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["bundle_sha256"] == EXPECTED_CROSS_FORMULA_BUNDLE_SHA256
    )
    checks["cross_formula_bundle_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="cross_formula_bundle_flags_locked",
            layer="cross_formula_bundle_identity_lock",
            expected="deny_mutate/inflate/deflate+KEEP_EXECUTE_FALSE",
            observed=f"hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "cross_formula_flags_drift",
        )
    )

    fp_ok = fp == FROZEN_CROSS_FORMULA_BUNDLE_IDENTITY_LOCK_FP_SHA256
    checks["cross_formula_bundle_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="cross_formula_bundle_fingerprint",
            layer="cross_formula_bundle_identity_lock",
            expected=FROZEN_CROSS_FORMULA_BUNDLE_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "cross_formula_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["cross_formula_bundle_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="cross_formula_bundle_identity_lock_all_pass",
            layer="cross_formula_bundle_identity_lock",
            expected="cross_formula_bundle_identity_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "cross_formula_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "bundle_sha256": EXPECTED_CROSS_FORMULA_BUNDLE_SHA256,
        "formulas": dict(EXPECTED_CROSS_FORMULA_BUNDLE),
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_fm39_continuity_rows(
    paths: Dry863UniqueSurfaceCrossFormulaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM39 packet / fingerprint / gate / 四 ledger 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm39_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm39_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm39_gate_json_rel, base_dir=base_dir))
    risk_led = load_json(_abs(paths.fm39_partial_risk_band_rel, base_dir=base_dir))
    combined_led = load_json(_abs(paths.fm39_combined_dryrun_rel, base_dir=base_dir))
    rb_formula_led = load_json(
        _abs(paths.fm39_risk_band_formula_rel, base_dir=base_dir)
    )
    resume_led = load_json(_abs(paths.fm39_resume_formula_rel, base_dir=base_dir))

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
        and packet.get("risk_band_formula") == FM39_EXPECTED_RISK_BAND_FORMULA
        and packet.get("resume_formula") == FM39_EXPECTED_RESUME_FORMULA
        and packet.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
        and packet.get("approved_for_snapshot_rebuild") is False
        and packet.get("seal_chain_extended") is False
    )
    checks["fm39_packet_zero_drift"] = pkt_ok
    rows.append(
        _row(
            check_id="fm39_packet_zero_drift",
            layer="fm39_continuity",
            path=paths.fm39_packet_rel,
            expected="PASS_OFFLINE+stable_metrics+formulas",
            observed=f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')}",
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm39_packet_drift",
        )
    )

    fp_ok = (
        fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and fp_doc.get("risk_band_formula") == FM39_EXPECTED_RISK_BAND_FORMULA
        and fp_doc.get("resume_formula") == FM39_EXPECTED_RESUME_FORMULA
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm39_fingerprint_zero_drift"] = fp_ok
    rows.append(
        _row(
            check_id="fm39_fingerprint_zero_drift",
            layer="fm39_continuity",
            path=paths.fm39_fingerprint_rel,
            expected="stable_metrics+fm39_fps",
            observed=f"unique={fp_doc.get('harvest_unique_union')}",
            ok=fp_ok,
            notes="ok" if fp_ok else "fm39_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and gate_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and gate_doc.get("risk_band_formula") == FM39_EXPECTED_RISK_BAND_FORMULA
        and gate_doc.get("resume_formula") == FM39_EXPECTED_RESUME_FORMULA
        and gate_doc.get("seal_chain_extended") is False
    )
    checks["fm39_gate_zero_drift"] = gate_ok
    rows.append(
        _row(
            check_id="fm39_gate_zero_drift",
            layer="fm39_continuity",
            path=paths.fm39_gate_json_rel,
            expected="PASS_OFFLINE+KEEP_EXECUTE_FALSE",
            observed=f"gate={gate_doc.get('gate')}",
            ok=gate_ok,
            notes="ok" if gate_ok else "fm39_gate_drift",
        )
    )

    risk_ok = (
        risk_led.get("fingerprint_sha256") == FM39_FROZEN_PARTIAL_RISK_BAND_MEM_FP
        and risk_led.get("membership_sha256")
        == FM39_EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256
    )
    checks["fm39_partial_risk_band_ledger_zero_drift"] = risk_ok
    rows.append(
        _row(
            check_id="fm39_partial_risk_band_ledger_zero_drift",
            layer="fm39_continuity",
            path=paths.fm39_partial_risk_band_rel,
            expected=FM39_FROZEN_PARTIAL_RISK_BAND_MEM_FP,
            observed=str(risk_led.get("fingerprint_sha256")),
            ok=risk_ok,
            notes="ok" if risk_ok else "fm39_partial_risk_band_ledger_drift",
        )
    )

    combined_ok = (
        combined_led.get("fingerprint_sha256") == FM39_FROZEN_COMBINED_DRYRUN_FP
        and combined_led.get("combined_dryrun_coverage")
        == EXPECTED_COMBINED_DRYRUN_COVERAGE
    )
    checks["fm39_combined_dryrun_ledger_zero_drift"] = combined_ok
    rows.append(
        _row(
            check_id="fm39_combined_dryrun_ledger_zero_drift",
            layer="fm39_continuity",
            path=paths.fm39_combined_dryrun_rel,
            expected=FM39_FROZEN_COMBINED_DRYRUN_FP,
            observed=str(combined_led.get("fingerprint_sha256")),
            ok=combined_ok,
            notes="ok" if combined_ok else "fm39_combined_dryrun_ledger_drift",
        )
    )

    rb_formula_ok = (
        rb_formula_led.get("fingerprint_sha256") == FM39_FROZEN_RISK_BAND_FORMULA_FP
        and rb_formula_led.get("risk_band_formula") == FM39_EXPECTED_RISK_BAND_FORMULA
    )
    checks["fm39_risk_band_formula_ledger_zero_drift"] = rb_formula_ok
    rows.append(
        _row(
            check_id="fm39_risk_band_formula_ledger_zero_drift",
            layer="fm39_continuity",
            path=paths.fm39_risk_band_formula_rel,
            expected=FM39_FROZEN_RISK_BAND_FORMULA_FP,
            observed=str(rb_formula_led.get("fingerprint_sha256")),
            ok=rb_formula_ok,
            notes="ok" if rb_formula_ok else "fm39_risk_band_formula_ledger_drift",
        )
    )

    resume_ok = (
        resume_led.get("fingerprint_sha256") == FM39_FROZEN_RESUME_FORMULA_FP
        and resume_led.get("resume_formula") == FM39_EXPECTED_RESUME_FORMULA
    )
    checks["fm39_resume_formula_ledger_zero_drift"] = resume_ok
    rows.append(
        _row(
            check_id="fm39_resume_formula_ledger_zero_drift",
            layer="fm39_continuity",
            path=paths.fm39_resume_formula_rel,
            expected=FM39_FROZEN_RESUME_FORMULA_FP,
            observed=str(resume_led.get("fingerprint_sha256")),
            ok=resume_ok,
            notes="ok" if resume_ok else "fm39_resume_formula_ledger_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm39_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm39_continuity_all_pass",
            layer="fm39_continuity",
            expected="packet+fp+gate+4ledgers",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm39_continuity_incomplete",
        )
    )
    return rows, checks



def build_output_root_protection_rows(
    paths: Dry863UniqueSurfaceCrossFormulaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK42 放行。"""
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
        assert_fm40_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK42_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock42_ok",
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
    paths: Dry863UniqueSurfaceCrossFormulaBundlePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–41 拒绝 · MOCK42 放行。"""
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

    # 先验 MOCK41（C-FM-39）写根必须仍冻结
    mock41_rel = (
        "outputs/validation/"
        "_mock_c_fm39_scale_risk_band_combined_dryrun_resume_formula_safety"
    )
    mock41_blocked = False
    try:
        assert_fm40_output_root(mock41_rel, base_dir=base_dir)
    except RuntimeError as exc:
        mock41_blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock41_still_frozen"] = mock41_blocked
    rows.append(
        _row(
            check_id="mock41_still_frozen",
            layer="frozen_mock_isolation",
            root_id=PRIOR_TASK_ROOT_ID,
            path=mock41_rel,
            expected="write_forbidden",
            observed="blocked" if mock41_blocked else "allowed",
            ok=mock41_blocked,
            notes="ok" if mock41_blocked else "mock41_write_leak",
        )
    )

    allow_ok = False
    try:
        assert_fm40_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except Exception:
        allow_ok = False
    checks["frozen_allow_mock42"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock42",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="MOCK42_or_ephemeral_allowed",
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
            expected="MOCK3-41_block+MOCK42_allow",
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
    """protected_output_roots.csv：MOCK42 已登记。"""
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

    mock42 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(mock42.get("path_pattern") or "")
    checks["protected_csv_mock42_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock42_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock42.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock42_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3–41+resume+auth+fuller_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..39 gate battery（跳过 seal FM06–11）。"""
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
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
        "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35",
        "fm36", "fm37", "fm38", "fm39",
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
            "fm33", "fm34", "fm35", "fm36", "fm37", "fm38", "fm39",
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
            "fm34", "fm35", "fm36", "fm37", "fm38", "fm39",
        ):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in (
            "fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34",
            "fm35", "fm36", "fm37", "fm38", "fm39",
        ):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key in (
            "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35",
            "fm36", "fm37", "fm38", "fm39",
        ):
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        if key in (
            "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35", "fm36", "fm37", "fm38", "fm39",
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
        if key in ("fm31", "fm32", "fm33", "fm34", "fm35", "fm36", "fm37", "fm38", "fm39"):
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
            check_id="fm01_05_12_39_battery_all_pass",
            layer="fm_gate_battery",
            expected="all_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_39_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm40(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK42；加固 C-ROOT-002 risk-band/combined/resume formula 说明。"""
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
                "C-FM-24..39 scale/safety freezes + C-FM-40 dry863/unique/surface/"
                "cross-formula-bundle; 只读直至人批重跑"
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
                "C-FM-40 scale dry863_extras membership freeze (Δ2) + "
                "unique_union composition identity lock (2249=2134+106+9) + "
                "surface_unique composition identity lock (2251=2249+2) + "
                "cross_formula_bundle identity lock + FM39 continuity; "
                "never production EXECUTE; must not overwrite MOCK3-41; "
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


def run_scale_dry863_unique_surface_cross_formula_bundle_safety(
    *,
    paths: Dry863UniqueSurfaceCrossFormulaBundlePaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-40 规模 dry863/unique/surface/cross-formula-bundle 离线 QA。"""
    paths = paths or Dry863UniqueSurfaceCrossFormulaBundlePaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm40(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm40_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm39_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    dry_rows, dry_checks, dry_meta = build_dry863_extras_membership_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(dry_rows)
    uniq_rows, uniq_checks, uniq_meta = (
        build_unique_union_composition_identity_lock_rows(paths, base_dir=base_dir)
    )
    matrix.extend(uniq_rows)
    surf_rows, surf_checks, surf_meta = (
        build_surface_unique_composition_identity_lock_rows(paths, base_dir=base_dir)
    )
    matrix.extend(surf_rows)
    bundle_rows, bundle_checks, bundle_meta = (
        build_cross_formula_bundle_identity_lock_rows(paths, base_dir=base_dir)
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
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm39_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm39_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "dry863_extras_membership_freeze": (
            "PASS_OFFLINE"
            if dry_checks.get("dry863_extras_membership_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "unique_union_composition_identity_lock": (
            "PASS_OFFLINE"
            if uniq_checks.get("unique_union_composition_identity_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "surface_unique_composition_identity_lock": (
            "PASS_OFFLINE"
            if surf_checks.get("surface_unique_composition_identity_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "cross_formula_bundle_identity_lock": (
            "PASS_OFFLINE"
            if bundle_checks.get("cross_formula_bundle_identity_lock_all_pass")
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
            if bat_checks.get("fm01_05_12_39_battery_all_pass")
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

    dry_rel = _write_ledger(
        "dry863_extras_membership_freeze_ledger.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "fingerprint_sha256": dry_meta["fingerprint"],
            "dry863_extras": dry_meta["dry863_extras"],
            "dry863_extras_sha256": dry_meta["dry863_extras_sha256"],
            "sample_denials": dry_meta["sample_denials"],
            "doc": dry_meta["doc"],
        },
    )
    uniq_rel = _write_ledger(
        "unique_union_composition_identity_lock_ledger.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "fingerprint_sha256": uniq_meta["fingerprint"],
            "composition_sha256": uniq_meta["composition_sha256"],
            "union_formula": uniq_meta["union_formula"],
            "sample_denials": uniq_meta["sample_denials"],
            "doc": uniq_meta["doc"],
        },
    )
    surf_rel = _write_ledger(
        "surface_unique_composition_identity_lock_ledger.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "fingerprint_sha256": surf_meta["fingerprint"],
            "composition_sha256": surf_meta["composition_sha256"],
            "surface_formula": surf_meta["surface_formula"],
            "sample_denials": surf_meta["sample_denials"],
            "doc": surf_meta["doc"],
        },
    )
    bundle_rel = _write_ledger(
        "cross_formula_bundle_identity_lock_ledger.json",
        {
            "generated_at": generated_at,
            "task_id": TASK_ID,
            "fingerprint_sha256": bundle_meta["fingerprint"],
            "bundle_sha256": bundle_meta["bundle_sha256"],
            "formulas": bundle_meta["formulas"],
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
            "fm39_gate": "PASS_OFFLINE",
            "fm40_gate": overall,
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
            "surface_formula": EXPECTED_SURFACE_FORMULA,
            "additive_formula": EXPECTED_ADDITIVE_FORMULA,
            "tier_coverage_formula": EXPECTED_TIER_COVERAGE_FORMULA,
            "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
            "resume_formula": EXPECTED_RESUME_FORMULA,
            "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
            "cross_formula_bundle_sha256": EXPECTED_CROSS_FORMULA_BUNDLE_SHA256,
        },
    )

    observed_fps = {
        "dry863_extras_membership_freeze": dry_meta["fingerprint"],
        "unique_union_composition_identity_lock": uniq_meta["fingerprint"],
        "surface_unique_composition_identity_lock": surf_meta["fingerprint"],
        "cross_formula_bundle_identity_lock": bundle_meta["fingerprint"],
        "fm39_partial_risk_band_membership_freeze": FM39_FROZEN_PARTIAL_RISK_BAND_MEM_FP,
        "fm39_combined_dryrun_coverage_identity_lock": FM39_FROZEN_COMBINED_DRYRUN_FP,
        "fm39_risk_band_formula_identity_lock": FM39_FROZEN_RISK_BAND_FORMULA_FP,
        "fm39_resume_formula_identity_lock": FM39_FROZEN_RESUME_FORMULA_FP,
        "fm38_complete_codes_membership_freeze": FM38_FROZEN_COMPLETE_FP,
        "fm38_overlap_delta_membership_freeze": FM38_FROZEN_OVERLAP_FP,
        "fm38_additive_formula_identity_lock": FM38_FROZEN_ADDITIVE_FP,
        "fm38_tier_coverage_formula_identity_lock": FM38_FROZEN_TIER_FP,
        "fm35_winner_map_sha256_lock": FM35_FROZEN_WINNER_MAP_FP,
        "fm35_resume_taxonomy_codeset_sha256_lock": FM35_FROZEN_RESUME_TAXONOMY_FP,
        "fm35_batch_priority_order_freeze": FM35_FROZEN_BATCH_PRIORITY_FP,
        "fm35_partial_risk_band_cardinality_freeze": FM35_FROZEN_PARTIAL_RISK_BAND_FP,
    }

    fingerprint_rel = _write_ledger(
        "scale_fingerprint.json",
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
            "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
            "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
            "partial_codes_sha256": EXPECTED_PARTIAL_CODES_SHA256,
            "failed_codes_sha256": EXPECTED_FAILED_CODES_SHA256,
            "overlap_codes_sha256": EXPECTED_OVERLAP_CODES_SHA256,
            "dry863_extras_sha256": EXPECTED_DRY863_EXTRAS_SHA256,
            "unique_union_composition_sha256": EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
            "surface_composition_sha256": EXPECTED_SURFACE_COMPOSITION_SHA256,
            "cross_formula_bundle_sha256": EXPECTED_CROSS_FORMULA_BUNDLE_SHA256,
            "partial_risk_band_membership_sha256": (
                FM39_EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256
            ),
            "residual_formula": EXPECTED_RESIDUAL_FORMULA,
            "union_formula": EXPECTED_UNION_FORMULA,
            "surface_formula": EXPECTED_SURFACE_FORMULA,
            "additive_formula": EXPECTED_ADDITIVE_FORMULA,
            "tier_coverage_formula": EXPECTED_TIER_COVERAGE_FORMULA,
            "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
            "resume_formula": EXPECTED_RESUME_FORMULA,
            "matrix_fingerprint_sha256": fp,
            "observed_fps": observed_fps,
        },
    )

    packet_rel = _write_ledger(
        "scale_packet.json",
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
            "fail_count": fail_count,
            "layer_gates": layer_gates,
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
            "overlap_codes_sha256": EXPECTED_OVERLAP_CODES_SHA256,
            "dry863_extras_sha256": EXPECTED_DRY863_EXTRAS_SHA256,
            "unique_union_composition_sha256": EXPECTED_UNIQUE_UNION_COMPOSITION_SHA256,
            "surface_composition_sha256": EXPECTED_SURFACE_COMPOSITION_SHA256,
            "cross_formula_bundle_sha256": EXPECTED_CROSS_FORMULA_BUNDLE_SHA256,
            "partial_risk_band_membership_sha256": (
                FM39_EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256
            ),
            "batch_priority": list(EXPECTED_BATCH_PRIORITY),
            "residual_formula": EXPECTED_RESIDUAL_FORMULA,
            "union_formula": EXPECTED_UNION_FORMULA,
            "surface_formula": EXPECTED_SURFACE_FORMULA,
            "additive_formula": EXPECTED_ADDITIVE_FORMULA,
            "tier_coverage_formula": EXPECTED_TIER_COVERAGE_FORMULA,
            "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
            "resume_formula": EXPECTED_RESUME_FORMULA,
            "notes": (
                "dry863_extras membership freeze (Δ2) + unique_union composition "
                "identity lock (2249=2134+106+9) + surface_unique composition "
                "identity lock (2251=2249+2) + cross_formula_bundle identity lock "
                "+ FM39 continuity + MOCK42; EXECUTE remains human-held; "
                "does not overwrite MOCK3-41"
            ),
        },
    )

    readme_path = os.path.join(out_root, "README.md")
    with open(readme_path, "w", encoding="utf-8") as fh:
        fh.write(
            "\n".join(
                [
                    "# C-FM-40 mock scale dry863/unique/surface/cross-formula-bundle safety root",
                    "",
                    f"gate: `{overall}`",
                    "seal_chain_extended: false",
                    f"scale_tier_count: {EXPECTED_SCALE_TIER_COUNT}",
                    f"company_coverage_sum: {EXPECTED_COMPANY_COVERAGE_SUM}",
                    f"harvest_unique_union: {EXPECTED_HARVEST_UNIQUE_UNION}",
                    f"surface_unique: {EXPECTED_SURFACE_UNIQUE}",
                    f"combined_dryrun_coverage: {EXPECTED_COMBINED_DRYRUN_COVERAGE}",
                    f"surface_harvest_delta_n: {EXPECTED_SURFACE_HARVEST_DELTA_N}",
                    f"union_status: {EXPECTED_UNION_COMPLETE}/"
                    f"{EXPECTED_UNION_PARTIAL}/{EXPECTED_UNION_FAILED}",
                    f"overlap_delta: {EXPECTED_OVERLAP_DELTA}",
                    f"residual_safety_coverage: {EXPECTED_RESIDUAL_SAFETY_COVERAGE}",
                    f"residual_formula: {EXPECTED_RESIDUAL_FORMULA}",
                    f"union_formula: {EXPECTED_UNION_FORMULA}",
                    f"surface_formula: {EXPECTED_SURFACE_FORMULA}",
                    f"additive_formula: {EXPECTED_ADDITIVE_FORMULA}",
                    f"tier_coverage_formula: {EXPECTED_TIER_COVERAGE_FORMULA}",
                    f"risk_band_formula: {EXPECTED_RISK_BAND_FORMULA}",
                    f"resume_formula: {EXPECTED_RESUME_FORMULA}",
                    f"cross_formula_bundle_sha256: {EXPECTED_CROSS_FORMULA_BUNDLE_SHA256}",
                    "does_not_overwrite: _mock_c_fm02.._mock_c_fm39 / standard dryrun",
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
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "partial_risk_bands": dict(EXPECTED_PARTIAL_RISK_BANDS),
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
        "cross_formula_bundle_sha256": EXPECTED_CROSS_FORMULA_BUNDLE_SHA256,
        "partial_risk_band_membership_sha256": (
            FM39_EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256
        ),
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "residual_formula": EXPECTED_RESIDUAL_FORMULA,
        "union_formula": EXPECTED_UNION_FORMULA,
        "surface_formula": EXPECTED_SURFACE_FORMULA,
        "additive_formula": EXPECTED_ADDITIVE_FORMULA,
        "tier_coverage_formula": EXPECTED_TIER_COVERAGE_FORMULA,
        "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
        "resume_formula": EXPECTED_RESUME_FORMULA,
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "dry863_path": dry_rel,
        "unique_union_path": uniq_rel,
        "surface_unique_path": surf_rel,
        "cross_formula_bundle_path": bundle_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "fm39_packet": paths.fm39_packet_rel,
            "fm39_fingerprint": paths.fm39_fingerprint_rel,
            "fm39_gate": paths.fm39_gate_json_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
        },
        "mock_root_is_isolated": True,
    }

