"""Entry point / runner for the Listed Company Data Collector.

Reads companies.yaml + sources.yaml, then for every company-source pair runs the
matching category collector and writes exactly one coverage row (success OR
failure). Finally writes the coverage CSV and the markdown summary.

This is a validation prototype: it never bypasses login/captcha/paywall/anti-
crawling, stores metadata + source_url (and official filings) only, and records
failures rather than crashing.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

import yaml

from collectors.registry import get_collector
from utils.coverage import CoverageRow, write_csv
from utils.fetcher import Fetcher
from utils.llm import LLMClient
from utils.logger import get_logger
from utils.summary import build_summary

logger = get_logger("lcdc.main")

HERE = os.path.dirname(os.path.abspath(__file__))


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def merge_source_defaults(raw: dict) -> list[dict]:
    """Merge `defaults` into each source entry; explicit keys win."""
    defaults = raw.get("defaults", {}) or {}
    sources = raw.get("sources", []) or []
    merged: list[dict] = []
    for src in sources:
        entry = dict(defaults)
        entry.update({k: v for k, v in (src or {}).items() if v is not None})
        merged.append(entry)
    return merged


def valid_companies(raw: dict) -> list[dict]:
    """Return configured companies that have at least one identifying field."""
    out: list[dict] = []
    for c in raw.get("companies", []) or []:
        if not c:
            continue
        if any((c.get(k) or "").strip() for k in ("company_name", "short_name", "stock_code")):
            out.append(c)
        else:
            logger.warning("Skipping placeholder/empty company entry in companies.yaml")
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Listed company public-data source validation framework")
    p.add_argument("--companies", default=os.path.join(HERE, "config", "companies.yaml"))
    p.add_argument("--sources", default=os.path.join(HERE, "config", "sources.yaml"))
    p.add_argument("--output-dir", default=os.path.join(HERE, "outputs"))
    p.add_argument("--use-playwright", action="store_true", help="enable optional JS-render fallback")
    p.add_argument("--use-llm", action="store_true", help="enable optional LLM enrichment")
    p.add_argument("--llm-provider", default="", help="LLM provider id (provider wiring is a stub)")
    p.add_argument("--only-priority", default="", help="restrict to a priority, e.g. P0")
    p.add_argument("--throttle", type=float, default=1.0, help="seconds between requests per host")
    p.add_argument("--timeout", type=float, default=15.0, help="per-request timeout seconds")
    p.add_argument("--max-retries", type=int, default=1)
    return p.parse_args()


def main() -> int:
    args = parse_args()

    companies_raw = load_yaml(args.companies)
    sources_raw = load_yaml(args.sources)
    companies = valid_companies(companies_raw)
    sources = merge_source_defaults(sources_raw)

    if args.only_priority:
        sources = [s for s in sources if s.get("priority") == args.only_priority]

    os.makedirs(args.output_dir, exist_ok=True)
    raw_samples_dir = os.path.join(args.output_dir, "raw_samples")
    os.makedirs(raw_samples_dir, exist_ok=True)

    fetcher = Fetcher(
        timeout=args.timeout,
        max_retries=args.max_retries,
        throttle_seconds=args.throttle,
        enable_playwright=args.use_playwright,
    )
    llm = LLMClient(enabled=args.use_llm, provider=args.llm_provider)

    logger.info(
        "Validating %d company(ies) x %d source(s) = %d pairs",
        len(companies), len(sources), len(companies) * len(sources),
    )

    rows: list[CoverageRow] = []
    samples: list[dict] = []
    for company in companies:
        for source in sources:
            category = source.get("category", "")
            collector = get_collector(category, fetcher, llm)
            try:
                row = collector.collect(company, source)
            except Exception as exc:  # noqa: BLE001 - guarantee one row per pair
                logger.exception("collector crashed for %s/%s", company.get("short_name"), source.get("name"))
                row = collector.new_row(company, source)
                row.fetch_status = "failure"
                row.failure_reason = f"collector_exception: {type(exc).__name__}: {exc}"
                row.recommended_next_step = "Investigate collector error; see logs."
                row.source_url = source.get("base_url", "")
            rows.append(row)
            samples.append(
                {
                    "company": company.get("short_name") or company.get("company_name"),
                    "source": row.data_source,
                    "category": row.data_category,
                    "source_url": row.source_url,
                    "fetch_status": row.fetch_status,
                    "title": row.title,
                    "sample_result": row.sample_result,
                    "extracted_fields": row.extracted_fields,
                }
            )

    csv_path = os.path.join(args.output_dir, "source_coverage.csv")
    write_csv(rows, csv_path)
    logger.info("Wrote %d rows -> %s", len(rows), csv_path)

    summary_md = build_summary(rows, companies, sources)
    summary_path = os.path.join(args.output_dir, "coverage_summary.md")
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write(summary_md)
    logger.info("Wrote summary -> %s", summary_path)

    # Save small traceability samples (titles/links/snippets only, no full text).
    if samples:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        sample_path = os.path.join(raw_samples_dir, f"samples_{stamp}.jsonl")
        with open(sample_path, "w", encoding="utf-8") as fh:
            for s in samples:
                fh.write(json.dumps(s, ensure_ascii=False) + "\n")
        logger.info("Wrote %d samples -> %s", len(samples), sample_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
