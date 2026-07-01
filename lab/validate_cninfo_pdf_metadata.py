"""
CNINFO announcement PDF metadata small-sample validation (Issue #83).

Inputs:
- outputs/validation/cninfo_latest_announcement_validation.csv (from Issue #82)

Outputs:
- outputs/validation/cninfo_pdf_metadata_validation.csv
- outputs/validation/cninfo_pdf_metadata_validation_summary.md

Scope:
- Small-sample HTTP checks of pdf_url already discovered in Issue #82.
- No login bypass, no captcha bypass, no high-frequency requests.
- Does NOT parse PDF text, does NOT OCR, does NOT upload to MinIO, does NOT touch databases.
"""

from __future__ import annotations

import csv
import hashlib
import os
import statistics
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_latest_announcement_validation.csv")
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_pdf_metadata_validation.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_pdf_metadata_validation_summary.md")

TARGET_MAX = 100
SLEEP_SECONDS = 0.5

CSV_FIELDS = [
    "company_code",
    "company_name",
    "cninfo_query_code",
    "announcement_title",
    "announcement_type",
    "publish_time",
    "source_url",
    "pdf_url",
    "download_status",
    "http_status_code",
    "content_hash",
    "file_size",
    "mime_type",
    "download_time",
    "has_text_layer",
    "validation_status",
    "failure_reason",
    "access_method",
    "notes",
]

FAILURE_REASONS = {
    "success",
    "missing_pdf_url",
    "invalid_pdf_url",
    "pdf_404",
    "pdf_403",
    "pdf_500",
    "not_pdf_content",
    "download_timeout",
    "file_too_large",
    "hash_failed",
    "mime_type_missing",
    "source_url_missing",
    "source_pdf_mismatch",
    "scan_pdf_no_text_layer",
    "rate_limited",
    "captcha_or_login_required",
    "network_timeout",
    "http_error",
    "unknown_error",
}


def ensure_dirs() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_candidates() -> List[Dict]:
    rows = []
    with open(INPUT_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            if r.get("validation_status") != "success":
                continue
            if not r.get("pdf_url"):
                continue
            rows.append(r)
    return rows[:TARGET_MAX]


def is_pdf_content(resp: requests.Response) -> bool:
    ctype = resp.headers.get("Content-Type", "").lower()
    if "pdf" in ctype:
        return True
    # fallback: check first bytes
    head = resp.content[:5]
    return head.startswith(b"%PDF")


def compute_hash(data: bytes) -> str | None:
    try:
        h = hashlib.sha256()
        h.update(data)
        return h.hexdigest()
    except Exception:
        return None


def fetch_pdf(url: str) -> Tuple[bytes | None, int | None, str | None, str | None, int | None]:
    try:
        resp = requests.get(url, timeout=15)
        status = resp.status_code
        mime = resp.headers.get("Content-Type", "")
        size = len(resp.content) if resp.content is not None else 0
        if status == 403:
            return None, status, mime, "pdf_403", size
        if status == 404:
            return None, status, mime, "pdf_404", size
        if status >= 500:
            return None, status, mime, "pdf_500", size
        if status != 200:
            return None, status, mime, "http_error", size
        if not is_pdf_content(resp):
            return None, status, mime, "not_pdf_content", size
        return resp.content, status, mime, None, size
    except requests.exceptions.Timeout:
        return None, None, None, "download_timeout", None
    except Exception:
        return None, None, None, "unknown_error", None


def process_record(rec: Dict) -> Dict:
    pdf_url = rec.get("pdf_url", "").strip()
    company_code = rec.get("company_code", "")
    company_name = rec.get("company_name", "")
    cninfo_query_code = rec.get("cninfo_query_code", "") or rec.get("company_code", "")
    access_method = "HTTP"

    if not pdf_url:
        return {
            "company_code": company_code,
            "company_name": company_name,
            "cninfo_query_code": cninfo_query_code,
            "announcement_title": rec.get("announcement_title", ""),
            "announcement_type": rec.get("announcement_type", ""),
            "publish_time": rec.get("publish_time", ""),
            "source_url": rec.get("source_url", ""),
            "pdf_url": pdf_url,
            "download_status": "failed",
            "http_status_code": "",
            "content_hash": "",
            "file_size": "",
            "mime_type": "",
            "download_time": now_iso(),
            "has_text_layer": "unknown",
            "validation_status": "failed",
            "failure_reason": "missing_pdf_url",
            "access_method": access_method,
            "notes": "pdf_url missing",
        }

    data, status, mime, failure, size = fetch_pdf(pdf_url)
    download_time = now_iso()
    if failure:
        return {
            "company_code": company_code,
            "company_name": company_name,
            "cninfo_query_code": cninfo_query_code,
            "announcement_title": rec.get("announcement_title", ""),
            "announcement_type": rec.get("announcement_type", ""),
            "publish_time": rec.get("publish_time", ""),
            "source_url": rec.get("source_url", ""),
            "pdf_url": pdf_url,
            "download_status": "failed",
            "http_status_code": status or "",
            "content_hash": "",
            "file_size": size if size is not None else "",
            "mime_type": mime or "",
            "download_time": download_time,
            "has_text_layer": "unknown",
            "validation_status": "failed",
            "failure_reason": failure if failure in FAILURE_REASONS else "unknown_error",
            "access_method": access_method,
            "notes": "download failed",
        }

    content_hash = compute_hash(data)
    if not content_hash:
        failure_reason = "hash_failed"
        status_label = "failed"
    else:
        failure_reason = "success"
        status_label = "success"

    return {
        "company_code": company_code,
        "company_name": company_name,
        "cninfo_query_code": cninfo_query_code,
        "announcement_title": rec.get("announcement_title", ""),
        "announcement_type": rec.get("announcement_type", ""),
        "publish_time": rec.get("publish_time", ""),
        "source_url": rec.get("source_url", ""),
        "pdf_url": pdf_url,
        "download_status": "success" if status == 200 else "partial",
        "http_status_code": status or "",
        "content_hash": content_hash or "",
        "file_size": size if size is not None else "",
        "mime_type": mime or "",
        "download_time": download_time,
        "has_text_layer": "unknown",
        "validation_status": status_label,
        "failure_reason": failure_reason,
        "access_method": access_method,
        "notes": "",
    }


def write_csv(rows: List[Dict]) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_summary(rows: List[Dict], failure_counter: Counter, candidates_count: int) -> None:
    total = candidates_count
    success = sum(1 for r in rows if r["validation_status"] == "success")
    partial = sum(1 for r in rows if r["validation_status"] == "partial")
    failed = sum(1 for r in rows if r["validation_status"] == "failed")

    file_sizes_int: List[int] = []
    for r in rows:
        if r.get("download_status") != "success":
            continue
        s = r.get("file_size")
        try:
            val = int(s)
            if val > 0:
                file_sizes_int.append(val)
        except Exception:
            continue

    def fmt_stat(vals: List[int]) -> str:
        if not vals:
            return "N/A"
        return f"min={min(vals)}, max={max(vals)}, avg={int(statistics.mean(vals))}"

    http_ok = sum(1 for r in rows if r["http_status_code"] in (200, "200"))
    hash_ok = sum(1 for r in rows if r["content_hash"])
    mime_ok = sum(1 for r in rows if r["mime_type"])

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO 公告 PDF 元数据小样本验证（Issue #83）\n\n")
        fh.write("## 数据来源\n")
        fh.write(f"- 输入：{os.path.relpath(INPUT_CSV, BASE_DIR)}（Issue #82 成功公告记录）\n")
        fh.write("- PDF URL 来源：Issue #82 最新公告验证结果中的 pdf_url\n\n")

        fh.write("## 样本概况\n")
        fh.write(f"- 候选 PDF 记录数：{total}\n")
        fh.write(f"- 实际验证 PDF 数：{len(rows)}\n")
        fh.write(f"- success：{success}\n")
        fh.write(f"- partial：{partial}\n")
        fh.write(f"- failed：{failed}\n\n")

        fh.write("## 字段可得性（按行计数）\n")
        fh.write(f"- pdf_url：{len(rows)}/{total}\n")
        fh.write(f"- http_status_code=200：{http_ok}/{len(rows)}\n")
        fh.write(f"- content_hash：{hash_ok}/{len(rows)}\n")
        fh.write(f"- file_size：{len(file_sizes_int)}/{len(rows)}\n")
        fh.write(f"- mime_type：{mime_ok}/{len(rows)}\n")
        fh.write(f"- download_time：{len(rows)}/{len(rows)}\n")
        fh.write(f"- has_text_layer：填充为 unknown（本次未解析正文）\n\n")

        fh.write("## 失败原因汇总\n")
        for reason, cnt in failure_counter.most_common():
            fh.write(f"- {reason}: {cnt}\n")
        if not failure_counter:
            fh.write("- 无失败记录\n")
        fh.write("\n")

        fh.write("## 文件大小概况\n")
        fh.write(f"- 统计口径：仅基于 download_status=success 且 file_size>0 的记录\n")
        fh.write(f"- {fmt_stat(file_sizes_int)}\n\n")

        fh.write("## hash 规则\n")
        fh.write("- content_hash 使用 sha256；计算对象是 PDF 原始二进制内容，不基于 URL/标题/文本。\n")
        fh.write("- 本次仅做元数据验证，不做 MinIO object_key 设计。\n\n")

        fh.write("## recommended_status（小样本）\n")
        if success > 0:
            fh.write("- 建议：testing / partial（小样本可继续验证），不代表长期稳定可用。\n")
        else:
            fh.write("- 建议：candidate（需改善可达性/映射后再测）。\n")
        fh.write("\n")

        fh.write("## 合规与边界确认\n")
        fh.write("- 未绕过登录/验证码/付费/权限。\n")
        fh.write("- 未解析 PDF 正文，未做 OCR，未做字段抽取。\n")
        fh.write("- 未上传 MinIO，未做 PostgreSQL / MongoDB 接入。\n")
        fh.write("- 请求间加入 sleep，避免高频访问。\n")
        fh.write("- 结果受网络/VPN/映射影响，需人工环境确认后视情况重跑。\n")


def main() -> None:
    ensure_dirs()
    candidates = load_candidates()
    failure_counter: Counter = Counter()
    rows: List[Dict] = []

    for rec in candidates:
        row = process_record(rec)
        if row["failure_reason"]:
            failure_counter[row["failure_reason"]] += 1
        rows.append(row)
        time.sleep(SLEEP_SECONDS)

    write_csv(rows)
    write_summary(rows, failure_counter, len(candidates))
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
