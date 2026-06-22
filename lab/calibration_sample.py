"""Manual calibration sampler for the eval200 'plausible' proxy.

The generalization eval scores each field with an AUTOMATIC proxy (`field_plausible`
in lab/eval_generalize.py): status=found + a value-shape check. That proxy is fast
and free but unverified. This tool draws a SMALL, REPRODUCIBLE, STRATIFIED sample of
(company, field) cells so a human can grade them against the cited PDF page, and then
measures how well the proxy agrees with human judgement.

Two modes:

  generate (default)
    Reads outputs/.../eval_results.json + each company_profile.json, samples cells,
    and writes a worksheet (CSV + Markdown). Stratified to include BOTH:
      - proxy_plausible=True cells  -> measures proxy PRECISION (false positives), and
      - proxy_plausible=False cells -> measures proxy MISS rate (false negatives).
    The positive sample is spread across fields so easy fields don't dominate.

  --score FILLED.csv
    Reads the worksheet after the `manual_grade` column is filled in with one of
    {CORRECT, PARTIAL, WRONG, MISSED, ABSENT-OK} and prints a calibration summary
    (proxy precision, false-positive rate, false-negative/missed-field rate split
    by cause, partial-but-usable count, and field-level error patterns) so the
    headline % can be trusted.

  Grade semantics (positive = the target field is present & extractable):
    CORRECT    field correctly extracted (full).
    PARTIAL    right region/some content, incomplete.
    WRONG      extracted content points to the wrong place / not this field.
    MISSED     extractor returned not_found / nothing usable, BUT the field
               actually exists in the report (a recall false-negative).
    ABSENT-OK  not_found is the correct answer (field genuinely N/A; no data invented).

Bounded by design: defaults to 40 graded cells. Deterministic via --seed.
Company values come from the eval data only; nothing company-specific is hard-coded.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
from collections import defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

GRADES = ("CORRECT", "PARTIAL", "WRONG", "MISSED", "ABSENT-OK")

CSV_COLUMNS = [
    "id", "stock_code", "short_name", "field", "label_cn", "extraction", "region",
    "proxy_status", "proxy_in_region", "proxy_plausible", "page", "source_url",
    "evidence_sentence", "value_preview", "manual_grade", "notes",
]


def value_preview(field: dict, limit: int = 160) -> str:
    """Render a short, single-line human preview of a field value by its type."""
    v = field.get("value")
    if v is None:
        return ""
    if isinstance(v, str):
        text = v
    elif isinstance(v, dict) and "labeled" in v:  # numeric
        pairs = "; ".join(f"{p.get('label')}={p.get('value')}" for p in v.get("labeled", []))
        text = pairs or v.get("context", "")
    elif isinstance(v, dict) and "ratio" in v:  # concentration
        text = f"amount={v.get('amount') or 'n/a'} ratio={v.get('ratio') or 'n/a'} :: {v.get('sentence', '')}"
    elif isinstance(v, dict) and "rows" in v:  # table
        rows = v.get("rows", [])
        head = " / ".join(" | ".join(r) for r in rows[:2])
        text = f"[table p.{v.get('table_page')} {v.get('n_rows')} rows, hits={v.get('match_hits')}] {head}"
    elif isinstance(v, dict):  # table snippet fallback
        text = f"{v.get('note', '')}: {v.get('snippet', '')}"
    else:
        text = str(v)
    text = " ".join(text.split())  # collapse whitespace/newlines for CSV
    return text[:limit]


def load_cells(eval_dir: str) -> list[dict]:
    """Build one record per (OK company, field) with proxy flags + evidence."""
    results = json.load(open(os.path.join(eval_dir, "eval_results.json"), encoding="utf-8"))
    cells: list[dict] = []
    for r in results:
        if r.get("status") != "ok":
            continue
        code = r["stock_code"]
        prof_path = os.path.join(eval_dir, code, "company_profile.json")
        if not os.path.exists(prof_path):
            continue
        prof = json.load(open(prof_path, encoding="utf-8"))
        by_field = {f["field"]: f for f in prof.get("fields", [])}
        for fkey, meta in r.get("fields", {}).items():
            pf = by_field.get(fkey, {})
            cells.append({
                "stock_code": code,
                "short_name": r.get("short_name", ""),
                "field": fkey,
                "label_cn": pf.get("label_cn", ""),
                "extraction": pf.get("extraction", ""),
                "region": pf.get("region", ""),
                "proxy_status": meta.get("status", ""),
                "proxy_in_region": meta.get("in_region", ""),
                "proxy_plausible": bool(meta.get("plausible")),
                "page": pf.get("page", meta.get("page")),
                "source_url": pf.get("source_url", prof.get("source", {}).get("source_url", "")),
                "evidence_sentence": " ".join((pf.get("evidence_sentence") or "").split())[:200],
                "value_preview": value_preview(pf),
            })
    return cells


def stratified_sample(cells: list[dict], n: int, frac_plausible: float, seed: int) -> list[dict]:
    rng = random.Random(seed)
    pos = [c for c in cells if c["proxy_plausible"]]
    neg = [c for c in cells if not c["proxy_plausible"]]
    n_pos = min(len(pos), round(n * frac_plausible))
    n_neg = min(len(neg), n - n_pos)
    n_pos = min(len(pos), n - n_neg)  # backfill if neg is scarce

    # Positives: spread across fields (round-robin over shuffled per-field buckets)
    # so the easy 99% fields don't crowd out the harder ones.
    buckets: dict[str, list[dict]] = defaultdict(list)
    for c in pos:
        buckets[c["field"]].append(c)
    for b in buckets.values():
        rng.shuffle(b)
    pos_pick: list[dict] = []
    fields_cycle = sorted(buckets.keys())
    while len(pos_pick) < n_pos and any(buckets[f] for f in fields_cycle):
        for f in fields_cycle:
            if buckets[f] and len(pos_pick) < n_pos:
                pos_pick.append(buckets[f].pop())

    neg_pick = rng.sample(neg, n_neg) if n_neg else []
    sample = pos_pick + neg_pick
    rng.shuffle(sample)
    for i, c in enumerate(sample, 1):
        c["id"] = i
        c["manual_grade"] = ""
        c["notes"] = ""
    return sample


def write_worksheet(sample: list[dict], out_csv: str, out_md: str) -> None:
    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for c in sample:
            w.writerow(c)

    pos = sum(1 for c in sample if c["proxy_plausible"])
    lines = [
        "# Manual Calibration Worksheet - eval200 'plausible' proxy",
        "",
        f"_Sample: {len(sample)} cells ({pos} proxy-plausible, {len(sample)-pos} not). "
        "Fixed seed -> reproducible._",
        "",
        "## How to grade",
        "",
        "For each row, open `source_url`, go to `page`, and compare against `evidence_sentence` "
        "/ `value_preview`. Put one grade in `manual_grade` (in the CSV):",
        "",
        "- **CORRECT** - right field content located.",
        "- **PARTIAL** - right region but messy/incomplete/mislocated table.",
        "- **WRONG** - extracted content points to the wrong place / not this field.",
        "- **MISSED** - extractor returned not_found/nothing usable, but the field DOES exist "
        "in the report (recall false-negative).",
        "- **ABSENT-OK** - `not_found` is the correct answer (field genuinely N/A; no data invented).",
        "",
        "Then run `python lab/calibration_sample.py --score <filled.csv>` for the summary.",
        "",
        "| id | code | field | proxy_status | plausible | page | evidence (preview) |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in sample:
        ev = (c["evidence_sentence"] or c["value_preview"] or "").replace("|", "/")[:80]
        lines.append(
            f"| {c['id']} | {c['stock_code']} | {c['field']} | {c['proxy_status']} | "
            f"{'Y' if c['proxy_plausible'] else 'N'} | {c['page']} | {ev} |"
        )
    lines.append("")
    open(out_md, "w", encoding="utf-8").write("\n".join(lines))


def cmd_generate(args) -> int:
    cells = load_cells(args.eval_dir)
    if not cells:
        print(f"[calib] no cells found under {args.eval_dir}", file=sys.stderr)
        return 2
    sample = stratified_sample(cells, args.n, args.frac_plausible, args.seed)
    out_csv = args.out or os.path.join(args.eval_dir, "calibration_sample.csv")
    out_md = os.path.splitext(out_csv)[0] + ".md"
    write_worksheet(sample, out_csv, out_md)
    pos = sum(1 for c in sample if c["proxy_plausible"])
    by_field = defaultdict(int)
    for c in sample:
        by_field[c["field"]] += 1
    print(f"[calib] universe: {len(cells)} cells "
          f"({sum(c['proxy_plausible'] for c in cells)} plausible)")
    print(f"[calib] sampled {len(sample)} cells: {pos} plausible / {len(sample)-pos} not "
          f"(seed={args.seed})")
    print(f"[calib] field coverage: {dict(sorted(by_field.items()))}")
    print(f"[calib] worksheet -> {out_csv}")
    print(f"[calib] instructions -> {out_md}")
    print("[calib] Fill the `manual_grade` column, then: "
          f"python lab/calibration_sample.py --score {out_csv}")
    return 0


def _pct(a: int, b: int) -> str:
    return f"{100*a/b:.0f}%" if b else "n/a"


def _plausible_fraction(csv_path: str) -> tuple[int, int] | None:
    """Read eval_results.json next to the CSV to get population strata weights
    (how many of ALL (OK company, field) cells are proxy-plausible)."""
    eval_dir = os.path.dirname(os.path.abspath(csv_path))
    rp = os.path.join(eval_dir, "eval_results.json")
    if not os.path.exists(rp):
        return None
    results = json.load(open(rp, encoding="utf-8"))
    total = plausible = 0
    for r in results:
        if r.get("status") != "ok":
            continue
        for meta in r.get("fields", {}).values():
            total += 1
            plausible += 1 if meta.get("plausible") else 0
    return (plausible, total) if total else None


def cmd_score(path: str) -> int:
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))  # tolerate Excel BOM
    graded = [r for r in rows if (r.get("manual_grade") or "").strip().upper() in GRADES]
    if not graded:
        print(f"[calib] no graded rows in {path} (fill `manual_grade` with one of {GRADES})",
              file=sys.stderr)
        return 2
    for r in graded:
        r["_g"] = r["manual_grade"].strip().upper()
        r["_pos"] = (r.get("proxy_plausible", "").strip().lower() == "true")
        r["_status"] = (r.get("proxy_status") or "").strip().lower()

    Y = [r for r in graded if r["_pos"]]   # proxy called the cell plausible
    N = [r for r in graded if not r["_pos"]]

    # --- proxy_plausible = Y : measures precision / false positives ----------
    y_correct = [r for r in Y if r["_g"] == "CORRECT"]
    y_partial = [r for r in Y if r["_g"] == "PARTIAL"]
    y_wrong = [r for r in Y if r["_g"] == "WRONG"]
    y_anom = [r for r in Y if r["_g"] in ("MISSED", "ABSENT-OK")]  # shouldn't happen

    # --- proxy_plausible = N : measures false negatives / correct rejects ----
    n_missed = [r for r in N if r["_g"] == "MISSED"]                 # recall failure
    n_recover = [r for r in N if r["_g"] in ("CORRECT", "PARTIAL")]  # content was there
    n_absent = [r for r in N if r["_g"] == "ABSENT-OK"]
    n_wrong = [r for r in N if r["_g"] == "WRONG"]

    # A false negative = a rejected cell whose field was actually present, by
    # EITHER cause: missed (nothing usable returned) OR partial-but-usable
    # (content present but flagged low-confidence). These are NOT independent
    # of each other; partial-but-usable is one of the two FN causes.
    false_neg = n_missed + n_recover
    true_neg = n_absent + n_wrong
    partial_usable = [r for r in n_recover if r["_status"] == "partial"]

    nY, nN, nG = len(Y), len(N), len(graded)

    print(f"[calib] scored {nG} / {len(rows)} graded rows  (proxy_plausible: {nY} Y / {nN} N)\n")

    print("== Proxy-plausible cells (precision / false positives) ==")
    print(f"  n = {nY}")
    print(f"  precision (CORRECT only)         = {_pct(len(y_correct), nY)}  ({len(y_correct)}/{nY})")
    print(f"  precision (CORRECT or PARTIAL)   = {_pct(len(y_correct)+len(y_partial), nY)}")
    print(f"  FALSE-POSITIVE rate (WRONG)      = {_pct(len(y_wrong), nY)}  ({len(y_wrong)}/{nY})")
    if y_anom:
        print(f"  (!) {len(y_anom)} anomalous grades on plausible cells: "
              f"{[r['id'] for r in y_anom]}")

    print("\n== Proxy-rejected cells (false negatives / correct rejects) ==")
    print(f"  n = {nN}")
    print(f"  FALSE-NEGATIVE / missed-field rate = {_pct(len(false_neg), nN)}  ({len(false_neg)}/{nN})")
    print(f"    - cause A: missed (not_found, recall)        = {len(n_missed)}")
    print(f"    - cause B: partial-but-usable (proxy strict) = {len(partial_usable)}")
    other_recover = len(n_recover) - len(partial_usable)
    if other_recover:
        print(f"    - cause B': usable but status!=partial       = {other_recover}")
    print(f"  correct rejections (TN)            = {_pct(len(true_neg), nN)}  "
          f"({len(true_neg)}/{nN}: absent-ok={len(n_absent)}, wrong={len(n_wrong)})")

    print("\n== Partial-but-usable (recoverable by loosening the proxy) ==")
    print(f"  count = {len(partial_usable)}  ids = {[r['id'] for r in partial_usable]}")

    # Overall agreement: proxy decision matches manual reality.
    agree = len(y_correct) + len(true_neg)
    print(f"\n== Overall ==")
    print(f"  agreement (proxy decision correct) = {_pct(agree, nG)}  ({agree}/{nG})")
    from collections import Counter
    print(f"  grade distribution = {dict(Counter(r['_g'] for r in graded))}")

    # --- field-level error patterns -----------------------------------------
    fld: dict[str, dict] = defaultdict(lambda: {"fp": 0, "missed": 0, "recover": 0})
    for r in y_wrong:
        fld[r["field"]]["fp"] += 1
    for r in n_missed:
        fld[r["field"]]["missed"] += 1
    for r in n_recover:
        fld[r["field"]]["recover"] += 1
    print("\n== Field-level error patterns ==")
    if not fld:
        print("  (none)")
    else:
        print(f"  {'field':24} {'FP(wrong)':>10} {'missed':>8} {'recover':>8}")
        for f in sorted(fld, key=lambda k: -(fld[k]['fp']+fld[k]['missed']+fld[k]['recover'])):
            v = fld[f]
            print(f"  {f:24} {v['fp']:>10} {v['missed']:>8} {v['recover']:>8}")

    # --- calibrated population estimate (bonus, clearly labeled) -------------
    strata = _plausible_fraction(path)
    if strata:
        plausible, total = strata
        p = plausible / total
        prec = len(y_correct) / nY if nY else 0.0
        # Among rejected cells, the fraction whose content is actually correct
        # & usable now (graded CORRECT) -> recoverable signal in the rejected pool.
        rej_correct = sum(1 for r in N if r["_g"] == "CORRECT") / nN if nN else 0.0
        calibrated = p * prec + (1 - p) * rej_correct
        print("\n== Calibrated population estimate (sample reweighted to all cells) ==")
        print(f"  population plausible fraction p = {p:.1%} ({plausible}/{total} cells)")
        print(f"  est. fully-correct rate ~= p*precision + (1-p)*rejected-correct")
        print(f"                           ~= {p:.3f}*{prec:.2f} + {1-p:.3f}*{rej_correct:.2f} "
              f"= {calibrated:.0%}")
        print("  (vs the raw 'plausible' headline which assumes every plausible cell is correct)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Manual calibration sampler for the eval200 plausible proxy")
    ap.add_argument("--eval-dir", default=os.path.join(_ROOT, "outputs", "generalization", "eval200"))
    ap.add_argument("--n", type=int, default=40, help="number of cells to sample")
    ap.add_argument("--frac-plausible", type=float, default=0.6,
                    help="fraction of the sample drawn from proxy_plausible=True cells")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="", help="output CSV path (default: <eval-dir>/calibration_sample.csv)")
    ap.add_argument("--score", default="", help="score a FILLED worksheet CSV instead of generating one")
    args = ap.parse_args()
    if args.score:
        return cmd_score(args.score)
    return cmd_generate(args)


if __name__ == "__main__":
    raise SystemExit(main())
