"""
CNINFO C-class — 规模 resume-improved / surface / additive / tier-coverage 单测
（离线 · CNINFO=0 · C-FM-32）。

运行：
    python3 lab/test_cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety.py
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

from cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_HARVEST_ADDITIVE,
    EXPECTED_HARVEST_UNIQUE_UNION,
    EXPECTED_OVERLAP_DELTA,
    EXPECTED_RESUME_IMPROVED,
    EXPECTED_RESUME_IMPROVED_CODES_SHA256,
    EXPECTED_RESUME_SAME,
    EXPECTED_RESUME_WORSE,
    EXPECTED_SCALE_TIER_COUNT,
    EXPECTED_SURFACE_UNIQUE,
    EXPECTED_UNION_COMPLETE,
    EXPECTED_UNION_FAILED,
    EXPECTED_UNION_PARTIAL,
    EXPECTED_RESIDUAL_SAFETY_COVERAGE,
    FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256,
    FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256,
    FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256,
    FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256,
    ResumeImprovedSurfaceAdditiveTierPaths,
    assert_fm32_output_root,
    build_fm31_continuity_rows,
    build_harvest_additive_cardinality_freeze_rows,
    build_scale_tier_coverage_sum_invariant_rows,
    build_surface_uniqueness_cardinality_freeze_rows,
    evaluate_harvest_additive_mutation,
    evaluate_resume_improved_write,
    evaluate_scale_tier_coverage_mutation,
    evaluate_surface_cardinality_mutation,
    evaluate_surface_membership_change,
    fingerprint_resume_improved_write_boundary,
    run_scale_resume_improved_surface_additive_tier_coverage_safety,
    _load_resume_improved_codes,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR,
    "run_cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety.py",
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_resume_improved_surface_additive_tier_coverage_safety_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-32 Scale Resume-Improved Surface Additive Tier Coverage — Test Summary",
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
            "c_fm_32_scale_resume_improved_surface_additive_tier_coverage_safety_test_gate = "
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
            f"union_complete = {EXPECTED_UNION_COMPLETE}",
            f"union_partial = {EXPECTED_UNION_PARTIAL}",
            f"union_failed = {EXPECTED_UNION_FAILED}",
            f"overlap_delta = {EXPECTED_OVERLAP_DELTA}",
            f"resume_improved = {EXPECTED_RESUME_IMPROVED}",
            f"resume_same = {EXPECTED_RESUME_SAME}",
            f"resume_worse = {EXPECTED_RESUME_WORSE}",
            f"residual_safety_coverage = {EXPECTED_RESIDUAL_SAFETY_COVERAGE}",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestCFm32ResumeImprovedSurfaceAdditiveTier(unittest.TestCase):
    def test_constants_frozen(self) -> None:
        self.assertEqual(EXPECTED_RESUME_IMPROVED, 28)
        self.assertEqual(EXPECTED_SURFACE_UNIQUE, 2251)
        self.assertEqual(EXPECTED_HARVEST_ADDITIVE, 2261)
        self.assertEqual(EXPECTED_HARVEST_UNIQUE_UNION, 2249)
        self.assertEqual(EXPECTED_SCALE_TIER_COUNT, 7)
        self.assertEqual(EXPECTED_COMPANY_COVERAGE_SUM, 3314)

    def test_resume_improved_fingerprint_frozen(self) -> None:
        paths = ResumeImprovedSurfaceAdditiveTierPaths()
        improved = _load_resume_improved_codes(paths)
        fp, doc = fingerprint_resume_improved_write_boundary(improved_codes=improved)
        self.assertEqual(len(improved), 28)
        self.assertEqual(doc["improved_codes_sha256"], EXPECTED_RESUME_IMPROVED_CODES_SHA256)
        self.assertEqual(fp, FROZEN_RESUME_IMPROVED_WRITE_BOUNDARY_FP_SHA256)

    def test_resume_improved_write_denied(self) -> None:
        paths = ResumeImprovedSurfaceAdditiveTierPaths()
        improved = _load_resume_improved_codes(paths)
        code = improved[0]
        for action in ("force_regress", "status_rewrite", "bucket_reclass"):
            d = evaluate_resume_improved_write(
                code=code, action=action, improved_codes=improved
            )
            self.assertIs(d["allowed"], False)

    def test_surface_cardinality_and_membership_denied(self) -> None:
        mut = evaluate_surface_cardinality_mutation(proposed_surface_unique=2250)
        self.assertIs(mut["mutation_allowed"], False)
        inj = evaluate_surface_membership_change(action="inject", code="999999")
        drop = evaluate_surface_membership_change(action="drop", code="000037")
        self.assertIs(inj["allowed"], False)
        self.assertIs(drop["allowed"], False)
        _rows, checks, meta = build_surface_uniqueness_cardinality_freeze_rows(
            ResumeImprovedSurfaceAdditiveTierPaths()
        )
        self.assertTrue(checks["surface_uniqueness_cardinality_freeze_all_pass"])
        self.assertEqual(meta["fingerprint"], FROZEN_SURFACE_UNIQUENESS_CARDINALITY_FP_SHA256)

    def test_harvest_additive_mutation_denied(self) -> None:
        mut = evaluate_harvest_additive_mutation(
            proposed_additive=2260, proposed_unique=2249
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_harvest_additive_cardinality_freeze_rows(
            ResumeImprovedSurfaceAdditiveTierPaths()
        )
        self.assertTrue(checks["harvest_additive_cardinality_freeze_all_pass"])
        self.assertEqual(meta["fingerprint"], FROZEN_HARVEST_ADDITIVE_CARDINALITY_FP_SHA256)

    def test_scale_tier_coverage_mutation_denied(self) -> None:
        mut = evaluate_scale_tier_coverage_mutation(
            proposed_tier_count=8, proposed_coverage_sum=3314
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_scale_tier_coverage_sum_invariant_rows(
            ResumeImprovedSurfaceAdditiveTierPaths()
        )
        self.assertTrue(checks["scale_tier_coverage_sum_invariant_all_pass"])
        self.assertEqual(meta["fingerprint"], FROZEN_SCALE_TIER_COVERAGE_SUM_FP_SHA256)

    def test_fm31_continuity(self) -> None:
        rows, checks = build_fm31_continuity_rows(ResumeImprovedSurfaceAdditiveTierPaths())
        self.assertTrue(checks.get("fm31_continuity_all_pass"), rows[-1])

    def test_output_root_guards(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            assert_fm32_output_root(
                "outputs/validation/"
                "_mock_c_fm31_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety"
            )
        self.assertIn(FROZEN_MOCK_COHORT_WRITE_FORBIDDEN, str(ctx.exception))
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(
                AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL
            )
        ok = assert_fm32_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertTrue(ok)

    def test_full_offline_run(self) -> None:
        result = run_scale_resume_improved_surface_additive_tier_coverage_safety()
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertIs(result["approved_for_snapshot_rebuild"], False)
        self.assertEqual(result["hold_recommendation"], "KEEP_EXECUTE_FALSE")
        self.assertEqual(result["resume_improved"], EXPECTED_RESUME_IMPROVED)
        self.assertEqual(result["surface_unique"], EXPECTED_SURFACE_UNIQUE)
        self.assertEqual(result["harvest_additive"], EXPECTED_HARVEST_ADDITIVE)
        self.assertEqual(result["scale_tier_count"], EXPECTED_SCALE_TIER_COUNT)
        self.assertEqual(result["company_coverage_sum"], EXPECTED_COMPANY_COVERAGE_SUM)
        packet = os.path.join(BASE_DIR, result["packet_path"])
        with open(packet, encoding="utf-8") as fh:
            doc = json.load(fh)
        self.assertEqual(doc["task_id"], "C-FM-32")
        self.assertFalse(doc["approved_for_snapshot_rebuild"])

    def test_cli_runner_offline(self) -> None:
        tmp = os.path.join(
            BASE_DIR,
            "outputs/validation/_mock_c_fm32_cli_test_tmp",
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
    suite = loader.loadTestsFromTestCase(TestCFm32ResumeImprovedSurfaceAdditiveTier)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    failed = {
        test.id().split(".")[-1]
        for test, _err in (result.failures + result.errors)
    }
    cases = []
    for test in loader.loadTestsFromTestCase(TestCFm32ResumeImprovedSurfaceAdditiveTier):
        name = test.id().split(".")[-1]
        cases.append(
            {"case": name, "result": "FAIL" if name in failed else "PASS"}
        )
    cases.sort(key=lambda x: x["case"])
    _write_test_summary(cases)
    raise SystemExit(0 if result.wasSuccessful() else 1)
