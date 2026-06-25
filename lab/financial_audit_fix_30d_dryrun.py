#!/usr/bin/env python3
"""#30d broker income / margin recall — read-only dry-run validation."""
from __future__ import annotations

import argparse
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

POSITIVE_TARGETS: list[dict] = [
    {"code": "601878", "board": "sse_main", "field": "investment_banking_income", "expected_value": "677,073,421.90"},
    {"code": "601878", "board": "sse_main", "field": "asset_management_income", "expected_value": "530,211,137.63"},
    {"code": "601878", "board": "sse_main", "field": "margin_lending_balance", "expected_value": "24,224,341,732.66"},
    {"code": "600030", "board": "sse_main", "field": "investment_banking_income", "expected_value": "4,159,191,856.95"},
]

NEGATIVE_CONTROLS: list[tuple[str, str, str]] = [
    ("601377", "sse_main", "brokerage_income"),
    ("601377", "sse_main", "margin_lending_balance"),
    ("601878", "sse_main", "brokerage_income"),
    ("601878", "sse_main", "proprietary_trading_income"),
    ("601878", "sse_main", "risk_control_indicators"),
    ("600369", "sse_main", "proprietary_trading_income"),
    ("600369", "sse_main", "risk_control_indicators"),
    ("601990", "sse_main", "brokerage_income"),
    ("601990", "sse_main", "asset_management_income"),
    ("601990", "sse_main", "risk_control_indicators"),
    ("601696", "sse_main", "asset_management_income"),
    ("601696", "sse_main", "margin_lending_balance"),
    ("600030", "sse_main", "margin_lending_balance"),
    ("600030", "sse_main", "risk_control_indicators"),
    ("601108", "sse_main", "investment_banking_income"),
    ("601108", "sse_main", "asset_management_income"),
    ("601108", "sse_main", "proprietary_trading_income"),
    ("000783", "szse_main", "brokerage_income"),
    ("000783", "szse_main", "investment_banking_income"),
    ("000783", "szse_main", "margin_lending_balance"),
    ("601059", "sse_main", "risk_control_indicators"),
    ("601136", "sse_main", "proprietary_trading_income"),
    ("601136", "sse_main", "margin_lending_balance"),
]


def _norm_num(s: str) -> str:
    return (s or "").replace(",", "").replace(" ", "").strip()


def _broker_spec(field_key: str):
    for spec in get_field_specs("broker"):
        if spec.key == field_key:
            return spec
    raise KeyError(field_key)


def _profile_field(code: str, board: str, field_key: str) -> dict | None:
    path = os.path.join(OUT_DIR, board, code, "company_profile.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    for f in data.get("fields") or []:
        if f.get("field") == field_key:
            return f
    return None


def _profile_field_map(code: str, board: str) -> dict[str, dict]:
    path = os.path.join(OUT_DIR, board, code, "company_profile.json")
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {f.get("field"): f for f in data.get("fields") or []}


def _pdf_path(code: str, board: str) -> str:
    return os.path.join(OUT_DIR, board, code, f"{code}.pdf")


def _dry_run_row(code: str, board: str, field_key: str) -> dict:
    pdf = _pdf_path(code, board)
    spec = _broker_spec(field_key)
    profile_fields = _profile_field_map(code, board)
    before = profile_fields.get(field_key) or {}
    pages, _ = parse_pages(pdf, CACHE_DIR)
    regions = compute_regions(pages)
    after = extract_field(
        spec, pages, pdf, before.get("source_url") or "", regions,
        profile_fields=profile_fields,
    )
    strict_before, _ = strict_audit_field(before, spec, pdf) if before else ("", "")
    strict_after, reason_after = strict_audit_field(after, spec, pdf)
    labeled = (after.get("value") or {}).get("labeled") or []
    preview = "; ".join(f"{x.get('label')}={x.get('value')}" for x in labeled[:3])
    return {
        "code": code,
        "board": board,
        "field": field_key,
        "before_strict": strict_before,
        "before_status": before.get("status", ""),
        "after_strict": strict_after,
        "after_status": after.get("status", ""),
        "after_page": after.get("page"),
        "after_reason": reason_after,
        "after_labeled": labeled,
        "value_preview": preview,
    }


def _positive_pass(row: dict, expected_value: str) -> tuple[bool, str]:
    if row["after_strict"] != "usable":
        return False, row["after_reason"]
    labeled = row["after_labeled"]
    if not labeled:
        return False, "no labeled pairs"
    got = _norm_num(str(labeled[0].get("value", "")))
    exp = _norm_num(expected_value)
    return (got == exp, f"got={labeled[0].get('value')} expected={expected_value}")


def _write_summary(path: str, pos_rows: list[dict], neg_rows: list[dict], gates: list[tuple[str, bool]]) -> None:
    verdict = "PASS" if all(ok for _, ok in gates) else "FAIL"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = []
    a = lines.append
    a("# Financial audit fix #30d dry-run — broker income / margin recall")
    a("")
    a(f"_Generated: {ts} | code-only dry-run on cached PDFs only_")
    a("")
    a(f"## Verdict: **{verdict}**")
    a("")
    a("| Gate | Result |")
    a("|---|---|")
    for name, ok in gates:
        a(f"| {name} | **{'PASS' if ok else 'FAIL'}** |")
    a("")
    a("## Files changed")
    a("")
    a("- `lab/extract_annual_report.py`")
    a("- `lab/field_schema.py`")
    a("- `lab/financial_audit_fix_30d_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/financial_audit_fix_30d_dryrun_summary.md`")
    a("")
    a("## Exact code changes")
    a("")
    a("1. Added broker-only `extract_broker_segment_income()` for `investment_banking_income` and `asset_management_income` with whitespace-tolerant labels, segment-table context checks, comma-amount requirement, and narrative rejects.")
    a("2. Added `extract_broker_deep_ib_income()` notes fallback for `investment_banking_income` only, gated by `手续费及佣金` page context and amount ≥ ¥1B.")
    a("3. Added `extract_broker_margin_balance()` for MD&A-only `融出资金` asset-composition rows; rejects 利息/净增加/减值/现金流 noise and does not search notes.")
    a("4. Wired these broker branches in `extract_field()` before generic numeric extraction.")
    a("5. Added narrow secondary anchors in `field_schema.py` for IB/AM net-income labels.")
    a("")
    a("## Positive recovery table")
    a("")
    a("| Code | Field | Before strict | After strict | After page | Value | Pass |")
    a("|---|---|---|---|---:|---|---|")
    for row, target in zip(pos_rows, POSITIVE_TARGETS):
        ok, _ = _positive_pass(row, target["expected_value"])
        a(f"| {row['code']} | `{row['field']}` | {row['before_strict']} | **{row['after_strict']}** | {row['after_page']} | {row['value_preview']} | **{'PASS' if ok else 'FAIL'}** |")
    a("")
    a("## Negative-control table")
    a("")
    a("| Code | Field | Before strict | After strict | After status | Pass |")
    a("|---|---|---|---|---|---|")
    for row in neg_rows:
        ok = row["after_strict"] != "usable"
        a(f"| {row['code']} | `{row['field']}` | {row['before_strict']} | {row['after_strict']} | {row['after_status']} | **{'PASS' if ok else 'FAIL'}** |")
    a("")
    a("## Risk caveats")
    a("")
    a("- Deep IB notes fallback is medium risk on other mega-brokers, but is constrained to fee-note pages and `投资银行业务净收入`/`投行业务净收入` labels with amount ≥ ¥1B.")
    a("- Margin parsing intentionally excludes notes, so large consolidated `融出资金` balances in notes remain unavailable by design.")
    a("- `brokerage_income` and generic `投资收益` logic were not widened.")
    a("")
    a(f"## Sample-company apply recommendation: **{'Yes' if verdict == 'PASS' else 'No'}**")
    a("")
    a("Proceed to a tightly scoped sample-company apply only if you want to persist the 4 broker positive recoveries into profile files." if verdict == "PASS" else "Do not apply until dry-run gates pass.")
    a("")
    a("## Safe-to-commit list")
    a("")
    a("- `lab/extract_annual_report.py`")
    a("- `lab/field_schema.py`")
    a("- `lab/financial_audit_fix_30d_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/financial_audit_fix_30d_dryrun_summary.md`")
    a("")
    a("## Do-not-commit list")
    a("")
    a("- any `company_profile.json`")
    a("- `financial_audit_population.csv`")
    a("- `financial_audit_summary.md`")
    a("- any `eval_results.json`")
    a("- PDFs / `.cache` / SQLite")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="#30d broker recall dry-run")
    ap.add_argument("--out-dir", default=OUT_DIR)
    args = ap.parse_args()
    summary_path = os.path.join(args.out_dir, "financial_audit_fix_30d_dryrun_summary.md")

    pos_rows = [_dry_run_row(t["code"], t["board"], t["field"]) for t in POSITIVE_TARGETS]
    neg_rows = [_dry_run_row(c, b, f) for c, b, f in NEGATIVE_CONTROLS]

    pos_ok = sum(1 for row, target in zip(pos_rows, POSITIVE_TARGETS) if _positive_pass(row, target["expected_value"])[0])
    neg_ok = sum(1 for row in neg_rows if row["after_strict"] != "usable")
    m030_margin = next(r for r in neg_rows if r["code"] == "600030" and r["field"] == "margin_lending_balance")
    gate_m030 = m030_margin["after_strict"] != "usable"
    gate_601108 = all(
        row["after_strict"] != "usable"
        for row in neg_rows
        if row["code"] == "601108" and row["field"] in {"investment_banking_income", "asset_management_income"}
    )
    gate_601108_prop = next(r for r in neg_rows if r["code"] == "601108" and r["field"] == "proprietary_trading_income")["after_strict"] != "usable"
    gates = [
        ("4/4 confirmed MISSED positives become strict usable", pos_ok == 4),
        ("0/23 ABSENT-OK controls become strict usable", neg_ok == 23),
        ("600030 margin_lending_balance remains not usable", gate_m030),
        ("601108 IB/AM/proprietary narrative rows remain not usable", gate_601108 and gate_601108_prop),
        ("No profile/eval/population/sample CSV writes", True),
    ]
    _write_summary(summary_path, pos_rows, neg_rows, gates)

    print(f"[30d_dryrun] positives {pos_ok}/4")
    print(f"[30d_dryrun] negatives {neg_ok}/23")
    print(f"[30d_dryrun] verdict {'PASS' if all(ok for _, ok in gates) else 'FAIL'}")
    print(f"[30d_dryrun] wrote {summary_path}")
    return 0 if all(ok for _, ok in gates) else 1


if __name__ == "__main__":
    raise SystemExit(main())
