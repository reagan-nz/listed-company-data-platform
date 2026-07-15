"""
B-FM-06：IR 投资者开放日晋升锁测（离线）。

覆盖：
- ir_activity_known_003 / ir_activity_sample_002 已为 ready 且字段齐全
- harvest 标题经 B-FM-04 routing edge 预测 investor_relations_activity
- title_pattern 为「投资者开放日」；与集体接待日 / 活动记录表 known 可区分
- 不含「说明会」以免误锁 meeting_notice

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_ir_activity_open_day_promotion.py
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

# harvest 证据标题（只读引用；BD2E232）
OPEN_DAY = "关于举办投资者开放日活动的公告"
PATTERN = "投资者开放日"
COLLECTIVE_PATTERN = "投资者网上集体接待日"
RECORD_PATTERN = "投资者关系活动记录表"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestIrActivityOpenDayPromotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)
        cls.category = _load_cases(CATEGORY_YAML)

    def test_ir_activity_known_003_ready_fields(self) -> None:
        c = _by_id(self.known, "ir_activity_known_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000949")
        self.assertEqual(c["company_name"], "新乡化纤")
        self.assertEqual(c["expected_document_type"], "investor_relations_activity")
        self.assertEqual(c["expected_route_to"], "cninfo_meeting_notice_pdf")
        self.assertEqual(c["date_start"], "2025-06-02")
        self.assertEqual(c["date_end"], "2025-06-05")
        self.assertEqual(c["title_pattern"], PATTERN)
        self.assertIn(PATTERN, OPEN_DAY)
        self.assertNotIn("说明会", c["title_pattern"])

    def test_ir_activity_sample_002_ready_fields(self) -> None:
        c = _by_id(self.category, "ir_activity_sample_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["title_pattern"], PATTERN)
        self.assertEqual(c["date_start"], "2025-06-01")
        self.assertEqual(c["date_end"], "2025-06-05")
        self.assertEqual(c["source_id"], "cninfo_meeting_notice_pdf")
        self.assertIn("investor_relations_activity", c["expected_document_types"])
        self.assertIn("meeting_notice", c["expected_document_types"])
        self.assertIn(PATTERN, OPEN_DAY)

    def test_harvest_title_routes_ir_activity(self) -> None:
        r = routing.route_title(OPEN_DAY, self.config)
        self.assertEqual(r.predicted_document_type, "investor_relations_activity")
        self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")
        self.assertEqual(r.predicted_classification, "meeting_notice")

    def test_open_day_distinct_from_sibling_ir_cases(self) -> None:
        """开放日 known/sample 与集体接待日、活动记录表边角可区分。"""
        k1 = _by_id(self.known, "ir_activity_known_001")
        k2 = _by_id(self.known, "ir_activity_known_002")
        k3 = _by_id(self.known, "ir_activity_known_003")
        s1 = _by_id(self.category, "ir_activity_sample_001")
        s2 = _by_id(self.category, "ir_activity_sample_002")
        for c in (k1, k2, k3, s1, s2):
            self.assertEqual(c["case_status"], "ready")
        self.assertEqual(k1["title_pattern"], RECORD_PATTERN)
        self.assertEqual(k2["title_pattern"], COLLECTIVE_PATTERN)
        self.assertEqual(k3["title_pattern"], PATTERN)
        self.assertEqual(s1["title_pattern"], COLLECTIVE_PATTERN)
        self.assertEqual(s2["title_pattern"], PATTERN)
        self.assertNotEqual(k3["company_code"], k1["company_code"])
        self.assertNotEqual(k3["company_code"], k2["company_code"])
        self.assertNotIn(PATTERN, COLLECTIVE_PATTERN)
        self.assertNotIn(COLLECTIVE_PATTERN, OPEN_DAY)


if __name__ == "__main__":
    unittest.main()
