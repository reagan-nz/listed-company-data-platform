"""
B-class Phase 3 EP002 reachability precheck runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_b_class_phase3_100_ep002_reachability_precheck_runner.py
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

import run_cninfo_b_class_phase3_100_ep002_reachability_precheck as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py"
)
CANDIDATES_CSV = runner.DEFAULT_PRECHECK_CANDIDATES_CSV
OUTPUT_ROOT = runner.DEFAULT_PRECHECK_OUTPUT_ROOT
DRYRUN_REPORT = os.path.join(OUTPUT_ROOT, "reports", runner.DRYRUN_REPORT_NAME)
DRYRUN_SUMMARY = os.path.join(OUTPUT_ROOT, "reports", runner.DRYRUN_SUMMARY_NAME)
PHASE3_EXPANSION_ROOT = runner.PHASE3_EXPANSION_ROOT
PHASE3_FAILED_RETRY_ROOT = runner.PHASE3_FAILED_RETRY_ROOT
PHASE25_EXPANSION_ROOT = runner.PHASE25_EXPANSION_ROOT
PHASE25_FAILED_RETRY_ROOT = runner.PHASE25_FAILED_RETRY_ROOT
RETRY_V2_UNIVERSE_CSV = runner.RETRY_V2_UNIVERSE_CSV

DRYRUN_ARGS = [
    "--dry-run",
    "--candidates-csv",
    CANDIDATES_CSV,
    "--output-root",
    OUTPUT_ROOT,
]

CANDIDATE_FIELDNAMES = [
    "precheck_id",
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "persistent_failure_stage",
    "original_phase3_status",
    "failed_retry_status",
    "precheck_include",
    "precheck_reason",
    "planned_check_type",
    "notes",
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


def _sample_candidate_row(
  precheck_id: str = "B3EP001",
  case_id: str = "B3E001",
) -> dict:
    return {
        "precheck_id": precheck_id,
        "case_id": case_id,
        "company_code": "600010",
        "company_name": "测试",
        "market": "SSE主板",
        "announcement_type": "periodic_report",
        "target_endpoint": "EP001;EP004",
        "persistent_failure_stage": "EP002_topSearch_orgId",
        "original_phase3_status": "network_error",
        "failed_retry_status": "network_error",
        "precheck_include": "yes",
        "precheck_reason": "x",
        "planned_check_type": "ep002_orgid_reachability",
        "notes": "x",
    }


class TestBClassPhase3Ep002ReachabilityPrecheckRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(DRYRUN_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_candidates_csv_is_required(self) -> None:
        result = _run(["--dry-run", "--output-root", OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.CANDIDATES_CSV_REQUIRED, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        for bad_root, err in (
            (PHASE3_EXPANSION_ROOT, runner.PHASE3_EXPANSION_WRITE_FORBIDDEN),
            (PHASE3_FAILED_RETRY_ROOT, runner.PHASE3_FAILED_RETRY_WRITE_FORBIDDEN),
            (PHASE25_EXPANSION_ROOT, runner.PHASE25_EXPANSION_WRITE_FORBIDDEN),
            (PHASE25_FAILED_RETRY_ROOT, runner.PHASE25_FAILED_RETRY_WRITE_FORBIDDEN),
        ):
            result = _run(
                [
                    "--dry-run",
                    "--candidates-csv",
                    CANDIDATES_CSV,
                    "--output-root",
                    bad_root,
                ]
            )
            self.assertNotEqual(result.returncode, 0, msg=bad_root)
            self.assertIn(err, result.stderr, msg=bad_root)

    def test_candidate_count_must_equal_8(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(tmp, fieldnames=CANDIDATE_FIELDNAMES)
            writer.writeheader()
            writer.writerow(_sample_candidate_row())
            tmp_path = tmp.name
        try:
            result = _run(
                [
                    "--dry-run",
                    "--candidates-csv",
                    tmp_path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.PRECHECK_CANDIDATE_COUNT_VIOLATION, result.stderr)
        finally:
            os.unlink(tmp_path)

    def test_only_b3ep001_b3ep008_allowed(self) -> None:
        candidates = runner.load_precheck_candidates(CANDIDATES_CSV)
        precheck_ids = {c.precheck_id for c in candidates}
        self.assertEqual(precheck_ids, runner.ALLOWED_PRECHECK_IDS)
        bad = runner.PrecheckCandidate(
            precheck_id="B3EP999",
            case_id="B3E001",
            company_code="600010",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint="EP001;EP004",
            persistent_failure_stage="EP002_topSearch_orgId",
            original_phase3_status="network_error",
            failed_retry_status="network_error",
            precheck_include="yes",
            precheck_reason="x",
            planned_check_type="ep002_orgid_reachability",
            notes="x",
        )
        issues = runner.validate_precheck_candidate(bad)
        self.assertIn(
            f"{runner.PRECHECK_ID_NOT_ALLOWED}:B3EP999",
            issues,
        )

    def test_only_selected_case_ids_allowed(self) -> None:
        candidates = runner.load_precheck_candidates(CANDIDATES_CSV)
        case_ids = {c.case_id for c in candidates}
        self.assertEqual(case_ids, runner.ALLOWED_CASE_IDS)

    def test_b3e087_rejected(self) -> None:
        candidate = runner.PrecheckCandidate(
            precheck_id="B3EP001",
            case_id="B3E087",
            company_code="000786",
            company_name="测试",
            market="SZSE主板",
            announcement_type="general_announcement",
            target_endpoint="EP001;EP005",
            persistent_failure_stage="EP002_topSearch_orgId",
            original_phase3_status="network_error",
            failed_retry_status="network_error",
            precheck_include="yes",
            precheck_reason="x",
            planned_check_type="ep002_orgid_reachability",
            notes="x",
        )
        issues = runner.validate_precheck_candidate(candidate)
        self.assertIn(
            f"{runner.HOLD_CASE_IN_PRECHECK_FORBIDDEN}:B3E087",
            issues,
        )

    def test_recovered_cases_rejected(self) -> None:
        for case_id in runner.RECOVERED_CASE_IDS:
            candidate = runner.PrecheckCandidate(
                precheck_id="B3EP001",
                case_id=case_id,
                company_code="600010",
                company_name="测试",
                market="SSE主板",
                announcement_type="periodic_report",
                target_endpoint="EP001;EP004",
                persistent_failure_stage="EP002_topSearch_orgId",
                original_phase3_status="network_error",
                failed_retry_status="network_error",
                precheck_include="yes",
                precheck_reason="x",
                planned_check_type="ep002_orgid_reachability",
                notes="x",
            )
            issues = runner.validate_precheck_candidate(candidate)
            self.assertIn(
                f"{runner.RECOVERED_CASE_IN_PRECHECK_FORBIDDEN}:{case_id}",
                issues,
                msg=case_id,
            )

    def test_prior_phase_cases_rejected_if_detectable(self) -> None:
        for case_id in ("B1E001", "B2E001", "B25E003"):
            candidate = runner.PrecheckCandidate(
                precheck_id="B3EP001",
                case_id=case_id,
                company_code="600010",
                company_name="测试",
                market="SSE主板",
                announcement_type="periodic_report",
                target_endpoint="EP001;EP004",
                persistent_failure_stage="EP002_topSearch_orgId",
                original_phase3_status="network_error",
                failed_retry_status="network_error",
                precheck_include="yes",
                precheck_reason="x",
                planned_check_type="ep002_orgid_reachability",
                notes="x",
            )
            issues = runner.validate_precheck_candidate(candidate)
            self.assertIn(
                f"{runner.PRIOR_PHASE_CASE_IN_PRECHECK_FORBIDDEN}:{case_id}",
                issues,
                msg=case_id,
            )

    def test_request_cap_enforced(self) -> None:
        ok, err = runner.validate_request_cap(8, 16)
        self.assertTrue(ok, msg=err)
        ok, err = runner.validate_request_cap(17, 16)
        self.assertFalse(ok)
        self.assertIn(runner.PRECHECK_REQUEST_CAP_EXCEEDED, err)
        result = _run(DRYRUN_ARGS + ["--request-cap", "7"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PRECHECK_REQUEST_CAP_EXCEEDED, result.stderr)

    def test_planned_check_type_must_be_ep002_orgid_reachability(self) -> None:
        candidate = runner.PrecheckCandidate(
            precheck_id="B3EP001",
            case_id="B3E001",
            company_code="600010",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint="EP001;EP004",
            persistent_failure_stage="EP002_topSearch_orgId",
            original_phase3_status="network_error",
            failed_retry_status="network_error",
            precheck_include="yes",
            precheck_reason="x",
            planned_check_type="announcement_query",
            notes="x",
        )
        issues = runner.validate_precheck_candidate(candidate)
        self.assertIn(
            f"{runner.PRECHECK_CHECK_TYPE_UNSUPPORTED}:announcement_query",
            issues,
        )

    def test_live_mode_requires_precheck_approval_flag(self) -> None:
        with mock.patch("requests.post") as post_mock:
            result = _run(
                [
                    "--live",
                    "--candidates-csv",
                    CANDIDATES_CSV,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PRECHECK_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        wrong_flags = (
            "--approve-b-class-phase3-100-expansion",
            "--approve-b-class-phase3-100-failed-retry",
            "--approve-b-class-phase25-expansion",
            "--approve-b-class-phase25-failed-retry",
            "--approve-b-class-tiny-live-validation",
        )
        for flag in wrong_flags:
            with mock.patch("requests.post") as post_mock:
                result = _run(
                    [
                        "--live",
                        "--candidates-csv",
                        CANDIDATES_CSV,
                        "--output-root",
                        OUTPUT_ROOT,
                        flag,
                    ]
                )
                post_mock.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(runner.PRECHECK_WRONG_APPROVAL, result.stderr, msg=flag)

    def test_original_phase3_reports_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--candidates-csv",
                CANDIDATES_CSV,
                "--output-root",
                PHASE3_EXPANSION_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_EXPANSION_WRITE_FORBIDDEN, result.stderr)

    def test_failed_retry_reports_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--candidates-csv",
                CANDIDATES_CSV,
                "--output-root",
                PHASE3_FAILED_RETRY_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_FAILED_RETRY_WRITE_FORBIDDEN, result.stderr)

    def test_phase25_reports_write_blocked(self) -> None:
        for bad_root, err in (
            (PHASE25_EXPANSION_ROOT, runner.PHASE25_EXPANSION_WRITE_FORBIDDEN),
            (PHASE25_FAILED_RETRY_ROOT, runner.PHASE25_FAILED_RETRY_WRITE_FORBIDDEN),
        ):
            result = _run(
                [
                    "--dry-run",
                    "--candidates-csv",
                    CANDIDATES_CSV,
                    "--output-root",
                    bad_root,
                ]
            )
            self.assertNotEqual(result.returncode, 0, msg=bad_root)
            self.assertIn(err, result.stderr, msg=bad_root)

    def test_retry_v2_universe_not_created(self) -> None:
        before_exists = os.path.isfile(RETRY_V2_UNIVERSE_CSV)
        result = _run(DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertFalse(os.path.isfile(RETRY_V2_UNIVERSE_CSV) and not before_exists)

    def test_ep001_ep004_ep005_validation_blocked(self) -> None:
        for flag, err in (
            ("--run-ep001-validation", runner.EP001_VALIDATION_REQUESTED_NOT_ALLOWED),
            ("--run-ep004-validation", runner.EP004_VALIDATION_REQUESTED_NOT_ALLOWED),
            ("--run-ep005-validation", runner.EP005_VALIDATION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_pdf_download_blocked(self) -> None:
        result = _run(DRYRUN_ARGS + ["--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(DRYRUN_ARGS + ["--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--enable-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--enable-extraction", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, err in (
            ("--write-db", runner.DB_WRITE_REQUESTED_NOT_ALLOWED),
            ("--write-minio", runner.MINIO_WRITE_REQUESTED_NOT_ALLOWED),
            ("--run-rag", runner.RAG_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, err in (
            ("--mark-verified", runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
            ("--mark-production-ready", runner.PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_dry_run_report_generated(self) -> None:
        result = _run(DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), runner.REQUIRED_CANDIDATE_COUNT)
        self.assertEqual(set(rows[0].keys()), set(runner.DRYRUN_COLUMNS))
        for row in rows:
            self.assertEqual(row["dryrun_status"], "planned_ok")
            self.assertEqual(row["cninfo_call_planned"], "0")

    def test_dry_run_summary_generated(self) -> None:
        result = _run(DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("precheck_dry_run", content)
        self.assertIn("CNINFO calls | **0**", content)
        self.assertIn("READY_FOR_APPROVAL", content)

    def test_candidates_csv_not_mutated(self) -> None:
        before = _file_sha256(CANDIDATES_CSV)
        result = _run(DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        after = _file_sha256(CANDIDATES_CSV)
        self.assertEqual(before, after)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
