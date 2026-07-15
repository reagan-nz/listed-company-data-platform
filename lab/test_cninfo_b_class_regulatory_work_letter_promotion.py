"""
B-FM-12：监管工作函（CPA 专项说明）晋升锁测（离线）。

覆盖：
- inquiry_known_004 / inquiry_sample_003 已为 ready 且字段齐全
- harvest 标题经 B-FM-11 routing edge 预测 inquiry_reply（不得进 periodic）
- title_pattern 锚定「监管工作函」边角；与 CPA「问询函的回复」known_001 可区分
- 「收到…监管工作函」仍走 regulatory_inquiry，不回退

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_regulatory_work_letter_promotion.py
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

# harvest 证据标题（只读引用；BD2E433）
WORK_LETTER_CPA = (
    "中兴财光华会计师事务所（特殊普通合伙）关于对文投控股股份有限公司"
    "2024年年度报告的信息披露监管工作函的专项说明"
)
WORK_LETTER_RECEIVED = "关于收到深圳证券交易所监管工作函的公告"
PATTERN = "监管工作函"
CPA_INQUIRY_REPLY = (
    "立信会计师事务所（特殊普通合伙）关于西藏华钰矿业股份有限公司"
    "2024年年度报告的信息披露监管问询函的回复"
)


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestRegulatoryWorkLetterPromotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)
        cls.category = _load_cases(CATEGORY_YAML)

    def test_inquiry_known_004_ready_fields(self) -> None:
        c = _by_id(self.known, "inquiry_known_004")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "600715")
        self.assertEqual(c["company_name"], "文投控股")
        self.assertEqual(c["expected_document_type"], "inquiry_reply")
        self.assertEqual(c["expected_route_to"], "cninfo_inquiry_reply_pdf")
        self.assertEqual(c["date_start"], "2025-04-27")
        self.assertEqual(c["date_end"], "2025-04-30")
        self.assertEqual(c["title_pattern"], WORK_LETTER_CPA)
        self.assertIn(PATTERN, c["title_pattern"])
        self.assertTrue(c["title_pattern"].endswith("监管工作函的专项说明"))
        self.assertIn("年度报告", c["title_pattern"])

    def test_inquiry_sample_003_ready_fields(self) -> None:
        c = _by_id(self.category, "inquiry_sample_003")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["title_pattern"], PATTERN)
        self.assertEqual(c["date_start"], "2025-04-26")
        self.assertEqual(c["date_end"], "2025-04-30")
        self.assertEqual(c["source_id"], "cninfo_inquiry_reply_pdf")
        self.assertIn("inquiry_reply", c["expected_document_types"])
        self.assertIn("regulatory_inquiry", c["expected_document_types"])
        # 工作函标题常含「年度报告」子串，不得用裸「年度报告」作 FP guard
        self.assertIn("年度报告全文", c["false_positive_guard_patterns"])
        self.assertNotIn("年度报告", c["false_positive_guard_patterns"])
        self.assertIn(PATTERN, WORK_LETTER_CPA)

    def test_harvest_title_routes_inquiry_reply_not_periodic(self) -> None:
        r = routing.route_title(WORK_LETTER_CPA, self.config)
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")
        self.assertEqual(r.predicted_classification, "inquiry_reply")
        self.assertNotEqual(r.predicted_document_type, "annual_report")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_received_work_letter_still_regulatory_inquiry(self) -> None:
        """晋升不回退：收到监管工作函原文仍为 regulatory_inquiry。"""
        r = routing.route_title(WORK_LETTER_RECEIVED, self.config)
        self.assertEqual(r.predicted_document_type, "regulatory_inquiry")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_work_letter_distinct_from_cpa_inquiry_reply_known(self) -> None:
        """监管工作函 known_004 与 CPA 问询函回复 known_001 边角可区分。"""
        k1 = _by_id(self.known, "inquiry_known_001")
        k4 = _by_id(self.known, "inquiry_known_004")
        for c in (k1, k4):
            self.assertEqual(c["case_status"], "ready")
            self.assertEqual(c["expected_document_type"], "inquiry_reply")
        self.assertEqual(k1["title_pattern"], CPA_INQUIRY_REPLY)
        self.assertEqual(k4["title_pattern"], WORK_LETTER_CPA)
        self.assertNotEqual(k1["company_code"], k4["company_code"])
        self.assertIn("问询函的回复", k1["title_pattern"])
        self.assertNotIn("问询函的回复", k4["title_pattern"])
        self.assertIn(PATTERN, k4["title_pattern"])
        self.assertNotIn(PATTERN, k1["title_pattern"])


if __name__ == "__main__":
    unittest.main()
