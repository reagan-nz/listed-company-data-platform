"""
B-FM-51：监事会决议 known_004 / 董事会决议 known_003 晋升锁测（离线）。

覆盖：
- supervisory_board_known_004 已为 ready（BD2E778 届次监事会）
- board_resolution_known_003 已为 ready（BD2E668 届次董事会）
- title_pattern 与 supervisory known_001–003、board known_001/002 可区分
- harvest 标题经既有路由预测正确（监事会 → announcement；董事会 → board_resolution）
- 既有 LIVE_PASS 路径不回退（含 B-FM-50 supervisory/articles）
- 本包不改路由；不重开已 LIVE_PASS 案；拒绝 audit 年报陷阱

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_supervisory_board_known_003_004_promotion.py
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

HARVEST_SB_004 = "海汽集团第四届监事会第三十次会议决议公告"
HARVEST_SB_003 = "第四届监事会第五次会议决议公告"
HARVEST_SB_001 = "第六届监事会第二十四次会议决议公告"
HARVEST_SB_002 = "农心作物科技股份有限公司第二届监事会第二十二次会议决议的公告"
HARVEST_SB_ANNUAL = "监事会关于公司2024年年度报告的审核意见"
HARVEST_BOARD_003 = "第五届董事会第五次会议决议公告"
HARVEST_BOARD_002 = "第三届董事会第四次会议决议公告"
HARVEST_BOARD_001 = "董事会决议公告"
HARVEST_ARTICLES_005 = "关于变更公司注册资本、修订《公司章程》完成工商变更登记的公告"
PATTERN_SB_004 = "第四届监事会第三十次会议决议公告"
PATTERN_SB_003 = "第四届监事会第五次会议决议公告"
PATTERN_SB_001 = "第二十四次会议决议公告"
PATTERN_SB_002 = "第二十二次会议决议的公告"
PATTERN_BOARD_003 = "第五届董事会第五次会议决议公告"
PATTERN_BOARD_002 = "第三届董事会第四次会议决议公告"
PATTERN_BOARD_001 = "董事会决议公告"
SM_RES = "2025年第二次临时股东大会决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestSupervisoryBoardKnown003004Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_supervisory_board_known_004_ready_fields(self) -> None:
        c = _by_id(self.known, "supervisory_board_known_004")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "603069")
        self.assertEqual(c["company_name"], "海汽集团")
        self.assertEqual(c["title_pattern"], PATTERN_SB_004)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_SB_004, HARVEST_SB_004)
        self.assertNotEqual(c["title_pattern"], PATTERN_SB_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_SB_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_SB_003)
        self.assertNotEqual(c["title_pattern"], "监事会")
        self.assertTrue(retrieval._title_matches(HARVEST_SB_004, PATTERN_SB_004))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_003, PATTERN_SB_004))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_001, PATTERN_SB_004))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_002, PATTERN_SB_004))
        self.assertFalse(retrieval._title_matches(HARVEST_BOARD_003, PATTERN_SB_004))
        # known_003 pattern 亦不误抬海汽案
        self.assertFalse(retrieval._title_matches(HARVEST_SB_004, PATTERN_SB_003))

    def test_board_resolution_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "board_resolution_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "301027")
        self.assertEqual(c["company_name"], "华蓝集团")
        self.assertEqual(c["title_pattern"], PATTERN_BOARD_003)
        self.assertEqual(c["date_start"], "2025-06-29")
        self.assertEqual(c["date_end"], "2025-07-02")
        self.assertEqual(c["expected_document_type"], "board_resolution")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_BOARD_003, HARVEST_BOARD_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_BOARD_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_BOARD_002)
        self.assertNotEqual(c["title_pattern"], "决议公告")
        self.assertTrue(retrieval._title_matches(HARVEST_BOARD_003, PATTERN_BOARD_003))
        self.assertFalse(retrieval._title_matches(HARVEST_BOARD_002, PATTERN_BOARD_003))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_004, PATTERN_BOARD_003))
        # known_002 仍不误抬华蓝案
        self.assertFalse(retrieval._title_matches(HARVEST_BOARD_003, PATTERN_BOARD_002))

    def test_patterns_mutually_distinct(self) -> None:
        self.assertNotEqual(PATTERN_SB_004, PATTERN_SB_003)
        self.assertNotEqual(PATTERN_SB_004, PATTERN_SB_001)
        self.assertNotEqual(PATTERN_SB_004, PATTERN_SB_002)
        self.assertNotEqual(PATTERN_BOARD_003, PATTERN_BOARD_002)
        self.assertNotEqual(PATTERN_BOARD_003, PATTERN_BOARD_001)
        self.assertFalse(retrieval._title_matches(HARVEST_SB_004, PATTERN_BOARD_003))
        self.assertFalse(retrieval._title_matches(HARVEST_BOARD_003, PATTERN_SB_004))

    def test_harvest_titles_route_correctly(self) -> None:
        r_sb = routing.route_title(HARVEST_SB_004, self.config)
        self.assertEqual(r_sb.predicted_document_type, "announcement")
        self.assertNotEqual(r_sb.predicted_document_type, "other")
        self.assertNotEqual(r_sb.predicted_document_type, "board_resolution")
        self.assertNotEqual(r_sb.predicted_document_type, "annual_report")
        self.assertEqual(r_sb.predicted_route_to, "cninfo_general_announcement_pdf")
        r_board = routing.route_title(HARVEST_BOARD_003, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        self.assertEqual(r_board.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_prior_paths_not_regressed(self) -> None:
        for title, expected in (
            (HARVEST_SB_001, "announcement"),
            (HARVEST_SB_002, "announcement"),
            (HARVEST_SB_003, "announcement"),
            (HARVEST_ARTICLES_005, "announcement"),
            (HARVEST_BOARD_002, "board_resolution"),
            (HARVEST_BOARD_001, "board_resolution"),
        ):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, expected)
                self.assertNotEqual(r.predicted_document_type, "other")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_sb_annual = routing.route_title(HARVEST_SB_ANNUAL, self.config)
        self.assertEqual(r_sb_annual.predicted_document_type, "annual_report")
        r_trap = routing.route_title("天健审〔2025〕11-195号 川网传媒2024年报审计报告", self.config)
        self.assertEqual(r_trap.predicted_document_type, "annual_report")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        for case_id in (
            "supervisory_board_known_001",
            "supervisory_board_known_002",
            "supervisory_board_known_003",
            "board_resolution_known_001",
            "board_resolution_known_002",
            "company_articles_known_005",
            "employee_stock_ownership_plan_known_003",
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
            "supervisory_board_known_004",
            "board_resolution_known_003",
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
