"""
A-class Phase 3 50-company live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_a_class_phase3_50_company_live_path.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
import tempfile
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
PHASE3_UNIVERSE = runner.DEFAULT_PHASE3_UNIVERSE_CSV
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
PHASE3_DRYRUN_ARGS = [
    "--phase3-50",
    "--dry-run",
    "--universe-csv",
    PHASE3_UNIVERSE,
    "--output-root",
    PHASE3_OUTPUT_ROOT,
]
EXPANSION_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
PHASE1_OUTPUT_ROOT = runner.PHASE1_OUTPUT_ROOT
RETRY_V1_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_RETRY_V2_OUTPUT_ROOT
RETRY_V3_OUTPUT_ROOT = runner.DEFAULT_RETRY_V3_OUTPUT_ROOT
PRECHECK_OUTPUT_ROOT = runner.PRECHECK_OUTPUT_ROOT
HARVEST_ROOT = runner.C_CLASS_HARVEST_ROOT

LIVE_ARGS = [
    "--phase3-50",
    "--live",
    "--universe-csv",
    PHASE3_UNIVERSE,
    "--output-root",
    PHASE3_OUTPUT_ROOT,
    "--approve-a-class-phase3-50-company-expansion",
]

LIVE_REPORT = os.path.join(
    PHASE3_OUTPUT_ROOT, "reports", "a_class_phase3_50_company_expansion_report.csv"
)
LIVE_SUMMARY = os.path.join(
    PHASE3_OUTPUT_ROOT, "reports", "a_class_phase3_50_company_expansion_summary.md"
)
QUALITY_REPORT = os.path.join(
    PHASE3_OUTPUT_ROOT, "reports", "a_class_phase3_50_company_expansion_quality_report.csv"
)


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
        "title_match_status": "pass",
        "period_match_status": "pass",
        "pdf_url_present": "yes",
        "adjunct_url_present": "no",
        "notes": "mock",
    }


def _gate_row(
    case_id: str,
    retrieval_status: str,
    quality_status: str = "pass",
    lineage_status: str = "discovered",
) -> Dict[str, str]:
    return {
        "case_id": case_id,
        "retrieval_status": retrieval_status,
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "notes": "mock",
    }


def _cleanup_mock_live_artifacts() -> None:
    for path in (LIVE_REPORT, LIVE_SUMMARY, QUALITY_REPORT):
        if os.path.isfile(path):
            os.remove(path)
    raw_dir = os.path.join(PHASE3_OUTPUT_ROOT, "raw_metadata")
    if os.path.isdir(raw_dir):
        for name in os.listdir(raw_dir):
            if name.endswith(".json"):
                os.remove(os.path.join(raw_dir, name))


class TestAClassPhase3FiftyCompanyLivePath(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        _cleanup_mock_live_artifacts()

    def test_live_without_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--phase3-50",
                    "--live",
                    "--universe-csv",
                    PHASE3_UNIVERSE,
                    "--output-root",
                    PHASE3_OUTPUT_ROOT,
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--phase3-50",
                    "--live",
                    "--universe-csv",
                    PHASE3_UNIVERSE,
                    "--output-root",
                    PHASE3_OUTPUT_ROOT,
                    "--approve-a-class-phase2-retry-v3",
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_WRONG_APPROVAL, result.stderr)

    def test_live_path_function_exists_and_wired(self) -> None:
        self.assertTrue(callable(runner.process_phase3_50_live))
        self.assertTrue(callable(runner.compute_phase3_execution_gate))
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ) as mock_exec:
            rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        self.assertEqual(mock_exec.call_count, runner.PHASE3_REQUIRED_UNIVERSE_SIZE)

    def test_universe_size_must_equal_50(self) -> None:
        result = _run(LIVE_ARGS + ["--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_only_a3m001_through_a3m050_allowed(self) -> None:
        case = runner.Phase3UniverseCase(
            case_id="A3M099",
            company_code="601398",
            company_name="工商银行",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="",
            risk_level="low",
            phase1_overlap="no",
            phase2_overlap="no",
            phase3_include="yes",
            reason="test",
        )
        issues = runner.validate_phase3_case(case)
        self.assertIn(runner.NON_PHASE3_CASE_REJECTED, issues)

    def test_phase1_overlap_rejected(self) -> None:
        case = runner.Phase3UniverseCase(
            case_id="A3M001",
            company_code="600519",
            company_name="贵州茅台",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="",
            risk_level="low",
            phase1_overlap="yes",
            phase2_overlap="no",
            phase3_include="yes",
            reason="test",
        )
        issues = runner.validate_phase3_case(case)
        self.assertTrue(
            any(runner.PHASE1_OVERLAP_REJECTED in issue for issue in issues),
            msg=issues,
        )

    def test_phase2_overlap_rejected(self) -> None:
        case = runner.Phase3UniverseCase(
            case_id="A3M001",
            company_code="600036",
            company_name="招商银行",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="",
            risk_level="low",
            phase1_overlap="no",
            phase2_overlap="yes",
            phase3_include="yes",
            reason="test",
        )
        issues = runner.validate_phase3_case(case)
        self.assertTrue(
            any(runner.PHASE2_OVERLAP_REJECTED in issue for issue in issues),
            msg=issues,
        )

    def test_duplicate_company_code_rejected(self) -> None:
        with open(PHASE3_UNIVERSE, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        rows[1]["company_code"] = rows[0]["company_code"]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(tmp, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            tmp_path = tmp.name
        try:
            cases = runner.load_phase3_universe(tmp_path)
            ok, err = runner.validate_phase3_duplicate_company_codes(cases)
            self.assertFalse(ok)
            self.assertIn(runner.DUPLICATE_COMPANY_CODE_REJECTED, err)
        finally:
            os.unlink(tmp_path)

    def test_output_root_isolation_enforced(self) -> None:
        ok, err = runner.validate_phase3_output_root(PHASE3_OUTPUT_ROOT)
        self.assertTrue(ok, msg=err)

    def test_phase1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--phase3-50",
                "--live",
                "--universe-csv",
                PHASE3_UNIVERSE,
                "--output-root",
                PHASE1_OUTPUT_ROOT,
                "--approve-a-class-phase3-50-company-expansion",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE1_BASELINE_WRITE_FORBIDDEN, result.stderr)

    def test_phase2_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--phase3-50",
                "--live",
                "--universe-csv",
                PHASE3_UNIVERSE,
                "--output-root",
                EXPANSION_OUTPUT_ROOT,
                "--approve-a-class-phase3-50-company-expansion",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE2_EXPANSION_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--phase3-50",
                "--live",
                "--universe-csv",
                PHASE3_UNIVERSE,
                "--output-root",
                RETRY_V1_OUTPUT_ROOT,
                "--approve-a-class-phase3-50-company-expansion",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V1_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v2_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--phase3-50",
                "--live",
                "--universe-csv",
                PHASE3_UNIVERSE,
                "--output-root",
                RETRY_V2_OUTPUT_ROOT,
                "--approve-a-class-phase3-50-company-expansion",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V2_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v3_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--phase3-50",
                "--live",
                "--universe-csv",
                PHASE3_UNIVERSE,
                "--output-root",
                RETRY_V3_OUTPUT_ROOT,
                "--approve-a-class-phase3-50-company-expansion",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V3_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_precheck_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--phase3-50",
                "--live",
                "--universe-csv",
                PHASE3_UNIVERSE,
                "--output-root",
                PRECHECK_OUTPUT_ROOT,
                "--approve-a-class-phase3-50-company-expansion",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PRECHECK_WRITE_FORBIDDEN, result.stderr)

    def test_harvest_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--phase3-50",
                "--live",
                "--universe-csv",
                PHASE3_UNIVERSE,
                "--output-root",
                HARVEST_ROOT,
                "--approve-a-class-phase3-50-company-expansion",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("c_class_harvest_output_root_forbidden", result.stderr)

    def test_pdf_download_blocked(self) -> None:
        result = _run(LIVE_ARGS + ["--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(LIVE_ARGS + ["--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag in ("--enable-ocr", "--enable-extraction"):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_db_minio_rag_blocked(self) -> None:
        for flag in ("--write-db", "--write-minio", "--run-rag"):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_verified_production_ready_blocked(self) -> None:
        for flag in ("--mark-verified", "--mark-production-ready"):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_live_path_does_not_execute_real_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            with mock.patch(
                "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
                side_effect=_mock_execute_live_case,
            ):
                rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        get_mock.assert_not_called()
        post_mock.assert_not_called()

    def test_dry_run_still_50_of_50_and_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(PHASE3_DRYRUN_ARGS)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("planned_ok=50", result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_live_report_paths_are_isolated(self) -> None:
        self.assertTrue(LIVE_REPORT.startswith(PHASE3_OUTPUT_ROOT))
        self.assertTrue(LIVE_SUMMARY.startswith(PHASE3_OUTPUT_ROOT))
        self.assertTrue(QUALITY_REPORT.startswith(PHASE3_OUTPUT_ROOT))
        self.assertIn("a_class_phase3_50_company_expansion_report.csv", LIVE_REPORT)
        self.assertNotIn("metadata_expansion", LIVE_REPORT)
        self.assertNotIn("metadata_retry", LIVE_REPORT)

    def test_mock_50_of_50_acceptable_produces_pass_with_caveat(self) -> None:
        rows = [
            _gate_row(f"A3M{i:03d}", "found") for i in range(1, 51)
        ]
        stats = tiny_live.LiveStats()
        gate = runner.compute_phase3_execution_gate(stats, rows, [], 50)
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_40_of_50_acceptable_produces_pass_with_caveat(self) -> None:
        rows: List[Dict[str, str]] = []
        for i in range(1, 51):
            status = "found" if i <= 40 else "network_error"
            rows.append(_gate_row(f"A3M{i:03d}", status))
        stats = tiny_live.LiveStats()
        gate = runner.compute_phase3_execution_gate(stats, rows, [], 50)
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_39_of_50_acceptable_produces_fail_review_required(self) -> None:
        rows: List[Dict[str, str]] = []
        for i in range(1, 51):
            status = "found" if i <= 39 else "network_error"
            rows.append(_gate_row(f"A3M{i:03d}", status))
        stats = tiny_live.LiveStats()
        gate = runner.compute_phase3_execution_gate(stats, rows, [], 50)
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")

    def test_execution_gate_never_uses_pass(self) -> None:
        rows = [_gate_row(f"A3M{i:03d}", "found") for i in range(1, 51)]
        stats = tiny_live.LiveStats()
        gate = runner.compute_phase3_execution_gate(stats, rows, [], 50)
        self.assertNotEqual(gate, "PASS")
        self.assertEqual(runner.PHASE3_EXECUTION_GATE_PASS, "PASS_WITH_CAVEAT")


if __name__ == "__main__":
    unittest.main()
