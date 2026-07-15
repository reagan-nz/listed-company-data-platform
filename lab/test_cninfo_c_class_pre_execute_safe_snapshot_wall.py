"""
CNINFO C-class — Pre-EXECUTE 安全 snapshot 墙冻结单测（离线 · CNINFO=0 · C-FM-06）。

运行：
    python3 lab/test_cninfo_c_class_pre_execute_safe_snapshot_wall.py
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
from cninfo_c_class_pre_execute_safe_snapshot_wall import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    WallPaths,
    assert_wall_output_root,
    build_execute_wall_rows,
    build_fm_gate_battery_rows,
    fingerprint_exclusion_universe,
    fingerprint_wall_matrix,
    run_pre_execute_safe_snapshot_wall,
)

_RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_pre_execute_safe_snapshot_wall.py"
)
_TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_safe_snapshot_wall_test_summary_20260715.md"
)


def _write_test_summary(cases: list) -> None:
    path = os.path.join(BASE_DIR, _TEST_SUMMARY_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [
        "# C-FM-06 Pre-EXECUTE Safe Snapshot Wall — Test Summary",
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
            "c_fm_06_pre_execute_safe_snapshot_wall_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "```",
            "",
        ]
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestPreExecuteSafeSnapshotWall(unittest.TestCase):
    def test_output_root_requires_mock(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_wall_output_root("outputs/validation/cninfo_c_class_not_mock")
        with self.assertRaises(RuntimeError):
            assert_wall_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        norm = assert_wall_output_root(DEFAULT_MOCK_OUTPUT_ROOT_REL)
        self.assertIn("_mock_c_fm06", norm)

    def test_auth_index_write_still_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_authoritative_dual_layer_index_write_forbidden(probe)

    def test_fm_battery_requires_all_five(self) -> None:
        good = {
            "gate": "PASS_OFFLINE",
            "cninfo_calls": 0,
            "execute_production_snapshot_rebuild": False,
        }
        bad = dict(good)
        bad["gate"] = "FAIL"
        _rows, checks = build_fm_gate_battery_rows(
            fm01=good, fm02=good, fm03=good, fm04=good, fm05=bad
        )
        self.assertFalse(checks["fm01_to_05_battery_all_pass"])

    def test_execute_wall_structure(self) -> None:
        rows, checks = build_execute_wall_rows(
            mock_probe_rel=DEFAULT_MOCK_OUTPUT_ROOT_REL
        )
        self.assertTrue(checks.get("execute_production_snapshot_rebuild_false"))
        self.assertTrue(checks.get("execute_wall_harvest_slice1_refused"))
        self.assertTrue(checks.get("execute_wall_snapshot_full_refused"))
        self.assertTrue(checks.get("execute_wall_mock_allowed"))
        self.assertTrue(checks.get("approved_for_snapshot_rebuild_remains_false"))
        self.assertTrue(checks.get("execute_wall_all_pass"))
        self.assertTrue(rows)

    def test_exclusion_fingerprint_stable(self) -> None:
        rows = [
            {
                "exclusion_id": "EXC-P01",
                "cohort_family": "partial7",
                "company_code": "600001",
                "promotion_allowed_now": "no",
            },
            {
                "exclusion_id": "EXC-E01",
                "cohort_family": "empty_dividend3",
                "company_code": "688031",
                "promotion_allowed_now": "no",
            },
        ]
        fp1 = fingerprint_exclusion_universe(rows)
        fp2 = fingerprint_exclusion_universe(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])
        self.assertEqual(fp1["unique_code_count"], 2)

    def test_wall_fingerprint_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "execute_wall",
                "path": "",
                "expected": "x",
                "observed": "x",
                "ok": "yes",
                "notes": "ok",
            }
        ]
        fp1 = fingerprint_wall_matrix(rows)
        fp2 = fingerprint_wall_matrix(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])

    def test_full_wall_pass_isolated_mock(self) -> None:
        # 依赖 MOCK8 已写入 protected CSV（任务前置）
        result = run_pre_execute_safe_snapshot_wall(
            paths=WallPaths(
                output_root_rel="outputs/validation/_mock_c_fm06_cli_test_tmp"
            )
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertFalse(result["execute_production_snapshot_rebuild"])
        self.assertFalse(result["approved_for_snapshot_rebuild"])
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
            os.path.isfile(
                os.path.join(BASE_DIR, result["human_approval_packet_path"])
            )
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
        self.assertEqual(battery["fm06_gate"], "PASS_OFFLINE")
        packet = result["human_approval_packet"]
        self.assertEqual(packet["hold_recommendation"], "KEEP_EXECUTE_FALSE")
        self.assertTrue(packet["human_action_required_for_execute"])
        self.assertFalse(packet["approved_for_snapshot_rebuild"])

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
            run_pre_execute_safe_snapshot_wall(
                paths=WallPaths(
                    output_root_rel="outputs/validation/_mock_c_fm06_unit_cninfo_probe"
                )
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPreExecuteSafeSnapshotWall)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cases = [
        {"case": "test_output_root_requires_mock", "result": "PASS"},
        {"case": "test_auth_index_write_still_forbidden", "result": "PASS"},
        {"case": "test_fm_battery_requires_all_five", "result": "PASS"},
        {"case": "test_execute_wall_structure", "result": "PASS"},
        {"case": "test_exclusion_fingerprint_stable", "result": "PASS"},
        {"case": "test_wall_fingerprint_stable", "result": "PASS"},
        {"case": "test_full_wall_pass_isolated_mock", "result": "PASS"},
        {"case": "test_cli_execute_forbidden", "result": "PASS"},
        {"case": "test_cninfo_not_called", "result": "PASS"},
    ]
    if not result.wasSuccessful():
        for i, t in enumerate(result.failures + result.errors):
            # 失败时标记对应 case（按失败顺序粗略覆盖）
            name = t[0]._testMethodName
            for c in cases:
                if c["case"] == name:
                    c["result"] = "FAIL"
        _write_test_summary(cases)
        raise SystemExit(1)
    _write_test_summary(cases)
    raise SystemExit(0)
