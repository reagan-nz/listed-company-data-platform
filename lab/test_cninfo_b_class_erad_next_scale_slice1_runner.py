"""
B-class Era D next-scale slice1 runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_b_class_erad_next_scale_slice1_runner.py
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
UNIVERSE = runner.DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT
SCALE_200_OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
PHASE3_RETRY_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_OUTPUT_ROOT
PHASE3_RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT
A_CLASS_ROOT = runner.A_CLASS_VALIDATION_ROOT
C_CLASS_HARVEST_ROOT = runner.C_CLASS_HARVEST_ROOT
D_CLASS_ROOT = runner.D_CLASS_VALIDATION_ROOT
MOCK_TEST_PARENT = runner.ERAD_NEXT_SCALE_SLICE1_MOCK_TEST_PARENT

SLICE1_BASE_ARGS = [
    "--erad-b-scale-500-slice1",
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


def _sample_slice1_row(case_id: str = "BD2E201", company_code: str = "000043") -> dict:
    return {
        "case_id": case_id,
        "company_code": company_code,
        "cohort": "next_scale_slice1",
        "prior_overlap": "none",
        "include_reason": "next_scale_slice1_staged_200_to_500;market_szse;zero_prior_b_phase_overlap",
    }


class TestEradNextScaleSlice1Runner(unittest.TestCase):
    def test_dry_run_300_planned_ok_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(SLICE1_BASE_ARGS + ["--dry-run"])
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
                fieldnames=list(_sample_slice1_row().keys()),
            )
            writer.writeheader()
            writer.writerow(_sample_slice1_row())
            tmp_path = tmp.name
        try:
            cases = runner.load_erad_next_scale_slice1_universe(tmp_path)
            ok, err = runner.validate_erad_next_scale_slice1_universe_size(cases)
            self.assertFalse(ok)
            self.assertIn(runner.ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE_VIOLATION, err)
        finally:
            os.unlink(tmp_path)

    def test_only_bd2e201_through_bd2e500_allowed(self) -> None:
        cases = runner.load_erad_next_scale_slice1_universe(UNIVERSE)
        case_ids = {c.case_id for c in cases}
        self.assertEqual(case_ids, runner.ALLOWED_ERAD_NEXT_SCALE_SLICE1_CASE_IDS)
        bad = runner.EraDNextScaleSlice1UniverseCase(
            case_id="BD2E090",
            company_code="000807",
            company_name="",
            market="SZSE主板",
            announcement_type="general_announcement",
            target_endpoint=["EP001", "EP005"],
            cohort="next_scale_slice1",
            prior_overlap="none",
            include_reason="x",
            erad_include="yes",
        )
        issues = runner.validate_erad_next_scale_slice1_case(bad)
        self.assertTrue(
            any(runner.ERAD_SLICE1_SCALE_200_CASE_FORBIDDEN in i for i in issues)
            or any(runner.ERAD_SLICE1_CASE_ID_NOT_ALLOWED in i for i in issues)
        )

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(SLICE1_BASE_ARGS + ["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_scale_200_root_write_blocked(self) -> None:
        ok, root_err = runner.validate_erad_next_scale_slice1_output_root(SCALE_200_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(root_err, runner.ERAD_SLICE1_SCALE_200_ROOT_WRITE_FORBIDDEN)

    def test_phase3_production_roots_write_blocked(self) -> None:
        for bad_root, err in (
            (PHASE3_OUTPUT_ROOT, runner.PHASE3_EXPANSION_BASELINE_WRITE_FORBIDDEN),
            (PHASE3_RETRY_OUTPUT_ROOT, runner.PHASE3_FAILED_RETRY_BASELINE_WRITE_FORBIDDEN),
            (PHASE3_RETRY_V2_OUTPUT_ROOT, runner.PHASE3_RETRY_V2_OUTPUT_ROOT_VIOLATION),
        ):
            ok, root_err = runner.validate_erad_next_scale_slice1_output_root(bad_root)
            self.assertFalse(ok, msg=bad_root)
            self.assertEqual(root_err, err, msg=bad_root)

    def test_acd_roots_write_blocked(self) -> None:
        for bad_root, err in (
            (A_CLASS_ROOT, runner.ERAD_A_CLASS_ROOT_WRITE_FORBIDDEN),
            (C_CLASS_HARVEST_ROOT, runner.ERAD_C_CLASS_HARVEST_ROOT_WRITE_FORBIDDEN),
            (D_CLASS_ROOT, runner.ERAD_D_CLASS_ROOT_WRITE_FORBIDDEN),
        ):
            ok, root_err = runner.validate_erad_next_scale_slice1_output_root(bad_root)
            self.assertFalse(ok, msg=bad_root)
            self.assertEqual(root_err, err, msg=bad_root)

    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.post") as post_mock:
            result = _run(SLICE1_BASE_ARGS + ["--live"])
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_NEXT_SCALE_SLICE1_APPROVAL_REQUIRED, result.stderr)

    def test_live_path_functions_exist(self) -> None:
        self.assertTrue(hasattr(runner, "process_erad_next_scale_slice1_live"))
        self.assertTrue(callable(runner.process_erad_next_scale_slice1_live))
        self.assertTrue(hasattr(runner, "write_live_erad_next_scale_slice1_reports"))

    def test_wrong_approval_flag_rejected(self) -> None:
        wrong_flags = (
            "--approve-b-class-erad-scale-200",
            "--approve-b-class-phase3-100-expansion",
            "--approve-b-class-phase25-expansion",
        )
        for flag in wrong_flags:
            with mock.patch("requests.post") as post_mock:
                result = _run(SLICE1_BASE_ARGS + ["--live", flag])
                post_mock.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_request_cap_720_enforced(self) -> None:
        ok, _ = runner.enforce_erad_next_scale_slice1_request_cap(600)
        self.assertTrue(ok)
        ok, err = runner.enforce_erad_next_scale_slice1_request_cap(721)
        self.assertFalse(ok)
        self.assertIn(runner.ERAD_SLICE1_REQUEST_CAP_EXCEEDED, err)
        cases = runner.load_erad_next_scale_slice1_universe(UNIVERSE)
        included = [c for c in cases if c.erad_include == "yes"]
        with tempfile.TemporaryDirectory() as tmp:
            output_paths = runner.ensure_output_layout(os.path.join(tmp, "slice1_mock"))
            rows, issues = runner.process_erad_next_scale_slice1_dry_run(included, output_paths)
        total = sum(int(r.get("planned_request_count", "0")) for r in rows)
        self.assertLessEqual(total, runner.MAX_ERAD_NEXT_SCALE_SLICE1_PLANNED_REQUESTS)
        gate = runner.compute_erad_next_scale_slice1_runner_gate(issues, len(included), total)
        self.assertEqual(gate, "READY_FOR_APPROVAL")

    def test_prior_overlap_zero_on_draft_universe(self) -> None:
        cases = runner.load_erad_next_scale_slice1_universe(UNIVERSE)
        for case in cases:
            self.assertEqual(case.prior_overlap, "none")
            overlap_issues = runner.validate_erad_next_scale_slice1_case(case)
            self.assertNotIn(runner.ERAD_SLICE1_PRIOR_COMPANY_OVERLAP, overlap_issues)

    def test_pdf_and_verified_blocked(self) -> None:
        for extra, err in (
            (["--download-pdf"], runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
            (["--mark-verified"], runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(SLICE1_BASE_ARGS + ["--dry-run"] + extra)
            self.assertNotEqual(result.returncode, 0, msg=extra)
            self.assertIn(err, result.stderr)

    def test_cleanup_does_not_delete_production_roots(self) -> None:
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(PHASE3_OUTPUT_ROOT)
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(SCALE_200_OUTPUT_ROOT)
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
