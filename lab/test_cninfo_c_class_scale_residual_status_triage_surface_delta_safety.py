"""
CNINFO C-class — 规模 residual / surface-delta / resume-same hold 单测
（离线 · CNINFO=0 · C-FM-26）。

运行：
    python3 lab/test_cninfo_c_class_scale_residual_status_triage_surface_delta_safety.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_scale_residual_status_triage_surface_delta_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_FAILED_CODES,
    EXPECTED_HARVEST_UNIQUE_UNION,
    EXPECTED_RESUME_SAME,
    EXPECTED_SCALE_TIER_COUNT,
    EXPECTED_SURFACE_HARVEST_DELTA_N,
    EXPECTED_SURFACE_UNIQUE,
    EXPECTED_UNION_COMPLETE,
    EXPECTED_UNION_FAILED,
    EXPECTED_UNION_PARTIAL,
    FROZEN_FAILED_RESIDUAL_FP_SHA256,
    FROZEN_PARTIAL_RESIDUAL_FP_SHA256,
    FROZEN_RESUME_SAME_HOLD_FP_SHA256,
    FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256,
    ResidualTriagePaths,
    assert_fm26_output_root,
    build_failed_residual_ledger_rows,
    build_fm25_continuity_rows,
    build_frozen_mock_isolation_rows,
    build_partial_residual_ledger_rows,
    build_resume_same_hold_rows,
    build_surface_harvest_delta_rows,
    fingerprint_failed_residual_ledger,
    fingerprint_scale_matrix,
    load_union_status_maps,
    compute_union_status_and_winners,
    run_scale_residual_status_triage_surface_delta_safety,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_scale_residual_status_triage_surface_delta_safety.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_residual_status_triage_surface_delta_safety_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-26 Scale Residual Status Triage Surface Delta Safety — Test Summary",
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
            "c_fm_26_scale_residual_status_triage_surface_delta_safety_test_gate = "
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
            f"union_complete = {EXPECTED_UNION_COMPLETE}",
            f"union_partial = {EXPECTED_UNION_PARTIAL}",
            f"union_failed = {EXPECTED_UNION_FAILED}",
            f"surface_harvest_delta_n = {EXPECTED_SURFACE_HARVEST_DELTA_N}",
            f"resume_same = {EXPECTED_RESUME_SAME}",
            f"surface_unique = {EXPECTED_SURFACE_UNIQUE}",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestScaleResidualStatusTriageSurfaceDeltaSafety(unittest.TestCase):
    def test_output_root_requires_mock_and_not_frozen(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_fm26_output_root("outputs/validation/cninfo_c_class_not_mock")
        with self.assertRaises(RuntimeError):
            assert_fm26_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        with self.assertRaisesRegex(
            RuntimeError, FROZEN_MOCK_COHORT_WRITE_FORBIDDEN
        ):
            assert_fm26_output_root(
                "outputs/validation/"
                "_mock_c_fm25_scale_overlap_status_rollup_resume_delta_safety"
            )
        norm = assert_fm26_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm26", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_residual_status_constants(self) -> None:
        self.assertEqual(EXPECTED_HARVEST_UNIQUE_UNION, 2249)
        self.assertEqual(EXPECTED_UNION_COMPLETE, 2134)
        self.assertEqual(EXPECTED_UNION_PARTIAL, 106)
        self.assertEqual(EXPECTED_UNION_FAILED, 9)
        self.assertEqual(EXPECTED_SURFACE_HARVEST_DELTA_N, 2)
        self.assertEqual(EXPECTED_RESUME_SAME, 1)
        self.assertEqual(EXPECTED_SURFACE_UNIQUE, 2251)
        self.assertEqual(len(EXPECTED_FAILED_CODES), 9)

    def test_failed_residual_fingerprint_frozen(self) -> None:
        paths = ResidualTriagePaths()
        status_maps = load_union_status_maps(paths)
        union_status, winning = compute_union_status_and_winners(status_maps)
        failed = sorted(c for c, s in union_status.items() if s == "failed")
        fp, doc = fingerprint_failed_residual_ledger(
            failed_codes=failed, winning_batch=winning
        )
        self.assertEqual(fp, FROZEN_FAILED_RESIDUAL_FP_SHA256)
        self.assertEqual(set(doc["failed_codes"]), EXPECTED_FAILED_CODES)
        self.assertEqual(doc["failed_winning_batch_counts"], {"p3": 3, "p35": 6})

    def test_fm25_continuity_and_new_layers(self) -> None:
        paths = ResidualTriagePaths()
        _r, c = build_fm25_continuity_rows(paths)
        self.assertTrue(c["fm25_continuity_all_pass"])
        _r2, c2, m2 = build_failed_residual_ledger_rows(paths)
        self.assertTrue(c2["failed_residual_code_ledger_all_pass"])
        self.assertEqual(m2["fingerprint"], FROZEN_FAILED_RESIDUAL_FP_SHA256)
        _r3, c3, m3 = build_partial_residual_ledger_rows(paths)
        self.assertTrue(c3["partial_residual_code_ledger_all_pass"])
        self.assertEqual(m3["fingerprint"], FROZEN_PARTIAL_RESIDUAL_FP_SHA256)
        self.assertEqual(len(m3["partial_codes"]), 106)
        _r4, c4, m4 = build_surface_harvest_delta_rows(paths)
        self.assertTrue(c4["surface_harvest_delta_recon_all_pass"])
        self.assertEqual(m4["fingerprint"], FROZEN_SURFACE_HARVEST_DELTA_FP_SHA256)
        self.assertEqual(m4["delta_codes"], ["000037", "000055"])
        _r5, c5, m5 = build_resume_same_hold_rows(paths)
        self.assertTrue(c5["resume_same_hold_all_pass"])
        self.assertEqual(m5["fingerprint"], FROZEN_RESUME_SAME_HOLD_FP_SHA256)
        self.assertEqual(m5["same_codes"], ["301212"])

    def test_frozen_isolation_blocks_mock27_allows_mock28(self) -> None:
        run_scale_residual_status_triage_surface_delta_safety(
            paths=ResidualTriagePaths(
                output_root_rel="outputs/validation/_mock_c_fm26_cli_test_tmp"
            )
        )
        _rows, checks = build_frozen_mock_isolation_rows(
            ResidualTriagePaths(
                output_root_rel="outputs/validation/_mock_c_fm26_cli_test_tmp"
            )
        )
        self.assertTrue(checks["frozen_mock_isolation_all_pass"], msg=str(checks))
        self.assertTrue(checks["mock27_still_frozen"])
        self.assertTrue(checks["frozen_allow_mock28"])

    def test_fingerprint_matrix_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "l",
                "cohort_id": "*",
                "root_id": "",
                "path": "",
                "expected": "e",
                "observed": "x",
                "ok": "yes",
                "notes": "ok",
            }
        ]
        fp1 = fingerprint_scale_matrix(rows)
        fp2 = fingerprint_scale_matrix(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])

    def test_full_scale_pass_isolated_mock(self) -> None:
        result = run_scale_residual_status_triage_surface_delta_safety(
            paths=ResidualTriagePaths(
                output_root_rel="outputs/validation/_mock_c_fm26_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertEqual(result["scale_tier_count"], EXPECTED_SCALE_TIER_COUNT)
        self.assertEqual(
            result["company_coverage_sum"], EXPECTED_COMPANY_COVERAGE_SUM
        )
        self.assertEqual(
            result["harvest_unique_union"], EXPECTED_HARVEST_UNIQUE_UNION
        )
        self.assertEqual(result["union_complete"], EXPECTED_UNION_COMPLETE)
        self.assertEqual(result["union_partial"], EXPECTED_UNION_PARTIAL)
        self.assertEqual(result["union_failed"], EXPECTED_UNION_FAILED)
        self.assertEqual(
            result["surface_harvest_delta_n"], EXPECTED_SURFACE_HARVEST_DELTA_N
        )
        self.assertEqual(result["resume_same"], EXPECTED_RESUME_SAME)
        self.assertEqual(result["surface_unique"], EXPECTED_SURFACE_UNIQUE)
        self.assertEqual(result["resume_same_codes"], ["301212"])
        self.assertFalse(result["execute_production_snapshot_rebuild"])
        self.assertFalse(result["approved_for_snapshot_rebuild"])
        self.assertFalse(result["ready_for_execute"])
        self.assertFalse(result["seal_chain_extended"])
        self.assertEqual(result["hold_recommendation"], "KEEP_EXECUTE_FALSE")
        self.assertTrue(result["idle_not_required_while_awaiting"])
        self.assertTrue(result["mock_root_is_isolated"])
        with open(
            os.path.join(BASE_DIR, result["battery_path"]), encoding="utf-8"
        ) as fh:
            battery = json.load(fh)
        self.assertEqual(battery["gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm25_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm26_gate"], "PASS_OFFLINE")
        self.assertFalse(battery["seal_chain_extended"])
        self.assertEqual(
            battery["layer_gates"]["failed_residual_code_ledger"], "PASS_OFFLINE"
        )
        self.assertEqual(
            battery["layer_gates"]["surface_harvest_delta_recon"], "PASS_OFFLINE"
        )

    def test_cli_execute_forbidden(self) -> None:
        proc = subprocess.run(
            [sys.executable, _RUNNER, "--execute"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("EXECUTE_PRODUCTION_SNAPSHOT_REBUILD_FORBIDDEN", proc.stderr)

    def test_cninfo_not_called(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            run_scale_residual_status_triage_surface_delta_safety(
                paths=ResidualTriagePaths(
                    output_root_rel=(
                        "outputs/validation/_mock_c_fm26_unit_cninfo_probe"
                    )
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(
        TestScaleResidualStatusTriageSurfaceDeltaSafety
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {
            "case": "test_output_root_requires_mock_and_not_frozen",
            "result": "PASS",
        },
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {"case": "test_residual_status_constants", "result": "PASS"},
        {"case": "test_failed_residual_fingerprint_frozen", "result": "PASS"},
        {"case": "test_fm25_continuity_and_new_layers", "result": "PASS"},
        {
            "case": "test_frozen_isolation_blocks_mock27_allows_mock28",
            "result": "PASS",
        },
        {"case": "test_fingerprint_matrix_stable", "result": "PASS"},
        {"case": "test_full_scale_pass_isolated_mock", "result": "PASS"},
        {"case": "test_cli_execute_forbidden", "result": "PASS"},
        {"case": "test_cninfo_not_called", "result": "PASS"},
    ]
    if result.wasSuccessful():
        _write_test_summary(cases)
        raise SystemExit(0)
    raise SystemExit(1)
