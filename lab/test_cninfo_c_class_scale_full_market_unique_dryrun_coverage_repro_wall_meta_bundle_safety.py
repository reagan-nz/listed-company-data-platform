"""
CNINFO C-class — 规模 unique/dryrun/coverage/repro-wall-meta-bundle
单测（离线 · CNINFO=0 · C-FM-47）。

运行：
    python3 lab/test_cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety.py
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

from cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    EXPECTED_COMBINED_DRYRUN_COVERAGE,
    EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256,
    EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE,
    EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256,
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
    EXPECTED_SCALE_TIER_COUNT,
    EXPECTED_SURFACE_HARVEST_DELTA_N,
    EXPECTED_SURFACE_UNIQUE,
    EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256,
    EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA,
    EXPECTED_UNION_COMPLETE,
    EXPECTED_UNION_FAILED,
    EXPECTED_UNION_PARTIAL,
    EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256,
    EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA,
    FROZEN_COMPANY_COVERAGE_SCALE_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
    FROZEN_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256,
    FROZEN_COMBINED_DRYRUN_COHORT_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
    FROZEN_FULL_MARKET_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
    FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths,
    assert_fm47_output_root,
    build_company_coverage_scale_composition_identity_lock_rows,
    build_cross_full_market_scale_repro_wall_meta_bundle_identity_lock_rows,
    build_fm46_continuity_rows,
    build_combined_dryrun_cohort_composition_identity_lock_rows,
    build_full_market_unique_union_composition_identity_lock_rows,
    evaluate_company_coverage_scale_composition_mutation,
    evaluate_cross_full_market_scale_repro_wall_meta_bundle_mutation,
    evaluate_combined_dryrun_cohort_composition_mutation,
    evaluate_full_market_unique_union_composition_mutation,
    fingerprint_full_market_unique_union_composition_identity_lock,
    run_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR,
    "run_cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety.py",
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety_test_summary_20260716.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-47 Scale Lineage/Drift/Protected/Repro-Wall-Meta-Bundle — Test Summary",
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
            "c_fm_47_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety_test_gate = "
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
            f"full_market_unique_union_formula = {EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA}",
            f"combined_dryrun_cohort_formula = {EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA}",
            f"company_coverage_scale_formula = {EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA}",
            f"residual_formula = {EXPECTED_RESIDUAL_FORMULA}",
            f"resume_taxonomy_formula = {EXPECTED_RESUME_TAXONOMY_FORMULA}",
            f"risk_band_status_formula = {EXPECTED_RISK_BAND_STATUS_FORMULA}",
            f"full_market_unique_union_composition_sha256 = {EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256}",
            f"combined_dryrun_cohort_composition_sha256 = {EXPECTED_COMBINED_DRYRUN_COHORT_COMPOSITION_SHA256}",
            f"company_coverage_scale_composition_sha256 = {EXPECTED_COMPANY_COVERAGE_SCALE_COMPOSITION_SHA256}",
            f"cross_full_market_scale_repro_wall_meta_bundle_sha256 = "
            f"{EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256}",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestCFm47FullMarketUniqueDryrunCoverageReproWallMetaBundle(unittest.TestCase):
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
        self.assertEqual(EXPECTED_FULL_MARKET_UNIQUE_UNION_FORMULA, "unique=2249")
        self.assertEqual(EXPECTED_COMBINED_DRYRUN_COHORT_FORMULA, "combined_dryrun=1053")
        self.assertEqual(EXPECTED_COMPANY_COVERAGE_SCALE_FORMULA, "tiers=7;coverage_sum=3314")
        self.assertEqual(EXPECTED_RESIDUAL_FORMULA, "106+9+2=117")
        self.assertEqual(EXPECTED_RESUME_TAXONOMY_FORMULA, "28/1/0")
        self.assertEqual(EXPECTED_RISK_BAND_STATUS_FORMULA, "75/14/12/5")
        self.assertEqual(EXPECTED_RESUME_FORMULA, "28+1+0=29")
        self.assertEqual(
            len(EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE), 5
        )

    def test_full_market_unique_union_composition_mutation_denied(self) -> None:
        mut = evaluate_full_market_unique_union_composition_mutation(
            proposed_harvest_unique_union=2200,
            proposed_unique_union_composition_sha256="0" * 64,
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_full_market_unique_union_composition_identity_lock_rows(
            FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths()
        )
        self.assertTrue(
            checks["full_market_unique_union_composition_identity_lock_all_pass"]
        )
        self.assertEqual(
            meta["fingerprint"],
            FROZEN_FULL_MARKET_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
        )
        fp, _doc = fingerprint_full_market_unique_union_composition_identity_lock()
        self.assertEqual(
            fp, FROZEN_FULL_MARKET_UNIQUE_UNION_COMPOSITION_IDENTITY_LOCK_FP_SHA256
        )

    def test_combined_dryrun_cohort_composition_mutation_denied(self) -> None:
        mut = evaluate_combined_dryrun_cohort_composition_mutation(
            proposed_combined_dryrun_coverage=1000,
            proposed_combined_dryrun_composition_sha256="0" * 64,
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_combined_dryrun_cohort_composition_identity_lock_rows(
            FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths()
        )
        self.assertTrue(
            checks["combined_dryrun_cohort_composition_identity_lock_all_pass"]
        )
        self.assertEqual(
            meta["fingerprint"],
            FROZEN_COMBINED_DRYRUN_COHORT_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
        )

    def test_company_coverage_scale_composition_mutation_denied(self) -> None:
        mut = evaluate_company_coverage_scale_composition_mutation(
            proposed_scale_tier_count=6,
            proposed_company_coverage_sum=3000,
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_company_coverage_scale_composition_identity_lock_rows(
            FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths()
        )
        self.assertTrue(
            checks["company_coverage_scale_composition_identity_lock_all_pass"]
        )
        self.assertEqual(
            meta["fingerprint"],
            FROZEN_COMPANY_COVERAGE_SCALE_COMPOSITION_IDENTITY_LOCK_FP_SHA256,
        )

    def test_wall_meta_bundle_mutation_denied(self) -> None:
        mutated = {
            k: dict(v)
            for k, v in EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE.items()
        }
        mutated["full_market_unique_union_composition"] = {
            "formula": "unique=2000",
            "composition_sha256": EXPECTED_FULL_MARKET_UNIQUE_UNION_COMPOSITION_SHA256,
            "n": 2000,
        }
        mut = evaluate_cross_full_market_scale_repro_wall_meta_bundle_mutation(
            proposed_compositions=mutated
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = (
            build_cross_full_market_scale_repro_wall_meta_bundle_identity_lock_rows(
                FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths()
            )
        )
        self.assertTrue(
            checks[
                "cross_full_market_scale_repro_wall_meta_bundle_identity_lock_all_pass"
            ]
        )
        self.assertEqual(
            meta["fingerprint"],
            FROZEN_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_IDENTITY_LOCK_FP_SHA256,
        )

    def test_fm46_continuity(self) -> None:
        rows, checks = build_fm46_continuity_rows(
            FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths()
        )
        self.assertTrue(checks.get("fm46_continuity_all_pass"), rows[-1])

    def test_output_root_guards(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            assert_fm47_output_root(
                "outputs/validation/"
                "_mock_c_fm46_scale_lineage_drift_protected_repro_wall_meta_bundle_safety"
            )
        self.assertIn(FROZEN_MOCK_COHORT_WRITE_FORBIDDEN, str(ctx.exception))
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(
                AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL
            )
        ok = assert_fm47_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertTrue(ok)

    def test_full_offline_run(self) -> None:
        result = run_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety()
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertIs(result["approved_for_snapshot_rebuild"], False)
        self.assertEqual(result["hold_recommendation"], "KEEP_EXECUTE_FALSE")
        self.assertEqual(
            result["combined_dryrun_coverage"], EXPECTED_COMBINED_DRYRUN_COVERAGE
        )
        self.assertEqual(result["full_market_unique_union_formula"], "unique=2249")
        self.assertEqual(result["combined_dryrun_cohort_formula"], "combined_dryrun=1053")
        self.assertEqual(result["company_coverage_scale_formula"], "tiers=7;coverage_sum=3314")
        self.assertEqual(
            result["cross_full_market_scale_repro_wall_meta_bundle_sha256"],
            EXPECTED_CROSS_FULL_MARKET_SCALE_REPRO_WALL_META_BUNDLE_SHA256,
        )
        packet = os.path.join(BASE_DIR, result["packet_path"])
        with open(packet, encoding="utf-8") as fh:
            doc = json.load(fh)
        self.assertEqual(doc["task_id"], "C-FM-47")
        self.assertFalse(doc["approved_for_snapshot_rebuild"])

    def test_cli_runner_offline(self) -> None:
        tmp = os.path.join(
            BASE_DIR,
            "outputs/validation/_mock_c_fm47_cli_test_tmp",
        )
        proc = subprocess.run(
            [sys.executable, _RUNNER, "--output-root", tmp],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["gate"], "PASS_OFFLINE")
        self.assertEqual(payload["cninfo_calls"], 0)

    def test_cli_execute_forbidden(self) -> None:
        proc = subprocess.run(
            [sys.executable, _RUNNER, "--execute"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("EXECUTE_PRODUCTION_SNAPSHOT_REBUILD_FORBIDDEN", proc.stderr)


if __name__ == "__main__":
    loader = unittest.defaultTestLoader
    suite = loader.loadTestsFromTestCase(
        TestCFm47FullMarketUniqueDryrunCoverageReproWallMetaBundle
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = []
    for test, err in result.failures + result.errors:
        cases.append({"case": test.id().split(".")[-1], "result": "FAIL"})
    if result.wasSuccessful():
        for name in [
            "test_constants_frozen",
            "test_full_market_unique_union_composition_mutation_denied",
            "test_combined_dryrun_cohort_composition_mutation_denied",
            "test_company_coverage_scale_composition_mutation_denied",
            "test_wall_meta_bundle_mutation_denied",
            "test_fm46_continuity",
            "test_output_root_guards",
            "test_full_offline_run",
            "test_cli_runner_offline",
            "test_cli_execute_forbidden",
        ]:
            cases.append({"case": name, "result": "PASS"})
    _write_test_summary(cases)
    sys.exit(0 if result.wasSuccessful() else 1)
