"""
A-class Phase 2 CNINFO reachability precheck runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_a_class_phase2_cninfo_reachability_precheck_runner.py
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

import run_cninfo_a_class_phase2_cninfo_reachability_precheck as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_a_class_phase2_cninfo_reachability_precheck.py")
CANDIDATES_CSV = runner.DEFAULT_PRECHECK_CANDIDATES_CSV
OUTPUT_ROOT = runner.DEFAULT_PRECHECK_OUTPUT_ROOT
DRYRUN_REPORT = os.path.join(
    OUTPUT_ROOT, "reports", runner.DRYRUN_REPORT_NAME
)
DRYRUN_SUMMARY = os.path.join(
    OUTPUT_ROOT, "reports", runner.DRYRUN_SUMMARY_NAME
)
EXPANSION_ROOT = runner.PHASE2_EXPANSION_ROOT
RETRY_V1_ROOT = runner.RETRY_V1_ROOT
RETRY_V2_ROOT = runner.RETRY_V2_ROOT
RETRY_V3_ROOT = runner.RETRY_V3_ROOT

DRYRUN_ARGS = [
    "--dry-run",
    "--candidates-csv",
    CANDIDATES_CSV,
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


class TestAClassPhase2CninfoReachabilityPrecheckRunner(unittest.TestCase):
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
            (EXPANSION_ROOT, runner.PHASE2_EXPANSION_WRITE_FORBIDDEN),
            (RETRY_V1_ROOT, runner.RETRY_V1_WRITE_FORBIDDEN),
            (RETRY_V2_ROOT, runner.RETRY_V2_WRITE_FORBIDDEN),
            (RETRY_V3_ROOT, runner.RETRY_V3_UNIVERSE_FORBIDDEN),
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

    def test_candidate_count_must_equal_3(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(
                tmp,
                fieldnames=[
                    "precheck_id",
                    "case_id",
                    "company_code",
                    "company_name",
                    "market",
                    "report_type",
                    "report_period",
                    "failure_pattern",
                    "precheck_include",
                    "precheck_reason",
                    "planned_check_type",
                    "notes",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "precheck_id": "APC001",
                    "case_id": "A2M005",
                    "company_code": "601012",
                    "company_name": "测试",
                    "market": "SSE",
                    "report_type": "annual_report",
                    "report_period": "2024-12-31",
                    "failure_pattern": "x",
                    "precheck_include": "yes",
                    "precheck_reason": "x",
                    "planned_check_type": "orgid_resolution_reachability",
                    "notes": "x",
                }
            )
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

    def test_only_apc001_apc002_apc003_allowed(self) -> None:
        candidates = runner.load_precheck_candidates(CANDIDATES_CSV)
        precheck_ids = {c.precheck_id for c in candidates}
        self.assertEqual(precheck_ids, runner.ALLOWED_PRECHECK_IDS)
        bad = runner.PrecheckCandidate(
            precheck_id="APC999",
            case_id="A2M005",
            company_code="601012",
            company_name="测试",
            market="SSE",
            report_type="annual_report",
            report_period="2024-12-31",
            failure_pattern="x",
            precheck_include="yes",
            precheck_reason="x",
            planned_check_type="orgid_resolution_reachability",
            notes="x",
        )
        issues = runner.validate_precheck_candidate(bad)
        self.assertIn(
            f"{runner.PRECHECK_ID_NOT_ALLOWED}:APC999",
            issues,
        )

    def test_only_a2m005_a2m010_a2m018_allowed(self) -> None:
        candidates = runner.load_precheck_candidates(CANDIDATES_CSV)
        case_ids = {c.case_id for c in candidates}
        self.assertEqual(case_ids, runner.ALLOWED_CASE_IDS)

    def test_successful_12_case_ids_rejected(self) -> None:
        for case_id in runner.SUCCESSFUL_CASE_IDS:
            candidate = runner.PrecheckCandidate(
                precheck_id="APC001",
                case_id=case_id,
                company_code="600036",
                company_name="测试",
                market="SSE",
                report_type="annual_report",
                report_period="2024-12-31",
                failure_pattern="x",
                precheck_include="yes",
                precheck_reason="x",
                planned_check_type="orgid_resolution_reachability",
                notes="x",
            )
            issues = runner.validate_precheck_candidate(candidate)
            self.assertIn(
                f"{runner.SUCCESSFUL_CASE_IN_PRECHECK_FORBIDDEN}:{case_id}",
                issues,
                msg=case_id,
            )

    def test_request_cap_enforced(self) -> None:
        ok, err = runner.validate_request_cap(3, 6)
        self.assertTrue(ok, msg=err)
        ok, err = runner.validate_request_cap(7, 6)
        self.assertFalse(ok)
        self.assertIn(runner.PRECHECK_REQUEST_CAP_EXCEEDED, err)
        result = _run(DRYRUN_ARGS + ["--request-cap", "2"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PRECHECK_REQUEST_CAP_EXCEEDED, result.stderr)

    def test_planned_check_type_must_be_orgid_resolution_reachability(self) -> None:
        candidate = runner.PrecheckCandidate(
            precheck_id="APC001",
            case_id="A2M005",
            company_code="601012",
            company_name="测试",
            market="SSE",
            report_type="annual_report",
            report_period="2024-12-31",
            failure_pattern="x",
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
            "--approve-a-class-phase2-metadata-expansion",
            "--approve-a-class-phase2-failed-retry",
            "--approve-a-class-phase2-network-recovery-retry-v2",
            "--approve-a-class-tiny-live-metadata",
            "--approve-full-harvest",
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

    def test_original_phase2_reports_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--candidates-csv",
                CANDIDATES_CSV,
                "--output-root",
                EXPANSION_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE2_EXPANSION_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v1_reports_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--candidates-csv",
                CANDIDATES_CSV,
                "--output-root",
                RETRY_V1_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V1_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v2_reports_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--candidates-csv",
                CANDIDATES_CSV,
                "--output-root",
                RETRY_V2_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.RETRY_V2_WRITE_FORBIDDEN, result.stderr)

    def test_retry_v3_universe_not_created(self) -> None:
        before_v3_exists = os.path.isdir(RETRY_V3_ROOT)
        result = _run(DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertFalse(os.path.isdir(RETRY_V3_ROOT) and not before_v3_exists)
        retry_v3_universe = os.path.join(
            BASE_DIR,
            "outputs",
            "validation",
            "cninfo_a_class_phase2_network_recovery_retry_v3_universe.csv",
        )
        self.assertFalse(os.path.isfile(retry_v3_universe))

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
