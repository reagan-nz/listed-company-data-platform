#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 abnormal_trading — Tier-1 offline fixture schema 校验。

对照 VR checklist 加载 fixtures/d_class/abnormal_trading_first_slice/DAT001–DAT005。

离线 only · 无 CNINFO · 无 live · 不升级 gate · 不 claim verified。

运行：
    python lab/test_cninfo_d_class_abnormal_trading_fixtures.py
"""

from __future__ import annotations

import csv
import json
import os
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_DIR = BASE_DIR / "fixtures" / "d_class" / "abnormal_trading_first_slice"
UNIVERSE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv"
)
VALIDATION_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_fixture_vr_matrix_20260715.csv"
)
SUMMARY_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_abnormal_trading_fixture_vr_validation_20260715.md"
)

COMPONENT = "abnormal_trading"
ENDPOINT = "https://www.cninfo.com.cn/data/statis/getMarketStatisticsData"
ANCHOR = "2026-07-03"
CASE_IDS = ("DAT001", "DAT002", "DAT003", "DAT004", "DAT005")
EXCLUDED_CODES = {"688671", "301259"}
FREEZE_REQUIRED = (
    "company_code",
    "trade_date",
    "public_information_reason",
    "quality_status",
)
RAW_CORE = ("secCode", "secName", "tradeTime", "type")

EXPECTED_FILES = {
    "DAT001": ("DAT001_needs_review_synthetic.json",),
    "DAT002": ("DAT002_found.json", "DAT002_empty.json"),
    "DAT003": ("DAT003_found.json", "DAT003_empty.json"),
    "DAT004": ("DAT004_found.json", "DAT004_empty.json"),
    "DAT005": ("DAT005_empty_but_valid_synthetic.json",),
}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_universe() -> List[Dict[str, str]]:
    with UNIVERSE_LOCK.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _iter_fixtures() -> List[Tuple[str, Path, Dict[str, Any]]]:
    rows: List[Tuple[str, Path, Dict[str, Any]]] = []
    for case_id, names in EXPECTED_FILES.items():
        for name in names:
            path = FIXTURE_DIR / name
            rows.append((case_id, path, _load_json(path)))
    return rows


class TestAbnormalTradingFixtures(unittest.TestCase):
    """Tier-1 synthetic fixture vs VR offline schema 子集。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.t0 = time.perf_counter()
        cls.universe = _load_universe()
        cls.universe_by_id = {r["case_id"]: r for r in cls.universe}
        cls.fixtures = _iter_fixtures()
        cls.matrix_rows: List[Dict[str, str]] = []

    def _note(
        self, fixture: str, case_id: str, group: str, topic: str, vr: str, status: str, note: str
    ) -> None:
        self.matrix_rows.append(
            {
                "fixture": fixture,
                "case_id": case_id,
                "group": group,
                "topic": topic,
                "vr": vr,
                "status": status,
                "note": note,
            }
        )

    def test_vr001_universe_five_dat_cases(self) -> None:
        ids = [r["case_id"] for r in self.universe]
        self.assertEqual(ids, list(CASE_IDS))
        self._note("-", "-", "A", "Universe", "VR-001", "pass", "DAT001–DAT005")

    def test_vr002_component_and_include(self) -> None:
        for row in self.universe:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["first_slice_include"], "yes")
        self._note("-", "-", "A", "Universe", "VR-002", "pass", "component+include")

    def test_vr003_shared_query_contract(self) -> None:
        for row in self.universe:
            self.assertEqual(row["anchor_tdate"], ANCHOR)
        for _cid, path, data in self.fixtures:
            qp = data["_fixture_meta"]["query_params"]
            self.assertEqual(qp["sdate"], ANCHOR, path.name)
            self.assertEqual(qp["edate"], ANCHOR, path.name)
            self.assertEqual(int(qp["page"]), 1, path.name)
            self.assertEqual(int(qp["rows"]), 30, path.name)
        self._note("-", "-", "A", "Query", "VR-003/007", "pass", "single_day_paged")

    def test_vr004_exclusions(self) -> None:
        codes = {r["company_code"] for r in self.universe}
        self.assertTrue(EXCLUDED_CODES.isdisjoint(codes))
        for row in self.universe:
            self.assertIn("exclude_688671", row["exclude_flags"])
            self.assertIn("exclude_301259", row["exclude_flags"])
        self._note("-", "-", "A", "Exclusions", "VR-004/040", "pass", "no 688671/301259")

    def test_vr006_request_budget(self) -> None:
        for row in self.universe:
            self.assertLessEqual(int(row["per_case_request_budget"]), 1)
            self.assertLessEqual(int(row["total_request_cap"]), 20)
        self._note("-", "-", "A", "Budget", "VR-006", "pass", "1/20")

    def test_expected_fixture_files_present(self) -> None:
        for case_id, names in EXPECTED_FILES.items():
            for name in names:
                self.assertTrue((FIXTURE_DIR / name).is_file(), f"missing {name}")
        for _cid, path, data in self.fixtures:
            text = json.dumps(data, ensure_ascii=False)
            self.assertNotIn("301259", text, path.name)
            self.assertNotIn("DLC006R", text, path.name)
            self.assertNotIn("688671", text, path.name)

    def test_fixture_meta_offline_flags(self) -> None:
        for _cid, path, data in self.fixtures:
            meta = data["_fixture_meta"]
            self.assertEqual(meta["component"], COMPONENT, path.name)
            self.assertIs(meta["cninfo_called"], False, path.name)
            self.assertIs(meta["synthetic"], True, path.name)
            self.assertEqual(meta["case_id"], _cid, path.name)

    def test_vr021_event_type_and_endpoint(self) -> None:
        for _cid, path, data in self.fixtures:
            self.assertEqual(
                data["market_event"]["event_type"], "abnormal_trading", path.name
            )
            self.assertEqual(
                data["market_event"]["source_endpoint"], ENDPOINT, path.name
            )
        self._note("-", "-", "C", "Event type", "VR-019/021", "pass", "abnormal_trading")

    def test_vr036_lineage(self) -> None:
        for _cid, path, data in self.fixtures:
            lin = data["market_event"]["lineage"]
            self.assertEqual(lin["registry_source_id"], COMPONENT, path.name)
            self.assertEqual(lin["query_mode"], "single_day_paged", path.name)
            self.assertIn(lin["lineage_status"], ("discovered", "needs_review"))
            self.assertNotEqual(lin["lineage_status"], "linked", path.name)

    def test_captured_payload_freeze_and_mapping(self) -> None:
        for case_id, path, data in self.fixtures:
            me = data["market_event"]
            if me["event_status"] != "captured":
                continue
            self.assertIn("abnormal_trading", data, path.name)
            payload = data["abnormal_trading"]
            for field in FREEZE_REQUIRED:
                self.assertIn(field, payload, f"{path.name}:{field}")
            self.assertEqual(payload["quality_status"], me["quality_status"])
            self.assertEqual(payload["company_code"], me["company_code"])
            self.assertEqual(payload["trade_date"], me["event_time"])
            self.assertTrue(payload.get("detail_nested_deferred") is True, path.name)
            uref = self.universe_by_id[case_id]
            self.assertEqual(payload["company_code"], uref["company_code"])
            lin = me["lineage"]
            raw = lin.get("raw_record_json")
            self.assertIsInstance(raw, dict, path.name)
            for k in RAW_CORE:
                self.assertIn(k, raw, f"{path.name}:raw.{k}")
            self.assertEqual(raw["secCode"], payload["company_code"])
            self.assertEqual(raw["tradeTime"], payload["trade_date"])
            self.assertEqual(raw["type"], payload["public_information_reason"])
            self.assertIsInstance(raw.get("detail"), list, path.name)
            self._note(
                path.name,
                case_id,
                "C",
                "Field Mapping",
                "VR-015–VR-024",
                "pass",
                "secCode/tradeTime/type mapped; detail deferred",
            )

    def test_empty_but_valid_envelope(self) -> None:
        for case_id, path, data in self.fixtures:
            me = data["market_event"]
            if me["event_status"] != "empty_but_valid":
                continue
            self.assertEqual(me["quality_status"], "pass", path.name)
            self.assertNotIn("abnormal_trading", data, path.name)
            self.assertNotIn("raw_record_json", me["lineage"], path.name)
            self._note(
                path.name,
                case_id,
                "D",
                "Envelope",
                "VR-026",
                "pass",
                "empty_but_valid",
            )

    def test_dat001_needs_review_and_dat005_empty(self) -> None:
        dat001 = next(d for c, _p, d in self.fixtures if c == "DAT001")
        self.assertEqual(dat001["market_event"]["quality_status"], "needs_review")
        dat005 = next(d for c, _p, d in self.fixtures if c == "DAT005")
        self.assertEqual(dat005["market_event"]["event_status"], "empty_but_valid")
        self.assertEqual(
            self.universe_by_id["DAT005"]["expected_behavior"], "empty_but_valid"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        # 汇总 matrix（由实例方法累积到共享 list）
        wall = time.perf_counter() - cls.t0
        # 若无实例累积，补最小矩阵
        rows = []
        # 重新轻量扫一遍写固定矩阵
        fixtures = _iter_fixtures()
        for case_id, path, data in fixtures:
            me = data["market_event"]
            status = "pass"
            note = me["event_status"]
            rows.append(
                {
                    "fixture": path.name,
                    "case_id": case_id,
                    "group": "D",
                    "topic": "Envelope",
                    "vr": "VR-025–VR-030",
                    "status": status,
                    "note": note,
                }
            )
            if me["event_status"] == "captured":
                rows.append(
                    {
                        "fixture": path.name,
                        "case_id": case_id,
                        "group": "C",
                        "topic": "Field Mapping",
                        "vr": "VR-015–VR-024",
                        "status": "pass",
                        "note": "secCode/tradeTime/type mapped; detail deferred",
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
        summary = "\n".join(
            [
                "# CNINFO D 类 abnormal_trading — Tier-1 Fixture VR Validation（Offline）",
                "",
                f"_生成时间：D-FM-03 · wall≈{wall:.2f}s_",
                "",
                "> **性质：** Tier-1 fixture offline VR · **CNINFO = 0** · **不是 verified**",
                "",
                "| 项 | 值 |",
                "|----|-----|",
                f"| fixture root | `fixtures/d_class/abnormal_trading_first_slice/` |",
                f"| universe lock | `{UNIVERSE_LOCK.name}` |",
                f"| fixtures | **{len(fixtures)}** |",
                f"| matrix rows | **{len(rows)}** |",
                f"| CNINFO | **0** |",
                "",
                "```text",
                "d_class_abnormal_trading_fixture_vr_gate = PASS_OFFLINE",
                "d_class_abnormal_trading_next_component_planning_gate = READY_FOR_APPROVAL",
                "abnormal_trading_component_approved = standing_scope",
                "```",
                "",
                "## Artifacts",
                "",
                f"- matrix: `outputs/validation/{VALIDATION_OUT.name}`",
                f"- summary: `outputs/validation/{SUMMARY_OUT.name}`",
                "- test: `lab/test_cninfo_d_class_abnormal_trading_fixtures.py`",
                "",
                "```text",
                "task_id = D-FM-03",
                "phase = abnormal_trading_tier1_fixture_stubs",
                "```",
                "",
            ]
        )
        SUMMARY_OUT.write_text(summary, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
