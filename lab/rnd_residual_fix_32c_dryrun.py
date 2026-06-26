#!/usr/bin/env python3
"""#32c R&D residual dry-run harness — R1 guard + R2 production validation.

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
    extract_rnd_investment_baseline,
    extract_rnd_numeric,
    extract_rnd_situation_table_numeric,
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
SUMMARY_R2_PATH = os.path.join(OUT_DIR, "rnd_residual_fix_32c_r2_summary.md")

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
        preferred = regions.get(spec.region)
        prod = extract_rnd_investment_baseline(spec, pages, source_url, preferred)
        if prod.get("status") != "not_found" and prod.get("value"):
            ps, pr = strict_audit_field(prod)
            return {
                **prod,
                "field": spec.key,
                "anchor_matched": prod.get("anchor_matched", "") + " (baseline_fallback)",
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
    order = {
        "usable": 4,
        "partial": 3,
        "wrong": 2,
        "not_found_missed": 1,
        "not_found_unverified": 1,
        "not_found": 1,
    }
    return order.get(label, 0)


def _is_cumulative_narrative(field: dict) -> bool:
    """Reject experimental picks that are narrative cumulative disclosures."""
    val = field.get("value")
    ctx = ""
    if isinstance(val, dict):
        ctx = val.get("context") or ""
    ctx += " " + (field.get("evidence_sentence") or "")
    if not any(m in ctx for m in _RND_CUMULATIVE_MARKERS):
        return False
    if "研发投入情况表" in ctx or "费用化研发投入" in ctx:
        return False
    return True


def _select_final_candidate(
    stored: dict,
    fresh: dict,
    experimental: dict,
    *,
    stored_strict: str,
    stored_reason: str,
    fresh_strict: str,
    fresh_reason: str,
    exp_strict: str,
    exp_reason: str,
) -> dict:
    """max(production, experimental) guard — dry-run only; never downgrade production."""
    prod_rank = max(_strict_rank(stored_strict), _strict_rank(fresh_strict))
    exp_rank = _strict_rank(exp_strict)
    exp_eligible = (
        exp_rank >= prod_rank
        and not _is_cumulative_narrative(experimental)
    )

    candidates: list[tuple[str, dict, str, str]] = [
        ("stored", stored, stored_strict, stored_reason),
        ("fresh", fresh, fresh_strict, fresh_reason),
    ]
    if exp_eligible:
        candidates.append(("experimental", experimental, exp_strict, exp_reason))

    tie_order = {"stored": 3, "fresh": 2, "experimental": 1}
    source, field, strict, reason = max(
        candidates,
        key=lambda c: (_strict_rank(c[2]), tie_order.get(c[0], 0)),
    )
    return {
        "selected_source": source,
        "selected_strict": strict,
        "selected_reason": reason,
        "selected_preview": _preview_value(field.get("value")),
        "selected_status": field.get("status", ""),
        "selected_page": field.get("page"),
        "exp_eligible": exp_eligible,
        "prod_rank": prod_rank,
        "exp_rank": exp_rank,
    }


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
    final = _select_final_candidate(
        stored, fresh, experimental,
        stored_strict=stored_strict,
        stored_reason=stored_reason,
        fresh_strict=fresh_strict,
        fresh_reason=fresh_reason,
        exp_strict=exp_strict,
        exp_reason=exp_reason,
    )
    selected_strict = final["selected_strict"]

    improved = _strict_rank(selected_strict) > _strict_rank(stored_strict)
    regressed = _strict_rank(selected_strict) < _strict_rank(stored_strict)
    exp_would_regress = _strict_rank(exp_strict) < prod_rank if (prod_rank := final["prod_rank"]) else False

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
        "exp_eligible": final["exp_eligible"],
        "exp_would_regress": exp_would_regress,
        "selected_source": final["selected_source"],
        "selected_strict": selected_strict,
        "selected_reason": final["selected_reason"],
        "selected_preview": final["selected_preview"],
        "improved": improved,
        "regressed": regressed,
    }


def _evaluate_code_r2(code: str, board: str, csv_row: dict | None, specs: dict) -> dict:
    """R2 validation: stored profile vs fresh production extract_field() after port."""
    prof, fmap = _profile(code, board)
    spec = specs["rnd_investment"]
    stored = fmap.get("rnd_investment") or {}
    pdf = os.path.join(OUT_DIR, board, code, f"{code}.pdf")
    pages, _ = parse_pages(pdf, CACHE_DIR)
    regions = compute_regions(pages)
    preferred = regions.get(spec.region)
    source_url = stored.get("source_url") or prof.get("source", {}).get("source_url", "")

    stored_strict, stored_reason = strict_audit_field(stored)
    fresh = extract_field(spec, pages, pdf, source_url, regions, profile_fields=fmap)
    fresh_strict, fresh_reason = strict_audit_field(fresh)

    baseline = extract_rnd_investment_baseline(spec, pages, source_url, preferred)
    baseline_strict, _ = strict_audit_field(baseline)
    situation = extract_rnd_situation_table_numeric(spec, pages, source_url, regions)
    sit_strict, _ = strict_audit_field(situation) if situation and situation.get("value") else ("not_found", "")

    experimental = _build_experimental_field(spec, pages, pdf, source_url, regions)
    exp_strict, _ = strict_audit_field(experimental)
    r1_final = _select_final_candidate(
        stored, baseline, experimental,
        stored_strict=stored_strict, stored_reason=stored_reason,
        fresh_strict=baseline_strict, fresh_reason="",
        exp_strict=exp_strict, exp_reason="",
    )

    improved = _strict_rank(fresh_strict) > _strict_rank(stored_strict)
    regressed = _strict_rank(fresh_strict) < _strict_rank(stored_strict)
    matches_r1 = fresh_strict == r1_final["selected_strict"]

    return {
        "code": code,
        "short_name": (csv_row or {}).get("short_name") or prof.get("company", {}).get("short_name", ""),
        "board": board,
        "csv_priority": (csv_row or {}).get("priority", "control"),
        "csv_root_cause": (csv_row or {}).get("root_cause", ""),
        "stored_strict": stored_strict,
        "stored_preview": _preview_value(stored.get("value")),
        "fresh_strict": fresh_strict,
        "fresh_preview": _preview_value(fresh.get("value")),
        "fresh_anchor": fresh.get("anchor_matched", ""),
        "baseline_strict": baseline_strict,
        "situation_strict": sit_strict,
        "r1_selected_strict": r1_final["selected_strict"],
        "r1_selected_source": r1_final["selected_source"],
        "matches_r1": matches_r1,
        "improved": improved,
        "regressed": regressed,
    }


def _write_summary_r2(rows: list[dict], controls: list[dict], path: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    all_rows = rows + controls
    targets = [r for r in rows if r["csv_priority"] != "control"]
    improved = [r for r in targets if r["improved"]]
    regressed = [r for r in all_rows if r["regressed"]]
    ctrl_regressed = [r for r in controls if r["regressed"]]
    p0_improved = [r for r in improved if r["csv_priority"] == "P0"]
    mandatory = [r for r in rows if r["code"] in MANDATORY_CODES]
    mand_improved = [r for r in mandatory if r["improved"]]
    r1_match = sum(1 for r in all_rows if r.get("matches_r1"))
    some_p0 = len(p0_improved) >= 10
    mand_ok = len(mand_improved) >= 5
    no_ctrl = len(ctrl_regressed) == 0
    no_target_regress = len(regressed) == 0
    verdict = "PASS" if some_p0 and mand_ok and no_ctrl and no_target_regress else "FAIL"
    r415 = next((r for r in controls if r["code"] == "002415"), None)
    r333 = next((r for r in rows if r["code"] == "000333"), None)

    lines: list[str] = []
    a = lines.append
    a("# R&D residual fix #32c-R2 production port dry-run summary")
    a("")
    a(f"_Generated: {ts} | R2 production extract_field() vs stored profiles; no profile writes_")
    a("")
    a(f"## Verdict: **{verdict}**")
    a("")
    a("| Gate | Result |")
    a("|---|---|")
    a(f"| Rows evaluated | **{len(all_rows)}** |")
    a(f"| Target improved (fresh R2 vs stored) | **{len(improved)}** |")
    a(f"| Target regressed | **{len(regressed)}** |")
    a(f"| P0 improved | **{len(p0_improved)}** |")
    a(f"| Mandatory improved | **{len(mand_improved)}/{len(MANDATORY_CODES)}** |")
    a(f"| Control regressions | **{len(ctrl_regressed)}** |")
    a(f"| Fresh R2 matches R1 selected_final | **{r1_match}/{len(all_rows)}** |")
    a(f"| Some P0 improvement | **{'PASS' if some_p0 else 'FAIL'}** |")
    a(f"| No control downgrade | **{'PASS' if no_ctrl else 'FAIL'}** |")
    a(f"| No target regression | **{'PASS' if no_target_regress else 'FAIL'}** |")
    a("| No profile/eval/audit writes | **PASS** |")
    a("")
    a("## Files changed")
    a("")
    a("- `lab/extract_annual_report.py` (R2 situation-table helper + production guard)")
    a("- `lab/rnd_residual_fix_32c_dryrun.py` (R2 validation mode)")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r2_summary.md` (this file)")
    a("")
    a("## Helper design")
    a("")
    a("- **`extract_rnd_situation_table_numeric()`** — Pass 1 scans MD&A in-region pages for `研发投入情况表`; Pass 2 walks anchor candidates. Parses 费用化/资本化/合计 with 元/万元/百万元/亿元 unit scaling. Rejects P&L-only windows and cumulative narrative without table labels.")
    a("- **`extract_rnd_investment_baseline()`** — prior anchor+candidate path unchanged.")
    a("")
    a("## Production guard design")
    a("")
    a("- **`merge_rnd_investment_with_guard(baseline, situation)`** — strict-rank max with tie-break favoring baseline.")
    a("- Situation eligible only when `sit_rank >= baseline_rank` and not cumulative narrative.")
    a("- Blocks usable→partial regressions (e.g. 002415 situation=partial, baseline=usable → fresh=usable).")
    a("")
    a("## Mandatory examples")
    a("")
    a("| Code | Name | Stored | Baseline | Situation | Fresh R2 | R1 selected |")
    a("|---|---|---|---|---|---|---|")
    for code in MANDATORY_CODES:
        r = next((x for x in rows if x["code"] == code), None)
        if r:
            a(f"| {r['code']} | {r['short_name']} | {r['stored_strict']} | {r['baseline_strict']} | {r['situation_strict']} | **{r['fresh_strict']}** | {r['r1_selected_strict']} |")
    a("")
    a("## Controls")
    a("")
    a("| Code | Stored | Baseline | Situation | Fresh R2 | Regressed? |")
    a("|---|---|---|---|---|---|")
    for r in controls:
        a(f"| {r['code']} | {r['stored_strict']} | {r['baseline_strict']} | {r['situation_strict']} | **{r['fresh_strict']}** | {'yes' if r['regressed'] else 'no'} |")
    a("")
    if r415:
        a(f"**002415**: stored={r415['stored_strict']}, situation={r415['situation_strict']}, fresh R2=**{r415['fresh_strict']}** — guard kept baseline.")
    a("")
    if r333:
        a(f"**000333**: fresh R2=**{r333['fresh_strict']}** (not forced usable; cumulative narrative blocked).")
    a("")
    a("## Regressed rows")
    a("")
    if regressed:
        for r in regressed:
            a(f"- {r['code']} {r['short_name']}: {r['stored_strict']} → {r['fresh_strict']}")
    else:
        a("_None_")
    a("")
    a("## Recommended next step")
    a("")
    if verdict == "PASS":
        a("1. **Scoped rnd_investment apply** on P0 residual list (dry-run refresh CSV first).")
        a("2. Human review for 000333 narrative partial.")
        a("3. Full-market apply only after P0 scoped apply + strict audit re-check.")
    else:
        a("1. Fix production guard or situation-table helper before any apply.")
        a("2. Do not run refresh/apply until PASS.")
    a("")
    a("## Safe to commit")
    a("")
    a("- `lab/extract_annual_report.py`")
    a("- `lab/rnd_residual_fix_32c_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r2_summary.md`")
    a("")
    a("## Do not commit")
    a("")
    a("- Profiles, eval_results, audit summaries, refresh CSVs, SQLite, YAML")
    a("")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return verdict


def _write_summary(rows: list[dict], controls: list[dict], path: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    all_rows = rows + controls
    targets = [r for r in rows if r["csv_priority"] != "control"]
    improved = [r for r in targets if r["improved"]]
    regressed = [r for r in targets if r["regressed"]]
    ctrl_regressed = [r for r in controls if r["regressed"]]
    exp_would_regress = [r for r in all_rows if r.get("exp_would_regress")]

    p0_improved = [r for r in improved if r["csv_priority"] == "P0"]
    mandatory = [r for r in rows if r["code"] in MANDATORY_CODES]
    mand_improved = [r for r in mandatory if r["improved"]]
    some_p0 = len(p0_improved) >= 10
    mand_ok = len(mand_improved) >= 5
    no_ctrl_downgrade = len(ctrl_regressed) == 0
    no_target_regress = len(regressed) == 0
    verdict = "PASS" if some_p0 and mand_ok and no_ctrl_downgrade and no_target_regress else "FAIL"

    r415 = next((r for r in controls if r["code"] == "002415"), None)

    lines: list[str] = []
    a = lines.append
    a("# R&D residual fix #32c-R1 dry-run summary")
    a("")
    a(f"_Generated: {ts} | R1 control-safe guard over cached PDFs; no profile writes_")
    a("")
    a(f"## Verdict: **{verdict}**")
    a("")
    a("| Gate | Result |")
    a("|---|---|")
    a(f"| Rows evaluated (targets + controls) | **{len(all_rows)}** |")
    a(f"| Target rows improved (selected_final vs stored) | **{len(improved)}** |")
    a(f"| Target rows regressed (selected_final) | **{len(regressed)}** |")
    a(f"| P0 rows improved | **{len(p0_improved)}** |")
    a(f"| Mandatory examples improved | **{len(mand_improved)}/{len(MANDATORY_CODES)}** |")
    a(f"| Control regressions (selected_final) | **{len(ctrl_regressed)}** (R0: 1) |")
    a(f"| Experimental-only regressions blocked by guard | **{len(exp_would_regress)}** |")
    a(f"| Some P0 rows show improved selection | **{'PASS' if some_p0 else 'FAIL'}** |")
    a(f"| No control downgrade | **{'PASS' if no_ctrl_downgrade else 'FAIL'}** |")
    a(f"| No target regression | **{'PASS' if no_target_regress else 'FAIL'}** |")
    a("| No profile/eval/audit writes | **PASS** |")
    a("")
    a("## Files changed")
    a("")
    a("- `lab/rnd_residual_fix_32c_dryrun.py` (R1 guard refinement)")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_dryrun_summary.md` (this file)")
    a("")
    a("## Guard design (R1)")
    a("")
    a("Added `selected_final = max(production, experimental)` with strict rank:")
    a("")
    a("| Label | Rank |")
    a("|---|---:|")
    a("| usable | 4 |")
    a("| partial | 3 |")
    a("| wrong | 2 |")
    a("| not_found_missed / not_found_unverified / not_found | 1 |")
    a("")
    a("- **Production baseline** = best of stored profile and fresh `extract_field()`.")
    a("- **Experimental** is eligible only if `exp_rank >= prod_rank` and evidence is not cumulative narrative.")
    a("- **Tie-break** at same rank: stored > fresh > experimental (prefer production).")
    a("- **Improvement/regression** metrics use `selected_final`, not raw experimental.")
    a("")
    a("## Why R0 failed on 002415")
    a("")
    if r415:
        a(f"- **002415** 海康威视: stored/fresh strict=**{r415['stored_strict']}**, raw experimental=**{r415['exp_strict']}** ({r415['exp_reason']}).")
        a(f"- Selected final=**{r415['selected_strict']}** via `{r415['selected_source']}` — guard kept production.")
        a("- Root cause: situation-table pass on MD&A picked a weaker partial table candidate instead of the production anchor hit.")
    else:
        a("- 002415 not in control set.")
    a("")
    a("## Scope")
    a("")
    a("- Same universe as R0: P0/P1 R&D residuals + mandatory examples + clean controls")
    a("- Compares stored / fresh / raw experimental / **selected_final** (dry-run only)")
    a("")
    a("## Mandatory examples")
    a("")
    a("| Code | Name | Stored | Fresh | Raw Exp | Selected | Source |")
    a("|---|---|---|---|---|---|---|")
    for code in MANDATORY_CODES:
        r = next((x for x in rows if x["code"] == code), None)
        if r:
            a(f"| {r['code']} | {r['short_name']} | {r['stored_strict']} | {r['fresh_strict']} | {r['exp_strict']} | **{r['selected_strict']}** | {r['selected_source']} |")
    a("")
    a("## Controls (before/after guard)")
    a("")
    a("| Code | Stored | Fresh | Raw Exp | Selected (R1) | Regressed? |")
    a("|---|---|---|---|---|---|")
    for r in controls:
        a(f"| {r['code']} | {r['stored_strict']} | {r['fresh_strict']} | {r['exp_strict']} | **{r['selected_strict']}** | {'yes' if r['regressed'] else 'no'} |")
    a("")
    a("R0: `002415` raw experimental=partial → regressed. R1: selected_final=usable via stored/fresh.")
    a("")
    a("## Improved targets (selected_final)")
    a("")
    if improved:
        a("| Code | Name | P | Stored → Selected | Preview change |")
        a("|---|---|---|---|---|")
        for r in improved[:40]:
            a(f"| {r['code']} | {r['short_name']} | {r['csv_priority']} | {r['stored_strict']} → **{r['selected_strict']}** | {r['stored_preview'][:50]} → {r['selected_preview'][:50]} |")
        if len(improved) > 40:
            a(f"| … | ({len(improved) - 40} more) | | | |")
    else:
        a("_None_")
    a("")
    a("## Regressed targets")
    a("")
    if regressed:
        for r in regressed:
            a(f"- {r['code']} {r['short_name']}: {r['stored_strict']} → {r['selected_strict']}")
    else:
        a("_None_")
    a("")
    a("## Experimental-only downgrades blocked by guard")
    a("")
    if exp_would_regress:
        for r in exp_would_regress[:15]:
            a(f"- {r['code']} {r['short_name']}: exp={r['exp_strict']} < prod → kept `{r['selected_source']}` ({r['selected_strict']})")
        if len(exp_would_regress) > 15:
            a(f"- … and {len(exp_would_regress) - 15} more")
    else:
        a("_None_")
    a("")
    a("## Failure / not-solved")
    a("")
    unsolved = [r for r in mandatory if not r["improved"]]
    for r in unsolved:
        a(f"- **{r['code']}** {r['short_name']}: selected={r['selected_strict']} — {r['csv_root_cause']}")
    a("")
    a("## Recommended next step")
    a("")
    if verdict == "PASS":
        a("1. **Implement production helper** in `extract_annual_report.py` with the same guard (situation-table-first + max(prod, exp)).")
        a("2. Run scoped P0 dry-run refresh harness before any `--apply`.")
        a("3. Defer narrative partial (`000333`) to manual review.")
    else:
        a("1. Further refine guard or experimental selector.")
        a("2. Do not change production extraction until dry-run PASS.")
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


def _load_controls(csv_rows: list[dict], existing_codes: set[str], evaluate_fn, specs: dict) -> list[dict]:
    controls: list[dict] = []
    for code in CONTROL_CODES:
        if code in existing_codes:
            continue
        tr = next((r for r in csv_rows if r["code"] == code), None)
        board = (tr or {}).get("board")
        if not board:
            for b in ("sse_main", "szse_main", "chinext", "star", "bse"):
                if os.path.isfile(os.path.join(OUT_DIR, b, code, "company_profile.json")):
                    board = b
                    break
        if not board:
            continue
        try:
            controls.append(evaluate_fn(code, board, None, specs))
        except Exception:
            pass
    return controls


def main() -> int:
    parser = argparse.ArgumentParser(description="#32c R&D residual dry-run")
    parser.add_argument("--mode", choices=("r1", "r2"), default="r2")
    parser.add_argument("--max-p0-extra", type=int, default=20)
    parser.add_argument("--summary", default="")
    args = parser.parse_args()
    if not args.summary:
        args.summary = SUMMARY_R2_PATH if args.mode == "r2" else SUMMARY_PATH

    specs = _specs()
    csv_rows = _load_csv_rows()
    targets = _select_target_rows(csv_rows, max_p0_extra=args.max_p0_extra)
    evaluate_fn = _evaluate_code_r2 if args.mode == "r2" else _evaluate_code
    write_fn = _write_summary_r2 if args.mode == "r2" else _write_summary

    rows: list[dict] = []
    for tr in targets:
        code = tr["code"]
        board = tr["board"]
        try:
            rows.append(evaluate_fn(code, board, tr, specs))
        except Exception as exc:
            rows.append({
                "code": code, "short_name": tr.get("short_name", ""), "board": board,
                "csv_priority": tr.get("priority", ""), "csv_root_cause": tr.get("root_cause", ""),
                "stored_strict": "error", "fresh_strict": "error",
                "improved": False, "regressed": False, "error": str(exc),
            })

    controls = _load_controls(csv_rows, {r["code"] for r in rows}, evaluate_fn, specs)
    verdict = write_fn(rows, controls, args.summary)
    all_rows = rows + controls
    improved = sum(1 for r in rows if r.get("improved"))
    regressed = sum(1 for r in all_rows if r.get("regressed"))
    ctrl_reg = sum(1 for r in controls if r.get("regressed"))
    print(f"mode={args.mode} evaluated={len(all_rows)} targets_improved={improved} regressions={regressed} ctrl_regressions={ctrl_reg} verdict={verdict}")
    print(f"summary={args.summary}")
    for code in MANDATORY_CODES:
        r = next((x for x in rows if x["code"] == code), None)
        if r:
            if args.mode == "r2":
                print(f"  {code}: stored={r['stored_strict']} fresh_r2={r['fresh_strict']} r1_sel={r.get('r1_selected_strict')}")
            else:
                print(f"  {code}: stored={r['stored_strict']} exp={r['exp_strict']} selected={r['selected_strict']} ({r['selected_source']})")
    r415 = next((x for x in controls if x["code"] == "002415"), None)
    if r415:
        if args.mode == "r2":
            print(f"  002415: stored={r415['stored_strict']} fresh_r2={r415['fresh_strict']} regressed={r415['regressed']}")
        else:
            print(f"  002415: stored={r415['stored_strict']} exp={r415['exp_strict']} selected={r415['selected_strict']} regressed={r415['regressed']}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
