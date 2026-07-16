#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-FM-13 指标解构离线审计 — 针对性测试。

只读现有产物，不发起 CNINFO 请求，不 mutate 任何冻结根。
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import audit_cninfo_d_class_dfm13_ep_s1000_metric_decomposition as audit  # noqa: E402


class TestDFM13MetricDecomposition(unittest.TestCase):
    def setUp(self) -> None:
        self.result = audit.decompose()

    def test_target_count_is_1000(self) -> None:
        self.assertEqual(self.result["target_count"], 1000)

    def test_real_found_count_matches_claimed_133(self) -> None:
        self.assertEqual(self.result["real_found_count"], 133)

    def test_synthetic_padded_empty_dominates_over_endpoint_confirmed(self) -> None:
        # 867 claimed "empty pad" 中，863 为连续占位符 SECCODE（从未被专门查询），
        # 仅 4 条（双汇发展/中国银行/贵州茅台/五粮液）是真实公司经共享探针
        # 命中零结果的合法端点确认空。
        self.assertEqual(self.result["synthetic_padded_empty_count"], 863)
        self.assertEqual(self.result["endpoint_confirmed_empty_count"], 4)
        self.assertEqual(
            self.result["synthetic_padded_empty_count"]
            + self.result["endpoint_confirmed_empty_count"],
            867,
        )

    def test_real_found_rate_is_13_3_percent_not_100_percent(self) -> None:
        self.assertAlmostEqual(self.result["real_found_rate"], 0.133, places=3)
        self.assertLess(self.result["real_found_rate"], 0.95)

    def test_synthetic_padding_rate_dominant(self) -> None:
        self.assertGreater(self.result["synthetic_padding_rate"], 0.80)

    def test_evidence_traceability_rate_is_real_found_plus_confirmed_empty(self) -> None:
        expected = (
            self.result["real_found_count"]
            + self.result["endpoint_confirmed_empty_count"]
        ) / self.result["target_count"]
        self.assertAlmostEqual(self.result["evidence_traceability_rate"], expected, places=3)
        self.assertLess(self.result["evidence_traceability_rate"], 0.20)

    def test_known_positive_recall_unverified_due_to_exclusion(self) -> None:
        self.assertEqual(self.result["known_positive_tested"], 0)
        self.assertIsNone(self.result["known_positive_recall"])

    def test_status_is_data_coverage_unverified_not_pass(self) -> None:
        self.assertEqual(self.result["status"], "DATA_COVERAGE_UNVERIFIED")
        self.assertNotIn("PASS", ["excellence", "DATA_COVERAGE_PASS"])

    def test_request_coverage_is_10_shared_not_1000_percompany(self) -> None:
        self.assertEqual(self.result["request_coverage_count"], 10)
        self.assertNotEqual(self.result["request_coverage_count"], self.result["target_count"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
