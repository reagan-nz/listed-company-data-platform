"""
CNINFO C-class profile mappers (Era C Phase 4 draft).

Maps getCompanyIntroduction basicInformation/listingInformation to
c_company_basic_profile logical records.

Maps marketOverview root object to c_company_security_profile logical records.

Maps getCompanyExecutives single row to c_executive_profile logical records.

Maps getStockStructure single row to c_share_capital_profile logical records.

Maps getTopTenStockholders / getTopTenCirculatingStockholders single row to
c_shareholder_profile logical records.

Maps getCompanyHisDividend data.records row(s) to dividend_history logical records.

No network, no database, no verified.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List, Optional

DEFAULT_BASIC_SOURCE_ID = "cninfo_company_basic_profile"
DEFAULT_SECURITY_SOURCE_ID = "cninfo_company_security_profile"
DEFAULT_EXECUTIVE_SOURCE_ID = "cninfo_executive_profile"
DEFAULT_SHARE_CAPITAL_SOURCE_ID = "cninfo_share_capital_profile"
DEFAULT_TOP_SHAREHOLDERS_SOURCE_ID = "cninfo_top_shareholders_profile"
DEFAULT_TOP_FLOAT_SHAREHOLDERS_SOURCE_ID = "cninfo_top_float_shareholders_profile"
DEFAULT_DIVIDEND_SOURCE_ID = "cninfo_dividend_financing_profile"
LOGICAL_DIVIDEND_SOURCE_ID = "dividend_history"
DEFAULT_SOURCE_STATUS = "testing"

# F007V 分红方案文本解析（dividend_history v1）
# 顺序：更具体模式优先；含税/税前/税后括号文本不影响金额捕获
_CASH_DIVIDEND_PATTERNS = [
    re.compile(r"每10股派发现金红利(\d+(?:\.\d+)?)元"),
    re.compile(r"每10股派(\d+(?:\.\d+)?)元"),
    re.compile(r"10股派(\d+(?:\.\d+)?)元"),
    re.compile(r"10派(\d+(?:\.\d+)?)元"),
    re.compile(r"派发现金红利(\d+(?:\.\d+)?)元"),
]
_STOCK_DIVIDEND_PATTERNS = [
    re.compile(r"10送(\d+(?:\.\d+)?)股"),
    re.compile(r"送(\d+(?:\.\d+)?)股"),
]
_TRANSFER_DIVIDEND_PATTERNS = [
    re.compile(r"10转增(\d+(?:\.\d+)?)股"),
    re.compile(r"10转(\d+(?:\.\d+)?)股"),
    re.compile(r"转增(\d+(?:\.\d+)?)股"),
]
_YEAR_PATTERN = re.compile(r"(\d{4})")

SHAREHOLDER_SCOPE_TOP = "top_shareholder"
SHAREHOLDER_SCOPE_TOP_FLOAT = "top_float_shareholder"


def compute_raw_record_hash(raw_record: Dict[str, Any]) -> str:
    payload = json.dumps(raw_record, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_profile_id(source_id: str, company_code: str) -> str:
    key = f"{source_id}|{company_code}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


def make_security_profile_id(source_id: str, company_code: str) -> str:
    return make_profile_id(source_id, company_code)


def _num_or_none(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def make_executive_profile_id(
    source_id: str,
    company_code: str,
    row_key: str,
) -> str:
    key = f"{source_id}|{company_code}|{row_key}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


def make_share_capital_profile_id(
    source_id: str,
    company_code: str,
    row_key: str,
) -> str:
    key = f"{source_id}|{company_code}|{row_key}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


def make_shareholder_profile_id(
    source_id: str,
    company_code: str,
    row_key: str,
) -> str:
    key = f"{source_id}|{company_code}|{row_key}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _map_establishment_date(raw_value: Any) -> Dict[str, Any]:
    """
    将 basic F010D 映射为 establishment_date。

    - 正常 ISO/YYYYMMDD 日期 -> parsed
    - null/空 -> null_but_valid
    - 非标准文本 -> 保留原值 + needs_review（不导致整家公司 mapper 失败）
    """
    if raw_value is None:
        return {
            "establishment_date": None,
            "establishment_date_parse_status": "null_but_valid",
        }
    if isinstance(raw_value, str) and not raw_value.strip():
        return {
            "establishment_date": None,
            "establishment_date_parse_status": "null_but_valid",
        }
    s = str(raw_value).strip()
    normalized = normalize_date(raw_value)
    if normalized and _ISO_DATE_RE.fullmatch(normalized):
        return {
            "establishment_date": normalized,
            "establishment_date_parse_status": "parsed",
        }
    return {
        "establishment_date": s,
        "establishment_date_parse_status": "needs_review",
        "establishment_date_field_quality": "nonstandard_date",
    }


def normalize_date(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    s = str(value).strip()
    if not s:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return s
    if re.fullmatch(r"\d{8}", s):
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return s


def _str_or_none(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _exchange_from_market(market: Optional[str]) -> Optional[str]:
    if not market:
        return None
    m = market.strip()
    if "深圳" in m or "创业板" in m:
        return "SZSE"
    if "上海" in m or "科创板" in m or "主板" in m:
        return "SSE"
    if "北京" in m or "北交所" in m:
        return "BSE"
    return None


def _exchange_from_company_code(company_code: str) -> Optional[str]:
    code = company_code.strip()
    if not code:
        return None
    if code.startswith(("600", "601", "603", "605", "688", "689")):
        return "SSE"
    if code.startswith(("000", "001", "002", "003", "300", "301")):
        return "SZSE"
    if code.startswith(("430", "831", "832", "833", "834", "835", "836", "837", "838", "839")):
        return "BSE"
    return None


def _bool_or_none(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        s = value.strip().lower()
        if s in {"true", "1", "yes"}:
            return True
        if s in {"false", "0", "no"}:
            return False
    return None


def _registered_capital_from_basic(basic: Dict[str, Any]) -> Optional[str]:
    val = basic.get("F007N")
    if val is None or val == "":
        return None
    return str(val)


def _has_non_empty_section(section: Any) -> bool:
    return isinstance(section, list) and len(section) > 0


def map_company_basic_profile(
    raw_record: Dict[str, Any],
    company_code: str,
    company_name: str,
    source_id: str = DEFAULT_BASIC_SOURCE_ID,
    source_status: str = DEFAULT_SOURCE_STATUS,
    org_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Map getCompanyIntroduction slice to c_company_basic_profile.

    raw_record shape:
        {"basicInformation": [...], "listingInformation": [...]}

    Returns None when both sections are empty (empty_but_valid upstream).
    """
    basic_list = raw_record.get("basicInformation") or []
    listing_list = raw_record.get("listingInformation") or []

    if not _has_non_empty_section(basic_list) and not _has_non_empty_section(listing_list):
        return None

    basic: Dict[str, Any] = basic_list[0] if _has_non_empty_section(basic_list) else {}
    listing: Dict[str, Any] = listing_list[0] if _has_non_empty_section(listing_list) else {}

    mapped_code = _str_or_none(basic.get("ASECCODE")) or company_code
    mapped_name = _str_or_none(basic.get("ASECNAME")) or company_name
    market = _str_or_none(basic.get("MARKET"))

    record: Dict[str, Any] = {
        "profile_id": make_profile_id(source_id, mapped_code),
        "source_id": source_id,
        "company_code": mapped_code,
        "company_name": mapped_name,
        "raw_record_json": raw_record,
        "raw_record_hash": compute_raw_record_hash(raw_record),
        "source_status": source_status,
        "field_confidence": "medium",
    }

    if org_id:
        record["org_id"] = org_id

    optional_fields = {
        "legal_name": _str_or_none(basic.get("ORGNAME")),
        "english_name": _str_or_none(basic.get("F001V")),
        "legal_representative": _str_or_none(basic.get("F003V")),
        "registered_address": _str_or_none(basic.get("F004V")),
        "office_address": _str_or_none(basic.get("F005V")),
        "listing_date": normalize_date(basic.get("F006D")),
        "company_website": _str_or_none(basic.get("F011V")),
        "business_scope": _str_or_none(basic.get("F016V")),
        "industry": _str_or_none(basic.get("F032V")),
        "listed_board": market,
        "exchange": _exchange_from_market(market),
        "registered_capital": _registered_capital_from_basic(basic),
    }

    for key, val in optional_fields.items():
        if val is not None:
            record[key] = val

    if basic_list:
        record.update(_map_establishment_date(basic.get("F010D")))

    # Fields without schema slots remain in raw_record_json only:
    # F015V main_business, F017V company_introduction,
    # F044V index_or_plate_labels, F012V-F014V contact, listing F047V etc.

    if listing and not basic.get("ASECCODE"):
        sec = _str_or_none(listing.get("SECCODE"))
        if sec:
            record["company_code"] = sec

    return record


def map_company_security_profile(
    raw_record: Dict[str, Any],
    company_code: str,
    company_name: str,
    source_id: str = DEFAULT_SECURITY_SOURCE_ID,
    source_status: str = DEFAULT_SOURCE_STATUS,
) -> Optional[Dict[str, Any]]:
    """
    Map marketOverview root object to c_company_security_profile.

    raw_record shape (root object):
        secCode, secName, secType, tradingStatus, age, finance,
        delisted, sshk, szhk

    Returns None when raw_record has no usable secCode and no other keys.
    """
    if not raw_record:
        return None

    mapped_code = _str_or_none(raw_record.get("secCode")) or company_code
    mapped_name = _str_or_none(raw_record.get("secName")) or company_name

    if not mapped_code and not raw_record:
        return None

    record: Dict[str, Any] = {
        "security_profile_id": make_security_profile_id(source_id, mapped_code),
        "source_id": source_id,
        "company_code": mapped_code,
        "company_name": mapped_name,
        "raw_record_json": raw_record,
        "raw_record_hash": compute_raw_record_hash(raw_record),
        "source_status": source_status,
        "field_confidence": "medium",
    }

    optional_fields: Dict[str, Any] = {
        "stock_short_name": _str_or_none(raw_record.get("secName")),
        "security_code": _str_or_none(raw_record.get("secCode")),
        "security_type_code": _str_or_none(raw_record.get("secType")),
        "trading_status_code": _str_or_none(raw_record.get("tradingStatus")),
        "listing_age_years_candidate": _str_or_none(raw_record.get("age")),
        "is_finance_related_candidate": _bool_or_none(raw_record.get("finance")),
        "is_delisted": _bool_or_none(raw_record.get("delisted")),
        "shanghai_hong_kong_connect_candidate": _bool_or_none(raw_record.get("sshk")),
        "shenzhen_hong_kong_connect_candidate": _bool_or_none(raw_record.get("szhk")),
        "exchange": _exchange_from_company_code(mapped_code),
    }

    for key, val in optional_fields.items():
        if val is not None:
            record[key] = val

    # Fields without schema slots or unconfirmed semantics remain in raw_record_json:
    # listed_board, listing_date, listing_status, is_st_candidate (YAML expected_fields).

    return record


def map_company_executive_profile(
    raw_record: Dict[str, Any],
    company_code: str,
    company_name: str,
    source_id: str = DEFAULT_EXECUTIVE_SOURCE_ID,
    source_status: str = DEFAULT_SOURCE_STATUS,
    org_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Map getCompanyExecutives single row to c_executive_profile.

    raw_record shape (one element of data.records):
        F002V, F009V, F010V, F012V, F017V, F005N, F012N, SEQID, F001V

    Returns None when person_name or position cannot be derived.
    """
    if not raw_record:
        return None

    person_name = _str_or_none(raw_record.get("F002V"))
    position = _str_or_none(raw_record.get("F009V"))

    if not person_name or not position:
        return None

    row_key = (
        _str_or_none(raw_record.get("F001V"))
        or _str_or_none(raw_record.get("SEQID"))
        or person_name
    )

    record: Dict[str, Any] = {
        "executive_profile_id": make_executive_profile_id(
            source_id, company_code, row_key or person_name
        ),
        "source_id": source_id,
        "company_code": company_code,
        "company_name": company_name,
        "person_name": person_name,
        "position": position,
        "raw_record_json": raw_record,
        "raw_record_hash": compute_raw_record_hash(raw_record),
        "source_status": source_status,
        "field_confidence": "medium",
    }

    if org_id:
        record["org_id"] = org_id

    optional_fields = {
        "gender_candidate": _str_or_none(raw_record.get("F010V")),
        "birth_year_candidate": _str_or_none(raw_record.get("F012V")),
        "education_candidate": _str_or_none(raw_record.get("F017V")),
    }

    for key, val in optional_fields.items():
        if val is not None:
            record[key] = val

    # Fields without schema slots remain in raw_record_json only:
    # F005N shareholding_quantity_candidate, F012N compensation_candidate,
    # SEQID row_sequence_id, F001V person_id_candidate.

    return record


def map_company_share_capital_profile(
    raw_record: Dict[str, Any],
    company_code: str,
    company_name: str,
    source_id: str = DEFAULT_SHARE_CAPITAL_SOURCE_ID,
    source_status: str = DEFAULT_SOURCE_STATUS,
    org_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Map getStockStructure single row to c_share_capital_profile.

    raw_record shape (one element of data.records):
        VARYDATE, F002V, F021N, F022N, F023N, F024N, F028N, F003N

    Returns None when raw_record is empty.
    """
    if not raw_record:
        return None

    vary_date = normalize_date(raw_record.get("VARYDATE"))
    change_reason = _str_or_none(raw_record.get("F002V"))
    row_key = f"{vary_date or 'unknown'}|{change_reason or 'unknown'}"

    record: Dict[str, Any] = {
        "share_capital_profile_id": make_share_capital_profile_id(
            source_id, company_code, row_key
        ),
        "source_id": source_id,
        "company_code": company_code,
        "company_name": company_name,
        "raw_record_json": raw_record,
        "raw_record_hash": compute_raw_record_hash(raw_record),
        "source_status": source_status,
        "field_confidence": "medium",
    }

    if org_id:
        record["org_id"] = org_id

    optional_fields: Dict[str, Any] = {
        "report_date": vary_date,
        "total_share_capital": _num_or_none(raw_record.get("F021N")),
        "float_share_capital": _num_or_none(raw_record.get("F022N")),
        "restricted_share_capital": _num_or_none(raw_record.get("F023N")),
    }

    for key, val in optional_fields.items():
        if val is not None:
            record[key] = val

    # Fields without schema slots remain in raw_record_json only:
    # F002V change_reason_or_source, F024N unrestricted_share_candidate,
    # F028N change_amount_candidate, F003N total_capital_candidate.

    return record


def map_company_shareholder_profile(
    raw_record: Dict[str, Any],
    company_code: str,
    company_name: str,
    source_id: str,
    source_status: str = DEFAULT_SOURCE_STATUS,
    shareholder_scope: str = SHAREHOLDER_SCOPE_TOP,
    org_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Map getTopTenStockholders / getTopTenCirculatingStockholders row to c_shareholder_profile.

    raw_record shape (one element of data.records):
        F001D, F002V, F003N, F004N, F005N, F006V, F007V

    shareholder_scope: top_shareholder | top_float_shareholder (schema enum).
    Returns None when raw_record is empty.
    """
    if not raw_record:
        return None

    report_period = normalize_date(raw_record.get("F001D"))
    shareholder_name = _str_or_none(raw_record.get("F002V"))
    rank = _int_or_none(raw_record.get("F005N"))
    row_key = (
        f"{report_period or 'unknown'}|{rank if rank is not None else 'unknown'}"
        f"|{shareholder_name or 'unknown'}"
    )

    record: Dict[str, Any] = {
        "shareholder_profile_id": make_shareholder_profile_id(
            source_id, company_code, row_key
        ),
        "source_id": source_id,
        "company_code": company_code,
        "company_name": company_name,
        "shareholder_scope": shareholder_scope,
        "raw_record_json": raw_record,
        "raw_record_hash": compute_raw_record_hash(raw_record),
        "source_status": source_status,
        "field_confidence": "medium",
    }

    if org_id:
        record["org_id"] = org_id

    optional_fields: Dict[str, Any] = {
        "report_period": report_period,
        "shareholder_name": shareholder_name,
        "holding_shares": _num_or_none(raw_record.get("F003N")),
        "holding_ratio": _num_or_none(raw_record.get("F004N")),
        "rank": rank,
        "shareholder_type_candidate": _str_or_none(raw_record.get("F006V")),
    }

    for key, val in optional_fields.items():
        if val is not None:
            record[key] = val

    # Fields without schema slots remain in raw_record_json only:
    # F007V change_status_or_change_amount_candidate.

    return record


def make_dividend_history_event_id(
    source_id: str,
    company_code: str,
    row_key: str,
) -> str:
    key = f"{source_id}|{company_code}|{row_key}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


def _parse_dividend_year(report_period: Optional[str]) -> Optional[int]:
    if not report_period:
        return None
    match = _YEAR_PATTERN.search(str(report_period))
    if not match:
        return None
    return int(match.group(1))


def _first_regex_match(patterns: List[re.Pattern], text: str) -> Optional[float]:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return float(match.group(1)) / 10.0
    return None


def parse_dividend_f007v(plan_text: Optional[str]) -> Dict[str, Any]:
    """
    解析 F007V 分红方案文本为 normalized_core 数值字段。

    返回 cash_dividend_per_share / stock_dividend_ratio / transfer_ratio /
    dividend_method / dividend_parse_status / dividend_plan_text_raw。
    """
    raw_text = _str_or_none(plan_text)
    result: Dict[str, Any] = {
        "cash_dividend_per_share": None,
        "stock_dividend_ratio": None,
        "transfer_ratio": None,
        "dividend_method": None,
        "dividend_plan_text_raw": raw_text,
        "dividend_parse_status": "needs_review",
    }
    if not raw_text:
        result["dividend_parse_status"] = "partial"
        return result

    cash = _first_regex_match(_CASH_DIVIDEND_PATTERNS, raw_text)
    stock = _first_regex_match(_STOCK_DIVIDEND_PATTERNS, raw_text)
    transfer = _first_regex_match(_TRANSFER_DIVIDEND_PATTERNS, raw_text)

    # 否定表述（如「不分配不转增」）不应触发送股/转增意图
    cash_flag = cash is not None or (
        "派" in raw_text and "元" in raw_text and "不分配" not in raw_text and "不派" not in raw_text
    )
    stock_flag = stock is not None or (
        "送" in raw_text and "股" in raw_text and "不送" not in raw_text
    )
    transfer_flag = transfer is not None or (
        ("转增" in raw_text or re.search(r"10转\d", raw_text) is not None)
        and "不转增" not in raw_text
    )

    flags = {
        "cash": cash_flag,
        "stock": stock_flag,
        "transfer": transfer_flag,
    }

    if cash is not None:
        result["cash_dividend_per_share"] = cash
    if stock is not None:
        result["stock_dividend_ratio"] = stock
    if transfer is not None:
        result["transfer_ratio"] = transfer

    active = sum(1 for k, v in flags.items() if v)
    if active == 0:
        result["dividend_method"] = "other"
        result["dividend_parse_status"] = "needs_review"
    elif active == 1:
        if flags["cash"]:
            result["dividend_method"] = "cash"
        elif flags["stock"]:
            result["dividend_method"] = "stock"
        else:
            result["dividend_method"] = "transfer"
        if (flags["cash"] and cash is None) or (flags["stock"] and stock is None) or (
            flags["transfer"] and transfer is None
        ):
            result["dividend_parse_status"] = "needs_review"
        else:
            result["dividend_parse_status"] = "parsed"
    else:
        result["dividend_method"] = "mixed"
        if cash is not None or stock is not None or transfer is not None:
            if (flags["cash"] and cash is None) or (flags["stock"] and stock is None) or (
                flags["transfer"] and transfer is None
            ):
                result["dividend_parse_status"] = "partial"
            else:
                result["dividend_parse_status"] = "parsed"
        else:
            result["dividend_parse_status"] = "needs_review"

    return result


def _extract_dividend_records(raw_input: Any) -> List[Dict[str, Any]]:
    """从 API 响应或 records 列表提取分红事件行。"""
    if raw_input is None:
        return []
    if isinstance(raw_input, list):
        return [r for r in raw_input if isinstance(r, dict)]
    if not isinstance(raw_input, dict):
        return []

    if "F001V" in raw_input or "F007V" in raw_input:
        return [raw_input]

    data = raw_input.get("data")
    if isinstance(data, dict) and isinstance(data.get("records"), list):
        return [r for r in data["records"] if isinstance(r, dict)]

    records = raw_input.get("records")
    if isinstance(records, list):
        return [r for r in records if isinstance(r, dict)]

    return []


def map_dividend_history_event(
    raw_record: Dict[str, Any],
    company_code: str,
    company_name: str = "",
    source_id: str = DEFAULT_DIVIDEND_SOURCE_ID,
    source_status: str = DEFAULT_SOURCE_STATUS,
) -> Dict[str, Any]:
    """单条 getCompanyHisDividend data.records 元素 → normalized 分红事件。"""
    report_period = _str_or_none(raw_record.get("F001V"))
    dividend_year = _parse_dividend_year(report_period)
    record_date = normalize_date(raw_record.get("F018D"))
    ex_dividend_date = normalize_date(raw_record.get("F020D"))
    payment_date = normalize_date(raw_record.get("F023D"))

    parsed = parse_dividend_f007v(raw_record.get("F007V"))
    row_key = f"{report_period or 'unknown'}|{record_date or 'unknown'}|{parsed.get('dividend_plan_text_raw') or 'unknown'}"

    event: Dict[str, Any] = {
        "dividend_history_event_id": make_dividend_history_event_id(
            source_id, company_code, row_key
        ),
        "logical_source_id": LOGICAL_DIVIDEND_SOURCE_ID,
        "source_id": source_id,
        "company_code": company_code,
        "report_period": report_period,
        "dividend_year": dividend_year,
        "record_date": record_date,
        "ex_dividend_date": ex_dividend_date,
        "payment_date": payment_date,
        "cash_dividend_per_share": parsed["cash_dividend_per_share"],
        "stock_dividend_ratio": parsed["stock_dividend_ratio"],
        "transfer_ratio": parsed["transfer_ratio"],
        "dividend_method": parsed["dividend_method"],
        "dividend_plan_text_raw": parsed["dividend_plan_text_raw"],
        "dividend_parse_status": parsed["dividend_parse_status"],
        "raw_record_json": raw_record,
        "raw_record_hash": compute_raw_record_hash(raw_record),
        "source_status": source_status,
        "field_confidence": "medium",
    }
    if company_name:
        event["company_name"] = company_name
    return event


def _aggregate_dividend_parse_status(statuses: List[str]) -> str:
    if not statuses:
        return "empty_but_valid"
    if all(s == "parsed" for s in statuses):
        return "parsed"
    if all(s == "needs_review" for s in statuses):
        return "needs_review"
    if any(s == "needs_review" for s in statuses):
        return "partial" if any(s == "parsed" for s in statuses) else "needs_review"
    if any(s == "partial" for s in statuses):
        return "partial"
    return "parsed"


def map_dividend_history(
    raw_input: Any,
    company_code: str,
    company_name: str = "",
    source_id: str = DEFAULT_DIVIDEND_SOURCE_ID,
    source_status: str = DEFAULT_SOURCE_STATUS,
) -> Dict[str, Any]:
    """
    将 getCompanyHisDividend 响应或 records 列表映射为公司级 dividend_history 对象。

    输入可为：单条 record dict · records list · 含 data.records 的 API 响应 dict。
    """
    records = _extract_dividend_records(raw_input)
    events = [
        map_dividend_history_event(
            raw_record=r,
            company_code=company_code,
            company_name=company_name,
            source_id=source_id,
            source_status=source_status,
        )
        for r in records
    ]

    report_periods = [e.get("report_period") for e in events if e.get("report_period")]
    top_report_period = report_periods[0] if len(report_periods) == 1 else None
    parse_statuses = [e.get("dividend_parse_status", "needs_review") for e in events]
    company_parse_status = _aggregate_dividend_parse_status(parse_statuses)

    # 对外暴露的精简事件列表（normalized_core）
    public_events: List[Dict[str, Any]] = []
    for e in events:
        public_events.append({
            "dividend_year": e.get("dividend_year"),
            "report_period": e.get("report_period"),
            "record_date": e.get("record_date"),
            "ex_dividend_date": e.get("ex_dividend_date"),
            "payment_date": e.get("payment_date"),
            "cash_dividend_per_share": e.get("cash_dividend_per_share"),
            "stock_dividend_ratio": e.get("stock_dividend_ratio"),
            "transfer_ratio": e.get("transfer_ratio"),
            "dividend_method": e.get("dividend_method"),
            "dividend_plan_text_raw": e.get("dividend_plan_text_raw"),
            "dividend_parse_status": e.get("dividend_parse_status"),
        })

    return {
        "company_code": company_code,
        "company_name": company_name or None,
        "report_period": top_report_period,
        "dividend_history": public_events,
        "dividend_parse_status": company_parse_status,
        "record_count": len(events),
        "source_evidence": {
            "source_id": source_id,
            "logical_source_id": LOGICAL_DIVIDEND_SOURCE_ID,
        },
        "events_full": events,
    }


def count_mapped_standard_fields(record: Dict[str, Any]) -> int:
    """Count non-lineage schema fields with values."""
    skip = {
        "profile_id", "source_id", "company_code", "company_name",
        "raw_record_json", "raw_record_hash", "source_status",
        "field_confidence", "created_at", "org_id",
        "establishment_date_parse_status", "establishment_date_field_quality",
    }
    return sum(
        1 for k, v in record.items()
        if k not in skip and v is not None and v != ""
    )


def count_mapped_security_profile_fields(record: Dict[str, Any]) -> int:
    """Count non-lineage schema fields with values for security_profile."""
    skip = {
        "security_profile_id", "source_id", "company_code", "company_name",
        "raw_record_json", "raw_record_hash", "source_status",
        "field_confidence", "created_at",
    }
    return sum(
        1 for k, v in record.items()
        if k not in skip and v is not None and v != ""
    )


def count_mapped_executive_profile_fields(record: Dict[str, Any]) -> int:
    """Count non-lineage schema fields with values for executive_profile."""
    skip = {
        "executive_profile_id", "source_id", "company_code", "company_name",
        "person_name", "position",
        "raw_record_json", "raw_record_hash", "source_status",
        "field_confidence", "created_at", "org_id",
    }
    return sum(
        1 for k, v in record.items()
        if k not in skip and v is not None and v != ""
    )


def count_mapped_share_capital_profile_fields(record: Dict[str, Any]) -> int:
    """Count non-lineage schema fields with values for share_capital_profile."""
    skip = {
        "share_capital_profile_id", "source_id", "company_code", "company_name",
        "raw_record_json", "raw_record_hash", "source_status",
        "field_confidence", "created_at", "org_id",
    }
    return sum(
        1 for k, v in record.items()
        if k not in skip and v is not None and v != ""
    )


def count_mapped_shareholder_profile_fields(record: Dict[str, Any]) -> int:
    """Count non-lineage schema fields with values for shareholder_profile."""
    skip = {
        "shareholder_profile_id", "source_id", "company_code", "company_name",
        "shareholder_scope",
        "raw_record_json", "raw_record_hash", "source_status",
        "field_confidence", "created_at", "org_id",
    }
    return sum(
        1 for k, v in record.items()
        if k not in skip and v is not None and v != ""
    )
