"""
B-FM-40：对外担保情况简报 / 英文 ESG known-document 晋升锁测（离线）。

覆盖：
- external_guarantee_situation_brief_known_001 与 esg_report_known_001 已为 ready
- title_pattern 与裸「简报」/「ESG」可区分；与对外担保管理制度可区分
- harvest 标题经硬化路由预测 announcement → general（非 other）
- 既有 LIVE_PASS 路径不回退（含 B-FM-39 subsidiary / compensation）
- 不重开 subsidiary / compensation / monetary / external_guarantee 等 LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_guarantee_brief_esg_known_001_promotion.py
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

HARVEST_BRIEF = "光明地产关于对外担保的情况简报"
HARVEST_ESG = "2024 Environmental, Social and Corporate Governance Report"
PATTERN_BRIEF = "对外担保的情况简报"
PATTERN_ESG = "Corporate Governance Report"
PATTERN_GUARANTEE_SYS = "对外担保管理制度"
BARE_JIANBAO = "某行业销售简报"
BARE_ESG = "某公司 ESG 专项说明"
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


class TestGuaranteeBriefEsgKnown001Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_guarantee_brief_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "external_guarantee_situation_brief_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "600708")
        self.assertEqual(c["company_name"], "光明地产")
        self.assertEqual(c["title_pattern"], PATTERN_BRIEF)
        self.assertEqual(c["date_start"], "2025-06-19")
        self.assertEqual(c["date_end"], "2025-06-22")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_BRIEF, HARVEST_BRIEF)
        self.assertNotEqual(c["title_pattern"], "简报")
        self.assertNotEqual(c["title_pattern"], "情况简报")
        self.assertNotEqual(c["title_pattern"], PATTERN_GUARANTEE_SYS)

    def test_esg_report_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "esg_report_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300661")
        self.assertEqual(c["company_name"], "圣邦股份")
        self.assertEqual(c["title_pattern"], PATTERN_ESG)
        self.assertEqual(c["date_start"], "2025-06-29")
        self.assertEqual(c["date_end"], "2025-07-02")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_ESG, HARVEST_ESG)
        self.assertNotEqual(c["title_pattern"], "ESG")
        self.assertNotEqual(c["title_pattern"], "Report")
        self.assertFalse(retrieval._title_matches(BARE_ESG, PATTERN_ESG))

    def test_patterns_mutually_distinct(self) -> None:
        """两案 pattern 与管理制度/裸简报互斥。"""
        self.assertNotEqual(PATTERN_BRIEF, PATTERN_ESG)
        self.assertNotEqual(PATTERN_BRIEF, PATTERN_GUARANTEE_SYS)
        self.assertFalse(retrieval._title_matches(HARVEST_BRIEF, PATTERN_ESG))
        self.assertFalse(retrieval._title_matches(HARVEST_ESG, PATTERN_BRIEF))
        self.assertTrue(retrieval._title_matches(HARVEST_BRIEF, PATTERN_BRIEF))
        self.assertTrue(retrieval._title_matches(HARVEST_ESG, PATTERN_ESG))
        self.assertFalse(retrieval._title_matches(BARE_JIANBAO, PATTERN_BRIEF))

    def test_harvest_titles_route_announcement(self) -> None:
        r_b = routing.route_title(HARVEST_BRIEF, self.config)
        self.assertEqual(r_b.predicted_document_type, "announcement")
        self.assertNotEqual(r_b.predicted_document_type, "other")
        self.assertEqual(r_b.predicted_route_to, "cninfo_general_announcement_pdf")
        r_e = routing.route_title(HARVEST_ESG, self.config)
        self.assertEqual(r_e.predicted_document_type, "announcement")
        self.assertNotEqual(r_e.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_gs = routing.route_title("海量数据对外担保管理制度", self.config)
        self.assertEqual(r_gs.predicted_document_type, "announcement")
        r_sub = routing.route_title("分、子公司管理制度（2025年6月）", self.config)
        self.assertEqual(r_sub.predicted_document_type, "announcement")
        r_xc = routing.route_title(
            "利尔化学股份有限公司2025年度经营团队薪酬与考核方案", self.config
        )
        self.assertEqual(r_xc.predicted_document_type, "announcement")
        r_m = routing.route_title("货币资金管理制度", self.config)
        self.assertEqual(r_m.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）；含 B-FM-38/39 四案。"""
        for case_id in (
            "legal_opinion_known_001",
            "continuous_supervision_annual_known_001",
            "bond_trustee_report_known_001",
            "listing_sponsor_known_001",
            "verification_opinion_known_001",
            "supervisory_board_known_001",
            "shareholder_meeting_known_001",
            "board_resolution_known_001",
            "nonstandard_audit_opinion_known_001",
            "raised_funds_usage_report_known_001",
            "independent_director_meeting_review_known_001",
            "asset_valuation_explanation_known_001",
            "audit_report_known_001",
            "incentive_trading_self_inspection_known_001",
            "employee_stock_ownership_plan_known_001",
            "company_articles_known_001",
            "raised_funds_management_system_known_001",
            "independent_ned_work_system_known_001",
            "general_manager_work_rules_known_001",
            "monetary_funds_management_system_known_001",
            "external_guarantee_management_system_known_001",
            "subsidiary_management_system_known_001",
            "compensation_assessment_plan_known_001",
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
            "external_guarantee_situation_brief_known_001",
            "esg_report_known_001",
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
