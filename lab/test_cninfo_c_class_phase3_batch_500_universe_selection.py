"""
CNINFO C-class Phase 3 batch 500 universe selection 测试（离线 only）。

运行：
    python lab/test_cninfo_c_class_phase3_batch_500_universe_selection.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from select_cninfo_c_class_phase3_batch_500_universe import (  # noqa: E402
    BASE_DIR,
    SAMPLING_SEED,
    TARGET_SIZE,
    _name_caveat,
    _normalize_code,
    load_already_in_c_class_codes,
    load_phase2_failure_codes,
    load_phase2_smoke_codes,
    select_batch_500_universe,
    write_batch_yaml,
)
from select_cninfo_c_class_phase2_smoke_universe import _load_csv, REFRESHED_CSV  # noqa: E402

SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_universe_selection_test_summary.md",
)


class TestPhase3Batch500UniverseSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.selected, cls.matrix, cls.stats = select_batch_500_universe()
        cls.phase2_smoke = load_phase2_smoke_codes()
        cls.phase2_failure = load_phase2_failure_codes()
        cls.era_c = load_already_in_c_class_codes(_load_csv(REFRESHED_CSV))

    def test_case1_selected_count_500(self) -> None:
        self.assertEqual(len(self.selected), TARGET_SIZE)
        self.assertEqual(self.stats["selected_count"], TARGET_SIZE)

    def test_case2_only_matched_active(self) -> None:
        for row in self.selected:
            self.assertEqual(row["reconciliation_classification"], "matched_active")
            self.assertEqual(row["refresh_action"], "full_market_active_candidate")

    def test_case3_no_phase2_smoke(self) -> None:
        codes = {_normalize_code(r["company_code"]) for r in self.selected}
        self.assertFalse(codes & self.phase2_smoke)

    def test_case4_no_phase2_failure(self) -> None:
        codes = {_normalize_code(r["company_code"]) for r in self.selected}
        self.assertFalse(codes & self.phase2_failure)

    def test_case5_no_863_active(self) -> None:
        codes = {_normalize_code(r["company_code"]) for r in self.selected}
        self.assertFalse(codes & self.era_c)

    def test_case6_no_bse(self) -> None:
        for row in self.selected:
            self.assertNotEqual(str(row.get("board", "")).lower(), "bse")

    def test_case7_no_hold(self) -> None:
        for row in self.selected:
            self.assertNotEqual(row["reconciliation_classification"], "matched_hold")

    def test_case8_no_manual_review_or_identity_conflict(self) -> None:
        for row in self.selected:
            self.assertNotEqual(row["reconciliation_classification"], "needs_manual_review")
            self.assertNotEqual(row["reconciliation_classification"], "identity_conflict")
            self.assertEqual(str(row.get("requires_manual_review", "")).lower(), "false")

    def test_case9_no_delisted_or_name_caveat(self) -> None:
        for row in self.selected:
            self.assertNotEqual(str(row.get("listing_status", "")).lower(), "delisted")
            self.assertFalse(_name_caveat(row.get("company_name", "")))

    def test_case10_no_duplicate_company_code(self) -> None:
        codes = [_normalize_code(r["company_code"]) for r in self.selected]
        self.assertEqual(len(codes), len(set(codes)))

    def test_case11_deterministic_seed_stable(self) -> None:
        s1, _, _ = select_batch_500_universe(seed=SAMPLING_SEED)
        s2, _, _ = select_batch_500_universe(seed=SAMPLING_SEED)
        codes1 = [_normalize_code(r["company_code"]) for r in s1]
        codes2 = [_normalize_code(r["company_code"]) for r in s2]
        self.assertEqual(codes1, codes2)

    def test_case12_yaml_only_with_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            yaml_path = os.path.join(tmp, "batch.yaml")
            self.assertFalse(os.path.exists(yaml_path))
            selected, _, stats = select_batch_500_universe()
            self.assertFalse(os.path.exists(yaml_path))
            write_batch_yaml(selected, stats, yaml_path)
            self.assertTrue(os.path.exists(yaml_path))
            data = yaml.safe_load(open(yaml_path, encoding="utf-8"))
            self.assertEqual(data["company_count"], TARGET_SIZE)
            self.assertEqual(len(data["companies"]), TARGET_SIZE)
            self.assertEqual(data["batch_id"], "phase3_batch_500_001")


def _write_test_summary(passed: int, total: int) -> None:
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write(
            f"# Phase 3 Batch 500 Selection Test Summary\n\n"
            f"| 结果 | **{passed}/{total} PASS** |\n"
        )


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPhase3Batch500UniverseSelection)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    _write_test_summary(passed, total)
    print(f"\n{passed}/{total} PASS")
    sys.exit(0 if result.wasSuccessful() else 1)
