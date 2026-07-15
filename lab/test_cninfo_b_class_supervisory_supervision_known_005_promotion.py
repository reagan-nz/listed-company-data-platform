"""
B-FM-54：监事会决议 known_005 / 持续督导年度 known_005 晋升锁测（离线）。

覆盖：
- supervisory_board_known_005 已为 ready（BD2E322 建新股份届次全锚定）
- continuous_supervision_annual_known_005 已为 ready（BD2E791 万朗磁塑督导年度）
- title_pattern 与 known_001–004 可区分
- harvest 标题经既有路由预测为 announcement（非 other / 非 annual_report）
- 既有 LIVE_PASS 路径不回退（含 B-FM-53 vo/supervision known_004）
- 本包不改路由；不重开已 LIVE_PASS 案；拒绝 audit 年报陷阱

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_supervisory_supervision_known_005_promotion.py
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

HARVEST_SB_005 = "建新股份第六届监事会第十二次会议决议公告"
HARVEST_SB_001 = "第六届监事会第二十四次会议决议公告"
HARVEST_SB_002 = "农心作物科技股份有限公司第二届监事会第二十二次会议决议的公告"
HARVEST_SB_003 = "第四届监事会第五次会议决议公告"
HARVEST_SB_004 = "海汽集团第四届监事会第三十次会议决议公告"
HARVEST_SUP_005 = (
    "国元证券股份有限公司关于安徽万朗磁塑股份有限公司2024年度持续督导年度报告书"
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
HARVEST_SUP_004 = (
    "民生证券股份有限公司关于上海汽车空调配件股份有限公司2024年度持续督导年度报告书"
)
PATTERN_SB_005 = "第六届监事会第十二次会议决议公告"
PATTERN_SB_001 = "第二十四次会议决议公告"
PATTERN_SB_002 = "第二十二次会议决议的公告"
PATTERN_SB_003 = "第四届监事会第五次会议决议公告"
PATTERN_SB_004 = "第四届监事会第三十次会议决议公告"
PATTERN_SUP_005 = "安徽万朗磁塑股份有限公司2024年度持续督导年度报告书"
PATTERN_SUP_001 = "持续督导年度报告书"
PATTERN_SUP_002 = "国检测试控股集团股份有限公司2024年度持续督导年度报告书"
PATTERN_SUP_003 = "可转换公司债券之2024年持续督导年度报告书"
PATTERN_SUP_004 = "上海汽车空调配件股份有限公司2024年度持续督导年度报告书"
HARVEST_VO_004 = (
    "监事会关于公司2025年限制性股票激励计划激励对象名单的核查意见及公示情况说明"
)
SM_RES = "2025年第二次临时股东大会决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestSupervisorySupervisionKnown005Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_supervisory_board_known_005_ready_fields(self) -> None:
        c = _by_id(self.known, "supervisory_board_known_005")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300107")
        self.assertEqual(c["company_name"], "建新股份")
        self.assertEqual(c["title_pattern"], PATTERN_SB_005)
        self.assertEqual(c["date_start"], "2025-05-27")
        self.assertEqual(c["date_end"], "2025-05-30")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN_SB_005, HARVEST_SB_005)
        self.assertNotEqual(c["title_pattern"], PATTERN_SB_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_SB_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_SB_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_SB_004)
        self.assertTrue(retrieval._title_matches(HARVEST_SB_005, PATTERN_SB_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_001, PATTERN_SB_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_002, PATTERN_SB_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_003, PATTERN_SB_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_004, PATTERN_SB_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_005, PATTERN_SB_005))

    def test_continuous_supervision_annual_known_005_ready_fields(self) -> None:
        c = _by_id(self.known, "continuous_supervision_annual_known_005")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "603150")
        self.assertEqual(c["company_name"], "万朗磁塑")
        self.assertEqual(c["title_pattern"], PATTERN_SUP_005)
        self.assertEqual(c["date_start"], "2025-04-28")
        self.assertEqual(c["date_end"], "2025-05-01")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertIn(PATTERN_SUP_005, HARVEST_SUP_005)
        self.assertNotEqual(c["title_pattern"], PATTERN_SUP_001)
        self.assertNotEqual(c["title_pattern"], PATTERN_SUP_002)
        self.assertNotEqual(c["title_pattern"], PATTERN_SUP_003)
        self.assertNotEqual(c["title_pattern"], PATTERN_SUP_004)
        self.assertTrue(retrieval._title_matches(HARVEST_SUP_005, PATTERN_SUP_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_001, PATTERN_SUP_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_002, PATTERN_SUP_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_003, PATTERN_SUP_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_004, PATTERN_SUP_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_005, PATTERN_SUP_005))
        # known_001 宽串仍可命中本案标题，但本案 pattern 不得反向误抬恒立液压
        self.assertTrue(retrieval._title_matches(HARVEST_SUP_005, PATTERN_SUP_001))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_001, PATTERN_SUP_005))

    def test_patterns_mutually_distinct(self) -> None:
        patterns = [
            PATTERN_SB_001,
            PATTERN_SB_002,
            PATTERN_SB_003,
            PATTERN_SB_004,
            PATTERN_SB_005,
            PATTERN_SUP_001,
            PATTERN_SUP_002,
            PATTERN_SUP_003,
            PATTERN_SUP_004,
            PATTERN_SUP_005,
        ]
        self.assertEqual(len(patterns), len(set(patterns)))
        self.assertFalse(retrieval._title_matches(HARVEST_SB_005, PATTERN_SUP_005))
        self.assertFalse(retrieval._title_matches(HARVEST_SUP_005, PATTERN_SB_005))

    def test_harvest_titles_route_correctly(self) -> None:
        for title in (HARVEST_SB_005, HARVEST_SUP_005):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")
                self.assertNotEqual(r.predicted_document_type, "annual_report")
                self.assertNotEqual(r.predicted_document_type, "board_resolution")

    def test_prior_paths_not_regressed(self) -> None:
        for title, expected in (
            (HARVEST_SB_001, "announcement"),
            (HARVEST_SB_002, "announcement"),
            (HARVEST_SB_003, "announcement"),
            (HARVEST_SB_004, "announcement"),
            (HARVEST_SUP_001, "announcement"),
            (HARVEST_SUP_002, "announcement"),
            (HARVEST_SUP_003, "announcement"),
            (HARVEST_SUP_004, "announcement"),
            (HARVEST_VO_004, "announcement"),
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
            "supervisory_board_known_001",
            "supervisory_board_known_002",
            "supervisory_board_known_003",
            "supervisory_board_known_004",
            "continuous_supervision_annual_known_001",
            "continuous_supervision_annual_known_002",
            "continuous_supervision_annual_known_003",
            "continuous_supervision_annual_known_004",
            "verification_opinion_known_004",
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
            "supervisory_board_known_005",
            "continuous_supervision_annual_known_005",
        ):
            with self.subTest(case_id=case_id):
                case = _by_id(self.known, case_id)
                row = retrieval._process_case(
                    case, "known_document", registry_ids, document_types, dry_run=True
                )
                self.assertEqual(row["dry_run_status"], "ready_for_future_live_validation")
                self.assertEqual(row["would_query"], "true")
                notes = case["notes"]
                self.assertIn("B-FM-54", notes)
                self.assertTrue(any("\u4e00" <= ch <= "\u9fff" for ch in notes))


if __name__ == "__main__":
    unittest.main()
