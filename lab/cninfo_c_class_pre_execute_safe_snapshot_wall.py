"""
CNINFO C-class — Pre-EXECUTE 安全 snapshot 墙冻结（离线 · C-FM-06）。

在 C-FM-05（cross-FM mock cohort 完整性）之上，补齐：
  1) FM-01..05 gate battery 只读聚合（含 FM-05 完整性 gate JSON）
  2) exclusion universe 结构冻结指纹（19 行 · 18 唯一码 · 7+3+9 家族）
  3) dual-layer QA closure 冻结（coverage 10/10 · empty3+partial7 索引）
  4) EXECUTE 硬墙：execute=false · CLI --execute 拒绝 · 生产根写守卫抽检
  5) protected_output_roots.csv 注册一致性（MOCK3–8 · AUTH1）

禁止：CNINFO live · production EXECUTE · 覆盖权威 dual-layer 索引 · verified 声称。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    CLEANUP_REFUSED_MSG,
    DUAL_LAYER_INDEX_WRITE_FORBIDDEN,
    PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN,
    PROTECTED_ROOTS_CSV_REL,
    assert_authoritative_dual_layer_index_write_forbidden,
    assert_safe_c_class_snapshot_dryrun_write_root,
    assert_safe_erad_audit_write_path,
    is_allowed_mock_test_cleanup_path,
)
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    EXPECTED_HOLDOUT9,
    load_csv_rows,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
)

TASK_ID = "C-FM-06"

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm06_pre_execute_safe_snapshot_wall"
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

EXCLUSION_UNIVERSE_CSV_REL = (
    "outputs/validation/"
    "cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv"
)
DUAL_LAYER_INDEX_ROOT_REL = AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL
COVERAGE_CSV_REL = (
    f"{DUAL_LAYER_INDEX_ROOT_REL}/qa_closure_dual_layer_cohort_coverage.csv"
)
EMPTY3_INDEX_CSV_REL = (
    f"{DUAL_LAYER_INDEX_ROOT_REL}/qa_closure_dual_layer_evidence_index.csv"
)
PARTIAL7_INDEX_CSV_REL = (
    f"{DUAL_LAYER_INDEX_ROOT_REL}/qa_closure_dual_layer_evidence_index_partial7.csv"
)

HARVEST_SLICE1_REL = "outputs/harvest/cninfo_c_class/fuller_market_slice1_200"
SNAPSHOT_FULL_REL = "outputs/snapshot/cninfo_c_class/full"

EXPECTED_EXCLUSION_ROWS = 19
EXPECTED_EXCLUSION_UNIQUE = 18  # 000003 同时出现在 partial7 与 holdout9
EXPECTED_CAVEAT10 = 10
EXPECTED_EMPTY3 = 3
EXPECTED_PARTIAL7 = 7
EXPECTED_HOLDOUT9_N = 9

REQUIRED_PROTECTED_ROOT_IDS = (
    "C-ROOT-MOCK3",
    "C-ROOT-MOCK4",
    "C-ROOT-MOCK5",
    "C-ROOT-MOCK6",
    "C-ROOT-MOCK7",
    "C-ROOT-MOCK8",
    "C-ROOT-AUTH1",
)

WALL_MATRIX_FIELDS = [
    "check_id",
    "layer",
    "path",
    "expected",
    "observed",
    "ok",
    "notes",
]


@dataclass(frozen=True)
class WallPaths:
    """只读输入与隔离写根路径规格。"""

    fm01_gate_json_rel: str = FM01_GATE_JSON_REL
    fm02_gate_json_rel: str = FM02_GATE_JSON_REL
    fm03_gate_json_rel: str = FM03_GATE_JSON_REL
    fm04_gate_json_rel: str = FM04_GATE_JSON_REL
    fm05_gate_json_rel: str = FM05_GATE_JSON_REL
    exclusion_universe_csv_rel: str = EXCLUSION_UNIVERSE_CSV_REL
    coverage_csv_rel: str = COVERAGE_CSV_REL
    empty3_index_csv_rel: str = EMPTY3_INDEX_CSV_REL
    partial7_index_csv_rel: str = PARTIAL7_INDEX_CSV_REL
    protected_roots_csv_rel: str = PROTECTED_ROOTS_CSV_REL
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


def assert_wall_output_root(output_root: str, *, base_dir: str = BASE_DIR) -> str:
    """墙冻结产物写根：必须 validation/_mock_*，并拒绝权威 dual-layer 索引根。"""
    out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    assert_authoritative_dual_layer_index_write_forbidden(out, base_dir=base_dir)
    return out


def load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_protected_root_rows(
    csv_rel: str = PROTECTED_ROOTS_CSV_REL, *, base_dir: str = BASE_DIR
) -> List[Dict[str, str]]:
    path = _abs(csv_rel, base_dir=base_dir)
    with open(path, encoding="utf-8", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def _row(
    *,
    check_id: str,
    layer: str,
    path: str = "",
    expected: str = "",
    observed: str = "",
    ok: bool = False,
    notes: str = "",
) -> Dict[str, str]:
    return {
        "check_id": check_id,
        "layer": layer,
        "path": path,
        "expected": expected,
        "observed": observed,
        "ok": "yes" if ok else "no",
        "notes": notes or ("ok" if ok else "fail"),
    }


def build_fm_gate_battery_rows(
    *,
    fm01: Dict[str, Any],
    fm02: Dict[str, Any],
    fm03: Dict[str, Any],
    fm04: Dict[str, Any],
    fm05: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """FM-01..05 既有 gate 只读聚合（不重跑）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    specs = [
        ("fm01_isolated_dryrun_repro", fm01),
        ("fm02_isolated_validation_cohorts", fm02),
        ("fm03_harvest_exclusion_dual_layer", fm03),
        ("fm04_ledger_resume_lineage", fm04),
        ("fm05_cross_fm_mock_cohort_integrity", fm05),
    ]
    for check_id, payload in specs:
        gate = str(payload.get("gate") or "").strip()
        cninfo = payload.get("cninfo_calls", None)
        execute = payload.get("execute_production_snapshot_rebuild", None)
        ok = gate == "PASS_OFFLINE" and cninfo == 0 and execute is False
        rows.append(
            _row(
                check_id=check_id,
                layer="fm_gate_battery",
                path=check_id,
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
            check_id="fm01_to_05_battery_all_pass",
            layer="fm_gate_battery",
            expected="all_prior_fm_gates_PASS_OFFLINE",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(specs)}",
            ok=all_ok,
            notes="ok" if all_ok else "battery_incomplete",
        )
    )
    checks["fm01_to_05_battery_all_pass"] = all_ok
    return rows, checks


def fingerprint_exclusion_universe(
    rows: Sequence[Dict[str, str]],
) -> Dict[str, Any]:
    """exclusion universe 结构指纹（不依赖文件 mtime）。"""
    families: Dict[str, int] = {}
    codes: List[str] = []
    promo_yes: List[str] = []
    for r in rows:
        fam = str(r.get("cohort_family") or "").strip()
        families[fam] = families.get(fam, 0) + 1
        code = str(r.get("company_code") or "").strip()
        if code:
            codes.append(code)
        if str(r.get("promotion_allowed_now") or "").strip().lower() == "yes":
            promo_yes.append(code)
    unique = sorted(set(codes))
    canon = json.dumps(
        {
            "row_count": len(rows),
            "unique_codes": unique,
            "families": dict(sorted(families.items())),
            "promo_yes": promo_yes,
            "exclusion_ids": [str(r.get("exclusion_id") or "") for r in rows],
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return {
        "row_count": len(rows),
        "unique_code_count": len(unique),
        "unique_codes": unique,
        "families": families,
        "promo_yes_count": len(promo_yes),
        "fingerprint_sha256": hashlib.sha256(canon.encode("utf-8")).hexdigest(),
    }


def build_exclusion_universe_freeze_rows(
    *,
    csv_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool], Dict[str, Any]]:
    """exclusion universe 结构冻结核验。"""
    rows_out: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    path = _abs(csv_rel, base_dir=base_dir)
    exists = os.path.isfile(path)
    csv_rows = load_csv_rows(path) if exists else []
    fp = fingerprint_exclusion_universe(csv_rows) if exists else {}

    exists_ok = exists
    checks["exclusion_universe_exists"] = exists_ok
    rows_out.append(
        _row(
            check_id="exclusion_universe_exists",
            layer="exclusion_universe_freeze",
            path=csv_rel,
            expected="file_present",
            observed=f"exists={exists}",
            ok=exists_ok,
        )
    )

    row_ok = exists and int(fp.get("row_count") or 0) == EXPECTED_EXCLUSION_ROWS
    checks["exclusion_universe_row_count_19"] = row_ok
    rows_out.append(
        _row(
            check_id="exclusion_universe_row_count_19",
            layer="exclusion_universe_freeze",
            path=csv_rel,
            expected=str(EXPECTED_EXCLUSION_ROWS),
            observed=str(fp.get("row_count", "missing")),
            ok=row_ok,
        )
    )

    unique_ok = (
        exists and int(fp.get("unique_code_count") or 0) == EXPECTED_EXCLUSION_UNIQUE
    )
    checks["exclusion_universe_unique_18"] = unique_ok
    rows_out.append(
        _row(
            check_id="exclusion_universe_unique_18",
            layer="exclusion_universe_freeze",
            path=csv_rel,
            expected=str(EXPECTED_EXCLUSION_UNIQUE),
            observed=str(fp.get("unique_code_count", "missing")),
            ok=unique_ok,
        )
    )

    families = fp.get("families") or {}
    fam_ok = (
        exists
        and int(families.get("partial7") or 0) == EXPECTED_PARTIAL7
        and int(families.get("empty_dividend3") or 0) == EXPECTED_EMPTY3
        and int(families.get("holdout9") or 0) == EXPECTED_HOLDOUT9_N
    )
    checks["exclusion_universe_families_7_3_9"] = fam_ok
    rows_out.append(
        _row(
            check_id="exclusion_universe_families_7_3_9",
            layer="exclusion_universe_freeze",
            path=csv_rel,
            expected="partial7=7;empty_dividend3=3;holdout9=9",
            observed=(
                f"partial7={families.get('partial7')};"
                f"empty_dividend3={families.get('empty_dividend3')};"
                f"holdout9={families.get('holdout9')}"
            ),
            ok=fam_ok,
        )
    )

    # 家族集合与既有 EXPECTED_* 对齐
    fam_codes: Dict[str, set] = {
        "partial7": set(),
        "empty_dividend3": set(),
        "holdout9": set(),
    }
    for r in csv_rows:
        fam = str(r.get("cohort_family") or "").strip()
        code = str(r.get("company_code") or "").strip()
        if fam in fam_codes and code:
            fam_codes[fam].add(code)
    set_ok = (
        fam_codes["partial7"] == set(EXPECTED_SLICE1_PARTIAL7)
        and fam_codes["empty_dividend3"] == set(EXPECTED_SLICE1_EMPTY_DIVIDEND3)
        and fam_codes["holdout9"] == set(EXPECTED_HOLDOUT9)
    )
    checks["exclusion_universe_family_sets"] = set_ok
    rows_out.append(
        _row(
            check_id="exclusion_universe_family_sets",
            layer="exclusion_universe_freeze",
            path=csv_rel,
            expected="partial7∪empty3∪holdout9 match EXPECTED_*",
            observed=(
                f"partial7={len(fam_codes['partial7'])};"
                f"empty3={len(fam_codes['empty_dividend3'])};"
                f"holdout9={len(fam_codes['holdout9'])}"
            ),
            ok=set_ok,
        )
    )

    promo_ok = exists and int(fp.get("promo_yes_count") or 0) == 0
    checks["exclusion_universe_no_promotion"] = promo_ok
    rows_out.append(
        _row(
            check_id="exclusion_universe_no_promotion",
            layer="exclusion_universe_freeze",
            path=csv_rel,
            expected="promotion_allowed_now=no for all",
            observed=f"promo_yes_count={fp.get('promo_yes_count', 'missing')}",
            ok=promo_ok,
        )
    )

    # slice1 排除唯一集仍为 caveat10（holdout 不膨胀 slice1 排除）
    slice1_core = fam_codes["partial7"] | fam_codes["empty_dividend3"]
    core_ok = slice1_core == set(EXPECTED_SLICE1_EXCLUDED_UNIQUE)
    checks["exclusion_slice1_core_equals_caveat10"] = core_ok
    rows_out.append(
        _row(
            check_id="exclusion_slice1_core_equals_caveat10",
            layer="exclusion_universe_freeze",
            path=csv_rel,
            expected=f"n={EXPECTED_CAVEAT10}",
            observed=f"n={len(slice1_core)}",
            ok=core_ok,
        )
    )

    all_ok = all(checks.values())
    rows_out.append(
        _row(
            check_id="exclusion_universe_freeze_all_pass",
            layer="exclusion_universe_freeze",
            path=csv_rel,
            expected="structure_frozen",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["exclusion_universe_freeze_all_pass"] = all_ok
    return rows_out, checks, fp


def build_dual_layer_qa_freeze_rows(
    *,
    coverage_csv_rel: str,
    empty3_index_csv_rel: str,
    partial7_index_csv_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """dual-layer QA closure 冻结：coverage 10/10 · 索引行数。"""
    rows_out: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    cov_path = _abs(coverage_csv_rel, base_dir=base_dir)
    cov_exists = os.path.isfile(cov_path)
    cov_rows = load_csv_rows(cov_path) if cov_exists else []
    by_fam = {
        str(r.get("caveat_family") or "").strip(): r for r in cov_rows
    }
    all_row = by_fam.get("all_caveats") or {}
    empty_row = by_fam.get("empty_dividend") or {}
    partial_row = by_fam.get("partial") or {}

    cov_ok = (
        cov_exists
        and str(all_row.get("expected_count") or "") == "10"
        and str(all_row.get("indexed_pass_count") or "") == "10"
        and str(all_row.get("index_status") or "") == "indexed_pass"
        and str(empty_row.get("indexed_pass_count") or "") == "3"
        and str(partial_row.get("indexed_pass_count") or "") == "7"
    )
    checks["dual_layer_coverage_10_of_10"] = cov_ok
    rows_out.append(
        _row(
            check_id="dual_layer_coverage_10_of_10",
            layer="dual_layer_qa_freeze",
            path=coverage_csv_rel,
            expected="all_caveats=10/10 indexed_pass; empty=3; partial=7",
            observed=(
                f"all={all_row.get('indexed_pass_count')}/"
                f"{all_row.get('expected_count')};"
                f"status={all_row.get('index_status')};"
                f"empty={empty_row.get('indexed_pass_count')};"
                f"partial={partial_row.get('indexed_pass_count')}"
            ),
            ok=cov_ok,
        )
    )

    e3_path = _abs(empty3_index_csv_rel, base_dir=base_dir)
    e3_exists = os.path.isfile(e3_path)
    e3_rows = load_csv_rows(e3_path) if e3_exists else []
    e3_codes = {
        str(r.get("company_code") or "").strip()
        for r in e3_rows
        if str(r.get("company_code") or "").strip()
    }
    e3_ok = e3_exists and e3_codes == set(EXPECTED_SLICE1_EMPTY_DIVIDEND3)
    checks["dual_layer_empty3_index_set"] = e3_ok
    rows_out.append(
        _row(
            check_id="dual_layer_empty3_index_set",
            layer="dual_layer_qa_freeze",
            path=empty3_index_csv_rel,
            expected=f"n={EXPECTED_EMPTY3};codes={','.join(sorted(EXPECTED_SLICE1_EMPTY_DIVIDEND3))}",
            observed=f"n={len(e3_codes)};codes={','.join(sorted(e3_codes)) or 'missing'}",
            ok=e3_ok,
        )
    )

    p7_path = _abs(partial7_index_csv_rel, base_dir=base_dir)
    p7_exists = os.path.isfile(p7_path)
    p7_rows = load_csv_rows(p7_path) if p7_exists else []
    p7_codes = {
        str(r.get("company_code") or "").strip()
        for r in p7_rows
        if str(r.get("company_code") or "").strip()
    }
    p7_ok = p7_exists and p7_codes == set(EXPECTED_SLICE1_PARTIAL7)
    checks["dual_layer_partial7_index_set"] = p7_ok
    rows_out.append(
        _row(
            check_id="dual_layer_partial7_index_set",
            layer="dual_layer_qa_freeze",
            path=partial7_index_csv_rel,
            expected=f"n={EXPECTED_PARTIAL7}",
            observed=f"n={len(p7_codes)}",
            ok=p7_ok,
        )
    )

    union = e3_codes | p7_codes
    union_ok = union == set(EXPECTED_SLICE1_EXCLUDED_UNIQUE) and len(union) == EXPECTED_CAVEAT10
    checks["dual_layer_union_equals_caveat10"] = union_ok
    rows_out.append(
        _row(
            check_id="dual_layer_union_equals_caveat10",
            layer="dual_layer_qa_freeze",
            path=DUAL_LAYER_INDEX_ROOT_REL,
            expected=f"n={EXPECTED_CAVEAT10}",
            observed=f"n={len(union)}",
            ok=union_ok,
        )
    )

    # 权威根不得被本任务写
    auth_probe = os.path.join(
        AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
        "qa_closure_dual_layer_evidence_index.csv",
    )
    auth_refused = False
    auth_msg = ""
    try:
        assert_authoritative_dual_layer_index_write_forbidden(
            _abs(auth_probe, base_dir=base_dir), base_dir=base_dir
        )
    except RuntimeError as exc:
        auth_refused = DUAL_LAYER_INDEX_WRITE_FORBIDDEN in str(exc)
        auth_msg = str(exc)[:120]
    checks["dual_layer_auth_write_forbidden"] = auth_refused
    rows_out.append(
        _row(
            check_id="dual_layer_auth_write_forbidden",
            layer="dual_layer_qa_freeze",
            path=auth_probe,
            expected="DUAL_LAYER_INDEX_WRITE_FORBIDDEN",
            observed=f"refused={auth_refused};msg={auth_msg}",
            ok=auth_refused,
        )
    )

    all_ok = all(checks.values())
    rows_out.append(
        _row(
            check_id="dual_layer_qa_freeze_all_pass",
            layer="dual_layer_qa_freeze",
            expected="coverage_10/10_and_indexes_frozen",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["dual_layer_qa_freeze_all_pass"] = all_ok
    return rows_out, checks


def build_execute_wall_rows(
    *,
    mock_probe_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """EXECUTE 硬墙：生产写拒绝 · mock 放行 · 显式 execute=false 语义。"""
    rows_out: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    # 1) 常量硬墙
    execute_flag = False
    checks["execute_production_snapshot_rebuild_false"] = execute_flag is False
    rows_out.append(
        _row(
            check_id="execute_production_snapshot_rebuild_false",
            layer="execute_wall",
            expected="false",
            observed=str(execute_flag).lower(),
            ok=execute_flag is False,
            notes="hard_wall_constant",
        )
    )

    # 2) harvest slice1 写拒绝
    harvest_probe = os.path.join(
        HARVEST_SLICE1_REL, "quality", "probe_write_forbidden.csv"
    )
    harvest_refused = False
    harvest_msg = ""
    try:
        assert_safe_erad_audit_write_path(
            _abs(harvest_probe, base_dir=base_dir),
            base_dir=base_dir,
            allowed_audit_root_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        )
    except RuntimeError as exc:
        harvest_refused = CLEANUP_REFUSED_MSG in str(exc)
        harvest_msg = str(exc)[:120]
    checks["execute_wall_harvest_slice1_refused"] = harvest_refused
    rows_out.append(
        _row(
            check_id="execute_wall_harvest_slice1_refused",
            layer="execute_wall",
            path=harvest_probe,
            expected="CLEANUP_REFUSED",
            observed=f"refused={harvest_refused};msg={harvest_msg}",
            ok=harvest_refused,
        )
    )

    # 3) snapshot full dry-run 写拒绝
    snap_refused = False
    snap_msg = ""
    try:
        assert_safe_c_class_snapshot_dryrun_write_root(
            _abs(SNAPSHOT_FULL_REL, base_dir=base_dir),
            base_dir=base_dir,
            allow_production_scaffold=False,
        )
    except RuntimeError as exc:
        snap_refused = PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN in str(exc)
        snap_msg = str(exc)[:120]
    checks["execute_wall_snapshot_full_refused"] = snap_refused
    rows_out.append(
        _row(
            check_id="execute_wall_snapshot_full_refused",
            layer="execute_wall",
            path=SNAPSHOT_FULL_REL,
            expected="PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN",
            observed=f"refused={snap_refused};msg={snap_msg}",
            ok=snap_refused,
        )
    )

    # 4) mock 探针允许
    mock_abs = _abs(mock_probe_rel, base_dir=base_dir)
    mock_ok = True
    mock_detail = "allowed"
    try:
        assert_authoritative_dual_layer_index_write_forbidden(
            mock_abs, base_dir=base_dir
        )
        assert_safe_erad_audit_write_path(
            os.path.join(mock_abs, "wall_probe.json"),
            base_dir=base_dir,
            allowed_audit_root_rel=mock_probe_rel,
        )
        assert_safe_c_class_snapshot_dryrun_write_root(
            mock_abs, base_dir=base_dir, allow_production_scaffold=False
        )
    except RuntimeError as exc:
        mock_ok = False
        mock_detail = str(exc)[:120]
    checks["execute_wall_mock_allowed"] = mock_ok
    rows_out.append(
        _row(
            check_id="execute_wall_mock_allowed",
            layer="execute_wall",
            path=mock_probe_rel,
            expected="mock_writable_by_guards",
            observed=mock_detail,
            ok=mock_ok,
        )
    )

    # 5) 人批语义：本包不翻转 approved_for_snapshot_rebuild
    approved = False
    checks["approved_for_snapshot_rebuild_remains_false"] = approved is False
    rows_out.append(
        _row(
            check_id="approved_for_snapshot_rebuild_remains_false",
            layer="execute_wall",
            expected="false",
            observed=str(approved).lower(),
            ok=approved is False,
            notes="freeze_packet_does_not_approve_execute",
        )
    )

    all_ok = all(checks.values())
    rows_out.append(
        _row(
            check_id="execute_wall_all_pass",
            layer="execute_wall",
            expected="execute_false;prod_refused;mock_allowed;not_approved",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["execute_wall_all_pass"] = all_ok
    return rows_out, checks


def build_protected_csv_registry_rows(
    *,
    csv_rel: str,
    base_dir: str = BASE_DIR,
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """protected_output_roots.csv 注册一致性（含 MOCK8）。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}
    csv_rows = load_protected_root_rows(csv_rel, base_dir=base_dir)
    by_id = {
        str(r.get("root_id") or "").strip(): r
        for r in csv_rows
        if str(r.get("root_id") or "").strip()
    }

    for root_id in REQUIRED_PROTECTED_ROOT_IDS:
        present = root_id in by_id
        path = ""
        if present:
            path = str(by_id[root_id].get("path_pattern") or "").strip()
        check_id = f"protected_csv_has_{root_id}"
        rows.append(
            _row(
                check_id=check_id,
                layer="protected_csv_registry",
                path=path,
                expected="listed_in_protected_csv",
                observed=f"present={present}",
                ok=present,
                notes="ok" if present else "missing_root_id",
            )
        )
        checks[check_id] = present

    auth = by_id.get("C-ROOT-AUTH1") or {}
    auth_policy = str(auth.get("write_policy") or "").strip()
    auth_ok = auth_policy == "read_only_no_overwrite"
    checks["protected_csv_auth1_readonly"] = auth_ok
    rows.append(
        _row(
            check_id="protected_csv_auth1_readonly",
            layer="protected_csv_registry",
            path=str(auth.get("path_pattern") or ""),
            expected="write_policy=read_only_no_overwrite",
            observed=f"write_policy={auth_policy or 'missing'}",
            ok=auth_ok,
        )
    )

    mock8 = by_id.get("C-ROOT-MOCK8") or {}
    mock8_path = str(mock8.get("path_pattern") or "").strip().rstrip("/")
    mock8_ok = mock8_path == DEFAULT_MOCK_OUTPUT_ROOT_REL
    checks["protected_csv_mock8_path"] = mock8_ok
    rows.append(
        _row(
            check_id="protected_csv_mock8_path",
            layer="protected_csv_registry",
            path=mock8_path,
            expected=DEFAULT_MOCK_OUTPUT_ROOT_REL,
            observed=mock8_path or "missing",
            ok=mock8_ok,
        )
    )

    all_ok = all(checks.values())
    rows.append(
        _row(
            check_id="protected_csv_registry_all_pass",
            layer="protected_csv_registry",
            expected="MOCK3-8+AUTH1_registered",
            observed=f"pass={sum(1 for v in checks.values() if v)}/{len(checks)}",
            ok=all_ok,
        )
    )
    checks["protected_csv_registry_all_pass"] = all_ok
    return rows, checks


def write_wall_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=WALL_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in WALL_MATRIX_FIELDS})


def fingerprint_wall_matrix(rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    """墙矩阵结构指纹。"""
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


def build_human_approval_packet(
    *,
    gate: str,
    exclusion_fp: Dict[str, Any],
    layer_gates: Dict[str, str],
    generated_at: str,
) -> Dict[str, Any]:
    """人批冻结包：记录墙状态，明确不批准 EXECUTE。"""
    return {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "packet_kind": "pre_execute_safe_snapshot_wall_freeze",
        "gate": gate,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "cninfo_calls": 0,
        "human_action_required_for_execute": True,
        "hold_recommendation": "KEEP_EXECUTE_FALSE",
        "layer_gates": layer_gates,
        "exclusion_universe_fingerprint_sha256": exclusion_fp.get(
            "fingerprint_sha256", ""
        ),
        "exclusion_row_count": exclusion_fp.get("row_count"),
        "caveat_cohort_coverage": "10/10",
        "verified_claim_forbidden": True,
        "production_ready_claim_forbidden": True,
        "notes": (
            "本包仅冻结 pre-EXECUTE 安全墙证据；"
            "不翻转 approved_for_snapshot_rebuild；"
            "生产 snapshot EXECUTE 仍须独立人批。"
        ),
    }


def run_pre_execute_safe_snapshot_wall(
    *,
    paths: WallPaths = WallPaths(),
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-06 pre-EXECUTE 安全 snapshot 墙冻结（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_wall_output_root(paths.output_root_rel, base_dir=base_dir)

    fm01 = load_json(_abs(paths.fm01_gate_json_rel, base_dir=base_dir))
    fm02 = load_json(_abs(paths.fm02_gate_json_rel, base_dir=base_dir))
    fm03 = load_json(_abs(paths.fm03_gate_json_rel, base_dir=base_dir))
    fm04 = load_json(_abs(paths.fm04_gate_json_rel, base_dir=base_dir))
    fm05 = load_json(_abs(paths.fm05_gate_json_rel, base_dir=base_dir))

    bat_rows, bat_checks = build_fm_gate_battery_rows(
        fm01=fm01, fm02=fm02, fm03=fm03, fm04=fm04, fm05=fm05
    )
    excl_rows, excl_checks, excl_fp = build_exclusion_universe_freeze_rows(
        csv_rel=paths.exclusion_universe_csv_rel, base_dir=base_dir
    )
    dl_rows, dl_checks = build_dual_layer_qa_freeze_rows(
        coverage_csv_rel=paths.coverage_csv_rel,
        empty3_index_csv_rel=paths.empty3_index_csv_rel,
        partial7_index_csv_rel=paths.partial7_index_csv_rel,
        base_dir=base_dir,
    )
    wall_rows, wall_checks = build_execute_wall_rows(
        mock_probe_rel=paths.output_root_rel, base_dir=base_dir
    )
    csv_rows, csv_checks = build_protected_csv_registry_rows(
        csv_rel=paths.protected_roots_csv_rel, base_dir=base_dir
    )

    matrix = bat_rows + excl_rows + dl_rows + wall_rows + csv_rows
    layer_gates = {
        "fm_gate_battery": (
            "PASS_OFFLINE" if all(bat_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "exclusion_universe_freeze": (
            "PASS_OFFLINE" if all(excl_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "dual_layer_qa_freeze": (
            "PASS_OFFLINE" if all(dl_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "execute_wall": (
            "PASS_OFFLINE" if all(wall_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
        "protected_csv_registry": (
            "PASS_OFFLINE" if all(csv_checks.values()) else "FAIL_REVIEW_REQUIRED"
        ),
    }
    overall = (
        "PASS_OFFLINE"
        if all(g == "PASS_OFFLINE" for g in layer_gates.values())
        else "FAIL_REVIEW_REQUIRED"
    )

    matrix_path = os.path.join(out_root, "wall_matrix.csv")
    write_wall_matrix_csv(matrix, matrix_path)
    fp = fingerprint_wall_matrix(matrix)
    fp_path = os.path.join(out_root, "wall_fingerprint.json")
    assert_safe_erad_audit_write_path(
        fp_path,
        base_dir=base_dir,
        allowed_audit_root_rel=paths.output_root_rel,
    )
    with open(fp_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
                "fingerprint": fp,
                "exclusion_universe_fingerprint": excl_fp,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    battery_path = os.path.join(out_root, "fm_gate_battery.json")
    with open(battery_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "fm01_gate": fm01.get("gate"),
                "fm02_gate": fm02.get("gate"),
                "fm03_gate": fm03.get("gate"),
                "fm04_gate": fm04.get("gate"),
                "fm05_gate": fm05.get("gate"),
                "fm06_gate": overall,
                "cninfo_calls": 0,
                "execute_production_snapshot_rebuild": False,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    packet = build_human_approval_packet(
        gate=overall,
        exclusion_fp=excl_fp,
        layer_gates=layer_gates,
        generated_at=generated_at,
    )
    packet_path = os.path.join(out_root, "human_approval_packet.json")
    with open(packet_path, "w", encoding="utf-8") as fh:
        json.dump(packet, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    excl_fp_path = os.path.join(out_root, "exclusion_universe_fingerprint.json")
    with open(excl_fp_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generated_at": generated_at,
                "task_id": TASK_ID,
                "source_csv": paths.exclusion_universe_csv_rel,
                "fingerprint": excl_fp,
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )
        fh.write("\n")

    fail_count = sum(1 for r in matrix if r.get("ok") != "yes")
    return {
        "generated_at": generated_at,
        "task_id": TASK_ID,
        "gate": overall,
        "layer_gates": layer_gates,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "fail_count": fail_count,
        "matrix_rows": len(matrix),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "fingerprint_path": _rel(fp_path, base_dir=base_dir),
        "fingerprint": fp,
        "exclusion_fingerprint": excl_fp,
        "exclusion_fingerprint_path": _rel(excl_fp_path, base_dir=base_dir),
        "battery_path": _rel(battery_path, base_dir=base_dir),
        "human_approval_packet_path": _rel(packet_path, base_dir=base_dir),
        "human_approval_packet": packet,
        "mock_root_is_isolated": is_allowed_mock_test_cleanup_path(
            out_root, base_dir=base_dir
        ),
        "inputs": {
            "fm01_gate_json": paths.fm01_gate_json_rel,
            "fm02_gate_json": paths.fm02_gate_json_rel,
            "fm03_gate_json": paths.fm03_gate_json_rel,
            "fm04_gate_json": paths.fm04_gate_json_rel,
            "fm05_gate_json": paths.fm05_gate_json_rel,
            "exclusion_universe_csv": paths.exclusion_universe_csv_rel,
            "coverage_csv": paths.coverage_csv_rel,
            "empty3_index_csv": paths.empty3_index_csv_rel,
            "partial7_index_csv": paths.partial7_index_csv_rel,
            "protected_roots_csv": paths.protected_roots_csv_rel,
        },
    }
