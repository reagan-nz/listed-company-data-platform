"""
B 类 category routing — announcement_preview false_positive lineage 单测。

覆盖 Phase 1 主假阳性类（披露提示性公告 / 提示性公告 / 预告公告）的
route_to + false_positive_reason=announcement_preview，以及更正公告不得进 periodic。

离线 only · 无 CNINFO · 无 live。

运行：
    python lab/test_cninfo_b_class_category_routing_preview_fp.py
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_b_class_category_routing as routing  # noqa: E402

BASE_DIR = routing.BASE_DIR
CATEGORIES = routing.DEFAULT_CATEGORIES
BENCHMARK = routing.DEFAULT_BENCHMARK


class TestAnnouncementPreviewFpLineage(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_disclosure_tip_q1_preview_fp(self) -> None:
        r = self._route("某某公司2024年第一季度报告披露提示性公告")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertEqual(r.classification_status, "title_excluded_from_periodic_but_routed")
        self.assertEqual(r.false_positive_reason, "announcement_preview")

    def test_disclosure_tip_q3_preview_fp(self) -> None:
        r = self._route("某某公司2024年第三季度报告披露提示性公告")
        self.assertEqual(r.false_positive_reason, "announcement_preview")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_tip_notice_with_guanyu_disclosure(self) -> None:
        r = self._route("关于披露第一季度报告的提示性公告")
        self.assertEqual(r.false_positive_reason, "announcement_preview")
        self.assertEqual(r.predicted_classification, "excluded_from_periodic_but_routed")

    def test_yugao_announcement_is_preview_not_delayed(self) -> None:
        r = self._route("某某公司2024年半年度报告预告公告")
        self.assertEqual(r.false_positive_reason, "announcement_preview")
        self.assertNotEqual(r.false_positive_reason, "delayed_disclosure_notice")

    def test_correction_announcement_not_periodic(self) -> None:
        r = self._route("关于2024年年度报告的更正公告")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.classification_status, "title_excluded_from_periodic_but_routed")

    def test_delayed_disclosure_reason_unchanged(self) -> None:
        r = self._route("关于延期披露2024年年度报告的公告")
        self.assertEqual(r.false_positive_reason, "delayed_disclosure_notice")

    def test_summary_reason_unchanged(self) -> None:
        r = self._route("2024年年度报告摘要")
        self.assertEqual(r.false_positive_reason, "summary")

    def test_jiedu_maps_to_summary(self) -> None:
        r = self._route("2024年年度报告解读")
        self.assertEqual(r.false_positive_reason, "summary")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_benchmark_suite_passes_with_preview_cases(self) -> None:
        """全量 known-document benchmark（含 Run11 preview/correction）须 overall_pass。"""
        data = routing._load_yaml(BENCHMARK)
        docs = data.get("documents") or []
        self.assertGreaterEqual(len(docs), 26)
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
