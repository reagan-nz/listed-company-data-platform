"""
C-class Era D fuller-market slice1 live path 回归测试（无 CNINFO · mock only）。

运行：
    python3 lab/test_cninfo_c_class_fuller_market_slice1_live_path.py
"""

from __future__ import annotations

import argparse
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import harvest_cninfo_c_class as harvest_runner  # noqa: E402
from harvest_cninfo_c_class import (  # noqa: E402
    BASE_DIR,
    COMPANY_HARVEST_STATUS_REL,
    DEFAULT_HARVEST_OUTPUT_ROOT,
    FULLER_MARKET_SLICE1_APPROVAL_REQUIRED,
    FULLER_MARKET_SLICE1_EXPECTED_COUNT,
    FULLER_MARKET_SLICE1_MOCK_ROOT_PREFIX,
    FULLER_MARKET_SLICE1_OUTPUT_ROOT,
    FULLER_MARKET_SLICE1_OUTPUT_ROOT_FORBIDDEN,
    FULLER_MARKET_SLICE1_OUTPUT_ROOT_REQUIRED,
    HOLD_SAMPLE_REL,
    PHASE2_BATCH_OUTPUT_ROOT,
    PHASE3_BATCH_OUTPUT_ROOT,
    PHASE35_BATCH_OUTPUT_ROOT,
    RUN_STATUS_REL,
    configure_harvest_output_root,
    enforce_live_approval_gate,
    reset_harvest_output_root,
    validate_fuller_market_slice1_output_root,
    validate_pre_live_harvest,
    _run_live_fuller_market_slice1,
    _planned_normalized_path,
    _planned_raw_path,
)
from validate_cninfo_c_class_scale_smoke import load_sample_companies  # noqa: E402

SLICE1_SAMPLE = os.path.join(
    BASE_DIR, "lab", "eval_companies_c_class_fuller_market_slice1_200.yaml",
)
HOLD_PATH = os.path.join(BASE_DIR, HOLD_SAMPLE_REL)
RUNNER = os.path.join(_LAB_DIR, "harvest_cninfo_c_class.py")
MOCK_LIVE_ROOT = f"{FULLER_MARKET_SLICE1_MOCK_ROOT_PREFIX}_live_test"
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_live_path_test_summary.md",
)


def _run_runner(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestFullerMarketSlice1LivePath(unittest.TestCase):
    def setUp(self) -> None:
        reset_harvest_output_root()

    def tearDown(self) -> None:
        reset_harvest_output_root()

    def test_case1_live_without_approval_fails(self) -> None:
        result = _run_runner([
            "--live",
            "--sample-file", "lab/eval_companies_c_class_fuller_market_slice1_200.yaml",
            "--output-root", FULLER_MARKET_SLICE1_OUTPUT_ROOT,
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(FULLER_MARKET_SLICE1_APPROVAL_REQUIRED, result.stderr)

        args = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            approve_fuller_market_slice1_harvest=False,
            resume=False,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit) as ctx:
                enforce_live_approval_gate(args, SLICE1_SAMPLE)
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn(FULLER_MARKET_SLICE1_APPROVAL_REQUIRED, buf.getvalue())

    def test_case2_wrong_approval_full_harvest_only_fails(self) -> None:
        companies = load_sample_companies(SLICE1_SAMPLE)[:10]
        ok, detail = validate_pre_live_harvest(
            SLICE1_SAMPLE,
            companies,
            HOLD_PATH,
            execution_mode="fuller_market_slice1",
            approve_full_harvest=True,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            approve_fuller_market_slice1_harvest=False,
            limit=10,
            resume=False,
            output_root=FULLER_MARKET_SLICE1_OUTPUT_ROOT,
        )
        self.assertFalse(ok)
        self.assertIn("approve_fuller_market_slice1_harvest_required", detail)

    def test_case3_output_root_isolation_rejects_863(self) -> None:
        ok, detail = validate_fuller_market_slice1_output_root(DEFAULT_HARVEST_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertIn(FULLER_MARKET_SLICE1_OUTPUT_ROOT_FORBIDDEN, detail)
        self.assertIn("default_863_root", detail)

    def test_case4_output_root_rejects_phase3_phase35(self) -> None:
        ok3, d3 = validate_fuller_market_slice1_output_root(PHASE3_BATCH_OUTPUT_ROOT)
        self.assertFalse(ok3)
        self.assertIn("phase3_batch_500_001", d3)

        ok35, d35 = validate_fuller_market_slice1_output_root(PHASE35_BATCH_OUTPUT_ROOT)
        self.assertFalse(ok35)
        self.assertIn("phase35_batch_500_001_resume", d35)

    def test_case5_output_root_required(self) -> None:
        ok, detail = validate_fuller_market_slice1_output_root(None)
        self.assertFalse(ok)
        self.assertEqual(detail, FULLER_MARKET_SLICE1_OUTPUT_ROOT_REQUIRED)

    def test_case6_approval_gate_returns_slice1_mode(self) -> None:
        args = argparse.Namespace(
            mode="live",
            limit=100,
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            approve_fuller_market_slice1_harvest=True,
            resume=False,
        )
        mode = enforce_live_approval_gate(args, SLICE1_SAMPLE)
        self.assertEqual(mode, "fuller_market_slice1")

    def test_case7_pre_live_pass_with_limit_and_isolated_root(self) -> None:
        companies = load_sample_companies(SLICE1_SAMPLE)[:100]
        ok, detail = validate_pre_live_harvest(
            SLICE1_SAMPLE,
            companies,
            HOLD_PATH,
            execution_mode="fuller_market_slice1",
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            approve_fuller_market_slice1_harvest=True,
            limit=100,
            resume=True,
            output_root=FULLER_MARKET_SLICE1_OUTPUT_ROOT,
        )
        self.assertTrue(ok, detail)
        self.assertIn("mode=fuller_market_slice1", detail)
        self.assertIn("resume=True", detail)

    def test_case8_resume_marker_isolated_under_output_root(self) -> None:
        configure_harvest_output_root(FULLER_MARKET_SLICE1_OUTPUT_ROOT)
        self.assertEqual(
            harvest_runner.RUN_STATUS_REL,
            f"{FULLER_MARKET_SLICE1_OUTPUT_ROOT}/run_status.json",
        )
        self.assertTrue(
            harvest_runner.COMPANY_HARVEST_STATUS_REL.endswith(
                "fuller_market_slice1_200/quality/company_harvest_status.csv"
            )
        )

    def test_case9_mock_root_routes_paths(self) -> None:
        configure_harvest_output_root(MOCK_LIVE_ROOT)
        ok, _ = validate_fuller_market_slice1_output_root(MOCK_LIVE_ROOT)
        self.assertTrue(ok)
        raw = _planned_raw_path("cninfo_company_basic_profile", "600000")
        self.assertTrue(raw.startswith(f"{MOCK_LIVE_ROOT}/raw/"))
        norm = _planned_normalized_path("cninfo_company_basic_profile", "600000")
        self.assertTrue(norm.startswith(f"{MOCK_LIVE_ROOT}/normalized/"))

    def test_case10_mock_live_run_no_cninfo(self) -> None:
        """mock run_live_harvest · 仅写 _mock_* 根 · CNINFO=0。"""
        companies = load_sample_companies(SLICE1_SAMPLE)[:2]
        args = argparse.Namespace(
            mode="live",
            limit=2,
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            approve_fuller_market_slice1_harvest=True,
            resume=False,
            output_root=MOCK_LIVE_ROOT,
            smoke_csv=os.path.join(tempfile.gettempdir(), "slice1_mock_smoke.csv"),
            smoke_md=os.path.join(tempfile.gettempdir(), "slice1_mock_smoke.md"),
        )
        configure_harvest_output_root(MOCK_LIVE_ROOT)
        mock_stats = {
            "http_requests": 0,
            "success_count": 0,
            "raw_files": 0,
            "normalized_files": 0,
        }
        with mock.patch(
            "harvest_cninfo_c_class.run_live_harvest",
            return_value=([], mock_stats),
        ) as live_mock:
            _run_live_fuller_market_slice1(args, SLICE1_SAMPLE, HOLD_PATH)
            live_mock.assert_called_once()
        self.assertEqual(live_mock.call_args[0][0], companies)

    def test_case11_dry_run_still_pass_cninfo_zero(self) -> None:
        result = _run_runner([
            "--dry-run",
            "--sample-file", "lab/eval_companies_c_class_fuller_market_slice1_200.yaml",
            "--output-root", f"{FULLER_MARKET_SLICE1_MOCK_ROOT_PREFIX}_dryrun/",
            "--output-csv",
            "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_harvest_dryrun_report.csv",
            "--output-md",
            "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_harvest_dryrun_summary.md",
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cninfo_requests=0", result.stdout)

    def test_case12_not_implemented_stub_removed(self) -> None:
        self.assertFalse(
            hasattr(harvest_runner, "FULLER_MARKET_SLICE1_LIVE_NOT_IMPLEMENTED"),
            "FULLER_MARKET_SLICE1_LIVE_NOT_IMPLEMENTED 应已移除",
        )
        args = argparse.Namespace(
            mode="live",
            limit=None,
            approve_full_harvest=False,
            approve_phase2_smoke_harvest=False,
            approve_phase3_batch_500_harvest=False,
            approve_fuller_market_slice1_harvest=True,
            resume=False,
        )
        mode = enforce_live_approval_gate(args, SLICE1_SAMPLE)
        self.assertEqual(mode, "fuller_market_slice1")


def write_summary(results: list) -> None:
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    passed = sum(1 for _, ok in results if ok)
    lines = [
        "# CNINFO C-Class Fuller-Market Slice1 Live Path Test Summary",
        "",
        f"## Result: **{passed}/{len(results)} PASS**",
        "",
        "| case | result |",
        "|------|--------|",
    ]
    for case_id, ok in results:
        lines.append(f"| `{case_id}` | **{'PASS' if ok else 'FAIL'}** |")
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFullerMarketSlice1LivePath)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    test_map = {
        "test_case1_live_without_approval_fails": "case_1_no_approval",
        "test_case2_wrong_approval_full_harvest_only_fails": "case_2_wrong_approval",
        "test_case3_output_root_isolation_rejects_863": "case_3_reject_863",
        "test_case4_output_root_rejects_phase3_phase35": "case_4_reject_phase3_phase35",
        "test_case5_output_root_required": "case_5_root_required",
        "test_case6_approval_gate_returns_slice1_mode": "case_6_gate_mode",
        "test_case7_pre_live_pass_with_limit_and_isolated_root": "case_7_pre_live_limit",
        "test_case8_resume_marker_isolated_under_output_root": "case_8_resume_isolated",
        "test_case9_mock_root_routes_paths": "case_9_mock_paths",
        "test_case10_mock_live_run_no_cninfo": "case_10_mock_live_no_cninfo",
        "test_case11_dry_run_still_pass_cninfo_zero": "case_11_dry_run",
        "test_case12_not_implemented_stub_removed": "case_12_stub_removed",
    }
    failed = {t[0]._testMethodName for t in result.failures + result.errors}  # type: ignore[attr-defined]
    final = [(cid, m not in failed) for m, cid in test_map.items()]
    write_summary(final)
    passed = sum(1 for _, ok in final if ok)
    print(f"\n{passed}/{len(final)} PASS")
    print(f"MD    {SUMMARY_PATH}")
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
