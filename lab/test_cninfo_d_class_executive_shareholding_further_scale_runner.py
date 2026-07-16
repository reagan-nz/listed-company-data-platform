#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 executive_shareholding further-scale（~50）runner 测试（无真实 CNINFO · mock live 允许）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_executive_shareholding_further_scale_runner.py
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

import run_cninfo_d_class_executive_shareholding_further_scale as fs  # noqa: E402
import run_cninfo_d_class_tiny_live_validation as core  # noqa: E402

BASE_DIR = fs.BASE_DIR
RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_d_class_executive_shareholding_further_scale.py"
)
UNIVERSE_CSV = fs.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = fs.DEFAULT_OUTPUT_ROOT
VALIDATION = fs.VALIDATION

ESH_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_next_slice_universe_lock_20260716.csv",
)
ESH_NEXT_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_next_slice",
    "reports",
    "d_class_executive_shareholding_next_slice_live_report.csv",
)
ESH_FIRST_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv",
)
ESH_FIRST_DRY = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_first_slice",
    "reports",
    "d_class_executive_shareholding_first_slice_dryrun_report.csv",
)
SC_DRY = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_next_slice",
    "reports",
    "d_class_shareholder_change_next_slice_dryrun_report.csv",
)
EP_DRY = os.path.join(
    VALIDATION,
    "cninfo_d_class_equity_pledge_next_slice",
    "reports",
    "d_class_equity_pledge_next_slice_dryrun_report.csv",
)
RSU_DRY = os.path.join(
    VALIDATION,
    "cninfo_d_class_restricted_shares_unlock_next_slice",
    "reports",
    "d_class_restricted_shares_unlock_next_slice_dryrun_report.csv",
)

ESH_NEXT_LOCK_SHA256 = (
    "4213de37e19d1d6bd920a9b2efd24495338a27eeb17f2602a8159fbb4b6d2fd1"
)
ESH_NEXT_LIVE_SHA256 = (
    "dc16b591b117a9411c0ec458a1ff3cdb4d850417fcf87d5de851c5c73af23e25"
)
ESH_FIRST_LOCK_SHA256 = (
    "d42aaaf71f427fefe96f03700ff33e333686965355149ff2ad63311f7ac283c8"
)
ESH_FIRST_DRY_SHA256 = (
    "cd8f25c24aebc75bc18ec5bb887eb4c0664ec7a579fcbc6d10c221f40a3b6092"
)
SC_DRY_SHA256 = (
    "5abc61e4f7ea6014af7e50847aefc7e46f4e39e3ba10e394fd56e683b19a08a5"
)
EP_DRY_SHA256 = (
    "054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e"
)
RSU_DRY_SHA256 = (
    "87f296cf51fd69873f8fd6fd05a541ebbfa35dab53b92063bdf841736b52b18c"
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


class TestExecutiveShareholdingFurtherScaleRunner(unittest.TestCase):
    def test_universe_lock_size_and_mix(self) -> None:
        self.assertTrue(os.path.isfile(UNIVERSE_CSV))
        with open(UNIVERSE_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 50)
        self.assertEqual(rows[0]["case_id"], "DES201")
        self.assertEqual(rows[-1]["case_id"], "DES250")
        found_like = [r for r in rows if r["expected_behavior"] == "captured_normal"]
        empty_like = [r for r in rows if r["expected_behavior"] == "empty_but_valid"]
        self.assertEqual(len(found_like), 48)
        self.assertEqual(len(empty_like), 2)
        self.assertEqual(empty_like[0]["company_code"], "000895")
        self.assertEqual(empty_like[1]["company_code"], "601988")
        # 不得复用 next-slice / first-slice found 锚码
        found_codes = {r["company_code"] for r in found_like}
        for code in ("002415", "000895", "600000", "000550", "601988"):
            self.assertNotIn(code, found_codes)
        for row in rows:
            self.assertEqual(row["time_mark"], "threeMonth")
            self.assertEqual(row["vary_type"], "b")
            self.assertNotEqual(row["time_mark"], "oneMonth")
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
                "executive_shareholding_further_scale_output_root_must_be_",
                result.stderr,
            )

        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            dry_report = os.path.join(
                OUTPUT_ROOT,
                "reports",
                "d_class_executive_shareholding_further_scale_dryrun_report.csv",
            )
            dry_summary = os.path.join(
                OUTPUT_ROOT,
                "reports",
                "d_class_executive_shareholding_further_scale_dryrun_summary.md",
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
            self.assertIn("threeMonth", content)
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
            "approve_d_class_executive_shareholding_further_scale_required",
            result.stderr,
        )

    def test_wrong_output_root_blocked(self) -> None:
        blocked = os.path.join(
            VALIDATION, "cninfo_d_class_executive_shareholding_next_slice"
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
            "executive_shareholding_further_scale_output_root_must_be_" in result.stderr
            or "frozen_root_write_blocked" in result.stderr
        )

    def test_mock_live_shared_one_request_excellence(self) -> None:
        rows = fs.load_universe(UNIVERSE_CSV)
        records = []
        for row in rows:
            if row["expected_behavior"] == "captured_normal":
                records.append(
                    {
                        "SECCODE": row["company_code"],
                        "SECNAME": row["company_name"],
                        "HUMANNAME": "mock",
                    }
                )
        payload = {"data": {"records": records, "total": len(records)}}

        with tempfile.TemporaryDirectory() as tmp:
            output_paths = {
                "root": tmp,
                "reports": os.path.join(tmp, "reports"),
                "live_snapshots": os.path.join(tmp, "live_snapshots"),
            }
            os.makedirs(output_paths["reports"], exist_ok=True)
            os.makedirs(output_paths["live_snapshots"], exist_ok=True)

            def fake_request(session, cfg, params, stats, case_id):
                stats.cninfo_requests += 1
                stats.case_request_counts[case_id] = (
                    stats.case_request_counts.get(case_id, 0) + 1
                )
                return payload, 200, ""

            with mock.patch.object(core, "_cninfo_request", side_effect=fake_request):
                rc = fs.execute_live(rows, output_paths)
            self.assertEqual(rc, 0)
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_executive_shareholding_further_scale_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = list(csv.DictReader(f))
            self.assertEqual(len(live_rows), 50)
            self.assertTrue(all(r["acceptable"] == "yes" for r in live_rows))
            found = [r for r in live_rows if r["retrieval_status"] == "found"]
            empty = [r for r in live_rows if r["retrieval_status"] == "empty_but_valid"]
            self.assertEqual(len(found), 48)
            self.assertEqual(len(empty), 2)
            excel = fs.excellence_metrics(live_rows)
            self.assertTrue(excel["excellent"])
            self.assertEqual(excel["failed_or_http_error"], 0)
            self.assertGreaterEqual(excel["acceptable_rate"], 0.95)

    def test_frozen_roots_unchanged(self) -> None:
        self.assertEqual(_sha256_file(ESH_NEXT_LOCK), ESH_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(ESH_NEXT_LIVE), ESH_NEXT_LIVE_SHA256)
        self.assertEqual(_sha256_file(ESH_FIRST_LOCK), ESH_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(ESH_FIRST_DRY), ESH_FIRST_DRY_SHA256)
        self.assertEqual(_sha256_file(SC_DRY), SC_DRY_SHA256)
        self.assertEqual(_sha256_file(EP_DRY), EP_DRY_SHA256)
        self.assertEqual(_sha256_file(RSU_DRY), RSU_DRY_SHA256)

    def test_live_report_excellence_when_present(self) -> None:
        live_report = os.path.join(
            OUTPUT_ROOT,
            "reports",
            "d_class_executive_shareholding_further_scale_live_report.csv",
        )
        if not os.path.isfile(live_report):
            self.skipTest("live report not yet generated")
        with open(live_report, newline="", encoding="utf-8") as f:
            live_rows = list(csv.DictReader(f))
        self.assertEqual(len(live_rows), 50)
        excel = fs.excellence_metrics(live_rows)
        self.assertEqual(excel["acceptable"], sum(1 for r in live_rows if r["acceptable"] == "yes"))


if __name__ == "__main__":
    unittest.main()
