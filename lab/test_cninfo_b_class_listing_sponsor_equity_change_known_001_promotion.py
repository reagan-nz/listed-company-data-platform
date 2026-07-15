"""
B-FM-28：上市保荐书 / 权益变动报告书 known-document 晋升锁测（离线）。

覆盖：
- listing_sponsor_known_001 与 equity_change_report_known_001 已为 ready
- title_pattern 与核查意见 / 法律意见书 / 股东会决议可区分
- harvest 标题经 B-FM-28 路由预测 announcement → general（非 other）
- 核查意见 / 法律意见 / 股东会决议 / 董事会路径不回退
- 不重开 verification_opinion / legal_opinion / supervisory / shareholder LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_listing_sponsor_equity_change_known_001_promotion.py
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

HARVEST_SPONSOR = (
    "国信证券股份有限公司关于石家庄尚太科技股份有限公司主板向不特定对象"
    "发行可转换公司债券的上市保荐书（修订稿）"
)
HARVEST_EQUITY = "德林海简式权益变动报告书"
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


class TestListingSponsorEquityChangeKnown001Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_listing_sponsor_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "listing_sponsor_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "001301")
        self.assertEqual(c["company_name"], "尚太科技")
        self.assertEqual(c["title_pattern"], PATTERN_SPONSOR)
        self.assertEqual(c["date_start"], "2025-06-08")
        self.assertEqual(c["date_end"], "2025-06-11")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn("保荐书", c["title_pattern"])

    def test_equity_change_report_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "equity_change_report_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "688069")
        self.assertEqual(c["company_name"], "德林海")
        self.assertEqual(c["title_pattern"], PATTERN_EQUITY)
        self.assertEqual(c["date_start"], "2025-06-24")
        self.assertEqual(c["date_end"], "2025-06-27")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertIn("权益变动报告书", c["title_pattern"])

    def test_patterns_mutually_distinct(self) -> None:
        """保荐书 / 权益变动 pattern 与核查意见 / 法律意见 / 股东会决议互斥。"""
        self.assertNotEqual(PATTERN_SPONSOR, PATTERN_EQUITY)
        self.assertNotIn(PATTERN_SPONSOR, PATTERN_VERIFICATION)
        self.assertNotIn(PATTERN_EQUITY, PATTERN_LEGAL)
        self.assertNotIn("核查意见", PATTERN_SPONSOR)
        self.assertNotIn("法律意见", PATTERN_EQUITY)
        self.assertNotIn("股东大会", PATTERN_SPONSOR)
        self.assertNotIn("董事会", PATTERN_EQUITY)
        self.assertIn(PATTERN_SPONSOR, HARVEST_SPONSOR)
        self.assertIn(PATTERN_EQUITY, HARVEST_EQUITY)
        self.assertNotIn(PATTERN_EQUITY, HARVEST_SPONSOR)
        self.assertNotIn(PATTERN_SPONSOR, HARVEST_EQUITY)

    def test_harvest_titles_route_announcement_not_other(self) -> None:
        for title in (HARVEST_SPONSOR, HARVEST_EQUITY):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")

    def test_verification_legal_shareholder_board_not_regressed(self) -> None:
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
        """已 LIVE_PASS 的核查意见 / 法律意见 / 监事会 / 股东会案仍为 ready（不降级）。"""
        for case_id in (
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
        for case_id in ("listing_sponsor_known_001", "equity_change_report_known_001"):
            with self.subTest(case_id=case_id):
                case = _by_id(self.known, case_id)
                row = retrieval._process_case(
                    case, "known_document", registry_ids, document_types, dry_run=True
                )
                self.assertEqual(row["dry_run_status"], "ready_for_future_live_validation")
                self.assertEqual(row["would_query"], "true")


if __name__ == "__main__":
    unittest.main()
