"""
Phase 3 success-subset snapshot approval 扩展测试（无 CNINFO · 无 snapshot build）。

运行：
    python lab/test_cninfo_c_class_phase3_success_snapshot_approval.py
"""

from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
import unittest
import yaml
from contextlib import redirect_stderr

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import build_cninfo_c_class_company_snapshot as company_snapshot  # noqa: E402
import build_cninfo_c_class_snapshot_batch as batch_runner  # noqa: E402
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    CLEANUP_REFUSED_MSG,
    assert_safe_test_cleanup_path,
    is_protected_c_class_production_root,
)
from build_cninfo_c_class_company_snapshot import (  # noqa: E402
    DEFAULT_HARVEST_ROOT,
    NORM_ROOT,
    _norm_path,
)
from build_cninfo_c_class_snapshot_batch import (  # noqa: E402
    BASE_DIR,
    DEFAULT_OUTPUT_DIR_REL,
    EXPECTED_COMPANY_COUNT,
    FULL_OUT_DIR,
    FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED,
    FULL_SNAPSHOT_OUT_DIR_REL,
    PHASE3_EXCLUDED_IDENTITY_CAVEAT_CODES,
    PHASE3_FULL_SNAPSHOT_APPROVAL_REJECTED,
    PHASE3_SUCCESS_SNAPSHOT_APPROVAL_REQUIRED,
    PHASE3_SUCCESS_SNAPSHOT_EXPECTED_COUNT,
    PHASE3_SUCCESS_SNAPSHOT_HARVEST_ROOT_REL,
    PHASE3_SUCCESS_SNAPSHOT_OUTPUT_ROOT_REL,
    configure_snapshot_batch_paths,
    enforce_execute_approval,
    enforce_phase3_success_snapshot_preflight,
    load_hold_codes,
    load_universe_yaml,
    planned_snapshot_path,
    reset_snapshot_batch_paths,
    validate_universe,
    HOLD_YAML,
)

PHASE3_HARVEST_ROOT = PHASE3_SUCCESS_SNAPSHOT_HARVEST_ROOT_REL
PHASE3_SNAPSHOT_ROOT = PHASE3_SUCCESS_SNAPSHOT_OUTPUT_ROOT_REL
PHASE3_SAMPLE = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml"
)
UNIVERSE_863 = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
RUNNER = os.path.join(_LAB_DIR, "build_cninfo_c_class_snapshot_batch.py")
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_success_snapshot_approval_test_summary.md",
)


def _run_runner(argv: list) -> subprocess.CompletedProcess:
    cmd = [sys.executable, RUNNER] + argv
    return subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)


class TestPhase3SuccessSnapshotApproval(unittest.TestCase):
    def setUp(self) -> None:
        reset_snapshot_batch_paths()

    def tearDown(self) -> None:
        reset_snapshot_batch_paths()

    def test_cleanup_refuses_production_phase3_snapshot_root(self) -> None:
        prod = os.path.join(BASE_DIR, PHASE3_SNAPSHOT_ROOT)
        self.assertTrue(is_protected_c_class_production_root(prod))
        with self.assertRaises(RuntimeError) as ctx:
            assert_safe_test_cleanup_path(prod)
        self.assertIn(CLEANUP_REFUSED_MSG, str(ctx.exception))

    def test_cleanup_refuses_production_full_snapshot_root(self) -> None:
        prod = os.path.join(BASE_DIR, FULL_SNAPSHOT_OUT_DIR_REL)
        with self.assertRaises(RuntimeError):
            assert_safe_test_cleanup_path(prod)
        with open(PHASE3_SAMPLE, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        self.assertEqual(data.get("company_count"), PHASE3_SUCCESS_SNAPSHOT_EXPECTED_COUNT)
        self.assertEqual(len(data.get("companies", [])), PHASE3_SUCCESS_SNAPSHOT_EXPECTED_COUNT)

    def test_case2_excluded_codes_absent(self) -> None:
        companies, _ = load_universe_yaml(PHASE3_SAMPLE)
        codes = {c["company_code"] for c in companies}
        self.assertEqual(len(codes), PHASE3_SUCCESS_SNAPSHOT_EXPECTED_COUNT)
        self.assertFalse(codes & PHASE3_EXCLUDED_IDENTITY_CAVEAT_CODES)

    def test_case3_harvest_root_routes_input(self) -> None:
        configure_snapshot_batch_paths(harvest_root=PHASE3_HARVEST_ROOT)
        path = _norm_path("cninfo_company_basic_profile", "000027")
        self.assertIn("phase3_batch_500_001", path)
        self.assertTrue(path.startswith(os.path.join(BASE_DIR, PHASE3_HARVEST_ROOT, "normalized")))

    def test_case4_output_dir_routes_output(self) -> None:
        configure_snapshot_batch_paths(output_dir=PHASE3_SNAPSHOT_ROOT)
        out = planned_snapshot_path("000027")
        self.assertIn("phase3_batch_500_001_success", out)
        self.assertTrue(out.endswith("000027.json"))

    def test_case5_omitting_harvest_root_preserves_863(self) -> None:
        configure_snapshot_batch_paths()
        self.assertEqual(company_snapshot.HARVEST_ROOT, DEFAULT_HARVEST_ROOT)
        self.assertEqual(NORM_ROOT, os.path.join(DEFAULT_HARVEST_ROOT, "normalized"))

    def test_case6_omitting_output_dir_preserves_863(self) -> None:
        configure_snapshot_batch_paths()
        expected = os.path.join(BASE_DIR, DEFAULT_OUTPUT_DIR_REL)
        self.assertEqual(FULL_OUT_DIR, expected)
        self.assertTrue(planned_snapshot_path("000019").startswith(expected))

    def test_case7_execute_without_phase3_approval_fails(self) -> None:
        result = _run_runner([
            "--execute",
            "--sample-file",
            "lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml",
            "--harvest-root", PHASE3_HARVEST_ROOT,
            "--output-dir", PHASE3_SNAPSHOT_ROOT,
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE3_SUCCESS_SNAPSHOT_APPROVAL_REQUIRED, result.stderr)

        args = argparse.Namespace(
            dry_run=False,
            approve_full_snapshot_batch=False,
            approve_phase2_smoke_188_snapshot=False,
            approve_phase3_success_snapshot_build=False,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_execute_approval(args, PHASE3_SAMPLE)
        self.assertIn(PHASE3_SUCCESS_SNAPSHOT_APPROVAL_REQUIRED, buf.getvalue())

    def test_case8_wrong_full_approval_rejected_for_phase3(self) -> None:
        result = _run_runner([
            "--execute",
            "--approve-full-snapshot-batch",
            "--sample-file",
            "lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml",
            "--harvest-root", PHASE3_HARVEST_ROOT,
            "--output-dir", PHASE3_SNAPSHOT_ROOT,
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE3_FULL_SNAPSHOT_APPROVAL_REJECTED, result.stderr)

        args = argparse.Namespace(
            dry_run=False,
            approve_full_snapshot_batch=True,
            approve_phase2_smoke_188_snapshot=False,
            approve_phase3_success_snapshot_build=True,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_execute_approval(args, PHASE3_SAMPLE)
        self.assertIn(PHASE3_FULL_SNAPSHOT_APPROVAL_REJECTED, buf.getvalue())

    def test_case9_output_root_isolation_preflight(self) -> None:
        companies, _ = load_universe_yaml(PHASE3_SAMPLE)
        good_out = os.path.join(BASE_DIR, PHASE3_SNAPSHOT_ROOT)
        enforce_phase3_success_snapshot_preflight(PHASE3_SAMPLE, good_out, companies)

        bad_out = os.path.join(BASE_DIR, FULL_SNAPSHOT_OUT_DIR_REL)
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_phase3_success_snapshot_preflight(PHASE3_SAMPLE, bad_out, companies)
        self.assertIn("PHASE3_OUTPUT_ROOT_MISMATCH", buf.getvalue())

    def test_case10_dry_run_does_not_require_approval(self) -> None:
        result = _run_runner([
            "--dry-run",
            "--sample-file",
            "lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml",
            "--harvest-root", PHASE3_HARVEST_ROOT,
            "--output-dir", PHASE3_SNAPSHOT_ROOT,
            "--output-csv",
            "outputs/validation/cninfo_c_class_phase3_success_snapshot_approval_dryrun_test_report.csv",
            "--output-md",
            "outputs/validation/cninfo_c_class_phase3_success_snapshot_approval_dryrun_test_summary.md",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("snapshot_batch_dryrun_gate: PASS_WITH_CAVEAT", result.stdout)
        self.assertIn("company_count: 491", result.stdout)

    def test_case11_863_behavior_unchanged(self) -> None:
        companies, meta = load_universe_yaml(UNIVERSE_863)
        hold = load_hold_codes(HOLD_YAML)
        ok, _ = validate_universe(companies, hold, expected_count=meta.get("company_count"))
        self.assertTrue(ok)
        self.assertEqual(len(companies), EXPECTED_COMPANY_COUNT)

        proc = _run_runner(["--dry-run"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("snapshot_batch_dryrun_gate: PASS_WITH_CAVEAT", proc.stdout)
        self.assertIn(f"company_count: {EXPECTED_COMPANY_COUNT}", proc.stdout)

        proc2 = _run_runner(["--execute"])
        self.assertEqual(proc2.returncode, 2)
        self.assertIn(FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED, proc2.stderr)


def write_summary(results: list) -> None:
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    passed = sum(1 for _, ok in results if ok)
    lines = [
        "# Phase 3 Success-Subset Snapshot Approval Extension Test Summary",
        "",
        f"## Result: **{passed}/{len(results)} PASS**",
        "",
        "| case | result |",
        "|------|--------|",
    ]
    for case_id, ok in results:
        lines.append(f"| `{case_id}` | **{'PASS' if ok else 'FAIL'}** |")
    lines.extend([
        "",
        "## 红线确认",
        "",
        "- 测试未请求 CNINFO · 未生成 snapshot JSON",
        "- raw / normalized **未修改**",
        "- 863 full dry-run 行为未变",
    ])
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase3SuccessSnapshotApproval)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    test_map = {
        "test_case1_yaml_has_491_rows": "case_1_yaml_491",
        "test_case2_excluded_codes_absent": "case_2_excluded_absent",
        "test_case3_harvest_root_routes_input": "case_3_harvest_root",
        "test_case4_output_dir_routes_output": "case_4_output_dir",
        "test_case5_omitting_harvest_root_preserves_863": "case_5_default_harvest",
        "test_case6_omitting_output_dir_preserves_863": "case_6_default_output",
        "test_case7_execute_without_phase3_approval_fails": "case_7_no_approval",
        "test_case8_wrong_full_approval_rejected_for_phase3": "case_8_wrong_approval",
        "test_case9_output_root_isolation_preflight": "case_9_output_isolation",
        "test_case10_dry_run_does_not_require_approval": "case_10_dry_run",
        "test_case11_863_behavior_unchanged": "case_11_863_unchanged",
    }
    failed = {t[0]._testMethodName for t in result.failures + result.errors}  # type: ignore[attr-defined]
    final = [(case_id, m not in failed) for m, case_id in test_map.items()]
    write_summary(final)
    passed = sum(1 for _, ok in final if ok)
    print(f"SUMMARY  phase3_success_snapshot_approval_tests  pass={passed}/{len(final)}")
    for case_id, ok in final:
        print(f"  {case_id}: {'PASS' if ok else 'FAIL'}")
    print(f"MD    {SUMMARY_PATH}")
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
