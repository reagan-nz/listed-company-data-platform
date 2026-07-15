#!/usr/bin/env python3
"""
CNINFO C-class — batch builder 原生 --exclusion-csv 单测（离线）。

覆盖：
  - --exclusion-csv + --execute 硬拒绝
  - Wave1 reconcile 过滤后 company_count=190
  - 生产 snapshot 根拒绝
  - 无 --exclusion-csv 时行为不变（不强制 validation 根）

运行：
    python3 lab/test_cninfo_c_class_snapshot_batch_exclusion_csv.py
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from build_cninfo_c_class_snapshot_batch import (  # noqa: E402
    BASE_DIR,
    EXCLUSION_CSV_NATIVE_DRYRUN_OUTPUT_ROOT_REL,
    assert_exclusion_csv_dryrun_output_root_safe,
    prepare_exclusion_csv_dryrun_universe,
    reset_snapshot_batch_paths,
    run_dry_run,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    refuse_exclusion_with_execute,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_PARTIAL7,
)

RUNNER = os.path.join(_LAB_DIR, "build_cninfo_c_class_snapshot_batch.py")
UNIVERSE_YAML = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_fuller_market_slice1_200.yaml"
)
RECONCILE_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv",
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_batch_native_exclusion_csv_test_summary_20260715.md",
)


def _run_runner(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False,
    )


class TestExclusionCsvGuards(unittest.TestCase):
    def test_refuse_exclusion_with_execute(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "EXCLUSION_CSV_EXECUTE_FORBIDDEN"):
            refuse_exclusion_with_execute(
                dry_run=False,
                exclusion_csv=RECONCILE_CSV,
            )

    def test_cli_refuse_exclusion_with_execute(self) -> None:
        proc = _run_runner(
            [
                "--execute",
                "--approve-full-snapshot-batch",
                "--sample-file",
                "lab/eval_companies_c_class_fuller_market_slice1_200.yaml",
                "--exclusion-csv",
                "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
                "exclusion_reconcile.csv",
            ]
        )
        self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
        self.assertIn("EXCLUSION_CSV_EXECUTE_FORBIDDEN", proc.stderr)

    def test_refuse_production_snapshot_root(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError, "EXCLUSION_CSV_OUTPUT_NOT_UNDER_VALIDATION"
        ):
            assert_exclusion_csv_dryrun_output_root_safe(
                os.path.join(BASE_DIR, "outputs/snapshot/cninfo_c_class/full")
            )

    def test_refuse_phase3_production_root(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError, "EXCLUSION_CSV_OUTPUT_NOT_UNDER_VALIDATION"
        ):
            assert_exclusion_csv_dryrun_output_root_safe(
                os.path.join(
                    BASE_DIR,
                    "outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success",
                )
            )

    def test_allow_validation_root(self) -> None:
        norm = assert_exclusion_csv_dryrun_output_root_safe(
            os.path.join(BASE_DIR, EXCLUSION_CSV_NATIVE_DRYRUN_OUTPUT_ROOT_REL)
        )
        self.assertTrue(norm.replace("\\", "/").endswith(
            "_batch_exclusion_csv_native_dryrun"
        ))


class TestExclusionCsvNativeDryRun(unittest.TestCase):
    def tearDown(self) -> None:
        reset_snapshot_batch_paths()

    def test_prepare_filter_wave1_190(self) -> None:
        self.assertTrue(os.path.isfile(UNIVERSE_YAML))
        self.assertTrue(os.path.isfile(RECONCILE_CSV))
        with tempfile.TemporaryDirectory(
            prefix="_batch_excl_prep_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            filtered_path, result = prepare_exclusion_csv_dryrun_universe(
                UNIVERSE_YAML,
                RECONCILE_CSV,
                tmp,
            )
            self.assertEqual(result.included_count, 190)
            self.assertEqual(len(result.excluded_codes), 10)
            self.assertTrue(os.path.isfile(filtered_path))
            codes = {c["company_code"] for c in result.included}
            self.assertFalse(codes & EXPECTED_SLICE1_PARTIAL7)

    def test_run_dry_run_on_filtered_universe(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="_batch_excl_dry_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            filtered_path, _ = prepare_exclusion_csv_dryrun_universe(
                UNIVERSE_YAML,
                RECONCILE_CSV,
                tmp,
            )
            result = run_dry_run(
                universe_path=filtered_path,
                out_dir=tmp,
                report_path=os.path.join(tmp, "dryrun_report.csv"),
                summary_path=os.path.join(tmp, "dryrun_summary.md"),
            )
            self.assertTrue(result["universe_ok"])
            self.assertEqual(result["validation"]["company_count"], 190)
            self.assertEqual(len(result["report_rows"]), 190)
            status_path = os.path.join(tmp, "quality", "company_snapshot_status.csv")
            self.assertTrue(os.path.isfile(status_path))
            with open(status_path, encoding="utf-8", newline="") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 190)

    def test_cli_native_exclusion_csv_dryrun(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="_batch_excl_cli_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            out_rel = os.path.relpath(tmp, BASE_DIR).replace("\\", "/")
            proc = _run_runner(
                [
                    "--dry-run",
                    "--sample-file",
                    "lab/eval_companies_c_class_fuller_market_slice1_200.yaml",
                    "--harvest-root",
                    "outputs/harvest/cninfo_c_class/fuller_market_slice1_200/",
                    "--output-root",
                    out_rel,
                    "--exclusion-csv",
                    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
                    "exclusion_reconcile.csv",
                ]
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("sample_mode: exclusion_csv_filter", proc.stdout)
            self.assertIn("company_count: 190", proc.stdout)
            self.assertIn("exclusion_csv_native_dryrun_gate: PASS_OFFLINE", proc.stdout)
            self.assertIn("cninfo_calls=0", proc.stdout)
            self.assertIn("snapshot_json_written=0", proc.stdout)
            self.assertIn("capability_gain: true", proc.stdout)
            filtered = os.path.join(tmp, "filtered_universe_included.yaml")
            self.assertTrue(os.path.isfile(filtered))
            status_path = os.path.join(
                tmp, "quality", "company_snapshot_status.csv"
            )
            self.assertTrue(os.path.isfile(status_path))


def _write_test_summary(result: unittest.TestResult) -> None:
    lines = [
        "# CNINFO C 类 — Batch 原生 --exclusion-csv 测试摘要",
        "",
        f"_生成时间：离线单测 · tests={result.testsRun} · "
        f"failures={len(result.failures)} · errors={len(result.errors)}_",
        "",
        "覆盖：execute 硬拒绝 · 生产根拒绝 · Wave1 190 过滤 · CLI PASS_OFFLINE。",
        "",
        f"结果：**{'PASS' if result.wasSuccessful() else 'FAIL'}**",
        "",
    ]
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    _write_test_summary(result)
    raise SystemExit(0 if result.wasSuccessful() else 1)
