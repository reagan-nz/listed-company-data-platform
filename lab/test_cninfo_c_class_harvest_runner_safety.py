"""
CNINFO C-class harvest runner 安全控制测试（无 CNINFO）。

运行：
    python lab/test_cninfo_c_class_harvest_runner_safety.py
"""

from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from harvest_cninfo_c_class import (  # noqa: E402
    BASE_DIR,
    FULL_HARVEST_APPROVAL_REQUIRED,
    HARVEST_EXPECTED_COMPANY_COUNT,
    HOLD_SAMPLE_REL,
    apply_resume_filter,
    enforce_live_approval_gate,
    load_sample_companies,
    validate_pre_live_harvest,
    _run_live_full,
)
from validate_cninfo_c_class_scale_smoke import load_sample_yaml  # noqa: E402

DEFAULT_SAMPLE = os.path.join(
    BASE_DIR, "lab", "eval_companies_c_class_harvest_863_non_bse.yaml"
)
HOLD_PATH = os.path.join(BASE_DIR, HOLD_SAMPLE_REL)
RUNNER = os.path.join(_LAB_DIR, "harvest_cninfo_c_class.py")
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_harvest_runner_safety_test_summary.md",
)


def _run_runner(argv: list) -> subprocess.CompletedProcess:
    cmd = [sys.executable, RUNNER] + argv
    return subprocess.run(
        cmd,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestHarvestRunnerSafety(unittest.TestCase):
    def test_case1_dry_run_pass(self) -> None:
        result = _run_runner([
            "--dry-run",
            "--sample-file", "lab/eval_companies_c_class_harvest_863_non_bse.yaml",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pre_dryrun_validation: PASS", result.stdout)

    def test_case2_live_without_approve_fail(self) -> None:
        result = _run_runner([
            "--live",
            "--sample-file", "lab/eval_companies_c_class_harvest_863_non_bse.yaml",
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(FULL_HARVEST_APPROVAL_REQUIRED, result.stderr)

    def test_case3_live_with_approve_enters_preflight(self) -> None:
        companies = load_sample_companies(DEFAULT_SAMPLE)
        ok, detail = validate_pre_live_harvest(
            DEFAULT_SAMPLE,
            companies,
            HOLD_PATH,
            execution_mode="full",
            approve_full_harvest=True,
            limit=None,
            resume=False,
        )
        self.assertTrue(ok, detail)
        self.assertIn("mode=full", detail)

        args = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=True,
            resume=False,
            smoke_csv="",
            smoke_md="",
        )
        mode = enforce_live_approval_gate(args)
        self.assertEqual(mode, "full")

        with patch("harvest_cninfo_c_class.run_live_harvest", return_value=([], {})):
            with patch("harvest_cninfo_c_class.write_smoke_csv"):
                with patch("harvest_cninfo_c_class.write_smoke_summary"):
                    with patch("harvest_cninfo_c_class.load_run_status", return_value=None):
                        buf = io.StringIO()
                        with redirect_stdout(buf):
                            _run_live_full(args, DEFAULT_SAMPLE, HOLD_PATH)
                        output = buf.getvalue()
        self.assertIn("pre_live_harvest_validation: PASS", output)
        self.assertIn("resume_skip_count=", output)
        self.assertIn("resume_pending_count=", output)

    def test_case4_resume_empty_status_pass(self) -> None:
        companies = [
            {"company_code": "000001", "company_name": "A"},
            {"company_code": "000002", "company_name": "B"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            status_path = os.path.join(tmp, "company_harvest_status.csv")
            pending, skip, pending_count = apply_resume_filter(
                companies, resume=True, status_csv_path=status_path,
            )
            self.assertEqual(skip, 0)
            self.assertEqual(pending_count, 2)
            self.assertEqual(len(pending), 2)

    def test_smoke_limit_without_approve_allowed(self) -> None:
        args = argparse.Namespace(
            mode="live",
            limit=10,
            approve_full_harvest=False,
            resume=False,
        )
        mode = enforce_live_approval_gate(args)
        self.assertEqual(mode, "smoke")


def write_summary(results: list) -> None:
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    passed = sum(1 for _, ok in results if ok)
    lines = [
        "# CNINFO C-Class Harvest Runner Safety Test Summary",
        "",
        f"## Result: **{passed}/{len(results)} PASS**",
        "",
        "| case | description | result |",
        "|------|-------------|--------|",
    ]
    for case_id, ok in results:
        lines.append(f"| `{case_id}` | {case_id} | **{'PASS' if ok else 'FAIL'}** |")
    lines.extend([
        "",
        "## Cases",
        "",
        "- case_1: `--dry-run` → PASS",
        "- case_2: `--live` without approve → FAIL (`FULL_HARVEST_APPROVAL_REQUIRED`)",
        "- case_3: `--live --approve-full-harvest` → preflight PASS（mock harvest）",
        "- case_4: `--resume` empty status → skip=0 pending=2",
        "",
    ])
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestHarvestRunnerSafety)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    test_map = {
        "test_case1_dry_run_pass": "case_1_dry_run",
        "test_case2_live_without_approve_fail": "case_2_live_no_approve",
        "test_case3_live_with_approve_enters_preflight": "case_3_live_approve_preflight",
        "test_case4_resume_empty_status_pass": "case_4_resume_empty",
        "test_smoke_limit_without_approve_allowed": "case_5_smoke_limit",
    }
    failed_methods = {t[0]._testMethodName for t in result.failures + result.errors}  # type: ignore[attr-defined]
    final_results = [
        (case_id, method not in failed_methods)
        for method, case_id in test_map.items()
    ]
    write_summary(final_results)
    passed = sum(1 for _, ok in final_results if ok)
    total = len(final_results)
    print(f"SUMMARY  harvest_runner_safety_tests  pass={passed}/{total}")
    for case_id, ok in final_results:
        print(f"  {case_id}: {'PASS' if ok else 'FAIL'}")
    print(f"MD    {SUMMARY_PATH}")
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
