#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-class shareholder_data first-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_d_class_shareholder_data_first_slice_runner.py
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
UNIVERSE_CSV = runner.DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT
DRYRUN_REPORT = runner.SHAREHOLDER_DATA_FIRST_SLICE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.SHAREHOLDER_DATA_FIRST_SLICE_DRYRUN_SUMMARY_MD
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
ES_OUTPUT_ROOT = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT
AT_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT

BASE_ARGS = [
    "--dry-run",
    "--shareholder-data-first-slice",
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


class TestShareholderDataFirstSliceRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_request_count_total=1", result.stdout)
        self.assertIn(
            "d_class_shareholder_data_first_slice_runner_extension_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_shareholder_data_first_slice_live_path_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_shareholder_data_first_slice_live_gate=NOT_APPROVED",
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
                    "--shareholder-data-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_data_first_slice_universe_size_must_equal_5",
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
                    "--shareholder-data-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "forbidden_company_code_in_shareholder_data_first_slice_universe",
                result.stderr,
            )

    def test_wrong_anchor_rdate_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[1]["anchor_rdate"] = "20251231"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--shareholder-data-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_data_first_slice_anchor_rdate_mismatch",
                result.stderr,
            )

    def test_component_must_be_shareholder_data(self) -> None:
        rows = _read_universe_rows()
        rows[2]["component"] = "shareholder_change"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--shareholder-data-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_data_first_slice_component_must_be_shareholder_data",
                result.stderr,
            )

    def test_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-data-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "v1_output_root_write_blocked_for_shareholder_data_first_slice",
            result.stderr,
        )

    def test_abnormal_trading_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-data-first-slice",
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

    def test_executive_shareholding_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-data-first-slice",
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

    def test_mixed_mode_with_abnormal_trading_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--abnormal-trading-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_data_first_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_wrong_approval_flag_blocked(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-abnormal-trading-first-slice"]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "wrong_approval_flag_for_shareholder_data_first_slice",
            result.stderr,
        )

    def test_live_without_approval_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--shareholder-data-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_shareholder_data_first_slice_required",
            result.stderr,
        )

    def test_live_with_approval_mock_shared_path_cninfo_zero(self) -> None:
        """离线 mock live：1 次共享截面 + SECCODE 过滤 · 不触网 · CNINFO=0。"""
        rows = runner.load_shareholder_data_first_slice_universe(UNIVERSE_CSV)

        def _fake_cninfo_request(session, source_cfg, params_override, stats, case_id):
            self.assertEqual(
                case_id, runner.SHAREHOLDER_DATA_FIRST_SLICE_SHARED_REQUEST_CASE_ID
            )
            self.assertEqual(params_override, {"rdate": "20260331"})
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = (
                stats.case_request_counts.get(case_id, 0) + 1
            )
            # 稀疏截面：无目标 SECCODE → 全案 empty；DSD001 mismatch → 4/5
            return (
                {
                    "data": {
                        "records": [
                            {
                                "SECCODE": "999999",
                                "SECNAME": "其他公司",
                                "ENDDATE": "2026-03-31",
                                "F001N": 1,
                            }
                        ]
                    }
                },
                200,
                "",
            )

        with tempfile.TemporaryDirectory() as tmp:
            out_root = os.path.join(
                tmp, "cninfo_d_class_shareholder_data_first_slice"
            )
            output_paths = runner.ensure_output_layout(out_root, "live")
            with mock.patch(
                "run_cninfo_d_class_tiny_live_validation._cninfo_request",
                side_effect=_fake_cninfo_request,
            ), mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                rc = runner.execute_shareholder_data_first_slice_live(
                    rows, output_paths
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertEqual(rc, 0)
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_shareholder_data_first_slice_live_report.csv",
            )
            quality_report = os.path.join(
                output_paths["reports"],
                "d_class_shareholder_data_first_slice_quality_report.csv",
            )
            live_summary = os.path.join(
                output_paths["reports"],
                "d_class_shareholder_data_first_slice_live_summary.md",
            )
            self.assertTrue(os.path.isfile(live_report))
            self.assertTrue(os.path.isfile(quality_report))
            self.assertTrue(os.path.isfile(live_summary))
            with open(live_report, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.assertEqual(
                    list(reader.fieldnames or []),
                    runner.SHAREHOLDER_DATA_FIRST_SLICE_LIVE_REPORT_COLUMNS,
                )
                live_rows = {r["case_id"]: r for r in reader}
            self.assertEqual(len(live_rows), 5)
            self.assertEqual(live_rows["DSD001"]["acceptable"], "no")
            self.assertEqual(
                live_rows["DSD001"]["failure_type"], "expectation_mismatch"
            )
            for case_id in ("DSD002", "DSD003", "DSD004", "DSD005"):
                self.assertEqual(live_rows[case_id]["acceptable"], "yes")
                self.assertEqual(
                    live_rows[case_id]["retrieval_status"], "empty_but_valid"
                )
            for case_id, row in live_rows.items():
                self.assertIn("shared_rdate_request=1", row["notes"])
                self.assertIn("seccode_filter=yes", row["notes"])
                snap = os.path.join(
                    output_paths["live_snapshots"],
                    f"{case_id}_shareholder_data.json",
                )
                self.assertTrue(os.path.isfile(snap), snap)
            with open(live_summary, encoding="utf-8") as f:
                content = f.read()
            self.assertIn(
                "d_class_shareholder_data_first_slice_live_path_gate = READY_FOR_APPROVAL",
                content,
            )
            self.assertIn(
                "d_class_shareholder_data_first_slice_live_gate = NOT_APPROVED",
                content,
            )
            self.assertIn(
                "d_class_shareholder_data_first_slice_execution_gate = PASS_WITH_CAVEAT",
                content,
            )
            self.assertIn("shared_cninfo_requests | **1**", content)
            self.assertIn("NOT verified", content)

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(
            hasattr(runner, "execute_shareholder_data_first_slice_live")
        )
        self.assertTrue(
            callable(runner.execute_shareholder_data_first_slice_live)
        )

    def test_empty_but_valid_acceptable_rules(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        rows = runner.load_shareholder_data_first_slice_universe(UNIVERSE_CSV)
        by_id = {r.case_id: r for r in rows}
        self.assertFalse(
            runner.is_shareholder_data_first_slice_acceptable(
                by_id["DSD001"], summary
            )
        )
        for case_id in ("DSD002", "DSD003", "DSD004", "DSD005"):
            self.assertTrue(
                runner.is_shareholder_data_first_slice_acceptable(
                    by_id[case_id], summary
                )
            )

    def test_dsd001_found_acceptable(self) -> None:
        row = next(
            r
            for r in runner.load_shareholder_data_first_slice_universe(UNIVERSE_CSV)
            if r.case_id == "DSD001"
        )
        summary = {
            "retrieval_status": "found",
            "quality_status": "pass",
            "record_count": "1",
        }
        self.assertTrue(
            runner.is_shareholder_data_first_slice_acceptable(row, summary)
        )

    def test_execution_gate_three_of_five(self) -> None:
        rows = runner.load_shareholder_data_first_slice_universe(UNIVERSE_CSV)
        summaries = {
            r.case_id: {
                "retrieval_status": "empty_but_valid",
                "quality_status": "pass",
                "record_count": "0",
            }
            for r in rows
        }
        gate = runner.compute_shareholder_data_first_slice_execution_gate(
            rows, summaries
        )
        self.assertEqual(
            gate, runner.SHAREHOLDER_DATA_FIRST_SLICE_EXECUTION_GATE_PASS
        )
        acceptable = sum(
            1
            for r in rows
            if runner.is_shareholder_data_first_slice_acceptable(
                r, summaries[r.case_id]
            )
        )
        self.assertEqual(acceptable, 4)

    def test_default_universe_csv_rejected(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-data-first-slice",
                "--universe-csv",
                runner.DEFAULT_UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_data_first_slice_requires_explicit_universe_csv",
            result.stderr,
        )

    def test_dryrun_report_five_planned_ok_shared_one(self) -> None:
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
            all(
                r["planned_endpoint"]
                == runner.SHAREHOLDER_DATA_FIRST_SLICE_ENDPOINT
                for r in rows
            )
        )
        self.assertTrue(all(r["cninfo_call_planned"] == "shared" for r in rows))
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            summary = f.read()
        self.assertIn("planned_shared_cninfo_requests | **1**", summary)
        self.assertIn(
            "d_class_shareholder_data_first_slice_runner_extension_gate = READY_FOR_APPROVAL",
            summary,
        )
        self.assertIn(
            "d_class_shareholder_data_first_slice_live_path_gate = READY_FOR_APPROVAL",
            summary,
        )
        self.assertIn(
            "d_class_shareholder_data_first_slice_live_gate = NOT_APPROVED",
            summary,
        )

    def test_plan_helpers(self) -> None:
        plan = runner.build_shareholder_data_first_slice_plan("20260331")
        self.assertEqual(plan, ["rdate_report_period_20260331"])
        self.assertEqual(
            runner.compute_shareholder_data_first_slice_planned_shared(), 1
        )
        rows = runner.load_shareholder_data_first_slice_universe(UNIVERSE_CSV)
        self.assertEqual(len(rows), 5)
        issues = runner.validate_shareholder_data_first_slice_universe(rows)
        self.assertEqual(issues, [])
        for row in rows:
            refs = runner.resolve_shareholder_data_first_slice_fixture_refs(
                row.case_id
            )
            self.assertTrue(refs)
            for ref in refs:
                self.assertTrue(os.path.isfile(ref), ref)
            params = runner._build_shareholder_data_first_slice_params(row)
            self.assertEqual(params, [{"rdate": "20260331"}])


if __name__ == "__main__":
    unittest.main()
