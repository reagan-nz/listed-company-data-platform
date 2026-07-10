"""
D-class known-event replacement runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_d_class_known_event_replacement_runner.py
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
FILLED_UNIVERSE = runner.DEFAULT_REPLACEMENT_UNIVERSE_CSV
REPLACEMENT_OUTPUT_ROOT = runner.DEFAULT_REPLACEMENT_OUTPUT_ROOT
REPLACEMENT_DRYRUN_REPORT = runner.REPLACEMENT_DRYRUN_REPORT_CSV
REPLACEMENT_DRYRUN_SUMMARY = runner.REPLACEMENT_DRYRUN_SUMMARY_MD
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
CALIBRATED_UNIVERSE = runner.CALIBRATED_UNIVERSE_CSV
ORIGINAL_UNIVERSE = runner.DEFAULT_UNIVERSE_CSV

BASE_ARGS = [
    "--dry-run",
    "--known-event-replacement",
    "--universe-csv",
    FILLED_UNIVERSE,
    "--output-root",
    REPLACEMENT_OUTPUT_ROOT,
]


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


def _read_filled_universe_rows() -> list[dict[str, str]]:
    with open(FILLED_UNIVERSE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_universe_csv(path: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


class TestKnownEventReplacementRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_known_event_replacement_requires_universe_csv(self) -> None:
        result = _run(["--dry-run", "--known-event-replacement"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_UNIVERSE_CSV_REQUIRED, result.stderr)

    def test_live_requires_replacement_approval_flag(self) -> None:
        result = _run(
            [
                "--live",
                "--known-event-replacement",
                "--universe-csv",
                FILLED_UNIVERSE,
                "--output-root",
                REPLACEMENT_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-tiny-live-validation"]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_WRONG_APPROVAL_FLAG, result.stderr)

    def test_universe_size_must_equal_7(self) -> None:
        rows = _read_filled_universe_rows()[:6]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-replacement",
                    "--universe-csv",
                    path,
                    "--output-root",
                    REPLACEMENT_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.UNIVERSE_SIZE_MISMATCH, result.stderr)

    def test_dlc003r_must_be_present(self) -> None:
        rows = [r for r in _read_filled_universe_rows() if r["case_id"] != "DLC003R"]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "missing_dlc003r.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-replacement",
                    "--universe-csv",
                    path,
                    "--output-root",
                    REPLACEMENT_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing_case:DLC003R", result.stderr)

    def test_dlc006r_must_be_present(self) -> None:
        rows = [r for r in _read_filled_universe_rows() if r["case_id"] != "DLC006R"]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "missing_dlc006r.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-replacement",
                    "--universe-csv",
                    path,
                    "--output-root",
                    REPLACEMENT_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing_case:DLC006R", result.stderr)

    def test_placeholder_rows_rejected(self) -> None:
        rows = _read_filled_universe_rows()
        rows = [r if r["case_id"] != "DLC003R" else {**r, "case_id": "DLC003R_CANDIDATE_REQUIRED"} for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "placeholder.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-replacement",
                    "--universe-csv",
                    path,
                    "--output-root",
                    REPLACEMENT_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_PLACEHOLDER_ROW_REJECTED, result.stderr)

    def test_original_dlc003_dlc006_rejected(self) -> None:
        rows = _read_filled_universe_rows()
        rows = [r if r["case_id"] != "DLC003R" else {**r, "case_id": "DLC003"} for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "original_case.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-replacement",
                    "--universe-csv",
                    path,
                    "--output-root",
                    REPLACEMENT_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_ORIGINAL_CASE_IN_UNIVERSE, result.stderr)

    def test_dlc003r_company_code_must_equal_688671(self) -> None:
        rows = _read_filled_universe_rows()
        rows = [
            {**r, "company_code": "999999"} if r["case_id"] == "DLC003R" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_code.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-replacement",
                    "--universe-csv",
                    path,
                    "--output-root",
                    REPLACEMENT_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_WRONG_COMPANY_CODE, result.stderr)

    def test_dlc006r_company_code_must_equal_301259(self) -> None:
        rows = _read_filled_universe_rows()
        rows = [
            {**r, "company_code": "999999"} if r["case_id"] == "DLC006R" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_code.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-replacement",
                    "--universe-csv",
                    path,
                    "--output-root",
                    REPLACEMENT_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_WRONG_COMPANY_CODE, result.stderr)

    def test_candidate_validation_status_must_be_human_candidate_validated(self) -> None:
        rows = _read_filled_universe_rows()
        rows = [
            {**r, "candidate_validation_status": "REJECTED"}
            if r["case_id"] == "DLC006R"
            else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_status.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-replacement",
                    "--universe-csv",
                    path,
                    "--output-root",
                    REPLACEMENT_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_INVALID_CANDIDATE_STATUS, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(BASE_ARGS + ["--output-root", tmp])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_OUTPUT_ROOT_REQUIRED, result.stderr)

    def test_original_v1_universe_write_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--output-root", ORIGINAL_UNIVERSE])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_ORIGINAL_UNIVERSE_WRITE_BLOCKED, result.stderr)

    def test_calibrated_universe_write_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--output-root", CALIBRATED_UNIVERSE])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_CALIBRATED_UNIVERSE_WRITE_BLOCKED, result.stderr)

    def test_v1_v2_execution_reports_write_blocked(self) -> None:
        result_v1 = _run(BASE_ARGS + ["--output-root", V1_OUTPUT_ROOT])
        self.assertNotEqual(result_v1.returncode, 0)
        self.assertIn(runner.REPLACEMENT_V1_OUTPUT_ROOT_WRITE_BLOCKED, result_v1.stderr)
        result_v2 = _run(BASE_ARGS + ["--output-root", V2_OUTPUT_ROOT])
        self.assertNotEqual(result_v2.returncode, 0)
        self.assertIn(runner.REPLACEMENT_V2_OUTPUT_ROOT_WRITE_BLOCKED, result_v2.stderr)

    def test_pdf_ocr_extraction_blocked(self) -> None:
        for flag, token in (
            ("--pdf-download", runner.PDF_DOWNLOAD_BLOCKED),
            ("--ocr", runner.OCR_BLOCKED),
            ("--extraction", runner.EXTRACTION_BLOCKED),
        ):
            result = _run(BASE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with open(REPLACEMENT_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            self.assertEqual(row["pdf_download"], "no")
            self.assertEqual(row["ocr"], "no")
            self.assertEqual(row["extraction"], "no")

    def test_db_minio_rag_blocked(self) -> None:
        for flag, token in (
            ("--db-write", runner.DB_WRITE_BLOCKED),
            ("--minio-write", runner.MINIO_WRITE_BLOCKED),
            ("--rag-run", runner.RAG_RUN_BLOCKED),
        ):
            result = _run(BASE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, token in (
            ("--mark-verified", runner.VERIFIED_BLOCKED),
            ("--production-ready", runner.PRODUCTION_READY_BLOCKED),
        ):
            result = _run(BASE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_dry_run_report_generated(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(REPLACEMENT_DRYRUN_REPORT), msg=REPLACEMENT_DRYRUN_REPORT)
        self.assertTrue(os.path.isfile(REPLACEMENT_DRYRUN_SUMMARY), msg=REPLACEMENT_DRYRUN_SUMMARY)
        with open(REPLACEMENT_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 7)
        self.assertEqual(set(rows[0].keys()), set(runner.REPLACEMENT_DRYRUN_REPORT_COLUMNS))
        self.assertEqual(sum(1 for r in rows if r["dryrun_status"] == "planned_ok"), 7)
        probe_rows = [r for r in rows if r["case_id"] in runner.REPLACEMENT_PROBE_CASE_IDS]
        baseline_rows = [r for r in rows if r["case_id"] in runner.REPLACEMENT_BASELINE_CASE_IDS]
        self.assertEqual(len(probe_rows), 2)
        self.assertEqual(len(baseline_rows), 5)
        for row in probe_rows:
            self.assertEqual(row["cninfo_call_planned"], "yes")
        for row in baseline_rows:
            self.assertEqual(row["cninfo_call_planned"], "no")
            self.assertEqual(row["planned_request_count"], "0")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
