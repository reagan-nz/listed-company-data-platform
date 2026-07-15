"""
B 类 category routing — 子公司管理制度 / 薪酬与考核方案边角锁测（B-FM-39）。

覆盖 harvest 已见但旧逻辑落 other 的标题：
- 「…分、子公司管理制度…」→ announcement（非 other；窄；勿裸「管理制度」）
- 「…薪酬与考核方案…」→ announcement（非 other；窄；勿裸「薪酬」）
- 裸「管理制度」不得因本包泛化抬成 announcement
- 名单 / 简报 / ESG / 对外担保情况简报仍落 other
- 货币资金 / 对外担保 / 章程 / 募资管理制度 / 独立非执行董事工作制度 / 总经理工作细则不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_subsidiary_compensation_edge.py
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
SUBSIDIARY = "分、子公司管理制度（2025年6月）"  # BD2E342
XINCHOU = "利尔化学股份有限公司2025年度经营团队薪酬与考核方案"  # BD2E296
BARE_SYS = "某事项管理制度"  # 不得因裸「管理制度」抬成 announcement
MINGDAN = "英科再生资源股份有限公司2025年限制性股票激励计划激励对象名单（授予日）"
JIANBAO = "2025年5月畜牧行业销售简报"
BARE_MINGDAN = "某事项名单"
BARE_JIANBAO = "某事项经营简报"
GUARANTEE_BRIEF = "光明地产关于对外担保的情况简报"
ESG = "2024 Environmental, Social and Corporate Governance Report"
MONETARY = "货币资金管理制度"
GUARANTEE = "海量数据对外担保管理制度"
ARTICLES = "安徽古麒绒材股份有限公司章程（2025年6月修订）"
RAISED_SYS = "广西绿城水务股份有限公司募集资金管理制度（2025年6月修订）"
INED = "株洲中车时代电气股份有限公司独立非执行董事工作制度"
GM_RULES = "中盐内蒙古化工股份有限公司总经理工作细则（2025年6月修订）"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"


class TestSubsidiaryCompensationRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_subsidiary_system_announcement_not_other(self) -> None:
        """BD2E342：分、子公司管理制度 → announcement（闭合 other）。"""
        r = routing.route_title(SUBSIDIARY, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("子公司管理制度", r.matched_patterns)

    def test_compensation_plan_announcement_not_other(self) -> None:
        """BD2E296：薪酬与考核方案 → announcement（闭合 other）。"""
        r = routing.route_title(XINCHOU, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("薪酬与考核方案", r.matched_patterns)

    def test_bare_system_not_lifted(self) -> None:
        """裸「管理制度」不得因本包泛化抬成 announcement。"""
        r_bare = routing.route_title(BARE_SYS, self.config)
        self.assertEqual(r_bare.predicted_document_type, "other")

    def test_remaining_bare_still_other(self) -> None:
        """裸名单/简报仍落 other（激励对象名单/销售简报由 B-FM-41 承接）。"""
        for title in (BARE_MINGDAN, BARE_JIANBAO):
            with self.subTest(title=title):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "other")
        # B-FM-41 承接后 harvest 标题应为 announcement（不回退）
        for title in (MINGDAN, JIANBAO):
            with self.subTest(title=title):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")

    def test_prior_paths_not_regressed(self) -> None:
        r_m = routing.route_title(MONETARY, self.config)
        self.assertEqual(r_m.predicted_document_type, "announcement")
        r_g = routing.route_title(GUARANTEE, self.config)
        self.assertEqual(r_g.predicted_document_type, "announcement")
        r_art = routing.route_title(ARTICLES, self.config)
        self.assertEqual(r_art.predicted_document_type, "announcement")
        r_rs = routing.route_title(RAISED_SYS, self.config)
        self.assertEqual(r_rs.predicted_document_type, "announcement")
        r_ined = routing.route_title(INED, self.config)
        self.assertEqual(r_ined.predicted_document_type, "announcement")
        r_gm = routing.route_title(GM_RULES, self.config)
        self.assertEqual(r_gm.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
