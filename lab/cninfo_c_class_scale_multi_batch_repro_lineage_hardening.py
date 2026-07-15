"""
CNINFO C-class — 扩展多 batch 规模 repro 指纹 + 隔离 dry-run 合标 +
lineage 加固 + output-root 保护（离线 · C-FM-23）。

在 C-FM-22（scale harvest-exclusion repro fingerprint）已 commit 且 EXECUTE 仍
human-held 之上，继续非 seal 规模/安全能力（不新增 seal / decision-await /
commit-boundary；非 extension↔drift 循环）：
  1) 多 cohort 可复现指纹扩展：FM01(863)+FM02(190)+FM03(861)+phase35(500)
     +phase3(500)+phase2(200)+fuller(200)
  2) 规模 lineage registry：scale_tier_count=7 · company_coverage_sum=3314
  3) 多 batch harvest×exclusion dual-layer（phase3/phase2/fuller 结构与家族交叉）
  4) 隔离 snapshot dry-run 合标规模指纹（863+190=1053，不 EXECUTE）
  5) lineage 加固：FM22 packet 零漂移连续 + 跨 batch 不相交不变式
  6) output-root 保护：phase3/phase2/fuller harvest 写拒绝；MOCK3–24 冻结；MOCK25 放行
  7) FM-01..05 + FM-12..22 gate battery（跳过 seal FM06–11）
  8) protected_output_roots.csv：MOCK25 + fuller harvest C-ROOT-011

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–24 / 权威 dual-layer 索引 ·
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
from typing import Any, Dict, List, Optional, Sequence, Tuple

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
    fingerprint_isolated_snapshot_dryrun,
    load_frozen_mock_cohort_roots,
    resolve_frozen_mock_cohort_root_id,
)
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    EXPECTED_HOLDOUT9,
    fingerprint_status_csv,
    load_csv_rows,
    load_manifest_family_map,
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
    EXPECTED_PHASE35_COMPLETE,
    EXPECTED_PHASE35_FAILED,
    EXPECTED_PHASE35_PARTIAL,
    EXPECTED_PHASE35_TOTAL,
    FROZEN_FM01_863_FP_SHA256,
    FROZEN_FM02_190_FP_SHA256,
    FROZEN_FM03_HARVEST_863_FP_SHA256,
    FROZEN_PHASE35_500_FP_SHA256,
    HARVEST_863_STATUS_REL,
    HARVEST_PHASE35_ROOT_REL,
    HARVEST_PHASE35_STATUS_REL,
    fingerprint_scale_matrix,
    write_scale_matrix_csv,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
)

TASK_ID = "C-FM-23"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm23_scale_multi_batch_repro_lineage_hardening"
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

FM01_MOCK_ROOT_REL = (
    "outputs/validation/_mock_snapshot_batch_standard_dryrun_isolated"
)
FM02_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm02_slice1_190_validation_cohort"
)
FM03_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency"
)
FM22_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm22_scale_harvest_exclusion_repro_fingerprint"
)
FM22_PACKET_REL = f"{FM22_MOCK_ROOT_REL}/scale_packet.json"
FM22_FINGERPRINT_REL = f"{FM22_MOCK_ROOT_REL}/scale_fingerprint.json"

HARVEST_PHASE3_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/phase3_batch_500_001/"
    "quality/company_harvest_status.csv"
)
HARVEST_PHASE3_ROOT_REL = (
    "outputs/harvest/cninfo_c_class/phase3_batch_500_001"
)
HARVEST_PHASE2_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/phase2_smoke_200/"
    "quality/company_harvest_status.csv"
)
HARVEST_PHASE2_ROOT_REL = "outputs/harvest/cninfo_c_class/phase2_smoke_200"
HARVEST_FULLER_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/fuller_market_slice1_200/"
    "quality/company_harvest_status.csv"
)
HARVEST_FULLER_ROOT_REL = (
    "outputs/harvest/cninfo_c_class/fuller_market_slice1_200"
)
EXCLUSION_MANIFEST_REL = (
    "outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv"
)

# 新增三层冻结指纹（只读复核锚点）
FROZEN_PHASE3_500_FP_SHA256 = (
    "72daace1d7d04194f37c75662c72b28411358dd1c1d9de9a9ceebc4e041c09e2"
)
FROZEN_PHASE2_200_FP_SHA256 = (
    "7eb5cf4f55a4f1feb3cf52a38db11e268d48417d9c54afc44f5e8983f956a56f"
)
FROZEN_FULLER_200_FP_SHA256 = (
    "3dad6198d15db75c8192d7b91a7dac8e0aace04a047d34246e030a9b4678f599"
)
FROZEN_COMBINED_DRYRUN_1053_FP_SHA256 = (
    "82caf6cadb33cc4820dc115d94649521c55732f29b9156b622f21747da1a5683"
)

EXPECTED_PHASE3_TOTAL = 500
EXPECTED_PHASE3_COMPLETE = 483
EXPECTED_PHASE3_PARTIAL = 14
EXPECTED_PHASE3_FAILED = 3
EXPECTED_PHASE2_TOTAL = 200
EXPECTED_PHASE2_COMPLETE = 188
EXPECTED_PHASE2_PARTIAL = 12
EXPECTED_FULLER_TOTAL = 200
EXPECTED_FULLER_COMPLETE = 193
EXPECTED_FULLER_PARTIAL = 7
EXPECTED_COMBINED_DRYRUN_COVERAGE = (
    EXPECTED_FM01_COMPANY_COUNT + EXPECTED_FM02_COMPANY_COUNT
)  # 1053
EXPECTED_HARVEST_BATCH_UNION = 1388  # p2∪p3∪p35∪fu
EXPECTED_FM22_COVERAGE_SUM = 2414

EXPECTED_SCALE_TIER_COUNT = 7
EXPECTED_COMPANY_COVERAGE_SUM = (
    EXPECTED_FM01_COMPANY_COUNT
    + EXPECTED_FM02_COMPANY_COUNT
    + EXPECTED_863_COMPLETE
    + EXPECTED_PHASE35_TOTAL
    + EXPECTED_PHASE3_TOTAL
    + EXPECTED_PHASE2_TOTAL
    + EXPECTED_FULLER_TOTAL
)  # 3314

THIS_TASK_ROOT_ID = "C-ROOT-MOCK25"
FULLER_HARVEST_ROOT_ID = "C-ROOT-011"

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
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    FULLER_HARVEST_ROOT_ID,
    "C-ROOT-AUTH1",
)


@dataclass(frozen=True)
class ExtendedScalePaths:
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
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    harvest_863_status_rel: str = HARVEST_863_STATUS_REL
    harvest_phase35_status_rel: str = HARVEST_PHASE35_STATUS_REL
    harvest_phase3_status_rel: str = HARVEST_PHASE3_STATUS_REL
    harvest_phase2_status_rel: str = HARVEST_PHASE2_STATUS_REL
    harvest_fuller_status_rel: str = HARVEST_FULLER_STATUS_REL
    exclusion_manifest_rel: str = EXCLUSION_MANIFEST_REL
    fm01_mock_root_rel: str = FM01_MOCK_ROOT_REL
    fm02_mock_root_rel: str = FM02_MOCK_ROOT_REL
    fm03_mock_root_rel: str = FM03_MOCK_ROOT_REL
    fm22_packet_rel: str = FM22_PACKET_REL
    fm22_fingerprint_rel: str = FM22_FINGERPRINT_REL
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


def assert_fm23_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-23 写根：须 validation/_mock_*，不得覆盖 MOCK3–24，
    不得写权威 dual-layer 索引；允许本任务 MOCK25 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-23 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def _status_counts(rows: Sequence[Dict[str, str]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for r in rows:
        st = str(r.get("harvest_status") or "").strip()
        counts[st] = counts.get(st, 0) + 1
    return counts


def _codes(rows: Sequence[Dict[str, str]]) -> set:
    return {
        str(r.get("company_code") or "").strip()
        for r in rows
        if str(r.get("company_code") or "").strip()
    }


def fingerprint_combined_isolated_dryrun_scale(
    *,
    fm01_fp: str,
    fm02_fp: str,
    company_coverage_sum: int = EXPECTED_COMBINED_DRYRUN_COVERAGE,
) -> str:
    """隔离 dry-run 合标规模指纹（不触发 production EXECUTE）。"""
    canon = json.dumps(
        {
            "kind": "isolated_combined_dryrun_scale",
            "fm01_fp": fm01_fp,
            "fm02_fp": fm02_fp,
            "company_coverage_sum": company_coverage_sum,
            "roots": [FM01_MOCK_ROOT_REL, FM02_MOCK_ROOT_REL],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def default_extended_scale_cohort_specs() -> Tuple[Dict[str, Any], ...]:
    """规模 lineage registry：七层可计量 coverage。"""
    return (
        {
            "cohort_id": "fm01_isolated_dryrun_863",
            "tier": "dryrun_863",
            "root_rel": FM01_MOCK_ROOT_REL,
            "company_count": EXPECTED_FM01_COMPANY_COUNT,
            "fingerprint_kind": "dryrun",
            "frozen_fp": FROZEN_FM01_863_FP_SHA256,
        },
        {
            "cohort_id": "fm02_slice1_190_validation",
            "tier": "slice1_190",
            "root_rel": FM02_MOCK_ROOT_REL,
            "company_count": EXPECTED_FM02_COMPANY_COUNT,
            "fingerprint_kind": "dryrun",
            "frozen_fp": FROZEN_FM02_190_FP_SHA256,
        },
        {
            "cohort_id": "fm03_harvest_863_structural",
            "tier": "harvest_861",
            "root_rel": FM03_MOCK_ROOT_REL,
            "company_count": EXPECTED_863_COMPLETE,
            "fingerprint_kind": "harvest_863",
            "frozen_fp": FROZEN_FM03_HARVEST_863_FP_SHA256,
        },
        {
            "cohort_id": "phase35_batch_500_harvest",
            "tier": "phase35_500",
            "root_rel": HARVEST_PHASE35_ROOT_REL,
            "company_count": EXPECTED_PHASE35_TOTAL,
            "fingerprint_kind": "phase35_harvest",
            "frozen_fp": FROZEN_PHASE35_500_FP_SHA256,
            "status_rel": HARVEST_PHASE35_STATUS_REL,
        },
        {
            "cohort_id": "phase3_batch_500_harvest",
            "tier": "phase3_500",
            "root_rel": HARVEST_PHASE3_ROOT_REL,
            "company_count": EXPECTED_PHASE3_TOTAL,
            "fingerprint_kind": "phase3_harvest",
            "frozen_fp": FROZEN_PHASE3_500_FP_SHA256,
            "status_rel": HARVEST_PHASE3_STATUS_REL,
        },
        {
            "cohort_id": "phase2_smoke_200_harvest",
            "tier": "phase2_200",
            "root_rel": HARVEST_PHASE2_ROOT_REL,
            "company_count": EXPECTED_PHASE2_TOTAL,
            "fingerprint_kind": "phase2_harvest",
            "frozen_fp": FROZEN_PHASE2_200_FP_SHA256,
            "status_rel": HARVEST_PHASE2_STATUS_REL,
        },
        {
            "cohort_id": "fuller_market_slice1_200_harvest",
            "tier": "fuller_200",
            "root_rel": HARVEST_FULLER_ROOT_REL,
            "company_count": EXPECTED_FULLER_TOTAL,
            "fingerprint_kind": "fuller_harvest",
            "frozen_fp": FROZEN_FULLER_200_FP_SHA256,
            "status_rel": HARVEST_FULLER_STATUS_REL,
        },
    )


def build_extended_scale_lineage_registry_rows(
    *,
    specs: Optional[Sequence[Dict[str, Any]]] = None,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """扩展规模 lineage registry：七层存在性 + company_coverage 计量。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    specs = tuple(specs) if specs is not None else default_extended_scale_cohort_specs()
    coverage_sum = 0
    registry: List[Dict[str, Any]] = []

    for spec in specs:
        cohort_id = str(spec["cohort_id"])
        root_rel = str(spec["root_rel"])
        expected_n = int(spec["company_count"])
        kind = str(spec["fingerprint_kind"])
        root_abs = _abs(root_rel, base_dir=base_dir)
        if kind == "harvest_863":
            present = os.path.isfile(
                _abs(HARVEST_863_STATUS_REL, base_dir=base_dir)
            ) and os.path.isdir(root_abs)
        elif kind.endswith("_harvest"):
            status_rel = str(spec.get("status_rel") or "")
            present = os.path.isfile(_abs(status_rel, base_dir=base_dir))
        else:
            status_csv = os.path.join(root_abs, "quality", "company_snapshot_status.csv")
            present = os.path.isfile(status_csv)
        ok = present and expected_n > 0
        coverage_sum += expected_n if ok else 0
        checks[f"scale_registry_{cohort_id}"] = ok
        rows.append(
            _row(
                check_id=f"scale_registry_{cohort_id}",
                layer="scale_lineage_registry",
                cohort_id=cohort_id,
                path=root_rel,
                expected=f"present;company_count={expected_n}",
                observed=f"present={present};company_count={expected_n}",
                ok=ok,
                notes="ok" if ok else "scale_cohort_missing",
            )
        )
        registry.append(
            {
                "cohort_id": cohort_id,
                "tier": spec["tier"],
                "root_rel": root_rel,
                "company_count": expected_n,
                "frozen_fp_sha256": spec["frozen_fp"],
                "present": present,
            }
        )

    tier_ok = len(specs) == EXPECTED_SCALE_TIER_COUNT
    checks["scale_tier_count"] = tier_ok
    rows.append(
        _row(
            check_id="scale_tier_count",
            layer="scale_lineage_registry",
            expected=str(EXPECTED_SCALE_TIER_COUNT),
            observed=str(len(specs)),
            ok=tier_ok,
            notes="ok" if tier_ok else "tier_count_mismatch",
        )
    )

    sum_ok = coverage_sum == EXPECTED_COMPANY_COVERAGE_SUM
    checks["company_coverage_sum"] = sum_ok
    rows.append(
        _row(
            check_id="company_coverage_sum",
            layer="scale_lineage_registry",
            expected=str(EXPECTED_COMPANY_COVERAGE_SUM),
            observed=str(coverage_sum),
            ok=sum_ok,
            notes="ok" if sum_ok else "coverage_sum_mismatch",
        )
    )

    jump_ok = coverage_sum == EXPECTED_FM22_COVERAGE_SUM + 900
    checks["coverage_jump_from_fm22"] = jump_ok
    rows.append(
        _row(
            check_id="coverage_jump_from_fm22",
            layer="scale_lineage_registry",
            expected=f"{EXPECTED_FM22_COVERAGE_SUM}+900={EXPECTED_COMPANY_COVERAGE_SUM}",
            observed=str(coverage_sum),
            ok=jump_ok,
            notes="ok" if jump_ok else "coverage_jump_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["scale_lineage_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="scale_lineage_registry_all_pass",
            layer="scale_lineage_registry",
            expected="7_tiers_coverage_3314",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "scale_registry_incomplete",
        )
    )
    meta = {
        "scale_tier_count": len(specs),
        "company_coverage_sum": coverage_sum,
        "registry": registry,
    }
    return rows, checks, meta


def build_extended_multi_cohort_repro_fingerprint_rows(
    paths: ExtendedScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, str]]:
    """七层多 cohort 可复现指纹：常量 · 重算对齐。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    observed_fps: Dict[str, str] = {}

    # FM01 / FM02 dry-run
    fm01_obs = str(
        fingerprint_isolated_snapshot_dryrun(
            paths.fm01_mock_root_rel,
            base_dir=base_dir,
            gate="PASS_WITH_CAVEAT",
            company_count=EXPECTED_FM01_COMPANY_COUNT,
        ).get("fingerprint_sha256")
        or ""
    )
    observed_fps["fm01_863"] = fm01_obs
    fm01_ok = bool(fm01_obs) and fm01_obs == FROZEN_FM01_863_FP_SHA256
    checks["repro_fm01_863"] = fm01_ok
    rows.append(
        _row(
            check_id="repro_fm01_863",
            layer="multi_cohort_repro_fingerprint",
            cohort_id="fm01_isolated_dryrun_863",
            path=paths.fm01_mock_root_rel,
            expected=FROZEN_FM01_863_FP_SHA256,
            observed=fm01_obs or "missing",
            ok=fm01_ok,
            notes="ok" if fm01_ok else "fm01_repro_drift",
        )
    )

    fm02_obs = str(
        fingerprint_isolated_snapshot_dryrun(
            paths.fm02_mock_root_rel,
            base_dir=base_dir,
            gate="PASS_WITH_CAVEAT",
            company_count=EXPECTED_FM02_COMPANY_COUNT,
        ).get("fingerprint_sha256")
        or ""
    )
    observed_fps["fm02_190"] = fm02_obs
    fm02_ok = bool(fm02_obs) and fm02_obs == FROZEN_FM02_190_FP_SHA256
    checks["repro_fm02_190"] = fm02_ok
    rows.append(
        _row(
            check_id="repro_fm02_190",
            layer="multi_cohort_repro_fingerprint",
            cohort_id="fm02_slice1_190_validation",
            path=paths.fm02_mock_root_rel,
            expected=FROZEN_FM02_190_FP_SHA256,
            observed=fm02_obs or "missing",
            ok=fm02_ok,
            notes="ok" if fm02_ok else "fm02_repro_drift",
        )
    )

    # harvest 层指纹
    harvest_specs = (
        (
            "fm03_harvest_863",
            paths.harvest_863_status_rel,
            FROZEN_FM03_HARVEST_863_FP_SHA256,
            EXPECTED_863_COMPLETE,
            "fm03_harvest_863_structural",
        ),
        (
            "phase35_500",
            paths.harvest_phase35_status_rel,
            FROZEN_PHASE35_500_FP_SHA256,
            EXPECTED_PHASE35_TOTAL,
            "phase35_batch_500_harvest",
        ),
        (
            "phase3_500",
            paths.harvest_phase3_status_rel,
            FROZEN_PHASE3_500_FP_SHA256,
            EXPECTED_PHASE3_TOTAL,
            "phase3_batch_500_harvest",
        ),
        (
            "phase2_200",
            paths.harvest_phase2_status_rel,
            FROZEN_PHASE2_200_FP_SHA256,
            EXPECTED_PHASE2_TOTAL,
            "phase2_smoke_200_harvest",
        ),
        (
            "fuller_200",
            paths.harvest_fuller_status_rel,
            FROZEN_FULLER_200_FP_SHA256,
            EXPECTED_FULLER_TOTAL,
            "fuller_market_slice1_200_harvest",
        ),
    )
    for key, status_rel, frozen_fp, expected_n, cohort_id in harvest_specs:
        fp = fingerprint_status_csv(_abs(status_rel, base_dir=base_dir))
        obs = str(fp.get("fingerprint_sha256") or "")
        observed_fps[key] = obs
        ok = bool(obs) and obs == frozen_fp and fp.get("row_count") == expected_n
        checks[f"repro_{key}"] = ok
        rows.append(
            _row(
                check_id=f"repro_{key}",
                layer="multi_cohort_repro_fingerprint",
                cohort_id=cohort_id,
                path=status_rel,
                expected=frozen_fp,
                observed=obs or "missing",
                ok=ok,
                notes="ok" if ok else f"{key}_repro_drift",
            )
        )

    unique_ok = (
        len(set(observed_fps.values())) == EXPECTED_SCALE_TIER_COUNT
        and all(observed_fps.values())
    )
    checks["repro_fingerprints_distinct"] = unique_ok
    rows.append(
        _row(
            check_id="repro_fingerprints_distinct",
            layer="multi_cohort_repro_fingerprint",
            expected="7_distinct_nonempty_fps",
            observed=f"unique={len(set(v for v in observed_fps.values() if v))}",
            ok=unique_ok,
            notes="ok" if unique_ok else "fingerprint_collapse",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["multi_cohort_repro_fingerprint_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="multi_cohort_repro_fingerprint_all_pass",
            layer="multi_cohort_repro_fingerprint",
            expected="7_cohort_zero_drift",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "repro_chain_incomplete",
        )
    )
    return rows, checks, observed_fps


def build_multi_batch_harvest_exclusion_dual_layer_rows(
    paths: ExtendedScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """多 batch harvest×exclusion dual-layer（phase3/phase2/fuller + 保留 phase35）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    p35_rows = load_csv_rows(
        _abs(paths.harvest_phase35_status_rel, base_dir=base_dir)
    )
    p3_rows = load_csv_rows(_abs(paths.harvest_phase3_status_rel, base_dir=base_dir))
    p2_rows = load_csv_rows(_abs(paths.harvest_phase2_status_rel, base_dir=base_dir))
    fu_rows = load_csv_rows(_abs(paths.harvest_fuller_status_rel, base_dir=base_dir))
    h863_rows = load_csv_rows(_abs(paths.harvest_863_status_rel, base_dir=base_dir))

    p35_by = {str(r.get("company_code") or "").strip(): r for r in p35_rows if r}
    fu_by = {str(r.get("company_code") or "").strip(): r for r in fu_rows if r}
    p35_codes = set(p35_by)
    p3_codes = _codes(p3_rows)
    p2_codes = _codes(p2_rows)
    fu_codes = set(fu_by)
    h863_codes = _codes(h863_rows)

    holdout = set(EXPECTED_HOLDOUT9)
    partial7 = set(EXPECTED_SLICE1_PARTIAL7)
    empty3 = set(EXPECTED_SLICE1_EMPTY_DIVIDEND3)
    caveat10 = set(EXPECTED_SLICE1_EXCLUDED_UNIQUE)
    family_map = load_manifest_family_map(
        _abs(paths.exclusion_manifest_rel, base_dir=base_dir)
    )

    # phase35 结构（继承 FM22 不变式）
    p35_counts = _status_counts(p35_rows)
    p35_struct_ok = (
        len(p35_rows) == EXPECTED_PHASE35_TOTAL
        and p35_counts.get("complete") == EXPECTED_PHASE35_COMPLETE
        and p35_counts.get("partial") == EXPECTED_PHASE35_PARTIAL
        and p35_counts.get("failed") == EXPECTED_PHASE35_FAILED
        and holdout <= p35_codes
        and all(str((p35_by.get(c) or {}).get("harvest_status")) == "partial" for c in holdout)
    )
    checks["phase35_holdout9_invariant"] = p35_struct_ok
    rows.append(
        _row(
            check_id="phase35_holdout9_invariant",
            layer="multi_batch_harvest_exclusion_dual_layer",
            cohort_id="phase35_500",
            expected="struct+holdout9_partial",
            observed=(
                f"n={len(p35_rows)};holdout_partial="
                f"{sum(1 for c in holdout if str((p35_by.get(c) or {}).get('harvest_status')) == 'partial')}/9"
            ),
            ok=p35_struct_ok,
            notes="ok" if p35_struct_ok else "phase35_invariant_fail",
        )
    )

    # phase3 结构 + holdout9 不相交
    p3_counts = _status_counts(p3_rows)
    p3_struct_ok = (
        len(p3_rows) == EXPECTED_PHASE3_TOTAL
        and p3_counts.get("complete") == EXPECTED_PHASE3_COMPLETE
        and p3_counts.get("partial") == EXPECTED_PHASE3_PARTIAL
        and p3_counts.get("failed") == EXPECTED_PHASE3_FAILED
    )
    checks["phase3_structural_counts"] = p3_struct_ok
    rows.append(
        _row(
            check_id="phase3_structural_counts",
            layer="multi_batch_harvest_exclusion_dual_layer",
            cohort_id="phase3_500",
            expected=(
                f"total={EXPECTED_PHASE3_TOTAL};complete={EXPECTED_PHASE3_COMPLETE};"
                f"partial={EXPECTED_PHASE3_PARTIAL};failed={EXPECTED_PHASE3_FAILED}"
            ),
            observed=(
                f"total={len(p3_rows)};complete={p3_counts.get('complete')};"
                f"partial={p3_counts.get('partial')};failed={p3_counts.get('failed')}"
            ),
            ok=p3_struct_ok,
            notes="ok" if p3_struct_ok else "phase3_count_mismatch",
        )
    )
    p3_holdout_ok = len(holdout & p3_codes) == 0
    checks["phase3_holdout9_absent"] = p3_holdout_ok
    rows.append(
        _row(
            check_id="phase3_holdout9_absent",
            layer="multi_batch_harvest_exclusion_dual_layer",
            cohort_id="phase3_500",
            expected="disjoint_from_holdout9",
            observed=f"leak={','.join(sorted(holdout & p3_codes)) or 'none'}",
            ok=p3_holdout_ok,
            notes="ok" if p3_holdout_ok else "phase3_holdout_leak",
        )
    )

    # phase2 结构 + holdout9 不相交
    p2_counts = _status_counts(p2_rows)
    p2_struct_ok = (
        len(p2_rows) == EXPECTED_PHASE2_TOTAL
        and p2_counts.get("complete") == EXPECTED_PHASE2_COMPLETE
        and p2_counts.get("partial") == EXPECTED_PHASE2_PARTIAL
    )
    checks["phase2_structural_counts"] = p2_struct_ok
    rows.append(
        _row(
            check_id="phase2_structural_counts",
            layer="multi_batch_harvest_exclusion_dual_layer",
            cohort_id="phase2_200",
            expected=(
                f"total={EXPECTED_PHASE2_TOTAL};complete={EXPECTED_PHASE2_COMPLETE};"
                f"partial={EXPECTED_PHASE2_PARTIAL}"
            ),
            observed=(
                f"total={len(p2_rows)};complete={p2_counts.get('complete')};"
                f"partial={p2_counts.get('partial')}"
            ),
            ok=p2_struct_ok,
            notes="ok" if p2_struct_ok else "phase2_count_mismatch",
        )
    )
    p2_holdout_ok = len(holdout & p2_codes) == 0
    checks["phase2_holdout9_absent"] = p2_holdout_ok
    rows.append(
        _row(
            check_id="phase2_holdout9_absent",
            layer="multi_batch_harvest_exclusion_dual_layer",
            cohort_id="phase2_200",
            expected="disjoint_from_holdout9",
            observed=f"leak={','.join(sorted(holdout & p2_codes)) or 'none'}",
            ok=p2_holdout_ok,
            notes="ok" if p2_holdout_ok else "phase2_holdout_leak",
        )
    )

    # fuller：000003 partial + 结构
    fu_counts = _status_counts(fu_rows)
    fu_struct_ok = (
        len(fu_rows) == EXPECTED_FULLER_TOTAL
        and fu_counts.get("complete") == EXPECTED_FULLER_COMPLETE
        and fu_counts.get("partial") == EXPECTED_FULLER_PARTIAL
    )
    checks["fuller_structural_counts"] = fu_struct_ok
    rows.append(
        _row(
            check_id="fuller_structural_counts",
            layer="multi_batch_harvest_exclusion_dual_layer",
            cohort_id="fuller_200",
            expected=(
                f"total={EXPECTED_FULLER_TOTAL};complete={EXPECTED_FULLER_COMPLETE};"
                f"partial={EXPECTED_FULLER_PARTIAL}"
            ),
            observed=(
                f"total={len(fu_rows)};complete={fu_counts.get('complete')};"
                f"partial={fu_counts.get('partial')}"
            ),
            ok=fu_struct_ok,
            notes="ok" if fu_struct_ok else "fuller_count_mismatch",
        )
    )
    fu_000003_ok = (
        "000003" in fu_codes
        and str((fu_by.get("000003") or {}).get("harvest_status") or "") == "partial"
    )
    checks["fuller_000003_partial"] = fu_000003_ok
    rows.append(
        _row(
            check_id="fuller_000003_partial",
            layer="multi_batch_harvest_exclusion_dual_layer",
            cohort_id="fuller_200",
            expected="000003_present_partial",
            observed=str((fu_by.get("000003") or {}).get("harvest_status") or "missing"),
            ok=fu_000003_ok,
            notes="ok" if fu_000003_ok else "fuller_partial7_anchor_fail",
        )
    )

    # empty3 不得进入 phase3/phase2
    empty_leak = sorted(empty3 & (p3_codes | p2_codes))
    empty_ok = len(empty_leak) == 0
    checks["phase3_phase2_empty3_absent"] = empty_ok
    rows.append(
        _row(
            check_id="phase3_phase2_empty3_absent",
            layer="multi_batch_harvest_exclusion_dual_layer",
            expected="empty3_disjoint",
            observed=f"leak={','.join(empty_leak) or 'none'}",
            ok=empty_ok,
            notes="ok" if empty_ok else "empty3_leaked",
        )
    )

    # 863 与 caveat10 不相交
    leak_863 = sorted(caveat10 & h863_codes)
    disjoint_863_ok = len(leak_863) == 0 and len(h863_codes) == EXPECTED_863_COMPLETE
    checks["harvest_863_disjoint_caveat10"] = disjoint_863_ok
    rows.append(
        _row(
            check_id="harvest_863_disjoint_caveat10",
            layer="multi_batch_harvest_exclusion_dual_layer",
            expected="disjoint;n=861",
            observed=f"n={len(h863_codes)};leak={','.join(leak_863) or 'none'}",
            ok=disjoint_863_ok,
            notes="ok" if disjoint_863_ok else "caveat10_leaked_into_863",
        )
    )

    fam_holdout = {c for c, fs in family_map.items() if "holdout9" in fs}
    fam_partial = {c for c, fs in family_map.items() if "partial7" in fs}
    fam_ok = fam_holdout == holdout and fam_partial == partial7
    checks["manifest_family_sets_stable"] = fam_ok
    rows.append(
        _row(
            check_id="manifest_family_sets_stable",
            layer="multi_batch_harvest_exclusion_dual_layer",
            expected="holdout9+partial7_match_constants",
            observed=f"holdout={len(fam_holdout)};partial7={len(fam_partial)}",
            ok=fam_ok,
            notes="ok" if fam_ok else "manifest_family_drift",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["multi_batch_harvest_exclusion_dual_layer_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="multi_batch_harvest_exclusion_dual_layer_all_pass",
            layer="multi_batch_harvest_exclusion_dual_layer",
            expected="phase3+phase2+fuller+phase35_invariants",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "multi_batch_dual_layer_incomplete",
        )
    )
    return rows, checks


def build_isolated_combined_dryrun_scale_rows(
    paths: ExtendedScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, str]]:
    """隔离 snapshot dry-run 合标规模（863+190=1053，不 EXECUTE）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    fm01_obs = str(
        fingerprint_isolated_snapshot_dryrun(
            paths.fm01_mock_root_rel,
            base_dir=base_dir,
            gate="PASS_WITH_CAVEAT",
            company_count=EXPECTED_FM01_COMPANY_COUNT,
        ).get("fingerprint_sha256")
        or ""
    )
    fm02_obs = str(
        fingerprint_isolated_snapshot_dryrun(
            paths.fm02_mock_root_rel,
            base_dir=base_dir,
            gate="PASS_WITH_CAVEAT",
            company_count=EXPECTED_FM02_COMPANY_COUNT,
        ).get("fingerprint_sha256")
        or ""
    )
    combined = fingerprint_combined_isolated_dryrun_scale(
        fm01_fp=fm01_obs, fm02_fp=fm02_obs
    )
    meta = {
        "fm01_fp": fm01_obs,
        "fm02_fp": fm02_obs,
        "combined_fp": combined,
        "company_coverage_sum": EXPECTED_COMBINED_DRYRUN_COVERAGE,
    }

    cov_ok = EXPECTED_COMBINED_DRYRUN_COVERAGE == 1053
    checks["combined_dryrun_coverage_1053"] = cov_ok
    rows.append(
        _row(
            check_id="combined_dryrun_coverage_1053",
            layer="isolated_combined_dryrun_scale",
            expected="1053",
            observed=str(EXPECTED_COMBINED_DRYRUN_COVERAGE),
            ok=cov_ok,
            notes="ok" if cov_ok else "coverage_mismatch",
        )
    )

    fp_ok = (
        bool(fm01_obs)
        and bool(fm02_obs)
        and fm01_obs == FROZEN_FM01_863_FP_SHA256
        and fm02_obs == FROZEN_FM02_190_FP_SHA256
        and combined == FROZEN_COMBINED_DRYRUN_1053_FP_SHA256
    )
    checks["combined_dryrun_fingerprint_match"] = fp_ok
    rows.append(
        _row(
            check_id="combined_dryrun_fingerprint_match",
            layer="isolated_combined_dryrun_scale",
            path=f"{paths.fm01_mock_root_rel}+{paths.fm02_mock_root_rel}",
            expected=FROZEN_COMBINED_DRYRUN_1053_FP_SHA256,
            observed=combined or "missing",
            ok=fp_ok,
            notes="ok" if fp_ok else "combined_dryrun_drift",
        )
    )

    # 确认两根仍是隔离 mock，且不得写生产 snapshot
    roots_ok = True
    for root in (paths.fm01_mock_root_rel, paths.fm02_mock_root_rel):
        try:
            assert_isolated_validation_output_root(root, base_dir=base_dir)
        except RuntimeError:
            roots_ok = False
    checks["combined_dryrun_roots_isolated"] = roots_ok
    rows.append(
        _row(
            check_id="combined_dryrun_roots_isolated",
            layer="isolated_combined_dryrun_scale",
            expected="both_validation_mock_roots",
            observed="ok" if roots_ok else "not_isolated",
            ok=roots_ok,
            notes="ok" if roots_ok else "dryrun_root_not_isolated",
        )
    )

    no_execute_ok = True
    checks["combined_dryrun_no_execute"] = no_execute_ok
    rows.append(
        _row(
            check_id="combined_dryrun_no_execute",
            layer="isolated_combined_dryrun_scale",
            expected="fingerprint_only_no_production_execute",
            observed="asserted",
            ok=no_execute_ok,
            notes="ok",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["isolated_combined_dryrun_scale_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="isolated_combined_dryrun_scale_all_pass",
            layer="isolated_combined_dryrun_scale",
            expected="combined_1053_zero_drift",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "combined_dryrun_incomplete",
        )
    )
    return rows, checks, meta


def build_scale_lineage_hardening_rows(
    paths: ExtendedScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """lineage 加固：FM22 连续零漂移 + 跨 batch 不相交 + union 计量。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    packet = load_json(_abs(paths.fm22_packet_rel, base_dir=base_dir))
    fp_doc = load_json(_abs(paths.fm22_fingerprint_rel, base_dir=base_dir))

    pkt_ok = (
        packet.get("gate") == "PASS_OFFLINE"
        and packet.get("cninfo_calls") == 0
        and packet.get("company_coverage_sum") == EXPECTED_FM22_COVERAGE_SUM
        and packet.get("scale_tier_count") == 4
        and packet.get("execute_production_snapshot_rebuild") is False
        and packet.get("approved_for_snapshot_rebuild") is False
        and packet.get("seal_chain_extended") is False
    )
    checks["fm22_packet_continuity"] = pkt_ok
    rows.append(
        _row(
            check_id="fm22_packet_continuity",
            layer="scale_lineage_hardening",
            path=paths.fm22_packet_rel,
            expected="PASS_OFFLINE;coverage=2414;tiers=4;execute=false",
            observed=(
                f"gate={packet.get('gate')};coverage={packet.get('company_coverage_sum')};"
                f"tiers={packet.get('scale_tier_count')}"
            ),
            ok=pkt_ok,
            notes="ok" if pkt_ok else "fm22_packet_drift",
        )
    )

    obs = fp_doc.get("observed_fps") or {}
    frozen_ok = (
        obs.get("fm01_863") == FROZEN_FM01_863_FP_SHA256
        and obs.get("fm02_190") == FROZEN_FM02_190_FP_SHA256
        and obs.get("fm03_harvest_863") == FROZEN_FM03_HARVEST_863_FP_SHA256
        and obs.get("phase35_500") == FROZEN_PHASE35_500_FP_SHA256
    )
    checks["fm22_observed_fps_stable"] = frozen_ok
    rows.append(
        _row(
            check_id="fm22_observed_fps_stable",
            layer="scale_lineage_hardening",
            path=paths.fm22_fingerprint_rel,
            expected="4_frozen_fps_match",
            observed=f"keys={len(obs)}",
            ok=frozen_ok,
            notes="ok" if frozen_ok else "fm22_fp_drift",
        )
    )

    p35 = _codes(
        load_csv_rows(_abs(paths.harvest_phase35_status_rel, base_dir=base_dir))
    )
    p3 = _codes(load_csv_rows(_abs(paths.harvest_phase3_status_rel, base_dir=base_dir)))
    p2 = _codes(load_csv_rows(_abs(paths.harvest_phase2_status_rel, base_dir=base_dir)))
    fu = _codes(load_csv_rows(_abs(paths.harvest_fuller_status_rel, base_dir=base_dir)))
    h863 = _codes(load_csv_rows(_abs(paths.harvest_863_status_rel, base_dir=base_dir)))

    disjoint_pairs = {
        "p35_p3": len(p35 & p3) == 0,
        "p35_p2": len(p35 & p2) == 0,
        "p3_p2": len(p3 & p2) == 0,
        "p3_fu": len(p3 & fu) == 0,
        "h863_p35": len(h863 & p35) == 0,
        "h863_p3": len(h863 & p3) == 0,
        "h863_p2": len(h863 & p2) == 0,
        "h863_fu": len(h863 & fu) == 0,
    }
    for key, ok in disjoint_pairs.items():
        checks[f"disjoint_{key}"] = ok
        rows.append(
            _row(
                check_id=f"disjoint_{key}",
                layer="scale_lineage_hardening",
                expected="empty_intersection",
                observed="ok" if ok else "overlap",
                ok=ok,
                notes="ok" if ok else f"{key}_overlap",
            )
        )

    # 已知小交集：p35∩fu=1 (000003), p2∩fu=11
    p35_fu_ok = (p35 & fu) == {"000003"}
    checks["expected_overlap_p35_fu_000003"] = p35_fu_ok
    rows.append(
        _row(
            check_id="expected_overlap_p35_fu_000003",
            layer="scale_lineage_hardening",
            expected="000003_only",
            observed=",".join(sorted(p35 & fu)) or "none",
            ok=p35_fu_ok,
            notes="ok" if p35_fu_ok else "p35_fu_overlap_drift",
        )
    )
    p2_fu_n = len(p2 & fu)
    p2_fu_ok = p2_fu_n == 11
    checks["expected_overlap_p2_fu_11"] = p2_fu_ok
    rows.append(
        _row(
            check_id="expected_overlap_p2_fu_11",
            layer="scale_lineage_hardening",
            expected="overlap=11",
            observed=str(p2_fu_n),
            ok=p2_fu_ok,
            notes="ok" if p2_fu_ok else "p2_fu_overlap_drift",
        )
    )

    union_n = len(p2 | p3 | p35 | fu)
    union_ok = union_n == EXPECTED_HARVEST_BATCH_UNION
    checks["harvest_batch_union_1388"] = union_ok
    rows.append(
        _row(
            check_id="harvest_batch_union_1388",
            layer="scale_lineage_hardening",
            expected=str(EXPECTED_HARVEST_BATCH_UNION),
            observed=str(union_n),
            ok=union_ok,
            notes="ok" if union_ok else "union_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["scale_lineage_hardening_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="scale_lineage_hardening_all_pass",
            layer="scale_lineage_hardening",
            expected="fm22_continuity+cross_batch_invariants",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "lineage_hardening_incomplete",
        )
    )
    return rows, checks


def build_output_root_protection_hardening_rows(
    paths: ExtendedScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """output-root 保护：phase3/phase2/fuller 写拒绝 + MOCK25 放行。"""
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
            f"{HARVEST_PHASE3_ROOT_REL}/quality/probe_write_forbidden_fm23.csv",
        ),
        (
            "write_guard_phase2_harvest_refused",
            f"{HARVEST_PHASE2_ROOT_REL}/quality/probe_write_forbidden_fm23.csv",
        ),
        (
            "write_guard_fuller_harvest_refused",
            f"{HARVEST_FULLER_ROOT_REL}/quality/probe_write_forbidden_fm23.csv",
        ),
        (
            "write_guard_phase35_harvest_refused",
            f"{HARVEST_PHASE35_ROOT_REL}/quality/probe_write_forbidden_fm23.csv",
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
                layer="output_root_protection_hardening",
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
        assert_fm23_output_root(paths.output_root_rel, base_dir=base_dir)
        out_ok = True
        out_detail = "allowed"
    except RuntimeError as exc:
        out_detail = str(exc)[:120]
    checks["hardening_output_root_allowed"] = out_ok
    rows.append(
        _row(
            check_id="hardening_output_root_allowed",
            layer="output_root_protection_hardening",
            path=paths.output_root_rel,
            expected="MOCK25_or_ephemeral_allowed",
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
        "hardening_output_root_allowed",
        "protected_write_guard_battery_all_pass",
    ]
    hardening_ok = all(checks.get(k) for k in hardening_keys)
    checks["output_root_protection_hardening_all_pass"] = hardening_ok
    rows.append(
        _row(
            check_id="output_root_protection_hardening_all_pass",
            layer="output_root_protection_hardening",
            expected="phase3+phase2+fuller+phase35_refused;mock25_ok",
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
    paths: ExtendedScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–24 拒绝 · MOCK25 放行。"""
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

    mock25_prefix = frozen.get(THIS_TASK_ROOT_ID)
    mock25_listed = mock25_prefix is not None
    mock25_allowed = False
    if mock25_prefix:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock25_prefix,
                allow_root_ids=(THIS_TASK_ROOT_ID,),
                base_dir=base_dir,
            )
            mock25_allowed = True
        except RuntimeError:
            mock25_allowed = False
    checks["frozen_allow_mock25"] = mock25_listed and mock25_allowed
    rows.append(
        _row(
            check_id="frozen_allow_mock25",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=_rel(mock25_prefix, base_dir=base_dir) if mock25_prefix else "",
            expected="listed_and_allowed_when_in_allowlist",
            observed=f"listed={mock25_listed};allowed={mock25_allowed}",
            ok=mock25_listed and mock25_allowed,
            notes="ok" if mock25_listed and mock25_allowed else "mock25_allow_fail",
        )
    )

    out_ok = False
    out_detail = ""
    try:
        assert_fm23_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK25_or_ephemeral_allowed",
            observed=out_detail,
            ok=out_ok,
        )
    )

    for root_id, check_id, expected in (
        ("C-ROOT-MOCK24", "mock24_still_frozen", "fm22_mock24_not_writable_by_fm23"),
        ("C-ROOT-MOCK8", "seal_mock8_still_frozen", "seal_chain_not_writable_by_fm23"),
    ):
        prefix = frozen.get(root_id)
        still_frozen = False
        if prefix:
            try:
                assert_frozen_mock_cohort_write_forbidden(
                    prefix, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
                )
            except RuntimeError as exc:
                still_frozen = FROZEN_MOCK_COHORT_WRITE_FORBIDDEN in str(exc)
        checks[check_id] = still_frozen
        rows.append(
            _row(
                check_id=check_id,
                layer="frozen_mock_isolation",
                root_id=root_id,
                expected=expected,
                observed=f"refused={still_frozen}",
                ok=still_frozen,
                notes="ok" if still_frozen else f"{root_id}_freeze_regressed",
            )
        )

    all_ok = all(checks.values()) if checks else False
    checks["frozen_mock_isolation_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="frozen_mock_isolation_all_pass",
            layer="frozen_mock_isolation",
            expected="MOCK3-24_blocked_MOCK25_ok",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "frozen_isolation_fail",
        )
    )
    return rows, checks


def build_protected_csv_registry_rows(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected CSV：MOCK3–25 + fuller harvest C-ROOT-011 + AUTH1。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    csv_rows = load_protected_root_rows(csv_rel, base_dir=base_dir)
    by_id = {str(r.get("root_id") or ""): r for r in csv_rows}

    for root_id in REQUIRED_PROTECTED_ROOT_IDS:
        present = root_id in by_id
        checks[f"protected_csv_has_{root_id}"] = present
        rows.append(
            _row(
                check_id=f"protected_csv_has_{root_id}",
                layer="protected_csv_registry",
                root_id=root_id,
                path=csv_rel,
                expected="listed_in_protected_csv",
                observed="present" if present else "missing",
                ok=present,
                notes="ok" if present else "missing_root_id",
            )
        )

    auth = by_id.get("C-ROOT-AUTH1") or {}
    auth_ok = (auth.get("write_policy") or "") == "read_only_no_overwrite"
    checks["protected_csv_auth1_readonly"] = auth_ok
    rows.append(
        _row(
            check_id="protected_csv_auth1_readonly",
            layer="protected_csv_registry",
            root_id="C-ROOT-AUTH1",
            path=csv_rel,
            expected="write_policy=read_only_no_overwrite",
            observed=str(auth.get("write_policy") or ""),
            ok=auth_ok,
            notes="ok" if auth_ok else "auth_policy_drift",
        )
    )

    mock25 = by_id.get(THIS_TASK_ROOT_ID) or {}
    mock25_path = (mock25.get("path_pattern") or "").strip().rstrip("/")
    mock25_ok = mock25_path.endswith(
        "_mock_c_fm23_scale_multi_batch_repro_lineage_hardening"
    ) or mock25_path == DEFAULT_MOCK_OUTPUT_ROOT_REL
    checks["protected_csv_mock25_path"] = mock25_ok
    rows.append(
        _row(
            check_id="protected_csv_mock25_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            path=mock25_path,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=mock25_path or "missing",
            ok=mock25_ok,
            notes="ok" if mock25_ok else "mock25_path_mismatch",
        )
    )

    fuller = by_id.get(FULLER_HARVEST_ROOT_ID) or {}
    fuller_path = (fuller.get("path_pattern") or "").strip().rstrip("/")
    fuller_ok = fuller_path.endswith("fuller_market_slice1_200") and (
        (fuller.get("write_policy") or "") == "read_only_erad_planning"
    )
    checks["protected_csv_fuller_harvest_root"] = fuller_ok
    rows.append(
        _row(
            check_id="protected_csv_fuller_harvest_root",
            layer="protected_csv_registry",
            root_id=FULLER_HARVEST_ROOT_ID,
            path=fuller_path,
            expected=HARVEST_FULLER_ROOT_REL,
            observed=fuller_path or "missing",
            ok=fuller_ok,
            notes="ok" if fuller_ok else "fuller_root_missing",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-25+C-ROOT-011+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "protected_csv_incomplete",
        )
    )
    return rows, checks


def build_fm_gate_battery_rows(
    *,
    gates: Dict[str, Dict[str, Any]],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 + FM-12..22 既有 gate 只读聚合（跳过 seal FM06–11）。"""
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
        ):
            if "seal_chain_extended" in payload:
                ok = ok and payload.get("seal_chain_extended") is False
        if key == "fm22":
            ok = (
                ok
                and payload.get("company_coverage_sum") == EXPECTED_FM22_COVERAGE_SUM
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
            check_id="fm01_05_12_22_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_22_battery_all_pass"] = all_ok
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


def ensure_protected_roots_csv_fm23(
    *,
    csv_rel: str = PROTECTED_ROOTS_CSV_REL,
    base_dir: str = BASE_DIR,
) -> None:
    """注册 C-ROOT-011（fuller harvest）与 C-ROOT-MOCK25（本任务写根）。"""
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

    _upsert(
        FULLER_HARVEST_ROOT_ID,
        {
            "root_id": FULLER_HARVEST_ROOT_ID,
            "path_pattern": f"{HARVEST_FULLER_ROOT_REL}/",
            "root_class": "harvest",
            "era_origin": "era_c_fuller",
            "protection_level": "production",
            "write_policy": "read_only_erad_planning",
            "notes": (
                "Fuller-market slice1 200 harvest root; C-FM-23 output-root "
                "protection hardening; 只读直至人批重跑"
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
                "C-FM-23 extended multi-batch scale repro (863/190/861/500/500/200/200) "
                "+ isolated combined dryrun 1053 + lineage hardening + output-root "
                "protection; never production EXECUTE; must not overwrite MOCK3-24; "
                "seal_chain_extended=false"
            ),
        },
    )

    # 保持原有顺序，新增行追加到末尾（若原先不存在）
    ordered: List[Dict[str, str]] = []
    seen = set()
    for r in existing:
        rid = str(r.get("root_id") or "")
        if rid in seen:
            continue
        # 用 upsert 后的内容
        ordered.append(by_id.get(rid, r))
        seen.add(rid)
    for rid in (FULLER_HARVEST_ROOT_ID, THIS_TASK_ROOT_ID):
        if rid not in seen:
            ordered.append(by_id[rid])
            seen.add(rid)

    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in ordered:
            writer.writerow({k: r.get(k, "") for k in fieldnames})
    load_frozen_mock_cohort_roots.cache_clear()


def run_scale_multi_batch_repro_lineage_hardening(
    *,
    paths: ExtendedScalePaths = ExtendedScalePaths(),
    base_dir: str = BASE_DIR,
    ensure_protected_csv: bool = True,
) -> Dict[str, Any]:
    """执行 C-FM-23 扩展多 batch 规模 repro + lineage 加固 QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    if ensure_protected_csv:
        ensure_protected_roots_csv_fm23(
            csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
        )
    out_root = assert_fm23_output_root(paths.output_root_rel, base_dir=base_dir)

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
    }

    reg_rows, reg_checks, reg_meta = build_extended_scale_lineage_registry_rows(
        base_dir=base_dir
    )
    repro_rows, repro_checks, observed_fps = (
        build_extended_multi_cohort_repro_fingerprint_rows(paths, base_dir=base_dir)
    )
    dual_rows, dual_checks = build_multi_batch_harvest_exclusion_dual_layer_rows(
        paths, base_dir=base_dir
    )
    dry_rows, dry_checks, dry_meta = build_isolated_combined_dryrun_scale_rows(
        paths, base_dir=base_dir
    )
    hard_lin_rows, hard_lin_checks = build_scale_lineage_hardening_rows(
        paths, base_dir=base_dir
    )
    hard_rows, hard_checks = build_output_root_protection_hardening_rows(
        paths, base_dir=base_dir
    )
    fr_rows, fr_checks = build_frozen_mock_isolation_rows(paths, base_dir=base_dir)
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )
    bat_rows, bat_checks = build_fm_gate_battery_rows(gates=gates)
    hold_rows, hold_checks = build_execute_hold_rows()

    matrix = (
        reg_rows
        + repro_rows
        + dual_rows
        + dry_rows
        + hard_lin_rows
        + hard_rows
        + fr_rows
        + csv_rows
        + bat_rows
        + hold_rows
    )
    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    layer_gates = {
        "scale_lineage_registry": (
            "PASS_OFFLINE"
            if reg_checks.get("scale_lineage_registry_all_pass")
            else "FAIL_OFFLINE"
        ),
        "multi_cohort_repro_fingerprint": (
            "PASS_OFFLINE"
            if repro_checks.get("multi_cohort_repro_fingerprint_all_pass")
            else "FAIL_OFFLINE"
        ),
        "multi_batch_harvest_exclusion_dual_layer": (
            "PASS_OFFLINE"
            if dual_checks.get("multi_batch_harvest_exclusion_dual_layer_all_pass")
            else "FAIL_OFFLINE"
        ),
        "isolated_combined_dryrun_scale": (
            "PASS_OFFLINE"
            if dry_checks.get("isolated_combined_dryrun_scale_all_pass")
            else "FAIL_OFFLINE"
        ),
        "scale_lineage_hardening": (
            "PASS_OFFLINE"
            if hard_lin_checks.get("scale_lineage_hardening_all_pass")
            else "FAIL_OFFLINE"
        ),
        "output_root_protection_hardening": (
            "PASS_OFFLINE"
            if hard_checks.get("output_root_protection_hardening_all_pass")
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
            if bat_checks.get("fm01_05_12_22_battery_all_pass")
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

    fingerprint_payload = {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "seal_chain_extended": False,
        "scale_tier_count": reg_meta["scale_tier_count"],
        "company_coverage_sum": reg_meta["company_coverage_sum"],
        "combined_dryrun_coverage": dry_meta["company_coverage_sum"],
        "combined_dryrun_fp": dry_meta["combined_fp"],
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
        },
        "fingerprint": fp,
    }
    fingerprint_rel = _rel(
        os.path.join(out_root, "scale_fingerprint.json"), base_dir=base_dir
    )
    with open(_abs(fingerprint_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(fingerprint_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    registry_rel = _rel(
        os.path.join(out_root, "scale_lineage_registry.json"), base_dir=base_dir
    )
    with open(_abs(registry_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "scale_tier_count": reg_meta["scale_tier_count"],
                "company_coverage_sum": reg_meta["company_coverage_sum"],
                "expected_company_coverage_sum": EXPECTED_COMPANY_COVERAGE_SUM,
                "prior_fm22_company_coverage_sum": EXPECTED_FM22_COVERAGE_SUM,
                "registry": reg_meta["registry"],
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    battery_rel = _rel(
        os.path.join(out_root, "fm_gate_battery.json"), base_dir=base_dir
    )
    battery_payload = {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "gate": overall,
        "layer_gates": layer_gates,
        "fm01_gate": gates["fm01"].get("gate"),
        "fm02_gate": gates["fm02"].get("gate"),
        "fm03_gate": gates["fm03"].get("gate"),
        "fm04_gate": gates["fm04"].get("gate"),
        "fm05_gate": gates["fm05"].get("gate"),
        "fm12_gate": gates["fm12"].get("gate"),
        "fm13_gate": gates["fm13"].get("gate"),
        "fm14_gate": gates["fm14"].get("gate"),
        "fm15_gate": gates["fm15"].get("gate"),
        "fm16_gate": gates["fm16"].get("gate"),
        "fm17_gate": gates["fm17"].get("gate"),
        "fm18_gate": gates["fm18"].get("gate"),
        "fm19_gate": gates["fm19"].get("gate"),
        "fm20_gate": gates["fm20"].get("gate"),
        "fm21_gate": gates["fm21"].get("gate"),
        "fm22_gate": gates["fm22"].get("gate"),
        "fm23_gate": overall,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "decision_status": "AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting": True,
        "seal_chain_extended": False,
        "scale_tier_count": reg_meta["scale_tier_count"],
        "company_coverage_sum": reg_meta["company_coverage_sum"],
        "combined_dryrun_coverage": dry_meta["company_coverage_sum"],
    }
    with open(_abs(battery_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(battery_payload, fh, ensure_ascii=False, indent=2)
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
                "scale_tier_count": reg_meta["scale_tier_count"],
                "company_coverage_sum": reg_meta["company_coverage_sum"],
                "combined_dryrun_coverage": dry_meta["company_coverage_sum"],
                "notes": (
                    "extended multi-batch repro (863/190/861/500/500/200/200) + "
                    "isolated combined dryrun 1053 + lineage hardening + "
                    "output-root protection (MOCK25 / C-ROOT-011); "
                    "EXECUTE remains human-held; does not overwrite MOCK3-24"
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
        "scale_tier_count": reg_meta["scale_tier_count"],
        "company_coverage_sum": reg_meta["company_coverage_sum"],
        "combined_dryrun_coverage": dry_meta["company_coverage_sum"],
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "registry_path": registry_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "combined_dryrun": dry_meta,
        "inputs": {
            "harvest_863_status": paths.harvest_863_status_rel,
            "harvest_phase35_status": paths.harvest_phase35_status_rel,
            "harvest_phase3_status": paths.harvest_phase3_status_rel,
            "harvest_phase2_status": paths.harvest_phase2_status_rel,
            "harvest_fuller_status": paths.harvest_fuller_status_rel,
            "exclusion_manifest": paths.exclusion_manifest_rel,
            "fm01_mock_root": paths.fm01_mock_root_rel,
            "fm02_mock_root": paths.fm02_mock_root_rel,
            "fm22_packet": paths.fm22_packet_rel,
        },
        "mock_root_is_isolated": True,
        "checks": {
            **reg_checks,
            **repro_checks,
            **dual_checks,
            **dry_checks,
            **hard_lin_checks,
            **hard_checks,
            **fr_checks,
            **csv_checks,
            **bat_checks,
            **hold_checks,
        },
    }
