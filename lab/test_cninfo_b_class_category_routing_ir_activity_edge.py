"""
B 类 category routing — IR activity document_type 边角锁测。

覆盖 harvest 已见但旧 meeting patterns 会落入 general_announcement 的标题：
- 「投资者网上集体接待日」（无说明会）→ investor_relations_activity
- 「投资者开放日」→ investor_relations_activity
- 「集体接待日暨…业绩说明会」→ 仍为 meeting_notice（说明会优先）
- 既有说明会 / 投资者关系活动记录表路径不回退
- 「引入投资者」「面向…投资者」债券/股权类不得误进 meeting

离线 only · 无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_category_routing_ir_activity_edge.py
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
COLLECTIVE_JILIN = "关于参加2025年吉林辖区上市公司投资者网上集体接待日活动的公告"
COLLECTIVE_FUJIAN = "关于参加2025年福建辖区上市公司投资者网上集体接待日活动的公告"
OPEN_DAY = "关于举办投资者开放日活动的公告"
COLLECTIVE_WITH_BRIEFING = (
    "关于参加青海辖区上市公司2025年投资者网上集体接待日暨2024年度业绩说明会的公告"
)
IR_RECORD = "万向钱潮投资者关系活动记录表（2025年6月24日）"
BRIEFING = "关于召开2024年年度暨2025年第一季度业绩说明会的公告"


class TestIrActivityDocumentTypeEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_collective_reception_day_routes_ir_activity(self) -> None:
        """BD2E202：纯集体接待日 → investor_relations_activity。"""
        r = self._route(COLLECTIVE_JILIN)
        self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")
        self.assertEqual(r.predicted_document_type, "investor_relations_activity")
        self.assertEqual(r.predicted_classification, "meeting_notice")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertNotEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_collective_fujian_same_edge(self) -> None:
        """BD2E206：同构集体接待日。"""
        r = self._route(COLLECTIVE_FUJIAN)
        self.assertEqual(r.predicted_document_type, "investor_relations_activity")
        self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_investor_open_day_routes_ir_activity(self) -> None:
        """BD2E232：投资者开放日 → investor_relations_activity。"""
        r = self._route(OPEN_DAY)
        self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")
        self.assertEqual(r.predicted_document_type, "investor_relations_activity")

    def test_helper_markers(self) -> None:
        self.assertEqual(
            routing._meeting_document_type(COLLECTIVE_JILIN),
            "investor_relations_activity",
        )
        self.assertEqual(
            routing._meeting_document_type(OPEN_DAY),
            "investor_relations_activity",
        )
        self.assertEqual(
            routing._meeting_document_type(COLLECTIVE_WITH_BRIEFING),
            "meeting_notice",
        )

    def test_collective_with_briefing_stays_meeting_notice(self) -> None:
        """BD2E088：集体接待日暨业绩说明会 → meeting_notice（说明会优先）。"""
        r = self._route(COLLECTIVE_WITH_BRIEFING)
        self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")
        self.assertEqual(r.predicted_document_type, "meeting_notice")
        self.assertNotEqual(r.predicted_document_type, "investor_relations_activity")

    def test_existing_meeting_and_ir_record_not_regressed(self) -> None:
        """既有说明会 / 活动记录表路径不回退。"""
        r1 = self._route(BRIEFING)
        self.assertEqual(r1.predicted_document_type, "meeting_notice")
        self.assertEqual(r1.predicted_route_to, "cninfo_meeting_notice_pdf")

        r2 = self._route(IR_RECORD)
        self.assertEqual(r2.predicted_document_type, "investor_relations_activity")
        self.assertEqual(r2.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_investor_substring_false_friends_stay_general(self) -> None:
        """含「投资者」但非 IR 接待/开放日的标题不得误进 meeting。"""
        for title in (
            "关于子公司增资扩股暨引入投资者及股权转让的进展公告（三）",
            "国元证券股份有限公司2025年面向专业投资者公开发行公司债券（第三期）募集说明书摘要",
            "关于收到中国银行间市场交易商协会《接受注册通知书》的公告",
        ):
            with self.subTest(title=title[:36]):
                r = self._route(title)
                self.assertNotEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")
                self.assertNotEqual(
                    r.predicted_document_type, "investor_relations_activity"
                )

    def test_not_periodic_and_no_invented_section7_fp(self) -> None:
        """边角硬化不得把 IR 误进 periodic，也不得新造 §7 FP 标签。"""
        for title in (
            COLLECTIVE_JILIN,
            COLLECTIVE_FUJIAN,
            OPEN_DAY,
            COLLECTIVE_WITH_BRIEFING,
            IR_RECORD,
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
