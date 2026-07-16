#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 abnormal_trading further-scale（~50）runner 测试（无 CNINFO · 无 live 触网）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_abnormal_trading_further_scale_runner.py
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

import run_cninfo_d_class_abnormal_trading_further_scale as fs  # noqa: E402
import run_cninfo_d_class_tiny_live_validation as core  # noqa: E402

BASE_DIR = fs.BASE_DIR
RUNNER = os.path.join(_LAB_DIR, "run_cninfo_d_class_abnormal_trading_further_scale.py")
UNIVERSE_CSV = fs.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = fs.DEFAULT_OUTPUT_ROOT
VALIDATION = fs.VALIDATION

AT_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv",
)
AT_NEXT_DRYRUN = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_next_slice",
    "reports",
    "d_class_abnormal_trading_next_slice_dryrun_report.csv",
)
ESH_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_next_slice_universe_lock_20260716.csv",
)
ESH_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_next_slice",
    "reports",
    "d_class_executive_shareholding_next_slice_live_report.csv",
)
SC_DRY = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_next_slice",
    "reports",
    "d_class_shareholder_change_next_slice_dryrun_report.csv",
)
EP_DRY = os.path.join(
    VALIDATION,
    "cninfo_d_class_equity_pledge_next_slice",
    "reports",
    "d_class_equity_pledge_next_slice_dryrun_report.csv",
)
RSU_DRY = os.path.join(
    VALIDATION,
    "cninfo_d_class_restricted_shares_unlock_next_slice",
    "reports",
    "d_class_restricted_shares_unlock_next_slice_dryrun_report.csv",
)

AT_NEXT_LOCK_SHA256 = (
    "4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6"
)
AT_NEXT_DRYRUN_SHA256 = (
    "51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497"
)
ESH_LOCK_SHA256 = (
    "4213de37e19d1d6bd920a9b2efd24495338a27eeb17f2602a8159fbb4b6d2fd1"
)
ESH_LIVE_SHA256 = (
    "dc16b591b117a9411c0ec458a1ff3cdb4d850417fcf87d5de851c5c73af23e25"
)
SC_DRY_SHA256 = (
    "5abc61e4f7ea6014af7e50847aefc7e46f4e39e3ba10e394fd56e683b19a08a5"
)
EP_DRY_SHA256 = (
    "054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e"
)
RSU_DRY_SHA256 = (
    "87f296cf51fd69873f8fd6fd05a541ebbfa35dab53b92063bdf841736b52b18c"
)


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _run(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )


class TestAbnormalTradingFurtherScaleRunner(unittest.TestCase):
    def test_universe_lock_size_and_mix(self) -> None:
        self.assertTrue(os.path.isfile(UNIVERSE_CSV))
        with open(UNIVERSE_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 50)
        self.assertEqual(rows[0]["case_id"], "DAT201")
        self.assertEqual(rows[-1]["case_id"], "DAT250")
        found_like = [r for r in rows if r["expected_behavior"] == "captured_normal"]
        empty_like = [r for r in rows if r["expected_behavior"] == "empty_but_valid"]
        self.assertEqual(len(found_like), 48)
        self.assertEqual(len(empty_like), 2)
        self.assertEqual(empty_like[0]["company_code"], "000895")
        self.assertEqual(empty_like[1]["company_code"], "601988")
        issues = fs.validate_universe(rows)
        self.assertEqual(issues, [])

    def test_dry_run_cninfo_zero_and_planned_ok(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # 仅验证 dry-run 逻辑对正式根只读；用真实锁但写到 temp 会被 root 校验拒绝
            result = _run(
                [
                    "--dry-run",
                    "--universe-csv",
                    UNIVERSE_CSV,
                    "--output-root",
                    tmp,
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "abnormal_trading_further_scale_output_root_must_be_",
                result.stderr,
            )

        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            # 正式 dry-run 已存在；此处仅断言产物与 CNINFO=0 语义，不重跑覆盖
            dry_report = os.path.join(
                OUTPUT_ROOT,
                "reports",
                "d_class_abnormal_trading_further_scale_dryrun_report.csv",
            )
            dry_summary = os.path.join(
                OUTPUT_ROOT,
                "reports",
                "d_class_abnormal_trading_further_scale_dryrun_summary.md",
            )
            self.assertTrue(os.path.isfile(dry_report))
            self.assertTrue(os.path.isfile(dry_summary))
            with open(dry_report, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 50)
            self.assertTrue(all(r["dryrun_status"] == "planned_ok" for r in rows))
            with open(dry_summary, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("CNINFO calls | **0**", content)
            self.assertIn("rows=200", content)
            get_mock.assert_not_called()
            post_mock.assert_not_called()

    def test_live_without_approve_blocked(self) -> None:
        result = _run(
            [
                "--live",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                OUTPUT_ROOT,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "approve_d_class_abnormal_trading_further_scale_required",
            result.stderr,
        )

    def test_wrong_output_root_blocked(self) -> None:
        blocked = os.path.join(
            VALIDATION, "cninfo_d_class_abnormal_trading_next_slice"
        )
        result = _run(
            [
                "--dry-run",
                "--universe-csv",
                UNIVERSE_CSV,
                "--output-root",
                blocked,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertTrue(
            "abnormal_trading_further_scale_output_root_must_be_" in result.stderr
            or "frozen_root_write_blocked" in result.stderr
        )

    def test_mock_live_shared_one_request(self) -> None:
        rows = fs.load_universe(UNIVERSE_CSV)
        # 构造含全部 found 候选 + 不含 empty control 的 marketList
        records = []
        for row in rows:
            if row["expected_behavior"] == "captured_normal":
                records.append(
                    {
                        "secCode": row["company_code"],
                        "secName": row["company_name"],
                        "type": "mock",
                    }
                )
        payload = {"marketList": records, "total": len(records), "count": len(records)}

        with tempfile.TemporaryDirectory() as tmp:
            # execute_live 需要正式 root；改用临时 layout 直接调函数前 patch validate
            output_paths = {
                "root": tmp,
                "reports": os.path.join(tmp, "reports"),
                "live_snapshots": os.path.join(tmp, "live_snapshots"),
            }
            os.makedirs(output_paths["reports"], exist_ok=True)
            os.makedirs(output_paths["live_snapshots"], exist_ok=True)

            def fake_request(session, cfg, params, stats, case_id):
                stats.cninfo_requests += 1
                stats.case_request_counts[case_id] = (
                    stats.case_request_counts.get(case_id, 0) + 1
                )
                return payload, 200, ""

            with mock.patch.object(core, "_cninfo_request", side_effect=fake_request):
                rc = fs.execute_live(rows, output_paths)
            self.assertEqual(rc, 0)
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_abnormal_trading_further_scale_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = list(csv.DictReader(f))
            self.assertEqual(len(live_rows), 50)
            self.assertTrue(all(r["acceptable"] == "yes" for r in live_rows))
            found = [r for r in live_rows if r["retrieval_status"] == "found"]
            empty = [r for r in live_rows if r["retrieval_status"] == "empty_but_valid"]
            self.assertEqual(len(found), 48)
            self.assertEqual(len(empty), 2)

    def test_frozen_roots_unchanged(self) -> None:
        self.assertEqual(_sha256_file(AT_NEXT_LOCK), AT_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(AT_NEXT_DRYRUN), AT_NEXT_DRYRUN_SHA256)
        self.assertEqual(_sha256_file(ESH_LOCK), ESH_LOCK_SHA256)
        self.assertEqual(_sha256_file(ESH_LIVE), ESH_LIVE_SHA256)
        self.assertEqual(_sha256_file(SC_DRY), SC_DRY_SHA256)
        self.assertEqual(_sha256_file(EP_DRY), EP_DRY_SHA256)
        self.assertEqual(_sha256_file(RSU_DRY), RSU_DRY_SHA256)

    def test_live_report_fifty_of_fifty(self) -> None:
        live_report = os.path.join(
            OUTPUT_ROOT,
            "reports",
            "d_class_abnormal_trading_further_scale_live_report.csv",
        )
        quality = os.path.join(
            OUTPUT_ROOT,
            "reports",
            "d_class_abnormal_trading_further_scale_quality_report.csv",
        )
        self.assertTrue(os.path.isfile(live_report))
        self.assertTrue(os.path.isfile(quality))
        with open(live_report, newline="", encoding="utf-8") as f:
            live_rows = {r["case_id"]: r for r in csv.DictReader(f)}
        with open(quality, newline="", encoding="utf-8") as f:
            quality_rows = {r["case_id"]: r for r in csv.DictReader(f)}
        self.assertEqual(len(live_rows), 50)
        self.assertEqual(set(live_rows), set(quality_rows))
        for case_id, row in live_rows.items():
            self.assertEqual(row["acceptable"], "yes")
            self.assertEqual(row["acceptable"], quality_rows[case_id]["acceptable"])
        self.assertEqual(live_rows["DAT201"]["retrieval_status"], "found")
        self.assertEqual(live_rows["DAT249"]["retrieval_status"], "empty_but_valid")
        self.assertEqual(live_rows["DAT250"]["retrieval_status"], "empty_but_valid")
        cite = fs.MARKETLIST_CITE_JSON
        self.assertTrue(os.path.isfile(cite))
        with open(cite, encoding="utf-8") as f:
            payload = json.load(f)
        self.assertEqual(payload.get("cninfo_requests"), 1)
        self.assertEqual(payload.get("total"), 170)


if __name__ == "__main__":
    unittest.main()
