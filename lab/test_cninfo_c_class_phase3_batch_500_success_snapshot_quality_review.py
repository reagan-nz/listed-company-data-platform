"""
CNINFO C-class Phase 3 batch 500 success-subset snapshot quality review 测试（只读 · 无 CNINFO）。

运行：
    python lab/test_cninfo_c_class_phase3_batch_500_success_snapshot_quality_review.py
"""

from __future__ import annotations

import csv
import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from review_cninfo_c_class_phase3_batch_500_success_snapshot_quality import (  # noqa: E402
    BASE_DIR,
    COMPLETENESS_CSV,
    EXPECTED_COMPANY_COUNT,
    EXCLUDED_CODES,
    MODULE_COVERAGE_CSV,
    PHASE3_SNAPSHOT_DIR,
    QA_SUMMARY_MD,
    QUALITY_FLAGS_CSV,
    STATUS_CSV,
    load_all_valid_snapshots,
    run_phase3_success_snapshot_quality_review,
)

TEST_SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_quality_review_test_summary.md",
)


class TestPhase3SuccessSnapshotQualityReview(unittest.TestCase):
    def test_case1_491_json_files_detected(self) -> None:
        snapshots, stats = load_all_valid_snapshots(PHASE3_SNAPSHOT_DIR)
        self.assertEqual(stats["json_count"], EXPECTED_COMPANY_COUNT)
        self.assertEqual(len(snapshots), EXPECTED_COMPANY_COUNT)

    def test_case2_invalid_json_count_zero(self) -> None:
        _, stats = load_all_valid_snapshots(PHASE3_SNAPSHOT_DIR)
        self.assertEqual(stats["invalid_json_count"], 0)
        self.assertEqual(stats["valid_json_count"], EXPECTED_COMPANY_COUNT)

    def test_case3_excluded_codes_absent(self) -> None:
        _, stats = load_all_valid_snapshots(PHASE3_SNAPSHOT_DIR)
        self.assertEqual(stats["excluded_code_present_count"], 0)
        paths = {
            os.path.basename(p)[:-5]
            for p in os.listdir(PHASE3_SNAPSHOT_DIR)
            if p.endswith(".json")
        }
        self.assertFalse(paths & set(EXCLUDED_CODES))

    def test_case4_no_duplicate_company_code(self) -> None:
        _, stats = load_all_valid_snapshots(PHASE3_SNAPSHOT_DIR)
        self.assertEqual(stats["duplicate_company_code_count"], 0)

    def test_case5_quality_reports_generated(self) -> None:
        run_phase3_success_snapshot_quality_review()
        self.assertTrue(os.path.isfile(COMPLETENESS_CSV))
        self.assertTrue(os.path.isfile(MODULE_COVERAGE_CSV))
        self.assertTrue(os.path.isfile(QUALITY_FLAGS_CSV))
        self.assertTrue(os.path.isfile(QA_SUMMARY_MD))
        with open(COMPLETENESS_CSV, encoding="utf-8") as fh:
            completeness = list(csv.DictReader(fh))
        with open(MODULE_COVERAGE_CSV, encoding="utf-8") as fh:
            modules = list(csv.DictReader(fh))
        self.assertEqual(len(completeness), EXPECTED_COMPANY_COUNT)
        self.assertGreater(len(modules), 0)
        with open(QA_SUMMARY_MD, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("phase3_batch_500_success_snapshot_qa_gate = PASS_WITH_CAVEAT", content)

    def test_case6_status_csv_regenerated_from_json(self) -> None:
        result = run_phase3_success_snapshot_quality_review()
        self.assertTrue(os.path.isfile(STATUS_CSV))
        with open(STATUS_CSV, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), EXPECTED_COMPANY_COUNT)
        self.assertTrue(all(r.get("file_exists") == "true" for r in rows))
        self.assertTrue(all(r.get("qa_review_status") == "reviewed" for r in rows))
        self.assertTrue(all(r.get("snapshot_status") for r in rows))
        self.assertTrue(all(r.get("retry_status") == "done" for r in rows))
        pending = [r for r in rows if r.get("status") == "pending"]
        self.assertEqual(len(pending), 0)
        self.assertEqual(result["gate"], "PASS_WITH_CAVEAT")


def write_test_summary(results: list) -> None:
    passed = sum(1 for r in results if r["status"] == "PASS")
    lines = [
        "# CNINFO C-Class Phase 3 Success-Subset Snapshot Quality Review Test Summary",
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
        "- 测试只读 snapshot JSON · status CSV 校正为 QA 产物",
    ])
    os.makedirs(os.path.dirname(TEST_SUMMARY_PATH), exist_ok=True)
    with open(TEST_SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase3SuccessSnapshotQualityReview)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    cases = [
        ("case_1_491_json_files_detected", "test_case1_491_json_files_detected"),
        ("case_2_invalid_json_count_zero", "test_case2_invalid_json_count_zero"),
        ("case_3_excluded_codes_absent", "test_case3_excluded_codes_absent"),
        ("case_4_no_duplicate_company_code", "test_case4_no_duplicate_company_code"),
        ("case_5_quality_reports_generated", "test_case5_quality_reports_generated"),
        ("case_6_status_csv_regenerated_from_json", "test_case6_status_csv_regenerated_from_json"),
    ]
    test_results = []
    for label, test_id in cases:
        failed = any(test_id in str(f) for f in result.failures + result.errors)
        test_results.append({"case": label, "status": "FAIL" if failed else "PASS"})

    write_test_summary(test_results)
    print(f"\nTest summary: {TEST_SUMMARY_PATH}")
    print(f"Result: {sum(1 for r in test_results if r['status']=='PASS')}/{len(test_results)} PASS")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
