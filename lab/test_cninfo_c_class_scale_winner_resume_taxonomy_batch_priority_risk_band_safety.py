"""
CNINFO C-class — 规模 winner/resume-taxonomy/batch-priority/risk-band 单测
（离线 · CNINFO=0 · C-FM-35）。

运行：
    python3 lab/test_cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety.py
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

from cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    EXPECTED_COMBINED_DRYRUN_COVERAGE,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_HARVEST_ADDITIVE,
    EXPECTED_HARVEST_UNIQUE_UNION,
    EXPECTED_OVERLAP_DELTA,
    EXPECTED_PARTIAL_RISK_BANDS,
    EXPECTED_RESUME_IMPROVED,
    EXPECTED_RESUME_SAME,
    EXPECTED_RESUME_WORSE,
    EXPECTED_RESIDUAL_SAFETY_COVERAGE,
    EXPECTED_SCALE_TIER_COUNT,
    EXPECTED_SURFACE_HARVEST_DELTA_N,
    EXPECTED_SURFACE_UNIQUE,
    EXPECTED_UNION_COMPLETE,
    EXPECTED_UNION_FAILED,
    EXPECTED_UNION_PARTIAL,
    EXPECTED_WINNER_MAP_SHA256,
    FROZEN_BATCH_PRIORITY_ORDER_FREEZE_FP_SHA256,
    FROZEN_PARTIAL_RISK_BAND_CARDINALITY_FP_SHA256,
    FROZEN_RESUME_TAXONOMY_CODESET_SHA256_LOCK_FP_SHA256,
    FROZEN_WINNER_MAP_SHA256_LOCK_FP_SHA256,
    WinnerResumeTaxonomyBatchPriorityRiskBandPaths,
    assert_fm35_output_root,
    build_batch_priority_order_freeze_rows,
    build_fm34_continuity_rows,
    build_partial_risk_band_cardinality_freeze_rows,
    build_resume_taxonomy_codeset_sha256_lock_rows,
    build_winner_map_sha256_lock_rows,
    evaluate_batch_priority_mutation,
    evaluate_partial_risk_band_mutation,
    evaluate_resume_taxonomy_codeset_mutation,
    evaluate_winner_map_mutation,
    fingerprint_winner_map_sha256_lock,
    run_scale_winner_resume_taxonomy_batch_priority_risk_band_safety,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR,
    "run_cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety.py",
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-35 Scale Winner Resume-Taxonomy Batch-Priority Risk-Band — Test Summary",
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
            "c_fm_35_scale_winner_resume_taxonomy_batch_priority_risk_band_safety_test_gate = "
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
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestCFm35WinnerResumeTaxonomyBatchPriorityRiskBand(unittest.TestCase):
    def test_constants_frozen(self) -> None:
        self.assertEqual(EXPECTED_SURFACE_HARVEST_DELTA_N, 2)
        self.assertEqual(EXPECTED_COMBINED_DRYRUN_COVERAGE, 1053)
        self.assertEqual(EXPECTED_UNION_COMPLETE, 2134)
        self.assertEqual(EXPECTED_UNION_PARTIAL, 106)
        self.assertEqual(EXPECTED_UNION_FAILED, 9)
        self.assertEqual(EXPECTED_OVERLAP_DELTA, 12)
        self.assertEqual(EXPECTED_RESIDUAL_SAFETY_COVERAGE, 117)
        self.assertEqual(EXPECTED_RESUME_IMPROVED, 28)
        self.assertEqual(EXPECTED_RESUME_SAME, 1)
        self.assertEqual(EXPECTED_RESUME_WORSE, 0)
        self.assertEqual(
            EXPECTED_PARTIAL_RISK_BANDS,
            {"p35_heavy": 75, "p3_mid": 14, "p2_mid": 12, "fu_light": 5},
        )

    def test_winner_map_mutation_denied(self) -> None:
        mut = evaluate_winner_map_mutation(proposed_sha256="a" * 64)
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_winner_map_sha256_lock_rows(
            WinnerResumeTaxonomyBatchPriorityRiskBandPaths()
        )
        self.assertTrue(checks["winner_map_sha256_lock_all_pass"])
        self.assertEqual(meta["fingerprint"], FROZEN_WINNER_MAP_SHA256_LOCK_FP_SHA256)
        self.assertEqual(meta["winner_map_sha256"], EXPECTED_WINNER_MAP_SHA256)
        fp, _doc = fingerprint_winner_map_sha256_lock()
        self.assertEqual(fp, FROZEN_WINNER_MAP_SHA256_LOCK_FP_SHA256)

    def test_resume_taxonomy_mutation_denied(self) -> None:
        mut = evaluate_resume_taxonomy_codeset_mutation(
            bucket="improved", proposed_sha256="b" * 64
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_resume_taxonomy_codeset_sha256_lock_rows(
            WinnerResumeTaxonomyBatchPriorityRiskBandPaths()
        )
        self.assertTrue(checks["resume_taxonomy_codeset_sha256_lock_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_RESUME_TAXONOMY_CODESET_SHA256_LOCK_FP_SHA256
        )

    def test_batch_priority_mutation_denied(self) -> None:
        mut = evaluate_batch_priority_mutation(
            proposed_priority=["p35", "h863", "p3", "p2", "fu"], action="reorder"
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_batch_priority_order_freeze_rows(
            WinnerResumeTaxonomyBatchPriorityRiskBandPaths()
        )
        self.assertTrue(checks["batch_priority_order_freeze_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_BATCH_PRIORITY_ORDER_FREEZE_FP_SHA256
        )

    def test_partial_risk_band_mutation_denied(self) -> None:
        inflated = dict(EXPECTED_PARTIAL_RISK_BANDS)
        inflated["p35_heavy"] = 76
        mut = evaluate_partial_risk_band_mutation(proposed_bands=inflated)
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_partial_risk_band_cardinality_freeze_rows(
            WinnerResumeTaxonomyBatchPriorityRiskBandPaths()
        )
        self.assertTrue(checks["partial_risk_band_cardinality_freeze_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_PARTIAL_RISK_BAND_CARDINALITY_FP_SHA256
        )

    def test_fm34_continuity(self) -> None:
        rows, checks = build_fm34_continuity_rows(
            WinnerResumeTaxonomyBatchPriorityRiskBandPaths()
        )
        self.assertTrue(checks.get("fm34_continuity_all_pass"), rows[-1])

    def test_output_root_guards(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            assert_fm35_output_root(
                "outputs/validation/"
                "_mock_c_fm34_scale_surface_delta_combined_dryrun_cross_identity_partition_codeset_safety"
            )
        self.assertIn(FROZEN_MOCK_COHORT_WRITE_FORBIDDEN, str(ctx.exception))
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(
                AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL
            )
        ok = assert_fm35_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertTrue(ok)

    def test_full_offline_run(self) -> None:
        result = run_scale_winner_resume_taxonomy_batch_priority_risk_band_safety()
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertIs(result["approved_for_snapshot_rebuild"], False)
        self.assertEqual(result["hold_recommendation"], "KEEP_EXECUTE_FALSE")
        self.assertEqual(
            result["combined_dryrun_coverage"], EXPECTED_COMBINED_DRYRUN_COVERAGE
        )
        self.assertEqual(
            result["surface_harvest_delta_n"], EXPECTED_SURFACE_HARVEST_DELTA_N
        )
        self.assertEqual(result["union_complete"], EXPECTED_UNION_COMPLETE)
        self.assertEqual(result["overlap_delta"], EXPECTED_OVERLAP_DELTA)
        self.assertEqual(result["resume_improved"], EXPECTED_RESUME_IMPROVED)
        packet = os.path.join(BASE_DIR, result["packet_path"])
        with open(packet, encoding="utf-8") as fh:
            doc = json.load(fh)
        self.assertEqual(doc["task_id"], "C-FM-35")
        self.assertFalse(doc["approved_for_snapshot_rebuild"])

    def test_cli_runner_offline(self) -> None:
        tmp = os.path.join(
            BASE_DIR,
            "outputs/validation/_mock_c_fm35_cli_test_tmp",
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
        TestCFm35WinnerResumeTaxonomyBatchPriorityRiskBand
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = []
    for test, err in result.failures + result.errors:
        cases.append({"case": test.id().split(".")[-1], "result": "FAIL"})
    if result.wasSuccessful():
        for name in [
            "test_constants_frozen",
            "test_winner_map_mutation_denied",
            "test_resume_taxonomy_mutation_denied",
            "test_batch_priority_mutation_denied",
            "test_partial_risk_band_mutation_denied",
            "test_fm34_continuity",
            "test_output_root_guards",
            "test_full_offline_run",
            "test_cli_runner_offline",
            "test_cli_execute_forbidden",
        ]:
            cases.append({"case": name, "result": "PASS"})
    _write_test_summary(cases)
    sys.exit(0 if result.wasSuccessful() else 1)
