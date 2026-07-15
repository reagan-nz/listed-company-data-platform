"""
B 类 category routing — 股东大会决议 / 召开公告 document_type 边角锁测（B-FM-18）。

覆盖 harvest 已见但旧 `_general_document_type` 一律落 announcement 的标题：
- 「…股东大会决议公告」→ shareholder_meeting_material
- 「关于召开…股东大会的公告」（无「通知」）→ shareholder_meeting_material
- 法律意见书 / 会议材料仍为 announcement
- 既有「股东大会通知 / 的通知」与董事会决议路径不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py
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
RESOLUTION = "2025年第二次临时股东大会决议公告"  # BD2E578
CONVENING_ANNOUNCEMENT = "关于召开2025年第二次临时股东大会的公告"  # BD2E080
LEGAL_OPINION = (
    "湖南启元律师事务所关于长高电新科技股份公司"
    "2025年第二次临时股东大会的法律意见书"
)  # BD2E508
MEETING_MATERIALS = "2025年第二次临时股东大会会议材料"  # BD2E067
NOTICE_CONTIG = "关于召开2025年度第二次临时股东大会通知的公告"
NOTICE_DE = "关于召开2025年第三次临时股东大会的通知"
BOARD_RESOLUTION = "九届二十九次董事会决议公告"
BRIEFING = "关于召开重大资产重组事项投资者说明会的公告"


class TestShareholderMeetingResolutionRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_resolution_routes_shareholder_meeting_material(self) -> None:
        """BD2E578：股东大会决议公告 → shareholder_meeting_material / general。"""
        r = self._route(RESOLUTION)
        self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.predicted_classification, "general_announcement")
        self.assertNotEqual(r.predicted_document_type, "board_resolution")
        self.assertNotEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_convening_announcement_without_notice_word(self) -> None:
        """BD2E080：召开…股东大会的公告（无「通知」）→ shareholder_meeting_material。"""
        r = self._route(CONVENING_ANNOUNCEMENT)
        self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotIn("通知", CONVENING_ANNOUNCEMENT)

    def test_legal_opinion_stays_announcement(self) -> None:
        """法律意见书不得抬成 shareholder_meeting_material。"""
        r = self._route(LEGAL_OPINION)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_meeting_materials_stay_announcement(self) -> None:
        """会议材料不得抬成 shareholder_meeting_material。"""
        r = self._route(MEETING_MATERIALS)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_notice_variants_not_regressed(self) -> None:
        """既有股东大会通知 / 「的」助词变体路径不回退。"""
        for title in (NOTICE_CONTIG, NOTICE_DE):
            with self.subTest(title=title[:40]):
                r = self._route(title)
                self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_board_resolution_not_regressed(self) -> None:
        """董事会决议仍为 board_resolution，不得误进 shareholder_meeting_material。"""
        r = self._route(BOARD_RESOLUTION)
        self.assertEqual(r.predicted_document_type, "board_resolution")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_briefing_still_meeting_notice(self) -> None:
        """纯说明会仍为 meeting_notice。"""
        r = self._route(BRIEFING)
        self.assertEqual(r.predicted_document_type, "meeting_notice")
        self.assertEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_helper_general_document_type_markers(self) -> None:
        """直接锁测 `_general_document_type` 边角分支。"""
        patterns = ["公告", "决议", "股东大会", "董事会", "监事会"]
        self.assertEqual(
            routing._general_document_type(RESOLUTION, patterns),
            "shareholder_meeting_material",
        )
        self.assertEqual(
            routing._general_document_type(CONVENING_ANNOUNCEMENT, patterns),
            "shareholder_meeting_material",
        )
        self.assertEqual(
            routing._general_document_type(LEGAL_OPINION, patterns),
            "announcement",
        )
        self.assertEqual(
            routing._general_document_type(MEETING_MATERIALS, patterns),
            "announcement",
        )

    def test_not_periodic_and_no_invented_section7_fp(self) -> None:
        """边角硬化不得把股东大会材料误进 periodic，也不得新造 §7 FP 标签。"""
        for title in (
            RESOLUTION,
            CONVENING_ANNOUNCEMENT,
            LEGAL_OPINION,
            MEETING_MATERIALS,
            NOTICE_CONTIG,
            NOTICE_DE,
            BOARD_RESOLUTION,
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
