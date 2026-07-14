"""
C-class Era D fuller-market slice1 YAML builder 回归测试（无 CNINFO）。

运行：
    python3 lab/test_cninfo_c_class_fuller_market_slice_yaml_builder.py
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

from build_cninfo_c_class_fuller_market_slice_yaml import (  # noqa: E402
    SLICE1_EXPECTED_COUNT,
    OverlapReport,
    _expected_case_id,
    _is_st_or_delist,
    _load_draft_rows,
    build_slice_yaml,
    validate_slice_companies,
)


class TestFullerMarketSliceYamlBuilder(unittest.TestCase):
    def test_expected_case_id_sequence(self) -> None:
        self.assertEqual(_expected_case_id(1), "CE1E001")
        self.assertEqual(_expected_case_id(200), "CE1E200")

    def test_st_or_delist_detection(self) -> None:
        self.assertTrue(_is_st_or_delist("*ST东珠"))
        self.assertTrue(_is_st_or_delist("国华退"))
        self.assertFalse(_is_st_or_delist("平安银行"))

    def test_overlap_guard_rejects_863_hit(self) -> None:
        draft = [{"case_id": "CE1E001", "company_code": "000009", "cohort": "x", "prior_in_863": "no", "include_reason": ""}]
        parent = {
            "000009": {
                "stock_code": "000009",
                "short_name": "中国宝安",
                "board": "szse_main",
                "exchange": "SZSE",
                "orgid": "gssz0000009",
                "financial": False,
            }
        }
        _, report = validate_slice_companies(draft, parent, {"000009"}, set(), set(), set())
        self.assertIn("000009", report.overlap_863)
        self.assertFalse(report.pass_offline)

    def test_build_from_project_draft(self) -> None:
        """使用仓库内真实 draft CSV 构建（离线）。"""
        base = os.path.normpath(os.path.join(_LAB_DIR, ".."))
        draft = os.path.join(
            base,
            "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_universe_draft.csv",
        )
        if not os.path.isfile(draft):
            self.skipTest("draft CSV 不存在")

        with tempfile.TemporaryDirectory() as tmp:
            out_yaml = os.path.join(tmp, "slice1.yaml")
            md = os.path.join(tmp, "overlap.md")
            csv_out = os.path.join(tmp, "overlap.csv")
            count, report = build_slice_yaml(
                draft,
                os.path.join(base, "lab/eval_companies_full_market_2024.yaml"),
                os.path.join(base, "lab/eval_companies_c_class_harvest_863_non_bse.yaml"),
                os.path.join(base, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml"),
                out_yaml,
                md,
                csv_out,
            )
            self.assertEqual(count, SLICE1_EXPECTED_COUNT)
            self.assertTrue(report.pass_offline)
            with open(out_yaml, encoding="utf-8") as fh:
                doc = yaml.safe_load(fh)
            self.assertEqual(doc["company_count"], SLICE1_EXPECTED_COUNT)
            self.assertEqual(len(doc["companies"]), SLICE1_EXPECTED_COUNT)
            self.assertEqual(doc["companies"][0]["case_id"], "CE1E001")
            self.assertEqual(doc["companies"][-1]["case_id"], "CE1E200")

    def test_draft_csv_has_200_rows(self) -> None:
        base = os.path.normpath(os.path.join(_LAB_DIR, ".."))
        draft = os.path.join(
            base,
            "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_universe_draft.csv",
        )
        if not os.path.isfile(draft):
            self.skipTest("draft CSV 不存在")
        rows = _load_draft_rows(draft)
        self.assertEqual(len(rows), SLICE1_EXPECTED_COUNT)
        self.assertEqual(rows[0]["case_id"], "CE1E001")
        self.assertEqual(rows[-1]["case_id"], "CE1E200")


if __name__ == "__main__":
    unittest.main()
