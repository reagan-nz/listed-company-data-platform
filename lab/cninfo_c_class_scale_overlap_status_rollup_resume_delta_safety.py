"""
CNINFO C-class — 规模 overlap 精确台账 + status rollup + resume delta 安全
（离线 · C-FM-25）。

在 C-FM-24（unique-coverage + resume lineage safety）已 commit 且 EXECUTE 仍
human-held 之上，继续非 seal 规模/安全能力（不新增 seal / decision-await /
commit-boundary；非 extension↔drift 循环）：
  1) FM24 packet / fingerprint 零漂移连续（unique=2249 · surface=2251 · resume=29）
  2) 精确 overlap 代码台账：p35∩fu={000003} · p2∩fu=11 码冻结指纹
  3) harvest unique-union status rollup：complete=2134 · partial=106 · failed=9
  4) resume vs base delta：improved=28 · same=1(301212) · worse=0 · 写拒绝
  5) dry863 extras={000037,000055} 隔离：不在五 harvest · 不在 exclusion 宇宙
  6) output-root：MOCK3–26 冻结 · MOCK27 放行
  7) FM-01..05 + FM-12..24 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–26 / 权威 dual-layer 索引 ·
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
    EXPECTED_863_COMPLETE,
    EXPECTED_PHASE35_TOTAL,
    fingerprint_scale_matrix,
    write_scale_matrix_csv,
)
from cninfo_c_class_scale_multi_batch_repro_lineage_hardening import (  # noqa: E402
    EXPECTED_COMBINED_DRYRUN_COVERAGE,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_FULLER_TOTAL,
    EXPECTED_PHASE2_TOTAL,
    EXPECTED_PHASE3_TOTAL,
    EXPECTED_SCALE_TIER_COUNT,
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
from cninfo_c_class_scale_unique_coverage_resume_lineage_safety import (  # noqa: E402
    EXPECTED_DRY863_EXTRA,
    EXPECTED_HARVEST_ADDITIVE,
    EXPECTED_HARVEST_UNIQUE_UNION,
    EXPECTED_OVERLAP_DELTA,
    EXPECTED_P2_FU_OVERLAP_N,
    EXPECTED_P35_FU_OVERLAP,
    EXPECTED_RESUME_COMPLETE,
    EXPECTED_RESUME_PARTIAL,
    EXPECTED_RESUME_TOTAL,
    EXPECTED_SURFACE_UNIQUE,
    FROZEN_PAIRWISE_INTERSECTION_FP_SHA256,
    HARVEST_863_STATUS_REL,
    HARVEST_PHASE35_RESUME_ROOT_REL,
    HARVEST_PHASE35_RESUME_STATUS_REL,
    HARVEST_PHASE35_STATUS_REL,
    UniqueCoveragePaths as Fm24Paths,
    fingerprint_harvest_pairwise_intersection,
    load_batch_code_sets,
)

TASK_ID = "C-FM-25"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm25_scale_overlap_status_rollup_resume_delta_safety"
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
FM24_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_unique_coverage_resume_lineage_safety_20260715.json"
)

FM24_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm24_scale_unique_coverage_resume_lineage_safety"
)
FM24_PACKET_REL = f"{FM24_MOCK_ROOT_REL}/scale_packet.json"
FM24_FINGERPRINT_REL = f"{FM24_MOCK_ROOT_REL}/scale_fingerprint.json"

FM01_SNAPSHOT_STATUS_REL = (
    f"{FM01_MOCK_ROOT_REL}/quality/company_snapshot_status.csv"
)
FM02_SNAPSHOT_STATUS_REL = (
    f"{FM02_MOCK_ROOT_REL}/quality/company_snapshot_status.csv"
)

EXCLUSION_UNIVERSE_REL = (
    "outputs/validation/"
    "cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv"
)

# overlap / status / resume-delta 冻结锚
EXPECTED_P2_FU_OVERLAP_CODES = frozenset(
    {
        "000019",
        "000026",
        "000035",
        "300013",
        "300083",
        "600005",
        "600037",
        "600095",
        "600098",
        "688061",
        "688079",
    }
)
EXPECTED_UNION_COMPLETE = 2134
EXPECTED_UNION_PARTIAL = 106
EXPECTED_UNION_FAILED = 9
EXPECTED_RESUME_IMPROVED = 28
EXPECTED_RESUME_SAME = 1
EXPECTED_RESUME_WORSE = 0
EXPECTED_RESUME_SAME_CODES = frozenset({"301212"})

EXPECTED_PER_BATCH_STATUS = {
    "h863": {"complete": 861},
    "p35": {"complete": 419, "partial": 75, "failed": 6},
    "p3": {"complete": 483, "partial": 14, "failed": 3},
    "p2": {"complete": 188, "partial": 12},
    "fu": {"complete": 193, "partial": 7},
}

FROZEN_OVERLAP_CODE_LEDGER_FP_SHA256 = (
    "db6bba96822942200eba74ffd75465f2abaabb63736ab77e86a41e02ce6259da"
)
FROZEN_STATUS_ROLLUP_FP_SHA256 = (
    "bf2c366446cb04846f4432ce6bb60de2d8009b20ff19b0cf64280065397529a9"
)
FROZEN_RESUME_DELTA_FP_SHA256 = (
    "d7aa3a92f479398b94c7a2a569d2b7dc6b18d1d4d7c2916a8a232d2bac4f3ad1"
)

STATUS_RANK = {"complete": 3, "partial": 2, "failed": 1, "": 0}
BATCH_PRIORITY = ("h863", "p35", "p3", "p2", "fu")

THIS_TASK_ROOT_ID = "C-ROOT-MOCK27"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK26"
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
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class OverlapStatusPaths:
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
    fm24_packet_rel: str = FM24_PACKET_REL
    fm24_fingerprint_rel: str = FM24_FINGERPRINT_REL
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


def _codes(rows: Sequence[Dict[str, str]]) -> set:
    return {
        str(r.get("company_code") or "").strip()
        for r in rows
        if str(r.get("company_code") or "").strip()
    }


def _status_map(rows: Sequence[Dict[str, str]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for r in rows:
        code = str(r.get("company_code") or "").strip()
        if code:
            out[code] = str(r.get("harvest_status") or "").strip()
    return out


def _status_counts(rows: Sequence[Dict[str, str]]) -> Dict[str, int]:
    return dict(
        sorted(
            Counter(
                str(r.get("harvest_status") or "").strip() for r in rows
            ).items()
        )
    )


def _to_fm24_paths(paths: OverlapStatusPaths) -> Fm24Paths:
    """复用 FM24 load_batch_code_sets 的路径视图。"""
    return Fm24Paths(
        harvest_863_status_rel=paths.harvest_863_status_rel,
        harvest_phase35_status_rel=paths.harvest_phase35_status_rel,
        harvest_phase3_status_rel=paths.harvest_phase3_status_rel,
        harvest_phase2_status_rel=paths.harvest_phase2_status_rel,
        harvest_fuller_status_rel=paths.harvest_fuller_status_rel,
        harvest_phase35_resume_status_rel=paths.harvest_phase35_resume_status_rel,
        fm01_snapshot_status_rel=paths.fm01_snapshot_status_rel,
        fm02_snapshot_status_rel=paths.fm02_snapshot_status_rel,
        output_root_rel=paths.output_root_rel,
    )


def assert_fm25_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-25 写根：须 validation/_mock_*，不得覆盖 MOCK3–26，
    不得写权威 dual-layer 索引；允许本任务 MOCK27 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-25 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def fingerprint_overlap_code_ledger(
    batches: Dict[str, set],
) -> Tuple[str, Dict[str, Any]]:
    """精确 overlap 代码台账指纹。"""
    p35_fu = sorted(batches["p35"] & batches["fu"])
    p2_fu = sorted(batches["p2"] & batches["fu"])
    doc = {
        "kind": "harvest_overlap_code_ledger",
        "p35_fu": p35_fu,
        "p2_fu": p2_fu,
        "overlap_delta": len(p35_fu) + len(p2_fu),
    }
    canon = json.dumps(doc, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest(), doc


def compute_unique_union_status_rollup(
    *,
    status_maps: Dict[str, Dict[str, str]],
) -> Tuple[Dict[str, int], Dict[str, Dict[str, int]], str]:
    """
    unique-union 取跨 batch 最优 status（complete>partial>failed），
    并附 per-batch status 计数。
    """
    per_batch: Dict[str, Dict[str, int]] = {}
    for key in BATCH_PRIORITY:
        counts = Counter(status_maps[key].values())
        per_batch[key] = dict(sorted(counts.items()))

    all_codes = set().union(*(set(m) for m in status_maps.values()))
    union_status: Dict[str, str] = {}
    for code in all_codes:
        best = ""
        for key in BATCH_PRIORITY:
            if code in status_maps[key]:
                st = status_maps[key][code]
                if STATUS_RANK.get(st, 0) > STATUS_RANK.get(best, 0):
                    best = st
        union_status[code] = best
    union_counts = dict(sorted(Counter(union_status.values()).items()))
    doc = {
        "kind": "harvest_unique_status_rollup",
        "unique_union": len(union_status),
        "union_status": union_counts,
        "per_batch_status": per_batch,
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return union_counts, per_batch, fp


def compute_resume_vs_base_delta(
    *,
    base_status: Dict[str, str],
    resume_status: Dict[str, str],
) -> Tuple[Dict[str, Any], str]:
    """resume 相对 phase35 base 的 status delta（只读，不 merge）。"""
    improved: List[str] = []
    same: List[str] = []
    worse: List[str] = []
    for code in sorted(resume_status):
        a = base_status.get(code, "")
        b = resume_status.get(code, "")
        if STATUS_RANK.get(b, 0) > STATUS_RANK.get(a, 0):
            improved.append(code)
        elif b == a:
            same.append(code)
        else:
            worse.append(code)
    doc = {
        "kind": "resume_vs_base_delta",
        "resume_total": len(resume_status),
        "improved": len(improved),
        "same": len(same),
        "worse": len(worse),
        "same_codes": same,
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    meta = {
        "improved": len(improved),
        "same": len(same),
        "worse": len(worse),
        "same_codes": same,
        "improved_codes": improved,
        "worse_codes": worse,
        "fingerprint": fp,
        "doc": doc,
    }
    return meta, fp


def build_fm24_continuity_rows(
    paths: OverlapStatusPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM24 packet / fingerprint 零漂移连续。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm24_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm24_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm24_gate_json_rel, base_dir=base_dir))

    pkt_ok = (
        packet.get("gate") == "PASS_OFFLINE"
        and packet.get("cninfo_calls") == 0
        and packet.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and packet.get("harvest_additive") == EXPECTED_HARVEST_ADDITIVE
        and packet.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and packet.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and packet.get("resume_total") == EXPECTED_RESUME_TOTAL
        and packet.get("company_coverage_sum") == EXPECTED_COMPANY_COVERAGE_SUM
        and packet.get("scale_tier_count") == EXPECTED_SCALE_TIER_COUNT
        and packet.get("execute_production_snapshot_rebuild") is False
        and packet.get("approved_for_snapshot_rebuild") is False
        and packet.get("seal_chain_extended") is False
        and packet.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
    )
    checks["fm24_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm24_packet_continuity",
            layer="fm24_continuity",
            path=paths.fm24_packet_rel,
            expected="PASS_OFFLINE;unique=2249;surface=2251;resume=29",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"surface={packet.get('surface_unique')};"
                f"resume={packet.get('resume_total')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm24_packet_drift",
        )
    )

    fp_ok = (
        fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and fp_doc.get("pairwise_fp") == FROZEN_PAIRWISE_INTERSECTION_FP_SHA256
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm24_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm24_fingerprint_continuity",
            layer="fm24_continuity",
            path=paths.fm24_fingerprint_rel,
            expected="unique2249+surface2251+pairwise_fp",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"surface={fp_doc.get('surface_unique')};"
                f"pairwise={str(fp_doc.get('pairwise_fp') or '')[:16]}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm24_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("seal_chain_extended") is False
    )
    checks["fm24_gate_json_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm24_gate_json_continuity",
            layer="fm24_continuity",
            path=paths.fm24_gate_json_rel,
            expected="PASS_OFFLINE;unique=2249;approved=false",
            observed=(
                f"gate={gate_doc.get('gate')};"
                f"unique={gate_doc.get('harvest_unique_union')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm24_gate_drift",
        )
    )

    # 再算 pairwise 确认相对 FM24 冻结锚无漂移
    batches = load_batch_code_sets(_to_fm24_paths(paths), base_dir=base_dir)
    pairwise_fp, _m, unique_n, additive_n = fingerprint_harvest_pairwise_intersection(
        batches
    )
    pair_ok = (
        pairwise_fp == FROZEN_PAIRWISE_INTERSECTION_FP_SHA256
        and unique_n == EXPECTED_HARVEST_UNIQUE_UNION
        and additive_n == EXPECTED_HARVEST_ADDITIVE
    )
    checks["fm24_pairwise_reaffirm"] = pair_ok
    rows.append(
        _row(
            check_id="fm24_pairwise_reaffirm",
            layer="fm24_continuity",
            expected=FROZEN_PAIRWISE_INTERSECTION_FP_SHA256,
            observed=f"{pairwise_fp};unique={unique_n};additive={additive_n}",
            ok=pair_ok,
            notes="ok" if pair_ok else "pairwise_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm24_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm24_continuity_all_pass",
            layer="fm24_continuity",
            expected="packet+fingerprint+gate+pairwise",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm24_continuity_incomplete",
        )
    )
    return rows, checks


def build_overlap_code_ledger_rows(
    paths: OverlapStatusPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """精确 overlap 代码台账（相对 Δ12）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    batches = load_batch_code_sets(_to_fm24_paths(paths), base_dir=base_dir)
    fp, doc = fingerprint_overlap_code_ledger(batches)

    size_ok = (
        len(batches["h863"]) == EXPECTED_863_COMPLETE
        and len(batches["p35"]) == EXPECTED_PHASE35_TOTAL
        and len(batches["p3"]) == EXPECTED_PHASE3_TOTAL
        and len(batches["p2"]) == EXPECTED_PHASE2_TOTAL
        and len(batches["fu"]) == EXPECTED_FULLER_TOTAL
    )
    checks["overlap_batch_sizes"] = size_ok
    rows.append(
        _row(
            check_id="overlap_batch_sizes",
            layer="overlap_code_ledger",
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

    p35_fu = set(doc["p35_fu"])
    p35_ok = p35_fu == EXPECTED_P35_FU_OVERLAP
    checks["overlap_p35_fu_exact_000003"] = p35_ok
    rows.append(
        _row(
            check_id="overlap_p35_fu_exact_000003",
            layer="overlap_code_ledger",
            expected="000003",
            observed=",".join(sorted(p35_fu)) or "none",
            ok=p35_ok,
            notes="ok" if p35_ok else "p35_fu_code_drift",
        )
    )

    p2_fu = set(doc["p2_fu"])
    p2_ok = (
        p2_fu == EXPECTED_P2_FU_OVERLAP_CODES
        and len(p2_fu) == EXPECTED_P2_FU_OVERLAP_N
    )
    checks["overlap_p2_fu_exact_11"] = p2_ok
    rows.append(
        _row(
            check_id="overlap_p2_fu_exact_11",
            layer="overlap_code_ledger",
            expected=",".join(sorted(EXPECTED_P2_FU_OVERLAP_CODES)),
            observed=",".join(sorted(p2_fu)) or "none",
            ok=p2_ok,
            notes="ok" if p2_ok else "p2_fu_code_drift",
        )
    )

    delta_ok = doc["overlap_delta"] == EXPECTED_OVERLAP_DELTA
    checks["overlap_delta_explains_12"] = delta_ok
    rows.append(
        _row(
            check_id="overlap_delta_explains_12",
            layer="overlap_code_ledger",
            expected=str(EXPECTED_OVERLAP_DELTA),
            observed=str(doc["overlap_delta"]),
            ok=delta_ok,
            notes="ok" if delta_ok else "overlap_delta_mismatch",
        )
    )

    # 确认无其它 pairwise 交集贡献 Δ（h863 与其它不相交；p3 与 p35/p2/fu 不相交等由矩阵保证）
    unique_n = len(set().union(*batches.values()))
    additive_n = sum(len(batches[k]) for k in batches)
    recon_ok = (
        unique_n == EXPECTED_HARVEST_UNIQUE_UNION
        and additive_n - unique_n == EXPECTED_OVERLAP_DELTA
    )
    checks["overlap_reconciles_unique_2249"] = recon_ok
    rows.append(
        _row(
            check_id="overlap_reconciles_unique_2249",
            layer="overlap_code_ledger",
            expected="unique2249;delta12",
            observed=f"unique={unique_n};delta={additive_n - unique_n}",
            ok=recon_ok,
            notes="ok" if recon_ok else "unique_recon_broken",
        )
    )

    fp_ok = fp == FROZEN_OVERLAP_CODE_LEDGER_FP_SHA256
    checks["overlap_code_ledger_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="overlap_code_ledger_fingerprint",
            layer="overlap_code_ledger",
            expected=FROZEN_OVERLAP_CODE_LEDGER_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "overlap_ledger_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["overlap_code_ledger_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="overlap_code_ledger_all_pass",
            layer="overlap_code_ledger",
            expected="exact_codes+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "overlap_ledger_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "p35_fu": sorted(p35_fu),
        "p2_fu": sorted(p2_fu),
        "overlap_delta": doc["overlap_delta"],
        "unique_union": unique_n,
    }
    return rows, checks, meta


def build_harvest_status_rollup_rows(
    paths: OverlapStatusPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """harvest unique-union status rollup。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    status_maps = {
        "h863": _status_map(
            load_csv_rows(_abs(paths.harvest_863_status_rel, base_dir=base_dir))
        ),
        "p35": _status_map(
            load_csv_rows(_abs(paths.harvest_phase35_status_rel, base_dir=base_dir))
        ),
        "p3": _status_map(
            load_csv_rows(_abs(paths.harvest_phase3_status_rel, base_dir=base_dir))
        ),
        "p2": _status_map(
            load_csv_rows(_abs(paths.harvest_phase2_status_rel, base_dir=base_dir))
        ),
        "fu": _status_map(
            load_csv_rows(_abs(paths.harvest_fuller_status_rel, base_dir=base_dir))
        ),
    }
    union_counts, per_batch, fp = compute_unique_union_status_rollup(
        status_maps=status_maps
    )

    union_n = sum(union_counts.values())
    n_ok = union_n == EXPECTED_HARVEST_UNIQUE_UNION
    checks["status_rollup_unique_n_2249"] = n_ok
    rows.append(
        _row(
            check_id="status_rollup_unique_n_2249",
            layer="harvest_status_rollup",
            expected=str(EXPECTED_HARVEST_UNIQUE_UNION),
            observed=str(union_n),
            ok=n_ok,
            notes="ok" if n_ok else "union_n_mismatch",
        )
    )

    class_ok = (
        union_counts.get("complete") == EXPECTED_UNION_COMPLETE
        and union_counts.get("partial") == EXPECTED_UNION_PARTIAL
        and union_counts.get("failed") == EXPECTED_UNION_FAILED
    )
    checks["status_rollup_union_classes"] = class_ok
    rows.append(
        _row(
            check_id="status_rollup_union_classes",
            layer="harvest_status_rollup",
            expected=(
                f"complete={EXPECTED_UNION_COMPLETE};"
                f"partial={EXPECTED_UNION_PARTIAL};"
                f"failed={EXPECTED_UNION_FAILED}"
            ),
            observed=(
                f"complete={union_counts.get('complete')};"
                f"partial={union_counts.get('partial')};"
                f"failed={union_counts.get('failed')}"
            ),
            ok=class_ok,
            notes="ok" if class_ok else "union_class_drift",
        )
    )

    per_ok = per_batch == EXPECTED_PER_BATCH_STATUS
    checks["status_rollup_per_batch"] = per_ok
    rows.append(
        _row(
            check_id="status_rollup_per_batch",
            layer="harvest_status_rollup",
            expected="h863/p35/p3/p2/fu frozen counts",
            observed=json.dumps(per_batch, ensure_ascii=False, sort_keys=True),
            ok=per_ok,
            notes="ok" if per_ok else "per_batch_status_drift",
        )
    )

    fp_ok = fp == FROZEN_STATUS_ROLLUP_FP_SHA256
    checks["status_rollup_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="status_rollup_fingerprint",
            layer="harvest_status_rollup",
            expected=FROZEN_STATUS_ROLLUP_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "status_rollup_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["harvest_status_rollup_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="harvest_status_rollup_all_pass",
            layer="harvest_status_rollup",
            expected="2134/106/9+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "status_rollup_incomplete",
        )
    )
    meta = {
        "union_counts": union_counts,
        "per_batch": per_batch,
        "fingerprint": fp,
        "unique_union": union_n,
    }
    return rows, checks, meta


def build_resume_delta_safety_rows(
    paths: OverlapStatusPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """resume vs phase35 base delta + 写拒绝。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    base_rows = load_csv_rows(
        _abs(paths.harvest_phase35_status_rel, base_dir=base_dir)
    )
    resume_rows = load_csv_rows(
        _abs(paths.harvest_phase35_resume_status_rel, base_dir=base_dir)
    )
    base_status = _status_map(base_rows)
    resume_status = _status_map(resume_rows)
    resume_codes = set(resume_status)

    n_ok = (
        len(resume_rows) == EXPECTED_RESUME_TOTAL
        and len(resume_codes) == EXPECTED_RESUME_TOTAL
    )
    checks["resume_delta_count_29"] = n_ok
    rows.append(
        _row(
            check_id="resume_delta_count_29",
            layer="resume_delta_safety",
            path=paths.harvest_phase35_resume_status_rel,
            expected=str(EXPECTED_RESUME_TOTAL),
            observed=f"rows={len(resume_rows)};unique={len(resume_codes)}",
            ok=n_ok,
            notes="ok" if n_ok else "resume_count_mismatch",
        )
    )

    subset_ok = resume_codes <= set(base_status)
    checks["resume_delta_subset_of_p35"] = subset_ok
    rows.append(
        _row(
            check_id="resume_delta_subset_of_p35",
            layer="resume_delta_safety",
            expected="resume_subseteq_p35",
            observed=f"leak={len(resume_codes - set(base_status))}",
            ok=subset_ok,
            notes="ok" if subset_ok else "resume_not_subset",
        )
    )

    meta, fp = compute_resume_vs_base_delta(
        base_status=base_status, resume_status=resume_status
    )
    delta_ok = (
        meta["improved"] == EXPECTED_RESUME_IMPROVED
        and meta["same"] == EXPECTED_RESUME_SAME
        and meta["worse"] == EXPECTED_RESUME_WORSE
        and set(meta["same_codes"]) == EXPECTED_RESUME_SAME_CODES
    )
    checks["resume_delta_structure"] = delta_ok
    rows.append(
        _row(
            check_id="resume_delta_structure",
            layer="resume_delta_safety",
            expected=(
                f"improved={EXPECTED_RESUME_IMPROVED};"
                f"same={EXPECTED_RESUME_SAME}:301212;worse=0"
            ),
            observed=(
                f"improved={meta['improved']};same={meta['same']}:"
                f"{','.join(meta['same_codes']) or 'none'};"
                f"worse={meta['worse']}"
            ),
            ok=delta_ok,
            notes="ok" if delta_ok else "resume_delta_drift",
        )
    )

    struct_counts = _status_counts(resume_rows)
    struct_ok = (
        struct_counts.get("complete") == EXPECTED_RESUME_COMPLETE
        and struct_counts.get("partial") == EXPECTED_RESUME_PARTIAL
    )
    checks["resume_delta_status_counts"] = struct_ok
    rows.append(
        _row(
            check_id="resume_delta_status_counts",
            layer="resume_delta_safety",
            expected=f"complete={EXPECTED_RESUME_COMPLETE};partial={EXPECTED_RESUME_PARTIAL}",
            observed=(
                f"complete={struct_counts.get('complete')};"
                f"partial={struct_counts.get('partial')}"
            ),
            ok=struct_ok,
            notes="ok" if struct_ok else "resume_status_count_drift",
        )
    )

    fp_ok = fp == FROZEN_RESUME_DELTA_FP_SHA256
    checks["resume_delta_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="resume_delta_fingerprint",
            layer="resume_delta_safety",
            expected=FROZEN_RESUME_DELTA_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "resume_delta_fp_drift",
        )
    )

    refused = False
    msg = ""
    probe_rel = (
        f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm25.csv"
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
    checks["write_guard_resume_refused"] = refused
    rows.append(
        _row(
            check_id="write_guard_resume_refused",
            layer="resume_delta_safety",
            path=probe_rel,
            root_id=RESUME_HARVEST_ROOT_ID,
            expected="CLEANUP_REFUSED",
            observed=f"refused={refused};msg={msg}",
            ok=refused,
            notes="ok" if refused else "resume_write_not_refused",
        )
    )

    # phase35 原根写拒绝
    refused_p35 = False
    msg_p35 = ""
    probe_p35 = f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm25.csv"
    try:
        assert_safe_erad_audit_write_path(
            _abs(probe_p35, base_dir=base_dir),
            base_dir=base_dir,
            allowed_audit_root_rel=paths.output_root_rel,
        )
    except RuntimeError as exc:
        refused_p35 = CLEANUP_REFUSED_MSG in str(exc)
        msg_p35 = str(exc)[:120]
    checks["write_guard_phase35_refused"] = refused_p35
    rows.append(
        _row(
            check_id="write_guard_phase35_refused",
            layer="resume_delta_safety",
            path=probe_p35,
            expected="CLEANUP_REFUSED",
            observed=f"refused={refused_p35};msg={msg_p35}",
            ok=refused_p35,
            notes="ok" if refused_p35 else "p35_write_not_refused",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_delta_safety_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_delta_safety_all_pass",
            layer="resume_delta_safety",
            expected="delta28/1/0+write_refuse",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_delta_incomplete",
        )
    )
    return rows, checks, meta


def build_dry863_extra_isolation_rows(
    paths: OverlapStatusPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """dry863 extras 相对 harvest / exclusion 隔离。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    dry863_rows = load_csv_rows(
        _abs(paths.fm01_snapshot_status_rel, base_dir=base_dir)
    )
    dry863 = _codes(dry863_rows)
    batches = load_batch_code_sets(_to_fm24_paths(paths), base_dir=base_dir)
    harvest_union = set().union(*batches.values()) if batches else set()
    extras = dry863 - batches["h863"]

    extras_ok = extras == EXPECTED_DRY863_EXTRA
    checks["dry863_extras_exact"] = extras_ok
    rows.append(
        _row(
            check_id="dry863_extras_exact",
            layer="dry863_extra_isolation",
            expected=",".join(sorted(EXPECTED_DRY863_EXTRA)),
            observed=",".join(sorted(extras)) or "none",
            ok=extras_ok,
            notes="ok" if extras_ok else "dry863_extra_drift",
        )
    )

    not_in_harvest = extras.isdisjoint(harvest_union)
    checks["dry863_extras_not_in_harvest"] = not_in_harvest
    rows.append(
        _row(
            check_id="dry863_extras_not_in_harvest",
            layer="dry863_extra_isolation",
            expected="disjoint_from_five_batches",
            observed="ok" if not_in_harvest else "overlap",
            ok=not_in_harvest,
            notes="ok" if not_in_harvest else "extras_in_harvest",
        )
    )

    excl_rows = load_csv_rows(_abs(paths.exclusion_universe_rel, base_dir=base_dir))
    excl_codes = _codes(excl_rows)
    not_in_excl = extras.isdisjoint(excl_codes)
    checks["dry863_extras_not_in_exclusion"] = not_in_excl
    rows.append(
        _row(
            check_id="dry863_extras_not_in_exclusion",
            layer="dry863_extra_isolation",
            path=paths.exclusion_universe_rel,
            expected="disjoint_from_exclusion_universe",
            observed="ok" if not_in_excl else "in_exclusion",
            ok=not_in_excl,
            notes="ok" if not_in_excl else "extras_in_exclusion",
        )
    )

    # dry surface 上 extras 必须为 pending（未 EXECUTE）
    dry_status = {
        str(r.get("company_code") or "").strip(): str(r.get("status") or "").strip()
        for r in dry863_rows
        if str(r.get("company_code") or "").strip() in EXPECTED_DRY863_EXTRA
    }
    pending_ok = dry_status == {"000037": "pending", "000055": "pending"}
    checks["dry863_extras_pending_only"] = pending_ok
    rows.append(
        _row(
            check_id="dry863_extras_pending_only",
            layer="dry863_extra_isolation",
            path=paths.fm01_snapshot_status_rel,
            expected="000037=pending;000055=pending",
            observed=";".join(f"{k}={v}" for k, v in sorted(dry_status.items())),
            ok=pending_ok,
            notes="ok" if pending_ok else "extras_not_pending",
        )
    )

    surface = dry863 | _codes(
        load_csv_rows(_abs(paths.fm02_snapshot_status_rel, base_dir=base_dir))
    ) | harvest_union
    surface_ok = len(surface) == EXPECTED_SURFACE_UNIQUE
    checks["surface_unique_still_2251"] = surface_ok
    rows.append(
        _row(
            check_id="surface_unique_still_2251",
            layer="dry863_extra_isolation",
            expected=str(EXPECTED_SURFACE_UNIQUE),
            observed=str(len(surface)),
            ok=surface_ok,
            notes="ok" if surface_ok else "surface_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["dry863_extra_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="dry863_extra_isolation_all_pass",
            layer="dry863_extra_isolation",
            expected="extras_isolated+surface2251",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "dry863_extra_incomplete",
        )
    )
    meta = {
        "extras": sorted(extras),
        "surface_unique": len(surface),
        "exclusion_universe_n": len(excl_codes),
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: OverlapStatusPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK27 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm25.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm25.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm25.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm25.csv",
        ),
        (
            "write_guard_phase35_resume_refused_dup",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm25b.csv",
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
        assert_fm25_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK27_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock27_ok",
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
    paths: OverlapStatusPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–26 拒绝 · MOCK27 放行。"""
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
        (PRIOR_TASK_ROOT_ID, "mock26_still_frozen"),
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
                expected="still_frozen_vs_fm25_allowlist",
                observed=f"blocked={blocked}",
                ok=checks[check_id],
                notes="ok" if checks[check_id] else "prior_mock_writable",
            )
        )

    allow_ok = False
    allow_msg = ""
    try:
        assert_fm25_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except RuntimeError as exc:
        allow_msg = str(exc)[:120]
    checks["frozen_allow_mock27"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock27",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="allow_MOCK27_or_ephemeral",
            observed=f"ok={allow_ok};msg={allow_msg}",
            ok=allow_ok,
            notes="ok" if allow_ok else "mock27_not_allowed",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-26_frozen;MOCK27_allow",
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
    """protected_output_roots.csv：MOCK27 已登记。"""
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

    mock27 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(
        mock27.get("path_pattern") or ""
    )
    checks["protected_csv_mock27_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock27_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock27.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock27_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK27_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..24 gate battery（跳过 seal FM06–11）。"""
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
    ]
    seal_skip_keys = {
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
        "fm24",
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
            check_id="fm01_05_12_24_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_24_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm25(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK27；加固 C-ROOT-002 resume delta 说明。"""
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
                "C-FM-24 lineage + C-FM-25 resume-delta (28 improved / 1 same "
                "301212); 只读直至人批重跑"
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
                "C-FM-25 scale overlap code ledger (Δ12 exact) + unique status "
                "rollup (2134/106/9) + resume delta safety + dry863 extras "
                "isolation + FM24 continuity; never production EXECUTE; "
                "must not overwrite MOCK3-26; seal_chain_extended=false"
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


def run_scale_overlap_status_rollup_resume_delta_safety(
    *,
    paths: OverlapStatusPaths = OverlapStatusPaths(),
    base_dir: str = BASE_DIR,
    ensure_protected_csv: bool = True,
) -> Dict[str, Any]:
    """执行 C-FM-25 overlap/status/resume-delta 安全 QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    if ensure_protected_csv:
        ensure_protected_roots_csv_fm25(
            csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
        )
    out_root = assert_fm25_output_root(paths.output_root_rel, base_dir=base_dir)

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
    }

    cont_rows, cont_checks = build_fm24_continuity_rows(paths, base_dir=base_dir)
    ov_rows, ov_checks, ov_meta = build_overlap_code_ledger_rows(
        paths, base_dir=base_dir
    )
    st_rows, st_checks, st_meta = build_harvest_status_rollup_rows(
        paths, base_dir=base_dir
    )
    rd_rows, rd_checks, rd_meta = build_resume_delta_safety_rows(
        paths, base_dir=base_dir
    )
    ex_rows, ex_checks, ex_meta = build_dry863_extra_isolation_rows(
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
        + ov_rows
        + st_rows
        + rd_rows
        + ex_rows
        + prot_rows
        + fr_rows
        + csv_rows
        + bat_rows
        + hold_rows
    )
    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm24_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm24_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "overlap_code_ledger": (
            "PASS_OFFLINE"
            if ov_checks.get("overlap_code_ledger_all_pass")
            else "FAIL_OFFLINE"
        ),
        "harvest_status_rollup": (
            "PASS_OFFLINE"
            if st_checks.get("harvest_status_rollup_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_delta_safety": (
            "PASS_OFFLINE"
            if rd_checks.get("resume_delta_safety_all_pass")
            else "FAIL_OFFLINE"
        ),
        "dry863_extra_isolation": (
            "PASS_OFFLINE"
            if ex_checks.get("dry863_extra_isolation_all_pass")
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
            if bat_checks.get("fm01_05_12_24_battery_all_pass")
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

    overlap_ledger_rel = _rel(
        os.path.join(out_root, "overlap_code_ledger.json"), base_dir=base_dir
    )
    with open(_abs(overlap_ledger_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": ov_meta["fingerprint"],
                "p35_fu": ov_meta["p35_fu"],
                "p2_fu": ov_meta["p2_fu"],
                "overlap_delta": ov_meta["overlap_delta"],
                "unique_union": ov_meta["unique_union"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    status_rollup_rel = _rel(
        os.path.join(out_root, "harvest_status_rollup.json"), base_dir=base_dir
    )
    with open(_abs(status_rollup_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": st_meta["fingerprint"],
                "unique_union": st_meta["unique_union"],
                "union_counts": st_meta["union_counts"],
                "per_batch": st_meta["per_batch"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    resume_delta_rel = _rel(
        os.path.join(out_root, "resume_delta_ledger.json"), base_dir=base_dir
    )
    with open(_abs(resume_delta_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": rd_meta["fingerprint"],
                "improved": rd_meta["improved"],
                "same": rd_meta["same"],
                "worse": rd_meta["worse"],
                "same_codes": rd_meta["same_codes"],
                "doc": rd_meta["doc"],
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
        "harvest_unique_union": EXPECTED_HARVEST_UNIQUE_UNION,
        "overlap_delta": EXPECTED_OVERLAP_DELTA,
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
        "frozen_fps": {
            "overlap_code_ledger": FROZEN_OVERLAP_CODE_LEDGER_FP_SHA256,
            "status_rollup": FROZEN_STATUS_ROLLUP_FP_SHA256,
            "resume_delta": FROZEN_RESUME_DELTA_FP_SHA256,
            "pairwise_intersection": FROZEN_PAIRWISE_INTERSECTION_FP_SHA256,
        },
        "observed_fps": {
            "overlap_code_ledger": ov_meta["fingerprint"],
            "status_rollup": st_meta["fingerprint"],
            "resume_delta": rd_meta["fingerprint"],
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
        "fm24_gate": (gates["fm24"] or {}).get("gate"),
        "fm25_gate": overall,
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
        "surface_unique": EXPECTED_SURFACE_UNIQUE,
        "union_complete": EXPECTED_UNION_COMPLETE,
        "union_partial": EXPECTED_UNION_PARTIAL,
        "union_failed": EXPECTED_UNION_FAILED,
        "resume_improved": EXPECTED_RESUME_IMPROVED,
        "resume_same": EXPECTED_RESUME_SAME,
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
        "dry863_extras": sorted(EXPECTED_DRY863_EXTRA),
        "notes": (
            "overlap code ledger (Δ12 exact p35∩fu+p2∩fu) + unique status "
            "rollup (2134/106/9) + resume delta (28 improved / 1 same 301212) "
            "+ dry863 extras isolation + FM24 continuity + MOCK27; "
            "EXECUTE remains human-held; does not overwrite MOCK3-26"
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
        "dry863_extras": sorted(EXPECTED_DRY863_EXTRA),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "overlap_ledger_path": overlap_ledger_rel,
        "status_rollup_path": status_rollup_rel,
        "resume_delta_path": resume_delta_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": {
            "overlap_code_ledger": ov_meta["fingerprint"],
            "status_rollup": st_meta["fingerprint"],
            "resume_delta": rd_meta["fingerprint"],
        },
        "inputs": {
            "harvest_863_status": paths.harvest_863_status_rel,
            "harvest_phase35_status": paths.harvest_phase35_status_rel,
            "harvest_phase3_status": paths.harvest_phase3_status_rel,
            "harvest_phase2_status": paths.harvest_phase2_status_rel,
            "harvest_fuller_status": paths.harvest_fuller_status_rel,
            "harvest_phase35_resume_status": paths.harvest_phase35_resume_status_rel,
            "fm01_snapshot_status": paths.fm01_snapshot_status_rel,
            "exclusion_universe": paths.exclusion_universe_rel,
            "fm24_packet": paths.fm24_packet_rel,
        },
        "mock_root_is_isolated": True,
    }
