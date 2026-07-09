"""
CNINFO B-class Phase 1 tiny live metadata validation runner.

默认 dry-run：校验 universe · 输出隔离 · 质量规则，**不请求 CNINFO**。
--live 须 --approve-b-class-tiny-live-validation；仅 metadata · 无 PDF 下载/解析。

Usage:
    python lab/run_cninfo_b_class_tiny_live_validation.py
    python lab/run_cninfo_b_class_tiny_live_validation.py --live \\
        --approve-b-class-tiny-live-validation
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
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_DIR = os.path.join(BASE_DIR, "lab")
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from validate_cninfo_b_class_category_routing import route_title  # noqa: E402

DEFAULT_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase1_tiny_live_validation_universe.csv",
)
DEFAULT_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tiny_live_validation"
)
VALIDATION_REPORT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tiny_live_validation_report.csv"
)
VALIDATION_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tiny_live_validation_summary.md"
)
QUALITY_REPORT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tiny_live_validation_quality_report.csv"
)
CATEGORIES_YAML = os.path.join(BASE_DIR, "config", "cninfo_announcement_categories.yaml")
PHASE3_FORBIDDEN_ROOT = os.path.join(
    BASE_DIR, "outputs", "harvest", "cninfo_c_class", "phase3_batch_500_001"
)

TOPSEARCH_URL = "https://www.cninfo.com.cn/new/information/topSearch/query"
REQUEST_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
SLEEP_SECONDS = 0.6
PAGE_SIZE = 30
REQUEST_TIMEOUT = 10

AJAX_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
        "ListedCompanyDataCollector/b-class-tiny-live"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.cninfo.com.cn/",
}

PERIODIC_TITLE_EXCLUSIONS = [
    "披露提示性公告", "提示性公告", "业绩说明会", "投资者说明会", "监管问询函",
    "预告公告", "说明会", "交流会", "问询函", "回复公告", "关于披露",
    "关于延期披露", "延期披露", "摘要", "解读",
]
PERIODIC_POSITIVE = ["年度报告", "年报", "半年度报告", "半年报"]

TINY_LIVE_APPROVAL_REQUIRED = "approve_b_class_tiny_live_validation_required"
FORBIDDEN_APPROVE_FULL_HARVEST = "approve_full_harvest_not_allowed_for_b_class_tiny_live"
FORBIDDEN_APPROVE_PHASE2 = "approve_phase2_smoke_harvest_not_allowed_for_b_class_tiny_live"
FORBIDDEN_APPROVE_PHASE3 = "approve_phase3_batch_500_harvest_not_allowed_for_b_class_tiny_live"
OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_b_class_tiny_live_validation"

ALLOWED_ENDPOINTS: Set[str] = {"EP001", "EP002", "EP004", "EP005"}
BLOCKED_ENDPOINTS: Set[str] = {"EP003", "EP006", "EP007"}
ALLOWED_SOURCE_TYPES: Set[str] = {
    "cninfo_periodic_report_pdf",
    "cninfo_general_announcement_pdf",
}
SOURCE_TYPE_PRIMARY_ENDPOINT = {
    "cninfo_periodic_report_pdf": "EP004",
    "cninfo_general_announcement_pdf": "EP005",
}

REPORT_COLUMNS = [
    "case_id", "company_code", "company_name", "endpoint_id",
    "announcement_id", "announcement_title", "announcement_time", "announcement_category",
    "pdf_url", "adjunct_url", "source_endpoint", "retrieval_status",
    "quality_status", "lineage_status", "error_type", "notes",
]

QUALITY_REQUIRED_FIELDS = [
    "company_code", "org_id", "announcement_id", "announcement_title", "announcement_time",
    "document_id", "retrieval_time", "quality_status", "pdf_url", "adjunct_url",
    "source_endpoint", "lineage_status",
]

PDF_DOWNLOAD_ENABLED = False
PDF_PARSE_ENABLED = False

_ORGID_CACHE: Dict[str, str] = {}


@dataclass
class UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    source_type: str
    endpoint_scope: List[str]
    expected_fields: str
    risk_level: str
    reason: str


@dataclass
class LiveStats:
    cninfo_requests: int = 0
    endpoint_hits: Dict[str, int] = field(default_factory=lambda: {"EP001": 0, "EP002": 0, "EP004": 0, "EP005": 0})
    success_count: int = 0
    failure_count: int = 0
    companies_executed: int = 0


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def _normalize_output_root(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    if PHASE3_FORBIDDEN_ROOT in root or root == _normalize_output_root(PHASE3_FORBIDDEN_ROOT):
        return False, "phase3_batch_500_output_root_forbidden"
    return False, OUTPUT_ROOT_VIOLATION


def ensure_output_layout(output_root: str) -> Dict[str, str]:
    paths = {
        "root": output_root,
        "raw_metadata": os.path.join(output_root, "raw_metadata"),
        "quality": os.path.join(output_root, "quality"),
        "reports": os.path.join(output_root, "reports"),
    }
    for key in paths:
        os.makedirs(paths[key], exist_ok=True)
    return paths


def load_universe(path: str) -> List[UniverseCase]:
    cases: List[UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            scope = [s.strip() for s in (row.get("endpoint_scope") or "").split(";") if s.strip()]
            cases.append(
                UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    source_type=str(row.get("source_type", "")).strip(),
                    endpoint_scope=scope,
                    expected_fields=str(row.get("expected_fields", "")).strip(),
                    risk_level=str(row.get("risk_level", "")).strip(),
                    reason=str(row.get("reason", "")).strip(),
                )
            )
    return cases


def validate_universe_case(case: UniverseCase) -> List[str]:
    issues: List[str] = []
    if not _is_present(case.case_id):
        issues.append("case_id_missing")
    if not _is_present(case.company_code):
        issues.append("company_code_missing")
    if not _is_present(case.company_name):
        issues.append("company_name_missing")
    if case.source_type not in ALLOWED_SOURCE_TYPES:
        issues.append(f"unsupported_source_type:{case.source_type}")
    if not case.endpoint_scope:
        issues.append("endpoint_scope_empty")
    for ep in case.endpoint_scope:
        if ep in BLOCKED_ENDPOINTS:
            issues.append(f"endpoint_blocked:{ep}")
        if ep not in ALLOWED_ENDPOINTS:
            issues.append(f"endpoint_not_allowed:{ep}")
    primary = SOURCE_TYPE_PRIMARY_ENDPOINT.get(case.source_type)
    if primary and primary not in case.endpoint_scope:
        issues.append(f"primary_endpoint_missing:{primary}")
    if "EP001" not in case.endpoint_scope:
        issues.append("EP001_required_in_scope")
    return issues


def enforce_live_approval_gate(args: argparse.Namespace) -> None:
    if args.approve_full_harvest:
        print(f"ERROR: {FORBIDDEN_APPROVE_FULL_HARVEST}", file=sys.stderr)
        sys.exit(2)
    if args.approve_phase2_smoke_harvest:
        print(f"ERROR: {FORBIDDEN_APPROVE_PHASE2}", file=sys.stderr)
        sys.exit(2)
    if args.approve_phase3_batch_500_harvest:
        print(f"ERROR: {FORBIDDEN_APPROVE_PHASE3}", file=sys.stderr)
        sys.exit(2)
    if args.mode == "live" and not args.approve_b_class_tiny_live_validation:
        print(f"ERROR: {TINY_LIVE_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def infer_column(company_code: str) -> str:
    code = (company_code or "").strip()
    if code.startswith(("60", "68")):
        return "sse"
    if code.startswith(("43", "92", "83")):
        return "bj"
    return "szse"


def build_pdf_url(adjunct_url: Optional[str]) -> str:
    if not adjunct_url:
        return ""
    return "http://static.cninfo.com.cn/" + str(adjunct_url).lstrip("/")


def build_query_payload(code: str, orgid: str, column: str, keyword: str, se_date: str) -> Dict[str, Any]:
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


def _format_ann_date(ts: Any) -> str:
    t = _format_ann_time(ts)
    return t[:10] if t else ""


def _document_id(announcement_id: str) -> str:
    if not announcement_id:
        return ""
    return "doc_live_" + hashlib.sha256(announcement_id.encode()).hexdigest()[:16]


def _raw_hash(payload: str) -> str:
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()


def resolve_orgid(company_code: str, stats: LiveStats) -> Tuple[str, str]:
    if company_code in _ORGID_CACHE:
        return _ORGID_CACHE[company_code], ""
    try:
        resp = requests.post(
            TOPSEARCH_URL,
            data={"keyWord": company_code, "maxNum": 10},
            headers=AJAX_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        stats.cninfo_requests += 1
        stats.endpoint_hits["EP002"] = stats.endpoint_hits.get("EP002", 0) + 1
        time.sleep(SLEEP_SECONDS)
        if resp.status_code == 429:
            return "", "network_error"
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
        stats.cninfo_requests += 0
        return "", "network_error"
    except Exception:
        return "", "network_error"
    return "", "empty_response"


def fetch_announcements(payload: Dict[str, Any], stats: LiveStats) -> Tuple[List[Dict[str, Any]], str, str]:
    try:
        resp = requests.post(
            REQUEST_URL, data=payload, headers=AJAX_HEADERS, timeout=REQUEST_TIMEOUT
        )
        stats.cninfo_requests += 1
        stats.endpoint_hits["EP001"] = stats.endpoint_hits.get("EP001", 0) + 1
        time.sleep(SLEEP_SECONDS)
        if resp.status_code == 429:
            return [], "network_error", "rate_limited"
        if resp.status_code != 200:
            return [], "network_error", f"http_{resp.status_code}"
        data = resp.json()
        if not isinstance(data, dict):
            return [], "empty_response", "invalid_json"
        return list(data.get("announcements") or []), "found", ""
    except requests.exceptions.Timeout:
        return [], "network_error", "network_timeout"
    except Exception as exc:
        return [], "network_error", str(exc)


def _title_excluded(title: str) -> bool:
    return any(ex in title for ex in PERIODIC_TITLE_EXCLUSIONS)


def _title_periodic_match(title: str) -> bool:
    return any(p in title for p in PERIODIC_POSITIVE)


def _sec_code_matches(rec: Dict[str, Any], company_code: str) -> bool:
    sec = str(rec.get("secCode") or "").strip()
    if sec:
        parts = [p.strip() for p in sec.replace(";", ",").split(",") if p.strip()]
        return company_code in parts
    return True


def _pick_periodic(records: List[Dict[str, Any]], company_code: str) -> Optional[Dict[str, Any]]:
    candidates = []
    for rec in records:
        title = _strip_html(str(rec.get("announcementTitle") or ""))
        if not title or not _sec_code_matches(rec, company_code):
            continue
        if _title_excluded(title):
            continue
        if not _title_periodic_match(title):
            continue
        candidates.append(rec)
    if not candidates:
        return None
    candidates.sort(key=lambda r: int(r.get("announcementTime") or 0), reverse=True)
    return candidates[0]


def _pick_general(records: List[Dict[str, Any]], company_code: str) -> Optional[Dict[str, Any]]:
    candidates = []
    for rec in records:
        title = _strip_html(str(rec.get("announcementTitle") or ""))
        if not title or not _sec_code_matches(rec, company_code):
            continue
        candidates.append(rec)
    if not candidates:
        return None
    candidates.sort(key=lambda r: int(r.get("announcementTime") or 0), reverse=True)
    return candidates[0]


def _detect_duplicate_ids(records: List[Dict[str, Any]]) -> bool:
    ids = [str(r.get("announcementId") or "") for r in records if r.get("announcementId")]
    return len(ids) != len(set(ids))


def _classify_category(title: str, categories_config: Dict[str, Any], source_type: str) -> Tuple[str, str]:
    route = route_title(title, categories_config)
    predicted = route.predicted_route_to or ""
    if source_type == "cninfo_periodic_report_pdf":
        if predicted == "cninfo_periodic_report_pdf":
            return "periodic_report", ""
        if route.predicted_document_type:
            return route.predicted_document_type, ""
    if predicted == "cninfo_general_announcement_pdf":
        return "general_announcement", ""
    if route.false_positive_reason or not predicted:
        return "unknown", "review_later"
    return "unknown", "review_later"


def assess_quality_rules(record: Dict[str, Any]) -> Tuple[str, str, str, str]:
    missing = [f for f in QUALITY_REQUIRED_FIELDS if not _is_present(record.get(f))]
    pdf_missing = not _is_present(record.get("pdf_url")) or not _is_present(record.get("adjunct_url"))
    category = record.get("announcement_category") or ""
    category_status = record.get("category_status") or ""
    duplicate_flag = record.get("duplicate_announcement_id_detected") is True

    error_type = ""
    notes_parts: List[str] = []

    if duplicate_flag:
        error_type = "duplicate_announcement_id"
        notes_parts.append("duplicate detected; no auto merge; dedup_decision_required")

    if category == "unknown" or category_status == "review_later":
        notes_parts.append("unknown category allowed; category_status=review_later")

    if pdf_missing:
        notes_parts.append("missing pdf_url allowed; quality_status=needs_review")
        return "needs_review", record.get("lineage_status") or "needs_review", error_type or "missing_pdf_url", "; ".join(notes_parts) or "missing pdf_url"

    if missing:
        return "needs_review", "needs_review", "required_field_missing", f"missing: {','.join(missing)}"

    if record.get("quality_status") == "verified":
        return "needs_review", record.get("lineage_status") or "discovered", "verified_not_allowed", "verified not allowed"

    qs = str(record.get("quality_status") or "pass")
    ls = str(record.get("lineage_status") or "discovered")
    return qs, ls, error_type, "; ".join(notes_parts) if notes_parts else "quality_checks_pass"


def build_dry_run_record(case: UniverseCase, endpoint_id: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "endpoint_id": endpoint_id,
        "announcement_id": "",
        "announcement_title": "",
        "announcement_time": "",
        "announcement_category": "",
        "pdf_url": "",
        "adjunct_url": "",
        "source_endpoint": REQUEST_URL,
        "retrieval_status": "dry_run_planned",
        "quality_status": "needs_review",
        "lineage_status": "not_retrieved",
        "error_type": "not_executed",
        "notes": "dry-run; CNINFO not called",
        "org_id": "",
        "document_id": "",
        "retrieval_time": now,
    }


def execute_live_case(
    case: UniverseCase,
    categories_config: Dict[str, Any],
    stats: LiveStats,
) -> Dict[str, Any]:
    primary_ep = SOURCE_TYPE_PRIMARY_ENDPOINT[case.source_type]
    stats.endpoint_hits[primary_ep] = stats.endpoint_hits.get(primary_ep, 0) + 1
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    se_date = "2024-01-01 ~ 2025-06-30"
    keyword = "年度报告" if case.source_type == "cninfo_periodic_report_pdf" else ""

    org_id, org_err = resolve_orgid(case.company_code, stats)
    if not org_id:
        stats.failure_count += 1
        return {
            "case_id": case.case_id,
            "company_code": case.company_code,
            "company_name": case.company_name,
            "endpoint_id": primary_ep,
            "announcement_id": "",
            "announcement_title": "",
            "announcement_time": "",
            "announcement_category": "",
            "pdf_url": "",
            "adjunct_url": "",
            "source_endpoint": REQUEST_URL,
            "retrieval_status": org_err or "network_error",
            "quality_status": "needs_review",
            "lineage_status": "needs_review",
            "error_type": org_err or "network_error",
            "notes": "EP002 orgId resolution failed",
            "org_id": "",
            "document_id": "",
            "retrieval_time": now,
        }

    column = infer_column(case.company_code)
    payload = build_query_payload(case.company_code, org_id, column, keyword, se_date)
    records, retrieval_status, err_msg = fetch_announcements(payload, stats)

    if retrieval_status == "network_error":
        stats.failure_count += 1
        return {
            "case_id": case.case_id,
            "company_code": case.company_code,
            "company_name": case.company_name,
            "endpoint_id": primary_ep,
            "announcement_id": "",
            "announcement_title": "",
            "announcement_time": "",
            "announcement_category": "",
            "pdf_url": "",
            "adjunct_url": "",
            "source_endpoint": REQUEST_URL,
            "retrieval_status": "network_error",
            "quality_status": "needs_review",
            "lineage_status": "needs_review",
            "error_type": "network_error",
            "notes": err_msg,
            "org_id": org_id,
            "document_id": "",
            "retrieval_time": now,
        }

    if not records:
        stats.failure_count += 1
        return {
            "case_id": case.case_id,
            "company_code": case.company_code,
            "company_name": case.company_name,
            "endpoint_id": primary_ep,
            "announcement_id": "",
            "announcement_title": "",
            "announcement_time": "",
            "announcement_category": "",
            "pdf_url": "",
            "adjunct_url": "",
            "source_endpoint": REQUEST_URL,
            "retrieval_status": "empty_response",
            "quality_status": "needs_review",
            "lineage_status": "needs_review",
            "error_type": "empty_response",
            "notes": "no announcements in response",
            "org_id": org_id,
            "document_id": "",
            "retrieval_time": now,
        }

    duplicate = _detect_duplicate_ids(records)
    picked = (
        _pick_periodic(records, case.company_code)
        if case.source_type == "cninfo_periodic_report_pdf"
        else _pick_general(records, case.company_code)
    )

    if not picked:
        stats.failure_count += 1
        return {
            "case_id": case.case_id,
            "company_code": case.company_code,
            "company_name": case.company_name,
            "endpoint_id": primary_ep,
            "announcement_id": "",
            "announcement_title": "",
            "announcement_time": "",
            "announcement_category": "",
            "pdf_url": "",
            "adjunct_url": "",
            "source_endpoint": REQUEST_URL,
            "retrieval_status": "not_found",
            "quality_status": "needs_review",
            "lineage_status": "needs_review",
            "error_type": "not_found",
            "notes": f"no matching title in {len(records)} records",
            "org_id": org_id,
            "document_id": "",
            "retrieval_time": now,
            "duplicate_announcement_id_detected": duplicate,
        }

    title = _strip_html(str(picked.get("announcementTitle") or ""))
    ann_id = str(picked.get("announcementId") or "")
    adjunct = str(picked.get("adjunctUrl") or "").strip() or None
    pdf_url = build_pdf_url(adjunct)
    ann_time = _format_ann_time(picked.get("announcementTime"))
    category, cat_status = _classify_category(title, categories_config, case.source_type)

    record: Dict[str, Any] = {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "endpoint_id": primary_ep,
        "announcement_id": ann_id,
        "announcement_title": title,
        "announcement_time": ann_time,
        "announcement_category": category,
        "category_status": cat_status,
        "pdf_url": pdf_url,
        "adjunct_url": adjunct or "",
        "source_endpoint": REQUEST_URL,
        "retrieval_status": "found",
        "quality_status": "pass",
        "lineage_status": "discovered",
        "error_type": "",
        "notes": "live metadata retrieved; PDF not downloaded",
        "org_id": org_id,
        "document_id": _document_id(ann_id),
        "retrieval_time": now,
        "duplicate_announcement_id_detected": duplicate,
        "raw_hash": _raw_hash(json.dumps(picked, ensure_ascii=False, sort_keys=True)),
        "raw_announcement": picked,
    }

    qs, ls, et, qnotes = assess_quality_rules(record)
    record["quality_status"] = qs
    record["lineage_status"] = ls
    record["error_type"] = et
    if qnotes:
        record["notes"] = f"{record['notes']}; {qnotes}"

    if record["retrieval_status"] == "found" and not et:
        stats.success_count += 1
    else:
        stats.failure_count += 1

    return record


def _print_progress(case: UniverseCase, record: Dict[str, Any]) -> None:
    rs = record.get("retrieval_status", "")
    ok = rs == "found" and record.get("quality_status") in ("pass", "needs_review")
    outcome = "success" if ok and rs == "found" else "failure"
    print(
        f"case_id={case.case_id} endpoint_id={record.get('endpoint_id')} "
        f"company_code={case.company_code} retrieval_status={rs} {outcome}",
        flush=True,
    )


def process_cases(
    cases: List[UniverseCase],
    mode: str,
    output_paths: Dict[str, str],
    categories_config: Optional[Dict[str, Any]] = None,
    stats: Optional[LiveStats] = None,
) -> Tuple[List[Dict[str, str]], List[str]]:
    report_rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    live_stats = stats or LiveStats()

    for case in cases:
        issues = validate_universe_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            primary = SOURCE_TYPE_PRIMARY_ENDPOINT.get(case.source_type, "EP001")
            row = build_dry_run_record(case, primary)
            row["retrieval_status"] = "universe_validation_failed"
            row["error_type"] = "universe_invalid"
            row["notes"] = "; ".join(issues)
            report_rows.append({k: str(row.get(k, "")) for k in REPORT_COLUMNS})
            continue

        if mode == "live":
            assert categories_config is not None
            live_stats.companies_executed += 1
            record = execute_live_case(case, categories_config, live_stats)
            _print_progress(case, record)
        else:
            primary_ep = SOURCE_TYPE_PRIMARY_ENDPOINT[case.source_type]
            record = build_dry_run_record(case, primary_ep)
            qs, ls, et, qnotes = assess_quality_rules(record)
            record["quality_status"] = qs
            record["lineage_status"] = ls
            record["error_type"] = et or record["error_type"]
            if qnotes:
                record["notes"] = f"{record['notes']}; {qnotes}"

        primary_ep = record.get("endpoint_id") or SOURCE_TYPE_PRIMARY_ENDPOINT.get(case.source_type, "EP001")
        snapshot_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}_{primary_ep}.json")
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": mode,
                    "cninfo_called": mode == "live",
                    "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                    "pdf_parse_enabled": PDF_PARSE_ENABLED,
                    "planned_endpoints": case.endpoint_scope,
                    "record": {k: record.get(k) for k in REPORT_COLUMNS},
                    "raw_announcement": record.get("raw_announcement"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        quality_path = os.path.join(output_paths["quality"], f"{case.case_id}.json")
        with open(quality_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case_id": case.case_id,
                    "quality_status": record["quality_status"],
                    "lineage_status": record["lineage_status"],
                    "error_type": record.get("error_type", ""),
                    "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                    "pdf_parse_enabled": PDF_PARSE_ENABLED,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        report_rows.append({k: str(record.get(k, "")) for k in REPORT_COLUMNS})

    return report_rows, universe_issues


def write_report(report_rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    isolated_report = os.path.join(
        output_paths["reports"], "cninfo_b_class_tiny_live_validation_report.csv"
    )
    for target in (isolated_report, VALIDATION_REPORT_CSV):
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=REPORT_COLUMNS)
            writer.writeheader()
            writer.writerows(report_rows)
    return isolated_report


def write_quality_report(report_rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    path = os.path.join(output_paths["reports"], "cninfo_b_class_tiny_live_validation_quality_report.csv")
    fields = ["case_id", "company_code", "quality_status", "lineage_status", "error_type", "retrieval_status", "notes"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in report_rows:
            w.writerow({k: row.get(k, "") for k in fields})
    with open(QUALITY_REPORT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in report_rows:
            w.writerow({k: row.get(k, "") for k in fields})
    return path


def write_live_summary(
    output_paths: Dict[str, str],
    mode: str,
    case_count: int,
    stats: LiveStats,
    universe_issues: List[str],
    gate: str,
) -> str:
    lines = [
        "# CNINFO B 类 Tiny Live Metadata Validation 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** 首次 B-class CNINFO metadata live validation · **无 PDF 下载/解析**",
        "",
        "## Counts",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| mode | {mode} |",
        f"| companies executed | {stats.companies_executed if mode == 'live' else case_count} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| success (found) | {stats.success_count} |",
        f"| failure | {stats.failure_count} |",
        f"| PDF download | **disabled** |",
        f"| PDF parse | **disabled** |",
        "",
        "## Endpoint usage",
        "",
    ]
    for ep in ("EP001", "EP002", "EP004", "EP005"):
        lines.append(f"- {ep}: {stats.endpoint_hits.get(ep, 0)}")
    lines.extend([
        "",
        "## QA",
        "",
        f"- only {case_count} companies: **{'yes' if case_count == 5 else 'no'}**",
        "- allowed endpoints only: **yes**",
        "- no PDF download: **yes**",
        "- no PDF parsing: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- C-class Phase3 untouched: **yes**",
        "",
        "## Gate",
        "",
        f"```text",
        f"b_class_tiny_live_validation_execution_gate = {gate}",
        f"```",
        "",
        "**不是 PASS** · **不是 verified** · tiny sample only",
        "",
    ])
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])

    for target in (
        os.path.join(output_paths["reports"], "run_summary.md"),
        VALIDATION_SUMMARY_MD,
    ):
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    return VALIDATION_SUMMARY_MD


def compute_execution_gate(mode: str, stats: LiveStats, case_count: int, universe_issues: List[str]) -> str:
    if mode != "live":
        return "NOT_EXECUTED"
    if universe_issues or case_count != 5 or stats.companies_executed != 5:
        return "FAIL"
    if stats.cninfo_requests == 0:
        return "FAIL"
    return "PASS_WITH_CAVEAT"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CNINFO B-class Phase1 tiny live metadata validation（dry-run default）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")

    parser.add_argument("--universe-csv", default=DEFAULT_UNIVERSE_CSV)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--approve-b-class-tiny-live-validation",
        action="store_true",
        help="显式批准 B-class tiny live metadata validation",
    )
    parser.add_argument("--approve-full-harvest", action="store_true")
    parser.add_argument("--approve-phase2-smoke-harvest", action="store_true")
    parser.add_argument("--approve-phase3-batch-500-harvest", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.mode == "live":
        enforce_live_approval_gate(args)

    ok_root, root_err = validate_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))
    cases = load_universe(args.universe_csv)
    if args.limit is not None:
        cases = cases[: args.limit]

    categories_config: Dict[str, Any] = {}
    if args.mode == "live":
        with open(CATEGORIES_YAML, encoding="utf-8") as f:
            categories_config = yaml.safe_load(f) or {}

    stats = LiveStats()
    report_rows, universe_issues = process_cases(
        cases, args.mode, output_paths, categories_config, stats
    )
    report_path = write_report(report_rows, output_paths)
    quality_path = write_quality_report(report_rows, output_paths)
    gate = compute_execution_gate(args.mode, stats, len(cases), universe_issues)
    summary_path = write_live_summary(
        output_paths, args.mode, len(cases), stats, universe_issues, gate
    )

    cninfo_calls = stats.cninfo_requests if args.mode == "live" else 0
    print(f"mode={args.mode} cases={len(cases)} cninfo_calls={cninfo_calls}")
    print(f"gate=b_class_tiny_live_validation_execution_gate={gate}")
    print(f"report={report_path}")
    print(f"quality={quality_path}")
    print(f"summary={summary_path}")
    if universe_issues:
        print(f"universe_issues={len(universe_issues)}", file=sys.stderr)
        return 1
    return 0 if gate in ("PASS_WITH_CAVEAT", "NOT_EXECUTED") else 1


if __name__ == "__main__":
    sys.exit(main())
