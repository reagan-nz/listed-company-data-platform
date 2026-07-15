"""
CNINFO C-class — 扩展多 batch 规模 repro + lineage 加固单测
（离线 · CNINFO=0 · C-FM-23）。

运行：
    python3 lab/test_cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py
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

from cninfo_c_class_scale_multi_batch_repro_lineage_hardening import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    EXPECTED_COMBINED_DRYRUN_COVERAGE,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_SCALE_TIER_COUNT,
    FROZEN_COMBINED_DRYRUN_1053_FP_SHA256,
    FROZEN_PHASE3_500_FP_SHA256,
    ExtendedScalePaths,
    assert_fm23_output_root,
    build_extended_multi_cohort_repro_fingerprint_rows,
    build_extended_scale_lineage_registry_rows,
    build_frozen_mock_isolation_rows,
    build_isolated_combined_dryrun_scale_rows,
    build_multi_batch_harvest_exclusion_dual_layer_rows,
    build_scale_lineage_hardening_rows,
    default_extended_scale_cohort_specs,
    fingerprint_combined_isolated_dryrun_scale,
    fingerprint_scale_matrix,
    run_scale_multi_batch_repro_lineage_hardening,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)
from cninfo_c_class_scale_harvest_exclusion_repro_fingerprint import (  # noqa: E402
    FROZEN_FM01_863_FP_SHA256,
    FROZEN_FM02_190_FP_SHA256,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_multi_batch_repro_lineage_hardening_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-23 Scale Multi-Batch Repro Lineage Hardening — Test Summary",
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
            "c_fm_23_scale_multi_batch_repro_lineage_hardening_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "ready_for_execute = false",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "idle_not_required_while_awaiting = true",
            "hold_recommendation = KEEP_EXECUTE_FALSE",
            "seal_chain_extended = false",
            f"scale_tier_count = {EXPECTED_SCALE_TIER_COUNT}",
            f"company_coverage_sum = {EXPECTED_COMPANY_COVERAGE_SUM}",
            f"combined_dryrun_coverage = {EXPECTED_COMBINED_DRYRUN_COVERAGE}",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestScaleMultiBatchReproLineageHardening(unittest.TestCase):
    def test_output_root_requires_mock_and_not_frozen(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_fm23_output_root("outputs/validation/cninfo_c_class_not_mock")
        with self.assertRaises(RuntimeError):
            assert_fm23_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        with self.assertRaisesRegex(
            RuntimeError, FROZEN_MOCK_COHORT_WRITE_FORBIDDEN
        ):
            assert_fm23_output_root(
                "outputs/validation/"
                "_mock_c_fm22_scale_harvest_exclusion_repro_fingerprint"
            )
        norm = assert_fm23_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm23", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_scale_specs_seven_tiers_coverage_3314(self) -> None:
        specs = default_extended_scale_cohort_specs()
        self.assertEqual(len(specs), EXPECTED_SCALE_TIER_COUNT)
        total = sum(int(s["company_count"]) for s in specs)
        self.assertEqual(total, EXPECTED_COMPANY_COVERAGE_SUM)
        ids = {s["cohort_id"] for s in specs}
        self.assertIn("phase3_batch_500_harvest", ids)
        self.assertIn("phase2_smoke_200_harvest", ids)
        self.assertIn("fuller_market_slice1_200_harvest", ids)

    def test_registry_repro_and_combined_dryrun_pass(self) -> None:
        _rows, checks, meta = build_extended_scale_lineage_registry_rows()
        self.assertTrue(checks.get("scale_lineage_registry_all_pass"))
        self.assertEqual(meta["company_coverage_sum"], EXPECTED_COMPANY_COVERAGE_SUM)
        repro_rows, repro_checks, fps = (
            build_extended_multi_cohort_repro_fingerprint_rows(ExtendedScalePaths())
        )
        self.assertTrue(repro_checks.get("multi_cohort_repro_fingerprint_all_pass"))
        self.assertEqual(fps.get("phase3_500"), FROZEN_PHASE3_500_FP_SHA256)
        self.assertTrue(repro_rows)
        dry_rows, dry_checks, dry_meta = build_isolated_combined_dryrun_scale_rows(
            ExtendedScalePaths()
        )
        self.assertTrue(dry_checks.get("isolated_combined_dryrun_scale_all_pass"))
        self.assertEqual(
            dry_meta["combined_fp"], FROZEN_COMBINED_DRYRUN_1053_FP_SHA256
        )
        self.assertEqual(
            fingerprint_combined_isolated_dryrun_scale(
                fm01_fp=FROZEN_FM01_863_FP_SHA256,
                fm02_fp=FROZEN_FM02_190_FP_SHA256,
            ),
            FROZEN_COMBINED_DRYRUN_1053_FP_SHA256,
        )
        self.assertTrue(dry_rows)

    def test_multi_batch_dual_layer_and_lineage_hardening(self) -> None:
        _rows, checks = build_multi_batch_harvest_exclusion_dual_layer_rows(
            ExtendedScalePaths()
        )
        self.assertTrue(checks.get("phase3_structural_counts"))
        self.assertTrue(checks.get("fuller_000003_partial"))
        self.assertTrue(
            checks.get("multi_batch_harvest_exclusion_dual_layer_all_pass")
        )
        _hrows, hchecks = build_scale_lineage_hardening_rows(ExtendedScalePaths())
        self.assertTrue(hchecks.get("fm22_packet_continuity"))
        self.assertTrue(hchecks.get("harvest_batch_union_1388"))
        self.assertTrue(hchecks.get("scale_lineage_hardening_all_pass"))

    def test_frozen_isolation_blocks_mock24_allows_mock25(self) -> None:
        # 先确保 MOCK25 已登记（完整 run 会登记；此处直接跑全量隔离检查）
        result = run_scale_multi_batch_repro_lineage_hardening(
            paths=ExtendedScalePaths(
                output_root_rel="outputs/validation/_mock_c_fm23_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        rows, checks = build_frozen_mock_isolation_rows(
            ExtendedScalePaths(output_root_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL)
        )
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK24"))
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK8"))
        self.assertTrue(checks.get("frozen_allow_mock25"))
        self.assertTrue(checks.get("mock24_still_frozen"))
        self.assertTrue(checks.get("frozen_mock_isolation_all_pass"))
        self.assertTrue(rows)

    def test_fingerprint_matrix_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "scale_lineage_registry",
                "cohort_id": "*",
                "root_id": "",
                "path": "",
                "expected": "x",
                "observed": "x",
                "ok": "yes",
                "notes": "ok",
            }
        ]
        fp1 = fingerprint_scale_matrix(rows)
        fp2 = fingerprint_scale_matrix(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])

    def test_full_scale_pass_isolated_mock(self) -> None:
        result = run_scale_multi_batch_repro_lineage_hardening(
            paths=ExtendedScalePaths(
                output_root_rel="outputs/validation/_mock_c_fm23_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertEqual(result["scale_tier_count"], EXPECTED_SCALE_TIER_COUNT)
        self.assertEqual(
            result["company_coverage_sum"], EXPECTED_COMPANY_COVERAGE_SUM
        )
        self.assertEqual(
            result["combined_dryrun_coverage"], EXPECTED_COMBINED_DRYRUN_COVERAGE
        )
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
        self.assertEqual(battery["fm22_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm23_gate"], "PASS_OFFLINE")
        self.assertFalse(battery["seal_chain_extended"])
        self.assertEqual(
            battery["layer_gates"]["isolated_combined_dryrun_scale"],
            "PASS_OFFLINE",
        )
        self.assertEqual(
            battery["layer_gates"]["scale_lineage_hardening"],
            "PASS_OFFLINE",
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
            run_scale_multi_batch_repro_lineage_hardening(
                paths=ExtendedScalePaths(
                    output_root_rel=(
                        "outputs/validation/_mock_c_fm23_unit_cninfo_probe"
                    )
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestScaleMultiBatchReproLineageHardening)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {
            "case": "test_output_root_requires_mock_and_not_frozen",
            "result": "PASS",
        },
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {
            "case": "test_scale_specs_seven_tiers_coverage_3314",
            "result": "PASS",
        },
        {
            "case": "test_registry_repro_and_combined_dryrun_pass",
            "result": "PASS",
        },
        {
            "case": "test_multi_batch_dual_layer_and_lineage_hardening",
            "result": "PASS",
        },
        {
            "case": "test_frozen_isolation_blocks_mock24_allows_mock25",
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
