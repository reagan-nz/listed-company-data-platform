"""
B 类 category routing — wrong_period false_positive lineage 单测。

覆盖 validation_design §7「报告期不匹配」：标题可正确路由到 periodic，
但 parsed_report_period ≠ expected_period 时须标注 false_positive_reason=wrong_period。

离线 only · 无 CNINFO · 无 live。

运行：
    python lab/test_cninfo_b_class_category_routing_wrong_period_fp.py
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_b_class_category_routing as routing  # noqa: E402

CATEGORIES = routing.DEFAULT_CATEGORIES
BENCHMARK = routing.DEFAULT_BENCHMARK


class TestWrongPeriodFpLineage(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str, expected_period: str | None = None):
        return routing.route_title(title, self.config, expected_period=expected_period)

    def test_annual_year_mismatch_is_wrong_period(self) -> None:
        r = self._route("某某公司2023年年度报告", expected_period="2024")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertEqual(r.predicted_document_type, "annual_report")
        self.assertEqual(r.false_positive_reason, "wrong_period")

    def test_semi_annual_year_mismatch_is_wrong_period(self) -> None:
        r = self._route("某某公司2023年半年度报告", expected_period="2024H1")
        self.assertEqual(r.false_positive_reason, "wrong_period")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_q1_year_mismatch_is_wrong_period(self) -> None:
        r = self._route("某某公司2023年第一季度报告", expected_period="2024Q1")
        self.assertEqual(r.false_positive_reason, "wrong_period")
        self.assertEqual(r.predicted_document_type, "quarterly_report_q1")

    def test_same_year_wrong_quarter_is_wrong_period(self) -> None:
        """同年错季：标题 Q3、期望 Q1 → wrong_period。"""
        r = self._route("某某公司2024年第三季度报告", expected_period="2024Q1")
        self.assertEqual(r.false_positive_reason, "wrong_period")
        self.assertEqual(r.predicted_document_type, "quarterly_report_q3")

    def test_matching_period_has_empty_fp(self) -> None:
        """报告期一致时不得误标 wrong_period。"""
        r = self._route("平安银行股份有限公司2024年年度报告", expected_period="2024")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertEqual(r.false_positive_reason, "")
        self.assertNotEqual(r.false_positive_reason, "wrong_period")

    def test_matching_q3_has_empty_fp(self) -> None:
        r = self._route("某某公司2024年第三季度报告", expected_period="2024Q3")
        self.assertEqual(r.false_positive_reason, "")

    def test_no_expected_period_leaves_fp_empty(self) -> None:
        """未提供 expected_period 时不做期错位标注（纯 title routing）。"""
        r = self._route("某某公司2023年年度报告")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertEqual(r.false_positive_reason, "")

    def test_parse_title_report_period_helpers(self) -> None:
        self.assertEqual(
            routing.parse_title_report_period("某某公司2024年年度报告", "annual_report"),
            "2024",
        )
        self.assertEqual(
            routing.parse_title_report_period("某某公司2024年半年度报告"),
            "2024H1",
        )
        self.assertEqual(
            routing.parse_title_report_period("某某公司2024年第一季度报告"),
            "2024Q1",
        )
        self.assertEqual(
            routing.parse_title_report_period("某某公司2024年第三季度报告"),
            "2024Q3",
        )

    def test_preview_and_wrong_company_not_regressed(self) -> None:
        """wrong_period 不得污染 Run11 preview / Run12 wrong_company。"""
        preview = self._route("关于披露第一季度报告的提示性公告", expected_period="2024Q1")
        self.assertEqual(preview.false_positive_reason, "announcement_preview")
        self.assertNotEqual(preview.false_positive_reason, "wrong_period")

        cross = self._route("关于披露冀东水泥半年报的提示性公告", expected_period="2024H1")
        self.assertEqual(cross.false_positive_reason, "wrong_company")
        self.assertNotEqual(cross.false_positive_reason, "wrong_period")

    def test_benchmark_suite_passes_with_wrong_period_cases(self) -> None:
        """全量 known-document benchmark（含 Run12W2 wrong_period）须 overall_pass。"""
        data = routing._load_yaml(BENCHMARK)
        docs = data.get("documents") or []
        self.assertGreaterEqual(len(docs), 34)
        fails = []
        for doc in docs:
            row = routing.evaluate_benchmark(doc, self.config)
            if not row["overall_pass"]:
                fails.append(
                    f"{row['benchmark_id']}: route={row['route_match']} "
                    f"dtype={row['document_type_match']} fp={row['false_positive_reason']!r}"
                )
        self.assertEqual(fails, [], msg="; ".join(fails))


if __name__ == "__main__":
    unittest.main()
