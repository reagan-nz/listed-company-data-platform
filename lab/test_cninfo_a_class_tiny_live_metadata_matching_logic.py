"""
A-class tiny live metadata matching logic 测试（纯离线 · 无 CNINFO）。

运行：
    python lab/test_cninfo_a_class_tiny_live_metadata_matching_logic.py
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_a_class_tiny_live_metadata_validation as runner  # noqa: E402


class TestMatchingLogic(unittest.TestCase):
    def test_annual_rejects_semi_annual(self) -> None:
        matched, reason = runner.match_title_for_report_type(
            "上海浦东发展银行股份有限公司2024年半年度报告",
            "annual_report",
            "2024-12-31",
        )
        self.assertFalse(matched)
        self.assertIn("半年", reason)

    def test_annual_accepts_annual_report(self) -> None:
        matched, _ = runner.match_title_for_report_type(
            "上海浦东发展银行股份有限公司2024年年度报告",
            "annual_report",
            "2024-12-31",
        )
        self.assertTrue(matched)

    def test_annual_rejects_q1_q3_titles(self) -> None:
        for title in (
            "某公司2024年第一季度报告",
            "某公司2024年第三季度报告",
        ):
            matched, _ = runner.match_title_for_report_type(
                title, "annual_report", "2024-12-31"
            )
            self.assertFalse(matched, msg=title)

    def test_semi_annual_accepts_semi_annual(self) -> None:
        matched, _ = runner.match_title_for_report_type(
            "2024年半年度报告",
            "semi_annual_report",
            "2024-06-30",
        )
        self.assertTrue(matched)

    def test_quarterly_q1_accepts_q1(self) -> None:
        for title in ("2025年第一季度报告", "华兴源创：2025年一季度报告"):
            matched, _ = runner.match_title_for_report_type(
                title, "quarterly_report_q1", "2025-03-31"
            )
            self.assertTrue(matched, msg=title)

    def test_quarterly_q3_accepts_q3(self) -> None:
        for title in ("2024年第三季度报告", "2024年三季度报告"):
            matched, _ = runner.match_title_for_report_type(
                title, "quarterly_report_q3", "2024-09-30"
            )
            self.assertTrue(matched, msg=title)

    def test_chinese_english_title_rejected(self) -> None:
        matched, reason = runner.match_title_for_report_type(
            "2024年第三季度报告（英文）",
            "quarterly_report_q3",
            "2024-09-30",
        )
        self.assertFalse(matched)
        self.assertIn("english", reason)

    def test_english_title_rejected(self) -> None:
        matched, reason = runner.match_title_for_report_type(
            "2024 Q3 Report English Version",
            "quarterly_report_q3",
            "2024-09-30",
        )
        self.assertFalse(matched)
        self.assertIn("english", reason)

    def test_code_name_mismatch_flagged(self) -> None:
        case = runner.UniverseCase(
            case_id="ALM003",
            company_code="688001",
            company_name="华熙生物",
            report_type="quarterly_report_q1",
            expected_period="2025-03-31",
            source_name="A类季报 metadata",
            risk_level="low",
            reason="",
        )
        issues = runner.validate_universe_code_name(case)
        self.assertTrue(any(runner.CODE_NAME_MISMATCH in i for i in issues))

    def test_pdf_download_parser_disabled(self) -> None:
        self.assertFalse(runner.PDF_DOWNLOAD_ENABLED)
        self.assertFalse(runner.PDF_PARSE_ENABLED)
        self.assertFalse(runner.ENABLE_OCR)
        self.assertFalse(runner.ENABLE_SECTION_EXTRACTION)


def main() -> None:
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
