"""
B-FM-45：独立董事提名人声明 known_002 / 核查意见 known_003 晋升锁测（离线）。

覆盖：
- independent_director_nominee_declaration_known_002 已为 ready（BD2E059）
- verification_opinion_known_003 已为 ready（BD2E524）
- title_pattern 与 known_001 / 专门会议审核意见 / 等额置换 / 限售流通 /
  激励对象名单核查意见可区分
- harvest 标题经既有 B-FM-33 / B-FM-27 路由预测 announcement → general（非 other）
- 既有 LIVE_PASS 路径不回退（含 nominee/VO known_001、B-FM-44 年报工作制度）
- 本包不改路由；不重开已 LIVE_PASS 案

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_nominee_vo_known_002_003_promotion.py
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

HARVEST_NOMINEE_002 = "独立董事提名人声明与承诺（冯天俊）"
HARVEST_NOMINEE_001 = "独立董事提名人声明与承诺（张永炬）"
HARVEST_VO_003 = (
    "国泰海通证券股份有限公司关于河南通达电缆股份有限公司"
    "募集资金投资项目结项并将节余募集资金永久补充流动资金的核查意见"
)
HARVEST_VO_001 = (
    "华泰联合证券有限责任公司关于三六零安全科技股份有限公司"
    "使用自有资金支付募投项目部分款项并以募集资金等额置换的核查意见"
)
HARVEST_VO_002 = (
    "中信建投证券股份有限公司关于北京福元医药股份有限公司"
    "首次公开发行限售股上市流通的核查意见"
)
HARVEST_INCENTIVE_VO = (
    "监事会关于公司2025年限制性股票激励计划激励对象名单的核查意见及公示情况说明"
)
HARVEST_MEETING_REVIEW = "金枫酒业2025年第二次独立董事专门会议的审核意见"
HARVEST_INED_ANNUAL = "独立董事年度报告工作制度"
PATTERN_NOMINEE_002 = "独立董事提名人声明与承诺（冯天俊）"
PATTERN_NOMINEE_001 = "独立董事提名人声明与承诺（张永炬）"
PATTERN_VO_003 = "节余募集资金永久补充流动资金的核查意见"
PATTERN_VO_001 = "募集资金等额置换的核查意见"
PATTERN_VO_002 = "限售股上市流通的核查意见"
PATTERN_MEETING = "独立董事专门会议的审核意见"
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


class TestNomineeVoKnown002003Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_nominee_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "independent_director_nominee_declaration_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000088")
        self.assertEqual(c["company_name"], "盐田港")
        self.assertEqual(c["title_pattern"], PATTERN_NOMINEE_002)
        self.assertEqual(c["date_start"], "2025-06-19")
        self.assertEqual(c["date_end"], "2025-06-22")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_NOMINEE_002, HARVEST_NOMINEE_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_NOMINEE_001)
        self.assertNotEqual(c["title_pattern"], "独立董事提名人声明与承诺")
        self.assertTrue(retrieval._title_matches(HARVEST_NOMINEE_002, PATTERN_NOMINEE_002))
        self.assertFalse(retrieval._title_matches(HARVEST_NOMINEE_001, PATTERN_NOMINEE_002))
        self.assertFalse(retrieval._title_matches(HARVEST_MEETING_REVIEW, PATTERN_NOMINEE_002))

    def test_vo_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "verification_opinion_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "002560")
        self.assertEqual(c["company_name"], "通达股份")
        self.assertEqual(c["title_pattern"], PATTERN_VO_003)
        self.assertEqual(c["date_start"], "2025-06-24")
        self.assertEqual(c["date_end"], "2025-06-27")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_VO_003, HARVEST_VO_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_VO_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_VO_002)
        self.assertNotEqual(c["title_pattern"], "核查意见")
        self.assertTrue(retrieval._title_matches(HARVEST_VO_003, PATTERN_VO_003))
        self.assertFalse(retrieval._title_matches(HARVEST_VO_001, PATTERN_VO_003))
        self.assertFalse(retrieval._title_matches(HARVEST_VO_002, PATTERN_VO_003))
        self.assertFalse(retrieval._title_matches(HARVEST_INCENTIVE_VO, PATTERN_VO_003))

    def test_patterns_mutually_distinct(self) -> None:
        """新晋 pattern 与 known_001/002 / 专门会议 / 激励核查互斥。"""
        self.assertNotEqual(PATTERN_NOMINEE_002, PATTERN_NOMINEE_001)
        self.assertNotEqual(PATTERN_VO_003, PATTERN_VO_001)
        self.assertNotEqual(PATTERN_VO_003, PATTERN_VO_002)
        self.assertNotEqual(PATTERN_NOMINEE_002, PATTERN_VO_003)
        self.assertNotIn("张永炬", PATTERN_NOMINEE_002)
        self.assertNotIn("等额置换", PATTERN_VO_003)
        self.assertNotIn("限售股", PATTERN_VO_003)
        self.assertTrue(retrieval._title_matches(HARVEST_NOMINEE_001, PATTERN_NOMINEE_001))
        self.assertTrue(retrieval._title_matches(HARVEST_VO_001, PATTERN_VO_001))
        self.assertTrue(retrieval._title_matches(HARVEST_VO_002, PATTERN_VO_002))
        self.assertTrue(retrieval._title_matches(HARVEST_MEETING_REVIEW, PATTERN_MEETING))
        self.assertFalse(retrieval._title_matches(HARVEST_NOMINEE_002, PATTERN_NOMINEE_001))
        self.assertFalse(retrieval._title_matches(HARVEST_INED_ANNUAL, PATTERN_NOMINEE_002))

    def test_harvest_titles_route_announcement_not_other(self) -> None:
        for title in (
            HARVEST_NOMINEE_002,
            HARVEST_NOMINEE_001,
            HARVEST_VO_003,
            HARVEST_VO_001,
            HARVEST_VO_002,
            HARVEST_INCENTIVE_VO,
            HARVEST_MEETING_REVIEW,
        ):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_ined = routing.route_title(HARVEST_INED_ANNUAL, self.config)
        self.assertEqual(r_ined.predicted_document_type, "announcement")
        self.assertNotEqual(r_ined.predicted_document_type, "annual_report")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        r_articles = routing.route_title(
            "江苏秀强玻璃工艺股份有限公司章程（2025年6月修订）", self.config
        )
        self.assertEqual(r_articles.predicted_document_type, "announcement")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）；含 nominee/VO known_001 与 B-FM-44。"""
        for case_id in (
            "independent_director_nominee_declaration_known_001",
            "independent_director_meeting_review_known_001",
            "verification_opinion_known_001",
            "verification_opinion_known_002",
            "independent_director_annual_report_work_system_known_001",
            "independent_director_annual_report_work_system_known_002",
            "continuous_supervision_annual_known_002",
            "company_articles_known_002",
            "bond_trustee_report_known_002",
            "tracking_rating_report_known_002",
            "incentive_object_list_known_001",
            "sales_brief_known_001",
            "shareholder_meeting_known_007",
            "board_resolution_known_001",
        ):
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                self.assertEqual(c["case_status"], "ready")

    def test_new_ready_cases_pass_dry_run_field_validation(self) -> None:
        """新晋 ready 案通过 corpus retrieval dry-run 字段校验。"""
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        registry_ids = retrieval._load_registry_source_ids(registry)
        document_types = retrieval._load_document_types(schema)
        for case_id in (
            "independent_director_nominee_declaration_known_002",
            "verification_opinion_known_003",
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
