"""
B 类 category routing — wrong_company false_positive lineage 单测。

覆盖 Phase 1 交叉披露他司报告（如「关于披露冀东水泥半年报的提示性公告」）的
route_to + false_positive_reason=wrong_company，并与本公司 announcement_preview 区分。

离线 only · 无 CNINFO · 无 live。

运行：
    python lab/test_cninfo_b_class_category_routing_wrong_company_fp.py
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


class TestWrongCompanyFpLineage(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(CATEGORIES)

    def _route(self, title: str):
        return routing.route_title(title, self.config)

    def test_jidong_cement_cross_disclosure_is_wrong_company(self) -> None:
        """Phase 1 P1-AUD-022 类：含提示性公告但主体为他司报告。"""
        r = self._route("关于披露冀东水泥半年报的提示性公告")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertNotEqual(r.predicted_route_to, "cninfo_periodic_report_pdf")
        self.assertEqual(r.classification_status, "title_excluded_from_periodic_but_routed")
        self.assertEqual(r.false_positive_reason, "wrong_company")
        self.assertNotEqual(r.false_positive_reason, "announcement_preview")

    def test_explicit_tasi_cross_disclosure(self) -> None:
        r = self._route("关于披露他司报告的提示性公告")
        self.assertEqual(r.false_positive_reason, "wrong_company")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_tasi_semi_annual_cross_disclosure(self) -> None:
        r = self._route("关于披露他司2024年半年度报告的提示性公告")
        self.assertEqual(r.false_positive_reason, "wrong_company")
        self.assertNotEqual(r.false_positive_reason, "announcement_preview")

    def test_entity_name_without_preview_marker(self) -> None:
        """无「提示性公告」字样的实体名交叉披露，fp 不得为空。"""
        r = self._route("关于披露某某股份有限公司2024年年度报告的公告")
        self.assertEqual(r.false_positive_reason, "wrong_company")
        self.assertEqual(r.classification_status, "title_excluded_from_periodic_but_routed")

    def test_own_period_tip_remains_announcement_preview(self) -> None:
        """本公司报告期提示仍为 announcement_preview（Run11 不回退）。"""
        r = self._route("关于披露第一季度报告的提示性公告")
        self.assertEqual(r.false_positive_reason, "announcement_preview")
        self.assertNotEqual(r.false_positive_reason, "wrong_company")

    def test_own_disclosure_tip_without_guanyu_remains_preview(self) -> None:
        r = self._route("某某公司2024年第一季度报告披露提示性公告")
        self.assertEqual(r.false_positive_reason, "announcement_preview")

    def test_delayed_disclosure_not_wrong_company(self) -> None:
        """「关于延期披露」含子串「关于披露」，不得误标 wrong_company。"""
        r = self._route("关于延期披露2024年年度报告的公告")
        self.assertEqual(r.false_positive_reason, "delayed_disclosure_notice")
        self.assertNotEqual(r.false_positive_reason, "wrong_company")

    def test_is_wrong_company_helper(self) -> None:
        self.assertTrue(
            routing._is_wrong_company_cross_disclosure("关于披露冀东水泥半年报的提示性公告")
        )
        self.assertFalse(
            routing._is_wrong_company_cross_disclosure("关于披露第一季度报告的提示性公告")
        )
        self.assertFalse(
            routing._is_wrong_company_cross_disclosure("关于延期披露2024年年度报告的公告")
        )

    def test_benchmark_suite_passes_with_wrong_company_cases(self) -> None:
        """全量 known-document benchmark（含 Run12 wrong_company）须 overall_pass。"""
        data = routing._load_yaml(BENCHMARK)
        docs = data.get("documents") or []
        self.assertGreaterEqual(len(docs), 30)
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
