"""
CNINFO latest announcement small-sample validation (Issue #82).

Inputs:
- outputs/validation/cninfo_p0_sample_companies.csv  (40 companies from Issue #81)
- Local orgId + meta info from outputs/generalization/full_market_2024/**/meta.json

Outputs:
- outputs/validation/cninfo_latest_announcement_validation.csv
- outputs/validation/cninfo_latest_announcement_validation_summary.md

Behavior:
- Offline-friendly; uses CNINFO public HTTP endpoint if reachable.
- No login bypass, no captcha bypass, no high-frequency requests.
- Does NOT download PDF bodies, compute hash, or touch databases.
"""

from __future__ import annotations

import csv
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_p0_sample_companies.csv")
FULL_MARKET_DIR = os.path.join(BASE_DIR, "outputs", "generalization", "full_market_2024")
VALIDATION_DIR = os.path.join(BASE_DIR, "outputs", "validation")
OUT_CSV = os.path.join(VALIDATION_DIR, "cninfo_latest_announcement_validation.csv")
SUMMARY_MD = os.path.join(VALIDATION_DIR, "cninfo_latest_announcement_validation_summary.md")

REQUEST_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"

# Map board/exchange to directory and CNINFO column hints.
BOARD_DIR_MAP = {
    ("主板", "SSE"): ("sse_main", "sse"),
    ("主板", "SZSE"): ("szse_main", "szse"),
    ("创业板", "SZSE"): ("chinext", "szse"),
    ("科创板", "SSE"): ("star", "sse"),
    ("北交所", "BSE"): ("bse", "neeq"),
}

CSV_FIELDS = [
    "company_code",
    "company_name",
    "cninfo_query_code",
    "announcement_title",
    "announcement_type",
    "publish_time",
    "source_url",
    "pdf_url",
    "file_type",
    "crawl_time",
    "validation_status",
    "failure_reason",
    "access_method",
    "http_status_code",
    "notes",
]

FAILURE_REASONS = {
    "success",
    "partial_missing_pdf_url",
    "missing_company_mapping",
    "missing_announcement_title",
    "missing_publish_time",
    "missing_source_url",
    "missing_pdf_url",
    # no_announcements_returned: could be true no data, code mapping mismatch, or network/VPN issues
    "no_announcements_returned",
    "page_structure_changed",
    "pagination_error",
    "rate_limited",
    "js_render_required",
    "captcha_or_login_required",
    "network_timeout",
    "http_error",
    "unknown_error",
}

BSE_OLD_PREFIX = "430"
BSE_NEW_PREFIX = "920"


def ensure_dirs() -> None:
    os.makedirs(VALIDATION_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_samples() -> List[Dict]:
    rows = []
    with open(SAMPLE_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def load_orgid(company_code: str, board: str, exchange: str) -> Tuple[str | None, str | None]:
    key = (board, exchange)
    if key not in BOARD_DIR_MAP:
        return None, None
    dir_name, _ = BOARD_DIR_MAP[key]
    meta_path = os.path.join(FULL_MARKET_DIR, dir_name, company_code, "meta.json")
    if not os.path.isfile(meta_path):
        return dir_name, None
    try:
        with open(meta_path, "r", encoding="utf-8") as fh:
            meta = json.load(fh)
            return dir_name, meta.get("orgid")
    except Exception:
        return dir_name, None


def build_payload(company_code: str, orgid: str | None, column: str) -> Dict:
    # CNINFO expects "stock": "<code>,<orgid>" when orgid is available; fallback to code only.
    stock_value = f"{company_code},{orgid}" if orgid else company_code
    return {
        "stock": stock_value,
        "searchkey": "",
        "plate": "",
        "category": "",
        "trade": "",
        "column": column,
        "tabName": "fulltext",
        "pageSize": 3,
        "pageNum": 1,
        "seDate": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": True,
    }


def fetch_announcements(payload: Dict) -> Tuple[List[Dict], int | None, str | None]:
    try:
        resp = requests.post(REQUEST_URL, data=payload, timeout=8)
        status = resp.status_code
        if status != 200:
            return [], status, "http_error"
        data = resp.json()
        ann = data.get("announcements") or []
        return ann, status, None
    except requests.exceptions.Timeout:
        return [], None, "network_timeout"
    except Exception:
        return [], None, "unknown_error"


def build_pdf_url(adjunct_url: str | None) -> str | None:
    if not adjunct_url:
        return None
    prefix = "http://static.cninfo.com.cn/"
    return prefix + adjunct_url.lstrip("/")


def normalize_publish_time(ts: int | None) -> str | None:
    if not ts:
        return None
    # CNINFO returns milliseconds epoch.
    try:
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()
    except Exception:
        return None


def classify_record(rec: Dict) -> Tuple[str, str]:
    title = rec.get("announcementTitle")
    publish_time = rec.get("announcementTime")
    source = rec.get("announcementUrl") or rec.get("adjunctUrl") or rec.get("announcementId")
    pdf_url = rec.get("adjunctUrl")

    if not title:
        return "missing_announcement_title", "title missing"
    if not publish_time:
        return "missing_publish_time", "publish_time missing"
    if not source:
        return "missing_source_url", "source_url missing"
    if not pdf_url:
        return "partial_missing_pdf_url", "pdf_url missing"
    return "success", ""


def map_bse_code_if_needed(company_code: str) -> str | None:
    if company_code.startswith(BSE_OLD_PREFIX) and len(company_code) >= 6:
        return BSE_NEW_PREFIX + company_code[len(BSE_OLD_PREFIX) :]
    return None


def process_company(sample: Dict) -> List[Dict]:
    company_code = sample.get("company_code", "").strip()
    company_name = sample.get("company_name", "").strip()
    board = sample.get("board", "").strip()
    exchange = sample.get("exchange", "").strip()
    access_method = "HTTP"
    cninfo_query_code = company_code

    dir_name, orgid = load_orgid(company_code, board, exchange)
    if orgid is None:
        failure = {
            "company_code": company_code,
            "company_name": company_name,
            "cninfo_query_code": cninfo_query_code,
            "announcement_title": "",
            "announcement_type": "unknown",
            "publish_time": "",
            "source_url": "",
            "pdf_url": "",
            "file_type": "",
            "crawl_time": now_iso(),
            "validation_status": "failed",
            "failure_reason": "missing_company_mapping",
            "access_method": access_method,
            "http_status_code": "",
            "notes": f"missing orgid (dir={dir_name})",
        }
        return [failure]

    column = BOARD_DIR_MAP.get((board, exchange), ("", "sse"))[1]
    payload = build_payload(company_code, orgid, column)
    ann, http_status, fetch_failure = fetch_announcements(payload)

    if fetch_failure:
        return [
            {
                "company_code": company_code,
                "company_name": company_name,
                "cninfo_query_code": cninfo_query_code,
                "announcement_title": "",
                "announcement_type": "unknown",
                "publish_time": "",
                "source_url": "",
                "pdf_url": "",
                "file_type": "",
                "crawl_time": now_iso(),
                "validation_status": "failed",
                "failure_reason": fetch_failure if fetch_failure in FAILURE_REASONS else "unknown_error",
                "access_method": access_method,
                "http_status_code": http_status or "",
                "notes": "request error",
            }
        ]

    rows: List[Dict] = []
    retry_used = False

    if not ann and company_code.startswith(BSE_OLD_PREFIX):
        mapped_code = map_bse_code_if_needed(company_code)
        if mapped_code:
            cninfo_query_code = mapped_code
            payload2 = build_payload(mapped_code, orgid, column)
            ann2, http_status2, fetch_failure2 = fetch_announcements(payload2)
            retry_used = True
            if fetch_failure2:
                return [
                    {
                        "company_code": company_code,
                        "company_name": company_name,
                        "cninfo_query_code": cninfo_query_code,
                        "announcement_title": "",
                        "announcement_type": "unknown",
                        "publish_time": "",
                        "source_url": "",
                        "pdf_url": "",
                        "file_type": "",
                        "crawl_time": now_iso(),
                        "validation_status": "failed",
                        "failure_reason": fetch_failure2 if fetch_failure2 in FAILURE_REASONS else "unknown_error",
                        "access_method": access_method,
                        "http_status_code": http_status2 or "",
                        "notes": "mapped BSE code retry failed",
                    }
                ]
            ann = ann2
            http_status = http_status2

    if not ann:
        rows.append(
            {
                "company_code": company_code,
                "company_name": company_name,
                "cninfo_query_code": cninfo_query_code,
                "announcement_title": "",
                "announcement_type": "unknown",
                "publish_time": "",
                "source_url": "",
                "pdf_url": "",
                "file_type": "",
                "crawl_time": now_iso(),
                "validation_status": "failed",
                "failure_reason": "no_announcements_returned",
                "access_method": access_method,
                "http_status_code": http_status or "",
                "notes": "no announcements returned; manual check recommended; possible code mapping or VPN/network issue",
            }
        )
        return rows

    for rec in ann[:3]:
        status_reason, notes = classify_record(rec)
        status = "success" if status_reason == "success" else "partial"

        pdf_url = build_pdf_url(rec.get("adjunctUrl"))
        publish_time_iso = normalize_publish_time(rec.get("announcementTime"))
        source_url = rec.get("announcementUrl") or (pdf_url or "")
        rows.append(
            {
                "company_code": company_code,
                "company_name": company_name,
                "cninfo_query_code": cninfo_query_code,
                "announcement_title": rec.get("announcementTitle") or "",
                "announcement_type": rec.get("announcementType") or "unknown",
                "publish_time": publish_time_iso or "",
                "source_url": source_url,
                "pdf_url": pdf_url or "",
                "file_type": rec.get("adjunctType") or "pdf",
                "crawl_time": now_iso(),
                "validation_status": status,
                "failure_reason": status_reason,
                "access_method": access_method,
                "http_status_code": http_status or "",
                "notes": notes if not retry_used else f"{notes}; retried with mapped BSE code",
            }
        )

    return rows


def write_csv(rows: List[Dict]) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_summary(rows: List[Dict], stats: Dict, failure_counter: Counter) -> None:
    total_companies = stats.get("companies", 0)
    success_companies = stats.get("success_companies", 0)
    partial_companies = stats.get("partial_companies", 0)
    failed_companies = stats.get("failed_companies", 0)

    title_ok = sum(1 for r in rows if r["announcement_title"])
    publish_ok = sum(1 for r in rows if r["publish_time"])
    source_ok = sum(1 for r in rows if r["source_url"])
    pdf_ok = sum(1 for r in rows if r["pdf_url"])
    type_ok = sum(1 for r in rows if r["announcement_type"] and r["announcement_type"] != "unknown")
    mapped_success_companies = len(
        {
            r["company_code"]
            for r in rows
            if r["validation_status"] == "success"
            and r.get("cninfo_query_code")
            and r["cninfo_query_code"] != r["company_code"]
        }
    )

    with open(SUMMARY_MD, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO 最新公告列表小样本验证（Issue #82）\n\n")
        fh.write("## 数据来源\n")
        fh.write(f"- 输入样本：{os.path.relpath(SAMPLE_CSV, BASE_DIR)}\n")
        fh.write("- CNINFO 公开接口：/new/hisAnnouncement/query（HTTP POST）\n\n")

        fh.write("## 样本概况\n")
        fh.write(f"- 样本公司数：{total_companies}\n")
        fh.write(f"- 成功公司数：{success_companies}\n")
        fh.write(f"- partial 公司数：{partial_companies}\n")
        fh.write(f"- 失败公司数：{failed_companies}\n\n")

        fh.write("## 字段可得性（按行计数）\n")
        fh.write(f"- announcement_title：{title_ok}/{len(rows)}\n")
        fh.write(f"- publish_time：{publish_ok}/{len(rows)}\n")
        fh.write(f"- source_url：{source_ok}/{len(rows)}\n")
        fh.write(f"- pdf_url：{pdf_ok}/{len(rows)}\n")
        fh.write(f"- announcement_type：{type_ok}/{len(rows)}\n\n")

        fh.write("## 失败原因汇总\n")
        for reason, cnt in failure_counter.most_common():
            fh.write(f"- {reason}: {cnt}\n")
        if not failure_counter:
            fh.write("- 无失败记录\n")
        fh.write("\n")

        fh.write("## recommended_status（小样本）\n")
        if success_companies > 0 or partial_companies > 0:
            fh.write("- 建议：testing / partial（小样本层面可继续验证），不代表长期稳定可用。\n")
        else:
            fh.write("- 建议：candidate（需补充 orgid/接口可用性后再测）。\n")
        fh.write("\n")

        fh.write("## 合规与边界确认\n")
        fh.write("- 未绕过登录/验证码/付费/权限。\n")
        fh.write("- 未下载 PDF 正文，未计算 hash。\n")
        fh.write("- 未做 PostgreSQL / MongoDB / MinIO 接入。\n")
        fh.write("- 请求间插入 sleep，未进行高频访问。\n")
        fh.write(f"- 使用 mapped BSE code 成功的公司数：{mapped_success_companies}\n")
        fh.write("- 430xxx -> 920xxx 映射仅用于小样本验证，可能未覆盖所有北交所代码；如仍失败需人工复核映射或公司状态。\n")


def main() -> None:
    ensure_dirs()
    samples = load_samples()
    rows: List[Dict] = []
    failure_counter: Counter = Counter()

    for sample in samples:
        company_rows = process_company(sample)
        # Aggregate company-level status
        has_success = any(r["validation_status"] == "success" for r in company_rows)
        has_partial = any(r["validation_status"] == "partial" for r in company_rows)
        if has_success:
            status = "success"
        elif has_partial:
            status = "partial"
        else:
            status = "failed"
        if status != "success":
            for r in company_rows:
                if r["failure_reason"]:
                    failure_counter[r["failure_reason"]] += 1

        rows.extend(company_rows)
        time.sleep(0.5)  # gentle pacing

    # company-level counts
    stats = {
        "companies": len(samples),
        "success_companies": len({r["company_code"] for r in rows if r["validation_status"] == "success"}),
        "partial_companies": len({r["company_code"] for r in rows if r["validation_status"] == "partial"}),
        "failed_companies": len({r["company_code"] for r in rows if r["validation_status"] == "failed"}),
    }

    write_csv(rows)
    write_summary(rows, stats, failure_counter)
    print(f"Wrote rows: {len(rows)} -> {OUT_CSV}")
    print(f"Summary -> {SUMMARY_MD}")


if __name__ == "__main__":
    main()
