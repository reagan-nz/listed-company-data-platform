"""
A-class Era D ~200 runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_a_class_erad_scale_200_runner.py
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
ERAD_UNIVERSE = runner.DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV
ERAD_OUTPUT_ROOT = runner.DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
ERAD_DRYRUN_REPORT = os.path.join(
    ERAD_OUTPUT_ROOT, "reports", "a_class_erad_scale_200_dryrun_report.csv"
)
ERAD_DRYRUN_SUMMARY = os.path.join(
    ERAD_OUTPUT_ROOT, "reports", "a_class_erad_scale_200_dryrun_summary.md"
)
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

ERAD_DRYRUN_ARGS = [
    "--erad-a-scale-200",
    "--dry-run",
    "--universe-csv",
    ERAD_UNIVERSE,
    "--output-root",
    ERAD_OUTPUT_ROOT,
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


class TestAClassEradScale200Runner(unittest.TestCase):
    def test_dry_run_200_planned_ok_cninfo_zero(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(ERAD_DRYRUN_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("planned_ok=200", result.stdout)
        self.assertIn("cninfo_calls=0", result.stdout)
        with open(ERAD_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 200)
        self.assertTrue(all(row["dryrun_status"] == "planned_ok" for row in rows))

    def test_universe_must_equal_200(self) -> None:
        result = _run(ERAD_DRYRUN_ARGS + ["--limit", "3"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_SCALE_200_UNIVERSE_SIZE_VIOLATION, result.stderr)

    def test_erad_requires_universe_csv(self) -> None:
        result = _run(["--erad-a-scale-200", "--dry-run"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_SCALE_200_UNIVERSE_CSV_REQUIRED, result.stderr)

    def test_output_root_isolation_enforced(self) -> None:
        ok, err = runner.validate_erad_scale_200_output_root(ERAD_OUTPUT_ROOT)
        self.assertTrue(ok, msg=err)

    def test_phase1_output_root_write_blocked(self) -> None:
        result = _run(ERAD_DRYRUN_ARGS[:-2] + ["--output-root", PHASE1_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE1_BASELINE_WRITE_FORBIDDEN, result.stderr)

    def test_phase2_output_root_write_blocked(self) -> None:
        result = _run(ERAD_DRYRUN_ARGS[:-2] + ["--output-root", PHASE2_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE2_EXPANSION_WRITE_FORBIDDEN, result.stderr)

    def test_phase3_output_root_write_blocked(self) -> None:
        result = _run(ERAD_DRYRUN_ARGS[:-2] + ["--output-root", PHASE3_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PHASE3_OUTPUT_ROOT_VIOLATION, result.stderr)

    def test_a3m017_output_root_write_blocked(self) -> None:
        result = _run(ERAD_DRYRUN_ARGS[:-2] + ["--output-root", A3M017_OUTPUT_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("a3m017_isolated_retry_output_root_forbidden", result.stderr)

    def test_retry_output_roots_write_blocked(self) -> None:
        for root, err in (
            (RETRY_V1_OUTPUT_ROOT, runner.RETRY_V1_WRITE_FORBIDDEN),
            (RETRY_V2_OUTPUT_ROOT, runner.RETRY_V2_WRITE_FORBIDDEN),
            (RETRY_V3_OUTPUT_ROOT, runner.RETRY_V3_OUTPUT_ROOT_VIOLATION),
            (PRECHECK_OUTPUT_ROOT, runner.PRECHECK_WRITE_FORBIDDEN),
        ):
            result = _run(ERAD_DRYRUN_ARGS[:-2] + ["--output-root", root])
            self.assertNotEqual(result.returncode, 0, msg=root)
            self.assertIn(err, result.stderr)

    def test_harvest_output_root_write_blocked(self) -> None:
        result = _run(ERAD_DRYRUN_ARGS[:-2] + ["--output-root", HARVEST_ROOT])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("c_class_harvest_output_root_forbidden", result.stderr)

    def test_b_class_output_root_write_blocked(self) -> None:
        result = _run(
            ERAD_DRYRUN_ARGS[:-2]
            + ["--output-root", os.path.join(B_CLASS_PREFIX, "phase3_100_expansion")]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("b_class_validation_output_root_forbidden", result.stderr)

    def test_c_class_validation_output_root_write_blocked(self) -> None:
        result = _run(
            ERAD_DRYRUN_ARGS[:-2]
            + ["--output-root", os.path.join(C_CLASS_PREFIX, "phase3_batch_500")]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("c_class_validation_output_root_forbidden", result.stderr)

    def test_d_class_output_root_write_blocked(self) -> None:
        result = _run(
            ERAD_DRYRUN_ARGS[:-2]
            + ["--output-root", os.path.join(D_CLASS_PREFIX, "disclosure_schedule_first_slice")]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("d_class_validation_output_root_forbidden", result.stderr)

    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            result = _run(
                [
                    "--erad-a-scale-200",
                    "--live",
                    "--universe-csv",
                    ERAD_UNIVERSE,
                    "--output-root",
                    ERAD_OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.ERAD_SCALE_200_APPROVAL_REQUIRED, result.stderr)

    def test_wrong_approval_flags_rejected_before_cninfo(self) -> None:
        wrong_flags = (
            "--approve-a-class-phase2-metadata-expansion",
            "--approve-a-class-phase2-failed-retry",
            "--approve-a-class-phase2-network-recovery-retry-v2",
            "--approve-a-class-phase2-retry-v3",
            "--approve-a-class-phase3-50-company-expansion",
            "--approve-a-class-tiny-live-metadata",
            "--approve-phase1-tiny-live-metadata",
        )
        for flag in wrong_flags:
            with mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                result = _run(
                    [
                        "--erad-a-scale-200",
                        "--live",
                        "--universe-csv",
                        ERAD_UNIVERSE,
                        "--output-root",
                        ERAD_OUTPUT_ROOT,
                        flag,
                    ]
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertNotEqual(result.returncode, 0, msg=flag)
            self.assertIn(runner.ERAD_SCALE_200_WRONG_APPROVAL, result.stderr)

    def test_request_cap_480_enforced(self) -> None:
        ok, err = runner.validate_erad_scale_200_request_cap(200)
        self.assertTrue(ok, msg=err)
        ok2, err2 = runner.validate_erad_scale_200_request_cap(241)
        self.assertFalse(ok2)
        self.assertIn(runner.ERAD_SCALE_200_REQUEST_CAP_EXCEEDED, err2)

    def test_pdf_download_blocked(self) -> None:
        result = _run(ERAD_DRYRUN_ARGS + ["--download-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_pdf_parser_blocked(self) -> None:
        result = _run(ERAD_DRYRUN_ARGS + ["--parse-pdf"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(runner.PDF_PARSE_REQUESTED_NOT_ALLOWED, result.stderr)

    def test_ocr_extraction_blocked(self) -> None:
        for flag in ("--enable-ocr", "--enable-extraction"):
            result = _run(ERAD_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_db_minio_rag_blocked(self) -> None:
        for flag in ("--write-db", "--write-minio", "--run-rag"):
            result = _run(ERAD_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_verified_production_ready_blocked(self) -> None:
        for flag in ("--mark-verified", "--mark-production-ready"):
            result = _run(ERAD_DRYRUN_ARGS + [flag])
            self.assertNotEqual(result.returncode, 0, msg=flag)

    def test_dry_run_summary_generated(self) -> None:
        result = _run(ERAD_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(ERAD_DRYRUN_SUMMARY))
        with open(ERAD_DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CNINFO calls | **0**", content)
        self.assertIn(runner.ERAD_SCALE_200_RUNNER_GATE, content)

    def test_input_universe_csv_not_mutated(self) -> None:
        before = _file_sha256(ERAD_UNIVERSE)
        result = _run(ERAD_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        after = _file_sha256(ERAD_UNIVERSE)
        self.assertEqual(before, after)

    def test_cleanup_does_not_delete_erad_production_marker(self) -> None:
        marker_dir = os.path.join(ERAD_OUTPUT_ROOT, "_production_guard")
        os.makedirs(marker_dir, exist_ok=True)
        marker_path = os.path.join(marker_dir, "keep.txt")
        with open(marker_path, "w", encoding="utf-8") as f:
            f.write("guard")
        before = _file_sha256(marker_path)
        result = _run(ERAD_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(marker_path))
        self.assertEqual(before, _file_sha256(marker_path))

    def test_retained_cohort_does_not_rewrite_phase3_production_root(self) -> None:
        os.makedirs(PHASE3_OUTPUT_ROOT, exist_ok=True)
        marker_path = os.path.join(PHASE3_OUTPUT_ROOT, "_erad_test_guard.txt")
        with open(marker_path, "w", encoding="utf-8") as f:
            f.write("phase3_guard")
        before = _file_sha256(marker_path)
        result = _run(ERAD_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertTrue(os.path.isfile(marker_path))
        self.assertEqual(before, _file_sha256(marker_path))
        with open(ERAD_DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        retained = [r for r in rows if r.get("cohort") == "retained_phase3"]
        self.assertEqual(len(retained), 50)
        for row in retained:
            self.assertIn("retained_phase3_lineage_only_no_phase3_root_write", row["notes"])

    def test_a3m017_production_root_not_mutated(self) -> None:
        os.makedirs(A3M017_OUTPUT_ROOT, exist_ok=True)
        marker_path = os.path.join(A3M017_OUTPUT_ROOT, "_erad_test_guard.txt")
        with open(marker_path, "w", encoding="utf-8") as f:
            f.write("a3m017_guard")
        before = _file_sha256(marker_path)
        result = _run(ERAD_DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertEqual(before, _file_sha256(marker_path))

    def test_new_cohort_zero_overlap(self) -> None:
        cases = runner.load_erad_scale_200_universe(ERAD_UNIVERSE)
        ok, err = runner.validate_erad_scale_200_new_cohort_overlap(cases)
        self.assertTrue(ok, msg=err)


if __name__ == "__main__":
    unittest.main()
