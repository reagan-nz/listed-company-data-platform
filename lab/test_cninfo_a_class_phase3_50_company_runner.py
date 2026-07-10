"""
A-class Phase 3 50-company runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_a_class_phase3_50_company_runner.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_metadata_expansion.py")
PHASE3_UNIVERSE = runner.DEFAULT_PHASE3_UNIVERSE_CSV
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
PHASE3_DRYRUN_REPORT = os.path.join(
    PHASE3_OUTPUT_ROOT, "reports", "a_class_phase3_50_company_dryrun_report.csv"
)
PHASE3_DRYRUN_SUMMARY = os.path.join(
    PHASE3_OUTPUT_ROOT, "reports", "a_class_phase3_50_company_dryrun_summary.md"
)
PHASE1_OUTPUT_ROOT = runner.PHASE1_OUTPUT_ROOT
EXPANSION_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
RETRY_V1_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_RETRY_V2_OUTPUT_ROOT
RETRY_V3_OUTPUT_ROOT = runner.DEFAULT_RETRY_V3_OUTPUT_ROOT
PRECHECK_OUTPUT_ROOT = runner.PRECHECK_OUTPUT_ROOT
HARVEST_ROOT = runner.C_CLASS_HARVEST_ROOT

PHASE3_DRYRUN_ARGS = [
    "--phase3-50",
    "--dry-run",
    "--universe-csv",
    PHASE3_UNIVERSE,
    "--output-root",
    PHASE3_OUTPUT_ROOT,
]


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


def _file_sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class TestAClassPhase3FiftyCompanyRunner(unittest.TestCase):
    def test_dry_run_phase3_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(PHASE3_DRYRUN_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_phase3_requires_universe_csv(self) -> None:
        result = _run(["--phase3-50", "--dry-run"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_UNIVERSE_CSV_REQUIRED, result.stderr)

    def test_universe_size_must_equal_50(self) -> None:
        result = _run(PHASE3_DRYRUN_ARGS + ["--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_only_a3m001_through_a3m050_allowed(self) -> None:
        case = runner.Phase3UniverseCase(
            case_id="A3M099",
            company_code="601398",
            company_name="工商银行",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="",
            risk_level="low",
            phase1_overlap="no",
            phase2_overlap="no",
            phase3_include="yes",
            reason="test",
        )
        issues = runner.validate_phase3_case(case)
        self.assertIn(runner.NON_PHASE3_CASE_REJECTED, issues)

    def test_phase3_include_must_be_yes_for_all_rows(self) -> None:
        cases = runner.load_phase3_universe(PHASE3_UNIVERSE)
        self.assertEqual(len(cases), 50)
        for case in cases:
            self.assertEqual(case.phase3_include, "yes")

    def test_phase1_overlap_rejected(self) -> None:
        case = runner.Phase3UniverseCase(
            case_id="A3M001",
            company_code="600519",
            company_name="贵州茅台",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="",
            risk_level="low",
            phase1_overlap="yes",
            phase2_overlap="no",
            phase3_include="yes",
            reason="test",
        )
        issues = runner.validate_phase3_case(case)
        self.assertTrue(
            any(runner.PHASE1_OVERLAP_REJECTED in issue for issue in issues),
            msg=issues,
        )

    def test_phase2_overlap_rejected(self) -> None:
        case = runner.Phase3UniverseCase(
            case_id="A3M001",
            company_code="600036",
            company_name="招商银行",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="",
            risk_level="low",
            phase1_overlap="no",
            phase2_overlap="yes",
            phase3_include="yes",
            reason="test",
        )
        issues = runner.validate_phase3_case(case)
        self.assertTrue(
            any(runner.PHASE2_OVERLAP_REJECTED in issue for issue in issues),
            msg=issues,
        )

    def test_duplicate_company_code_rejected(self) -> None:
        with open(PHASE3_UNIVERSE, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        rows[1]["company_code"] = rows[0]["company_code"]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(tmp, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            tmp_path = tmp.name
        try:
            cases = runner.load_phase3_universe(tmp_path)
            ok, err = runner.validate_phase3_duplicate_company_codes(cases)
            self.assertFalse(ok)
            self.assertIn(runner.DUPLICATE_COMPANY_CODE_REJECTED, err)
        finally:
            os.unlink(tmp_path)

    def test_output_root_isolation_enforced(self) -> None:
        ok, err = runner.validate_phase3_output_root(PHASE3_OUTPUT_ROOT)
        self.assertTrue(ok, msg=err)

    def test_phase1_output_root_write_blocked(self) -> None:
        result = _run(
            PHASE3_DRYRUN_ARGS[:-2]
            + ["--output-root", PHASE1_OUTPUT_ROOT]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE1_BASELINE_WRITE_FORBIDDEN, result.stderr)

    def test_phase2_output_root_write_blocked(self) -> None:
        result = _run(
            PHASE3_DRYRUN_ARGS[:-2]
            + ["--output-root", EXPANSION_OUTPUT_ROOT]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE2_EXPANSION_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v1_output_root_write_blocked(self) -> None:
        result = _run(
            PHASE3_DRYRUN_ARGS[:-2]
            + ["--output-root", RETRY_V1_OUTPUT_ROOT]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V1_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v2_output_root_write_blocked(self) -> None:
        result = _run(
            PHASE3_DRYRUN_ARGS[:-2]
            + ["--output-root", RETRY_V2_OUTPUT_ROOT]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V2_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v3_output_root_write_blocked(self) -> None:
        result = _run(
            PHASE3_DRYRUN_ARGS[:-2]
            + ["--output-root", RETRY_V3_OUTPUT_ROOT]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V3_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_precheck_output_root_write_blocked(self) -> None:
        result = _run(
            PHASE3_DRYRUN_ARGS[:-2]
            + ["--output-root", PRECHECK_OUTPUT_ROOT]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PRECHECK_WRITE_FORBIDDEN, result.stderr)

    def test_harvest_output_root_write_blocked(self) -> None:
        result = _run(
            PHASE3_DRYRUN_ARGS[:-2]
            + ["--output-root", HARVEST_ROOT]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("c_class_harvest_output_root_forbidden", result.stderr)

    def test_live_mode_requires_phase3_approval_flag(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                [
                    "--phase3-50",
                    "--live",
                    "--universe-csv",
                    PHASE3_UNIVERSE,
                    "--output-root",
                    PHASE3_OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        wrong_flags = (
            "--approve-a-class-phase2-metadata-expansion",
            "--approve-a-class-phase2-failed-retry",
            "--approve-a-class-phase2-network-recovery-retry-v2",
            "--approve-a-class-phase2-retry-v3",
            "--approve-a-class-tiny-live-metadata",
            "--approve-phase1-tiny-live-metadata",
            "--approve-full-harvest",
            "--approve-b-class-tiny-live-validation",
        )
        for flag in wrong_flags:
            with mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                result = _run(
                    [
                        "--phase3-50",
                        "--live",
                        "--universe-csv",
                        PHASE3_UNIVERSE,
                        "--output-root",
                        PHASE3_OUTPUT_ROOT,
                        flag,
                    ]
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(runner.PHASE3_WRONG_APPROVAL, result.stderr)

    def test_pdf_download_blocked(self) -> None:
        result = _run(PHASE3_DRYRUN_ARGS + ["--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(PHASE3_DRYRUN_ARGS + ["--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag in ("--enable-ocr", "--enable-extraction"):
            result = _run(PHASE3_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_db_minio_rag_blocked(self) -> None:
        for flag in ("--write-db", "--write-minio", "--run-rag"):
            result = _run(PHASE3_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_verified_production_ready_blocked(self) -> None:
        for flag in ("--mark-verified", "--mark-production-ready"):
            result = _run(PHASE3_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_dry_run_report_generated(self) -> None:
        result = _run(PHASE3_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(PHASE3_DRYRUN_REPORT))
        with open(PHASE3_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 50)
        self.assertTrue(all(row["dryrun_status"] == "planned_ok" for row in rows))

    def test_dry_run_summary_generated(self) -> None:
        result = _run(PHASE3_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(PHASE3_DRYRUN_SUMMARY))
        with open(PHASE3_DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CNINFO calls | **0**", content)
        self.assertIn(runner.PHASE3_RUNNER_GATE, content)

    def test_input_universe_csv_not_mutated(self) -> None:
        before = _file_sha256(PHASE3_UNIVERSE)
        with open(PHASE3_UNIVERSE, newline="", encoding="utf-8") as f:
            header = next(csv.reader(f))
        self.assertIn("phase3_include", header)
        result = _run(PHASE3_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        after = _file_sha256(PHASE3_UNIVERSE)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
