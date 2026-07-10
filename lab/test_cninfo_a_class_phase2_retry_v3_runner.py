"""
A-class Phase 2 retry v3 runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_a_class_phase2_retry_v3_runner.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_metadata_expansion.py")
RETRY_V3_UNIVERSE = runner.DEFAULT_RETRY_V3_UNIVERSE_CSV
RETRY_V3_OUTPUT_ROOT = runner.DEFAULT_RETRY_V3_OUTPUT_ROOT
RETRY_V3_DRYRUN_REPORT = os.path.join(
    RETRY_V3_OUTPUT_ROOT, "reports", "a_class_phase2_retry_v3_dryrun_report.csv"
)
RETRY_V3_DRYRUN_SUMMARY = os.path.join(
    RETRY_V3_OUTPUT_ROOT, "reports", "a_class_phase2_retry_v3_dryrun_summary.md"
)
EXPANSION_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
RETRY_V1_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_RETRY_V2_OUTPUT_ROOT
PRECHECK_OUTPUT_ROOT = runner.PRECHECK_OUTPUT_ROOT

V3_DRYRUN_ARGS = [
    "--retry-v3",
    "--dry-run",
    "--universe-csv",
    RETRY_V3_UNIVERSE,
    "--output-root",
    RETRY_V3_OUTPUT_ROOT,
]


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


def _file_sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class TestAClassPhase2RetryV3Runner(unittest.TestCase):
    def test_dry_run_retry_v3_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(V3_DRYRUN_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_retry_v3_requires_universe_csv(self) -> None:
        result = _run(["--retry-v3", "--dry-run"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V3_UNIVERSE_CSV_REQUIRED, result.stderr)

    def test_retry_v3_universe_size_must_equal_8(self) -> None:
        result = _run(V3_DRYRUN_ARGS + ["--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_only_unresolved_8_case_ids_allowed(self) -> None:
        case = runner.RetryUniverseCase(
            case_id="A2M099",
            company_code="600000",
            company_name="测试",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            original_failure_type="network_error",
            original_failure_reason="test",
            retry_include="yes",
            retry_strategy="",
            notes="",
        )
        issues = runner.validate_retry_case(case)
        self.assertIn(runner.NON_RETRY_CASE_REJECTED, issues)

    def test_successful_12_case_ids_rejected(self) -> None:
        for case_id in runner.SUCCESSFUL_CASE_IDS:
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
                retry_strategy="",
                notes="",
            )
            issues = runner.validate_retry_case(case)
            self.assertIn(
                runner.SUCCESSFUL_CASE_IN_RETRY_FORBIDDEN,
                issues,
                msg=case_id,
            )

    def test_retry_v3_include_must_be_yes_for_all_rows(self) -> None:
        cases = runner.load_retry_universe(RETRY_V3_UNIVERSE)
        self.assertEqual(len(cases), 8)
        for case in cases:
            self.assertEqual(case.retry_include, "yes")

    def test_report_type_is_preserved(self) -> None:
        cases = runner.load_retry_universe(RETRY_V3_UNIVERSE)
        by_id = {c.case_id: c for c in cases}
        with open(RETRY_V3_UNIVERSE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                case_id = row["case_id"]
                self.assertEqual(by_id[case_id].report_type, row["report_type"])

    def test_report_period_is_preserved(self) -> None:
        cases = runner.load_retry_universe(RETRY_V3_UNIVERSE)
        by_id = {c.case_id: c for c in cases}
        self.assertEqual(by_id["A2M005"].expected_period, "2024-12-31")
        self.assertEqual(by_id["A2M010"].expected_period, "2024-06-30")
        self.assertEqual(by_id["A2M013"].expected_period, "2025-03-31")
        with open(RETRY_V3_UNIVERSE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                case_id = row["case_id"]
                self.assertEqual(by_id[case_id].expected_period, row["report_period"])

    def test_input_universe_csv_not_mutated(self) -> None:
        before = _file_sha256(RETRY_V3_UNIVERSE)
        with open(RETRY_V3_UNIVERSE, newline="", encoding="utf-8") as f:
            header = next(csv.reader(f))
        self.assertIn("retry_v3_include", header)
        self.assertIn("report_period", header)
        self.assertNotIn("retry_include", header)
        result = _run(V3_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        after = _file_sha256(RETRY_V3_UNIVERSE)
        self.assertEqual(before, after)

    def test_retry_v3_output_root_accepted(self) -> None:
        ok, err = runner.validate_retry_v3_output_root(RETRY_V3_OUTPUT_ROOT)
        self.assertTrue(ok, msg=err)

    def test_original_phase2_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--retry-v3",
                "--dry-run",
                "--universe-csv",
                RETRY_V3_UNIVERSE,
                "--output-root",
                EXPANSION_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE2_EXPANSION_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--retry-v3",
                "--dry-run",
                "--universe-csv",
                RETRY_V3_UNIVERSE,
                "--output-root",
                RETRY_V1_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V1_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v2_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--retry-v3",
                "--dry-run",
                "--universe-csv",
                RETRY_V3_UNIVERSE,
                "--output-root",
                RETRY_V2_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V2_WRITE_FORBIDDEN, result.stderr)

    def test_precheck_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--retry-v3",
                "--dry-run",
                "--universe-csv",
                RETRY_V3_UNIVERSE,
                "--output-root",
                PRECHECK_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PRECHECK_WRITE_FORBIDDEN, result.stderr)

    def test_live_mode_requires_retry_v3_approval_flag(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                [
                    "--retry-v3",
                    "--live",
                    "--universe-csv",
                    RETRY_V3_UNIVERSE,
                    "--output-root",
                    RETRY_V3_OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V3_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        wrong_flags = (
            "--approve-a-class-phase2-metadata-expansion",
            "--approve-a-class-phase2-failed-retry",
            "--approve-a-class-phase2-network-recovery-retry-v2",
            "--approve-a-class-tiny-live-metadata",
            "--approve-phase1-tiny-live-metadata",
            "--approve-full-harvest",
            "--approve-b-class-tiny-live-validation",
        )
        for flag in wrong_flags:
            with mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                result = _run(
                    [
                        "--retry-v3",
                        "--live",
                        "--universe-csv",
                        RETRY_V3_UNIVERSE,
                        "--output-root",
                        RETRY_V3_OUTPUT_ROOT,
                        flag,
                    ]
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(runner.RETRY_V3_WRONG_APPROVAL, result.stderr)

    def test_pdf_download_blocked(self) -> None:
        result = _run(V3_DRYRUN_ARGS + ["--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(V3_DRYRUN_ARGS + ["--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--enable-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--enable-extraction", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(V3_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, err in (
            ("--write-db", runner.DB_WRITE_REQUESTED_NOT_ALLOWED),
            ("--write-minio", runner.MINIO_WRITE_REQUESTED_NOT_ALLOWED),
            ("--run-rag", runner.RAG_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(V3_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, err in (
            ("--mark-verified", runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
            ("--mark-production-ready", runner.PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(V3_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_dry_run_retry_v3_report_generated(self) -> None:
        result = _run(V3_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(RETRY_V3_DRYRUN_REPORT))
        with open(RETRY_V3_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), runner.RETRY_REQUIRED_UNIVERSE_SIZE)
        self.assertEqual(set(rows[0].keys()), set(runner.RETRY_V3_DRYRUN_COLUMNS))
        case_ids = {row["case_id"] for row in rows}
        self.assertEqual(case_ids, runner.RETRY_ALLOWED_CASE_IDS)
        for row in rows:
            self.assertEqual(row["retry_v3_include"], "yes")
            self.assertEqual(row["pdf_download"], "0")
            self.assertEqual(row["cninfo_call_planned"], "0")
            self.assertEqual(row["dryrun_status"], "planned_ok")

    def test_dry_run_retry_v3_summary_generated(self) -> None:
        result = _run(V3_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(RETRY_V3_DRYRUN_SUMMARY))
        with open(RETRY_V3_DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("8/8", content)
        self.assertIn("CNINFO calls: 0", content)
        self.assertIn(runner.RETRY_V3_RUNNER_GATE, content)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
