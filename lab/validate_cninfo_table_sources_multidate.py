"""
CNINFO D 类 priority-1 多日期小样本稳定性复测（Era C Phase 2.3）。

对每个 testing source 在 2–3 个日期/报告期下各请求一次，检查 endpoint、records path、字段集合是否稳定。
不翻页、不全量抓取、不入库、不写 verified。

用法：
    python lab/validate_cninfo_table_sources_multidate.py
    python lab/validate_cninfo_table_sources_multidate.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlencode

import requests
import yaml

from validate_cninfo_table_sources import (
    AJAX_HEADERS,
    BASE_DIR,
    DEFAULT_CONFIG,
    _detect_blocked,
    _dimension_flags_from_record_keys,
    _extract_records,
    _field_hints_available,
    _flatten_keys,
    _infer_response_type,
    _observed_meta_from_payload,
    load_config,
)

DEFAULT_OUT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_table_sources_multidate_stability.csv"
)
DEFAULT_OUT_SUMMARY = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_table_sources_multidate_stability_summary.md"
)

SLEEP_SECONDS = 0.6
REQUEST_TIMEOUT = 10

PRIORITY1_IDS = (
    "disclosure_schedule",
    "restricted_shares_unlock",
    "block_trade",
    "margin_trading",
    "abnormal_trading",
)

CSV_FIELDS = [
    "source_id",
    "source_name",
    "test_case_id",
    "request_url",
    "method",
    "params",
    "http_status",
    "response_ok",
    "records_path",
    "sample_rows",
    "observed_total_rows",
    "observed_total_pages",
    "field_count",
    "key_fields",
    "company_code_available",
    "date_available",
    "amount_available",
    "nested_detail_available",
    "requires_login",
    "requires_captcha",
    "requires_paid_permission",
    "schema_matches_expected",
    "field_set_changed",
    "empty_but_valid_response",
    "validation_status",
    "recommended_status_after_stability",
    "notes",
]

# Predefined test cases (no pagination, single request each)
TEST_CASES: List[Dict[str, Any]] = [
    # disclosure_schedule
    {
        "source_id": "disclosure_schedule",
        "test_case_id": "ds_section_2025_12_31",
        "params": {
            "sectionTime": "2025-12-31",
            "firstTime": "",
            "lastTime": "",
            "market": "szsh",
            "stockCode": "",
            "orderClos": "",
            "isDesc": "",
            "pagesize": 20,
            "pagenum": 1,
        },
        "params_location": "form",
        "is_auxiliary": False,
    },
    {
        "source_id": "disclosure_schedule",
        "test_case_id": "ds_section_2026_06_30",
        "params": {
            "sectionTime": "2026-06-30",
            "firstTime": "",
            "lastTime": "",
            "market": "szsh",
            "stockCode": "",
            "orderClos": "",
            "isDesc": "",
            "pagesize": 20,
            "pagenum": 1,
        },
        "params_location": "form",
        "is_auxiliary": False,
    },
    # restricted_shares_unlock
    {
        "source_id": "restricted_shares_unlock",
        "test_case_id": "rsu_tdate_2026_06_08",
        "params": {"tdate": "2026-06-08"},
        "params_location": "query",
        "is_auxiliary": False,
    },
    {
        "source_id": "restricted_shares_unlock",
        "test_case_id": "rsu_tdate_2026_07_06",
        "params": {"tdate": "2026-07-06"},
        "params_location": "query",
        "is_auxiliary": False,
    },
    {
        "source_id": "restricted_shares_unlock",
        "test_case_id": "rsu_tdate_2026_07_03",
        "params": {"tdate": "2026-07-03"},
        "params_location": "query",
        "is_auxiliary": False,
    },
    # block_trade
    {
        "source_id": "block_trade",
        "test_case_id": "bt_tdate_2026_07_03",
        "params": {"tdate": "2026-07-03"},
        "params_location": "query",
        "is_auxiliary": False,
    },
    {
        "source_id": "block_trade",
        "test_case_id": "bt_tdate_2026_07_02",
        "params": {"tdate": "2026-07-02"},
        "params_location": "query",
        "is_auxiliary": False,
    },
    {
        "source_id": "block_trade",
        "test_case_id": "bt_tdate_2026_07_01",
        "params": {"tdate": "2026-07-01"},
        "params_location": "query",
        "is_auxiliary": False,
    },
    # margin_trading detailList (no explicit date)
    {
        "source_id": "margin_trading",
        "test_case_id": "mt_detail_default_1",
        "api_url_override": None,
        "params": {},
        "params_location": "none",
        "method": "POST",
        "is_auxiliary": False,
    },
    {
        "source_id": "margin_trading",
        "test_case_id": "mt_detail_default_2",
        "api_url_override": None,
        "params": {},
        "params_location": "none",
        "method": "POST",
        "is_auxiliary": False,
    },
    # margin_trading market summary (auxiliary)
    {
        "source_id": "margin_trading",
        "test_case_id": "mt_market_2026_07_02",
        "api_url_override": "https://www.cninfo.com.cn/data20/marginTrading/market",
        "params": {"tdate": "2026-07-02"},
        "params_location": "query",
        "method": "GET",
        "is_auxiliary": True,
    },
    {
        "source_id": "margin_trading",
        "test_case_id": "mt_market_2026_07_01",
        "api_url_override": "https://www.cninfo.com.cn/data20/marginTrading/market",
        "params": {"tdate": "2026-07-01"},
        "params_location": "query",
        "method": "GET",
        "is_auxiliary": True,
    },
    # abnormal_trading
    {
        "source_id": "abnormal_trading",
        "test_case_id": "at_2026_07_03",
        "params": {
            "sdate": "2026-07-03",
            "edate": "2026-07-03",
            "platecode": "",
            "orderby": "",
            "page": 1,
            "rows": 30,
        },
        "params_location": "query",
        "is_auxiliary": False,
    },
    {
        "source_id": "abnormal_trading",
        "test_case_id": "at_2026_07_02",
        "params": {
            "sdate": "2026-07-02",
            "edate": "2026-07-02",
            "platecode": "",
            "orderby": "",
            "page": 1,
            "rows": 30,
        },
        "params_location": "query",
        "is_auxiliary": False,
    },
    {
        "source_id": "abnormal_trading",
        "test_case_id": "at_2026_07_01",
        "params": {
            "sdate": "2026-07-01",
            "edate": "2026-07-01",
            "platecode": "",
            "orderby": "",
            "page": 1,
            "rows": 30,
        },
        "params_location": "query",
        "is_auxiliary": False,
    },
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _detect_records_path(payload: Any) -> str:
    if isinstance(payload, list):
        return "(root_array)"
    if not isinstance(payload, dict):
        return ""
    for key in (
        "prbookinfos",
        "marketList",
        "records",
        "data",
        "list",
        "result",
        "announcements",
        "content",
    ):
        val = payload.get(key)
        if isinstance(val, list):
            return key
        if isinstance(val, dict):
            for sub in ("records", "list", "data"):
                subval = val.get(sub)
                if isinstance(subval, list):
                    return f"{key}.{sub}"
    return "unknown"


def _build_request_url(api_url: str, params: Dict[str, Any], params_location: str, method: str) -> str:
    if params_location == "query" and params and method.upper() == "GET":
        return f"{api_url}?{urlencode(params)}"
    if params_location == "query" and params:
        return f"{api_url}?{urlencode(params)}"
    return api_url


def _empty_result_row(
    source: Dict[str, Any],
    case: Dict[str, Any],
    *,
    dry_run: bool,
) -> Dict[str, str]:
    api_url = case.get("api_url_override") or source.get("api_url") or ""
    params = dict(case.get("params") or {})
    params_location = str(case.get("params_location") or source.get("params_location") or "form")
    method = str(case.get("method") or source.get("method") or "POST").upper()
    return {
        "source_id": str(source.get("source_id", "")),
        "source_name": str(source.get("source_name", "")),
        "test_case_id": str(case.get("test_case_id", "")),
        "request_url": _build_request_url(str(api_url), params, params_location, method),
        "method": method,
        "params": json.dumps(params, ensure_ascii=False),
        "http_status": "",
        "response_ok": "no",
        "records_path": "",
        "sample_rows": "",
        "observed_total_rows": "",
        "observed_total_pages": "",
        "field_count": "",
        "key_fields": "",
        "company_code_available": "unknown",
        "date_available": "unknown",
        "amount_available": "unknown",
        "nested_detail_available": "unknown",
        "requires_login": "unknown",
        "requires_captcha": "unknown",
        "requires_paid_permission": "unknown",
        "schema_matches_expected": "unknown",
        "field_set_changed": "unknown",
        "empty_but_valid_response": "no",
        "validation_status": "dry_run" if dry_run else "unknown_error",
        "recommended_status_after_stability": "unknown",
        "notes": "auxiliary market summary" if case.get("is_auxiliary") else "",
    }


def _schema_matches(expected: List[str], record_keys: Set[str]) -> str:
    if not expected:
        return "unknown"
    if not record_keys:
        return "partial"
    matched = [f for f in expected if f in record_keys]
    if len(matched) == len(expected):
        return "yes"
    if len(matched) >= max(1, len(expected) // 2):
        return "partial"
    return "no"


def run_test_case(
    source: Dict[str, Any],
    case: Dict[str, Any],
    defaults: Dict[str, Any],
    session: requests.Session,
    *,
    dry_run: bool,
) -> Dict[str, str]:
    row = _empty_result_row(source, case, dry_run=dry_run)
    if dry_run:
        row["validation_status"] = "dry_run"
        row["notes"] = (row["notes"] + "; dry-run: 未发起请求").strip("; ")
        return row

    api_url = case.get("api_url_override") or source.get("api_url")
    if not api_url:
        row["validation_status"] = "unknown_error"
        row["notes"] = "api_url 未配置"
        return row

    timeout = float(source.get("timeout_seconds") or defaults.get("timeout_seconds") or REQUEST_TIMEOUT)
    method = str(case.get("method") or source.get("method") or "POST").upper()
    params = dict(case.get("params") or {})
    params_location = str(
        case.get("params_location") or source.get("params_location") or defaults.get("params_location") or "form"
    ).lower()
    expected = list(source.get("expected_fields") or [])
    base_notes = str(source.get("notes", ""))
    aux_note = "auxiliary: marginTrading/market 汇总，非 detailList 主 source" if case.get("is_auxiliary") else ""

    headers = dict(AJAX_HEADERS)
    try:
        if method == "GET":
            resp = session.get(api_url, params=params, headers={k: v for k, v in headers.items() if k != "Content-Type"}, timeout=timeout)
        elif params_location == "query":
            post_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
            resp = session.post(api_url, params=params, headers=post_headers, timeout=timeout)
        elif params_location == "none":
            post_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
            resp = session.post(api_url, headers=post_headers, timeout=timeout)
        else:
            resp = session.post(api_url, data=params, headers=headers, timeout=timeout)

        row["http_status"] = str(resp.status_code)
        body = resp.text or ""
        blocked, reason = _detect_blocked(body[:8000])
        if blocked:
            row["validation_status"] = "blocked"
            row["response_ok"] = "no"
            if reason == "requires_login":
                row["requires_login"] = "yes"
            elif reason == "requires_captcha":
                row["requires_captcha"] = "yes"
            elif reason == "requires_paid_permission":
                row["requires_paid_permission"] = "yes"
            row["notes"] = f"{aux_note}; API 响应提示 {reason}".strip("; ")
            return row

        row["requires_login"] = "no"
        row["requires_captcha"] = "no"
        row["requires_paid_permission"] = "no"

        if resp.status_code != 200:
            row["validation_status"] = "http_error"
            row["response_ok"] = "no"
            row["notes"] = f"{aux_note}; HTTP {resp.status_code}".strip("; ")
            return row

        response_type = _infer_response_type(resp.headers.get("Content-Type", ""), body[:2000])
        if response_type != "json":
            row["validation_status"] = "parse_error"
            row["response_ok"] = "no"
            row["notes"] = f"{aux_note}; 非 JSON 响应: {response_type}".strip("; ")
            return row

        try:
            payload = resp.json()
        except json.JSONDecodeError:
            row["validation_status"] = "parse_error"
            row["response_ok"] = "no"
            row["notes"] = f"{aux_note}; JSON 解析失败".strip("; ")
            return row

        row["response_ok"] = "yes"
        records_path = _detect_records_path(payload)
        row["records_path"] = records_path
        records = _extract_records(payload)
        observed_total_rows, observed_total_pages = _observed_meta_from_payload(payload)
        row["observed_total_rows"] = observed_total_rows
        row["observed_total_pages"] = observed_total_pages
        row["sample_rows"] = str(len(records))

        if records:
            record_keys = set(records[0].keys())
            keys = list(record_keys)
            matched = [f for f in expected if f in record_keys] if expected else keys
            row["field_count"] = str(len(matched) if expected else len(keys))
            row["key_fields"] = "|".join(matched if expected else keys[:30])
            dim_code, dim_date, dim_amount = _dimension_flags_from_record_keys(record_keys)
            code_ok, date_ok, amount_ok = _field_hints_available(keys)
            row["company_code_available"] = dim_code if dim_code == "yes" else code_ok
            row["date_available"] = dim_date if dim_date == "yes" else date_ok
            row["amount_available"] = dim_amount if dim_amount == "yes" else amount_ok
            if "detail" in record_keys:
                detail_val = records[0].get("detail")
                row["nested_detail_available"] = (
                    "yes" if isinstance(detail_val, list) and len(detail_val) > 0 else "partial"
                )
            else:
                row["nested_detail_available"] = "no"
            row["schema_matches_expected"] = _schema_matches(expected, record_keys)
            row["empty_but_valid_response"] = "no"
            row["validation_status"] = "sample_ok"
        else:
            keys = _flatten_keys(payload)
            row["field_count"] = "0"
            row["key_fields"] = ""
            row["company_code_available"] = "no"
            row["date_available"] = "no"
            row["amount_available"] = "no"
            row["nested_detail_available"] = "no"
            row["schema_matches_expected"] = "partial" if records_path not in ("", "unknown") else "no"
            row["empty_but_valid_response"] = "yes"
            row["validation_status"] = "empty_but_valid_response"

        note_parts = [p for p in (aux_note, base_notes[:120] if base_notes else "") if p]
        if observed_total_rows:
            note_parts.append(f"observed_total_rows={observed_total_rows}")
        if observed_total_pages:
            note_parts.append(f"observed_total_pages={observed_total_pages}")
        row["notes"] = "; ".join(note_parts)
        return row

    except requests.RequestException as exc:
        row["validation_status"] = "unknown_error"
        row["response_ok"] = "no"
        row["notes"] = f"{aux_note}; 请求异常: {exc}".strip("; ")
        return row


def _field_signature(row: Dict[str, str]) -> str:
    return row.get("key_fields") or ""


def _aggregate_source_stability(
    rows: List[Dict[str, str]],
    *,
    include_auxiliary: bool = False,
) -> Dict[str, str]:
    """Return per-source recommended_status_after_stability and field_set_changed flags."""
    by_source: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for r in rows:
        if r.get("is_auxiliary_tag") == "yes" and not include_auxiliary:
            continue
        by_source[r["source_id"]].append(r)

    source_status: Dict[str, str] = {}
    for sid, srows in by_source.items():
        main_rows = [r for r in srows if r.get("is_auxiliary_tag") != "yes"]
        if not main_rows:
            main_rows = srows

        statuses = [r["validation_status"] for r in main_rows]
        ok_like = {"sample_ok", "empty_but_valid_response"}
        if any(s == "blocked" for s in statuses):
            source_status[sid] = "blocked"
            continue
        if any(s == "schema_changed" for s in statuses):
            source_status[sid] = "testing_needs_more_review"
            continue
        if all(s in ok_like for s in statuses):
            paths = {r["records_path"] for r in main_rows if r.get("records_path")}
            sigs = {_field_signature(r) for r in main_rows if r.get("validation_status") == "sample_ok"}
            sigs.discard("")
            path_stable = len(paths) <= 1 or paths == {""}
            sig_stable = len(sigs) <= 1
            if path_stable and sig_stable:
                source_status[sid] = "testing_stable_sample"
            else:
                source_status[sid] = "testing_partial"
        elif any(s in ok_like for s in statuses):
            source_status[sid] = "testing_partial"
        else:
            source_status[sid] = "testing_needs_more_review"

    return source_status


def apply_field_set_and_stability(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Mark field_set_changed vs first successful case; set source-level stability status."""
    baseline_sig: Dict[str, str] = {}
    baseline_path: Dict[str, str] = {}

    for r in rows:
        if r.get("is_auxiliary_tag") == "yes":
            r["field_set_changed"] = "n/a"
            continue
        sid = r["source_id"]
        if r["validation_status"] in ("sample_ok", "empty_but_valid_response"):
            sig = _field_signature(r)
            path = r.get("records_path") or ""
            if sid not in baseline_sig and sig:
                baseline_sig[sid] = sig
                baseline_path[sid] = path
                r["field_set_changed"] = "no"
            elif sid not in baseline_path and not sig:
                baseline_path[sid] = path
                r["field_set_changed"] = "no"
            else:
                changed = False
                if sig and sid in baseline_sig and sig != baseline_sig[sid]:
                    changed = True
                if path and sid in baseline_path and path != baseline_path[sid]:
                    changed = True
                r["field_set_changed"] = "yes" if changed else "no"
                if changed and r["validation_status"] == "sample_ok":
                    r["validation_status"] = "schema_changed"
        else:
            r["field_set_changed"] = "unknown"

    source_status = _aggregate_source_stability(rows)
    for r in rows:
        sid = r["source_id"]
        if r.get("is_auxiliary_tag") == "yes":
            r["recommended_status_after_stability"] = source_status.get(sid, "testing_partial")
            if "auxiliary" not in (r.get("notes") or ""):
                r["notes"] = ((r.get("notes") or "") + "; auxiliary observation").strip("; ")
        else:
            r["recommended_status_after_stability"] = source_status.get(sid, "unknown")

    return rows


def write_csv(rows: List[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out_rows = [{k: r.get(k, "") for k in CSV_FIELDS} for r in rows]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)


def write_summary(
    rows: List[Dict[str, str]],
    path: str,
    *,
    dry_run: bool,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    val_counts = Counter(r["validation_status"] for r in rows)
    stab_counts = Counter(r["recommended_status_after_stability"] for r in rows if r.get("is_auxiliary_tag") != "yes")
    source_stab = _aggregate_source_stability(rows)

    lines = [
        "# CNINFO D 类 Priority-1 多日期小样本稳定性复测总结",
        "",
        f"- 生成时间：{_now_iso()}",
        "- 脚本：`lab/validate_cninfo_table_sources_multidate.py`",
        "- 配置：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)",
        "- 前置：[cninfo_table_sources_priority1_summary.md](cninfo_table_sources_priority1_summary.md)",
        "- 字段语义 UI 对照：[cninfo_table_field_semantics_ui_check_summary.md](cninfo_table_field_semantics_ui_check_summary.md)",
        f"- 模式：**{'dry-run（未联网）' if dry_run else 'live 小样本'}**",
        "",
        "---",
        "",
        "## 1. 目的",
        "",
        "在 priority-1 endpoint discovery 与 UI 字段语义对照完成后，验证 5 个 **testing** source",
        "在多个日期 / 报告期下 **endpoint 可访问性**、**records JSON path**、**字段集合** 是否保持稳定。",
        "",
        "这是 **多日期小样本** 稳定性复测，不是全量或长期稳定性验证；**不写 verified**。",
        "",
        "## 2. 测试范围",
        "",
        "| source_id | 测试用例 | 参数要点 |",
        "|-----------|----------|----------|",
        "| disclosure_schedule | 2 | `sectionTime=2025-12-31`, `2026-06-30`; market=szsh; pagesize=20; pagenum=1 |",
        "| restricted_shares_unlock | 3 | `tdate=2026-06-08`, `2026-07-06`, `2026-07-03` |",
        "| block_trade | 3 | `tdate=2026-07-03`, `2026-07-02`, `2026-07-01` |",
        "| margin_trading | 2 + 2(aux) | detailList 默认请求 ×2；market summary `tdate=2026-07-02/01`（附属） |",
        "| abnormal_trading | 3 | `sdate=edate` 2026-07-03 / 07-02 / 07-01; page=1; rows=30 |",
        "",
        f"- **total_test_cases**：**{len(rows)}**",
        "- 每个用例 **仅请求一次**，不翻页、不循环长区间。",
        "",
        "## 3. 总体结果",
        "",
        "### validation_status",
        "",
        "| validation_status | 数量 |",
        "|-------------------|------|",
    ]
    for vs in (
        "sample_ok",
        "empty_but_valid_response",
        "schema_changed",
        "http_error",
        "blocked",
        "parse_error",
        "unknown_error",
        "dry_run",
    ):
        if val_counts.get(vs, 0):
            lines.append(f"| {vs} | {val_counts[vs]} |")

    lines.extend([
        "",
        "### recommended_status_after_stability（按 source，主用例）",
        "",
        "| recommended_status_after_stability | source 数 |",
        "|----------------------------------|-----------|",
    ])
    src_stab_counter = Counter(source_stab.values())
    for st in (
        "testing_stable_sample",
        "testing_partial",
        "testing_needs_more_review",
        "blocked",
        "unknown",
    ):
        if src_stab_counter.get(st, 0):
            lines.append(f"| {st} | {src_stab_counter[st]} |")

    lines.extend(["", "## 4. 分 source 结果", ""])

    for sid in PRIORITY1_IDS:
        srows = [r for r in rows if r["source_id"] == sid]
        if not srows:
            continue
        main_rows = [r for r in srows if r.get("is_auxiliary_tag") != "yes"]
        stab = source_stab.get(sid, "unknown")
        lines.append(f"### {sid}")
        lines.append("")
        lines.append(f"- **recommended_status_after_stability**：**{stab}**")
        lines.append("")
        lines.append("| test_case_id | http_status | sample_rows | records_path | field_count | validation_status | field_set_changed |")
        lines.append("|--------------|-------------|-------------|--------------|-------------|-------------------|-------------------|")
        for r in srows:
            lines.append(
                f"| {r['test_case_id']} | {r['http_status'] or '—'} | {r['sample_rows'] or '—'} | "
                f"{r['records_path'] or '—'} | {r['field_count'] or '—'} | {r['validation_status']} | "
                f"{r.get('field_set_changed', '—')} |"
            )
        paths = {r["records_path"] for r in main_rows if r.get("records_path")}
        schema_stable = not any(r["validation_status"] == "schema_changed" for r in main_rows)
        lines.append("")
        lines.append(
            f"- **schema 稳定**：{'是' if schema_stable and len(paths) <= 1 else '部分/待观察'} "
            f"（records_path: {', '.join(sorted(paths)) or '—'}）"
        )
        lines.append("")

    lines.extend([
        "## 5. 发现的问题",
        "",
    ])

    empty_cases = [r for r in rows if r["validation_status"] == "empty_but_valid_response"]
    if empty_cases:
        lines.append("### 空结果但结构正常（empty_but_valid_response）")
        for r in empty_cases:
            lines.append(f"- `{r['source_id']}` / `{r['test_case_id']}`：records=0，records_path=`{r['records_path']}`")
        lines.append("")

    schema_changed = [r for r in rows if r["validation_status"] == "schema_changed"]
    if schema_changed:
        lines.append("### 字段集合变化（schema_changed）")
        for r in schema_changed:
            lines.append(f"- `{r['source_id']}` / `{r['test_case_id']}`")
        lines.append("")
    else:
        lines.append("- 本次 **未发现** 主用例 `schema_changed`。")
        lines.append("")

    partial_sources = [sid for sid, st in source_stab.items() if st == "testing_partial"]
    if partial_sources:
        lines.append("### testing_partial source")
        for sid in partial_sources:
            lines.append(f"- **{sid}**")
        lines.append("")

    lines.extend([
        "### margin_trading 限制",
        "",
        "- `detailList` 主接口 **不显式传 date**（`params_location=none`）；稳定性复测主要看 **两次默认请求返回结构是否一致**。",
        "- 页面上方 `marginTrading/market?tdate=` 为 **市场汇总** 附属接口，字段语义与 detailList 不同，**不作主 source**。",
        "",
        "## 6. 结论",
        "",
        "- 本次为 **多日期小样本** 稳定性复测，覆盖 5 个 priority-1 testing source，**不是**全市场或长期稳定性验证。",
        "- **不写 verified**；通过复测最多标记为 **testing_stable_sample**。",
        "- **空结果不等于接口不可用**：`empty_but_valid_response` 表示 HTTP 200 + JSON 可解析 + records path 稳定，仅当日无数据。",
        "- 单日期失败 **不直接否定** source，需在 summary 中结合其他日期综合判断。",
        "",
        "## 7. 下一步",
        "",
        "1. 对 **testing_stable_sample** source 建立 future schema draft（仍非 verified）。",
        "2. 对 **testing_partial** source 补充日期或页面确认（如 margin_trading 日期参数、空日期解释）。",
        "3. 进入 **priority-2 source discovery**（shareholder_change、equity_pledge 等）。",
        "4. **暂不入库、不全量抓取**。",
        "",
        "## 8. 边界",
        "",
        "- 不修改原 `cninfo_table_sources_validation.csv`",
        "- 不登录、不绕过验证码/付费；timeout ≈10s；请求间 sleep",
        "- 不写 **verified**",
        "",
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CNINFO D-class priority-1 multi-date stability retest"
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--output-csv", default=DEFAULT_OUT_CSV)
    parser.add_argument("--output-summary", default=DEFAULT_OUT_SUMMARY)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    defaults = config.get("defaults") or {}
    sources_by_id = {
        s["source_id"]: s
        for s in (config.get("sources") or [])
        if s.get("source_id") in PRIORITY1_IDS
    }

    sleep_sec = float(defaults.get("sleep_seconds") or SLEEP_SECONDS)
    session = requests.Session()
    rows: List[Dict[str, str]] = []

    print(f"[{_now_iso()}] CNINFO multidate stability — {len(TEST_CASES)} test cases")
    if args.dry_run:
        print("[dry-run] No HTTP requests.")

    for i, case in enumerate(TEST_CASES, 1):
        sid = case["source_id"]
        tcid = case["test_case_id"]
        source = sources_by_id.get(sid)
        if not source:
            print(f"[{i}/{len(TEST_CASES)}] SKIP {tcid}: source not in config")
            continue
        print(f"[{i}/{len(TEST_CASES)}] {tcid} ...")
        row = run_test_case(source, case, defaults, session, dry_run=args.dry_run)
        row["is_auxiliary_tag"] = "yes" if case.get("is_auxiliary") else "no"
        rows.append(row)
        if not args.dry_run and i < len(TEST_CASES):
            time.sleep(sleep_sec)

    rows = apply_field_set_and_stability(rows)
    write_csv(rows, args.output_csv)
    write_summary(rows, args.output_summary, dry_run=args.dry_run)
    print(f"Wrote {args.output_csv}")
    print(f"Wrote {args.output_summary}")


if __name__ == "__main__":
    main()
