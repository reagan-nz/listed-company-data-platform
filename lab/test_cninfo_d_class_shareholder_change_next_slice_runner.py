#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 shareholder_change next-slice runner 测试（无 CNINFO · 无 live 执行）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_shareholder_change_next_slice_runner.py
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
UNIVERSE_CSV = runner.DEFAULT_SHAREHOLDER_CHANGE_NEXT_SLICE_UNIVERSE_CSV
OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_CHANGE_NEXT_SLICE_OUTPUT_ROOT
DRYRUN_REPORT = runner.SHAREHOLDER_CHANGE_NEXT_SLICE_DRYRUN_REPORT_CSV
DRYRUN_SUMMARY = runner.SHAREHOLDER_CHANGE_NEXT_SLICE_DRYRUN_SUMMARY_MD
FIRST_SLICE_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT
V1_OUTPUT_ROOT = runner.DEFAULT_OUTPUT_ROOT
AT_NEXT_OUTPUT_ROOT = runner.DEFAULT_ABNORMAL_TRADING_NEXT_SLICE_OUTPUT_ROOT
SD_NEXT_OUTPUT_ROOT = runner.DEFAULT_SHAREHOLDER_DATA_NEXT_SLICE_OUTPUT_ROOT
FIA_FURTHER_OUTPUT_ROOT = (
    runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FURTHER_SCALE_OUTPUT_ROOT
)
FIA_NEXT_OUTPUT_ROOT = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_NEXT_SLICE_OUTPUT_ROOT
ES_OUTPUT_ROOT = runner.DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT

VALIDATION = os.path.join(BASE_DIR, "outputs", "validation")
SC_NEXT_LOCK = UNIVERSE_CSV
SC_FIRST_LOCK = runner.DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_UNIVERSE_CSV
RSU_NEXT_LOCK = runner.DEFAULT_RESTRICTED_SHARES_UNLOCK_NEXT_SLICE_UNIVERSE_CSV
RSU_NEXT_DRYRUN = os.path.join(
    VALIDATION,
    "cninfo_d_class_restricted_shares_unlock_next_slice",
    "reports",
    "d_class_restricted_shares_unlock_next_slice_dryrun_report.csv",
)
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
SC_FIRST_DRYRUN = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_first_slice",
    "reports",
    "d_class_shareholder_change_first_slice_dryrun_report.csv",
)
EP_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_equity_pledge_next_slice_universe_lock_20260715.csv",
)
EP_NEXT_DRYRUN = os.path.join(
    VALIDATION,
    "cninfo_d_class_equity_pledge_next_slice",
    "reports",
    "d_class_equity_pledge_next_slice_dryrun_report.csv",
)

SC_NEXT_LOCK_SHA256 = (
    "5452bc546def60754182a0e5b38fb165d709a37e0a267113088732237b5508fb"
)
SC_FIRST_LOCK_SHA256 = (
    "49e6ece0c0a5c5ecce32328e4e1fe990b48d7d46d3cc1f32da1c8d2245a3c402"
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
SC_FIRST_DRYRUN_SHA256 = (
    "e37e9fbe485bf63b9c4d41cf1170aec558100f51c9ac69654bf09f7eb1213e44"
)
EP_NEXT_LOCK_SHA256 = (
    "1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384"
)
EP_NEXT_DRYRUN_SHA256 = (
    "054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e"
)
RSU_NEXT_LOCK_SHA256 = (
    "13254f44f344c0f2976dfbde6fe75e363f91283a6eec1a5ae02d29f3831f193f"
)
RSU_NEXT_DRYRUN_SHA256 = (
    "87f296cf51fd69873f8fd6fd05a541ebbfa35dab53b92063bdf841736b52b18c"
)

BASE_ARGS = [
    "--dry-run",
    "--shareholder-change-next-slice",
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


class TestShareholderChangeNextSliceRunner(unittest.TestCase):
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
            "d_class_shareholder_change_next_slice_runner_extension_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_shareholder_change_next_slice_live_path_gate=READY_FOR_APPROVAL",
            result.stdout,
        )
        self.assertIn(
            "d_class_shareholder_change_next_slice_live_gate=NOT_APPROVED",
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
            set(runner.SHAREHOLDER_CHANGE_NEXT_SLICE_ALLOWED_CASE_IDS),
        )
        for row in rows:
            self.assertEqual(row["dryrun_status"], "planned_ok")
            self.assertEqual(row["cninfo_call_planned"], "shared")
            self.assertEqual(
                row["shared_probe_key"],
                runner.SHAREHOLDER_CHANGE_NEXT_SLICE_SHARED_PROBE_KEY,
            )
            self.assertEqual(
                row["planned_endpoint"], runner.SHAREHOLDER_CHANGE_NEXT_SLICE_ENDPOINT
            )
            self.assertEqual(row["query_mode"], "type_desc_tdate_daily")
            self.assertEqual(row["query_type"], "desc")
            self.assertEqual(row["anchor_tdate"], "2026-07-03")

    def test_planned_snapshots_written(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        snap_dir = os.path.join(OUTPUT_ROOT, "planned_snapshots")
        for case_id in sorted(runner.SHAREHOLDER_CHANGE_NEXT_SLICE_ALLOWED_CASE_IDS):
            path = os.path.join(snap_dir, f"{case_id}_shareholder_change.json")
            self.assertTrue(os.path.isfile(path), msg=path)
            with open(path, encoding="utf-8") as f:
                payload = json.load(f)
            self.assertEqual(payload["query_params"]["tdate"], "2026-07-03")
            self.assertEqual(payload["query_params"]["type"], "desc")
            self.assertEqual(payload["query_type"], "desc")
            self.assertEqual(payload["company_filter_field"], "SECCODE")
            self.assertFalse(payload["cninfo_called"])
            self.assertEqual(
                payload["forbidden_sole_found_anchor"], "type=inc+2026-07-03"
            )

    def test_universe_size_must_equal_5(self) -> None:
        rows = _read_universe_rows()[:3]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_universe.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--shareholder-change-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_change_next_slice_universe_size_must_equal_5",
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
                    "--shareholder-change-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "forbidden_company_code_in_shareholder_change_next_slice_universe",
                result.stderr,
            )

    def test_forbidden_query_type_inc_blocked(self) -> None:
        rows = _read_universe_rows()
        rows[2]["query_type"] = "inc"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forbidden_query_type.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--shareholder-change-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_change_next_slice_forbidden_query_type_inc",
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
                    "--shareholder-change-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_change_next_slice_anchor_tdate_mismatch",
                result.stderr,
            )

    def test_component_must_be_shareholder_change(self) -> None:
        rows = _read_universe_rows()
        rows[2]["component"] = "block_trade"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_component.csv")
            _write_universe_csv(path, rows)
            result = _run(
                [
                    "--dry-run",
                    "--shareholder-change-next-slice",
                    "--universe-csv",
                    path,
                    "--output-root",
                    OUTPUT_ROOT,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "shareholder_change_next_slice_component_must_be_shareholder_change",
                result.stderr,
            )

    def test_v1_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-change-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                V1_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "v1_output_root_write_blocked_for_shareholder_change_next_slice",
            result.stderr,
        )

    def test_first_slice_output_root_write_blocked(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-change-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                FIRST_SLICE_OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_change_first_slice_output_root_write_blocked",
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
                        "--shareholder-change-next-slice",
                        "--universe-csv",
                        UNIVERSE_CSV,
                        "--output-root",
                        root,
                    ]
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(token, result.stderr)

    def test_mixed_mode_with_first_slice_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--restricted-shares-unlock-first-slice"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_change_next_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_mixed_mode_with_fia_further_blocked(self) -> None:
        result = _run(BASE_ARGS + ["--fund-industry-allocation-further-scale"])
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_change_next_slice_incompatible_with_other_modes",
            result.stderr,
        )

    def test_wrong_approval_flag_blocked(self) -> None:
        result = _run(
            BASE_ARGS + ["--approve-d-class-restricted-shares-unlock-first-slice"]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "wrong_approval_flag_for_shareholder_change_next_slice",
            result.stderr,
        )

    def test_live_without_approval_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--shareholder-change-next-slice",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_shareholder_change_next_slice_required",
            result.stderr,
        )

    def test_live_path_execute_function_exists(self) -> None:
        self.assertTrue(hasattr(runner, "execute_shareholder_change_next_slice_live"))
        self.assertTrue(callable(runner.execute_shareholder_change_next_slice_live))

    def test_shared_plan_equals_one(self) -> None:
        self.assertEqual(
            runner.compute_shareholder_change_next_slice_planned_shared(), 1
        )
        self.assertEqual(
            runner.build_shareholder_change_next_slice_plan(),
            ["type_desc_tdate_daily_2026-07-03"],
        )

    def test_empty_but_valid_acceptable_rules(self) -> None:
        summary = {
            "retrieval_status": "empty_but_valid",
            "quality_status": "pass",
            "record_count": "0",
        }
        rows = runner.load_shareholder_change_next_slice_universe(UNIVERSE_CSV)
        by_id = {r.case_id: r for r in rows}
        for case_id in ("DSC101", "DSC102", "DSC103", "DSC104", "DSC105"):
            self.assertTrue(
                runner.is_shareholder_change_next_slice_acceptable(
                    by_id[case_id], summary
                ),
                msg=case_id,
            )

    def test_live_with_approval_mock_shared_path_cninfo_zero(self) -> None:
        """离线 mock live：1 次共享探针 + SECCODE 过滤 · 不触网 · CNINFO=0。"""
        rows = runner.load_shareholder_change_next_slice_universe(UNIVERSE_CSV)
        call_ids: list[str] = []

        def _fake_cninfo_request(session, source_cfg, params_override, stats, case_id):
            call_ids.append(case_id)
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = (
                stats.case_request_counts.get(case_id, 0) + 1
            )
            self.assertEqual(
                params_override.get("tdate"),
                runner.SHAREHOLDER_CHANGE_NEXT_SLICE_ANCHOR_TDATE,
            )
            self.assertEqual(
                params_override.get("type"),
                runner.SHAREHOLDER_CHANGE_NEXT_SLICE_QUERY_TYPE,
            )
            return (
                {
                    "data": {
                        "records": [
                            {
                                "SECCODE": "000550",
                                "SECNAME": "江铃汽车",
                                "DECLAREDATE": "2026-07-02",
                                "VARYDATE": "2026-07-03",
                                "F002V": "合成股东名称DSC101",
                                "F004N": 420000.0,
                                "F005N": 0.08,
                                "F007V": "10.20",
                            },
                            {
                                "SECCODE": "000895",
                                "SECNAME": "双汇发展",
                                "DECLAREDATE": "2026-07-01",
                                "VARYDATE": "2026-07-03",
                                "F004N": 100000.0,
                                "F005N": 0.1,
                                "F007V": "10.00",
                            },
                            {
                                "SECCODE": "600000",
                                "SECNAME": "浦发银行",
                                "DECLAREDATE": "2026-07-01",
                                "VARYDATE": "2026-07-03",
                                "F004N": 200000.0,
                                "F005N": 0.2,
                                "F007V": "10.00",
                            },
                            {
                                "SECCODE": "002415",
                                "SECNAME": "海康威视",
                                "DECLAREDATE": "2026-07-01",
                                "VARYDATE": "2026-07-03",
                                "F004N": 300000.0,
                                "F005N": 0.3,
                                "F007V": "10.00",
                            },
                        ]
                    }
                },
                200,
                "",
            )

        with tempfile.TemporaryDirectory() as tmp:
            out_root = os.path.join(
                tmp, "cninfo_d_class_shareholder_change_next_slice"
            )
            output_paths = runner.ensure_output_layout(out_root, "live")
            with mock.patch(
                "run_cninfo_d_class_tiny_live_validation._cninfo_request",
                side_effect=_fake_cninfo_request,
            ), mock.patch("requests.get") as get_mock, mock.patch(
                "requests.post"
            ) as post_mock:
                rc = runner.execute_shareholder_change_next_slice_live(
                    rows, output_paths
                )
                get_mock.assert_not_called()
                post_mock.assert_not_called()
            self.assertEqual(rc, 0)
            self.assertEqual(
                call_ids, [runner.SHAREHOLDER_CHANGE_NEXT_SLICE_SHARED_PROBE_KEY]
            )
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_shareholder_change_next_slice_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = {r["case_id"]: r for r in csv.DictReader(f)}
            self.assertEqual(len(live_rows), 5)
            for case_id in ("DSC101", "DSC102", "DSC103", "DSC104"):
                self.assertEqual(live_rows[case_id]["acceptable"], "yes")
                self.assertEqual(live_rows[case_id]["retrieval_status"], "found")
            self.assertEqual(live_rows["DSC105"]["acceptable"], "yes")
            self.assertEqual(
                live_rows["DSC105"]["retrieval_status"], "empty_but_valid"
            )

    def test_default_universe_csv_rejected(self) -> None:
        result = _run(
            [
                "--dry-run",
                "--shareholder-change-next-slice",
                "--universe-csv",
                runner.DEFAULT_UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "shareholder_change_next_slice_requires_explicit_universe_csv",
            result.stderr,
        )

    def test_plan_helpers_and_fixtures(self) -> None:
        rows = runner.load_shareholder_change_next_slice_universe(UNIVERSE_CSV)
        self.assertEqual(len(rows), 5)
        issues = runner.validate_shareholder_change_next_slice_universe(rows)
        self.assertEqual(issues, [])
        for row in rows:
            refs = runner.resolve_shareholder_change_next_slice_fixture_refs(row.case_id)
            self.assertTrue(refs)
            for ref in refs:
                self.assertTrue(os.path.isfile(ref), ref)

    def test_frozen_locks_and_peer_dryruns_unchanged(self) -> None:
        self.assertEqual(_sha256_file(SC_NEXT_LOCK), SC_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SC_FIRST_LOCK), SC_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(RSU_NEXT_LOCK), RSU_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(RSU_NEXT_DRYRUN), RSU_NEXT_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(EP_NEXT_LOCK), EP_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(EP_NEXT_DRYRUN), EP_NEXT_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(AT_NEXT_LOCK), AT_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(SD_NEXT_LOCK), SD_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_NEXT_LOCK), FIA_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_FURTHER_LOCK), FIA_FURTHER_LOCK_SHA256)
        self.assertEqual(_sha256_file(FIA_FIRST_LOCK), FIA_FIRST_LOCK_SHA256)
        self.assertEqual(_sha256_file(AT_DRYRUN_REPORT), AT_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(SD_DRYRUN_REPORT), SD_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(FIA_FURTHER_DRYRUN), FIA_FURTHER_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(SC_FIRST_DRYRUN), SC_FIRST_DRYRUN_SHA256)

    def test_dryrun_summary_gates_and_chinese(self) -> None:
        result = _run(BASE_ARGS)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        with open(DRYRUN_SUMMARY, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("planned_shared_cninfo_requests | **1**", content)
        self.assertIn("NOT APPROVED for live", content)
        self.assertIn("2026-07-03", content)
        self.assertIn("type=inc", content)
        self.assertIn("desc", content)
        self.assertIn("shareholder_change", content)
        self.assertIn("SECCODE", content)
        self.assertIn("type_desc_tdate_daily", content)
        self.assertNotIn("\ufffd", content)


if __name__ == "__main__":
    unittest.main()

