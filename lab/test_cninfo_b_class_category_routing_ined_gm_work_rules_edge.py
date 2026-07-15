"""
B 类 category routing — 独立非执行董事工作制度 / 总经理工作细则边角锁测（B-FM-37）。

覆盖 harvest 已见但旧逻辑落 other 的标题：
- 「…独立非执行董事工作制度…」→ announcement（非 other；窄；勿裸「工作制度」）
- 「…总经理工作细则…」→ announcement（非 other；窄；勿裸「工作细则」）
- 裸「工作制度」/「工作细则」不得因本包泛化抬成 announcement
- 货币资金管理制度 / 薪酬 / 名单 / 简报 / ESG 仍落 other
- 公司章程 / 募资管理制度 / 激励买卖自查 / ESOP 不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_ined_gm_work_rules_edge.py
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
INED = "株洲中车时代电气股份有限公司独立非执行董事工作制度"  # BD2E181
GM_RULES = "中盐内蒙古化工股份有限公司总经理工作细则（2025年6月修订）"  # BD2E384
BARE_WORK_SYS = "某委员会工作制度"  # 不得因裸「工作制度」抬成 announcement
BARE_RULES = "财务负责人工作细则"  # 非总经理；不得因裸「工作细则」抬成 announcement
BARE_ZHIDU = "货币资金管理制度"  # 一般管理制度仍 other
XINCHOU = "利尔化学股份有限公司2025年度经营团队薪酬与考核方案"
MINGDAN = "英科再生资源股份有限公司2025年限制性股票激励计划激励对象名单（授予日）"
JIANBAO = "2025年5月畜牧行业销售简报"
ESG = "2024 Environmental, Social and Corporate Governance Report"
ARTICLES = "安徽古麒绒材股份有限公司章程（2025年6月修订）"
RAISED_SYS = "广西绿城水务股份有限公司募集资金管理制度（2025年6月修订）"
SELF_INSPECT = (
    "关于2024年限制性股票激励计划内幕信息知情人及激励对象买卖公司股票的自查报告"
)
ESOP = "第二期员工持股计划（草案）(修订稿）"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
IND_MEETING = "金枫酒业2025年第二次独立董事专门会议的审核意见"


class TestInedGmWorkRulesRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_ined_work_system_announcement_not_other(self) -> None:
        """BD2E181：独立非执行董事工作制度 → announcement（闭合 other）。"""
        r = routing.route_title(INED, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("独立非执行董事工作制度", r.matched_patterns)

    def test_gm_work_rules_announcement_not_other(self) -> None:
        """BD2E384：总经理工作细则 → announcement（闭合 other）。"""
        r = routing.route_title(GM_RULES, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("总经理工作细则", r.matched_patterns)

    def test_bare_work_system_or_rules_not_lifted(self) -> None:
        """裸「工作制度」/非总经理「工作细则」不得因本包泛化抬成 announcement。"""
        r_bare = routing.route_title(BARE_WORK_SYS, self.config)
        self.assertEqual(r_bare.predicted_document_type, "other")
        r_rules = routing.route_title(BARE_RULES, self.config)
        self.assertEqual(r_rules.predicted_document_type, "other")

    def test_remaining_low_value_edges_still_other(self) -> None:
        """货币资金管理制度/薪酬/名单/简报/ESG 仍落 other（本包不硬推）。"""
        for title in (BARE_ZHIDU, XINCHOU, MINGDAN, JIANBAO, ESG):
            with self.subTest(title=title):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_art = routing.route_title(ARTICLES, self.config)
        self.assertEqual(r_art.predicted_document_type, "announcement")
        r_rs = routing.route_title(RAISED_SYS, self.config)
        self.assertEqual(r_rs.predicted_document_type, "announcement")
        r_si = routing.route_title(SELF_INSPECT, self.config)
        self.assertEqual(r_si.predicted_document_type, "announcement")
        r_esop = routing.route_title(ESOP, self.config)
        self.assertEqual(r_esop.predicted_document_type, "announcement")
        r_ind = routing.route_title(IND_MEETING, self.config)
        self.assertEqual(r_ind.predicted_document_type, "announcement")
        self.assertIn("独立董事专门会议的审核意见", r_ind.matched_patterns)
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
