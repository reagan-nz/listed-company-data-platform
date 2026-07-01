"""
CNINFO F10 / 公司资料 Playwright 验证（Issue #84，第四步）。

对静态 HTML 无字段候选 + 页面可达性 partial（疑似 JS shell）页面做 Playwright 轻量字段检查。

说明与边界：
- 手动运行：python lab/validate_cninfo_f10_playwright_profile_fields.py
- 不使用 BrowserUser；不做数据库/MinIO 接入；不保存完整 HTML 快照。
- 需要：pip install playwright && playwright install chromium（脚本不会自动安装）

输入：
- outputs/validation/cninfo_f10_static_html_field_validation.csv
- outputs/validation/cninfo_f10_profile_page_reachability.csv

输出（运行时生成）：
- outputs/validation/cninfo_f10_playwright_profile_field_validation.csv
- outputs/validation/cninfo_f10_playwright_profile_field_validation_summary.md
"""

from __future__ import annotations

import csv
import os
import re
import time
from datetime import datetime, timezone
from typing import Dict, List, NamedTuple, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_HTML_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_f10_static_html_field_validation.csv")
REACHABILITY_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_f10_profile_page_reachability.csv")
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_f10_playwright_profile_field_validation.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_f10_playwright_profile_field_validation_summary.md")

SLEEP_SECONDS = 1.0
PAGE_TIMEOUT_MS = 20000
KEYWORD_WAIT_MS = 8000

PROFILE_URL_RULES = [
    "manual_rule_600_300_gssh0",
    "manual_rule_688_gshk",
    "manual_rule_bse_430017_to_920017",
]

SOURCE_STATIC = "static_html_no_fields"
SOURCE_REACHABILITY = "reachability_partial"

EXCLUDED_PROFILE_RULES = {"needs_orgid_mapping", "bse_orgid_required"}

KEYWORDS = [
    "companyProfile",
    "公司概况",
    "公司资料",
    "主营业务",
    "注册地址",
    "办公地址",
    "联系电话",
    "电子邮箱",
    "董秘",
]

CAPTCHA_HINTS = ["验证码", "请登录", "登录后", "无权访问", "access denied", "captcha"]

CSV_FIELDS = [
    "company_code",
    "company_name",
    "cninfo_stock_code",
    "cninfo_org_id",
    "cninfo_profile_url",
    "profile_url_rule",
    "sample_source",
    "playwright_status",
    "http_or_page_status",
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

CORE_FIELDS = ["company_profile", "main_business_summary", "registered_address", "website"]


class CandidateSelection(NamedTuple):
    static_html_count: int
    reachability_count: int
    merged_count: int
    duplicates_removed: int
    excluded_not_in_playwright: int
    samples: List[Dict]


def dedupe_key(row: Dict) -> Tuple[str, str]:
    return (row.get("company_code", ""), row.get("cninfo_profile_url", "").strip())


def should_exclude(row: Dict) -> Optional[str]:
    if not row.get("cninfo_profile_url", "").strip():
        return "missing_profile_url"
    rule = (row.get("profile_url_rule") or "").strip()
    if rule in EXCLUDED_PROFILE_RULES:
        return rule
    mapping = (row.get("mapping_status") or "").strip()
    if mapping == "needs_mapping":
        return "needs_mapping"
    org_id = (row.get("cninfo_org_id") or "").strip()
    if not org_id or org_id.lower() == "unknown":
        return "missing_org_id"
    return None


def normalize_entry(row: Dict, sample_source: str, notes: str = "") -> Dict:
    return {
        "company_code": row.get("company_code", ""),
        "company_name": row.get("company_name", ""),
        "cninfo_stock_code": row.get("cninfo_stock_code", ""),
        "cninfo_org_id": row.get("cninfo_org_id", ""),
        "cninfo_profile_url": row.get("cninfo_profile_url", "").strip(),
        "profile_url_rule": row.get("profile_url_rule", ""),
        "sample_source": sample_source,
        "notes": notes,
    }


def load_static_html_candidates() -> Tuple[List[Dict], int]:
    rows: List[Dict] = []
    excluded = 0
    with open(STATIC_HTML_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            if r.get("validation_status") != "failed":
                continue
            if r.get("failure_reason") != "no_static_fields_found":
                continue
            reason = should_exclude(r)
            if reason:
                excluded += 1
                continue
            rows.append(normalize_entry(r, SOURCE_STATIC))
    return rows, excluded


def load_reachability_candidates() -> Tuple[List[Dict], int]:
    rows: List[Dict] = []
    excluded = 0
    with open(REACHABILITY_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            if r.get("validation_status") != "partial":
                continue
            reason = should_exclude(r)
            if reason:
                excluded += 1
                continue
            rows.append(normalize_entry(r, SOURCE_REACHABILITY))
    return rows, excluded


def merge_candidates(static_rows: List[Dict], reachability_rows: List[Dict]) -> Tuple[List[Dict], int]:
    merged: Dict[Tuple[str, str], Dict] = {}
    duplicates_removed = 0

    for row in static_rows:
        merged[dedupe_key(row)] = row

    for row in reachability_rows:
        key = dedupe_key(row)
        if key in merged:
            duplicates_removed += 1
            existing = merged[key]
            note = "duplicate removed / source priority applied"
            if existing.get("notes"):
                existing["notes"] = f"{existing['notes']}; {note}"
            else:
                existing["notes"] = note
            continue
        merged[key] = row

    return list(merged.values()), duplicates_removed


def load_candidates() -> CandidateSelection:
    static_rows, static_excluded = load_static_html_candidates()
    reachability_rows, reachability_excluded = load_reachability_candidates()
    merged, duplicates_removed = merge_candidates(static_rows, reachability_rows)
    return CandidateSelection(
        static_html_count=len(static_rows),
        reachability_count=len(reachability_rows),
        merged_count=len(merged),
        duplicates_removed=duplicates_removed,
        excluded_not_in_playwright=static_excluded + reachability_excluded,
        samples=merged,
    )


def ensure_dirs() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_playwright() -> Tuple[bool, str]:
    try:
        import playwright  # noqa: F401
    except ImportError:
        return False, "playwright package not installed (pip install playwright)"
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        return False, "playwright sync_api unavailable"
    return True, ""


def extract_with_regex(text: str, labels: List[str], max_len: int = 120) -> str:
    for label in labels:
        pattern = rf"{re.escape(label)}[:：]?\s*([\u4e00-\u9fa5A-Za-z0-9（）()、，。,.;；:/\-＿_ ]{{1,{max_len}}})"
        m = re.search(pattern, text)
        if m:
            return m.group(1).strip()
    return ""


def parse_fields(text: str) -> Dict[str, str]:
    body = re.sub(r"\s+", " ", text)
    return {
        "stock_short_name": extract_with_regex(body, ["证券简称", "股票简称"]),
        "industry": extract_with_regex(body, ["所属行业", "行业"]),
        "listing_status": extract_with_regex(body, ["上市状态", "上市板块"]),
        "company_profile": extract_with_regex(body, ["公司简介", "公司概况"]),
        "main_business_summary": extract_with_regex(body, ["主营业务", "主要业务"]),
        "registered_address": extract_with_regex(body, ["注册地址"]),
        "office_address": extract_with_regex(body, ["办公地址"]),
        "website": extract_with_regex(body, ["公司网址", "公司网站", "官方网站"]),
        "contact_phone": extract_with_regex(body, ["联系电话", "公司电话", "电话"]),
        "contact_email": extract_with_regex(body, ["电子邮箱", "联系邮箱", "邮箱"]),
        "board_secretary": extract_with_regex(body, ["董秘", "董事会秘书"]),
    }


def decide_status(fields: Dict[str, str]) -> Tuple[str, str]:
    obtained = [k for k, v in fields.items() if v]
    core_hits = sum(1 for k in CORE_FIELDS if fields.get(k))
    if core_hits >= 2:
        return "success", "success"
    if obtained:
        return "partial", "partial_fields_obtained"
    return "failed", "no_fields_after_js_render"


def combine_notes(entry: Dict, extra: str) -> str:
    base = (entry.get("notes") or "").strip()
    extra = (extra or "").strip()
    if base and extra:
        return f"{base}; {extra}"
    return base or extra


def base_row(entry: Dict, playwright_status: str, page_status: str, failure: str, notes: str) -> Dict:
    return {
        "company_code": entry.get("company_code", ""),
        "company_name": entry.get("company_name", ""),
        "cninfo_stock_code": entry.get("cninfo_stock_code", ""),
        "cninfo_org_id": entry.get("cninfo_org_id", ""),
        "cninfo_profile_url": entry.get("cninfo_profile_url", ""),
        "profile_url_rule": entry.get("profile_url_rule", ""),
        "sample_source": entry.get("sample_source", ""),
        "playwright_status": playwright_status,
        "http_or_page_status": page_status,
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
        "failure_reason": failure,
        "access_method": "Playwright",
        "crawl_time": now_iso(),
        "notes": combine_notes(entry, notes),
    }


def process_sample(page, entry: Dict) -> Dict:
    url = entry.get("cninfo_profile_url", "").strip()
    try:
        response = page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
        page_status = str(response.status) if response else "unknown"

        for kw in KEYWORDS:
            try:
                page.get_by_text(kw, exact=False).first.wait_for(timeout=KEYWORD_WAIT_MS)
                break
            except Exception:
                continue

        page.wait_for_timeout(1000)
        body_text = page.locator("body").inner_text(timeout=5000)
        lower = body_text.lower()

        if any(h.lower() in lower for h in CAPTCHA_HINTS):
            return base_row(entry, "error", page_status, "captcha_or_login_required", "captcha/login hint detected")

        fields = parse_fields(body_text)
        obtained = sum(1 for v in fields.values() if v)
        missing = len(TARGET_FIELDS) - obtained
        validation_status, failure_reason = decide_status(fields)

        return {
            "company_code": entry.get("company_code", ""),
            "company_name": entry.get("company_name", ""),
            "cninfo_stock_code": entry.get("cninfo_stock_code", ""),
            "cninfo_org_id": entry.get("cninfo_org_id", ""),
            "cninfo_profile_url": url,
            "profile_url_rule": entry.get("profile_url_rule", ""),
            "sample_source": entry.get("sample_source", ""),
            "playwright_status": "ok",
            "http_or_page_status": page_status,
            "field_obtained_count": obtained,
            "field_missing_count": missing,
            "validation_status": validation_status,
            "failure_reason": failure_reason,
            "access_method": "Playwright",
            "crawl_time": now_iso(),
            "notes": entry.get("notes", ""),
            **fields,
        }
    except Exception as exc:
        msg = str(exc).lower()
        if "timeout" in msg:
            failure = "page_load_timeout"
        else:
            failure = "unknown_error"
        return base_row(entry, "error", "error", failure, str(exc)[:200])


def write_csv(rows: List[Dict]) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def status_stats(rows: List[Dict], key_field: str) -> Dict[str, Dict[str, int]]:
    stats: Dict[str, Dict[str, int]] = {}
    for r in rows:
        key = r.get(key_field) or "unknown"
        if key not in stats:
            stats[key] = {"total": 0, "success": 0, "partial": 0, "failed": 0}
        stats[key]["total"] += 1
        status = r.get("validation_status", "")
        if status in stats[key]:
            stats[key][status] += 1
    return stats


def write_summary_selection_section(fh, selection: CandidateSelection) -> None:
    fh.write("## 样本选择\n")
    fh.write(f"- static_html_no_fields 候选：{selection.static_html_count}\n")
    fh.write(f"- reachability_partial 候选：{selection.reachability_count}\n")
    fh.write(f"- 去重后实际验证：{selection.merged_count}\n")
    if selection.duplicates_removed:
        fh.write(f"- 去重移除：{selection.duplicates_removed}（优先保留 static_html_no_fields）\n")
    fh.write(f"- 未纳入 Playwright（mapping/orgId/空 URL 等）：{selection.excluded_not_in_playwright}\n")
    fh.write("- 明确未纳入：reachability failed、needs_orgid_mapping、bse_orgid_required、缺 orgId、profile_url 为空\n\n")


def write_summary_pending(playwright_ok: bool, playwright_msg: str, selection: CandidateSelection) -> None:
    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO F10 / 公司资料 Playwright 验证（Issue #84）\n\n")
        fh.write("本文件为待运行脚本说明；真实统计结果需在本地手动运行脚本后生成。\n\n")
        fh.write("## 数据来源\n")
        fh.write(f"- A：`{os.path.relpath(STATIC_HTML_CSV, BASE_DIR)}`（failed + no_static_fields_found）\n")
        fh.write(f"- B：`{os.path.relpath(REACHABILITY_CSV, BASE_DIR)}`（partial + profile_url 非空）\n\n")
        write_summary_selection_section(fh, selection)
        fh.write("## 运行方式\n")
        fh.write("```bash\npython lab/validate_cninfo_f10_playwright_profile_fields.py\n```\n\n")
        fh.write("依赖：\n")
        fh.write("- pip install playwright\n")
        fh.write("- playwright install chromium\n")
        fh.write("- 脚本不会自动安装 Playwright 或浏览器\n\n")
        if playwright_ok:
            fh.write("当前环境：Playwright 已检测到，可手动运行脚本。\n\n")
        else:
            fh.write(f"当前环境：Playwright 不可用（{playwright_msg}）。\n\n")
        fh.write("## 运行后统计项\n")
        fh.write("- 按 sample_source 统计 success / partial / failed\n")
        fh.write("- 按 profile_url_rule 统计 success / partial / failed\n")
        fh.write("- 各字段可得性\n\n")
        fh.write("## 边界确认\n")
        fh.write("- 未使用 BrowserUser。\n")
        fh.write("- 未绕过登录 / 验证码 / 权限。\n")
        fh.write("- 未做数据库 / MinIO 接入；未保存完整 HTML 快照。\n")
        fh.write("- 未修改 docs/data_sources.md 与 storage schema。\n")


def write_summary_results(rows: List[Dict], selection: CandidateSelection) -> None:
    total = len(rows)
    success = sum(1 for r in rows if r["validation_status"] == "success")
    partial = sum(1 for r in rows if r["validation_status"] == "partial")
    failed = sum(1 for r in rows if r["validation_status"] == "failed")

    def count_field(name: str) -> int:
        return sum(1 for r in rows if r.get(name))

    by_source = status_stats(rows, "sample_source")
    by_rule = status_stats(rows, "profile_url_rule")

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO F10 / 公司资料 Playwright 验证（Issue #84）\n\n")
        fh.write("## 数据来源\n")
        fh.write(f"- A：`{os.path.relpath(STATIC_HTML_CSV, BASE_DIR)}`\n")
        fh.write(f"- B：`{os.path.relpath(REACHABILITY_CSV, BASE_DIR)}`\n\n")
        write_summary_selection_section(fh, selection)
        fh.write("## 验证结果\n")
        fh.write(f"- 实际验证数：{total}\n")
        fh.write(f"- success：{success}\n")
        fh.write(f"- partial：{partial}\n")
        fh.write(f"- failed：{failed}\n\n")
        fh.write("## sample_source 分布\n")
        for source in [SOURCE_STATIC, SOURCE_REACHABILITY]:
            if source not in by_source:
                continue
            s = by_source[source]
            fh.write(f"- {source}：{s['total']} 家（success {s['success']} / partial {s['partial']} / failed {s['failed']}）\n")
        fh.write("\n")
        fh.write("## profile_url_rule 分布\n")
        for rule in PROFILE_URL_RULES + sorted(set(by_rule) - set(PROFILE_URL_RULES)):
            if rule not in by_rule:
                continue
            s = by_rule[rule]
            fh.write(f"- {rule}：{s['total']} 家（success {s['success']} / partial {s['partial']} / failed {s['failed']}）\n")
        fh.write("\n")
        fh.write("## 字段可得性（按行计数）\n")
        for fld in TARGET_FIELDS:
            fh.write(f"- {fld}：{count_field(fld)}/{total}\n")
        fh.write("\n")
        fh.write("## 当前结论\n")
        fh.write("- 静态 HTML 已不足以提取字段；本步用于判断 JS 渲染后是否可见。\n")
        fh.write("- 若仍无字段，需继续修正 entry mapping 或页面结构。\n\n")
        fh.write("## recommended_status（小样本）\n")
        if success > 0:
            fh.write("- 建议：testing / partial（Playwright 后可提取部分字段），不代表长期稳定可用。\n")
        else:
            fh.write("- 建议：candidate（Playwright 后仍不足，需继续排查）。\n")
        fh.write("\n")
        fh.write("## 边界确认\n")
        fh.write("- 未使用 BrowserUser。\n")
        fh.write("- 未绕过登录 / 验证码 / 权限。\n")
        fh.write("- 未做数据库 / MinIO 接入；未保存完整 HTML 快照。\n")


def main() -> None:
    ensure_dirs()
    selection = load_candidates()
    samples = selection.samples

    playwright_ok, playwright_msg = check_playwright()
    if not playwright_ok:
        write_csv([])
        write_summary_pending(playwright_ok, playwright_msg, selection)
        print(f"Playwright not available: {playwright_msg}")
        print("Install with: pip install playwright && playwright install chromium")
        print(f"Prepared header-only CSV -> {OUT_CSV}")
        print(f"Candidates: static={selection.static_html_count}, reachability={selection.reachability_count}, merged={selection.merged_count}")
        return

    from playwright.sync_api import sync_playwright

    rows: List[Dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for entry in samples:
            rows.append(process_sample(page, entry))
            time.sleep(SLEEP_SECONDS)
        browser.close()

    write_csv(rows)
    write_summary_results(rows, selection)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")
    print(f"Candidates: static={selection.static_html_count}, reachability={selection.reachability_count}, merged={selection.merged_count}")


if __name__ == "__main__":
    main()
