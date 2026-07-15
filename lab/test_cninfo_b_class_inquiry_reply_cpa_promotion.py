"""
B-FM-03：CPA「问询函的回复」晋升锁测（离线）。

覆盖：
- inquiry_known_001 / inquiry_sample_002 已为 ready 且字段齐全
- harvest 标题经 B-FM-02 routing edge 预测 inquiry_reply
- title_pattern 为 harvest 标题子串

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_inquiry_reply_cpa_promotion.py
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
CPA_HUAYU = (
    "立信会计师事务所（特殊普通合伙）关于西藏华钰矿业股份有限公司"
    "2024年年度报告的信息披露监管问询函的回复"
)
CPA_LANSHI = (
    "利安达会计师事务所关于兰石重装2024年年度报告的信息披露监管问询函的回复"
)


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestInquiryReplyCpaPromotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)
        cls.category = _load_cases(CATEGORY_YAML)

    def test_inquiry_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "inquiry_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "601020")
        self.assertEqual(c["company_name"], "华钰矿业")
        self.assertEqual(c["expected_document_type"], "inquiry_reply")
        self.assertEqual(c["expected_route_to"], "cninfo_inquiry_reply_pdf")
        self.assertTrue(c["date_start"] and c["date_end"])
        self.assertEqual(c["title_pattern"], CPA_HUAYU)

    def test_inquiry_sample_002_ready_fields(self) -> None:
        c = _by_id(self.category, "inquiry_sample_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["title_pattern"], "问询函的回复")
        self.assertEqual(c["date_start"], "2025-06-23")
        self.assertEqual(c["date_end"], "2025-06-28")
        self.assertIn("inquiry_reply", c["expected_document_types"])
        self.assertIn(c["title_pattern"], CPA_HUAYU)
        self.assertIn(c["title_pattern"], CPA_LANSHI)

    def test_harvest_titles_route_inquiry_reply(self) -> None:
        for title in (CPA_HUAYU, CPA_LANSHI):
            r = routing.route_title(title, self.config)
            self.assertEqual(r.predicted_document_type, "inquiry_reply")
            self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")
            self.assertEqual(r.predicted_classification, "inquiry_reply")

    def test_known_pattern_does_not_require_announcement_suffix(self) -> None:
        """晋升 pattern 刻意不含「回复公告」，锁住 CPA 边角。"""
        c = _by_id(self.known, "inquiry_known_001")
        self.assertNotIn("回复公告", c["title_pattern"])
        self.assertTrue(c["title_pattern"].endswith("问询函的回复"))
        self.assertTrue(CPA_HUAYU.endswith("问询函的回复"))


if __name__ == "__main__":
    unittest.main()
