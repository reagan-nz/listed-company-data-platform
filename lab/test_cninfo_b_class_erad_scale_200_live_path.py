"""
B-class Era D ~200 live path 测试（mock CNINFO · 不执行真实 live）。

运行：
    python lab/test_cninfo_b_class_erad_scale_200_live_path.py
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, List
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_b_class_phase25_expansion_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_b_class_phase25_expansion_validation.py")
UNIVERSE = runner.DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
MOCK_LIVE_PARENT = runner.ERAD_SCALE_200_MOCK_LIVE_TEST_PARENT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
PHASE3_RETRY_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_OUTPUT_ROOT
PHASE3_RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT
A_CLASS_ROOT = runner.A_CLASS_VALIDATION_ROOT
C_CLASS_HARVEST_ROOT = runner.C_CLASS_HARVEST_ROOT
D_CLASS_ROOT = runner.D_CLASS_VALIDATION_ROOT
LIVE_REPORT = runner.ERAD_SCALE_200_LIVE_REPORT_CSV
LIVE_SUMMARY = runner.ERAD_SCALE_200_LIVE_SUMMARY_MD
QUALITY_REPORT = runner.ERAD_SCALE_200_QUALITY_REPORT_CSV
DRYRUN_REPORT = runner.ERAD_SCALE_200_DRYRUN_REPORT_CSV

LIVE_ARGS = [
    "--erad-b-scale-200",
    "--live",
    "--universe-csv",
    UNIVERSE,
    "--output-root",
    OUTPUT_ROOT,
    "--approve-b-class-erad-scale-200",
]

DRYRUN_ARGS = [
    "--erad-b-scale-200",
    "--dry-run",
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


def _mock_execute_live_case(
    tl_case: Any,
    _categories_config: Dict[str, Any],
    stats: Any,
) -> Dict[str, Any]:
    stats.cninfo_requests += 2
    return {
        "case_id": tl_case.case_id,
        "company_code": tl_case.company_code,
        "retrieval_status": "found",
        "quality_status": "pass",
        "lineage_status": "discovered",
        "announcement_id": "ann-001",
        "announcement_title": "测试公告",
        "announcement_time": "2024-01-01 00:00:00",
        "pdf_url": "http://example.com/a.pdf",
        "adjunct_url": "",
        "endpoint_id": "EP004",
        "_case_cninfo_requests": 2,
        "notes": "mock",
    }


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


def _live_args_for_output_root(output_root: str) -> List[str]:
    return [
        "--erad-b-scale-200",
        "--live",
        "--universe-csv",
        UNIVERSE,
        "--output-root",
        output_root,
        "--approve-b-class-erad-scale-200",
    ]


def _create_mock_live_output_root() -> str:
    os.makedirs(MOCK_LIVE_PARENT, exist_ok=True)
    return tempfile.mkdtemp(prefix="run_", dir=MOCK_LIVE_PARENT)


def _cleanup_mock_live_output_root(temp_root: str) -> None:
    runner.safe_cleanup_erad_test_output_root(temp_root)


def _count_files_under(root: str) -> int:
    if not os.path.isdir(root):
        return 0
    total = 0
    for _dirpath, _dirnames, filenames in os.walk(root):
        total += len(filenames)
    return total


class TestEradScale200LivePath(unittest.TestCase):
    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_b_class_tiny_live_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--erad-b-scale-200",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_SCALE_200_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_b_class_tiny_live_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--erad-b-scale-200",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    OUTPUT_ROOT,
                    "--approve-b-class-phase3-100-expansion",
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)

    def test_live_path_function_exists_and_wired(self) -> None:
        self.assertTrue(hasattr(runner, "process_erad_scale_200_live"))
        self.assertTrue(callable(runner.process_erad_scale_200_live))
        self.assertTrue(hasattr(runner, "write_live_erad_scale_200_reports"))
        with mock.patch(
            "run_cninfo_b_class_tiny_live_validation.execute_live_case",
            side_effect=_mock_execute_live_case,
        ):
            tmp_root = _create_mock_live_output_root()
            try:
                rc = runner.main(_live_args_for_output_root(tmp_root))
            finally:
                _cleanup_mock_live_output_root(tmp_root)
        self.assertEqual(rc, 0)

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

    def test_output_root_isolation_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = _run(
                [
                    "--erad-b-scale-200",
                    "--live",
                    "--universe-csv",
                    UNIVERSE,
                    "--output-root",
                    tmp,
                    "--approve-b-class-erad-scale-200",
                ]
            )
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

    def test_request_cap_480_enforced(self) -> None:
        ok, _ = runner.enforce_erad_scale_200_request_cap(400)
        self.assertTrue(ok)
        ok, err = runner.enforce_erad_scale_200_request_cap(481)
        self.assertFalse(ok)
        self.assertIn(runner.ERAD_REQUEST_CAP_EXCEEDED, err)
        self.assertEqual(runner.MAX_ERAD_SCALE_200_CNINFO_REQUESTS, 480)

    def test_retained_cohort_does_not_write_phase3_production_root(self) -> None:
        phase3_before = _count_files_under(
            os.path.join(PHASE3_OUTPUT_ROOT, "raw_metadata")
        )
        tmp_root = _create_mock_live_output_root()
        try:
            with mock.patch(
                "run_cninfo_b_class_tiny_live_validation.execute_live_case",
                side_effect=_mock_execute_live_case,
            ):
                rc = runner.main(_live_args_for_output_root(tmp_root))
            self.assertEqual(rc, 0)
            report_path = os.path.join(
                tmp_root, "reports", "b_class_erad_scale_200_report.csv"
            )
            with open(report_path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            retained = [r for r in rows if r.get("cohort") == "retained_phase3"]
            self.assertEqual(len(retained), 100)
            self.assertTrue(
                all(r.get("retained_evidence_mode") == "live_refresh" for r in retained)
            )
            self.assertTrue(
                all(r.get("phase3_source_case_id", "").startswith("B3E") for r in retained)
            )
            snap = os.path.join(tmp_root, "raw_metadata", "BD2E001_EP004.json")
            self.assertTrue(os.path.isfile(snap))
            with open(snap, encoding="utf-8") as f:
                payload = json.load(f)
            self.assertFalse(payload.get("phase3_production_root_write"))
            self.assertEqual(payload.get("retained_evidence_mode"), "live_refresh")
        finally:
            _cleanup_mock_live_output_root(tmp_root)
        phase3_after = _count_files_under(
            os.path.join(PHASE3_OUTPUT_ROOT, "raw_metadata")
        )
        self.assertEqual(phase3_before, phase3_after)

    def test_pdf_ocr_extraction_blocked(self) -> None:
        for flag, err in (
            ("--download-pdf", runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
            ("--parse-pdf", runner.PDF_PARSE_REQUESTED_NOT_ALLOWED),
            ("--run-ocr", runner.OCR_REQUESTED_NOT_ALLOWED),
            ("--extract-sections", runner.EXTRACTION_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, err in (
            ("--write-db", runner.DB_WRITE_REQUESTED_NOT_ALLOWED),
            ("--write-minio", runner.MINIO_WRITE_REQUESTED_NOT_ALLOWED),
            ("--run-rag", runner.RAG_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, err in (
            ("--mark-verified", runner.VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
            ("--mark-production-ready", runner.PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
        ):
            result = _run(LIVE_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(err, result.stderr)

    def test_live_path_does_not_call_real_cninfo(self) -> None:
        tmp_root = _create_mock_live_output_root()
        try:
            with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
                with mock.patch(
                    "run_cninfo_b_class_tiny_live_validation.execute_live_case",
                    side_effect=_mock_execute_live_case,
                ) as mock_exec:
                    rc = runner.main(_live_args_for_output_root(tmp_root))
            self.assertEqual(rc, 0)
            self.assertEqual(mock_exec.call_count, runner.REQUIRED_ERAD_SCALE_200_UNIVERSE_SIZE)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        finally:
            _cleanup_mock_live_output_root(tmp_root)

    def test_dry_run_still_200_of_200_and_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(DRYRUN_ARGS)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_ok=200", result.stdout)

    def test_cleanup_does_not_delete_phase3_or_erad_production_outputs(self) -> None:
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(PHASE3_OUTPUT_ROOT)
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(PHASE3_RETRY_V2_OUTPUT_ROOT)
        with self.assertRaises(RuntimeError):
            runner.safe_cleanup_erad_test_output_root(OUTPUT_ROOT)
        tmp_root = _create_mock_live_output_root()
        marker = os.path.join(tmp_root, "marker.txt")
        with open(marker, "w", encoding="utf-8") as f:
            f.write("ok")
        _cleanup_mock_live_output_root(tmp_root)
        self.assertFalse(os.path.isdir(tmp_root))

    def test_no_production_live_report_at_erad_root(self) -> None:
        self.assertFalse(os.path.isfile(LIVE_REPORT))
        self.assertFalse(os.path.isfile(LIVE_SUMMARY))
        self.assertFalse(os.path.isfile(QUALITY_REPORT))
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    summary_path = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_b_class_erad_scale_200_live_path_test_summary.md",
    )
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(
            "# B-class Era D ~200 Live Path Test Summary\n\n"
            f"- tests_run: {result.testsRun}\n"
            f"- passed: {passed}\n"
            f"- failed: {len(result.failures)}\n"
            f"- errors: {len(result.errors)}\n"
            f"- CNINFO calls: **0** (mock only)\n"
            f"- gate: **READY_FOR_APPROVAL** (live path offline prep)\n"
            f"- approval_status: **NOT_APPROVED**\n"
            f"- production live report at erad root: **no**\n"
        )
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
