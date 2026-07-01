"""
CNINFO F10 / 公司资料静态 HTML 轻量字段验证脚本（Issue #84，第三步）。

说明与边界：
- 本脚本仅定义流程，当前不自动运行、不联网，请在本地关闭 VPN 后手动执行：
  python lab/validate_cninfo_f10_static_html_fields.py
- 仅对 reachability 成功的页面做轻量 HTML 提取；不使用 BrowserUser；不做数据库/MinIO 接入；不保存完整 HTML。
- 需要 requests；若可用 beautifulsoup4（bs4）则优先；若未安装，脚本会退化为简易正则解析。

输入：
- outputs/validation/cninfo_f10_profile_page_reachability.csv（仅使用 validation_status=success 的记录）

输出（运行时生成）：
- outputs/validation/cninfo_f10_static_html_field_validation.csv
- outputs/validation/cninfo_f10_static_html_field_validation_summary.md
"""

from __future__ import annotations

import csv
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import requests

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:
    BeautifulSoup = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_f10_profile_page_reachability.csv")
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_f10_static_html_field_validation.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_f10_static_html_field_validation_summary.md")

SLEEP_SECONDS = 0.5
HTTP_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (compatible; CNINFO-F10-Validator/1.0)"

CSV_FIELDS = [
    "company_code",
    "company_name",
    "cninfo_stock_code",
    "cninfo_org_id",
    "cninfo_profile_url",
    "profile_url_rule",
    "http_status_code",
    "html_fetch_status",
    "stock_short_name",
    "industry",
    "listing_status",
    "company_profile",
    "main_business_summary",
    "registered_address",
    "office_address",
    "website",
    "contact_phone",
    "contact_email",
    "board_secretary",
    "field_obtained_count",
    "field_missing_count",
    "validation_status",
    "failure_reason",
    "access_method",
    "crawl_time",
    "notes",
]

TARGET_FIELDS = [
    "stock_short_name",
    "industry",
    "listing_status",
    "company_profile",
    "main_business_summary",
    "registered_address",
    "office_address",
    "website",
    "contact_phone",
    "contact_email",
    "board_secretary",
]

FAILURE_REASONS = {
    "success",
    "partial_fields_obtained",
    "no_static_fields_found",
    "js_render_required",
    "field_semantics_unclear",
    "http_404",
    "http_500",
    "http_403",
    "network_timeout",
    "captcha_or_login_required",
    "page_structure_changed",
    "unknown_error",
}


def ensure_dirs() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_success_entries() -> List[Dict]:
    rows = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            if r.get("validation_status") == "success":
                rows.append(r)
    return rows


def fetch_html(url: str) -> Tuple[str, int | None, str | None]:
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, timeout=HTTP_TIMEOUT, headers=headers)
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


def extract_with_regex(text: str, labels: List[str], max_len: int = 120) -> str:
    for label in labels:
        pattern = rf"{re.escape(label)}[:：]?\s*([\u4e00-\u9fa5A-Za-z0-9（）()、，。,.;；:/\-＿_ ]{{1,{max_len}}})"
        m = re.search(pattern, text)
        if m:
            return m.group(1).strip()
    return ""


def parse_fields(text: str) -> Dict:
    fields = {k: "" for k in TARGET_FIELDS}

    if BeautifulSoup:
        soup = BeautifulSoup(text, "html.parser")
        body_text = soup.get_text(" ", strip=True)
    else:
        body_text = re.sub(r"\s+", " ", text)

    fields["company_profile"] = extract_with_regex(body_text, ["公司简介", "公司概况"])
    fields["main_business_summary"] = extract_with_regex(body_text, ["主营业务", "主要业务"])
    fields["registered_address"] = extract_with_regex(body_text, ["注册地址"])
    fields["office_address"] = extract_with_regex(body_text, ["办公地址"])
    fields["website"] = extract_with_regex(body_text, ["公司网址", "公司网站", "官方网站"])
    fields["contact_phone"] = extract_with_regex(body_text, ["联系电话", "公司电话", "电话"])
    fields["contact_email"] = extract_with_regex(body_text, ["电子邮箱", "联系邮箱", "邮箱"])
    fields["board_secretary"] = extract_with_regex(body_text, ["董秘", "董事会秘书"])
    fields["industry"] = extract_with_regex(body_text, ["所属行业", "行业"])
    fields["listing_status"] = extract_with_regex(body_text, ["上市状态", "上市板块"])
    fields["stock_short_name"] = extract_with_regex(body_text, ["证券简称", "股票简称"])

    return fields


def decide_status(fields: Dict, has_keywords: bool, js_shell: bool) -> Tuple[str, str]:
    obtained = [k for k, v in fields.items() if v]
    core_hits = sum(1 for k in ["company_profile", "main_business_summary", "registered_address", "website"] if fields.get(k))

    if js_shell:
        return "failed", "js_render_required"
    if core_hits >= 2:
        return "success", "success"
    if obtained:
        return "partial", "partial_fields_obtained"
    return "failed", "no_static_fields_found"


def process_entry(entry: Dict) -> Dict:
    url = entry.get("cninfo_profile_url", "").strip()
    company_code = entry.get("company_code", "")
    company_name = entry.get("company_name", "")
    access_method = "HTTP"

    if not url:
        return base_row(entry, http_status="", html_status="not_attempted", failure="missing_profile_url", notes="profile_url empty")

    text, status, failure = fetch_html(url)
    if failure:
        return base_row(entry, http_status=status or "", html_status="error", failure=failure, notes="")

    lower = text.lower()
    has_keywords = any(k.lower() in lower for k in ["companyprofile", "公司概况", "公司资料", "主营业务", "注册地址", "办公地址"])
    js_shell = not has_keywords and len(text.strip()) < 200

    fields = parse_fields(text) if not js_shell else {k: "" for k in TARGET_FIELDS}
    obtained = sum(1 for v in fields.values() if v)
    missing = len(TARGET_FIELDS) - obtained
    validation_status, failure_reason = decide_status(fields, has_keywords, js_shell)

    return {
        "company_code": company_code,
        "company_name": company_name,
        "cninfo_stock_code": entry.get("cninfo_stock_code", ""),
        "cninfo_org_id": entry.get("cninfo_org_id", ""),
        "cninfo_profile_url": url,
        "profile_url_rule": entry.get("profile_url_rule", ""),
        "http_status_code": status or "",
        "html_fetch_status": "ok",
        "field_obtained_count": obtained,
        "field_missing_count": missing,
        "validation_status": validation_status,
        "failure_reason": failure_reason,
        "access_method": access_method,
        "crawl_time": now_iso(),
        "notes": "suspected JS shell" if js_shell else "",
        **fields,
    }


def base_row(entry: Dict, http_status: str | int, html_status: str, failure: str, notes: str) -> Dict:
    return {
        "company_code": entry.get("company_code", ""),
        "company_name": entry.get("company_name", ""),
        "cninfo_stock_code": entry.get("cninfo_stock_code", ""),
        "cninfo_org_id": entry.get("cninfo_org_id", ""),
        "cninfo_profile_url": entry.get("cninfo_profile_url", ""),
        "profile_url_rule": entry.get("profile_url_rule", ""),
        "http_status_code": http_status,
        "html_fetch_status": html_status,
        "stock_short_name": "",
        "industry": "",
        "listing_status": "",
        "company_profile": "",
        "main_business_summary": "",
        "registered_address": "",
        "office_address": "",
        "website": "",
        "contact_phone": "",
        "contact_email": "",
        "board_secretary": "",
        "field_obtained_count": 0,
        "field_missing_count": len(TARGET_FIELDS),
        "validation_status": "failed",
        "failure_reason": failure if failure in FAILURE_REASONS else "unknown_error",
        "access_method": "HTTP",
        "crawl_time": now_iso(),
        "notes": notes,
    }


def write_csv(rows: List[Dict]) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_summary(rows: List[Dict], input_count: int) -> None:
    total = len(rows)
    success = sum(1 for r in rows if r["validation_status"] == "success")
    partial = sum(1 for r in rows if r["validation_status"] == "partial")
    failed = sum(1 for r in rows if r["validation_status"] == "failed")

    def count_field(name: str) -> int:
        return sum(1 for r in rows if r.get(name))

    js_needed = sum(1 for r in rows if r.get("failure_reason") == "js_render_required")

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO F10 / 公司资料静态 HTML 字段验证（Issue #84）\n\n")
        fh.write("## 数据来源\n")
        fh.write(f"- 输入：{os.path.relpath(INPUT_CSV, BASE_DIR)}（仅 validation_status=success 的记录，数量：{input_count}）\n")
        fh.write("- 访问：CNINFO stock profile 页面 URL（/new/disclosure/stock?...#companyProfile）\n\n")

        fh.write("## 样本概况\n")
        fh.write(f"- 输入 success 页面数：{input_count}\n")
        fh.write(f"- 实际验证数：{total}\n")
        fh.write(f"- success：{success}\n")
        fh.write(f"- partial：{partial}\n")
        fh.write(f"- failed：{failed}\n\n")

        fh.write("## 字段可得性（按行计数）\n")
        for fld in TARGET_FIELDS:
            fh.write(f"- {fld}：{count_field(fld)}/{total}\n")
        fh.write("\n")

        fh.write("## 字段抽取观察\n")
        fh.write(f"- js_render_required：{js_needed}\n")
        fh.write("- 若核心字段缺失或仅有少量字段，则结果标记为 partial 或 failed。\n")
        fh.write("- 字段语义不清或无静态字段时，不做强行填充。\n\n")

        fh.write("## recommended_status（小样本）\n")
        if success > 0:
            fh.write("- 建议：testing / partial（静态 HTML 可提取部分字段），不代表长期稳定可用。\n")
        else:
            fh.write("- 建议：candidate（静态 HTML 信息不足，后续需 Playwright/映射补充）。\n")
        fh.write("\n")

        fh.write("## 边界确认\n")
        fh.write("- 未使用 BrowserUser；仅 HTTP + 轻量解析。\n")
        fh.write("- 未做数据库/MinIO 接入；未保存完整 HTML；未解析 PDF/OCR。\n")
        fh.write("- 请求需节流；结果受网络/VPN/映射影响，必要时人工重跑。\n")


def main() -> None:
    ensure_dirs()
    entries = load_success_entries()
    rows: List[Dict] = []
    for entry in entries:
        rows.append(process_entry(entry))
        time.sleep(SLEEP_SECONDS)

    write_csv(rows)
    write_summary(rows, len(entries))
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
