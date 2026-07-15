"""
CNINFO C-class — 非 seal 三次扩展 post-commit 漂移复核单测（离线 · CNINFO=0 · C-FM-21）。

运行：
    python3 lab/test_cninfo_c_class_nonseal_third_extension_post_commit_drift_recheck.py
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
from cninfo_c_class_nonseal_third_extension_post_commit_drift_recheck import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    FM20_MOCK_ROOT_REL,
    FROZEN_THIRD_EXTENSION_FP_SHA256,
    ThirdExtensionDriftPaths,
    assert_fm21_output_root,
    build_fm01_05_12_20_gate_battery_rows,
    build_frozen_mock_isolation_rows,
    fingerprint_third_extension_drift_matrix,
    recompute_third_extension_fingerprints,
    run_nonseal_third_extension_post_commit_drift_recheck,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_nonseal_third_extension_post_commit_drift_recheck.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_third_extension_post_commit_drift_recheck_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-21 Non-seal Third Extension Post-Commit Drift Recheck — Test Summary",
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
            "c_fm_21_nonseal_third_extension_post_commit_drift_recheck_test_gate = PASS_OFFLINE",
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


class TestNonsealThirdExtensionPostCommitDriftRecheck(unittest.TestCase):
    def test_output_root_requires_mock_and_not_fm20(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_fm21_output_root("outputs/validation/cninfo_c_class_not_mock")
        with self.assertRaises(RuntimeError):
            assert_fm21_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        with self.assertRaisesRegex(RuntimeError, "C_FM21_MUST_NOT_OVERWRITE"):
            assert_fm21_output_root(FM20_MOCK_ROOT_REL)
        # 已登记但非本任务的 MOCK12 亦拒写
        with self.assertRaisesRegex(
            RuntimeError, FROZEN_MOCK_COHORT_WRITE_FORBIDDEN
        ):
            assert_fm21_output_root(
                "outputs/validation/_mock_c_fm12_dryrun_fingerprint_lineage_isolation"
            )
        norm = assert_fm21_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm21", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_fm_battery_requires_fm20(self) -> None:
        good = {
            "gate": "PASS_OFFLINE",
            "cninfo_calls": 0,
            "execute_production_snapshot_rebuild": False,
            "approved_for_snapshot_rebuild": False,
            "seal_chain_extended": False,
        }
        bad = dict(good)
        bad["gate"] = "FAIL"
        gates = {k: good for k in (
            "fm01", "fm02", "fm03", "fm04", "fm05",
            "fm12", "fm13", "fm14", "fm15", "fm16", "fm17",
            "fm18", "fm19",
        )}
        gates["fm20"] = bad
        _rows, checks = build_fm01_05_12_20_gate_battery_rows(gates=gates)
        self.assertFalse(checks["fm01_05_12_20_battery_all_pass"])

    def test_recompute_matches_frozen_constant(self) -> None:
        fp, matrix = recompute_third_extension_fingerprints(
            probe_output_root_rel="outputs/validation/_mock_c_fm21_recompute_probe"
        )
        self.assertEqual(fp["fingerprint_sha256"], FROZEN_THIRD_EXTENSION_FP_SHA256)
        self.assertEqual(fp["fail_count"], 0)
        self.assertEqual(len(matrix), 115)

    def test_frozen_isolation_blocks_mock22_allows_mock23(self) -> None:
        rows, checks = build_frozen_mock_isolation_rows(
            ThirdExtensionDriftPaths(output_root_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL)
        )
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK22"))
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK21"))
        self.assertTrue(checks.get("frozen_allow_mock23"))
        self.assertTrue(checks.get("mock22_still_frozen"))
        self.assertTrue(checks.get("seal_mock8_still_frozen"))
        self.assertTrue(checks.get("frozen_mock_isolation_all_pass"))
        self.assertTrue(rows)

    def test_drift_matrix_fingerprint_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "fingerprint_drift",
                "cohort_id": "*",
                "root_id": "",
                "path": "",
                "expected": "x",
                "observed": "x",
                "ok": "yes",
                "notes": "ok",
            }
        ]
        fp1 = fingerprint_third_extension_drift_matrix(rows)
        fp2 = fingerprint_third_extension_drift_matrix(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])

    def test_full_drift_recheck_pass_isolated_mock(self) -> None:
        result = run_nonseal_third_extension_post_commit_drift_recheck(
            paths=ThirdExtensionDriftPaths(
                output_root_rel="outputs/validation/_mock_c_fm21_cli_test_tmp"
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
        self.assertTrue(result["idle_not_required_while_awaiting"])
        self.assertTrue(result["mock_root_is_isolated"])
        self.assertEqual(
            result["frozen_third_extension_fp_sha256"],
            FROZEN_THIRD_EXTENSION_FP_SHA256,
        )
        self.assertEqual(
            result["recomputed_third_extension_fp_sha256"],
            FROZEN_THIRD_EXTENSION_FP_SHA256,
        )
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
            os.path.isfile(os.path.join(BASE_DIR, result["seal_packet_path"]))
        )
        with open(
            os.path.join(BASE_DIR, result["battery_path"]), encoding="utf-8"
        ) as fh:
            battery = json.load(fh)
        self.assertEqual(battery["fm20_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm21_gate"], "PASS_OFFLINE")
        self.assertFalse(battery["seal_chain_extended"])
        # 确认未覆盖 MOCK22
        fm18_fp = os.path.join(
            BASE_DIR, FM20_MOCK_ROOT_REL, "extension_fingerprint.json"
        )
        with open(fm18_fp, encoding="utf-8") as fh:
            frozen = json.load(fh)
        self.assertEqual(frozen["task_id"], "C-FM-20")
        self.assertEqual(
            frozen["fingerprint"]["fingerprint_sha256"],
            FROZEN_THIRD_EXTENSION_FP_SHA256,
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
            run_nonseal_third_extension_post_commit_drift_recheck(
                paths=ThirdExtensionDriftPaths(
                    output_root_rel=(
                        "outputs/validation/_mock_c_fm21_unit_cninfo_probe"
                    )
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(
        TestNonsealThirdExtensionPostCommitDriftRecheck
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {
            "case": "test_output_root_requires_mock_and_not_fm20",
            "result": "PASS",
        },
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {"case": "test_fm_battery_requires_fm20", "result": "PASS"},
        {"case": "test_recompute_matches_frozen_constant", "result": "PASS"},
        {
            "case": "test_frozen_isolation_blocks_mock22_allows_mock23",
            "result": "PASS",
        },
        {"case": "test_drift_matrix_fingerprint_stable", "result": "PASS"},
        {"case": "test_full_drift_recheck_pass_isolated_mock", "result": "PASS"},
        {"case": "test_cli_execute_forbidden", "result": "PASS"},
        {"case": "test_cninfo_not_called", "result": "PASS"},
    ]
    if result.wasSuccessful():
        _write_test_summary(cases)
        raise SystemExit(0)
    raise SystemExit(1)
