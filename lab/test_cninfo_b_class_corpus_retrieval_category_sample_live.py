#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B-FM-01：category-sample live 路径离线锁测（不请求 CNINFO）。"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest import mock

LAB_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(LAB_DIR)
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

import validate_cninfo_b_class_corpus_retrieval as m  # noqa: E402


class CategorySampleLivePathTests(unittest.TestCase):
    def test_positive_category_sample_flag(self) -> None:
        self.assertTrue(
            m._is_live_positive_category_sample(
                {"case_id": "general_sample_001", "case_status": "ready"}
            )
        )
        self.assertFalse(
            m._is_live_positive_category_sample(
                {"case_id": "periodic_guard_002", "case_status": "ready"}
            )
        )
        self.assertFalse(
            m._is_live_positive_category_sample(
                {"case_id": "general_sample_001", "case_status": "placeholder"}
            )
        )

    def test_dry_run_marks_category_sample_live_ready(self) -> None:
        known = os.path.join(
            BASE_DIR, "fixtures", "b_class", "retrieval_validation",
            "known_document_retrieval_cases.yaml",
        )
        category = os.path.join(
            BASE_DIR, "fixtures", "b_class", "retrieval_validation",
            "category_sample_cases.yaml",
        )
        registry = os.path.join(
            BASE_DIR, "config", "cninfo_b_class_source_registry_draft.yaml"
        )
        schema = os.path.join(
            BASE_DIR, "schemas", "b_class", "b_document.schema.json"
        )
        rows, stats = m.run_dry_run(known, category, registry, schema, dry_run=True)
        self.assertEqual(stats["invalid_ready"], 0)
        by_id = {r["case_id"]: r for r in rows}
        sample = by_id["general_sample_001"]
        self.assertEqual(sample["case_status"], "ready")
        self.assertEqual(
            sample["dry_run_status"], "ready_for_category_sample_live_validation"
        )
        self.assertEqual(sample["would_query"], "true")

    def test_process_live_category_sample_pass_with_mock(self) -> None:
        case = {
            "case_id": "general_sample_001",
            "case_status": "ready",
            "source_id": "cninfo_general_announcement_pdf",
            "source_category": "announcement_pdf",
            "title_pattern": "董事会决议公告",
            "date_start": "2025-06-26",
            "date_end": "2025-06-29",
            "expected_min_results": 1,
            "expected_document_types": ["board_resolution", "announcement"],
        }
        registry_ids = {"cninfo_general_announcement_pdf"}
        document_types = {"board_resolution", "announcement"}
        categories_config = m._load_yaml(
            os.path.join(BASE_DIR, "config", "cninfo_announcement_categories.yaml")
        )
        fake_records = [
            {
                "announcementId": "1",
                "announcementTitle": "九届二十九次董事会决议公告",
                "announcementTime": "2025-06-27 00:00:00",
                "adjunctUrl": "/finalpage/2025-06-27/1224014247.PDF",
                "secCode": "000683",
            }
        ]

        def fake_fetch(payload):
            return fake_records, "executed", ""

        with mock.patch.object(m, "fetch_announcements", side_effect=fake_fetch):
            with mock.patch.object(m.time, "sleep", return_value=None):
                row, qcount = m.process_live_category_sample(
                    case, registry_ids, document_types, categories_config
                )
        self.assertEqual(qcount, 2)  # sse + szse
        self.assertEqual(row["case_result"], "pass")
        self.assertEqual(row["predicted_document_type"], "board_resolution")
        self.assertIn("董事会决议公告", row["matched_title"])

    def test_live_result_uses_case_pass_not_query_count(self) -> None:
        """多 query/case 时 pass==ready 即 LIVE_PASS（不得要求 pass==query_executed）。"""
        result = m._compute_live_result(
            {
                "invalid_ready": 0,
                "ready_cases": 4,
                "query_executed": 8,
                "pass": 4,
                "fail": 0,
                "ambiguous": 0,
                "request_error": 0,
            }
        )
        self.assertEqual(result, "LIVE_PASS")


if __name__ == "__main__":
    unittest.main()
