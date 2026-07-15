"""
B-FM-49：公司章程修订公告 known_004 / 员工持股计划调价 known_003 晋升锁测（离线）。

覆盖：
- company_articles_known_004 已为 ready（BD2E736 修订公告）
- employee_stock_ownership_plan_known_003 已为 ready（BD2E800 购买价格调整）
- title_pattern 与 articles known_001–003 / ESOP known_001–002 可区分
- harvest 标题经既有路由预测正确（均 → announcement）
- 既有 LIVE_PASS 路径不回退（含 B-FM-48 articles/board）
- 本包不改路由；不重开已 LIVE_PASS 案；拒绝 audit 年报陷阱

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_articles_esop_known_003_004_promotion.py
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

HARVEST_ARTICLES_004 = "关于修订《公司章程》的公告"
HARVEST_ARTICLES_001 = "安徽古麒绒材股份有限公司章程（2025年6月修订）"
HARVEST_ARTICLES_002 = "江苏秀强玻璃工艺股份有限公司章程（2025年6月修订）"
HARVEST_ARTICLES_003 = "【通程控股】公司章程"
HARVEST_ARTICLES_BIZ = "关于变更公司注册资本、修订《公司章程》完成工商变更登记的公告"
HARVEST_ESOP_003 = "快克智能关于调整公司2025年员工持股计划购买价格的公告"
HARVEST_ESOP_001 = "第二期员工持股计划（草案）(修订稿）"
HARVEST_ESOP_002 = "2025年员工持股计划第一次持有人会议决议公告"
HARVEST_BOARD_002 = "第三届董事会第四次会议决议公告"
PATTERN_ARTICLES_004 = "关于修订《公司章程》的公告"
PATTERN_ARTICLES_001 = "公司章程（2025年6月修订）"
PATTERN_ARTICLES_002 = "秀强玻璃工艺股份有限公司章程（2025年6月修订）"
PATTERN_ARTICLES_003 = "【通程控股】公司章程"
PATTERN_ESOP_003 = "员工持股计划购买价格"
PATTERN_ESOP_001 = "第二期员工持股计划（草案）(修订稿）"
PATTERN_ESOP_002 = "员工持股计划第一次持有人会议决议"
SM_RES = "2025年第二次临时股东大会决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestArticlesEsopKnown003004Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_company_articles_known_004_ready_fields(self) -> None:
        c = _by_id(self.known, "company_articles_known_004")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "301577")
        self.assertEqual(c["company_name"], "美信科技")
        self.assertEqual(c["title_pattern"], PATTERN_ARTICLES_004)
        self.assertEqual(c["date_start"], "2025-06-18")
        self.assertEqual(c["date_end"], "2025-06-21")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_ARTICLES_004, HARVEST_ARTICLES_004)
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_003)
        self.assertNotEqual(c["title_pattern"], "章程")
        self.assertTrue(retrieval._title_matches(HARVEST_ARTICLES_004, PATTERN_ARTICLES_004))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_001, PATTERN_ARTICLES_004))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_002, PATTERN_ARTICLES_004))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_003, PATTERN_ARTICLES_004))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_BIZ, PATTERN_ARTICLES_004))

    def test_employee_stock_ownership_plan_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "employee_stock_ownership_plan_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "603203")
        self.assertEqual(c["company_name"], "快克智能")
        self.assertEqual(c["title_pattern"], PATTERN_ESOP_003)
        self.assertEqual(c["date_start"], "2025-06-23")
        self.assertEqual(c["date_end"], "2025-06-26")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_ESOP_003, HARVEST_ESOP_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_ESOP_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_ESOP_002)
        self.assertNotEqual(c["title_pattern"], "员工持股计划")
        self.assertTrue(retrieval._title_matches(HARVEST_ESOP_003, PATTERN_ESOP_003))
        self.assertFalse(retrieval._title_matches(HARVEST_ESOP_001, PATTERN_ESOP_003))
        self.assertFalse(retrieval._title_matches(HARVEST_ESOP_002, PATTERN_ESOP_003))

    def test_patterns_mutually_distinct(self) -> None:
        self.assertNotEqual(PATTERN_ARTICLES_004, PATTERN_ARTICLES_001)
        self.assertNotEqual(PATTERN_ARTICLES_004, PATTERN_ARTICLES_003)
        self.assertNotEqual(PATTERN_ESOP_003, PATTERN_ESOP_001)
        self.assertNotEqual(PATTERN_ESOP_003, PATTERN_ESOP_002)
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_004, PATTERN_ESOP_003))
        self.assertFalse(retrieval._title_matches(HARVEST_ESOP_003, PATTERN_ARTICLES_004))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_004, PATTERN_ARTICLES_003))

    def test_harvest_titles_route_correctly(self) -> None:
        r_art = routing.route_title(HARVEST_ARTICLES_004, self.config)
        self.assertEqual(r_art.predicted_document_type, "announcement")
        self.assertNotEqual(r_art.predicted_document_type, "other")
        self.assertNotEqual(r_art.predicted_document_type, "annual_report")
        self.assertEqual(r_art.predicted_route_to, "cninfo_general_announcement_pdf")
        r_esop = routing.route_title(HARVEST_ESOP_003, self.config)
        self.assertEqual(r_esop.predicted_document_type, "announcement")
        self.assertEqual(r_esop.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_prior_paths_not_regressed(self) -> None:
        for title in (
            HARVEST_ARTICLES_001,
            HARVEST_ARTICLES_002,
            HARVEST_ARTICLES_003,
            HARVEST_ESOP_001,
            HARVEST_ESOP_002,
            HARVEST_BOARD_002,
        ):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertNotEqual(r.predicted_document_type, "other")
                if title == HARVEST_BOARD_002:
                    self.assertEqual(r.predicted_document_type, "board_resolution")
                else:
                    self.assertEqual(r.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        # 拒绝 audit_report_known_002 年报陷阱仍落 periodic
        r_trap = routing.route_title("天健审〔2025〕11-195号 川网传媒2024年报审计报告", self.config)
        self.assertEqual(r_trap.predicted_document_type, "annual_report")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        for case_id in (
            "company_articles_known_001",
            "company_articles_known_002",
            "company_articles_known_003",
            "board_resolution_known_002",
            "employee_stock_ownership_plan_known_001",
            "employee_stock_ownership_plan_known_002",
            "listing_sponsor_known_001",
            "asset_valuation_explanation_known_001",
            "independent_director_meeting_review_known_001",
            "continuous_supervision_training_known_001",
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
            "company_articles_known_004",
            "employee_stock_ownership_plan_known_003",
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
