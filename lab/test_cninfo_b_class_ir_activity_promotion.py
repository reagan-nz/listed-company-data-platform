"""
B-FM-05：IR 集体接待日晋升锁测（离线）。

覆盖：
- ir_activity_known_002 / ir_activity_sample_001 已为 ready 且字段齐全
- harvest 标题经 B-FM-04 routing edge 预测 investor_relations_activity
- title_pattern 为 harvest 标题子串；不含「说明会」以免误锁 meeting_notice

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_ir_activity_promotion.py
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

# harvest 证据标题（只读引用）
COLLECTIVE_JILIN = "关于参加2025年吉林辖区上市公司投资者网上集体接待日活动的公告"
COLLECTIVE_FUJIAN = "关于参加2025年福建辖区上市公司投资者网上集体接待日活动的公告"
OPEN_DAY = "关于举办投资者开放日活动的公告"
PATTERN = "投资者网上集体接待日"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestIrActivityPromotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)
        cls.category = _load_cases(CATEGORY_YAML)

    def test_ir_activity_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "ir_activity_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000420")
        self.assertEqual(c["company_name"], "吉林化纤")
        self.assertEqual(c["expected_document_type"], "investor_relations_activity")
        self.assertEqual(c["expected_route_to"], "cninfo_meeting_notice_pdf")
        self.assertEqual(c["date_start"], "2025-05-19")
        self.assertEqual(c["date_end"], "2025-05-22")
        self.assertEqual(c["title_pattern"], PATTERN)
        self.assertIn(PATTERN, COLLECTIVE_JILIN)
        self.assertNotIn("说明会", c["title_pattern"])

    def test_ir_activity_sample_001_ready_fields(self) -> None:
        c = _by_id(self.category, "ir_activity_sample_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["title_pattern"], PATTERN)
        self.assertEqual(c["date_start"], "2025-05-08")
        self.assertEqual(c["date_end"], "2025-05-22")
        self.assertEqual(c["source_id"], "cninfo_meeting_notice_pdf")
        self.assertIn("investor_relations_activity", c["expected_document_types"])
        self.assertIn("meeting_notice", c["expected_document_types"])
        self.assertIn(PATTERN, COLLECTIVE_JILIN)
        self.assertIn(PATTERN, COLLECTIVE_FUJIAN)

    def test_harvest_titles_route_ir_activity(self) -> None:
        for title in (COLLECTIVE_JILIN, COLLECTIVE_FUJIAN):
            r = routing.route_title(title, self.config)
            self.assertEqual(r.predicted_document_type, "investor_relations_activity")
            self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")
            self.assertEqual(r.predicted_classification, "meeting_notice")

    def test_open_day_still_routes_but_not_this_pattern(self) -> None:
        """开放日证据保留路由；本包 pattern 专锁集体接待日边角。"""
        r = routing.route_title(OPEN_DAY, self.config)
        self.assertEqual(r.predicted_document_type, "investor_relations_activity")
        self.assertNotIn(PATTERN, OPEN_DAY)

    def test_known_distinct_from_ir_record_case(self) -> None:
        """集体接待日 known 与活动记录表 known_001 可区分。"""
        c1 = _by_id(self.known, "ir_activity_known_001")
        c2 = _by_id(self.known, "ir_activity_known_002")
        self.assertEqual(c1["case_status"], "ready")
        self.assertEqual(c2["case_status"], "ready")
        self.assertNotEqual(c1["title_pattern"], c2["title_pattern"])
        self.assertNotEqual(c1["company_code"], c2["company_code"])


if __name__ == "__main__":
    unittest.main()
