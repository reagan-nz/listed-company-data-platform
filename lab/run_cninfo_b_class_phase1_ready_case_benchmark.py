"""
CNINFO B-class Phase 1 ready-case benchmark offline runner.

Reads local fixtures only. No CNINFO requests. No network.

Usage:
    python lab/run_cninfo_b_class_phase1_ready_case_benchmark.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BENCHMARK_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase1_ready_case_benchmark.csv"
)
FIELD_CATALOG = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase1_freeze_v1_field_catalog.csv"
)
PDF_LINEAGE_COMPANION = os.path.join(
    BASE_DIR, "fixtures", "b_class", "phase1", "pdf_url_lineage_fixture.json"
)
REPORT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase1_ready_case_benchmark_execution_report.csv"
)
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase1_ready_case_benchmark_execution_summary.md"
)

SCHEMA_VERSION = "phase1_freeze_v1"

REQUIRED_FIELDS = [
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
]


@dataclass
class CaseResult:
    case_id: str
    fixture: str
    execution_status: str
    expected_result: str
    actual_result: str
    passed: bool
    failure_reason: str
    notes: str


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_field_catalog() -> List[str]:
    required = []
    with open(FIELD_CATALOG, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("required_level") == "required":
                required.append(row["field_name"])
    return required


def _resolve_fixture_path(rel_path: str) -> str:
    return os.path.join(BASE_DIR, rel_path)


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    return True


def _flatten_record(data: dict) -> Dict[str, Any]:
    """将分块 fixture 扁平化为 required 字段查找表。"""
    out: Dict[str, Any] = {}
    ann = data.get("announcement_record") or {}
    doc = data.get("document_metadata") or {}
    pdf = data.get("pdf_reference") or {}
    cat = data.get("announcement_category") or {}
    ev = data.get("document_evidence") or {}
    lineage = data.get("lineage") or {}

    out["company_code"] = ann.get("company_code")
    out["org_id"] = ann.get("org_id")
    out["announcement_id"] = ann.get("announcement_id")
    out["announcement_title"] = ann.get("announcement_title")
    out["announcement_time"] = ann.get("announcement_time")
    out["announcement_date"] = ann.get("announcement_date")
    out["document_id"] = doc.get("document_id")
    out["retrieval_time"] = doc.get("retrieval_time")
    out["raw_hash"] = doc.get("raw_hash")
    out["quality_status"] = doc.get("quality_status")
    out["pdf_url"] = pdf.get("pdf_url")
    out["adjunct_url"] = pdf.get("adjunct_url")
    out["source_endpoint"] = pdf.get("source_endpoint") or lineage.get("source_endpoint")
    out["lineage_status"] = ev.get("lineage_status") or lineage.get("lineage_status")
    out["announcement_category"] = cat.get("announcement_category")
    out["category_status"] = cat.get("category_status")
    out["forced_taxonomy_mapping"] = cat.get("forced_taxonomy_mapping")
    out["source_id"] = doc.get("source_id")
    return out


def _merge_pdf_companion(data: dict, companion: dict) -> dict:
    """RC001/RC002：主 fixture 无 pdf_reference 时合并 companion。"""
    merged = json.loads(json.dumps(data))
    pdf_ref = companion.get("pdf_reference") or {}
    doc_id = (merged.get("document_metadata") or {}).get("document_id")
    if doc_id and pdf_ref.get("document_id") == doc_id:
        merged["pdf_reference"] = pdf_ref
        if companion.get("lineage"):
            merged.setdefault("document_evidence", {})
            if not merged["document_evidence"].get("lineage_status"):
                merged["document_evidence"]["lineage_status"] = companion["lineage"].get(
                    "lineage_status"
                )
    return merged


def _missing_required(flat: Dict[str, Any], fields: List[str]) -> List[str]:
    return [f for f in fields if not _is_present(flat.get(f))]


def _validate_rc001(data: dict, catalog_required: List[str]) -> Tuple[bool, str]:
    flat = _flatten_record(data)
    missing = _missing_required(flat, catalog_required)
    if missing:
        return False, f"missing required fields: {', '.join(missing)}"
    if not _is_present(flat.get("pdf_url")):
        return False, "pdf_url missing"
    if not _is_present(flat.get("adjunct_url")):
        return False, "adjunct_url missing"
    if flat.get("quality_status") != "pass":
        return False, f"quality_status={flat.get('quality_status')}, expected pass"
    if flat.get("lineage_status") != "discovered":
        return False, f"lineage_status={flat.get('lineage_status')}, expected discovered"
    return True, "required complete; pdf lineage present; quality_status=pass; lineage_status=discovered"


def _validate_rc002(data: dict, catalog_required: List[str]) -> Tuple[bool, str]:
    flat = _flatten_record(data)
    missing = _missing_required(flat, catalog_required)
    if missing:
        return False, f"missing required fields: {', '.join(missing)}"
    if not _is_present(flat.get("announcement_category")):
        return False, "announcement_category missing"
    # RC002 验证 general 形状：分块结构齐全即可（与 RC001 同形）
    for block in ("announcement_record", "document_metadata", "announcement_category", "document_evidence"):
        if block not in data:
            return False, f"missing block: {block}"
    if flat.get("quality_status") != "pass":
        return False, f"quality_status={flat.get('quality_status')}, expected pass"
    return True, "general metadata shape ok; required complete; category present"


def _validate_rc003(data: dict) -> Tuple[bool, str]:
    flat = _flatten_record(data)
    if not _is_present(flat.get("announcement_id")):
        return False, "announcement_id missing"
    if not _is_present(flat.get("announcement_title")):
        return False, "announcement_title missing"
    if _is_present(flat.get("pdf_url")):
        return False, "pdf_url should be missing"
    if _is_present(flat.get("adjunct_url")):
        return False, "adjunct_url should be missing"
    if flat.get("quality_status") != "needs_review":
        return False, f"quality_status={flat.get('quality_status')}, expected needs_review"
    if flat.get("quality_status") == "verified":
        return False, "quality_status must not be verified"
    return True, "missing pdf lineage; quality_status=needs_review; not verified"


def _validate_rc004(data: dict) -> Tuple[bool, str]:
    ann_id = data.get("announcement_id")
    candidates = data.get("candidates") or []
    if not ann_id:
        return False, "announcement_id missing at root"
    if len(candidates) < 2:
        return False, f"expected >=2 candidates, got {len(candidates)}"
    ids = [(c.get("announcement_record") or {}).get("announcement_id") for c in candidates]
    if not all(i == ann_id for i in ids):
        return False, "candidate announcement_id mismatch"
    titles = [(c.get("announcement_record") or {}).get("announcement_title") for c in candidates]
    if len(set(titles)) < 2:
        return False, "candidates should differ in metadata"
    exp = data.get("expected_behavior") or {}
    if not exp.get("dedup_decision_required"):
        return False, "dedup_decision_required not true in fixture"
    if exp.get("automatic_merge"):
        return False, "automatic_merge must be false"
    return True, "duplicate detected; candidates preserved; dedup required; no auto merge"


def _validate_rc005(data: dict) -> Tuple[bool, str]:
    flat = _flatten_record(data)
    cat = data.get("announcement_category") or {}
    if flat.get("announcement_category") != "unknown":
        return False, f"announcement_category={flat.get('announcement_category')}, expected unknown"
    if cat.get("category_status") != "review_later":
        return False, f"category_status={cat.get('category_status')}, expected review_later"
    if cat.get("forced_taxonomy_mapping") is True:
        return False, "forced_taxonomy_mapping must be false"
    exp = data.get("expected_behavior") or {}
    if exp.get("forced_taxonomy_mapping") is True:
        return False, "expected_behavior.forced_taxonomy_mapping must be false"
    return True, "unknown category preserved; category_status=review_later; no forced mapping"


def _run_case(row: dict, catalog_required: List[str], pdf_companion: dict) -> CaseResult:
    case_id = row["case_id"]
    fixture_rel = row["input_fixture"]
    fixture_path = _resolve_fixture_path(fixture_rel)
    expected = "PASS"

    if not os.path.isfile(fixture_path):
        return CaseResult(
            case_id, fixture_rel, "error", expected, "ERROR", False, "fixture not found", row.get("notes", "")
        )

    data = _load_json(fixture_path)

    if case_id in ("RC001", "RC002") and "pdf_reference" not in data:
        data = _merge_pdf_companion(data, pdf_companion)

    validators = {
        "RC001": lambda: _validate_rc001(data, catalog_required),
        "RC002": lambda: _validate_rc002(data, catalog_required),
        "RC003": lambda: _validate_rc003(data),
        "RC004": lambda: _validate_rc004(data),
        "RC005": lambda: _validate_rc005(data),
    }
    fn = validators.get(case_id)
    if not fn:
        return CaseResult(
            case_id, fixture_rel, "skipped", expected, "SKIP", False, f"unknown case_id {case_id}", ""
        )

    ok, detail = fn()
    return CaseResult(
        case_id,
        fixture_rel,
        "executed_offline",
        expected,
        "PASS" if ok else "FAIL",
        ok,
        "" if ok else detail,
        detail if ok else row.get("notes", ""),
    )


def _write_report(results: List[CaseResult]) -> None:
    os.makedirs(os.path.dirname(REPORT_CSV), exist_ok=True)
    with open(REPORT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "case_id",
                "fixture",
                "execution_status",
                "expected_result",
                "actual_result",
                "passed",
                "failure_reason",
                "notes",
            ],
        )
        w.writeheader()
        for r in results:
            w.writerow(
                {
                    "case_id": r.case_id,
                    "fixture": r.fixture,
                    "execution_status": r.execution_status,
                    "expected_result": r.expected_result,
                    "actual_result": r.actual_result,
                    "passed": "yes" if r.passed else "no",
                    "failure_reason": r.failure_reason,
                    "notes": r.notes,
                }
            )


def _write_summary(results: List[CaseResult], gate: str) -> None:
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    lines = [
        "# CNINFO B 类 Phase 1 Ready-case Benchmark 离线执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** 离线 fixture 执行；**无 CNINFO**；**无 live**；**无 PDF 下载**。",
        "",
        "## Counts",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| Total cases | {len(results)} |",
        f"| Passed | {passed} |",
        f"| Failed | {failed} |",
        f"| Schema version | {SCHEMA_VERSION} |",
        f"| Executed endpoints | **NONE** |",
        "",
        "## Case Results",
        "",
        "| case_id | actual_result | passed | notes |",
        "|---------|---------------|--------|-------|",
    ]
    for r in results:
        lines.append(f"| {r.case_id} | {r.actual_result} | {'yes' if r.passed else 'no'} | {r.notes} |")
    lines.extend(
        [
            "",
            "## Gate",
            "",
            f"```text",
            f"b_class_ready_case_benchmark_execution_gate = {gate}",
            f"```",
            "",
            "**不是 PASS**（production）· **不是 live approved**。",
            "",
            "## Parallel Safety",
            "",
            "- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**",
            "- `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`: **untouched**",
            "- CNINFO calls: **0**",
            "",
        ]
    )
    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    catalog_required = _load_field_catalog()
    if set(catalog_required) != set(REQUIRED_FIELDS):
        print(
            "WARN: catalog required fields differ from runner constant",
            file=sys.stderr,
        )

    pdf_companion = _load_json(PDF_LINEAGE_COMPANION) if os.path.isfile(PDF_LINEAGE_COMPANION) else {}

    with open(BENCHMARK_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    results = [_run_case(row, catalog_required, pdf_companion) for row in rows]
    gate = "PASS_OFFLINE" if all(r.passed for r in results) else "FAIL"

    _write_report(results)
    _write_summary(results, gate)

    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"{r.case_id} {mark}: {r.notes or r.failure_reason}")

    print(f"\nGate: b_class_ready_case_benchmark_execution_gate = {gate}")
    print(f"Report: {REPORT_CSV}")
    print(f"Summary: {SUMMARY_MD}")
    return 0 if gate == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    sys.exit(main())
