"""
B-FM-53：核查意见 known_004 / 持续督导年度 known_004 晋升锁测（离线）。

覆盖：
- verification_opinion_known_004 已为 ready（BD2E550 激励对象名单核查）
- continuous_supervision_annual_known_004 已为 ready（BD2E785 上海汽配督导年度）
- title_pattern 与 known_001–003 可区分
- harvest 标题经既有路由预测为 announcement（非 other / 非 annual_report）
- 既有 LIVE_PASS 路径不回退（含 B-FM-52 board known_004/005）
- 本包不改路由；不重开已 LIVE_PASS 案；拒绝 audit 年报陷阱

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_verification_supervision_known_004_promotion.py
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

HARVEST_VO_004 = (
    "监事会关于公司2025年限制性股票激励计划激励对象名单的核查意见及公示情况说明"
)
HARVEST_VO_001 = (
    "华泰联合证券有限责任公司关于三六零安全科技股份有限公司"
    "使用自有资金支付募投项目部分款项并以募集资金等额置换的核查意见"
)
HARVEST_VO_002 = (
    "中信建投证券股份有限公司关于北京福元医药股份有限公司"
    "首次公开发行限售股上市流通的核查意见"
)
HARVEST_VO_003 = (
    "国泰海通证券股份有限公司关于河南通达电缆股份有限公司募集资金投资项目结项"
    "并将节余募集资金永久补充流动资金的核查意见"
)
HARVEST_SUP_004 = (
    "民生证券股份有限公司关于上海汽车空调配件股份有限公司2024年度持续督导年度报告书"
)
HARVEST_SUP_001 = (
    "中国国际金融股份有限公司关于江苏恒立液压股份有限公司2024年度持续督导年度报告书"
)
HARVEST_SUP_002 = (
    "中国国际金融股份有限公司关于中国国检测试控股集团股份有限公司2024年度持续督导年度报告书"
)
HARVEST_SUP_003 = (
    "首创证券关于和邦生物向不特定对象发行可转换公司债券之2024年持续督导年度报告书"
)
PATTERN_VO_004 = "激励对象名单的核查意见"
PATTERN_VO_001 = "募集资金等额置换的核查意见"
PATTERN_VO_002 = "限售股上市流通的核查意见"
PATTERN_VO_003 = "节余募集资金永久补充流动资金的核查意见"
PATTERN_SUP_004 = "上海汽车空调配件股份有限公司2024年度持续督导年度报告书"
PATTERN_SUP_001 = "持续督导年度报告书"
PATTERN_SUP_002 = "国检测试控股集团股份有限公司2024年度持续督导年度报告书"
PATTERN_SUP_003 = "可转换公司债券之2024年持续督导年度报告书"
HARVEST_BOARD_004 = "第三届董事会第十四次会议决议公告"
HARVEST_BOARD_005 = "第三届董事会第十三次会议决议公告"
SM_RES = "2025年第二次临时股东大会决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestVerificationSupervisionKnown004Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_verification_opinion_known_004_ready_fields(self) -> None:
        c = _by_id(self.known, "verification_opinion_known_004")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "002827")
        self.assertEqual(c["company_name"], "高争民爆")
        self.assertEqual(c["title_pattern"], PATTERN_VO_004)
        self.assertEqual(c["date_start"], "2025-06-22")
        self.assertEqual(c["date_end"], "2025-06-25")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_VO_004, HARVEST_VO_004)
        self.assertNotEqual(c["title_pattern"], PATTERN_VO_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_VO_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_VO_003)
        self.assertNotEqual(c["title_pattern"], "核查意见")
        self.assertTrue(retrieval._title_matches(HARVEST_VO_004, PATTERN_VO_004))
        self.assertFalse(retrieval._title_matches(HARVEST_VO_001, PATTERN_VO_004))
        self.assertFalse(retrieval._title_matches(HARVEST_VO_002, PATTERN_VO_004))
        self.assertFalse(retrieval._title_matches(HARVEST_VO_003, PATTERN_VO_004))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_004, PATTERN_VO_004))

    def test_continuous_supervision_annual_known_004_ready_fields(self) -> None:
        c = _by_id(self.known, "continuous_supervision_annual_known_004")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "603107")
        self.assertEqual(c["company_name"], "上海汽配")
        self.assertEqual(c["title_pattern"], PATTERN_SUP_004)
        self.assertEqual(c["date_start"], "2025-04-20")
        self.assertEqual(c["date_end"], "2025-04-23")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_SUP_004, HARVEST_SUP_004)
        self.assertNotEqual(c["title_pattern"], PATTERN_SUP_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_SUP_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_SUP_003)
        self.assertTrue(retrieval._title_matches(HARVEST_SUP_004, PATTERN_SUP_004))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_001, PATTERN_SUP_004))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_002, PATTERN_SUP_004))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_003, PATTERN_SUP_004))
        self.assertFalse(retrieval._title_matches(HARVEST_VO_004, PATTERN_SUP_004))
        # known_001 宽串仍可命中本案标题，但本案 pattern 不得反向误抬恒立液压
        self.assertTrue(retrieval._title_matches(HARVEST_SUP_004, PATTERN_SUP_001))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_001, PATTERN_SUP_004))

    def test_patterns_mutually_distinct(self) -> None:
        patterns = [
            PATTERN_VO_001,
            PATTERN_VO_002,
            PATTERN_VO_003,
            PATTERN_VO_004,
            PATTERN_SUP_001,
            PATTERN_SUP_002,
            PATTERN_SUP_003,
            PATTERN_SUP_004,
        ]
        self.assertEqual(len(patterns), len(set(patterns)))
        self.assertFalse(retrieval._title_matches(HARVEST_VO_004, PATTERN_SUP_004))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_004, PATTERN_VO_004))

    def test_harvest_titles_route_correctly(self) -> None:
        for title in (HARVEST_VO_004, HARVEST_SUP_004):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")
                self.assertNotEqual(r.predicted_document_type, "annual_report")
                self.assertNotEqual(r.predicted_document_type, "board_resolution")

    def test_prior_paths_not_regressed(self) -> None:
        for title, expected in (
            (HARVEST_VO_001, "announcement"),
            (HARVEST_VO_002, "announcement"),
            (HARVEST_VO_003, "announcement"),
            (HARVEST_SUP_001, "announcement"),
            (HARVEST_SUP_002, "announcement"),
            (HARVEST_SUP_003, "announcement"),
            (HARVEST_BOARD_004, "board_resolution"),
            (HARVEST_BOARD_005, "board_resolution"),
        ):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, expected)
                self.assertNotEqual(r.predicted_document_type, "other")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_trap = routing.route_title("天健审〔2025〕11-195号 川网传媒2024年报审计报告", self.config)
        self.assertEqual(r_trap.predicted_document_type, "annual_report")

    def test_closed_live_pass_cases_still_ready(self) -> None:
        for case_id in (
            "verification_opinion_known_001",
            "verification_opinion_known_002",
            "verification_opinion_known_003",
            "continuous_supervision_annual_known_001",
            "continuous_supervision_annual_known_002",
            "continuous_supervision_annual_known_003",
            "board_resolution_known_004",
            "board_resolution_known_005",
            "listing_sponsor_known_001",
            "asset_valuation_explanation_known_001",
            "independent_director_meeting_review_known_001",
            "continuous_supervision_training_known_001",
            "audit_report_known_001",
        ):
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                self.assertEqual(c["case_status"], "ready")

    def test_new_ready_cases_pass_dry_run_field_validation(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        registry_ids = retrieval._load_registry_source_ids(registry)
        document_types = retrieval._load_document_types(schema)
        for case_id in (
            "verification_opinion_known_004",
            "continuous_supervision_annual_known_004",
        ):
            with self.subTest(case_id=case_id):
                case = _by_id(self.known, case_id)
                row = retrieval._process_case(
                    case, "known_document", registry_ids, document_types, dry_run=True
                )
                self.assertEqual(row["dry_run_status"], "ready_for_future_live_validation")
                self.assertEqual(row["would_query"], "true")
                notes = case["notes"]
                self.assertIn("B-FM-53", notes)
                self.assertTrue(any("\u4e00" <= ch <= "\u9fff" for ch in notes))


if __name__ == "__main__":
    unittest.main()
