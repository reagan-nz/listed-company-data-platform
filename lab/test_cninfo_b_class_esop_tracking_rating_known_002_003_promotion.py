"""
B-FM-46：员工持股计划 known_002 / 跟踪评级 known_003 晋升锁测（离线）。

覆盖：
- employee_stock_ownership_plan_known_002 已为 ready（BD2E672）
- tracking_rating_report_known_003 已为 ready（BD2E051）
- title_pattern 与 known_001 草案 / known_001–002 跟踪评级可区分
- harvest 标题经既有 B-FM-35 / B-FM-29 路由预测 announcement → general（非 other）
- 既有 LIVE_PASS 路径不回退（含 ESOP known_001、tracking known_001/002、B-FM-45）
- 本包不改路由；不重开已 LIVE_PASS 案

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_esop_tracking_rating_known_002_003_promotion.py
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

HARVEST_ESOP_002 = "2025年员工持股计划第一次持有人会议决议公告"
HARVEST_ESOP_001 = "第二期员工持股计划（草案）(修订稿）"
HARVEST_ESOP_PRICE = "快克智能关于调整公司2025年员工持股计划购买价格的公告"
HARVEST_RATING_003 = (
    "中国宝安集团股份有限公司2022年面向合格投资者公开发行公司债券(第一期)定期跟踪评级报告"
)
HARVEST_RATING_001 = (
    "2020年浙江华海药业股份有限公司公开发行可转换公司债券定期跟踪评级报告"
)
HARVEST_RATING_002 = "长江证券股份有限公司2025年跟踪评级报告"
PATTERN_ESOP_002 = "员工持股计划第一次持有人会议决议"
PATTERN_ESOP_001 = "第二期员工持股计划（草案）(修订稿）"
PATTERN_RATING_003 = "公开发行公司债券(第一期)定期跟踪评级报告"
PATTERN_RATING_001 = "跟踪评级报告"
PATTERN_RATING_002 = "股份有限公司2025年跟踪评级报告"
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


class TestEsopTrackingRatingKnown002003Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_esop_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "employee_stock_ownership_plan_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "301063")
        self.assertEqual(c["company_name"], "海锅股份")
        self.assertEqual(c["title_pattern"], PATTERN_ESOP_002)
        self.assertEqual(c["date_start"], "2025-06-19")
        self.assertEqual(c["date_end"], "2025-06-22")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_ESOP_002, HARVEST_ESOP_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_ESOP_001)
        self.assertNotEqual(c["title_pattern"], "员工持股计划")
        self.assertTrue(retrieval._title_matches(HARVEST_ESOP_002, PATTERN_ESOP_002))
        self.assertFalse(retrieval._title_matches(HARVEST_ESOP_001, PATTERN_ESOP_002))
        self.assertFalse(retrieval._title_matches(HARVEST_ESOP_PRICE, PATTERN_ESOP_002))

    def test_tracking_rating_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "tracking_rating_report_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000009")
        self.assertEqual(c["company_name"], "中国宝安")
        self.assertEqual(c["title_pattern"], PATTERN_RATING_003)
        self.assertEqual(c["date_start"], "2025-06-15")
        self.assertEqual(c["date_end"], "2025-06-18")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_RATING_003, HARVEST_RATING_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_RATING_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_RATING_002)
        self.assertNotEqual(c["title_pattern"], "跟踪评级报告")
        self.assertTrue(retrieval._title_matches(HARVEST_RATING_003, PATTERN_RATING_003))
        self.assertFalse(retrieval._title_matches(HARVEST_RATING_001, PATTERN_RATING_003))
        self.assertFalse(retrieval._title_matches(HARVEST_RATING_002, PATTERN_RATING_003))
        self.assertFalse(retrieval._title_matches(HARVEST_RATING_003, PATTERN_RATING_002))

    def test_patterns_mutually_distinct(self) -> None:
        self.assertNotEqual(PATTERN_ESOP_002, PATTERN_ESOP_001)
        self.assertNotEqual(PATTERN_RATING_003, PATTERN_RATING_002)
        self.assertFalse(retrieval._title_matches(HARVEST_ESOP_002, PATTERN_RATING_003))
        self.assertFalse(retrieval._title_matches(HARVEST_RATING_003, PATTERN_ESOP_002))

    def test_harvest_titles_route_announcement(self) -> None:
        r_esop = routing.route_title(HARVEST_ESOP_002, self.config)
        self.assertEqual(r_esop.predicted_document_type, "announcement")
        self.assertNotEqual(r_esop.predicted_document_type, "other")
        self.assertEqual(r_esop.predicted_route_to, "cninfo_general_announcement_pdf")
        r_rating = routing.route_title(HARVEST_RATING_003, self.config)
        self.assertEqual(r_rating.predicted_document_type, "announcement")
        self.assertNotEqual(r_rating.predicted_document_type, "other")
        self.assertEqual(r_rating.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_prior_paths_not_regressed(self) -> None:
        r_esop001 = routing.route_title(HARVEST_ESOP_001, self.config)
        self.assertEqual(r_esop001.predicted_document_type, "announcement")
        r_r001 = routing.route_title(HARVEST_RATING_001, self.config)
        self.assertEqual(r_r001.predicted_document_type, "announcement")
        r_r002 = routing.route_title(HARVEST_RATING_002, self.config)
        self.assertEqual(r_r002.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        # 拒绝 audit_report_known_002 年报陷阱仍落 periodic
        r_trap = routing.route_title("天健审〔2025〕11-195号 川网传媒2024年报审计报告", self.config)
        self.assertEqual(r_trap.predicted_document_type, "annual_report")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        for case_id in (
            "employee_stock_ownership_plan_known_001",
            "incentive_trading_self_inspection_known_001",
            "tracking_rating_report_known_001",
            "tracking_rating_report_known_002",
            "bond_trustee_report_known_001",
            "bond_trustee_report_known_002",
            "independent_director_nominee_declaration_known_001",
            "independent_director_nominee_declaration_known_002",
            "verification_opinion_known_001",
            "verification_opinion_known_002",
            "verification_opinion_known_003",
            "independent_director_annual_report_work_system_known_001",
            "independent_director_annual_report_work_system_known_002",
            "continuous_supervision_annual_known_002",
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
            "employee_stock_ownership_plan_known_002",
            "tracking_rating_report_known_003",
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
