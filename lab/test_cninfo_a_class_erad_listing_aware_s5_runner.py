"""
A-class listing-aware S5 runner 路径隔离测试（mock · CNINFO = 0）。

运行：
    python lab/test_cninfo_a_class_erad_listing_aware_s5_runner.py
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402


class ListingAwareS5RunnerTests(unittest.TestCase):
    def test_mode_detection_and_cap(self) -> None:
        self.assertTrue(
            runner.is_erad_listing_aware_s5_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, None
            )
        )
        self.assertFalse(
            runner.is_erad_listing_aware_s5_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, None
            )
        )
        self.assertFalse(
            runner.is_erad_listing_aware_s4_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, None
            )
        )
        self.assertEqual(
            runner.erad_slice2_request_cap_for_mode(listing_aware_s5=True),
            runner.ERAD_LISTING_AWARE_S5_REQUEST_CAP,
        )

    def test_closed_s1_s2_s3_s4_roots_forbidden(self) -> None:
        ok, err = runner.validate_erad_listing_aware_s5_output_root(
            runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT
        )
        self.assertFalse(ok)
        self.assertEqual(err, runner.ERAD_LISTING_AWARE_S5_CLOSED_ROOT_WRITE_FORBIDDEN)
        ok2, err2 = runner.validate_erad_listing_aware_s5_output_root(
            runner.DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT
        )
        self.assertFalse(ok2)
        self.assertEqual(err2, runner.ERAD_LISTING_AWARE_S5_CLOSED_ROOT_WRITE_FORBIDDEN)
        ok3, err3 = runner.validate_erad_listing_aware_s5_output_root(
            runner.DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT
        )
        self.assertFalse(ok3)
        self.assertEqual(err3, runner.ERAD_LISTING_AWARE_S5_CLOSED_ROOT_WRITE_FORBIDDEN)
        ok4, err4 = runner.validate_erad_listing_aware_s5_output_root(
            runner.DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT
        )
        self.assertFalse(ok4)
        self.assertEqual(err4, runner.ERAD_LISTING_AWARE_S5_CLOSED_ROOT_WRITE_FORBIDDEN)

    def test_allowed_root_ok(self) -> None:
        ok, err = runner.validate_erad_listing_aware_s5_output_root(
            runner.DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT
        )
        self.assertTrue(ok)
        self.assertEqual(err, "")

    def test_universe_load_and_size(self) -> None:
        if not os.path.isfile(runner.DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV):
            self.skipTest("listing-aware S5 universe CSV not generated yet")
        cases = runner.load_erad_next_scale_slice2_universe(
            runner.DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV
        )
        ok, err = runner.validate_erad_listing_aware_s5_universe_size(cases)
        self.assertTrue(ok, err)
        self.assertEqual(cases[0].cohort, runner.ERAD_LISTING_AWARE_S5_COHORT)
        self.assertEqual(cases[0].case_id, "AD2E751")
        self.assertEqual(cases[-1].case_id, "AD2E800")
        issues = runner.lint_erad_listing_aware_s5_overlap(cases)
        self.assertEqual(issues, [])

    def test_case_range_allows_751_800_blocks_cross_band(self) -> None:
        start, end = runner.parse_erad_a_slice2_case_range("AD2E751:AD2E775")
        self.assertEqual(start, "AD2E751")
        self.assertEqual(end, "AD2E775")
        with self.assertRaises(ValueError):
            runner.parse_erad_a_slice2_case_range("AD2E740:AD2E760")
        with self.assertRaises(ValueError):
            runner.parse_erad_a_slice2_case_range("AD2E700:AD2E780")


if __name__ == "__main__":
    unittest.main()
