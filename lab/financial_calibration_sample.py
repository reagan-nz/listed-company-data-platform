"""Financial manual calibration worksheet generator (Issue #27 Phase 1B).

Generates a stratified (company, field) worksheet for human PDF review of the
financial cohort. Read-only over outputs; does not modify profiles or eval_results.

Grade semantics (fill manual_grade after PDF review):
  CORRECT    - field correctly extracted (full).
  PARTIAL    - right region/some content, incomplete.
  WRONG      - wrong section / wrong line item / not this field.
  MISSED     - extractor not_found but disclosure exists in PDF.
  ABSENT-OK  - not_found is correct (genuinely N/A / not disclosed).

Usage:
  python lab/financial_calibration_sample.py --generate \\
    --out-dir outputs/generalization/full_market_2024

  python lab/financial_calibration_sample.py --score FILLED.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
from collections import Counter, defaultdict
from statistics import mean

import yaml

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from lab.field_schema import get_field_specs  # noqa: E402

GRADES = ("CORRECT", "PARTIAL", "WRONG", "MISSED", "ABSENT-OK")

DEFAULT_OUT = os.path.join(_ROOT, "outputs", "generalization", "full_market_2024")
DEFAULT_YAML = os.path.join(_ROOT, "lab", "eval_companies_full_market_2024.yaml")

SEED = 20260627

SUBTYPE_CAVEAT_CODES = frozenset({"000402", "600816", "600318"})

FORCE_BY_SUBTYPE: dict[str, frozenset[str]] = {
    "bank": frozenset({"601963", "600816", "600318"}),
    "broker": frozenset({"601375", "601377", "601878", "000402"}),
    "insurer": frozenset({"601336", "601628"}),
    "other_financial": frozenset({"600927", "001236", "002961", "603093"}),
}

TARGET_COUNTS = {"bank": 12, "broker": 12, "insurer": 2, "other_financial": 4}

RISKY_SNIPPETS = frozenset({
    "major_subsidiaries",
    "industry_discussion",
    "risk_factors",
    "main_business_segments",
})

BAD_STRICT_LABELS = frozenset({"wrong", "partial", "not_found_missed"})

CSV_COLUMNS = [
    "code",
    "name",
    "board",
    "schema_profile",
    "subtype_caveat_flag",
    "field",
    "extraction_type",
    "status",
    "proxy_plausible",
    "automated_strict_label",
    "automated_reason",
    "value_preview",
    "evidence_sentence",
    "page",
    "source_url",
    "pdf_path",
    "manual_grade",
    "manual_notes",
    "reviewer",
    "reviewed_at",
]

GRADE_LEGEND = (
    "# manual_grade allowed values: CORRECT | PARTIAL | WRONG | MISSED | ABSENT-OK "
    "(see lab/financial_calibration_sample.py docstring)"
)


def _profile_path(out_dir: str, code: str, board: str) -> str | None:
    for rel in (f"{code}/company_profile.json", f"{board}/{code}/company_profile.json"):
        p = os.path.join(out_dir, rel)
        if os.path.isfile(p):
            return p
    return None


def _pdf_path(out_dir: str, code: str, board: str) -> str:
    return os.path.join(out_dir, board, code, f"{code}.pdf")


def load_population(path: str) -> list[dict]:
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    for r in rows:
        r["proxy_plausible"] = r["proxy_plausible"].strip().lower() in ("true", "1", "yes")
        r["subtype_caveat_flag"] = r.get("subtype_caveat_flag", "").strip().lower() in (
            "true", "1", "yes",
        )
    return rows


def _company_stats(rows: list[dict]) -> dict[str, dict]:
    by_co: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_co[r["code"]].append(r)
    stats: dict[str, dict] = {}
    for code, crows in by_co.items():
        ft = len(crows)
        proxy = mean(1.0 if r["proxy_plausible"] else 0.0 for r in crows)
        bad = sum(1 for r in crows if r["strict_label"] in BAD_STRICT_LABELS)
        wrong_missed = sum(
            1 for r in crows if r["strict_label"] in ("wrong", "not_found_missed")
        )
        numeric_risk = sum(
            1 for r in crows
            if r["extraction_type"] == "numeric"
            and r["strict_label"] in BAD_STRICT_LABELS
        )
        stats[code] = {
            "rows": crows,
            "schema_profile": crows[0]["schema_profile"],
            "name": crows[0]["name"],
            "board": crows[0]["board"],
            "field_total": ft,
            "proxy_ratio": proxy,
            "bad_count": bad,
            "wrong_missed_count": wrong_missed,
            "numeric_risk_count": numeric_risk,
        }
    return stats


def _tier(code: str, st: dict) -> str:
    if st["proxy_ratio"] < 0.50:
        return "low_proxy"
    if st["wrong_missed_count"] >= 4 or st["numeric_risk_count"] >= 3:
        return "high_bad"
    if st["proxy_ratio"] >= 0.80:
        return "high_proxy"
    return "mid"


def select_companies(stats: dict[str, dict], seed: int) -> dict[str, list[str]]:
    """Return subtype -> ordered list of selected company codes."""
    rng = random.Random(seed)
    selected: dict[str, list[str]] = {}

    for subtype, target in TARGET_COUNTS.items():
        forced = sorted(FORCE_BY_SUBTYPE.get(subtype, frozenset()))
        pool = [
            c for c, st in stats.items()
            if st["schema_profile"] == subtype and c not in forced
        ]
        tiers: dict[str, list[str]] = defaultdict(list)
        for code in pool:
            tiers[_tier(code, stats[code])].append(code)
        for t in tiers:
            rng.shuffle(tiers[t])

        picks = list(forced)
        tier_order = ("high_bad", "low_proxy", "high_proxy", "mid")
        idx = 0
        while len(picks) < target:
            progressed = False
            for t in tier_order:
                if tiers[t]:
                    c = tiers[t].pop(0)
                    if c not in picks:
                        picks.append(c)
                        progressed = True
                        break
            if not progressed:
                rest = [c for c in pool if c not in picks]
                rng.shuffle(rest)
                if rest:
                    picks.append(rest[0])
                else:
                    break
        selected[subtype] = picks[:target]
    return selected


def _fields_for_company(crows: list[dict], schema: str) -> list[dict]:
    spec_keys = {s.key: s.extraction for s in get_field_specs(schema)}
    chosen: dict[str, dict] = {}

    def add(row: dict) -> None:
        chosen[row["field"]] = row

    for row in crows:
        fk = row["field"]
        ex = row["extraction_type"]
        if ex == "numeric" or ex == "table":
            add(row)
        elif fk in RISKY_SNIPPETS:
            add(row)
        elif row["strict_label"] in BAD_STRICT_LABELS:
            add(row)

    # Ensure mda included if any bad label on narrative fields (optional coverage)
    for row in crows:
        if row["field"] == "mda" and row["strict_label"] in BAD_STRICT_LABELS:
            add(row)

    # Stable field order: schema order then extras
    order = [s.key for s in get_field_specs(schema)]
    ordered = [chosen[fk] for fk in order if fk in chosen]
    for fk, row in sorted(chosen.items()):
        if fk not in order:
            ordered.append(row)
    return ordered


def build_worksheet_rows(
    selected: dict[str, list[str]],
    stats: dict[str, dict],
    out_dir: str,
) -> list[dict]:
    out: list[dict] = []
    for subtype in ("bank", "broker", "insurer", "other_financial"):
        for code in selected.get(subtype, []):
            st = stats[code]
            pdf = _pdf_path(out_dir, code, st["board"])
            for row in _fields_for_company(st["rows"], st["schema_profile"]):
                out.append({
                    "code": code,
                    "name": st["name"],
                    "board": st["board"],
                    "schema_profile": st["schema_profile"],
                    "subtype_caveat_flag": code in SUBTYPE_CAVEAT_CODES,
                    "field": row["field"],
                    "extraction_type": row["extraction_type"],
                    "status": row["status"],
                    "proxy_plausible": row["proxy_plausible"],
                    "automated_strict_label": row["strict_label"],
                    "automated_reason": row["reason"],
                    "value_preview": row["value_preview"],
                    "evidence_sentence": row["evidence_sentence"],
                    "page": row["page"],
                    "source_url": row["source_url"],
                    "pdf_path": pdf if os.path.isfile(pdf) else "",
                    "manual_grade": "",
                    "manual_notes": "",
                    "reviewer": "",
                    "reviewed_at": "",
                })
    return out


def write_csv(path: str, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(GRADE_LEGEND + "\n")
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({
                **r,
                "proxy_plausible": r["proxy_plausible"],
                "subtype_caveat_flag": r["subtype_caveat_flag"],
            })


def cmd_generate(out_dir: str, yaml_path: str, seed: int) -> int:
    pop_path = os.path.join(out_dir, "financial_audit_population.csv")
    if not os.path.isfile(pop_path):
        print(f"[fin_calib] missing {pop_path}; run strict_audit_financial_full_market.py first",
              file=sys.stderr)
        return 2

    population = load_population(pop_path)
    stats = _company_stats(population)
    selected = select_companies(stats, seed)
    worksheet = build_worksheet_rows(selected, stats, out_dir)

    out_csv = os.path.join(out_dir, "financial_audit_sample.csv")
    write_csv(out_csv, worksheet)

    all_codes = [c for sub in selected.values() for c in sub]
    print(f"[fin_calib] selected companies: {len(all_codes)}")
    for sub, codes in selected.items():
        print(f"  {sub}: {len(codes)} -> {', '.join(codes)}")
    print(f"[fin_calib] worksheet cells: {len(worksheet)}")
    print(f"[fin_calib] wrote {out_csv}")
    return 0


def cmd_score(path: str) -> int:
    with open(path, encoding="utf-8-sig") as fh:
        lines = [ln for ln in fh if not ln.startswith("#")]
    rows = list(csv.DictReader(lines))
    graded = [r for r in rows if (r.get("manual_grade") or "").strip().upper() in GRADES]
    if not graded:
        print(f"[fin_calib] no graded rows (use one of {GRADES})", file=sys.stderr)
        return 2
    for r in graded:
        r["_g"] = r["manual_grade"].strip().upper()
        r["_auto"] = (r.get("automated_strict_label") or "").strip()
        r["_proxy"] = str(r.get("proxy_plausible", "")).strip().lower() in ("true", "1")

    agree_auto = sum(
        1 for r in graded
        if (r["_g"] == "CORRECT" and r["_auto"] == "usable")
        or (r["_g"] in ("PARTIAL", "CORRECT") and r["_auto"] == "partial")
        or (r["_g"] == "WRONG" and r["_auto"] == "wrong")
        or (r["_g"] == "MISSED" and r["_auto"] == "not_found_missed")
        or (r["_g"] == "ABSENT-OK" and r["_auto"] == "not_found_unverified")
    )
    print(f"[fin_calib] graded {len(graded)}/{len(rows)} rows")
    print(f"[fin_calib] manual vs automated strict agreement (heuristic): "
          f"{agree_auto}/{len(graded)} ({100*agree_auto/len(graded):.0f}%)")
    print(f"[fin_calib] grade distribution: {dict(Counter(r['_g'] for r in graded))}")
    by_field = Counter(r["field"] for r in graded if r["_g"] in ("WRONG", "MISSED"))
    if by_field:
        print(f"[fin_calib] fields with WRONG/MISSED: {dict(by_field.most_common(10))}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Financial manual calibration worksheet")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--companies-yaml", default=DEFAULT_YAML)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--generate", action="store_true", help="generate worksheet (default)")
    ap.add_argument("--score", default="", help="score a filled worksheet CSV")
    args = ap.parse_args()
    if args.score:
        return cmd_score(args.score)
    return cmd_generate(args.out_dir, args.companies_yaml, args.seed)


if __name__ == "__main__":
    raise SystemExit(main())
