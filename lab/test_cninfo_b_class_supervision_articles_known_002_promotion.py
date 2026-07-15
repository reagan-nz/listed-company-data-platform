"""
B-FM-43：持续督导年度报告书 / 公司章程 known_002 晋升锁测（离线）。

覆盖：
- continuous_supervision_annual_known_002 与 company_articles_known_002 已为 ready
- title_pattern 与 known_001 / 培训报告 / 管理制度 / 年报可区分
- harvest 标题经既有 B-FM-30 / B-FM-36 路由预测 announcement → general（非 other /
  annual_report）
- 既有 LIVE_PASS 路径不回退（含 known_001 与 B-FM-42 债券受托/跟踪评级）
- 不重开 continuous_supervision / company_articles known_001 LIVE_PASS（仅扩 known_002）

无 CNINFO · 无 live · 不造 §7 FP。本包不改路由。

运行：
    python lab/test_cninfo_b_class_supervision_articles_known_002_promotion.py
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

HARVEST_CSA_002 = (
    "中国国际金融股份有限公司关于中国国检测试控股集团股份有限公司"
    "2024年度持续督导年度报告书"
)
HARVEST_ARTICLES_002 = "江苏秀强玻璃工艺股份有限公司章程（2025年6月修订）"
HARVEST_CSA_001 = (
    "中国国际金融股份有限公司关于江苏恒立液压股份有限公司2024年度持续督导年度报告书"
)
HARVEST_ARTICLES_001 = "安徽古麒绒材股份有限公司章程（2025年6月修订）"
HARVEST_TRAINING = (
    "国投证券股份有限公司关于芜湖三联锻造股份有限公司2025年度持续督导培训情况的报告"
)
HARVEST_ANNUAL_REPORT = "江苏恒立液压股份有限公司2024年年度报告"
PATTERN_CSA_002 = "国检测试控股集团股份有限公司2024年度持续督导年度报告书"
PATTERN_ARTICLES_002 = "秀强玻璃工艺股份有限公司章程（2025年6月修订）"
PATTERN_CSA_001 = "持续督导年度报告书"
PATTERN_ARTICLES_001 = "公司章程（2025年6月修订）"
PATTERN_FUNDS_SYS = "募集资金管理制度"
PATTERN_TRUSTEE_002 = "股份有限公司公司债券受托管理事务报告（2024年度）"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
LEGAL_REAL = (
    "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书"
)


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestSupervisionArticlesKnown002Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_continuous_supervision_annual_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "continuous_supervision_annual_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "603060")
        self.assertEqual(c["company_name"], "国检集团")
        self.assertEqual(c["title_pattern"], PATTERN_CSA_002)
        self.assertEqual(c["date_start"], "2025-04-26")
        self.assertEqual(c["date_end"], "2025-04-29")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_CSA_002, HARVEST_CSA_002)
        self.assertIn("持续督导年度报告书", c["title_pattern"])
        self.assertNotEqual(c["title_pattern"], PATTERN_CSA_001)
        self.assertTrue(retrieval._title_matches(HARVEST_CSA_002, PATTERN_CSA_002))
        self.assertFalse(retrieval._title_matches(HARVEST_CSA_001, PATTERN_CSA_002))
        self.assertFalse(retrieval._title_matches(HARVEST_TRAINING, PATTERN_CSA_002))

    def test_company_articles_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "company_articles_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300160")
        self.assertEqual(c["company_name"], "秀强股份")
        self.assertEqual(c["title_pattern"], PATTERN_ARTICLES_002)
        self.assertEqual(c["date_start"], "2025-06-19")
        self.assertEqual(c["date_end"], "2025-06-22")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_ARTICLES_002, HARVEST_ARTICLES_002)
        self.assertIn("公司章程（2025年6月修订）", c["title_pattern"])
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_001)
        self.assertNotEqual(c["title_pattern"], "章程")
        self.assertTrue(retrieval._title_matches(HARVEST_ARTICLES_002, PATTERN_ARTICLES_002))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_001, PATTERN_ARTICLES_002))

    def test_patterns_mutually_distinct_from_known_001(self) -> None:
        """known_002 pattern 与 known_001 / 培训 / 管理制度 / 年报互斥。"""
        self.assertNotEqual(PATTERN_CSA_002, PATTERN_CSA_001)
        self.assertNotEqual(PATTERN_ARTICLES_002, PATTERN_ARTICLES_001)
        self.assertNotEqual(PATTERN_CSA_002, PATTERN_ARTICLES_002)
        self.assertNotIn("培训情况", PATTERN_CSA_002)
        self.assertNotIn("管理制度", PATTERN_ARTICLES_002)
        self.assertNotIn("年度报告", PATTERN_ARTICLES_002)
        self.assertTrue(retrieval._title_matches(HARVEST_CSA_001, PATTERN_CSA_001))
        self.assertTrue(retrieval._title_matches(HARVEST_ARTICLES_001, PATTERN_ARTICLES_001))
        # known_001 宽串仍可命中 known_002 标题（公司窗隔离）；窄串不得反向命中 known_001
        self.assertTrue(retrieval._title_matches(HARVEST_CSA_002, PATTERN_CSA_001))
        self.assertTrue(retrieval._title_matches(HARVEST_ARTICLES_002, PATTERN_ARTICLES_001))
        self.assertFalse(retrieval._title_matches(HARVEST_ANNUAL_REPORT, PATTERN_CSA_002))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_002, PATTERN_FUNDS_SYS))
        self.assertFalse(retrieval._title_matches(HARVEST_CSA_002, PATTERN_TRUSTEE_002))

    def test_harvest_titles_route_announcement_not_other_or_annual(self) -> None:
        for title in (
            HARVEST_CSA_002,
            HARVEST_ARTICLES_002,
            HARVEST_CSA_001,
            HARVEST_ARTICLES_001,
            HARVEST_TRAINING,
        ):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")
                self.assertNotEqual(r.predicted_document_type, "annual_report")
        r_annual = routing.route_title(HARVEST_ANNUAL_REPORT, self.config)
        self.assertEqual(r_annual.predicted_document_type, "annual_report")

    def test_prior_paths_not_regressed(self) -> None:
        r_trustee = routing.route_title(
            "深圳能源集团股份有限公司公司债券受托管理事务报告（2024年度）",
            self.config,
        )
        self.assertEqual(r_trustee.predicted_document_type, "announcement")
        r_rating = routing.route_title(
            "长江证券股份有限公司2025年跟踪评级报告", self.config
        )
        self.assertEqual(r_rating.predicted_document_type, "announcement")
        r_legal = routing.route_title(LEGAL_REAL, self.config)
        self.assertEqual(r_legal.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        r_funds = routing.route_title("绿城水务股份有限公司募集资金管理制度", self.config)
        self.assertEqual(r_funds.predicted_document_type, "announcement")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）；含 known_001 与 B-FM-42。"""
        for case_id in (
            "continuous_supervision_annual_known_001",
            "continuous_supervision_training_known_001",
            "company_articles_known_001",
            "raised_funds_management_system_known_001",
            "bond_trustee_report_known_001",
            "bond_trustee_report_known_002",
            "tracking_rating_report_known_001",
            "tracking_rating_report_known_002",
            "incentive_object_list_known_001",
            "sales_brief_known_001",
            "external_guarantee_situation_brief_known_001",
            "esg_report_known_001",
            "legal_opinion_known_005",
            "legal_opinion_known_006",
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
            "continuous_supervision_annual_known_002",
            "company_articles_known_002",
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
