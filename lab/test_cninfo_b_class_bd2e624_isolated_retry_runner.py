"""
BD2E624 isolated retry runner 测试（无 CNINFO · mock live only）。

运行：
    python lab/test_cninfo_b_class_bd2e624_isolated_retry_runner.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_b_class_phase25_expansion_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_b_class_phase25_expansion_validation.py")
UNIVERSE = runner.DEFAULT_BD2E624_ISOLATED_RETRY_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_BD2E624_ISOLATED_RETRY_OUTPUT_ROOT
SLICE2_MAIN_ROOT = runner.DEFAULT_ERAD_FULLER_SLICE2_OUTPUT_ROOT
MOCK_TEST_PARENT = runner.BD2E624_ISOLATED_RETRY_MOCK_TEST_PARENT

DRYRUN_ARGS = [
    "--erad-b-fuller-slice2",
    "--universe-csv",
    UNIVERSE,
    "--output-root",
    OUTPUT_ROOT,
    "--case-range",
    runner.BD2E624_ISOLATED_RETRY_CASE_RANGE,
    "--dry-run",
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
        "announcement_id": "ann-bd2e624",
        "announcement_title": "测试",
        "announcement_time": "2024-01-01 00:00:00",
        "pdf_url": "http://example.com/a.pdf",
        "adjunct_url": "",
        "endpoint_id": "EP005",
        "_case_cninfo_requests": 2,
        "notes": "mock",
    }


class TestBd2e624IsolatedRetryRunner(unittest.TestCase):
    def test_dry_run_1_planned_ok_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(DRYRUN_ARGS)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("planned_ok=1", result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_request_count_total=2", result.stdout)

    def test_isolated_universe_csv_required(self) -> None:
        ok, err = runner.validate_bd2e624_isolated_retry_universe_csv_path(
            runner.DEFAULT_ERAD_FULLER_SLICE2_UNIVERSE_CSV
        )
        self.assertFalse(ok)
        self.assertEqual(err, runner.BD2E624_ISOLATED_RETRY_UNIVERSE_CSV_REQUIRED)

    def test_slice2_main_root_write_blocked(self) -> None:
        ok, err = runner.validate_bd2e624_isolated_retry_output_root(SLICE2_MAIN_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.BD2E624_SLICE2_MAIN_ROOT_WRITE_FORBIDDEN)

    def test_case_range_required(self) -> None:
        result = _run(
            [
                "--erad-b-fuller-slice2",
                "--universe-csv",
                UNIVERSE,
                "--output-root",
                OUTPUT_ROOT,
                "--dry-run",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.BD2E624_ISOLATED_RETRY_CASE_RANGE_REQUIRED, result.stderr)

    def test_live_without_approval_rejected(self) -> None:
        with mock.patch("requests.post") as post_mock:
            result = _run(DRYRUN_ARGS[:-1] + ["--live"])
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.BD2E624_ISOLATED_RETRY_APPROVAL_REQUIRED, result.stderr)

    def test_live_mock_path_cninfo_cap(self) -> None:
        os.makedirs(runner.BD2E624_ISOLATED_RETRY_MOCK_LIVE_TEST_PARENT, exist_ok=True)
        tmp_root = tempfile.mkdtemp(
            prefix="run_", dir=runner.BD2E624_ISOLATED_RETRY_MOCK_LIVE_TEST_PARENT
        )
        try:
            with mock.patch(
                "run_cninfo_b_class_tiny_live_validation.execute_live_case",
                side_effect=_mock_execute_live_case,
            ):
                with mock.patch("requests.post") as post_mock:
                    rc = runner.main(
                        [
                            "--erad-b-bd2e624-isolated-retry",
                            "--live",
                            "--universe-csv",
                            UNIVERSE,
                            "--output-root",
                            tmp_root,
                            "--case-range",
                            runner.BD2E624_ISOLATED_RETRY_CASE_RANGE,
                            "--approve-b-class-bd2e624-isolated-retry",
                        ]
                    )
                    post_mock.assert_not_called()
            self.assertEqual(rc, 0)
            report = os.path.join(
                tmp_root,
                "reports",
                "b_class_erad_fuller_next_slice2_bd2e624_retry_report.csv",
            )
            self.assertTrue(os.path.isfile(report))
        finally:
            runner.safe_cleanup_erad_test_output_root(tmp_root)

    def test_request_cap_2_enforced(self) -> None:
        ok, _ = runner.enforce_bd2e624_isolated_retry_request_cap(2)
        self.assertTrue(ok)
        ok, err = runner.enforce_bd2e624_isolated_retry_request_cap(3)
        self.assertFalse(ok)
        self.assertIn(runner.BD2E624_ISOLATED_RETRY_REQUEST_CAP_EXCEEDED, err)


if __name__ == "__main__":
    unittest.main()
