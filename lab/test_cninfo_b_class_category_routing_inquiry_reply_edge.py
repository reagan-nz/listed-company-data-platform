"""
B 类 category routing — inquiry_reply document_type 边角锁测。

覆盖 harvest 已见但旧 `_inquiry_document_type` 会误判的标题：
- CPA「…监管问询函的回复」（无「回复公告」后缀）→ inquiry_reply
- 「延期回复…问询函」→ 仍为 regulatory_inquiry（非回复正文）
- 既有「回复公告 / 问询函回复」路径不回退
- 纯问询/关注函原文仍为 regulatory_inquiry

离线 only · 无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_category_routing_inquiry_reply_edge.py
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_b_class_category_routing as routing  # noqa: E402

CATEGORIES = routing.DEFAULT_CATEGORIES

# harvest 证据标题（只读引用；本测不请求 CNINFO）
CPA_HUAYU = (
    "立信会计师事务所（特殊普通合伙）关于西藏华钰矿业股份有限公司"
    "2024年年度报告的信息披露监管问询函的回复"
)
CPA_LANSHI = (
    "利安达会计师事务所关于兰石重装2024年年度报告的信息披露监管问询函的回复"
)
DELAYED_REPLY = (
    "希荻微关于延期回复《关于希荻微电子集团股份有限公司发行股份及支付现金购买资产"
    "并募集配套资金申请的审核问询函》的公告"
)
COMPANY_REPLY_ANNOUNCEMENT = (
    "关于2024年年度报告的信息披露监管问询函的回复公告"
)


class TestInquiryReplyDocumentTypeEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_cpa_inquiry_reply_without_announcement_suffix(self) -> None:
        """BD2E462 形态：以「问询函的回复」结尾 → inquiry_reply。"""
        r = self._route(CPA_HUAYU)
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_classification, "inquiry_reply")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertNotEqual(r.predicted_document_type, "regulatory_inquiry")

    def test_cpa_lanshi_same_edge(self) -> None:
        """BD2E794 形态：同构 CPA 回复标题。"""
        r = self._route(CPA_LANSHI)
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_helper_markers_include_de_particle(self) -> None:
        self.assertEqual(routing._inquiry_document_type(CPA_HUAYU), "inquiry_reply")
        self.assertEqual(routing._inquiry_document_type(CPA_LANSHI), "inquiry_reply")
        self.assertEqual(
            routing._inquiry_document_type("关于关注函的回复"),
            "inquiry_reply",
        )

    def test_delayed_reply_stays_regulatory_inquiry(self) -> None:
        """BD2E500：延期回复问询函，非回复正文 → regulatory_inquiry。"""
        r = self._route(DELAYED_REPLY)
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")
        self.assertEqual(r.predicted_document_type, "regulatory_inquiry")
        self.assertNotEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(
            routing._inquiry_document_type(DELAYED_REPLY),
            "regulatory_inquiry",
        )

    def test_existing_reply_announcement_not_regressed(self) -> None:
        """既有「回复公告」路径保持 inquiry_reply。"""
        r = self._route(COMPANY_REPLY_ANNOUNCEMENT)
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

        r2 = self._route("关于深圳证券交易所年报问询函回复的公告")
        self.assertEqual(r2.predicted_document_type, "inquiry_reply")

    def test_pure_inquiry_letter_stays_regulatory(self) -> None:
        """问询/关注函原文不得误升为 inquiry_reply。"""
        for title in (
            "关于对某公司年报的问询函",
            "深圳证券交易所关注函",
            "关于收到深圳证券交易所关注函的公告",
            "深圳证券交易所年报问询函",
        ):
            with self.subTest(title=title):
                r = self._route(title)
                self.assertEqual(r.predicted_document_type, "regulatory_inquiry")
                self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_not_periodic_and_no_invented_section7_fp(self) -> None:
        """边角硬化不得把回复误进 periodic，也不得新造 §7 FP 标签。"""
        for title in (CPA_HUAYU, CPA_LANSHI, DELAYED_REPLY, COMPANY_REPLY_ANNOUNCEMENT):
            with self.subTest(title=title[:40]):
                r = self._route(title)
                self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
                self.assertNotIn(
                    r.false_positive_reason,
                    (
                        "wrong_company",
                        "wrong_period",
                        "announcement_preview",
                        "unrelated_announcement",
                    ),
                )


if __name__ == "__main__":
    unittest.main()
