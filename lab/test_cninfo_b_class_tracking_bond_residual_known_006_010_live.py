"""
B-FM-02（R19）：跟踪评级 known_006–010 + 债券受托 known_005–007 live allow-list 锁测（离线）。

覆盖：
- allow-list 仅含本包 8 案（category 空）
- 字段与 fixtures ready 对齐
- mock live 路径可对八案得到 pass（→ announcement）
- 不包含已 LIVE_PASS 旧案；不含 deferred known_002

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_tracking_bond_residual_known_006_010_live.py
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_b_class_corpus_retrieval as m  # noqa: E402

LIVE_DIR = os.path.join(
    _BASE,
    "outputs",
    "validation",
    "cninfo_b_class_tracking_bond_residual_known_006_010_live_20260716",
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_EMPTY = os.path.join(LIVE_DIR, "category_sample_cases_live_empty.yaml")
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

ALLOW_IDS = [
    "tracking_rating_report_known_006",
    "tracking_rating_report_known_007",
    "tracking_rating_report_known_008",
    "tracking_rating_report_known_009",
    "tracking_rating_report_known_010",
    "bond_trustee_report_known_005",
    "bond_trustee_report_known_006",
    "bond_trustee_report_known_007",
]

# (case_id, title, ann_id, ts_ms, code, date_str)
# ts_ms = UTC midnight of announcement_date
MOCK_FIXTURES = [
    (
        "tracking_rating_report_known_006",
        "2020年深圳市华阳国际工程设计股份有限公司公开发行可转换公司债券2025年跟踪评级报告",
        "1223952243",
        1750377600000,  # 2025-06-20
        "002949",
        "2025-06-20",
    ),
    (
        "tracking_rating_report_known_007",
        "广联航空工业股份有限公司相关债券2025年跟踪评级报告",
        "1224016467",
        1750982400000,  # 2025-06-27
        "300900",
        "2025-06-27",
    ),
    (
        "tracking_rating_report_known_008",
        "立讯精密工业股份有限公司公开发行可转换公司债券2025年跟踪评级报告",
        "1224016122",
        1750982400000,  # 2025-06-27
        "002475",
        "2025-06-27",
    ),
    (
        "tracking_rating_report_known_009",
        "天合光能股份有限公司向不特定对象发行可转换公司债券2025年跟踪评级报告",
        "1223956820",
        1750636800000,  # 2025-06-23
        "688599",
        "2025-06-23",
    ),
    (
        "tracking_rating_report_known_010",
        "广州航新航空科技股份有限公司公开发行可转换公司债券定期跟踪评级报告",
        "1224012941",
        1750982400000,  # 2025-06-27
        "300424",
        "2025-06-27",
    ),
    (
        "bond_trustee_report_known_005",
        "中国南方航空股份有限公司公开发行A股可转换公司债券受托管理事务报告（2024年度）",
        "1224014795",
        1750982400000,  # 2025-06-27
        "600029",
        "2025-06-27",
    ),
    (
        "bond_trustee_report_known_006",
        "铜陵有色金属集团股份有限公司向特定对象发行可转换公司债券受托管理事务报告（2024年度）",
        "1223997318",
        1750896000000,  # 2025-06-26
        "000630",
        "2025-06-26",
    ),
    (
        "bond_trustee_report_known_007",
        "山西美锦能源股份有限公司公开发行可转换公司债券2024年度受托管理事务报告",
        "1224016384",
        1751155200000,  # 2025-06-29
        "000723",
        "2025-06-29",
    ),
]


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestTrackingBondResidualKnown006010LiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_eight_known_cases(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_EMPTY)
        self.assertEqual([c["case_id"] for c in known], ALLOW_IDS)
        self.assertEqual(category, [])
        self.assertTrue(all(c["case_status"] == "ready" for c in known))
        ids = {c["case_id"] for c in known}
        for closed in (
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
            self.assertNotIn(closed, ids)

    def test_allowlist_fields_match_fixtures(self) -> None:
        allow = _load_cases(KNOWN_ALLOW)
        fixture = _load_cases(FIXTURE_KNOWN)
        for case_id in ALLOW_IDS:
            ak = _by_id(allow, case_id)
            fk = _by_id(fixture, case_id)
            for key in (
                "company_code",
                "company_name",
                "title_pattern",
                "expected_document_type",
                "date_start",
                "date_end",
                "expected_route_to",
                "source_id",
            ):
                self.assertEqual(ak[key], fk[key], f"{case_id}.{key}")
            self.assertEqual(ak["expected_document_type"], "announcement")
            self.assertEqual(ak["expected_route_to"], "cninfo_general_announcement_pdf")

    def test_mock_live_eight_cases_pass(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        categories = os.path.join(_BASE, "config", "cninfo_announcement_categories.yaml")
        categories_config = m._load_yaml(categories)
        registry_ids = m._load_registry_source_ids(registry)
        document_types = m._load_document_types(schema)

        for case_id, title, ann_id, ts_ms, code, date_str in MOCK_FIXTURES:
            known_case = _by_id(_load_cases(KNOWN_ALLOW), case_id)
            fake = [
                {
                    "announcementId": ann_id,
                    "announcementTitle": title,
                    "announcementTime": ts_ms,
                    "adjunctUrl": f"/finalpage/{date_str}/{ann_id}.PDF",
                    "secCode": code,
                }
            ]
            with mock.patch.object(m, "resolve_orgid_via_topsearch", return_value="org-mock"):
                with mock.patch.object(
                    m, "fetch_announcements", return_value=(fake, "executed", "")
                ):
                    with mock.patch.object(m.time, "sleep", return_value=None):
                        row_k, qcount = m.process_live_known_case(
                            known_case, registry_ids, document_types, categories_config
                        )
            self.assertEqual(qcount, 1, case_id)
            self.assertEqual(row_k["case_result"], "pass", case_id)
            self.assertEqual(row_k["predicted_document_type"], "announcement", case_id)
            self.assertNotEqual(row_k["predicted_document_type"], "other", case_id)
            self.assertNotEqual(row_k["predicted_document_type"], "annual_report", case_id)
            self.assertEqual(
                row_k["predicted_route_to"], "cninfo_general_announcement_pdf", case_id
            )
            self.assertEqual(row_k["matched_title"], title, case_id)


if __name__ == "__main__":
    unittest.main()
