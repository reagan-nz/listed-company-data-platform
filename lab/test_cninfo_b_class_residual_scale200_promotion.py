"""
B-FM-04（R19）：~200 known-doc residual scale 晋升锁测（离线）。

覆盖：
- allow-list 200 案均为 ready
- title_pattern 命中 harvest 且全局互斥
- harvest 标题路由符合 expected_document_type
- 拒绝 audit_report_known_002；不回退既有 LIVE_PASS

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_residual_scale200_promotion.py
"""

from __future__ import annotations

import os
import sys
import unittest

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_b_class_category_routing as routing  # noqa: E402
import validate_cninfo_b_class_corpus_retrieval as retrieval  # noqa: E402

KNOWN_YAML = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)
MANIFEST = os.path.join(_BASE, "outputs", "validation", "_bfm04_manifest.json")

import json

with open(MANIFEST, encoding="utf-8") as f:
    _MANIFEST = json.load(f)

ALLOW_IDS = list(_MANIFEST["allow_ids"])
HARVESTS = {}
for _src in ("yaml_harvests", "harvests"):
    for _cid, _meta in _MANIFEST.get(_src, {}).items():
        HARVESTS[_cid] = _meta["title"]


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestResidualScale200Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_allowlist_size_two_hundred(self) -> None:
        self.assertEqual(len(ALLOW_IDS), 200)
        self.assertEqual(len(set(ALLOW_IDS)), 200)

    def test_new_cases_ready_fields(self) -> None:
        for case_id in ALLOW_IDS:
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                self.assertEqual(c["case_status"], "ready")
                self.assertTrue(c["title_pattern"])
                self.assertTrue(c["company_code"])
                self.assertTrue(c["date_start"] and c["date_end"])
                self.assertTrue(c["expected_pdf_url_available"])
                self.assertIn("B-FM-04", c["notes"])
                self.assertTrue(any("\u4e00" <= ch <= "\u9fff" for ch in c["notes"]))
                harvest = HARVESTS[case_id]
                self.assertTrue(retrieval._title_matches(harvest, c["title_pattern"]))

    def test_patterns_unique_among_ready(self) -> None:
        pats = [c["title_pattern"] for c in self.known if c.get("case_status") == "ready"]
        self.assertEqual(len(pats), len(set(pats)))

    def test_harvest_titles_route_correctly(self) -> None:
        for case_id in ALLOW_IDS:
            with self.subTest(case_id=case_id):
                c = _by_id(self.known, case_id)
                r = routing.route_title(HARVESTS[case_id], self.config)
                self.assertEqual(r.predicted_document_type, c["expected_document_type"])
                self.assertEqual(r.predicted_route_to, c["expected_route_to"])
                self.assertNotEqual(r.predicted_document_type, "other")
                self.assertNotEqual(r.predicted_document_type, "annual_report")

    def test_reject_audit_report_known_002(self) -> None:
        ids = {c["case_id"] for c in self.known}
        self.assertNotIn("audit_report_known_002", ids)
        r = routing.route_title("天健审〔2025〕11-195号 川网传媒2024年报审计报告", self.config)
        self.assertEqual(r.predicted_document_type, "annual_report")

    def test_deferred_known_002_not_promoted(self) -> None:
        ids = {c["case_id"] for c in self.known}
        for case_id in (
            "independent_director_meeting_review_known_002",
            "asset_valuation_explanation_known_002",
            "listing_sponsor_known_002",
            "continuous_supervision_training_known_002",
            "equity_change_report_known_002",
        ):
            self.assertNotIn(case_id, ids)

    def test_closed_live_pass_still_ready(self) -> None:
        for case_id in (
            "tracking_rating_report_known_001",
            "tracking_rating_report_known_010",
            "bond_trustee_report_known_001",
            "bond_trustee_report_known_007",
            "bond_trustee_report_known_008",
            "legal_opinion_known_019",
            "supervisory_board_known_005",
            "continuous_supervision_annual_known_005",
        ):
            with self.subTest(case_id=case_id):
                self.assertEqual(_by_id(self.known, case_id)["case_status"], "ready")

    def test_dry_run_field_validation(self) -> None:
        registry = os.path.join(_BASE, "config", "cninfo_b_class_source_registry_draft.yaml")
        schema = os.path.join(_BASE, "schemas", "b_class", "b_document.schema.json")
        registry_ids = retrieval._load_registry_source_ids(registry)
        document_types = retrieval._load_document_types(schema)
        for case_id in ALLOW_IDS:
            with self.subTest(case_id=case_id):
                case = _by_id(self.known, case_id)
                row = retrieval._process_case(
                    case, "known_document", registry_ids, document_types, dry_run=True
                )
                self.assertEqual(row["dry_run_status"], "ready_for_future_live_validation")
                self.assertEqual(row["would_query"], "true")


if __name__ == "__main__":
    unittest.main()
