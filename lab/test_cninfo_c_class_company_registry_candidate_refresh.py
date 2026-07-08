"""
CNINFO C-class registry candidate refresh 测试（离线 only）。

运行：
    python lab/test_cninfo_c_class_company_registry_candidate_refresh.py
"""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from refresh_cninfo_c_class_company_registry_candidate import (  # noqa: E402
    BASE_COLUMNS,
    BASE_DIR,
    LEDGER_CSV,
    RECONCILIATION_CSV,
    CANDIDATE_DRAFT_CSV,
    refresh_candidate_row,
    refresh_candidates,
    _load_csv,
)

SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_company_registry_candidate_refresh_test_summary.md",
)


def _row_by_code(rows: list, code: str) -> dict:
    code = code.zfill(6)
    for r in rows:
        if r["company_code"].zfill(6) == code:
            return r
    raise KeyError(code)


class TestRegistryCandidateRefresh(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.refreshed, cls.stats = refresh_candidates()

    def test_case1_already_in_c_class_high_confidence(self) -> None:
        """case 1: already_in_c_class preserves high confidence"""
        row = _row_by_code(self.refreshed, "000009")
        self.assertEqual(row["reconciliation_classification"], "already_in_c_class")
        self.assertEqual(row["refresh_confidence"], "high")
        self.assertEqual(row["confidence"], "high")
        self.assertEqual(row["refresh_action"], "preserve_high_confidence")

    def test_case2_matched_active_full_market_candidate(self) -> None:
        """case 2: matched_active becomes full_market_active_candidate"""
        row = _row_by_code(self.refreshed, "000001")
        self.assertEqual(row["reconciliation_classification"], "matched_active")
        self.assertEqual(row["refresh_action"], "full_market_active_candidate")
        self.assertEqual(row["harvest_support_status"], "candidate_supported")
        self.assertEqual(row["snapshot_support_status"], "not_built")

    def test_case3_matched_hold_preserved(self) -> None:
        """case 3: matched_hold preserves hold"""
        row = _row_by_code(self.refreshed, "000043")
        self.assertEqual(row["reconciliation_classification"], "matched_hold")
        self.assertEqual(row["refresh_action"], "preserve_hold")
        self.assertEqual(row["harvest_support_status"], "hold")
        self.assertEqual(row["hold_flag"], "true")

    def test_case4_bse_legacy_hold_preserved(self) -> None:
        """case 4: matched_bse_legacy_hold preserves legacy_hold"""
        row = _row_by_code(self.refreshed, "832491")
        self.assertEqual(row["reconciliation_classification"], "matched_bse_legacy_hold")
        self.assertEqual(row["refresh_action"], "preserve_legacy_hold")
        self.assertEqual(row["harvest_support_status"], "legacy_hold")

    def test_case5_identity_conflict_manual_review(self) -> None:
        """case 5: identity_conflict requires manual review"""
        row = _row_by_code(self.refreshed, "000022")
        self.assertEqual(row["reconciliation_classification"], "identity_conflict")
        self.assertEqual(row["requires_manual_review"], "true")
        self.assertEqual(row["refresh_action"], "conflict_review_required")

    def test_case6_needs_manual_review(self) -> None:
        """case 6: needs_manual_review requires manual review"""
        row = _row_by_code(self.refreshed, "600631")
        self.assertEqual(row["reconciliation_classification"], "needs_manual_review")
        self.assertEqual(row["requires_manual_review"], "true")
        self.assertEqual(row["refresh_action"], "manual_review_required")

    def test_case7_same_name_no_merge(self) -> None:
        """case 7: same-name / identity conflict does not merge"""
        row631 = _row_by_code(self.refreshed, "600631")
        row827 = _row_by_code(self.refreshed, "600827")
        self.assertNotEqual(row631["company_id"], row827["company_id"])
        self.assertEqual(row631["company_code"], "600631")
        self.assertEqual(row827["company_code"], "600827")
        self.assertIn("merge_executed=false", row631["lineage_note"])
        self.assertIn("merge_executed=false", row827["lineage_note"])

    def test_refresh_row_count_matches_draft(self) -> None:
        self.assertEqual(self.stats["refreshed_count"], self.stats["candidate_draft_count"])
        self.assertEqual(self.stats["classification_counts"].get("already_in_c_class"), 863)


def _write_test_summary(passed: int, total: int) -> None:
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(f"# Registry Candidate Refresh Test Summary\n\n| 结果 | **{passed}/{total} PASS** |\n")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestRegistryCandidateRefresh)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    _write_test_summary(passed, total)
    print(f"\n{passed}/{total} PASS")
    sys.exit(0 if result.wasSuccessful() else 1)
