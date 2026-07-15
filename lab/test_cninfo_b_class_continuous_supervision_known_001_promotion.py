"""
B-FM-30：持续督导年度报告书 / 培训情况报告 known-document 晋升锁测（离线）。

覆盖：
- continuous_supervision_annual_known_001 与 continuous_supervision_training_known_001 已为 ready
- title_pattern 与真·年度报告 / 受托管理 / 跟踪评级 / 保荐书 / 法律意见 / 股东会决议可区分
- harvest 标题经 B-FM-30 路由预测 announcement → general（非 annual_report / other）
- 既有 LIVE_PASS 路径不回退
- 不重开 bond_trustee / tracking_rating / listing_sponsor / equity_change / verification /
  legal / supervisory / shareholder LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_continuous_supervision_known_001_promotion.py
"""

from __future__ import annotations

import os
import sys
import unittest

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_b_class_category_routing as routing  # noqa: E402
import validate_cninfo_b_class_corpus_retrieval as retrieval  # noqa: E402

KNOWN_YAML = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

HARVEST_ANNUAL = (
    "中国国际金融股份有限公司关于江苏恒立液压股份有限公司2024年度持续督导年度报告书"
)
HARVEST_TRAINING = (
    "国投证券股份有限公司关于芜湖三联锻造股份有限公司2025年度持续督导培训情况的报告"
)
PATTERN_ANNUAL = "持续督导年度报告书"
PATTERN_TRAINING = "持续督导培训情况的报告"
PATTERN_TRUSTEE = "可转换公司债券受托管理事务报告（2024年度）"
PATTERN_RATING = "跟踪评级报告"
PATTERN_SPONSOR = "可转换公司债券的上市保荐书"
PATTERN_LEGAL = "增持公司股份之法律意见书"
REAL_ANNUAL = "江苏恒立液压股份有限公司2024年年度报告"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestContinuousSupervisionKnown001Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_continuous_supervision_annual_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "continuous_supervision_annual_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "601100")
        self.assertEqual(c["company_name"], "恒立液压")
        self.assertEqual(c["title_pattern"], PATTERN_ANNUAL)
        self.assertEqual(c["date_start"], "2025-05-07")
        self.assertEqual(c["date_end"], "2025-05-10")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn("持续督导年度报告书", c["title_pattern"])
        self.assertIn(PATTERN_ANNUAL, HARVEST_ANNUAL)

    def test_continuous_supervision_training_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "continuous_supervision_training_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "001282")
        self.assertEqual(c["company_name"], "三联锻造")
        self.assertEqual(c["title_pattern"], PATTERN_TRAINING)
        self.assertEqual(c["date_start"], "2025-06-22")
        self.assertEqual(c["date_end"], "2025-06-25")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertIn("持续督导培训", c["title_pattern"])
        self.assertIn(PATTERN_TRAINING, HARVEST_TRAINING)

    def test_patterns_mutually_distinct(self) -> None:
        """持续督导 annual / training pattern 与受托管理 / 评级 / 保荐 / 法律意见互斥。"""
        self.assertNotEqual(PATTERN_ANNUAL, PATTERN_TRAINING)
        self.assertNotIn(PATTERN_ANNUAL, PATTERN_TRUSTEE)
        self.assertNotIn(PATTERN_TRAINING, PATTERN_RATING)
        self.assertNotIn("受托管理", PATTERN_ANNUAL)
        self.assertNotIn("跟踪评级", PATTERN_TRAINING)
        self.assertNotIn("保荐书", PATTERN_ANNUAL)
        self.assertNotIn("法律意见", PATTERN_TRAINING)
        self.assertNotIn(PATTERN_ANNUAL, REAL_ANNUAL)
        self.assertFalse(retrieval._title_matches(REAL_ANNUAL, PATTERN_ANNUAL))
        self.assertFalse(retrieval._title_matches(HARVEST_ANNUAL, PATTERN_TRAINING))
        self.assertFalse(retrieval._title_matches(HARVEST_TRAINING, PATTERN_ANNUAL))

    def test_harvest_titles_route_announcement(self) -> None:
        r_a = routing.route_title(HARVEST_ANNUAL, self.config)
        self.assertEqual(r_a.predicted_document_type, "announcement")
        self.assertNotEqual(r_a.predicted_document_type, "annual_report")
        self.assertNotEqual(r_a.predicted_route_to, "cninfo_periodic_report_pdf")
        r_t = routing.route_title(HARVEST_TRAINING, self.config)
        self.assertEqual(r_t.predicted_document_type, "announcement")
        self.assertNotEqual(r_t.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_real = routing.route_title(REAL_ANNUAL, self.config)
        self.assertEqual(r_real.predicted_document_type, "annual_report")
        r_trustee = routing.route_title(
            "申港证券股份有限公司关于三羊马(重庆)物流股份有限公司向不特定对象"
            "发行可转换公司债券受托管理事务报告（2024年度）",
            self.config,
        )
        self.assertEqual(r_trustee.predicted_document_type, "announcement")
        r_sponsor = routing.route_title(
            "国信证券股份有限公司关于石家庄尚太科技股份有限公司主板向不特定对象"
            "发行可转换公司债券的上市保荐书（修订稿）",
            self.config,
        )
        self.assertEqual(r_sponsor.predicted_document_type, "announcement")
        r_legal = routing.route_title(
            "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书",
            self.config,
        )
        self.assertEqual(r_legal.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）。"""
        for case_id in (
            "bond_trustee_report_known_001",
            "tracking_rating_report_known_001",
            "listing_sponsor_known_001",
            "equity_change_report_known_001",
            "verification_opinion_known_001",
            "verification_opinion_known_002",
            "legal_opinion_known_001",
            "legal_opinion_known_003",
            "legal_opinion_known_004",
            "supervisory_board_known_001",
            "supervisory_board_known_002",
            "shareholder_meeting_known_001",
            "shareholder_meeting_known_007",
            "board_resolution_known_001",
        ):
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                self.assertEqual(c["case_status"], "ready")

    def test_new_ready_cases_pass_dry_run_field_validation(self) -> None:
        """新晋 ready 案通过 corpus retrieval dry-run 字段校验。"""
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        registry_ids = retrieval._load_registry_source_ids(registry)
        document_types = retrieval._load_document_types(schema)
        for case_id in (
            "continuous_supervision_annual_known_001",
            "continuous_supervision_training_known_001",
        ):
            with self.subTest(case_id=case_id):
                case = _by_id(self.known, case_id)
                row = retrieval._process_case(
                    case, "known_document", registry_ids, document_types, dry_run=True
                )
                self.assertEqual(row["dry_run_status"], "ready_for_future_live_validation")
                self.assertEqual(row["would_query"], "true")


if __name__ == "__main__":
    unittest.main()
