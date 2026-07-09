"""
A-class Phase 2 metadata expansion runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_a_class_phase2_metadata_expansion_runner.py
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

import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_metadata_expansion.py")
UNIVERSE = runner.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
DRYRUN_REPORT = runner.DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.DRYRUN_SUMMARY_MD


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestAClassPhase2MetadataExpansionRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(["--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_live_requires_approve_a_class_phase2_metadata_expansion(self) -> None:
        result = _run(["--live"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE2_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected(self) -> None:
        wrong_flags = (
            "--approve-a-class-tiny-live-metadata",
            "--approve-phase1-tiny-live-metadata",
            "--approve-full-harvest",
            "--approve-phase2-smoke-harvest",
            "--approve-phase3-batch-500-harvest",
            "--approve-b-class-tiny-live-validation",
        )
        for flag in wrong_flags:
            result = _run(["--live", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_universe_size_must_equal_20(self) -> None:
        result = _run(["--dry-run", "--limit", "5"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_only_a2m_cases_allowed(self) -> None:
        case = runner.Phase2UniverseCase(
            case_id="ALM001",
            company_code="600000",
            company_name="浦发银行",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="英文",
            risk_level="low",
            phase1_overlap="no",
            phase2_include="yes",
            reason="",
        )
        issues = runner.validate_phase2_case(case)
        self.assertIn(runner.NON_PHASE2_CASE_REJECTED, issues)

    def test_phase2_include_must_be_yes(self) -> None:
        case = runner.Phase2UniverseCase(
            case_id="A2M099",
            company_code="600036",
            company_name="招商银行",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="英文",
            risk_level="low",
            phase1_overlap="no",
            phase2_include="no",
            reason="",
        )
        issues = runner.validate_phase2_case(case)
        self.assertIn(runner.PHASE2_INCLUDE_REQUIRED, issues)

    def test_phase1_overlap_rejected(self) -> None:
        case = runner.Phase2UniverseCase(
            case_id="A2M099",
            company_code="600519",
            company_name="贵州茅台",
            market="SSE",
            report_type="annual_report",
            expected_period="2024-12-31",
            expected_title_keywords="年度报告",
            excluded_title_keywords="英文",
            risk_level="low",
            phase1_overlap="yes",
            phase2_include="yes",
            reason="",
        )
        issues = runner.validate_phase2_case(case)
        self.assertTrue(
            any(runner.PHASE1_OVERLAP_REJECTED in i for i in issues),
            msg=issues,
        )

    def test_pdf_download_blocked(self) -> None:
        result = _run(["--dry-run", "--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(["--dry-run", "--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--enable-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--enable-extraction", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, err in (
            ("--write-db", runner.DB_WRITE_REQUESTED_NOT_ALLOWED),
            ("--write-minio", runner.MINIO_WRITE_REQUESTED_NOT_ALLOWED),
            ("--run-rag", runner.RAG_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, err in (
            ("--mark-verified", runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
            ("--mark-production-ready", runner.PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_dry_run_report_generated(self) -> None:
        result = _run(["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), runner.REQUIRED_UNIVERSE_SIZE)
        self.assertEqual(set(rows[0].keys()), set(runner.DRYRUN_COLUMNS))
        for row in rows:
            self.assertEqual(row["pdf_download"], "0")
            self.assertEqual(row["pdf_parse"], "0")
            self.assertEqual(row["ocr"], "0")
            self.assertEqual(row["extraction"], "0")
            self.assertEqual(row["cninfo_call_planned"], "0")
            self.assertEqual(row["dryrun_status"], "planned_ok")

    def test_report_type_mix_validated_as_8_4_4_4(self) -> None:
        cases = runner.load_universe(UNIVERSE)
        ok, err = runner.validate_report_type_mix(cases)
        self.assertTrue(ok, msg=err)
        included = [c for c in cases if c.phase2_include == "yes"]
        counts: dict[str, int] = {}
        for case in included:
            counts[case.report_type] = counts.get(case.report_type, 0) + 1
        self.assertEqual(counts, runner.EXPECTED_REPORT_TYPE_MIX)

    def test_v2_title_matching_logic_loaded(self) -> None:
        self.assertEqual(runner.MATCHING_LOGIC_VERSION, "v2")
        matched, reason = runner.tiny_live.match_title_for_report_type(
            "2024年年度报告",
            "annual_report",
            "2024-12-31",
        )
        self.assertTrue(matched, msg=reason)
        matched_en, reason_en = runner.tiny_live.match_title_for_report_type(
            "2024 Third Quarterly Report (English)",
            "quarterly_report_q3",
            "2024-09-30",
        )
        self.assertFalse(matched_en)
        self.assertIn("english", reason_en.lower())


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
