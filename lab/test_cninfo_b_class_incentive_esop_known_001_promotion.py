"""
B-FM-35：激励买卖自查报告 / 员工持股计划 known-document 晋升锁测（离线）。

覆盖：
- incentive_trading_self_inspection_known_001 与 employee_stock_ownership_plan_known_001
  已为 ready
- title_pattern 与裸「自查报告」/ 章程制度可区分
- harvest 标题经硬化路由预测 announcement → general（非 other）
- 既有 LIVE_PASS 路径不回退（含 B-FM-34 资产评估/审计报告）
- 不重开 asset_valuation / audit_report / independent_director 等 LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_incentive_esop_known_001_promotion.py
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

HARVEST_SI = (
    "关于2024年限制性股票激励计划内幕信息知情人及激励对象买卖公司股票的自查报告"
)
HARVEST_ESOP = "第二期员工持股计划（草案）(修订稿）"
PATTERN_SI = "买卖公司股票的自查报告"
PATTERN_ESOP = "第二期员工持股计划（草案）(修订稿）"
PATTERN_BARE_ZICHA = "自查报告"
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


class TestIncentiveEsopKnown001Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_self_inspection_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "incentive_trading_self_inspection_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000786")
        self.assertEqual(c["company_name"], "北新建材")
        self.assertEqual(c["title_pattern"], PATTERN_SI)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_SI, HARVEST_SI)
        # 窄 pattern：不得仅用裸「自查报告」
        self.assertNotEqual(c["title_pattern"], "自查报告")
        self.assertNotIn("章程", c["title_pattern"])

    def test_esop_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "employee_stock_ownership_plan_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000301")
        self.assertEqual(c["company_name"], "东方盛虹")
        self.assertEqual(c["title_pattern"], PATTERN_ESOP)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_ESOP, HARVEST_ESOP)
        self.assertIn("员工持股计划", c["title_pattern"])
        self.assertNotIn("自查报告", c["title_pattern"])
        # 消歧：不得仅用裸「员工持股计划」（窗内可多条）
        self.assertNotEqual(c["title_pattern"], "员工持股计划")

    def test_patterns_mutually_distinct(self) -> None:
        """两案 pattern 与裸自查报告互斥。"""
        self.assertNotEqual(PATTERN_SI, PATTERN_ESOP)
        self.assertNotEqual(PATTERN_SI, PATTERN_BARE_ZICHA)
        self.assertFalse(retrieval._title_matches(HARVEST_SI, PATTERN_ESOP))
        self.assertFalse(retrieval._title_matches(HARVEST_ESOP, PATTERN_SI))
        self.assertTrue(retrieval._title_matches(HARVEST_SI, PATTERN_SI))
        self.assertTrue(retrieval._title_matches(HARVEST_ESOP, PATTERN_ESOP))

    def test_harvest_titles_route_announcement(self) -> None:
        r_si = routing.route_title(HARVEST_SI, self.config)
        self.assertEqual(r_si.predicted_document_type, "announcement")
        self.assertNotEqual(r_si.predicted_document_type, "other")
        self.assertEqual(r_si.predicted_route_to, "cninfo_general_announcement_pdf")
        r_esop = routing.route_title(HARVEST_ESOP, self.config)
        self.assertEqual(r_esop.predicted_document_type, "announcement")
        self.assertNotEqual(r_esop.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_av = routing.route_title(
            "舍得酒业拟进行资产收购所涉及的位于遂宁市射洪县沱牌镇四处住宅用、"
            "商业用房地产市场价值资产评估说明",
            self.config,
        )
        self.assertEqual(r_av.predicted_document_type, "announcement")
        r_ar = routing.route_title(
            "迎驾贡酒2024年审计报告-容诚审字[2025]230Z0521号（修订版）",
            self.config,
        )
        self.assertEqual(r_ar.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）；含 B-FM-34 两案。"""
        for case_id in (
            "legal_opinion_known_001",
            "legal_opinion_known_005",
            "legal_opinion_known_006",
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
            "nonstandard_audit_opinion_known_001",
            "raised_funds_usage_report_known_001",
            "independent_director_meeting_review_known_001",
            "independent_director_nominee_declaration_known_001",
            "asset_valuation_explanation_known_001",
            "audit_report_known_001",
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
            "incentive_trading_self_inspection_known_001",
            "employee_stock_ownership_plan_known_001",
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
