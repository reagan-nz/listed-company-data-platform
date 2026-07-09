"""
CNINFO A-class Phase 1 freeze v1 offline lint.

Validates freeze v1 field decision matrix, phase1 fixture skeletons,
required fields, object relationships, lineage fields, and status enums.
No CNINFO requests; no PDF download.

Usage:
    python lab/lint_cninfo_a_class_phase1_freeze_v1.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Set

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIELD_DECISION_MATRIX = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase1_field_decision_matrix.csv"
)
MINIMUM_FIELDS_CATALOG = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase1_minimum_fields.csv"
)
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures", "a_class", "phase1")
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase1_freeze_v1_lint_summary.md"
)

REPORT_DOCUMENT_REQUIRED: Set[str] = {
    "document_id",
    "company_code",
    "report_type",
    "report_period",
    "publish_date",
    "announcement_id",
    "announcement_title",
    "pdf_url",
    "source_endpoint",
    "retrieval_time",
    "raw_hash",
    "lineage_status",
    "quality_status",
}

PERIOD_SNAPSHOT_REQUIRED: Set[str] = {
    "company_code",
    "year",
    "report_type",
    "document_id",
}

LINEAGE_REQUIRED: Set[str] = {
    "storage_status",
    "version",
    "source_endpoint",
    "retrieval_time",
    "lineage_status",
}

VALID_REPORT_TYPES = frozenset({
    "annual_report",
    "semi_annual_report",
    "quarterly_report_q1",
    "quarterly_report_q3",
})

VALID_LINEAGE_STATUS = frozenset({
    "discovered",
    "linked",
    "needs_review",
    "not_found",
})

VALID_QUALITY_STATUS = frozenset({
    "pass",
    "caveat",
    "blocked",
    "needs_review",
})

VALID_STORAGE_STATUS_PHASE1 = frozenset({"not_attempted"})

VALID_COVERAGE_STATUS = frozenset({
    "found",
    "not_found",
    "caveat",
})

FORBIDDEN_FIELD_PATTERNS = (
    "pdf_body",
    "pdf_text",
    "extracted_text",
    "ocr_text",
    "page_text",
    "chunk_id",
    "embedding",
    "vector",
    "parsed_content",
)

EXPECTED_FIXTURES = (
    "report_document_fixture.json",
    "report_period_snapshot_fixture.json",
    "document_lineage_fixture.json",
)

LINK_DOCUMENT_ID = "a_doc_fixture_999001_2024_annual"


@dataclass
class LintResult:
    rule_id: str
    description: str
    passed: bool
    detail: str


def _read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _fixture_meta_ok(data: dict) -> bool:
    meta = data.get("_fixture_meta") or {}
    return meta.get("cninfo_called") is False and meta.get("pdf_downloaded") is False


def check_decision_matrix_covers_catalog(matrix_rows: List[dict], catalog_rows: List[dict]) -> LintResult:
    matrix_keys = {(r["field_name"], r["object"]) for r in matrix_rows}
    catalog_keys = {(r["field_name"], r["object"]) for r in catalog_rows}
    missing = catalog_keys - matrix_keys
    ok = not missing
    detail = (
        "missing: " + "; ".join(f"{f}@{o}" for f, o in sorted(missing))
        if missing
        else f"all {len(catalog_keys)} catalog fields covered"
    )
    return LintResult(
        "R-A1-001",
        "field decision matrix covers all minimum catalog fields",
        ok,
        detail,
    )


def check_fixtures_exist() -> LintResult:
    missing = [name for name in EXPECTED_FIXTURES if not os.path.isfile(os.path.join(FIXTURES_DIR, name))]
    ok = not missing
    return LintResult(
        "R-A1-002",
        "phase1 fixture skeleton files exist",
        ok,
        "missing: " + ", ".join(missing) if missing else f"{len(EXPECTED_FIXTURES)} fixtures present",
    )


def check_fixture_meta_flags() -> LintResult:
    bad = []
    for name in EXPECTED_FIXTURES:
        data = _load_json(os.path.join(FIXTURES_DIR, name))
        if not _fixture_meta_ok(data):
            bad.append(name)
    ok = not bad
    return LintResult(
        "R-A1-003",
        "all fixtures declare cninfo_called=false and pdf_downloaded=false",
        ok,
        "bad: " + ", ".join(bad) if bad else "all 3 fixtures ok",
    )


def check_report_document_required_fields() -> LintResult:
    data = _load_json(os.path.join(FIXTURES_DIR, "report_document_fixture.json"))
    doc = data.get("report_document") or {}
    missing = REPORT_DOCUMENT_REQUIRED - set(doc.keys())
    ok = not missing
    return LintResult(
        "R-A1-004",
        "report_document fixture contains all freeze v1 required fields",
        ok,
        "missing: " + ", ".join(sorted(missing)) if missing else f"all {len(REPORT_DOCUMENT_REQUIRED)} present",
    )


def check_period_snapshot_required_fields() -> LintResult:
    data = _load_json(os.path.join(FIXTURES_DIR, "report_period_snapshot_fixture.json"))
    snap = data.get("report_period_snapshot") or {}
    missing = PERIOD_SNAPSHOT_REQUIRED - set(snap.keys())
    ok = not missing
    return LintResult(
        "R-A1-005",
        "report_period_snapshot fixture contains all freeze v1 required fields",
        ok,
        "missing: " + ", ".join(sorted(missing)) if missing else f"all {len(PERIOD_SNAPSHOT_REQUIRED)} present",
    )


def check_lineage_required_fields() -> LintResult:
    data = _load_json(os.path.join(FIXTURES_DIR, "document_lineage_fixture.json"))
    lineage = data.get("document_lineage") or {}
    missing = LINEAGE_REQUIRED - set(lineage.keys())
    ok = not missing
    return LintResult(
        "R-A1-006",
        "document_lineage fixture contains all freeze v1 required fields",
        ok,
        "missing: " + ", ".join(sorted(missing)) if missing else f"all {len(LINEAGE_REQUIRED)} present",
    )


def check_object_relationships() -> LintResult:
    doc = _load_json(os.path.join(FIXTURES_DIR, "report_document_fixture.json"))
    snap = _load_json(os.path.join(FIXTURES_DIR, "report_period_snapshot_fixture.json"))
    lineage = _load_json(os.path.join(FIXTURES_DIR, "document_lineage_fixture.json"))

    doc_id = (doc.get("report_document") or {}).get("document_id")
    snap_id = (snap.get("report_period_snapshot") or {}).get("document_id")
    lineage_id = lineage.get("document_id")
    snap_company = (snap.get("report_period_snapshot") or {}).get("company_code")
    doc_company = (doc.get("report_document") or {}).get("company_code")

    issues = []
    if doc_id != LINK_DOCUMENT_ID:
        issues.append(f"report_document document_id={doc_id}")
    if snap_id != LINK_DOCUMENT_ID:
        issues.append(f"snapshot document_id={snap_id}")
    if lineage_id != LINK_DOCUMENT_ID:
        issues.append(f"lineage document_id={lineage_id}")
    if snap_company != doc_company:
        issues.append("company_code mismatch between snapshot and document")

    ok = not issues
    return LintResult(
        "R-A1-007",
        "object relationships valid (document_id and company_code aligned)",
        ok,
        "; ".join(issues) if issues else f"linked via {LINK_DOCUMENT_ID}",
    )


def check_status_enums() -> LintResult:
    doc = (_load_json(os.path.join(FIXTURES_DIR, "report_document_fixture.json")).get("report_document") or {})
    snap = (
        _load_json(os.path.join(FIXTURES_DIR, "report_period_snapshot_fixture.json")).get("report_period_snapshot")
        or {}
    )
    lineage = (
        _load_json(os.path.join(FIXTURES_DIR, "document_lineage_fixture.json")).get("document_lineage") or {}
    )

    issues = []
    if doc.get("report_type") not in VALID_REPORT_TYPES:
        issues.append(f"report_type={doc.get('report_type')}")
    if doc.get("lineage_status") not in VALID_LINEAGE_STATUS:
        issues.append(f"doc lineage_status={doc.get('lineage_status')}")
    if doc.get("quality_status") not in VALID_QUALITY_STATUS:
        issues.append(f"quality_status={doc.get('quality_status')}")
    if snap.get("coverage_status") not in VALID_COVERAGE_STATUS:
        issues.append(f"coverage_status={snap.get('coverage_status')}")
    if lineage.get("lineage_status") not in VALID_LINEAGE_STATUS:
        issues.append(f"lineage lineage_status={lineage.get('lineage_status')}")
    if lineage.get("storage_status") not in VALID_STORAGE_STATUS_PHASE1:
        issues.append(f"storage_status={lineage.get('storage_status')}")

    if doc.get("lineage_status") != lineage.get("lineage_status"):
        issues.append("lineage_status mismatch between report_document and document_lineage")

    ok = not issues
    return LintResult(
        "R-A1-008",
        "status enums valid for Phase1 freeze v1",
        ok,
        "; ".join(issues) if issues else "all enums valid",
    )


def check_no_parser_fields_in_fixtures() -> LintResult:
    offenders: List[str] = []

    def walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                key_lower = k.lower()
                if any(p in key_lower for p in FORBIDDEN_FIELD_PATTERNS):
                    offenders.append(f"{path}.{k}" if path else k)
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{path}[{i}]")

    for name in EXPECTED_FIXTURES:
        walk(_load_json(os.path.join(FIXTURES_DIR, name)), name)

    ok = not offenders
    return LintResult(
        "R-A1-009",
        "no PDF parser / embedding fields in fixtures",
        ok,
        "forbidden: " + ", ".join(offenders) if offenders else "none found",
    )


def check_lineage_phase1_boundary() -> LintResult:
    lineage = (
        _load_json(os.path.join(FIXTURES_DIR, "document_lineage_fixture.json")).get("document_lineage") or {}
    )
    forbidden_present = [k for k in ("download_time", "file_hash", "file_size") if k in lineage and lineage[k] is not None]
    ok = not forbidden_present and lineage.get("storage_status") == "not_attempted"
    detail_parts = []
    if forbidden_present:
        detail_parts.append("future fields non-null: " + ", ".join(forbidden_present))
    if lineage.get("storage_status") != "not_attempted":
        detail_parts.append(f"storage_status={lineage.get('storage_status')}")
    if ok:
        detail_parts.append("storage_status=not_attempted; no download fields")
    return LintResult(
        "R-A1-010",
        "document_lineage respects Phase1 boundary (no download fields)",
        ok,
        "; ".join(detail_parts),
    )


def write_summary(results: List[LintResult], gate: str) -> None:
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    lines = [
        "# CNINFO A 类 Phase 1 Freeze v1 Lint Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** 离线 lint；无 CNINFO；无 live；无 PDF 下载。",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase1_freeze_v1_lint_gate = {gate}",
        "```",
        "",
        "## Results",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| checks run | {len(results)} |",
        f"| passed | {passed} |",
        f"| failed | {failed} |",
        "",
        "## Rule Details",
        "",
        "| rule_id | description | result | detail |",
        "|---------|-------------|--------|--------|",
    ]
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"| {r.rule_id} | {r.description} | {status} | {r.detail} |")
    lines.append("")
    os.makedirs(os.path.dirname(SUMMARY_MD), exist_ok=True)
    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    matrix_rows = _read_csv(FIELD_DECISION_MATRIX)
    catalog_rows = _read_csv(MINIMUM_FIELDS_CATALOG)

    results = [
        check_decision_matrix_covers_catalog(matrix_rows, catalog_rows),
        check_fixtures_exist(),
        check_fixture_meta_flags(),
        check_report_document_required_fields(),
        check_period_snapshot_required_fields(),
        check_lineage_required_fields(),
        check_object_relationships(),
        check_status_enums(),
        check_no_parser_fields_in_fixtures(),
        check_lineage_phase1_boundary(),
    ]

    gate = "PASS_OFFLINE" if all(r.passed for r in results) else "FAIL"
    write_summary(results, gate)

    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"{r.rule_id} {mark}: {r.description} — {r.detail}")

    print(f"\nGate: a_class_phase1_freeze_v1_lint_gate = {gate}")
    print(f"Summary: {SUMMARY_MD}")
    return 0 if gate == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    sys.exit(main())
