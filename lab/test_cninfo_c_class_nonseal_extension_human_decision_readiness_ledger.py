"""
CNINFO C-class — 非 seal 扩展 human decision readiness ledger 单测（离线 · CNINFO=0 · C-FM-17）。

运行：
    python3 lab/test_cninfo_c_class_nonseal_extension_human_decision_readiness_ledger.py
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

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)
from cninfo_c_class_nonseal_extension_human_decision_readiness_ledger import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    FM13_MOCK_ROOT_REL,
    FM14_MOCK_ROOT_REL,
    FM15_MOCK_ROOT_REL,
    FM16_MOCK_ROOT_REL,
    FROZEN_ATTESTATION_FP_SHA256,
    FROZEN_BOUNDARY_FP_SHA256,
    FROZEN_DRIFT_FP_SHA256,
    FROZEN_EXTENSION_FP_SHA256,
    NonsealHumanDecisionReadinessPaths,
    assert_fm17_output_root,
    build_fm01_05_12_13_14_15_16_gate_battery_rows,
    build_frozen_mock_isolation_rows,
    fingerprint_ledger_matrix,
    run_nonseal_extension_human_decision_readiness_ledger,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_nonseal_extension_human_decision_readiness_ledger.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_human_decision_readiness_ledger_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-17 Non-seal Extension Human Decision Readiness Ledger — Test Summary",
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
            "c_fm_17_nonseal_extension_human_decision_readiness_ledger_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "ready_for_execute = false",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "idle_not_required_while_awaiting = true",
            "hold_recommendation = KEEP_EXECUTE_FALSE",
            "decision_option_a = HOLD_KEEP_EXECUTE_FALSE",
            "seal_chain_extended = false",
            "drift_detected = false",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestNonsealExtensionHumanDecisionReadinessLedger(unittest.TestCase):
    def test_output_root_requires_mock_and_not_fm13_to_fm16(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_fm17_output_root("outputs/validation/cninfo_c_class_not_mock")
        with self.assertRaises(RuntimeError):
            assert_fm17_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        with self.assertRaisesRegex(RuntimeError, "C_FM17_MUST_NOT_OVERWRITE"):
            assert_fm17_output_root(FM13_MOCK_ROOT_REL)
        with self.assertRaisesRegex(RuntimeError, "C_FM17_MUST_NOT_OVERWRITE"):
            assert_fm17_output_root(FM14_MOCK_ROOT_REL)
        with self.assertRaisesRegex(RuntimeError, "C_FM17_MUST_NOT_OVERWRITE"):
            assert_fm17_output_root(FM15_MOCK_ROOT_REL)
        with self.assertRaisesRegex(RuntimeError, "C_FM17_MUST_NOT_OVERWRITE"):
            assert_fm17_output_root(FM16_MOCK_ROOT_REL)
        with self.assertRaisesRegex(
            RuntimeError, FROZEN_MOCK_COHORT_WRITE_FORBIDDEN
        ):
            assert_fm17_output_root(
                "outputs/validation/_mock_c_fm12_dryrun_fingerprint_lineage_isolation"
            )
        norm = assert_fm17_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm17", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_fm_battery_requires_fm16(self) -> None:
        good = {
            "gate": "PASS_OFFLINE",
            "cninfo_calls": 0,
            "execute_production_snapshot_rebuild": False,
            "approved_for_snapshot_rebuild": False,
            "seal_chain_extended": False,
            "drift_detected": False,
            "ready_for_execute": False,
        }
        bad = dict(good)
        bad["gate"] = "FAIL"
        _rows, checks = build_fm01_05_12_13_14_15_16_gate_battery_rows(
            fm01=good,
            fm02=good,
            fm03=good,
            fm04=good,
            fm05=good,
            fm12=good,
            fm13=good,
            fm14=good,
            fm15=good,
            fm16=bad,
        )
        self.assertFalse(checks["fm01_05_12_13_14_15_16_battery_all_pass"])

    def test_frozen_isolation_blocks_mock18_allows_mock19(self) -> None:
        rows, checks = build_frozen_mock_isolation_rows(
            NonsealHumanDecisionReadinessPaths(
                output_root_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL
            )
        )
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK18"))
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK17"))
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK16"))
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK15"))
        self.assertTrue(checks.get("frozen_allow_mock19"))
        self.assertTrue(checks.get("mock18_still_frozen"))
        self.assertTrue(checks.get("mock17_still_frozen"))
        self.assertTrue(checks.get("mock16_still_frozen"))
        self.assertTrue(checks.get("mock15_still_frozen"))
        self.assertTrue(checks.get("seal_mock8_still_frozen"))
        self.assertTrue(checks.get("frozen_mock_isolation_all_pass"))
        self.assertTrue(rows)

    def test_ledger_matrix_fingerprint_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "human_decision_readiness",
                "cohort_id": "*",
                "root_id": "",
                "path": "",
                "expected": "x",
                "observed": "x",
                "ok": "yes",
                "notes": "ok",
            }
        ]
        fp1 = fingerprint_ledger_matrix(rows)
        fp2 = fingerprint_ledger_matrix(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])

    def test_full_readiness_pass_isolated_mock(self) -> None:
        result = run_nonseal_extension_human_decision_readiness_ledger(
            paths=NonsealHumanDecisionReadinessPaths(
                output_root_rel="outputs/validation/_mock_c_fm17_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertFalse(result["execute_production_snapshot_rebuild"])
        self.assertFalse(result["approved_for_snapshot_rebuild"])
        self.assertFalse(result["ready_for_execute"])
        self.assertFalse(result["seal_chain_extended"])
        self.assertFalse(result["drift_detected"])
        self.assertEqual(result["hold_recommendation"], "KEEP_EXECUTE_FALSE")
        self.assertEqual(result["decision_option_a"], "HOLD_KEEP_EXECUTE_FALSE")
        self.assertTrue(result["idle_not_required_while_awaiting"])
        self.assertTrue(result["mock_root_is_isolated"])
        self.assertEqual(
            result["frozen_extension_fp_sha256"], FROZEN_EXTENSION_FP_SHA256
        )
        self.assertEqual(result["frozen_drift_fp_sha256"], FROZEN_DRIFT_FP_SHA256)
        self.assertEqual(
            result["frozen_boundary_fp_sha256"], FROZEN_BOUNDARY_FP_SHA256
        )
        self.assertEqual(
            result["frozen_attestation_fp_sha256"], FROZEN_ATTESTATION_FP_SHA256
        )
        self.assertTrue(result["readiness_packet"]["ready_for_commit"])
        self.assertFalse(result["readiness_packet"]["ready_for_execute"])
        self.assertTrue(result["readiness_packet"]["decision_option_a_recommended"])
        self.assertFalse(result["readiness_packet"]["decision_option_b_auto_applied"])
        self.assertEqual(
            result["readiness_packet"]["controller_action"],
            "HUMAN_DECISION_READINESS_LEDGER_ONLY",
        )
        self.assertEqual(
            result["checklist"]["options"][0]["label"], "HOLD_KEEP_EXECUTE_FALSE"
        )
        self.assertTrue(result["checklist"]["options"][0]["recommended"])
        self.assertFalse(result["checklist"]["options"][1]["auto_applied"])
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
            os.path.isfile(os.path.join(BASE_DIR, result["readiness_packet_path"]))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["checklist_path"]))
        )
        with open(
            os.path.join(BASE_DIR, result["battery_path"]), encoding="utf-8"
        ) as fh:
            battery = json.load(fh)
        self.assertEqual(battery["fm13_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm14_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm15_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm16_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm17_gate"], "PASS_OFFLINE")
        self.assertFalse(battery["seal_chain_extended"])
        self.assertFalse(battery["drift_detected"])
        # 确认未覆盖 MOCK15–18
        fm13_fp = os.path.join(
            BASE_DIR, FM13_MOCK_ROOT_REL, "extension_fingerprint.json"
        )
        with open(fm13_fp, encoding="utf-8") as fh:
            frozen = json.load(fh)
        self.assertEqual(frozen["task_id"], "C-FM-13")
        self.assertEqual(
            frozen["fingerprint"]["fingerprint_sha256"], FROZEN_EXTENSION_FP_SHA256
        )
        fm16_fp = os.path.join(
            BASE_DIR, FM16_MOCK_ROOT_REL, "attestation_fingerprint.json"
        )
        with open(fm16_fp, encoding="utf-8") as fh:
            att = json.load(fh)
        self.assertEqual(att["task_id"], "C-FM-16")
        self.assertEqual(
            att["fingerprint"]["fingerprint_sha256"], FROZEN_ATTESTATION_FP_SHA256
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
            run_nonseal_extension_human_decision_readiness_ledger(
                paths=NonsealHumanDecisionReadinessPaths(
                    output_root_rel=(
                        "outputs/validation/_mock_c_fm17_unit_cninfo_probe"
                    )
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(
        TestNonsealExtensionHumanDecisionReadinessLedger
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {
            "case": "test_output_root_requires_mock_and_not_fm13_to_fm16",
            "result": "PASS",
        },
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {"case": "test_fm_battery_requires_fm16", "result": "PASS"},
        {
            "case": "test_frozen_isolation_blocks_mock18_allows_mock19",
            "result": "PASS",
        },
        {"case": "test_ledger_matrix_fingerprint_stable", "result": "PASS"},
        {"case": "test_full_readiness_pass_isolated_mock", "result": "PASS"},
        {"case": "test_cli_execute_forbidden", "result": "PASS"},
        {"case": "test_cninfo_not_called", "result": "PASS"},
    ]
    if not result.wasSuccessful():
        for t in result.failures + result.errors:
            name = t[0]._testMethodName
            for c in cases:
                if c["case"] == name:
                    c["result"] = "FAIL"
        _write_test_summary(cases)
        raise SystemExit(1)
    _write_test_summary(cases)
    raise SystemExit(0)
