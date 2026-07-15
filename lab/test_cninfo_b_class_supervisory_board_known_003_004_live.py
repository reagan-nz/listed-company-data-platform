"""
B-FM-51：监事会决议 known_004 / 董事会决议 known_003 live allow-list 锁测（离线）。

覆盖：
- allow-list 仅含 supervisory_board_known_004 与 board_resolution_known_003（category 空）
- 字段与 fixtures ready 对齐
- mock live 路径可对两案得到 pass（监事会 → announcement；董事会 → board_resolution）
- 不包含 supervisory known_001–003、board known_001/002 及 B-FM-50 等已 LIVE_PASS 案

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_supervisory_board_known_003_004_live.py
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
    "cninfo_b_class_supervisory_board_known_003_004_live_20260715",
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_EMPTY = os.path.join(LIVE_DIR, "category_sample_cases_live_empty.yaml")
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

HARVEST_SB = "海汽集团第四届监事会第三十次会议决议公告"
HARVEST_BOARD = "第五届董事会第五次会议决议公告"
ANN_SB = "1224016686"
ANN_BOARD = "1224036271"
# 2025-06-27 / 2025-06-30 00:00:00 UTC
ANN_TS_SB_MS = 1750982400000
ANN_TS_BOARD_MS = 1751241600000


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestSupervisoryBoardKnown003004LiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_two_known_cases(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_EMPTY)
        self.assertEqual(
            [c["case_id"] for c in known],
            [
                "supervisory_board_known_004",
                "board_resolution_known_003",
            ],
        )
        self.assertEqual(category, [])
        self.assertTrue(all(c["case_status"] == "ready" for c in known))
        ids = {c["case_id"] for c in known}
        for closed in (
            "supervisory_board_known_001",
            "supervisory_board_known_002",
            "supervisory_board_known_003",
            "board_resolution_known_001",
            "board_resolution_known_002",
            "company_articles_known_005",
            "employee_stock_ownership_plan_known_003",
            "listing_sponsor_known_001",
            "asset_valuation_explanation_known_001",
            "independent_director_meeting_review_known_001",
            "continuous_supervision_training_known_001",
            "audit_report_known_001",
            "shareholder_meeting_known_007",
        ):
            self.assertNotIn(closed, ids)

    def test_allowlist_fields_match_fixtures(self) -> None:
        allow = _load_cases(KNOWN_ALLOW)
        fixture = _load_cases(FIXTURE_KNOWN)
        for case_id, expected_type in (
            ("supervisory_board_known_004", "announcement"),
            ("board_resolution_known_003", "board_resolution"),
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
            self.assertEqual(ak["expected_document_type"], expected_type)
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
                "supervisory_board_known_004",
                HARVEST_SB,
                ANN_SB,
                ANN_TS_SB_MS,
                "603069",
                "2025-06-27",
                "announcement",
            ),
            (
                "board_resolution_known_003",
                HARVEST_BOARD,
                ANN_BOARD,
                ANN_TS_BOARD_MS,
                "301027",
                "2025-06-30",
                "board_resolution",
            ),
        ]
        for case_id, title, ann_id, ts_ms, code, date_str, expected_type in fixtures:
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
            self.assertEqual(row_k["predicted_document_type"], expected_type, case_id)
            self.assertNotEqual(row_k["predicted_document_type"], "other", case_id)
            self.assertNotEqual(row_k["predicted_document_type"], "annual_report", case_id)
            if expected_type == "announcement":
                self.assertNotEqual(
                    row_k["predicted_document_type"], "board_resolution", case_id
                )
            self.assertEqual(
                row_k["predicted_route_to"], "cninfo_general_announcement_pdf", case_id
            )
            self.assertEqual(row_k["matched_title"], title, case_id)


if __name__ == "__main__":
    unittest.main()
