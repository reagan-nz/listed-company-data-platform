"""
B-FM-45：提名人声明 known_002 / 核查意见 known_003 live allow-list 锁测（离线）。

覆盖：
- allow-list 仅含 independent_director_nominee_declaration_known_002 与
  verification_opinion_known_003（category 空）
- 字段与 fixtures ready 对齐
- mock live 路径可对两案得到 pass（predicted_document_type=announcement；非 other）
- 不包含 nominee/VO known_001 及 B-FM-44 等已 LIVE_PASS 案

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_nominee_vo_known_002_003_live.py
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
    "cninfo_b_class_nominee_vo_known_002_003_live_20260715",
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_EMPTY = os.path.join(LIVE_DIR, "category_sample_cases_live_empty.yaml")
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

HARVEST_NOMINEE = "独立董事提名人声明与承诺（冯天俊）"
HARVEST_VO = (
    "国泰海通证券股份有限公司关于河南通达电缆股份有限公司"
    "募集资金投资项目结项并将节余募集资金永久补充流动资金的核查意见"
)
ANN_NOMINEE = "1223951151"
ANN_VO = "1223981802"
# 2025-06-20 / 2025-06-25 00:00:00 UTC
ANN_TS_NOMINEE_MS = 1750377600000
ANN_TS_VO_MS = 1750809600000


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestNomineeVoKnown002003LiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_two_known_cases(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_EMPTY)
        self.assertEqual(
            [c["case_id"] for c in known],
            [
                "independent_director_nominee_declaration_known_002",
                "verification_opinion_known_003",
            ],
        )
        self.assertEqual(category, [])
        self.assertTrue(all(c["case_status"] == "ready" for c in known))
        ids = {c["case_id"] for c in known}
        for closed in (
            "independent_director_nominee_declaration_known_001",
            "independent_director_meeting_review_known_001",
            "verification_opinion_known_001",
            "verification_opinion_known_002",
            "independent_director_annual_report_work_system_known_001",
            "independent_director_annual_report_work_system_known_002",
            "continuous_supervision_annual_known_002",
            "company_articles_known_002",
            "bond_trustee_report_known_002",
            "tracking_rating_report_known_002",
            "incentive_object_list_known_001",
            "sales_brief_known_001",
            "audit_report_known_001",
            "shareholder_meeting_known_007",
            "board_resolution_known_001",
        ):
            self.assertNotIn(closed, ids)

    def test_allowlist_fields_match_fixtures(self) -> None:
        allow = _load_cases(KNOWN_ALLOW)
        fixture = _load_cases(FIXTURE_KNOWN)
        for case_id in (
            "independent_director_nominee_declaration_known_002",
            "verification_opinion_known_003",
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
                "independent_director_nominee_declaration_known_002",
                HARVEST_NOMINEE,
                ANN_NOMINEE,
                ANN_TS_NOMINEE_MS,
                "000088",
                "2025-06-20",
            ),
            (
                "verification_opinion_known_003",
                HARVEST_VO,
                ANN_VO,
                ANN_TS_VO_MS,
                "002560",
                "2025-06-25",
            ),
        ]
        for case_id, title, ann_id, ts_ms, code, date_str in fixtures:
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
            self.assertEqual(
                row_k["predicted_route_to"], "cninfo_general_announcement_pdf", case_id
            )
            self.assertEqual(row_k["matched_title"], title, case_id)


if __name__ == "__main__":
    unittest.main()
