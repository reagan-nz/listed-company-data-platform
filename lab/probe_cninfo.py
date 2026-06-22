"""Plan A: CNINFO verification probe (read-only).

Tests the HYPOTHESIS that CNINFO (巨潮资讯) exposes a stable structured
announcement query that can anchor Phase 1, using the checklist:
  - code -> internal orgId resolution
  - hisAnnouncement/query params (stock, category, seDate, pagination)
  - required headers
  - rate-limit behavior
  - PDF link retrieval + reliable download
  - robots.txt / terms (commercial-use uncertainty)

COMPANY-AGNOSTIC: every company-specific value (stock code, dates, category,
exchange column) is a CLI argument. Nothing about any specific company is
hard-coded. The endpoint paths and CNINFO announcement category codes are
SOURCE config (not company config) and are declared as constants below.

This script only READS public endpoints politely; it never bypasses any
protection. It writes a findings report and a PASS/FAIL verdict.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

# Make the project root importable whether run as `python lab/probe_cninfo.py`
# or `python -m lab.probe_cninfo` from the project directory.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import requests  # noqa: E402

# --- SOURCE config (not company-specific) ----------------------------------
TOPSEARCH_URL = "http://www.cninfo.com.cn/new/information/topSearch/query"
HISANN_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
STATIC_HOST = "http://static.cninfo.com.cn/"
ROBOTS_URL = "http://www.cninfo.com.cn/robots.txt"

# CNINFO announcement category codes (source-level, not company-level).
CATEGORY_CODES = {
    "annual_report": "category_ndbg_szsh",
    "semiannual_report": "category_bndbg_szsh",
    "q1_report": "category_yjdbg_szsh",
    "q3_report": "category_sjdbg_szsh",
}

# Exchange -> CNINFO `column` value (source-level mapping).
EXCHANGE_COLUMN = {
    "SZSE": "szse",
    "SSE": "sse",
    "BSE": "bj",
}

BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
        "ListedCompanyDataCollector/cninfo-probe"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
AJAX_HEADERS = {
    **BASE_HEADERS,
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "http://www.cninfo.com.cn/",
}


@dataclass
class ProbeResult:
    checklist: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    egress_ip: str = ""
    verdict: str = "UNKNOWN"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _session(timeout: float) -> requests.Session:
    s = requests.Session()
    s.headers.update(BASE_HEADERS)
    s.request = _wrap_timeout(s.request, timeout)  # type: ignore
    return s


def _wrap_timeout(fn, timeout):
    def inner(method, url, **kw):
        kw.setdefault("timeout", timeout)
        return fn(method, url, **kw)
    return inner


def detect_egress_ip(sess: requests.Session) -> str:
    for url in ("https://api.ipify.org?format=json", "https://ifconfig.me/all.json"):
        try:
            r = sess.get(url, timeout=8)
            if r.ok:
                data = r.json()
                return data.get("ip") or data.get("ip_addr") or json.dumps(data)[:60]
        except Exception:
            continue
    return "unknown"


# -- A1: resolve orgId -------------------------------------------------------
def resolve_org_id(sess: requests.Session, stock_code: str) -> tuple[str, dict]:
    """Return (orgId, raw_match) for a stock code via topSearch, or ("", {})."""
    try:
        r = sess.post(TOPSEARCH_URL, data={"keyWord": stock_code, "maxNum": 10}, headers=AJAX_HEADERS)
    except Exception as exc:
        return "", {"error": f"{type(exc).__name__}: {exc}"}
    if not r.ok:
        return "", {"http_status": r.status_code}
    try:
        items = r.json()
    except Exception:
        return "", {"error": "non_json_response", "text_head": r.text[:200]}
    if isinstance(items, list):
        for it in items:
            if str(it.get("code")) == str(stock_code):
                return it.get("orgId", ""), it
        if items:
            return items[0].get("orgId", ""), items[0]
    return "", {"raw": str(items)[:200]}


# -- A2/A3: announcement query ----------------------------------------------
def query_announcements(
    sess: requests.Session,
    stock_code: str,
    org_id: str,
    column: str,
    category: str,
    se_date: str,
    page_num: int = 1,
    page_size: int = 30,
    use_ajax_headers: bool = True,
) -> tuple[int, dict]:
    payload = {
        "stock": f"{stock_code},{org_id}" if org_id else stock_code,
        "tabName": "fulltext",
        "pageSize": page_size,
        "pageNum": page_num,
        "column": column,
        "category": category,
        "plate": "",
        "seDate": se_date,
        "searchkey": "",
        "secid": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    headers = AJAX_HEADERS if use_ajax_headers else BASE_HEADERS
    try:
        r = sess.post(HISANN_URL, data=payload, headers=headers)
    except Exception as exc:
        return -1, {"error": f"{type(exc).__name__}: {exc}"}
    try:
        return r.status_code, (r.json() if r.ok else {"text_head": r.text[:200]})
    except Exception:
        return r.status_code, {"error": "non_json_response", "text_head": r.text[:200]}


# Title tokens that mark a NON-full-report announcement (summary, cancellation,
# correction, English version, etc.). Source-level, not company-specific.
_NOT_FULL_REPORT = ("摘要", "取消", "更正", "英文", "补充", "英文版",
                    "内部控制", "审计报告", "专项", "问询", "已取消")

# Title tokens that mark a DUAL-LISTING / overseas variant of the annual report.
# For A+H (and B-share) issuers, CNINFO lists both the A-share full report and an
# "H股公告-..." (HKEX-format) version. The H-share report has a different
# structure (no 第三节 MD&A with the 主营业务分行业 tables, etc.), so the
# industrial extractor scores near-zero on it (中国银行 601988: 1/11). These are
# still valid full reports, so we DEPRIORITIZE rather than exclude them: an
# A-share full report is preferred when present, with the H-share kept as a
# fallback so single-listing edge cases never lose their only report.
# Source-level, not company-specific.
_DUAL_LISTING = ("H股", "H 股", "境外", "GDR")


def pick_full_report(announcements: list[dict]) -> dict | None:
    """Select the FULL A-share annual report, not the summary or an H-share variant.

    `announcements[0]` is NOT reliable (ordering varies; the 摘要 can come first).
    Selection is tiered, most-preferred first:
      1. a full report that is NOT a dual-listing/overseas (H股...) variant,
      2. any full report (covers issuers whose only report is tagged H股),
      3. the first announcement (last-resort, preserves prior behavior).
    """
    def is_full(title: str) -> bool:
        title = title or ""
        return "年度报告" in title and not any(tok in title for tok in _NOT_FULL_REPORT)

    def is_dual_listing(title: str) -> bool:
        return any(tok in (title or "") for tok in _DUAL_LISTING)

    full = [a for a in announcements if is_full(a.get("announcementTitle", ""))]
    for a in full:
        if not is_dual_listing(a.get("announcementTitle", "")):
            return a
    if full:
        return full[0]
    return announcements[0] if announcements else None


def main() -> int:
    ap = argparse.ArgumentParser(description="CNINFO verification probe (company-agnostic; values via CLI)")
    ap.add_argument("--stock-code", required=True, help="e.g. 300750 (provided by caller, never hard-coded)")
    ap.add_argument("--exchange", default="SZSE", choices=sorted(EXCHANGE_COLUMN.keys()))
    ap.add_argument("--category", default="annual_report", choices=sorted(CATEGORY_CODES.keys()))
    ap.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--rate-probe-count", type=int, default=5, help="number of spaced requests for rate-limit check")
    ap.add_argument("--rate-probe-gap", type=float, default=0.6, help="seconds between rate-probe requests")
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--download-pdf", action="store_true", help="download the first matching PDF and verify it opens")
    ap.add_argument("--pdf-out", default=os.path.join(_PROJECT_ROOT, "outputs", "extraction"))
    ap.add_argument("--report-out", default=os.path.join(_PROJECT_ROOT, "outputs", "cninfo_probe_report.md"))
    args = ap.parse_args()

    column = EXCHANGE_COLUMN[args.exchange]
    category = CATEGORY_CODES[args.category]
    se_date = f"{args.start_date}~{args.end_date}"

    sess = _session(args.timeout)
    res = ProbeResult()
    res.egress_ip = detect_egress_ip(sess)
    print(f"[probe] egress IP: {res.egress_ip}")

    # A1
    print("[probe] A1 resolve orgId ...")
    org_id, match = resolve_org_id(sess, args.stock_code)
    res.checklist["A1_orgId_resolution"] = {
        "ok": bool(org_id),
        "org_id": org_id,
        "matched": {k: match.get(k) for k in ("code", "zwjc", "orgId", "category")} if isinstance(match, dict) else match,
    }
    time.sleep(args.rate_probe_gap)

    # A2 query
    print("[probe] A2 hisAnnouncement query ...")
    status, body = query_announcements(sess, args.stock_code, org_id, column, category, se_date)
    anns = body.get("announcements") if isinstance(body, dict) else None
    anns = anns or []
    res.checklist["A2_query"] = {
        "http_status": status,
        "ok": status == 200 and isinstance(body, dict),
        "returned_count": len(anns),
        "total_announcement": body.get("totalannouncement") if isinstance(body, dict) else None,
        "sample_titles": [a.get("announcementTitle", "") for a in anns[:3]],
        "supports_params": {"stock": True, "category": bool(category), "seDate": True, "pagination": True},
    }

    # A3 headers requirement: retry WITHOUT ajax headers to see if still works
    print("[probe] A3 header sensitivity ...")
    time.sleep(args.rate_probe_gap)
    status_plain, body_plain = query_announcements(
        sess, args.stock_code, org_id, column, category, se_date, use_ajax_headers=False
    )
    res.checklist["A3_headers"] = {
        "works_with_ajax_headers": res.checklist["A2_query"]["ok"],
        "works_without_ajax_headers": status_plain == 200 and isinstance(body_plain, dict)
        and bool(body_plain.get("announcements") is not None),
        "note": "if only ajax-headers works, Content-Type/X-Requested-With/Referer are required",
    }

    # A4 rate-limit behavior
    print(f"[probe] A4 rate-limit ({args.rate_probe_count} spaced requests) ...")
    timings = []
    statuses = []
    for i in range(args.rate_probe_count):
        t0 = time.monotonic()
        st, _ = query_announcements(sess, args.stock_code, org_id, column, category, se_date, page_num=1)
        timings.append(round((time.monotonic() - t0) * 1000))
        statuses.append(st)
        time.sleep(args.rate_probe_gap)
    res.checklist["A4_rate_limit"] = {
        "request_count": args.rate_probe_count,
        "gap_seconds": args.rate_probe_gap,
        "statuses": statuses,
        "latencies_ms": timings,
        "throttled": any(s in (403, 429, 456, 509) for s in statuses),
    }

    # A5 PDF retrieval + download
    print("[probe] A5 PDF link retrieval ...")
    pdf_info: dict = {"ok": False}
    first = pick_full_report(anns)
    if first:
        adjunct = first.get("adjunctUrl", "")
        pdf_url = STATIC_HOST + adjunct if adjunct else ""
        pdf_info = {
            "announcement_title": first.get("announcementTitle", ""),
            "announcement_time": first.get("announcementTime"),
            "adjunct_url": adjunct,
            "pdf_url": pdf_url,
            "ok": bool(pdf_url),
        }
        if args.download_pdf and pdf_url:
            try:
                pr = sess.get(pdf_url, timeout=args.timeout)
                content = pr.content if pr.ok else b""
                pdf_info["download_status"] = pr.status_code
                pdf_info["bytes"] = len(content)
                pages = 0
                if content[:4] == b"%PDF":
                    try:
                        import fitz  # type: ignore
                        with fitz.open(stream=content, filetype="pdf") as doc:
                            pages = doc.page_count
                    except Exception as exc:
                        pdf_info["open_error"] = f"{type(exc).__name__}: {exc}"
                pdf_info["pdf_pages"] = pages
                pdf_info["opens"] = pages > 0
                if pages > 0:
                    os.makedirs(args.pdf_out, exist_ok=True)
                    safe = f"{args.stock_code}_{args.category}_{(first.get('announcementTime') or 'na')}".replace("/", "-")
                    saved = os.path.join(args.pdf_out, f"{safe}.pdf")
                    with open(saved, "wb") as fh:
                        fh.write(content)
                    pdf_info["saved_path"] = saved
            except Exception as exc:
                pdf_info["download_error"] = f"{type(exc).__name__}: {exc}"
    res.checklist["A5_pdf"] = pdf_info

    # A6 robots/terms
    print("[probe] A6 robots.txt ...")
    robots_info: dict = {}
    try:
        rr = sess.get(ROBOTS_URL, timeout=args.timeout)
        robots_info = {"http_status": rr.status_code, "body_head": (rr.text or "")[:500] if rr.ok else ""}
    except Exception as exc:
        robots_info = {"error": f"{type(exc).__name__}: {exc}"}
    robots_info["commercial_use"] = "UNVERIFIED - requires legal review of CNINFO terms of use"
    res.checklist["A6_robots_terms"] = robots_info

    # Verdict
    a1 = res.checklist["A1_orgId_resolution"]["ok"]
    a2 = res.checklist["A2_query"]["ok"]
    a5 = res.checklist["A5_pdf"].get("ok") and (res.checklist["A5_pdf"].get("opens", not args.download_pdf))
    throttled = res.checklist["A4_rate_limit"]["throttled"]
    if a1 and a2 and a5 and not throttled:
        res.verdict = "PASS (L2 confirmed now; L3 needs scheduled re-run)"
    elif a1 and a2:
        res.verdict = "PARTIAL (query works; verify PDF/rate-limit)"
    else:
        res.verdict = "FAIL (fall back to HTML/Playwright; demote to L1 candidate)"

    write_report(args, res, column, category, se_date)
    print(f"[probe] verdict: {res.verdict}")
    print(f"[probe] report -> {args.report_out}")
    return 0


def write_report(args, res: ProbeResult, column: str, category: str, se_date: str) -> None:
    os.makedirs(os.path.dirname(args.report_out), exist_ok=True)
    c = res.checklist
    lines: list[str] = []
    a = lines.append
    a("# CNINFO Verification Probe Report")
    a("")
    a(f"_Generated: {_now()}_")
    a("")
    a("Plan A: validate whether CNINFO can be the Phase-1 structured anchor. "
      "All company-specific inputs were passed via CLI (not hard-coded).")
    a("")
    a("## Run parameters")
    a("")
    a(f"- stock_code: `{args.stock_code}` (CLI)")
    a(f"- exchange: `{args.exchange}` -> column=`{column}` (CLI)")
    a(f"- category: `{args.category}` -> code=`{category}` (CLI)")
    a(f"- date range: `{se_date}` (CLI)")
    a(f"- egress IP: `{res.egress_ip}` (affects geo-gated behavior)")
    a(f"- PDF download attempted: `{bool(args.download_pdf)}`")
    a("")
    a(f"## VERDICT: {res.verdict}")
    a("")
    a("## Checklist results")
    a("")
    a("### A1. code -> orgId resolution")
    a("```json")
    a(json.dumps(c.get("A1_orgId_resolution", {}), ensure_ascii=False, indent=2))
    a("```")
    a("### A2. hisAnnouncement/query (stock + category + seDate + pagination)")
    a("```json")
    a(json.dumps(c.get("A2_query", {}), ensure_ascii=False, indent=2))
    a("```")
    a("### A3. header sensitivity")
    a("```json")
    a(json.dumps(c.get("A3_headers", {}), ensure_ascii=False, indent=2))
    a("```")
    a("### A4. rate-limit behavior")
    a("```json")
    a(json.dumps(c.get("A4_rate_limit", {}), ensure_ascii=False, indent=2))
    a("```")
    a("### A5. PDF link retrieval + download")
    a("```json")
    a(json.dumps(c.get("A5_pdf", {}), ensure_ascii=False, indent=2))
    a("```")
    a("### A6. robots.txt / terms")
    a("```json")
    a(json.dumps(c.get("A6_robots_terms", {}), ensure_ascii=False, indent=2))
    a("```")
    a("")
    a("## Honest limits")
    a("")
    a("- L3 (stable over time) is NOT proven by one session. This run only shows "
      "the endpoint worked across a few spaced requests now; a scheduled re-run is required.")
    a("- Commercial-use permission is UNVERIFIED and needs legal review of CNINFO terms.")
    a("- Behavior may differ by egress IP (VPN/overseas vs mainland).")
    with open(args.report_out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
