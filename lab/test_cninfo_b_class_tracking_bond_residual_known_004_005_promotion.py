"""
B-FM-01（R19）：跟踪评级 known_004/005 + 债券受托 known_004 晋升锁测（离线）。

覆盖：
- tracking_rating_report_known_004 已为 ready（BD2E606 南京聚隆相关债券）
- tracking_rating_report_known_005 已为 ready（BD2E636 申昊科技主体及转债）
- bond_trustee_report_known_004 已为 ready（B2E013 京东方A 可续期公司债）
- title_pattern 与 known_001–003 可区分；新 pattern 不反向误抬旧 harvest
- harvest 标题经既有路由预测为 announcement（非 other / 非 annual_report）
- 既有 LIVE_PASS 路径不回退；拒绝 deferred known_002 薄 harvest 与 audit 年报陷阱

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_tracking_bond_residual_known_004_005_promotion.py
"""

from __future__ import annotations

import os
import sys
import unittest

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_b_class_category_routing as routing  # noqa: E402
import validate_cninfo_b_class_corpus_retrieval as retrieval  # noqa: E402

KNOWN_YAML = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

HARVEST_TR_004 = "南京聚隆科技股份有限公司相关债券2025年跟踪评级报告"
HARVEST_TR_005 = "杭州申昊科技股份有限公司主体及“申昊转债”2025年度跟踪评级报告"
HARVEST_BT_004 = "京东方科技集团股份有限公司可续期公司债券受托管理事务报告（2024年度）"
HARVEST_TR_001 = "2020年浙江华海药业股份有限公司公开发行可转换公司债券定期跟踪评级报告"
HARVEST_TR_002 = "长江证券股份有限公司2025年跟踪评级报告"
HARVEST_TR_003 = (
    "中国宝安集团股份有限公司2022年面向合格投资者公开发行公司债券(第一期)定期跟踪评级报告"
)
HARVEST_BT_001 = (
    "申港证券股份有限公司关于三羊马(重庆)物流股份有限公司向不特定对象"
    "发行可转换公司债券受托管理事务报告（2024年度）"
)
HARVEST_BT_002 = "深圳能源集团股份有限公司公司债券受托管理事务报告（2024年度）"
HARVEST_BT_003 = (
    "中联重科股份有限公司2019年面向合格投资者公开发行公司债券（第一期）"
    "受托管理事务报告（2024年度）"
)
PATTERN_TR_004 = "相关债券2025年跟踪评级报告"
PATTERN_TR_005 = "主体及“申昊转债”2025年度跟踪评级报告"
PATTERN_BT_004 = "可续期公司债券受托管理事务报告（2024年度）"
PATTERN_TR_001 = "跟踪评级报告"
PATTERN_TR_002 = "股份有限公司2025年跟踪评级报告"
PATTERN_TR_003 = "公开发行公司债券(第一期)定期跟踪评级报告"
PATTERN_BT_001 = "可转换公司债券受托管理事务报告（2024年度）"
PATTERN_BT_002 = "股份有限公司公司债券受托管理事务报告（2024年度）"
PATTERN_BT_003 = "公开发行公司债券（第一期）受托管理事务报告（2024年度）"
SM_RES = "2025年第二次临时股东大会决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestTrackingBondResidualKnown004005Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_tracking_rating_known_004_ready_fields(self) -> None:
        c = _by_id(self.known, "tracking_rating_report_known_004")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300644")
        self.assertEqual(c["company_name"], "南京聚隆")
        self.assertEqual(c["title_pattern"], PATTERN_TR_004)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_TR_004, HARVEST_TR_004)
        self.assertNotEqual(c["title_pattern"], PATTERN_TR_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_TR_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_TR_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_TR_005)
        self.assertTrue(retrieval._title_matches(HARVEST_TR_004, PATTERN_TR_004))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_001, PATTERN_TR_004))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_002, PATTERN_TR_004))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_003, PATTERN_TR_004))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_005, PATTERN_TR_004))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_004, PATTERN_TR_004))

    def test_tracking_rating_known_005_ready_fields(self) -> None:
        c = _by_id(self.known, "tracking_rating_report_known_005")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300853")
        self.assertEqual(c["company_name"], "申昊科技")
        self.assertEqual(c["title_pattern"], PATTERN_TR_005)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertIn(PATTERN_TR_005, HARVEST_TR_005)
        self.assertNotEqual(c["title_pattern"], PATTERN_TR_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_TR_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_TR_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_TR_004)
        self.assertTrue(retrieval._title_matches(HARVEST_TR_005, PATTERN_TR_005))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_001, PATTERN_TR_005))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_002, PATTERN_TR_005))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_003, PATTERN_TR_005))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_004, PATTERN_TR_005))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_004, PATTERN_TR_005))

    def test_bond_trustee_known_004_ready_fields(self) -> None:
        c = _by_id(self.known, "bond_trustee_report_known_004")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000725")
        self.assertEqual(c["company_name"], "京东方A")
        self.assertEqual(c["title_pattern"], PATTERN_BT_004)
        self.assertEqual(c["date_start"], "2025-06-29")
        self.assertEqual(c["date_end"], "2025-07-02")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_BT_004, HARVEST_BT_004)
        self.assertNotEqual(c["title_pattern"], PATTERN_BT_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_BT_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_BT_003)
        self.assertTrue(retrieval._title_matches(HARVEST_BT_004, PATTERN_BT_004))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_001, PATTERN_BT_004))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_002, PATTERN_BT_004))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_003, PATTERN_BT_004))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_004, PATTERN_BT_004))

    def test_patterns_mutually_distinct(self) -> None:
        patterns = [
            PATTERN_TR_001,
            PATTERN_TR_002,
            PATTERN_TR_003,
            PATTERN_TR_004,
            PATTERN_TR_005,
            PATTERN_BT_001,
            PATTERN_BT_002,
            PATTERN_BT_003,
            PATTERN_BT_004,
        ]
        self.assertEqual(len(patterns), len(set(patterns)))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_004, PATTERN_BT_004))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_004, PATTERN_TR_004))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_005, PATTERN_TR_004))
        self.assertFalse(retrieval._title_matches(HARVEST_TR_004, PATTERN_TR_005))

    def test_harvest_titles_route_correctly(self) -> None:
        for title in (HARVEST_TR_004, HARVEST_TR_005, HARVEST_BT_004):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")
                self.assertNotEqual(r.predicted_document_type, "annual_report")

    def test_prior_paths_not_regressed(self) -> None:
        for title, expected in (
            (HARVEST_TR_001, "announcement"),
            (HARVEST_TR_002, "announcement"),
            (HARVEST_TR_003, "announcement"),
            (HARVEST_BT_001, "announcement"),
            (HARVEST_BT_002, "announcement"),
            (HARVEST_BT_003, "announcement"),
        ):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, expected)
                self.assertNotEqual(r.predicted_document_type, "other")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_trap = routing.route_title("天健审〔2025〕11-195号 川网传媒2024年报审计报告", self.config)
        self.assertEqual(r_trap.predicted_document_type, "annual_report")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        for case_id in (
            "tracking_rating_report_known_001",
            "tracking_rating_report_known_002",
            "tracking_rating_report_known_003",
            "bond_trustee_report_known_001",
            "bond_trustee_report_known_002",
            "bond_trustee_report_known_003",
            "supervisory_board_known_005",
            "continuous_supervision_annual_known_005",
            "listing_sponsor_known_001",
            "equity_change_report_known_001",
            "independent_director_meeting_review_known_001",
            "asset_valuation_explanation_known_001",
            "continuous_supervision_training_known_001",
            "audit_report_known_001",
        ):
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                self.assertEqual(c["case_status"], "ready")

    def test_deferred_known_002_families_not_promoted(self) -> None:
        ids = {c["case_id"] for c in self.known}
        for case_id in (
            "independent_director_meeting_review_known_002",
            "asset_valuation_explanation_known_002",
            "listing_sponsor_known_002",
            "continuous_supervision_training_known_002",
            "audit_report_known_002",
            "equity_change_report_known_002",
        ):
            self.assertNotIn(case_id, ids)

    def test_new_ready_cases_pass_dry_run_field_validation(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        registry_ids = retrieval._load_registry_source_ids(registry)
        document_types = retrieval._load_document_types(schema)
        for case_id in (
            "tracking_rating_report_known_004",
            "tracking_rating_report_known_005",
            "bond_trustee_report_known_004",
        ):
            with self.subTest(case_id=case_id):
                case = _by_id(self.known, case_id)
                row = retrieval._process_case(
                    case, "known_document", registry_ids, document_types, dry_run=True
                )
                self.assertEqual(row["dry_run_status"], "ready_for_future_live_validation")
                self.assertEqual(row["would_query"], "true")
                notes = case["notes"]
                self.assertIn("B-FM-01", notes)
                self.assertTrue(any("\u4e00" <= ch <= "\u9fff" for ch in notes))


if __name__ == "__main__":
    unittest.main()
