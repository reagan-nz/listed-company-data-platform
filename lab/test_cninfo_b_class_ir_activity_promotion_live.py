"""
B-FM-10：IR activity promotion live allow-list 锁测（离线；不请求 CNINFO）。

覆盖：
- allow-list 仅含 ir_activity_known_002/003 + ir_activity_sample_001/002
- 字段与 fixtures ready 对齐
- mock live 路径可对四 case 得到 pass

无真实 CNINFO · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_ir_activity_promotion_live.py
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
    "cninfo_b_class_ir_activity_promotion_live_20260715",
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

KNOWN_IDS = ["ir_activity_known_002", "ir_activity_known_003"]
CATEGORY_IDS = ["ir_activity_sample_001", "ir_activity_sample_002"]

# 集体接待日 / 开放日 锚点标题（与 harvest 证据一致）
TITLE_COLLECTIVE = "关于参加2025年吉林辖区上市公司投资者网上集体接待日活动的公告"
TITLE_OPEN_DAY = "关于举办投资者开放日活动的公告"
PATTERN_COLLECTIVE = "投资者网上集体接待日"
PATTERN_OPEN_DAY = "投资者开放日"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestIrActivityPromotionLiveAllowList(unittest.TestCase):
    def test_allowlist_scope_exactly_four_cases(self) -> None:
        known = _load_cases(KNOWN_ALLOW)
        category = _load_cases(CATEGORY_ALLOW)
        self.assertEqual([c["case_id"] for c in known], KNOWN_IDS)
        self.assertEqual([c["case_id"] for c in category], CATEGORY_IDS)
        for c in known + category:
            self.assertEqual(c["case_status"], "ready")

    def test_allowlist_fields_match_fixtures(self) -> None:
        for case_id in KNOWN_IDS:
            ak = _by_id(_load_cases(KNOWN_ALLOW), case_id)
            fk = _by_id(_load_cases(FIXTURE_KNOWN), case_id)
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
            self.assertEqual(ak["expected_document_type"], "investor_relations_activity")

        for case_id in CATEGORY_IDS:
            ac = _by_id(_load_cases(CATEGORY_ALLOW), case_id)
            fc = _by_id(_load_cases(FIXTURE_CATEGORY), case_id)
            for key in (
                "title_pattern",
                "date_start",
                "date_end",
                "source_id",
                "expected_min_results",
            ):
                self.assertEqual(ac[key], fc[key], f"{case_id}.{key}")
            self.assertEqual(
                sorted(ac["expected_document_types"]),
                sorted(fc["expected_document_types"]),
            )

        self.assertEqual(
            _by_id(_load_cases(KNOWN_ALLOW), "ir_activity_known_002")["title_pattern"],
            PATTERN_COLLECTIVE,
        )
        self.assertEqual(
            _by_id(_load_cases(KNOWN_ALLOW), "ir_activity_known_003")["title_pattern"],
            PATTERN_OPEN_DAY,
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

        # CNINFO announcementTime 为毫秒时间戳（UTC 解释）
        # 2025-05-20 / 2025-06-03
        ts_collective = 1747699200000
        ts_open = 1748908800000

        known_specs = [
            (
                "ir_activity_known_002",
                TITLE_COLLECTIVE,
                ts_collective,
                "1223605360",
                "000420",
            ),
            (
                "ir_activity_known_003",
                TITLE_OPEN_DAY,
                ts_open,
                "1223746795",
                "000949",
            ),
        ]
        for case_id, title, ts, ann_id, code in known_specs:
            known_case = _by_id(_load_cases(KNOWN_ALLOW), case_id)
            fake_known = [
                {
                    "announcementId": ann_id,
                    "announcementTitle": title,
                    "announcementTime": ts,
                    "adjunctUrl": f"/finalpage/{title[:10]}/{ann_id}.PDF",
                    "secCode": code,
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
            self.assertEqual(row_k["case_result"], "pass", case_id)
            self.assertEqual(
                row_k["predicted_document_type"],
                "investor_relations_activity",
                case_id,
            )

        cat_specs = [
            ("ir_activity_sample_001", TITLE_COLLECTIVE, ts_collective, "1223605360"),
            ("ir_activity_sample_002", TITLE_OPEN_DAY, ts_open, "1223746795"),
        ]
        for case_id, title, ts, ann_id in cat_specs:
            cat_case = _by_id(_load_cases(CATEGORY_ALLOW), case_id)
            fake_cat = [
                {
                    "announcementId": ann_id,
                    "announcementTitle": title,
                    "announcementTime": ts,
                    "adjunctUrl": f"/finalpage/x/{ann_id}.PDF",
                    "secCode": "000420",
                }
            ]

            def fake_fetch(_payload, _fake=fake_cat):
                return _fake, "executed", ""

            with mock.patch.object(m, "fetch_announcements", side_effect=fake_fetch):
                with mock.patch.object(m.time, "sleep", return_value=None):
                    row_c, qcount = m.process_live_category_sample(
                        cat_case, registry_ids, document_types, categories_config
                    )
            self.assertEqual(qcount, 2, case_id)
            self.assertEqual(row_c["case_result"], "pass", case_id)
            self.assertEqual(
                row_c["predicted_document_type"],
                "investor_relations_activity",
                case_id,
            )


if __name__ == "__main__":
    unittest.main()
