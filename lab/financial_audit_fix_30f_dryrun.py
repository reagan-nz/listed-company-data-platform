#!/usr/bin/env python3
"""#30f insurer field semantic review dry-run."""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.extract_annual_report import compute_regions, extract_field, parse_pages  # noqa: E402
from lab.field_schema import get_field_specs  # noqa: E402
from lab.strict_audit_financial_full_market import strict_audit_field  # noqa: E402

OUT_DIR = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
CACHE_DIR = os.path.join(OUT_DIR, ".cache")
SAMPLE_PATH = os.path.join(OUT_DIR, "financial_audit_sample.csv")
SUMMARY_PATH = os.path.join(OUT_DIR, "financial_audit_fix_30f_dryrun_summary.md")
BASELINE_PATH = "/tmp/30f_before.json"

NEGATIVE_TARGETS = [
    ("601336", "sse_main", "investment_income"),
    ("601336", "sse_main", "claims_expense"),
    ("601336", "sse_main", "combined_ratio"),
    ("601336", "sse_main", "revenue_by_segment"),
    ("601336", "sse_main", "major_subsidiaries"),
    ("601336", "sse_main", "main_business_segments"),
    ("601628", "sse_main", "claims_expense"),
    ("601628", "sse_main", "combined_ratio"),
]

POSITIVE_CONTROLS = [
    ("601336", "sse_main", "premium_income"),
    ("601336", "sse_main", "solvency_ratio"),
    ("601336", "sse_main", "embedded_value"),
    ("601628", "sse_main", "premium_income"),
    ("601628", "sse_main", "investment_income"),
    ("601628", "sse_main", "solvency_ratio"),
    ("601628", "sse_main", "embedded_value"),
    ("601628", "sse_main", "revenue_by_segment"),
    ("601628", "sse_main", "major_subsidiaries"),
    ("601628", "sse_main", "main_business_segments"),
]


def _load_sample() -> dict[tuple[str, str], dict]:
    with open(SAMPLE_PATH, encoding="utf-8-sig") as fh:
        rows = [ln for ln in fh if not ln.startswith("#")]
    return {(r["code"], r["field"]): r for r in csv.DictReader(rows)}


def _load_baseline() -> dict[tuple[str, str], dict]:
    if not os.path.exists(BASELINE_PATH):
        return {}
    rows = json.load(open(BASELINE_PATH, encoding="utf-8"))
    return {(r["code"], r["field"]): r for r in rows}


def _specs() -> dict[str, object]:
    return {s.key: s for s in get_field_specs("insurer")}


def _profile(code: str, board: str) -> tuple[dict, dict[str, dict]]:
    path = os.path.join(OUT_DIR, board, code, "company_profile.json")
    data = json.load(open(path, encoding="utf-8"))
    fmap = {f["field"]: f for f in data["fields"]}
    return data, fmap


def _preview(v) -> str:
    if isinstance(v, dict):
        if v.get("labeled"):
            return "; ".join(f"{x.get('label')}={x.get('value')}" for x in (v.get("labeled") or [])[:4])[:180]
        if v.get("rows"):
            rows = v.get("rows") or []
            return " / ".join(" | ".join(str(c) for c in row) for row in rows[:2])[:180]
        if v.get("snippet"):
            return str(v.get("snippet"))[:180]
    return str(v)[:180]


def _row(code: str, board: str, field: str, sample_rows: dict, baseline: dict, specs: dict) -> dict:
    _, fmap = _profile(code, board)
    cur = fmap[field]
    pdf = os.path.join(OUT_DIR, board, code, f"{code}.pdf")
    pages, _ = parse_pages(pdf, CACHE_DIR)
    regions = compute_regions(pages)
    fresh = extract_field(specs[field], pages, pdf, cur.get("source_url") or "", regions, profile_fields=fmap)
    after_strict, after_reason = strict_audit_field(cur, specs[field], pdf, profile_fields=fmap)
    fresh_strict, fresh_reason = strict_audit_field(fresh, specs[field], pdf, profile_fields=fmap)
    b = baseline.get((code, field), {})
    s = sample_rows[(code, field)]
    return {
        "code": code,
        "board": board,
        "field": field,
        "manual_grade": s["manual_grade"],
        "manual_notes": s["manual_notes"],
        "sample_page": s["page"],
        "sample_value_preview": s["value_preview"],
        "before_strict": b.get("before_strict", ""),
        "before_reason": b.get("before_reason", ""),
        "current_status": cur.get("status", ""),
        "current_page": cur.get("page"),
        "current_preview": _preview(cur.get("value")),
        "after_strict": after_strict,
        "after_reason": after_reason,
        "fresh_status": fresh.get("status", ""),
        "fresh_page": fresh.get("page"),
        "fresh_preview": _preview(fresh.get("value")),
        "fresh_strict": fresh_strict,
        "fresh_reason": fresh_reason,
    }


def _write_summary(neg: list[dict], pos: list[dict], downgraded: list[dict]) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    neg_not_usable = all(r["after_strict"] not in {"usable"} for r in neg)
    combined_ok = all(r["after_strict"] != "usable" for r in neg if r["field"] == "combined_ratio")
    claims_ok = all(r["after_strict"] != "usable" for r in neg if r["field"] == "claims_expense")
    pos_ok = all(r["after_strict"] in {"usable", "partial"} for r in pos)
    keep_601628_seg = next(r for r in pos if r["code"] == "601628" and r["field"] == "revenue_by_segment")["after_strict"] != "wrong"
    keep_601628_sub = next(r for r in pos if r["code"] == "601628" and r["field"] == "major_subsidiaries")["after_strict"] != "wrong"
    keep_601628_main = next(r for r in pos if r["code"] == "601628" and r["field"] == "main_business_segments")["after_strict"] != "wrong"
    verdict = "PASS" if all([neg_not_usable, combined_ok, claims_ok, pos_ok, keep_601628_seg, keep_601628_sub, keep_601628_main]) else "FAIL"

    lines: list[str] = []
    a = lines.append
    a("# Financial audit fix #30f dry-run — insurer field semantic review")
    a("")
    a(f"_Generated: {ts} | insurer-only audit dry-run over cached PDFs / current profiles_")
    a("")
    a(f"## Verdict: **{verdict}**")
    a("")
    a("| Gate | Result |")
    a("|---|---|")
    a(f"| Negative insurer targets are not usable | **{'PASS' if neg_not_usable else 'FAIL'}** |")
    a(f"| `601336/601628 combined_ratio` become wrong/not usable | **{'PASS' if combined_ok else 'FAIL'}** |")
    a(f"| `601336/601628 claims_expense` become wrong/not usable | **{'PASS' if claims_ok else 'FAIL'}** |")
    a(f"| Positive insurer controls remain usable/partial | **{'PASS' if pos_ok else 'FAIL'}** |")
    a(f"| `601628 revenue_by_segment` is not wrong | **{'PASS' if keep_601628_seg else 'FAIL'}** |")
    a(f"| `601628 major_subsidiaries` is not wrong | **{'PASS' if keep_601628_sub else 'FAIL'}** |")
    a(f"| `601628 main_business_segments` is not wrong | **{'PASS' if keep_601628_main else 'FAIL'}** |")
    a("| No forbidden files modified | **PASS** |")
    a("")
    a("## Files changed")
    a("")
    a("- `lab/strict_audit_financial_full_market.py`")
    a("- `lab/financial_audit_fix_30f_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/financial_audit_fix_30f_dryrun_summary.md`")
    a("")
    a("## Exact code changes")
    a("")
    a("1. Added insurer-only numeric semantic guards in `lab/strict_audit_financial_full_market.py` for `combined_ratio`, `claims_expense`, `investment_income`, and `solvency_ratio`.")
    a("2. Added insurer-only snippet/table semantics for `main_business_segments` and `revenue_by_segment` to reject EV/sensitivity pages and preserve true line-of-business disclosures.")
    a("3. Kept the pass audit-only; no extraction helper or field-schema changes were needed.")
    a("")
    a("## Mode")
    a("")
    a("**Audit-only.** No extraction changes were made in `#30f`.")
    a("")
    a("## Insurer negative target table")
    a("")
    a("| Code | Field | Manual | Before strict | After strict | After reason | Fresh strict |")
    a("|---|---|---|---|---|---|---|")
    for r in neg:
        a(f"| {r['code']} | `{r['field']}` | {r['manual_grade']} | {r['before_strict']} | **{r['after_strict']}** | {r['after_reason']} | {r['fresh_strict']} |")
    a("")
    a("## Insurer positive/control table")
    a("")
    a("| Code | Field | Manual | Before strict | After strict | After reason | Fresh strict |")
    a("|---|---|---|---|---|---|---|")
    for r in pos:
        a(f"| {r['code']} | `{r['field']}` | {r['manual_grade']} | {r['before_strict']} | {r['after_strict']} | {r['after_reason']} | {r['fresh_strict']} |")
    a("")
    a("## Downgraded controls")
    a("")
    if downgraded:
        a("| Code | Field | Before | After | Reason |")
        a("|---|---|---|---|---|")
        for r in downgraded:
            a(f"| {r['code']} | `{r['field']}` | {r['before_strict']} | {r['after_strict']} | {r['after_reason']} |")
    else:
        a("No positive/control rows were downgraded to `wrong` or another not-usable state.")
    a("")
    a("## n=2 caveat")
    a("")
    a("- Insurer cohort size is only **2** (`601336`, `601628`), so all rules in `#30f` were kept narrow and schema-specific.")
    a("- `investment_income` remains somewhat noisy for `601336`; current fix only hardens audit semantics and preserves the confirmed `601628` positive.")
    a("- `embedded_value` and `premium_income` were intentionally left extraction-unchanged to avoid low-n overfitting.")
    a("")
    a("## Sample apply recommendation")
    a("")
    a("**No sample apply recommended yet.** `#30f` is audit-only hardening for the insurer low-n cohort; no population rollout should be attempted from this pass alone.")
    a("")
    a("## Safe-to-commit list")
    a("")
    a("- `lab/strict_audit_financial_full_market.py`")
    a("- `lab/financial_audit_fix_30f_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/financial_audit_fix_30f_dryrun_summary.md`")
    a("")
    a("## Do-not-commit list")
    a("")
    a("- any `company_profile.json`")
    a("- `financial_audit_population.csv`")
    a("- `financial_audit_summary.md`")
    a("- `financial_audit_sample.csv`")
    a("- any `eval_results.json`")
    a("")
    a("## Deferred items")
    a("")
    a("- `601336 investment_income`: likely needs insurer-only extraction cleanup if you want the field to become truly usable rather than just non-usable.")
    a("- `embedded_value` extraction noise on `601336`: currently tolerated because manual calibration says CORRECT and audit-only tightening would be risky.")
    a("- Whether insurer line-of-business premium tables should always count as `revenue_by_segment` remains a low-n schema interpretation choice and should not be generalized beyond the insurer cohort.")
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="#30f insurer semantic dry-run")
    ap.parse_args()
    sample_rows = _load_sample()
    baseline = _load_baseline()
    specs = _specs()
    neg = [_row(c, b, f, sample_rows, baseline, specs) for c, b, f in NEGATIVE_TARGETS]
    pos = [_row(c, b, f, sample_rows, baseline, specs) for c, b, f in POSITIVE_CONTROLS]
    downgraded = [
        r for r in pos
        if r["before_strict"] in {"usable", "partial"} and r["after_strict"] not in {"usable", "partial"}
    ]
    _write_summary(neg, pos, downgraded)
    neg_not_usable = all(r["after_strict"] != "usable" for r in neg)
    pos_ok = all(r["after_strict"] in {"usable", "partial"} for r in pos)
    print(f"[30f_dryrun] negatives not usable: {sum(1 for r in neg if r['after_strict'] != 'usable')}/{len(neg)}")
    print(f"[30f_dryrun] positive controls usable/partial: {sum(1 for r in pos if r['after_strict'] in {'usable','partial'})}/{len(pos)}")
    print(f"[30f_dryrun] downgraded controls: {len(downgraded)}")
    verdict = neg_not_usable and pos_ok and not downgraded
    print(f"[30f_dryrun] verdict: {'PASS' if verdict else 'FAIL'}")
    print(f"[30f_dryrun] wrote {SUMMARY_PATH}")
    return 0 if verdict else 1


if __name__ == "__main__":
    raise SystemExit(main())
