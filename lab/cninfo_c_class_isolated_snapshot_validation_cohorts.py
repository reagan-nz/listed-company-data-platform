"""
CNINFO C-class — 隔离 snapshot 校验 cohort 与 dry-run lineage 自动化（离线）。

在 validation/_mock_* 根上对多 cohort 做：
  1) 隔离 dry-run（复用 batch run_dry_run + FM-01 指纹）
  2) lineage 核验：filtered universe ↔ snapshot status ↔ harvest ledger ↔ exclusion
  3) caveat10 负对照：排除码不得出现在 included dry-run status

禁止：CNINFO live · production EXECUTE · 写生产 snapshot 根 · verified 声称。
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from build_cninfo_c_class_snapshot_batch import (  # noqa: E402
    load_universe_yaml,
    reset_snapshot_batch_paths,
    run_dry_run,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL,
    assert_safe_c_class_snapshot_dryrun_write_root,
    fingerprint_isolated_snapshot_dryrun,
    is_allowed_mock_test_cleanup_path,
    normalize_cleanup_path,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    filter_universe_with_exclusion_csv,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
)

SLICE1_UNIVERSE_YAML_REL = "lab/eval_companies_c_class_fuller_market_slice1_200.yaml"
SLICE1_EXCLUSION_RECONCILE_REL = (
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv"
)
SLICE1_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class/fuller_market_slice1_200"
SLICE1_190_OUTPUT_ROOT_REL = (
    "outputs/validation/_mock_c_fm02_slice1_190_validation_cohort"
)
STANDARD_ISOLATED_OUTPUT_ROOT_REL = DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL

COHORT_SLICE1_190 = "slice1_190_included"
COHORT_CAVEAT10_NEG = "slice1_caveat10_negative_control"
COHORT_STANDARD_ISOLATED = "standard_isolated_fingerprint"

LINEAGE_MATRIX_FIELDS = [
    "cohort_id",
    "company_code",
    "company_name",
    "role",
    "in_universe",
    "in_dryrun_status",
    "pool_decision",
    "harvest_status",
    "harvest_row_present",
    "lineage_ok",
    "notes",
]


@dataclass
class CohortSpec:
    """隔离 snapshot 校验 cohort 规格。"""

    cohort_id: str
    description: str
    universe_yaml_rel: str
    exclusion_csv_rel: Optional[str]
    harvest_root_rel: str
    output_root_rel: str
    expected_included_count: int
    expected_excluded_codes: frozenset = field(default_factory=frozenset)
    run_dryrun: bool = True
    fingerprint_repro: bool = True


DEFAULT_COHORTS: Tuple[CohortSpec, ...] = (
    CohortSpec(
        cohort_id=COHORT_SLICE1_190,
        description=(
            "slice1 fuller-market 200 经 exclusion 过滤后的 190 included complete pool；"
            "隔离 dry-run + harvest/exclusion lineage"
        ),
        universe_yaml_rel=SLICE1_UNIVERSE_YAML_REL,
        exclusion_csv_rel=SLICE1_EXCLUSION_RECONCILE_REL,
        harvest_root_rel=SLICE1_HARVEST_ROOT_REL,
        output_root_rel=SLICE1_190_OUTPUT_ROOT_REL,
        expected_included_count=190,
        expected_excluded_codes=EXPECTED_SLICE1_EXCLUDED_UNIQUE,
        run_dryrun=True,
        fingerprint_repro=True,
    ),
    CohortSpec(
        cohort_id=COHORT_STANDARD_ISOLATED,
        description=(
            "C-FM-01 标准隔离 dry-run 根只读指纹核验（不重跑 863 dry-run）；"
            "确认隔离产物与指纹可复算"
        ),
        universe_yaml_rel="lab/eval_companies_c_class_harvest_863_non_bse.yaml",
        exclusion_csv_rel=None,
        harvest_root_rel="outputs/harvest/cninfo_c_class",
        output_root_rel=STANDARD_ISOLATED_OUTPUT_ROOT_REL,
        expected_included_count=0,  # 由 status 行数推导
        expected_excluded_codes=frozenset(),
        run_dryrun=False,
        fingerprint_repro=False,
    ),
)


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


def assert_isolated_validation_output_root(
    output_root: str, *, base_dir: str = BASE_DIR
) -> str:
    """
    cohort 写根守卫：必须在 outputs/validation/ 且含 _mock_* 段；
    同时走生产 snapshot dry-run 写根拒绝。
    """
    norm = normalize_cleanup_path(output_root, base_dir=base_dir)
    validation_root = normalize_cleanup_path("outputs/validation", base_dir=base_dir)
    if not (norm == validation_root or norm.startswith(validation_root + os.sep)):
        raise RuntimeError(
            "COHORT_ROOT_NOT_UNDER_VALIDATION: "
            f"output-root 必须在 outputs/validation/ 下，收到: {_rel(norm, base_dir=base_dir)}"
        )
    if not is_allowed_mock_test_cleanup_path(norm, base_dir=base_dir):
        raise RuntimeError(
            "COHORT_ROOT_MOCK_PREFIX_REQUIRED: "
            f"output-root 路径段必须含 _mock_*，收到: {_rel(norm, base_dir=base_dir)}"
        )
    return assert_safe_c_class_snapshot_dryrun_write_root(
        norm, base_dir=base_dir, allow_production_scaffold=False
    )


def load_harvest_status_map(
    harvest_root: str, *, base_dir: str = BASE_DIR
) -> Dict[str, Dict[str, str]]:
    """读取 harvest company_harvest_status.csv → code→row。"""
    root = _abs(harvest_root, base_dir=base_dir)
    path = os.path.join(root, "quality", "company_harvest_status.csv")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"harvest_status_missing: {_rel(path, base_dir=base_dir)}")
    out: Dict[str, Dict[str, str]] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            code = str(row.get("company_code") or "").strip()
            if code:
                out[code] = dict(row)
    return out


def load_dryrun_status_map(
    output_root: str, *, base_dir: str = BASE_DIR
) -> Dict[str, Dict[str, str]]:
    """读取隔离 dry-run company_snapshot_status.csv → code→row。"""
    root = _abs(output_root, base_dir=base_dir)
    path = os.path.join(root, "quality", "company_snapshot_status.csv")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"dryrun_status_missing: {_rel(path, base_dir=base_dir)}")
    out: Dict[str, Dict[str, str]] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            code = str(row.get("company_code") or "").strip()
            if code:
                out[code] = dict(row)
    return out


def load_reconcile_pool_decisions(
    exclusion_csv: str, *, base_dir: str = BASE_DIR
) -> Dict[str, str]:
    """exclusion reconcile → code→pool_decision。"""
    path = _abs(exclusion_csv, base_dir=base_dir)
    decisions: Dict[str, str] = {}
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            code = str(row.get("company_code") or "").strip()
            if not code:
                continue
            decisions[code] = str(row.get("pool_decision") or "").strip()
    return decisions


def prepare_included_universe(
    *,
    universe_yaml: str,
    exclusion_csv: str,
    output_root: str,
    base_dir: str = BASE_DIR,
) -> Tuple[str, Set[str], Set[str], int]:
    """
    按 exclusion 过滤 universe，写出 mock 根下 filtered YAML。
    返回 (filtered_yaml_path, included_codes, excluded_codes, source_count)。
    """
    companies, _meta = load_universe_yaml(_abs(universe_yaml, base_dir=base_dir))
    result = filter_universe_with_exclusion_csv(
        companies, _abs(exclusion_csv, base_dir=base_dir)
    )
    included_codes = {
        str(c.get("company_code") or "").strip() for c in result.included
    }
    included_codes.discard("")
    os.makedirs(output_root, exist_ok=True)
    filtered_path = os.path.join(output_root, "filtered_universe_included.yaml")
    # 最小 YAML 写出（与 batch exclusion 过滤语义对齐）
    payload = {
        "version": "c-fm02-isolated-validation-cohort-v1",
        "generated_at": _utc_now_iso(),
        "purpose": "isolated_snapshot_validation_cohort_dryrun",
        "source_universe": _rel(universe_yaml, base_dir=base_dir),
        "exclusion_csv": _rel(exclusion_csv, base_dir=base_dir),
        "company_count": len(result.included),
        "excluded_unique_count": len(result.excluded_codes),
        "execute_production_snapshot_rebuild": False,
        "companies": [
            {
                "stock_code": c["company_code"],
                "company_code": c["company_code"],
                "company_name": c.get("company_name") or "",
                "board": c.get("board") or "",
            }
            for c in result.included
        ],
    }
    import yaml  # 局部导入，避免模块顶层依赖顺序问题

    with open(filtered_path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(payload, fh, allow_unicode=True, sort_keys=False)
    return filtered_path, included_codes, set(result.excluded_codes), len(companies)


def build_lineage_matrix_rows(
    *,
    cohort_id: str,
    included_codes: Set[str],
    excluded_codes: Set[str],
    dryrun_status: Dict[str, Dict[str, str]],
    harvest_status: Dict[str, Dict[str, str]],
    pool_decisions: Dict[str, str],
    universe_names: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """构造 lineage 矩阵行（included 正例 + excluded 负对照）。"""
    names = universe_names or {}
    rows: List[Dict[str, str]] = []

    for code in sorted(included_codes):
        dry = dryrun_status.get(code)
        harvest = harvest_status.get(code)
        pool = pool_decisions.get(code, "")
        harvest_st = (harvest or {}).get("harvest_status", "")
        in_status = dry is not None
        harvest_present = harvest is not None
        # included 正例：须在 status、须有 harvest 行、pool 非 excluded、harvest 宜为 complete
        notes: List[str] = []
        lineage_ok = True
        if not in_status:
            lineage_ok = False
            notes.append("missing_dryrun_status")
        if pool == "excluded":
            lineage_ok = False
            notes.append("pool_decision_excluded")
        if not harvest_present:
            lineage_ok = False
            notes.append("missing_harvest_row")
        elif harvest_st and harvest_st != "complete":
            # included complete pool 期望 complete；非 complete 记失败
            lineage_ok = False
            notes.append(f"harvest_status={harvest_st}")
        if code in excluded_codes:
            lineage_ok = False
            notes.append("code_in_excluded_set")
        rows.append(
            {
                "cohort_id": cohort_id,
                "company_code": code,
                "company_name": names.get(code)
                or (dry or {}).get("company_name", "")
                or (harvest or {}).get("company_name", ""),
                "role": "included",
                "in_universe": "yes",
                "in_dryrun_status": "yes" if in_status else "no",
                "pool_decision": pool or "n/a",
                "harvest_status": harvest_st or "",
                "harvest_row_present": "yes" if harvest_present else "no",
                "lineage_ok": "yes" if lineage_ok else "no",
                "notes": ";".join(notes) if notes else "ok",
            }
        )

    for code in sorted(excluded_codes):
        dry = dryrun_status.get(code)
        harvest = harvest_status.get(code)
        pool = pool_decisions.get(code, "")
        in_status = dry is not None
        # 负对照：排除码不得出现在 included dry-run status
        lineage_ok = not in_status
        notes = []
        if in_status:
            notes.append("excluded_code_leaked_into_dryrun_status")
        if pool and pool != "excluded":
            notes.append(f"unexpected_pool_decision={pool}")
            lineage_ok = False
        if not pool:
            notes.append("missing_pool_decision")
        rows.append(
            {
                "cohort_id": cohort_id,
                "company_code": code,
                "company_name": names.get(code)
                or (harvest or {}).get("company_name", ""),
                "role": "excluded_negative_control",
                "in_universe": "no",
                "in_dryrun_status": "yes" if in_status else "no",
                "pool_decision": pool or "n/a",
                "harvest_status": (harvest or {}).get("harvest_status", ""),
                "harvest_row_present": "yes" if harvest is not None else "no",
                "lineage_ok": "yes" if lineage_ok else "no",
                "notes": ";".join(notes) if notes else "ok_absent_from_dryrun",
            }
        )
    return rows


def summarize_lineage_checks(
    matrix_rows: Sequence[Dict[str, str]],
    *,
    expected_included_count: int,
    expected_excluded_codes: Set[str],
) -> Dict[str, Any]:
    """从 lineage 矩阵汇总检查项。"""
    included = [r for r in matrix_rows if r["role"] == "included"]
    excluded = [r for r in matrix_rows if r["role"] == "excluded_negative_control"]
    included_ok = all(r["lineage_ok"] == "yes" for r in included)
    excluded_ok = all(r["lineage_ok"] == "yes" for r in excluded)
    excluded_codes_seen = {r["company_code"] for r in excluded}
    expected_set = set(expected_excluded_codes)
    # 仅当期望集覆盖完整 caveat 家族时强制家族覆盖检查
    require_partial7 = bool(EXPECTED_SLICE1_PARTIAL7 & expected_set) and (
        EXPECTED_SLICE1_PARTIAL7 <= expected_set
    )
    require_empty3 = bool(EXPECTED_SLICE1_EMPTY_DIVIDEND3 & expected_set) and (
        EXPECTED_SLICE1_EMPTY_DIVIDEND3 <= expected_set
    )
    checks = {
        "included_count_matches": len(included) == expected_included_count,
        "included_lineage_all_ok": included_ok and len(included) > 0,
        "excluded_negative_control_all_ok": excluded_ok
        and excluded_codes_seen == expected_set,
        "excluded_count_matches": len(excluded) == len(expected_set),
        "no_lineage_failures": all(r["lineage_ok"] == "yes" for r in matrix_rows),
        "partial7_covered": (
            EXPECTED_SLICE1_PARTIAL7 <= excluded_codes_seen
            if require_partial7
            else True
        ),
        "empty_dividend3_covered": (
            EXPECTED_SLICE1_EMPTY_DIVIDEND3 <= excluded_codes_seen
            if require_empty3
            else True
        ),
    }
    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"
    return {
        "included_count": len(included),
        "excluded_control_count": len(excluded),
        "lineage_fail_count": sum(1 for r in matrix_rows if r["lineage_ok"] != "yes"),
        "checks": checks,
        "gate": gate,
    }


def write_lineage_matrix_csv(rows: Sequence[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LINEAGE_MATRIX_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in LINEAGE_MATRIX_FIELDS})


def run_cohort_dryrun_with_repro(
    *,
    universe_path: str,
    output_root: str,
    harvest_root: str,
    fingerprint_repro: bool = True,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """在隔离根执行 dry-run；可选连续两次比对指纹。"""
    safe_out = assert_isolated_validation_output_root(output_root, base_dir=base_dir)
    report_path = os.path.join(safe_out, "dryrun_report.csv")
    summary_path = os.path.join(safe_out, "dryrun_summary.md")
    runs: List[Dict[str, Any]] = []
    iterations = 2 if fingerprint_repro else 1
    last_result: Dict[str, Any] = {}
    for i in range(iterations):
        reset_snapshot_batch_paths()
        last_result = run_dry_run(
            universe_path=universe_path,
            out_dir=safe_out,
            harvest_root=_abs(harvest_root, base_dir=base_dir),
            report_path=report_path,
            summary_path=summary_path,
            resume=False,
            force=False,
            allow_production_scaffold=False,
        )
        fp = last_result.get("dryrun_fingerprint") or {}
        runs.append(
            {
                "run_index": i + 1,
                "gate": last_result.get("gate"),
                "company_count": (last_result.get("validation") or {}).get(
                    "company_count"
                ),
                "content_sha256": fp.get("content_sha256", ""),
                "fingerprint_sha256": fp.get("fingerprint_sha256", ""),
            }
        )
    reproducible = True
    if fingerprint_repro and len(runs) == 2:
        reproducible = (
            runs[0]["content_sha256"] == runs[1]["content_sha256"]
            and runs[0]["fingerprint_sha256"] == runs[1]["fingerprint_sha256"]
        )
    return {
        "dry_result": last_result,
        "output_root": safe_out,
        "runs": runs,
        "reproducible": reproducible,
        "fingerprint": (last_result.get("dryrun_fingerprint") or {}),
    }


def validate_standard_isolated_fingerprint_cohort(
    *,
    output_root_rel: str = STANDARD_ISOLATED_OUTPUT_ROOT_REL,
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """
    只读核验 C-FM-01 标准隔离 dry-run 根：产物存在 + 指纹可复算。
    不重跑 863 dry-run（避免低价值重复 wall）。
    """
    root = assert_isolated_validation_output_root(output_root_rel, base_dir=base_dir)
    status_path = os.path.join(root, "quality", "company_snapshot_status.csv")
    report_path = os.path.join(root, "dryrun_report.csv")
    summary_path = os.path.join(root, "dryrun_summary.md")
    present = {
        "status_csv": os.path.isfile(status_path),
        "report_csv": os.path.isfile(report_path),
        "summary_md": os.path.isfile(summary_path),
    }
    status_rows = 0
    if present["status_csv"]:
        with open(status_path, encoding="utf-8", newline="") as fh:
            status_rows = sum(1 for _ in csv.DictReader(fh))
    fp = fingerprint_isolated_snapshot_dryrun(
        root,
        base_dir=base_dir,
        company_count=status_rows,
    )
    checks = {
        "artifacts_present": all(present.values()),
        "status_rows_positive": status_rows > 0,
        "fingerprint_nonempty": bool(fp.get("fingerprint_sha256")),
        "content_sha256_nonempty": bool(fp.get("content_sha256")),
        "cninfo_calls_zero": fp.get("cninfo_calls") == 0,
        "execute_flag_false": fp.get("execute_production_snapshot_rebuild") is False,
    }
    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"
    return {
        "cohort_id": COHORT_STANDARD_ISOLATED,
        "output_root": _rel(root, base_dir=base_dir),
        "status_rows": status_rows,
        "files_present": present,
        "fingerprint": fp,
        "checks": checks,
        "gate": gate,
        "run_dryrun": False,
    }


def run_slice1_190_validation_cohort(
    *,
    cohort: CohortSpec = DEFAULT_COHORTS[0],
    base_dir: str = BASE_DIR,
) -> Dict[str, Any]:
    """执行 slice1_190 隔离 dry-run + lineage + caveat10 负对照。"""
    out_root = assert_isolated_validation_output_root(
        cohort.output_root_rel, base_dir=base_dir
    )
    if not cohort.exclusion_csv_rel:
        raise RuntimeError("slice1_190 cohort requires exclusion_csv_rel")

    filtered_path, included_codes, excluded_codes, source_count = (
        prepare_included_universe(
            universe_yaml=cohort.universe_yaml_rel,
            exclusion_csv=cohort.exclusion_csv_rel,
            output_root=out_root,
            base_dir=base_dir,
        )
    )
    # 以权威 caveat10 集合为准（与 reconcile 交叉）
    expected_excluded = set(cohort.expected_excluded_codes) or set(excluded_codes)
    dry_bundle = run_cohort_dryrun_with_repro(
        universe_path=filtered_path,
        output_root=out_root,
        harvest_root=cohort.harvest_root_rel,
        fingerprint_repro=cohort.fingerprint_repro,
        base_dir=base_dir,
    )
    dryrun_status = load_dryrun_status_map(out_root, base_dir=base_dir)
    harvest_status = load_harvest_status_map(
        cohort.harvest_root_rel, base_dir=base_dir
    )
    pool_decisions = load_reconcile_pool_decisions(
        cohort.exclusion_csv_rel, base_dir=base_dir
    )
    companies, _ = load_universe_yaml(_abs(cohort.universe_yaml_rel, base_dir=base_dir))
    names = {
        str(c.get("company_code") or "").strip(): str(c.get("company_name") or "")
        for c in companies
    }

    matrix = build_lineage_matrix_rows(
        cohort_id=cohort.cohort_id,
        included_codes=included_codes,
        excluded_codes=expected_excluded,
        dryrun_status=dryrun_status,
        harvest_status=harvest_status,
        pool_decisions=pool_decisions,
        universe_names=names,
    )
    # 负对照 cohort 行复用同一矩阵（标注 cohort_id 变体便于索引）
    neg_rows = []
    for row in matrix:
        if row["role"] == "excluded_negative_control":
            cloned = dict(row)
            cloned["cohort_id"] = COHORT_CAVEAT10_NEG
            neg_rows.append(cloned)
    lineage_summary = summarize_lineage_checks(
        matrix,
        expected_included_count=cohort.expected_included_count,
        expected_excluded_codes=expected_excluded,
    )
    checks = dict(lineage_summary["checks"])
    checks["fingerprint_reproducible"] = bool(dry_bundle["reproducible"])
    checks["dryrun_universe_ok"] = bool(
        (dry_bundle["dry_result"] or {}).get("universe_ok")
    )
    checks["source_universe_200"] = source_count == 200
    checks["excluded_codes_match_filter"] = expected_excluded <= excluded_codes
    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"

    matrix_path = os.path.join(out_root, "cohort_lineage_matrix.csv")
    write_lineage_matrix_csv(matrix + neg_rows, matrix_path)

    return {
        "cohort_id": cohort.cohort_id,
        "negative_control_cohort_id": COHORT_CAVEAT10_NEG,
        "output_root": _rel(out_root, base_dir=base_dir),
        "filtered_universe": _rel(filtered_path, base_dir=base_dir),
        "source_universe_count": source_count,
        "included_count": len(included_codes),
        "excluded_control_count": len(expected_excluded),
        "lineage_summary": lineage_summary,
        "checks": checks,
        "gate": gate,
        "fingerprint": dry_bundle["fingerprint"],
        "reproducible": dry_bundle["reproducible"],
        "dryrun_runs": dry_bundle["runs"],
        "matrix_path": _rel(matrix_path, base_dir=base_dir),
        "matrix_rows": matrix + neg_rows,
        "builder_gate": (dry_bundle["dry_result"] or {}).get("gate"),
    }


def run_all_validation_cohorts(
    *,
    base_dir: str = BASE_DIR,
    include_standard_isolated: bool = True,
) -> Dict[str, Any]:
    """跑全部默认校验 cohort（CNINFO=0）。"""
    generated_at = _utc_now_iso()
    slice1 = run_slice1_190_validation_cohort(base_dir=base_dir)
    standard: Optional[Dict[str, Any]] = None
    if include_standard_isolated:
        standard = validate_standard_isolated_fingerprint_cohort(base_dir=base_dir)

    cohort_gates = {
        COHORT_SLICE1_190: slice1["gate"],
        COHORT_CAVEAT10_NEG: (
            "PASS_OFFLINE"
            if slice1["checks"].get("excluded_negative_control_all_ok")
            else "FAIL_REVIEW_REQUIRED"
        ),
    }
    if standard is not None:
        cohort_gates[COHORT_STANDARD_ISOLATED] = standard["gate"]

    overall = (
        "PASS_OFFLINE"
        if all(g == "PASS_OFFLINE" for g in cohort_gates.values())
        else "FAIL_REVIEW_REQUIRED"
    )
    return {
        "generated_at": generated_at,
        "task_id": "C-FM-02",
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "cohort_gates": cohort_gates,
        "gate": overall,
        "slice1_190": slice1,
        "standard_isolated": standard,
    }
