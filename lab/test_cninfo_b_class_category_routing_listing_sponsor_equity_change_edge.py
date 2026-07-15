"""
B 类 category routing — 「保荐书」/「权益变动报告书」document_type 边角锁测（B-FM-28）。

覆盖 harvest 已见但旧 `_general_document_type` 落 other 的标题：
- 「…可转换公司债券的上市保荐书（修订稿）」→ announcement（非 other）
- 「…简式权益变动报告书」→ announcement
- 核查意见 / 法律意见书 / 股东会决议 / 董事会决议 / 异常波动不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 verification_opinion / LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_listing_sponsor_equity_change_edge.py
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
LISTING_SPONSOR = (
    "国信证券股份有限公司关于石家庄尚太科技股份有限公司主板向不特定对象"
    "发行可转换公司债券的上市保荐书（修订稿）"
)  # BD2E252
EQUITY_CHANGE = "德林海简式权益变动报告书"  # BD2E482
VERIFICATION = (
    "华泰联合证券有限责任公司关于三六零安全科技股份有限公司"
    "使用自有资金支付募投项目部分款项并以募集资金等额置换的核查意见"
)
LEGAL_NON_MEETING = (
    "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书"
)
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
ABNORMAL = "股票交易异常波动公告"


class TestListingSponsorEquityChangeRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_listing_sponsor_announcement_not_other(self) -> None:
        """BD2E252：可转债上市保荐书 → announcement（闭合 other 误落）。"""
        r = self._route(LISTING_SPONSOR)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.predicted_classification, "general_announcement")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertNotEqual(r.predicted_document_type, "board_resolution")

    def test_equity_change_report_announcement(self) -> None:
        """BD2E482：简式权益变动报告书 → announcement。"""
        r = self._route(EQUITY_CHANGE)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")

    def test_verification_and_legal_not_regressed(self) -> None:
        """B-FM-26/27 法律意见 / 核查意见路径不回退。"""
        for title in (VERIFICATION, LEGAL_NON_MEETING):
            with self.subTest(title=title[:40]):
                r = self._route(title)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertNotEqual(r.predicted_document_type, "other")

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

    def test_helper_general_document_type_sponsor_equity(self) -> None:
        """直接锁测 `_general_document_type` 保荐书 / 权益变动报告书早退。"""
        patterns = ["公告", "决议", "股东大会", "股东会", "董事会", "监事会"]
        self.assertEqual(
            routing._general_document_type(LISTING_SPONSOR, patterns),
            "announcement",
        )
        self.assertEqual(
            routing._general_document_type(EQUITY_CHANGE, patterns),
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
            LISTING_SPONSOR,
            EQUITY_CHANGE,
            VERIFICATION,
            LEGAL_NON_MEETING,
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
