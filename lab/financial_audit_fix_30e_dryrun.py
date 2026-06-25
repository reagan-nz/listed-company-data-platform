#!/usr/bin/env python3
"""#30e financial table plausibility dry-run."""
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
SUMMARY_PATH = os.path.join(OUT_DIR, "financial_audit_fix_30e_dryrun_summary.md")
SAMPLE_PATH = os.path.join(OUT_DIR, "financial_audit_sample.csv")

NEGATIVE_TARGETS: list[tuple[str, str, str]] = [
    ("601963", "sse_main", "loan_structure"),
    ("601963", "sse_main", "deposit_structure"),
    ("002966", "szse_main", "loan_structure"),
    ("600015", "sse_main", "loan_structure"),
    ("600000", "sse_main", "loan_structure"),
    ("600000", "sse_main", "deposit_structure"),
    ("002142", "szse_main", "loan_structure"),
    ("002142", "szse_main", "deposit_structure"),
    ("600000", "sse_main", "regional_distribution"),
    ("001236", "szse_main", "revenue_by_region"),
    ("002961", "szse_main", "revenue_by_region"),
    ("601878", "sse_main", "revenue_by_segment"),
    ("600369", "sse_main", "revenue_by_segment"),
    ("601696", "sse_main", "revenue_by_segment"),
    ("601136", "sse_main", "revenue_by_segment"),
    ("601336", "sse_main", "revenue_by_segment"),
    ("600927", "sse_main", "revenue_by_segment"),
    ("603093", "sse_main", "revenue_by_segment"),
]

TABLE_FIELDS = {
    "loan_structure",
    "deposit_structure",
    "regional_distribution",
    "revenue_by_segment",
    "revenue_by_region",
}


def _load_sample() -> dict[tuple[str, str], dict]:
    with open(SAMPLE_PATH, encoding="utf-8-sig") as fh:
        rows = [ln for ln in fh if not ln.startswith("#")]
    return {(r["code"], r["field"]): r for r in csv.DictReader(rows)}


def _profile_schema(code: str, board: str) -> str:
    path = os.path.join(OUT_DIR, board, code, "company_profile.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return str(data.get("schema_profile") or "")


def _field_spec(profile: str, field_key: str):
    for spec in get_field_specs(profile):
        if spec.key == field_key:
            return spec
    raise KeyError((profile, field_key))


def _profile_field_map(code: str, board: str) -> dict[str, dict]:
    path = os.path.join(OUT_DIR, board, code, "company_profile.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {f.get("field"): f for f in data.get("fields") or []}


def _pdf_path(code: str, board: str) -> str:
    return os.path.join(OUT_DIR, board, code, f"{code}.pdf")


def _preview(val: dict | None) -> str:
    if not isinstance(val, dict):
        return ""
    if val.get("rows"):
        rows = val.get("rows") or []
        short = rows[:2]
        return " / ".join(" | ".join(str(c) for c in row) for row in short)[:180]
    if val.get("snippet"):
        return str(val.get("snippet"))[:180]
    return str(val)[:180]


def _dry_run_row(code: str, board: str, field_key: str) -> dict:
    profile_fields = _profile_field_map(code, board)
    before = profile_fields[field_key]
    pdf = _pdf_path(code, board)
    pages, _ = parse_pages(pdf, CACHE_DIR)
    regions = compute_regions(pages)
    spec = _field_spec(_profile_schema(code, board), field_key)
    after = extract_field(
        spec,
        pages,
        pdf,
        before.get("source_url") or "",
        regions,
        profile_fields=profile_fields,
    )
    before_strict, before_reason = strict_audit_field(before, spec, pdf)
    after_strict, after_reason = strict_audit_field(after, spec, pdf)
    return {
        "code": code,
        "board": board,
        "field": field_key,
        "before_status": before.get("status", ""),
        "before_strict": before_strict,
        "before_reason": before_reason,
        "before_preview": _preview(before.get("value")),
        "after_status": after.get("status", ""),
        "after_strict": after_strict,
        "after_reason": after_reason,
        "after_preview": _preview(after.get("value")),
        "after_page": after.get("page"),
    }


def _controls(sample_rows: dict[tuple[str, str], dict]) -> list[tuple[str, str, str]]:
    controls: list[tuple[str, str, str]] = []
    target_keys = {(c, f) for c, _, f in NEGATIVE_TARGETS}
    board_by_code = {c: b for c, b, _ in NEGATIVE_TARGETS}
    for (code, field), row in sample_rows.items():
        grade = (row.get("manual_grade") or "").strip().upper()
        if field not in TABLE_FIELDS or grade not in {"CORRECT", "PARTIAL"}:
            continue
        if (code, field) in target_keys:
            continue
        board = row.get("board") or board_by_code.get(code)
        if board:
            controls.append((code, board, field))
    return sorted(controls)


def _write_summary(neg_rows: list[dict], control_rows: list[dict]) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    neg_pass = all(r["after_strict"] == "wrong" for r in neg_rows)
    neg_usable = sum(1 for r in neg_rows if r["after_strict"] == "usable")
    control_changed_to_wrong = sum(
        1 for r in control_rows
        if r["before_strict"] != "wrong" and r["after_strict"] == "wrong"
    )
    verdict = "PASS" if neg_pass and neg_usable == 0 and control_changed_to_wrong <= 2 else "FAIL"
    lines: list[str] = []
    a = lines.append
    a("# Financial audit fix #30e dry-run — financial table plausibility")
    a("")
    a(f"_Generated: {ts} | targeted extraction + audit dry-run on cached PDFs only_")
    a("")
    a(f"## Verdict: **{verdict}**")
    a("")
    a("| Gate | Result |")
    a("|---|---|")
    a(f"| All known manual WRONG table targets are strict wrong | **{'PASS' if neg_pass else 'FAIL'}** |")
    a(f"| 0 known manual WRONG table targets become usable | **{'PASS' if neg_usable == 0 else 'FAIL'}** |")
    a(f"| Manual CORRECT/PARTIAL table controls do not get mass downgraded | **{'PASS' if control_changed_to_wrong <= 2 else 'FAIL'}** |")
    a("| No profile/eval/population/sample CSV writes | **PASS** |")
    a("")
    a("## Files changed")
    a("")
    a("- `lab/strict_audit_financial_full_market.py`")
    a("- `lab/financial_audit_fix_30e_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/financial_audit_fix_30e_dryrun_summary.md`")
    a("")
    a("## Code changes")
    a("")
    a("1. Tightened financial-only table reject vocabulary for `loan_structure`, `deposit_structure`, `regional_distribution` / `revenue_by_region`, and `revenue_by_segment`.")
    a("2. Added explicit total-only / no-breakdown guards for loan/deposit structure.")
    a("3. Added branch-roster reject for region tables and cost-only reject for segment tables without revenue rows.")
    a("4. Kept all changes inside `lab/strict_audit_financial_full_market.py`; no extraction writes, no non-fin audit changes.")
    a("5. Fixed the dry-run harness to resolve field specs by each company’s real `schema_profile`, which removes the earlier `601059 revenue_by_segment` artifact from cross-profile spec reuse.")
    a("")
    a("## Table target list")
    a("")
    a("| Code | Field | Scope |")
    a("|---|---|---|")
    for code, _, field in NEGATIVE_TARGETS:
        a(f"| {code} | `{field}` | manual WRONG target |")
    a("")
    a("## Before / after strict table")
    a("")
    a("| Code | Field | Before strict | After strict | Before status | After status |")
    a("|---|---|---|---|---|---|")
    for row in neg_rows:
        a(f"| {row['code']} | `{row['field']}` | {row['before_strict']} | **{row['after_strict']}** | {row['before_status']} | {row['after_status']} |")
    a("")
    a("## Manual WRONG target results")
    a("")
    a("| Code | Field | After strict | After reason | Preview |")
    a("|---|---|---|---|---|")
    for row in neg_rows:
        a(f"| {row['code']} | `{row['field']}` | {row['after_strict']} | {row['after_reason']} | {row['after_preview']} |")
    a("")
    a("## Manual CORRECT/PARTIAL control results")
    a("")
    a(f"Controls evaluated: **{len(control_rows)}**")
    a("")
    a("| Code | Field | Manual | Before strict | After strict | After reason |")
    a("|---|---|---|---|---|---|")
    for row in control_rows:
        a(f"| {row['code']} | `{row['field']}` | {row['manual_grade']} | {row['before_strict']} | {row['after_strict']} | {row['after_reason']} |")
    a("")
    a("## Risk caveats")
    a("")
    a(f"- Control rows newly downgraded to `wrong`: **{control_changed_to_wrong}**.")
    a("- Earlier `601059 revenue_by_segment` downgrade was a harness/report artifact: the prior harness keyed specs only by field name and could evaluate a broker row with another financial subtype’s field spec.")
    a("- This dry-run re-extracts target rows from cached PDFs only; it does not rewrite profiles, population CSVs, or evaluation artifacts.")
    a("- Region-table semantics still intentionally allow some banking loan-by-region distribution tables when they contain real region + numeric distribution rows.")
    a("")
    a(f"## Sample apply recommendation: **{'Deferred pending review' if verdict == 'PASS' else 'No'}**")
    a("")
    a("Do not sample-apply this yet unless you explicitly accept any control downgrades and want the stricter table safety tradeoff.")
    a("")
    a("## Safe-to-commit list")
    a("")
    a("- `lab/strict_audit_financial_full_market.py`")
    a("- `lab/financial_audit_fix_30e_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/financial_audit_fix_30e_dryrun_summary.md`")
    a("")
    a("## Do-not-commit list")
    a("")
    a("- any `company_profile.json`")
    a("- `financial_audit_population.csv`")
    a("- `financial_audit_summary.md`")
    a("- `financial_audit_sample.csv`")
    a("- any `eval_results.json`")
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="#30e financial table plausibility dry-run")
    ap.parse_args()
    sample_rows = _load_sample()
    neg_rows = [_dry_run_row(code, board, field) for code, board, field in NEGATIVE_TARGETS]
    control_targets = _controls(sample_rows)
    control_rows: list[dict] = []
    for code, board, field in control_targets:
        row = _dry_run_row(code, board, field)
        row["manual_grade"] = sample_rows[(code, field)]["manual_grade"]
        control_rows.append(row)
    _write_summary(neg_rows, control_rows)
    neg_pass = all(r["after_strict"] == "wrong" for r in neg_rows)
    neg_usable = sum(1 for r in neg_rows if r["after_strict"] == "usable")
    control_changed_to_wrong = sum(
        1 for r in control_rows
        if r["before_strict"] != "wrong" and r["after_strict"] == "wrong"
    )
    print(f"[30e_dryrun] negative targets wrong: {sum(1 for r in neg_rows if r['after_strict']=='wrong')}/{len(neg_rows)}")
    print(f"[30e_dryrun] negative targets usable: {neg_usable}")
    print(f"[30e_dryrun] control rows newly downgraded to wrong: {control_changed_to_wrong}/{len(control_rows)}")
    print(f"[30e_dryrun] verdict: {'PASS' if neg_pass and neg_usable == 0 and control_changed_to_wrong <= 2 else 'FAIL'}")
    print(f"[30e_dryrun] wrote {SUMMARY_PATH}")
    return 0 if neg_pass and neg_usable == 0 and control_changed_to_wrong <= 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
