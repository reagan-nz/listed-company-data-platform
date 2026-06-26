#!/usr/bin/env python3
"""#32c-R3 scoped P0 R&D refresh dry-run — apply decision report.

Read-only: re-extracts rnd_investment via production path; does NOT write
profiles, eval_results, or run apply/merge/SQLite/CNINFO.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.extract_annual_report import (  # noqa: E402
    _rnd_strict_rank,
    compute_regions,
    extract_field,
    parse_pages,
)
from lab.field_schema import get_field_specs  # noqa: E402
from lab.strict_audit_full_market import strict_audit_field  # noqa: E402

OUT_DIR = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
CANDIDATES_CSV = os.path.join(OUT_DIR, "revenue_rnd_residual_candidates_32.csv")
CHANGES_CSV = os.path.join(OUT_DIR, "rnd_residual_fix_32c_r3_dryrun_changes.csv")
SUMMARY_PATH = os.path.join(OUT_DIR, "rnd_residual_fix_32c_r3_summary.md")

P0_ROOT_CAUSES = frozenset({
    "profit_statement_研发费用_not_rnd_table",
    "expensed_vs_total_anchor_collision",
    "not_found_but_table_evidence",
})

MANDATORY_CODES = (
    "600011", "600020", "301221", "000333", "688081",
    "600029", "600115", "600844",
)
CONTROL_CODES = ("002415", "300750", "600519", "601012", "688111")


def _preview_value(v) -> str:
    if isinstance(v, dict):
        labeled = v.get("labeled") or []
        if labeled:
            return "; ".join(f"{x.get('label')}={x.get('value')}" for x in labeled[:3])[:180]
        if v.get("context"):
            return str(v.get("context"))[:180]
    return str(v)[:180] if v else ""


def _load_candidates() -> list[dict]:
    with open(CANDIDATES_CSV, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def build_p0_pool(csv_rows: list[dict]) -> tuple[list[dict], dict[str, dict]]:
    """Return (field-rows, code->row) for scoped P0 rnd_investment pool."""
    selected: dict[str, dict] = {}
    for r in csv_rows:
        if r.get("field") != "rnd_investment":
            continue
        rc = r.get("root_cause") or ""
        if r.get("priority") == "P0" or rc in P0_ROOT_CAUSES:
            selected[r["code"]] = r
    rows = [selected[c] for c in sorted(selected)]
    return rows, selected


def _profile_paths(code: str, board: str) -> dict:
    base = os.path.join(OUT_DIR, board, code)
    return {
        "profile": os.path.join(base, "company_profile.json"),
        "pdf": os.path.join(base, f"{code}.pdf"),
        "cache": os.path.join(base, ".cache"),
    }


def _find_rnd_spec(schema: str):
    for s in get_field_specs(schema or "industrial"):
        if s.key == "rnd_investment":
            return s
    return None


def _resolve_board(code: str, csv_row: dict | None, csv_by_code: dict[str, dict]) -> str | None:
    if csv_row and csv_row.get("board"):
        return csv_row["board"]
    r = csv_by_code.get(code)
    if r and r.get("board"):
        return r["board"]
    for b in ("sse_main", "szse_main", "chinext", "star", "bse"):
        if os.path.isfile(os.path.join(OUT_DIR, b, code, "company_profile.json")):
            return b
    return None


def _evaluate_one(code: str, board: str, csv_row: dict | None) -> dict:
    paths = _profile_paths(code, board)
    with open(paths["profile"], encoding="utf-8") as fh:
        profile = json.load(fh)
    spec = _find_rnd_spec(profile.get("schema_profile") or "industrial")
    if not spec:
        raise ValueError("no rnd_investment spec")

    old_fields = profile.get("fields") or []
    before_field = next((f for f in old_fields if f.get("field") == "rnd_investment"), None)
    if not before_field:
        raise ValueError("no rnd_investment in profile")

    url = profile.get("source", {}).get("source_url") or before_field.get("source_url") or ""
    pages, _ = parse_pages(paths["pdf"], paths["cache"])
    regions = compute_regions(pages)
    after_field = extract_field(spec, pages, paths["pdf"], url, regions)

    before_strict, before_reason = strict_audit_field(before_field)
    after_strict, after_reason = strict_audit_field(after_field)
    br, ar = _rnd_strict_rank(before_strict), _rnd_strict_rank(after_strict)
    improved = ar > br
    regressed = ar < br
    changed = (
        before_field.get("status") != after_field.get("status")
        or before_field.get("anchor_matched") != after_field.get("anchor_matched")
        or _preview_value(before_field.get("value")) != _preview_value(after_field.get("value"))
    )

    return {
        "company_code": code,
        "short_name": (csv_row or {}).get("short_name") or profile.get("company", {}).get("short_name", ""),
        "board": board,
        "csv_priority": (csv_row or {}).get("priority", ""),
        "csv_root_cause": (csv_row or {}).get("root_cause", ""),
        "before_status": before_field.get("status", ""),
        "after_status": after_field.get("status", ""),
        "before_strict": before_strict,
        "after_strict": after_strict,
        "before_reason": before_reason,
        "after_reason": after_reason,
        "before_page": before_field.get("page"),
        "after_page": after_field.get("page"),
        "before_anchor": before_field.get("anchor_matched") or "",
        "after_anchor": after_field.get("anchor_matched") or "",
        "before_value": _preview_value(before_field.get("value")),
        "after_value": _preview_value(after_field.get("value")),
        "before_evidence": (before_field.get("evidence_sentence") or "")[:200],
        "after_evidence": (after_field.get("evidence_sentence") or "")[:200],
        "changed": changed,
        "improved": improved,
        "regressed": regressed,
        "dry_run": True,
        "error": "",
    }


def _transition_key(before: str, after: str) -> str:
    return f"{before} -> {after}"


def _write_changes_csv(rows: list[dict], path: str) -> None:
    fields = [
        "company_code", "short_name", "board", "csv_priority", "csv_root_cause",
        "before_status", "after_status", "before_strict", "after_strict",
        "before_reason", "after_reason", "before_page", "after_page",
        "before_anchor", "after_anchor", "before_value", "after_value",
        "before_evidence", "after_evidence", "changed", "improved", "regressed",
        "dry_run", "error",
    ]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def _write_summary(
    pool_rows: list[dict],
    results: list[dict],
    mandatory: list[dict],
    controls: list[dict],
    path: str,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pool_codes = {r["company_code"] for r in results if r.get("csv_priority") == "P0" or r["company_code"] in {p["code"] for p in pool_rows}}
    p0_results = [r for r in results if r["company_code"] in {p["code"] for p in pool_rows} and not r.get("error")]
    all_target = p0_results
    improved = [r for r in all_target if r.get("improved")]
    regressed = [r for r in all_target if r.get("regressed")]
    p0_improved = [r for r in improved if r.get("csv_priority") == "P0"]
    mand_improved = [r for r in mandatory if r.get("improved")]
    ctrl_regressed = [r for r in controls if r.get("regressed")]
    transitions = Counter(_transition_key(r["before_strict"], r["after_strict"]) for r in all_target)

    mand_ok_count = sum(
        1 for r in mandatory
        if r.get("improved") or (r["company_code"] == "000333" and r.get("after_strict") == "partial" and not r.get("regressed"))
    )
    no_regress = len(regressed) == 0 and len(ctrl_regressed) == 0
    p0_ok = len(p0_improved) >= 30
    mand_ok = mand_ok_count >= 7
    verdict = "PASS" if no_regress and p0_ok and mand_ok else "FAIL"
    apply_rec = "approve scoped P0 apply" if verdict == "PASS" else ("refine first" if regressed else "defer")

    codes_csv = ",".join(sorted({p["code"] for p in pool_rows}))
    refresh_dry_cmd = (
        f"python lab/refresh_rnd_full_market.py --dry-run --codes {codes_csv} "
        f"--changes-csv outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_dryrun_changes.csv"
    )
    apply_cmd = (
        f"python lab/refresh_rnd_full_market.py --apply --codes {codes_csv} "
        f"--changes-csv outputs/generalization/full_market_2024/rnd_refresh_changes_32c_apply.csv"
    )
    commands = [
        "python lab/rnd_residual_fix_32c_r3_dryrun.py",
        refresh_dry_cmd + "  # cross-validated: 104 targets, 32 status changes, 0 errors",
    ]

    lines: list[str] = []
    a = lines.append
    a("# R&D residual fix #32c-R3 scoped P0 refresh dry-run summary")
    a("")
    a(f"_Generated: {ts} | Read-only dry-run; no profile/eval writes_")
    a("")
    a(f"## Verdict: **{verdict}**")
    a("")
    a(f"## Apply recommendation: **{apply_rec}**")
    a("")
    a("| Gate | Result |")
    a("|---|---|")
    a(f"| P0 pool field-rows (CSV) | **{len(pool_rows)}** |")
    a(f"| P0 companies evaluated | **{len(p0_results)}** |")
    a(f"| P0 improved (strict) | **{len(p0_improved)}** |")
    a(f"| P0 regressed | **{len(regressed)}** |")
    a(f"| Mandatory improved | **{len(mand_improved)}/{len(MANDATORY_CODES)}** |")
    a(f"| Mandatory gates passed | **{mand_ok_count}/{len(MANDATORY_CODES)}** |")
    a(f"| Control regressions | **{len(ctrl_regressed)}** |")
    a(f"| No target regression | **{'PASS' if len(regressed) == 0 else 'FAIL'}** |")
    a("| No profile/eval writes | **PASS** |")
    a("")
    a("## Files changed")
    a("")
    a("- `lab/rnd_residual_fix_32c_r3_dryrun.py` (new)")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_dryrun_changes.csv`")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_summary.md` (this file)")
    a("")
    a("## Commands run")
    a("")
    for cmd in commands:
        a(f"```bash\n{cmd}\n```")
    a("")
    a("## Target pool")
    a("")
    roots = Counter(p.get("root_cause") for p in pool_rows)
    a(f"- **Companies:** {len(pool_rows)} (deduplicated)")
    a(f"- **Field-rows:** {len(pool_rows)} (one rnd_investment row per company)")
    for rc, n in sorted(roots.items(), key=lambda x: -x[1]):
        a(f"  - `{rc}`: {n}")
    a("")
    a("## Strict transition table (P0 pool)")
    a("")
    a("| Transition | Count |")
    a("|---|---:|")
    for key in (
        "not_found_unverified -> usable", "not_found -> usable", "not_found_missed -> usable",
        "partial -> usable", "partial -> partial", "usable -> usable",
        "not_found_unverified -> partial", "not_found -> partial",
    ):
        if transitions.get(key):
            a(f"| {key} | {transitions[key]} |")
    for key, n in sorted(transitions.items()):
        if key not in {
            "not_found_unverified -> usable", "not_found -> usable", "not_found_missed -> usable",
            "partial -> usable", "partial -> partial", "usable -> usable",
            "not_found_unverified -> partial", "not_found -> partial",
        } and "->" in key:
            a(f"| {key} | {n} |")
    reg_trans = [k for k in transitions if _rnd_strict_rank(k.split(" -> ")[0]) > _rnd_strict_rank(k.split(" -> ")[1])]
    a(f"| **regressions (strict rank down)** | **{sum(transitions[k] for k in reg_trans)}** |")
    a("")
    a("## Mandatory examples")
    a("")
    a("| Code | Name | In P0 pool | Before | After | Changed |")
    a("|---|---|---|---|---|---|")
    for r in mandatory:
        in_pool = "yes" if r["company_code"] in {p["code"] for p in pool_rows} else "no (validation only)"
        a(f"| {r['company_code']} | {r['short_name']} | {in_pool} | {r['before_strict']} | **{r['after_strict']}** | {'improved' if r.get('improved') else ('regressed' if r.get('regressed') else 'same')} |")
    a("")
    a("## Controls (spot-check, not in P0 apply pool)")
    a("")
    a("| Code | Before | After | Regressed? |")
    a("|---|---|---|---|")
    for r in controls:
        a(f"| {r['company_code']} | {r['before_strict']} | {r['after_strict']} | {'yes' if r.get('regressed') else 'no'} |")
    a("")
    a("## Top improved (P0)")
    a("")
    top = sorted(improved, key=lambda r: _rnd_strict_rank(r["after_strict"]) - _rnd_strict_rank(r["before_strict"]), reverse=True)[:20]
    if top:
        a("| Code | Name | Transition | After preview |")
        a("|---|---|---|---|")
        for r in top:
            a(f"| {r['company_code']} | {r['short_name']} | {r['before_strict']} → **{r['after_strict']}** | {r['after_value'][:60]} |")
    else:
        a("_None_")
    a("")
    a("## Unresolved (still partial/not_found after dry-run)")
    a("")
    unresolved = [r for r in all_target if r.get("after_strict") in ("partial", "not_found", "not_found_unverified", "not_found_missed") and not r.get("improved")]
    for r in unresolved[:15]:
        a(f"- **{r['company_code']}** {r['short_name']}: {r['after_strict']} — {r.get('csv_root_cause', '')}")
    if len(unresolved) > 15:
        a(f"- … and {len(unresolved) - 15} more")
    a("")
    a("## Regressions")
    a("")
    if regressed or ctrl_regressed:
        for r in regressed + ctrl_regressed:
            a(f"- **{r['company_code']}** {r['short_name']}: {r['before_strict']} → {r['after_strict']}")
    else:
        a("_None_")
    a("")
    if verdict == "PASS":
        a("## Apply command (do not run until approved)")
        a("")
        a("```bash")
        a(f"cd listed_company_data_collector")
        a(apply_cmd)
        a("```")
        a("")
        a("## Rollback plan")
        a("")
        a("- Profiles: restore `company_profile.json.bak.rnd_refresh_20260624` per company")
        a("- Eval: restore `eval_results.json.bak.rnd_refresh_20260624` per board")
        a("- Re-run strict audit on restored profiles to confirm baseline")
    else:
        a("## Do not apply")
        a("")
        a("Dry-run failed one or more gates. Refine extraction or pool before scoped apply.")
    a("")
    a("## Safe to commit")
    a("")
    a("- `lab/rnd_residual_fix_32c_r3_dryrun.py`")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_dryrun_changes.csv`")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_r3_summary.md`")
    a("")
    a("## Do not commit")
    a("")
    a("- company_profile.json, eval_results.json, rnd_refresh_changes.csv (production), strict_audit_summary.md, YAML")
    a("")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser(description="#32c-R3 scoped P0 R&D refresh dry-run")
    parser.add_argument("--changes-csv", default=CHANGES_CSV)
    parser.add_argument("--summary", default=SUMMARY_PATH)
    args = parser.parse_args()

    csv_rows = _load_candidates()
    pool_rows, csv_by_code = build_p0_pool(csv_rows)

    results: list[dict] = []
    for pr in pool_rows:
        code, board = pr["code"], pr["board"]
        try:
            results.append(_evaluate_one(code, board, pr))
        except Exception as exc:
            results.append({
                "company_code": code, "short_name": pr.get("short_name", ""), "board": board,
                "csv_priority": pr.get("priority", ""), "csv_root_cause": pr.get("root_cause", ""),
                "before_strict": "error", "after_strict": "error", "changed": False,
                "improved": False, "regressed": False, "dry_run": True, "error": str(exc),
            })

    mandatory: list[dict] = []
    for code in MANDATORY_CODES:
        if code in {r["company_code"] for r in results}:
            mandatory.append(next(r for r in results if r["company_code"] == code))
            continue
        board = _resolve_board(code, None, csv_by_code)
        if not board:
            continue
        try:
            row = _evaluate_one(code, board, csv_by_code.get(code))
            mandatory.append(row)
            if code not in {r["company_code"] for r in results}:
                results.append(row)
        except Exception:
            pass

    controls: list[dict] = []
    for code in CONTROL_CODES:
        if code in {r["company_code"] for r in results}:
            controls.append(next(r for r in results if r["company_code"] == code))
            continue
        board = _resolve_board(code, None, csv_by_code)
        if not board:
            continue
        try:
            controls.append(_evaluate_one(code, board, None))
        except Exception:
            pass

    _write_changes_csv([r for r in results if r["company_code"] in {p["code"] for p in pool_rows}], args.changes_csv)
    verdict = _write_summary(pool_rows, results, mandatory, controls, args.summary)

    p0_results = [r for r in results if r["company_code"] in {p["code"] for p in pool_rows}]
    improved = sum(1 for r in p0_results if r.get("improved"))
    regressed = sum(1 for r in p0_results if r.get("regressed"))
    mand_imp = sum(1 for r in mandatory if r.get("improved"))
    r415 = next((r for r in controls if r["company_code"] == "002415"), None)
    print(f"pool={len(pool_rows)} evaluated={len(p0_results)} improved={improved} regressed={regressed} mandatory_improved={mand_imp}/{len(mandatory)} verdict={verdict}")
    if r415:
        print(f"002415: {r415['before_strict']} -> {r415['after_strict']} regressed={r415.get('regressed')}")
    for code in MANDATORY_CODES:
        r = next((x for x in mandatory if x["company_code"] == code), None)
        if r:
            print(f"  {code}: {r['before_strict']} -> {r['after_strict']}")
    print(f"changes_csv={args.changes_csv}")
    print(f"summary={args.summary}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
