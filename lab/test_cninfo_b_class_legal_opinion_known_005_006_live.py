"""
B-FM-31：可转债 / 激励行权价格调整法律意见书 known-document live allow-list 锁测（离线；不请求 CNINFO）。

覆盖：
- allow-list 仅含 legal_opinion_known_005 与 known_006（category 空）
- 字段与 fixtures ready 对齐
- mock live 路径可对两案得到 pass（predicted_document_type=announcement；非 other）
- 不包含 legal_opinion_known_001–004 及 continuous_supervision / bond_trustee 等已 LIVE_PASS 案

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_legal_opinion_known_005_006_live.py
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
    "cninfo_b_class_legal_opinion_known_005_006_live_20260715",
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_EMPTY = os.path.join(LIVE_DIR, "category_sample_cases_live_empty.yaml")
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

HARVEST_005 = (
    "浙江六和律师事务所关于苏州天准科技股份有限公司"
    "向不特定对象发行可转换公司债券的法律意见书"
)
HARVEST_006 = (
    "北京竞天公诚（杭州）律师事务所关于恒生电子股份有限公司"
    "调整2024年股票期权激励计划行权价格的法律意见书"
)
ANN_005 = "1223956527"
ANN_006 = "1223877213"
# 2025-06-23 / 2025-06-13 00:00:00 UTC
ANN_TS_005_MS = 1750636800000
ANN_TS_006_MS = 1749772800000


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestLegalOpinionKnown005006LiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_two_known_cases(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_EMPTY)
        self.assertEqual(
            [c["case_id"] for c in known],
            ["legal_opinion_known_005", "legal_opinion_known_006"],
        )
        self.assertEqual(category, [])
        self.assertTrue(all(c["case_status"] == "ready" for c in known))
        ids = {c["case_id"] for c in known}
        for closed in (
            "legal_opinion_known_001",
            "legal_opinion_known_002",
            "legal_opinion_known_003",
            "legal_opinion_known_004",
            "continuous_supervision_annual_known_001",
            "continuous_supervision_training_known_001",
            "bond_trustee_report_known_001",
            "tracking_rating_report_known_001",
            "listing_sponsor_known_001",
            "equity_change_report_known_001",
            "verification_opinion_known_001",
            "supervisory_board_known_001",
            "shareholder_meeting_known_001",
            "board_resolution_known_001",
        ):
            self.assertNotIn(closed, ids)

    def test_allowlist_fields_match_fixtures(self) -> None:
        allow = _load_cases(KNOWN_ALLOW)
        fixture = _load_cases(FIXTURE_KNOWN)
        for case_id in ("legal_opinion_known_005", "legal_opinion_known_006"):
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
            self.assertIn("法律意见书", ak["title_pattern"])

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
                "legal_opinion_known_005",
                HARVEST_005,
                ANN_005,
                ANN_TS_005_MS,
                "688003",
                "2025-06-23",
            ),
            (
                "legal_opinion_known_006",
                HARVEST_006,
                ANN_006,
                ANN_TS_006_MS,
                "600570",
                "2025-06-13",
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
