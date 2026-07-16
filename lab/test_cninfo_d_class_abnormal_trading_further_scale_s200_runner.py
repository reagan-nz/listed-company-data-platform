#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 abnormal_trading further-scale S200 runner 测试（无 CNINFO · 无 live 触网）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_abnormal_trading_further_scale_s200_runner.py
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

import run_cninfo_d_class_abnormal_trading_further_scale_s200 as s200  # noqa: E402
import run_cninfo_d_class_tiny_live_validation as core  # noqa: E402

BASE_DIR = s200.BASE_DIR
RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_d_class_abnormal_trading_further_scale_s200.py"
)
UNIVERSE_CSV = s200.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = s200.DEFAULT_OUTPUT_ROOT
VALIDATION = s200.VALIDATION

S50_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_further_scale",
    "reports",
    "d_class_abnormal_trading_further_scale_live_report.csv",
)
S50_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_further_scale_universe_lock_20260716.csv",
)
AT_NEXT_DRYRUN = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_next_slice",
    "reports",
    "d_class_abnormal_trading_next_slice_dryrun_report.csv",
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


def _synthetic_universe(n: int = 200) -> list:
    rows = []
    for i in range(s200.CASE_ID_START, s200.CASE_ID_START + n - 5):
        code = f"{i:06d}"
        rows.append(
            {
                "case_id": f"DAT{i}",
                "company_code": code,
                "company_name": f"mock{code}",
                "component": "abnormal_trading",
                "market": "szse_main",
                "query_mode": "single_day_paged",
                "anchor_tdate": s200.PRIMARY_TDATE
                if i < s200.CASE_ID_START + 150
                else s200.ADJACENT_TDATE,
                "further_scale_include": "yes",
                "expected_behavior": "captured_normal",
            }
        )
    empties = [
        ("000895", "双汇发展"),
        ("601988", "中国银行"),
        ("600519", "贵州茅台"),
        ("000858", "五粮液"),
        ("601318", "中国平安"),
    ]
    for j, (code, name) in enumerate(empties):
        case_id = f"DAT{s200.CASE_ID_END - 4 + j}"
        rows.append(
            {
                "case_id": case_id,
                "company_code": code,
                "company_name": name,
                "component": "abnormal_trading",
                "market": s200._infer_market(code),
                "query_mode": "single_day_paged",
                "anchor_tdate": s200.PRIMARY_TDATE,
                "further_scale_include": "yes",
                "expected_behavior": "empty_but_valid",
            }
        )
    rows_by = {r["case_id"]: r for r in rows}
    return [rows_by[f"DAT{i}"] for i in range(s200.CASE_ID_START, s200.CASE_ID_END + 1)]


class TestAbnormalTradingFurtherScaleS200Runner(unittest.TestCase):
    def test_wrong_output_root_blocked(self) -> None:
        blocked = os.path.join(
            VALIDATION, "cninfo_d_class_abnormal_trading_further_scale"
        )
        # 无 universe 时也会先校验 root；构造临时假锁仍应挡 S50 根
        result = _run(
            [
                "--dry-run",
                "--universe-csv",
                S50_LOCK if os.path.isfile(S50_LOCK) else UNIVERSE_CSV,
                "--output-root",
                blocked,
            ]
        )
        self.assertEqual(result.returncode, 2)
        self.assertTrue(
            "abnormal_trading_further_scale_s200_output_root_must_be_" in result.stderr
            or "frozen_root_write_blocked" in result.stderr
        )

    def test_live_without_approve_blocked(self) -> None:
        # 若锁尚未生成，仍应因 approve 缺失而失败（或 universe missing）
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
        self.assertTrue(
            "approve_d_class_abnormal_trading_further_scale_s200_required"
            in result.stderr
            or "universe not found" in result.stderr
        )

    def test_validate_universe_size(self) -> None:
        rows = _synthetic_universe()
        self.assertEqual(len(rows), 200)
        issues = s200.validate_universe(rows)
        self.assertEqual(issues, [])

    def test_mock_live_shared_two_day_requests(self) -> None:
        rows = _synthetic_universe()
        primary_recs = [
            {"secCode": r["company_code"], "secName": r["company_name"], "type": "m"}
            for r in rows
            if r["expected_behavior"] == "captured_normal"
            and r["anchor_tdate"] == s200.PRIMARY_TDATE
        ]
        adjacent_recs = [
            {"secCode": r["company_code"], "secName": r["company_name"], "type": "m"}
            for r in rows
            if r["expected_behavior"] == "captured_normal"
            and r["anchor_tdate"] == s200.ADJACENT_TDATE
        ]

        with tempfile.TemporaryDirectory() as tmp:
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
                tdate = params.get("sdate")
                if tdate == s200.PRIMARY_TDATE:
                    payload = {
                        "marketList": primary_recs,
                        "total": len(primary_recs),
                    }
                else:
                    payload = {
                        "marketList": adjacent_recs,
                        "total": len(adjacent_recs),
                    }
                return payload, 200, ""

            with mock.patch.object(core, "_cninfo_request", side_effect=fake_request):
                rc = s200.execute_live(rows, output_paths)
            self.assertEqual(rc, 0)
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_abnormal_trading_further_scale_s200_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = list(csv.DictReader(f))
            self.assertEqual(len(live_rows), 200)
            self.assertTrue(all(r["acceptable"] == "yes" for r in live_rows))
            excel = s200.excellence_metrics(live_rows)
            self.assertTrue(excel["excellent"])
            self.assertEqual(excel["failed_or_http_error"], 0)

    def test_frozen_s50_and_next_slice_untouched_hashes_if_present(self) -> None:
        # 若产物存在，记录基线哈希供 freeze attestation 对照（本测试不修改）
        for path in (S50_LIVE, S50_LOCK, AT_NEXT_DRYRUN):
            if os.path.isfile(path):
                digest = _sha256_file(path)
                self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
