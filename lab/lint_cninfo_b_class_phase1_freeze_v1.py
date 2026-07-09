"""
CNINFO B-class Phase 1 freeze v1 offline lint.

Validates freeze v1 field catalog, endpoint catalog, registry YAML draft,
and phase1 fixtures. No CNINFO requests; no PDF download.

Usage:
    python lab/lint_cninfo_b_class_phase1_freeze_v1.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Set

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIELD_CATALOG = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase1_freeze_v1_field_catalog.csv"
)
ENDPOINT_CATALOG = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase1_freeze_v1_endpoint_catalog.csv"
)
REGISTRY_YAML = os.path.join(BASE_DIR, "config", "cninfo_b_class_source_registry_draft.yaml")
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures", "b_class", "phase1")
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase1_freeze_v1_lint_summary.md"
)

SIGNOFF_REQUIRED_FIELDS: Set[str] = {
    "company_code",
    "org_id",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "announcement_date",
    "document_id",
    "retrieval_time",
    "raw_hash",
    "quality_status",
    "pdf_url",
    "adjunct_url",
    "source_endpoint",
    "lineage_status",
    "announcement_category",
}

FORBIDDEN_PHASE1_FIELD_PATTERNS = (
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

PHASE1_IN_SCOPE_SOURCES = frozenset({
    "cninfo_periodic_report_pdf",
    "cninfo_general_announcement_pdf",
})

EXPECTED_FIXTURES = (
    "announcement_metadata_fixture.json",
    "pdf_url_lineage_fixture.json",
    "source_registry_fixture.json",
)

TOTAL_CHECKS = 8


@dataclass
class LintResult:
    rule_id: str
    description: str
    passed: bool
    detail: str


def _read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check_required_field_count(rows: List[dict]) -> LintResult:
    required = [r for r in rows if r.get("required_level") == "required"]
    ok = len(required) == 15
    return LintResult(
        "R-P1-001",
        "required field count = 15",
        ok,
        f"found {len(required)} required rows",
    )


def check_required_fields_in_catalog(rows: List[dict]) -> LintResult:
    names = {r["field_name"] for r in rows}
    missing = SIGNOFF_REQUIRED_FIELDS - names
    ok = not missing
    return LintResult(
        "R-P1-002",
        "all signoff required fields appear in field catalog",
        ok,
        "missing: " + ", ".join(sorted(missing)) if missing else "all 15 present",
    )


def check_no_pdf_body_fields(rows: List[dict]) -> LintResult:
    offenders = []
    for row in rows:
        name = row["field_name"].lower()
        if any(p in name for p in FORBIDDEN_PHASE1_FIELD_PATTERNS):
            offenders.append(row["field_name"])
    ok = not offenders
    return LintResult(
        "R-P1-003",
        "no PDF body parsing / embedding fields in Phase1 catalog",
        ok,
        "forbidden: " + ", ".join(offenders) if offenders else "none found",
    )


def check_endpoint_in_scope_count(rows: List[dict]) -> LintResult:
    in_scope = [r for r in rows if r.get("phase1_status") == "phase1_in_scope"]
    ok = len(in_scope) == 4
    ids = [r["endpoint_id"] for r in in_scope]
    return LintResult(
        "R-P1-004",
        "endpoint catalog has exactly 4 phase1_in_scope endpoints",
        ok,
        f"count={len(in_scope)} ids={ids}",
    )


def check_endpoint_live_not_run(rows: List[dict]) -> LintResult:
  bad = [r["endpoint_id"] for r in rows if r.get("live_validation_status") != "not_run"]
  ok = not bad
  return LintResult(
      "R-P1-005",
      "all endpoint live_validation_status = not_run",
      ok,
      "non not_run: " + ", ".join(bad) if bad else "all not_run",
  )


def check_registry_phase1_sources(registry: dict) -> LintResult:
    sources = registry.get("sources") or []
    by_id = {s.get("source_id"): s for s in sources}
    missing = [sid for sid in PHASE1_IN_SCOPE_SOURCES if sid not in by_id]
    phase1_ok = all(
        by_id[sid].get("phase1_status") == "phase1_in_scope"
        for sid in PHASE1_IN_SCOPE_SOURCES
        if sid in by_id
    )
    ok = not missing and phase1_ok
    detail_parts = []
    if missing:
        detail_parts.append("missing sources: " + ", ".join(missing))
    if not phase1_ok:
        detail_parts.append("phase1_status not in_scope on one or more Phase1 sources")
    if ok:
        detail_parts.append("cninfo_periodic_report_pdf and cninfo_general_announcement_pdf present")
    return LintResult(
        "R-P1-006",
        "registry YAML contains Phase1 in_scope source entries",
        ok,
        "; ".join(detail_parts),
    )


def check_registry_no_verified(registry: dict) -> LintResult:
    sources = registry.get("sources") or []
    bad = [s.get("source_id") for s in sources if s.get("status", {}).get("verified") is True]
    ok = not bad
    return LintResult(
        "R-P1-007",
        "no registry source marked verified",
        ok,
        "verified=true: " + ", ".join(bad) if bad else "all verified=false",
    )


def check_registry_no_testing_stable_sample(registry: dict) -> LintResult:
    sources = registry.get("sources") or []
    bad = [
        s.get("source_id")
        for s in sources
        if s.get("status", {}).get("recommended_status") == "testing_stable_sample"
    ]
    ok = not bad
    return LintResult(
        "R-P1-008",
        "no registry source marked testing_stable_sample",
        ok,
        "testing_stable_sample: " + ", ".join(bad) if bad else "none",
    )


def check_fixtures_exist() -> LintResult:
    missing = [name for name in EXPECTED_FIXTURES if not os.path.isfile(os.path.join(FIXTURES_DIR, name))]
    ok = not missing
    return LintResult(
        "R-P1-009",
        "phase1 fixture skeleton files exist",
        ok,
        "missing: " + ", ".join(missing) if missing else f"{len(EXPECTED_FIXTURES)} fixtures present",
    )


def write_summary(results: List[LintResult], gate: str) -> None:
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    lines = [
        "# CNINFO B 类 Phase 1 Freeze v1 Lint Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** 离线 lint；无 CNINFO；无 live；无 PDF 下载。",
        "",
        "## Gate",
        "",
        f"```text",
        f"b_class_phase1_freeze_v1_implementation_gate = {gate}",
        f"```",
        "",
        "## Results",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
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
    field_rows = _read_csv(FIELD_CATALOG)
    endpoint_rows = _read_csv(ENDPOINT_CATALOG)
    with open(REGISTRY_YAML, encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    results = [
        check_required_field_count(field_rows),
        check_required_fields_in_catalog(field_rows),
        check_no_pdf_body_fields(field_rows),
        check_endpoint_in_scope_count(endpoint_rows),
        check_endpoint_live_not_run(endpoint_rows),
        check_registry_phase1_sources(registry),
        check_registry_no_verified(registry),
        check_registry_no_testing_stable_sample(registry),
        check_fixtures_exist(),
    ]

    gate = "PASS_OFFLINE" if all(r.passed for r in results) else "FAIL"
    write_summary(results, gate)

    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"{r.rule_id} {mark}: {r.description} — {r.detail}")

    print(f"\nGate: b_class_phase1_freeze_v1_implementation_gate = {gate}")
    print(f"Summary: {SUMMARY_MD}")
    return 0 if gate == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    sys.exit(main())
