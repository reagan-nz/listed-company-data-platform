"""
CNINFO C-class snapshot exclusion 过滤逻辑单测（离线 · 无 CNINFO · 无 snapshot）。

覆盖：
  - manifest / reconcile CSV 识别与排除代码提取
  - universe 过滤（slice1 190/10 语义）
  - --exclusion-csv 与 --execute 互斥
  - execute_production_snapshot_rebuild 硬拒绝
  - prep adapter dry-run 产物与 gate

运行：
    python3 lab/test_cninfo_c_class_snapshot_exclusion_filter.py
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from typing import Dict, List

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    KIND_MANIFEST,
    KIND_RECONCILE,
    apply_exclusion_filter,
    assert_execute_production_snapshot_rebuild_false,
    detect_exclusion_csv_kind,
    extract_excluded_codes_from_manifest,
    extract_excluded_codes_from_reconcile,
    filter_universe_with_exclusion_csv,
    load_excluded_codes,
    refuse_exclusion_with_execute,
)
from run_cninfo_c_class_snapshot_exclusion_prep_adapter_dryrun import (  # noqa: E402
    run_adapter,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
)

ADAPTER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_snapshot_exclusion_prep_adapter_dryrun.py"
)
RECONCILE_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv",
)
MANIFEST_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv",
)
UNIVERSE_YAML = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_fuller_market_slice1_200.yaml"
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_snapshot_exclusion_filter_test_summary_20260715.md",
)


def _write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class TestExclusionCsvKind(unittest.TestCase):
    def test_detect_manifest(self) -> None:
        kind = detect_exclusion_csv_kind(
            ["exclusion_id", "cohort_family", "company_code"]
        )
        self.assertEqual(kind, KIND_MANIFEST)

    def test_detect_reconcile(self) -> None:
        kind = detect_exclusion_csv_kind(
            ["company_code", "pool_decision", "reconcile_ok"]
        )
        self.assertEqual(kind, KIND_RECONCILE)


class TestExtractExcludedCodes(unittest.TestCase):
    def test_manifest_extract(self) -> None:
        rows = [
            {"company_code": "600001", "cohort_family": "partial7"},
            {"company_code": "688031", "cohort_family": "empty_dividend3"},
            {"company_code": "600001", "cohort_family": "holdout9"},
        ]
        codes = extract_excluded_codes_from_manifest(rows)
        self.assertEqual(codes, {"600001", "688031"})

    def test_manifest_unknown_family_raises(self) -> None:
        rows = [{"company_code": "600000", "cohort_family": "bogus_family"}]
        with self.assertRaises(ValueError) as ctx:
            extract_excluded_codes_from_manifest(rows)
        self.assertIn("unknown_exclusion_cohort_family", str(ctx.exception))

    def test_reconcile_extract_only_excluded(self) -> None:
        rows = [
            {"company_code": "600000", "pool_decision": "included_complete_pool"},
            {"company_code": "600001", "pool_decision": "excluded"},
            {"company_code": "688031", "pool_decision": "excluded"},
        ]
        codes = extract_excluded_codes_from_reconcile(rows)
        self.assertEqual(codes, {"600001", "688031"})


class TestApplyExclusionFilter(unittest.TestCase):
    def test_filter_splits_included_excluded(self) -> None:
        companies = [
            {"company_code": "600000", "company_name": "A"},
            {"company_code": "600001", "company_name": "B"},
            {"company_code": "688031", "company_name": "C"},
        ]
        result = apply_exclusion_filter(companies, {"600001", "688031"})
        self.assertEqual(result.included_count, 1)
        self.assertEqual(result.excluded_count, 2)
        self.assertEqual(result.included[0]["company_code"], "600000")
        self.assertEqual(
            {r["company_code"] for r in result.excluded},
            {"600001", "688031"},
        )

    def test_filter_idempotent_on_missing_codes(self) -> None:
        companies = [{"company_code": "600000", "company_name": "A"}]
        result = apply_exclusion_filter(companies, {"999999"})
        self.assertEqual(result.included_count, 1)
        self.assertEqual(result.excluded_count, 0)
        self.assertEqual(result.excluded_codes, {"999999"})


class TestSafetyGuards(unittest.TestCase):
    def test_refuse_exclusion_with_execute(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            refuse_exclusion_with_execute(
                dry_run=False,
                exclusion_csv="outputs/validation/x.csv",
            )
        self.assertIn("EXCLUSION_CSV_EXECUTE_FORBIDDEN", str(ctx.exception))

    def test_allow_exclusion_with_dry_run(self) -> None:
        refuse_exclusion_with_execute(
            dry_run=True,
            exclusion_csv="outputs/validation/x.csv",
        )

    def test_refuse_production_rebuild_flag(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            assert_execute_production_snapshot_rebuild_false(True)
        self.assertIn(
            "EXECUTE_PRODUCTION_SNAPSHOT_REBUILD_FORBIDDEN",
            str(ctx.exception),
        )


class TestRealArtifactsOffline(unittest.TestCase):
    @unittest.skipUnless(os.path.isfile(RECONCILE_CSV), "Run11 reconcile CSV missing")
    def test_reconcile_csv_loads_slice1_excluded_10(self) -> None:
        codes, kind, row_count = load_excluded_codes(RECONCILE_CSV)
        self.assertEqual(kind, KIND_RECONCILE)
        self.assertEqual(row_count, 200)
        self.assertEqual(len(codes), 10)
        self.assertTrue(EXPECTED_SLICE1_PARTIAL7.issubset(codes))
        self.assertTrue(EXPECTED_SLICE1_EMPTY_DIVIDEND3.issubset(codes))
        self.assertEqual(codes, EXPECTED_SLICE1_EXCLUDED_UNIQUE)

    @unittest.skipUnless(os.path.isfile(MANIFEST_CSV), "manifest CSV missing")
    def test_manifest_csv_loads_19_rows(self) -> None:
        codes, kind, row_count = load_excluded_codes(MANIFEST_CSV)
        self.assertEqual(kind, KIND_MANIFEST)
        self.assertEqual(row_count, 19)
        self.assertGreaterEqual(len(codes), 10)
        self.assertTrue(EXPECTED_SLICE1_PARTIAL7.issubset(codes))
        self.assertTrue(EXPECTED_SLICE1_EMPTY_DIVIDEND3.issubset(codes))


class TestPrepAdapterDryRun(unittest.TestCase):
    @unittest.skipUnless(
        os.path.isfile(RECONCILE_CSV) and os.path.isfile(UNIVERSE_YAML),
        "slice1 inputs missing",
    )
    def test_adapter_run_pass_offline(self) -> None:
        out_rel = (
            "outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter"
        )
        result = run_adapter(
            universe_yaml="lab/eval_companies_c_class_fuller_market_slice1_200.yaml",
            exclusion_csv=(
                "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
                "exclusion_reconcile.csv"
            ),
            output_root=out_rel,
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["included_count"], 190)
        self.assertEqual(result["excluded_unique_count"], 10)
        self.assertFalse(result["execute_production_snapshot_rebuild"])
        self.assertFalse(result["batch_builder_execute_invoked"])
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertEqual(result["snapshot_json_writes"], 0)
        artifacts = result["artifacts"]
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, artifacts["filtered_universe_yaml"]))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, artifacts["builder_command_draft"]))
        )
        with open(
            os.path.join(BASE_DIR, artifacts["builder_command_draft"]),
            encoding="utf-8",
        ) as fh:
            draft = fh.read()
        self.assertIn("--exclusion-csv", draft)
        self.assertIn("--dry-run", draft)
        self.assertIn("_mock_erad_rebuild_slice1_200_dryrun", draft)
        # 命令草案正文不得出现 execute 模式开关
        active = "\n".join(
            line.lstrip("# ").rstrip()
            for line in draft.splitlines()
            if "python3 lab/build_cninfo_c_class_snapshot_batch.py" in line
        )
        self.assertIn("--dry-run", active)
        self.assertNotIn("--execute", active)

    def test_filter_universe_with_temp_reconcile(self) -> None:
        companies = [
            {"company_code": "600000", "company_name": "A"},
            {"company_code": "600001", "company_name": "B"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "reconcile.csv")
            _write_csv(
                path,
                ["company_code", "pool_decision"],
                [
                    {"company_code": "600000", "pool_decision": "included_complete_pool"},
                    {"company_code": "600001", "pool_decision": "excluded"},
                ],
            )
            result = filter_universe_with_exclusion_csv(companies, path)
        self.assertEqual(result.csv_kind, KIND_RECONCILE)
        self.assertEqual(result.included_count, 1)
        self.assertEqual(result.excluded_count, 1)

    def test_cli_subprocess(self) -> None:
        if not (os.path.isfile(RECONCILE_CSV) and os.path.isfile(UNIVERSE_YAML)):
            self.skipTest("slice1 inputs missing")
        proc = subprocess.run(
            [sys.executable, ADAPTER],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("gate: PASS_OFFLINE", proc.stdout)
        self.assertIn("execute_production_snapshot_rebuild: False", proc.stdout)
        self.assertIn("batch_builder_execute_invoked: False", proc.stdout)


def _write_test_summary(results: unittest.TestResult) -> None:
    total = results.testsRun
    failed = len(results.failures) + len(results.errors)
    passed = total - failed
    lines = [
        "# CNINFO C 类 — Snapshot Exclusion Filter 测试摘要",
        "",
        f"_生成时间：offline · tests={total} · passed={passed} · failed={failed}_",
        "",
        "> 无 CNINFO · 无 snapshot JSON · execute_production_snapshot_rebuild=false",
        "",
        "## Gate",
        "",
        "```",
        f"c_class_snapshot_exclusion_filter_test_gate = "
        f"{'PASS_OFFLINE' if failed == 0 else 'FAIL_REVIEW_REQUIRED'}",
        "```",
        "",
        f"tests_run={total} passed={passed} failed={failed}",
        "",
    ]
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    _write_test_summary(result)
    raise SystemExit(0 if result.wasSuccessful() else 1)
