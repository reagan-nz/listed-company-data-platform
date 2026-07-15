"""
B-FM-32：非标准审计意见消除专项说明 / 前次募集资金使用情况报告 known-document 晋升锁测（离线）。

覆盖：
- nonstandard_audit_opinion_known_001 与 raised_funds_usage_report_known_001 已为 ready
- title_pattern 与 §7 非标意见短串 / 监管工作函专项说明 / 持续督导 / 法律意见可区分
- harvest 标题经硬化路由预测 announcement → general（非 other）
- 既有 LIVE_PASS 路径不回退
- 不重开 legal_opinion_known_001–006 / continuous_supervision / bond_trustee 等 LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_nonstandard_audit_raised_funds_known_001_promotion.py
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

HARVEST_NS = (
    "中兴华会计师事务所关于对永鼎股份2023年度财务报表出具非标准审计意见"
    "审计报告所涉及事项在2024年度消除情况的专项说明"
)
HARVEST_RF = "公司前次募集资金使用情况报告"
PATTERN_NS = "非标准审计意见审计报告所涉及事项在2024年度消除情况的专项说明"
PATTERN_RF = "前次募集资金使用情况报告"
PATTERN_SHORT_FEIBIAO = "非标意见涉及事项的专项说明"
PATTERN_WORK_LETTER = (
    "中兴财光华会计师事务所（特殊普通合伙）关于对文投控股股份有限公司"
    "2024年年度报告的信息披露监管工作函的专项说明"
)
PATTERN_LEGAL = "可转换公司债券的法律意见书"
PATTERN_SUP = "持续督导年度报告书"
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


class TestNonstandardAuditRaisedFundsKnown001Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_nonstandard_audit_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "nonstandard_audit_opinion_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "600105")
        self.assertEqual(c["company_name"], "永鼎股份")
        self.assertEqual(c["title_pattern"], PATTERN_NS)
        self.assertEqual(c["date_start"], "2025-06-22")
        self.assertEqual(c["date_end"], "2025-06-25")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_NS, HARVEST_NS)
        self.assertIn("非标准审计意见", c["title_pattern"])
        self.assertIn("消除情况的专项说明", c["title_pattern"])
        # 窄 pattern：不得仅用裸「专项说明」
        self.assertNotEqual(c["title_pattern"], "专项说明")
        self.assertNotIn("监管工作函", c["title_pattern"])
        self.assertNotIn("非标意见", c["title_pattern"])  # 短串「非标意见」非子串

    def test_raised_funds_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "raised_funds_usage_report_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "000962")
        self.assertEqual(c["company_name"], "东方钽业")
        self.assertEqual(c["title_pattern"], PATTERN_RF)
        self.assertEqual(c["date_start"], "2025-06-22")
        self.assertEqual(c["date_end"], "2025-06-25")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_RF, HARVEST_RF)
        self.assertIn("前次募集资金使用情况报告", c["title_pattern"])
        self.assertNotIn("非标准审计意见", c["title_pattern"])
        self.assertNotIn("章程", c["title_pattern"])

    def test_patterns_mutually_distinct(self) -> None:
        """两案 pattern 与 §7 短串 / 监管工作函专项说明 / 法律意见 / 持续督导互斥。"""
        self.assertNotEqual(PATTERN_NS, PATTERN_RF)
        self.assertNotEqual(PATTERN_NS, PATTERN_SHORT_FEIBIAO)
        self.assertNotIn(PATTERN_NS, PATTERN_WORK_LETTER)
        self.assertNotIn(PATTERN_RF, PATTERN_LEGAL)
        self.assertNotIn(PATTERN_RF, PATTERN_SUP)
        self.assertFalse(retrieval._title_matches(HARVEST_NS, PATTERN_RF))
        self.assertFalse(retrieval._title_matches(HARVEST_RF, PATTERN_NS))
        self.assertTrue(retrieval._title_matches(HARVEST_NS, PATTERN_NS))
        self.assertTrue(retrieval._title_matches(HARVEST_RF, PATTERN_RF))
        # 「非标意见」短串不得误匹配全称 harvest
        self.assertFalse(retrieval._title_matches(HARVEST_NS, "非标意见"))

    def test_harvest_titles_route_announcement(self) -> None:
        r_ns = routing.route_title(HARVEST_NS, self.config)
        self.assertEqual(r_ns.predicted_document_type, "announcement")
        self.assertNotEqual(r_ns.predicted_document_type, "other")
        self.assertEqual(r_ns.predicted_route_to, "cninfo_general_announcement_pdf")
        r_rf = routing.route_title(HARVEST_RF, self.config)
        self.assertEqual(r_rf.predicted_document_type, "announcement")
        self.assertNotEqual(r_rf.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_legal = routing.route_title(
            "浙江六和律师事务所关于苏州天准科技股份有限公司"
            "向不特定对象发行可转换公司债券的法律意见书",
            self.config,
        )
        self.assertEqual(r_legal.predicted_document_type, "announcement")
        r_sup = routing.route_title(
            "中国国际金融股份有限公司关于江苏恒立液压股份有限公司2024年度持续督导年度报告书",
            self.config,
        )
        self.assertEqual(r_sup.predicted_document_type, "announcement")
        self.assertNotEqual(r_sup.predicted_document_type, "annual_report")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）；含 B-FM-31 legal_005/006。"""
        for case_id in (
            "legal_opinion_known_001",
            "legal_opinion_known_002",
            "legal_opinion_known_003",
            "legal_opinion_known_004",
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
            "nonstandard_audit_opinion_known_001",
            "raised_funds_usage_report_known_001",
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
