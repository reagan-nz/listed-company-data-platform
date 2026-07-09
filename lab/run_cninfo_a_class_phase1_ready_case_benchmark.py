"""
CNINFO A-class Phase 1 ready-case benchmark offline runner.

Reads local fixtures only. No CNINFO requests. No network. No PDF download.

Usage:
    python lab/run_cninfo_a_class_phase1_ready_case_benchmark.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIELD_CATALOG = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase1_freeze_v1_field_catalog.csv"
)
READY_CASES_DIR = os.path.join(BASE_DIR, "fixtures", "a_class", "phase1", "ready_cases")
BENCHMARK_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase1_ready_case_benchmark.csv"
)
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase1_ready_case_benchmark_summary.md"
)

SCHEMA_VERSION = "a_class_phase1_freeze_v1"
BENCHMARK_GATE = "READY_FOR_REVIEW"

VALID_REPORT_TYPES = frozenset({
    "annual_report",
    "semi_annual_report",
    "quarterly_report_q1",
    "quarterly_report_q3",
})

VALID_LINEAGE_STATUS = frozenset({"discovered", "linked", "needs_review", "not_found"})
VALID_QUALITY_STATUS = frozenset({"pass", "caveat", "blocked", "needs_review"})
VALID_STORAGE_STATUS_PHASE1 = frozenset({"not_attempted"})

CASE_REGISTRY = [
    {
        "case_id": "AC001",
        "object_type": "report_document",
        "fixture": "AC001_valid_periodic_report_case.json",
        "expected_status": "valid_pass",
    },
    {
        "case_id": "AC002",
        "object_type": "document_lineage",
        "fixture": "AC002_valid_announcement_lineage_case.json",
        "expected_status": "lineage_valid",
    },
    {
        "case_id": "AC003",
        "object_type": "report_document",
        "fixture": "AC003_missing_pdf_url_case.json",
        "expected_status": "quality_downgrade",
    },
    {
        "case_id": "AC004",
        "object_type": "report_document",
        "fixture": "AC004_duplicate_document_id_case.json",
        "expected_status": "dedup_review",
    },
    {
        "case_id": "AC005",
        "object_type": "report_document",
        "fixture": "AC005_unknown_report_type_case.json",
        "expected_status": "enum_invalid",
    },
]


@dataclass
class BenchmarkRow:
    case_id: str
    object_type: str
    expected_status: str
    actual_status: str
    quality_status: str
    lineage_status: str
    passed: str
    notes: str = ""


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    return True


def _load_required_by_object() -> Dict[str, Set[str]]:
    out: Dict[str, Set[str]] = {}
    with open(FIELD_CATALOG, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("level") != "required":
                continue
            obj = row["object"]
            out.setdefault(obj, set()).add(row["field_name"])
    return out


def _missing_required(payload: dict, required: Set[str]) -> List[str]:
    return sorted(f for f in required if f not in payload or not _is_present(payload.get(f)))


def _validate_ac001(data: dict, required: Dict[str, Set[str]]) -> Tuple[str, str, str, bool, str]:
    doc = data.get("report_document") or {}
    snap = data.get("report_period_snapshot") or {}
    lineage = data.get("document_lineage") or {}

    missing_doc = _missing_required(doc, required.get("report_document", set()))
    missing_snap = _missing_required(snap, required.get("report_period_snapshot", set()))
    missing_lin = _missing_required(lineage, required.get("document_lineage", set()))
    if missing_doc or missing_snap or missing_lin:
        return "fail", "blocked", "needs_review", False, (
            f"missing required: doc={missing_doc} snap={missing_snap} lin={missing_lin}"
        )

    if doc.get("report_type") not in VALID_REPORT_TYPES:
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "invalid report_type"
    if doc.get("quality_status") != "pass":
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "quality_status != pass"
    if lineage.get("storage_status") != "not_attempted":
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "storage_status invalid"
    if snap.get("document_id") != doc.get("document_id"):
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "snapshot link mismatch"

    return "valid_pass", "pass", "discovered", True, "all objects valid; quality pass; lineage discovered"


def _validate_ac002(data: dict, required: Dict[str, Set[str]]) -> Tuple[str, str, str, bool, str]:
    doc = data.get("report_document") or {}
    lineage = data.get("document_lineage") or {}
    root_id = data.get("document_id")

    missing_doc = _missing_required(doc, required.get("report_document", set()))
    missing_lin = _missing_required(lineage, required.get("document_lineage", set()))
    if missing_doc or missing_lin:
        return "fail", str(doc.get("quality_status")), str(lineage.get("lineage_status")), False, (
            f"missing required: doc={missing_doc} lin={missing_lin}"
        )

    if root_id != doc.get("document_id"):
        return "fail", str(doc.get("quality_status")), str(lineage.get("lineage_status")), False, "document_id mismatch"
    if doc.get("lineage_status") != lineage.get("lineage_status"):
        return "fail", str(doc.get("quality_status")), str(lineage.get("lineage_status")), False, "lineage_status mismatch"
    if lineage.get("storage_status") != "not_attempted":
        return "fail", str(doc.get("quality_status")), str(lineage.get("lineage_status")), False, "storage_status invalid"
    if not _is_present(lineage.get("pdf_url")):
        return "fail", str(doc.get("quality_status")), str(lineage.get("lineage_status")), False, "lineage pdf_url missing"

    return "lineage_valid", "pass", "linked", True, "lineage aligned with report_document"


def _validate_ac003(data: dict, required: Dict[str, Set[str]]) -> Tuple[str, str, str, bool, str]:
    doc = data.get("report_document") or {}
    lineage = data.get("document_lineage") or {}

    if _is_present(doc.get("pdf_url")):
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "pdf_url should be null"
    if doc.get("quality_status") != "needs_review":
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "quality_status != needs_review"
    if doc.get("quality_status") == "verified":
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "must not be verified"
    if lineage.get("lineage_status") != "needs_review":
        return "fail", str(doc.get("quality_status")), str(lineage.get("lineage_status")), False, "lineage needs_review expected"

    # pdf_url 字段必须存在（值可为 null）
    if "pdf_url" not in doc:
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "pdf_url key missing"

    return "quality_downgrade", "needs_review", "needs_review", True, "missing pdf_url; quality downgraded"


def _validate_ac004(data: dict, required: Dict[str, Set[str]]) -> Tuple[str, str, str, bool, str]:
    root_id = data.get("document_id")
    candidates = data.get("candidates") or []
    exp = data.get("expected_behavior") or {}

    if not root_id:
        return "fail", "blocked", "needs_review", False, "document_id missing at root"
    if len(candidates) < 2:
        return "fail", "caveat", "needs_review", False, "expected >=2 candidates"

    doc_ids = [(c.get("report_document") or {}).get("document_id") for c in candidates]
    if not all(d == root_id for d in doc_ids):
        return "fail", "caveat", "needs_review", False, "candidate document_id mismatch"

    titles = [(c.get("report_document") or {}).get("announcement_title") for c in candidates]
    if len(set(titles)) < 2:
        return "fail", "caveat", "needs_review", False, "candidates should differ in title"

    if not exp.get("dedup_decision_required"):
        return "fail", "caveat", "needs_review", False, "dedup_decision_required not set"
    if exp.get("automatic_merge"):
        return "fail", "caveat", "needs_review", False, "automatic_merge must be false"

    q_statuses = [(c.get("report_document") or {}).get("quality_status") for c in candidates]
    if not all(q == "caveat" for q in q_statuses):
        return "fail", "caveat", "needs_review", False, "expected quality_status=caveat on candidates"

    return "dedup_review", "caveat", "needs_review", True, "duplicate document_id; dedup required; no auto merge"


def _validate_ac005(data: dict, required: Dict[str, Set[str]]) -> Tuple[str, str, str, bool, str]:
    doc = data.get("report_document") or {}
    exp = data.get("expected_behavior") or {}

    if doc.get("report_type") in VALID_REPORT_TYPES:
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "report_type should be invalid"
    if exp.get("forced_report_type_mapping"):
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "forced mapping not allowed"
    if doc.get("quality_status") != "needs_review":
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "quality_status != needs_review"
    if doc.get("quality_status") == "verified":
        return "fail", str(doc.get("quality_status")), str(doc.get("lineage_status")), False, "must not be verified"

    return "enum_invalid", "needs_review", "needs_review", True, "unknown report_type preserved; quality downgraded"


def _run_case(case: dict, required: Dict[str, Set[str]]) -> BenchmarkRow:
    case_id = case["case_id"]
    fixture_path = os.path.join(READY_CASES_DIR, case["fixture"])
    if not os.path.isfile(fixture_path):
        return BenchmarkRow(
            case_id,
            case["object_type"],
            case["expected_status"],
            "error",
            "",
            "",
            "no",
            "fixture not found",
        )

    data = _load_json(fixture_path)
    validators = {
        "AC001": lambda: _validate_ac001(data, required),
        "AC002": lambda: _validate_ac002(data, required),
        "AC003": lambda: _validate_ac003(data, required),
        "AC004": lambda: _validate_ac004(data, required),
        "AC005": lambda: _validate_ac005(data, required),
    }
    fn = validators.get(case_id)
    if not fn:
        return BenchmarkRow(case_id, case["object_type"], case["expected_status"], "skip", "", "", "no", "unknown case")

    actual, quality, lineage, ok, notes = fn()
    return BenchmarkRow(
        case_id,
        case["object_type"],
        case["expected_status"],
        actual,
        quality,
        lineage,
        "yes" if ok else "no",
        notes,
    )


def _write_benchmark_csv(rows: List[BenchmarkRow]) -> None:
    os.makedirs(os.path.dirname(BENCHMARK_CSV), exist_ok=True)
    with open(BENCHMARK_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "case_id",
                "object_type",
                "expected_status",
                "actual_status",
                "quality_status",
                "lineage_status",
                "passed",
                "notes",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    "case_id": r.case_id,
                    "object_type": r.object_type,
                    "expected_status": r.expected_status,
                    "actual_status": r.actual_status,
                    "quality_status": r.quality_status,
                    "lineage_status": r.lineage_status,
                    "passed": r.passed,
                    "notes": r.notes,
                }
            )


def _write_summary(rows: List[BenchmarkRow]) -> None:
    passed = sum(1 for r in rows if r.passed == "yes")
    failed = len(rows) - passed
    lines = [
        "# CNINFO A 类 Phase 1 Ready-case Benchmark 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** 离线 fixture benchmark；**无 CNINFO**；**无 live**；**无 PDF 下载**。",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| Total cases | {len(rows)} |",
        f"| Passed | {passed} |",
        f"| Failed | {failed} |",
        f"| Schema version | {SCHEMA_VERSION} |",
        f"| CNINFO calls | **0** |",
        "",
        "## Case Results",
        "",
        "| case_id | object_type | expected_status | actual_status | quality_status | lineage_status | passed |",
        "|---------|-------------|-----------------|---------------|----------------|----------------|--------|",
    ]
    for r in rows:
        lines.append(
            f"| {r.case_id} | {r.object_type} | {r.expected_status} | {r.actual_status} | "
            f"{r.quality_status} | {r.lineage_status} | {r.passed} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "```text",
            f"a_class_ready_case_benchmark_gate = {BENCHMARK_GATE}",
            "```",
            "",
            "**不是 PASS** · **不是 live_ready** · **不是 verified**.",
            "",
            "## Parallel Safety",
            "",
            "- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**（不变）",
            "- B-class outputs: **unchanged**",
            "- CNINFO calls: **0**",
            "",
        ]
    )
    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    required = _load_required_by_object()
    rows = [_run_case(case, required) for case in CASE_REGISTRY]
    _write_benchmark_csv(rows)
    _write_summary(rows)

    for r in rows:
        mark = "PASS" if r.passed == "yes" else "FAIL"
        print(f"{r.case_id} {mark}: {r.notes}")

    all_passed = all(r.passed == "yes" for r in rows)
    print(f"\nGate: a_class_ready_case_benchmark_gate = {BENCHMARK_GATE}")
    print(f"All cases passed: {all_passed}")
    print(f"Benchmark CSV: {BENCHMARK_CSV}")
    print(f"Summary: {SUMMARY_MD}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
