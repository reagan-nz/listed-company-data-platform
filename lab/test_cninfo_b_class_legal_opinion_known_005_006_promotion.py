"""
B-FM-31：可转债 / 激励行权价格调整法律意见书 known-document 晋升锁测（离线）。

覆盖：
- legal_opinion_known_005（可转债法律意见书）与 known_006（激励行权价格调整）已为 ready
- title_pattern 与 known_001–004 / 上市保荐书 / 受托管理 / 股东会决议可区分
- harvest 标题经既有路由预测 announcement → general（非 other）
- 既有 LIVE_PASS 路径不回退
- 不重开 legal_opinion_known_001–004 / continuous_supervision / bond_trustee 等 LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_legal_opinion_known_005_006_promotion.py
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

HARVEST_005 = (
    "浙江六和律师事务所关于苏州天准科技股份有限公司"
    "向不特定对象发行可转换公司债券的法律意见书"
)
HARVEST_006 = (
    "北京竞天公诚（杭州）律师事务所关于恒生电子股份有限公司"
    "调整2024年股票期权激励计划行权价格的法律意见书"
)
PATTERN_005 = "可转换公司债券的法律意见书"
PATTERN_006 = "调整2024年股票期权激励计划行权价格的法律意见书"
PATTERN_003 = "增持公司股份之法律意见书"
PATTERN_004 = "差异化分红的法律意见书"
PATTERN_001 = "第一次临时股东大会的法律意见书"
PATTERN_SPONSOR = "可转换公司债券的上市保荐书"
PATTERN_TRUSTEE = "可转换公司债券受托管理事务报告（2024年度）"
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


class TestLegalOpinionKnown005006Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_legal_opinion_known_005_ready_fields(self) -> None:
        c = _by_id(self.known, "legal_opinion_known_005")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "688003")
        self.assertEqual(c["company_name"], "天准科技")
        self.assertEqual(c["title_pattern"], PATTERN_005)
        self.assertEqual(c["date_start"], "2025-06-22")
        self.assertEqual(c["date_end"], "2025-06-25")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_005, HARVEST_005)
        self.assertIn("可转换公司债券", c["title_pattern"])
        self.assertIn("法律意见书", c["title_pattern"])
        self.assertNotIn("上市保荐书", c["title_pattern"])
        self.assertNotIn("股东大会", c["title_pattern"])
        self.assertNotIn("股东会", c["title_pattern"])

    def test_legal_opinion_known_006_ready_fields(self) -> None:
        c = _by_id(self.known, "legal_opinion_known_006")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "600570")
        self.assertEqual(c["company_name"], "恒生电子")
        self.assertEqual(c["title_pattern"], PATTERN_006)
        self.assertEqual(c["date_start"], "2025-06-12")
        self.assertEqual(c["date_end"], "2025-06-15")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_006, HARVEST_006)
        self.assertIn("调整2024年", c["title_pattern"])
        self.assertIn("股票期权激励计划", c["title_pattern"])
        self.assertIn("行权价格", c["title_pattern"])
        self.assertNotIn("股东大会", c["title_pattern"])
        self.assertNotIn("可转换公司债券", c["title_pattern"])

    def test_patterns_mutually_distinct(self) -> None:
        """known_005/006 pattern 与 001–004 / 保荐书 / 受托管理互斥。"""
        self.assertNotEqual(PATTERN_005, PATTERN_006)
        self.assertNotEqual(PATTERN_005, PATTERN_003)
        self.assertNotEqual(PATTERN_005, PATTERN_004)
        self.assertNotEqual(PATTERN_005, PATTERN_001)
        self.assertNotEqual(PATTERN_005, PATTERN_SPONSOR)
        self.assertNotIn(PATTERN_005, PATTERN_TRUSTEE)
        self.assertNotIn(PATTERN_006, PATTERN_003)
        self.assertNotIn(PATTERN_006, PATTERN_004)
        self.assertFalse(retrieval._title_matches(HARVEST_005, PATTERN_006))
        self.assertFalse(retrieval._title_matches(HARVEST_006, PATTERN_005))
        self.assertFalse(retrieval._title_matches(HARVEST_005, PATTERN_SPONSOR))
        self.assertTrue(retrieval._title_matches(HARVEST_005, PATTERN_005))
        self.assertTrue(retrieval._title_matches(HARVEST_006, PATTERN_006))

    def test_harvest_titles_route_announcement(self) -> None:
        r5 = routing.route_title(HARVEST_005, self.config)
        self.assertEqual(r5.predicted_document_type, "announcement")
        self.assertNotEqual(r5.predicted_document_type, "other")
        self.assertEqual(r5.predicted_route_to, "cninfo_general_announcement_pdf")
        r6 = routing.route_title(HARVEST_006, self.config)
        self.assertEqual(r6.predicted_document_type, "announcement")
        self.assertNotEqual(r6.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_legal3 = routing.route_title(
            "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书",
            self.config,
        )
        self.assertEqual(r_legal3.predicted_document_type, "announcement")
        r_sponsor = routing.route_title(
            "国信证券股份有限公司关于石家庄尚太科技股份有限公司主板向不特定对象"
            "发行可转换公司债券的上市保荐书（修订稿）",
            self.config,
        )
        self.assertEqual(r_sponsor.predicted_document_type, "announcement")
        r_trustee = routing.route_title(
            "申港证券股份有限公司关于三羊马(重庆)物流股份有限公司向不特定对象"
            "发行可转换公司债券受托管理事务报告（2024年度）",
            self.config,
        )
        self.assertEqual(r_trustee.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）。"""
        for case_id in (
            "legal_opinion_known_001",
            "legal_opinion_known_002",
            "legal_opinion_known_003",
            "legal_opinion_known_004",
            "continuous_supervision_annual_known_001",
            "continuous_supervision_training_known_001",
            "bond_trustee_report_known_001",
            "tracking_rating_report_known_001",
            "listing_sponsor_known_001",
            "equity_change_report_known_001",
            "verification_opinion_known_001",
            "verification_opinion_known_002",
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
        for case_id in ("legal_opinion_known_005", "legal_opinion_known_006"):
            with self.subTest(case_id=case_id):
                case = _by_id(self.known, case_id)
                row = retrieval._process_case(
                    case, "known_document", registry_ids, document_types, dry_run=True
                )
                self.assertEqual(row["dry_run_status"], "ready_for_future_live_validation")
                self.assertEqual(row["would_query"], "true")


if __name__ == "__main__":
    unittest.main()
