"""
B-FM-25：法律意见书 known-document 晋升锁测（离线）。

覆盖：
- legal_opinion_known_001（股东大会的法律意见书）与 known_002（股东会的法律意见书）已为 ready
- title_pattern 与股东会决议/通知族 / 监事会决议可区分
- harvest 标题经既有路由预测 announcement → general（非 shareholder_meeting_material）
- 股东会决议 / 通知 / 监事会 / 董事会路径不回退
- 不重开 supervisory_board_known_001–002 / shareholder_meeting_known_001–007

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_legal_opinion_known_001_002_promotion.py
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

# harvest 证据标题（只读引用；BD2E544 / BD2E416）
HARVEST_001 = "2025年第一次临时股东大会的法律意见书"
HARVEST_002 = (
    "北京市星河律师事务所关于北京金自天正智能控制股份有限公司"
    "2024年年度股东会的法律意见书"
)
PATTERN_001 = "第一次临时股东大会的法律意见书"
PATTERN_002 = "年度股东会的法律意见书"
SM_RES = "2025年第二次临时股东大会决议公告"
SM_SHORT_RES = "2025年第五次临时股东会决议公告"
SM_ANNUAL = "2024年年度股东会决议公告"
SM_NOTICE = "关于召开2025年度第二次临时股东大会通知的公告"
SB_001 = "第六届监事会第二十四次会议决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
MATERIALS = "2025年第二次临时股东大会会议材料"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestLegalOpinionKnown001002Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_legal_opinion_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "legal_opinion_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "002756")
        self.assertEqual(c["company_name"], "永兴材料")
        self.assertEqual(c["title_pattern"], PATTERN_001)
        self.assertEqual(c["date_start"], "2025-06-01")
        self.assertEqual(c["date_end"], "2025-06-04")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_001, HARVEST_001)
        self.assertIn("股东大会", c["title_pattern"])
        self.assertIn("法律意见书", c["title_pattern"])
        self.assertNotIn("股东会决议", c["title_pattern"])
        self.assertNotIn("通知", c["title_pattern"])

    def test_legal_opinion_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "legal_opinion_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "600560")
        self.assertEqual(c["company_name"], "金自天正")
        self.assertEqual(c["title_pattern"], PATTERN_002)
        self.assertEqual(c["date_start"], "2025-06-25")
        self.assertEqual(c["date_end"], "2025-06-28")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_002, HARVEST_002)
        self.assertIn("股东会", c["title_pattern"])
        self.assertNotIn("股东大会", c["title_pattern"])
        self.assertIn("法律意见书", c["title_pattern"])

    def test_title_patterns_mutually_exclusive(self) -> None:
        """法律意见 pattern 与股东会决议/通知 / 监事会 / 董事会互斥。"""
        self.assertTrue(retrieval._title_matches(HARVEST_001, PATTERN_001))
        self.assertTrue(retrieval._title_matches(HARVEST_002, PATTERN_002))
        self.assertFalse(retrieval._title_matches(HARVEST_001, PATTERN_002))
        self.assertFalse(retrieval._title_matches(HARVEST_002, PATTERN_001))
        for title in (SM_RES, SM_SHORT_RES, SM_ANNUAL, SM_NOTICE, SB_001, BOARD, MATERIALS):
            self.assertFalse(retrieval._title_matches(title, PATTERN_001), title)
            self.assertFalse(retrieval._title_matches(title, PATTERN_002), title)

    def test_closed_anchors_untouched(self) -> None:
        """不削弱已 LIVE_PASS / 既有 ready 锚点字段。"""
        sb1 = _by_id(self.known, "supervisory_board_known_001")
        sb2 = _by_id(self.known, "supervisory_board_known_002")
        self.assertEqual(sb1["case_status"], "ready")
        self.assertEqual(sb2["case_status"], "ready")
        self.assertEqual(sb1["title_pattern"], "第二十四次会议决议公告")
        self.assertEqual(sb2["title_pattern"], "第二十二次会议决议的公告")

        sm_expect = {
            "shareholder_meeting_known_001": "股东大会通知",
            "shareholder_meeting_known_002": "股东大会的通知",
            "shareholder_meeting_known_003": "股东大会决议",
            "shareholder_meeting_known_004": "股东大会的公告",
            "shareholder_meeting_known_005": "临时股东会决议",
            "shareholder_meeting_known_006": "股东会的通知",
            "shareholder_meeting_known_007": "年度股东会决议",
        }
        for case_id, pattern in sm_expect.items():
            c = _by_id(self.known, case_id)
            self.assertEqual(c["case_status"], "ready", case_id)
            self.assertEqual(c["title_pattern"], pattern, case_id)
            self.assertEqual(c["expected_document_type"], "shareholder_meeting_material", case_id)

    def test_harvest_titles_route_announcement_not_shareholder_meeting(self) -> None:
        for title in (HARVEST_001, HARVEST_002):
            r = routing.route_title(title, self.config)
            self.assertEqual(r.predicted_document_type, "announcement", title)
            self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf", title)
            self.assertEqual(r.predicted_classification, "general_announcement", title)
            self.assertNotEqual(r.predicted_document_type, "shareholder_meeting_material", title)
            self.assertNotEqual(r.predicted_document_type, "board_resolution", title)

    def test_shareholder_supervisory_board_routes_untouched(self) -> None:
        """股东会决议/通知 / 监事会 / 董事会路由不回退。"""
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_short = routing.route_title(SM_SHORT_RES, self.config)
        self.assertEqual(r_short.predicted_document_type, "shareholder_meeting_material")
        r_sb = routing.route_title(SB_001, self.config)
        self.assertEqual(r_sb.predicted_document_type, "announcement")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_pair_distinct_from_each_other_and_shareholder(self) -> None:
        k1 = _by_id(self.known, "legal_opinion_known_001")
        k2 = _by_id(self.known, "legal_opinion_known_002")
        self.assertNotEqual(k1["company_code"], k2["company_code"])
        self.assertNotEqual(k1["title_pattern"], k2["title_pattern"])
        self.assertEqual(k1["expected_document_type"], k2["expected_document_type"])
        sm3 = _by_id(self.known, "shareholder_meeting_known_003")
        self.assertNotEqual(k1["expected_document_type"], sm3["expected_document_type"])
        self.assertEqual(k1["expected_route_to"], sm3["expected_route_to"])


if __name__ == "__main__":
    unittest.main()
