"""
D-class tiny live validation runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_d_class_tiny_live_validation_runner.py
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
UNIVERSE = runner.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
DRYRUN_REPORT = runner.DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.DRYRUN_SUMMARY_MD


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestTinyLiveValidationRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            with mock.patch("urllib.request.urlopen") as urlopen_mock:
                result = _run(["--dry-run"])
                self.assertEqual(result.returncode, 0, msg=result.stderr)
                get_mock.assert_not_called()
                post_mock.assert_not_called()
                urlopen_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_live_requires_approve_d_class_tiny_live_validation(self) -> None:
        result = _run(["--live"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TINY_LIVE_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected(self) -> None:
        for flag in (
            "--approve-b-class-tiny-live-validation",
            "--approve-full-harvest",
            "--approve-a-class-tiny-live-validation",
        ):
            result = _run(["--live", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(runner.WRONG_APPROVAL_FLAG, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_universe_size_must_equal_seven(self) -> None:
        cases = runner.load_universe(UNIVERSE)
        self.assertEqual(len(cases), 7)
        issues = runner.validate_universe_batch(cases[:6])
        self.assertTrue(any(runner.UNIVERSE_SIZE_MISMATCH in i for i in issues))

    def test_only_dlc001_dlc007_allowed(self) -> None:
        bad = runner.UniverseCase(
            case_id="DC001",
            company_code="000001",
            company_name="测试",
            component="margin_trading",
            market="szse_main",
            risk_level="low",
            expected_behavior="captured_normal",
            reason="",
        )
        issues = runner.validate_universe_batch([bad])
        self.assertTrue(any(runner.NON_DLC_CASE in i for i in issues))

    def test_all_seven_components_covered(self) -> None:
        cases = runner.load_universe(UNIVERSE)
        components = {c.component for c in cases}
        self.assertEqual(components, runner.ALLOWED_COMPONENTS)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, token in (
            ("--db-write", runner.DB_WRITE_BLOCKED),
            ("--minio-write", runner.MINIO_WRITE_BLOCKED),
            ("--rag-run", runner.RAG_RUN_BLOCKED),
        ):
            result = _run(["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, token in (
            ("--mark-verified", runner.VERIFIED_BLOCKED),
            ("--production-ready", runner.PRODUCTION_READY_BLOCKED),
        ):
            result = _run(["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_dry_run_report_generated(self) -> None:
        result = _run(["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT), msg=DRYRUN_REPORT)
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY), msg=DRYRUN_SUMMARY)
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 7)
        self.assertEqual(set(rows[0].keys()), set(runner.DRYRUN_REPORT_COLUMNS))
        for row in rows:
            self.assertEqual(row["db_write"], "no")
            self.assertEqual(row["minio_write"], "no")
            self.assertEqual(row["rag_run"], "no")
            self.assertEqual(row["cninfo_call_planned"], "no")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
