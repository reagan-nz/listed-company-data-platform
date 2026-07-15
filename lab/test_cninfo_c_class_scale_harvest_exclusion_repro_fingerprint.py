"""
CNINFO C-class — 规模 harvest/exclusion + 多 cohort 可复现指纹单测
（离线 · CNINFO=0 · C-FM-22）。

运行：
    python3 lab/test_cninfo_c_class_scale_harvest_exclusion_repro_fingerprint.py
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

from cninfo_c_class_scale_harvest_exclusion_repro_fingerprint import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    EXPECTED_COMPANY_COVERAGE_SUM,
    EXPECTED_SCALE_TIER_COUNT,
    FROZEN_PHASE35_500_FP_SHA256,
    ScalePaths,
    assert_fm22_output_root,
    build_frozen_mock_isolation_rows,
    build_multi_cohort_repro_fingerprint_rows,
    build_phase35_scale_dual_layer_rows,
    build_scale_lineage_registry_rows,
    default_scale_cohort_specs,
    fingerprint_scale_matrix,
    run_scale_harvest_exclusion_repro_fingerprint,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_scale_harvest_exclusion_repro_fingerprint.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_harvest_exclusion_repro_fingerprint_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-22 Scale Harvest-Exclusion Repro Fingerprint — Test Summary",
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
            "c_fm_22_scale_harvest_exclusion_repro_fingerprint_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "ready_for_execute = false",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "idle_not_required_while_awaiting = true",
            "hold_recommendation = KEEP_EXECUTE_FALSE",
            "seal_chain_extended = false",
            f"scale_tier_count = {EXPECTED_SCALE_TIER_COUNT}",
            f"company_coverage_sum = {EXPECTED_COMPANY_COVERAGE_SUM}",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestScaleHarvestExclusionReproFingerprint(unittest.TestCase):
    def test_output_root_requires_mock_and_not_frozen(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_fm22_output_root("outputs/validation/cninfo_c_class_not_mock")
        with self.assertRaises(RuntimeError):
            assert_fm22_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        with self.assertRaisesRegex(
            RuntimeError, FROZEN_MOCK_COHORT_WRITE_FORBIDDEN
        ):
            assert_fm22_output_root(
                "outputs/validation/"
                "_mock_c_fm21_nonseal_third_extension_post_commit_drift_recheck"
            )
        norm = assert_fm22_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm22", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_scale_specs_four_tiers_coverage_2414(self) -> None:
        specs = default_scale_cohort_specs()
        self.assertEqual(len(specs), EXPECTED_SCALE_TIER_COUNT)
        total = sum(int(s["company_count"]) for s in specs)
        self.assertEqual(total, EXPECTED_COMPANY_COVERAGE_SUM)
        ids = {s["cohort_id"] for s in specs}
        self.assertIn("fm01_isolated_dryrun_863", ids)
        self.assertIn("phase35_batch_500_harvest", ids)

    def test_scale_registry_and_repro_pass(self) -> None:
        _rows, checks, meta = build_scale_lineage_registry_rows()
        self.assertTrue(checks.get("scale_lineage_registry_all_pass"))
        self.assertEqual(meta["company_coverage_sum"], EXPECTED_COMPANY_COVERAGE_SUM)
        repro_rows, repro_checks, fps = build_multi_cohort_repro_fingerprint_rows(
            ScalePaths()
        )
        self.assertTrue(repro_checks.get("multi_cohort_repro_fingerprint_all_pass"))
        self.assertEqual(fps.get("phase35_500"), FROZEN_PHASE35_500_FP_SHA256)
        self.assertTrue(repro_rows)

    def test_phase35_dual_layer_pass(self) -> None:
        _rows, checks = build_phase35_scale_dual_layer_rows(ScalePaths())
        self.assertTrue(checks.get("phase35_holdout9_all_partial"))
        self.assertTrue(checks.get("harvest_863_disjoint_caveat10"))
        self.assertTrue(checks.get("scale_harvest_exclusion_dual_layer_all_pass"))

    def test_frozen_isolation_blocks_mock23_allows_mock24(self) -> None:
        rows, checks = build_frozen_mock_isolation_rows(
            ScalePaths(output_root_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL)
        )
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK23"))
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK8"))
        self.assertTrue(checks.get("frozen_allow_mock24"))
        self.assertTrue(checks.get("mock23_still_frozen"))
        self.assertTrue(checks.get("seal_mock8_still_frozen"))
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
        result = run_scale_harvest_exclusion_repro_fingerprint(
            paths=ScalePaths(
                output_root_rel="outputs/validation/_mock_c_fm22_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertEqual(result["scale_tier_count"], EXPECTED_SCALE_TIER_COUNT)
        self.assertEqual(
            result["company_coverage_sum"], EXPECTED_COMPANY_COVERAGE_SUM
        )
        self.assertFalse(result["execute_production_snapshot_rebuild"])
        self.assertFalse(result["approved_for_snapshot_rebuild"])
        self.assertFalse(result["ready_for_execute"])
        self.assertFalse(result["seal_chain_extended"])
        self.assertEqual(result["hold_recommendation"], "KEEP_EXECUTE_FALSE")
        self.assertTrue(result["idle_not_required_while_awaiting"])
        self.assertTrue(result["mock_root_is_isolated"])
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["matrix_path"]))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["fingerprint_path"]))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["battery_path"]))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["registry_path"]))
        )
        with open(
            os.path.join(BASE_DIR, result["battery_path"]), encoding="utf-8"
        ) as fh:
            battery = json.load(fh)
        self.assertEqual(battery["gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm21_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm22_gate"], "PASS_OFFLINE")
        self.assertFalse(battery["seal_chain_extended"])
        self.assertEqual(
            battery["layer_gates"]["scale_harvest_exclusion_dual_layer"],
            "PASS_OFFLINE",
        )
        self.assertEqual(
            battery["layer_gates"]["multi_cohort_repro_fingerprint"],
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
            run_scale_harvest_exclusion_repro_fingerprint(
                paths=ScalePaths(
                    output_root_rel=(
                        "outputs/validation/_mock_c_fm22_unit_cninfo_probe"
                    )
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestScaleHarvestExclusionReproFingerprint)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {
            "case": "test_output_root_requires_mock_and_not_frozen",
            "result": "PASS",
        },
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {"case": "test_scale_specs_four_tiers_coverage_2414", "result": "PASS"},
        {"case": "test_scale_registry_and_repro_pass", "result": "PASS"},
        {"case": "test_phase35_dual_layer_pass", "result": "PASS"},
        {
            "case": "test_frozen_isolation_blocks_mock23_allows_mock24",
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
