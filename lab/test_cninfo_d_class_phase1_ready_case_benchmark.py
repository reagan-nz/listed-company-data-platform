"""
D-class Phase 1 ready-case benchmark 测试（无 CNINFO · 无网络）。

运行：
    python lab/test_cninfo_d_class_phase1_ready_case_benchmark.py
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

import run_cninfo_d_class_phase1_ready_case_benchmark as benchmark  # noqa: E402

BASE_DIR = benchmark.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_phase1_ready_case_benchmark.py")
FIXTURES_DIR = benchmark.FIXTURES_DIR
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
    def test_all_seven_ready_cases_detected(self) -> None:
        self.assertEqual(len(benchmark.CASE_REGISTRY), 7)
        case_ids = {c["case_id"] for c in benchmark.CASE_REGISTRY}
        self.assertEqual(
            case_ids,
            {"DC001", "DC002", "DC003", "DC004", "DC005", "DC006", "DC007"},
        )
        for case in benchmark.CASE_REGISTRY:
            path = os.path.join(FIXTURES_DIR, case["fixture"])
            self.assertTrue(os.path.isfile(path), msg=path)

    def test_required_fields_validated(self) -> None:
        result = _run_runner()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with open(BENCHMARK_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        captured = [r for r in rows if r["scenario"] == "captured_normal"]
        self.assertTrue(captured)
        for row in captured:
            self.assertEqual(row["passed"], "yes", msg=row["case_id"])
            self.assertEqual(row["actual_status"], "captured_pass", msg=row["case_id"])

    def test_empty_but_valid_accepted(self) -> None:
        result = _run_runner()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with open(BENCHMARK_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        empty_rows = [r for r in rows if r["scenario"] == "empty_but_valid"]
        self.assertEqual(len(empty_rows), 2)
        for row in empty_rows:
            self.assertEqual(row["passed"], "yes", msg=row["case_id"])
            self.assertEqual(row["retrieval_status"], "empty_but_valid", msg=row["case_id"])
            self.assertEqual(row["actual_status"], "empty_but_valid_pass", msg=row["case_id"])

    def test_needs_review_accepted(self) -> None:
        result = _run_runner()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with open(BENCHMARK_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        dc007 = next(r for r in rows if r["case_id"] == "DC007")
        self.assertEqual(dc007["passed"], "yes")
        self.assertEqual(dc007["quality_status"], "needs_review")
        self.assertEqual(dc007["lineage_status"], "needs_review")
        self.assertEqual(dc007["actual_status"], "needs_review_accepted")

    def test_removed_fields_absent(self) -> None:
        for case in benchmark.CASE_REGISTRY:
            path = os.path.join(FIXTURES_DIR, case["fixture"])
            with open(path, encoding="utf-8") as f:
                blob = f.read()
            for field in benchmark.REMOVED_FIELDS:
                self.assertNotIn(f'"{field}"', blob, msg=f"{case['case_id']}:{field}")

    def test_no_verified_status(self) -> None:
        for case in benchmark.CASE_REGISTRY:
            path = os.path.join(FIXTURES_DIR, case["fixture"])
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            env = data.get("market_event") or {}
            payload = data.get(case["component"]) or {}
            self.assertNotEqual(env.get("quality_status"), "verified")
            self.assertNotEqual(payload.get("quality_status"), "verified")
            self.assertNotIn("verified", json.dumps(data).lower().replace("needs_review", ""))

    def test_no_testing_stable_sample_upgrade(self) -> None:
        registry_path = os.path.join(BASE_DIR, "config", "cninfo_d_class_source_registry_draft.yaml")
        with open(registry_path, encoding="utf-8") as f:
            registry_text = f.read()
        self.assertNotIn("testing_stable_sample: true", registry_text)
        for case in benchmark.CASE_REGISTRY:
            path = os.path.join(FIXTURES_DIR, case["fixture"])
            with open(path, encoding="utf-8") as f:
                meta = json.load(f).get("_fixture_meta") or {}
            self.assertFalse(meta.get("testing_stable_sample_upgraded"))
            self.assertFalse(meta.get("cninfo_called"))

    def test_no_cninfo_network_call(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            with mock.patch("urllib.request.urlopen") as urlopen_mock:
                result = _run_runner()
                self.assertEqual(result.returncode, 0, msg=result.stderr)
                get_mock.assert_not_called()
                post_mock.assert_not_called()
                urlopen_mock.assert_not_called()
        self.assertIn("READY_FOR_REVIEW", result.stdout)


if __name__ == "__main__":
    unittest.main()
