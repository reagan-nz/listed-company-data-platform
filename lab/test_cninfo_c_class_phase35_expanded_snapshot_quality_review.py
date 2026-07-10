"""
CNINFO C-class Phase 3.5 expanded snapshot quality review 测试（只读 · 无 CNINFO）。

运行：
    python lab/test_cninfo_c_class_phase35_expanded_snapshot_quality_review.py
"""

from __future__ import annotations

import csv
import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from review_cninfo_c_class_phase35_expanded_snapshot_quality import (  # noqa: E402
    BASE_DIR,
    C35R016_CODE,
    EXPECTED_COMPANY_COUNT,
    EXPECTED_ORIGINAL_COUNT,
    EXPECTED_RESUME_COUNT,
    HOLD_FOR_REVIEW_CODES,
    PHASE35_SNAPSHOT_DIR,
    QA_CASE_LEDGER_CSV,
    QA_HOLDOUT_CONFIRMATION_CSV,
    QA_METRICS_CSV,
    QA_SUMMARY_MD,
    STATUS_CSV,
    load_all_valid_snapshots,
    load_universe_rows,
    run_phase35_expanded_snapshot_quality_review,
)

TEST_SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_quality_review_test_summary.md",
)


class TestPhase35ExpandedSnapshotQualityReview(unittest.TestCase):
    def test_case1_491_json_files_detected(self) -> None:
        snapshots, stats = load_all_valid_snapshots(PHASE35_SNAPSHOT_DIR)
        self.assertEqual(stats["json_count"], EXPECTED_COMPANY_COUNT)
        self.assertEqual(len(snapshots), EXPECTED_COMPANY_COUNT)

    def test_case2_universe_one_snapshot_per_company(self) -> None:
        universe = load_universe_rows()
        snapshots, _ = load_all_valid_snapshots(PHASE35_SNAPSHOT_DIR)
        self.assertEqual(len(universe), EXPECTED_COMPANY_COUNT)
        self.assertEqual(set(snapshots.keys()), {r["company_code"] for r in universe})

    def test_case3_c35r016_absent(self) -> None:
        _, stats = load_all_valid_snapshots(PHASE35_SNAPSHOT_DIR)
        self.assertFalse(stats["c35r016_present"])
        paths = {
            os.path.basename(p)[:-5]
            for p in os.listdir(PHASE35_SNAPSHOT_DIR)
            if p.endswith(".json")
        }
        self.assertNotIn(C35R016_CODE, paths)

    def test_case4_hold_for_review_absent(self) -> None:
        _, stats = load_all_valid_snapshots(PHASE35_SNAPSHOT_DIR)
        self.assertEqual(stats["hold_for_review_present_count"], 0)
        paths = {
            os.path.basename(p)[:-5]
            for p in os.listdir(PHASE35_SNAPSHOT_DIR)
            if p.endswith(".json")
        }
        self.assertFalse(paths & HOLD_FOR_REVIEW_CODES)

    def test_case5_original_resume_split(self) -> None:
        universe = load_universe_rows()
        original_n = sum(1 for r in universe if r["source_root_role"] == "original")
        resume_n = sum(1 for r in universe if r["source_root_role"] == "resume")
        self.assertEqual(original_n, EXPECTED_ORIGINAL_COUNT)
        self.assertEqual(resume_n, EXPECTED_RESUME_COUNT)

    def test_case6_invalid_json_count_zero(self) -> None:
        _, stats = load_all_valid_snapshots(PHASE35_SNAPSHOT_DIR)
        self.assertEqual(stats["invalid_json_count"], 0)
        self.assertEqual(stats["valid_json_count"], EXPECTED_COMPANY_COUNT)

    def test_case7_qa_outputs_generated(self) -> None:
        result = run_phase35_expanded_snapshot_quality_review()
        self.assertTrue(os.path.isfile(QA_SUMMARY_MD))
        self.assertTrue(os.path.isfile(QA_METRICS_CSV))
        self.assertTrue(os.path.isfile(QA_CASE_LEDGER_CSV))
        self.assertTrue(os.path.isfile(QA_HOLDOUT_CONFIRMATION_CSV))
        with open(QA_CASE_LEDGER_CSV, encoding="utf-8") as fh:
            ledger = list(csv.DictReader(fh))
        with open(QA_HOLDOUT_CONFIRMATION_CSV, encoding="utf-8") as fh:
            holdout = list(csv.DictReader(fh))
        self.assertEqual(len(ledger), EXPECTED_COMPANY_COUNT)
        self.assertEqual(len(holdout), 9)
        self.assertIn(
            "phase35_expanded_success_subset_snapshot_qa_gate = PASS_WITH_CAVEAT",
            open(QA_SUMMARY_MD, encoding="utf-8").read(),
        )
        self.assertEqual(result["gate"], "PASS_WITH_CAVEAT")

    def test_case8_holdout_excluded_confirmed(self) -> None:
        run_phase35_expanded_snapshot_quality_review()
        with open(QA_HOLDOUT_CONFIRMATION_CSV, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertTrue(all(r["snapshot_json_present"] == "false" for r in rows))
        self.assertTrue(all(r["qa_outcome"] == "excluded_holdout_confirmed" for r in rows))
        c35 = next(r for r in rows if r["company_code"] == C35R016_CODE)
        self.assertEqual(c35["resume_qa_classification"], "still_partial")

    def test_case9_no_db_minio_rag_markers(self) -> None:
        run_phase35_expanded_snapshot_quality_review()
        with open(QA_METRICS_CSV, encoding="utf-8") as fh:
            metrics = {r["metric_name"]: r["metric_value"] for r in csv.DictReader(fh)}
        self.assertEqual(metrics.get("cninfo_calls"), "0")
        self.assertEqual(metrics.get("db_writes"), "0")
        self.assertEqual(metrics.get("minio_writes"), "0")
        self.assertEqual(metrics.get("rag_runs"), "0")

    def test_case10_status_csv_regenerated_from_json(self) -> None:
        run_phase35_expanded_snapshot_quality_review()
        self.assertTrue(os.path.isfile(STATUS_CSV))
        with open(STATUS_CSV, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), EXPECTED_COMPANY_COUNT)
        self.assertTrue(all(r.get("qa_review_status") == "reviewed" for r in rows))


def write_test_summary(results: list) -> None:
    passed = sum(1 for r in results if r["status"] == "PASS")
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Quality Review Test Summary",
        "",
        f"**{passed}/{len(results)} PASS**",
        "",
        "| case | status |",
        "|------|--------|",
    ]
    for r in results:
        lines.append(f"| {r['case']} | **{r['status']}** |")
    os.makedirs(os.path.dirname(TEST_SUMMARY_PATH), exist_ok=True)
    with open(TEST_SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase35ExpandedSnapshotQualityReview)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    cases = [
        ("case_1_491_json", "test_case1_491_json_files_detected"),
        ("case_2_one_per_company", "test_case2_universe_one_snapshot_per_company"),
        ("case_3_c35r016_absent", "test_case3_c35r016_absent"),
        ("case_4_hold_absent", "test_case4_hold_for_review_absent"),
        ("case_5_split_463_28", "test_case5_original_resume_split"),
        ("case_6_invalid_zero", "test_case6_invalid_json_count_zero"),
        ("case_7_qa_outputs", "test_case7_qa_outputs_generated"),
        ("case_8_holdout_confirmed", "test_case8_holdout_excluded_confirmed"),
        ("case_9_no_db_minio_rag", "test_case9_no_db_minio_rag_markers"),
        ("case_10_status_csv", "test_case10_status_csv_regenerated_from_json"),
    ]
    failed = {t[0]._testMethodName for t in result.failures + result.errors}  # type: ignore[attr-defined]
    final = [(label, test_id not in failed) for label, test_id in cases]
    write_test_summary([{"case": c, "status": "PASS" if ok else "FAIL"} for c, ok in final])
    passed = sum(1 for _, ok in final if ok)
    print(f"\n{passed}/{len(final)} PASS")
    print(f"MD    {TEST_SUMMARY_PATH}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
