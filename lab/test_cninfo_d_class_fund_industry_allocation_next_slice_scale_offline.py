#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 fund_industry_allocation — D-FM-23 next-slice scale offline smoke。

离线 only · 无 CNINFO · 无 live · 无 runner · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_fund_industry_allocation_next_slice_scale_offline.py
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
CASE_IDS = ("DFIA101", "DFIA102", "DFIA103", "DFIA104", "DFIA105")
EXCLUDED_CODES = {"688671", "301259"}
COARSE_INDUSTRIES = {"A", "B", "C", "*"}
# first-slice C26 不得作为 next-slice 唯一 found 锚（可出现在说明中，但 industry_code 列禁止）
FORBIDDEN_INDUSTRY_CODES = {"C26", "C27", "I65", "J66"}

FIRST_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv"
)
# D-FM-20 closure 记录的 lock sha256；本任务必须保持
EXPECTED_LOCK_SHA256 = (
    "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
)

PLANNING_MD = (
    BASE_DIR
    / "plans"
    / "cninfo_d_class_fund_industry_allocation_next_slice_scale_planning_20260715.md"
)
MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_candidate_matrix_20260715.csv"
)
SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_universe_draft_sketch_20260715.csv"
)
RECOMMENDATION_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_recommendation_20260715.md"
)
SUMMARY_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_planning_summary_20260715.md"
)
CHECKLIST_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_offline_prep_checklist_stub_20260715.csv"
)
NEXT_STEP_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_next_step_recommendation_20260715.md"
)
EVIDENCE_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_dfm23_next_slice_scale_offline_20260715.md"
)
SCALE_MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_dfm23_next_slice_scale_matrix_20260715.csv"
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


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class FundIndustryAllocationNextSliceScaleOfflineTests(unittest.TestCase):
    """D-FM-23：next-slice sketch + first-slice freeze + ESS no-blind-retry 文案。"""

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

    def test_first_slice_lock_sha256_unchanged(self) -> None:
        self.assertTrue(FIRST_SLICE_LOCK.is_file())
        digest = _sha256_file(FIRST_SLICE_LOCK)
        self.assertEqual(
            digest,
            EXPECTED_LOCK_SHA256,
            "first-slice universe lock must not be mutated in D-FM-23",
        )

    def test_first_slice_live_report_still_present(self) -> None:
        """只读存在性：确认未删除 first-slice live 证据根。"""
        self.assertTrue(FIRST_SLICE_LIVE_REPORT.is_file())
        rows = _load_csv(FIRST_SLICE_LIVE_REPORT)
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["case_id"], "DFIA001")

    def test_universe_sketch_five_cases_coarse_industries(self) -> None:
        rows = _load_csv(SKETCH_CSV)
        self.assertEqual(len(rows), 5)
        self.assertEqual(tuple(r["case_id"] for r in rows), CASE_IDS)
        for row in rows:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["next_slice_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertIn("no_company_code", row["exclude_flags"])
            self.assertIn("exclude_company_event_schema", row["exclude_flags"])
            self.assertIn("exclude_688671", row["exclude_flags"])
            self.assertIn("exclude_301259", row["exclude_flags"])
            self.assertIn(
                "exclude_first_slice_C26_sole_anchor", row["exclude_flags"]
            )
            code = row["industry_code"]
            self.assertIn(code, COARSE_INDUSTRIES)
            self.assertNotIn(code, EXCLUDED_CODES)
            self.assertNotIn(code, FORBIDDEN_INDUSTRY_CODES)
            self.assertEqual(int(row["shared_probe_prefer"]), 3)
            self.assertEqual(int(row["total_request_cap"]), 5)

        self.assertEqual(rows[0]["industry_code"], "A")
        self.assertEqual(rows[0]["query_mode"], "default")
        self.assertEqual(rows[1]["industry_code"], "C")
        self.assertEqual(rows[2]["industry_code"], "*")
        self.assertEqual(rows[2]["query_mode"], "rdate")
        self.assertEqual(rows[2]["anchor_rdate"], "20260331")
        self.assertEqual(rows[2]["expected_behavior"], "captured_normal")
        self.assertEqual(rows[3]["industry_code"], "B")
        self.assertEqual(rows[3]["anchor_rdate"], "20260331")
        self.assertEqual(rows[4]["industry_code"], "C")
        self.assertEqual(rows[4]["anchor_rdate"], "20251231")
        self.assertEqual(
            rows[4]["expected_behavior"], "captured_normal_or_empty_but_valid"
        )

    def test_candidate_matrix_ranks_fia_primary_and_forbids_h3_h4(self) -> None:
        rows = _load_csv(MATRIX_CSV)
        by_id = {r["option_id"]: r for r in rows}
        self.assertEqual(by_id["FIA_NEXT_SLICE_SCALE_OFFLINE"]["recommendation_rank"], "1")
        self.assertEqual(by_id["FIA_NEXT_SLICE_SCALE_OFFLINE"]["status"], "primary_executed")
        self.assertEqual(by_id["ESS_H3_H4_BLIND_PROBE"]["status"], "forbidden")
        self.assertEqual(by_id["LEVEL2_IDLE"]["status"], "forbidden")
        self.assertEqual(by_id["DLC006R_REOPEN"]["status"], "forbidden")

    def test_planning_and_gates_text(self) -> None:
        planning = PLANNING_MD.read_text(encoding="utf-8")
        evidence = EVIDENCE_MD.read_text(encoding="utf-8")
        next_step = NEXT_STEP_MD.read_text(encoding="utf-8")
        for text in (planning, evidence, next_step):
            self.assertIn("READY_FOR_APPROVAL", text)
            self.assertIn("CNINFO", text)
            # 禁止盲探 H3/H4
            self.assertTrue(
                ("H3/H4" in text) or ("H3 / H4" in text) or ("h3_h4" in text.lower())
            )
            self.assertNotIn("verified_claim = true", text)
            self.assertNotIn("production_ready = true", text)

        # sketch 命名空间在 planning / evidence 中必须出现
        self.assertIn("DFIA101", planning)
        self.assertIn("DFIA101", evidence)
        self.assertIn(
            "d_class_fund_industry_allocation_next_slice_scale_planning_gate = READY_FOR_APPROVAL",
            planning,
        )
        self.assertIn("cninfo_calls = 0", evidence)
        self.assertIn("paused_pending_devtools", next_step)
        self.assertIn("FAIL_REVIEW_REQUIRED", next_step)

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
        # 用正则锚定真实 import 行，避免 assert 字符串自引用误报
        self.assertIsNone(re.search(r"(?m)^\s*import\s+requests\b", src))
        self.assertIsNone(re.search(r"(?m)^\s*from\s+requests\b", src))


if __name__ == "__main__":
    # 确保不依赖代理环境变量误触网
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(key, None)
    unittest.main()
