#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 fund_industry_allocation first-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_fund_industry_allocation_first_slice_runner.py
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
UNIVERSE_CSV = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
SD_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT
AT_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT

BASE_ARGS = [
    "--dry-run",
    "--fund-industry-allocation-first-slice",
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


class TestFundIndustryAllocationFirstSliceRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_request_count_total=3", result.stdout)
        self.assertIn(
            "d_class_fund_industry_allocation_first_slice_runner_extension_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_fund_industry_allocation_first_slice_live_path_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_fund_industry_allocation_first_slice_live_gate=NOT_APPROVED",
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
                    "--fund-industry-allocation-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_first_slice_universe_size_must_equal_5",
                result.stderr,
            )

    def test_wrong_industry_code_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[0]["industry_code"] = "Z99"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_industry.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--fund-industry-allocation-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_first_slice_industry_code_mismatch",
                result.stderr,
            )

    def test_wrong_anchor_rdate_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[2]["anchor_rdate"] = "20240101"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--fund-industry-allocation-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_first_slice_anchor_rdate_mismatch",
                result.stderr,
            )

    def test_component_must_be_fund_industry_allocation(self) -> None:
        rows = _read_universe_rows()
        rows[1]["component"] = "shareholder_data"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--fund-industry-allocation-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_first_slice_component_must_be_fund_industry_allocation",
                result.stderr,
            )

    def test_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--fund-industry-allocation-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "v1_output_root_write_blocked_for_fund_industry_allocation_first_slice",
            result.stderr,
        )

    def test_shareholder_data_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--fund-industry-allocation-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                SD_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_data_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_abnormal_trading_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--fund-industry-allocation-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                AT_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "abnormal_trading_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_mixed_mode_with_shareholder_data_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--shareholder-data-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "fund_industry_allocation_first_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_wrong_approval_flag_blocked(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-shareholder-data-first-slice"]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "wrong_approval_flag_for_fund_industry_allocation_first_slice",
            result.stderr,
        )

    def test_live_without_approval_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--fund-industry-allocation-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_fund_industry_allocation_first_slice_required",
            result.stderr,
        )

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(
            hasattr(runner, "execute_fund_industry_allocation_first_slice_live")
        )
        self.assertTrue(
            callable(runner.execute_fund_industry_allocation_first_slice_live)
        )

    def test_shared_plan_equals_three(self) -> None:
        self.assertEqual(
            runner.compute_fund_industry_allocation_first_slice_planned_shared(),
            3,
        )
        self.assertEqual(
            runner.build_fund_industry_allocation_first_slice_plan(),
            ["default", "rdate_20260331", "rdate_20251231"],
        )

    def test_empty_but_valid_acceptable_rules(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        rows = runner.load_fund_industry_allocation_first_slice_universe(UNIVERSE_CSV)
        by_id = {r.case_id: r for r in rows}
        # D-FM-17：DFIA001 期望放宽后 empty_but_valid 可接受（对齐 DFIA004）
        self.assertTrue(
            runner.is_fund_industry_allocation_first_slice_acceptable(
                by_id["DFIA001"], summary
            )
        )
        self.assertFalse(
            runner.is_fund_industry_allocation_first_slice_acceptable(
                by_id["DFIA002"], summary
            )
        )
        self.assertFalse(
            runner.is_fund_industry_allocation_first_slice_acceptable(
                by_id["DFIA003"], summary
            )
        )
        self.assertTrue(
            runner.is_fund_industry_allocation_first_slice_acceptable(
                by_id["DFIA004"], summary
            )
        )
        self.assertTrue(
            runner.is_fund_industry_allocation_first_slice_acceptable(
                by_id["DFIA005"], summary
            )
        )

    def test_live_with_approval_mock_shared_path_cninfo_zero(self) -> None:
        """离线 mock live：3 次共享探针 + F001V 过滤 · 不触网 · CNINFO=0。"""
        rows = runner.load_fund_industry_allocation_first_slice_universe(UNIVERSE_CSV)
        call_ids: list[str] = []

        def _fake_cninfo_request(session, source_cfg, params_override, stats, case_id):
            call_ids.append(case_id)
            # registry 默认 params_location=none 会丢弃 rdate；live path 必须强制 form
            self.assertEqual(
                str(source_cfg.get("params_location") or "").lower(),
                "form",
            )
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = (
                stats.case_request_counts.get(case_id, 0) + 1
            )
            if case_id == "default":
                self.assertEqual(params_override, {})
                return (
                    {
                        "data": {
                            "records": [
                                {
                                    "F001V": "C26",
                                    "F002V": "化学原料和化学制品制造业",
                                    "ENDDATE": "2026-03-31",
                                    "F003N": 10,
                                    "F004N": 1.2,
                                    "F005N": 3.4,
                                },
                                {
                                    "F001V": "C27",
                                    "F002V": "其他",
                                    "ENDDATE": "2026-03-31",
                                    "F003N": 1,
                                    "F004N": 0.1,
                                    "F005N": 0.2,
                                },
                            ]
                        }
                    },
                    200,
                    "",
                )
            if case_id == "rdate_20260331":
                self.assertEqual(params_override, {"rdate": "20260331"})
                return (
                    {
                        "data": {
                            "records": [
                                {
                                    "F001V": "C27",
                                    "F002V": "其他",
                                    "ENDDATE": "2026-03-31",
                                    "F003N": 2,
                                    "F004N": 0.3,
                                    "F005N": 0.4,
                                }
                            ]
                        }
                    },
                    200,
                    "",
                )
            if case_id == "rdate_20251231":
                self.assertEqual(params_override, {"rdate": "20251231"})
                return ({"data": {"records": []}}, 200, "")
            self.fail(f"unexpected probe {case_id}")

        with tempfile.TemporaryDirectory() as tmp:
            out_root = os.path.join(
                tmp, "cninfo_d_class_fund_industry_allocation_first_slice"
            )
            output_paths = runner.ensure_output_layout(out_root, "live")
            with mock.patch(
                "run_cninfo_d_class_tiny_live_validation._cninfo_request",
                side_effect=_fake_cninfo_request,
            ), mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                rc = runner.execute_fund_industry_allocation_first_slice_live(
                    rows, output_paths
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertEqual(rc, 0)
            self.assertEqual(
                call_ids, ["default", "rdate_20260331", "rdate_20251231"]
            )
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_fund_industry_allocation_first_slice_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = {r["case_id"]: r for r in csv.DictReader(f)}
            self.assertEqual(len(live_rows), 5)
            # DFIA001: C26 found on default
            self.assertEqual(live_rows["DFIA001"]["acceptable"], "yes")
            self.assertEqual(live_rows["DFIA001"]["retrieval_status"], "found")
            # DFIA002: cross-section non-empty
            self.assertEqual(live_rows["DFIA002"]["acceptable"], "yes")
            # DFIA003: cross-section on rdate found
            self.assertEqual(live_rows["DFIA003"]["acceptable"], "yes")
            # DFIA004: C26 filtered empty on rdate — empty_but_valid ok
            self.assertEqual(live_rows["DFIA004"]["acceptable"], "yes")
            self.assertEqual(
                live_rows["DFIA004"]["retrieval_status"], "empty_but_valid"
            )
            # DFIA005: empty control
            self.assertEqual(live_rows["DFIA005"]["acceptable"], "yes")
            self.assertEqual(
                live_rows["DFIA005"]["retrieval_status"], "empty_but_valid"
            )


if __name__ == "__main__":
    unittest.main()
