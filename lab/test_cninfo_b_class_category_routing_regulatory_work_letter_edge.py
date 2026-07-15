"""
B 类 category routing — 监管工作函 document_type 边角锁测（B-FM-11）。

覆盖 harvest 已见但旧 patterns 会落入 periodic_report 的标题：
- CPA「…监管工作函的专项说明」（含「年度报告」）→ inquiry_reply / 非 periodic
- 「关于收到…监管工作函的公告」→ regulatory_inquiry
- 既有警示函 / 关注函 / CPA 问询函回复路径不回退
- 「延期回复…问询函」仍为 regulatory_inquiry

离线 only · 无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_category_routing_regulatory_work_letter_edge.py
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

# harvest 证据标题（只读引用；BD2E433；本测不请求 CNINFO）
WORK_LETTER_CPA = (
    "中兴财光华会计师事务所（特殊普通合伙）关于对文投控股股份有限公司"
    "2024年年度报告的信息披露监管工作函的专项说明"
)
WORK_LETTER_RECEIVED = "关于收到深圳证券交易所监管工作函的公告"
WORK_LETTER_REPLY = "关于对监管工作函的回复公告"
WARNING_LETTER = "关于收到浙江证监局警示函的公告"
CONCERN_LETTER = "关于收到深圳证券交易所关注函的公告"
CPA_REPLY = (
    "立信会计师事务所（特殊普通合伙）关于西藏华钰矿业股份有限公司"
    "2024年年度报告的信息披露监管问询函的回复"
)
DELAYED_REPLY = (
    "希荻微关于延期回复《关于希荻微电子集团股份有限公司发行股份及支付现金购买资产"
    "并募集配套资金申请的审核问询函》的公告"
)
# 非标意见专项说明：不得仅因「专项说明」误进 inquiry
NON_STD_SPECIAL = (
    "中兴华会计师事务所关于对永鼎股份2023年度财务报表出具非标准审计意见"
    "审计报告所涉及事项在2024年度消除情况的专项说明"
)


class TestRegulatoryWorkLetterDocumentTypeEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_cpa_work_letter_special_statement_routes_inquiry_reply(self) -> None:
        """BD2E433：CPA 监管工作函专项说明 → inquiry_reply，不得进 periodic。"""
        r = self._route(WORK_LETTER_CPA)
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_classification, "inquiry_reply")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertNotEqual(r.predicted_document_type, "annual_report")

    def test_helper_markers_include_work_letter(self) -> None:
        self.assertEqual(
            routing._inquiry_document_type(WORK_LETTER_CPA),
            "inquiry_reply",
        )
        self.assertEqual(
            routing._inquiry_document_type(WORK_LETTER_RECEIVED),
            "regulatory_inquiry",
        )
        self.assertEqual(
            routing._inquiry_document_type(WORK_LETTER_REPLY),
            "inquiry_reply",
        )

    def test_received_work_letter_routes_regulatory(self) -> None:
        """收到监管工作函原文 → regulatory_inquiry。"""
        r = self._route(WORK_LETTER_RECEIVED)
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")
        self.assertEqual(r.predicted_document_type, "regulatory_inquiry")
        self.assertEqual(r.predicted_classification, "inquiry_reply")

    def test_work_letter_reply_routes_inquiry_reply(self) -> None:
        r = self._route(WORK_LETTER_REPLY)
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_warning_and_concern_not_regressed(self) -> None:
        for title, dtype in (
            (WARNING_LETTER, "regulatory_inquiry"),
            (CONCERN_LETTER, "regulatory_inquiry"),
        ):
            with self.subTest(title=title[:30]):
                r = self._route(title)
                self.assertEqual(r.predicted_document_type, dtype)
                self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_cpa_inquiry_reply_not_regressed(self) -> None:
        """B-FM-02 CPA「问询函的回复」路径不回退。"""
        r = self._route(CPA_REPLY)
        self.assertEqual(r.predicted_document_type, "inquiry_reply")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_delayed_reply_stays_regulatory(self) -> None:
        """BD2E500：延期回复问询函仍为 regulatory_inquiry。"""
        r = self._route(DELAYED_REPLY)
        self.assertEqual(r.predicted_document_type, "regulatory_inquiry")
        self.assertEqual(r.predicted_route_to, "cninfo_inquiry_reply_pdf")

    def test_non_std_special_statement_not_forced_to_inquiry(self) -> None:
        """裸「专项说明」不得仅因该词误进 inquiry；非工作函标题保持原路径。"""
        r = self._route(NON_STD_SPECIAL)
        self.assertNotEqual(r.predicted_document_type, "inquiry_reply")
        self.assertNotEqual(r.predicted_document_type, "regulatory_inquiry")
        self.assertNotIn("监管工作函", NON_STD_SPECIAL)

    def test_not_periodic_and_no_invented_section7_fp(self) -> None:
        """边角硬化不得把监管工作函误进 periodic，也不得新造 §7 FP 标签。"""
        for title in (
            WORK_LETTER_CPA,
            WORK_LETTER_RECEIVED,
            WORK_LETTER_REPLY,
            WARNING_LETTER,
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
