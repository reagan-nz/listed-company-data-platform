"""
B-FM-39：子公司管理制度 / 薪酬与考核方案 known-document live allow-list 锁测（离线；不请求 CNINFO）。

覆盖：
- allow-list 仅含 subsidiary_management_system_known_001 与
  compensation_assessment_plan_known_001（category 空）
- 字段与 fixtures ready 对齐
- mock live 路径可对两案得到 pass（predicted_document_type=announcement；非 other）
- 不包含 monetary / external_guarantee / ined 等已 LIVE_PASS 案

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_subsidiary_compensation_known_001_live.py
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
    "cninfo_b_class_subsidiary_compensation_known_001_live_20260715",
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_EMPTY = os.path.join(LIVE_DIR, "category_sample_cases_live_empty.yaml")
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

HARVEST_SUB = "分、子公司管理制度（2025年6月）"
HARVEST_COMP = "利尔化学股份有限公司2025年度经营团队薪酬与考核方案"
ANN_SUB = "1223889267"
ANN_COMP = "1223834178"
# 近似毫秒时间戳（mock）
ANN_TS_SUB = 1750032000000  # 2025-06-16
ANN_TS_COMP = 1749513600000  # 2025-06-10


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestSubsidiaryCompensationKnown001LiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_two_known_cases(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_EMPTY)
        self.assertEqual(
            [c["case_id"] for c in known],
            [
                "subsidiary_management_system_known_001",
                "compensation_assessment_plan_known_001",
            ],
        )
        self.assertEqual(category, [])
        self.assertTrue(all(c["case_status"] == "ready" for c in known))
        ids = {c["case_id"] for c in known}
        for closed in (
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
        ):
            self.assertNotIn(closed, ids)

    def test_allowlist_fields_match_fixtures(self) -> None:
        allow = _load_cases(KNOWN_ALLOW)
        fixture = _load_cases(FIXTURE_KNOWN)
        for case_id in (
            "subsidiary_management_system_known_001",
            "compensation_assessment_plan_known_001",
        ):
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

    def test_mock_live_both_cases_pass(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        categories = os.path.join(_BASE, "config", "cninfo_announcement_categories.yaml")
        categories_config = m._load_yaml(categories)
        registry_ids = m._load_registry_source_ids(registry)
        document_types = m._load_document_types(schema)

        fixtures = [
            (
                "subsidiary_management_system_known_001",
                HARVEST_SUB,
                ANN_SUB,
                "300261",
                "2025-06-16",
                ANN_TS_SUB,
            ),
            (
                "compensation_assessment_plan_known_001",
                HARVEST_COMP,
                ANN_COMP,
                "002258",
                "2025-06-10",
                ANN_TS_COMP,
            ),
        ]
        for case_id, title, ann_id, code, date_str, ts in fixtures:
            known_case = _by_id(_load_cases(KNOWN_ALLOW), case_id)
            fake = [
                {
                    "announcementId": ann_id,
                    "announcementTitle": title,
                    "announcementTime": ts,
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
            self.assertEqual(
                row_k["predicted_route_to"], "cninfo_general_announcement_pdf", case_id
            )
            self.assertEqual(row_k["matched_title"], title, case_id)


if __name__ == "__main__":
    unittest.main()
