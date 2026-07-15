"""
B-FM-23：监事会决议 known-document 晋升锁测（离线）。

覆盖：
- supervisory_board_known_001（监事会会议决议）已为 ready
- title_pattern 与 board_resolution / 股东会决议族 / 非决议监事会标题可区分
- harvest 标题经既有 general_006 路由预测 announcement → general
- 董事会决议仍为 board_resolution；股东会路径不回退
- 不重开 shareholder_meeting_known_001–007 / board_resolution_known_001 字段

无 CNINFO · 无 live · 不造 §7 FP。

运行：
    python lab/test_cninfo_b_class_supervisory_board_known_001_promotion.py
"""

from __future__ import annotations

import os
import sys
import unittest

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_b_class_category_routing as routing  # noqa: E402
import validate_cninfo_b_class_corpus_retrieval as retrieval  # noqa: E402

KNOWN_YAML = os.path.join(
    _BASE, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)

# harvest 证据标题（只读引用；BD2E091）
HARVEST_TITLE = "第六届监事会第二十四次会议决议公告"
PATTERN = "第二十四次会议决议公告"
BOARD_PATTERN = "董事会决议公告"
BOARD_TITLE = "第七届董事会第十一次会议决议公告"
BOARD_SHORT = "董事会决议公告"
SM_RES = "2025年第二次临时股东大会决议公告"
SM_SHORT_RES = "2025年第五次临时股东会决议公告"
SM_ANNUAL = "2024年年度股东会决议公告"
AUDIT_OPINION = "监事会关于公司2024年年度报告的审核意见"
DELAY_ELECTION = "昂立教育关于董事会、监事会延期换届的公告"
GENERAL_006 = "监事会决议公告"


def _load_cases(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]


def _by_id(cases: list, case_id: str) -> dict:
    for c in cases:
        if c["case_id"] == case_id:
            return c
    raise KeyError(case_id)


class TestSupervisoryBoardKnown001Promotion(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = routing._load_yaml(routing.DEFAULT_CATEGORIES)
        cls.known = _load_cases(KNOWN_YAML)

    def test_supervisory_board_known_001_ready_fields(self) -> None:
        c = _by_id(self.known, "supervisory_board_known_001")
        self.assertEqual(c["case_status"], "ready")
        self.assertEqual(c["company_code"], "300017")
        self.assertEqual(c["company_name"], "网宿科技")
        self.assertEqual(c["title_pattern"], PATTERN)
        self.assertEqual(c["date_start"], "2025-06-26")
        self.assertEqual(c["date_end"], "2025-06-29")
        self.assertEqual(c["source_id"], "cninfo_general_announcement_pdf")
        self.assertEqual(c["expected_document_type"], "announcement")
        self.assertEqual(c["expected_route_to"], "cninfo_general_announcement_pdf")
        self.assertTrue(c["expected_pdf_url_available"])
        self.assertIn(PATTERN, HARVEST_TITLE)
        self.assertNotIn("董事会", c["title_pattern"])
        self.assertNotIn("股东大会", c["title_pattern"])
        self.assertNotIn("股东会", c["title_pattern"])

    def test_title_patterns_mutually_exclusive(self) -> None:
        """监事会决议 pattern 不误命中董事会 / 股东会；非决议监事会标题不命中。"""
        self.assertTrue(retrieval._title_matches(HARVEST_TITLE, PATTERN))
        self.assertFalse(retrieval._title_matches(HARVEST_TITLE, BOARD_PATTERN))
        self.assertFalse(retrieval._title_matches(BOARD_TITLE, PATTERN))
        self.assertFalse(retrieval._title_matches(BOARD_SHORT, PATTERN))
        self.assertFalse(retrieval._title_matches(SM_RES, PATTERN))
        self.assertFalse(retrieval._title_matches(SM_SHORT_RES, PATTERN))
        self.assertFalse(retrieval._title_matches(SM_ANNUAL, PATTERN))
        # 非决议监事会：审核意见 / 延期换届
        self.assertFalse(retrieval._title_matches(AUDIT_OPINION, PATTERN))
        self.assertFalse(retrieval._title_matches(DELAY_ELECTION, PATTERN))
        # general_006 短标题不含本 case 的届次子串（已知限制；本包锚定长标题）
        self.assertFalse(retrieval._title_matches(GENERAL_006, PATTERN))

    def test_board_resolution_and_shareholder_meeting_anchors_untouched(self) -> None:
        """不削弱既有董事会 / 股东会 known 锚点。"""
        br = _by_id(self.known, "board_resolution_known_001")
        self.assertEqual(br["case_status"], "ready")
        self.assertEqual(br["company_code"], "000581")
        self.assertEqual(br["title_pattern"], BOARD_PATTERN)
        self.assertEqual(br["expected_document_type"], "board_resolution")

        sm_expect = {
            "shareholder_meeting_known_001": "股东大会通知",
            "shareholder_meeting_known_002": "股东大会的通知",
            "shareholder_meeting_known_003": "股东大会决议",
            "shareholder_meeting_known_004": "股东大会的公告",
            "shareholder_meeting_known_005": "临时股东会决议",
            "shareholder_meeting_known_006": "股东会的通知",
            "shareholder_meeting_known_007": "年度股东会决议",
        }
        for case_id, pattern in sm_expect.items():
            c = _by_id(self.known, case_id)
            self.assertEqual(c["case_status"], "ready", case_id)
            self.assertEqual(c["title_pattern"], pattern, case_id)
            self.assertEqual(c["expected_document_type"], "shareholder_meeting_material", case_id)

    def test_harvest_title_routes_announcement_not_board_resolution(self) -> None:
        r = routing.route_title(HARVEST_TITLE, self.config)
        self.assertEqual(r.predicted_document_type, "announcement")
        self.assertEqual(r.predicted_route_to, "cninfo_general_announcement_pdf")
        self.assertEqual(r.predicted_classification, "general_announcement")
        self.assertNotEqual(r.predicted_document_type, "board_resolution")
        self.assertNotEqual(r.predicted_document_type, "shareholder_meeting_material")

        r006 = routing.route_title(GENERAL_006, self.config)
        self.assertEqual(r006.predicted_document_type, "announcement")
        self.assertEqual(r006.predicted_route_to, "cninfo_general_announcement_pdf")

    def test_board_and_shareholder_meeting_routes_untouched(self) -> None:
        """董事会决议 / 股东会决议路由不回退。"""
        r_board = routing.route_title(BOARD_TITLE, self.config)
        self.assertEqual(r_board.predicted_document_type, "board_resolution")
        r_sm = routing.route_title(SM_RES, self.config)
        self.assertEqual(r_sm.predicted_document_type, "shareholder_meeting_material")
        r_short = routing.route_title(SM_SHORT_RES, self.config)
        self.assertEqual(r_short.predicted_document_type, "shareholder_meeting_material")

    def test_distinct_from_board_resolution_company_and_pattern(self) -> None:
        """监事会 known 与董事会 known 公司、pattern、document_type 均可区分。"""
        sb = _by_id(self.known, "supervisory_board_known_001")
        br = _by_id(self.known, "board_resolution_known_001")
        self.assertNotEqual(sb["company_code"], br["company_code"])
        self.assertNotEqual(sb["title_pattern"], br["title_pattern"])
        self.assertNotEqual(sb["expected_document_type"], br["expected_document_type"])
        self.assertEqual(sb["expected_route_to"], br["expected_route_to"])


if __name__ == "__main__":
    unittest.main()
