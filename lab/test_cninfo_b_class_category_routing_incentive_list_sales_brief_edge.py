"""
B 类 category routing — 激励对象名单 / 销售简报边角锁测（B-FM-41）。

覆盖 harvest 已见但旧逻辑落 other 的标题：
- 「…激励对象名单…」→ announcement（非 other；窄；勿裸「名单」）
- 「…销售简报…」→ announcement（非 other；窄；勿裸「简报」）
- 裸「名单」/「简报」/「情况简报」不得因本包泛化抬成 announcement
- 对外担保情况简报 / ESG / 子公司管理制度 / 薪酬与考核方案不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_incentive_list_sales_brief_edge.py
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
MINGDAN = "英科再生资源股份有限公司2025年限制性股票激励计划激励对象名单（授予日）"  # BD2E484
JIANBAO = "2025年5月畜牧行业销售简报"  # BD2E210
BARE_MINGDAN = "某事项名单"  # 不得因裸「名单」抬成 announcement
BARE_JIANBAO = "某事项经营简报"  # 不得因裸「简报」抬成 announcement
BARE_QINGKUANG = "某事项情况简报"  # 不得因裸「情况简报」抬成 announcement
GUARANTEE_BRIEF = "光明地产关于对外担保的情况简报"
ESG = "2024 Environmental, Social and Corporate Governance Report"
SUBSIDIARY = "分、子公司管理制度（2025年6月）"
XINCHOU = "利尔化学股份有限公司2025年度经营团队薪酬与考核方案"
GUARANTEE_SYS = "海量数据对外担保管理制度"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"


class TestIncentiveListSalesBriefRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_incentive_object_list_announcement_not_other(self) -> None:
        """BD2E484：激励对象名单 → announcement（闭合 other）。"""
        r = routing.route_title(MINGDAN, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("激励对象名单", r.matched_patterns)

    def test_sales_brief_announcement_not_other(self) -> None:
        """BD2E210：销售简报 → announcement（闭合 other）。"""
        r = routing.route_title(JIANBAO, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("销售简报", r.matched_patterns)

    def test_bare_list_or_brief_not_lifted(self) -> None:
        """裸「名单」/「简报」/「情况简报」不得因本包泛化抬成 announcement。"""
        for title in (BARE_MINGDAN, BARE_JIANBAO, BARE_QINGKUANG):
            with self.subTest(title=title):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "other")

    def test_guarantee_brief_distinct_from_sales_brief(self) -> None:
        """对外担保的情况简报仍 announcement，且与销售简报 pattern 可区分。"""
        r = routing.route_title(GUARANTEE_BRIEF, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertIn("对外担保的情况简报", r.matched_patterns)
        self.assertNotIn("销售简报", r.matched_patterns)

    def test_prior_paths_not_regressed(self) -> None:
        r_esg = routing.route_title(ESG, self.config)
        self.assertEqual(r_esg.predicted_document_type, "announcement")
        r_sub = routing.route_title(SUBSIDIARY, self.config)
        self.assertEqual(r_sub.predicted_document_type, "announcement")
        r_xc = routing.route_title(XINCHOU, self.config)
        self.assertEqual(r_xc.predicted_document_type, "announcement")
        r_gs = routing.route_title(GUARANTEE_SYS, self.config)
        self.assertEqual(r_gs.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
