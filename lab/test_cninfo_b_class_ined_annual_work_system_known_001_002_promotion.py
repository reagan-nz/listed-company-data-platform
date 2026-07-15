"""
B-FM-44：独立董事年报/年度报告工作制度 known_001/002 晋升锁测（离线）。

覆盖：
- independent_director_annual_report_work_system_known_001 / known_002 已为 ready
- title_pattern 与独立非执行董事工作制度 / 真·年报 / 提名人声明可区分
- harvest 标题经 B-FM-44 路由预测 announcement → general（非 annual_report / other）
- 既有 LIVE_PASS 路径不回退（含 B-FM-37 NED / B-FM-43 督导章程 known_002）
- 不重开 independent_ned_work_system / continuous_supervision / company_articles LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_ined_annual_work_system_known_001_002_promotion.py
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

HARVEST_001 = "独立董事年度报告工作制度"
HARVEST_002 = "独立董事年报工作制度"
HARVEST_NED = "株洲中车时代电气股份有限公司独立非执行董事工作制度"
HARVEST_ANNUAL = "江苏恒立液压股份有限公司2024年年度报告"
HARVEST_NOMINEE = "独立董事提名人声明与承诺（张永炬）"
PATTERN_001 = "独立董事年度报告工作制度"
PATTERN_002 = "独立董事年报工作制度"
PATTERN_NED = "独立非执行董事工作制度"
PATTERN_NOMINEE = "独立董事提名人声明与承诺（张永炬）"
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


class TestInedAnnualWorkSystemKnown001002Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "independent_director_annual_report_work_system_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "600066")
        self.assertEqual(c["company_name"], "宇通客车")
        self.assertEqual(c["title_pattern"], PATTERN_001)
        self.assertEqual(c["date_start"], "2025-04-24")
        self.assertEqual(c["date_end"], "2025-04-27")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_001, HARVEST_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_NED)
        self.assertTrue(retrieval._title_matches(HARVEST_001, PATTERN_001))
        self.assertFalse(retrieval._title_matches(HARVEST_002, PATTERN_001))
        self.assertFalse(retrieval._title_matches(HARVEST_NED, PATTERN_001))
        self.assertFalse(retrieval._title_matches(HARVEST_ANNUAL, PATTERN_001))

    def test_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "independent_director_annual_report_work_system_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "301198")
        self.assertEqual(c["company_name"], "喜悦智行")
        self.assertEqual(c["title_pattern"], PATTERN_002)
        self.assertEqual(c["date_start"], "2025-06-03")
        self.assertEqual(c["date_end"], "2025-06-06")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_002, HARVEST_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_001)
        self.assertNotEqual(c["title_pattern"], "年报")
        self.assertNotEqual(c["title_pattern"], "工作制度")
        self.assertTrue(retrieval._title_matches(HARVEST_002, PATTERN_002))
        self.assertFalse(retrieval._title_matches(HARVEST_001, PATTERN_002))
        self.assertFalse(retrieval._title_matches(HARVEST_NED, PATTERN_002))

    def test_patterns_mutually_distinct(self) -> None:
        """known_001/002 pattern 与 NED / 真·年报 / 提名人声明互斥。"""
        self.assertNotEqual(PATTERN_001, PATTERN_002)
        self.assertNotEqual(PATTERN_001, PATTERN_NED)
        self.assertNotEqual(PATTERN_002, PATTERN_NED)
        self.assertNotIn("独立非执行", PATTERN_001)
        self.assertNotIn("独立非执行", PATTERN_002)
        self.assertTrue(retrieval._title_matches(HARVEST_NED, PATTERN_NED))
        self.assertTrue(retrieval._title_matches(HARVEST_NOMINEE, PATTERN_NOMINEE))
        self.assertFalse(retrieval._title_matches(HARVEST_001, PATTERN_NED))
        self.assertFalse(retrieval._title_matches(HARVEST_002, PATTERN_NED))
        self.assertFalse(retrieval._title_matches(HARVEST_ANNUAL, PATTERN_002))

    def test_harvest_titles_route_announcement_not_annual_or_other(self) -> None:
        for title in (HARVEST_001, HARVEST_002, HARVEST_NED, HARVEST_NOMINEE):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")
                self.assertNotEqual(r.predicted_document_type, "annual_report")
        r_annual = routing.route_title(HARVEST_ANNUAL, self.config)
        self.assertEqual(r_annual.predicted_document_type, "annual_report")

    def test_prior_paths_not_regressed(self) -> None:
        r_csa = routing.route_title(
            "中国国际金融股份有限公司关于中国国检测试控股集团股份有限公司"
            "2024年度持续督导年度报告书",
            self.config,
        )
        self.assertEqual(r_csa.predicted_document_type, "announcement")
        r_articles = routing.route_title(
            "江苏秀强玻璃工艺股份有限公司章程（2025年6月修订）", self.config
        )
        self.assertEqual(r_articles.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）。"""
        for case_id in (
            "independent_ned_work_system_known_001",
            "general_manager_work_rules_known_001",
            "independent_director_meeting_review_known_001",
            "independent_director_nominee_declaration_known_001",
            "continuous_supervision_annual_known_001",
            "continuous_supervision_annual_known_002",
            "company_articles_known_001",
            "company_articles_known_002",
            "bond_trustee_report_known_002",
            "tracking_rating_report_known_002",
            "incentive_object_list_known_001",
            "sales_brief_known_001",
            "esg_report_known_001",
            "external_guarantee_situation_brief_known_001",
            "audit_report_known_001",
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
            "independent_director_annual_report_work_system_known_001",
            "independent_director_annual_report_work_system_known_002",
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
