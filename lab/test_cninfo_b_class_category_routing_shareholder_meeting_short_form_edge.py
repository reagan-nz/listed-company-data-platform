"""
B 类 category routing — 「股东会」同义简称 document_type 边角锁测（B-FM-20）。

覆盖 harvest 已见但旧 `_general_document_type` 仅认「股东大会」、简称落 announcement/other 的标题：
- 「…临时/年度股东会决议公告」→ shareholder_meeting_material
- 「关于召开…股东会的通知」→ shareholder_meeting_material
- 法律意见书 / 会议资料仍为 announcement
- 既有「股东大会」决议/通知/召开公告路径不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 known_003/004。

运行：
    python lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py
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
SHORT_RESOLUTION = "2025年第五次临时股东会决议公告"  # BD2E646
SHORT_NOTICE = "关于召开2025年第二次临时股东会的通知"  # BD2E276
SHORT_ANNUAL_RESOLUTION = "2024年年度股东会决议公告"  # BD2E258
SHORT_LEGAL = (
    "北京市星河律师事务所关于北京金自天正智能控制股份有限公司"
    "2024年年度股东会的法律意见书"
)  # BD2E416
SHORT_MATERIALS = "鲁信创投2025年第一次临时股东会会议资料"  # BD2E438
FULL_RESOLUTION = "2025年第二次临时股东大会决议公告"  # BD2E578 / B-FM-18
FULL_CONVENING = "关于召开2025年第二次临时股东大会的公告"  # BD2E080
FULL_NOTICE = "关于召开2025年度第二次临时股东大会通知的公告"
BOARD_RESOLUTION = "九届二十九次董事会决议公告"


class TestShareholderMeetingShortFormRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_helper_recognizes_both_forms(self) -> None:
        """「股东大会」与「股东会」分别识别；二者互不为子串。"""
        self.assertTrue(routing._is_shareholder_meeting_title(FULL_RESOLUTION))
        self.assertTrue(routing._is_shareholder_meeting_title(SHORT_RESOLUTION))
        self.assertNotIn("股东会", "股东大会")
        self.assertNotIn("股东大会", SHORT_RESOLUTION)

    def test_short_resolution_routes_shareholder_meeting_material(self) -> None:
        """BD2E646：临时股东会决议公告 → shareholder_meeting_material / general。"""
        r = self._route(SHORT_RESOLUTION)
        self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.predicted_classification, "general_announcement")
        self.assertNotEqual(r.predicted_document_type, "board_resolution")

    def test_short_notice_routes_shareholder_meeting_material(self) -> None:
        """BD2E276：召开…股东会的通知 → shareholder_meeting_material。"""
        r = self._route(SHORT_NOTICE)
        self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_route_to, "cninfo_meeting_notice_pdf")

    def test_short_annual_resolution_routes(self) -> None:
        """BD2E258：年度股东会决议公告 → shareholder_meeting_material。"""
        r = self._route(SHORT_ANNUAL_RESOLUTION)
        self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_short_legal_opinion_stays_announcement(self) -> None:
        """简称法律意见书不得抬成 shareholder_meeting_material。"""
        r = self._route(SHORT_LEGAL)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_short_meeting_materials_stay_announcement(self) -> None:
        """简称会议资料不得抬成 shareholder_meeting_material。"""
        r = self._route(SHORT_MATERIALS)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_full_form_not_regressed(self) -> None:
        """B-FM-18 股东大会决议 / 召开公告 / 通知路径不回退。"""
        for title in (FULL_RESOLUTION, FULL_CONVENING, FULL_NOTICE):
            with self.subTest(title=title[:40]):
                r = self._route(title)
                self.assertEqual(r.predicted_document_type, "shareholder_meeting_material")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_board_resolution_not_regressed(self) -> None:
        """董事会决议仍为 board_resolution。"""
        r = self._route(BOARD_RESOLUTION)
        self.assertEqual(r.predicted_document_type, "board_resolution")

    def test_helper_general_document_type_short_form(self) -> None:
        """直接锁测 `_general_document_type` 简称边角。"""
        patterns = ["公告", "决议", "股东大会", "股东会", "董事会", "监事会"]
        self.assertEqual(
            routing._general_document_type(SHORT_RESOLUTION, patterns),
            "shareholder_meeting_material",
        )
        self.assertEqual(
            routing._general_document_type(SHORT_NOTICE, patterns),
            "shareholder_meeting_material",
        )
        self.assertEqual(
            routing._general_document_type(SHORT_LEGAL, patterns),
            "announcement",
        )
        self.assertEqual(
            routing._general_document_type(SHORT_MATERIALS, patterns),
            "announcement",
        )
        self.assertEqual(
            routing._general_document_type(FULL_RESOLUTION, patterns),
            "shareholder_meeting_material",
        )

    def test_not_periodic_and_no_invented_section7_fp(self) -> None:
        """边角硬化不得误进 periodic，也不得新造 §7 FP 标签。"""
        for title in (
            SHORT_RESOLUTION,
            SHORT_NOTICE,
            SHORT_ANNUAL_RESOLUTION,
            SHORT_LEGAL,
            SHORT_MATERIALS,
            FULL_RESOLUTION,
            FULL_CONVENING,
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
