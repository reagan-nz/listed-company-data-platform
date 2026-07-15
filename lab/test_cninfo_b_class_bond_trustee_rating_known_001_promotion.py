"""
B-FM-29：债券受托管理事务报告 / 跟踪评级报告 known-document 晋升锁测（离线）。

覆盖：
- bond_trustee_report_known_001 与 tracking_rating_report_known_001 已为 ready
- title_pattern 与保荐书 / 权益变动 / 核查意见 / 法律意见书 / 股东会决议可区分
- harvest 标题经 B-FM-29 路由预测 announcement → general（非 other）
- 既有 LIVE_PASS 路径不回退
- 不重开 listing_sponsor / equity_change / verification / legal / supervisory / shareholder

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_bond_trustee_rating_known_001_promotion.py
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

HARVEST_TRUSTEE = (
    "申港证券股份有限公司关于三羊马(重庆)物流股份有限公司向不特定对象"
    "发行可转换公司债券受托管理事务报告（2024年度）"
)
HARVEST_RATING = (
    "2020年浙江华海药业股份有限公司公开发行可转换公司债券定期跟踪评级报告"
)
PATTERN_TRUSTEE = "可转换公司债券受托管理事务报告（2024年度）"
PATTERN_RATING = "跟踪评级报告"
PATTERN_SPONSOR = "可转换公司债券的上市保荐书"
PATTERN_EQUITY = "权益变动报告书"
PATTERN_VERIFICATION = "募集资金等额置换的核查意见"
PATTERN_LEGAL = "增持公司股份之法律意见书"
SM_RES = "2025年第二次临时股东大会决议公告"
BOARD = "第七届董事会第十一次会议决议公告"
LEGAL_REAL = (
    "浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书"
)


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestBondTrusteeRatingKnown001Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_bond_trustee_report_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "bond_trustee_report_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "001317")
        self.assertEqual(c["company_name"], "三羊马")
        self.assertEqual(c["title_pattern"], PATTERN_TRUSTEE)
        self.assertEqual(c["date_start"], "2025-06-24")
        self.assertEqual(c["date_end"], "2025-06-27")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn("受托管理事务报告", c["title_pattern"])
        self.assertIn("2024年度", c["title_pattern"])

    def test_tracking_rating_report_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "tracking_rating_report_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "600521")
        self.assertEqual(c["company_name"], "华海药业")
        self.assertEqual(c["title_pattern"], PATTERN_RATING)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertIn("跟踪评级报告", c["title_pattern"])

    def test_patterns_mutually_distinct(self) -> None:
        """受托管理 / 跟踪评级 pattern 与保荐书 / 权益变动 / 核查意见 / 法律意见互斥。"""
        self.assertNotEqual(PATTERN_TRUSTEE, PATTERN_RATING)
        self.assertNotIn(PATTERN_TRUSTEE, PATTERN_SPONSOR)
        self.assertNotIn(PATTERN_RATING, PATTERN_EQUITY)
        self.assertNotIn("保荐书", PATTERN_TRUSTEE)
        self.assertNotIn("权益变动", PATTERN_RATING)
        self.assertNotIn("核查意见", PATTERN_TRUSTEE)
        self.assertNotIn("法律意见", PATTERN_RATING)
        self.assertNotIn("股东大会", PATTERN_TRUSTEE)
        self.assertNotIn("董事会", PATTERN_RATING)
        self.assertIn(PATTERN_TRUSTEE, HARVEST_TRUSTEE)
        self.assertIn(PATTERN_RATING, HARVEST_RATING)
        self.assertNotIn(PATTERN_RATING, HARVEST_TRUSTEE)
        self.assertNotIn(PATTERN_TRUSTEE, HARVEST_RATING)

    def test_harvest_titles_route_announcement_not_other(self) -> None:
        for title in (HARVEST_TRUSTEE, HARVEST_RATING):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")

    def test_prior_paths_not_regressed(self) -> None:
        r_sponsor = routing.route_title(
            "国信证券股份有限公司关于石家庄尚太科技股份有限公司主板向不特定对象"
            "发行可转换公司债券的上市保荐书（修订稿）",
            self.config,
        )
        self.assertEqual(r_sponsor.predicted_document_type, "announcement")
        r_equity = routing.route_title("德林海简式权益变动报告书", self.config)
        self.assertEqual(r_equity.predicted_document_type, "announcement")
        r_v = routing.route_title(
            "华泰联合证券有限责任公司关于三六零安全科技股份有限公司"
            "使用自有资金支付募投项目部分款项并以募集资金等额置换的核查意见",
            self.config,
        )
        self.assertEqual(r_v.predicted_document_type, "announcement")
        r_legal = routing.route_title(LEGAL_REAL, self.config)
        self.assertEqual(r_legal.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        """已 LIVE_PASS 案仍为 ready（不降级）。"""
        for case_id in (
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
            "bond_trustee_report_known_001",
            "tracking_rating_report_known_001",
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
