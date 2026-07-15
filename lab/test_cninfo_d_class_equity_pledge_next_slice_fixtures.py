#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 equity_pledge — Next-slice Tier-1 offline fixture / universe lock / VR。

对照 VR-EP-NS checklist 加载 fixtures/d_class/equity_pledge_next_slice/DEP101–DEP105。

离线 only · 无 CNINFO · 无 live · 不实现 runner · 不升级 live gate · 不 claim verified。
冻结：EP first-slice · FIA first/next/further-scale · AT/SD first/next lock + dry-run。

运行：
    .venv/bin/python lab/test_cninfo_d_class_equity_pledge_next_slice_fixtures.py
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

FIXTURE_DIR = BASE_DIR / "fixtures" / "d_class" / "equity_pledge_next_slice"
UNIVERSE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv"
)
SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_universe_draft_sketch_20260715.csv"
)
VR_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_validation_rules_20260715.md"
)
APPROVAL_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_approval_package_20260715.md"
)
EVIDENCE_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_dfm42_next_slice_approval_package_20260715.md"
)
CHECKLIST_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_offline_prep_checklist_20260715.csv"
)
NEXT_STEP_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_approval_next_step_recommendation_20260715.md"
)
COMMAND_DRAFT_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_command_draft_20260715.md"
)
SAMPLE_RAW = BASE_DIR / "fixtures" / "d_class" / "equity_pledge" / "sample_raw.json"
VALIDATION_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_fixture_vr_matrix_20260715.csv"
)
SUMMARY_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_next_slice_fixture_vr_validation_20260715.md"
)

EP_FIRST_UNIVERSE = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_first_slice_universe_draft.csv"
)
EP_FIRST_LIVE_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_first_slice"
    / "reports"
    / "d_class_equity_pledge_first_slice_live_report.csv"
)
EP_FIRST_DRYRUN_REPORT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_equity_pledge_first_slice"
    / "reports"
    / "d_class_equity_pledge_first_slice_dryrun_report.csv"
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
FIA_FURTHER_DRYRUN = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_fund_industry_allocation_further_scale"
    / "reports"
    / "d_class_fund_industry_allocation_further_scale_dryrun_report.csv"
)

EXPECTED_SHA256 = {
    EP_FIRST_UNIVERSE: (
        "5fb4fa005236a162ef3bcc5322fe3b7134b36cbe7727fb0273724d0638dc8e10"
    ),
    EP_FIRST_LIVE_REPORT: (
        "435b53bc9cc5360a0dc8843b81431bbc108b37a71fc80527d501bf420fc12387"
    ),
    EP_FIRST_DRYRUN_REPORT: (
        "a035f8ef6102946bb2b4406f59f17cff20aff810de9c1fb59cab82c7d43084bc"
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
    FIA_FURTHER_DRYRUN: (
        "fc7cfc51493c426d0db1608aad09b0dc4a7755c0019f8d822a46e40fa85fefd4"
    ),
    SAMPLE_RAW: (
        "3b989118da44ee9d357a3da134df918b5ec44c3d410d28658cce4bdac51ca2c5"
    ),
}

COMPONENT = "equity_pledge"
ENDPOINT = "https://www.cninfo.com.cn/data20/equityPledge/list"
ANCHOR = "2026-07-02"
FORBIDDEN_ANCHOR = "2026-07-03"
CASE_IDS = ("DEP101", "DEP102", "DEP103", "DEP104", "DEP105")
EXCLUDED_CODES = {"688671", "301259"}
FREEZE_REQUIRED = (
    "company_code",
    "announcement_date",
    "pledgor",
    "pledged_shares",
    "quality_status",
)
RAW_CORE = (
    "SECCODE",
    "SECNAME",
    "DECLAREDATE",
    "F001V",
    "F003V",
    "F006N",
    "F007N",
    "F018N",
)

EXPECTED_FILES = {
    "DEP101": ("DEP101_found.json", "DEP101_empty.json"),
    "DEP102": ("DEP102_found.json", "DEP102_empty.json"),
    "DEP103": ("DEP103_found.json", "DEP103_empty.json"),
    "DEP104": ("DEP104_found.json", "DEP104_empty.json"),
    "DEP105": ("DEP105_empty_but_valid_synthetic.json",),
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


class TestEquityPledgeNextSliceFixtures(unittest.TestCase):
    """Next-slice Tier-1 synthetic fixture vs VR-EP-NS offline 子集。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.t0 = time.perf_counter()
        cls.universe = _load_csv(UNIVERSE_LOCK)
        cls.universe_by_id = {r["case_id"]: r for r in cls.universe}
        cls.fixtures = _iter_fixtures()

    def test_vr_ep_ns001_universe_five_dep_cases(self) -> None:
        ids = [r["case_id"] for r in self.universe]
        self.assertEqual(ids, list(CASE_IDS))

    def test_vr_ep_ns002_component_include_lock(self) -> None:
        for row in self.universe:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["next_slice_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "locked")
            self.assertEqual(row["approval_task_id"], "D-FM-42")

    def test_vr_ep_ns003_shared_dense_anchor(self) -> None:
        for row in self.universe:
            self.assertEqual(row["anchor_tdate"], ANCHOR)
            self.assertNotEqual(row["anchor_tdate"], FORBIDDEN_ANCHOR)
            self.assertEqual(row["query_mode"], "tdate_daily")
            self.assertEqual(row["dense_day_cite_task"], "D-FM-41")
        for _cid, path, data in self.fixtures:
            qp = data["_fixture_meta"]["query_params"]
            self.assertEqual(qp["tdate"], ANCHOR, path.name)
            self.assertNotEqual(qp["tdate"], FORBIDDEN_ANCHOR, path.name)

    def test_vr_ep_ns004_exclusions(self) -> None:
        codes = {r["company_code"] for r in self.universe}
        self.assertTrue(EXCLUDED_CODES.isdisjoint(codes))
        for row in self.universe:
            flags = row["exclude_flags"]
            self.assertIn("exclude_688671", flags)
            self.assertIn("exclude_301259", flags)
            self.assertIn("exclude_sparse_day_20260703_sole_found_anchor", flags)
            self.assertIn("exclude_sole_needs_review", flags)
            self.assertIn("exclude_first_slice_DEP001_005_mutate", flags)

    def test_vr_ep_ns006_request_budget(self) -> None:
        for row in self.universe:
            self.assertLessEqual(int(row["per_case_request_budget"]), 1)
            self.assertLessEqual(int(row["total_request_cap"]), 5)
            self.assertEqual(int(row["shared_probe_prefer"]), 1)

    def test_vr_ep_ns012_expectation_mix(self) -> None:
        for cid in ("DEP101", "DEP102", "DEP103", "DEP104"):
            self.assertEqual(
                self.universe_by_id[cid]["expected_behavior"],
                "captured_normal_or_empty_but_valid",
            )
        self.assertEqual(
            self.universe_by_id["DEP105"]["expected_behavior"],
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
        first_ids = {r["case_id"] for r in _load_csv(EP_FIRST_UNIVERSE)}
        next_ids = {r["case_id"] for r in self.universe}
        self.assertTrue(first_ids.isdisjoint(next_ids))

    def test_sketch_remains_draft_history(self) -> None:
        sketch = _load_csv(SKETCH_CSV)
        self.assertEqual([r["case_id"] for r in sketch], list(CASE_IDS))
        for row in sketch:
            self.assertEqual(row["universe_lock_status"], "draft_not_locked")
            self.assertEqual(row["anchor_tdate"], ANCHOR)

    def test_expected_fixture_files_present(self) -> None:
        for case_id, names in EXPECTED_FILES.items():
            for name in names:
                self.assertTrue((FIXTURE_DIR / name).is_file(), f"missing {name}")
        for _cid, path, data in self.fixtures:
            text = json.dumps(data, ensure_ascii=False)
            self.assertNotIn("301259", text, path.name)
            self.assertNotIn("DLC006R", text, path.name)
            self.assertNotIn("688671", text, path.name)
            self.assertNotIn(FORBIDDEN_ANCHOR, text, path.name)

    def test_fixture_meta_offline_flags(self) -> None:
        for _cid, path, data in self.fixtures:
            meta = data["_fixture_meta"]
            self.assertEqual(meta["component"], COMPONENT, path.name)
            self.assertIs(meta["cninfo_called"], False, path.name)
            self.assertIs(meta["synthetic"], True, path.name)
            self.assertEqual(meta["case_id"], _cid, path.name)
            self.assertEqual(meta["dense_day_cite"], ANCHOR, path.name)
            self.assertEqual(meta["approval_task_id"], "D-FM-42", path.name)

    def test_vr_ep_ns005_endpoint_and_event_type(self) -> None:
        for _cid, path, data in self.fixtures:
            self.assertEqual(
                data["market_event"]["event_type"], "equity_pledge", path.name
            )
            self.assertEqual(
                data["market_event"]["source_endpoint"], ENDPOINT, path.name
            )

    def test_vr_ep_ns036_lineage(self) -> None:
        for case_id, path, data in self.fixtures:
            lin = data["market_event"]["lineage"]
            uref = self.universe_by_id[case_id]
            self.assertEqual(lin["registry_source_id"], COMPONENT, path.name)
            self.assertEqual(lin["query_mode"], uref["query_mode"], path.name)
            self.assertIn(lin["lineage_status"], ("discovered", "needs_review"))
            self.assertNotEqual(lin["lineage_status"], "linked", path.name)
            self.assertEqual(lin["query_params"]["tdate"], ANCHOR, path.name)

    def test_captured_payload_freeze(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["market_event"]
            if env["event_status"] != "captured":
                continue
            self.assertIn("equity_pledge", data, path.name)
            payload = data["equity_pledge"]
            for field in FREEZE_REQUIRED:
                self.assertIn(field, payload, f"{path.name}:{field}")
            self.assertEqual(payload["quality_status"], env["quality_status"])
            self.assertEqual(payload["announcement_date"], ANCHOR, path.name)
            uref = self.universe_by_id[case_id]
            self.assertEqual(payload["company_code"], uref["company_code"])
            raw = env["lineage"].get("raw_record_json")
            self.assertIsInstance(raw, dict, path.name)
            for k in RAW_CORE:
                self.assertIn(k, raw, f"{path.name}:raw.{k}")
            self.assertEqual(raw["DECLAREDATE"], ANCHOR, path.name)
            self.assertEqual(raw["SECCODE"], uref["company_code"], path.name)
            # F008V 仅 raw_only · 禁止升为标准必填列
            self.assertNotIn("pledge_description_text", payload, path.name)
            self.assertNotIn("F008V", payload, path.name)

    def test_empty_but_valid_envelope(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["market_event"]
            if env["event_status"] != "empty_but_valid":
                continue
            self.assertEqual(env["quality_status"], "pass", path.name)
            self.assertNotIn("equity_pledge", data, path.name)
            self.assertNotIn("raw_record_json", env["lineage"], path.name)
            uref = self.universe_by_id[case_id]
            self.assertIn(
                uref["expected_behavior"],
                ("captured_normal_or_empty_but_valid", "empty_but_valid"),
            )

    def test_dep105_empty_control_only(self) -> None:
        names = EXPECTED_FILES["DEP105"]
        self.assertEqual(names, ("DEP105_empty_but_valid_synthetic.json",))
        data = _load_json(FIXTURE_DIR / names[0])
        self.assertEqual(data["market_event"]["event_status"], "empty_but_valid")
        self.assertEqual(data["market_event"]["company_code"], "601988")

    def test_dep101_sample_raw_aligned(self) -> None:
        self.assertEqual(self.universe_by_id["DEP101"]["sample_raw_reference"], "yes")
        self.assertEqual(self.universe_by_id["DEP101"]["company_code"], "000001")
        sample = _load_json(SAMPLE_RAW)
        self.assertEqual(sample["query_params"]["tdate"], ANCHOR)
        self.assertEqual(sample["raw_record"]["SECCODE"], "000001")

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
        self.assertIn("DEP101", vr_text)
        self.assertIn("VR-EP-NS-001", vr_text)
        self.assertIn("2026-07-02", vr_text)
        self.assertIn("不是 verified", vr_text)
        self.assertIn("universe_lock_status=`locked`", vr_text)
        self.assertIn("DEP101", approval)
        self.assertIn("STANDING_SCOPE_AUTHORIZED", approval)
        self.assertIn("不是 verified", approval)
        self.assertNotRegex(approval, r"(?m)^\s*verified\s*=")
        self.assertNotIn("production_ready = true", approval)
        self.assertIn(
            "d_class_equity_pledge_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED",
            approval,
        )
        self.assertIn(
            "d_class_equity_pledge_next_slice_fixture_vr_gate = PASS_OFFLINE",
            approval,
        )
        self.assertIn("NOT_APPROVED", approval)
        self.assertIn("H3/H4", approval)
        self.assertIn("console", evidence.lower())
        self.assertIn("allow_list_excludes = console_logs", evidence)

    def test_checklist_gates(self) -> None:
        rows = _load_csv(CHECKLIST_CSV)
        by_id = {r["item_id"]: r for r in rows}
        self.assertEqual(by_id["EP-NS-GATE-02"]["status"], "NOT_APPROVED")
        self.assertEqual(by_id["EP-NS-GATE-03"]["status"], "NOT_APPROVED")
        self.assertEqual(by_id["EP-NS-GATE-04"]["status"], "STANDING_SCOPE_AUTHORIZED")
        self.assertEqual(by_id["EP-NS-GATE-05"]["status"], "PASS_OFFLINE")
        self.assertEqual(by_id["EP-NS-STUB-03"]["status"], "forbidden_this_round")
        self.assertEqual(by_id["EP-NS-SAFE-14"]["status"], "policy")
        self.assertEqual(by_id["EP-NS-SAFE-16"]["status"], "policy")

    def test_no_network_imports(self) -> None:
        import lab.test_cninfo_d_class_equity_pledge_next_slice_fixtures as self_mod

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
                    "vr": "VR-EP-NS-025–VR-EP-NS-030",
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
                        "vr": "VR-EP-NS-015–VR-EP-NS-024",
                        "status": "pass",
                        "note": "SECCODE/DECLAREDATE/F001V/F006N freeze; F008V raw_only",
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
        ep_sha = _sha256_file(EP_FIRST_UNIVERSE)
        fia_fs_sha = _sha256_file(FIA_FIRST_LOCK)
        fia_ns_sha = _sha256_file(FIA_NEXT_LOCK)
        lock_sha = _sha256_file(UNIVERSE_LOCK)
        summary = "\n".join(
            [
                "# CNINFO D 类 equity_pledge — Next-Slice Tier-1 Fixture VR Validation（Offline）",
                "",
                f"_生成时间：D-FM-42 · wall≈{wall:.2f}s_",
                "",
                "> **性质：** Tier-1 next-slice fixture offline VR · **CNINFO = 0** · **不是 verified**",
                "",
                "| 项 | 值 |",
                "|----|-----|",
                f"| fixture root | `fixtures/d_class/equity_pledge_next_slice/` |",
                f"| universe lock | `{UNIVERSE_LOCK.name}` |",
                f"| fixtures | **{len(fixtures)}** |",
                f"| matrix rows | **{len(rows)}** |",
                f"| anchor_tdate | `{ANCHOR}` |",
                f"| EP next-slice lock sha256 | `{lock_sha}` |",
                f"| EP first-slice universe sha256 | `{ep_sha}` |",
                f"| FIA first-slice lock sha256 | `{fia_fs_sha}` |",
                f"| FIA next-slice lock sha256 | `{fia_ns_sha}` |",
                f"| CNINFO | **0** |",
                "",
                "```text",
                "d_class_equity_pledge_next_slice_fixture_vr_gate = PASS_OFFLINE",
                "d_class_equity_pledge_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED",
                "d_class_equity_pledge_next_slice_live_gate = NOT_APPROVED",
                "d_class_equity_pledge_next_slice_runner_gate = NOT_APPROVED",
                "equity_pledge_component_approved = standing_scope",
                "closed_roots_mutated = false",
                "company_level_live_found_path_for_DEP101_105 = NOT_PROVEN",
                "```",
                "",
                "## Artifacts",
                "",
                f"- matrix: `outputs/validation/{VALIDATION_OUT.name}`",
                f"- summary: `outputs/validation/{SUMMARY_OUT.name}`",
                "- test: `lab/test_cninfo_d_class_equity_pledge_next_slice_fixtures.py`",
                "",
                "```text",
                "task_id = D-FM-42",
                "phase = equity_pledge_next_slice_approval_package_offline",
                "allow_list_excludes = console_logs",
                "```",
                "",
            ]
        )
        SUMMARY_OUT.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    unittest.main(verbosity=2)
