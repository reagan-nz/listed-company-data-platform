#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 abnormal_trading — D-FM-29 dense-day offline cite smoke。

离线 only · 无 CNINFO · 无 live · 无 runner · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_abnormal_trading_dense_day_cite_offline.py
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

AT_CASE_IDS = ("DAT101", "DAT102", "DAT103", "DAT104", "DAT105")
EXCLUDED_CODES = {"688671", "301259"}
FORBIDDEN_AT_TDATE = {"2026-07-03"}
CITED_TDATE = "2026-07-02"
ALTERNATE_TDATE = "2026-07-01"

AT_FIRST_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv"
)
SD_FIRST_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv"
)
FIA_NEXT_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv"
)
FIA_FIRST_SLICE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv"
)

EXPECTED_AT_LOCK_SHA256 = (
    "d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2"
)
EXPECTED_SD_LOCK_SHA256 = (
    "06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5"
)
EXPECTED_FIA_NEXT_LOCK_SHA256 = (
    "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
)
EXPECTED_FIA_FIRST_LOCK_SHA256 = (
    "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
)

CITE_PLAN_MD = (
    BASE_DIR
    / "plans"
    / "cninfo_d_class_abnormal_trading_dense_day_cite_20260715.md"
)
CANDIDATE_MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_dense_day_candidate_matrix_20260715.csv"
)
AT_SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_universe_draft_sketch_20260715.csv"
)
DECISION_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_dense_day_cite_decision_20260715.md"
)
SUMMARY_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_dense_day_cite_summary_20260715.md"
)
NEXT_STEP_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_dense_day_next_step_recommendation_20260715.md"
)
CAVEAT_LEDGER_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_dense_day_final_caveat_ledger.csv"
)
EVIDENCE_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_dfm29_dense_day_cite_offline_20260715.md"
)
MULTIDATE_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_table_sources_multidate_stability.csv"
)
SCALE_MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_at_sd_dfm28_next_slice_scale_matrix_20260715.csv"
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_csv(path: Path) -> List[Dict[str, str]]:
    # utf-8-sig：兼容既有 multidate 等带 BOM 的 CSV
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


class AbnormalTradingDenseDayCiteOfflineTests(unittest.TestCase):
    """D-FM-29：AT denser-day offline cite + closed-root freeze。"""

    def test_artifacts_exist(self) -> None:
        for path in (
            CITE_PLAN_MD,
            CANDIDATE_MATRIX_CSV,
            AT_SKETCH_CSV,
            DECISION_MD,
            SUMMARY_MD,
            NEXT_STEP_MD,
            CAVEAT_LEDGER_CSV,
            EVIDENCE_MD,
            MULTIDATE_CSV,
        ):
            self.assertTrue(path.is_file(), f"missing {path}")

    def test_closed_locks_unchanged(self) -> None:
        self.assertEqual(_sha256_file(AT_FIRST_SLICE_LOCK), EXPECTED_AT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_FIRST_SLICE_LOCK), EXPECTED_SD_LOCK_SHA256)
        self.assertEqual(
            _sha256_file(FIA_NEXT_SLICE_LOCK), EXPECTED_FIA_NEXT_LOCK_SHA256
        )
        self.assertEqual(
            _sha256_file(FIA_FIRST_SLICE_LOCK), EXPECTED_FIA_FIRST_LOCK_SHA256
        )

    def test_candidate_matrix_selects_2026_07_02(self) -> None:
        rows = _load_csv(CANDIDATE_MATRIX_CSV)
        self.assertEqual(len(rows), 3)
        by_tdate = {r["candidate_tdate"]: r for r in rows}
        self.assertEqual(by_tdate[CITED_TDATE]["decision"], "SELECTED")
        self.assertEqual(by_tdate[CITED_TDATE]["observed_total_rows"], "173")
        self.assertEqual(by_tdate["2026-07-03"]["decision"], "REJECTED")
        self.assertEqual(by_tdate[ALTERNATE_TDATE]["decision"], "ALTERNATE")
        for row in rows:
            self.assertEqual(row["cninfo_this_round"], "0")

    def test_multidate_source_rows_match_matrix(self) -> None:
        """只读确认矩阵数字来自既有 multidate 产物（无新 CNINFO）。"""
        multi = [
            r
            for r in _load_csv(MULTIDATE_CSV)
            if r.get("source_id") == "abnormal_trading"
        ]
        by_case = {r["test_case_id"]: r for r in multi}
        self.assertEqual(by_case["at_2026_07_02"]["observed_total_rows"], "173")
        self.assertEqual(by_case["at_2026_07_03"]["observed_total_rows"], "151")
        self.assertEqual(by_case["at_2026_07_01"]["observed_total_rows"], "127")
        for case_id in ("at_2026_07_02", "at_2026_07_03", "at_2026_07_01"):
            self.assertEqual(by_case[case_id]["records_path"], "marketList")
            self.assertEqual(by_case[case_id]["validation_status"], "sample_ok")

    def test_at_sketch_resolved_to_cited_tdate(self) -> None:
        rows = _load_csv(AT_SKETCH_CSV)
        self.assertEqual(len(rows), 5)
        self.assertEqual(tuple(r["case_id"] for r in rows), AT_CASE_IDS)
        for row in rows:
            self.assertEqual(row["anchor_tdate"], CITED_TDATE)
            self.assertNotIn(row["anchor_tdate"], FORBIDDEN_AT_TDATE)
            self.assertNotEqual(row["anchor_tdate"], "PENDING_DENSE_DAY_CITE")
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertEqual(row["dense_day_cite_task"], "D-FM-29")
            self.assertEqual(
                row["dense_day_cite_strength"],
                "offline_multidate_observed_total_rows",
            )
            self.assertIn("exclude_sparse_day_20260703_sole_found_anchor", row["exclude_flags"])
            self.assertIn("exclude_sole_needs_review", row["exclude_flags"])
            self.assertNotIn(row["company_code"], EXCLUDED_CODES)
            self.assertNotEqual(
                row["expected_behavior"], "captured_normal_or_needs_review"
            )
            self.assertEqual(int(row["shared_probe_prefer"]), 1)
        self.assertEqual(rows[4]["expected_behavior"], "empty_but_valid")

    def test_scale_matrix_at_rows_synced(self) -> None:
        at_sketch = {r["case_id"]: r for r in _load_csv(AT_SKETCH_CSV)}
        scale = [
            r
            for r in _load_csv(SCALE_MATRIX_CSV)
            if r["component"] == "abnormal_trading"
        ]
        self.assertEqual(len(scale), 5)
        for row in scale:
            sk = at_sketch[row["case_id"]]
            self.assertEqual(row["anchor_value"], CITED_TDATE)
            self.assertEqual(row["anchor_value"], sk["anchor_tdate"])
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertEqual(row["cninfo_this_round"], "0")

    def test_gates_and_non_claims(self) -> None:
        plan = CITE_PLAN_MD.read_text(encoding="utf-8")
        decision = DECISION_MD.read_text(encoding="utf-8")
        evidence = EVIDENCE_MD.read_text(encoding="utf-8")
        next_step = NEXT_STEP_MD.read_text(encoding="utf-8")
        for text in (plan, decision, evidence, next_step):
            self.assertIn("READY_FOR_APPROVAL", text)
            self.assertIn(CITED_TDATE, text)
            self.assertIn("OFFLINE_PROVISIONAL_CITE_2026_07_02", text)
            self.assertNotIn("verified_claim = true", text)
            self.assertNotIn("production_ready = true", text)
        self.assertIn(
            "d_class_abnormal_trading_dense_day_cite_gate = READY_FOR_APPROVAL",
            plan,
        )
        self.assertIn("cninfo_calls = 0", evidence)
        self.assertIn("draft_not_locked", evidence)
        self.assertIn("paused_pending_devtools", next_step)
        self.assertIn("at_next_slice_approval_package", next_step)
        # 禁止把 2026-07-03 选为 cite
        self.assertIn("REJECTED", CANDIDATE_MATRIX_CSV.read_text(encoding="utf-8"))

    def test_caveat_ledger_has_required_entries(self) -> None:
        rows = _load_csv(CAVEAT_LEDGER_CSV)
        ids = {r["caveat_id"] for r in rows}
        for needed in (
            "CAV-AT-DD-001",
            "CAV-AT-DD-002",
            "CAV-AT-DD-003",
            "CAV-AT-DD-005",
            "CAV-AT-DD-006",
        ):
            self.assertIn(needed, ids)

    def test_no_network_imports_in_this_module(self) -> None:
        self.assertNotIn("requests", sys.modules)
        src = Path(__file__).read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"(?m)^\s*import\s+requests\b", src))
        self.assertIsNone(re.search(r"(?m)^\s*from\s+requests\b", src))


if __name__ == "__main__":
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(key, None)
    unittest.main()
