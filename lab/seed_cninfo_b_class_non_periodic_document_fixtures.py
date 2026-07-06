"""
Seed B-class non-periodic document metadata fixtures from known-document benchmark YAML.

Reads fixtures/b_class/known_documents/known_document_benchmark.yaml (read-only),
writes non_periodic document JSONL + seed report. Does NOT request CNINFO.

Usage:
    python lab/seed_cninfo_b_class_non_periodic_document_fixtures.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_BENCHMARK = os.path.join(
    BASE_DIR, "fixtures", "b_class", "known_documents", "known_document_benchmark.yaml"
)
DEFAULT_DOCUMENT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "non_periodic_document_fixtures.jsonl"
)
DEFAULT_RAW_FILE_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "b_class", "raw_file", "non_periodic_raw_file_fixtures.jsonl"
)
DEFAULT_SEED_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_non_periodic_document_seed_report.csv"
)

CREATED_FROM = "offline_known_document_benchmark"
PERIODIC_ROUTE = "cninfo_periodic_report_pdf"
PERIODIC_DOCUMENT_TYPES = frozenset({
    "annual_report",
    "semi_annual_report",
    "quarterly_report_q1",
    "quarterly_report_q3",
})
ALLOWED_DOCUMENT_TYPES = frozenset({
    "inquiry_reply",
    "regulatory_inquiry",
    "meeting_notice",
    "investor_relations_activity",
    "board_resolution",
    "shareholder_meeting_material",
    "announcement",
    "other",
})
NOTES = (
    "offline title fixture only; no CNINFO request; no PDF URL; "
    "not real retrieval coverage"
)


def load_benchmark(path: str) -> List[Dict[str, Any]]:
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit("PyYAML required: pip install pyyaml") from exc
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return list(data.get("documents") or [])


def document_id_for(benchmark_id: str, source_id: str, title: str) -> str:
    key = f"{benchmark_id}|{source_id}|{title}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


def build_document(entry: Dict[str, Any]) -> Dict[str, Any]:
    benchmark_id = entry["benchmark_id"]
    source_id = entry["expected_route_to"]
    document_type = entry["expected_document_type"]
    title = entry["title"]

    raw_metadata = {
        "benchmark_row": {
            k: entry.get(k)
            for k in (
                "benchmark_id", "company_code", "company_name", "title",
                "expected_route_to", "expected_document_type", "expected_classification",
                "benchmark_group", "notes",
            )
        }
    }

    doc: Dict[str, Any] = {
        "document_id": document_id_for(benchmark_id, source_id, title),
        "source_id": source_id,
        "company_code": entry.get("company_code"),
        "company_name": entry.get("company_name"),
        "org_id": None,
        "title": title,
        "document_type": document_type,
        "report_period": None,
        "announcement_date": None,
        "pdf_url": None,
        "retrieval_status": "found",
        "classification_status": "classified_correctly",
        "classification_confidence": "medium",
        "source_confidence": "candidate",
        "raw_metadata_json": raw_metadata,
        "created_from": CREATED_FROM,
        "created_at": None,
        "notes": NOTES,
    }
    if entry.get("notes"):
        doc["notes"] += f"; benchmark: {entry['notes']}"
    return doc


def classify_entry(entry: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any] | None]:
    """Return (seed_status, skip_notes, document_or_none)."""
    benchmark_id = entry.get("benchmark_id", "")
    route = (entry.get("expected_route_to") or "").strip()
    doc_type = (entry.get("expected_document_type") or "").strip()
    group = (entry.get("benchmark_group") or "").strip()

    if not route:
        return "skipped_missing_expected_route", "missing expected_route_to", None

    if route == PERIODIC_ROUTE or group == "periodic_report" or doc_type in PERIODIC_DOCUMENT_TYPES:
        return "skipped_periodic", f"periodic benchmark ({doc_type})", None

    if doc_type not in ALLOWED_DOCUMENT_TYPES:
        return "skipped_unknown_document_type", f"unknown document_type: {doc_type}", None

    return "seeded", "", build_document(entry)


def process_benchmark(entries: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    documents: List[Dict[str, Any]] = []
    report_rows: List[Dict[str, str]] = []

    for entry in entries:
        benchmark_id = entry.get("benchmark_id", "")
        seed_status, skip_notes, doc = classify_entry(entry)
        route = entry.get("expected_route_to", "")
        doc_type = entry.get("expected_document_type", "")
        title = entry.get("title", "")

        row = {
            "seed_id": benchmark_id,
            "benchmark_id": benchmark_id,
            "source_id": route or "",
            "title": title,
            "document_type": doc_type,
            "retrieval_status": "found" if doc else "",
            "classification_status": "classified_correctly" if doc else "",
            "pdf_url_available": "no",
            "seed_status": seed_status,
            "notes": skip_notes or NOTES,
        }
        report_rows.append(row)
        if doc is not None:
            documents.append(doc)

    return documents, report_rows


def write_jsonl(path: str, records: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_seed_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "seed_id", "benchmark_id", "source_id", "title", "document_type",
        "retrieval_status", "classification_status", "pdf_url_available",
        "seed_status", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed non-periodic B-class document fixtures")
    parser.add_argument("--benchmark", default=DEFAULT_BENCHMARK)
    parser.add_argument("--output-documents", default=DEFAULT_DOCUMENT_FIXTURES)
    parser.add_argument("--output-raw-files", default=DEFAULT_RAW_FILE_FIXTURES)
    parser.add_argument("--output-csv", default=DEFAULT_SEED_CSV)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries = load_benchmark(args.benchmark)
    documents, report_rows = process_benchmark(entries)

    write_jsonl(args.output_documents, documents)
    write_jsonl(args.output_raw_files, [])  # empty: no pdf_url
    write_seed_csv(args.output_csv, report_rows)

    seeded = sum(1 for r in report_rows if r["seed_status"] == "seeded")
    skipped_periodic = sum(1 for r in report_rows if r["seed_status"] == "skipped_periodic")
    print(
        f"SUMMARY  benchmark_total={len(entries)}  seeded={seeded}  "
        f"skipped_periodic={skipped_periodic}"
    )
    print(f"JSONL {args.output_documents}")
    print(f"RAW   {args.output_raw_files} (empty)")
    print(f"CSV   {args.output_csv}")
    sys.exit(0)


if __name__ == "__main__":
    main()
