#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 AT/SD — D-FM-28 next-slice scale offline smoke。

离线 only · 无 CNINFO · 无 live · 无 runner · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_at_sd_next_slice_scale_offline.py
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
SD_CASE_IDS = ("DSD101", "DSD102", "DSD103", "DSD104", "DSD105")
EXCLUDED_CODES = {"688671", "301259"}
FORBIDDEN_AT_TDATE = {"2026-07-03"}

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

EXPECTED_AT_LOCK_SHA256 = (
    "d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2"
)
EXPECTED_SD_LOCK_SHA256 = (
    "06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5"
)
EXPECTED_FIA_NEXT_LOCK_SHA256 = (
    "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
)

PLANNING_MD = (
    BASE_DIR
    / "plans"
    / "cninfo_d_class_at_sd_next_slice_scale_planning_20260715.md"
)
MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_at_sd_next_slice_candidate_matrix_20260715.csv"
)
AT_SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_universe_draft_sketch_20260715.csv"
)
SD_SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_universe_draft_sketch_20260715.csv"
)
RECOMMENDATION_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_at_sd_next_slice_recommendation_20260715.md"
)
SUMMARY_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_at_sd_next_slice_planning_summary_20260715.md"
)
CHECKLIST_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_at_sd_next_slice_offline_prep_checklist_stub_20260715.csv"
)
NEXT_STEP_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_at_sd_next_slice_next_step_recommendation_20260715.md"
)
EVIDENCE_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_at_sd_dfm28_next_slice_scale_offline_20260715.md"
)
SCALE_MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_at_sd_dfm28_next_slice_scale_matrix_20260715.csv"
)
CAVEAT_LEDGER_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_at_sd_next_slice_final_caveat_ledger.csv"
)
REGISTRY = BASE_DIR / "config" / "cninfo_d_class_source_registry_draft.yaml"

AT_FIRST_SLICE_LIVE_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_first_slice"
    / "reports"
    / "d_class_abnormal_trading_first_slice_live_report.csv"
)
SD_FIRST_SLICE_LIVE_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_first_slice"
    / "reports"
    / "d_class_shareholder_data_first_slice_live_report.csv"
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class AtSdNextSliceScaleOfflineTests(unittest.TestCase):
    """D-FM-28：AT/SD next-slice sketch + first-slice / FIA freeze。"""

    def test_artifacts_exist(self) -> None:
        for path in (
            PLANNING_MD,
            MATRIX_CSV,
            AT_SKETCH_CSV,
            SD_SKETCH_CSV,
            RECOMMENDATION_MD,
            SUMMARY_MD,
            CHECKLIST_CSV,
            NEXT_STEP_MD,
            EVIDENCE_MD,
            SCALE_MATRIX_CSV,
            CAVEAT_LEDGER_CSV,
        ):
            self.assertTrue(path.is_file(), f"missing {path}")

    def test_at_first_slice_lock_sha256_unchanged(self) -> None:
        self.assertTrue(AT_FIRST_SLICE_LOCK.is_file())
        digest = _sha256_file(AT_FIRST_SLICE_LOCK)
        self.assertEqual(
            digest,
            EXPECTED_AT_LOCK_SHA256,
            "AT first-slice universe lock must not be mutated in D-FM-28",
        )

    def test_sd_first_slice_lock_sha256_unchanged(self) -> None:
        self.assertTrue(SD_FIRST_SLICE_LOCK.is_file())
        digest = _sha256_file(SD_FIRST_SLICE_LOCK)
        self.assertEqual(
            digest,
            EXPECTED_SD_LOCK_SHA256,
            "SD first-slice universe lock must not be mutated in D-FM-28",
        )

    def test_fia_next_slice_lock_sha256_unchanged(self) -> None:
        self.assertTrue(FIA_NEXT_SLICE_LOCK.is_file())
        digest = _sha256_file(FIA_NEXT_SLICE_LOCK)
        self.assertEqual(
            digest,
            EXPECTED_FIA_NEXT_LOCK_SHA256,
            "FIA next-slice universe lock must not be mutated in D-FM-28",
        )

    def test_first_slice_live_reports_still_present(self) -> None:
        """只读存在性：确认未删除 AT/SD first-slice live 证据根。"""
        self.assertTrue(AT_FIRST_SLICE_LIVE_REPORT.is_file())
        at_rows = _load_csv(AT_FIRST_SLICE_LIVE_REPORT)
        self.assertEqual(len(at_rows), 5)
        self.assertEqual(at_rows[0]["case_id"], "DAT001")

        self.assertTrue(SD_FIRST_SLICE_LIVE_REPORT.is_file())
        sd_rows = _load_csv(SD_FIRST_SLICE_LIVE_REPORT)
        self.assertEqual(len(sd_rows), 5)
        self.assertEqual(sd_rows[0]["case_id"], "DSD001")

    def test_at_universe_sketch_five_cases_pending_dense_day(self) -> None:
        rows = _load_csv(AT_SKETCH_CSV)
        self.assertEqual(len(rows), 5)
        self.assertEqual(tuple(r["case_id"] for r in rows), AT_CASE_IDS)
        for row in rows:
            self.assertEqual(row["component"], "abnormal_trading")
            self.assertEqual(row["next_slice_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertEqual(row["anchor_tdate"], "PENDING_DENSE_DAY_CITE")
            self.assertNotIn(row["anchor_tdate"], FORBIDDEN_AT_TDATE)
            self.assertIn("exclude_688671", row["exclude_flags"])
            self.assertIn("exclude_301259", row["exclude_flags"])
            self.assertIn(
                "exclude_sparse_day_20260703_sole_found_anchor",
                row["exclude_flags"],
            )
            self.assertIn("exclude_sole_needs_review", row["exclude_flags"])
            self.assertNotIn(row["company_code"], EXCLUDED_CODES)
            self.assertEqual(int(row["shared_probe_prefer"]), 1)
            self.assertEqual(int(row["total_request_cap"]), 5)
            self.assertNotEqual(
                row["expected_behavior"], "captured_normal_or_needs_review"
            )

        self.assertEqual(rows[0]["company_code"], "000895")
        self.assertEqual(rows[3]["company_code"], "000001")
        self.assertEqual(rows[4]["expected_behavior"], "empty_but_valid")

    def test_sd_universe_sketch_five_cases_multi_rdate(self) -> None:
        rows = _load_csv(SD_SKETCH_CSV)
        self.assertEqual(len(rows), 5)
        self.assertEqual(tuple(r["case_id"] for r in rows), SD_CASE_IDS)
        for row in rows:
            self.assertEqual(row["component"], "shareholder_data")
            self.assertEqual(row["next_slice_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertIn("exclude_688671", row["exclude_flags"])
            self.assertIn("exclude_301259", row["exclude_flags"])
            self.assertNotIn(row["company_code"], EXCLUDED_CODES)
            self.assertEqual(int(row["shared_probe_prefer"]), 2)
            self.assertEqual(int(row["total_request_cap"]), 5)

        self.assertEqual(rows[0]["anchor_rdate"], "20260331")
        self.assertEqual(rows[0]["expected_behavior"], "captured_normal")
        self.assertEqual(rows[2]["company_code"], "600519")
        self.assertEqual(rows[3]["anchor_rdate"], "20251231")
        self.assertIn("unproven_rdate_mixed", rows[3]["exclude_flags"])
        self.assertEqual(rows[4]["expected_behavior"], "empty_but_valid")
        self.assertEqual(rows[4]["anchor_rdate"], "20251231")

    def test_candidate_matrix_ranks_at_sd_primary_and_forbids_h3_h4(self) -> None:
        rows = _load_csv(MATRIX_CSV)
        by_id = {r["option_id"]: r for r in rows}
        self.assertEqual(
            by_id["AT_SD_NEXT_SLICE_SCALE_OFFLINE"]["recommendation_rank"], "1"
        )
        self.assertEqual(
            by_id["AT_SD_NEXT_SLICE_SCALE_OFFLINE"]["status"], "primary_executed"
        )
        self.assertEqual(by_id["ESS_H3_H4_BLIND_PROBE"]["status"], "forbidden")
        self.assertEqual(by_id["LEVEL2_IDLE"]["status"], "forbidden")
        self.assertEqual(by_id["DLC006R_REOPEN"]["status"], "forbidden")
        self.assertEqual(by_id["AT_FIRST_SLICE_RELIVE"]["status"], "forbidden")
        self.assertEqual(by_id["SD_FIRST_SLICE_RELIVE"]["status"], "forbidden")
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

        self.assertIn("DAT101", planning)
        self.assertIn("DSD101", planning)
        self.assertIn("PENDING_DENSE_DAY_CITE", planning)
        self.assertIn(
            "d_class_at_sd_next_slice_scale_planning_gate = READY_FOR_APPROVAL",
            planning,
        )
        self.assertIn("cninfo_calls = 0", evidence)
        self.assertIn("blocked_until_dense_day_cite", next_step)
        self.assertIn("paused_pending_devtools", next_step)
        self.assertIn("FAIL_REVIEW_REQUIRED", next_step)

    def test_scale_matrix_matches_sketches(self) -> None:
        at_sketch = {r["case_id"]: r for r in _load_csv(AT_SKETCH_CSV)}
        sd_sketch = {r["case_id"]: r for r in _load_csv(SD_SKETCH_CSV)}
        scale = _load_csv(SCALE_MATRIX_CSV)
        self.assertEqual(len(scale), 10)
        for row in scale:
            self.assertEqual(int(row["cninfo_this_round"]), 0)
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            if row["component"] == "abnormal_trading":
                sk = at_sketch[row["case_id"]]
                self.assertEqual(row["company_code"], sk["company_code"])
                self.assertEqual(row["anchor_value"], sk["anchor_tdate"])
                self.assertEqual(row["expected_behavior"], sk["expected_behavior"])
            else:
                sk = sd_sketch[row["case_id"]]
                self.assertEqual(row["company_code"], sk["company_code"])
                self.assertEqual(row["anchor_value"], sk["anchor_rdate"])
                self.assertEqual(row["expected_behavior"], sk["expected_behavior"])

    def test_caveat_ledger_has_at_and_sd_entries(self) -> None:
        rows = _load_csv(CAVEAT_LEDGER_CSV)
        ids = {r["caveat_id"] for r in rows}
        self.assertIn("CAV-AT-NS-001", ids)
        self.assertIn("CAV-AT-NS-002", ids)
        self.assertIn("CAV-SD-NS-001", ids)
        self.assertIn("CAV-SD-NS-002", ids)
        self.assertIn("CAV-ATSD-NS-001", ids)

    def test_registry_at_sd_still_present(self) -> None:
        self.assertTrue(REGISTRY.is_file())
        text = REGISTRY.read_text(encoding="utf-8")
        self.assertIn("source_id: abnormal_trading", text)
        self.assertIn("getMarketStatisticsData", text)
        self.assertIn("source_id: shareholder_data", text)
        self.assertIn("shareholeder", text)

    def test_no_network_imports_in_this_module(self) -> None:
        """本测试模块自身不得引入 requests（离线保证）。"""
        self.assertNotIn("requests", sys.modules)
        src = Path(__file__).read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"(?m)^\s*import\s+requests\b", src))
        self.assertIsNone(re.search(r"(?m)^\s*from\s+requests\b", src))


if __name__ == "__main__":
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ.pop(key, None)
    unittest.main()
