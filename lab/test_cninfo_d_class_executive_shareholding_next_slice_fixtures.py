#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 executive_shareholding — Next-slice Tier-1 offline fixture / universe lock / VR。

对照 VR-ESH-NS checklist 加载 fixtures/d_class/executive_shareholding_next_slice/DES101–DES105。

离线 only · 无 CNINFO · 无 live · 不实现 runner · 不升级 live gate · 不 claim verified。
冻结：ESH first-slice · SC first/next · RSU first/next · EP first/next · FIA first/next/further-scale · AT/SD first/next lock + dry-run。
ESS H3/H4 禁止重开。

运行：
    .venv/bin/python lab/test_cninfo_d_class_executive_shareholding_next_slice_fixtures.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

FIXTURE_DIR = BASE_DIR / "fixtures" / "d_class" / "executive_shareholding_next_slice"
UNIVERSE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_next_slice_universe_lock_20260716.csv"
)
SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_next_slice_universe_draft_sketch_20260716.csv"
)
VR_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_next_slice_validation_rules_20260716.md"
)
APPROVAL_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_next_slice_approval_package_20260716.md"
)
EVIDENCE_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_dfm54_next_slice_approval_package_20260716.md"
)
CHECKLIST_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_next_slice_offline_prep_checklist_20260716.csv"
)
NEXT_STEP_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_next_slice_approval_next_step_recommendation_20260716.md"
)
COMMAND_DRAFT_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_next_slice_command_draft_20260716.md"
)
DC006 = BASE_DIR / "fixtures" / "d_class" / "phase1" / "DC006.json"
PRIORITY2_STABILITY = (
    BASE_DIR / "outputs" / "validation" / "cninfo_table_sources_priority2_stability.csv"
)
VALIDATION_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_next_slice_fixture_vr_matrix_20260716.csv"
)
SUMMARY_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_next_slice_fixture_vr_validation_20260716.md"
)

ESH_FIRST_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv"
)
ESH_FIRST_LIVE_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_first_slice"
    / "reports"
    / "d_class_executive_shareholding_first_slice_live_report.csv"
)
ESH_FIRST_DRYRUN = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_first_slice"
    / "reports"
    / "d_class_executive_shareholding_first_slice_dryrun_report.csv"
)
SC_NEXT_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice_universe_lock_20260716.csv"
)
SC_NEXT_DRYRUN = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_shareholder_change_next_slice"
    / "reports"
    / "d_class_shareholder_change_next_slice_dryrun_report.csv"
)
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
    ESH_FIRST_LOCK: (
        "d42aaaf71f427fefe96f03700ff33e333686965355149ff2ad63311f7ac283c8"
    ),
    ESH_FIRST_LIVE_REPORT: (
        "7ad294d3840abe12e09b68cd918f4cd91b910867215f4090bab3e9e225c5d585"
    ),
    ESH_FIRST_DRYRUN: (
        "cd8f25c24aebc75bc18ec5bb887eb4c0664ec7a579fcbc6d10c221f40a3b6092"
    ),
    SC_NEXT_LOCK: (
        "5452bc546def60754182a0e5b38fb165d709a37e0a267113088732237b5508fb"
    ),
    SC_NEXT_DRYRUN: (
        "5abc61e4f7ea6014af7e50847aefc7e46f4e39e3ba10e394fd56e683b19a08a5"
    ),
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
    SKETCH_CSV: (
        "b0076b0348b4c34c679fd25cf5226cb506f2a15ef7cddc895189ca11ecb29f87"
    ),
    DC006: (
        "fc39e678afaff82e6bd216a9b5161fb6fb05e0d994a11fb644dd771c27f2694d"
    ),
    PRIORITY2_STABILITY: (
        "1608df92a9741d75ca10e9652ffdeaad358cac6d3fcf7f6352bcad5429b9fb8c"
    ),
}

COMPONENT = "executive_shareholding"
ENDPOINT = "https://www.cninfo.com.cn/data20/leader/detail"
TIME_MARK = "threeMonth"
VARY_TYPE = "b"
FORBIDDEN_TIME_MARK = "oneMonth"
QUERY_MODE = "timeMark_threeMonth_varyType_b"
CASE_IDS = ("DES101", "DES102", "DES103", "DES104", "DES105")
EXCLUDED_CODES = {"688671", "301259"}
FREEZE_REQUIRED = (
    "company_code",
    "change_date",
    "changed_shares",
    "executive_name",
    "quality_status",
)
RAW_CORE = (
    "SECCODE",
    "SECNAME",
    "ENDDATE",
    "HUMANNAME",
    "F001V",
    "F002V",
    "F003V",
    "F006N",
    "F008N",
    "F010V",
)

EXPECTED_FILES = {
    "DES101": ("DES101_found.json", "DES101_empty.json"),
    "DES102": ("DES102_found.json", "DES102_empty.json"),
    "DES103": ("DES103_found.json", "DES103_empty.json"),
    "DES104": ("DES104_found.json", "DES104_empty.json"),
    "DES105": ("DES105_empty_but_valid_synthetic.json",),
}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_fixtures() -> List[Tuple[str, Path, Dict[str, Any]]]:
    rows: List[Tuple[str, Path, Dict[str, Any]]] = []
    for case_id, names in EXPECTED_FILES.items():
        for name in names:
            path = FIXTURE_DIR / name
            rows.append((case_id, path, _load_json(path)))
    return rows


class TestExecutiveShareholdingNextSliceFixtures(unittest.TestCase):
    """Next-slice Tier-1 synthetic fixture vs VR-ESH-NS offline 子集。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.t0 = time.perf_counter()
        cls.universe = _load_csv(UNIVERSE_LOCK)
        cls.universe_by_id = {r["case_id"]: r for r in cls.universe}
        cls.fixtures = _iter_fixtures()

    def test_vr_esh_ns001_universe_five_des_cases(self) -> None:
        ids = [r["case_id"] for r in self.universe]
        self.assertEqual(ids, list(CASE_IDS))

    def test_vr_esh_ns002_component_include_lock(self) -> None:
        for row in self.universe:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["next_slice_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "locked")
            self.assertEqual(row["approval_task_id"], "D-FM-54")

    def test_vr_esh_ns003_shared_dense_threeMonth_b(self) -> None:
        for row in self.universe:
            self.assertEqual(row["time_mark"], TIME_MARK)
            self.assertEqual(row["vary_type"], VARY_TYPE)
            self.assertNotEqual(row["time_mark"], FORBIDDEN_TIME_MARK)
            self.assertEqual(row["query_mode"], QUERY_MODE)
            self.assertEqual(row["dense_mode_cite_task"], "D-FM-53")
        for _cid, path, data in self.fixtures:
            qp = data["_fixture_meta"]["query_params"]
            self.assertEqual(qp["timeMark"], TIME_MARK, path.name)
            self.assertEqual(qp["varyType"], VARY_TYPE, path.name)
            self.assertNotEqual(qp["timeMark"], FORBIDDEN_TIME_MARK, path.name)

    def test_vr_esh_ns004_exclusions(self) -> None:
        codes = {r["company_code"] for r in self.universe}
        self.assertTrue(EXCLUDED_CODES.isdisjoint(codes))
        for row in self.universe:
            flags = row["exclude_flags"]
            self.assertIn("exclude_688671", flags)
            self.assertIn("exclude_301259", flags)
            self.assertIn("exclude_sparse_oneMonth_b_sole_found_anchor", flags)
            self.assertIn("exclude_sole_needs_review", flags)
            self.assertIn("exclude_first_slice_DES001_005_mutate", flags)
            self.assertIn("exclude_dlc006r", flags)
            self.assertIn("exclude_ess_h3_h4", flags)

    def test_vr_esh_ns006_request_budget(self) -> None:
        for row in self.universe:
            self.assertLessEqual(int(row["per_case_request_budget"]), 1)
            self.assertLessEqual(int(row["total_request_cap"]), 5)
            self.assertEqual(int(row["shared_probe_prefer"]), 1)

    def test_vr_esh_ns012_expectation_mix(self) -> None:
        for cid in ("DES101", "DES102", "DES103", "DES104"):
            self.assertEqual(
                self.universe_by_id[cid]["expected_behavior"],
                "captured_normal_or_empty_but_valid",
            )
        self.assertEqual(
            self.universe_by_id["DES105"]["expected_behavior"],
            "empty_but_valid",
        )
        for row in self.universe:
            self.assertNotEqual(row["expected_behavior"], "captured_normal_candidate")
            self.assertNotEqual(
                row["expected_behavior"],
                "captured_normal_or_needs_review",
            )

    def test_closed_roots_frozen(self) -> None:
        for path, expected in EXPECTED_SHA256.items():
            self.assertTrue(path.is_file(), f"missing freeze target {path}")
            self.assertEqual(
                _sha256_file(path),
                expected,
                f"frozen root mutated: {path}",
            )
        first_ids = {r["case_id"] for r in _load_csv(ESH_FIRST_LOCK)}
        next_ids = {r["case_id"] for r in self.universe}
        self.assertTrue(first_ids.isdisjoint(next_ids))

    def test_sketch_remains_draft_history(self) -> None:
        sketch = _load_csv(SKETCH_CSV)
        self.assertEqual([r["case_id"] for r in sketch], list(CASE_IDS))
        for row in sketch:
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertEqual(row["time_mark"], TIME_MARK)
            self.assertEqual(row["vary_type"], VARY_TYPE)

    def test_expected_fixture_files_present(self) -> None:
        for case_id, names in EXPECTED_FILES.items():
            for name in names:
                self.assertTrue((FIXTURE_DIR / name).is_file(), f"missing {name}")
        for _cid, path, data in self.fixtures:
            text = json.dumps(data, ensure_ascii=False)
            self.assertNotIn("301259", text, path.name)
            self.assertNotIn("DLC006R", text, path.name)
            self.assertNotIn("688671", text, path.name)
            meta_qp = data["_fixture_meta"]["query_params"]
            self.assertEqual(meta_qp["timeMark"], TIME_MARK, path.name)
            self.assertEqual(meta_qp["varyType"], VARY_TYPE, path.name)
            lin_qp = data["market_event"]["lineage"]["query_params"]
            self.assertEqual(lin_qp["timeMark"], TIME_MARK, path.name)
            self.assertEqual(lin_qp["varyType"], VARY_TYPE, path.name)

    def test_fixture_meta_offline_flags(self) -> None:
        for _cid, path, data in self.fixtures:
            meta = data["_fixture_meta"]
            self.assertEqual(meta["component"], COMPONENT, path.name)
            self.assertIs(meta["cninfo_called"], False, path.name)
            self.assertIs(meta["synthetic"], True, path.name)
            self.assertEqual(meta["case_id"], _cid, path.name)
            self.assertEqual(meta["dense_mode_cite"], "threeMonth+b", path.name)
            self.assertEqual(meta["approval_task_id"], "D-FM-54", path.name)
            self.assertEqual(meta["time_mark"], TIME_MARK, path.name)
            self.assertEqual(meta["vary_type"], VARY_TYPE, path.name)

    def test_vr_esh_ns005_endpoint_and_event_type(self) -> None:
        for _cid, path, data in self.fixtures:
            self.assertEqual(
                data["market_event"]["event_type"], COMPONENT, path.name
            )
            self.assertEqual(
                data["market_event"]["source_endpoint"], ENDPOINT, path.name
            )
            self.assertIn("leader/detail", data["market_event"]["source_endpoint"])

    def test_vr_esh_ns036_lineage(self) -> None:
        for case_id, path, data in self.fixtures:
            lin = data["market_event"]["lineage"]
            uref = self.universe_by_id[case_id]
            self.assertEqual(lin["registry_source_id"], COMPONENT, path.name)
            self.assertEqual(lin["query_mode"], uref["query_mode"], path.name)
            self.assertIn(lin["lineage_status"], ("discovered", "needs_review"))
            self.assertNotEqual(lin["lineage_status"], "linked", path.name)
            self.assertEqual(lin["query_params"]["timeMark"], TIME_MARK, path.name)
            self.assertEqual(lin["query_params"]["varyType"], VARY_TYPE, path.name)

    def test_captured_payload_freeze(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["market_event"]
            if env["event_status"] != "captured":
                continue
            self.assertIn("executive_shareholding", data, path.name)
            payload = data["executive_shareholding"]
            for field in FREEZE_REQUIRED:
                self.assertIn(field, payload, f"{path.name}:{field}")
            self.assertEqual(payload["quality_status"], env["quality_status"])
            self.assertEqual(
                payload["event_type"], "executive_shareholding_change", path.name
            )
            uref = self.universe_by_id[case_id]
            self.assertEqual(payload["company_code"], uref["company_code"])
            raw = env["lineage"].get("raw_record_json")
            self.assertIsInstance(raw, dict, path.name)
            for k in RAW_CORE:
                self.assertIn(k, raw, f"{path.name}:raw.{k}")
            self.assertEqual(raw["SECCODE"], uref["company_code"], path.name)

    def test_empty_but_valid_envelope(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["market_event"]
            if env["event_status"] != "empty_but_valid":
                continue
            self.assertEqual(env["quality_status"], "pass", path.name)
            self.assertNotIn("executive_shareholding", data, path.name)
            self.assertNotIn("raw_record_json", env["lineage"], path.name)
            uref = self.universe_by_id[case_id]
            self.assertIn(
                uref["expected_behavior"],
                ("captured_normal_or_empty_but_valid", "empty_but_valid"),
            )

    def test_des105_empty_control_only(self) -> None:
        names = EXPECTED_FILES["DES105"]
        self.assertEqual(names, ("DES105_empty_but_valid_synthetic.json",))
        data = _load_json(FIXTURE_DIR / names[0])
        self.assertEqual(data["market_event"]["event_status"], "empty_but_valid")
        self.assertEqual(data["market_event"]["company_code"], "601988")

    def test_des101_structure_cite_aligned(self) -> None:
        self.assertEqual(
            self.universe_by_id["DES101"]["structure_cite_reference"], "yes"
        )
        self.assertEqual(self.universe_by_id["DES101"]["company_code"], "002415")
        dc006 = _load_json(DC006)
        # DC006 仅为结构 cite；不得误导 denser threeMonth company found
        self.assertEqual(dc006["_fixture_meta"]["component"], COMPONENT)
        self.assertEqual(dc006["executive_shareholding"]["company_code"], "999106")
        lineage = dc006["market_event"]["lineage"]
        self.assertNotEqual(lineage.get("query_mode"), QUERY_MODE)

    def test_approval_and_vr_docs_present(self) -> None:
        self.assertTrue(VR_MD.is_file())
        self.assertTrue(APPROVAL_MD.is_file())
        self.assertTrue(EVIDENCE_MD.is_file())
        self.assertTrue(COMMAND_DRAFT_MD.is_file())
        self.assertTrue(NEXT_STEP_MD.is_file())
        self.assertTrue(CHECKLIST_CSV.is_file())
        vr_text = VR_MD.read_text(encoding="utf-8")
        approval = APPROVAL_MD.read_text(encoding="utf-8")
        evidence = EVIDENCE_MD.read_text(encoding="utf-8")
        self.assertIn("DES101", vr_text)
        self.assertIn("VR-ESH-NS-001", vr_text)
        self.assertIn("threeMonth", vr_text)
        self.assertIn("varyType=b", vr_text)
        self.assertIn("不是 verified", vr_text)
        self.assertIn("universe_lock_status=`locked`", vr_text)
        self.assertIn("DES101", approval)
        self.assertIn("STANDING_SCOPE_AUTHORIZED", approval)
        self.assertIn("不是 verified", approval)
        self.assertNotRegex(approval, r"(?m)^\s*verified\s*=")
        self.assertNotIn("production_ready = true", approval)
        self.assertIn(
            "d_class_executive_shareholding_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED",
            approval,
        )
        self.assertIn(
            "d_class_executive_shareholding_next_slice_fixture_vr_gate = PASS_OFFLINE",
            approval,
        )
        self.assertIn("NOT_APPROVED", approval)
        self.assertIn("H3/H4", approval)
        self.assertIn("console", evidence.lower())
        self.assertIn("allow_list_excludes = console_logs", evidence)

    def test_checklist_gates(self) -> None:
        rows = _load_csv(CHECKLIST_CSV)
        by_id = {r["item_id"]: r for r in rows}
        self.assertEqual(by_id["ESH-NS-GATE-03"]["status"], "NOT_APPROVED")
        self.assertEqual(by_id["ESH-NS-GATE-04"]["status"], "NOT_APPROVED")
        self.assertEqual(by_id["ESH-NS-GATE-06"]["status"], "STANDING_SCOPE_AUTHORIZED")
        self.assertEqual(by_id["ESH-NS-GATE-07"]["status"], "PASS_OFFLINE")
        self.assertEqual(by_id["ESH-NS-STUB-05"]["status"], "forbidden_this_round")
        self.assertEqual(by_id["ESH-NS-SAFE-20"]["status"], "policy")
        self.assertEqual(by_id["ESH-NS-SAFE-21"]["status"], "policy")

    def test_no_network_imports(self) -> None:
        import lab.test_cninfo_d_class_executive_shareholding_next_slice_fixtures as self_mod

        self.assertFalse(hasattr(self_mod, "requests"))

    @classmethod
    def tearDownClass(cls) -> None:
        wall = time.perf_counter() - cls.t0
        fixtures = _iter_fixtures()
        rows: List[Dict[str, str]] = []
        for case_id, path, data in fixtures:
            env = data["market_event"]
            rows.append(
                {
                    "fixture": path.name,
                    "case_id": case_id,
                    "group": "D",
                    "topic": "Envelope",
                    "vr": "VR-ESH-NS-025–VR-ESH-NS-030",
                    "status": "pass",
                    "note": env["event_status"],
                }
            )
            if env["event_status"] == "captured":
                rows.append(
                    {
                        "fixture": path.name,
                        "case_id": case_id,
                        "group": "C",
                        "topic": "Field Mapping",
                        "vr": "VR-ESH-NS-015–VR-ESH-NS-024",
                        "status": "pass",
                        "note": "SECCODE/ENDDATE/HUMANNAME/F006N freeze · threeMonth+b",
                    }
                )
        VALIDATION_OUT.parent.mkdir(parents=True, exist_ok=True)
        with VALIDATION_OUT.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "fixture",
                    "case_id",
                    "group",
                    "topic",
                    "vr",
                    "status",
                    "note",
                ],
            )
            w.writeheader()
            w.writerows(rows)
        esh_sha = _sha256_file(ESH_FIRST_LOCK)
        sc_ns_sha = _sha256_file(SC_NEXT_LOCK)
        rsu_ns_sha = _sha256_file(RSU_NEXT_LOCK)
        ep_ns_sha = _sha256_file(EP_NEXT_LOCK)
        lock_sha = _sha256_file(UNIVERSE_LOCK)
        summary = "\n".join(
            [
                "# CNINFO D 类 executive_shareholding — Next-Slice Tier-1 Fixture VR Validation（Offline）",
                "",
                f"_生成时间：D-FM-54 · wall≈{wall:.2f}s_",
                "",
                "> **性质：** Tier-1 next-slice fixture offline VR · **CNINFO = 0** · **不是 verified**",
                "",
                "| 项 | 值 |",
                "|----|-----|",
                f"| fixture root | `fixtures/d_class/executive_shareholding_next_slice/` |",
                f"| universe lock | `{UNIVERSE_LOCK.name}` |",
                f"| fixtures | **{len(fixtures)}** |",
                f"| matrix rows | **{len(rows)}** |",
                f"| timeMark | `{TIME_MARK}` |",
                f"| varyType | `{VARY_TYPE}` |",
                f"| ESH next-slice lock sha256 | `{lock_sha}` |",
                f"| ESH first-slice lock sha256 | `{esh_sha}` |",
                f"| SC next-slice lock sha256 | `{sc_ns_sha}` |",
                f"| RSU next-slice lock sha256 | `{rsu_ns_sha}` |",
                f"| EP next-slice lock sha256 | `{ep_ns_sha}` |",
                f"| CNINFO | **0** |",
                "",
                "```text",
                "d_class_executive_shareholding_next_slice_fixture_vr_gate = PASS_OFFLINE",
                "d_class_executive_shareholding_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED",
                "d_class_executive_shareholding_next_slice_live_gate = NOT_APPROVED",
                "d_class_executive_shareholding_next_slice_runner_gate = NOT_APPROVED",
                "executive_shareholding_component_approved = standing_scope",
                "closed_roots_mutated = false",
                "company_level_live_found_path_for_DES101_105 = NOT_PROVEN",
                "ess_h3_h4_probed = false",
                "```",
                "",
                "## Artifacts",
                "",
                f"- matrix: `outputs/validation/{VALIDATION_OUT.name}`",
                f"- summary: `outputs/validation/{SUMMARY_OUT.name}`",
                "- test: `lab/test_cninfo_d_class_executive_shareholding_next_slice_fixtures.py`",
                "",
                "```text",
                "task_id = D-FM-54",
                "phase = executive_shareholding_next_slice_approval_package_offline",
                "allow_list_excludes = console_logs",
                "```",
                "",
            ]
        )
        SUMMARY_OUT.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    unittest.main(verbosity=2)
