#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 equity_pledge next-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_equity_pledge_next_slice_runner.py
"""

from __future__ import annotations

import csv
import hashlib
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
UNIVERSE_CSV = runner.DEFAULT_EQUITY_PLEDGE_NEXT_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_EQUITY_PLEDGE_NEXT_SLICE_OUTPUT_ROOT
DRYRUN_REPORT = runner.EQUITY_PLEDGE_NEXT_SLICE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.EQUITY_PLEDGE_NEXT_SLICE_DRYRUN_SUMMARY_MD
FIRST_SLICE_OUTPUT_ROOT = runner.DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
AT_NEXT_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_NEXT_SLICE_OUTPUT_ROOT
SD_NEXT_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_NEXT_SLICE_OUTPUT_ROOT
FIA_FURTHER_OUTPUT_ROOT = (
    runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FURTHER_SCALE_OUTPUT_ROOT
)
FIA_NEXT_OUTPUT_ROOT = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_NEXT_SLICE_OUTPUT_ROOT
ES_OUTPUT_ROOT = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT

VALIDATION = os.path.join(BASE_DIR, "outputs", "validation")
EP_NEXT_LOCK = UNIVERSE_CSV
EP_FIRST_DRAFT = runner.DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_UNIVERSE_CSV
AT_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv",
)
SD_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv",
)
FIA_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv",
)
FIA_FURTHER_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_fund_industry_allocation_further_scale_universe_lock_20260715.csv",
)
FIA_FIRST_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv",
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
FIA_FURTHER_DRYRUN = os.path.join(
    VALIDATION,
    "cninfo_d_class_fund_industry_allocation_further_scale",
    "reports",
    "d_class_fund_industry_allocation_further_scale_dryrun_report.csv",
)
EP_FIRST_DRYRUN = os.path.join(
    VALIDATION,
    "cninfo_d_class_equity_pledge_first_slice",
    "reports",
    "d_class_equity_pledge_first_slice_dryrun_report.csv",
)

EP_NEXT_LOCK_SHA256 = (
    "1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384"
)
EP_FIRST_DRAFT_SHA256 = (
    "5fb4fa005236a162ef3bcc5322fe3b7134b36cbe7727fb0273724d0638dc8e10"
)
AT_NEXT_LOCK_SHA256 = (
    "4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6"
)
SD_NEXT_LOCK_SHA256 = (
    "c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f"
)
FIA_NEXT_LOCK_SHA256 = (
    "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
)
FIA_FURTHER_LOCK_SHA256 = (
    "398494f1cf6a6cf00637b82d6e3f5c38ae21671a4b47324fd1ee2262df92e9f1"
)
FIA_FIRST_LOCK_SHA256 = (
    "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
)
AT_DRYRUN_SHA256 = (
    "51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497"
)
SD_DRYRUN_SHA256 = (
    "2b74aac55299bc844e7df49725ad9ccf1f9c4dfbfc7db403f026412faf177362"
)
FIA_FURTHER_DRYRUN_SHA256 = (
    "fc7cfc51493c426d0db1608aad09b0dc4a7755c0019f8d822a46e40fa85fefd4"
)
EP_FIRST_DRYRUN_SHA256 = (
    "a035f8ef6102946bb2b4406f59f17cff20aff810de9c1fb59cab82c7d43084bc"
)

BASE_ARGS = [
    "--dry-run",
    "--equity-pledge-next-slice",
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


class TestEquityPledgeNextSliceRunner(unittest.TestCase):
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
            "d_class_equity_pledge_next_slice_runner_extension_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_equity_pledge_next_slice_live_path_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_equity_pledge_next_slice_live_gate=NOT_APPROVED",
            result.stdout,
        )

    def test_dry_run_planned_ok_five_of_five(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(os.path.isfile(DRYRUN_REPORT))
        self.assertTrue(os.path.isfile(DRYRUN_SUMMARY))
        with open(DRYRUN_REPORT, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 5)
        self.assertEqual(
            {r["case_id"] for r in rows},
            set(runner.EQUITY_PLEDGE_NEXT_SLICE_ALLOWED_CASE_IDS),
        )
        for row in rows:
            self.assertEqual(row["dryrun_status"], "planned_ok")
            self.assertEqual(row["cninfo_call_planned"], "shared")
            self.assertEqual(
                row["shared_probe_key"],
                runner.EQUITY_PLEDGE_NEXT_SLICE_SHARED_PROBE_KEY,
            )
            self.assertEqual(
                row["planned_endpoint"], runner.EQUITY_PLEDGE_NEXT_SLICE_ENDPOINT
            )
            self.assertEqual(row["query_mode"], "tdate_daily")
            self.assertEqual(row["anchor_tdate"], "2026-07-02")

    def test_planned_snapshots_written(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        snap_dir = os.path.join(OUTPUT_ROOT, "planned_snapshots")
        for case_id in sorted(runner.EQUITY_PLEDGE_NEXT_SLICE_ALLOWED_CASE_IDS):
            path = os.path.join(snap_dir, f"{case_id}_equity_pledge.json")
            self.assertTrue(os.path.isfile(path), msg=path)
            with open(path, encoding="utf-8") as f:
                payload = json.load(f)
            self.assertEqual(payload["query_params"]["tdate"], "2026-07-02")
            self.assertEqual(payload["company_filter_field"], "SECCODE")
            self.assertFalse(payload["cninfo_called"])
            self.assertEqual(
                payload["forbidden_sole_found_anchor"], "2026-07-03"
            )

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--equity-pledge-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "equity_pledge_next_slice_universe_size_must_equal_5",
                result.stderr,
            )

    def test_forbidden_company_code_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[0]["company_code"] = "301259"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_code.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--equity-pledge-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "forbidden_company_code_in_equity_pledge_next_slice_universe",
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
                    "--equity-pledge-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "equity_pledge_next_slice_forbidden_anchor_tdate_20260703",
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
                    "--equity-pledge-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "equity_pledge_next_slice_anchor_tdate_mismatch",
                result.stderr,
            )

    def test_component_must_be_equity_pledge(self) -> None:
        rows = _read_universe_rows()
        rows[2]["component"] = "block_trade"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--equity-pledge-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "equity_pledge_next_slice_component_must_be_equity_pledge",
                result.stderr,
            )

    def test_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--equity-pledge-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "v1_output_root_write_blocked_for_equity_pledge_next_slice",
            result.stderr,
        )

    def test_first_slice_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--equity-pledge-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                FIRST_SLICE_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "equity_pledge_first_slice_output_root_write_blocked",
            result.stderr,
        )

    def test_frozen_peer_roots_write_blocked(self) -> None:
        for root, token in (
            (AT_NEXT_OUTPUT_ROOT, "abnormal_trading_next_slice_output_root_write_blocked"),
            (SD_NEXT_OUTPUT_ROOT, "shareholder_data_next_slice_output_root_write_blocked"),
            (
                FIA_FURTHER_OUTPUT_ROOT,
                "fund_industry_allocation_further_scale_output_root_write_blocked",
            ),
            (
                FIA_NEXT_OUTPUT_ROOT,
                "fund_industry_allocation_next_slice_output_root_write_blocked",
            ),
            (
                ES_OUTPUT_ROOT,
                "executive_shareholding_first_slice_output_root_write_blocked",
            ),
        ):
            with self.subTest(root=root):
                result = _run(
                    [
                        "--dry-run",
                        "--equity-pledge-next-slice",
                        "--universe-csv",
                        UNIVERSE_CSV,
                        "--output-root",
                        root,
                    ]
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(token, result.stderr)

    def test_mixed_mode_with_first_slice_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--equity-pledge-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "equity_pledge_next_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_mixed_mode_with_fia_further_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--fund-industry-allocation-further-scale"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "equity_pledge_next_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_wrong_approval_flag_blocked(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-equity-pledge-first-slice"]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "wrong_approval_flag_for_equity_pledge_next_slice",
            result.stderr,
        )

    def test_live_without_approval_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--equity-pledge-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_equity_pledge_next_slice_required",
            result.stderr,
        )

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(hasattr(runner, "execute_equity_pledge_next_slice_live"))
        self.assertTrue(callable(runner.execute_equity_pledge_next_slice_live))

    def test_shared_plan_equals_one(self) -> None:
        self.assertEqual(
            runner.compute_equity_pledge_next_slice_planned_shared(), 1
        )
        self.assertEqual(
            runner.build_equity_pledge_next_slice_plan(),
            ["tdate_daily_2026-07-02"],
        )

    def test_empty_but_valid_acceptable_rules(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        rows = runner.load_equity_pledge_next_slice_universe(UNIVERSE_CSV)
        by_id = {r.case_id: r for r in rows}
        for case_id in ("DEP101", "DEP102", "DEP103", "DEP104", "DEP105"):
            self.assertTrue(
                runner.is_equity_pledge_next_slice_acceptable(
                    by_id[case_id], summary
                ),
                msg=case_id,
            )

    def test_live_with_approval_mock_shared_path_cninfo_zero(self) -> None:
        """离线 mock live：1 次共享探针 + SECCODE 过滤 · 不触网 · CNINFO=0。"""
        rows = runner.load_equity_pledge_next_slice_universe(UNIVERSE_CSV)
        call_ids: list[str] = []

        def _fake_cninfo_request(session, source_cfg, params_override, stats, case_id):
            call_ids.append(case_id)
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = (
                stats.case_request_counts.get(case_id, 0) + 1
            )
            self.assertEqual(
                params_override.get("tdate"),
                runner.EQUITY_PLEDGE_NEXT_SLICE_ANCHOR_TDATE,
            )
            return (
                {
                    "data": {
                        "records": [
                            {
                                "SECCODE": "000001",
                                "SECNAME": "平安银行",
                                "DECLAREDATE": "2026-07-02",
                                "F001V": "测试出质人",
                                "F003V": "测试质权人",
                                "F006N": 100.0,
                                "F007N": 1.0,
                                "F018N": 2.0,
                            },
                            {
                                "SECCODE": "000895",
                                "SECNAME": "双汇发展",
                                "DECLAREDATE": "2026-07-02",
                                "F001V": "测试出质人2",
                                "F003V": "测试质权人2",
                                "F006N": 50.0,
                                "F007N": 0.5,
                                "F018N": 1.0,
                            },
                            {
                                "SECCODE": "600000",
                                "SECNAME": "浦发银行",
                                "DECLAREDATE": "2026-07-02",
                                "F001V": "测试出质人3",
                                "F003V": "测试质权人3",
                                "F006N": 80.0,
                                "F007N": 0.8,
                                "F018N": 1.2,
                            },
                            {
                                "SECCODE": "002415",
                                "SECNAME": "海康威视",
                                "DECLAREDATE": "2026-07-02",
                                "F001V": "测试出质人4",
                                "F003V": "测试质权人4",
                                "F006N": 60.0,
                                "F007N": 0.6,
                                "F018N": 0.9,
                            },
                        ]
                    }
                },
                200,
                "",
            )

        with tempfile.TemporaryDirectory() as tmp:
            out_root = os.path.join(
                tmp, "cninfo_d_class_equity_pledge_next_slice"
            )
            output_paths = runner.ensure_output_layout(out_root, "live")
            with mock.patch(
                "run_cninfo_d_class_tiny_live_validation._cninfo_request",
                side_effect=_fake_cninfo_request,
            ), mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                rc = runner.execute_equity_pledge_next_slice_live(
                    rows, output_paths
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertEqual(rc, 0)
            self.assertEqual(
                call_ids, [runner.EQUITY_PLEDGE_NEXT_SLICE_SHARED_PROBE_KEY]
            )
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_equity_pledge_next_slice_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = {r["case_id"]: r for r in csv.DictReader(f)}
            self.assertEqual(len(live_rows), 5)
            for case_id in ("DEP101", "DEP102", "DEP103", "DEP104"):
                self.assertEqual(live_rows[case_id]["acceptable"], "yes")
                self.assertEqual(live_rows[case_id]["retrieval_status"], "found")
            self.assertEqual(live_rows["DEP105"]["acceptable"], "yes")
            self.assertEqual(
                live_rows["DEP105"]["retrieval_status"], "empty_but_valid"
            )

    def test_default_universe_csv_rejected(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--equity-pledge-next-slice",
                "--universe-csv",
                runner.DEFAULT_UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "equity_pledge_next_slice_requires_explicit_universe_csv",
            result.stderr,
        )

    def test_plan_helpers_and_fixtures(self) -> None:
        rows = runner.load_equity_pledge_next_slice_universe(UNIVERSE_CSV)
        self.assertEqual(len(rows), 5)
        issues = runner.validate_equity_pledge_next_slice_universe(rows)
        self.assertEqual(issues, [])
        for row in rows:
            refs = runner.resolve_equity_pledge_next_slice_fixture_refs(row.case_id)
            self.assertTrue(refs)
            for ref in refs:
                self.assertTrue(os.path.isfile(ref), ref)

    def test_frozen_locks_and_peer_dryruns_unchanged(self) -> None:
        self.assertEqual(_sha256_file(EP_NEXT_LOCK), EP_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(EP_FIRST_DRAFT), EP_FIRST_DRAFT_SHA256)
        self.assertEqual(_sha256_file(AT_NEXT_LOCK), AT_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_NEXT_LOCK), SD_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_NEXT_LOCK), FIA_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_FURTHER_LOCK), FIA_FURTHER_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_FIRST_LOCK), FIA_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(AT_DRYRUN_REPORT), AT_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(SD_DRYRUN_REPORT), SD_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(FIA_FURTHER_DRYRUN), FIA_FURTHER_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(EP_FIRST_DRYRUN), EP_FIRST_DRYRUN_SHA256)

    def test_dryrun_summary_gates_and_chinese(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("planned_shared_cninfo_requests | **1**", content)
        self.assertIn("NOT APPROVED for live", content)
        self.assertIn("2026-07-02", content)
        self.assertIn("2026-07-03", content)
        self.assertIn("equity_pledge", content)
        self.assertIn("SECCODE", content)
        self.assertNotIn("\ufffd", content)


if __name__ == "__main__":
    unittest.main()
