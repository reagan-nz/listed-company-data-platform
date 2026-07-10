"""
B-class Era D ~200 runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_b_class_erad_scale_200_runner.py
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
UNIVERSE = runner.DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
PHASE3_RETRY_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_OUTPUT_ROOT
PHASE3_RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT
A_CLASS_ROOT = runner.A_CLASS_VALIDATION_ROOT
C_CLASS_HARVEST_ROOT = runner.C_CLASS_HARVEST_ROOT
D_CLASS_ROOT = runner.D_CLASS_VALIDATION_ROOT
DRYRUN_REPORT = runner.ERAD_SCALE_200_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.ERAD_SCALE_200_DRYRUN_SUMMARY_MD
MOCK_TEST_PARENT = runner.ERAD_SCALE_200_MOCK_TEST_PARENT

ERAD_HEADER = (
    "case_id,company_code,company_name,market,announcement_type,target_endpoint,"
    "cohort,phase3_source_case_id,erad_include,phase1_overlap,phase2_overlap,"
    "phase25_overlap,phase3_overlap,prior_b_phase_overlap,selection_bucket,"
    "expected_behavior,notes\n"
)

ERAD_BASE_ARGS = [
    "--erad-b-scale-200",
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


def _sample_erad_row(case_id: str = "BD2E001") -> dict:
    cohort = "retained_phase3" if case_id <= "BD2E100" else "new_expansion"
    phase3_src = f"B3E{int(case_id.replace('BD2E', '')):03d}" if cohort == "retained_phase3" else ""
    return {
        "case_id": case_id,
        "company_code": "600010",
        "company_name": "测试",
        "market": "SSE主板",
        "announcement_type": "periodic_report",
        "target_endpoint": "EP001;EP004",
        "cohort": cohort,
        "phase3_source_case_id": phase3_src,
        "erad_include": "yes",
        "phase1_overlap": "no",
        "phase2_overlap": "no",
        "phase25_overlap": "no",
        "phase3_overlap": "yes" if cohort == "retained_phase3" else "no",
        "prior_b_phase_overlap": "yes" if cohort == "retained_phase3" else "no",
        "selection_bucket": "test",
        "expected_behavior": "x",
        "notes": "x",
    }


class TestEradScale200Runner(unittest.TestCase):
    def test_dry_run_200_planned_ok_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(ERAD_BASE_ARGS + ["--dry-run"])
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_ok=200", result.stdout)

    def test_universe_must_equal_200(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(
                tmp,
                fieldnames=list(_sample_erad_row().keys()),
            )
            writer.writeheader()
            writer.writerow(_sample_erad_row())
            tmp_path = tmp.name
        try:
            cases = runner.load_erad_scale_200_universe(tmp_path)
            ok, err = runner.validate_erad_scale_200_universe_size(cases)
            self.assertFalse(ok)
            self.assertIn(runner.ERAD_SCALE_200_UNIVERSE_SIZE_VIOLATION, err)
        finally:
            os.unlink(tmp_path)

    def test_only_bd2e001_through_bd2e200_allowed(self) -> None:
        cases = runner.load_erad_scale_200_universe(UNIVERSE)
        case_ids = {c.case_id for c in cases}
        self.assertEqual(case_ids, runner.ALLOWED_ERAD_SCALE_200_CASE_IDS)
        bad = runner.EraDScale200UniverseCase(
            case_id="BD2E999",
            company_code="600010",
            company_name="测试",
            market="SSE主板",
            announcement_type="periodic_report",
            target_endpoint=["EP001", "EP004"],
            cohort="new_expansion",
            phase3_source_case_id="",
            erad_include="yes",
            phase1_overlap="no",
            phase2_overlap="no",
            phase25_overlap="no",
            phase3_overlap="no",
            prior_b_phase_overlap="no",
            selection_bucket="x",
            expected_behavior="x",
            notes="x",
        )
        issues = runner.validate_erad_scale_200_case(bad)
        self.assertIn(f"{runner.ERAD_CASE_ID_NOT_ALLOWED}:BD2E999", issues)

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(ERAD_BASE_ARGS + ["--dry-run", "--output-root", tmp])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.ERAD_SCALE_200_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_phase3_production_roots_write_blocked(self) -> None:
        for bad_root, err in (
            (PHASE3_OUTPUT_ROOT, runner.PHASE3_EXPANSION_BASELINE_WRITE_FORBIDDEN),
            (PHASE3_RETRY_OUTPUT_ROOT, runner.PHASE3_FAILED_RETRY_BASELINE_WRITE_FORBIDDEN),
            (
                PHASE3_RETRY_V2_OUTPUT_ROOT,
                runner.PHASE3_RETRY_V2_OUTPUT_ROOT_VIOLATION,
            ),
        ):
            ok, root_err = runner.validate_erad_scale_200_output_root(bad_root)
            self.assertFalse(ok, msg=bad_root)
            self.assertEqual(root_err, err, msg=bad_root)

    def test_acd_roots_write_blocked(self) -> None:
        for bad_root, err in (
            (A_CLASS_ROOT, runner.ERAD_A_CLASS_ROOT_WRITE_FORBIDDEN),
            (C_CLASS_HARVEST_ROOT, runner.ERAD_C_CLASS_HARVEST_ROOT_WRITE_FORBIDDEN),
            (D_CLASS_ROOT, runner.ERAD_D_CLASS_ROOT_WRITE_FORBIDDEN),
        ):
            ok, root_err = runner.validate_erad_scale_200_output_root(bad_root)
            self.assertFalse(ok, msg=bad_root)
            self.assertEqual(root_err, err, msg=bad_root)

    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.post") as post_mock:
            result = _run(ERAD_BASE_ARGS + ["--live"])
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_SCALE_200_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        wrong_flags = (
            "--approve-b-class-phase25-expansion",
            "--approve-b-class-phase25-failed-retry",
            "--approve-b-class-phase3-100-expansion",
            "--approve-b-class-phase3-100-failed-retry",
            "--approve-b-class-phase3-100-retry-v2",
            "--approve-b-class-phase3-100-ep002-reachability-precheck",
        )
        for flag in wrong_flags:
            with mock.patch("requests.post") as post_mock:
                result = _run(ERAD_BASE_ARGS + ["--live", flag])
                post_mock.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_request_cap_480_enforced_in_guards(self) -> None:
        ok, _ = runner.enforce_erad_scale_200_request_cap(400)
        self.assertTrue(ok)
        ok, err = runner.enforce_erad_scale_200_request_cap(481)
        self.assertFalse(ok)
        self.assertIn(runner.ERAD_REQUEST_CAP_EXCEEDED, err)
        cases = runner.load_erad_scale_200_universe(UNIVERSE)
        included = [c for c in cases if c.erad_include == "yes"]
        with tempfile.TemporaryDirectory() as tmp:
            output_paths = runner.ensure_output_layout(
                os.path.join(tmp, "erad_mock")
            )
            rows, issues = runner.process_erad_scale_200_dry_run(included, output_paths)
        total = sum(int(r.get("planned_request_count", "0")) for r in rows)
        self.assertLessEqual(total, runner.MAX_ERAD_SCALE_200_PLANNED_REQUESTS)
        gate = runner.compute_erad_scale_200_runner_gate(issues, len(included), total)
        self.assertEqual(gate, "READY_FOR_APPROVAL")

    def test_pdf_download_blocked(self) -> None:
        result = _run(ERAD_BASE_ARGS + ["--dry-run", "--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(ERAD_BASE_ARGS + ["--dry-run", "--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--run-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--extract-sections", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(ERAD_BASE_ARGS + ["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, err in (
            ("--write-db", runner.DB_WRITE_REQUESTED_NOT_ALLOWED),
            ("--write-minio", runner.MINIO_WRITE_REQUESTED_NOT_ALLOWED),
            ("--run-rag", runner.RAG_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(ERAD_BASE_ARGS + ["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, err in (
            ("--mark-verified", runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
            ("--mark-production-ready", runner.PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(ERAD_BASE_ARGS + ["--dry-run", flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_cleanup_does_not_delete_phase3_or_erad_production_sidecars(self) -> None:
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(PHASE3_OUTPUT_ROOT)
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(PHASE3_RETRY_V2_OUTPUT_ROOT)
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(OUTPUT_ROOT)
        os.makedirs(MOCK_TEST_PARENT, exist_ok=True)
        tmp_root = tempfile.mkdtemp(prefix="run_", dir=MOCK_TEST_PARENT)
        marker = os.path.join(tmp_root, "marker.txt")
        with open(marker, "w", encoding="utf-8") as f:
            f.write("ok")
        runner.safe_cleanup_erad_test_output_root(tmp_root)
        self.assertFalse(os.path.isdir(tmp_root))


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
