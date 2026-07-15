"""
B 类 category routing — 非标准审计意见 / 募集资金使用情况报告边角锁测（B-FM-32）。

覆盖 harvest 已见但旧逻辑落 other 的标题：
- 「…非标准审计意见…消除情况的专项说明」→ announcement（非 other；「非标准审计意见」≠「非标意见」）
- 「公司前次募集资金使用情况报告」→ announcement（非 other）
- 既有「非标意见」短串 §7 FP 仍走 excluded_from_periodic
- 不泛化裸「专项说明」；真·年度报告 / 法律意见 / 持续督导 / 股东会决议不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_nonstandard_audit_raised_funds_edge.py
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
NONSTANDARD_AUDIT = (
    "中兴华会计师事务所关于对永鼎股份2023年度财务报表出具非标准审计意见"
    "审计报告所涉及事项在2024年度消除情况的专项说明"
)  # BD2E366
RAISED_FUNDS = "公司前次募集资金使用情况报告"  # BD2E234
SHORT_FEIBIAO = "关于2024年年度报告非标意见涉及事项的专项说明"  # periodic_false_positive_021
BARE_ZHUANXIANG = "关于某事项的专项说明"  # 不得因泛化「专项说明」抬成 announcement
REAL_ANNUAL = "江苏恒立液压股份有限公司2024年年度报告"
LEGAL_NON_MEETING = (
    "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书"
)
SUPERVISION_ANNUAL = (
    "中国国际金融股份有限公司关于江苏恒立液压股份有限公司2024年度持续督导年度报告书"
)
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
# 含「审核意见」+「年度报告」：不得被本包误抬；保持既有 periodic 路径
SUPERVISORY_AUDIT_ON_ANNUAL = "监事会关于公司2024年年度报告的审核意见"  # BD2E501


class TestNonstandardAuditRaisedFundsRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_nonstandard_audit_announcement_not_other(self) -> None:
        """BD2E366：非标准审计意见消除专项说明 → announcement（闭合 other）。"""
        r = routing.route_title(NONSTANDARD_AUDIT, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertNotEqual(r.predicted_document_type, "annual_report")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        # 因 periodic exclusion 含「非标准审计意见」，可走 excluded_from_periodic 或 general
        self.assertIn(
            r.classification_status,
            ("classified_correctly", "title_excluded_from_periodic_but_routed"),
        )

    def test_raised_funds_usage_announcement_not_other(self) -> None:
        """BD2E234：前次募集资金使用情况报告 → announcement（闭合 other）。"""
        r = routing.route_title(RAISED_FUNDS, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")

    def test_short_feibiao_still_excluded_from_periodic(self) -> None:
        """既有「非标意见」短串仍走 excluded_from_periodic（§7 FP 不回退）。"""
        r = routing.route_title(SHORT_FEIBIAO, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.predicted_classification, "excluded_from_periodic_but_routed")
        self.assertEqual(r.false_positive_reason, "unrelated_announcement")
        self.assertIn("非标意见", r.matched_patterns)

    def test_bare_zhuanxiang_not_lifted(self) -> None:
        """裸「专项说明」不得因本包泛化抬成 announcement。"""
        r = routing.route_title(BARE_ZHUANXIANG, self.config)
        self.assertEqual(r.predicted_document_type, "other")

    def test_nonstandard_with_annual_report_substring_not_periodic(self) -> None:
        """含「年度报告」+「非标准审计意见」不得进 periodic。"""
        title = "关于2024年年度报告非标准审计意见涉及事项的专项说明"
        r = routing.route_title(title, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertNotEqual(r.predicted_document_type, "annual_report")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_supervisory_audit_on_annual_not_regressed_by_shenhe(self) -> None:
        """BD2E501：监事会年报审核意见 — 本包不扩「审核意见」，保持既有路径。"""
        r = routing.route_title(SUPERVISORY_AUDIT_ON_ANNUAL, self.config)
        # 既有：含「年度报告」且无排除 → annual_report；本包不得改成 other/announcement 早退
        self.assertEqual(r.predicted_document_type, "annual_report")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_prior_paths_not_regressed(self) -> None:
        r_annual = routing.route_title(REAL_ANNUAL, self.config)
        self.assertEqual(r_annual.predicted_document_type, "annual_report")
        r_legal = routing.route_title(LEGAL_NON_MEETING, self.config)
        self.assertEqual(r_legal.predicted_document_type, "announcement")
        r_sup = routing.route_title(SUPERVISION_ANNUAL, self.config)
        self.assertEqual(r_sup.predicted_document_type, "announcement")
        self.assertNotEqual(r_sup.predicted_document_type, "annual_report")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
