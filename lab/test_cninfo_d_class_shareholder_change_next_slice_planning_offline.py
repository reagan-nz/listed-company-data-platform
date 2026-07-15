#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 shareholder_change — D-FM-49 next-slice offline planning smoke。

离线 only · 无 CNINFO · 无 live · 无 runner · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_shareholder_change_next_slice_planning_offline.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import unittest
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SC_CASE_IDS = ("DSC101", "DSC102", "DSC103", "DSC104", "DSC105")
EXCLUDED_CODES = {"688671", "301259"}
FORBIDDEN_SC_MODE = {"inc"}
EXPECTED_ANCHOR = "2026-07-03"
EXPECTED_QUERY_TYPE = "desc"

PLANNING_MD = (
    BASE_DIR
    / "plans"
    / "cninfo_d_class_shareholder_change_next_slice_planning_20260716.md"
)
MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice_candidate_matrix_20260716.csv"
)
SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice_universe_draft_sketch_20260716.csv"
)
VR_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice_validation_rules_20260716.md"
)
CHECKLIST_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice_offline_prep_checklist_20260716.csv"
)
RECOMMENDATION_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice_recommendation_20260716.md"
)
SUMMARY_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice_planning_summary_20260716.md"
)
NEXT_STEP_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice_next_step_recommendation_20260716.md"
)
CAVEAT_LEDGER_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice_final_caveat_ledger.csv"
)
EVIDENCE_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_dfm49_next_slice_planning_20260716.md"
)
DC005 = BASE_DIR / "fixtures" / "d_class" / "phase1" / "DC005.json"
PRIORITY2_STABILITY = (
    BASE_DIR / "outputs" / "validation" / "cninfo_table_sources_priority2_stability.csv"
)
REGISTRY = BASE_DIR / "config" / "cninfo_d_class_source_registry_draft.yaml"

SC_FIRST_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv"
)
SC_FIRST_LIVE_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_first_slice"
    / "reports"
    / "d_class_shareholder_change_first_slice_live_report.csv"
)
SC_FIRST_DRYRUN = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_first_slice"
    / "reports"
    / "d_class_shareholder_change_first_slice_dryrun_report.csv"
)
RSU_FIRST_UNIVERSE = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv"
)
RSU_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv"
)
RSU_NEXT_DRYRUN = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_restricted_shares_unlock_next_slice"
    / "reports"
    / "d_class_restricted_shares_unlock_next_slice_dryrun_report.csv"
)
EP_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv"
)
EP_NEXT_DRYRUN = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice"
    / "reports"
    / "d_class_equity_pledge_next_slice_dryrun_report.csv"
)
EP_FIRST_UNIVERSE = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_first_slice_universe_draft.csv"
)
FIA_FURTHER_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale_universe_lock_20260715.csv"
)
FIA_FIRST_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv"
)
FIA_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv"
)
AT_FIRST_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv"
)
AT_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv"
)
SD_FIRST_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv"
)
SD_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv"
)
AT_NEXT_DRYRUN = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice"
    / "reports"
    / "d_class_abnormal_trading_next_slice_dryrun_report.csv"
)
SD_NEXT_DRYRUN = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_data_next_slice"
    / "reports"
    / "d_class_shareholder_data_next_slice_dryrun_report.csv"
)

EXPECTED_SHA256 = {
    SC_FIRST_LOCK: (
        "49e6ece0c0a5c5ecce32328e4e1fe990b48d7d46d3cc1f32da1c8d2245a3c402"
    ),
    SC_FIRST_LIVE_REPORT: (
        "5d73c24e40d028976da4054983649ee2a3e2a9ad2b3edf12babe893cfc779e1f"
    ),
    SC_FIRST_DRYRUN: (
        "e37e9fbe485bf63b9c4d41cf1170aec558100f51c9ac69654bf09f7eb1213e44"
    ),
    RSU_FIRST_UNIVERSE: (
        "81a792f43962849778d53af97b4d67c64d53b1cd15d8428ff6d0a74931c84ec9"
    ),
    RSU_NEXT_LOCK: (
        "13254f44f344c0f2976dfbde6fe75e363f91283a6eec1a5ae02d29f3831f193f"
    ),
    RSU_NEXT_DRYRUN: (
        "87f296cf51fd69873f8fd6fd05a541ebbfa35dab53b92063bdf841736b52b18c"
    ),
    EP_NEXT_LOCK: (
        "1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384"
    ),
    EP_NEXT_DRYRUN: (
        "054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e"
    ),
    EP_FIRST_UNIVERSE: (
        "5fb4fa005236a162ef3bcc5322fe3b7134b36cbe7727fb0273724d0638dc8e10"
    ),
    FIA_FURTHER_LOCK: (
        "398494f1cf6a6cf00637b82d6e3f5c38ae21671a4b47324fd1ee2262df92e9f1"
    ),
    FIA_FIRST_LOCK: (
        "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
    ),
    FIA_NEXT_LOCK: (
        "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
    ),
    AT_FIRST_LOCK: (
        "d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2"
    ),
    AT_NEXT_LOCK: (
        "4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6"
    ),
    SD_FIRST_LOCK: (
        "06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5"
    ),
    SD_NEXT_LOCK: (
        "c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f"
    ),
    AT_NEXT_DRYRUN: (
        "51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497"
    ),
    SD_NEXT_DRYRUN: (
        "2b74aac55299bc844e7df49725ad9ccf1f9c4dfbfc7db403f026412faf177362"
    ),
    PRIORITY2_STABILITY: (
        "1608df92a9741d75ca10e9652ffdeaad358cac6d3fcf7f6352bcad5429b9fb8c"
    ),
    DC005: (
        "99bcb6199d2b177faa3650c775ac42e0655c7f588e640139798e73aadfed012c"
    ),
}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _load_csv(path: Path) -> List[Dict[str, str]]:
    # utf-8-sig：兼容 priority2 等带 BOM 的离线 cite CSV
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


class ShareholderChangeNextSlicePlanningOfflineTests(unittest.TestCase):
    """D-FM-49：SC next-slice sketch + frozen-root sha256。"""

    def test_artifacts_exist(self) -> None:
        for path in (
            PLANNING_MD,
            MATRIX_CSV,
            SKETCH_CSV,
            VR_MD,
            CHECKLIST_CSV,
            RECOMMENDATION_MD,
            SUMMARY_MD,
            NEXT_STEP_MD,
            CAVEAT_LEDGER_CSV,
            EVIDENCE_MD,
            DC005,
            PRIORITY2_STABILITY,
        ):
            self.assertTrue(path.is_file(), f"missing {path}")

    def test_frozen_roots_sha256_unchanged(self) -> None:
        for path, expected in EXPECTED_SHA256.items():
            self.assertTrue(path.is_file(), f"missing freeze target {path}")
            digest = _sha256_file(path)
            self.assertEqual(
                digest,
                expected,
                f"frozen root mutated: {path}",
            )

    def test_universe_sketch_five_cases_dense_mode(self) -> None:
        rows = _load_csv(SKETCH_CSV)
        self.assertEqual(len(rows), 5)
        self.assertEqual(tuple(r["case_id"] for r in rows), SC_CASE_IDS)
        for row in rows:
            self.assertEqual(row["component"], "shareholder_change")
            self.assertEqual(row["next_slice_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertEqual(row["anchor_tdate"], EXPECTED_ANCHOR)
            self.assertEqual(row["query_type"], EXPECTED_QUERY_TYPE)
            self.assertNotIn(row["query_type"], FORBIDDEN_SC_MODE)
            self.assertEqual(row["query_mode"], "type_desc_tdate_daily")
            self.assertIn("exclude_688671", row["exclude_flags"])
            self.assertIn("exclude_301259", row["exclude_flags"])
            self.assertIn(
                "exclude_sparse_inc_20260703_sole_found_anchor",
                row["exclude_flags"],
            )
            self.assertIn("exclude_sole_needs_review", row["exclude_flags"])
            self.assertIn("exclude_dlc006r", row["exclude_flags"])
            self.assertNotIn(row["company_code"], EXCLUDED_CODES)
            self.assertEqual(int(row["shared_probe_prefer"]), 1)
            self.assertEqual(int(row["total_request_cap"]), 5)
            self.assertNotEqual(
                row["expected_behavior"], "captured_normal_or_needs_review"
            )

        self.assertEqual(rows[0]["company_code"], "000550")
        self.assertEqual(rows[0]["structure_cite_reference"], "yes")
        self.assertEqual(rows[3]["company_code"], "002415")
        self.assertEqual(rows[4]["expected_behavior"], "empty_but_valid")

    def test_dc005_is_structure_cite_not_dense_desc(self) -> None:
        """DC005 为 envelope 结构 cite；change_type=inc 不得误导 denser desc。"""
        payload = json.loads(DC005.read_text(encoding="utf-8"))
        self.assertEqual(payload["_fixture_meta"]["component"], "shareholder_change")
        self.assertEqual(payload["shareholder_change"]["change_type"], "inc")
        self.assertNotEqual(
            payload["shareholder_change"]["change_type"], EXPECTED_QUERY_TYPE
        )

    def test_priority2_desc_dense_cite_present(self) -> None:
        rows = _load_csv(PRIORITY2_STABILITY)
        by_id = {r["test_case_id"]: r for r in rows}
        desc = by_id["sc_desc_tdate_2026_07_03"]
        inc = by_id["sc_inc_tdate_2026_07_03"]
        self.assertEqual(desc["source_id"], "shareholder_change")
        self.assertEqual(int(desc["observed_total_rows"]), 16)
        self.assertEqual(int(inc["observed_total_rows"]), 3)
        self.assertGreater(
            int(desc["observed_total_rows"]), int(inc["observed_total_rows"])
        )

    def test_candidate_matrix_ranks_sc_primary_and_forbids_live(self) -> None:
        rows = _load_csv(MATRIX_CSV)
        by_id = {r["option_id"]: r for r in rows}
        self.assertEqual(
            by_id["SHAREHOLDER_CHANGE_NEXT_SLICE_OFFLINE"]["recommendation_rank"], "1"
        )
        self.assertEqual(
            by_id["SHAREHOLDER_CHANGE_NEXT_SLICE_OFFLINE"]["status"], "primary_executed"
        )
        self.assertEqual(
            by_id["EXECUTIVE_SHAREHOLDING_NEXT_SLICE_OFFLINE"]["status"], "deferred"
        )
        self.assertEqual(by_id["ESS_H3_H4_BLIND_PROBE"]["status"], "forbidden")
        self.assertEqual(by_id["LEVEL2_IDLE"]["status"], "forbidden")
        self.assertEqual(by_id["DLC006R_REOPEN"]["status"], "forbidden")
        self.assertEqual(
            by_id["SHAREHOLDER_CHANGE_FIRST_SLICE_RELIVE"]["status"], "forbidden"
        )
        self.assertEqual(
            by_id["RSU_FIRST_OR_NEXT_MUTATE"]["status"], "forbidden"
        )
        self.assertEqual(
            by_id["EP_FIA_AT_SD_FROZEN_ROOT_MUTATE"]["status"], "forbidden"
        )
        self.assertEqual(
            by_id["RSU_NEXT_SLICE_BOUNDED_LIVE"]["status"], "forbidden_this_round"
        )

    def test_planning_and_gates_text(self) -> None:
        planning = PLANNING_MD.read_text(encoding="utf-8")
        evidence = EVIDENCE_MD.read_text(encoding="utf-8")
        next_step = NEXT_STEP_MD.read_text(encoding="utf-8")
        recommendation = RECOMMENDATION_MD.read_text(encoding="utf-8")
        for text in (planning, evidence, next_step, recommendation):
            self.assertIn("READY_FOR_APPROVAL", text)
            self.assertIn("CNINFO", text)
            self.assertTrue(
                ("H3/H4" in text) or ("H3 / H4" in text) or ("h3_h4" in text.lower())
            )
            self.assertNotIn("verified_claim = true", text)
            self.assertNotIn("production_ready = true", text)

        self.assertIn("DSC101", planning)
        self.assertIn("2026-07-03", planning)
        self.assertIn("type=desc", planning)
        self.assertIn(
            "d_class_shareholder_change_next_slice_planning_gate = READY_FOR_APPROVAL",
            planning,
        )
        self.assertIn("cninfo_calls = 0", evidence)
        self.assertIn("NOT_APPROVED", next_step)
        self.assertIn("paused_pending_devtools", next_step)
        self.assertIn("primary_component = shareholder_change", recommendation)

    def test_validation_rules_cover_core_ids(self) -> None:
        text = VR_MD.read_text(encoding="utf-8")
        for rule_id in (
            "VR-SC-NS-001",
            "VR-SC-NS-003",
            "VR-SC-NS-013",
            "VR-SC-NS-039",
            "VR-SC-NS-042",
        ):
            self.assertIn(rule_id, text)
        self.assertIn("2026-07-03", text)
        self.assertIn("type=desc", text)
        self.assertIn("shareholeder/detail", text)

    def test_caveat_ledger_has_sc_ns_entries(self) -> None:
        rows = _load_csv(CAVEAT_LEDGER_CSV)
        ids = {r["caveat_id"] for r in rows}
        self.assertIn("CAV-SC-NS-001", ids)
        self.assertIn("CAV-SC-NS-002", ids)
        self.assertIn("CAV-SC-NS-003", ids)
        self.assertIn("CAV-SC-NS-007", ids)
        self.assertIn("CAV-SC-NS-009", ids)

    def test_checklist_blocks_live_and_runner(self) -> None:
        rows = _load_csv(CHECKLIST_CSV)
        by_id = {r["item_id"]: r for r in rows}
        self.assertEqual(by_id["SC-NS-STUB-05"]["status"], "forbidden_this_round")
        self.assertEqual(by_id["SC-NS-GATE-03"]["status"], "NOT_APPROVED")
        self.assertEqual(by_id["SC-NS-GATE-01"]["status"], "READY_FOR_APPROVAL")
        self.assertEqual(by_id["SC-NS-SAFE-18"]["status"], "policy")
        self.assertEqual(by_id["SC-NS-SAFE-19"]["status"], "policy")

    def test_registry_shareholder_change_still_present(self) -> None:
        self.assertTrue(REGISTRY.is_file())
        text = REGISTRY.read_text(encoding="utf-8")
        self.assertIn("source_id: shareholder_change", text)
        self.assertIn("shareholeder/detail", text)

    def test_sc_first_slice_live_report_still_present(self) -> None:
        rows = _load_csv(SC_FIRST_LIVE_REPORT)
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["case_id"], "DSC001")

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
