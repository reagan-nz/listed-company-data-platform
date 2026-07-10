"""
D-class restricted_shares_unlock first-slice live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_d_class_restricted_shares_unlock_first_slice_live_path.py
"""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, Optional, Tuple
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_tiny_live_validation.py")
UNIVERSE_CSV = runner.DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
PRODUCTION_LIVE_REPORT = os.path.join(
    OUTPUT_ROOT,
    "reports",
    "d_class_restricted_shares_unlock_first_slice_live_report.csv",
)
DRYRUN_ARGS = [
    "--dry-run",
    "--restricted-shares-unlock-first-slice",
    "--universe-csv",
    UNIVERSE_CSV,
    "--output-root",
    OUTPUT_ROOT,
]
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
REPLACEMENT_OUTPUT_ROOT = runner.DEFAULT_REPLACEMENT_OUTPUT_ROOT
TARGETED_OUTPUT_ROOT = runner.DEFAULT_TARGETED_PROBE_OUTPUT_ROOT
MARGIN_OUTPUT_ROOT = runner.DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT
DISCLOSURE_OUTPUT_ROOT = runner.DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT
BLOCK_TRADE_OUTPUT_ROOT = runner.DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT
BLOCK_TRADE_UNIVERSE_CSV = runner.DEFAULT_BLOCK_TRADE_FIRST_SLICE_UNIVERSE_CSV
MARGIN_UNIVERSE_CSV = runner.DEFAULT_MARGIN_TRADING_FIRST_SLICE_UNIVERSE_CSV
MOCK_LIVE_PARENT = os.path.join(OUTPUT_ROOT, "_mock_live_tests")


def _live_args(output_root: str, extra: Optional[list] = None) -> list:
    args = [
        "--live",
        "--restricted-shares-unlock-first-slice",
        "--universe-csv",
        UNIVERSE_CSV,
        "--output-root",
        output_root,
        "--approve-d-class-restricted-shares-unlock-first-slice",
    ]
    if extra:
        args.extend(extra)
    return args


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


def _read_universe_rows() -> list[dict[str, str]]:
    with open(UNIVERSE_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_universe_csv(path: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _rsu_row_from_dict(r: dict[str, str]) -> runner.RestrictedSharesUnlockFirstSliceRow:
    return runner.RestrictedSharesUnlockFirstSliceRow(
        case_id=r["case_id"],
        company_code=r["company_code"],
        company_name=r["company_name"],
        component=r["component"],
        market=r["market"],
        anchor_tdate=r["anchor_tdate"],
        first_slice_include=r["first_slice_include"],
        expected_behavior=r["expected_behavior"],
        exclude_flags=r.get("exclude_flags", ""),
        notes=r.get("notes", ""),
        dlc003_reference=r.get("dlc003_reference", ""),
    )


def _mock_cninfo_rsu(
    _session: Any,
    _source_cfg: dict,
    _params_override: Optional[Dict[str, Any]],
    stats: runner.LiveStats,
    case_id: str,
) -> Tuple[Optional[Any], int, str]:
    stats.cninfo_requests += 1
    stats.case_request_counts[case_id] = stats.case_request_counts.get(case_id, 0) + 1
    if case_id == "DRU001":
        return ({"data": {"records": []}}, 200, "")
    code = runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(
        case_id, "000895"
    )
    return (
        {
            "data": {
                "records": [
                    {
                        "SECCODE": code,
                        "SECNAME": "mock",
                        "F003D": "2026-06-08",
                        "F004N": "1000",
                        "F005N": "0.01",
                    }
                ]
            }
        },
        200,
        "",
    )


def _mock_live_output_root() -> str:
    os.makedirs(MOCK_LIVE_PARENT, exist_ok=True)
    return tempfile.mkdtemp(dir=MOCK_LIVE_PARENT, prefix="live_")


def _run_live_inprocess(
    output_root: Optional[str] = None,
    extra: Optional[list] = None,
) -> Tuple[int, mock.Mock, str]:
    root = output_root or _mock_live_output_root()
    with mock.patch.object(
        runner, "_cninfo_request", side_effect=_mock_cninfo_rsu
    ) as mock_req, mock.patch("time.sleep"):
        rc = runner.main(_live_args(root, extra=extra))
    return rc, mock_req, root


class TestRestrictedSharesUnlockFirstSliceLivePath(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.isdir(MOCK_LIVE_PARENT):
            shutil.rmtree(MOCK_LIVE_PARENT, ignore_errors=True)

    def test_live_without_approval_flag_rejected_before_cninfo(self) -> None:
        result = _run(
            [
                "--live",
                "--restricted-shares-unlock-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_APPROVAL_REQUIRED,
            result.stderr,
        )

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                _live_args(OUTPUT_ROOT, extra=["--approve-d-class-block-trade-first-slice"])
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_APPROVAL_FLAG,
            result.stderr,
        )

    def test_live_path_function_exists_and_wired(self) -> None:
        self.assertTrue(hasattr(runner, "execute_restricted_shares_unlock_first_slice_live"))
        rc, mock_req, root = _run_live_inprocess()
        self.assertEqual(rc, 0)
        self.assertGreaterEqual(mock_req.call_count, 5)
        self.assertLessEqual(
            mock_req.call_count,
            runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TOTAL_MAX_REQUESTS,
        )
        called_cases = {call.args[4] for call in mock_req.call_args_list}
        self.assertEqual(
            called_cases, runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ALLOWED_CASE_IDS
        )
        live_report = os.path.join(
            root,
            "reports",
            "d_class_restricted_shares_unlock_first_slice_live_report.csv",
        )
        self.assertTrue(os.path.isfile(live_report))

    def test_live_stub_removed(self) -> None:
        rc, _, _ = _run_live_inprocess()
        self.assertEqual(rc, 0)

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(OUTPUT_ROOT, extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH,
            result.stderr,
        )

    def test_only_dru001_through_dru005_allowed(self) -> None:
        rows = _read_universe_rows()
        rows[0] = {**rows[0], "case_id": "DRU999"}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_case.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(OUTPUT_ROOT, extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_FORBIDDEN_CASE_ID,
            result.stderr,
        )

    def test_component_must_be_restricted_shares_unlock(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "component": "block_trade"} if r["case_id"] == "DRU002" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(OUTPUT_ROOT, extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_COMPONENT,
            result.stderr,
        )

    def test_688671_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "company_code": "688671"} if r["case_id"] == "DRU003" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_688671.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(OUTPUT_ROOT, extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_FORBIDDEN_COMPANY_CODE,
            result.stderr,
        )

    def test_301259_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "company_code": "301259"} if r["case_id"] == "DRU004" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_301259.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(OUTPUT_ROOT, extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_FORBIDDEN_COMPANY_CODE,
            result.stderr,
        )

    def test_output_root_isolation_enforced(self) -> None:
        result = _run(_live_args(V1_OUTPUT_ROOT))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED,
            result.stderr,
        )

    def test_closed_track_roots_write_blocked(self) -> None:
        for bad_root, token in [
            (V2_OUTPUT_ROOT, runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED),
            (
                REPLACEMENT_OUTPUT_ROOT,
                runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                TARGETED_OUTPUT_ROOT,
                runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                MARGIN_OUTPUT_ROOT,
                runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                DISCLOSURE_OUTPUT_ROOT,
                runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                BLOCK_TRADE_OUTPUT_ROOT,
                runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
        ]:
            with self.subTest(bad_root=bad_root):
                result = _run(_live_args(bad_root))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_request_cap_lte_20_in_planning(self) -> None:
        rows = _read_universe_rows()
        total = sum(
            runner.compute_restricted_shares_unlock_first_slice_planned_requests(
                _rsu_row_from_dict(r)
            )
            for r in rows
        )
        self.assertLessEqual(
            total, runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TOTAL_MAX_REQUESTS
        )
        self.assertEqual(total, 20)

    def test_execution_gate_pass_with_caveat_at_three_of_five(self) -> None:
        rows = [
            _rsu_row_from_dict(r)
            for r in _read_universe_rows()
            if r["case_id"] in ("DRU001", "DRU002", "DRU003")
        ]
        summaries = {
            "DRU001": {
                "retrieval_status": "empty_but_valid",
                "quality_status": "pass",
                "record_count": "0",
            },
            "DRU002": {
                "retrieval_status": "found",
                "quality_status": "pass",
                "record_count": "1",
            },
            "DRU003": {
                "retrieval_status": "empty_but_valid",
                "quality_status": "pass",
                "record_count": "0",
            },
        }
        gate = runner.compute_restricted_shares_unlock_first_slice_execution_gate(
            rows, summaries
        )
        self.assertEqual(
            gate, runner.RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXECUTION_GATE_PASS
        )

    def test_empty_but_valid_semantics_dru001(self) -> None:
        row = _rsu_row_from_dict(_read_universe_rows()[0])
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        self.assertTrue(
            runner.is_restricted_shares_unlock_first_slice_acceptable(row, summary)
        )

    def test_captured_normal_or_empty_but_valid_found(self) -> None:
        row = _rsu_row_from_dict(
            next(r for r in _read_universe_rows() if r["case_id"] == "DRU002")
        )
        summary = {
            "retrieval_status": "found",
            "quality_status": "pass",
            "record_count": "1",
        }
        self.assertTrue(
            runner.is_restricted_shares_unlock_first_slice_acceptable(row, summary)
        )

    def test_captured_normal_or_needs_review_found(self) -> None:
        row = _rsu_row_from_dict(
            next(r for r in _read_universe_rows() if r["case_id"] == "DRU004")
        )
        summary = {
            "retrieval_status": "found",
            "quality_status": "needs_review",
            "record_count": "1",
        }
        self.assertTrue(
            runner.is_restricted_shares_unlock_first_slice_acceptable(row, summary)
        )

    def test_disclosure_only_notes_does_not_upgrade_captured_normal(self) -> None:
        row = runner.RestrictedSharesUnlockFirstSliceRow(
            case_id="DRU002",
            company_code="000895",
            company_name="双汇发展",
            component="restricted_shares_unlock",
            market="szse_main",
            anchor_tdate="2026-06-08",
            first_slice_include="yes",
            expected_behavior="captured_normal_or_empty_but_valid",
            exclude_flags="",
            notes="human disclosure evidence only; not structured capture",
            dlc003_reference="no",
        )
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        self.assertFalse(
            runner.is_restricted_shares_unlock_first_slice_acceptable(row, summary)
        )

    def test_live_path_uses_mock_not_real_cninfo_in_offline_task(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            rc, _, _ = _run_live_inprocess()
        self.assertEqual(rc, 0)
        get_mock.assert_not_called()
        post_mock.assert_not_called()

    def test_mock_live_writes_under_isolated_subdir_not_production_report(self) -> None:
        self.assertFalse(os.path.isfile(PRODUCTION_LIVE_REPORT))
        rc, _, root = _run_live_inprocess()
        self.assertEqual(rc, 0)
        self.assertTrue(root.startswith(MOCK_LIVE_PARENT))
        self.assertFalse(os.path.isfile(PRODUCTION_LIVE_REPORT))

    def test_dry_run_still_five_of_five_and_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(DRYRUN_ARGS)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("cases=5", result.stdout)
        self.assertIn("planned_request_count_total=20", result.stdout)

    def test_block_trade_first_slice_mode_smoke_intact(self) -> None:
        if not os.path.isfile(BLOCK_TRADE_UNIVERSE_CSV):
            self.skipTest("block_trade universe not present")
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                [
                    "--dry-run",
                    "--block-trade-first-slice",
                    "--universe-csv",
                    BLOCK_TRADE_UNIVERSE_CSV,
                    "--output-root",
                    BLOCK_TRADE_OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_margin_trading_first_slice_mode_smoke_intact(self) -> None:
        if not os.path.isfile(MARGIN_UNIVERSE_CSV):
            self.skipTest("margin_trading universe not present")
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                [
                    "--dry-run",
                    "--margin-trading-first-slice",
                    "--universe-csv",
                    MARGIN_UNIVERSE_CSV,
                    "--output-root",
                    MARGIN_OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("cninfo_calls=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
