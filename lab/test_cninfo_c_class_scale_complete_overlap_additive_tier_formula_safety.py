"""
CNINFO C-class — 规模 complete/overlap membership + additive/tier formula
单测（离线 · CNINFO=0 · C-FM-38）。

运行：
    python3 lab/test_cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety.py
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

from cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    EXPECTED_COMBINED_DRYRUN_COVERAGE,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_COMPLETE_CODES_SHA256,
    EXPECTED_DRY863_EXTRA,
    EXPECTED_FAILED_CODES,
    EXPECTED_HARVEST_ADDITIVE,
    EXPECTED_HARVEST_UNIQUE_UNION,
    EXPECTED_OVERLAP_CODES,
    EXPECTED_OVERLAP_CODES_SHA256,
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
    FROZEN_ADDITIVE_FORMULA_IDENTITY_LOCK_FP_SHA256,
    FROZEN_COMPLETE_CODES_MEMBERSHIP_FREEZE_FP_SHA256,
    FROZEN_OVERLAP_DELTA_MEMBERSHIP_FREEZE_FP_SHA256,
    FROZEN_TIER_COVERAGE_FORMULA_IDENTITY_LOCK_FP_SHA256,
    CompleteOverlapAdditiveTierFormulaPaths,
    assert_fm38_output_root,
    build_additive_formula_identity_lock_rows,
    build_complete_codes_membership_freeze_rows,
    build_fm37_continuity_rows,
    build_overlap_delta_membership_freeze_rows,
    build_tier_coverage_formula_identity_lock_rows,
    evaluate_additive_formula_mutation,
    evaluate_complete_codes_membership_mutation,
    evaluate_overlap_delta_membership_mutation,
    evaluate_tier_coverage_formula_mutation,
    fingerprint_complete_codes_membership_freeze,
    run_scale_complete_overlap_additive_tier_formula_safety,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR,
    "run_cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety.py",
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-38 Scale Complete/Overlap/Additive/Tier Formula — Test Summary",
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
            "c_fm_38_scale_complete_overlap_additive_tier_formula_safety_test_gate = "
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
            "residual_formula = 106+9+2=117",
            "union_formula = 2134+106+9=2249",
            "surface_formula = 2249+2=2251",
            "additive_formula = 2249+12=2261",
            "tier_coverage_formula = tiers=7;coverage_sum=3314",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestCFm38CompleteOverlapAdditiveTierFormula(unittest.TestCase):
    def test_constants_frozen(self) -> None:
        self.assertEqual(EXPECTED_SURFACE_HARVEST_DELTA_N, 2)
        self.assertEqual(EXPECTED_COMBINED_DRYRUN_COVERAGE, 1053)
        self.assertEqual(EXPECTED_UNION_COMPLETE, 2134)
        self.assertEqual(EXPECTED_UNION_PARTIAL, 106)
        self.assertEqual(EXPECTED_UNION_FAILED, 9)
        self.assertEqual(EXPECTED_OVERLAP_DELTA, 12)
        self.assertEqual(len(EXPECTED_OVERLAP_CODES), 12)
        self.assertEqual(EXPECTED_RESIDUAL_SAFETY_COVERAGE, 117)
        self.assertEqual(EXPECTED_SCALE_TIER_COUNT, 7)
        self.assertEqual(EXPECTED_COMPANY_COVERAGE_SUM, 3314)
        self.assertEqual(
            EXPECTED_HARVEST_UNIQUE_UNION + EXPECTED_OVERLAP_DELTA,
            EXPECTED_HARVEST_ADDITIVE,
        )
        self.assertEqual(
            EXPECTED_UNION_COMPLETE + EXPECTED_UNION_PARTIAL + EXPECTED_UNION_FAILED,
            EXPECTED_HARVEST_UNIQUE_UNION,
        )
        self.assertEqual(
            EXPECTED_HARVEST_UNIQUE_UNION + EXPECTED_SURFACE_HARVEST_DELTA_N,
            EXPECTED_SURFACE_UNIQUE,
        )
        self.assertEqual(EXPECTED_RESUME_IMPROVED, 28)
        self.assertEqual(EXPECTED_RESUME_SAME, 1)
        self.assertEqual(EXPECTED_RESUME_WORSE, 0)
        self.assertEqual(sorted(EXPECTED_DRY863_EXTRA), ["000037", "000055"])
        self.assertEqual(len(EXPECTED_FAILED_CODES), 9)
        self.assertEqual(
            EXPECTED_PARTIAL_RISK_BANDS,
            {"p35_heavy": 75, "p3_mid": 14, "p2_mid": 12, "fu_light": 5},
        )

    def test_complete_codes_membership_mutation_denied(self) -> None:
        mut = evaluate_complete_codes_membership_mutation(
            proposed_n=2135,
            proposed_sha256=EXPECTED_COMPLETE_CODES_SHA256,
            action="inject",
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_complete_codes_membership_freeze_rows(
            CompleteOverlapAdditiveTierFormulaPaths()
        )
        self.assertTrue(checks["complete_codes_membership_freeze_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_COMPLETE_CODES_MEMBERSHIP_FREEZE_FP_SHA256
        )
        fp, _doc = fingerprint_complete_codes_membership_freeze()
        self.assertEqual(fp, FROZEN_COMPLETE_CODES_MEMBERSHIP_FREEZE_FP_SHA256)

    def test_overlap_delta_membership_mutation_denied(self) -> None:
        mut = evaluate_overlap_delta_membership_mutation(
            proposed_codes=sorted(EXPECTED_OVERLAP_CODES) + ["999999"], action="inject"
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_overlap_delta_membership_freeze_rows(
            CompleteOverlapAdditiveTierFormulaPaths()
        )
        self.assertTrue(checks["overlap_delta_membership_freeze_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_OVERLAP_DELTA_MEMBERSHIP_FREEZE_FP_SHA256
        )
        self.assertEqual(meta["overlap_codes_sha256"], EXPECTED_OVERLAP_CODES_SHA256)

    def test_additive_formula_mutation_denied(self) -> None:
        mut = evaluate_additive_formula_mutation(
            proposed_unique=2250, proposed_additive=2261, proposed_overlap=12
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_additive_formula_identity_lock_rows(
            CompleteOverlapAdditiveTierFormulaPaths()
        )
        self.assertTrue(checks["additive_formula_identity_lock_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_ADDITIVE_FORMULA_IDENTITY_LOCK_FP_SHA256
        )

    def test_tier_coverage_formula_mutation_denied(self) -> None:
        mut = evaluate_tier_coverage_formula_mutation(
            proposed_tiers=8, proposed_coverage_sum=3314
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_tier_coverage_formula_identity_lock_rows(
            CompleteOverlapAdditiveTierFormulaPaths()
        )
        self.assertTrue(checks["tier_coverage_formula_identity_lock_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_TIER_COVERAGE_FORMULA_IDENTITY_LOCK_FP_SHA256
        )

    def test_fm37_continuity(self) -> None:
        rows, checks = build_fm37_continuity_rows(
            CompleteOverlapAdditiveTierFormulaPaths()
        )
        self.assertTrue(checks.get("fm37_continuity_all_pass"), rows[-1])

    def test_output_root_guards(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            assert_fm38_output_root(
                "outputs/validation/"
                "_mock_c_fm37_scale_improved_partial_surface_delta_union_partition_formula_safety"
            )
        self.assertIn(FROZEN_MOCK_COHORT_WRITE_FORBIDDEN, str(ctx.exception))
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(
                AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL
            )
        ok = assert_fm38_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertTrue(ok)

    def test_full_offline_run(self) -> None:
        result = run_scale_complete_overlap_additive_tier_formula_safety()
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
        self.assertEqual(result["residual_formula"], "106+9+2=117")
        self.assertEqual(result["union_formula"], "2134+106+9=2249")
        self.assertEqual(result["surface_formula"], "2249+2=2251")
        self.assertEqual(result["additive_formula"], "2249+12=2261")
        self.assertEqual(result["tier_coverage_formula"], "tiers=7;coverage_sum=3314")
        packet = os.path.join(BASE_DIR, result["packet_path"])
        with open(packet, encoding="utf-8") as fh:
            doc = json.load(fh)
        self.assertEqual(doc["task_id"], "C-FM-38")
        self.assertFalse(doc["approved_for_snapshot_rebuild"])

    def test_cli_runner_offline(self) -> None:
        tmp = os.path.join(
            BASE_DIR,
            "outputs/validation/_mock_c_fm38_cli_test_tmp",
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
        TestCFm38CompleteOverlapAdditiveTierFormula
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = []
    for test, err in result.failures + result.errors:
        cases.append({"case": test.id().split(".")[-1], "result": "FAIL"})
    if result.wasSuccessful():
        for name in [
            "test_constants_frozen",
            "test_complete_codes_membership_mutation_denied",
            "test_overlap_delta_membership_mutation_denied",
            "test_additive_formula_mutation_denied",
            "test_tier_coverage_formula_mutation_denied",
            "test_fm37_continuity",
            "test_output_root_guards",
            "test_full_offline_run",
            "test_cli_runner_offline",
            "test_cli_execute_forbidden",
        ]:
            cases.append({"case": name, "result": "PASS"})
    _write_test_summary(cases)
    sys.exit(0 if result.wasSuccessful() else 1)
