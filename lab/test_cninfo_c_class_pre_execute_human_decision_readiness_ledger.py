"""
CNINFO C-class — Pre-EXECUTE human decision readiness ledger 单测（离线 · CNINFO=0 · C-FM-10）。

运行：
    python3 lab/test_cninfo_c_class_pre_execute_human_decision_readiness_ledger.py
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
    assert_authoritative_dual_layer_index_write_forbidden,
)
from cninfo_c_class_pre_execute_human_decision_readiness_ledger import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    FM06_MOCK_ROOT_REL,
    FM07_MOCK_ROOT_REL,
    FM08_MOCK_ROOT_REL,
    FM09_MOCK_ROOT_REL,
    FROZEN_ATTESTATION_FP_SHA256,
    FROZEN_BOUNDARY_FP_SHA256,
    FROZEN_WALL_FP_SHA256,
    HumanDecisionReadinessPaths,
    assert_human_decision_readiness_output_root,
    build_fm01_to_09_gate_battery_rows,
    fingerprint_ledger_matrix,
    run_pre_execute_human_decision_readiness_ledger,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_pre_execute_human_decision_readiness_ledger.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_human_decision_readiness_ledger_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-10 Pre-EXECUTE Human Decision Readiness Ledger — Test Summary",
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
            "c_fm_10_pre_execute_human_decision_readiness_ledger_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "ready_for_execute = false",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "decision_option_a = HOLD_KEEP_EXECUTE_FALSE",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestPreExecuteHumanDecisionReadinessLedger(unittest.TestCase):
    def test_output_root_requires_mock_and_not_fm06_to_fm09(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_human_decision_readiness_output_root(
                "outputs/validation/cninfo_c_class_not_mock"
            )
        with self.assertRaises(RuntimeError):
            assert_human_decision_readiness_output_root(
                AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL
            )
        with self.assertRaises(RuntimeError):
            assert_human_decision_readiness_output_root(FM06_MOCK_ROOT_REL)
        with self.assertRaises(RuntimeError):
            assert_human_decision_readiness_output_root(FM07_MOCK_ROOT_REL)
        with self.assertRaises(RuntimeError):
            assert_human_decision_readiness_output_root(FM08_MOCK_ROOT_REL)
        with self.assertRaises(RuntimeError):
            assert_human_decision_readiness_output_root(FM09_MOCK_ROOT_REL)
        norm = assert_human_decision_readiness_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm10", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_fm_battery_requires_all_nine(self) -> None:
        good = {
            "gate": "PASS_OFFLINE",
            "cninfo_calls": 0,
            "execute_production_snapshot_rebuild": False,
            "approved_for_snapshot_rebuild": False,
        }
        bad = dict(good)
        bad["gate"] = "FAIL"
        _rows, checks = build_fm01_to_09_gate_battery_rows(
            fm01=good,
            fm02=good,
            fm03=good,
            fm04=good,
            fm05=good,
            fm06=good,
            fm07=good,
            fm08=good,
            fm09=bad,
        )
        self.assertFalse(checks["fm01_to_09_battery_all_pass"])

    def test_ledger_matrix_fingerprint_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "human_decision_readiness",
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
        result = run_pre_execute_human_decision_readiness_ledger(
            paths=HumanDecisionReadinessPaths(
                output_root_rel="outputs/validation/_mock_c_fm10_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertFalse(result["execute_production_snapshot_rebuild"])
        self.assertFalse(result["approved_for_snapshot_rebuild"])
        self.assertTrue(result["mock_root_is_isolated"])
        self.assertEqual(
            result["readiness_packet"]["hold_recommendation"], "KEEP_EXECUTE_FALSE"
        )
        self.assertTrue(result["readiness_packet"]["ready_for_commit"])
        self.assertFalse(result["readiness_packet"]["ready_for_execute"])
        self.assertEqual(
            result["readiness_packet"]["controller_action"],
            "HUMAN_DECISION_READINESS_LEDGER_ONLY",
        )
        self.assertEqual(
            result["readiness_packet"]["decision_status"],
            "AWAITING_HUMAN_EXECUTE_DECISION",
        )
        self.assertEqual(
            result["readiness_packet"]["decision_option_a"],
            "HOLD_KEEP_EXECUTE_FALSE",
        )
        self.assertTrue(result["readiness_packet"]["decision_option_a_recommended"])
        self.assertFalse(result["readiness_packet"]["decision_option_b_auto_applied"])
        self.assertEqual(
            result["frozen_attestation_fingerprint_sha256"],
            FROZEN_ATTESTATION_FP_SHA256,
        )
        self.assertFalse(result["seal_packet"]["drift_detected"])
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
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["seal_packet_path"]))
        )
        with open(
            os.path.join(BASE_DIR, result["battery_path"]), encoding="utf-8"
        ) as fh:
            battery = json.load(fh)
        self.assertEqual(battery["fm01_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm09_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm10_gate"], "PASS_OFFLINE")
        with open(
            os.path.join(BASE_DIR, result["checklist_path"]), encoding="utf-8"
        ) as fh:
            checklist = json.load(fh)
        self.assertEqual(len(checklist["options"]), 2)
        self.assertTrue(checklist["options"][0]["recommended"])
        self.assertFalse(checklist["options"][1]["auto_applied"])
        # 确认未覆盖 MOCK8 / MOCK9 / MOCK10 / MOCK11
        fm06_fp = os.path.join(
            BASE_DIR, FM06_MOCK_ROOT_REL, "wall_fingerprint.json"
        )
        with open(fm06_fp, encoding="utf-8") as fh:
            frozen = json.load(fh)
        self.assertEqual(frozen["task_id"], "C-FM-06")
        self.assertEqual(
            frozen["fingerprint"]["fingerprint_sha256"], FROZEN_WALL_FP_SHA256
        )
        fm08_fp = os.path.join(
            BASE_DIR, FM08_MOCK_ROOT_REL, "boundary_fingerprint.json"
        )
        with open(fm08_fp, encoding="utf-8") as fh:
            bfp = json.load(fh)
        self.assertEqual(bfp["task_id"], "C-FM-08")
        self.assertEqual(
            bfp["fingerprint"]["fingerprint_sha256"], FROZEN_BOUNDARY_FP_SHA256
        )
        fm09_fp = os.path.join(
            BASE_DIR, FM09_MOCK_ROOT_REL, "attestation_fingerprint.json"
        )
        with open(fm09_fp, encoding="utf-8") as fh:
            afp = json.load(fh)
        self.assertEqual(afp["task_id"], "C-FM-09")
        self.assertEqual(
            afp["fingerprint"]["fingerprint_sha256"], FROZEN_ATTESTATION_FP_SHA256
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
            run_pre_execute_human_decision_readiness_ledger(
                paths=HumanDecisionReadinessPaths(
                    output_root_rel=(
                        "outputs/validation/_mock_c_fm10_unit_cninfo_probe"
                    )
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPreExecuteHumanDecisionReadinessLedger)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {
            "case": "test_output_root_requires_mock_and_not_fm06_to_fm09",
            "result": "PASS",
        },
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {"case": "test_fm_battery_requires_all_nine", "result": "PASS"},
        {"case": "test_ledger_matrix_fingerprint_stable", "result": "PASS"},
        {
            "case": "test_full_readiness_pass_isolated_mock",
            "result": "PASS",
        },
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
