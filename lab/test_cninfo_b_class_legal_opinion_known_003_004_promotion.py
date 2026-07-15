"""
B-FM-26：非会议类法律意见书 known-document 晋升锁测（离线）。

覆盖：
- legal_opinion_known_003（增持法律意见书）与 known_004（差异化分红法律意见书）已为 ready
- title_pattern 与会议法律意见 known_001/002 / 股东会决议 / 监事会可区分
- harvest 标题经 B-FM-26 路由预测 announcement → general（非 other）
- 会议法律意见 / 股东会决议 / 董事会路径不回退
- 不重开 legal_opinion_known_001–002 / supervisory_board / shareholder_meeting LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_legal_opinion_known_003_004_promotion.py
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

# harvest 证据标题（只读引用；BD2E079 / BD2E442）
HARVEST_003 = (
    "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书"
)
HARVEST_004 = (
    "北京市通商律师事务所上海分所关于东浩兰生会展集团股份有限公司"
    "差异化分红的法律意见书"
)
PATTERN_003 = "增持公司股份之法律意见书"
PATTERN_004 = "差异化分红的法律意见书"
PATTERN_001 = "第一次临时股东大会的法律意见书"
PATTERN_002 = "年度股东会的法律意见书"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
MEETING_LEGAL = "2025年第一次临时股东大会的法律意见书"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestLegalOpinionKnown003004Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_legal_opinion_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "legal_opinion_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000703")
        self.assertEqual(c["company_name"], "恒逸石化")
        self.assertEqual(c["title_pattern"], PATTERN_003)
        self.assertEqual(c["date_start"], "2025-06-23")
        self.assertEqual(c["date_end"], "2025-06-26")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_003, HARVEST_003)
        self.assertIn("增持", c["title_pattern"])
        self.assertIn("法律意见书", c["title_pattern"])
        self.assertNotIn("股东大会", c["title_pattern"])
        self.assertNotIn("股东会", c["title_pattern"])

    def test_legal_opinion_known_004_ready_fields(self) -> None:
        c = _by_id(self.known, "legal_opinion_known_004")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "600826")
        self.assertEqual(c["company_name"], "兰生股份")
        self.assertEqual(c["title_pattern"], PATTERN_004)
        self.assertEqual(c["date_start"], "2025-06-16")
        self.assertEqual(c["date_end"], "2025-06-19")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_004, HARVEST_004)
        self.assertIn("差异化分红", c["title_pattern"])
        self.assertIn("法律意见书", c["title_pattern"])
        self.assertNotIn("增持", c["title_pattern"])

    def test_title_patterns_mutually_exclusive(self) -> None:
        """非会议 pattern 与会议法律意见 / 股东会决议互斥。"""
        self.assertTrue(retrieval._title_matches(HARVEST_003, PATTERN_003))
        self.assertTrue(retrieval._title_matches(HARVEST_004, PATTERN_004))
        self.assertFalse(retrieval._title_matches(HARVEST_003, PATTERN_004))
        self.assertFalse(retrieval._title_matches(HARVEST_004, PATTERN_003))
        for title in (MEETING_LEGAL, SM_RES, BOARD):
            self.assertFalse(retrieval._title_matches(title, PATTERN_003), title)
            self.assertFalse(retrieval._title_matches(title, PATTERN_004), title)
        self.assertFalse(retrieval._title_matches(HARVEST_003, PATTERN_001))
        self.assertFalse(retrieval._title_matches(HARVEST_003, PATTERN_002))

    def test_closed_anchors_untouched(self) -> None:
        """不削弱已 LIVE_PASS / 既有 ready 锚点字段。"""
        for case_id, pattern in (
            ("legal_opinion_known_001", PATTERN_001),
            ("legal_opinion_known_002", PATTERN_002),
            ("supervisory_board_known_001", "第二十四次会议决议公告"),
            ("supervisory_board_known_002", "第二十二次会议决议的公告"),
            ("shareholder_meeting_known_007", "年度股东会决议"),
        ):
            c = _by_id(self.known, case_id)
            self.assertEqual(c["case_status"], "ready", case_id)
            self.assertEqual(c["title_pattern"], pattern, case_id)

    def test_harvest_titles_route_announcement_not_other(self) -> None:
        for title in (HARVEST_003, HARVEST_004):
            r = routing.route_title(title, self.config)
            self.assertEqual(r.predicted_document_type, "announcement", title)
            self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf", title)
            self.assertEqual(r.predicted_classification, "general_announcement", title)
            self.assertNotEqual(r.predicted_document_type, "other", title)
            self.assertNotEqual(r.predicted_document_type, "shareholder_meeting_material", title)

    def test_meeting_legal_and_resolution_routes_untouched(self) -> None:
        """会议法律意见仍为 announcement；股东会决议 / 董事会不回退。"""
        r_ml = routing.route_title(MEETING_LEGAL, self.config)
        self.assertEqual(r_ml.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_pair_distinct_from_meeting_legal(self) -> None:
        k3 = _by_id(self.known, "legal_opinion_known_003")
        k4 = _by_id(self.known, "legal_opinion_known_004")
        k1 = _by_id(self.known, "legal_opinion_known_001")
        self.assertNotEqual(k3["company_code"], k4["company_code"])
        self.assertNotEqual(k3["title_pattern"], k4["title_pattern"])
        self.assertNotEqual(k3["title_pattern"], k1["title_pattern"])
        self.assertEqual(k3["expected_document_type"], k1["expected_document_type"])


if __name__ == "__main__":
    unittest.main()
