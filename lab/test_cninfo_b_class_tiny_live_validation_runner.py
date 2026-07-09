"""
B-class tiny live validation runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_b_class_tiny_live_validation_runner.py
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

import run_cninfo_b_class_tiny_live_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_b_class_tiny_live_validation.py")
UNIVERSE = runner.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestTinyLiveValidationRunner(unittest.TestCase):
    def test_dry_run_default_no_network(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(["--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_output_isolation_rejects_foreign_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_output_isolation_accepts_default_root(self) -> None:
        ok, err = runner.validate_output_root(OUTPUT_ROOT)
        self.assertTrue(ok)
        self.assertEqual(err, "")

    def test_live_without_approval_blocked(self) -> None:
        result = _run(["--live"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TINY_LIVE_APPROVAL_REQUIRED, result.stderr)

    def test_live_with_wrong_approval_flags_blocked(self) -> None:
        for flag in (
            "--approve-full-harvest",
            "--approve-phase2-smoke-harvest",
            "--approve-phase3-batch-500-harvest",
        ):
            result = _run(["--live", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_endpoint_whitelist_blocks_ep003(self) -> None:
        case = runner.UniverseCase(
            case_id="TX",
            company_code="000001",
            company_name="测试",
            source_type="cninfo_general_announcement_pdf",
            endpoint_scope=["EP001", "EP003", "EP005"],
            expected_fields="",
            risk_level="low",
            reason="",
        )
        issues = runner.validate_universe_case(case)
        self.assertTrue(any("endpoint_blocked:EP003" in i for i in issues))

    def test_endpoint_whitelist_allows_ep001_ep004(self) -> None:
        case = runner.UniverseCase(
            case_id="TLC001",
            company_code="000895",
            company_name="双汇发展",
            source_type="cninfo_periodic_report_pdf",
            endpoint_scope=["EP001", "EP004"],
            expected_fields="",
            risk_level="low",
            reason="",
        )
        issues = runner.validate_universe_case(case)
        self.assertEqual(issues, [])

    def test_pdf_download_disabled(self) -> None:
        self.assertFalse(runner.PDF_DOWNLOAD_ENABLED)

    def test_pdf_parse_disabled(self) -> None:
        self.assertFalse(runner.PDF_PARSE_ENABLED)

    def test_dry_run_writes_isolated_layout(self) -> None:
        result = _run(["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        for sub in ("raw_metadata", "quality", "reports"):
            path = os.path.join(OUTPUT_ROOT, sub)
            self.assertTrue(os.path.isdir(path), msg=sub)
        report = os.path.join(
            OUTPUT_ROOT, "reports", "cninfo_b_class_tiny_live_validation_report.csv"
        )
        self.assertTrue(os.path.isfile(report))
        # 无 PDF 落盘
        for root, _dirs, files in os.walk(OUTPUT_ROOT):
            for name in files:
                self.assertFalse(name.lower().endswith(".pdf"), msg=name)

    def test_quality_missing_pdf_needs_review(self) -> None:
        record = {
            "company_code": "000895",
            "org_id": "x",
            "announcement_id": "a1",
            "announcement_title": "t",
            "announcement_time": "2025-01-01",
            "document_id": "d1",
            "retrieval_time": "2026-01-01",
            "quality_status": "",
            "pdf_url": "",
            "adjunct_url": "",
            "source_endpoint": "https://example.com",
            "lineage_status": "",
        }
        qs, ls, et, _ = runner.assess_quality_rules(record)
        self.assertEqual(qs, "needs_review")
        self.assertIn("pdf", et)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary_path = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_b_class_tiny_live_validation_runner_test_summary.md",
    )
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(
            "# B-class Tiny Live Runner Test Summary\n\n"
            f"- tests_run: {result.testsRun}\n"
            f"- passed: {passed}\n"
            f"- failed: {len(result.failures)}\n"
            f"- errors: {len(result.errors)}\n"
            f"- CNINFO calls: **0**\n"
        )
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
