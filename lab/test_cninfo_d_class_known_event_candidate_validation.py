"""
D-class known event candidate intake 校验测试（无 CNINFO · 无 web）。

运行：
    python lab/test_cninfo_d_class_known_event_candidate_validation.py
"""

from __future__ import annotations

import csv
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import validate_cninfo_d_class_known_event_candidates as validator  # noqa: E402

BASE_DIR = validator.BASE_DIR
TEMPLATE = validator.DEFAULT_INPUT
VALIDATOR = os.path.join(_LAB_DIR, "validate_cninfo_d_class_known_event_candidates.py")


def _write_csv(path: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _run_validator(input_path: str, report: str, summary: str) -> int:
    return validator.main(["--input", input_path, "--report", report, "--summary", summary])


class TestKnownEventCandidateValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_empty_template_returns_waiting_for_human_input(self) -> None:
        src = os.path.join(self.tmp, "in.csv")
        shutil.copy(TEMPLATE, src)
        report = os.path.join(self.tmp, "report.csv")
        summary = os.path.join(self.tmp, "summary.md")
        rc = _run_validator(src, report, summary)
        self.assertEqual(rc, 0)
        overall, _, _ = validator.validate_candidates(src)
        self.assertEqual(overall, validator.STATUS_WAITING)

    def test_dlc003r_maps_to_restricted_shares_unlock(self) -> None:
        rows = validator.load_candidates(TEMPLATE)
        row = next(r for r in rows if r["replacement_case_id"] == "DLC003R")
        checks = validator.validate_row(row)
        comp_check = next(c for c in checks if c["check_id"] == "R003_component")
        self.assertEqual(comp_check["check_status"], "PASS")
        self.assertEqual(row["component"], "restricted_shares_unlock")

    def test_dlc006r_maps_to_shareholder_change(self) -> None:
        rows = validator.load_candidates(TEMPLATE)
        row = next(r for r in rows if r["replacement_case_id"] == "DLC006R")
        checks = validator.validate_row(row)
        comp_check = next(c for c in checks if c["check_id"] == "R003_component")
        self.assertEqual(comp_check["check_status"], "PASS")
        self.assertEqual(row["component"], "shareholder_change")

    def test_missing_company_code_rejected(self) -> None:
        row = {
            "replacement_case_id": "DLC003R",
            "replaces_case_id": "DLC003",
            "component": "restricted_shares_unlock",
            "required_behavior": "captured_normal",
            "company_code": "",
            "company_name": "测试公司",
            "event_evidence_type": "unlock_schedule_record",
            "event_evidence_description": "desc",
            "event_date_or_period": "2025-01-01",
            "source_reference": "ref",
            "human_provided": "true",
            "candidate_status": "human_candidate_provided",
            "notes": "test",
        }
        checks = validator.validate_row(row)
        code_check = next(c for c in checks if c["check_id"] == "R005_company_code")
        self.assertEqual(code_check["check_status"], "FAIL")
        overall = validator.compute_overall_status([row], checks)
        self.assertEqual(overall, validator.STATUS_REJECTED)

    def test_missing_event_evidence_rejected(self) -> None:
        row = {
            "replacement_case_id": "DLC006R",
            "replaces_case_id": "DLC006",
            "component": "shareholder_change",
            "required_behavior": "captured_normal",
            "company_code": "000001",
            "company_name": "测试",
            "event_evidence_type": "",
            "event_evidence_description": "",
            "event_date_or_period": "",
            "source_reference": "",
            "human_provided": "true",
            "candidate_status": "human_candidate_provided",
            "notes": "test",
        }
        checks = validator.validate_row(row)
        fails = [c for c in checks if c["check_status"] == "FAIL" and c["check_id"].startswith("R006")]
        self.assertGreater(len(fails), 0)

    def test_wrong_component_rejected(self) -> None:
        row = {
            "replacement_case_id": "DLC003R",
            "replaces_case_id": "DLC003",
            "component": "shareholder_change",
            "required_behavior": "captured_normal",
            "company_code": "000001",
            "company_name": "测试",
            "event_evidence_type": "unlock_schedule_record",
            "event_evidence_description": "d",
            "event_date_or_period": "2025",
            "source_reference": "r",
            "human_provided": "true",
            "candidate_status": "human_candidate_provided",
            "notes": "n",
        }
        checks = validator.validate_row(row)
        comp = next(c for c in checks if c["check_id"] == "R003_component")
        self.assertEqual(comp["check_status"], "FAIL")

    def test_duplicate_company_code_flagged(self) -> None:
        base = {
            "required_behavior": "captured_normal",
            "company_code": "000001",
            "company_name": "测试",
            "event_evidence_type": "regulatory_disclosure",
            "event_evidence_description": "d",
            "event_date_or_period": "2025",
            "source_reference": "r",
            "human_provided": "true",
            "candidate_status": "human_candidate_provided",
            "notes": "no justify",
        }
        rows = [
            {"replacement_case_id": "DLC003R", "replaces_case_id": "DLC003", "component": "restricted_shares_unlock", **base},
            {"replacement_case_id": "DLC006R", "replaces_case_id": "DLC006", "component": "shareholder_change", **base},
        ]
        dup_checks = validator.validate_duplicate_codes(rows)
        self.assertTrue(any(c["check_id"] == "R010_duplicate_company_code" for c in dup_checks))
        self.assertTrue(any(c["check_status"] == "FAIL" for c in dup_checks))

    def test_no_cninfo_web_calls(self) -> None:
        src = os.path.join(self.tmp, "in.csv")
        shutil.copy(TEMPLATE, src)
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            with mock.patch("urllib.request.urlopen") as urlopen_mock:
                rc = _run_validator(
                    src,
                    os.path.join(self.tmp, "r.csv"),
                    os.path.join(self.tmp, "s.md"),
                )
                self.assertEqual(rc, 0)
                get_mock.assert_not_called()
                post_mock.assert_not_called()
                urlopen_mock.assert_not_called()

    def test_validation_report_generated(self) -> None:
        src = os.path.join(self.tmp, "in.csv")
        report = os.path.join(self.tmp, "report.csv")
        summary = os.path.join(self.tmp, "summary.md")
        shutil.copy(TEMPLATE, src)
        _run_validator(src, report, summary)
        self.assertTrue(os.path.isfile(report))
        self.assertTrue(os.path.isfile(summary))
        with open(report, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreater(len(rows), 0)

    def test_input_template_not_modified(self) -> None:
        src = os.path.join(self.tmp, "in.csv")
        shutil.copy(TEMPLATE, src)
        before = open(src, encoding="utf-8").read()
        _run_validator(
            src,
            os.path.join(self.tmp, "r.csv"),
            os.path.join(self.tmp, "s.md"),
        )
        after = open(src, encoding="utf-8").read()
        self.assertEqual(before, after)


def main() -> None:
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
