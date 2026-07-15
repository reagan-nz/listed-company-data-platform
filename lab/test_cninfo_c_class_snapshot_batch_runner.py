"""
CNINFO C-class snapshot full batch runner 测试（无 CNINFO · 无 build_snapshot 执行）。

运行：
    python lab/test_cninfo_c_class_snapshot_batch_runner.py
"""

from __future__ import annotations

import csv
import os
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Dict, List
from unittest.mock import patch

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from build_cninfo_c_class_snapshot_batch import (  # noqa: E402
    BASE_DIR,
    ERROR_FIELDS,
    EXPECTED_COMPANY_COUNT,
    FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED,
    STATUS_FIELDS,
    append_error_record,
    build_execution_list,
    filter_resume_targets,
    init_status_rows,
    load_hold_codes,
    load_universe_yaml,
    read_status_csv,
    run_dry_run,
    run_single_company_safe,
    validate_universe,
    write_status_csv,
)

RUNNER = os.path.join(_LAB_DIR, "build_cninfo_c_class_snapshot_batch.py")
UNIVERSE_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
HOLD_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml")
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_snapshot_batch_runner_test_summary.md",
)


def _run_runner(argv: List[str]) -> subprocess.CompletedProcess:
    cmd = [sys.executable, RUNNER] + argv
    return subprocess.run(cmd, cwd=BASE_DIR, capture_output=True, text=True)


class TestSnapshotBatchRunner(unittest.TestCase):
    def test_case1_dry_run_universe_863(self) -> None:
        companies, meta = load_universe_yaml(UNIVERSE_YAML)
        hold_codes = load_hold_codes(HOLD_YAML)
        ok, detail = validate_universe(companies, hold_codes)
        self.assertTrue(ok, detail)
        self.assertEqual(detail["company_count"], EXPECTED_COMPANY_COUNT)
        self.assertEqual(meta.get("company_count"), EXPECTED_COMPANY_COUNT)

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = os.path.join(tmp, "full")
            quality = os.path.join(out_dir, "quality")
            result = run_dry_run(
                universe_path=UNIVERSE_YAML,
                hold_path=HOLD_YAML,
                out_dir=out_dir,
                status_path=os.path.join(quality, "company_snapshot_status.csv"),
                error_path=os.path.join(quality, "company_snapshot_error.csv"),
                report_path=os.path.join(tmp, "dryrun_report.csv"),
                summary_path=os.path.join(tmp, "dryrun_summary.md"),
            )
        self.assertTrue(result["universe_ok"])
        self.assertEqual(len(result["report_rows"]), EXPECTED_COMPANY_COUNT)
        self.assertEqual(result["gate"], "PASS_WITH_CAVEAT")

        # CLI bare --dry-run：写隔离 mock 根，不触碰生产 snapshot quality
        proc = _run_runner(["--dry-run"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("snapshot_batch_dryrun_gate: PASS_WITH_CAVEAT", proc.stdout)
        self.assertIn("snapshot_dryrun_output_root_isolation: enforced", proc.stdout)
        self.assertIn("_mock_snapshot_batch_standard_dryrun_isolated", proc.stdout)
        self.assertIn("dryrun_fingerprint_sha256:", proc.stdout)

    def test_case2_hold_overlap_detection(self) -> None:
        companies, _ = load_universe_yaml(UNIVERSE_YAML)
        hold_codes = load_hold_codes(HOLD_YAML)
        ok, detail = validate_universe(companies, hold_codes)
        self.assertEqual(detail["hold_overlap_count"], 0)
        self.assertTrue(ok)

        poisoned = list(companies)
        poisoned[0] = dict(poisoned[0])
        poisoned[0]["company_code"] = sorted(hold_codes)[0]
        ok2, detail2 = validate_universe(poisoned, hold_codes)
        self.assertFalse(ok2)
        self.assertGreater(detail2["hold_overlap_count"], 0)

    def test_case3_status_csv_generation(self) -> None:
        companies, _ = load_universe_yaml(UNIVERSE_YAML)
        execution = build_execution_list(companies[:3])
        rows = init_status_rows(execution)

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "company_snapshot_status.csv")
            write_status_csv(rows, path=path)
            loaded = read_status_csv(path)

        self.assertEqual(len(loaded), 3)
        for code, row in loaded.items():
            self.assertEqual(set(row.keys()), set(STATUS_FIELDS))
            self.assertEqual(row["status"], "pending")
            self.assertEqual(row["retry_status"], "none")

    def test_case4_error_isolation_mock(self) -> None:
        calls: List[str] = []

        def flaky_build(code: str, _mapping: List[Dict[str, Any]]) -> Any:
            calls.append(code)
            if code == "000002":
                raise ValueError("mock build failure")
            return {"snapshot_status": "complete_with_caveat"}, {
                "module_status": {"m": "available"},
            }

        mapping: List[Dict[str, str]] = []
        targets = [
            {"company_code": "000001", "company_name": "A", "board": "szse_main"},
            {"company_code": "000002", "company_name": "B", "board": "szse_main"},
            {"company_code": "000003", "company_name": "C", "board": "szse_main"},
        ]
        status_rows = init_status_rows(targets)
        status_by_code = {r["company_code"]: r for r in status_rows}

        from build_cninfo_c_class_snapshot_batch import run_execute_batch

        with tempfile.TemporaryDirectory() as tmp:
            errors, success, failed = run_execute_batch(
                targets,
                mapping,
                status_by_code,
                out_dir=tmp,
                build_fn=flaky_build,
                write_json=False,
            )

        self.assertEqual(success, 2)
        self.assertEqual(failed, 1)
        self.assertEqual(len(calls), 3)
        self.assertEqual(status_by_code["000002"]["status"], "failed")
        self.assertEqual(status_by_code["000001"]["status"], "complete_with_caveat")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["error_type"], "ValueError")

    def test_case5_resume_mock(self) -> None:
        companies, _ = load_universe_yaml(UNIVERSE_YAML)
        execution = build_execution_list(companies[:5])
        status_rows = init_status_rows(execution)
        status_rows[0]["status"] = "complete_with_caveat"
        status_rows[1]["status"] = "failed"
        status_by_code = {r["company_code"]: r for r in status_rows}

        filtered = filter_resume_targets(execution, status_by_code, force=False)
        self.assertEqual(len(filtered), 3)

        forced = filter_resume_targets(execution, status_by_code, force=True)
        self.assertEqual(len(forced), 5)

        with tempfile.TemporaryDirectory() as tmp:
            quality = os.path.join(tmp, "quality")
            status_path = os.path.join(quality, "company_snapshot_status.csv")
            write_status_csv(status_rows, path=status_path)
            result = run_dry_run(
                universe_path=UNIVERSE_YAML,
                hold_path=HOLD_YAML,
                out_dir=os.path.join(tmp, "full"),
                status_path=status_path,
                error_path=os.path.join(quality, "company_snapshot_error.csv"),
                report_path=os.path.join(tmp, "report.csv"),
                summary_path=os.path.join(tmp, "summary.md"),
                resume=True,
                force=False,
            )
        self.assertEqual(result["resume_skipped"], 2)

    def test_execute_without_approve_rejected(self) -> None:
        proc = _run_runner(["--execute"])
        self.assertEqual(proc.returncode, 2)
        self.assertIn(FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED, proc.stderr)


def write_test_summary(results: List[Dict[str, str]]) -> None:
    passed = sum(1 for r in results if r["status"] == "PASS")
    lines = [
        "# CNINFO C-Class Snapshot Batch Runner Test Summary",
        "",
        f"**{passed}/{len(results)} PASS**",
        "",
        "| case | status |",
        "|------|--------|",
    ]
    for r in results:
        lines.append(f"| {r['case']} | **{r['status']}** |")
    lines.extend([
        "",
        "**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`",
        "",
        "## 红线确认",
        "",
        "- 测试未请求 CNINFO · 未生成 full snapshot JSON（case_4 write_json=False）",
        "- raw / normalized / field_inventory **未修改**",
    ])
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSnapshotBatchRunner)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    case_names = [
        "case_1_dry_run_universe_863",
        "case_2_hold_overlap_detection",
        "case_3_status_csv_generation",
        "case_4_error_isolation_mock",
        "case_5_resume_mock",
    ]
    test_results = []
    for i, test_id in enumerate([
        "test_case1_dry_run_universe_863",
        "test_case2_hold_overlap_detection",
        "test_case3_status_csv_generation",
        "test_case4_error_isolation_mock",
        "test_case5_resume_mock",
    ]):
        failed = any(test_id in str(f) for f in result.failures + result.errors)
        test_results.append({
            "case": case_names[i],
            "status": "FAIL" if failed else "PASS",
        })

    write_test_summary(test_results)
    print(f"\nTest summary: {SUMMARY_PATH}")
    print(f"Result: {sum(1 for r in test_results if r['status']=='PASS')}/{len(test_results)} PASS")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
