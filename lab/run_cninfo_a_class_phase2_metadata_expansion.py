"""
CNINFO A-class Phase 2 metadata expansion runner.

默认 dry-run：校验 universe · 输出隔离 · 生成规划报告，**不请求 CNINFO**。
--live 须 --approve-a-class-phase2-metadata-expansion；仅 metadata · 无 PDF 下载/解析。

Usage:
    python lab/run_cninfo_a_class_phase2_metadata_expansion.py
    python lab/run_cninfo_a_class_phase2_metadata_expansion.py --live \\
        --approve-a-class-phase2-metadata-expansion
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_DIR = os.path.join(BASE_DIR, "lab")
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

import run_cninfo_a_class_tiny_live_metadata_validation as tiny_live  # noqa: E402

DEFAULT_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase2_metadata_universe_draft.csv",
)
DEFAULT_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_metadata_expansion"
)
DEFAULT_RETRY_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase2_failed_retry_universe.csv",
)
DEFAULT_RETRY_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_metadata_retry"
)
PHASE1_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_tiny_live_metadata"
)
C_CLASS_HARVEST_ROOT = os.path.join(BASE_DIR, "outputs", "harvest", "cninfo_c_class")

DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "a_class_phase2_metadata_dryrun_report.csv"
)
DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "a_class_phase2_metadata_dryrun_summary.md"
)

REQUIRED_UNIVERSE_SIZE = 20
RETRY_REQUIRED_UNIVERSE_SIZE = 8
RETRY_ALLOWED_CASE_IDS: Set[str] = {
    "A2M005",
    "A2M010",
    "A2M011",
    "A2M012",
    "A2M013",
    "A2M018",
    "A2M019",
    "A2M020",
}
SUCCESSFUL_CASE_IDS: Set[str] = {
    "A2M001",
    "A2M002",
    "A2M003",
    "A2M004",
    "A2M006",
    "A2M007",
    "A2M008",
    "A2M009",
    "A2M014",
    "A2M015",
    "A2M016",
    "A2M017",
}
PHASE2_CASE_ID_PATTERN = re.compile(r"^A2M\d{3}$")
PHASE1_COMPANY_CODES: Set[str] = {"600000", "300001", "688001", "000858", "600519"}

EXPECTED_REPORT_TYPE_MIX: Dict[str, int] = {
    "annual_report": 8,
    "semi_annual_report": 4,
    "quarterly_report_q1": 4,
    "quarterly_report_q3": 4,
}

RUNNER_GATE = "READY_FOR_APPROVAL"
MATCHING_LOGIC_VERSION = tiny_live.MATCHING_LOGIC_VERSION

PHASE2_APPROVAL_REQUIRED = "approve_a_class_phase2_metadata_expansion_required"
RETRY_APPROVAL_REQUIRED = "approve_a_class_phase2_failed_retry_required"
OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_a_class_phase2_metadata_expansion"
RETRY_OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_a_class_phase2_metadata_retry"
PHASE2_EXPANSION_WRITE_FORBIDDEN = "phase2_expansion_baseline_write_forbidden"
UNIVERSE_SIZE_VIOLATION = "universe_size_must_equal_20"
RETRY_UNIVERSE_SIZE_VIOLATION = "retry_universe_size_must_equal_8"
SUCCESSFUL_CASE_IN_RETRY_FORBIDDEN = "successful_case_not_allowed_in_retry_universe"
NON_RETRY_CASE_REJECTED = "non_retry_failed_case_not_allowed"
RETRY_INCLUDE_REQUIRED = "retry_include_must_be_yes"
NON_PHASE2_CASE_REJECTED = "non_a2m_case_not_allowed"
PHASE2_INCLUDE_REQUIRED = "phase2_include_must_be_yes"
RETRY_PLANNING_GATE = "READY_FOR_APPROVAL"
RETRY_CORRECT_THRESHOLD = 6

RETRY_LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "expected_period",
    "original_failure_type",
    "retry_retrieval_status",
    "quality_status",
    "lineage_status",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "title_match_status",
    "period_match_status",
    "wrong_report_type",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "ocr_enabled",
    "extraction_enabled",
    "cninfo_request_count",
    "notes",
]

RETRY_LIVE_QUALITY_COLUMNS = [
    "case_id",
    "company_code",
    "report_type",
    "expected_period",
    "original_failure_type",
    "retry_retrieval_status",
    "title_match_status",
    "period_match_status",
    "wrong_report_type",
    "quality_status",
    "lineage_status",
    "pdf_downloaded",
    "pdf_parsed",
    "notes",
]

PHASE1_OVERLAP_REJECTED = "phase1_overlap_not_allowed"
REPORT_TYPE_MIX_VIOLATION = "report_type_mix_must_be_8_4_4_4"
PHASE1_BASELINE_WRITE_FORBIDDEN = "phase1_tiny_live_baseline_write_forbidden"
PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED = "pdf_download_not_allowed"
PDF_PARSE_REQUESTED_NOT_ALLOWED = "pdf_parse_not_allowed"
OCR_REQUESTED_NOT_ALLOWED = "ocr_not_allowed"
EXTRACTION_REQUESTED_NOT_ALLOWED = "extraction_not_allowed"
DB_WRITE_REQUESTED_NOT_ALLOWED = "db_write_not_allowed"
MINIO_WRITE_REQUESTED_NOT_ALLOWED = "minio_write_not_allowed"
RAG_REQUESTED_NOT_ALLOWED = "rag_not_allowed"
VERIFIED_STATUS_REQUESTED_NOT_ALLOWED = "verified_status_not_allowed"
PRODUCTION_READY_REQUESTED_NOT_ALLOWED = "production_ready_not_allowed"
TINY_LIVE_APPROVAL_WRONG = "approve_a_class_tiny_live_metadata_not_valid_for_phase2"
PHASE1_TINY_LIVE_APPROVAL_WRONG = "approve_phase1_tiny_live_metadata_not_valid_for_phase2"

DOWNLOAD_PDF = False
PARSE_PDF = False
ENABLE_OCR = False
ENABLE_EXTRACTION = False
WRITE_DB = False
WRITE_MINIO = False
ENABLE_RAG = False
WRITE_VERIFIED = False
UPGRADE_TESTING_STABLE_SAMPLE = False

PLANNED_OUTPUT_OBJECTS = tiny_live.PLANNED_OUTPUT_OBJECTS
REPORT_TYPE_SOURCE_ID = tiny_live.REPORT_TYPE_SOURCE_ID

# Phase 2 universe 已知代码-简称对照
KNOWN_COMPANY_NAMES: Dict[str, str] = {
    "600036": "招商银行",
    "601318": "中国平安",
    "000333": "美的集团",
    "002415": "海康威视",
    "601012": "隆基绿能",
    "600276": "恒瑞医药",
    "000002": "万科A",
    "601888": "中国中免",
    "300014": "亿纬锂能",
    "300750": "宁德时代",
    "600887": "伊利股份",
    "601166": "兴业银行",
    "688599": "天合光能",
    "688036": "传音控股",
    "000725": "京东方A",
    "601899": "紫金矿业",
    "300059": "东方财富",
    "688111": "金山办公",
    "600309": "万华化学",
    "002594": "比亚迪",
}

DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "expected_period",
    "expected_title_keywords",
    "excluded_title_keywords",
    "planned_source",
    "planned_endpoint",
    "planned_output",
    "pdf_download",
    "pdf_parse",
    "ocr",
    "extraction",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "expected_period",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "title_match_status",
    "period_match_status",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "ocr_enabled",
    "extraction_enabled",
    "cninfo_request_count",
    "notes",
]

LIVE_QUALITY_COLUMNS = [
    "case_id",
    "company_code",
    "report_type",
    "expected_period",
    "retrieval_status",
    "title_match_status",
    "period_match_status",
    "quality_status",
    "lineage_status",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "notes",
]

RETRY_DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "expected_period",
    "original_failure_type",
    "retry_strategy",
    "planned_source",
    "planned_endpoint",
    "pdf_download",
    "pdf_parse",
    "ocr",
    "extraction",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

PHASE2_CORRECT_THRESHOLD = 18


@dataclass
class Phase2UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    expected_title_keywords: str
    excluded_title_keywords: str
    risk_level: str
    phase1_overlap: str
    phase2_include: str
    reason: str


@dataclass
class RetryUniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    original_failure_type: str
    original_failure_reason: str
    retry_include: str
    retry_strategy: str
    notes: str


def build_live_report_row(
    case: Phase2UniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "retrieval_status": str(record.get("retrieval_status") or ""),
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": str(record.get("announcement_time") or ""),
        "title_match_status": str(record.get("title_match_status") or ""),
        "period_match_status": str(record.get("period_match_status") or ""),
        "pdf_url_present": str(record.get("pdf_url_present") or "no"),
        "adjunct_url_present": str(record.get("adjunct_url_present") or "no"),
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "cninfo_request_count": str(cninfo_request_count),
        "notes": str(record.get("notes") or ""),
    }


def is_case_correct(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    if row.get("retrieval_status") != "found":
        return False
    if row.get("title_match_status") != "pass":
        return False
    if row.get("period_match_status") != "pass":
        return False
    return True


def has_red_line_violation(stats: tiny_live.LiveStats, rows: List[Dict[str, str]]) -> bool:
    if stats.pdf_downloaded_count > 0 or stats.pdf_parsed_count > 0:
        return True
    for row in rows:
        if row.get("pdf_downloaded") not in ("0", "no", ""):
            return True
        if row.get("pdf_parsed") not in ("0", "no", ""):
            return True
        if row.get("quality_status") == "verified":
            return True
    return False


def compute_phase2_execution_gate(
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues or case_count != REQUIRED_UNIVERSE_SIZE:
        return "FAIL_REVIEW_REQUIRED"
    correct_count = sum(1 for row in rows if is_case_correct(row))
    if correct_count >= PHASE2_CORRECT_THRESHOLD:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def write_live_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_live_quality_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in LIVE_QUALITY_COLUMNS})
    return report_path


def write_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    correct_count = sum(1 for row in rows if is_case_correct(row))
    title_mismatch = sum(
        1 for row in rows if row.get("title_match_status") not in ("pass", "n/a", "")
    )
    period_mismatch = sum(
        1 for row in rows if row.get("period_match_status") not in ("pass", "n/a", "")
    )
    lines = [
        "# CNINFO A 类 Phase 2 Metadata Expansion — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2 live metadata validation · **无 PDF 下载/解析** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | live |",
        f"| universe size | {len(rows)} |",
        f"| correct report-type metadata | {correct_count} |",
        f"| success (found) | {stats.success_count} |",
        f"| failure | {stats.failure_count} |",
        f"| wrong report-type match | {stats.wrong_report_type_count} |",
        f"| title mismatch | {title_mismatch} |",
        f"| period mismatch | {period_mismatch} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| PDF downloaded | **{stats.pdf_downloaded_count}** |",
        f"| PDF parsed | **{stats.pdf_parsed_count}** |",
        f"| OCR | **0** |",
        f"| extraction | **0** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "",
        "## Endpoint usage",
        "",
        f"- topSearch/query: {stats.endpoint_hits.get('topSearch', 0)}",
        f"- hisAnnouncement/query: {stats.endpoint_hits.get('hisAnnouncement', 0)}",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- Phase 1 baseline untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_metadata_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready** · Phase 2 limited expansion only",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    expected_title_keywords: str
    excluded_title_keywords: str
    risk_level: str
    phase1_overlap: str
    phase2_include: str
    reason: str


def validate_retry_output_root(output_root: str) -> Tuple[bool, str]:
    """retry 输出仅允许 retry 隔离根；禁止写入 Phase 2 expansion / Phase 1 baseline。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_RETRY_OUTPUT_ROOT)
    expansion = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    phase1 = _normalize_output_root(PHASE1_OUTPUT_ROOT)

    if root == expansion or root.startswith(expansion + os.sep):
        return False, PHASE2_EXPANSION_WRITE_FORBIDDEN
    if root == phase1 or root.startswith(phase1 + os.sep):
        return False, PHASE1_BASELINE_WRITE_FORBIDDEN
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, RETRY_OUTPUT_ROOT_VIOLATION


def load_retry_universe(path: str) -> List[RetryUniverseCase]:
    cases: List[RetryUniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(
                RetryUniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    report_type=str(row.get("report_type", "")).strip(),
                    expected_period=str(row.get("expected_period", "")).strip(),
                    original_failure_type=str(
                        row.get("original_failure_type", "")
                    ).strip(),
                    original_failure_reason=str(
                        row.get("original_failure_reason", "")
                    ).strip(),
                    retry_include=str(row.get("retry_include", "")).strip().lower(),
                    retry_strategy=str(row.get("retry_strategy", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return cases


def retry_to_phase2_case(case: RetryUniverseCase) -> Phase2UniverseCase:
    return Phase2UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        report_type=case.report_type,
        expected_period=case.expected_period,
        expected_title_keywords="",
        excluded_title_keywords="",
        risk_level="low",
        phase1_overlap="no",
        phase2_include="yes",
        reason=case.notes,
    )


def validate_retry_case(case: RetryUniverseCase) -> List[str]:
    issues: List[str] = []
    if case.case_id in SUCCESSFUL_CASE_IDS:
        issues.append(SUCCESSFUL_CASE_IN_RETRY_FORBIDDEN)
    if case.case_id not in RETRY_ALLOWED_CASE_IDS:
        issues.append(NON_RETRY_CASE_REJECTED)
    if case.retry_include != "yes":
        issues.append(RETRY_INCLUDE_REQUIRED)
    if not case.company_code:
        issues.append("company_code_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    issues.extend(validate_universe_code_name(retry_to_phase2_case(case)))
    return issues


def validate_retry_universe_size(cases: List[RetryUniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.retry_include == "yes"]
    if len(included) != RETRY_REQUIRED_UNIVERSE_SIZE:
        return (
            False,
            f"{RETRY_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {RETRY_REQUIRED_UNIVERSE_SIZE}",
        )
    return True, ""


def enforce_retry_approval_gate(args: argparse.Namespace) -> None:
    wrong_flags = (
        (args.approve_a_class_phase2_metadata_expansion, PHASE2_APPROVAL_REQUIRED),
        (args.approve_a_class_tiny_live_metadata, TINY_LIVE_APPROVAL_WRONG),
        (args.approve_phase1_tiny_live_metadata, PHASE1_TINY_LIVE_APPROVAL_WRONG),
        (args.approve_full_harvest, tiny_live.FORBIDDEN_APPROVE_FULL_HARVEST),
        (args.approve_phase2_smoke_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE2),
        (args.approve_phase3_batch_500_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE3),
        (args.approve_b_class_tiny_live_validation, tiny_live.FORBIDDEN_APPROVE_B_CLASS),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not args.approve_a_class_phase2_failed_retry:
        print(f"ERROR: {RETRY_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def build_retry_dryrun_row(case: RetryUniverseCase, issues: List[str]) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"retry dry-run; CNINFO not called; metadata only; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"original_failure={case.original_failure_type}"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "original_failure_type": case.original_failure_type,
        "retry_strategy": case.retry_strategy,
        "planned_source": source_id,
        "planned_endpoint": planned_endpoints_for_case(retry_to_phase2_case(case)),
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def process_retry_dry_run(
    cases: List[RetryUniverseCase],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = validate_retry_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(build_retry_dryrun_row(case, issues))
    return rows, universe_issues


def write_retry_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_retry_dryrun_summary(
    output_paths: Dict[str, str],
    case_count: int,
    universe_issues: List[str],
) -> str:
    planned_ok = case_count - len(universe_issues)
    lines = [
        "# CNINFO A 类 Phase 2 Failed Retry — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** isolated retry dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | retry_dry_run |",
        f"| retry cases | {case_count} |",
        f"| planned_ok | {planned_ok} |",
        f"| successful 12 excluded | **yes** |",
        f"| universe_issues | {len(universe_issues)} |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB / MinIO / RAG | **0** |",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_failed_retry_planning_gate = {RETRY_PLANNING_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_retry_live_report_row(
    retry_case: RetryUniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    retrieval = str(record.get("retrieval_status") or "")
    wrong_rt = "1" if retrieval == "title_mismatch" else "0"
    return {
        "case_id": retry_case.case_id,
        "company_code": retry_case.company_code,
        "company_name": retry_case.company_name,
        "market": retry_case.market,
        "report_type": retry_case.report_type,
        "expected_period": retry_case.expected_period,
        "original_failure_type": retry_case.original_failure_type,
        "retry_retrieval_status": retrieval,
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": str(record.get("announcement_time") or ""),
        "title_match_status": str(record.get("title_match_status") or ""),
        "period_match_status": str(record.get("period_match_status") or ""),
        "wrong_report_type": wrong_rt,
        "pdf_url_present": str(record.get("pdf_url_present") or "no"),
        "adjunct_url_present": str(record.get("adjunct_url_present") or "no"),
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "cninfo_request_count": str(cninfo_request_count),
        "notes": (
            f"isolated retry live; original={retry_case.original_failure_type}; "
            f"matching_logic={MATCHING_LOGIC_VERSION}; PDF not downloaded; "
            f"{record.get('notes', '')}"
        ),
    }


def is_retry_case_correct(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    if row.get("wrong_report_type") not in ("0", "no", ""):
        return False
    if row.get("retry_retrieval_status") != "found":
        return False
    if row.get("title_match_status") != "pass":
        return False
    if row.get("period_match_status") != "pass":
        return False
    return True


def compute_retry_execution_gate(
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues or case_count != RETRY_REQUIRED_UNIVERSE_SIZE:
        return "FAIL_REVIEW_REQUIRED"
    correct_count = sum(1 for row in rows if is_retry_case_correct(row))
    if correct_count >= RETRY_CORRECT_THRESHOLD:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def process_retry_live(
    retry_cases: List[RetryUniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for retry_case in retry_cases:
        if retry_case.retry_include != "yes":
            continue
        issues = validate_retry_case(retry_case)
        if issues:
            universe_issues.append(f"{retry_case.case_id}:{';'.join(issues)}")
            rows.append(
                build_retry_live_report_row(
                    retry_case,
                    {
                        "retrieval_status": "universe_invalid",
                        "quality_status": "blocked",
                        "lineage_status": "needs_review",
                        "announcement_id": "",
                        "announcement_title": "",
                        "announcement_time": "",
                        "title_match_status": "n/a",
                        "period_match_status": "n/a",
                        "pdf_url_present": "no",
                        "adjunct_url_present": "no",
                        "notes": "; ".join(issues),
                    },
                    0,
                )
            )
            stats.failure_count += 1
            continue

        phase2_case = retry_to_phase2_case(retry_case)
        tl_case = to_tiny_live_case(phase2_case)
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        live_row = build_retry_live_report_row(retry_case, record, case_cninfo_requests)
        snapshot_path = os.path.join(
            output_paths["raw_metadata"], f"{retry_case.case_id}_retry.json"
        )
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": retry_case.__dict__,
                    "mode": "retry_live",
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": DOWNLOAD_PDF,
                    "pdf_parse_enabled": PARSE_PDF,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={retry_case.case_id} company_code={retry_case.company_code} "
            f"retry_retrieval_status={live_row['retry_retrieval_status']} "
            f"title_match={live_row.get('title_match_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def write_retry_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_retry_live_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in RETRY_LIVE_QUALITY_COLUMNS})
    return report_path


def write_retry_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    correct_count = sum(1 for row in rows if is_retry_case_correct(row))
    wrong_rt = sum(1 for row in rows if row.get("wrong_report_type") == "1")
    title_mismatch = sum(
        1 for row in rows if row.get("title_match_status") not in ("pass", "n/a", "")
    )
    period_mismatch = sum(
        1 for row in rows if row.get("period_match_status") not in ("pass", "n/a", "")
    )
    lines = [
        "# CNINFO A 类 Phase 2 Failed Retry — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** isolated retry live · **8 failed cases only** · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | retry_live |",
        f"| retry cases | {len(rows)} |",
        f"| retry correct | {correct_count} |",
        f"| success (found) | {stats.success_count} |",
        f"| failure | {stats.failure_count} |",
        f"| wrong report-type | {wrong_rt} |",
        f"| title mismatch | {title_mismatch} |",
        f"| period mismatch | {period_mismatch} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| PDF downloaded | **{stats.pdf_downloaded_count}** |",
        f"| PDF parsed | **{stats.pdf_parsed_count}** |",
        f"| OCR / extraction | **0** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "",
        "## Safety",
        "",
        "- successful 12 cases not rerun: **yes**",
        "- Phase 2 expansion reports untouched: **yes**",
        "- Phase 1 baseline untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_failed_retry_execution_gate = {gate}",
        "a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED (unchanged)",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def _normalize_output_root(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    """输出仅允许 Phase 2 expansion 隔离根；禁止写入 Phase 1 / C-class harvest。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    phase1 = _normalize_output_root(PHASE1_OUTPUT_ROOT)
    c_harvest = _normalize_output_root(C_CLASS_HARVEST_ROOT)

    if root == phase1 or root.startswith(phase1 + os.sep):
        return False, PHASE1_BASELINE_WRITE_FORBIDDEN
    if root == c_harvest or root.startswith(c_harvest + os.sep):
        return False, "c_class_harvest_output_root_forbidden"
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, OUTPUT_ROOT_VIOLATION


def ensure_output_layout(output_root: str) -> Dict[str, str]:
    paths = {
        "root": output_root,
        "reports": os.path.join(output_root, "reports"),
        "raw_metadata": os.path.join(output_root, "raw_metadata"),
    }
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    return paths


def load_universe(path: str) -> List[Phase2UniverseCase]:
    cases: List[Phase2UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(
                Phase2UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    report_type=str(row.get("report_type", "")).strip(),
                    expected_period=str(row.get("expected_period", "")).strip(),
                    expected_title_keywords=str(
                        row.get("expected_title_keywords", "")
                    ).strip(),
                    excluded_title_keywords=str(
                        row.get("excluded_title_keywords", "")
                    ).strip(),
                    risk_level=str(row.get("risk_level", "")).strip(),
                    phase1_overlap=str(row.get("phase1_overlap", "")).strip().lower(),
                    phase2_include=str(row.get("phase2_include", "")).strip().lower(),
                    reason=str(row.get("reason", "")).strip(),
                )
            )
    return cases


def validate_universe_code_name(case: Phase2UniverseCase) -> List[str]:
    issues: List[str] = []
    known = KNOWN_COMPANY_NAMES.get(case.company_code)
    if not known:
        return issues
    if known not in case.company_name and case.company_name not in known:
        issues.append(
            f"code_name_mismatch:{case.company_code}:{case.company_name}!={known}"
        )
    return issues


def validate_phase2_case(case: Phase2UniverseCase) -> List[str]:
    issues: List[str] = []
    if not PHASE2_CASE_ID_PATTERN.match(case.case_id or ""):
        issues.append(NON_PHASE2_CASE_REJECTED)
    if case.phase2_include != "yes":
        issues.append(PHASE2_INCLUDE_REQUIRED)
    if case.phase1_overlap not in ("", "no"):
        issues.append(PHASE1_OVERLAP_REJECTED)
    if case.company_code in PHASE1_COMPANY_CODES:
        issues.append(f"{PHASE1_OVERLAP_REJECTED}:code:{case.company_code}")
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    issues.extend(validate_universe_code_name(case))
    return issues


def validate_universe_size(cases: List[Phase2UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.phase2_include == "yes"]
    if len(included) != REQUIRED_UNIVERSE_SIZE:
        return (
            False,
            f"{UNIVERSE_SIZE_VIOLATION}: got {len(included)} expected {REQUIRED_UNIVERSE_SIZE}",
        )
    return True, ""


def validate_report_type_mix(cases: List[Phase2UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.phase2_include == "yes"]
    counts: Dict[str, int] = {}
    for case in included:
        counts[case.report_type] = counts.get(case.report_type, 0) + 1
    for report_type, expected in EXPECTED_REPORT_TYPE_MIX.items():
        if counts.get(report_type, 0) != expected:
            return (
                False,
                f"{REPORT_TYPE_MIX_VIOLATION}: {report_type}="
                f"{counts.get(report_type, 0)} expected {expected}",
            )
    return True, ""


def count_phase1_overlap(cases: List[Phase2UniverseCase]) -> int:
    count = 0
    for case in cases:
        if case.phase1_overlap not in ("", "no"):
            count += 1
        if case.company_code in PHASE1_COMPANY_CODES:
            count += 1
    return count


def enforce_forbidden_options(args: argparse.Namespace) -> None:
    checks = (
        (args.download_pdf, PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
        (args.parse_pdf, PDF_PARSE_REQUESTED_NOT_ALLOWED),
        (args.enable_ocr, OCR_REQUESTED_NOT_ALLOWED),
        (args.enable_extraction, EXTRACTION_REQUESTED_NOT_ALLOWED),
        (args.write_db, DB_WRITE_REQUESTED_NOT_ALLOWED),
        (args.write_minio, MINIO_WRITE_REQUESTED_NOT_ALLOWED),
        (args.run_rag, RAG_REQUESTED_NOT_ALLOWED),
        (args.mark_verified, VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
        (args.mark_production_ready, PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
    )
    for enabled, err in checks:
        if enabled:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(2)


def enforce_live_approval_gate(args: argparse.Namespace) -> None:
    wrong_flags = (
        (args.approve_a_class_tiny_live_metadata, TINY_LIVE_APPROVAL_WRONG),
        (args.approve_phase1_tiny_live_metadata, PHASE1_TINY_LIVE_APPROVAL_WRONG),
        (args.approve_full_harvest, tiny_live.FORBIDDEN_APPROVE_FULL_HARVEST),
        (args.approve_phase2_smoke_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE2),
        (args.approve_phase3_batch_500_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE3),
        (args.approve_b_class_tiny_live_validation, tiny_live.FORBIDDEN_APPROVE_B_CLASS),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not args.approve_a_class_phase2_metadata_expansion:
        print(f"ERROR: {PHASE2_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def planned_endpoints_for_case(_case: Phase2UniverseCase) -> str:
    return f"{tiny_live.TOPSEARCH_ENDPOINT};{tiny_live.HIS_ANNOUNCEMENT_ENDPOINT}"


def to_tiny_live_case(case: Phase2UniverseCase) -> tiny_live.UniverseCase:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    return tiny_live.UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        report_type=case.report_type,
        expected_period=case.expected_period,
        source_name=source_id,
        risk_level=case.risk_level,
        reason=case.reason,
    )


def build_dryrun_row(case: Phase2UniverseCase, issues: List[str]) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"dry-run; CNINFO not called; metadata only; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"storage_status=not_attempted"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "expected_title_keywords": case.expected_title_keywords,
        "excluded_title_keywords": case.excluded_title_keywords,
        "planned_source": source_id,
        "planned_endpoint": planned_endpoints_for_case(case),
        "planned_output": PLANNED_OUTPUT_OBJECTS,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def process_dry_run(
    cases: List[Phase2UniverseCase],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.phase2_include != "yes":
            continue
        issues = validate_phase2_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(build_dryrun_row(case, issues))
    return rows, universe_issues


def process_live(
    cases: List[Phase2UniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.phase2_include != "yes":
            continue
        issues = validate_phase2_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            invalid = build_live_report_row(
                case,
                {
                    "retrieval_status": "universe_invalid",
                    "quality_status": "blocked",
                    "lineage_status": "needs_review",
                    "announcement_id": "",
                    "announcement_title": "",
                    "announcement_time": "",
                    "title_match_status": "n/a",
                    "period_match_status": "n/a",
                    "pdf_url_present": "no",
                    "adjunct_url_present": "no",
                    "notes": "; ".join(issues),
                },
                0,
            )
            rows.append(invalid)
            stats.failure_count += 1
            continue

        tl_case = to_tiny_live_case(case)
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        snapshot_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}.json")
        live_row = build_live_report_row(case, record, case_cninfo_requests)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": "live_phase2",
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": DOWNLOAD_PDF,
                    "pdf_parse_enabled": PARSE_PDF,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={case.case_id} company_code={case.company_code} "
            f"retrieval_status={live_row['retrieval_status']} "
            f"title_match={live_row.get('title_match_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def write_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_dryrun_summary(
    output_paths: Dict[str, str],
    case_count: int,
    universe_issues: List[str],
    report_type_mix: Dict[str, int],
    phase1_overlap_count: int,
) -> str:
    planned_ok = case_count - len(universe_issues)
    mix_line = " / ".join(f"{k}={v}" for k, v in sorted(report_type_mix.items()))
    lines = [
        "# CNINFO A 类 Phase 2 Metadata Expansion — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2 runner dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | dry_run |",
        f"| universe size | {case_count} |",
        f"| planned_ok | {planned_ok} |",
        f"| universe_issues | {len(universe_issues)} |",
        f"| report-type mix | {mix_line} |",
        f"| phase1_overlap | **{phase1_overlap_count}** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- Phase 1 baseline untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_metadata_runner_gate = {RUNNER_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CNINFO A-class Phase2 metadata expansion（dry-run default）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")

    parser.add_argument("--universe-csv", default=DEFAULT_UNIVERSE_CSV)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--approve-a-class-phase2-metadata-expansion",
        action="store_true",
        help="显式批准 A-class Phase 2 metadata expansion live",
    )
    parser.add_argument(
        "--approve-a-class-phase2-failed-retry",
        action="store_true",
        help="显式批准 A-class Phase 2 failed-case isolated retry live",
    )
    parser.add_argument(
        "--retry-failed-only",
        action="store_true",
        help="isolated retry 模式：仅 8 个 failed case",
    )
    parser.add_argument("--approve-a-class-tiny-live-metadata", action="store_true")
    parser.add_argument("--approve-phase1-tiny-live-metadata", action="store_true")
    parser.add_argument("--approve-full-harvest", action="store_true")
    parser.add_argument("--approve-phase2-smoke-harvest", action="store_true")
    parser.add_argument("--approve-phase3-batch-500-harvest", action="store_true")
    parser.add_argument("--approve-b-class-tiny-live-validation", action="store_true")
    parser.add_argument("--download-pdf", action="store_true")
    parser.add_argument("--parse-pdf", action="store_true")
    parser.add_argument("--enable-ocr", action="store_true")
    parser.add_argument("--enable-extraction", action="store_true")
    parser.add_argument("--write-db", action="store_true")
    parser.add_argument("--write-minio", action="store_true")
    parser.add_argument("--run-rag", action="store_true")
    parser.add_argument("--mark-verified", action="store_true")
    parser.add_argument("--mark-production-ready", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.retry_failed_only:
        if not args.universe_csv or args.universe_csv == DEFAULT_UNIVERSE_CSV:
            args.universe_csv = DEFAULT_RETRY_UNIVERSE_CSV
        if not args.output_root or args.output_root == DEFAULT_OUTPUT_ROOT:
            args.output_root = DEFAULT_RETRY_OUTPUT_ROOT

    enforce_forbidden_options(args)

    if args.mode == "live":
        if args.retry_failed_only:
            enforce_retry_approval_gate(args)
        else:
            enforce_live_approval_gate(args)

    if args.retry_failed_only:
        ok_root, root_err = validate_retry_output_root(args.output_root)
    else:
        ok_root, root_err = validate_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))

    if args.retry_failed_only:
        retry_cases = load_retry_universe(args.universe_csv)
        if args.limit is not None:
            retry_cases = retry_cases[: args.limit]

        ok_size, size_err = validate_retry_universe_size(retry_cases)
        if not ok_size:
            print(f"ERROR: {size_err}", file=sys.stderr)
            return 2

        included_retry = [c for c in retry_cases if c.retry_include == "yes"]

        if args.mode == "live":
            stats = tiny_live.LiveStats()
            rows, universe_issues = process_retry_live(
                included_retry, output_paths, stats
            )
            gate = compute_retry_execution_gate(
                stats, rows, universe_issues, len(included_retry)
            )
            report_path = write_retry_live_report(rows, output_paths)
            quality_path = write_retry_live_quality_report(rows, output_paths)
            summary_path = write_retry_live_summary(
                output_paths, stats, rows, universe_issues, gate
            )
            correct_count = sum(1 for row in rows if is_retry_case_correct(row))
            wrong_rt = sum(1 for row in rows if row.get("wrong_report_type") == "1")
            print(f"mode=retry_live cases={len(included_retry)} cninfo_calls={stats.cninfo_requests}")
            print(f"success={stats.success_count} failure={stats.failure_count}")
            print(f"correct={correct_count} wrong_report_type={wrong_rt}")
            print(f"pdf_downloaded={stats.pdf_downloaded_count} pdf_parsed={stats.pdf_parsed_count}")
            print(f"gate=a_class_phase2_failed_retry_execution_gate={gate}")
            print(f"report={report_path}")
            print(f"quality={quality_path}")
            print(f"summary={summary_path}")
            if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
                return 1
            return 0

        rows, universe_issues = process_retry_dry_run(retry_cases)
        report_path = write_retry_dryrun_report(rows, output_paths)
        summary_path = write_retry_dryrun_summary(
            output_paths, len(included_retry), universe_issues
        )
        planned_ok = len(included_retry) - len(universe_issues)
        print(f"mode=retry_dry_run cases={len(included_retry)} planned_ok={planned_ok} cninfo_calls=0")
        print(f"gate=a_class_phase2_failed_retry_planning_gate={RETRY_PLANNING_GATE}")
        print(f"retry_dryrun_report={report_path}")
        print(f"retry_dryrun_summary={summary_path}")
        if universe_issues:
            return 1
        return 0

    cases = load_universe(args.universe_csv)
    if args.limit is not None:
        cases = cases[: args.limit]

    ok_size, size_err = validate_universe_size(cases)
    if not ok_size:
        print(f"ERROR: {size_err}", file=sys.stderr)
        return 2

    ok_mix, mix_err = validate_report_type_mix(cases)
    if not ok_mix:
        print(f"ERROR: {mix_err}", file=sys.stderr)
        return 2

    overlap_count = count_phase1_overlap(cases)
    if overlap_count > 0:
        print(f"ERROR: {PHASE1_OVERLAP_REJECTED}: count={overlap_count}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))

    included = [c for c in cases if c.phase2_include == "yes"]
    report_type_mix: Dict[str, int] = {}
    for case in included:
        report_type_mix[case.report_type] = report_type_mix.get(case.report_type, 0) + 1

    if args.mode == "live":
        stats = tiny_live.LiveStats()
        rows, universe_issues = process_live(cases, output_paths, stats)
        gate = compute_phase2_execution_gate(stats, rows, universe_issues, len(included))
        report_path = write_live_report(rows, output_paths)
        quality_path = write_live_quality_report(rows, output_paths)
        summary_path = write_live_summary(
            output_paths, stats, rows, universe_issues, gate
        )
        correct_count = sum(1 for row in rows if is_case_correct(row))
        print(f"mode=live cases={len(included)} cninfo_calls={stats.cninfo_requests}")
        print(f"success={stats.success_count} failure={stats.failure_count}")
        print(f"correct={correct_count} wrong_report_type={stats.wrong_report_type_count}")
        print(f"pdf_downloaded={stats.pdf_downloaded_count} pdf_parsed={stats.pdf_parsed_count}")
        print(f"gate=a_class_phase2_metadata_execution_gate={gate}")
        print(f"report={report_path}")
        print(f"quality={quality_path}")
        print(f"summary={summary_path}")
        if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
            return 1
        return 0

    rows, universe_issues = process_dry_run(cases)
    report_path = write_dryrun_report(rows, output_paths)
    summary_path = write_dryrun_summary(
        output_paths,
        len(included),
        universe_issues,
        report_type_mix,
        overlap_count,
    )
    planned_ok = len(included) - len(universe_issues)
    print(f"mode=dry_run cases={len(included)} planned_ok={planned_ok} cninfo_calls=0")
    print(f"gate=a_class_phase2_metadata_runner_gate={RUNNER_GATE}")
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    if universe_issues:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
