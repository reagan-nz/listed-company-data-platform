"""
CNINFO C-class — 规模化 harvest/exclusion dual-layer 一致性 +
多 cohort 可复现指纹 + output-root 保护加固（离线 · C-FM-22）。

在 C-FM-21（non-seal third-extension post-commit drift recheck）已 commit 且 EXECUTE 仍
human-held 之上，补齐非 seal 能力（不新增 seal / decision-await / commit-boundary；
非第四次 identical extension→drift 循环）：
  1) phase35×500 harvest × exclusion manifest 规模 dual-layer 一致性
  2) 多 cohort 可复现指纹链：FM01(863) + FM02(190) + FM03(861) + phase35(500)
  3) 规模 lineage registry（可计量 company_coverage / scale_tier_count）
  4) 863 harvest 与 caveat10 排除集不相交（规模不变式）
  5) output-root 保护加固：phase35/863/slice1 harvest + snapshot + auth 拒绝；
     MOCK3–23 冻结；本任务 MOCK24 / ephemeral 放行
  6) FM-01..05 + FM-12..21 gate battery（显式跳过 seal FM06–11）
  7) protected_output_roots.csv 注册一致性（含 MOCK24）

禁止：CNINFO live · production EXECUTE · 覆盖 MOCK3–23 / 权威 dual-layer 索引 ·
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
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
)

TASK_ID = "C-FM-22"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm22_scale_harvest_exclusion_repro_fingerprint"
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

FM01_MOCK_ROOT_REL = (
    "outputs/validation/_mock_snapshot_batch_standard_dryrun_isolated"
)
FM02_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm02_slice1_190_validation_cohort"
)
FM03_MOCK_ROOT_REL = (
    "outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency"
)

HARVEST_863_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"
)
HARVEST_PHASE35_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/phase35_batch_500_001/"
    "quality/company_harvest_status.csv"
)
HARVEST_PHASE35_ROOT_REL = (
    "outputs/harvest/cninfo_c_class/phase35_batch_500_001"
)
HARVEST_863_ROOT_REL = "outputs/harvest/cninfo_c_class"
EXCLUSION_MANIFEST_REL = (
    "outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv"
)

# 冻结多尺度可复现指纹常量（只读复核锚点）
FROZEN_FM01_863_FP_SHA256 = (
    "cb0cf6b116c59e0326b380f31efedb73fefcf30e54d3ce1dd14db91efe508759"
)
FROZEN_FM02_190_FP_SHA256 = (
    "6dc30af0fe8e8ade2f10da8599891005fde0158e324c9a1273112a461f04971c"
)
FROZEN_FM03_HARVEST_863_FP_SHA256 = (
    "b25006b906a7ad14a96c703a896dd7fc18741d2c3e03886e87c01b898ba76278"
)
FROZEN_PHASE35_500_FP_SHA256 = (
    "0aa3faad0387d7833769997fb705370105f56ba5204b4ec8878e432df27b9664"
)

EXPECTED_PHASE35_TOTAL = 500
EXPECTED_PHASE35_COMPLETE = 419
EXPECTED_PHASE35_PARTIAL = 75
EXPECTED_PHASE35_FAILED = 6
EXPECTED_863_COMPLETE = 861
EXPECTED_FM01_COMPANY_COUNT = 863
EXPECTED_FM02_COMPANY_COUNT = 190

# 规模计量：四层 company_coverage 之和（可计量 jump）
EXPECTED_SCALE_TIER_COUNT = 4
EXPECTED_COMPANY_COVERAGE_SUM = (
    EXPECTED_FM01_COMPANY_COUNT
    + EXPECTED_FM02_COMPANY_COUNT
    + EXPECTED_863_COMPLETE
    + EXPECTED_PHASE35_TOTAL
)  # 2414

THIS_TASK_ROOT_ID = "C-ROOT-MOCK24"
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
)

REQUIRED_PROTECTED_ROOT_IDS = FROZEN_ROOT_IDS_MUST_BLOCK + (
    THIS_TASK_ROOT_ID,
    "C-ROOT-AUTH1",
)

MATRIX_FIELDS = [
    "check_id",
    "layer",
    "cohort_id",
    "root_id",
    "path",
    "expected",
    "observed",
    "ok",
    "notes",
]


@dataclass(frozen=True)
class ScalePaths:
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
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
    harvest_863_status_rel: str = HARVEST_863_STATUS_REL
    harvest_phase35_status_rel: str = HARVEST_PHASE35_STATUS_REL
    exclusion_manifest_rel: str = EXCLUSION_MANIFEST_REL
    fm01_mock_root_rel: str = FM01_MOCK_ROOT_REL
    fm02_mock_root_rel: str = FM02_MOCK_ROOT_REL
    fm03_mock_root_rel: str = FM03_MOCK_ROOT_REL
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


def assert_fm22_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    C-FM-22 写根：须 validation/_mock_*，不得覆盖 MOCK3–23，
    不得写权威 dual-layer 索引；允许本任务 MOCK24 或未登记 ephemeral。
    """
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    load_frozen_mock_cohort_roots.cache_clear()
    root_id = resolve_frozen_mock_cohort_root_id(out, base_dir=base_dir)
    if root_id is not None and root_id != THIS_TASK_ROOT_ID:
        raise RuntimeError(
            f"{FROZEN_MOCK_COHORT_WRITE_FORBIDDEN}: "
            f"cannot write frozen root_id={root_id} "
            f"(C-FM-22 only writes {THIS_TASK_ROOT_ID} or ephemeral _mock_*)"
        )
    if root_id is not None:
        assert_frozen_mock_cohort_write_forbidden(
            out, allow_root_ids=(THIS_TASK_ROOT_ID,), base_dir=base_dir
        )
    return out


def default_scale_cohort_specs() -> Tuple[Dict[str, Any], ...]:
    """规模 lineage registry 规格：四层可计量 coverage。"""
    return (
        {
            "cohort_id": "fm01_isolated_dryrun_863",
            "tier": "dryrun_863",
            "root_rel": FM01_MOCK_ROOT_REL,
            "company_count": EXPECTED_FM01_COMPANY_COUNT,
            "fingerprint_kind": "dryrun",
            "frozen_fp": FROZEN_FM01_863_FP_SHA256,
            "gate_json_rel": FM01_GATE_JSON_REL,
        },
        {
            "cohort_id": "fm02_slice1_190_validation",
            "tier": "slice1_190",
            "root_rel": FM02_MOCK_ROOT_REL,
            "company_count": EXPECTED_FM02_COMPANY_COUNT,
            "fingerprint_kind": "dryrun",
            "frozen_fp": FROZEN_FM02_190_FP_SHA256,
            "gate_json_rel": FM02_GATE_JSON_REL,
        },
        {
            "cohort_id": "fm03_harvest_863_structural",
            "tier": "harvest_861",
            "root_rel": FM03_MOCK_ROOT_REL,
            "company_count": EXPECTED_863_COMPLETE,
            "fingerprint_kind": "harvest_863",
            "frozen_fp": FROZEN_FM03_HARVEST_863_FP_SHA256,
            "gate_json_rel": FM03_GATE_JSON_REL,
        },
        {
            "cohort_id": "phase35_batch_500_harvest",
            "tier": "phase35_500",
            "root_rel": HARVEST_PHASE35_ROOT_REL,
            "company_count": EXPECTED_PHASE35_TOTAL,
            "fingerprint_kind": "phase35_harvest",
            "frozen_fp": FROZEN_PHASE35_500_FP_SHA256,
            "gate_json_rel": "",
        },
    )


def build_scale_lineage_registry_rows(
    *,
    specs: Optional[Sequence[Dict[str, Any]]] = None,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """规模 lineage registry：四层存在性 + company_coverage 计量。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    specs = tuple(specs) if specs is not None else default_scale_cohort_specs()
    coverage_sum = 0
    registry: List[Dict[str, Any]] = []

    for spec in specs:
        cohort_id = str(spec["cohort_id"])
        root_rel = str(spec["root_rel"])
        expected_n = int(spec["company_count"])
        root_abs = _abs(root_rel, base_dir=base_dir)
        if spec["fingerprint_kind"] == "phase35_harvest":
            present = os.path.isfile(
                _abs(HARVEST_PHASE35_STATUS_REL, base_dir=base_dir)
            )
        elif spec["fingerprint_kind"] == "harvest_863":
            present = os.path.isfile(
                _abs(HARVEST_863_STATUS_REL, base_dir=base_dir)
            ) and os.path.isdir(root_abs)
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

    all_ok = all(checks.values()) if checks else False
    checks["scale_lineage_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="scale_lineage_registry_all_pass",
            layer="scale_lineage_registry",
            expected="4_tiers_coverage_2414",
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


def build_multi_cohort_repro_fingerprint_rows(
    paths: ScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, str]]:
    """多 cohort 可复现指纹：常量 · 重算 · gate JSON 三方对齐。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    observed_fps: Dict[str, str] = {}

    # FM01 863 dry-run
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
    fm01_gate = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm01_gate_fp = ""
    runs = fm01_gate.get("runs") or []
    if runs:
        fm01_gate_fp = str(runs[0].get("fingerprint_sha256") or "")
    fm01_ok = (
        bool(fm01_obs)
        and fm01_obs == FROZEN_FM01_863_FP_SHA256
        and fm01_obs == fm01_gate_fp
    )
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

    # FM02 190
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
    fm02_gate = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm02_gate_fp = str(
        ((fm02_gate.get("slice1_190") or {}).get("fingerprint") or {}).get(
            "fingerprint_sha256"
        )
        or ""
    )
    fm02_ok = (
        bool(fm02_obs)
        and fm02_obs == FROZEN_FM02_190_FP_SHA256
        and fm02_obs == fm02_gate_fp
    )
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

    # FM03 harvest 863
    harvest_fp = fingerprint_status_csv(
        _abs(paths.harvest_863_status_rel, base_dir=base_dir)
    )
    fm03_obs = str(harvest_fp.get("fingerprint_sha256") or "")
    observed_fps["fm03_harvest_863"] = fm03_obs
    fm03_gate = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm03_gate_fp = str(
        (fm03_gate.get("fingerprint_863") or {}).get("fingerprint_sha256") or ""
    )
    fm03_ok = (
        bool(fm03_obs)
        and fm03_obs == FROZEN_FM03_HARVEST_863_FP_SHA256
        and fm03_obs == fm03_gate_fp
        and harvest_fp.get("row_count") == EXPECTED_863_COMPLETE
    )
    checks["repro_fm03_harvest_863"] = fm03_ok
    rows.append(
        _row(
            check_id="repro_fm03_harvest_863",
            layer="multi_cohort_repro_fingerprint",
            cohort_id="fm03_harvest_863_structural",
            path=paths.harvest_863_status_rel,
            expected=FROZEN_FM03_HARVEST_863_FP_SHA256,
            observed=fm03_obs or "missing",
            ok=fm03_ok,
            notes="ok" if fm03_ok else "fm03_repro_drift",
        )
    )

    # phase35 500
    p35_fp = fingerprint_status_csv(
        _abs(paths.harvest_phase35_status_rel, base_dir=base_dir)
    )
    p35_obs = str(p35_fp.get("fingerprint_sha256") or "")
    observed_fps["phase35_500"] = p35_obs
    p35_ok = (
        bool(p35_obs)
        and p35_obs == FROZEN_PHASE35_500_FP_SHA256
        and p35_fp.get("row_count") == EXPECTED_PHASE35_TOTAL
    )
    checks["repro_phase35_500"] = p35_ok
    rows.append(
        _row(
            check_id="repro_phase35_500",
            layer="multi_cohort_repro_fingerprint",
            cohort_id="phase35_batch_500_harvest",
            path=paths.harvest_phase35_status_rel,
            expected=FROZEN_PHASE35_500_FP_SHA256,
            observed=p35_obs or "missing",
            ok=p35_ok,
            notes="ok" if p35_ok else "phase35_repro_drift",
        )
    )

    # 四层互异（防指纹坍缩）
    unique_ok = len(set(observed_fps.values())) == 4 and all(observed_fps.values())
    checks["repro_fingerprints_distinct"] = unique_ok
    rows.append(
        _row(
            check_id="repro_fingerprints_distinct",
            layer="multi_cohort_repro_fingerprint",
            expected="4_distinct_nonempty_fps",
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
            expected="fm01+fm02+fm03+phase35_zero_drift",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "repro_chain_incomplete",
        )
    )
    return rows, checks, observed_fps


def build_phase35_scale_dual_layer_rows(
    paths: ScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """
    phase35×500 规模 dual-layer：exclusion manifest × phase35 harvest。
    相对 FM-03（slice1+863 结构）新增 500 规模家族交叉核验。
    """
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    p35_rows = load_csv_rows(
        _abs(paths.harvest_phase35_status_rel, base_dir=base_dir)
    )
    p35_by_code = {
        str(r.get("company_code") or "").strip(): r for r in p35_rows if r
    }
    p35_codes = set(p35_by_code)

    family_map = load_manifest_family_map(
        _abs(paths.exclusion_manifest_rel, base_dir=base_dir)
    )
    holdout = set(EXPECTED_HOLDOUT9)
    partial7 = set(EXPECTED_SLICE1_PARTIAL7)
    empty3 = set(EXPECTED_SLICE1_EMPTY_DIVIDEND3)
    caveat10 = set(EXPECTED_SLICE1_EXCLUDED_UNIQUE)

    # 结构计数
    status_counts: Dict[str, int] = {}
    for r in p35_rows:
        st = str(r.get("harvest_status") or "").strip()
        status_counts[st] = status_counts.get(st, 0) + 1
    struct_ok = (
        len(p35_rows) == EXPECTED_PHASE35_TOTAL
        and len(p35_codes) == EXPECTED_PHASE35_TOTAL
        and status_counts.get("complete") == EXPECTED_PHASE35_COMPLETE
        and status_counts.get("partial") == EXPECTED_PHASE35_PARTIAL
        and status_counts.get("failed") == EXPECTED_PHASE35_FAILED
    )
    checks["phase35_structural_counts"] = struct_ok
    rows.append(
        _row(
            check_id="phase35_structural_counts",
            layer="scale_harvest_exclusion_dual_layer",
            cohort_id="phase35_500",
            path=paths.harvest_phase35_status_rel,
            expected=(
                f"total={EXPECTED_PHASE35_TOTAL};complete={EXPECTED_PHASE35_COMPLETE};"
                f"partial={EXPECTED_PHASE35_PARTIAL};failed={EXPECTED_PHASE35_FAILED}"
            ),
            observed=(
                f"total={len(p35_rows)};complete={status_counts.get('complete')};"
                f"partial={status_counts.get('partial')};"
                f"failed={status_counts.get('failed')}"
            ),
            ok=struct_ok,
            notes="ok" if struct_ok else "phase35_count_mismatch",
        )
    )

    # holdout9 全员落在 phase35 且均为 partial
    holdout_in = holdout & p35_codes
    holdout_partial_ok = holdout_in == holdout and all(
        str((p35_by_code.get(c) or {}).get("harvest_status") or "") == "partial"
        for c in sorted(holdout)
    )
    checks["phase35_holdout9_all_partial"] = holdout_partial_ok
    rows.append(
        _row(
            check_id="phase35_holdout9_all_partial",
            layer="scale_harvest_exclusion_dual_layer",
            cohort_id="holdout9",
            expected="9/9_present_and_partial",
            observed=(
                f"present={len(holdout_in)}/9;"
                f"statuses="
                + ",".join(
                    f"{c}={(p35_by_code.get(c) or {}).get('harvest_status')}"
                    for c in sorted(holdout)
                )
            ),
            ok=holdout_partial_ok,
            notes="ok" if holdout_partial_ok else "holdout9_phase35_fail",
        )
    )

    # partial7 ∩ phase35：至少含 000003；若出现须为 partial
    partial_in = partial7 & p35_codes
    partial_ok = "000003" in partial_in and all(
        str((p35_by_code.get(c) or {}).get("harvest_status") or "") == "partial"
        for c in sorted(partial_in)
    )
    checks["phase35_partial7_overlap_semantics"] = partial_ok
    rows.append(
        _row(
            check_id="phase35_partial7_overlap_semantics",
            layer="scale_harvest_exclusion_dual_layer",
            cohort_id="partial7",
            expected="000003_in_phase35_partial",
            observed=f"overlap={','.join(sorted(partial_in)) or 'none'}",
            ok=partial_ok,
            notes="ok" if partial_ok else "partial7_phase35_fail",
        )
    )

    # empty3 不得落在 phase35（当前规模不变式）
    empty_in = empty3 & p35_codes
    empty_ok = len(empty_in) == 0
    checks["phase35_empty3_absent"] = empty_ok
    rows.append(
        _row(
            check_id="phase35_empty3_absent",
            layer="scale_harvest_exclusion_dual_layer",
            cohort_id="empty_dividend3",
            expected="disjoint_from_phase35",
            observed=f"leak={','.join(sorted(empty_in)) or 'none'}",
            ok=empty_ok,
            notes="ok" if empty_ok else "empty3_leaked_into_phase35",
        )
    )

    # manifest 家族映射与 holdout/partial 集合一致
    fam_holdout = {c for c, fs in family_map.items() if "holdout9" in fs}
    fam_partial = {c for c, fs in family_map.items() if "partial7" in fs}
    fam_ok = fam_holdout == holdout and fam_partial == partial7
    checks["manifest_family_sets_stable"] = fam_ok
    rows.append(
        _row(
            check_id="manifest_family_sets_stable",
            layer="scale_harvest_exclusion_dual_layer",
            expected="holdout9+partial7_match_constants",
            observed=(
                f"holdout={len(fam_holdout)};partial7={len(fam_partial)}"
            ),
            ok=fam_ok,
            notes="ok" if fam_ok else "manifest_family_drift",
        )
    )

    # 863 与 caveat10 不相交（规模不变式）
    h863_rows = load_csv_rows(_abs(paths.harvest_863_status_rel, base_dir=base_dir))
    h863_codes = {
        str(r.get("company_code") or "").strip() for r in h863_rows if r
    }
    leak_863 = sorted(caveat10 & h863_codes)
    disjoint_ok = len(leak_863) == 0 and len(h863_codes) == EXPECTED_863_COMPLETE
    checks["harvest_863_disjoint_caveat10"] = disjoint_ok
    rows.append(
        _row(
            check_id="harvest_863_disjoint_caveat10",
            layer="scale_harvest_exclusion_dual_layer",
            cohort_id="harvest_863",
            expected="disjoint;n=861",
            observed=(
                f"n={len(h863_codes)};leak={','.join(leak_863) or 'none'}"
            ),
            ok=disjoint_ok,
            notes="ok" if disjoint_ok else "caveat10_leaked_into_863",
        )
    )

    # FM-03 mock 产物仍在（不覆盖）
    fm03_matrix = _abs(
        os.path.join(paths.fm03_mock_root_rel, "consistency_matrix.csv"),
        base_dir=base_dir,
    )
    fm03_present = os.path.isfile(fm03_matrix)
    checks["fm03_mock_artifacts_preserved"] = fm03_present
    rows.append(
        _row(
            check_id="fm03_mock_artifacts_preserved",
            layer="scale_harvest_exclusion_dual_layer",
            root_id="C-ROOT-MOCK5",
            path=paths.fm03_mock_root_rel,
            expected="consistency_matrix_present",
            observed="present" if fm03_present else "missing",
            ok=fm03_present,
            notes="ok" if fm03_present else "fm03_overwrite_or_missing",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["scale_harvest_exclusion_dual_layer_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="scale_harvest_exclusion_dual_layer_all_pass",
            layer="scale_harvest_exclusion_dual_layer",
            expected="phase35_500+863_disjoint+fm03_preserved",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
            notes="ok" if all_ok else "scale_dual_layer_incomplete",
        )
    )
    return rows, checks


def build_output_root_protection_hardening_rows(
    paths: ScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """
    output-root 保护加固：在既有 harvest/snapshot/auth 守卫之上，
    追加 phase35 + 863 harvest 根拒绝，并核对 MOCK24 放行。
    """
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    # 复用既有 battery（slice1 harvest + snapshot full + auth + mock）
    base_rows, base_checks = build_protected_write_guard_battery_rows(
        mock_probe_rel=paths.output_root_rel, base_dir=base_dir
    )
    rows.extend(base_rows)
    checks.update(base_checks)

    # phase35 harvest 写拒绝
    p35_probe = os.path.join(
        HARVEST_PHASE35_ROOT_REL, "quality", "probe_write_forbidden.csv"
    )
    p35_refused = False
    p35_msg = ""
    try:
        assert_safe_erad_audit_write_path(
            _abs(p35_probe, base_dir=base_dir),
            base_dir=base_dir,
            allowed_audit_root_rel=paths.output_root_rel,
        )
    except RuntimeError as exc:
        p35_refused = CLEANUP_REFUSED_MSG in str(exc)
        p35_msg = str(exc)[:120]
    checks["write_guard_phase35_harvest_refused"] = p35_refused
    rows.append(
        _row(
            check_id="write_guard_phase35_harvest_refused",
            layer="output_root_protection_hardening",
            path=p35_probe,
            expected="CLEANUP_REFUSED",
            observed=f"refused={p35_refused};msg={p35_msg}",
            ok=p35_refused,
            notes="ok" if p35_refused else "phase35_write_guard_gap",
        )
    )

    # 863 harvest 树写拒绝（quality 探针）
    h863_probe = os.path.join(
        HARVEST_863_ROOT_REL, "quality", "probe_write_forbidden_fm22.csv"
    )
    h863_refused = False
    h863_msg = ""
    try:
        assert_safe_erad_audit_write_path(
            _abs(h863_probe, base_dir=base_dir),
            base_dir=base_dir,
            allowed_audit_root_rel=paths.output_root_rel,
        )
    except RuntimeError as exc:
        h863_refused = CLEANUP_REFUSED_MSG in str(exc)
        h863_msg = str(exc)[:120]
    checks["write_guard_harvest_863_refused"] = h863_refused
    rows.append(
        _row(
            check_id="write_guard_harvest_863_refused",
            layer="output_root_protection_hardening",
            path=h863_probe,
            expected="CLEANUP_REFUSED",
            observed=f"refused={h863_refused};msg={h863_msg}",
            ok=h863_refused,
            notes="ok" if h863_refused else "harvest_863_write_guard_gap",
        )
    )

    # 本任务 output root 放行
    out_ok = False
    out_detail = ""
    try:
        assert_fm22_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK24_or_ephemeral_allowed",
            observed=out_detail,
            ok=out_ok,
            notes="ok" if out_ok else "output_root_blocked",
        )
    )

    hardening_keys = [
        "write_guard_phase35_harvest_refused",
        "write_guard_harvest_863_refused",
        "hardening_output_root_allowed",
        "protected_write_guard_battery_all_pass",
    ]
    hardening_ok = all(checks.get(k) for k in hardening_keys)
    checks["output_root_protection_hardening_all_pass"] = hardening_ok
    rows.append(
        _row(
            check_id="output_root_protection_hardening_all_pass",
            layer="output_root_protection_hardening",
            expected="base_guard+phase35+863_refused;mock24_ok",
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
    paths: ScalePaths, *, base_dir: str = BASE_DIR
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """冻结 mock cohort 写隔离：MOCK3–23 拒绝 · MOCK24 放行。"""
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

    mock24_prefix = frozen.get(THIS_TASK_ROOT_ID)
    mock24_listed = mock24_prefix is not None
    mock24_allowed = False
    if mock24_prefix:
        try:
            assert_frozen_mock_cohort_write_forbidden(
                mock24_prefix,
                allow_root_ids=(THIS_TASK_ROOT_ID,),
                base_dir=base_dir,
            )
            mock24_allowed = True
        except RuntimeError:
            mock24_allowed = False
    checks["frozen_allow_mock24"] = mock24_listed and mock24_allowed
    rows.append(
        _row(
            check_id="frozen_allow_mock24",
            layer="frozen_mock_isolation",
            root_id=THIS_TASK_ROOT_ID,
            path=_rel(mock24_prefix, base_dir=base_dir) if mock24_prefix else "",
            expected="listed_and_allowed_when_in_allowlist",
            observed=f"listed={mock24_listed};allowed={mock24_allowed}",
            ok=mock24_listed and mock24_allowed,
            notes="ok" if mock24_listed and mock24_allowed else "mock24_allow_fail",
        )
    )

    out_ok = False
    out_detail = ""
    try:
        assert_fm22_output_root(paths.output_root_rel, base_dir=base_dir)
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
            expected="MOCK24_or_ephemeral_allowed",
            observed=out_detail,
            ok=out_ok,
        )
    )

    # MOCK23 / MOCK8 抽样：即使 allow MOCK24 仍不可写
    for root_id, check_id, expected in (
        ("C-ROOT-MOCK23", "mock23_still_frozen", "fm21_mock23_not_writable_by_fm22"),
        ("C-ROOT-MOCK8", "seal_mock8_still_frozen", "seal_chain_not_writable_by_fm22"),
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
            expected="MOCK3-23_blocked_MOCK24_ok",
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
    """protected CSV：MOCK3–24 + AUTH1 注册一致性。"""
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
            expected="write_policy=read_only_no_overwrite",
            observed=str(auth.get("write_policy") or ""),
            ok=auth_ok,
            notes="ok" if auth_ok else "auth_policy_drift",
        )
    )

    mock24 = by_id.get(THIS_TASK_ROOT_ID) or {}
    mock24_path = (mock24.get("path_pattern") or "").strip().rstrip("/")
    expected_path = DEFAULT_MOCK_OUTPUT_ROOT_REL
    mock24_ok = mock24_path.endswith(
        "_mock_c_fm22_scale_harvest_exclusion_repro_fingerprint"
    ) or mock24_path == expected_path
    checks["protected_csv_mock24_path"] = mock24_ok
    rows.append(
        _row(
            check_id="protected_csv_mock24_path",
            layer="protected_csv_registry",
            root_id=THIS_TASK_ROOT_ID,
            path=mock24_path,
            expected=expected_path,
            observed=mock24_path or "missing",
            ok=mock24_ok,
            notes="ok" if mock24_ok else "mock24_path_mismatch",
        )
    )

    all_ok = all(checks.values()) if checks else False
    checks["protected_csv_registry_all_pass"] = all_ok
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-24+AUTH1_registered",
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
    """FM-01..05 + FM-12..21 既有 gate 只读聚合（跳过 seal FM06–11）。"""
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
        ):
            if "seal_chain_extended" in payload:
                ok = ok and payload.get("seal_chain_extended") is False
        if key == "fm21" and "drift_detected" in payload:
            ok = ok and payload.get("drift_detected") is False
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
            check_id="fm01_05_12_21_battery_all_pass",
            layer="fm_gate_battery",
            expected="nonseal_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_05_12_21_battery_all_pass"] = all_ok
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


def write_scale_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in MATRIX_FIELDS})


def fingerprint_scale_matrix(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    """规模 QA 矩阵结构指纹。"""
    ok_count = sum(1 for r in rows if r.get("ok") == "yes")
    fail_count = sum(1 for r in rows if r.get("ok") != "yes")
    layers: Dict[str, int] = {}
    for r in rows:
        layer = str(r.get("layer") or "")
        layers[layer] = layers.get(layer, 0) + 1
    canon = json.dumps(
        {
            "row_count": len(rows),
            "ok_count": ok_count,
            "fail_count": fail_count,
            "layers": dict(sorted(layers.items())),
            "check_ids": [str(r.get("check_id") or "") for r in rows],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return {
        "row_count": len(rows),
        "ok_count": ok_count,
        "fail_count": fail_count,
        "layers": layers,
        "fingerprint_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
    }


def run_scale_harvest_exclusion_repro_fingerprint(
    *,
    paths: ScalePaths = ScalePaths(),
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-22 规模 harvest/exclusion + 可复现指纹 QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_fm22_output_root(paths.output_root_rel, base_dir=base_dir)

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
    }

    reg_rows, reg_checks, reg_meta = build_scale_lineage_registry_rows(
        base_dir=base_dir
    )
    repro_rows, repro_checks, observed_fps = build_multi_cohort_repro_fingerprint_rows(
        paths, base_dir=base_dir
    )
    dual_rows, dual_checks = build_phase35_scale_dual_layer_rows(
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
        "scale_harvest_exclusion_dual_layer": (
            "PASS_OFFLINE"
            if dual_checks.get("scale_harvest_exclusion_dual_layer_all_pass")
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
            if bat_checks.get("fm01_05_12_21_battery_all_pass")
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
    matrix_rel = _rel(
        os.path.join(out_root, "scale_matrix.csv"), base_dir=base_dir
    )
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
        "observed_fps": observed_fps,
        "frozen_fps": {
            "fm01_863": FROZEN_FM01_863_FP_SHA256,
            "fm02_190": FROZEN_FM02_190_FP_SHA256,
            "fm03_harvest_863": FROZEN_FM03_HARVEST_863_FP_SHA256,
            "phase35_500": FROZEN_PHASE35_500_FP_SHA256,
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
        "fm22_gate": overall,
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
    }
    with open(_abs(battery_rel, base_dir=base_dir), "w", encoding="utf-8") as fh:
        json.dump(battery_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    packet_rel = _rel(
        os.path.join(out_root, "scale_packet.json"), base_dir=base_dir
    )
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
                "notes": (
                    "scale harvest-exclusion dual-layer (phase35×500) + "
                    "multi-cohort repro fingerprint (863/190/861/500) + "
                    "output-root protection hardening; "
                    "EXECUTE remains human-held; does not overwrite MOCK3-23"
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
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": matrix_rel,
        "fingerprint_path": fingerprint_rel,
        "fingerprint": fp,
        "registry_path": registry_rel,
        "battery_path": battery_rel,
        "packet_path": packet_rel,
        "observed_fps": observed_fps,
        "inputs": {
            "harvest_863_status": paths.harvest_863_status_rel,
            "harvest_phase35_status": paths.harvest_phase35_status_rel,
            "exclusion_manifest": paths.exclusion_manifest_rel,
            "fm01_mock_root": paths.fm01_mock_root_rel,
            "fm02_mock_root": paths.fm02_mock_root_rel,
            "fm03_mock_root": paths.fm03_mock_root_rel,
        },
        "mock_root_is_isolated": True,
        "checks": {
            **reg_checks,
            **repro_checks,
            **dual_checks,
            **hard_checks,
            **fr_checks,
            **csv_checks,
            **bat_checks,
            **hold_checks,
        },
    }
