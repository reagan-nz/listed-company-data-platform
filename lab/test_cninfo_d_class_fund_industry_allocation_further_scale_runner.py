#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 fund_industry_allocation further-scale runner 测试（无 CNINFO · 无 live 执行）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_fund_industry_allocation_further_scale_runner.py
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

import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

BASE_DIR = runner.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_tiny_live_validation.py")
UNIVERSE_CSV = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FURTHER_SCALE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FURTHER_SCALE_OUTPUT_ROOT
FIRST_SLICE_OUTPUT_ROOT = (
    runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT
)
NEXT_SLICE_OUTPUT_ROOT = (
    runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_NEXT_SLICE_OUTPUT_ROOT
)
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
SD_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT
AT_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT
AT_NEXT_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_NEXT_SLICE_OUTPUT_ROOT
SD_NEXT_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_NEXT_SLICE_OUTPUT_ROOT
ES_OUTPUT_ROOT = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT

VALIDATION = os.path.join(BASE_DIR, "outputs", "validation")
FIRST_SLICE_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv",
)
NEXT_SLICE_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv",
)
AT_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv",
)
SD_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv",
)
AT_DRYRUN_REPORT = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_next_slice",
    "reports",
    "d_class_abnormal_trading_next_slice_dryrun_report.csv",
)
SD_DRYRUN_REPORT = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_data_next_slice",
    "reports",
    "d_class_shareholder_data_next_slice_dryrun_report.csv",
)
EXPECTED_FIRST_SLICE_LOCK_SHA256 = (
    "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
)
EXPECTED_NEXT_SLICE_LOCK_SHA256 = (
    "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
)
EXPECTED_AT_NEXT_LOCK_SHA256 = (
    "4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6"
)
EXPECTED_SD_NEXT_LOCK_SHA256 = (
    "c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f"
)
EXPECTED_AT_DRYRUN_SHA256 = (
    "51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497"
)
EXPECTED_SD_DRYRUN_SHA256 = (
    "2b74aac55299bc844e7df49725ad9ccf1f9c4dfbfc7db403f026412faf177362"
)
EXPECTED_FURTHER_SCALE_LOCK_SHA256 = (
    "398494f1cf6a6cf00637b82d6e3f5c38ae21671a4b47324fd1ee2262df92e9f1"
)
AT_FIRST_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv",
)
SD_FIRST_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv",
)
EXPECTED_AT_FIRST_LOCK_SHA256 = (
    "d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2"
)
EXPECTED_SD_FIRST_LOCK_SHA256 = (
    "06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5"
)
EXPECTED_AT_DRYRUN_SUMMARY_SHA256 = (
    "7fae1ccaacf31cbb254e51fc4b5a139554f40185eacd29ed692b1ce9320bb624"
)
EXPECTED_SD_DRYRUN_SUMMARY_SHA256 = (
    "86ffa6df3b59a5aa0ee8573a109947998f42aca879a7d7f0fddb2e8f1e8d38dc"
)
DRYRUN_REPORT = os.path.join(
    OUTPUT_ROOT,
    "reports",
    "d_class_fund_industry_allocation_further_scale_dryrun_report.csv",
)
DRYRUN_SUMMARY = os.path.join(
    OUTPUT_ROOT,
    "reports",
    "d_class_fund_industry_allocation_further_scale_dryrun_summary.md",
)
AT_DRYRUN_SUMMARY = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_next_slice",
    "reports",
    "d_class_abnormal_trading_next_slice_dryrun_summary.md",
)
SD_DRYRUN_SUMMARY = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_data_next_slice",
    "reports",
    "d_class_shareholder_data_next_slice_dryrun_summary.md",
)

BASE_ARGS = [
    "--dry-run",
    "--fund-industry-allocation-further-scale",
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


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


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


class TestFundIndustryAllocationFurtherScaleRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_request_count_total=3", result.stdout)
        self.assertIn(
            "d_class_fund_industry_allocation_further_scale_runner_extension_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_fund_industry_allocation_further_scale_live_path_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_fund_industry_allocation_further_scale_live_gate=NOT_APPROVED",
            result.stdout,
        )

    def test_dry_run_planned_ok_five_of_five(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        report = os.path.join(
            OUTPUT_ROOT,
            "reports",
            "d_class_fund_industry_allocation_further_scale_dryrun_report.csv",
        )
        with open(report, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        self.assertEqual({r["case_id"] for r in rows}, set(runner.FUND_INDUSTRY_ALLOCATION_FURTHER_SCALE_ALLOWED_CASE_IDS))
        for row in rows:
            self.assertEqual(row["dryrun_status"], "planned_ok")
            self.assertEqual(row["cninfo_call_planned"], "shared")

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--fund-industry-allocation-further-scale",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_further_scale_universe_size_must_equal_5",
                result.stderr,
            )

    def test_wrong_industry_code_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[0]["industry_code"] = "C26"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_industry.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--fund-industry-allocation-further-scale",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_further_scale_industry_code_mismatch",
                result.stderr,
            )

    def test_wrong_anchor_rdate_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[2]["anchor_rdate"] = "20240101"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--fund-industry-allocation-further-scale",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_further_scale_anchor_rdate_mismatch",
                result.stderr,
            )

    def test_component_must_be_fund_industry_allocation(self) -> None:
        rows = _read_universe_rows()
        rows[1]["component"] = "shareholder_data"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--fund-industry-allocation-further-scale",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "fund_industry_allocation_further_scale_component_must_be_fund_industry_allocation",
                result.stderr,
            )

    def test_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--fund-industry-allocation-further-scale",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "v1_output_root_write_blocked_for_fund_industry_allocation_further_scale",
            result.stderr,
        )

    def test_first_slice_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--fund-industry-allocation-further-scale",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                FIRST_SLICE_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "fund_industry_allocation_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_next_slice_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--fund-industry-allocation-further-scale",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                NEXT_SLICE_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "fund_industry_allocation_next_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_at_sd_next_output_roots_write_blocked(self) -> None:
        for root, token in (
            (AT_NEXT_OUTPUT_ROOT, "abnormal_trading_next_slice_output_root_write_blocked"),
            (SD_NEXT_OUTPUT_ROOT, "shareholder_data_next_slice_output_root_write_blocked"),
            (AT_OUTPUT_ROOT, "abnormal_trading_first_slice_output_root_write_blocked"),
            (SD_OUTPUT_ROOT, "shareholder_data_first_slice_output_root_write_blocked"),
            (ES_OUTPUT_ROOT, "executive_shareholding_first_slice_output_root_write_blocked"),
        ):
            result = _run(
                [
                    "--dry-run",
                    "--fund-industry-allocation-further-scale",
                    "--universe-csv",
                    UNIVERSE_CSV,
                    "--output-root",
                    root,
                ]
            )
            self.assertEqual(result.returncode, 2, msg=root)
            self.assertIn(token, result.stderr, msg=root)

    def test_mixed_mode_with_next_slice_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--fund-industry-allocation-next-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "fund_industry_allocation_further_scale_incompatible_with_other_modes",
            result.stderr,
        )

    def test_mixed_mode_with_first_slice_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--fund-industry-allocation-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "fund_industry_allocation_further_scale_incompatible_with_other_modes",
            result.stderr,
        )

    def test_wrong_approval_flag_blocked(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-fund-industry-allocation-next-slice"]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "wrong_approval_flag_for_fund_industry_allocation_further_scale",
            result.stderr,
        )

    def test_live_without_approval_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--fund-industry-allocation-further-scale",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_fund_industry_allocation_further_scale_required",
            result.stderr,
        )

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(
            hasattr(runner, "execute_fund_industry_allocation_further_scale_live")
        )
        self.assertTrue(
            callable(runner.execute_fund_industry_allocation_further_scale_live)
        )

    def test_shared_plan_equals_three(self) -> None:
        self.assertEqual(
            runner.compute_fund_industry_allocation_further_scale_planned_shared(),
            3,
        )
        self.assertEqual(
            runner.build_fund_industry_allocation_further_scale_plan(),
            ["default", "rdate_20260331", "rdate_20251231"],
        )

    def test_empty_but_valid_acceptable_rules(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        rows = runner.load_fund_industry_allocation_further_scale_universe(UNIVERSE_CSV)
        by_id = {r.case_id: r for r in rows}
        self.assertTrue(
            runner.is_fund_industry_allocation_further_scale_acceptable(
                by_id["DFIA201"], summary
            )
        )
        self.assertFalse(
            runner.is_fund_industry_allocation_further_scale_acceptable(
                by_id["DFIA202"], summary
            )
        )
        self.assertFalse(
            runner.is_fund_industry_allocation_further_scale_acceptable(
                by_id["DFIA203"], summary
            )
        )
        self.assertTrue(
            runner.is_fund_industry_allocation_further_scale_acceptable(
                by_id["DFIA204"], summary
            )
        )
        self.assertTrue(
            runner.is_fund_industry_allocation_further_scale_acceptable(
                by_id["DFIA205"], summary
            )
        )

    def test_frozen_locks_and_dryrun_roots(self) -> None:
        self.assertEqual(
            _sha256_file(FIRST_SLICE_LOCK), EXPECTED_FIRST_SLICE_LOCK_SHA256
        )
        self.assertEqual(
            _sha256_file(NEXT_SLICE_LOCK), EXPECTED_NEXT_SLICE_LOCK_SHA256
        )
        self.assertEqual(_sha256_file(AT_NEXT_LOCK), EXPECTED_AT_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_NEXT_LOCK), EXPECTED_SD_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(AT_DRYRUN_REPORT), EXPECTED_AT_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(SD_DRYRUN_REPORT), EXPECTED_SD_DRYRUN_SHA256)

    def test_live_with_approval_mock_shared_path_cninfo_zero(self) -> None:
        """离线 mock live：3 次共享探针 + 粗粒度 F001V 过滤 · 不触网 · CNINFO=0。"""
        rows = runner.load_fund_industry_allocation_further_scale_universe(UNIVERSE_CSV)
        call_ids: list[str] = []

        def _fake_cninfo_request(session, source_cfg, params_override, stats, case_id):
            call_ids.append(case_id)
            self.assertEqual(
                str(source_cfg.get("params_location") or "").lower(),
                "form",
            )
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = (
                stats.case_request_counts.get(case_id, 0) + 1
            )
            if case_id == "default":
                self.assertEqual(params_override, {})
                return (
                    {
                        "data": {
                            "records": [
                                {
                                    "F001V": "B",
                                    "F002V": "采矿业",
                                    "ENDDATE": "2026-06-30",
                                    "F003N": 2,
                                    "F004N": 0.3,
                                    "F005N": 0.4,
                                },
                                {
                                    "F001V": "A",
                                    "F002V": "农、林、牧、渔业",
                                    "ENDDATE": "2026-06-30",
                                    "F003N": 1,
                                    "F004N": 0.1,
                                    "F005N": 0.2,
                                },
                            ]
                        }
                    },
                    200,
                    "",
                )
            if case_id == "rdate_20260331":
                self.assertEqual(params_override, {"rdate": "20260331"})
                return (
                    {
                        "data": {
                            "records": [
                                {
                                    "F001V": "A",
                                    "F002V": "农、林、牧、渔业",
                                    "ENDDATE": "2026-03-31",
                                    "F003N": 3,
                                    "F004N": 0.5,
                                    "F005N": 0.6,
                                }
                            ]
                        }
                    },
                    200,
                    "",
                )
            if case_id == "rdate_20251231":
                self.assertEqual(params_override, {"rdate": "20251231"})
                return (
                    {
                        "data": {
                            "records": [
                                {
                                    "F001V": "A",
                                    "F002V": "农、林、牧、渔业",
                                    "ENDDATE": "2025-12-31",
                                    "F003N": 1,
                                    "F004N": 0.1,
                                    "F005N": 0.2,
                                },
                                {
                                    "F001V": "B",
                                    "F002V": "采矿业",
                                    "ENDDATE": "2025-12-31",
                                    "F003N": 2,
                                    "F004N": 0.2,
                                    "F005N": 0.3,
                                },
                            ]
                        }
                    },
                    200,
                    "",
                )
            self.fail(f"unexpected probe {case_id}")

        with tempfile.TemporaryDirectory() as tmp:
            out_root = os.path.join(
                tmp, "cninfo_d_class_fund_industry_allocation_further_scale"
            )
            output_paths = runner.ensure_output_layout(out_root, "live")
            with mock.patch(
                "run_cninfo_d_class_tiny_live_validation._cninfo_request",
                side_effect=_fake_cninfo_request,
            ), mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                rc = runner.execute_fund_industry_allocation_further_scale_live(
                    rows, output_paths
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertEqual(rc, 0)
            self.assertEqual(
                call_ids, ["default", "rdate_20260331", "rdate_20251231"]
            )
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_fund_industry_allocation_further_scale_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = {r["case_id"]: r for r in csv.DictReader(f)}
            self.assertEqual(len(live_rows), 5)
            for case_id in ("DFIA201", "DFIA202", "DFIA203", "DFIA204", "DFIA205"):
                self.assertEqual(live_rows[case_id]["acceptable"], "yes")


class TestFundIndustryAllocationFurtherScaleDfm40DryrunClosure(unittest.TestCase):
    """D-FM-40 FIA further-scale dry-run offline closure：只读复核 + freeze（无 CNINFO · 无 dry-run 重写）。"""

    CLOSURE_METRICS = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_further_scale_dryrun_closure_metrics.csv",
    )
    CAVEAT_LEDGER = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_further_scale_runner_final_caveat_ledger.csv",
    )
    FREEZE_LEDGER = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_further_scale_dryrun_artifact_freeze_ledger.csv",
    )
    CLOSURE_MATRIX = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_dfm40_further_scale_dryrun_closure_matrix_20260715.csv",
    )
    CLOSURE_DECISION = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_further_scale_dryrun_closure_decision.md",
    )
    CLOSURE_SUMMARY = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_further_scale_dryrun_closure_summary.md",
    )
    CLOSURE_EVIDENCE = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_dfm40_further_scale_dryrun_offline_closure_20260715.md",
    )
    POST_NEXT = os.path.join(
        VALIDATION,
        "cninfo_d_class_fund_industry_allocation_further_scale_post_dryrun_closure_next_step_recommendation.md",
    )
    LIVE_REPORT = os.path.join(
        OUTPUT_ROOT,
        "reports",
        "d_class_fund_industry_allocation_further_scale_live_report.csv",
    )

    # D-FM-39 冻结的 dry-run 产物 sha256；D-FM-40 不得改写
    DRYRUN_ARTIFACT_SHA256 = {
        "dryrun_report": (
            "fc7cfc51493c426d0db1608aad09b0dc4a7755c0019f8d822a46e40fa85fefd4"
        ),
        "dryrun_summary": (
            "b226006cf6a8008541ae391473740e184dc9549dd3d0398624bd6fe1b8755bc6"
        ),
        "planned_snapshot_DFIA201": (
            "e100d4e02e83fdaef856a935fb7fc373a78bd972b3ac8b14b8d733e8aff10ee5"
        ),
        "planned_snapshot_DFIA202": (
            "17e480c33545bf04c1cd6f9afd47d7096ac3c1fadff88a695ace7dae229fad60"
        ),
        "planned_snapshot_DFIA203": (
            "fbbb01e131ef8c6c13ae0f87f16ae90b09f921f46e766961ca18626ae3c7ffb2"
        ),
        "planned_snapshot_DFIA204": (
            "2cc29a0ff7daba871522a7cb08bce2a5149432f124c1aa778f8e9d302781602c"
        ),
        "planned_snapshot_DFIA205": (
            "62b5ac695fec2fc9fad5026159a62a7b7cf3a5db8608d0f595842ec56d490654"
        ),
    }

    def test_closure_artifacts_present_and_caveats(self) -> None:
        for path in (
            self.CLOSURE_METRICS,
            self.CAVEAT_LEDGER,
            self.FREEZE_LEDGER,
            self.CLOSURE_MATRIX,
            self.CLOSURE_DECISION,
            self.CLOSURE_SUMMARY,
            self.CLOSURE_EVIDENCE,
            self.POST_NEXT,
        ):
            self.assertTrue(os.path.isfile(path), msg=path)
        with open(self.CAVEAT_LEDGER, newline="", encoding="utf-8") as f:
            caveats = {c["caveat_id"]: c for c in csv.DictReader(f)}
        self.assertIn("CAV-FIA-FS-R01", caveats)
        self.assertEqual(caveats["CAV-FIA-FS-R01"]["caveat_type"], "s4_dryrun_not_live")
        self.assertIn("bare PASS", caveats["CAV-FIA-FS-R01"]["forbidden_interpretation"])
        self.assertEqual(
            caveats["CAV-FIA-FS-R03"]["caveat_type"], "shared_probe_not_found_path"
        )
        self.assertEqual(
            caveats["CAV-FIA-FS-R06"]["caveat_type"], "further_scale_live_not_flipped"
        )
        with open(self.CLOSURE_METRICS, newline="", encoding="utf-8") as f:
            metrics = {r["metric_name"]: r["value"] for r in csv.DictReader(f)}
        self.assertEqual(metrics["planned_ok"], "5")
        self.assertEqual(metrics["planned_shared_cninfo_requests"], "3")
        self.assertEqual(metrics["CNINFO_during_dfm40_closure"], "0")
        self.assertEqual(metrics["s4_dryrun_closure_gate"], "PASS_OFFLINE")
        self.assertEqual(metrics["live_gate"], "NOT_APPROVED")
        self.assertEqual(metrics["execution_gate"], "NOT_APPLICABLE")
        self.assertEqual(metrics["commit_boundary_gate"], "READY_FOR_COMMIT_REVIEW")
        self.assertEqual(metrics["live_report_present"], "no")
        with open(self.CLOSURE_MATRIX, newline="", encoding="utf-8") as f:
            matrix = {r["case_id"]: r for r in csv.DictReader(f)}
        self.assertEqual(len(matrix), 5)
        for case_id in ("DFIA201", "DFIA202", "DFIA203", "DFIA204", "DFIA205"):
            self.assertEqual(matrix[case_id]["dryrun_status"], "planned_ok")
            self.assertEqual(matrix[case_id]["cninfo_called"], "false")
            self.assertEqual(
                matrix[case_id]["live_found_path_DFIA201_205"], "NOT_PROVEN"
            )
        self.assertEqual(matrix["DFIA202"]["expected_behavior"], "captured_normal")
        self.assertEqual(matrix["DFIA201"]["shared_probe_key"], "default")
        self.assertEqual(matrix["DFIA203"]["shared_probe_key"], "rdate_20251231")

    def test_frozen_dryrun_artifacts_and_locks(self) -> None:
        self.assertFalse(os.path.isfile(self.LIVE_REPORT))
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        self.assertEqual(
            _sha256_file(DRYRUN_REPORT),
            self.DRYRUN_ARTIFACT_SHA256["dryrun_report"],
        )
        self.assertEqual(
            _sha256_file(DRYRUN_SUMMARY),
            self.DRYRUN_ARTIFACT_SHA256["dryrun_summary"],
        )
        for case_id in ("DFIA201", "DFIA202", "DFIA203", "DFIA204", "DFIA205"):
            path = os.path.join(
                OUTPUT_ROOT,
                "planned_snapshots",
                f"{case_id}_fund_industry_allocation.json",
            )
            self.assertTrue(os.path.isfile(path), msg=path)
            key = f"planned_snapshot_{case_id}"
            self.assertEqual(
                _sha256_file(path), self.DRYRUN_ARTIFACT_SHA256[key], msg=key
            )
        with open(self.FREEZE_LEDGER, newline="", encoding="utf-8") as f:
            freeze_rows = list(csv.DictReader(f))
        freeze_by_role = {r["artifact_role"]: r for r in freeze_rows}
        for role, expected in self.DRYRUN_ARTIFACT_SHA256.items():
            self.assertEqual(freeze_by_role[role]["sha256"], expected, msg=role)
            self.assertEqual(freeze_by_role[role]["freeze_policy"], "frozen_read_only")
        self.assertEqual(_sha256_file(UNIVERSE_CSV), EXPECTED_FURTHER_SCALE_LOCK_SHA256)
        self.assertEqual(
            _sha256_file(FIRST_SLICE_LOCK), EXPECTED_FIRST_SLICE_LOCK_SHA256
        )
        self.assertEqual(
            _sha256_file(NEXT_SLICE_LOCK), EXPECTED_NEXT_SLICE_LOCK_SHA256
        )
        self.assertEqual(_sha256_file(AT_NEXT_LOCK), EXPECTED_AT_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_NEXT_LOCK), EXPECTED_SD_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(AT_FIRST_LOCK), EXPECTED_AT_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_FIRST_LOCK), EXPECTED_SD_FIRST_LOCK_SHA256)
        # AT/SD next-slice dry-run 根只读确认（本任务不得 mutate）
        self.assertEqual(_sha256_file(AT_DRYRUN_REPORT), EXPECTED_AT_DRYRUN_SHA256)
        self.assertEqual(
            _sha256_file(AT_DRYRUN_SUMMARY), EXPECTED_AT_DRYRUN_SUMMARY_SHA256
        )
        self.assertEqual(_sha256_file(SD_DRYRUN_REPORT), EXPECTED_SD_DRYRUN_SHA256)
        self.assertEqual(
            _sha256_file(SD_DRYRUN_SUMMARY), EXPECTED_SD_DRYRUN_SUMMARY_SHA256
        )
        self.assertEqual(
            _sha256_file(AT_DRYRUN_REPORT),
            freeze_by_role["at_next_dryrun_report"]["sha256"],
        )
        self.assertEqual(
            _sha256_file(SD_DRYRUN_REPORT),
            freeze_by_role["sd_next_dryrun_report"]["sha256"],
        )

    def test_dryrun_report_readonly_five_of_five(self) -> None:
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
        shared = {r["shared_probe_key"] for r in rows}
        self.assertEqual(
            shared, {"default", "rdate_20260331", "rdate_20251231"}
        )
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("planned_shared_cninfo_requests | **3**", content)
        self.assertIn("NOT APPROVED for live", content)
        self.assertIn("20260331", content)
        self.assertIn("20251231", content)
        with open(self.CLOSURE_EVIDENCE, encoding="utf-8") as f:
            evidence = f.read()
        self.assertIn("s4_dryrun_closure_gate = PASS_OFFLINE", evidence)
        self.assertIn("cninfo_calls = 0", evidence)
        self.assertIn("further_scale_live_flipped = false", evidence)
        self.assertIn("at_next_live_flipped = false", evidence)
        self.assertIn("sd_next_live_flipped = false", evidence)
        self.assertIn("NOT verified", evidence)
        self.assertIn("NOT production_ready", evidence)
        self.assertIn("不使用：** bare PASS", evidence)
        self.assertIn("ready_for_commit = true", evidence)
        with open(self.POST_NEXT, encoding="utf-8") as f:
            post = f.read()
        self.assertIn("equity_pledge_or_es_or_shareholder_change", post)
        self.assertIn("recommended_next_offline", post)


if __name__ == "__main__":
    unittest.main()
