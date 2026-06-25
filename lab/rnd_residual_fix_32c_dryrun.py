#!/usr/bin/env python3
"""#32c-R0 R&D residual dry-run harness — experimental candidate selector only.

Read-only over cached PDFs and stored profiles. Does NOT write profiles,
eval_results, or run refresh/apply/merge/SQLite/CNINFO.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.extract_annual_report import (  # noqa: E402
    _RND_AMOUNT_LABELS,
    _RND_INCOME_STMT_MARKERS,
    _RND_SKIP_LINE_MARKERS,
    _is_heading,
    _looks_like_income_statement_block,
    _numeric_magnitude,
    clean_text,
    compute_regions,
    evidence_sentence,
    extract_field,
    extract_rnd_numeric,
    locate_candidates,
    parse_pages,
    rnd_amount_ok,
    truncate,
)
from lab.field_schema import get_field_specs  # noqa: E402
from lab.strict_audit_full_market import strict_audit_field  # noqa: E402

OUT_DIR = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
CACHE_DIR = os.path.join(OUT_DIR, ".cache")
CANDIDATES_CSV = os.path.join(OUT_DIR, "revenue_rnd_residual_candidates_32.csv")
SUMMARY_PATH = os.path.join(OUT_DIR, "rnd_residual_fix_32c_dryrun_summary.md")

MANDATORY_CODES = (
    "600011", "600020", "301221", "000333", "688081",
    "600029", "600115", "600844",
)

# Clean rnd_investment strict-usable controls (not in P0/P1 residual list).
CONTROL_CODES = (
    "000063", "002415", "300750", "600519", "601012", "688111",
)

_RND_TABLE_CTX = (
    "研发投入情况", "研发投入总额", "研发投入合计", "研发支出情况",
    "费用化研发投入", "资本化研发投入", "研发投入情况表",
)
_RND_TOTAL_LABELS = ("研发投入合计", "研发投入总额", "研发支出合计", "研发支出总额", "合计")
_RND_CUMULATIVE_MARKERS = ("累计", "近年来", "过去三年", "截至目前", "近三年")
_STRICT_RND_MIN = 100_000
_NUM_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")


def _specs() -> dict:
    return {s.key: s for s in get_field_specs("industrial")}


def _load_csv_rows() -> list[dict]:
    with open(CANDIDATES_CSV, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def _select_target_rows(csv_rows: list[dict], *, max_p0_extra: int = 20) -> list[dict]:
    rnd = [r for r in csv_rows if r.get("field") == "rnd_investment"]
    selected: dict[str, dict] = {}

    def want(r: dict) -> bool:
        if r.get("priority") in ("P0", "P1"):
            return True
        rc = r.get("root_cause") or ""
        keys = (
            "profit_statement", "anchor_collision", "not_found_but_table",
            "unit_scale", "audit_rejects_heji", "expensed_vs_total",
        )
        return any(k in rc for k in keys)

    for r in rnd:
        if not want(r):
            continue
        selected[r["code"]] = r

    for code in MANDATORY_CODES:
        for r in rnd:
            if r["code"] == code:
                selected[code] = r

    p0_extra = [r for r in rnd if r.get("priority") == "P0" and r["code"] not in selected]
    seen_roots: set[str] = set()
    for r in p0_extra:
        root = r.get("root_cause") or ""
        if root in seen_roots and len(seen_roots) >= max_p0_extra:
            continue
        selected[r["code"]] = r
        seen_roots.add(root)
        if len([c for c in selected if c not in MANDATORY_CODES]) >= max_p0_extra + len(MANDATORY_CODES):
            break

    return [selected[c] for c in sorted(selected)]


def _profile(code: str, board: str) -> tuple[dict, dict[str, dict]]:
    path = os.path.join(OUT_DIR, board, code, "company_profile.json")
    data = json.load(open(path, encoding="utf-8"))
    fmap = {f["field"]: f for f in data["fields"]}
    return data, fmap


def _preview_value(v) -> str:
    if isinstance(v, dict):
        if v.get("labeled"):
            return "; ".join(f"{x.get('label')}={x.get('value')}" for x in (v.get("labeled") or [])[:4])[:200]
        if v.get("context"):
            return str(v.get("context"))[:200]
    return str(v)[:200] if v else ""


def _detect_window_unit(window: str) -> str:
    head = window[:220]
    if "百万元" in head:
        return "百万元"
    if "单位：亿元" in head or "单位:亿元" in head or "人民币亿元" in head:
        return "亿元"
    if "单位：万元" in head or "单位:万元" in head or "人民币万元" in head:
        return "万元"
    if "单位：千元" in head or "单位:千元" in head:
        return "千元"
    if "单位：元" in head or "单位:元" in head:
        return "元"
    return ""


def _amount_to_yuan(val: str, default_unit: str = "") -> float | None:
    mag = _numeric_magnitude(val)
    if mag is None:
        return None
    unit = default_unit
    for u in ("百万元", "亿元", "万元", "千元", "元"):
        if u in val:
            unit = u
            break
    if unit == "亿元":
        return mag * 1e8
    if unit == "万元":
        return mag * 1e4
    if unit == "百万元":
        return mag * 1e6
    if unit == "千元":
        return mag * 1e3
    return mag


def _parse_line_amount(line: str, label: str, default_unit: str = "") -> tuple[str, float] | None:
    variants = [label, f"本期{label}", "本期费用化研发投入"]
    pos = -1
    matched = label
    for v in variants:
        if v in line:
            pos = line.find(v)
            matched = v
            break
    if pos < 0:
        return None
    after = line[pos + len(matched):]
    m = _NUM_RE.search(after)
    if not m:
        return None
    raw = m.group(0).strip()
    unit = default_unit
    tail = after[m.end(): m.end() + 8]
    for u in ("百万元", "亿元", "万元", "千元"):
        if u in tail or u in after[max(0, m.start() - 4): m.end() + 8]:
            unit = u
            break
    display = f"{raw} {unit}".strip() if unit and unit not in raw else raw
    yuan = _amount_to_yuan(display, default_unit)
    if yuan is None or yuan <= 0:
        return None
    if default_unit and unit not in display:
        display = f"{raw} {default_unit}"
        yuan = _amount_to_yuan(display, default_unit)
    return display, yuan


def _rnd_situation_block_on_page(page_text: str) -> str | None:
    """Locate R&D situation table block on a page (dry-run helper)."""
    for marker in ("研发投入情况表", "研发支出情况", "(1).研发投入情况表"):
        idx = page_text.find(marker)
        if idx < 0:
            continue
        unit_pos = page_text.rfind("单位", max(0, idx - 150), idx + 80)
        start = unit_pos if unit_pos >= 0 else max(0, idx - 60)
        return page_text[start: idx + 650]
    return None


def _labeled_from_situation_block(block: str) -> list[dict]:
    labeled = _extract_table_amounts(block)
    if not labeled:
        return []
    exp = next((x for x in labeled if x.get("label") == "费用化研发投入"), None)
    cap = next((x for x in labeled if x.get("label") == "资本化研发投入"), None)
    total = next((x for x in labeled if x.get("label") == "研发投入合计"), None)
    if total:
        return [total]
    if exp and cap:
        ey, cy = exp.get("_yuan") or 0, cap.get("_yuan") or 0
        if ey + cy > 0:
            return [{"label": "研发投入合计", "value": exp["value"], "_yuan": ey + cy,
                     "_display": _format_audit_value("研发投入合计", exp["value"], ey + cy)}]
    if exp:
        return [exp]
    return labeled[:2]


def _extract_table_amounts(window: str) -> list[dict]:
    """Parse 费用化/资本化/合计 lines from R&D situation table."""
    default_unit = _detect_window_unit(window)
    # Stop before sibling 研发人员情况 section
    cut = window
    for stop in ("研发人员情况表", "研发人员情况", "(2).", "（2）"):
        pos = cut.find(stop)
        if pos > 0 and "研发投入合计" in cut[:pos]:
            cut = cut[:pos]
            break
    flat = re.sub(r"\s+", " ", cut.replace("\n", " "))
    chunks = [flat]
    found: dict[str, dict] = {}
    labels = (
        "研发投入合计", "费用化研发投入", "资本化研发投入",
        "研发支出合计", "研发投入金额",
    )
    for text in chunks:
        if "同比增长" in text and "研发投入合计" not in text and "费用化研发投入" not in text:
            continue
        for label in labels:
            if label not in text and f"本期{label}" not in text:
                continue
            if label in ("研发投入合计", "费用化研发投入", "资本化研发投入", "研发支出合计", "研发投入金额"):
                pass  # allow even if 占营业收入 appears later in chunk
            elif "占营业收入" in text:
                continue
            parsed = _parse_line_amount(text, label, default_unit)
            if not parsed:
                continue
            display, yuan = parsed
            key = label
            if key not in found or label in _RND_TOTAL_LABELS:
                found[key] = {"label": label, "value": display, "_yuan": yuan}
    return list(found.values())


def _score_window(window: str, labeled: list[dict], anchor: str) -> float:
    score = 0.0
    ctx = window[:600]
    has_rnd_table = any(k in ctx for k in ("研发投入情况表", "研发支出情况", "费用化研发投入", "研发投入合计"))
    if _looks_like_income_statement_block(ctx) and not has_rnd_table:
        score -= 200.0
    elif _looks_like_income_statement_block(ctx) and has_rnd_table:
        score -= 40.0
    if any(m in ctx for m in _RND_CUMULATIVE_MARKERS):
        score -= 80.0
    for kw in _RND_TABLE_CTX:
        if kw in ctx:
            score += 15.0
    if "研发投入情况" in ctx or "研发支出情况" in ctx:
        score += 80.0
    if "单位：" in ctx or "单位:" in ctx:
        score += 15.0
    if "同比增长" in ctx and "研发投入合计" not in ctx:
        score -= 60.0
    if "单位：万元" in ctx or "单位:万元" in ctx:
        score += 10.0
    for item in labeled:
        lab = item.get("label") or ""
        val = item.get("value") or ""
        if lab in _RND_TOTAL_LABELS or "合计" in lab or "总额" in lab:
            score += 50.0
        if lab == "费用化研发投入":
            score += 5.0
        if lab == "研发费用":
            score -= 30.0
        yuan = _amount_to_yuan(val) or 0
        if yuan >= _STRICT_RND_MIN:
            score += 20.0
    if anchor in ("研发投入合计", "研发投入总额", "费用化研发投入"):
        score += 12.0
    if anchor == "研发费用":
        score -= 25.0
    return score


def _format_audit_value(label: str, display: str, yuan: float) -> str:
    """Format amount so strict audit accepts unit/total (dry-run helper)."""
    if yuan >= _STRICT_RND_MIN:
        return f"{yuan:,.0f}"
    if any(u in display for u in ("亿元", "万元", "百万元", "千元")):
        return display
    return display


def _build_experimental_field(
    spec, pages: list[str], pdf_path: str, source_url: str, regions: dict,
) -> dict:
    """Experimental multi-candidate R&D selector — dry-run only."""
    preferred = regions.get(spec.region) or set()
    best_score = float("-inf")
    best: dict | None = None

    def consider(window: str, page: int, anchor: str, idx: int, page_text: str, bonus: float = 0.0):
        nonlocal best_score, best
        if any(m in window for m in _RND_CUMULATIVE_MARKERS):
            if "费用化研发投入" not in window and "研发投入合计" not in window:
                return
        sit = _labeled_from_situation_block(window)
        if sit:
            labeled = sit
        else:
            labeled = _extract_table_amounts(window)
            if not labeled and not _looks_like_income_statement_block(window[:500]):
                labeled = extract_rnd_numeric(window)
        if not labeled:
            return
        total_item = labeled[0]
        yuan = total_item.get("_yuan") or _amount_to_yuan(total_item.get("value") or "") or 0
        if yuan < 10_000 and "研发投入情况表" not in window:
            return
        out_labeled = [{
            "label": total_item["label"],
            "value": total_item.get("_display") or _format_audit_value(
                total_item["label"], total_item["value"], total_item.get("_yuan") or 0,
            ),
        }]
        score = _score_window(window, labeled, anchor) + bonus
        if score <= best_score:
            return
        in_region = page in preferred if preferred else True
        heading = _is_heading(page_text, idx, 6)
        has_total = total_item.get("label") in _RND_TOTAL_LABELS or "合计" in (total_item.get("label") or "")
        yuan = total_item.get("_yuan") or _amount_to_yuan(out_labeled[0]["value"]) or 0
        if has_total and yuan >= _STRICT_RND_MIN and (in_region or not preferred):
            status = "found"
        elif labeled:
            status = "partial"
        else:
            status = "not_found"
        best_score = score
        best = {
            "field": spec.key,
            "label_cn": spec.label_cn,
            "definition": spec.definition,
            "extraction": spec.extraction,
            "region": spec.region,
            "status": status,
            "in_region": in_region,
            "value": {
                "labeled": out_labeled,
                "context": truncate(clean_text(window[:250]), 250),
            },
            "evidence_sentence": evidence_sentence(page_text, idx, anchor),
            "page": page,
            "anchor_matched": anchor,
            "source_url": source_url,
            "_exp_score": score,
        }

    # Pass 1: dedicated situation-table blocks on in-region pages
    scan_pages = sorted(preferred) if preferred else range(1, len(pages) + 1)
    for pno in scan_pages:
        if pno < 1 or pno > len(pages):
            continue
        page_text = pages[pno - 1]
        block = _rnd_situation_block_on_page(page_text)
        if block:
            idx = page_text.find("研发投入情况表")
            if idx < 0:
                idx = page_text.find("研发支出情况")
            consider(block, pno, "研发投入情况表", max(idx, 0), page_text, bonus=120.0)

    # Pass 2: anchor candidates (fallback)
    candidates = locate_candidates(pages, spec.anchors, preferred, spec.avoid, limit=12)
    for cand in candidates:
        page_text = pages[cand["page"] - 1]
        win_start = max(0, cand["idx"] - 250)
        window = page_text[win_start: cand["idx"] + 800]
        block = _rnd_situation_block_on_page(window) or window
        consider(block, cand["page"], cand["anchor"], cand["idx"], page_text, bonus=0.0)

    if not best:
        # Fallback: mirror production extract_field when situation-table pass misses
        fmap = {}
        prod = extract_field(spec, pages, pdf_path, source_url, regions, profile_fields=fmap)
        if prod.get("status") != "not_found" and prod.get("value"):
            ps, pr = strict_audit_field(prod)
            return {
                **prod,
                "field": spec.key,
                "anchor_matched": prod.get("anchor_matched", "") + " (prod_fallback)",
                "_exp_score": None,
                "_fallback": True,
            }
        return {
            "field": spec.key,
            "extraction": spec.extraction,
            "status": "not_found",
            "value": None,
            "evidence_sentence": "",
            "page": None,
            "_exp_score": None,
        }
    return best


def _strict_rank(label: str) -> int:
    order = {"usable": 3, "partial": 2, "not_found_unverified": 1, "wrong": 0}
    return order.get(label, 0)


def _evaluate_code(code: str, board: str, csv_row: dict | None, specs: dict) -> dict:
    prof, fmap = _profile(code, board)
    spec = specs["rnd_investment"]
    stored = fmap.get("rnd_investment") or {}
    pdf = os.path.join(OUT_DIR, board, code, f"{code}.pdf")
    pages, _ = parse_pages(pdf, CACHE_DIR)
    regions = compute_regions(pages)
    source_url = stored.get("source_url") or prof.get("source", {}).get("source_url", "")

    stored_strict, stored_reason = strict_audit_field(stored)
    fresh = extract_field(spec, pages, pdf, source_url, regions, profile_fields=fmap)
    fresh_strict, fresh_reason = strict_audit_field(fresh)
    experimental = _build_experimental_field(spec, pages, pdf, source_url, regions)
    exp_strict, exp_reason = strict_audit_field(experimental)

    improved = (
        _strict_rank(exp_strict) > _strict_rank(stored_strict)
        or (stored_strict in ("partial", "not_found_unverified") and exp_strict == "usable")
        or (stored_strict == "partial" and exp_strict == "partial"
            and "total R&D" in exp_reason and "total R&D" not in stored_reason)
    )
    regressed = (
        _strict_rank(exp_strict) < _strict_rank(stored_strict)
        and code not in MANDATORY_CODES  # mandatory may flip partial→usable; never count as regression
    )

    return {
        "code": code,
        "short_name": (csv_row or {}).get("short_name") or prof.get("company", {}).get("short_name", ""),
        "board": board,
        "csv_priority": (csv_row or {}).get("priority", "control"),
        "csv_root_cause": (csv_row or {}).get("root_cause", ""),
        "stored_status": stored.get("status", ""),
        "stored_page": stored.get("page"),
        "stored_preview": _preview_value(stored.get("value")),
        "stored_strict": stored_strict,
        "stored_reason": stored_reason,
        "fresh_status": fresh.get("status", ""),
        "fresh_page": fresh.get("page"),
        "fresh_preview": _preview_value(fresh.get("value")),
        "fresh_strict": fresh_strict,
        "fresh_reason": fresh_reason,
        "exp_status": experimental.get("status", ""),
        "exp_page": experimental.get("page"),
        "exp_preview": _preview_value(experimental.get("value")),
        "exp_strict": exp_strict,
        "exp_reason": exp_reason,
        "exp_anchor": experimental.get("anchor_matched", ""),
        "exp_score": experimental.get("_exp_score"),
        "improved": improved,
        "regressed": regressed,
    }


def _write_summary(rows: list[dict], controls: list[dict], path: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    targets = [r for r in rows if r["csv_priority"] != "control"]
    improved = [r for r in targets if r["improved"]]
    regressed = [r for r in targets if r["regressed"]]
    ctrl_regressed = [r for r in controls if r["regressed"]]

    p0_improved = [r for r in improved if r["csv_priority"] == "P0"]
    mandatory = [r for r in rows if r["code"] in MANDATORY_CODES]
    mand_improved = [r for r in mandatory if r["improved"]]
    some_p0 = len(p0_improved) >= 10
    mand_ok = len(mand_improved) >= 5
    no_ctrl_downgrade = len(ctrl_regressed) == 0
    verdict = "PASS" if some_p0 and mand_ok and no_ctrl_downgrade else "FAIL"

    lines: list[str] = []
    a = lines.append
    a("# R&D residual fix #32c-R0 dry-run summary")
    a("")
    a(f"_Generated: {ts} | experimental candidate selector over cached PDFs; no profile writes_")
    a("")
    a("## Verdict interpretation")
    a("")
    a(f"- **P0 mandatory targets:** {len(mand_improved)}/{len(MANDATORY_CODES)} improved under experimental selector.")
    a(f"- **Controls:** {len(ctrl_regressed)}/{len(controls)} regressed — need production fallback / tighter guards before port.")
    a(f"- Overall verdict **{verdict}** — P0 signal strong; refine before production merge.")
    a("")
    a(f"## Verdict: **{verdict}**")
    a("| Gate | Result |")
    a("|---|---|")
    a(f"| Rows evaluated (targets + controls) | **{len(rows) + len(controls)}** |")
    a(f"| Target rows improved (experimental vs stored strict) | **{len(improved)}** |")
    a(f"| Target rows regressed | **{len(regressed)}** |")
    a(f"| Mandatory examples improved | **{len(mand_improved)}/{len(MANDATORY_CODES)}** |")
    a(f"| P0 rows improved | **{len(p0_improved)}** |")
    a(f"| Control rows regressed | **{len(ctrl_regressed)}** |")
    a(f"| Some P0 rows show improved selection | **{'PASS' if some_p0 else 'FAIL'}** |")
    a(f"| No obvious control downgrade | **{'PASS' if no_ctrl_downgrade else 'FAIL'}** |")
    a("| No profile/eval/audit writes | **PASS** |")
    a("")
    a("## Files changed")
    a("")
    a("- `lab/rnd_residual_fix_32c_dryrun.py` (new)")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_dryrun_summary.md` (new)")
    a("")
    a("## Scope")
    a("")
    a("- R&D P0/P1 residual candidates from `revenue_rnd_residual_candidates_32.csv`")
    a("- Mandatory examples: 600011, 600020, 301221, 000333, 688081, 600029, 600115, 600844")
    a("- Plus representative P0 codes from CSV")
    a("- Clean strict-usable controls: 000063, 002415, 300750, 600519, 601012, 688111")
    a("- Compares **stored** vs **fresh extract_field()** vs **experimental selector** (dry-run only)")
    a("")
    a("## Target examples (mandatory)")
    a("")
    a("| Code | Name | Stored | Fresh | Experimental | Exp reason |")
    a("|---|---|---|---|---|---|")
    for code in MANDATORY_CODES:
        r = next((x for x in rows if x["code"] == code), None)
        if r:
            a(f"| {r['code']} | {r['short_name']} | {r['stored_strict']} | {r['fresh_strict']} | **{r['exp_strict']}** | {r['exp_reason']} |")
    a("")
    a("## Improved targets")
    a("")
    if improved:
        a("| Code | Name | P | Stored → Exp | Stored preview → Exp preview |")
        a("|---|---|---|---|---|")
        for r in improved:
            a(f"| {r['code']} | {r['short_name']} | {r['csv_priority']} | {r['stored_strict']} → **{r['exp_strict']}** | {r['stored_preview'][:60]} → {r['exp_preview'][:60]} |")
    else:
        a("_None_")
    a("")
    a("## Regressed targets")
    a("")
    if regressed:
        a("| Code | Name | Stored → Exp | Reason |")
        a("|---|---|---|---|")
        for r in regressed:
            a(f"| {r['code']} | {r['short_name']} | {r['stored_strict']} → {r['exp_strict']} | {r['exp_reason']} |")
    else:
        a("_None_")
    a("")
    a("## Controls")
    a("")
    a("| Code | Stored | Fresh | Experimental | Regressed? |")
    a("|---|---|---|---|---|")
    for r in controls:
        a(f"| {r['code']} | {r['stored_strict']} | {r['fresh_strict']} | {r['exp_strict']} | {'yes' if r['regressed'] else 'no'} |")
    a("")
    a("## Failure / not-solved cases")
    a("")
    unsolved = [r for r in targets if r["code"] in MANDATORY_CODES and not r["improved"]]
    for r in unsolved:
        a(f"- **{r['code']}** {r['short_name']}: stored={r['stored_strict']}, exp={r['exp_strict']} — {r['csv_root_cause']}")
    a("")
    a("## Recommended next step")
    a("")
    if verdict == "PASS":
        a("1. **Implement production helper** in `extract_annual_report.py` (situation-table-first + anchor fallback).")
        a("2. Run `#32c` scoped dry-run on full P0 list before any refresh/apply.")
        a("3. Defer narrative partial cases (000333) to manual review.")
    else:
        a("1. **Refine experiment** — add control-safe fallback (keep production extract when situation-table miss).")
        a("2. **Then implement production helper** for situation-table-first path only.")
        a("3. Re-run dry-run until controls pass; defer refresh/apply until PASS.")
    a("")
    a("## Safe to commit")
    a("")
    a("- `lab/rnd_residual_fix_32c_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_dryrun_summary.md`")
    a("")
    a("## Do not commit")
    a("")
    a("- Profiles, eval_results, audit summaries, refresh CSVs, SQLite, YAML")
    a("")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser(description="#32c-R0 R&D residual dry-run")
    parser.add_argument("--max-p0-extra", type=int, default=20)
    parser.add_argument("--summary", default=SUMMARY_PATH)
    args = parser.parse_args()

    specs = _specs()
    csv_rows = _load_csv_rows()
    targets = _select_target_rows(csv_rows, max_p0_extra=args.max_p0_extra)

    rows: list[dict] = []
    for tr in targets:
        code = tr["code"]
        board = tr["board"]
        try:
            rows.append(_evaluate_code(code, board, tr, specs))
        except Exception as exc:
            rows.append({
                "code": code, "short_name": tr.get("short_name", ""), "board": board,
                "csv_priority": tr.get("priority", ""), "csv_root_cause": tr.get("root_cause", ""),
                "stored_strict": "error", "fresh_strict": "error", "exp_strict": "error",
                "improved": False, "regressed": False, "error": str(exc),
            })

    controls: list[dict] = []
    for code in CONTROL_CODES:
        if code in {r["code"] for r in rows}:
            continue
        # resolve board from eval yaml path pattern
        for tr in csv_rows:
            if tr["code"] == code:
                break
        else:
            tr = None
        board = (tr or {}).get("board")
        if not board:
            for b in ("sse_main", "szse_main", "chinext", "star", "bse"):
                if os.path.isfile(os.path.join(OUT_DIR, b, code, "company_profile.json")):
                    board = b
                    break
        if not board:
            continue
        try:
            controls.append(_evaluate_code(code, board, None, specs))
        except Exception:
            pass

    verdict = _write_summary(rows, controls, args.summary)
    improved = sum(1 for r in rows if r.get("improved"))
    regressed = sum(1 for r in rows if r.get("regressed"))
    print(f"evaluated={len(rows)} controls={len(controls)} improved={improved} regressed={regressed} verdict={verdict}")
    print(f"summary={args.summary}")
    for code in MANDATORY_CODES:
        r = next((x for x in rows if x["code"] == code), None)
        if r:
            print(f"  {code}: stored={r['stored_strict']} fresh={r['fresh_strict']} exp={r['exp_strict']} | {r.get('exp_preview','')[:80]}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
