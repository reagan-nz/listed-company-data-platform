"""
B-FM-19：股东大会决议 / 召开公告 known-document 晋升锁测（离线）。

覆盖：
- shareholder_meeting_known_003（决议）与 known_004（召开…的公告无通知）已为 ready
- title_pattern 与 known_001/002 / meeting_sample_002 可区分
- harvest 标题经 B-FM-18 路由预测 shareholder_meeting_material → general
- 法律意见书 / 会议材料 / 董事会决议 / 说明会路径不回退

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_shareholder_meeting_known_003_004_promotion.py
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
CATEGORY_YAML = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "category_sample_cases.yaml"
)

# harvest 证据标题（只读引用；BD2E578 / BD2E080）
RESOLUTION = "2025年第二次临时股东大会决议公告"
CONVENING = "关于召开2025年第二次临时股东大会的公告"
PATTERN_RES = "股东大会决议"
PATTERN_CONV = "股东大会的公告"
PATTERN_CONTIG = "股东大会通知"
PATTERN_DE = "股东大会的通知"
KNOWN_001_TITLE = "关于召开2025年度第二次临时股东大会通知的公告"
KNOWN_002_TITLE = "关于召开2025年第三次临时股东大会的通知"
BRIEFING = "关于召开重大资产重组事项投资者说明会的公告"
LEGAL = "关于2025年第二次临时股东大会的法律意见书"
MATERIALS = "2025年第二次临时股东大会会议材料"
BOARD = "第七届董事会第十一次会议决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestShareholderMeetingKnown003004Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)
        cls.category = _load_cases(CATEGORY_YAML)

    def test_shareholder_meeting_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "shareholder_meeting_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300463")
        self.assertEqual(c["company_name"], "迈克生物")
        self.assertEqual(c["title_pattern"], PATTERN_RES)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "shareholder_meeting_material")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_RES, RESOLUTION)
        self.assertNotIn("通知", c["title_pattern"])
        self.assertNotIn("说明会", c["title_pattern"])

    def test_shareholder_meeting_known_004_ready_fields(self) -> None:
        c = _by_id(self.known, "shareholder_meeting_known_004")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000708")
        self.assertEqual(c["company_name"], "中信特钢")
        self.assertEqual(c["title_pattern"], PATTERN_CONV)
        self.assertEqual(c["date_start"], "2025-06-25")
        self.assertEqual(c["date_end"], "2025-06-28")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "shareholder_meeting_material")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_CONV, CONVENING)
        self.assertNotIn("通知", CONVENING)
        self.assertNotIn("通知", c["title_pattern"])
        self.assertNotIn("说明会", c["title_pattern"])

    def test_title_patterns_mutually_exclusive(self) -> None:
        """决议 / 召开公告 / 通知类 pattern 互不误命中对方 harvest 标题。"""
        self.assertTrue(retrieval._title_matches(RESOLUTION, PATTERN_RES))
        self.assertFalse(retrieval._title_matches(RESOLUTION, PATTERN_CONV))
        self.assertFalse(retrieval._title_matches(RESOLUTION, PATTERN_CONTIG))
        self.assertFalse(retrieval._title_matches(RESOLUTION, PATTERN_DE))

        self.assertTrue(retrieval._title_matches(CONVENING, PATTERN_CONV))
        self.assertFalse(retrieval._title_matches(CONVENING, PATTERN_RES))
        self.assertFalse(retrieval._title_matches(CONVENING, PATTERN_CONTIG))
        self.assertFalse(retrieval._title_matches(CONVENING, PATTERN_DE))

        self.assertFalse(retrieval._title_matches(KNOWN_001_TITLE, PATTERN_RES))
        self.assertFalse(retrieval._title_matches(KNOWN_001_TITLE, PATTERN_CONV))
        self.assertTrue(retrieval._title_matches(KNOWN_001_TITLE, PATTERN_CONTIG))

        self.assertFalse(retrieval._title_matches(KNOWN_002_TITLE, PATTERN_RES))
        self.assertFalse(retrieval._title_matches(KNOWN_002_TITLE, PATTERN_CONV))
        self.assertTrue(retrieval._title_matches(KNOWN_002_TITLE, PATTERN_DE))

    def test_prior_shareholder_meeting_anchors_untouched(self) -> None:
        """新晋 known_003/004 不削弱既有股东会锚点。"""
        k1 = _by_id(self.known, "shareholder_meeting_known_001")
        k2 = _by_id(self.known, "shareholder_meeting_known_002")
        s2 = _by_id(self.category, "meeting_sample_002")
        self.assertEqual(k1["case_status"], "ready")
        self.assertEqual(k1["title_pattern"], PATTERN_CONTIG)
        self.assertEqual(k1["company_code"], "300446")
        self.assertEqual(k2["case_status"], "ready")
        self.assertEqual(k2["title_pattern"], PATTERN_DE)
        self.assertEqual(k2["company_code"], "002237")
        self.assertEqual(s2["case_status"], "ready")
        self.assertEqual(s2["title_pattern"], PATTERN_CONTIG)

    def test_harvest_titles_route_general_not_meeting_notice(self) -> None:
        for title in (RESOLUTION, CONVENING):
            r = routing.route_title(title, self.config)
            self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
            self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
            self.assertEqual(r.predicted_classification, "general_announcement")
            self.assertNotEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_exclusions_and_board_resolution_untouched(self) -> None:
        """法律意见书 / 会议材料仍为 announcement；董事会决议仍为 board_resolution。"""
        r_legal = routing.route_title(LEGAL, self.config)
        self.assertEqual(r_legal.predicted_document_type, "announcement")
        r_mat = routing.route_title(MATERIALS, self.config)
        self.assertEqual(r_mat.predicted_document_type, "announcement")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        r_brief = routing.route_title(BRIEFING, self.config)
        self.assertEqual(r_brief.predicted_document_type, "meeting_notice")
        self.assertEqual(r_brief.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_distinct_company_and_pattern_matrix(self) -> None:
        """四档 known 公司与 pattern 两两可区分。"""
        k1 = _by_id(self.known, "shareholder_meeting_known_001")
        k2 = _by_id(self.known, "shareholder_meeting_known_002")
        k3 = _by_id(self.known, "shareholder_meeting_known_003")
        k4 = _by_id(self.known, "shareholder_meeting_known_004")
        codes = {k1["company_code"], k2["company_code"], k3["company_code"], k4["company_code"]}
        patterns = {
            k1["title_pattern"],
            k2["title_pattern"],
            k3["title_pattern"],
            k4["title_pattern"],
        }
        self.assertEqual(len(codes), 4)
        self.assertEqual(len(patterns), 4)
        for c in (k1, k2, k3, k4):
            self.assertEqual(c["expected_document_type"], "shareholder_meeting_material")
            self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")


if __name__ == "__main__":
    unittest.main()
