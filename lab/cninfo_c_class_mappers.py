"""
CNINFO C-class profile mappers (Era C Phase 4 draft).

Maps getCompanyIntroduction basicInformation/listingInformation to
c_company_basic_profile logical records.

Maps marketOverview root object to c_company_security_profile logical records.

Maps getCompanyExecutives single row to c_executive_profile logical records.

Maps getStockStructure single row to c_share_capital_profile logical records.

No network, no database, no verified.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Optional

DEFAULT_BASIC_SOURCE_ID = "cninfo_company_basic_profile"
DEFAULT_SECURITY_SOURCE_ID = "cninfo_company_security_profile"
DEFAULT_EXECUTIVE_SOURCE_ID = "cninfo_executive_profile"
DEFAULT_SHARE_CAPITAL_SOURCE_ID = "cninfo_share_capital_profile"
DEFAULT_SOURCE_STATUS = "testing"


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

    # Fields without schema slots remain in raw_record_json only:
    # F015V main_business, F017V company_introduction, F010D establishment_date,
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


def count_mapped_standard_fields(record: Dict[str, Any]) -> int:
    """Count non-lineage schema fields with values."""
    skip = {
        "profile_id", "source_id", "company_code", "company_name",
        "raw_record_json", "raw_record_hash", "source_status",
        "field_confidence", "created_at", "org_id",
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
