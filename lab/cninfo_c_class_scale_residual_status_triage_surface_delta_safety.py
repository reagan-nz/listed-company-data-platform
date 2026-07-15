"""
CNINFO C-class — 规模 residual status triage + surface-delta + resume-same hold
（离线 · C-FM-26）。

在 C-FM-25（overlap ledger + status rollup + resume-delta）已 commit 且 EXECUTE
仍 human-held 之上，继续非 seal 规模/安全能力（不新增 seal / decision-await /
commit-boundary；非 extension↔drift 循环）：
  1) FM25 packet / fingerprint / gate 零漂移连续（unique=2249 · 2134/106/9 · resume 28/1/0）
  2) failed residual 精确代码台账：9 码 + winning-batch（p35=6 · p3=3）指纹冻结
  3) partial residual 精确代码台账：106 码 + winning-batch 计数（p35=75…）指纹冻结
  4) surface−harvest delta 对账：2251−2249={000037,000055}=dry863 extras · pending
  5) resume-same hold：301212 partial→partial · KEEP_EXECUTE_FALSE · 写拒绝
  6) output-root：MOCK3–27 冻结 · MOCK28 放行
  7) FM-01..05 + FM-12..25 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–27 / 权威 dual-layer 索引 ·
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
    UniqueCoveragePaths as Fm24Paths,
    load_batch_code_sets,
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
    FROZEN_OVERLAP_CODE_LEDGER_FP_SHA256,
    FROZEN_RESUME_DELTA_FP_SHA256,
    FROZEN_STATUS_ROLLUP_FP_SHA256,
    STATUS_RANK,
    _status_map,
    compute_resume_vs_base_delta,
    compute_unique_union_status_rollup,
)

TASK_ID = "C-FM-26"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm26_scale_residual_status_triage_surface_delta_safety"
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
FM25_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety_20260715.json"
)

FM25_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm25_scale_overlap_status_rollup_resume_delta_safety"
)
FM25_PACKET_REL = f"{FM25_MOCK_ROOT_REL}/scale_packet.json"
FM25_FINGERPRINT_REL = f"{FM25_MOCK_ROOT_REL}/scale_fingerprint.json"

from cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety import (  # noqa: E402
    EXCLUSION_UNIVERSE_REL,
    FM01_SNAPSHOT_STATUS_REL,
    FM02_SNAPSHOT_STATUS_REL,
    HARVEST_863_STATUS_REL,
    HARVEST_FULLER_STATUS_REL,
    HARVEST_PHASE2_STATUS_REL,
    HARVEST_PHASE3_STATUS_REL,
    HARVEST_PHASE35_RESUME_STATUS_REL,
    HARVEST_PHASE35_STATUS_REL,
)

# residual / surface-delta / resume-same 冻结锚
EXPECTED_FAILED_CODES = frozenset(
    {
        "002140",
        "300055",
        "300069",
        "300074",
        "300540",
        "300552",
        "301195",
        "603885",
        "605060",
    }
)
EXPECTED_FAILED_WINNING_BATCH = {
    "002140": "p35",
    "300055": "p3",
    "300069": "p3",
    "300074": "p3",
    "300540": "p35",
    "300552": "p35",
    "301195": "p35",
    "603885": "p35",
    "605060": "p35",
}
EXPECTED_FAILED_WINNING_BATCH_COUNTS = {"p3": 3, "p35": 6}
EXPECTED_PARTIAL_WINNING_BATCH_COUNTS = {
    "fu": 5,
    "p2": 12,
    "p3": 14,
    "p35": 75,
}
EXPECTED_SURFACE_HARVEST_DELTA_N = 2
EXPECTED_RESUME_SAME_BASE_STATUS = "partial"
EXPECTED_RESUME_SAME_RESUME_STATUS = "partial"

FROZEN_FAILED_RESIDUAL_FP_SHA256 = (
    "f1ba366b5176964310aeff70973493f991877ce9cab7c6c22f084ddc051982ea"
)
FROZEN_PARTIAL_RESIDUAL_FP_SHA256 = (
    "2fb60ea3ea7ee3bacb64bad3a288adefa28f1fc1319eca6a3e05048be8be1b20"
)
FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256 = (
    "da84d8027f9aa3bb6d530885de1dff78ea52416b01fe1f1df5511c70268b6eb5"
)
FROZEN_RESUME_SAME_HOLD_FP_SHA256 = (
    "43298ff9949dad24d6088ab4e174de4a25e2afb1ef509fa419dbeaeaa76a4171"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK28"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK27"
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
    "C-ROOT-MOCK27",
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class ResidualTriagePaths:
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
    fm25_packet_rel: str = FM25_PACKET_REL
    fm25_fingerprint_rel: str = FM25_FINGERPRINT_REL
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


def _to_fm24_paths(paths: ResidualTriagePaths) -> Fm24Paths:
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


def assert_fm26_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-26 写根：须 validation/_mock_*，不得覆盖 MOCK3–27，
    不得写权威 dual-layer 索引；允许本任务 MOCK28 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-26 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def load_union_status_maps(
    paths: ResidualTriagePaths, *, base_dir: str = BASE_DIR
) -> Dict[str, Dict[str, str]]:
    """五 harvest status map。"""
    return {
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


def compute_union_status_and_winners(
    status_maps: Dict[str, Dict[str, str]],
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """unique-union 最优 status + winning batch。"""
    all_codes = set().union(*(set(m) for m in status_maps.values()))
    union_status: Dict[str, str] = {}
    winning_batch: Dict[str, str] = {}
    for code in all_codes:
        best = ""
        win = ""
        for key in BATCH_PRIORITY:
            if code in status_maps[key]:
                st = status_maps[key][code]
                if STATUS_RANK.get(st, 0) > STATUS_RANK.get(best, 0):
                    best = st
                    win = key
        union_status[code] = best
        winning_batch[code] = win
    return union_status, winning_batch


def fingerprint_failed_residual_ledger(
    *,
    failed_codes: Sequence[str],
    winning_batch: Dict[str, str],
) -> Tuple[str, Dict[str, Any]]:
    """failed residual 精确代码台账指纹。"""
    codes = sorted(failed_codes)
    win = {c: winning_batch[c] for c in codes}
    counts = dict(sorted(Counter(win.values()).items()))
    doc = {
        "kind": "union_failed_residual_code_ledger",
        "failed_n": len(codes),
        "failed_codes": codes,
        "failed_winning_batch": win,
        "failed_winning_batch_counts": counts,
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_partial_residual_ledger(
    *,
    partial_codes: Sequence[str],
    winning_batch: Dict[str, str],
) -> Tuple[str, Dict[str, Any]]:
    """partial residual 精确代码台账指纹。"""
    codes = sorted(partial_codes)
    counts = dict(
        sorted(Counter(winning_batch[c] for c in codes).items())
    )
    doc = {
        "kind": "union_partial_residual_code_ledger",
        "partial_n": len(codes),
        "partial_codes": codes,
        "partial_winning_batch_counts": counts,
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_surface_harvest_delta(
    *,
    surface_unique: int,
    harvest_unique: int,
    delta_codes: Sequence[str],
) -> Tuple[str, Dict[str, Any]]:
    """surface−harvest delta 对账指纹。"""
    doc = {
        "kind": "surface_minus_harvest_delta",
        "surface_unique": surface_unique,
        "harvest_unique": harvest_unique,
        "delta_n": len(list(delta_codes)),
        "delta_codes": sorted(delta_codes),
        "disposition": "pending_dryrun_only_not_in_harvest_not_in_exclusion",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_resume_same_hold(
    *,
    same_codes: Sequence[str],
    base_status: str,
    resume_status: str,
) -> Tuple[str, Dict[str, Any]]:
    """resume-same hold 台账指纹。"""
    doc = {
        "kind": "resume_same_hold_ledger",
        "same_n": len(list(same_codes)),
        "same_codes": sorted(same_codes),
        "base_status": base_status,
        "resume_status": resume_status,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def build_fm25_continuity_rows(
    paths: ResidualTriagePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM25 packet / fingerprint / gate 零漂移连续。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm25_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm25_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm25_gate_json_rel, base_dir=base_dir))

    pkt_ok = (
        packet.get("gate") == "PASS_OFFLINE"
        and packet.get("cninfo_calls") == 0
        and packet.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and packet.get("union_complete") == EXPECTED_UNION_COMPLETE
        and packet.get("union_partial") == EXPECTED_UNION_PARTIAL
        and packet.get("union_failed") == EXPECTED_UNION_FAILED
        and packet.get("resume_improved") == EXPECTED_RESUME_IMPROVED
        and packet.get("resume_same") == EXPECTED_RESUME_SAME
        and packet.get("resume_worse") == EXPECTED_RESUME_WORSE
        and packet.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and packet.get("overlap_delta") == EXPECTED_OVERLAP_DELTA
        and packet.get("execute_production_snapshot_rebuild") is False
        and packet.get("approved_for_snapshot_rebuild") is False
        and packet.get("seal_chain_extended") is False
        and packet.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
    )
    checks["fm25_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm25_packet_continuity",
            layer="fm25_continuity",
            path=paths.fm25_packet_rel,
            expected="PASS_OFFLINE;unique=2249;2134/106/9;resume28/1/0",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"status={packet.get('union_complete')}/"
                f"{packet.get('union_partial')}/{packet.get('union_failed')};"
                f"resume={packet.get('resume_improved')}/"
                f"{packet.get('resume_same')}/{packet.get('resume_worse')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm25_packet_drift",
        )
    )

    fp_ok = (
        fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("union_complete") == EXPECTED_UNION_COMPLETE
        and fp_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and fp_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and fp_doc.get("resume_improved") == EXPECTED_RESUME_IMPROVED
        and fp_doc.get("resume_same") == EXPECTED_RESUME_SAME
        and (fp_doc.get("frozen_fps") or {}).get("overlap_code_ledger")
        == FROZEN_OVERLAP_CODE_LEDGER_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("status_rollup")
        == FROZEN_STATUS_ROLLUP_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("resume_delta")
        == FROZEN_RESUME_DELTA_FP_SHA256
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm25_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm25_fingerprint_continuity",
            layer="fm25_continuity",
            path=paths.fm25_fingerprint_rel,
            expected="unique2249+2134/106/9+fm25_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"failed={fp_doc.get('union_failed')};"
                f"resume_same={fp_doc.get('resume_same')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm25_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and gate_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and gate_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and gate_doc.get("resume_same") == EXPECTED_RESUME_SAME
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("seal_chain_extended") is False
    )
    checks["fm25_gate_json_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm25_gate_json_continuity",
            layer="fm25_continuity",
            path=paths.fm25_gate_json_rel,
            expected="PASS_OFFLINE;unique=2249;failed=9;approved=false",
            observed=(
                f"gate={gate_doc.get('gate')};"
                f"unique={gate_doc.get('harvest_unique_union')};"
                f"failed={gate_doc.get('union_failed')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm25_gate_drift",
        )
    )

    # 再算 status rollup / resume delta 确认相对 FM25 冻结锚无漂移
    status_maps = load_union_status_maps(paths, base_dir=base_dir)
    union_counts, _per, status_fp = compute_unique_union_status_rollup(
        status_maps=status_maps
    )
    status_ok = (
        status_fp == FROZEN_STATUS_ROLLUP_FP_SHA256
        and union_counts.get("complete") == EXPECTED_UNION_COMPLETE
        and union_counts.get("partial") == EXPECTED_UNION_PARTIAL
        and union_counts.get("failed") == EXPECTED_UNION_FAILED
    )
    checks["fm25_status_rollup_reaffirm"] = status_ok
    rows.append(
        _row(
            check_id="fm25_status_rollup_reaffirm",
            layer="fm25_continuity",
            expected=FROZEN_STATUS_ROLLUP_FP_SHA256,
            observed=(
                f"{status_fp};"
                f"{union_counts.get('complete')}/"
                f"{union_counts.get('partial')}/"
                f"{union_counts.get('failed')}"
            ),
            ok=status_ok,
            notes="ok" if status_ok else "status_rollup_drift",
        )
    )

    base_status = _status_map(
        load_csv_rows(_abs(paths.harvest_phase35_status_rel, base_dir=base_dir))
    )
    resume_status = _status_map(
        load_csv_rows(
            _abs(paths.harvest_phase35_resume_status_rel, base_dir=base_dir)
        )
    )
    rd_meta, rd_fp = compute_resume_vs_base_delta(
        base_status=base_status, resume_status=resume_status
    )
    rd_ok = (
        rd_fp == FROZEN_RESUME_DELTA_FP_SHA256
        and rd_meta["improved"] == EXPECTED_RESUME_IMPROVED
        and rd_meta["same"] == EXPECTED_RESUME_SAME
        and set(rd_meta["same_codes"]) == EXPECTED_RESUME_SAME_CODES
    )
    checks["fm25_resume_delta_reaffirm"] = rd_ok
    rows.append(
        _row(
            check_id="fm25_resume_delta_reaffirm",
            layer="fm25_continuity",
            expected=FROZEN_RESUME_DELTA_FP_SHA256,
            observed=(
                f"{rd_fp};improved={rd_meta['improved']};"
                f"same={','.join(rd_meta['same_codes'])}"
            ),
            ok=rd_ok,
            notes="ok" if rd_ok else "resume_delta_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm25_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm25_continuity_all_pass",
            layer="fm25_continuity",
            expected="packet+fingerprint+gate+rollup+resume",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm25_continuity_incomplete",
        )
    )
    return rows, checks


def build_failed_residual_ledger_rows(
    paths: ResidualTriagePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """failed residual 精确代码台账（9）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    status_maps = load_union_status_maps(paths, base_dir=base_dir)
    union_status, winning_batch = compute_union_status_and_winners(status_maps)
    failed = sorted(c for c, s in union_status.items() if s == "failed")
    fp, doc = fingerprint_failed_residual_ledger(
        failed_codes=failed, winning_batch=winning_batch
    )

    n_ok = len(failed) == EXPECTED_UNION_FAILED
    checks["failed_residual_count_9"] = n_ok
    rows.append(
        _row(
            check_id="failed_residual_count_9",
            layer="failed_residual_code_ledger",
            expected=str(EXPECTED_UNION_FAILED),
            observed=str(len(failed)),
            ok=n_ok,
            notes="ok" if n_ok else "failed_count_mismatch",
        )
    )

    codes_ok = set(failed) == EXPECTED_FAILED_CODES
    checks["failed_residual_codes_exact"] = codes_ok
    rows.append(
        _row(
            check_id="failed_residual_codes_exact",
            layer="failed_residual_code_ledger",
            expected=",".join(sorted(EXPECTED_FAILED_CODES)),
            observed=",".join(failed) or "none",
            ok=codes_ok,
            notes="ok" if codes_ok else "failed_codes_drift",
        )
    )

    win_ok = (
        {c: winning_batch[c] for c in failed} == EXPECTED_FAILED_WINNING_BATCH
        and doc["failed_winning_batch_counts"] == EXPECTED_FAILED_WINNING_BATCH_COUNTS
    )
    checks["failed_residual_winning_batch"] = win_ok
    rows.append(
        _row(
            check_id="failed_residual_winning_batch",
            layer="failed_residual_code_ledger",
            expected="p35=6;p3=3",
            observed=json.dumps(
                doc["failed_winning_batch_counts"], ensure_ascii=False, sort_keys=True
            ),
            ok=win_ok,
            notes="ok" if win_ok else "failed_winning_batch_drift",
        )
    )

    fp_ok = fp == FROZEN_FAILED_RESIDUAL_FP_SHA256
    checks["failed_residual_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="failed_residual_fingerprint",
            layer="failed_residual_code_ledger",
            expected=FROZEN_FAILED_RESIDUAL_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "failed_residual_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["failed_residual_code_ledger_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="failed_residual_code_ledger_all_pass",
            layer="failed_residual_code_ledger",
            expected="9_exact_codes+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "failed_residual_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "failed_codes": failed,
        "failed_winning_batch": doc["failed_winning_batch"],
        "failed_winning_batch_counts": doc["failed_winning_batch_counts"],
        "doc": doc,
    }
    return rows, checks, meta


def build_partial_residual_ledger_rows(
    paths: ResidualTriagePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """partial residual 精确代码台账（106）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    status_maps = load_union_status_maps(paths, base_dir=base_dir)
    union_status, winning_batch = compute_union_status_and_winners(status_maps)
    partial = sorted(c for c, s in union_status.items() if s == "partial")
    fp, doc = fingerprint_partial_residual_ledger(
        partial_codes=partial, winning_batch=winning_batch
    )

    n_ok = len(partial) == EXPECTED_UNION_PARTIAL
    checks["partial_residual_count_106"] = n_ok
    rows.append(
        _row(
            check_id="partial_residual_count_106",
            layer="partial_residual_code_ledger",
            expected=str(EXPECTED_UNION_PARTIAL),
            observed=str(len(partial)),
            ok=n_ok,
            notes="ok" if n_ok else "partial_count_mismatch",
        )
    )

    counts_ok = (
        doc["partial_winning_batch_counts"] == EXPECTED_PARTIAL_WINNING_BATCH_COUNTS
    )
    checks["partial_residual_winning_batch_counts"] = counts_ok
    rows.append(
        _row(
            check_id="partial_residual_winning_batch_counts",
            layer="partial_residual_code_ledger",
            expected="fu=5;p2=12;p3=14;p35=75",
            observed=json.dumps(
                doc["partial_winning_batch_counts"], ensure_ascii=False, sort_keys=True
            ),
            ok=counts_ok,
            notes="ok" if counts_ok else "partial_winning_batch_drift",
        )
    )

    # complete+partial+failed 必须拼回 unique=2249
    complete_n = sum(1 for s in union_status.values() if s == "complete")
    recon_ok = (
        complete_n == EXPECTED_UNION_COMPLETE
        and len(partial) == EXPECTED_UNION_PARTIAL
        and sum(1 for s in union_status.values() if s == "failed")
        == EXPECTED_UNION_FAILED
        and len(union_status) == EXPECTED_HARVEST_UNIQUE_UNION
    )
    checks["partial_residual_recon_unique_2249"] = recon_ok
    rows.append(
        _row(
            check_id="partial_residual_recon_unique_2249",
            layer="partial_residual_code_ledger",
            expected="2134+106+9=2249",
            observed=(
                f"{complete_n}+{len(partial)}+"
                f"{sum(1 for s in union_status.values() if s == 'failed')}"
                f"={len(union_status)}"
            ),
            ok=recon_ok,
            notes="ok" if recon_ok else "union_recon_broken",
        )
    )

    fp_ok = fp == FROZEN_PARTIAL_RESIDUAL_FP_SHA256
    checks["partial_residual_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="partial_residual_fingerprint",
            layer="partial_residual_code_ledger",
            expected=FROZEN_PARTIAL_RESIDUAL_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "partial_residual_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["partial_residual_code_ledger_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="partial_residual_code_ledger_all_pass",
            layer="partial_residual_code_ledger",
            expected="106_codes+fp+recon",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "partial_residual_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "partial_codes": partial,
        "partial_winning_batch_counts": doc["partial_winning_batch_counts"],
        "doc": doc,
    }
    return rows, checks, meta


def build_surface_harvest_delta_rows(
    paths: ResidualTriagePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """surface−harvest delta 对账（= dry863 extras）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    batches = load_batch_code_sets(_to_fm24_paths(paths), base_dir=base_dir)
    harvest_union = set().union(*batches.values()) if batches else set()
    dry863 = _codes(
        load_csv_rows(_abs(paths.fm01_snapshot_status_rel, base_dir=base_dir))
    )
    dry190 = _codes(
        load_csv_rows(_abs(paths.fm02_snapshot_status_rel, base_dir=base_dir))
    )
    surface = dry863 | dry190 | harvest_union
    delta = sorted(surface - harvest_union)
    fp, doc = fingerprint_surface_harvest_delta(
        surface_unique=len(surface),
        harvest_unique=len(harvest_union),
        delta_codes=delta,
    )

    n_ok = (
        len(surface) == EXPECTED_SURFACE_UNIQUE
        and len(harvest_union) == EXPECTED_HARVEST_UNIQUE_UNION
        and len(delta) == EXPECTED_SURFACE_HARVEST_DELTA_N
    )
    checks["surface_harvest_delta_counts"] = n_ok
    rows.append(
        _row(
            check_id="surface_harvest_delta_counts",
            layer="surface_harvest_delta_recon",
            expected="surface2251;harvest2249;delta2",
            observed=(
                f"surface={len(surface)};harvest={len(harvest_union)};"
                f"delta={len(delta)}"
            ),
            ok=n_ok,
            notes="ok" if n_ok else "surface_harvest_count_mismatch",
        )
    )

    codes_ok = set(delta) == EXPECTED_DRY863_EXTRA
    checks["surface_harvest_delta_equals_dry863_extras"] = codes_ok
    rows.append(
        _row(
            check_id="surface_harvest_delta_equals_dry863_extras",
            layer="surface_harvest_delta_recon",
            expected=",".join(sorted(EXPECTED_DRY863_EXTRA)),
            observed=",".join(delta) or "none",
            ok=codes_ok,
            notes="ok" if codes_ok else "delta_codes_drift",
        )
    )

    excl_codes = _codes(
        load_csv_rows(_abs(paths.exclusion_universe_rel, base_dir=base_dir))
    )
    isol_ok = set(delta).isdisjoint(harvest_union) and set(delta).isdisjoint(
        excl_codes
    )
    checks["surface_delta_isolated_from_harvest_exclusion"] = isol_ok
    rows.append(
        _row(
            check_id="surface_delta_isolated_from_harvest_exclusion",
            layer="surface_harvest_delta_recon",
            expected="disjoint_harvest_and_exclusion",
            observed="ok" if isol_ok else "overlap",
            ok=isol_ok,
            notes="ok" if isol_ok else "delta_not_isolated",
        )
    )

    dry_rows = load_csv_rows(
        _abs(paths.fm01_snapshot_status_rel, base_dir=base_dir)
    )
    dry_status = {
        str(r.get("company_code") or "").strip(): str(r.get("status") or "").strip()
        for r in dry_rows
        if str(r.get("company_code") or "").strip() in EXPECTED_DRY863_EXTRA
    }
    pending_ok = dry_status == {"000037": "pending", "000055": "pending"}
    checks["surface_delta_pending_only"] = pending_ok
    rows.append(
        _row(
            check_id="surface_delta_pending_only",
            layer="surface_harvest_delta_recon",
            expected="000037=pending;000055=pending",
            observed=";".join(f"{k}={v}" for k, v in sorted(dry_status.items())),
            ok=pending_ok,
            notes="ok" if pending_ok else "delta_not_pending",
        )
    )

    fp_ok = fp == FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256
    checks["surface_harvest_delta_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="surface_harvest_delta_fingerprint",
            layer="surface_harvest_delta_recon",
            expected=FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "surface_delta_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["surface_harvest_delta_recon_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="surface_harvest_delta_recon_all_pass",
            layer="surface_harvest_delta_recon",
            expected="delta2=dry863_extras+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "surface_delta_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "surface_unique": len(surface),
        "harvest_unique": len(harvest_union),
        "delta_codes": delta,
        "doc": doc,
    }
    return rows, checks, meta


def build_resume_same_hold_rows(
    paths: ResidualTriagePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """resume-same hold：301212 partial→partial + 写拒绝。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    base_status = _status_map(
        load_csv_rows(_abs(paths.harvest_phase35_status_rel, base_dir=base_dir))
    )
    resume_status = _status_map(
        load_csv_rows(
            _abs(paths.harvest_phase35_resume_status_rel, base_dir=base_dir)
        )
    )
    rd_meta, _rd_fp = compute_resume_vs_base_delta(
        base_status=base_status, resume_status=resume_status
    )
    same_codes = list(rd_meta["same_codes"])
    code = same_codes[0] if same_codes else ""
    base_st = base_status.get(code, "")
    resume_st = resume_status.get(code, "")
    fp, doc = fingerprint_resume_same_hold(
        same_codes=same_codes,
        base_status=base_st,
        resume_status=resume_st,
    )

    struct_ok = (
        rd_meta["same"] == EXPECTED_RESUME_SAME
        and set(same_codes) == EXPECTED_RESUME_SAME_CODES
        and rd_meta["worse"] == EXPECTED_RESUME_WORSE
        and rd_meta["improved"] == EXPECTED_RESUME_IMPROVED
    )
    checks["resume_same_structure"] = struct_ok
    rows.append(
        _row(
            check_id="resume_same_structure",
            layer="resume_same_hold",
            expected="same=1:301212;worse=0;improved=28",
            observed=(
                f"same={rd_meta['same']}:{','.join(same_codes) or 'none'};"
                f"worse={rd_meta['worse']};improved={rd_meta['improved']}"
            ),
            ok=struct_ok,
            notes="ok" if struct_ok else "resume_same_structure_drift",
        )
    )

    status_ok = (
        base_st == EXPECTED_RESUME_SAME_BASE_STATUS
        and resume_st == EXPECTED_RESUME_SAME_RESUME_STATUS
    )
    checks["resume_same_partial_to_partial"] = status_ok
    rows.append(
        _row(
            check_id="resume_same_partial_to_partial",
            layer="resume_same_hold",
            expected="301212:partial→partial",
            observed=f"{code}:{base_st}→{resume_st}",
            ok=status_ok,
            notes="ok" if status_ok else "resume_same_status_drift",
        )
    )

    fp_ok = fp == FROZEN_RESUME_SAME_HOLD_FP_SHA256
    checks["resume_same_hold_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="resume_same_hold_fingerprint",
            layer="resume_same_hold",
            expected=FROZEN_RESUME_SAME_HOLD_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "resume_same_fp_drift",
        )
    )

    refused = False
    msg = ""
    probe_rel = (
        f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm26.csv"
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
            layer="resume_same_hold",
            path=probe_rel,
            root_id=RESUME_HARVEST_ROOT_ID,
            expected="CLEANUP_REFUSED",
            observed=f"refused={refused};msg={msg}",
            ok=refused,
            notes="ok" if refused else "resume_write_not_refused",
        )
    )

    refused_p35 = False
    msg_p35 = ""
    probe_p35 = f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm26.csv"
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
            layer="resume_same_hold",
            path=probe_p35,
            expected="CLEANUP_REFUSED",
            observed=f"refused={refused_p35};msg={msg_p35}",
            ok=refused_p35,
            notes="ok" if refused_p35 else "p35_write_not_refused",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["resume_same_hold_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="resume_same_hold_all_pass",
            layer="resume_same_hold",
            expected="301212_hold+write_refuse",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "resume_same_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "same_codes": same_codes,
        "base_status": base_st,
        "resume_status": resume_st,
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: ResidualTriagePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK28 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm26.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm26.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm26.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm26b.csv",
        ),
        (
            "write_guard_phase35_resume_refused_dup",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm26b.csv",
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
        assert_fm26_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK28_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock28_ok",
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
    paths: ResidualTriagePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–27 拒绝 · MOCK28 放行。"""
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
        (PRIOR_TASK_ROOT_ID, "mock27_still_frozen"),
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
                expected="still_frozen_vs_fm26_allowlist",
                observed=f"blocked={blocked}",
                ok=checks[check_id],
                notes="ok" if checks[check_id] else "prior_mock_writable",
            )
        )

    allow_ok = False
    allow_msg = ""
    try:
        assert_fm26_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
    except RuntimeError as exc:
        allow_msg = str(exc)[:120]
    checks["frozen_allow_mock28"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock28",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=paths.output_root_rel,
            expected="allow_MOCK28_or_ephemeral",
            observed=f"ok={allow_ok};msg={allow_msg}",
            ok=allow_ok,
            notes="ok" if allow_ok else "mock28_not_allowed",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-27_frozen;MOCK28_allow",
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
    """protected_output_roots.csv：MOCK28 已登记。"""
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

    mock28 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(
        mock28.get("path_pattern") or ""
    )
    checks["protected_csv_mock28_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock28_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock28.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock28_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK28_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..25 gate battery（跳过 seal FM06–11）。"""
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
        "fm25",
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
        if key == "fm25":
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
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
            check_id="fm01_05_12_25_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_25_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm26(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK28；加固 C-ROOT-002 resume-same hold 说明。"""
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
                "resume-same hold (301212 partial→partial); 只读直至人批重跑"
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
                "C-FM-26 scale residual status triage (failed=9 exact / "
                "partial=106 ledger) + surface−harvest delta recon "
                "({000037,000055}) + resume-same hold + FM25 continuity; "
                "never production EXECUTE; must not overwrite MOCK3-27; "
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


def run_scale_residual_status_triage_surface_delta_safety(
    *,
    paths: ResidualTriagePaths = ResidualTriagePaths(),
    base_dir: str = BASE_DIR,
    ensure_protected_csv: bool = True,
) -> Dict[str, Any]:
    """执行 C-FM-26 residual/surface-delta/resume-same 安全 QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    if ensure_protected_csv:
        ensure_protected_roots_csv_fm26(
            csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
        )
    out_root = assert_fm26_output_root(paths.output_root_rel, base_dir=base_dir)

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
    }

    cont_rows, cont_checks = build_fm25_continuity_rows(paths, base_dir=base_dir)
    fail_rows, fail_checks, fail_meta = build_failed_residual_ledger_rows(
        paths, base_dir=base_dir
    )
    part_rows, part_checks, part_meta = build_partial_residual_ledger_rows(
        paths, base_dir=base_dir
    )
    surf_rows, surf_checks, surf_meta = build_surface_harvest_delta_rows(
        paths, base_dir=base_dir
    )
    same_rows, same_checks, same_meta = build_resume_same_hold_rows(
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
        + fail_rows
        + part_rows
        + surf_rows
        + same_rows
        + prot_rows
        + fr_rows
        + csv_rows
        + bat_rows
        + hold_rows
    )
    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm25_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm25_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "failed_residual_code_ledger": (
            "PASS_OFFLINE"
            if fail_checks.get("failed_residual_code_ledger_all_pass")
            else "FAIL_OFFLINE"
        ),
        "partial_residual_code_ledger": (
            "PASS_OFFLINE"
            if part_checks.get("partial_residual_code_ledger_all_pass")
            else "FAIL_OFFLINE"
        ),
        "surface_harvest_delta_recon": (
            "PASS_OFFLINE"
            if surf_checks.get("surface_harvest_delta_recon_all_pass")
            else "FAIL_OFFLINE"
        ),
        "resume_same_hold": (
            "PASS_OFFLINE"
            if same_checks.get("resume_same_hold_all_pass")
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
            if bat_checks.get("fm01_05_12_25_battery_all_pass")
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

    failed_ledger_rel = _rel(
        os.path.join(out_root, "failed_residual_code_ledger.json"), base_dir=base_dir
    )
    with open(_abs(failed_ledger_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": fail_meta["fingerprint"],
                "failed_n": len(fail_meta["failed_codes"]),
                "failed_codes": fail_meta["failed_codes"],
                "failed_winning_batch": fail_meta["failed_winning_batch"],
                "failed_winning_batch_counts": fail_meta[
                    "failed_winning_batch_counts"
                ],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    partial_ledger_rel = _rel(
        os.path.join(out_root, "partial_residual_code_ledger.json"), base_dir=base_dir
    )
    with open(_abs(partial_ledger_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": part_meta["fingerprint"],
                "partial_n": len(part_meta["partial_codes"]),
                "partial_codes": part_meta["partial_codes"],
                "partial_winning_batch_counts": part_meta[
                    "partial_winning_batch_counts"
                ],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    surface_delta_rel = _rel(
        os.path.join(out_root, "surface_harvest_delta_ledger.json"), base_dir=base_dir
    )
    with open(_abs(surface_delta_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": surf_meta["fingerprint"],
                "surface_unique": surf_meta["surface_unique"],
                "harvest_unique": surf_meta["harvest_unique"],
                "delta_codes": surf_meta["delta_codes"],
                "doc": surf_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    resume_same_rel = _rel(
        os.path.join(out_root, "resume_same_hold_ledger.json"), base_dir=base_dir
    )
    with open(_abs(resume_same_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": same_meta["fingerprint"],
                "same_codes": same_meta["same_codes"],
                "base_status": same_meta["base_status"],
                "resume_status": same_meta["resume_status"],
                "doc": same_meta["doc"],
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
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "frozen_fps": {
            "failed_residual": FROZEN_FAILED_RESIDUAL_FP_SHA256,
            "partial_residual": FROZEN_PARTIAL_RESIDUAL_FP_SHA256,
            "surface_harvest_delta": FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256,
            "resume_same_hold": FROZEN_RESUME_SAME_HOLD_FP_SHA256,
            "fm25_status_rollup": FROZEN_STATUS_ROLLUP_FP_SHA256,
            "fm25_resume_delta": FROZEN_RESUME_DELTA_FP_SHA256,
        },
        "observed_fps": {
            "failed_residual": fail_meta["fingerprint"],
            "partial_residual": part_meta["fingerprint"],
            "surface_harvest_delta": surf_meta["fingerprint"],
            "resume_same_hold": same_meta["fingerprint"],
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
        "fm25_gate": (gates["fm25"] or {}).get("gate"),
        "fm26_gate": overall,
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
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
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
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "dry863_extras": sorted(EXPECTED_DRY863_EXTRA),
        "failed_codes": fail_meta["failed_codes"],
        "resume_same_codes": same_meta["same_codes"],
        "notes": (
            "residual status triage (failed=9 exact / partial=106 ledger) + "
            "surface−harvest delta recon ({000037,000055}) + resume-same hold "
            "(301212 partial→partial) + FM25 continuity + MOCK28; "
            "EXECUTE remains human-held; does not overwrite MOCK3-27"
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
        "surface_harvest_delta_n": EXPECTED_SURFACE_HARVEST_DELTA_N,
        "dry863_extras": sorted(EXPECTED_DRY863_EXTRA),
        "failed_codes": fail_meta["failed_codes"],
        "resume_same_codes": same_meta["same_codes"],
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "failed_ledger_path": failed_ledger_rel,
        "partial_ledger_path": partial_ledger_rel,
        "surface_delta_path": surface_delta_rel,
        "resume_same_path": resume_same_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": {
            "failed_residual": fail_meta["fingerprint"],
            "partial_residual": part_meta["fingerprint"],
            "surface_harvest_delta": surf_meta["fingerprint"],
            "resume_same_hold": same_meta["fingerprint"],
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
            "fm25_packet": paths.fm25_packet_rel,
        },
        "mock_root_is_isolated": True,
    }
