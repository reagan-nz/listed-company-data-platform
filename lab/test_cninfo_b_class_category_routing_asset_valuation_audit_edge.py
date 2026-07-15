"""
B 类 category routing — 资产评估说明 / 独立审计报告边角锁测（B-FM-34）。

覆盖 harvest 已见但旧逻辑落 other 的标题：
- 「…资产评估说明」→ announcement（非 other；窄；勿裸「说明」）
- 「…审计报告…」（无「年度报告」/「年报」）→ announcement（非 other）
- 「…年度报告审计报告」/「…年报审计报告」仍走 periodic annual_report
- 裸「说明」不得因本包泛化抬成 announcement
- 真·年度报告 / 独立董事审核意见 / 非标准审计意见 / 股东会决议不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_asset_valuation_audit_edge.py
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
ASSET_VAL = (
    "舍得酒业拟进行资产收购所涉及的位于遂宁市射洪县沱牌镇四处住宅用、"
    "商业用房地产市场价值资产评估说明"
)  # BD2E430
AUDIT_STANDALONE = "迎驾贡酒2024年审计报告-容诚审字[2025]230Z0521号（修订版）"  # BD2E798
BARE_SHUOMING = "关于某事项的说明"  # 不得因泛化「说明」抬成 announcement
ANNUAL_AUDIT = "天健会计师事务所关于新安股份2024年年度报告审计报告"
NIANBAO_AUDIT = "天健审〔2025〕11-195号 川网传媒2024年报审计报告"
REAL_ANNUAL = "江苏恒立液压股份有限公司2024年年度报告"
IND_MEETING = "金枫酒业2025年第二次独立董事专门会议的审核意见"
NONSTANDARD = (
    "中兴华会计师事务所关于对永鼎股份2023年度财务报表出具非标准审计意见"
    "审计报告所涉及事项在2024年度消除情况的专项说明"
)
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
ZHIDU = "货币资金管理制度"


class TestAssetValuationAuditRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_asset_valuation_explanation_announcement_not_other(self) -> None:
        """BD2E430：资产评估说明 → announcement（闭合 other）。"""
        r = routing.route_title(ASSET_VAL, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertNotEqual(r.predicted_document_type, "annual_report")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("资产评估说明", r.matched_patterns)

    def test_standalone_audit_report_announcement_not_other(self) -> None:
        """BD2E798：独立审计报告（无年报字样）→ announcement（闭合 other）。"""
        r = routing.route_title(AUDIT_STANDALONE, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertNotEqual(r.predicted_document_type, "annual_report")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("审计报告", r.matched_patterns)

    def test_bare_shuoming_not_lifted(self) -> None:
        """裸「说明」不得因本包泛化抬成 announcement。"""
        r = routing.route_title(BARE_SHUOMING, self.config)
        self.assertEqual(r.predicted_document_type, "other")

    def test_annual_report_audit_still_periodic(self) -> None:
        """含「年度报告」的审计报告仍走 periodic（Priority 3 先于 general）。"""
        r = routing.route_title(ANNUAL_AUDIT, self.config)
        self.assertEqual(r.predicted_document_type, "annual_report")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_nianbao_audit_still_periodic(self) -> None:
        """含「年报」的审计报告仍走 periodic。"""
        r = routing.route_title(NIANBAO_AUDIT, self.config)
        self.assertEqual(r.predicted_document_type, "annual_report")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_general_system_still_other(self) -> None:
        """一般管理制度低价值边角仍落 other（本包不硬推）。"""
        r = routing.route_title(ZHIDU, self.config)
        self.assertEqual(r.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_annual = routing.route_title(REAL_ANNUAL, self.config)
        self.assertEqual(r_annual.predicted_document_type, "annual_report")
        r_ind = routing.route_title(IND_MEETING, self.config)
        self.assertEqual(r_ind.predicted_document_type, "announcement")
        r_ns = routing.route_title(NONSTANDARD, self.config)
        self.assertEqual(r_ns.predicted_document_type, "announcement")
        self.assertNotEqual(r_ns.predicted_document_type, "other")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
