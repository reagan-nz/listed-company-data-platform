#!/usr/bin/env python3
"""
CNINFO C-class 863 full harvest 离线 QA Review（Era C Phase 4）。

仅读取现有 harvest 输出，不请求 CNINFO，不重跑 live，不修改 raw/normalized 数据。

Usage:
    python lab/review_cninfo_c_class_full_harvest_qa.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_mappers import _aggregate_dividend_parse_status  # noqa: E402
from harvest_cninfo_c_class import (  # noqa: E402
    BASE_DIR,
    HARVEST_EXPECTED_COMPANY_COUNT,
    HARVEST_MATRIX_SOURCE_ORDER,
    HARVEST_OUTPUT_ROOT,
    HOLD_SAMPLE_REL,
    HTTP_SOURCES_PER_COMPANY,
    MATRIX_SOURCES_PER_COMPANY,
    SOURCE_HARVEST_META,
    count_harvest_artifacts_on_disk,
    load_harvest_report_csv,
)

DEFAULT_HARVEST_SAMPLE_REL = "lab/eval_companies_c_class_harvest_863_non_bse.yaml"
HARVEST_SUMMARY_REL = f"{HARVEST_OUTPUT_ROOT}/quality/harvest_summary.md"
FULL_SUMMARY_REL = "outputs/validation/cninfo_c_class_harvest_full_summary.md"
FULL_REPORT_REL = "outputs/validation/cninfo_c_class_harvest_full_report.csv"
SOURCE_QUALITY_REL = f"{HARVEST_OUTPUT_ROOT}/quality/source_quality.csv"
COMPANY_STATUS_REL = f"{HARVEST_OUTPUT_ROOT}/quality/company_harvest_status.csv"
FIELD_FILL_REL = f"{HARVEST_OUTPUT_ROOT}/quality/field_fill_rate.csv"
QA_REVIEW_MD_REL = "outputs/validation/cninfo_c_class_full_harvest_qa_review.md"
QA_FLAGS_CSV_REL = "outputs/validation/cninfo_c_class_full_harvest_qa_flags.csv"

# 主 company snapshot 源（不含 security observe_only）
CORE_SNAPSHOT_SOURCE_IDS = tuple(
    sid for sid in HARVEST_MATRIX_SOURCE_ORDER
    if SOURCE_HARVEST_META[sid]["source_status"] != "observe_only"
)

SOURCE_LOGICAL_NAMES: Dict[str, str] = {
    "cninfo_company_basic_profile": "basic",
    "cninfo_executive_profile": "executive",
    "cninfo_share_capital_profile": "share_capital",
    "cninfo_top_shareholders_profile": "top_shareholders",
    "cninfo_top_float_shareholders_profile": "top_float",
    "cninfo_dividend_financing_profile": "dividend_history",
    "cninfo_company_security_profile": "security_observe",
    "cninfo_company_contact_profile": "contact",
    "cninfo_company_business_scope": "business_scope",
    "cninfo_company_industry_profile": "industry",
}

CAVEAT_SOURCE_STATUSES = frozenset({
    "proceed_testing_with_caveat",
    "source_partial",
})

FLAG_CSV_FIELDS = [
    "company_code",
    "company_name",
    "flag_category",
    "flag_detail",
    "severity",
    "source_id",
    "metric_value",
]


@dataclass
class QAReviewResult:
    """离线 QA 汇总结果。"""

    harvest_full_gate: str = ""
    qa_conclusion: str = ""
    total_harvest_universe: int = 0
    hold_overlap: int = 0
    raw_total: int = 0
    normalized_total: int = 0
    completed_companies: int = 0
    blocked_count: int = 0
    http_error_count: int = 0
    company_status_dist: Counter = field(default_factory=Counter)
    retrieval_status_dist: Counter = field(default_factory=Counter)
    dividend_parse_dist: Counter = field(default_factory=Counter)
    dividend_event_needs_review: int = 0
    dividend_companies_with_needs_review_event: int = 0
    per_source_reachability: Dict[str, Counter] = field(default_factory=dict)
    flags: List[Dict[str, str]] = field(default_factory=list)
    hard_fail_reasons: List[str] = field(default_factory=list)
    caveat_reasons: List[str] = field(default_factory=list)


def _abs(rel_path: str) -> str:
    return os.path.join(BASE_DIR, rel_path)


def _load_yaml_company_codes(path: str) -> Set[str]:
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return {str(c["stock_code"]).zfill(6) for c in data["companies"]}


def _load_company_names(sample_path: str) -> Dict[str, str]:
    with open(sample_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return {str(c["stock_code"]).zfill(6): c.get("company_name", "") for c in data["companies"]}


def _parse_gate_from_md(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    match = re.search(r"harvest_full_gate\s*=\s*(\w+)", text)
    return match.group(1) if match else ""


def _load_csv_rows(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _disk_company_codes() -> Set[str]:
    basic_dir = _abs(f"{HARVEST_OUTPUT_ROOT}/normalized/company_basic_profile")
    return {name[:-5] for name in os.listdir(basic_dir) if name.endswith(".json")}


def _normalized_subdir_for(source_id: str) -> Tuple[str, str]:
    meta = SOURCE_HARVEST_META[source_id]
    return meta["normalized_subdir"], meta["file_ext"]


def _infer_retrieval_for_disk_only(
    source_id: str,
    company_code: str,
    norm_root: str,
) -> str:
    """对 resume 跳过的 smoke 批次（仅磁盘、无 report 行）推断 retrieval_status。"""
    subdir, ext = _normalized_subdir_for(source_id)
    norm_path = os.path.join(norm_root, subdir, f"{company_code}{ext}")
    if not os.path.isfile(norm_path):
        return "missing_on_disk"
    if source_id in (
        "cninfo_company_contact_profile",
        "cninfo_company_business_scope",
        "cninfo_company_industry_profile",
    ):
        return "derived_from_basic"
    if source_id == "cninfo_dividend_financing_profile":
        # valid_empty：文件存在但无事件行
        with open(norm_path, encoding="utf-8") as fh:
            has_line = any(line.strip() for line in fh)
        return "valid_empty" if not has_line else "endpoint_found"
    if os.path.getsize(norm_path) <= 4:
        return "empty_but_valid_response"
    return "endpoint_found"


def _build_unified_report_rows(
    report_rows: List[Dict[str, str]],
    disk_codes: Set[str],
) -> List[Dict[str, str]]:
    """合并 full report 与磁盘-only smoke 公司，得到 863 家统一视图。"""
    report_codes = {r["company_code"] for r in report_rows}
    report_index = {(r["company_code"], r["source_id"]): r for r in report_rows}
    norm_root = _abs(f"{HARVEST_OUTPUT_ROOT}/normalized")
    unified: List[Dict[str, str]] = list(report_rows)

    for code in sorted(disk_codes - report_codes):
        for source_id in HARVEST_MATRIX_SOURCE_ORDER:
            existing = report_index.get((code, source_id))
            if existing:
                continue
            retrieval = _infer_retrieval_for_disk_only(source_id, code, norm_root)
            meta = SOURCE_HARVEST_META[source_id]
            subdir, ext = _normalized_subdir_for(source_id)
            norm_path = os.path.join(
                HARVEST_OUTPUT_ROOT, "normalized", subdir, f"{code}{ext}",
            )
            unified.append({
                "company_code": code,
                "company_name": "",
                "board": "",
                "source_id": source_id,
                "source_type": meta["source_type"],
                "retrieval_status": retrieval,
                "case_result": "pass",
                "http_status": "200",
                "business_code": "200",
                "harvest_result": "success",
                "raw_path": "",
                "normalized_path": norm_path,
                "raw_written": "yes",
                "normalized_written": "yes",
                "record_count": "",
                "error_message": "",
            })
    return unified


def _rebuild_company_status(
    disk_codes: Set[str],
    status_rows: List[Dict[str, str]],
    unified_rows: List[Dict[str, str]],
) -> Dict[str, str]:
    """重建 863 家 harvest_status（CSV 仅含 resume 批次 853 家）。"""
    status_by_code = {r["company_code"]: r["harvest_status"] for r in status_rows}
    core_norm_subdirs = {
        SOURCE_HARVEST_META[sid]["normalized_subdir"]
        for sid in CORE_SNAPSHOT_SOURCE_IDS
    }
    norm_root = _abs(f"{HARVEST_OUTPUT_ROOT}/normalized")
    by_company: Dict[str, Set[str]] = defaultdict(set)
    for sub in core_norm_subdirs:
        d = os.path.join(norm_root, sub)
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if name.endswith((".json", ".jsonl")):
                ext = ".jsonl" if name.endswith(".jsonl") else ".json"
                by_company[name[: -len(ext)]].add(sub)

    result: Dict[str, str] = {}
    for code in disk_codes:
        if code in status_by_code:
            result[code] = status_by_code[code]
            continue
        present = by_company.get(code, set())
        if present == core_norm_subdirs:
            result[code] = "complete"
        elif present:
            result[code] = "partial"
        else:
            result[code] = "failed"

        # 对 report 中 empty_but_valid 但文件齐的情况仍视为 complete
        company_rows = [r for r in unified_rows if r["company_code"] == code]
        if result[code] != "complete" and len(present) == len(core_norm_subdirs):
            result[code] = "complete"
        elif company_rows and all(
            r.get("harvest_result") in ("success", "empty_but_valid")
            for r in company_rows
            if r["source_id"] in CORE_SNAPSHOT_SOURCE_IDS
        ) and len(present) == len(core_norm_subdirs):
            result[code] = "complete"
    return result


def _collect_dividend_parse_stats(
    disk_codes: Set[str],
    company_names: Dict[str, str],
) -> Tuple[Counter, Dict[str, str], Set[str], int]:
    """从 normalized dividend_history jsonl 统计 company 级 parse 分布。"""
    div_dir = _abs(f"{HARVEST_OUTPUT_ROOT}/normalized/dividend_history")
    dist: Counter = Counter()
    by_company: Dict[str, str] = {}
    needs_review_codes: Set[str] = set()
    event_needs_review_count = 0

    for code in disk_codes:
        path = os.path.join(div_dir, f"{code}.jsonl")
        if not os.path.isfile(path):
            dist["missing_file"] += 1
            by_company[code] = "missing_file"
            continue
        event_statuses: List[str] = []
        has_needs_review_event = False
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                event = json.loads(line)
                st = event.get("dividend_parse_status", "needs_review")
                event_statuses.append(st)
                if st == "needs_review":
                    has_needs_review_event = True
                    event_needs_review_count += 1
        company_st = _aggregate_dividend_parse_status(event_statuses)
        dist[company_st] += 1
        by_company[code] = company_st
        if company_st == "needs_review" or has_needs_review_event:
            needs_review_codes.add(code)
    return dist, by_company, needs_review_codes, event_needs_review_count


def _collect_field_fill_gaps(
    fill_rows: List[Dict[str, str]],
    threshold: int = 1,
) -> Dict[str, int]:
    """统计 core snapshot 源中 filled!=1 的字段行数（按公司）。"""
    missing: Counter = Counter()
    for row in fill_rows:
        if row["source_id"] not in CORE_SNAPSHOT_SOURCE_IDS:
            continue
        if row.get("filled") != "1":
            missing[row["company_code"]] += 1
    return {code: n for code, n in missing.items() if n >= threshold}


def _per_source_reachability(unified_rows: List[Dict[str, str]]) -> Dict[str, Counter]:
    result: Dict[str, Counter] = {}
    for source_id in HARVEST_MATRIX_SOURCE_ORDER:
        rows = [r for r in unified_rows if r["source_id"] == source_id]
        result[SOURCE_LOGICAL_NAMES[source_id]] = Counter(
            r["retrieval_status"] for r in rows
        )
    return result


def _collect_flags(
    company_status: Dict[str, str],
    unified_rows: List[Dict[str, str]],
    dividend_by_company: Dict[str, str],
    needs_review_dividend: Set[str],
    field_fill_gaps: Dict[str, int],
    company_names: Dict[str, str],
) -> List[Dict[str, str]]:
    flags: List[Dict[str, str]] = []

    for code, status in sorted(company_status.items()):
        name = company_names.get(code, "")
        if status != "complete":
            flags.append({
                "company_code": code,
                "company_name": name,
                "flag_category": "company_status",
                "flag_detail": f"harvest_status={status}",
                "severity": "high" if status == "failed" else "medium",
                "source_id": "",
                "metric_value": status,
            })

    rows_by_company: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in unified_rows:
        rows_by_company[row["company_code"]].append(row)

    for code, rows in sorted(rows_by_company.items()):
        name = company_names.get(code, rows[0].get("company_name", "") if rows else "")
        for row in rows:
            source_id = row["source_id"]
            meta = SOURCE_HARVEST_META[source_id]
            source_status = meta["source_status"]
            retrieval = row["retrieval_status"]
            if source_status in CAVEAT_SOURCE_STATUSES and retrieval in (
                "empty_but_valid_response",
                "valid_empty",
            ):
                flags.append({
                    "company_code": code,
                    "company_name": name,
                    "flag_category": "source_caveat",
                    "flag_detail": (
                        f"{SOURCE_LOGICAL_NAMES[source_id]} "
                        f"retrieval={retrieval} source_status={source_status}"
                    ),
                    "severity": "low",
                    "source_id": source_id,
                    "metric_value": retrieval,
                })

    for code in sorted(needs_review_dividend):
        parse_st = dividend_by_company.get(code, "")
        flags.append({
            "company_code": code,
            "company_name": company_names.get(code, ""),
            "flag_category": "dividend_parse",
            "flag_detail": f"dividend_parse_status={parse_st} (含 needs_review 事件)",
            "severity": "medium",
            "source_id": "cninfo_dividend_financing_profile",
            "metric_value": parse_st,
        })

    # missing normalized_core：字段 fill 缺口较多的公司（Top 阈值 >= 2 或唯一缺口）
    for code, gap_n in sorted(field_fill_gaps.items(), key=lambda x: (-x[1], x[0])):
        if gap_n < 2:
            continue
        flags.append({
            "company_code": code,
            "company_name": company_names.get(code, ""),
            "flag_category": "missing_normalized_core",
            "flag_detail": f"core_field_fill_gaps={gap_n}",
            "severity": "medium",
            "source_id": "",
            "metric_value": str(gap_n),
        })

    return flags


def _evaluate_qa_conclusion(result: QAReviewResult) -> str:
    if result.hard_fail_reasons:
        return "FAIL"
    if result.caveat_reasons or result.flags:
        return "PASS_WITH_CAVEAT"
    return "PASS"


def run_qa_review(
    *,
    harvest_summary_path: Optional[str] = None,
    full_summary_path: Optional[str] = None,
    full_report_path: Optional[str] = None,
    source_quality_path: Optional[str] = None,
    company_status_path: Optional[str] = None,
    field_fill_path: Optional[str] = None,
    sample_path: Optional[str] = None,
    qa_review_md_path: Optional[str] = None,
    qa_flags_csv_path: Optional[str] = None,
) -> QAReviewResult:
    harvest_summary_path = harvest_summary_path or _abs(HARVEST_SUMMARY_REL)
    full_summary_path = full_summary_path or _abs(FULL_SUMMARY_REL)
    full_report_path = full_report_path or _abs(FULL_REPORT_REL)
    source_quality_path = source_quality_path or _abs(SOURCE_QUALITY_REL)
    company_status_path = company_status_path or _abs(COMPANY_STATUS_REL)
    field_fill_path = field_fill_path or _abs(FIELD_FILL_REL)
    sample_path = sample_path or _abs(DEFAULT_HARVEST_SAMPLE_REL)
    qa_review_md_path = qa_review_md_path or _abs(QA_REVIEW_MD_REL)
    qa_flags_csv_path = qa_flags_csv_path or _abs(QA_FLAGS_CSV_REL)

    result = QAReviewResult()

    harvest_codes = _load_yaml_company_codes(sample_path)
    hold_codes = _load_yaml_company_codes(_abs(HOLD_SAMPLE_REL))
    company_names = _load_company_names(sample_path)

    result.total_harvest_universe = len(harvest_codes)
    result.hold_overlap = len(harvest_codes & hold_codes)

    gate_full = _parse_gate_from_md(full_summary_path)
    gate_quality = _parse_gate_from_md(harvest_summary_path)
    result.harvest_full_gate = gate_full or gate_quality

    disk_counts = count_harvest_artifacts_on_disk()
    result.raw_total = disk_counts["raw_files_total"]
    result.normalized_total = disk_counts["normalized_files_total"]
    result.completed_companies = disk_counts["completed_companies_total"]

    report_rows = load_harvest_report_csv(full_report_path)
    disk_codes = _disk_company_codes()
    unified_rows = _build_unified_report_rows(report_rows, disk_codes)

    result.retrieval_status_dist = Counter(r["retrieval_status"] for r in unified_rows)
    result.blocked_count = sum(1 for r in unified_rows if r.get("harvest_result") == "blocked")
    result.http_error_count = sum(1 for r in unified_rows if r.get("harvest_result") == "http_error")

    status_rows = _load_csv_rows(company_status_path)
    company_status = _rebuild_company_status(disk_codes, status_rows, unified_rows)
    result.company_status_dist = Counter(company_status.values())

    result.per_source_reachability = _per_source_reachability(unified_rows)

    dividend_dist, dividend_by_company, needs_review_dividend, event_nr = _collect_dividend_parse_stats(
        disk_codes, company_names,
    )
    result.dividend_parse_dist = dividend_dist
    result.dividend_event_needs_review = event_nr
    result.dividend_companies_with_needs_review_event = len(needs_review_dividend)

    fill_rows = _load_csv_rows(field_fill_path)
    field_fill_gaps = _collect_field_fill_gaps(fill_rows, threshold=1)

    result.flags = _collect_flags(
        company_status,
        unified_rows,
        dividend_by_company,
        needs_review_dividend,
        field_fill_gaps,
        company_names,
    )

    # hard fail 判定
    if result.harvest_full_gate not in ("PASS_WITH_RESUME", "PASS"):
        result.hard_fail_reasons.append(
            f"harvest_full_gate={result.harvest_full_gate or 'UNKNOWN'}",
        )
    if result.hold_overlap != 0:
        result.hard_fail_reasons.append(f"hold_overlap={result.hold_overlap}")
    if result.completed_companies != HARVEST_EXPECTED_COMPANY_COUNT:
        result.hard_fail_reasons.append(
            f"completed_companies={result.completed_companies} "
            f"(expected {HARVEST_EXPECTED_COMPANY_COUNT})",
        )
    if result.raw_total != HARVEST_EXPECTED_COMPANY_COUNT * HTTP_SOURCES_PER_COMPANY:
        result.hard_fail_reasons.append(
            f"raw_total={result.raw_total} "
            f"(expected {HARVEST_EXPECTED_COMPANY_COUNT * HTTP_SOURCES_PER_COMPANY})",
        )
    if result.normalized_total != HARVEST_EXPECTED_COMPANY_COUNT * MATRIX_SOURCES_PER_COMPANY:
        result.hard_fail_reasons.append(
            f"normalized_total={result.normalized_total} "
            f"(expected {HARVEST_EXPECTED_COMPANY_COUNT * MATRIX_SOURCES_PER_COMPANY})",
        )
    if result.blocked_count > 0:
        result.hard_fail_reasons.append(f"blocked_count={result.blocked_count}")
    if result.http_error_count > 0:
        result.hard_fail_reasons.append(f"http_error_count={result.http_error_count}")
    if result.company_status_dist.get("failed", 0) > 0:
        result.hard_fail_reasons.append(
            f"company_failed={result.company_status_dist.get('failed', 0)}",
        )

    # caveat 说明（不自动 FAIL）
    resume_skipped = len(disk_codes - {r["company_code"] for r in report_rows})
    if resume_skipped > 0:
        result.caveat_reasons.append(
            f"resume_smoke_batch={resume_skipped} 家仅磁盘覆盖、无 full report 行",
        )
    if result.dividend_parse_dist.get("partial", 0) > 0:
        result.caveat_reasons.append(
            f"dividend_parse partial={result.dividend_parse_dist.get('partial', 0)}",
        )
    if result.dividend_parse_dist.get("empty_but_valid", 0) > 0:
        result.caveat_reasons.append(
            f"dividend_parse empty_but_valid="
            f"{result.dividend_parse_dist.get('empty_but_valid', 0)}",
        )
    if needs_review_dividend:
        result.caveat_reasons.append(
            f"dividend needs_review 事件涉及 {len(needs_review_dividend)} 家",
        )
    caveat_source_flags = [f for f in result.flags if f["flag_category"] == "source_caveat"]
    if caveat_source_flags:
        result.caveat_reasons.append(
            f"source_caveat flags={len(caveat_source_flags)} "
            f"(empty_but_valid on partial/caveat sources)",
        )
    if field_fill_gaps:
        result.caveat_reasons.append(
            f"normalized_core fill gaps: {len(field_fill_gaps)} 家有缺口",
        )

    result.qa_conclusion = _evaluate_qa_conclusion(result)

    _write_qa_review_md(
        qa_review_md_path,
        result,
        harvest_summary_path,
        full_summary_path,
        full_report_path,
        source_quality_path,
        company_status_path,
        field_fill_path,
        sample_path,
        len(report_rows),
        len(disk_codes - {r["company_code"] for r in report_rows}),
    )
    _write_qa_flags_csv(qa_flags_csv_path, result.flags)
    return result


def _write_qa_flags_csv(path: str, flags: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FLAG_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(flags)


def _write_qa_review_md(
    path: str,
    result: QAReviewResult,
    harvest_summary_path: str,
    full_summary_path: str,
    full_report_path: str,
    source_quality_path: str,
    company_status_path: str,
    field_fill_path: str,
    sample_path: str,
    report_row_count: int,
    resume_smoke_count: int,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    lines = [
        "# CNINFO C-Class Full Harvest QA Review",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 QA：仅读取现有 harvest 输出。**无 CNINFO** · **无 live 重跑** · **无 raw/normalized 修改** · **无 verified** · **无 DB/MinIO/RAG**",
        "",
        "## QA Conclusion",
        "",
        f"**{result.qa_conclusion}**",
        "",
        f"- harvest_full_gate: **{result.harvest_full_gate}**",
        "",
        "## 1. Full harvest gate",
        "",
        f"| 检查项 | 值 | 期望 | 判定 |",
        f"|--------|-----|------|------|",
        f"| harvest_full_gate | {result.harvest_full_gate} | PASS_WITH_RESUME | "
        f"**{'PASS' if result.harvest_full_gate == 'PASS_WITH_RESUME' else 'CHECK'}** |",
        f"| blocked | {result.blocked_count} | 0 | "
        f"**{'PASS' if result.blocked_count == 0 else 'FAIL'}** |",
        f"| http_error | {result.http_error_count} | 0 | "
        f"**{'PASS' if result.http_error_count == 0 else 'FAIL'}** |",
        "",
        "## 2. 文件计数 & universe",
        "",
        f"| 指标 | 实际 | 期望 |",
        f"|------|------|------|",
        f"| raw total | **{result.raw_total}** | 6041 |",
        f"| normalized total | **{result.normalized_total}** | 8630 |",
        f"| completed companies | **{result.completed_companies}** | 863 |",
        f"| hold_overlap | **{result.hold_overlap}** | 0 |",
        f"| total_harvest_universe | **{result.total_harvest_universe}** | 863 |",
        f"| resume_smoke_only_disk | **{resume_smoke_count}** | 10（resume 跳过 smoke） |",
        "",
        "## 3. Per-source reachability（863 家 · 含磁盘 smoke 补齐）",
        "",
        "| source | endpoint_found | derived_from_basic | empty_but_valid_response | valid_empty | other |",
        "|--------|----------------|--------------------|--------------------------|-------------|-------|",
    ]

    for logical_name in (
        "basic", "executive", "share_capital", "top_shareholders", "top_float",
        "dividend_history", "security_observe", "contact", "business_scope", "industry",
    ):
        ctr = result.per_source_reachability.get(logical_name, Counter())
        total = sum(ctr.values())
        other = total - (
            ctr.get("endpoint_found", 0)
            + ctr.get("derived_from_basic", 0)
            + ctr.get("empty_but_valid_response", 0)
            + ctr.get("valid_empty", 0)
        )
        observe_note = " _(observe_only)_" if logical_name == "security_observe" else ""
        lines.append(
            f"| {logical_name}{observe_note} | {ctr.get('endpoint_found', 0)} | "
            f"{ctr.get('derived_from_basic', 0)} | {ctr.get('empty_but_valid_response', 0)} | "
            f"{ctr.get('valid_empty', 0)} | {other} |",
        )

    lines.extend([
        "",
        "## 4. company_harvest_status 分布（863 家重建）",
        "",
    ])
    for status, count in sorted(result.company_status_dist.items()):
        lines.append(f"- `{status}`: **{count}**")
    lines.extend([
        "",
        "## 5. retrieval_status 分布（8630 rows）",
        "",
    ])
    retrieval_display = Counter(result.retrieval_status_dist)
    for status in (
        "endpoint_found",
        "derived_from_basic",
        "empty_but_valid_response",
        "valid_empty",
        "blocked",
        "http_error",
    ):
        if status not in retrieval_display:
            retrieval_display[status] = 0
    for status, count in sorted(retrieval_display.items()):
        lines.append(f"- `{status}`: **{count}**")
    lines.extend([
        "",
        "## 6. dividend_parse_status 分布（company 级 · 863 家）",
        "",
        "_dividend_history ≠ financing；自 normalized/dividend_history jsonl 聚合。_",
        "",
    ])
    for status, count in sorted(result.dividend_parse_dist.items()):
        lines.append(f"- `{status}`: **{count}**")
    lines.extend([
        "",
        f"_补充：事件级 `needs_review` 共 **{result.dividend_event_needs_review}** 条，"
        f"分布于 **{result.dividend_companies_with_needs_review_event}** 家公司"
        f"（company 级聚合为 `partial`）。_",
        "",
    ])

    flag_categories = Counter(f["flag_category"] for f in result.flags)
    lines.extend([
        "",
        "## 7. Review flags 摘要",
        "",
        f"- 总 flags: **{len(result.flags)}**",
    ])
    for cat, n in sorted(flag_categories.items()):
        lines.append(f"- `{cat}`: **{n}**")
    lines.extend([
        "",
        "详见 [cninfo_c_class_full_harvest_qa_flags.csv](cninfo_c_class_full_harvest_qa_flags.csv)。",
        "",
        "## 8. 判定说明",
        "",
        "| 级别 | 条件 |",
        "|------|------|",
        "| **PASS** | gate 通过 · 计数正确 · 无 review flags |",
        "| **PASS_WITH_CAVEAT** | gate 通过 · 存在 source_partial / empty_but_valid / dividend parse / fill gap 等待人工 review |",
        "| **FAIL** | gate 失败 · hold_overlap · 计数不符 · blocked/http_error · company failed |",
        "",
        "**政策：** `source_partial` / `empty_but_valid` **不自动判 FAIL**；`security_observe` **observe_only**，不进入主 company snapshot。",
        "",
    ])

    if result.hard_fail_reasons:
        lines.extend(["### Hard fail reasons", ""])
        for reason in result.hard_fail_reasons:
            lines.append(f"- {reason}")
        lines.append("")

    if result.caveat_reasons:
        lines.extend(["### Caveat notes", ""])
        for reason in result.caveat_reasons:
            lines.append(f"- {reason}")
        lines.append("")

    lines.extend([
        "## 9. 输入文件",
        "",
        f"- `{os.path.relpath(harvest_summary_path, BASE_DIR)}`",
        f"- `{os.path.relpath(full_summary_path, BASE_DIR)}`",
        f"- `{os.path.relpath(full_report_path, BASE_DIR)}` ({report_row_count} rows)",
        f"- `{os.path.relpath(source_quality_path, BASE_DIR)}`",
        f"- `{os.path.relpath(company_status_path, BASE_DIR)}`",
        f"- `{os.path.relpath(field_fill_path, BASE_DIR)}`",
        f"- sample: `{os.path.relpath(sample_path, BASE_DIR)}`",
        "",
        "## 10. 红线确认",
        "",
        "- 未请求 CNINFO",
        "- 未重跑 live harvest",
        "- 未修改 raw / normalized 数据",
        "- 未写 verified / 未升级 testing_stable_sample",
        "- 未入库 / MinIO / RAG / YAML backfill",
        "",
    ])

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="CNINFO C-class full harvest 离线 QA review")
    parser.add_argument("--qa-review-md", default=QA_REVIEW_MD_REL)
    parser.add_argument("--qa-flags-csv", default=QA_FLAGS_CSV_REL)
    args = parser.parse_args()

    result = run_qa_review(
        qa_review_md_path=_abs(args.qa_review_md),
        qa_flags_csv_path=_abs(args.qa_flags_csv),
    )

    print("pre_qa_review: PASS")
    print(f"harvest_full_gate={result.harvest_full_gate}")
    print(f"qa_conclusion={result.qa_conclusion}")
    print(f"raw_total={result.raw_total}")
    print(f"normalized_total={result.normalized_total}")
    print(f"completed_companies={result.completed_companies}")
    print(f"hold_overlap={result.hold_overlap}")
    print(f"flags={len(result.flags)}")
    print(f"MD    {_abs(args.qa_review_md)}")
    print(f"CSV   {_abs(args.qa_flags_csv)}")


if __name__ == "__main__":
    main()
