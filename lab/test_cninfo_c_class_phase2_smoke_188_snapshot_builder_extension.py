"""
Phase 2 smoke 188 snapshot builder 扩展测试（无 CNINFO · 无 snapshot build）。

运行：
    python lab/test_cninfo_c_class_phase2_smoke_188_snapshot_builder_extension.py
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
from build_cninfo_c_class_company_snapshot import (  # noqa: E402
    DEFAULT_HARVEST_ROOT,
    NORM_ROOT,
    _norm_path,
)
from build_cninfo_c_class_snapshot_batch import (  # noqa: E402
    BASE_DIR,
    DEFAULT_OUTPUT_DIR_REL,
    FULL_OUT_DIR,
    FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED,
    PHASE2_SMOKE_188_APPROVAL_REQUIRED,
    PHASE2_SMOKE_188_EXPECTED_COUNT,
    configure_snapshot_batch_paths,
    enforce_execute_approval,
    load_universe_yaml,
    planned_snapshot_path,
    reset_snapshot_batch_paths,
    validate_universe,
)
from build_cninfo_c_class_snapshot_batch import load_hold_codes, HOLD_YAML  # noqa: E402

PHASE2_HARVEST_ROOT = "outputs/harvest/cninfo_c_class/phase2_smoke_200"
PHASE2_SNAPSHOT_ROOT = "outputs/snapshot/cninfo_c_class/phase2_smoke_188"
PHASE2_SAMPLE = os.path.join(BASE_DIR, "lab/eval_companies_c_class_phase2_smoke_188_snapshot.yaml")
UNIVERSE_863 = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
RUNNER = os.path.join(_LAB_DIR, "build_cninfo_c_class_snapshot_batch.py")
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_c_class_phase2_smoke_188_snapshot_builder_extension_test_summary.md",
)

# 与 subset design 对齐的排除代码
EXCLUDED_PHASE2_CODES = frozenset({
    "000038", "000616", "000956", "002087", "002231", "300023",
    "300356", "600005", "600290", "600634", "600646", "600696",
})


def _run_runner(argv: list) -> subprocess.CompletedProcess:
    cmd = [sys.executable, RUNNER] + argv
    return subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)


class TestPhase2SnapshotBuilderExtension(unittest.TestCase):
    def setUp(self) -> None:
        reset_snapshot_batch_paths()

    def tearDown(self) -> None:
        reset_snapshot_batch_paths()

    def test_case1_yaml_has_188_rows(self) -> None:
        with open(PHASE2_SAMPLE, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        self.assertEqual(data.get("company_count"), PHASE2_SMOKE_188_EXPECTED_COUNT)
        self.assertEqual(len(data.get("companies", [])), PHASE2_SMOKE_188_EXPECTED_COUNT)

    def test_case2_excluded_codes_absent(self) -> None:
        companies, _ = load_universe_yaml(PHASE2_SAMPLE)
        codes = {c["company_code"] for c in companies}
        self.assertEqual(len(codes), PHASE2_SMOKE_188_EXPECTED_COUNT)
        self.assertFalse(codes & EXCLUDED_PHASE2_CODES)

    def test_case3_harvest_root_routes_input(self) -> None:
        configure_snapshot_batch_paths(harvest_root=PHASE2_HARVEST_ROOT)
        path = _norm_path("cninfo_company_basic_profile", "000019")
        self.assertIn("phase2_smoke_200", path)
        self.assertTrue(path.startswith(os.path.join(BASE_DIR, PHASE2_HARVEST_ROOT, "normalized")))

    def test_case4_output_dir_routes_output(self) -> None:
        configure_snapshot_batch_paths(output_dir=PHASE2_SNAPSHOT_ROOT)
        out = planned_snapshot_path("000019")
        self.assertIn("phase2_smoke_188", out)
        self.assertTrue(out.endswith("000019.json"))

    def test_case5_omitting_harvest_root_preserves_863(self) -> None:
        configure_snapshot_batch_paths()
        self.assertEqual(company_snapshot.HARVEST_ROOT, DEFAULT_HARVEST_ROOT)
        self.assertEqual(NORM_ROOT, os.path.join(DEFAULT_HARVEST_ROOT, "normalized"))

    def test_case6_omitting_output_dir_preserves_863(self) -> None:
        configure_snapshot_batch_paths()
        expected = os.path.join(BASE_DIR, DEFAULT_OUTPUT_DIR_REL)
        self.assertEqual(FULL_OUT_DIR, expected)
        self.assertTrue(planned_snapshot_path("000019").startswith(expected))

    def test_case7_execute_without_phase2_approval_fails(self) -> None:
        result = _run_runner([
            "--execute",
            "--sample-file", "lab/eval_companies_c_class_phase2_smoke_188_snapshot.yaml",
            "--harvest-root", PHASE2_HARVEST_ROOT,
            "--output-dir", PHASE2_SNAPSHOT_ROOT,
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE2_SMOKE_188_APPROVAL_REQUIRED, result.stderr)

        args = argparse.Namespace(
            dry_run=False,
            approve_full_snapshot_batch=False,
            approve_phase2_smoke_188_snapshot=False,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_execute_approval(args, PHASE2_SAMPLE)
        self.assertIn(PHASE2_SMOKE_188_APPROVAL_REQUIRED, buf.getvalue())

    def test_case8_dry_run_does_not_require_approval(self) -> None:
        result = _run_runner([
            "--dry-run",
            "--sample-file", "lab/eval_companies_c_class_phase2_smoke_188_snapshot.yaml",
            "--harvest-root", PHASE2_HARVEST_ROOT,
            "--output-dir", PHASE2_SNAPSHOT_ROOT,
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("snapshot_batch_dryrun_gate: PASS_WITH_CAVEAT", result.stdout)

    def test_case9_phase2_approval_separate_from_full(self) -> None:
        args_phase2 = argparse.Namespace(
            dry_run=False,
            approve_full_snapshot_batch=False,
            approve_phase2_smoke_188_snapshot=True,
        )
        mode = enforce_execute_approval(args_phase2, PHASE2_SAMPLE)
        self.assertEqual(mode, "phase2_smoke_188")

        args_full_only = argparse.Namespace(
            dry_run=False,
            approve_full_snapshot_batch=True,
            approve_phase2_smoke_188_snapshot=False,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_execute_approval(args_full_only, PHASE2_SAMPLE)
        self.assertIn(PHASE2_SMOKE_188_APPROVAL_REQUIRED, buf.getvalue())

        companies, meta = load_universe_yaml(UNIVERSE_863)
        hold = load_hold_codes(HOLD_YAML)
        ok, _ = validate_universe(companies, hold, expected_count=meta.get("company_count"))
        self.assertTrue(ok)


def write_summary(results: list) -> None:
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    passed = sum(1 for _, ok in results if ok)
    lines = [
        "# Phase 2 Smoke 188 Snapshot Builder Extension Test Summary",
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
    suite = loader.loadTestsFromTestCase(TestPhase2SnapshotBuilderExtension)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    test_map = {
        "test_case1_yaml_has_188_rows": "case_1_yaml_188",
        "test_case2_excluded_codes_absent": "case_2_excluded_absent",
        "test_case3_harvest_root_routes_input": "case_3_harvest_root",
        "test_case4_output_dir_routes_output": "case_4_output_dir",
        "test_case5_omitting_harvest_root_preserves_863": "case_5_default_harvest",
        "test_case6_omitting_output_dir_preserves_863": "case_6_default_output",
        "test_case7_execute_without_phase2_approval_fails": "case_7_no_approval",
        "test_case8_dry_run_does_not_require_approval": "case_8_dry_run",
        "test_case9_phase2_approval_separate_from_full": "case_9_approval_scope",
    }
    failed = {t[0]._testMethodName for t in result.failures + result.errors}  # type: ignore[attr-defined]
    final = [(case_id, m not in failed) for m, case_id in test_map.items()]
    write_summary(final)
    passed = sum(1 for _, ok in final if ok)
    print(f"SUMMARY  phase2_snapshot_builder_extension_tests  pass={passed}/{len(final)}")
    for case_id, ok in final:
        print(f"  {case_id}: {'PASS' if ok else 'FAIL'}")
    print(f"MD    {SUMMARY_PATH}")
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
