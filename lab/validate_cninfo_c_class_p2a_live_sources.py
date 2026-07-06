"""
CNINFO C-class P2-A live source validation v1 (Era C Phase 4).

Validates YAML backfill endpoints for executive / share_capital / shareholders
on 3 known companies only (12 requests max in live mode).

Default: --dry-run (no network). Use --live to request CNINFO.

Does NOT write verified, ingest to DB, download PDF, or expand to full market.

Usage:
    python lab/validate_cninfo_c_class_p2a_live_sources.py --dry-run
    python lab/validate_cninfo_c_class_p2a_live_sources.py --live
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_p2a_live_source_validation_report.csv"
)
DEFAULT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_p2a_live_source_validation_summary.md"
)

SLEEP_SECONDS = 0.8
REQUEST_TIMEOUT = 10
MAX_RETRIES = 1
MAX_LIVE_REQUESTS = 12

KNOWN_COMPANIES: List[Dict[str, str]] = [
    {"company_code": "600000", "company_name": "浦发银行", "org_id": "gssh0600000"},
    {"company_code": "300001", "company_name": "特锐德", "org_id": "9900008270"},
    {"company_code": "688001", "company_name": "华兴源创", "org_id": "9900038969"},
]

SOURCE_SPECS: Dict[str, Dict[str, Any]] = {
    "cninfo_executive_profile": {
        "url": "https://www.cninfo.com.cn/data20/companyOverview/getCompanyExecutives",
        "records_path": "data.records",
        "expected_fields": [
            "F002V", "F009V", "F010V", "F012V", "F005N", "F012N", "SEQID", "F001V",
        ],
        "optional_fields": ["F017V"],
    },
    "cninfo_share_capital_profile": {
        "url": "https://www.cninfo.com.cn/data20/stockholderCapital/getStockStructure",
        "records_path": "data.records",
        "expected_fields": ["VARYDATE", "F002V", "F021N", "F022N", "F003N"],
        "optional_fields": ["F023N", "F024N", "F028N"],
    },
    "cninfo_top_shareholders_profile": {
        "url": "https://www.cninfo.com.cn/data20/stockholderCapital/getTopTenStockholders",
        "records_path": "data.records",
        "expected_fields": ["F001D", "F002V", "F003N", "F004N", "F005N", "F006V"],
        "optional_fields": ["F007V"],
    },
    "cninfo_top_float_shareholders_profile": {
        "url": "https://www.cninfo.com.cn/data20/stockholderCapital/getTopTenCirculatingStockholders",
        "records_path": "data.records",
        "expected_fields": ["F001D", "F002V", "F003N", "F004N", "F005N", "F006V"],
        "optional_fields": ["F007V"],
    },
}

SOURCES = tuple(SOURCE_SPECS.keys())
EXPECTED_STATUS = "endpoint_found"

CSV_FIELDS = [
    "run_mode",
    "source_id",
    "company_code",
    "company_name",
    "org_id",
    "request_url",
    "http_status",
    "json_code",
    "result_code",
    "retrieval_status",
    "expected_status",
    "case_result",
    "records_path",
    "record_count",
    "observed_fields",
    "missing_fields",
    "optional_missing_or_null_fields",
    "error_message",
]


@dataclass
class CaseRow:
    run_mode: str
    source_id: str
    company_code: str
    company_name: str
    org_id: str
    request_url: str = ""
    http_status: str = ""
    json_code: str = ""
    result_code: str = ""
    retrieval_status: str = ""
    expected_status: str = EXPECTED_STATUS
    case_result: str = "skipped"
    records_path: str = "data.records"
    record_count: str = ""
    observed_fields: str = ""
    missing_fields: str = ""
    optional_missing_or_null_fields: str = ""
    error_message: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {k: getattr(self, k) for k in CSV_FIELDS}


def _referer(company_code: str, org_id: str) -> str:
    return (
        f"https://www.cninfo.com.cn/new/disclosure/stock"
        f"?stockCode={company_code}&orgId={org_id}"
    )


def _request_url(base_url: str, company_code: str) -> str:
    return f"{base_url}?scode={company_code}"


def _browser_headers(company_code: str, org_id: str) -> Dict[str, str]:
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
            "ListedCompanyDataCollector/c-class-p2a-live-v1"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": _referer(company_code, org_id),
    }


def _http_get(url: str, headers: Dict[str, str]) -> Tuple[Optional[int], Any, str]:
    last_err = ""
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            status = resp.status_code
            text = resp.text or ""
            if "tenantLogin" in text or "login" in resp.url.lower():
                return status, None, "blocked_or_login_redirect"
            if "captcha" in text.lower():
                return status, None, "captcha_detected"
            try:
                return status, resp.json(), ""
            except json.JSONDecodeError:
                return status, None, "response_not_json"
        except requests.RequestException as exc:
            last_err = str(exc)
            if attempt < MAX_RETRIES:
                time.sleep(SLEEP_SECONDS)
    return None, None, last_err or "request_failed"


def _extract_codes(payload: Any) -> Tuple[str, str]:
    if not isinstance(payload, dict):
        return "", ""
    json_code = payload.get("code")
    json_code_s = str(json_code) if json_code is not None else ""
    result_code = ""
    data = payload.get("data")
    if isinstance(data, dict) and data.get("resultCode") is not None:
        result_code = str(data.get("resultCode"))
    return json_code_s, result_code


def _is_success_payload(payload: Any, http_status: int) -> bool:
    if http_status != 200 or not isinstance(payload, dict):
        return False
    json_code, result_code = _extract_codes(payload)
    if json_code in ("200", "0"):
        return True
    if result_code in ("200", "0"):
        return True
    return False


def _get_path(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        if not part:
            continue
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, list) and part.isdigit():
            idx = int(part)
            cur = cur[idx] if 0 <= idx < len(cur) else None
        else:
            return None
    return cur


def _field_present(record: Dict[str, Any], field: str) -> bool:
    """Field key present on record; null/empty values allowed (shape validation)."""
    return field in record


def validate_records_case(
    source_id: str,
    company: Dict[str, str],
) -> CaseRow:
    spec = SOURCE_SPECS[source_id]
    code = company["company_code"]
    org_id = company["org_id"]
    url = _request_url(spec["url"], code)
    row = CaseRow(
        run_mode="live",
        source_id=source_id,
        company_code=code,
        company_name=company["company_name"],
        org_id=org_id,
        request_url=url,
        expected_status=EXPECTED_STATUS,
        records_path=spec["records_path"],
    )

    http_status, payload, err = _http_get(url, _browser_headers(code, org_id))
    row.http_status = str(http_status) if http_status is not None else ""

    if err:
        row.error_message = err
        if err in ("blocked_or_login_redirect", "captcha_detected"):
            row.retrieval_status = "blocked"
        elif http_status is None:
            row.retrieval_status = "http_error"
        else:
            row.retrieval_status = "blocked" if "login" in err else "http_error"
        row.case_result = "fail"
        return row

    json_code, result_code = _extract_codes(payload)
    row.json_code = json_code
    row.result_code = result_code

    if http_status != 200:
        row.retrieval_status = "http_error"
        row.error_message = f"HTTP {http_status}"
        row.case_result = "fail"
        return row

    if not isinstance(payload, dict):
        row.retrieval_status = "schema_unexpected"
        row.error_message = "response not object"
        row.case_result = "fail"
        return row

    records = _get_path(payload, spec["records_path"])
    if records is None:
        row.retrieval_status = "schema_unexpected"
        row.error_message = f"{spec['records_path']} missing"
        row.case_result = "fail"
        return row

    if not isinstance(records, list):
        row.retrieval_status = "schema_unexpected"
        row.error_message = f"{spec['records_path']} not list"
        row.case_result = "fail"
        return row

    row.record_count = str(len(records))

    if not _is_success_payload(payload, http_status):
        row.retrieval_status = "http_error"
        row.error_message = "JSON code or resultCode not success"
        row.case_result = "fail"
        return row

    if len(records) == 0:
        row.retrieval_status = "empty_but_valid_response"
        row.case_result = "fail" if EXPECTED_STATUS != "empty_but_valid_response" else "pass"
        return row

    first = records[0]
    if not isinstance(first, dict):
        row.retrieval_status = "schema_unexpected"
        row.error_message = "records[0] not object"
        row.case_result = "fail"
        return row

    required = spec["expected_fields"]
    optional = spec.get("optional_fields") or []
    missing = [f for f in required if not _field_present(first, f)]
    optional_missing = [
        f for f in optional
        if f not in first or first.get(f) is None or first.get(f) == ""
    ]
    observed = [f for f in required + optional if f in first]

    row.observed_fields = ";".join(observed)
    row.missing_fields = ";".join(missing)
    row.optional_missing_or_null_fields = ";".join(optional_missing)

    if missing:
        row.retrieval_status = "schema_unexpected"
        row.error_message = f"missing required fields: {', '.join(missing)}"
        row.case_result = "fail"
        return row

    row.retrieval_status = "endpoint_found"
    row.case_result = "pass" if row.retrieval_status == row.expected_status else "fail"
    return row


def build_dry_run_rows() -> List[CaseRow]:
    rows: List[CaseRow] = []
    for source_id in SOURCES:
        spec = SOURCE_SPECS[source_id]
        for company in KNOWN_COMPANIES:
            rows.append(CaseRow(
                run_mode="dry-run",
                source_id=source_id,
                company_code=company["company_code"],
                company_name=company["company_name"],
                org_id=company["org_id"],
                request_url=_request_url(spec["url"], company["company_code"]),
                expected_status=EXPECTED_STATUS,
                records_path=spec["records_path"],
                case_result="skipped",
            ))
    return rows


def run_live() -> List[CaseRow]:
    rows: List[CaseRow] = []
    request_count = 0

    for source_id in SOURCES:
        for company in KNOWN_COMPANIES:
            rows.append(validate_records_case(source_id, company))
            request_count += 1
            if request_count < MAX_LIVE_REQUESTS:
                time.sleep(SLEEP_SECONDS)

    return rows


def write_csv(path: str, rows: List[CaseRow]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict())


def _aggregate_by_source(rows: List[CaseRow]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for sid in SOURCES:
        subset = [r for r in rows if r.source_id == sid]
        status_ctr = Counter(r.retrieval_status for r in subset if r.retrieval_status)
        out.append({
            "source_id": sid,
            "total": len(subset),
            "pass": sum(1 for r in subset if r.case_result == "pass"),
            "fail": sum(1 for r in subset if r.case_result == "fail"),
            "skipped": sum(1 for r in subset if r.case_result == "skipped"),
            "endpoint_found": status_ctr.get("endpoint_found", 0),
            "empty_but_valid_response": status_ctr.get("empty_but_valid_response", 0),
            "schema_unexpected": status_ctr.get("schema_unexpected", 0),
            "blocked": status_ctr.get("blocked", 0),
            "http_error": status_ctr.get("http_error", 0),
        })
    return out


def write_summary_md(path: str, rows: List[CaseRow], run_mode: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    agg = _aggregate_by_source(rows)
    total_pass = sum(1 for r in rows if r.case_result == "pass")
    total_fail = sum(1 for r in rows if r.case_result == "fail")
    total_skip = sum(1 for r in rows if r.case_result == "skipped")
    blocked = [r for r in rows if r.retrieval_status == "blocked"]
    schema_unexp = [r for r in rows if r.retrieval_status == "schema_unexpected"]
    http_err = [r for r in rows if r.retrieval_status == "http_error"]

    lines = [
        "# CNINFO C Class P2-A Live Source Validation Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## Run mode",
        "",
        f"**{run_mode}**",
        "",
        "## Scope",
        "",
        "**Sources tested:**",
    ]
    for sid in SOURCES:
        lines.append(f"- `{sid}`")
    lines.extend([
        "",
        "**Companies tested:**",
        "- 600000 浦发银行",
        "- 300001 特锐德",
        "- 688001 华兴源创",
        "",
        f"**Total planned requests (live):** {MAX_LIVE_REQUESTS}",
        "",
        "## Result summary",
        "",
        "| source_id | total | pass | fail | skipped | endpoint_found | "
        "empty_but_valid_response | schema_unexpected | blocked | http_error |",
        "|-----------|-------|------|------|---------|----------------|"
        "--------------------------|-------------------|---------|------------|",
    ])
    for a in agg:
        lines.append(
            f"| `{a['source_id']}` | {a['total']} | {a['pass']} | {a['fail']} | "
            f"{a['skipped']} | {a['endpoint_found']} | {a['empty_but_valid_response']} | "
            f"{a['schema_unexpected']} | {a['blocked']} | {a['http_error']} |"
        )

    overall = (
        "DRY_RUN_ONLY" if run_mode == "dry-run"
        else ("LIVE_PASS" if total_fail == 0 else "LIVE_PARTIAL")
    )
    lines.extend([
        "",
        f"**Overall:** pass={total_pass} fail={total_fail} skipped={total_skip} "
        f"**result={overall}**",
        "",
        "## Key findings",
        "",
    ])

    if run_mode == "dry-run":
        lines.append("- **DRY_RUN_ONLY** — no CNINFO requests executed; 12 cases skipped.")
    else:
        for sid in SOURCES:
            subset = [r for r in rows if r.source_id == sid]
            found = sum(1 for r in subset if r.retrieval_status == "endpoint_found")
            passed = sum(1 for r in subset if r.case_result == "pass")
            lines.append(
                f"- **{sid}:** {found}/3 endpoint_found; case pass={passed}/3"
            )
        if blocked:
            lines.append(f"- **blocked/login/captcha:** {len(blocked)} case(s)")
        else:
            lines.append("- **blocked/login/captcha:** none observed")
        if schema_unexp:
            lines.append(f"- **schema_unexpected:** {len(schema_unexp)} case(s)")
        else:
            lines.append("- **schema_unexpected:** none observed")
        if http_err:
            lines.append(f"- **http_error:** {len(http_err)} case(s)")
        empty_cases = [
            r for r in rows if r.retrieval_status == "empty_but_valid_response"
        ]
        if empty_cases:
            lines.append(
                f"- **empty_but_valid_response:** {len(empty_cases)} case(s) "
                f"({', '.join(r.source_id + '/' + r.company_code for r in empty_cases)})"
            )
        bad_rc = [
            r for r in rows
            if r.result_code and r.result_code not in ("200", "0", "")
        ]
        if bad_rc:
            lines.append(
                f"- **intermittent resultCode:** {len(bad_rc)} case(s) with non-200 resultCode"
            )

    lines.extend([
        "",
        "## Caveats",
        "",
        "- 3 known-company sample only.",
        "- **testing** status only; **no verified**.",
        "- **No testing_stable_sample**.",
        "- No database ingestion.",
        "- Numeric field units remain candidate-level.",
        "- Full raw response bodies not saved.",
        "",
        "## Next steps",
        "",
    ])
    if run_mode == "live" and total_fail == 0:
        lines.append("- **LIVE_PASS:** implement P2-A mapper drafts (executive / share_capital / shareholders).")
    elif run_mode == "live":
        lines.append("- **LIVE_PARTIAL/FAIL:** reconcile expectation / endpoint caveat before mapper.")
    else:
        lines.append("- Run with `--live` to validate endpoint shape on CNINFO.")
    lines.extend([
        "",
        "## Appendix",
        "",
        "详见 [cninfo_c_class_p2a_live_source_validation_report.csv]"
        "(cninfo_c_class_p2a_live_source_validation_report.csv)。",
        "",
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="C-class P2-A live source validation v1 (dry-run default)"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "live":
        rows = run_live()
        run_label = "live"
    else:
        rows = build_dry_run_rows()
        run_label = "dry-run"

    write_csv(args.output_csv, rows)
    write_summary_md(args.output_md, rows, run_label)

    total_pass = sum(1 for r in rows if r.case_result == "pass")
    total_fail = sum(1 for r in rows if r.case_result == "fail")
    total_skip = sum(1 for r in rows if r.case_result == "skipped")
    result = (
        "DRY_RUN_ONLY" if run_label == "dry-run"
        else ("LIVE_PASS" if total_fail == 0 else "LIVE_PARTIAL")
    )

    print(
        f"SUMMARY  mode={run_label}  cases={len(rows)}  "
        f"pass={total_pass}  fail={total_fail}  skipped={total_skip}  result={result}"
    )
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")

    if run_label == "live" and total_fail > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
