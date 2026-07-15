"""
B 类 category routing — 独立董事专门会议审核意见 / 提名人声明边角锁测（B-FM-33）。

覆盖 harvest 已见但旧逻辑落 other 的标题：
- 「…独立董事专门会议的审核意见」→ announcement（非 other；窄；勿裸「审核意见」）
- 「独立董事提名人声明与承诺…」→ announcement（非 other）
- 监事会「…年度报告的审核意见」仍走 periodic annual_report（BD2E501 不回退）
- 裸「审核意见」不得因本包泛化抬成 announcement
- 真·年度报告 / 法律意见 / 非标准审计意见 / 股东会决议不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_ind_director_governance_edge.py
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
MEETING_REVIEW = "金枫酒业2025年第二次独立董事专门会议的审核意见"  # BD2E426
NOMINEE_DECL = "独立董事提名人声明与承诺（张永炬）"  # BD2E264
BARE_SHENHE = "关于某事项的审核意见"  # 不得因泛化「审核意见」抬成 announcement
SUPERVISORY_AUDIT_ON_ANNUAL = "监事会关于公司2024年年度报告的审核意见"  # BD2E501
BOARD_AUDIT_ON_ANNUAL = "董事会关于年度报告的审核意见"
REAL_ANNUAL = "江苏恒立液压股份有限公司2024年年度报告"
LEGAL_NON_MEETING = (
    "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书"
)
NONSTANDARD = (
    "中兴华会计师事务所关于对永鼎股份2023年度财务报表出具非标准审计意见"
    "审计报告所涉及事项在2024年度消除情况的专项说明"
)
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
BARE_ZHIDU = "某事项管理制度"  # 裸管理制度仍 other（B-FM-39 未泛化）


class TestIndDirectorGovernanceRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_meeting_review_announcement_not_other(self) -> None:
        """BD2E426：独立董事专门会议的审核意见 → announcement（闭合 other）。"""
        r = routing.route_title(MEETING_REVIEW, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertNotEqual(r.predicted_document_type, "annual_report")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("独立董事专门会议的审核意见", r.matched_patterns)

    def test_nominee_declaration_announcement_not_other(self) -> None:
        """BD2E264：独立董事提名人声明与承诺 → announcement（闭合 other）。"""
        r = routing.route_title(NOMINEE_DECL, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("独立董事提名人声明与承诺", r.matched_patterns)

    def test_bare_shenhe_not_lifted(self) -> None:
        """裸「审核意见」不得因本包泛化抬成 announcement。"""
        r = routing.route_title(BARE_SHENHE, self.config)
        self.assertEqual(r.predicted_document_type, "other")

    def test_supervisory_audit_on_annual_not_regressed(self) -> None:
        """BD2E501：监事会年报审核意见 — 本包不扩裸「审核意见」，保持 periodic。"""
        r = routing.route_title(SUPERVISORY_AUDIT_ON_ANNUAL, self.config)
        self.assertEqual(r.predicted_document_type, "annual_report")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_board_audit_on_annual_still_periodic(self) -> None:
        """董事会年报审核意见仍走 periodic（含「年度报告」）。"""
        r = routing.route_title(BOARD_AUDIT_ON_ANNUAL, self.config)
        self.assertEqual(r.predicted_document_type, "annual_report")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_general_system_still_other(self) -> None:
        """裸管理制度仍落 other（本包不硬推；勿泛化）。"""
        r = routing.route_title(BARE_ZHIDU, self.config)
        self.assertEqual(r.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_annual = routing.route_title(REAL_ANNUAL, self.config)
        self.assertEqual(r_annual.predicted_document_type, "annual_report")
        r_legal = routing.route_title(LEGAL_NON_MEETING, self.config)
        self.assertEqual(r_legal.predicted_document_type, "announcement")
        r_ns = routing.route_title(NONSTANDARD, self.config)
        self.assertEqual(r_ns.predicted_document_type, "announcement")
        self.assertNotEqual(r_ns.predicted_document_type, "other")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
