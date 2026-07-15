"""
B 类 category routing — 「核查意见」document_type 边角锁测（B-FM-27）。

覆盖 harvest 已见但旧 `_general_document_type` 落 other 的标题：
- 「…募集资金等额置换的核查意见」→ announcement（非 other）
- 「…限售股上市流通的核查意见」→ announcement
- 「…募集资金…核查意见」（结项/补流变体）→ announcement
- 监事会激励名单核查意见 → announcement（非 board_resolution）
- 法律意见书 / 股东会决议 / 董事会决议 / 异常波动不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 legal_opinion / LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_verification_opinion_edge.py
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
FUND_REPLACE = (
    "华泰联合证券有限责任公司关于三六零安全科技股份有限公司"
    "使用自有资金支付募投项目部分款项并以募集资金等额置换的核查意见"
)  # BD2E172
LOCKUP = (
    "中信建投证券股份有限公司关于北京福元医药股份有限公司"
    "首次公开发行限售股上市流通的核查意见"
)  # BD2E466
FUND_CLOSEOUT = (
    "国泰海通证券股份有限公司关于河南通达电缆股份有限公司"
    "募集资金投资项目结项并将节余募集资金永久补充流动资金的核查意见"
)  # BD2E524
SUPERVISORY_LIST = (
    "监事会关于公司2025年限制性股票激励计划激励对象名单的核查意见及公示情况说明"
)  # BD2E550
LEGAL_NON_MEETING = (
    "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书"
)
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
ABNORMAL = "股票交易异常波动公告"


class TestVerificationOpinionRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_fund_replace_verification_announcement_not_other(self) -> None:
        """BD2E172：募资置换核查意见 → announcement（闭合 other 误落）。"""
        r = self._route(FUND_REPLACE)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.predicted_classification, "general_announcement")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertNotEqual(r.predicted_document_type, "board_resolution")

    def test_lockup_verification_announcement(self) -> None:
        """BD2E466：限售流通核查意见 → announcement。"""
        r = self._route(LOCKUP)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertNotEqual(r.predicted_document_type, "other")

    def test_fund_closeout_verification_announcement(self) -> None:
        """BD2E524：募资结项核查意见 → announcement。"""
        r = self._route(FUND_CLOSEOUT)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertNotEqual(r.predicted_document_type, "other")

    def test_supervisory_list_verification_announcement(self) -> None:
        """BD2E550：监事会激励名单核查意见 → announcement（非 board_resolution）。"""
        r = self._route(SUPERVISORY_LIST)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertNotEqual(r.predicted_document_type, "board_resolution")
        self.assertNotEqual(r.predicted_document_type, "other")

    def test_legal_opinion_not_regressed(self) -> None:
        """B-FM-26 非会议法律意见书路径不回退。"""
        r = self._route(LEGAL_NON_MEETING)
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

    def test_helper_general_document_type_verification(self) -> None:
        """直接锁测 `_general_document_type` 核查意见早退。"""
        patterns = ["公告", "决议", "股东大会", "股东会", "董事会", "监事会"]
        self.assertEqual(
            routing._general_document_type(FUND_REPLACE, patterns),
            "announcement",
        )
        self.assertEqual(
            routing._general_document_type(LOCKUP, patterns),
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
            FUND_REPLACE,
            LOCKUP,
            FUND_CLOSEOUT,
            SUPERVISORY_LIST,
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
