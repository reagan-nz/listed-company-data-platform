"""
CNINFO C-class — dry-run 指纹 lineage 扩展 + 冻结 mock 隔离单测（离线 · CNINFO=0 · C-FM-12）。

运行：
    python3 lab/test_cninfo_c_class_dryrun_fingerprint_lineage_isolation.py
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

from cninfo_c_class_dryrun_fingerprint_lineage_isolation import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    IsolationPaths,
    assert_fm12_output_root,
    build_dryrun_lineage_extension_rows,
    build_frozen_mock_isolation_rows,
    fingerprint_isolation_matrix,
    run_dryrun_fingerprint_lineage_isolation,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
    fingerprint_isolated_snapshot_dryrun,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_dryrun_fingerprint_lineage_isolation.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_dryrun_fingerprint_lineage_isolation_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-12 Dry-run Fingerprint Lineage Isolation — Test Summary",
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
            "c_fm_12_dryrun_fingerprint_lineage_isolation_test_gate = PASS_OFFLINE",
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


class TestDryrunFingerprintLineageIsolation(unittest.TestCase):
    def test_output_root_requires_mock_and_not_frozen(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_fm12_output_root("outputs/validation/cninfo_c_class_not_mock")
        with self.assertRaises(RuntimeError):
            assert_fm12_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        with self.assertRaisesRegex(
            RuntimeError, FROZEN_MOCK_COHORT_WRITE_FORBIDDEN
        ):
            assert_fm12_output_root(
                "outputs/validation/_mock_c_fm06_pre_execute_safe_snapshot_wall"
            )
        norm = assert_fm12_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm12", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_lineage_extension_differs_and_reproducible(self) -> None:
        paths = IsolationPaths()
        _rows, checks, meta = build_dryrun_lineage_extension_rows(paths)
        self.assertTrue(checks.get("lineage_ext_fm02_differs_base"))
        self.assertTrue(checks.get("lineage_ext_fm02_reproducible"))
        self.assertTrue(checks.get("lineage_ext_fm02_artifacts_present"))
        self.assertTrue(checks.get("dryrun_lineage_extension_all_pass"))
        self.assertTrue(meta.get("fm02_lineage_ext_sha256"))

    def test_frozen_isolation_blocks_mock8(self) -> None:
        rows, checks = build_frozen_mock_isolation_rows(
            IsolationPaths(output_root_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL)
        )
        self.assertTrue(checks.get("frozen_block_C-ROOT-MOCK8"))
        self.assertTrue(checks.get("frozen_allow_mock14"))
        self.assertTrue(checks.get("frozen_mock_isolation_all_pass"))
        self.assertTrue(rows)

    def test_base_fingerprint_api_unchanged_without_flag(self) -> None:
        root = (
            "outputs/validation/_mock_c_fm02_slice1_190_validation_cohort"
        )
        fp = fingerprint_isolated_snapshot_dryrun(
            root, gate="PASS_WITH_CAVEAT", company_count=190
        )
        self.assertNotIn("lineage_artifacts", fp)
        with open(
            os.path.join(
                BASE_DIR,
                "outputs/validation/"
                "cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json",
            ),
            encoding="utf-8",
        ) as fh:
            gate = json.load(fh)
        expected = (
            (gate.get("slice1_190") or {}).get("fingerprint") or {}
        ).get("fingerprint_sha256")
        self.assertEqual(fp["fingerprint_sha256"], expected)

    def test_fingerprint_matrix_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "dryrun_base_fingerprint",
                "cohort_id": "*",
                "root_id": "",
                "path": "",
                "expected": "x",
                "observed": "x",
                "ok": "yes",
                "notes": "ok",
            }
        ]
        fp1 = fingerprint_isolation_matrix(rows)
        fp2 = fingerprint_isolation_matrix(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])

    def test_full_isolation_pass_isolated_mock(self) -> None:
        result = run_dryrun_fingerprint_lineage_isolation(
            paths=IsolationPaths(
                output_root_rel="outputs/validation/_mock_c_fm12_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertFalse(result["execute_production_snapshot_rebuild"])
        self.assertFalse(result["approved_for_snapshot_rebuild"])
        self.assertFalse(result["ready_for_execute"])
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
            battery["layer_gates"]["dryrun_lineage_extension"], "PASS_OFFLINE"
        )
        self.assertEqual(
            battery["layer_gates"]["frozen_mock_isolation"], "PASS_OFFLINE"
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
            run_dryrun_fingerprint_lineage_isolation(
                paths=IsolationPaths(
                    output_root_rel=(
                        "outputs/validation/_mock_c_fm12_unit_cninfo_probe"
                    )
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDryrunFingerprintLineageIsolation)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {
            "case": "test_output_root_requires_mock_and_not_frozen",
            "result": "PASS",
        },
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {
            "case": "test_lineage_extension_differs_and_reproducible",
            "result": "PASS",
        },
        {"case": "test_frozen_isolation_blocks_mock8", "result": "PASS"},
        {
            "case": "test_base_fingerprint_api_unchanged_without_flag",
            "result": "PASS",
        },
        {"case": "test_fingerprint_matrix_stable", "result": "PASS"},
        {"case": "test_full_isolation_pass_isolated_mock", "result": "PASS"},
        {"case": "test_cli_execute_forbidden", "result": "PASS"},
        {"case": "test_cninfo_not_called", "result": "PASS"},
    ]
    if result.wasSuccessful():
        _write_test_summary(cases)
        raise SystemExit(0)
    raise SystemExit(1)
