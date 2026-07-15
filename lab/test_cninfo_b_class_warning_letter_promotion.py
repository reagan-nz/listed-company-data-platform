"""
B-FM-08：警示函（监管函件原文）晋升锁测（离线）。

覆盖：
- regulatory_known_001 / inquiry_sample_001 已为 ready 且字段齐全
- harvest 标题经 B-FM-07 routing edge 预测 regulatory_inquiry
- title_pattern 锚定「警示函」边角；与关注函 known_002 可区分
- 「警示函的回复」仍走 inquiry_reply，不回退

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_warning_letter_promotion.py
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

# harvest 证据标题（只读引用；BD2E626）
WARNING_LETTER = "关于收到浙江证监局警示函的公告"
WARNING_REPLY = "关于警示函的回复公告"
PATTERN = "警示函"
CONCERN_PATTERN = "关于收到深圳证券交易所关注函的公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestWarningLetterPromotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)
        cls.category = _load_cases(CATEGORY_YAML)

    def test_regulatory_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "regulatory_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300792")
        self.assertEqual(c["company_name"], "壹网壹创")
        self.assertEqual(c["expected_document_type"], "regulatory_inquiry")
        self.assertEqual(c["expected_route_to"], "cninfo_inquiry_reply_pdf")
        self.assertEqual(c["date_start"], "2025-06-22")
        self.assertEqual(c["date_end"], "2025-06-25")
        self.assertEqual(c["title_pattern"], WARNING_LETTER)
        self.assertIn(PATTERN, c["title_pattern"])
        self.assertNotIn("回复", c["title_pattern"])

    def test_inquiry_sample_001_ready_fields(self) -> None:
        c = _by_id(self.category, "inquiry_sample_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["title_pattern"], PATTERN)
        self.assertEqual(c["date_start"], "2025-06-21")
        self.assertEqual(c["date_end"], "2025-06-25")
        self.assertEqual(c["source_id"], "cninfo_inquiry_reply_pdf")
        self.assertIn("regulatory_inquiry", c["expected_document_types"])
        self.assertIn("inquiry_reply", c["expected_document_types"])
        self.assertIn(PATTERN, WARNING_LETTER)

    def test_harvest_title_routes_regulatory_inquiry(self) -> None:
        r = routing.route_title(WARNING_LETTER, self.config)
        self.assertEqual(r.predicted_document_type, "regulatory_inquiry")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")
        self.assertEqual(r.predicted_classification, "inquiry_reply")

    def test_warning_reply_still_inquiry_reply(self) -> None:
        """晋升不回退：警示函回复仍为 inquiry_reply。"""
        r = routing.route_title(WARNING_REPLY, self.config)
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_warning_distinct_from_concern_letter_known(self) -> None:
        """警示函 known 与关注函 known_002 边角可区分。"""
        k1 = _by_id(self.known, "regulatory_known_001")
        k2 = _by_id(self.known, "regulatory_known_002")
        for c in (k1, k2):
            self.assertEqual(c["case_status"], "ready")
            self.assertEqual(c["expected_document_type"], "regulatory_inquiry")
        self.assertEqual(k1["title_pattern"], WARNING_LETTER)
        self.assertEqual(k2["title_pattern"], CONCERN_PATTERN)
        self.assertNotEqual(k1["company_code"], k2["company_code"])
        self.assertIn(PATTERN, k1["title_pattern"])
        self.assertNotIn(PATTERN, k2["title_pattern"])
        self.assertIn("关注函", k2["title_pattern"])


if __name__ == "__main__":
    unittest.main()
