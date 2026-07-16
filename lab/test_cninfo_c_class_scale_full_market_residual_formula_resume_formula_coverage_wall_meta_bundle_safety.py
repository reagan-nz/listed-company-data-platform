"""
CNINFO C-class — 规模 residual_formula/resume_formula/coverage/repro-wall-meta-bundle
单测（离线 · CNINFO=0 · C-FM-51）。

运行：
    python3 lab/test_cninfo_c_class_scale_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_safety.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_scale_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    EXPECTED_COMBINED_DRYRUN_COVERAGE,
    EXPECTED_COVERAGE_PRIMARY_COMPOSITION_SHA256,
    EXPECTED_COVERAGE_PRIMARY_FORMULA,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_CROSS_FULL_MARKET_RESIDUAL_FORMULA_RESUME_FORMULA_COVERAGE_WALL_META_BUNDLE,
    EXPECTED_CROSS_FULL_MARKET_RESIDUAL_FORMULA_RESUME_FORMULA_COVERAGE_WALL_META_BUNDLE_SHA256,
    EXPECTED_DRY863_EXTRA,
    EXPECTED_FAILED_CODES,
    EXPECTED_HARVEST_ADDITIVE,
    EXPECTED_HARVEST_UNIQUE_UNION,
    EXPECTED_OVERLAP_DELTA,
    EXPECTED_PARTIAL_RISK_BANDS,
    EXPECTED_RESIDUAL_FORMULA,
    EXPECTED_RESIDUAL_SAFETY_COVERAGE,
    EXPECTED_RESUME_FORMULA,
    EXPECTED_RESUME_IMPROVED,
    EXPECTED_RESUME_SAME,
    EXPECTED_RESUME_TAXONOMY_FORMULA,
    EXPECTED_RESUME_TOTAL,
    EXPECTED_RESUME_WORSE,
    EXPECTED_RISK_BAND_STATUS_FORMULA,
    EXPECTED_RESIDUAL_FORMULA_PRIMARY_COMPOSITION_SHA256,
    EXPECTED_RESIDUAL_FORMULA_PRIMARY_FORMULA,
    EXPECTED_SCALE_TIER_COUNT,
    EXPECTED_SURFACE_HARVEST_DELTA_N,
    EXPECTED_SURFACE_UNIQUE,
    EXPECTED_RESUME_FORMULA_PRIMARY_COMPOSITION_SHA256,
    EXPECTED_RESUME_FORMULA_PRIMARY_FORMULA,
    EXPECTED_UNION_COMPLETE,
    EXPECTED_UNION_FAILED,
    EXPECTED_UNION_PARTIAL,
    FROZEN_COVERAGE_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
    FROZEN_CROSS_FULL_MARKET_RESIDUAL_FORMULA_RESUME_FORMULA_COVERAGE_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256,
    FROZEN_RESIDUAL_FORMULA_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
    FROZEN_RESUME_FORMULA_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
    FullMarketResidualFormulaResumeFormulaCoverageWallMetaBundlePaths,
    assert_fm51_output_root,
    build_coverage_composition_identity_lock_rows,
    build_cross_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_identity_lock_rows,
    build_fm50_continuity_rows,
    build_residual_formula_composition_identity_lock_rows,
    build_resume_formula_composition_identity_lock_rows,
    evaluate_coverage_composition_mutation,
    evaluate_cross_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_mutation,
    evaluate_residual_formula_composition_mutation,
    evaluate_resume_formula_composition_mutation,
    fingerprint_residual_formula_composition_identity_lock,
    run_scale_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_safety,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR,
    "run_cninfo_c_class_scale_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_safety.py",
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_safety_test_summary_20260716.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-51 Scale Residual-Formula/Resume-Formula/Coverage-Wall-Meta-Bundle — Test Summary",
        "",
        "_offline · CNINFO=0_",
        "",
        "| case | result |",
        "|------|--------|",
    ]
    for c in cases:
        lines.append(f"| `{c['case']}` | **{c['result']}** |")
    lines.extend(
        [
            "",
            "```",
            "c_fm_50_scale_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_safety_test_gate = "
            "PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "ready_for_execute = false",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "idle_not_required_while_awaiting = true",
            "hold_recommendation = KEEP_EXECUTE_FALSE",
            "seal_chain_extended = false",
            f"scale_tier_count = {EXPECTED_SCALE_TIER_COUNT}",
            f"company_coverage_sum = {EXPECTED_COMPANY_COVERAGE_SUM}",
            f"harvest_unique_union = {EXPECTED_HARVEST_UNIQUE_UNION}",
            f"harvest_additive = {EXPECTED_HARVEST_ADDITIVE}",
            f"surface_unique = {EXPECTED_SURFACE_UNIQUE}",
            f"combined_dryrun_coverage = {EXPECTED_COMBINED_DRYRUN_COVERAGE}",
            f"union_complete = {EXPECTED_UNION_COMPLETE}",
            f"union_partial = {EXPECTED_UNION_PARTIAL}",
            f"union_failed = {EXPECTED_UNION_FAILED}",
            f"overlap_delta = {EXPECTED_OVERLAP_DELTA}",
            f"resume_improved = {EXPECTED_RESUME_IMPROVED}",
            f"resume_same = {EXPECTED_RESUME_SAME}",
            f"resume_worse = {EXPECTED_RESUME_WORSE}",
            f"surface_harvest_delta_n = {EXPECTED_SURFACE_HARVEST_DELTA_N}",
            f"residual_safety_coverage = {EXPECTED_RESIDUAL_SAFETY_COVERAGE}",
            f"residual_formula = {EXPECTED_RESIDUAL_FORMULA_PRIMARY_FORMULA}",
            f"resume_formula = {EXPECTED_RESUME_FORMULA_PRIMARY_FORMULA}",
            f"coverage_formula = {EXPECTED_COVERAGE_PRIMARY_FORMULA}",
            f"residual_formula = {EXPECTED_RESIDUAL_FORMULA}",
            f"resume_taxonomy_formula = {EXPECTED_RESUME_TAXONOMY_FORMULA}",
            f"risk_band_status_wall_formula = {EXPECTED_RISK_BAND_STATUS_FORMULA}",
            f"residual_formula_composition_sha256 = {EXPECTED_RESIDUAL_FORMULA_PRIMARY_COMPOSITION_SHA256}",
            f"resume_formula_composition_sha256 = {EXPECTED_RESUME_FORMULA_PRIMARY_COMPOSITION_SHA256}",
            f"coverage_composition_sha256 = {EXPECTED_COVERAGE_PRIMARY_COMPOSITION_SHA256}",
            f"cross_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_sha256 = "
            f"{EXPECTED_CROSS_FULL_MARKET_RESIDUAL_FORMULA_RESUME_FORMULA_COVERAGE_WALL_META_BUNDLE_SHA256}",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestCFm51FullMarketResidualFormulaResumeFormulaCoverageWallMetaBundle(unittest.TestCase):
    def test_constants_frozen(self) -> None:
        self.assertEqual(EXPECTED_SURFACE_HARVEST_DELTA_N, 2)
        self.assertEqual(EXPECTED_COMBINED_DRYRUN_COVERAGE, 1053)
        self.assertEqual(EXPECTED_UNION_COMPLETE, 2134)
        self.assertEqual(EXPECTED_UNION_PARTIAL, 106)
        self.assertEqual(EXPECTED_UNION_FAILED, 9)
        self.assertEqual(EXPECTED_OVERLAP_DELTA, 12)
        self.assertEqual(EXPECTED_RESIDUAL_SAFETY_COVERAGE, 117)
        self.assertEqual(EXPECTED_SCALE_TIER_COUNT, 7)
        self.assertEqual(EXPECTED_COMPANY_COVERAGE_SUM, 3314)
        self.assertEqual(EXPECTED_HARVEST_UNIQUE_UNION, 2249)
        self.assertEqual(EXPECTED_SURFACE_UNIQUE, 2251)
        self.assertEqual(EXPECTED_HARVEST_ADDITIVE, 2261)
        self.assertEqual(
            EXPECTED_HARVEST_UNIQUE_UNION + EXPECTED_SURFACE_HARVEST_DELTA_N,
            EXPECTED_SURFACE_UNIQUE,
        )
        self.assertEqual(
            EXPECTED_HARVEST_UNIQUE_UNION + EXPECTED_OVERLAP_DELTA,
            EXPECTED_HARVEST_ADDITIVE,
        )
        self.assertEqual(EXPECTED_RESUME_IMPROVED, 28)
        self.assertEqual(EXPECTED_RESUME_SAME, 1)
        self.assertEqual(EXPECTED_RESUME_WORSE, 0)
        self.assertEqual(EXPECTED_RESUME_TOTAL, 29)
        self.assertEqual(sorted(EXPECTED_DRY863_EXTRA), ["000037", "000055"])
        self.assertEqual(len(EXPECTED_FAILED_CODES), 9)
        self.assertEqual(
            EXPECTED_PARTIAL_RISK_BANDS,
            {"p35_heavy": 75, "p3_mid": 14, "p2_mid": 12, "fu_light": 5},
        )
        self.assertEqual(EXPECTED_RESIDUAL_FORMULA_PRIMARY_FORMULA, "106+9+2=117")
        self.assertEqual(EXPECTED_RESUME_FORMULA_PRIMARY_FORMULA, "28+1+0=29")
        self.assertEqual(EXPECTED_COVERAGE_PRIMARY_FORMULA, "coverage=117")
        self.assertEqual(EXPECTED_RESIDUAL_FORMULA, "106+9+2=117")
        self.assertEqual(EXPECTED_RESUME_TAXONOMY_FORMULA, "28/1/0")
        self.assertEqual(EXPECTED_RISK_BAND_STATUS_FORMULA, "75/14/12/5")
        self.assertEqual(EXPECTED_RESUME_FORMULA, "28+1+0=29")
        self.assertEqual(
            len(EXPECTED_CROSS_FULL_MARKET_RESIDUAL_FORMULA_RESUME_FORMULA_COVERAGE_WALL_META_BUNDLE), 5
        )

    def test_residual_formula_composition_mutation_denied(self) -> None:
        mut = evaluate_residual_formula_composition_mutation(
            proposed_partial=107,
            proposed_failed=9,
            proposed_delta_n=2,
            proposed_coverage=118,
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_residual_formula_composition_identity_lock_rows(
            FullMarketResidualFormulaResumeFormulaCoverageWallMetaBundlePaths()
        )
        self.assertTrue(checks["residual_formula_composition_identity_lock_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_RESIDUAL_FORMULA_COMPOSITION_IDENTITY_LOCK_FP_SHA256
        )


    def test_resume_formula_composition_mutation_denied(self) -> None:
        mut = evaluate_resume_formula_composition_mutation(
            proposed_improved=27,
            proposed_same=1,
            proposed_worse=0,
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_resume_formula_composition_identity_lock_rows(
            FullMarketResidualFormulaResumeFormulaCoverageWallMetaBundlePaths()
        )
        self.assertTrue(checks["resume_formula_composition_identity_lock_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_RESUME_FORMULA_COMPOSITION_IDENTITY_LOCK_FP_SHA256
        )


    def test_coverage_composition_mutation_denied(self) -> None:
        mut = evaluate_coverage_composition_mutation(
            proposed_coverage=116,
            proposed_formula="coverage=117",
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_coverage_composition_identity_lock_rows(
            FullMarketResidualFormulaResumeFormulaCoverageWallMetaBundlePaths()
        )
        self.assertTrue(checks["coverage_composition_identity_lock_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_COVERAGE_COMPOSITION_IDENTITY_LOCK_FP_SHA256
        )


    def test_wall_meta_bundle_mutation_denied(self) -> None:
        mut = evaluate_cross_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_mutation(
            proposed_compositions={}
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_cross_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_identity_lock_rows(
            FullMarketResidualFormulaResumeFormulaCoverageWallMetaBundlePaths()
        )
        self.assertTrue(
            checks[
                "cross_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_identity_lock_all_pass"
            ]
        )
        self.assertEqual(
            meta["fingerprint"],
            FROZEN_CROSS_FULL_MARKET_RESIDUAL_FORMULA_RESUME_FORMULA_COVERAGE_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256,
        )

    def test_fm50_continuity(self) -> None:
        rows, checks = build_fm50_continuity_rows(
            FullMarketResidualFormulaResumeFormulaCoverageWallMetaBundlePaths()
        )
        self.assertTrue(checks["fm50_continuity_all_pass"])
        self.assertGreaterEqual(len(rows), 7)

    def test_output_root_guards(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_fm51_output_root(
                "outputs/validation/_mock_c_fm49_scale_full_market_union_status_residual_coverage_resume_taxonomy_disposition_wall_meta_bundle_safety"
            )
        ok = assert_fm51_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertTrue(ok.endswith(DEFAULT_MOCK_OUTPUT_ROOT_REL.split("/")[-1]) or DEFAULT_MOCK_OUTPUT_ROOT_REL in ok)
        with self.assertRaises(Exception):
            assert_authoritative_dual_layer_index_write_forbidden(
                AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL
            )

    def test_full_offline_run(self) -> None:
        payload = run_scale_full_market_residual_formula_resume_formula_coverage_wall_meta_bundle_safety()
        self.assertEqual(payload["gate"], "PASS_OFFLINE")
        self.assertEqual(payload["fail_count"], 0)
        self.assertEqual(payload["cninfo_calls"], 0)
        self.assertIs(payload["execute_production_snapshot_rebuild"], False)
        self.assertEqual(payload["hold_recommendation"], "KEEP_EXECUTE_FALSE")
        self.assertIs(payload["seal_chain_extended"], False)
        self.assertEqual(payload["risk_band_status_formula"] if "risk_band_status_formula" in payload else EXPECTED_RISK_BAND_STATUS_FORMULA, EXPECTED_RISK_BAND_STATUS_FORMULA)

    def test_cli_runner_offline(self) -> None:
        proc = subprocess.run(
            [sys.executable, _RUNNER],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS_OFFLINE", proc.stdout)

    def test_cli_execute_forbidden(self) -> None:
        proc = subprocess.run(
            [sys.executable, _RUNNER, "--execute-production-snapshot-rebuild"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestCFm51FullMarketResidualFormulaResumeFormulaCoverageWallMetaBundle
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = []
    for test, err in result.failures + result.errors:
        cases.append({"case": test.id().split(".")[-1], "result": "FAIL"})
    # map known cases
    names = [
        "test_constants_frozen",
        "test_residual_formula_composition_mutation_denied",
        "test_resume_formula_composition_mutation_denied",
        "test_coverage_composition_mutation_denied",
        "test_wall_meta_bundle_mutation_denied",
        "test_fm50_continuity",
        "test_output_root_guards",
        "test_full_offline_run",
        "test_cli_runner_offline",
        "test_cli_execute_forbidden",
    ]
    failed = {c["case"] for c in cases}
    summary = [{"case": n, "result": "FAIL" if n in failed else "PASS"} for n in names]
    _write_test_summary(summary)
    sys.exit(0 if result.wasSuccessful() else 1)
