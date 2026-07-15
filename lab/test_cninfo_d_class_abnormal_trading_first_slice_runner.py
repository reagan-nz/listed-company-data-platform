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

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(
            hasattr(runner, "execute_abnormal_trading_first_slice_live")
        )
        self.assertTrue(
            callable(runner.execute_abnormal_trading_first_slice_live)
        )

    def test_live_with_approval_mock_writes_reports_cninfo_zero(self) -> None:
        """离线 mock live：不触网 · 写 live/quality/summary · CNINFO=0。"""
        rows = runner.load_abnormal_trading_first_slice_universe(UNIVERSE_CSV)

        def _fake_execute_live_case(
            case,
            source_cfg,
            endpoint,
            session,
            stats,
            output_paths,
            param_list=None,
        ):
            # 模拟 per-case 计数但不发 HTTP
            stats.cninfo_requests += 1
            stats.case_request_counts[case.case_id] = (
                stats.case_request_counts.get(case.case_id, 0) + 1
            )
            if case.case_id == "DAT001":
                return {
                    "case_id": case.case_id,
                    "company_code": case.company_code,
                    "company_name": case.company_name,
                    "component": case.component,
                    "expected_behavior": case.expected_behavior,
                    "retrieval_status": "empty_but_valid",
                    "quality_status": "pass",
                    "lineage_status": "discovered",
                    "record_count": "0",
                    "empty_but_valid": "yes",
                    "needs_review": "no",
                    "endpoint_used": endpoint,
                    "cninfo_request_count": "1",
                    "db_write": "no",
                    "minio_write": "no",
                    "rag_run": "no",
                    "notes": "mock sparse empty for DAT001",
                }
            if case.case_id == "DAT005":
                return {
                    "case_id": case.case_id,
                    "company_code": case.company_code,
                    "company_name": case.company_name,
                    "component": case.component,
                    "expected_behavior": case.expected_behavior,
                    "retrieval_status": "empty_but_valid",
                    "quality_status": "pass",
                    "lineage_status": "discovered",
                    "record_count": "0",
                    "empty_but_valid": "yes",
                    "needs_review": "no",
                    "endpoint_used": endpoint,
                    "cninfo_request_count": "1",
                    "db_write": "no",
                    "minio_write": "no",
                    "rag_run": "no",
                    "notes": "mock empty_but_valid control",
                }
            return {
                "case_id": case.case_id,
                "company_code": case.company_code,
                "company_name": case.company_name,
                "component": case.component,
                "expected_behavior": case.expected_behavior,
                "retrieval_status": "empty_but_valid",
                "quality_status": "pass",
                "lineage_status": "discovered",
                "record_count": "0",
                "empty_but_valid": "yes",
                "needs_review": "no",
                "endpoint_used": endpoint,
                "cninfo_request_count": "1",
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
                "notes": "mock empty_but_valid sparse day",
            }

        with tempfile.TemporaryDirectory() as tmp:
            out_root = os.path.join(tmp, "cninfo_d_class_abnormal_trading_first_slice")
            output_paths = runner.ensure_output_layout(out_root, "live")
            with mock.patch(
                "run_cninfo_d_class_tiny_live_validation.execute_live_case",
                side_effect=_fake_execute_live_case,
            ), mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                rc = runner.execute_abnormal_trading_first_slice_live(
                    rows, output_paths
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            # DAT001 empty 对 needs_review 期望不可接受；DAT002–005 empty 可接受 → 4/5
            self.assertEqual(rc, 0)
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_abnormal_trading_first_slice_live_report.csv",
            )
            quality_report = os.path.join(
                output_paths["reports"],
                "d_class_abnormal_trading_first_slice_quality_report.csv",
            )
            live_summary = os.path.join(
                output_paths["reports"],
                "d_class_abnormal_trading_first_slice_live_summary.md",
            )
            self.assertTrue(os.path.isfile(live_report))
            self.assertTrue(os.path.isfile(quality_report))
            self.assertTrue(os.path.isfile(live_summary))
            with open(live_report, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.assertEqual(
                    list(reader.fieldnames or []),
                    runner.ABNORMAL_TRADING_FIRST_SLICE_LIVE_REPORT_COLUMNS,
                )
                live_rows = {r["case_id"]: r for r in reader}
            self.assertEqual(len(live_rows), 5)
            self.assertEqual(live_rows["DAT001"]["acceptable"], "no")
            self.assertEqual(
                live_rows["DAT001"]["failure_type"], "expectation_mismatch"
            )
            for case_id in ("DAT002", "DAT003", "DAT004", "DAT005"):
                self.assertEqual(live_rows[case_id]["acceptable"], "yes")
            with open(live_summary, encoding="utf-8") as f:
                content = f.read()
            self.assertIn(
                "d_class_abnormal_trading_first_slice_live_path_gate = READY_FOR_APPROVAL",
                content,
            )
            self.assertIn(
                "d_class_abnormal_trading_first_slice_execution_gate = PASS_WITH_CAVEAT",
                content,
            )
            self.assertIn("NOT verified", content)

    def test_empty_but_valid_acceptable_rules(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        rows = runner.load_abnormal_trading_first_slice_universe(UNIVERSE_CSV)
        by_id = {r.case_id: r for r in rows}
        self.assertFalse(
            runner.is_abnormal_trading_first_slice_acceptable(
                by_id["DAT001"], summary
            )
        )
        for case_id in ("DAT002", "DAT003", "DAT004", "DAT005"):
            self.assertTrue(
                runner.is_abnormal_trading_first_slice_acceptable(
                    by_id[case_id], summary
                )
            )

    def test_dat001_found_or_needs_review_acceptable(self) -> None:
        row = next(
            r
            for r in runner.load_abnormal_trading_first_slice_universe(UNIVERSE_CSV)
            if r.case_id == "DAT001"
        )
        for rs, qs in (("found", "pass"), ("needs_review", "needs_review")):
            with self.subTest(retrieval_status=rs):
                summary = {
                    "retrieval_status": rs,
                    "quality_status": qs,
                    "record_count": "1",
                }
                self.assertTrue(
                    runner.is_abnormal_trading_first_slice_acceptable(row, summary)
                )

    def test_execution_gate_three_of_five(self) -> None:
        rows = runner.load_abnormal_trading_first_slice_universe(UNIVERSE_CSV)
        summaries = {
            r.case_id: {
                "retrieval_status": "empty_but_valid",
                "quality_status": "pass",
                "record_count": "0",
            }
            for r in rows
        }
        gate = runner.compute_abnormal_trading_first_slice_execution_gate(
            rows, summaries
        )
        self.assertEqual(
            gate, runner.ABNORMAL_TRADING_FIRST_SLICE_EXECUTION_GATE_PASS
        )
        acceptable = sum(
            1
            for r in rows
            if runner.is_abnormal_trading_first_slice_acceptable(
                r, summaries[r.case_id]
            )
        )
        self.assertEqual(acceptable, 4)

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
