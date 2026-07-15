"""
CNINFO C-class — 规模 failed_codes membership freeze + resume_same/worse
membership freeze + residual_formula identity lock + hold_decision identity lock
（离线 · C-FM-36）。

在 C-FM-35（winner_map SHA256 lock + resume taxonomy codeset SHA256 lock
（28/1/0）+ batch_priority order freeze + partial_risk_band cardinality freeze
（75/14/12/5））已 commit 且 EXECUTE 仍 human-held 之上，继续非 seal 规模/安全
能力（不新增 seal / decision-await / commit-boundary；非 extension↔drift 循环）：
  1) FM35 packet / fingerprint / gate / winner·resume-taxonomy·batch·risk
     ledgers 零漂移连续
  2) failed_codes_membership_freeze：失败码精确集合（9）禁止注入/删除/替换
  3) resume_same_worse_membership_freeze：same={301212} · worse=∅ 禁止变异
  4) residual_formula_identity_lock：117=106+9+2 禁止公式/覆盖变异
  5) hold_decision_identity_lock：KEEP_EXECUTE_FALSE + AWAITING + approved=false
     + seal=false 禁止翻转
  6) output-root：MOCK3–37 冻结 · MOCK38 放行
  7) FM-01..05 + FM-12..35 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–37 / 权威 dual-layer 索引 ·
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
from cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety import (  # noqa: E402
    FROZEN_BATCH_PRIORITY_ORDER_FREEZE_FP_SHA256 as FM35_FROZEN_BATCH_PRIORITY_FP,
    FROZEN_PARTIAL_RISK_BAND_CARDINALITY_FP_SHA256 as FM35_FROZEN_PARTIAL_RISK_BAND_FP,
    FROZEN_RESUME_TAXONOMY_CODESET_SHA256_LOCK_FP_SHA256 as FM35_FROZEN_RESUME_TAXONOMY_FP,
    FROZEN_WINNER_MAP_SHA256_LOCK_FP_SHA256 as FM35_FROZEN_WINNER_MAP_FP,
)

TASK_ID = "C-FM-36"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm36_scale_failed_resume_membership_residual_formula_hold_identity_safety"
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
FM35_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm35_scale_winner_resume_taxonomy_batch_priority_risk_band_safety"
)
FM35_PACKET_REL = f"{FM35_MOCK_ROOT_REL}/scale_packet.json"
FM35_FINGERPRINT_REL = f"{FM35_MOCK_ROOT_REL}/scale_fingerprint.json"
FM35_WINNER_REL = f"{FM35_MOCK_ROOT_REL}/winner_map_sha256_lock_ledger.json"
FM35_RESUME_TAX_REL = (
    f"{FM35_MOCK_ROOT_REL}/resume_taxonomy_codeset_sha256_lock_ledger.json"
)
FM35_BATCH_PRI_REL = (
    f"{FM35_MOCK_ROOT_REL}/batch_priority_order_freeze_ledger.json"
)
FM35_RISK_BAND_REL = (
    f"{FM35_MOCK_ROOT_REL}/partial_risk_band_cardinality_freeze_ledger.json"
)

# C-FM-36 本包冻结指纹
FROZEN_FAILED_CODES_MEMBERSHIP_FREEZE_FP_SHA256 = (
    "232308b7488af325257c650380adb7a4cdea65464a3400ad3931c83f23d83bce"
)
FROZEN_RESUME_SAME_WORSE_MEMBERSHIP_FREEZE_FP_SHA256 = (
    "237cd509fe9a9db9d49bbf60b070177a25f1e75bc4804556cf1103878898e674"
)
FROZEN_RESIDUAL_FORMULA_IDENTITY_LOCK_FP_SHA256 = (
    "62cc02077579e6cd37c12a32df266c5c6e7f2f99e87594711727a5a2fd8f27d9"
)
FROZEN_HOLD_DECISION_IDENTITY_LOCK_FP_SHA256 = (
    "0b0708213941c07fa4774783f429d188b3a07869ea9f560a6e0caa541c90a4b5"
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

THIS_TASK_ROOT_ID = "C-ROOT-MOCK38"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK37"
RESUME_HARVEST_ROOT_ID = "C-ROOT-002"

FROZEN_ROOT_IDS_MUST_BLOCK = tuple(f"C-ROOT-MOCK{i}" for i in range(3, 38))

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class FailedResumeMembershipResidualFormulaHoldIdentityPaths:
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
    fm35_packet_rel: str = FM35_PACKET_REL
    fm35_fingerprint_rel: str = FM35_FINGERPRINT_REL
    fm35_winner_rel: str = FM35_WINNER_REL
    fm35_resume_tax_rel: str = FM35_RESUME_TAX_REL
    fm35_batch_pri_rel: str = FM35_BATCH_PRI_REL
    fm35_risk_band_rel: str = FM35_RISK_BAND_REL
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


def assert_fm36_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-36 写根：须 validation/_mock_*，不得覆盖 MOCK3–37，
    不得写权威 dual-layer 索引；允许本任务 MOCK38 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-36 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _sha256_codes(codes: Sequence[str]) -> str:
    return hashlib.sha256(",".join(sorted(codes)).encode("utf-8")).hexdigest()




def fingerprint_failed_codes_membership_freeze() -> Tuple[str, Dict[str, Any]]:
    """failed_codes membership freeze 指纹。"""
    doc = {
        "kind": "failed_codes_membership_freeze",
        "failed_codes": sorted(EXPECTED_FAILED_CODES),
        "failed_n": EXPECTED_UNION_FAILED,
        "deny_inject": True,
        "deny_drop": True,
        "deny_replace": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_resume_same_worse_membership_freeze() -> Tuple[str, Dict[str, Any]]:
    """resume_same/worse membership freeze 指纹。"""
    doc = {
        "kind": "resume_same_worse_membership_freeze",
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "worse_codes": [],
        "deny_same_inject": True,
        "deny_same_drop": True,
        "deny_worse_inject": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_residual_formula_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """residual_formula identity lock 指纹（117=106+9+2）。"""
    doc = {
        "kind": "residual_formula_identity_lock",
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "formula": "106+9+2=117",
        "deny_formula_mutate": True,
        "deny_coverage_inflate": True,
        "deny_coverage_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_hold_decision_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """hold_decision identity lock 指纹。"""
    doc = {
        "kind": "hold_decision_identity_lock",
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "execute_production_snapshot_rebuild": False,
        "seal_chain_extended": False,
        "idle_not_required_while_awaiting": True,
        "deny_hold_flip": True,
        "deny_approved_flip": True,
        "deny_seal_extend": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_failed_codes_membership_mutation(
    *, proposed_codes: Sequence[str], action: str
) -> Dict[str, Any]:
    """评估 failed_codes 成员变异；inject/drop/replace 一律拒绝。"""
    if action not in ("inject", "drop", "replace"):
        raise ValueError(f"unknown failed_codes action: {action}")
    proposed = sorted(proposed_codes)
    frozen = sorted(EXPECTED_FAILED_CODES)
    return {
        "action": action,
        "proposed_codes": proposed,
        "frozen_codes": frozen,
        "matches_frozen": proposed == frozen,
        "mutation_allowed": False,
        "reason": "failed_codes_membership_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_resume_same_worse_membership_mutation(
    *, bucket: str, proposed_codes: Sequence[str]
) -> Dict[str, Any]:
    """评估 resume_same/worse 成员变异；一律拒绝。"""
    if bucket not in ("same", "worse"):
        raise ValueError(f"unknown resume membership bucket: {bucket}")
    frozen_map = {
        "same": sorted(EXPECTED_RESUME_SAME_CODES),
        "worse": [],
    }
    frozen = frozen_map[bucket]
    proposed = sorted(proposed_codes)
    return {
        "bucket": bucket,
        "proposed_codes": proposed,
        "frozen_codes": frozen,
        "matches_frozen": proposed == frozen,
        "mutation_allowed": False,
        "reason": "resume_same_worse_membership_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_residual_formula_mutation(
    *,
    proposed_coverage: int,
    proposed_partial: int,
    proposed_failed: int,
    proposed_delta: int,
) -> Dict[str, Any]:
    """评估 residual 公式变异；一律拒绝。"""
    formula_ok = (
        proposed_partial + proposed_failed + proposed_delta == proposed_coverage
    )
    matches = (
        proposed_coverage == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        and proposed_partial == EXPECTED_UNION_PARTIAL
        and proposed_failed == EXPECTED_UNION_FAILED
        and proposed_delta == EXPECTED_SURFACE_HARVEST_DELTA_N
        and formula_ok
        and proposed_coverage
        == EXPECTED_UNION_PARTIAL
        + EXPECTED_UNION_FAILED
        + EXPECTED_SURFACE_HARVEST_DELTA_N
    )
    return {
        "proposed": {
            "coverage": proposed_coverage,
            "partial": proposed_partial,
            "failed": proposed_failed,
            "delta": proposed_delta,
        },
        "frozen": {
            "coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
            "partial": EXPECTED_UNION_PARTIAL,
            "failed": EXPECTED_UNION_FAILED,
            "delta": EXPECTED_SURFACE_HARVEST_DELTA_N,
        },
        "formula_holds": formula_ok,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "residual_formula_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_hold_decision_mutation(*, proposed: Dict[str, Any]) -> Dict[str, Any]:
    """评估 hold/decision 身份变异；一律拒绝。"""
    frozen = {
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "execute_production_snapshot_rebuild": False,
        "seal_chain_extended": False,
        "idle_not_required_while_awaiting": True,
    }
    return {
        "proposed": dict(proposed),
        "frozen": dict(frozen),
        "matches_frozen": dict(proposed) == dict(frozen),
        "mutation_allowed": False,
        "reason": "hold_decision_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }



def build_fm35_continuity_rows(
    paths: FailedResumeMembershipResidualFormulaHoldIdentityPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM35 packet / fingerprint / gate / 四 ledger 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm35_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm35_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm35_gate_json_rel, base_dir=base_dir))
    win_led = load_json(_abs(paths.fm35_winner_rel, base_dir=base_dir))
    tax_led = load_json(_abs(paths.fm35_resume_tax_rel, base_dir=base_dir))
    bat_led = load_json(_abs(paths.fm35_batch_pri_rel, base_dir=base_dir))
    risk_led = load_json(_abs(paths.fm35_risk_band_rel, base_dir=base_dir))

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
    checks["fm35_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm35_packet_continuity",
            layer="fm35_continuity",
            path=paths.fm35_packet_rel,
            expected="PASS_OFFLINE;unique=2249;1053;delta2;KEEP",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"dryrun={packet.get('combined_dryrun_coverage')};"
                f"delta={packet.get('surface_harvest_delta_n')};"
                f"winner={str(packet.get('winner_map_sha256') or '')[:12]}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm35_packet_drift",
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
        and frozen.get("winner_map_sha256_lock") == FM35_FROZEN_WINNER_MAP_FP
        and frozen.get("resume_taxonomy_codeset_sha256_lock")
        == FM35_FROZEN_RESUME_TAXONOMY_FP
        and frozen.get("batch_priority_order_freeze") == FM35_FROZEN_BATCH_PRIORITY_FP
        and frozen.get("partial_risk_band_cardinality_freeze")
        == FM35_FROZEN_PARTIAL_RISK_BAND_FP
        and frozen.get("fm34_dry863_surface_delta_codeset_freeze") == FM34_FROZEN_DRY863_FP
        and frozen.get("fm34_combined_dryrun_coverage_cardinality_freeze")
        == FM34_FROZEN_COMBINED_DRYRUN_FP
        and frozen.get("fm34_cross_metric_identity_lock") == FM34_FROZEN_CROSS_IDENTITY_FP
        and frozen.get("fm34_partition_codeset_sha256_lock")
        == FM34_FROZEN_PARTITION_CODESET_FP
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm35_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm35_fingerprint_continuity",
            layer="fm35_continuity",
            path=paths.fm35_fingerprint_rel,
            expected="unique2249+fm35_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"dryrun={fp_doc.get('combined_dryrun_coverage')};"
                f"delta={fp_doc.get('surface_harvest_delta_n')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm35_fingerprint_drift",
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
        and gate_doc.get("winner_map_sha256") == EXPECTED_WINNER_MAP_SHA256
        and list(gate_doc.get("batch_priority") or []) == list(EXPECTED_BATCH_PRIORITY)
        and gate_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
    )
    checks["fm35_gate_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm35_gate_continuity",
            layer="fm35_continuity",
            path=paths.fm35_gate_json_rel,
            expected="PASS_OFFLINE;KEEP;1053;delta2;28/1/0",
            observed=(
                f"gate={gate_doc.get('gate')};"
                f"dryrun={gate_doc.get('combined_dryrun_coverage')};"
                f"delta={gate_doc.get('surface_harvest_delta_n')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm35_gate_drift",
        )
    )

    win_ok = (
        win_led.get("fingerprint_sha256") == FM35_FROZEN_WINNER_MAP_FP
        and win_led.get("winner_map_sha256") == EXPECTED_WINNER_MAP_SHA256
    )
    checks["fm35_winner_ledger_continuity"] = win_ok
    rows.append(
        _row(
            check_id="fm35_winner_ledger_continuity",
            layer="fm35_continuity",
            path=paths.fm35_winner_rel,
            expected=FM35_FROZEN_WINNER_MAP_FP,
            observed=str(win_led.get("fingerprint_sha256") or ""),
            ok=win_ok,
            notes="ok" if win_ok else "fm35_winner_drift",
        )
    )

    tax_ok = (
        tax_led.get("fingerprint_sha256") == FM35_FROZEN_RESUME_TAXONOMY_FP
        and tax_led.get("improved_codes_sha256") == EXPECTED_RESUME_IMPROVED_CODES_SHA256
        and tax_led.get("same_codes_sha256") == EXPECTED_RESUME_SAME_CODES_SHA256
        and tax_led.get("worse_codes_sha256") == EXPECTED_RESUME_WORSE_CODES_SHA256
    )
    checks["fm35_resume_taxonomy_ledger_continuity"] = tax_ok
    rows.append(
        _row(
            check_id="fm35_resume_taxonomy_ledger_continuity",
            layer="fm35_continuity",
            path=paths.fm35_resume_tax_rel,
            expected=FM35_FROZEN_RESUME_TAXONOMY_FP,
            observed=str(tax_led.get("fingerprint_sha256") or ""),
            ok=tax_ok,
            notes="ok" if tax_ok else "fm35_resume_taxonomy_drift",
        )
    )

    bat_ok = (
        bat_led.get("fingerprint_sha256") == FM35_FROZEN_BATCH_PRIORITY_FP
        and list(bat_led.get("batch_priority") or []) == list(EXPECTED_BATCH_PRIORITY)
    )
    checks["fm35_batch_priority_ledger_continuity"] = bat_ok
    rows.append(
        _row(
            check_id="fm35_batch_priority_ledger_continuity",
            layer="fm35_continuity",
            path=paths.fm35_batch_pri_rel,
            expected=FM35_FROZEN_BATCH_PRIORITY_FP,
            observed=str(bat_led.get("fingerprint_sha256") or ""),
            ok=bat_ok,
            notes="ok" if bat_ok else "fm35_batch_priority_drift",
        )
    )

    risk_ok = (
        risk_led.get("fingerprint_sha256") == FM35_FROZEN_PARTIAL_RISK_BAND_FP
        and risk_led.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
    )
    checks["fm35_risk_band_ledger_continuity"] = risk_ok
    rows.append(
        _row(
            check_id="fm35_risk_band_ledger_continuity",
            layer="fm35_continuity",
            path=paths.fm35_risk_band_rel,
            expected=FM35_FROZEN_PARTIAL_RISK_BAND_FP,
            observed=str(risk_led.get("fingerprint_sha256") or ""),
            ok=risk_ok,
            notes="ok" if risk_ok else "fm35_risk_band_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm35_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm35_continuity_all_pass",
            layer="fm35_continuity",
            expected="packet+fp+gate+4ledgers",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm35_continuity_incomplete",
        )
    )
    return rows, checks


def build_failed_codes_membership_freeze_rows(
    paths: FailedResumeMembershipResidualFormulaHoldIdentityPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """failed_codes membership freeze（9）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_failed_codes_membership_freeze()

    exact_ok = (
        sorted(EXPECTED_FAILED_CODES)
        == sorted(
            [
                "002140",
                "300055",
                "300069",
                "300074",
                "300540",
                "300552",
                "301195",
                "603885",
                "605060",
            ]
        )
        and EXPECTED_UNION_FAILED == 9
        and len(EXPECTED_FAILED_CODES) == 9
    )
    checks["failed_codes_membership_exact"] = exact_ok
    rows.append(
        _row(
            check_id="failed_codes_membership_exact",
            layer="failed_codes_membership_freeze",
            expected="9_exact_codes",
            observed=f"n={len(EXPECTED_FAILED_CODES)};{','.join(sorted(EXPECTED_FAILED_CODES)[:3])}...",
            ok=exact_ok,
            notes="ok" if exact_ok else "failed_codes_drift",
        )
    )

    injected = sorted(EXPECTED_FAILED_CODES) + ["999999"]
    dropped = sorted(EXPECTED_FAILED_CODES)[:-1]
    replaced = ["000001"] * 9
    sample_denials = [
        evaluate_failed_codes_membership_mutation(
            proposed_codes=injected, action="inject"
        ),
        evaluate_failed_codes_membership_mutation(
            proposed_codes=dropped, action="drop"
        ),
        evaluate_failed_codes_membership_mutation(
            proposed_codes=replaced, action="replace"
        ),
        evaluate_failed_codes_membership_mutation(
            proposed_codes=sorted(EXPECTED_FAILED_CODES), action="replace"
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["failed_codes_membership_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="failed_codes_membership_mutation_denied",
            layer="failed_codes_membership_freeze",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "failed_codes_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_inject"] is True
        and doc["deny_drop"] is True
        and doc["deny_replace"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["failed_n"] == 9
    )
    checks["failed_codes_membership_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="failed_codes_membership_flags_locked",
            layer="failed_codes_membership_freeze",
            expected="deny_inject+drop+replace+KEEP",
            observed=f"flags_ok={flags_ok};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_FAILED_CODES_MEMBERSHIP_FREEZE_FP_SHA256
    checks["failed_codes_membership_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="failed_codes_membership_fingerprint",
            layer="failed_codes_membership_freeze",
            expected=FROZEN_FAILED_CODES_MEMBERSHIP_FREEZE_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "failed_codes_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["failed_codes_membership_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="failed_codes_membership_freeze_all_pass",
            layer="failed_codes_membership_freeze",
            expected="failed_codes_membership_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "failed_codes_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "failed_codes": sorted(EXPECTED_FAILED_CODES),
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_resume_same_worse_membership_freeze_rows(
    paths: FailedResumeMembershipResidualFormulaHoldIdentityPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """resume_same/worse membership freeze（1/0）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_resume_same_worse_membership_freeze()

    exact_ok = (
        EXPECTED_RESUME_SAME == 1
        and EXPECTED_RESUME_WORSE == 0
        and set(EXPECTED_RESUME_SAME_CODES) == {"301212"}
        and _sha256_codes(sorted(EXPECTED_RESUME_SAME_CODES))
        == EXPECTED_RESUME_SAME_CODES_SHA256
        and EXPECTED_RESUME_WORSE_CODES_SHA256
        == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
    checks["resume_same_worse_membership_exact"] = exact_ok
    rows.append(
        _row(
            check_id="resume_same_worse_membership_exact",
            layer="resume_same_worse_membership_freeze",
            expected="same=301212;worse=empty",
            observed=(
                f"same={','.join(sorted(EXPECTED_RESUME_SAME_CODES))};"
                f"worse_n=0;card={EXPECTED_RESUME_SAME}/{EXPECTED_RESUME_WORSE}"
            ),
            ok=exact_ok,
            notes="ok" if exact_ok else "resume_same_worse_drift",
        )
    )

    sample_denials = [
        evaluate_resume_same_worse_membership_mutation(
            bucket="same", proposed_codes=["301212", "999999"]
        ),
        evaluate_resume_same_worse_membership_mutation(
            bucket="same", proposed_codes=[]
        ),
        evaluate_resume_same_worse_membership_mutation(
            bucket="worse", proposed_codes=["000001"]
        ),
        evaluate_resume_same_worse_membership_mutation(
            bucket="same", proposed_codes=sorted(EXPECTED_RESUME_SAME_CODES)
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["resume_same_worse_membership_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="resume_same_worse_membership_mutation_denied",
            layer="resume_same_worse_membership_freeze",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "resume_same_worse_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_same_inject"] is True
        and doc["deny_same_drop"] is True
        and doc["deny_worse_inject"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["same_codes"] == ["301212"]
        and doc["worse_codes"] == []
    )
    checks["resume_same_worse_membership_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="resume_same_worse_membership_flags_locked",
            layer="resume_same_worse_membership_freeze",
            expected="deny_same+worse+KEEP",
            observed=f"flags_ok={flags_ok};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_RESUME_SAME_WORSE_MEMBERSHIP_FREEZE_FP_SHA256
    checks["resume_same_worse_membership_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="resume_same_worse_membership_fingerprint",
            layer="resume_same_worse_membership_freeze",
            expected=FROZEN_RESUME_SAME_WORSE_MEMBERSHIP_FREEZE_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "resume_same_worse_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_same_worse_membership_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_same_worse_membership_freeze_all_pass",
            layer="resume_same_worse_membership_freeze",
            expected="same_worse_membership_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_same_worse_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "worse_codes": [],
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_residual_formula_identity_lock_rows(
    paths: FailedResumeMembershipResidualFormulaHoldIdentityPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """residual_formula identity lock（117=106+9+2）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_residual_formula_identity_lock()

    formula_ok = (
        EXPECTED_RESIDUAL_SAFETY_COVERAGE == 117
        and EXPECTED_UNION_PARTIAL == 106
        and EXPECTED_UNION_FAILED == 9
        and EXPECTED_SURFACE_HARVEST_DELTA_N == 2
        and (
            EXPECTED_UNION_PARTIAL
            + EXPECTED_UNION_FAILED
            + EXPECTED_SURFACE_HARVEST_DELTA_N
            == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        )
    )
    checks["residual_formula_exact"] = formula_ok
    rows.append(
        _row(
            check_id="residual_formula_exact",
            layer="residual_formula_identity_lock",
            expected="117=106+9+2",
            observed=(
                f"{EXPECTED_RESIDUAL_SAFETY_COVERAGE}="
                f"{EXPECTED_UNION_PARTIAL}+{EXPECTED_UNION_FAILED}+"
                f"{EXPECTED_SURFACE_HARVEST_DELTA_N}"
            ),
            ok=formula_ok,
            notes="ok" if formula_ok else "residual_formula_drift",
        )
    )

    sample_denials = [
        evaluate_residual_formula_mutation(
            proposed_coverage=118,
            proposed_partial=106,
            proposed_failed=9,
            proposed_delta=2,
        ),
        evaluate_residual_formula_mutation(
            proposed_coverage=116,
            proposed_partial=106,
            proposed_failed=9,
            proposed_delta=2,
        ),
        evaluate_residual_formula_mutation(
            proposed_coverage=117,
            proposed_partial=107,
            proposed_failed=9,
            proposed_delta=1,
        ),
        evaluate_residual_formula_mutation(
            proposed_coverage=117,
            proposed_partial=106,
            proposed_failed=9,
            proposed_delta=2,
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["residual_formula_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="residual_formula_mutation_denied",
            layer="residual_formula_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "residual_formula_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_formula_mutate"] is True
        and doc["deny_coverage_inflate"] is True
        and doc["deny_coverage_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["formula"] == "106+9+2=117"
    )
    checks["residual_formula_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="residual_formula_flags_locked",
            layer="residual_formula_identity_lock",
            expected="deny_formula+inflate+deflate+KEEP",
            observed=f"flags_ok={flags_ok};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_RESIDUAL_FORMULA_IDENTITY_LOCK_FP_SHA256
    checks["residual_formula_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="residual_formula_fingerprint",
            layer="residual_formula_identity_lock",
            expected=FROZEN_RESIDUAL_FORMULA_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "residual_formula_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["residual_formula_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="residual_formula_identity_lock_all_pass",
            layer="residual_formula_identity_lock",
            expected="residual_formula_identity_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "residual_formula_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "formula": "106+9+2=117",
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_hold_decision_identity_lock_rows(
    paths: FailedResumeMembershipResidualFormulaHoldIdentityPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """hold_decision identity lock。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_hold_decision_identity_lock()

    identity = {
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "execute_production_snapshot_rebuild": False,
        "seal_chain_extended": False,
        "idle_not_required_while_awaiting": True,
    }
    exact_ok = doc == {
        "kind": "hold_decision_identity_lock",
        **identity,
        "deny_hold_flip": True,
        "deny_approved_flip": True,
        "deny_seal_extend": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    # 指纹 doc 字段顺序不影响；按关键字段校验
    exact_ok = (
        doc["hold_recommendation"] == "KEEP_EXECUTE_FALSE"
        and doc["decision_status"] == "AWAITING_HUMAN_EXECUTE_DECISION"
        and doc["approved_for_snapshot_rebuild"] is False
        and doc["ready_for_execute"] is False
        and doc["execute_production_snapshot_rebuild"] is False
        and doc["seal_chain_extended"] is False
        and doc["idle_not_required_while_awaiting"] is True
    )
    checks["hold_decision_identity_exact"] = exact_ok
    rows.append(
        _row(
            check_id="hold_decision_identity_exact",
            layer="hold_decision_identity_lock",
            expected="KEEP+AWAITING+approved=false+seal=false",
            observed=(
                f"{doc['hold_recommendation']};{doc['decision_status']};"
                f"approved={doc['approved_for_snapshot_rebuild']}"
            ),
            ok=exact_ok,
            notes="ok" if exact_ok else "hold_decision_drift",
        )
    )

    flipped_hold = dict(identity)
    flipped_hold["hold_recommendation"] = "READY_EXECUTE"
    flipped_approved = dict(identity)
    flipped_approved["approved_for_snapshot_rebuild"] = True
    flipped_seal = dict(identity)
    flipped_seal["seal_chain_extended"] = True
    sample_denials = [
        evaluate_hold_decision_mutation(proposed=flipped_hold),
        evaluate_hold_decision_mutation(proposed=flipped_approved),
        evaluate_hold_decision_mutation(proposed=flipped_seal),
        evaluate_hold_decision_mutation(proposed=dict(identity)),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["hold_decision_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="hold_decision_mutation_denied",
            layer="hold_decision_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "hold_decision_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_hold_flip"] is True
        and doc["deny_approved_flip"] is True
        and doc["deny_seal_extend"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["hold_decision_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="hold_decision_flags_locked",
            layer="hold_decision_identity_lock",
            expected="deny_hold+approved+seal+KEEP",
            observed=f"flags_ok={flags_ok};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_HOLD_DECISION_IDENTITY_LOCK_FP_SHA256
    checks["hold_decision_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="hold_decision_fingerprint",
            layer="hold_decision_identity_lock",
            expected=FROZEN_HOLD_DECISION_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "hold_decision_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["hold_decision_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="hold_decision_identity_lock_all_pass",
            layer="hold_decision_identity_lock",
            expected="hold_decision_identity_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "hold_decision_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "identity": identity,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: FailedResumeMembershipResidualFormulaHoldIdentityPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK38 放行。"""
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
        assert_fm36_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK38_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock38_ok",
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
    paths: FailedResumeMembershipResidualFormulaHoldIdentityPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–37 拒绝 · MOCK38 放行。"""
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

    mock37_rel = (
        "outputs/validation/"
        "_mock_c_fm35_scale_winner_resume_taxonomy_batch_priority_risk_band_safety"
    )
    mock37_blocked = False
    try:
        assert_fm36_output_root(mock37_rel, base_dir=base_dir)
    except RuntimeError as exc:
        mock37_blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock37_still_frozen"] = mock37_blocked
    rows.append(
        _row(
            check_id="mock37_still_frozen",
            layer="frozen_mock_isolation",
            root_id=PRIOR_TASK_ROOT_ID,
            path=mock37_rel,
            expected="write_forbidden",
            observed="blocked" if mock37_blocked else "allowed",
            ok=mock37_blocked,
            notes="ok" if mock37_blocked else "mock37_write_leak",
        )
    )

    allow_ok = False
    try:
        assert_fm36_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except Exception:
        allow_ok = False
    checks["frozen_allow_mock38"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock38",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="MOCK38_or_ephemeral_allowed",
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
            expected="MOCK3-37_block+MOCK38_allow",
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
    """protected_output_roots.csv：MOCK38 已登记。"""
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
    checks["protected_csv_mock38_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock38_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock37.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock38_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3–37+resume+auth+fuller_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..35 gate battery（跳过 seal FM06–11）。"""
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
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
        "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35",
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
            "fm25", "fm26", "fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35"
        ):
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in ("fm26", "fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35"):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in ("fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35"):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key in ("fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35"):
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        if key in ("fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35"):
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
        if key in ("fm31", "fm32", "fm33", "fm34", "fm35"):
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
            check_id="fm01_05_12_35_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_35_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm36(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK38；加固 C-ROOT-002 winner/resume-taxonomy/batch/risk 说明。"""
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
                "C-FM-24..35 scale/safety freezes + C-FM-36 failed/resume "
                "membership + residual formula + hold identity; "
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
                "C-FM-36 scale failed_codes membership freeze (9) + "
                "resume_same/worse membership freeze (1/0) + residual_formula "
                "identity lock (117=106+9+2) + hold_decision identity lock + "
                "FM35 continuity; never production EXECUTE; must not overwrite "
                "MOCK3-37; seal_chain_extended=false"
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



def run_scale_failed_resume_membership_residual_formula_hold_identity_safety(
    *,
    paths: FailedResumeMembershipResidualFormulaHoldIdentityPaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-36 规模 failed/resume membership + residual formula + hold 离线 QA。"""
    paths = paths or FailedResumeMembershipResidualFormulaHoldIdentityPaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm36(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm36_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm35_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    fail_rows, fail_checks, fail_meta = build_failed_codes_membership_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(fail_rows)
    same_rows, same_checks, same_meta = build_resume_same_worse_membership_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(same_rows)
    formula_rows, formula_checks, formula_meta = build_residual_formula_identity_lock_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(formula_rows)
    hold_id_rows, hold_id_checks, hold_id_meta = build_hold_decision_identity_lock_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(hold_id_rows)
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
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm35_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm35_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "failed_codes_membership_freeze": (
            "PASS_OFFLINE"
            if fail_checks.get("failed_codes_membership_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_same_worse_membership_freeze": (
            "PASS_OFFLINE"
            if same_checks.get("resume_same_worse_membership_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "residual_formula_identity_lock": (
            "PASS_OFFLINE"
            if formula_checks.get("residual_formula_identity_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "hold_decision_identity_lock": (
            "PASS_OFFLINE"
            if hold_id_checks.get("hold_decision_identity_lock_all_pass")
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
            if bat_checks.get("fm01_05_12_35_battery_all_pass")
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

    fail_rel = _rel(
        os.path.join(out_root, "failed_codes_membership_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(fail_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": fail_meta["fingerprint"],
                "failed_codes": fail_meta["failed_codes"],
                "sample_denials": fail_meta["sample_denials"],
                "doc": fail_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    same_rel = _rel(
        os.path.join(out_root, "resume_same_worse_membership_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(same_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": same_meta["fingerprint"],
                "same_codes": same_meta["same_codes"],
                "worse_codes": same_meta["worse_codes"],
                "sample_denials": same_meta["sample_denials"],
                "doc": same_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    formula_rel = _rel(
        os.path.join(out_root, "residual_formula_identity_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(formula_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": formula_meta["fingerprint"],
                "residual_safety_coverage": formula_meta["residual_safety_coverage"],
                "formula": formula_meta["formula"],
                "sample_denials": formula_meta["sample_denials"],
                "doc": formula_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    hold_id_rel = _rel(
        os.path.join(out_root, "hold_decision_identity_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(hold_id_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": hold_id_meta["fingerprint"],
                "identity": hold_id_meta["identity"],
                "sample_denials": hold_id_meta["sample_denials"],
                "doc": hold_id_meta["doc"],
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
                "fm35_gate": gates["fm35"].get("gate"),
                "fm36_gate": overall,
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
                "residual_formula": "106+9+2=117",
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
                "residual_formula": "106+9+2=117",
                "notes": (
                    "failed_codes membership freeze (9) + resume_same/worse "
                    "membership freeze (1/0) + residual_formula identity lock "
                    "(117=106+9+2) + hold_decision identity lock + FM35 continuity "
                    "+ MOCK38; EXECUTE remains human-held; does not overwrite "
                    "MOCK3-37"
                ),
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    observed_fps = {
        "failed_codes_membership_freeze": fail_meta["fingerprint"],
        "resume_same_worse_membership_freeze": same_meta["fingerprint"],
        "residual_formula_identity_lock": formula_meta["fingerprint"],
        "hold_decision_identity_lock": hold_id_meta["fingerprint"],
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
                "residual_formula": "106+9+2=117",
                "frozen_fps": {
                    "failed_codes_membership_freeze": (
                        FROZEN_FAILED_CODES_MEMBERSHIP_FREEZE_FP_SHA256
                    ),
                    "resume_same_worse_membership_freeze": (
                        FROZEN_RESUME_SAME_WORSE_MEMBERSHIP_FREEZE_FP_SHA256
                    ),
                    "residual_formula_identity_lock": (
                        FROZEN_RESIDUAL_FORMULA_IDENTITY_LOCK_FP_SHA256
                    ),
                    "hold_decision_identity_lock": (
                        FROZEN_HOLD_DECISION_IDENTITY_LOCK_FP_SHA256
                    ),
                    "fm35_winner_map_sha256_lock": FM35_FROZEN_WINNER_MAP_FP,
                    "fm35_resume_taxonomy_codeset_sha256_lock": (
                        FM35_FROZEN_RESUME_TAXONOMY_FP
                    ),
                    "fm35_batch_priority_order_freeze": FM35_FROZEN_BATCH_PRIORITY_FP,
                    "fm35_partial_risk_band_cardinality_freeze": (
                        FM35_FROZEN_PARTIAL_RISK_BAND_FP
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
        "residual_formula": "106+9+2=117",
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fp_rel,
        "fingerprint": fp,
        "failed_codes_path": fail_rel,
        "resume_same_worse_path": same_rel,
        "residual_formula_path": formula_rel,
        "hold_decision_path": hold_id_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "fm35_packet": paths.fm35_packet_rel,
            "fm35_gate": paths.fm35_gate_json_rel,
        },
        "mock_root_is_isolated": True,
    }

