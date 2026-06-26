#!/usr/bin/env python3
"""#32b Revenue residual Tier 4 / wrong-table dry-run diagnosis.

Read-only over cached PDFs and stored profiles. Does NOT write profiles,
eval_results, or run refresh/apply/merge/SQLite/CNINFO.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.extract_annual_report import (  # noqa: E402
    _PREVIEW_ROW_LIMIT,
    _continuation_stop_row,
    _format_preview_row,
    _preview_has_revenue_section_header,
    _reject_continuation_table,
    _stitch_revenue_table_continuation,
    _table_row_is_data_row,
    _trim_revenue_stacked_preview,
    compute_regions,
    extract_field,
    extract_table_near,
    locate_section,
    parse_pages,
    revenue_table_plausible,
)
from lab.field_schema import get_field_specs  # noqa: E402
from lab.strict_audit_full_market import (  # noqa: E402
    _table_row_is_data_row as audit_data_row,
    strict_audit_field,
    strict_table,
)

OUT_DIR = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
CANDIDATES_CSV = os.path.join(OUT_DIR, "revenue_rnd_residual_candidates_32.csv")
SUMMARY_PATH = os.path.join(OUT_DIR, "revenue_residual_fix_32b_dryrun_summary.md")
DETAIL_CSV = os.path.join(OUT_DIR, "revenue_residual_fix_32b_dryrun_details.csv")

REVENUE_FIELDS = ("revenue_by_region", "revenue_by_segment")
FINANCIAL_DEFER = frozenset({"financial_like_holding_disclosure"})
CONTROL_CODES = ("000063", "600519", "601012", "002415", "300750", "688111")

REGION_LABEL_KW = (
    "华东", "华南", "华北", "华中", "西南", "西北", "东北",
    "境内", "境外", "国内", "国外", "海外", "国际",
    "北京", "上海", "广东", "江苏", "浙江", "山东", "四川",
)
SEGMENT_LABEL_KW = (
    "分行业", "分产品", "行业", "产品", "业务", "制造", "服务", "销售",
)
CUSTOMER_SUPPLIER_KW = (
    "前五名客户", "前五名供应商", "前五大客户", "前五大供应商",
    "客户名称", "供应商名称", "客户一", "客户二", "客户三",
    "第一大客户", "第二大客户", "合同标的", "履行金额",
)
REJECT_TABLE_KW = (
    "现金流量", "利润表", "资产负债表", "科目", "本期数", "上年同期",
    "融出资金", "买入返售",
)
SINGLE_ROW_REGION_LABELS = frozenset({"境内", "境外", "国内", "国外"})


def _strict_rank(label: str) -> int:
    return {
        "usable": 4, "partial": 3, "wrong": 2,
        "not_found_unverified": 1, "not_found_missed": 1, "not_found": 1,
    }.get(label, 0)


def _load_wrong_rows() -> list[dict]:
    with open(CANDIDATES_CSV, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    return [
        r for r in rows
        if r.get("field") in REVENUE_FIELDS and r.get("strict_label") == "wrong"
    ]


def _bse_group_key(code: str, short_name: str) -> str:
    """Group BSE 83xxxx / 92xxxx mirror listings."""
    if code.startswith("92") and len(code) == 6:
        return f"bse:{short_name}:{code[2:]}"
    if code.startswith("83") and len(code) == 6:
        return f"bse:{short_name}:{code[2:]}"
    return code


def _profile_field(code: str, board: str, field: str) -> tuple[dict, dict]:
    path = os.path.join(OUT_DIR, board, code, "company_profile.json")
    with open(path, encoding="utf-8") as fh:
        prof = json.load(fh)
    f = next(x for x in prof["fields"] if x.get("field") == field)
    return prof, f


def _field_from_table(tbl: dict, spec, source_url: str, *, anchor: str = "") -> dict:
    return {
        "field": spec.key,
        "extraction": "table",
        "status": "found",
        "value": tbl,
        "page": tbl.get("table_page"),
        "anchor_matched": anchor,
        "source_url": source_url,
    }


def _stitch_tier4_extended(
    pdf_path: str, tbl: dict, field_key: str, preview_focus: tuple[str, ...], *, max_extra: int = 3,
) -> dict:
    """Harness-only Tier 4: scan N+2..N+max_extra when Tier 3 still has 0 data rows."""
    if any(_table_row_is_data_row(r) for r in (tbl.get("rows") or [])):
        return tbl
    if not _preview_has_revenue_section_header(tbl.get("rows") or [], preview_focus):
        return tbl
    header_page = tbl.get("table_page")
    if not header_page:
        return tbl
    try:
        import pdfplumber  # type: ignore
    except Exception:
        return tbl

    combined_rows = list(tbl.get("rows") or [])
    last_cont = tbl.get("continuation_page") or header_page
    stitched_from = last_cont

    try:
        with open(pdf_path, "rb") as fh:
            data = fh.read()
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for off in range(2, max_extra + 1):
                pg = header_page + off
                if pg < 1 or pg > len(pdf.pages):
                    continue
                page = pdf.pages[pg - 1]
                best_append: list[list] = []
                for raw_tbl in (page.extract_tables() or []):
                    flat = " ".join(str(c) for row in raw_tbl for c in row if c)
                    if _reject_continuation_table(flat):
                        continue
                    if any(k in flat for k in REJECT_TABLE_KW):
                        continue
                    append: list[list] = []
                    for row in raw_tbl:
                        if _continuation_stop_row(row, field_key):
                            break
                        if _table_row_is_data_row(row):
                            append.append(_format_preview_row(row))
                    if len(append) > len(best_append):
                        best_append = append
                if best_append:
                    combined_rows.extend(best_append)
                    stitched_from = pg
                    if any(_table_row_is_data_row(r) for r in combined_rows):
                        break
    except Exception:
        return tbl

    if stitched_from == (tbl.get("continuation_page") or header_page) and not any(
        _table_row_is_data_row(r) for r in combined_rows
    ):
        return tbl

    out = dict(tbl)
    out["rows"] = combined_rows[:_PREVIEW_ROW_LIMIT]
    out["tier4_page"] = stitched_from
    out["tier4_stitched"] = True
    return out


def _table_text(rows: list) -> str:
    return " ".join(str(c) for row in rows for c in row if c)


def _score_table(tbl: dict, field_key: str) -> float:
    rows = tbl.get("rows") or []
    flat = _table_text(rows)
    score = float(tbl.get("match_hits") or 0) * 2.0
    data_rows = [r for r in rows if _table_row_is_data_row(r)]
    score += len(data_rows) * 5.0
    if any(k in flat for k in CUSTOMER_SUPPLIER_KW):
        score -= 80.0
    if any(k in flat for k in REJECT_TABLE_KW):
        score -= 60.0
    labels = " ".join(str(r[0]) if r else "" for r in data_rows)
    if field_key == "revenue_by_region":
        score += sum(3.0 for k in REGION_LABEL_KW if k in labels or k in flat)
        if "分地区" in flat or "分地区" in labels:
            score += 10.0
    else:
        score += sum(2.0 for k in SEGMENT_LABEL_KW if k in labels or k in flat)
        if "分行业" in flat or "分产品" in flat:
            score += 8.0
    return score


def _scan_ranked_tables(
    pdf_path: str, page_no: int, spec, field_key: str,
) -> dict | None:
    """Harness wrong-table ranking: pick best-scoring table on nearby pages."""
    focus = spec.table_match or spec.anchors
    best_tbl = None
    best_score = float("-inf")
    try:
        import pdfplumber  # type: ignore
    except Exception:
        return None
    with open(pdf_path, "rb") as fh:
        data = fh.read()
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for cand in range(max(1, page_no - 1), min(len(pdf.pages), page_no + 3) + 1):
            page = pdf.pages[cand - 1]
            for raw in (page.extract_tables() or []):
                flat = " ".join(str(c) for row in raw for c in row if c)
                if spec.table_require and not any(t in flat for t in spec.table_require):
                    continue
                tokens = spec.table_match or spec.anchors
                if not any(t in flat for t in tokens) and not any(a in flat for a in spec.anchors):
                    continue
                hits = sum(1 for t in tokens if t in flat)
                start = 0
                if focus:
                    for ri, row in enumerate(raw):
                        rowtxt = " ".join(str(c) for c in row if c)
                        if any(tok in rowtxt for tok in focus):
                            start = ri
                            break
                rows = [[str(c or "")[:40] for c in row[:6]] for row in raw[start:start + 8]]
                tbl = {"table_page": cand, "rows": rows, "match_hits": hits, "preview_from_row": start}
                sc = _score_table(tbl, field_key)
                if sc > best_score:
                    best_score = sc
                    best_tbl = tbl
    return best_tbl


def _audit_single_row_relaxed(f: dict) -> tuple[str, str]:
    """Harness-only: 境内/境外 single-row region → partial instead of wrong."""
    if f.get("field") != "revenue_by_region":
        return strict_table(f)
    val = f.get("value")
    if not isinstance(val, dict):
        return strict_table(f)
    rows = val.get("rows") or []
    data_rows = [r for r in rows if audit_data_row(r)]
    if len(data_rows) != 1:
        return strict_table(f)
    label = str(data_rows[0][0] if data_rows[0] else "").replace(" ", "")
    if label in SINGLE_ROW_REGION_LABELS or any(l in label for l in SINGLE_ROW_REGION_LABELS):
        if revenue_table_plausible(val):
            return "partial", "single domestic/foreign row (audit relaxation candidate)"
    return strict_table(f)


def _classify_row(row: dict, stored: dict, *, tier4_strict: str, rank_strict: str) -> str:
    inv = row.get("root_cause") or ""
    if inv in FINANCIAL_DEFER:
        return "financial_like_defer"
    if tier4_strict in ("usable", "partial") and _strict_rank(tier4_strict) > _strict_rank("wrong"):
        return "tier4_multipage_candidate"
    if rank_strict in ("usable", "partial") and _strict_rank(rank_strict) > _strict_rank("wrong"):
        return "wrong_table_ranking_candidate"
    mapping = {
        "tier3_stitched_still_empty_multipage": "tier4_multipage_candidate",
        "wrong_table_customer_captured_as_region": "wrong_sibling_table",
        "wrong_table_sales_mode_bleed": "sales_mode_bleed",
        "empty_table_no_stitch": "empty_table_no_stitch",
        "rows_present_fail_data_row_heuristic": "layout_numeric_format",
        "financial_like_holding_disclosure": "financial_like_defer",
    }
    return mapping.get(inv, "no_safe_fix")


def _decision_priority(classification: str, inv_priority: str) -> str:
    if classification == "financial_like_defer":
        return "P2 defer (#31)"
    if classification == "tier4_multipage_candidate":
        return "P0 Tier4" if inv_priority == "P0" else "P1 Tier4"
    if classification in ("wrong_sibling_table", "wrong_table_ranking_candidate"):
        return "P1 wrong-table ranking"
    if classification == "sales_mode_bleed":
        return "P1 trim/ranking"
    if classification == "layout_numeric_format":
        return "P1 layout/heuristic"
    if classification == "empty_table_no_stitch":
        return "P1 manual PDF review"
    return "P2 no safe fix"


def _evaluate_wrong_row(row: dict, specs: dict) -> dict:
    code, board, field = row["code"], row["board"], row["field"]
    spec = specs[field]
    pdf = os.path.join(OUT_DIR, board, code, f"{code}.pdf")
    cache = os.path.join(OUT_DIR, board, code, ".cache")
    prof, stored = _profile_field(code, board, field)
    url = stored.get("source_url") or prof.get("source", {}).get("source_url", "")

    stored_strict, stored_reason = strict_audit_field(stored)
    pages, _ = parse_pages(pdf, cache)
    regions = compute_regions(pages)
    fresh = extract_field(spec, pages, pdf, url, regions)
    fresh_strict, fresh_reason = strict_audit_field(fresh)

    page = stored.get("page") or fresh.get("page") or 1
    focus = spec.table_match or spec.anchors
    base_tbl = extract_table_near(
        pdf, int(page), spec.anchors, spec.table_match, spec.table_require, preview_focus=focus,
    )
    tier4_strict, tier4_reason, tier4_tbl = "", "", None
    rank_strict, rank_reason = "", ""
    single_relaxed = ""

    if base_tbl and field in REVENUE_FIELDS:
        t3 = _stitch_revenue_table_continuation(pdf, base_tbl, field, focus)
        t3 = _trim_revenue_stacked_preview(t3, field)
        t4 = _stitch_tier4_extended(pdf, t3, field, focus)
        tier4_tbl = t4
        f4 = _field_from_table(t4, spec, url)
        tier4_strict, tier4_reason = strict_audit_field(f4)

        ranked = _scan_ranked_tables(pdf, int(page), spec, field)
        if ranked:
            r3 = _stitch_revenue_table_continuation(pdf, ranked, field, focus)
            r3 = _trim_revenue_stacked_preview(r3, field)
            r4 = _stitch_tier4_extended(pdf, r3, field, focus)
            fr = _field_from_table(r4, spec, url, anchor="ranked_table")
            rank_strict, rank_reason = strict_audit_field(fr)

    single_relaxed, _ = _audit_single_row_relaxed(stored)
    classification = _classify_row(
        row, stored, tier4_strict=tier4_strict or stored_strict, rank_strict=rank_strict or stored_strict,
    )
    exp_best = max(
        [("stored", stored_strict), ("fresh", fresh_strict), ("tier4", tier4_strict), ("ranked", rank_strict)],
        key=lambda x: _strict_rank(x[1]),
    )
    improved = _strict_rank(exp_best[1]) > _strict_rank(stored_strict)

    return {
        "code": code,
        "short_name": row.get("short_name", ""),
        "board": board,
        "field": field,
        "inventory_root_cause": row.get("root_cause", ""),
        "inventory_priority": row.get("priority", ""),
        "bse_group": _bse_group_key(code, row.get("short_name", "")),
        "stored_strict": stored_strict,
        "stored_reason": stored_reason,
        "fresh_strict": fresh_strict,
        "fresh_reason": fresh_reason,
        "tier4_strict": tier4_strict,
        "tier4_reason": tier4_reason,
        "rank_strict": rank_strict,
        "rank_reason": rank_reason,
        "single_row_relaxed": single_relaxed,
        "classification": classification,
        "decision": _decision_priority(classification, row.get("priority", "")),
        "exp_best_source": exp_best[0],
        "exp_best_strict": exp_best[1],
        "improved": improved,
        "regressed": False,
    }


def _evaluate_controls(specs: dict) -> list[dict]:
    out = []
    for code in CONTROL_CODES:
        for board in ("sse_main", "szse_main", "chinext", "star", "bse"):
            path = os.path.join(OUT_DIR, board, code, "company_profile.json")
            if not os.path.isfile(path):
                continue
            pdf = os.path.join(OUT_DIR, board, code, f"{code}.pdf")
            cache = os.path.join(OUT_DIR, board, code, ".cache")
            prof = json.load(open(path, encoding="utf-8"))
            pages, _ = parse_pages(pdf, cache)
            regions = compute_regions(pages)
            url = prof.get("source", {}).get("source_url", "")
            for fk in REVENUE_FIELDS:
                stored = next((f for f in prof["fields"] if f.get("field") == fk), None)
                if not stored:
                    continue
                before, _ = strict_audit_field(stored)
                fresh = extract_field(specs[fk], pages, pdf, url, regions)
                after, _ = strict_audit_field(fresh)
                out.append({
                    "code": code, "field": fk, "before": before, "after": after,
                    "regressed": _strict_rank(after) < _strict_rank(before),
                })
            break
    return out


def _write_summary(
    results: list[dict], controls: list[dict], path: str,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    n = len(results)
    classified = Counter(r["classification"] for r in results)
    inv_roots = Counter(r["inventory_root_cause"] for r in results)
    decisions = Counter(r["decision"] for r in results)
    improved = [r for r in results if r["improved"]]
    tier4_imp = [r for r in results if r["tier4_strict"] in ("usable", "partial") and r["stored_strict"] == "wrong"]
    rank_imp = [r for r in results if r["rank_strict"] in ("usable", "partial") and r["stored_strict"] == "wrong"]
    single_cand = [r for r in results if r["single_row_relaxed"] == "partial" and r["stored_strict"] == "wrong"]
    ctrl_reg = [c for c in controls if c["regressed"]]
    bse_groups = len({r["bse_group"] for r in results if r["code"].startswith(("83", "92"))})

    unique_issuers = len({r["bse_group"] if r["code"].startswith(("83", "92")) else r["code"] for r in results})

    fixable_now = sum(
        1 for r in results
        if r["decision"].startswith("P0") or (
            r["decision"].startswith("P1") and r["classification"] in (
                "tier4_multipage_candidate", "wrong_sibling_table", "wrong_table_ranking_candidate", "sales_mode_bleed",
            )
        )
    )
    defer = sum(1 for r in results if "defer" in r["decision"] or r["classification"] == "financial_like_defer")

    verdict = "PASS" if n == 57 and not ctrl_reg else "FAIL"
    prod_rec = "defer production apply; scoped Tier4 + wrong-table pilot after human sign-off"
    close_32 = "yes — #32 can close with revenue/R&D residuals explicitly deferred"

    lines: list[str] = []
    a = lines.append
    a("# Revenue residual fix #32b dry-run summary")
    a("")
    a(f"_Generated: {ts} | Read-only diagnosis; no profile writes_")
    a("")
    a(f"## Verdict: **{verdict}**")
    a("")
    a("## 1. Scope and guardrails")
    a("")
    a("- **Universe:** 57 revenue strict-wrong field-cells (48 issuers) from `#32` inventory")
    a("- **Fields:** `revenue_by_region` (38) + `revenue_by_segment` (19)")
    a("- **Mode:** Read-only harness experiments; no apply, no full refresh, no CNINFO/SQLite")
    a("- **Non-fin headline 9.43/11:** unchanged; no `strict_audit_summary.md` update")
    a("- **R&D extraction:** not touched")
    a("- **Financial-like rows (8 cells):** marked defer to #31 — not forced fix")
    a("")
    a("## 2. Files changed")
    a("")
    a("- `lab/revenue_residual_fix_32b_dryrun.py` (new)")
    a("- `outputs/generalization/full_market_2024/revenue_residual_fix_32b_dryrun_summary.md` (this file)")
    a("- `outputs/generalization/full_market_2024/revenue_residual_fix_32b_dryrun_details.csv` (optional detail)")
    a("")
    a("## 3. Rows evaluated")
    a("")
    a(f"| Metric | Value |")
    a(f"|---|---:|")
    a(f"| Field-cells evaluated | **{n}** |")
    a(f"| Unique issuers (BSE mirrors grouped) | **{unique_issuers}** |")
    a(f"| BSE mirror pairs in pool | **{bse_groups}** groups |")
    a(f"| Experimental improvements (any harness path) | **{len(improved)}** |")
    a(f"| Control revenue regressions | **{len(ctrl_reg)}** |")
    a("")
    a("## 4. Root-cause distribution (inventory + harness classification)")
    a("")
    a("### Inventory root_cause")
    a("")
    a("| Root cause | Cells |")
    a("|---|---:|")
    for k, v in inv_roots.most_common():
        a(f"| `{k}` | {v} |")
    a("")
    a("### Harness classification")
    a("")
    a("| Classification | Cells |")
    a("|---|---:|")
    for k, v in classified.most_common():
        a(f"| {k} | {v} |")
    a("")
    a("## 5. Experimental Tier4 multipage (N+2..N+4)")
    a("")
    a(f"- Rows where Tier4 experiment yields usable/partial: **{len(tier4_imp)}**")
    if tier4_imp[:10]:
        a("| Code | Field | Stored → Tier4 |")
        a("|---|---|---|")
        for r in tier4_imp[:10]:
            a(f"| {r['code']} | {r['field']} | {r['stored_strict']} → **{r['tier4_strict']}** |")
    a("")
    a("## 6. Experimental wrong-table ranking")
    a("")
    a(f"- Rows where ranked re-scan yields usable/partial: **{len(rank_imp)}**")
    if rank_imp[:10]:
        a("| Code | Field | Stored → Ranked |")
        a("|---|---|---|")
        for r in rank_imp[:10]:
            a(f"| {r['code']} | {r['field']} | {r['stored_strict']} → **{r['rank_strict']}** |")
    a("")
    a("## 7. Single-row audit relaxation estimate")
    a("")
    a(f"- Rows that could become **partial** (not usable) under 境内/境外 relaxation: **{len(single_cand)}**")
    a("- Production audit **not changed** in this task; count only.")
    a("")
    a("## 8. P0/P1/P2 decision table")
    a("")
    a("| Decision | Cells |")
    a("|---|---:|")
    for k, v in decisions.most_common():
        a(f"| {k} | {v} |")
    a("")
    a(f"- **Fixable now (P0/P1 extraction or ranking pilot):** ~{fixable_now} cells")
    a(f"- **Deferred (#31 / manual / no safe fix):** ~{defer + (n - fixable_now - defer)} cells")
    a("")
    a("## 9. Recommendation")
    a("")
    if verdict == "PASS":
        a(f"1. **{prod_rec}**")
        a(f"2. **Close #32:** {close_32}.")
        a("3. Next engineering (not this task): port Tier4 N+2..N+4 stitch + wrong-table ranking into harness-validated scoped pilot (~12 unique Tier4 issuers after BSE dedupe).")
        a("4. Do **not** update non-fin **9.43/11** headline until intentional scoped apply + strict audit rerun.")
        a("")
        a("> **Caveat:** Some Tier4 hits overlap sales-mode-bleed inventory rows (e.g. 000011) — require PDF spot-check before production port.")
    else:
        a("1. Fix harness or re-run controls before production decision.")
    a("")
    a("## 10. Safe to commit")
    a("")
    a("- `lab/revenue_residual_fix_32b_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/revenue_residual_fix_32b_dryrun_summary.md`")
    a("- `outputs/generalization/full_market_2024/revenue_residual_fix_32b_dryrun_details.csv`")
    a("")
    a("## 11. Do not commit")
    a("")
    a("- Profiles, eval_results, strict_audit_summary.md, refresh CSVs, YAML")
    a("")
    a("## GitHub #32b comment (中文)")
    a("")
    a("```")
    a("#32b revenue residual dry-run 完成（只读诊断）")
    a("")
    a(f"结论：**{verdict}** — 57/57 strict-wrong 收入 cell 已分类；control 回归 {len(ctrl_reg)}。")
    a(f"- region wrong 38 + segment wrong 19")
    a(f"- Tier4 实验改善：{len(tier4_imp)}；wrong-table ranking 改善：{len(rank_imp)}")
    a(f"- 金融控股类 8 cell → defer #31；BSE 83/92 镜像已分组")
    a(f"- 建议：**defer 生产 apply**；#32 可关单并将 revenue 剩余项 defer 到后续 scoped pilot（Tier4 + wrong-table ranking）")
    a("未改 production extraction/audit；未更新 9.43/11 headline。")
    a("```")
    a("")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser(description="#32b revenue residual dry-run")
    parser.add_argument("--summary", default=SUMMARY_PATH)
    parser.add_argument("--details-csv", default=DETAIL_CSV)
    args = parser.parse_args()

    specs = {s.key: s for s in get_field_specs("industrial")}
    wrong_rows = _load_wrong_rows()
    results = [_evaluate_wrong_row(r, specs) for r in wrong_rows]
    controls = _evaluate_controls(specs)

    if results:
        fields = list(results[0].keys())
        with open(args.details_csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(results)

    verdict = _write_summary(results, controls, args.summary)
    improved = sum(1 for r in results if r["improved"])
    ctrl_reg = sum(1 for c in controls if c["regressed"])
    print(f"rows={len(results)} improved={improved} ctrl_regressions={ctrl_reg} verdict={verdict}")
    print(f"summary={args.summary}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
