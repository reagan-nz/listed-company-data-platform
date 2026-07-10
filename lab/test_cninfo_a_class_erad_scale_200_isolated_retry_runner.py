"""
A-class Era D ~200 isolated failed-retry runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_a_class_erad_scale_200_isolated_retry_runner.py
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
RETRY_UNIVERSE = runner.DEFAULT_ERAD_FAILED_RETRY_UNIVERSE_CSV
RETRY_OUTPUT_ROOT = runner.DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT
ERAD_MAIN_OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
PHASE1_OUTPUT_ROOT = runner.PHASE1_OUTPUT_ROOT
PHASE2_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
PHASE3_OUTPUT_ROOT = runner.DEFAULT_PHASE3_OUTPUT_ROOT
A3M017_OUTPUT_ROOT = runner.DEFAULT_A3M017_RETRY_OUTPUT_ROOT
RETRY_V1_OUTPUT_ROOT = runner.DEFAULT_RETRY_OUTPUT_ROOT
RETRY_V2_OUTPUT_ROOT = runner.DEFAULT_RETRY_V2_OUTPUT_ROOT
RETRY_V3_OUTPUT_ROOT = runner.DEFAULT_RETRY_V3_OUTPUT_ROOT
PRECHECK_OUTPUT_ROOT = runner.PRECHECK_OUTPUT_ROOT
HARVEST_ROOT = runner.C_CLASS_HARVEST_ROOT
B_CLASS_PREFIX = runner.B_CLASS_VALIDATION_PREFIX
C_CLASS_PREFIX = runner.C_CLASS_VALIDATION_PREFIX
D_CLASS_PREFIX = runner.D_CLASS_VALIDATION_PREFIX

RETRY_DRYRUN_ARGS = [
    "--erad-a-scale-200-failed-retry",
    "--dry-run",
    "--universe-csv",
    RETRY_UNIVERSE,
    "--output-root",
    RETRY_OUTPUT_ROOT,
]

RETRY_DRYRUN_REPORT = os.path.join(
    RETRY_OUTPUT_ROOT,
    "reports",
    "a_class_erad_scale_200_failed_retry_dryrun_report.csv",
)
RETRY_DRYRUN_SUMMARY = os.path.join(
    RETRY_OUTPUT_ROOT,
    "reports",
    "a_class_erad_scale_200_failed_retry_dryrun_summary.md",
)

ALLOWED_CASE_IDS = runner.ERAD_FAILED_RETRY_ALLOWED_CASE_IDS
DEFERRED_CASE_ID = runner.ERAD_FAILED_RETRY_DEFERRED_CASE_ID


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


class TestAClassEradScale200IsolatedRetryRunner(unittest.TestCase):
    def test_dry_run_7_planned_ok_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(RETRY_DRYRUN_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("planned_ok=7", result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)
        with open(RETRY_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(row["dryrun_status"] == "planned_ok" for row in rows))
        case_ids = {row["case_id"] for row in rows}
        self.assertEqual(case_ids, ALLOWED_CASE_IDS)
        self.assertNotIn(DEFERRED_CASE_ID, case_ids)

    def test_universe_must_equal_7(self) -> None:
        result = _run(RETRY_DRYRUN_ARGS + ["--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FAILED_RETRY_UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_ad2e146_deferred_case_rejected_in_universe(self) -> None:
        with open(RETRY_UNIVERSE, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        rows[0]["case_id"] = DEFERRED_CASE_ID
        rows[0]["company_code"] = "688755"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8", newline=""
        ) as tmp:
            writer = csv.DictWriter(tmp, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            tmp_path = tmp.name
        try:
            result = _run(RETRY_DRYRUN_ARGS[:-2] + ["--universe-csv", tmp_path])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(runner.ERAD_FAILED_RETRY_DEFERRED_CASE_REJECTED, result.stderr)
        finally:
            os.unlink(tmp_path)

    def test_requires_universe_csv(self) -> None:
        result = _run(["--erad-a-scale-200-failed-retry", "--dry-run"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FAILED_RETRY_UNIVERSE_CSV_REQUIRED, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        ok, err = runner.validate_erad_failed_retry_output_root(RETRY_OUTPUT_ROOT)
        self.assertTrue(ok, msg=err)

    def test_main_erad_live_root_write_blocked(self) -> None:
        result = _run(RETRY_DRYRUN_ARGS[:-2] + ["--output-root", ERAD_MAIN_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FAILED_RETRY_MAIN_ERAD_ROOT_FORBIDDEN, result.stderr)

    def test_phase1_output_root_write_blocked(self) -> None:
        result = _run(RETRY_DRYRUN_ARGS[:-2] + ["--output-root", PHASE1_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE1_BASELINE_WRITE_FORBIDDEN, result.stderr)

    def test_phase2_output_root_write_blocked(self) -> None:
        result = _run(RETRY_DRYRUN_ARGS[:-2] + ["--output-root", PHASE2_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE2_EXPANSION_WRITE_FORBIDDEN, result.stderr)

    def test_phase3_output_root_write_blocked(self) -> None:
        result = _run(RETRY_DRYRUN_ARGS[:-2] + ["--output-root", PHASE3_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_a3m017_output_root_write_blocked(self) -> None:
        result = _run(RETRY_DRYRUN_ARGS[:-2] + ["--output-root", A3M017_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("a3m017_isolated_retry_output_root_forbidden", result.stderr)

    def test_harvest_output_root_write_blocked(self) -> None:
        result = _run(RETRY_DRYRUN_ARGS[:-2] + ["--output-root", HARVEST_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("c_class_harvest_output_root_forbidden", result.stderr)

    def test_b_class_output_root_write_blocked(self) -> None:
        result = _run(
            RETRY_DRYRUN_ARGS[:-2]
            + ["--output-root", os.path.join(B_CLASS_PREFIX, "phase3_100")]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("b_class_validation_output_root_forbidden", result.stderr)

    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch(
            "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
        ) as mock_exec:
            result = _run(
                [
                    "--erad-a-scale-200-failed-retry",
                    "--live",
                    "--universe-csv",
                    RETRY_UNIVERSE,
                    "--output-root",
                    RETRY_OUTPUT_ROOT,
                ]
            )
            mock_exec.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FAILED_RETRY_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flags_rejected_before_cninfo(self) -> None:
        wrong_flags = (
            "--approve-a-class-erad-scale-200",
            "--approve-a-class-phase3-50-company-expansion",
            "--approve-a-class-phase2-retry-v3",
        )
        for flag in wrong_flags:
            with mock.patch(
                "run_cninfo_a_class_tiny_live_metadata_validation.execute_live_case"
            ) as mock_exec:
                result = _run(
                    [
                        "--erad-a-scale-200-failed-retry",
                        "--live",
                        "--universe-csv",
                        RETRY_UNIVERSE,
                        "--output-root",
                        RETRY_OUTPUT_ROOT,
                        flag,
                    ]
                )
                mock_exec.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(runner.ERAD_FAILED_RETRY_WRONG_APPROVAL, result.stderr)

    def test_request_cap_24_enforced(self) -> None:
        ok, err = runner.validate_erad_failed_retry_request_cap(7)
        self.assertTrue(ok, msg=err)
        ok2, err2 = runner.validate_erad_failed_retry_request_cap(13)
        self.assertFalse(ok2)
        self.assertIn(runner.ERAD_FAILED_RETRY_REQUEST_CAP_EXCEEDED, err2)

    def test_pdf_download_blocked(self) -> None:
        result = _run(RETRY_DRYRUN_ARGS + ["--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag in ("--write-db", "--write-minio", "--run-rag"):
            result = _run(RETRY_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_verified_production_ready_blocked(self) -> None:
        for flag in ("--mark-verified", "--mark-production-ready"):
            result = _run(RETRY_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_incompatible_with_erad_main_mode(self) -> None:
        result = _run(
            [
                "--erad-a-scale-200",
                "--erad-a-scale-200-failed-retry",
                "--dry-run",
                "--universe-csv",
                RETRY_UNIVERSE,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_FAILED_RETRY_INCOMPATIBLE_WITH_OTHER_MODES, result.stderr)

    def test_main_erad_root_not_mutated_by_dry_run(self) -> None:
        marker_dir = os.path.join(ERAD_MAIN_OUTPUT_ROOT, "reports")
        os.makedirs(marker_dir, exist_ok=True)
        marker_path = os.path.join(marker_dir, "_failed_retry_guard.txt")
        with open(marker_path, "w", encoding="utf-8") as f:
            f.write("guard")
        before = _file_sha256(marker_path)
        result = _run(RETRY_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertEqual(before, _file_sha256(marker_path))
        if os.path.isfile(marker_path):
            os.remove(marker_path)

    def test_dry_run_summary_generated(self) -> None:
        result = _run(RETRY_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(RETRY_DRYRUN_SUMMARY))
        with open(RETRY_DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CNINFO calls | **0**", content)
        self.assertIn("AD2E146", content)
        self.assertIn(runner.ERAD_FAILED_RETRY_RUNNER_GATE, content)


if __name__ == "__main__":
    unittest.main()
