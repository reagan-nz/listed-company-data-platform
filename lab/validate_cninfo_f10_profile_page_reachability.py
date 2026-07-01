"""
CNINFO F10 / 公司资料页面可达性小样本验证（Issue #84，第二轮）。

Inputs:
- outputs/validation/cninfo_f10_entry_mapping.csv

Outputs:
- outputs/validation/cninfo_f10_profile_page_reachability.csv
- outputs/validation/cninfo_f10_profile_page_reachability_summary.md

Scope:
- 仅验证 companyProfile 页面可达性与轻量关键词，不做字段抽取/数据库/存储。
- 不使用 BrowserUser；HTTP GET + 轻量文本检查；请求间 sleep。
"""

from __future__ import annotations

import csv
import os
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_f10_entry_mapping.csv")
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_f10_profile_page_reachability.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_f10_profile_page_reachability_summary.md")

SLEEP_SECONDS = 0.5

CSV_FIELDS = [
    "company_code",
    "company_name",
    "exchange",
    "board",
    "cninfo_stock_code",
    "cninfo_org_id",
    "cninfo_profile_url",
    "profile_url_rule",
    "mapping_status",
    "http_status_code",
    "page_access_status",
    "has_company_profile_anchor",
    "has_company_name_in_page",
    "has_company_profile_keywords",
    "js_render_required",
    "validation_status",
    "failure_reason",
    "access_method",
    "crawl_time",
    "notes",
]

FAILURE_REASONS = {
    "success",
    "partial_js_shell",
    "missing_profile_url",
    "http_404",
    "http_500",
    "http_403",
    "network_timeout",
    "captcha_or_login_required",
    "page_structure_changed",
    "missing_company_profile_keywords",
    "needs_orgid_mapping",
    "bse_mapping_incomplete",
    "unknown_error",
}


def ensure_dirs() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_entries() -> List[Dict]:
    rows = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def fetch_page(url: str) -> Tuple[str, int | None, str | None]:
    try:
        resp = requests.get(url, timeout=10)
        status = resp.status_code
        text = resp.text or ""
        if status == 403:
            return text, status, "http_403"
        if status == 404:
            return text, status, "http_404"
        if status >= 500:
            return text, status, "http_500"
        if status != 200:
            return text, status, "unknown_error"
        return text, status, None
    except requests.exceptions.Timeout:
        return "", None, "network_timeout"
    except Exception:
        return "", None, "unknown_error"


KEYWORDS = ["companyprofile", "公司概况", "公司资料", "主营业务", "注册地址", "办公地址"]


def analyze_page(text: str, company_name: str) -> Tuple[bool, bool, bool, bool]:
    lower = text.lower()
    has_anchor = "#companyprofile" in text.lower() or "companyprofile" in lower
    has_keywords = any(k.lower() in lower for k in KEYWORDS)
    has_name = company_name and company_name in text
    # If no keywords and no name, likely JS shell
    js_render_required = not has_keywords and not has_name
    return has_anchor, has_name, has_keywords, js_render_required


def process_entry(entry: Dict) -> Dict:
    company_code = entry.get("company_code", "").strip()
    company_name = entry.get("company_name", "").strip()
    exchange = entry.get("exchange", "").strip()
    board = entry.get("board", "").strip()
    cninfo_stock_code = entry.get("cninfo_stock_code", "").strip()
    cninfo_org_id = entry.get("cninfo_org_id", "").strip()
    cninfo_profile_url = entry.get("cninfo_profile_url", "").strip()
    profile_url_rule = entry.get("profile_url_rule", "").strip()
    mapping_status = entry.get("mapping_status", "").strip()

    access_method = "HTTP"
    if not cninfo_profile_url:
        return {
            "company_code": company_code,
            "company_name": company_name,
            "exchange": exchange,
            "board": board,
            "cninfo_stock_code": cninfo_stock_code,
            "cninfo_org_id": cninfo_org_id,
            "cninfo_profile_url": cninfo_profile_url,
            "profile_url_rule": profile_url_rule,
            "mapping_status": mapping_status,
            "http_status_code": "",
            "page_access_status": "not_attempted",
            "has_company_profile_anchor": "false",
            "has_company_name_in_page": "false",
            "has_company_profile_keywords": "false",
            "js_render_required": "unknown",
            "validation_status": "failed",
            "failure_reason": "missing_profile_url",
            "access_method": access_method,
            "crawl_time": now_iso(),
            "notes": "profile_url empty; needs orgId mapping" if "needs" in profile_url_rule or "required" in profile_url_rule else "",
        }

    text, status, failure = fetch_page(cninfo_profile_url)
    has_anchor, has_name, has_keywords, js_render_required = analyze_page(text, company_name)

    if failure:
        failure_reason = failure if failure in FAILURE_REASONS else "unknown_error"
        validation_status = "failed"
    else:
        if has_name or has_keywords:
            failure_reason = "success"
            validation_status = "success"
        else:
            failure_reason = "partial_js_shell"
            validation_status = "partial"

    notes = ""
    if js_render_required and failure_reason != "success":
        notes = "page may need JS rendering"

    return {
        "company_code": company_code,
        "company_name": company_name,
        "exchange": exchange,
        "board": board,
        "cninfo_stock_code": cninfo_stock_code,
        "cninfo_org_id": cninfo_org_id,
        "cninfo_profile_url": cninfo_profile_url,
        "profile_url_rule": profile_url_rule,
        "mapping_status": mapping_status,
        "http_status_code": status or "",
        "page_access_status": "ok" if status == 200 else "error",
        "has_company_profile_anchor": str(has_anchor).lower(),
        "has_company_name_in_page": str(has_name).lower(),
        "has_company_profile_keywords": str(has_keywords).lower(),
        "js_render_required": str(js_render_required).lower(),
        "validation_status": validation_status,
        "failure_reason": failure_reason,
        "access_method": access_method,
        "crawl_time": now_iso(),
        "notes": notes,
    }


def write_csv(rows: List[Dict]) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_summary(rows: List[Dict]) -> None:
    total_entries = len(rows)
    success = sum(1 for r in rows if r["validation_status"] == "success")
    partial = sum(1 for r in rows if r["validation_status"] == "partial")
    failed = sum(1 for r in rows if r["validation_status"] == "failed")

    rule_counter = Counter(r.get("profile_url_rule") for r in rows)
    status_by_rule = defaultdict(Counter)
    for r in rows:
        status_by_rule[r.get("profile_url_rule")][r["validation_status"]] += 1

    http_200 = sum(1 for r in rows if r.get("http_status_code") == 200 or r.get("http_status_code") == "200")
    http_404 = sum(1 for r in rows if r.get("failure_reason") == "http_404")
    http_500 = sum(1 for r in rows if r.get("failure_reason") == "http_500")
    timeout = sum(1 for r in rows if r.get("failure_reason") == "network_timeout")
    js_needed = sum(1 for r in rows if r.get("js_render_required") == "true")
    keywords_ok = sum(1 for r in rows if r.get("has_company_profile_keywords") == "true")
    name_ok = sum(1 for r in rows if r.get("has_company_name_in_page") == "true")

    needs_orgid = sum(1 for r in rows if r.get("failure_reason") in ("missing_profile_url", "needs_orgid_mapping", "bse_mapping_incomplete"))

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO F10 / 公司资料页面可达性验证（Issue #84 第二轮）\n\n")
        fh.write("## 数据来源\n")
        fh.write(f"- 输入：{os.path.relpath(INPUT_CSV, BASE_DIR)}\n")
        fh.write("- 访问：CNINFO stock profile 页面 URL（/new/disclosure/stock?...#companyProfile）\n\n")

        fh.write("## 样本概况\n")
        fh.write(f"- entry mapping 总数：{total_entries}\n")
        fh.write(f"- 成功：{success}\n")
        fh.write(f"- partial：{partial}\n")
        fh.write(f"- failed：{failed}\n\n")

        fh.write("## 按规则类型统计\n")
        for rule, cnt in rule_counter.items():
            succ = status_by_rule[rule]["success"]
            part = status_by_rule[rule]["partial"]
            fail = status_by_rule[rule]["failed"]
            fh.write(f"- {rule}: total {cnt}, success {succ}, partial {part}, failed {fail}\n")
        fh.write("\n")

        fh.write("## 可达性结果\n")
        fh.write(f"- HTTP 200：{http_200}/{total_entries}\n")
        fh.write(f"- 404：{http_404}\n")
        fh.write(f"- 500：{http_500}\n")
        fh.write(f"- timeout：{timeout}\n")
        fh.write(f"- 需要 JS 渲染（无关键词且无公司名）：{js_needed}\n")
        fh.write(f"- 含公司资料关键词：{keywords_ok}\n")
        fh.write(f"- 含公司名称：{name_ok}\n")
        fh.write(f"- 缺 orgId/映射待补充：{needs_orgid}\n\n")

        fh.write("## 北交所 / 代码映射观察\n")
        fh.write("- 430/920 映射仅对 430017→920017 有样例，其余 430 需补 orgId 后再测；本轮未泛化。\n\n")

        fh.write("## 当前结论\n")
        fh.write("- 若页面 200 且含关键词，可进入后续轻量 HTML 抽取验证；若 200 但无内容，考虑 JS 渲染（Playwright 备用）。\n")
        fh.write("- 若大量 500/超时，需继续修正 orgId / stockCode 映射或检查网络环境。\n\n")

        fh.write("## recommended_status（小样本）\n")
        if success > 0:
            fh.write("- 建议：testing / partial（小样本继续验证），不代表长期稳定可用。\n")
        else:
            fh.write("- 建议：candidate（入口可达性需进一步排查后再测）。\n")
        fh.write("\n")

        fh.write("## 合规与边界确认\n")
        fh.write("- 未绕过登录/验证码/付费/权限。\n")
        fh.write("- 未使用 BrowserUser；未做数据库/MinIO 接入。\n")
        fh.write("- 未做字段抽取，仅做可达性与轻量关键词检查。\n")
        fh.write("- 请求间加入 sleep，避免高频访问。\n")


def main() -> None:
    ensure_dirs()
    entries = load_entries()
    rows: List[Dict] = []
    for entry in entries:
        if not entry.get("cninfo_profile_url"):
            rows.append(process_entry(entry))
            continue
        rows.append(process_entry(entry))
        time.sleep(SLEEP_SECONDS)

    write_csv(rows)
    write_summary(rows)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
