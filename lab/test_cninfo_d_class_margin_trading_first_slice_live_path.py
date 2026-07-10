"""
D-class margin_trading first-slice live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_d_class_margin_trading_first_slice_live_path.py
"""

from __future__ import annotations

import csv
import os
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
UNIVERSE_CSV = runner.DEFAULT_MARGIN_TRADING_FIRST_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT
DRYRUN_ARGS = [
    "--dry-run",
    "--margin-trading-first-slice",
    "--universe-csv",
    UNIVERSE_CSV,
    "--output-root",
    OUTPUT_ROOT,
]
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
REPLACEMENT_OUTPUT_ROOT = runner.DEFAULT_REPLACEMENT_OUTPUT_ROOT
TARGETED_OUTPUT_ROOT = runner.DEFAULT_TARGETED_PROBE_OUTPUT_ROOT


def _live_args(extra: Optional[list] = None) -> list:
    args = [
        "--live",
        "--margin-trading-first-slice",
        "--universe-csv",
        UNIVERSE_CSV,
        "--output-root",
        OUTPUT_ROOT,
        "--approve-d-class-margin-trading-first-slice",
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


def _mock_cninfo_margin_hit(
    _session: Any,
    _source_cfg: dict,
    _params_override: Optional[Dict[str, Any]],
    stats: runner.LiveStats,
    case_id: str,
) -> Tuple[Optional[Any], int, str]:
    stats.cninfo_requests += 1
    stats.case_request_counts[case_id] = stats.case_request_counts.get(case_id, 0) + 1
    code = runner.MARGIN_TRADING_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(case_id, "000895")
    return (
        {"data": {"records": [{"SECCODE": code, "SECNAME": "mock", "TRADEDATE": "2026-07-08"}]}},
        200,
        "",
    )


def _run_live_inprocess(extra: Optional[list] = None) -> Tuple[int, mock.Mock]:
    with mock.patch.object(
        runner, "_cninfo_request", side_effect=_mock_cninfo_margin_hit
    ) as mock_req, mock.patch("time.sleep"):
        rc = runner.main(_live_args(extra=extra or []))
    return rc, mock_req


class TestMarginTradingFirstSliceLivePath(unittest.TestCase):
    def test_live_without_approval_flag_rejected_before_cninfo(self) -> None:
        result = _run(
            [
                "--live",
                "--margin-trading-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                _live_args(extra=["--approve-d-class-known-event-targeted-probe"])
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_WRONG_APPROVAL_FLAG, result.stderr)

    def test_live_path_function_exists_and_wired(self) -> None:
        self.assertTrue(hasattr(runner, "execute_margin_trading_first_slice_live"))
        rc, mock_req = _run_live_inprocess()
        self.assertEqual(rc, 0)
        self.assertGreater(mock_req.call_count, 0)
        called_cases = {call.args[4] for call in mock_req.call_args_list}
        self.assertEqual(called_cases, runner.MARGIN_TRADING_FIRST_SLICE_ALLOWED_CASE_IDS)

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH, result.stderr)

    def test_only_dmt001_through_dmt005_allowed(self) -> None:
        rows = _read_universe_rows()
        rows[0] = {**rows[0], "case_id": "DMT999"}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_case.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_CASE_ID, result.stderr)

    def test_component_must_be_margin_trading(self) -> None:
        rows = _read_universe_rows()
        rows = [{**r, "component": "block_trade"} if r["case_id"] == "DMT002" else r for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_WRONG_COMPONENT, result.stderr)

    def test_688671_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [{**r, "company_code": "688671"} if r["case_id"] == "DMT003" else r for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_688671.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE, result.stderr)

    def test_301259_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [{**r, "company_code": "301259"} if r["case_id"] == "DMT004" else r for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_301259.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(extra=["--universe-csv", path]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        result = _run(_live_args(extra=["--output-root", V1_OUTPUT_ROOT]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.MARGIN_TRADING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED, result.stderr)

    def test_known_event_and_tiny_live_roots_write_blocked(self) -> None:
        for bad_root, token in [
            (V2_OUTPUT_ROOT, runner.MARGIN_TRADING_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED),
            (
                REPLACEMENT_OUTPUT_ROOT,
                runner.MARGIN_TRADING_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                TARGETED_OUTPUT_ROOT,
                runner.MARGIN_TRADING_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
        ]:
            with self.subTest(bad_root=bad_root):
                result = _run(_live_args(extra=["--output-root", bad_root]))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_request_cap_lte_20_in_planning(self) -> None:
        rows = _read_universe_rows()
        total = 0
        for r in rows:
            row = runner.MarginTradingFirstSliceRow(
                case_id=r["case_id"],
                company_code=r["company_code"],
                company_name=r["company_name"],
                component=r["component"],
                market=r["market"],
                anchor_tdate=r["anchor_tdate"],
                first_slice_include=r["first_slice_include"],
                expected_behavior=r["expected_behavior"],
                reason=r.get("reason", ""),
                dlc001_reference=r.get("dlc001_reference", ""),
            )
            total += runner.compute_margin_trading_first_slice_planned_requests(row)
        self.assertLessEqual(total, runner.MARGIN_TRADING_FIRST_SLICE_TOTAL_MAX_REQUESTS)

    def test_pdf_download_blocked(self) -> None:
        result = _run(DRYRUN_ARGS + ["--pdf-download"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_BLOCKED, result.stderr)

    def test_pdf_parser_blocked_via_extraction(self) -> None:
        result = _run(DRYRUN_ARGS + ["--extraction"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.EXTRACTION_BLOCKED, result.stderr)

    def test_ocr_blocked(self) -> None:
        result = _run(DRYRUN_ARGS + ["--ocr"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.OCR_BLOCKED, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, token in [
            ("--db-write", runner.DB_WRITE_BLOCKED),
            ("--minio-write", runner.MINIO_WRITE_BLOCKED),
            ("--rag-run", runner.RAG_RUN_BLOCKED),
        ]:
            with self.subTest(flag=flag):
                result = _run(DRYRUN_ARGS + [flag])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, token in [
            ("--mark-verified", runner.VERIFIED_BLOCKED),
            ("--production-ready", runner.PRODUCTION_READY_BLOCKED),
        ]:
            with self.subTest(flag=flag):
                result = _run(DRYRUN_ARGS + [flag])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_disclosure_only_reason_does_not_upgrade_captured_normal(self) -> None:
        row = runner.MarginTradingFirstSliceRow(
            case_id="DMT001",
            company_code="000895",
            company_name="双汇发展",
            component="margin_trading",
            market="szse_main",
            anchor_tdate="2026-07-08",
            first_slice_include="yes",
            expected_behavior="captured_normal_candidate",
            reason="human disclosure evidence only; not structured capture",
            dlc001_reference="yes",
        )
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        self.assertFalse(runner.is_margin_trading_first_slice_acceptable(row, summary))

    def test_live_path_uses_mock_not_real_cninfo_in_offline_task(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            rc, _ = _run_live_inprocess()
        self.assertEqual(rc, 0)
        get_mock.assert_not_called()
        post_mock.assert_not_called()

    def test_dry_run_still_five_of_five_and_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(DRYRUN_ARGS)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("cases=5", result.stdout)


if __name__ == "__main__":
    unittest.main()
