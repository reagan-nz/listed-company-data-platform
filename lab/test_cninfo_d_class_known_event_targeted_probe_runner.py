"""
D-class known-event targeted probe runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_d_class_known_event_targeted_probe_runner.py
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_tiny_live_validation.py")
UNIVERSE_CSV = runner.DEFAULT_TARGETED_PROBE_UNIVERSE_CSV
TARGETED_OUTPUT_ROOT = runner.DEFAULT_TARGETED_PROBE_OUTPUT_ROOT
TARGETED_DRYRUN_REPORT = runner.TARGETED_PROBE_DRYRUN_REPORT_CSV
TARGETED_DRYRUN_SUMMARY = runner.TARGETED_PROBE_DRYRUN_SUMMARY_MD
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
REPLACEMENT_OUTPUT_ROOT = runner.DEFAULT_REPLACEMENT_OUTPUT_ROOT
CALIBRATED_UNIVERSE = runner.CALIBRATED_UNIVERSE_CSV
ORIGINAL_UNIVERSE = runner.DEFAULT_UNIVERSE_CSV

BASE_ARGS = [
    "--dry-run",
    "--known-event-targeted-probe",
    "--universe-csv",
    UNIVERSE_CSV,
    "--output-root",
    TARGETED_OUTPUT_ROOT,
]


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


class TestKnownEventTargetedProbeRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_known_event_targeted_probe_requires_universe_csv(self) -> None:
        result = _run(["--dry-run", "--known-event-targeted-probe"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_UNIVERSE_CSV_REQUIRED, result.stderr)

    def test_live_requires_targeted_probe_approval_flag(self) -> None:
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

    def test_wrong_approval_flag_rejected(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-known-event-replacement-validation"]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_APPROVAL_FLAG, result.stderr)

    def test_universe_size_must_equal_2(self) -> None:
        rows = _read_universe_rows()[:1]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_UNIVERSE_SIZE_MISMATCH, result.stderr)

    def test_only_dlc003r_t01_and_dlc006r_t01_allowed(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "targeted_probe_id": "DLC003R-T99"} if r["targeted_probe_id"] == "DLC003R-T01" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_id.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_FORBIDDEN_CASE_ID, result.stderr)

    def test_old_dlc003_dlc006_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "replacement_case_id": "DLC003"} if r["targeted_probe_id"] == "DLC003R-T01" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "original_case.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_ORIGINAL_CASE_IN_UNIVERSE, result.stderr)

    def test_baseline_rows_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "targeted_probe_id": "DLC001"} if r["targeted_probe_id"] == "DLC003R-T01" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "baseline.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_BASELINE_CASE_IN_UNIVERSE, result.stderr)

    def test_dlc003r_t01_company_code_must_equal_688671(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "company_code": "999999"} if r["targeted_probe_id"] == "DLC003R-T01" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_code.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_COMPANY_CODE, result.stderr)

    def test_dlc006r_t01_company_code_must_equal_301259(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "company_code": "999999"} if r["targeted_probe_id"] == "DLC006R-T01" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_code.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_COMPANY_CODE, result.stderr)

    def test_dlc003r_t01_component_must_equal_restricted_shares_unlock(self) -> None:
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
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_COMPONENT, result.stderr)

    def test_dlc006r_t01_component_must_equal_shareholder_change(self) -> None:
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
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_COMPONENT, result.stderr)

    def test_dlc003r_t01_anchor_date_must_equal_2024_02_19(self) -> None:
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
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_ANCHOR_DATE, result.stderr)

    def test_dlc006r_t01_anchor_date_must_equal_2024_07_16(self) -> None:
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
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_WRONG_ANCHOR_DATE, result.stderr)

    def test_per_row_request_cap_lte_12(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "request_cap": "13"} if r["targeted_probe_id"] == "DLC003R-T01" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_cap.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_ROW_CAP_EXCEEDED, result.stderr)

    def test_total_request_cap_lte_24(self) -> None:
        rows = _read_universe_rows()
        rows = [{**r, "request_cap": "13"} for r in rows]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_total_cap.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_ROW_CAP_EXCEEDED, result.stderr)

    def test_targeted_probe_include_must_be_yes(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "targeted_probe_include": "no"}
            if r["targeted_probe_id"] == "DLC003R-T01"
            else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_include.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--known-event-targeted-probe",
                    "--universe-csv",
                    path,
                    "--output-root",
                    TARGETED_OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_INCLUDE_REQUIRED, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(BASE_ARGS + ["--output-root", tmp])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_OUTPUT_ROOT_REQUIRED, result.stderr)

    def test_original_v1_universe_write_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--output-root", ORIGINAL_UNIVERSE])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_ORIGINAL_UNIVERSE_WRITE_BLOCKED, result.stderr)

    def test_calibrated_universe_write_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--output-root", CALIBRATED_UNIVERSE])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_CALIBRATED_UNIVERSE_WRITE_BLOCKED, result.stderr)

    def test_v1_v2_execution_reports_write_blocked(self) -> None:
        result_v1 = _run(BASE_ARGS + ["--output-root", V1_OUTPUT_ROOT])
        self.assertNotEqual(result_v1.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_V1_OUTPUT_ROOT_WRITE_BLOCKED, result_v1.stderr)
        result_v2 = _run(BASE_ARGS + ["--output-root", V2_OUTPUT_ROOT])
        self.assertNotEqual(result_v2.returncode, 0)
        self.assertIn(runner.TARGETED_PROBE_V2_OUTPUT_ROOT_WRITE_BLOCKED, result_v2.stderr)

    def test_replacement_live_reports_write_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--output-root", REPLACEMENT_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.TARGETED_PROBE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED, result.stderr
        )

    def test_pdf_ocr_extraction_blocked(self) -> None:
        for flag, token in (
            ("--pdf-download", runner.PDF_DOWNLOAD_BLOCKED),
            ("--ocr", runner.OCR_BLOCKED),
            ("--extraction", runner.EXTRACTION_BLOCKED),
        ):
            result = _run(BASE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with open(TARGETED_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            self.assertEqual(row["pdf_download"], "no")
            self.assertEqual(row["ocr"], "no")
            self.assertEqual(row["extraction"], "no")

    def test_db_minio_rag_blocked(self) -> None:
        for flag, token in (
            ("--db-write", runner.DB_WRITE_BLOCKED),
            ("--minio-write", runner.MINIO_WRITE_BLOCKED),
            ("--rag-run", runner.RAG_RUN_BLOCKED),
        ):
            result = _run(BASE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, token in (
            ("--mark-verified", runner.VERIFIED_BLOCKED),
            ("--production-ready", runner.PRODUCTION_READY_BLOCKED),
        ):
            result = _run(BASE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(token, result.stderr)

    def test_dry_run_report_generated(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(TARGETED_DRYRUN_REPORT), msg=TARGETED_DRYRUN_REPORT)
        with open(TARGETED_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)
        self.assertEqual(set(rows[0].keys()), set(runner.TARGETED_PROBE_DRYRUN_REPORT_COLUMNS))
        self.assertEqual(sum(1 for r in rows if r["dryrun_status"] == "planned_ok"), 2)
        planned_total = sum(int(r["planned_request_count"]) for r in rows)
        self.assertLessEqual(planned_total, runner.TARGETED_PROBE_TOTAL_MAX_CAP)

    def test_dry_run_summary_generated(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(TARGETED_DRYRUN_SUMMARY), msg=TARGETED_DRYRUN_SUMMARY)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
