"""
A-class Era D ~200 live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_a_class_erad_scale_200_live_path.py
"""

from __future__ import annotations

import csv
import hashlib
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

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402
import run_cninfo_a_class_tiny_live_metadata_validation as tiny_live  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_metadata_expansion.py")
ERAD_UNIVERSE = runner.DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV
ERAD_OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
PHASE1_OUTPUT_ROOT = runner.PHASE1_OUTPUT_ROOT
PHASE2_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
A3M017_OUTPUT_ROOT = runner.DEFAULT_A3M017_RETRY_OUTPUT_ROOT
RETRY_V1_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_RETRY_V2_OUTPUT_ROOT
RETRY_V3_OUTPUT_ROOT = runner.DEFAULT_RETRY_V3_OUTPUT_ROOT
PRECHECK_OUTPUT_ROOT = runner.PRECHECK_OUTPUT_ROOT
HARVEST_ROOT = runner.C_CLASS_HARVEST_ROOT
B_CLASS_PREFIX = runner.B_CLASS_VALIDATION_PREFIX
C_CLASS_PREFIX = runner.C_CLASS_VALIDATION_PREFIX
D_CLASS_PREFIX = runner.D_CLASS_VALIDATION_PREFIX

ERAD_DRYRUN_ARGS = [
    "--erad-a-scale-200",
    "--dry-run",
    "--universe-csv",
    ERAD_UNIVERSE,
    "--output-root",
    ERAD_OUTPUT_ROOT,
]

MOCK_OUTPUT_ROOT = os.path.join(ERAD_OUTPUT_ROOT, "_mock_live_path_test")
LIVE_REPORT = os.path.join(MOCK_OUTPUT_ROOT, "reports", "a_class_erad_scale_200_live_report.csv")
LIVE_SUMMARY = os.path.join(MOCK_OUTPUT_ROOT, "reports", "a_class_erad_scale_200_live_summary.md")
QUALITY_REPORT = os.path.join(
    MOCK_OUTPUT_ROOT, "reports", "a_class_erad_scale_200_live_quality_report.csv"
)

LIVE_ARGS = [
    "--erad-a-scale-200",
    "--live",
    "--universe-csv",
    ERAD_UNIVERSE,
    "--output-root",
    MOCK_OUTPUT_ROOT,
    "--approve-a-class-erad-scale-200",
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
    cohort: str = "new_erad",
) -> Dict[str, str]:
    return {
        "case_id": case_id,
        "retrieval_status": retrieval_status,
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "cohort": cohort,
        "phase3_source_case_id": "",
        "notes": "mock",
    }


def _cleanup_mock_live_artifacts() -> None:
    if os.path.isdir(MOCK_OUTPUT_ROOT):
        shutil.rmtree(MOCK_OUTPUT_ROOT, ignore_errors=True)


class TestAClassEradScale200LivePath(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _cleanup_mock_live_artifacts()
        os.makedirs(MOCK_OUTPUT_ROOT, exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        _cleanup_mock_live_artifacts()

    def test_live_without_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--erad-a-scale-200",
                    "--live",
                    "--universe-csv",
                    ERAD_UNIVERSE,
                    "--output-root",
                    MOCK_OUTPUT_ROOT,
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_SCALE_200_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        wrong_flags = (
            "--approve-a-class-phase2-metadata-expansion",
            "--approve-a-class-phase2-failed-retry",
            "--approve-a-class-phase2-network-recovery-retry-v2",
            "--approve-a-class-phase2-retry-v3",
            "--approve-a-class-phase3-50-company-expansion",
            "--approve-a-class-tiny-live-metadata",
            "--approve-phase1-tiny-live-metadata",
        )
        for flag in wrong_flags:
            with mock.patch(
                "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
            ) as mock_exec:
                result = _run(
                    [
                        "--erad-a-scale-200",
                        "--live",
                        "--universe-csv",
                        ERAD_UNIVERSE,
                        "--output-root",
                        MOCK_OUTPUT_ROOT,
                        flag,
                    ]
                )
                mock_exec.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(runner.ERAD_SCALE_200_WRONG_APPROVAL, result.stderr)

    def test_live_path_function_exists_and_wired(self) -> None:
        self.assertTrue(callable(runner.process_erad_scale_200_live))
        self.assertTrue(callable(runner.compute_erad_scale_200_execution_gate))
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ) as mock_exec:
            rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        self.assertEqual(mock_exec.call_count, runner.ERAD_SCALE_200_REQUIRED_UNIVERSE_SIZE)
        self.assertTrue(os.path.isfile(LIVE_REPORT))
        self.assertTrue(os.path.isfile(LIVE_SUMMARY))

    def test_universe_size_must_equal_200(self) -> None:
        result = _run(LIVE_ARGS + ["--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_SCALE_200_UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        ok, err = runner.validate_erad_scale_200_output_root(MOCK_OUTPUT_ROOT)
        self.assertTrue(ok, msg=err)

    def test_phase1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--live",
                "--universe-csv",
                ERAD_UNIVERSE,
                "--output-root",
                PHASE1_OUTPUT_ROOT,
                "--approve-a-class-erad-scale-200",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE1_BASELINE_WRITE_FORBIDDEN, result.stderr)

    def test_phase2_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--live",
                "--universe-csv",
                ERAD_UNIVERSE,
                "--output-root",
                PHASE2_OUTPUT_ROOT,
                "--approve-a-class-erad-scale-200",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE2_EXPANSION_WRITE_FORBIDDEN, result.stderr)

    def test_phase3_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--live",
                "--universe-csv",
                ERAD_UNIVERSE,
                "--output-root",
                PHASE3_OUTPUT_ROOT,
                "--approve-a-class-erad-scale-200",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_a3m017_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--live",
                "--universe-csv",
                ERAD_UNIVERSE,
                "--output-root",
                A3M017_OUTPUT_ROOT,
                "--approve-a-class-erad-scale-200",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("a3m017_isolated_retry_output_root_forbidden", result.stderr)

    def test_harvest_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--live",
                "--universe-csv",
                ERAD_UNIVERSE,
                "--output-root",
                HARVEST_ROOT,
                "--approve-a-class-erad-scale-200",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("c_class_harvest_output_root_forbidden", result.stderr)

    def test_b_class_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--live",
                "--universe-csv",
                ERAD_UNIVERSE,
                "--output-root",
                os.path.join(B_CLASS_PREFIX, "phase3_100"),
                "--approve-a-class-erad-scale-200",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("b_class_validation_output_root_forbidden", result.stderr)

    def test_c_class_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--live",
                "--universe-csv",
                ERAD_UNIVERSE,
                "--output-root",
                os.path.join(C_CLASS_PREFIX, "phase35_expanded_snapshot"),
                "--approve-a-class-erad-scale-200",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("c_class_validation_output_root_forbidden", result.stderr)

    def test_d_class_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--live",
                "--universe-csv",
                ERAD_UNIVERSE,
                "--output-root",
                os.path.join(D_CLASS_PREFIX, "disclosure_schedule_first_slice"),
                "--approve-a-class-erad-scale-200",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("d_class_validation_output_root_forbidden", result.stderr)

    def test_request_cap_480_enforced(self) -> None:
        ok, err = runner.validate_erad_scale_200_request_cap(200)
        self.assertTrue(ok, msg=err)
        ok2, err2 = runner.validate_erad_scale_200_request_cap(241)
        self.assertFalse(ok2)
        self.assertIn(runner.ERAD_SCALE_200_REQUEST_CAP_EXCEEDED, err2)

    def test_retained_cohort_does_not_rewrite_phase3_or_a3m017_roots(self) -> None:
        os.makedirs(PHASE3_OUTPUT_ROOT, exist_ok=True)
        os.makedirs(A3M017_OUTPUT_ROOT, exist_ok=True)
        phase3_marker = os.path.join(PHASE3_OUTPUT_ROOT, "_erad_live_test_guard.txt")
        a3m017_marker = os.path.join(A3M017_OUTPUT_ROOT, "_erad_live_test_guard.txt")
        for path, content in (
            (phase3_marker, "phase3_guard"),
            (a3m017_marker, "a3m017_guard"),
        ):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        phase3_before = _file_sha256(phase3_marker)
        a3m017_before = _file_sha256(a3m017_marker)
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ):
            rc = runner.main(LIVE_ARGS)
        self.assertEqual(rc, 0)
        self.assertEqual(phase3_before, _file_sha256(phase3_marker))
        self.assertEqual(a3m017_before, _file_sha256(a3m017_marker))
        with open(LIVE_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        retained = [r for r in rows if r.get("cohort") == "retained_phase3"]
        self.assertEqual(len(retained), 50)
        for row in retained:
            self.assertIn("retained_phase3_lineage_only_no_phase3_root_write", row["notes"])
        for path in (phase3_marker, a3m017_marker):
            if os.path.isfile(path):
                os.remove(path)

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

    def test_dry_run_still_200_of_200_and_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(ERAD_DRYRUN_ARGS)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("planned_ok=200", result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_cleanup_does_not_delete_production_markers(self) -> None:
        marker_dir = os.path.join(ERAD_OUTPUT_ROOT, "_production_guard")
        os.makedirs(marker_dir, exist_ok=True)
        marker_path = os.path.join(marker_dir, "keep.txt")
        with open(marker_path, "w", encoding="utf-8") as f:
            f.write("guard")
        before = _file_sha256(marker_path)
        result = _run(ERAD_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(marker_path))
        self.assertEqual(before, _file_sha256(marker_path))

    def test_mock_180_of_200_acceptable_produces_pass_with_caveat(self) -> None:
        rows: List[Dict[str, str]] = []
        for i in range(1, 201):
            status = "found" if i <= 180 else "network_error"
            cohort = "retained_phase3" if i <= 50 else "new_erad"
            rows.append(_gate_row(f"AD2E{i:03d}", status, cohort=cohort))
        stats = tiny_live.LiveStats()
        gate = runner.compute_erad_scale_200_execution_gate(stats, rows, [], 200)
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_179_of_200_acceptable_produces_fail_review_required(self) -> None:
        rows: List[Dict[str, str]] = []
        for i in range(1, 201):
            status = "found" if i <= 179 else "network_error"
            rows.append(_gate_row(f"AD2E{i:03d}", status))
        stats = tiny_live.LiveStats()
        gate = runner.compute_erad_scale_200_execution_gate(stats, rows, [], 200)
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")

    def test_execution_gate_never_uses_pass(self) -> None:
        rows = [_gate_row(f"AD2E{i:03d}", "found") for i in range(1, 201)]
        stats = tiny_live.LiveStats()
        gate = runner.compute_erad_scale_200_execution_gate(stats, rows, [], 200)
        self.assertNotEqual(gate, "PASS")
        self.assertEqual(runner.ERAD_SCALE_200_EXECUTION_GATE_PASS, "PASS_WITH_CAVEAT")


if __name__ == "__main__":
    unittest.main()
