"""
CNINFO B-class corpus retrieval validation — dry-run (default) + live metadata v1.

Loads ready cases from retrieval validation YAML. Default mode is dry-run (no CNINFO).
Pass --live-metadata to request announcement metadata for ready known-document cases only.

Does NOT download PDF, parse PDF, write verified, or upgrade source status.

Usage:
    python lab/validate_cninfo_b_class_corpus_retrieval.py --dry-run
    python lab/validate_cninfo_b_class_corpus_retrieval.py --live-metadata \\
        --output-csv outputs/validation/cninfo_b_class_corpus_retrieval_live_report.csv \\
        --output-md outputs/validation/cninfo_b_class_corpus_retrieval_live_summary.md
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_DIR = os.path.join(BASE_DIR, "lab")
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from validate_cninfo_b_class_category_routing import route_title  # noqa: E402

DEFAULT_KNOWN = os.path.join(
    BASE_DIR, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)
DEFAULT_CATEGORY = os.path.join(
    BASE_DIR, "fixtures", "b_class", "retrieval_validation", "category_sample_cases.yaml"
)
DEFAULT_REGISTRY = os.path.join(BASE_DIR, "config", "cninfo_b_class_source_registry_draft.yaml")
DEFAULT_CATEGORIES = os.path.join(BASE_DIR, "config", "cninfo_announcement_categories.yaml")
DEFAULT_SCHEMA = os.path.join(BASE_DIR, "schemas", "b_class", "b_document.schema.json")
DEFAULT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_corpus_retrieval_dry_run_report.csv"
)
DEFAULT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_corpus_retrieval_dry_run_summary.md"
)
DEFAULT_LIVE_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_corpus_retrieval_live_report.csv"
)
DEFAULT_LIVE_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_corpus_retrieval_live_summary.md"
)

# CNINFO announcement metadata (aligned with Phase 1 validate_cninfo_report_coverage.py)
TOPSEARCH_URL = "https://www.cninfo.com.cn/new/information/topSearch/query"
REQUEST_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
SLEEP_SECONDS = 0.6
PAGE_SIZE = 30
REQUEST_TIMEOUT = 10

AJAX_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
        "ListedCompanyDataCollector/b-class-corpus-retrieval"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.cninfo.com.cn/",
}

_ORGID_SEARCH_CACHE: Dict[str, str] = {}

LIVE_CSV_FIELDS = [
    "case_id", "source_id", "company_code", "company_name", "title_pattern",
    "expected_document_type", "expected_route_to", "date_start", "date_end",
    "query_status", "retrieval_status", "matched_title", "matched_date",
    "matched_pdf_url_available", "predicted_document_type", "predicted_route_to",
    "classification_status", "case_result", "false_positive_reason", "notes",
]

KNOWN_READY_REQUIRED = [
    "case_id", "source_id", "company_code", "company_name", "title_pattern",
    "expected_document_type", "date_start", "date_end", "expected_route_to",
    "expected_pdf_url_available",
]
CATEGORY_READY_REQUIRED = [
    "case_id", "source_id", "source_category", "title_pattern",
    "date_start", "date_end", "expected_min_results", "expected_document_types",
]


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_cases(path: str) -> List[Dict[str, Any]]:
    return list(_load_yaml(path).get("cases") or [])


def _load_registry_source_ids(path: str) -> Set[str]:
    data = _load_yaml(path)
    return {
        str(s.get("source_id"))
        for s in (data.get("sources") or [])
        if s.get("source_id")
    }


def _load_document_types(schema_path: str) -> Set[str]:
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    enum = (schema.get("definitions") or {}).get("document_type", {}).get("enum", [])
    return {str(v) for v in enum}


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    return False


def _missing_required(case: Dict[str, Any], fields: List[str]) -> List[str]:
    missing: List[str] = []
    for field in fields:
        if field not in case or _is_empty(case.get(field)):
            missing.append(field)
    if "expected_pdf_url_available" in fields and case.get("expected_pdf_url_available") is None:
        if "expected_pdf_url_available" not in missing:
            missing.append("expected_pdf_url_available")
    return missing


def _validate_ready_case(
    case: Dict[str, Any],
    case_type: str,
    registry_ids: Set[str],
    document_types: Set[str],
) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    if case_type == "known_document":
        issues.extend(_missing_required(case, KNOWN_READY_REQUIRED))
        route = case.get("expected_route_to")
        if route and route not in registry_ids:
            issues.append(f"expected_route_to not in registry: {route}")
        doc_type = case.get("expected_document_type")
        if doc_type and doc_type not in document_types:
            issues.append(f"invalid expected_document_type: {doc_type}")
    else:
        issues.extend(_missing_required(case, CATEGORY_READY_REQUIRED))
        for dt in case.get("expected_document_types") or []:
            if dt not in document_types:
                issues.append(f"invalid expected_document_type in list: {dt}")

    sid = case.get("source_id")
    if sid and sid not in registry_ids:
        issues.append(f"source_id not in registry: {sid}")

    if _is_empty(case.get("date_start")) or _is_empty(case.get("date_end")):
        if "date_start" not in issues and _is_empty(case.get("date_start")):
            issues.append("date_start empty")
        if "date_end" not in issues and _is_empty(case.get("date_end")):
            issues.append("date_end empty")

    return len(issues) == 0, issues


def _process_case(
    case: Dict[str, Any],
    case_type: str,
    registry_ids: Set[str],
    document_types: Set[str],
    dry_run: bool,
) -> Dict[str, str]:
    case_id = str(case.get("case_id", ""))
    status = str(case.get("case_status", "placeholder"))
    source_id = str(case.get("source_id", ""))
    title_pattern = str(case.get("title_pattern", ""))
    date_start = str(case.get("date_start") or "")
    date_end = str(case.get("date_end") or "")
    expected_doc_type = str(
        case.get("expected_document_type")
        or ",".join(case.get("expected_document_types") or [])
    )
    expected_route = str(case.get("expected_route_to", ""))

    if status in ("placeholder", "example_only"):
        return {
            "case_id": case_id,
            "case_type": case_type,
            "case_status": status,
            "source_id": source_id,
            "title_pattern": title_pattern,
            "date_start": date_start,
            "date_end": date_end,
            "expected_document_type": expected_doc_type,
            "expected_route_to": expected_route,
            "dry_run_status": "skipped_placeholder",
            "would_query": "false",
            "query_status": "not_executed_dry_run",
            "notes": "case not ready; no CNINFO request",
        }

    if status == "retired":
        return {
            "case_id": case_id,
            "case_type": case_type,
            "case_status": status,
            "source_id": source_id,
            "title_pattern": title_pattern,
            "date_start": date_start,
            "date_end": date_end,
            "expected_document_type": expected_doc_type,
            "expected_route_to": expected_route,
            "dry_run_status": "skipped_retired",
            "would_query": "false",
            "query_status": "not_executed_dry_run",
            "notes": "retired case; skipped",
        }

    if status == "ready":
        ok, issues = _validate_ready_case(case, case_type, registry_ids, document_types)
        if not ok:
            return {
                "case_id": case_id,
                "case_type": case_type,
                "case_status": status,
                "source_id": source_id,
                "title_pattern": title_pattern,
                "date_start": date_start,
                "date_end": date_end,
                "expected_document_type": expected_doc_type,
                "expected_route_to": expected_route,
                "dry_run_status": "invalid_ready",
                "would_query": "false",
                "query_status": "not_executed_dry_run",
                "notes": "; ".join(issues),
            }
        would_live = "true"
        if case_type == "category_sample" and not _is_live_guard_case(case):
            # 正向 category-sample 与 guard 均可 live metadata（B-FM-01）
            would_live = "true"
        qs = "not_executed_dry_run" if dry_run else "live_mode_not_implemented"
        dry_status = "ready_for_future_live_validation"
        if case_type == "category_sample" and _is_live_guard_case(case):
            dry_status = "ready_for_guard_live_validation"
        elif case_type == "category_sample":
            dry_status = "ready_for_category_sample_live_validation"
            qs = "not_executed_dry_run"
        return {
            "case_id": case_id,
            "case_type": case_type,
            "case_status": status,
            "source_id": source_id,
            "title_pattern": title_pattern,
            "date_start": date_start,
            "date_end": date_end,
            "expected_document_type": expected_doc_type,
            "expected_route_to": expected_route,
            "dry_run_status": dry_status,
            "would_query": would_live,
            "query_status": qs,
            "notes": "dry-run only; CNINFO not called",
        }

    return {
        "case_id": case_id,
        "case_type": case_type,
        "case_status": status,
        "source_id": source_id,
        "title_pattern": title_pattern,
        "date_start": date_start,
        "date_end": date_end,
        "expected_document_type": expected_doc_type,
        "expected_route_to": expected_route,
        "dry_run_status": "invalid_ready",
        "would_query": "false",
        "query_status": "not_executed_dry_run",
        "notes": f"unknown case_status: {status}",
    }


def run_dry_run(
    known_path: str,
    category_path: str,
    registry_path: str,
    schema_path: str,
    dry_run: bool,
) -> Tuple[List[Dict[str, str]], Dict[str, int]]:
    registry_ids = _load_registry_source_ids(registry_path)
    document_types = _load_document_types(schema_path)
    rows: List[Dict[str, str]] = []

    for case in _load_cases(known_path):
        rows.append(_process_case(case, "known_document", registry_ids, document_types, dry_run))
    for case in _load_cases(category_path):
        rows.append(_process_case(case, "category_sample", registry_ids, document_types, dry_run))

    stats = {
        "total_cases": len(rows),
        "ready_cases": sum(1 for r in rows if r["case_status"] == "ready"),
        "invalid_ready": sum(1 for r in rows if r["dry_run_status"] == "invalid_ready"),
        "placeholder_cases": sum(1 for r in rows if r["dry_run_status"] == "skipped_placeholder"),
        "retired_cases": sum(1 for r in rows if r["dry_run_status"] == "skipped_retired"),
        "ready_for_live": sum(
            1 for r in rows
            if r["dry_run_status"] in (
                "ready_for_future_live_validation",
                "ready_for_guard_live_validation",
                "ready_for_category_sample_live_validation",
            )
        ),
        "query_executed": 0,
    }
    return rows, stats


def _compute_result(stats: Dict[str, int]) -> str:
    if stats["invalid_ready"] > 0:
        return "FAIL"
    if stats["ready_cases"] == 0:
        return "NO_READY_CASES"
    if stats["ready_for_live"] > 0:
        return "DRY_RUN_PASS"
    return "PASS"


def _compute_live_result(stats: Dict[str, int]) -> str:
    if stats.get("invalid_ready", 0) > 0:
        return "FAIL"
    if stats.get("ready_cases", 0) == 0:
        return "NO_READY_CASES"
    if stats.get("request_error", 0) > 0 and stats.get("pass", 0) == 0:
        return "FAIL"
    if stats.get("fail", 0) > 0 or stats.get("ambiguous", 0) > 0:
        return "PARTIAL"
    # 每 case 可多次 CNINFO（topSearch + query，或 sse+szse）；以 case pass 对齐 ready
    if (
        stats.get("pass", 0) > 0
        and stats.get("pass", 0) == stats.get("ready_cases", 0)
        and stats.get("query_executed", 0) > 0
    ):
        return "LIVE_PASS"
    return "PARTIAL"


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


def build_query_payload(
    code: str,
    orgid: str,
    column: str,
    keyword: str,
    se_date: str,
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


def resolve_orgid_via_topsearch(stock_code: str) -> str:
    if not stock_code:
        return ""
    if stock_code in _ORGID_SEARCH_CACHE:
        return _ORGID_SEARCH_CACHE[stock_code]
    try:
        resp = requests.post(
            TOPSEARCH_URL,
            data={"keyWord": stock_code, "maxNum": 10},
            headers=AJAX_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        if not resp.ok:
            return ""
        items = resp.json()
        if not isinstance(items, list):
            return ""
        for item in items:
            if str(item.get("code")) == str(stock_code):
                org = (item.get("orgId") or "").strip()
                if org:
                    _ORGID_SEARCH_CACHE[stock_code] = org
                    return org
        if items:
            org = (items[0].get("orgId") or "").strip()
            if org:
                _ORGID_SEARCH_CACHE[stock_code] = org
                return org
    except Exception:
        return ""
    return ""


def fetch_announcements(payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], str, str]:
    """Return (records, query_status, error_message)."""
    try:
        resp = requests.post(
            REQUEST_URL, data=payload, headers=AJAX_HEADERS, timeout=REQUEST_TIMEOUT
        )
        if resp.status_code == 429:
            return [], "request_error", "rate_limited"
        if resp.status_code in (401, 403):
            return [], "request_error", "captcha_or_login_required"
        if resp.status_code != 200:
            return [], "request_error", f"http_{resp.status_code}"
        data = resp.json()
        if not isinstance(data, dict):
            return [], "parse_error", "invalid_json_response"
        return list(data.get("announcements") or []), "executed", ""
    except requests.exceptions.Timeout:
        return [], "request_error", "network_timeout"
    except json.JSONDecodeError:
        return [], "parse_error", "json_decode_error"
    except Exception as exc:
        return [], "request_error", f"{type(exc).__name__}: {exc}"


def _announcement_date(ts: Any) -> Optional[date]:
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).date()
    except (TypeError, ValueError, OSError):
        return None


def _format_announcement_date(ts: Any) -> str:
    d = _announcement_date(ts)
    return d.isoformat() if d else ""


def _strip_html_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def _title_matches(title: str, pattern: str) -> bool:
    clean_title = _strip_html_tags((title or "").strip())
    clean_pattern = (pattern or "").strip()
    if not clean_title or not clean_pattern:
        return False
    if clean_pattern in clean_title:
        return True
    return clean_pattern.replace(" ", "") in clean_title.replace(" ", "")


def _sec_code_matches(rec: Dict[str, Any], company_code: str) -> bool:
    code = (company_code or "").strip()
    if not code:
        return False
    sec = str(rec.get("secCode") or rec.get("seccode") or "").strip()
    if sec:
        parts = [p.strip() for p in sec.replace(";", ",").split(",") if p.strip()]
        return code in parts or sec == code
    stock = str(rec.get("stockCode") or rec.get("code") or "").strip()
    return stock == code if stock else True


def _date_in_range(ts: Any, date_start: str, date_end: str) -> bool:
    ann_date = _announcement_date(ts)
    if not ann_date:
        return False
    try:
        start = date.fromisoformat(date_start)
        end = date.fromisoformat(date_end)
    except ValueError:
        return False
    return start <= ann_date <= end


def _shorter_searchkey(title_pattern: str) -> str:
    s = (title_pattern or "").strip()
    if s.startswith("关于"):
        s = s[2:]
    if s.endswith("的公告"):
        s = s[:-3]
    return s.strip()


def _classify_match(
    title: str,
    categories_config: Dict[str, Any],
    expected_document_type: str,
    expected_route_to: str,
) -> Tuple[str, str, str, str]:
    route = route_title(title.strip(), categories_config)
    predicted_doc = route.predicted_document_type
    predicted_route = route.predicted_route_to
    false_positive = route.false_positive_reason or ""

    if predicted_doc == expected_document_type and predicted_route == expected_route_to:
        status = "classified_correctly"
    elif predicted_route != expected_route_to or predicted_doc != expected_document_type:
        status = "misclassified"
    else:
        status = "unknown"
    return predicted_doc, predicted_route, status, false_positive


def _find_matching_records(
    records: List[Dict[str, Any]],
    case: Dict[str, Any],
    categories_config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    company_code = str(case.get("company_code", ""))
    title_pattern = str(case.get("title_pattern", ""))
    date_start = str(case.get("date_start", ""))
    date_end = str(case.get("date_end", ""))
    expected_document_type = str(case.get("expected_document_type", ""))
    expected_route_to = str(case.get("expected_route_to", ""))

    seen: Set[str] = set()
    matches: List[Dict[str, Any]] = []
    for rec in records:
        rec_key = str(rec.get("announcementId") or rec.get("announcementTitle") or "")
        if rec_key in seen:
            continue
        seen.add(rec_key)

        title = _strip_html_tags(str(rec.get("announcementTitle") or ""))
        if not _title_matches(title, title_pattern):
            continue
        if not _sec_code_matches(rec, company_code):
            continue
        if not _date_in_range(rec.get("announcementTime"), date_start, date_end):
            continue
        pdf_url = build_pdf_url(rec.get("adjunctUrl"))
        if not pdf_url:
            continue

        predicted_doc, predicted_route, class_status, fp_reason = _classify_match(
            title, categories_config, expected_document_type, expected_route_to
        )
        matches.append({
            "title": title,
            "date": _format_announcement_date(rec.get("announcementTime")),
            "pdf_url": pdf_url,
            "pdf_available": True,
            "predicted_document_type": predicted_doc,
            "predicted_route_to": predicted_route,
            "classification_status": class_status,
            "false_positive_reason": fp_reason,
        })
    return matches


def _live_row_from_case(case: Dict[str, Any], **kwargs: Any) -> Dict[str, str]:
    base = {
        "case_id": str(case.get("case_id", "")),
        "source_id": str(case.get("source_id", "")),
        "company_code": str(case.get("company_code", "")),
        "company_name": str(case.get("company_name", "")),
        "title_pattern": str(case.get("title_pattern", "")),
        "expected_document_type": str(case.get("expected_document_type", "")),
        "expected_route_to": str(case.get("expected_route_to", "")),
        "date_start": str(case.get("date_start", "")),
        "date_end": str(case.get("date_end", "")),
        "query_status": "",
        "retrieval_status": "",
        "matched_title": "",
        "matched_date": "",
        "matched_pdf_url_available": "",
        "predicted_document_type": "",
        "predicted_route_to": "",
        "classification_status": "",
        "case_result": "",
        "false_positive_reason": "",
        "notes": str(case.get("notes", "")),
    }
    base.update({k: str(v) for k, v in kwargs.items()})
    return base


def process_live_known_case(
    case: Dict[str, Any],
    registry_ids: Set[str],
    document_types: Set[str],
    categories_config: Dict[str, Any],
) -> Tuple[Dict[str, str], int]:
    """Process one ready known-document case. Returns (row, query_count)."""
    ok, issues = _validate_ready_case(case, "known_document", registry_ids, document_types)
    if not ok:
        return _live_row_from_case(
            case,
            query_status="skipped_invalid_ready",
            retrieval_status="request_failed",
            case_result="skipped",
            classification_status="unknown",
            notes="; ".join(issues),
        ), 0

    company_code = str(case.get("company_code", ""))
    date_start = str(case.get("date_start", ""))
    date_end = str(case.get("date_end", ""))
    title_pattern = str(case.get("title_pattern", ""))
    se_date = f"{date_start} ~ {date_end}"

    orgid = resolve_orgid_via_topsearch(company_code)
    time.sleep(SLEEP_SECONDS)
    if not orgid:
        return _live_row_from_case(
            case,
            query_status="request_error",
            retrieval_status="request_failed",
            case_result="fail",
            classification_status="unknown",
            notes="orgId resolution failed via topSearch",
        ), 0

    column = infer_column(company_code)
    search_attempts = [title_pattern]
    shorter = _shorter_searchkey(title_pattern)
    if shorter and shorter != title_pattern:
        search_attempts.append(shorter)

    all_records: List[Dict[str, Any]] = []
    query_count = 0
    last_query_status = "executed"
    last_error = ""

    for keyword in search_attempts[:2]:
        payload = build_query_payload(company_code, orgid, column, keyword, se_date)
        records, query_status, err = fetch_announcements(payload)
        query_count += 1
        last_query_status = query_status
        last_error = err
        time.sleep(SLEEP_SECONDS)
        if query_status != "executed":
            break
        all_records.extend(records)
        if records:
            break

    if last_query_status != "executed":
        return _live_row_from_case(
            case,
            query_status=last_query_status,
            retrieval_status="request_failed",
            case_result="fail",
            classification_status="unknown",
            notes=last_error or "CNINFO request failed",
        ), query_count

    matches = _find_matching_records(all_records, case, categories_config)
    if not matches:
        return _live_row_from_case(
            case,
            query_status="executed",
            retrieval_status="not_found",
            case_result="fail",
            classification_status="not_found",
            matched_pdf_url_available="false",
            notes=f"no match in {len(all_records)} announcements returned",
        ), query_count

    if len(matches) > 1:
        best = matches[0]
        return _live_row_from_case(
            case,
            query_status="executed",
            retrieval_status="ambiguous",
            matched_title=best["title"],
            matched_date=best["date"],
            matched_pdf_url_available="true",
            predicted_document_type=best["predicted_document_type"],
            predicted_route_to=best["predicted_route_to"],
            classification_status="ambiguous",
            case_result="ambiguous",
            false_positive_reason=best.get("false_positive_reason", ""),
            notes=f"multiple matches ({len(matches)}); first shown",
        ), query_count

    match = matches[0]
    if match["classification_status"] == "classified_correctly":
        case_result = "pass"
        retrieval_status = "found"
    else:
        case_result = "fail"
        retrieval_status = "found"

    return _live_row_from_case(
        case,
        query_status="executed",
        retrieval_status=retrieval_status,
        matched_title=match["title"],
        matched_date=match["date"],
        matched_pdf_url_available="true",
        predicted_document_type=match["predicted_document_type"],
        predicted_route_to=match["predicted_route_to"],
        classification_status=match["classification_status"],
        case_result=case_result,
        false_positive_reason=match.get("false_positive_reason", ""),
        notes="live metadata match; PDF not downloaded",
    ), query_count


PERIODIC_REPORT_ROUTE = "cninfo_periodic_report_pdf"
PERIODIC_DOC_TYPES = {
    "annual_report",
    "semi_annual_report",
    "quarterly_report_q1",
    "quarterly_report_q3",
}


def _is_live_guard_case(case: Dict[str, Any]) -> bool:
    """Only periodic_guard_* category-sample cases are eligible for live guard audit."""
    return str(case.get("case_id", "")).startswith("periodic_guard_")


def _is_live_positive_category_sample(case: Dict[str, Any]) -> bool:
    """正向 category-sample（非 periodic_guard_*）可做全市场 metadata 抽样 live。"""
    if str(case.get("case_status")) != "ready":
        return False
    cid = str(case.get("case_id", ""))
    return bool(cid) and not _is_live_guard_case(case)


def _dedupe_announcements(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Set[str] = set()
    out: List[Dict[str, Any]] = []
    for rec in records:
        key = str(rec.get("announcementId") or rec.get("announcementTitle") or "")
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)
    return out


def process_live_guard_case(
    case: Dict[str, Any],
    registry_ids: Set[str],
    document_types: Set[str],
    categories_config: Dict[str, Any],
) -> Tuple[Dict[str, str], int]:
    """Live metadata false-positive guard audit for ready periodic_guard_* cases."""
    ok, issues = _validate_ready_case(case, "category_sample", registry_ids, document_types)
    base_kwargs = {
        "source_id": str(case.get("source_id", "")),
        "company_code": "",
        "company_name": "",
        "title_pattern": str(case.get("title_pattern", "")),
        "expected_document_type": ",".join(case.get("expected_document_types") or []),
        "expected_route_to": str(case.get("source_id", "")),
        "date_start": str(case.get("date_start", "")),
        "date_end": str(case.get("date_end", "")),
    }
    if not ok:
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status="skipped_invalid_ready",
            retrieval_status="request_failed",
            case_result="skipped",
            classification_status="unknown",
            notes="; ".join(issues),
        ), 0

    title_pattern = str(case.get("title_pattern", ""))
    date_start = str(case.get("date_start", ""))
    date_end = str(case.get("date_end", ""))
    se_date = f"{date_start} ~ {date_end}"
    expected_min = int(case.get("expected_min_results") or 0)

    all_records: List[Dict[str, Any]] = []
    query_count = 0
    last_query_status = "executed"
    last_error = ""

    for column in ("sse", "szse"):
        payload = build_query_payload("", "", column, title_pattern, se_date)
        records, query_status, err = fetch_announcements(payload)
        query_count += 1
        last_query_status = query_status
        last_error = err
        time.sleep(SLEEP_SECONDS)
        if query_status != "executed":
            break
        all_records.extend(records)
        if records:
            break

    if last_query_status != "executed":
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status=last_query_status,
            retrieval_status="request_failed",
            case_result="fail",
            classification_status="unknown",
            notes=last_error or "CNINFO request failed",
        ), query_count

    title_hits: List[Dict[str, Any]] = []
    false_positive_hits: List[Dict[str, Any]] = []

    for rec in _dedupe_announcements(all_records):
        title = _strip_html_tags(str(rec.get("announcementTitle") or ""))
        if not _title_matches(title, title_pattern):
            continue
        pdf_url = build_pdf_url(rec.get("adjunctUrl"))
        predicted_doc, predicted_route, class_status, fp_reason = _classify_match(
            title,
            categories_config,
            "announcement",
            str(case.get("source_id", "")),
        )
        entry = {
            "title": title,
            "date": _format_announcement_date(rec.get("announcementTime")),
            "pdf_available": bool(pdf_url),
            "predicted_document_type": predicted_doc,
            "predicted_route_to": predicted_route,
            "classification_status": class_status,
            "false_positive_reason": fp_reason,
            "sec_code": str(rec.get("secCode") or ""),
        }
        if (
            predicted_route == PERIODIC_REPORT_ROUTE
            or predicted_doc in PERIODIC_DOC_TYPES
        ):
            false_positive_hits.append(entry)
        else:
            title_hits.append(entry)

    if false_positive_hits:
        bad = false_positive_hits[0]
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status="executed",
            retrieval_status="found",
            matched_title=bad["title"],
            matched_date=bad["date"],
            matched_pdf_url_available=str(bad["pdf_available"]).lower(),
            predicted_document_type=bad["predicted_document_type"],
            predicted_route_to=bad["predicted_route_to"],
            classification_status="misclassified",
            case_result="fail",
            false_positive_reason="summary_as_periodic_report",
            notes=(
                f"guard fail: {len(false_positive_hits)} title(s) misrouted to periodic_report; "
                f"PDF not downloaded"
            ),
        ), query_count

    if title_hits:
        good = title_hits[0]
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status="executed",
            retrieval_status="found",
            matched_title=good["title"],
            matched_date=good["date"],
            matched_pdf_url_available=str(good["pdf_available"]).lower(),
            predicted_document_type=good["predicted_document_type"],
            predicted_route_to=good["predicted_route_to"],
            classification_status="classified_correctly",
            case_result="pass",
            false_positive_reason="",
            notes=(
                f"guard pass: {len(title_hits)} summary title(s) not routed to periodic_report; "
                f"PDF not downloaded"
            ),
        ), query_count

    if expected_min == 0:
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status="executed",
            retrieval_status="not_found",
            case_result="pass",
            classification_status="not_found",
            matched_pdf_url_available="false",
            notes=(
                f"guard pass (no matches in window): expected_min_results=0; "
                f"no false-positive to audit; {len(all_records)} announcements scanned"
            ),
        ), query_count

    return _live_row_from_case(
        case,
        **base_kwargs,
        query_status="executed",
        retrieval_status="not_found",
        case_result="fail",
        classification_status="not_found",
        matched_pdf_url_available="false",
        notes=f"no title matches; expected_min_results={expected_min}",
    ), query_count


def process_live_category_sample(
    case: Dict[str, Any],
    registry_ids: Set[str],
    document_types: Set[str],
    categories_config: Dict[str, Any],
) -> Tuple[Dict[str, str], int]:
    """Live metadata 正向 category-sample：全市场标题抽样 + 类型/路由审计（不下载 PDF）。"""
    ok, issues = _validate_ready_case(case, "category_sample", registry_ids, document_types)
    expected_types = [str(t) for t in (case.get("expected_document_types") or [])]
    base_kwargs = {
        "source_id": str(case.get("source_id", "")),
        "company_code": "",
        "company_name": "",
        "title_pattern": str(case.get("title_pattern", "")),
        "expected_document_type": ",".join(expected_types),
        "expected_route_to": str(case.get("source_id", "")),
        "date_start": str(case.get("date_start", "")),
        "date_end": str(case.get("date_end", "")),
    }
    if not ok:
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status="skipped_invalid_ready",
            retrieval_status="request_failed",
            case_result="skipped",
            classification_status="unknown",
            notes="; ".join(issues),
        ), 0

    title_pattern = str(case.get("title_pattern", ""))
    date_start = str(case.get("date_start", ""))
    date_end = str(case.get("date_end", ""))
    se_date = f"{date_start} ~ {date_end}"
    expected_min = int(case.get("expected_min_results") or 0)

    all_records: List[Dict[str, Any]] = []
    query_count = 0
    last_query_status = "executed"
    last_error = ""

    for column in ("sse", "szse"):
        payload = build_query_payload("", "", column, title_pattern, se_date)
        records, query_status, err = fetch_announcements(payload)
        query_count += 1
        last_query_status = query_status
        last_error = err
        time.sleep(SLEEP_SECONDS)
        if query_status != "executed":
            break
        all_records.extend(records)

    if last_query_status != "executed":
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status=last_query_status,
            retrieval_status="request_failed",
            case_result="fail",
            classification_status="unknown",
            notes=last_error or "CNINFO request failed",
        ), query_count

    title_hits: List[Dict[str, Any]] = []
    false_positive_hits: List[Dict[str, Any]] = []
    type_mismatch_hits: List[Dict[str, Any]] = []

    for rec in _dedupe_announcements(all_records):
        title = _strip_html_tags(str(rec.get("announcementTitle") or ""))
        if not _title_matches(title, title_pattern):
            continue
        pdf_url = build_pdf_url(rec.get("adjunctUrl"))
        predicted_doc, predicted_route, class_status, fp_reason = _classify_match(
            title,
            categories_config,
            expected_types[0] if expected_types else "announcement",
            str(case.get("source_id", "")),
        )
        entry = {
            "title": title,
            "date": _format_announcement_date(rec.get("announcementTime")),
            "pdf_available": bool(pdf_url),
            "predicted_document_type": predicted_doc,
            "predicted_route_to": predicted_route,
            "classification_status": class_status,
            "false_positive_reason": fp_reason,
            "sec_code": str(rec.get("secCode") or ""),
        }
        if (
            predicted_route == PERIODIC_REPORT_ROUTE
            or predicted_doc in PERIODIC_DOC_TYPES
        ):
            false_positive_hits.append(entry)
            continue
        if expected_types and predicted_doc not in expected_types:
            type_mismatch_hits.append(entry)
            continue
        title_hits.append(entry)

    if false_positive_hits:
        bad = false_positive_hits[0]
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status="executed",
            retrieval_status="found",
            matched_title=bad["title"],
            matched_date=bad["date"],
            matched_pdf_url_available=str(bad["pdf_available"]).lower(),
            predicted_document_type=bad["predicted_document_type"],
            predicted_route_to=bad["predicted_route_to"],
            classification_status="misclassified",
            case_result="fail",
            false_positive_reason="category_sample_as_periodic_report",
            notes=(
                f"category-sample fail: {len(false_positive_hits)} title(s) misrouted "
                f"to periodic_report; PDF not downloaded"
            ),
        ), query_count

    if type_mismatch_hits and not title_hits:
        bad = type_mismatch_hits[0]
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status="executed",
            retrieval_status="found",
            matched_title=bad["title"],
            matched_date=bad["date"],
            matched_pdf_url_available=str(bad["pdf_available"]).lower(),
            predicted_document_type=bad["predicted_document_type"],
            predicted_route_to=bad["predicted_route_to"],
            classification_status="misclassified",
            case_result="fail",
            false_positive_reason="",
            notes=(
                f"category-sample fail: title matched but document_type not in "
                f"expected={expected_types}; PDF not downloaded"
            ),
        ), query_count

    if len(title_hits) >= expected_min:
        good = title_hits[0]
        return _live_row_from_case(
            case,
            **base_kwargs,
            query_status="executed",
            retrieval_status="found",
            matched_title=good["title"],
            matched_date=good["date"],
            matched_pdf_url_available=str(good["pdf_available"]).lower(),
            predicted_document_type=good["predicted_document_type"],
            predicted_route_to=good["predicted_route_to"],
            classification_status="classified_correctly",
            case_result="pass",
            false_positive_reason="",
            notes=(
                f"category-sample pass: {len(title_hits)} hit(s) "
                f"(min={expected_min}); scanned={len(all_records)}; PDF not downloaded"
            ),
        ), query_count

    return _live_row_from_case(
        case,
        **base_kwargs,
        query_status="executed",
        retrieval_status="not_found",
        case_result="fail",
        classification_status="not_found",
        matched_pdf_url_available="false",
        notes=(
            f"category-sample fail: hits={len(title_hits)} < expected_min={expected_min}; "
            f"type_mismatch={len(type_mismatch_hits)}; scanned={len(all_records)}"
        ),
    ), query_count


def run_live_metadata(
    known_path: str,
    category_path: str,
    registry_path: str,
    schema_path: str,
    categories_path: str,
) -> Tuple[List[Dict[str, str]], Dict[str, int]]:
    registry_ids = _load_registry_source_ids(registry_path)
    document_types = _load_document_types(schema_path)
    categories_config = _load_yaml(categories_path)

    invalid_ready = 0
    for case in _load_cases(known_path):
        if str(case.get("case_status")) == "ready":
            ok, _ = _validate_ready_case(case, "known_document", registry_ids, document_types)
            if not ok:
                invalid_ready += 1
    for case in _load_cases(category_path):
        if str(case.get("case_status")) == "ready":
            ok, _ = _validate_ready_case(case, "category_sample", registry_ids, document_types)
            if not ok:
                invalid_ready += 1

    if invalid_ready > 0:
        return [], {
            "total_cases": 0,
            "ready_cases": 0,
            "invalid_ready": invalid_ready,
            "query_executed": 0,
            "pass": 0,
            "fail": 0,
            "ambiguous": 0,
            "not_found": 0,
            "request_error": 0,
        }

    ready_known = [
        c for c in _load_cases(known_path)
        if str(c.get("case_status")) == "ready"
    ]
    ready_guards = [
        c for c in _load_cases(category_path)
        if str(c.get("case_status")) == "ready" and _is_live_guard_case(c)
    ]
    ready_category_samples = [
        c for c in _load_cases(category_path)
        if _is_live_positive_category_sample(c)
    ]

    rows: List[Dict[str, str]] = []
    query_executed = 0
    for case in ready_known:
        row, qcount = process_live_known_case(
            case, registry_ids, document_types, categories_config
        )
        rows.append(row)
        query_executed += qcount
    for case in ready_guards:
        row, qcount = process_live_guard_case(
            case, registry_ids, document_types, categories_config
        )
        rows.append(row)
        query_executed += qcount
    for case in ready_category_samples:
        row, qcount = process_live_category_sample(
            case, registry_ids, document_types, categories_config
        )
        rows.append(row)
        query_executed += qcount

    ready_total = len(ready_known) + len(ready_guards) + len(ready_category_samples)
    stats = {
        "total_cases": len(rows),
        "ready_cases": ready_total,
        "ready_known": len(ready_known),
        "ready_guards": len(ready_guards),
        "ready_category_samples": len(ready_category_samples),
        "invalid_ready": 0,
        "query_executed": query_executed,
        "pass": sum(1 for r in rows if r["case_result"] == "pass"),
        "fail": sum(1 for r in rows if r["case_result"] == "fail"),
        "ambiguous": sum(1 for r in rows if r["case_result"] == "ambiguous"),
        "not_found": sum(1 for r in rows if r["retrieval_status"] == "not_found"),
        "request_error": sum(
            1 for r in rows
            if r["query_status"] in ("request_error", "parse_error")
        ),
    }
    return rows, stats


def write_live_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in LIVE_CSV_FIELDS})


def write_live_summary_md(
    path: str,
    rows: List[Dict[str, str]],
    stats: Dict[str, int],
    result: str,
    known_path: str,
    registry_path: str,
    categories_path: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ready_ids = [r["case_id"] for r in rows]

    lines = [
        "# CNINFO B 类 Corpus Retrieval Live Metadata Validation Summary",
        "",
        f"_生成时间：{now}（live metadata v1；仅公告 metadata；不下载 PDF）_",
        "",
        "## 1. 目的",
        "",
        "本次只做 **live metadata validation**：对 ready known-document case 调用",
        "`hisAnnouncement/query` 检索公告标题、日期、pdf_url 可用性与路由分类。",
        "**不下载 PDF，不解析 PDF，不入库。**",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| Ready known-document cases | `{os.path.relpath(known_path, BASE_DIR)}` |",
        f"| B 类 registry | `{os.path.relpath(registry_path, BASE_DIR)}` |",
        f"| Category routing | `{os.path.relpath(categories_path, BASE_DIR)}` |",
        f"| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |",
        f"| mode | **--live-metadata** |",
        "",
        f"Ready case IDs: {', '.join(f'`{c}`' for c in ready_ids) or '_none_'}",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_cases | **{stats.get('total_cases', 0)}** |",
        f"| ready_cases | **{stats.get('ready_cases', 0)}** |",
        f"| query_executed | **{stats.get('query_executed', 0)}** |",
        f"| pass | **{stats.get('pass', 0)}** |",
        f"| fail | **{stats.get('fail', 0)}** |",
        f"| ambiguous | **{stats.get('ambiguous', 0)}** |",
        f"| not_found | **{stats.get('not_found', 0)}** |",
        f"| request_error | **{stats.get('request_error', 0)}** |",
        f"| result | **{result}** |",
        "",
        "## 4. 分 case 结果",
        "",
        "| case_id | expected title pattern | matched title | matched date | pdf_url | route | case_result |",
        "|---------|------------------------|---------------|--------------|---------|-------|-------------|",
    ]

    for r in rows:
        title_short = (r.get("matched_title") or "")[:40]
        if len(r.get("matched_title") or "") > 40:
            title_short += "…"
        route_info = f"{r.get('predicted_route_to', '')} / {r.get('classification_status', '')}"
        pdf_flag = r.get("matched_pdf_url_available", "")
        lines.append(
            f"| `{r['case_id']}` | {r.get('title_pattern', '')[:30]} | {title_short} | "
            f"{r.get('matched_date', '')} | {pdf_flag} | {route_info} | **{r.get('case_result', '')}** |"
        )

    lines.extend([
        "",
        "## 5. 质量边界",
        "",
        "- 本次 **只验证 metadata retrieval**（标题 / 日期 / pdf_url 字段存在性）。",
        "- **PDF 未下载**；**PDF 未解析**；未生成 chunk / embedding。",
        "- **不代表** corpus parsing 成功；**不代表** RAG 可用。",
        "- **不写 verified**；**不升级** source status。",
        "- placeholder category-sample case **未请求** CNINFO。",
        "- guard case（`periodic_guard_*`）仅做 route/type false-positive 审计。",
        "- 正向 category-sample（`*_sample_*` ready）做全市场 metadata 抽样 + 类型审计。",
        "",
        "## 6. 下一步",
        "",
        "1. 若 category-sample live pass，可继续补 inquiry/meeting 类 placeholder。",
        "2. 若 fail，先分析 query params / title matching / date window。",
        "3. **暂不下载 PDF**；parse pipeline 仍保持 dry-run。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_b_class_corpus_retrieval_live_report.csv](cninfo_b_class_corpus_retrieval_live_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def write_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "case_id", "case_type", "case_status", "source_id", "title_pattern",
        "date_start", "date_end", "expected_document_type", "expected_route_to",
        "dry_run_status", "would_query", "query_status", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(
    path: str,
    rows: List[Dict[str, str]],
    stats: Dict[str, int],
    result: str,
    known_path: str,
    category_path: str,
    registry_path: str,
    categories_path: str,
    dry_run: bool,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ready_rows = [
        r for r in rows
        if r["dry_run_status"] in (
            "ready_for_future_live_validation",
            "ready_for_guard_live_validation",
            "ready_for_category_sample_live_validation",
        )
    ]

    lines = [
        "# CNINFO B 类 Corpus Retrieval Dry-run Summary",
        "",
        f"_生成时间：{now}（corpus retrieval 脚本骨架 dry-run；不请求 CNINFO）_",
        "",
        "## 1. 目的",
        "",
        "验证 `lab/validate_cninfo_b_class_corpus_retrieval.py` 骨架：",
        "加载 **ready** case、校验字段、输出 dry-run 报告。**不发起 CNINFO 请求。**",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| Known-document cases | `{os.path.relpath(known_path, BASE_DIR)}` |",
        f"| Category-sample cases | `{os.path.relpath(category_path, BASE_DIR)}` |",
        f"| B 类 registry | `{os.path.relpath(registry_path, BASE_DIR)}` |",
        f"| Category routing | `{os.path.relpath(categories_path, BASE_DIR)}` |",
        f"| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |",
        f"| dry_run | **{dry_run}** |",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_cases | **{stats['total_cases']}** |",
        f"| ready_cases | **{stats['ready_cases']}** |",
        f"| invalid_ready | **{stats['invalid_ready']}** |",
        f"| placeholder_cases | **{stats['placeholder_cases']}** |",
        f"| retired_cases | **{stats['retired_cases']}** |",
        f"| query_executed | **{stats['query_executed']}** |",
        f"| result | **{result}** |",
        "",
        "## 4. Ready case 明细",
        "",
    ]
    if ready_rows:
        for r in ready_rows:
            lines.append(f"- `{r['case_id']}` would_query={r['would_query']}")
    else:
        lines.append("_当前 **没有** 可运行 live validation 的 ready case（ready_cases=0）。_")

    lines.extend([
        "",
        "## 5. Dry-run 行为",
        "",
        "- `would_query=true` 仅表示 **未来** 将对该 case 发起 `hisAnnouncement/query`。",
        "- 本阶段所有行 `query_status=not_executed_dry_run`。",
        "- Live metadata：使用 `--live-metadata`（见 live summary 输出）。",
        "",
        "## 6. 质量边界",
        "",
        "- **不代表** CNINFO retrieval coverage%。",
        "- **不代表** PDF URL 已补齐或 PDF 已下载/解析。",
        "- **不写 verified**；**不升级** candidate source。",
        "",
        "## 7. 下一步",
        "",
        "1. 人工补 3–5 条真实 ready case（见 intake template + review checklist）。",
        "2. 运行 `select_cninfo_b_class_retrieval_ready_cases.py` 确认 `invalid_ready=0`。",
        "3. 再运行本 dry-run 脚本确认 ready case 被正确选中。",
        "4. 最后才实现 live metadata request（单独评审）。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_b_class_corpus_retrieval_dry_run_report.csv](cninfo_b_class_corpus_retrieval_dry_run_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="B-class corpus retrieval validation (dry-run default; --live-metadata for CNINFO)"
    )
    parser.add_argument("--known-cases", default=DEFAULT_KNOWN)
    parser.add_argument("--category-cases", default=DEFAULT_CATEGORY)
    parser.add_argument("--registry", default=DEFAULT_REGISTRY)
    parser.add_argument("--categories", default=DEFAULT_CATEGORIES)
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    parser.add_argument("--output-csv", default=None)
    parser.add_argument("--output-md", default=None)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live-metadata", dest="mode", action="store_const", const="live_metadata")
    parser.set_defaults(mode="dry_run")
    parser.add_argument("--no-dry-run", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.no_dry_run and args.mode != "live_metadata":
        print("ERROR  use --live-metadata for CNINFO requests; default is --dry-run")
        sys.exit(3)

    if args.mode == "live_metadata":
        out_csv = args.output_csv or DEFAULT_LIVE_CSV
        out_md = args.output_md or DEFAULT_LIVE_MD
        rows, stats = run_live_metadata(
            args.known_cases,
            args.category_cases,
            args.registry,
            args.schema,
            args.categories,
        )
        result = _compute_live_result(stats)
        if stats.get("invalid_ready", 0) > 0:
            print(f"ERROR  invalid_ready={stats['invalid_ready']}; live metadata blocked")
            sys.exit(1)
        if stats.get("ready_cases", 0) == 0:
            print("SUMMARY  ready_cases=0  result=NO_READY_CASES")
            sys.exit(2)
        write_live_csv(out_csv, rows)
        write_live_summary_md(
            out_md, rows, stats, result,
            args.known_cases, args.registry, args.categories,
        )
        print(
            f"SUMMARY  ready={stats['ready_cases']}  query_executed={stats['query_executed']}  "
            f"pass={stats['pass']}  fail={stats['fail']}  ambiguous={stats['ambiguous']}  "
            f"result={result}"
        )
        print(f"CSV   {out_csv}")
        print(f"MD    {out_md}")
        if result == "FAIL":
            sys.exit(1)
        sys.exit(0)

    out_csv = args.output_csv or DEFAULT_CSV
    out_md = args.output_md or DEFAULT_MD
    rows, stats = run_dry_run(
        args.known_cases,
        args.category_cases,
        args.registry,
        args.schema,
        dry_run=True,
    )
    result = _compute_result(stats)

    write_csv(out_csv, rows)
    write_summary_md(
        out_md,
        rows,
        stats,
        result,
        args.known_cases,
        args.category_cases,
        args.registry,
        args.categories,
        True,
    )

    print(
        f"SUMMARY  total={stats['total_cases']}  ready={stats['ready_cases']}  "
        f"invalid_ready={stats['invalid_ready']}  query_executed={stats['query_executed']}  "
        f"result={result}"
    )
    print(f"CSV   {out_csv}")
    print(f"MD    {out_md}")

    if stats["invalid_ready"] > 0:
        sys.exit(1)
    if args.strict and stats["ready_cases"] == 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
