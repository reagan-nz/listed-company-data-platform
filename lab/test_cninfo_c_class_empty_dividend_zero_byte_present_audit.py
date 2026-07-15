"""
CNINFO C-class Empty-Dividend 零字节 present 双层语义审计单测（离线）。

覆盖：
  - ledger/audit present 语义分叉
  - 零字节 dividend 发现
  - 单案 DLVR-E01–E05
  - dry-run CLI → PASS_OFFLINE · 3/3
  - execute_production_snapshot_rebuild 硬拒绝

运行：
    python3 lab/test_cninfo_c_class_empty_dividend_zero_byte_present_audit.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_empty_dividend_zero_byte_present_audit import (  # noqa: E402
    DIVIDEND_SOURCE_ID,
    EXPECTED_EMPTY_DIVIDEND_CASE_CODE,
    EXPECTED_EMPTY_DIVIDEND_CODES,
    audit_content_present,
    audit_empty_dividend_case,
    count_dual_layer_sources,
    discover_zero_byte_dividend_codes,
    ledger_file_present,
    run_empty_dividend_zero_byte_present_audit,
)
from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    assert_execute_production_snapshot_rebuild_false,
)
from run_cninfo_c_class_empty_dividend_zero_byte_present_audit_dryrun import (  # noqa: E402
    run_audit,
)

RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_empty_dividend_zero_byte_present_audit_dryrun.py"
)
HARVEST_ROOT = os.path.join(
    BASE_DIR, "outputs/harvest/cninfo_c_class/fuller_market_slice1_200"
)
STATUS_CSV = os.path.join(HARVEST_ROOT, "quality/company_harvest_status.csv")
RESUME_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/"
    "reports/c_class_erad_harvest_resume_audit_report.csv",
)
CAVEAT_LEDGER = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv",
)
OFFLINE_MATRIX = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_empty_dividend_offline_matrix_20260714.csv",
)
DUAL_LAYER_MATRIX = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_dual_layer_rule_matrix_20260714.csv",
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_empty_dividend_zero_byte_present_audit_test_summary_20260715.md",
)

_INPUTS_READY = all(
    os.path.exists(p)
    for p in (
        HARVEST_ROOT,
        STATUS_CSV,
        RESUME_CSV,
        CAVEAT_LEDGER,
        OFFLINE_MATRIX,
        DUAL_LAYER_MATRIX,
    )
)


class TestPresentSemantics(unittest.TestCase):
    def test_zero_byte_ledger_yes_audit_no(self) -> None:
        with tempfile.TemporaryDirectory(prefix="_mock_edzb_") as tmp:
            path = os.path.join(tmp, "x.jsonl")
            with open(path, "wb") as fh:
                fh.write(b"")
            self.assertTrue(ledger_file_present(path))
            self.assertFalse(audit_content_present(path))

    def test_jsonl_nonempty_line_audit_yes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="_mock_edzb_") as tmp:
            path = os.path.join(tmp, "x.jsonl")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write('{"a":1}\n')
            self.assertTrue(ledger_file_present(path))
            self.assertTrue(audit_content_present(path))

    def test_json_size_le_2_audit_no(self) -> None:
        with tempfile.TemporaryDirectory(prefix="_mock_edzb_") as tmp:
            path = os.path.join(tmp, "x.json")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("{}")
            self.assertTrue(ledger_file_present(path))
            self.assertFalse(audit_content_present(path))


@unittest.skipUnless(_INPUTS_READY, "slice1 harvest / matrices missing")
class TestHarvestDisk(unittest.TestCase):
    def test_discover_exactly_three_zero_byte(self) -> None:
        codes = discover_zero_byte_dividend_codes(HARVEST_ROOT)
        self.assertEqual(codes, set(EXPECTED_EMPTY_DIVIDEND_CODES))

    def test_count_dual_layer_for_688031(self) -> None:
        ledger_n, audit_n, per = count_dual_layer_sources(HARVEST_ROOT, "688031")
        self.assertEqual(ledger_n, 10)
        self.assertEqual(audit_n, 9)
        div = per[DIVIDEND_SOURCE_ID]
        self.assertEqual(div["ledger_present"], "yes")
        self.assertEqual(div["audit_present"], "no")
        self.assertEqual(div["byte_size"], "0")


@unittest.skipUnless(_INPUTS_READY, "slice1 harvest / matrices missing")
class TestCaseAudit(unittest.TestCase):
    def test_single_case_all_rules_pass(self) -> None:
        from cninfo_c_class_empty_dividend_zero_byte_present_audit import (
            index_by_case_id,
            index_by_code,
            load_csv_rows,
        )

        status = index_by_code(load_csv_rows(STATUS_CSV))
        resume = index_by_code(load_csv_rows(RESUME_CSV))
        caveat = index_by_code(load_csv_rows(CAVEAT_LEDGER))
        offline = index_by_case_id(load_csv_rows(OFFLINE_MATRIX))
        row, rules = audit_empty_dividend_case(
            case_id="CE1E176",
            company_code="688031",
            harvest_root=HARVEST_ROOT,
            status_by_code=status,
            resume_by_code=resume,
            caveat_by_code=caveat,
            offline_by_case=offline,
        )
        self.assertEqual(row["rules_all_pass"], "yes")
        self.assertEqual(len(rules), 5)
        self.assertTrue(all(r["result"] == "PASS" for r in rules))


class TestExecuteGuard(unittest.TestCase):
    def test_execute_flag_forbidden(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_execute_production_snapshot_rebuild_false(True)


@unittest.skipUnless(_INPUTS_READY, "slice1 harvest / matrices missing")
class TestEndToEndOffline(unittest.TestCase):
    def test_pure_audit_api(self) -> None:
        result = run_empty_dividend_zero_byte_present_audit(
            harvest_root=HARVEST_ROOT,
            status_csv=STATUS_CSV,
            resume_audit_csv=RESUME_CSV,
            caveat_ledger_csv=CAVEAT_LEDGER,
            offline_matrix_csv=OFFLINE_MATRIX,
            dual_layer_matrix_csv=DUAL_LAYER_MATRIX,
        )
        self.assertEqual(result.gate, "PASS_OFFLINE")
        self.assertEqual(len(result.rows), 3)
        self.assertTrue(all(r["rules_all_pass"] == "yes" for r in result.rows))
        self.assertEqual(
            set(EXPECTED_EMPTY_DIVIDEND_CASE_CODE.keys()),
            {r["case_id"] for r in result.rows},
        )
        self.assertEqual(len(result.rule_rows), 15)

    def test_run_audit_function(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="_mock_edzb_out_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            mock_root = os.path.join(tmp, "_mock_empty_dividend_zb_audit")
            os.makedirs(mock_root, exist_ok=True)
            rel = os.path.relpath(mock_root, BASE_DIR).replace("\\", "/")
            metrics = run_audit(
                harvest_root=os.path.relpath(HARVEST_ROOT, BASE_DIR),
                status_csv=os.path.relpath(STATUS_CSV, BASE_DIR),
                resume_audit_csv=os.path.relpath(RESUME_CSV, BASE_DIR),
                caveat_ledger=os.path.relpath(CAVEAT_LEDGER, BASE_DIR),
                offline_matrix=os.path.relpath(OFFLINE_MATRIX, BASE_DIR),
                dual_layer_matrix=os.path.relpath(DUAL_LAYER_MATRIX, BASE_DIR),
                output_root=rel,
            )
            self.assertEqual(metrics["gate"], "PASS_OFFLINE")
            self.assertEqual(metrics["rules_all_pass_count"], 3)
            self.assertEqual(metrics["disk_zero_byte_count"], 3)
            self.assertTrue(metrics["capability_gain"])
            self.assertTrue(metrics["ready_for_commit"])
            self.assertTrue(
                os.path.isfile(
                    os.path.join(
                        mock_root, "empty_dividend_zero_byte_present_audit.csv"
                    )
                )
            )

    def test_cli_dryrun(self) -> None:
        out_root = (
            "outputs/validation/cninfo_c_class_empty_dividend_zero_byte_present_audit"
        )
        proc = subprocess.run(
            [
                sys.executable,
                RUNNER,
                "--harvest-root",
                os.path.relpath(HARVEST_ROOT, BASE_DIR),
                "--status-csv",
                os.path.relpath(STATUS_CSV, BASE_DIR),
                "--resume-audit-csv",
                os.path.relpath(RESUME_CSV, BASE_DIR),
                "--caveat-ledger",
                os.path.relpath(CAVEAT_LEDGER, BASE_DIR),
                "--offline-matrix",
                os.path.relpath(OFFLINE_MATRIX, BASE_DIR),
                "--dual-layer-matrix",
                os.path.relpath(DUAL_LAYER_MATRIX, BASE_DIR),
                "--output-root",
                out_root,
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr + proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["gate"], "PASS_OFFLINE")
        self.assertEqual(payload["rules_all_pass_count"], 3)
        self.assertEqual(payload["cninfo_calls"], 0)


def _write_test_summary(success: bool, ran: int, failures: int, errors: int) -> None:
    lines = [
        "# CNINFO C 类 — Empty-Dividend 零字节 Present 审计单测摘要",
        "",
        "_生成时间：2026-07-15 · offline · CNINFO=0_",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        f"| result | **{'OK' if success else 'FAILED'}** |",
        f"| tests_run | **{ran}** |",
        f"| failures | **{failures}** |",
        f"| errors | **{errors}** |",
        "",
        "覆盖：ledger/audit present 分叉 · 零字节发现 · DLVR-E01–E05 · "
        "CLI PASS_OFFLINE · execute 硬拒绝。",
        "",
    ]
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    _write_test_summary(
        result.wasSuccessful(),
        result.testsRun,
        len(result.failures),
        len(result.errors),
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
