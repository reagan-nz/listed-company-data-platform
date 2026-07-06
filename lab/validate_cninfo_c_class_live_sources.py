"""
CNINFO C-class live source validation v1 (Era C Phase 4).

Validates P1 YAML backfill endpoints for basic_profile and security_profile
on 3 known companies only.

Default: --dry-run (no network). Use --live to request CNINFO.

Does NOT write verified, ingest to DB, download PDF, or expand to full market.

Usage:
    python lab/validate_cninfo_c_class_live_sources.py --dry-run
    python lab/validate_cninfo_c_class_live_sources.py --live
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_live_source_validation_report.csv"
)
DEFAULT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_live_source_validation_summary.md"
)

BASIC_URL = (
    "https://www.cninfo.com.cn/data20/companyOverview/getCompanyIntroduction"
)
SECURITY_URL = (
    "https://www.cninfo.com.cn/new/newInterface/marketOverview"
)

SLEEP_SECONDS = 0.8
REQUEST_TIMEOUT = 10
MAX_RETRIES = 1

SOURCES = (
    "cninfo_company_basic_profile",
    "cninfo_company_security_profile",
)

KNOWN_COMPANIES: List[Dict[str, str]] = [
    {
        "company_code": "600000",
        "company_name": "浦发银行",
        "org_id": "gssh0600000",
        # Earlier DevTools probe saw empty arrays; live validation v1 returns non-empty.
        "expected_basic_result": "endpoint_found",
        "expected_security_result": "endpoint_found",
        "notes": (
            "Earlier manual DevTools probe observed empty basicInformation/"
            "listingInformation for 600000, but live validation currently returns "
            "non-empty records. Treat endpoint_found as current expected behavior; "
            "keep empty observation as historical caveat."
        ),
    },
    {
        "company_code": "300001",
        "company_name": "特锐德",
        "org_id": "9900008270",
        "expected_basic_result": "endpoint_found",
        "expected_security_result": "endpoint_found",
    },
    {
        "company_code": "688001",
        "company_name": "华兴源创",
        "org_id": "9900038969",
        "expected_basic_result": "endpoint_found",
        "expected_security_result": "endpoint_found",
    },
]

SECURITY_REQUIRED_FIELDS = (
    "secCode",
    "secName",
    "secType",
    "tradingStatus",
    "age",
    "finance",
    "delisted",
)
SECURITY_OPTIONAL_FIELDS = ("sshk", "szhk")

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
    "basic_information_count",
    "listing_information_count",
    "observed_fields",
    "missing_fields",
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
    expected_status: str = ""
    case_result: str = "skipped"
    records_path: str = ""
    basic_information_count: str = ""
    listing_information_count: str = ""
    observed_fields: str = ""
    missing_fields: str = ""
    error_message: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {k: getattr(self, k) for k in CSV_FIELDS}


def _referer(company_code: str, org_id: str) -> str:
    return (
        f"https://www.cninfo.com.cn/new/disclosure/stock"
        f"?stockCode={company_code}&orgId={org_id}"
    )


def _basic_request_url(company_code: str) -> str:
    return f"{BASIC_URL}?scode={company_code}"


def _security_request_url(company_code: str, org_id: str) -> str:
    return (
        f"{SECURITY_URL}?secCode={company_code}&orgId={org_id}&secType=szshe"
    )


def _browser_headers(company_code: str, org_id: str, xhr: bool = False) -> Dict[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
            "ListedCompanyDataCollector/c-class-live-v1"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": _referer(company_code, org_id),
    }
    if xhr:
        headers["X-Requested-With"] = "XMLHttpRequest"
    return headers


def _http_get(url: str, headers: Dict[str, str]) -> Tuple[Optional[int], Any, str]:
    last_err = ""
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            status = resp.status_code
            text = resp.text or ""
            if "tenantLogin" in text or "login" in resp.url.lower():
                return status, None, "blocked_or_login_redirect"
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
    if json_code == "200":
        return True
    if result_code == "200":
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


def _list_len(val: Any) -> int:
    return len(val) if isinstance(val, list) else 0


def validate_basic_live(company: Dict[str, str]) -> CaseRow:
    code = company["company_code"]
    org_id = company["org_id"]
    url = _basic_request_url(code)
    row = CaseRow(
        run_mode="live",
        source_id="cninfo_company_basic_profile",
        company_code=code,
        company_name=company["company_name"],
        org_id=org_id,
        request_url=url,
        expected_status=company["expected_basic_result"],
        records_path="data.records[0]",
    )
    http_status, payload, err = _http_get(url, _browser_headers(code, org_id, xhr=False))
    row.http_status = str(http_status) if http_status is not None else ""
    if err:
        row.error_message = err
        row.retrieval_status = "http_error" if http_status is None else "blocked"
        row.case_result = "fail"
        return row

    json_code, result_code = _extract_codes(payload)
    row.json_code = json_code
    row.result_code = result_code

    if not _is_success_payload(payload, http_status or 0):
        row.retrieval_status = "http_error"
        row.error_message = "HTTP or JSON code not success"
        row.case_result = "fail"
        return row

    record0 = _get_path(payload, "data.records.0")
    if record0 is None:
        row.retrieval_status = "empty_response"
        row.error_message = "data.records[0] missing"
        row.case_result = "fail"
        return row

    basic = record0.get("basicInformation") if isinstance(record0, dict) else None
    listing = record0.get("listingInformation") if isinstance(record0, dict) else None
    row.basic_information_count = str(_list_len(basic))
    row.listing_information_count = str(_list_len(listing))

    if _list_len(basic) > 0 and _list_len(listing) > 0:
        row.retrieval_status = "endpoint_found"
        fields = ["basicInformation", "listingInformation"]
        if isinstance(basic, list) and basic and isinstance(basic[0], dict):
            fields.extend(f"basicInformation.{k}" for k in sorted(basic[0].keys()))
        row.observed_fields = ";".join(fields[:30])
    elif isinstance(record0, dict):
        row.retrieval_status = "empty_but_valid_response"
        row.observed_fields = "basicInformation;listingInformation"
    else:
        row.retrieval_status = "schema_unexpected"
        row.error_message = "records[0] not object"

    row.case_result = (
        "pass" if row.retrieval_status == row.expected_status else "fail"
    )
    return row


def validate_security_live(company: Dict[str, str]) -> CaseRow:
    code = company["company_code"]
    org_id = company["org_id"]
    url = _security_request_url(code, org_id)
    row = CaseRow(
        run_mode="live",
        source_id="cninfo_company_security_profile",
        company_code=code,
        company_name=company["company_name"],
        org_id=org_id,
        request_url=url,
        expected_status=company["expected_security_result"],
        records_path="$",
    )
    http_status, payload, err = _http_get(url, _browser_headers(code, org_id, xhr=True))
    row.http_status = str(http_status) if http_status is not None else ""
    if err:
        row.error_message = err
        row.retrieval_status = "http_error" if http_status is None else "blocked"
        row.case_result = "fail"
        return row

    json_code, result_code = _extract_codes(payload)
    row.json_code = json_code
    row.result_code = result_code

    if http_status != 200:
        row.retrieval_status = "http_error"
        row.case_result = "fail"
        return row

    if not isinstance(payload, dict):
        row.retrieval_status = "schema_unexpected"
        row.error_message = "response not object"
        row.case_result = "fail"
        return row

    missing = [f for f in SECURITY_REQUIRED_FIELDS if f not in payload]
    observed = [f for f in SECURITY_REQUIRED_FIELDS if f in payload]
    for opt in SECURITY_OPTIONAL_FIELDS:
        if opt in payload:
            observed.append(opt)
    row.observed_fields = ";".join(observed)
    row.missing_fields = ";".join(missing)

    if missing:
        row.retrieval_status = "schema_unexpected"
        row.case_result = "fail"
        return row

    row.retrieval_status = "endpoint_found"
    row.case_result = (
        "pass" if row.retrieval_status == row.expected_status else "fail"
    )
    return row


def build_dry_run_rows() -> List[CaseRow]:
    rows: List[CaseRow] = []
    for company in KNOWN_COMPANIES:
        rows.append(CaseRow(
            run_mode="dry-run",
            source_id="cninfo_company_basic_profile",
            company_code=company["company_code"],
            company_name=company["company_name"],
            org_id=company["org_id"],
            request_url=_basic_request_url(company["company_code"]),
            expected_status=company["expected_basic_result"],
            records_path="data.records[0]",
            case_result="skipped",
        ))
        rows.append(CaseRow(
            run_mode="dry-run",
            source_id="cninfo_company_security_profile",
            company_code=company["company_code"],
            company_name=company["company_name"],
            org_id=company["org_id"],
            request_url=_security_request_url(
                company["company_code"], company["org_id"]
            ),
            expected_status=company["expected_security_result"],
            records_path="$",
            case_result="skipped",
        ))
    return rows


def run_live() -> List[CaseRow]:
    rows: List[CaseRow] = []
    request_count = 0
    max_requests = len(KNOWN_COMPANIES) * len(SOURCES)

    for company in KNOWN_COMPANIES:
        rows.append(validate_basic_live(company))
        request_count += 1
        if request_count < max_requests:
            time.sleep(SLEEP_SECONDS)

        rows.append(validate_security_live(company))
        request_count += 1
        if request_count < max_requests:
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
            "http_error": status_ctr.get("http_error", 0) + status_ctr.get("blocked", 0),
        })
    return out


def write_summary_md(path: str, rows: List[CaseRow], run_mode: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    agg = _aggregate_by_source(rows)
    total_pass = sum(1 for r in rows if r.case_result == "pass")
    total_fail = sum(1 for r in rows if r.case_result == "fail")
    total_skip = sum(1 for r in rows if r.case_result == "skipped")
    blocked = [r for r in rows if r.retrieval_status in ("blocked", "http_error")]
    schema_changed = [r for r in rows if r.retrieval_status == "schema_unexpected"]

    lines = [
        "# CNINFO C Class Live Source Validation Summary",
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
        "- `cninfo_company_basic_profile`",
        "- `cninfo_company_security_profile`",
        "",
        "**Companies tested:**",
        "- 600000 浦发银行",
        "- 300001 特锐德",
        "- 688001 华兴源创",
        "",
        f"**Total planned requests (live):** {len(KNOWN_COMPANIES) * len(SOURCES)}",
        "",
        "## Result summary",
        "",
        "| source_id | total | pass | fail | skipped | endpoint_found | "
        "empty_but_valid_response | schema_unexpected | http_error |",
        "|-----------|-------|------|------|---------|----------------|"
        "--------------------------|-------------------|------------|",
    ]
    for a in agg:
        lines.append(
            f"| `{a['source_id']}` | {a['total']} | {a['pass']} | {a['fail']} | "
            f"{a['skipped']} | {a['endpoint_found']} | {a['empty_but_valid_response']} | "
            f"{a['schema_unexpected']} | {a['http_error']} |"
        )

    lines.extend([
        "",
        f"**Overall:** pass={total_pass} fail={total_fail} skipped={total_skip}",
        "",
        "## Key findings",
        "",
    ])

    if run_mode == "dry-run":
        lines.append("- **DRY_RUN_ONLY** — no CNINFO requests executed.")
    else:
        basic_rows = [r for r in rows if r.source_id == "cninfo_company_basic_profile"]
        sec_rows = [r for r in rows if r.source_id == "cninfo_company_security_profile"]
        basic_found = sum(1 for r in basic_rows if r.retrieval_status == "endpoint_found")
        basic_empty = sum(
            1 for r in basic_rows if r.retrieval_status == "empty_but_valid_response"
        )
        lines.append(
            f"- **basic_profile:** {basic_found}/3 endpoint_found "
            f"(expected 3/3); case pass="
            f"{sum(1 for r in basic_rows if r.case_result == 'pass')}/3"
        )
        if basic_empty:
            lines.append(
                f"- **basic_profile historical:** {basic_empty}/3 "
                f"empty_but_valid_response observed in this run"
            )
        lines.append(
            "- **600000:** manual DevTools empty vs live non-empty reconciled; "
            "expected_status=endpoint_found with historical caveat."
        )
        lines.append(
            f"- **security_profile:** "
            f"{sum(1 for r in sec_rows if r.retrieval_status == 'endpoint_found')}/3 "
            f"endpoint_found; case pass="
            f"{sum(1 for r in sec_rows if r.case_result == 'pass')}/3"
        )
        if blocked:
            lines.append(f"- **blocked/login/http errors:** {len(blocked)} case(s)")
        else:
            lines.append("- **blocked/login/captcha:** none observed")
        if schema_changed:
            lines.append(f"- **schema_unexpected:** {len(schema_changed)} case(s)")
        else:
            lines.append("- **schema_changed:** none observed")

    lines.extend([
        "",
        "## Caveats",
        "",
        "- Small sample only (3 known companies).",
        "- Sources remain **testing**; **no verified**.",
        "- No database ingestion.",
        "- No full-market coverage.",
        "- getHeadStripData annex not validated in v1.",
        "",
        "## Next steps",
        "",
        "1. Implement mapper draft for basic_profile.",
        "2. Reconcile any future empty_but_valid_response vs endpoint_found drift.",
        "3. Validate secType on more board samples later.",
        "4. Decide whether to include getHeadStripData annex in next script.",
        "",
        "## Appendix",
        "",
        "详见 [cninfo_c_class_live_source_validation_report.csv]"
        "(cninfo_c_class_live_source_validation_report.csv)。",
        "",
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="C-class live source validation v1 (dry-run default)"
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
        else ("LIVE_PASS" if total_fail == 0 else "LIVE_FAIL")
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
