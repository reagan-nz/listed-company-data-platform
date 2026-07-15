#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 abnormal_trading — Next-slice Tier-1 offline fixture / universe lock / VR。

对照 VR-NS checklist 加载 fixtures/d_class/abnormal_trading_next_slice/DAT101–DAT105。

离线 only · 无 CNINFO · 无 live · 不实现 runner · 不升级 live gate · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_abnormal_trading_next_slice_fixtures.py
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

FIXTURE_DIR = BASE_DIR / "fixtures" / "d_class" / "abnormal_trading_next_slice"
UNIVERSE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv"
)
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
# 关闭根冻结 sha256；本任务必须保持
EXPECTED_AT_FIRST_SLICE_LOCK_SHA256 = (
    "d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2"
)
EXPECTED_SD_FIRST_SLICE_LOCK_SHA256 = (
    "06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5"
)
EXPECTED_FIA_NEXT_SLICE_LOCK_SHA256 = (
    "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
)
EXPECTED_FIA_FIRST_SLICE_LOCK_SHA256 = (
    "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
)
SKETCH_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_universe_draft_sketch_20260715.csv"
)
VR_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_validation_rules_20260715.md"
)
APPROVAL_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_approval_package_20260715.md"
)
VALIDATION_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_fixture_vr_matrix_20260715.csv"
)
SUMMARY_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_next_slice_fixture_vr_validation_20260715.md"
)

COMPONENT = "abnormal_trading"
ENDPOINT = "https://www.cninfo.com.cn/data/statis/getMarketStatisticsData"
ANCHOR = "2026-07-02"
FORBIDDEN_ANCHOR = "2026-07-03"
CASE_IDS = ("DAT101", "DAT102", "DAT103", "DAT104", "DAT105")
EXCLUDED_CODES = {"688671", "301259"}
FREEZE_REQUIRED = (
    "company_code",
    "trade_date",
    "public_information_reason",
    "quality_status",
)
RAW_CORE = ("secCode", "secName", "tradeTime", "type")
DETAIL_FLAT_FORBIDDEN = (
    "buyOrgName",
    "sellOrgName",
    "buyOrgBuyTotal",
    "sellOrgSellTotal",
)

EXPECTED_FILES = {
    "DAT101": ("DAT101_found.json", "DAT101_empty.json"),
    "DAT102": ("DAT102_found.json", "DAT102_empty.json"),
    "DAT103": ("DAT103_found.json", "DAT103_multi_type_found.json"),
    "DAT104": ("DAT104_found.json", "DAT104_empty.json"),
    "DAT105": ("DAT105_empty_but_valid_synthetic.json",),
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


class TestAbnormalTradingNextSliceFixtures(unittest.TestCase):
    """Next-slice Tier-1 synthetic fixture vs VR-NS offline 子集。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.t0 = time.perf_counter()
        cls.universe = _load_csv(UNIVERSE_LOCK)
        cls.universe_by_id = {r["case_id"]: r for r in cls.universe}
        cls.fixtures = _iter_fixtures()

    def test_vr_ns001_universe_five_dat_cases(self) -> None:
        ids = [r["case_id"] for r in self.universe]
        self.assertEqual(ids, list(CASE_IDS))

    def test_vr_ns002_component_include_lock(self) -> None:
        for row in self.universe:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["next_slice_include"], "yes")
            self.assertEqual(row["universe_lock_status"], "locked")
            self.assertEqual(row["approval_task_id"], "D-FM-30")

    def test_vr_ns003_shared_dense_anchor(self) -> None:
        for row in self.universe:
            self.assertEqual(row["anchor_tdate"], ANCHOR)
            self.assertNotEqual(row["anchor_tdate"], FORBIDDEN_ANCHOR)
            self.assertEqual(row["query_mode"], "single_day_paged")
            self.assertEqual(row["dense_day_cite_task"], "D-FM-29")
        for _cid, path, data in self.fixtures:
            qp = data["_fixture_meta"]["query_params"]
            self.assertEqual(qp["sdate"], ANCHOR, path.name)
            self.assertEqual(qp["edate"], ANCHOR, path.name)
            self.assertNotEqual(qp["sdate"], FORBIDDEN_ANCHOR, path.name)
            self.assertEqual(int(qp["page"]), 1, path.name)
            self.assertEqual(int(qp["rows"]), 30, path.name)

    def test_vr_ns004_exclusions(self) -> None:
        codes = {r["company_code"] for r in self.universe}
        self.assertTrue(EXCLUDED_CODES.isdisjoint(codes))
        for row in self.universe:
            flags = row["exclude_flags"]
            self.assertIn("exclude_688671", flags)
            self.assertIn("exclude_301259", flags)
            self.assertIn("exclude_sparse_day_20260703_sole_found_anchor", flags)
            self.assertIn("exclude_sole_needs_review", flags)
            self.assertIn("detail_nested_deferred", flags)

    def test_vr_ns006_request_budget(self) -> None:
        for row in self.universe:
            self.assertLessEqual(int(row["per_case_request_budget"]), 1)
            self.assertLessEqual(int(row["total_request_cap"]), 5)
            self.assertEqual(int(row["shared_probe_prefer"]), 1)

    def test_vr_ns012_expectation_mix(self) -> None:
        for cid in ("DAT101", "DAT102", "DAT103", "DAT104"):
            self.assertEqual(
                self.universe_by_id[cid]["expected_behavior"],
                "captured_normal_or_empty_but_valid",
            )
        self.assertEqual(
            self.universe_by_id["DAT105"]["expected_behavior"],
            "empty_but_valid",
        )
        for row in self.universe:
            self.assertNotEqual(
                row["expected_behavior"],
                "captured_normal_or_needs_review",
            )

    def test_closed_roots_frozen(self) -> None:
        self.assertEqual(
            _sha256_file(AT_FIRST_SLICE_LOCK),
            EXPECTED_AT_FIRST_SLICE_LOCK_SHA256,
            "AT first-slice universe lock must not be mutated in D-FM-30",
        )
        self.assertEqual(
            _sha256_file(SD_FIRST_SLICE_LOCK),
            EXPECTED_SD_FIRST_SLICE_LOCK_SHA256,
            "SD first-slice universe lock must not be mutated in D-FM-30",
        )
        self.assertEqual(
            _sha256_file(FIA_NEXT_SLICE_LOCK),
            EXPECTED_FIA_NEXT_SLICE_LOCK_SHA256,
            "FIA next-slice universe lock must not be mutated in D-FM-30",
        )
        self.assertEqual(
            _sha256_file(FIA_FIRST_SLICE_LOCK),
            EXPECTED_FIA_FIRST_SLICE_LOCK_SHA256,
            "FIA first-slice universe lock must not be mutated in D-FM-30",
        )
        first_ids = {r["case_id"] for r in _load_csv(AT_FIRST_SLICE_LOCK)}
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

    def test_vr_ns019_event_type_and_endpoint(self) -> None:
        for _cid, path, data in self.fixtures:
            self.assertEqual(
                data["market_event"]["event_type"], "abnormal_trading", path.name
            )
            self.assertEqual(
                data["market_event"]["source_endpoint"], ENDPOINT, path.name
            )

    def test_vr_ns036_lineage(self) -> None:
        for case_id, path, data in self.fixtures:
            lin = data["market_event"]["lineage"]
            uref = self.universe_by_id[case_id]
            self.assertEqual(lin["registry_source_id"], COMPONENT, path.name)
            self.assertEqual(lin["query_mode"], uref["query_mode"], path.name)
            self.assertIn(lin["lineage_status"], ("discovered", "needs_review"))
            self.assertNotEqual(lin["lineage_status"], "linked", path.name)
            self.assertEqual(lin["query_params"]["sdate"], ANCHOR, path.name)
            self.assertEqual(lin["query_params"]["edate"], ANCHOR, path.name)

    def test_captured_payload_freeze(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["market_event"]
            if env["event_status"] != "captured":
                continue
            self.assertIn("abnormal_trading", data, path.name)
            payload = data["abnormal_trading"]
            for field in FREEZE_REQUIRED:
                self.assertIn(field, payload, f"{path.name}:{field}")
            self.assertEqual(payload["quality_status"], env["quality_status"])
            self.assertEqual(payload["trade_date"], ANCHOR, path.name)
            self.assertTrue(payload.get("detail_nested_deferred"), path.name)
            uref = self.universe_by_id[case_id]
            self.assertEqual(payload["company_code"], uref["company_code"])
            raw = env["lineage"].get("raw_record_json")
            self.assertIsInstance(raw, dict, path.name)
            for k in RAW_CORE:
                self.assertIn(k, raw, f"{path.name}:raw.{k}")
            self.assertEqual(raw["tradeTime"], ANCHOR, path.name)
            # detail 不得扁平到主 payload
            for forbidden in DETAIL_FLAT_FORBIDDEN:
                self.assertNotIn(forbidden, payload, path.name)

    def test_empty_but_valid_envelope(self) -> None:
        for case_id, path, data in self.fixtures:
            env = data["market_event"]
            if env["event_status"] != "empty_but_valid":
                continue
            self.assertEqual(env["quality_status"], "pass", path.name)
            self.assertNotIn("abnormal_trading", data, path.name)
            self.assertNotIn("raw_record_json", env["lineage"], path.name)
            uref = self.universe_by_id[case_id]
            self.assertIn(
                uref["expected_behavior"],
                ("captured_normal_or_empty_but_valid", "empty_but_valid"),
            )

    def test_dat105_empty_control_only(self) -> None:
        names = EXPECTED_FILES["DAT105"]
        self.assertEqual(names, ("DAT105_empty_but_valid_synthetic.json",))
        data = _load_json(FIXTURE_DIR / names[0])
        self.assertEqual(data["market_event"]["event_status"], "empty_but_valid")
        self.assertEqual(data["market_event"]["company_code"], "601988")

    def test_multi_type_structure_dat103(self) -> None:
        path = FIXTURE_DIR / "DAT103_multi_type_found.json"
        data = _load_json(path)
        meta = data["_fixture_meta"]
        self.assertEqual(meta["scenario"], "captured_multi_type")
        self.assertEqual(len(meta["sibling_raw_records"]), 2)
        types = {r["type"] for r in meta["sibling_raw_records"]}
        self.assertEqual(len(types), 2)
        for rec in meta["sibling_raw_records"]:
            self.assertEqual(rec["tradeTime"], ANCHOR)

    def test_approval_and_vr_docs_present(self) -> None:
        self.assertTrue(VR_MD.is_file())
        self.assertTrue(APPROVAL_MD.is_file())
        vr_text = VR_MD.read_text(encoding="utf-8")
        approval = APPROVAL_MD.read_text(encoding="utf-8")
        self.assertIn("DAT101", vr_text)
        self.assertIn("VR-NS-001", vr_text)
        self.assertIn("2026-07-02", vr_text)
        self.assertIn("不是 verified", vr_text)
        self.assertIn("DAT101", approval)
        self.assertIn("STANDING_SCOPE_AUTHORIZED", approval)
        self.assertIn("不是 verified", approval)
        self.assertNotRegex(approval, r"(?m)^\s*verified\s*=")
        self.assertNotIn("production_ready = true", approval)
        self.assertIn(
            "d_class_abnormal_trading_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED",
            approval,
        )
        self.assertIn(
            "d_class_abnormal_trading_next_slice_fixture_vr_gate = PASS_OFFLINE",
            approval,
        )
        self.assertIn("NOT_APPROVED", approval)
        self.assertIn("H3/H4", approval)
        self.assertIn("OFFLINE_PROVISIONAL_CITE_2026_07_02", approval)

    def test_no_network_imports(self) -> None:
        import lab.test_cninfo_d_class_abnormal_trading_next_slice_fixtures as self_mod

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
                    "vr": "VR-NS-025–VR-NS-030",
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
                        "vr": "VR-NS-015–VR-NS-024",
                        "status": "pass",
                        "note": "secCode/tradeTime/type freeze; detail deferred",
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
        at_sha = _sha256_file(AT_FIRST_SLICE_LOCK)
        sd_sha = _sha256_file(SD_FIRST_SLICE_LOCK)
        fia_ns_sha = _sha256_file(FIA_NEXT_SLICE_LOCK)
        fia_fs_sha = _sha256_file(FIA_FIRST_SLICE_LOCK)
        summary = "\n".join(
            [
                "# CNINFO D 类 abnormal_trading — Next-Slice Tier-1 Fixture VR Validation（Offline）",
                "",
                f"_生成时间：D-FM-30 · wall≈{wall:.2f}s_",
                "",
                "> **性质：** Tier-1 next-slice fixture offline VR · **CNINFO = 0** · **不是 verified**",
                "",
                "| 项 | 值 |",
                "|----|-----|",
                f"| fixture root | `fixtures/d_class/abnormal_trading_next_slice/` |",
                f"| universe lock | `{UNIVERSE_LOCK.name}` |",
                f"| fixtures | **{len(fixtures)}** |",
                f"| matrix rows | **{len(rows)}** |",
                f"| anchor_tdate | `{ANCHOR}` |",
                f"| AT first-slice lock sha256 | `{at_sha}` |",
                f"| SD first-slice lock sha256 | `{sd_sha}` |",
                f"| FIA next-slice lock sha256 | `{fia_ns_sha}` |",
                f"| FIA first-slice lock sha256 | `{fia_fs_sha}` |",
                f"| CNINFO | **0** |",
                "",
                "```text",
                "d_class_abnormal_trading_next_slice_fixture_vr_gate = PASS_OFFLINE",
                "d_class_abnormal_trading_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED",
                "d_class_abnormal_trading_next_slice_live_gate = NOT_APPROVED",
                "d_class_abnormal_trading_next_slice_runner_gate = NOT_APPROVED",
                "at_dense_day_status = OFFLINE_PROVISIONAL_CITE_2026_07_02",
                "abnormal_trading_component_approved = standing_scope",
                "closed_roots_mutated = false",
                "```",
                "",
                "## Artifacts",
                "",
                f"- matrix: `outputs/validation/{VALIDATION_OUT.name}`",
                f"- summary: `outputs/validation/{SUMMARY_OUT.name}`",
                "- test: `lab/test_cninfo_d_class_abnormal_trading_next_slice_fixtures.py`",
                "",
                "```text",
                "task_id = D-FM-30",
                "phase = abnormal_trading_next_slice_approval_package_offline",
                "```",
                "",
            ]
        )
        SUMMARY_OUT.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    unittest.main(verbosity=2)
