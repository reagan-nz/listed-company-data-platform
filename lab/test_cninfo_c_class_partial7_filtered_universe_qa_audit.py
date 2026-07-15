"""
CNINFO C-class Partial7 × Wave1 filtered_universe QA 审计单测（离线）。

覆盖：
  - filtered_universe 代码提取
  - 单行 reason reconcile（正常 / 泄漏 / 字段漂移）
  - 硬化 QA matrix 列追加
  - dry-run CLI → PASS_OFFLINE · 7/7
  - execute_production_snapshot_rebuild 硬拒绝

运行：
    python3 lab/test_cninfo_c_class_partial7_filtered_universe_qa_audit.py
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from typing import Dict, List

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402
from cninfo_c_class_partial7_filtered_universe_qa_audit import (  # noqa: E402
    EXPECTED_PARTIAL7_CASE_CODE,
    EXPECTED_PARTIAL7_CODES,
    audit_partial7_row,
    build_hardened_qa_matrix_rows,
    load_filtered_universe_codes,
    run_partial7_filtered_universe_audit,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    assert_execute_production_snapshot_rebuild_false,
)
from run_cninfo_c_class_partial7_filtered_universe_qa_audit_dryrun import (  # noqa: E402
    run_audit,
)

RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_partial7_filtered_universe_qa_audit_dryrun.py"
)
FILTERED_YAML = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/"
    "filtered_universe_included.yaml",
)
CAVEAT_LEDGER = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv",
)
RECONCILE_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv",
)
QA_MATRIX = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_partial7_offline_qa_matrix_20260714.csv",
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_partial7_filtered_universe_qa_audit_test_summary_20260715.md",
)


def _write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_filtered_yaml(path: str, codes: List[str]) -> None:
    # 最小 YAML：仅 companies 列表
    lines = ["companies:"]
    for code in codes:
        lines.append(f"- company_code: '{code}'")
        lines.append(f"  stock_code: '{code}'")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


class TestLoadFilteredUniverse(unittest.TestCase):
    def test_load_codes_from_temp_yaml(self) -> None:
        with tempfile.TemporaryDirectory(prefix="_mock_p7_qa_") as tmp:
            path = os.path.join(tmp, "filtered.yaml")
            _write_filtered_yaml(path, ["600000", "600006"])
            codes, count = load_filtered_universe_codes(path)
            self.assertEqual(codes, {"600000", "600006"})
            self.assertEqual(count, 2)

    @unittest.skipUnless(os.path.isfile(FILTERED_YAML), "Wave1 filtered yaml missing")
    def test_wave1_filtered_has_190_and_no_partial7(self) -> None:
        codes, count = load_filtered_universe_codes(FILTERED_YAML)
        self.assertEqual(count, 190)
        self.assertTrue(EXPECTED_PARTIAL7_CODES.isdisjoint(codes))


class TestAuditPartial7Row(unittest.TestCase):
    def _ok_sources(self) -> tuple:
        code = "600001"
        filtered: set = set()
        reconcile = {
            code: {
                "company_code": code,
                "case_id": "CE1E002",
                "company_name": "邯郸钢铁",
                "pool_decision": "excluded",
                "cohort_families": "partial7",
            }
        }
        ledger = {
            code: {
                "company_code": code,
                "case_id": "CE1E002",
                "company_name": "邯郸钢铁",
                "harvest_status": "partial",
                "caveat_class": "delisted_or_merged_partial_normalized",
                "disposition": "accept_with_caveat",
            }
        }
        qa = {
            "CE1E002": {
                "case_id": "CE1E002",
                "company_code": code,
                "caveat_type": "delisted_or_merged_partial_normalized",
                "evidence_gap": "normalized 4/10",
            }
        }
        return filtered, reconcile, ledger, qa

    def test_ok_row(self) -> None:
        filtered, reconcile, ledger, qa = self._ok_sources()
        row = audit_partial7_row(
            case_id="CE1E002",
            company_code="600001",
            filtered_included=filtered,
            reconcile_by_code=reconcile,
            ledger_by_code=ledger,
            qa_by_case=qa,
        )
        self.assertEqual(row["reason_reconcile_ok"], "yes")
        self.assertEqual(row["in_filtered_included"], "no")

    def test_leak_into_filtered_fails(self) -> None:
        filtered, reconcile, ledger, qa = self._ok_sources()
        filtered.add("600001")
        row = audit_partial7_row(
            case_id="CE1E002",
            company_code="600001",
            filtered_included=filtered,
            reconcile_by_code=reconcile,
            ledger_by_code=ledger,
            qa_by_case=qa,
        )
        self.assertEqual(row["reason_reconcile_ok"], "no")
        self.assertIn("partial_still_in_filtered_included", row["notes"])

    def test_disposition_drift_fails(self) -> None:
        filtered, reconcile, ledger, qa = self._ok_sources()
        ledger["600001"]["disposition"] = "promote_now"
        row = audit_partial7_row(
            case_id="CE1E002",
            company_code="600001",
            filtered_included=filtered,
            reconcile_by_code=reconcile,
            ledger_by_code=ledger,
            qa_by_case=qa,
        )
        self.assertEqual(row["reason_reconcile_ok"], "no")
        self.assertIn("ledger_disposition", row["notes"])


class TestHardenedMatrix(unittest.TestCase):
    def test_append_columns(self) -> None:
        audit_rows = [
            {
                "case_id": "CE1E002",
                "company_code": "600001",
                "in_filtered_included": "no",
                "reason_reconcile_ok": "yes",
                "ledger_caveat_class": "delisted_or_merged_partial_normalized",
                "ledger_disposition": "accept_with_caveat",
            }
        ]
        qa_rows = [
            {
                "case_id": "CE1E002",
                "company_code": "600001",
                "caveat_type": "x",
                "evidence_gap": "y",
            }
        ]
        hardened = build_hardened_qa_matrix_rows(audit_rows, qa_rows)
        self.assertEqual(hardened[0]["wave1_filtered_universe_check"], "excluded_ok")
        self.assertEqual(hardened[0]["reason_reconcile_ok"], "yes")


class TestExecuteGuard(unittest.TestCase):
    def test_execute_flag_forbidden(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_execute_production_snapshot_rebuild_false(True)


@unittest.skipUnless(
    all(os.path.isfile(p) for p in (FILTERED_YAML, CAVEAT_LEDGER, RECONCILE_CSV, QA_MATRIX)),
    "Wave1 / ledger / reconcile / qa matrix missing",
)
class TestEndToEndOffline(unittest.TestCase):
    def test_run_audit_function(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="_mock_p7_qa_out_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            # assert_safe_erad_audit_write_path 要求路径在 allowed root 下；
            # 使用 mock 目录名以绕过 production validation 保护。
            mock_root = os.path.join(tmp, "_mock_partial7_qa_audit")
            os.makedirs(mock_root, exist_ok=True)
            rel = os.path.relpath(mock_root, BASE_DIR).replace("\\", "/")
            metrics = run_audit(
                filtered_universe=os.path.relpath(FILTERED_YAML, BASE_DIR),
                caveat_ledger=os.path.relpath(CAVEAT_LEDGER, BASE_DIR),
                exclusion_reconcile=os.path.relpath(RECONCILE_CSV, BASE_DIR),
                offline_qa_matrix=os.path.relpath(QA_MATRIX, BASE_DIR),
                output_root=rel,
            )
            self.assertEqual(metrics["gate"], "PASS_OFFLINE")
            self.assertEqual(metrics["reason_reconcile_ok_count"], 7)
            self.assertEqual(metrics["leaked_into_filtered_count"], 0)
            self.assertEqual(metrics["filtered_company_count"], 190)
            self.assertTrue(
                os.path.isfile(
                    os.path.join(mock_root, "partial7_reason_reconcile.csv")
                )
            )

    def test_pure_audit_api(self) -> None:
        result = run_partial7_filtered_universe_audit(
            filtered_universe_yaml=FILTERED_YAML,
            caveat_ledger_csv=CAVEAT_LEDGER,
            exclusion_reconcile_csv=RECONCILE_CSV,
            offline_qa_matrix_csv=QA_MATRIX,
        )
        self.assertEqual(result.gate, "PASS_OFFLINE")
        self.assertEqual(len(result.rows), 7)
        self.assertTrue(all(r["reason_reconcile_ok"] == "yes" for r in result.rows))
        self.assertEqual(
            set(EXPECTED_PARTIAL7_CASE_CODE.keys()),
            {r["case_id"] for r in result.rows},
        )

    def test_cli_dryrun(self) -> None:
        out_root = (
            "outputs/validation/cninfo_c_class_erad_partial7_filtered_universe_qa_audit"
        )
        proc = subprocess.run(
            [
                sys.executable,
                RUNNER,
                "--filtered-universe",
                os.path.relpath(FILTERED_YAML, BASE_DIR),
                "--caveat-ledger",
                os.path.relpath(CAVEAT_LEDGER, BASE_DIR),
                "--exclusion-reconcile",
                os.path.relpath(RECONCILE_CSV, BASE_DIR),
                "--offline-qa-matrix",
                os.path.relpath(QA_MATRIX, BASE_DIR),
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
        self.assertEqual(payload["reason_reconcile_ok_count"], 7)


def _write_test_summary(success: bool, ran: int, failures: int, errors: int) -> None:
    lines = [
        "# CNINFO C 类 — Partial7 Filtered Universe QA Audit 单测摘要",
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
        "覆盖：filtered_universe 提取 · reason reconcile · 硬化矩阵 · "
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
