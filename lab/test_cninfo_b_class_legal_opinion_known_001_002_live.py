"""
B-FM-25：法律意见书 known-document live allow-list 锁测（离线；不请求 CNINFO）。

覆盖：
- allow-list 仅含 legal_opinion_known_001 与 known_002（category 空）
- 字段与 fixtures ready 对齐
- mock live 路径可对两案得到 pass（predicted_document_type=announcement）
- 不包含 supervisory_board / shareholder_meeting 已 LIVE_PASS 案

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_legal_opinion_known_001_002_live.py
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
    "cninfo_b_class_legal_opinion_known_001_002_live_20260715",
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_EMPTY = os.path.join(LIVE_DIR, "category_sample_cases_live_empty.yaml")
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

HARVEST_001 = "2025年第一次临时股东大会的法律意见书"
HARVEST_002 = (
    "北京市星河律师事务所关于北京金自天正智能控制股份有限公司"
    "2024年年度股东会的法律意见书"
)
ANN_001 = "1223733432"
ANN_002 = "1223998801"
# 2025-06-02 / 2025-06-26 00:00:00 UTC
ANN_TS_001_MS = 1748822400000
ANN_TS_002_MS = 1750896000000


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestLegalOpinionKnown001002LiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_two_known_cases(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_EMPTY)
        self.assertEqual(
            [c["case_id"] for c in known],
            ["legal_opinion_known_001", "legal_opinion_known_002"],
        )
        self.assertEqual(category, [])
        self.assertTrue(all(c["case_status"] == "ready" for c in known))
        ids = {c["case_id"] for c in known}
        for closed in (
            "supervisory_board_known_001",
            "supervisory_board_known_002",
            "shareholder_meeting_known_001",
            "shareholder_meeting_known_002",
            "shareholder_meeting_known_003",
            "shareholder_meeting_known_004",
            "shareholder_meeting_known_005",
            "shareholder_meeting_known_006",
            "shareholder_meeting_known_007",
            "board_resolution_known_001",
        ):
            self.assertNotIn(closed, ids)

    def test_allowlist_fields_match_fixtures(self) -> None:
        allow = _load_cases(KNOWN_ALLOW)
        fixture = _load_cases(FIXTURE_KNOWN)
        for case_id in ("legal_opinion_known_001", "legal_opinion_known_002"):
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
                "legal_opinion_known_001",
                HARVEST_001,
                ANN_001,
                ANN_TS_001_MS,
                "002756",
                "2025-06-02",
            ),
            (
                "legal_opinion_known_002",
                HARVEST_002,
                ANN_002,
                ANN_TS_002_MS,
                "600560",
                "2025-06-26",
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
            self.assertEqual(
                row_k["predicted_route_to"], "cninfo_general_announcement_pdf", case_id
            )
            self.assertEqual(row_k["matched_title"], title, case_id)


if __name__ == "__main__":
    unittest.main()
