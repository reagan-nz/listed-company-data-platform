"""
CNINFO D-class minimal transform mappers (Era C Phase 3 draft).

Maps Phase 2 raw CNINFO record fixtures to logical table records.
No network, no database. Preserves raw_record_json lineage fields.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List, Optional

SOURCE_STATUS = "testing_stable_sample"
DEFAULT_FETCH_TIME = "2026-07-05T08:00:00+00:00"


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def compute_raw_record_hash(source_id: str, query_mode: str, raw_record: Dict[str, Any]) -> str:
    payload = f"{source_id}|{query_mode}|{_canonical_json(raw_record)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_logical_id(*parts: Any) -> str:
    key = "|".join(str(p) for p in parts)
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


def _lineage_fields(
    source_id: str,
    raw_record: Dict[str, Any],
    query_params: Dict[str, Any],
    fetch_time: str,
    field_confidence: str = "high",
    *,
    query_mode: Optional[str] = None,
    include_query_mode: bool = False,
) -> Dict[str, Any]:
    hash_mode = query_mode or ""
    fields: Dict[str, Any] = {
        "source_id": source_id,
        "query_params": query_params,
        "fetch_time": fetch_time,
        "source_status": SOURCE_STATUS,
        "field_confidence": field_confidence,
        "raw_record_json": raw_record,
        "raw_record_hash": compute_raw_record_hash(source_id, hash_mode, raw_record),
    }
    if include_query_mode and query_mode is not None:
        fields["query_mode"] = query_mode
    return fields


def map_to_disclosure_schedule(
    raw_record: Dict[str, Any],
    *,
    source_id: str = "disclosure_schedule",
    query_mode: str = "section_time_paged",
    query_params: Optional[Dict[str, Any]] = None,
    fetch_time: str = DEFAULT_FETCH_TIME,
    field_confidence: str = "high",
) -> Dict[str, Any]:
    query_params = query_params or {}
    company_code = str(raw_record.get("seccode", ""))
    record = {
        "schedule_id": make_logical_id(source_id, query_mode, company_code, raw_record.get("f001d_0102")),
        "company_code": company_code,
        "company_name": raw_record.get("secname"),
        "org_id": raw_record.get("orgId"),
        "report_period": normalize_date(raw_record.get("f001d_0102")),
        "first_scheduled_date": normalize_date(raw_record.get("f002d_0102")),
        "first_changed_date": normalize_date(raw_record.get("f003d_0102")),
        "second_changed_date": normalize_date(raw_record.get("f004d_0102")),
        "third_changed_date": normalize_date(raw_record.get("f005d_0102")),
        "actual_disclosure_date": normalize_date(raw_record.get("f006d_0102")),
        **_lineage_fields(source_id, raw_record, query_params, fetch_time, field_confidence, query_mode=query_mode),
    }
    latest = raw_record.get("latest_time")
    if latest:
        record["latest_time_candidate"] = str(latest)
    return {k: v for k, v in record.items() if v is not None}


def map_to_company_event(
    raw_record: Dict[str, Any],
    *,
    source_id: str,
    query_mode: str,
    query_params: Optional[Dict[str, Any]] = None,
    fetch_time: str = DEFAULT_FETCH_TIME,
    field_confidence: str = "high",
) -> Dict[str, Any]:
    query_params = query_params or {}
    mappers = {
        "restricted_shares_unlock": _map_restricted_shares_unlock,
        "block_trade": _map_block_trade,
        "abnormal_trading": _map_abnormal_trading,
        "equity_pledge": _map_equity_pledge,
        "shareholder_change": _map_shareholder_change,
        "executive_shareholding": _map_executive_shareholding,
    }
    fn = mappers.get(source_id)
    if fn is None:
        raise ValueError(f"No company_event mapper for source_id={source_id}")
    return fn(raw_record, source_id, query_mode, query_params, fetch_time, field_confidence)


def _map_restricted_shares_unlock(
    raw: Dict[str, Any], source_id: str, query_mode: str, query_params: Dict[str, Any],
    fetch_time: str, field_confidence: str,
) -> Dict[str, Any]:
    company_code = str(raw.get("SECCODE", ""))
    event_date = normalize_date(raw.get("F003D"))
    return {
        "event_id": make_logical_id(source_id, query_mode, company_code, event_date),
        "company_code": company_code,
        "company_name": raw.get("SECNAME"),
        "event_date": event_date,
        "announcement_date": normalize_date(raw.get("DECLAREDATE")),
        "event_type": "restricted_shares_unlock",
        "primary_amount": raw.get("F004N"),
        "primary_amount_unit": "shares",
        "primary_ratio": raw.get("F005N"),
        "primary_ratio_unit": "percent",
        **_lineage_fields(source_id, raw, query_params, fetch_time, field_confidence, query_mode=query_mode, include_query_mode=True),
    }


def _map_block_trade(
    raw: Dict[str, Any], source_id: str, query_mode: str, query_params: Dict[str, Any],
    fetch_time: str, field_confidence: str,
) -> Dict[str, Any]:
    company_code = str(raw.get("SECCODE", ""))
    event_date = normalize_date(raw.get("TRADEDATE"))
    return {
        "event_id": make_logical_id(source_id, query_mode, company_code, event_date),
        "company_code": company_code,
        "company_name": raw.get("SECNAME"),
        "event_date": event_date,
        "event_type": "block_trade",
        "event_subtype": "block_trade_statistics",
        "primary_amount": raw.get("F002N"),
        "primary_amount_unit": "10k_shares",
        "primary_price": raw.get("F004N"),
        "primary_price_unit": "yuan_per_share",
        **_lineage_fields(source_id, raw, query_params, fetch_time, field_confidence, query_mode=query_mode, include_query_mode=True),
    }


def _map_abnormal_trading(
    raw: Dict[str, Any], source_id: str, query_mode: str, query_params: Dict[str, Any],
    fetch_time: str, field_confidence: str,
) -> Dict[str, Any]:
    company_code = str(raw.get("secCode", ""))
    event_date = normalize_date(raw.get("tradeTime"))
    return {
        "event_id": make_logical_id(source_id, query_mode, company_code, event_date, raw.get("type")),
        "company_code": company_code,
        "company_name": raw.get("secName"),
        "event_date": event_date,
        "event_type": "abnormal_trading",
        "event_subtype": str(raw.get("type", "")),
        **_lineage_fields(source_id, raw, query_params, fetch_time, "medium", query_mode=query_mode, include_query_mode=True),
    }


def _map_equity_pledge(
    raw: Dict[str, Any], source_id: str, query_mode: str, query_params: Dict[str, Any],
    fetch_time: str, field_confidence: str,
) -> Dict[str, Any]:
    company_code = str(raw.get("SECCODE", ""))
    announcement_date = normalize_date(raw.get("DECLAREDATE"))
    return {
        "event_id": make_logical_id(source_id, query_mode, company_code, announcement_date, raw.get("F001V")),
        "company_code": company_code,
        "company_name": raw.get("SECNAME"),
        "announcement_date": announcement_date,
        "event_type": "equity_pledge",
        "actor_name": raw.get("F001V"),
        "counterparty_name": raw.get("F003V"),
        "primary_amount": raw.get("F006N"),
        "primary_amount_unit": "10k_shares",
        "primary_ratio": raw.get("F007N"),
        "primary_ratio_unit": "percent",
        **_lineage_fields(source_id, raw, query_params, fetch_time, field_confidence, query_mode=query_mode, include_query_mode=True),
    }


def _map_shareholder_change(
    raw: Dict[str, Any], source_id: str, query_mode: str, query_params: Dict[str, Any],
    fetch_time: str, field_confidence: str,
) -> Dict[str, Any]:
    company_code = str(raw.get("SECCODE", ""))
    event_date = normalize_date(raw.get("VARYDATE"))
    change_type = str(query_params.get("type", ""))
    subtype = "increase" if change_type == "inc" else "decrease"
    record: Dict[str, Any] = {
        "event_id": make_logical_id(source_id, query_mode, company_code, event_date, raw.get("F002V")),
        "company_code": company_code,
        "company_name": raw.get("SECNAME"),
        "announcement_date": normalize_date(raw.get("DECLAREDATE")),
        "event_date": event_date,
        "event_type": "shareholder_change",
        "event_subtype": subtype,
        "actor_name": raw.get("F002V"),
        "primary_amount": raw.get("F004N"),
        "primary_amount_unit": "shares",
        "primary_ratio": raw.get("F005N"),
        "primary_ratio_unit": "percent",
        **_lineage_fields(source_id, raw, query_params, fetch_time, field_confidence, query_mode=query_mode, include_query_mode=True),
    }
    price = raw.get("F007V")
    if price is not None:
        record["primary_price"] = price
        record["primary_price_unit"] = "yuan_per_share"
    return record


def _map_executive_shareholding(
    raw: Dict[str, Any], source_id: str, query_mode: str, query_params: Dict[str, Any],
    fetch_time: str, field_confidence: str,
) -> Dict[str, Any]:
    company_code = str(raw.get("SECCODE", ""))
    event_date = normalize_date(raw.get("ENDDATE"))
    return {
        "event_id": make_logical_id(source_id, query_mode, company_code, event_date, raw.get("HUMANNAME")),
        "company_code": company_code,
        "company_name": raw.get("SECNAME"),
        "event_date": event_date,
        "event_type": "executive_shareholding",
        "event_subtype": f"varyType_{query_params.get('varyType', 'b')}",
        "actor_name": raw.get("HUMANNAME"),
        "primary_amount": raw.get("F006N"),
        "primary_amount_unit": "shares",
        "primary_price": raw.get("F008N"),
        "primary_price_unit": "yuan_per_share",
        **_lineage_fields(source_id, raw, query_params, fetch_time, field_confidence, query_mode=query_mode, include_query_mode=True),
    }


MARGIN_METRIC_MAP = [
    ("F001N", "financing_balance_yuan", "yuan"),
    ("F002N", "financing_buy_amount_yuan", "yuan"),
    ("F004N", "securities_lending_balance_shares", "shares"),
    ("F006N", "securities_lending_sell_volume_shares", "shares"),
    ("F009N", "margin_trading_balance_yuan", "yuan"),
]

SHAREHOLDER_DATA_METRIC_MAP = [
    ("F001N", "current_shareholder_count", "count"),
    ("F002N", "previous_shareholder_count", "count"),
    ("F003N", "shareholder_count_change_percent", "percent"),
    ("F004N", "current_avg_shares_per_holder", "shares"),
    ("F005N", "previous_avg_shares_per_holder", "shares"),
    ("F006N", "avg_shares_per_holder_change_percent", "percent"),
]

FUND_INDUSTRY_METRIC_MAP = [
    ("F003N", "fund_coverage_count", "count"),
    ("F004N", "industry_scale_100m_yuan", "100m_yuan"),
    ("F005N", "net_asset_ratio_percent", "percent"),
]


def map_to_company_metric_daily(
    raw_record: Dict[str, Any],
    *,
    source_id: str = "margin_trading",
    query_mode: str = "detailList_default",
    query_params: Optional[Dict[str, Any]] = None,
    fetch_time: str = DEFAULT_FETCH_TIME,
    field_confidence: str = "medium",
    validate_all_metrics: bool = True,
) -> List[Dict[str, Any]]:
    """One raw margin_trading row → up to 5 metric rows (confirmed fields only)."""
    query_params = query_params or {}
    company_code = str(raw_record.get("SECCODE", ""))
    trade_date = normalize_date(raw_record.get("TRADEDATE"))
    lineage = _lineage_fields(source_id, raw_record, query_params, fetch_time, field_confidence, query_mode=query_mode)
    metrics = MARGIN_METRIC_MAP if validate_all_metrics else MARGIN_METRIC_MAP[:1]
    rows: List[Dict[str, Any]] = []
    for raw_field, metric_name, unit in metrics:
        value = raw_record.get(raw_field)
        if value is None:
            continue
        rows.append({
            "metric_id": make_logical_id(source_id, query_mode, company_code, trade_date, metric_name),
            "company_code": company_code,
            "company_name": raw_record.get("SECNAME"),
            "trade_date": trade_date,
            "metric_name": metric_name,
            "metric_value": float(value),
            "unit": unit,
            "raw_field": raw_field,
            **lineage,
        })
    return rows


def map_to_company_metric_periodic(
    raw_record: Dict[str, Any],
    *,
    source_id: str = "shareholder_data",
    query_mode: str = "rdate_report_period",
    query_params: Optional[Dict[str, Any]] = None,
    fetch_time: str = DEFAULT_FETCH_TIME,
    field_confidence: str = "high",
) -> List[Dict[str, Any]]:
    query_params = query_params or {}
    company_code = str(raw_record.get("SECCODE", ""))
    report_period = normalize_date(raw_record.get("ENDDATE"))
    lineage = _lineage_fields(source_id, raw_record, query_params, fetch_time, field_confidence, query_mode=query_mode)
    rows: List[Dict[str, Any]] = []
    for raw_field, metric_name, unit in SHAREHOLDER_DATA_METRIC_MAP:
        value = raw_record.get(raw_field)
        if value is None:
            continue
        rows.append({
            "metric_id": make_logical_id(source_id, query_mode, company_code, report_period, metric_name),
            "company_code": company_code,
            "company_name": raw_record.get("SECNAME"),
            "report_period": report_period,
            "metric_name": metric_name,
            "metric_value": float(value),
            "unit": unit,
            "raw_field": raw_field,
            **lineage,
        })
    return rows


def map_to_industry_aggregate(
    raw_record: Dict[str, Any],
    *,
    source_id: str = "fund_industry_allocation",
    query_mode: str = "default",
    query_params: Optional[Dict[str, Any]] = None,
    fetch_time: str = DEFAULT_FETCH_TIME,
    field_confidence: str = "high",
) -> List[Dict[str, Any]]:
    query_params = query_params or {}
    industry_code = str(raw_record.get("F001V", ""))
    report_period = normalize_date(raw_record.get("ENDDATE"))
    lineage = _lineage_fields(source_id, raw_record, query_params, fetch_time, field_confidence, query_mode=query_mode)
    rows: List[Dict[str, Any]] = []
    for raw_field, metric_name, unit in FUND_INDUSTRY_METRIC_MAP:
        value = raw_record.get(raw_field)
        if value is None:
            continue
        rows.append({
            "aggregate_id": make_logical_id(source_id, query_mode, industry_code, report_period, metric_name),
            "industry_code": industry_code,
            "industry_name": raw_record.get("F002V"),
            "report_period": report_period,
            "metric_name": metric_name,
            "metric_value": float(value),
            "unit": unit,
            "raw_field": raw_field,
            **lineage,
        })
    return rows


def map_to_raw_record_snapshot(
    fixture: Dict[str, Any],
    *,
    fetch_time: str = DEFAULT_FETCH_TIME,
    fetch_status: str = "success",
    http_status: int = 200,
) -> Dict[str, Any]:
    source_id = fixture["source_id"]
    query_mode = fixture.get("query_mode", "default")
    raw_record = fixture["raw_record"]
    query_params = fixture.get("query_params", {})
    return {
        "snapshot_id": make_logical_id("snapshot", source_id, query_mode, compute_raw_record_hash(source_id, query_mode, raw_record)),
        "source_id": source_id,
        "query_mode": query_mode,
        "query_params": query_params,
        "request_url": fixture.get("request_url", ""),
        "records_path": fixture.get("records_path", ""),
        "raw_record_json": raw_record,
        "raw_record_hash": compute_raw_record_hash(source_id, query_mode, raw_record),
        "fetch_time": fetch_time,
        "fetch_status": fetch_status,
        "http_status": http_status,
        "source_status": SOURCE_STATUS,
        "field_confidence": "high",
        "schema_version": "draft-0.1",
        "notes": "Offline fixture snapshot from Phase 2 documented sample",
    }
