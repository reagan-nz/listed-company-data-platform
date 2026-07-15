"""
CNINFO C-class — 规模 union/overlap/residual/resume_same-worse 单测
（离线 · CNINFO=0 · C-FM-33）。

运行：
    python3 lab/test_cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety.py
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

from cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_HARVEST_ADDITIVE,
    EXPECTED_HARVEST_UNIQUE_UNION,
    EXPECTED_OVERLAP_DELTA,
    EXPECTED_RESUME_IMPROVED,
    EXPECTED_RESUME_SAME,
    EXPECTED_RESUME_SAME_CODES_SHA256,
    EXPECTED_RESUME_WORSE,
    EXPECTED_RESIDUAL_SAFETY_COVERAGE,
    EXPECTED_SCALE_TIER_COUNT,
    EXPECTED_SURFACE_UNIQUE,
    EXPECTED_UNION_COMPLETE,
    EXPECTED_UNION_FAILED,
    EXPECTED_UNION_PARTIAL,
    FROZEN_OVERLAP_DELTA_CARDINALITY_FP_SHA256,
    FROZEN_RESIDUAL_SAFETY_COVERAGE_LOCK_FP_SHA256,
    FROZEN_RESUME_SAME_WORSE_WRITE_BOUNDARY_FP_SHA256,
    FROZEN_UNION_STATUS_PARTITION_CARDINALITY_FP_SHA256,
    UnionPartitionOverlapResidualResumePaths,
    assert_fm33_output_root,
    build_fm32_continuity_rows,
    build_overlap_delta_cardinality_freeze_rows,
    build_residual_safety_coverage_lock_rows,
    build_resume_same_worse_write_boundary_rows,
    build_union_status_partition_cardinality_freeze_rows,
    evaluate_overlap_delta_mutation,
    evaluate_residual_safety_coverage_mutation,
    evaluate_resume_same_write,
    evaluate_resume_worse_inject,
    evaluate_union_partition_mutation,
    fingerprint_resume_same_worse_write_boundary,
    run_scale_union_partition_overlap_residual_resume_same_worse_safety,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR,
    "run_cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety.py",
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-33 Scale Union Partition Overlap Residual Resume Same/Worse — Test Summary",
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
            "c_fm_33_scale_union_partition_overlap_residual_resume_same_worse_safety_test_gate = "
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


class TestCFm33UnionPartitionOverlapResidualResumeSameWorse(unittest.TestCase):
    def test_constants_frozen(self) -> None:
        self.assertEqual(EXPECTED_UNION_COMPLETE, 2134)
        self.assertEqual(EXPECTED_UNION_PARTIAL, 106)
        self.assertEqual(EXPECTED_UNION_FAILED, 9)
        self.assertEqual(EXPECTED_OVERLAP_DELTA, 12)
        self.assertEqual(EXPECTED_RESIDUAL_SAFETY_COVERAGE, 117)
        self.assertEqual(EXPECTED_RESUME_SAME, 1)
        self.assertEqual(EXPECTED_RESUME_WORSE, 0)

    def test_union_partition_mutation_denied(self) -> None:
        mut = evaluate_union_partition_mutation(
            proposed_complete=2133, proposed_partial=107, proposed_failed=9
        )
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_union_status_partition_cardinality_freeze_rows(
            UnionPartitionOverlapResidualResumePaths()
        )
        self.assertTrue(checks["union_status_partition_cardinality_freeze_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_UNION_STATUS_PARTITION_CARDINALITY_FP_SHA256
        )

    def test_overlap_delta_mutation_denied(self) -> None:
        mut = evaluate_overlap_delta_mutation(proposed_overlap_delta=11)
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_overlap_delta_cardinality_freeze_rows(
            UnionPartitionOverlapResidualResumePaths()
        )
        self.assertTrue(checks["overlap_delta_cardinality_freeze_all_pass"])
        self.assertEqual(meta["fingerprint"], FROZEN_OVERLAP_DELTA_CARDINALITY_FP_SHA256)

    def test_residual_safety_coverage_mutation_denied(self) -> None:
        mut = evaluate_residual_safety_coverage_mutation(proposed_coverage=118)
        self.assertIs(mut["mutation_allowed"], False)
        _rows, checks, meta = build_residual_safety_coverage_lock_rows(
            UnionPartitionOverlapResidualResumePaths()
        )
        self.assertTrue(checks["residual_safety_coverage_lock_all_pass"])
        self.assertEqual(
            meta["fingerprint"], FROZEN_RESIDUAL_SAFETY_COVERAGE_LOCK_FP_SHA256
        )

    def test_resume_same_worse_write_denied(self) -> None:
        d = evaluate_resume_same_write(code="301212", action="force_improve")
        self.assertIs(d["allowed"], False)
        w = evaluate_resume_worse_inject()
        self.assertIs(w["allowed"], False)
        fp, doc = fingerprint_resume_same_worse_write_boundary()
        self.assertEqual(fp, FROZEN_RESUME_SAME_WORSE_WRITE_BOUNDARY_FP_SHA256)
        self.assertEqual(doc["same_codes"], ["301212"])
        _rows, checks, meta = build_resume_same_worse_write_boundary_rows(
            UnionPartitionOverlapResidualResumePaths()
        )
        self.assertTrue(checks["resume_same_worse_write_boundary_all_pass"])
        self.assertEqual(meta["same_codes_sha256"], EXPECTED_RESUME_SAME_CODES_SHA256)

    def test_fm32_continuity(self) -> None:
        rows, checks = build_fm32_continuity_rows(
            UnionPartitionOverlapResidualResumePaths()
        )
        self.assertTrue(checks.get("fm32_continuity_all_pass"), rows[-1])

    def test_output_root_guards(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            assert_fm33_output_root(
                "outputs/validation/"
                "_mock_c_fm32_scale_resume_improved_surface_additive_tier_coverage_safety"
            )
        self.assertIn(FROZEN_MOCK_COHORT_WRITE_FORBIDDEN, str(ctx.exception))
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(
                AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL
            )
        ok = assert_fm33_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertTrue(ok)

    def test_full_offline_run(self) -> None:
        result = run_scale_union_partition_overlap_residual_resume_same_worse_safety()
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertIs(result["approved_for_snapshot_rebuild"], False)
        self.assertEqual(result["hold_recommendation"], "KEEP_EXECUTE_FALSE")
        self.assertEqual(result["union_complete"], EXPECTED_UNION_COMPLETE)
        self.assertEqual(result["union_partial"], EXPECTED_UNION_PARTIAL)
        self.assertEqual(result["union_failed"], EXPECTED_UNION_FAILED)
        self.assertEqual(result["overlap_delta"], EXPECTED_OVERLAP_DELTA)
        self.assertEqual(
            result["residual_safety_coverage"], EXPECTED_RESIDUAL_SAFETY_COVERAGE
        )
        self.assertEqual(result["resume_same"], EXPECTED_RESUME_SAME)
        self.assertEqual(result["resume_worse"], EXPECTED_RESUME_WORSE)
        packet = os.path.join(BASE_DIR, result["packet_path"])
        with open(packet, encoding="utf-8") as fh:
            doc = json.load(fh)
        self.assertEqual(doc["task_id"], "C-FM-33")
        self.assertFalse(doc["approved_for_snapshot_rebuild"])

    def test_cli_runner_offline(self) -> None:
        tmp = os.path.join(
            BASE_DIR,
            "outputs/validation/_mock_c_fm33_cli_test_tmp",
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
        TestCFm33UnionPartitionOverlapResidualResumeSameWorse
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    failed = {
        test.id().split(".")[-1]
        for test, _err in (result.failures + result.errors)
    }
    cases = []
    for test in loader.loadTestsFromTestCase(
        TestCFm33UnionPartitionOverlapResidualResumeSameWorse
    ):
        name = test.id().split(".")[-1]
        cases.append(
            {"case": name, "result": "FAIL" if name in failed else "PASS"}
        )
    cases.sort(key=lambda x: x["case"])
    _write_test_summary(cases)
    raise SystemExit(0 if result.wasSuccessful() else 1)
