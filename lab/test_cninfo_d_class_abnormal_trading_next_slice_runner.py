#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 abnormal_trading next-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_abnormal_trading_next_slice_runner.py
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
UNIVERSE_CSV = runner.DEFAULT_ABNORMAL_TRADING_NEXT_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_NEXT_SLICE_OUTPUT_ROOT
DRYRUN_REPORT = runner.ABNORMAL_TRADING_NEXT_SLICE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.ABNORMAL_TRADING_NEXT_SLICE_DRYRUN_SUMMARY_MD
FIRST_SLICE_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
SD_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT
FIA_FIRST_OUTPUT_ROOT = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT
FIA_NEXT_OUTPUT_ROOT = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_NEXT_SLICE_OUTPUT_ROOT
ES_OUTPUT_ROOT = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT

AT_FIRST_LOCK = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv",
)
SD_FIRST_LOCK = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv",
)
FIA_NEXT_LOCK = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv",
)
FIA_FIRST_LOCK = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv",
)
SD_NEXT_LOCK = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv",
)
SD_NEXT_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_NEXT_SLICE_OUTPUT_ROOT

# D-FM-30/31/34/35 冻结 lock sha256；本任务不得 mutate
AT_FIRST_LOCK_SHA256 = (
    "d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2"
)
AT_NEXT_LOCK_SHA256 = (
    "4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6"
)
SD_FIRST_LOCK_SHA256 = (
    "06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5"
)
SD_NEXT_LOCK_SHA256 = (
    "c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f"
)
FIA_NEXT_LOCK_SHA256 = (
    "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
)
FIA_FIRST_LOCK_SHA256 = (
    "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
)

BASE_ARGS = [
    "--dry-run",
    "--abnormal-trading-next-slice",
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


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class TestAbnormalTradingNextSliceRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_request_count_total=1", result.stdout)
        self.assertIn(
            "d_class_abnormal_trading_next_slice_runner_extension_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_abnormal_trading_next_slice_live_path_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_abnormal_trading_next_slice_live_gate=NOT_APPROVED",
            result.stdout,
        )

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--abnormal-trading-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "abnormal_trading_next_slice_universe_size_must_equal_5",
                result.stderr,
            )

    def test_forbidden_company_code_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[0]["company_code"] = "301259"
        rows[0]["company_name"] = "艾布鲁"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_code.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--abnormal-trading-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "forbidden_company_code_in_abnormal_trading_next_slice_universe",
                result.stderr,
            )

    def test_wrong_anchor_tdate_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[1]["anchor_tdate"] = "2026-07-04"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--abnormal-trading-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "abnormal_trading_next_slice_anchor_tdate_mismatch",
                result.stderr,
            )

    def test_forbidden_anchor_20260703_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[2]["anchor_tdate"] = "2026-07-03"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forbidden_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--abnormal-trading-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "abnormal_trading_next_slice_forbidden_anchor_tdate_20260703",
                result.stderr,
            )

    def test_component_must_be_abnormal_trading(self) -> None:
        rows = _read_universe_rows()
        rows[2]["component"] = "block_trade"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--abnormal-trading-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "abnormal_trading_next_slice_component_must_be_abnormal_trading",
                result.stderr,
            )

    def test_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--abnormal-trading-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "v1_output_root_write_blocked_for_abnormal_trading_next_slice",
            result.stderr,
        )

    def test_first_slice_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--abnormal-trading-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                FIRST_SLICE_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "abnormal_trading_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_shareholder_data_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--abnormal-trading-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                SD_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_data_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_fia_roots_write_blocked(self) -> None:
        for root, token in (
            (
                FIA_FIRST_OUTPUT_ROOT,
                "fund_industry_allocation_first_slice_output_root_write_blocked",
            ),
            (
                FIA_NEXT_OUTPUT_ROOT,
                "fund_industry_allocation_next_slice_output_root_write_blocked",
            ),
        ):
            with self.subTest(root=root):
                result = _run(
                    [
                        "--dry-run",
                        "--abnormal-trading-next-slice",
                        "--universe-csv",
                        UNIVERSE_CSV,
                        "--output-root",
                        root,
                    ]
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(token, result.stderr)

    def test_executive_shareholding_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--abnormal-trading-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                ES_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "executive_shareholding_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_mixed_mode_with_first_slice_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--abnormal-trading-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "abnormal_trading_next_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_mixed_mode_with_fia_next_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--fund-industry-allocation-next-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "abnormal_trading_next_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_wrong_approval_flag_blocked(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-abnormal-trading-first-slice"]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "wrong_approval_flag_for_abnormal_trading_next_slice",
            result.stderr,
        )

    def test_live_without_approval_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--abnormal-trading-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_abnormal_trading_next_slice_required",
            result.stderr,
        )

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(
            hasattr(runner, "execute_abnormal_trading_next_slice_live")
        )
        self.assertTrue(callable(runner.execute_abnormal_trading_next_slice_live))

    def test_shared_plan_equals_one(self) -> None:
        self.assertEqual(
            runner.compute_abnormal_trading_next_slice_planned_shared(), 1
        )
        self.assertEqual(
            runner.build_abnormal_trading_next_slice_plan(),
            ["single_day_paged_2026-07-02"],
        )

    def test_empty_but_valid_acceptable_rules(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        rows = runner.load_abnormal_trading_next_slice_universe(UNIVERSE_CSV)
        by_id = {r.case_id: r for r in rows}
        for case_id in ("DAT101", "DAT102", "DAT103", "DAT104", "DAT105"):
            self.assertTrue(
                runner.is_abnormal_trading_next_slice_acceptable(
                    by_id[case_id], summary
                ),
                msg=case_id,
            )

    def test_live_with_approval_mock_shared_path_cninfo_zero(self) -> None:
        """离线 mock live：1 次共享探针 + secCode 过滤 · 不触网 · CNINFO=0。"""
        rows = runner.load_abnormal_trading_next_slice_universe(UNIVERSE_CSV)
        call_ids: list[str] = []

        def _fake_cninfo_request(session, source_cfg, params_override, stats, case_id):
            call_ids.append(case_id)
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = (
                stats.case_request_counts.get(case_id, 0) + 1
            )
            self.assertEqual(
                params_override.get("sdate"),
                runner.ABNORMAL_TRADING_NEXT_SLICE_ANCHOR_TDATE,
            )
            self.assertEqual(
                params_override.get("edate"),
                runner.ABNORMAL_TRADING_NEXT_SLICE_ANCHOR_TDATE,
            )
            return (
                {
                    "marketList": [
                        {
                            "secCode": "000895",
                            "secName": "双汇发展",
                            "tradeTime": "2026-07-02",
                            "type": "涨幅偏离值达7%",
                        },
                        {
                            "secCode": "600000",
                            "secName": "浦发银行",
                            "tradeTime": "2026-07-02",
                            "type": "跌幅偏离值达7%",
                        },
                        {
                            "secCode": "002415",
                            "secName": "海康威视",
                            "tradeTime": "2026-07-02",
                            "type": "换手率达20%",
                        },
                        {
                            "secCode": "000001",
                            "secName": "平安银行",
                            "tradeTime": "2026-07-02",
                            "type": "连续三个交易日内涨幅偏离值累计达20%",
                        },
                    ]
                },
                200,
                "",
            )

        with tempfile.TemporaryDirectory() as tmp:
            out_root = os.path.join(
                tmp, "cninfo_d_class_abnormal_trading_next_slice"
            )
            output_paths = runner.ensure_output_layout(out_root, "live")
            with mock.patch(
                "run_cninfo_d_class_tiny_live_validation._cninfo_request",
                side_effect=_fake_cninfo_request,
            ), mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                rc = runner.execute_abnormal_trading_next_slice_live(
                    rows, output_paths
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertEqual(rc, 0)
            self.assertEqual(
                call_ids, [runner.ABNORMAL_TRADING_NEXT_SLICE_SHARED_PROBE_KEY]
            )
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_abnormal_trading_next_slice_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = {r["case_id"]: r for r in csv.DictReader(f)}
            self.assertEqual(len(live_rows), 5)
            for case_id in ("DAT101", "DAT102", "DAT103", "DAT104"):
                self.assertEqual(live_rows[case_id]["acceptable"], "yes")
                self.assertEqual(live_rows[case_id]["retrieval_status"], "found")
            self.assertEqual(live_rows["DAT105"]["acceptable"], "yes")
            self.assertEqual(
                live_rows["DAT105"]["retrieval_status"], "empty_but_valid"
            )

    def test_dryrun_report_five_planned_ok_shared_one(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
        self.assertEqual(
            sum(int(r["planned_request_count"]) for r in rows),
            5,
        )
        self.assertTrue(
            all(
                r["shared_probe_key"]
                == runner.ABNORMAL_TRADING_NEXT_SLICE_SHARED_PROBE_KEY
                for r in rows
            )
        )
        self.assertTrue(
            all(
                r["planned_endpoint"] == runner.ABNORMAL_TRADING_NEXT_SLICE_ENDPOINT
                for r in rows
            )
        )
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("planned_shared_cninfo_requests | **1**", content)
        self.assertIn("NOT APPROVED for live", content)
        self.assertIn("2026-07-02", content)
        self.assertIn("2026-07-03", content)

    def test_default_universe_csv_rejected(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--abnormal-trading-next-slice",
                "--universe-csv",
                runner.DEFAULT_UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "abnormal_trading_next_slice_requires_explicit_universe_csv",
            result.stderr,
        )

    def test_frozen_locks_unchanged(self) -> None:
        self.assertEqual(_sha256_file(AT_FIRST_LOCK), AT_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(UNIVERSE_CSV), AT_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_FIRST_LOCK), SD_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_NEXT_LOCK), SD_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_NEXT_LOCK), FIA_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_FIRST_LOCK), FIA_FIRST_LOCK_SHA256)

    def test_plan_helpers(self) -> None:
        rows = runner.load_abnormal_trading_next_slice_universe(UNIVERSE_CSV)
        self.assertEqual(len(rows), 5)
        issues = runner.validate_abnormal_trading_next_slice_universe(rows)
        self.assertEqual(issues, [])
        for row in rows:
            refs = runner.resolve_abnormal_trading_next_slice_fixture_refs(row.case_id)
            self.assertTrue(refs)
            for ref in refs:
                self.assertTrue(os.path.isfile(ref), ref)


class TestAbnormalTradingNextSliceDfm35DryrunClosure(unittest.TestCase):
    """D-FM-35 AT next-slice dry-run offline closure：只读复核 + freeze（无 CNINFO · 无 dry-run 重写）。"""

    VALIDATION = os.path.join(BASE_DIR, "outputs", "validation")
    CLOSURE_METRICS = os.path.join(
        VALIDATION,
        "cninfo_d_class_abnormal_trading_next_slice_dryrun_closure_metrics.csv",
    )
    CAVEAT_LEDGER = os.path.join(
        VALIDATION,
        "cninfo_d_class_abnormal_trading_next_slice_runner_final_caveat_ledger.csv",
    )
    FREEZE_LEDGER = os.path.join(
        VALIDATION,
        "cninfo_d_class_abnormal_trading_next_slice_dryrun_artifact_freeze_ledger.csv",
    )
    CLOSURE_MATRIX = os.path.join(
        VALIDATION,
        "cninfo_d_class_abnormal_trading_dfm35_next_slice_dryrun_closure_matrix_20260715.csv",
    )
    CLOSURE_DECISION = os.path.join(
        VALIDATION,
        "cninfo_d_class_abnormal_trading_next_slice_dryrun_closure_decision.md",
    )
    CLOSURE_SUMMARY = os.path.join(
        VALIDATION,
        "cninfo_d_class_abnormal_trading_next_slice_dryrun_closure_summary.md",
    )
    CLOSURE_EVIDENCE = os.path.join(
        VALIDATION,
        "cninfo_d_class_abnormal_trading_dfm35_next_slice_dryrun_offline_closure_20260715.md",
    )
    POST_NEXT = os.path.join(
        VALIDATION,
        "cninfo_d_class_abnormal_trading_next_slice_post_dryrun_closure_next_step_recommendation.md",
    )
    LIVE_REPORT = os.path.join(
        OUTPUT_ROOT,
        "reports",
        "d_class_abnormal_trading_next_slice_live_report.csv",
    )

    # D-FM-31 冻结的 dry-run 产物 sha256；D-FM-35 不得改写
    DRYRUN_ARTIFACT_SHA256 = {
        "dryrun_report": (
            "51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497"
        ),
        "dryrun_summary": (
            "7fae1ccaacf31cbb254e51fc4b5a139554f40185eacd29ed692b1ce9320bb624"
        ),
        "planned_snapshot_DAT101": (
            "f1fefd89417f00080d4a1f4c4692e08f7700941a91154679d7e9d0e1b2b96673"
        ),
        "planned_snapshot_DAT102": (
            "dae68e77544474d391491221998c9c4b266f8e7cfb9946480deb53aab3e4a976"
        ),
        "planned_snapshot_DAT103": (
            "80ef09cfd5bf29f14b36cd5750aebf03dd70051bb1cc91c592e7980e7727f5ff"
        ),
        "planned_snapshot_DAT104": (
            "8fc2906fa1a0ccbc4c4f902e83643ad572805309c6f11bee98476fe17cbeec5f"
        ),
        "planned_snapshot_DAT105": (
            "14f424d5ec83eb6765a3c537e2dc9854eece2348f9d26170b924c7d7bbaff9db"
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
        self.assertIn("CAV-AT-NS-R01", caveats)
        self.assertEqual(caveats["CAV-AT-NS-R01"]["caveat_type"], "s4_dryrun_not_live")
        self.assertIn("bare PASS", caveats["CAV-AT-NS-R01"]["forbidden_interpretation"])
        self.assertEqual(
            caveats["CAV-AT-NS-R03"]["caveat_type"], "shared_probe_not_found_path"
        )
        self.assertEqual(
            caveats["CAV-AT-NS-R06"]["caveat_type"], "at_sd_live_not_flipped"
        )
        with open(self.CLOSURE_METRICS, newline="", encoding="utf-8") as f:
            metrics = {r["metric_name"]: r["value"] for r in csv.DictReader(f)}
        self.assertEqual(metrics["planned_ok"], "5")
        self.assertEqual(metrics["planned_shared_cninfo_requests"], "1")
        self.assertEqual(metrics["CNINFO_during_dfm35_closure"], "0")
        self.assertEqual(metrics["s4_dryrun_closure_gate"], "PASS_OFFLINE")
        self.assertEqual(metrics["live_gate"], "NOT_APPROVED")
        self.assertEqual(metrics["execution_gate"], "NOT_APPLICABLE")
        self.assertEqual(metrics["commit_boundary_gate"], "READY_FOR_COMMIT_REVIEW")
        self.assertEqual(metrics["live_report_present"], "no")
        with open(self.CLOSURE_MATRIX, newline="", encoding="utf-8") as f:
            matrix = {r["case_id"]: r for r in csv.DictReader(f)}
        self.assertEqual(len(matrix), 5)
        for case_id in ("DAT101", "DAT102", "DAT103", "DAT104", "DAT105"):
            self.assertEqual(matrix[case_id]["dryrun_status"], "planned_ok")
            self.assertEqual(matrix[case_id]["cninfo_called"], "false")
            self.assertEqual(matrix[case_id]["live_found_path_DAT101_105"], "NOT_PROVEN")
        self.assertEqual(matrix["DAT105"]["expected_behavior"], "empty_but_valid")
        self.assertEqual(matrix["DAT101"]["anchor_tdate"], "2026-07-02")

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
        for case_id in ("DAT101", "DAT102", "DAT103", "DAT104", "DAT105"):
            path = os.path.join(
                OUTPUT_ROOT, "planned_snapshots", f"{case_id}_abnormal_trading.json"
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
        self.assertEqual(_sha256_file(AT_FIRST_LOCK), AT_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(UNIVERSE_CSV), AT_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_FIRST_LOCK), SD_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_NEXT_LOCK), SD_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_NEXT_LOCK), FIA_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_FIRST_LOCK), FIA_FIRST_LOCK_SHA256)
        # SD next-slice dry-run 根只读确认（本任务不得 mutate）
        sd_dryrun_report = os.path.join(
            SD_NEXT_OUTPUT_ROOT,
            "reports",
            "d_class_shareholder_data_next_slice_dryrun_report.csv",
        )
        sd_dryrun_summary = os.path.join(
            SD_NEXT_OUTPUT_ROOT,
            "reports",
            "d_class_shareholder_data_next_slice_dryrun_summary.md",
        )
        self.assertEqual(
            _sha256_file(sd_dryrun_report),
            freeze_by_role["sd_next_dryrun_report"]["sha256"],
        )
        self.assertEqual(
            _sha256_file(sd_dryrun_summary),
            freeze_by_role["sd_next_dryrun_summary"]["sha256"],
        )

    def test_dryrun_report_readonly_five_of_five(self) -> None:
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
        shared = {r["shared_probe_key"] for r in rows}
        self.assertEqual(shared, {runner.ABNORMAL_TRADING_NEXT_SLICE_SHARED_PROBE_KEY})
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("planned_shared_cninfo_requests | **1**", content)
        self.assertIn("NOT APPROVED for live", content)
        self.assertIn("2026-07-02", content)
        self.assertIn("2026-07-03", content)
        with open(self.CLOSURE_EVIDENCE, encoding="utf-8") as f:
            evidence = f.read()
        self.assertIn("s4_dryrun_closure_gate = PASS_OFFLINE", evidence)
        self.assertIn("cninfo_calls = 0", evidence)
        self.assertIn("at_next_slice_live_flipped = false", evidence)
        self.assertIn("sd_next_slice_live_flipped = false", evidence)
        self.assertIn("NOT verified", evidence)
        self.assertIn("NOT production_ready", evidence)
        self.assertIn("不使用：** bare PASS", evidence)
        self.assertIn("ready_for_commit = true", evidence)


if __name__ == "__main__":
    unittest.main()
