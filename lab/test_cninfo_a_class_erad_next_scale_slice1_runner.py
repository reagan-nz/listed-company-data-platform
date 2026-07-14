"""
A-class Era D next-scale slice1 runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_a_class_erad_next_scale_slice1_runner.py
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

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_metadata_expansion.py")
UNIVERSE = runner.DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT
SCALE_200_OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
FAILED_RETRY_OUTPUT_ROOT = runner.DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
A3M017_OUTPUT_ROOT = runner.DEFAULT_A3M017_RETRY_OUTPUT_ROOT

SLICE1_BASE_ARGS = [
    "--erad-a-scale-500-slice1",
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


def _sample_slice1_row(case_id: str = "AD2E201", company_code: str = "600009") -> dict:
    return {
        "case_id": case_id,
        "company_code": company_code,
        "cohort": "next_scale_slice1",
        "prior_in_scale_200": "no",
        "include_reason": "next_scale_slice1_staged_200_to_500;zero_prior_a_scale_200_overlap",
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
        self.assertIn("planned_request_count_total=600", result.stdout)

    def test_universe_must_equal_300(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(tmp, fieldnames=list(_sample_slice1_row().keys()))
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

    def test_only_ad2e201_through_ad2e500_allowed(self) -> None:
        cases = runner.load_erad_next_scale_slice1_universe(UNIVERSE)
        case_ids = {c.case_id for c in cases}
        self.assertEqual(case_ids, runner.ALLOWED_ERAD_NEXT_SCALE_SLICE1_CASE_IDS)
        bad = runner.EraDNextScaleSlice1UniverseCase(
            case_id="AD2E090",
            company_code="600807",
            company_name="",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="",
            cohort="next_scale_slice1",
            prior_in_scale_200="no",
            include_reason="x",
            erad_include="yes",
        )
        issues = runner.validate_erad_next_scale_slice1_case(bad)
        self.assertTrue(
            any(runner.ERAD_SLICE1_SCALE_200_CASE_FORBIDDEN in i for i in issues)
            or any(runner.ERAD_SLICE1_CASE_ID_NOT_ALLOWED in i for i in issues)
        )

    def test_mode_isolation_with_scale_200(self) -> None:
        result = _run(
            SLICE1_BASE_ARGS
            + ["--dry-run", "--erad-a-scale-200"]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_NEXT_SCALE_SLICE1_INCOMPATIBLE_WITH_OTHER_MODES, result.stderr)

    def test_mode_isolation_with_failed_retry(self) -> None:
        result = _run(
            SLICE1_BASE_ARGS
            + ["--dry-run", "--erad-a-scale-200-failed-retry"]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_NEXT_SCALE_SLICE1_INCOMPATIBLE_WITH_OTHER_MODES, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(SLICE1_BASE_ARGS + ["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_scale_200_root_write_blocked(self) -> None:
        ok, root_err = runner.validate_erad_next_scale_slice1_output_root(SCALE_200_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(root_err, runner.ERAD_SLICE1_SCALE_200_ROOT_WRITE_FORBIDDEN)

    def test_failed_retry_root_write_blocked(self) -> None:
        ok, root_err = runner.validate_erad_next_scale_slice1_output_root(
            FAILED_RETRY_OUTPUT_ROOT
        )
        self.assertFalse(ok)
        self.assertEqual(root_err, runner.ERAD_SLICE1_FAILED_RETRY_ROOT_WRITE_FORBIDDEN)

    def test_phase3_and_a3m017_roots_write_blocked(self) -> None:
        ok, root_err = runner.validate_erad_next_scale_slice1_output_root(PHASE3_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(root_err, runner.PHASE3_OUTPUT_ROOT_VIOLATION)
        ok, root_err = runner.validate_erad_next_scale_slice1_output_root(A3M017_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn("a3m017", root_err)

    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.post") as post_mock:
            result = _run(SLICE1_BASE_ARGS + ["--live"])
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_NEXT_SCALE_SLICE1_APPROVAL_REQUIRED, result.stderr)

    def test_live_path_function_exists(self) -> None:
        self.assertTrue(hasattr(runner, "process_erad_a_next_scale_slice1_live"))
        self.assertTrue(callable(runner.process_erad_a_next_scale_slice1_live))
        self.assertTrue(hasattr(runner, "write_erad_next_scale_slice1_live_report"))
        self.assertTrue(callable(runner.write_erad_next_scale_slice1_live_report))

    def test_wrong_approval_flag_rejected(self) -> None:
        wrong_flags = (
            "--approve-a-class-erad-scale-200",
            "--approve-a-class-erad-scale-200-failed-retry",
            "--approve-a-class-phase3-50-company-expansion",
        )
        for flag in wrong_flags:
            with mock.patch("requests.post") as post_mock:
                result = _run(SLICE1_BASE_ARGS + ["--live", flag])
                post_mock.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(runner.ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL, result.stderr)

    def test_request_cap_720_enforced(self) -> None:
        ok, _ = runner.enforce_erad_next_scale_slice1_request_cap(600)
        self.assertTrue(ok)
        ok, err = runner.enforce_erad_next_scale_slice1_request_cap(721)
        self.assertFalse(ok)
        self.assertIn(runner.ERAD_SLICE1_REQUEST_CAP_EXCEEDED, err)
        cases = runner.load_erad_next_scale_slice1_universe(UNIVERSE)
        included = [c for c in cases if c.erad_include == "yes"]
        rows, issues = runner.process_erad_next_scale_slice1_dry_run(included, OUTPUT_ROOT)
        total = sum(int(r.get("planned_request_count_case", "0")) for r in rows)
        self.assertLessEqual(total, runner.ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP)
        gate = runner.compute_erad_next_scale_slice1_runner_gate(issues, len(included), total)
        self.assertEqual(gate, "READY_FOR_APPROVAL")

    def test_overlap_lint_zero_on_draft_universe(self) -> None:
        cases = runner.load_erad_next_scale_slice1_universe(UNIVERSE)
        overlap_issues = runner.lint_erad_next_scale_slice1_overlap(cases)
        self.assertEqual(overlap_issues, [])

    def test_pdf_and_verified_blocked(self) -> None:
        for extra, err in (
            (["--download-pdf"], runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
            (["--mark-verified"], runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(SLICE1_BASE_ARGS + ["--dry-run"] + extra)
            self.assertNotEqual(result.returncode, 0, msg=extra)
            self.assertIn(err, result.stderr)

    def test_case_range_session_split_supported(self) -> None:
        start, end = runner.parse_erad_a_slice1_case_range("AD2E201:AD2E350")
        self.assertEqual(start, "AD2E201")
        self.assertEqual(end, "AD2E350")
        cases = runner.load_erad_next_scale_slice1_universe(UNIVERSE)
        included = [c for c in cases if c.erad_include == "yes"]
        subset = runner.filter_erad_a_next_scale_slice1_cases_by_range(
            included, "AD2E201:AD2E350"
        )
        self.assertEqual(len(subset), 150)


class TestEradScale200RunnerSmoke(unittest.TestCase):
    def test_scale_200_dry_run_still_works(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--dry-run",
                "--universe-csv",
                runner.DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV,
                "--output-root",
                runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
