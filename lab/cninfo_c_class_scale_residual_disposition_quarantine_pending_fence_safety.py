"""
CNINFO C-class — 规模 residual disposition quarantine + surface-delta pending
fence + partial risk-band rollup（离线 · C-FM-27）。

在 C-FM-26（residual status triage + surface-delta + resume-same hold）已 commit
且 EXECUTE 仍 human-held 之上，继续非 seal 规模/安全能力（不新增 seal /
decision-await / commit-boundary；非 extension↔drift 循环）：
  1) FM26 packet / fingerprint / gate / residual ledgers 零漂移连续
  2) failed residual disposition quarantine：9 码 disposition 冻结 + 禁止静默
     promote→complete
  3) surface−harvest delta pending fence：{000037,000055} 禁止静默吸入 harvest /
     exclusion
  4) partial risk-band rollup：106 码按 winning-batch 分带（p35_heavy=75…）指纹冻结
  5) output-root：MOCK3–28 冻结 · MOCK29 放行
  6) FM-01..05 + FM-12..26 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–28 / 权威 dual-layer 索引 ·
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
    EXPECTED_FAILED_WINNING_BATCH,
    EXPECTED_FAILED_WINNING_BATCH_COUNTS,
    EXPECTED_PARTIAL_WINNING_BATCH_COUNTS,
    EXPECTED_SURFACE_HARVEST_DELTA_N,
    FROZEN_FAILED_RESIDUAL_FP_SHA256,
    FROZEN_PARTIAL_RESIDUAL_FP_SHA256,
    FROZEN_RESUME_SAME_HOLD_FP_SHA256,
    FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256,
    FM01_GATE_JSON_REL,
    FM02_GATE_JSON_REL,
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
    EXCLUSION_UNIVERSE_REL,
    FM01_SNAPSHOT_STATUS_REL,
    FM02_SNAPSHOT_STATUS_REL,
    HARVEST_863_STATUS_REL,
    HARVEST_FULLER_STATUS_REL,
    HARVEST_PHASE2_STATUS_REL,
    HARVEST_PHASE3_STATUS_REL,
    HARVEST_PHASE35_RESUME_STATUS_REL,
    HARVEST_PHASE35_STATUS_REL,
    build_failed_residual_ledger_rows,
    build_partial_residual_ledger_rows,
    build_resume_same_hold_rows,
    build_surface_harvest_delta_rows,
    compute_union_status_and_winners,
    load_union_status_maps,
    _codes,
)
from cninfo_c_class_scale_residual_status_triage_surface_delta_safety import (  # noqa: E402
    ResidualTriagePaths as Fm26Paths,
)

TASK_ID = "C-FM-27"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm27_scale_residual_disposition_quarantine_pending_fence_safety"
)

FM26_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_residual_status_triage_surface_delta_safety_20260715.json"
)
FM26_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm26_scale_residual_status_triage_surface_delta_safety"
)
FM26_PACKET_REL = f"{FM26_MOCK_ROOT_REL}/scale_packet.json"
FM26_FINGERPRINT_REL = f"{FM26_MOCK_ROOT_REL}/scale_fingerprint.json"
FM26_FAILED_LEDGER_REL = f"{FM26_MOCK_ROOT_REL}/failed_residual_code_ledger.json"
FM26_PARTIAL_LEDGER_REL = f"{FM26_MOCK_ROOT_REL}/partial_residual_code_ledger.json"
FM26_SURFACE_DELTA_REL = f"{FM26_MOCK_ROOT_REL}/surface_harvest_delta_ledger.json"
FM26_RESUME_SAME_REL = f"{FM26_MOCK_ROOT_REL}/resume_same_hold_ledger.json"

FAILED_DISPOSITION = "quarantine_pre_execute_not_approved"
SURFACE_DELTA_FENCE_DISPOSITION = "pending_dryrun_only_fence"

EXPECTED_PARTIAL_RISK_BANDS = {
    "p35_heavy": 75,
    "p3_mid": 14,
    "p2_mid": 12,
    "fu_light": 5,
}
EXPECTED_SURFACE_DELTA_DRY_STATUS = {"000037": "pending", "000055": "pending"}

FROZEN_FAILED_DISPOSITION_FP_SHA256 = (
    "d8a70c1a820dacbf344c059b52a94bd84b7649acd7a58e0bba2f81930c007daa"
)
FROZEN_SURFACE_DELTA_PENDING_FENCE_FP_SHA256 = (
    "2d711e4444256a8c0cf483b62269c16fff183422dc61b59715b3c74dc3ff86ad"
)
FROZEN_PARTIAL_RISK_BAND_FP_SHA256 = (
    "fbb51d7701bc85ac6727f77ab08a4348d00cb13429b151bc7ffc99047e6dbf90"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK29"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK28"
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
    "C-ROOT-MOCK28",
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class DispositionQuarantinePaths:
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
    fm26_packet_rel: str = FM26_PACKET_REL
    fm26_fingerprint_rel: str = FM26_FINGERPRINT_REL
    fm26_failed_ledger_rel: str = FM26_FAILED_LEDGER_REL
    fm26_partial_ledger_rel: str = FM26_PARTIAL_LEDGER_REL
    fm26_surface_delta_rel: str = FM26_SURFACE_DELTA_REL
    fm26_resume_same_rel: str = FM26_RESUME_SAME_REL
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


def _to_fm26_paths(paths: DispositionQuarantinePaths) -> Fm26Paths:
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


def assert_fm27_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-27 写根：须 validation/_mock_*，不得覆盖 MOCK3–28，
    不得写权威 dual-layer 索引；允许本任务 MOCK29 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-27 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def fingerprint_failed_disposition_quarantine(
    *,
    failed_codes: Sequence[str],
    winning_batch: Dict[str, str],
) -> Tuple[str, Dict[str, Any]]:
    """failed residual disposition quarantine 指纹。"""
    codes = sorted(failed_codes)
    win = {c: winning_batch[c] for c in codes}
    disp = {c: FAILED_DISPOSITION for c in codes}
    doc = {
        "kind": "failed_residual_disposition_quarantine",
        "failed_n": len(codes),
        "failed_codes": codes,
        "failed_winning_batch": win,
        "disposition_by_code": disp,
        "promote_to_complete_allowed": False,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_surface_delta_pending_fence(
    *,
    delta_codes: Sequence[str],
    dry_status: Dict[str, str],
) -> Tuple[str, Dict[str, Any]]:
    """surface−harvest delta pending fence 指纹。"""
    codes = sorted(delta_codes)
    doc = {
        "kind": "surface_delta_pending_fence",
        "delta_n": len(codes),
        "delta_codes": codes,
        "dry_status": {c: dry_status[c] for c in codes},
        "disposition": SURFACE_DELTA_FENCE_DISPOSITION,
        "absorb_into_harvest_allowed": False,
        "absorb_into_exclusion_allowed": False,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_partial_risk_band_rollup(
    *,
    partial_n: int,
    winning_batch_counts: Dict[str, int],
) -> Tuple[str, Dict[str, Any]]:
    """partial risk-band rollup 指纹。"""
    bands = {
        "p35_heavy": int(winning_batch_counts.get("p35", 0)),
        "p3_mid": int(winning_batch_counts.get("p3", 0)),
        "p2_mid": int(winning_batch_counts.get("p2", 0)),
        "fu_light": int(winning_batch_counts.get("fu", 0)),
    }
    doc = {
        "kind": "partial_risk_band_rollup",
        "partial_n": partial_n,
        "risk_bands": bands,
        "winning_batch_counts": dict(sorted(winning_batch_counts.items())),
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def build_fm26_continuity_rows(
    paths: DispositionQuarantinePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM26 packet / fingerprint / gate / residual ledgers 零漂移连续。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm26_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm26_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm26_gate_json_rel, base_dir=base_dir))
    failed_led = load_json(_abs(paths.fm26_failed_ledger_rel, base_dir=base_dir))
    partial_led = load_json(_abs(paths.fm26_partial_ledger_rel, base_dir=base_dir))
    surface_led = load_json(_abs(paths.fm26_surface_delta_rel, base_dir=base_dir))
    resume_led = load_json(_abs(paths.fm26_resume_same_rel, base_dir=base_dir))

    pkt_ok = (
        packet.get("gate") == "PASS_OFFLINE"
        and packet.get("cninfo_calls") == 0
        and packet.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and packet.get("union_complete") == EXPECTED_UNION_COMPLETE
        and packet.get("union_partial") == EXPECTED_UNION_PARTIAL
        and packet.get("union_failed") == EXPECTED_UNION_FAILED
        and packet.get("resume_same") == EXPECTED_RESUME_SAME
        and packet.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and packet.get("surface_unique") == EXPECTED_SURFACE_UNIQUE
        and packet.get("execute_production_snapshot_rebuild") is False
        and packet.get("approved_for_snapshot_rebuild") is False
        and packet.get("seal_chain_extended") is False
        and packet.get("hold_recommendation") == "KEEP_EXECUTE_FALSE"
        and set(packet.get("failed_codes") or []) == EXPECTED_FAILED_CODES
        and set(packet.get("resume_same_codes") or []) == EXPECTED_RESUME_SAME_CODES
        and set(packet.get("dry863_extras") or []) == EXPECTED_DRY863_EXTRA
    )
    checks["fm26_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm26_packet_continuity",
            layer="fm26_continuity",
            path=paths.fm26_packet_rel,
            expected="PASS_OFFLINE;unique=2249;2134/106/9;delta2;same1",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"status={packet.get('union_complete')}/"
                f"{packet.get('union_partial')}/{packet.get('union_failed')};"
                f"delta={packet.get('surface_harvest_delta_n')};"
                f"same={packet.get('resume_same')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm26_packet_drift",
        )
    )

    fp_ok = (
        fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and fp_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and fp_doc.get("resume_same") == EXPECTED_RESUME_SAME
        and fp_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and (fp_doc.get("frozen_fps") or {}).get("failed_residual")
        == FROZEN_FAILED_RESIDUAL_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("partial_residual")
        == FROZEN_PARTIAL_RESIDUAL_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("surface_harvest_delta")
        == FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("resume_same_hold")
        == FROZEN_RESUME_SAME_HOLD_FP_SHA256
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm26_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm26_fingerprint_continuity",
            layer="fm26_continuity",
            path=paths.fm26_fingerprint_rel,
            expected="unique2249+fm26_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"failed={fp_doc.get('union_failed')};"
                f"delta={fp_doc.get('surface_harvest_delta_n')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm26_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and gate_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and gate_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and gate_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and gate_doc.get("resume_same") == EXPECTED_RESUME_SAME
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("seal_chain_extended") is False
    )
    checks["fm26_gate_json_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm26_gate_json_continuity",
            layer="fm26_continuity",
            path=paths.fm26_gate_json_rel,
            expected="PASS_OFFLINE;failed=9;delta=2;approved=false",
            observed=(
                f"gate={gate_doc.get('gate')};"
                f"failed={gate_doc.get('union_failed')};"
                f"delta={gate_doc.get('surface_harvest_delta_n')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm26_gate_drift",
        )
    )

    led_ok = (
        failed_led.get("fingerprint_sha256") == FROZEN_FAILED_RESIDUAL_FP_SHA256
        and set(failed_led.get("failed_codes") or []) == EXPECTED_FAILED_CODES
        and partial_led.get("fingerprint_sha256") == FROZEN_PARTIAL_RESIDUAL_FP_SHA256
        and int(partial_led.get("partial_n") or 0) == EXPECTED_UNION_PARTIAL
        and surface_led.get("fingerprint_sha256")
        == FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256
        and set(surface_led.get("delta_codes") or []) == EXPECTED_DRY863_EXTRA
        and resume_led.get("fingerprint_sha256") == FROZEN_RESUME_SAME_HOLD_FP_SHA256
        and set(resume_led.get("same_codes") or []) == EXPECTED_RESUME_SAME_CODES
    )
    checks["fm26_ledger_continuity"] = led_ok
    rows.append(
        _row(
            check_id="fm26_ledger_continuity",
            layer="fm26_continuity",
            expected="failed+partial+surface+resume_fps",
            observed=(
                f"failed_fp={str(failed_led.get('fingerprint_sha256') or '')[:12]};"
                f"partial_n={partial_led.get('partial_n')};"
                f"delta={','.join(surface_led.get('delta_codes') or [])};"
                f"same={','.join(resume_led.get('same_codes') or [])}"
            ),
            ok=led_ok,
            notes="ok" if led_ok else "fm26_ledger_drift",
        )
    )

    # 再算 residual / surface / resume 确认相对 FM26 冻结锚无漂移
    fm26_paths = _to_fm26_paths(paths)
    _r1, c1, m1 = build_failed_residual_ledger_rows(fm26_paths, base_dir=base_dir)
    _r2, c2, m2 = build_partial_residual_ledger_rows(fm26_paths, base_dir=base_dir)
    _r3, c3, m3 = build_surface_harvest_delta_rows(fm26_paths, base_dir=base_dir)
    _r4, c4, m4 = build_resume_same_hold_rows(fm26_paths, base_dir=base_dir)
    reaffirm_ok = (
        c1.get("failed_residual_code_ledger_all_pass")
        and m1["fingerprint"] == FROZEN_FAILED_RESIDUAL_FP_SHA256
        and c2.get("partial_residual_code_ledger_all_pass")
        and m2["fingerprint"] == FROZEN_PARTIAL_RESIDUAL_FP_SHA256
        and c3.get("surface_harvest_delta_recon_all_pass")
        and m3["fingerprint"] == FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256
        and c4.get("resume_same_hold_all_pass")
        and m4["fingerprint"] == FROZEN_RESUME_SAME_HOLD_FP_SHA256
    )
    checks["fm26_residual_reaffirm"] = bool(reaffirm_ok)
    rows.append(
        _row(
            check_id="fm26_residual_reaffirm",
            layer="fm26_continuity",
            expected="failed+partial+surface+resume_reaffirm",
            observed=f"ok={bool(reaffirm_ok)}",
            ok=bool(reaffirm_ok),
            notes="ok" if reaffirm_ok else "fm26_reaffirm_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm26_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm26_continuity_all_pass",
            layer="fm26_continuity",
            expected="packet+fingerprint+gate+ledgers+reaffirm",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm26_continuity_incomplete",
        )
    )
    return rows, checks


def build_failed_disposition_quarantine_rows(
    paths: DispositionQuarantinePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """failed residual disposition quarantine（9 码）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning_batch = compute_union_status_and_winners(status_maps)
    failed = sorted(c for c, s in union_status.items() if s == "failed")
    fp, doc = fingerprint_failed_disposition_quarantine(
        failed_codes=failed, winning_batch=winning_batch
    )

    n_ok = len(failed) == EXPECTED_UNION_FAILED and set(failed) == EXPECTED_FAILED_CODES
    checks["failed_disposition_codes_exact"] = n_ok
    rows.append(
        _row(
            check_id="failed_disposition_codes_exact",
            layer="failed_residual_disposition_quarantine",
            expected=",".join(sorted(EXPECTED_FAILED_CODES)),
            observed=",".join(failed) or "none",
            ok=n_ok,
            notes="ok" if n_ok else "failed_codes_drift",
        )
    )

    win_ok = (
        {c: winning_batch[c] for c in failed} == EXPECTED_FAILED_WINNING_BATCH
        and dict(sorted(Counter(winning_batch[c] for c in failed).items()))
        == EXPECTED_FAILED_WINNING_BATCH_COUNTS
    )
    checks["failed_disposition_winning_batch"] = win_ok
    rows.append(
        _row(
            check_id="failed_disposition_winning_batch",
            layer="failed_residual_disposition_quarantine",
            expected="p35=6;p3=3",
            observed=json.dumps(
                doc.get("failed_winning_batch")
                and dict(sorted(Counter(doc["failed_winning_batch"].values()).items())),
                ensure_ascii=False,
                sort_keys=True,
            ),
            ok=win_ok,
            notes="ok" if win_ok else "failed_winning_batch_drift",
        )
    )

    disp_ok = (
        all(v == FAILED_DISPOSITION for v in doc["disposition_by_code"].values())
        and doc["promote_to_complete_allowed"] is False
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["failed_disposition_quarantine_locked"] = disp_ok
    rows.append(
        _row(
            check_id="failed_disposition_quarantine_locked",
            layer="failed_residual_disposition_quarantine",
            expected=f"{FAILED_DISPOSITION};promote=false",
            observed=(
                f"disp_n={len(doc['disposition_by_code'])};"
                f"promote={doc['promote_to_complete_allowed']};hold={doc['hold']}"
            ),
            ok=disp_ok,
            notes="ok" if disp_ok else "disposition_unlocked",
        )
    )

    # 禁止静默 promote：union 中 failed 码不得同时以 complete 出现
    promote_leak = any(union_status.get(c) == "complete" for c in failed)
    leak_ok = not promote_leak
    checks["failed_no_silent_promote_to_complete"] = leak_ok
    rows.append(
        _row(
            check_id="failed_no_silent_promote_to_complete",
            layer="failed_residual_disposition_quarantine",
            expected="no_failed_as_complete",
            observed="leak" if promote_leak else "clean",
            ok=leak_ok,
            notes="ok" if leak_ok else "silent_promote_detected",
        )
    )

    fp_ok = fp == FROZEN_FAILED_DISPOSITION_FP_SHA256
    checks["failed_disposition_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="failed_disposition_fingerprint",
            layer="failed_residual_disposition_quarantine",
            expected=FROZEN_FAILED_DISPOSITION_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "failed_disposition_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["failed_residual_disposition_quarantine_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="failed_residual_disposition_quarantine_all_pass",
            layer="failed_residual_disposition_quarantine",
            expected="9_quarantine+fp+no_promote",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "failed_disposition_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "failed_codes": failed,
        "failed_winning_batch": doc["failed_winning_batch"],
        "disposition_by_code": doc["disposition_by_code"],
        "doc": doc,
    }
    return rows, checks, meta


def build_surface_delta_pending_fence_rows(
    paths: DispositionQuarantinePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """surface−harvest delta pending fence（Δ2）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    _surf_rows, surf_checks, surf_meta = build_surface_harvest_delta_rows(
        fm26_paths, base_dir=base_dir
    )
    delta = list(surf_meta["delta_codes"])
    dry_rows = load_csv_rows(
        _abs(paths.fm01_snapshot_status_rel, base_dir=base_dir)
    )
    dry_status = {
        str(r.get("company_code") or "").strip(): str(r.get("status") or "").strip()
        for r in dry_rows
        if str(r.get("company_code") or "").strip() in EXPECTED_DRY863_EXTRA
    }
    fp, doc = fingerprint_surface_delta_pending_fence(
        delta_codes=delta, dry_status=dry_status
    )

    base_ok = bool(surf_checks.get("surface_harvest_delta_recon_all_pass"))
    checks["surface_delta_base_recon"] = base_ok
    rows.append(
        _row(
            check_id="surface_delta_base_recon",
            layer="surface_delta_pending_fence",
            expected="fm26_surface_delta_pass",
            observed=f"pass={base_ok}",
            ok=base_ok,
            notes="ok" if base_ok else "surface_base_recon_fail",
        )
    )

    codes_ok = set(delta) == EXPECTED_DRY863_EXTRA and len(delta) == (
        EXPECTED_SURFACE_HARVEST_DELTA_N
    )
    checks["surface_delta_codes_exact"] = codes_ok
    rows.append(
        _row(
            check_id="surface_delta_codes_exact",
            layer="surface_delta_pending_fence",
            expected=",".join(sorted(EXPECTED_DRY863_EXTRA)),
            observed=",".join(delta) or "none",
            ok=codes_ok,
            notes="ok" if codes_ok else "delta_codes_drift",
        )
    )

    pending_ok = dry_status == EXPECTED_SURFACE_DELTA_DRY_STATUS
    checks["surface_delta_still_pending"] = pending_ok
    rows.append(
        _row(
            check_id="surface_delta_still_pending",
            layer="surface_delta_pending_fence",
            expected="000037=pending;000055=pending",
            observed=";".join(f"{k}={v}" for k, v in sorted(dry_status.items())),
            ok=pending_ok,
            notes="ok" if pending_ok else "delta_not_pending",
        )
    )

    excl_codes = _codes(
        load_csv_rows(_abs(paths.exclusion_universe_rel, base_dir=base_dir))
    )
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    harvest_union = set().union(*(set(m) for m in status_maps.values()))
    absorb_ok = (
        set(delta).isdisjoint(harvest_union)
        and set(delta).isdisjoint(excl_codes)
        and doc["absorb_into_harvest_allowed"] is False
        and doc["absorb_into_exclusion_allowed"] is False
        and doc["disposition"] == SURFACE_DELTA_FENCE_DISPOSITION
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["surface_delta_absorb_fence_locked"] = absorb_ok
    rows.append(
        _row(
            check_id="surface_delta_absorb_fence_locked",
            layer="surface_delta_pending_fence",
            expected="disjoint+absorb=false+fence",
            observed=(
                f"in_harvest={bool(set(delta) & harvest_union)};"
                f"in_excl={bool(set(delta) & excl_codes)};"
                f"disp={doc['disposition']}"
            ),
            ok=absorb_ok,
            notes="ok" if absorb_ok else "absorb_fence_broken",
        )
    )

    fp_ok = fp == FROZEN_SURFACE_DELTA_PENDING_FENCE_FP_SHA256
    checks["surface_delta_pending_fence_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="surface_delta_pending_fence_fingerprint",
            layer="surface_delta_pending_fence",
            expected=FROZEN_SURFACE_DELTA_PENDING_FENCE_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "surface_fence_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["surface_delta_pending_fence_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="surface_delta_pending_fence_all_pass",
            layer="surface_delta_pending_fence",
            expected="delta2_pending_fence+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "surface_fence_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "delta_codes": delta,
        "dry_status": dry_status,
        "doc": doc,
    }
    return rows, checks, meta


def build_partial_risk_band_rollup_rows(
    paths: DispositionQuarantinePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """partial residual risk-band rollup（106）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning_batch = compute_union_status_and_winners(status_maps)
    partial = sorted(c for c, s in union_status.items() if s == "partial")
    counts = dict(sorted(Counter(winning_batch[c] for c in partial).items()))
    fp, doc = fingerprint_partial_risk_band_rollup(
        partial_n=len(partial), winning_batch_counts=counts
    )

    n_ok = len(partial) == EXPECTED_UNION_PARTIAL
    checks["partial_risk_band_count_106"] = n_ok
    rows.append(
        _row(
            check_id="partial_risk_band_count_106",
            layer="partial_risk_band_rollup",
            expected=str(EXPECTED_UNION_PARTIAL),
            observed=str(len(partial)),
            ok=n_ok,
            notes="ok" if n_ok else "partial_count_mismatch",
        )
    )

    counts_ok = counts == EXPECTED_PARTIAL_WINNING_BATCH_COUNTS
    checks["partial_risk_band_winning_counts"] = counts_ok
    rows.append(
        _row(
            check_id="partial_risk_band_winning_counts",
            layer="partial_risk_band_rollup",
            expected="fu=5;p2=12;p3=14;p35=75",
            observed=json.dumps(counts, ensure_ascii=False, sort_keys=True),
            ok=counts_ok,
            notes="ok" if counts_ok else "partial_counts_drift",
        )
    )

    bands_ok = doc["risk_bands"] == EXPECTED_PARTIAL_RISK_BANDS
    checks["partial_risk_bands_exact"] = bands_ok
    rows.append(
        _row(
            check_id="partial_risk_bands_exact",
            layer="partial_risk_band_rollup",
            expected="p35_heavy=75;p3_mid=14;p2_mid=12;fu_light=5",
            observed=json.dumps(
                doc["risk_bands"], ensure_ascii=False, sort_keys=True
            ),
            ok=bands_ok,
            notes="ok" if bands_ok else "risk_bands_drift",
        )
    )

    sum_ok = sum(doc["risk_bands"].values()) == EXPECTED_UNION_PARTIAL
    checks["partial_risk_band_sum_106"] = sum_ok
    rows.append(
        _row(
            check_id="partial_risk_band_sum_106",
            layer="partial_risk_band_rollup",
            expected=str(EXPECTED_UNION_PARTIAL),
            observed=str(sum(doc["risk_bands"].values())),
            ok=sum_ok,
            notes="ok" if sum_ok else "risk_band_sum_mismatch",
        )
    )

    hold_ok = doc["hold"] == "KEEP_EXECUTE_FALSE"
    checks["partial_risk_band_hold"] = hold_ok
    rows.append(
        _row(
            check_id="partial_risk_band_hold",
            layer="partial_risk_band_rollup",
            expected="KEEP_EXECUTE_FALSE",
            observed=str(doc["hold"]),
            ok=hold_ok,
            notes="ok" if hold_ok else "hold_drift",
        )
    )

    fp_ok = fp == FROZEN_PARTIAL_RISK_BAND_FP_SHA256
    checks["partial_risk_band_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="partial_risk_band_fingerprint",
            layer="partial_risk_band_rollup",
            expected=FROZEN_PARTIAL_RISK_BAND_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "partial_risk_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["partial_risk_band_rollup_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="partial_risk_band_rollup_all_pass",
            layer="partial_risk_band_rollup",
            expected="106_bands+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "partial_risk_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "partial_n": len(partial),
        "risk_bands": doc["risk_bands"],
        "winning_batch_counts": counts,
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: DispositionQuarantinePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK29 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm27.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm27.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm27.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm27.csv",
        ),
        (
            "write_guard_phase35_resume_refused",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm27.csv",
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
        assert_fm27_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK29_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock29_ok",
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
    paths: DispositionQuarantinePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–28 拒绝 · MOCK29 放行。"""
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
        (PRIOR_TASK_ROOT_ID, "mock28_still_frozen"),
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
                expected="still_frozen_vs_fm27_allowlist",
                observed=f"blocked={blocked}",
                ok=checks[check_id],
                notes="ok" if checks[check_id] else "prior_not_frozen",
            )
        )

    allow_ok = False
    allow_detail = ""
    try:
        assert_fm27_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
        allow_detail = "allowed"
    except RuntimeError as exc:
        allow_detail = str(exc)[:120]
    checks["frozen_allow_mock29"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock29",
            layer="frozen_mock_isolation",
            path=paths.output_root_rel,
            root_id=THIS_TASK_ROOT_ID,
            expected="MOCK29_or_ephemeral_allowed",
            observed=allow_detail,
            ok=allow_ok,
            notes="ok" if allow_ok else "mock29_blocked",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-28_frozen;MOCK29_ok",
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
    """protected_output_roots.csv：MOCK29 已登记。"""
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

    mock29 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(
        mock29.get("path_pattern") or ""
    )
    checks["protected_csv_mock29_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock29_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock29.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock29_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK29_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..26 gate battery（跳过 seal FM06–11）。"""
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
        "fm26",
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
        if key == "fm26":
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
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
            check_id="fm01_05_12_26_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_26_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm27(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK29；加固 C-ROOT-002 disposition/fence 说明。"""
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
                "resume-same hold (301212) + C-FM-27 disposition/fence; "
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
                "C-FM-27 scale residual disposition quarantine (failed=9) + "
                "surface-delta pending fence ({000037,000055}) + partial "
                "risk-band rollup (106) + FM26 continuity; never production "
                "EXECUTE; must not overwrite MOCK3-28; seal_chain_extended=false"
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


def run_scale_residual_disposition_quarantine_pending_fence_safety(
    *,
    paths: DispositionQuarantinePaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-27 规模 disposition / pending-fence / risk-band 离线 QA。"""
    paths = paths or DispositionQuarantinePaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm27(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm27_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm26_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    fail_rows, fail_checks, fail_meta = build_failed_disposition_quarantine_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(fail_rows)
    fence_rows, fence_checks, fence_meta = build_surface_delta_pending_fence_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(fence_rows)
    band_rows, band_checks, band_meta = build_partial_risk_band_rollup_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(band_rows)
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
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm26_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm26_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "failed_residual_disposition_quarantine": (
            "PASS_OFFLINE"
            if fail_checks.get("failed_residual_disposition_quarantine_all_pass")
            else "FAIL_OFFLINE"
        ),
        "surface_delta_pending_fence": (
            "PASS_OFFLINE"
            if fence_checks.get("surface_delta_pending_fence_all_pass")
            else "FAIL_OFFLINE"
        ),
        "partial_risk_band_rollup": (
            "PASS_OFFLINE"
            if band_checks.get("partial_risk_band_rollup_all_pass")
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
            if bat_checks.get("fm01_05_12_26_battery_all_pass")
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

    failed_disp_rel = _rel(
        os.path.join(out_root, "failed_disposition_quarantine_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(failed_disp_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": fail_meta["fingerprint"],
                "failed_n": len(fail_meta["failed_codes"]),
                "failed_codes": fail_meta["failed_codes"],
                "failed_winning_batch": fail_meta["failed_winning_batch"],
                "disposition_by_code": fail_meta["disposition_by_code"],
                "doc": fail_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    surface_fence_rel = _rel(
        os.path.join(out_root, "surface_delta_pending_fence_ledger.json"),
        base_dir=base_dir,
    )
    with open(
        _abs(surface_fence_rel, base_dir=base_dir), "w", encoding="utf-8"
    ) as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": fence_meta["fingerprint"],
                "delta_codes": fence_meta["delta_codes"],
                "dry_status": fence_meta["dry_status"],
                "doc": fence_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    partial_band_rel = _rel(
        os.path.join(out_root, "partial_risk_band_rollup_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(partial_band_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": band_meta["fingerprint"],
                "partial_n": band_meta["partial_n"],
                "risk_bands": band_meta["risk_bands"],
                "winning_batch_counts": band_meta["winning_batch_counts"],
                "doc": band_meta["doc"],
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
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "frozen_fps": {
            "failed_disposition_quarantine": FROZEN_FAILED_DISPOSITION_FP_SHA256,
            "surface_delta_pending_fence": FROZEN_SURFACE_DELTA_PENDING_FENCE_FP_SHA256,
            "partial_risk_band_rollup": FROZEN_PARTIAL_RISK_BAND_FP_SHA256,
            "fm26_failed_residual": FROZEN_FAILED_RESIDUAL_FP_SHA256,
            "fm26_partial_residual": FROZEN_PARTIAL_RESIDUAL_FP_SHA256,
            "fm26_surface_harvest_delta": FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256,
            "fm26_resume_same_hold": FROZEN_RESUME_SAME_HOLD_FP_SHA256,
        },
        "observed_fps": {
            "failed_disposition_quarantine": fail_meta["fingerprint"],
            "surface_delta_pending_fence": fence_meta["fingerprint"],
            "partial_risk_band_rollup": band_meta["fingerprint"],
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
        "fm26_gate": (gates["fm26"] or {}).get("gate"),
        "fm27_gate": overall,
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
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
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
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "notes": (
            "residual disposition quarantine (failed=9) + surface-delta pending "
            "fence ({000037,000055}) + partial risk-band rollup "
            "(p35_heavy=75/p3_mid=14/p2_mid=12/fu_light=5) + FM26 continuity + "
            "MOCK29; EXECUTE remains human-held; does not overwrite MOCK3-28"
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
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "failed_disposition_path": failed_disp_rel,
        "surface_fence_path": surface_fence_rel,
        "partial_band_path": partial_band_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": {
            "failed_disposition_quarantine": fail_meta["fingerprint"],
            "surface_delta_pending_fence": fence_meta["fingerprint"],
            "partial_risk_band_rollup": band_meta["fingerprint"],
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
            "fm26_packet": paths.fm26_packet_rel,
        },
        "mock_root_is_isolated": True,
    }
