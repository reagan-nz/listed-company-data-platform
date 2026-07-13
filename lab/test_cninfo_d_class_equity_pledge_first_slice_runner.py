"""
D-class equity_pledge first-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_d_class_equity_pledge_first_slice_runner.py
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
UNIVERSE_CSV = runner.DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT
DRYRUN_REPORT = runner.EQUITY_PLEDGE_FIRST_SLICE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.EQUITY_PLEDGE_FIRST_SLICE_DRYRUN_SUMMARY_MD
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
REPLACEMENT_OUTPUT_ROOT = runner.DEFAULT_REPLACEMENT_OUTPUT_ROOT
TARGETED_OUTPUT_ROOT = runner.DEFAULT_TARGETED_PROBE_OUTPUT_ROOT
MARGIN_OUTPUT_ROOT = runner.DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT
DISCLOSURE_OUTPUT_ROOT = runner.DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT
BLOCK_TRADE_OUTPUT_ROOT = runner.DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT
RSU_OUTPUT_ROOT = runner.DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
RSU_UNIVERSE_CSV = runner.DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_UNIVERSE_CSV
BLOCK_TRADE_UNIVERSE_CSV = runner.DEFAULT_BLOCK_TRADE_FIRST_SLICE_UNIVERSE_CSV

BASE_ARGS = [
    "--dry-run",
    "--equity-pledge-first-slice",
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


def _ep_row_from_dict(r: dict[str, str]) -> runner.EquityPledgeFirstSliceRow:
    return runner.EquityPledgeFirstSliceRow(
        case_id=r["case_id"],
        company_code=r["company_code"],
        company_name=r["company_name"],
        component=r["component"],
        market=r["market"],
        anchor_tdate=r["anchor_tdate"],
        first_slice_include=r["first_slice_include"],
        expected_behavior=r["expected_behavior"],
        exclude_flags=r.get("exclude_flags", ""),
        notes=r.get("notes", ""),
        dlc005_reference=r.get("dlc005_reference", ""),
    )


class TestEquityPledgeFirstSliceRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--equity-pledge-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EQUITY_PLEDGE_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH,
            result.stderr,
        )

    def test_only_dep001_through_dep005_allowed(self) -> None:
        rows = _read_universe_rows()
        rows[0] = {**rows[0], "case_id": "DEP999"}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_case.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--equity-pledge-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EQUITY_PLEDGE_FIRST_SLICE_FORBIDDEN_CASE_ID,
            result.stderr,
        )

    def test_component_must_be_equity_pledge(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "component": "block_trade"} if r["case_id"] == "DEP002" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--equity-pledge-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EQUITY_PLEDGE_FIRST_SLICE_WRONG_COMPONENT,
            result.stderr,
        )

    def test_688671_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "company_code": "688671"} if r["case_id"] == "DEP003" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_688671.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--equity-pledge-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EQUITY_PLEDGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODE,
            result.stderr,
        )

    def test_301259_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "company_code": "301259"} if r["case_id"] == "DEP004" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_301259.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--equity-pledge-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EQUITY_PLEDGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODE,
            result.stderr,
        )

    def test_output_root_isolation_enforced(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--equity-pledge-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EQUITY_PLEDGE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED,
            result.stderr,
        )

    def test_closed_track_roots_write_blocked(self) -> None:
        for bad_root, token in [
            (V2_OUTPUT_ROOT, runner.EQUITY_PLEDGE_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED),
            (
                REPLACEMENT_OUTPUT_ROOT,
                runner.EQUITY_PLEDGE_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                TARGETED_OUTPUT_ROOT,
                runner.EQUITY_PLEDGE_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                MARGIN_OUTPUT_ROOT,
                runner.EQUITY_PLEDGE_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                DISCLOSURE_OUTPUT_ROOT,
                runner.EQUITY_PLEDGE_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                BLOCK_TRADE_OUTPUT_ROOT,
                runner.EQUITY_PLEDGE_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                RSU_OUTPUT_ROOT,
                runner.EQUITY_PLEDGE_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
        ]:
            with self.subTest(bad_root=bad_root):
                result = _run(
                    [
                        "--dry-run",
                        "--equity-pledge-first-slice",
                        "--universe-csv",
                        UNIVERSE_CSV,
                        "--output-root",
                        bad_root,
                    ]
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_mixed_mode_with_rsu_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--restricted-shares-unlock-first-slice"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EQUITY_PLEDGE_FIRST_SLICE_MIXED_MODE_BLOCKED,
            result.stderr,
        )

    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                [
                    "--live",
                    "--equity-pledge-first-slice",
                    "--universe-csv",
                    UNIVERSE_CSV,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EQUITY_PLEDGE_FIRST_SLICE_APPROVAL_REQUIRED,
            result.stderr,
        )

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(hasattr(runner, "execute_equity_pledge_first_slice_live"))
        self.assertTrue(callable(runner.execute_equity_pledge_first_slice_live))

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                BASE_ARGS + ["--approve-d-class-restricted-shares-unlock-first-slice"]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EQUITY_PLEDGE_FIRST_SLICE_WRONG_APPROVAL_FLAG,
            result.stderr,
        )

    def test_planned_request_count_lte_20(self) -> None:
        load_rows = _read_universe_rows()
        total = sum(
            runner.compute_equity_pledge_first_slice_planned_requests(
                _ep_row_from_dict(r)
            )
            for r in load_rows
        )
        self.assertLessEqual(
            total, runner.EQUITY_PLEDGE_FIRST_SLICE_TOTAL_MAX_REQUESTS
        )
        self.assertEqual(total, 5)

    def test_pdf_ocr_extraction_blocked(self) -> None:
        for flag, token in [
            ("--pdf-download", runner.PDF_DOWNLOAD_BLOCKED),
            ("--ocr", runner.OCR_BLOCKED),
            ("--extraction", runner.EXTRACTION_BLOCKED),
        ]:
            with self.subTest(flag=flag):
                result = _run(BASE_ARGS + [flag])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, token in [
            ("--db-write", runner.DB_WRITE_BLOCKED),
            ("--minio-write", runner.MINIO_WRITE_BLOCKED),
            ("--rag-run", runner.RAG_RUN_BLOCKED),
        ]:
            with self.subTest(flag=flag):
                result = _run(BASE_ARGS + [flag])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, token in [
            ("--mark-verified", runner.VERIFIED_BLOCKED),
            ("--production-ready", runner.PRODUCTION_READY_BLOCKED),
        ]:
            with self.subTest(flag=flag):
                result = _run(BASE_ARGS + [flag])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_rsu_first_slice_mode_smoke_intact(self) -> None:
        if not os.path.isfile(RSU_UNIVERSE_CSV):
            self.skipTest("RSU universe not present")
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                [
                    "--dry-run",
                    "--restricted-shares-unlock-first-slice",
                    "--universe-csv",
                    RSU_UNIVERSE_CSV,
                    "--output-root",
                    RSU_OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_block_trade_first_slice_mode_smoke_intact(self) -> None:
        if not os.path.isfile(BLOCK_TRADE_UNIVERSE_CSV):
            self.skipTest("block_trade universe not present")
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                [
                    "--dry-run",
                    "--block-trade-first-slice",
                    "--universe-csv",
                    BLOCK_TRADE_UNIVERSE_CSV,
                    "--output-root",
                    BLOCK_TRADE_OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_dry_run_report_generated(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            report_rows = list(csv.DictReader(f))
        self.assertEqual(len(report_rows), 5)
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in report_rows))

    def test_dry_run_summary_generated(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CNINFO calls = 0", content)
        self.assertIn("NOT APPROVED", content)


if __name__ == "__main__":
    unittest.main()
