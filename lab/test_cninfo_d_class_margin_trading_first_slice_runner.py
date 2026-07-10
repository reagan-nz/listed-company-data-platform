"""
D-class margin_trading first-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_d_class_margin_trading_first_slice_runner.py
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

import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_tiny_live_validation.py")
UNIVERSE_CSV = runner.DEFAULT_MARGIN_TRADING_FIRST_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT
DRYRUN_REPORT = runner.MARGIN_TRADING_FIRST_SLICE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.MARGIN_TRADING_FIRST_SLICE_DRYRUN_SUMMARY_MD
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
REPLACEMENT_OUTPUT_ROOT = runner.DEFAULT_REPLACEMENT_OUTPUT_ROOT
TARGETED_OUTPUT_ROOT = runner.DEFAULT_TARGETED_PROBE_OUTPUT_ROOT

BASE_ARGS = [
    "--dry-run",
    "--margin-trading-first-slice",
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


class TestMarginTradingFirstSliceRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_margin_trading_first_slice_requires_universe_csv(self) -> None:
        result = _run(["--dry-run", "--margin-trading-first-slice"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_UNIVERSE_CSV_REQUIRED, result.stderr)

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--margin-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH, result.stderr)

    def test_only_dmt001_through_dmt005_allowed(self) -> None:
        rows = _read_universe_rows()
        rows[0] = {**rows[0], "case_id": "DMT999"}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_case.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--margin-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_CASE_ID, result.stderr)

    def test_first_slice_include_must_be_yes(self) -> None:
        rows = _read_universe_rows()
        rows = [{**r, "first_slice_include": "no"} if r["case_id"] == "DMT001" else r for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_include.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--margin-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_INCLUDE_REQUIRED, result.stderr)

    def test_component_must_be_margin_trading(self) -> None:
        rows = _read_universe_rows()
        rows = [{**r, "component": "block_trade"} if r["case_id"] == "DMT002" else r for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--margin-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_WRONG_COMPONENT, result.stderr)

    def test_688671_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [{**r, "company_code": "688671"} if r["case_id"] == "DMT003" else r for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_688671.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--margin-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE, result.stderr)

    def test_301259_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [{**r, "company_code": "301259"} if r["case_id"] == "DMT004" else r for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_301259.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--margin-trading-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--margin-trading-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED, result.stderr)

    def test_known_event_and_tiny_live_roots_write_blocked(self) -> None:
        for bad_root, token in [
            (V2_OUTPUT_ROOT, runner.MARGIN_TRADING_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED),
            (
                REPLACEMENT_OUTPUT_ROOT,
                runner.MARGIN_TRADING_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                TARGETED_OUTPUT_ROOT,
                runner.MARGIN_TRADING_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
        ]:
            with self.subTest(bad_root=bad_root):
                result = _run(
                    [
                        "--dry-run",
                        "--margin-trading-first-slice",
                        "--universe-csv",
                        UNIVERSE_CSV,
                        "--output-root",
                        bad_root,
                    ]
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_live_requires_margin_trading_first_slice_approval_flag(self) -> None:
        result = _run(
            [
                "--live",
                "--margin-trading-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                BASE_ARGS + ["--approve-d-class-known-event-targeted-probe"]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_WRONG_APPROVAL_FLAG, result.stderr)

    def test_pdf_download_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--pdf-download"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_BLOCKED, result.stderr)

    def test_pdf_parser_blocked_via_extraction(self) -> None:
        result = _run(BASE_ARGS + ["--extraction"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.EXTRACTION_BLOCKED, result.stderr)

    def test_ocr_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--ocr"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.OCR_BLOCKED, result.stderr)

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

    def test_planned_request_count_lte_20(self) -> None:
        rows = load_rows = _read_universe_rows()
        total = sum(
            runner.compute_margin_trading_first_slice_planned_requests(
                runner.MarginTradingFirstSliceRow(
                    case_id=r["case_id"],
                    company_code=r["company_code"],
                    company_name=r["company_name"],
                    component=r["component"],
                    market=r["market"],
                    anchor_tdate=r["anchor_tdate"],
                    first_slice_include=r["first_slice_include"],
                    expected_behavior=r["expected_behavior"],
                    reason=r.get("reason", ""),
                    dlc001_reference=r.get("dlc001_reference", ""),
                )
            )
            for r in load_rows
        )
        self.assertLessEqual(total, runner.MARGIN_TRADING_FIRST_SLICE_TOTAL_MAX_REQUESTS)

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

    def test_input_universe_csv_not_mutated(self) -> None:
        before = hashlib.sha256(open(UNIVERSE_CSV, "rb").read()).hexdigest()
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        after = hashlib.sha256(open(UNIVERSE_CSV, "rb").read()).hexdigest()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
