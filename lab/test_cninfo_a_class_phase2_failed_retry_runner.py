"""
A-class Phase 2 failed retry runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_a_class_phase2_failed_retry_runner.py
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

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_metadata_expansion.py")
RETRY_UNIVERSE = runner.DEFAULT_RETRY_UNIVERSE_CSV
RETRY_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
RETRY_DRYRUN_REPORT = os.path.join(
    RETRY_OUTPUT_ROOT, "reports", "a_class_phase2_failed_retry_dryrun_report.csv"
)
RETRY_DRYRUN_SUMMARY = os.path.join(
    RETRY_OUTPUT_ROOT, "reports", "a_class_phase2_failed_retry_dryrun_summary.md"
)


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestAClassPhase2FailedRetryRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(["--retry-failed-only", "--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_retry_live_requires_approve_a_class_phase2_failed_retry(self) -> None:
        result = _run(["--retry-failed-only", "--live"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected(self) -> None:
        wrong_flags = (
            "--approve-a-class-phase2-metadata-expansion",
            "--approve-a-class-tiny-live-metadata",
            "--approve-phase1-tiny-live-metadata",
            "--approve-full-harvest",
            "--approve-b-class-tiny-live-validation",
        )
        for flag in wrong_flags:
            result = _run(["--retry-failed-only", "--live", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_retry_universe_size_must_equal_8(self) -> None:
        result = _run(["--retry-failed-only", "--dry-run", "--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_only_failed_a2m_cases_allowed(self) -> None:
        case = runner.RetryUniverseCase(
            case_id="A2M001",
            company_code="600036",
            company_name="招商银行",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            original_failure_type="network_error",
            original_failure_reason="test",
            retry_include="yes",
            retry_strategy="isolated_orgId_retry_then_announcement_query",
            notes="",
        )
        issues = runner.validate_retry_case(case)
        self.assertIn(runner.SUCCESSFUL_CASE_IN_RETRY_FORBIDDEN, issues)

    def test_successful_a2m_cases_rejected(self) -> None:
        for case_id in ("A2M001", "A2M014", "A2M017"):
            case = runner.RetryUniverseCase(
                case_id=case_id,
                company_code="600036",
                company_name="测试",
                market="SSE",
                report_type="annual_report",
                expected_period="2024-12-31",
                original_failure_type="found",
                original_failure_reason="should not retry",
                retry_include="yes",
                retry_strategy="none",
                notes="",
            )
            issues = runner.validate_retry_case(case)
            self.assertIn(runner.SUCCESSFUL_CASE_IN_RETRY_FORBIDDEN, issues, msg=case_id)

    def test_retry_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(["--retry-failed-only", "--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.RETRY_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_pdf_download_blocked(self) -> None:
        result = _run(["--retry-failed-only", "--dry-run", "--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(["--retry-failed-only", "--dry-run", "--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--enable-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--enable-extraction", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(["--retry-failed-only", "--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, err in (
            ("--write-db", runner.DB_WRITE_REQUESTED_NOT_ALLOWED),
            ("--write-minio", runner.MINIO_WRITE_REQUESTED_NOT_ALLOWED),
            ("--run-rag", runner.RAG_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(["--retry-failed-only", "--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_dry_run_retry_report_generated(self) -> None:
        result = _run(["--retry-failed-only", "--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(RETRY_DRYRUN_REPORT))
        self.assertTrue(os.path.isfile(RETRY_DRYRUN_SUMMARY))
        with open(RETRY_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), runner.RETRY_REQUIRED_UNIVERSE_SIZE)
        self.assertEqual(set(rows[0].keys()), set(runner.RETRY_DRYRUN_COLUMNS))
        case_ids = {row["case_id"] for row in rows}
        self.assertEqual(case_ids, runner.RETRY_ALLOWED_CASE_IDS)
        for row in rows:
            self.assertEqual(row["pdf_download"], "0")
            self.assertEqual(row["cninfo_call_planned"], "0")
            self.assertEqual(row["dryrun_status"], "planned_ok")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
