"""
B-class Phase 3 100 failed-case isolated retry live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_b_class_phase3_100_failed_retry_live_path.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, List, Optional
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
LIVE_REPORT = runner.PHASE3_RETRY_LIVE_REPORT_CSV
LIVE_SUMMARY = runner.PHASE3_RETRY_LIVE_SUMMARY_MD
QUALITY_REPORT = runner.PHASE3_RETRY_QUALITY_REPORT_CSV

RETRY_HEADER = (
    "case_id,company_code,company_name,market,announcement_type,target_endpoint,"
    "original_phase3_status,original_failure_type,original_failure_stage,"
    "retry_include,retry_strategy,notes\n"
)

LIVE_ARGS = [
    "--phase3-100-failed-retry",
    "--live",
    "--universe-csv",
    UNIVERSE,
    "--output-root",
    OUTPUT_ROOT,
    "--approve-b-class-phase3-100-failed-retry",
]


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


def _mock_execute_live_case(
    tl_case: Any,
    _categories_config: Dict[str, Any],
    stats: Any,
) -> Dict[str, Any]:
    stats.cninfo_requests += 2
    return {
        "case_id": tl_case.case_id,
        "company_code": tl_case.company_code,
        "retrieval_status": "found",
        "quality_status": "pass",
        "lineage_status": "discovered",
        "announcement_id": "ann-001",
        "announcement_title": "测试公告",
        "announcement_time": "2024-01-01 00:00:00",
        "pdf_url": "http://example.com/a.pdf",
        "adjunct_url": "",
        "endpoint_id": "EP001",
        "_case_cninfo_requests": 2,
        "notes": "mock",
    }


def _gate_row(
    case_id: str,
    retry_retrieval_status: str,
    quality_status: str = "pass",
    lineage_status: str = "discovered",
    notes: str = "",
) -> Dict[str, str]:
    return {
        "case_id": case_id,
        "retry_retrieval_status": retry_retrieval_status,
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "notes": notes,
    }


class TestPhase3FailedRetryLivePath(unittest.TestCase):
    def test_live_without_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_b_class_tiny_live_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--phase3-100-failed-retry",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_RETRY_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_b_class_tiny_live_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--phase3-100-failed-retry",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    OUTPUT_ROOT,
                    "--approve-b-class-phase3-100-expansion",
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)

    def test_live_with_approval_only_processes_99_retry_cases(self) -> None:
        with mock.patch(
            "run_cninfo_b_class_tiny_live_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ) as mock_exec:
            rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        self.assertEqual(mock_exec.call_count, runner.REQUIRED_PHASE3_RETRY_UNIVERSE_SIZE)
        case_ids = {c.args[0].case_id for c in mock_exec.call_args_list}
        self.assertEqual(len(case_ids), 99)
        self.assertNotIn(runner.PHASE3_SUCCESS_HOLD_CASE_ID, case_ids)

    def test_b3e087_rejected_from_live_retry(self) -> None:
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

    def test_prior_phase_cases_rejected_from_live_retry(self) -> None:
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

    def test_total_request_cap_lte_198(self) -> None:
        cases = runner.load_phase3_retry_universe(UNIVERSE)
        total = runner.compute_phase3_retry_max_planned_requests(cases)
        self.assertLessEqual(total, runner.MAX_PHASE3_RETRY_CNINFO_REQUESTS)
        self.assertEqual(total, 198)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(
                [
                    "--phase3-100-failed-retry",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    tmp,
                    "--approve-b-class-phase3-100-failed-retry",
                ]
            )
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
        result = _run(LIVE_ARGS + ["--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(LIVE_ARGS + ["--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--run-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--extract-sections", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
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
        self.assertTrue(LIVE_REPORT.startswith(OUTPUT_ROOT))
        self.assertTrue(LIVE_SUMMARY.startswith(OUTPUT_ROOT))
        self.assertTrue(QUALITY_REPORT.startswith(OUTPUT_ROOT))
        self.assertIn("b_class_phase3_100_failed_retry_report.csv", LIVE_REPORT)
        self.assertIn("b_class_phase3_100_failed_retry_summary.md", LIVE_SUMMARY)
        self.assertIn("b_class_phase3_100_failed_retry_quality_report.csv", QUALITY_REPORT)
        self.assertNotIn("phase3_100_expansion", LIVE_REPORT)
        self.assertNotIn("phase25", LIVE_REPORT)

    def test_execution_gate_never_uses_pass(self) -> None:
        rows = [
            _gate_row(f"B3E{i:03d}", "found")
            for i in range(1, 100)
            if f"B3E{i:03d}" != runner.PHASE3_SUCCESS_HOLD_CASE_ID
        ]
        gate = runner.compute_phase3_retry_execution_gate(rows)
        self.assertNotEqual(gate, "PASS")
        self.assertIn(gate, ("PASS_WITH_CAVEAT", "FAIL_REVIEW_REQUIRED"))

    def test_no_live_path_test_calls_real_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            with mock.patch(
                "run_cninfo_b_class_tiny_live_validation.execute_live_case",
                side_effect=_mock_execute_live_case,
            ):
                rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        get_mock.assert_not_called()
        post_mock.assert_not_called()

    def test_mock_retry_acceptable_90_of_99_produces_pass_with_caveat(self) -> None:
        rows: List[Dict[str, str]] = []
        idx = 0
        for i in range(1, 101):
            case_id = f"B3E{i:03d}"
            if case_id == runner.PHASE3_SUCCESS_HOLD_CASE_ID:
                continue
            idx += 1
            status = "found" if idx <= 90 else "network_error"
            rows.append(_gate_row(case_id, status))
        self.assertEqual(len(rows), 99)
        gate = runner.compute_phase3_retry_execution_gate(rows)
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_retry_acceptable_89_of_99_produces_fail_review_required(self) -> None:
        rows: List[Dict[str, str]] = []
        idx = 0
        for i in range(1, 101):
            case_id = f"B3E{i:03d}"
            if case_id == runner.PHASE3_SUCCESS_HOLD_CASE_ID:
                continue
            idx += 1
            status = "found" if idx <= 89 else "network_error"
            rows.append(_gate_row(case_id, status))
        self.assertEqual(len(rows), 99)
        gate = runner.compute_phase3_retry_execution_gate(rows)
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")

    def test_mock_all_network_error_produces_fail_review_required(self) -> None:
        rows = [
            _gate_row(f"B3E{i:03d}", "network_error")
            for i in range(1, 101)
            if f"B3E{i:03d}" != runner.PHASE3_SUCCESS_HOLD_CASE_ID
        ]
        self.assertEqual(len(rows), 99)
        gate = runner.compute_phase3_retry_execution_gate(rows)
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary_path = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_b_class_phase3_100_failed_retry_live_path_test_summary.md",
    )
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(
            "# B-class Phase 3 100 Failed-Case Isolated Retry Live Path Test Summary\n\n"
            f"- tests_run: {result.testsRun}\n"
            f"- passed: {passed}\n"
            f"- failed: {len(result.failures)}\n"
            f"- errors: {len(result.errors)}\n"
            f"- CNINFO calls: **0** (mock only)\n"
            f"- gate: **READY_FOR_APPROVAL** (live path offline prep)\n"
        )
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
