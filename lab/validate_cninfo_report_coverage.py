"""
CNINFO A 类（类年报 PDF 文档流）per-company coverage 验证（Era C Phase 1）。

口径：一家公司 × 一个 report_type × 一个 expected_period = 一行。
多种 query strategy 仅作内部 fallback，不拆成多行。

默认不自动联网；请在本地合规环境执行：
    python lab/validate_cninfo_report_coverage.py
    python lab/validate_cninfo_report_coverage.py --summary-only
    python lab/validate_cninfo_report_coverage.py --diagnostics-only

P1 扩展样本（需先有 P1 identity mapping）：
    python lab/validate_cninfo_report_coverage.py \\
      --input-mapping outputs/validation/cninfo_report_p1_identity_mapping.csv \\
      --output-prefix outputs/validation/cninfo_report_p1_coverage \\
      --sample-csv outputs/validation/cninfo_report_p1_sample_companies.csv

边界：不下载/解析 PDF；不计算 hash；不接数据库/MinIO；不使用 BrowserUser；请求间 sleep。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")

MAPPING_CSV = os.path.join(OUT_DIR, "cninfo_company_identity_mapping.csv")
SAMPLE_CSV = os.path.join(OUT_DIR, "cninfo_p0_sample_companies.csv")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_report_coverage_validation.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_report_coverage_validation_summary.md")
OUT_DIAGNOSTICS = os.path.join(OUT_DIR, "cninfo_report_coverage_parameter_diagnostics.md")
OLD_SUMMARY = os.path.join(OUT_DIR, "cninfo_report_announcement_validation_summary.md")

# 当前跑次标签（P0 默认；--output-prefix 含 p1 时为 P1）
RUN_LABEL = "P0"

# P0 最终 coverage（供 P1 summary 对比）
P0_COVERAGE_BASELINE = {
    "label": "P0",
    "companies": 30,
    "overall_found": 113,
    "overall_expected": 120,
    "overall_pct": 94.17,
    "annual": (30, 30),
    "semi": (30, 30),
    "q1": (26, 30),
    "q3": (27, 30),
    "sse": (68, 68),
    "szse": (21, 28),
    "bse": (24, 24),
}

TOPSEARCH_URL = "https://www.cninfo.com.cn/new/information/topSearch/query"
REQUEST_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
SLEEP_SECONDS = 0.6
PAGE_SIZE = 30

AJAX_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
        "ListedCompanyDataCollector/cninfo-report-coverage"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.cninfo.com.cn/",
}

# 创业板 P0 样本：F10 经验规则 gssh0+code 对公告查询无效；以下为 full_market_2024 已验证 orgId
CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES: Dict[str, str] = {
    "300001": "9900008270",
    "300002": "9900008268",
    "300003": "9900008269",
    "300004": "9900008272",
    "300005": "9900008308",
    "300006": "9900008273",
    "300007": "9900008312",
}

_ORGID_SEARCH_CACHE: Dict[str, str] = {}


class _RunStats:
    """单次 coverage 运行的质量统计（title filter / SZSE category fallback）。"""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.found_before_title_filter = 0
        self.found_after_title_filter = 0
        self.title_excluded_rows = 0
        self.annual_title_excluded = 0
        self.semi_title_excluded = 0
        self.q1_title_excluded = 0
        self.q3_title_excluded = 0
        self.summary_title_hits = 0
        self.szse_category_fallback_hits = 0
        self.exclusion_reason_counter: Counter = Counter()


_RUN_STATS = _RunStats()

PROGRESS_LOG_INTERVAL = 10


def format_duration(seconds: float) -> str:
    if seconds < 0:
        return "n/a"
    total = int(seconds)
    if total < 60:
        return f"{total}s"
    minutes, sec = divmod(total, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {sec}s"


def log_fetch_error(
    company_code: str,
    report_type: str,
    strategy: str,
    failure: str,
    message: str,
) -> None:
    print(
        f"[coverage] {failure} | company={company_code} report_type={report_type} "
        f"strategy={strategy} | {message or failure}",
        flush=True,
    )


class CoverageProgressLogger:
    """轻量进度日志（仅 stdout，不影响 coverage 口径）。"""

    def __init__(self, total_mapped: int) -> None:
        self.total_mapped = total_mapped
        self.mapped_processed = 0
        self.found_rows = 0
        self.not_found_rows = 0
        self.skipped_rows = 0
        self._start = time.monotonic()

    def _elapsed(self) -> float:
        return time.monotonic() - self._start

    def elapsed_seconds(self) -> float:
        return self._elapsed()

    def _eta_seconds(self) -> float:
        if self.mapped_processed <= 0:
            return -1.0
        return (self._elapsed() / self.mapped_processed) * (self.total_mapped - self.mapped_processed)

    def _record_rows(self, company_results: List[Dict]) -> None:
        for result in company_results:
            reason = (result.get("failure_reason") or "").strip()
            if reason == "needs_orgid_mapping":
                self.skipped_rows += 1
            elif (result.get("found") or "").lower() == "yes":
                self.found_rows += 1
            else:
                self.not_found_rows += 1

    def on_company_done(self, row: Dict, company_results: List[Dict]) -> None:
        self._record_rows(company_results)
        mapped_company = is_mapped(row)
        if mapped_company:
            self.mapped_processed += 1

        code = (row.get("company_code") or "").strip()
        name = (row.get("company_name") or "").strip()
        company_found = sum(1 for r in company_results if (r.get("found") or "").lower() == "yes")
        elapsed = format_duration(self._elapsed())
        print(
            f"[coverage] done {code} {name} | company_rows {company_found}/{len(company_results)} found | "
            f"cumulative found={self.found_rows} not_found={self.not_found_rows} skipped={self.skipped_rows} | "
            f"elapsed={elapsed}",
            flush=True,
        )

        if mapped_company and self.mapped_processed % PROGRESS_LOG_INTERVAL == 0:
            eta = format_duration(self._eta_seconds())
            print(
                f"[coverage] progress {self.mapped_processed}/{self.total_mapped} mapped companies | "
                f"current {code} {name} | "
                f"rows found={self.found_rows} not_found={self.not_found_rows} skipped={self.skipped_rows} | "
                f"elapsed={elapsed} eta={eta}",
                flush=True,
            )

# 预期报告期（可扩展 2023 / 2025）
EXPECTED_PERIODS: Dict[str, List[str]] = {
    "annual_report": ["2024"],
    "semi_annual_report": ["2024H1"],
    "quarterly_report_q1": ["2024Q1"],
    "quarterly_report_q3": ["2024Q3"],
}

REPORT_TYPES = {
    "annual_report": {
        "title_patterns": ["年度报告"],
        "keywords_recent": ["年度报告", "年报"],
    },
    "semi_annual_report": {
        "title_patterns": ["半年度报告", "半年报"],
        "keywords_recent": ["半年度报告", "半年报"],
    },
    "quarterly_report_q1": {
        "title_patterns": [
            "第一季度报告",
            "一季度报告",
            "第一季度报告全文",
            "一季度报告全文",
        ],
        "keywords_recent": ["第一季度报告", "季度报告"],
    },
    "quarterly_report_q3": {
        "title_patterns": [
            "第三季度报告",
            "三季度报告",
            "第三季度报告全文",
            "三季度报告全文",
        ],
        "keywords_recent": ["第三季度报告", "季度报告"],
    },
}

# 季报 category fallback（SZSE / BSE quarterly 内部 fallback；来源 probe_cninfo）
QUARTERLY_CATEGORY_CANDIDATES: Dict[str, List[str]] = {
    "quarterly_report_q1": ["category_yjdbg_szsh"],
    "quarterly_report_q3": ["category_sjdbg_szsh"],
}

# 所有 report_type 正式全文 found 共用 exclusion（quality audit 驱动）
# 顺序：长短语优先，避免「说明会」误伤「业绩说明会」的细分类
OFFICIAL_REPORT_TITLE_EXCLUSIONS: List[str] = [
    "披露提示性公告",
    "提示性公告",
    "业绩说明会",
    "投资者说明会",
    "监管问询函",
    "预告公告",
    "说明会",
    "交流会",
    "问询函",
    "回复公告",
    "关于披露",
    "关于延期披露",
    "延期披露",
    "摘要",
    "解读",
]

# P1 quality audit 前自动跑次（retrieval hit rate，含假阳性）
P1_PRE_TITLE_FILTER_BASELINE = {
    "found": 750,
    "expected": 796,
    "pct": 94.22,
    "audit_found_pass_rate": 78.0,
    "audit_estimated_effective_pct": 73.5,
}

# P1 更早跑次（title filter 初版前）
P1_PRE_FIX_BASELINE = {
    "found": 620,
    "expected": 796,
    "pct": 77.89,
    "annual_found": 191,
    "semi_found": 183,
    "q1_found": 123,
    "q3_found": 123,
}

# Q1/Q3 优化前 baseline（用于 summary 对比）
Q1Q3_OPTIMIZATION_BASELINE = {
    "overall_found": 101,
    "overall_expected": 120,
    "overall_pct": 84.17,
    "q1_found": 20,
    "q1_expected": 30,
    "q3_found": 21,
    "q3_expected": 30,
}

# 内部 fallback 顺序（不拆行）；季报在耗尽后另有 QUARTERLY_EXTRA_STRATEGIES
STRATEGY_ORDER = [
    "keyword_with_year",
    "keyword_recent",
    "longer_time_window",
    "report_title_pattern",
]

QUARTERLY_EXTRA_STRATEGIES = [
    "quarterly_keyword_expanded",
    "quarterly_seDate_fallback",
    "quarterly_category_fallback",
]

BOARD_COLUMN_MAP = {
    ("主板", "SSE"): "sse",
    ("主板", "SZSE"): "szse",
    ("创业板", "SZSE"): "szse",
    ("科创板", "SSE"): "sse",
    # probe_cninfo / eval_generalize 使用 bj；旧脚本 neeq 导致 BSE empty_response
    ("北交所", "BSE"): "bj",
}

# column 内部 fallback（仅参数层，不拆 coverage 行）
COLUMN_FALLBACKS: Dict[str, List[str]] = {
    "bj": ["bj", "neeq"],
    "szse": ["szse"],
    "sse": ["sse"],
}

CSV_FIELDS = [
    "company_code",
    "company_name",
    "exchange",
    "board",
    "mapping_status",
    "cninfo_announcement_query_code",
    "report_type",
    "expected_period",
    "found",
    "matched_title",
    "publish_time",
    "parsed_report_period",
    "pdf_url",
    "matched_strategy",
    "http_status_code",
    "failure_reason",
    "crawl_time",
    "notes",
]


def ensure_dirs() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def resolve_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)


def is_p1_run() -> bool:
    return RUN_LABEL == "P1"


def configure_run_paths(
    input_mapping: str | None = None,
    output_prefix: str | None = None,
    sample_csv: str | None = None,
) -> None:
    """根据 CLI 设置本次运行的 mapping / 输出 / 样本路径（默认 P0）。"""
    global MAPPING_CSV, OUT_CSV, OUT_SUMMARY, OUT_DIAGNOSTICS, SAMPLE_CSV, RUN_LABEL

    MAPPING_CSV = resolve_path(input_mapping) if input_mapping else os.path.join(
        OUT_DIR, "cninfo_company_identity_mapping.csv"
    )
    prefix = resolve_path(output_prefix) if output_prefix else os.path.join(
        OUT_DIR, "cninfo_report_coverage"
    )
    OUT_CSV = f"{prefix}_validation.csv"
    OUT_SUMMARY = f"{prefix}_validation_summary.md"
    OUT_DIAGNOSTICS = f"{prefix}_parameter_diagnostics.md"

    if sample_csv:
        SAMPLE_CSV = resolve_path(sample_csv)
    elif "p1" in os.path.basename(prefix).lower():
        SAMPLE_CSV = os.path.join(OUT_DIR, "cninfo_report_p1_sample_companies.csv")
    else:
        SAMPLE_CSV = os.path.join(OUT_DIR, "cninfo_p0_sample_companies.csv")

    RUN_LABEL = "P1" if "p1" in os.path.basename(prefix).lower() else "P0"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_mapping() -> List[Dict]:
    with open(MAPPING_CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


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


def build_payload(
    code: str,
    orgid: str,
    column: str,
    keyword: str,
    se_date: str,
    category: str = "",
) -> Dict:
    stock_value = f"{code},{orgid}" if orgid else code
    return {
        "stock": stock_value,
        "searchkey": keyword,
        "plate": "",
        "category": category or "",
        "trade": "",
        "column": column or "sse",
        "tabName": "fulltext",
        "pageSize": PAGE_SIZE,
        "pageNum": 1,
        "seDate": se_date,
        "sortName": "",
        "sortType": "",
        "secid": "",
        "isHLtitle": "true",
    }


def is_quarterly_report(report_type: str) -> bool:
    return report_type in ("quarterly_report_q1", "quarterly_report_q3")


def quarterly_year(expected_period: str) -> str:
    m = re.match(r"(20\d{2})", expected_period or "")
    return m.group(1) if m else ""


def quarterly_expanded_keywords(report_type: str, expected_period: str) -> List[str]:
    """季报扩展关键词（quarterly_keyword_expanded 策略专用）。"""
    year = quarterly_year(expected_period)
    if report_type == "quarterly_report_q1":
        return [
            f"{year}年第一季度报告",
            f"{year}年一季度报告",
            f"{year}第一季度报告",
            f"{year}一季度报告",
            "第一季度报告",
            "一季度报告",
            f"{year}年第一季度报告全文",
            f"{year}年一季度报告全文",
        ]
    if report_type == "quarterly_report_q3":
        return [
            f"{year}年第三季度报告",
            f"{year}年三季度报告",
            f"{year}第三季度报告",
            f"{year}三季度报告",
            "第三季度报告",
            "三季度报告",
            f"{year}年第三季度报告全文",
            f"{year}年三季度报告全文",
        ]
    return []


def quarterly_se_date_windows(report_type: str, expected_period: str) -> List[str]:
    """SZSE/BSE 季报披露窗口 fallback。"""
    year = quarterly_year(expected_period)
    if report_type == "quarterly_report_q1":
        return [
            f"{year}-04-01 ~ {year}-05-31",
            f"{year}-03-01 ~ {year}-05-31",
        ]
    if report_type == "quarterly_report_q3":
        return [
            f"{year}-10-01 ~ {year}-11-30",
            f"{year}-09-01 ~ {year}-11-30",
        ]
    return []


def quarterly_se_date_keywords(report_type: str) -> List[str]:
    if report_type == "quarterly_report_q1":
        return ["一季度报告", "第一季度报告"]
    if report_type == "quarterly_report_q3":
        return ["三季度报告", "第三季度报告"]
    return []


def iter_query_attempts(
    report_type: str,
    expected_period: str,
    exchange: str,
    cfg: Dict,
) -> List[Dict]:
    """生成单次 hisAnnouncement/query 尝试计划（strategy / keyword / seDate / category）。"""
    attempts: List[Dict] = []

    def add(strategy: str, keyword: str = "", se_date: str = "", category: str = "") -> None:
        attempts.append(
            {
                "strategy": strategy,
                "keyword": keyword,
                "se_date": se_date,
                "category": category,
            }
        )

    for strategy in STRATEGY_ORDER:
        if strategy == "keyword_with_year":
            kw = keyword_with_year_for_period(report_type, expected_period)
            if kw:
                add(strategy, kw, time_window(strategy))
        elif strategy == "keyword_recent":
            for kw in cfg.get("keywords_recent") or []:
                add(strategy, kw, time_window(strategy))
        elif strategy == "longer_time_window":
            recent = cfg.get("keywords_recent") or []
            if recent:
                add(strategy, recent[0], time_window(strategy))
        elif strategy == "report_title_pattern":
            add(strategy, "", time_window(strategy))

    if not is_quarterly_report(report_type):
        return attempts

    for kw in quarterly_expanded_keywords(report_type, expected_period):
        add("quarterly_keyword_expanded", kw, "")

    if exchange in ("SZSE", "BSE"):
        for se_date in quarterly_se_date_windows(report_type, expected_period):
            for kw in quarterly_se_date_keywords(report_type):
                add("quarterly_seDate_fallback", kw, se_date)

    if exchange in ("SZSE", "BSE"):
        for category in QUARTERLY_CATEGORY_CANDIDATES.get(report_type, []):
            add("quarterly_category_fallback", "", "", category)
            for kw in quarterly_se_date_keywords(report_type):
                add("quarterly_category_fallback", kw, "", category)
            for se_date in quarterly_se_date_windows(report_type, expected_period):
                add("quarterly_category_fallback", "", se_date, category)
                for kw in quarterly_se_date_keywords(report_type):
                    add("quarterly_category_fallback", kw, se_date, category)

    return attempts


def fetch_announcements(payload: Dict) -> Tuple[List[Dict], int | None, str | None, str]:
    try:
        resp = requests.post(REQUEST_URL, data=payload, headers=AJAX_HEADERS, timeout=8)
        status = resp.status_code
        if status == 429:
            return [], status, "rate_limited", ""
        if status == 401 or status == 403:
            return [], status, "captcha_or_login_required", ""
        if status != 200:
            return [], status, "http_error", f"HTTP {status}"
        data = resp.json()
        ann = data.get("announcements") or []
        if not ann:
            return [], status, "empty_response", ""
        return ann, status, None, ""
    except requests.exceptions.Timeout:
        return [], None, "network_timeout", "HTTP request timed out (8s)"
    except Exception as exc:
        return [], None, "unknown_error", f"{type(exc).__name__}: {exc}"


def is_empirical_gssh_orgid(orgid: str, stock: str) -> bool:
    return bool(orgid and stock and orgid.lower() == f"gssh0{stock}".lower())


def resolve_orgid_via_topsearch(stock_code: str) -> str:
    if not stock_code:
        return ""
    if stock_code in _ORGID_SEARCH_CACHE:
        return _ORGID_SEARCH_CACHE[stock_code]
    try:
        resp = requests.post(
            TOPSEARCH_URL,
            data={"keyWord": stock_code, "maxNum": 10},
            headers=AJAX_HEADERS,
            timeout=8,
        )
        if not resp.ok:
            return ""
        items = resp.json()
        if not isinstance(items, list):
            return ""
        for item in items:
            if str(item.get("code")) == str(stock_code):
                org = (item.get("orgId") or "").strip()
                if org:
                    _ORGID_SEARCH_CACHE[stock_code] = org
                    return org
        if items:
            org = (items[0].get("orgId") or "").strip()
            if org:
                _ORGID_SEARCH_CACHE[stock_code] = org
                return org
    except Exception:
        return ""
    return ""


def stock_code_variants(row: Dict) -> List[Tuple[str, str]]:
    company = (row.get("company_code") or "").strip()
    cninfo = (row.get("cninfo_stock_code") or "").strip()
    query = (row.get("cninfo_announcement_query_code") or "").strip()
    seen: set[str] = set()
    variants: List[Tuple[str, str]] = []

    def add(code: str, note: str) -> None:
        if code and code not in seen:
            seen.add(code)
            variants.append((code, note))

    add(cninfo, "cninfo_stock_code")
    add(query, "cninfo_announcement_query_code")
    add(company, "company_code")
    if company.startswith("430") and len(company) >= 6:
        add("92" + company[2:], "bse_430_to_92")
    return variants


def orgid_variants(row: Dict, stock_code: str) -> List[Tuple[str, str]]:
    company = (row.get("company_code") or "").strip()
    mapped_org = (row.get("cninfo_org_id") or "").strip()
    seen: set[str] = set()
    variants: List[Tuple[str, str]] = []

    def add(org: str, note: str) -> None:
        if org and org.lower() != "unknown" and org not in seen:
            seen.add(org)
            variants.append((org, note))

    if company in CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES:
        add(CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES[company], "chinext_announcement_orgid_override")
    add(mapped_org, "mapping_csv_orgid")
    if row.get("board") == "创业板" and is_empirical_gssh_orgid(mapped_org, stock_code):
        resolved = resolve_orgid_via_topsearch(stock_code)
        add(resolved, "topsearch_resolved_orgid")
    return variants


def column_variants(board: str, exchange: str) -> List[str]:
    primary = BOARD_COLUMN_MAP.get((board, exchange), "sse")
    return COLUMN_FALLBACKS.get(primary, [primary])


def query_param_variants(row: Dict) -> List[Dict]:
    """生成 hisAnnouncement/query 参数组合（内部 fallback，不拆 coverage 行）。"""
    board = row.get("board", "")
    exchange = row.get("exchange", "")
    variants: List[Dict] = []
    for stock_code, stock_note in stock_code_variants(row):
        for orgid, org_note in orgid_variants(row, stock_code):
            for column in column_variants(board, exchange):
                variants.append(
                    {
                        "stock_code": stock_code,
                        "orgid": orgid,
                        "column": column,
                        "note": f"stock={stock_note}; orgid={org_note}; column={column}",
                    }
                )
    return variants


def build_pdf_url(adjunct_url: str | None) -> str:
    if not adjunct_url:
        return ""
    return "http://static.cninfo.com.cn/" + adjunct_url.lstrip("/")


def normalize_publish_time(ts: int | None) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return ""


def publish_time_sort_key(ts: int | None) -> int:
    return int(ts or 0)


def strip_title_markup(title: str) -> str:
    """去除 CNINFO 高亮标签（如 <em>）便于标题判断。"""
    if not title:
        return ""
    return re.sub(r"</?em>", "", title, flags=re.IGNORECASE)


def match_report_title(title: str, patterns: List[str]) -> bool:
    t = strip_title_markup(title).lower()
    return any((p or "").lower() in t for p in patterns)


def get_title_exclusion_reason(title: str, report_type: str = "") -> str:
    """若标题应排除（非正式全文报告），返回命中关键词；否则返回空字符串。"""
    t = strip_title_markup(title)
    if not t:
        return ""
    for kw in OFFICIAL_REPORT_TITLE_EXCLUSIONS:
        if kw in t:
            return kw
    return ""


def is_title_excluded(title: str, report_type: str = "") -> bool:
    return bool(get_title_exclusion_reason(title, report_type))


def classify_exclusion_keyword(keyword: str) -> str:
    """将 exclusion 关键词归类，供 summary excluded_by_reason 统计。"""
    if keyword in ("披露提示性公告", "提示性公告", "预告公告"):
        return "announcement_preview"
    if keyword in ("问询函", "回复公告", "监管问询函"):
        return "inquiry_reply"
    if keyword in ("说明会", "业绩说明会", "投资者说明会", "交流会"):
        return "investor_meeting_notice"
    if keyword in ("关于延期披露", "延期披露"):
        return "delayed_disclosure_notice"
    if keyword == "关于披露":
        return "cross_company_disclosure"
    if keyword == "摘要":
        return "summary_or_abstract_only"
    if keyword:
        return "other_exclusion"
    return "unknown"


def is_summary_only_title(title: str, report_type: str) -> bool:
    """报告摘要类标题（单独统计，不计入正式全文 found）。"""
    t = strip_title_markup(title)
    if "摘要" not in t:
        return False
    if report_type == "annual_report":
        return "年度报告" in t
    if report_type == "semi_annual_report":
        return "半年度报告" in t or "半年报" in t
    if report_type == "quarterly_report_q1":
        return "一季度" in t or "第一季度" in t
    if report_type == "quarterly_report_q3":
        return "三季度" in t or "第三季度" in t
    return False


def _title_has_q1_marker(t: str) -> bool:
    if is_title_excluded(t):
        return False
    return any(
        marker in t
        for marker in (
            "第一季度报告",
            "一季度报告",
            "第一季度报告全文",
            "一季度报告全文",
        )
    )


def _title_has_q3_marker(t: str) -> bool:
    if is_title_excluded(t):
        return False
    return any(
        marker in t
        for marker in (
            "第三季度报告",
            "三季度报告",
            "第三季度报告全文",
            "三季度报告全文",
        )
    )


def parse_report_period(title: str, report_type: str) -> str:
    if not title:
        return "unknown"
    t = "".join(strip_title_markup(title).split())
    m = re.search(r"(20[0-9]{2})", t)
    if not m:
        return "unknown"
    year = m.group(1)
    if report_type == "annual_report":
        return year if "年度报告" in t else "unknown"
    if report_type == "semi_annual_report":
        return f"{year}H1" if ("半年度报告" in t or "半年报" in t) else "unknown"
    if report_type == "quarterly_report_q1":
        return f"{year}Q1" if _title_has_q1_marker(t) else "unknown"
    if report_type == "quarterly_report_q3":
        return f"{year}Q3" if _title_has_q3_marker(t) else "unknown"
    return "unknown"


def keyword_with_year_for_period(report_type: str, expected_period: str) -> str:
    if report_type == "annual_report":
        return f"{expected_period}年年度报告"
    if report_type == "semi_annual_report":
        year = expected_period.replace("H1", "")
        return f"{year}年半年度报告"
    if report_type == "quarterly_report_q1":
        year = expected_period.replace("Q1", "")
        return f"{year}年第一季度报告"
    if report_type == "quarterly_report_q3":
        year = expected_period.replace("Q3", "")
        return f"{year}年第三季度报告"
    return ""


def time_window(strategy: str) -> str:
    if strategy == "longer_time_window":
        end = datetime.now()
        start = end.replace(year=end.year - 3)
        return f"{start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}"
    return ""


def _sort_match_candidates(valid: List[Dict]) -> List[Dict]:
    return sorted(
        valid,
        key=lambda x: (
            -x["has_report_word"],
            -publish_time_sort_key(x.get("announcement_time")),
        ),
    )


def pick_best_match(
    candidates: List[Dict],
    report_type: str,
    expected_period: str,
    title_patterns: List[str],
) -> Tuple[Optional[Dict], Optional[Dict]]:
    """返回 (post_filter_match, pre_filter_best)；后者仅在因 title filter 被排除时非空。"""
    pre_valid: List[Dict] = []
    for rec in candidates:
        title = rec.get("announcementTitle") or ""
        if not match_report_title(title, title_patterns):
            continue
        parsed = parse_report_period(title, report_type)
        if parsed != expected_period:
            continue
        pdf_url = build_pdf_url(rec.get("adjunctUrl"))
        if not pdf_url:
            continue
        clean_title = strip_title_markup(title)
        pre_valid.append(
            {
                "title": title,
                "clean_title": clean_title,
                "publish_time": normalize_publish_time(rec.get("announcementTime")),
                "parsed_report_period": parsed,
                "pdf_url": pdf_url,
                "announcement_time": rec.get("announcementTime"),
                "has_report_word": 1 if "报告" in clean_title else 0,
            }
        )
    if not pre_valid:
        return None, None

    pre_sorted = _sort_match_candidates(pre_valid)
    pre_best = pre_sorted[0]

    post_valid = [v for v in pre_valid if not is_title_excluded(v["clean_title"], report_type)]
    if not post_valid:
        return None, pre_best

    post_best = _sort_match_candidates(post_valid)[0]
    return post_best, None


def try_find_report(
    row: Dict,
    report_type: str,
    expected_period: str,
    cfg: Dict,
) -> Tuple[Optional[Dict], str, str, str]:
    """返回 (match_dict|None, last_failure_reason, last_http_status, param_note)."""
    param_variants = query_param_variants(row)
    if not param_variants:
        return None, "missing_query_code", "", ""

    title_patterns = cfg.get("title_patterns") or []
    exchange = row.get("exchange", "")
    query_attempts = iter_query_attempts(report_type, expected_period, exchange, cfg)
    last_failure = "not_found"
    last_http = ""
    last_param_note = param_variants[0]["note"]
    last_attempt: Dict = {}
    last_title_excluded: Optional[Dict] = None

    for param in param_variants:
        stock_code = param["stock_code"]
        orgid = param["orgid"]
        column = param["column"]
        last_param_note = param["note"]
        if not stock_code:
            continue
        if not orgid:
            last_failure = "missing_query_code"
            continue

        for attempt in query_attempts:
            last_attempt = attempt
            keyword = attempt.get("keyword", "")
            se_date = attempt.get("se_date", "")
            category = attempt.get("category", "")
            strategy = attempt.get("strategy", "")
            payload = build_payload(stock_code, orgid, column, keyword, se_date, category)
            ann, http_status, fetch_failure, fetch_error_msg = fetch_announcements(payload)
            last_http = str(http_status or "")
            if fetch_failure:
                if fetch_failure in ("network_timeout", "unknown_error"):
                    log_fetch_error(
                        row.get("company_code", ""),
                        report_type,
                        strategy,
                        fetch_failure,
                        fetch_error_msg,
                    )
                if fetch_failure == "rate_limited":
                    return None, fetch_failure, last_http, last_param_note
                last_failure = fetch_failure
                time.sleep(SLEEP_SECONDS)
                continue
            match, excluded_match = pick_best_match(ann, report_type, expected_period, title_patterns)
            if match:
                match["matched_strategy"] = strategy
                match["http_status_code"] = last_http
                match["param_note"] = last_param_note
                match["matched_keyword"] = keyword
                match["matched_category"] = category
                match["matched_se_date"] = se_date
                return match, "success", last_http, last_param_note
            if excluded_match:
                last_title_excluded = excluded_match
                last_failure = "title_excluded"
            had_title_match = False
            had_period_issue = False
            had_pdf_issue = False
            for rec in ann:
                title = rec.get("announcementTitle") or ""
                if not match_report_title(title, title_patterns):
                    continue
                had_title_match = True
                if parse_report_period(title, report_type) != expected_period:
                    had_period_issue = True
                if not build_pdf_url(rec.get("adjunctUrl")):
                    had_pdf_issue = True
            if had_title_match and last_failure != "title_excluded":
                if had_period_issue:
                    last_failure = "period_mismatch"
                elif had_pdf_issue:
                    last_failure = "missing_pdf_url"
                else:
                    last_failure = "not_found"
            time.sleep(SLEEP_SECONDS)

    if last_attempt:
        extra = []
        if last_attempt.get("keyword"):
            extra.append(f"keyword={last_attempt['keyword']}")
        if last_attempt.get("category"):
            extra.append(f"category={last_attempt['category']}")
        if last_attempt.get("se_date"):
            extra.append(f"seDate={last_attempt['se_date']}")
        if extra:
            last_param_note = f"{last_param_note}; last_attempt: {last_attempt.get('strategy')}; " + "; ".join(extra)
    if last_title_excluded and last_failure == "title_excluded":
        return last_title_excluded, last_failure, last_http, last_param_note
    return None, last_failure, last_http, last_param_note


def build_skipped_row(row: Dict, report_type: str, expected_period: str) -> Dict:
    return {
        "company_code": row.get("company_code", ""),
        "company_name": row.get("company_name", ""),
        "exchange": row.get("exchange", ""),
        "board": row.get("board", ""),
        "mapping_status": row.get("mapping_status", ""),
        "cninfo_announcement_query_code": announcement_query_code(row) or "",
        "report_type": report_type,
        "expected_period": expected_period,
        "found": "no",
        "matched_title": "",
        "publish_time": "",
        "parsed_report_period": "",
        "pdf_url": "",
        "matched_strategy": "",
        "http_status_code": "",
        "failure_reason": "needs_orgid_mapping",
        "crawl_time": now_iso(),
        "notes": "mapping_status not mapped; skipped CNINFO query",
    }


def process_coverage_row(row: Dict, report_type: str, expected_period: str) -> Dict:
    cfg = REPORT_TYPES[report_type]
    base = {
        "company_code": row.get("company_code", ""),
        "company_name": row.get("company_name", ""),
        "exchange": row.get("exchange", ""),
        "board": row.get("board", ""),
        "mapping_status": row.get("mapping_status", ""),
        "cninfo_announcement_query_code": announcement_query_code(row) or "",
        "report_type": report_type,
        "expected_period": expected_period,
        "found": "no",
        "matched_title": "",
        "publish_time": "",
        "parsed_report_period": "",
        "pdf_url": "",
        "matched_strategy": "",
        "http_status_code": "",
        "failure_reason": "",
        "crawl_time": now_iso(),
        "notes": "",
    }

    if not is_mapped(row):
        base["failure_reason"] = "needs_orgid_mapping"
        base["notes"] = "mapping_status not mapped; skipped CNINFO query"
        return base

    match, failure, http_status, param_note = try_find_report(row, report_type, expected_period, cfg)
    base["http_status_code"] = http_status
    if match and failure == "success":
        _RUN_STATS.found_before_title_filter += 1
        _RUN_STATS.found_after_title_filter += 1
        note_parts = [f"param: {match.get('param_note', param_note)}"]
        note_parts.append(f"strategy: {match.get('matched_strategy', '')}")
        if match.get("matched_keyword"):
            note_parts.append(f"keyword: {match['matched_keyword']}")
        if match.get("matched_category"):
            note_parts.append(f"category: {match['matched_category']}")
        if match.get("matched_se_date"):
            note_parts.append(f"seDate: {match['matched_se_date']}")
        if (
            match.get("matched_strategy") == "quarterly_category_fallback"
            and row.get("exchange") == "SZSE"
            and is_quarterly_report(report_type)
        ):
            _RUN_STATS.szse_category_fallback_hits += 1
        if is_quarterly_report(report_type):
            note_parts.append(
                "quarterly_fallbacks: "
                + ", ".join(STRATEGY_ORDER + QUARTERLY_EXTRA_STRATEGIES)
            )
        else:
            note_parts.append(f"strategies: {', '.join(STRATEGY_ORDER)}")
        base.update(
            {
                "found": "yes",
                "matched_title": match["title"],
                "publish_time": match["publish_time"],
                "parsed_report_period": match["parsed_report_period"],
                "pdf_url": match["pdf_url"],
                "matched_strategy": match["matched_strategy"],
                "failure_reason": "success",
                "notes": "; ".join(note_parts),
            }
        )
    elif match and failure == "title_excluded":
        _RUN_STATS.found_before_title_filter += 1
        excluded_title = strip_title_markup(match.get("title") or match.get("clean_title", ""))
        excl_kw = get_title_exclusion_reason(excluded_title, report_type)
        if is_summary_only_title(excluded_title, report_type):
            _RUN_STATS.summary_title_hits += 1
        _RUN_STATS.title_excluded_rows += 1
        _RUN_STATS.exclusion_reason_counter[excl_kw] += 1
        if report_type == "annual_report":
            _RUN_STATS.annual_title_excluded += 1
        elif report_type == "semi_annual_report":
            _RUN_STATS.semi_title_excluded += 1
        elif report_type == "quarterly_report_q1":
            _RUN_STATS.q1_title_excluded += 1
        elif report_type == "quarterly_report_q3":
            _RUN_STATS.q3_title_excluded += 1
        base["failure_reason"] = "title_excluded"
        base["notes"] = (
            f"excluded_by_title_filter; keyword={excl_kw}; "
            f"would_match_title={excluded_title[:120]}"
        )
        if param_note:
            base["notes"] += f"; last_param: {param_note}"
    else:
        base["failure_reason"] = failure or "not_found"
        if param_note:
            base["notes"] = f"last_param: {param_note}"
    return base


def write_csv(rows: List[Dict]) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def load_csv_results() -> List[Dict]:
    with open(OUT_CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def coverage_status(pct: float) -> str:
    if pct >= 95:
        return "stable pipeline candidate"
    if pct >= 90:
        return "testing / usable candidate"
    if pct >= 80:
        return "partial"
    return "partial / not acceptable"


def row_effective_found(row: Dict) -> bool:
    """修正后口径：排除 title_excluded 与假阳性 found=yes。"""
    if (row.get("failure_reason") or "") == "needs_orgid_mapping":
        return False
    if (row.get("failure_reason") or "") == "title_excluded":
        return False
    if (row.get("found") or "").lower() != "yes":
        return False
    title = strip_title_markup(row.get("matched_title") or "")
    return not is_title_excluded(title, row.get("report_type", ""))


def row_found_before_title_filter(row: Dict) -> bool:
    """修正前口径：含说明会预告等假阳性。"""
    if (row.get("failure_reason") or "") == "needs_orgid_mapping":
        return False
    if (row.get("failure_reason") or "") == "title_excluded":
        return True
    return (row.get("found") or "").lower() == "yes"


def compute_quality_stats(mapped_rows: List[Dict]) -> Dict:
    """从 CSV 行或 _RUN_STATS 汇总 title filter / SZSE category 质量指标。"""
    found_before = sum(1 for r in mapped_rows if row_found_before_title_filter(r))
    found_after = sum(1 for r in mapped_rows if row_effective_found(r))
    title_excluded_rows = sum(
        1
        for r in mapped_rows
        if (r.get("failure_reason") or "") == "title_excluded"
        or (
            (r.get("found") or "").lower() == "yes"
            and is_title_excluded(
                strip_title_markup(r.get("matched_title") or ""),
                r.get("report_type", ""),
            )
        )
    )
    annual_excluded = sum(
        1
        for r in mapped_rows
        if r.get("report_type") == "annual_report"
        and (
            (r.get("failure_reason") or "") == "title_excluded"
            or (
                (r.get("found") or "").lower() == "yes"
                and is_title_excluded(
                    strip_title_markup(r.get("matched_title") or ""),
                    "annual_report",
                )
            )
        )
    )
    semi_excluded = sum(
        1
        for r in mapped_rows
        if r.get("report_type") == "semi_annual_report"
        and (
            (r.get("failure_reason") or "") == "title_excluded"
            or (
                (r.get("found") or "").lower() == "yes"
                and is_title_excluded(
                    strip_title_markup(r.get("matched_title") or ""),
                    "semi_annual_report",
                )
            )
        )
    )
    q1_excluded = sum(
        1
        for r in mapped_rows
        if r.get("report_type") == "quarterly_report_q1"
        and (
            (r.get("failure_reason") or "") == "title_excluded"
            or (
                (r.get("found") or "").lower() == "yes"
                and is_title_excluded(
                    strip_title_markup(r.get("matched_title") or ""),
                    "quarterly_report_q1",
                )
            )
        )
    )
    q3_excluded = sum(
        1
        for r in mapped_rows
        if r.get("report_type") == "quarterly_report_q3"
        and (
            (r.get("failure_reason") or "") == "title_excluded"
            or (
                (r.get("found") or "").lower() == "yes"
                and is_title_excluded(
                    strip_title_markup(r.get("matched_title") or ""),
                    "quarterly_report_q3",
                )
            )
        )
    )
    excluded_by_reason: Counter = Counter()
    for r in mapped_rows:
        if (r.get("failure_reason") or "") == "title_excluded":
            kw = ""
            notes = r.get("notes") or ""
            if "keyword=" in notes:
                m = re.search(r"keyword=([^;]+)", notes)
                if m:
                    kw = m.group(1).strip()
            if not kw:
                kw = get_title_exclusion_reason(
                    strip_title_markup(r.get("matched_title") or ""),
                    r.get("report_type", ""),
                )
            excluded_by_reason[classify_exclusion_keyword(kw)] += 1
    summary_hits = sum(
        1
        for r in mapped_rows
        if row_found_before_title_filter(r)
        and is_summary_only_title(
            strip_title_markup(r.get("matched_title") or ""),
            r.get("report_type", ""),
        )
    )
    szse_cat = sum(
        1
        for r in mapped_rows
        if row_effective_found(r)
        and r.get("exchange") == "SZSE"
        and is_quarterly_report(r.get("report_type", ""))
        and r.get("matched_strategy") == "quarterly_category_fallback"
    )
    if _RUN_STATS.title_excluded_rows > 0:
        title_excluded_rows = _RUN_STATS.title_excluded_rows
        annual_excluded = _RUN_STATS.annual_title_excluded
        semi_excluded = _RUN_STATS.semi_title_excluded
        q1_excluded = _RUN_STATS.q1_title_excluded
        q3_excluded = _RUN_STATS.q3_title_excluded
        summary_hits = _RUN_STATS.summary_title_hits
        if _RUN_STATS.found_before_title_filter > 0:
            found_before = _RUN_STATS.found_before_title_filter
            found_after = _RUN_STATS.found_after_title_filter
        if _RUN_STATS.szse_category_fallback_hits > 0:
            szse_cat = _RUN_STATS.szse_category_fallback_hits
        if _RUN_STATS.exclusion_reason_counter:
            excluded_by_reason = Counter()
            for kw, cnt in _RUN_STATS.exclusion_reason_counter.items():
                excluded_by_reason[classify_exclusion_keyword(kw)] += cnt
    return {
        "found_before_title_filter": found_before,
        "found_after_title_filter": found_after,
        "title_excluded_rows": title_excluded_rows,
        "title_excluded_count": title_excluded_rows,
        "annual_title_excluded": annual_excluded,
        "semi_title_excluded": semi_excluded,
        "q1_title_excluded": q1_excluded,
        "q3_title_excluded": q3_excluded,
        "excluded_by_report_type": {
            "annual_report": annual_excluded,
            "semi_annual_report": semi_excluded,
            "quarterly_report_q1": q1_excluded,
            "quarterly_report_q3": q3_excluded,
        },
        "excluded_by_reason": dict(excluded_by_reason),
        "summary_title_hits": summary_hits,
        "szse_category_fallback_hits": szse_cat,
    }


def summarize(rows: List[Dict], total_companies: int, mapped_count: int, skipped_companies: int) -> None:
    mapped_rows = [r for r in rows if (r.get("failure_reason") or "") != "needs_orgid_mapping"]
    skipped_rows = [r for r in rows if (r.get("failure_reason") or "") == "needs_orgid_mapping"]

    expected_count = len(mapped_rows)
    found_count = sum(1 for r in mapped_rows if row_effective_found(r))
    not_found_count = expected_count - found_count
    quality = compute_quality_stats(mapped_rows)

    overall_pct = (found_count / expected_count * 100) if expected_count else 0.0

    report_counter: Dict[str, Counter] = defaultdict(Counter)
    board_counter: Dict[str, Counter] = defaultdict(Counter)
    exchange_counter: Dict[str, Counter] = defaultdict(Counter)
    failure_counter = Counter(
        r.get("failure_reason", "")
        for r in mapped_rows
        if not row_effective_found(r)
    )

    pdf_avail = sum(1 for r in mapped_rows if row_effective_found(r) and (r.get("pdf_url") or "").strip())
    period_match = sum(
        1
        for r in mapped_rows
        if row_effective_found(r)
        and (r.get("parsed_report_period") or "") == (r.get("expected_period") or "")
    )

    for r in mapped_rows:
        rt = r.get("report_type", "")
        bd = r.get("board", "")
        ex = r.get("exchange", "")
        found = row_effective_found(r)
        report_counter[rt]["expected"] += 1
        board_counter[bd]["expected"] += 1
        exchange_counter[ex]["expected"] += 1
        if found:
            report_counter[rt]["found"] += 1
            board_counter[bd]["found"] += 1
            exchange_counter[ex]["found"] += 1

    rec_status = coverage_status(overall_pct)

    q1_exp = report_counter.get("quarterly_report_q1", {}).get("expected", 0)
    q1_fnd = report_counter.get("quarterly_report_q1", {}).get("found", 0)
    q3_exp = report_counter.get("quarterly_report_q3", {}).get("expected", 0)
    q3_fnd = report_counter.get("quarterly_report_q3", {}).get("found", 0)
    q1_pct = (q1_fnd / q1_exp * 100) if q1_exp else 0.0
    q3_pct = (q3_fnd / q3_exp * 100) if q3_exp else 0.0

    quarterly_rows = [
        r
        for r in mapped_rows
        if r.get("report_type") in ("quarterly_report_q1", "quarterly_report_q3")
        and row_effective_found(r)
    ]
    quarterly_strategy_counter = Counter(r.get("matched_strategy", "") for r in quarterly_rows)
    quarterly_extra_hits = sum(
        quarterly_strategy_counter.get(s, 0) for s in QUARTERLY_EXTRA_STRATEGIES
    )

    remaining_q_failures = [
        r
        for r in mapped_rows
        if r.get("report_type") in ("quarterly_report_q1", "quarterly_report_q3")
        and not row_effective_found(r)
    ]

    baseline = Q1Q3_OPTIMIZATION_BASELINE
    overall_delta = found_count - baseline["overall_found"]
    q1_delta = q1_fnd - baseline["q1_found"]
    q3_delta = q3_fnd - baseline["q3_found"]

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        title_suffix = f" — {RUN_LABEL} 扩展样本" if is_p1_run() else "（Era C Phase 1）"
        fh.write(f"# CNINFO A 类报告 coverage 验证{title_suffix}\n\n")

        fh.write("## 1. 数据来源\n")
        fh.write(f"- 跑次标签：**{RUN_LABEL}**\n")
        fh.write(f"- 公司映射：{os.path.relpath(MAPPING_CSV, BASE_DIR)}\n")
        fh.write(f"- 样本公司：{os.path.relpath(SAMPLE_CSV, BASE_DIR)}\n")
        fh.write(f"- 分层口径：{os.path.relpath(os.path.join(BASE_DIR, 'plans', 'cninfo_data_source_layered_inventory.md'), BASE_DIR)}\n")
        fh.write(f"- 脚本：{os.path.relpath(__file__, BASE_DIR)}\n\n")

        fh.write("## 2. Coverage 口径说明\n")
        fh.write("- **一行 = 一家公司 × 一个 report_type × 一个 expected_period**。\n")
        fh.write(
            "- 多种 query strategy（keyword_with_year → keyword_recent → longer_time_window → "
            "report_title_pattern；季报另增 quarterly_keyword_expanded / quarterly_seDate_fallback / "
            "quarterly_category_fallback）仅作**内部 fallback**，命中即停，**不拆成多行**。\n"
        )
        fh.write("- **分母（expected）**：`mapping_status=mapped` 的公司 × 各 report_type 的 expected_period 行数。\n")
        fh.write("- **分子（found / effective found）**：`found=yes` 且 `pdf_url` 非空、`parsed_report_period == expected_period`、")
        fh.write("标题匹配 `report_type`，且**未命中** official title exclusion（说明会/预告/披露提示/问询函回复/摘要/交叉披露提示等；`title_excluded` 不计入）。\n")
        fh.write("- **found_before_title_filter**：若策略曾命中 excluded 标题后仍继续 fallback，最终在 `_RUN_STATS` 中单独统计。\n")
        fh.write("- **skipped**：`needs_orgid_mapping` 公司行计入 CSV 与 skipped 统计，**不计入 coverage 分母**。\n\n")

        fh.write("## 3. 样本与覆盖\n")
        fh.write(f"- 样本公司数：{total_companies}\n")
        fh.write(f"- mapped 公司数：{mapped_count}\n")
        fh.write(f"- skipped（needs_orgid_mapping）公司数：{skipped_companies}\n")
        fh.write(f"- expected rows（coverage 分母）：{expected_count}\n")
        fh.write(f"- CSV 总行数（含 skipped 行）：{len(rows)}\n\n")

        fh.write("## 4. 结果分布\n")
        fh.write(f"- found：{found_count}\n")
        fh.write(f"- not_found：{not_found_count}\n")
        fh.write(f"- skipped rows（needs_orgid_mapping）：{len(skipped_rows)}\n\n")

        fh.write("## 5. Overall coverage\n")
        fh.write(f"- **coverage = found / expected = {found_count}/{expected_count} = {overall_pct:.2f}%**\n")
        fh.write(
            f"- （title filter 后口径；修正前 found = {quality['found_before_title_filter']}，"
            f"排除 {quality['title_excluded_rows']} 条假阳性）\n\n"
        )

        fh.write("## 5a. 质量口径（audit-aware title filter / SZSE category fallback）\n\n")
        fh.write(f"- **found_before_title_filter**：{quality['found_before_title_filter']}\n")
        fh.write(f"- **found_after_title_filter**（coverage 分子）：{quality['found_after_title_filter']}\n")
        fh.write(f"- **excluded_title_count** / **title_excluded_count**：{quality['title_excluded_count']}\n")
        fh.write("\n**excluded_by_report_type：**\n\n")
        fh.write("| report_type | 被排除行数 |\n")
        fh.write("|-------------|------------|\n")
        for rt, cnt in sorted(quality.get("excluded_by_report_type", {}).items()):
            fh.write(f"| {rt} | {cnt} |\n")
        fh.write("\n**excluded_by_reason（归类）：**\n\n")
        if quality.get("excluded_by_reason"):
            fh.write("| reason | count |\n")
            fh.write("|--------|-------|\n")
            for reason, cnt in sorted(quality["excluded_by_reason"].items(), key=lambda x: -x[1]):
                fh.write(f"| {reason} | {cnt} |\n")
        else:
            fh.write("- （本次无 title_excluded 行）\n")
        fh.write(
            f"\n- **摘要类命中（单独统计，不计正式全文 found）**：{quality['summary_title_hits']}\n"
        )
        fh.write(
            f"- **Q1/Q3 通过 SZSE quarterly_category_fallback 新增命中**："
            f"{quality['szse_category_fallback_hits']}\n"
        )
        if is_p1_run():
            p1b = P1_PRE_TITLE_FILTER_BASELINE
            fh.write(
                f"\n- P1 title-filter 修正前 retrieval：**{p1b['found']}/{p1b['expected']} = {p1b['pct']:.2f}%**"
                f"（含假阳性；quality audit 标题级 pass rate **{p1b['audit_found_pass_rate']:.0f}%**，"
                f"粗算有效 **~{p1b['audit_estimated_effective_pct']:.1f}%**）\n"
            )
            fh.write(
                f"- 本次重跑（official title filter 后）effective coverage = **{overall_pct:.2f}%**\n"
            )
            fh.write(
                "- 参考：[cninfo_report_p1_quality_audit_results.md](cninfo_report_p1_quality_audit_results.md)\n"
            )
        fh.write("\n")

        fh.write("## 6. 按 report_type\n")
        for rt in sorted(report_counter.keys()):
            exp = report_counter[rt]["expected"]
            fnd = report_counter[rt]["found"]
            pct = (fnd / exp * 100) if exp else 0
            fh.write(f"- {rt}: {fnd}/{exp} ({pct:.2f}%)\n")
        fh.write("\n")

        fh.write("## 7. 按 board\n")
        for bd in sorted(board_counter.keys()):
            exp = board_counter[bd]["expected"]
            fnd = board_counter[bd]["found"]
            pct = (fnd / exp * 100) if exp else 0
            fh.write(f"- {bd}: {fnd}/{exp} ({pct:.2f}%)\n")
        fh.write("\n")

        fh.write("## 8. 按 exchange\n")
        for ex in sorted(exchange_counter.keys()):
            exp = exchange_counter[ex]["expected"]
            fnd = exchange_counter[ex]["found"]
            pct = (fnd / exp * 100) if exp else 0
            fh.write(f"- {ex}: {fnd}/{exp} ({pct:.2f}%)\n")
        fh.write("\n")

        fh.write("## 9. 字段可得性（mapped expected 行）\n")
        fh.write(f"- pdf_url 可得（found 行）：{pdf_avail}/{expected_count}\n")
        fh.write(f"- parsed_report_period 与 expected_period 一致（found 行）：{period_match}/{found_count if found_count else 1}\n\n")

        fh.write("## 10. 主要 failure_reason（not_found 行）\n")
        for reason, cnt in failure_counter.most_common():
            if reason == "success":
                continue
            fh.write(f"- {reason}：{cnt}\n")
        if not any(k != "success" for k in failure_counter):
            fh.write("- （无 not_found 行）\n")
        fh.write("\n")

        fh.write("## 11. 与旧口径的区别\n")
        fh.write("- 旧 [cninfo_report_announcement_validation_summary.md](cninfo_report_announcement_validation_summary.md)：`success 368/780` 按 **company × report_type × query_strategy** 计行，同一报告可能多行 success/failed。\n")
        fh.write("- 本摘要：**company × expected_period** 一行；strategy 仅记录 `matched_strategy`。\n\n")

        fh.write("## 12. recommended_status\n")
        fh.write(f"- overall **effective** coverage（title filter 后）{overall_pct:.2f}% → **{rec_status}**\n")
        fh.write("- 阈值：<80% partial/not acceptable；80–90% partial；90–95% testing/usable candidate；95%+ stable pipeline candidate。\n")
        if is_p1_run():
            p1b = P1_PRE_TITLE_FILTER_BASELINE
            fh.write(
                f"- P1 quality audit 已显示修正前 **{p1b['found']}/{p1b['expected']} = {p1b['pct']:.2f}%** retrieval 含约 "
                f"**{100 - p1b['audit_found_pass_rate']:.0f}%** found 样本标题级假阳性；"
                f"**勿将旧 94.22% 视为 accuracy**。\n"
            )
            fh.write(
                "- 本次跑次使用 **official report title filter**（全 report_type exclusion）；coverage 以 **found_after_title_filter** 为准。\n"
            )
            fh.write("- **不写 verified**；**不写 full-market stable**；仅代表当前 P1 扩展样本。\n\n")
        else:
            fh.write("- **不写 verified**；仅代表当前 40 家 P0 样本小样本结论。\n\n")

        fh.write("## 13. 边界确认\n")
        fh.write("- 未下载 PDF 正文；未解析 PDF；未计算 hash。\n")
        fh.write("- 未做数据库 / MinIO 接入；未使用 BrowserUser。\n")
        fh.write("- 请求间 sleep；不绕过登录/验证码/付费/权限。\n")
        fh.write("- 本摘要基于当前脚本运行结果生成。\n")
        fh.write(f"- 参数诊断详见 [{os.path.basename(OUT_DIAGNOSTICS)}]({os.path.basename(OUT_DIAGNOSTICS)})。\n")
        fh.write(
            f"- 季报失败诊断详见 [cninfo_report_quarterly_failure_diagnostics.md]"
            f"(cninfo_report_quarterly_failure_diagnostics.md)。\n"
        )
        if is_p1_run():
            fh.write(f"- P1 计划详见 [cninfo_report_p1_expansion_plan.md](cninfo_report_p1_expansion_plan.md)。\n\n")
        else:
            fh.write("\n")

        if is_p1_run():
            p0 = P0_COVERAGE_BASELINE
            fh.write("## 14. 与 P0 baseline 对比\n\n")
            fh.write("- P0 小样本（30 mapped）：**113/120 = 94.17%** — mechanism passed，非全市场结论\n")
            fh.write(f"- P1 本次（{mapped_count} mapped）：**{found_count}/{expected_count} = {overall_pct:.2f}%**"
                     f"（Δ overall {found_count - p0['overall_found']:+d}）\n\n")
            fh.write("| 维度 | P0 | P1（本次） |\n")
            fh.write("|------|-----|----------|\n")
            fh.write(f"| overall | {p0['overall_found']}/{p0['overall_expected']} ({p0['overall_pct']:.2f}%) | "
                     f"{found_count}/{expected_count} ({overall_pct:.2f}%) |\n")
            fh.write(f"| annual_report | {p0['annual'][0]}/{p0['annual'][1]} | "
                     f"{report_counter.get('annual_report', {}).get('found', 0)}/"
                     f"{report_counter.get('annual_report', {}).get('expected', 0)} |\n")
            fh.write(f"| semi_annual_report | {p0['semi'][0]}/{p0['semi'][1]} | "
                     f"{report_counter.get('semi_annual_report', {}).get('found', 0)}/"
                     f"{report_counter.get('semi_annual_report', {}).get('expected', 0)} |\n")
            fh.write(f"| quarterly_report_q1 | {p0['q1'][0]}/{p0['q1'][1]} | {q1_fnd}/{q1_exp} |\n")
            fh.write(f"| quarterly_report_q3 | {p0['q3'][0]}/{p0['q3'][1]} | {q3_fnd}/{q3_exp} |\n")
            fh.write(f"| SSE | {p0['sse'][0]}/{p0['sse'][1]} | "
                     f"{exchange_counter.get('SSE', {}).get('found', 0)}/"
                     f"{exchange_counter.get('SSE', {}).get('expected', 0)} |\n")
            fh.write(f"| SZSE | {p0['szse'][0]}/{p0['szse'][1]} | "
                     f"{exchange_counter.get('SZSE', {}).get('found', 0)}/"
                     f"{exchange_counter.get('SZSE', {}).get('expected', 0)} |\n")
            fh.write(f"| BSE | {p0['bse'][0]}/{p0['bse'][1]} | "
                     f"{exchange_counter.get('BSE', {}).get('found', 0)}/"
                     f"{exchange_counter.get('BSE', {}).get('expected', 0)} |\n\n")
            fh.write("### P1 remaining gaps（not_found 行）\n\n")
            not_found_rows = [
                r for r in mapped_rows if not row_effective_found(r)
            ]
            if not_found_rows:
                fh.write("| company_code | company_name | exchange | board | report_type | failure_reason |\n")
                fh.write("|--------------|--------------|----------|-------|-------------|----------------|\n")
                for r in sorted(
                    not_found_rows,
                    key=lambda x: (x.get("exchange", ""), x.get("company_code", ""), x.get("report_type", "")),
                ):
                    fh.write(
                        f"| {r.get('company_code', '')} | {r.get('company_name', '')} | "
                        f"{r.get('exchange', '')} | {r.get('board', '')} | "
                        f"{r.get('report_type', '')} | {r.get('failure_reason', '')} |\n"
                    )
            else:
                fh.write("- （无 not_found 行）\n")
            fh.write("\n")
        else:
            fh.write("## 14. Q1/Q3 季报策略优化对比（本轮仅改季报）\n\n")
            fh.write("- **本轮变更范围**：仅 `quarterly_report_q1` / `quarterly_report_q3` 关键词、title_patterns、")
            fh.write("seDate/category fallback；**annual_report / semi_annual_report 逻辑未改**。\n\n")
            fh.write("### 优化前（baseline）\n")
            fh.write(
                f"- overall：{baseline['overall_found']}/{baseline['overall_expected']} "
                f"= {baseline['overall_pct']:.2f}%\n"
            )
            fh.write(f"- Q1：{baseline['q1_found']}/{baseline['q1_expected']} "
                     f"= {baseline['q1_found']/baseline['q1_expected']*100:.2f}%\n")
            fh.write(f"- Q3：{baseline['q3_found']}/{baseline['q3_expected']} "
                     f"= {baseline['q3_found']/baseline['q3_expected']*100:.2f}%\n\n")
            fh.write("### 优化后（本次运行）\n")
            fh.write(f"- overall：**{found_count}/{expected_count} = {overall_pct:.2f}%**"
                     f"（Δ {overall_delta:+d}）\n")
            fh.write(f"- Q1：**{q1_fnd}/{q1_exp} = {q1_pct:.2f}%**（Δ {q1_delta:+d}）\n")
            fh.write(f"- Q3：**{q3_fnd}/{q3_exp} = {q3_pct:.2f}%**（Δ {q3_delta:+d}）\n\n")
            fh.write("### 季报命中策略分布（found 行）\n")
            if quarterly_strategy_counter:
                for strategy, cnt in quarterly_strategy_counter.most_common():
                    fh.write(f"- {strategy or '(empty)'}：{cnt}\n")
            else:
                fh.write("- （无季报 found 行）\n")
            fh.write(f"\n- 其中新增季报 fallback 策略命中：**{quarterly_extra_hits}** 行")
            fh.write("（quarterly_keyword_expanded / quarterly_seDate_fallback / quarterly_category_fallback）\n\n")
            fh.write("### 仍 not_found 的季报样本\n")
            if remaining_q_failures:
                fh.write("| company_code | company_name | exchange | board | report_type | failure_reason |\n")
                fh.write("|--------------|--------------|----------|-------|-------------|----------------|\n")
                for r in sorted(
                    remaining_q_failures,
                    key=lambda x: (x.get("exchange", ""), x.get("company_code", ""), x.get("report_type", "")),
                ):
                    fh.write(
                        f"| {r.get('company_code', '')} | {r.get('company_name', '')} | "
                        f"{r.get('exchange', '')} | {r.get('board', '')} | "
                        f"{r.get('report_type', '')} | {r.get('failure_reason', '')} |\n"
                    )
            else:
                fh.write("- （季报全部 found）\n")
            fh.write("\n")


def sample_payload_for_row(row: Dict, keyword: str = "2024年年度报告") -> Dict:
    """取该公司第一个有效参数组合，生成 hisAnnouncement/query 样例 payload。"""
    variants = query_param_variants(row)
    if not variants:
        v = {"stock_code": announcement_query_code(row) or "", "orgid": "", "column": "sse"}
    else:
        v = variants[0]
    return build_payload(v["stock_code"], v["orgid"], v["column"], keyword, "")


def probe_param_sample(row: Dict, keyword: str = "年度报告") -> Dict:
    """对单家公司发一次轻量探测（diagnostics 用，不计入 coverage）。"""
    variants = query_param_variants(row)
    if not variants:
        return {"probe_status": "no_variants", "announcement_count": 0}
    v = variants[0]
    payload = build_payload(v["stock_code"], v["orgid"], v["column"], keyword, "")
    ann, http_status, fetch_failure, _fetch_error_msg = fetch_announcements(payload)
    return {
        "stock_code": v["stock_code"],
        "orgid": v["orgid"],
        "column": v["column"],
        "stock_field": payload["stock"],
        "searchkey": keyword,
        "plate": payload["plate"],
        "category": payload["category"],
        "seDate": payload["seDate"],
        "http_status": http_status,
        "fetch_failure": fetch_failure or "ok",
        "announcement_count": len(ann),
        "first_title": (ann[0].get("announcementTitle") or "")[:80] if ann else "",
    }


def write_parameter_diagnostics(
    mapping_rows: List[Dict],
    *,
    probe: bool = False,
) -> None:
    """输出 SSE / SZSE / BSE 参数映射与每板块样例（可选一次探测）。"""
    mapped = [r for r in mapping_rows if is_mapped(r)]
    by_key: Dict[Tuple[str, str], List[Dict]] = defaultdict(list)
    for row in mapped:
        by_key[(row.get("exchange", ""), row.get("board", ""))].append(row)

    lines: List[str] = [
        "# CNINFO hisAnnouncement/query 参数诊断（Era C Phase 1）",
        "",
        f"- 生成时间：{now_iso()}",
        f"- 脚本：{os.path.relpath(__file__, BASE_DIR)}",
        f"- 映射输入：{os.path.relpath(MAPPING_CSV, BASE_DIR)}",
        "",
        "## 1. 根因摘要（SZSE / BSE coverage=0）",
        "",
        "| 板块 | 旧行为 | 问题 | 修正 |",
        "|------|--------|------|------|",
        "| SSE 主板 / 科创板 | `column=sse`，`stock=code,orgId` | 无（100%） | 保持 |",
        "| SZSE 创业板 | `column=szse`，orgId=`gssh0{code}`（F10 经验规则） | `gssh*` 对 **公告查询** 无效 → `empty_response` | 优先 `CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES`（numeric orgId）；fallback topSearch |",
        "| BSE 北交所 | `column=neeq`（旧脚本） | probe/eval 使用 `column=bj`；`neeq` 导致 `empty_response` | `column=bj`，fallback `neeq`；stock 试 `920xxx` 与 `430xxx` |",
        "",
        "## 2. BOARD_COLUMN_MAP（board × exchange → column）",
        "",
        "| board | exchange | column | column fallbacks |",
        "|-------|----------|--------|------------------|",
    ]
    seen_cols: set[Tuple[str, str]] = set()
    for (board, exchange), cols in sorted(BOARD_COLUMN_MAP.items()):
        if (board, exchange) in seen_cols:
            continue
        seen_cols.add((board, exchange))
        primary = cols
        fallbacks = ", ".join(COLUMN_FALLBACKS.get(primary, [primary]))
        lines.append(f"| {board} | {exchange} | `{primary}` | `{fallbacks}` |")

    lines.extend(
        [
            "",
            "## 3. 与 probe_cninfo EXCHANGE_COLUMN 对照",
            "",
            "| exchange | probe_cninfo column | 本脚本 primary column |",
            "|----------|---------------------|-------------------------|",
            "| SSE | `sse` | `sse` |",
            "| SZSE | `szse` | `szse` |",
            "| BSE | `bj` | `bj`（旧为 `neeq`） |",
            "",
            "## 4. 公共 payload 字段（build_payload）",
            "",
            "- `stock`：`{stock_code},{orgid}`（orgId 非空时）",
            "- `column`：见上表",
            "- `plate` / `category` / `trade`：空字符串",
            "- `tabName`：`fulltext`",
            "- `seDate`：策略相关（`keyword_with_year` 等为空；`longer_time_window` 为近三年）",
            "- `searchkey`：策略关键词",
            "- `isHLtitle`：`true`",
            "- `secid`：空",
            "",
            "## 5. 各 exchange / board 请求参数样例",
            "",
        ]
    )

    for (exchange, board), rows in sorted(by_key.items()):
        sample = rows[0]
        company = sample.get("company_code", "")
        lines.append(f"### {exchange} / {board}（样本：{company} {sample.get('company_name', '')}）")
        lines.append("")
        lines.append("| 字段 | 映射 CSV | 查询用值 |")
        lines.append("|------|----------|----------|")
        lines.append(f"| company_code | `{company}` | — |")
        lines.append(f"| exchange | `{exchange}` | — |")
        lines.append(f"| board | `{board}` | — |")
        lines.append(f"| cninfo_stock_code | `{sample.get('cninfo_stock_code', '')}` | stock 候选 |")
        lines.append(f"| cninfo_announcement_query_code | `{sample.get('cninfo_announcement_query_code', '')}` | stock 候选 |")
        lines.append(f"| cninfo_org_id（CSV） | `{sample.get('cninfo_org_id', '')}` | orgId 候选 |")
        primary_col = BOARD_COLUMN_MAP.get((board, exchange), "sse")
        lines.append(f"| column | — | `{primary_col}` |")

        variants = query_param_variants(sample)
        lines.append("")
        lines.append(f"**参数组合数（内部 fallback，不拆 coverage 行）**：{len(variants)}")
        lines.append("")
        lines.append("前 3 组 param variant：")
        lines.append("")
        for i, v in enumerate(variants[:3], 1):
            payload = build_payload(v["stock_code"], v["orgid"], v["column"], "2024年年度报告", "")
            lines.append(f"{i}. `{v['note']}`")
            lines.append(f"   - `stock={payload['stock']}`")
            lines.append(f"   - `column={payload['column']}` `searchkey=2024年年度报告` `seDate=` `plate=` `category=`")
            lines.append("")

        if company in CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES:
            lines.append(
                f"- 创业板 orgId override：`{company}` → `{CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES[company]}` "
                f"（替代 CSV 中 `{sample.get('cninfo_org_id', '')}`）"
            )
            lines.append("")

        if probe:
            lines.append("**探测（keyword=年度报告，仅首组参数）**：")
            probe_result = probe_param_sample(sample)
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(probe_result, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")
            time.sleep(SLEEP_SECONDS)

    lines.extend(
        [
            "## 6. 创业板 P0 样本 orgId override 表",
            "",
            "| company_code | CSV orgId (gssh) | announcement orgId override |",
            "|--------------|------------------|----------------------------|",
        ]
    )
    for row in sorted(mapped, key=lambda r: r.get("company_code", "")):
        if row.get("board") != "创业板":
            continue
        code = row.get("company_code", "")
        override = CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES.get(code, "—")
        lines.append(f"| {code} | `{row.get('cninfo_org_id', '')}` | `{override}` |")

    lines.extend(
        [
            "",
            "## 7. 说明",
            "",
            "- 多种 stock / orgId / column 组合仅在 `try_find_report` 内部 fallback，**一行仍 = company × report_type × expected_period**。",
            "- 未下载 PDF；未改 `parse_report_period`。",
            "- 完整 coverage 请运行：`python lab/validate_cninfo_report_coverage.py`",
            "- 仅生成本诊断（可加 `--probe-samples` 做一次探测）：`python lab/validate_cninfo_report_coverage.py --diagnostics-only`",
            "",
        ]
    )

    with open(OUT_DIAGNOSTICS, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    ensure_dirs()
    _RUN_STATS.reset()
    mapping_rows = load_mapping()
    mapped_rows = [r for r in mapping_rows if is_mapped(r)]
    skipped_companies = len(mapping_rows) - len(mapped_rows)

    results: List[Dict] = []
    progress = CoverageProgressLogger(len(mapped_rows))
    print(
        f"[coverage] start {RUN_LABEL} | companies={len(mapping_rows)} mapped={len(mapped_rows)} "
        f"expected_rows≈{len(mapped_rows) * sum(len(p) for p in EXPECTED_PERIODS.values())}",
        flush=True,
    )
    for row in mapping_rows:
        company_results: List[Dict] = []
        for report_type, periods in EXPECTED_PERIODS.items():
            for expected_period in periods:
                company_results.append(process_coverage_row(row, report_type, expected_period))
        results.extend(company_results)
        progress.on_company_done(row, company_results)

    write_csv(results)
    summarize(results, len(mapping_rows), len(mapped_rows), skipped_companies)
    write_parameter_diagnostics(mapping_rows, probe=False)
    print(f"Wrote {len(results)} rows -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")
    print(f"Diagnostics -> {OUT_DIAGNOSTICS}")
    print(
        f"[coverage] finished | rows found={progress.found_rows} not_found={progress.not_found_rows} "
        f"skipped={progress.skipped_rows} | elapsed={format_duration(progress.elapsed_seconds())}",
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CNINFO A 类 report coverage 验证")
    parser.add_argument(
        "--input-mapping",
        default=None,
        help="identity mapping CSV（默认 P0：outputs/validation/cninfo_company_identity_mapping.csv）",
    )
    parser.add_argument(
        "--output-prefix",
        default=None,
        help="输出前缀（默认 P0：outputs/validation/cninfo_report_coverage → *_validation.csv）",
    )
    parser.add_argument(
        "--sample-csv",
        default=None,
        help="样本清单 CSV（写入 summary；P1 默认 cninfo_report_p1_sample_companies.csv）",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="仅从已有 CSV 重生成 summary，不访问 CNINFO",
    )
    parser.add_argument(
        "--diagnostics-only",
        action="store_true",
        help="仅生成参数诊断 markdown，不跑完整 coverage",
    )
    parser.add_argument(
        "--probe-samples",
        action="store_true",
        help="与 --diagnostics-only 联用：对各板块样本发一次轻量探测",
    )
    args = parser.parse_args()
    configure_run_paths(args.input_mapping, args.output_prefix, args.sample_csv)

    if args.diagnostics_only:
        ensure_dirs()
        mapping_rows = load_mapping()
        write_parameter_diagnostics(mapping_rows, probe=args.probe_samples)
        print(f"Diagnostics -> {OUT_DIAGNOSTICS}")
        if args.probe_samples:
            print("(included per-board probe requests)")
    elif args.summary_only:
        ensure_dirs()
        mapping_rows = load_mapping()
        mapped_rows = [r for r in mapping_rows if is_mapped(r)]
        rows = load_csv_results()
        if not rows:
            print(f"No rows in {OUT_CSV}; run without --summary-only first.")
        else:
            summarize(rows, len(mapping_rows), len(mapped_rows), len(mapping_rows) - len(mapped_rows))
            print(f"Summary -> {OUT_SUMMARY}")
    else:
        # 请在本地、合规网络环境下手动执行。
        main()
