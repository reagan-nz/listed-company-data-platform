#!/usr/bin/env python3
"""
CNINFO C-class — harvest/exclusion/dual-layer 一致性单测（离线 · CNINFO=0 · C-FM-03）。

运行：
    python3 lab/test_cninfo_c_class_harvest_exclusion_dual_layer_consistency.py
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import unittest
from typing import Dict, List

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    ConsistencyPaths,
    EXPECTED_HOLDOUT9,
    assert_consistency_output_root,
    build_dual_layer_cohort_rows,
    build_family_harvest_exclusion_rows,
    build_manifest_reconcile_rows,
    family_expected_harvest_status,
    fingerprint_status_csv,
    run_harvest_exclusion_dual_layer_consistency,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
)

RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_harvest_exclusion_dual_layer_consistency.py"
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_harvest_exclusion_dual_layer_consistency_test_summary_20260715.md",
)


def _write_test_summary(results: List[Dict[str, str]]) -> None:
    lines = [
        "# C-FM-03 Harvest/Exclusion/Dual-layer Consistency — Test Summary",
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
            "c_fm_03_harvest_exclusion_dual_layer_consistency_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "```",
            "",
        ]
    )
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestRootGuards(unittest.TestCase):
    def test_refuse_non_mock(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "COHORT_ROOT_MOCK_PREFIX_REQUIRED"):
            assert_consistency_output_root(
                "outputs/validation/cninfo_c_class_not_mock"
            )

    def test_refuse_production_snapshot(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            "COHORT_ROOT_NOT_UNDER_VALIDATION|PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN",
        ):
            assert_consistency_output_root("outputs/snapshot/cninfo_c_class/full")

    def test_allow_mock(self) -> None:
        norm = assert_consistency_output_root(
            "outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency"
        )
        self.assertIn("_mock_c_fm03", norm)


class TestFamilySemantics(unittest.TestCase):
    def test_family_expected_status(self) -> None:
        self.assertEqual(
            family_expected_harvest_status({"partial7"}), "partial"
        )
        self.assertEqual(
            family_expected_harvest_status({"empty_dividend3"}), "complete"
        )
        self.assertIsNone(family_expected_harvest_status({"holdout9"}))
        self.assertEqual(
            family_expected_harvest_status({"partial7", "holdout9"}), "partial"
        )

    def test_family_rows_detect_empty3_in_pool(self) -> None:
        harvest = {
            "688031": {"harvest_status": "complete"},
            "600001": {"harvest_status": "partial"},
        }
        pool = {
            "688031": "included_complete_pool",  # 错误：应 excluded
            "600001": "excluded",
        }
        family_map = {
            "688031": {"empty_dividend3"},
            "600001": {"partial7"},
        }
        rows, checks = build_family_harvest_exclusion_rows(
            harvest_status=harvest,
            pool_decisions=pool,
            family_map=family_map,
            expected_excluded={"688031", "600001"},
        )
        self.assertFalse(checks["empty3_excluded_despite_complete_ledger"])
        self.assertFalse(checks["family_excluded_688031"])
        self.assertTrue(any(r["ok"] == "no" for r in rows))


class TestDualLayerCohortTooling(unittest.TestCase):
    def test_union_and_coverage(self) -> None:
        empty3 = {
            c: {
                "dual_layer_audit_gate": "PASS_OFFLINE",
                "rules_all_pass": "yes",
                "index_status": "indexed_pass",
            }
            for c in EXPECTED_SLICE1_EMPTY_DIVIDEND3
        }
        partial7 = {
            c: {
                "dual_layer_audit_gate": "PASS_OFFLINE",
                "rules_all_pass": "yes",
                "index_status": "indexed_pass",
            }
            for c in EXPECTED_SLICE1_PARTIAL7
        }
        coverage = [
            {
                "caveat_family": "empty_dividend",
                "expected_count": "3",
                "indexed_pass_count": "3",
                "index_status": "indexed_pass",
            },
            {
                "caveat_family": "partial",
                "expected_count": "7",
                "indexed_pass_count": "7",
                "index_status": "indexed_pass",
            },
            {
                "caveat_family": "all_caveats",
                "expected_count": "10",
                "indexed_pass_count": "10",
                "index_status": "indexed_pass",
            },
        ]
        _rows, checks = build_dual_layer_cohort_rows(
            empty3_index=empty3,
            partial7_index=partial7,
            coverage_rows=coverage,
            expected_excluded=set(EXPECTED_SLICE1_EXCLUDED_UNIQUE),
        )
        self.assertTrue(checks["dual_layer_union_equals_caveat10"])
        self.assertTrue(checks["cohort_coverage_10_of_10"])
        self.assertTrue(checks["empty3_partial7_indexes_disjoint"])


class TestManifestReconcile(unittest.TestCase):
    def test_holdout_does_not_inflate_slice1(self) -> None:
        family_map = {
            **{c: {"partial7"} for c in EXPECTED_SLICE1_PARTIAL7},
            **{c: {"empty_dividend3"} for c in EXPECTED_SLICE1_EMPTY_DIVIDEND3},
            **{c: {"holdout9"} for c in EXPECTED_HOLDOUT9},
        }
        # 000003 同时 partial7+holdout9
        family_map["000003"] = {"partial7", "holdout9"}
        harvest_codes = set(EXPECTED_SLICE1_EXCLUDED_UNIQUE) | {"600000", "600004"}
        pool = {
            **{c: "excluded" for c in EXPECTED_SLICE1_EXCLUDED_UNIQUE},
            "600000": "included_complete_pool",
            "600004": "included_complete_pool",
        }
        _rows, checks = build_manifest_reconcile_rows(
            family_map=family_map,
            pool_decisions=pool,
            harvest_codes=harvest_codes,
            expected_excluded=set(EXPECTED_SLICE1_EXCLUDED_UNIQUE),
        )
        self.assertTrue(checks["holdout9_outside_slice1_except_partial_overlap"])
        self.assertTrue(checks["slice1_manifest_hits_equal_caveat10"])
        self.assertTrue(checks["reconcile_excluded_equals_caveat10"])


class Test863Fingerprint(unittest.TestCase):
    def test_fingerprint_real_863(self) -> None:
        path = os.path.join(
            BASE_DIR,
            "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv",
        )
        fp = fingerprint_status_csv(path)
        self.assertEqual(fp["row_count"], 861)
        self.assertEqual(fp["unique_codes"], 861)
        self.assertEqual(fp["empty_code_rows"], 0)
        self.assertEqual(fp["status_counts"].get("complete"), 861)
        self.assertTrue(fp["fingerprint_sha256"])


class TestEndToEnd(unittest.TestCase):
    def test_full_consistency_pass_isolated_mock(self) -> None:
        mock_root = os.path.join(
            BASE_DIR,
            "outputs/validation/_mock_c_fm03_unit_test_tmp",
        )
        try:
            result = run_harvest_exclusion_dual_layer_consistency(
                paths=ConsistencyPaths(
                    output_root_rel=(
                        "outputs/validation/_mock_c_fm03_unit_test_tmp"
                    )
                )
            )
            self.assertEqual(result["gate"], "PASS_OFFLINE")
            self.assertEqual(result["cninfo_calls"], 0)
            self.assertFalse(result["execute_production_snapshot_rebuild"])
            self.assertEqual(result["fail_count"], 0)
            self.assertTrue(result["mock_root_is_isolated"])
            for layer, gate in result["layer_gates"].items():
                self.assertEqual(gate, "PASS_OFFLINE", msg=layer)
            matrix_path = os.path.join(BASE_DIR, result["matrix_path"])
            self.assertTrue(os.path.isfile(matrix_path))
            with open(matrix_path, encoding="utf-8", newline="") as fh:
                rows = list(csv.DictReader(fh))
            self.assertGreater(len(rows), 20)
            self.assertTrue(all(r["ok"] == "yes" for r in rows))
            fp_path = os.path.join(BASE_DIR, result["fingerprint_863_path"])
            self.assertTrue(os.path.isfile(fp_path))
        finally:
            if os.path.isdir(mock_root):
                from cninfo_c_class_erad_cleanup_guard import (
                    safe_cleanup_temp_output_root,
                )

                safe_cleanup_temp_output_root(mock_root)

    def test_cli_pass_and_execute_refuse(self) -> None:
        mock_rel = "outputs/validation/_mock_c_fm03_cli_test_tmp"
        mock_abs = os.path.join(BASE_DIR, mock_rel)
        try:
            proc = subprocess.run(
                [sys.executable, RUNNER, "--output-root", mock_rel],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr + proc.stdout)
            self.assertIn("gate: PASS_OFFLINE", proc.stdout)
            self.assertIn("cninfo_calls=0", proc.stdout)

            bad = subprocess.run(
                [sys.executable, RUNNER, "--execute"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("C_FM03_EXECUTE_FORBIDDEN", bad.stderr + bad.stdout)
        finally:
            if os.path.isdir(mock_abs):
                from cninfo_c_class_erad_cleanup_guard import (
                    safe_cleanup_temp_output_root,
                )

                safe_cleanup_temp_output_root(mock_abs)


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        rows = [
            {"case": "test_refuse_non_mock", "result": "PASS"},
            {"case": "test_refuse_production_snapshot", "result": "PASS"},
            {"case": "test_allow_mock", "result": "PASS"},
            {"case": "test_family_expected_status", "result": "PASS"},
            {"case": "test_family_rows_detect_empty3_in_pool", "result": "PASS"},
            {"case": "test_union_and_coverage", "result": "PASS"},
            {"case": "test_holdout_does_not_inflate_slice1", "result": "PASS"},
            {"case": "test_fingerprint_real_863", "result": "PASS"},
            {"case": "test_full_consistency_pass_isolated_mock", "result": "PASS"},
            {"case": "test_cli_pass_and_execute_refuse", "result": "PASS"},
        ]
    else:
        rows = [
            {"case": t.id(), "result": "FAIL"}
            for t, _err in (result.failures + result.errors)
        ]
    _write_test_summary(rows)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
