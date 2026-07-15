"""
B 类 category routing — 公司章程 / 募集资金管理制度边角锁测（B-FM-36）。

覆盖 harvest 已见但旧逻辑落 other 的标题：
- 「…公司章程…」→ announcement（非 other；窄；勿裸「章程」）
- 「…募集资金管理制度…」→ announcement（非 other；窄；勿裸「管理制度」）
- 裸「章程」/「管理制度」不得因本包泛化抬成 announcement
- 名单 / 简报 / ESG / 裸管理制度仍落 other（分子公司/薪酬由 B-FM-39 承接）
- 激励买卖自查 / ESOP / 资产评估 / 股东会决议不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_articles_raised_funds_system_edge.py
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
ARTICLES = "安徽古麒绒材股份有限公司章程（2025年6月修订）"  # BD2E262
RAISED_SYS = "广西绿城水务股份有限公司募集资金管理制度（2025年6月修订）"  # BD2E756
BARE_ZHANGCHENG = "某事项章程修订说明"  # 不得因裸「章程」抬成 announcement
BARE_ZHIDU = "某事项管理制度"  # 裸管理制度仍 other（B-FM-39 未泛化）
MINGDAN = "英科再生资源股份有限公司2025年限制性股票激励计划激励对象名单（授予日）"
JIANBAO = "2025年5月畜牧行业销售简报"
ESG = "2024 Environmental, Social and Corporate Governance Report"
SELF_INSPECT = (
    "关于2024年限制性股票激励计划内幕信息知情人及激励对象买卖公司股票的自查报告"
)
ESOP = "第二期员工持股计划（草案）(修订稿）"
ASSET_VAL = (
    "舍得酒业拟进行资产置换所涉及的位于遂宁市射洪县沱牌镇四处住宅用、"
    "商业用房地产市场价值资产评估说明"
)
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
RAISED_USAGE = "公司前次募集资金使用情况报告"


class TestArticlesRaisedFundsSystemRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_company_articles_announcement_not_other(self) -> None:
        """BD2E262：公司章程 → announcement（闭合 other）。"""
        r = routing.route_title(ARTICLES, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("公司章程", r.matched_patterns)

    def test_raised_funds_management_system_announcement_not_other(self) -> None:
        """BD2E756：募集资金管理制度 → announcement（闭合 other）。"""
        r = routing.route_title(RAISED_SYS, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("募集资金管理制度", r.matched_patterns)

    def test_bare_zhangcheng_or_general_system_not_lifted(self) -> None:
        """裸「章程」/一般「管理制度」不得因本包泛化抬成 announcement。"""
        r_bare = routing.route_title(BARE_ZHANGCHENG, self.config)
        self.assertEqual(r_bare.predicted_document_type, "other")
        r_sys = routing.route_title(BARE_ZHIDU, self.config)
        self.assertEqual(r_sys.predicted_document_type, "other")

    def test_remaining_low_value_edges_still_other(self) -> None:
        """激励名单/销售简报仍落 other（ESG 由 B-FM-40 承接）。"""
        for title in (MINGDAN, JIANBAO):
            with self.subTest(title=title):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_si = routing.route_title(SELF_INSPECT, self.config)
        self.assertEqual(r_si.predicted_document_type, "announcement")
        r_esop = routing.route_title(ESOP, self.config)
        self.assertEqual(r_esop.predicted_document_type, "announcement")
        r_av = routing.route_title(ASSET_VAL, self.config)
        self.assertEqual(r_av.predicted_document_type, "announcement")
        r_ru = routing.route_title(RAISED_USAGE, self.config)
        self.assertEqual(r_ru.predicted_document_type, "announcement")
        self.assertIn("募集资金使用情况报告", r_ru.matched_patterns)
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
