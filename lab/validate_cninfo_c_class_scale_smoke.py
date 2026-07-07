"""
CNINFO C-class 30-company scale smoke test (Era C Phase 4).

配置驱动：从样本 YAML 读取公司列表，对 basic / dividend / P2-A 四源做主判定；
security 单列观察；contact / business_scope / industry 仅随 basic basicInformation fill_rate 统计。

默认 --dry-run（无网络）。使用 --live 发起真实 CNINFO 请求（带 sleep 限流）。

Usage:
    python lab/validate_cninfo_c_class_scale_smoke.py --dry-run
    python lab/validate_cninfo_c_class_scale_smoke.py --live
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_SAMPLE = os.path.join(BASE_DIR, "lab", "eval_companies_c_class_smoke_30.yaml")
DEFAULT_ACTIVE_SAMPLE = os.path.join(
    BASE_DIR, "lab", "eval_companies_c_class_smoke_30_active.yaml"
)
DEFAULT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_scale_smoke_30_report.csv"
)
DEFAULT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_scale_smoke_30_summary.md"
)
DEFAULT_ACTIVE_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_scale_smoke_30_active_report.csv"
)
DEFAULT_ACTIVE_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_scale_smoke_30_active_summary.md"
)
DEFAULT_ACTIVE_200_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_scale_smoke_200_active_report.csv"
)
DEFAULT_ACTIVE_200_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_scale_smoke_200_active_summary.md"
)
DEFAULT_1000_NON_BSE_DRYRUN_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_smoke_1000_non_bse_dryrun_report.csv",
)
DEFAULT_1000_NON_BSE_DRYRUN_MD = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_smoke_1000_non_bse_dryrun_summary.md",
)
DEFAULT_1000_NON_BSE_LIVE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_smoke_1000_non_bse_live_report.csv",
)
DEFAULT_1000_NON_BSE_LIVE_MD = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_smoke_1000_non_bse_live_summary.md",
)
DEFAULT_RETRY_889_PARTIAL_DRYRUN_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_retry_889_partial_fail_dryrun_report.csv",
)
DEFAULT_RETRY_889_PARTIAL_DRYRUN_MD = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_retry_889_partial_fail_dryrun_summary.md",
)
DEFAULT_RETRY_889_PARTIAL_LIVE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_retry_889_partial_fail_live_report.csv",
)
DEFAULT_RETRY_889_PARTIAL_LIVE_MD = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_retry_889_partial_fail_live_summary.md",
)
DEFAULT_STABLE_200_DRYRUN_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_stable_200_dryrun_report.csv",
)
DEFAULT_STABLE_200_DRYRUN_MD = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_stable_200_dryrun_summary.md",
)
DEFAULT_STABLE_200_LIVE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_stable_200_live_report.csv",
)
DEFAULT_STABLE_200_LIVE_MD = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_stable_200_live_summary.md",
)
# 兼容旧常量名（dry-run 默认）
DEFAULT_1000_NON_BSE_CSV = DEFAULT_1000_NON_BSE_DRYRUN_CSV
DEFAULT_1000_NON_BSE_MD = DEFAULT_1000_NON_BSE_DRYRUN_MD
PREVIOUS_BASELINE_CSV = DEFAULT_CSV

BASIC_URL = "https://www.cninfo.com.cn/data20/companyOverview/getCompanyIntroduction"
DIVIDEND_URL = "https://www.cninfo.com.cn/data20/companyOverview/getCompanyHisDividend"
SECURITY_URL = "https://www.cninfo.com.cn/new/newInterface/marketOverview"

SLEEP_SECONDS = 0.8
REQUEST_TIMEOUT = 10
MAX_RETRIES = 1
LIVE_PROGRESS_INTERVAL = 50

# 主判定 source（按请求顺序）
MAIN_SOURCE_IDS = (
    "cninfo_company_basic_profile",
    "cninfo_dividend_financing_profile",
    "cninfo_executive_profile",
    "cninfo_share_capital_profile",
    "cninfo_top_shareholders_profile",
    "cninfo_top_float_shareholders_profile",
)

OBSERVE_SOURCE_ID = "cninfo_company_security_profile"

# targeted retry partial-fail 样本 live 前置校验预期
RETRY_889_PARTIAL_SAMPLE_NAME = "eval_companies_c_class_retry_889_partial_fail_retry.yaml"
RETRY_889_PARTIAL_EXPECTED_COMPANY_COUNT = 62
RETRY_889_PARTIAL_EXPECTED_FAILURE_TYPE_COUNTS: Dict[str, int] = {
    "multi_partial_fail": 35,
    "single_source_fail": 17,
    "only_shareholder_empty_but_valid": 10,
}
SOURCE_COUNT_PER_COMPANY = len(MAIN_SOURCE_IDS) + 1  # 6 主判定 + security observe

# 股东源：空 records 视为 empty_but_valid，主 gate 不计 fail
SHAREHOLDER_SOURCE_IDS = (
    "cninfo_top_shareholders_profile",
    "cninfo_top_float_shareholders_profile",
)

# derived 三源：不单独发请求，仅统计 basicInformation 字段 fill_rate
DERIVED_SOURCE_FIELDS: Dict[str, List[str]] = {
    "cninfo_company_contact_profile": [
        "F004V", "F005V", "F006V", "F011V", "F012V", "F013V", "F014V", "F018V",
    ],
    "cninfo_company_business_scope": ["F015V", "F016V", "F017V"],
    "cninfo_company_industry_profile": ["F032V", "MARKET", "F044V"],
}

# basic 关键字段（地址/行业类 fill_rate 门槛参考）
BASIC_KEY_FIELDS = [
    "F001V", "F004V", "F005V", "F032V", "MARKET", "F015V", "F016V",
]

SOURCE_SPECS: Dict[str, Dict[str, Any]] = {
    "cninfo_company_basic_profile": {
        "url": BASIC_URL,
        "kind": "basic",
        "records_path": "data.records.0",
        "judgment": True,
    },
    "cninfo_dividend_financing_profile": {
        "url": DIVIDEND_URL,
        "kind": "records_list",
        "records_path": "data.records",
        "expected_fields": ["F001V", "F007V", "F018D", "F020D", "F023D"],
        "allow_valid_empty": True,
        "judgment": True,
    },
    "cninfo_executive_profile": {
        "url": "https://www.cninfo.com.cn/data20/companyOverview/getCompanyExecutives",
        "kind": "records_list",
        "records_path": "data.records",
        "expected_fields": [
            "F002V", "F009V", "F010V", "F012V", "F005N", "F012N", "SEQID", "F001V",
        ],
        "optional_fields": ["F017V"],
        "judgment": True,
    },
    "cninfo_share_capital_profile": {
        "url": "https://www.cninfo.com.cn/data20/stockholderCapital/getStockStructure",
        "kind": "records_list",
        "records_path": "data.records",
        "expected_fields": ["VARYDATE", "F002V", "F021N", "F022N", "F003N"],
        "optional_fields": ["F023N", "F024N", "F028N"],
        "judgment": True,
    },
    "cninfo_top_shareholders_profile": {
        "url": "https://www.cninfo.com.cn/data20/stockholderCapital/getTopTenStockholders",
        "kind": "records_list",
        "records_path": "data.records",
        "expected_fields": ["F001D", "F002V", "F003N", "F004N", "F005N", "F006V"],
        "optional_fields": ["F007V"],
        "judgment": True,
    },
    "cninfo_top_float_shareholders_profile": {
        "url": "https://www.cninfo.com.cn/data20/stockholderCapital/getTopTenCirculatingStockholders",
        "kind": "records_list",
        "records_path": "data.records",
        "expected_fields": ["F001D", "F002V", "F003N", "F004N", "F005N", "F006V"],
        "optional_fields": ["F007V"],
        "judgment": True,
    },
    "cninfo_company_security_profile": {
        "url": SECURITY_URL,
        "kind": "security",
        "judgment": False,
        "observe_only": True,
    },
}

REACHABILITY_THRESHOLD = 0.95
BASIC_NON_EMPTY_THRESHOLD = 0.90
ERROR_RATE_THRESHOLD = 0.05
BASIC_KEY_FILL_THRESHOLD = 0.85
DIVIDEND_DATE_FILL_THRESHOLD = 0.80

CSV_FIELDS = [
    "run_mode",
    "source_id",
    "company_code",
    "company_name",
    "org_id",
    "board",
    "request_url",
    "http_status",
    "json_code",
    "result_code",
    "retrieval_status",
    "case_result",
    "records_path",
    "record_count",
    "non_empty",
    "field_fill_rates",
    "observed_fields",
    "missing_fields",
    "error_message",
    "suspected_no_dividend",
]


@dataclass
class CaseRow:
    run_mode: str
    source_id: str
    company_code: str
    company_name: str
    org_id: str
    board: str = ""
    request_url: str = ""
    http_status: str = ""
    json_code: str = ""
    result_code: str = ""
    retrieval_status: str = ""
    case_result: str = "skipped"
    records_path: str = ""
    record_count: str = ""
    non_empty: str = ""
    field_fill_rates: str = ""
    observed_fields: str = ""
    missing_fields: str = ""
    error_message: str = ""
    suspected_no_dividend: str = ""
    # 内存统计用，不写 CSV
    filled_fields: Dict[str, bool] = field(default_factory=dict, repr=False)

    def to_dict(self) -> Dict[str, str]:
        return {k: getattr(self, k) for k in CSV_FIELDS}


def load_sample_yaml(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_sample_companies(path: str) -> List[Dict[str, str]]:
    data = load_sample_yaml(path)
    companies = data.get("companies") or []
    out: List[Dict[str, str]] = []
    for c in companies:
        org = c.get("orgid") or c.get("org_id") or ""
        name = c.get("short_name") or c.get("company_name") or ""
        out.append({
            "company_code": str(c["stock_code"]),
            "company_name": str(name),
            "org_id": str(org),
            "board": str(c.get("board", "")),
            "exchange": str(c.get("exchange", "")),
            "suspected_no_dividend": "yes" if c.get("suspected_no_dividend") else "no",
        })
    return out


def _is_retry_889_partial_sample(sample_path: str) -> bool:
    return os.path.basename(sample_path) == RETRY_889_PARTIAL_SAMPLE_NAME


def _validate_pre_live_retry_partial(
    sample_path: str,
    companies: List[Dict[str, str]],
) -> Tuple[bool, str]:
    """targeted retry partial-fail 样本 live 前置校验；失败则不发起 CNINFO。"""
    with open(sample_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    issues: List[str] = []
    expected_co = RETRY_889_PARTIAL_EXPECTED_COMPANY_COUNT
    expected_cases = expected_co * SOURCE_COUNT_PER_COMPANY
    actual_co = len(companies)

    declared_count = data.get("company_count")
    if declared_count != expected_co:
        issues.append(
            f"company_count={declared_count!r} expected={expected_co}"
        )

    if actual_co != expected_co:
        issues.append(
            f"companies list length={actual_co} expected={expected_co}"
        )

    ftc = data.get("failure_type_counts")
    if not isinstance(ftc, dict):
        issues.append("failure_type_counts missing or not a mapping")
    else:
        for key, expected_n in RETRY_889_PARTIAL_EXPECTED_FAILURE_TYPE_COUNTS.items():
            actual_n = ftc.get(key)
            if actual_n != expected_n:
                issues.append(
                    f"failure_type_counts[{key}]={actual_n!r} expected={expected_n}"
                )
        extra_keys = set(ftc.keys()) - set(RETRY_889_PARTIAL_EXPECTED_FAILURE_TYPE_COUNTS)
        if extra_keys:
            issues.append(f"failure_type_counts unexpected keys: {sorted(extra_keys)}")

    actual_cases = actual_co * SOURCE_COUNT_PER_COMPANY
    if actual_cases != expected_cases:
        issues.append(
            f"cases={actual_co}x{SOURCE_COUNT_PER_COMPANY}={actual_cases} "
            f"expected={expected_cases}"
        )

    if issues:
        return False, "; ".join(issues)
    return True, (
        f"company_count={expected_co} "
        f"failure_type_counts={RETRY_889_PARTIAL_EXPECTED_FAILURE_TYPE_COUNTS} "
        f"cases={expected_cases}"
    )


def _referer(company_code: str, org_id: str) -> str:
    return (
        f"https://www.cninfo.com.cn/new/disclosure/stock"
        f"?stockCode={company_code}&orgId={org_id}"
    )


def _scode_url(base_url: str, company_code: str) -> str:
    return f"{base_url}?scode={company_code}"


def _security_url(company_code: str, org_id: str) -> str:
    return f"{SECURITY_URL}?secCode={company_code}&orgId={org_id}&secType=szshe"


def _browser_headers(company_code: str, org_id: str, xhr: bool = False) -> Dict[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
            "ListedCompanyDataCollector/c-class-scale-smoke-v1"
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
            if status == 429:
                return status, None, "rate_limited_429"
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


def _list_len(val: Any) -> int:
    return len(val) if isinstance(val, list) else 0


def _field_filled(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, str):
        return val.strip() != ""
    if isinstance(val, (list, dict)):
        return len(val) > 0
    return True


def _record_field_filled(record: Dict[str, Any], fname: str) -> bool:
    return fname in record and _field_filled(record.get(fname))


def _collect_field_fill(
    record: Optional[Dict[str, Any]],
    field_names: List[str],
) -> Dict[str, bool]:
    if not isinstance(record, dict):
        return {f: False for f in field_names}
    return {f: _record_field_filled(record, f) for f in field_names}


def _apply_http_error(row: CaseRow, http_status: Optional[int], err: str) -> CaseRow:
    row.error_message = err
    if err == "rate_limited_429":
        row.retrieval_status = "rate_limited"
    elif err in ("blocked_or_login_redirect", "captcha_detected"):
        row.retrieval_status = "blocked"
    elif http_status is None:
        row.retrieval_status = "http_error"
    else:
        row.retrieval_status = "blocked"
    row.case_result = "fail"
    return row


def validate_basic_live(company: Dict[str, str]) -> CaseRow:
    code = company["company_code"]
    org_id = company["org_id"]
    url = _scode_url(BASIC_URL, code)
    row = CaseRow(
        run_mode="live",
        source_id="cninfo_company_basic_profile",
        company_code=code,
        company_name=company["company_name"],
        org_id=org_id,
        board=company["board"],
        request_url=url,
        records_path="data.records[0]",
        suspected_no_dividend=company.get("suspected_no_dividend", "no"),
    )

    http_status, payload, err = _http_get(url, _browser_headers(code, org_id, xhr=False))
    row.http_status = str(http_status) if http_status is not None else ""
    if err:
        return _apply_http_error(row, http_status, err)

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
    basic_n = _list_len(basic)
    listing_n = _list_len(listing)
    row.record_count = str(basic_n)
    row.non_empty = "yes" if basic_n > 0 and listing_n > 0 else "no"

    basic0: Optional[Dict[str, Any]] = None
    if isinstance(basic, list) and basic and isinstance(basic[0], dict):
        basic0 = basic[0]

    # basic 关键字段 + derived 字段一并统计
    all_derived_fields: List[str] = []
    for fields in DERIVED_SOURCE_FIELDS.values():
        all_derived_fields.extend(fields)
    track_fields = list(dict.fromkeys(BASIC_KEY_FIELDS + all_derived_fields))
    row.filled_fields = _collect_field_fill(basic0, track_fields)
    row.field_fill_rates = ";".join(
        f"{k}={'1' if v else '0'}" for k, v in sorted(row.filled_fields.items())
    )

    if basic_n > 0 and listing_n > 0:
        row.retrieval_status = "endpoint_found"
        observed = ["basicInformation", "listingInformation"]
        if basic0:
            observed.extend(f"basicInformation.{k}" for k in sorted(basic0.keys()))
        row.observed_fields = ";".join(observed[:40])
        row.case_result = "pass"
    elif isinstance(record0, dict):
        row.retrieval_status = "empty_but_valid_response"
        row.observed_fields = "basicInformation;listingInformation"
        row.case_result = "fail"
    else:
        row.retrieval_status = "schema_unexpected"
        row.error_message = "records[0] not object"
        row.case_result = "fail"
    return row


def validate_records_list_live(source_id: str, company: Dict[str, str]) -> CaseRow:
    spec = SOURCE_SPECS[source_id]
    code = company["company_code"]
    org_id = company["org_id"]
    url = _scode_url(spec["url"], code)
    row = CaseRow(
        run_mode="live",
        source_id=source_id,
        company_code=code,
        company_name=company["company_name"],
        org_id=org_id,
        board=company["board"],
        request_url=url,
        records_path=spec["records_path"],
        suspected_no_dividend=company.get("suspected_no_dividend", "no"),
    )

    http_status, payload, err = _http_get(url, _browser_headers(code, org_id))
    row.http_status = str(http_status) if http_status is not None else ""
    if err:
        return _apply_http_error(row, http_status, err)

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

    allow_valid_empty = spec.get("allow_valid_empty", False)
    if len(records) == 0:
        if allow_valid_empty:
            row.retrieval_status = "valid_empty"
            row.non_empty = "no"
            row.case_result = "pass"
        elif source_id in SHAREHOLDER_SOURCE_IDS:
            # 股东源：HTTP 200 + 空 list 为有效空响应，endpoint 可达但 non_empty 下降
            row.retrieval_status = "empty_but_valid_response"
            row.non_empty = "no"
            row.case_result = "pass"
        else:
            row.retrieval_status = "empty_but_valid_response"
            row.non_empty = "no"
            row.case_result = "fail"
        return row

    first = records[0]
    if not isinstance(first, dict):
        row.retrieval_status = "schema_unexpected"
        row.error_message = "records[0] not object"
        row.case_result = "fail"
        return row

    required = spec.get("expected_fields") or []
    optional = spec.get("optional_fields") or []
    missing = [f for f in required if f not in first]
    row.filled_fields = _collect_field_fill(first, required)
    row.field_fill_rates = ";".join(
        f"{k}={'1' if v else '0'}" for k, v in sorted(row.filled_fields.items())
    )
    observed = [f for f in required + optional if f in first]
    row.observed_fields = ";".join(observed)
    row.missing_fields = ";".join(missing)
    row.non_empty = "yes"

    if missing:
        row.retrieval_status = "schema_unexpected"
        row.error_message = f"missing required fields: {', '.join(missing)}"
        row.case_result = "fail"
        return row

    row.retrieval_status = "endpoint_found"
    row.case_result = "pass"
    return row


def validate_security_observe(company: Dict[str, str]) -> CaseRow:
    code = company["company_code"]
    org_id = company["org_id"]
    url = _security_url(code, org_id)
    required = (
        "secCode", "secName", "secType", "tradingStatus",
        "age", "finance", "delisted",
    )
    row = CaseRow(
        run_mode="live",
        source_id=OBSERVE_SOURCE_ID,
        company_code=code,
        company_name=company["company_name"],
        org_id=org_id,
        board=company["board"],
        request_url=url,
        records_path="$",
        suspected_no_dividend=company.get("suspected_no_dividend", "no"),
    )

    http_status, payload, err = _http_get(url, _browser_headers(code, org_id, xhr=True))
    row.http_status = str(http_status) if http_status is not None else ""
    if err:
        return _apply_http_error(row, http_status, err)

    json_code, result_code = _extract_codes(payload)
    row.json_code = json_code
    row.result_code = result_code

    if http_status != 200 or not isinstance(payload, dict):
        row.retrieval_status = "http_error"
        row.case_result = "observe_fail"
        return row

    missing = [f for f in required if f not in payload]
    observed = [f for f in required if f in payload]
    row.observed_fields = ";".join(observed)
    row.missing_fields = ";".join(missing)
    if missing:
        row.retrieval_status = "schema_unexpected"
        row.case_result = "observe_fail"
        return row

    row.retrieval_status = "endpoint_found"
    row.case_result = "observe_pass"
    return row


def build_dry_run_rows(companies: List[Dict[str, str]]) -> List[CaseRow]:
    rows: List[CaseRow] = []
    request_sources = list(MAIN_SOURCE_IDS) + [OBSERVE_SOURCE_ID]
    for source_id in request_sources:
        spec = SOURCE_SPECS[source_id]
        for company in companies:
            if source_id == OBSERVE_SOURCE_ID:
                url = _security_url(company["company_code"], company["org_id"])
            else:
                url = _scode_url(spec["url"], company["company_code"])
            rows.append(CaseRow(
                run_mode="dry-run",
                source_id=source_id,
                company_code=company["company_code"],
                company_name=company["company_name"],
                org_id=company["org_id"],
                board=company["board"],
                request_url=url,
                records_path=spec.get("records_path", ""),
                case_result="skipped",
                suspected_no_dividend=company.get("suspected_no_dividend", "no"),
            ))
    return rows


def _format_duration(seconds: float) -> str:
    return f"{seconds:.1f}s"


def _live_progress_stats(rows: List[CaseRow]) -> Dict[str, int]:
    return {
        "pass": sum(1 for r in rows if r.case_result == "pass"),
        "fail": sum(1 for r in rows if r.case_result == "fail"),
        "observe_pass": sum(1 for r in rows if r.case_result == "observe_pass"),
        "blocked": sum(1 for r in rows if r.retrieval_status == "blocked"),
        "http_error": sum(1 for r in rows if r.retrieval_status == "http_error"),
        "429": sum(1 for r in rows if r.retrieval_status == "rate_limited"),
    }


def _log_live_progress(rows: List[CaseRow], total: int, start_time: float) -> None:
    completed = len(rows)
    stats = _live_progress_stats(rows)
    elapsed = time.time() - start_time
    remaining = (elapsed / completed * (total - completed)) if completed else 0.0
    print(
        f"progress: completed={completed}/{total} "
        f"pass={stats['pass']} fail={stats['fail']} observe_pass={stats['observe_pass']} "
        f"blocked={stats['blocked']} http_error={stats['http_error']} 429={stats['429']} "
        f"elapsed={_format_duration(elapsed)} "
        f"estimated_remaining={_format_duration(remaining)}",
        flush=True,
    )


def _on_live_case_done(rows: List[CaseRow], total: int, start_time: float) -> None:
    if len(rows) % LIVE_PROGRESS_INTERVAL == 0:
        _log_live_progress(rows, total, start_time)


def run_live(companies: List[Dict[str, str]]) -> List[CaseRow]:
    rows: List[CaseRow] = []
    request_count = 0
    total_requests = len(companies) * (len(MAIN_SOURCE_IDS) + 1)
    start_time = time.time()

    for company in companies:
        rows.append(validate_basic_live(company))
        request_count += 1
        _on_live_case_done(rows, total_requests, start_time)
        if request_count < total_requests:
            time.sleep(SLEEP_SECONDS)

        rows.append(validate_records_list_live("cninfo_dividend_financing_profile", company))
        request_count += 1
        _on_live_case_done(rows, total_requests, start_time)
        if request_count < total_requests:
            time.sleep(SLEEP_SECONDS)

        for sid in MAIN_SOURCE_IDS[2:]:
            rows.append(validate_records_list_live(sid, company))
            request_count += 1
            _on_live_case_done(rows, total_requests, start_time)
            if request_count < total_requests:
                time.sleep(SLEEP_SECONDS)

        rows.append(validate_security_observe(company))
        request_count += 1
        _on_live_case_done(rows, total_requests, start_time)
        if request_count < total_requests:
            time.sleep(SLEEP_SECONDS)

    if len(rows) % LIVE_PROGRESS_INTERVAL != 0:
        _log_live_progress(rows, total_requests, start_time)

    return rows


def _is_reachable(status: str, source_id: str = "") -> bool:
    if status in ("endpoint_found", "valid_empty"):
        return True
    if source_id in SHAREHOLDER_SOURCE_IDS and status == "empty_but_valid_response":
        return True
    return False


def _field_fill_aggregate(rows: List[CaseRow], field_names: List[str]) -> Dict[str, float]:
    eligible = [r for r in rows if r.retrieval_status == "endpoint_found" and r.filled_fields]
    if not eligible:
        return {f: 0.0 for f in field_names}
    out: Dict[str, float] = {}
    for f in field_names:
        filled = sum(1 for r in eligible if r.filled_fields.get(f))
        out[f] = filled / len(eligible)
    return out


def _aggregate_by_source(rows: List[CaseRow], companies: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    all_sources = list(MAIN_SOURCE_IDS) + [OBSERVE_SOURCE_ID]
    out: List[Dict[str, Any]] = []
    n_companies = len(companies)

    for sid in all_sources:
        subset = [r for r in rows if r.source_id == sid]
        status_ctr = Counter(r.retrieval_status for r in subset if r.retrieval_status)
        reachable = sum(1 for r in subset if _is_reachable(r.retrieval_status, sid))
        pass_n = sum(1 for r in subset if r.case_result == "pass")
        fail_n = sum(1 for r in subset if r.case_result == "fail")
        blocked = status_ctr.get("blocked", 0)
        rate429 = status_ctr.get("rate_limited", 0)
        http_err = status_ctr.get("http_error", 0)
        non_empty_n = sum(1 for r in subset if r.non_empty == "yes")
        valid_empty_n = status_ctr.get("valid_empty", 0)

        out.append({
            "source_id": sid,
            "total": len(subset),
            "companies": n_companies,
            "pass": pass_n,
            "fail": fail_n,
            "skipped": sum(1 for r in subset if r.case_result == "skipped"),
            "reachable": reachable,
            "reachability_pct": (reachable / n_companies * 100) if n_companies else 0,
            "non_empty": non_empty_n,
            "non_empty_rate_pct": (non_empty_n / n_companies * 100) if n_companies else 0,
            "valid_empty": valid_empty_n,
            "endpoint_found": status_ctr.get("endpoint_found", 0),
            "empty_but_valid_response": status_ctr.get("empty_but_valid_response", 0),
            "schema_unexpected": status_ctr.get("schema_unexpected", 0),
            "blocked": blocked,
            "rate_limited_429": rate429,
            "http_error": http_err,
            "error_rate_pct": ((blocked + rate429 + http_err) / n_companies * 100) if n_companies else 0,
        })
    return out


def _board_group_stats(rows: List[CaseRow]) -> List[Dict[str, Any]]:
    boards = sorted({r.board for r in rows if r.board})
    out: List[Dict[str, Any]] = []
    for board in boards:
        for sid in MAIN_SOURCE_IDS:
            subset = [r for r in rows if r.board == board and r.source_id == sid]
            if not subset:
                continue
            reachable = sum(1 for r in subset if _is_reachable(r.retrieval_status, sid))
            pass_n = sum(1 for r in subset if r.case_result == "pass")
            out.append({
                "board": board,
                "source_id": sid,
                "total": len(subset),
                "reachable": reachable,
                "reachability_pct": reachable / len(subset) * 100,
                "pass": pass_n,
                "pass_pct": pass_n / len(subset) * 100,
            })
    return out


def _derived_fill_from_basic(rows: List[CaseRow]) -> Dict[str, Dict[str, float]]:
    basic_rows = [r for r in rows if r.source_id == "cninfo_company_basic_profile"
                  and r.retrieval_status == "endpoint_found" and r.filled_fields]
    out: Dict[str, Dict[str, float]] = {}
    n = len(basic_rows)
    for derived_sid, fields in DERIVED_SOURCE_FIELDS.items():
        rates: Dict[str, float] = {}
        for f in fields:
            rates[f] = (sum(1 for r in basic_rows if r.filled_fields.get(f)) / n) if n else 0.0
        out[derived_sid] = rates
    return out


def _dividend_empty_distribution(rows: List[CaseRow]) -> Dict[str, int]:
    div_rows = [r for r in rows if r.source_id == "cninfo_dividend_financing_profile"]
    return dict(Counter(r.retrieval_status for r in div_rows))


def _gate_dividend_backfill(agg: List[Dict[str, Any]], div_dist: Dict[str, int]) -> Tuple[str, str]:
    div = next(a for a in agg if a["source_id"] == "cninfo_dividend_financing_profile")
    reach = div["reachability_pct"] / 100
    err_rate = div["error_rate_pct"] / 100
    valid_empty = div_dist.get("valid_empty", 0)

    if reach >= REACHABILITY_THRESHOLD and err_rate < ERROR_RATE_THRESHOLD:
        rename_note = (
            "建议 YAML backfill 时窄化命名为 `dividend_history`（或等价语义），"
            "以消除 financing 过度承诺；当前 endpoint 仅覆盖历史分红。"
        )
        return (
            "GO",
            f"dividend reachability={div['reachability_pct']:.1f}% "
            f"error_rate={div['error_rate_pct']:.1f}% valid_empty={valid_empty}. "
            f"{rename_note}",
        )
    return (
        "NO-GO",
        f"dividend reachability={div['reachability_pct']:.1f}% "
        f"error_rate={div['error_rate_pct']:.1f}% — 未达门槛 "
        f"(reach>={REACHABILITY_THRESHOLD*100:.0f}% & error<{ERROR_RATE_THRESHOLD*100:.0f}%).",
    )


def _gate_to_200(agg: List[Dict[str, Any]], board_stats: List[Dict[str, Any]]) -> Tuple[str, str]:
    decision, detail = _gate_enter_200(agg, board_stats, [], is_active_sample=False)
    if decision in ("YES", "CONDITIONAL_YES"):
        return "GO", detail
    if decision == "CONDITIONAL":
        return "CONDITIONAL", detail
    return "NO", detail


def _gate_enter_200(
    agg: List[Dict[str, Any]],
    board_stats: List[Dict[str, Any]],
    empty_shareholder_cases: List[CaseRow],
    is_active_sample: bool,
) -> Tuple[str, str]:
    """扩至 200 家 gate：active 样本达标时可 YES / CONDITIONAL_YES。"""
    issues: List[str] = []
    caveats: List[str] = []

    total_blocked = sum(a["blocked"] for a in agg)
    total_429 = sum(a["rate_limited_429"] for a in agg)
    if total_blocked > 0 or total_429 > 0:
        issues.append(f"blocked={total_blocked} rate_limited_429={total_429}")

    basic = next(a for a in agg if a["source_id"] == "cninfo_company_basic_profile")
    div = next(a for a in agg if a["source_id"] == "cninfo_dividend_financing_profile")

    if basic["reachability_pct"] < REACHABILITY_THRESHOLD * 100:
        issues.append(f"basic reachability {basic['reachability_pct']:.1f}%")
    if basic["non_empty_rate_pct"] < BASIC_NON_EMPTY_THRESHOLD * 100:
        issues.append(f"basic non_empty {basic['non_empty_rate_pct']:.1f}%")
    if div["reachability_pct"] < REACHABILITY_THRESHOLD * 100:
        issues.append(f"dividend reachability {div['reachability_pct']:.1f}%")

    for a in agg:
        if a["source_id"] in (OBSERVE_SOURCE_ID,):
            continue
        if a["error_rate_pct"] >= ERROR_RATE_THRESHOLD * 100:
            issues.append(f"{a['source_id']}: error_rate {a['error_rate_pct']:.1f}%")

    board_failures = [
        bs for bs in board_stats
        if bs["source_id"] in MAIN_SOURCE_IDS and bs["pass_pct"] < 80
    ]
    for bs in board_failures:
        issues.append(f"board {bs['board']} / {bs['source_id']}: pass {bs['pass_pct']:.1f}%")

    if empty_shareholder_cases:
        caveats.append(
            f"empty_but_valid 股东源 {len(empty_shareholder_cases)} 例（新股/数据空，非 blocked）"
        )

    sec = next((a for a in agg if a["source_id"] == OBSERVE_SOURCE_ID), None)
    if sec and sec["error_rate_pct"] == 0:
        caveats.append("security secType=szshe 硬编码跨板块风险尚未验证，扩 200 时继续单列观察")

    if issues:
        prefix = "active-only 样本" if is_active_sample else "当前样本"
        return "CONDITIONAL", f"{prefix}扩至 200 家前需修复：" + "; ".join(issues)

    if caveats:
        return (
            "CONDITIONAL_YES",
            "门槛达标，可进入 200 家 smoke（保持 sleep 限流与分板块监控）。注意："
            + "; ".join(caveats),
        )
    return (
        "YES",
        "30 家门槛达标：reachability>=95%、basic non_empty>=90%、blocked/429=0、"
        "无板块系统性失败。可扩至 200 家。",
    )


def _empty_but_valid_shareholder_cases(rows: List[CaseRow]) -> List[CaseRow]:
    shareholder_sources = (
        "cninfo_top_shareholders_profile",
        "cninfo_top_float_shareholders_profile",
    )
    return [
        r for r in rows
        if r.source_id in shareholder_sources
        and r.retrieval_status == "empty_but_valid_response"
    ]


def _sample_strata(companies: List[Dict[str, str]]) -> Dict[str, int]:
    return dict(Counter(c["board"] for c in companies))


def _load_previous_baseline(csv_path: str) -> Optional[Dict[str, Any]]:
    """从上一轮含退市样本 report CSV 加载对比基线。"""
    if not os.path.isfile(csv_path):
        return None
    rows_raw: List[Dict[str, str]] = []
    with open(csv_path, encoding="utf-8") as fh:
        rows_raw = list(csv.DictReader(fh))
    if not rows_raw or rows_raw[0].get("run_mode") != "live":
        return None

    class _Mini:
        def __init__(self, d: Dict[str, str]):
            self.source_id = d.get("source_id", "")
            self.retrieval_status = d.get("retrieval_status", "")
            self.case_result = d.get("case_result", "")
            self.board = d.get("board", "")

    mini = [_Mini(d) for d in rows_raw]
    companies_n = len({d.get("company_code") for d in rows_raw})
    agg = []
    for sid in list(MAIN_SOURCE_IDS) + [OBSERVE_SOURCE_ID]:
        subset = [m for m in mini if m.source_id == sid]
        reachable = sum(
            1 for m in subset
            if m.retrieval_status in ("endpoint_found", "valid_empty")
        )
        agg.append({
            "source_id": sid,
            "reachable": reachable,
            "reachability_pct": reachable / companies_n * 100 if companies_n else 0,
            "pass": sum(1 for m in subset if m.case_result == "pass"),
            "fail": sum(1 for m in subset if m.case_result == "fail"),
            "blocked": sum(1 for m in subset if m.retrieval_status == "blocked"),
            "rate_limited_429": sum(1 for m in subset if m.retrieval_status == "rate_limited"),
            "http_error": sum(1 for m in subset if m.retrieval_status == "http_error"),
        })
    return {
        "label": "含退市样本（上一轮）",
        "companies": companies_n,
        "pass": sum(1 for m in mini if m.case_result == "pass"),
        "fail": sum(1 for m in mini if m.case_result == "fail"),
        "agg": agg,
    }


def _resolve_output_paths(
    sample_path: str,
    output_csv: Optional[str],
    output_md: Optional[str],
    run_mode: str = "dry_run",
) -> Tuple[str, str]:
    base = os.path.basename(sample_path)
    if output_csv and output_md:
        return output_csv, output_md
    if "stable_200_non_bse" in base or "stable_200" in base:
        if run_mode == "live":
            return (
                output_csv or DEFAULT_STABLE_200_LIVE_CSV,
                output_md or DEFAULT_STABLE_200_LIVE_MD,
            )
        return (
            output_csv or DEFAULT_STABLE_200_DRYRUN_CSV,
            output_md or DEFAULT_STABLE_200_DRYRUN_MD,
        )
    if "retry_889_partial_fail" in base or "retry_889_partial" in base:
        if run_mode == "live":
            return (
                output_csv or DEFAULT_RETRY_889_PARTIAL_LIVE_CSV,
                output_md or DEFAULT_RETRY_889_PARTIAL_LIVE_MD,
            )
        return (
            output_csv or DEFAULT_RETRY_889_PARTIAL_DRYRUN_CSV,
            output_md or DEFAULT_RETRY_889_PARTIAL_DRYRUN_MD,
        )
    if "1000_non_bse" in base or "non_bse_candidate" in base:
        if run_mode == "live":
            return (
                output_csv or DEFAULT_1000_NON_BSE_LIVE_CSV,
                output_md or DEFAULT_1000_NON_BSE_LIVE_MD,
            )
        return (
            output_csv or DEFAULT_1000_NON_BSE_DRYRUN_CSV,
            output_md or DEFAULT_1000_NON_BSE_DRYRUN_MD,
        )
    if "smoke_200" in base or "200_active" in base:
        return output_csv or DEFAULT_ACTIVE_200_CSV, output_md or DEFAULT_ACTIVE_200_MD
    if "active" in base:
        return output_csv or DEFAULT_ACTIVE_CSV, output_md or DEFAULT_ACTIVE_MD
    return output_csv or DEFAULT_CSV, output_md or DEFAULT_MD


def write_csv(path: str, rows: List[CaseRow]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict())


def write_summary_md(
    path: str,
    rows: List[CaseRow],
    companies: List[Dict[str, str]],
    run_mode: str,
    sample_path: str,
    previous_baseline: Optional[Dict[str, Any]] = None,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    agg = _aggregate_by_source(rows, companies)
    board_stats = _board_group_stats(rows)
    derived_fill = _derived_fill_from_basic(rows)
    div_dist = _dividend_empty_distribution(rows)
    strata = _sample_strata(companies)
    empty_sh = _empty_but_valid_shareholder_cases(rows)
    is_active = "active" in os.path.basename(sample_path)

    basic_rows = [r for r in rows if r.source_id == "cninfo_company_basic_profile"
                  and r.retrieval_status == "endpoint_found"]
    basic_key_fill = _field_fill_aggregate(basic_rows, BASIC_KEY_FIELDS)

    div_rows = [r for r in rows if r.source_id == "cninfo_dividend_financing_profile"
                and r.retrieval_status == "endpoint_found"]
    div_fields = SOURCE_SPECS["cninfo_dividend_financing_profile"]["expected_fields"]
    div_field_fill = _field_fill_aggregate(div_rows, div_fields)

    div_gate, div_gate_detail = _gate_dividend_backfill(agg, div_dist)
    enter_200, enter_200_detail = _gate_enter_200(
        agg, board_stats, empty_sh, is_active_sample=is_active
    )
    scale_gate = enter_200
    scale_gate_detail = enter_200_detail

    total_pass = sum(1 for r in rows if r.case_result == "pass")
    total_fail = sum(1 for r in rows if r.case_result == "fail")
    total_skip = sum(1 for r in rows if r.case_result == "skipped")
    total_blocked = sum(1 for r in rows if r.retrieval_status == "blocked")
    total_429 = sum(1 for r in rows if r.retrieval_status == "rate_limited")

    sample_base = os.path.basename(sample_path)
    is_active = "active" in sample_base
    is_200 = "smoke_200" in sample_base or "200_active" in sample_base
    is_1000_non_bse = "1000_non_bse" in sample_base or "non_bse_candidate" in sample_base
    is_retry_889 = "retry_889" in sample_base
    is_stable_200 = "stable_200" in sample_base
    sample_meta = load_sample_yaml(sample_path) if is_stable_200 else {}

    if is_stable_200:
        title = (
            f"CNINFO C Class Stable 200 Non-BSE "
            f"({'Dry-Run' if run_mode == 'dry-run' else 'Live'}) Summary"
        )
    elif is_retry_889:
        title = (
            f"CNINFO C Class 889 Retry — Partial Fail Targeted "
            f"({'Dry-Run' if run_mode == 'dry-run' else 'Live'}) — {len(companies)} companies"
        )
    elif is_1000_non_bse:
        title = (
            f"CNINFO C Class {len(companies)}-Company Non-BSE 1000-like Dry-Run Summary"
        )
    elif is_200:
        title = (
            f"CNINFO C Class {len(companies)}-Company Scale Smoke Summary (Active-Only)"
        )
    elif is_active:
        title = "CNINFO C Class 30-Company Scale Smoke Summary (Active-Only)"
    else:
        title = "CNINFO C Class 30-Company Scale Smoke Summary"

    lines = [
        f"# {title}",
        "",
        f"_生成时间：{now}_",
        "",
        "## Run mode",
        "",
        f"**{run_mode}**",
        "",
        "## Scope",
        "",
        f"- **Sample:** `{sample_path}` ({len(companies)} companies)",
        "- **主判定 source:** basic · dividend · P2-A 四源",
        "- **观察维度:** security（不绑定主判定）",
        "- **derived 三源:** contact / business_scope / industry（随 basic fill_rate，无单独请求）",
        "",
    ]
    if is_stable_200:
        excl = sample_meta.get("excluded_by_reason") or {}
        rules = sample_meta.get("cleaning_rules") or []
        targets = sample_meta.get("board_targets") or {}
        lines.extend([
            "## Stable sample design",
            "",
            f"- **Parent:** `{sample_meta.get('parent_candidate', '')}` ({sample_meta.get('parent_candidate_count', '?')} companies)",
            f"- **Eligible pool after cleaning:** {sample_meta.get('eligible_pool_count', '?')}",
            f"- **Excluded from pool:** {sample_meta.get('excluded_count', '?')}",
            "",
            "### Exclusion rules",
            "",
        ])
        for rule in rules:
            lines.append(f"- {rule}")
        lines.extend([
            "",
            "### Excluded by reason",
            "",
            "| reason | count |",
            "|--------|-------|",
        ])
        for reason, cnt in sorted(excl.items()):
            lines.append(f"| `{reason}` | {cnt} |")
        if targets:
            lines.extend([
                "",
                "### Board targets vs actual",
                "",
                "| board | target | actual |",
                "|-------|--------|--------|",
            ])
            for board, tgt in sorted(targets.items()):
                lines.append(f"| `{board}` | {tgt} | {strata.get(board, 0)} |")
        lines.extend([
            "",
            "### Source policy（[source status decision](../plans/cninfo_c_class_source_status_decision.md)）",
            "",
            "- **主判定 source（6）：** basic · dividend · executive · share_capital · top_shareholders · top_float",
            "- **observe_only：** security（不绑定主 gate）",
            "- **derived_no_separate_fetch：** contact · business_scope · industry",
            "- **source_partial 提醒：** share_capital · top_float（reachable ≠ non_empty）",
            "",
        ])
    lines.extend([
        "## Active-only 样本分层",
        "",
        "| board | count |",
        "|-------|-------|",
    ])
    for board, cnt in sorted(strata.items()):
        lines.append(f"| `{board}` | {cnt} |")

    lines.extend([
        "",
        f"**pass / fail / blocked / 429:** {total_pass} / {total_fail} / {total_blocked} / {total_429}",
        "",
        f"**Planned live requests per company:** {len(MAIN_SOURCE_IDS) + 1}",
        f"**Total planned (live):** {len(companies) * (len(MAIN_SOURCE_IDS) + 1)}",
        "",
        "## Per-source reachability",
        "",
        "| source_id | reachable | reachability% | non_empty | non_empty% | valid_empty | "
        "blocked | 429 | http_error | error% | pass | fail |",
        "|-----------|-----------|---------------|-----------|------------|-------------|"
        "---------|-----|------------|--------|------|------|",
    ])
    for a in agg:
        lines.append(
            f"| `{a['source_id']}` | {a['reachable']}/{a['companies']} | "
            f"{a['reachability_pct']:.1f}% | {a['non_empty']} | {a['non_empty_rate_pct']:.1f}% | "
            f"{a['valid_empty']} | {a['blocked']} | {a['rate_limited_429']} | "
            f"{a['http_error']} | {a['error_rate_pct']:.1f}% | {a['pass']} | {a['fail']} |"
        )

    lines.extend([
        "",
        "## Basic key field fill_rate (endpoint_found only)",
        "",
        "| field | fill_rate% |",
        "|-------|------------|",
    ])
    for f, rate in sorted(basic_key_fill.items()):
        lines.append(f"| `{f}` | {rate * 100:.1f}% |")

    lines.extend([
        "",
        "## Dividend field fill_rate (non-empty records only)",
        "",
        "| field | fill_rate% |",
        "|-------|------------|",
    ])
    for f, rate in sorted(div_field_fill.items()):
        lines.append(f"| `{f}` | {rate * 100:.1f}% |")

    lines.extend([
        "",
        "## Dividend empty distribution",
        "",
        "| status | count |",
        "|--------|-------|",
    ])
    for status, cnt in sorted(div_dist.items()):
        lines.append(f"| `{status}` | {cnt} |")

    lines.extend([
        "",
        "## empty_but_valid 股东源案例",
        "",
    ])
    if empty_sh:
        lines.append("| company_code | company_name | board | source_id | record_count |")
        lines.append("|--------------|--------------|-------|-----------|--------------|")
        for r in empty_sh:
            lines.append(
                f"| `{r.company_code}` | {r.company_name} | `{r.board}` | "
                f"`{r.source_id}` | {r.record_count} |"
            )
    else:
        lines.append("- 无")

    sh_empty_n = sum(
        1 for r in rows
        if r.source_id in SHAREHOLDER_SOURCE_IDS
        and r.retrieval_status == "empty_but_valid_response"
    )
    lines.extend([
        "",
        "## Shareholder empty_but_valid policy",
        "",
        f"- **empty_but_valid_count（股东源）:** {sh_empty_n}",
        "- HTTP 200 · json/resultCode 正常 · `data.records` 为空 list → `empty_but_valid_response`",
        "- **不计** http_error / blocked / schema_unexpected；**计入** endpoint reachable",
        "- 主 gate **case_result=pass**（非接口失败）；**non_empty_rate** 仍下降",
        "- top_float / top_shareholders 标记 **source_partial**（reachable ≠ non_empty）",
    ])

    if previous_baseline and is_active:
        lines.extend([
            "",
            "## 与上一轮含退市样本对比",
            "",
            f"**上一轮：** {previous_baseline['label']} · "
            f"pass={previous_baseline['pass']} fail={previous_baseline['fail']}",
            f"**本轮 active-only：** pass={total_pass} fail={total_fail}",
            "",
            "| source_id | 上一轮 reachability% | 本轮 reachability% | Δ fail |",
            "|-----------|---------------------|-------------------|--------|",
        ])
        prev_by_sid = {a["source_id"]: a for a in previous_baseline["agg"]}
        for a in agg:
            prev = prev_by_sid.get(a["source_id"], {})
            delta_fail = a["fail"] - prev.get("fail", 0)
            sign = "+" if delta_fail > 0 else ""
            lines.append(
                f"| `{a['source_id']}` | {prev.get('reachability_pct', 0):.1f}% | "
                f"{a['reachability_pct']:.1f}% | {sign}{delta_fail} |"
            )
        lines.extend([
            "",
            "**解读：** 上一轮 3 家退市标的（600647 / 600002 / 002473）各拖累 6 条主判定 fail；"
            "剔除后 fail 应显著下降，reachability 应升至 ~100%。",
            "",
        ])

    lines.extend([
        "",
        "## Derived sources (from basic basicInformation)",
        "",
    ])
    for derived_sid, rates in derived_fill.items():
        lines.append(f"### `{derived_sid}`")
        lines.append("")
        lines.append("| field | fill_rate% |")
        lines.append("|-------|------------|")
        for f, rate in sorted(rates.items()):
            lines.append(f"| `{f}` | {rate * 100:.1f}% |")
        lines.append("")

    lines.extend([
        "## Board-group pass rate (main judgment sources)",
        "",
        "| board | source_id | pass | total | pass% | reachability% |",
        "|-------|-----------|------|-------|-------|---------------|",
    ])
    for bs in board_stats:
        lines.append(
            f"| `{bs['board']}` | `{bs['source_id']}` | {bs['pass']} | {bs['total']} | "
            f"{bs['pass_pct']:.1f}% | {bs['reachability_pct']:.1f}% |"
        )

    overall = (
        "DRY_RUN_ONLY" if run_mode == "dry-run"
        else ("LIVE_PASS" if total_fail == 0 else "LIVE_PARTIAL")
    )
    lines.extend([
        "",
        f"**Overall:** pass={total_pass} fail={total_fail} skipped={total_skip} **result={overall}**",
    ])
    if run_mode == "dry-run":
        lines.extend([
            "",
            "## Dry-run confirmation",
            "",
            f"- **No CNINFO requests executed**（all cases skipped）",
            f"- **Company count:** {len(companies)}",
            f"- **Cases:** {len(rows)} = {len(companies)} × {len(MAIN_SOURCE_IDS) + 1} sources",
            f"- **Planned live requests:** {len(companies) * (len(MAIN_SOURCE_IDS) + 1)}",
            "- **主判定 source:** basic · dividend · P2-A 四源（executive / share_capital / top_shareholders / top_float）",
            "- **security_profile:** observe-only（不绑定主判定 gate）",
            "- **derived 三源:** contact / business_scope / industry — 无单独 HTTP 请求，仅 live 时随 basic fill_rate 统计",
        ])
        if is_stable_200:
            lines.extend([
                "- **stable_200_non_bse** cleaned sample；验证清洗异常后 non-BSE 稳定性。",
                "- **derived 三源无单独请求**；**security observe-only**；**source_partial** 口径见 Source policy。",
            ])
    lines.extend([
        "",
        "## Gate: dividend YAML backfill",
        "",
        f"**Decision: {div_gate}**",
        "",
        div_gate_detail,
    ])
    if is_stable_200:
        lines.extend([
            "",
            "## Gate: stable 200 non-BSE",
            "",
            f"**stable_gate = {'DRY_RUN_READY' if run_mode == 'dry-run' else 'LIVE_PENDING_APPROVAL'}**",
            "",
            f"Cleaned stable sample **{len(companies)}** 家；planned live **{len(companies) * (len(MAIN_SOURCE_IDS) + 1)}** requests。",
            "目的：验证剔除 six_fail_hold 后 non-BSE 主宇宙是否稳定。",
            "**等待人工批准**后跑 `--live`。",
        ])
    elif is_retry_889:
        lines.extend([
            "",
            "## Gate: targeted retry",
            "",
            f"**retry_gate = {'DRY_RUN_READY' if run_mode == 'dry-run' else 'LIVE_PENDING_REVIEW'}**",
            "",
            f"Partial-fail subset **{len(companies)}** 家；planned live **{len(companies) * (len(MAIN_SOURCE_IDS) + 1)}** requests。",
            "26 家 6/6 全失败已 hold，不在此样本。",
            "**等待人工批准**后跑 `--live`。",
        ])
    elif is_1000_non_bse:
        lines.extend([
            "",
            "## Gate: post-889 scale / next planning",
            "",
            f"**next_gate = {'DIAGNOSIS_PENDING' if run_mode == 'dry-run' else 'SEE_DIAGNOSIS'}**",
            "",
            "889-company non-BSE 1000-like；下一门槛为 post-889 diagnosis / full-market non-BSE planning（非 enter_200）。",
        ])
    else:
        lines.extend([
            "",
            "## Gate: expand to 200 companies",
            "",
            f"**enter_200 = {scale_gate}**",
            "",
            scale_gate_detail,
        ])
    lines.extend([
        "",
        "## Caveats",
        "",
    ])
    if is_stable_200:
        if run_mode == "live":
            lines.extend([
                "- **stable 200 non-BSE live**；非 889 全量；非 verified / testing_stable_sample。",
            ])
        else:
            lines.extend([
                "- **stable 200 non-BSE dry-run**；planned live only；**无 CNINFO**。",
                "- 26 家 six_fail_hold 已从池中剔除。",
            ])
        lines.extend([
            "- **testing** status only; **no verified**.",
            "- **No testing_stable_sample**（文件名 stable 仅为设计语义）。",
            "- No database ingestion.",
            "- observe_only / derived_no_separate_fetch / source_partial 口径见 [source status decision](../plans/cninfo_c_class_source_status_decision.md)。",
        ])
    elif is_retry_889:
        if run_mode == "live":
            lines.extend([
                "- **889 partial-fail targeted retry live**；非 889 全量重跑。",
                "- 26 家 6/6 全失败见 `eval_companies_c_class_retry_889_six_fail_hold.yaml`（hold）。",
            ])
        else:
            lines.extend([
                "- **889 partial-fail targeted retry dry-run**；planned live only；**无 CNINFO**。",
                "- 26 家 6/6 全失败已剔除；见 six_fail_hold 样本。",
            ])
        lines.extend([
            "- **testing** status only; **no verified**.",
            "- **No testing_stable_sample**.",
            "- No database ingestion.",
            "- 股东 empty_but_valid 口径已修正（见 Shareholder empty_but_valid policy）。",
        ])
    elif is_1000_non_bse:
        if run_mode == "live":
            lines.extend([
                "- **889-company non-BSE 1000-like live sample**；非 full-market verified。",
                "- Live 输出：`cninfo_c_class_smoke_1000_non_bse_live_report.csv` / `_live_summary.md`。",
                "- Next gate: post-889 diagnosis / possible 1000 or full-market non-BSE planning.",
            ])
        else:
            lines.extend([
                "- **889-company non-BSE 1000-like dry-run**；planned live only；无 CNINFO。",
            ])
        lines.extend([
            "- **testing** status only; **no verified**.",
            "- **No testing_stable_sample**.",
            "- No database ingestion.",
            "- security observe-only；不绑定主 gate。",
        ])
    else:
        lines.extend([
            "- 30-company stratified sample only; not full-market.",
            "- **testing** status only; **no verified**.",
            "- **No testing_stable_sample**.",
            "- No database ingestion.",
            "- security uses hardcoded `secType=szshe`; cross-board risk observed separately.",
        ])
    if is_active:
        lines.append(
            "- active 样本以 YAML 名称 heuristics 剔除退市，未联网校验 *ST 等上市状态。"
        )
    lines.extend([
        "",
        "## Appendix",
        "",
        f"详见 [{os.path.basename(path.replace('.md', '.csv'))}]({os.path.basename(path.replace('.md', '.csv'))})。",
        "",
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="C-class 30-company scale smoke test (dry-run default)"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")
    parser.add_argument("--sample", default=None, help="样本 YAML 路径")
    parser.add_argument(
        "--sample-file", dest="sample", default=None,
        help="样本 YAML 路径（--sample 别名）",
    )
    parser.add_argument("--output-csv", default=None)
    parser.add_argument("--output-md", default=None)
    parser.add_argument(
        "--compare-with",
        default=PREVIOUS_BASELINE_CSV,
        help="上一轮 report CSV，用于 active rerun 对比",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_path = args.sample or DEFAULT_SAMPLE
    output_csv, output_md = _resolve_output_paths(
        sample_path, args.output_csv, args.output_md, args.mode
    )
    companies = load_sample_companies(sample_path)
    if args.mode == "live" and len(companies) < 10:
        print(f"WARN: very small sample ({len(companies)} companies)", file=sys.stderr)

    if args.mode == "live" and _is_retry_889_partial_sample(sample_path):
        ok, detail = _validate_pre_live_retry_partial(sample_path, companies)
        if ok:
            print(f"pre_live_validation: PASS  ({detail})")
        else:
            print(f"pre_live_validation: FAIL  ({detail})")
            sys.exit(2)

    previous_baseline = None
    if "active" in os.path.basename(sample_path) and os.path.isfile(args.compare_with):
        previous_baseline = _load_previous_baseline(args.compare_with)

    if args.mode == "live":
        rows = run_live(companies)
        run_label = "live"
    else:
        rows = build_dry_run_rows(companies)
        run_label = "dry-run"

    write_csv(output_csv, rows)
    write_summary_md(
        output_md, rows, companies, run_label, sample_path, previous_baseline
    )

    total_pass = sum(1 for r in rows if r.case_result == "pass")
    total_fail = sum(1 for r in rows if r.case_result == "fail")
    total_skip = sum(1 for r in rows if r.case_result == "skipped")
    result = (
        "DRY_RUN_ONLY" if run_label == "dry-run"
        else ("LIVE_PASS" if total_fail == 0 else "LIVE_PARTIAL")
    )

    print(
        f"SUMMARY  mode={run_label}  companies={len(companies)}  cases={len(rows)}  "
        f"pass={total_pass}  fail={total_fail}  skipped={total_skip}  result={result}"
    )
    if run_label == "dry-run":
        per_company = len(MAIN_SOURCE_IDS) + 1
        print(
            f"progress: dry-run planned_cases={len(rows)} "
            f"(companies={len(companies)} x {per_company} sources, no CNINFO requests)",
            flush=True,
        )
    print(f"CSV   {output_csv}")
    print(f"MD    {output_md}")

    if run_label == "live" and total_fail > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
