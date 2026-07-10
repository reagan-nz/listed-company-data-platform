"""
D-class known-event targeted probe live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_d_class_known_event_targeted_probe_live_path.py
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
UNIVERSE_CSV = runner.DEFAULT_TARGETED_PROBE_UNIVERSE_CSV
TARGETED_OUTPUT_ROOT = runner.DEFAULT_TARGETED_PROBE_OUTPUT_ROOT
DRYRUN_REPORT = runner.TARGETED_PROBE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.TARGETED_PROBE_DRYRUN_SUMMARY_MD
LIVE_REPORT = os.path.join(
    TARGETED_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_targeted_probe_live_report.csv",
)
LIVE_SUMMARY = os.path.join(
    TARGETED_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_targeted_probe_live_summary.md",
)
QUALITY_REPORT = os.path.join(
    TARGETED_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_targeted_probe_quality_report.csv",
)
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
REPLACEMENT_OUTPUT_ROOT = runner.DEFAULT_REPLACEMENT_OUTPUT_ROOT
CALIBRATED_UNIVERSE = runner.CALIBRATED_UNIVERSE_CSV
ORIGINAL_UNIVERSE = runner.DEFAULT_UNIVERSE_CSV


def _live_args(
    output_root: str = TARGETED_OUTPUT_ROOT,
    universe_csv: str = UNIVERSE_CSV,
    extra: Optional[list] = None,
) -> list:
    args = [
        "--live",
        "--known-event-targeted-probe",
        "--universe-csv",
        universe_csv,
        "--output-root",
        output_root,
        "--approve-d-class-known-event-targeted-probe",
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


def _mock_cninfo_hit(
    _session: Any,
    _source_cfg: dict,
    _params_override: Optional[Dict[str, Any]],
    stats: runner.LiveStats,
    case_id: str,
) -> Tuple[Optional[Any], int, str]:
    stats.cninfo_requests += 1
    stats.case_request_counts[case_id] = stats.case_request_counts.get(case_id, 0) + 1
    code = "688671" if case_id == "DLC003R-T01" else "301259"
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


class TestKnownEventTargetedProbeLivePath(unittest.TestCase):
    def test_live_without_approval_flag_rejected_before_cninfo(self) -> None:
        result = _run(
            [
                "--live",
                "--known-event-targeted-probe",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                TARGETED_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        result = _run(
            [
                "--live",
                "--known-event-targeted-probe",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                TARGETED_OUTPUT_ROOT,
                "--approve-d-class-known-event-replacement-validation",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_APPROVAL_FLAG, result.stderr)

    def test_live_with_approval_only_processes_targeted_probe_ids(self) -> None:
        rc, mock_req = _run_live_inprocess()
        self.assertEqual(rc, 0)
        called_cases = {call.args[4] for call in mock_req.call_args_list}
        self.assertEqual(called_cases, runner.TARGETED_PROBE_ALLOWED_IDS)

    def test_old_dlc003_dlc006_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "replacement_case_id": "DLC003"}
            if r["targeted_probe_id"] == "DLC003R-T01"
            else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "original.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(universe_csv=path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_ORIGINAL_CASE_IN_UNIVERSE, result.stderr)

    def test_replacement_live_mode_not_rerun(self) -> None:
        result = _run(
            _live_args(
                extra=[
                    "--known-event-replacement",
                    "--approve-d-class-known-event-replacement-validation",
                ]
            )
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_MIXED_MODE_BLOCKED, result.stderr)

    def test_baseline_rows_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "targeted_probe_id": "DLC001"}
            if r["targeted_probe_id"] == "DLC003R-T01"
            else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "baseline.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(universe_csv=path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_BASELINE_CASE_IN_UNIVERSE, result.stderr)

    def test_total_request_cap_at_most_24(self) -> None:
        rows = _read_universe_rows()
        plan_total = 0
        for row_dict in rows:
            row = runner.TargetedProbeUniverseRow(
                targeted_probe_id=row_dict["targeted_probe_id"],
                replacement_case_id=row_dict["replacement_case_id"],
                company_code=row_dict["company_code"],
                company_name=row_dict["company_name"],
                component=row_dict["component"],
                anchor_date=row_dict["anchor_date"],
                human_event_evidence_type=row_dict["human_event_evidence_type"],
                human_event_evidence_description=row_dict["human_event_evidence_description"],
                previous_replacement_live_status=row_dict["previous_replacement_live_status"],
                previous_record_count=row_dict["previous_record_count"],
                targeted_probe_include=row_dict["targeted_probe_include"],
                targeted_probe_strategy=row_dict["targeted_probe_strategy"],
                request_cap=row_dict["request_cap"],
                expected_behavior=row_dict["expected_behavior"],
                notes=row_dict["notes"],
            )
            plan_total += runner.compute_targeted_probe_planned_requests(row)
        self.assertLessEqual(plan_total, 24)

    def test_dlc003r_t01_request_cap_at_most_12(self) -> None:
        row = next(r for r in _read_universe_rows() if r["targeted_probe_id"] == "DLC003R-T01")
        plan = runner.build_targeted_probe_plan_dlc003r(row["anchor_date"], 12)
        self.assertLessEqual(len(plan), 12)

    def test_dlc006r_t01_request_cap_at_most_12(self) -> None:
        row = next(r for r in _read_universe_rows() if r["targeted_probe_id"] == "DLC006R-T01")
        plan = runner.build_targeted_probe_plan_dlc006r(row["anchor_date"], 12)
        self.assertLessEqual(len(plan), 12)

    def test_dlc003r_t01_anchor_date_must_be_2024_02_19(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "anchor_date": "2024-01-01"}
            if r["targeted_probe_id"] == "DLC003R-T01"
            else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(universe_csv=path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_ANCHOR_DATE, result.stderr)

    def test_dlc006r_t01_anchor_date_must_be_2024_07_16(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "anchor_date": "2024-01-01"}
            if r["targeted_probe_id"] == "DLC006R-T01"
            else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(universe_csv=path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_ANCHOR_DATE, result.stderr)

    def test_dlc003r_t01_component_must_be_restricted_shares_unlock(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "component": "margin_trading"}
            if r["targeted_probe_id"] == "DLC003R-T01"
            else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(universe_csv=path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_COMPONENT, result.stderr)

    def test_dlc006r_t01_component_must_be_shareholder_change(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "component": "margin_trading"}
            if r["targeted_probe_id"] == "DLC006R-T01"
            else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(_live_args(universe_csv=path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_COMPONENT, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(_live_args(output_root=tmp))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_OUTPUT_ROOT_REQUIRED, result.stderr)

    def test_original_v1_universe_write_blocked(self) -> None:
        result = _run(_live_args(output_root=ORIGINAL_UNIVERSE))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_ORIGINAL_UNIVERSE_WRITE_BLOCKED, result.stderr)

    def test_calibrated_universe_write_blocked(self) -> None:
        result = _run(_live_args(output_root=CALIBRATED_UNIVERSE))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_CALIBRATED_UNIVERSE_WRITE_BLOCKED, result.stderr)

    def test_v1_execution_reports_write_blocked(self) -> None:
        result = _run(_live_args(output_root=V1_OUTPUT_ROOT))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_V1_OUTPUT_ROOT_WRITE_BLOCKED, result.stderr)

    def test_v2_execution_reports_write_blocked(self) -> None:
        result = _run(_live_args(output_root=V2_OUTPUT_ROOT))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_V2_OUTPUT_ROOT_WRITE_BLOCKED, result.stderr)

    def test_replacement_live_reports_write_blocked(self) -> None:
        result = _run(_live_args(output_root=REPLACEMENT_OUTPUT_ROOT))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.TARGETED_PROBE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED, result.stderr
        )

    def test_targeted_probe_dryrun_reports_not_overwritten_by_live_writers(self) -> None:
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_REPORT, encoding="utf-8") as f:
            before_report = f.read()
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            before_summary = f.read()
        rc, _ = _run_live_inprocess()
        self.assertEqual(rc, 0)
        with open(DRYRUN_REPORT, encoding="utf-8") as f:
            after_report = f.read()
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            after_summary = f.read()
        self.assertEqual(before_report, after_report)
        self.assertEqual(before_summary, after_summary)

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
        self.assertTrue(LIVE_REPORT.startswith(TARGETED_OUTPUT_ROOT))
        self.assertFalse(LIVE_REPORT.startswith(V1_OUTPUT_ROOT))
        self.assertFalse(LIVE_REPORT.startswith(V2_OUTPUT_ROOT))
        self.assertFalse(LIVE_REPORT.startswith(REPLACEMENT_OUTPUT_ROOT))

    def test_execution_gate_never_uses_pass(self) -> None:
        self.assertEqual(runner.TARGETED_PROBE_EXECUTION_GATE_PASS, "PASS_WITH_CAVEAT")
        self.assertNotEqual(runner.TARGETED_PROBE_EXECUTION_GATE_PASS, "PASS")
        gate = runner.compute_targeted_probe_execution_gate(
            {
                "DLC003R-T01": {
                    "retrieval_status": "found",
                    "record_count": "1",
                    "quality_status": "pass",
                    "notes": "",
                },
                "DLC006R-T01": {
                    "retrieval_status": "found",
                    "record_count": "1",
                    "quality_status": "pass",
                    "notes": "",
                },
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
        gate = runner.compute_targeted_probe_execution_gate(
            {
                "DLC003R-T01": {
                    "retrieval_status": "found",
                    "record_count": "2",
                    "quality_status": "pass",
                    "notes": "found 2 row(s)",
                },
                "DLC006R-T01": {
                    "retrieval_status": "found",
                    "record_count": "1",
                    "quality_status": "pass",
                    "notes": "found 1 row(s)",
                },
            }
        )
        self.assertEqual(gate, "PASS_WITH_CAVEAT")

    def test_mock_partial_success_produces_fail_review_required(self) -> None:
        gate = runner.compute_targeted_probe_execution_gate(
            {
                "DLC003R-T01": {
                    "retrieval_status": "found",
                    "record_count": "1",
                    "quality_status": "pass",
                    "notes": "",
                },
                "DLC006R-T01": {
                    "retrieval_status": "empty_but_valid",
                    "record_count": "0",
                    "quality_status": "pass",
                    "notes": "exhausted bounded probe cap",
                },
            }
        )
        self.assertEqual(gate, "FAIL_REVIEW_REQUIRED")

    def test_mock_both_fail_produces_fail_review_required(self) -> None:
        gate = runner.compute_targeted_probe_execution_gate(
            {
                "DLC003R-T01": {
                    "retrieval_status": "empty_but_valid",
                    "record_count": "0",
                    "quality_status": "pass",
                    "notes": "",
                },
                "DLC006R-T01": {
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
