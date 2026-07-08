"""
CNINFO C-class harvest runner output-root 隔离扩展测试（无 CNINFO）。

运行：
    python lab/test_cninfo_c_class_harvest_output_root_isolation.py
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
    HOLD_SAMPLE_REL,
    HARVEST_MATRIX_SOURCE_ORDER,
    PHASE2_SMOKE_APPROVAL_REQUIRED,
    configure_harvest_output_root,
    enforce_live_approval_gate,
    reset_harvest_output_root,
    validate_pre_live_harvest,
    _planned_normalized_path,
    _planned_quality_paths,
    _planned_raw_path,
)
from validate_cninfo_c_class_scale_smoke import load_sample_companies  # noqa: E402

ISOLATED_ROOT = "outputs/harvest/cninfo_c_class/phase2_smoke_200"
PHASE2_SAMPLE = os.path.join(BASE_DIR, "lab", "eval_companies_c_class_phase2_smoke_200.yaml")
HOLD_PATH = os.path.join(BASE_DIR, HOLD_SAMPLE_REL)
RUNNER = os.path.join(_LAB_DIR, "harvest_cninfo_c_class.py")
SAMPLE_SOURCE_ID = HARVEST_MATRIX_SOURCE_ORDER[0]
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_phase2_smoke_200_harvest_output_root_isolation_test_summary.md",
)


def _run_runner(argv: list) -> subprocess.CompletedProcess:
    cmd = [sys.executable, RUNNER] + argv
    return subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)


class TestHarvestOutputRootIsolation(unittest.TestCase):
    def setUp(self) -> None:
        reset_harvest_output_root()

    def tearDown(self) -> None:
        reset_harvest_output_root()

    def test_case1_output_root_routes_raw(self) -> None:
        configure_harvest_output_root(ISOLATED_ROOT)
        path = _planned_raw_path(SAMPLE_SOURCE_ID, "000001")
        self.assertTrue(path.startswith(f"{ISOLATED_ROOT}/raw/"))

    def test_case2_output_root_routes_normalized(self) -> None:
        configure_harvest_output_root(ISOLATED_ROOT)
        path = _planned_normalized_path(SAMPLE_SOURCE_ID, "000001")
        self.assertTrue(path.startswith(f"{ISOLATED_ROOT}/normalized/"))

    def test_case3_output_root_routes_quality(self) -> None:
        configure_harvest_output_root(ISOLATED_ROOT)
        paths = _planned_quality_paths()
        self.assertTrue(paths)
        for qp in paths:
            self.assertTrue(qp.startswith(f"{ISOLATED_ROOT}/quality/"))

    def test_case4_run_status_isolated_under_output_root(self) -> None:
        configure_harvest_output_root(ISOLATED_ROOT)
        self.assertEqual(
            harvest_runner.RUN_STATUS_REL,
            f"{ISOLATED_ROOT}/run_status.json",
        )

    def test_case5_omitting_output_root_preserves_old_paths(self) -> None:
        configure_harvest_output_root(None)
        raw = _planned_raw_path(SAMPLE_SOURCE_ID, "000001")
        norm = _planned_normalized_path(SAMPLE_SOURCE_ID, "000001")
        self.assertTrue(raw.startswith(f"{DEFAULT_HARVEST_OUTPUT_ROOT}/raw/"))
        self.assertTrue(norm.startswith(f"{DEFAULT_HARVEST_OUTPUT_ROOT}/normalized/"))
        self.assertEqual(
            harvest_runner.RUN_STATUS_REL,
            f"{DEFAULT_HARVEST_OUTPUT_ROOT}/quality/run_status.json",
        )

    def test_case6_phase2_live_without_approval_fails_safely(self) -> None:
        result = _run_runner([
            "--live",
            "--sample-file", "lab/eval_companies_c_class_phase2_smoke_200.yaml",
            "--output-root", ISOLATED_ROOT,
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE2_SMOKE_APPROVAL_REQUIRED, result.stderr)

        args = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=False,
            resume=False,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit) as ctx:
                enforce_live_approval_gate(args, PHASE2_SAMPLE)
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn(PHASE2_SMOKE_APPROVAL_REQUIRED, buf.getvalue())

    def test_case7_phase2_approval_separate_from_full_harvest(self) -> None:
        companies = load_sample_companies(PHASE2_SAMPLE)
        ok, detail = validate_pre_live_harvest(
            PHASE2_SAMPLE,
            companies,
            HOLD_PATH,
            execution_mode="phase2_smoke",
            approve_full_harvest=True,
            approve_phase2_smoke_harvest=True,
            limit=None,
            resume=False,
        )
        self.assertFalse(ok)
        self.assertIn("approve_full_harvest_not_valid_for_phase2", detail)

        args_approve_phase2 = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=True,
            resume=False,
        )
        mode = enforce_live_approval_gate(args_approve_phase2, PHASE2_SAMPLE)
        self.assertEqual(mode, "phase2_smoke")

        args_full_only = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=True,
            approve_phase2_smoke_harvest=False,
            resume=False,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_live_approval_gate(args_full_only, PHASE2_SAMPLE)
        self.assertIn(PHASE2_SMOKE_APPROVAL_REQUIRED, buf.getvalue())

    def test_case8_dry_run_does_not_require_live_approval(self) -> None:
        result = _run_runner([
            "--dry-run",
            "--sample-file", "lab/eval_companies_c_class_phase2_smoke_200.yaml",
            "--output-root", ISOLATED_ROOT,
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pre_dryrun_validation: PASS", result.stdout)
        self.assertIn("cninfo_requests=0", result.stdout)


def write_summary(results: list) -> None:
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    passed = sum(1 for _, ok in results if ok)
    lines = [
        "# CNINFO C-Class Harvest Output-Root Isolation Test Summary",
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
        "- case_1: `--output-root` routes raw path",
        "- case_2: `--output-root` routes normalized path",
        "- case_3: `--output-root` routes quality path",
        "- case_4: `run_status.json` isolated under output-root",
        "- case_5: omitting `--output-root` preserves old paths",
        "- case_6: phase2 live without `--approve-phase2-smoke-harvest` fails safely",
        "- case_7: phase2 approval separate from `--approve-full-harvest`",
        "- case_8: dry-run does not require live approval flag",
        "",
    ])
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestHarvestOutputRootIsolation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    test_map = {
        "test_case1_output_root_routes_raw": "case_1_raw_path",
        "test_case2_output_root_routes_normalized": "case_2_normalized_path",
        "test_case3_output_root_routes_quality": "case_3_quality_path",
        "test_case4_run_status_isolated_under_output_root": "case_4_run_status",
        "test_case5_omitting_output_root_preserves_old_paths": "case_5_default_paths",
        "test_case6_phase2_live_without_approval_fails_safely": "case_6_no_approval",
        "test_case7_phase2_approval_separate_from_full_harvest": "case_7_approval_scope",
        "test_case8_dry_run_does_not_require_live_approval": "case_8_dry_run",
    }
    failed_methods = {t[0]._testMethodName for t in result.failures + result.errors}  # type: ignore[attr-defined]
    final_results = [
        (case_id, method not in failed_methods)
        for method, case_id in test_map.items()
    ]
    write_summary(final_results)
    passed = sum(1 for _, ok in final_results if ok)
    total = len(final_results)
    print(f"SUMMARY  output_root_isolation_tests  pass={passed}/{total}")
    for case_id, ok in final_results:
        print(f"  {case_id}: {'PASS' if ok else 'FAIL'}")
    print(f"MD    {SUMMARY_PATH}")
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
