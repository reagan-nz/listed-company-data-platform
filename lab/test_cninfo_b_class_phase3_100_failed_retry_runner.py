"""
B-class Phase 3 100 failed-case isolated retry runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_b_class_phase3_100_failed_retry_runner.py
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

import run_cninfo_b_class_phase25_expansion_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_b_class_phase25_expansion_validation.py")
UNIVERSE = runner.DEFAULT_PHASE3_RETRY_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_OUTPUT_ROOT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
PHASE25_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
PHASE25_RETRY_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
DRYRUN_REPORT = runner.PHASE3_RETRY_DRYRUN_REPORT_CSV

RETRY_HEADER = (
    "case_id,company_code,company_name,market,announcement_type,target_endpoint,"
    "original_phase3_status,original_failure_type,original_failure_stage,"
    "retry_include,retry_strategy,notes\n"
)

RETRY_BASE_ARGS = [
    "--phase3-100-failed-retry",
    "--universe-csv",
    UNIVERSE,
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


class TestPhase3FailedRetryRunner(unittest.TestCase):
    def test_dry_run_phase3_retry_no_network(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(RETRY_BASE_ARGS + ["--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_phase3_retry_requires_universe_csv(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(RETRY_HEADER)
            f.write(
                "B3E001,600010,测试,SSE主板,periodic_report,EP001;EP004,"
                "network_error,ep002_orgid_resolution_failed,EP002_topSearch_orgId,"
                "yes,isolated_metadata_retry,test\n"
            )
            bad_path = f.name
        try:
            result = _run(
                [
                    "--phase3-100-failed-retry",
                    "--dry-run",
                    "--universe-csv",
                    bad_path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.PHASE3_RETRY_UNIVERSE_CSV_REQUIRED, result.stderr)
        finally:
            os.unlink(bad_path)

    def test_phase3_retry_live_without_approval_blocked(self) -> None:
        result = _run(RETRY_BASE_ARGS + ["--live"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_RETRY_APPROVAL_REQUIRED, result.stderr)

    def test_phase3_retry_live_with_wrong_approval_flags_blocked(self) -> None:
        wrong_flags = (
            "--approve-b-class-phase25-expansion",
            "--approve-b-class-phase25-failed-retry",
            "--approve-b-class-phase3-100-expansion",
            "--approve-b-class-phase2-expansion",
            "--approve-b-class-tiny-live-validation",
            "--approve-b-class-tlc002-retry",
            "--approve-full-harvest",
            "--approve-phase3-batch-500-harvest",
        )
        for flag in wrong_flags:
            result = _run(RETRY_BASE_ARGS + ["--live", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_retry_universe_size_must_equal_99(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(RETRY_HEADER)
            f.write(
                "B3E001,600010,测试,SSE主板,periodic_report,EP001;EP004,"
                "network_error,ep002_orgid_resolution_failed,EP002_topSearch_orgId,"
                "yes,isolated_metadata_retry,test\n"
            )
            bad_path = f.name
        try:
            cases = runner.load_phase3_retry_universe(bad_path)
            ok, err = runner.validate_phase3_retry_universe_size(cases)
            self.assertFalse(ok)
            self.assertIn(runner.PHASE3_RETRY_UNIVERSE_SIZE_VIOLATION, err)
        finally:
            os.unlink(bad_path)

    def test_b3e087_rejected(self) -> None:
        case = runner.Phase3RetryUniverseCase(
            case_id=runner.PHASE3_SUCCESS_HOLD_CASE_ID,
            company_code="000786",
            company_name="北新建材",
            market="SZSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            original_phase3_status="found",
            original_failure_type="",
            original_failure_stage="",
            retry_include="yes",
            retry_strategy="isolated_metadata_retry",
            notes="",
        )
        issues = runner.validate_phase3_retry_case(case)
        self.assertIn(runner.SUCCESSFUL_PHASE3_CASE_RETRY_REJECTED, issues)

    def test_prior_phase_case_ids_rejected(self) -> None:
        for case_id in ("B25E001", "B2E001", "B1E001"):
            case = runner.Phase3RetryUniverseCase(
                case_id=case_id,
                company_code="600099",
                company_name="测试",
                market="SSE主板",
                announcement_type="periodic_report",
                target_endpoint=["EP001", "EP004"],
                original_phase3_status="network_error",
                original_failure_type="ep002_orgid_resolution_failed",
                original_failure_stage="EP002_topSearch_orgId",
                retry_include="yes",
                retry_strategy="isolated_metadata_retry",
                notes="",
            )
            issues = runner.validate_phase3_retry_case(case)
            self.assertIn(runner.PRIOR_PHASE_CASE_ID_REJECTED, issues, msg=case_id)

    def test_retry_include_must_be_yes(self) -> None:
        case = runner.Phase3RetryUniverseCase(
            case_id="B3E001",
            company_code="600010",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            original_phase3_status="network_error",
            original_failure_type="ep002_orgid_resolution_failed",
            original_failure_stage="EP002_topSearch_orgId",
            retry_include="no",
            retry_strategy="isolated_metadata_retry",
            notes="",
        )
        issues = runner.validate_phase3_retry_case(case)
        self.assertIn(runner.RETRY_INCLUDE_REQUIRED, issues)

    def test_duplicate_company_code_rejected(self) -> None:
        cases = [
            runner.Phase3RetryUniverseCase(
                case_id="B3E001",
                company_code="600099",
                company_name="测试A",
                market="SSE主板",
                announcement_type="periodic_report",
                target_endpoint=["EP001", "EP004"],
                original_phase3_status="network_error",
                original_failure_type="ep002_orgid_resolution_failed",
                original_failure_stage="EP002_topSearch_orgId",
                retry_include="yes",
                retry_strategy="isolated_metadata_retry",
                notes="",
            ),
            runner.Phase3RetryUniverseCase(
                case_id="B3E002",
                company_code="600099",
                company_name="测试B",
                market="SSE主板",
                announcement_type="periodic_report",
                target_endpoint=["EP001", "EP004"],
                original_phase3_status="network_error",
                original_failure_type="ep002_orgid_resolution_failed",
                original_failure_stage="EP002_topSearch_orgId",
                retry_include="yes",
                retry_strategy="isolated_metadata_retry",
                notes="",
            ),
        ]
        issues = runner.validate_phase3_retry_duplicate_codes(cases)
        self.assertTrue(any(runner.DUPLICATE_COMPANY_CODE_REJECTED in x for x in issues))

    def test_output_root_isolation_rejects_foreign_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(RETRY_BASE_ARGS + ["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.PHASE3_RETRY_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_phase3_expansion_root_write_blocked(self) -> None:
        ok, err = runner.validate_phase3_retry_output_root(PHASE3_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.PHASE3_EXPANSION_BASELINE_WRITE_FORBIDDEN)

    def test_phase25_expansion_root_write_blocked(self) -> None:
        ok, err = runner.validate_phase3_retry_output_root(PHASE25_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.PHASE25_BASELINE_WRITE_FORBIDDEN)

    def test_phase25_failed_retry_root_write_blocked(self) -> None:
        ok, err = runner.validate_phase3_retry_output_root(PHASE25_RETRY_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.RETRY_BASELINE_WRITE_FORBIDDEN)

    def test_pdf_download_blocked(self) -> None:
        result = _run(RETRY_BASE_ARGS + ["--dry-run", "--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(RETRY_BASE_ARGS + ["--dry-run", "--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--run-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--extract-sections", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(RETRY_BASE_ARGS + ["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, err in (
            ("--write-db", runner.DB_WRITE_REQUESTED_NOT_ALLOWED),
            ("--write-minio", runner.MINIO_WRITE_REQUESTED_NOT_ALLOWED),
            ("--run-rag", runner.RAG_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(RETRY_BASE_ARGS + ["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, err in (
            ("--mark-verified", runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
            ("--mark-production-ready", runner.PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(RETRY_BASE_ARGS + ["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_dry_run_report_generated(self) -> None:
        result = _run(RETRY_BASE_ARGS + ["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT), msg=DRYRUN_REPORT)
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), runner.REQUIRED_PHASE3_RETRY_UNIVERSE_SIZE)
        self.assertEqual(set(rows[0].keys()), set(runner.PHASE3_RETRY_DRYRUN_REPORT_COLUMNS))
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
        for row in rows:
            self.assertEqual(row["cninfo_call_planned"], "0")
            self.assertEqual(row["pdf_download"], "0")
            self.assertEqual(row["pdf_parse"], "0")
            self.assertEqual(row["ocr"], "0")
            self.assertEqual(row["extraction"], "0")
            self.assertEqual(row["db_write"], "0")
            self.assertEqual(row["minio_write"], "0")
            self.assertEqual(row["rag_run"], "0")
        self.assertNotIn(runner.PHASE3_SUCCESS_HOLD_CASE_ID, {r["case_id"] for r in rows})

    def test_planned_request_count_generated(self) -> None:
        result = _run(RETRY_BASE_ARGS + ["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("planned_request_count_total=", result.stdout)
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        total = sum(int(r["planned_request_count"]) for r in rows)
        self.assertEqual(total, 198)
        self.assertIn(f"planned_request_count_total={total}", result.stdout)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary_path = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_b_class_phase3_100_failed_retry_runner_test_summary.md",
    )
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(
            "# B-class Phase 3 100 Failed-Case Isolated Retry Runner Test Summary\n\n"
            f"- tests_run: {result.testsRun}\n"
            f"- passed: {passed}\n"
            f"- failed: {len(result.failures)}\n"
            f"- errors: {len(result.errors)}\n"
            f"- CNINFO calls: **0**\n"
            f"- gate: **READY_FOR_APPROVAL** (runner offline prep)\n"
        )
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
