"""
B-class Phase 2.5 expansion runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_b_class_phase25_expansion_runner.py
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

import run_cninfo_b_class_phase25_expansion_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_b_class_phase25_expansion_validation.py")
UNIVERSE = runner.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
DRYRUN_REPORT = runner.DRYRUN_REPORT_CSV

PHASE25_HEADER = (
    "case_id,company_code,company_name,market,announcement_type,target_endpoint,"
    "expected_lineage_type,risk_level,phase1_overlap,phase2_overlap,phase25_include,reason\n"
)


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestPhase25ExpansionRunner(unittest.TestCase):
    def test_dry_run_default_no_network(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(["--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_live_without_approval_blocked(self) -> None:
        result = _run(["--live"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE25_APPROVAL_REQUIRED, result.stderr)

    def test_live_with_wrong_approval_flags_blocked(self) -> None:
        wrong_flags = (
            "--approve-b-class-phase2-expansion",
            "--approve-b-class-tiny-live-validation",
            "--approve-b-class-tlc002-retry",
            "--approve-full-harvest",
            "--approve-phase2-smoke-harvest",
            "--approve-phase3-batch-500-harvest",
        )
        for flag in wrong_flags:
            result = _run(["--live", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_output_root_isolation_rejects_foreign_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_output_root_isolation_accepts_default_root(self) -> None:
        ok, err = runner.validate_output_root(OUTPUT_ROOT)
        self.assertTrue(ok)
        self.assertEqual(err, "")

    def test_universe_size_must_equal_50(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write(PHASE25_HEADER)
            f.write(
                "B25E001,600900,测试,SSE主板,periodic_report,EP001;EP004,"
                "periodic_report_metadata_lineage,low,no,no,yes,test\n"
            )
            bad_path = f.name
        try:
            result = _run(["--dry-run", "--universe-csv", bad_path])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.UNIVERSE_SIZE_VIOLATION, result.stderr)
        finally:
            os.unlink(bad_path)

    def test_only_b25e_cases_allowed(self) -> None:
        case = runner.Phase25UniverseCase(
            case_id="B2E001",
            company_code="600900",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            expected_lineage_type="periodic_report_metadata_lineage",
            risk_level="low",
            phase1_overlap="no",
            phase2_overlap="no",
            phase25_include="yes",
            reason="",
        )
        issues = runner.validate_phase25_case(case)
        self.assertIn(runner.NON_PHASE25_CASE_REJECTED, issues)

    def test_phase25_include_must_be_yes(self) -> None:
        case = runner.Phase25UniverseCase(
            case_id="B25E099",
            company_code="600900",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            expected_lineage_type="periodic_report_metadata_lineage",
            risk_level="low",
            phase1_overlap="no",
            phase2_overlap="no",
            phase25_include="no",
            reason="",
        )
        issues = runner.validate_phase25_case(case)
        self.assertIn(runner.PHASE25_INCLUDE_REQUIRED, issues)

    def test_phase1_overlap_rejected(self) -> None:
        case = runner.Phase25UniverseCase(
            case_id="B25E099",
            company_code="000895",
            company_name="双汇发展",
            market="SZSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            expected_lineage_type="periodic_report_metadata_lineage",
            risk_level="low",
            phase1_overlap="yes",
            phase2_overlap="no",
            phase25_include="yes",
            reason="",
        )
        issues = runner.validate_phase25_case(case)
        self.assertIn(runner.PHASE1_OVERLAP_REJECTED, issues)

    def test_phase2_overlap_rejected(self) -> None:
        case = runner.Phase25UniverseCase(
            case_id="B25E099",
            company_code="000001",
            company_name="平安银行",
            market="SZSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            expected_lineage_type="periodic_report_metadata_lineage",
            risk_level="low",
            phase1_overlap="no",
            phase2_overlap="yes",
            phase25_include="yes",
            reason="",
        )
        issues = runner.validate_phase25_case(case)
        self.assertIn(runner.PHASE2_OVERLAP_REJECTED, issues)

    def test_pdf_download_blocked(self) -> None:
        result = _run(["--dry-run", "--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(["--dry-run", "--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

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
        self.assertTrue(os.path.isfile(DRYRUN_REPORT), msg=DRYRUN_REPORT)
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), runner.REQUIRED_UNIVERSE_SIZE)
        self.assertEqual(set(rows[0].keys()), set(runner.DRYRUN_REPORT_COLUMNS))
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
        for row in rows:
            self.assertEqual(row["cninfo_call_planned"], "0")
            self.assertEqual(row["pdf_download"], "0")
            self.assertEqual(row["pdf_parse"], "0")
        for root, _dirs, files in os.walk(OUTPUT_ROOT):
            for name in files:
                self.assertFalse(name.lower().endswith(".pdf"), msg=name)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary_path = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_b_class_phase25_expansion_runner_test_summary.md",
    )
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(
            "# B-class Phase 2.5 Expansion Runner Test Summary\n\n"
            f"- tests_run: {result.testsRun}\n"
            f"- passed: {passed}\n"
            f"- failed: {len(result.failures)}\n"
            f"- errors: {len(result.errors)}\n"
            f"- CNINFO calls: **0**\n"
            f"- gate: **READY_FOR_APPROVAL** (runner offline prep)\n"
        )
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
