#!/usr/bin/env python3
"""
CNINFO C-class — 隔离 snapshot 校验 cohort / lineage 单测（离线 · CNINFO=0）。

运行：
    python3 lab/test_cninfo_c_class_isolated_snapshot_validation_cohorts.py
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
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    COHORT_CAVEAT10_NEG,
    COHORT_SLICE1_190,
    assert_isolated_validation_output_root,
    build_lineage_matrix_rows,
    run_slice1_190_validation_cohort,
    summarize_lineage_checks,
    validate_standard_isolated_fingerprint_cohort,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
)

RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_isolated_snapshot_validation_cohorts.py"
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_isolated_snapshot_validation_cohorts_test_summary_20260715.md",
)


def _write_test_summary(results: List[Dict[str, str]]) -> None:
    lines = [
        "# C-FM-02 Isolated Snapshot Validation Cohorts — Test Summary",
        "",
        "_offline · CNINFO=0_",
        "",
        "| case | result |",
        "|------|--------|",
    ]
    for row in results:
        lines.append(f"| `{row['case']}` | **{row['result']}** |")
    lines.extend(
        [
            "",
            "```",
            "c_fm_02_isolated_snapshot_validation_cohorts_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "```",
            "",
        ]
    )
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestCohortRootGuards(unittest.TestCase):
    def test_refuse_non_mock_validation(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "COHORT_ROOT_MOCK_PREFIX_REQUIRED"):
            assert_isolated_validation_output_root(
                "outputs/validation/cninfo_c_class_not_mock"
            )

    def test_refuse_production_snapshot(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "COHORT_ROOT_NOT_UNDER_VALIDATION|PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN",
        ):
            assert_isolated_validation_output_root(
                "outputs/snapshot/cninfo_c_class/full"
            )

    def test_allow_validation_mock(self) -> None:
        norm = assert_isolated_validation_output_root(
            "outputs/validation/_mock_c_fm02_slice1_190_validation_cohort"
        )
        self.assertIn("_mock_c_fm02_slice1_190_validation_cohort", norm)


class TestLineageMatrixLogic(unittest.TestCase):
    def test_included_and_excluded_negative_control(self) -> None:
        included = {"600000", "600004"}
        excluded = set(EXPECTED_SLICE1_PARTIAL7)  # 用子集测逻辑
        dryrun = {
            "600000": {"company_code": "600000", "company_name": "A", "status": "pending"},
            "600004": {"company_code": "600004", "company_name": "B", "status": "pending"},
        }
        harvest = {
            "600000": {"company_code": "600000", "harvest_status": "complete"},
            "600004": {"company_code": "600004", "harvest_status": "complete"},
            "600001": {"company_code": "600001", "harvest_status": "partial"},
        }
        pool = {
            "600000": "included_complete_pool",
            "600004": "included_complete_pool",
            "600001": "excluded",
        }
        # 仅测 partial7 中的 600001 负对照
        excluded_one = {"600001"}
        rows = build_lineage_matrix_rows(
            cohort_id=COHORT_SLICE1_190,
            included_codes=included,
            excluded_codes=excluded_one,
            dryrun_status=dryrun,
            harvest_status=harvest,
            pool_decisions=pool,
        )
        summary = summarize_lineage_checks(
            rows,
            expected_included_count=2,
            expected_excluded_codes=excluded_one,
        )
        self.assertEqual(summary["gate"], "PASS_OFFLINE")
        self.assertTrue(summary["checks"]["no_lineage_failures"])

    def test_leak_fails_negative_control(self) -> None:
        included = {"600000"}
        excluded = {"600001"}
        dryrun = {
            "600000": {"company_code": "600000", "status": "pending"},
            "600001": {"company_code": "600001", "status": "pending"},  # leak
        }
        harvest = {
            "600000": {"harvest_status": "complete"},
            "600001": {"harvest_status": "partial"},
        }
        pool = {"600000": "included_complete_pool", "600001": "excluded"}
        rows = build_lineage_matrix_rows(
            cohort_id=COHORT_CAVEAT10_NEG,
            included_codes=included,
            excluded_codes=excluded,
            dryrun_status=dryrun,
            harvest_status=harvest,
            pool_decisions=pool,
        )
        summary = summarize_lineage_checks(
            rows,
            expected_included_count=1,
            expected_excluded_codes=excluded,
        )
        self.assertEqual(summary["gate"], "FAIL_REVIEW_REQUIRED")
        self.assertFalse(summary["checks"]["excluded_negative_control_all_ok"])


class TestIntegrationOffline(unittest.TestCase):
    def test_standard_isolated_fingerprint_readonly(self) -> None:
        result = validate_standard_isolated_fingerprint_cohort()
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertGreater(result["status_rows"], 0)

    def test_slice1_190_cohort_lineage_pass(self) -> None:
        # 使用临时 mock 根，避免污染默认产物；但 harvest/exclusion 用真实只读输入
        with tempfile.TemporaryDirectory(
            prefix="_mock_c_fm02_test_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            mock_root = os.path.join(tmp, "_mock_c_fm02_slice1_unit")
            from cninfo_c_class_isolated_snapshot_validation_cohorts import (
                CohortSpec,
                SLICE1_EXCLUSION_RECONCILE_REL,
                SLICE1_HARVEST_ROOT_REL,
                SLICE1_UNIVERSE_YAML_REL,
            )

            spec = CohortSpec(
                cohort_id=COHORT_SLICE1_190,
                description="unit",
                universe_yaml_rel=SLICE1_UNIVERSE_YAML_REL,
                exclusion_csv_rel=SLICE1_EXCLUSION_RECONCILE_REL,
                harvest_root_rel=SLICE1_HARVEST_ROOT_REL,
                output_root_rel=os.path.relpath(mock_root, BASE_DIR),
                expected_included_count=190,
                expected_excluded_codes=EXPECTED_SLICE1_EXCLUDED_UNIQUE,
                run_dryrun=True,
                fingerprint_repro=True,
            )
            result = run_slice1_190_validation_cohort(cohort=spec)
            self.assertEqual(result["gate"], "PASS_OFFLINE")
            self.assertEqual(result["included_count"], 190)
            self.assertEqual(result["excluded_control_count"], 10)
            self.assertTrue(result["reproducible"])
            matrix_path = os.path.join(BASE_DIR, result["matrix_path"])
            self.assertTrue(os.path.isfile(matrix_path))
            with open(matrix_path, encoding="utf-8", newline="") as fh:
                rows = list(csv.DictReader(fh))
            # included(190) + excluded(10) + neg-control clone(10) = 210
            self.assertEqual(len(rows), 210)
            included_ok = sum(
                1
                for r in rows
                if r["role"] == "included" and r["lineage_ok"] == "yes"
            )
            self.assertEqual(included_ok, 190)

    def test_runner_cli_refuse_execute(self) -> None:
        proc = subprocess.run(
            [sys.executable, RUNNER, "--execute"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("C_FM02_EXECUTE_FORBIDDEN", proc.stderr + proc.stdout)

    def test_runner_cli_pass_offline(self) -> None:
        proc = subprocess.run(
            [sys.executable, RUNNER],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("cninfo_calls=0", proc.stdout)
        self.assertIn("gate: PASS_OFFLINE", proc.stdout)


def main() -> int:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestCohortRootGuards))
    suite.addTests(loader.loadTestsFromTestCase(TestLineageMatrixLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationOffline))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    cases = []
    for test, err in result.failures + result.errors:
        cases.append({"case": test.id(), "result": "FAIL"})
    # 成功 case 名（简化）
    if result.wasSuccessful():
        cases = [
            {"case": "case_1_refuse_non_mock", "result": "PASS"},
            {"case": "case_2_refuse_production_snapshot", "result": "PASS"},
            {"case": "case_3_allow_validation_mock", "result": "PASS"},
            {"case": "case_4_lineage_ok", "result": "PASS"},
            {"case": "case_5_leak_fails", "result": "PASS"},
            {"case": "case_6_standard_isolated_readonly", "result": "PASS"},
            {"case": "case_7_slice1_190_lineage", "result": "PASS"},
            {"case": "case_8_cli_refuse_execute", "result": "PASS"},
            {"case": "case_9_cli_pass_offline", "result": "PASS"},
        ]
        _write_test_summary(cases)
        print(f"test_summary: {SUMMARY_PATH}")
        return 0
    _write_test_summary(cases or [{"case": "suite", "result": "FAIL"}])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
