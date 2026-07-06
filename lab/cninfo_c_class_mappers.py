"""
CNINFO C-class profile mappers (Era C Phase 4 draft).

Maps getCompanyIntroduction basicInformation/listingInformation to
c_company_basic_profile logical records.

No network, no database, no verified.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Optional

DEFAULT_BASIC_SOURCE_ID = "cninfo_company_basic_profile"
DEFAULT_SOURCE_STATUS = "testing"


def compute_raw_record_hash(raw_record: Dict[str, Any]) -> str:
    payload = json.dumps(raw_record, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_profile_id(source_id: str, company_code: str) -> str:
    key = f"{source_id}|{company_code}"
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
