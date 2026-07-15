"""
A-class listing-aware S2 runner 路径隔离测试（mock · CNINFO = 0）。

运行：
    python lab/test_cninfo_a_class_erad_listing_aware_s2_runner.py
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402


class ListingAwareS2RunnerTests(unittest.TestCase):
    def test_mode_detection_and_cap(self) -> None:
        self.assertTrue(
            runner.is_erad_listing_aware_s2_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, None
            )
        )
        self.assertFalse(
            runner.is_erad_listing_aware_s2_mode(
                runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, None
            )
        )
        self.assertEqual(
            runner.erad_slice2_request_cap_for_mode(listing_aware_s2=True),
            runner.ERAD_LISTING_AWARE_S2_REQUEST_CAP,
        )

    def test_closed_s1_root_forbidden(self) -> None:
        ok, err = runner.validate_erad_listing_aware_s2_output_root(
            runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT
        )
        self.assertFalse(ok)
        self.assertEqual(err, runner.ERAD_LISTING_AWARE_S2_CLOSED_ROOT_WRITE_FORBIDDEN)

    def test_allowed_root_ok(self) -> None:
        ok, err = runner.validate_erad_listing_aware_s2_output_root(
            runner.DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT
        )
        self.assertTrue(ok)
        self.assertEqual(err, "")

    def test_universe_load_and_size(self) -> None:
        if not os.path.isfile(runner.DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV):
            self.skipTest("listing-aware universe CSV not generated yet")
        cases = runner.load_erad_next_scale_slice2_universe(
            runner.DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV
        )
        ok, err = runner.validate_erad_listing_aware_s2_universe_size(cases)
        self.assertTrue(ok, err)
        self.assertEqual(cases[0].cohort, runner.ERAD_LISTING_AWARE_S2_COHORT)
        self.assertEqual(cases[0].case_id, "AD2E601")
        self.assertEqual(cases[-1].case_id, "AD2E650")
        issues = runner.lint_erad_listing_aware_s2_overlap(cases)
        self.assertEqual(issues, [])

    def test_case_range_allows_601_650(self) -> None:
        start, end = runner.parse_erad_a_slice2_case_range("AD2E601:AD2E625")
        self.assertEqual(start, "AD2E601")
        self.assertEqual(end, "AD2E625")
        with self.assertRaises(ValueError):
            runner.parse_erad_a_slice2_case_range("AD2E550:AD2E620")


if __name__ == "__main__":
    unittest.main()
