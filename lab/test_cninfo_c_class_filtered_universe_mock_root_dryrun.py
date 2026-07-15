#!/usr/bin/env python3
"""
CNINFO C-class — filtered_universe mock-root dry-run 单测（离线）。

覆盖：
  - mock validation 根守卫（非 _mock_* / 非 validation / 生产根拒绝）
  - execute / production rebuild 硬拒绝
  - Wave1 filtered_universe 可被 batch run_dry_run 消费（mock 根）
  - --exclusion-csv 现场过滤语义
  - CLI PASS_OFFLINE · 无 snapshot JSON

运行：
    python3 lab/test_cninfo_c_class_filtered_universe_mock_root_dryrun.py
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

from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    assert_execute_production_snapshot_rebuild_false,
    refuse_exclusion_with_execute,
)
from run_cninfo_c_class_filtered_universe_mock_root_dryrun import (  # noqa: E402
    assert_mock_validation_output_root,
    run_mock_root_dryrun,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_PARTIAL7,
)

RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_filtered_universe_mock_root_dryrun.py"
)
FILTERED_YAML = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/"
    "filtered_universe_included.yaml",
)
RECONCILE_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv",
)
UNIVERSE_YAML = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_fuller_market_slice1_200.yaml"
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_filtered_universe_mock_root_dryrun_test_summary_20260715.md",
)


class TestMockRootGuards(unittest.TestCase):
    def test_refuse_non_mock_validation_path(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "MOCK_ROOT_PREFIX_REQUIRED"):
            assert_mock_validation_output_root(
                "outputs/validation/cninfo_c_class_not_mock_root"
            )

    def test_refuse_snapshot_mock_outside_validation(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "MOCK_ROOT_NOT_UNDER_VALIDATION"):
            assert_mock_validation_output_root(
                "outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_slice1_200_dryrun"
            )

    def test_refuse_full_production_root(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "MOCK_ROOT_NOT_UNDER_VALIDATION"):
            assert_mock_validation_output_root(
                "outputs/snapshot/cninfo_c_class/full"
            )

    def test_allow_validation_mock(self) -> None:
        norm = assert_mock_validation_output_root(
            "outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun"
        )
        self.assertTrue(norm.endswith("_mock_erad_filtered_universe_slice1_190_dryrun"))

    def test_refuse_execute_flag(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError, "MOCK_ROOT_DRYRUN_EXECUTE_FORBIDDEN"
        ):
            run_mock_root_dryrun(
                filtered_universe=FILTERED_YAML,
                output_root="outputs/validation/_mock_unit_refuse_execute",
                dry_run=False,
            )

    def test_refuse_production_rebuild_flag(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError, "EXECUTE_PRODUCTION_SNAPSHOT_REBUILD_FORBIDDEN"
        ):
            assert_execute_production_snapshot_rebuild_false(True)

    def test_refuse_exclusion_with_execute(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "EXCLUSION_CSV_EXECUTE_FORBIDDEN"):
            refuse_exclusion_with_execute(
                dry_run=False, exclusion_csv=RECONCILE_CSV
            )


class TestMockRootDryRun(unittest.TestCase):
    def test_wave1_filtered_consumable_by_batch_dryrun(self) -> None:
        self.assertTrue(os.path.isfile(FILTERED_YAML))
        with tempfile.TemporaryDirectory(
            prefix="_mock_fu_dryrun_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            # TemporaryDirectory 名已含 _mock_；再套一层明确段
            mock_root = os.path.join(tmp, "_mock_wave1_filtered_dryrun")
            os.makedirs(mock_root, exist_ok=True)
            rel = os.path.relpath(mock_root, BASE_DIR).replace("\\", "/")
            result = run_mock_root_dryrun(
                filtered_universe=os.path.relpath(FILTERED_YAML, BASE_DIR),
                output_root=rel,
                dry_run=True,
                execute_production_snapshot_rebuild=False,
            )
            self.assertEqual(result["gate"], "PASS_OFFLINE")
            self.assertEqual(result["company_count"], 190)
            self.assertEqual(result["snapshot_json_writes"], 0)
            self.assertFalse(result["batch_builder_execute_invoked"])
            self.assertEqual(result["partial7_leak_codes"], [])
            status_path = os.path.join(
                BASE_DIR, result["artifacts"]["status_csv"]
            )
            self.assertTrue(os.path.isfile(status_path))
            with open(status_path, encoding="utf-8", newline="") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 190)
            codes = {r["company_code"] for r in rows}
            self.assertFalse(codes & EXPECTED_SLICE1_PARTIAL7)

    def test_exclusion_csv_filter_mode(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="_mock_fu_excl_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            mock_root = os.path.join(tmp, "_mock_exclusion_csv_dryrun")
            os.makedirs(mock_root, exist_ok=True)
            rel = os.path.relpath(mock_root, BASE_DIR).replace("\\", "/")
            result = run_mock_root_dryrun(
                filtered_universe=None,
                universe_yaml=os.path.relpath(UNIVERSE_YAML, BASE_DIR),
                exclusion_csv=os.path.relpath(RECONCILE_CSV, BASE_DIR),
                output_root=rel,
                dry_run=True,
            )
            self.assertEqual(result["gate"], "PASS_OFFLINE")
            self.assertEqual(result["company_count"], 190)
            self.assertEqual(result["sample_mode"], "exclusion_csv_filter")
            filtered_out = os.path.join(mock_root, "filtered_universe_included.yaml")
            self.assertTrue(os.path.isfile(filtered_out))

    def test_cli_pass_offline(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="_mock_fu_cli_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            mock_root = os.path.join(tmp, "_mock_cli_filtered_dryrun")
            os.makedirs(mock_root, exist_ok=True)
            rel = os.path.relpath(mock_root, BASE_DIR).replace("\\", "/")
            proc = subprocess.run(
                [
                    sys.executable,
                    RUNNER,
                    "--filtered-universe",
                    os.path.relpath(FILTERED_YAML, BASE_DIR),
                    "--output-root",
                    rel,
                ],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("gate: PASS_OFFLINE", proc.stdout)
            self.assertIn("company_count: 190", proc.stdout)
            self.assertIn("snapshot_json_writes: 0", proc.stdout)
            self.assertIn("batch_builder_execute_invoked: False", proc.stdout)


def _write_test_summary(result: unittest.TestResult) -> None:
    lines = [
        "# CNINFO C 类 — Filtered Universe Mock-Root Dry-Run 测试摘要",
        "",
        f"_生成时间：离线单测 · tests={result.testsRun} · "
        f"failures={len(result.failures)} · errors={len(result.errors)}_",
        "",
        "覆盖：mock 根守卫 · execute 硬拒绝 · Wave1 filtered 消费 batch "
        "`run_dry_run` · `--exclusion-csv` 现场过滤 · CLI PASS_OFFLINE。",
        "",
        f"结果：**{'PASS' if result.wasSuccessful() else 'FAIL'}**",
        "",
    ]
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    _write_test_summary(result)
    raise SystemExit(0 if result.wasSuccessful() else 1)
