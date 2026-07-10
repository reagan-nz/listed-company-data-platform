"""
A-class Era D ~200 isolated failed-retry live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_a_class_erad_scale_200_isolated_retry_live_path.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import shutil
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
RETRY_UNIVERSE = runner.DEFAULT_ERAD_FAILED_RETRY_UNIVERSE_CSV
RETRY_OUTPUT_ROOT = runner.DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT
ERAD_MAIN_OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
A3M017_OUTPUT_ROOT = runner.DEFAULT_A3M017_RETRY_OUTPUT_ROOT
HARVEST_ROOT = runner.C_CLASS_HARVEST_ROOT

RETRY_DRYRUN_ARGS = [
    "--erad-a-scale-200-failed-retry",
    "--dry-run",
    "--universe-csv",
    RETRY_UNIVERSE,
    "--output-root",
    RETRY_OUTPUT_ROOT,
]

MOCK_OUTPUT_ROOT = os.path.join(RETRY_OUTPUT_ROOT, "_mock_live_path_test")
LIVE_REPORT = os.path.join(
    MOCK_OUTPUT_ROOT, "reports", "a_class_erad_scale_200_failed_retry_live_report.csv"
)
LIVE_SUMMARY = os.path.join(
    MOCK_OUTPUT_ROOT, "reports", "a_class_erad_scale_200_failed_retry_live_summary.md"
)
QUALITY_REPORT = os.path.join(
    MOCK_OUTPUT_ROOT, "reports", "a_class_erad_scale_200_failed_retry_live_quality_report.csv"
)

LIVE_ARGS = [
    "--erad-a-scale-200-failed-retry",
    "--live",
    "--universe-csv",
    RETRY_UNIVERSE,
    "--output-root",
    MOCK_OUTPUT_ROOT,
    "--approve-a-class-erad-scale-200-failed-retry",
]

ALLOWED_CASE_IDS = runner.ERAD_FAILED_RETRY_ALLOWED_CASE_IDS
DEFERRED_CASE_ID = runner.ERAD_FAILED_RETRY_DEFERRED_CASE_ID


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


def _mock_execute_live_case(tl_case: Any, stats: Any) -> Dict[str, Any]:
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


def _gate_row(case_id: str, retrieval_status: str) -> Dict[str, str]:
    return {
        "case_id": case_id,
        "retrieval_status": retrieval_status,
        "quality_status": "pass",
        "lineage_status": "discovered",
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "notes": "mock",
    }


def _cleanup_mock_live_artifacts() -> None:
    if os.path.isdir(MOCK_OUTPUT_ROOT):
        shutil.rmtree(MOCK_OUTPUT_ROOT, ignore_errors=True)


class TestAClassEradScale200IsolatedRetryLivePath(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _cleanup_mock_live_artifacts()
        os.makedirs(MOCK_OUTPUT_ROOT, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        _cleanup_mock_live_artifacts()

    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--erad-a-scale-200-failed-retry",
                    "--live",
                    "--universe-csv",
                    RETRY_UNIVERSE,
                    "--output-root",
                    MOCK_OUTPUT_ROOT,
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FAILED_RETRY_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--erad-a-scale-200-failed-retry",
                    "--live",
                    "--universe-csv",
                    RETRY_UNIVERSE,
                    "--output-root",
                    MOCK_OUTPUT_ROOT,
                    "--approve-a-class-erad-scale-200",
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FAILED_RETRY_WRONG_APPROVAL, result.stderr)

    def test_live_path_function_exists_and_wired(self) -> None:
        self.assertTrue(callable(runner.process_erad_failed_retry_live))
        self.assertTrue(callable(runner.compute_erad_failed_retry_execution_gate))
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ) as mock_exec:
            rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        self.assertEqual(mock_exec.call_count, runner.ERAD_FAILED_RETRY_REQUIRED_UNIVERSE_SIZE)
        self.assertTrue(os.path.isfile(LIVE_REPORT))
        self.assertTrue(os.path.isfile(LIVE_SUMMARY))
        with open(LIVE_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 7)
        self.assertEqual({r["case_id"] for r in rows}, ALLOWED_CASE_IDS)
        self.assertNotIn(DEFERRED_CASE_ID, {r["case_id"] for r in rows})

    def test_universe_size_must_equal_7(self) -> None:
        result = _run(LIVE_ARGS + ["--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FAILED_RETRY_UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_main_erad_live_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200-failed-retry",
                "--live",
                "--universe-csv",
                RETRY_UNIVERSE,
                "--output-root",
                ERAD_MAIN_OUTPUT_ROOT,
                "--approve-a-class-erad-scale-200-failed-retry",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FAILED_RETRY_MAIN_ERAD_ROOT_FORBIDDEN, result.stderr)

    def test_phase3_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200-failed-retry",
                "--live",
                "--universe-csv",
                RETRY_UNIVERSE,
                "--output-root",
                PHASE3_OUTPUT_ROOT,
                "--approve-a-class-erad-scale-200-failed-retry",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_a3m017_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200-failed-retry",
                "--live",
                "--universe-csv",
                RETRY_UNIVERSE,
                "--output-root",
                A3M017_OUTPUT_ROOT,
                "--approve-a-class-erad-scale-200-failed-retry",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("a3m017_isolated_retry_output_root_forbidden", result.stderr)

    def test_harvest_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200-failed-retry",
                "--live",
                "--universe-csv",
                RETRY_UNIVERSE,
                "--output-root",
                HARVEST_ROOT,
                "--approve-a-class-erad-scale-200-failed-retry",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("c_class_harvest_output_root_forbidden", result.stderr)

    def test_request_cap_24_enforced(self) -> None:
        ok, err = runner.validate_erad_failed_retry_request_cap(7)
        self.assertTrue(ok, msg=err)
        ok2, err2 = runner.validate_erad_failed_retry_request_cap(13)
        self.assertFalse(ok2)
        self.assertIn(runner.ERAD_FAILED_RETRY_REQUEST_CAP_EXCEEDED, err2)

    def test_pdf_download_blocked(self) -> None:
        result = _run(LIVE_ARGS + ["--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

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

    def test_dry_run_still_7_of_7_and_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(RETRY_DRYRUN_ARGS)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("planned_ok=7", result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_main_erad_root_not_mutated_by_mock_live(self) -> None:
        marker_dir = os.path.join(ERAD_MAIN_OUTPUT_ROOT, "reports")
        os.makedirs(marker_dir, exist_ok=True)
        marker_path = os.path.join(marker_dir, "_failed_retry_live_guard.txt")
        with open(marker_path, "w", encoding="utf-8") as f:
            f.write("guard")
        before = _file_sha256(marker_path)
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ):
            rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        self.assertEqual(before, _file_sha256(marker_path))
        if os.path.isfile(marker_path):
            os.remove(marker_path)

    def test_mock_6_of_7_acceptable_produces_pass_with_caveat(self) -> None:
        rows = [_gate_row(cid, "found") for cid in sorted(ALLOWED_CASE_IDS)]
        rows[-1] = _gate_row("AD2E190", "not_found")
        stats = tiny_live.LiveStats()
        gate = runner.compute_erad_failed_retry_execution_gate(stats, rows, [], 7)
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_5_of_7_acceptable_produces_fail_review_required(self) -> None:
        rows: List[Dict[str, str]] = []
        for i, cid in enumerate(
            ["AD2E066", "AD2E088", "AD2E119", "AD2E121", "AD2E122", "AD2E185", "AD2E190"]
        ):
            status = "found" if i < 5 else "not_found"
            rows.append(_gate_row(cid, status))
        stats = tiny_live.LiveStats()
        gate = runner.compute_erad_failed_retry_execution_gate(stats, rows, [], 7)
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")

    def test_execution_gate_never_uses_pass(self) -> None:
        rows = [_gate_row(cid, "found") for cid in sorted(ALLOWED_CASE_IDS)]
        stats = tiny_live.LiveStats()
        gate = runner.compute_erad_failed_retry_execution_gate(stats, rows, [], 7)
        self.assertNotEqual(gate, "PASS")
        self.assertEqual(runner.ERAD_FAILED_RETRY_EXECUTION_GATE_PASS, "PASS_WITH_CAVEAT")


if __name__ == "__main__":
    unittest.main()
