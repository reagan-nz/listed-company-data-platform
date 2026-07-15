#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 fund_industry_allocation — D-FM-37 further-scale offline smoke。

离线 only · 无 CNINFO · 无 live · 无 runner · 不 claim verified。
冻结：FIA first/next lock+live · AT/SD next-slice lock（只读 attestation）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_fund_industry_allocation_further_scale_offline.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import re
import sys
import unittest
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

COMPONENT = "fund_industry_allocation"
CASE_IDS = ("DFIA201", "DFIA202", "DFIA203", "DFIA204", "DFIA205")
EXCLUDED_CODES = {"688671", "301259"}
COARSE_INDUSTRIES = {"A", "B", "C", "*"}
# first-slice C26 不得作为 further-scale 唯一 found 锚
FORBIDDEN_INDUSTRY_CODES = {"C26", "C27", "I65", "J66"}

FIRST_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv"
)
NEXT_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv"
)
AT_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv"
)
SD_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv"
)

# D-FM-20 / D-FM-24 / D-FM-36 记录的 lock sha256；本任务必须保持
EXPECTED_FIA_FIRST_LOCK_SHA256 = (
    "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
)
EXPECTED_FIA_NEXT_LOCK_SHA256 = (
    "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
)
EXPECTED_AT_NEXT_LOCK_SHA256 = (
    "4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6"
)
EXPECTED_SD_NEXT_LOCK_SHA256 = (
    "c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f"
)

PLANNING_MD = (
    BASE_DIR
    / "plans"
    / "cninfo_d_class_fund_industry_allocation_further_scale_planning_20260715.md"
)
MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_candidate_matrix_20260715.csv"
)
SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_universe_draft_sketch_20260715.csv"
)
RECOMMENDATION_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_recommendation_20260715.md"
)
SUMMARY_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_planning_summary_20260715.md"
)
CHECKLIST_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_offline_prep_checklist_stub_20260715.csv"
)
NEXT_STEP_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_next_step_recommendation_20260715.md"
)
EVIDENCE_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_dfm37_further_scale_offline_20260715.md"
)
SCALE_MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_dfm37_further_scale_matrix_20260715.csv"
)
REGISTRY = BASE_DIR / "config" / "cninfo_d_class_source_registry_draft.yaml"

FIRST_SLICE_LIVE_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_first_slice"
    / "reports"
    / "d_class_fund_industry_allocation_first_slice_live_report.csv"
)
NEXT_SLICE_LIVE_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice"
    / "reports"
    / "d_class_fund_industry_allocation_next_slice_live_report.csv"
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class FundIndustryAllocationFurtherScaleOfflineTests(unittest.TestCase):
    """D-FM-37：further-scale sketch + FIA/AT/SD freeze + ESS no-blind-retry 文案。"""

    def test_artifacts_exist(self) -> None:
        for path in (
            PLANNING_MD,
            MATRIX_CSV,
            SKETCH_CSV,
            RECOMMENDATION_MD,
            SUMMARY_MD,
            CHECKLIST_CSV,
            NEXT_STEP_MD,
            EVIDENCE_MD,
            SCALE_MATRIX_CSV,
        ):
            self.assertTrue(path.is_file(), f"missing {path}")

    def test_fia_first_and_next_lock_sha256_unchanged(self) -> None:
        self.assertTrue(FIRST_SLICE_LOCK.is_file())
        self.assertTrue(NEXT_SLICE_LOCK.is_file())
        self.assertEqual(
            _sha256_file(FIRST_SLICE_LOCK),
            EXPECTED_FIA_FIRST_LOCK_SHA256,
            "FIA first-slice universe lock must not be mutated in D-FM-37",
        )
        self.assertEqual(
            _sha256_file(NEXT_SLICE_LOCK),
            EXPECTED_FIA_NEXT_LOCK_SHA256,
            "FIA next-slice universe lock must not be mutated in D-FM-37",
        )

    def test_at_sd_next_lock_sha256_unchanged(self) -> None:
        """只读 attestation：AT/SD next-slice lock 不得被本包改写。"""
        self.assertTrue(AT_NEXT_LOCK.is_file())
        self.assertTrue(SD_NEXT_LOCK.is_file())
        self.assertEqual(
            _sha256_file(AT_NEXT_LOCK),
            EXPECTED_AT_NEXT_LOCK_SHA256,
            "AT next-slice universe lock must not be mutated in D-FM-37",
        )
        self.assertEqual(
            _sha256_file(SD_NEXT_LOCK),
            EXPECTED_SD_NEXT_LOCK_SHA256,
            "SD next-slice universe lock must not be mutated in D-FM-37",
        )

    def test_fia_live_reports_still_present(self) -> None:
        """只读存在性：确认未删除 FIA first/next live 证据根。"""
        self.assertTrue(FIRST_SLICE_LIVE_REPORT.is_file())
        self.assertTrue(NEXT_SLICE_LIVE_REPORT.is_file())
        first_rows = _load_csv(FIRST_SLICE_LIVE_REPORT)
        next_rows = _load_csv(NEXT_SLICE_LIVE_REPORT)
        self.assertEqual(len(first_rows), 5)
        self.assertEqual(len(next_rows), 5)
        self.assertEqual(first_rows[0]["case_id"], "DFIA001")
        self.assertEqual(next_rows[0]["case_id"], "DFIA101")

    def test_universe_sketch_five_cases_matrix_completion(self) -> None:
        rows = _load_csv(SKETCH_CSV)
        self.assertEqual(len(rows), 5)
        self.assertEqual(tuple(r["case_id"] for r in rows), CASE_IDS)
        for row in rows:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["further_scale_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertIn("no_company_code", row["exclude_flags"])
            self.assertIn("exclude_company_event_schema", row["exclude_flags"])
            self.assertIn("exclude_688671", row["exclude_flags"])
            self.assertIn("exclude_301259", row["exclude_flags"])
            self.assertIn(
                "exclude_first_slice_C26_sole_anchor", row["exclude_flags"]
            )
            self.assertIn(
                "exclude_mutate_next_slice_DFIA101_105", row["exclude_flags"]
            )
            code = row["industry_code"]
            self.assertIn(code, COARSE_INDUSTRIES)
            self.assertNotIn(code, EXCLUDED_CODES)
            self.assertNotIn(code, FORBIDDEN_INDUSTRY_CODES)
            self.assertEqual(int(row["shared_probe_prefer"]), 3)
            self.assertEqual(int(row["total_request_cap"]), 5)

        # 矩阵补全：default B · 20260331 A · 20251231 * / A / B
        self.assertEqual(rows[0]["industry_code"], "B")
        self.assertEqual(rows[0]["query_mode"], "default")
        self.assertEqual(rows[1]["industry_code"], "A")
        self.assertEqual(rows[1]["query_mode"], "rdate")
        self.assertEqual(rows[1]["anchor_rdate"], "20260331")
        self.assertEqual(rows[1]["expected_behavior"], "captured_normal")
        self.assertEqual(rows[2]["industry_code"], "*")
        self.assertEqual(rows[2]["anchor_rdate"], "20251231")
        self.assertEqual(rows[2]["expected_behavior"], "captured_normal")
        self.assertEqual(rows[3]["industry_code"], "A")
        self.assertEqual(rows[3]["anchor_rdate"], "20251231")
        self.assertEqual(
            rows[3]["expected_behavior"], "captured_normal_or_empty_but_valid"
        )
        self.assertEqual(rows[4]["industry_code"], "B")
        self.assertEqual(rows[4]["anchor_rdate"], "20251231")
        self.assertEqual(
            rows[4]["expected_behavior"], "captured_normal_or_empty_but_valid"
        )

    def test_candidate_matrix_ranks_fia_primary_and_forbids_live_flip(self) -> None:
        rows = _load_csv(MATRIX_CSV)
        by_id = {r["option_id"]: r for r in rows}
        self.assertEqual(
            by_id["FIA_FURTHER_SCALE_OFFLINE"]["recommendation_rank"], "1"
        )
        self.assertEqual(
            by_id["FIA_FURTHER_SCALE_OFFLINE"]["status"], "primary_executed"
        )
        self.assertEqual(
            by_id["EQUITY_PLEDGE_ES_SHAREHOLDER_CHANGE_NEXT_SLICE_OFFLINE"][
                "status"
            ],
            "deferred",
        )
        self.assertEqual(by_id["AT_NEXT_SLICE_BOUNDED_LIVE"]["status"], "forbidden")
        self.assertEqual(by_id["SD_NEXT_SLICE_BOUNDED_LIVE"]["status"], "forbidden")
        self.assertEqual(by_id["ESS_H3_H4_BLIND_PROBE"]["status"], "forbidden")
        self.assertEqual(by_id["LEVEL2_IDLE"]["status"], "forbidden")
        self.assertEqual(by_id["DLC006R_REOPEN"]["status"], "forbidden")
        self.assertEqual(
            by_id["FIA_FIRST_OR_NEXT_SLICE_MUTATE"]["status"], "forbidden"
        )

    def test_planning_and_gates_text(self) -> None:
        planning = PLANNING_MD.read_text(encoding="utf-8")
        evidence = EVIDENCE_MD.read_text(encoding="utf-8")
        next_step = NEXT_STEP_MD.read_text(encoding="utf-8")
        for text in (planning, evidence, next_step):
            self.assertIn("READY_FOR_APPROVAL", text)
            self.assertIn("CNINFO", text)
            self.assertTrue(
                ("H3/H4" in text) or ("H3 / H4" in text) or ("h3_h4" in text.lower())
            )
            self.assertNotIn("verified_claim = true", text)
            self.assertNotIn("production_ready = true", text)

        self.assertIn("DFIA201", planning)
        self.assertIn("DFIA201", evidence)
        self.assertIn(
            "d_class_fund_industry_allocation_further_scale_planning_gate = READY_FOR_APPROVAL",
            planning,
        )
        self.assertIn("controller_execution_allowed = false", planning)
        self.assertIn("cninfo_calls = 0", evidence)
        self.assertIn("paused_pending_devtools", next_step)
        self.assertIn("FAIL_REVIEW_REQUIRED", next_step)
        self.assertIn("allow-list **不含** console logs", evidence)

    def test_scale_matrix_matches_sketch(self) -> None:
        sketch = {r["case_id"]: r for r in _load_csv(SKETCH_CSV)}
        scale = _load_csv(SCALE_MATRIX_CSV)
        self.assertEqual(len(scale), 5)
        for row in scale:
            self.assertEqual(int(row["cninfo_this_round"]), 0)
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            sk = sketch[row["case_id"]]
            self.assertEqual(row["industry_code"], sk["industry_code"])
            self.assertEqual(row["query_mode"], sk["query_mode"])
            self.assertEqual(row["anchor_rdate"], sk["anchor_rdate"])
            self.assertEqual(row["expected_behavior"], sk["expected_behavior"])

    def test_registry_fund_industry_still_present_unchanged_contract(self) -> None:
        self.assertTrue(REGISTRY.is_file())
        text = REGISTRY.read_text(encoding="utf-8")
        self.assertIn("source_id: fund_industry_allocation", text)
        self.assertIn("fund/industry", text)
        self.assertIn("d_industry_aggregate", text)
        self.assertIn("company_code_available: false", text)

    def test_no_network_imports_in_this_module(self) -> None:
        """本测试模块自身不得引入 requests（离线保证）。"""
        self.assertNotIn("requests", sys.modules)
        src = Path(__file__).read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"(?m)^\s*import\s+requests\b", src))
        self.assertIsNone(re.search(r"(?m)^\s*from\s+requests\b", src))

    def test_allow_list_excludes_console_logs(self) -> None:
        """allow-list 备注不得把 console log 列入可提交产物。"""
        evidence = EVIDENCE_MD.read_text(encoding="utf-8")
        checklist = CHECKLIST_CSV.read_text(encoding="utf-8")
        self.assertIn("不含** console logs", evidence)
        # checklist 可提及 exclude console logs，但不得把 console log 标为 ready 产物
        for line in checklist.splitlines():
            if "console" in line.lower() and "log" in line.lower():
                self.assertNotIn(",ready,", line)


if __name__ == "__main__":
    # 确保不依赖代理环境变量误触网
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(key, None)
    unittest.main()
