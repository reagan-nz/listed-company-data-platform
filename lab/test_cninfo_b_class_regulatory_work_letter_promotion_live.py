"""
B-FM-13：监管工作函 promotion live allow-list 锁测（离线；不请求 CNINFO）。

覆盖：
- allow-list 仅含 inquiry_known_004 + inquiry_sample_003
- 字段与 fixtures ready 对齐
- mock live 路径可对两 case 得到 pass

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_regulatory_work_letter_promotion_live.py
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
    "cninfo_b_class_regulatory_work_letter_promotion_live_20260715",
)
KNOWN_ALLOW = os.path.join(LIVE_DIR, "known_document_retrieval_cases_live_allowlist.yaml")
CATEGORY_ALLOW = os.path.join(
    LIVE_DIR, "category_sample_cases_live_allowlist.yaml"
)
FIXTURE_KNOWN = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)
FIXTURE_CATEGORY = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "category_sample_cases.yaml"
)

# harvest 证据标题（只读引用；BD2E433；本测不请求 CNINFO）
TITLE_WORK_LETTER = (
    "中兴财光华会计师事务所（特殊普通合伙）关于对文投控股股份有限公司"
    "2024年年度报告的信息披露监管工作函的专项说明"
)
PATTERN = "监管工作函"
ANN_ID = "1223358761"
# 2025-04-28 00:00:00 UTC
ANN_TS_MS = 1745798400000


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestRegulatoryWorkLetterPromotionLiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_two_cases(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_ALLOW)
        self.assertEqual([c["case_id"] for c in known], ["inquiry_known_004"])
        self.assertEqual([c["case_id"] for c in category], ["inquiry_sample_003"])
        self.assertEqual(known[0]["case_status"], "ready")
        self.assertEqual(category[0]["case_status"], "ready")

    def test_allowlist_fields_match_fixtures(self) -> None:
        ak = _by_id(_load_cases(KNOWN_ALLOW), "inquiry_known_004")
        fk = _by_id(_load_cases(FIXTURE_KNOWN), "inquiry_known_004")
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
        self.assertEqual(ak["title_pattern"], TITLE_WORK_LETTER)
        self.assertEqual(ak["expected_document_type"], "inquiry_reply")

        ac = _by_id(_load_cases(CATEGORY_ALLOW), "inquiry_sample_003")
        fc = _by_id(_load_cases(FIXTURE_CATEGORY), "inquiry_sample_003")
        for key in (
            "title_pattern",
            "date_start",
            "date_end",
            "source_id",
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

    def test_mock_live_known_and_category_pass(self) -> None:
        registry = os.path.join(
            _BASE, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        categories = os.path.join(_BASE, "config", "cninfo_announcement_categories.yaml")
        categories_config = m._load_yaml(categories)
        registry_ids = m._load_registry_source_ids(registry)
        document_types = m._load_document_types(schema)

        known_case = _by_id(_load_cases(KNOWN_ALLOW), "inquiry_known_004")
        fake_known = [
            {
                "announcementId": ANN_ID,
                "announcementTitle": TITLE_WORK_LETTER,
                "announcementTime": ANN_TS_MS,
                "adjunctUrl": f"/finalpage/2025-04-28/{ANN_ID}.PDF",
                "secCode": "600715",
            }
        ]
        with mock.patch.object(m, "resolve_orgid_via_topsearch", return_value="org-mock"):
            with mock.patch.object(
                m, "fetch_announcements", return_value=(fake_known, "executed", "")
            ):
                with mock.patch.object(m.time, "sleep", return_value=None):
                    row_k, _ = m.process_live_known_case(
                        known_case, registry_ids, document_types, categories_config
                    )
        self.assertEqual(row_k["case_result"], "pass")
        self.assertEqual(row_k["predicted_document_type"], "inquiry_reply")

        cat_case = _by_id(_load_cases(CATEGORY_ALLOW), "inquiry_sample_003")
        fake_cat = [
            {
                "announcementId": ANN_ID,
                "announcementTitle": TITLE_WORK_LETTER,
                "announcementTime": ANN_TS_MS,
                "adjunctUrl": f"/finalpage/2025-04-28/{ANN_ID}.PDF",
                "secCode": "600715",
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
        self.assertEqual(row_c["predicted_document_type"], "inquiry_reply")


if __name__ == "__main__":
    unittest.main()
