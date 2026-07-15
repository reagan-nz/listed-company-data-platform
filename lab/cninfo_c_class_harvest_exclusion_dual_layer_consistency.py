"""
CNINFO C-class — harvest ↔ exclusion ↔ dual-layer cohort 一致性 QA（离线 · C-FM-03）。

在 C-FM-02 lineage（universe↔status↔harvest↔pool_decision）之上，新增：
  1) 家族感知 harvest/exclusion 一致性（partial7 vs empty_dividend3）
  2) dual-layer cohort 工具：empty3 + partial7 索引 + coverage 交叉核验
  3) exclusion manifest ↔ reconcile 一致性（含 holdout9 不膨胀 slice1 排除集）
  4) 更大 mock：863 harvest ledger 只读结构核验 + 指纹写入 _mock_* 根

禁止：CNINFO live · production EXECUTE · 覆盖 empty3/partial7 权威索引 · verified 声称。
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    assert_safe_erad_audit_write_path,
    is_allowed_mock_test_cleanup_path,
)
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    assert_isolated_validation_output_root,
    load_harvest_status_map,
    load_reconcile_pool_decisions,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    POOL_EXCLUSION_FAMILIES,
    detect_exclusion_csv_kind,
    load_exclusion_csv_rows,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
)

TASK_ID = "C-FM-03"

SLICE1_HARVEST_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/fuller_market_slice1_200/"
    "quality/company_harvest_status.csv"
)
SLICE1_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class/fuller_market_slice1_200"
HARVEST_863_STATUS_REL = (
    "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"
)
EXCLUSION_MANIFEST_REL = (
    "outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv"
)
EXCLUSION_RECONCILE_REL = (
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv"
)
DUAL_LAYER_INDEX_ROOT_REL = (
    "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index"
)
EMPTY3_INDEX_REL = (
    f"{DUAL_LAYER_INDEX_ROOT_REL}/qa_closure_dual_layer_evidence_index.csv"
)
PARTIAL7_INDEX_REL = (
    f"{DUAL_LAYER_INDEX_ROOT_REL}/qa_closure_dual_layer_evidence_index_partial7.csv"
)
COHORT_COVERAGE_REL = (
    f"{DUAL_LAYER_INDEX_ROOT_REL}/qa_closure_dual_layer_cohort_coverage.csv"
)

DEFAULT_MOCK_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency"
)

EXPECTED_SLICE1_COMPLETE = 193
EXPECTED_SLICE1_PARTIAL = 7
EXPECTED_SLICE1_TOTAL = 200
EXPECTED_COMPLETE_POOL = 190
EXPECTED_863_COMPLETE = 861
EXPECTED_HOLDOUT9 = frozenset(
    {
        "000003",
        "000578",
        "000666",
        "000689",
        "000861",
        "000961",
        "002280",
        "301212",
        "600220",
    }
)

CONSISTENCY_MATRIX_FIELDS = [
    "check_id",
    "layer",
    "company_code",
    "expected",
    "observed",
    "ok",
    "notes",
]


@dataclass(frozen=True)
class ConsistencyPaths:
    """只读输入与隔离写根路径规格。"""

    slice1_harvest_status_rel: str = SLICE1_HARVEST_STATUS_REL
    harvest_863_status_rel: str = HARVEST_863_STATUS_REL
    exclusion_manifest_rel: str = EXCLUSION_MANIFEST_REL
    exclusion_reconcile_rel: str = EXCLUSION_RECONCILE_REL
    empty3_index_rel: str = EMPTY3_INDEX_REL
    partial7_index_rel: str = PARTIAL7_INDEX_REL
    cohort_coverage_rel: str = COHORT_COVERAGE_REL
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


def assert_consistency_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """一致性产物写根：必须 validation/_mock_*，并拒绝生产根。"""
    return assert_isolated_validation_output_root(output_root, base_dir=base_dir)


def load_csv_rows(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def load_dual_layer_index_codes(
    path: str,
    *,
    require_indexed_pass: bool = True,
) -> Dict[str, Dict[str, str]]:
    """读取 dual-layer evidence index → code→row。"""
    rows = load_csv_rows(path)
    out: Dict[str, Dict[str, str]] = {}
    for row in rows:
        code = str(row.get("company_code") or "").strip()
        if not code:
            continue
        if require_indexed_pass:
            status = str(row.get("index_status") or "").strip()
            if status != "indexed_pass":
                continue
        out[code] = row
    return out


def load_manifest_family_map(
    manifest_path: str,
) -> Dict[str, Set[str]]:
    """exclusion manifest → code→families（一行可多家族，如 000003）。"""
    rows, fieldnames = load_exclusion_csv_rows(manifest_path)
    kind = detect_exclusion_csv_kind(fieldnames)
    if kind != "exclusion_manifest":
        raise ValueError(f"expected_exclusion_manifest, got={kind}")
    mapping: Dict[str, Set[str]] = {}
    for row in rows:
        code = str(row.get("company_code") or "").strip()
        family = str(row.get("cohort_family") or "").strip()
        if not code or not family:
            continue
        if family not in POOL_EXCLUSION_FAMILIES:
            raise ValueError(f"unknown_exclusion_cohort_family: {family}")
        mapping.setdefault(code, set()).add(family)
    return mapping


def family_expected_harvest_status(families: Set[str]) -> Optional[str]:
    """
    按家族推导期望 harvest_status（slice1 ledger 语义）。
    partial7 → partial；empty_dividend3 → complete；仅 holdout9 → None（不强制）。
    """
    if "partial7" in families:
        return "partial"
    if "empty_dividend3" in families:
        return "complete"
    return None


def build_family_harvest_exclusion_rows(
    *,
    harvest_status: Dict[str, Dict[str, str]],
    pool_decisions: Dict[str, str],
    family_map: Dict[str, Set[str]],
    expected_excluded: Set[str],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """家族感知一致性矩阵行 + 汇总 checks。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    # 1) caveat10 每码：须 excluded + harvest 家族语义 + 出现在 manifest
    for code in sorted(expected_excluded):
        families = family_map.get(code, set())
        harvest = harvest_status.get(code)
        harvest_st = (harvest or {}).get("harvest_status", "")
        pool = pool_decisions.get(code, "")
        expected_st = family_expected_harvest_status(families)
        ok = True
        notes: List[str] = []
        if pool != "excluded":
            ok = False
            notes.append(f"pool_decision={pool or 'missing'}")
        if not harvest:
            ok = False
            notes.append("missing_harvest_row")
        elif expected_st and harvest_st != expected_st:
            ok = False
            notes.append(f"harvest_status={harvest_st} expected={expected_st}")
        if not families:
            ok = False
            notes.append("missing_manifest_family")
        if "partial7" in families and "empty_dividend3" in families:
            ok = False
            notes.append("conflicting_partial_and_empty_families")
        rows.append(
            {
                "check_id": f"family_excluded_{code}",
                "layer": "harvest_exclusion_family",
                "company_code": code,
                "expected": (
                    f"pool=excluded;harvest={expected_st or 'n/a'};"
                    f"families={','.join(sorted(families))}"
                ),
                "observed": (
                    f"pool={pool or 'n/a'};harvest={harvest_st or 'n/a'};"
                    f"families={','.join(sorted(families))}"
                ),
                "ok": "yes" if ok else "no",
                "notes": ";".join(notes) if notes else "ok",
            }
        )
        checks[f"family_excluded_{code}"] = ok

    # 2) complete pool 不得落在 caveat10
    complete_pool = {
        c for c, d in pool_decisions.items() if d == "included_complete_pool"
    }
    leak = sorted(complete_pool & expected_excluded)
    leak_ok = len(leak) == 0
    rows.append(
        {
            "check_id": "complete_pool_excludes_caveat10",
            "layer": "harvest_exclusion_family",
            "company_code": "*",
            "expected": "disjoint",
            "observed": f"leak_count={len(leak)}",
            "ok": "yes" if leak_ok else "no",
            "notes": ",".join(leak) if leak else "ok",
        }
    )
    checks["complete_pool_excludes_caveat10"] = leak_ok

    # 3) slice1 harvest 计数
    statuses = [
        str((harvest_status.get(c) or {}).get("harvest_status") or "")
        for c in harvest_status
    ]
    n_complete = sum(1 for s in statuses if s == "complete")
    n_partial = sum(1 for s in statuses if s == "partial")
    count_ok = (
        len(harvest_status) == EXPECTED_SLICE1_TOTAL
        and n_complete == EXPECTED_SLICE1_COMPLETE
        and n_partial == EXPECTED_SLICE1_PARTIAL
    )
    rows.append(
        {
            "check_id": "slice1_harvest_status_counts",
            "layer": "harvest_exclusion_family",
            "company_code": "*",
            "expected": (
                f"total={EXPECTED_SLICE1_TOTAL};"
                f"complete={EXPECTED_SLICE1_COMPLETE};"
                f"partial={EXPECTED_SLICE1_PARTIAL}"
            ),
            "observed": (
                f"total={len(harvest_status)};"
                f"complete={n_complete};partial={n_partial}"
            ),
            "ok": "yes" if count_ok else "no",
            "notes": "ok" if count_ok else "count_mismatch",
        }
    )
    checks["slice1_harvest_status_counts"] = count_ok

    # 4) empty3 虽 ledger=complete，不得进入 complete pool
    empty_in_pool = sorted(EXPECTED_SLICE1_EMPTY_DIVIDEND3 & complete_pool)
    empty_pool_ok = len(empty_in_pool) == 0 and all(
        pool_decisions.get(c) == "excluded" for c in EXPECTED_SLICE1_EMPTY_DIVIDEND3
    )
    rows.append(
        {
            "check_id": "empty3_excluded_despite_complete_ledger",
            "layer": "harvest_exclusion_family",
            "company_code": "*",
            "expected": "all_excluded_from_complete_pool",
            "observed": f"in_pool={','.join(empty_in_pool) or 'none'}",
            "ok": "yes" if empty_pool_ok else "no",
            "notes": "ok" if empty_pool_ok else "empty3_leaked_into_pool",
        }
    )
    checks["empty3_excluded_despite_complete_ledger"] = empty_pool_ok

    pool_count_ok = len(complete_pool) == EXPECTED_COMPLETE_POOL
    rows.append(
        {
            "check_id": "complete_pool_count_190",
            "layer": "harvest_exclusion_family",
            "company_code": "*",
            "expected": str(EXPECTED_COMPLETE_POOL),
            "observed": str(len(complete_pool)),
            "ok": "yes" if pool_count_ok else "no",
            "notes": "ok" if pool_count_ok else "pool_count_mismatch",
        }
    )
    checks["complete_pool_count_190"] = pool_count_ok

    return rows, checks


def build_dual_layer_cohort_rows(
    *,
    empty3_index: Dict[str, Dict[str, str]],
    partial7_index: Dict[str, Dict[str, str]],
    coverage_rows: Sequence[Dict[str, str]],
    expected_excluded: Set[str],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """dual-layer cohort 工具层：索引并集 ↔ caveat10 ↔ coverage。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    empty_codes = set(empty3_index)
    partial_codes = set(partial7_index)
    union = empty_codes | partial_codes

    empty_ok = empty_codes == set(EXPECTED_SLICE1_EMPTY_DIVIDEND3)
    rows.append(
        {
            "check_id": "empty3_index_codes",
            "layer": "dual_layer_cohort",
            "company_code": "*",
            "expected": ",".join(sorted(EXPECTED_SLICE1_EMPTY_DIVIDEND3)),
            "observed": ",".join(sorted(empty_codes)),
            "ok": "yes" if empty_ok else "no",
            "notes": "ok" if empty_ok else "empty3_index_mismatch",
        }
    )
    checks["empty3_index_codes"] = empty_ok

    partial_ok = partial_codes == set(EXPECTED_SLICE1_PARTIAL7)
    rows.append(
        {
            "check_id": "partial7_index_codes",
            "layer": "dual_layer_cohort",
            "company_code": "*",
            "expected": ",".join(sorted(EXPECTED_SLICE1_PARTIAL7)),
            "observed": ",".join(sorted(partial_codes)),
            "ok": "yes" if partial_ok else "no",
            "notes": "ok" if partial_ok else "partial7_index_mismatch",
        }
    )
    checks["partial7_index_codes"] = partial_ok

    overlap = empty_codes & partial_codes
    disjoint_ok = len(overlap) == 0
    rows.append(
        {
            "check_id": "empty3_partial7_indexes_disjoint",
            "layer": "dual_layer_cohort",
            "company_code": "*",
            "expected": "disjoint",
            "observed": f"overlap={','.join(sorted(overlap)) or 'none'}",
            "ok": "yes" if disjoint_ok else "no",
            "notes": "ok" if disjoint_ok else "index_overlap",
        }
    )
    checks["empty3_partial7_indexes_disjoint"] = disjoint_ok

    union_ok = union == expected_excluded
    rows.append(
        {
            "check_id": "dual_layer_union_equals_caveat10",
            "layer": "dual_layer_cohort",
            "company_code": "*",
            "expected": f"n={len(expected_excluded)}",
            "observed": f"n={len(union)}",
            "ok": "yes" if union_ok else "no",
            "notes": (
                "ok"
                if union_ok
                else (
                    f"missing={','.join(sorted(expected_excluded - union))};"
                    f"extra={','.join(sorted(union - expected_excluded))}"
                )
            ),
        }
    )
    checks["dual_layer_union_equals_caveat10"] = union_ok

    # 每码 gate / rules
    for code, row in sorted({**empty3_index, **partial7_index}.items()):
        gate = str(row.get("dual_layer_audit_gate") or "").strip()
        rules = str(row.get("rules_all_pass") or "").strip().lower()
        status = str(row.get("index_status") or "").strip()
        ok = gate == "PASS_OFFLINE" and rules == "yes" and status == "indexed_pass"
        rows.append(
            {
                "check_id": f"dual_layer_gate_{code}",
                "layer": "dual_layer_cohort",
                "company_code": code,
                "expected": "PASS_OFFLINE;rules=yes;indexed_pass",
                "observed": f"{gate};rules={rules};{status}",
                "ok": "yes" if ok else "no",
                "notes": "ok" if ok else "gate_or_rules_fail",
            }
        )
        checks[f"dual_layer_gate_{code}"] = ok

    # coverage：all_caveats 10/10
    coverage_by_family = {
        str(r.get("caveat_family") or "").strip(): r for r in coverage_rows
    }
    all_row = coverage_by_family.get("all_caveats") or {}
    indexed_pass = str(all_row.get("indexed_pass_count") or "").strip()
    expected_count = str(all_row.get("expected_count") or "").strip()
    index_status = str(all_row.get("index_status") or "").strip()
    coverage_ok = (
        indexed_pass == "10"
        and expected_count == "10"
        and index_status == "indexed_pass"
        and "empty_dividend" in coverage_by_family
        and "partial" in coverage_by_family
    )
    rows.append(
        {
            "check_id": "cohort_coverage_10_of_10",
            "layer": "dual_layer_cohort",
            "company_code": "*",
            "expected": "all_caveats=10/10 indexed_pass",
            "observed": (
                f"indexed_pass={indexed_pass};expected={expected_count};"
                f"status={index_status};families={sorted(coverage_by_family)}"
            ),
            "ok": "yes" if coverage_ok else "no",
            "notes": "ok" if coverage_ok else "coverage_mismatch",
        }
    )
    checks["cohort_coverage_10_of_10"] = coverage_ok

    return rows, checks


def build_manifest_reconcile_rows(
    *,
    family_map: Dict[str, Set[str]],
    pool_decisions: Dict[str, str],
    harvest_codes: Set[str],
    expected_excluded: Set[str],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """manifest ↔ reconcile ↔ slice1 universe 一致性。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    # manifest 中 partial7+empty3 并集须等于 caveat10
    fam_partial = {c for c, fs in family_map.items() if "partial7" in fs}
    fam_empty = {c for c, fs in family_map.items() if "empty_dividend3" in fs}
    fam_holdout = {c for c, fs in family_map.items() if "holdout9" in fs}
    core = fam_partial | fam_empty
    core_ok = core == expected_excluded
    rows.append(
        {
            "check_id": "manifest_core_equals_caveat10",
            "layer": "manifest_reconcile",
            "company_code": "*",
            "expected": f"n={len(expected_excluded)}",
            "observed": (
                f"partial7={len(fam_partial)};empty3={len(fam_empty)};"
                f"union={len(core)}"
            ),
            "ok": "yes" if core_ok else "no",
            "notes": "ok" if core_ok else "manifest_core_mismatch",
        }
    )
    checks["manifest_core_equals_caveat10"] = core_ok

    holdout_ok = fam_holdout == set(EXPECTED_HOLDOUT9)
    rows.append(
        {
            "check_id": "holdout9_manifest_set",
            "layer": "manifest_reconcile",
            "company_code": "*",
            "expected": f"n={len(EXPECTED_HOLDOUT9)}",
            "observed": f"n={len(fam_holdout)}",
            "ok": "yes" if holdout_ok else "no",
            "notes": (
                "ok"
                if holdout_ok
                else (
                    f"missing={','.join(sorted(set(EXPECTED_HOLDOUT9) - fam_holdout))};"
                    f"extra={','.join(sorted(fam_holdout - set(EXPECTED_HOLDOUT9)))}"
                )
            ),
        }
    )
    checks["holdout9_manifest_set"] = holdout_ok

    # holdout 中除与 partial7 重叠外，不得在 slice1 harvest
    holdout_only = fam_holdout - fam_partial
    holdout_in_slice1 = sorted(holdout_only & harvest_codes)
    holdout_isolated_ok = len(holdout_in_slice1) == 0
    rows.append(
        {
            "check_id": "holdout9_outside_slice1_except_partial_overlap",
            "layer": "manifest_reconcile",
            "company_code": "*",
            "expected": "no_holdout_only_in_slice1",
            "observed": f"in_slice1={','.join(holdout_in_slice1) or 'none'}",
            "ok": "yes" if holdout_isolated_ok else "no",
            "notes": "ok" if holdout_isolated_ok else "holdout_inflates_slice1",
        }
    )
    checks["holdout9_outside_slice1_except_partial_overlap"] = holdout_isolated_ok

    # manifest 全码与 slice1 相交 = caveat10（含 000003 的 holdout∩partial）；
    # 不得因 holdout9 其余码膨胀 slice1 排除集
    inflated = set(family_map) & harvest_codes
    inflated_ok = inflated == expected_excluded
    rows.append(
        {
            "check_id": "slice1_manifest_hits_equal_caveat10",
            "layer": "manifest_reconcile",
            "company_code": "*",
            "expected": f"n={len(expected_excluded)}",
            "observed": f"n={len(inflated)} codes={','.join(sorted(inflated))}",
            "ok": "yes" if inflated_ok else "no",
            "notes": "ok" if inflated_ok else "manifest_slice1_hit_mismatch",
        }
    )
    checks["slice1_manifest_hits_equal_caveat10"] = inflated_ok

    excluded_recon = {
        c for c, d in pool_decisions.items() if d == "excluded"
    }
    recon_ok = excluded_recon == expected_excluded
    rows.append(
        {
            "check_id": "reconcile_excluded_equals_caveat10",
            "layer": "manifest_reconcile",
            "company_code": "*",
            "expected": f"n={len(expected_excluded)}",
            "observed": f"n={len(excluded_recon)}",
            "ok": "yes" if recon_ok else "no",
            "notes": "ok" if recon_ok else "reconcile_excluded_mismatch",
        }
    )
    checks["reconcile_excluded_equals_caveat10"] = recon_ok

    return rows, checks


def fingerprint_status_csv(path: str) -> Dict[str, Any]:
    """只读 CSV 结构指纹（行数 · 状态分布 · sha256）。"""
    rows = load_csv_rows(path)
    codes = [str(r.get("company_code") or "").strip() for r in rows]
    statuses = [str(r.get("harvest_status") or "").strip() for r in rows]
    status_counts: Dict[str, int] = {}
    for s in statuses:
        status_counts[s] = status_counts.get(s, 0) + 1
    raw = open(path, "rb").read()
    content_sha = hashlib.sha256(raw).hexdigest()
    payload = {
        "row_count": len(rows),
        "unique_codes": len({c for c in codes if c}),
        "empty_code_rows": sum(1 for c in codes if not c),
        "status_counts": status_counts,
        "content_sha256": content_sha,
        "path": path,
    }
    canon = json.dumps(
        {
            "row_count": payload["row_count"],
            "unique_codes": payload["unique_codes"],
            "empty_code_rows": payload["empty_code_rows"],
            "status_counts": dict(sorted(status_counts.items())),
            "content_sha256": content_sha,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    payload["fingerprint_sha256"] = hashlib.sha256(
        canon.encode("utf-8")
    ).hexdigest()
    return payload


def build_harvest_863_structural_rows(
    *,
    fingerprint: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], Dict[str, bool]]:
    """863 harvest ledger 更大 mock：只读结构核验。"""
    rows: List[Dict[str, str]] = []
    checks: Dict[str, bool] = {}

    row_ok = fingerprint.get("row_count") == EXPECTED_863_COMPLETE
    unique_ok = fingerprint.get("unique_codes") == EXPECTED_863_COMPLETE
    empty_ok = fingerprint.get("empty_code_rows") == 0
    status_counts = fingerprint.get("status_counts") or {}
    complete_ok = status_counts.get("complete") == EXPECTED_863_COMPLETE
    fp_ok = bool(fingerprint.get("fingerprint_sha256")) and bool(
        fingerprint.get("content_sha256")
    )

    specs = [
        ("harvest_863_row_count", EXPECTED_863_COMPLETE, fingerprint.get("row_count")),
        (
            "harvest_863_unique_codes",
            EXPECTED_863_COMPLETE,
            fingerprint.get("unique_codes"),
        ),
        ("harvest_863_no_empty_codes", 0, fingerprint.get("empty_code_rows")),
        (
            "harvest_863_all_complete",
            EXPECTED_863_COMPLETE,
            status_counts.get("complete"),
        ),
    ]
    for check_id, expected, observed in specs:
        ok = expected == observed
        rows.append(
            {
                "check_id": check_id,
                "layer": "harvest_863_structural",
                "company_code": "*",
                "expected": str(expected),
                "observed": str(observed),
                "ok": "yes" if ok else "no",
                "notes": "ok" if ok else "mismatch",
            }
        )
        checks[check_id] = ok

    rows.append(
        {
            "check_id": "harvest_863_fingerprint_present",
            "layer": "harvest_863_structural",
            "company_code": "*",
            "expected": "nonempty_sha256",
            "observed": str(fingerprint.get("fingerprint_sha256") or "")[:16],
            "ok": "yes" if fp_ok else "no",
            "notes": "ok" if fp_ok else "missing_fingerprint",
        }
    )
    checks["harvest_863_fingerprint_present"] = fp_ok
    checks["harvest_863_structural_all"] = all(
        [
            row_ok,
            unique_ok,
            empty_ok,
            complete_ok,
            fp_ok,
        ]
    )
    return rows, checks


def write_consistency_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CONSISTENCY_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in CONSISTENCY_MATRIX_FIELDS})


def run_harvest_exclusion_dual_layer_consistency(
    *,
    paths: ConsistencyPaths = ConsistencyPaths(),
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 C-FM-03 全层一致性 QA（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    out_root = assert_consistency_output_root(paths.output_root_rel, base_dir=base_dir)

    # 只读输入
    harvest = load_harvest_status_map(
        SLICE1_HARVEST_ROOT_REL
        if paths.slice1_harvest_status_rel == SLICE1_HARVEST_STATUS_REL
        else os.path.dirname(os.path.dirname(paths.slice1_harvest_status_rel)),
        base_dir=base_dir,
    )
    # 若自定义 status 路径，直接读该文件
    if paths.slice1_harvest_status_rel != SLICE1_HARVEST_STATUS_REL:
        status_path = _abs(paths.slice1_harvest_status_rel, base_dir=base_dir)
        harvest = {}
        for row in load_csv_rows(status_path):
            code = str(row.get("company_code") or "").strip()
            if code:
                harvest[code] = row

    pool = load_reconcile_pool_decisions(
        paths.exclusion_reconcile_rel, base_dir=base_dir
    )
    family_map = load_manifest_family_map(
        _abs(paths.exclusion_manifest_rel, base_dir=base_dir)
    )
    empty3_index = load_dual_layer_index_codes(
        _abs(paths.empty3_index_rel, base_dir=base_dir)
    )
    partial7_index = load_dual_layer_index_codes(
        _abs(paths.partial7_index_rel, base_dir=base_dir)
    )
    coverage_rows = load_csv_rows(_abs(paths.cohort_coverage_rel, base_dir=base_dir))
    fp_863 = fingerprint_status_csv(
        _abs(paths.harvest_863_status_rel, base_dir=base_dir)
    )

    expected_excluded = set(EXPECTED_SLICE1_EXCLUDED_UNIQUE)
    fam_rows, fam_checks = build_family_harvest_exclusion_rows(
        harvest_status=harvest,
        pool_decisions=pool,
        family_map=family_map,
        expected_excluded=expected_excluded,
    )
    dl_rows, dl_checks = build_dual_layer_cohort_rows(
        empty3_index=empty3_index,
        partial7_index=partial7_index,
        coverage_rows=coverage_rows,
        expected_excluded=expected_excluded,
    )
    mr_rows, mr_checks = build_manifest_reconcile_rows(
        family_map=family_map,
        pool_decisions=pool,
        harvest_codes=set(harvest),
        expected_excluded=expected_excluded,
    )
    h863_rows, h863_checks = build_harvest_863_structural_rows(fingerprint=fp_863)

    matrix = fam_rows + dl_rows + mr_rows + h863_rows
    all_checks = {**fam_checks, **dl_checks, **mr_checks, **h863_checks}
    # 汇总层 gate 用关键检查键，避免 10× dual_layer_gate_* 噪音进 cohort_gates
    layer_gates = {
        "harvest_exclusion_family": (
            "PASS_OFFLINE"
            if all(
                v
                for k, v in fam_checks.items()
                if not k.startswith("family_excluded_") or v is not None
            )
            and all(fam_checks.values())
            else "FAIL_REVIEW_REQUIRED"
        ),
        "dual_layer_cohort": (
            "PASS_OFFLINE"
            if all(dl_checks.values())
            else "FAIL_REVIEW_REQUIRED"
        ),
        "manifest_reconcile": (
            "PASS_OFFLINE"
            if all(mr_checks.values())
            else "FAIL_REVIEW_REQUIRED"
        ),
        "harvest_863_structural": (
            "PASS_OFFLINE"
            if h863_checks.get("harvest_863_structural_all")
            else "FAIL_REVIEW_REQUIRED"
        ),
    }
    overall = (
        "PASS_OFFLINE"
        if all(g == "PASS_OFFLINE" for g in layer_gates.values())
        else "FAIL_REVIEW_REQUIRED"
    )

    matrix_path = os.path.join(out_root, "consistency_matrix.csv")
    write_consistency_matrix_csv(matrix, matrix_path)

    fp_path = os.path.join(out_root, "harvest_863_structural_fingerprint.json")
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
                "fingerprint": {
                    k: v
                    for k, v in fp_863.items()
                    if k != "path"
                },
                "source_rel": _rel(
                    paths.harvest_863_status_rel, base_dir=base_dir
                ),
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
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "gate": overall,
        "layer_gates": layer_gates,
        "checks": all_checks,
        "fail_count": fail_count,
        "matrix_rows": len(matrix),
        "output_root": _rel(out_root, base_dir=base_dir),
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "fingerprint_863_path": _rel(fp_path, base_dir=base_dir),
        "fingerprint_863": {
            k: v for k, v in fp_863.items() if k != "path"
        },
        "inputs": {
            "slice1_harvest_status": paths.slice1_harvest_status_rel,
            "harvest_863_status": paths.harvest_863_status_rel,
            "exclusion_manifest": paths.exclusion_manifest_rel,
            "exclusion_reconcile": paths.exclusion_reconcile_rel,
            "empty3_index": paths.empty3_index_rel,
            "partial7_index": paths.partial7_index_rel,
            "cohort_coverage": paths.cohort_coverage_rel,
        },
        "mock_root_is_isolated": is_allowed_mock_test_cleanup_path(
            out_root, base_dir=base_dir
        ),
    }
