"""
C-class Era D cleanup 硬化回归测试（无 CNINFO · 不触碰生产根）。

运行：
    python -m pytest lab/test_cninfo_c_class_erad_cleanup_hardening.py -q
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    CLEANUP_REFUSED_MSG,
    assert_safe_test_cleanup_path,
    create_c_class_mock_test_output_root,
    is_allowed_mock_test_cleanup_path,
    is_protected_c_class_production_root,
    normalize_cleanup_path,
    safe_cleanup_temp_output_root,
)

PHASE3_HARVEST = "outputs/harvest/cninfo_c_class/phase3_batch_500_001"
PHASE35_RESUME_HARVEST = "outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume"
SNAPSHOT_491 = (
    "outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491"
)
SNAPSHOT_FULL = "outputs/snapshot/cninfo_c_class/full"


class TestCClassEradCleanupHardening(unittest.TestCase):
    def test_case1_mock_path_cleanup_allowed(self) -> None:
        tmp = create_c_class_mock_test_output_root()
        try:
            self.assertTrue(is_allowed_mock_test_cleanup_path(tmp))
            marker = os.path.join(tmp, "probe.txt")
            with open(marker, "w", encoding="utf-8") as fh:
                fh.write("x")
            assert_safe_test_cleanup_path(tmp)
            safe_cleanup_temp_output_root(tmp)
            self.assertFalse(os.path.exists(tmp))
        finally:
            if os.path.isdir(tmp):
                safe_cleanup_temp_output_root(tmp)

    def test_case2_production_harvest_root_refused(self) -> None:
        target = os.path.join(BASE_DIR, PHASE3_HARVEST)
        self.assertTrue(is_protected_c_class_production_root(target))
        with self.assertRaises(RuntimeError) as ctx:
            assert_safe_test_cleanup_path(target)
        self.assertIn(CLEANUP_REFUSED_MSG, str(ctx.exception))

    def test_case3_production_snapshot_491_refused(self) -> None:
        target = os.path.join(BASE_DIR, SNAPSHOT_491, "000001.json")
        self.assertTrue(is_protected_c_class_production_root(target))
        with self.assertRaises(RuntimeError):
            safe_cleanup_temp_output_root(target)

    def test_case4_production_snapshot_full_refused(self) -> None:
        target = os.path.join(BASE_DIR, SNAPSHOT_FULL)
        with self.assertRaises(RuntimeError):
            assert_safe_test_cleanup_path(target)

    def test_case5_phase35_resume_harvest_refused(self) -> None:
        target = os.path.join(BASE_DIR, PHASE35_RESUME_HARVEST, "reports")
        with self.assertRaises(RuntimeError):
            safe_cleanup_temp_output_root(target)

    def test_case6_path_normalization_cannot_bypass_guard(self) -> None:
        tricky = os.path.join(
            BASE_DIR,
            "outputs/harvest/cninfo_c_class/phase3_batch_500_001/../phase3_batch_500_001",
            "normalized",
        )
        norm = normalize_cleanup_path(tricky)
        self.assertTrue(is_protected_c_class_production_root(norm))
        with self.assertRaises(RuntimeError):
            assert_safe_test_cleanup_path(tricky)

        suffix_trick = PHASE3_HARVEST + "/."
        with self.assertRaises(RuntimeError):
            assert_safe_test_cleanup_path(suffix_trick)

    def test_case7_cninfo_not_called(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch("requests.post") as post_mock:
            tmp = create_c_class_mock_test_output_root(
                parent_rel="outputs/snapshot/cninfo_c_class/_mock_erad_test"
            )
            try:
                assert_safe_test_cleanup_path(tmp)
                self.assertTrue(is_allowed_mock_test_cleanup_path(tmp))
            finally:
                safe_cleanup_temp_output_root(tmp)
        get_mock.assert_not_called()
        post_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
