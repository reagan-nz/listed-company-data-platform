"""
CNINFO A-class freeze v1 offline lint.

Validates freeze v1 field catalog, registry draft YAML, and phase1 fixtures.
No CNINFO requests; no PDF download.

Usage:
    python lab/lint_cninfo_a_class_freeze_v1.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Set

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIELD_CATALOG = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase1_freeze_v1_field_catalog.csv"
)
REGISTRY_YAML = os.path.join(BASE_DIR, "config", "cninfo_a_class_source_registry_draft.yaml")
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures", "a_class", "phase1")
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase1_freeze_v1_lint_summary.md"
)

LINK_DOCUMENT_ID = "a_doc_fixture_999001_2024_annual"

REMOVED_FIELDS = frozenset({("report_document", "notes"), ("document_lineage", "mime_type")})

FUTURE_FIELDS_PHASE1_FORBIDDEN = frozenset({
    ("report_period_snapshot", "available_sections"),
    ("document_lineage", "download_time"),
    ("document_lineage", "file_hash"),
    ("document_lineage", "file_size"),
})

FORBIDDEN_PARSER_PATTERNS = (
    "pdf_body",
    "pdf_text",
    "extracted_text",
    "ocr_text",
    "chunk_id",
    "embedding",
    "vector",
    "parsed_content",
)

VALID_REPORT_TYPES = frozenset({
    "annual_report",
    "semi_annual_report",
    "quarterly_report_q1",
    "quarterly_report_q3",
})

VALID_LINEAGE_STATUS = frozenset({"discovered", "linked", "needs_review", "not_found"})
VALID_QUALITY_STATUS = frozenset({"pass", "caveat", "blocked", "needs_review"})
VALID_COVERAGE_STATUS = frozenset({"found", "not_found", "caveat"})

EXPECTED_FIXTURES = (
    "report_document_fixture.json",
    "report_period_snapshot_fixture.json",
    "document_lineage_fixture.json",
)


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


def _required_by_object(rows: List[dict]) -> Dict[str, Set[str]]:
    out: Dict[str, Set[str]] = {}
    for row in rows:
        if row.get("level") != "required":
            continue
        obj = row["object"]
        out.setdefault(obj, set()).add(row["field_name"])
    return out


def check_field_catalog_counts(rows: List[dict]) -> LintResult:
    counts = {"required": 0, "recommended": 0, "future": 0, "removed": 0}
    for row in rows:
        level = row.get("level", "")
        if level in counts:
            counts[level] += 1
    ok = counts == {"required": 22, "recommended": 12, "future": 4, "removed": 2}
    return LintResult(
        "R-AF1-001",
        "field catalog counts match freeze v1 contract",
        ok,
        f"required={counts['required']} recommended={counts['recommended']} "
        f"future={counts['future']} removed={counts['removed']}",
    )


def check_three_objects(rows: List[dict]) -> LintResult:
    objects = {row["object"] for row in rows}
    expected = {"report_document", "report_period_snapshot", "document_lineage"}
    ok = objects == expected
    return LintResult(
        "R-AF1-002",
        "field catalog covers exactly 3 objects",
        ok,
        f"objects={sorted(objects)}",
    )


def check_registry_exists_and_objects(registry: dict) -> LintResult:
    mapping = registry.get("object_mapping") or {}
    expected = {"report_document", "report_period_snapshot", "document_lineage"}
    ok = set(mapping.keys()) == expected
    return LintResult(
        "R-AF1-003",
        "registry YAML defines 3 object mappings",
        ok,
        f"objects={sorted(mapping.keys())}",
    )


def check_registry_phase1_sources(registry: dict) -> LintResult:
    sources = registry.get("sources") or []
    in_scope = [s for s in sources if s.get("phase1_status") == "phase1_in_scope"]
    ok = len(in_scope) == 3
    ids = [s.get("source_id") for s in in_scope]
    return LintResult(
        "R-AF1-004",
        "registry has 3 phase1_in_scope sources",
        ok,
        f"count={len(in_scope)} ids={ids}",
    )


def check_registry_no_verified(registry: dict) -> LintResult:
    sources = registry.get("sources") or []
    bad = [s.get("source_id") for s in sources if (s.get("status") or {}).get("verified") is True]
    ok = not bad
    return LintResult(
        "R-AF1-005",
        "no registry source marked verified",
        ok,
        "verified=true: " + ", ".join(bad) if bad else "all verified=false",
    )


def check_registry_live_not_run(registry: dict) -> LintResult:
    top = registry.get("live_validation_status")
    sources = registry.get("sources") or []
    bad = [s.get("source_id") for s in sources if s.get("live_validation_status") != "not_run"]
    ok = top == "not_run" and not bad
    detail = f"registry={top}"
    if bad:
        detail += "; sources: " + ", ".join(bad)
    return LintResult(
        "R-AF1-006",
        "registry live_validation_status = not_run",
        ok,
        detail,
    )


def check_registry_no_testing_stable_sample(registry: dict) -> LintResult:
    sources = registry.get("sources") or []
    bad = [
        s.get("source_id")
        for s in sources
        if (s.get("status") or {}).get("recommended_status") == "testing_stable_sample"
    ]
    ok = not bad
    return LintResult(
        "R-AF1-007",
        "no registry source marked testing_stable_sample",
        ok,
        "found: " + ", ".join(bad) if bad else "none",
    )


def check_fixtures_required_fields(catalog_rows: List[dict]) -> LintResult:
    required = _required_by_object(catalog_rows)
    doc = (_load_json(os.path.join(FIXTURES_DIR, "report_document_fixture.json")).get("report_document") or {})
    snap = (
        _load_json(os.path.join(FIXTURES_DIR, "report_period_snapshot_fixture.json")).get("report_period_snapshot")
        or {}
    )
    lineage = (
        _load_json(os.path.join(FIXTURES_DIR, "document_lineage_fixture.json")).get("document_lineage") or {}
    )

    missing_parts = []
    for obj_name, payload in (
        ("report_document", doc),
        ("report_period_snapshot", snap),
        ("document_lineage", lineage),
    ):
        miss = required.get(obj_name, set()) - set(payload.keys())
        if miss:
            missing_parts.append(f"{obj_name}: " + ", ".join(sorted(miss)))

    ok = not missing_parts
    return LintResult(
        "R-AF1-008",
        "fixtures contain all freeze v1 required fields per object",
        ok,
        "; ".join(missing_parts) if missing_parts else "all required fields present",
    )


def check_removed_fields_absent() -> LintResult:
    offenders: List[str] = []
    normalized_keys = ("report_document", "report_period_snapshot", "document_lineage")

    for name in EXPECTED_FIXTURES:
        data = _load_json(os.path.join(FIXTURES_DIR, name))
        for obj_key in normalized_keys:
            payload = data.get(obj_key)
            if not isinstance(payload, dict):
                continue
            for field in ("notes", "mime_type"):
                if field in payload:
                    offenders.append(f"{name}:{obj_key}.{field}")

    ok = not offenders
    return LintResult(
        "R-AF1-009",
        "removed fields (notes, mime_type) absent from fixtures",
        ok,
        "found: " + ", ".join(offenders) if offenders else "none",
    )


def check_future_fields_absent_from_normalized() -> LintResult:
    lineage = (
        _load_json(os.path.join(FIXTURES_DIR, "document_lineage_fixture.json")).get("document_lineage") or {}
    )
    snap = (
        _load_json(os.path.join(FIXTURES_DIR, "report_period_snapshot_fixture.json")).get("report_period_snapshot")
        or {}
    )
    bad = []
    for field in ("download_time", "file_hash", "file_size"):
        if field in lineage:
            bad.append(f"document_lineage.{field}")
    if "available_sections" in snap:
        bad.append("report_period_snapshot.available_sections")
    ok = not bad
    return LintResult(
        "R-AF1-010",
        "future fields absent from phase1 normalized fixture payloads",
        ok,
        "found: " + ", ".join(bad) if bad else "none",
    )


def check_object_relationships() -> LintResult:
    doc = _load_json(os.path.join(FIXTURES_DIR, "report_document_fixture.json"))
    snap = _load_json(os.path.join(FIXTURES_DIR, "report_period_snapshot_fixture.json"))
    lineage = _load_json(os.path.join(FIXTURES_DIR, "document_lineage_fixture.json"))

    doc_id = (doc.get("report_document") or {}).get("document_id")
    snap_id = (snap.get("report_period_snapshot") or {}).get("document_id")
    lineage_id = lineage.get("document_id")
    issues = []
    if doc_id != LINK_DOCUMENT_ID:
        issues.append(f"doc_id={doc_id}")
    if snap_id != LINK_DOCUMENT_ID:
        issues.append(f"snap_id={snap_id}")
    if lineage_id != LINK_DOCUMENT_ID:
        issues.append(f"lineage_id={lineage_id}")
    if (doc.get("report_document") or {}).get("company_code") != (
        snap.get("report_period_snapshot") or {}
    ).get("company_code"):
        issues.append("company_code mismatch")
    ok = not issues
    return LintResult(
        "R-AF1-011",
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
        issues.append(f"doc.lineage_status={doc.get('lineage_status')}")
    if doc.get("quality_status") not in VALID_QUALITY_STATUS:
        issues.append(f"quality_status={doc.get('quality_status')}")
    if snap.get("coverage_status") not in VALID_COVERAGE_STATUS:
        issues.append(f"coverage_status={snap.get('coverage_status')}")
    if lineage.get("lineage_status") not in VALID_LINEAGE_STATUS:
        issues.append(f"lineage.lineage_status={lineage.get('lineage_status')}")
    if lineage.get("storage_status") != "not_attempted":
        issues.append(f"storage_status={lineage.get('storage_status')}")
    if doc.get("lineage_status") != lineage.get("lineage_status"):
        issues.append("lineage_status mismatch doc vs lineage")
    ok = not issues
    return LintResult(
        "R-AF1-012",
        "status enums valid for Phase1 freeze v1",
        ok,
        "; ".join(issues) if issues else "all enums valid",
    )


def check_fixture_meta() -> LintResult:
    bad = []
    for name in EXPECTED_FIXTURES:
        meta = (_load_json(os.path.join(FIXTURES_DIR, name)).get("_fixture_meta") or {})
        if meta.get("cninfo_called") is not False:
            bad.append(f"{name}:cninfo_called")
        if meta.get("pdf_downloaded") is not False:
            bad.append(f"{name}:pdf_downloaded")
        if meta.get("validated_against") != "freeze_v1":
            bad.append(f"{name}:validated_against")
    ok = not bad
    return LintResult(
        "R-AF1-013",
        "fixtures declare offline freeze_v1 validation metadata",
        ok,
        "bad: " + ", ".join(bad) if bad else "all 3 fixtures ok",
    )


def check_no_parser_fields() -> LintResult:
    offenders: List[str] = []

    def walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if any(p in k.lower() for p in FORBIDDEN_PARSER_PATTERNS):
                    offenders.append(f"{path}.{k}" if path else k)
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{path}[{i}]")

    for name in EXPECTED_FIXTURES:
        walk(_load_json(os.path.join(FIXTURES_DIR, name)), name)

    ok = not offenders
    return LintResult(
        "R-AF1-014",
        "no PDF parser / embedding fields in fixtures",
        ok,
        "forbidden: " + ", ".join(offenders) if offenders else "none found",
    )


def write_summary(results: List[LintResult], gate: str) -> None:
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    lines = [
        "# CNINFO A 类 Phase 1 Freeze v1 Lint Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** 离线 lint（freeze v1 implementation）；无 CNINFO；无 live；无 PDF 下载。",
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
    catalog_rows = _read_csv(FIELD_CATALOG)
    with open(REGISTRY_YAML, encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    results = [
        check_field_catalog_counts(catalog_rows),
        check_three_objects(catalog_rows),
        check_registry_exists_and_objects(registry),
        check_registry_phase1_sources(registry),
        check_registry_no_verified(registry),
        check_registry_live_not_run(registry),
        check_registry_no_testing_stable_sample(registry),
        check_fixtures_required_fields(catalog_rows),
        check_removed_fields_absent(),
        check_future_fields_absent_from_normalized(),
        check_object_relationships(),
        check_status_enums(),
        check_fixture_meta(),
        check_no_parser_fields(),
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
