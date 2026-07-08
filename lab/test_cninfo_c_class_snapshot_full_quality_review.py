"""
CNINFO C-class snapshot full quality review 测试（只读 · 无 CNINFO）。

运行：
    python lab/test_cninfo_c_class_snapshot_full_quality_review.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from typing import Any, Dict

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from review_cninfo_c_class_snapshot_full_quality import (  # noqa: E402
    BASE_DIR,
    EXPECTED_COMPANY_COUNT,
    SNAPSHOT_MODULES,
    detect_quality_flags,
    detect_schema_drift,
    load_all_valid_snapshots,
    run_completeness_check,
    run_field_coverage,
    run_full_quality_review,
    run_module_coverage,
    write_quality_summary,
)
from build_cninfo_c_class_company_snapshot import build_snapshot, _load_mapping  # noqa: E402

FULL_DIR = os.path.join(BASE_DIR, "outputs/snapshot/cninfo_c_class/full")
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_snapshot_full_quality_review_test_summary.md",
)


def _minimal_snapshot(code: str, mod_status: str = "available") -> Dict[str, Any]:
    modules = {}
    for mod in SNAPSHOT_MODULES:
        if mod == "technology_profile":
            modules[mod] = {"fields": {}, "status": "not_available", "sources": []}
        elif mod in {"shareholder_profile", "executive_profile"}:
            key = "shareholders" if mod == "shareholder_profile" else "executives"
            modules[mod] = {
                "fields": {key: [{"person_name": "A", "scope": "x"}]} if mod == "shareholder_profile" else {key: [{"person_name": "A"}]},
                "status": "partial",
                "sources": ["cninfo_executive_profile"],
            }
        else:
            modules[mod] = {
                "fields": {"company_code": code} if mod == "company_identity" else {},
                "status": mod_status,
                "sources": ["cninfo_company_basic_profile"],
            }
    return {
        "company_code": code,
        "company_name": f"Co{code}",
        "snapshot_status": "complete_with_caveat",
        "modules": modules,
    }


class TestSnapshotFullQualityReview(unittest.TestCase):
    def test_case1_863_snapshot_count_check(self) -> None:
        snapshots = load_all_valid_snapshots(FULL_DIR)
        self.assertEqual(len(snapshots), EXPECTED_COMPANY_COUNT)
        rows, stats = run_completeness_check(FULL_DIR)
        self.assertEqual(stats["snapshot_json_count"], EXPECTED_COMPANY_COUNT)
        self.assertEqual(stats["valid_json_count"], EXPECTED_COMPANY_COUNT)
        self.assertEqual(stats["malformed_json_count"], 0)
        self.assertEqual(len(rows), EXPECTED_COMPANY_COUNT)

    def test_case2_module_coverage_calculation(self) -> None:
        snapshots = load_all_valid_snapshots(FULL_DIR)
        rows = run_module_coverage(snapshots)
        self.assertEqual(len(rows), len(SNAPSHOT_MODULES))
        tech = next(r for r in rows if r["module"] == "technology_profile")
        self.assertEqual(tech["not_available_count"], EXPECTED_COMPANY_COUNT)
        self.assertEqual(tech["available_count"], 0)
        identity = next(r for r in rows if r["module"] == "company_identity")
        self.assertEqual(identity["available_count"], EXPECTED_COMPANY_COUNT)

    def test_case3_missing_field_detection(self) -> None:
        mapping = _load_mapping()
        snapshots = load_all_valid_snapshots(FULL_DIR)
        field_rows = run_field_coverage(snapshots, mapping)
        self.assertGreater(len(field_rows), 0)
        tech_fields = [r for r in field_rows if r["module"] == "technology_profile"]
        if tech_fields:
            for row in tech_fields:
                self.assertEqual(row["available_count"], 0)
        high_missing = [r for r in field_rows if r["missing_rate"] >= 0.99]
        self.assertGreater(len(high_missing), 0)

    def test_case4_schema_drift_detection_mock(self) -> None:
        s1 = _minimal_snapshot("000001")
        s2 = _minimal_snapshot("000002")
        s2["modules"]["company_identity"]["fields"].update({
            "extra_a": "1", "extra_b": "2", "extra_c": "3",
        })
        flags = detect_schema_drift({"000001": s1, "000002": s2})
        self.assertTrue(any(f["flag_type"] == "schema_drift" for f in flags))

    def test_case5_quality_summary_generation(self) -> None:
        snapshots = {"000001": _minimal_snapshot("000001")}
        module_rows = run_module_coverage(snapshots)
        field_rows = run_field_coverage(snapshots, _load_mapping())
        flag_rows = detect_quality_flags(snapshots, _load_mapping())
        stats = {
            "snapshot_json_count": 1,
            "valid_json_count": 1,
            "malformed_json_count": 0,
            "empty_snapshot_count": 0,
            "duplicate_company_codes": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "summary.md")
            write_quality_summary(stats, module_rows, field_rows, flag_rows, path=path)
            self.assertTrue(os.path.isfile(path))
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("SNAPSHOT_GENERATED_QA_REVIEW", content)
            self.assertIn("Module Coverage", content)


def write_test_summary(results: list) -> None:
    passed = sum(1 for r in results if r["status"] == "PASS")
    lines = [
        "# CNINFO C-Class Snapshot Full Quality Review Test Summary",
        "",
        f"**{passed}/{len(results)} PASS**",
        "",
        "| case | status |",
        "|------|--------|",
    ]
    for r in results:
        lines.append(f"| {r['case']} | **{r['status']}** |")
    lines.extend([
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## 红线确认",
        "",
        "- 测试只读 snapshot · 未修改 JSON / normalized",
    ])
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSnapshotFullQualityReview)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    cases = [
        ("case_1_863_snapshot_count_check", "test_case1_863_snapshot_count_check"),
        ("case_2_module_coverage_calculation", "test_case2_module_coverage_calculation"),
        ("case_3_missing_field_detection", "test_case3_missing_field_detection"),
        ("case_4_schema_drift_detection_mock", "test_case4_schema_drift_detection_mock"),
        ("case_5_quality_summary_generation", "test_case5_quality_summary_generation"),
    ]
    test_results = []
    for label, test_id in cases:
        failed = any(test_id in str(f) for f in result.failures + result.errors)
        test_results.append({"case": label, "status": "FAIL" if failed else "PASS"})

    write_test_summary(test_results)
    print(f"\nTest summary: {SUMMARY_PATH}")
    print(f"Result: {sum(1 for r in test_results if r['status']=='PASS')}/{len(test_results)} PASS")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
