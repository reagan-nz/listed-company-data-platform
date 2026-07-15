"""
B-FM-22：「年度股东会决议」简称 known-document 晋升锁测（离线）。

覆盖：
- shareholder_meeting_known_007（年度股东会决议）已为 ready
- title_pattern 与 known_001–006 / meeting_sample_002 可区分
- harvest 标题经 B-FM-20 路由预测 shareholder_meeting_material → general
- 法律意见书 / 会议材料 / 董事会决议 / 说明会路径不回退
- 不重开 known_001–006 字段

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_shareholder_meeting_known_007_promotion.py
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

# harvest 证据标题（只读引用；BD2E258）
SHORT_ANNUAL = "2024年年度股东会决议公告"
SHORT_TEMP = "2025年第五次临时股东会决议公告"
PATTERN_ANNUAL = "年度股东会决议"
PATTERN_SHORT_RES = "临时股东会决议"
PATTERN_SHORT_NOTICE = "股东会的通知"
PATTERN_FULL_RES = "股东大会决议"
PATTERN_FULL_CONV = "股东大会的公告"
PATTERN_CONTIG = "股东大会通知"
PATTERN_DE = "股东大会的通知"
KNOWN_001_TITLE = "关于召开2025年度第二次临时股东大会通知的公告"
KNOWN_002_TITLE = "关于召开2025年第三次临时股东大会的通知"
KNOWN_003_TITLE = "2025年第二次临时股东大会决议公告"
KNOWN_004_TITLE = "关于召开2025年第二次临时股东大会的公告"
KNOWN_005_TITLE = SHORT_TEMP
KNOWN_006_TITLE = "关于召开2025年第二次临时股东会的通知"
BRIEFING = "关于召开重大资产重组事项投资者说明会的公告"
LEGAL = "关于2025年第二次临时股东大会的法律意见书"
MATERIALS = "2025年第二次临时股东大会会议材料"
BOARD = "第七届董事会第十一次会议决议公告"
SHORT_LEGAL = "关于2024年年度股东会的法律意见书"
SHORT_MATERIALS = "2025年第五次临时股东会会议资料"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestShareholderMeetingKnown007Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)
        cls.category = _load_cases(CATEGORY_YAML)

    def test_shareholder_meeting_known_007_ready_fields(self) -> None:
        c = _by_id(self.known, "shareholder_meeting_known_007")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "001335")
        self.assertEqual(c["company_name"], "信凯科技")
        self.assertEqual(c["title_pattern"], PATTERN_ANNUAL)
        self.assertEqual(c["date_start"], "2025-06-24")
        self.assertEqual(c["date_end"], "2025-06-27")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "shareholder_meeting_material")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_ANNUAL, SHORT_ANNUAL)
        self.assertNotIn("股东大会", c["title_pattern"])
        self.assertNotIn("临时", c["title_pattern"])
        self.assertNotIn("说明会", c["title_pattern"])

    def test_title_patterns_mutually_exclusive(self) -> None:
        """年度简称决议与临时简称 / 完整 pattern / 通知类互不误命中。"""
        self.assertTrue(retrieval._title_matches(SHORT_ANNUAL, PATTERN_ANNUAL))
        self.assertFalse(retrieval._title_matches(SHORT_ANNUAL, PATTERN_SHORT_RES))
        self.assertFalse(retrieval._title_matches(SHORT_ANNUAL, PATTERN_SHORT_NOTICE))
        self.assertFalse(retrieval._title_matches(SHORT_ANNUAL, PATTERN_FULL_RES))
        self.assertFalse(retrieval._title_matches(SHORT_ANNUAL, PATTERN_FULL_CONV))
        self.assertFalse(retrieval._title_matches(SHORT_ANNUAL, PATTERN_CONTIG))
        self.assertFalse(retrieval._title_matches(SHORT_ANNUAL, PATTERN_DE))

        # known_005 临时简称不得命中年度 pattern
        self.assertFalse(retrieval._title_matches(KNOWN_005_TITLE, PATTERN_ANNUAL))
        self.assertTrue(retrieval._title_matches(KNOWN_005_TITLE, PATTERN_SHORT_RES))

        # 完整「股东大会决议」不得命中简称年度 pattern
        self.assertFalse(retrieval._title_matches(KNOWN_003_TITLE, PATTERN_ANNUAL))
        self.assertTrue(retrieval._title_matches(KNOWN_003_TITLE, PATTERN_FULL_RES))

        # 通知类 / 召开公告不得命中
        self.assertFalse(retrieval._title_matches(KNOWN_006_TITLE, PATTERN_ANNUAL))
        self.assertFalse(retrieval._title_matches(KNOWN_002_TITLE, PATTERN_ANNUAL))
        self.assertFalse(retrieval._title_matches(KNOWN_001_TITLE, PATTERN_ANNUAL))
        self.assertFalse(retrieval._title_matches(KNOWN_004_TITLE, PATTERN_ANNUAL))

    def test_prior_shareholder_meeting_anchors_untouched(self) -> None:
        """新晋 known_007 不削弱既有股东会锚点（含已 LIVE_PASS 的 001–006）。"""
        expect = {
            "shareholder_meeting_known_001": ("300446", PATTERN_CONTIG),
            "shareholder_meeting_known_002": ("002237", PATTERN_DE),
            "shareholder_meeting_known_003": ("300463", PATTERN_FULL_RES),
            "shareholder_meeting_known_004": ("000708", PATTERN_FULL_CONV),
            "shareholder_meeting_known_005": ("300907", PATTERN_SHORT_RES),
            "shareholder_meeting_known_006": ("002083", PATTERN_SHORT_NOTICE),
        }
        for case_id, (code, pattern) in expect.items():
            c = _by_id(self.known, case_id)
            self.assertEqual(c["case_status"], "ready", case_id)
            self.assertEqual(c["company_code"], code, case_id)
            self.assertEqual(c["title_pattern"], pattern, case_id)
        s2 = _by_id(self.category, "meeting_sample_002")
        self.assertEqual(s2["case_status"], "ready")
        self.assertEqual(s2["title_pattern"], PATTERN_CONTIG)

    def test_harvest_title_routes_general_not_meeting_notice(self) -> None:
        r = routing.route_title(SHORT_ANNUAL, self.config)
        self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.predicted_classification, "general_announcement")
        self.assertNotEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_exclusions_and_board_resolution_untouched(self) -> None:
        """法律意见书 / 会议材料仍为 announcement；董事会决议仍为 board_resolution。"""
        for title in (LEGAL, MATERIALS, SHORT_LEGAL, SHORT_MATERIALS):
            r = routing.route_title(title, self.config)
            self.assertEqual(r.predicted_document_type, "announcement", title)
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        r_brief = routing.route_title(BRIEFING, self.config)
        self.assertEqual(r_brief.predicted_document_type, "meeting_notice")
        self.assertEqual(r_brief.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_distinct_company_and_pattern_matrix(self) -> None:
        """七档 known 公司与 pattern 两两可区分。"""
        ids = [
            "shareholder_meeting_known_001",
            "shareholder_meeting_known_002",
            "shareholder_meeting_known_003",
            "shareholder_meeting_known_004",
            "shareholder_meeting_known_005",
            "shareholder_meeting_known_006",
            "shareholder_meeting_known_007",
        ]
        cases = [_by_id(self.known, i) for i in ids]
        codes = {c["company_code"] for c in cases}
        patterns = {c["title_pattern"] for c in cases}
        self.assertEqual(len(codes), 7)
        self.assertEqual(len(patterns), 7)
        for c in cases:
            self.assertEqual(c["expected_document_type"], "shareholder_meeting_material")
            self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")


if __name__ == "__main__":
    unittest.main()
