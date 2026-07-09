"""
CNINFO C-class Phase 3 batch 500 harvest approval 扩展测试（无 CNINFO）。

运行：
    python lab/test_cninfo_c_class_phase3_batch_500_harvest_approval.py
"""

from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import harvest_cninfo_c_class as harvest_runner  # noqa: E402
from harvest_cninfo_c_class import (  # noqa: E402
    BASE_DIR,
    DEFAULT_HARVEST_OUTPUT_ROOT,
    FULL_HARVEST_APPROVAL_REQUIRED,
    HOLD_SAMPLE_REL,
    PHASE2_BATCH_OUTPUT_ROOT,
    PHASE2_SMOKE_APPROVAL_REQUIRED,
    PHASE3_BATCH_APPROVAL_REQUIRED,
    PHASE3_BATCH_OUTPUT_ROOT,
    PHASE3_OUTPUT_ROOT_FORBIDDEN,
    PHASE3_OUTPUT_ROOT_REQUIRED,
    COMPANY_HARVEST_STATUS_REL,
    RUN_STATUS_REL,
    configure_harvest_output_root,
    enforce_live_approval_gate,
    reset_harvest_output_root,
    validate_phase3_output_root,
    validate_pre_live_harvest,
)
from validate_cninfo_c_class_scale_smoke import load_sample_companies  # noqa: E402

PHASE3_SAMPLE = os.path.join(BASE_DIR, "lab", "eval_companies_c_class_phase3_batch_500_001.yaml")
PHASE2_SAMPLE = os.path.join(BASE_DIR, "lab", "eval_companies_c_class_phase2_smoke_200.yaml")
FULL_SAMPLE = os.path.join(BASE_DIR, "lab", "eval_companies_c_class_harvest_863_non_bse.yaml")
HOLD_PATH = os.path.join(BASE_DIR, HOLD_SAMPLE_REL)
RUNNER = os.path.join(_LAB_DIR, "harvest_cninfo_c_class.py")
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_harvest_approval_test_summary.md",
)


def _run_runner(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestPhase3Batch500HarvestApproval(unittest.TestCase):
    def setUp(self) -> None:
        reset_harvest_output_root()

    def tearDown(self) -> None:
        reset_harvest_output_root()

    def test_case1_phase3_live_without_approval_fails(self) -> None:
        result = _run_runner([
            "--live",
            "--sample-file", "lab/eval_companies_c_class_phase3_batch_500_001.yaml",
            "--output-root", PHASE3_BATCH_OUTPUT_ROOT,
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE3_BATCH_APPROVAL_REQUIRED, result.stderr)

        args = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            resume=False,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit) as ctx:
                enforce_live_approval_gate(args, PHASE3_SAMPLE)
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn(PHASE3_BATCH_APPROVAL_REQUIRED, buf.getvalue())

    def test_case2_phase3_live_with_full_harvest_only_fails(self) -> None:
        companies = load_sample_companies(PHASE3_SAMPLE)
        ok, detail = validate_pre_live_harvest(
            PHASE3_SAMPLE,
            companies,
            HOLD_PATH,
            execution_mode="phase3_batch",
            approve_full_harvest=True,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            limit=None,
            resume=False,
            output_root=PHASE3_BATCH_OUTPUT_ROOT,
        )
        self.assertFalse(ok)
        self.assertIn("approve_phase3_batch_500_harvest_required", detail)

        result = _run_runner([
            "--live",
            "--sample-file", "lab/eval_companies_c_class_phase3_batch_500_001.yaml",
            "--output-root", PHASE3_BATCH_OUTPUT_ROOT,
            "--approve-full-harvest",
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE3_BATCH_APPROVAL_REQUIRED, result.stderr)

    def test_case3_phase3_live_with_phase2_approval_only_fails(self) -> None:
        companies = load_sample_companies(PHASE3_SAMPLE)
        ok, detail = validate_pre_live_harvest(
            PHASE3_SAMPLE,
            companies,
            HOLD_PATH,
            execution_mode="phase3_batch",
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=True,
            approve_phase3_batch_500_harvest=False,
            limit=None,
            resume=False,
            output_root=PHASE3_BATCH_OUTPUT_ROOT,
        )
        self.assertFalse(ok)
        self.assertIn("approve_phase3_batch_500_harvest_required", detail)

        result = _run_runner([
            "--live",
            "--sample-file", "lab/eval_companies_c_class_phase3_batch_500_001.yaml",
            "--output-root", PHASE3_BATCH_OUTPUT_ROOT,
            "--approve-phase2-smoke-harvest",
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE3_BATCH_APPROVAL_REQUIRED, result.stderr)

    def test_case4_phase3_dry_run_no_approval_required(self) -> None:
        result = _run_runner([
            "--dry-run",
            "--sample-file", "lab/eval_companies_c_class_phase3_batch_500_001.yaml",
            "--output-root", PHASE3_BATCH_OUTPUT_ROOT,
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pre_dryrun_validation: PASS", result.stdout)
        self.assertIn("cninfo_requests=0", result.stdout)

    def test_case5_phase3_live_requires_isolated_output_root(self) -> None:
        companies = load_sample_companies(PHASE3_SAMPLE)
        ok, detail = validate_pre_live_harvest(
            PHASE3_SAMPLE,
            companies,
            HOLD_PATH,
            execution_mode="phase3_batch",
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=True,
            limit=None,
            resume=False,
            output_root=None,
        )
        self.assertFalse(ok)
        self.assertIn(PHASE3_OUTPUT_ROOT_REQUIRED, detail)

    def test_case6_phase3_live_rejects_default_863_root(self) -> None:
        ok, detail = validate_phase3_output_root(DEFAULT_HARVEST_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn(PHASE3_OUTPUT_ROOT_FORBIDDEN, detail)

        companies = load_sample_companies(PHASE3_SAMPLE)
        ok2, detail2 = validate_pre_live_harvest(
            PHASE3_SAMPLE,
            companies,
            HOLD_PATH,
            execution_mode="phase3_batch",
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=True,
            limit=None,
            resume=False,
            output_root=DEFAULT_HARVEST_OUTPUT_ROOT,
        )
        self.assertFalse(ok2)
        self.assertIn("default_863_root", detail2)

    def test_case7_phase3_live_rejects_phase2_output_root(self) -> None:
        ok, detail = validate_phase3_output_root(PHASE2_BATCH_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn("phase2_smoke_200", detail)

    def test_case8_phase3_resume_marker_isolated(self) -> None:
        configure_harvest_output_root(PHASE3_BATCH_OUTPUT_ROOT)
        self.assertEqual(
            harvest_runner.RUN_STATUS_REL,
            f"{PHASE3_BATCH_OUTPUT_ROOT}/run_status.json",
        )
        self.assertTrue(
            harvest_runner.COMPANY_HARVEST_STATUS_REL.endswith(
                "phase3_batch_500_001/quality/company_harvest_status.csv"
            )
        )

    def test_case9_phase2_approval_unchanged(self) -> None:
        args = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=True,
            approve_phase3_batch_500_harvest=False,
            resume=False,
        )
        mode = enforce_live_approval_gate(args, PHASE2_SAMPLE)
        self.assertEqual(mode, "phase2_smoke")

        args_full_only = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=True,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            resume=False,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_live_approval_gate(args_full_only, PHASE2_SAMPLE)
        self.assertIn(PHASE2_SMOKE_APPROVAL_REQUIRED, buf.getvalue())

    def test_case10_full_harvest_approval_unchanged(self) -> None:
        args = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=True,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            resume=False,
        )
        mode = enforce_live_approval_gate(args, FULL_SAMPLE)
        self.assertEqual(mode, "full")

        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_live_approval_gate(args, PHASE3_SAMPLE)
        self.assertIn(PHASE3_BATCH_APPROVAL_REQUIRED, buf.getvalue())
        self.assertNotIn(FULL_HARVEST_APPROVAL_REQUIRED, buf.getvalue())


def write_summary(results: list) -> None:
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    passed = sum(1 for _, ok in results if ok)
    lines = [
        "# CNINFO C-Class Phase 3 Batch 500 Harvest Approval Test Summary",
        "",
        f"## Result: **{passed}/{len(results)} PASS**",
        "",
        "| case | result |",
        "|------|--------|",
    ]
    for case_id, ok in results:
        lines.append(f"| `{case_id}` | **{'PASS' if ok else 'FAIL'}** |")
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase3Batch500HarvestApproval)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    test_map = {
        "test_case1_phase3_live_without_approval_fails": "case_1_no_approval",
        "test_case2_phase3_live_with_full_harvest_only_fails": "case_2_full_only",
        "test_case3_phase3_live_with_phase2_approval_only_fails": "case_3_phase2_only",
        "test_case4_phase3_dry_run_no_approval_required": "case_4_dry_run",
        "test_case5_phase3_live_requires_isolated_output_root": "case_5_output_root_required",
        "test_case6_phase3_live_rejects_default_863_root": "case_6_reject_863",
        "test_case7_phase3_live_rejects_phase2_output_root": "case_7_reject_phase2",
        "test_case8_phase3_resume_marker_isolated": "case_8_resume_isolated",
        "test_case9_phase2_approval_unchanged": "case_9_phase2_preserved",
        "test_case10_full_harvest_approval_unchanged": "case_10_863_preserved",
    }
    failed = {t[0]._testMethodName for t in result.failures + result.errors}  # type: ignore[attr-defined]
    final = [(cid, m not in failed) for m, cid in test_map.items()]
    write_summary(final)
    passed = sum(1 for _, ok in final if ok)
    print(f"\n{passed}/{len(final)} PASS")
    print(f"MD    {SUMMARY_PATH}")
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
