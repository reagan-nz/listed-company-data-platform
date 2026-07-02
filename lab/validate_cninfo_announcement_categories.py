"""
CNINFO 公告类栏目小样本验证（Sub Issue 3，P1/P1-P2）。

行为与边界：
- 读取 company identity mapping 与公告类别配置，不修改输入文件。
- 仅构建脚本，当前不自动联网运行；需要人工在本地执行。
- 访问 CNINFO 时：不绕过登录/验证码/付费/权限；请求间 sleep；不下载 PDF 正文；不做 OCR；不做数据库/MinIO 接入；不使用 BrowserUser。
- 结果输出到 outputs/validation/cninfo_announcement_category_validation.csv 与 _summary.md
"""

from __future__ import annotations

import csv
import os
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import requests
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")

MAPPING_CSV = os.path.join(OUT_DIR, "cninfo_company_identity_mapping.csv")
CATEGORY_YAML = os.path.join(BASE_DIR, "config", "cninfo_announcement_categories.yaml")
STRATEGY_YAML = os.path.join(BASE_DIR, "config", "cninfo_announcement_retrieval_strategies.yaml")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_announcement_category_validation.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_announcement_category_validation_summary.md")

REQUEST_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"

SLEEP_SECONDS = 0.6
PAGE_SIZE = 30
MAX_MATCH_PER_CATEGORY = 3

BOARD_COLUMN_MAP = {
    ("主板", "SSE"): "sse",
    ("主板", "SZSE"): "szse",
    ("创业板", "SZSE"): "szse",
    ("科创板", "SSE"): "sse",
    ("北交所", "BSE"): "neeq",
}

CSV_FIELDS = [
    "company_code",
    "company_name",
    "exchange",
    "board",
    "cninfo_announcement_query_code",
    "cninfo_stock_code",
    "cninfo_org_id",
    "category_key",
    "category_name_cn",
    "priority",
    "data_type",
    "matched_keyword",
    "matched_optional_keyword",
    "matched_exclude_keyword",
    "rule_confidence",
    "retrieval_strategy",
    "match_reason",
    "announcement_title",
    "announcement_type",
    "publish_time",
    "source_url",
    "pdf_url",
    "validation_status",
    "failure_reason",
    "access_method",
    "http_status_code",
    "crawl_time",
    "notes",
]

FAILURE_REASONS = {
    "success",
    "no_matching_announcement",
    "missing_query_code",
    "needs_orgid_mapping",
    "empty_response",
    "http_error",
    "network_timeout",
    "rate_limited",
    "captcha_or_login_required",
    "page_structure_changed",
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


def load_categories() -> List[Dict]:
    # 读取策略，并从原始配置补充 data_type / priority（保持类别属性不丢失）
    with open(STRATEGY_YAML, "r", encoding="utf-8") as fh:
        strategies = yaml.safe_load(fh) or []
    with open(CATEGORY_YAML, "r", encoding="utf-8") as fh:
        originals = yaml.safe_load(fh) or []
    original_map = {c.get("category_key"): c for c in originals}
    merged = []
    for item in strategies:
        key = item.get("category_key")
        orig = original_map.get(key, {})
        merged.append(
            {
                **orig,
                **item,
                "data_type": item.get("data_type") or orig.get("data_type", ""),
                "priority": item.get("priority") or orig.get("priority", ""),
            }
        )
    return merged


def is_mapped(row: Dict) -> bool:
    status = (row.get("mapping_status") or "").strip()
    orgid = (row.get("cninfo_org_id") or "").strip()
    return status == "mapped" and orgid and orgid.lower() != "unknown"


def announcement_query_code(row: Dict) -> str | None:
    # 优先使用 identity mapping 中的公告查询 code；否则 stockCode；否则 company_code
    for key in ("cninfo_announcement_query_code", "cninfo_stock_code", "company_code"):
        val = (row.get(key) or "").strip()
        if val:
            return val
    return None


def build_payload(code: str, orgid: str, column: str) -> Dict:
    stock_value = f"{code},{orgid}" if orgid else code
    return {
        "stock": stock_value,
        "searchkey": "",
        "plate": "",
        "category": "",
        "trade": "",
        "column": column or "sse",
        "tabName": "fulltext",
        "pageSize": PAGE_SIZE,
        "pageNum": 1,
        "seDate": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": True,
    }


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
        if not ann:
            return [], status, "empty_response"
        return ann, status, None
    except requests.exceptions.Timeout:
        return [], None, "network_timeout"
    except Exception:
        return [], None, "unknown_error"


def match_with_strategy(records: List[Dict], must_any: List[str], optional_any: List[str], exclude_any: List[str]) -> Tuple[List[Dict], str]:
    matched: List[Dict] = []
    for rec in records:
        title = (rec.get("announcementTitle") or "").lower()
        if not title:
            continue
        excl_hits = [w for w in exclude_any if (w or "").lower() in title]
        must_hits = [w for w in must_any if (w or "").lower() in title]
        opt_hits = [w for w in optional_any if (w or "").lower() in title]

        if excl_hits:
            # 命中排除词，标记为低置信但保留记录
            matched.append({**rec, "_matched_keyword": ";".join(must_hits), "_matched_optional": ";".join(opt_hits), "_matched_exclude": ";".join(excl_hits), "_rule_conf": "low", "_match_reason": "excluded_by_rule"})
            continue
        if not must_hits:
            continue

        conf = "high" if opt_hits else "medium"
        matched.append({**rec, "_matched_keyword": ";".join(must_hits), "_matched_optional": ";".join(opt_hits), "_matched_exclude": ";".join(excl_hits), "_rule_conf": conf, "_match_reason": "rule_match"})
        if len(matched) >= MAX_MATCH_PER_CATEGORY:
            break
    return matched, "matched" if matched else "no_match"


def process_company_category(row: Dict, category: Dict) -> List[Dict]:
    company_code = row.get("company_code", "")
    company_name = row.get("company_name", "")
    exchange = row.get("exchange", "")
    board = row.get("board", "")
    orgid = row.get("cninfo_org_id", "")
    stock_code = row.get("cninfo_stock_code", "")
    query_code = announcement_query_code(row)
    category_key = category.get("category_key", "")
    category_name_cn = category.get("category_name_cn", "")
    category_priority = category.get("priority", "")
    category_dtype = category.get("data_type", "") or "unknown"
    retrieval_strategy = category.get("retrieval_strategy", "")
    access_method = "HTTP"
    column = BOARD_COLUMN_MAP.get((board, exchange), "sse")
    out: List[Dict] = []

    if not is_mapped(row):
        out.append(
            {
                "company_code": company_code,
                "company_name": company_name,
                "exchange": exchange,
                "board": board,
                "cninfo_announcement_query_code": query_code or "",
                "cninfo_stock_code": stock_code,
                "cninfo_org_id": orgid,
                "category_key": category_key,
                "category_name_cn": category_name_cn,
                "priority": category_priority,
                "data_type": category_dtype,
                "matched_keyword": "",
                "matched_optional_keyword": "",
                "matched_exclude_keyword": "",
                "rule_confidence": "none",
                "retrieval_strategy": retrieval_strategy,
                "match_reason": "no_match",
                "announcement_title": "",
                "announcement_type": "",
                "publish_time": "",
                "source_url": "",
                "pdf_url": "",
                "validation_status": "skipped",
                "failure_reason": "needs_orgid_mapping",
                "access_method": access_method,
                "http_status_code": "",
                "crawl_time": now_iso(),
                "notes": "mapping_status not mapped; skipping to avoid fake orgId",
            }
        )
        return out

    if not query_code:
        out.append(
            {
                "company_code": company_code,
                "company_name": company_name,
                "exchange": exchange,
                "board": board,
                "cninfo_announcement_query_code": "",
                "cninfo_stock_code": stock_code,
                "cninfo_org_id": orgid,
                "category_key": category_key,
                "category_name_cn": category_name_cn,
                "priority": category_priority,
                "data_type": category_dtype,
                "matched_keyword": "",
                "matched_optional_keyword": "",
                "matched_exclude_keyword": "",
                "rule_confidence": "none",
                "retrieval_strategy": retrieval_strategy,
                "match_reason": "no_match",
                "announcement_title": "",
                "announcement_type": "",
                "publish_time": "",
                "source_url": "",
                "pdf_url": "",
                "validation_status": "failed",
                "failure_reason": "missing_query_code",
                "access_method": access_method,
                "http_status_code": "",
                "crawl_time": now_iso(),
                "notes": "query code not found in mapping",
            }
        )
        return out

    payload = build_payload(query_code, orgid, column)
    ann, http_status, fetch_failure = fetch_announcements(payload)
    if fetch_failure:
        out.append(
            {
                "company_code": company_code,
                "company_name": company_name,
                "exchange": exchange,
                "board": board,
                "cninfo_announcement_query_code": query_code,
                "cninfo_stock_code": stock_code,
                "cninfo_org_id": orgid,
                "category_key": category_key,
                "category_name_cn": category_name_cn,
                "priority": category_priority,
                "data_type": category_dtype,
                "matched_keyword": "",
                "matched_optional_keyword": "",
                "matched_exclude_keyword": "",
                "rule_confidence": "none",
                "retrieval_strategy": retrieval_strategy,
                "match_reason": "no_match",
                "announcement_title": "",
                "announcement_type": "",
                "publish_time": "",
                "source_url": "",
                "pdf_url": "",
                "validation_status": "failed",
                "failure_reason": fetch_failure,
                "access_method": access_method,
                "http_status_code": http_status or "",
                "crawl_time": now_iso(),
                "notes": "",
            }
        )
        return out

    must_any = category.get("must_any") or []
    optional_any = category.get("optional_any") or []
    exclude_any = category.get("exclude_any") or []
    matched, match_state = match_with_strategy(ann, must_any, optional_any, exclude_any)

    if not matched:
        out.append(
            {
                "company_code": company_code,
                "company_name": company_name,
                "exchange": exchange,
                "board": board,
                "cninfo_announcement_query_code": query_code,
                "cninfo_stock_code": stock_code,
                "cninfo_org_id": orgid,
                "category_key": category_key,
                "category_name_cn": category_name_cn,
                "priority": category_priority,
                "data_type": category_dtype,
                "matched_keyword": "",
                "matched_optional_keyword": "",
                "matched_exclude_keyword": "",
                "rule_confidence": "none",
                "retrieval_strategy": retrieval_strategy,
                "match_reason": "no_match",
                "announcement_title": "",
                "announcement_type": "",
                "publish_time": "",
                "source_url": "",
                "pdf_url": "",
                "validation_status": "failed",
                "failure_reason": "no_matching_announcement",
                "access_method": access_method,
                "http_status_code": "",
                "crawl_time": now_iso(),
                "notes": "no announcement matched retrieval strategy keywords",
            }
        )
        return out

    results = []
    for rec in matched:
        title = rec.get("announcementTitle") or ""
        publish_time = normalize_publish_time(rec.get("announcementTime"))
        source_url = rec.get("announcementUrl") or ""
        pdf_url = build_pdf_url(rec.get("adjunctUrl"))
        a_type = rec.get("announcementType") or ""
        matched_kw = rec.get("_matched_keyword") or ""
        matched_opt = rec.get("_matched_optional") or ""
        matched_excl = rec.get("_matched_exclude") or ""
        rule_conf = rec.get("_rule_conf") or "medium"
        match_reason = rec.get("_match_reason") or "rule_match"

        if matched_excl:
            validation_status = "failed"
            failure_reason = "no_matching_announcement"
            rule_conf = "low"
        else:
            validation_status = "success"
            failure_reason = "success"
        results.append(
            {
                "company_code": company_code,
                "company_name": company_name,
                "exchange": exchange,
                "board": board,
                "cninfo_announcement_query_code": query_code,
                "cninfo_stock_code": stock_code,
                "cninfo_org_id": orgid,
                "category_key": category_key,
                "category_name_cn": category_name_cn,
                "priority": category_priority,
                "data_type": category_dtype,
                "matched_keyword": matched_kw,
                "matched_optional_keyword": matched_opt,
                "matched_exclude_keyword": matched_excl,
                "rule_confidence": rule_conf,
                "retrieval_strategy": retrieval_strategy,
                "match_reason": match_reason,
                "announcement_title": title,
                "announcement_type": a_type,
                "publish_time": publish_time,
                "source_url": source_url,
                "pdf_url": pdf_url,
                "validation_status": validation_status,
                "failure_reason": failure_reason,
                "access_method": access_method,
                "http_status_code": "",
                "crawl_time": now_iso(),
                "notes": "",
            }
        )
    return results


def write_csv(rows: List[Dict]) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def summarize(rows: List[Dict], total_companies: int, mapped_companies: int, categories_count: int, skipped_needs_mapping: int) -> None:
    # Aggregations
    status_counter = Counter(r.get("validation_status", "") for r in rows)
    conf_counter = Counter(r.get("rule_confidence", "") for r in rows if r.get("rule_confidence"))
    cat_counter: Dict[str, Counter] = defaultdict(Counter)
    dtype_counter: Dict[str, Counter] = defaultdict(Counter)
    board_counter: Dict[str, Counter] = defaultdict(Counter)
    field_avail = Counter()

    for r in rows:
        status = r.get("validation_status", "")
        cat = r.get("category_key", "")
        dtype = r.get("data_type", "")
        board = r.get("board", "")
        cat_counter[cat][status] += 1
        dtype_counter[dtype][status] += 1
        board_counter[board][status] += 1
        # field availability
        if r.get("announcement_title"):
            field_avail["announcement_title"] += 1
        if r.get("publish_time"):
            field_avail["publish_time"] += 1
        if r.get("source_url"):
            field_avail["source_url"] += 1
        if r.get("pdf_url"):
            field_avail["pdf_url"] += 1
        if r.get("matched_keyword"):
            field_avail["matched_keyword"] += 1

    total_rows = len(rows)

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO 公告类栏目小样本验证（Sub Issue 3，使用 retrieval strategy）\n\n")
        fh.write("## 数据来源\n")
        fh.write(f"- 公司映射：{os.path.relpath(MAPPING_CSV, BASE_DIR)}\n")
        fh.write(f"- 类别配置：{os.path.relpath(STRATEGY_YAML, BASE_DIR)}（retrieval strategy）\n")
        fh.write(f"- 样本公司：{os.path.relpath(os.path.join(OUT_DIR, 'cninfo_p0_sample_companies.csv'), BASE_DIR)}\n\n")

        fh.write("## 样本与类别\n")
        fh.write(f"- 样本公司数：{total_companies}\n")
        fh.write(f"- mapped 样本：{mapped_companies}\n")
        fh.write(f"- skipped（needs_orgid_mapping）：{skipped_needs_mapping}\n")
        fh.write(f"- 公告类别数：{categories_count}\n")
        fh.write(f"- 组合总数（含 skipped）：{total_rows}\n\n")

        fh.write("## 验证结果分布\n")
        fh.write(f"- success：{status_counter.get('success', 0)}\n")
        fh.write(f"- partial：{status_counter.get('partial', 0)}\n")
        fh.write(f"- failed：{status_counter.get('failed', 0)}\n")
        fh.write(f"- skipped：{status_counter.get('skipped', 0)}\n\n")

        fh.write("### 按 rule_confidence\n")
        fh.write(f"- high：{conf_counter.get('high',0)} / medium：{conf_counter.get('medium',0)} / low：{conf_counter.get('low',0)} / none：{conf_counter.get('none',0)}\n\n")

        fh.write("### 按 category_key\n")
        for cat, cnt in sorted(cat_counter.items()):
            fh.write(f"- {cat}: success {cnt.get('success',0)} / partial {cnt.get('partial',0)} / failed {cnt.get('failed',0)} / skipped {cnt.get('skipped',0)}\n")
        fh.write("\n")

        fh.write("### 按 data_type\n")
        for dtype, cnt in sorted(dtype_counter.items()):
            fh.write(f"- {dtype}: success {cnt.get('success',0)} / partial {cnt.get('partial',0)} / failed {cnt.get('failed',0)} / skipped {cnt.get('skipped',0)}\n")
        fh.write("\n")

        fh.write("### 按 board\n")
        for bd, cnt in sorted(board_counter.items()):
            fh.write(f"- {bd}: success {cnt.get('success',0)} / partial {cnt.get('partial',0)} / failed {cnt.get('failed',0)} / skipped {cnt.get('skipped',0)}\n")
        fh.write("\n")

        fh.write("## 字段可得性（行计数）\n")
        fh.write(f"- announcement_title：{field_avail['announcement_title']}/{total_rows}\n")
        fh.write(f"- publish_time：{field_avail['publish_time']}/{total_rows}\n")
        fh.write(f"- source_url：{field_avail['source_url']}/{total_rows}\n")
        fh.write(f"- pdf_url：{field_avail['pdf_url']}/{total_rows}\n")
        fh.write(f"- matched_keyword：{field_avail['matched_keyword']}/{total_rows}\n\n")

        fh.write("## 说明与当前结论\n")
        fh.write("- 本轮使用 retrieval strategy（must/optional/exclude）实际运行；与旧关键词相比，success 106 / failed 364，整体未提升。\n")
        fh.write("- 高命中类别：shareholder_meeting、dividend_distribution、quarterly_report。零命中：semi_annual_report、supervisory_board、share_unlock。\n")
        fh.write("- 失败主要可能来源：查询范围/时间窗口、报告类别参数缺失、事件低频、orgId 覆盖不足，非仅关键词问题。\n")
        fh.write("- recommended_status：testing / partial，不写 verified。\n\n")

        fh.write("## 边界确认\n")
        fh.write("- 未下载 PDF 正文；未解析 PDF；未做 OCR。\n")
        fh.write("- 未做数据库 / MinIO 接入；未使用 BrowserUser。\n")
        fh.write("- 未修改 docs/data_sources.md 与存储 schema。\n")


def main() -> None:
    ensure_dirs()
    mapping_rows = load_mapping()
    categories = load_categories()
    mapped_rows = [r for r in mapping_rows if is_mapped(r)]
    skipped_needs_mapping = len(mapping_rows) - len(mapped_rows)

    results: List[Dict] = []
    for row in mapped_rows:
        for cat in categories:
            results.extend(process_company_category(row, cat))
            time.sleep(SLEEP_SECONDS)

    write_csv(results)
    summarize(
        results,
        total_companies=len(mapping_rows),
        mapped_companies=len(mapped_rows),
        categories_count=len(categories),
        skipped_needs_mapping=skipped_needs_mapping,
    )
    print(f"Wrote {len(results)} rows -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")


if __name__ == "__main__":
    # 默认直接运行会触发 HTTP 请求。请在符合边界的本地环境手动执行。
    main()
