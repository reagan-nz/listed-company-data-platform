#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 executive_shareholding further-scale S200 runner 测试（无真实 CNINFO · mock live 允许）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_executive_shareholding_further_scale_s200_runner.py
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

import run_cninfo_d_class_executive_shareholding_further_scale_s200 as s200  # noqa: E402
import run_cninfo_d_class_tiny_live_validation as core  # noqa: E402

BASE_DIR = s200.BASE_DIR
RUNNER = os.path.join(
    _LAB_DIR, "run_cninfo_d_class_executive_shareholding_further_scale_s200.py"
)
UNIVERSE_CSV = s200.DEFAULT_UNIVERSE_CSV
OUTPUT_ROOT = s200.DEFAULT_OUTPUT_ROOT
VALIDATION = s200.VALIDATION

S50_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_further_scale_universe_lock_20260716.csv",
)
S50_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_further_scale",
    "reports",
    "d_class_executive_shareholding_further_scale_live_report.csv",
)
ESH_NEXT_LOCK = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_next_slice_universe_lock_20260716.csv",
)
ESH_NEXT_LIVE = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_next_slice",
    "reports",
    "d_class_executive_shareholding_next_slice_live_report.csv",
)

S50_LOCK_SHA256 = (
    "8ca94115a7ae180cb382687b46d864bedcbe28343eb0efe2cb2cd552dd97f068"
)
S50_LIVE_SHA256 = (
    "1d32b6f324948417b2726e0dd5bd637db1ce01e30e0fe29ae983cd3c4ab73d06"
)
ESH_NEXT_LOCK_SHA256 = (
    "4213de37e19d1d6bd920a9b2efd24495338a27eeb17f2602a8159fbb4b6d2fd1"
)
ESH_NEXT_LIVE_SHA256 = (
    "dc16b591b117a9411c0ec458a1ff3cdb4d850417fcf87d5de851c5c73af23e25"
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
    # 避开 EXCLUDED_S50_FOUND_CODES / prior slice：用高位合成码
    for i in range(s200.CASE_ID_START, s200.CASE_ID_END - 1):
        code = f"{900000 + (i - s200.CASE_ID_START):06d}"
        rows.append(
            {
                "case_id": f"DES{i}",
                "company_code": code,
                "company_name": f"mock{code}",
                "component": "executive_shareholding",
                "market": "sse_main",
                "query_mode": s200.QUERY_MODE,
                "time_mark": s200.TIME_MARK,
                "vary_type": s200.VARY_TYPE,
                "further_scale_include": "yes",
                "expected_behavior": "captured_normal",
            }
        )
    empties = [
        ("000895", "双汇发展"),
        ("601988", "中国银行"),
    ]
    for j, (code, name) in enumerate(empties):
        case_id = f"DES{s200.CASE_ID_END - 1 + j}"
        rows.append(
            {
                "case_id": case_id,
                "company_code": code,
                "company_name": name,
                "component": "executive_shareholding",
                "market": s200._infer_market(code),
                "query_mode": s200.QUERY_MODE,
                "time_mark": s200.TIME_MARK,
                "vary_type": s200.VARY_TYPE,
                "further_scale_include": "yes",
                "expected_behavior": "empty_but_valid",
            }
        )
    rows_by = {r["case_id"]: r for r in rows}
    return [
        rows_by[f"DES{i}"]
        for i in range(s200.CASE_ID_START, s200.CASE_ID_END + 1)
    ]


class TestExecutiveShareholdingFurtherScaleS200Runner(unittest.TestCase):
    def test_validate_universe_size_and_ids(self) -> None:
        rows = _synthetic_universe()
        self.assertEqual(len(rows), 200)
        self.assertEqual(rows[0]["case_id"], "DES251")
        self.assertEqual(rows[-1]["case_id"], "DES450")
        issues = s200.validate_universe(rows)
        self.assertEqual(issues, [])

    def test_wrong_output_root_blocked_including_s50(self) -> None:
        blocked = os.path.join(
            VALIDATION, "cninfo_d_class_executive_shareholding_further_scale"
        )
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
            "executive_shareholding_further_scale_s200_output_root_must_be_"
            in result.stderr
            or "frozen_root_write_blocked" in result.stderr
        )

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
        self.assertTrue(
            "approve_d_class_executive_shareholding_further_scale_s200_required"
            in result.stderr
            or "universe not found" in result.stderr
        )

    def test_mock_live_shared_one_request_excellence(self) -> None:
        rows = _synthetic_universe()
        records = []
        for row in rows:
            if row["expected_behavior"] == "captured_normal":
                records.append(
                    {
                        "SECCODE": row["company_code"],
                        "SECNAME": row["company_name"],
                        "HUMANNAME": "mock",
                    }
                )
        payload = {"data": {"records": records, "total": len(records)}}

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
                return payload, 200, ""

            with mock.patch.object(core, "_cninfo_request", side_effect=fake_request):
                rc = s200.execute_live(rows, output_paths)
            self.assertEqual(rc, 0)
            live_report = os.path.join(
                output_paths["reports"],
                "d_class_executive_shareholding_further_scale_s200_live_report.csv",
            )
            with open(live_report, newline="", encoding="utf-8") as f:
                live_rows = list(csv.DictReader(f))
            self.assertEqual(len(live_rows), 200)
            self.assertTrue(all(r["acceptable"] == "yes" for r in live_rows))
            found = [r for r in live_rows if r["retrieval_status"] == "found"]
            empty = [
                r for r in live_rows if r["retrieval_status"] == "empty_but_valid"
            ]
            self.assertEqual(len(found), 198)
            self.assertEqual(len(empty), 2)
            excel = s200.excellence_metrics(live_rows)
            self.assertTrue(excel["excellent"])
            self.assertEqual(excel["failed_or_http_error"], 0)
            self.assertGreaterEqual(excel["acceptable_rate"], 0.95)

    def test_frozen_s50_and_next_slice_untouched(self) -> None:
        self.assertTrue(os.path.isfile(S50_LOCK))
        self.assertEqual(_sha256_file(S50_LOCK), S50_LOCK_SHA256)
        if os.path.isfile(S50_LIVE):
            self.assertEqual(_sha256_file(S50_LIVE), S50_LIVE_SHA256)
        self.assertEqual(_sha256_file(ESH_NEXT_LOCK), ESH_NEXT_LOCK_SHA256)
        self.assertEqual(_sha256_file(ESH_NEXT_LIVE), ESH_NEXT_LIVE_SHA256)

    def test_universe_lock_when_present(self) -> None:
        if not os.path.isfile(UNIVERSE_CSV):
            self.skipTest("s200 universe lock not yet generated")
        with open(UNIVERSE_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 200)
        self.assertEqual(rows[0]["case_id"], "DES251")
        self.assertEqual(rows[-1]["case_id"], "DES450")
        found_like = [r for r in rows if r["expected_behavior"] == "captured_normal"]
        empty_like = [r for r in rows if r["expected_behavior"] == "empty_but_valid"]
        self.assertEqual(len(found_like), 198)
        self.assertEqual(len(empty_like), 2)
        found_codes = {r["company_code"] for r in found_like}
        for code in s200.EXCLUDED_S50_FOUND_CODES:
            self.assertNotIn(code, found_codes)
        for code in ("002415", "000895", "600000", "000550", "601988"):
            self.assertNotIn(code, found_codes)
        issues = s200.validate_universe(rows)
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
