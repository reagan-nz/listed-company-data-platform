"""
B-class Phase 3 100 retry_v2 live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_b_class_phase3_100_retry_v2_live_path.py
"""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, List
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_b_class_phase25_expansion_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_b_class_phase25_expansion_validation.py")
UNIVERSE = runner.DEFAULT_PHASE3_RETRY_V2_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT
MOCK_TEST_PARENT = os.path.join(OUTPUT_ROOT, "_mock_live_test")
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
PHASE3_RETRY_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_OUTPUT_ROOT
EP002_PRECHECK_ROOT = runner.DEFAULT_EP002_PRECHECK_ROOT
PHASE25_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
PHASE25_RETRY_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
LIVE_REPORT = runner.PHASE3_RETRY_V2_LIVE_REPORT_CSV
LIVE_SUMMARY = runner.PHASE3_RETRY_V2_LIVE_SUMMARY_MD
QUALITY_REPORT = runner.PHASE3_RETRY_V2_QUALITY_REPORT_CSV

RETRY_V2_HEADER = (
    "retry_v2_case_id,original_case_id,company_code,company_name,market,"
    "announcement_type,target_endpoint,original_phase3_status,failed_retry_status,"
    "final_effective_status_before_retry_v2,persistent_failure_stage,schema_impact,"
    "quality_impact,ep002_precheck_signal,retry_v2_include,retry_v2_reason,risk_note,notes\n"
)

LIVE_ARGS = [
    "--phase3-100-retry-v2",
    "--live",
    "--universe-csv",
    UNIVERSE,
    "--output-root",
    OUTPUT_ROOT,
    "--approve-b-class-phase3-100-retry-v2",
]

DRYRUN_ARGS = [
    "--phase3-100-retry-v2",
    "--dry-run",
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


def _sample_retry_v2_row(
    retry_v2_case_id: str = "B3R2_001",
    original_case_id: str = "B3E001",
    company_code: str = "600010",
) -> dict:
    return {
        "retry_v2_case_id": retry_v2_case_id,
        "original_case_id": original_case_id,
        "company_code": company_code,
        "company_name": "测试",
        "market": "SSE主板",
        "announcement_type": "periodic_report",
        "target_endpoint": "EP001;EP004",
        "original_phase3_status": "network_error",
        "failed_retry_status": "network_error",
        "final_effective_status_before_retry_v2": "unresolved_ep002_orgid_network_failure",
        "persistent_failure_stage": "EP002_topSearch_orgId",
        "schema_impact": "none",
        "quality_impact": "unresolved_network_caveat",
        "ep002_precheck_signal": "no_precheck_sample",
        "retry_v2_include": "yes",
        "retry_v2_reason": "x",
        "risk_note": "x",
        "notes": "x",
    }


def _gate_row(
    retry_v2_case_id: str,
    original_case_id: str,
    retry_retrieval_status: str,
    quality_status: str = "pass",
    lineage_status: str = "discovered",
) -> Dict[str, str]:
    return {
        "retry_v2_case_id": retry_v2_case_id,
        "original_case_id": original_case_id,
        "retry_retrieval_status": retry_retrieval_status,
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "notes": "",
    }


def _normalize_root(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def _is_production_retry_v2_output_root(output_root: str) -> bool:
    return _normalize_root(output_root) == _normalize_root(OUTPUT_ROOT)


def _live_args_for_output_root(output_root: str) -> List[str]:
    return [
        "--phase3-100-retry-v2", "--live", "--universe-csv", UNIVERSE,
        "--output-root", output_root, "--approve-b-class-phase3-100-retry-v2",
    ]


def _is_allowed_mock_test_output_root(output_root: str) -> bool:
    root = _normalize_root(output_root)
    parent = _normalize_root(MOCK_TEST_PARENT)
    return root.startswith(parent + os.sep)


def _create_mock_test_output_root() -> str:
    os.makedirs(MOCK_TEST_PARENT, exist_ok=True)
    return tempfile.mkdtemp(prefix="run_", dir=MOCK_TEST_PARENT)


def _cleanup_temp_output_root(temp_root: str) -> None:
    if _is_production_retry_v2_output_root(temp_root):
        raise RuntimeError("拒绝清理生产 retry_v2 output root")
    if not _is_allowed_mock_test_output_root(temp_root):
        raise RuntimeError("拒绝清理非 mock 测试目录")
    shutil.rmtree(temp_root, ignore_errors=True)


def _cleanup_mock_live_artifacts() -> None:
    _cleanup_temp_output_root(OUTPUT_ROOT)


class TestPhase3RetryV2LivePath(unittest.TestCase):
    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_b_class_tiny_live_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--phase3-100-retry-v2",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_RETRY_V2_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_b_class_tiny_live_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--phase3-100-retry-v2",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    OUTPUT_ROOT,
                    "--approve-b-class-phase3-100-failed-retry",
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)

    def test_live_path_function_exists_and_wired(self) -> None:
        self.assertTrue(hasattr(runner, "process_phase3_retry_v2_live"))
        self.assertTrue(callable(runner.process_phase3_retry_v2_live))
        self.assertTrue(hasattr(runner, "write_live_phase3_retry_v2_reports"))
        with mock.patch(
            "run_cninfo_b_class_tiny_live_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ):
            tmp_root = _create_mock_test_output_root()
            try:
                rc = runner.main(_live_args_for_output_root(tmp_root))
            finally:
                _cleanup_temp_output_root(tmp_root)
        self.assertEqual(rc, 0)

    def test_universe_must_equal_91(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(
                tmp,
                fieldnames=list(_sample_retry_v2_row().keys()),
            )
            writer.writeheader()
            writer.writerow(_sample_retry_v2_row())
            tmp_path = tmp.name
        try:
            cases = runner.load_phase3_retry_v2_universe(tmp_path)
            ok, err = runner.validate_phase3_retry_v2_universe_size(cases)
            self.assertFalse(ok)
            self.assertIn(runner.PHASE3_RETRY_V2_UNIVERSE_SIZE_VIOLATION, err)
        finally:
            os.unlink(tmp_path)

    def test_b3e087_rejected(self) -> None:
        case = runner.Phase3RetryV2UniverseCase(
            retry_v2_case_id="B3R2_001",
            original_case_id=runner.PHASE3_SUCCESS_HOLD_CASE_ID,
            company_code="000786",
            company_name="北新建材",
            market="SZSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            original_phase3_status="found",
            failed_retry_status="found",
            final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
            persistent_failure_stage="EP002_topSearch_orgId",
            schema_impact="none",
            quality_impact="unresolved_network_caveat",
            ep002_precheck_signal="no_precheck_sample",
            retry_v2_include="yes",
            retry_v2_reason="x",
            risk_note="x",
            notes="x",
        )
        issues = runner.validate_phase3_retry_v2_case(case)
        self.assertIn(runner.SUCCESSFUL_PHASE3_CASE_RETRY_REJECTED, issues)

    def test_recovered_cases_rejected(self) -> None:
        for original_case_id in runner.RECOVERED_PHASE3_CASE_IDS:
            case = runner.Phase3RetryV2UniverseCase(
                retry_v2_case_id="B3R2_001",
                original_case_id=original_case_id,
                company_code="600010",
                company_name="测试",
                market="SSE主板",
                announcement_type="periodic_report",
                target_endpoint=["EP001", "EP004"],
                original_phase3_status="network_error",
                failed_retry_status="network_error",
                final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
                persistent_failure_stage="EP002_topSearch_orgId",
                schema_impact="none",
                quality_impact="unresolved_network_caveat",
                ep002_precheck_signal="no_precheck_sample",
                retry_v2_include="yes",
                retry_v2_reason="x",
                risk_note="x",
                notes="x",
            )
            issues = runner.validate_phase3_retry_v2_case(case)
            self.assertIn(
                f"{runner.RECOVERED_CASE_IN_RETRY_V2_FORBIDDEN}:{original_case_id}",
                issues,
                msg=original_case_id,
            )

    def test_prior_phases_rejected(self) -> None:
        for original_case_id in ("B25E001", "B2E001", "B1E001"):
            case = runner.Phase3RetryV2UniverseCase(
                retry_v2_case_id="B3R2_001",
                original_case_id=original_case_id,
                company_code="600099",
                company_name="测试",
                market="SSE主板",
                announcement_type="periodic_report",
                target_endpoint=["EP001", "EP004"],
                original_phase3_status="network_error",
                failed_retry_status="network_error",
                final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
                persistent_failure_stage="EP002_topSearch_orgId",
                schema_impact="none",
                quality_impact="unresolved_network_caveat",
                ep002_precheck_signal="no_precheck_sample",
                retry_v2_include="yes",
                retry_v2_reason="x",
                risk_note="x",
                notes="x",
            )
            issues = runner.validate_phase3_retry_v2_case(case)
            self.assertIn(runner.PRIOR_PHASE_CASE_ID_REJECTED, issues, msg=original_case_id)

    def test_replacement_cases_rejected(self) -> None:
        case = runner.Phase3RetryV2UniverseCase(
            retry_v2_case_id="B3R2_001",
            original_case_id="B3E001",
            company_code="999999",
            company_name="替换公司",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            original_phase3_status="network_error",
            failed_retry_status="network_error",
            final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
            persistent_failure_stage="EP002_topSearch_orgId",
            schema_impact="none",
            quality_impact="unresolved_network_caveat",
            ep002_precheck_signal="no_precheck_sample",
            retry_v2_include="yes",
            retry_v2_reason="x",
            risk_note="x",
            notes="x",
        )
        issues = runner.validate_phase3_retry_v2_case(case)
        self.assertIn(f"{runner.REPLACEMENT_CASE_IN_RETRY_V2_FORBIDDEN}:B3E001", issues)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(
                [
                    "--phase3-100-retry-v2",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    tmp,
                    "--approve-b-class-phase3-100-retry-v2",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.PHASE3_RETRY_V2_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_phase3_expansion_root_write_blocked(self) -> None:
        ok, err = runner.validate_phase3_retry_v2_output_root(PHASE3_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.PHASE3_EXPANSION_BASELINE_WRITE_FORBIDDEN)

    def test_failed_retry_root_write_blocked(self) -> None:
        ok, err = runner.validate_phase3_retry_v2_output_root(PHASE3_RETRY_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.PHASE3_FAILED_RETRY_BASELINE_WRITE_FORBIDDEN)

    def test_ep002_precheck_root_write_blocked(self) -> None:
        ok, err = runner.validate_phase3_retry_v2_output_root(EP002_PRECHECK_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.EP002_PRECHECK_BASELINE_WRITE_FORBIDDEN)

    def test_phase25_roots_write_blocked(self) -> None:
        for root, err_code in (
            (PHASE25_OUTPUT_ROOT, runner.PHASE25_BASELINE_WRITE_FORBIDDEN),
            (PHASE25_RETRY_OUTPUT_ROOT, runner.RETRY_BASELINE_WRITE_FORBIDDEN),
        ):
            ok, err = runner.validate_phase3_retry_v2_output_root(root)
            self.assertFalse(ok, msg=root)
            self.assertEqual(err, err_code, msg=root)

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

    def test_live_path_does_not_call_real_cninfo(self) -> None:
        tmp_root = _create_mock_test_output_root()
        try:
            with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
                with mock.patch(
                    "run_cninfo_b_class_tiny_live_validation.execute_live_case",
                    side_effect=_mock_execute_live_case,
                ) as mock_exec:
                    rc = runner.main(_live_args_for_output_root(tmp_root))
            self.assertEqual(rc, 0)
            self.assertEqual(mock_exec.call_count, runner.REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        finally:
            _cleanup_temp_output_root(tmp_root)

    def test_cleanup_refuses_production_output_root(self) -> None:
        with self.assertRaises(RuntimeError):
            _cleanup_temp_output_root(OUTPUT_ROOT)

    def test_dry_run_still_91_of_91_and_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(DRYRUN_ARGS)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_ok=91", result.stdout)

    def test_live_report_paths_are_isolated(self) -> None:
        self.assertTrue(LIVE_REPORT.startswith(OUTPUT_ROOT))
        self.assertTrue(LIVE_SUMMARY.startswith(OUTPUT_ROOT))
        self.assertTrue(QUALITY_REPORT.startswith(OUTPUT_ROOT))
        self.assertIn("b_class_phase3_100_retry_v2_report.csv", LIVE_REPORT)
        self.assertIn("b_class_phase3_100_retry_v2_summary.md", LIVE_SUMMARY)
        self.assertIn("b_class_phase3_100_retry_v2_quality_report.csv", QUALITY_REPORT)
        self.assertNotIn("phase3_100_expansion", LIVE_REPORT)
        self.assertNotIn("failed_retry", LIVE_REPORT)

    def test_execution_gate_never_uses_pass(self) -> None:
        rows = [
            _gate_row(f"B3R2_{i:03d}", f"B3E{i:03d}", "found")
            for i in range(1, 92)
        ]
        gate = runner.compute_phase3_retry_v2_execution_gate(rows)
        self.assertNotEqual(gate, "PASS")
        self.assertIn(gate, ("PASS_WITH_CAVEAT", "FAIL_REVIEW_REQUIRED"))

    def test_mock_82_of_91_produces_pass_with_caveat(self) -> None:
        cases = runner.load_phase3_retry_v2_universe(UNIVERSE)
        rows: List[Dict[str, str]] = []
        for idx, case in enumerate(cases, start=1):
            status = "found" if idx <= 82 else "network_error"
            rows.append(_gate_row(case.retry_v2_case_id, case.original_case_id, status))
        self.assertEqual(len(rows), 91)
        gate = runner.compute_phase3_retry_v2_execution_gate(rows)
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_81_of_91_produces_fail_review_required(self) -> None:
        cases = runner.load_phase3_retry_v2_universe(UNIVERSE)
        rows: List[Dict[str, str]] = []
        for idx, case in enumerate(cases, start=1):
            status = "found" if idx <= 81 else "network_error"
            rows.append(_gate_row(case.retry_v2_case_id, case.original_case_id, status))
        self.assertEqual(len(rows), 91)
        gate = runner.compute_phase3_retry_v2_execution_gate(rows)
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary_path = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_b_class_phase3_100_retry_v2_live_path_test_summary.md",
    )
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(
            "# B-class Phase 3 100 Retry v2 Live Path Test Summary\n\n"
            f"- tests_run: {result.testsRun}\n"
            f"- passed: {passed}\n"
            f"- failed: {len(result.failures)}\n"
            f"- errors: {len(result.errors)}\n"
            f"- CNINFO calls: **0** (mock only)\n"
            f"- gate: **READY_FOR_APPROVAL** (live path offline prep)\n"
            f"- approval_status: **NOT_APPROVED**\n"
        )
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
