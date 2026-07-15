"""
B-FM-48：公司章程 known_003 / 董事会决议 known_002 晋升锁测（离线）。

覆盖：
- company_articles_known_003 已为 ready（BD2E189 短标题）
- board_resolution_known_002 已为 ready（BD2E648 届次决议）
- title_pattern 与 known_001/002（章程）及 known_001（董事会）可区分
- harvest 标题经既有路由预测正确（章程→announcement；董事会→board_resolution）
- 既有 LIVE_PASS 路径不回退（含 B-FM-47 supervision/trustee known_003）
- 本包不改路由；不重开已 LIVE_PASS 案；拒绝 audit 年报陷阱

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_articles_board_known_002_003_promotion.py
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

HARVEST_ARTICLES_003 = "【通程控股】公司章程"
HARVEST_ARTICLES_001 = "安徽古麒绒材股份有限公司章程（2025年6月修订）"
HARVEST_ARTICLES_002 = "江苏秀强玻璃工艺股份有限公司章程（2025年6月修订）"
HARVEST_BOARD_002 = "第三届董事会第四次会议决议公告"
HARVEST_BOARD_001 = "董事会决议公告"
HARVEST_REVISION_ANN = "关于修订《公司章程》的公告"
HARVEST_SUP_003 = (
    "首创证券关于和邦生物向不特定对象发行可转换公司债券之2024年持续督导年度报告书"
)
HARVEST_BT_003 = (
    "中联重科股份有限公司2019年面向合格投资者公开发行公司债券（第一期）"
    "受托管理事务报告（2024年度）"
)
PATTERN_ARTICLES_003 = "【通程控股】公司章程"
PATTERN_ARTICLES_001 = "公司章程（2025年6月修订）"
PATTERN_ARTICLES_002 = "秀强玻璃工艺股份有限公司章程（2025年6月修订）"
PATTERN_BOARD_002 = "第三届董事会第四次会议决议公告"
PATTERN_BOARD_001 = "董事会决议公告"
SM_RES = "2025年第二次临时股东大会决议公告"
SUPERVISORY = "第六届监事会第二十四次会议决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestArticlesBoardKnown002003Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_company_articles_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "company_articles_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000419")
        self.assertEqual(c["company_name"], "通程控股")
        self.assertEqual(c["title_pattern"], PATTERN_ARTICLES_003)
        self.assertEqual(c["date_start"], "2025-06-19")
        self.assertEqual(c["date_end"], "2025-06-22")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_ARTICLES_003, HARVEST_ARTICLES_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_ARTICLES_002)
        self.assertNotEqual(c["title_pattern"], "章程")
        self.assertTrue(retrieval._title_matches(HARVEST_ARTICLES_003, PATTERN_ARTICLES_003))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_001, PATTERN_ARTICLES_003))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_002, PATTERN_ARTICLES_003))
        self.assertFalse(retrieval._title_matches(HARVEST_REVISION_ANN, PATTERN_ARTICLES_003))

    def test_board_resolution_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "board_resolution_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300930")
        self.assertEqual(c["company_name"], "屹通新材")
        self.assertEqual(c["title_pattern"], PATTERN_BOARD_002)
        self.assertEqual(c["date_start"], "2025-06-19")
        self.assertEqual(c["date_end"], "2025-06-22")
        self.assertEqual(c["expected_document_type"], "board_resolution")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_BOARD_002, HARVEST_BOARD_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_BOARD_001)
        self.assertTrue(retrieval._title_matches(HARVEST_BOARD_002, PATTERN_BOARD_002))
        self.assertFalse(retrieval._title_matches(HARVEST_BOARD_001, PATTERN_BOARD_002))
        # 届次标题在「董事会」与「决议公告」之间插入次数，宽串不连续命中（互斥更强）
        self.assertFalse(retrieval._title_matches(HARVEST_BOARD_002, PATTERN_BOARD_001))

    def test_patterns_mutually_distinct(self) -> None:
        self.assertNotEqual(PATTERN_ARTICLES_003, PATTERN_ARTICLES_001)
        self.assertNotEqual(PATTERN_ARTICLES_003, PATTERN_ARTICLES_002)
        self.assertNotEqual(PATTERN_BOARD_002, PATTERN_BOARD_001)
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_003, PATTERN_BOARD_002))
        self.assertFalse(retrieval._title_matches(HARVEST_BOARD_002, PATTERN_ARTICLES_003))
        self.assertFalse(retrieval._title_matches(HARVEST_ARTICLES_003, PATTERN_ARTICLES_001))

    def test_harvest_titles_route_correctly(self) -> None:
        r_art = routing.route_title(HARVEST_ARTICLES_003, self.config)
        self.assertEqual(r_art.predicted_document_type, "announcement")
        self.assertNotEqual(r_art.predicted_document_type, "other")
        self.assertNotEqual(r_art.predicted_document_type, "annual_report")
        self.assertEqual(r_art.predicted_route_to, "cninfo_general_announcement_pdf")
        r_board = routing.route_title(HARVEST_BOARD_002, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        self.assertEqual(r_board.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_prior_paths_not_regressed(self) -> None:
        for title in (HARVEST_ARTICLES_001, HARVEST_ARTICLES_002, HARVEST_SUP_003, HARVEST_BT_003):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
        r_board001 = routing.route_title(HARVEST_BOARD_001, self.config)
        self.assertEqual(r_board001.predicted_document_type, "board_resolution")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_sup = routing.route_title(SUPERVISORY, self.config)
        self.assertEqual(r_sup.predicted_document_type, "announcement")
        # 拒绝 audit_report_known_002 年报陷阱仍落 periodic
        r_trap = routing.route_title("天健审〔2025〕11-195号 川网传媒2024年报审计报告", self.config)
        self.assertEqual(r_trap.predicted_document_type, "annual_report")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        for case_id in (
            "company_articles_known_001",
            "company_articles_known_002",
            "board_resolution_known_001",
            "continuous_supervision_annual_known_003",
            "bond_trustee_report_known_003",
            "tracking_rating_report_known_003",
            "employee_stock_ownership_plan_known_002",
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
            "company_articles_known_003",
            "board_resolution_known_002",
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
