"""
B 类 category routing — 「受托管理事务报告」/「跟踪评级报告」document_type 边角锁测（B-FM-29）。

覆盖 harvest 已见但旧 `_general_document_type` 落 other 的标题：
- 「…可转换公司债券受托管理事务报告（2024年度）」→ announcement（非 other）
- 「…可转换公司债券定期跟踪评级报告」→ announcement
- 保荐书 / 权益变动 / 核查意见 / 法律意见书 / 股东会决议 / 董事会决议不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 listing_sponsor / equity_change / LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py
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
BOND_TRUSTEE = (
    "申港证券股份有限公司关于三羊马(重庆)物流股份有限公司向不特定对象"
    "发行可转换公司债券受托管理事务报告（2024年度）"
)  # BD2E254
TRACKING_RATING = (
    "2020年浙江华海药业股份有限公司公开发行可转换公司债券定期跟踪评级报告"
)  # BD2E408
LISTING_SPONSOR = (
    "国信证券股份有限公司关于石家庄尚太科技股份有限公司主板向不特定对象"
    "发行可转换公司债券的上市保荐书（修订稿）"
)
EQUITY_CHANGE = "德林海简式权益变动报告书"
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


class TestBondTrusteeRatingRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_bond_trustee_announcement_not_other(self) -> None:
        """BD2E254：可转债受托管理事务报告 → announcement（闭合 other 误落）。"""
        r = routing.route_title(BOND_TRUSTEE, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")

    def test_tracking_rating_announcement_not_other(self) -> None:
        """BD2E408：定期跟踪评级报告 → announcement。"""
        r = routing.route_title(TRACKING_RATING, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")

    def test_extra_harvest_titles_not_other(self) -> None:
        extras = (
            "山西美锦能源股份有限公司公开发行可转换公司债券2024年度受托管理事务报告",
            "立讯精密工业股份有限公司公开发行可转换公司债券2025年跟踪评级报告",
            "华兴源创：苏州华兴源创科技股份有限公司向不特定对象"
            "发行可转换公司债券受托管理事务报告（2024年度）",
        )
        for title in extras:
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertNotEqual(r.predicted_document_type, "other")

    def test_prior_edges_not_regressed(self) -> None:
        for title, expected in (
            (LISTING_SPONSOR, "announcement"),
            (EQUITY_CHANGE, "announcement"),
            (VERIFICATION, "announcement"),
            (LEGAL_NON_MEETING, "announcement"),
            (SM_RES, "shareholder_meeting_material"),
            (BOARD, "board_resolution"),
            (ABNORMAL, "announcement"),
        ):
            with self.subTest(title=title[:30]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, expected)
                self.assertNotEqual(r.predicted_document_type, "other")

    def test_general_document_type_early_exit(self) -> None:
        """直接锁测 `_general_document_type` 受托管理 / 跟踪评级早退。"""
        patterns = (
            self.config.get("categories", {})
            .get("general_announcement", {})
            .get("positive_patterns")
            or []
        )
        self.assertEqual(
            routing._general_document_type(BOND_TRUSTEE, patterns), "announcement"
        )
        self.assertEqual(
            routing._general_document_type(TRACKING_RATING, patterns), "announcement"
        )
        self.assertIn("受托管理事务报告", patterns)
        self.assertIn("跟踪评级报告", patterns)


if __name__ == "__main__":
    unittest.main()
