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
    in_region           INTEGER,
    anchor_matched      TEXT,
    extraction_version  TEXT NOT NULL,
    updated_at          TEXT NOT NULL,
    PRIMARY KEY (company_code, report_year, field_name, extraction_version),
    FOREIGN KEY (company_code) REFERENCES company_basic(company_code)
);

CREATE TABLE IF NOT EXISTS evaluation_result (
    run_name            TEXT NOT NULL,
    company_code        TEXT NOT NULL,
    report_year         INTEGER NOT NULL,
    field_name          TEXT NOT NULL,
    proxy_plausible     INTEGER NOT NULL DEFAULT 0,
    strict_audit_result TEXT,
    notes               TEXT,
    created_at          TEXT NOT NULL,
    PRIMARY KEY (run_name, company_code, report_year, field_name),
    FOREIGN KEY (company_code) REFERENCES company_basic(company_code)
);

CREATE INDEX IF NOT EXISTS idx_evaluation_run
    ON evaluation_result (run_name, company_code);
"""


def connect_db(db_path: str) -> sqlite3.Connection:
    """Open SQLite connection with foreign keys enforced."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate_schema(conn: sqlite3.Connection) -> None:
    """Apply lightweight upgrades for databases created before schema changes."""
    conn.execute("DROP INDEX IF EXISTS idx_extracted_field_lookup")

    ef_cols = {row[1] for row in conn.execute("PRAGMA table_info(extracted_field)")}
    if ef_cols:
        if "in_region" not in ef_cols:
            conn.execute("ALTER TABLE extracted_field ADD COLUMN in_region INTEGER")
        if "anchor_matched" not in ef_cols:
            conn.execute("ALTER TABLE extracted_field ADD COLUMN anchor_matched TEXT")

    er_cols = {row[1] for row in conn.execute("PRAGMA table_info(evaluation_result)")}
    if er_cols and "report_year" not in er_cols:
        conn.executescript(
            """
            CREATE TABLE evaluation_result_new (
                run_name            TEXT NOT NULL,
                company_code        TEXT NOT NULL,
                report_year         INTEGER NOT NULL,
                field_name          TEXT NOT NULL,
                proxy_plausible     INTEGER NOT NULL DEFAULT 0,
                strict_audit_result TEXT,
                notes               TEXT,
                created_at          TEXT NOT NULL,
                PRIMARY KEY (run_name, company_code, report_year, field_name),
                FOREIGN KEY (company_code) REFERENCES company_basic(company_code)
            );
            INSERT INTO evaluation_result_new (
                run_name, company_code, report_year, field_name,
                proxy_plausible, strict_audit_result, notes, created_at)
            SELECT run_name, company_code, 2024, field_name,
                proxy_plausible, strict_audit_result, notes, created_at
            FROM evaluation_result;
            DROP TABLE evaluation_result;
            ALTER TABLE evaluation_result_new RENAME TO evaluation_result;
            CREATE INDEX IF NOT EXISTS idx_evaluation_run
                ON evaluation_result (run_name, company_code);
            """
        )


def create_schema(db_path: str = DEFAULT_DB_PATH) -> str:
    """Create v1 tables (idempotent). Returns absolute db path."""
    db_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = connect_db(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        _migrate_schema(conn)
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
