"""
B-FM-42：债券受托管理事务报告 / 跟踪评级报告 known_002 晋升锁测（离线）。

覆盖：
- bond_trustee_report_known_002 与 tracking_rating_report_known_002 已为 ready
- title_pattern 与 known_001 / 保荐书 / 权益变动 / 法律意见书 / 股东会决议可区分
- harvest 标题经既有 B-FM-29 路由预测 announcement → general（非 other）
- 既有 LIVE_PASS 路径不回退（含 known_001 与 B-FM-41 激励名单/销售简报）
- 不重开 bond_trustee / tracking_rating known_001 LIVE_PASS（仅扩 known_002）

无 CNINFO · 无 live · 不造 §7 FP。本包不改路由。

运行：
    python lab/test_cninfo_b_class_bond_trustee_rating_known_002_promotion.py
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

HARVEST_TRUSTEE_002 = "深圳能源集团股份有限公司公司债券受托管理事务报告（2024年度）"
HARVEST_RATING_002 = "长江证券股份有限公司2025年跟踪评级报告"
HARVEST_TRUSTEE_001 = (
    "申港证券股份有限公司关于三羊马(重庆)物流股份有限公司向不特定对象"
    "发行可转换公司债券受托管理事务报告（2024年度）"
)
HARVEST_RATING_001 = (
    "2020年浙江华海药业股份有限公司公开发行可转换公司债券定期跟踪评级报告"
)
PATTERN_TRUSTEE_002 = "股份有限公司公司债券受托管理事务报告（2024年度）"
PATTERN_RATING_002 = "股份有限公司2025年跟踪评级报告"
PATTERN_TRUSTEE_001 = "可转换公司债券受托管理事务报告（2024年度）"
PATTERN_RATING_001 = "跟踪评级报告"
PATTERN_SPONSOR = "可转换公司债券的上市保荐书"
PATTERN_EQUITY = "权益变动报告书"
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


class TestBondTrusteeRatingKnown002Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_bond_trustee_report_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "bond_trustee_report_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000027")
        self.assertEqual(c["company_name"], "深圳能源")
        self.assertEqual(c["title_pattern"], PATTERN_TRUSTEE_002)
        self.assertEqual(c["date_start"], "2025-06-29")
        self.assertEqual(c["date_end"], "2025-07-02")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_TRUSTEE_002, HARVEST_TRUSTEE_002)
        self.assertIn("公司债券受托管理事务报告", c["title_pattern"])
        self.assertNotIn("可转换", c["title_pattern"])
        self.assertNotEqual(c["title_pattern"], "受托管理事务报告")
        self.assertTrue(retrieval._title_matches(HARVEST_TRUSTEE_002, PATTERN_TRUSTEE_002))
        self.assertFalse(retrieval._title_matches(HARVEST_TRUSTEE_001, PATTERN_TRUSTEE_002))

    def test_tracking_rating_report_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "tracking_rating_report_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000783")
        self.assertEqual(c["company_name"], "长江证券")
        self.assertEqual(c["title_pattern"], PATTERN_RATING_002)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_RATING_002, HARVEST_RATING_002)
        self.assertIn("2025年跟踪评级报告", c["title_pattern"])
        self.assertNotEqual(c["title_pattern"], PATTERN_RATING_001)
        self.assertTrue(retrieval._title_matches(HARVEST_RATING_002, PATTERN_RATING_002))
        self.assertFalse(retrieval._title_matches(HARVEST_RATING_001, PATTERN_RATING_002))

    def test_patterns_mutually_distinct_from_known_001(self) -> None:
        """known_002 pattern 与 known_001 / 保荐书 / 权益变动互斥。"""
        self.assertNotEqual(PATTERN_TRUSTEE_002, PATTERN_TRUSTEE_001)
        self.assertNotEqual(PATTERN_RATING_002, PATTERN_RATING_001)
        self.assertNotEqual(PATTERN_TRUSTEE_002, PATTERN_RATING_002)
        self.assertNotIn("保荐书", PATTERN_TRUSTEE_002)
        self.assertNotIn("权益变动", PATTERN_RATING_002)
        self.assertNotIn("法律意见", PATTERN_TRUSTEE_002)
        self.assertNotIn("股东大会", PATTERN_RATING_002)
        self.assertIn(PATTERN_TRUSTEE_001, HARVEST_TRUSTEE_001)
        self.assertIn(PATTERN_RATING_001, HARVEST_RATING_001)
        self.assertFalse(retrieval._title_matches(HARVEST_TRUSTEE_002, PATTERN_TRUSTEE_001))
        self.assertTrue(retrieval._title_matches(HARVEST_RATING_002, PATTERN_RATING_001))
        self.assertFalse(retrieval._title_matches(HARVEST_TRUSTEE_002, PATTERN_SPONSOR))
        self.assertFalse(retrieval._title_matches(HARVEST_RATING_002, PATTERN_EQUITY))

    def test_harvest_titles_route_announcement_not_other(self) -> None:
        for title in (HARVEST_TRUSTEE_002, HARVEST_RATING_002, HARVEST_TRUSTEE_001, HARVEST_RATING_001):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_sponsor = routing.route_title(
            "国信证券股份有限公司关于石家庄尚太科技股份有限公司主板向不特定对象"
            "发行可转换公司债券的上市保荐书（修订稿）",
            self.config,
        )
        self.assertEqual(r_sponsor.predicted_document_type, "announcement")
        r_equity = routing.route_title("德林海简式权益变动报告书", self.config)
        self.assertEqual(r_equity.predicted_document_type, "announcement")
        r_legal = routing.route_title(LEGAL_REAL, self.config)
        self.assertEqual(r_legal.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        r_list = routing.route_title(
            "英科再生资源股份有限公司2025年限制性股票激励计划激励对象名单（授予日）",
            self.config,
        )
        self.assertEqual(r_list.predicted_document_type, "announcement")
        r_brief = routing.route_title("2025年5月畜牧行业销售简报", self.config)
        self.assertEqual(r_brief.predicted_document_type, "announcement")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）；含 known_001。"""
        for case_id in (
            "bond_trustee_report_known_001",
            "tracking_rating_report_known_001",
            "listing_sponsor_known_001",
            "equity_change_report_known_001",
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
            "bond_trustee_report_known_002",
            "tracking_rating_report_known_002",
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
