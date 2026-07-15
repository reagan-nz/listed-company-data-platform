"""
B-FM-14：股东大会通知 category-sample 晋升锁测（离线）。

覆盖：
- meeting_sample_002 已为 ready 且字段齐全
- source_id 为 cninfo_general_announcement_pdf（非 meeting_notice）
- harvest 标题经既有路由预测 shareholder_meeting_material → general
- 与 meeting_sample_001（说明会）边角可区分
- 含「说明会」的会议通知仍走 meeting_notice，不回退

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py
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

KNOWN_YAML = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)
CATEGORY_YAML = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "category_sample_cases.yaml"
)

# harvest 证据标题（只读引用；BD2E574）
SHAREHOLDER_NOTICE = "关于召开2025年度第二次临时股东大会通知的公告"
PATTERN = "股东大会通知"
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


class TestShareholderMeetingSamplePromotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)
        cls.category = _load_cases(CATEGORY_YAML)

    def test_meeting_sample_002_ready_fields(self) -> None:
        c = _by_id(self.category, "meeting_sample_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["title_pattern"], PATTERN)
        self.assertEqual(c["date_start"], "2025-06-22")
        self.assertEqual(c["date_end"], "2025-06-26")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["source_category"], "announcement_pdf")
        self.assertIn("shareholder_meeting_material", c["expected_document_types"])
        self.assertIn("meeting_notice", c["expected_document_types"])
        self.assertIn("announcement", c["expected_document_types"])
        self.assertIn(PATTERN, SHAREHOLDER_NOTICE)
        self.assertNotIn("说明会", c["title_pattern"])

    def test_shareholder_meeting_known_001_still_ready_anchor(self) -> None:
        """category-sample 晋升不削弱 known-document 锚点。"""
        c = _by_id(self.known, "shareholder_meeting_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300446")
        self.assertEqual(c["company_name"], "航天智造")
        self.assertEqual(c["title_pattern"], PATTERN)
        self.assertEqual(c["expected_document_type"], "shareholder_meeting_material")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["date_start"], "2025-06-23")
        self.assertEqual(c["date_end"], "2025-06-26")

    def test_harvest_title_routes_general_not_meeting_notice(self) -> None:
        r = routing.route_title(SHAREHOLDER_NOTICE, self.config)
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
        """含说明会的股东大会通知仍走 meeting_notice（expected 允许多类型）。"""
        r = routing.route_title(COMBO, self.config)
        self.assertEqual(r.predicted_document_type, "meeting_notice")
        self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")
        self.assertIn(PATTERN, COMBO)

    def test_distinct_from_meeting_sample_001(self) -> None:
        """股东大会通知 sample 与说明会 sample_001 边角可区分。"""
        s1 = _by_id(self.category, "meeting_sample_001")
        s2 = _by_id(self.category, "meeting_sample_002")
        for c in (s1, s2):
            self.assertEqual(c["case_status"], "ready")
        self.assertEqual(s1["title_pattern"], "说明会")
        self.assertEqual(s2["title_pattern"], PATTERN)
        self.assertEqual(s1["source_id"], "cninfo_meeting_notice_pdf")
        self.assertEqual(s2["source_id"], "cninfo_general_announcement_pdf")
        self.assertNotEqual(s1["title_pattern"], s2["title_pattern"])


if __name__ == "__main__":
    unittest.main()
