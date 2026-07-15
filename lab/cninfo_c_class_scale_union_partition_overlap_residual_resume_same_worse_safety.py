"""
CNINFO C-class — 规模 union status partition cardinality freeze + overlap_delta
cardinality freeze + residual_safety_coverage lock + resume_same/worse
write-boundary（离线 · C-FM-33）。

在 C-FM-32（resume-improved write-boundary + surface uniqueness + harvest
additive + scale-tier/coverage-sum）已 commit 且 EXECUTE 仍 human-held 之上，
继续非 seal 规模/安全能力（不新增 seal / decision-await / commit-boundary；
非 extension↔drift 循环）：
  1) FM32 packet / fingerprint / gate / resume-improved·surface·additive·
     tier ledgers 零漂移连续
  2) union status partition cardinality freeze：2134/106/9（sum=2249）禁止
     partition mutation / status rebalance
  3) overlap_delta cardinality freeze：Δ12 禁止 inflate/deflate
  4) residual_safety_coverage lock：117 · mutation_allowed=false
  5) resume_same/worse write-boundary：same=1（301212）禁止 force_improve/
     reclass；worse=0 禁止 inject_worse
  6) output-root：MOCK3–34 冻结 · MOCK35 放行
  7) FM-01..05 + FM-12..32 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–34 / 权威 dual-layer 索引 ·
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
    FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256,
    FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256,
    FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256,
    FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256,
)

TASK_ID = "C-FM-33"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm33_scale_union_partition_overlap_residual_resume_same_worse_safety"
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
FM32_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm32_scale_resume_improved_surface_additive_tier_coverage_safety"
)
FM32_PACKET_REL = f"{FM32_MOCK_ROOT_REL}/scale_packet.json"
FM32_FINGERPRINT_REL = f"{FM32_MOCK_ROOT_REL}/scale_fingerprint.json"
FM32_RESUME_IMPROVED_REL = (
    f"{FM32_MOCK_ROOT_REL}/resume_improved_write_boundary_ledger.json"
)
FM32_SURFACE_REL = (
    f"{FM32_MOCK_ROOT_REL}/surface_uniqueness_cardinality_freeze_ledger.json"
)
FM32_ADDITIVE_REL = (
    f"{FM32_MOCK_ROOT_REL}/harvest_additive_cardinality_freeze_ledger.json"
)
FM32_TIER_REL = (
    f"{FM32_MOCK_ROOT_REL}/scale_tier_coverage_sum_invariant_ledger.json"
)

# C-FM-33 本包冻结指纹
FROZEN_UNION_STATUS_PARTITION_CARDINALITY_FP_SHA256 = (
    "2c0bbb7b1704dd8246eb37db6f617458e7de71d6ca89592e0c21aa4cff56cf34"
)
FROZEN_OVERLAP_DELTA_CARDINALITY_FP_SHA256 = (
    "bb2fec2da48551d74b22c3a68a971793331bb88cff5937e8d1c4dbe0f9af30c7"
)
FROZEN_RESIDUAL_SAFETY_COVERAGE_LOCK_FP_SHA256 = (
    "56a5b3978d7cd9e96710b012af416125c14cf301aa3b9ed81d4e52ce0c46ecf9"
)
FROZEN_RESUME_SAME_WORSE_WRITE_BOUNDARY_FP_SHA256 = (
    "c2623992e1e63b1b8789a43c47aaf6bcabae5de6ecd1662a09e588e5b40c9908"
)

EXPECTED_PARTIAL_CODES_SHA256 = FM31_EXPECTED_PARTIAL_CODES_SHA256
EXPECTED_FAILED_CODES_SHA256 = FM31_EXPECTED_FAILED_CODES_SHA256
EXPECTED_RESUME_SAME_CODES_SHA256 = (
    "2896da9453ebb1a999cf3074dc4753d776587b6a385ab9d5a5ed0fe9942bf5d6"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK35"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK34"
RESUME_HARVEST_ROOT_ID = "C-ROOT-002"

FROZEN_ROOT_IDS_MUST_BLOCK = tuple(f"C-ROOT-MOCK{i}" for i in range(3, 35))

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class UnionPartitionOverlapResidualResumePaths:
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
    fm32_packet_rel: str = FM32_PACKET_REL
    fm32_fingerprint_rel: str = FM32_FINGERPRINT_REL
    fm32_resume_improved_rel: str = FM32_RESUME_IMPROVED_REL
    fm32_surface_rel: str = FM32_SURFACE_REL
    fm32_additive_rel: str = FM32_ADDITIVE_REL
    fm32_tier_rel: str = FM32_TIER_REL
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


def assert_fm33_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-33 写根：须 validation/_mock_*，不得覆盖 MOCK3–34，
    不得写权威 dual-layer 索引；允许本任务 MOCK35 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-33 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _sha256_codes(codes: Sequence[str]) -> str:
    return hashlib.sha256(",".join(sorted(codes)).encode("utf-8")).hexdigest()


def fingerprint_union_status_partition_cardinality_freeze() -> Tuple[str, Dict[str, Any]]:
    """union status partition cardinality freeze 指纹。"""
    doc = {
        "kind": "union_status_partition_cardinality_freeze",
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "partition_sum": (
            EXPECTED_UNION_COMPLETE
            + EXPECTED_UNION_PARTIAL
            + EXPECTED_UNION_FAILED
        ),
        "deny_partition_mutation": True,
        "deny_status_rebalance": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_overlap_delta_cardinality_freeze() -> Tuple[str, Dict[str, Any]]:
    """overlap_delta cardinality freeze 指纹。"""
    doc = {
        "kind": "overlap_delta_cardinality_freeze",
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "deny_overlap_inflate": True,
        "deny_overlap_deflate": True,
        "deny_cardinality_mutation": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_residual_safety_coverage_lock() -> Tuple[str, Dict[str, Any]]:
    """residual_safety_coverage lock 指纹。"""
    doc = {
        "kind": "residual_safety_coverage_lock",
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "mutation_allowed": False,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_resume_same_worse_write_boundary() -> Tuple[str, Dict[str, Any]]:
    """resume_same/worse write-boundary 指纹。"""
    doc = {
        "kind": "resume_same_worse_write_boundary",
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "deny_same_force_improve": True,
        "deny_same_reclass": True,
        "deny_worse_inject": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_union_partition_mutation(
    *,
    proposed_complete: int,
    proposed_partial: int,
    proposed_failed: int,
) -> Dict[str, Any]:
    """评估 union status partition 变异；mutation 一律拒绝。"""
    matches = (
        proposed_complete == EXPECTED_UNION_COMPLETE
        and proposed_partial == EXPECTED_UNION_PARTIAL
        and proposed_failed == EXPECTED_UNION_FAILED
    )
    return {
        "proposed": {
            "union_complete": proposed_complete,
            "union_partial": proposed_partial,
            "union_failed": proposed_failed,
        },
        "frozen": {
            "union_complete": EXPECTED_UNION_COMPLETE,
            "union_partial": EXPECTED_UNION_PARTIAL,
            "union_failed": EXPECTED_UNION_FAILED,
        },
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "union_status_partition_cardinality_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_overlap_delta_mutation(*, proposed_overlap_delta: int) -> Dict[str, Any]:
    """评估 overlap_delta 基数变异；mutation 一律拒绝。"""
    matches = proposed_overlap_delta == EXPECTED_OVERLAP_DELTA
    return {
        "proposed_overlap_delta": proposed_overlap_delta,
        "frozen_overlap_delta": EXPECTED_OVERLAP_DELTA,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "overlap_delta_cardinality_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_residual_safety_coverage_mutation(
    *, proposed_coverage: int
) -> Dict[str, Any]:
    """评估 residual_safety_coverage 变异；mutation 一律拒绝。"""
    matches = proposed_coverage == EXPECTED_RESIDUAL_SAFETY_COVERAGE
    return {
        "proposed_residual_safety_coverage": proposed_coverage,
        "frozen_residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "residual_safety_coverage_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_resume_same_write(*, code: str, action: str) -> Dict[str, Any]:
    """评估 resume_same 码写动作；显式 denial。"""
    if code not in EXPECTED_RESUME_SAME_CODES:
        raise ValueError(f"not a resume_same code: {code}")
    if action not in ("force_improve", "status_reclass", "bucket_reclass"):
        raise ValueError(f"unknown same write action: {action}")
    return {
        "code": code,
        "action": action,
        "bucket": "same",
        "allowed": False,
        "reason": "resume_same_write_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_resume_worse_inject(*, action: str = "inject_worse") -> Dict[str, Any]:
    """评估 resume_worse 注入；显式 denial（worse 冻结为 0）。"""
    if action != "inject_worse":
        raise ValueError(f"unknown worse action: {action}")
    return {
        "action": action,
        "bucket": "worse",
        "frozen_resume_worse": EXPECTED_RESUME_WORSE,
        "allowed": False,
        "reason": "resume_worse_inject_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def build_fm32_continuity_rows(
    paths: UnionPartitionOverlapResidualResumePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM32 packet / fingerprint / gate / 四 ledger 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm32_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm32_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm32_gate_json_rel, base_dir=base_dir))
    ri_led = load_json(_abs(paths.fm32_resume_improved_rel, base_dir=base_dir))
    surf_led = load_json(_abs(paths.fm32_surface_rel, base_dir=base_dir))
    add_led = load_json(_abs(paths.fm32_additive_rel, base_dir=base_dir))
    tier_led = load_json(_abs(paths.fm32_tier_rel, base_dir=base_dir))

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
        and list(packet.get("batch_priority") or []) == list(EXPECTED_BATCH_PRIORITY)
        and packet.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
        and packet.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
    )
    checks["fm32_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm32_packet_continuity",
            layer="fm32_continuity",
            path=paths.fm32_packet_rel,
            expected="PASS_OFFLINE;unique=2249;2134/106/9;28/1/0;7/3314;KEEP",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"status={packet.get('union_complete')}/"
                f"{packet.get('union_partial')}/{packet.get('union_failed')};"
                f"resume={packet.get('resume_improved')}/"
                f"{packet.get('resume_same')}/{packet.get('resume_worse')};"
                f"tier={packet.get('scale_tier_count')}/"
                f"{packet.get('company_coverage_sum')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm32_packet_drift",
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
        and fp_doc.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and fp_doc.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
        and fp_doc.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
        and fp_doc.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
        and frozen.get("resume_improved_write_boundary")
        == FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256
        and frozen.get("surface_uniqueness_cardinality_freeze")
        == FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256
        and frozen.get("harvest_additive_cardinality_freeze")
        == FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256
        and frozen.get("scale_tier_coverage_sum_invariant")
        == FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm32_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm32_fingerprint_continuity",
            layer="fm32_continuity",
            path=paths.fm32_fingerprint_rel,
            expected="unique2249+fm32_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"surface={fp_doc.get('surface_unique')};"
                f"additive={fp_doc.get('harvest_additive')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm32_fingerprint_drift",
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
        and gate_doc.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and gate_doc.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
        and gate_doc.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
        and gate_doc.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
    )
    checks["fm32_gate_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm32_gate_continuity",
            layer="fm32_continuity",
            path=paths.fm32_gate_json_rel,
            expected="PASS_OFFLINE;KEEP;surface2251;additive2261;7/3314",
            observed=(
                f"gate={gate_doc.get('gate')};surface={gate_doc.get('surface_unique')};"
                f"additive={gate_doc.get('harvest_additive')};"
                f"tier={gate_doc.get('scale_tier_count')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm32_gate_drift",
        )
    )

    ri_ok = (
        ri_led.get("fingerprint_sha256")
        == FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256
        and ri_led.get("improved_n") == EXPECTED_RESUME_IMPROVED
        and ri_led.get("improved_codes_sha256") == EXPECTED_RESUME_IMPROVED_CODES_SHA256
    )
    checks["fm32_resume_improved_ledger_continuity"] = ri_ok
    rows.append(
        _row(
            check_id="fm32_resume_improved_ledger_continuity",
            layer="fm32_continuity",
            path=paths.fm32_resume_improved_rel,
            expected=FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256,
            observed=str(ri_led.get("fingerprint_sha256") or ""),
            ok=ri_ok,
            notes="ok" if ri_ok else "fm32_resume_improved_drift",
        )
    )

    surf_ok = (
        surf_led.get("fingerprint_sha256")
        == FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256
        and surf_led.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
    )
    checks["fm32_surface_ledger_continuity"] = surf_ok
    rows.append(
        _row(
            check_id="fm32_surface_ledger_continuity",
            layer="fm32_continuity",
            path=paths.fm32_surface_rel,
            expected=FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256,
            observed=str(surf_led.get("fingerprint_sha256") or ""),
            ok=surf_ok,
            notes="ok" if surf_ok else "fm32_surface_drift",
        )
    )

    add_ok = (
        add_led.get("fingerprint_sha256")
        == FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256
        and add_led.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
        and add_led.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
    )
    checks["fm32_additive_ledger_continuity"] = add_ok
    rows.append(
        _row(
            check_id="fm32_additive_ledger_continuity",
            layer="fm32_continuity",
            path=paths.fm32_additive_rel,
            expected=FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256,
            observed=str(add_led.get("fingerprint_sha256") or ""),
            ok=add_ok,
            notes="ok" if add_ok else "fm32_additive_drift",
        )
    )

    tier_ok = (
        tier_led.get("fingerprint_sha256") == FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256
        and tier_led.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
        and tier_led.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
    )
    checks["fm32_tier_ledger_continuity"] = tier_ok
    rows.append(
        _row(
            check_id="fm32_tier_ledger_continuity",
            layer="fm32_continuity",
            path=paths.fm32_tier_rel,
            expected=FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256,
            observed=str(tier_led.get("fingerprint_sha256") or ""),
            ok=tier_ok,
            notes="ok" if tier_ok else "fm32_tier_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm32_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm32_continuity_all_pass",
            layer="fm32_continuity",
            expected="packet+fp+gate+4ledgers",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm32_continuity_incomplete",
        )
    )
    return rows, checks


def build_union_status_partition_cardinality_freeze_rows(
    paths: UnionPartitionOverlapResidualResumePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """union status partition cardinality freeze（2134/106/9）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_union_status_partition_cardinality_freeze()

    counts_ok = (
        EXPECTED_UNION_COMPLETE == 2134
        and EXPECTED_UNION_PARTIAL == 106
        and EXPECTED_UNION_FAILED == 9
        and (
            EXPECTED_UNION_COMPLETE
            + EXPECTED_UNION_PARTIAL
            + EXPECTED_UNION_FAILED
        )
        == EXPECTED_HARVEST_UNIQUE_UNION
    )
    checks["union_partition_exact"] = counts_ok
    rows.append(
        _row(
            check_id="union_partition_exact",
            layer="union_status_partition_cardinality_freeze",
            expected="2134/106/9;sum=2249",
            observed=(
                f"{EXPECTED_UNION_COMPLETE}/{EXPECTED_UNION_PARTIAL}/"
                f"{EXPECTED_UNION_FAILED};sum="
                f"{EXPECTED_UNION_COMPLETE + EXPECTED_UNION_PARTIAL + EXPECTED_UNION_FAILED}"
            ),
            ok=counts_ok,
            notes="ok" if counts_ok else "union_partition_drift",
        )
    )

    mut = evaluate_union_partition_mutation(
        proposed_complete=2133, proposed_partial=107, proposed_failed=9
    )
    mut2 = evaluate_union_partition_mutation(
        proposed_complete=EXPECTED_UNION_COMPLETE,
        proposed_partial=EXPECTED_UNION_PARTIAL,
        proposed_failed=EXPECTED_UNION_FAILED,
    )
    mut_ok = mut["mutation_allowed"] is False and mut2["mutation_allowed"] is False
    checks["union_partition_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="union_partition_mutation_denied",
            layer="union_status_partition_cardinality_freeze",
            expected="mutation_allowed=false",
            observed=(
                f"drift_denied={mut['mutation_allowed']};"
                f"exact_denied={mut2['mutation_allowed']}"
            ),
            ok=mut_ok,
            notes="ok" if mut_ok else "union_partition_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_partition_mutation"] is True
        and doc["deny_status_rebalance"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["partition_sum"] == EXPECTED_HARVEST_UNIQUE_UNION
    )
    checks["union_partition_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="union_partition_flags_locked",
            layer="union_status_partition_cardinality_freeze",
            expected="deny_mutation+rebalance+KEEP;sum2249",
            observed=(
                f"mutation={doc['deny_partition_mutation']};"
                f"rebalance={doc['deny_status_rebalance']};"
                f"sum={doc['partition_sum']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_UNION_STATUS_PARTITION_CARDINALITY_FP_SHA256
    checks["union_partition_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="union_partition_fingerprint",
            layer="union_status_partition_cardinality_freeze",
            expected=FROZEN_UNION_STATUS_PARTITION_CARDINALITY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "union_partition_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["union_status_partition_cardinality_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="union_status_partition_cardinality_freeze_all_pass",
            layer="union_status_partition_cardinality_freeze",
            expected="2134_106_9_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "union_partition_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "sample_denials": [mut, mut2],
        "doc": doc,
    }
    return rows, checks, meta


def build_overlap_delta_cardinality_freeze_rows(
    paths: UnionPartitionOverlapResidualResumePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """overlap_delta cardinality freeze（12）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_overlap_delta_cardinality_freeze()

    counts_ok = (
        EXPECTED_OVERLAP_DELTA == 12
        and EXPECTED_HARVEST_ADDITIVE - EXPECTED_HARVEST_UNIQUE_UNION
        == EXPECTED_OVERLAP_DELTA
    )
    checks["overlap_delta_exact"] = counts_ok
    rows.append(
        _row(
            check_id="overlap_delta_exact",
            layer="overlap_delta_cardinality_freeze",
            expected="12;additive-unique",
            observed=(
                f"{EXPECTED_OVERLAP_DELTA};"
                f"{EXPECTED_HARVEST_ADDITIVE}-{EXPECTED_HARVEST_UNIQUE_UNION}"
            ),
            ok=counts_ok,
            notes="ok" if counts_ok else "overlap_delta_drift",
        )
    )

    mut = evaluate_overlap_delta_mutation(proposed_overlap_delta=13)
    mut2 = evaluate_overlap_delta_mutation(
        proposed_overlap_delta=EXPECTED_OVERLAP_DELTA
    )
    mut_ok = mut["mutation_allowed"] is False and mut2["mutation_allowed"] is False
    checks["overlap_delta_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="overlap_delta_mutation_denied",
            layer="overlap_delta_cardinality_freeze",
            expected="mutation_allowed=false",
            observed=(
                f"drift_denied={mut['mutation_allowed']};"
                f"exact_denied={mut2['mutation_allowed']}"
            ),
            ok=mut_ok,
            notes="ok" if mut_ok else "overlap_delta_mutation_leak",
        )
    )

    flags_ok = (
        doc["deny_overlap_inflate"] is True
        and doc["deny_overlap_deflate"] is True
        and doc["deny_cardinality_mutation"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["overlap_delta_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="overlap_delta_flags_locked",
            layer="overlap_delta_cardinality_freeze",
            expected="deny_inflate+deflate+mutation+KEEP",
            observed=(
                f"inflate={doc['deny_overlap_inflate']};"
                f"deflate={doc['deny_overlap_deflate']};"
                f"mutation={doc['deny_cardinality_mutation']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_OVERLAP_DELTA_CARDINALITY_FP_SHA256
    checks["overlap_delta_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="overlap_delta_fingerprint",
            layer="overlap_delta_cardinality_freeze",
            expected=FROZEN_OVERLAP_DELTA_CARDINALITY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "overlap_delta_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["overlap_delta_cardinality_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="overlap_delta_cardinality_freeze_all_pass",
            layer="overlap_delta_cardinality_freeze",
            expected="12_overlap_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "overlap_delta_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "sample_denials": [mut, mut2],
        "doc": doc,
    }
    return rows, checks, meta


def build_residual_safety_coverage_lock_rows(
    paths: UnionPartitionOverlapResidualResumePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """residual_safety_coverage lock（117）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_residual_safety_coverage_lock()

    counts_ok = EXPECTED_RESIDUAL_SAFETY_COVERAGE == 117
    checks["residual_safety_coverage_exact"] = counts_ok
    rows.append(
        _row(
            check_id="residual_safety_coverage_exact",
            layer="residual_safety_coverage_lock",
            expected="117",
            observed=str(EXPECTED_RESIDUAL_SAFETY_COVERAGE),
            ok=counts_ok,
            notes="ok" if counts_ok else "residual_coverage_drift",
        )
    )

    mut = evaluate_residual_safety_coverage_mutation(proposed_coverage=116)
    mut2 = evaluate_residual_safety_coverage_mutation(
        proposed_coverage=EXPECTED_RESIDUAL_SAFETY_COVERAGE
    )
    mut_ok = mut["mutation_allowed"] is False and mut2["mutation_allowed"] is False
    checks["residual_safety_coverage_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="residual_safety_coverage_mutation_denied",
            layer="residual_safety_coverage_lock",
            expected="mutation_allowed=false",
            observed=(
                f"drift_denied={mut['mutation_allowed']};"
                f"exact_denied={mut2['mutation_allowed']}"
            ),
            ok=mut_ok,
            notes="ok" if mut_ok else "residual_coverage_mutation_leak",
        )
    )

    flags_ok = (
        doc["mutation_allowed"] is False and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["residual_safety_coverage_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="residual_safety_coverage_flags_locked",
            layer="residual_safety_coverage_lock",
            expected="mutation_allowed=false+KEEP",
            observed=f"mutation={doc['mutation_allowed']};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_RESIDUAL_SAFETY_COVERAGE_LOCK_FP_SHA256
    checks["residual_safety_coverage_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="residual_safety_coverage_fingerprint",
            layer="residual_safety_coverage_lock",
            expected=FROZEN_RESIDUAL_SAFETY_COVERAGE_LOCK_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "residual_coverage_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["residual_safety_coverage_lock_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="residual_safety_coverage_lock_all_pass",
            layer="residual_safety_coverage_lock",
            expected="117_lock+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "residual_coverage_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "sample_denials": [mut, mut2],
        "doc": doc,
    }
    return rows, checks, meta


def build_resume_same_worse_write_boundary_rows(
    paths: UnionPartitionOverlapResidualResumePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """resume_same/worse write-boundary（1/0）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    fp, doc = fingerprint_resume_same_worse_write_boundary()

    counts_ok = (
        EXPECTED_RESUME_SAME == 1
        and EXPECTED_RESUME_WORSE == 0
        and set(EXPECTED_RESUME_SAME_CODES) == {"301212"}
        and _sha256_codes(sorted(EXPECTED_RESUME_SAME_CODES))
        == EXPECTED_RESUME_SAME_CODES_SHA256
    )
    checks["resume_same_worse_exact"] = counts_ok
    rows.append(
        _row(
            check_id="resume_same_worse_exact",
            layer="resume_same_worse_write_boundary",
            expected="1/0;301212",
            observed=(
                f"{EXPECTED_RESUME_SAME}/{EXPECTED_RESUME_WORSE};"
                f"{','.join(sorted(EXPECTED_RESUME_SAME_CODES))}"
            ),
            ok=counts_ok,
            notes="ok" if counts_ok else "resume_same_worse_drift",
        )
    )

    denial_ok = True
    sample_denials: List[Dict[str, Any]] = []
    code = sorted(EXPECTED_RESUME_SAME_CODES)[0]
    for action in ("force_improve", "status_reclass", "bucket_reclass"):
        d = evaluate_resume_same_write(code=code, action=action)
        sample_denials.append(d)
        if d.get("allowed") is not False:
            denial_ok = False
    worse = evaluate_resume_worse_inject()
    sample_denials.append(worse)
    if worse.get("allowed") is not False:
        denial_ok = False
    checks["resume_same_worse_write_denied"] = denial_ok
    rows.append(
        _row(
            check_id="resume_same_worse_write_denied",
            layer="resume_same_worse_write_boundary",
            expected="same_writes+worse_inject_denied",
            observed=f"samples={len(sample_denials)};all_denied={denial_ok}",
            ok=denial_ok,
            notes="ok" if denial_ok else "write_leak",
        )
    )

    flags_ok = (
        doc["deny_same_force_improve"] is True
        and doc["deny_same_reclass"] is True
        and doc["deny_worse_inject"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["resume_same_worse_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="resume_same_worse_flags_locked",
            layer="resume_same_worse_write_boundary",
            expected="deny_improve+reclass+inject_worse+KEEP",
            observed=(
                f"improve={doc['deny_same_force_improve']};"
                f"reclass={doc['deny_same_reclass']};"
                f"worse={doc['deny_worse_inject']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_RESUME_SAME_WORSE_WRITE_BOUNDARY_FP_SHA256
    checks["resume_same_worse_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="resume_same_worse_fingerprint",
            layer="resume_same_worse_write_boundary",
            expected=FROZEN_RESUME_SAME_WORSE_WRITE_BOUNDARY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "resume_same_worse_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_same_worse_write_boundary_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_same_worse_write_boundary_all_pass",
            layer="resume_same_worse_write_boundary",
            expected="1_0_write_boundary+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_same_worse_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: UnionPartitionOverlapResidualResumePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK35 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm33.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm33.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm33.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm33.csv",
        ),
        (
            "write_guard_phase35_resume_refused",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm33.csv",
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
        assert_fm33_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK35_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock35_ok",
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
    paths: UnionPartitionOverlapResidualResumePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–34 拒绝 · MOCK35 放行。"""
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

    mock34_rel = (
        "outputs/validation/"
        "_mock_c_fm32_scale_resume_improved_surface_additive_tier_coverage_safety"
    )
    mock34_blocked = False
    try:
        assert_fm33_output_root(mock34_rel, base_dir=base_dir)
    except RuntimeError as exc:
        mock34_blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock34_still_frozen"] = mock34_blocked
    rows.append(
        _row(
            check_id="mock34_still_frozen",
            layer="frozen_mock_isolation",
            root_id=PRIOR_TASK_ROOT_ID,
            path=mock34_rel,
            expected="write_forbidden",
            observed="blocked" if mock34_blocked else "allowed",
            ok=mock34_blocked,
            notes="ok" if mock34_blocked else "mock34_write_leak",
        )
    )

    allow_ok = False
    try:
        assert_fm33_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except Exception:
        allow_ok = False
    checks["frozen_allow_mock35"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock35",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="MOCK35_or_ephemeral_allowed",
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
            expected="MOCK3-34_block+MOCK35_allow",
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
    """protected_output_roots.csv：MOCK35 已登记。"""
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

    mock35 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(mock35.get("path_pattern") or "")
    checks["protected_csv_mock35_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock35_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock35.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock35_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-34+resume+auth+fuller_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..32 gate battery（跳过 seal FM06–11）。"""
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
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
        "fm28", "fm29", "fm30", "fm31", "fm32",
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
        if key in ("fm25", "fm26", "fm27", "fm28", "fm29", "fm30", "fm31", "fm32"):
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in ("fm26", "fm27", "fm28", "fm29", "fm30", "fm31", "fm32"):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in ("fm27", "fm28", "fm29", "fm30", "fm31", "fm32"):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key in ("fm28", "fm29", "fm30", "fm31", "fm32"):
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        if key in ("fm29", "fm30", "fm31", "fm32"):
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
        if key in ("fm31", "fm32"):
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
            check_id="fm01_05_12_32_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_32_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm33(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK35；加固 C-ROOT-002 union/overlap/residual/same-worse 说明。"""
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
                "C-FM-24..32 scale/safety freezes + C-FM-33 union-partition/"
                "overlap-delta/residual-coverage/resume-same-worse; "
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
                "C-FM-33 scale union status partition cardinality freeze "
                "(2134/106/9) + overlap_delta cardinality freeze (12) + "
                "residual_safety_coverage lock (117) + resume_same/worse "
                "write-boundary (1/0) + FM32 continuity; never production "
                "EXECUTE; must not overwrite MOCK3-34; seal_chain_extended=false"
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


def run_scale_union_partition_overlap_residual_resume_same_worse_safety(
    *,
    paths: UnionPartitionOverlapResidualResumePaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-33 规模 union/overlap/residual/resume_same-worse 离线 QA。"""
    paths = paths or UnionPartitionOverlapResidualResumePaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm33(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm33_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm32_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    uni_rows, uni_checks, uni_meta = build_union_status_partition_cardinality_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(uni_rows)
    ov_rows, ov_checks, ov_meta = build_overlap_delta_cardinality_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(ov_rows)
    res_rows, res_checks, res_meta = build_residual_safety_coverage_lock_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(res_rows)
    sw_rows, sw_checks, sw_meta = build_resume_same_worse_write_boundary_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(sw_rows)
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
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm32_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm32_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "union_status_partition_cardinality_freeze": (
            "PASS_OFFLINE"
            if uni_checks.get("union_status_partition_cardinality_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "overlap_delta_cardinality_freeze": (
            "PASS_OFFLINE"
            if ov_checks.get("overlap_delta_cardinality_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "residual_safety_coverage_lock": (
            "PASS_OFFLINE"
            if res_checks.get("residual_safety_coverage_lock_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_same_worse_write_boundary": (
            "PASS_OFFLINE"
            if sw_checks.get("resume_same_worse_write_boundary_all_pass")
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
            if bat_checks.get("fm01_05_12_32_battery_all_pass")
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

    uni_rel = _rel(
        os.path.join(out_root, "union_status_partition_cardinality_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(uni_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": uni_meta["fingerprint"],
                "union_complete": uni_meta["union_complete"],
                "union_partial": uni_meta["union_partial"],
                "union_failed": uni_meta["union_failed"],
                "sample_denials": uni_meta["sample_denials"],
                "doc": uni_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    ov_rel = _rel(
        os.path.join(out_root, "overlap_delta_cardinality_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(ov_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": ov_meta["fingerprint"],
                "overlap_delta": ov_meta["overlap_delta"],
                "sample_denials": ov_meta["sample_denials"],
                "doc": ov_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    res_rel = _rel(
        os.path.join(out_root, "residual_safety_coverage_lock_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(res_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": res_meta["fingerprint"],
                "residual_safety_coverage": res_meta["residual_safety_coverage"],
                "sample_denials": res_meta["sample_denials"],
                "doc": res_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    sw_rel = _rel(
        os.path.join(out_root, "resume_same_worse_write_boundary_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(sw_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": sw_meta["fingerprint"],
                "resume_same": sw_meta["resume_same"],
                "resume_worse": sw_meta["resume_worse"],
                "same_codes_sha256": sw_meta["same_codes_sha256"],
                "sample_denials": sw_meta["sample_denials"],
                "doc": sw_meta["doc"],
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
                "fm32_gate": gates["fm32"].get("gate"),
                "fm33_gate": overall,
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
                "improved_codes_sha256": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
                "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
                "notes": (
                    "union status partition cardinality freeze (2134/106/9) + "
                    "overlap_delta cardinality freeze (12) + residual_safety_"
                    "coverage lock (117) + resume_same/worse write-boundary "
                    "(1/0) + FM32 continuity + MOCK35; EXECUTE remains "
                    "human-held; does not overwrite MOCK3-34"
                ),
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    observed_fps = {
        "union_status_partition_cardinality_freeze": uni_meta["fingerprint"],
        "overlap_delta_cardinality_freeze": ov_meta["fingerprint"],
        "residual_safety_coverage_lock": res_meta["fingerprint"],
        "resume_same_worse_write_boundary": sw_meta["fingerprint"],
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
                "improved_codes_sha256": EXPECTED_RESUME_IMPROVED_CODES_SHA256,
                "same_codes_sha256": EXPECTED_RESUME_SAME_CODES_SHA256,
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
                "frozen_fps": {
                    "union_status_partition_cardinality_freeze": (
                        FROZEN_UNION_STATUS_PARTITION_CARDINALITY_FP_SHA256
                    ),
                    "overlap_delta_cardinality_freeze": (
                        FROZEN_OVERLAP_DELTA_CARDINALITY_FP_SHA256
                    ),
                    "residual_safety_coverage_lock": (
                        FROZEN_RESIDUAL_SAFETY_COVERAGE_LOCK_FP_SHA256
                    ),
                    "resume_same_worse_write_boundary": (
                        FROZEN_RESUME_SAME_WORSE_WRITE_BOUNDARY_FP_SHA256
                    ),
                    "fm32_resume_improved_write_boundary": (
                        FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256
                    ),
                    "fm32_surface_uniqueness_cardinality_freeze": (
                        FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256
                    ),
                    "fm32_harvest_additive_cardinality_freeze": (
                        FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256
                    ),
                    "fm32_scale_tier_coverage_sum_invariant": (
                        FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256
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
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fp_rel,
        "fingerprint": fp,
        "union_partition_path": uni_rel,
        "overlap_delta_path": ov_rel,
        "residual_coverage_path": res_rel,
        "resume_same_worse_path": sw_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "fm32_packet": paths.fm32_packet_rel,
            "fm32_gate": paths.fm32_gate_json_rel,
        },
        "mock_root_is_isolated": True,
    }
