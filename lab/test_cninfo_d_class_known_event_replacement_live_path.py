"""
D-class known-event replacement live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_d_class_known_event_replacement_live_path.py
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, List, Optional, Tuple
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_tiny_live_validation.py")
FILLED_UNIVERSE = runner.DEFAULT_REPLACEMENT_UNIVERSE_CSV
REPLACEMENT_OUTPUT_ROOT = runner.DEFAULT_REPLACEMENT_OUTPUT_ROOT
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
CALIBRATED_UNIVERSE = runner.CALIBRATED_UNIVERSE_CSV
ORIGINAL_UNIVERSE = runner.DEFAULT_UNIVERSE_CSV
LIVE_REPORT = os.path.join(
    REPLACEMENT_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_replacement_live_report.csv",
)
LIVE_SUMMARY = os.path.join(
    REPLACEMENT_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_replacement_live_summary.md",
)
QUALITY_REPORT = os.path.join(
    REPLACEMENT_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_replacement_quality_report.csv",
)

LIVE_ARGS = [
    "--live",
    "--known-event-replacement",
    "--universe-csv",
    FILLED_UNIVERSE,
    "--output-root",
    REPLACEMENT_OUTPUT_ROOT,
    "--approve-d-class-known-event-replacement-validation",
]


def _live_args(
    output_root: str = REPLACEMENT_OUTPUT_ROOT,
    universe_csv: str = FILLED_UNIVERSE,
    extra: Optional[list] = None,
) -> list:
    args = [
        "--live",
        "--known-event-replacement",
        "--universe-csv",
        universe_csv,
        "--output-root",
        output_root,
        "--approve-d-class-known-event-replacement-validation",
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


def _mock_cninfo_hit(
    _session: Any,
    _source_cfg: dict,
    _params_override: Optional[Dict[str, Any]],
    stats: runner.LiveStats,
    case_id: str,
) -> Tuple[Optional[Any], int, str]:
    stats.cninfo_requests += 1
    stats.case_request_counts[case_id] = stats.case_request_counts.get(case_id, 0) + 1
    code = "688671" if case_id == "DLC003R" else "301259"
    return (
        {"records": [{"SECCODE": code, "value": 1}]},
        200,
        "",
    )


def _run_live_inprocess(extra: Optional[list] = None) -> Tuple[int, mock.Mock]:
    with mock.patch.object(
        runner, "_cninfo_request", side_effect=_mock_cninfo_hit
    ) as mock_req, mock.patch("time.sleep"):
        rc = runner.main(_live_args(extra=extra or []))
    return rc, mock_req


class TestKnownEventReplacementLivePath(unittest.TestCase):
    def test_live_without_approval_flag_rejected_before_cninfo(self) -> None:
        result = _run(
            [
                "--live",
                "--known-event-replacement",
                "--universe-csv",
                FILLED_UNIVERSE,
                "--output-root",
                REPLACEMENT_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        result = _run(
            [
                "--live",
                "--known-event-replacement",
                "--universe-csv",
                FILLED_UNIVERSE,
                "--output-root",
                REPLACEMENT_OUTPUT_ROOT,
                "--approve-d-class-tiny-live-validation",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_WRONG_APPROVAL_FLAG, result.stderr)

    def test_live_with_approval_only_allows_dlc003r_dlc006r_probes(self) -> None:
        result = _run(_live_args(extra=["--cases", "DLC001"]))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_PROBE_CASE_ONLY, result.stderr)

    def test_baseline_reference_rows_do_not_call_cninfo(self) -> None:
        rc, mock_req = _run_live_inprocess()
        self.assertEqual(rc, 0)
        called_cases = {call.args[4] for call in mock_req.call_args_list}
        self.assertTrue(called_cases.issubset(runner.REPLACEMENT_PROBE_CASE_IDS))
        self.assertEqual(len(called_cases), 2)

    def test_original_dlc003_dlc006_rejected(self) -> None:
        rows = []
        with open(FILLED_UNIVERSE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["case_id"] == "DLC003R":
                    row = {**row, "case_id": "DLC003"}
                rows.append(row)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.csv")
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            result = _run(_live_args(universe_csv=path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_ORIGINAL_CASE_IN_UNIVERSE, result.stderr)

    def test_total_request_cap_at_most_44(self) -> None:
        plan003 = runner.build_replacement_probe_plan("DLC003R", 24)
        plan006 = runner.build_replacement_probe_plan("DLC006R", 20)
        self.assertLessEqual(len(plan003), 24)
        self.assertLessEqual(len(plan006), 20)
        self.assertLessEqual(len(plan003) + len(plan006), 44)

    def test_dlc003r_request_cap_at_most_24(self) -> None:
        plan = runner.build_replacement_probe_plan("DLC003R", 24)
        self.assertLessEqual(len(plan), 24)

    def test_dlc006r_request_cap_at_most_20(self) -> None:
        plan = runner.build_replacement_probe_plan("DLC006R", 20)
        self.assertLessEqual(len(plan), 20)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(_live_args(output_root=tmp))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_OUTPUT_ROOT_REQUIRED, result.stderr)

    def test_original_v1_universe_write_blocked(self) -> None:
        result = _run(_live_args(output_root=ORIGINAL_UNIVERSE))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_ORIGINAL_UNIVERSE_WRITE_BLOCKED, result.stderr)

    def test_calibrated_universe_write_blocked(self) -> None:
        result = _run(_live_args(output_root=CALIBRATED_UNIVERSE))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_CALIBRATED_UNIVERSE_WRITE_BLOCKED, result.stderr)

    def test_v1_execution_reports_write_blocked(self) -> None:
        result = _run(_live_args(output_root=V1_OUTPUT_ROOT))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_V1_OUTPUT_ROOT_WRITE_BLOCKED, result.stderr)

    def test_v2_execution_reports_write_blocked(self) -> None:
        result = _run(_live_args(output_root=V2_OUTPUT_ROOT))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.REPLACEMENT_V2_OUTPUT_ROOT_WRITE_BLOCKED, result.stderr)

    def test_pdf_ocr_extraction_blocked(self) -> None:
        for flag, token in (
            ("--pdf-download", runner.PDF_DOWNLOAD_BLOCKED),
            ("--ocr", runner.OCR_BLOCKED),
            ("--extraction", runner.EXTRACTION_BLOCKED),
        ):
            result = _run(_live_args(extra=[flag]))
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, token in (
            ("--db-write", runner.DB_WRITE_BLOCKED),
            ("--minio-write", runner.MINIO_WRITE_BLOCKED),
            ("--rag-run", runner.RAG_RUN_BLOCKED),
        ):
            result = _run(_live_args(extra=[flag]))
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, token in (
            ("--mark-verified", runner.VERIFIED_BLOCKED),
            ("--production-ready", runner.PRODUCTION_READY_BLOCKED),
        ):
            result = _run(_live_args(extra=[flag]))
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_future_live_report_paths_are_isolated(self) -> None:
        rc, _ = _run_live_inprocess()
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(LIVE_REPORT))
        self.assertTrue(os.path.isfile(LIVE_SUMMARY))
        self.assertTrue(os.path.isfile(QUALITY_REPORT))
        self.assertTrue(LIVE_REPORT.startswith(REPLACEMENT_OUTPUT_ROOT))
        self.assertFalse(LIVE_REPORT.startswith(V1_OUTPUT_ROOT))
        self.assertFalse(LIVE_REPORT.startswith(V2_OUTPUT_ROOT))

    def test_execution_gate_never_uses_pass(self) -> None:
        self.assertEqual(runner.REPLACEMENT_EXECUTION_GATE_PASS, "PASS_WITH_CAVEAT")
        self.assertNotEqual(runner.REPLACEMENT_EXECUTION_GATE_PASS, "PASS")
        gate = runner.compute_replacement_execution_gate(
            {
                "DLC003R": {"retrieval_status": "found", "record_count": "1", "quality_status": "pass", "notes": ""},
                "DLC006R": {"retrieval_status": "found", "record_count": "1", "quality_status": "pass", "notes": ""},
            }
        )
        self.assertNotEqual(gate, "PASS")

    def test_no_live_test_calls_real_cninfo(self) -> None:
        with mock.patch("requests.Session") as session_cls:
            session_cls.return_value.get.side_effect = AssertionError("real CNINFO get called")
            session_cls.return_value.post.side_effect = AssertionError(
                "real CNINFO post called"
            )
            rc, mock_req = _run_live_inprocess()
        self.assertEqual(rc, 0)
        self.assertGreater(mock_req.call_count, 0)

    def test_mock_both_success_produces_pass_with_caveat(self) -> None:
        gate = runner.compute_replacement_execution_gate(
            {
                "DLC003R": {
                    "retrieval_status": "found",
                    "record_count": "2",
                    "quality_status": "pass",
                    "notes": "found 2 row(s)",
                },
                "DLC006R": {
                    "retrieval_status": "found",
                    "record_count": "1",
                    "quality_status": "pass",
                    "notes": "found 1 row(s)",
                },
            }
        )
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_partial_success_produces_fail_review_required(self) -> None:
        gate = runner.compute_replacement_execution_gate(
            {
                "DLC003R": {
                    "retrieval_status": "found",
                    "record_count": "1",
                    "quality_status": "pass",
                    "notes": "",
                },
                "DLC006R": {
                    "retrieval_status": "empty_but_valid",
                    "record_count": "0",
                    "quality_status": "pass",
                    "notes": "exhausted bounded probe cap",
                },
            }
        )
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")

    def test_mock_both_fail_produces_fail_review_required(self) -> None:
        gate = runner.compute_replacement_execution_gate(
            {
                "DLC003R": {
                    "retrieval_status": "empty_but_valid",
                    "record_count": "0",
                    "quality_status": "pass",
                    "notes": "",
                },
                "DLC006R": {
                    "retrieval_status": "http_error",
                    "record_count": "0",
                    "quality_status": "blocked",
                    "notes": "network_error:timeout",
                },
            }
        )
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
