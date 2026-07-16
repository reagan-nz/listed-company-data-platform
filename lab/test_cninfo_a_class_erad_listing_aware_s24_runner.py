"""
A-class listing-aware S24 residual runner 路径隔离测试（mock · CNINFO = 0）。

运行：
    python lab/test_cninfo_a_class_erad_listing_aware_s24_runner.py
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402


class ListingAwareS24RunnerTests(unittest.TestCase):
    def test_mode_detection_and_cap(self) -> None:
        self.assertTrue(
            runner.is_erad_listing_aware_s24_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S24_UNIVERSE_CSV, None
            )
        )
        self.assertFalse(
            runner.is_erad_listing_aware_s24_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S23_UNIVERSE_CSV, None
            )
        )
        self.assertFalse(
            runner.is_erad_listing_aware_s23_mode(
                runner.DEFAULT_ERAD_LISTING_AWARE_S24_UNIVERSE_CSV, None
            )
        )
        self.assertEqual(
            runner.erad_slice2_request_cap_for_mode(listing_aware_s24=True),
            runner.ERAD_LISTING_AWARE_S24_REQUEST_CAP,
        )
        self.assertEqual(runner.REQUIRED_ERAD_LISTING_AWARE_S24_UNIVERSE_SIZE, 371)
        self.assertEqual(runner.ERAD_LISTING_AWARE_S24_REQUEST_CAP, 960)

    def test_closed_s1_to_s23_roots_forbidden(self) -> None:
        for closed_root in (
            runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S22_OUTPUT_ROOT,
            runner.DEFAULT_ERAD_LISTING_AWARE_S23_OUTPUT_ROOT,
        ):
            ok, err = runner.validate_erad_listing_aware_s24_output_root(closed_root)
            self.assertFalse(ok)
            self.assertEqual(err, runner.ERAD_LISTING_AWARE_S24_CLOSED_ROOT_WRITE_FORBIDDEN)

    def test_allowed_root_ok(self) -> None:
        ok, err = runner.validate_erad_listing_aware_s24_output_root(
            runner.DEFAULT_ERAD_LISTING_AWARE_S24_OUTPUT_ROOT
        )
        self.assertTrue(ok)
        self.assertEqual(err, "")
        retry_subdir = os.path.join(
            runner.DEFAULT_ERAD_LISTING_AWARE_S24_OUTPUT_ROOT,
            "retry_not_found_probe",
        )
        ok2, err2 = runner.validate_erad_listing_aware_s24_output_root(retry_subdir)
        self.assertTrue(ok2, err2)
        self.assertEqual(err2, "")

    def test_universe_load_and_size(self) -> None:
        if not os.path.isfile(runner.DEFAULT_ERAD_LISTING_AWARE_S24_UNIVERSE_CSV):
            self.skipTest("listing-aware S24 residual universe CSV not generated yet")
        cases = runner.load_erad_next_scale_slice2_universe(
            runner.DEFAULT_ERAD_LISTING_AWARE_S24_UNIVERSE_CSV
        )
        ok, err = runner.validate_erad_listing_aware_s24_universe_size(cases)
        self.assertTrue(ok, err)
        self.assertEqual(cases[0].cohort, runner.ERAD_LISTING_AWARE_S24_COHORT)
        self.assertEqual(cases[0].case_id, "AD2E1851")
        self.assertEqual(cases[-1].case_id, "AD2E2221")
        self.assertTrue(runner.ERAD_SCALE_200_CASE_ID_PATTERN.match("AD2E2221"))
        issues = runner.lint_erad_listing_aware_s24_overlap(cases)
        self.assertEqual(issues, [])

    def test_case_range_allows_1851_2221_blocks_cross_band(self) -> None:
        start, end = runner.parse_erad_a_slice2_case_range("AD2E1851:AD2E2000")
        self.assertEqual(start, "AD2E1851")
        self.assertEqual(end, "AD2E2000")
        start2, end2 = runner.parse_erad_a_slice2_case_range("AD2E2100:AD2E2221")
        self.assertEqual(start2, "AD2E2100")
        self.assertEqual(end2, "AD2E2221")
        with self.assertRaises(ValueError):
            runner.parse_erad_a_slice2_case_range("AD2E1800:AD2E1900")
        with self.assertRaises(ValueError):
            runner.parse_erad_a_slice2_case_range("AD2E1850:AD2E1900")


if __name__ == "__main__":
    unittest.main()
