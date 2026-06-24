"""Scoped rnd_investment refresh over full_market_2024 cached PDFs.

Re-extracts ONLY rnd_investment from existing PDFs; updates company_profile.json
and batch eval_results.json rnd field. Does not download PDFs or re-run full eval.

See outputs/generalization/full_market_2024/rnd_refresh_changes.csv for audit trail.

Safety:
  - --apply without --codes requires --confirm-full (blocks accidental full runs).
  - Progress is logged before each company (flush=True).
  - Per-company try/except prevents one bad PDF from aborting the batch.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import traceback
from datetime import datetime, timezone

import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.eval_generalize import field_plausible  # noqa: E402
from lab.extract_annual_report import compute_regions, extract_field, parse_pages  # noqa: E402
from lab.field_schema import get_field_specs  # noqa: E402

DEFAULT_OUT = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
DEFAULT_YAML = os.path.join(_PROJECT_ROOT, "lab", "eval_companies_full_market_2024.yaml")
DEFAULT_BOARDS = ["bse", "star", "szse_main", "chinext", "sse_main"]
RND_REFRESH_TAG = "rnd_refresh_20260624"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_yaml(path: str) -> list[dict]:
    data = yaml.safe_load(open(path, encoding="utf-8")) or {}
    return data.get("companies", [])


def _load_batch_eval(out_dir: str, board: str) -> list[dict]:
    path = os.path.join(out_dir, board, "eval_results.json")
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _save_batch_eval(out_dir: str, board: str, rows: list[dict], *, backup: bool) -> None:
    path = os.path.join(out_dir, board, "eval_results.json")
    if backup and os.path.isfile(path):
        bak = path + f".bak.{RND_REFRESH_TAG}"
        if not os.path.isfile(bak):
            shutil.copy2(path, bak)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)


def _serialize_value(v) -> str:
    if v is None:
        return ""
    if isinstance(v, dict):
        labeled = v.get("labeled") or []
        if labeled:
            return json.dumps(labeled[0], ensure_ascii=False)
        return json.dumps(v, ensure_ascii=False)[:200]
    return str(v)[:200]


def _profile_counts(fields: list[dict]) -> dict:
    return {
        "found": sum(1 for f in fields if f.get("status") == "found"),
        "partial": sum(1 for f in fields if f.get("status") == "partial"),
        "not_found": sum(1 for f in fields if f.get("status") == "not_found"),
        "total": len(fields),
    }


def _find_rnd_spec(schema_profile: str):
    specs = get_field_specs(schema_profile)
    for s in specs:
        if s.key == "rnd_investment":
            return s
    return None


def _company_paths(out_dir: str, code: str, board: str) -> dict:
    base = os.path.join(out_dir, board, code)
    return {
        "dir": base,
        "pdf": os.path.join(base, f"{code}.pdf"),
        "profile": os.path.join(base, "company_profile.json"),
        "cache": os.path.join(base, ".cache"),
    }


def _load_ok_codes(out_dir: str, boards: list[str], *, codes: set[str] | None) -> dict[str, dict]:
    """code -> eval row. When codes is set, only load matching rows from batch files."""
    by_code: dict[str, dict] = {}
    for board in boards:
        for row in _load_batch_eval(out_dir, board):
            code = str(row["stock_code"]).strip()
            if codes and code not in codes:
                continue
            row["_board"] = board
            by_code[code] = row
    return by_code


def _get_batch_rows(out_dir: str, board: str, cache: dict[str, list[dict]]) -> list[dict]:
    if board not in cache:
        cache[board] = _load_batch_eval(out_dir, board)
    return cache[board]


def refresh_rnd(
    out_dir: str,
    companies_yaml: str,
    *,
    dry_run: bool = True,
    limit: int | None = None,
    start_after: str | None = None,
    codes: set[str] | None = None,
    changes_csv: str,
) -> dict:
    out_dir = os.path.abspath(out_dir)
    companies = _load_yaml(companies_yaml)
    ok_by_code = _load_ok_codes(out_dir, DEFAULT_BOARDS, codes=codes)

    targets: list[tuple[str, str, dict]] = []
    for c in companies:
        code = str(c.get("stock_code", "")).strip()
        board = c.get("board") or ok_by_code.get(code, {}).get("_board", "")
        if not code or not board:
            continue
        if codes and code not in codes:
            continue
        if start_after and code <= start_after:
            continue
        row = ok_by_code.get(code)
        if not row or row.get("status") != "ok":
            continue
        paths = _company_paths(out_dir, code, board)
        if not os.path.isfile(paths["pdf"]) or not os.path.isfile(paths["profile"]):
            continue
        targets.append((code, board, c))

    targets.sort(key=lambda x: x[0])
    if limit is not None:
        targets = targets[:limit]

    print(
        f"[rnd_refresh] starting {'DRY-RUN' if dry_run else 'APPLY'} "
        f"targets={len(targets)} codes={','.join(sorted(codes)) if codes else 'ALL'}",
        flush=True,
    )

    stats = {
        "targets": len(targets),
        "updated": 0,
        "unchanged": 0,
        "errors": 0,
        "not_found_to_found": 0,
        "found_to_not_found": 0,
        "status_changes": 0,
    }
    batch_rows_cache: dict[str, list[dict]] = {}
    batch_dirty: set[str] = set()
    change_rows: list[dict] = []

    for i, (code, board, _yaml_c) in enumerate(targets, 1):
        print(f"[rnd_refresh] [{i}/{len(targets)}] {code} ({board}) ...", flush=True)
        paths = _company_paths(out_dir, code, board)
        try:
            with open(paths["profile"], encoding="utf-8") as fh:
                profile = json.load(fh)
            schema = profile.get("schema_profile") or "industrial"
            spec = _find_rnd_spec(schema)
            if not spec:
                stats["errors"] += 1
                print(f"[rnd_refresh] [{i}/{len(targets)}] {code} SKIP no rnd spec", flush=True)
                continue

            old_fields = profile.get("fields") or []
            old_rnd = next((f for f in old_fields if f.get("field") == "rnd_investment"), None)
            if not old_rnd:
                stats["errors"] += 1
                print(f"[rnd_refresh] [{i}/{len(targets)}] {code} SKIP no rnd field", flush=True)
                continue

            url = profile.get("source", {}).get("source_url") or ""
            pages, _ = parse_pages(paths["pdf"], paths["cache"])
            regions = compute_regions(pages)
            new_rnd = extract_field(spec, pages, paths["pdf"], url, regions)

            before_status = old_rnd.get("status", "")
            after_status = new_rnd.get("status", "")
            before_anchor = old_rnd.get("anchor_matched") or ""
            after_anchor = new_rnd.get("anchor_matched") or ""
            before_val = _serialize_value(old_rnd.get("value"))
            after_val = _serialize_value(new_rnd.get("value"))

            changed = (
                before_status != after_status
                or before_anchor != after_anchor
                or before_val != after_val
            )

            change_rows.append({
                "company_code": code,
                "board": board,
                "before_status": before_status,
                "after_status": after_status,
                "before_anchor": before_anchor,
                "after_anchor": after_anchor,
                "before_value": before_val,
                "after_value": after_val,
                "changed": changed,
                "dry_run": dry_run,
            })

            print(
                f"[rnd_refresh] [{i}/{len(targets)}] {code} "
                f"{before_status} -> {after_status} anchor={after_anchor!r}",
                flush=True,
            )

            if not changed:
                stats["unchanged"] += 1
                continue

            stats["status_changes"] += 1
            if before_status != "found" and after_status == "found":
                stats["not_found_to_found"] += 1
            elif before_status == "found" and after_status != "found":
                stats["found_to_not_found"] += 1

            if dry_run:
                stats["updated"] += 1
                continue

            new_fields = []
            for f in old_fields:
                if f.get("field") == "rnd_investment":
                    new_fields.append(new_rnd)
                else:
                    new_fields.append(f)
            profile["fields"] = new_fields
            profile["field_counts"] = _profile_counts(new_fields)
            profile["rnd_refresh"] = {"tag": RND_REFRESH_TAG, "at": _now()}

            bak_profile = paths["profile"] + f".bak.{RND_REFRESH_TAG}"
            if not os.path.isfile(bak_profile):
                shutil.copy2(paths["profile"], bak_profile)
            with open(paths["profile"], "w", encoding="utf-8") as fh:
                json.dump(profile, fh, ensure_ascii=False, indent=2)

            rows = _get_batch_rows(out_dir, board, batch_rows_cache)
            for row in rows:
                if str(row["stock_code"]).strip() != code:
                    continue
                flds = row.setdefault("fields", {})
                plausible = field_plausible(new_rnd)
                old_finfo = flds.get("rnd_investment") or {}
                old_plausible = old_finfo.get("plausible", False)
                flds["rnd_investment"] = {
                    "status": new_rnd.get("status"),
                    "in_region": new_rnd.get("in_region"),
                    "page": new_rnd.get("page"),
                    "plausible": plausible,
                }
                if old_finfo.get("status") != new_rnd.get("status"):
                    if old_finfo.get("status") == "found":
                        row["found"] = max(0, row.get("found", 0) - 1)
                    elif old_finfo.get("status") == "partial":
                        row["partial"] = max(0, row.get("partial", 0) - 1)
                    elif old_finfo.get("status") == "not_found":
                        row["not_found"] = max(0, row.get("not_found", 0) - 1)
                    st = new_rnd.get("status")
                    if st == "found":
                        row["found"] = row.get("found", 0) + 1
                    elif st == "partial":
                        row["partial"] = row.get("partial", 0) + 1
                    elif st == "not_found":
                        row["not_found"] = row.get("not_found", 0) + 1
                if old_plausible != plausible:
                    row["plausible"] = (
                        row.get("plausible", 0)
                        + (1 if plausible else 0)
                        - (1 if old_plausible else 0)
                    )
                break

            batch_dirty.add(board)
            stats["updated"] += 1

        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            change_rows.append({
                "company_code": code,
                "board": board,
                "before_status": "",
                "after_status": "",
                "before_anchor": "",
                "after_anchor": "",
                "before_value": "",
                "after_value": "",
                "changed": False,
                "dry_run": dry_run,
                "error": str(exc),
            })
            print(f"[rnd_refresh] ERROR {code}: {exc}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)

    if not dry_run:
        for board in batch_dirty:
            _save_batch_eval(out_dir, board, batch_rows_cache[board], backup=True)

    os.makedirs(os.path.dirname(changes_csv) or ".", exist_ok=True)
    fields = [
        "company_code", "board", "before_status", "after_status",
        "before_anchor", "after_anchor", "before_value", "after_value",
        "changed", "dry_run", "error",
    ]
    with open(changes_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in change_rows:
            w.writerow({k: r.get(k, "") for k in fields})

    stats["batch_files_updated"] = len(batch_dirty)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scoped rnd_investment refresh over full_market_2024 cached PDFs",
    )
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--companies-yaml", default=DEFAULT_YAML)
    ap.add_argument("--dry-run", action="store_true",
                    help="preview changes without writing profiles or eval_results")
    ap.add_argument("--apply", action="store_true",
                    help="write changes (requires --codes or --confirm-full)")
    ap.add_argument("--confirm-full", action="store_true",
                    help="explicitly allow --apply over all ok companies (slow; ~1-2h)")
    ap.add_argument("--limit", type=int, default=0, help="max companies to process (0=all)")
    ap.add_argument("--start-after", default="",
                    help="process codes strictly greater than this stock code")
    ap.add_argument("--codes", default="",
                    help="comma-separated stock codes (required for --apply unless --confirm-full)")
    ap.add_argument("--changes-csv", default="",
                    help="change log path (default: out-dir/rnd_refresh_changes.csv)")
    args = ap.parse_args()

    if args.apply and args.dry_run:
        print("[rnd_refresh] use --dry-run OR --apply, not both", file=sys.stderr)
        return 2
    if not args.apply and not args.dry_run:
        print("[rnd_refresh] specify --dry-run (preview) or --apply (write)", file=sys.stderr)
        return 2

    codes = {c.strip() for c in args.codes.split(",") if c.strip()} or None

    if args.apply and not codes and not args.confirm_full:
        print(
            "[rnd_refresh] REFUSED: --apply without --codes would touch ~5700 profiles.\n"
            "  Use --codes CODE1,CODE2,... for targeted refresh, or\n"
            "  add --confirm-full only after reviewing targeted results.",
            file=sys.stderr,
        )
        return 2

    if args.confirm_full and not args.apply:
        print("[rnd_refresh] --confirm-full requires --apply", file=sys.stderr)
        return 2

    changes_csv = args.changes_csv or os.path.join(args.out_dir, "rnd_refresh_changes.csv")

    stats = refresh_rnd(
        args.out_dir,
        args.companies_yaml,
        dry_run=not args.apply,
        limit=args.limit if args.limit > 0 else None,
        start_after=args.start_after.strip() or None,
        codes=codes,
        changes_csv=changes_csv,
    )

    mode = "DRY-RUN" if not args.apply else "APPLIED"
    print(f"[rnd_refresh] {mode} complete", flush=True)
    for k, v in stats.items():
        print(f"  {k}: {v}", flush=True)
    print(f"  changes_csv: {changes_csv}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
