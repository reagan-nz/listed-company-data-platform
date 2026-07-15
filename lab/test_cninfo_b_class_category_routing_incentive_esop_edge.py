"""
B 类 category routing — 激励买卖自查报告 / 员工持股计划边角锁测（B-FM-35）。

覆盖 harvest 已见但旧逻辑落 other 的标题：
- 「…买卖公司股票的自查报告」→ announcement（非 other；窄；勿裸「自查报告」）
- 「…员工持股计划…」→ announcement（非 other）
- 裸「自查报告」不得因本包泛化抬成 announcement
- 名单 / 简报 / 裸管理制度仍落 other（分子公司/薪酬由 B-FM-39 承接）
- 资产评估说明 / 独立审计报告 / 股东会决议不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_incentive_esop_edge.py
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
SELF_INSPECT = (
    "关于2024年限制性股票激励计划内幕信息知情人及激励对象买卖公司股票的自查报告"
)  # BD2E087
ESOP = "第二期员工持股计划（草案）(修订稿）"  # BD2E062
BARE_ZICHA = "关于某事项的自查报告"  # 不得因泛化「自查报告」抬成 announcement
ASSET_VAL = (
    "舍得酒业拟进行资产收购所涉及的位于遂宁市射洪县沱牌镇四处住宅用、"
    "商业用房地产市场价值资产评估说明"
)
AUDIT_STANDALONE = "迎驾贡酒2024年审计报告-容诚审字[2025]230Z0521号（修订版）"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
BARE_ZHIDU = "某事项管理制度"  # 裸管理制度仍 other（B-FM-39 未泛化）
MINGDAN = "英科再生资源股份有限公司2025年限制性股票激励计划激励对象名单（授予日）"
JIANBAO = "2025年5月畜牧行业销售简报"


class TestIncentiveEsopRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_incentive_trading_self_inspection_announcement_not_other(self) -> None:
        """BD2E087：买卖公司股票的自查报告 → announcement（闭合 other）。"""
        r = routing.route_title(SELF_INSPECT, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("买卖公司股票的自查报告", r.matched_patterns)

    def test_employee_stock_ownership_plan_announcement_not_other(self) -> None:
        """BD2E062：员工持股计划 → announcement（闭合 other）。"""
        r = routing.route_title(ESOP, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("员工持股计划", r.matched_patterns)

    def test_bare_zicha_report_not_lifted(self) -> None:
        """裸「自查报告」不得因本包泛化抬成 announcement。"""
        r = routing.route_title(BARE_ZICHA, self.config)
        self.assertEqual(r.predicted_document_type, "other")

    def test_low_value_edges_still_other(self) -> None:
        """名单/简报/裸管理制度仍落 other（本包不硬推）。"""
        for title in (BARE_ZHIDU, MINGDAN, JIANBAO):
            with self.subTest(title=title):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_av = routing.route_title(ASSET_VAL, self.config)
        self.assertEqual(r_av.predicted_document_type, "announcement")
        r_ar = routing.route_title(AUDIT_STANDALONE, self.config)
        self.assertEqual(r_ar.predicted_document_type, "announcement")
        self.assertNotEqual(r_ar.predicted_document_type, "annual_report")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
