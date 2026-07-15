#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 shareholder_data next-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_shareholder_data_next_slice_runner.py
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
UNIVERSE_CSV = runner.DEFAULT_SHAREHOLDER_DATA_NEXT_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_NEXT_SLICE_OUTPUT_ROOT
DRYRUN_REPORT = runner.SHAREHOLDER_DATA_NEXT_SLICE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.SHAREHOLDER_DATA_NEXT_SLICE_DRYRUN_SUMMARY_MD
FIRST_SLICE_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
AT_FIRST_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT
AT_NEXT_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_NEXT_SLICE_OUTPUT_ROOT
FIA_FIRST_OUTPUT_ROOT = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT
FIA_NEXT_OUTPUT_ROOT = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_NEXT_SLICE_OUTPUT_ROOT
ES_OUTPUT_ROOT = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT

AT_FIRST_LOCK = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv",
)
AT_NEXT_LOCK = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv",
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

# D-FM-32/33 冻结 lock sha256；本任务不得 mutate
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
    "--shareholder-data-next-slice",
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


class TestShareholderDataNextSliceRunner(unittest.TestCase):
    def test_dry_run_calls_cninfo_zero_times(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            result = _run(BASE_ARGS)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
        self.assertIn("cninfo_calls=0", result.stdout)
        self.assertIn("planned_request_count_total=2", result.stdout)
        self.assertIn(
            "d_class_shareholder_data_next_slice_runner_extension_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_shareholder_data_next_slice_live_path_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_shareholder_data_next_slice_live_gate=NOT_APPROVED",
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
                    "--shareholder-data-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_data_next_slice_universe_size_must_equal_5",
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
                    "--shareholder-data-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "forbidden_company_code_in_shareholder_data_next_slice_universe",
                result.stderr,
            )

    def test_wrong_anchor_rdate_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[1]["anchor_rdate"] = "20241231"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--shareholder-data-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_data_next_slice_anchor_rdate_not_in_allowed_set",
                result.stderr,
            )

    def test_case_anchor_mismatch_blocked(self) -> None:
        rows = _read_universe_rows()
        # DSD101 必须是 20260331
        rows[0]["anchor_rdate"] = "20251231"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "mismatch_anchor.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--shareholder-data-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_data_next_slice_anchor_rdate_mismatch",
                result.stderr,
            )

    def test_component_must_be_shareholder_data(self) -> None:
        rows = _read_universe_rows()
        rows[2]["component"] = "abnormal_trading"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--shareholder-data-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_data_next_slice_component_must_be_shareholder_data",
                result.stderr,
            )

    def test_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-data-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "v1_output_root_write_blocked_for_shareholder_data_next_slice",
            result.stderr,
        )

    def test_first_slice_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-data-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                FIRST_SLICE_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_data_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_at_next_slice_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-data-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                AT_NEXT_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "abnormal_trading_next_slice_output_root_write_blocked",
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
            (
                AT_FIRST_OUTPUT_ROOT,
                "abnormal_trading_first_slice_output_root_write_blocked",
            ),
        ):
            with self.subTest(root=root):
                result = _run(
                    [
                        "--dry-run",
                        "--shareholder-data-next-slice",
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
                "--shareholder-data-next-slice",
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
        result = _run(BASE_ARGS + ["--shareholder-data-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_data_next_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_mixed_mode_with_at_next_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--abnormal-trading-next-slice"])
        self.assertEqual(result.returncode, 2)
        # main 先派发 AT next；任一侧 mixed 拦截均可
        self.assertTrue(
            "shareholder_data_next_slice_incompatible_with_other_modes" in result.stderr
            or "abnormal_trading_next_slice_incompatible_with_other_modes" in result.stderr,
            msg=result.stderr,
        )

    def test_wrong_approval_flag_blocked(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-shareholder-data-first-slice"]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "wrong_approval_flag_for_shareholder_data_next_slice",
            result.stderr,
        )

    def test_live_without_approval_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--shareholder-data-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_shareholder_data_next_slice_required",
            result.stderr,
        )

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(
            hasattr(runner, "execute_shareholder_data_next_slice_live")
        )
        self.assertTrue(callable(runner.execute_shareholder_data_next_slice_live))

    def test_shared_plan_equals_two(self) -> None:
        self.assertEqual(
            runner.compute_shareholder_data_next_slice_planned_shared(), 2
        )
        self.assertEqual(
            runner.build_shareholder_data_next_slice_plan(),
            [
                "rdate_report_period_20260331",
                "rdate_report_period_20251231",
            ],
        )

    def test_empty_but_valid_acceptable_rules(self) -> None:
        empty_summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        found_summary = {
            "retrieval_status": "found",
            "quality_status": "pass",
            "record_count": "1",
        }
        rows = runner.load_shareholder_data_next_slice_universe(UNIVERSE_CSV)
        by_id = {r.case_id: r for r in rows}
        self.assertTrue(
            runner.is_shareholder_data_next_slice_acceptable(
                by_id["DSD101"], found_summary
            )
        )
        self.assertTrue(
            runner.is_shareholder_data_next_slice_acceptable(
                by_id["DSD102"], empty_summary
            )
        )
        self.assertTrue(
            runner.is_shareholder_data_next_slice_acceptable(
                by_id["DSD105"], empty_summary
            )
        )

    def test_live_with_approval_mock_shared_path_cninfo_zero(self) -> None:
        """离线 mock live：2 次共享 rdate 探针 + SECCODE 过滤 · 不触网 · CNINFO=0。"""
        rows = runner.load_shareholder_data_next_slice_universe(UNIVERSE_CSV)
        call_ids: list[str] = []

        def _fake_cninfo_request(session, source_cfg, params_override, stats, case_id):
            call_ids.append(case_id)
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = (
                stats.case_request_counts.get(case_id, 0) + 1
            )
            rdate = params_override.get("rdate")
            self.assertIn(rdate, ("20260331", "20251231"))
            records = []
            if rdate == "20260331":
                records = [
                    {
                        "SECCODE": "000001",
                        "SECNAME": "平安银行",
                        "ENDDATE": "2026-03-31",
                        "F001N": 1,
                        "F002N": 1,
                        "F003N": 0,
                        "F004N": 1,
                        "F005N": 1,
                        "F006N": 0,
                    },
                    {
                        "SECCODE": "000895",
                        "SECNAME": "双汇发展",
                        "ENDDATE": "2026-03-31",
                        "F001N": 1,
                        "F002N": 1,
                        "F003N": 0,
                        "F004N": 1,
                        "F005N": 1,
                        "F006N": 0,
                    },
                    {
                        "SECCODE": "600519",
                        "SECNAME": "贵州茅台",
                        "ENDDATE": "2026-03-31",
                        "F001N": 1,
                        "F002N": 1,
                        "F003N": 0,
                        "F004N": 1,
                        "F005N": 1,
                        "F006N": 0,
                    },
                ]
            elif rdate == "20251231":
                records = [
                    {
                        "SECCODE": "002415",
                        "SECNAME": "海康威视",
                        "ENDDATE": "2025-12-31",
                        "F001N": 1,
                        "F002N": 1,
                        "F003N": 0,
                        "F004N": 1,
                        "F005N": 1,
                        "F006N": 0,
                    },
                ]
            return ({"data": {"records": records}}, 200, "")

        with tempfile.TemporaryDirectory() as tmp:
            out_root = os.path.join(
                tmp, "cninfo_d_class_shareholder_data_next_slice"
            )
            output_paths = runner.ensure_output_layout(out_root, "live")
            with mock.patch(
                "run_cninfo_d_class_tiny_live_validation._cninfo_request",
                side_effect=_fake_cninfo_request,
            ), mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                rc = runner.execute_shareholder_data_next_slice_live(
                    rows, output_paths
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertEqual(rc, 0)
            self.assertEqual(
                call_ids,
                [
                    "rdate_report_period_20260331",
                    "rdate_report_period_20251231",
                ],
            )
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_shareholder_data_next_slice_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = {r["case_id"]: r for r in csv.DictReader(f)}
            self.assertEqual(len(live_rows), 5)
            for case_id in ("DSD101", "DSD102", "DSD103", "DSD104"):
                self.assertEqual(live_rows[case_id]["acceptable"], "yes")
                self.assertEqual(live_rows[case_id]["retrieval_status"], "found")
            self.assertEqual(live_rows["DSD105"]["acceptable"], "yes")
            self.assertEqual(
                live_rows["DSD105"]["retrieval_status"], "empty_but_valid"
            )

    def test_dryrun_report_five_planned_ok_shared_two(self) -> None:
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
        by_id = {r["case_id"]: r for r in rows}
        self.assertEqual(
            by_id["DSD101"]["shared_probe_key"], "rdate_report_period_20260331"
        )
        self.assertEqual(
            by_id["DSD104"]["shared_probe_key"], "rdate_report_period_20251231"
        )
        self.assertTrue(
            all(
                r["planned_endpoint"] == runner.SHAREHOLDER_DATA_NEXT_SLICE_ENDPOINT
                for r in rows
            )
        )
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("planned_shared_cninfo_requests | **2**", content)
        self.assertIn("NOT APPROVED for live", content)
        self.assertIn("20260331", content)
        self.assertIn("20251231", content)
        self.assertIn("NOT_PROVEN", content)

    def test_default_universe_csv_rejected(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-data-next-slice",
                "--universe-csv",
                runner.DEFAULT_UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_data_next_slice_requires_explicit_universe_csv",
            result.stderr,
        )

    def test_frozen_locks_unchanged(self) -> None:
        self.assertEqual(_sha256_file(AT_FIRST_LOCK), AT_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(AT_NEXT_LOCK), AT_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_FIRST_LOCK), SD_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(UNIVERSE_CSV), SD_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_NEXT_LOCK), FIA_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_FIRST_LOCK), FIA_FIRST_LOCK_SHA256)

    def test_plan_helpers(self) -> None:
        rows = runner.load_shareholder_data_next_slice_universe(UNIVERSE_CSV)
        self.assertEqual(len(rows), 5)
        issues = runner.validate_shareholder_data_next_slice_universe(rows)
        self.assertEqual(issues, [])
        for row in rows:
            refs = runner.resolve_shareholder_data_next_slice_fixture_refs(row.case_id)
            self.assertTrue(refs)
            for ref in refs:
                self.assertTrue(os.path.isfile(ref), ref)


class TestShareholderDataNextSliceDfm34DryrunClosure(unittest.TestCase):
    """D-FM-34 SD next-slice dry-run offline closure：只读复核 + freeze（无 CNINFO · 无 dry-run 重写）。"""

    VALIDATION = os.path.join(BASE_DIR, "outputs", "validation")
    CLOSURE_METRICS = os.path.join(
        VALIDATION,
        "cninfo_d_class_shareholder_data_next_slice_dryrun_closure_metrics.csv",
    )
    CAVEAT_LEDGER = os.path.join(
        VALIDATION,
        "cninfo_d_class_shareholder_data_next_slice_runner_final_caveat_ledger.csv",
    )
    FREEZE_LEDGER = os.path.join(
        VALIDATION,
        "cninfo_d_class_shareholder_data_next_slice_dryrun_artifact_freeze_ledger.csv",
    )
    CLOSURE_MATRIX = os.path.join(
        VALIDATION,
        "cninfo_d_class_shareholder_data_dfm34_next_slice_dryrun_closure_matrix_20260715.csv",
    )
    CLOSURE_DECISION = os.path.join(
        VALIDATION,
        "cninfo_d_class_shareholder_data_next_slice_dryrun_closure_decision.md",
    )
    CLOSURE_SUMMARY = os.path.join(
        VALIDATION,
        "cninfo_d_class_shareholder_data_next_slice_dryrun_closure_summary.md",
    )
    CLOSURE_EVIDENCE = os.path.join(
        VALIDATION,
        "cninfo_d_class_shareholder_data_dfm34_next_slice_dryrun_offline_closure_20260715.md",
    )
    POST_NEXT = os.path.join(
        VALIDATION,
        "cninfo_d_class_shareholder_data_next_slice_post_dryrun_closure_next_step_recommendation.md",
    )
    LIVE_REPORT = os.path.join(
        OUTPUT_ROOT,
        "reports",
        "d_class_shareholder_data_next_slice_live_report.csv",
    )

    # D-FM-33 冻结的 dry-run 产物 sha256；D-FM-34 不得改写
    DRYRUN_ARTIFACT_SHA256 = {
        "dryrun_report": (
            "2b74aac55299bc844e7df49725ad9ccf1f9c4dfbfc7db403f026412faf177362"
        ),
        "dryrun_summary": (
            "86ffa6df3b59a5aa0ee8573a109947998f42aca879a7d7f0fddb2e8f1e8d38dc"
        ),
        "planned_snapshot_DSD101": (
            "7415dc2de66c75d162f7cd4f4c34e502a916a9218a35dff100b614e94d86c6a7"
        ),
        "planned_snapshot_DSD102": (
            "5bf06570d7635e62b13d6bfc3c14243dd30d13cb6ed38fce3ce6a9a6133c9c19"
        ),
        "planned_snapshot_DSD103": (
            "882ea7d32603725a2b83a3012649945300199a252c2fa56498790d25ad14c6e1"
        ),
        "planned_snapshot_DSD104": (
            "8f12fa0586b150643369d8514fd00cbcefa45822a67c63dffced63d17cd46d4d"
        ),
        "planned_snapshot_DSD105": (
            "1ae22919ae71676afaa62d56f5ff0b96aa8a793a8bb04c3fec4434650629f829"
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
        self.assertIn("CAV-SD-NS-R01", caveats)
        self.assertEqual(caveats["CAV-SD-NS-R01"]["caveat_type"], "s4_dryrun_not_live")
        self.assertIn("bare PASS", caveats["CAV-SD-NS-R01"]["forbidden_interpretation"])
        self.assertEqual(
            caveats["CAV-SD-NS-R03"]["caveat_type"], "unproven_rdate_20251231"
        )
        self.assertEqual(
            caveats["CAV-SD-NS-R06"]["caveat_type"], "at_next_live_not_flipped"
        )
        with open(self.CLOSURE_METRICS, newline="", encoding="utf-8") as f:
            metrics = {r["metric_name"]: r["value"] for r in csv.DictReader(f)}
        self.assertEqual(metrics["planned_ok"], "5")
        self.assertEqual(metrics["planned_shared_cninfo_requests"], "2")
        self.assertEqual(metrics["CNINFO_during_dfm34_closure"], "0")
        self.assertEqual(metrics["s4_dryrun_closure_gate"], "PASS_OFFLINE")
        self.assertEqual(metrics["live_gate"], "NOT_APPROVED")
        self.assertEqual(metrics["execution_gate"], "NOT_APPLICABLE")
        self.assertEqual(metrics["commit_boundary_gate"], "READY_FOR_COMMIT_REVIEW")
        self.assertEqual(metrics["live_report_present"], "no")
        with open(self.CLOSURE_MATRIX, newline="", encoding="utf-8") as f:
            matrix = {r["case_id"]: r for r in csv.DictReader(f)}
        self.assertEqual(len(matrix), 5)
        for case_id in ("DSD101", "DSD102", "DSD103", "DSD104", "DSD105"):
            self.assertEqual(matrix[case_id]["dryrun_status"], "planned_ok")
            self.assertEqual(matrix[case_id]["cninfo_called"], "false")
            self.assertEqual(matrix[case_id]["live_found_path_20251231"], "NOT_PROVEN")
        self.assertEqual(matrix["DSD105"]["expected_behavior"], "empty_but_valid")
        self.assertEqual(matrix["DSD104"]["anchor_rdate"], "20251231")

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
        for case_id in ("DSD101", "DSD102", "DSD103", "DSD104", "DSD105"):
            path = os.path.join(
                OUTPUT_ROOT, "planned_snapshots", f"{case_id}_shareholder_data.json"
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
        self.assertEqual(_sha256_file(AT_NEXT_LOCK), AT_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_FIRST_LOCK), SD_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(UNIVERSE_CSV), SD_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_NEXT_LOCK), FIA_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_FIRST_LOCK), FIA_FIRST_LOCK_SHA256)
        # AT next-slice dry-run 根只读确认（本任务不得 mutate）
        at_dryrun_report = os.path.join(
            AT_NEXT_OUTPUT_ROOT,
            "reports",
            "d_class_abnormal_trading_next_slice_dryrun_report.csv",
        )
        at_dryrun_summary = os.path.join(
            AT_NEXT_OUTPUT_ROOT,
            "reports",
            "d_class_abnormal_trading_next_slice_dryrun_summary.md",
        )
        self.assertEqual(
            _sha256_file(at_dryrun_report),
            freeze_by_role["at_next_dryrun_report"]["sha256"],
        )
        self.assertEqual(
            _sha256_file(at_dryrun_summary),
            freeze_by_role["at_next_dryrun_summary"]["sha256"],
        )

    def test_dryrun_report_readonly_five_of_five(self) -> None:
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
        shared = {r["shared_probe_key"] for r in rows}
        self.assertEqual(
            shared,
            {"rdate_report_period_20260331", "rdate_report_period_20251231"},
        )
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("planned_shared_cninfo_requests | **2**", content)
        self.assertIn("NOT APPROVED for live", content)
        self.assertIn("NOT_PROVEN", content)
        with open(self.CLOSURE_EVIDENCE, encoding="utf-8") as f:
            evidence = f.read()
        self.assertIn("s4_dryrun_closure_gate = PASS_OFFLINE", evidence)
        self.assertIn("cninfo_calls = 0", evidence)
        self.assertIn("at_next_slice_live_flipped = false", evidence)
        self.assertIn("NOT verified", evidence)
        self.assertIn("NOT production_ready", evidence)
        self.assertIn("不使用：** bare PASS", evidence)
        self.assertIn("ready_for_commit = true", evidence)


if __name__ == "__main__":
    unittest.main()
