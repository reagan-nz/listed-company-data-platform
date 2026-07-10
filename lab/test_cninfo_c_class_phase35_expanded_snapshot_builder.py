"""
Phase 3.5 expanded success-subset snapshot builder 扩展测试（无 CNINFO · 无 snapshot JSON）。

运行：
    python lab/test_cninfo_c_class_phase35_expanded_snapshot_builder.py
"""

from __future__ import annotations

import argparse
import csv
import glob
import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import build_cninfo_c_class_snapshot_batch as batch_runner  # noqa: E402
from build_cninfo_c_class_snapshot_batch import (  # noqa: E402
    BASE_DIR,
    FULL_SNAPSHOT_OUT_DIR_REL,
    PHASE35_BATCH_HARVEST_ROOT_REL,
    PHASE35_C35R016_CODE,
    PHASE35_EXPANDED_DRYRUN_REPORT_CSV,
    PHASE35_EXPANDED_DRYRUN_SUMMARY_MD,
    PHASE35_EXPANDED_EXPECTED_COUNT,
    PHASE35_EXPANDED_MANIFEST_ROWS,
    PHASE35_EXPANDED_ORIGINAL_COUNT,
    PHASE35_EXPANDED_RESUME_COUNT,
    PHASE35_EXPANDED_SNAPSHOT_APPROVAL_REQUIRED,
    PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL,
    PHASE35_EXPANDED_UNIVERSE_CSV_REL,
    PHASE35_EXPANDED_WRONG_APPROVAL_REJECTED,
    PHASE35_HOLD_FOR_REVIEW_CODES,
    PHASE35_MERGE_MANIFEST_CSV_REL,
    PHASE35_RESUME_HARVEST_ROOT_REL,
    enforce_execute_approval,
    enforce_phase35_expanded_snapshot_preflight,
    load_expanded_universe_csv,
    load_merge_manifest_csv,
    validate_phase35_expanded_output_root,
    validate_phase35_expanded_universe_and_manifest,
    validate_phase35_harvest_roots_readonly,
)

PHASE35_SAMPLE = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml"
)
UNIVERSE_CSV = os.path.join(BASE_DIR, PHASE35_EXPANDED_UNIVERSE_CSV_REL)
MANIFEST_CSV = os.path.join(BASE_DIR, PHASE35_MERGE_MANIFEST_CSV_REL)
SNAPSHOT_ROOT = os.path.join(BASE_DIR, PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL)
RUNNER = os.path.join(_LAB_DIR, "build_cninfo_c_class_snapshot_batch.py")
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_builder_test_summary.md",
)

DRYRUN_ARGS = [
    "--dry-run",
    "--sample-file", "lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml",
    "--harvest-root", PHASE35_BATCH_HARVEST_ROOT_REL,
    "--resume-harvest-root", PHASE35_RESUME_HARVEST_ROOT_REL,
    "--merge-manifest", PHASE35_MERGE_MANIFEST_CSV_REL,
    "--output-root", PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL,
]


def _run_runner(argv: list) -> subprocess.CompletedProcess:
    cmd = [sys.executable, RUNNER] + argv
    return subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)


def _phase35_args(**overrides) -> argparse.Namespace:
    base = {
        "dry_run": True,
        "approve_full_snapshot_batch": False,
        "approve_phase2_smoke_188_snapshot": False,
        "approve_phase3_success_snapshot_build": False,
        "approve_phase35_expanded_success_snapshot_build": False,
        "harvest_root": os.path.join(BASE_DIR, PHASE35_BATCH_HARVEST_ROOT_REL),
        "resume_harvest_root": os.path.join(BASE_DIR, PHASE35_RESUME_HARVEST_ROOT_REL),
        "merge_manifest": MANIFEST_CSV,
        "output_root": SNAPSHOT_ROOT,
        "output_dir": None,
        "output_csv": None,
        "output_md": None,
    }
    base.update(overrides)
    return argparse.Namespace(**base)


class TestPhase35ExpandedSnapshotBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        result = _run_runner(DRYRUN_ARGS)
        if result.returncode != 0:
            raise RuntimeError(f"phase35 expanded dry-run failed: {result.stderr}")

    def setUp(self) -> None:
        with open(UNIVERSE_CSV, encoding="utf-8") as fh:
            self._universe_text = fh.read()
        with open(MANIFEST_CSV, encoding="utf-8") as fh:
            self._manifest_text = fh.read()
        self._snapshot_json_before = set(
            glob.glob(os.path.join(SNAPSHOT_ROOT, "**", "*.json"), recursive=True)
        )

    def tearDown(self) -> None:
        snapshot_json_after = set(
            glob.glob(os.path.join(SNAPSHOT_ROOT, "**", "*.json"), recursive=True)
        )
        self.assertEqual(snapshot_json_after, self._snapshot_json_before)

    def test_case1_dry_run_calls_cninfo_zero_times(self) -> None:
        result = _run_runner(DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_case2_dry_run_writes_snapshot_json_zero_times(self) -> None:
        result = _run_runner(DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("snapshot_json_written=0", result.stdout)
        self.assertEqual(
            len(glob.glob(os.path.join(SNAPSHOT_ROOT, "**", "*.json"), recursive=True)),
            len(self._snapshot_json_before),
        )

    def test_case3_universe_size_must_equal_491(self) -> None:
        companies = load_expanded_universe_csv(UNIVERSE_CSV)
        self.assertEqual(len(companies), PHASE35_EXPANDED_EXPECTED_COUNT)
        ok, detail = validate_phase35_expanded_universe_and_manifest(
            companies, load_merge_manifest_csv(MANIFEST_CSV)
        )
        self.assertTrue(ok, detail)

    def test_case4_original_resume_split_463_28(self) -> None:
        companies = load_expanded_universe_csv(UNIVERSE_CSV)
        original_n = sum(1 for c in companies if c.get("source_root_role") == "original")
        resume_n = sum(1 for c in companies if c.get("source_root_role") == "resume")
        self.assertEqual(original_n, PHASE35_EXPANDED_ORIGINAL_COUNT)
        self.assertEqual(resume_n, PHASE35_EXPANDED_RESUME_COUNT)

    def test_case5_c35r016_rejected(self) -> None:
        companies = load_expanded_universe_csv(UNIVERSE_CSV)
        codes = {c["company_code"] for c in companies}
        self.assertNotIn(PHASE35_C35R016_CODE, codes)

    def test_case6_hold_for_review_rejected(self) -> None:
        companies = load_expanded_universe_csv(UNIVERSE_CSV)
        codes = {c["company_code"] for c in companies}
        self.assertFalse(codes & PHASE35_HOLD_FOR_REVIEW_CODES)

    def test_case7_merge_manifest_size_4910(self) -> None:
        manifest_rows = load_merge_manifest_csv(MANIFEST_CSV)
        self.assertEqual(len(manifest_rows), PHASE35_EXPANDED_MANIFEST_ROWS)

    def test_case8_output_root_isolation_enforced(self) -> None:
        self.assertTrue(validate_phase35_expanded_output_root(SNAPSHOT_ROOT))
        bad_out = os.path.join(BASE_DIR, FULL_SNAPSHOT_OUT_DIR_REL)
        self.assertFalse(validate_phase35_expanded_output_root(bad_out))

        args = _phase35_args()
        companies = load_expanded_universe_csv(UNIVERSE_CSV)
        manifest_rows = load_merge_manifest_csv(MANIFEST_CSV)
        enforce_phase35_expanded_snapshot_preflight(
            args, PHASE35_SAMPLE, SNAPSHOT_ROOT, companies, manifest_rows,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_phase35_expanded_snapshot_preflight(
                    args, PHASE35_SAMPLE, bad_out, companies, manifest_rows,
                )
        self.assertIn("PHASE35_EXPANDED_OUTPUT_ROOT_MISMATCH", buf.getvalue())

    def test_case9_original_harvest_root_write_blocked(self) -> None:
        ok, detail = validate_phase35_harvest_roots_readonly(
            os.path.join(BASE_DIR, PHASE35_BATCH_HARVEST_ROOT_REL),
            os.path.join(BASE_DIR, PHASE35_RESUME_HARVEST_ROOT_REL),
        )
        self.assertTrue(ok, detail)
        bad_ok, _ = validate_phase35_harvest_roots_readonly(
            os.path.join(BASE_DIR, "outputs/harvest/cninfo_c_class/wrong"),
            os.path.join(BASE_DIR, PHASE35_RESUME_HARVEST_ROOT_REL),
        )
        self.assertFalse(bad_ok)

    def test_case10_resume_harvest_root_write_blocked(self) -> None:
        bad_ok, _ = validate_phase35_harvest_roots_readonly(
            os.path.join(BASE_DIR, PHASE35_BATCH_HARVEST_ROOT_REL),
            os.path.join(BASE_DIR, "outputs/harvest/cninfo_c_class/wrong_resume"),
        )
        self.assertFalse(bad_ok)

    def test_case11_real_build_requires_phase35_approval(self) -> None:
        result = _run_runner([
            "--execute",
            "--sample-file", "lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml",
            "--harvest-root", PHASE35_BATCH_HARVEST_ROOT_REL,
            "--resume-harvest-root", PHASE35_RESUME_HARVEST_ROOT_REL,
            "--merge-manifest", PHASE35_MERGE_MANIFEST_CSV_REL,
            "--output-root", PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL,
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE35_EXPANDED_SNAPSHOT_APPROVAL_REQUIRED, result.stderr)

        args = _phase35_args(dry_run=False)
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_execute_approval(args, PHASE35_SAMPLE)
        self.assertIn(PHASE35_EXPANDED_SNAPSHOT_APPROVAL_REQUIRED, buf.getvalue())

    def test_case12_wrong_approval_flag_rejected(self) -> None:
        result = _run_runner([
            "--execute",
            "--approve-full-snapshot-batch",
            "--sample-file", "lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml",
            "--harvest-root", PHASE35_BATCH_HARVEST_ROOT_REL,
            "--resume-harvest-root", PHASE35_RESUME_HARVEST_ROOT_REL,
            "--merge-manifest", PHASE35_MERGE_MANIFEST_CSV_REL,
            "--output-root", PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL,
        ])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(PHASE35_EXPANDED_WRONG_APPROVAL_REJECTED, result.stderr)

        args = _phase35_args(
            dry_run=False,
            approve_full_snapshot_batch=True,
            approve_phase35_expanded_success_snapshot_build=True,
        )
        buf = io.StringIO()
        with redirect_stderr(buf):
            with self.assertRaises(SystemExit):
                enforce_execute_approval(args, PHASE35_SAMPLE)
        self.assertIn(PHASE35_EXPANDED_WRONG_APPROVAL_REJECTED, buf.getvalue())

    def test_case13_db_minio_rag_blocked(self) -> None:
        result = _run_runner(DRYRUN_ARGS)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("db_writes=0", result.stdout)
        self.assertIn("minio_writes=0", result.stdout)
        self.assertIn("rag_runs=0", result.stdout)

    def test_case14_verified_production_ready_blocked(self) -> None:
        self.assertTrue(os.path.isfile(PHASE35_EXPANDED_DRYRUN_SUMMARY_MD))
        text = open(PHASE35_EXPANDED_DRYRUN_SUMMARY_MD, encoding="utf-8").read().lower()
        self.assertIn("not verified", text)
        self.assertIn("not production_ready", text)
        self.assertNotIn("production_ready = true", text)
        self.assertNotIn("verified = true", text)

    def test_case15_dryrun_report_generated(self) -> None:
        self.assertTrue(os.path.isfile(PHASE35_EXPANDED_DRYRUN_REPORT_CSV))
        with open(PHASE35_EXPANDED_DRYRUN_REPORT_CSV, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), PHASE35_EXPANDED_EXPECTED_COUNT)
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))

    def test_case16_dryrun_summary_generated(self) -> None:
        self.assertTrue(os.path.isfile(PHASE35_EXPANDED_DRYRUN_SUMMARY_MD))
        text = open(PHASE35_EXPANDED_DRYRUN_SUMMARY_MD, encoding="utf-8").read()
        self.assertIn("PASS_OFFLINE", text)
        self.assertIn("491", text)

    def test_case17_input_universe_manifest_not_mutated(self) -> None:
        with open(UNIVERSE_CSV, encoding="utf-8") as fh:
            after_universe = fh.read()
        with open(MANIFEST_CSV, encoding="utf-8") as fh:
            after_manifest = fh.read()
        self.assertEqual(after_universe, self._universe_text)
        self.assertEqual(after_manifest, self._manifest_text)


def write_summary(results: list) -> None:
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    passed = sum(1 for _, ok in results if ok)
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Builder Test Summary",
        "",
        f"## Result: **{passed}/{len(results)} PASS**",
        "",
        "| case | result |",
        "|------|--------|",
    ]
    for case_id, ok in results:
        lines.append(f"| `{case_id}` | **{'PASS' if ok else 'FAIL'}** |")
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPhase35ExpandedSnapshotBuilder)
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    name_map = {
        "test_case1_dry_run_calls_cninfo_zero_times": "case_1_cninfo_zero",
        "test_case2_dry_run_writes_snapshot_json_zero_times": "case_2_snapshot_json_zero",
        "test_case3_universe_size_must_equal_491": "case_3_universe_491",
        "test_case4_original_resume_split_463_28": "case_4_split_463_28",
        "test_case5_c35r016_rejected": "case_5_c35r016_excluded",
        "test_case6_hold_for_review_rejected": "case_6_hold_excluded",
        "test_case7_merge_manifest_size_4910": "case_7_manifest_4910",
        "test_case8_output_root_isolation_enforced": "case_8_output_isolation",
        "test_case9_original_harvest_root_write_blocked": "case_9_orig_block",
        "test_case10_resume_harvest_root_write_blocked": "case_10_resume_block",
        "test_case11_real_build_requires_phase35_approval": "case_11_approval_required",
        "test_case12_wrong_approval_flag_rejected": "case_12_wrong_flag",
        "test_case13_db_minio_rag_blocked": "case_13_db_minio_rag",
        "test_case14_verified_production_ready_blocked": "case_14_not_verified",
        "test_case15_dryrun_report_generated": "case_15_dryrun_report",
        "test_case16_dryrun_summary_generated": "case_16_dryrun_summary",
        "test_case17_input_universe_manifest_not_mutated": "case_17_inputs_unchanged",
    }
    failed = {t[0]._testMethodName for t in result.failures + result.errors}  # type: ignore[attr-defined]
    final = [(cid, m not in failed) for m, cid in name_map.items()]
    write_summary(final)
    passed = sum(1 for _, ok in final if ok)
    print(f"\n{passed}/{len(final)} PASS")
    print(f"MD    {SUMMARY_PATH}")
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
