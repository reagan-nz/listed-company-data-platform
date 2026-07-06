"""
CNINFO D 类固定表格 / 市场行为数据源入口探测（Era C Phase 2）。

读取 config/cninfo_table_sources.yaml，对每个 source 做轻量验证：
- api_url 为空：仅记录 page_url，validation_status=needs_manual_endpoint_discovery
- api_url 非空：小样本请求，判断 HTTP / 结构化字段 / 权限

默认不自动联网；请在本地合规环境执行：
    python lab/validate_cninfo_table_sources.py --dry-run
    python lab/validate_cninfo_table_sources.py
    python lab/validate_cninfo_table_sources.py --config config/cninfo_table_sources.yaml \\
        --output-prefix outputs/validation/cninfo_table_sources

边界：不登录、不绕过验证码/付费/权限；不大规模抓取；不入库；不写 verified。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG = os.path.join(BASE_DIR, "config", "cninfo_table_sources.yaml")
DEFAULT_OUT_PREFIX = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_table_sources")

SLEEP_SECONDS = 0.6
REQUEST_TIMEOUT = 10

AJAX_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
        "ListedCompanyDataCollector/cninfo-table-sources"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.cninfo.com.cn/",
}

PAGE_HEADERS = {
    "User-Agent": AJAX_HEADERS["User-Agent"],
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": AJAX_HEADERS["Accept-Language"],
}

CSV_FIELDS = [
    "source_id",
    "source_name",
    "page_url",
    "api_url",
    "http_status",
    "access_status",
    "requires_login",
    "requires_captcha",
    "requires_paid_permission",
    "response_type",
    "sample_rows",
    "field_count",
    "key_fields",
    "company_code_available",
    "date_available",
    "amount_available",
    "nested_detail_available",
    "validation_status",
    "recommended_status",
    "notes",
]

CODE_FIELD_HINTS = ("code", "stock", "secid", "symbol", "companycode", "seccode", "secname", "证券代码", "股票代码")
DATE_FIELD_HINTS = ("date", "time", "日期", "时间", "d_0102", "latest_time", "f003d", "declaredate")
AMOUNT_FIELD_HINTS = ("amount", "balance", "volume", "price", "数量", "金额", "余额", "价格", "比例", "f004n", "f005n", "f008n")

BLOCKED_TEXT_HINTS = (
    "登录",
    "请登录",
    "验证码",
    "captcha",
    "无权限",
    "权限不足",
    "付费",
    "商业",
    "数据商城",
    "webapi.cninfo.com.cn",
    "login",
    "unauthorized",
    "forbidden",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_config(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _empty_row(source: Dict[str, Any]) -> Dict[str, str]:
    return {
        "source_id": str(source.get("source_id", "")),
        "source_name": str(source.get("source_name", "")),
        "page_url": str(source.get("page_url") or ""),
        "api_url": str(source.get("api_url") or ""),
        "http_status": "",
        "access_status": "not_checked",
        "requires_login": "unknown",
        "requires_captcha": "unknown",
        "requires_paid_permission": "unknown",
        "response_type": "",
        "sample_rows": "",
        "field_count": "",
        "key_fields": "",
        "company_code_available": "unknown",
        "date_available": "unknown",
        "amount_available": "unknown",
        "nested_detail_available": "unknown",
        "validation_status": "not_run",
        "recommended_status": str(source.get("recommended_status", "unknown")),
        "notes": str(source.get("notes", "")),
    }


def _detect_blocked(text: str) -> Tuple[bool, str]:
    lower = text.lower()
    for hint in BLOCKED_TEXT_HINTS:
        if hint.lower() in lower:
            if hint in ("登录", "请登录", "login"):
                return True, "requires_login"
            if hint in ("验证码", "captcha"):
                return True, "requires_captcha"
            if hint in ("付费", "商业", "数据商城", "webapi.cninfo.com.cn"):
                return True, "requires_paid_permission"
            return True, "blocked"
    return False, ""


def _flatten_keys(obj: Any, prefix: str = "") -> List[str]:
    keys: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            keys.append(path)
            keys.extend(_flatten_keys(v, path))
    elif isinstance(obj, list) and obj:
        keys.extend(_flatten_keys(obj[0], prefix))
    return keys


def _extract_records(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    for key in (
        "records", "marketList", "data", "list", "result", "announcements", "content", "prbookinfos"
    ):
        val = payload.get(key)
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]
        if isinstance(val, dict):
            for sub in ("records", "list", "data"):
                subval = val.get(sub)
                if isinstance(subval, list):
                    return [x for x in subval if isinstance(x, dict)]
    return []


def _observed_meta_from_payload(payload: Any) -> Tuple[str, str]:
    if not isinstance(payload, dict):
        return "", ""
    total = ""
    pages = ""
    if payload.get("totalRows") is not None:
        total = str(payload.get("totalRows"))
    elif payload.get("total") is not None:
        total = str(payload.get("total"))
    data = payload.get("data")
    if isinstance(data, dict):
        if not total and data.get("total") is not None:
            total = str(data.get("total"))
        elif not total and data.get("count") is not None:
            total = str(data.get("count"))
    if payload.get("totalPage") is not None:
        pages = str(payload.get("totalPage"))
    return total, pages


def _observed_total_from_payload(payload: Any) -> str:
    total, _ = _observed_meta_from_payload(payload)
    return total


def _dimension_flags_from_record_keys(record_keys: set) -> Tuple[str, str, str]:
    upper = {k.upper() for k in record_keys}
    code_yes = bool(
        {"SECCODE", "SECNAME"} & upper
        or {"seccode", "secname"} & record_keys
    )
    date_yes = bool(
        upper & {"DECLAREDATE", "F003D", "TRADEDATE", "TRADETIME", "F001D_0102", "F002D_0102", "F006D_0102"}
        or record_keys & {"f001d_0102", "f002d_0102", "f006d_0102"}
    )
    amount_yes = bool(
        upper
        & {
            "F001N", "F002N", "F003N", "F004N", "F005N", "F006N", "F007N", "F008N", "F009N",
            "BUYTOTAL", "SELLTOTAL", "BUYPERCENT", "SELLPERCENT",
        }
    )
    return (
        "yes" if code_yes else "no",
        "yes" if date_yes else "no",
        "yes" if amount_yes else "no",
    )


def _field_hints_available(keys: List[str]) -> Tuple[str, str, str]:
    joined = " ".join(keys).lower()
    code_ok = "yes" if any(h in joined for h in CODE_FIELD_HINTS) else "no"
    date_ok = "yes" if any(h in joined for h in DATE_FIELD_HINTS) else "no"
    amount_ok = "yes" if any(h in joined for h in AMOUNT_FIELD_HINTS) else "no"
    return code_ok, date_ok, amount_ok


def _infer_response_type(content_type: str, body: str) -> str:
    ct = (content_type or "").lower()
    if "json" in ct or body.strip().startswith(("{", "[")):
        return "json"
    if "html" in ct:
        if re.search(r"<table\b", body, re.I):
            return "html_table"
        return "html"
    if "excel" in ct or "spreadsheet" in ct:
        return "excel"
    if "pdf" in ct:
        return "pdf"
    return "unknown"


def validate_source(
    source: Dict[str, Any],
    defaults: Dict[str, Any],
    *,
    dry_run: bool,
    session: requests.Session,
) -> Dict[str, str]:
    row = _empty_row(source)
    api_url = source.get("api_url")
    page_url = source.get("page_url")
    config_status = str(source.get("recommended_status", "unknown"))
    base_notes = str(source.get("notes", ""))

    if dry_run:
        row["access_status"] = "dry_run"
        row["validation_status"] = "dry_run"
        row["recommended_status"] = config_status or "unknown"
        if not api_url:
            row["validation_status"] = "needs_manual_endpoint_discovery"
            row["recommended_status"] = "candidate" if page_url else "unknown"
            row["notes"] = (
                f"{base_notes}; dry-run: api_url 为空，待 DevTools endpoint discovery"
            ).strip("; ")
        else:
            row["notes"] = f"{base_notes}; dry-run: 未发起请求".strip("; ")
        return row

    timeout = float(source.get("timeout_seconds") or defaults.get("timeout_seconds") or REQUEST_TIMEOUT)
    method = str(source.get("method") or defaults.get("method") or "POST").upper()
    params = dict(source.get("params_template") or {})
    params_location = str(
        source.get("params_location") or defaults.get("params_location") or "form"
    ).lower()

    # --- api_url 为空：仅记录 page，不猜接口 ---
    if not api_url:
        row["validation_status"] = "needs_manual_endpoint_discovery"
        row["recommended_status"] = "candidate" if page_url else "unknown"
        row["notes"] = (
            f"{base_notes}; api_url 未配置，跳过 API 请求"
        ).strip("; ")
        if page_url:
            try:
                resp = session.get(page_url, headers=PAGE_HEADERS, timeout=timeout, allow_redirects=True)
                row["http_status"] = str(resp.status_code)
                blocked, reason = _detect_blocked(resp.text[:8000])
                if blocked:
                    row["access_status"] = "blocked"
                    row["validation_status"] = "blocked"
                    row["recommended_status"] = "blocked"
                    if reason == "requires_login":
                        row["requires_login"] = "yes"
                    elif reason == "requires_captcha":
                        row["requires_captcha"] = "yes"
                    elif reason == "requires_paid_permission":
                        row["requires_paid_permission"] = "yes"
                    row["notes"] += f"; page 检测到 {reason}"
                elif resp.status_code == 200:
                    row["access_status"] = "page_reachable"
                    row["response_type"] = _infer_response_type(
                        resp.headers.get("Content-Type", ""), resp.text[:2000]
                    )
                else:
                    row["access_status"] = f"http_{resp.status_code}"
            except requests.RequestException as exc:
                row["access_status"] = "request_error"
                row["notes"] += f"; page 请求失败: {exc}"
        return row

    # --- api_url 非空：小样本请求 ---
    headers = dict(AJAX_HEADERS)
    if page_url:
        headers["Referer"] = str(page_url)
    try:
        if method == "GET":
            resp = session.get(api_url, params=params, headers=headers, timeout=timeout)
        elif params_location == "query":
            # POST with query string params and empty body (e.g. liftBan/detail?tdate=...)
            post_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
            resp = session.post(
                api_url, params=params, headers=post_headers, timeout=timeout
            )
        elif params_location == "none":
            # POST with no query params and empty body (e.g. marginTrading/detailList)
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
                row["access_status"] = "blocked"
                row["validation_status"] = "blocked"
                row["recommended_status"] = "blocked"
                if reason == "requires_login":
                    row["requires_login"] = "yes"
                elif reason == "requires_captcha":
                    row["requires_captcha"] = "yes"
                elif reason == "requires_paid_permission":
                    row["requires_paid_permission"] = "yes"
                row["notes"] = f"{base_notes}; API 响应提示 {reason}".strip("; ")
                return row

        row["response_type"] = response_type
        if resp.status_code != 200:
            row["access_status"] = f"http_{resp.status_code}"
            row["validation_status"] = "http_error"
            row["recommended_status"] = "partial"
            row["notes"] = f"{base_notes}; HTTP {resp.status_code}".strip("; ")
            return row

        row["access_status"] = "ok"
        row["requires_login"] = "no"
        row["requires_captcha"] = "no"
        row["requires_paid_permission"] = "no"
        records: List[Dict[str, Any]] = []
        observed_total_rows = ""
        observed_total_pages = ""
        if row["response_type"] == "json":
            if payload is None:
                try:
                    payload = resp.json()
                except json.JSONDecodeError:
                    row["validation_status"] = "invalid_json"
                    row["recommended_status"] = "partial"
                    row["notes"] = f"{base_notes}; 响应非合法 JSON".strip("; ")
                    return row
            observed_total_rows, observed_total_pages = _observed_meta_from_payload(payload)
            records = _extract_records(payload)
            keys = list(records[0].keys()) if records else _flatten_keys(payload)
        else:
            keys = []
            if row["response_type"] == "html_table":
                row["validation_status"] = "html_table_needs_parser"
                row["recommended_status"] = "candidate"
                row["notes"] = f"{base_notes}; HTML 表格需单独解析器".strip("; ")
                return row

        row["sample_rows"] = str(len(records))
        code_ok, date_ok, amount_ok = _field_hints_available(keys)
        expected = list(source.get("expected_fields") or [])
        if records and expected:
            record_keys = set(records[0].keys())
            matched = [f for f in expected if f in record_keys]
            row["field_count"] = str(len(matched))
            row["key_fields"] = "|".join(matched)
            dim_code, dim_date, dim_amount = _dimension_flags_from_record_keys(record_keys)
            row["company_code_available"] = dim_code if dim_code == "yes" else code_ok
            row["date_available"] = dim_date if dim_date == "yes" else date_ok
            row["amount_available"] = dim_amount if dim_amount == "yes" else amount_ok
            detail_val = records[0].get("detail")
            if "detail" in record_keys:
                row["nested_detail_available"] = (
                    "yes" if isinstance(detail_val, list) and len(detail_val) > 0 else "partial"
                )
            else:
                row["nested_detail_available"] = "no"
        else:
            row["field_count"] = str(len(keys))
            row["key_fields"] = "|".join(keys[:30])
            row["company_code_available"] = code_ok
            row["date_available"] = date_ok
            row["amount_available"] = amount_ok
            row["nested_detail_available"] = "unknown"

        if records and int(row["sample_rows"]) > 0:
            row["validation_status"] = "sample_ok"
            config_status = str(source.get("recommended_status", ""))
            if config_status in ("testing", "candidate", "partial"):
                row["recommended_status"] = config_status
            elif code_ok == "yes" and date_ok == "yes":
                row["recommended_status"] = "testing"
            else:
                row["recommended_status"] = "candidate"
        else:
            row["validation_status"] = "empty_sample"
            row["recommended_status"] = "partial"
        note_parts = [base_notes]
        if observed_total_rows:
            note_parts.append(f"observed_total_rows={observed_total_rows}")
        if observed_total_pages:
            note_parts.append(f"observed_total_pages={observed_total_pages}")
        row["notes"] = "; ".join(p for p in note_parts if p)
        return row

    except requests.RequestException as exc:
        row["access_status"] = "request_error"
        row["validation_status"] = "request_error"
        row["recommended_status"] = "partial"
        row["notes"] = f"{base_notes}; 请求异常: {exc}".strip("; ")
        return row


def write_csv(rows: List[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    rows: List[Dict[str, str]],
    path: str,
    *,
    config_path: str,
    dry_run: bool,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    status_counts = Counter(r["recommended_status"] for r in rows)
    validation_counts = Counter(r["validation_status"] for r in rows)
    with_api = [r for r in rows if r.get("api_url")]
    without_api = [r for r in rows if not r.get("api_url")]
    blocked = [r for r in rows if r["recommended_status"] == "blocked"]
    needs_discovery = [
        r for r in rows
        if r["validation_status"] == "needs_manual_endpoint_discovery"
    ]

    lines = [
        "# CNINFO D 类固定表格数据源验证摘要",
        "",
        f"- 生成时间：{_now_iso()}",
        f"- 配置：{os.path.relpath(config_path, BASE_DIR)}",
        f"- 脚本：`lab/validate_cninfo_table_sources.py`",
        f"- 计划：[cninfo_table_sources_phase2_plan.md](cninfo_table_sources_phase2_plan.md)",
        f"- 模式：**{'dry-run（未联网 API 探测）' if dry_run else 'live 小样本'}**",
        "",
        "---",
        "",
        "## 1. 本次验证范围",
        "",
        "- **层级**：D 类固定表格 / 市场行为",
        "- **目标**：入口探测、字段盘点、可用性分类",
        "- **非目标**：全量抓取、入库、生产化",
        "",
        "## 2. source 总数",
        "",
        f"- **配置 source 数**：**{len(rows)}**",
        "",
        "## 3. recommended_status 分布",
        "",
        "| recommended_status | 数量 |",
        "|--------------------|------|",
    ]
    for status in ("testing", "candidate", "partial", "blocked", "unknown"):
        lines.append(f"| {status} | {status_counts.get(status, 0)} |")

    lines.extend([
        "",
        "## 4. validation_status 分布",
        "",
        "| validation_status | 数量 |",
        "|-------------------|------|",
    ])
    for vs, cnt in sorted(validation_counts.items()):
        lines.append(f"| {vs} | {cnt} |")

    lines.extend([
        "",
        "## 5. api_url 配置情况",
        "",
        f"- **已配置 api_url**：{len(with_api)}",
        f"- **api_url 为空（待 DevTools）**：{len(without_api)}",
        "",
    ])
    if with_api:
        lines.append("已有 api_url 的 source：")
        for r in with_api:
            lines.append(f"- `{r['source_id']}` → `{r['api_url']}`")
        lines.append("")
    else:
        lines.append("当前 **无** source 配置 api_url；全部待手工 endpoint discovery。\n")

    lines.extend([
        "## 6. 需手工 DevTools endpoint discovery",
        "",
    ])
    if needs_discovery:
        for r in needs_discovery:
            lines.append(f"- **{r['source_id']}**（{r['source_name']}）— page: `{r['page_url']}`")
    else:
        lines.append("- （无）")
    lines.append("")

    lines.extend([
        "## 7. blocked source",
        "",
    ])
    if blocked:
        for r in blocked:
            lines.append(
                f"- **{r['source_id']}**：{r['notes']}"
            )
    else:
        lines.append("- 本次 **未发现** blocked source（或未执行 live 验证）。")
    lines.append("")

    lines.extend([
        "## 8. 各 source 字段价值（来自配置 expected_fields）",
        "",
        "| source_id | 中文名 | 关键维度 | 配置 priority | recommended_status |",
        "|-----------|--------|----------|---------------|-------------------|",
    ])
    # reload expected fields from rows only - use notes in table
    for r in rows:
        lines.append(
            f"| {r['source_id']} | {r['source_name']} | "
            f"见 config expected_fields | — | {r['recommended_status']} |"
        )

    lines.extend([
        "",
        "## 9. 逐 source 结果",
        "",
        "| source_id | validation_status | access_status | http_status | sample_rows | recommended_status |",
        "|-----------|-------------------|---------------|-------------|-------------|-------------------|",
    ])
    for r in rows:
        lines.append(
            f"| {r['source_id']} | {r['validation_status']} | {r['access_status']} | "
            f"{r['http_status'] or '—'} | {r['sample_rows'] or '—'} | {r['recommended_status']} |"
        )

    lines.extend([
        "",
        "## 10. 下一步建议",
        "",
        "1. **DevTools 抓 XHR**（priority-2）：`szse_calendar` / `equity_pledge` / `shareholder_change` 等",
        "2. **回填** `config/cninfo_table_sources.yaml` 的 `api_url` 与 `params_template`",
        "3. **本地小样本 live 跑**：`python lab/validate_cninfo_table_sources.py --source-id <id>`",
        "4. 遇登录 / 验证码 / 付费 → 标 `blocked`，不绕过",
        "5. 字段可得性达标后，将 D 类状态从 `candidate` 提升至 `testing`",
        "6. **暂缓全市场**；Phase 1 A 类 BSE residual 作为 later improvement",
        "",
        "## 11. 边界",
        "",
        "- 不登录；不绕过权限；不大规模请求；不入库",
        "- 不写 **verified**",
        "- 仅代表配置与小样本探测，非全市场结论",
        "",
    ])

    ds = next((r for r in rows if r["source_id"] == "disclosure_schedule"), None)
    if ds and ds.get("validation_status") == "sample_ok":
        obs_total = ""
        for part in (ds.get("notes") or "").split(";"):
            part = part.strip()
            if part.startswith("observed_total_rows="):
                obs_total = part.split("=", 1)[1]
        lines.extend([
            "## 12. disclosure_schedule 小样本验证（getPrbookInfo）",
            "",
            "- **公开 JSON endpoint 已确认**：`https://www.cninfo.com.cn/new/information/getPrbookInfo`",
            f"- **HTTP status**：**{ds.get('http_status', '—')}**",
            f"- **sample_rows**（page 1, pagesize 20）：**{ds.get('sample_rows', '—')}**",
            f"- **observed_total_rows**：**{obs_total or '见 notes'}**",
            f"- **field_count**：**{ds.get('field_count', '—')}**",
            f"- **key_fields**：`{ds.get('key_fields', '—')}`",
            f"- **company_code_available**：**{ds.get('company_code_available', '—')}**",
            f"- **date_available**：**{ds.get('date_available', '—')}**",
            f"- **requires_login**：**{ds.get('requires_login', '—')}**",
            f"- **requires_captcha**：**{ds.get('requires_captcha', '—')}**",
            f"- **requires_paid_permission**：**{ds.get('requires_paid_permission', '—')}**",
            f"- **recommended_status**：**{ds.get('recommended_status', '—')}**",
            "",
            "**字段语义待确认：**",
            "- `f001d_0102` 疑似报告期 / section date",
            "- `f002d_0102` 与 `f006d_0102` 疑似预约 / 当前披露日，二者区别待确认",
            "- `f003d_0102` / `f004d_0102` / `f005d_0102` 疑似变更日期相关字段",
            "- 不写 verified；不代表全市场稳定性",
            "",
        ])

    rsu = next((r for r in rows if r["source_id"] == "restricted_shares_unlock"), None)
    if rsu and rsu.get("validation_status") == "sample_ok":
        obs_total = ""
        for part in (rsu.get("notes") or "").split(";"):
            part = part.strip()
            if part.startswith("observed_total_rows="):
                obs_total = part.split("=", 1)[1]
        lines.extend([
            "## 13. restricted_shares_unlock 小样本验证（liftBan/detail）",
            "",
            "- **公开 JSON endpoint 已确认**：`https://www.cninfo.com.cn/data20/liftBan/detail`",
            "- **请求方式**：POST + query param `tdate=2026-06-08`，empty body",
            f"- **HTTP status**：**{rsu.get('http_status', '—')}**",
            f"- **sample_rows**（tdate=2026-06-08）：**{rsu.get('sample_rows', '—')}**",
            f"- **observed_total_rows**：**{obs_total or '见 notes'}**",
            f"- **field_count**：**{rsu.get('field_count', '—')}**",
            f"- **key_fields**：`{rsu.get('key_fields', '—')}`",
            f"- **company_code_available**：**{rsu.get('company_code_available', '—')}**",
            f"- **date_available**：**{rsu.get('date_available', '—')}**",
            f"- **amount_available**：**{rsu.get('amount_available', '—')}**",
            f"- **requires_login**：**{rsu.get('requires_login', '—')}**",
            f"- **requires_captcha**：**{rsu.get('requires_captcha', '—')}**",
            f"- **requires_paid_permission**：**{rsu.get('requires_paid_permission', '—')}**",
            f"- **recommended_status**：**{rsu.get('recommended_status', '—')}**",
            "",
            "**字段语义待确认：**",
            "- `F003D` 疑似解禁 / 上市流通日期",
            "- `F004N` 疑似解禁股份数量",
            "- `F005N` 疑似解禁比例（占总股本）",
            "- `F008N` 疑似实际可流通 / 本次可上市流通数量",
            "- 不写 verified；不代表全市场稳定性",
            "",
        ])

    bt = next((r for r in rows if r["source_id"] == "block_trade"), None)
    if bt and bt.get("validation_status") == "sample_ok":
        obs_total = ""
        for part in (bt.get("notes") or "").split(";"):
            part = part.strip()
            if part.startswith("observed_total_rows="):
                obs_total = part.split("=", 1)[1]
        lines.extend([
            "## 14. block_trade 小样本验证（ints/statistics）",
            "",
            "- **公开 JSON endpoint 已确认**：`https://www.cninfo.com.cn/data20/ints/statistics`",
            "- **请求方式**：POST + query param `tdate=2026-07-03`，empty body",
            "- **Referrer 页面**：`url=data/dzjy`（大宗交易）",
            f"- **HTTP status**：**{bt.get('http_status', '—')}**",
            f"- **sample_rows**（tdate=2026-07-03）：**{bt.get('sample_rows', '—')}**",
            f"- **observed_total_rows**：**{obs_total or '见 notes'}**",
            f"- **field_count**：**{bt.get('field_count', '—')}**",
            f"- **key_fields**：`{bt.get('key_fields', '—')}`",
            f"- **company_code_available**：**{bt.get('company_code_available', '—')}**",
            f"- **date_available**：**{bt.get('date_available', '—')}**",
            f"- **amount_available**：**{bt.get('amount_available', '—')}**",
            f"- **requires_login**：**{bt.get('requires_login', '—')}**",
            f"- **requires_captcha**：**{bt.get('requires_captcha', '—')}**",
            f"- **requires_paid_permission**：**{bt.get('requires_paid_permission', '—')}**",
            f"- **recommended_status**：**{bt.get('recommended_status', '—')}**",
            "",
            "**字段语义待确认：**",
            "- `F001N` 疑似成交笔数 / 次数",
            "- `F002N` 疑似成交量（单位待确认）",
            "- `F003N` 疑似成交金额（单位待确认）",
            "- `F004N` 疑似成交均价；样本中 F003N/F002N ≈ F004N",
            "- 不写 verified；不代表全市场稳定性",
            "",
        ])

    mt = next((r for r in rows if r["source_id"] == "margin_trading"), None)
    if mt and mt.get("validation_status") == "sample_ok":
        obs_total = ""
        for part in (mt.get("notes") or "").split(";"):
            part = part.strip()
            if part.startswith("observed_total_rows="):
                obs_total = part.split("=", 1)[1]
        lines.extend([
            "## 15. margin_trading 小样本验证（marginTrading/detailList）",
            "",
            "- **公开 JSON endpoint 已确认**：`https://www.cninfo.com.cn/data20/marginTrading/detailList`",
            "- **请求方式**：POST，empty body，无 query params（`params_location: none`）",
            "- **Referrer 页面**：`url=data/rzrq-zjlx`（融资融券）",
            f"- **HTTP status**：**{mt.get('http_status', '—')}**",
            f"- **sample_rows**（detailList 默认请求）：**{mt.get('sample_rows', '—')}**",
            f"- **observed_total_rows**：**{obs_total or '见 notes'}**",
            f"- **field_count**：**{mt.get('field_count', '—')}**",
            f"- **key_fields**：`{mt.get('key_fields', '—')}`",
            f"- **company_code_available**：**{mt.get('company_code_available', '—')}**",
            f"- **date_available**：**{mt.get('date_available', '—')}**",
            f"- **amount_available**：**{mt.get('amount_available', '—')}**",
            f"- **requires_login**：**{mt.get('requires_login', '—')}**",
            f"- **requires_captcha**：**{mt.get('requires_captcha', '—')}**",
            f"- **requires_paid_permission**：**{mt.get('requires_paid_permission', '—')}**",
            f"- **recommended_status**：**{mt.get('recommended_status', '—')}**",
            "",
            "**备注：** market 汇总接口 `marginTrading/market?tdate=...` 存在但未作本 task 主 source。",
            "",
            "**字段语义待确认：**",
            "- `F001N`–`F009N` 融资/融券余额、买入额、余量等具体含义与单位",
            "- `F010V` / `F011V` / `F012V` 疑似市场 / 板块 / 股票类型",
            "- 不写 verified；不代表全市场稳定性",
            "",
        ])

    at = next((r for r in rows if r["source_id"] == "abnormal_trading"), None)
    if at and at.get("validation_status") == "sample_ok":
        obs_total = ""
        obs_pages = ""
        for part in (at.get("notes") or "").split(";"):
            part = part.strip()
            if part.startswith("observed_total_rows="):
                obs_total = part.split("=", 1)[1]
            if part.startswith("observed_total_pages="):
                obs_pages = part.split("=", 1)[1]
        lines.extend([
            "## 16. abnormal_trading 小样本验证（getMarketStatisticsData）",
            "",
            "- **公开 JSON endpoint 已确认**：`https://www.cninfo.com.cn/data/statis/getMarketStatisticsData`",
            "- **请求方式**：POST + query params（sdate/edate/page/rows），empty body",
            "- **Referrer 页面**：`url=data/public-information`（公开信息）",
            f"- **HTTP status**：**{at.get('http_status', '—')}**",
            f"- **sample_rows**（page=1, rows=30）：**{at.get('sample_rows', '—')}**",
            f"- **observed_total_rows**：**{obs_total or '见 notes'}**",
            f"- **observed_total_pages**：**{obs_pages or '见 notes'}**",
            f"- **field_count**：**{at.get('field_count', '—')}**",
            f"- **key_fields**：`{at.get('key_fields', '—')}`",
            f"- **company_code_available**：**{at.get('company_code_available', '—')}**",
            f"- **date_available**：**{at.get('date_available', '—')}**",
            f"- **amount_available**：**{at.get('amount_available', '—')}**",
            f"- **nested_detail_available**：**{at.get('nested_detail_available', '—')}**",
            f"- **requires_login**：**{at.get('requires_login', '—')}**",
            f"- **requires_captcha**：**{at.get('requires_captcha', '—')}**",
            f"- **requires_paid_permission**：**{at.get('requires_paid_permission', '—')}**",
            f"- **recommended_status**：**{at.get('recommended_status', '—')}**",
            "",
            "**字段语义待确认：**",
            "- `type` 异常交易 / 公开信息类型",
            "- `buyTotal` / `sellTotal` / `buyPercent` / `sellPercent` 可能为空",
            "- `detail` 内营业部买卖金额字段语义待确认",
            "- 不写 verified；不代表全市场稳定性",
            "",
        ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CNINFO D-class fixed table source validation (Era C Phase 2)"
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help="Path to cninfo_table_sources.yaml",
    )
    parser.add_argument(
        "--output-prefix",
        default=DEFAULT_OUT_PREFIX,
        help="Output path prefix (without extension)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not send HTTP requests; emit config-only validation rows",
    )
    parser.add_argument(
        "--source-id",
        action="append",
        dest="source_ids",
        help="Validate only these source_id values (repeatable)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    defaults = config.get("defaults") or {}
    all_sources: List[Dict[str, Any]] = list(config.get("sources") or [])
    live_ids: Optional[set] = None
    if args.source_ids:
        live_ids = set(args.source_ids)
        sources = all_sources
    else:
        sources = all_sources

    sleep_sec = float(defaults.get("sleep_seconds") or SLEEP_SECONDS)
    out_csv = f"{args.output_prefix}_validation.csv"
    out_summary = f"{args.output_prefix}_validation_summary.md"

    session = requests.Session()
    rows: List[Dict[str, str]] = []
    total = len(sources)

    print(f"[{_now_iso()}] CNINFO D-class table source validation — {total} sources")
    if args.dry_run:
        print("[dry-run] No HTTP requests will be sent.")

    for i, source in enumerate(sources, 1):
        sid = source.get("source_id", "?")
        is_live = not args.dry_run and (live_ids is None or sid in live_ids)
        mode = "live" if is_live else "dry-run"
        print(f"[{i}/{total}] {sid} ({mode}) ...")
        row = validate_source(
            source, defaults, dry_run=not is_live, session=session
        )
        rows.append(row)
        if is_live and i < total:
            time.sleep(sleep_sec)

    write_csv(rows, out_csv)
    write_summary(
        rows,
        out_summary,
        config_path=args.config,
        dry_run=args.dry_run,
    )
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_summary}")


if __name__ == "__main__":
    main()
