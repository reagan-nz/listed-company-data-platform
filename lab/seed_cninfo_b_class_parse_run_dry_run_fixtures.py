"""
Seed B-class document_parse_run dry-run fixtures from document + raw_file metadata.

Reads document JSONL fixtures (read-only), joins periodic raw_file by document_id,
writes parse_run dry-run JSONL + seed report. Does NOT parse PDF.

Usage:
    python lab/seed_cninfo_b_class_parse_run_dry_run_fixtures.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_PERIODIC_DOCS = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "periodic_report_document_fixtures.jsonl"
)
DEFAULT_NON_PERIODIC_DOCS = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "non_periodic_document_fixtures.jsonl"
)
DEFAULT_PERIODIC_RAW = os.path.join(
    BASE_DIR, "fixtures", "b_class", "raw_file", "periodic_report_raw_file_fixtures.jsonl"
)
DEFAULT_OUTPUT = os.path.join(
    BASE_DIR, "fixtures", "b_class", "parse_run", "document_parse_run_dry_run_fixtures.jsonl"
)
DEFAULT_REPORT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_parse_run_dry_run_report.csv"
)

PARSER_NAME = "dry_run_no_parser"
PARSER_VERSION = "draft-0.1"
CREATED_FROM = "b_class_parse_run_dry_run_seed"

PERIODIC_NOTES = (
    "raw file metadata exists; PDF not downloaded; parser not started"
)
NON_PERIODIC_NOTES = (
    "title-only offline fixture; no pdf_url; parse skipped"
)


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_raw_file_map(path: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for row in load_jsonl(path):
        doc_id = row.get("document_id")
        raw_id = row.get("raw_file_id")
        if doc_id and raw_id:
            mapping[doc_id] = raw_id
    return mapping


def parse_run_id_for(document_id: str) -> str:
    return f"parse_run_{document_id}"


def build_parse_run(
    document: Dict[str, Any],
    document_group: str,
    raw_file_map: Dict[str, str],
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    document_id = (document.get("document_id") or "").strip()
    if not document_id:
        return {}, {
            "parse_run_id": "",
            "document_id": "",
            "document_group": document_group,
            "raw_file_available": "no",
            "parse_status": "",
            "seed_status": "skipped_missing_document_id",
            "notes": "missing document_id",
        }

    if document_group == "periodic":
        raw_file_id = raw_file_map.get(document_id)
        parse_status = "not_started"
        notes = PERIODIC_NOTES
        raw_available = "yes" if raw_file_id else "no"
        if not raw_file_id:
            notes += "; raw_file_id not found in periodic raw_file fixtures"
    else:
        raw_file_id = None
        parse_status = "skipped"
        notes = NON_PERIODIC_NOTES
        raw_available = "no"

    parse_run = {
        "parse_run_id": parse_run_id_for(document_id),
        "document_id": document_id,
        "raw_file_id": raw_file_id,
        "parser_name": PARSER_NAME,
        "parser_version": PARSER_VERSION,
        "parse_status": parse_status,
        "page_count": None,
        "text_length": None,
        "error_message": None,
        "created_at": None,
        "created_from": CREATED_FROM,
        "notes": notes,
    }

    report_row = {
        "parse_run_id": parse_run["parse_run_id"],
        "document_id": document_id,
        "document_group": document_group,
        "raw_file_available": raw_available,
        "parse_status": parse_status,
        "seed_status": "seeded",
        "notes": notes,
    }
    return parse_run, report_row


def process_documents(
    periodic_docs: List[Dict[str, Any]],
    non_periodic_docs: List[Dict[str, Any]],
    raw_file_map: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    parse_runs: List[Dict[str, Any]] = []
    report_rows: List[Dict[str, str]] = []

    for doc in periodic_docs:
        pr, row = build_parse_run(doc, "periodic", raw_file_map)
        if row["seed_status"] == "seeded":
            parse_runs.append(pr)
        report_rows.append(row)

    for doc in non_periodic_docs:
        pr, row = build_parse_run(doc, "non_periodic", raw_file_map)
        if row["seed_status"] == "seeded":
            parse_runs.append(pr)
        report_rows.append(row)

    return parse_runs, report_rows


def write_jsonl(path: str, records: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_report_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "parse_run_id", "document_id", "document_group", "raw_file_available",
        "parse_status", "seed_status", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed parse_run dry-run fixtures")
    parser.add_argument("--periodic-documents", default=DEFAULT_PERIODIC_DOCS)
    parser.add_argument("--non-periodic-documents", default=DEFAULT_NON_PERIODIC_DOCS)
    parser.add_argument("--periodic-raw-files", default=DEFAULT_PERIODIC_RAW)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--output-csv", default=DEFAULT_REPORT_CSV)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    periodic_docs = load_jsonl(args.periodic_documents)
    non_periodic_docs = load_jsonl(args.non_periodic_documents)
    raw_file_map = load_raw_file_map(args.periodic_raw_files)

    parse_runs, report_rows = process_documents(
        periodic_docs, non_periodic_docs, raw_file_map
    )
    write_jsonl(args.output, parse_runs)
    write_report_csv(args.output_csv, report_rows)

    total = len(periodic_docs) + len(non_periodic_docs)
    seeded = len(parse_runs)
    print(f"SUMMARY  total_documents={total}  parse_run_seeded={seeded}")
    print(f"JSONL {args.output}")
    print(f"CSV   {args.output_csv}")
    sys.exit(0)


if __name__ == "__main__":
    main()
