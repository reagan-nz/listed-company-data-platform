"""
D-class executive_shareholding first-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    python lab/test_cninfo_d_class_executive_shareholding_first_slice_runner.py
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_tiny_live_validation.py")
UNIVERSE_CSV = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT
DRYRUN_REPORT = runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_DRYRUN_SUMMARY_MD
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
V2_OUTPUT_ROOT = runner.DEFAULT_V2_OUTPUT_ROOT
REPLACEMENT_OUTPUT_ROOT = runner.DEFAULT_REPLACEMENT_OUTPUT_ROOT
TARGETED_OUTPUT_ROOT = runner.DEFAULT_TARGETED_PROBE_OUTPUT_ROOT
MARGIN_OUTPUT_ROOT = runner.DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT
DISCLOSURE_OUTPUT_ROOT = runner.DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT
BLOCK_TRADE_OUTPUT_ROOT = runner.DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT
RSU_OUTPUT_ROOT = runner.DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
EQUITY_PLEDGE_OUTPUT_ROOT = runner.DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT
SHAREHOLDER_CHANGE_OUTPUT_ROOT = (
    runner.DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT
)
SHAREHOLDER_CHANGE_UNIVERSE_CSV = (
    runner.DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_UNIVERSE_CSV
)

BASE_ARGS = [
    "--dry-run",
    "--executive-shareholding-first-slice",
    "--universe-csv",
    UNIVERSE_CSV,
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


def _read_universe_rows() -> list[dict[str, str]]:
    with open(UNIVERSE_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_universe_csv(path: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _es_row_from_dict(r: dict[str, str]) -> runner.ExecutiveShareholdingFirstSliceRow:
    return runner.ExecutiveShareholdingFirstSliceRow(
        case_id=r["case_id"],
        company_code=r["company_code"],
        company_name=r["company_name"],
        component=r["component"],
        market=r["market"],
        time_mark=r.get("time_mark", "oneMonth"),
        vary_type=r.get("vary_type", "b"),
        first_slice_include=r["first_slice_include"],
        expected_behavior=r["expected_behavior"],
        exclude_flags=r.get("exclude_flags", ""),
        notes=r.get("notes", ""),
        dlc007_reference=r.get("dlc007_reference", ""),
    )


class TestExecutiveShareholdingFirstSliceRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_request_count_total=5", result.stdout)

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--executive-shareholding-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH,
            result.stderr,
        )

    def test_only_des001_through_des005_allowed(self) -> None:
        rows = _read_universe_rows()
        rows[0] = {**rows[0], "case_id": "DES999"}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_case.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--executive-shareholding-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FORBIDDEN_CASE_ID,
            result.stderr,
        )

    def test_component_must_be_executive_shareholding(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "component": "shareholder_change"}
            if r["case_id"] == "DES002"
            else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--executive-shareholding-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_COMPONENT,
            result.stderr,
        )

    def test_688671_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "company_code": "688671"} if r["case_id"] == "DES003" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_688671.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--executive-shareholding-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE,
            result.stderr,
        )

    def test_301259_rejected(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "company_code": "301259"} if r["case_id"] == "DES004" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_301259.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--executive-shareholding-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE,
            result.stderr,
        )

    def test_time_mark_must_be_oneMonth(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "time_mark": "threeMonth"} if r["case_id"] == "DES001" else r
            for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_time_mark.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--executive-shareholding-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_TIME_MARK,
            result.stderr,
        )

    def test_vary_type_must_be_b(self) -> None:
        rows = _read_universe_rows()
        rows = [
            {**r, "vary_type": "s"} if r["case_id"] == "DES001" else r for r in rows
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_vary_type.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--executive-shareholding-first-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_VARY_TYPE,
            result.stderr,
        )

    def test_output_root_isolation_enforced(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--executive-shareholding-first-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED,
            result.stderr,
        )

    def test_closed_track_roots_write_blocked(self) -> None:
        for bad_root, token in [
            (
                V2_OUTPUT_ROOT,
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                REPLACEMENT_OUTPUT_ROOT,
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                TARGETED_OUTPUT_ROOT,
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                MARGIN_OUTPUT_ROOT,
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                DISCLOSURE_OUTPUT_ROOT,
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                BLOCK_TRADE_OUTPUT_ROOT,
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                RSU_OUTPUT_ROOT,
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                EQUITY_PLEDGE_OUTPUT_ROOT,
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
            (
                SHAREHOLDER_CHANGE_OUTPUT_ROOT,
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_SHAREHOLDER_CHANGE_OUTPUT_ROOT_WRITE_BLOCKED,
            ),
        ]:
            with self.subTest(bad_root=bad_root):
                result = _run(
                    [
                        "--dry-run",
                        "--executive-shareholding-first-slice",
                        "--universe-csv",
                        UNIVERSE_CSV,
                        "--output-root",
                        bad_root,
                    ]
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_mixed_mode_with_shareholder_change_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--shareholder-change-first-slice"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_MIXED_MODE_BLOCKED,
            result.stderr,
        )

    def test_live_without_approval_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(
                [
                    "--live",
                    "--executive-shareholding-first-slice",
                    "--universe-csv",
                    UNIVERSE_CSV,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_APPROVAL_REQUIRED,
            result.stderr,
        )

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(
            hasattr(runner, "execute_executive_shareholding_first_slice_live")
        )
        self.assertTrue(
            callable(runner.execute_executive_shareholding_first_slice_live)
        )

    def test_wrong_approval_flag_rejected_before_cninfo(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(
                BASE_ARGS + ["--approve-d-class-shareholder-change-first-slice"]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_APPROVAL_FLAG,
            result.stderr,
        )

    def test_plan_is_oneMonth_b_only(self) -> None:
        rows = _read_universe_rows()
        for r in rows:
            row = _es_row_from_dict(r)
            plan = runner.build_executive_shareholding_first_slice_plan(
                row.time_mark, row.vary_type
            )
            params = runner._build_executive_shareholding_first_slice_params(row)
            self.assertEqual(plan, ["timeMark_oneMonth_varyType_b"])
            self.assertEqual(params, [{"timeMark": "oneMonth", "varyType": "b"}])
            self.assertEqual(len(params), 1)

    def test_planned_request_count_equals_5(self) -> None:
        load_rows = _read_universe_rows()
        total = sum(
            runner.compute_executive_shareholding_first_slice_planned_requests(
                _es_row_from_dict(r)
            )
            for r in load_rows
        )
        self.assertLessEqual(
            total, runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TOTAL_MAX_REQUESTS
        )
        self.assertEqual(total, 5)

    def test_tier1_fixtures_wired(self) -> None:
        for case_id in ("DES001", "DES002", "DES003", "DES004", "DES005"):
            refs = runner.resolve_executive_shareholding_first_slice_fixture_refs(
                case_id
            )
            self.assertTrue(refs, msg=case_id)
            for ref in refs:
                self.assertTrue(os.path.isfile(ref), msg=ref)

    def test_pdf_ocr_extraction_blocked(self) -> None:
        for flag, token in [
            ("--pdf-download", runner.PDF_DOWNLOAD_BLOCKED),
            ("--ocr", runner.OCR_BLOCKED),
            ("--extraction", runner.EXTRACTION_BLOCKED),
        ]:
            with self.subTest(flag=flag):
                result = _run(BASE_ARGS + [flag])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_db_minio_rag_blocked(self) -> None:
        for flag, token in [
            ("--db-write", runner.DB_WRITE_BLOCKED),
            ("--minio-write", runner.MINIO_WRITE_BLOCKED),
            ("--rag-run", runner.RAG_RUN_BLOCKED),
        ]:
            with self.subTest(flag=flag):
                result = _run(BASE_ARGS + [flag])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_verified_production_ready_blocked(self) -> None:
        for flag, token in [
            ("--mark-verified", runner.VERIFIED_BLOCKED),
            ("--production-ready", runner.PRODUCTION_READY_BLOCKED),
        ]:
            with self.subTest(flag=flag):
                result = _run(BASE_ARGS + [flag])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(token, result.stderr)

    def test_shareholder_change_first_slice_mode_smoke_intact(self) -> None:
        if not os.path.isfile(SHAREHOLDER_CHANGE_UNIVERSE_CSV):
            self.skipTest("shareholder_change universe not present")
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(
                [
                    "--dry-run",
                    "--shareholder-change-first-slice",
                    "--universe-csv",
                    SHAREHOLDER_CHANGE_UNIVERSE_CSV,
                    "--output-root",
                    SHAREHOLDER_CHANGE_OUTPUT_ROOT,
                ]
            )
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("cninfo_calls=0", result.stdout)

    def test_dry_run_report_and_planned_snapshots(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            report_rows = list(csv.DictReader(f))
        self.assertEqual(len(report_rows), 5)
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in report_rows))
        self.assertTrue(all(r["planned_request_count"] == "1" for r in report_rows))
        for case_id in ("DES001", "DES002", "DES003", "DES004", "DES005"):
            snap = os.path.join(
                OUTPUT_ROOT,
                "planned_snapshots",
                f"{case_id}_executive_shareholding.json",
            )
            self.assertTrue(os.path.isfile(snap), msg=snap)
            with open(snap, encoding="utf-8") as f:
                meta = json.load(f)
            self.assertIs(meta.get("cninfo_called"), False)
            self.assertEqual(
                meta.get("planned_params"),
                [{"timeMark": "oneMonth", "varyType": "b"}],
            )
            self.assertTrue(meta.get("tier1_fixture_refs"), msg=case_id)

    def test_dry_run_summary_generated(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("CNINFO calls = 0", content)
        self.assertIn("NOT APPROVED", content)
        self.assertIn("timeMark=oneMonth", content)
        self.assertIn("Tier-1", content)

    def test_empty_but_valid_acceptable_rules(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        for case_id in ("DES002", "DES003", "DES004", "DES005"):
            with self.subTest(case_id=case_id):
                row = _es_row_from_dict(
                    next(r for r in _read_universe_rows() if r["case_id"] == case_id)
                )
                self.assertTrue(
                    runner.is_executive_shareholding_first_slice_acceptable(
                        row, summary
                    )
                )

    def test_des001_empty_is_expectation_mismatch(self) -> None:
        row = _es_row_from_dict(
            next(r for r in _read_universe_rows() if r["case_id"] == "DES001")
        )
        self.assertEqual(row.expected_behavior, "captured_normal_or_needs_review")
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        self.assertFalse(
            runner.is_executive_shareholding_first_slice_acceptable(row, summary)
        )
        self.assertEqual(
            runner.assess_executive_shareholding_first_slice_failure_type(
                row, summary
            ),
            "expectation_mismatch",
        )

    def test_execution_gate_three_of_five(self) -> None:
        rows = [_es_row_from_dict(r) for r in _read_universe_rows()]
        summaries = {
            r.case_id: {
                "retrieval_status": "empty_but_valid",
                "quality_status": "pass",
                "record_count": "0",
            }
            for r in rows
        }
        # DES001 empty -> not acceptable; DES002-005 empty -> acceptable => 4/5
        gate = runner.compute_executive_shareholding_first_slice_execution_gate(
            rows, summaries
        )
        self.assertEqual(
            gate, runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXECUTION_GATE_PASS
        )


class TestExecutiveShareholdingFirstSliceS5Closure(unittest.TestCase):
    """S5 closure 离线校验：acceptable 规则 + live/quality/ledger schema（无 CNINFO）。"""

    LIVE_REPORT = os.path.join(
        OUTPUT_ROOT,
        "reports",
        "d_class_executive_shareholding_first_slice_live_report.csv",
    )
    QUALITY_REPORT = os.path.join(
        OUTPUT_ROOT,
        "reports",
        "d_class_executive_shareholding_first_slice_quality_report.csv",
    )
    OUTCOME_LEDGER = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_d_class_executive_shareholding_first_slice_live_outcome_ledger.csv",
    )
    CLOSURE_METRICS = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_d_class_executive_shareholding_first_slice_closure_metrics.csv",
    )
    CAVEAT_LEDGER = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_d_class_executive_shareholding_first_slice_final_caveat_ledger.csv",
    )
    EFFECTIVE_RESULT = os.path.join(
        BASE_DIR,
        "outputs",
        "validation",
        "cninfo_d_class_executive_shareholding_first_slice_effective_result.csv",
    )

    def _row(self, case_id: str) -> runner.ExecutiveShareholdingFirstSliceRow:
        return _es_row_from_dict(
            next(r for r in _read_universe_rows() if r["case_id"] == case_id)
        )

    def test_empty_but_valid_acceptable_when_expectation_allows(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        for case_id in ("DES002", "DES003", "DES004", "DES005"):
            with self.subTest(case_id=case_id):
                row = self._row(case_id)
                self.assertTrue(
                    runner.is_executive_shareholding_first_slice_acceptable(
                        row, summary
                    )
                )
                self.assertEqual(
                    runner.assess_executive_shareholding_first_slice_failure_type(
                        row, summary
                    ),
                    "",
                )

    def test_des001_empty_is_expectation_mismatch(self) -> None:
        row = self._row("DES001")
        self.assertEqual(row.expected_behavior, "captured_normal_or_needs_review")
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        self.assertFalse(
            runner.is_executive_shareholding_first_slice_acceptable(row, summary)
        )
        self.assertEqual(
            runner.assess_executive_shareholding_first_slice_failure_type(
                row, summary
            ),
            "expectation_mismatch",
        )

    def test_des001_found_or_needs_review_with_rows_is_acceptable(self) -> None:
        row = self._row("DES001")
        for rs in ("found", "needs_review"):
            with self.subTest(retrieval_status=rs):
                summary = {
                    "retrieval_status": rs,
                    "quality_status": (
                        "needs_review" if rs == "needs_review" else "pass"
                    ),
                    "record_count": "1",
                }
                self.assertTrue(
                    runner.is_executive_shareholding_first_slice_acceptable(
                        row, summary
                    )
                )

    def test_execution_gate_four_of_five_sparse_window(self) -> None:
        rows = [_es_row_from_dict(r) for r in _read_universe_rows()]
        summaries = {
            r.case_id: {
                "retrieval_status": "empty_but_valid",
                "quality_status": "pass",
                "record_count": "0",
            }
            for r in rows
        }
        gate = runner.compute_executive_shareholding_first_slice_execution_gate(
            rows, summaries
        )
        self.assertEqual(
            gate, runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXECUTION_GATE_PASS
        )
        acceptable = sum(
            1
            for r in rows
            if runner.is_executive_shareholding_first_slice_acceptable(
                r, summaries[r.case_id]
            )
        )
        self.assertEqual(acceptable, 4)

    def test_live_report_schema_and_des001_row(self) -> None:
        if not os.path.isfile(self.LIVE_REPORT):
            self.skipTest("live report not present")
        with open(self.LIVE_REPORT, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.assertEqual(
                list(reader.fieldnames or []),
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_LIVE_REPORT_COLUMNS,
            )
            rows = list(reader)
        self.assertEqual(len(rows), 5)
        by_id = {r["case_id"]: r for r in rows}
        self.assertEqual(by_id["DES001"]["acceptable"], "no")
        self.assertEqual(by_id["DES001"]["failure_type"], "expectation_mismatch")
        self.assertEqual(by_id["DES001"]["retrieval_status"], "empty_but_valid")
        for case_id in ("DES002", "DES003", "DES004", "DES005"):
            self.assertEqual(by_id[case_id]["acceptable"], "yes")
            self.assertEqual(by_id[case_id]["failure_type"], "")

    def test_quality_report_schema_matches_live_acceptable(self) -> None:
        if not os.path.isfile(self.QUALITY_REPORT):
            self.skipTest("quality report not present")
        with open(self.QUALITY_REPORT, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.assertEqual(
                list(reader.fieldnames or []),
                runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_QUALITY_REPORT_COLUMNS,
            )
            q_rows = {r["case_id"]: r for r in reader}
        with open(self.LIVE_REPORT, newline="", encoding="utf-8") as f:
            live_rows = {r["case_id"]: r for r in csv.DictReader(f)}
        for case_id in runner.EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ALLOWED_CASE_IDS:
            self.assertEqual(
                q_rows[case_id]["acceptable"], live_rows[case_id]["acceptable"]
            )
            self.assertEqual(
                q_rows[case_id]["failure_type"], live_rows[case_id]["failure_type"]
            )

    def test_outcome_ledger_schema_and_cross_check(self) -> None:
        if not os.path.isfile(self.OUTCOME_LEDGER):
            self.skipTest("outcome ledger not present")
        expected_cols = [
            "case_id",
            "company_code",
            "company_name",
            "time_mark",
            "vary_type",
            "expected_behavior",
            "retrieval_status",
            "quality_status",
            "record_count",
            "outcome",
            "acceptable",
            "failure_type",
            "cninfo_request_count",
            "notes",
        ]
        with open(self.OUTCOME_LEDGER, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.assertEqual(list(reader.fieldnames or []), expected_cols)
            ledger = {r["case_id"]: r for r in reader}
        self.assertEqual(len(ledger), 5)
        self.assertEqual(ledger["DES001"]["acceptable"], "no")
        self.assertEqual(ledger["DES001"]["failure_type"], "expectation_mismatch")
        self.assertEqual(ledger["DES001"]["outcome"], "empty_but_valid")
        for case_id in ("DES002", "DES003", "DES004", "DES005"):
            self.assertEqual(ledger[case_id]["acceptable"], "yes")

    def test_closure_artifacts_present_and_des001_caveat(self) -> None:
        for path in (
            self.CLOSURE_METRICS,
            self.CAVEAT_LEDGER,
            self.EFFECTIVE_RESULT,
        ):
            self.assertTrue(os.path.isfile(path), msg=path)
        with open(self.CAVEAT_LEDGER, newline="", encoding="utf-8") as f:
            caveats = list(csv.DictReader(f))
        des001 = next(c for c in caveats if c["caveat_id"] == "CAV-DES-004")
        self.assertEqual(des001["case_id"], "DES001")
        self.assertEqual(des001["company_code"], "002415")
        self.assertEqual(
            des001["caveat_type"], "expectation_mismatch_on_sparse_window"
        )
        self.assertIn("accept_with_caveat", des001["allowed_interpretation"])
        with open(self.CLOSURE_METRICS, newline="", encoding="utf-8") as f:
            metrics = {r["metric_name"]: r["value"] for r in csv.DictReader(f)}
        self.assertEqual(metrics["acceptable"], "4")
        self.assertEqual(metrics["CNINFO_during_closure"], "0")
        self.assertEqual(metrics["closure_gate"], "PASS_WITH_CAVEAT")
        with open(self.EFFECTIVE_RESULT, newline="", encoding="utf-8") as f:
            eff = {r["case_id"]: r for r in csv.DictReader(f)}
        self.assertEqual(eff["DES001"]["acceptable"], "no")
        self.assertEqual(
            eff["DES001"]["failure_type"],
            "expectation_mismatch_on_sparse_window",
        )


if __name__ == "__main__":
    unittest.main()
