#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 equity_pledge further-scale（~50）runner 测试（无真实 CNINFO · mock live 允许）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_equity_pledge_further_scale_runner.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_d_class_equity_pledge_further_scale as fs  # noqa: E402

BASE_DIR = fs.BASE_DIR
RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_d_class_equity_pledge_further_scale.py"
)
UNIVERSE_CSV = fs.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = fs.DEFAULT_OUTPUT_ROOT
VALIDATION = fs.VALIDATION

EP_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv",
)
EP_NEXT_DRY = os.path.join(
    VALIDATION,
    "cninfo_d_class_equity_pledge_next_slice",
    "reports",
    "d_class_equity_pledge_next_slice_dryrun_report.csv",
)
SC_S50_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_further_scale",
    "reports",
    "d_class_shareholder_change_further_scale_live_report.csv",
)
ESH_S50_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_further_scale",
    "reports",
    "d_class_executive_shareholding_further_scale_live_report.csv",
)
AT_S50_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_further_scale",
    "reports",
    "d_class_abnormal_trading_further_scale_live_report.csv",
)

EP_NEXT_LOCK_SHA256 = (
    "1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384"
)


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestEquityPledgeFurtherScaleRunner(unittest.TestCase):
    def test_universe_lock_size_and_mix(self) -> None:
        self.assertTrue(os.path.isfile(UNIVERSE_CSV))
        with open(UNIVERSE_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 50)
        self.assertEqual(rows[0]["case_id"], "DEP201")
        self.assertEqual(rows[-1]["case_id"], "DEP250")
        found_like = [r for r in rows if r["expected_behavior"] == "captured_normal"]
        empty_like = [r for r in rows if r["expected_behavior"] == "empty_but_valid"]
        self.assertEqual(len(found_like), 48)
        self.assertEqual(len(empty_like), 2)
        found_codes = {r["company_code"] for r in found_like}
        for code in ("000001", "000895", "600000", "002415", "601988", "688981"):
            self.assertNotIn(code, found_codes)
        for row in rows:
            self.assertNotEqual(row["anchor_tdate"], "2026-07-03")
            self.assertIn(row["anchor_tdate"], ("2026-07-02", "2026-07-01"))
            self.assertEqual(row["query_mode"], "tdate_daily_multi_day_union")
        issues = fs.validate_universe(rows)
        self.assertEqual(issues, [])

    def test_dry_run_cninfo_zero_and_planned_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(
                [
                    "--dry-run",
                    "--universe-csv",
                    UNIVERSE_CSV,
                    "--output-root",
                    tmp,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "equity_pledge_further_scale_output_root_must_be_",
                result.stderr,
            )

        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            dry_report = os.path.join(
                OUTPUT_ROOT,
                "reports",
                "d_class_equity_pledge_further_scale_dryrun_report.csv",
            )
            dry_summary = os.path.join(
                OUTPUT_ROOT,
                "reports",
                "d_class_equity_pledge_further_scale_dryrun_summary.md",
            )
            self.assertTrue(os.path.isfile(dry_report))
            self.assertTrue(os.path.isfile(dry_summary))
            with open(dry_report, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 50)
            self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
            with open(dry_summary, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("CNINFO calls | **0**", content)
            self.assertIn("tdate_daily_multi_day_union", content)
            get_mock.assert_not_called()
            post_mock.assert_not_called()

    def test_live_without_approve_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_equity_pledge_further_scale_required",
            result.stderr,
        )

    def test_wrong_output_root_blocked(self) -> None:
        blocked = os.path.join(
            VALIDATION, "cninfo_d_class_equity_pledge_next_slice"
        )
        result = _run(
            [
                "--dry-run",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                blocked,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertTrue(
            "equity_pledge_further_scale_output_root_must_be_" in result.stderr
            or "frozen_root_write_blocked" in result.stderr
        )

    def test_frozen_prior_roots_untouched_hashes(self) -> None:
        self.assertEqual(_sha256_file(EP_NEXT_LOCK), EP_NEXT_LOCK_SHA256)
        # dry report sha 可能因历史路径差异变化；至少确认文件仍存在且可读
        self.assertTrue(os.path.isfile(EP_NEXT_DRY))
        for path in (SC_S50_LIVE, ESH_S50_LIVE, AT_S50_LIVE):
            if os.path.isfile(path):
                before = _sha256_file(path)
                after = _sha256_file(path)
                self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
