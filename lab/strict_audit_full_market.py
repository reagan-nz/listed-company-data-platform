"""Strict adversarial audit of full_market_2024 non-financial extraction results.

Hybrid method:
  1. Automated adversarial recheck over ALL non-financial ok companies (population).
  2. PDF-backed deep verification on a stratified manual subset (~12-15 companies).
  3. Stratified sample CSV (>=50 companies, 7 targeted fields).

Read-only over outputs; does not modify extraction logic or eval_results.json.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.extract_annual_report import (  # noqa: E402
    _numeric_magnitude,
    _table_row_is_data_row,
    rnd_amount_ok,
    revenue_table_plausible,
)
from lab.field_schema import FIELD_SPECS  # noqa: E402

DEFAULT_OUT = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
DEFAULT_YAML = os.path.join(_PROJECT_ROOT, "lab", "eval_companies_full_market_2024.yaml")

INDUSTRIAL_KEYS = [s.key for s in FIELD_SPECS]
TARGET_KEYS = (
    "mda",
    "main_business_segments",
    "revenue_by_segment",
    "revenue_by_region",
    "rnd_investment",
    "top_customers",
    "top_suppliers",
)

POINTER_KW = ("详见", "参见", "请见", "见下文", "见本报告", "见上述", "见附注")
FIN_BOILER_KW = ("金融工具", "公允价值", "《企业会计准则", "法律法规", "监管要求", "套期保值")
TOP_KW = (
    "前五", "前5", "前五名", "前五大", "合计", "占年度", "占销售", "占采购",
    "年度销售占比", "年度采购占比", "销售占比", "采购占比",  # BSE table column headers
)
RND_TOTAL_KW = ("金额", "总额", "合计")
STRICT_RND_MIN = 100_000  # 10万元 per eval_method strict audit

SPEC_BY_KEY = {s.key: s for s in FIELD_SPECS}


@dataclass
class AuditRow:
    company_code: str
    company_name: str
    board: str
    field_name: str
    proxy_plausible: bool
    strict_label: str
    reason: str
    evidence_sentence: str
    page: str
    source_url: str
    audit_mode: str  # automated | manual


def _load_meta(yaml_path: str) -> dict[str, dict]:
    data = yaml.safe_load(open(yaml_path, encoding="utf-8")) or {}
    return {str(c["stock_code"]): c for c in data.get("companies", [])}


def _profile_path(out_dir: str, code: str, board: str) -> str | None:
    for rel in (f"{code}/company_profile.json", f"{board}/{code}/company_profile.json"):
        p = os.path.join(out_dir, rel)
        if os.path.isfile(p):
            return p
    return None


def _pdf_path(out_dir: str, code: str, board: str) -> str | None:
    p = os.path.join(out_dir, board, code, f"{code}.pdf")
    return p if os.path.isfile(p) else None


def _field_map(profile: dict) -> dict[str, dict]:
    return {f["field"]: f for f in profile.get("fields", [])}


def _is_pointer_only(text: str) -> bool:
    t = (text or "").strip()
    if len(t) >= 80:
        return False
    return any(p in t for p in POINTER_KW)


def strict_section_snippet(f: dict) -> tuple[str, str]:
    st = f.get("status", "not_found")
    if st == "not_found":
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        v = f.get("value") if isinstance(f.get("value"), str) else ""
        if v and len(v) >= 25:
            return "partial", "status=partial with some content"
        return "partial", "status=partial low confidence"
    v = f.get("value")
    if not isinstance(v, str):
        return "wrong", "expected string snippet"
    ev = f.get("evidence_sentence") or ""
    if _is_pointer_only(v) or (_is_pointer_only(ev) and len(v) < 80):
        return "wrong", "pointer-only reference"
    if any(b in v for b in FIN_BOILER_KW):
        return "wrong", "financial/legal boilerplate"
    in_reg = f.get("in_region")
    if len(v) >= 80 and in_reg:
        return "usable", f"substantive in-region snippet (len={len(v)})"
    if len(v) >= 80 and not in_reg:
        return "partial", f"substantive but out-of-region (len={len(v)})"
    if len(v) >= 25:
        return "partial", f"short snippet (len={len(v)})"
    return "wrong", f"too short (len={len(v)})"


def strict_numeric_rnd(f: dict) -> tuple[str, str]:
    st = f.get("status", "not_found")
    if st == "not_found":
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        return "partial", "status=partial"
    val = f.get("value")
    if not isinstance(val, dict):
        return "wrong", "missing numeric value dict"
    labeled = val.get("labeled") or []
    if not labeled:
        ctx = val.get("context") or ""
        if "研发" in ctx and any(c.isdigit() for c in ctx):
            return "partial", "context-only R&D numbers without labeled total"
        return "wrong", "empty labeled list"
    best = None
    for item in labeled:
        lab = item.get("label") or ""
        num = item.get("value") or ""
        if not rnd_amount_ok(num):
            continue
        mag = _numeric_magnitude(num) or 0
        is_total_label = any(k in lab for k in RND_TOTAL_KW) or lab.strip() == "研发投入"
        if mag >= STRICT_RND_MIN and is_total_label:
            return "usable", f"total R&D label '{lab}' amount>={STRICT_RND_MIN}"
        if mag >= 10_000 and is_total_label:
            best = ("partial", f"total label but amount<{STRICT_RND_MIN}")
        elif rnd_amount_ok(num):
            best = best or ("partial", f"non-total label '{lab}'")
    if best:
        return best
    return "wrong", "no substantive R&D total amount"


def strict_table(f: dict) -> tuple[str, str]:
    st = f.get("status", "not_found")
    if st == "not_found":
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        return "partial", "status=partial"
    val = f.get("value")
    if not isinstance(val, dict):
        return "wrong", "missing table dict"
    if not revenue_table_plausible(val):
        return "wrong", "fails revenue_table_plausible"
    rows = val.get("rows") or []
    data_rows = [r for r in rows if _table_row_is_data_row(r)]
    if len(data_rows) >= 2:
        return "usable", f"{len(data_rows)} data rows with numerics"
    if len(data_rows) == 1:
        return "partial", "single data row only"
    return "wrong", "no data rows in table preview"


def strict_concentration(f: dict) -> tuple[str, str]:
    st = f.get("status", "not_found")
    if st == "not_found":
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        return "partial", "status=partial"
    val = f.get("value")
    if not isinstance(val, dict):
        return "wrong", "missing concentration dict"
    ev = f.get("evidence_sentence") or val.get("sentence") or ""
    has_val = bool(val.get("ratio") or val.get("amount"))
    if not has_val:
        return "wrong", "empty ratio/amount"
    if any(k in ev for k in TOP_KW):
        return "usable", "top-N keyword in evidence with ratio/amount"
    if any(k in (val.get("sentence") or "") for k in TOP_KW):
        return "usable", "top-N keyword in value sentence"
    return "partial", "ratio/amount without clear top-N evidence keyword"


def strict_audit_field(f: dict) -> tuple[str, str]:
    ex = f.get("extraction") or ""
    if ex == "section_snippet":
        return strict_section_snippet(f)
    if ex == "numeric":
        if f.get("field") == "rnd_investment":
            return strict_numeric_rnd(f)
        return strict_section_snippet(f)
    if ex == "table":
        return strict_table(f)
    if ex == "concentration":
        return strict_concentration(f)
    return "wrong", f"unknown extraction type {ex}"


def _pdf_page_text(pdf_path: str, page: int) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return ""
    if page is None or page < 1:
        return ""
    try:
        doc = fitz.open(pdf_path)
        if page > len(doc):
            doc.close()
            return ""
        text = doc[page - 1].get_text()
        doc.close()
        return text
    except Exception:
        return ""


def _pdf_search_anchors(pdf_path: str, anchors: tuple[str, ...], max_pages: int = 100) -> list[tuple[int, str, str]]:
    try:
        import fitz
    except ImportError:
        return []
    hits: list[tuple[int, str, str]] = []
    try:
        doc = fitz.open(pdf_path)
        n = min(len(doc), max_pages)
        for i in range(n):
            text = doc[i].get_text()
            for a in anchors:
                if a in text:
                    pos = text.find(a)
                    snippet = text[max(0, pos - 20): pos + 120].replace("\n", " ")
                    hits.append((i + 1, a, snippet))
        doc.close()
    except Exception:
        pass
    return hits


def pdf_verify_field(f: dict, pdf_path: str | None, spec) -> tuple[str, str]:
    """PDF-backed verification for manual subset."""
    if not pdf_path or not os.path.isfile(pdf_path):
        return strict_audit_field(f)[0], "pdf missing; fallback automated"

    st = f.get("status", "not_found")
    key = f.get("field", "")

    if st == "not_found":
        anchors = spec.anchors[:6] if spec else ()
        hits = _pdf_search_anchors(pdf_path, anchors)
        if not hits:
            return "not_found_correct", "anchor not found in first 100 pages"
        # substantive context near anchor?
        for pg, anchor, snippet in hits:
            if len(snippet.strip()) >= 40 and not _is_pointer_only(snippet):
                return "not_found_missed", f"anchor '{anchor}' on p{pg} with content"
        return "not_found_correct", "anchor hits are pointer-only or too thin"

    page = f.get("page")
    page_text = _pdf_page_text(pdf_path, page) if page else ""
    ev = (f.get("evidence_sentence") or "").strip()
    auto_label, auto_reason = strict_audit_field(f)

    if page_text and ev:
        ev_short = ev[: min(30, len(ev))]
        if ev_short not in page_text and ev not in page_text:
            if auto_label == "usable":
                return "partial", "evidence not located on cited PDF page"
            return "wrong", "evidence not on cited page"

    if key in ("revenue_by_segment", "revenue_by_region"):
        val = f.get("value")
        if isinstance(val, dict) and page_text:
            rows = val.get("rows") or []
            for row in rows[:3]:
                for cell in row:
                    cell_s = str(cell).strip()
                    if cell_s and len(cell_s) >= 4 and cell_s in page_text:
                        return auto_label if auto_label != "wrong" else "partial", "table cell found on page"
        return auto_label, auto_reason

    if key == "rnd_investment":
        val = f.get("value")
        if isinstance(val, dict) and page_text:
            for item in val.get("labeled") or []:
                num = (item.get("value") or "").replace(",", "")
                if num and num in page_text.replace(",", ""):
                    lbl, rsn = strict_numeric_rnd(f)
                    return lbl, f"pdf confirms number; {rsn}"
        return auto_label, auto_reason

    if st == "found" and isinstance(f.get("value"), str):
        v = f.get("value") or ""
        if page_text and len(v) >= 25:
            chunk = v[:40].strip()
            if chunk in page_text or (ev and ev in page_text):
                return auto_label if auto_label in ("usable", "partial") else "partial", "snippet/evidence on page"
            return "wrong", "snippet not on cited page"
        return auto_label, auto_reason

    if st == "found" and f.get("extraction") == "concentration":
        val = f.get("value") or {}
        if page_text:
            for token in (val.get("ratio"), val.get("amount")):
                if token and str(token) in page_text:
                    return strict_concentration(f)
        return auto_label, auto_reason

    return auto_label, auto_reason


def audit_company(
    code: str,
    name: str,
    board: str,
    eval_row: dict,
    out_dir: str,
    *,
    audit_mode: str = "automated",
    manual: bool = False,
) -> list[AuditRow]:
    prof_path = _profile_path(out_dir, code, board)
    if not prof_path:
        return []
    profile = json.load(open(prof_path, encoding="utf-8"))
    fmap = _field_map(profile)
    pdf_path = _pdf_path(out_dir, code, board)
    proxy_fields = eval_row.get("fields") or {}
    rows: list[AuditRow] = []

    for key in INDUSTRIAL_KEYS:
        f = fmap.get(key)
        if not f:
            continue
        spec = SPEC_BY_KEY.get(key)
        proxy = bool((proxy_fields.get(key) or {}).get("plausible"))
        if manual:
            label, reason = pdf_verify_field(f, pdf_path, spec)
            mode = "manual"
        else:
            label, reason = strict_audit_field(f)
            mode = "automated"
        rows.append(AuditRow(
            company_code=code,
            company_name=name,
            board=board,
            field_name=key,
            proxy_plausible=proxy,
            strict_label=label,
            reason=reason,
            evidence_sentence=(f.get("evidence_sentence") or "")[:200],
            page=str(f.get("page") if f.get("page") is not None else ""),
            source_url=f.get("source_url") or profile.get("source", {}).get("source_url", ""),
            audit_mode=mode,
        ))
    return rows


def _strict_score(rows: list[AuditRow], *, lenient: bool = False) -> float:
    usable = {"usable", "not_found_correct"} if lenient else {"usable"}
    if lenient:
        usable.add("partial")
    n = len(rows)
    if not n:
        return 0.0
    return sum(1 for r in rows if r.strict_label in usable) / n


def select_sample_companies(
    eval_rows: list[dict],
    meta: dict[str, dict],
    *,
    n: int = 55,
    seed: int = 20260624,
) -> list[str]:
    """Stratified sample: board x proxy tier x risky-field presence."""
    nonfin = [r for r in eval_rows if r["status"] == "ok" and not r.get("financial")]
    rng = random.Random(seed)
    boards = ["bse", "star", "szse_main", "chinext", "sse_main"]
    per_board = max(10, n // len(boards))
    chosen: set[str] = set()

    def tier(r):
        p = r.get("plausible", 0)
        if p >= 11:
            return "high"
        if p >= 9:
            return "mid"
        return "low"

    def risky_state(r):
        flds = r.get("fields") or {}
        risky = ("rnd_investment", "revenue_by_region", "revenue_by_segment")
        states = []
        for k in risky:
            fi = flds.get(k) or {}
            if fi.get("plausible"):
                states.append(f"{k}_plausible")
            elif fi.get("status") == "not_found":
                states.append(f"{k}_missing")
            else:
                states.append(f"{k}_other")
        return tuple(states)

    for board in boards:
        pool = [r for r in nonfin if meta.get(r["stock_code"], {}).get("board") == board]
        if not pool:
            continue
        by_tier: dict[str, list] = defaultdict(list)
        for r in pool:
            by_tier[tier(r)].append(r)
        pick_n = per_board
        for t in ("high", "mid", "low"):
            sub = by_tier[t]
            rng.shuffle(sub)
            take = pick_n // 3 + (1 if t == "low" else 0)
            for r in sub[:take]:
                chosen.add(r["stock_code"])
        # ensure risky-field coverage
        for r in pool:
            if len(chosen) >= n:
                break
            rs = risky_state(r)
            if any("missing" in x for x in rs) and r["stock_code"] not in chosen:
                chosen.add(r["stock_code"])

    if len(chosen) < n:
        rest = [r for r in nonfin if r["stock_code"] not in chosen]
        rng.shuffle(rest)
        for r in rest:
            chosen.add(r["stock_code"])
            if len(chosen) >= n:
                break
    return sorted(chosen)[:n]


def select_manual_companies(
    eval_rows: list[dict],
    meta: dict[str, dict],
    *,
    n: int = 15,
    seed: int = 20260624,
) -> list[str]:
    rng = random.Random(seed + 1)
    boards = ["bse", "star", "szse_main", "chinext", "sse_main"]
    chosen: list[str] = []
    nonfin = [r for r in eval_rows if r["status"] == "ok" and not r.get("financial")]

    for board in boards:
        pool = [r for r in nonfin if meta.get(r["stock_code"], {}).get("board") == board]
        if not pool:
            continue
        high = [r for r in pool if r.get("plausible", 0) >= 11]
        low = [r for r in pool if r.get("plausible", 0) < 9]
        mid = [r for r in pool if 9 <= r.get("plausible", 0) < 11]
        risky_nf = []
        for r in pool:
            flds = r.get("fields") or {}
            if (flds.get("rnd_investment") or {}).get("status") == "not_found":
                risky_nf.append(r)
        for bucket in (high, mid, low, risky_nf):
            rng.shuffle(bucket)
            for r in bucket:
                if r["stock_code"] not in chosen:
                    chosen.append(r["stock_code"])
                    break
        if len([c for c in chosen if meta.get(c, {}).get("board") == board]) >= 3:
            continue

    if len(chosen) < n:
        rest = [r for r in nonfin if r["stock_code"] not in chosen]
        rng.shuffle(rest)
        for r in rest:
            chosen.append(r["stock_code"])
            if len(chosen) >= n:
                break
    return chosen[:n]


def write_csv(path: str, rows: list[AuditRow]) -> None:
    fields = [
        "company_code", "company_name", "board", "field_name", "proxy_plausible",
        "strict_label", "reason", "evidence_sentence", "page", "source_url", "audit_mode",
    ]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "company_code": r.company_code,
                "company_name": r.company_name,
                "board": r.board,
                "field_name": r.field_name,
                "proxy_plausible": r.proxy_plausible,
                "strict_label": r.strict_label,
                "reason": r.reason,
                "evidence_sentence": r.evidence_sentence,
                "page": r.page,
                "source_url": r.source_url,
                "audit_mode": r.audit_mode,
            })


def financial_qualitative(out_dir: str, eval_rows: list[dict], meta: dict[str, dict]) -> list[str]:
    """Qualitative notes on 2-3 financial companies (not in 11-field headline)."""
    fin = [r for r in eval_rows if r["status"] == "ok" and r.get("financial")]
    by_sub: dict[str, list] = defaultdict(list)
    for r in fin:
        by_sub[r.get("schema_profile") or "unknown"].append(r)
    notes: list[str] = []
    for subtype in ("bank", "broker", "insurer"):
        pool = by_sub.get(subtype, [])
        if not pool:
            continue
        r = pool[0]
        code = r["stock_code"]
        board = meta.get(code, {}).get("board", "")
        prof_path = _profile_path(out_dir, code, board)
        if not prof_path:
            continue
        profile = json.load(open(prof_path, encoding="utf-8"))
        fmap = _field_map(profile)
        found = sum(1 for f in fmap.values() if f.get("status") == "found")
        plausible = r.get("plausible", 0)
        ft = r.get("field_total") or len(fmap)
        notes.append(
            f"- **{r['short_name']} ({code})**, subtype `{subtype}`: "
            f"found={found}/{ft}, proxy_plausible={plausible}/{ft}, "
            f"schema={profile.get('schema_profile')}. "
            f"Numeric fields may contain table noise; not strict-audited for headline."
        )
        # one field example
        for k, f in list(fmap.items())[:3]:
            if f.get("status") == "found":
                ev = (f.get("evidence_sentence") or "")[:80]
                notes.append(f"  - `{k}`: status={f.get('status')}, evidence=\"{ev}...\"")
    return notes


def write_summary(
    path: str,
    *,
    population_rows: list[AuditRow],
    sample_rows: list[AuditRow],
    manual_rows: list[AuditRow],
    manual_codes: list[str],
    sample_codes: list[str],
    fin_notes: list[str],
    eval_rows: list[dict],
) -> None:
    nonfin = [r for r in eval_rows if r["status"] == "ok" and not r.get("financial")]
    n_co = len(nonfin)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def agg(rows: list[AuditRow]):
        c = Counter(r.strict_label for r in rows)
        return dict(c)

    pop_by_field: dict[str, Counter] = defaultdict(Counter)
    pop_by_board: dict[str, list[float]] = defaultdict(list)
    co_scores_strict: list[float] = []
    co_scores_lenient: list[float] = []
    co_proxy: list[float] = []

    by_co: dict[str, list[AuditRow]] = defaultdict(list)
    for r in population_rows:
        by_co[r.company_code].append(r)
        pop_by_field[r.field_name][r.strict_label] += 1

    for code, crows in by_co.items():
        co_scores_strict.append(_strict_score(crows, lenient=False) * 11)
        co_scores_lenient.append(_strict_score(crows, lenient=True) * 11)
        er = next(x for x in nonfin if x["stock_code"] == code)
        co_proxy.append(er.get("plausible", 0))
        board = crows[0].board
        pop_by_board[board].append(_strict_score(crows, lenient=False) * 11)

    strict_mean = statistics.mean(co_scores_strict) if co_scores_strict else 0
    lenient_mean = statistics.mean(co_scores_lenient) if co_scores_lenient else 0
    proxy_mean = statistics.mean(co_proxy) if co_proxy else 0

    # manual calibration
    manual_target = [r for r in manual_rows if r.field_name in TARGET_KEYS]
    auto_for_manual = [r for r in sample_rows if r.audit_mode == "automated" and r.company_code in manual_codes and r.field_name in TARGET_KEYS]
    # compare manual vs what automated would have been on same cells
    agree = 0
    total_m = 0
    for mr in manual_target:
        total_m += 1
        ar = next((x for x in population_rows if x.company_code == mr.company_code and x.field_name == mr.field_name), None)
        if ar and ar.strict_label == mr.strict_label:
            agree += 1
        elif ar and ar.strict_label in ("partial", "not_found_unverified") and mr.strict_label in ("partial", "not_found_correct", "not_found_missed"):
            if ar.strict_label == mr.strict_label:
                agree += 1
    cal_rate = 100 * agree / total_m if total_m else 0

    missed_manual = sum(1 for r in manual_target if r.strict_label == "not_found_missed")
    nf_manual = sum(1 for r in manual_target if r.strict_label.startswith("not_found"))

    L: list[str] = []
    a = L.append
    a("# full_market_2024 Strict Audit Summary")
    a("")
    a(f"_Generated: {ts}_")
    a("")
    a("## 1. Sample design")
    a("")
    a("- **Method**: Hybrid — automated adversarial recheck over all non-financial ok companies, plus PDF-backed deep verification on a stratified manual subset.")
    a(f"- **Population**: {n_co} non-financial companies with status=ok, all 11 industrial fields ({n_co * 11} field-cells).")
    a(f"- **Targeted sample CSV**: {len(sample_codes)} companies × 7 fields = {len(sample_rows)} rows.")
    a(f"- **Manual PDF subset**: {len(manual_codes)} companies × 7 targeted fields = {len(manual_target)} manual-verified cells.")
    a("- **Stratification**: board (bse/star/szse_main/chinext/sse_main) × proxy tier (high≥11, mid 9–10, low<9) × risky-field state (rnd/revenue plausible vs missing). Industry field unavailable (empty in YAML).")
    a("- **Targeted fields**: mda, main_business_segments, revenue_by_segment, revenue_by_region, rnd_investment, top_customers, top_suppliers.")
    a("")
    a("## 2. Companies and fields audited")
    a("")
    a(f"| scope | companies | field-cells |")
    a(f"|---|---:|---:|")
    a(f"| population (automated) | {n_co} | {len(population_rows)} |")
    a(f"| sample CSV (7 fields) | {len(sample_codes)} | {len(sample_rows)} |")
    a(f"| manual PDF (7 fields) | {len(manual_codes)} | {len(manual_target)} |")
    a("")
    a("## 3. Label counts (population, all 11 fields)")
    a("")
    pop_agg = agg(population_rows)
    a("| label | count | pct |")
    a("|---|---:|---:|")
    for lab, cnt in sorted(pop_agg.items(), key=lambda x: -x[1]):
        a(f"| {lab} | {cnt} | {100*cnt/len(population_rows):.1f}% |")
    a("")
    a("## 4. Proxy vs strict comparison")
    a("")
    a(f"| metric | mean / 11 |")
    a(f"|---|---:|")
    a(f"| proxy plausible (eval) | **{proxy_mean:.2f}** |")
    a(f"| strict usable (automated, usable only) | **{strict_mean:.2f}** |")
    a(f"| strict lenient (usable + partial) | **{lenient_mean:.2f}** |")
    a(f"| gap proxy − strict usable | **{proxy_mean - strict_mean:.2f}** |")
    a("")
    a("> Old baseline strict-usable **10.16/11** was on eval1000 with looser proxy (10.5/11). Current proxy already uses tightened rnd/table rules (10.35/11). **Do not claim strict improved** without like-for-like comparison.")
    a("")
    a("## 5. Strict-usable estimate")
    a("")
    a(f"- **Population automated strict-usable: {strict_mean:.2f} / 11** ({100*strict_mean/11:.1f}%) over {n_co} non-financial companies.")
    a(f"- **Lenient band (usable+partial): {lenient_mean:.2f} / 11** ({100*lenient_mean/11:.1f}%).")
    a(f"- Manual PDF subset: {missed_manual} `not_found_missed` of {nf_manual} not_found-class cells in targeted fields ({len(manual_target)} cells).")
    a(f"- Automated vs manual label agreement on manual subset: **{agree}/{total_m} ({cal_rate:.0f}%)** (same strict_label).")
    a("")
    a("## 6. Major error patterns")
    a("")
    wrong_rows = [r for r in population_rows if r.strict_label == "wrong" and r.proxy_plausible]
    fp = Counter(r.field_name for r in wrong_rows)
    a("**False positives (proxy=true, strict=wrong)** — top fields:")
    for fld, cnt in fp.most_common(8):
        a(f"- `{fld}`: {cnt}")
    partial_pl = [r for r in population_rows if r.strict_label == "partial" and r.proxy_plausible]
    a("")
    a(f"- proxy=true but strict=partial: **{len(partial_pl)}** cells (overstated as fully correct by proxy).")
    a("- Common rnd pattern: per-product R&D rows without clear total label ≥10万元.")
    a("- Common section pattern: short snippets or out-of-region extractions marked plausible.")
    a("")
    a("## 7. Field-level observations (population)")
    a("")
    a("| field | usable | partial | wrong | not_found_unverified |")
    a("|---|---:|---:|---:|---:|")
    for key in INDUSTRIAL_KEYS:
        c = pop_by_field[key]
        a(f"| {key} | {c.get('usable',0)} | {c.get('partial',0)} | {c.get('wrong',0)} | {c.get('not_found_unverified',0)} |")
    a("")
    a("## 8. Board-level observations")
    a("")
    a("| board | n | strict usable mean /11 |")
    a("|---|---:|---:|")
    for board in ["bse", "star", "szse_main", "chinext", "sse_main"]:
        scores = pop_by_board.get(board, [])
        if scores:
            a(f"| {board} | {len(scores)} | {statistics.mean(scores):.2f} |")
    a("")
    a("## 9. Financial companies (qualitative, separate from headline)")
    a("")
    if fin_notes:
        a("\n".join(fin_notes))
    else:
        a("- No financial profiles reviewed.")
    a("")
    a("## 10. Caveats")
    a("")
    a("- This is an **automated adversarial recheck** over stored values, **not** manual validation of all 62,890 SQLite rows.")
    a(f"- `not_found_missed` is estimated only from **{len(manual_codes)}-company PDF deep-read**, not the full population.")
    a("- `not_found_unverified` cells are conservatively excluded from strict-usable credit.")
    a("- Do not claim the entire full_market_2024 corpus is manually verified.")
    a("- Do not claim strict-usable improved vs historical 10.16/11 without noting proxy baseline shift.")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Strict audit full_market_2024")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--companies-yaml", default=DEFAULT_YAML)
    ap.add_argument("--sample-size", type=int, default=55)
    ap.add_argument("--manual-size", type=int, default=15)
    ap.add_argument("--seed", type=int, default=20260624)
    args = ap.parse_args()

    out_dir = os.path.abspath(args.out_dir)
    meta = _load_meta(args.companies_yaml)
    eval_path = os.path.join(out_dir, "eval_results.json")
    eval_rows = json.load(open(eval_path, encoding="utf-8"))
    nonfin = [r for r in eval_rows if r["status"] == "ok" and not r.get("financial")]
    print(f"[strict_audit] non-fin ok companies: {len(nonfin)}")

    population_rows: list[AuditRow] = []
    missing = 0
    for er in nonfin:
        code = er["stock_code"]
        board = meta.get(code, {}).get("board", "")
        rows = audit_company(code, er["short_name"], board, er, out_dir, manual=False)
        if not rows:
            missing += 1
            continue
        population_rows.extend(rows)
    print(f"[strict_audit] population field-cells: {len(population_rows)} (missing profiles: {missing})")

    sample_codes = select_sample_companies(eval_rows, meta, n=args.sample_size, seed=args.seed)
    manual_codes = select_manual_companies(eval_rows, meta, n=args.manual_size, seed=args.seed)
    print(f"[strict_audit] sample companies: {len(sample_codes)}, manual: {len(manual_codes)}")

    sample_rows: list[AuditRow] = []
    for code in sample_codes:
        er = next(r for r in nonfin if r["stock_code"] == code)
        board = meta.get(code, {}).get("board", "")
        for row in audit_company(code, er["short_name"], board, er, out_dir, manual=False):
            if row.field_name in TARGET_KEYS:
                sample_rows.append(row)

    manual_rows: list[AuditRow] = []
    for code in manual_codes:
        er = next(r for r in nonfin if r["stock_code"] == code)
        board = meta.get(code, {}).get("board", "")
        for row in audit_company(code, er["short_name"], board, er, out_dir, manual=True):
            if row.field_name in TARGET_KEYS:
                manual_rows.append(row)

    # CSV: sample automated + manual overrides for manual companies
    csv_rows: list[AuditRow] = []
    manual_set = set(manual_codes)
    for r in sample_rows:
        if r.company_code in manual_set:
            mr = next((x for x in manual_rows if x.company_code == r.company_code and x.field_name == r.field_name), r)
            csv_rows.append(mr)
        else:
            csv_rows.append(r)
    # add manual-only companies not in sample
    for r in manual_rows:
        if not any(x.company_code == r.company_code and x.field_name == r.field_name for x in csv_rows):
            csv_rows.append(r)

    csv_path = os.path.join(out_dir, "strict_audit_sample.csv")
    summary_path = os.path.join(out_dir, "strict_audit_summary.md")
    write_csv(csv_path, csv_rows)
    fin_notes = financial_qualitative(out_dir, eval_rows, meta)
    write_summary(
        summary_path,
        population_rows=population_rows,
        sample_rows=csv_rows,
        manual_rows=manual_rows,
        manual_codes=manual_codes,
        sample_codes=sample_codes,
        fin_notes=fin_notes,
        eval_rows=eval_rows,
    )

    co_scores = []
    by_co: dict[str, list[AuditRow]] = defaultdict(list)
    for r in population_rows:
        by_co[r.company_code].append(r)
    for crows in by_co.values():
        co_scores.append(_strict_score(crows, lenient=False) * 11)
    print(f"[strict_audit] population strict-usable mean: {statistics.mean(co_scores):.2f}/11")
    print(f"[strict_audit] wrote {csv_path}")
    print(f"[strict_audit] wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
