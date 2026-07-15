"""
B 类 non-periodic document fixtures — announcement_preview / wrong_company FP 同源锁测。

确保 known_document_benchmark 中的 FP lineage 行已同步进 non_periodic fixtures，
且 raw_metadata 保留 expected_false_positive_reason（与 routing benchmark 同源）。
wrong_period 行路由 periodic，不得进入 non_periodic fixture。

离线 only · 无 CNINFO · 无 live。

运行：
    python lab/test_cninfo_b_class_non_periodic_fp_fixture_sync.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from typing import Any, Dict, List

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import seed_cninfo_b_class_non_periodic_document_fixtures as seed  # noqa: E402

BASE_DIR = seed.BASE_DIR
BENCHMARK = seed.DEFAULT_BENCHMARK
FIXTURES = seed.DEFAULT_DOCUMENT_FIXTURES

PREVIEW_IDS = {
    "periodic_false_positive_005",
    "periodic_false_positive_006",
    "periodic_false_positive_007",
    "periodic_false_positive_008",
}
WRONG_COMPANY_IDS = {
    "periodic_false_positive_010",
    "periodic_false_positive_011",
    "periodic_false_positive_012",
    "periodic_false_positive_013",
}
WRONG_PERIOD_IDS = {
    "periodic_false_positive_014",
    "periodic_false_positive_015",
    "periodic_false_positive_016",
    "periodic_false_positive_017",
}


def _load_fixtures(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _fixture_by_benchmark_id(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        br = (row.get("raw_metadata_json") or {}).get("benchmark_row") or {}
        bid = br.get("benchmark_id")
        if bid:
            out[bid] = row
    return out


class TestNonPeriodicFpFixtureSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.benchmark = seed.load_benchmark(BENCHMARK)
        cls.fixtures = _load_fixtures(FIXTURES)
        cls.by_id = _fixture_by_benchmark_id(cls.fixtures)
        cls.bench_by_id = {e["benchmark_id"]: e for e in cls.benchmark}

    def test_preview_rows_seeded_in_fixtures(self) -> None:
        for bid in PREVIEW_IDS:
            self.assertIn(bid, self.by_id, f"{bid} 须在 non_periodic fixtures")
            br = self.by_id[bid]["raw_metadata_json"]["benchmark_row"]
            self.assertEqual(br.get("expected_false_positive_reason"), "announcement_preview")
            self.assertEqual(self.by_id[bid]["source_id"], "cninfo_general_announcement_pdf")
            self.assertEqual(self.by_id[bid]["document_type"], "announcement")

    def test_wrong_company_rows_seeded_in_fixtures(self) -> None:
        for bid in WRONG_COMPANY_IDS:
            self.assertIn(bid, self.by_id, f"{bid} 须在 non_periodic fixtures")
            br = self.by_id[bid]["raw_metadata_json"]["benchmark_row"]
            self.assertEqual(br.get("expected_false_positive_reason"), "wrong_company")
            self.assertEqual(self.by_id[bid]["source_id"], "cninfo_general_announcement_pdf")

    def test_wrong_period_not_in_non_periodic_fixtures(self) -> None:
        """wrong_period 仍 route periodic，seed 须 skipped_periodic。"""
        for bid in WRONG_PERIOD_IDS:
            self.assertNotIn(bid, self.by_id)
            status, _, doc = seed.classify_entry(self.bench_by_id[bid])
            self.assertEqual(status, "skipped_periodic")
            self.assertIsNone(doc)

    def test_seed_preserves_fp_reason_in_build_document(self) -> None:
        preview = self.bench_by_id["periodic_false_positive_005"]
        doc = seed.build_document(preview)
        br = doc["raw_metadata_json"]["benchmark_row"]
        self.assertEqual(br["expected_false_positive_reason"], "announcement_preview")

        cross = self.bench_by_id["periodic_false_positive_010"]
        doc2 = seed.build_document(cross)
        br2 = doc2["raw_metadata_json"]["benchmark_row"]
        self.assertEqual(br2["expected_false_positive_reason"], "wrong_company")

    def test_process_benchmark_seeds_preview_and_wrong_company(self) -> None:
        documents, report_rows = seed.process_benchmark(self.benchmark)
        seeded_ids = {
            (d.get("raw_metadata_json") or {}).get("benchmark_row", {}).get("benchmark_id")
            for d in documents
        }
        for bid in PREVIEW_IDS | WRONG_COMPANY_IDS:
            self.assertIn(bid, seeded_ids)

        status_by_id = {r["benchmark_id"]: r["seed_status"] for r in report_rows}
        for bid in PREVIEW_IDS | WRONG_COMPANY_IDS:
            self.assertEqual(status_by_id[bid], "seeded")
        for bid in WRONG_PERIOD_IDS:
            self.assertEqual(status_by_id[bid], "skipped_periodic")

    def test_fixture_fp_counts(self) -> None:
        preview_n = sum(
            1
            for row in self.fixtures
            if ((row.get("raw_metadata_json") or {}).get("benchmark_row") or {}).get(
                "expected_false_positive_reason"
            )
            == "announcement_preview"
        )
        wrong_company_n = sum(
            1
            for row in self.fixtures
            if ((row.get("raw_metadata_json") or {}).get("benchmark_row") or {}).get(
                "expected_false_positive_reason"
            )
            == "wrong_company"
        )
        self.assertEqual(preview_n, 4)
        self.assertEqual(wrong_company_n, 4)

    def test_reseed_roundtrip_preserves_fp(self) -> None:
        """临时目录重跑 seed，preview/wrong_company FP 字段不得丢失。"""
        with tempfile.TemporaryDirectory() as tmp:
            out_docs = os.path.join(tmp, "docs.jsonl")
            out_raw = os.path.join(tmp, "raw.jsonl")
            out_csv = os.path.join(tmp, "seed.csv")
            entries = seed.load_benchmark(BENCHMARK)
            documents, report_rows = seed.process_benchmark(entries)
            seed.write_jsonl(out_docs, documents)
            seed.write_jsonl(out_raw, [])
            seed.write_seed_csv(out_csv, report_rows)

            reloaded = _fixture_by_benchmark_id(_load_fixtures(out_docs))
            self.assertEqual(
                reloaded["periodic_false_positive_007"]["raw_metadata_json"]["benchmark_row"][
                    "expected_false_positive_reason"
                ],
                "announcement_preview",
            )
            self.assertEqual(
                reloaded["periodic_false_positive_013"]["raw_metadata_json"]["benchmark_row"][
                    "expected_false_positive_reason"
                ],
                "wrong_company",
            )
            self.assertNotIn("periodic_false_positive_014", reloaded)


if __name__ == "__main__":
    unittest.main()
