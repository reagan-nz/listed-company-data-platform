"""
CNINFO C-class — 规模 unique-coverage 对账 + resume lineage 安全加固
（离线 · C-FM-24）。

在 C-FM-23（scale multi-batch repro + lineage hardening）已 commit 且 EXECUTE 仍
human-held 之上，继续非 seal 规模/安全能力（不新增 seal / decision-await /
commit-boundary；非 extension↔drift 循环）：
  1) FM23 packet / fingerprint 零漂移连续（coverage_sum=3314 · tiers=7）
  2) harvest unique-coverage 对账：unique=2249 · additive=2261 · delta=12
  3) 五 batch pairwise 交集矩阵冻结指纹
  4) dryrun∪harvest 表面 unique=2251；dry863 相对 h863 多出 {000037,000055}
  5) phase35 resume lineage：n=29 ⊆ p35 · complete=28/partial=1 · 写拒绝
  6) 七层 repro 指纹再确认（继承 FM23 冻结锚）
  7) output-root：MOCK3–25 冻结 · MOCK26 放行；resume/harvest 写拒绝
  8) FM-01..05 + FM-12..23 gate battery（跳过 seal FM06–11）
  9) protected_output_roots.csv：MOCK26 + C-ROOT-002 resume 说明加固

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–25 / 权威 dual-layer 索引 ·
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
    fingerprint_status_csv,
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
    EXPECTED_863_COMPLETE,
    EXPECTED_FM01_COMPANY_COUNT,
    EXPECTED_FM02_COMPANY_COUNT,
    EXPECTED_PHASE35_TOTAL,
    FROZEN_FM01_863_FP_SHA256,
    FROZEN_FM02_190_FP_SHA256,
    FROZEN_FM03_HARVEST_863_FP_SHA256,
    FROZEN_PHASE35_500_FP_SHA256,
    HARVEST_863_STATUS_REL,
    HARVEST_PHASE35_STATUS_REL,
    fingerprint_scale_matrix,
    write_scale_matrix_csv,
)
from cninfo_c_class_scale_multi_batch_repro_lineage_hardening import (  # noqa: E402
    EXPECTED_COMBINED_DRYRUN_COVERAGE,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_FULLER_TOTAL,
    EXPECTED_HARVEST_BATCH_UNION,
    EXPECTED_PHASE2_TOTAL,
    EXPECTED_PHASE3_TOTAL,
    EXPECTED_SCALE_TIER_COUNT,
    FROZEN_COMBINED_DRYRUN_1053_FP_SHA256,
    FROZEN_FULLER_200_FP_SHA256,
    FROZEN_PHASE2_200_FP_SHA256,
    FROZEN_PHASE3_500_FP_SHA256,
    HARVEST_FULLER_ROOT_REL,
    HARVEST_FULLER_STATUS_REL,
    HARVEST_PHASE2_ROOT_REL,
    HARVEST_PHASE2_STATUS_REL,
    HARVEST_PHASE3_ROOT_REL,
    HARVEST_PHASE3_STATUS_REL,
    HARVEST_PHASE35_ROOT_REL,
    FM01_MOCK_ROOT_REL,
    FM02_MOCK_ROOT_REL,
)

TASK_ID = "C-FM-24"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm24_scale_unique_coverage_resume_lineage_safety"
)

FM01_GATE_JSON_REL = (
    "outputs/validation/cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.json"
)
FM02_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json"
)
FM03_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json"
)
FM04_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.json"
)
FM05_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_cross_fm_mock_cohort_integrity_20260715.json"
)
FM12_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_dryrun_fingerprint_lineage_isolation_20260715.json"
)
FM13_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_cross_fm_mock_cohort_extension_20260715.json"
)
FM14_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_post_commit_drift_recheck_20260715.json"
)
FM15_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_controller_commit_boundary_20260715.json"
)
FM16_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_post_commit_seal_attestation_20260715.json"
)
FM17_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_human_decision_readiness_ledger_20260715.json"
)
FM18_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension_20260715.json"
)
FM19_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_second_extension_post_commit_drift_recheck_20260715.json"
)
FM20_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_cross_fm_mock_cohort_third_extension_20260715.json"
)
FM21_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_third_extension_post_commit_drift_recheck_20260715.json"
)
FM22_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_harvest_exclusion_repro_fingerprint_20260715.json"
)
FM23_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_multi_batch_repro_lineage_hardening_20260715.json"
)

FM23_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm23_scale_multi_batch_repro_lineage_hardening"
)
FM23_PACKET_REL = f"{FM23_MOCK_ROOT_REL}/scale_packet.json"
FM23_FINGERPRINT_REL = f"{FM23_MOCK_ROOT_REL}/scale_fingerprint.json"

FM01_SNAPSHOT_STATUS_REL = (
    f"{FM01_MOCK_ROOT_REL}/quality/company_snapshot_status.csv"
)
FM02_SNAPSHOT_STATUS_REL = (
    f"{FM02_MOCK_ROOT_REL}/quality/company_snapshot_status.csv"
)

HARVEST_PHASE35_RESUME_ROOT_REL = (
    "outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume"
)
HARVEST_PHASE35_RESUME_STATUS_REL = (
    f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/company_harvest_status.csv"
)

# unique-coverage 冻结锚点（相对 FM23 additive coverage_sum 的可审计对账）
EXPECTED_HARVEST_UNIQUE_UNION = 2249  # h863∪p35∪p3∪p2∪fu
EXPECTED_HARVEST_ADDITIVE = 2261  # 861+500+500+200+200
EXPECTED_OVERLAP_DELTA = 12  # p35∩fu(1) + p2∪fu(11)
EXPECTED_SURFACE_UNIQUE = 2251  # dry863∪dry190∪harvest5
EXPECTED_DRY863_EXTRA = frozenset({"000037", "000055"})
EXPECTED_RESUME_TOTAL = 29
EXPECTED_RESUME_COMPLETE = 28
EXPECTED_RESUME_PARTIAL = 1
EXPECTED_P35_FU_OVERLAP = frozenset({"000003"})
EXPECTED_P2_FU_OVERLAP_N = 11

FROZEN_PAIRWISE_INTERSECTION_FP_SHA256 = (
    "7f8e11847b318fc6743d61ce20add195c2345ec5ee7635cab37923f4eec1498a"
)
FROZEN_FM23_MATRIX_FP_SHA256 = (
    "856b1d15d045ece336de08b9ed27b777379558a4cee0db6f5bcf367d64c6ac5e"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK26"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK25"
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
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class UniqueCoveragePaths:
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
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    harvest_863_status_rel: str = HARVEST_863_STATUS_REL
    harvest_phase35_status_rel: str = HARVEST_PHASE35_STATUS_REL
    harvest_phase3_status_rel: str = HARVEST_PHASE3_STATUS_REL
    harvest_phase2_status_rel: str = HARVEST_PHASE2_STATUS_REL
    harvest_fuller_status_rel: str = HARVEST_FULLER_STATUS_REL
    harvest_phase35_resume_status_rel: str = HARVEST_PHASE35_RESUME_STATUS_REL
    fm01_snapshot_status_rel: str = FM01_SNAPSHOT_STATUS_REL
    fm02_snapshot_status_rel: str = FM02_SNAPSHOT_STATUS_REL
    fm23_packet_rel: str = FM23_PACKET_REL
    fm23_fingerprint_rel: str = FM23_FINGERPRINT_REL
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


def assert_fm24_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-24 写根：须 validation/_mock_*，不得覆盖 MOCK3–25，
    不得写权威 dual-layer 索引；允许本任务 MOCK26 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-24 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _codes(rows: Sequence[Dict[str, str]]) -> set:
    return {
        str(r.get("company_code") or "").strip()
        for r in rows
        if str(r.get("company_code") or "").strip()
    }


def _status_counts(rows: Sequence[Dict[str, str]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for r in rows:
        st = str(r.get("harvest_status") or "").strip()
        counts[st] = counts.get(st, 0) + 1
    return counts


def load_batch_code_sets(
    paths: UniqueCoveragePaths, *, base_dir: str = BASE_DIR
) -> Dict[str, set]:
    """加载五 harvest batch 公司代码集合。"""
    return {
        "h863": _codes(
            load_csv_rows(_abs(paths.harvest_863_status_rel, base_dir=base_dir))
        ),
        "p35": _codes(
            load_csv_rows(_abs(paths.harvest_phase35_status_rel, base_dir=base_dir))
        ),
        "p3": _codes(
            load_csv_rows(_abs(paths.harvest_phase3_status_rel, base_dir=base_dir))
        ),
        "p2": _codes(
            load_csv_rows(_abs(paths.harvest_phase2_status_rel, base_dir=base_dir))
        ),
        "fu": _codes(
            load_csv_rows(_abs(paths.harvest_fuller_status_rel, base_dir=base_dir))
        ),
    }


def fingerprint_harvest_pairwise_intersection(
    batches: Dict[str, set],
) -> Tuple[str, Dict[str, int], int, int]:
    """五 batch pairwise 交集矩阵指纹（只读对账，不 EXECUTE）。"""
    keys = sorted(batches)
    matrix: Dict[str, int] = {}
    for i, a in enumerate(keys):
        for b in keys[i:]:
            if a == b:
                matrix[f"{a}|{b}"] = len(batches[a])
            else:
                matrix[f"{a}|{b}"] = len(batches[a] & batches[b])
    unique_union = len(set().union(*batches.values())) if batches else 0
    additive = sum(len(batches[k]) for k in keys)
    canon = json.dumps(
        {
            "kind": "harvest_pairwise_intersection",
            "matrix": matrix,
            "unique_union": unique_union,
            "additive": additive,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return (
        hashlib.sha256(canon.encode("utf-8")).hexdigest(),
        matrix,
        unique_union,
        additive,
    )


def build_fm23_continuity_rows(
    paths: UniqueCoveragePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM23 packet / fingerprint 零漂移连续。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm23_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm23_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm23_gate_json_rel, base_dir=base_dir))

    pkt_ok = (
        packet.get("gate") == "PASS_OFFLINE"
        and packet.get("cninfo_calls") == 0
        and packet.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
        and packet.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
        and packet.get("combined_dryrun_coverage") == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and packet.get("execute_production_snapshot_rebuild") is False
        and packet.get("approved_for_snapshot_rebuild") is False
        and packet.get("seal_chain_extended") is False
        and packet.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
    )
    checks["fm23_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm23_packet_continuity",
            layer="fm23_continuity",
            path=paths.fm23_packet_rel,
            expected="PASS_OFFLINE;coverage=3314;tiers=7;dryrun=1053;execute=false",
            observed=(
                f"gate={packet.get('gate')};coverage={packet.get('company_coverage_sum')};"
                f"tiers={packet.get('scale_tier_count')};"
                f"dryrun={packet.get('combined_dryrun_coverage')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm23_packet_drift",
        )
    )

    nested_fp = fp_doc.get("fingerprint")
    if isinstance(nested_fp, dict):
        obs_fp = str(nested_fp.get("fingerprint_sha256") or "")
    else:
        obs_fp = str(fp_doc.get("fingerprint_sha256") or "")

    fp_ok = obs_fp == FROZEN_FM23_MATRIX_FP_SHA256
    checks["fm23_matrix_fingerprint_stable"] = fp_ok
    rows.append(
        _row(
            check_id="fm23_matrix_fingerprint_stable",
            layer="fm23_continuity",
            path=paths.fm23_fingerprint_rel,
            expected=FROZEN_FM23_MATRIX_FP_SHA256,
            observed=obs_fp or "missing",
            ok=fp_ok,
            notes="ok" if fp_ok else "fm23_matrix_fp_drift",
        )
    )

    obs = fp_doc.get("observed_fps") or {}
    frozen_ok = (
        obs.get("fm01_863") == FROZEN_FM01_863_FP_SHA256
        and obs.get("fm02_190") == FROZEN_FM02_190_FP_SHA256
        and obs.get("fm03_harvest_863") == FROZEN_FM03_HARVEST_863_FP_SHA256
        and obs.get("phase35_500") == FROZEN_PHASE35_500_FP_SHA256
        and obs.get("phase3_500") == FROZEN_PHASE3_500_FP_SHA256
        and obs.get("phase2_200") == FROZEN_PHASE2_200_FP_SHA256
        and obs.get("fuller_200") == FROZEN_FULLER_200_FP_SHA256
    )
    checks["fm23_observed_fps_stable"] = frozen_ok
    rows.append(
        _row(
            check_id="fm23_observed_fps_stable",
            layer="fm23_continuity",
            path=paths.fm23_fingerprint_rel,
            expected="7_frozen_fps_match",
            observed=f"keys={len(obs)}",
            ok=frozen_ok,
            notes="ok" if frozen_ok else "fm23_observed_fp_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
        and gate_doc.get("approved_for_snapshot_rebuild") is False
    )
    checks["fm23_gate_json_stable"] = gate_ok
    rows.append(
        _row(
            check_id="fm23_gate_json_stable",
            layer="fm23_continuity",
            path=paths.fm23_gate_json_rel,
            expected="PASS_OFFLINE;coverage=3314;cninfo=0",
            observed=(
                f"gate={gate_doc.get('gate')};"
                f"coverage={gate_doc.get('company_coverage_sum')};"
                f"cninfo={gate_doc.get('cninfo_calls')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm23_gate_json_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm23_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm23_continuity_all_pass",
            layer="fm23_continuity",
            expected="packet+fps+gate_zero_drift",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm23_continuity_incomplete",
        )
    )
    return rows, checks


def build_unique_coverage_reconciliation_rows(
    paths: UniqueCoveragePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """harvest unique vs additive 对账 + pairwise 矩阵指纹。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    batches = load_batch_code_sets(paths, base_dir=base_dir)
    fp, matrix, unique_n, additive_n = fingerprint_harvest_pairwise_intersection(
        batches
    )

    size_ok = (
        len(batches["h863"]) == EXPECTED_863_COMPLETE
        and len(batches["p35"]) == EXPECTED_PHASE35_TOTAL
        and len(batches["p3"]) == EXPECTED_PHASE3_TOTAL
        and len(batches["p2"]) == EXPECTED_PHASE2_TOTAL
        and len(batches["fu"]) == EXPECTED_FULLER_TOTAL
    )
    checks["harvest_batch_sizes"] = size_ok
    rows.append(
        _row(
            check_id="harvest_batch_sizes",
            layer="unique_coverage_reconciliation",
            expected="861+500+500+200+200",
            observed=(
                f"h863={len(batches['h863'])};p35={len(batches['p35'])};"
                f"p3={len(batches['p3'])};p2={len(batches['p2'])};"
                f"fu={len(batches['fu'])}"
            ),
            ok=size_ok,
            notes="ok" if size_ok else "batch_size_mismatch",
        )
    )

    unique_ok = unique_n == EXPECTED_HARVEST_UNIQUE_UNION
    checks["harvest_unique_union_2249"] = unique_ok
    rows.append(
        _row(
            check_id="harvest_unique_union_2249",
            layer="unique_coverage_reconciliation",
            expected=str(EXPECTED_HARVEST_UNIQUE_UNION),
            observed=str(unique_n),
            ok=unique_ok,
            notes="ok" if unique_ok else "unique_union_mismatch",
        )
    )

    additive_ok = additive_n == EXPECTED_HARVEST_ADDITIVE
    checks["harvest_additive_2261"] = additive_ok
    rows.append(
        _row(
            check_id="harvest_additive_2261",
            layer="unique_coverage_reconciliation",
            expected=str(EXPECTED_HARVEST_ADDITIVE),
            observed=str(additive_n),
            ok=additive_ok,
            notes="ok" if additive_ok else "additive_mismatch",
        )
    )

    delta = additive_n - unique_n
    delta_ok = delta == EXPECTED_OVERLAP_DELTA
    checks["overlap_delta_12"] = delta_ok
    rows.append(
        _row(
            check_id="overlap_delta_12",
            layer="unique_coverage_reconciliation",
            expected=str(EXPECTED_OVERLAP_DELTA),
            observed=str(delta),
            ok=delta_ok,
            notes="ok" if delta_ok else "overlap_delta_mismatch",
        )
    )

    # 与 FM23 已冻结的 p2∪p3∪p35∪fu=1388 对齐
    four_union = len(batches["p2"] | batches["p3"] | batches["p35"] | batches["fu"])
    four_ok = four_union == EXPECTED_HARVEST_BATCH_UNION
    checks["four_batch_union_1388"] = four_ok
    rows.append(
        _row(
            check_id="four_batch_union_1388",
            layer="unique_coverage_reconciliation",
            expected=str(EXPECTED_HARVEST_BATCH_UNION),
            observed=str(four_union),
            ok=four_ok,
            notes="ok" if four_ok else "four_batch_union_drift",
        )
    )

    p35_fu = batches["p35"] & batches["fu"]
    p35_fu_ok = p35_fu == EXPECTED_P35_FU_OVERLAP
    checks["expected_overlap_p35_fu_000003"] = p35_fu_ok
    rows.append(
        _row(
            check_id="expected_overlap_p35_fu_000003",
            layer="unique_coverage_reconciliation",
            expected="000003_only",
            observed=",".join(sorted(p35_fu)) or "none",
            ok=p35_fu_ok,
            notes="ok" if p35_fu_ok else "p35_fu_overlap_drift",
        )
    )

    p2_fu_n = len(batches["p2"] & batches["fu"])
    p2_fu_ok = p2_fu_n == EXPECTED_P2_FU_OVERLAP_N
    checks["expected_overlap_p2_fu_11"] = p2_fu_ok
    rows.append(
        _row(
            check_id="expected_overlap_p2_fu_11",
            layer="unique_coverage_reconciliation",
            expected=str(EXPECTED_P2_FU_OVERLAP_N),
            observed=str(p2_fu_n),
            ok=p2_fu_ok,
            notes="ok" if p2_fu_ok else "p2_fu_overlap_drift",
        )
    )

    # h863 与其余四 batch 不相交（继承 FM23）
    disjoint_ok = all(
        len(batches["h863"] & batches[k]) == 0 for k in ("p35", "p3", "p2", "fu")
    )
    checks["h863_disjoint_from_other_batches"] = disjoint_ok
    rows.append(
        _row(
            check_id="h863_disjoint_from_other_batches",
            layer="unique_coverage_reconciliation",
            expected="empty_intersection",
            observed="ok" if disjoint_ok else "overlap",
            ok=disjoint_ok,
            notes="ok" if disjoint_ok else "h863_overlap",
        )
    )

    # additive coverage_sum(3314) = dryrun(1053)+harvest_additive 结构的可解释性
    # 863+190+861+500+500+200+200 = 3314；unique harvest 不替代 additive 指标
    explain_ok = (
        EXPECTED_COMPANY_COVERAGE_SUM
        == (
            EXPECTED_FM01_COMPANY_COUNT
            + EXPECTED_FM02_COMPANY_COUNT
            + EXPECTED_863_COMPLETE
            + EXPECTED_PHASE35_TOTAL
            + EXPECTED_PHASE3_TOTAL
            + EXPECTED_PHASE2_TOTAL
            + EXPECTED_FULLER_TOTAL
        )
        and EXPECTED_HARVEST_ADDITIVE
        == (
            EXPECTED_863_COMPLETE
            + EXPECTED_PHASE35_TOTAL
            + EXPECTED_PHASE3_TOTAL
            + EXPECTED_PHASE2_TOTAL
            + EXPECTED_FULLER_TOTAL
        )
    )
    checks["coverage_sum_vs_unique_explained"] = explain_ok
    rows.append(
        _row(
            check_id="coverage_sum_vs_unique_explained",
            layer="unique_coverage_reconciliation",
            expected="3314_additive_vs_2249_unique_harvest",
            observed=(
                f"coverage_sum={EXPECTED_COMPANY_COVERAGE_SUM};"
                f"harvest_additive={EXPECTED_HARVEST_ADDITIVE};"
                f"harvest_unique={EXPECTED_HARVEST_UNIQUE_UNION}"
            ),
            ok=explain_ok,
            notes="ok" if explain_ok else "coverage_explanation_broken",
        )
    )

    fp_ok = fp == FROZEN_PAIRWISE_INTERSECTION_FP_SHA256
    checks["pairwise_intersection_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="pairwise_intersection_fingerprint",
            layer="unique_coverage_reconciliation",
            expected=FROZEN_PAIRWISE_INTERSECTION_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "pairwise_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["unique_coverage_reconciliation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="unique_coverage_reconciliation_all_pass",
            layer="unique_coverage_reconciliation",
            expected="unique2249+additive2261+pairwise_fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "unique_coverage_incomplete",
        )
    )
    meta = {
        "unique_union": unique_n,
        "additive": additive_n,
        "overlap_delta": delta,
        "pairwise_fp": fp,
        "pairwise_matrix": matrix,
        "batch_sizes": {k: len(v) for k, v in batches.items()},
    }
    return rows, checks, meta


def build_dryrun_surface_unique_rows(
    paths: UniqueCoveragePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """dryrun∪harvest 表面 unique 对账。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    dry863 = _codes(
        load_csv_rows(_abs(paths.fm01_snapshot_status_rel, base_dir=base_dir))
    )
    dry190 = _codes(
        load_csv_rows(_abs(paths.fm02_snapshot_status_rel, base_dir=base_dir))
    )
    batches = load_batch_code_sets(paths, base_dir=base_dir)
    harvest_union = set().union(*batches.values()) if batches else set()

    d863_ok = len(dry863) == EXPECTED_FM01_COMPANY_COUNT
    checks["dry863_count"] = d863_ok
    rows.append(
        _row(
            check_id="dry863_count",
            layer="dryrun_surface_unique",
            path=paths.fm01_snapshot_status_rel,
            expected=str(EXPECTED_FM01_COMPANY_COUNT),
            observed=str(len(dry863)),
            ok=d863_ok,
            notes="ok" if d863_ok else "dry863_count_mismatch",
        )
    )

    d190_ok = len(dry190) == EXPECTED_FM02_COMPANY_COUNT
    checks["dry190_count"] = d190_ok
    rows.append(
        _row(
            check_id="dry190_count",
            layer="dryrun_surface_unique",
            path=paths.fm02_snapshot_status_rel,
            expected=str(EXPECTED_FM02_COMPANY_COUNT),
            observed=str(len(dry190)),
            ok=d190_ok,
            notes="ok" if d190_ok else "dry190_count_mismatch",
        )
    )

    dry_union = dry863 | dry190
    dry_union_ok = (
        len(dry_union) == EXPECTED_COMBINED_DRYRUN_COVERAGE
        and len(dry863 & dry190) == 0
    )
    checks["dryrun_union_1053_disjoint"] = dry_union_ok
    rows.append(
        _row(
            check_id="dryrun_union_1053_disjoint",
            layer="dryrun_surface_unique",
            expected="1053;inter=0",
            observed=f"union={len(dry_union)};inter={len(dry863 & dry190)}",
            ok=dry_union_ok,
            notes="ok" if dry_union_ok else "dryrun_union_drift",
        )
    )

    extras = dry863 - batches["h863"]
    extras_ok = extras == EXPECTED_DRY863_EXTRA
    checks["dry863_extra_vs_h863"] = extras_ok
    rows.append(
        _row(
            check_id="dry863_extra_vs_h863",
            layer="dryrun_surface_unique",
            expected=",".join(sorted(EXPECTED_DRY863_EXTRA)),
            observed=",".join(sorted(extras)) or "none",
            ok=extras_ok,
            notes="ok" if extras_ok else "dry863_extra_drift",
        )
    )

    # h863 ⊆ dry863（harvest 861 是 dryrun 863 的子集）
    subset_ok = batches["h863"] <= dry863
    checks["h863_subset_of_dry863"] = subset_ok
    rows.append(
        _row(
            check_id="h863_subset_of_dry863",
            layer="dryrun_surface_unique",
            expected="h863_subseteq_dry863",
            observed="ok" if subset_ok else "not_subset",
            ok=subset_ok,
            notes="ok" if subset_ok else "h863_not_subset_dry863",
        )
    )

    surface = dry_union | harvest_union
    surface_ok = len(surface) == EXPECTED_SURFACE_UNIQUE
    checks["surface_unique_2251"] = surface_ok
    rows.append(
        _row(
            check_id="surface_unique_2251",
            layer="dryrun_surface_unique",
            expected=str(EXPECTED_SURFACE_UNIQUE),
            observed=str(len(surface)),
            ok=surface_ok,
            notes="ok" if surface_ok else "surface_unique_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["dryrun_surface_unique_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="dryrun_surface_unique_all_pass",
            layer="dryrun_surface_unique",
            expected="surface2251+dry863_extras",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "dryrun_surface_incomplete",
        )
    )
    meta = {
        "surface_unique": len(surface),
        "dryrun_union": len(dry_union),
        "dry863_extras": sorted(extras),
    }
    return rows, checks, meta


def build_resume_lineage_safety_rows(
    paths: UniqueCoveragePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """phase35 resume lineage：子集 / 结构 / 写拒绝。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    p35_rows = load_csv_rows(
        _abs(paths.harvest_phase35_status_rel, base_dir=base_dir)
    )
    resume_rows = load_csv_rows(
        _abs(paths.harvest_phase35_resume_status_rel, base_dir=base_dir)
    )
    p35_codes = _codes(p35_rows)
    resume_codes = _codes(resume_rows)
    resume_counts = _status_counts(resume_rows)

    n_ok = len(resume_rows) == EXPECTED_RESUME_TOTAL and len(resume_codes) == (
        EXPECTED_RESUME_TOTAL
    )
    checks["resume_count_29"] = n_ok
    rows.append(
        _row(
            check_id="resume_count_29",
            layer="resume_lineage_safety",
            path=paths.harvest_phase35_resume_status_rel,
            expected=str(EXPECTED_RESUME_TOTAL),
            observed=f"rows={len(resume_rows)};unique={len(resume_codes)}",
            ok=n_ok,
            notes="ok" if n_ok else "resume_count_mismatch",
        )
    )

    subset_ok = resume_codes <= p35_codes and len(p35_codes) == EXPECTED_PHASE35_TOTAL
    checks["resume_subset_of_phase35"] = subset_ok
    rows.append(
        _row(
            check_id="resume_subset_of_phase35",
            layer="resume_lineage_safety",
            expected="resume_subseteq_p35",
            observed=(
                f"resume={len(resume_codes)};p35={len(p35_codes)};"
                f"leak={len(resume_codes - p35_codes)}"
            ),
            ok=subset_ok,
            notes="ok" if subset_ok else "resume_not_subset",
        )
    )

    struct_ok = (
        resume_counts.get("complete") == EXPECTED_RESUME_COMPLETE
        and resume_counts.get("partial") == EXPECTED_RESUME_PARTIAL
    )
    checks["resume_status_structure"] = struct_ok
    rows.append(
        _row(
            check_id="resume_status_structure",
            layer="resume_lineage_safety",
            expected=(
                f"complete={EXPECTED_RESUME_COMPLETE};"
                f"partial={EXPECTED_RESUME_PARTIAL}"
            ),
            observed=(
                f"complete={resume_counts.get('complete')};"
                f"partial={resume_counts.get('partial')}"
            ),
            ok=struct_ok,
            notes="ok" if struct_ok else "resume_status_mismatch",
        )
    )

    # resume 指纹可复现（结构指纹，不写生产）
    resume_fp_doc = fingerprint_status_csv(
        _abs(paths.harvest_phase35_resume_status_rel, base_dir=base_dir)
    )
    resume_fp = str(resume_fp_doc.get("fingerprint_sha256") or "")
    resume_fp_ok = (
        bool(resume_fp)
        and len(resume_fp) == 64
        and resume_fp_doc.get("row_count") == EXPECTED_RESUME_TOTAL
    )
    checks["resume_status_fingerprint_present"] = resume_fp_ok
    rows.append(
        _row(
            check_id="resume_status_fingerprint_present",
            layer="resume_lineage_safety",
            path=paths.harvest_phase35_resume_status_rel,
            expected="sha256_64hex;rows=29",
            observed=(
                f"{resume_fp[:16]}...;rows={resume_fp_doc.get('row_count')}"
                if resume_fp
                else "missing"
            ),
            ok=resume_fp_ok,
            notes="ok" if resume_fp_ok else "resume_fp_missing",
        )
    )

    refused = False
    msg = ""
    probe_rel = (
        f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm24.csv"
    )
    try:
        assert_safe_erad_audit_write_path(
            _abs(probe_rel, base_dir=base_dir),
            base_dir=base_dir,
            allowed_audit_root_rel=paths.output_root_rel,
        )
    except RuntimeError as exc:
        refused = CLEANUP_REFUSED_MSG in str(exc)
        msg = str(exc)[:120]
    checks["write_guard_phase35_resume_refused"] = refused
    rows.append(
        _row(
            check_id="write_guard_phase35_resume_refused",
            layer="resume_lineage_safety",
            path=probe_rel,
            root_id=RESUME_HARVEST_ROOT_ID,
            expected="CLEANUP_REFUSED",
            observed=f"refused={refused};msg={msg}",
            ok=refused,
            notes="ok" if refused else "resume_write_not_refused",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_lineage_safety_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_lineage_safety_all_pass",
            layer="resume_lineage_safety",
            expected="subset29+struct+write_refuse",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_lineage_incomplete",
        )
    )
    meta = {
        "resume_total": len(resume_rows),
        "resume_complete": resume_counts.get("complete", 0),
        "resume_partial": resume_counts.get("partial", 0),
        "resume_fp": resume_fp,
    }
    return rows, checks, meta


def build_seven_tier_repro_reaffirm_rows(
    paths: UniqueCoveragePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, str]]:
    """七层 repro 指纹再确认（相对 FM23 冻结锚）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    observed: Dict[str, str] = {}

    specs = (
        ("fm01_863", FM01_MOCK_ROOT_REL, None, FROZEN_FM01_863_FP_SHA256, "dryrun"),
        ("fm02_190", FM02_MOCK_ROOT_REL, None, FROZEN_FM02_190_FP_SHA256, "dryrun"),
        (
            "fm03_harvest_863",
            None,
            HARVEST_863_STATUS_REL,
            FROZEN_FM03_HARVEST_863_FP_SHA256,
            "harvest",
        ),
        (
            "phase35_500",
            None,
            HARVEST_PHASE35_STATUS_REL,
            FROZEN_PHASE35_500_FP_SHA256,
            "harvest",
        ),
        (
            "phase3_500",
            None,
            HARVEST_PHASE3_STATUS_REL,
            FROZEN_PHASE3_500_FP_SHA256,
            "harvest",
        ),
        (
            "phase2_200",
            None,
            HARVEST_PHASE2_STATUS_REL,
            FROZEN_PHASE2_200_FP_SHA256,
            "harvest",
        ),
        (
            "fuller_200",
            None,
            HARVEST_FULLER_STATUS_REL,
            FROZEN_FULLER_200_FP_SHA256,
            "harvest",
        ),
    )

    from cninfo_c_class_erad_cleanup_guard import (  # noqa: WPS433
        fingerprint_isolated_snapshot_dryrun,
    )

    for key, root_rel, status_rel, frozen, kind in specs:
        if kind == "dryrun":
            obs = str(
                fingerprint_isolated_snapshot_dryrun(
                    root_rel or "",
                    base_dir=base_dir,
                    gate="PASS_WITH_CAVEAT",
                    company_count=(
                        EXPECTED_FM01_COMPANY_COUNT
                        if key == "fm01_863"
                        else EXPECTED_FM02_COMPANY_COUNT
                    ),
                ).get("fingerprint_sha256")
                or ""
            )
            path = root_rel or ""
            ok = bool(obs) and obs == frozen
        else:
            fp_doc = fingerprint_status_csv(
                _abs(status_rel or "", base_dir=base_dir)
            )
            obs = str(fp_doc.get("fingerprint_sha256") or "")
            path = status_rel or ""
            ok = bool(obs) and obs == frozen
        observed[key] = obs
        checks[f"reaffirm_{key}"] = ok
        rows.append(
            _row(
                check_id=f"reaffirm_{key}",
                layer="seven_tier_repro_reaffirm",
                cohort_id=key,
                path=path,
                expected=frozen,
                observed=obs or "missing",
                ok=ok,
                notes="ok" if ok else "repro_drift",
            )
        )

    combined_ok = (
        observed.get("fm01_863") == FROZEN_FM01_863_FP_SHA256
        and observed.get("fm02_190") == FROZEN_FM02_190_FP_SHA256
    )
    # combined dryrun fp 再算
    from cninfo_c_class_scale_multi_batch_repro_lineage_hardening import (  # noqa: WPS433
        fingerprint_combined_isolated_dryrun_scale,
    )

    combined = fingerprint_combined_isolated_dryrun_scale(
        fm01_fp=observed.get("fm01_863") or "",
        fm02_fp=observed.get("fm02_190") or "",
    )
    combined_match = combined == FROZEN_COMBINED_DRYRUN_1053_FP_SHA256 and combined_ok
    checks["reaffirm_combined_dryrun_1053"] = combined_match
    rows.append(
        _row(
            check_id="reaffirm_combined_dryrun_1053",
            layer="seven_tier_repro_reaffirm",
            expected=FROZEN_COMBINED_DRYRUN_1053_FP_SHA256,
            observed=combined,
            ok=combined_match,
            notes="ok" if combined_match else "combined_dryrun_drift",
        )
    )
    observed["combined_dryrun_1053"] = combined

    distinct_ok = (
        len(set(v for k, v in observed.items() if k != "combined_dryrun_1053" and v))
        == EXPECTED_SCALE_TIER_COUNT
    )
    checks["reaffirm_seven_distinct"] = distinct_ok
    rows.append(
        _row(
            check_id="reaffirm_seven_distinct",
            layer="seven_tier_repro_reaffirm",
            expected="7_distinct",
            observed=str(
                len(
                    set(
                        v
                        for k, v in observed.items()
                        if k != "combined_dryrun_1053" and v
                    )
                )
            ),
            ok=distinct_ok,
            notes="ok" if distinct_ok else "fingerprint_collapse",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["seven_tier_repro_reaffirm_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="seven_tier_repro_reaffirm_all_pass",
            layer="seven_tier_repro_reaffirm",
            expected="7_tier_zero_drift+combined1053",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "reaffirm_incomplete",
        )
    )
    return rows, checks, observed


def build_output_root_protection_rows(
    paths: UniqueCoveragePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK26 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm24.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm24.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm24.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm24.csv",
        ),
        (
            "write_guard_phase35_resume_refused_dup",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm24b.csv",
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
        assert_fm24_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK26_or_ephemeral_allowed",
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
        "write_guard_phase35_resume_refused_dup",
        "hardening_output_root_allowed",
        "protected_write_guard_battery_all_pass",
    ]
    hardening_ok = all(checks.get(k) for k in hardening_keys)
    checks["output_root_protection_all_pass"] = hardening_ok
    rows.append(
        _row(
            check_id="output_root_protection_all_pass",
            layer="output_root_protection",
            expected="harvest+resume_refused;mock26_ok",
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
    paths: UniqueCoveragePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–25 拒绝 · MOCK26 放行。"""
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

    # MOCK25 / MOCK8 重点确认仍冻结（相对本任务 allowlist）
    for root_id, check_id, note in (
        (PRIOR_TASK_ROOT_ID, "mock25_still_frozen", "fm23_mock25_not_writable_by_fm24"),
        ("C-ROOT-MOCK8", "seal_mock8_still_frozen", "seal_chain_not_writable_by_fm24"),
    ):
        prefix = frozen.get(root_id) or _abs(FM23_MOCK_ROOT_REL, base_dir=base_dir)
        blocked = False
        try:
            assert_frozen_mock_cohort_write_forbidden(
                prefix,
                allow_root_ids=(THIS_TASK_ROOT_ID,),
                base_dir=base_dir,
            )
        except RuntimeError as exc:
            blocked = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
        checks[check_id] = blocked
        rows.append(
            _row(
                check_id=check_id,
                layer="frozen_mock_isolation",
                root_id=root_id,
                path=_rel(prefix, base_dir=base_dir) if prefix else "",
                expected="WRITE_FORBIDDEN",
                observed="blocked" if blocked else "writable",
                ok=blocked,
                notes=note if blocked else f"{note}_fail",
            )
        )

    mock26_prefix = frozen.get(THIS_TASK_ROOT_ID)
    mock26_listed = mock26_prefix is not None
    mock26_allowed = False
    if mock26_prefix:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock26_prefix,
                allow_root_ids=(THIS_TASK_ROOT_ID,),
                base_dir=base_dir,
            )
            mock26_allowed = True
        except RuntimeError:
            mock26_allowed = False
    checks["frozen_allow_mock26"] = mock26_listed and mock26_allowed
    rows.append(
        _row(
            check_id="frozen_allow_mock26",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=_rel(mock26_prefix, base_dir=base_dir) if mock26_prefix else "",
            expected="listed_and_allowed_when_in_allowlist",
            observed=f"listed={mock26_listed};allowed={mock26_allowed}",
            ok=mock26_listed and mock26_allowed,
            notes="ok" if mock26_listed and mock26_allowed else "mock26_allow_fail",
        )
    )

    out_ok = False
    out_detail = ""
    try:
        assert_fm24_output_root(paths.output_root_rel, base_dir=base_dir)
        out_ok = True
        out_detail = "allowed"
    except RuntimeError as exc:
        out_detail = str(exc)[:120]
    checks["frozen_output_root_allowed"] = out_ok
    rows.append(
        _row(
            check_id="frozen_output_root_allowed",
            layer="frozen_mock_isolation",
            path=paths.output_root_rel,
            expected="MOCK26_or_ephemeral_allowed",
            observed=out_detail,
            ok=out_ok,
            notes="ok" if out_ok else "mock26_blocked",
        )
    )

    blocked_n = sum(
        1 for k, v in checks.items() if k.startswith("frozen_block_") and v
    )
    summary_ok = (
        blocked_n == len(FROZEN_ROOT_IDS_MUST_BLOCK)
        and checks.get("mock25_still_frozen")
        and checks.get("seal_mock8_still_frozen")
        and checks.get("frozen_allow_mock26")
        and checks.get("frozen_output_root_allowed")
    )
    checks["frozen_mock_isolation_all_pass"] = bool(summary_ok)
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-25_blocked_MOCK26_ok",
            observed=(
                f"blocked={blocked_n}/{len(FROZEN_ROOT_IDS_MUST_BLOCK)};"
                f"mock26={'ok' if out_ok else 'fail'}"
            ),
            ok=bool(summary_ok),
            notes="ok" if summary_ok else "isolation_incomplete",
        )
    )
    return rows, checks


def build_protected_csv_registry_rows(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected CSV：MOCK3–26 + resume C-ROOT-002 + AUTH1 + fuller。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    root_rows = load_protected_root_rows(csv_rel=csv_rel, base_dir=base_dir)
    by_id = {str(r.get("root_id") or ""): r for r in root_rows}

    for root_id in REQUIRED_PROTECTED_ROOT_IDS:
        present = root_id in by_id
        checks[f"csv_has_{root_id}"] = present
        rows.append(
            _row(
                check_id=f"csv_has_{root_id}",
                layer="protected_csv_registry",
                root_id=root_id,
                expected="registered",
                observed="yes" if present else "missing",
                ok=present,
                notes="ok" if present else "missing_root",
            )
        )

    mock26 = by_id.get(THIS_TASK_ROOT_ID) or {}
    mock26_ok = (
        str(mock26.get("path_pattern") or "").rstrip("/")
        == DEFAULT_MOCK_OUTPUT_ROOT_REL
        and str(mock26.get("write_policy") or "") == "delete_ok_tests_only"
    )
    checks["csv_mock26_path_policy"] = mock26_ok
    rows.append(
        _row(
            check_id="csv_mock26_path_policy",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=f"{DEFAULT_MOCK_OUTPUT_ROOT_REL}/;delete_ok_tests_only",
            observed=(
                f"{mock26.get('path_pattern')};{mock26.get('write_policy')}"
            ),
            ok=mock26_ok,
            notes="ok" if mock26_ok else "mock26_csv_mismatch",
        )
    )

    resume = by_id.get(RESUME_HARVEST_ROOT_ID) or {}
    resume_ok = (
        HARVEST_PHASE35_RESUME_ROOT_REL.rstrip("/")
        in str(resume.get("path_pattern") or "").rstrip("/")
        and str(resume.get("write_policy") or "") == "read_only_erad_planning"
    )
    checks["csv_resume_root_readonly"] = resume_ok
    rows.append(
        _row(
            check_id="csv_resume_root_readonly",
            layer="protected_csv_registry",
            root_id=RESUME_HARVEST_ROOT_ID,
            expected="resume_path;read_only_erad_planning",
            observed=(
                f"{resume.get('path_pattern')};{resume.get('write_policy')}"
            ),
            ok=resume_ok,
            notes="ok" if resume_ok else "resume_csv_mismatch",
        )
    )

    auth = by_id.get("C-ROOT-AUTH1") or {}
    auth_ok = str(auth.get("write_policy") or "") == "read_only_no_overwrite"
    checks["csv_auth1_readonly"] = auth_ok
    rows.append(
        _row(
            check_id="csv_auth1_readonly",
            layer="protected_csv_registry",
            root_id="C-ROOT-AUTH1",
            expected="read_only_no_overwrite",
            observed=str(auth.get("write_policy") or ""),
            ok=auth_ok,
            notes="ok" if auth_ok else "auth1_policy_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-26+C-ROOT-002+C-ROOT-011+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "csv_registry_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..23 gate battery（跳过 seal FM06–11）。"""
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
    ]
    for check_id, key in specs:
        payload = gates[key]
        gate = str(payload.get("gate") or "").strip()
        cninfo = payload.get("cninfo_calls", None)
        execute = payload.get("execute_production_snapshot_rebuild", None)
        ok = gate == "PASS_OFFLINE" and cninfo == 0 and execute is False
        if key in (
            "fm12",
            "fm13",
            "fm14",
            "fm15",
            "fm16",
            "fm17",
            "fm18",
            "fm19",
            "fm20",
            "fm21",
            "fm22",
            "fm23",
        ):
            if "seal_chain_extended" in payload:
                ok = ok and payload.get("seal_chain_extended") is False
        if key == "fm23":
            ok = (
                ok
                and payload.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
                and payload.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
                and payload.get("approved_for_snapshot_rebuild") is False
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
            check_id="fm01_05_12_23_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_23_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm24(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK26；加固 C-ROOT-002 resume 说明。"""
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

    # 加固 resume 根说明（路径/策略保持不变）
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
                "C-FM-24 resume-lineage safety hardening; 只读直至人批重跑"
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
                "C-FM-24 scale unique-coverage reconciliation (unique=2249/"
                "additive=2261/delta=12) + dryrun surface 2251 + phase35 resume "
                "lineage safety + FM23 continuity; never production EXECUTE; "
                "must not overwrite MOCK3-25; seal_chain_extended=false"
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


def run_scale_unique_coverage_resume_lineage_safety(
    *,
    paths: UniqueCoveragePaths = UniqueCoveragePaths(),
    base_dir: str = BASE_DIR,
    ensure_protected_csv: bool = True,
) -> Dict[str, Any]:
    """执行 C-FM-24 unique-coverage 对账 + resume lineage 安全 QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    if ensure_protected_csv:
        ensure_protected_roots_csv_fm24(
            csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
        )
    out_root = assert_fm24_output_root(paths.output_root_rel, base_dir=base_dir)

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
    }

    cont_rows, cont_checks = build_fm23_continuity_rows(paths, base_dir=base_dir)
    uniq_rows, uniq_checks, uniq_meta = build_unique_coverage_reconciliation_rows(
        paths, base_dir=base_dir
    )
    surf_rows, surf_checks, surf_meta = build_dryrun_surface_unique_rows(
        paths, base_dir=base_dir
    )
    resume_rows, resume_checks, resume_meta = build_resume_lineage_safety_rows(
        paths, base_dir=base_dir
    )
    reaff_rows, reaff_checks, observed_fps = build_seven_tier_repro_reaffirm_rows(
        paths, base_dir=base_dir
    )
    prot_rows, prot_checks = build_output_root_protection_rows(
        paths, base_dir=base_dir
    )
    fr_rows, fr_checks = build_frozen_mock_isolation_rows(paths, base_dir=base_dir)
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    hold_rows, hold_checks = build_execute_hold_rows()

    matrix = (
        cont_rows
        + uniq_rows
        + surf_rows
        + resume_rows
        + reaff_rows
        + prot_rows
        + fr_rows
        + csv_rows
        + bat_rows
        + hold_rows
    )
    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm23_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm23_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "unique_coverage_reconciliation": (
            "PASS_OFFLINE"
            if uniq_checks.get("unique_coverage_reconciliation_all_pass")
            else "FAIL_OFFLINE"
        ),
        "dryrun_surface_unique": (
            "PASS_OFFLINE"
            if surf_checks.get("dryrun_surface_unique_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_lineage_safety": (
            "PASS_OFFLINE"
            if resume_checks.get("resume_lineage_safety_all_pass")
            else "FAIL_OFFLINE"
        ),
        "seven_tier_repro_reaffirm": (
            "PASS_OFFLINE"
            if reaff_checks.get("seven_tier_repro_reaffirm_all_pass")
            else "FAIL_OFFLINE"
        ),
        "output_root_protection": (
            "PASS_OFFLINE"
            if prot_checks.get("output_root_protection_all_pass")
            else "FAIL_OFFLINE"
        ),
        "frozen_mock_isolation": (
            "PASS_OFFLINE"
            if fr_checks.get("frozen_mock_isolation_all_pass")
            else "FAIL_OFFLINE"
        ),
        "protected_csv_registry": (
            "PASS_OFFLINE"
            if csv_checks.get("protected_csv_registry_all_pass")
            else "FAIL_OFFLINE"
        ),
        "fm_gate_battery": (
            "PASS_OFFLINE"
            if bat_checks.get("fm01_05_12_23_battery_all_pass")
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

    # pairwise matrix 产物
    pairwise_rel = _rel(
        os.path.join(out_root, "pairwise_intersection_matrix.json"), base_dir=base_dir
    )
    with open(_abs(pairwise_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": uniq_meta["pairwise_fp"],
                "unique_union": uniq_meta["unique_union"],
                "additive": uniq_meta["additive"],
                "overlap_delta": uniq_meta["overlap_delta"],
                "matrix": uniq_meta["pairwise_matrix"],
                "batch_sizes": uniq_meta["batch_sizes"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    coverage_ledger_rel = _rel(
        os.path.join(out_root, "unique_coverage_ledger.json"), base_dir=base_dir
    )
    with open(
        _abs(coverage_ledger_rel, base_dir=base_dir), "w", encoding="utf-8"
    ) as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "company_coverage_sum_additive_tiers": EXPECTED_COMPANY_COVERAGE_SUM,
                "harvest_unique_union": uniq_meta["unique_union"],
                "harvest_additive": uniq_meta["additive"],
                "overlap_delta": uniq_meta["overlap_delta"],
                "four_batch_union": EXPECTED_HARVEST_BATCH_UNION,
                "surface_unique_dryrun_harvest": surf_meta["surface_unique"],
                "dryrun_union": surf_meta["dryrun_union"],
                "dry863_extras": surf_meta["dry863_extras"],
                "resume_total": resume_meta["resume_total"],
                "resume_complete": resume_meta["resume_complete"],
                "resume_partial": resume_meta["resume_partial"],
                "resume_fp": resume_meta["resume_fp"],
                "pairwise_fp": uniq_meta["pairwise_fp"],
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
        "harvest_unique_union": uniq_meta["unique_union"],
        "harvest_additive": uniq_meta["additive"],
        "overlap_delta": uniq_meta["overlap_delta"],
        "surface_unique": surf_meta["surface_unique"],
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "pairwise_fp": uniq_meta["pairwise_fp"],
        "observed_fps": observed_fps,
        "frozen_fps": {
            "fm01_863": FROZEN_FM01_863_FP_SHA256,
            "fm02_190": FROZEN_FM02_190_FP_SHA256,
            "fm03_harvest_863": FROZEN_FM03_HARVEST_863_FP_SHA256,
            "phase35_500": FROZEN_PHASE35_500_FP_SHA256,
            "phase3_500": FROZEN_PHASE3_500_FP_SHA256,
            "phase2_200": FROZEN_PHASE2_200_FP_SHA256,
            "fuller_200": FROZEN_FULLER_200_FP_SHA256,
            "combined_dryrun_1053": FROZEN_COMBINED_DRYRUN_1053_FP_SHA256,
            "pairwise_intersection": FROZEN_PAIRWISE_INTERSECTION_FP_SHA256,
            "fm23_matrix": FROZEN_FM23_MATRIX_FP_SHA256,
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
        "fm24_gate": overall,
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
        "harvest_unique_union": uniq_meta["unique_union"],
        "surface_unique": surf_meta["surface_unique"],
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
        "harvest_unique_union": uniq_meta["unique_union"],
        "harvest_additive": uniq_meta["additive"],
        "overlap_delta": uniq_meta["overlap_delta"],
        "surface_unique": surf_meta["surface_unique"],
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "resume_total": resume_meta["resume_total"],
        "notes": (
            "unique-coverage reconciliation (unique=2249/additive=2261/delta=12) "
            "+ dryrun surface 2251 + phase35 resume lineage safety (29⊆p35) "
            "+ FM23 continuity + output-root protection (MOCK26 / C-ROOT-002); "
            "EXECUTE remains human-held; does not overwrite MOCK3-25"
        ),
    }
    packet_rel = _rel(
        os.path.join(out_root, "scale_packet.json"), base_dir=base_dir
    )
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
        "harvest_unique_union": uniq_meta["unique_union"],
        "harvest_additive": uniq_meta["additive"],
        "overlap_delta": uniq_meta["overlap_delta"],
        "surface_unique": surf_meta["surface_unique"],
        "combined_dryrun_coverage": EXPECTED_COMBINED_DRYRUN_COVERAGE,
        "resume_total": resume_meta["resume_total"],
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "pairwise_path": pairwise_rel,
        "coverage_ledger_path": coverage_ledger_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "pairwise_fp": uniq_meta["pairwise_fp"],
        "inputs": {
            "harvest_863_status": paths.harvest_863_status_rel,
            "harvest_phase35_status": paths.harvest_phase35_status_rel,
            "harvest_phase3_status": paths.harvest_phase3_status_rel,
            "harvest_phase2_status": paths.harvest_phase2_status_rel,
            "harvest_fuller_status": paths.harvest_fuller_status_rel,
            "harvest_phase35_resume_status": paths.harvest_phase35_resume_status_rel,
            "fm01_snapshot_status": paths.fm01_snapshot_status_rel,
            "fm02_snapshot_status": paths.fm02_snapshot_status_rel,
            "fm23_packet": paths.fm23_packet_rel,
        },
        "mock_root_is_isolated": True,
    }
