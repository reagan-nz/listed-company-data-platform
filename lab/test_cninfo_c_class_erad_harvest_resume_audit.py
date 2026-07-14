"""
C-class Era D harvest resume audit 回归测试（无 CNINFO · 不触碰生产根）。

运行：
    python lab/test_cninfo_c_class_erad_harvest_resume_audit.py
"""

from __future__ import annotations

import io
import csv
import os
import sys
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    CLEANUP_REFUSED_MSG,
    assert_safe_erad_audit_write_path,
    create_c_class_mock_test_output_root,
    is_protected_c_class_production_root,
    safe_cleanup_temp_output_root,
)
from run_cninfo_c_class_harvest_resume_audit import (  # noqa: E402
    HARVEST_RESUME_LIVE_APPROVAL_REQUIRED,
    REPORT_CSV_NAME,
    SUMMARY_MD_NAME,
    audit_harvest_subtree,
    build_parser,
    main,
    run_audit,
)

PHASE3_HARVEST = "outputs/harvest/cninfo_c_class/phase3_batch_500_001"
SNAPSHOT_491 = (
    "outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491"
)
SNAPSHOT_FULL = "outputs/snapshot/cninfo_c_class/full"
DEFAULT_AUDIT_ROOT = "outputs/validation/cninfo_c_class_erad_harvest_resume_audit"


class TestCClassEradHarvestResumeAudit(unittest.TestCase):
    def test_case1_dry_run_does_not_call_cninfo(self) -> None:
        mock_out = create_c_class_mock_test_output_root(
            parent_rel="outputs/validation/_mock_erad_audit_test"
        )
        try:
            args = build_parser().parse_args([
                "--dry-run",
                "--harvest-root", "outputs/harvest/cninfo_c_class",
                "--output-root", mock_out,
            ])
            with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
                meta = run_audit(args)
            get_mock.assert_not_called()
            post_mock.assert_not_called()
            self.assertEqual(meta["cninfo_calls"], 0)
            self.assertTrue(os.path.isfile(os.path.join(mock_out, "reports", REPORT_CSV_NAME)))
        finally:
            safe_cleanup_temp_output_root(mock_out)

    def test_case2_refuses_writing_into_production_harvest_root(self) -> None:
        target = os.path.join(BASE_DIR, PHASE3_HARVEST, "reports", "probe.csv")
        with self.assertRaises(RuntimeError) as ctx:
            assert_safe_erad_audit_write_path(target)
        self.assertIn(CLEANUP_REFUSED_MSG, str(ctx.exception))

    def test_case3_refuses_writing_into_production_snapshot_roots(self) -> None:
        for rel in (SNAPSHOT_491, SNAPSHOT_FULL):
            target = os.path.join(BASE_DIR, rel, "probe.json")
            self.assertTrue(is_protected_c_class_production_root(target))
            with self.assertRaises(RuntimeError):
                assert_safe_erad_audit_write_path(target)

    def test_case4_allows_writing_under_audit_root_or_mock(self) -> None:
        audit_reports = os.path.join(
            BASE_DIR, DEFAULT_AUDIT_ROOT, "reports", "test_probe.csv"
        )
        assert_safe_erad_audit_write_path(audit_reports)

        mock_out = create_c_class_mock_test_output_root(
            parent_rel="outputs/validation/_mock_erad_audit_test"
        )
        try:
            probe = os.path.join(mock_out, "reports", "x.csv")
            assert_safe_erad_audit_write_path(probe)
        finally:
            safe_cleanup_temp_output_root(mock_out)

    def test_case5_protected_root_guard_still_enforced(self) -> None:
        tricky = os.path.join(
            BASE_DIR,
            "outputs/harvest/cninfo_c_class/phase3_batch_500_001/../phase3_batch_500_001",
            "quality",
            "x.csv",
        )
        with self.assertRaises(RuntimeError):
            assert_safe_erad_audit_write_path(tricky)

    def test_case6_produces_expected_artifacts_in_mock_tree(self) -> None:
        mock_harvest = create_c_class_mock_test_output_root(
            parent_rel="outputs/harvest/cninfo_c_class/_mock_live_test",
            prefix="audit_harvest_",
        )
        mock_out = create_c_class_mock_test_output_root(
            parent_rel="outputs/validation/_mock_erad_audit_test",
            prefix="audit_out_",
        )
        try:
            os.makedirs(os.path.join(mock_harvest, "normalized", "company_basic_profile"), exist_ok=True)
            with open(
                os.path.join(mock_harvest, "normalized", "company_basic_profile", "000001.json"),
                "w",
                encoding="utf-8",
            ) as fh:
                fh.write('{"company_code":"000001"}')

            universe = [{"company_code": "000001", "company_name": "测试", "board": "SZSE"}]
            reports, ledger, counts = audit_harvest_subtree(
                "863_primary", mock_harvest, universe, audit_mode="dry_run",
            )
            self.assertEqual(len(reports), 1)
            self.assertIn(reports[0]["resume_state"], ("needs_review", "partial", "complete"))
            self.assertGreaterEqual(len(ledger), 10)

            args = build_parser().parse_args([
                "--dry-run",
                "--harvest-root", mock_harvest,
                "--output-root", mock_out,
            ])
            run_audit(args)
            report_path = os.path.join(mock_out, "reports", REPORT_CSV_NAME)
            summary_path = os.path.join(mock_out, "reports", SUMMARY_MD_NAME)
            self.assertTrue(os.path.isfile(report_path))
            self.assertTrue(os.path.isfile(summary_path))
            with open(report_path, encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
            self.assertGreaterEqual(len(rows), 1)
        finally:
            safe_cleanup_temp_output_root(mock_out)
            safe_cleanup_temp_output_root(mock_harvest)

    def test_case7_live_without_approval_rejected(self) -> None:
        err1 = io.StringIO()
        with mock.patch("sys.stderr", err1):
            with self.assertRaises(SystemExit) as ctx:
                main(["--live"])
            self.assertEqual(ctx.exception.code, 2)
        self.assertIn(HARVEST_RESUME_LIVE_APPROVAL_REQUIRED, err1.getvalue())

        err2 = io.StringIO()
        with mock.patch("sys.stderr", err2):
            with self.assertRaises(SystemExit) as ctx:
                main(["--live", "--approve-harvest-resume-live"])
            self.assertEqual(ctx.exception.code, 2)
        self.assertIn("not implemented", err2.getvalue())


if __name__ == "__main__":
    unittest.main()
