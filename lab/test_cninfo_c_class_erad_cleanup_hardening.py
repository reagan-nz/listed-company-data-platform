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

    def test_case8_snapshot_dryrun_write_guard_refuses_full(self) -> None:
        from cninfo_c_class_erad_cleanup_guard import (
            PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN,
            assert_safe_c_class_snapshot_dryrun_write_root,
            is_protected_c_class_production_snapshot_root,
            resolve_standard_snapshot_dryrun_output_root,
        )

        full = os.path.join(BASE_DIR, SNAPSHOT_FULL)
        self.assertTrue(is_protected_c_class_production_snapshot_root(full))
        with self.assertRaisesRegex(
            RuntimeError, PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN
        ):
            assert_safe_c_class_snapshot_dryrun_write_root(full)
        isolated = resolve_standard_snapshot_dryrun_output_root(None)
        self.assertIn("_mock_snapshot_batch_standard_dryrun_isolated", isolated)

    def test_case9_authoritative_dual_layer_index_write_forbidden(self) -> None:
        from cninfo_c_class_erad_cleanup_guard import (
            AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            DUAL_LAYER_INDEX_WRITE_FORBIDDEN,
            assert_authoritative_dual_layer_index_write_forbidden,
            assert_safe_erad_audit_write_path,
            is_authoritative_dual_layer_index_path,
        )

        auth = os.path.join(BASE_DIR, AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL)
        self.assertTrue(is_authoritative_dual_layer_index_path(auth))
        probe = os.path.join(auth, "qa_closure_dual_layer_evidence_index.csv")
        with self.assertRaisesRegex(RuntimeError, DUAL_LAYER_INDEX_WRITE_FORBIDDEN):
            assert_authoritative_dual_layer_index_write_forbidden(probe)
        # 即使误把权威索引当作 allowed_audit_root，也必须拒绝
        with self.assertRaisesRegex(RuntimeError, DUAL_LAYER_INDEX_WRITE_FORBIDDEN):
            assert_safe_erad_audit_write_path(
                probe,
                allowed_audit_root_rel=AUTHORITATIVE_DUAL_LAYER_INDEX_ROOT_REL,
            )

    def test_case10_frozen_mock_cohort_write_isolation(self) -> None:
        from cninfo_c_class_erad_cleanup_guard import (
            FROZEN_MOCK_COHORT_WRITE_FORBIDDEN,
            assert_frozen_mock_cohort_write_forbidden,
            load_frozen_mock_cohort_roots,
            resolve_frozen_mock_cohort_root_id,
        )

        load_frozen_mock_cohort_roots.cache_clear()
        frozen = load_frozen_mock_cohort_roots()
        self.assertTrue(frozen)
        # MOCK8（pre-EXECUTE wall）必须被识别为冻结根
        mock8 = (
            "outputs/validation/_mock_c_fm06_pre_execute_safe_snapshot_wall"
        )
        self.assertEqual(
            resolve_frozen_mock_cohort_root_id(mock8), "C-ROOT-MOCK8"
        )
        with self.assertRaisesRegex(
            RuntimeError, FROZEN_MOCK_COHORT_WRITE_FORBIDDEN
        ):
            assert_frozen_mock_cohort_write_forbidden(mock8)
        # allow 列表放行
        allowed = assert_frozen_mock_cohort_write_forbidden(
            mock8, allow_root_ids=("C-ROOT-MOCK8",)
        )
        self.assertTrue(allowed.endswith("safe_snapshot_wall") or "fm06" in allowed)
        # 未登记 ephemeral mock 不受冻结守卫约束
        ephemeral = (
            "outputs/validation/_mock_c_fm12_cli_test_tmp_isolation_probe"
        )
        self.assertIsNone(resolve_frozen_mock_cohort_root_id(ephemeral))
        assert_frozen_mock_cohort_write_forbidden(ephemeral)

    def test_case11_dryrun_fingerprint_lineage_extension_stable(self) -> None:
        from cninfo_c_class_erad_cleanup_guard import (
            fingerprint_isolated_snapshot_dryrun,
        )

        root = (
            "outputs/validation/_mock_c_fm02_slice1_190_validation_cohort"
        )
        base = fingerprint_isolated_snapshot_dryrun(
            root, gate="PASS_WITH_CAVEAT", company_count=190
        )
        base2 = fingerprint_isolated_snapshot_dryrun(
            root, gate="PASS_WITH_CAVEAT", company_count=190
        )
        self.assertEqual(base["fingerprint_sha256"], base2["fingerprint_sha256"])
        self.assertNotIn("lineage_artifacts", base)
        ext = fingerprint_isolated_snapshot_dryrun(
            root,
            gate="PASS_WITH_CAVEAT",
            company_count=190,
            lineage_artifacts=True,
        )
        self.assertTrue(ext.get("lineage_artifacts"))
        self.assertNotEqual(base["fingerprint_sha256"], ext["fingerprint_sha256"])
        # FM-02 应含 lineage 产物
        self.assertTrue(
            ext["files_present"].get("filtered_universe_included.yaml")
        )
        self.assertTrue(ext["files_present"].get("cohort_lineage_matrix.csv"))


if __name__ == "__main__":
    unittest.main()
