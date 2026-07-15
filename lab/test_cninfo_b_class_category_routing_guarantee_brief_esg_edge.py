"""
B 类 category routing — 对外担保情况简报 / 英文 ESG 边角锁测（B-FM-40）。

覆盖 harvest 已见但旧逻辑落 other 的标题：
- 「…对外担保的情况简报…」→ announcement（非 other；窄；≠对外担保管理制度）
- 「…Environmental, Social and Corporate Governance…」→ announcement（非 other；窄）
- 裸「简报」/「情况简报」/「ESG」不得因本包泛化抬成 announcement
- 激励名单 / 销售简报仍落 other
- 子公司管理制度 / 薪酬与考核方案 / 对外担保管理制度不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_guarantee_brief_esg_edge.py
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
GUARANTEE_BRIEF = "光明地产关于对外担保的情况简报"  # BD2E432
ESG = "2024 Environmental, Social and Corporate Governance Report"  # BD2E166
BARE_JIANBAO = "某行业销售简报"  # 不得因裸「简报」抬成 announcement
BARE_QINGKUANG = "某事项情况简报"  # 不得因裸「情况简报」抬成 announcement
BARE_ESG = "某公司 ESG 专项说明"  # 不得因裸「ESG」抬成 announcement
MINGDAN = "英科再生资源股份有限公司2025年限制性股票激励计划激励对象名单（授予日）"
JIANBAO = "2025年5月畜牧行业销售简报"
GUARANTEE_SYS = "海量数据对外担保管理制度"
SUBSIDIARY = "分、子公司管理制度（2025年6月）"
XINCHOU = "利尔化学股份有限公司2025年度经营团队薪酬与考核方案"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"


class TestGuaranteeBriefEsgRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_guarantee_brief_announcement_not_other(self) -> None:
        """BD2E432：对外担保的情况简报 → announcement（闭合 other）。"""
        r = routing.route_title(GUARANTEE_BRIEF, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("对外担保的情况简报", r.matched_patterns)

    def test_esg_report_announcement_not_other(self) -> None:
        """BD2E166：英文 ESG 报告 → announcement（闭合 other）。"""
        r = routing.route_title(ESG, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("Corporate Governance Report", r.matched_patterns)

    def test_bare_brief_or_esg_not_lifted(self) -> None:
        """裸「简报」/「情况简报」/「ESG」不得因本包泛化抬成 announcement。"""
        for title in (BARE_JIANBAO, BARE_QINGKUANG, BARE_ESG):
            with self.subTest(title=title):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "other")

    def test_remaining_low_value_still_other(self) -> None:
        """激励名单/销售简报仍落 other（本包不硬推）。"""
        for title in (MINGDAN, JIANBAO):
            with self.subTest(title=title):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_gs = routing.route_title(GUARANTEE_SYS, self.config)
        self.assertEqual(r_gs.predicted_document_type, "announcement")
        self.assertIn("对外担保管理制度", r_gs.matched_patterns)
        r_sub = routing.route_title(SUBSIDIARY, self.config)
        self.assertEqual(r_sub.predicted_document_type, "announcement")
        r_xc = routing.route_title(XINCHOU, self.config)
        self.assertEqual(r_xc.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
