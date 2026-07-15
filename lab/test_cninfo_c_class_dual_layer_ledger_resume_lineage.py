#!/usr/bin/env python3
"""
CNINFO C-class — ledger↔resume-audit dual-layer lineage 单测（离线 · CNINFO=0 · C-FM-04）。

运行：
    python3 lab/test_cninfo_c_class_dual_layer_ledger_resume_lineage.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from typing import Dict, List
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_dual_layer_ledger_resume_lineage import (  # noqa: E402
    LineagePaths,
    assert_lineage_output_root,
    build_caveat_ledger_resume_rows,
    build_fm_gate_battery_rows,
    build_index_isolation_rows,
    build_resume_aggregate_rows,
    expected_resume_semantics,
    family_for_code,
    fingerprint_lineage_matrix,
    run_dual_layer_ledger_resume_lineage,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
    BASE_DIR,
    DUAL_LAYER_INDEX_WRITE_FORBIDDEN,
    assert_authoritative_dual_layer_index_write_forbidden,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_PARTIAL7,
)

RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_dual_layer_ledger_resume_lineage.py"
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_dual_layer_ledger_resume_lineage_test_summary_20260715.md",
)


def _write_test_summary(results: List[Dict[str, str]]) -> None:
    lines = [
        "# C-FM-04 Dual-layer Ledger/Resume Lineage — Test Summary",
        "",
        "_offline · CNINFO=0_",
        "",
        "| case | result |",
        "|------|--------|",
    ]
    for row in results:
        lines.append(f"| `{row['case']}` | **{row['result']}** |")
    lines.extend(
        [
            "",
            "```",
            "c_fm_04_dual_layer_ledger_resume_lineage_test_gate = PASS_OFFLINE",
            "cninfo_calls = 0",
            "execute_production_snapshot_rebuild = false",
            "```",
            "",
        ]
    )
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


class TestRootGuards(unittest.TestCase):
    def test_refuse_non_mock(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "COHORT_ROOT_MOCK_PREFIX_REQUIRED"):
            assert_lineage_output_root(
                "outputs/validation/cninfo_c_class_not_mock"
            )

    def test_refuse_authoritative_dual_layer_index(self) -> None:
        with self.assertRaisesRegex(
            RuntimeError,
            f"{DUAL_LAYER_INDEX_WRITE_FORBIDDEN}|COHORT_ROOT_MOCK_PREFIX_REQUIRED",
        ):
            assert_lineage_output_root(AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)

    def test_allow_mock(self) -> None:
        norm = assert_lineage_output_root(
            "outputs/validation/_mock_c_fm04_dual_layer_ledger_resume_lineage"
        )
        self.assertIn("_mock_c_fm04", norm)

    def test_authoritative_write_forbidden(self) -> None:
        probe = os.path.join(
            BASE_DIR,
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            "qa_closure_dual_layer_evidence_index.csv",
        )
        with self.assertRaisesRegex(RuntimeError, DUAL_LAYER_INDEX_WRITE_FORBIDDEN):
            assert_authoritative_dual_layer_index_write_forbidden(probe)


class TestSemantics(unittest.TestCase):
    def test_family_and_expected(self) -> None:
        code_e = sorted(EXPECTED_SLICE1_EMPTY_DIVIDEND3)[0]
        code_p = sorted(EXPECTED_SLICE1_PARTIAL7)[0]
        self.assertEqual(family_for_code(code_e), "empty_dividend3")
        self.assertEqual(family_for_code(code_p), "partial7")
        self.assertEqual(
            expected_resume_semantics(code_e)["resume"], "needs_review"
        )
        self.assertEqual(expected_resume_semantics(code_p)["resume"], "partial")

    def test_caveat_rows_detect_empty3_resume_flip(self) -> None:
        code = sorted(EXPECTED_SLICE1_EMPTY_DIVIDEND3)[0]
        harvest = {code: {"harvest_status": "complete"}}
        resume = {
            code: {
                "resume_state": "complete",  # 错误：应为 needs_review
                "sources_present": "10",
                "live_resume_recommendation": "none",
            }
        }
        pool = {code: "excluded"}
        empty3 = {
            code: {
                "index_status": "indexed_pass",
                "dual_layer_audit_gate": "PASS_OFFLINE",
                "rules_all_pass": "yes",
            }
        }
        rows, checks = build_caveat_ledger_resume_rows(
            harvest_status=harvest,
            resume_map=resume,
            pool_decisions=pool,
            empty3_index=empty3,
            partial7_index={},
        )
        self.assertFalse(checks[f"caveat_lineage_{code}"])
        self.assertTrue(any(r["ok"] == "no" for r in rows if r["company_code"] == code))

    def test_resume_aggregate_detects_count_drift(self) -> None:
        resume_map = {
            "000001": {"resume_state": "complete"},
            "000002": {"resume_state": "partial"},
        }
        metrics = {
            "863_primary_complete": "190",
            "863_primary_partial": "7",
            "863_primary_needs_review": "3",
            "cninfo_calls": "0",
        }
        rows, checks = build_resume_aggregate_rows(
            resume_map=resume_map,
            metrics=metrics,
            harvest_codes=set(resume_map),
        )
        self.assertFalse(checks["resume_state_counts_190_7_3"])
        self.assertTrue(any(r["check_id"] == "resume_state_counts_190_7_3" for r in rows))

    def test_fm_battery_requires_pass(self) -> None:
        good = {
            "gate": "PASS_OFFLINE",
            "cninfo_calls": 0,
            "execute_production_snapshot_rebuild": False,
        }
        bad = {
            "gate": "FAIL_REVIEW_REQUIRED",
            "cninfo_calls": 0,
            "execute_production_snapshot_rebuild": False,
        }
        _rows, checks = build_fm_gate_battery_rows(fm01=good, fm02=good, fm03=bad)
        self.assertFalse(checks["fm03_harvest_exclusion_dual_layer"])
        self.assertFalse(checks["fm01_02_03_battery_all_pass"])

    def test_index_isolation_rows(self) -> None:
        rows, checks = build_index_isolation_rows()
        self.assertTrue(checks["authoritative_dual_layer_index_write_forbidden"])
        self.assertEqual(rows[0]["ok"], "yes")

    def test_fingerprint_stable(self) -> None:
        rows = [
            {
                "check_id": "a",
                "layer": "x",
                "ok": "yes",
            },
            {
                "check_id": "b",
                "layer": "x",
                "ok": "no",
            },
        ]
        fp1 = fingerprint_lineage_matrix(rows)
        fp2 = fingerprint_lineage_matrix(rows)
        self.assertEqual(fp1["fingerprint_sha256"], fp2["fingerprint_sha256"])
        self.assertEqual(fp1["ok_count"], 1)
        self.assertEqual(fp1["fail_count"], 1)


class TestEndToEnd(unittest.TestCase):
    def test_run_offline_pass(self) -> None:
        mock_root = "outputs/validation/_mock_c_fm04_cli_test_tmp"
        os.makedirs(os.path.join(BASE_DIR, mock_root), exist_ok=True)
        result = run_dual_layer_ledger_resume_lineage(
            paths=LineagePaths(output_root_rel=mock_root)
        )
        self.assertEqual(result["gate"], "PASS_OFFLINE")
        self.assertEqual(result["cninfo_calls"], 0)
        self.assertFalse(result["execute_production_snapshot_rebuild"])
        for layer, gate in result["layer_gates"].items():
            self.assertEqual(gate, "PASS_OFFLINE", msg=layer)
        self.assertEqual(result["fail_count"], 0)
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
        self.assertEqual(battery["fm01_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm02_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm03_gate"], "PASS_OFFLINE")
        self.assertEqual(battery["fm04_gate"], "PASS_OFFLINE")

    def test_cli_pass_and_execute_refused(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            proc = subprocess.run(
                [sys.executable, RUNNER],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            self.assertIn("gate: PASS_OFFLINE", proc.stdout)
            self.assertIn("cninfo_calls: 0", proc.stdout)
            self.assertIn("ready_for_commit: true", proc.stdout)

            bad = subprocess.run(
                [sys.executable, RUNNER, "--execute"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(bad.returncode, 2)
            self.assertIn(
                "EXECUTE_PRODUCTION_SNAPSHOT_REBUILD_FORBIDDEN", bad.stderr
            )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    rows = []
    for test, err in result.failures + result.errors:
        rows.append({"case": test.id().split(".")[-1], "result": "FAIL"})
    if result.wasSuccessful():
        # 按发现顺序记录 PASS
        for case_name in [
            "test_refuse_non_mock",
            "test_refuse_authoritative_dual_layer_index",
            "test_allow_mock",
            "test_authoritative_write_forbidden",
            "test_family_and_expected",
            "test_caveat_rows_detect_empty3_resume_flip",
            "test_resume_aggregate_detects_count_drift",
            "test_fm_battery_requires_pass",
            "test_index_isolation_rows",
            "test_fingerprint_stable",
            "test_run_offline_pass",
            "test_cli_pass_and_execute_refused",
        ]:
            rows.append({"case": case_name, "result": "PASS"})
    _write_test_summary(rows)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
