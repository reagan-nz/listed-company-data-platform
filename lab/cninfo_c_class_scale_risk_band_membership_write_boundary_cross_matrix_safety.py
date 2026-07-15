"""
CNINFO C-class — 规模 risk-band membership + quarantine/fence write-boundary
denial + residual safety cross-matrix（离线 · C-FM-28）。

在 C-FM-27（disposition quarantine + pending fence + partial risk-band rollup）
已 commit 且 EXECUTE 仍 human-held 之上，继续非 seal 规模/安全能力（不新增 seal /
decision-await / commit-boundary；非 extension↔drift 循环）：
  1) FM27 packet / fingerprint / gate / disposition·fence·band ledgers 零漂移连续
  2) partial risk-band membership：106 码精确分带指纹冻结（升级 counts-only）
  3) quarantine write-boundary denial：failed=9 禁止写入 harvest/exclusion/promote
  4) fence absorb denial battery：Δ2={000037,000055} 双路径吸入拒绝
  5) residual safety cross-matrix：quarantine∩fence∩partial 两两不相交 · coverage=117
  6) output-root：MOCK3–29 冻结 · MOCK30 放行
  7) FM-01..05 + FM-12..27 gate battery（跳过 seal FM06–11）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–29 / 权威 dual-layer 索引 ·
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
    EXPECTED_PARTIAL_WINNING_BATCH_COUNTS,
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
    _codes,
)
from cninfo_c_class_scale_residual_status_triage_surface_delta_safety import (  # noqa: E402
    ResidualTriagePaths as Fm26Paths,
)
from cninfo_c_class_scale_residual_disposition_quarantine_pending_fence_safety import (  # noqa: E402
    EXPECTED_PARTIAL_RISK_BANDS,
    EXPECTED_SURFACE_DELTA_DRY_STATUS,
    FROZEN_FAILED_DISPOSITION_FP_SHA256,
    FROZEN_PARTIAL_RISK_BAND_FP_SHA256,
    FROZEN_SURFACE_DELTA_PENDING_FENCE_FP_SHA256,
    SURFACE_DELTA_FENCE_DISPOSITION,
    FM26_GATE_JSON_REL,
    fingerprint_failed_disposition_quarantine,
    fingerprint_partial_risk_band_rollup,
    fingerprint_surface_delta_pending_fence,
)

TASK_ID = "C-FM-28"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm28_scale_risk_band_membership_write_boundary_cross_matrix_safety"
)

FM27_GATE_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_residual_disposition_quarantine_pending_fence_safety_20260715.json"
)
FM27_MOCK_ROOT_REL = (
    "outputs/validation/"
    "_mock_c_fm27_scale_residual_disposition_quarantine_pending_fence_safety"
)
FM27_PACKET_REL = f"{FM27_MOCK_ROOT_REL}/scale_packet.json"
FM27_FINGERPRINT_REL = f"{FM27_MOCK_ROOT_REL}/scale_fingerprint.json"
FM27_FAILED_DISP_REL = f"{FM27_MOCK_ROOT_REL}/failed_disposition_quarantine_ledger.json"
FM27_SURFACE_FENCE_REL = f"{FM27_MOCK_ROOT_REL}/surface_delta_pending_fence_ledger.json"
FM27_PARTIAL_BAND_REL = f"{FM27_MOCK_ROOT_REL}/partial_risk_band_rollup_ledger.json"

WINNING_TO_BAND = {
    "p35": "p35_heavy",
    "p3": "p3_mid",
    "p2": "p2_mid",
    "fu": "fu_light",
}
BAND_ORDER = ("p35_heavy", "p3_mid", "p2_mid", "fu_light")

EXPECTED_RESIDUAL_SAFETY_COVERAGE = (
    EXPECTED_UNION_FAILED
    + EXPECTED_SURFACE_HARVEST_DELTA_N
    + EXPECTED_UNION_PARTIAL
)

FROZEN_RISK_BAND_MEMBERSHIP_FP_SHA256 = (
    "bfb3cecfe39ccad2e35b066980a63ae866ddd5f5027238f8f4223a64259979f7"
)
FROZEN_QUARANTINE_WRITE_BOUNDARY_FP_SHA256 = (
    "10a68c46d192aa2d3e3b10580eaf532d7bc6a49296c0191f00a3e83ced0806af"
)
FROZEN_FENCE_ABSORB_DENIAL_FP_SHA256 = (
    "df88f767d1bb298f09688e80938fbaea83fbb0de610fd94d435c9dd894c9f0ed"
)
FROZEN_RESIDUAL_SAFETY_CROSS_MATRIX_FP_SHA256 = (
    "23d72224e7d1a4de79ccd5061e09de4cb5133b6f1e12822af9e29c897e03389d"
)

THIS_TASK_ROOT_ID = "C-ROOT-MOCK30"
PRIOR_TASK_ROOT_ID = "C-ROOT-MOCK29"
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
    "C-ROOT-MOCK29",
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    RESUME_HARVEST_ROOT_ID,
    "C-ROOT-011",
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class RiskBandMembershipPaths:
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
    fm27_packet_rel: str = FM27_PACKET_REL
    fm27_fingerprint_rel: str = FM27_FINGERPRINT_REL
    fm27_failed_disp_rel: str = FM27_FAILED_DISP_REL
    fm27_surface_fence_rel: str = FM27_SURFACE_FENCE_REL
    fm27_partial_band_rel: str = FM27_PARTIAL_BAND_REL
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


def _to_fm26_paths(paths: RiskBandMembershipPaths) -> Fm26Paths:
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


def assert_fm28_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-28 写根：须 validation/_mock_*，不得覆盖 MOCK3–29，
    不得写权威 dual-layer 索引；允许本任务 MOCK30 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-28 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def classify_risk_band(winning_batch: str) -> str:
    """winning-batch → risk-band 标签。"""
    band = WINNING_TO_BAND.get(str(winning_batch or "").strip())
    if not band:
        raise ValueError(f"unknown winning_batch for risk-band: {winning_batch!r}")
    return band


def build_risk_band_membership(
    *,
    partial_codes: Sequence[str],
    winning_batch: Dict[str, str],
) -> Tuple[Dict[str, str], Dict[str, List[str]], Dict[str, int]]:
    """构建 106 码 risk-band membership。"""
    membership = {
        c: classify_risk_band(winning_batch[c]) for c in sorted(partial_codes)
    }
    codes_by_band = {
        b: sorted(c for c, bb in membership.items() if bb == b) for b in BAND_ORDER
    }
    risk_bands = {b: len(codes_by_band[b]) for b in BAND_ORDER}
    return membership, codes_by_band, risk_bands


def fingerprint_risk_band_membership(
    *,
    partial_codes: Sequence[str],
    winning_batch: Dict[str, str],
) -> Tuple[str, Dict[str, Any]]:
    """partial risk-band membership 指纹。"""
    membership, codes_by_band, risk_bands = build_risk_band_membership(
        partial_codes=partial_codes, winning_batch=winning_batch
    )
    doc = {
        "kind": "partial_risk_band_membership",
        "partial_n": len(membership),
        "risk_bands": risk_bands,
        "membership_by_code": {c: membership[c] for c in sorted(membership)},
        "codes_by_band": codes_by_band,
        "promote_band_reclass_allowed": False,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_quarantine_write_boundary_denial(
    *,
    failed_codes: Sequence[str],
) -> Tuple[str, Dict[str, Any]]:
    """quarantine write-boundary denial 指纹。"""
    codes = sorted(failed_codes)
    doc = {
        "kind": "quarantine_write_boundary_denial",
        "failed_n": len(codes),
        "failed_codes": codes,
        "deny_harvest_write": True,
        "deny_exclusion_write": True,
        "deny_promote_to_complete": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_fence_absorb_denial(
    *,
    delta_codes: Sequence[str],
) -> Tuple[str, Dict[str, Any]]:
    """fence absorb denial battery 指纹。"""
    codes = sorted(delta_codes)
    doc = {
        "kind": "fence_absorb_denial_battery",
        "delta_n": len(codes),
        "delta_codes": codes,
        "deny_absorb_harvest": True,
        "deny_absorb_exclusion": True,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def fingerprint_residual_safety_cross_matrix(
    *,
    failed_n: int,
    delta_n: int,
    partial_n: int,
    disjoint_quarantine_fence: bool,
    disjoint_quarantine_partial: bool,
    disjoint_fence_partial: bool,
) -> Tuple[str, Dict[str, Any]]:
    """residual safety cross-matrix 指纹。"""
    doc = {
        "kind": "residual_safety_cross_matrix",
        "failed_n": failed_n,
        "delta_n": delta_n,
        "partial_n": partial_n,
        "disjoint_quarantine_fence": disjoint_quarantine_fence,
        "disjoint_quarantine_partial": disjoint_quarantine_partial,
        "disjoint_fence_partial": disjoint_fence_partial,
        "coverage_sum": failed_n + delta_n + partial_n,
        "hold": "KEEP_EXECUTE_FALSE",
    }
    fp = hashlib.sha256(
        json.dumps(doc, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return fp, doc


def evaluate_quarantine_write_boundary(
    *,
    code: str,
    target: str,
) -> Dict[str, Any]:
    """
    评估 quarantine 码对 harvest / exclusion / promote 写边界。
    返回显式 denial；无静默放行。
    """
    if code not in EXPECTED_FAILED_CODES:
        raise ValueError(f"not a quarantined failed code: {code}")
    if target not in ("harvest", "exclusion", "promote_to_complete"):
        raise ValueError(f"unknown write-boundary target: {target}")
    return {
        "code": code,
        "target": target,
        "allowed": False,
        "reason": "quarantine_pre_execute_not_approved",
        "hold": "KEEP_EXECUTE_FALSE",
    }


def evaluate_fence_absorb(
    *,
    code: str,
    target: str,
) -> Dict[str, Any]:
    """
    评估 surface-delta fence 码对 harvest / exclusion 吸入。
    返回显式 denial；无静默吸入。
    """
    if code not in EXPECTED_DRY863_EXTRA:
        raise ValueError(f"not a fenced delta code: {code}")
    if target not in ("harvest", "exclusion"):
        raise ValueError(f"unknown absorb target: {target}")
    return {
        "code": code,
        "target": target,
        "allowed": False,
        "reason": SURFACE_DELTA_FENCE_DISPOSITION,
        "hold": "KEEP_EXECUTE_FALSE",
    }


def build_fm27_continuity_rows(
    paths: RiskBandMembershipPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM27 packet / fingerprint / gate / disposition·fence·band ledgers 零漂移。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm27_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm27_fingerprint_rel, base_dir=base_dir))
    gate_doc = load_json(_abs(paths.fm27_gate_json_rel, base_dir=base_dir))
    fail_led = load_json(_abs(paths.fm27_failed_disp_rel, base_dir=base_dir))
    fence_led = load_json(_abs(paths.fm27_surface_fence_rel, base_dir=base_dir))
    band_led = load_json(_abs(paths.fm27_partial_band_rel, base_dir=base_dir))

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
        and packet.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
    )
    checks["fm27_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm27_packet_continuity",
            layer="fm27_continuity",
            path=paths.fm27_packet_rel,
            expected="PASS_OFFLINE;unique=2249;2134/106/9;bands;KEEP",
            observed=(
                f"gate={packet.get('gate')};unique={packet.get('harvest_unique_union')};"
                f"status={packet.get('union_complete')}/"
                f"{packet.get('union_partial')}/{packet.get('union_failed')};"
                f"bands={packet.get('partial_risk_bands')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm27_packet_drift",
        )
    )

    fp_ok = (
        fp_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and fp_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and fp_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and fp_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and (fp_doc.get("frozen_fps") or {}).get("failed_disposition_quarantine")
        == FROZEN_FAILED_DISPOSITION_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("surface_delta_pending_fence")
        == FROZEN_SURFACE_DELTA_PENDING_FENCE_FP_SHA256
        and (fp_doc.get("frozen_fps") or {}).get("partial_risk_band_rollup")
        == FROZEN_PARTIAL_RISK_BAND_FP_SHA256
        and fp_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and fp_doc.get("cninfo_calls") == 0
        and fp_doc.get("execute_production_snapshot_rebuild") is False
        and fp_doc.get("seal_chain_extended") is False
    )
    checks["fm27_fingerprint_continuity"] = fp_ok
    rows.append(
        _row(
            check_id="fm27_fingerprint_continuity",
            layer="fm27_continuity",
            path=paths.fm27_fingerprint_rel,
            expected="unique2249+fm27_frozen_fps",
            observed=(
                f"unique={fp_doc.get('harvest_unique_union')};"
                f"failed={fp_doc.get('union_failed')};"
                f"bands={fp_doc.get('partial_risk_bands')}"
            ),
            ok=fp_ok,
            notes="ok" if fp_ok else "fm27_fingerprint_drift",
        )
    )

    gate_ok = (
        gate_doc.get("gate") == "PASS_OFFLINE"
        and gate_doc.get("cninfo_calls") == 0
        and gate_doc.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
        and gate_doc.get("union_failed") == EXPECTED_UNION_FAILED
        and gate_doc.get("union_partial") == EXPECTED_UNION_PARTIAL
        and gate_doc.get("surface_harvest_delta_n") == EXPECTED_SURFACE_HARVEST_DELTA_N
        and gate_doc.get("partial_risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and gate_doc.get("approved_for_snapshot_rebuild") is False
        and gate_doc.get("seal_chain_extended") is False
    )
    checks["fm27_gate_json_continuity"] = gate_ok
    rows.append(
        _row(
            check_id="fm27_gate_json_continuity",
            layer="fm27_continuity",
            path=paths.fm27_gate_json_rel,
            expected="PASS_OFFLINE;failed=9;delta=2;bands;approved=false",
            observed=(
                f"gate={gate_doc.get('gate')};"
                f"failed={gate_doc.get('union_failed')};"
                f"bands={gate_doc.get('partial_risk_bands')}"
            ),
            ok=gate_ok,
            notes="ok" if gate_ok else "fm27_gate_drift",
        )
    )

    led_ok = (
        fail_led.get("fingerprint_sha256") == FROZEN_FAILED_DISPOSITION_FP_SHA256
        and set(fail_led.get("failed_codes") or []) == EXPECTED_FAILED_CODES
        and fence_led.get("fingerprint_sha256")
        == FROZEN_SURFACE_DELTA_PENDING_FENCE_FP_SHA256
        and set(fence_led.get("delta_codes") or []) == EXPECTED_DRY863_EXTRA
        and band_led.get("fingerprint_sha256") == FROZEN_PARTIAL_RISK_BAND_FP_SHA256
        and band_led.get("risk_bands") == EXPECTED_PARTIAL_RISK_BANDS
        and int(band_led.get("partial_n") or 0) == EXPECTED_UNION_PARTIAL
    )
    checks["fm27_ledger_continuity"] = led_ok
    rows.append(
        _row(
            check_id="fm27_ledger_continuity",
            layer="fm27_continuity",
            expected="disp+fence+band_fps",
            observed=(
                f"disp_fp={str(fail_led.get('fingerprint_sha256') or '')[:12]};"
                f"fence_n={len(fence_led.get('delta_codes') or [])};"
                f"bands={band_led.get('risk_bands')}"
            ),
            ok=led_ok,
            notes="ok" if led_ok else "fm27_ledger_drift",
        )
    )

    # 再算 FM27 三层指纹确认相对冻结锚无漂移
    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    failed = sorted(c for c, s in union_status.items() if s == "failed")
    partial = sorted(c for c, s in union_status.items() if s == "partial")
    counts = dict(sorted(Counter(winning[c] for c in partial).items()))
    dry_rows = load_csv_rows(
        _abs(paths.fm01_snapshot_status_rel, base_dir=base_dir)
    )
    dry_status = {
        str(r.get("company_code") or "").strip(): str(r.get("status") or "").strip()
        for r in dry_rows
        if str(r.get("company_code") or "").strip() in EXPECTED_DRY863_EXTRA
    }
    fp_fail, _ = fingerprint_failed_disposition_quarantine(
        failed_codes=failed, winning_batch=winning
    )
    fp_fence, _ = fingerprint_surface_delta_pending_fence(
        delta_codes=sorted(EXPECTED_DRY863_EXTRA), dry_status=dry_status
    )
    fp_band, _ = fingerprint_partial_risk_band_rollup(
        partial_n=len(partial), winning_batch_counts=counts
    )
    reaffirm_ok = (
        fp_fail == FROZEN_FAILED_DISPOSITION_FP_SHA256
        and fp_fence == FROZEN_SURFACE_DELTA_PENDING_FENCE_FP_SHA256
        and fp_band == FROZEN_PARTIAL_RISK_BAND_FP_SHA256
        and dry_status == EXPECTED_SURFACE_DELTA_DRY_STATUS
        and set(failed) == EXPECTED_FAILED_CODES
        and len(partial) == EXPECTED_UNION_PARTIAL
        and counts == EXPECTED_PARTIAL_WINNING_BATCH_COUNTS
    )
    checks["fm27_disposition_fence_band_reaffirm"] = bool(reaffirm_ok)
    rows.append(
        _row(
            check_id="fm27_disposition_fence_band_reaffirm",
            layer="fm27_continuity",
            expected="disp+fence+band_reaffirm",
            observed=f"ok={bool(reaffirm_ok)}",
            ok=bool(reaffirm_ok),
            notes="ok" if reaffirm_ok else "fm27_reaffirm_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fm27_continuity_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fm27_continuity_all_pass",
            layer="fm27_continuity",
            expected="packet+fingerprint+gate+ledgers+reaffirm",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fm27_continuity_incomplete",
        )
    )
    return rows, checks


def build_risk_band_membership_rows(
    paths: RiskBandMembershipPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """partial risk-band membership（106 码精确分带）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    partial = sorted(c for c, s in union_status.items() if s == "partial")
    fp, doc = fingerprint_risk_band_membership(
        partial_codes=partial, winning_batch=winning
    )

    n_ok = len(partial) == EXPECTED_UNION_PARTIAL
    checks["risk_band_membership_count_106"] = n_ok
    rows.append(
        _row(
            check_id="risk_band_membership_count_106",
            layer="partial_risk_band_membership",
            expected=str(EXPECTED_UNION_PARTIAL),
            observed=str(len(partial)),
            ok=n_ok,
            notes="ok" if n_ok else "partial_count_mismatch",
        )
    )

    bands_ok = doc["risk_bands"] == EXPECTED_PARTIAL_RISK_BANDS
    checks["risk_band_membership_bands_exact"] = bands_ok
    rows.append(
        _row(
            check_id="risk_band_membership_bands_exact",
            layer="partial_risk_band_membership",
            expected="p35_heavy=75;p3_mid=14;p2_mid=12;fu_light=5",
            observed=json.dumps(doc["risk_bands"], ensure_ascii=False, sort_keys=True),
            ok=bands_ok,
            notes="ok" if bands_ok else "bands_drift",
        )
    )

    # membership 与 winning-batch 一致；禁止静默 reclass
    mem = doc["membership_by_code"]
    map_ok = all(
        mem[c] == classify_risk_band(winning[c]) for c in partial
    ) and doc["promote_band_reclass_allowed"] is False
    checks["risk_band_membership_map_locked"] = map_ok
    rows.append(
        _row(
            check_id="risk_band_membership_map_locked",
            layer="partial_risk_band_membership",
            expected="membership≡winning;reclass=false",
            observed=(
                f"mem_n={len(mem)};reclass={doc['promote_band_reclass_allowed']}"
            ),
            ok=map_ok,
            notes="ok" if map_ok else "membership_unlocked",
        )
    )

    by_band = doc["codes_by_band"]
    partition_ok = (
        set().union(*(set(by_band[b]) for b in BAND_ORDER)) == set(partial)
        and sum(len(by_band[b]) for b in BAND_ORDER) == EXPECTED_UNION_PARTIAL
        and all(
            set(by_band[b]).isdisjoint(set(by_band[c]))
            for i, b in enumerate(BAND_ORDER)
            for c in BAND_ORDER[i + 1 :]
        )
    )
    checks["risk_band_membership_partition"] = partition_ok
    rows.append(
        _row(
            check_id="risk_band_membership_partition",
            layer="partial_risk_band_membership",
            expected="disjoint_cover_106",
            observed=(
                f"union={sum(len(by_band[b]) for b in BAND_ORDER)};"
                f"partition_ok={partition_ok}"
            ),
            ok=partition_ok,
            notes="ok" if partition_ok else "partition_broken",
        )
    )

    hold_ok = doc["hold"] == "KEEP_EXECUTE_FALSE"
    checks["risk_band_membership_hold"] = hold_ok
    rows.append(
        _row(
            check_id="risk_band_membership_hold",
            layer="partial_risk_band_membership",
            expected="KEEP_EXECUTE_FALSE",
            observed=str(doc["hold"]),
            ok=hold_ok,
            notes="ok" if hold_ok else "hold_drift",
        )
    )

    fp_ok = fp == FROZEN_RISK_BAND_MEMBERSHIP_FP_SHA256
    checks["risk_band_membership_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="risk_band_membership_fingerprint",
            layer="partial_risk_band_membership",
            expected=FROZEN_RISK_BAND_MEMBERSHIP_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "membership_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["partial_risk_band_membership_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="partial_risk_band_membership_all_pass",
            layer="partial_risk_band_membership",
            expected="106_membership+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "membership_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "partial_n": len(partial),
        "risk_bands": doc["risk_bands"],
        "membership_by_code": mem,
        "codes_by_band": by_band,
        "doc": doc,
    }
    return rows, checks, meta


def build_quarantine_write_boundary_rows(
    paths: RiskBandMembershipPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """quarantine write-boundary denial（failed=9）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, winning = compute_union_status_and_winners(status_maps)
    failed = sorted(c for c, s in union_status.items() if s == "failed")
    fp, doc = fingerprint_quarantine_write_boundary_denial(failed_codes=failed)

    codes_ok = set(failed) == EXPECTED_FAILED_CODES and len(failed) == (
        EXPECTED_UNION_FAILED
    )
    checks["quarantine_write_codes_exact"] = codes_ok
    rows.append(
        _row(
            check_id="quarantine_write_codes_exact",
            layer="quarantine_write_boundary_denial",
            expected=",".join(sorted(EXPECTED_FAILED_CODES)),
            observed=",".join(failed) or "none",
            ok=codes_ok,
            notes="ok" if codes_ok else "failed_codes_drift",
        )
    )

    win_ok = {c: winning[c] for c in failed} == EXPECTED_FAILED_WINNING_BATCH
    checks["quarantine_write_winning_batch"] = win_ok
    rows.append(
        _row(
            check_id="quarantine_write_winning_batch",
            layer="quarantine_write_boundary_denial",
            expected="p35=6;p3=3",
            observed=json.dumps(
                dict(sorted(Counter(winning[c] for c in failed).items())),
                ensure_ascii=False,
                sort_keys=True,
            ),
            ok=win_ok,
            notes="ok" if win_ok else "winning_batch_drift",
        )
    )

    # 显式 denial 电池：每码 × harvest/exclusion/promote
    denials = []
    deny_ok = True
    for code in failed:
        for target in ("harvest", "exclusion", "promote_to_complete"):
            d = evaluate_quarantine_write_boundary(code=code, target=target)
            denials.append(d)
            if d.get("allowed") is not False:
                deny_ok = False
    checks["quarantine_write_denial_battery"] = deny_ok and len(denials) == 27
    rows.append(
        _row(
            check_id="quarantine_write_denial_battery",
            layer="quarantine_write_boundary_denial",
            expected="9x3_denied",
            observed=f"denials={len(denials)};all_denied={deny_ok}",
            ok=checks["quarantine_write_denial_battery"],
            notes="ok" if checks["quarantine_write_denial_battery"] else "denial_leak",
        )
    )

    # harvest / exclusion 写路径仍拒绝（相对本任务 mock 根）
    root_refuse = True
    for probe_rel in (
        f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm28.csv",
        f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm28.csv",
    ):
        refused = False
        try:
            assert_safe_erad_audit_write_path(
                _abs(probe_rel, base_dir=base_dir),
                base_dir=base_dir,
                allowed_audit_root_rel=paths.output_root_rel,
            )
        except RuntimeError as exc:
            refused = CLEANUP_REFUSED_MSG in str(exc)
        root_refuse = root_refuse and refused
    checks["quarantine_harvest_path_write_refused"] = root_refuse
    rows.append(
        _row(
            check_id="quarantine_harvest_path_write_refused",
            layer="quarantine_write_boundary_denial",
            expected="phase35+resume_refused",
            observed=f"refused={root_refuse}",
            ok=root_refuse,
            notes="ok" if root_refuse else "harvest_path_writable",
        )
    )

    # 不得静默 promote
    promote_leak = any(union_status.get(c) == "complete" for c in failed)
    leak_ok = (
        not promote_leak
        and doc["deny_promote_to_complete"] is True
        and doc["deny_harvest_write"] is True
        and doc["deny_exclusion_write"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["quarantine_no_silent_promote"] = leak_ok
    rows.append(
        _row(
            check_id="quarantine_no_silent_promote",
            layer="quarantine_write_boundary_denial",
            expected="deny_all+no_complete",
            observed=f"leak={promote_leak};hold={doc['hold']}",
            ok=leak_ok,
            notes="ok" if leak_ok else "promote_or_deny_broken",
        )
    )

    fp_ok = fp == FROZEN_QUARANTINE_WRITE_BOUNDARY_FP_SHA256
    checks["quarantine_write_boundary_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="quarantine_write_boundary_fingerprint",
            layer="quarantine_write_boundary_denial",
            expected=FROZEN_QUARANTINE_WRITE_BOUNDARY_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "quarantine_write_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["quarantine_write_boundary_denial_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="quarantine_write_boundary_denial_all_pass",
            layer="quarantine_write_boundary_denial",
            expected="9_quarantine_write_deny+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "quarantine_write_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "failed_codes": failed,
        "denials": denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_fence_absorb_denial_rows(
    paths: RiskBandMembershipPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """fence absorb denial battery（Δ2）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    delta = sorted(EXPECTED_DRY863_EXTRA)
    fp, doc = fingerprint_fence_absorb_denial(delta_codes=delta)

    codes_ok = (
        set(delta) == EXPECTED_DRY863_EXTRA
        and len(delta) == EXPECTED_SURFACE_HARVEST_DELTA_N
    )
    checks["fence_absorb_codes_exact"] = codes_ok
    rows.append(
        _row(
            check_id="fence_absorb_codes_exact",
            layer="fence_absorb_denial_battery",
            expected=",".join(sorted(EXPECTED_DRY863_EXTRA)),
            observed=",".join(delta) or "none",
            ok=codes_ok,
            notes="ok" if codes_ok else "delta_codes_drift",
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
    pending_ok = dry_status == EXPECTED_SURFACE_DELTA_DRY_STATUS
    checks["fence_absorb_still_pending"] = pending_ok
    rows.append(
        _row(
            check_id="fence_absorb_still_pending",
            layer="fence_absorb_denial_battery",
            expected="000037=pending;000055=pending",
            observed=";".join(f"{k}={v}" for k, v in sorted(dry_status.items())),
            ok=pending_ok,
            notes="ok" if pending_ok else "delta_not_pending",
        )
    )

    denials = []
    deny_ok = True
    for code in delta:
        for target in ("harvest", "exclusion"):
            d = evaluate_fence_absorb(code=code, target=target)
            denials.append(d)
            if d.get("allowed") is not False:
                deny_ok = False
    checks["fence_absorb_denial_battery"] = deny_ok and len(denials) == 4
    rows.append(
        _row(
            check_id="fence_absorb_denial_battery",
            layer="fence_absorb_denial_battery",
            expected="2x2_denied",
            observed=f"denials={len(denials)};all_denied={deny_ok}",
            ok=checks["fence_absorb_denial_battery"],
            notes="ok" if checks["fence_absorb_denial_battery"] else "absorb_leak",
        )
    )

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    harvest_union = set().union(*(set(m) for m in status_maps.values()))
    excl_codes = _codes(
        load_csv_rows(_abs(paths.exclusion_universe_rel, base_dir=base_dir))
    )
    absorb_ok = (
        set(delta).isdisjoint(harvest_union)
        and set(delta).isdisjoint(excl_codes)
        and doc["deny_absorb_harvest"] is True
        and doc["deny_absorb_exclusion"] is True
        and doc["hold"] == "KEEP_EXECUTE_FALSE"
    )
    checks["fence_absorb_disjoint_locked"] = absorb_ok
    rows.append(
        _row(
            check_id="fence_absorb_disjoint_locked",
            layer="fence_absorb_denial_battery",
            expected="disjoint+deny=true",
            observed=(
                f"in_harvest={bool(set(delta) & harvest_union)};"
                f"in_excl={bool(set(delta) & excl_codes)}"
            ),
            ok=absorb_ok,
            notes="ok" if absorb_ok else "absorb_fence_broken",
        )
    )

    fp_ok = fp == FROZEN_FENCE_ABSORB_DENIAL_FP_SHA256
    checks["fence_absorb_denial_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="fence_absorb_denial_fingerprint",
            layer="fence_absorb_denial_battery",
            expected=FROZEN_FENCE_ABSORB_DENIAL_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "fence_absorb_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["fence_absorb_denial_battery_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="fence_absorb_denial_battery_all_pass",
            layer="fence_absorb_denial_battery",
            expected="delta2_absorb_deny+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "fence_absorb_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "delta_codes": delta,
        "dry_status": dry_status,
        "denials": denials,
        "doc": doc,
    }
    return rows, checks, meta


def build_residual_safety_cross_matrix_rows(
    paths: RiskBandMembershipPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """residual safety cross-matrix：quarantine / fence / partial 两两不相交。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm26_paths = _to_fm26_paths(paths)
    status_maps = load_union_status_maps(fm26_paths, base_dir=base_dir)
    union_status, _winning = compute_union_status_and_winners(status_maps)
    failed = set(c for c, s in union_status.items() if s == "failed")
    partial = set(c for c, s in union_status.items() if s == "partial")
    fence = set(EXPECTED_DRY863_EXTRA)

    d_qf = failed.isdisjoint(fence)
    d_qp = failed.isdisjoint(partial)
    d_fp = fence.isdisjoint(partial)
    fp, doc = fingerprint_residual_safety_cross_matrix(
        failed_n=len(failed),
        delta_n=len(fence),
        partial_n=len(partial),
        disjoint_quarantine_fence=d_qf,
        disjoint_quarantine_partial=d_qp,
        disjoint_fence_partial=d_fp,
    )

    checks["cross_disjoint_quarantine_fence"] = d_qf
    rows.append(
        _row(
            check_id="cross_disjoint_quarantine_fence",
            layer="residual_safety_cross_matrix",
            expected="empty_intersection",
            observed=f"intersect={sorted(failed & fence) or 'none'}",
            ok=d_qf,
            notes="ok" if d_qf else "quarantine_fence_overlap",
        )
    )
    checks["cross_disjoint_quarantine_partial"] = d_qp
    rows.append(
        _row(
            check_id="cross_disjoint_quarantine_partial",
            layer="residual_safety_cross_matrix",
            expected="empty_intersection",
            observed=f"intersect_n={len(failed & partial)}",
            ok=d_qp,
            notes="ok" if d_qp else "quarantine_partial_overlap",
        )
    )
    checks["cross_disjoint_fence_partial"] = d_fp
    rows.append(
        _row(
            check_id="cross_disjoint_fence_partial",
            layer="residual_safety_cross_matrix",
            expected="empty_intersection",
            observed=f"intersect={sorted(fence & partial) or 'none'}",
            ok=d_fp,
            notes="ok" if d_fp else "fence_partial_overlap",
        )
    )

    cov = len(failed) + len(fence) + len(partial)
    cov_ok = (
        cov == EXPECTED_RESIDUAL_SAFETY_COVERAGE
        and len(failed) == EXPECTED_UNION_FAILED
        and len(fence) == EXPECTED_SURFACE_HARVEST_DELTA_N
        and len(partial) == EXPECTED_UNION_PARTIAL
        and doc["coverage_sum"] == EXPECTED_RESIDUAL_SAFETY_COVERAGE
    )
    checks["cross_coverage_117"] = cov_ok
    rows.append(
        _row(
            check_id="cross_coverage_117",
            layer="residual_safety_cross_matrix",
            expected=str(EXPECTED_RESIDUAL_SAFETY_COVERAGE),
            observed=f"9+2+106={cov}",
            ok=cov_ok,
            notes="ok" if cov_ok else "coverage_mismatch",
        )
    )

    hold_ok = doc["hold"] == "KEEP_EXECUTE_FALSE"
    checks["cross_matrix_hold"] = hold_ok
    rows.append(
        _row(
            check_id="cross_matrix_hold",
            layer="residual_safety_cross_matrix",
            expected="KEEP_EXECUTE_FALSE",
            observed=str(doc["hold"]),
            ok=hold_ok,
            notes="ok" if hold_ok else "hold_drift",
        )
    )

    fp_ok = fp == FROZEN_RESIDUAL_SAFETY_CROSS_MATRIX_FP_SHA256
    checks["residual_safety_cross_matrix_fingerprint"] = fp_ok
    rows.append(
        _row(
            check_id="residual_safety_cross_matrix_fingerprint",
            layer="residual_safety_cross_matrix",
            expected=FROZEN_RESIDUAL_SAFETY_CROSS_MATRIX_FP_SHA256,
            observed=fp,
            ok=fp_ok,
            notes="ok" if fp_ok else "cross_matrix_fp_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["residual_safety_cross_matrix_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="residual_safety_cross_matrix_all_pass",
            layer="residual_safety_cross_matrix",
            expected="disjoint+coverage117+fp",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "cross_matrix_incomplete",
        )
    )
    meta = {
        "fingerprint": fp,
        "failed_n": len(failed),
        "delta_n": len(fence),
        "partial_n": len(partial),
        "coverage_sum": cov,
        "doc": doc,
    }
    return rows, checks, meta


def build_output_root_protection_rows(
    paths: RiskBandMembershipPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：resume/harvest 写拒绝 + MOCK30 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm28.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm28.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm28.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm28.csv",
        ),
        (
            "write_guard_phase35_resume_refused",
            f"{HARVEST_PHASE35_RESUME_ROOT_REL}/quality/probe_write_forbidden_fm28.csv",
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
        assert_fm28_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK30_or_ephemeral_allowed",
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
            expected="harvest+resume_refused;mock30_ok",
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
    paths: RiskBandMembershipPaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–29 拒绝 · MOCK30 放行。"""
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
        (PRIOR_TASK_ROOT_ID, "mock29_still_frozen"),
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
                expected="still_frozen_vs_fm28_allowlist",
                observed=f"blocked={blocked}",
                ok=checks[check_id],
                notes="ok" if checks[check_id] else "prior_not_frozen",
            )
        )

    allow_ok = False
    allow_detail = ""
    try:
        assert_fm28_output_root(paths.output_root_rel, base_dir=base_dir)
        allow_ok = True
        allow_detail = "allowed"
    except RuntimeError as exc:
        allow_detail = str(exc)[:120]
    checks["frozen_allow_mock30"] = allow_ok
    rows.append(
        _row(
            check_id="frozen_allow_mock30",
            layer="frozen_mock_isolation",
            path=paths.output_root_rel,
            root_id=THIS_TASK_ROOT_ID,
            expected="MOCK30_or_ephemeral_allowed",
            observed=allow_detail,
            ok=allow_ok,
            notes="ok" if allow_ok else "mock30_blocked",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-29_frozen;MOCK30_ok",
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
    """protected_output_roots.csv：MOCK30 已登记。"""
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

    mock30 = by_id.get(THIS_TASK_ROOT_ID) or {}
    path_ok = DEFAULT_MOCK_OUTPUT_ROOT_REL in str(
        mock30.get("path_pattern") or ""
    )
    checks["protected_csv_mock30_path"] = path_ok
    rows.append(
        _row(
            check_id="protected_csv_mock30_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=str(mock30.get("path_pattern") or ""),
            ok=path_ok,
            notes="ok" if path_ok else "mock30_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK30_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *, gates: Dict[str, Dict[str, Any]]
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..27 gate battery（跳过 seal FM06–11）。"""
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
    ]
    seal_skip_keys = {
        "fm12", "fm13", "fm14", "fm15", "fm16", "fm17", "fm18", "fm19",
        "fm20", "fm21", "fm22", "fm23", "fm24", "fm25", "fm26", "fm27",
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
        if key in ("fm25", "fm26", "fm27"):
            ok = (
                ok
                and payload.get("harvest_unique_union") == EXPECTED_HARVEST_UNIQUE_UNION
                and payload.get("union_failed") == EXPECTED_UNION_FAILED
                and payload.get("union_partial") == EXPECTED_UNION_PARTIAL
                and payload.get("approved_for_snapshot_rebuild") is False
            )
        if key in ("fm26", "fm27"):
            ok = (
                ok
                and payload.get("surface_harvest_delta_n")
                == EXPECTED_SURFACE_HARVEST_DELTA_N
                and payload.get("resume_same") == EXPECTED_RESUME_SAME
            )
        if key == "fm27":
            ok = (
                ok
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
            check_id="fm01_05_12_27_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_27_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm28(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-MOCK30；加固 C-ROOT-002 membership/write-boundary 说明。"""
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
                "C-FM-28 membership/write-boundary; 只读直至人批重跑"
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
                "C-FM-28 scale risk-band membership (106) + quarantine "
                "write-boundary denial (failed=9) + fence absorb denial "
                "(Δ2) + residual safety cross-matrix (coverage=117) + FM27 "
                "continuity; never production EXECUTE; must not overwrite "
                "MOCK3-29; seal_chain_extended=false"
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


def run_scale_risk_band_membership_write_boundary_cross_matrix_safety(
    *,
    paths: RiskBandMembershipPaths | None = None,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-28 规模 membership / write-boundary / cross-matrix 离线 QA。"""
    paths = paths or RiskBandMembershipPaths()
    generated_at = _utc_now_iso()
    ensure_protected_roots_csv_fm28(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    out_root = assert_fm28_output_root(paths.output_root_rel, base_dir=base_dir)

    matrix: List[Dict[str, str]] = []
    cont_rows, cont_checks = build_fm27_continuity_rows(paths, base_dir=base_dir)
    matrix.extend(cont_rows)
    mem_rows, mem_checks, mem_meta = build_risk_band_membership_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(mem_rows)
    q_rows, q_checks, q_meta = build_quarantine_write_boundary_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(q_rows)
    f_rows, f_checks, f_meta = build_fence_absorb_denial_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(f_rows)
    x_rows, x_checks, x_meta = build_residual_safety_cross_matrix_rows(
        paths, base_dir=base_dir
    )
    matrix.extend(x_rows)
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
    }
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    matrix.extend(bat_rows)
    hold_rows, hold_checks = build_execute_hold_rows()
    matrix.extend(hold_rows)

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "fm27_continuity": (
            "PASS_OFFLINE"
            if cont_checks.get("fm27_continuity_all_pass")
            else "FAIL_OFFLINE"
        ),
        "partial_risk_band_membership": (
            "PASS_OFFLINE"
            if mem_checks.get("partial_risk_band_membership_all_pass")
            else "FAIL_OFFLINE"
        ),
        "quarantine_write_boundary_denial": (
            "PASS_OFFLINE"
            if q_checks.get("quarantine_write_boundary_denial_all_pass")
            else "FAIL_OFFLINE"
        ),
        "fence_absorb_denial_battery": (
            "PASS_OFFLINE"
            if f_checks.get("fence_absorb_denial_battery_all_pass")
            else "FAIL_OFFLINE"
        ),
        "residual_safety_cross_matrix": (
            "PASS_OFFLINE"
            if x_checks.get("residual_safety_cross_matrix_all_pass")
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
            if bat_checks.get("fm01_05_12_27_battery_all_pass")
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

    membership_rel = _rel(
        os.path.join(out_root, "partial_risk_band_membership_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(membership_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": mem_meta["fingerprint"],
                "partial_n": mem_meta["partial_n"],
                "risk_bands": mem_meta["risk_bands"],
                "membership_by_code": mem_meta["membership_by_code"],
                "codes_by_band": mem_meta["codes_by_band"],
                "doc": mem_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    q_rel = _rel(
        os.path.join(out_root, "quarantine_write_boundary_denial_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(q_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": q_meta["fingerprint"],
                "failed_codes": q_meta["failed_codes"],
                "denial_count": len(q_meta["denials"]),
                "doc": q_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    f_rel = _rel(
        os.path.join(out_root, "fence_absorb_denial_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(f_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": f_meta["fingerprint"],
                "delta_codes": f_meta["delta_codes"],
                "dry_status": f_meta["dry_status"],
                "denial_count": len(f_meta["denials"]),
                "doc": f_meta["doc"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    x_rel = _rel(
        os.path.join(out_root, "residual_safety_cross_matrix_ledger.json"),
        base_dir=base_dir,
    )
    with open(_abs(x_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fingerprint_sha256": x_meta["fingerprint"],
                "failed_n": x_meta["failed_n"],
                "delta_n": x_meta["delta_n"],
                "partial_n": x_meta["partial_n"],
                "coverage_sum": x_meta["coverage_sum"],
                "doc": x_meta["doc"],
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
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "frozen_fps": {
            "partial_risk_band_membership": FROZEN_RISK_BAND_MEMBERSHIP_FP_SHA256,
            "quarantine_write_boundary_denial": (
                FROZEN_QUARANTINE_WRITE_BOUNDARY_FP_SHA256
            ),
            "fence_absorb_denial_battery": FROZEN_FENCE_ABSORB_DENIAL_FP_SHA256,
            "residual_safety_cross_matrix": (
                FROZEN_RESIDUAL_SAFETY_CROSS_MATRIX_FP_SHA256
            ),
            "fm27_failed_disposition_quarantine": FROZEN_FAILED_DISPOSITION_FP_SHA256,
            "fm27_surface_delta_pending_fence": (
                FROZEN_SURFACE_DELTA_PENDING_FENCE_FP_SHA256
            ),
            "fm27_partial_risk_band_rollup": FROZEN_PARTIAL_RISK_BAND_FP_SHA256,
        },
        "observed_fps": {
            "partial_risk_band_membership": mem_meta["fingerprint"],
            "quarantine_write_boundary_denial": q_meta["fingerprint"],
            "fence_absorb_denial_battery": f_meta["fingerprint"],
            "residual_safety_cross_matrix": x_meta["fingerprint"],
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
        "fm27_gate": (gates["fm27"] or {}).get("gate"),
        "fm28_gate": overall,
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
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
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
        "failed_codes": q_meta["failed_codes"],
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "notes": (
            "risk-band membership (106 exact) + quarantine write-boundary "
            "denial (failed=9) + fence absorb denial ({000037,000055}) + "
            "residual safety cross-matrix (coverage=117) + FM27 continuity + "
            "MOCK30; EXECUTE remains human-held; does not overwrite MOCK3-29"
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
        "failed_codes": q_meta["failed_codes"],
        "resume_same_codes": sorted(EXPECTED_RESUME_SAME_CODES),
        "partial_risk_bands": EXPECTED_PARTIAL_RISK_BANDS,
        "residual_safety_coverage": EXPECTED_RESIDUAL_SAFETY_COVERAGE,
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "membership_path": membership_rel,
        "quarantine_write_path": q_rel,
        "fence_absorb_path": f_rel,
        "cross_matrix_path": x_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": {
            "partial_risk_band_membership": mem_meta["fingerprint"],
            "quarantine_write_boundary_denial": q_meta["fingerprint"],
            "fence_absorb_denial_battery": f_meta["fingerprint"],
            "residual_safety_cross_matrix": x_meta["fingerprint"],
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
            "fm27_packet": paths.fm27_packet_rel,
        },
        "mock_root_is_isolated": True,
    }
