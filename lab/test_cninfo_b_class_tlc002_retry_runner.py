"""
TLC002 isolated retry runner 测试（无 CNINFO · 无 live retry）。

运行：
    python lab/test_cninfo_b_class_tlc002_retry_runner.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_b_class_tlc002_retry as retry_runner  # noqa: E402

BASE_DIR = retry_runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_b_class_tlc002_retry.py")
OUTPUT_ROOT = retry_runner.DEFAULT_OUTPUT_ROOT
TINY_LIVE_ROOT = retry_runner.TINY_LIVE_BASELINE_ROOT


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestTlc002RetryRunner(unittest.TestCase):
    def test_dry_run_no_network(self) -> None:
        with mock.patch("requests.post") as post_mock:
            result = _run(["--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("case_id=TLC002", result.stdout)

    def test_only_tlc002_accepted(self) -> None:
        case = retry_runner.load_tlc002_case(retry_runner.DEFAULT_UNIVERSE_CSV)
        self.assertEqual(case.case_id, "TLC002")
        self.assertEqual(case.company_code, "300009")
        issues = retry_runner.validate_tlc002_only(case)
        self.assertEqual(issues, [])

    def test_wrong_case_rejected(self) -> None:
        bad = retry_runner.tiny_live.UniverseCase(
            case_id="TLC001",
            company_code="000895",
            company_name="双汇发展",
            source_type="cninfo_periodic_report_pdf",
            endpoint_scope=["EP001", "EP004"],
            expected_fields="",
            risk_level="low",
            reason="",
        )
        issues = retry_runner.validate_tlc002_only(bad)
        self.assertTrue(any("case_id_must_be_TLC002" in i for i in issues))

    def test_live_without_approval_blocked(self) -> None:
        result = _run(["--live"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(retry_runner.TLC002_RETRY_APPROVAL_REQUIRED, result.stderr)

    def test_tiny_live_alone_rejected(self) -> None:
        result = _run(["--live", "--approve-b-class-tiny-live-validation"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(retry_runner.TINY_LIVE_ALONE_REJECTED, result.stderr)

    def test_output_isolation_rejects_foreign_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(retry_runner.OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_output_isolation_rejects_tiny_live_baseline(self) -> None:
        result = _run(["--dry-run", "--output-root", TINY_LIVE_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(retry_runner.TINY_LIVE_BASELINE_WRITE_FORBIDDEN, result.stderr)

    def test_output_isolation_accepts_retry_root(self) -> None:
        ok, err = retry_runner.validate_output_root(OUTPUT_ROOT)
        self.assertTrue(ok)
        self.assertEqual(err, "")

    def test_pdf_flags_disabled(self) -> None:
        self.assertFalse(retry_runner.PDF_DOWNLOAD_ENABLED)
        self.assertFalse(retry_runner.PDF_PARSE_ENABLED)

    def test_dry_run_writes_retry_layout(self) -> None:
        result = _run(["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        for sub in ("raw_metadata", "quality", "reports"):
            self.assertTrue(os.path.isdir(os.path.join(OUTPUT_ROOT, sub)), msg=sub)
        report = os.path.join(OUTPUT_ROOT, "reports", "tlc002_retry_report.csv")
        self.assertTrue(os.path.isfile(report))


def main() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_b_class_tlc002_retry_runner_test_summary.md",
    )
    os.makedirs(os.path.dirname(summary), exist_ok=True)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    with open(summary, "w", encoding="utf-8") as f:
        f.write(
            "# TLC002 Retry Runner Test Summary\n\n"
            f"- tests_run: {result.testsRun}\n"
            f"- passed: {passed}\n"
            f"- CNINFO calls: **0**\n"
        )
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
