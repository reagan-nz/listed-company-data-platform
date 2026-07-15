"""
A-class Era D next-scale slice2 S1 live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_a_class_erad_next_scale_slice2_live_path.py
"""

from __future__ import annotations

import csv
import json
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

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_metadata_expansion.py")
UNIVERSE = runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT
SCALE_200_OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
FAILED_RETRY_OUTPUT_ROOT = runner.DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT
SLICE1_OUTPUT_ROOT = runner.DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT
MOCK_LIVE_PARENT = runner.ERAD_NEXT_SCALE_SLICE2_S1_MOCK_LIVE_TEST_PARENT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
A3M017_OUTPUT_ROOT = runner.DEFAULT_A3M017_RETRY_OUTPUT_ROOT
DRYRUN_REPORT = os.path.join(
    OUTPUT_ROOT, "reports", "a_class_erad_next_scale_slice2_s1_dryrun_report.csv"
)

LIVE_ARGS = [
    "--erad-a-scale-500-slice2",
    "--live",
    "--universe-csv",
    UNIVERSE,
    "--output-root",
    OUTPUT_ROOT,
    "--approve-a-class-erad-scale-500-slice2",
]

DRYRUN_ARGS = [
    "--erad-a-scale-500-slice2",
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
    stats: Any,
) -> Dict[str, str]:
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


def _mock_execute_live_case_fail(
    tl_case: Any,
    stats: Any,
) -> Dict[str, str]:
    stats.cninfo_requests += 2
    stats.failure_count += 1
    return {
        "retrieval_status": "not_found",
        "quality_status": "fail",
        "lineage_status": "missing",
        "announcement_id": "",
        "announcement_title": "",
        "announcement_time": "",
        "title_match_status": "fail",
        "period_match_status": "fail",
        "pdf_url_present": "no",
        "adjunct_url_present": "no",
        "notes": "mock_fail",
    }


def _live_args_for_output_root(output_root: str, extra: List[str] | None = None) -> List[str]:
    args = [
        "--erad-a-scale-500-slice2",
        "--live",
        "--universe-csv",
        UNIVERSE,
        "--output-root",
        output_root,
        "--approve-a-class-erad-scale-500-slice2",
    ]
    if extra:
        args.extend(extra)
    return args


def _create_mock_live_output_root() -> str:
    os.makedirs(MOCK_LIVE_PARENT, exist_ok=True)
    return tempfile.mkdtemp(prefix="run_", dir=MOCK_LIVE_PARENT)


def _cleanup_mock_live_output_root(temp_root: str) -> None:
    runner.safe_cleanup_erad_a_slice2_test_output_root(temp_root)


def _count_files_under(root: str) -> int:
    if not os.path.isdir(root):
        return 0
    total = 0
    for _dirpath, _dirnames, filenames in os.walk(root):
        total += len(filenames)
    return total


class TestEradNextScaleSlice2LivePath(unittest.TestCase):
    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--erad-a-scale-500-slice2",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_NEXT_SCALE_SLICE2_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--erad-a-scale-500-slice2",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    OUTPUT_ROOT,
                    "--approve-a-class-erad-scale-500-slice1",
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL, result.stderr)

    def test_live_path_function_exists_and_wired(self) -> None:
        self.assertTrue(callable(runner.process_erad_a_next_scale_slice2_live))
        self.assertTrue(callable(runner.write_erad_next_scale_slice2_live_report))
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ):
            tmp_root = _create_mock_live_output_root()
            try:
                rc = runner.main(_live_args_for_output_root(tmp_root))
            finally:
                _cleanup_mock_live_output_root(tmp_root)
        self.assertEqual(rc, 0)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(_live_args_for_output_root(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.ERAD_NEXT_SCALE_SLICE2_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_scale_200_root_write_blocked(self) -> None:
        ok, root_err = runner.validate_erad_next_scale_slice2_output_root(SCALE_200_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(root_err, runner.ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN)

    def test_failed_retry_root_write_blocked(self) -> None:
        ok, root_err = runner.validate_erad_next_scale_slice2_output_root(
            FAILED_RETRY_OUTPUT_ROOT
        )
        self.assertFalse(ok)
        self.assertEqual(root_err, runner.ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN)

    def test_slice1_root_write_blocked(self) -> None:
        ok, root_err = runner.validate_erad_next_scale_slice2_output_root(SLICE1_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(root_err, runner.ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN)

    def test_phase3_and_a3m017_roots_write_blocked(self) -> None:
        ok, root_err = runner.validate_erad_next_scale_slice2_output_root(PHASE3_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(root_err, runner.PHASE3_OUTPUT_ROOT_VIOLATION)
        ok, root_err = runner.validate_erad_next_scale_slice2_output_root(A3M017_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn("a3m017", root_err)

    def test_request_cap_240_enforced(self) -> None:
        ok, _ = runner.enforce_erad_next_scale_slice2_request_cap(200)
        self.assertTrue(ok)
        ok, err = runner.enforce_erad_next_scale_slice2_request_cap(241)
        self.assertFalse(ok)
        self.assertIn(runner.ERAD_SLICE2_REQUEST_CAP_EXCEEDED, err)
        self.assertEqual(runner.ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP, 240)

    def test_execution_gate_pass_with_caveat_at_90_threshold(self) -> None:
        rows = []
        for i in range(100):
            rows.append(
                {
                    "case_id": f"AD2E{i + 501:03d}",
                    "retrieval_status": "found",
                    "quality_status": "pass",
                    "lineage_status": "discovered",
                    "pdf_downloaded": "0",
                    "pdf_parsed": "0",
                    "ocr_enabled": "0",
                    "extraction_enabled": "0",
                }
            )
        stats = runner.tiny_live.LiveStats()
        gate = runner.compute_erad_next_scale_slice2_execution_gate(
            rows, [], stats, 100
        )
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_execution_gate_fail_below_90(self) -> None:
        rows = []
        for i in range(100):
            if i < 89:
                rows.append(
                    {
                        "case_id": f"AD2E{i + 501:03d}",
                        "retrieval_status": "found",
                        "quality_status": "pass",
                        "lineage_status": "discovered",
                        "pdf_downloaded": "0",
                        "pdf_parsed": "0",
                        "ocr_enabled": "0",
                        "extraction_enabled": "0",
                    }
                )
            else:
                rows.append(
                    {
                        "case_id": f"AD2E{i + 501:03d}",
                        "retrieval_status": "network_error",
                        "quality_status": "fail",
                        "lineage_status": "missing",
                        "pdf_downloaded": "0",
                        "pdf_parsed": "0",
                        "ocr_enabled": "0",
                        "extraction_enabled": "0",
                    }
                )
        stats = runner.tiny_live.LiveStats()
        gate = runner.compute_erad_next_scale_slice2_execution_gate(
            rows, [], stats, 100
        )
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")

    def test_session1_case_range_threshold_45_of_50(self) -> None:
        rows = []
        for i in range(50):
            rows.append(
                {
                    "case_id": f"AD2E{i + 501:03d}",
                    "retrieval_status": "found",
                    "quality_status": "pass",
                    "lineage_status": "discovered",
                    "pdf_downloaded": "0",
                    "pdf_parsed": "0",
                    "ocr_enabled": "0",
                    "extraction_enabled": "0",
                }
            )
        stats = runner.tiny_live.LiveStats()
        gate = runner.compute_erad_next_scale_slice2_execution_gate(
            rows, [], stats, 50
        )
        self.assertEqual(gate, "PASS_WITH_CAVEAT")
        # 50 * 0.9 = 45
        rows[0]["retrieval_status"] = "network_error"
        for i in range(1, 6):
            rows[i]["retrieval_status"] = "network_error"
        # 44 acceptable → fail
        gate_fail = runner.compute_erad_next_scale_slice2_execution_gate(
            rows, [], stats, 50
        )
        self.assertEqual(gate_fail, "FAIL_REVIEW_REQUIRED")

    def test_fresh_metadata_only_no_prior_root_mutation(self) -> None:
        scale200_before = _count_files_under(
            os.path.join(SCALE_200_OUTPUT_ROOT, "raw_metadata")
        )
        slice1_before = _count_files_under(
            os.path.join(SLICE1_OUTPUT_ROOT, "raw_metadata")
        )
        phase3_before = _count_files_under(
            os.path.join(PHASE3_OUTPUT_ROOT, "raw_metadata")
        )
        tmp_root = _create_mock_live_output_root()
        try:
            with mock.patch(
                "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
                side_effect=_mock_execute_live_case,
            ):
                rc = runner.main(_live_args_for_output_root(tmp_root))
            self.assertEqual(rc, 0)
            report_path = os.path.join(
                tmp_root, "reports", "a_class_erad_next_scale_slice2_s1_live_report.csv"
            )
            with open(report_path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 100)
            self.assertTrue(all(r.get("cohort") == "next_scale_slice2" for r in rows))
            self.assertTrue(
                all(r.get("lineage_evidence_mode") == "fresh_metadata" for r in rows)
            )
            self.assertTrue(all(r["case_id"] >= "AD2E501" for r in rows))
            self.assertTrue(all(r["case_id"] <= "AD2E600" for r in rows))
            snap = os.path.join(tmp_root, "raw_metadata", "AD2E501.json")
            self.assertTrue(os.path.isfile(snap))
            with open(snap, encoding="utf-8") as f:
                payload = json.load(f)
            self.assertTrue(payload.get("ad2e001_500_lineage_reference_only"))
            self.assertFalse(payload.get("slice1_production_root_write"))
        finally:
            _cleanup_mock_live_output_root(tmp_root)
        self.assertEqual(
            scale200_before,
            _count_files_under(os.path.join(SCALE_200_OUTPUT_ROOT, "raw_metadata")),
        )
        self.assertEqual(
            slice1_before,
            _count_files_under(os.path.join(SLICE1_OUTPUT_ROOT, "raw_metadata")),
        )
        self.assertEqual(
            phase3_before,
            _count_files_under(os.path.join(PHASE3_OUTPUT_ROOT, "raw_metadata")),
        )

    def test_session_split_case_range_session1(self) -> None:
        tmp_root = _create_mock_live_output_root()
        try:
            with mock.patch(
                "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
                side_effect=_mock_execute_live_case,
            ):
                rc = runner.main(
                    _live_args_for_output_root(
                        tmp_root, ["--case-range", "AD2E501:AD2E550"]
                    )
                )
            self.assertEqual(rc, 0)
            report_path = os.path.join(
                tmp_root, "reports", "a_class_erad_next_scale_slice2_s1_live_report.csv"
            )
            with open(report_path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 50)
            self.assertEqual(rows[0]["case_id"], "AD2E501")
            self.assertEqual(rows[-1]["case_id"], "AD2E550")
        finally:
            _cleanup_mock_live_output_root(tmp_root)

    def test_live_path_does_not_call_real_cninfo(self) -> None:
        tmp_root = _create_mock_live_output_root()
        try:
            with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
                with mock.patch(
                    "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
                    side_effect=_mock_execute_live_case,
                ) as mock_exec:
                    rc = runner.main(_live_args_for_output_root(tmp_root))
            self.assertEqual(rc, 0)
            self.assertEqual(
                mock_exec.call_count, runner.REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        finally:
            _cleanup_mock_live_output_root(tmp_root)

    def test_dry_run_still_100_of_100_and_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(DRYRUN_ARGS)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_ok=100", result.stdout)
        self.assertIn("planned_request_count_total=200", result.stdout)

    def test_dryrun_report_exists_and_mock_live_isolated(self) -> None:
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        self.assertTrue(
            runner.is_allowed_erad_a_slice2_mock_test_output_root(
                os.path.join(MOCK_LIVE_PARENT, "run_example")
            )
        )
        self.assertFalse(
            runner.is_production_erad_a_next_scale_slice2_output_root(
                os.path.join(MOCK_LIVE_PARENT, "run_example")
            )
        )

    def test_pdf_and_verified_blocked(self) -> None:
        for flag, err in (
            ("--download-pdf", runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
            ("--mark-verified", runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_mock_live_failure_path_returns_fail_gate(self) -> None:
        tmp_root = _create_mock_live_output_root()
        try:
            with mock.patch(
                "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case",
                side_effect=_mock_execute_live_case_fail,
            ):
                rc = runner.main(_live_args_for_output_root(tmp_root))
            self.assertEqual(rc, 1)
            summary_path = os.path.join(
                tmp_root, "reports", "a_class_erad_next_scale_slice2_s1_live_summary.md"
            )
            self.assertTrue(os.path.isfile(summary_path))
            with open(summary_path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("FAIL_REVIEW_REQUIRED", content)
        finally:
            _cleanup_mock_live_output_root(tmp_root)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary_path = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_a_class_erad_next_scale_slice2_live_path_summary.md",
    )
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(
            "# A-class Era D Next-Scale Slice2 Live Path Summary\n\n"
            f"- tests_run: {result.testsRun}\n"
            f"- passed: {passed}\n"
            f"- failed: {len(result.failures)}\n"
            f"- errors: {len(result.errors)}\n"
            f"- CNINFO calls: **0** (mock only)\n"
            f"- gate: **a_class_erad_next_scale_slice2_s1_live_path_gate = READY_FOR_APPROVAL**\n"
            f"- approval_status: **NOT_APPROVED**（本测试文件不批准生产 live）\n"
            f"- approved_for_live: **false**（mock only）\n"
            f"- production live report at slice2 root: **mock only under _mock_live_test**\n"
            f"- acceptance threshold: **≥90/100** → PASS_WITH_CAVEAT；session1 **≥45/50**\n"
            f"- session split: `--case-range AD2E501:AD2E550` / `AD2E551:AD2E600` wired\n"
        )
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
