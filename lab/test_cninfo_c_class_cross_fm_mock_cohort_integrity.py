"""
CNINFO C-class — Cross-FM mock cohort 完整性单测（离线 · CNINFO=0 · C-FM-05）。

运行：
    python3 lab/test_cninfo_c_class_cross_fm_mock_cohort_integrity.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_cross_fm_mock_cohort_integrity import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    IntegrityPaths,
    MockCohortSpec,
    assert_integrity_output_root,
    build_fm_gate_battery_rows,
    build_mock_cohort_registry_rows,
    build_protected_write_guard_battery_rows,
    default_mock_cohort_specs,
    fingerprint_integrity_matrix,
    run_cross_fm_mock_cohort_integrity,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    assert_authoritative_dual_layer_index_write_forbidden,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_cross_fm_mock_cohort_integrity.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_cross_fm_mock_cohort_integrity_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-05 Cross-FM Mock Cohort Integrity — Test Summary",
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
            "c_fm_05_cross_fm_mock_cohort_integrity_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestCrossFmMockCohortIntegrity(unittest.TestCase):
    def test_output_root_requires_mock(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_integrity_output_root(
                "outputs/validation/cninfo_c_class_not_mock"
            )
        with self.assertRaises(RuntimeError):
            assert_integrity_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        norm = assert_integrity_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm05", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_registry_flags_missing_artifact(self) -> None:
        bad = MockCohortSpec(
            cohort_id="broken_cohort",
            root_rel="outputs/validation/_mock_c_fm05_unit_missing",
            root_id="C-ROOT-MOCK7",
            required_files=("definitely_missing.csv",),
            fingerprint_kind="none",
            gate_json_rel="outputs/validation/does_not_exist.json",
        )
        rows, checks = build_mock_cohort_registry_rows([bad])
        self.assertFalse(checks["cohort_registry_broken_cohort"])
        self.assertTrue(any(r["ok"] == "no" for r in rows))

    def test_write_guard_battery_structure(self) -> None:
        rows, checks = build_protected_write_guard_battery_rows(
            mock_probe_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL
        )
        self.assertTrue(checks.get("write_guard_harvest_slice1_refused"))
        self.assertTrue(checks.get("write_guard_snapshot_full_refused"))
        self.assertTrue(checks.get("write_guard_auth_dual_layer_refused"))
        self.assertTrue(checks.get("write_guard_mock_allowed"))
        self.assertTrue(checks.get("protected_write_guard_battery_all_pass"))
        self.assertTrue(rows)

    def test_fm_battery_requires_all_four(self) -> None:
        good = {
            "gate": "PASS_OFFLINE",
            "cninfo_calls": 0,
            "execute_production_snapshot_rebuild": False,
        }
        bad = dict(good)
        bad["gate"] = "FAIL"
        _rows, checks = build_fm_gate_battery_rows(
            fm01=good, fm02=good, fm03=good, fm04=bad
        )
        self.assertFalse(checks["fm01_02_03_04_battery_all_pass"])

    def test_fingerprint_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "mock_cohort_registry",
                "cohort_id": "*",
                "root_id": "",
                "path": "",
                "expected": "x",
                "observed": "x",
                "ok": "yes",
                "notes": "ok",
            }
        ]
        fp1 = fingerprint_integrity_matrix(rows)
        fp2 = fingerprint_integrity_matrix(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])

    def test_full_integrity_pass_isolated_mock(self) -> None:
        # 先确保 MOCK7 已写入 protected CSV（runner/任务前置）；测试读真实 CSV
        result = run_cross_fm_mock_cohort_integrity(
            paths=IntegrityPaths(
                output_root_rel="outputs/validation/_mock_c_fm05_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertFalse(result["execute_production_snapshot_rebuild"])
        self.assertTrue(result["mock_root_is_isolated"])
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["matrix_path"]))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["fingerprint_path"]))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["registry_path"]))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(BASE_DIR, result["battery_path"]))
        )
        with open(
            os.path.join(BASE_DIR, result["battery_path"]), encoding="utf-8"
        ) as fh:
            battery = json.load(fh)
        self.assertEqual(battery["fm01_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm02_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm03_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm04_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm05_gate"], "PASS_OFFLINE")
        self.assertEqual(len(default_mock_cohort_specs()), 4)

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
            run_cross_fm_mock_cohort_integrity(
                paths=IntegrityPaths(
                    output_root_rel="outputs/validation/_mock_c_fm05_unit_cninfo_probe"
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestCrossFmMockCohortIntegrity)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {"case": "test_output_root_requires_mock", "result": "PASS"},
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {"case": "test_registry_flags_missing_artifact", "result": "PASS"},
        {"case": "test_write_guard_battery_structure", "result": "PASS"},
        {"case": "test_fm_battery_requires_all_four", "result": "PASS"},
        {"case": "test_fingerprint_stable", "result": "PASS"},
        {"case": "test_full_integrity_pass_isolated_mock", "result": "PASS"},
        {"case": "test_cli_execute_forbidden", "result": "PASS"},
        {"case": "test_cninfo_not_called", "result": "PASS"},
    ]
    if result.wasSuccessful():
        _write_test_summary(cases)
        raise SystemExit(0)
    raise SystemExit(1)
