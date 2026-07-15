"""
B-FM-27：核查意见 known-document 晋升锁测（离线）。

覆盖：
- verification_opinion_known_001（募资置换核查意见）与 known_002（限售流通核查意见）已为 ready
- title_pattern 与法律意见书 / 股东会决议 / 董事会可区分
- harvest 标题经 B-FM-27 路由预测 announcement → general（非 other）
- 法律意见 / 股东会决议 / 董事会路径不回退
- 不重开 legal_opinion_known_001–004 / supervisory_board / shareholder_meeting LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_verification_opinion_known_001_002_promotion.py
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

HARVEST_001 = (
    "华泰联合证券有限责任公司关于三六零安全科技股份有限公司"
    "使用自有资金支付募投项目部分款项并以募集资金等额置换的核查意见"
)
HARVEST_002 = (
    "中信建投证券股份有限公司关于北京福元医药股份有限公司"
    "首次公开发行限售股上市流通的核查意见"
)
PATTERN_001 = "募集资金等额置换的核查意见"
PATTERN_002 = "限售股上市流通的核查意见"
PATTERN_LEGAL_003 = "增持公司股份之法律意见书"
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


class TestVerificationOpinionKnown001002Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_verification_opinion_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "verification_opinion_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "601360")
        self.assertEqual(c["company_name"], "三六零")
        self.assertEqual(c["title_pattern"], PATTERN_001)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn("核查意见", c["title_pattern"])

    def test_verification_opinion_known_002_ready_fields(self) -> None:
        c = _by_id(self.known, "verification_opinion_known_002")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "601089")
        self.assertEqual(c["company_name"], "福元医药")
        self.assertEqual(c["title_pattern"], PATTERN_002)
        self.assertEqual(c["date_start"], "2025-06-23")
        self.assertEqual(c["date_end"], "2025-06-26")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertIn("核查意见", c["title_pattern"])

    def test_patterns_mutually_distinct(self) -> None:
        """核查意见 pattern 与法律意见 / 股东会决议互斥。"""
        self.assertNotEqual(PATTERN_001, PATTERN_002)
        self.assertNotIn(PATTERN_001, PATTERN_LEGAL_003)
        self.assertNotIn(PATTERN_002, PATTERN_LEGAL_003)
        self.assertNotIn("法律意见", PATTERN_001)
        self.assertNotIn("股东大会", PATTERN_001)
        self.assertNotIn("董事会", PATTERN_002)
        # harvest 标题应命中各自 pattern
        self.assertIn(PATTERN_001, HARVEST_001)
        self.assertIn(PATTERN_002, HARVEST_002)
        self.assertNotIn(PATTERN_002, HARVEST_001)
        self.assertNotIn(PATTERN_001, HARVEST_002)

    def test_harvest_titles_route_announcement_not_other(self) -> None:
        for title in (HARVEST_001, HARVEST_002):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")

    def test_legal_shareholder_board_not_regressed(self) -> None:
        """法律意见 / 股东会决议 / 董事会路径不回退。"""
        r_legal = routing.route_title(LEGAL_REAL, self.config)
        self.assertEqual(r_legal.predicted_document_type, "announcement")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")

    def test_closed_live_pass_cases_remain_ready(self) -> None:
        """已 LIVE_PASS 的法律意见 / 监事会 / 股东会案仍为 ready（不降级）。"""
        for case_id in (
            "legal_opinion_known_001",
            "legal_opinion_known_002",
            "legal_opinion_known_003",
            "legal_opinion_known_004",
            "supervisory_board_known_001",
            "supervisory_board_known_002",
            "shareholder_meeting_known_007",
        ):
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                self.assertEqual(c["case_status"], "ready")

    def test_ready_case_selector_accepts_new_cases(self) -> None:
        """新晋 ready 案通过 corpus retrieval dry-run 字段校验。"""
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        registry_ids = retrieval._load_registry_source_ids(registry)
        document_types = retrieval._load_document_types(schema)
        for case_id in (
            "verification_opinion_known_001",
            "verification_opinion_known_002",
        ):
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                ok, issues = retrieval._validate_ready_case(
                    c, "known_document", registry_ids, document_types
                )
                self.assertTrue(ok, f"{case_id}: {issues}")


if __name__ == "__main__":
    unittest.main()
