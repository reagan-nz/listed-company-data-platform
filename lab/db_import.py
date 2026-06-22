"""Import eval outputs into SQLite v1 prototype.

Reads eval_results.json + per-company company_profile.json from an eval
directory (default: outputs/generalization/eval1000). Does not touch the
extraction pipeline.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.db_init import DEFAULT_DB_PATH, connect_db, create_schema  # noqa: E402

DEFAULT_EVAL_DIR = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "eval1000")
DEFAULT_COMPANIES_YAML = os.path.join(_PROJECT_ROOT, "lab", "eval_companies_1000.yaml")
EXTRACTION_VERSION = "v1-prototype"
DEFAULT_REPORT_YEAR = 2024


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _infer_report_year(title: str | None) -> int:
    if not title:
        return DEFAULT_REPORT_YEAR
    m = re.search(r"(20\d{2})", title)
    return int(m.group(1)) if m else DEFAULT_REPORT_YEAR


def _load_company_meta(yaml_path: str) -> dict[str, dict]:
    if not os.path.exists(yaml_path):
        return {}
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    out: dict[str, dict] = {}
    for c in data.get("companies", []):
        code = str(c.get("stock_code", "")).strip()
        if code:
            out[code] = c
    return out


def _load_profile(profile_path: str) -> tuple[dict | None, str | None]:
    """Return (profile, error). error is set when file exists but cannot be read."""
    if not os.path.exists(profile_path):
        return None, None
    try:
        with open(profile_path, encoding="utf-8") as f:
            return json.load(f), None
    except (json.JSONDecodeError, OSError) as exc:
        return None, str(exc)


def _status_maps(eval_status: str) -> tuple[str, str, int]:
    """Return (download_status, parse_status, text_layer_ok)."""
    if eval_status == "ok":
        return "ok", "ok", 1
    if eval_status == "no_text_layer":
        return "ok", "no_text_layer", 0
    if eval_status == "no_announcement":
        return "no_announcement", "skipped", 0
    if eval_status == "no_orgid":
        return "no_orgid", "skipped", 0
    return "error", "error", 0


def _serialize_value(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def _in_region_value(raw) -> int | None:
    if raw is None:
        return None
    return 1 if raw else 0


def import_eval(
    eval_dir: str,
    db_path: str,
    *,
    run_name: str,
    limit: int | None = None,
    companies_yaml: str = DEFAULT_COMPANIES_YAML,
    extraction_version: str = EXTRACTION_VERSION,
    report_year: int | None = None,
) -> dict[str, int]:
    """Import a sample from eval_dir into db_path. Returns row counts."""
    eval_dir = os.path.abspath(eval_dir)
    create_schema(db_path)

    results_path = os.path.join(eval_dir, "eval_results.json")
    if not os.path.exists(results_path):
        raise FileNotFoundError(f"eval_results.json not found under {eval_dir}")

    with open(results_path, encoding="utf-8") as f:
        results = json.load(f)
    if limit is not None:
        results = results[:limit]

    meta_by_code = _load_company_meta(companies_yaml)
    ts = _now()
    counts = {"company_basic": 0, "report_source": 0, "extracted_field": 0, "evaluation_result": 0}
    profile_errors = 0

    conn = connect_db(db_path)
    try:
        for row in results:
            code = str(row["stock_code"]).strip()
            yaml_row = meta_by_code.get(code, {})
            company_name = row.get("short_name") or yaml_row.get("short_name") or code
            exchange = row.get("exchange") or yaml_row.get("exchange") or ""
            board = yaml_row.get("board") or ""
            is_financial = 1 if (row.get("financial") or yaml_row.get("financial")) else 0

            conn.execute(
                """INSERT INTO company_basic (
                       company_code, company_name, exchange, board, is_financial,
                       listing_status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(company_code) DO UPDATE SET
                       company_name=excluded.company_name,
                       exchange=excluded.exchange,
                       board=excluded.board,
                       is_financial=excluded.is_financial,
                       updated_at=excluded.updated_at""",
                (code, company_name, exchange, board, is_financial, "listed", ts, ts),
            )
            counts["company_basic"] += 1

            title = row.get("picked_title") or ""
            yr = report_year or _infer_report_year(title)
            dl, parse, text_ok = _status_maps(row.get("status") or "error")
            source_url = row.get("source_url") or ""

            profile_path = os.path.join(eval_dir, code, "company_profile.json")
            prof, prof_err = _load_profile(profile_path)
            if prof_err:
                profile_errors += 1
                print(f"[db_import] WARN skip profile {code}: {prof_err}", file=sys.stderr)

            pdf_sha256 = None
            if prof:
                src = prof.get("source") or {}
                pdf_sha256 = src.get("pdf_sha256")
                if not title:
                    title = src.get("report_title") or title
                if not source_url:
                    source_url = src.get("source_url") or source_url

            conn.execute(
                """INSERT INTO report_source (
                       company_code, report_year, report_title, source_url, pdf_sha256,
                       download_status, parse_status, text_layer_ok, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(company_code, report_year) DO UPDATE SET
                       report_title=excluded.report_title,
                       source_url=excluded.source_url,
                       pdf_sha256=excluded.pdf_sha256,
                       download_status=excluded.download_status,
                       parse_status=excluded.parse_status,
                       text_layer_ok=excluded.text_layer_ok,
                       updated_at=excluded.updated_at""",
                (code, yr, title, source_url, pdf_sha256, dl, parse, text_ok, ts, ts),
            )
            counts["report_source"] += 1

            if prof:
                for f in prof.get("fields", []):
                    conn.execute(
                        """INSERT INTO extracted_field (
                               company_code, report_year, field_name, field_label_cn, value,
                               status, page, evidence_sentence, source_url,
                               in_region, anchor_matched,
                               extraction_version, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           ON CONFLICT(company_code, report_year, field_name, extraction_version)
                           DO UPDATE SET
                               field_label_cn=excluded.field_label_cn,
                               value=excluded.value,
                               status=excluded.status,
                               page=excluded.page,
                               evidence_sentence=excluded.evidence_sentence,
                               source_url=excluded.source_url,
                               in_region=excluded.in_region,
                               anchor_matched=excluded.anchor_matched,
                               updated_at=excluded.updated_at""",
                        (
                            code,
                            yr,
                            f.get("field", ""),
                            f.get("label_cn", ""),
                            _serialize_value(f.get("value")),
                            f.get("status", "not_found"),
                            f.get("page"),
                            f.get("evidence_sentence", ""),
                            f.get("source_url") or source_url,
                            _in_region_value(f.get("in_region")),
                            f.get("anchor_matched"),
                            extraction_version,
                            ts,
                        ),
                    )
                    counts["extracted_field"] += 1

            for field_name, finfo in (row.get("fields") or {}).items():
                conn.execute(
                    """INSERT INTO evaluation_result (
                           run_name, company_code, report_year, field_name, proxy_plausible,
                           strict_audit_result, notes, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(run_name, company_code, report_year, field_name) DO UPDATE SET
                           proxy_plausible=excluded.proxy_plausible,
                           created_at=excluded.created_at""",
                    (
                        run_name,
                        code,
                        yr,
                        field_name,
                        1 if finfo.get("plausible") else 0,
                        None,
                        None,
                        ts,
                    ),
                )
                counts["evaluation_result"] += 1

        conn.commit()
    finally:
        conn.close()

    if profile_errors:
        counts["profile_errors"] = profile_errors
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="Import eval outputs into SQLite v1 prototype")
    ap.add_argument("--eval-dir", default=DEFAULT_EVAL_DIR)
    ap.add_argument("--db", default=DEFAULT_DB_PATH)
    ap.add_argument("--run-name", default="eval1000")
    ap.add_argument("--limit", type=int, default=10,
                    help="max companies to import (default 10 for prototype)")
    ap.add_argument("--companies-yaml", default=DEFAULT_COMPANIES_YAML)
    ap.add_argument("--extraction-version", default=EXTRACTION_VERSION)
    ap.add_argument("--report-year", type=int, default=0,
                    help="override report year (0 = infer from title)")
    args = ap.parse_args()

    counts = import_eval(
        args.eval_dir,
        args.db,
        run_name=args.run_name,
        limit=args.limit if args.limit > 0 else None,
        companies_yaml=args.companies_yaml,
        extraction_version=args.extraction_version,
        report_year=args.report_year or None,
    )
    print(f"[db_import] imported from {args.eval_dir} -> {os.path.abspath(args.db)}")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
