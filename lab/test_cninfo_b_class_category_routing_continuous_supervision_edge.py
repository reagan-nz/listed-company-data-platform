"""
B 类 category routing — 「持续督导」document_type 边角锁测（B-FM-30）。

覆盖 harvest 已见但旧逻辑误路由的标题：
- 「…持续督导年度报告书」→ announcement（非 annual_report / periodic）
- 「…持续督导培训情况的报告」→ announcement（非 other）
- 「变更持续督导保荐代表人的公告」仍为 announcement
- 真·年度报告 / 受托管理 / 跟踪评级 / 保荐书 / 法律意见 / 股东会决议不回退

离线 only · 无 CNINFO · 无 live · 不造 §7 FP · 不重开 LIVE_PASS 包。

运行：
    python lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py
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
SUPERVISION_ANNUAL = (
    "中国国际金融股份有限公司关于江苏恒立液压股份有限公司2024年度持续督导年度报告书"
)  # BD2E131
SUPERVISION_TRAINING = (
    "国投证券股份有限公司关于芜湖三联锻造股份有限公司2025年度持续督导培训情况的报告"
)  # BD2E248
SUPERVISION_CHANGE = "本钢板材股份有限公司关于变更持续督导保荐代表人的公告"  # BD2E214
REAL_ANNUAL = "江苏恒立液压股份有限公司2024年年度报告"
BOND_TRUSTEE = (
    "申港证券股份有限公司关于三羊马(重庆)物流股份有限公司向不特定对象"
    "发行可转换公司债券受托管理事务报告（2024年度）"
)
TRACKING_RATING = (
    "2020年浙江华海药业股份有限公司公开发行可转换公司债券定期跟踪评级报告"
)
LISTING_SPONSOR = (
    "国信证券股份有限公司关于石家庄尚太科技股份有限公司主板向不特定对象"
    "发行可转换公司债券的上市保荐书（修订稿）"
)
LEGAL_NON_MEETING = (
    "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书"
)
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"


class TestContinuousSupervisionRoutingEdge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def test_supervision_annual_announcement_not_periodic(self) -> None:
        """BD2E131：持续督导年度报告书 → announcement（闭合 periodic 误抬）。"""
        r = routing.route_title(SUPERVISION_ANNUAL, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "annual_report")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.predicted_classification, "general_announcement")
        self.assertEqual(r.classification_status, "classified_correctly")

    def test_supervision_training_announcement_not_other(self) -> None:
        """BD2E248：持续督导培训情况的报告 → announcement（闭合 other 误落）。"""
        r = routing.route_title(SUPERVISION_TRAINING, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_document_type, "other")
        self.assertEqual(r.classification_status, "classified_correctly")

    def test_extra_supervision_annual_variants(self) -> None:
        extras = (
            "中国国际金融股份有限公司关于中国国检测试控股集团股份有限公司"
            "2024年度持续督导年度报告书",
            "首创证券关于和邦生物向不特定对象发行可转换公司债券之2024年持续督导年度报告书",
            "国盛证券有限责任公司、浙商证券股份有限公司关于浙江镇洋发展股份有限公司"
            "2024年持续督导年度报告",
        )
        for title in extras:
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertNotEqual(r.predicted_document_type, "annual_report")
                self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_change_sponsor_rep_still_announcement(self) -> None:
        r = routing.route_title(SUPERVISION_CHANGE, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_real_annual_report_not_regressed(self) -> None:
        """真·公司年度报告仍进 periodic。"""
        r = routing.route_title(REAL_ANNUAL, self.config)
        self.assertEqual(r.predicted_document_type, "annual_report")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_prior_edges_not_regressed(self) -> None:
        for title, expected in (
            (BOND_TRUSTEE, "announcement"),
            (TRACKING_RATING, "announcement"),
            (LISTING_SPONSOR, "announcement"),
            (LEGAL_NON_MEETING, "announcement"),
            (SM_RES, "shareholder_meeting_material"),
            (BOARD, "board_resolution"),
        ):
            with self.subTest(title=title[:30]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, expected)

    def test_helpers_early_exit(self) -> None:
        """锁测 `_periodic_document_type` 早退与 `_general_document_type` 持续督导。"""
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
            routing._periodic_document_type(SUPERVISION_ANNUAL, periodic_positive)
        )
        self.assertEqual(
            routing._general_document_type(SUPERVISION_ANNUAL, patterns), "announcement"
        )
        self.assertEqual(
            routing._general_document_type(SUPERVISION_TRAINING, patterns), "announcement"
        )
        self.assertIn("持续督导", patterns)


if __name__ == "__main__":
    unittest.main()
