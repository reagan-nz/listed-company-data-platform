"""
B-class Phase 3 100 retry_v2 runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_b_class_phase3_100_retry_v2_runner.py
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

import run_cninfo_b_class_phase25_expansion_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_b_class_phase25_expansion_validation.py")
UNIVERSE = runner.DEFAULT_PHASE3_RETRY_V2_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
PHASE3_RETRY_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_OUTPUT_ROOT
EP002_PRECHECK_ROOT = runner.DEFAULT_EP002_PRECHECK_ROOT
PHASE25_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
PHASE25_RETRY_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
DRYRUN_REPORT = runner.PHASE3_RETRY_V2_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.PHASE3_RETRY_V2_DRYRUN_SUMMARY_MD

RETRY_V2_HEADER = (
    "retry_v2_case_id,original_case_id,company_code,company_name,market,"
    "announcement_type,target_endpoint,original_phase3_status,failed_retry_status,"
    "final_effective_status_before_retry_v2,persistent_failure_stage,schema_impact,"
    "quality_impact,ep002_precheck_signal,retry_v2_include,retry_v2_reason,risk_note,notes\n"
)

RETRY_V2_BASE_ARGS = [
    "--phase3-100-retry-v2",
    "--universe-csv",
    UNIVERSE,
    "--output-root",
    OUTPUT_ROOT,
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


def _sample_retry_v2_row(
    retry_v2_case_id: str = "B3R2_001",
    original_case_id: str = "B3E001",
) -> dict:
    return {
        "retry_v2_case_id": retry_v2_case_id,
        "original_case_id": original_case_id,
        "company_code": "600010",
        "company_name": "测试",
        "market": "SSE主板",
        "announcement_type": "periodic_report",
        "target_endpoint": "EP001;EP004",
        "original_phase3_status": "network_error",
        "failed_retry_status": "network_error",
        "final_effective_status_before_retry_v2": "unresolved_ep002_orgid_network_failure",
        "persistent_failure_stage": "EP002_topSearch_orgId",
        "schema_impact": "none",
        "quality_impact": "unresolved_network_caveat",
        "ep002_precheck_signal": "no_precheck_sample",
        "retry_v2_include": "yes",
        "retry_v2_reason": "x",
        "risk_note": "x",
        "notes": "x",
    }


class TestPhase3RetryV2Runner(unittest.TestCase):
    def test_dry_run_retry_v2_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(RETRY_V2_BASE_ARGS + ["--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_phase3_retry_v2_requires_universe_csv(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(RETRY_V2_HEADER)
            f.write(
                "B3R2_001,B3E001,600010,测试,SSE主板,periodic_report,EP001;EP004,"
                "network_error,network_error,unresolved_ep002_orgid_network_failure,"
                "EP002_topSearch_orgId,none,unresolved_network_caveat,no_precheck_sample,"
                "yes,x,x,x\n"
            )
            bad_path = f.name
        try:
            result = _run(
                [
                    "--phase3-100-retry-v2",
                    "--dry-run",
                    "--universe-csv",
                    bad_path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.PHASE3_RETRY_V2_UNIVERSE_CSV_REQUIRED, result.stderr)
        finally:
            os.unlink(bad_path)

    def test_retry_v2_universe_size_must_equal_91(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(
                tmp,
                fieldnames=list(_sample_retry_v2_row().keys()),
            )
            writer.writeheader()
            writer.writerow(_sample_retry_v2_row())
            tmp_path = tmp.name
        try:
            cases = runner.load_phase3_retry_v2_universe(tmp_path)
            ok, err = runner.validate_phase3_retry_v2_universe_size(cases)
            self.assertFalse(ok)
            self.assertIn(runner.PHASE3_RETRY_V2_UNIVERSE_SIZE_VIOLATION, err)
        finally:
            os.unlink(tmp_path)

    def test_only_b3r2_001_through_b3r2_091_allowed(self) -> None:
        cases = runner.load_phase3_retry_v2_universe(UNIVERSE)
        retry_v2_ids = {c.retry_v2_case_id for c in cases}
        self.assertEqual(retry_v2_ids, runner.ALLOWED_RETRY_V2_CASE_IDS)
        bad = runner.Phase3RetryV2UniverseCase(
            retry_v2_case_id="B3R2_999",
            original_case_id="B3E001",
            company_code="600010",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            original_phase3_status="network_error",
            failed_retry_status="network_error",
            final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
            persistent_failure_stage="EP002_topSearch_orgId",
            schema_impact="none",
            quality_impact="unresolved_network_caveat",
            ep002_precheck_signal="no_precheck_sample",
            retry_v2_include="yes",
            retry_v2_reason="x",
            risk_note="x",
            notes="x",
        )
        issues = runner.validate_phase3_retry_v2_case(bad)
        self.assertIn(f"{runner.RETRY_V2_CASE_ID_NOT_ALLOWED}:B3R2_999", issues)

    def test_retry_v2_include_must_be_yes_for_all_rows(self) -> None:
        cases = runner.load_phase3_retry_v2_universe(UNIVERSE)
        self.assertTrue(all(c.retry_v2_include == "yes" for c in cases))
        bad = runner.Phase3RetryV2UniverseCase(
            retry_v2_case_id="B3R2_001",
            original_case_id="B3E001",
            company_code="600010",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            original_phase3_status="network_error",
            failed_retry_status="network_error",
            final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
            persistent_failure_stage="EP002_topSearch_orgId",
            schema_impact="none",
            quality_impact="unresolved_network_caveat",
            ep002_precheck_signal="no_precheck_sample",
            retry_v2_include="no",
            retry_v2_reason="x",
            risk_note="x",
            notes="x",
        )
        issues = runner.validate_phase3_retry_v2_case(bad)
        self.assertIn(runner.RETRY_V2_INCLUDE_REQUIRED, issues)

    def test_final_effective_status_must_be_unresolved(self) -> None:
        case = runner.Phase3RetryV2UniverseCase(
            retry_v2_case_id="B3R2_001",
            original_case_id="B3E001",
            company_code="600010",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            original_phase3_status="network_error",
            failed_retry_status="network_error",
            final_effective_status_before_retry_v2="accepted",
            persistent_failure_stage="EP002_topSearch_orgId",
            schema_impact="none",
            quality_impact="unresolved_network_caveat",
            ep002_precheck_signal="no_precheck_sample",
            retry_v2_include="yes",
            retry_v2_reason="x",
            risk_note="x",
            notes="x",
        )
        issues = runner.validate_phase3_retry_v2_case(case)
        self.assertIn(runner.RETRY_V2_FINAL_STATUS_INVALID, issues)

    def test_persistent_failure_stage_must_be_ep002(self) -> None:
        case = runner.Phase3RetryV2UniverseCase(
            retry_v2_case_id="B3R2_001",
            original_case_id="B3E001",
            company_code="600010",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            original_phase3_status="network_error",
            failed_retry_status="network_error",
            final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
            persistent_failure_stage="EP001_query",
            schema_impact="none",
            quality_impact="unresolved_network_caveat",
            ep002_precheck_signal="no_precheck_sample",
            retry_v2_include="yes",
            retry_v2_reason="x",
            risk_note="x",
            notes="x",
        )
        issues = runner.validate_phase3_retry_v2_case(case)
        self.assertIn(runner.RETRY_V2_FAILURE_STAGE_INVALID, issues)

    def test_b3e087_rejected(self) -> None:
        case = runner.Phase3RetryV2UniverseCase(
            retry_v2_case_id="B3R2_001",
            original_case_id=runner.PHASE3_SUCCESS_HOLD_CASE_ID,
            company_code="000786",
            company_name="北新建材",
            market="SZSE主板",
            announcement_type="general_announcement",
            target_endpoint=["EP001", "EP005"],
            original_phase3_status="found",
            failed_retry_status="",
            final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
            persistent_failure_stage="EP002_topSearch_orgId",
            schema_impact="none",
            quality_impact="unresolved_network_caveat",
            ep002_precheck_signal="no_precheck_sample",
            retry_v2_include="yes",
            retry_v2_reason="x",
            risk_note="x",
            notes="x",
        )
        issues = runner.validate_phase3_retry_v2_case(case)
        self.assertIn(runner.SUCCESSFUL_PHASE3_CASE_RETRY_REJECTED, issues)

    def test_recovered_cases_rejected(self) -> None:
        for case_id in runner.RECOVERED_PHASE3_CASE_IDS:
            case = runner.Phase3RetryV2UniverseCase(
                retry_v2_case_id="B3R2_001",
                original_case_id=case_id,
                company_code="600010",
                company_name="测试",
                market="SSE主板",
                announcement_type="periodic_report",
                target_endpoint=["EP001", "EP004"],
                original_phase3_status="network_error",
                failed_retry_status="found",
                final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
                persistent_failure_stage="EP002_topSearch_orgId",
                schema_impact="none",
                quality_impact="unresolved_network_caveat",
                ep002_precheck_signal="no_precheck_sample",
                retry_v2_include="yes",
                retry_v2_reason="x",
                risk_note="x",
                notes="x",
            )
            issues = runner.validate_phase3_retry_v2_case(case)
            self.assertIn(
                f"{runner.RECOVERED_CASE_IN_RETRY_V2_FORBIDDEN}:{case_id}",
                issues,
                msg=case_id,
            )

    def test_prior_phase_cases_rejected_if_detectable(self) -> None:
        for case_id in ("B1E001", "B2E001", "B25E003"):
            case = runner.Phase3RetryV2UniverseCase(
                retry_v2_case_id="B3R2_001",
                original_case_id=case_id,
                company_code="600010",
                company_name="测试",
                market="SSE主板",
                announcement_type="periodic_report",
                target_endpoint=["EP001", "EP004"],
                original_phase3_status="network_error",
                failed_retry_status="network_error",
                final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
                persistent_failure_stage="EP002_topSearch_orgId",
                schema_impact="none",
                quality_impact="unresolved_network_caveat",
                ep002_precheck_signal="no_precheck_sample",
                retry_v2_include="yes",
                retry_v2_reason="x",
                risk_note="x",
                notes="x",
            )
            issues = runner.validate_phase3_retry_v2_case(case)
            self.assertIn(runner.PRIOR_PHASE_CASE_ID_REJECTED, issues, msg=case_id)

    def test_replacement_cases_rejected(self) -> None:
        case = runner.Phase3RetryV2UniverseCase(
            retry_v2_case_id="B3R2_001",
            original_case_id="B3E999",
            company_code="600010",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            original_phase3_status="network_error",
            failed_retry_status="network_error",
            final_effective_status_before_retry_v2="unresolved_ep002_orgid_network_failure",
            persistent_failure_stage="EP002_topSearch_orgId",
            schema_impact="none",
            quality_impact="unresolved_network_caveat",
            ep002_precheck_signal="no_precheck_sample",
            retry_v2_include="yes",
            retry_v2_reason="x",
            risk_note="x",
            notes="x",
        )
        issues = runner.validate_phase3_retry_v2_case(case)
        self.assertIn(f"{runner.NON_RETRY_V2_ORIGINAL_CASE_REJECTED}:B3E999", issues)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(RETRY_V2_BASE_ARGS + ["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.PHASE3_RETRY_V2_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_original_phase3_reports_write_blocked(self) -> None:
        ok, err = runner.validate_phase3_retry_v2_output_root(PHASE3_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.PHASE3_EXPANSION_BASELINE_WRITE_FORBIDDEN)

    def test_failed_retry_reports_write_blocked(self) -> None:
        ok, err = runner.validate_phase3_retry_v2_output_root(PHASE3_RETRY_OUTPUT_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.PHASE3_FAILED_RETRY_BASELINE_WRITE_FORBIDDEN)

    def test_ep002_precheck_reports_write_blocked(self) -> None:
        ok, err = runner.validate_phase3_retry_v2_output_root(EP002_PRECHECK_ROOT)
        self.assertFalse(ok)
        self.assertEqual(err, runner.EP002_PRECHECK_BASELINE_WRITE_FORBIDDEN)

    def test_phase25_reports_write_blocked(self) -> None:
        for bad_root, err in (
            (PHASE25_OUTPUT_ROOT, runner.PHASE25_BASELINE_WRITE_FORBIDDEN),
            (PHASE25_RETRY_OUTPUT_ROOT, runner.RETRY_BASELINE_WRITE_FORBIDDEN),
        ):
            ok, root_err = runner.validate_phase3_retry_v2_output_root(bad_root)
            self.assertFalse(ok, msg=bad_root)
            self.assertEqual(root_err, err, msg=bad_root)

    def test_live_mode_requires_retry_v2_approval_flag(self) -> None:
        with mock.patch("requests.post") as post_mock:
            result = _run(RETRY_V2_BASE_ARGS + ["--live"])
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_RETRY_V2_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        wrong_flags = (
            "--approve-b-class-phase25-expansion",
            "--approve-b-class-phase25-failed-retry",
            "--approve-b-class-phase3-100-expansion",
            "--approve-b-class-phase3-100-failed-retry",
            "--approve-b-class-phase3-100-ep002-reachability-precheck",
        )
        for flag in wrong_flags:
            with mock.patch("requests.post") as post_mock:
                result = _run(RETRY_V2_BASE_ARGS + ["--live", flag])
                post_mock.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_pdf_download_blocked(self) -> None:
        result = _run(RETRY_V2_BASE_ARGS + ["--dry-run", "--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(RETRY_V2_BASE_ARGS + ["--dry-run", "--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--run-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--extract-sections", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(RETRY_V2_BASE_ARGS + ["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, err in (
            ("--write-db", runner.DB_WRITE_REQUESTED_NOT_ALLOWED),
            ("--write-minio", runner.MINIO_WRITE_REQUESTED_NOT_ALLOWED),
            ("--run-rag", runner.RAG_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(RETRY_V2_BASE_ARGS + ["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, err in (
            ("--mark-verified", runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
            ("--mark-production-ready", runner.PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(RETRY_V2_BASE_ARGS + ["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_dry_run_report_generated(self) -> None:
        result = _run(RETRY_V2_BASE_ARGS + ["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), runner.REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE)
        self.assertEqual(set(rows[0].keys()), set(runner.PHASE3_RETRY_V2_DRYRUN_REPORT_COLUMNS))
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
        for row in rows:
            self.assertEqual(row["cninfo_call_planned"], "0")
            self.assertEqual(row["pdf_download"], "0")
            self.assertEqual(row["pdf_parse"], "0")
            self.assertEqual(row["ocr"], "0")
            self.assertEqual(row["extraction"], "0")
            self.assertEqual(row["db_write"], "0")
            self.assertEqual(row["minio_write"], "0")
            self.assertEqual(row["rag_run"], "0")

    def test_dry_run_summary_generated(self) -> None:
        result = _run(RETRY_V2_BASE_ARGS + ["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("phase3_retry_v2_dry_run", content)
        self.assertIn("CNINFO calls (dry-run) | **0**", content)
        self.assertIn("READY_FOR_APPROVAL", content)

    def test_retry_v2_universe_csv_not_mutated(self) -> None:
        before = _file_sha256(UNIVERSE)
        result = _run(RETRY_V2_BASE_ARGS + ["--dry-run"])
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        after = _file_sha256(UNIVERSE)
        self.assertEqual(before, after)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
