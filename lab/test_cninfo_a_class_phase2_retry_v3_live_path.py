"""
A-class Phase 2 retry v3 live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_a_class_phase2_retry_v3_live_path.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
import unittest
from typing import Any, Dict, List
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402
import run_cninfo_a_class_tiny_live_metadata_validation as tiny_live  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_metadata_expansion.py")
RETRY_V3_UNIVERSE = runner.DEFAULT_RETRY_V3_UNIVERSE_CSV
RETRY_V3_OUTPUT_ROOT = runner.DEFAULT_RETRY_V3_OUTPUT_ROOT
EXPANSION_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
RETRY_V1_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_RETRY_V2_OUTPUT_ROOT
PRECHECK_OUTPUT_ROOT = runner.PRECHECK_OUTPUT_ROOT
LIVE_REPORT = os.path.join(
    RETRY_V3_OUTPUT_ROOT, "reports", "a_class_phase2_retry_v3_report.csv"
)
LIVE_SUMMARY = os.path.join(
    RETRY_V3_OUTPUT_ROOT, "reports", "a_class_phase2_retry_v3_summary.md"
)
QUALITY_REPORT = os.path.join(
    RETRY_V3_OUTPUT_ROOT, "reports", "a_class_phase2_retry_v3_quality_report.csv"
)

LIVE_ARGS = [
    "--retry-v3",
    "--live",
    "--universe-csv",
    RETRY_V3_UNIVERSE,
    "--output-root",
    RETRY_V3_OUTPUT_ROOT,
    "--approve-a-class-phase2-retry-v3",
]

RETRY_V3_CASE_IDS = sorted(runner.RETRY_ALLOWED_CASE_IDS)


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


def _mock_execute_live_case(
    tl_case: Any,
    stats: Any,
) -> Dict[str, Any]:
    stats.cninfo_requests += 2
    stats.success_count += 1
    return {
        "retrieval_status": "found",
        "quality_status": "pass",
        "lineage_status": "discovered",
        "announcement_id": "ann-001",
        "announcement_title": "测试公告",
        "announcement_time": "2024-01-01 00:00:00",
        "pdf_url_present": "yes",
        "adjunct_url_present": "no",
        "failure_type": "",
        "notes": "mock",
    }


def _gate_row(
    case_id: str,
    retry_v3_retrieval_status: str,
    quality_status: str = "pass",
    lineage_status: str = "discovered",
    notes: str = "mock lineage",
) -> Dict[str, str]:
    return {
        "case_id": case_id,
        "retry_v3_retrieval_status": retry_v3_retrieval_status,
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "notes": notes,
    }


class TestAClassPhase2RetryV3LivePath(unittest.TestCase):
    def test_live_without_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
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
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V3_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--retry-v3",
                    "--live",
                    "--universe-csv",
                    RETRY_V3_UNIVERSE,
                    "--output-root",
                    RETRY_V3_OUTPUT_ROOT,
                    "--approve-a-class-phase2-failed-retry",
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V3_WRONG_APPROVAL, result.stderr)

    def test_live_with_approval_processes_only_8_retry_v3_cases(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ) as mock_exec:
            rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        self.assertEqual(mock_exec.call_count, runner.RETRY_REQUIRED_UNIVERSE_SIZE)
        case_ids = {c.args[0].case_id for c in mock_exec.call_args_list}
        self.assertEqual(case_ids, runner.RETRY_ALLOWED_CASE_IDS)

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

    def test_retry_v3_universe_size_must_equal_8(self) -> None:
        result = _run(LIVE_ARGS + ["--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_retry_v3_include_must_be_yes(self) -> None:
        cases = runner.load_retry_universe(RETRY_V3_UNIVERSE)
        self.assertEqual(len(cases), 8)
        for case in cases:
            self.assertEqual(case.retry_include, "yes")

    def test_report_type_is_preserved(self) -> None:
        cases = runner.load_retry_universe(RETRY_V3_UNIVERSE)
        by_id = {c.case_id: c for c in cases}
        with open(RETRY_V3_UNIVERSE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                self.assertEqual(by_id[row["case_id"]].report_type, row["report_type"])

    def test_report_period_is_preserved(self) -> None:
        cases = runner.load_retry_universe(RETRY_V3_UNIVERSE)
        by_id = {c.case_id: c for c in cases}
        with open(RETRY_V3_UNIVERSE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                self.assertEqual(by_id[row["case_id"]].expected_period, row["report_period"])

    def test_input_universe_csv_not_mutated(self) -> None:
        before = _file_sha256(RETRY_V3_UNIVERSE)
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ):
            rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        after = _file_sha256(RETRY_V3_UNIVERSE)
        self.assertEqual(before, after)

    def test_output_root_isolation_enforced(self) -> None:
        ok, err = runner.validate_retry_v3_output_root(RETRY_V3_OUTPUT_ROOT)
        self.assertTrue(ok, msg=err)

    def test_original_phase2_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--retry-v3",
                "--live",
                "--universe-csv",
                RETRY_V3_UNIVERSE,
                "--output-root",
                EXPANSION_OUTPUT_ROOT,
                "--approve-a-class-phase2-retry-v3",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE2_EXPANSION_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--retry-v3",
                "--live",
                "--universe-csv",
                RETRY_V3_UNIVERSE,
                "--output-root",
                RETRY_V1_OUTPUT_ROOT,
                "--approve-a-class-phase2-retry-v3",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V1_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v2_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--retry-v3",
                "--live",
                "--universe-csv",
                RETRY_V3_UNIVERSE,
                "--output-root",
                RETRY_V2_OUTPUT_ROOT,
                "--approve-a-class-phase2-retry-v3",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V2_WRITE_FORBIDDEN, result.stderr)

    def test_precheck_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--retry-v3",
                "--live",
                "--universe-csv",
                RETRY_V3_UNIVERSE,
                "--output-root",
                PRECHECK_OUTPUT_ROOT,
                "--approve-a-class-phase2-retry-v3",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PRECHECK_WRITE_FORBIDDEN, result.stderr)

    def test_pdf_download_blocked(self) -> None:
        result = _run(LIVE_ARGS + ["--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(LIVE_ARGS + ["--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--enable-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--enable-extraction", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, err in (
            ("--write-db", runner.DB_WRITE_REQUESTED_NOT_ALLOWED),
            ("--write-minio", runner.MINIO_WRITE_REQUESTED_NOT_ALLOWED),
            ("--run-rag", runner.RAG_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, err in (
            ("--mark-verified", runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
            ("--mark-production-ready", runner.PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_live_report_paths_are_isolated(self) -> None:
        self.assertTrue(LIVE_REPORT.startswith(RETRY_V3_OUTPUT_ROOT))
        self.assertTrue(LIVE_SUMMARY.startswith(RETRY_V3_OUTPUT_ROOT))
        self.assertTrue(QUALITY_REPORT.startswith(RETRY_V3_OUTPUT_ROOT))
        self.assertIn("a_class_phase2_retry_v3_report.csv", LIVE_REPORT)
        self.assertIn("a_class_phase2_retry_v3_summary.md", LIVE_SUMMARY)
        self.assertIn("a_class_phase2_retry_v3_quality_report.csv", QUALITY_REPORT)
        self.assertNotIn("metadata_expansion", LIVE_REPORT)
        self.assertNotIn("metadata_retry/", LIVE_REPORT)
        self.assertNotIn("metadata_retry_v2", LIVE_REPORT)
        self.assertNotIn("reachability_precheck", LIVE_REPORT)

    def test_live_path_tests_call_cninfo_zero_times_through_mocks(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            with mock.patch(
                "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
                side_effect=_mock_execute_live_case,
            ):
                rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        get_mock.assert_not_called()
        post_mock.assert_not_called()

    def test_mock_8_of_8_acceptable_produces_pass_with_caveat(self) -> None:
        rows = [_gate_row(case_id, "found") for case_id in RETRY_V3_CASE_IDS]
        stats = tiny_live.LiveStats()
        gate = runner.compute_retry_v3_execution_gate(stats, rows, [], 8)
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_6_of_8_acceptable_produces_pass_with_caveat(self) -> None:
        rows: List[Dict[str, str]] = []
        for idx, case_id in enumerate(RETRY_V3_CASE_IDS):
            status = "found" if idx < 6 else "network_error"
            rows.append(_gate_row(case_id, status))
        stats = tiny_live.LiveStats()
        gate = runner.compute_retry_v3_execution_gate(stats, rows, [], 8)
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_5_of_8_acceptable_produces_fail_review_required(self) -> None:
        rows: List[Dict[str, str]] = []
        for idx, case_id in enumerate(RETRY_V3_CASE_IDS):
            status = "found" if idx < 5 else "network_error"
            rows.append(_gate_row(case_id, status))
        stats = tiny_live.LiveStats()
        gate = runner.compute_retry_v3_execution_gate(stats, rows, [], 8)
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")

    def test_execution_gate_never_uses_pass(self) -> None:
        rows = [_gate_row(case_id, "found") for case_id in RETRY_V3_CASE_IDS]
        stats = tiny_live.LiveStats()
        gate = runner.compute_retry_v3_execution_gate(stats, rows, [], 8)
        self.assertNotEqual(gate, "PASS")
        self.assertEqual(runner.RETRY_V3_EXECUTION_GATE_PASS, "PASS_WITH_CAVEAT")
        self.assertIn(gate, ("PASS_WITH_CAVEAT", "FAIL_REVIEW_REQUIRED"))


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
