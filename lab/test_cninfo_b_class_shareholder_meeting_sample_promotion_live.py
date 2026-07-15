"""
B-FM-15：股东大会通知 category-sample promotion live allow-list 锁测（离线；不请求 CNINFO）。

覆盖：
- allow-list 仅含 meeting_sample_002（known 空）
- 字段与 fixtures ready 对齐
- mock live 路径可对 category case 得到 pass

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion_live.py
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
    "cninfo_b_class_shareholder_meeting_sample_promotion_live_20260715",
)
KNOWN_EMPTY = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_empty.yaml")
CATEGORY_ALLOW = os.path.join(
    LIVE_DIR, "category_sample_cases_live_allowlist.yaml"
)
FIXTURE_CATEGORY = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "category_sample_cases.yaml"
)

# harvest 证据标题（只读引用；BD2E574；本测不请求 CNINFO）
TITLE_NOTICE = "关于召开2025年度第二次临时股东大会通知的公告"
PATTERN = "股东大会通知"
ANN_ID = "1223974102"
# 2025-06-24 00:00:00 UTC
ANN_TS_MS = 1750723200000


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(yaml.safe_load(f).get("cases") or [])


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestShareholderMeetingSamplePromotionLiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_one_category_case(self) -> None:
        known = _load_cases(KNOWN_EMPTY)
        category = _load_cases(CATEGORY_ALLOW)
        self.assertEqual(known, [])
        self.assertEqual([c["case_id"] for c in category], ["meeting_sample_002"])
        self.assertEqual(category[0]["case_status"], "ready")

    def test_allowlist_fields_match_fixtures(self) -> None:
        ac = _by_id(_load_cases(CATEGORY_ALLOW), "meeting_sample_002")
        fc = _by_id(_load_cases(FIXTURE_CATEGORY), "meeting_sample_002")
        for key in (
            "title_pattern",
            "date_start",
            "date_end",
            "source_id",
            "source_category",
            "expected_min_results",
        ):
            self.assertEqual(ac[key], fc[key], key)
        self.assertEqual(ac["title_pattern"], PATTERN)
        self.assertEqual(
            sorted(ac["expected_document_types"]),
            sorted(fc["expected_document_types"]),
        )
        self.assertEqual(
            ac["false_positive_guard_patterns"],
            fc["false_positive_guard_patterns"],
        )
        self.assertEqual(ac["source_id"], "cninfo_general_announcement_pdf")

    def test_mock_live_category_pass(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        categories = os.path.join(_BASE, "config", "cninfo_announcement_categories.yaml")
        categories_config = m._load_yaml(categories)
        registry_ids = m._load_registry_source_ids(registry)
        document_types = m._load_document_types(schema)

        cat_case = _by_id(_load_cases(CATEGORY_ALLOW), "meeting_sample_002")
        fake_cat = [
            {
                "announcementId": ANN_ID,
                "announcementTitle": TITLE_NOTICE,
                "announcementTime": ANN_TS_MS,
                "adjunctUrl": f"/finalpage/2025-06-24/{ANN_ID}.PDF",
                "secCode": "300446",
            }
        ]

        def fake_fetch(_payload):
            return fake_cat, "executed", ""

        with mock.patch.object(m, "fetch_announcements", side_effect=fake_fetch):
            with mock.patch.object(m.time, "sleep", return_value=None):
                row_c, qcount = m.process_live_category_sample(
                    cat_case, registry_ids, document_types, categories_config
                )
        self.assertEqual(qcount, 2)
        self.assertEqual(row_c["case_result"], "pass")
        self.assertEqual(
            row_c["predicted_document_type"], "shareholder_meeting_material"
        )


if __name__ == "__main__":
    unittest.main()
