"""
B 类 category routing — 警示函 document_type 边角锁测。

覆盖 harvest 已见但旧 inquiry patterns 会落入 general_announcement 的标题：
- 「关于收到…警示函的公告」（无回复）→ regulatory_inquiry
- 「警示函的回复 / 回复公告」→ inquiry_reply
- 既有问询函 / 关注函原文与 CPA 回复路径不回退
- 「延期回复…问询函」仍为 regulatory_inquiry

离线 only · 无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_category_routing_warning_letter_edge.py
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
WARNING_LETTER = "关于收到浙江证监局警示函的公告"
WARNING_REPLY = "关于警示函的回复公告"
WARNING_REPLY_DE = "关于对警示函的回复"
CONCERN_LETTER = "关于收到深圳证券交易所关注函的公告"
CPA_REPLY = (
    "立信会计师事务所（特殊普通合伙）关于西藏华钰矿业股份有限公司"
    "2024年年度报告的信息披露监管问询函的回复"
)
DELAYED_REPLY = (
    "希荻微关于延期回复《关于希荻微电子集团股份有限公司发行股份及支付现金购买资产"
    "并募集配套资金申请的审核问询函》的公告"
)


class TestWarningLetterDocumentTypeEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_received_warning_letter_routes_regulatory(self) -> None:
        """BD2E626：收到警示函原文 → regulatory_inquiry / inquiry_reply 源。"""
        r = self._route(WARNING_LETTER)
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")
        self.assertEqual(r.predicted_document_type, "regulatory_inquiry")
        self.assertEqual(r.predicted_classification, "inquiry_reply")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertNotEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "announcement")

    def test_helper_markers_include_warning_letter(self) -> None:
        self.assertEqual(
            routing._inquiry_document_type(WARNING_LETTER),
            "regulatory_inquiry",
        )
        self.assertEqual(
            routing._inquiry_document_type(WARNING_REPLY_DE),
            "inquiry_reply",
        )
        self.assertEqual(
            routing._inquiry_document_type("关于警示函回复"),
            "inquiry_reply",
        )

    def test_warning_letter_reply_routes_inquiry_reply(self) -> None:
        """警示函回复不得误判为 regulatory_inquiry。"""
        r = self._route(WARNING_REPLY)
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

        r2 = self._route(WARNING_REPLY_DE)
        self.assertEqual(r2.predicted_document_type, "inquiry_reply")
        self.assertEqual(r2.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_concern_letter_not_regressed(self) -> None:
        """既有关注函原文路径保持 regulatory_inquiry。"""
        r = self._route(CONCERN_LETTER)
        self.assertEqual(r.predicted_document_type, "regulatory_inquiry")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_cpa_reply_not_regressed(self) -> None:
        """B-FM-02 CPA「问询函的回复」路径不回退。"""
        r = self._route(CPA_REPLY)
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_delayed_reply_stays_regulatory(self) -> None:
        """BD2E500：延期回复问询函仍为 regulatory_inquiry。"""
        r = self._route(DELAYED_REPLY)
        self.assertEqual(r.predicted_document_type, "regulatory_inquiry")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_not_periodic_and_no_invented_section7_fp(self) -> None:
        """边角硬化不得把警示函误进 periodic，也不得新造 §7 FP 标签。"""
        for title in (
            WARNING_LETTER,
            WARNING_REPLY,
            WARNING_REPLY_DE,
            CONCERN_LETTER,
            CPA_REPLY,
            DELAYED_REPLY,
        ):
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
