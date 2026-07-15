"""
B-FM-16：股东大会通知「的」助词变体 known-document 晋升锁测（离线）。

覆盖：
- shareholder_meeting_known_002 已为 ready 且字段齐全
- title_pattern 为「股东大会的通知」（非连续「股东大会通知」）
- harvest 标题经既有路由预测 shareholder_meeting_material → general
- 与 known_001 / meeting_sample_002 边角可区分
- 含「说明会」的会议通知仍走 meeting_notice，不回退

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py
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

# harvest 证据标题（只读引用；BD2E292）
SHAREHOLDER_NOTICE_DE = "关于召开2025年第三次临时股东大会的通知"
PATTERN_DE = "股东大会的通知"
PATTERN_CONTIG = "股东大会通知"
KNOWN_001_TITLE = "关于召开2025年度第二次临时股东大会通知的公告"
BRIEFING = "关于召开重大资产重组事项投资者说明会的公告"
COMBO = "关于召开2025年年度股东大会通知暨投资者说明会的公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestShareholderMeetingKnown002Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)
        cls.category = _load_cases(CATEGORY_YAML)

    def test_shareholder_meeting_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "shareholder_meeting_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "002237")
        self.assertEqual(c["company_name"], "恒邦股份")
        self.assertEqual(c["title_pattern"], PATTERN_DE)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "shareholder_meeting_material")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_DE, SHAREHOLDER_NOTICE_DE)
        self.assertNotIn(PATTERN_CONTIG, SHAREHOLDER_NOTICE_DE)
        self.assertNotIn("说明会", c["title_pattern"])

    def test_title_pattern_matches_harvest_not_contig(self) -> None:
        """「的」助词变体：_title_matches 命中 known_002，不命中连续子串 pattern。"""
        self.assertTrue(
            retrieval._title_matches(SHAREHOLDER_NOTICE_DE, PATTERN_DE)
        )
        self.assertFalse(
            retrieval._title_matches(SHAREHOLDER_NOTICE_DE, PATTERN_CONTIG)
        )
        self.assertTrue(
            retrieval._title_matches(KNOWN_001_TITLE, PATTERN_CONTIG)
        )
        self.assertFalse(
            retrieval._title_matches(KNOWN_001_TITLE, PATTERN_DE)
        )

    def test_shareholder_meeting_known_001_still_ready_anchor(self) -> None:
        """新晋 known_002 不削弱 known_001 / category-sample 锚点。"""
        k1 = _by_id(self.known, "shareholder_meeting_known_001")
        s2 = _by_id(self.category, "meeting_sample_002")
        self.assertEqual(k1["case_status"], "ready")
        self.assertEqual(k1["title_pattern"], PATTERN_CONTIG)
        self.assertEqual(k1["company_code"], "300446")
        self.assertEqual(s2["case_status"], "ready")
        self.assertEqual(s2["title_pattern"], PATTERN_CONTIG)
        self.assertEqual(s2["source_id"], "cninfo_general_announcement_pdf")

    def test_harvest_title_routes_general_not_meeting_notice(self) -> None:
        r = routing.route_title(SHAREHOLDER_NOTICE_DE, self.config)
        self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.predicted_classification, "general_announcement")
        self.assertNotEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_briefing_still_meeting_notice(self) -> None:
        """晋升不回退：纯说明会仍为 meeting_notice。"""
        r = routing.route_title(BRIEFING, self.config)
        self.assertEqual(r.predicted_document_type, "meeting_notice")
        self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_combo_notice_with_briefing_still_meeting_notice(self) -> None:
        """含说明会的股东大会通知仍走 meeting_notice。"""
        r = routing.route_title(COMBO, self.config)
        self.assertEqual(r.predicted_document_type, "meeting_notice")
        self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_distinct_from_known_001_and_sample_002(self) -> None:
        """known_002 与 known_001 / meeting_sample_002 公司与 pattern 可区分。"""
        k1 = _by_id(self.known, "shareholder_meeting_known_001")
        k2 = _by_id(self.known, "shareholder_meeting_known_002")
        s2 = _by_id(self.category, "meeting_sample_002")
        self.assertNotEqual(k1["company_code"], k2["company_code"])
        self.assertNotEqual(k1["title_pattern"], k2["title_pattern"])
        self.assertEqual(s2["title_pattern"], k1["title_pattern"])
        self.assertNotEqual(s2["title_pattern"], k2["title_pattern"])
        self.assertEqual(k1["expected_document_type"], k2["expected_document_type"])
        self.assertEqual(k1["expected_route_to"], k2["expected_route_to"])


if __name__ == "__main__":
    unittest.main()
