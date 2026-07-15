"""
B 类 category routing — 非会议类法律意见书 document_type 边角锁测（B-FM-26）。

覆盖 harvest 已见但旧 `_general_document_type` 落 other / 误抬会议材料的标题：
- 「…增持公司股份之法律意见书」→ announcement（非 other）
- 「…差异化分红的法律意见书」→ announcement
- 「…可转换公司债券的法律意见书」→ announcement
- 「…股东大会决议的法律意见书」→ announcement（不得抬成 shareholder_meeting_material）
- 会议类 known_001/002 路径与股东会决议 / 董事会决议不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 legal_opinion_known_001/002 LIVE_PASS。

运行：
    python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py
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
INCREASE_HOLDING = (
    "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书"
)  # BD2E079
DIFF_DIVIDEND = (
    "北京市通商律师事务所上海分所关于东浩兰生会展集团股份有限公司"
    "差异化分红的法律意见书"
)  # BD2E442
CONVERTIBLE_BOND = (
    "浙江六和律师事务所关于苏州天准科技股份有限公司"
    "向不特定对象发行可转换公司债券的法律意见书"
)  # BD2E472
MEETING_RESOLUTION_LEGAL = "关于公司2025年第一次临时股东大会决议的法律意见书"
MEETING_LEGAL_FULL = "2025年第一次临时股东大会的法律意见书"  # known_001
MEETING_LEGAL_SHORT = (
    "北京市星河律师事务所关于北京金自天正智能控制股份有限公司"
    "2024年年度股东会的法律意见书"
)  # known_002
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
ABNORMAL = "股票交易异常波动公告"


class TestLegalOpinionNonMeetingRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_increase_holding_legal_opinion_announcement_not_other(self) -> None:
        """BD2E079：增持法律意见书 → announcement（闭合 other 误落）。"""
        r = self._route(INCREASE_HOLDING)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.predicted_classification, "general_announcement")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertNotEqual(r.predicted_document_type, "shareholder_meeting_material")

    def test_diff_dividend_legal_opinion_announcement(self) -> None:
        """BD2E442：差异化分红法律意见书 → announcement。"""
        r = self._route(DIFF_DIVIDEND)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")

    def test_convertible_bond_legal_opinion_announcement(self) -> None:
        """BD2E472：可转债法律意见书 → announcement。"""
        r = self._route(CONVERTIBLE_BOND)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertNotEqual(r.predicted_document_type, "other")

    def test_meeting_resolution_legal_opinion_not_elevated(self) -> None:
        """含「决议」的会议法律意见不得抬成 shareholder_meeting_material。"""
        r = self._route(MEETING_RESOLUTION_LEGAL)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertNotEqual(r.predicted_document_type, "shareholder_meeting_material")

    def test_meeting_legal_opinions_not_regressed(self) -> None:
        """B-FM-25 会议法律意见书路径不回退。"""
        for title in (MEETING_LEGAL_FULL, MEETING_LEGAL_SHORT):
            with self.subTest(title=title[:40]):
                r = self._route(title)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_shareholder_and_board_not_regressed(self) -> None:
        """股东会决议 / 董事会决议路径不回退。"""
        r_sm = self._route(SM_RES)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = self._route(BOARD)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_abnormal_fluctuation_still_announcement(self) -> None:
        """异常波动公告仍走 announcement（本包不改其路由）。"""
        r = self._route(ABNORMAL)
        self.assertEqual(r.predicted_document_type, "announcement")

    def test_helper_general_document_type_non_meeting(self) -> None:
        """直接锁测 `_general_document_type` 非会议法律意见早退。"""
        patterns = ["公告", "决议", "股东大会", "股东会", "董事会", "监事会"]
        self.assertEqual(
            routing._general_document_type(INCREASE_HOLDING, patterns),
            "announcement",
        )
        self.assertEqual(
            routing._general_document_type(DIFF_DIVIDEND, patterns),
            "announcement",
        )
        self.assertEqual(
            routing._general_document_type(MEETING_RESOLUTION_LEGAL, patterns),
            "announcement",
        )
        self.assertEqual(
            routing._general_document_type(SM_RES, patterns),
            "shareholder_meeting_material",
        )
        self.assertEqual(
            routing._general_document_type(BOARD, patterns),
            "board_resolution",
        )

    def test_not_periodic_and_no_invented_section7_fp(self) -> None:
        """边角硬化不得误进 periodic，也不得新造 §7 FP 标签。"""
        for title in (
            INCREASE_HOLDING,
            DIFF_DIVIDEND,
            CONVERTIBLE_BOND,
            MEETING_RESOLUTION_LEGAL,
            MEETING_LEGAL_FULL,
            SM_RES,
            BOARD,
            ABNORMAL,
        ):
            with self.subTest(title=title[:40]):
                r = self._route(title)
                self.assertNotEqual(r.predicted_classification, "periodic_report")
                self.assertNotIn("announcement_preview", r.false_positive_reason or "")
                self.assertNotIn("wrong_company", r.false_positive_reason or "")


if __name__ == "__main__":
    unittest.main()
