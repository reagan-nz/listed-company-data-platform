"""
A-class listing-aware S23 runner 路径隔离测试（mock · CNINFO = 0）。

运行：
    python lab/test_cninfo_a_class_erad_listing_aware_s23_runner.py
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402


class ListingAwareS23RunnerTests(unittest.TestCase):
    def test_mode_detection_and_cap(self) -> None:
        self.assertTrue(
            runner.is_erad_listing_aware_s23_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S23_UNIVERSE_CSV, None
            )
        )
        self.assertFalse(
            runner.is_erad_listing_aware_s23_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S22_UNIVERSE_CSV, None
            )
        )
        self.assertFalse(
            runner.is_erad_listing_aware_s22_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S23_UNIVERSE_CSV, None
            )
        )
        self.assertEqual(
            runner.erad_slice2_request_cap_for_mode(listing_aware_s23=True),
            runner.ERAD_LISTING_AWARE_S23_REQUEST_CAP,
        )

    def test_closed_s1_to_s22_roots_forbidden(self) -> None:
        for closed_root in (
            runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S20_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S21_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S22_OUTPUT_ROOT,
        ):
            ok, err = runner.validate_erad_listing_aware_s23_output_root(closed_root)
            self.assertFalse(ok)
            self.assertEqual(err, runner.ERAD_LISTING_AWARE_S23_CLOSED_ROOT_WRITE_FORBIDDEN)

    def test_allowed_root_ok(self) -> None:
        ok, err = runner.validate_erad_listing_aware_s23_output_root(
            runner.DEFAULT_ERAD_LISTING_AWARE_S23_OUTPUT_ROOT
        )
        self.assertTrue(ok)
        self.assertEqual(err, "")
        # 孤立 retry 子根必须落在 S23 根下
        retry_subdir = os.path.join(
            runner.DEFAULT_ERAD_LISTING_AWARE_S23_OUTPUT_ROOT,
            "retry_not_found_probe",
        )
        ok2, err2 = runner.validate_erad_listing_aware_s23_output_root(retry_subdir)
        self.assertTrue(ok2, err2)
        self.assertEqual(err2, "")

    def test_universe_load_and_size(self) -> None:
        if not os.path.isfile(runner.DEFAULT_ERAD_LISTING_AWARE_S23_UNIVERSE_CSV):
            self.skipTest("listing-aware S23 universe CSV not generated yet")
        cases = runner.load_erad_next_scale_slice2_universe(
            runner.DEFAULT_ERAD_LISTING_AWARE_S23_UNIVERSE_CSV
        )
        ok, err = runner.validate_erad_listing_aware_s23_universe_size(cases)
        self.assertTrue(ok, err)
        self.assertEqual(cases[0].cohort, runner.ERAD_LISTING_AWARE_S23_COHORT)
        self.assertEqual(cases[0].case_id, "AD2E1651")
        self.assertEqual(cases[-1].case_id, "AD2E1850")
        self.assertTrue(runner.ERAD_SCALE_200_CASE_ID_PATTERN.match("AD2E1850"))
        issues = runner.lint_erad_listing_aware_s23_overlap(cases)
        self.assertEqual(issues, [])

    def test_case_range_allows_1651_1850_blocks_cross_band(self) -> None:
        start, end = runner.parse_erad_a_slice2_case_range("AD2E1651:AD2E1750")
        self.assertEqual(start, "AD2E1651")
        self.assertEqual(end, "AD2E1750")
        start2, end2 = runner.parse_erad_a_slice2_case_range("AD2E1800:AD2E1850")
        self.assertEqual(start2, "AD2E1800")
        self.assertEqual(end2, "AD2E1850")
        with self.assertRaises(ValueError):
            runner.parse_erad_a_slice2_case_range("AD2E1640:AD2E1700")
        with self.assertRaises(ValueError):
            runner.parse_erad_a_slice2_case_range("AD2E1600:AD2E1700")


if __name__ == "__main__":
    unittest.main()
