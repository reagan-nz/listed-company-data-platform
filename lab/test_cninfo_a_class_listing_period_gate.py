"""A-class listing_period_gate 离线门禁单测（CNINFO = 0）。"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_LAB = Path(__file__).resolve().parent
if str(_LAB) not in sys.path:
    sys.path.insert(0, str(_LAB))

import cninfo_a_class_listing_period_gate as gate  # noqa: E402


class ListingPeriodGateTests(unittest.TestCase):
    def test_normalize_code(self) -> None:
        self.assertEqual(gate.normalize_code("688605"), "688605")
        self.assertEqual(gate.normalize_code("8605"), "008605")

    def test_parse_iso_date(self) -> None:
        self.assertEqual(str(gate.parse_iso_date("2024-06-30")), "2024-06-30")
        self.assertIsNone(gate.parse_iso_date(None))
        self.assertIsNone(gate.parse_iso_date("null"))

    def test_listing_gap_when_listed_after_period(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = {
                "company_code": "688605",
                "listing_date": "2024-12-12",
                "raw_record_json": {"basicInformation": [{"F006D": "2024-12-12"}]},
            }
            path = Path(tmp) / "688605.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            result = gate.assess_listing_vs_expected_period(
                "688605", "2024-06-30", profile_dir=tmp
            )
            self.assertEqual(result.failure_class, gate.FAILURE_LISTING_GAP)
            self.assertEqual(result.root_cause, gate.ROOT_PERIOD_BEFORE_LISTING)
            self.assertFalse(result.retry_recommended)
            self.assertTrue(result.blocks_periodic_retrieval)
            self.assertEqual(result.cninfo_calls, 0)

    def test_unlisted_when_listing_date_null(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = {
                "company_code": "688688",
                "listing_date": None,
                "raw_record_json": {"basicInformation": [{"F006D": None}]},
            }
            (Path(tmp) / "688688.json").write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            result = gate.assess_listing_vs_expected_period(
                "688688", "2024-09-30", profile_dir=tmp
            )
            self.assertEqual(result.failure_class, gate.FAILURE_UNLISTED)
            self.assertTrue(result.blocks_periodic_retrieval)
            self.assertFalse(result.retry_recommended)

    def test_ok_when_listed_before_period(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = {"company_code": "600000", "listing_date": "1999-11-10"}
            (Path(tmp) / "600000.json").write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
            result = gate.assess_listing_vs_expected_period(
                "600000", "2024-06-30", profile_dir=tmp
            )
            self.assertEqual(result.failure_class, gate.FAILURE_OK)
            self.assertFalse(result.blocks_periodic_retrieval)

    def test_profile_missing_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = gate.assess_listing_vs_expected_period(
                "999999", "2024-06-30", profile_dir=tmp
            )
            self.assertEqual(result.failure_class, gate.FAILURE_PROFILE_MISSING)
            self.assertFalse(result.found_profile)

    def test_live_c_class_profiles_for_ad2e_triad(self) -> None:
        """对照仓库内真实 C-class profile（若存在）验证三案门禁。"""
        if not os.path.isdir(gate.DEFAULT_PROFILE_DIR):
            self.skipTest("C-class basic_profile 目录不存在")
        cases = [
            ("688605", "2024-06-30", gate.FAILURE_LISTING_GAP),
            ("688688", "2024-09-30", gate.FAILURE_UNLISTED),
            ("688758", "2024-06-30", gate.FAILURE_LISTING_GAP),
        ]
        for code, period, expected_fc in cases:
            path = os.path.join(gate.DEFAULT_PROFILE_DIR, f"{code}.json")
            if not os.path.isfile(path):
                self.skipTest(f"missing profile {code}")
            result = gate.assess_listing_vs_expected_period(code, period)
            self.assertEqual(result.failure_class, expected_fc, msg=code)
            self.assertEqual(result.cninfo_calls, 0)
            self.assertTrue(result.blocks_periodic_retrieval)


if __name__ == "__main__":
    unittest.main()
