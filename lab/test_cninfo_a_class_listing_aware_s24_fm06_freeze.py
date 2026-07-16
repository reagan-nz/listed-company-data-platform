"""
A-FM-06：S24 residual-exhausted 冻结断言（纯离线 · CNINFO = 0）。

运行：
    python lab/test_cninfo_a_class_listing_aware_s24_fm06_freeze.py
"""

from __future__ import annotations

import csv
import json
import os
import unittest

import cninfo_a_class_listing_aware_cohort_builder as builder
import cninfo_a_class_listing_period_gate as listing_period_gate
import cninfo_a_class_profile_coverage as pc

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_LAB_DIR)
_VAL = os.path.join(_BASE_DIR, "outputs", "validation")

PROBE_JSON = os.path.join(
    _VAL, "cninfo_a_class_listing_aware_s24_fm06_overlay_residual_probe_20260716.json"
)
SIZE_CLAIM = "residual_371_not_1000"


def _count_post_s24_selectable() -> int:
    """统计 Exclude 含 S24 后、case 窗 AD2E2222+ 的可选残差（不写盘）。"""
    exclude = builder.DEFAULT_A_EXCLUDE_S24_UNIVERSE_CSVS + (
        builder.DEFAULT_S24_OUTPUT_UNIVERSE_CSV,
    )
    a_exclude = builder.load_a_exclude_codes(exclude)
    names = builder.load_full_market_name_map(builder.DEFAULT_FULL_MARKET_YAML)
    profile_dir = builder.DEFAULT_S24_PROFILE_DIR
    selected = 0
    for code in builder.list_profile_codes(profile_dir):
        name = names.get(code, "")
        if code in a_exclude:
            continue
        if not name or builder.is_st_name(name) or builder.is_bse_code(code):
            continue
        case_num = 2222 + selected
        _, expected_period, *_ = builder.derive_report_fields_for_case_num(case_num)
        gate = listing_period_gate.assess_listing_vs_expected_period(
            code, expected_period, profile_dir=profile_dir
        )
        if listing_period_gate.is_listing_period_reject(gate):
            continue
        selected += 1
    return selected


class TestListingAwareS24Fm06Freeze(unittest.TestCase):
    """冻结：union 停滞、微残差、size_claim、禁止伪 1000。"""

    def test_overlay_union_still_2213(self) -> None:
        path_map = pc.discover_profile_path_map()
        self.assertEqual(len(path_map), 2213)
        overlay = pc.DEFAULT_OVERLAY_DIR
        self.assertTrue(os.path.isdir(overlay))
        n = sum(1 for n in os.listdir(overlay) if n.endswith(".json"))
        self.assertEqual(n, 2213)

    def test_post_s24_residual_is_micro_not_1000(self) -> None:
        residual = _count_post_s24_selectable()
        # 诚实：scale 已耗尽；允许 0–2 的 period-window 微残差；绝非 ~1000
        self.assertLessEqual(residual, 2)
        self.assertGreaterEqual(residual, 0)
        self.assertNotEqual(residual, 1000)

    def test_size_claim_frozen_in_probe_json(self) -> None:
        self.assertTrue(os.path.isfile(PROBE_JSON), "fm06 probe json missing")
        with open(PROBE_JSON, "r", encoding="utf-8") as f:
            probe = json.load(f)
        self.assertEqual(probe.get("cninfo_calls"), 0)
        self.assertEqual(probe.get("live_executed"), False)
        self.assertEqual(probe.get("size_claim"), SIZE_CLAIM)
        self.assertEqual(probe.get("overlay_union"), 2213)
        self.assertEqual(probe.get("residual_listing_aware_scale"), "EXHAUSTED")
        self.assertLessEqual(int(probe.get("selectable_residual_post_s24", 9999)), 2)

    def test_s24_universe_still_371(self) -> None:
        path = builder.DEFAULT_S24_OUTPUT_UNIVERSE_CSV
        self.assertTrue(os.path.isfile(path))
        with open(path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 371)
        self.assertEqual(rows[0]["case_id"], "AD2E1851")
        self.assertEqual(rows[-1]["case_id"], "AD2E2221")

    def test_target_1000_still_undersized(self) -> None:
        exclude = builder.DEFAULT_A_EXCLUDE_S24_UNIVERSE_CSVS + (
            builder.DEFAULT_S24_OUTPUT_UNIVERSE_CSV,
        )
        with self.assertRaises(RuntimeError) as ctx:
            builder.build_listing_aware_cohort(
                target_size=1000,
                case_id_start=2222,
                a_exclude_csvs=exclude,
                profile_dir=builder.DEFAULT_S24_PROFILE_DIR,
                max_same_prefix=1000,
            )
        self.assertIn("listing_aware_cohort_undersized", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
