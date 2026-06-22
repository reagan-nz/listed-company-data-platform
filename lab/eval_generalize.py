"""Held-out generalization evaluation harness (drives the FROZEN pipeline).

This script does NOT modify the extraction pipeline. It:
  1. reads a stratified company list (config),
  2. for each company: resolves orgId, picks the FULL annual report (frozen
     probe selector), downloads it, runs the frozen extractor,
  3. computes an AUTOMATIC proxy "plausible" score per field,
  4. flags scanned/no-text-layer PDFs and probe failures,
  5. aggregates per-field, per-company, and financial-vs-non-financial,
  6. writes eval_summary.md + eval_results.json.

Manual spot-check of a random subset is done separately to calibrate the proxy.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import requests  # noqa: E402

from lab.field_schema import FIELD_SPECS, detect_profile  # noqa: E402
from lab.probe_cninfo import (CATEGORY_CODES, EXCHANGE_COLUMN, STATIC_HOST,  # noqa: E402
                              _session, pick_full_report, query_announcements,
                              resolve_org_id)
from lab.extract_annual_report import (compute_regions, extract_field,  # noqa: E402
                                       parse_pages, revenue_table_plausible,
                                       rnd_investment_plausible)


def _retry(fn, tries=3, gap=1.5):
    last = None
    for _ in range(tries):
        try:
            r = fn()
            if r:
                return r
        except Exception as exc:  # noqa: BLE001
            last = exc
        time.sleep(gap)
    if last:
        raise last
    return None


def field_plausible(f: dict) -> bool:
    """Automatic proxy for 'looks correctly extracted'."""
    if f.get("status") != "found":
        return False
    ex = f.get("extraction")
    v = f.get("value")
    if ex == "section_snippet":
        return isinstance(v, str) and len(v) >= 25
    if ex == "numeric":
        if f.get("field") == "rnd_investment":
            return rnd_investment_plausible(v)
        return isinstance(v, dict) and any(
            any(c.isdigit() for c in (x.get("value") or "")) for x in v.get("labeled", [])
        )
    if ex == "concentration":
        return isinstance(v, dict) and bool(v.get("ratio") or v.get("amount"))
    if ex == "table":
        if f.get("field") in ("revenue_by_region", "revenue_by_segment"):
            return revenue_table_plausible(v)
        return isinstance(v, dict) and bool(v.get("rows")) and v.get("match_hits", 0) >= 1
    return False


def evaluate_company(c: dict, sess, out_dir: str) -> dict:
    code = str(c["stock_code"]).strip()
    ex = c.get("exchange", "SSE")
    short = c.get("short_name", "")
    res = {"stock_code": code, "short_name": short, "exchange": ex,
           "industry": c.get("industry", ""), "financial": bool(c.get("financial", False)),
           "status": "ok", "error": ""}
    cdir = os.path.join(out_dir, code)
    os.makedirs(cdir, exist_ok=True)
    pdf_path = os.path.join(cdir, f"{code}.pdf")
    meta_path = os.path.join(cdir, "meta.json")
    try:
        # Resumable / offline-on-rerun: if the PDF + announcement meta are cached,
        # skip all network (this removes transient VPN orgId/query failures on re-runs).
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) >= 10000 and os.path.exists(meta_path):
            meta_j = json.load(open(meta_path, encoding="utf-8"))
            url = meta_j.get("source_url", "")
            res["picked_title"] = meta_j.get("picked_title", "")
        else:
            org = str(c.get("orgid") or "").strip()  # orgId from the universe list avoids resolve
            if not org:
                resolved = _retry(lambda: resolve_org_id(sess, code))
                org = (resolved[0] if resolved else "") or ""
            if not org:
                res["status"] = "no_orgid"; return res
            column = EXCHANGE_COLUMN.get(ex, "sse")
            # `_retry` returns None when every attempt yields no announcements
            # (e.g. delisted/ST firms with no 2024-2025 annual report). Guard the
            # unpack so this is recorded as a clean finding, never a crash.
            qr = _retry(lambda: (lambda r: r if (isinstance(r[1], dict) and (r[1].get("announcements"))) else None)(
                query_announcements(sess, code, org, column, CATEGORY_CODES["annual_report"],
                                    "2024-01-01~2025-12-31", page_size=50)))
            if not qr:
                res["status"] = "no_announcement"; return res
            st, body = qr
            anns = (body.get("announcements") if isinstance(body, dict) else None) or []
            if not anns:
                res["status"] = "no_announcement"; return res
            pick = pick_full_report(anns)
            res["picked_title"] = pick.get("announcementTitle", "")
            url = STATIC_HOST + pick.get("adjunctUrl", "")
            if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 10000:
                r = sess.get(url, timeout=90)
                open(pdf_path, "wb").write(r.content)
            json.dump({"source_url": url, "picked_title": res["picked_title"], "orgid": org},
                      open(meta_path, "w", encoding="utf-8"), ensure_ascii=False)
        res["source_url"] = url
        res["pdf_bytes"] = os.path.getsize(pdf_path)

        pages, meta = parse_pages(pdf_path, os.path.join(out_dir, ".cache"))
        text_len = sum(len(p) for p in pages)
        res["page_count"] = meta["page_count"]
        res["text_len"] = text_len
        if meta["page_count"] >= 15 and text_len < 3000:
            res["status"] = "no_text_layer"  # likely scanned -> would need OCR
            return res

        # Auto financial-profile is OFF (it regressed); eval uses the shipped
        # industrial profile. `suggested` is recorded for visibility only.
        res["suggested_profile"] = detect_profile(pages)
        specs = FIELD_SPECS
        regions = compute_regions(pages)
        res["regions"] = {k: [min(v), max(v)] for k, v in regions.items() if v}
        fields = [extract_field(spec, pages, pdf_path, url, regions) for spec in specs]
        res["fields"] = {f["field"]: {"status": f["status"], "in_region": f.get("in_region"),
                                      "page": f.get("page"), "plausible": field_plausible(f)}
                         for f in fields}
        res["found"] = sum(1 for f in fields if f["status"] == "found")
        res["partial"] = sum(1 for f in fields if f["status"] == "partial")
        res["not_found"] = sum(1 for f in fields if f["status"] == "not_found")
        res["plausible"] = sum(1 for f in fields if field_plausible(f))
        # keep the brief for manual spot-check
        from lab.extract_annual_report import render_brief
        profile = {"company": {"short_name": short, "stock_code": code, "exchange": ex},
                   "source": {"report_title": res.get("picked_title", ""), "source_url": url,
                              "pdf_sha256": meta["sha256"], "page_count": meta["page_count"]},
                   "field_counts": {"found": res["found"], "partial": res["partial"],
                                    "not_found": res["not_found"], "total": len(fields)},
                   "fields": fields}
        with open(os.path.join(cdir, "company_profile.json"), "w", encoding="utf-8") as fh:
            json.dump(profile, fh, ensure_ascii=False, indent=2)
        with open(os.path.join(cdir, "company_brief.md"), "w", encoding="utf-8") as fh:
            fh.write(render_brief(profile))
    except Exception as exc:  # noqa: BLE001
        res["status"] = "error"
        res["error"] = f"{type(exc).__name__}: {exc}"
        res["trace"] = traceback.format_exc()[-400:]
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description="Held-out generalization eval harness (frozen pipeline)")
    ap.add_argument("--companies", default=os.path.join(_PROJECT_ROOT, "lab", "eval_companies.yaml"))
    ap.add_argument("--out", default=os.path.join(_PROJECT_ROOT, "outputs", "generalization", "eval"))
    ap.add_argument("--throttle", type=float, default=1.0)
    args = ap.parse_args()

    companies = (yaml.safe_load(open(args.companies, encoding="utf-8")) or {}).get("companies", [])
    os.makedirs(args.out, exist_ok=True)
    sess = _session(90)

    results = []
    for i, c in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] {c.get('short_name')} {c.get('stock_code')} ...", flush=True)
        r = evaluate_company(c, sess, args.out)
        print(f"    -> status={r['status']} found={r.get('found')} plausible={r.get('plausible')} "
              f"pages={r.get('page_count')} title={r.get('picked_title','')[:30]}", flush=True)
        results.append(r)
        time.sleep(args.throttle)

    with open(os.path.join(args.out, "eval_results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    write_summary(results, os.path.join(args.out, "eval_summary.md"))
    print("[done] ->", os.path.join(args.out, "eval_summary.md"))
    return 0


def write_summary(results: list[dict], path: str) -> None:
    field_keys = [s.key for s in FIELD_SPECS]
    ok = [r for r in results if r["status"] == "ok"]
    nonfin = [r for r in ok if not r["financial"]]
    fin = [r for r in ok if r["financial"]]
    errs = [r for r in results if r["status"] != "ok"]

    def field_rate(rows, key):
        if not rows:
            return 0, 0
        p = sum(1 for r in rows if r["fields"].get(key, {}).get("plausible"))
        return p, len(rows)

    L = []
    a = L.append
    a("# Held-out Generalization Evaluation (frozen pipeline)")
    a("")
    a(f"_Companies: {len(results)} | evaluated OK: {len(ok)} (non-financial {len(nonfin)}, "
      f"financial {len(fin)}) | excluded/errors: {len(errs)}_")
    a("")
    a("Metric = AUTOMATIC proxy 'plausible' per field (status=found + value-shape valid; "
      "tables also require a header-token match). Calibrated by a manual spot-check (separate).")
    a("")
    if nonfin:
        tot = sum(r["plausible"] for r in nonfin)
        a(f"## Headline (non-financial, n={len(nonfin)})")
        a(f"Mean plausible fields/company: **{tot/len(nonfin):.1f} / 11** "
          f"({100*tot/(11*len(nonfin)):.0f}%).")
        a("")
    a("## Per-field plausible rate (non-financial)")
    a("")
    a("| field | rate |")
    a("|---|---|")
    for k in field_keys:
        p, n = field_rate(nonfin, k)
        a(f"| {k} | {p}/{n} ({(100*p/n if n else 0):.0f}%) |")
    a("")
    a("## Per-company (non-financial)")
    a("")
    a("| company | code | board/industry | pages | found | plausible |")
    a("|---|---|---|---|---|---|")
    for r in nonfin:
        a(f"| {r['short_name']} | {r['stock_code']} | {r['industry']} | {r.get('page_count')} | "
          f"{r.get('found')} | {r.get('plausible')}/11 |")
    a("")
    a("## Financials (reported separately - schema is industrial-shaped)")
    a("")
    a("| company | code | found | plausible | note |")
    a("|---|---|---|---|---|")
    for r in fin:
        a(f"| {r['short_name']} | {r['stock_code']} | {r.get('found')} | {r.get('plausible')}/11 | "
          f"many fields N/A for financials |")
    a("")
    if errs:
        a("## Excluded / failures (these ARE findings)")
        a("")
        a("| company | code | status | detail |")
        a("|---|---|---|---|")
        for r in errs:
            a(f"| {r['short_name']} | {r['stock_code']} | {r['status']} | {r.get('error','')[:60]} |")
        a("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


if __name__ == "__main__":
    raise SystemExit(main())
