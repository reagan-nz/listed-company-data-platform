"""
A-class Phase 1 ready-case benchmark 测试（无 CNINFO · 无网络）。

运行：
    python lab/test_cninfo_a_class_phase1_ready_case_benchmark.py
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_phase1_ready_case_benchmark as benchmark  # noqa: E402

BASE_DIR = benchmark.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase1_ready_case_benchmark.py")
READY_CASES_DIR = benchmark.READY_CASES_DIR
BENCHMARK_CSV = benchmark.BENCHMARK_CSV
FIELD_CATALOG = benchmark.FIELD_CATALOG


def _run_runner() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestReadyCaseBenchmark(unittest.TestCase):
    def test_runner_no_network(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run_runner()
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()

    def test_all_fixtures_exist(self) -> None:
        for case in benchmark.CASE_REGISTRY:
            path = os.path.join(READY_CASES_DIR, case["fixture"])
            self.assertTrue(os.path.isfile(path), msg=path)

    def test_benchmark_csv_schema(self) -> None:
        _run_runner()
        with open(BENCHMARK_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        expected_cols = {
            "case_id",
            "object_type",
            "expected_status",
            "actual_status",
            "quality_status",
            "lineage_status",
            "passed",
            "notes",
        }
        self.assertEqual(set(rows[0].keys()), expected_cols)

    def test_all_cases_pass(self) -> None:
        _run_runner()
        with open(BENCHMARK_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            self.assertEqual(row["passed"], "yes", msg=row["case_id"])

    def test_enum_validity_ac001(self) -> None:
        path = os.path.join(READY_CASES_DIR, "AC001_valid_periodic_report_case.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        doc = data["report_document"]
        self.assertIn(doc["report_type"], benchmark.VALID_REPORT_TYPES)
        self.assertIn(doc["lineage_status"], benchmark.VALID_LINEAGE_STATUS)
        self.assertIn(doc["quality_status"], benchmark.VALID_QUALITY_STATUS)

    def test_lineage_policy_ac003(self) -> None:
        path = os.path.join(READY_CASES_DIR, "AC003_missing_pdf_url_case.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        lineage = data["document_lineage"]
        self.assertEqual(lineage["storage_status"], "not_attempted")
        self.assertIsNone(lineage.get("pdf_url"))
        self.assertEqual(data["report_document"]["lineage_status"], "needs_review")

    def test_quality_policy_no_verified(self) -> None:
        for name in (
            "AC003_missing_pdf_url_case.json",
            "AC005_unknown_report_type_case.json",
        ):
            with open(os.path.join(READY_CASES_DIR, name), encoding="utf-8") as f:
                data = json.load(f)
            doc = data.get("report_document") or {}
            self.assertNotEqual(doc.get("quality_status"), "verified")

    def test_unknown_report_type_ac005(self) -> None:
        path = os.path.join(READY_CASES_DIR, "AC005_unknown_report_type_case.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        report_type = data["report_document"]["report_type"]
        self.assertNotIn(report_type, benchmark.VALID_REPORT_TYPES)

    def test_field_catalog_required_count(self) -> None:
        required = 0
        with open(FIELD_CATALOG, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("level") == "required":
                    required += 1
        self.assertEqual(required, 22)

    def test_gate_ready_for_review(self) -> None:
        self.assertEqual(benchmark.BENCHMARK_GATE, "READY_FOR_REVIEW")
        result = _run_runner()
        self.assertIn("READY_FOR_REVIEW", result.stdout)

    def test_fixture_meta_offline(self) -> None:
        for case in benchmark.CASE_REGISTRY:
            path = os.path.join(READY_CASES_DIR, case["fixture"])
            with open(path, encoding="utf-8") as f:
                meta = json.load(f).get("_fixture_meta") or {}
            self.assertFalse(meta.get("cninfo_called"))
            self.assertFalse(meta.get("pdf_downloaded"))


if __name__ == "__main__":
    unittest.main()
