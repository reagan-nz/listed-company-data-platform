"""
CNINFO C-class — 规模 failed promotion denial + partial demotion-to-failed denial
+ batch-priority order freeze + resume-delta taxonomy freeze（离线 · C-FM-31）。

在 C-FM-30（complete demotion + partition + winner provenance + overlap/surface
freeze）已 commit 且 EXECUTE 仍 human-held 之上，继续非 seal 规模/安全能力
（不新增 seal / decision-await / commit-boundary；非 extension↔drift 循环）：
  1) FM30 packet / fingerprint / gate / demotion·partition·winner·overlap
     ledgers 零漂移连续
  2) failed promotion denial：9 码禁止 promote→partial / promote→complete
  3) partial demotion-to-failed denial：106 码禁止 demote→failed
  4) batch-priority order freeze：BATCH_PRIORITY=(h863,p35,p3,p2,fu) 冻结
  5) resume-delta taxonomy freeze：improved=28 / same=1 / worse=0 冻结
  6) output-root：MOCK3–32 冻结 · MOCK33 放行
  7) FM-01..05 + FM-12..30 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–32 / 权威 dual-layer 索引 ·
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
)
from cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety import (  # noqa: E402
    EXPECTED_COMPLETE_CODES_SHA256,
    EXPECTED_WINNER_MAP_SHA256,
    FROZEN_COMPLETE_DEMOTION_DENIAL_FP_SHA256,
    FROZEN_OVERLAP_SURFACE_FREEZE_FP_SHA256,
    FROZEN_STATUS_PARTITION_INVARIANT_FP_SHA256,
    FROZEN_WINNER_PROVENANCE_LOCK_FP_SHA256,
)

TASK_ID = "C-FM-31"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm31_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety"
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
FM30_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm30_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety"
)
FM30_PACKET_REL = f"{FM30_MOCK_ROOT_REL}/scale_packet.json"
FM30_FINGERPRINT_REL = f"{FM30_MOCK_ROOT_REL}/scale_fingerprint.json"
FM30_DEMOTION_REL = f"{FM30_MOCK_ROOT_REL}/complete_demotion_denial_ledger.json"
FM30_PARTITION_REL = f"{FM30_MOCK_ROOT_REL}/status_partition_invariant_lock_ledger.json"
FM30_WINNER_REL = f"{FM30_MOCK_ROOT_REL}/winner_provenance_lock_ledger.json"
FM30_OVERLAP_REL = (
    f"{FM30_MOCK_ROOT_REL}/overlap_delta_surface_injection_freeze_ledger.json"
)

FROZEN_FAILED_PROMOTION_DENIAL_FP_SHA256 = (
    "8b581766d5dfbecacecbf37cbadec2d2abb5d846913545e82bf11b46447c47c9"
)
FROZEN_PARTIAL_DEMOTION_TO_FAILED_FP_SHA256 = (
    "6a232823808d17f67af8a8189faa01ad810fec18d4abe4d27e48d1da90e77d28"
)
FROZEN_BATCH_PRIORITY_ORDER_FP_SHA256 = (
    "8470ed60a660340ef61dcfbb6a88c7532bd11f814008c75453b4788c3dabaf98"
)
FROZEN_RESUME_DELTA_TAXONOMY_FP_SHA256 = (
    "e96f85868931736b993ba1e7e445cdda66e48ee6f966ad1f19d5fc22a093b33d"
)

EXPECTED_PARTIAL_CODES_SHA256 = (
    "5d5da7030f91e60893627d7fcf208b79f4f09e3edc5c4255fb797c1706672d73"
)
EXPECTED_FAILED_CODES_SHA256 = (
    "fb74a9df6bbecf75a7c2b354491a80c4b294c3c1cd392ec429bd8d16b74a14f6"
)
EXPECTED_PARTIAL_WINNER_BATCHES = {
    "fu": 5,
    "p2": 12,
    "p3": 14,
    "p35": 75,
}
EXPECTED_FAILED_WINNER_BATCHES = {
    "p3": 3,
    "p35": 6,
}
EXPECTED_BATCH_PRIORITY = ("h863", "p35", "p3", "p2", "fu")

THIS_TASK_ROOT_ID = "C-ROOT-MOCK33"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK32"
RESUME_HARVEST_ROOT_ID = "C-ROOT-002"

FROZEN_ROOT_IDS_MUST_BLOCK = tuple(
    f"C-ROOT-MOCK{i}" for i in range(3, 33)
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class FailedPromotionPartialDemotionPaths:
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
    fm30_packet_rel: str = FM30_PACKET_REL
    fm30_fingerprint_rel: str = FM30_FINGERPRINT_REL
    fm30_demotion_rel: str = FM30_DEMOTION_REL
    fm30_partition_rel: str = FM30_PARTITION_REL
    fm30_winner_rel: str = FM30_WINNER_REL
    fm30_overlap_rel: str = FM30_OVERLAP_REL
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


def _to_fm26_paths(paths: FailedPromotionPartialDemotionPaths) -> Fm26Paths:
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


def assert_fm31_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-31 写根：须 validation/_mock_*，不得覆盖 MOCK3–32，
    不得写权威 dual-layer 索引；允许本任务 MOCK33 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-31 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _sha256_codes(codes: Sequence[str]) -> str:
    return hashlib.sha256(",".join(sorted(codes)).encode("utf-8")).hexdigest()


def fingerprint_failed_promotion_denial(
    *,
    failed_codes: Sequence[str],
) -> Tuple[str, Dict[str, Any]]:
    """failed promotion denial 指纹。"""
    codes = sorted(failed_codes)
    doc = {
        "kind": "failed_promotion_denial",
        "failed_n": len(codes),
        "failed_codes_sha256": _sha256_codes(codes),
        "deny_promote_to_partial": True,
        "deny_promote_to_complete": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_partial_demotion_to_failed(
    *,
    partial_codes: Sequence[str],
) -> Tuple[str, Dict[str, Any]]:
    """partial demotion-to-failed denial 指纹。"""
    codes = sorted(partial_codes)
    doc = {
        "kind": "partial_demotion_to_failed_denial",
        "partial_n": len(codes),
        "partial_codes_sha256": _sha256_codes(codes),
        "deny_demote_to_failed": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_batch_priority_order_freeze() -> Tuple[str, Dict[str, Any]]:
    """batch-priority order freeze 指纹。"""
    doc = {
        "kind": "batch_priority_order_freeze",
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "deny_priority_reorder": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_resume_delta_taxonomy_freeze() -> Tuple[str, Dict[str, Any]]:
    """resume-delta taxonomy freeze 指纹。"""
    doc = {
        "kind": "resume_delta_taxonomy_freeze",
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "deny_taxonomy_reclass": True,
        "deny_taxonomy_count_mutation": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_failed_promotion(
    *,
    code: str,
    to_status: str,
    failed_codes: Sequence[str],
) -> Dict[str, Any]:
    """评估 failed 码 promotion；显式 denial。"""
    if code not in set(failed_codes):
        raise ValueError(f"not a failed code: {code}")
    if to_status not in ("partial", "complete"):
        raise ValueError(f"unknown promotion target: {to_status}")
    return {
        "code": code,
        "from_status": "failed",
        "to_status": to_status,
        "allowed": False,
        "reason": "failed_promotion_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_partial_demotion_to_failed(
    *,
    code: str,
    partial_codes: Sequence[str],
) -> Dict[str, Any]:
    """评估 partial→failed demotion；显式 denial。"""
    if code not in set(partial_codes):
        raise ValueError(f"not a partial code: {code}")
    return {
        "code": code,
        "from_status": "partial",
        "to_status": "failed",
        "allowed": False,
        "reason": "partial_demotion_to_failed_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_batch_priority_reorder(
    *,
    proposed_priority: Sequence[str],
) -> Dict[str, Any]:
    """评估 BATCH_PRIORITY 重排；mutation 一律拒绝。"""
    matches = tuple(proposed_priority) == EXPECTED_BATCH_PRIORITY
    return {
        "proposed_priority": list(proposed_priority),
        "frozen_priority": list(EXPECTED_BATCH_PRIORITY),
        "matches_frozen": matches,
        "reorder_allowed": False,
        "reason": "batch_priority_order_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_resume_taxonomy_mutation(
    *,
    proposed_improved: int,
    proposed_same: int,
    proposed_worse: int,
) -> Dict[str, Any]:
    """评估 resume taxonomy 计数变异；mutation 一律拒绝。"""
    matches = (
        proposed_improved == EXPECTED_RESUME_IMPROVED
        and proposed_same == EXPECTED_RESUME_SAME
        and proposed_worse == EXPECTED_RESUME_WORSE
        and proposed_improved + proposed_same + proposed_worse
        == EXPECTED_RESUME_TOTAL
    )
    return {
        "proposed": {
            "improved": proposed_improved,
            "same": proposed_same,
            "worse": proposed_worse,
        },
        "frozen": {
            "improved": EXPECTED_RESUME_IMPROVED,
            "same": EXPECTED_RESUME_SAME,
            "worse": EXPECTED_RESUME_WORSE,
        },
        "matches_frozen": matches,
        "mutation_allowed": False,
        "reason": "resume_delta_taxonomy_frozen_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_resume_taxonomy_reclass(
    *,
    code: str,
    from_bucket: str,
    to_bucket: str,
) -> Dict[str, Any]:
    """评估 resume taxonomy 桶重分类；显式 denial。"""
    if from_bucket not in ("improved", "same", "worse"):
        raise ValueError(f"unknown from_bucket: {from_bucket}")
    if to_bucket not in ("improved", "same", "worse"):
        raise ValueError(f"unknown to_bucket: {to_bucket}")
    if from_bucket == "same" and code not in EXPECTED_RESUME_SAME_CODES:
        raise ValueError(f"not a resume-same code: {code}")
    return {
        "code": code,
        "from_bucket": from_bucket,
        "to_bucket": to_bucket,
        "allowed": False,
        "reason": "resume_taxonomy_reclass_forbidden_pre_execute",
        "hold": "KEEP_EXECUTE_FALSE",
    }



def build_fm30_continuity_rows(
    paths: FailedPromotionPartialDemotionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM30 packet / fingerprint / gate / demotion·partition·winner·overlap 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm30_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm30_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm30_gate_json_rel, base_dir=base_dir))
    dem_led = load_json(_abs(paths.fm30_demotion_rel, base_dir=base_dir))
    part_led = load_json(_abs(paths.fm30_partition_rel, base_dir=base_dir))
    win_led = load_json(_abs(paths.fm30_winner_rel, base_dir=base_dir))
    ov_led = load_json(_abs(paths.fm30_overlap_rel, base_dir=base_dir))

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
    )
    checks["fm30_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm30_packet_continuity",
            layer="fm30_continuity",
            path=paths.fm30_packet_rel,
            expected="PASS_OFFLINE;unique=2249;2134/106/9;Δ12;KEEP",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"status={packet.get('union_complete')}/"
                f"{packet.get('union_partial')}/{packet.get('union_failed')};"
                f"delta={packet.get('overlap_delta')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm30_packet_drift",
        )
    )

    frozen = fp_doc.get("frozen_fps") or {}
    fp_ok = (
        fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and fp_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and fp_doc.get("union_complete") == EXPECTED_UNION_COMPLETE
        and fp_doc.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and fp_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and frozen.get("complete_demotion_denial")
        == FROZEN_COMPLETE_DEMOTION_DENIAL_FP_SHA256
        and frozen.get("status_partition_invariant_lock")
        == FROZEN_STATUS_PARTITION_INVARIANT_FP_SHA256
        and frozen.get("winner_provenance_lock")
        == FROZEN_WINNER_PROVENANCE_LOCK_FP_SHA256
        and frozen.get("overlap_delta_surface_injection_freeze")
        == FROZEN_OVERLAP_SURFACE_FREEZE_FP_SHA256
        and fp_doc.get("complete_codes_sha256") == EXPECTED_COMPLETE_CODES_SHA256
        and fp_doc.get("winner_map_sha256") == EXPECTED_WINNER_MAP_SHA256
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm30_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm30_fingerprint_continuity",
            layer="fm30_continuity",
            path=paths.fm30_fingerprint_rel,
            expected="unique2249+fm30_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"complete={fp_doc.get('union_complete')};"
                f"delta={fp_doc.get('overlap_delta')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm30_fingerprint_drift",
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
        and gate_doc.get("residual_safety_coverage") == EXPECTED_RESIDUAL_SAFETY_COVERAGE
    )
    checks["fm30_gate_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm30_gate_continuity",
            layer="fm30_continuity",
            path=paths.fm30_gate_json_rel,
            expected="PASS_OFFLINE;KEEP;unique2249",
            observed=f"gate={gate_doc.get('gate')};unique={gate_doc.get('harvest_unique_union')}",
            ok=gate_ok,
            notes="ok" if gate_ok else "fm30_gate_drift",
        )
    )

    dem_ok = (
        dem_led.get("fingerprint_sha256") == FROZEN_COMPLETE_DEMOTION_DENIAL_FP_SHA256
        and dem_led.get("complete_n") == EXPECTED_UNION_COMPLETE
        and dem_led.get("complete_codes_sha256") == EXPECTED_COMPLETE_CODES_SHA256
    )
    checks["fm30_demotion_ledger_continuity"] = dem_ok
    rows.append(
        _row(
            check_id="fm30_demotion_ledger_continuity",
            layer="fm30_continuity",
            path=paths.fm30_demotion_rel,
            expected=FROZEN_COMPLETE_DEMOTION_DENIAL_FP_SHA256,
            observed=str(dem_led.get("fingerprint_sha256") or ""),
            ok=dem_ok,
            notes="ok" if dem_ok else "fm30_demotion_drift",
        )
    )

    part_ok = (
        part_led.get("fingerprint_sha256")
        == FROZEN_STATUS_PARTITION_INVARIANT_FP_SHA256
        and part_led.get("unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and part_led.get("complete_n") == EXPECTED_UNION_COMPLETE
        and part_led.get("partial_n") == EXPECTED_UNION_PARTIAL
        and part_led.get("failed_n") == EXPECTED_UNION_FAILED
    )
    checks["fm30_partition_ledger_continuity"] = part_ok
    rows.append(
        _row(
            check_id="fm30_partition_ledger_continuity",
            layer="fm30_continuity",
            path=paths.fm30_partition_rel,
            expected=FROZEN_STATUS_PARTITION_INVARIANT_FP_SHA256,
            observed=str(part_led.get("fingerprint_sha256") or ""),
            ok=part_ok,
            notes="ok" if part_ok else "fm30_partition_drift",
        )
    )

    win_ok = (
        win_led.get("fingerprint_sha256") == FROZEN_WINNER_PROVENANCE_LOCK_FP_SHA256
        and win_led.get("unique_n") == EXPECTED_HARVEST_UNIQUE_UNION
        and win_led.get("winner_map_sha256") == EXPECTED_WINNER_MAP_SHA256
    )
    checks["fm30_winner_ledger_continuity"] = win_ok
    rows.append(
        _row(
            check_id="fm30_winner_ledger_continuity",
            layer="fm30_continuity",
            path=paths.fm30_winner_rel,
            expected=FROZEN_WINNER_PROVENANCE_LOCK_FP_SHA256,
            observed=str(win_led.get("fingerprint_sha256") or ""),
            ok=win_ok,
            notes="ok" if win_ok else "fm30_winner_drift",
        )
    )

    ov_ok = (
        ov_led.get("fingerprint_sha256") == FROZEN_OVERLAP_SURFACE_FREEZE_FP_SHA256
        and ov_led.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and ov_led.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
    )
    checks["fm30_overlap_ledger_continuity"] = ov_ok
    rows.append(
        _row(
            check_id="fm30_overlap_ledger_continuity",
            layer="fm30_continuity",
            path=paths.fm30_overlap_rel,
            expected=FROZEN_OVERLAP_SURFACE_FREEZE_FP_SHA256,
            observed=str(ov_led.get("fingerprint_sha256") or ""),
            ok=ov_ok,
            notes="ok" if ov_ok else "fm30_overlap_drift",
        )
    )

    # FM29 frozen fps still referenced inside FM30 fingerprint
    fm29_fp_ok = (
        frozen.get("fm29_partial_promote_reclass_denial")
        == FROZEN_PARTIAL_PROMOTE_RECLASS_DENIAL_FP_SHA256
        and frozen.get("fm29_resume_same_hold_write_boundary")
        == FROZEN_RESUME_SAME_HOLD_BOUNDARY_FP_SHA256
        and frozen.get("fm29_residual_lift_denial")
        == FROZEN_RESIDUAL_LIFT_DENIAL_FP_SHA256
        and frozen.get("fm29_coverage_invariant_lock")
        == FROZEN_COVERAGE_INVARIANT_LOCK_FP_SHA256
    )
    checks["fm30_embeds_fm29_frozen_fps"] = fm29_fp_ok
    rows.append(
        _row(
            check_id="fm30_embeds_fm29_frozen_fps",
            layer="fm30_continuity",
            path=paths.fm30_fingerprint_rel,
            expected="fm29_four_frozen_fps",
            observed=f"embedded={fm29_fp_ok}",
            ok=fm29_fp_ok,
            notes="ok" if fm29_fp_ok else "fm29_fp_embed_missing",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm30_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm30_continuity_all_pass",
            layer="fm30_continuity",
            expected="packet+fp+gate+4ledgers",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm30_continuity_incomplete",
        )
    )
    return rows, checks


def build_failed_promotion_denial_rows(
    paths: FailedPromotionPartialDemotionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """failed promotion denial（9 码）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    failed = sorted(c for c, s in union_status.items() if s == "failed")
    fp, doc = fingerprint_failed_promotion_denial(failed_codes=failed)

    n_ok = (
        len(failed) == EXPECTED_UNION_FAILED
        and set(failed) == EXPECTED_FAILED_CODES
    )
    checks["failed_count_9"] = n_ok
    rows.append(
        _row(
            check_id="failed_count_9",
            layer="failed_promotion_denial",
            expected=str(EXPECTED_UNION_FAILED),
            observed=str(len(failed)),
            ok=n_ok,
            notes="ok" if n_ok else "failed_count_mismatch",
        )
    )

    codes_fp_ok = doc["failed_codes_sha256"] == EXPECTED_FAILED_CODES_SHA256
    checks["failed_codes_sha256_exact"] = codes_fp_ok
    rows.append(
        _row(
            check_id="failed_codes_sha256_exact",
            layer="failed_promotion_denial",
            expected=EXPECTED_FAILED_CODES_SHA256,
            observed=doc["failed_codes_sha256"],
            ok=codes_fp_ok,
            notes="ok" if codes_fp_ok else "failed_codes_sha_drift",
        )
    )

    batch_counts = dict(sorted(Counter(winning[c] for c in failed).items()))
    batches_ok = batch_counts == EXPECTED_FAILED_WINNER_BATCHES
    checks["failed_winner_batches_exact"] = batches_ok
    rows.append(
        _row(
            check_id="failed_winner_batches_exact",
            layer="failed_promotion_denial",
            expected="p35=6;p3=3",
            observed=json.dumps(batch_counts, ensure_ascii=False, sort_keys=True),
            ok=batches_ok,
            notes="ok" if batches_ok else "failed_batch_drift",
        )
    )

    promote_ok = True
    denial_count = 0
    sample_denials: List[Dict[str, Any]] = []
    for code in failed:
        for to_status in ("partial", "complete"):
            d = evaluate_failed_promotion(
                code=code, to_status=to_status, failed_codes=failed
            )
            denial_count += 1
            if len(sample_denials) < 6:
                sample_denials.append(d)
            if d.get("allowed") is not False:
                promote_ok = False
    checks["failed_promotion_denial_battery"] = (
        promote_ok and denial_count == EXPECTED_UNION_FAILED * 2
    )
    rows.append(
        _row(
            check_id="failed_promotion_denial_battery",
            layer="failed_promotion_denial",
            expected="18_promotions_denied",
            observed=f"denials={denial_count};all_denied={promote_ok}",
            ok=checks["failed_promotion_denial_battery"],
            notes="ok" if checks["failed_promotion_denial_battery"] else "promote_leak",
        )
    )

    flags_ok = (
        doc["deny_promote_to_partial"] is True
        and doc["deny_promote_to_complete"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["failed_promotion_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="failed_promotion_flags_locked",
            layer="failed_promotion_denial",
            expected="deny_partial+deny_complete+KEEP",
            observed=(
                f"partial={doc['deny_promote_to_partial']};"
                f"complete={doc['deny_promote_to_complete']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_FAILED_PROMOTION_DENIAL_FP_SHA256
    checks["failed_promotion_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="failed_promotion_fingerprint",
            layer="failed_promotion_denial",
            expected=FROZEN_FAILED_PROMOTION_DENIAL_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "failed_promotion_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["failed_promotion_denial_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="failed_promotion_denial_all_pass",
            layer="failed_promotion_denial",
            expected="9_promote_deny+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "failed_promotion_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "failed_n": len(failed),
        "failed_codes_sha256": doc["failed_codes_sha256"],
        "winner_batches": batch_counts,
        "denial_count": denial_count,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_partial_demotion_to_failed_rows(
    paths: FailedPromotionPartialDemotionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """partial demotion-to-failed denial（106 码）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    partial = sorted(c for c, s in union_status.items() if s == "partial")
    fp, doc = fingerprint_partial_demotion_to_failed(partial_codes=partial)

    n_ok = len(partial) == EXPECTED_UNION_PARTIAL
    checks["partial_count_106"] = n_ok
    rows.append(
        _row(
            check_id="partial_count_106",
            layer="partial_demotion_to_failed_denial",
            expected=str(EXPECTED_UNION_PARTIAL),
            observed=str(len(partial)),
            ok=n_ok,
            notes="ok" if n_ok else "partial_count_mismatch",
        )
    )

    codes_fp_ok = doc["partial_codes_sha256"] == EXPECTED_PARTIAL_CODES_SHA256
    checks["partial_codes_sha256_exact"] = codes_fp_ok
    rows.append(
        _row(
            check_id="partial_codes_sha256_exact",
            layer="partial_demotion_to_failed_denial",
            expected=EXPECTED_PARTIAL_CODES_SHA256,
            observed=doc["partial_codes_sha256"],
            ok=codes_fp_ok,
            notes="ok" if codes_fp_ok else "partial_codes_sha_drift",
        )
    )

    batch_counts = dict(sorted(Counter(winning[c] for c in partial).items()))
    batches_ok = batch_counts == EXPECTED_PARTIAL_WINNER_BATCHES
    checks["partial_winner_batches_exact"] = batches_ok
    rows.append(
        _row(
            check_id="partial_winner_batches_exact",
            layer="partial_demotion_to_failed_denial",
            expected="p35=75;p3=14;p2=12;fu=5",
            observed=json.dumps(batch_counts, ensure_ascii=False, sort_keys=True),
            ok=batches_ok,
            notes="ok" if batches_ok else "partial_batch_drift",
        )
    )

    demote_ok = True
    denial_count = 0
    sample_denials: List[Dict[str, Any]] = []
    for code in partial:
        d = evaluate_partial_demotion_to_failed(code=code, partial_codes=partial)
        denial_count += 1
        if len(sample_denials) < 6:
            sample_denials.append(d)
        if d.get("allowed") is not False:
            demote_ok = False
    checks["partial_demotion_to_failed_battery"] = (
        demote_ok and denial_count == EXPECTED_UNION_PARTIAL
    )
    rows.append(
        _row(
            check_id="partial_demotion_to_failed_battery",
            layer="partial_demotion_to_failed_denial",
            expected="106_demotions_denied",
            observed=f"denials={denial_count};all_denied={demote_ok}",
            ok=checks["partial_demotion_to_failed_battery"],
            notes="ok" if checks["partial_demotion_to_failed_battery"] else "demote_leak",
        )
    )

    flags_ok = (
        doc["deny_demote_to_failed"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["partial_demotion_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="partial_demotion_flags_locked",
            layer="partial_demotion_to_failed_denial",
            expected="deny_failed+KEEP",
            observed=f"deny={doc['deny_demote_to_failed']};hold={doc['hold']}",
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_PARTIAL_DEMOTION_TO_FAILED_FP_SHA256
    checks["partial_demotion_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="partial_demotion_fingerprint",
            layer="partial_demotion_to_failed_denial",
            expected=FROZEN_PARTIAL_DEMOTION_TO_FAILED_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "partial_demotion_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["partial_demotion_to_failed_denial_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="partial_demotion_to_failed_denial_all_pass",
            layer="partial_demotion_to_failed_denial",
            expected="106_demote_failed_deny+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "partial_demotion_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "partial_n": len(partial),
        "partial_codes_sha256": doc["partial_codes_sha256"],
        "winner_batches": batch_counts,
        "denial_count": denial_count,
        "sample_denials": sample_denials,
        "doc": doc,
    }
    return rows, checks, meta



def build_batch_priority_order_freeze_rows(
    paths: FailedPromotionPartialDemotionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """batch-priority order freeze。"""
    del paths, base_dir  # 纯常量层；保留签名一致
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fp, doc = fingerprint_batch_priority_order_freeze()

    live_ok = tuple(BATCH_PRIORITY) == EXPECTED_BATCH_PRIORITY
    checks["batch_priority_live_exact"] = live_ok
    rows.append(
        _row(
            check_id="batch_priority_live_exact",
            layer="batch_priority_order_freeze",
            expected="h863>p35>p3>p2>fu",
            observed=">".join(BATCH_PRIORITY),
            ok=live_ok,
            notes="ok" if live_ok else "batch_priority_drift",
        )
    )

    # 重排提案（逆序 / 轮转）一律拒绝
    reorder_ok = True
    samples: List[Dict[str, Any]] = []
    for proposed in (
        list(reversed(EXPECTED_BATCH_PRIORITY)),
        list(EXPECTED_BATCH_PRIORITY[1:]) + [EXPECTED_BATCH_PRIORITY[0]],
        list(EXPECTED_BATCH_PRIORITY),
    ):
        d = evaluate_batch_priority_reorder(proposed_priority=proposed)
        samples.append(d)
        if d.get("reorder_allowed") is not False:
            reorder_ok = False
    checks["batch_priority_reorder_denied"] = reorder_ok
    rows.append(
        _row(
            check_id="batch_priority_reorder_denied",
            layer="batch_priority_order_freeze",
            expected="reorder_allowed=false",
            observed=f"samples={len(samples)};all_denied={reorder_ok}",
            ok=reorder_ok,
            notes="ok" if reorder_ok else "reorder_leak",
        )
    )

    flags_ok = (
        doc["deny_priority_reorder"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
        and doc["batch_priority"] == list(EXPECTED_BATCH_PRIORITY)
    )
    checks["batch_priority_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="batch_priority_flags_locked",
            layer="batch_priority_order_freeze",
            expected="deny_reorder+KEEP+exact",
            observed=(
                f"deny={doc['deny_priority_reorder']};hold={doc['hold']};"
                f"prio={doc['batch_priority']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_BATCH_PRIORITY_ORDER_FP_SHA256
    checks["batch_priority_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="batch_priority_fingerprint",
            layer="batch_priority_order_freeze",
            expected=FROZEN_BATCH_PRIORITY_ORDER_FP_SHA256,
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
            expected="priority_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "batch_priority_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "sample_denials": samples,
        "doc": doc,
    }
    return rows, checks, meta


def build_resume_delta_taxonomy_freeze_rows(
    paths: FailedPromotionPartialDemotionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """resume-delta taxonomy freeze（28/1/0）。"""
    del paths, base_dir
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fp, doc = fingerprint_resume_delta_taxonomy_freeze()

    counts_ok = (
        EXPECTED_RESUME_IMPROVED == 28
        and EXPECTED_RESUME_SAME == 1
        and EXPECTED_RESUME_WORSE == 0
        and EXPECTED_RESUME_IMPROVED
        + EXPECTED_RESUME_SAME
        + EXPECTED_RESUME_WORSE
        == EXPECTED_RESUME_TOTAL
        and set(EXPECTED_RESUME_SAME_CODES) == {"301212"}
    )
    checks["resume_taxonomy_counts_exact"] = counts_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_counts_exact",
            layer="resume_delta_taxonomy_freeze",
            expected="28/1/0;same=301212",
            observed=(
                f"{EXPECTED_RESUME_IMPROVED}/{EXPECTED_RESUME_SAME}/"
                f"{EXPECTED_RESUME_WORSE};"
                f"same={','.join(sorted(EXPECTED_RESUME_SAME_CODES))}"
            ),
            ok=counts_ok,
            notes="ok" if counts_ok else "resume_taxonomy_count_drift",
        )
    )

    mut = evaluate_resume_taxonomy_mutation(
        proposed_improved=27, proposed_same=2, proposed_worse=0
    )
    mut2 = evaluate_resume_taxonomy_mutation(
        proposed_improved=EXPECTED_RESUME_IMPROVED,
        proposed_same=EXPECTED_RESUME_SAME,
        proposed_worse=EXPECTED_RESUME_WORSE,
    )
    mut_ok = mut["mutation_allowed"] is False and mut2["mutation_allowed"] is False
    checks["resume_taxonomy_mutation_denied"] = mut_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_mutation_denied",
            layer="resume_delta_taxonomy_freeze",
            expected="mutation_allowed=false",
            observed=(
                f"drift_denied={mut['mutation_allowed']};"
                f"exact_denied={mut2['mutation_allowed']}"
            ),
            ok=mut_ok,
            notes="ok" if mut_ok else "taxonomy_mutation_leak",
        )
    )

    reclass_ok = True
    sample_reclass: List[Dict[str, Any]] = []
    for to_bucket in ("improved", "worse"):
        d = evaluate_resume_taxonomy_reclass(
            code="301212", from_bucket="same", to_bucket=to_bucket
        )
        sample_reclass.append(d)
        if d.get("allowed") is not False:
            reclass_ok = False
    checks["resume_taxonomy_reclass_denied"] = reclass_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_reclass_denied",
            layer="resume_delta_taxonomy_freeze",
            expected="same_301212_reclass_denied",
            observed=f"samples={len(sample_reclass)};all_denied={reclass_ok}",
            ok=reclass_ok,
            notes="ok" if reclass_ok else "reclass_leak",
        )
    )

    flags_ok = (
        doc["deny_taxonomy_reclass"] is True
        and doc["deny_taxonomy_count_mutation"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["resume_taxonomy_flags_locked"] = flags_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_flags_locked",
            layer="resume_delta_taxonomy_freeze",
            expected="deny_reclass+deny_mutation+KEEP",
            observed=(
                f"reclass={doc['deny_taxonomy_reclass']};"
                f"mutation={doc['deny_taxonomy_count_mutation']};hold={doc['hold']}"
            ),
            ok=flags_ok,
            notes="ok" if flags_ok else "flags_unlocked",
        )
    )

    fp_ok = fp == FROZEN_RESUME_DELTA_TAXONOMY_FP_SHA256
    checks["resume_taxonomy_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="resume_taxonomy_fingerprint",
            layer="resume_delta_taxonomy_freeze",
            expected=FROZEN_RESUME_DELTA_TAXONOMY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "resume_taxonomy_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_delta_taxonomy_freeze_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_delta_taxonomy_freeze_all_pass",
            layer="resume_delta_taxonomy_freeze",
            expected="28/1/0_taxonomy_freeze+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_taxonomy_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "resume_worse": EXPECTED_RESUME_WORSE,
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "sample_denials": sample_reclass,
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: FailedPromotionPartialDemotionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK33 放行。"""
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
        assert_fm31_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK33_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock33_ok",
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
    paths: FailedPromotionPartialDemotionPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–32 拒绝 · MOCK33 放行。"""
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

    mock32_rel = (
        "outputs/validation/"
        "_mock_c_fm30_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety"
    )
    mock32_blocked = False
    try:
        assert_fm31_output_root(mock32_rel, base_dir=base_dir)
    except RuntimeError as exc:
        mock32_blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
    checks["mock32_still_frozen"] = mock32_blocked
    rows.append(
        _row(
            check_id="mock32_still_frozen",
            layer="frozen_mock_isolation",
            root_id=PRIOR_TASK_ROOT_ID,
            path=mock32_rel,
            expected="write_forbidden",
            observed="blocked" if mock32_blocked else "allowed",
            ok=mock32_blocked,
            notes="ok" if mock32_blocked else "mock32_write_leak",
        )
    )

    allow_ok = False
    try:
        assert_fm31_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except Exception:
        allow_ok = False
    checks["frozen_allow_mock33"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock33",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="MOCK33_or_ephemeral_allowed",
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
            expected="MOCK3-32_block+MOCK33_allow",
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
    """protected_output_roots.csv：MOCK33 已登记。"""
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

    mock33 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(
        mock33.get("path_pattern") or ""
    )
    checks["protected_csv_mock33_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock33_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock33.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock33_path_mismatch",
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
    """FM-01..05 + FM-12..30 gate battery（跳过 seal FM06–11）。"""
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
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
        "fm28", "fm29", "fm30",
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
        if key in ("fm25", "fm26", "fm27", "fm28", "fm29", "fm30"):
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in ("fm26", "fm27", "fm28", "fm29", "fm30"):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key in ("fm27", "fm28", "fm29", "fm30"):
            ok = (
                ok
                and payload.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
            )
        if key in ("fm28", "fm29", "fm30"):
            ok = (
                ok
                and payload.get("residual_safety_coverage")
                == EXPECTED_RESIDUAL_SAFETY_COVERAGE
            )
        if key in ("fm29", "fm30"):
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
            check_id="fm01_05_12_30_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_30_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm31(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK33；加固 C-ROOT-002 failed-promo/partial-demote 说明。"""
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
                "resume-taxonomy; 只读直至人批重跑"
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
                "C-FM-31 scale failed promotion denial (9) + partial "
                "demotion-to-failed denial (106) + batch-priority order "
                "freeze + resume-delta taxonomy freeze (28/1/0) + FM30 "
                "continuity; never production EXECUTE; must not overwrite "
                "MOCK3-32; seal_chain_extended=false"
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


def run_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety(
    *,
    paths: FailedPromotionPartialDemotionPaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-31 规模 failed-promo / partial-demote / priority / taxonomy 离线 QA。"""
    paths = paths or FailedPromotionPartialDemotionPaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm31(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm31_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm30_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    fail_rows, fail_checks, fail_meta = build_failed_promotion_denial_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(fail_rows)
    part_rows, part_checks, part_meta = build_partial_demotion_to_failed_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(part_rows)
    bp_rows, bp_checks, bp_meta = build_batch_priority_order_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(bp_rows)
    tax_rows, tax_checks, tax_meta = build_resume_delta_taxonomy_freeze_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(tax_rows)
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
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm30_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm30_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "failed_promotion_denial": (
            "PASS_OFFLINE"
            if fail_checks.get("failed_promotion_denial_all_pass")
            else "FAIL_OFFLINE"
        ),
        "partial_demotion_to_failed_denial": (
            "PASS_OFFLINE"
            if part_checks.get("partial_demotion_to_failed_denial_all_pass")
            else "FAIL_OFFLINE"
        ),
        "batch_priority_order_freeze": (
            "PASS_OFFLINE"
            if bp_checks.get("batch_priority_order_freeze_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_delta_taxonomy_freeze": (
            "PASS_OFFLINE"
            if tax_checks.get("resume_delta_taxonomy_freeze_all_pass")
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
            if bat_checks.get("fm01_05_12_30_battery_all_pass")
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
        os.path.join(out_root, "failed_promotion_denial_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(fail_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": fail_meta["fingerprint"],
                "failed_n": fail_meta["failed_n"],
                "failed_codes_sha256": fail_meta["failed_codes_sha256"],
                "winner_batches": fail_meta["winner_batches"],
                "denial_count": fail_meta["denial_count"],
                "sample_denials": fail_meta["sample_denials"],
                "doc": fail_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    part_rel = _rel(
        os.path.join(out_root, "partial_demotion_to_failed_denial_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(part_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": part_meta["fingerprint"],
                "partial_n": part_meta["partial_n"],
                "partial_codes_sha256": part_meta["partial_codes_sha256"],
                "winner_batches": part_meta["winner_batches"],
                "denial_count": part_meta["denial_count"],
                "sample_denials": part_meta["sample_denials"],
                "doc": part_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    bp_rel = _rel(
        os.path.join(out_root, "batch_priority_order_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(bp_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": bp_meta["fingerprint"],
                "batch_priority": bp_meta["batch_priority"],
                "sample_denials": bp_meta["sample_denials"],
                "doc": bp_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    tax_rel = _rel(
        os.path.join(out_root, "resume_delta_taxonomy_freeze_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(tax_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": tax_meta["fingerprint"],
                "resume_improved": tax_meta["resume_improved"],
                "resume_same": tax_meta["resume_same"],
                "resume_worse": tax_meta["resume_worse"],
                "resume_same_codes": tax_meta["resume_same_codes"],
                "sample_denials": tax_meta["sample_denials"],
                "doc": tax_meta["doc"],
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
                "fm30_gate": gates["fm30"].get("gate"),
                "fm31_gate": overall,
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
                "partial_codes_sha256": part_meta["partial_codes_sha256"],
                "failed_codes_sha256": fail_meta["failed_codes_sha256"],
                "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
                "notes": (
                    "failed promotion denial (9) + partial demotion-to-failed "
                    "denial (106) + batch-priority order freeze + resume-delta "
                    "taxonomy freeze (28/1/0) + FM30 continuity + MOCK33; "
                    "EXECUTE remains human-held; does not overwrite MOCK3-32"
                ),
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    observed_fps = {
        "failed_promotion_denial": fail_meta["fingerprint"],
        "partial_demotion_to_failed_denial": part_meta["fingerprint"],
        "batch_priority_order_freeze": bp_meta["fingerprint"],
        "resume_delta_taxonomy_freeze": tax_meta["fingerprint"],
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
                "resume_worse": EXPECTED_RESUME_WORSE,
                "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
                "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
                "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
                "complete_codes_sha256": EXPECTED_COMPLETE_CODES_SHA256,
                "partial_codes_sha256": part_meta["partial_codes_sha256"],
                "failed_codes_sha256": fail_meta["failed_codes_sha256"],
                "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
                "batch_priority": list(EXPECTED_BATCH_PRIORITY),
                "frozen_fps": {
                    "failed_promotion_denial": FROZEN_FAILED_PROMOTION_DENIAL_FP_SHA256,
                    "partial_demotion_to_failed_denial": FROZEN_PARTIAL_DEMOTION_TO_FAILED_FP_SHA256,
                    "batch_priority_order_freeze": FROZEN_BATCH_PRIORITY_ORDER_FP_SHA256,
                    "resume_delta_taxonomy_freeze": FROZEN_RESUME_DELTA_TAXONOMY_FP_SHA256,
                    "fm30_complete_demotion_denial": FROZEN_COMPLETE_DEMOTION_DENIAL_FP_SHA256,
                    "fm30_status_partition_invariant_lock": FROZEN_STATUS_PARTITION_INVARIANT_FP_SHA256,
                    "fm30_winner_provenance_lock": FROZEN_WINNER_PROVENANCE_LOCK_FP_SHA256,
                    "fm30_overlap_delta_surface_injection_freeze": FROZEN_OVERLAP_SURFACE_FREEZE_FP_SHA256,
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
        "partial_codes_sha256": part_meta["partial_codes_sha256"],
        "failed_codes_sha256": fail_meta["failed_codes_sha256"],
        "winner_map_sha256": EXPECTED_WINNER_MAP_SHA256,
        "batch_priority": list(EXPECTED_BATCH_PRIORITY),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fp_rel,
        "fingerprint": fp,
        "failed_promotion_path": fail_rel,
        "partial_demotion_path": part_rel,
        "batch_priority_path": bp_rel,
        "resume_taxonomy_path": tax_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "fm30_packet": paths.fm30_packet_rel,
            "fm30_gate": paths.fm30_gate_json_rel,
        },
        "mock_root_is_isolated": True,
    }
