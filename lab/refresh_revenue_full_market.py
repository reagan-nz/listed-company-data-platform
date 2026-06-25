"""Scoped revenue table refresh over full_market_2024 cached PDFs.

Re-extracts ONLY revenue_by_region and revenue_by_segment from existing PDFs;
updates company_profile.json and batch eval_results.json on --apply only.

See outputs/generalization/full_market_2024/revenue_refresh_changes.csv for audit trail.

Safety:
  - Default mode is --dry-run (no writes).
  - --apply without --codes requires --confirm-full (blocks accidental full runs).
  - --dry-run --confirm-full previews all ok companies without writing.
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
from lab.extract_annual_report import (  # noqa: E402
    _table_row_is_data_row,
    compute_regions,
    extract_field,
    parse_pages,
)
from lab.field_schema import get_field_specs  # noqa: E402
from lab.strict_audit_full_market import strict_audit_field  # noqa: E402

DEFAULT_OUT = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
DEFAULT_YAML = os.path.join(_PROJECT_ROOT, "lab", "eval_companies_full_market_2024.yaml")
DEFAULT_BOARDS = ["bse", "star", "szse_main", "chinext", "sse_main"]
REVENUE_REFRESH_TAG = "revenue_refresh_20260624"
REVENUE_FIELDS = ("revenue_by_region", "revenue_by_segment")


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
        bak = path + f".bak.{REVENUE_REFRESH_TAG}"
        if not os.path.isfile(bak):
            shutil.copy2(path, bak)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)


def _profile_counts(fields: list[dict]) -> dict:
    return {
        "found": sum(1 for f in fields if f.get("status") == "found"),
        "partial": sum(1 for f in fields if f.get("status") == "partial"),
        "not_found": sum(1 for f in fields if f.get("status") == "not_found"),
        "total": len(fields),
    }


def _find_revenue_specs(schema_profile: str) -> dict[str, object]:
    specs = get_field_specs(schema_profile)
    out = {}
    for key in REVENUE_FIELDS:
        for s in specs:
            if s.key == key:
                out[key] = s
                break
    return out


def _company_paths(out_dir: str, code: str, board: str) -> dict:
    base = os.path.join(out_dir, board, code)
    return {
        "dir": base,
        "pdf": os.path.join(base, f"{code}.pdf"),
        "profile": os.path.join(base, "company_profile.json"),
        "cache": os.path.join(base, ".cache"),
    }


def _load_ok_codes(out_dir: str, boards: list[str], *, codes: set[str] | None) -> dict[str, dict]:
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


def _field_metrics(f: dict | None) -> dict:
    if not f:
        return {
            "status": "", "strict": "", "row_count": 0, "data_row_count": 0,
            "table_page": "", "continuation_page": "", "stitched": "", "preview_trimmed": "",
        }
    val = f.get("value") or {}
    rows = val.get("rows") or []
    return {
        "status": f.get("status") or "",
        "strict": strict_audit_field(f)[0],
        "row_count": len(rows),
        "data_row_count": sum(1 for r in rows if _table_row_is_data_row(r)),
        "table_page": val.get("table_page") if val.get("table_page") is not None else (f.get("page") or ""),
        "continuation_page": val.get("continuation_page") or "",
        "stitched": val.get("stitched") if val.get("stitched") is not None else "",
        "preview_trimmed": val.get("preview_trimmed") if val.get("preview_trimmed") is not None else "",
    }


def _field_changed(old_f: dict, new_f: dict) -> bool:
    om, nm = _field_metrics(old_f), _field_metrics(new_f)
    keys = ("status", "strict", "row_count", "data_row_count", "table_page",
            "continuation_page", "stitched", "preview_trimmed")
    return any(om[k] != nm[k] for k in keys)


def _update_eval_row(row: dict, key: str, new_f: dict) -> None:
    flds = row.setdefault("fields", {})
    plausible = field_plausible(new_f)
    old_finfo = flds.get(key) or {}
    old_plausible = old_finfo.get("plausible", False)
    flds[key] = {
        "status": new_f.get("status"),
        "in_region": new_f.get("in_region"),
        "page": new_f.get("page"),
        "plausible": plausible,
    }
    if old_finfo.get("status") != new_f.get("status"):
        if old_finfo.get("status") == "found":
            row["found"] = max(0, row.get("found", 0) - 1)
        elif old_finfo.get("status") == "partial":
            row["partial"] = max(0, row.get("partial", 0) - 1)
        elif old_finfo.get("status") == "not_found":
            row["not_found"] = max(0, row.get("not_found", 0) - 1)
        st = new_f.get("status")
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


def _change_row(
    code: str, board: str, key: str, old_f: dict, new_f: dict, *, dry_run: bool,
) -> dict:
    om, nm = _field_metrics(old_f), _field_metrics(new_f)
    changed = _field_changed(old_f, new_f)
    return {
        "company_code": code,
        "board": board,
        "field": key,
        "before_status": om["status"],
        "after_status": nm["status"],
        "before_strict": om["strict"],
        "after_strict": nm["strict"],
        "before_row_count": om["row_count"],
        "after_row_count": nm["row_count"],
        "before_data_row_count": om["data_row_count"],
        "after_data_row_count": nm["data_row_count"],
        "before_table_page": om["table_page"],
        "after_table_page": nm["table_page"],
        "before_continuation_page": om["continuation_page"],
        "after_continuation_page": nm["continuation_page"],
        "before_stitched": om["stitched"],
        "after_stitched": nm["stitched"],
        "before_preview_trimmed": om["preview_trimmed"],
        "after_preview_trimmed": nm["preview_trimmed"],
        "changed": changed,
        "dry_run": dry_run,
    }


CSV_FIELDS = [
    "company_code", "board", "field",
    "before_status", "after_status",
    "before_strict", "after_strict",
    "before_row_count", "after_row_count",
    "before_data_row_count", "after_data_row_count",
    "before_table_page", "after_table_page",
    "before_continuation_page", "after_continuation_page",
    "before_stitched", "after_stitched",
    "before_preview_trimmed", "after_preview_trimmed",
    "changed", "dry_run", "error",
]


def refresh_revenue(
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
        f"[revenue_refresh] starting {'DRY-RUN' if dry_run else 'APPLY'} "
        f"targets={len(targets)} codes={','.join(sorted(codes)) if codes else 'ALL'}",
        flush=True,
    )

    stats = {
        "targets": len(targets),
        "companies_changed": 0,
        "companies_unchanged": 0,
        "field_updates": 0,
        "region_changed": 0,
        "segment_changed": 0,
        "errors": 0,
        "wrong_to_usable": 0,
        "partial_to_usable": 0,
        "usable_to_partial": 0,
        "usable_to_wrong": 0,
        "stitched_after": 0,
        "preview_trimmed_after": 0,
    }
    batch_rows_cache: dict[str, list[dict]] = {}
    batch_dirty: set[str] = set()
    change_rows: list[dict] = []

    for i, (code, board, _yaml_c) in enumerate(targets, 1):
        print(f"[revenue_refresh] [{i}/{len(targets)}] {code} ({board}) ...", flush=True)
        paths = _company_paths(out_dir, code, board)
        try:
            with open(paths["profile"], encoding="utf-8") as fh:
                profile = json.load(fh)
            schema = profile.get("schema_profile") or "industrial"
            specs = _find_revenue_specs(schema)
            if len(specs) != len(REVENUE_FIELDS):
                stats["errors"] += 1
                print(f"[revenue_refresh] [{i}/{len(targets)}] {code} SKIP missing revenue specs", flush=True)
                continue

            old_fields = profile.get("fields") or []
            old_by_key = {f.get("field"): f for f in old_fields if f.get("field") in REVENUE_FIELDS}
            if not old_by_key:
                stats["errors"] += 1
                print(f"[revenue_refresh] [{i}/{len(targets)}] {code} SKIP no revenue fields", flush=True)
                continue

            url = profile.get("source", {}).get("source_url") or ""
            pages, _ = parse_pages(paths["pdf"], paths["cache"])
            regions = compute_regions(pages)

            company_changed = False
            new_by_key: dict[str, dict] = {}
            for key in REVENUE_FIELDS:
                old_f = old_by_key.get(key)
                if not old_f:
                    continue
                new_f = extract_field(specs[key], pages, paths["pdf"], url, regions)
                new_by_key[key] = new_f
                row = _change_row(code, board, key, old_f, new_f, dry_run=dry_run)
                change_rows.append(row)

                if not row["changed"]:
                    continue

                company_changed = True
                stats["field_updates"] += 1
                if key == "revenue_by_region":
                    stats["region_changed"] += 1
                else:
                    stats["segment_changed"] += 1

                bs, asl = row["before_strict"], row["after_strict"]
                if bs == "wrong" and asl == "usable":
                    stats["wrong_to_usable"] += 1
                elif bs == "partial" and asl == "usable":
                    stats["partial_to_usable"] += 1
                elif bs == "usable" and asl == "partial":
                    stats["usable_to_partial"] += 1
                elif bs == "usable" and asl == "wrong":
                    stats["usable_to_wrong"] += 1

                if row["after_stitched"] is True or row["after_stitched"] == "True":
                    stats["stitched_after"] += 1
                if row["after_preview_trimmed"] is True or row["after_preview_trimmed"] == "True":
                    stats["preview_trimmed_after"] += 1

                print(
                    f"[revenue_refresh] [{i}/{len(targets)}] {code} {key} "
                    f"{row['before_status']}->{row['after_status']} "
                    f"strict {bs}->{asl} data {row['before_data_row_count']}->{row['after_data_row_count']}",
                    flush=True,
                )

            if not company_changed:
                stats["companies_unchanged"] += 1
                continue

            stats["companies_changed"] += 1
            if dry_run:
                continue

            new_fields = []
            for f in old_fields:
                key = f.get("field")
                new_fields.append(new_by_key[key] if key in new_by_key else f)
            profile["fields"] = new_fields
            profile["field_counts"] = _profile_counts(new_fields)
            profile["revenue_refresh"] = {"tag": REVENUE_REFRESH_TAG, "at": _now()}

            bak_profile = paths["profile"] + f".bak.{REVENUE_REFRESH_TAG}"
            if not os.path.isfile(bak_profile):
                shutil.copy2(paths["profile"], bak_profile)
            with open(paths["profile"], "w", encoding="utf-8") as fh:
                json.dump(profile, fh, ensure_ascii=False, indent=2)

            rows = _get_batch_rows(out_dir, board, batch_rows_cache)
            for erow in rows:
                if str(erow["stock_code"]).strip() != code:
                    continue
                for key in REVENUE_FIELDS:
                    if key in new_by_key:
                        _update_eval_row(erow, key, new_by_key[key])
                break

            batch_dirty.add(board)

        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            for key in REVENUE_FIELDS:
                err_row = {k: "" for k in CSV_FIELDS}
                err_row.update({
                    "company_code": code,
                    "board": board,
                    "field": key,
                    "changed": False,
                    "dry_run": dry_run,
                    "error": str(exc),
                })
                change_rows.append(err_row)
            print(f"[revenue_refresh] ERROR {code}: {exc}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)

    if not dry_run:
        for board in batch_dirty:
            _save_batch_eval(out_dir, board, batch_rows_cache[board], backup=True)

    os.makedirs(os.path.dirname(changes_csv) or ".", exist_ok=True)
    with open(changes_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in change_rows:
            w.writerow({k: r.get(k, "") for k in CSV_FIELDS})

    stats["batch_files_updated"] = len(batch_dirty)
    stats["changes_csv"] = changes_csv
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scoped revenue table refresh over full_market_2024 cached PDFs",
    )
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--companies-yaml", default=DEFAULT_YAML)
    ap.add_argument("--dry-run", action="store_true",
                    help="preview changes without writing (default when --apply omitted)")
    ap.add_argument("--apply", action="store_true",
                    help="write changes (requires --codes or --confirm-full)")
    ap.add_argument("--confirm-full", action="store_true",
                    help="process all ok companies (dry-run preview or apply with writes)")
    ap.add_argument("--limit", type=int, default=0, help="max companies to process (0=all)")
    ap.add_argument("--start-after", default="",
                    help="process codes strictly greater than this stock code")
    ap.add_argument("--codes", default="",
                    help="comma-separated stock codes")
    ap.add_argument("--changes-csv", default="",
                    help="change log path (default: out-dir/revenue_refresh_changes.csv)")
    args = ap.parse_args()

    dry_run = not args.apply
    if args.apply and args.dry_run:
        # --apply wins over default dry-run flag
        dry_run = False

    codes = {c.strip() for c in args.codes.split(",") if c.strip()} or None

    if not codes and not args.confirm_full:
        print(
            "[revenue_refresh] REFUSED: specify --codes CODE1,CODE2,... or --confirm-full "
            "to process more than zero companies.",
            file=sys.stderr,
        )
        return 2

    if args.apply and not codes and not args.confirm_full:
        print(
            "[revenue_refresh] REFUSED: --apply without --codes requires --confirm-full.",
            file=sys.stderr,
        )
        return 2

    changes_csv = args.changes_csv or os.path.join(args.out_dir, "revenue_refresh_changes.csv")

    stats = refresh_revenue(
        args.out_dir,
        args.companies_yaml,
        dry_run=dry_run,
        limit=args.limit if args.limit > 0 else None,
        start_after=args.start_after.strip() or None,
        codes=codes,
        changes_csv=changes_csv,
    )

    mode = "DRY-RUN" if dry_run else "APPLIED"
    print(f"[revenue_refresh] {mode} complete", flush=True)
    for k, v in stats.items():
        print(f"  {k}: {v}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
