"""SQLite schema creation for listed-company database v1.

See docs/database_schema.md for table definitions.
"""

from __future__ import annotations

import os
import sqlite3

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(_PROJECT_ROOT, "outputs", "db", "listed_companies_v1.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS company_basic (
    company_code   TEXT PRIMARY KEY,
    company_name   TEXT NOT NULL,
    exchange       TEXT,
    board          TEXT,
    is_financial   INTEGER NOT NULL DEFAULT 0,
    listing_status TEXT,
    created_at     TEXT NOT NULL,
    updated_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS report_source (
    company_code     TEXT NOT NULL,
    report_year      INTEGER NOT NULL,
    report_title     TEXT,
    source_url       TEXT,
    pdf_sha256       TEXT,
    download_status  TEXT NOT NULL,
    parse_status     TEXT NOT NULL,
    text_layer_ok    INTEGER NOT NULL DEFAULT 0,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL,
    PRIMARY KEY (company_code, report_year),
    FOREIGN KEY (company_code) REFERENCES company_basic(company_code)
);

CREATE TABLE IF NOT EXISTS extracted_field (
    company_code        TEXT NOT NULL,
    report_year         INTEGER NOT NULL,
    field_name          TEXT NOT NULL,
    field_label_cn      TEXT,
    value               TEXT,
    status              TEXT NOT NULL,
    page                INTEGER,
    evidence_sentence   TEXT,
    source_url          TEXT,
    extraction_version  TEXT NOT NULL,
    updated_at          TEXT NOT NULL,
    PRIMARY KEY (company_code, report_year, field_name, extraction_version),
    FOREIGN KEY (company_code) REFERENCES company_basic(company_code)
);

CREATE TABLE IF NOT EXISTS evaluation_result (
    run_name            TEXT NOT NULL,
    company_code        TEXT NOT NULL,
    field_name          TEXT NOT NULL,
    proxy_plausible     INTEGER NOT NULL DEFAULT 0,
    strict_audit_result TEXT,
    notes               TEXT,
    created_at          TEXT NOT NULL,
    PRIMARY KEY (run_name, company_code, field_name),
    FOREIGN KEY (company_code) REFERENCES company_basic(company_code)
);

CREATE INDEX IF NOT EXISTS idx_extracted_field_lookup
    ON extracted_field (company_code, report_year, field_name);
CREATE INDEX IF NOT EXISTS idx_evaluation_run
    ON evaluation_result (run_name, company_code);
"""


def create_schema(db_path: str = DEFAULT_DB_PATH) -> str:
    """Create v1 tables (idempotent). Returns absolute db path."""
    db_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()
    return db_path


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Create SQLite v1 schema for listed-company DB")
    ap.add_argument("--db", default=DEFAULT_DB_PATH, help="SQLite database file path")
    args = ap.parse_args()
    path = create_schema(args.db)
    print(f"[db_init] schema ready -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
