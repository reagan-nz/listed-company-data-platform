"""
D-class tiny live v2 bounded probe runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_d_class_tiny_live_v2_bounded_probe_runner.py
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

import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_tiny_live_validation.py")
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_DRYRUN_REPORT = runner.V2_DRYRUN_REPORT_CSV
V2_DRYRUN_SUMMARY = runner.V2_DRYRUN_SUMMARY_MD
V2_COMPARISON_REPORT = runner.V2_COMPARISON_REPORT_CSV


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestV2BoundedProbeRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(["--dry-run", "--bounded-probe-v2"])
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_live_requires_v2_approval_flag(self) -> None:
        result = _run(["--live", "--bounded-probe-v2"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.V2_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--bounded-probe-v2",
                "--approve-d-class-tiny-live-validation",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.V2_WRONG_APPROVAL_FLAG, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(["--dry-run", "--bounded-probe-v2", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.V2_OUTPUT_ROOT_REQUIRED, result.stderr)

    def test_v1_output_root_overwrite_rejected(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--bounded-probe-v2",
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.V1_OUTPUT_ROOT_WRITE_BLOCKED, result.stderr)

    def test_only_dlc003_dlc006_probe_execution_allowed(self) -> None:
        result = _run(["--dry-run", "--bounded-probe-v2", "--cases", "DLC001"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.V2_PROBE_CASE_ONLY, result.stderr)

    def test_dlc003_request_cap_at_most_24(self) -> None:
        plan = runner.build_bounded_probe_plan_dlc003(24)
        self.assertLessEqual(len(plan), 24)
        result = _run(["--dry-run", "--bounded-probe-v2", "--dlc003-max-requests", "25"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.V2_DLC003_CAP_EXCEEDED, result.stderr)

    def test_dlc006_request_cap_at_most_20(self) -> None:
        plan = runner.build_bounded_probe_plan_dlc006(20)
        self.assertLessEqual(len(plan), 20)
        result = _run(["--dry-run", "--bounded-probe-v2", "--dlc006-max-requests", "21"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.V2_DLC006_CAP_EXCEEDED, result.stderr)

    def test_total_request_cap_at_most_44(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--bounded-probe-v2",
                "--dlc003-max-requests",
                "24",
                "--dlc006-max-requests",
                "21",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(
            runner.V2_DLC006_CAP_EXCEEDED in result.stderr
            or runner.V2_TOTAL_CAP_EXCEEDED in result.stderr,
            msg=result.stderr,
        )

    def test_no_invented_company_codes(self) -> None:
        cases = runner.load_v1_probe_cases()
        for case_id, case in cases.items():
            self.assertTrue(case.company_code)
            self.assertNotIn("CANDIDATE_REQUIRED", case.case_id)
            if case_id == "DLC003":
                self.assertEqual(case.company_code, "300009")
            if case_id == "DLC006":
                self.assertEqual(case.company_code, "000550")

    def test_db_minio_rag_blocked(self) -> None:
        for flag, token in (
            ("--db-write", runner.DB_WRITE_BLOCKED),
            ("--minio-write", runner.MINIO_WRITE_BLOCKED),
            ("--rag-run", runner.RAG_RUN_BLOCKED),
        ):
            result = _run(["--dry-run", "--bounded-probe-v2", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, token in (
            ("--mark-verified", runner.VERIFIED_BLOCKED),
            ("--production-ready", runner.PRODUCTION_READY_BLOCKED),
        ):
            result = _run(["--dry-run", "--bounded-probe-v2", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_dry_run_report_generated(self) -> None:
        result = _run(["--dry-run", "--bounded-probe-v2"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(V2_DRYRUN_REPORT), msg=V2_DRYRUN_REPORT)
        self.assertTrue(os.path.isfile(V2_DRYRUN_SUMMARY), msg=V2_DRYRUN_SUMMARY)
        with open(V2_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 0)
        self.assertEqual(set(rows[0].keys()), set(runner.V2_DRYRUN_REPORT_COLUMNS))
        for row in rows:
            self.assertIn(row["case_id"], runner.V2_PROBE_CASE_IDS)
            self.assertEqual(row["cninfo_call_planned"], "yes")
            self.assertEqual(row["dryrun_status"], "planned")

    def test_v2_comparison_report_planned(self) -> None:
        result = _run(["--dry-run", "--bounded-probe-v2"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(V2_COMPARISON_REPORT), msg=V2_COMPARISON_REPORT)
        with open(V2_COMPARISON_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 7)
        self.assertEqual(set(rows[0].keys()), set(runner.V2_COMPARISON_REPORT_COLUMNS))
        probe_rows = [r for r in rows if r["probe_extension_applied"] == "yes"]
        baseline_rows = [r for r in rows if r["probe_extension_applied"] == "no"]
        self.assertEqual(len(probe_rows), 2)
        self.assertEqual(len(baseline_rows), 5)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
