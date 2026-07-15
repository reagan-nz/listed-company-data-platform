"""
CNINFO C-class Partial7 双层语义审计单测（离线）。

覆盖：
  - 单案 DLVR-P01–P04
  - PT tradingStatus=0 注解（CE1E061/067）
  - QA closure 累积双层证据索引（sibling · 不覆盖 empty3）
  - dry-run CLI → PASS_OFFLINE · 7/7 indexed · 10/10 cohort
  - execute_production_snapshot_rebuild 硬拒绝（API + CLI）

运行：
    python3 lab/test_cninfo_c_class_partial7_dual_layer_present_audit.py
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402
from cninfo_c_class_partial7_dual_layer_present_audit import (  # noqa: E402
    EXPECTED_PARTIAL7_CASE_CODE,
    EXPECTED_PARTIAL7_CODES,
    EXPECTED_PT_CASE_IDS,
    audit_partial7_case,
    build_qa_closure_partial7_dual_layer_evidence_index,
    count_http_error_envelopes,
    index_by_case_id,
    index_by_code,
    load_csv_rows,
    load_delisted_flag,
    load_trading_status,
    read_empty3_indexed_pass_count,
    run_partial7_dual_layer_present_audit,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    assert_execute_production_snapshot_rebuild_false,
)
from run_cninfo_c_class_partial7_dual_layer_present_audit_dryrun import (  # noqa: E402
    run_audit,
)

RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_c_class_partial7_dual_layer_present_audit_dryrun.py"
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
    "outputs/validation/cninfo_c_class_partial7_offline_qa_matrix_20260714.csv",
)
DUAL_LAYER_MATRIX = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_dual_layer_rule_matrix_20260714.csv",
)
EMPTY3_INDEX = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/"
    "qa_closure_dual_layer_evidence_index.csv",
)
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_partial7_dual_layer_present_audit_test_summary_20260715.md",
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


class TestExecuteGuard(unittest.TestCase):
    def test_execute_flag_forbidden(self) -> None:
        with self.assertRaises(RuntimeError):
            assert_execute_production_snapshot_rebuild_false(True)

    def test_cli_execute_flag_refused(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                RUNNER,
                "--execute-production-snapshot-rebuild",
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        combined = (proc.stderr or "") + (proc.stdout or "")
        self.assertTrue(
            "execute_production_snapshot_rebuild" in combined
            or "RuntimeError" in combined
            or "FORBIDDEN" in combined
            or proc.returncode != 0
        )


@unittest.skipUnless(_INPUTS_READY, "slice1 harvest / matrices missing")
class TestHarvestDisk(unittest.TestCase):
    def test_http_error_count_600001(self) -> None:
        http_err, biz_ok, notes = count_http_error_envelopes(HARVEST_ROOT, "600001")
        self.assertEqual(http_err, 6)
        self.assertEqual(biz_ok, 6)
        self.assertEqual(notes, [])

    def test_delisted_true_all_partial7(self) -> None:
        for code in EXPECTED_PARTIAL7_CODES:
            self.assertTrue(
                load_delisted_flag(HARVEST_ROOT, code),
                msg=f"expected delisted=true for {code}",
            )

    def test_pt_trading_status(self) -> None:
        self.assertEqual(load_trading_status(HARVEST_ROOT, "000003"), "0")
        self.assertEqual(load_trading_status(HARVEST_ROOT, "000015"), "0")
        self.assertNotEqual(load_trading_status(HARVEST_ROOT, "600001"), "0")


@unittest.skipUnless(_INPUTS_READY, "slice1 harvest / matrices missing")
class TestCaseAudit(unittest.TestCase):
    def test_single_case_all_rules_pass(self) -> None:
        status = index_by_code(load_csv_rows(STATUS_CSV))
        resume = index_by_code(load_csv_rows(RESUME_CSV))
        caveat = index_by_code(load_csv_rows(CAVEAT_LEDGER))
        offline = index_by_case_id(load_csv_rows(OFFLINE_MATRIX))
        row, rules = audit_partial7_case(
            case_id="CE1E002",
            company_code="600001",
            harvest_root=HARVEST_ROOT,
            status_by_code=status,
            resume_by_code=resume,
            caveat_by_code=caveat,
            offline_by_case=offline,
        )
        self.assertEqual(row["rules_all_pass"], "yes")
        self.assertEqual(len(rules), 4)
        self.assertTrue(all(r["result"] == "PASS" for r in rules))
        self.assertEqual(row["is_pt_annotated"], "no")

    def test_pt_case_annotated(self) -> None:
        status = index_by_code(load_csv_rows(STATUS_CSV))
        resume = index_by_code(load_csv_rows(RESUME_CSV))
        caveat = index_by_code(load_csv_rows(CAVEAT_LEDGER))
        offline = index_by_case_id(load_csv_rows(OFFLINE_MATRIX))
        row, rules = audit_partial7_case(
            case_id="CE1E061",
            company_code="000003",
            harvest_root=HARVEST_ROOT,
            status_by_code=status,
            resume_by_code=resume,
            caveat_by_code=caveat,
            offline_by_case=offline,
        )
        self.assertEqual(row["rules_all_pass"], "yes")
        self.assertEqual(row["is_pt_annotated"], "yes")
        self.assertEqual(row["trading_status"], "0")
        self.assertTrue(all(r["result"] == "PASS" for r in rules))


@unittest.skipUnless(_INPUTS_READY, "slice1 harvest / matrices missing")
class TestEndToEndOffline(unittest.TestCase):
    def test_pure_audit_api(self) -> None:
        result = run_partial7_dual_layer_present_audit(
            harvest_root=HARVEST_ROOT,
            status_csv=STATUS_CSV,
            resume_audit_csv=RESUME_CSV,
            caveat_ledger_csv=CAVEAT_LEDGER,
            offline_matrix_csv=OFFLINE_MATRIX,
            dual_layer_matrix_csv=DUAL_LAYER_MATRIX,
        )
        self.assertEqual(result.gate, "PASS_OFFLINE")
        self.assertEqual(len(result.rows), 7)
        self.assertTrue(all(r["rules_all_pass"] == "yes" for r in result.rows))
        self.assertEqual(
            set(EXPECTED_PARTIAL7_CASE_CODE.keys()),
            {r["case_id"] for r in result.rows},
        )
        self.assertEqual(len(result.rule_rows), 28)
        pt_rows = [r for r in result.rows if r["case_id"] in EXPECTED_PT_CASE_IDS]
        self.assertEqual(len(pt_rows), 2)
        self.assertTrue(all(r["is_pt_annotated"] == "yes" for r in pt_rows))

    def test_qa_closure_index_builder(self) -> None:
        result = run_partial7_dual_layer_present_audit(
            harvest_root=HARVEST_ROOT,
            status_csv=STATUS_CSV,
            resume_audit_csv=RESUME_CSV,
            caveat_ledger_csv=CAVEAT_LEDGER,
            offline_matrix_csv=OFFLINE_MATRIX,
            dual_layer_matrix_csv=DUAL_LAYER_MATRIX,
        )
        empty3_pass = read_empty3_indexed_pass_count(EMPTY3_INDEX)
        index = build_qa_closure_partial7_dual_layer_evidence_index(
            audit_rows=result.rows,
            rule_rows=result.rule_rows,
            caveat_ledger_rows=load_csv_rows(CAVEAT_LEDGER),
            audit_gate=result.gate,
            audit_csv_ref="outputs/validation/mock/partial7_audit.csv",
            rule_matrix_ref="outputs/validation/mock/partial7_rules.csv",
            empty3_indexed_pass_count=empty3_pass,
            empty3_index_csv_ref=os.path.relpath(EMPTY3_INDEX, BASE_DIR),
        )
        self.assertEqual(index.gate, "PASS_OFFLINE")
        self.assertEqual(len(index.rows), 7)
        self.assertTrue(all(r["index_status"] == "indexed_pass" for r in index.rows))
        self.assertTrue(index.checks["original_caveat_ledger_unmutated"])
        self.assertTrue(index.checks["empty3_index_file_not_overwritten"])
        if empty3_pass == 3:
            self.assertTrue(index.checks["full_10_caveat_cohort_indexed"])
        self.assertEqual(len(index.cohort_coverage_rows), 3)

    def test_run_audit_function(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="_mock_p7dl_out_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            mock_root = os.path.join(tmp, "_mock_partial7_dual_layer_audit")
            mock_index = os.path.join(tmp, "_mock_qa_closure_dual_layer_index")
            os.makedirs(mock_root, exist_ok=True)
            os.makedirs(mock_index, exist_ok=True)
            # 复制 empty3 索引到 mock，验证不覆盖
            empty3_src = EMPTY3_INDEX
            empty3_dst = os.path.join(
                mock_index, "qa_closure_dual_layer_evidence_index.csv"
            )
            if os.path.isfile(empty3_src):
                with open(empty3_src, encoding="utf-8") as fh:
                    content = fh.read()
                with open(empty3_dst, "w", encoding="utf-8") as fh:
                    fh.write(content)
                mtime_before = os.path.getmtime(empty3_dst)
            else:
                mtime_before = None
                # 无 empty3 时写入最小 3 行 indexed_pass 以满足 cohort check
                with open(empty3_dst, "w", encoding="utf-8", newline="") as fh:
                    writer = csv.DictWriter(
                        fh,
                        fieldnames=[
                            "case_id",
                            "company_code",
                            "index_status",
                        ],
                    )
                    writer.writeheader()
                    for case_id, code in (
                        ("CE1E176", "688031"),
                        ("CE1E188", "688062"),
                        ("CE1E193", "688071"),
                    ):
                        writer.writerow(
                            {
                                "case_id": case_id,
                                "company_code": code,
                                "index_status": "indexed_pass",
                            }
                        )
                mtime_before = os.path.getmtime(empty3_dst)

            rel = os.path.relpath(mock_root, BASE_DIR).replace("\\", "/")
            rel_index = os.path.relpath(mock_index, BASE_DIR).replace("\\", "/")
            rel_empty3 = os.path.relpath(empty3_dst, BASE_DIR).replace("\\", "/")
            metrics = run_audit(
                harvest_root=os.path.relpath(HARVEST_ROOT, BASE_DIR),
                status_csv=os.path.relpath(STATUS_CSV, BASE_DIR),
                resume_audit_csv=os.path.relpath(RESUME_CSV, BASE_DIR),
                caveat_ledger=os.path.relpath(CAVEAT_LEDGER, BASE_DIR),
                offline_matrix=os.path.relpath(OFFLINE_MATRIX, BASE_DIR),
                dual_layer_matrix=os.path.relpath(DUAL_LAYER_MATRIX, BASE_DIR),
                output_root=rel,
                qa_index_root=rel_index,
                empty3_index_csv=rel_empty3,
            )
            self.assertEqual(metrics["gate"], "PASS_OFFLINE")
            self.assertEqual(metrics["index_gate"], "PASS_OFFLINE")
            self.assertEqual(metrics["rules_all_pass_count"], 7)
            self.assertEqual(metrics["indexed_pass_count"], 7)
            self.assertEqual(metrics["empty3_indexed_pass_count"], 3)
            self.assertEqual(metrics["full_caveat_cohort_indexed"], 10)
            self.assertEqual(metrics["pt_annotated_count"], 2)
            self.assertTrue(metrics["capability_gain"])
            self.assertTrue(metrics["ready_for_commit"])
            self.assertFalse(metrics["original_qa_closure_caveat_ledger_mutated"])
            self.assertFalse(metrics["empty3_index_overwritten"])
            self.assertEqual(os.path.getmtime(empty3_dst), mtime_before)
            self.assertTrue(
                os.path.isfile(
                    os.path.join(mock_root, "partial7_dual_layer_present_audit.csv")
                )
            )
            self.assertTrue(
                os.path.isfile(
                    os.path.join(
                        mock_index,
                        "qa_closure_dual_layer_evidence_index_partial7.csv",
                    )
                )
            )
            self.assertTrue(
                os.path.isfile(
                    os.path.join(
                        mock_index, "qa_closure_dual_layer_cohort_coverage.csv"
                    )
                )
            )

    def test_cli_dryrun(self) -> None:
        out_root = (
            "outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit"
        )
        index_root = (
            "outputs/validation/"
            "cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index"
        )
        empty3_mtime = (
            os.path.getmtime(EMPTY3_INDEX) if os.path.isfile(EMPTY3_INDEX) else None
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
                "--qa-index-root",
                index_root,
                "--empty3-index-csv",
                os.path.relpath(EMPTY3_INDEX, BASE_DIR),
            ],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stderr or proc.stdout)
        self.assertIn("PASS_OFFLINE", proc.stdout)
        self.assertIn("ready_for_commit: True", proc.stdout)
        self.assertIn("full_cohort=10/10", proc.stdout)
        if empty3_mtime is not None:
            self.assertEqual(os.path.getmtime(EMPTY3_INDEX), empty3_mtime)
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    BASE_DIR,
                    out_root,
                    "partial7_dual_layer_present_audit.csv",
                )
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    BASE_DIR,
                    index_root,
                    "qa_closure_dual_layer_evidence_index_partial7.csv",
                )
            )
        )


def _write_test_summary(result: unittest.TestResult) -> None:
    lines = [
        "# CNINFO C 类 — Partial7 双层 Present 审计单测摘要",
        "",
        "_生成时间：2026-07-15 · offline · CNINFO=0 · task C-R16-03_",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        f"| result | **{'OK' if result.wasSuccessful() else 'FAIL'}** |",
        f"| tests_run | **{result.testsRun}** |",
        f"| failures | **{len(result.failures)}** |",
        f"| errors | **{len(result.errors)}** |",
        "",
        "覆盖：DLVR-P01–P04 · PT tradingStatus=0 注解 · QA closure 双层索引 "
        "sibling · 10/10 caveat cohort · CLI PASS_OFFLINE · execute 硬拒绝 · "
        "empty3 索引不覆盖。",
        "",
    ]
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    _write_test_summary(result)
    raise SystemExit(0 if result.wasSuccessful() else 1)
