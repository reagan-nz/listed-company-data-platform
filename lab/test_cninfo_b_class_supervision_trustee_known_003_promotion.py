"""
B-FM-47：持续督导年度 known_003 / 债券受托 known_003 晋升锁测（离线）。

覆盖：
- continuous_supervision_annual_known_003 已为 ready（BD2E779）
- bond_trustee_report_known_003 已为 ready（BD2E061）
- title_pattern 与 known_001/002 可区分
- harvest 标题经既有 B-FM-30 / B-FM-29 路由预测 announcement → general（非 other / 非 annual_report）
- 既有 LIVE_PASS 路径不回退（含 supervision/trustee known_001/002、B-FM-46）
- 本包不改路由；不重开已 LIVE_PASS 案

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_supervision_trustee_known_003_promotion.py
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

HARVEST_SUP_003 = (
    "首创证券关于和邦生物向不特定对象发行可转换公司债券之2024年持续督导年度报告书"
)
HARVEST_SUP_001 = (
    "中国国际金融股份有限公司关于江苏恒立液压股份有限公司2024年度持续督导年度报告书"
)
HARVEST_SUP_002 = (
    "中国国际金融股份有限公司关于中国国检测试控股集团股份有限公司2024年度持续督导年度报告书"
)
HARVEST_BT_003 = (
    "中联重科股份有限公司2019年面向合格投资者公开发行公司债券（第一期）"
    "受托管理事务报告（2024年度）"
)
HARVEST_BT_001 = (
    "申港证券股份有限公司关于三羊马(重庆)物流股份有限公司向不特定对象"
    "发行可转换公司债券受托管理事务报告（2024年度）"
)
HARVEST_BT_002 = "深圳能源集团股份有限公司公司债券受托管理事务报告（2024年度）"
PATTERN_SUP_003 = "可转换公司债券之2024年持续督导年度报告书"
PATTERN_SUP_001 = "持续督导年度报告书"
PATTERN_SUP_002 = "国检测试控股集团股份有限公司2024年度持续督导年度报告书"
PATTERN_BT_003 = "公开发行公司债券（第一期）受托管理事务报告（2024年度）"
PATTERN_BT_001 = "可转换公司债券受托管理事务报告（2024年度）"
PATTERN_BT_002 = "股份有限公司公司债券受托管理事务报告（2024年度）"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestSupervisionTrusteeKnown003Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_supervision_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "continuous_supervision_annual_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "603077")
        self.assertEqual(c["company_name"], "和邦生物")
        self.assertEqual(c["title_pattern"], PATTERN_SUP_003)
        self.assertEqual(c["date_start"], "2025-04-27")
        self.assertEqual(c["date_end"], "2025-04-30")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_SUP_003, HARVEST_SUP_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_SUP_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_SUP_002)
        self.assertTrue(retrieval._title_matches(HARVEST_SUP_003, PATTERN_SUP_003))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_001, PATTERN_SUP_003))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_002, PATTERN_SUP_003))

    def test_bond_trustee_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "bond_trustee_report_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000157")
        self.assertEqual(c["company_name"], "中联重科")
        self.assertEqual(c["title_pattern"], PATTERN_BT_003)
        self.assertEqual(c["date_start"], "2025-06-29")
        self.assertEqual(c["date_end"], "2025-07-02")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_BT_003, HARVEST_BT_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_BT_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_BT_002)
        self.assertTrue(retrieval._title_matches(HARVEST_BT_003, PATTERN_BT_003))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_001, PATTERN_BT_003))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_002, PATTERN_BT_003))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_003, PATTERN_BT_001))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_003, PATTERN_BT_002))

    def test_patterns_mutually_distinct(self) -> None:
        self.assertNotEqual(PATTERN_SUP_003, PATTERN_SUP_001)
        self.assertNotEqual(PATTERN_SUP_003, PATTERN_SUP_002)
        self.assertNotEqual(PATTERN_BT_003, PATTERN_BT_001)
        self.assertNotEqual(PATTERN_BT_003, PATTERN_BT_002)
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_003, PATTERN_BT_003))
        self.assertFalse(retrieval._title_matches(HARVEST_BT_003, PATTERN_SUP_003))

    def test_harvest_titles_route_announcement(self) -> None:
        r_sup = routing.route_title(HARVEST_SUP_003, self.config)
        self.assertEqual(r_sup.predicted_document_type, "announcement")
        self.assertNotEqual(r_sup.predicted_document_type, "other")
        self.assertNotEqual(r_sup.predicted_document_type, "annual_report")
        self.assertEqual(r_sup.predicted_route_to, "cninfo_general_announcement_pdf")
        r_bt = routing.route_title(HARVEST_BT_003, self.config)
        self.assertEqual(r_bt.predicted_document_type, "announcement")
        self.assertNotEqual(r_bt.predicted_document_type, "other")
        self.assertEqual(r_bt.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_prior_paths_not_regressed(self) -> None:
        r_sup001 = routing.route_title(HARVEST_SUP_001, self.config)
        self.assertEqual(r_sup001.predicted_document_type, "announcement")
        r_bt001 = routing.route_title(HARVEST_BT_001, self.config)
        self.assertEqual(r_bt001.predicted_document_type, "announcement")
        r_bt002 = routing.route_title(HARVEST_BT_002, self.config)
        self.assertEqual(r_bt002.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        # 拒绝 audit_report_known_002 年报陷阱仍落 periodic
        r_trap = routing.route_title("天健审〔2025〕11-195号 川网传媒2024年报审计报告", self.config)
        self.assertEqual(r_trap.predicted_document_type, "annual_report")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        for case_id in (
            "continuous_supervision_annual_known_001",
            "continuous_supervision_annual_known_002",
            "continuous_supervision_training_known_001",
            "bond_trustee_report_known_001",
            "bond_trustee_report_known_002",
            "tracking_rating_report_known_001",
            "tracking_rating_report_known_002",
            "tracking_rating_report_known_003",
            "employee_stock_ownership_plan_known_001",
            "employee_stock_ownership_plan_known_002",
            "company_articles_known_001",
            "company_articles_known_002",
            "listing_sponsor_known_001",
            "asset_valuation_explanation_known_001",
            "independent_director_meeting_review_known_001",
            "audit_report_known_001",
        ):
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                self.assertEqual(c["case_status"], "ready")

    def test_new_ready_cases_pass_dry_run_field_validation(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        registry_ids = retrieval._load_registry_source_ids(registry)
        document_types = retrieval._load_document_types(schema)
        for case_id in (
            "continuous_supervision_annual_known_003",
            "bond_trustee_report_known_003",
        ):
            with self.subTest(case_id=case_id):
                case = _by_id(self.known, case_id)
                row = retrieval._process_case(
                    case, "known_document", registry_ids, document_types, dry_run=True
                )
                self.assertEqual(row["dry_run_status"], "ready_for_future_live_validation")
                self.assertEqual(row["would_query"], "true")


if __name__ == "__main__":
    unittest.main()
