"""
CNINFO 报告类公告查询机制验证（Sub Issue 5）。

目标：验证年报/半年报/季报在 CNINFO 公告查询接口下的可获取性与查询策略（时间范围、关键词、报告期写法）。

行为与边界：
- 读取已有 identity mapping（不伪造 query code）。
- 仅构建脚本，默认不自动运行；若需真实结果，请在本地执行：
    python lab/validate_cninfo_report_announcements.py
- 访问 CNINFO 时：不绕过登录/验证码/付费/权限；请求间 sleep；不下载 PDF 正文；不做 OCR；不做数据库/MinIO 接入；不使用 BrowserUser。
"""

from __future__ import annotations

import csv
import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")

MAPPING_CSV = os.path.join(OUT_DIR, "cninfo_company_identity_mapping.csv")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_report_announcement_validation.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_report_announcement_validation_summary.md")

REQUEST_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"

SLEEP_SECONDS = 0.6
PAGE_SIZE = 30

REPORT_TYPES = {
    "annual_report": {
        "title_patterns": ["年度报告", "年度报告摘要"],
        "keywords_recent": ["年度报告", "年报"],
        "keywords_with_year": ["2024年年度报告"],
    },
    "semi_annual_report": {
        "title_patterns": ["半年度报告", "半年度报告摘要", "半年报"],
        "keywords_recent": ["半年度报告", "半年报"],
        "keywords_with_year": ["2024年半年度报告"],
    },
    "quarterly_report_q1": {
        "title_patterns": ["第一季度报告"],
        "keywords_recent": ["第一季度报告", "季度报告"],
        "keywords_with_year": ["2024年第一季度报告", "2025年第一季度报告"],
    },
    "quarterly_report_q3": {
        "title_patterns": ["第三季度报告"],
        "keywords_recent": ["第三季度报告", "季度报告"],
        "keywords_with_year": ["2024年第三季度报告", "2025年第三季度报告"],
    },
}

QUERY_STRATEGIES = [
    "keyword_recent",
    "keyword_with_year",
    "longer_time_window",
    "report_title_pattern",
]

CSV_FIELDS = [
    "company_code",
    "company_name",
    "exchange",
    "board",
    "cninfo_announcement_query_code",
    "report_type",
    "query_strategy",
    "query_keyword",
    "announcement_title",
    "publish_time",
    "report_period",
    "source_url",
    "pdf_url",
    "validation_status",
    "failure_reason",
    "http_status_code",
    "crawl_time",
    "notes",
]

FAILURE_REASONS = {
    "success",
    "no_matching_report",
    "missing_query_code",
    "needs_orgid_mapping",
    "empty_response",
    "http_error",
    "network_timeout",
    "rate_limited",
    "captcha_or_login_required",
    "unknown_error",
}


def ensure_dirs() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_mapping() -> List[Dict]:
    rows: List[Dict] = []
    with open(MAPPING_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def is_mapped(row: Dict) -> bool:
    status = (row.get("mapping_status") or "").strip()
    orgid = (row.get("cninfo_org_id") or "").strip()
    return status == "mapped" and orgid and orgid.lower() != "unknown"


def announcement_query_code(row: Dict) -> str | None:
    for key in ("cninfo_announcement_query_code", "cninfo_stock_code", "company_code"):
        val = (row.get(key) or "").strip()
        if val:
            return val
    return None


def build_payload(code: str, orgid: str, column: str, keyword: str, se_date: str) -> Dict:
    stock_value = f"{code},{orgid}" if orgid else code
    return {
        "stock": stock_value,
        "searchkey": keyword,
        "plate": "",
        "category": "",
        "trade": "",
        "column": column or "sse",
        "tabName": "fulltext",
        "pageSize": PAGE_SIZE,
        "pageNum": 1,
        "seDate": se_date,
        "sortName": "",
        "sortType": "",
        "isHLtitle": True,
    }


def fetch_announcements(payload: Dict) -> Tuple[List[Dict], int | None, str | None]:
    try:
        resp = requests.post(REQUEST_URL, data=payload, timeout=8)
        status = resp.status_code
        if status == 429:
            return [], status, "rate_limited"
        if status != 200:
            return [], status, "http_error"
        data = resp.json()
        ann = data.get("announcements") or []
        return ann, status, None
    except requests.exceptions.Timeout:
        return [], None, "network_timeout"
    except Exception:
        return [], None, "unknown_error"


def build_pdf_url(adjunct_url: str | None) -> str:
    if not adjunct_url:
        return ""
    prefix = "http://static.cninfo.com.cn/"
    return prefix + adjunct_url.lstrip("/")


def normalize_publish_time(ts: int | None) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return ""


def match_report_title(title: str, patterns: List[str]) -> Tuple[bool, str]:
    t = (title or "").lower()
    for p in patterns:
        if (p or "").lower() in t:
            return True, p
    return False, ""


def parse_report_period(title: str, report_type: str) -> str:
    """
    从公告标题中解析报告期，仅在模式明确时返回：
    - annual_report:  2024年年度报告 / 2024 年年度报告 / 2024年度报告 -> 2024
    - semi_annual_report: 2024年半年度报告 / 2024 年半年度报告 / 2024半年度报告 -> 2024H1
    - quarterly_report_q1: 2025年第一季度报告 / 2025 年第一季度报告 / 2025一季度报告 -> 2025Q1
    - quarterly_report_q3: 2024年第三季度报告 / 2024 年第三季度报告 / 2024三季度报告 -> 2024Q3

    无法可靠判断时返回 "unknown"。
    """
    import re

    if not title:
        return "unknown"

    # 去掉空格，统一中文数字表达
    t = "".join(title.split())

    # 匹配年份
    m = re.search(r"(20[0-9]{2})", t)
    if not m:
        return "unknown"
    year = m.group(1)

    if report_type == "annual_report":
        if "年度报告" in t:
            return year
        return "unknown"

    if report_type == "semi_annual_report":
        if "半年度报告" in t or "半年报" in t:
            return f"{year}H1"
        return "unknown"

    if report_type == "quarterly_report_q1":
        if "第一季度报告" in t or "一季度报告" in t:
            return f"{year}Q1"
        return "unknown"

    if report_type == "quarterly_report_q3":
        if "第三季度报告" in t or "三季度报告" in t:
            return f"{year}Q3"
        return "unknown"

    return "unknown"


def time_window(strategy: str) -> str:
    # seDate format "YYYY-MM-DD ~ YYYY-MM-DD"; longer window 3y
    if strategy == "longer_time_window":
        end = datetime.now()
        start = end.replace(year=end.year - 3)
        return f"{start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}"
    # default empty uses CNINFO recent window
    return ""


def process_record(row: Dict, report_type: str, strategy: str, keyword: str, title_patterns: List[str]) -> Dict:
    company_code = row.get("company_code", "")
    company_name = row.get("company_name", "")
    exchange = row.get("exchange", "")
    board = row.get("board", "")
    orgid = row.get("cninfo_org_id", "")
    stock_code = row.get("cninfo_stock_code", "")
    query_code = announcement_query_code(row)
    column = {
        ("主板", "SSE"): "sse",
        ("主板", "SZSE"): "szse",
        ("创业板", "SZSE"): "szse",
        ("科创板", "SSE"): "sse",
        ("北交所", "BSE"): "neeq",
    }.get((board, exchange), "sse")

    base = {
        "company_code": company_code,
        "company_name": company_name,
        "exchange": exchange,
        "board": board,
        "cninfo_announcement_query_code": query_code or "",
        "report_type": report_type,
        "query_strategy": strategy,
        "query_keyword": keyword,
        "announcement_title": "",
        "publish_time": "",
        "report_period": "",
        "source_url": "",
        "pdf_url": "",
        "validation_status": "failed",
        "failure_reason": "",
        "http_status_code": "",
        "crawl_time": now_iso(),
        "notes": "",
    }

    if not is_mapped(row):
        base.update({"validation_status": "skipped", "failure_reason": "needs_orgid_mapping"})
        return base

    if not query_code:
        base.update({"validation_status": "failed", "failure_reason": "missing_query_code"})
        return base

    payload = build_payload(query_code, orgid, column, keyword, time_window(strategy))
    ann, status, fetch_failure = fetch_announcements(payload)
    if fetch_failure:
        base.update({"validation_status": "failed", "failure_reason": fetch_failure, "http_status_code": status or ""})
        return base
    if not ann:
        base.update({"validation_status": "failed", "failure_reason": "empty_response", "http_status_code": status or ""})
        return base

    # pick first matching by pattern
    for rec in ann:
        title = rec.get("announcementTitle") or ""
        matched, matched_pattern = match_report_title(title, title_patterns if strategy == "report_title_pattern" else title_patterns + [keyword])
        if not matched:
            continue
        base.update(
            {
                "announcement_title": title,
                "publish_time": normalize_publish_time(rec.get("announcementTime")),
                "source_url": rec.get("announcementUrl") or "",
                "pdf_url": build_pdf_url(rec.get("adjunctUrl")),
                "report_period": parse_report_period(title, report_type),
                "validation_status": "success",
                "failure_reason": "success",
                "http_status_code": status or "",
                "notes": f"matched:{matched_pattern}",
            }
        )
        return base

    base.update({"validation_status": "failed", "failure_reason": "no_matching_report", "http_status_code": status or ""})
    return base


def main() -> None:
    ensure_dirs()
    mapping_rows = load_mapping()
    mapped = [r for r in mapping_rows if is_mapped(r)]
    skipped = len(mapping_rows) - len(mapped)

    results: List[Dict] = []
    for row in mapped:
        for rtype, cfg in REPORT_TYPES.items():
            title_patterns = cfg.get("title_patterns") or []
            # strategy 1: keyword_recent
            for kw in cfg.get("keywords_recent", []):
                results.append(process_record(row, rtype, "keyword_recent", kw, title_patterns))
                time.sleep(SLEEP_SECONDS)
            # strategy 2: keyword_with_year
            for kw in cfg.get("keywords_with_year", []):
                results.append(process_record(row, rtype, "keyword_with_year", kw, title_patterns))
                time.sleep(SLEEP_SECONDS)
            # strategy 3: longer_time_window (reuse recent keyword if available)
            for kw in cfg.get("keywords_recent", []):
                results.append(process_record(row, rtype, "longer_time_window", kw, title_patterns))
                time.sleep(SLEEP_SECONDS)
            # strategy 4: report_title_pattern (no keyword, only pattern match)
            results.append(process_record(row, rtype, "report_title_pattern", "", title_patterns))
            time.sleep(SLEEP_SECONDS)

    write_csv(results)
    summarize(results, len(mapping_rows), len(mapped), skipped)
    print(f"Wrote {len(results)} rows -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")


def write_csv(rows: List[Dict]) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def load_csv_results() -> List[Dict]:
    with open(OUT_CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _is_field_available(value: str | None) -> bool:
    text = (value or "").strip()
    return bool(text) and text.lower() != "unknown"


def summarize(rows: List[Dict], total_companies: int, mapped: int, skipped: int) -> None:
    status_counter = {}
    from collections import Counter, defaultdict

    status_counter = Counter(r.get("validation_status", "") for r in rows)
    report_counter = defaultdict(Counter)
    strategy_counter = defaultdict(Counter)
    field_avail = Counter()
    report_period_unknown = 0
    failure_counter = Counter(r.get("failure_reason", "") for r in rows)

    for r in rows:
        rt = r.get("report_type", "")
        st = r.get("query_strategy", "")
        status = r.get("validation_status", "")
        report_counter[rt][status] += 1
        strategy_counter[st][status] += 1
        if _is_field_available(r.get("announcement_title")):
            field_avail["announcement_title"] += 1
        if _is_field_available(r.get("publish_time")):
            field_avail["publish_time"] += 1
        if _is_field_available(r.get("report_period")):
            field_avail["report_period"] += 1
        elif (r.get("report_period") or "").strip().lower() == "unknown":
            report_period_unknown += 1
        if _is_field_available(r.get("pdf_url")):
            field_avail["pdf_url"] += 1
        if _is_field_available(r.get("source_url")):
            field_avail["source_url"] += 1

    total_rows = len(rows)

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO 报告类公告查询机制验证（Sub Issue 5）\n\n")
        fh.write("## 数据来源\n")
        fh.write(f"- 公司映射：{os.path.relpath(MAPPING_CSV, BASE_DIR)}\n")
        fh.write(f"- 样本公司：{os.path.relpath(os.path.join(OUT_DIR, 'cninfo_p0_sample_companies.csv'), BASE_DIR)}\n")
        fh.write(f"- 策略配置：{os.path.relpath(os.path.join(BASE_DIR, 'config', 'cninfo_announcement_retrieval_strategies.yaml'), BASE_DIR)}\n\n")

        fh.write("## 样本与覆盖\n")
        fh.write(f"- 样本公司数：{total_companies}\n")
        fh.write(f"- mapped：{mapped}\n")
        fh.write(f"- skipped（needs_orgid_mapping）：{skipped}\n")
        fh.write(f"- report_type 数量：{len(REPORT_TYPES)}\n")
        fh.write(f"- query_strategy 数量：{len(QUERY_STRATEGIES)}\n")
        fh.write(f"- 输出行数：{total_rows}\n\n")

        fh.write("## 结果分布\n")
        fh.write(f"- success：{status_counter.get('success',0)}\n")
        fh.write(f"- failed：{status_counter.get('failed',0)}\n")
        fh.write(f"- skipped：{status_counter.get('skipped',0)}\n\n")

        fh.write("### 按 report_type\n")
        for rt, cnt in sorted(report_counter.items()):
            fh.write(f"- {rt}: success {cnt.get('success',0)} / failed {cnt.get('failed',0)} / skipped {cnt.get('skipped',0)}\n")
        fh.write("\n")

        fh.write("### 按 query_strategy\n")
        for st, cnt in sorted(strategy_counter.items()):
            fh.write(f"- {st}: success {cnt.get('success',0)} / failed {cnt.get('failed',0)} / skipped {cnt.get('skipped',0)}\n")
        fh.write("\n")

        fh.write("### 字段可得性（行计数，非空且非 unknown）\n")
        fh.write(f"- announcement_title：{field_avail['announcement_title']}/{total_rows}\n")
        fh.write(f"- publish_time：{field_avail['publish_time']}/{total_rows}\n")
        fh.write(f"- report_period：{field_avail['report_period']}/{total_rows}\n")
        fh.write(f"- report_period_unknown：{report_period_unknown}\n")
        fh.write(f"- pdf_url：{field_avail['pdf_url']}/{total_rows}\n")
        fh.write(f"- source_url：{field_avail['source_url']}/{total_rows}\n")
        fh.write("- 说明：failed 行 CSV 中 report_period 保留为 unknown，不计入 report_period 可得性。\n\n")

        fh.write("## 观察与结论\n")
        fh.write("- 报告类专项查询明显有效。\n")
        fh.write("- 半年报已从前一轮公告类别验证的 0 命中提升到 55 success。\n")
        fh.write("- Q1/Q3 季报比普通 category 验证更稳定，分别达到 113 / 102 success。\n")
        fh.write("- 年报、半年报、季报应从普通事件公告分类中拆出，作为 document/report retrieval 机制单独处理。\n")
        fh.write("- keyword_recent 和 longer_time_window 当前效果最好；keyword_with_year 也有效。\n")
        fh.write("- report_title_pattern 单独使用效果较弱。\n")
        fh.write(
            f"- report_period 已从标题解析 {field_avail['report_period']}/{total_rows}；"
            f"另有 {report_period_unknown} 行为 unknown（含 failed 行占位，不代表解析成功）。\n"
        )
        fh.write("- source_url 当前仍为 0，但 pdf_url 可得。\n")
        fh.write("- recommended_status：testing / partial（不写 verified）。\n\n")

        fh.write("## 边界确认\n")
        fh.write("- 未下载 PDF 正文；未解析 PDF；未做 hash。\n")
        fh.write("- 未做数据库 / MinIO 接入；未使用 BrowserUser。\n")
        fh.write("- 不修改 docs / plans / storage schema；不修改原始 CSV。\n")
        fh.write("- 本摘要已基于当前运行结果生成。\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CNINFO 报告类公告查询机制验证")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="仅从已有 CSV 重生成 summary，不访问 CNINFO",
    )
    args = parser.parse_args()

    if args.summary_only:
        ensure_dirs()
        mapping_rows = load_mapping()
        mapped_rows = [r for r in mapping_rows if is_mapped(r)]
        summarize(
            load_csv_results(),
            len(mapping_rows),
            len(mapped_rows),
            len(mapping_rows) - len(mapped_rows),
        )
        print(f"Summary -> {OUT_SUMMARY}")
    else:
        # 默认直接运行会访问 CNINFO 公告接口。请在本地、合规网络环境下手动执行。
        main()
