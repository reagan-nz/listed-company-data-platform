#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 fund_industry_allocation next-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_fund_industry_allocation_next_slice_runner.py
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
UNIVERSE_CSV = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_NEXT_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_NEXT_SLICE_OUTPUT_ROOT
FIRST_SLICE_OUTPUT_ROOT = (
    runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT
)
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
SD_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT
AT_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT
ES_OUTPUT_ROOT = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT

BASE_ARGS = [
    "--dry-run",
    "--fund-industry-allocation-next-slice",
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


class TestFundIndustryAllocationNextSliceRunner(unittest.TestCase):
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
            "d_class_fund_industry_allocation_next_slice_runner_extension_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_fund_industry_allocation_next_slice_live_path_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_fund_industry_allocation_next_slice_live_gate=NOT_APPROVED",
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
                    "--fund-industry-allocation-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_next_slice_universe_size_must_equal_5",
                result.stderr,
            )

    def test_wrong_industry_code_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[0]["industry_code"] = "C26"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_industry.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--fund-industry-allocation-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_next_slice_industry_code_mismatch",
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
                    "--fund-industry-allocation-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_next_slice_anchor_rdate_mismatch",
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
                    "--fund-industry-allocation-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_next_slice_component_must_be_fund_industry_allocation",
                result.stderr,
            )

    def test_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--fund-industry-allocation-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "v1_output_root_write_blocked_for_fund_industry_allocation_next_slice",
            result.stderr,
        )

    def test_first_slice_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--fund-industry-allocation-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                FIRST_SLICE_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "fund_industry_allocation_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_shareholder_data_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--fund-industry-allocation-next-slice",
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
                "--fund-industry-allocation-next-slice",
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
                "--fund-industry-allocation-next-slice",
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

    def test_mixed_mode_with_first_slice_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--fund-industry-allocation-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "fund_industry_allocation_next_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_mixed_mode_with_shareholder_data_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--shareholder-data-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "fund_industry_allocation_next_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_wrong_approval_flag_blocked(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-fund-industry-allocation-first-slice"]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "wrong_approval_flag_for_fund_industry_allocation_next_slice",
            result.stderr,
        )

    def test_live_without_approval_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--fund-industry-allocation-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_fund_industry_allocation_next_slice_required",
            result.stderr,
        )

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(
            hasattr(runner, "execute_fund_industry_allocation_next_slice_live")
        )
        self.assertTrue(
            callable(runner.execute_fund_industry_allocation_next_slice_live)
        )

    def test_shared_plan_equals_three(self) -> None:
        self.assertEqual(
            runner.compute_fund_industry_allocation_next_slice_planned_shared(),
            3,
        )
        self.assertEqual(
            runner.build_fund_industry_allocation_next_slice_plan(),
            ["default", "rdate_20260331", "rdate_20251231"],
        )

    def test_coarse_filter_prefix_and_exact(self) -> None:
        records = [
            {"F001V": "A", "F002V": "农"},
            {"F001V": "C26", "F002V": "化"},
            {"F001V": "B", "F002V": "采"},
            {"F001V": "C", "F002V": "制"},
        ]
        self.assertEqual(
            len(runner._filter_industry_records_coarse(records, "A")), 1
        )
        self.assertEqual(
            len(runner._filter_industry_records_coarse(records, "C")), 2
        )
        self.assertEqual(
            len(runner._filter_industry_records_coarse(records, "*")), 4
        )

    def test_empty_but_valid_acceptable_rules(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        rows = runner.load_fund_industry_allocation_next_slice_universe(UNIVERSE_CSV)
        by_id = {r.case_id: r for r in rows}
        self.assertTrue(
            runner.is_fund_industry_allocation_next_slice_acceptable(
                by_id["DFIA101"], summary
            )
        )
        self.assertTrue(
            runner.is_fund_industry_allocation_next_slice_acceptable(
                by_id["DFIA102"], summary
            )
        )
        self.assertFalse(
            runner.is_fund_industry_allocation_next_slice_acceptable(
                by_id["DFIA103"], summary
            )
        )
        self.assertFalse(
            runner.is_fund_industry_allocation_next_slice_acceptable(
                by_id["DFIA104"], summary
            )
        )
        self.assertTrue(
            runner.is_fund_industry_allocation_next_slice_acceptable(
                by_id["DFIA105"], summary
            )
        )

    def test_live_with_approval_mock_shared_path_cninfo_zero(self) -> None:
        """离线 mock live：3 次共享探针 + 粗粒度 F001V 过滤 · 不触网 · CNINFO=0。"""
        rows = runner.load_fund_industry_allocation_next_slice_universe(UNIVERSE_CSV)
        call_ids: list[str] = []

        def _fake_cninfo_request(session, source_cfg, params_override, stats, case_id):
            call_ids.append(case_id)
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
                                    "F001V": "A",
                                    "F002V": "农、林、牧、渔业",
                                    "ENDDATE": "2026-06-30",
                                    "F003N": 3,
                                    "F004N": 0.34,
                                    "F005N": 0.03,
                                },
                                {
                                    "F001V": "C",
                                    "F002V": "制造业",
                                    "ENDDATE": "2026-06-30",
                                    "F003N": 10,
                                    "F004N": 1.2,
                                    "F005N": 3.4,
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
                                    "F001V": "B",
                                    "F002V": "采矿业",
                                    "ENDDATE": "2026-03-31",
                                    "F003N": 2,
                                    "F004N": 0.3,
                                    "F005N": 0.4,
                                },
                                {
                                    "F001V": "C26",
                                    "F002V": "化学原料",
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
            if case_id == "rdate_20251231":
                self.assertEqual(params_override, {"rdate": "20251231"})
                return ({"data": {"records": []}}, 200, "")
            self.fail(f"unexpected probe {case_id}")

        with tempfile.TemporaryDirectory() as tmp:
            out_root = os.path.join(
                tmp, "cninfo_d_class_fund_industry_allocation_next_slice"
            )
            output_paths = runner.ensure_output_layout(out_root, "live")
            with mock.patch(
                "run_cninfo_d_class_tiny_live_validation._cninfo_request",
                side_effect=_fake_cninfo_request,
            ), mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                rc = runner.execute_fund_industry_allocation_next_slice_live(
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
                "d_class_fund_industry_allocation_next_slice_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = {r["case_id"]: r for r in csv.DictReader(f)}
            self.assertEqual(len(live_rows), 5)
            self.assertEqual(live_rows["DFIA101"]["acceptable"], "yes")
            self.assertEqual(live_rows["DFIA101"]["retrieval_status"], "found")
            self.assertEqual(live_rows["DFIA102"]["acceptable"], "yes")
            self.assertEqual(live_rows["DFIA103"]["acceptable"], "yes")
            self.assertEqual(live_rows["DFIA104"]["acceptable"], "yes")
            self.assertEqual(live_rows["DFIA105"]["acceptable"], "yes")
            self.assertEqual(
                live_rows["DFIA105"]["retrieval_status"], "empty_but_valid"
            )


class TestFundIndustryAllocationNextSliceDfm27Closure(unittest.TestCase):
    """D-FM-27 next-slice offline closure：统一 live 5/5 + 产物 schema（无 CNINFO）。"""

    VALIDATION = os.path.join(BASE_DIR, "outputs", "validation")
    CLOSURE_METRICS = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_next_slice_closure_metrics.csv",
    )
    CAVEAT_LEDGER = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_next_slice_final_caveat_ledger.csv",
    )
    EFFECTIVE_RESULT = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_next_slice_effective_result.csv",
    )
    CLOSURE_MATRIX = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_dfm27_next_slice_closure_matrix_20260715.csv",
    )
    LIVE_REPORT = os.path.join(
        OUTPUT_ROOT,
        "reports",
        "d_class_fund_industry_allocation_next_slice_live_report.csv",
    )
    NEXT_SLICE_LOCK = UNIVERSE_CSV
    FIRST_SLICE_LOCK = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv",
    )
    # D-FM-24/26 冻结的 next-slice / first-slice lock sha256；closure 不得改动
    NEXT_SLICE_LOCK_SHA256 = (
        "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
    )
    FIRST_SLICE_LOCK_SHA256 = (
        "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
    )

    @staticmethod
    def _sha256_file(path: str) -> str:
        import hashlib

        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    def test_unified_live_five_of_five_offline(self) -> None:
        rows = runner.load_fund_industry_allocation_next_slice_universe(UNIVERSE_CSV)
        if not os.path.isfile(self.LIVE_REPORT):
            self.skipTest("live report not present")
        with open(self.LIVE_REPORT, newline="", encoding="utf-8") as f:
            live = {r["case_id"]: r for r in csv.DictReader(f)}
        acceptable = sum(
            1
            for r in rows
            if runner.is_fund_industry_allocation_next_slice_acceptable(
                r, live[r.case_id]
            )
        )
        self.assertEqual(acceptable, 5)
        gate = runner.compute_fund_industry_allocation_next_slice_execution_gate(
            rows, live
        )
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_closure_artifacts_present_and_caveats(self) -> None:
        for path in (
            self.CLOSURE_METRICS,
            self.CAVEAT_LEDGER,
            self.EFFECTIVE_RESULT,
            self.CLOSURE_MATRIX,
        ):
            self.assertTrue(os.path.isfile(path), msg=path)
        with open(self.CAVEAT_LEDGER, newline="", encoding="utf-8") as f:
            caveats = {c["caveat_id"]: c for c in csv.DictReader(f)}
        self.assertIn("CAV-FIA-NS-002", caveats)
        self.assertEqual(
            caveats["CAV-FIA-NS-002"]["caveat_type"],
            "unified_live_pass_with_caveat",
        )
        self.assertIn("bare PASS", caveats["CAV-FIA-NS-002"]["forbidden_interpretation"])
        self.assertEqual(
            caveats["CAV-FIA-NS-003"]["caveat_type"], "coarse_f001v_filter"
        )
        with open(self.CLOSURE_METRICS, newline="", encoding="utf-8") as f:
            metrics = {r["metric_name"]: r["value"] for r in csv.DictReader(f)}
        self.assertEqual(metrics["acceptable_unified_live"], "5")
        self.assertEqual(metrics["CNINFO_during_closure"], "0")
        self.assertEqual(metrics["closure_gate"], "PASS_WITH_CAVEAT")
        self.assertEqual(metrics["CNINFO_during_dfm26_live"], "3")
        with open(self.EFFECTIVE_RESULT, newline="", encoding="utf-8") as f:
            eff = {r["case_id"]: r for r in csv.DictReader(f)}
        self.assertEqual(len(eff), 5)
        for case_id in ("DFIA101", "DFIA102", "DFIA103", "DFIA104", "DFIA105"):
            self.assertEqual(eff[case_id]["acceptable"], "yes")
            self.assertEqual(eff[case_id]["source_of_final_result"], "dfm26_unified_live")
        self.assertEqual(eff["DFIA103"]["record_count"], "19")
        self.assertEqual(eff["DFIA101"]["record_count"], "1")

    def test_live_report_not_overwritten_and_locks_frozen(self) -> None:
        if not os.path.isfile(self.LIVE_REPORT):
            self.skipTest("live report not present")
        with open(self.LIVE_REPORT, newline="", encoding="utf-8") as f:
            live = {r["case_id"]: r for r in csv.DictReader(f)}
        # D-FM-26 统一 5/5 只读保留；closure 不得改写为其他叙事
        for case_id in ("DFIA101", "DFIA102", "DFIA103", "DFIA104", "DFIA105"):
            self.assertEqual(live[case_id]["acceptable"], "yes")
        self.assertEqual(live["DFIA103"]["record_count"], "19")
        self.assertEqual(live["DFIA105"]["retrieval_status"], "found")
        self.assertEqual(
            self._sha256_file(self.NEXT_SLICE_LOCK), self.NEXT_SLICE_LOCK_SHA256
        )
        self.assertEqual(
            self._sha256_file(self.FIRST_SLICE_LOCK), self.FIRST_SLICE_LOCK_SHA256
        )


if __name__ == "__main__":
    unittest.main()
