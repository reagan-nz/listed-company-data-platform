"""
B-class Era D fuller next-slice2 runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_b_class_erad_fuller_next_slice2_runner.py
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
UNIVERSE = runner.DEFAULT_ERAD_FULLER_SLICE2_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_ERAD_FULLER_SLICE2_OUTPUT_ROOT
SCALE_200_OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
SLICE1_OUTPUT_ROOT = runner.DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
PHASE3_RETRY_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_OUTPUT_ROOT
PHASE3_RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT
A_CLASS_ROOT = runner.A_CLASS_VALIDATION_ROOT
C_CLASS_HARVEST_ROOT = runner.C_CLASS_HARVEST_ROOT
D_CLASS_ROOT = runner.D_CLASS_VALIDATION_ROOT
MOCK_TEST_PARENT = runner.ERAD_FULLER_SLICE2_MOCK_TEST_PARENT

SLICE2_BASE_ARGS = [
    "--erad-b-fuller-slice2",
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


def _sample_slice2_row(case_id: str = "BD2E501", company_code: str = "000166") -> dict:
    return {
        "case_id": case_id,
        "company_code": company_code,
        "cohort": "fuller_next_slice2",
        "prior_in_scale_200_or_slice1": "none",
        "include_reason": "fuller_next_slice2_staged_beyond_500;market_szse_main;zero_prior_b_phase_overlap",
    }


class TestEradFullerSlice2Runner(unittest.TestCase):
    def test_dry_run_300_planned_ok_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(SLICE2_BASE_ARGS + ["--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_ok=300", result.stdout)

    def test_universe_must_equal_300(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(
                tmp,
                fieldnames=list(_sample_slice2_row().keys()),
            )
            writer.writeheader()
            writer.writerow(_sample_slice2_row())
            tmp_path = tmp.name
        try:
            cases = runner.load_erad_fuller_slice2_universe(tmp_path)
            ok, err = runner.validate_erad_fuller_slice2_universe_size(cases)
            self.assertFalse(ok)
            self.assertIn(runner.ERAD_FULLER_SLICE2_UNIVERSE_SIZE_VIOLATION, err)
        finally:
            os.unlink(tmp_path)

    def test_only_bd2e501_through_bd2e800_allowed(self) -> None:
        cases = runner.load_erad_fuller_slice2_universe(UNIVERSE)
        case_ids = {c.case_id for c in cases}
        self.assertEqual(case_ids, runner.ALLOWED_ERAD_FULLER_SLICE2_CASE_IDS)
        bad = runner.EraDFullerSlice2UniverseCase(
            case_id="BD2E090",
            company_code="000807",
            company_name="",
            market="SZSE主板",
            announcement_type="general_announcement",
            target_endpoint=["EP001", "EP005"],
            cohort="fuller_next_slice2",
            prior_in_scale_200_or_slice1="none",
            include_reason="x",
            erad_include="yes",
        )
        issues = runner.validate_erad_fuller_slice2_case(bad)
        self.assertTrue(
            any(runner.ERAD_FULLER_SLICE2_PRIOR_CASE_FORBIDDEN in i for i in issues)
            or any(runner.ERAD_FULLER_SLICE2_CASE_ID_NOT_ALLOWED in i for i in issues)
        )

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(SLICE2_BASE_ARGS + ["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.ERAD_FULLER_SLICE2_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_scale_200_and_slice1_roots_write_blocked(self) -> None:
        for bad_root, err in (
            (SCALE_200_OUTPUT_ROOT, runner.ERAD_FULLER_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
            (SLICE1_OUTPUT_ROOT, runner.ERAD_FULLER_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        ):
            ok, root_err = runner.validate_erad_fuller_slice2_output_root(bad_root)
            self.assertFalse(ok, msg=bad_root)
            self.assertEqual(root_err, err, msg=bad_root)

    def test_phase3_production_roots_write_blocked(self) -> None:
        for bad_root, err in (
            (PHASE3_OUTPUT_ROOT, runner.PHASE3_EXPANSION_BASELINE_WRITE_FORBIDDEN),
            (PHASE3_RETRY_OUTPUT_ROOT, runner.PHASE3_FAILED_RETRY_BASELINE_WRITE_FORBIDDEN),
            (PHASE3_RETRY_V2_OUTPUT_ROOT, runner.PHASE3_RETRY_V2_OUTPUT_ROOT_VIOLATION),
        ):
            ok, root_err = runner.validate_erad_fuller_slice2_output_root(bad_root)
            self.assertFalse(ok, msg=bad_root)
            self.assertEqual(root_err, err, msg=bad_root)

    def test_acd_roots_write_blocked(self) -> None:
        for bad_root, err in (
            (A_CLASS_ROOT, runner.ERAD_A_CLASS_ROOT_WRITE_FORBIDDEN),
            (C_CLASS_HARVEST_ROOT, runner.ERAD_C_CLASS_HARVEST_ROOT_WRITE_FORBIDDEN),
            (D_CLASS_ROOT, runner.ERAD_D_CLASS_ROOT_WRITE_FORBIDDEN),
        ):
            ok, root_err = runner.validate_erad_fuller_slice2_output_root(bad_root)
            self.assertFalse(ok, msg=bad_root)
            self.assertEqual(root_err, err, msg=bad_root)

    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.post") as post_mock:
            result = _run(SLICE2_BASE_ARGS + ["--live"])
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FULLER_SLICE2_APPROVAL_REQUIRED, result.stderr)

    def test_live_with_approval_wired_not_stub(self) -> None:
        os.makedirs(runner.ERAD_FULLER_SLICE2_MOCK_LIVE_TEST_PARENT, exist_ok=True)
        tmp_root = tempfile.mkdtemp(
            prefix="run_", dir=runner.ERAD_FULLER_SLICE2_MOCK_LIVE_TEST_PARENT
        )
        try:
            with mock.patch(
                "run_cninfo_b_class_tiny_live_validation.execute_live_case"
            ) as mock_exec:
                mock_exec.return_value = {
                    "case_id": "BD2E501",
                    "company_code": "000166",
                    "retrieval_status": "found",
                    "quality_status": "pass",
                    "lineage_status": "discovered",
                    "announcement_id": "ann-001",
                    "announcement_title": "测试",
                    "announcement_time": "2024-01-01 00:00:00",
                    "pdf_url": "http://example.com/a.pdf",
                    "adjunct_url": "",
                    "endpoint_id": "EP004",
                    "_case_cninfo_requests": 2,
                    "notes": "mock",
                }
                with mock.patch("requests.post") as post_mock:
                    rc = runner.main(
                        [
                            "--erad-b-fuller-slice2",
                            "--live",
                            "--universe-csv",
                            UNIVERSE,
                            "--output-root",
                            tmp_root,
                            "--approve-b-class-erad-fuller-slice2",
                            "--case-range",
                            "BD2E501:BD2E501",
                        ]
                    )
                    post_mock.assert_not_called()
            self.assertEqual(rc, 0)
            self.assertGreater(mock_exec.call_count, 0)
        finally:
            runner.safe_cleanup_erad_test_output_root(tmp_root)

    def test_live_path_functions_exist(self) -> None:
        self.assertTrue(callable(runner.process_erad_fuller_slice2_live))
        self.assertTrue(callable(runner.write_live_erad_fuller_slice2_reports))
        self.assertTrue(callable(runner.compute_erad_fuller_slice2_execution_gate))

    def test_wrong_approval_flag_rejected(self) -> None:
        wrong_flags = (
            "--approve-b-class-erad-scale-200",
            "--approve-b-class-erad-scale-500-slice1",
            "--approve-b-class-phase3-100-expansion",
        )
        for flag in wrong_flags:
            with mock.patch("requests.post") as post_mock:
                result = _run(
                    SLICE2_BASE_ARGS
                    + ["--live", "--approve-b-class-erad-fuller-slice2", flag]
                )
                post_mock.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_request_cap_720_enforced(self) -> None:
        ok, _ = runner.enforce_erad_fuller_slice2_request_cap(600)
        self.assertTrue(ok)
        ok, err = runner.enforce_erad_fuller_slice2_request_cap(721)
        self.assertFalse(ok)
        self.assertIn(runner.ERAD_FULLER_SLICE2_REQUEST_CAP_EXCEEDED, err)
        cases = runner.load_erad_fuller_slice2_universe(UNIVERSE)
        included = [c for c in cases if c.erad_include == "yes"]
        with tempfile.TemporaryDirectory() as tmp:
            output_paths = runner.ensure_output_layout(os.path.join(tmp, "slice2_mock"))
            rows, issues = runner.process_erad_fuller_slice2_dry_run(included, output_paths)
        total = sum(int(r.get("planned_request_count", "0")) for r in rows)
        self.assertLessEqual(total, runner.MAX_ERAD_FULLER_SLICE2_PLANNED_REQUESTS)
        gate = runner.compute_erad_fuller_slice2_runner_gate(issues, len(included), total)
        self.assertEqual(gate, "READY_FOR_APPROVAL")

    def test_prior_overlap_zero_on_draft_universe(self) -> None:
        cases = runner.load_erad_fuller_slice2_universe(UNIVERSE)
        for case in cases:
            self.assertEqual(case.prior_in_scale_200_or_slice1, "none")
            overlap_issues = runner.validate_erad_fuller_slice2_case(case)
            self.assertNotIn(runner.ERAD_FULLER_SLICE2_PRIOR_COMPANY_OVERLAP, overlap_issues)

    def test_case_range_session_split(self) -> None:
        cases = runner.load_erad_fuller_slice2_universe(UNIVERSE)
        subset = runner.filter_erad_fuller_slice2_cases_by_range(cases, "BD2E501:BD2E650")
        self.assertEqual(len(subset), 150)
        self.assertEqual(subset[0].case_id, "BD2E501")
        self.assertEqual(subset[-1].case_id, "BD2E650")

    def test_pdf_and_verified_blocked(self) -> None:
        for extra, err in (
            (["--download-pdf"], runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
            (["--mark-verified"], runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(SLICE2_BASE_ARGS + ["--dry-run"] + extra)
            self.assertNotEqual(result.returncode, 0, msg=extra)
            self.assertIn(err, result.stderr)

    def test_cleanup_does_not_delete_production_roots(self) -> None:
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(PHASE3_OUTPUT_ROOT)
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(SCALE_200_OUTPUT_ROOT)
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(SLICE1_OUTPUT_ROOT)
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(OUTPUT_ROOT)
        os.makedirs(MOCK_TEST_PARENT, exist_ok=True)
        tmp_root = tempfile.mkdtemp(prefix="run_", dir=MOCK_TEST_PARENT)
        marker = os.path.join(tmp_root, "marker.txt")
        with open(marker, "w", encoding="utf-8") as f:
            f.write("ok")
        runner.safe_cleanup_erad_test_output_root(tmp_root)
        self.assertFalse(os.path.exists(marker))


if __name__ == "__main__":
    unittest.main()
