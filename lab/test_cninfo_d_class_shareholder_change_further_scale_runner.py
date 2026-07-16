#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 shareholder_change further-scale（~50）runner 测试（无真实 CNINFO · mock live 允许）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_shareholder_change_further_scale_runner.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_d_class_shareholder_change_further_scale as fs  # noqa: E402

BASE_DIR = fs.BASE_DIR
RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_d_class_shareholder_change_further_scale.py"
)
UNIVERSE_CSV = fs.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = fs.DEFAULT_OUTPUT_ROOT
VALIDATION = fs.VALIDATION

SC_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_next_slice_universe_lock_20260716.csv",
)
SC_NEXT_DRY = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_next_slice",
    "reports",
    "d_class_shareholder_change_next_slice_dryrun_report.csv",
)
SC_FIRST_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv",
)
ESH_S50_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_further_scale",
    "reports",
    "d_class_executive_shareholding_further_scale_live_report.csv",
)
ESH_S200_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_further_scale_s200",
    "reports",
    "d_class_executive_shareholding_further_scale_s200_live_report.csv",
)
ESH_S1000_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_further_scale_s1000",
    "reports",
    "d_class_executive_shareholding_further_scale_s1000_live_report.csv",
)
AT_S50_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_further_scale",
    "reports",
    "d_class_abnormal_trading_further_scale_live_report.csv",
)

SC_NEXT_LOCK_SHA256 = (
    "5452bc546def60754182a0e5b38fb165d709a37e0a267113088732237b5508fb"
)
SC_NEXT_DRY_SHA256 = (
    "5abc61e4f7ea6014af7e50847aefc7e46f4e39e3ba10e394fd56e683b19a08a5"
)
SC_FIRST_LOCK_SHA256 = (
    "49e6ece0c0a5c5ecce32328e4e1fe990b48d7d46d3cc1f32da1c8d2245a3c402"
)
ESH_S50_LIVE_SHA256 = (
    "1d32b6f324948417b2726e0dd5bd637db1ce01e30e0fe29ae983cd3c4ab73d06"
)
ESH_S200_LIVE_SHA256 = (
    "2f8c038e5729fabbfef6e34fadc5c40eb5ce5a8ba3d7540d23f88af0209203dc"
)
ESH_S1000_LIVE_SHA256 = (
    "3285526e7c96d0b5656198cc4fbcf0c1e6f4bca270d12533f2d73d851101c443"
)
AT_S50_LIVE_SHA256 = (
    "88d77c2b60bb28535a2d073009a0f734056ad995a0deb1b1f99d27300225253c"
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


class TestShareholderChangeFurtherScaleRunner(unittest.TestCase):
    def test_universe_lock_size_and_mix(self) -> None:
        self.assertTrue(os.path.isfile(UNIVERSE_CSV))
        with open(UNIVERSE_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 50)
        self.assertEqual(rows[0]["case_id"], "DSC201")
        self.assertEqual(rows[-1]["case_id"], "DSC250")
        found_like = [r for r in rows if r["expected_behavior"] == "captured_normal"]
        empty_like = [r for r in rows if r["expected_behavior"] == "empty_but_valid"]
        self.assertEqual(len(found_like), 48)
        self.assertEqual(len(empty_like), 2)
        found_codes = {r["company_code"] for r in found_like}
        for code in ("002415", "000895", "600000", "000550", "601988"):
            self.assertNotIn(code, found_codes)
        for row in rows:
            self.assertEqual(row["query_type"], "desc")
            self.assertNotEqual(row["query_type"], "inc")
            self.assertNotEqual(row["anchor_tdate"], "2026-07-03")
            self.assertIn(row["anchor_tdate"], ("2026-07-01", "2026-07-14"))
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
                "shareholder_change_further_scale_output_root_must_be_",
                result.stderr,
            )

        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            dry_report = os.path.join(
                OUTPUT_ROOT,
                "reports",
                "d_class_shareholder_change_further_scale_dryrun_report.csv",
            )
            dry_summary = os.path.join(
                OUTPUT_ROOT,
                "reports",
                "d_class_shareholder_change_further_scale_dryrun_summary.md",
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
            self.assertIn("type_desc_multi_day_union", content)
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
            "approve_d_class_shareholder_change_further_scale_required",
            result.stderr,
        )

    def test_wrong_output_root_blocked(self) -> None:
        blocked = os.path.join(
            VALIDATION, "cninfo_d_class_shareholder_change_next_slice"
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
            "shareholder_change_further_scale_output_root_must_be_" in result.stderr
            or "frozen_root_write_blocked" in result.stderr
        )

    def test_frozen_roots_untouched(self) -> None:
        pairs = [
            (SC_NEXT_LOCK, SC_NEXT_LOCK_SHA256),
            (SC_NEXT_DRY, SC_NEXT_DRY_SHA256),
            (SC_FIRST_LOCK, SC_FIRST_LOCK_SHA256),
            (ESH_S50_LIVE, ESH_S50_LIVE_SHA256),
            (ESH_S200_LIVE, ESH_S200_LIVE_SHA256),
            (ESH_S1000_LIVE, ESH_S1000_LIVE_SHA256),
            (AT_S50_LIVE, AT_S50_LIVE_SHA256),
        ]
        for path, expected in pairs:
            self.assertTrue(os.path.isfile(path), path)
            self.assertEqual(_sha256_file(path), expected, path)

    def test_excellence_helpers(self) -> None:
        rows = [
            {"acceptable": "yes", "retrieval_status": "found", "failure_type": ""},
            {"acceptable": "yes", "retrieval_status": "empty_but_valid", "failure_type": ""},
        ]
        # pad to 50 yes
        rows = rows + [
            {"acceptable": "yes", "retrieval_status": "found", "failure_type": ""}
            for _ in range(48)
        ]
        excel = fs.excellence_metrics(rows)
        self.assertTrue(excel["excellent"])
        self.assertEqual(excel["acceptable"], 50)
        bad = list(rows)
        bad[0] = {
            "acceptable": "no",
            "retrieval_status": "empty_but_valid",
            "failure_type": "expectation_mismatch",
        }
        excel2 = fs.excellence_metrics(bad)
        self.assertFalse(excel2["excellent"])


if __name__ == "__main__":
    unittest.main()
