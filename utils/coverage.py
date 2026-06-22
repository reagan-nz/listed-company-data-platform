"""Coverage row model and CSV writer.

`CoverageRow` is the single output contract of the whole framework. Every
company-source pair produces exactly one row, success or failure. The field
order here is authoritative and matches the CSV header required by the spec.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone

# Authoritative CSV column order (matches the spec exactly).
CSV_FIELDS = [
    "company_name",
    "short_name",
    "stock_code",
    "exchange",
    "data_category",
    "data_source",
    "source_url",
    "query_used",
    "fetch_status",
    "status_code",
    "content_type",
    "title",
    "publish_date",
    "extracted_fields",
    "sample_result",
    "evidence_sentence",
    "recommended_method",
    "needs_playwright",
    "needs_llm",
    "can_store_full_text",
    "suggested_storage",
    "legal_risk_note",
    "needs_legal_review",
    "failure_reason",
    "recommended_next_step",
    "crawl_time",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


@dataclass
class CoverageRow:
    company_name: str = ""
    short_name: str = ""
    stock_code: str = ""
    exchange: str = ""
    data_category: str = ""
    data_source: str = ""
    source_url: str = ""
    query_used: str = ""
    fetch_status: str = ""  # success | partial | failure | skipped
    status_code: str = ""
    content_type: str = ""
    title: str = ""
    publish_date: str = ""
    extracted_fields: str = ""  # JSON-encoded mapping
    sample_result: str = ""
    evidence_sentence: str = ""
    recommended_method: str = ""
    needs_playwright: bool = False
    needs_llm: bool = False
    can_store_full_text: bool = False
    suggested_storage: str = ""
    legal_risk_note: str = ""
    needs_legal_review: bool = False
    failure_reason: str = ""
    recommended_next_step: str = ""
    crawl_time: str = field(default_factory=_now_iso)

    def set_extracted(self, mapping: dict) -> None:
        """Store a mapping of extracted fields as compact JSON."""
        if mapping:
            self.extracted_fields = json.dumps(mapping, ensure_ascii=False)

    def to_csv_dict(self) -> dict:
        data = asdict(self)
        # Normalize booleans to lowercase strings for stable CSV output.
        for key, value in data.items():
            if isinstance(value, bool):
                data[key] = "true" if value else "false"
            elif value is None:
                data[key] = ""
        return {k: data.get(k, "") for k in CSV_FIELDS}


def write_csv(rows: list[CoverageRow], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_csv_dict())


# Sanity check: dataclass fields must match the declared CSV column set.
assert {f.name for f in fields(CoverageRow)} == set(CSV_FIELDS), (
    "CoverageRow fields and CSV_FIELDS are out of sync"
)
