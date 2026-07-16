"""
B-FM-02（R19）：跟踪评级 known_006–010 + 债券受托 known_005–007 晋升锁测（离线）。

覆盖：
- tracking_rating_report_known_006–010 已为 ready
- bond_trustee_report_known_005–007 已为 ready
- title_pattern 与 known_001–005（tracking）/ known_001–004（bond）可区分
- harvest 标题经既有路由预测为 announcement
- 既有 LIVE_PASS 路径不回退；拒绝 deferred known_002 与 audit 年报陷阱

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_tracking_bond_residual_known_006_010_promotion.py
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

# 本包 harvest
HARVEST_TR_006 = (
    "2020年深圳市华阳国际工程设计股份有限公司公开发行可转换公司债券2025年跟踪评级报告"
)
HARVEST_TR_007 = "广联航空工业股份有限公司相关债券2025年跟踪评级报告"
HARVEST_TR_008 = "立讯精密工业股份有限公司公开发行可转换公司债券2025年跟踪评级报告"
HARVEST_TR_009 = "天合光能股份有限公司向不特定对象发行可转换公司债券2025年跟踪评级报告"
HARVEST_TR_010 = "广州航新航空科技股份有限公司公开发行可转换公司债券定期跟踪评级报告"
HARVEST_BT_005 = (
    "中国南方航空股份有限公司公开发行A股可转换公司债券受托管理事务报告（2024年度）"
)
HARVEST_BT_006 = (
    "铜陵有色金属集团股份有限公司向特定对象发行可转换公司债券受托管理事务报告（2024年度）"
)
HARVEST_BT_007 = "山西美锦能源股份有限公司公开发行可转换公司债券2024年度受托管理事务报告"

# 既有 harvest（防回退 / 互斥）
HARVEST_TR_001 = "2020年浙江华海药业股份有限公司公开发行可转换公司债券定期跟踪评级报告"
HARVEST_TR_002 = "长江证券股份有限公司2025年跟踪评级报告"
HARVEST_TR_003 = (
    "中国宝安集团股份有限公司2022年面向合格投资者公开发行公司债券(第一期)定期跟踪评级报告"
)
HARVEST_TR_004 = "南京聚隆科技股份有限公司相关债券2025年跟踪评级报告"
HARVEST_TR_005 = "杭州申昊科技股份有限公司主体及“申昊转债”2025年度跟踪评级报告"
HARVEST_BT_001 = (
    "申港证券股份有限公司关于三羊马(重庆)物流股份有限公司向不特定对象"
    "发行可转换公司债券受托管理事务报告（2024年度）"
)
HARVEST_BT_002 = "深圳能源集团股份有限公司公司债券受托管理事务报告（2024年度）"
HARVEST_BT_003 = (
    "中联重科股份有限公司2019年面向合格投资者公开发行公司债券（第一期）"
    "受托管理事务报告（2024年度）"
)
HARVEST_BT_004 = "京东方科技集团股份有限公司可续期公司债券受托管理事务报告（2024年度）"

PATTERN_TR_006 = (
    "深圳市华阳国际工程设计股份有限公司公开发行可转换公司债券2025年跟踪评级报告"
)
PATTERN_TR_007 = "广联航空工业股份有限公司相关债券2025年跟踪评级报告"
PATTERN_TR_008 = "立讯精密工业股份有限公司公开发行可转换公司债券2025年跟踪评级报告"
PATTERN_TR_009 = "向不特定对象发行可转换公司债券2025年跟踪评级报告"
PATTERN_TR_010 = "广州航新航空科技股份有限公司公开发行可转换公司债券定期跟踪评级报告"
PATTERN_BT_005 = "公开发行A股可转换公司债券受托管理事务报告（2024年度）"
PATTERN_BT_006 = "向特定对象发行可转换公司债券受托管理事务报告（2024年度）"
PATTERN_BT_007 = "公开发行可转换公司债券2024年度受托管理事务报告"

PATTERN_TR_001 = "跟踪评级报告"
PATTERN_TR_002 = "股份有限公司2025年跟踪评级报告"
PATTERN_TR_003 = "公开发行公司债券(第一期)定期跟踪评级报告"
PATTERN_TR_004 = "相关债券2025年跟踪评级报告"
PATTERN_TR_005 = "主体及“申昊转债”2025年度跟踪评级报告"
PATTERN_BT_001 = "可转换公司债券受托管理事务报告（2024年度）"
PATTERN_BT_002 = "股份有限公司公司债券受托管理事务报告（2024年度）"
PATTERN_BT_003 = "公开发行公司债券（第一期）受托管理事务报告（2024年度）"
PATTERN_BT_004 = "可续期公司债券受托管理事务报告（2024年度）"
SM_RES = "2025年第二次临时股东大会决议公告"

NEW_CASE_IDS = (
    "tracking_rating_report_known_006",
    "tracking_rating_report_known_007",
    "tracking_rating_report_known_008",
    "tracking_rating_report_known_009",
    "tracking_rating_report_known_010",
    "bond_trustee_report_known_005",
    "bond_trustee_report_known_006",
    "bond_trustee_report_known_007",
)

NEW_SPECS = (
    (
        "tracking_rating_report_known_006",
        "002949",
        "华阳国际",
        PATTERN_TR_006,
        "2025-06-19",
        "2025-06-22",
        HARVEST_TR_006,
    ),
    (
        "tracking_rating_report_known_007",
        "300900",
        "广联航空",
        PATTERN_TR_007,
        "2025-06-26",
        "2025-06-29",
        HARVEST_TR_007,
    ),
    (
        "tracking_rating_report_known_008",
        "002475",
        "立讯精密",
        PATTERN_TR_008,
        "2025-06-26",
        "2025-06-29",
        HARVEST_TR_008,
    ),
    (
        "tracking_rating_report_known_009",
        "688599",
        "天合光能",
        PATTERN_TR_009,
        "2025-06-22",
        "2025-06-25",
        HARVEST_TR_009,
    ),
    (
        "tracking_rating_report_known_010",
        "300424",
        "航新科技",
        PATTERN_TR_010,
        "2025-06-26",
        "2025-06-29",
        HARVEST_TR_010,
    ),
    (
        "bond_trustee_report_known_005",
        "600029",
        "南方航空",
        PATTERN_BT_005,
        "2025-06-26",
        "2025-06-29",
        HARVEST_BT_005,
    ),
    (
        "bond_trustee_report_known_006",
        "000630",
        "铜陵有色",
        PATTERN_BT_006,
        "2025-06-25",
        "2025-06-28",
        HARVEST_BT_006,
    ),
    (
        "bond_trustee_report_known_007",
        "000723",
        "美锦能源",
        PATTERN_BT_007,
        "2025-06-28",
        "2025-07-01",
        HARVEST_BT_007,
    ),
)


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestTrackingBondResidualKnown006010Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_new_cases_ready_fields(self) -> None:
        for case_id, code, name, pattern, d0, d1, harvest in NEW_SPECS:
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                self.assertEqual(c["case_status"], "ready")
                self.assertEqual(c["company_code"], code)
                self.assertEqual(c["company_name"], name)
                self.assertEqual(c["title_pattern"], pattern)
                self.assertEqual(c["date_start"], d0)
                self.assertEqual(c["date_end"], d1)
                self.assertEqual(c["expected_document_type"], "announcement")
                self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
                self.assertTrue(c["expected_pdf_url_available"])
                self.assertIn(pattern, harvest)
                self.assertTrue(retrieval._title_matches(harvest, pattern))
                self.assertIn("B-FM-02", c["notes"])
                self.assertTrue(any("\u4e00" <= ch <= "\u9fff" for ch in c["notes"]))

    def test_patterns_mutually_distinct(self) -> None:
        patterns = [
            PATTERN_TR_001,
            PATTERN_TR_002,
            PATTERN_TR_003,
            PATTERN_TR_004,
            PATTERN_TR_005,
            PATTERN_TR_006,
            PATTERN_TR_007,
            PATTERN_TR_008,
            PATTERN_TR_009,
            PATTERN_TR_010,
            PATTERN_BT_001,
            PATTERN_BT_002,
            PATTERN_BT_003,
            PATTERN_BT_004,
            PATTERN_BT_005,
            PATTERN_BT_006,
            PATTERN_BT_007,
        ]
        self.assertEqual(len(patterns), len(set(patterns)))

    def test_new_patterns_do_not_cross_hit_priors(self) -> None:
        new_patterns = {
            "TR006": PATTERN_TR_006,
            "TR007": PATTERN_TR_007,
            "TR008": PATTERN_TR_008,
            "TR009": PATTERN_TR_009,
            "TR010": PATTERN_TR_010,
            "BT005": PATTERN_BT_005,
            "BT006": PATTERN_BT_006,
            "BT007": PATTERN_BT_007,
        }
        prior_harvests = {
            "TR001": HARVEST_TR_001,
            "TR002": HARVEST_TR_002,
            "TR003": HARVEST_TR_003,
            "TR004": HARVEST_TR_004,
            "TR005": HARVEST_TR_005,
            "BT001": HARVEST_BT_001,
            "BT002": HARVEST_BT_002,
            "BT003": HARVEST_BT_003,
            "BT004": HARVEST_BT_004,
        }
        own = {
            "TR006": HARVEST_TR_006,
            "TR007": HARVEST_TR_007,
            "TR008": HARVEST_TR_008,
            "TR009": HARVEST_TR_009,
            "TR010": HARVEST_TR_010,
            "BT005": HARVEST_BT_005,
            "BT006": HARVEST_BT_006,
            "BT007": HARVEST_BT_007,
        }
        for pid, pat in new_patterns.items():
            with self.subTest(pattern=pid):
                self.assertTrue(retrieval._title_matches(own[pid], pat))
                for hid, title in prior_harvests.items():
                    self.assertFalse(
                        retrieval._title_matches(title, pat),
                        f"{pid} should not match prior {hid}",
                    )
                for oid, title in own.items():
                    if oid == pid:
                        continue
                    self.assertFalse(
                        retrieval._title_matches(title, pat),
                        f"{pid} should not match sibling {oid}",
                    )

    def test_harvest_titles_route_correctly(self) -> None:
        for title in (
            HARVEST_TR_006,
            HARVEST_TR_007,
            HARVEST_TR_008,
            HARVEST_TR_009,
            HARVEST_TR_010,
            HARVEST_BT_005,
            HARVEST_BT_006,
            HARVEST_BT_007,
        ):
            with self.subTest(title=title[:40]):
                r = routing.route_title(title, self.config)
                self.assertEqual(r.predicted_document_type, "announcement")
                self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
                self.assertNotEqual(r.predicted_document_type, "other")
                self.assertNotEqual(r.predicted_document_type, "annual_report")

    def test_prior_paths_not_regressed(self) -> None:
        for title, expected in (
            (HARVEST_TR_001, "announcement"),
            (HARVEST_TR_002, "announcement"),
            (HARVEST_TR_003, "announcement"),
            (HARVEST_TR_004, "announcement"),
            (HARVEST_TR_005, "announcement"),
            (HARVEST_BT_001, "announcement"),
            (HARVEST_BT_002, "announcement"),
            (HARVEST_BT_003, "announcement"),
            (HARVEST_BT_004, "announcement"),
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
            "tracking_rating_report_known_001",
            "tracking_rating_report_known_002",
            "tracking_rating_report_known_003",
            "tracking_rating_report_known_004",
            "tracking_rating_report_known_005",
            "bond_trustee_report_known_001",
            "bond_trustee_report_known_002",
            "bond_trustee_report_known_003",
            "bond_trustee_report_known_004",
            "supervisory_board_known_005",
            "continuous_supervision_annual_known_005",
            "listing_sponsor_known_001",
            "equity_change_report_known_001",
            "independent_director_meeting_review_known_001",
            "asset_valuation_explanation_known_001",
            "continuous_supervision_training_known_001",
            "audit_report_known_001",
        ):
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                self.assertEqual(c["case_status"], "ready")

    def test_deferred_known_002_families_not_promoted(self) -> None:
        ids = {c["case_id"] for c in self.known}
        for case_id in (
            "independent_director_meeting_review_known_002",
            "asset_valuation_explanation_known_002",
            "listing_sponsor_known_002",
            "continuous_supervision_training_known_002",
            "audit_report_known_002",
            "equity_change_report_known_002",
        ):
            self.assertNotIn(case_id, ids)

    def test_new_ready_cases_pass_dry_run_field_validation(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        registry_ids = retrieval._load_registry_source_ids(registry)
        document_types = retrieval._load_document_types(schema)
        for case_id in NEW_CASE_IDS:
            with self.subTest(case_id=case_id):
                case = _by_id(self.known, case_id)
                row = retrieval._process_case(
                    case, "known_document", registry_ids, document_types, dry_run=True
                )
                self.assertEqual(row["dry_run_status"], "ready_for_future_live_validation")
                self.assertEqual(row["would_query"], "true")


if __name__ == "__main__":
    unittest.main()
