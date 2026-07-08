"""
CNINFO C-class registry candidate generator 测试（离线 only）。

运行：
    python lab/test_cninfo_c_class_registry_candidate_generator.py
"""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import unittest
from typing import Dict, List

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from derive_cninfo_c_class_company_registry_candidate import (  # noqa: E402
    BASE_DIR,
    CSV_COLUMNS,
    _make_company_id,
    derive_registry_candidates,
    write_candidate_csv,
)

ACTIVE_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
HOLD_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml")
BSE_920_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_920_active.yaml")
BSE_LEGACY_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_legacy_hold.yaml")
FULL_MARKET_YAML = os.path.join(BASE_DIR, "lab/eval_companies_full_market_2024.yaml")
SNAPSHOT_DIR = os.path.join(BASE_DIR, "outputs/snapshot/cninfo_c_class/full")
SNAPSHOT_STATUS_CSV = os.path.join(SNAPSHOT_DIR, "quality/company_snapshot_status.csv")

SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_registry_candidate_generator_test_summary.md",
)


def _write_mini_yaml(path: str, companies: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"companies": companies}, f, allow_unicode=True)


class TestRegistryCandidateGenerator(unittest.TestCase):
    def test_case1_active_company_mapping(self) -> None:
        candidates, stats = derive_registry_candidates(
            active_yaml=ACTIVE_YAML,
            hold_yaml=HOLD_YAML,
            bse_920_yaml=BSE_920_YAML,
            bse_legacy_yaml=BSE_LEGACY_YAML,
            full_market_yaml=FULL_MARKET_YAML,
            snapshot_dir=SNAPSHOT_DIR,
            snapshot_status_csv=SNAPSHOT_STATUS_CSV,
        )
        row = next(r for r in candidates if r["company_code"] == "000009")
        self.assertEqual(row["company_id"], "CNINFO_000009")
        self.assertEqual(row["company_name"], "中国宝安")
        self.assertEqual(row["org_id"], "gssz0000009")
        self.assertEqual(row["source"], "harvest_863_yaml")
        self.assertEqual(row["harvest_support_status"], "completed_863")
        self.assertEqual(row["hold_flag"], "false")
        self.assertEqual(row["confidence"], "high")
        self.assertTrue(row["company_full_name"])
        self.assertEqual(stats["active_universe_count"], 863)

    def test_case2_hold_company_mapping(self) -> None:
        candidates, _ = derive_registry_candidates(
            active_yaml=ACTIVE_YAML,
            hold_yaml=HOLD_YAML,
            bse_920_yaml=BSE_920_YAML,
            bse_legacy_yaml=BSE_LEGACY_YAML,
            full_market_yaml=FULL_MARKET_YAML,
            snapshot_dir=SNAPSHOT_DIR,
            snapshot_status_csv=SNAPSHOT_STATUS_CSV,
        )
        row = next(r for r in candidates if r["company_code"] == "000043")
        self.assertEqual(row["source"], "hold_26_yaml")
        self.assertEqual(row["hold_flag"], "true")
        self.assertEqual(row["harvest_support_status"], "hold")
        self.assertTrue(row["notes"])

    def test_case3_duplicate_org_id_detection(self) -> None:
        candidates, stats = derive_registry_candidates(
            active_yaml=ACTIVE_YAML,
            hold_yaml=HOLD_YAML,
            bse_920_yaml=BSE_920_YAML,
            bse_legacy_yaml=BSE_LEGACY_YAML,
            full_market_yaml=FULL_MARKET_YAML,
            snapshot_dir=SNAPSHOT_DIR,
            snapshot_status_csv=SNAPSHOT_STATUS_CSV,
        )
        row_920 = next(r for r in candidates if r["company_code"] == "920729")
        row_839 = next(r for r in candidates if r["company_code"] == "839729")
        self.assertEqual(row_920["org_id"], "gfbj0839729")
        self.assertEqual(row_839["org_id"], "gfbj0839729")
        self.assertEqual(row_920["org_id_conflict_flag"], "true")
        self.assertEqual(row_839["org_id_conflict_flag"], "true")
        self.assertEqual(row_920["previous_code"], "839729")
        self.assertEqual(row_920["legacy_code"], "839729")
        self.assertGreaterEqual(stats["identity_conflict_count"], 1)

    def test_case4_missing_optional_field_handling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            active = os.path.join(tmp, "active.yaml")
            hold = os.path.join(tmp, "hold.yaml")
            bse920 = os.path.join(tmp, "bse920.yaml")
            bse_legacy = os.path.join(tmp, "bse_legacy.yaml")
            full = os.path.join(tmp, "full.yaml")
            _write_mini_yaml(
                active,
                [
                    {
                        "stock_code": "600000",
                        "short_name": "浦发银行",
                        "exchange": "SSE",
                        "orgid": "gssh0600000",
                        "board": "sse_main",
                    }
                ],
            )
            _write_mini_yaml(hold, [])
            _write_mini_yaml(bse920, [])
            _write_mini_yaml(bse_legacy, [])
            _write_mini_yaml(
                full,
                [
                    {
                        "stock_code": "600000",
                        "short_name": "浦发银行",
                        "exchange": "SSE",
                        "orgid": "gssh0600000",
                        "board": "sse_main",
                    }
                ],
            )
            candidates, _ = derive_registry_candidates(
                active_yaml=active,
                hold_yaml=hold,
                bse_920_yaml=bse920,
                bse_legacy_yaml=bse_legacy,
                full_market_yaml=full,
                snapshot_dir=os.path.join(tmp, "no_snapshots"),
                snapshot_status_csv=os.path.join(tmp, "no_status.csv"),
            )
        self.assertEqual(len(candidates), 1)
        row = candidates[0]
        self.assertEqual(row["company_full_name"], "")
        self.assertEqual(row["english_name"], "")
        self.assertEqual(row["security_type"], "")
        self.assertEqual(row["rename_history"], "[]")
        self.assertEqual(row["suspended_flag"], "false")
        self.assertEqual(row["snapshot_support_status"], "unsupported")

    def test_case5_lineage_source_tracking(self) -> None:
        candidates, stats = derive_registry_candidates(
            active_yaml=ACTIVE_YAML,
            hold_yaml=HOLD_YAML,
            bse_920_yaml=BSE_920_YAML,
            bse_legacy_yaml=BSE_LEGACY_YAML,
            full_market_yaml=FULL_MARKET_YAML,
            snapshot_dir=SNAPSHOT_DIR,
            snapshot_status_csv=SNAPSHOT_STATUS_CSV,
        )
        sources = {r["source"] for r in candidates}
        self.assertIn("harvest_863_yaml", sources)
        self.assertIn("hold_26_yaml", sources)
        self.assertIn("bse_920_yaml", sources)
        self.assertIn("bse_legacy_yaml", sources)
        self.assertIn("full_market_2024", sources)
        self.assertEqual(stats["candidate_count"], len(candidates))
        dist = stats["source_distribution"]
        self.assertEqual(dist.get("harvest_863_yaml", 0), 863)
        self.assertEqual(dist.get("hold_26_yaml", 0), 26)

    def test_make_company_id_format(self) -> None:
        self.assertEqual(_make_company_id("9"), "CNINFO_000009")
        self.assertEqual(_make_company_id("920729"), "CNINFO_920729")


def _write_test_summary(results: List[tuple]) -> None:
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    lines = [
        "# Registry Candidate Generator Test Summary",
        "",
        f"**结果：** {passed}/{total} PASS",
        "",
        "| # | case | result |",
        "|---|------|--------|",
    ]
    for idx, (name, ok) in enumerate(results, 1):
        lines.append(f"| {idx} | {name} | {'PASS' if ok else 'FAIL'} |")
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRegistryCandidateGenerator)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    case_names = [
        "active company mapping",
        "hold company mapping",
        "duplicate org_id detection",
        "missing optional field handling",
        "lineage source tracking",
    ]
    results = []
    test_methods = [
        "test_case1_active_company_mapping",
        "test_case2_hold_company_mapping",
        "test_case3_duplicate_org_id_detection",
        "test_case4_missing_optional_field_handling",
        "test_case5_lineage_source_tracking",
    ]
    failed_methods = {case.id().split(".")[-1] for case, _ in result.failures + result.errors}
    for i, method in enumerate(test_methods):
        name = case_names[i] if i < len(case_names) else method
        results.append((name, method not in failed_methods))
    _write_test_summary(results)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
