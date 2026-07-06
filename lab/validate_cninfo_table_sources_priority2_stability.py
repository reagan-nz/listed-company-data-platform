"""
CNINFO D 类 priority-2 多日期 / 多参数小样本稳定性复测（Era C Phase 2）。

对 5 个 priority-2 testing source 在 2–3 个日期 / 参数下各请求一次，
检查 endpoint、records path、字段集合是否稳定。
不翻页、不全量抓取、不入库、不写 verified。

用法：
    python lab/validate_cninfo_table_sources_priority2_stability.py
    python lab/validate_cninfo_table_sources_priority2_stability.py --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple
from urllib.parse import urlencode

import requests
import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

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
    BASE_DIR, "outputs", "validation", "cninfo_table_sources_priority2_stability.csv"
)
DEFAULT_OUT_SUMMARY = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_table_sources_priority2_stability_summary.md"
)

SLEEP_SECONDS = 0.6
REQUEST_TIMEOUT = 10

PRIORITY2_IDS = (
    "equity_pledge",
    "shareholder_change",
    "executive_shareholding",
    "fund_industry_allocation",
    "shareholder_data",
)

INDUSTRY_AGGREGATE_IDS = frozenset({"fund_industry_allocation"})

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
    "field_count",
    "key_fields",
    "company_code_available",
    "date_available",
    "amount_available",
    "schema_matches_expected",
    "field_set_changed",
    "empty_but_valid_response",
    "validation_status",
    "recommended_status_after_stability",
    "notes",
]

TEST_CASES: List[Dict[str, Any]] = [
    # equity_pledge
    {
        "source_id": "equity_pledge",
        "test_case_id": "ep_tdate_2026_07_03",
        "params": {"tdate": "2026-07-03"},
        "params_location": "query",
    },
    {
        "source_id": "equity_pledge",
        "test_case_id": "ep_tdate_2026_07_02",
        "params": {"tdate": "2026-07-02"},
        "params_location": "query",
    },
    {
        "source_id": "equity_pledge",
        "test_case_id": "ep_tdate_2026_07_01",
        "params": {"tdate": "2026-07-01"},
        "params_location": "query",
    },
    # shareholder_change
    {
        "source_id": "shareholder_change",
        "test_case_id": "sc_inc_tdate_2026_07_03",
        "params": {"type": "inc", "tdate": "2026-07-03"},
        "params_location": "query",
    },
    {
        "source_id": "shareholder_change",
        "test_case_id": "sc_desc_no_tdate",
        "params": {"type": "desc"},
        "params_location": "query",
    },
    {
        "source_id": "shareholder_change",
        "test_case_id": "sc_desc_tdate_2026_07_03",
        "params": {"type": "desc", "tdate": "2026-07-03"},
        "params_location": "query",
    },
    # executive_shareholding
    {
        "source_id": "executive_shareholding",
        "test_case_id": "esh_oneMonth_varyType_b",
        "params": {"timeMark": "oneMonth", "varyType": "b"},
        "params_location": "query",
    },
    {
        "source_id": "executive_shareholding",
        "test_case_id": "esh_threeMonth_varyType_b",
        "params": {"timeMark": "threeMonth", "varyType": "b"},
        "params_location": "query",
    },
    {
        "source_id": "executive_shareholding",
        "test_case_id": "esh_oneMonth_varyType_s",
        "params": {"timeMark": "oneMonth", "varyType": "s"},
        "params_location": "query",
    },
    # fund_industry_allocation
    {
        "source_id": "fund_industry_allocation",
        "test_case_id": "fia_default",
        "params": {},
        "params_location": "none",
    },
    {
        "source_id": "fund_industry_allocation",
        "test_case_id": "fia_rdate_20260331",
        "params": {"rdate": "20260331"},
        "params_location": "query",
    },
    {
        "source_id": "fund_industry_allocation",
        "test_case_id": "fia_rdate_20251231",
        "params": {"rdate": "20251231"},
        "params_location": "query",
    },
    # shareholder_data
    {
        "source_id": "shareholder_data",
        "test_case_id": "sd_rdate_20260331",
        "params": {"rdate": "20260331"},
        "params_location": "query",
    },
    {
        "source_id": "shareholder_data",
        "test_case_id": "sd_rdate_20251231",
        "params": {"rdate": "20251231"},
        "params_location": "query",
    },
    {
        "source_id": "shareholder_data",
        "test_case_id": "sd_rdate_20250930",
        "params": {"rdate": "20250930"},
        "params_location": "query",
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
    if params_location in ("query",) and params:
        return f"{api_url}?{urlencode(params)}"
    return api_url


def _empty_result_row(source: Dict[str, Any], case: Dict[str, Any], *, dry_run: bool) -> Dict[str, str]:
    api_url = str(source.get("api_url") or "")
    params = dict(case.get("params") or {})
    params_location = str(case.get("params_location") or source.get("params_location") or "form")
    method = str(case.get("method") or source.get("method") or "POST").upper()
    return {
        "source_id": str(source.get("source_id", "")),
        "source_name": str(source.get("source_name", "")),
        "test_case_id": str(case.get("test_case_id", "")),
        "request_url": _build_request_url(api_url, params, params_location, method),
        "method": method,
        "params": json.dumps(params, ensure_ascii=False),
        "http_status": "",
        "response_ok": "no",
        "records_path": "",
        "sample_rows": "",
        "observed_total_rows": "",
        "field_count": "",
        "key_fields": "",
        "company_code_available": "unknown",
        "date_available": "unknown",
        "amount_available": "unknown",
        "schema_matches_expected": "unknown",
        "field_set_changed": "unknown",
        "empty_but_valid_response": "no",
        "validation_status": "dry_run" if dry_run else "unknown_error",
        "recommended_status_after_stability": "unknown",
        "notes": "",
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
        row["notes"] = "dry-run: 未发起请求"
        return row

    api_url = source.get("api_url")
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
    page_url = source.get("page_url")
    sid = str(source.get("source_id", ""))

    headers = dict(AJAX_HEADERS)
    if page_url:
        headers["Referer"] = str(page_url)

    try:
        if method == "GET":
            resp = session.get(
                api_url,
                params=params,
                headers={k: v for k, v in headers.items() if k != "Content-Type"},
                timeout=timeout,
            )
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

        response_type = _infer_response_type(resp.headers.get("Content-Type", ""), body[:2000])
        payload: Any = None
        if response_type == "json":
            try:
                payload = resp.json()
            except json.JSONDecodeError:
                payload = None

        skip_content_blocked = (
            isinstance(payload, dict)
            and payload.get("code") in (200, "200")
            and bool(_extract_records(payload))
        )
        if not skip_content_blocked:
            blocked, reason = _detect_blocked(body[:8000])
            if blocked:
                row["validation_status"] = "blocked"
                row["response_ok"] = "no"
                row["notes"] = f"API 响应提示 {reason}"
                return row

        if resp.status_code != 200:
            row["validation_status"] = "http_error"
            row["response_ok"] = "no"
            row["notes"] = f"HTTP {resp.status_code}"
            return row

        if response_type != "json":
            row["validation_status"] = "parse_error"
            row["response_ok"] = "no"
            row["notes"] = f"非 JSON 响应: {response_type}"
            return row

        if payload is None:
            row["validation_status"] = "parse_error"
            row["response_ok"] = "no"
            row["notes"] = "JSON 解析失败"
            return row

        row["response_ok"] = "yes"
        records_path = _detect_records_path(payload)
        row["records_path"] = records_path
        records = _extract_records(payload)
        observed_total_rows, _ = _observed_meta_from_payload(payload)
        row["observed_total_rows"] = observed_total_rows
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
            if sid in INDUSTRY_AGGREGATE_IDS:
                row["company_code_available"] = "no"
            row["schema_matches_expected"] = _schema_matches(expected, record_keys)
            row["empty_but_valid_response"] = "no"
            row["validation_status"] = "sample_ok"
        else:
            row["field_count"] = "0"
            row["key_fields"] = ""
            row["company_code_available"] = "no" if sid not in INDUSTRY_AGGREGATE_IDS else "no"
            row["date_available"] = "no"
            row["amount_available"] = "no"
            row["schema_matches_expected"] = "partial" if records_path not in ("", "unknown") else "no"
            row["empty_but_valid_response"] = "yes"
            row["validation_status"] = "empty_but_valid_response"

        note_parts: List[str] = []
        if observed_total_rows:
            note_parts.append(f"observed_total_rows={observed_total_rows}")
        row["notes"] = "; ".join(note_parts)
        return row

    except requests.RequestException as exc:
        row["validation_status"] = "unknown_error"
        row["response_ok"] = "no"
        row["notes"] = f"请求异常: {exc}"
        return row


def _field_signature(row: Dict[str, str]) -> str:
    return row.get("key_fields") or ""


def _aggregate_source_stability(rows: List[Dict[str, str]]) -> Dict[str, str]:
    by_source: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for r in rows:
        by_source[r["source_id"]].append(r)

    source_status: Dict[str, str] = {}
    for sid, srows in by_source.items():
        statuses = [r["validation_status"] for r in srows]
        ok_like = {"sample_ok", "empty_but_valid_response"}
        if any(s == "blocked" for s in statuses):
            source_status[sid] = "blocked"
            continue
        if any(s == "schema_changed" for s in statuses):
            source_status[sid] = "testing_needs_more_review"
            continue
        if all(s in ok_like for s in statuses):
            paths = {r["records_path"] for r in srows if r.get("records_path")}
            sigs = {_field_signature(r) for r in srows if r.get("validation_status") == "sample_ok"}
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
    baseline_sig: Dict[str, str] = {}
    baseline_path: Dict[str, str] = {}

    for r in rows:
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
        r["recommended_status_after_stability"] = source_status.get(r["source_id"], "unknown")

    return rows


def write_csv(rows: List[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out_rows = [{k: r.get(k, "") for k in CSV_FIELDS} for r in rows]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)


def write_summary(rows: List[Dict[str, str]], path: str, *, dry_run: bool) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    val_counts = Counter(r["validation_status"] for r in rows)
    source_stab = _aggregate_source_stability(rows)
    src_stab_counter = Counter(source_stab.values())

    lines = [
        "# CNINFO D 类 Priority-2 多参数稳定性复测总结",
        "",
        f"- 生成时间：{_now_iso()}",
        "- 脚本：`lab/validate_cninfo_table_sources_priority2_stability.py`",
        "- 配置：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)",
        "- 前置：[cninfo_table_sources_priority2_current_summary.md](cninfo_table_sources_priority2_current_summary.md)",
        "- 字段语义 UI 对照：[cninfo_table_field_semantics_priority2.md](cninfo_table_field_semantics_priority2.md)",
        f"- 模式：**{'dry-run（未联网）' if dry_run else 'live 小样本'}**",
        "",
        "---",
        "",
        "## 1. 目的",
        "",
        "本阶段验证 priority-2 五个 **testing** source 在多个日期 / 参数组合下",
        "**endpoint 可访问性**、**records JSON path**、**字段集合** 是否保持稳定。",
        "",
        "这是 **多参数小样本** 稳定性复测，不是全量或长期稳定性验证；**不写 verified**。",
        "",
        "## 2. 测试范围",
        "",
        "| source_id | 测试用例数 | 参数要点 |",
        "|-----------|------------|----------|",
        "| equity_pledge | 3 | `tdate=2026-07-03`, `2026-07-02`, `2026-07-01` |",
        "| shareholder_change | 3 | `type=inc,tdate=2026-07-03`; `type=desc`; `type=desc,tdate=2026-07-03` |",
        "| executive_shareholding | 3 | `oneMonth+b`; `threeMonth+b`; `oneMonth+s` |",
        "| fund_industry_allocation | 3 | 默认请求；`rdate=20260331`; `rdate=20251231` |",
        "| shareholder_data | 3 | `rdate=20260331`, `20251231`, `20250930` |",
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
        "### recommended_status_after_stability（按 source）",
        "",
        "| recommended_status_after_stability | source 数 |",
        "|----------------------------------|-----------|",
    ])
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

    for sid in PRIORITY2_IDS:
        srows = [r for r in rows if r["source_id"] == sid]
        if not srows:
            continue
        stab = source_stab.get(sid, "unknown")
        lines.append(f"### {sid}")
        lines.append("")
        lines.append(f"- **recommended_status_after_stability**：**{stab}**")
        lines.append("")
        lines.append(
            "| test_case_id | http_status | sample_rows | field_count | records_path | "
            "validation_status | field_set_changed |"
        )
        lines.append(
            "|--------------|-------------|-------------|-------------|--------------|"
            "-------------------|-------------------|"
        )
        for r in srows:
            lines.append(
                f"| {r['test_case_id']} | {r['http_status'] or '—'} | {r['sample_rows'] or '—'} | "
                f"{r['field_count'] or '—'} | {r['records_path'] or '—'} | {r['validation_status']} | "
                f"{r.get('field_set_changed', '—')} |"
            )
        paths = {r["records_path"] for r in srows if r.get("records_path")}
        sigs = {_field_signature(r) for r in srows if r.get("validation_status") == "sample_ok"}
        sigs.discard("")
        schema_stable = not any(r["validation_status"] == "schema_changed" for r in srows)
        lines.append("")
        lines.append(
            f"- **records path 稳定**：{'是' if len(paths) <= 1 else '否'} "
            f"（{', '.join(sorted(paths)) or '—'}）"
        )
        lines.append(
            f"- **field set 稳定**：{'是' if len(sigs) <= 1 and schema_stable else '部分/待观察'}"
        )
        lines.append("")

    lines.extend([
        "## 5. 分层说明",
        "",
        "### company-level source",
        "",
        "- `equity_pledge` — 股权质押",
        "- `shareholder_change` — 股东增减持（inc / desc）",
        "- `executive_shareholding` — 高管持股变动明细",
        "- `shareholder_data` — 股东人数 / 人均持股定期数据",
        "",
        "### industry-level aggregate",
        "",
        "- `fund_industry_allocation` — 基金行业配置（行业级聚合表）",
        "- **不要**将 `fund_industry_allocation` 归入 company event schema",
        "- 稳定性判断 **不要求** `company_code_available=yes`",
        "",
        "## 6. 发现的问题",
        "",
    ])

    empty_cases = [r for r in rows if r["validation_status"] == "empty_but_valid_response"]
    if empty_cases:
        lines.append("### 空结果但结构正常（empty_but_valid_response）")
        for r in empty_cases:
            lines.append(
                f"- `{r['source_id']}` / `{r['test_case_id']}`：records=0，records_path=`{r['records_path']}`"
            )
        lines.append("")
    else:
        lines.append("- 本次 **未发现** `empty_but_valid_response` 用例。")
        lines.append("")

    schema_changed = [r for r in rows if r["validation_status"] == "schema_changed"]
    if schema_changed:
        lines.append("### 字段集合变化（schema_changed）")
        for r in schema_changed:
            lines.append(f"- `{r['source_id']}` / `{r['test_case_id']}`")
        lines.append("")
    else:
        lines.append("- 本次 **未发现** `schema_changed`。")
        lines.append("")

    blocked = [r for r in rows if r["validation_status"] == "blocked"]
    if blocked:
        lines.append("### blocked")
        for r in blocked:
            lines.append(f"- `{r['source_id']}` / `{r['test_case_id']}`")
        lines.append("")

    lines.extend([
        "### 参数敏感性观察",
        "",
        "- **shareholder_change**：`type=desc` 可不传 `tdate`；与 `type=desc,tdate=...` 对比见分 source 表。",
        "- **executive_shareholding**：`varyType` / `timeMark` 组合影响返回行数；空结果若 HTTP 200 + records path 正常记为 `empty_but_valid_response`。",
        "- **fund_industry_allocation**：`rdate` query 参数是否改变结果集待结合各 test case `sample_rows` 观察。",
        "- **shareholder_data**：不同 `rdate` 报告期返回行数可能不同，属预期行为。",
        "",
        "## 7. 结论",
        "",
        "- 本次为 **多参数小样本** 稳定性复测，覆盖 5 个 priority-2 testing source。",
        "- **不写 verified**；通过复测最多标记为 **testing_stable_sample**。",
        "- 该阶段仍 **不是** 生产化验证或全市场稳定性结论。",
        "- **空结果不等于接口不可用**：`empty_but_valid_response` 表示 HTTP 200 + JSON 可解析 + records path 稳定。",
        "",
        "### 各 source 稳定性判定",
        "",
    ])
    for sid in PRIORITY2_IDS:
        stab = source_stab.get(sid, "unknown")
        lines.append(f"- **{sid}** → `{stab}`")

    lines.extend([
        "",
        "## 8. 下一步",
        "",
        "1. 若五源稳定，priority-2 当前批次可收口。",
        "2. 进入下一批 discovery：`ipo_query`、`szse_calendar`、`executive_shareholding_summary`、`fund_stock_holding`。",
        "3. **暂不入库、不全量抓取**；不写 verified。",
        "",
        "## 9. 边界",
        "",
        "- 不修改原 `cninfo_table_sources_validation.csv`",
        "- 不修改 priority-1 summary",
        "- 不登录、不绕过验证码/付费；timeout ≈10s；请求间 sleep",
        "- 不写 **verified**",
        "",
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CNINFO D-class priority-2 multi-param stability retest"
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
        if s.get("source_id") in PRIORITY2_IDS
    }

    sleep_sec = float(defaults.get("sleep_seconds") or SLEEP_SECONDS)
    session = requests.Session()
    rows: List[Dict[str, str]] = []

    print(f"[{_now_iso()}] CNINFO priority-2 stability — {len(TEST_CASES)} test cases")
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
