"""
CNINFO A-class Phase 1 tiny live metadata validation runner.

默认 dry-run：校验 universe · 输出隔离 · 质量规则，**不请求 CNINFO**。
--live 须 --approve-a-class-tiny-live-metadata；仅 metadata · 无 PDF 下载/解析。

Usage:
    python lab/run_cninfo_a_class_tiny_live_metadata_validation.py
    python lab/run_cninfo_a_class_tiny_live_metadata_validation.py --live \\
        --approve-a-class-tiny-live-metadata
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase1_tiny_live_metadata_universe.csv",
)
UNIVERSE_V2_DRAFT_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase1_tiny_live_metadata_universe_v2_draft.csv",
)
DEFAULT_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_tiny_live_metadata"
)
DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_OUTPUT_ROOT,
    "reports",
    "a_class_tiny_live_metadata_dryrun_report.csv",
)
DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_OUTPUT_ROOT,
    "reports",
    "a_class_tiny_live_metadata_dryrun_summary.md",
)
LIVE_REPORT_CSV = os.path.join(
    DEFAULT_OUTPUT_ROOT,
    "reports",
    "a_class_tiny_live_metadata_report.csv",
)
LIVE_SUMMARY_MD = os.path.join(
    DEFAULT_OUTPUT_ROOT,
    "reports",
    "a_class_tiny_live_metadata_summary.md",
)
QUALITY_REPORT_CSV = os.path.join(
    DEFAULT_OUTPUT_ROOT,
    "reports",
    "a_class_tiny_live_metadata_quality_report.csv",
)

C_CLASS_HARVEST_ROOT = os.path.join(BASE_DIR, "outputs", "harvest", "cninfo_c_class")
B_CLASS_VALIDATION_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tiny_live_validation"
)
D_CLASS_VALIDATION_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class"
)

HIS_ANNOUNCEMENT_ENDPOINT = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
TOPSEARCH_ENDPOINT = "https://www.cninfo.com.cn/new/information/topSearch/query"
SLEEP_SECONDS = 0.6
PAGE_SIZE = 30
REQUEST_TIMEOUT = 10

AJAX_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
        "ListedCompanyDataCollector/a-class-tiny-live"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.cninfo.com.cn/",
}

RUNNER_GATE = "READY_FOR_APPROVAL"
EXPECTED_UNIVERSE_SIZE = 5
ALLOWED_CASE_IDS: Set[str] = {"ALM001", "ALM002", "ALM003", "ALM004", "ALM005"}

VALID_REPORT_TYPES: Set[str] = {
    "annual_report",
    "semi_annual_report",
    "quarterly_report_q1",
    "quarterly_report_q3",
}

REPORT_TYPE_SOURCE_ID = {
    "annual_report": "cninfo_a_class_periodic_report_annual",
    "semi_annual_report": "cninfo_a_class_periodic_report_semi_annual",
    "quarterly_report_q1": "cninfo_a_class_periodic_report_quarterly",
    "quarterly_report_q3": "cninfo_a_class_periodic_report_quarterly",
}

REPORT_TYPE_KEYWORDS: Dict[str, List[str]] = {
    "annual_report": ["年度报告", "年报"],
    "semi_annual_report": ["半年度报告", "半年报"],
    "quarterly_report_q1": ["第一季度报告", "一季度报告"],
    "quarterly_report_q3": ["第三季度报告", "三季度报告"],
}

TITLE_EXCLUSIONS = [
    "披露提示性公告",
    "提示性公告",
    "业绩说明会",
    "投资者说明会",
    "摘要",
    "英文版",
    "解读",
    "说明会",
    "问询函",
    "英文",
    "English",
    "english",
]

# tiny universe 已知代码-简称对照（用于 universe code/name 一致性校验）
KNOWN_COMPANY_NAMES: Dict[str, str] = {
    "600000": "浦发银行",
    "300001": "特锐德",
    "688001": "华兴源创",
    "000858": "五粮液",
    "600519": "贵州茅台",
}

MATCHING_LOGIC_VERSION = "v2"
FIX_GATE = "READY_FOR_RERUN_APPROVAL"
CODE_NAME_MISMATCH = "code_name_mismatch"

# report_type 标题匹配：必须包含 / 必须拒绝
TITLE_MATCH_REQUIRE: Dict[str, List[str]] = {
    "annual_report": ["年度报告"],
    "semi_annual_report": ["半年度报告", "半年报"],
    "quarterly_report_q1": ["一季度报告", "第一季度报告", "Q1", "q1"],
    "quarterly_report_q3": ["三季度报告", "第三季度报告", "Q3", "q3"],
}

TITLE_MATCH_REJECT: Dict[str, List[str]] = {
    "annual_report": [
        "半年度报告",
        "半年报",
        "一季度报告",
        "第一季度报告",
        "三季度报告",
        "第三季度报告",
        "英文",
        "English",
        "english",
    ],
    "semi_annual_report": [
        "年度报告摘要",
        "英文",
        "English",
        "english",
    ],
    "quarterly_report_q1": ["英文", "English", "english"],
    "quarterly_report_q3": ["英文", "English", "english"],
}

ENGLISH_TITLE_REJECT = ["英文", "English", "english", "ENGLISH", "（英文）", "(英文)"]

PLANNED_OUTPUT_OBJECTS = "report_document;report_period_snapshot;document_lineage"

# 永久禁用 — 不可通过 CLI 开启
DOWNLOAD_PDF = False
PARSE_PDF = False
ENABLE_OCR = False
ENABLE_SECTION_EXTRACTION = False
ENABLE_TABLE_EXTRACTION = False
WRITE_VERIFIED = False
UPGRADE_TESTING_STABLE_SAMPLE = False
STORAGE_STATUS_PHASE1 = "not_attempted"

PDF_DOWNLOAD_ENABLED = DOWNLOAD_PDF
PDF_PARSE_ENABLED = PARSE_PDF

TINY_LIVE_APPROVAL_REQUIRED = "approve_a_class_tiny_live_metadata_required"
OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_a_class_tiny_live_metadata"
UNIVERSE_SIZE_VIOLATION = "universe_size_must_equal_5"
NON_ALM_CASE_FORBIDDEN = "non_alm_case_forbidden"
PDF_DOWNLOAD_FORBIDDEN = "pdf_download_permanently_disabled"
PDF_PARSE_FORBIDDEN = "pdf_parse_permanently_disabled"
FORBIDDEN_APPROVE_FULL_HARVEST = "approve_full_harvest_not_allowed_for_a_class_tiny_live"
FORBIDDEN_APPROVE_PHASE2 = "approve_phase2_smoke_harvest_not_allowed_for_a_class_tiny_live"
FORBIDDEN_APPROVE_PHASE3 = "approve_phase3_batch_500_harvest_not_allowed_for_a_class_tiny_live"
FORBIDDEN_APPROVE_B_CLASS = "approve_b_class_tiny_live_validation_not_allowed_for_a_class"
FORBIDDEN_APPROVE_B_CLASS_PHASE1 = "approve_phase1_tiny_live_metadata_not_allowed_for_a_class"

DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "report_type",
    "planned_source",
    "planned_endpoint",
    "planned_output",
    "pdf_download",
    "pdf_parse",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

LIVE_V2_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
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
    "notes",
]

LIVE_V2_QUALITY_COLUMNS = [
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

LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "report_type",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "notes",
]

QUALITY_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "report_type",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "notes",
]

_ORGID_CACHE: Dict[str, str] = {}


@dataclass
class UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    report_type: str
    expected_period: str
    source_name: str
    risk_level: str
    reason: str


@dataclass
class LiveStats:
    cninfo_requests: int = 0
    success_count: int = 0
    failure_count: int = 0
    pdf_downloaded_count: int = 0
    pdf_parsed_count: int = 0
    companies_executed: int = 0
    wrong_report_type_count: int = 0
    english_title_rejected_count: int = 0
    endpoint_hits: Dict[str, int] = field(
        default_factory=lambda: {"topSearch": 0, "hisAnnouncement": 0}
    )


def _normalize_output_root(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    forbidden_roots = (
        _normalize_output_root(C_CLASS_HARVEST_ROOT),
        _normalize_output_root(B_CLASS_VALIDATION_ROOT),
        _normalize_output_root(D_CLASS_VALIDATION_ROOT),
    )
    for forbidden in forbidden_roots:
        if root == forbidden or root.startswith(forbidden + os.sep):
            return False, f"forbidden_output_root:{forbidden}"
    return False, OUTPUT_ROOT_VIOLATION


def ensure_output_layout(output_root: str) -> Dict[str, str]:
    paths = {
        "root": output_root,
        "reports": os.path.join(output_root, "reports"),
        "planned": os.path.join(output_root, "planned"),
        "raw_metadata": os.path.join(output_root, "raw_metadata"),
    }
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    return paths


def load_universe(path: str) -> List[UniverseCase]:
    cases: List[UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(
                UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    report_type=str(row.get("report_type", "")).strip(),
                    expected_period=str(row.get("expected_period", "")).strip(),
                    source_name=str(row.get("source_name", "")).strip(),
                    risk_level=str(row.get("risk_level", "")).strip(),
                    reason=str(row.get("reason", "")).strip(),
                )
            )
    return cases


def validate_universe_size(cases: List[UniverseCase]) -> Optional[str]:
    if len(cases) != EXPECTED_UNIVERSE_SIZE:
        return UNIVERSE_SIZE_VIOLATION
    return None


def validate_universe_case(case: UniverseCase, *, strict_code_name: bool = False) -> List[str]:
    issues: List[str] = []
    if not case.case_id:
        issues.append("case_id_missing")
    elif case.case_id not in ALLOWED_CASE_IDS:
        issues.append(f"{NON_ALM_CASE_FORBIDDEN}:{case.case_id}")
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.source_name:
        issues.append("source_name_missing")
    if strict_code_name:
        issues.extend(validate_universe_code_name(case))
    return issues


def validate_universe_code_name(case: UniverseCase) -> List[str]:
    """校验 universe 中 company_code 与 company_name 是否一致。"""
    issues: List[str] = []
    known = KNOWN_COMPANY_NAMES.get(case.company_code)
    if not known:
        return issues
    if known not in case.company_name and case.company_name not in known:
        issues.append(f"{CODE_NAME_MISMATCH}:{case.company_code}:{case.company_name}!={known}")
    return issues


def _has_english_title(title: str) -> bool:
    return any(marker in title for marker in ENGLISH_TITLE_REJECT)


def _expected_period_in_title(title: str, expected_period: str, report_type: str) -> bool:
    year = (expected_period or "")[:4]
    if not year:
        return True
    if year not in title:
        return False
    if report_type == "semi_annual_report":
        return "半年" in title
    if report_type == "quarterly_report_q1":
        return any(p in title for p in ("一季度", "第一季度", "Q1", "q1"))
    if report_type == "quarterly_report_q3":
        return any(p in title for p in ("三季度", "第三季度", "Q3", "q3"))
    return True


def match_title_for_report_type(
    title: str,
    report_type: str,
    expected_period: str = "",
) -> Tuple[bool, str]:
    """
    report_type 专用标题匹配。
    返回 (matched, reason)；不匹配时 reason 说明原因。
    """
    clean = _strip_html(title)
    if not clean:
        return False, "empty_title"
    if _has_english_title(clean):
        return False, "english_title_rejected"
    if _title_excluded(clean):
        return False, "title_excluded"

    required = TITLE_MATCH_REQUIRE.get(report_type, [])
    if required and not any(p in clean for p in required):
        return False, "required_pattern_missing"

    for reject in TITLE_MATCH_REJECT.get(report_type, []):
        if reject in clean:
            return False, f"reject_pattern:{reject}"

    if report_type == "annual_report":
        if "半年" in clean:
            return False, "annual_vs_semi_annual"
        if any(p in clean for p in ("一季度", "第一季度", "三季度", "第三季度")):
            return False, "annual_vs_quarterly"

    if expected_period and not _expected_period_in_title(clean, expected_period, report_type):
        return False, "expected_period_mismatch"

    return True, ""


def assess_title_match_quality(
    title: str,
    report_type: str,
    expected_period: str,
) -> Tuple[str, str, str]:
    """
    标题与 report_type / expected_period 对齐评估。
    返回 (retrieval_status, quality_status, mismatch_reason)。
    """
    matched, reason = match_title_for_report_type(title, report_type, expected_period)
    if matched:
        return "found", "pass", ""
    return "title_mismatch", "needs_review", reason


def enforce_live_approval_gate(args: argparse.Namespace) -> None:
    wrong_flags = (
        (args.approve_full_harvest, FORBIDDEN_APPROVE_FULL_HARVEST),
        (args.approve_phase2_smoke_harvest, FORBIDDEN_APPROVE_PHASE2),
        (args.approve_phase3_batch_500_harvest, FORBIDDEN_APPROVE_PHASE3),
        (args.approve_b_class_tiny_live_validation, FORBIDDEN_APPROVE_B_CLASS),
        (args.approve_phase1_tiny_live_metadata, FORBIDDEN_APPROVE_B_CLASS_PHASE1),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    if args.download_pdf:
        print(f"ERROR: {PDF_DOWNLOAD_FORBIDDEN}", file=sys.stderr)
        sys.exit(2)
    if args.enable_parser:
        print(f"ERROR: {PDF_PARSE_FORBIDDEN}", file=sys.stderr)
        sys.exit(2)
    if args.mode == "live" and not args.approve_a_class_tiny_live_metadata:
        print(f"ERROR: {TINY_LIVE_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def planned_endpoints_for_case(case: UniverseCase) -> str:
    return f"{TOPSEARCH_ENDPOINT};{HIS_ANNOUNCEMENT_ENDPOINT}"


def build_dryrun_row(
    case: UniverseCase,
    issues: List[str],
    *,
    universe_version: str = "v1",
    matching_logic_version: str = MATCHING_LOGIC_VERSION,
) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"dry-run; CNINFO not called; metadata only; storage_status=not_attempted; "
        f"universe={universe_version}; matching_logic={matching_logic_version}"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "report_type": case.report_type,
        "planned_source": f"{source_id}|{case.source_name}",
        "planned_endpoint": planned_endpoints_for_case(case),
        "planned_output": PLANNED_OUTPUT_OBJECTS,
        "pdf_download": "disabled",
        "pdf_parse": "disabled",
        "cninfo_call_planned": "no",
        "dryrun_status": status,
        "notes": notes,
    }


def process_dry_run(
    cases: List[UniverseCase],
    *,
    universe_version: str = "v1",
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    strict = universe_version == "v2_draft"
    for case in cases:
        issues = validate_universe_case(case, strict_code_name=strict)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(
            build_dryrun_row(
                case,
                issues,
                universe_version=universe_version,
            )
        )
    return rows, universe_issues


def write_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_dryrun_v2_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_v2_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_dryrun_v2_summary(
    output_paths: Dict[str, str],
    case_count: int,
    universe_issues: List[str],
) -> str:
    planned_ok = case_count - len(universe_issues)
    lines = [
        "# CNINFO A 类 Tiny Live Metadata V2 Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** caveat fix v2 dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | dry_run_v2 |",
        f"| universe size | {case_count} |",
        f"| planned_ok | {planned_ok} |",
        f"| universe_issues | {len(universe_issues)} |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| universe_version | **v2_draft** |",
        "| CNINFO calls | **0** |",
        "| PDF download | **false** |",
        "| PDF parse | **false** |",
        "",
        "## Fixes applied (offline)",
        "",
        "- ALM003 company_name corrected to 华兴源创 (688001)",
        "- annual_report rejects 半年度/季报/英文标题",
        "- quarterly rejects 英文/English 标题",
        "- universe code/name consistency validation",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_tiny_live_metadata_fix_gate = {FIX_GATE}",
        "```",
        "",
        f"execution gate unchanged: **PASS_WITH_CAVEAT** (prior live run)",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_v2_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def write_dryrun_summary(
    output_paths: Dict[str, str],
    case_count: int,
    universe_issues: List[str],
    mode: str,
) -> str:
    planned_ok = case_count - len(universe_issues)
    lines = [
        "# CNINFO A 类 Tiny Live Metadata Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** runner dry-run · **无 CNINFO** · **无 live** · **无 PDF 下载/解析**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| mode | {mode} |",
        f"| universe size | {case_count} |",
        f"| planned_ok | {planned_ok} |",
        f"| universe_issues | {len(universe_issues)} |",
        "| CNINFO calls | **0** |",
        "| PDF download | **disabled** |",
        "| PDF parse | **disabled** |",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_tiny_live_metadata_runner_gate = {RUNNER_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def _format_ann_time(ts: Any) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    except (TypeError, ValueError, OSError):
        return ""


def infer_column(company_code: str) -> str:
    code = (company_code or "").strip()
    if code.startswith(("60", "68")):
        return "sse"
    return "szse"


def build_pdf_url(adjunct_url: Optional[str]) -> str:
    if not adjunct_url:
        return ""
    return "http://static.cninfo.com.cn/" + str(adjunct_url).lstrip("/")


def build_query_payload(
    code: str, orgid: str, column: str, keyword: str, se_date: str
) -> Dict[str, Any]:
    stock_value = f"{code},{orgid}" if orgid else code
    return {
        "stock": stock_value,
        "searchkey": keyword,
        "plate": "",
        "category": "",
        "trade": "",
        "column": column or "szse",
        "tabName": "fulltext",
        "pageSize": PAGE_SIZE,
        "pageNum": 1,
        "seDate": se_date,
        "sortName": "",
        "sortType": "",
        "secid": "",
        "isHLtitle": "true",
    }


def _title_excluded(title: str) -> bool:
    return any(ex in title for ex in TITLE_EXCLUSIONS)


def _title_matches_report_type(
    title: str, report_type: str, expected_period: str = ""
) -> bool:
    matched, _ = match_title_for_report_type(title, report_type, expected_period)
    return matched


def _sec_code_matches(rec: Dict[str, Any], company_code: str) -> bool:
    sec = str(rec.get("secCode") or "").strip()
    if sec:
        parts = [p.strip() for p in sec.replace(";", ",").split(",") if p.strip()]
        return company_code in parts
    return True


def assess_match_status(
    title: str,
    report_type: str,
    expected_period: str,
) -> Tuple[str, str]:
    """返回 (title_match_status, period_match_status)。"""
    type_matched, _ = match_title_for_report_type(title, report_type, "")
    if not type_matched:
        return "fail", "n/a"
    if expected_period and not _expected_period_in_title(title, expected_period, report_type):
        return "pass", "fail"
    return "pass", "pass"


def _live_row_base(case: UniverseCase) -> Dict[str, str]:
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "pdf_downloaded": "no",
        "pdf_parsed": "no",
    }


def _search_date_window(case: UniverseCase) -> str:
    year = (case.expected_period or "")[:4]
    if case.report_type == "annual_report":
        y = int(year) if year.isdigit() else 2024
        return f"{y}-01-01 ~ {y + 1}-04-30"
    if case.report_type == "semi_annual_report":
        return f"{year}-01-01 ~ {year}-09-30"
    if case.report_type == "quarterly_report_q1":
        y = year or "2025"
        return f"{y}-01-01 ~ {y}-05-31"
    if case.report_type == "quarterly_report_q3":
        y = year or "2024"
        return f"{y}-07-01 ~ {y}-11-30"
    return "2023-01-01 ~ 2025-12-31"


def _count_english_rejected(records: List[Dict[str, Any]], company_code: str) -> int:
    count = 0
    for rec in records:
        title = _strip_html(str(rec.get("announcementTitle") or ""))
        if title and _sec_code_matches(rec, company_code) and _has_english_title(title):
            count += 1
    return count


def resolve_orgid(company_code: str, stats: LiveStats) -> Tuple[str, str]:
    if company_code in _ORGID_CACHE:
        return _ORGID_CACHE[company_code], ""
    try:
        resp = requests.post(
            TOPSEARCH_ENDPOINT,
            data={"keyWord": company_code, "maxNum": 10},
            headers=AJAX_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        stats.cninfo_requests += 1
        stats.endpoint_hits["topSearch"] = stats.endpoint_hits.get("topSearch", 0) + 1
        time.sleep(SLEEP_SECONDS)
        if resp.status_code == 429:
            return "", "rate_limited"
        if not resp.ok:
            return "", "network_error"
        items = resp.json()
        if not isinstance(items, list):
            return "", "empty_response"
        for item in items:
            if str(item.get("code")) == str(company_code):
                org = (item.get("orgId") or "").strip()
                if org:
                    _ORGID_CACHE[company_code] = org
                    return org, ""
        if items:
            org = (items[0].get("orgId") or "").strip()
            if org:
                _ORGID_CACHE[company_code] = org
                return org, ""
    except requests.exceptions.Timeout:
        return "", "network_error"
    except Exception:
        return "", "network_error"
    return "", "empty_response"


def fetch_announcements(
    payload: Dict[str, Any], stats: LiveStats
) -> Tuple[List[Dict[str, Any]], str, str]:
    try:
        resp = requests.post(
            HIS_ANNOUNCEMENT_ENDPOINT,
            data=payload,
            headers=AJAX_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        stats.cninfo_requests += 1
        stats.endpoint_hits["hisAnnouncement"] = stats.endpoint_hits.get("hisAnnouncement", 0) + 1
        time.sleep(SLEEP_SECONDS)
        if resp.status_code == 429:
            return [], "network_error", "rate_limited"
        if resp.status_code != 200:
            return [], "network_error", f"http_{resp.status_code}"
        data = resp.json()
        if not isinstance(data, dict):
            return [], "empty_response", "invalid_json"
        return list(data.get("announcements") or []), "ok", ""
    except requests.exceptions.Timeout:
        return [], "network_error", "network_timeout"
    except Exception as exc:
        return [], "network_error", str(exc)


def _pick_best_record(
    records: List[Dict[str, Any]], case: UniverseCase
) -> Optional[Dict[str, Any]]:
    candidates: List[Dict[str, Any]] = []
    for rec in records:
        title = _strip_html(str(rec.get("announcementTitle") or ""))
        if not title or not _sec_code_matches(rec, case.company_code):
            continue
        if not _title_matches_report_type(title, case.report_type, case.expected_period):
            continue
        candidates.append(rec)
    if not candidates:
        return None
    candidates.sort(key=lambda r: int(r.get("announcementTime") or 0), reverse=True)
    return candidates[0]


def assess_live_quality(
    adjunct_url: str, pdf_url: str, retrieval_status: str
) -> Tuple[str, str]:
    if retrieval_status != "found":
        return "needs_review", "needs_review"
    if pdf_url and adjunct_url:
        return "pass", "discovered"
    if pdf_url or adjunct_url:
        return "needs_review", "needs_review"
    return "needs_review", "not_found"


def execute_live_case(case: UniverseCase, stats: LiveStats) -> Dict[str, str]:
    stats.companies_executed += 1
    base = _live_row_base(case)
    org_id, org_err = resolve_orgid(case.company_code, stats)
    if not org_id:
        stats.failure_count += 1
        return {
            **base,
            "retrieval_status": org_err or "network_error",
            "quality_status": "needs_review",
            "lineage_status": "needs_review",
            "announcement_id": "",
            "announcement_title": "",
            "announcement_time": "",
            "title_match_status": "n/a",
            "period_match_status": "n/a",
            "pdf_url_present": "no",
            "adjunct_url_present": "no",
            "notes": f"orgId resolution failed: {org_err}",
        }

    column = infer_column(case.company_code)
    se_date = _search_date_window(case)
    keywords = REPORT_TYPE_KEYWORDS.get(case.report_type, [""])
    records: List[Dict[str, Any]] = []
    last_err = ""
    picked: Optional[Dict[str, Any]] = None

    for keyword in keywords:
        payload = build_query_payload(case.company_code, org_id, column, keyword, se_date)
        batch, status, err_msg = fetch_announcements(payload, stats)
        stats.english_title_rejected_count += _count_english_rejected(batch, case.company_code)
        if status == "network_error" and err_msg == "rate_limited":
            stats.failure_count += 1
            return {
                **base,
                "retrieval_status": "network_error",
                "quality_status": "needs_review",
                "lineage_status": "needs_review",
                "announcement_id": "",
                "announcement_title": "",
                "announcement_time": "",
                "title_match_status": "n/a",
                "period_match_status": "n/a",
                "pdf_url_present": "no",
                "adjunct_url_present": "no",
                "notes": "rate_limited; stopped",
            }
        if batch:
            records.extend(batch)
            picked = _pick_best_record(batch, case)
            if picked:
                break
        last_err = err_msg or status

    if not picked and records:
        picked = _pick_best_record(records, case)

    if not picked:
        stats.failure_count += 1
        return {
            **base,
            "retrieval_status": "not_found",
            "quality_status": "needs_review",
            "lineage_status": "not_found",
            "announcement_id": "",
            "announcement_title": "",
            "announcement_time": "",
            "title_match_status": "fail",
            "period_match_status": "n/a",
            "pdf_url_present": "no",
            "adjunct_url_present": "no",
            "notes": (
                f"no v2 matching periodic report; records={len(records)}; "
                f"last_err={last_err}; matching_logic={MATCHING_LOGIC_VERSION}"
            ),
        }

    title = _strip_html(str(picked.get("announcementTitle") or ""))
    ann_id = str(picked.get("announcementId") or "")
    adjunct = str(picked.get("adjunctUrl") or "").strip()
    pdf_url = build_pdf_url(adjunct) if adjunct else ""
    ann_time = _format_ann_time(picked.get("announcementTime"))
    title_match_status, period_match_status = assess_match_status(
        title, case.report_type, case.expected_period
    )

    retrieval_status, _, mismatch_reason = assess_title_match_quality(
        title, case.report_type, case.expected_period
    )
    if retrieval_status == "title_mismatch":
        stats.failure_count += 1
        stats.wrong_report_type_count += 1
        return {
            **base,
            "retrieval_status": "title_mismatch",
            "quality_status": "needs_review",
            "lineage_status": "needs_review",
            "announcement_id": ann_id,
            "announcement_title": title,
            "announcement_time": ann_time,
            "title_match_status": title_match_status,
            "period_match_status": period_match_status,
            "pdf_url_present": "yes" if pdf_url else "no",
            "adjunct_url_present": "yes" if adjunct else "no",
            "notes": (
                f"title mismatch: {mismatch_reason}; matching_logic={MATCHING_LOGIC_VERSION}"
            ),
        }

    quality_status, lineage_status = assess_live_quality(adjunct, pdf_url, "found")
    stats.success_count += 1
    return {
        **base,
        "retrieval_status": "found",
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "announcement_id": ann_id,
        "announcement_title": title,
        "announcement_time": ann_time,
        "title_match_status": title_match_status,
        "period_match_status": period_match_status,
        "pdf_url_present": "yes" if pdf_url else "no",
        "adjunct_url_present": "yes" if adjunct else "no",
        "notes": (
            f"v2 live metadata; storage_status={STORAGE_STATUS_PHASE1}; "
            f"matching_logic={MATCHING_LOGIC_VERSION}; PDF not downloaded"
        ),
        "_raw_announcement": picked,
        "_org_id": org_id,
    }


def process_live(
    cases: List[UniverseCase],
    output_paths: Dict[str, str],
    stats: LiveStats,
    *,
    live_version: str = "v1",
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    strict = live_version == "v2"
    report_columns = LIVE_V2_REPORT_COLUMNS if live_version == "v2" else LIVE_REPORT_COLUMNS
    for case in cases:
        issues = validate_universe_case(case, strict_code_name=strict)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            invalid = {
                **_live_row_base(case),
                "retrieval_status": "universe_invalid",
                "quality_status": "blocked",
                "lineage_status": "needs_review",
                "announcement_id": "",
                "announcement_title": "",
                "announcement_time": "",
                "pdf_url_present": "no",
                "adjunct_url_present": "no",
                "notes": "; ".join(issues),
            }
            if live_version == "v2":
                invalid["title_match_status"] = "n/a"
                invalid["period_match_status"] = "n/a"
            rows.append({k: str(invalid.get(k, "")) for k in report_columns})
            stats.failure_count += 1
            continue

        record = execute_live_case(case, stats)
        snapshot_name = f"{case.case_id}_v2.json" if live_version == "v2" else f"{case.case_id}.json"
        snapshot_path = os.path.join(output_paths["raw_metadata"], snapshot_name)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": f"live_{live_version}",
                    "cninfo_called": True,
                    "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                    "pdf_parse_enabled": PDF_PARSE_ENABLED,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": {k: record.get(k, "") for k in report_columns},
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append({k: str(record.get(k, "")) for k in report_columns})
        print(
            f"case_id={case.case_id} company_code={case.company_code} "
            f"retrieval_status={record['retrieval_status']} "
            f"title_match={record.get('title_match_status', 'n/a')} "
            f"quality_status={record['quality_status']}",
            flush=True,
        )
    return rows, universe_issues


def write_live_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_quality_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in QUALITY_REPORT_COLUMNS})
    return report_path


def compute_v2_execution_gate(
    stats: LiveStats,
    case_count: int,
    universe_issues: List[str],
    correct_type_count: int,
) -> str:
    if stats.pdf_downloaded_count > 0 or stats.pdf_parsed_count > 0:
        return "FAIL"
    if universe_issues or case_count != EXPECTED_UNIVERSE_SIZE:
        return "FAIL"
    if correct_type_count >= 4:
        return "PASS_WITH_CAVEAT"
    return "FAIL"


def write_live_v2_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_v2_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_V2_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_live_v2_quality_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_v2_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_V2_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in LIVE_V2_QUALITY_COLUMNS})
    return report_path


def write_live_v2_summary(
    output_paths: Dict[str, str],
    stats: LiveStats,
    case_count: int,
    universe_issues: List[str],
    gate: str,
    correct_type_count: int,
) -> str:
    lines = [
        "# CNINFO A 类 Tiny Live Metadata V2 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** v2 rerun · matching v2 · universe v2 · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | live_v2 |",
        f"| universe size | {case_count} |",
        f"| correct report-type metadata | {correct_type_count} |",
        f"| success (found) | {stats.success_count} |",
        f"| failure | {stats.failure_count} |",
        f"| wrong report-type match | {stats.wrong_report_type_count} |",
        f"| english titles rejected (skipped) | {stats.english_title_rejected_count} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| PDF downloaded | **{stats.pdf_downloaded_count}** |",
        f"| PDF parsed | **{stats.pdf_parsed_count}** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_tiny_live_metadata_v2_execution_gate = {gate}",
        "```",
        "",
        "prior: `a_class_tiny_live_metadata_execution_gate = PASS_WITH_CAVEAT`（v1 · 不变）",
        "",
        "**不是 PASS** · **不是 production_ready** · **不是 verified**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_v2_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def compute_execution_gate(
    stats: LiveStats,
    case_count: int,
    universe_issues: List[str],
    found_count: int,
) -> str:
    if stats.pdf_downloaded_count > 0 or stats.pdf_parsed_count > 0:
        return "FAIL"
    if universe_issues or case_count != EXPECTED_UNIVERSE_SIZE:
        return "FAIL"
    if found_count >= 4:
        return "PASS_WITH_CAVEAT"
    return "FAIL"


def write_live_summary(
    output_paths: Dict[str, str],
    stats: LiveStats,
    case_count: int,
    universe_issues: List[str],
    gate: str,
    found_count: int,
) -> str:
    lines = [
        "# CNINFO A 类 Tiny Live Metadata Validation 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** A-class tiny live metadata validation · **无 PDF 下载/解析** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| mode | live |",
        f"| universe size | {case_count} |",
        f"| companies executed | {stats.companies_executed} |",
        f"| metadata found | {found_count} |",
        f"| success (found) | {stats.success_count} |",
        f"| failure | {stats.failure_count} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| PDF downloaded | **{stats.pdf_downloaded_count}** |",
        f"| PDF parsed | **{stats.pdf_parsed_count}** |",
        "",
        "## Endpoint usage",
        "",
        f"- topSearch/query: {stats.endpoint_hits.get('topSearch', 0)}",
        f"- hisAnnouncement/query: {stats.endpoint_hits.get('hisAnnouncement', 0)}",
        "",
        "## QA",
        "",
        f"- only {case_count} companies: **{'yes' if case_count == 5 else 'no'}**",
        "- metadata only: **yes**",
        "- no PDF download: **yes**",
        "- no PDF parsing: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- C-class untouched: **yes**",
        "- B-class untouched: **yes**",
        "- D-class untouched: **yes**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_tiny_live_metadata_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 production_ready** · **不是 verified** · tiny sample only",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_tiny_live_metadata_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CNINFO A-class Phase1 tiny live metadata validation（dry-run default）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")

    parser.add_argument("--universe-csv", default=DEFAULT_UNIVERSE_CSV)
    parser.add_argument("--universe", dest="universe_csv", help="universe CSV 别名")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--approve-a-class-tiny-live-metadata",
        action="store_true",
        help="显式批准 A-class Phase 1 tiny live metadata validation",
    )
    parser.add_argument("--approve-full-harvest", action="store_true")
    parser.add_argument("--approve-phase2-smoke-harvest", action="store_true")
    parser.add_argument("--approve-phase3-batch-500-harvest", action="store_true")
    parser.add_argument("--approve-b-class-tiny-live-validation", action="store_true")
    parser.add_argument("--approve-phase1-tiny-live-metadata", action="store_true")
    parser.add_argument(
        "--download-pdf",
        action="store_true",
        help="永久禁用；传入即拒绝",
    )
    parser.add_argument(
        "--enable-parser",
        action="store_true",
        help="永久禁用；传入即拒绝",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--dry-run-v2",
        action="store_true",
        help="v2 dry-run：使用 universe v2 draft · 写入 v2 dryrun 报告",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.mode == "live":
        enforce_live_approval_gate(args)

    if args.download_pdf or args.enable_parser:
        enforce_live_approval_gate(args)

    ok_root, root_err = validate_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    universe_csv = args.universe_csv
    if args.dry_run_v2:
        universe_csv = UNIVERSE_V2_DRAFT_CSV
        if not os.path.isfile(universe_csv):
            print(f"ERROR: universe v2 draft not found: {universe_csv}", file=sys.stderr)
            return 2

    cases = load_universe(universe_csv)
    if args.limit is not None:
        cases = cases[: args.limit]

    size_err = validate_universe_size(cases)
    if size_err:
        print(f"ERROR: {size_err}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))

    if args.mode == "live":
        live_version = "v2" if _normalize_output_root(universe_csv) == _normalize_output_root(
            UNIVERSE_V2_DRAFT_CSV
        ) or "universe_v2" in os.path.basename(universe_csv) else "v1"
        stats = LiveStats()
        rows, universe_issues = process_live(
            cases, output_paths, stats, live_version=live_version
        )
        if live_version == "v2":
            correct_type_count = sum(
                1
                for r in rows
                if r.get("retrieval_status") == "found"
                and r.get("title_match_status") == "pass"
            )
            gate = compute_v2_execution_gate(
                stats, len(cases), universe_issues, correct_type_count
            )
            report_path = write_live_v2_report(rows, output_paths)
            quality_path = write_live_v2_quality_report(rows, output_paths)
            summary_path = write_live_v2_summary(
                output_paths,
                stats,
                len(cases),
                universe_issues,
                gate,
                correct_type_count,
            )
            print(f"mode=live_v2 cases={len(cases)} cninfo_calls={stats.cninfo_requests}")
            print(f"success={stats.success_count} failure={stats.failure_count}")
            print(
                f"wrong_report_type={stats.wrong_report_type_count} "
                f"english_rejected={stats.english_title_rejected_count}"
            )
            print(
                f"pdf_downloaded={stats.pdf_downloaded_count} "
                f"pdf_parsed={stats.pdf_parsed_count}"
            )
            print(f"gate=a_class_tiny_live_metadata_v2_execution_gate={gate}")
            print(f"v2_report={report_path}")
            print(f"v2_quality={quality_path}")
            print(f"v2_summary={summary_path}")
        else:
            found_count = sum(1 for r in rows if r.get("retrieval_status") == "found")
            gate = compute_execution_gate(stats, len(cases), universe_issues, found_count)
            report_path = write_live_report(rows, output_paths)
            quality_path = write_quality_report(rows, output_paths)
            summary_path = write_live_summary(
                output_paths, stats, len(cases), universe_issues, gate, found_count
            )
            print(f"mode=live cases={len(cases)} cninfo_calls={stats.cninfo_requests}")
            print(f"success={stats.success_count} failure={stats.failure_count}")
            print(
                f"pdf_downloaded={stats.pdf_downloaded_count} "
                f"pdf_parsed={stats.pdf_parsed_count}"
            )
            print(f"gate=a_class_tiny_live_metadata_execution_gate={gate}")
            print(f"report={report_path}")
            print(f"quality={quality_path}")
            print(f"summary={summary_path}")
        if universe_issues or gate == "FAIL":
            return 1
        return 0

    universe_version = "v2_draft" if args.dry_run_v2 else "v1"
    rows, universe_issues = process_dry_run(cases, universe_version=universe_version)
    if args.dry_run_v2:
        report_path = write_dryrun_v2_report(rows, output_paths)
        summary_path = write_dryrun_v2_summary(output_paths, len(cases), universe_issues)
        print(f"mode=dry_run_v2 cases={len(cases)} cninfo_calls=0")
        print(f"gate=a_class_tiny_live_metadata_fix_gate={FIX_GATE}")
        print(f"v2_dryrun_report={report_path}")
        print(f"v2_dryrun_summary={summary_path}")
    else:
        report_path = write_dryrun_report(rows, output_paths)
        summary_path = write_dryrun_summary(output_paths, len(cases), universe_issues, args.mode)
        print(f"mode={args.mode} cases={len(cases)} cninfo_calls=0")
        print(f"gate=a_class_tiny_live_metadata_runner_gate={RUNNER_GATE}")
        print(f"dryrun_report={report_path}")
        print(f"dryrun_summary={summary_path}")
    if universe_issues:
        print(f"universe_issues={len(universe_issues)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
