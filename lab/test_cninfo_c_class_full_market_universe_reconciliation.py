"""
CNINFO C-class 全市场 universe 离线对账测试。

运行：
    python lab/test_cninfo_c_class_full_market_universe_reconciliation.py
"""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import unittest

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from reconcile_cninfo_c_class_full_market_universe import (  # noqa: E402
    BASE_DIR,
    LEDGER_CSV,
    classify_company,
    load_candidate_map,
    load_universe_codes,
    reconcile_universe,
    build_conflict_code_set,
    build_ledger_index,
    build_name_index,
    build_org_index,
    _load_csv,
    _load_yaml_companies,
)

ERA_C_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
HOLD_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml")
BSE_LEGACY_YAML = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_legacy_hold.yaml"
)
BSE_920_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_920_active.yaml")
CONFLICT_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_conflict_triage.csv"
)

SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_full_market_universe_reconciliation_test_summary.md",
)


def _write_mini_era_b(path: str, companies: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"companies": companies}, f, allow_unicode=True)


def _write_mini_era_c(path: str, codes: list) -> None:
    companies = [{"stock_code": c, "short_name": f"Co{c}", "orgid": f"org{c}"} for c in codes]
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {"companies": companies, "company_count": len(codes), "universe_id": "test"},
            f,
            allow_unicode=True,
        )


def _write_mini_hold(path: str, codes: list) -> None:
    companies = [
        {
            "stock_code": c,
            "company_name": f"Hold{c}",
            "short_name": f"Hold{c}",
            "orgid": f"org{c}",
            "retry_decision": "hold_no_retry",
        }
        for c in codes
    ]
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump({"companies": companies, "company_count": len(codes)}, f, allow_unicode=True)


class TestFullMarketUniverseReconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.era_c_codes = load_universe_codes(ERA_C_YAML)
        cls.hold_codes = load_universe_codes(HOLD_YAML)
        cls.ledger_index = build_ledger_index(_load_csv(LEDGER_CSV))
        cls.candidate_map = load_candidate_map()
        cls.conflict_codes = build_conflict_code_set(_load_csv(CONFLICT_CSV))
        era_b_rows = _load_yaml_companies(
            os.path.join(BASE_DIR, "lab/eval_companies_full_market_2024.yaml")
        )
        cls.org_index = build_org_index(era_b_rows, cls.candidate_map)
        cls.name_index = build_name_index(era_b_rows)
        cls.bse_920_codes = load_universe_codes(BSE_920_YAML)
        cls.bse_legacy_codes = load_universe_codes(BSE_LEGACY_YAML)

    def _classify(self, code: str, name: str = "", org_id: str = "") -> dict:
        cand = self.candidate_map.get(code, {})
        return classify_company(
            code=code,
            name=name or cand.get("company_name", f"Test{code}"),
            org_id=org_id or cand.get("org_id", ""),
            era_c_codes=self.era_c_codes,
            hold_codes=self.hold_codes,
            bse_920_codes=self.bse_920_codes,
            bse_legacy_codes=self.bse_legacy_codes,
            ledger_index=self.ledger_index,
            candidate_map=self.candidate_map,
            org_index=self.org_index,
            name_index=self.name_index,
            conflict_codes=self.conflict_codes,
        )

    def test_case1_863_active_matched(self) -> None:
        """case 1: 863 active matched"""
        row = self._classify("000009")
        self.assertEqual(row["classification"], "already_in_c_class")
        self.assertEqual(row["matched_universe"], "era_c")
        self.assertEqual(row["identity_confidence"], "high")

    def test_case2_hold_company_classified(self) -> None:
        """case 2: hold company classified correctly"""
        row = self._classify("000043")
        self.assertEqual(row["classification"], "matched_hold")
        self.assertEqual(row["matched_universe"], "hold")

    def test_case3_bse_legacy_classified(self) -> None:
        """case 3: BSE legacy classified correctly"""
        row = self._classify("832491")
        self.assertEqual(row["classification"], "matched_bse_legacy_hold")
        self.assertEqual(row["evidence_source"], "legacy_code_mapping")
        self.assertEqual(row["canonical_candidate"], "CNINFO_920491")

    def test_case4_rename_mapping_recognized(self) -> None:
        """case 4: rename mapping recognized"""
        row = self._classify("000022")
        self.assertEqual(row["evidence_source"], "rename_history")
        self.assertEqual(row["canonical_candidate"], "CNINFO_001872")
        self.assertEqual(row["classification"], "identity_conflict")

    def test_case5_same_name_different_code_no_merge(self) -> None:
        """case 5: same-name different-code does not auto merge"""
        row631 = self._classify("600631", name="百联股份")
        row827 = self._classify("600827", name="百联股份")
        self.assertEqual(row631["classification"], "needs_manual_review")
        self.assertEqual(row827["classification"], "needs_manual_review")
        self.assertNotEqual(row631["canonical_candidate"], row827["canonical_candidate"])
        self.assertIn("不自动合并", row631["notes"] + row827["notes"])

    def test_mini_universe_reconcile_row_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            era_b = os.path.join(tmp, "era_b.yaml")
            era_c = os.path.join(tmp, "era_c.yaml")
            hold = os.path.join(tmp, "hold.yaml")
            _write_mini_era_b(
                era_b,
                [
                    {"stock_code": "000009", "short_name": "中国宝安", "orgid": "gssz0000009"},
                    {"stock_code": "000043", "short_name": "中航善达", "orgid": "gssz0000043"},
                ],
            )
            _write_mini_era_c(era_c, ["000009"])
            _write_mini_hold(hold, ["000043"])
            rows, stats = reconcile_universe(
                era_b_yaml=era_b,
                era_c_yaml=era_c,
                hold_yaml=hold,
                bse_920_yaml=BSE_920_YAML,
                bse_legacy_yaml=BSE_LEGACY_YAML,
            )
            self.assertEqual(len(rows), 2)
            self.assertEqual(stats["classification_counts"].get("already_in_c_class"), 1)
            self.assertEqual(stats["classification_counts"].get("matched_hold"), 1)


def _write_test_summary(passed: int, total: int) -> None:
    lines = [
        "# Full Market Universe Reconciliation Test Summary",
        "",
        f"| 结果 | **{passed}/{total} PASS** |",
        "",
    ]
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestFullMarketUniverseReconciliation)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    _write_test_summary(passed, total)
    print(f"\n{passed}/{total} PASS")
    sys.exit(0 if result.wasSuccessful() else 1)
