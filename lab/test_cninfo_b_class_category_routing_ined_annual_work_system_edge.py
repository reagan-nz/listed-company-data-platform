"""
B 类 category routing — 独立董事年报/年度报告工作制度边角锁测（B-FM-44）。

覆盖 harvest 已见但旧逻辑误进 periodic 的标题：
- 「独立董事年度报告工作制度」→ announcement（非 annual_report / periodic）
- 「独立董事年报工作制度」→ announcement（非 annual_report / periodic）
- 裸「工作制度」/「年报」不得因本包泛化抬成 announcement
- 真·年度报告 / 独立非执行董事工作制度 / 提名人声明 / 专门会议不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_ined_annual_work_system_edge.py
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
INED_ANNUAL_SYS = "独立董事年度报告工作制度"  # BD2E028
INED_NIANBAO_SYS = "独立董事年报工作制度"  # BD2E695
BARE_WORK_SYS = "某委员会工作制度"  # 不得因裸「工作制度」抬成 announcement
BARE_NIANBAO = "某事项年报说明"  # 不得因裸「年报」抬成 announcement（仍可 periodic）
REAL_ANNUAL = "江苏恒立液压股份有限公司2024年年度报告"
INED_NED = "株洲中车时代电气股份有限公司独立非执行董事工作制度"
IND_NOMINEE = "独立董事提名人声明与承诺（张永炬）"
IND_MEETING = "金枫酒业2025年第二次独立董事专门会议的审核意见"
GM_RULES = "中盐内蒙古化工股份有限公司总经理工作细则（2025年6月修订）"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
AUDIT_WITH_NIANBAO = "天健审〔2025〕11-195号 川网传媒2024年报审计报告"
AUDIT_CLEAN = "迎驾贡酒2024年审计报告"


class TestInedAnnualWorkSystemRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_ined_annual_report_work_system_not_periodic(self) -> None:
        """BD2E028：独立董事年度报告工作制度 → announcement（闭合 periodic 误抬）。"""
        r = routing.route_title(INED_ANNUAL_SYS, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "annual_report")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("独立董事年度报告工作制度", r.matched_patterns)

    def test_ined_nianbao_work_system_not_periodic(self) -> None:
        """BD2E695：独立董事年报工作制度 → announcement（闭合 periodic 误抬）。"""
        r = routing.route_title(INED_NIANBAO_SYS, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "annual_report")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")
        self.assertIn("独立董事年报工作制度", r.matched_patterns)

    def test_bare_work_system_not_lifted(self) -> None:
        """裸「工作制度」不得因本包泛化抬成 announcement。"""
        r = routing.route_title(BARE_WORK_SYS, self.config)
        self.assertEqual(r.predicted_document_type, "other")

    def test_real_annual_and_nianbao_audit_not_regressed(self) -> None:
        """真·年度报告与含「年报」审计报告仍进 periodic；无年报字样审计报告仍 announcement。"""
        r_annual = routing.route_title(REAL_ANNUAL, self.config)
        self.assertEqual(r_annual.predicted_document_type, "annual_report")
        self.assertEqual(r_annual.predicted_route_to, "cninfo_periodic_report_pdf")
        r_audit_nb = routing.route_title(AUDIT_WITH_NIANBAO, self.config)
        self.assertEqual(r_audit_nb.predicted_document_type, "annual_report")
        r_audit = routing.route_title(AUDIT_CLEAN, self.config)
        self.assertEqual(r_audit.predicted_document_type, "announcement")

    def test_prior_governance_paths_not_regressed(self) -> None:
        for title, expected in (
            (INED_NED, "announcement"),
            (IND_NOMINEE, "announcement"),
            (IND_MEETING, "announcement"),
            (GM_RULES, "announcement"),
            (SM_RES, "shareholder_meeting_material"),
            (BOARD, "board_resolution"),
        ):
            with self.subTest(title=title[:30]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, expected)

    def test_helpers_early_exit(self) -> None:
        """锁测 `_periodic_document_type` 早退与 `_general_document_type`。"""
        patterns = (
            self.config.get("categories", {})
            .get("general_announcement", {})
            .get("positive_patterns")
            or []
        )
        periodic_positive = (
            self.config.get("categories", {})
            .get("periodic_report", {})
            .get("positive_patterns")
            or {}
        )
        self.assertIsNone(
            routing._periodic_document_type(INED_ANNUAL_SYS, periodic_positive)
        )
        self.assertIsNone(
            routing._periodic_document_type(INED_NIANBAO_SYS, periodic_positive)
        )
        self.assertEqual(
            routing._general_document_type(INED_ANNUAL_SYS, patterns), "announcement"
        )
        self.assertEqual(
            routing._general_document_type(INED_NIANBAO_SYS, patterns), "announcement"
        )
        self.assertIn("独立董事年度报告工作制度", patterns)
        self.assertIn("独立董事年报工作制度", patterns)


if __name__ == "__main__":
    unittest.main()
