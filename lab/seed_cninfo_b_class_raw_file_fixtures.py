"""
Seed B-class raw_file metadata fixtures from b_document fixtures.

Reads fixtures/b_class/document/*.jsonl (read-only), derives one raw_file row per
document with pdf_url. Does NOT download PDF, does NOT request CNINFO.

Usage:
    python lab/seed_cninfo_b_class_raw_file_fixtures.py
    python lab/seed_cninfo_b_class_raw_file_fixtures.py --input fixtures/b_class/document/periodic_report_document_fixtures.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_INPUT = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "periodic_report_document_fixtures.jsonl"
)
DEFAULT_OUTPUT = os.path.join(
    BASE_DIR, "fixtures", "b_class", "raw_file", "periodic_report_raw_file_fixtures.jsonl"
)

CREATED_FROM = "b_document_fixture_seed"
MIME_TYPE = "application/pdf"
NOTES = "metadata only; PDF not downloaded"


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def raw_file_id_for(document_id: str) -> str:
    return f"raw_file_{document_id}"


def derive_raw_file(document: Dict[str, Any]) -> Dict[str, Any]:
    document_id = document["document_id"]
    return {
        "raw_file_id": raw_file_id_for(document_id),
        "document_id": document_id,
        "source_url": document["pdf_url"],
        "download_status": "not_started",
        "sha256_candidate": None,
        "mime_type": MIME_TYPE,
        "file_size_candidate": None,
        "storage_uri_candidate": None,
        "fetch_time": None,
        "created_from": CREATED_FROM,
        "notes": NOTES,
    }


def process_documents(
    documents: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int]:
    fixtures: List[Dict[str, Any]] = []
    skipped = 0
    for doc in documents:
        pdf_url = (doc.get("pdf_url") or "").strip()
        if not pdf_url:
            skipped += 1
            continue
        fixtures.append(derive_raw_file(doc))
    return fixtures, skipped


def write_jsonl(path: str, records: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed B-class raw_file fixtures from document fixtures")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    documents = load_jsonl(args.input)
    fixtures, skipped = process_documents(documents)
    write_jsonl(args.output, fixtures)

    print(
        f"SUMMARY  total_documents={len(documents)}  "
        f"raw_file_seeded={len(fixtures)}  skipped_missing_source_url={skipped}"
    )
    print(f"JSONL {args.output}")
    sys.exit(0)


if __name__ == "__main__":
    main()
