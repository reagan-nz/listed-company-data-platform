#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFIA005 单探针脚本离线单测（无 CNINFO · 无真实 live）。

运行：
    .venv/bin/python lab/test_cninfo_d_class_fund_industry_allocation_dfia005_single_probe.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_d_class_fund_industry_allocation_dfia005_single_probe as probe  # noqa: E402
import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

UNIVERSE_CSV = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_UNIVERSE_CSV


class TestDfia005SingleProbe(unittest.TestCase):
    def test_dry_run_cninfo_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("requests.get") as get_m, mock.patch(
                "requests.post"
            ) as post_m:
                rc = probe.main(
                    [
                        "--dry-run",
                        "--universe-csv",
                        UNIVERSE_CSV,
                        "--output-dir",
                        tmp,
                    ]
                )
                self.assertEqual(rc, 0)
                get_m.assert_not_called()
                post_m.assert_not_called()
            plan_path = os.path.join(tmp, "reports", "dfia005_single_probe_plan.json")
            self.assertTrue(os.path.isfile(plan_path))
            with open(plan_path, encoding="utf-8") as f:
                plan = json.load(f)
            self.assertEqual(plan["case_id"], "DFIA005")
            self.assertEqual(plan["shared_probe_key"], "rdate_20251231")
            self.assertEqual(plan["query_params"], {"rdate": "20251231"})
            self.assertEqual(plan["cninfo_budget"], 1)
            self.assertFalse(plan["universe_lock_mutated"])

    def test_live_requires_approve_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc = probe.main(
                [
                    "--live",
                    "--universe-csv",
                    UNIVERSE_CSV,
                    "--output-dir",
                    tmp,
                ]
            )
            self.assertEqual(rc, 2)

    def test_mocked_live_empty_but_valid_clears_transport(self) -> None:
        def _fake_cninfo(session, source_cfg, params_override, stats, case_id):
            self.assertEqual(case_id, "rdate_20251231")
            self.assertEqual(params_override, {"rdate": "20251231"})
            self.assertEqual(
                str(source_cfg.get("params_location") or "").lower(), "form"
            )
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = (
                stats.case_request_counts.get(case_id, 0) + 1
            )
            return {"data": {"records": []}}, 200, ""

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("requests.Session"):
                rc = probe.execute_live_single_probe(
                    tmp,
                    UNIVERSE_CSV,
                    cninfo_request_fn=_fake_cninfo,
                )
            self.assertEqual(rc, 0)
            report = os.path.join(
                tmp, "reports", "dfia005_single_probe_live_report.csv"
            )
            self.assertTrue(os.path.isfile(report))
            import csv

            with open(report, newline="", encoding="utf-8") as f:
                row = next(csv.DictReader(f))
            self.assertEqual(row["acceptable"], "yes")
            self.assertEqual(row["retrieval_status"], "empty_but_valid")
            self.assertEqual(row["cninfo_requests"], "1")
            self.assertEqual(row["failure_type"], "")
            self.assertEqual(row["probe_key"], "rdate_20251231")

    def test_mocked_live_found_clears_under_mixed_expectation(self) -> None:
        def _fake_cninfo(session, source_cfg, params_override, stats, case_id):
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = 1
            return {
                "data": {
                    "records": [
                        {
                            "F001V": "A",
                            "F002V": "农、林、牧、渔业",
                            "ENDDATE": "2025-12-31",
                            "F003N": 1,
                            "F004N": 1.0,
                            "F005N": 0.1,
                        }
                    ]
                }
            }, 200, ""

        with tempfile.TemporaryDirectory() as tmp:
            rc = probe.execute_live_single_probe(
                tmp,
                UNIVERSE_CSV,
                cninfo_request_fn=_fake_cninfo,
            )
            self.assertEqual(rc, 0)
            import csv

            report = os.path.join(
                tmp, "reports", "dfia005_single_probe_live_report.csv"
            )
            with open(report, newline="", encoding="utf-8") as f:
                row = next(csv.DictReader(f))
            self.assertEqual(row["retrieval_status"], "found")
            self.assertEqual(row["acceptable"], "yes")
            # D-FM-19：mixed 期望下 found 不再标 empty_control_anchor_stale
            self.assertEqual(row["caveat"], "")
            self.assertEqual(row["probe_gate"], "PASS_OFFLINE_TRANSPORT_CLEARED")
            self.assertEqual(row["cninfo_requests"], "1")

    def test_mocked_live_timeout_keeps_caveat(self) -> None:
        def _fake_cninfo(session, source_cfg, params_override, stats, case_id):
            stats.cninfo_requests += 1
            stats.case_request_counts[case_id] = 1
            return None, 0, "network_error:Read timeout"

        with tempfile.TemporaryDirectory() as tmp:
            rc = probe.execute_live_single_probe(
                tmp,
                UNIVERSE_CSV,
                cninfo_request_fn=_fake_cninfo,
            )
            self.assertEqual(rc, 0)  # PASS_WITH_CAVEAT exit 0
            import csv

            report = os.path.join(
                tmp, "reports", "dfia005_single_probe_live_report.csv"
            )
            with open(report, newline="", encoding="utf-8") as f:
                row = next(csv.DictReader(f))
            self.assertEqual(row["acceptable"], "no")
            self.assertEqual(row["retrieval_status"], "http_error")
            self.assertEqual(row["failure_type"], "transport_or_http_error")
            self.assertEqual(row["caveat"], "transport_or_http_error")
            self.assertEqual(row["cninfo_requests"], "1")
            self.assertEqual(row["probe_gate"], "PASS_WITH_CAVEAT")


if __name__ == "__main__":
    unittest.main()
