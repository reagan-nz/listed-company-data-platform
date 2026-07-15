#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 executive_shareholding_summary — D-FM-21 offline discovery smoke。

离线 only · 无 CNINFO · 无 live · 无 runner · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_executive_shareholding_summary_offline_discovery.py
"""

from __future__ import annotations

import csv
import os
import sys
import unittest
from pathlib import Path
from typing import Dict, List

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

COMPONENT = "executive_shareholding_summary"
CASE_IDS = ("DESS001", "DESS002", "DESS003", "DESS004", "DESS005")
EXCLUDED_CODES = {"688671", "301259"}
SIBLING_DETAIL_URL = "https://www.cninfo.com.cn/data20/leader/detail"
H1_SUMMARY_URL = "https://www.cninfo.com.cn/data20/leader/summary"

PLANNING_MD = (
    BASE_DIR
    / "plans"
    / "cninfo_d_class_executive_shareholding_summary_discovery_planning_20260715.md"
)
MATRIX_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_summary_discovery_candidate_matrix_20260715.csv"
)
RECOMMENDATION_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_summary_discovery_recommendation_20260715.md"
)
SUMMARY_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_summary_discovery_planning_summary_20260715.md"
)
ENDPOINT_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_summary_endpoint_hypothesis_20260715.md"
)
UI_FIELD_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_summary_ui_field_sketch_20260715.csv"
)
UNIVERSE_SKETCH = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_summary_first_slice_universe_draft_sketch_20260715.csv"
)
CHECKLIST_CSV = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_summary_offline_prep_checklist_stub_20260715.csv"
)
NEXT_STEP_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_summary_discovery_next_step_recommendation_20260715.md"
)
EVIDENCE_MD = (
    BASE_DIR
    / "outputs"
    / "validation"
    / "cninfo_d_class_executive_shareholding_summary_dfm21_offline_discovery_20260715.md"
)
REGISTRY = BASE_DIR / "config" / "cninfo_d_class_source_registry_draft.yaml"
PRIORITY2_SEMANTICS = (
    BASE_DIR / "outputs" / "validation" / "cninfo_table_field_semantics_priority2.md"
)

REQUIRED_UI_LABELS = (
    "变动统计区间",
    "证券代码",
    "证券简称",
    "变动类型",
    "高管持股变动数量合计(万股)",
)

GATE_TOKEN = (
    "d_class_executive_shareholding_summary_discovery_planning_gate = READY_FOR_APPROVAL"
)


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class ExecutiveShareholdingSummaryOfflineDiscoveryTests(unittest.TestCase):
    """D-FM-21：ESS offline discovery 产物结构校验（无网络）。"""

    def test_core_artifacts_exist_and_utf8_chinese(self) -> None:
        paths = [
            PLANNING_MD,
            MATRIX_CSV,
            RECOMMENDATION_MD,
            SUMMARY_MD,
            ENDPOINT_MD,
            UI_FIELD_CSV,
            UNIVERSE_SKETCH,
            CHECKLIST_CSV,
            NEXT_STEP_MD,
            EVIDENCE_MD,
        ]
        for path in paths:
            self.assertTrue(path.is_file(), f"missing {path}")
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("\ufffd", text)
            # md 须含中文组件名；csv 可用英文 source_id
            self.assertTrue(
                ("高管持股" in text) or (COMPONENT in text),
                f"missing ESS marker in {path}",
            )

    def test_planning_gate_and_red_lines(self) -> None:
        text = PLANNING_MD.read_text(encoding="utf-8")
        self.assertIn(GATE_TOKEN, text)
        self.assertIn("endpoint_status = unconfirmed", text)
        self.assertIn("registry_status = not_registered", text)
        self.assertIn("No CNINFO", text)
        self.assertIn("No Level-2 IDLE", text)
        self.assertIn("DLC006R", text)
        self.assertIn(COMPONENT, text)

    def test_candidate_matrix_ranks_ess_primary(self) -> None:
        rows = _read_csv(MATRIX_CSV)
        by_component = {r["component"]: r for r in rows}
        self.assertIn(COMPONENT, by_component)
        self.assertEqual(by_component[COMPONENT]["recommendation_rank"], "1")
        self.assertEqual(by_component[COMPONENT]["endpoint_readiness"], "unconfirmed_ui_only")
        self.assertEqual(
            by_component["fund_industry_allocation_scale"]["recommendation_rank"], "2"
        )
        self.assertEqual(
            by_component["abnormal_trading_scale"]["recommendation_rank"], "excluded"
        )
        self.assertEqual(
            by_component["shareholder_data_scale"]["recommendation_rank"], "excluded"
        )
        self.assertEqual(
            by_component["executive_shareholding"]["recommendation_rank"], "excluded"
        )
        self.assertEqual(
            by_component["known_event_replacement"]["recommendation_rank"], "excluded"
        )
        self.assertEqual(
            by_component["fund_industry_allocation_first_slice_live_roots"][
                "recommendation_rank"
            ],
            "excluded",
        )

    def test_ui_field_sketch_covers_priority2_headers(self) -> None:
        self.assertTrue(PRIORITY2_SEMANTICS.is_file())
        semantics = PRIORITY2_SEMANTICS.read_text(encoding="utf-8")
        self.assertIn("高管持股变动汇总", semantics)
        rows = _read_csv(UI_FIELD_CSV)
        labels = [r["ui_label"] for r in rows]
        self.assertEqual(tuple(labels), REQUIRED_UI_LABELS)
        for row in rows:
            self.assertEqual(row["raw_field_status"], "unknown")
            self.assertTrue(row["standard_candidate"])

    def test_endpoint_hypothesis_lists_h1_and_sibling(self) -> None:
        text = ENDPOINT_MD.read_text(encoding="utf-8")
        self.assertIn(SIBLING_DETAIL_URL, text)
        self.assertIn(H1_SUMMARY_URL, text)
        self.assertIn("probe_executed = false", text)
        self.assertIn("cninfo_calls = 0", text)
        self.assertIn("unprobed", text)

    def test_universe_sketch_five_cases_and_excludes(self) -> None:
        rows = _read_csv(UNIVERSE_SKETCH)
        self.assertEqual(len(rows), 5)
        self.assertEqual(tuple(r["case_id"] for r in rows), CASE_IDS)
        for row in rows:
            self.assertEqual(row["component"], COMPONENT)
            self.assertEqual(row["first_slice_include"], "yes")
            self.assertEqual(row["endpoint_status"], "unconfirmed")
            flags = row["exclude_flags"]
            self.assertIn("exclude_688671", flags)
            self.assertIn("exclude_301259", flags)
            self.assertIn("exclude_es_detail_reopen", flags)
            self.assertIn("exclude_fia_live_root_mutate", flags)
            # sketch 阶段不得误把排除码写成 case 主键字段
            self.assertNotIn(row["case_id"], EXCLUDED_CODES)

    def test_registry_has_sibling_but_not_ess(self) -> None:
        self.assertTrue(REGISTRY.is_file())
        text = REGISTRY.read_text(encoding="utf-8")
        self.assertIn("source_id: executive_shareholding", text)
        self.assertIn("leader/detail", text)
        self.assertIn("future executive_shareholding_summary", text)
        self.assertNotIn("source_id: executive_shareholding_summary", text)

    def test_checklist_blocks_live_and_registry_freeze(self) -> None:
        rows = _read_csv(CHECKLIST_CSV)
        by_id = {r["item_id"]: r for r in rows}
        self.assertEqual(by_id["ESS-GATE-01"]["status"], "READY_FOR_APPROVAL")
        self.assertEqual(by_id["ESS-STUB-06"]["status"], "forbidden_this_round")
        self.assertEqual(by_id["ESS-STUB-05"]["status"], "forbidden_this_round")
        self.assertEqual(by_id["ESS-STUB-04"]["status"], "blocked_until_endpoint_probe")
        self.assertEqual(by_id["ESS-SAFE-04"]["status"], "locked_policy")

    def test_no_network_imports_for_cninfo(self) -> None:
        import lab.test_cninfo_d_class_executive_shareholding_summary_offline_discovery as self_mod

        self.assertFalse(hasattr(self_mod, "requests"))
        self.assertFalse(hasattr(self_mod, "urllib"))
        src = Path(self_mod.__file__).read_text(encoding="utf-8")
        # 避免字面量自引用误伤断言行：拆开检查禁网络导入
        banned = (
            "import " + "requests",
            "from " + "requests",
            "urllib" + ".request",
            "http" + ".client",
        )
        for token in banned:
            self.assertNotIn(token, src)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    unittest.main(verbosity=2)
