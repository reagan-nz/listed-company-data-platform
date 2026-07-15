"""
B-FM-50：监事会决议 known_003 / 公司章程工商变更修订 known_005 晋升锁测（离线）。

覆盖：
- supervisory_board_known_003 已为 ready（BD2E702 届次监事会）
- company_articles_known_005 已为 ready（BD2E674 工商变更+修订章程）
- title_pattern 与 supervisory known_001/002、articles known_001–004 可区分
- harvest 标题经既有路由预测正确（均 → announcement）
- 既有 LIVE_PASS 路径不回退（含 B-FM-49 articles/ESOP）
- 本包不改路由；不重开已 LIVE_PASS 案；拒绝 audit 年报陷阱

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_supervisory_articles_known_003_005_promotion.py
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

HARVEST_SB_003 = "第四届监事会第五次会议决议公告"
HARVEST_SB_001 = "第六届监事会第二十四次会议决议公告"
HARVEST_SB_002 = "农心作物科技股份有限公司第二届监事会第二十二次会议决议的公告"
HARVEST_SB_778 = "海汽集团第四届监事会第三十次会议决议公告"
HARVEST_SB_ANNUAL = "监事会关于公司2024年年度报告的审核意见"
HARVEST_ARTICLES_005 = "关于变更公司注册资本、修订《公司章程》完成工商变更登记的公告"
HARVEST_ARTICLES_004 = "关于修订《公司章程》的公告"
HARVEST_ARTICLES_001 = "安徽古麒绒材股份有限公司章程（2025年6月修订）"
HARVEST_ARTICLES_002 = "江苏秀强玻璃工艺股份有限公司章程（2025年6月修订）"
HARVEST_ARTICLES_003 = "【通程控股】公司章程"
HARVEST_ARTICLES_BIZ_ONLY = "关于完成工商变更登记并换发营业执照的公告"
HARVEST_ESOP_003 = "快克智能关于调整公司2025年员工持股计划购买价格的公告"
HARVEST_BOARD_002 = "第三届董事会第四次会议决议公告"
PATTERN_SB_003 = "第四届监事会第五次会议决议公告"
PATTERN_SB_001 = "第二十四次会议决议公告"
PATTERN_SB_002 = "第二十二次会议决议的公告"
PATTERN_ARTICLES_005 = "修订《公司章程》完成工商变更登记"
PATTERN_ARTICLES_004 = "关于修订《公司章程》的公告"
PATTERN_ARTICLES_001 = "公司章程（2025年6月修订）"
PATTERN_ARTICLES_002 = "秀强玻璃工艺股份有限公司章程（2025年6月修订）"
PATTERN_ARTICLES_003 = "【通程控股】公司章程"
SM_RES = "2025年第二次临时股东大会决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestSupervisoryArticlesKnown003005Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_supervisory_board_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "supervisory_board_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "301265")
        self.assertEqual(c["company_name"], "华新科技")
        self.assertEqual(c["title_pattern"], PATTERN_SB_003)
        self.assertEqual(c["date_start"], "2025-06-22")
        self.assertEqual(c["date_end"], "2025-06-25")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_SB_003, HARVEST_SB_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_SB_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_SB_002)
        self.assertNotEqual(c["title_pattern"], "监事会")
        self.assertTrue(retrieval._title_matches(HARVEST_SB_003, PATTERN_SB_003))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_001, PATTERN_SB_003))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_002, PATTERN_SB_003))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_778, PATTERN_SB_003))
        self.assertFalse(retrieval._title_matches(HARVEST_BOARD_002, PATTERN_SB_003))

    def test_company_articles_known_005_ready_fields(self) -> None:
        c = _by_id(self.known, "company_articles_known_005")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "301068")
        self.assertEqual(c["company_name"], "大地海洋")
        self.assertEqual(c["title_pattern"], PATTERN_ARTICLES_005)
        self.assertEqual(c["date_start"], "2025-06-10")
        self.assertEqual(c["date_end"], "2025-06-13")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_ARTICLES_005, HARVEST_ARTICLES_005)
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_004)
        self.assertNotEqual(c["title_pattern"], "章程")
        self.assertNotEqual(c["title_pattern"], "工商变更")
        self.assertTrue(retrieval._title_matches(HARVEST_ARTICLES_005, PATTERN_ARTICLES_005))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_004, PATTERN_ARTICLES_005))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_001, PATTERN_ARTICLES_005))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_002, PATTERN_ARTICLES_005))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_003, PATTERN_ARTICLES_005))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_BIZ_ONLY, PATTERN_ARTICLES_005))
        # known_004 仍不误抬工商变更标题
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_005, PATTERN_ARTICLES_004))

    def test_patterns_mutually_distinct(self) -> None:
        self.assertNotEqual(PATTERN_SB_003, PATTERN_SB_001)
        self.assertNotEqual(PATTERN_SB_003, PATTERN_SB_002)
        self.assertNotEqual(PATTERN_ARTICLES_005, PATTERN_ARTICLES_004)
        self.assertFalse(retrieval._title_matches(HARVEST_SB_003, PATTERN_ARTICLES_005))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_005, PATTERN_SB_003))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_004, PATTERN_ARTICLES_005))

    def test_harvest_titles_route_correctly(self) -> None:
        r_sb = routing.route_title(HARVEST_SB_003, self.config)
        self.assertEqual(r_sb.predicted_document_type, "announcement")
        self.assertNotEqual(r_sb.predicted_document_type, "other")
        self.assertNotEqual(r_sb.predicted_document_type, "board_resolution")
        self.assertNotEqual(r_sb.predicted_document_type, "annual_report")
        self.assertEqual(r_sb.predicted_route_to, "cninfo_general_announcement_pdf")
        r_art = routing.route_title(HARVEST_ARTICLES_005, self.config)
        self.assertEqual(r_art.predicted_document_type, "announcement")
        self.assertEqual(r_art.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_prior_paths_not_regressed(self) -> None:
        for title in (
            HARVEST_SB_001,
            HARVEST_SB_002,
            HARVEST_ARTICLES_001,
            HARVEST_ARTICLES_002,
            HARVEST_ARTICLES_003,
            HARVEST_ARTICLES_004,
            HARVEST_ESOP_003,
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
        # 监事会年报审核意见仍落 periodic；audit 年报陷阱仍落 periodic
        r_sb_annual = routing.route_title(HARVEST_SB_ANNUAL, self.config)
        self.assertEqual(r_sb_annual.predicted_document_type, "annual_report")
        r_trap = routing.route_title("天健审〔2025〕11-195号 川网传媒2024年报审计报告", self.config)
        self.assertEqual(r_trap.predicted_document_type, "annual_report")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        for case_id in (
            "supervisory_board_known_001",
            "supervisory_board_known_002",
            "company_articles_known_001",
            "company_articles_known_002",
            "company_articles_known_003",
            "company_articles_known_004",
            "employee_stock_ownership_plan_known_003",
            "board_resolution_known_002",
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
            "supervisory_board_known_003",
            "company_articles_known_005",
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
