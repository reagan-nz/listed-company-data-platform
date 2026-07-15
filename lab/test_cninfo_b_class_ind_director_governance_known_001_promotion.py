"""
B-FM-33：独立董事专门会议审核意见 / 提名人声明 known-document 晋升锁测（离线）。

覆盖：
- independent_director_meeting_review_known_001 与
  independent_director_nominee_declaration_known_001 已为 ready
- title_pattern 与年报审核意见 / 裸「审核意见」/ 章程 / 法律意见可区分
- harvest 标题经硬化路由预测 announcement → general（非 other）
- 既有 LIVE_PASS 路径不回退
- 不重开 legal_opinion / continuous_supervision / nonstandard_audit 等 LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_ind_director_governance_known_001_promotion.py
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

HARVEST_MR = "金枫酒业2025年第二次独立董事专门会议的审核意见"
HARVEST_ND = "独立董事提名人声明与承诺（张永炬）"
PATTERN_MR = "独立董事专门会议的审核意见"
PATTERN_ND = "独立董事提名人声明与承诺（张永炬）"
PATTERN_ANNUAL_SHENHE = "监事会关于公司2024年年度报告的审核意见"
PATTERN_LEGAL = "可转换公司债券的法律意见书"
PATTERN_NS = "非标准审计意见审计报告所涉及事项在2024年度消除情况的专项说明"
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


class TestIndDirectorGovernanceKnown001Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_meeting_review_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "independent_director_meeting_review_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "600616")
        self.assertEqual(c["company_name"], "金枫酒业")
        self.assertEqual(c["title_pattern"], PATTERN_MR)
        self.assertEqual(c["date_start"], "2025-06-19")
        self.assertEqual(c["date_end"], "2025-06-22")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_MR, HARVEST_MR)
        # 窄 pattern：不得仅用裸「审核意见」
        self.assertNotEqual(c["title_pattern"], "审核意见")
        self.assertIn("独立董事专门会议", c["title_pattern"])
        self.assertNotIn("年度报告", c["title_pattern"])
        self.assertNotIn("章程", c["title_pattern"])

    def test_nominee_declaration_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "independent_director_nominee_declaration_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "002003")
        self.assertEqual(c["company_name"], "伟星股份")
        self.assertEqual(c["title_pattern"], PATTERN_ND)
        self.assertEqual(c["date_start"], "2025-06-23")
        self.assertEqual(c["date_end"], "2025-06-26")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertEqual(PATTERN_ND, HARVEST_ND)
        self.assertIn("提名人声明与承诺", c["title_pattern"])
        self.assertIn("张永炬", c["title_pattern"])  # 同窗多提名人消歧
        self.assertNotIn("审核意见", c["title_pattern"])
        self.assertNotIn("章程", c["title_pattern"])

    def test_patterns_mutually_distinct(self) -> None:
        """两案 pattern 与年报审核意见 / 法律意见 / 非标准审计意见互斥。"""
        self.assertNotEqual(PATTERN_MR, PATTERN_ND)
        self.assertNotEqual(PATTERN_MR, PATTERN_ANNUAL_SHENHE)
        self.assertNotIn(PATTERN_MR, PATTERN_LEGAL)
        self.assertNotIn(PATTERN_ND, PATTERN_NS)
        self.assertFalse(retrieval._title_matches(HARVEST_MR, PATTERN_ND))
        self.assertFalse(retrieval._title_matches(HARVEST_ND, PATTERN_MR))
        self.assertTrue(retrieval._title_matches(HARVEST_MR, PATTERN_MR))
        self.assertTrue(retrieval._title_matches(HARVEST_ND, PATTERN_ND))
        # 裸「审核意见」不得误匹配专门会议 harvest 的 title_pattern 语义（pattern 更长）
        self.assertTrue(retrieval._title_matches(HARVEST_MR, "审核意见"))  # 子串存在
        self.assertNotEqual(PATTERN_MR, "审核意见")  # fixture 不得用裸串

    def test_harvest_routes_to_announcement(self) -> None:
        for title in (HARVEST_MR, HARVEST_ND):
            r = routing.route_title(title, self.config)
            self.assertEqual(r.predicted_document_type, "announcement", title)
            self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf", title)
            self.assertNotEqual(r.predicted_document_type, "other", title)

    def test_annual_shenhe_still_periodic(self) -> None:
        r = routing.route_title(PATTERN_ANNUAL_SHENHE, self.config)
        self.assertEqual(r.predicted_document_type, "annual_report")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_prior_live_pass_fixtures_still_ready(self) -> None:
        for case_id in (
            "nonstandard_audit_opinion_known_001",
            "raised_funds_usage_report_known_001",
            "legal_opinion_known_006",
            "continuous_supervision_annual_known_001",
            "bond_trustee_report_known_001",
        ):
            c = _by_id(self.known, case_id)
            self.assertEqual(c["case_status"], "ready", case_id)

    def test_sm_and_board_not_regressed(self) -> None:
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_board = routing.route_title(BOARD, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")


if __name__ == "__main__":
    unittest.main()
