"""
A-class tiny live metadata validation runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_a_class_tiny_live_metadata_validation_runner.py
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

import run_cninfo_a_class_tiny_live_metadata_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_tiny_live_metadata_validation.py")
UNIVERSE = runner.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
DRYRUN_REPORT = runner.DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.DRYRUN_SUMMARY_MD

C_CLASS_HARVEST = runner.C_CLASS_HARVEST_ROOT
B_CLASS_ROOT = runner.B_CLASS_VALIDATION_ROOT


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestATinyLiveMetadataValidationRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(["--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_live_requires_approve_a_class_tiny_live_metadata(self) -> None:
        result = _run(["--live"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TINY_LIVE_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected(self) -> None:
        for flag in (
            "--approve-full-harvest",
            "--approve-phase2-smoke-harvest",
            "--approve-phase3-batch-500-harvest",
            "--approve-b-class-tiny-live-validation",
            "--approve-phase1-tiny-live-metadata",
        ):
            result = _run(["--live", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_universe_size_must_equal_five(self) -> None:
        result = _run(["--dry-run", "--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_pdf_download_disabled(self) -> None:
        self.assertFalse(runner.PDF_DOWNLOAD_ENABLED)
        result = _run(["--dry-run", "--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_FORBIDDEN, result.stderr)

    def test_parser_disabled(self) -> None:
        self.assertFalse(runner.PDF_PARSE_ENABLED)
        result = _run(["--dry-run", "--enable-parser"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_FORBIDDEN, result.stderr)

    def test_dry_run_report_generated(self) -> None:
        result = _run(["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        self.assertEqual(set(rows[0].keys()), set(runner.DRYRUN_COLUMNS))
        for row in rows:
            self.assertEqual(row["pdf_download"], "disabled")
            self.assertEqual(row["pdf_parse"], "disabled")
            self.assertEqual(row["cninfo_call_planned"], "no")

    def test_b_c_d_outputs_untouched(self) -> None:
        before_c = set()
        if os.path.isdir(C_CLASS_HARVEST):
            for root, _dirs, files in os.walk(C_CLASS_HARVEST):
                for name in files:
                    before_c.add(os.path.join(root, name))
        before_b = set()
        if os.path.isdir(B_CLASS_ROOT):
            for root, _dirs, files in os.walk(B_CLASS_ROOT):
                for name in files:
                    before_b.add(os.path.join(root, name))

        result = _run(["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        after_c = set()
        if os.path.isdir(C_CLASS_HARVEST):
            for root, _dirs, files in os.walk(C_CLASS_HARVEST):
                for name in files:
                    after_c.add(os.path.join(root, name))
        after_b = set()
        if os.path.isdir(B_CLASS_ROOT):
            for root, _dirs, files in os.walk(B_CLASS_ROOT):
                for name in files:
                    after_b.add(os.path.join(root, name))

        self.assertEqual(before_c, after_c)
        self.assertEqual(before_b, after_b)
        report_root = os.path.normpath(OUTPUT_ROOT)
        self.assertTrue(report_root in os.path.normpath(DRYRUN_REPORT))


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
