"""
B-FM-17：股东大会通知「的」助词变体 known-document live allow-list 锁测（离线；不请求 CNINFO）。

覆盖：
- allow-list 仅含 shareholder_meeting_known_002（category 空）
- 字段与 fixtures ready 对齐
- mock live 路径可对 known case 得到 pass

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_shareholder_meeting_known_002_live.py
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
    "cninfo_b_class_shareholder_meeting_known_002_live_20260715",
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_EMPTY = os.path.join(LIVE_DIR, "category_sample_cases_live_empty.yaml")
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

# harvest 证据标题（只读引用；BD2E292；本测不请求 CNINFO）
TITLE_NOTICE_DE = "关于召开2025年第三次临时股东大会的通知"
PATTERN_DE = "股东大会的通知"
ANN_ID = "1224014462"
# 2025-06-27 00:00:00 UTC
ANN_TS_MS = 1750982400000


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestShareholderMeetingKnown002LiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_one_known_case(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_EMPTY)
        self.assertEqual([c["case_id"] for c in known], ["shareholder_meeting_known_002"])
        self.assertEqual(category, [])
        self.assertEqual(known[0]["case_status"], "ready")

    def test_allowlist_fields_match_fixtures(self) -> None:
        ak = _by_id(_load_cases(KNOWN_ALLOW), "shareholder_meeting_known_002")
        fk = _by_id(_load_cases(FIXTURE_KNOWN), "shareholder_meeting_known_002")
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
            self.assertEqual(ak[key], fk[key], key)
        self.assertEqual(ak["title_pattern"], PATTERN_DE)
        self.assertEqual(ak["company_code"], "002237")
        self.assertEqual(ak["expected_document_type"], "shareholder_meeting_material")
        self.assertEqual(ak["expected_route_to"], "cninfo_general_announcement_pdf")

    def test_mock_live_known_pass(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        categories = os.path.join(_BASE, "config", "cninfo_announcement_categories.yaml")
        categories_config = m._load_yaml(categories)
        registry_ids = m._load_registry_source_ids(registry)
        document_types = m._load_document_types(schema)

        known_case = _by_id(_load_cases(KNOWN_ALLOW), "shareholder_meeting_known_002")
        fake_known = [
            {
                "announcementId": ANN_ID,
                "announcementTitle": TITLE_NOTICE_DE,
                "announcementTime": ANN_TS_MS,
                "adjunctUrl": f"/finalpage/2025-06-27/{ANN_ID}.PDF",
                "secCode": "002237",
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
        self.assertEqual(
            row_k["predicted_document_type"], "shareholder_meeting_material"
        )
        self.assertEqual(row_k["predicted_route_to"], "cninfo_general_announcement_pdf")
        self.assertEqual(row_k["matched_title"], TITLE_NOTICE_DE)


if __name__ == "__main__":
    unittest.main()
