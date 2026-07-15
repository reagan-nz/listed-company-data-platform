#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-class abnormal_trading first-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_d_class_abnormal_trading_first_slice_runner.py
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_tiny_live_validation.py")
UNIVERSE_CSV = runner.DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT
DRYRUN_REPORT = runner.ABNORMAL_TRADING_FIRST_SLICE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.ABNORMAL_TRADING_FIRST_SLICE_DRYRUN_SUMMARY_MD
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
ES_OUTPUT_ROOT = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT

BASE_ARGS = [
    "--dry-run",
    "--abnormal-trading-first-slice",
    "--universe-csv",
    UNIVERSE_CSV,
    "--output-root",
    OUTPUT_ROOT,
]


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


def _read_universe_rows() -> list[dict[str, str]]:
    with open(UNIVERSE_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_universe_csv(path: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


class TestAbnormalTradingFirstSliceRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn(
            "d_class_abnormal_trading_first_slice_runner_extension_gate=READY_FOR_APPROVAL",
            result.stdout,
        )

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--abnormal-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "abnormal_trading_first_slice_universe_size_must_equal_5",
                result.stderr,
            )

    def test_forbidden_company_code_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[0]["company_code"] = "301259"
        rows[0]["company_name"] = "艾布鲁"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_code.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--abnormal-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "forbidden_company_code_in_abnormal_trading_first_slice_universe",
                result.stderr,
            )

    def test_wrong_anchor_tdate_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[1]["anchor_tdate"] = "2026-07-04"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--abnormal-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "abnormal_trading_first_slice_anchor_tdate_mismatch",
                result.stderr,
            )

    def test_component_must_be_abnormal_trading(self) -> None:
        rows = _read_universe_rows()
        rows[2]["component"] = "block_trade"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--abnormal-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "abnormal_trading_first_slice_component_must_be_abnormal_trading",
                result.stderr,
            )

    def test_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--abnormal-trading-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "v1_output_root_write_blocked_for_abnormal_trading_first_slice",
            result.stderr,
        )

    def test_executive_shareholding_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--abnormal-trading-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                ES_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "executive_shareholding_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_mixed_mode_with_executive_shareholding_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--executive-shareholding-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "abnormal_trading_first_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_wrong_approval_flag_blocked(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-executive-shareholding-first-slice"]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "wrong_approval_flag_for_abnormal_trading_first_slice",
            result.stderr,
        )

    def test_live_without_approval_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--abnormal-trading-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_abnormal_trading_first_slice_required",
            result.stderr,
        )

    def test_live_with_approval_still_not_implemented(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(
                [
                    "--live",
                    "--abnormal-trading-first-slice",
                    "--approve-d-class-abnormal-trading-first-slice",
                    "--universe-csv",
                    UNIVERSE_CSV,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "abnormal_trading_first_slice_live_not_implemented",
            result.stderr,
        )

    def test_default_universe_csv_rejected(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--abnormal-trading-first-slice",
                "--universe-csv",
                runner.DEFAULT_UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "abnormal_trading_first_slice_requires_explicit_universe_csv",
            result.stderr,
        )

    def test_dryrun_report_five_planned_ok(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
        self.assertEqual(
            sum(int(r["planned_request_count"]) for r in rows),
            5,
        )
        self.assertTrue(
            all(r["planned_endpoint"] == runner.ABNORMAL_TRADING_FIRST_SLICE_ENDPOINT for r in rows)
        )

    def test_plan_helpers(self) -> None:
        plan = runner.build_abnormal_trading_first_slice_plan("2026-07-03")
        self.assertEqual(plan, ["single_day_paged_2026-07-03"])
        rows = runner.load_abnormal_trading_first_slice_universe(UNIVERSE_CSV)
        self.assertEqual(len(rows), 5)
        issues = runner.validate_abnormal_trading_first_slice_universe(rows)
        self.assertEqual(issues, [])
        for row in rows:
            refs = runner.resolve_abnormal_trading_first_slice_fixture_refs(row.case_id)
            self.assertTrue(refs)
            for ref in refs:
                self.assertTrue(os.path.isfile(ref), ref)


if __name__ == "__main__":
    unittest.main()
