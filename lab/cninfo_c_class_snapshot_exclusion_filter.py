"""
CNINFO C-class — Snapshot exclusion 过滤纯逻辑（离线 · 可单测）。

从 exclusion manifest CSV 或 Run 11 exclusion_reconcile.csv 提取排除代码，
过滤 universe，供 preparation dry-run / command-draft 使用。

不写 snapshot JSON · 不触碰 863/phase3/phase35 生产根 ·
不启用 execute_production_snapshot_rebuild。
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

# lab/ 上一级为仓库根
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

POOL_EXCLUSION_FAMILIES = frozenset({"partial7", "empty_dividend3", "holdout9"})

KIND_MANIFEST = "exclusion_manifest"
KIND_RECONCILE = "exclusion_reconcile"
KIND_UNKNOWN = "unknown"


@dataclass
class ExclusionFilterResult:
    """universe 排除过滤结果。"""

    included: List[Dict[str, str]] = field(default_factory=list)
    excluded: List[Dict[str, str]] = field(default_factory=list)
    excluded_codes: Set[str] = field(default_factory=set)
    csv_kind: str = KIND_UNKNOWN
    source_row_count: int = 0
    notes: str = ""

    @property
    def included_count(self) -> int:
        return len(self.included)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)


def _normalize_code(value: object) -> str:
    return str(value or "").strip()


def detect_exclusion_csv_kind(fieldnames: Optional[Sequence[str]]) -> str:
    """根据表头判定 CSV 类型：manifest / reconcile。"""
    names = {(f or "").strip().lower() for f in (fieldnames or [])}
    if "pool_decision" in names and "company_code" in names:
        return KIND_RECONCILE
    if "cohort_family" in names and "company_code" in names:
        return KIND_MANIFEST
    if "exclusion_id" in names and "company_code" in names:
        return KIND_MANIFEST
    return KIND_UNKNOWN


def load_exclusion_csv_rows(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    """读取 exclusion CSV；返回 (rows, fieldnames)。"""
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = [dict(r) for r in reader]
    return rows, fieldnames


def extract_excluded_codes_from_manifest(
    rows: Sequence[Dict[str, str]],
    *,
    allowed_families: Optional[Set[str]] = None,
) -> Set[str]:
    """
    从 exclusion manifest 提取排除代码。
    若提供 allowed_families，则仅保留白名单家族；未知家族抛错（禁止静默）。
    """
    families = allowed_families if allowed_families is not None else set(POOL_EXCLUSION_FAMILIES)
    codes: Set[str] = set()
    bad_families: Set[str] = set()
    for row in rows:
        code = _normalize_code(row.get("company_code"))
        if not code:
            continue
        family = _normalize_code(row.get("cohort_family"))
        if family and family not in families:
            bad_families.add(family)
            continue
        codes.add(code)
    if bad_families:
        raise ValueError(f"unknown_exclusion_cohort_family: {sorted(bad_families)}")
    return codes


def extract_excluded_codes_from_reconcile(rows: Sequence[Dict[str, str]]) -> Set[str]:
    """从 exclusion_reconcile.csv 提取 pool_decision=excluded 的代码。"""
    codes: Set[str] = set()
    for row in rows:
        code = _normalize_code(row.get("company_code"))
        if not code:
            continue
        decision = _normalize_code(row.get("pool_decision")).lower()
        if decision == "excluded":
            codes.add(code)
    return codes


def load_excluded_codes(
    path: str,
    *,
    kind: Optional[str] = None,
    allowed_families: Optional[Set[str]] = None,
) -> Tuple[Set[str], str, int]:
    """
    加载排除代码集合。
    返回 (excluded_codes, detected_kind, source_row_count)。
    """
    rows, fieldnames = load_exclusion_csv_rows(path)
    detected = kind or detect_exclusion_csv_kind(fieldnames)
    if detected == KIND_UNKNOWN:
        raise ValueError(
            "unrecognized_exclusion_csv_kind: need cohort_family/exclusion_id "
            "or pool_decision columns"
        )
    if detected == KIND_RECONCILE:
        codes = extract_excluded_codes_from_reconcile(rows)
    else:
        codes = extract_excluded_codes_from_manifest(
            rows, allowed_families=allowed_families
        )
    return codes, detected, len(rows)


def apply_exclusion_filter(
    companies: Sequence[Dict[str, str]],
    excluded_codes: Iterable[str],
    *,
    code_key: str = "company_code",
) -> ExclusionFilterResult:
    """
    按 excluded_codes 拆分 universe。
    保留原 dict 引用顺序；不修改入参元素。
    """
    excluded_set = {_normalize_code(c) for c in excluded_codes if _normalize_code(c)}
    included: List[Dict[str, str]] = []
    excluded: List[Dict[str, str]] = []
    for company in companies:
        code = _normalize_code(company.get(code_key) or company.get("stock_code"))
        if code in excluded_set:
            excluded.append(dict(company))
        else:
            included.append(dict(company))
    return ExclusionFilterResult(
        included=included,
        excluded=excluded,
        excluded_codes=excluded_set,
        notes=f"excluded_unique={len(excluded_set)}; filtered_rows={len(excluded)}",
    )


def filter_universe_with_exclusion_csv(
    companies: Sequence[Dict[str, str]],
    exclusion_csv_path: str,
    *,
    kind: Optional[str] = None,
) -> ExclusionFilterResult:
    """加载 exclusion CSV 并过滤 universe（纯函数入口）。"""
    codes, detected, row_count = load_excluded_codes(exclusion_csv_path, kind=kind)
    result = apply_exclusion_filter(companies, codes)
    result.csv_kind = detected
    result.source_row_count = row_count
    return result


def refuse_exclusion_with_execute(
    *,
    dry_run: bool,
    exclusion_csv: Optional[str],
) -> None:
    """
    安全边界：exclusion-csv 仅允许 dry-run / preparation。
    --execute 路径严禁携带 exclusion-csv（禁止静默忽略）。
    """
    if exclusion_csv and not dry_run:
        raise RuntimeError(
            "EXCLUSION_CSV_EXECUTE_FORBIDDEN: "
            "--exclusion-csv 仅允许 preparation dry-run，禁止与 --execute 同用"
        )


def assert_execute_production_snapshot_rebuild_false(
    execute_production_snapshot_rebuild: bool = False,
) -> None:
    """硬拒绝 production snapshot rebuild 标志。"""
    if execute_production_snapshot_rebuild:
        raise RuntimeError(
            "EXECUTE_PRODUCTION_SNAPSHOT_REBUILD_FORBIDDEN: "
            "本模块禁止设置 execute_production_snapshot_rebuild=true"
        )
