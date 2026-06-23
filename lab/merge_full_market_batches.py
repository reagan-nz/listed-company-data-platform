"""Merge full_market_2024 board batch outputs for db_import compatibility.

Reads per-board eval_results.json under out_dir/{board}/, merges to
out_dir/eval_results.json, writes eval_summary.md, creates root-level
symlinks out_dir/{code} -> {board}/{code} so db_import finds
company_profile.json at eval_dir/{code}/company_profile.json.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.eval_generalize import write_summary  # noqa: E402
from lab.field_schema import FIELD_SPECS, resolve_profile  # noqa: E402

DEFAULT_BOARDS = ["bse", "star", "szse_main", "chinext", "sse_main"]
DEFAULT_OUT = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
KEY_FIELDS = ("rnd_investment", "revenue_by_region", "revenue_by_segment")


def _infer_schema_profile(r: dict) -> str:
    if r.get("schema_profile"):
        return r["schema_profile"]
    if r.get("financial"):
        return resolve_profile([], short_name=r.get("short_name", ""), financial=True)
    return "industrial"


def load_batch_results(
    out_dir: str,
    boards: list[str],
) -> tuple[list[dict], dict[str, str]]:
    """Load and merge batch eval_results.json. Returns (results, code -> board)."""
    out_dir = os.path.abspath(out_dir)
    by_code: dict[str, dict] = {}
    code_board: dict[str, str] = {}

    for board in boards:
        path = os.path.join(out_dir, board, "eval_results.json")
        if not os.path.exists(path):
            print(f"[merge] skip missing {path}", file=sys.stderr)
            continue
        with open(path, encoding="utf-8") as fh:
            rows = json.load(fh)
        print(f"[merge] {board}: {len(rows)} rows")
        for row in rows:
            code = str(row["stock_code"]).strip()
            if code in by_code:
                print(
                    f"[merge] WARN duplicate {code}: replacing {code_board[code]} with {board}",
                    file=sys.stderr,
                )
            by_code[code] = row
            code_board[code] = board

    if not by_code:
        raise FileNotFoundError(f"no batch eval_results.json found under {out_dir}")

    # Stable order: board sequence, then stock code within board
    board_order = {b: i for i, b in enumerate(boards)}
    results = sorted(
        by_code.values(),
        key=lambda r: (board_order.get(code_board[r["stock_code"]], 99), r["stock_code"]),
    )
    return results, code_board


def link_company_dirs(
    out_dir: str,
    code_board: dict[str, str],
    *,
    require_profile: bool = False,
) -> tuple[int, int, int]:
    """Create root symlinks {code} -> {board}/{code}. Returns (linked, skipped, missing)."""
    out_dir = os.path.abspath(out_dir)
    linked = skipped = missing = 0

    for code, board in sorted(code_board.items()):
        src = os.path.join(out_dir, board, code)
        profile = os.path.join(src, "company_profile.json")
        link = os.path.join(out_dir, code)

        if require_profile and not os.path.isfile(profile):
            missing += 1
            continue

        if not os.path.isdir(src):
            missing += 1
            continue

        rel_target = os.path.join(board, code)
        if os.path.islink(link):
            if os.readlink(link) == rel_target:
                skipped += 1
                continue
            os.unlink(link)
        elif os.path.exists(link):
            print(f"[merge] WARN skip {code}: {link} exists and is not a symlink", file=sys.stderr)
            skipped += 1
            continue

        os.symlink(rel_target, link)
        linked += 1

    return linked, skipped, missing


def write_full_market_summary(
    results: list[dict],
    code_board: dict[str, str],
    path: str,
) -> None:
    """Write full_market_2024_summary.md with headline metrics."""
    status = Counter(r["status"] for r in results)
    ok = [r for r in results if r["status"] == "ok"]
    nonfin = [r for r in ok if not r.get("financial")]
    fin = [r for r in ok if r.get("financial")]
    board_counts = Counter(code_board.get(r["stock_code"], "?") for r in results)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    L: list[str] = []
    a = L.append
    a("# full_market_2024 Summary")
    a("")
    a(f"_Generated: {ts} | total companies: {len(results)}_")
    a("")
    a("## Status counts")
    a("")
    a("| status | count | pct |")
    a("|---|---:|---:|")
    for st, cnt in sorted(status.items(), key=lambda x: -x[1]):
        a(f"| {st} | {cnt} | {100 * cnt / len(results):.1f}% |")
    a("")
    a(f"- **ok**: {len(ok)} ({100 * len(ok) / len(results):.1f}%)")
    a(f"- non-financial ok: {len(nonfin)}")
    a(f"- financial ok: {len(fin)}")
    a("")
    a("## Board counts (from batch merge)")
    a("")
    a("| board | count |")
    a("|---|---:|")
    for board in DEFAULT_BOARDS:
        if board_counts.get(board):
            a(f"| {board} | {board_counts[board]} |")
    if board_counts.get("?"):
        a(f"| unknown | {board_counts['?']} |")
    a("")
    if nonfin:
        mean_proxy = statistics.mean(r["plausible"] for r in nonfin)
        a("## Non-financial proxy (headline)")
        a("")
        a(f"- Mean plausible: **{mean_proxy:.2f} / 11** (n={len(nonfin)})")
        a("- Reference: eval1000_v2 **10.33/11**; independent **10.30/11**")
        a("")
        a("## Key field plausible rates (non-financial)")
        a("")
        a("| field | plausible | rate |")
        a("|---|---:|---:|")
        for field in KEY_FIELDS:
            p = sum(1 for r in nonfin if r.get("fields", {}).get(field, {}).get("plausible"))
            rate = 100 * p / len(nonfin) if nonfin else 0
            a(f"| {field} | {p}/{len(nonfin)} | {rate:.1f}% |")
        a("")
    if fin:
        subtypes = Counter(_infer_schema_profile(r) for r in fin)
        a("## Financial subtypes (ok)")
        a("")
        a("| subtype | count |")
        a("|---|---:|")
        for st, cnt in sorted(subtypes.items(), key=lambda x: -x[1]):
            a(f"| {st} | {cnt} |")
        a("")
    a("## Notes")
    a("")
    a("- strict-usable not re-run on full_market_2024.")
    a("- Root symlinks `{code}` -> `{board}/{code}` enable db_import profile lookup.")
    a("- Re-run this merge after error retries or batch re-runs.")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")


def merge_batches(
    out_dir: str,
    boards: list[str] | None = None,
    *,
    link_profiles: bool = True,
    require_profile: bool = False,
) -> dict:
    """Merge batches; write eval_results.json, eval_summary.md, full_market summary."""
    boards = boards or DEFAULT_BOARDS
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    results, code_board = load_batch_results(out_dir, boards)

    eval_path = os.path.join(out_dir, "eval_results.json")
    with open(eval_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2)
    print(f"[merge] wrote {eval_path} ({len(results)} rows)")

    summary_path = os.path.join(out_dir, "eval_summary.md")
    write_summary(results, summary_path)
    print(f"[merge] wrote {summary_path}")

    fm_summary_path = os.path.join(out_dir, "full_market_2024_summary.md")
    write_full_market_summary(results, code_board, fm_summary_path)
    print(f"[merge] wrote {fm_summary_path}")

    stats = {"total": len(results), "linked": 0, "skipped": 0, "missing": 0}
    if link_profiles:
        linked, skipped, missing = link_company_dirs(
            out_dir, code_board, require_profile=require_profile
        )
        stats.update(linked=linked, skipped=skipped, missing=missing)
        print(f"[merge] symlinks: linked={linked} skipped={skipped} missing={missing}")

    return stats


def run_self_test() -> None:
    """Minimal merge + db_import path check in a temp directory."""
    with tempfile.TemporaryDirectory(prefix="fm_merge_test_") as tmp:
        boards_data = {
            "bse": [
                {"stock_code": "920001", "short_name": "T1", "status": "ok",
                 "financial": False, "plausible": 10, "found": 10, "fields": {
                     "rnd_investment": {"plausible": True},
                     "revenue_by_region": {"plausible": True},
                     "revenue_by_segment": {"plausible": False},
                 }, "industry": "test"},
            ],
            "star": [
                {"stock_code": "688001", "short_name": "T2", "status": "ok",
                 "financial": True, "schema_profile": "broker", "plausible": 8,
                 "found": 8, "fields": {}, "industry": "broker"},
                {"stock_code": "688002", "short_name": "T3", "status": "no_announcement",
                 "financial": False, "plausible": 0, "found": 0, "fields": {}, "industry": ""},
            ],
        }
        for board, rows in boards_data.items():
            bdir = os.path.join(tmp, board)
            os.makedirs(bdir, exist_ok=True)
            with open(os.path.join(bdir, "eval_results.json"), "w", encoding="utf-8") as fh:
                json.dump(rows, fh)
            for row in rows:
                if row["status"] != "ok":
                    continue
                cdir = os.path.join(bdir, row["stock_code"])
                os.makedirs(cdir, exist_ok=True)
                prof = {"source": {"report_title": "2024年年度报告"}, "fields": [
                    {"field": "mda", "label_cn": "MDA", "status": "found",
                     "value": "x" * 30, "page": 1, "evidence_sentence": "ev",
                     "source_url": "http://example.com", "in_region": True},
                ]}
                with open(os.path.join(cdir, "company_profile.json"), "w", encoding="utf-8") as fh:
                    json.dump(prof, fh)

        stats = merge_batches(tmp, ["bse", "star"], link_profiles=True)
        assert stats["total"] == 3
        assert stats["linked"] == 2

        link = os.path.join(tmp, "920001")
        assert os.path.islink(link)
        assert os.readlink(link) == os.path.join("bse", "920001")
        prof_path = os.path.join(tmp, "920001", "company_profile.json")
        assert os.path.isfile(prof_path), prof_path

        from lab.db_import import import_eval  # noqa: E402

        db_path = os.path.join(tmp, "test.db")
        counts = import_eval(tmp, db_path, run_name="test_merge", limit=None,
                             companies_yaml=os.path.join(tmp, "missing.yaml"))
        assert counts["company_basic"] == 3
        assert counts["extracted_field"] == 2  # two ok profiles with one field each
        print("[self-test] PASS")


def main() -> int:
    ap = argparse.ArgumentParser(description="Merge full_market_2024 board batches")
    ap.add_argument("--out-dir", default=DEFAULT_OUT,
                    help="full_market_2024 root directory")
    ap.add_argument("--boards", nargs="+", default=DEFAULT_BOARDS,
                    help="board subdirs to merge (order preserved)")
    ap.add_argument("--no-symlinks", action="store_true",
                    help="skip creating root company dir symlinks")
    ap.add_argument("--require-profile", action="store_true",
                    help="only symlink when company_profile.json exists")
    ap.add_argument("--self-test", action="store_true",
                    help="run temp-dir self test and exit")
    args = ap.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    merge_batches(
        args.out_dir,
        args.boards,
        link_profiles=not args.no_symlinks,
        require_profile=args.require_profile,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
