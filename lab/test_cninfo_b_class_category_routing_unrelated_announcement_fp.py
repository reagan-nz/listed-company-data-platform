"""
B 类 category routing — unrelated_announcement false_positive lineage 单测。

覆盖 validation_design §7「其他无关公告」：含报告字样但非定期全文
（补充/更正/取消披露/审计机构/内控评价/非标意见），须标注
false_positive_reason=unrelated_announcement，且不回退 preview/wrong_company/wrong_period。

离线 only · 无 CNINFO · 无 live。

运行：
    python lab/test_cninfo_b_class_category_routing_unrelated_announcement_fp.py
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


class TestUnrelatedAnnouncementFpLineage(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str, expected_period: str | None = None):
        return routing.route_title(title, self.config, expected_period=expected_period)

    def test_supplement_announcement_is_unrelated(self) -> None:
        r = self._route("关于2024年年度报告的补充公告")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertEqual(r.classification_status, "title_excluded_from_periodic_but_routed")
        self.assertEqual(r.false_positive_reason, "unrelated_announcement")

    def test_correction_announcement_is_unrelated(self) -> None:
        r = self._route("关于2024年年度报告的更正公告")
        self.assertEqual(r.false_positive_reason, "unrelated_announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_cancel_disclosure_is_unrelated(self) -> None:
        r = self._route("关于取消披露2024年年度报告的公告")
        self.assertEqual(r.false_positive_reason, "unrelated_announcement")
        self.assertNotEqual(r.false_positive_reason, "announcement_preview")

    def test_auditor_appointment_is_unrelated_not_periodic(self) -> None:
        """修复前误 route periodic；须排除并标 unrelated_announcement。"""
        r = self._route("关于聘任2024年年度报告审计机构的公告")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.false_positive_reason, "unrelated_announcement")

    def test_internal_control_eval_is_unrelated(self) -> None:
        """含子串「年度报告」的内控评价报告，非年报全文。"""
        r = self._route("某某公司2024年年度报告内部控制评价报告")
        self.assertEqual(r.false_positive_reason, "unrelated_announcement")
        self.assertEqual(r.classification_status, "title_excluded_from_periodic_but_routed")

    def test_nonstandard_opinion_is_unrelated(self) -> None:
        r = self._route("关于2024年年度报告非标意见涉及事项的专项说明")
        self.assertEqual(r.false_positive_reason, "unrelated_announcement")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")

    def test_full_annual_report_not_unrelated(self) -> None:
        """正式年报全文不得误标 unrelated_announcement。"""
        r = self._route("某某公司2024年年度报告")
        self.assertEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertEqual(r.false_positive_reason, "")
        self.assertNotEqual(r.false_positive_reason, "unrelated_announcement")

    def test_preview_wrong_company_wrong_period_not_regressed(self) -> None:
        """不得污染 Run11 preview / Wave1 wrong_company / Wave2 wrong_period。"""
        preview = self._route("关于披露第一季度报告的提示性公告")
        self.assertEqual(preview.false_positive_reason, "announcement_preview")
        self.assertNotEqual(preview.false_positive_reason, "unrelated_announcement")

        cross = self._route("关于披露冀东水泥半年报的提示性公告")
        self.assertEqual(cross.false_positive_reason, "wrong_company")
        self.assertNotEqual(cross.false_positive_reason, "unrelated_announcement")

        period = self._route("某某公司2023年年度报告", expected_period="2024")
        self.assertEqual(period.false_positive_reason, "wrong_period")
        self.assertEqual(period.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertNotEqual(period.false_positive_reason, "unrelated_announcement")

        delayed = self._route("关于延期披露2024年年度报告的公告")
        self.assertEqual(delayed.false_positive_reason, "delayed_disclosure_notice")
        self.assertNotEqual(delayed.false_positive_reason, "unrelated_announcement")

    def test_is_unrelated_helper(self) -> None:
        self.assertTrue(
            routing._is_unrelated_announcement("关于2024年年度报告的补充公告")
        )
        self.assertTrue(
            routing._is_unrelated_announcement("关于聘任2024年年度报告审计机构的公告")
        )
        self.assertFalse(routing._is_unrelated_announcement("某某公司2024年年度报告"))
        self.assertFalse(
            routing._is_unrelated_announcement("关于披露第一季度报告的提示性公告")
        )

    def test_benchmark_suite_passes_with_unrelated_cases(self) -> None:
        """全量 known-document benchmark（含 Run12W4 unrelated）须 overall_pass。"""
        data = routing._load_yaml(BENCHMARK)
        docs = data.get("documents") or []
        self.assertGreaterEqual(len(docs), 38)
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
