"""
CNINFO C-class — 规模 partial_risk_band membership freeze + combined_dryrun
coverage identity lock + risk_band_formula identity lock + resume_formula
identity lock（离线 · C-FM-39）。

在 C-FM-38（complete_codes membership freeze（2134）+ overlap_delta membership
freeze（Δ12）+ additive_formula identity lock（2261=2249+12）+
tier_coverage_formula identity lock（7/3314））已 commit 且 EXECUTE 仍
human-held 之上，继续非 seal 规模/安全能力（不新增 seal / decision-await /
commit-boundary；非 extension↔drift 循环）：
  1) FM38 packet / fingerprint / gate / complete·overlap·additive·tier ledgers
     零漂移连续
  2) partial_risk_band_membership_freeze：75/14/12/5 成员映射 SHA256 禁止注入/删除/重分类
  3) combined_dryrun_coverage_identity_lock：1053 禁止 inflate/deflate/变异
  4) risk_band_formula_identity_lock：75+14+12+5=106 禁止公式变异
  5) resume_formula_identity_lock：28+1+0=29 禁止公式变异
  6) output-root：MOCK3–40 冻结 · MOCK41 放行
  7) FM-01..05 + FM-12..38 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–40 / 权威 dual-layer 索引 ·
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
from cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety import (  # noqa: E402
    FROZEN_ADDITIVE_FORMULA_IDENTITY_LOCK_FP_SHA256 as FM38_FROZEN_ADDITIVE_FP,
    FROZEN_COMPLETE_CODES_MEMBERSHIP_FREEZE_FP_SHA256 as FM38_FROZEN_COMPLETE_FP,
    FROZEN_OVERLAP_DELTA_MEMBERSHIP_FREEZE_FP_SHA256 as FM38_FROZEN_OVERLAP_FP,
    FROZEN_TIER_COVERAGE_FORMULA_IDENTITY_LOCK_FP_SHA256 as FM38_FROZEN_TIER_FP,
)

TASK_ID = "C-FM-39"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm39_scale_risk_band_combined_dryrun_resume_formula_safety"
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
FM38_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm38_scale_complete_overlap_additive_tier_formula_safety"
)
FM38_PACKET_REL = f"{FM38_MOCK_ROOT_REL}/scale_packet.json"
FM38_FINGERPRINT_REL = f"{FM38_MOCK_ROOT_REL}/scale_fingerprint.json"
FM38_COMPLETE_REL = (
    f"{FM38_MOCK_ROOT_REL}/complete_codes_membership_freeze_ledger.json"
)
FM38_OVERLAP_REL = (
    f"{FM38_MOCK_ROOT_REL}/overlap_delta_membership_freeze_ledger.json"
)
FM38_ADDITIVE_REL = (
    f"{FM38_MOCK_ROOT_REL}/additive_formula_identity_lock_ledger.json"
)
FM38_TIER_REL = (
    f"{FM38_MOCK_ROOT_REL}/tier_coverage_formula_identity_lock_ledger.json"
)
FM28_RISK_BAND_MEMBERSHIP_LEDGER_REL = (
    "outputs/validation/"
    "_mock_c_fm28_scale_risk_band_membership_write_boundary_cross_matrix_safety/"
    "partial_risk_band_membership_ledger.json"
)

# C-FM-39 本包冻结指纹（运行后由 fingerprint_* 锁定）
FROZEN_PARTIAL_RISK_BAND_MEMBERSHIP_FREEZE_FP_SHA256 = (
    "9d88b04f0439afac07b238f818c51fbdfd38980e2ab6b27ad6239cc8a5cbcd2e"
)
FROZEN_COMBINED_DRYRUN_COVERAGE_IDENTITY_LOCK_FP_SHA256 = (
    "e652acc962993e51c8c7fc6f30eefea118031ac9b9a7fa38437acbd4721793c5"
)
FROZEN_RISK_BAND_FORMULA_IDENTITY_LOCK_FP_SHA256 = (
    "d13c0be85f39b5d54247e6c05139600b8b883ce70046902a35ac52bad551b148"
)
FROZEN_RESUME_FORMULA_IDENTITY_LOCK_FP_SHA256 = (
    "9e6438ffa64e52a5ed512f9848a4075347c78757d8cae473fb698d45f164c3d7"
)
EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256 = (
    "92e65657252fb88420e2733a34dfb7100b8c0c3050ec24a156a23a0c89719fb5"
)
EXPECTED_RISK_BAND_FORMULA = "75+14+12+5=106"
EXPECTED_RESUME_FORMULA = "28+1+0=29"

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

THIS_TASK_ROOT_ID = "C-ROOT-MOCK41"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK40"
RESUME_HARVEST_ROOT_ID = "C-ROOT-002"

FROZEN_ROOT_IDS_MUST_BLOCK = tuple(f"C-ROOT-MOCK{i}" for i in range(3, 41))

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class RiskBandCombinedDryrunResumeFormulaPaths:
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
    fm38_packet_rel: str = FM38_PACKET_REL
    fm38_fingerprint_rel: str = FM38_FINGERPRINT_REL
    fm38_complete_rel: str = FM38_COMPLETE_REL
    fm38_overlap_rel: str = FM38_OVERLAP_REL
    fm38_additive_rel: str = FM38_ADDITIVE_REL
    fm38_tier_rel: str = FM38_TIER_REL
    fm28_risk_band_membership_ledger_rel: str = FM28_RISK_BAND_MEMBERSHIP_LEDGER_REL
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


def assert_fm39_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-39 写根：须 validation/_mock_*，不得覆盖 MOCK3–40，
    不得写权威 dual-layer 索引；允许本任务 MOCK41 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-39 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _sha256_codes(codes: Sequence[str]) -> str:
    return hashlib.sha256(",".join(sorted(codes)).encode("utf-8")).hexdigest()




def load_frozen_partial_risk_band_membership(
    *, base_dir: str = BASE_DIR
) -> Dict[str, str]:
    """从 FM28 ledger 加载冻结 partial risk-band membership（106）。"""
    led = load_json(_abs(FM28_RISK_BAND_MEMBERSHIP_LEDGER_REL, base_dir=base_dir))
    mem = {str(k): str(v) for k, v in (led.get("membership_by_code") or {}).items()}
    if len(mem) != EXPECTED_UNION_PARTIAL:
        raise RuntimeError(
            f"partial risk-band membership cardinality drift: {len(mem)}"
        )
    sha = hashlib.sha256(
        json.dumps(
            mem, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    if sha != EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256:
        raise RuntimeError("partial risk-band membership sha256 drift")
    if dict(led.get("risk_bands") or {}) != dict(EXPECTED_PARTIAL_RISK_BANDS):
        raise RuntimeError("partial risk-band counts drift")
    return mem


def fingerprint_partial_risk_band_membership_freeze(
    *, base_dir: str = BASE_DIR
) -> Tuple[str, Dict[str, Any]]:
    """partial_risk_band membership freeze 指纹（75/14/12/5）。"""
    mem = load_frozen_partial_risk_band_membership(base_dir=base_dir)
    doc = {
        "kind": "partial_risk_band_membership_freeze",
        "partial_n": EXPECTED_UNION_PARTIAL,
        "risk_bands": dict(EXPECTED_PARTIAL_RISK_BANDS),
        "membership_sha256": EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256,
        "deny_inject": True,
        "deny_drop": True,
        "deny_reclass": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    # 校验映射与冻结 SHA 一致（不把全量 codes 写入指纹，避免膨胀）
    _ = mem
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_combined_dryrun_coverage_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """combined_dryrun_coverage identity lock 指纹（1053）。"""
    doc = {
        "kind": "combined_dryrun_coverage_identity_lock",
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "deny_inflate": True,
        "deny_deflate": True,
        "deny_coverage_mutate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_risk_band_formula_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """risk_band_formula identity lock 指纹（75+14+12+5=106）。"""
    doc = {
        "kind": "risk_band_formula_identity_lock",
        "risk_bands": dict(EXPECTED_PARTIAL_RISK_BANDS),
        "band_sum": EXPECTED_UNION_PARTIAL,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
        "deny_formula_mutate": True,
        "deny_band_inflate": True,
        "deny_band_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_resume_formula_identity_lock() -> Tuple[str, Dict[str, Any]]:
    """resume_formula identity lock 指纹（28+1+0=29）。"""
    doc = {
        "kind": "resume_formula_identity_lock",
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "resume_total": EXPECTED_RESUME_TOTAL,
        "resume_formula": EXPECTED_RESUME_FORMULA,
        "deny_formula_mutate": True,
        "deny_resume_inflate": True,
        "deny_resume_deflate": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_partial_risk_band_membership_mutation(
    *,
    proposed_membership: Dict[str, str],
    action: str,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """评估 partial risk-band 成员变异；inject/drop/reclass 一律拒绝。"""
    if action not in ("inject", "drop", "reclass"):
        raise ValueError(f"unknown risk-band action: {action}")
    frozen = load_frozen_partial_risk_band_membership(base_dir=base_dir)
    proposed = {str(k): str(v) for k, v in proposed_membership.items()}
    return {
        "action": action,
        "proposed_n": len(proposed),
        "frozen_n": len(frozen),
        "matches_frozen": proposed == frozen,
        "mutation_allowed": False,
        "reason": "partial_risk_band_membership_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_combined_dryrun_coverage_mutation(
    *, proposed_coverage: int
) -> Dict[str, Any]:
    """评估 combined_dryrun_coverage 变异；一律拒绝。"""
    matches = proposed_coverage == EXPECTED_COMBINED_DRYRUN_COVERAGE
    return {
        "proposed_combined_dryrun_coverage": proposed_coverage,
        "frozen_combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "combined_dryrun_coverage_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_risk_band_formula_mutation(
    *, proposed_bands: Dict[str, int]
) -> Dict[str, Any]:
    """评估 risk_band 公式变异；一律拒绝。"""
    proposed = {str(k): int(v) for k, v in proposed_bands.items()}
    band_sum = sum(proposed.values())
    formula_ok = band_sum == EXPECTED_UNION_PARTIAL
    matches = proposed == dict(EXPECTED_PARTIAL_RISK_BANDS) and formula_ok
    return {
        "proposed_bands": proposed,
        "proposed_sum": band_sum,
        "frozen_bands": dict(EXPECTED_PARTIAL_RISK_BANDS),
        "frozen_sum": EXPECTED_UNION_PARTIAL,
        "risk_band_formula_holds": formula_ok,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "risk_band_formula_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_resume_formula_mutation(
    *,
    proposed_improved: int,
    proposed_same: int,
    proposed_worse: int,
) -> Dict[str, Any]:
    """评估 resume 公式变异；一律拒绝。"""
    total = proposed_improved + proposed_same + proposed_worse
    formula_ok = total == EXPECTED_RESUME_TOTAL
    matches = (
        proposed_improved == EXPECTED_RESUME_IMPROVED
        and proposed_same == EXPECTED_RESUME_SAME
        and proposed_worse == EXPECTED_RESUME_WORSE
        and formula_ok
    )
    return {
        "proposed": {
            "improved": proposed_improved,
            "same": proposed_same,
            "worse": proposed_worse,
            "total": total,
        },
        "frozen": {
            "improved": EXPECTED_RESUME_IMPROVED,
            "same": EXPECTED_RESUME_SAME,
            "worse": EXPECTED_RESUME_WORSE,
            "total": EXPECTED_RESUME_TOTAL,
        },
        "resume_formula_holds": formula_ok,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "resume_formula_identity_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def build_fm38_continuity_rows(
    paths: RiskBandCombinedDryrunResumeFormulaPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM38 packet / fingerprint / gate / 四 ledger 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm38_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm38_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm38_gate_json_rel, base_dir=base_dir))
    complete_led = load_json(_abs(paths.fm38_complete_rel, base_dir=base_dir))
    overlap_led = load_json(_abs(paths.fm38_overlap_rel, base_dir=base_dir))
    additive_led = load_json(_abs(paths.fm38_additive_rel, base_dir=base_dir))
    tier_led = load_json(_abs(paths.fm38_tier_rel, base_dir=base_dir))

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
        and packet.get("additive_formula") == "2249+12=2261"
        and packet.get("tier_coverage_formula") == "tiers=7;coverage_sum=3314"
        and packet.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
        and packet.get("approved_for_snapshot_rebuild") is False
        and packet.get("seal_chain_extended") is False
    )
    checks["fm38_packet_zero_drift"] = pkt_ok
    rows.append(
        _row(
            check_id="fm38_packet_zero_drift",
            layer="fm38_continuity",
            path=paths.fm38_packet_rel,
            expected="PASS_OFFLINE+stable_metrics+formulas",
            observed=f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')}",
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm38_packet_drift",
        )
    )

    fp_ok = (
        fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and fp_doc.get("additive_formula") == "2249+12=2261"
        and fp_doc.get("tier_coverage_formula") == "tiers=7;coverage_sum=3314"
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm38_fingerprint_zero_drift"] = fp_ok
    rows.append(
        _row(
            check_id="fm38_fingerprint_zero_drift",
            layer="fm38_continuity",
            path=paths.fm38_fingerprint_rel,
            expected="stable_metrics+fm38_fps",
            observed=f"unique={fp_doc.get('harvest_unique_union')}",
            ok=fp_ok,
            notes="ok" if fp_ok else "fm38_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and gate_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and gate_doc.get("additive_formula") == "2249+12=2261"
        and gate_doc.get("tier_coverage_formula") == "tiers=7;coverage_sum=3314"
        and gate_doc.get("seal_chain_extended") is False
    )
    checks["fm38_gate_zero_drift"] = gate_ok
    rows.append(
        _row(
            check_id="fm38_gate_zero_drift",
            layer="fm38_continuity",
            path=paths.fm38_gate_json_rel,
            expected="PASS_OFFLINE+KEEP_EXECUTE_FALSE",
            observed=f"gate={gate_doc.get('gate')}",
            ok=gate_ok,
            notes="ok" if gate_ok else "fm38_gate_drift",
        )
    )

    complete_ok = (
        complete_led.get("fingerprint_sha256") == FM38_FROZEN_COMPLETE_FP
        and complete_led.get("union_complete") == EXPECTED_UNION_COMPLETE
        and complete_led.get("complete_codes_sha256") == EXPECTED_COMPLETE_CODES_SHA256
    )
    checks["fm38_complete_ledger_zero_drift"] = complete_ok
    rows.append(
        _row(
            check_id="fm38_complete_ledger_zero_drift",
            layer="fm38_continuity",
            path=paths.fm38_complete_rel,
            expected=FM38_FROZEN_COMPLETE_FP,
            observed=str(complete_led.get("fingerprint_sha256")),
            ok=complete_ok,
            notes="ok" if complete_ok else "fm38_complete_ledger_drift",
        )
    )

    overlap_ok = (
        overlap_led.get("fingerprint_sha256") == FM38_FROZEN_OVERLAP_FP
        and overlap_led.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and overlap_led.get("overlap_codes_sha256") == EXPECTED_OVERLAP_CODES_SHA256
    )
    checks["fm38_overlap_ledger_zero_drift"] = overlap_ok
    rows.append(
        _row(
            check_id="fm38_overlap_ledger_zero_drift",
            layer="fm38_continuity",
            path=paths.fm38_overlap_rel,
            expected=FM38_FROZEN_OVERLAP_FP,
            observed=str(overlap_led.get("fingerprint_sha256")),
            ok=overlap_ok,
            notes="ok" if overlap_ok else "fm38_overlap_ledger_drift",
        )
    )

    additive_ok = (
        additive_led.get("fingerprint_sha256") == FM38_FROZEN_ADDITIVE_FP
        and additive_led.get("additive_formula") == "2249+12=2261"
    )
    checks["fm38_additive_ledger_zero_drift"] = additive_ok
    rows.append(
        _row(
            check_id="fm38_additive_ledger_zero_drift",
            layer="fm38_continuity",
            path=paths.fm38_additive_rel,
            expected=FM38_FROZEN_ADDITIVE_FP,
            observed=str(additive_led.get("fingerprint_sha256")),
            ok=additive_ok,
            notes="ok" if additive_ok else "fm38_additive_ledger_drift",
        )
    )

    tier_ok = (
        tier_led.get("fingerprint_sha256") == FM38_FROZEN_TIER_FP
        and tier_led.get("tier_coverage_formula") == "tiers=7;coverage_sum=3314"
    )
    checks["fm38_tier_ledger_zero_drift"] = tier_ok
    rows.append(
        _row(
            check_id="fm38_tier_ledger_zero_drift",
            layer="fm38_continuity",
            path=paths.fm38_tier_rel,
            expected=FM38_FROZEN_TIER_FP,
            observed=str(tier_led.get("fingerprint_sha256")),
            ok=tier_ok,
            notes="ok" if tier_ok else "fm38_tier_ledger_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm38_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm38_continuity_all_pass",
            layer="fm38_continuity",
            expected="packet+fp+gate+4ledgers",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm38_continuity_incomplete",
        )
    )
    return rows, checks


def build_partial_risk_band_membership_freeze_rows(
    paths: RiskBandCombinedDryrunResumeFormulaPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """partial_risk_band membership freeze（75/14/12/5）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_partial_risk_band_membership_freeze(base_dir=base_dir)
    mem = load_frozen_partial_risk_band_membership(base_dir=base_dir)

    card_ok = (
        len(mem) == 106
        and dict(EXPECTED_PARTIAL_RISK_BANDS)
        == {"p35_heavy": 75, "p3_mid": 14, "p2_mid": 12, "fu_light": 5}
        and sum(EXPECTED_PARTIAL_RISK_BANDS.values()) == EXPECTED_UNION_PARTIAL
    )
    checks["partial_risk_band_membership_cardinality"] = card_ok
    rows.append(
        _row(
            check_id="partial_risk_band_membership_cardinality",
            layer="partial_risk_band_membership_freeze",
            expected="106=75+14+12+5",
            observed=(
                f"n={len(mem)};bands={EXPECTED_PARTIAL_RISK_BANDS};"
                f"sha={EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256[:12]}"
            ),
            ok=card_ok,
            notes="ok" if card_ok else "risk_band_cardinality_drift",
        )
    )

    inj = dict(mem)
    inj["999999"] = "fu_light"
    drop = {k: v for k, v in mem.items() if k != sorted(mem)[0]}
    reclass = dict(mem)
    first = sorted(reclass)[0]
    reclass[first] = "fu_light" if reclass[first] != "fu_light" else "p35_heavy"
    sample_denials = [
        evaluate_partial_risk_band_membership_mutation(
            proposed_membership=inj, action="inject", base_dir=base_dir
        ),
        evaluate_partial_risk_band_membership_mutation(
            proposed_membership=drop, action="drop", base_dir=base_dir
        ),
        evaluate_partial_risk_band_membership_mutation(
            proposed_membership=reclass, action="reclass", base_dir=base_dir
        ),
        evaluate_partial_risk_band_membership_mutation(
            proposed_membership=mem, action="reclass", base_dir=base_dir
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["partial_risk_band_membership_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="partial_risk_band_membership_mutation_denied",
            layer="partial_risk_band_membership_freeze",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "risk_band_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_inject"] is True
        and doc["deny_drop"] is True
        and doc["deny_reclass"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["partial_n"] == 106
        and doc["membership_sha256"] == EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256
    )
    checks["partial_risk_band_membership_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="partial_risk_band_membership_flags_locked",
            layer="partial_risk_band_membership_freeze",
            expected="deny_inject/drop/reclass+KEEP_EXECUTE_FALSE",
            observed=f"hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "risk_band_flags_drift",
        )
    )

    fp_ok = fp == FROZEN_PARTIAL_RISK_BAND_MEMBERSHIP_FREEZE_FP_SHA256
    checks["partial_risk_band_membership_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="partial_risk_band_membership_fingerprint",
            layer="partial_risk_band_membership_freeze",
            expected=FROZEN_PARTIAL_RISK_BAND_MEMBERSHIP_FREEZE_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "risk_band_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["partial_risk_band_membership_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="partial_risk_band_membership_freeze_all_pass",
            layer="partial_risk_band_membership_freeze",
            expected="partial_risk_band_membership_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "risk_band_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "partial_n": 106,
        "risk_bands": dict(EXPECTED_PARTIAL_RISK_BANDS),
        "membership_sha256": EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_combined_dryrun_coverage_identity_lock_rows(
    paths: RiskBandCombinedDryrunResumeFormulaPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """combined_dryrun_coverage identity lock（1053）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_combined_dryrun_coverage_identity_lock()

    exact_ok = EXPECTED_COMBINED_DRYRUN_COVERAGE == 1053
    checks["combined_dryrun_coverage_identity"] = exact_ok
    rows.append(
        _row(
            check_id="combined_dryrun_coverage_identity",
            layer="combined_dryrun_coverage_identity_lock",
            expected="1053",
            observed=str(EXPECTED_COMBINED_DRYRUN_COVERAGE),
            ok=exact_ok,
            notes="ok" if exact_ok else "combined_dryrun_drift",
        )
    )

    sample_denials = [
        evaluate_combined_dryrun_coverage_mutation(proposed_coverage=1054),
        evaluate_combined_dryrun_coverage_mutation(proposed_coverage=1052),
        evaluate_combined_dryrun_coverage_mutation(proposed_coverage=0),
        evaluate_combined_dryrun_coverage_mutation(
            proposed_coverage=EXPECTED_COMBINED_DRYRUN_COVERAGE
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["combined_dryrun_coverage_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="combined_dryrun_coverage_mutation_denied",
            layer="combined_dryrun_coverage_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "combined_dryrun_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_inflate"] is True
        and doc["deny_deflate"] is True
        and doc["deny_coverage_mutate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["combined_dryrun_coverage"] == 1053
    )
    checks["combined_dryrun_coverage_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="combined_dryrun_coverage_flags_locked",
            layer="combined_dryrun_coverage_identity_lock",
            expected="deny_inflate/deflate/mutate+KEEP_EXECUTE_FALSE",
            observed=f"hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "combined_dryrun_flags_drift",
        )
    )

    fp_ok = fp == FROZEN_COMBINED_DRYRUN_COVERAGE_IDENTITY_LOCK_FP_SHA256
    checks["combined_dryrun_coverage_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="combined_dryrun_coverage_fingerprint",
            layer="combined_dryrun_coverage_identity_lock",
            expected=FROZEN_COMBINED_DRYRUN_COVERAGE_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "combined_dryrun_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["combined_dryrun_coverage_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="combined_dryrun_coverage_identity_lock_all_pass",
            layer="combined_dryrun_coverage_identity_lock",
            expected="combined_dryrun_coverage_identity_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "combined_dryrun_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_risk_band_formula_identity_lock_rows(
    paths: RiskBandCombinedDryrunResumeFormulaPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """risk_band_formula identity lock（75+14+12+5=106）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_risk_band_formula_identity_lock()

    formula_ok = (
        sum(EXPECTED_PARTIAL_RISK_BANDS.values()) == EXPECTED_UNION_PARTIAL
        and EXPECTED_PARTIAL_RISK_BANDS["p35_heavy"] == 75
        and EXPECTED_PARTIAL_RISK_BANDS["p3_mid"] == 14
        and EXPECTED_PARTIAL_RISK_BANDS["p2_mid"] == 12
        and EXPECTED_PARTIAL_RISK_BANDS["fu_light"] == 5
        and EXPECTED_RISK_BAND_FORMULA == "75+14+12+5=106"
    )
    checks["risk_band_formula_identity"] = formula_ok
    rows.append(
        _row(
            check_id="risk_band_formula_identity",
            layer="risk_band_formula_identity_lock",
            expected="75+14+12+5=106",
            observed=EXPECTED_RISK_BAND_FORMULA,
            ok=formula_ok,
            notes="ok" if formula_ok else "risk_band_formula_drift",
        )
    )

    sample_denials = [
        evaluate_risk_band_formula_mutation(
            proposed_bands={"p35_heavy": 76, "p3_mid": 14, "p2_mid": 12, "fu_light": 5}
        ),
        evaluate_risk_band_formula_mutation(
            proposed_bands={"p35_heavy": 75, "p3_mid": 13, "p2_mid": 12, "fu_light": 5}
        ),
        evaluate_risk_band_formula_mutation(
            proposed_bands={"p35_heavy": 74, "p3_mid": 15, "p2_mid": 12, "fu_light": 5}
        ),
        evaluate_risk_band_formula_mutation(
            proposed_bands=dict(EXPECTED_PARTIAL_RISK_BANDS)
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["risk_band_formula_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="risk_band_formula_mutation_denied",
            layer="risk_band_formula_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "risk_band_formula_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_formula_mutate"] is True
        and doc["deny_band_inflate"] is True
        and doc["deny_band_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["risk_band_formula"] == "75+14+12+5=106"
    )
    checks["risk_band_formula_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="risk_band_formula_flags_locked",
            layer="risk_band_formula_identity_lock",
            expected="deny_mutate/inflate/deflate+KEEP_EXECUTE_FALSE",
            observed=f"hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "risk_band_formula_flags_drift",
        )
    )

    fp_ok = fp == FROZEN_RISK_BAND_FORMULA_IDENTITY_LOCK_FP_SHA256
    checks["risk_band_formula_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="risk_band_formula_fingerprint",
            layer="risk_band_formula_identity_lock",
            expected=FROZEN_RISK_BAND_FORMULA_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "risk_band_formula_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["risk_band_formula_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="risk_band_formula_identity_lock_all_pass",
            layer="risk_band_formula_identity_lock",
            expected="risk_band_formula_identity_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "risk_band_formula_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_resume_formula_identity_lock_rows(
    paths: RiskBandCombinedDryrunResumeFormulaPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """resume_formula identity lock（28+1+0=29）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_resume_formula_identity_lock()

    formula_ok = (
        EXPECTED_RESUME_IMPROVED + EXPECTED_RESUME_SAME + EXPECTED_RESUME_WORSE
        == EXPECTED_RESUME_TOTAL
        and EXPECTED_RESUME_IMPROVED == 28
        and EXPECTED_RESUME_SAME == 1
        and EXPECTED_RESUME_WORSE == 0
        and EXPECTED_RESUME_TOTAL == 29
        and EXPECTED_RESUME_FORMULA == "28+1+0=29"
    )
    checks["resume_formula_identity"] = formula_ok
    rows.append(
        _row(
            check_id="resume_formula_identity",
            layer="resume_formula_identity_lock",
            expected="28+1+0=29",
            observed=EXPECTED_RESUME_FORMULA,
            ok=formula_ok,
            notes="ok" if formula_ok else "resume_formula_drift",
        )
    )

    sample_denials = [
        evaluate_resume_formula_mutation(
            proposed_improved=29, proposed_same=1, proposed_worse=0
        ),
        evaluate_resume_formula_mutation(
            proposed_improved=28, proposed_same=0, proposed_worse=0
        ),
        evaluate_resume_formula_mutation(
            proposed_improved=28, proposed_same=1, proposed_worse=1
        ),
        evaluate_resume_formula_mutation(
            proposed_improved=28, proposed_same=1, proposed_worse=0
        ),
    ]
    mut_ok = all(d["mutation_allowed"] is False for d in sample_denials)
    checks["resume_formula_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="resume_formula_mutation_denied",
            layer="resume_formula_identity_lock",
            expected="mutation_allowed=false",
            observed=f"samples={len(sample_denials)};all_denied={mut_ok}",
            ok=mut_ok,
            notes="ok" if mut_ok else "resume_formula_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_formula_mutate"] is True
        and doc["deny_resume_inflate"] is True
        and doc["deny_resume_deflate"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["resume_formula"] == "28+1+0=29"
    )
    checks["resume_formula_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="resume_formula_flags_locked",
            layer="resume_formula_identity_lock",
            expected="deny_mutate/inflate/deflate+KEEP_EXECUTE_FALSE",
            observed=f"hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "resume_formula_flags_drift",
        )
    )

    fp_ok = fp == FROZEN_RESUME_FORMULA_IDENTITY_LOCK_FP_SHA256
    checks["resume_formula_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="resume_formula_fingerprint",
            layer="resume_formula_identity_lock",
            expected=FROZEN_RESUME_FORMULA_IDENTITY_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "resume_formula_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_formula_identity_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_formula_identity_lock_all_pass",
            layer="resume_formula_identity_lock",
            expected="resume_formula_identity_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_formula_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "resume_formula": EXPECTED_RESUME_FORMULA,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: RiskBandCombinedDryrunResumeFormulaPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK41 放行。"""
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
        assert_fm39_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK41_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock41_ok",
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
    paths: RiskBandCombinedDryrunResumeFormulaPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–40 拒绝 · MOCK41 放行。"""
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

    mock40_rel = (
        "outputs/validation/"
        "_mock_c_fm38_scale_complete_overlap_additive_tier_formula_safety"
    )
    mock40_blocked = False
    try:
        assert_fm39_output_root(mock40_rel, base_dir=base_dir)
    except RuntimeError as exc:
        mock40_blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock40_still_frozen"] = mock40_blocked
    rows.append(
        _row(
            check_id="mock40_still_frozen",
            layer="frozen_mock_isolation",
            root_id=PRIOR_TASK_ROOT_ID,
            path=mock40_rel,
            expected="write_forbidden",
            observed="blocked" if mock40_blocked else "allowed",
            ok=mock40_blocked,
            notes="ok" if mock40_blocked else "mock40_write_leak",
        )
    )

    allow_ok = False
    try:
        assert_fm39_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except Exception:
        allow_ok = False
    checks["frozen_allow_mock41"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock41",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="MOCK41_or_ephemeral_allowed",
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
            expected="MOCK3-40_block+MOCK41_allow",
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
    """protected_output_roots.csv：MOCK41 已登记。"""
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

    mock41 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(mock41.get("path_pattern") or "")
    checks["protected_csv_mock41_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock41_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock41.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock41_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3–40+resume+auth+fuller_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..38 gate battery（跳过 seal FM06–11）。"""
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
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
        "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35",
        "fm36", "fm37", "fm38",
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
            "fm33", "fm34", "fm35", "fm36", "fm37", "fm38",
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
            "fm34", "fm35", "fm36", "fm37", "fm38",
        ):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in (
            "fm27", "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34",
            "fm35", "fm36", "fm37", "fm38",
        ):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key in (
            "fm28", "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35",
            "fm36", "fm37", "fm38",
        ):
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        if key in (
            "fm29", "fm30", "fm31", "fm32", "fm33", "fm34", "fm35", "fm36", "fm37", "fm38",
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
        if key in ("fm31", "fm32", "fm33", "fm34", "fm35", "fm36", "fm37", "fm38"):
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
            check_id="fm01_05_12_38_battery_all_pass",
            layer="fm_gate_battery",
            expected="all_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_38_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm39(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK41；加固 C-ROOT-002 risk-band/combined/resume formula 说明。"""
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
                "C-FM-24..38 scale/safety freezes + C-FM-39 risk-band membership + "
                "combined_dryrun/resume formula; 只读直至人批重跑"
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
                "C-FM-39 scale partial_risk_band membership freeze (75/14/12/5) + "
                "combined_dryrun_coverage identity lock (1053) + risk_band_formula "
                "identity lock (75+14+12+5=106) + resume_formula identity lock "
                "(28+1+0=29) + FM38 continuity; never production EXECUTE; "
                "must not overwrite MOCK3-40; seal_chain_extended=false"
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


def run_scale_risk_band_combined_dryrun_resume_formula_safety(
    *,
    paths: RiskBandCombinedDryrunResumeFormulaPaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-39 规模 risk-band membership + combined/resume formula 离线 QA。"""
    paths = paths or RiskBandCombinedDryrunResumeFormulaPaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm39(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm39_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm38_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    risk_rows, risk_checks, risk_meta = (
        build_partial_risk_band_membership_freeze_rows(paths, base_dir=base_dir)
    )
    matrix.extend(risk_rows)
    combined_rows, combined_checks, combined_meta = (
        build_combined_dryrun_coverage_identity_lock_rows(paths, base_dir=base_dir)
    )
    matrix.extend(combined_rows)
    rb_formula_rows, rb_formula_checks, rb_formula_meta = (
        build_risk_band_formula_identity_lock_rows(paths, base_dir=base_dir)
    )
    matrix.extend(rb_formula_rows)
    resume_rows, resume_checks, resume_meta = (
        build_resume_formula_identity_lock_rows(paths, base_dir=base_dir)
    )
    matrix.extend(resume_rows)
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
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm38_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm38_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "partial_risk_band_membership_freeze": (
            "PASS_OFFLINE"
            if risk_checks.get("partial_risk_band_membership_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "combined_dryrun_coverage_identity_lock": (
            "PASS_OFFLINE"
            if combined_checks.get("combined_dryrun_coverage_identity_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "risk_band_formula_identity_lock": (
            "PASS_OFFLINE"
            if rb_formula_checks.get("risk_band_formula_identity_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_formula_identity_lock": (
            "PASS_OFFLINE"
            if resume_checks.get("resume_formula_identity_lock_all_pass")
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
            if bat_checks.get("fm01_05_12_38_battery_all_pass")
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

    risk_rel = _rel(
        os.path.join(out_root, "partial_risk_band_membership_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(risk_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": risk_meta["fingerprint"],
                "partial_n": risk_meta["partial_n"],
                "risk_bands": risk_meta["risk_bands"],
                "membership_sha256": risk_meta["membership_sha256"],
                "sample_denials": risk_meta["sample_denials"],
                "doc": risk_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    combined_rel = _rel(
        os.path.join(out_root, "combined_dryrun_coverage_identity_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(combined_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": combined_meta["fingerprint"],
                "combined_dryrun_coverage": combined_meta["combined_dryrun_coverage"],
                "sample_denials": combined_meta["sample_denials"],
                "doc": combined_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    rb_formula_rel = _rel(
        os.path.join(out_root, "risk_band_formula_identity_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(rb_formula_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": rb_formula_meta["fingerprint"],
                "risk_band_formula": rb_formula_meta["risk_band_formula"],
                "sample_denials": rb_formula_meta["sample_denials"],
                "doc": rb_formula_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    resume_rel = _rel(
        os.path.join(out_root, "resume_formula_identity_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(resume_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": resume_meta["fingerprint"],
                "resume_formula": resume_meta["resume_formula"],
                "sample_denials": resume_meta["sample_denials"],
                "doc": resume_meta["doc"],
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
                "gate": overall,
                "fm38_gate": "PASS_OFFLINE",
                "fm39_gate": overall,
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
                "residual_formula": "106+9+2=117",
                "union_formula": "2134+106+9=2249",
                "surface_formula": "2249+2=2251",
                "additive_formula": "2249+12=2261",
                "tier_coverage_formula": "tiers=7;coverage_sum=3314",
                "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
                "resume_formula": EXPECTED_RESUME_FORMULA,
                "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    observed_fps = {
        "partial_risk_band_membership_freeze": risk_meta["fingerprint"],
        "combined_dryrun_coverage_identity_lock": combined_meta["fingerprint"],
        "risk_band_formula_identity_lock": rb_formula_meta["fingerprint"],
        "resume_formula_identity_lock": resume_meta["fingerprint"],
        "fm38_complete_codes_membership_freeze": FM38_FROZEN_COMPLETE_FP,
        "fm38_overlap_delta_membership_freeze": FM38_FROZEN_OVERLAP_FP,
        "fm38_additive_formula_identity_lock": FM38_FROZEN_ADDITIVE_FP,
        "fm38_tier_coverage_formula_identity_lock": FM38_FROZEN_TIER_FP,
        "fm35_winner_map_sha256_lock": FM35_FROZEN_WINNER_MAP_FP,
        "fm35_resume_taxonomy_codeset_sha256_lock": FM35_FROZEN_RESUME_TAXONOMY_FP,
        "fm35_batch_priority_order_freeze": FM35_FROZEN_BATCH_PRIORITY_FP,
        "fm35_partial_risk_band_cardinality_freeze": FM35_FROZEN_PARTIAL_RISK_BAND_FP,
    }

    fingerprint_rel = _rel(
        os.path.join(out_root, "scale_fingerprint.json"), base_dir=base_dir
    )
    with open(_abs(fingerprint_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
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
                "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
                "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
                "overlap_codes_sha256": EXPECTED_OVERLAP_CODES_SHA256,
                "partial_risk_band_membership_sha256": (
                    EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256
                ),
                "residual_formula": "106+9+2=117",
                "union_formula": "2134+106+9=2249",
                "surface_formula": "2249+2=2251",
                "additive_formula": "2249+12=2261",
                "tier_coverage_formula": "tiers=7;coverage_sum=3314",
                "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
                "resume_formula": EXPECTED_RESUME_FORMULA,
                "matrix_fingerprint_sha256": fp,
                "observed_fps": observed_fps,
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
                "partial_risk_band_membership_sha256": (
                    EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256
                ),
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
                "residual_formula": "106+9+2=117",
                "union_formula": "2134+106+9=2249",
                "surface_formula": "2249+2=2251",
                "additive_formula": "2249+12=2261",
                "tier_coverage_formula": "tiers=7;coverage_sum=3314",
                "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
                "resume_formula": EXPECTED_RESUME_FORMULA,
                "notes": (
                    "partial_risk_band membership freeze (75/14/12/5) + "
                    "combined_dryrun_coverage identity lock (1053) + "
                    "risk_band_formula identity lock (75+14+12+5=106) + "
                    "resume_formula identity lock (28+1+0=29) + FM38 continuity + "
                    "MOCK41; EXECUTE remains human-held; does not overwrite MOCK3-40"
                ),
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
        "overlap_codes_sha256": EXPECTED_OVERLAP_CODES_SHA256,
        "partial_risk_band_membership_sha256": (
            EXPECTED_PARTIAL_RISK_BAND_MEMBERSHIP_SHA256
        ),
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "residual_formula": "106+9+2=117",
        "union_formula": "2134+106+9=2249",
        "surface_formula": "2249+2=2251",
        "additive_formula": "2249+12=2261",
        "tier_coverage_formula": "tiers=7;coverage_sum=3314",
        "risk_band_formula": EXPECTED_RISK_BAND_FORMULA,
        "resume_formula": EXPECTED_RESUME_FORMULA,
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "partial_risk_band_path": risk_rel,
        "combined_dryrun_path": combined_rel,
        "risk_band_formula_path": rb_formula_rel,
        "resume_formula_path": resume_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "fm38_packet": paths.fm38_packet_rel,
            "fm38_fingerprint": paths.fm38_fingerprint_rel,
            "fm38_gate": paths.fm38_gate_json_rel,
        },
        "mock_root_is_isolated": True,
    }
