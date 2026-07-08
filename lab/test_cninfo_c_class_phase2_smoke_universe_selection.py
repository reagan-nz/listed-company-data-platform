"""
CNINFO C-class Phase 2 smoke universe selection 测试（离线 only）。

运行：
    python lab/test_cninfo_c_class_phase2_smoke_universe_selection.py
"""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import unittest

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from select_cninfo_c_class_phase2_smoke_universe import (  # noqa: E402
    BASE_DIR,
    REFRESHED_CSV,
    SAMPLING_SEED,
    TARGET_SIZE,
    select_smoke_universe,
    write_smoke_yaml,
)

SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase2_smoke_universe_selection_test_summary.md",
)


class TestPhase2SmokeUniverseSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.selected, cls.matrix, cls.stats = select_smoke_universe()

    def test_case1_selected_count_200(self) -> None:
        """case 1: selected count = 200"""
        self.assertEqual(len(self.selected), TARGET_SIZE)
        self.assertEqual(self.stats["selected_count"], TARGET_SIZE)

    def test_case2_only_matched_active(self) -> None:
        """case 2: only matched_active included"""
        for row in self.selected:
            self.assertEqual(row["reconciliation_classification"], "matched_active")
            self.assertEqual(row["refresh_action"], "full_market_active_candidate")

    def test_case3_no_manual_review(self) -> None:
        """case 3: no manual_review rows included"""
        for row in self.selected:
            self.assertEqual(str(row.get("requires_manual_review", "")).lower(), "false")
            self.assertNotEqual(row["reconciliation_classification"], "needs_manual_review")

    def test_case4_no_hold_rows(self) -> None:
        """case 4: no hold rows included"""
        for row in self.selected:
            self.assertNotEqual(row["reconciliation_classification"], "matched_hold")
            self.assertNotEqual(row.get("harvest_support_status"), "hold")

    def test_case5_no_bse_rows(self) -> None:
        """case 5: no BSE rows included"""
        for row in self.selected:
            self.assertNotEqual(str(row.get("board", "")).lower(), "bse")
            self.assertNotEqual(row["reconciliation_classification"], "matched_bse_supported_candidate")
            self.assertNotEqual(row["reconciliation_classification"], "matched_bse_legacy_hold")

    def test_case6_no_duplicate_company_code(self) -> None:
        """case 6: no duplicate company_code"""
        codes = [r["company_code"].zfill(6) for r in self.selected]
        self.assertEqual(len(codes), len(set(codes)))

    def test_case7_deterministic_seed_stable(self) -> None:
        """case 7: deterministic seed produces stable output"""
        s1, _, _ = select_smoke_universe(seed=SAMPLING_SEED)
        s2, _, _ = select_smoke_universe(seed=SAMPLING_SEED)
        codes1 = [r["company_code"].zfill(6) for r in s1]
        codes2 = [r["company_code"].zfill(6) for r in s2]
        self.assertEqual(codes1, codes2)

    def test_case8_yaml_only_with_write(self) -> None:
        """case 8: YAML generated only with --write"""
        with tempfile.TemporaryDirectory() as tmp:
            yaml_path = os.path.join(tmp, "smoke.yaml")
            self.assertFalse(os.path.exists(yaml_path))
            selected, _, stats = select_smoke_universe()
            # dry-run path: no write call
            self.assertFalse(os.path.exists(yaml_path))
            write_smoke_yaml(selected, stats, yaml_path)
            self.assertTrue(os.path.exists(yaml_path))
            data = yaml.safe_load(open(yaml_path, encoding="utf-8"))
            self.assertEqual(data["company_count"], TARGET_SIZE)
            self.assertEqual(len(data["companies"]), TARGET_SIZE)


def _write_test_summary(passed: int, total: int) -> None:
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(f"# Phase 2 Smoke Selection Test Summary\n\n| 结果 | **{passed}/{total} PASS** |\n")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPhase2SmokeUniverseSelection)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    _write_test_summary(passed, total)
    print(f"\n{passed}/{total} PASS")
    sys.exit(0 if result.wasSuccessful() else 1)
