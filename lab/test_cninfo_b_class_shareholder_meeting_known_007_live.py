"""
B-FM-22：「年度股东会决议」known-document live allow-list 锁测（离线；不请求 CNINFO）。

覆盖：
- allow-list 仅含 shareholder_meeting_known_007（category 空）
- 字段与 fixtures ready 对齐
- mock live 路径可对 known_007 得到 pass
- 不包含 known_001–006（已 LIVE_PASS）

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_shareholder_meeting_known_007_live.py
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
    "cninfo_b_class_shareholder_meeting_known_007_live_20260715",
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_EMPTY = os.path.join(LIVE_DIR, "category_sample_cases_live_empty.yaml")
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

# harvest 证据（只读引用；本测不请求 CNINFO）
SHORT_ANNUAL = "2024年年度股东会决议公告"
ANN_ID = "1223981729"
# 2025-06-25 00:00:00 UTC
ANN_TS_MS = 1750809600000


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestShareholderMeetingKnown007LiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_one_known_case(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_EMPTY)
        self.assertEqual(
            [c["case_id"] for c in known],
            ["shareholder_meeting_known_007"],
        )
        self.assertEqual(category, [])
        self.assertTrue(all(c["case_status"] == "ready" for c in known))
        # 明确不重开已 LIVE_PASS 案
        ids = {c["case_id"] for c in known}
        for closed in (
            "shareholder_meeting_known_001",
            "shareholder_meeting_known_002",
            "shareholder_meeting_known_003",
            "shareholder_meeting_known_004",
            "shareholder_meeting_known_005",
            "shareholder_meeting_known_006",
        ):
            self.assertNotIn(closed, ids)

    def test_allowlist_fields_match_fixtures(self) -> None:
        ak = _by_id(_load_cases(KNOWN_ALLOW), "shareholder_meeting_known_007")
        fk = _by_id(_load_cases(FIXTURE_KNOWN), "shareholder_meeting_known_007")
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
            self.assertEqual(ak[key], fk[key], f"shareholder_meeting_known_007.{key}")
        self.assertEqual(ak["expected_document_type"], "shareholder_meeting_material")
        self.assertEqual(ak["expected_route_to"], "cninfo_general_announcement_pdf")

    def test_mock_live_known_007_pass(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        categories = os.path.join(_BASE, "config", "cninfo_announcement_categories.yaml")
        categories_config = m._load_yaml(categories)
        registry_ids = m._load_registry_source_ids(registry)
        document_types = m._load_document_types(schema)

        known_case = _by_id(_load_cases(KNOWN_ALLOW), "shareholder_meeting_known_007")
        fake_known = [
            {
                "announcementId": ANN_ID,
                "announcementTitle": SHORT_ANNUAL,
                "announcementTime": ANN_TS_MS,
                "adjunctUrl": f"/finalpage/2025-06-25/{ANN_ID}.PDF",
                "secCode": "001335",
            }
        ]
        with mock.patch.object(m, "resolve_orgid_via_topsearch", return_value="org-mock"):
            with mock.patch.object(
                m, "fetch_announcements", return_value=(fake_known, "executed", "")
            ):
                with mock.patch.object(m.time, "sleep", return_value=None):
                    row_k, qcount = m.process_live_known_case(
                        known_case, registry_ids, document_types, categories_config
                    )
        self.assertEqual(qcount, 1)
        self.assertEqual(row_k["case_result"], "pass")
        self.assertEqual(row_k["predicted_document_type"], "shareholder_meeting_material")
        self.assertEqual(row_k["predicted_route_to"], "cninfo_general_announcement_pdf")
        self.assertEqual(row_k["matched_title"], SHORT_ANNUAL)


if __name__ == "__main__":
    unittest.main()
