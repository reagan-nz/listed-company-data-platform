"""
CNINFO C-class — 非 seal Cross-FM mock cohort 二次扩展单测（离线 · CNINFO=0 · C-FM-18）。

运行：
    python3 lab/test_cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension.py
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

from cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    SecondExtensionPaths,
    assert_fm18_output_root,
    build_frozen_mock_isolation_rows,
    build_nonseal_chain_anchor_rows,
    default_nonseal_second_extension_cohort_specs,
    fingerprint_second_extension_matrix,
    run_nonseal_cross_fm_mock_cohort_second_extension,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_cross_fm_mock_cohort_second_extension_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-18 Non-seal Cross-FM Mock Cohort Second Extension — Test Summary",
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
            "c_fm_18_nonseal_cross_fm_mock_cohort_second_extension_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "ready_for_execute = false",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "idle_not_required_while_awaiting = true",
            "hold_recommendation = KEEP_EXECUTE_FALSE",
            "seal_chain_extended = false",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestNonsealCrossFmMockCohortSecondExtension(unittest.TestCase):
    def test_output_root_requires_mock_and_not_frozen(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_fm18_output_root("outputs/validation/cninfo_c_class_not_mock")
        with self.assertRaises(RuntimeError):
            assert_fm18_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        with self.assertRaisesRegex(
            RuntimeError, FROZEN_MOCK_COHORT_WRITE_FORBIDDEN
        ):
            assert_fm18_output_root(
                "outputs/validation/"
                "_mock_c_fm17_nonseal_extension_human_decision_readiness_ledger"
            )
        norm = assert_fm18_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm18", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_second_extension_specs_include_fm13_to_fm17(self) -> None:
        specs = default_nonseal_second_extension_cohort_specs()
        ids = {s.cohort_id for s in specs}
        self.assertIn("fm05_cross_fm_mock_cohort_integrity", ids)
        self.assertIn("fm12_dryrun_fingerprint_lineage_isolation", ids)
        self.assertIn("fm13_nonseal_cross_fm_mock_cohort_extension", ids)
        self.assertIn("fm17_nonseal_extension_human_decision_readiness_ledger", ids)
        self.assertEqual(len(specs), 11)

    def test_nonseal_chain_anchors_pass(self) -> None:
        _rows, checks = build_nonseal_chain_anchor_rows()
        self.assertTrue(checks.get("anchor_extension_fp"))
        self.assertTrue(checks.get("anchor_readiness_fp"))
        self.assertTrue(checks.get("nonseal_chain_continuity_all_pass"))

    def test_frozen_isolation_blocks_mock19_allows_mock20(self) -> None:
        rows, checks = build_frozen_mock_isolation_rows(
            SecondExtensionPaths(output_root_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL)
        )
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK19"))
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK8"))
        self.assertTrue(checks.get("frozen_allow_mock20"))
        self.assertTrue(checks.get("mock19_still_frozen"))
        self.assertTrue(checks.get("seal_mock8_still_frozen"))
        self.assertTrue(checks.get("frozen_mock_isolation_all_pass"))
        self.assertTrue(rows)

    def test_fingerprint_matrix_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "nonseal_cohort_registry",
                "cohort_id": "*",
                "root_id": "",
                "path": "",
                "expected": "x",
                "observed": "x",
                "ok": "yes",
                "notes": "ok",
            }
        ]
        fp1 = fingerprint_second_extension_matrix(rows)
        fp2 = fingerprint_second_extension_matrix(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])

    def test_full_extension_pass_isolated_mock(self) -> None:
        result = run_nonseal_cross_fm_mock_cohort_second_extension(
            paths=SecondExtensionPaths(
                output_root_rel="outputs/validation/_mock_c_fm18_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertEqual(result["cohort_count"], 11)
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
        with open(
            os.path.join(BASE_DIR, result["battery_path"]), encoding="utf-8"
        ) as fh:
            battery = json.load(fh)
        self.assertEqual(battery["gate"], "PASS_OFFLINE")
        self.assertEqual(
            battery["layer_gates"]["nonseal_cohort_registry"], "PASS_OFFLINE"
        )
        self.assertEqual(
            battery["layer_gates"]["frozen_mock_isolation"], "PASS_OFFLINE"
        )
        self.assertEqual(
            battery["layer_gates"]["nonseal_chain_continuity"], "PASS_OFFLINE"
        )
        self.assertFalse(battery["seal_chain_extended"])
        self.assertEqual(battery["fm17_gate"], "PASS_OFFLINE")

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
            run_nonseal_cross_fm_mock_cohort_second_extension(
                paths=SecondExtensionPaths(
                    output_root_rel=(
                        "outputs/validation/_mock_c_fm18_unit_cninfo_probe"
                    )
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestNonsealCrossFmMockCohortSecondExtension)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {
            "case": "test_output_root_requires_mock_and_not_frozen",
            "result": "PASS",
        },
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {
            "case": "test_second_extension_specs_include_fm13_to_fm17",
            "result": "PASS",
        },
        {"case": "test_nonseal_chain_anchors_pass", "result": "PASS"},
        {
            "case": "test_frozen_isolation_blocks_mock19_allows_mock20",
            "result": "PASS",
        },
        {"case": "test_fingerprint_matrix_stable", "result": "PASS"},
        {"case": "test_full_extension_pass_isolated_mock", "result": "PASS"},
        {"case": "test_cli_execute_forbidden", "result": "PASS"},
        {"case": "test_cninfo_not_called", "result": "PASS"},
    ]
    if result.wasSuccessful():
        _write_test_summary(cases)
        raise SystemExit(0)
    raise SystemExit(1)
