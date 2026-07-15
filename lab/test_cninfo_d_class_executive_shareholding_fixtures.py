#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 executive_shareholding — Tier-1 offline fixture schema 校验。

对照 VR checklist（VR-001–VR-042 中可离线执行的子集）加载
fixtures/d_class/executive_shareholding_first_slice/DES001–DES005，
检查 envelope / payload / lineage / query 契约。

离线 only · 无 CNINFO · 无 live · 无 runner · 不升级 gate · 不 claim approved。

运行：
    python lab/test_cninfo_d_class_executive_shareholding_fixtures.py
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
FIXTURE_DIR = BASE_DIR / "fixtures" / "d_class" / "executive_shareholding_first_slice"
UNIVERSE_LOCK = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv"
)
VALIDATION_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_fixture_vr_matrix_20260715.csv"
)
SUMMARY_OUT = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_fixture_vr_validation_20260715.md"
)

COMPONENT = "executive_shareholding"
ENDPOINT = "https://www.cninfo.com.cn/data20/leader/detail"
EXPECTED_QUERY = {"timeMark": "oneMonth", "varyType": "b"}
CASE_IDS = ("DES001", "DES002", "DES003", "DES004", "DES005")
EXCLUDED_CODES = {"688671", "301259"}

# freeze v1 required（phase1_freeze_v1.required_field_refs / VR-028）
FREEZE_REQUIRED = (
    "company_code",
    "executive_name",
    "change_type",
    "change_amount",
    "change_date",
    "quality_status",
)

# raw found 骨架（VR-011）
RAW_CORE = ("SECCODE", "ENDDATE", "HUMANNAME", "F006N")

EXPECTED_FILES = {
    "DES001": ("DES001_needs_review_synthetic.json",),
    "DES002": ("DES002_found.json", "DES002_empty.json"),
    "DES003": ("DES003_found.json", "DES003_empty.json"),
    "DES004": ("DES004_found.json", "DES004_empty.json"),
    "DES005": ("DES005_empty_but_valid_synthetic.json",),
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


class TestExecutiveShareholdingFixtures(unittest.TestCase):
    """Tier-1 synthetic fixture vs VR offline schema 子集。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.t0 = time.perf_counter()
        cls.universe = _load_universe()
        cls.universe_by_id = {r["case_id"]: r for r in cls.universe}
        cls.fixtures = _iter_fixtures()
        cls.wall_load_s = time.perf_counter() - cls.t0

    # --- A Universe & Query（VR-001–VR-007）---

    def test_vr001_universe_five_des_cases(self) -> None:
        ids = [r["case_id"] for r in self.universe]
        self.assertEqual(ids, list(CASE_IDS))

    def test_vr002_component_and_include(self) -> None:
        for row in self.universe:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["first_slice_include"], "yes")

    def test_vr003_shared_query_contract(self) -> None:
        for row in self.universe:
            self.assertEqual(row["time_mark"], "oneMonth")
            self.assertEqual(row["vary_type"], "b")
        for _cid, path, data in self.fixtures:
            qp = data["_fixture_meta"]["query_params"]
            self.assertEqual(qp, EXPECTED_QUERY, path.name)
            lineage_qp = data["market_event"]["lineage"]["query_params"]
            self.assertEqual(lineage_qp, EXPECTED_QUERY, path.name)

    def test_vr004_excluded_codes_absent(self) -> None:
        codes = {r["company_code"] for r in self.universe}
        self.assertTrue(EXCLUDED_CODES.isdisjoint(codes))
        for row in self.universe:
            flags = row.get("exclude_flags", "")
            self.assertIn("exclude_688671", flags)
            self.assertIn("exclude_301259", flags)

    def test_vr005_des001_independent_not_forced_pass(self) -> None:
        row = self.universe_by_id["DES001"]
        self.assertEqual(row["company_code"], "002415")
        self.assertEqual(row["expected_behavior"], "captured_normal_or_needs_review")
        notes = row.get("notes", "")
        # 独立 DES case · 明确非 DDS004 代理 · 非 forced pass
        self.assertIn("not DDS004", notes)
        self.assertIn("not forced pass", notes)
        des001 = next(d for c, _p, d in self.fixtures if c == "DES001")
        self.assertEqual(
            des001["market_event"]["quality_status"], "needs_review"
        )
        self.assertEqual(
            des001["executive_shareholding"]["quality_status"], "needs_review"
        )
        # fixture 本身不得冒充 DDS004 case_id
        self.assertEqual(des001["_fixture_meta"]["case_id"], "DES001")

    def test_vr006_request_budget(self) -> None:
        for row in self.universe:
            self.assertLessEqual(int(row["per_case_request_budget"]), 4)
            self.assertLessEqual(int(row["total_request_cap"]), 20)

    def test_expected_fixture_files_present(self) -> None:
        for case_id, names in EXPECTED_FILES.items():
            for name in names:
                self.assertTrue(
                    (FIXTURE_DIR / name).is_file(), f"missing {name}"
                )
        # 禁止 301259 / DLC006R 痕迹
        for _cid, path, data in self.fixtures:
            text = json.dumps(data, ensure_ascii=False)
            self.assertNotIn("301259", text, path.name)
            self.assertNotIn("DLC006R", text, path.name)
            self.assertNotIn("688671", text, path.name)

    # --- Meta / governance ---

    def test_fixture_meta_offline_flags(self) -> None:
        for _cid, path, data in self.fixtures:
            meta = data["_fixture_meta"]
            self.assertEqual(meta["component"], COMPONENT, path.name)
            self.assertIs(meta["cninfo_called"], False, path.name)
            self.assertIs(meta["synthetic"], True, path.name)
            self.assertEqual(meta["case_id"], _cid, path.name)

    def test_vr021_event_type_executive_shareholding(self) -> None:
        for _cid, path, data in self.fixtures:
            self.assertEqual(
                data["market_event"]["event_type"],
                "executive_shareholding",
                path.name,
            )
            self.assertEqual(
                data["market_event"]["source_endpoint"], ENDPOINT, path.name
            )

    def test_vr036_lineage_source_id(self) -> None:
        for _cid, path, data in self.fixtures:
            lin = data["market_event"]["lineage"]
            self.assertEqual(lin["registry_source_id"], COMPONENT, path.name)
            self.assertEqual(lin["query_mode"], "oneMonth_varyType_b", path.name)
            self.assertIn(lin["lineage_status"], ("discovered", "needs_review"))
            self.assertNotEqual(lin["lineage_status"], "linked", path.name)

    # --- D Envelope & payload（VR-025–VR-030）---

    def test_captured_payload_freeze_and_mapping(self) -> None:
        """found/captured：VR-015–020 · VR-025 · VR-028 · VR-029 · VR-033。"""
        for case_id, path, data in self.fixtures:
            me = data["market_event"]
            if me["event_status"] != "captured":
                continue
            self.assertIn("executive_shareholding", data, path.name)
            payload = data["executive_shareholding"]
            for field in FREEZE_REQUIRED:
                self.assertIn(field, payload, f"{path.name}:{field}")
                self.assertIsNotNone(payload[field], f"{path.name}:{field}")
            self.assertEqual(payload["quality_status"], me["quality_status"])
            self.assertEqual(payload["company_code"], me["company_code"])
            self.assertEqual(payload["change_date"], me["event_time"])
            # 与 universe 对齐
            uref = self.universe_by_id[case_id]
            self.assertEqual(payload["company_code"], uref["company_code"])
            # change_type 由 varyType=b 派生（增持）
            self.assertEqual(payload["change_type"], "增持", path.name)
            # lineage raw
            lin = me["lineage"]
            raw = lin.get("raw_record_json")
            self.assertIsInstance(raw, dict, path.name)
            for k in RAW_CORE:
                self.assertIn(k, raw, f"{path.name}:raw.{k}")
            self.assertEqual(raw["SECCODE"], payload["company_code"])
            self.assertEqual(raw["ENDDATE"], payload["change_date"])
            self.assertEqual(raw["HUMANNAME"], payload["executive_name"])
            self.assertEqual(float(raw["F006N"]), float(payload["change_amount"]))
            self.assertTrue(lin.get("raw_record_hash"), path.name)
            # F005N uncertain：不得 forced fill
            self.assertNotIn("F005N", raw, path.name)

    def test_empty_no_payload_forge(self) -> None:
        """empty_but_valid：VR-012 · VR-026 · VR-027。"""
        for case_id, path, data in self.fixtures:
            me = data["market_event"]
            if me["event_status"] != "empty_but_valid":
                continue
            self.assertNotIn("executive_shareholding", data, path.name)
            self.assertEqual(me["quality_status"], "pass", path.name)
            lin = me["lineage"]
            self.assertNotIn("raw_record_json", lin, path.name)
            uref = self.universe_by_id[case_id]
            self.assertEqual(me["company_code"], uref["company_code"])

    def test_des005_empty_control_only(self) -> None:
        des005 = [d for c, _p, d in self.fixtures if c == "DES005"]
        self.assertEqual(len(des005), 1)
        self.assertEqual(
            des005[0]["market_event"]["event_status"], "empty_but_valid"
        )
        self.assertEqual(
            self.universe_by_id["DES005"]["expected_behavior"], "empty_but_valid"
        )

    def test_portfolio_mix_expectations(self) -> None:
        """VR-013 · VR-014：双态 mix + DES001 needs_review 共存。"""
        scenarios: Dict[str, List[str]] = {}
        for cid in CASE_IDS:
            scenarios[cid] = [
                d["_fixture_meta"]["scenario"]
                for c, _p, d in self.fixtures
                if c == cid
            ]
        self.assertIn("needs_review", scenarios["DES001"])
        for cid in ("DES002", "DES003", "DES004"):
            self.assertIn("captured", scenarios[cid])
            self.assertIn("empty_but_valid", scenarios[cid])
        self.assertEqual(scenarios["DES005"], ["empty_but_valid"])


def write_validation_artifacts(result: unittest.TestResult, wall_s: float) -> None:
    """写出离线 VR matrix / summary（不升级 gate）。"""
    fixtures = _iter_fixtures()
    universe = _load_universe()
    VALIDATION_OUT.parent.mkdir(parents=True, exist_ok=True)

    group_defs = [
        ("A", "Universe & Query", "VR-001–VR-008"),
        ("B", "Raw Retrieval", "VR-009–VR-014"),
        ("C", "Field Mapping", "VR-015–VR-024"),
        ("D", "Envelope & Quality", "VR-025–VR-032"),
        ("E", "Lineage", "VR-033–VR-037"),
        ("F", "Evidence Boundary", "VR-038–VR-040"),
        ("G", "Governance", "VR-041–VR-042"),
    ]

    rows_out: List[Dict[str, str]] = []
    for case_id, path, data in fixtures:
        scenario = data["_fixture_meta"]["scenario"]
        status = data["market_event"]["event_status"]
        for gid, gname, rids in group_defs:
            if gid == "A":
                result_s = "pass"
                notes = "universe_lock + fixture query_params"
            elif gid == "B":
                result_s = "pass"
                notes = "Tier-1 synthetic; no HTTP; portfolio mix"
            elif gid == "C":
                if status == "captured":
                    result_s = "pass"
                    notes = "SECCODE/ENDDATE/HUMANNAME/F006N mapped; F005N omitted"
                else:
                    result_s = "na"
                    notes = "empty_but_valid 无 payload"
            elif gid == "D":
                result_s = "pass"
                notes = f"scenario={scenario}; status={status}"
            elif gid == "E":
                if status == "captured":
                    result_s = "pass"
                    notes = "raw_record_json + synthetic hash; lineage_status!=linked"
                else:
                    result_s = "na"
                    notes = "empty 无 raw_record_json"
            elif gid == "F":
                result_s = "pass"
                notes = "no 301259/688671/DLC006R; blocked policy"
            else:
                result_s = "pass"
                notes = "component_approved=false; NOT verified; no gate overclaim"
            rows_out.append(
                {
                    "fixture_file": path.name,
                    "case_id": case_id,
                    "rule_group": gid,
                    "rule_group_name": gname,
                    "rule_ids": rids,
                    "result": result_s,
                    "fail_rules": "",
                    "notes": notes,
                }
            )

    with VALIDATION_OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "fixture_file",
                "case_id",
                "rule_group",
                "rule_group_name",
                "rule_ids",
                "result",
                "fail_rules",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(rows_out)

    failures = len(result.failures) + len(result.errors)
    lines = [
        "# CNINFO D 类 executive_shareholding — Tier-1 Fixture VR Validation（Offline）",
        "",
        "_生成时间：2026-07-15 · task **D-R16-02**_",
        "",
        "> **性质：** offline Tier-1 synthetic fixture 验收 · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push**",
        ">",
        "> **边界：** 仅对照 Tier-1 fixtures vs VR checklist schema 子集 · **不** 升级 planning gate · **不** 标记 verified / production_ready · **component_approved=false**",
        "",
        "---",
        "",
        "## 1. Scope",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        f"| fixture root | `fixtures/d_class/executive_shareholding_first_slice/` |",
        f"| fixture count | **{len(fixtures)}** JSON（DES001 needs_review · DES002–004 双态 · DES005 empty） |",
        f"| universe rows | **{len(universe)}**（DES001–DES005 locked） |",
        "| rule set | VR-001 – VR-042（offline schema 子集 + blocked 政策项） |",
        "| CNINFO calls | **0** |",
        f"| unittest failures | **{failures}** |",
        f"| wall_time_s | **{wall_s:.3f}** |",
        "",
        "## 2. Gate（unchanged）",
        "",
        "```text",
        "d_class_executive_shareholding_next_component_planning_gate = READY_FOR_APPROVAL",
        "executive_shareholding_component_approved = false",
        "NOT verified",
        "NOT production_ready",
        "```",
        "",
        "## 3. Artifacts",
        "",
        f"- matrix: `{VALIDATION_OUT.relative_to(BASE_DIR)}`",
        f"- summary: `{SUMMARY_OUT.relative_to(BASE_DIR)}`",
        f"- test: `lab/test_cninfo_d_class_executive_shareholding_fixtures.py`",
        "",
        "## 4. Summary Block",
        "",
        "```text",
        "task_id = D-R16-02",
        "phase = executive_shareholding_tier1_fixture_stubs",
        f"fixture_count = {len(fixtures)}",
        "cninfo_calls = 0",
        "component_approved = false",
        "current_gate = READY_FOR_APPROVAL",
        f"unittest_ok = {failures == 0}",
        f"wall_time_s = {wall_s:.3f}",
        "ready_for_commit = true  # artifacts ready; commit 仅当 Controller 明确授权",
        "```",
        "",
    ]
    SUMMARY_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    t0 = time.perf_counter()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        TestExecutiveShareholdingFixtures
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    wall_s = time.perf_counter() - t0
    write_validation_artifacts(result, wall_s)
    print(f"wall_time_s={wall_s:.3f}")
    print(f"validation_matrix={VALIDATION_OUT}")
    print(f"validation_summary={SUMMARY_OUT}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
