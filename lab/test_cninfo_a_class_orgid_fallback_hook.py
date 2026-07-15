"""
A-class orgId 离线回退接入 resolve_orgid 的单元测试（mock topSearch · CNINFO = 0）。

覆盖：
1. topSearch 失败 + 离线命中 → 返回映射 orgId，cninfo 仅计 topSearch 一次
2. topSearch 失败 + 离线未命中 → 保留原错误，显式 miss，不伪造
3. topSearch 成功 → 不走 fallback，保持先验行为
4. slice2 orgid fallback retry 路径隔离（universe/root/cap）

运行：
    python lab/test_cninfo_a_class_orgid_fallback_hook.py
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import cninfo_a_class_orgid_mapping_fallback as fallback  # noqa: E402
import run_cninfo_a_class_phase2_metadata_expansion as runner  # noqa: E402
import run_cninfo_a_class_tiny_live_metadata_validation as tiny_live  # noqa: E402


class _FakeResp:
    def __init__(self, status_code: int = 200, payload=None, ok: bool = True):
        self.status_code = status_code
        self._payload = payload if payload is not None else []
        self.ok = ok

    def json(self):
        return self._payload


class TestOrgidFallbackHook(unittest.TestCase):
    def setUp(self) -> None:
        tiny_live._ORGID_CACHE.clear()
        fallback.reset_default_index()

    def tearDown(self) -> None:
        tiny_live._ORGID_CACHE.clear()

    def test_topsearch_miss_uses_offline_fallback_for_known_codes(self) -> None:
        """topSearch 返回空 orgId 时，AD2E578/590/598 码应离线恢复。"""
        stats = tiny_live.LiveStats()
        with mock.patch.object(
            tiny_live.requests,
            "post",
            return_value=_FakeResp(payload=[{"code": "688605", "orgId": None}]),
        ) as post_mock:
            org_id, err = tiny_live.resolve_orgid("688605", stats)
        self.assertEqual(org_id, "9900059045")
        self.assertEqual(err, "")
        self.assertEqual(stats.cninfo_requests, 1)
        self.assertEqual(stats.orgid_offline_fallback_hits, 1)
        self.assertEqual(stats.orgid_offline_fallback_misses, 0)
        self.assertIn("688605", stats.orgid_offline_fallback_sources)
        self.assertFalse(
            stats.orgid_offline_fallback_sources["688605"].startswith("miss:")
        )
        self.assertEqual(post_mock.call_count, 1)

    def test_topsearch_miss_and_offline_miss_preserves_error(self) -> None:
        """映射未命中不得静默成功；保留 topSearch 错误并显式记 miss。"""
        stats = tiny_live.LiveStats()
        with mock.patch.object(
            tiny_live.requests,
            "post",
            return_value=_FakeResp(payload=[]),
        ):
            org_id, err = tiny_live.resolve_orgid("000000", stats)
        self.assertEqual(org_id, "")
        self.assertEqual(err, "empty_response")
        self.assertEqual(stats.cninfo_requests, 1)
        self.assertEqual(stats.orgid_offline_fallback_hits, 0)
        self.assertEqual(stats.orgid_offline_fallback_misses, 1)
        self.assertTrue(
            stats.orgid_offline_fallback_sources["000000"].startswith("miss:")
        )

    def test_topsearch_hit_skips_offline_fallback(self) -> None:
        """topSearch 命中时保持先验行为，不增加 fallback 计数。"""
        stats = tiny_live.LiveStats()
        with mock.patch.object(
            tiny_live.requests,
            "post",
            return_value=_FakeResp(
                payload=[{"code": "600000", "orgId": "gssh0600000"}]
            ),
        ):
            org_id, err = tiny_live.resolve_orgid("600000", stats)
        self.assertEqual(org_id, "gssh0600000")
        self.assertEqual(err, "")
        self.assertEqual(stats.cninfo_requests, 1)
        self.assertEqual(stats.orgid_offline_fallback_hits, 0)
        self.assertEqual(stats.orgid_offline_fallback_misses, 0)
        self.assertNotIn("600000", stats.orgid_offline_fallback_sources)

    def test_all_three_slice2_unresolved_codes_recover(self) -> None:
        stats = tiny_live.LiveStats()
        with mock.patch.object(
            tiny_live.requests,
            "post",
            return_value=_FakeResp(payload=[]),
        ):
            for code, expected in fallback.SLICE2_S1_EXPECTED_ORGIDS.items():
                tiny_live._ORGID_CACHE.clear()
                org_id, err = tiny_live.resolve_orgid(code, stats)
                self.assertEqual(org_id, expected, msg=code)
                self.assertEqual(err, "")
        self.assertEqual(stats.orgid_offline_fallback_hits, 3)
        self.assertEqual(stats.cninfo_requests, 3)


class TestOrgidFallbackRetryPath(unittest.TestCase):
    def test_retry_mode_detection(self) -> None:
        self.assertTrue(
            runner.is_erad_slice2_orgid_fallback_retry_mode(
                runner.DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_UNIVERSE_CSV,
                None,
            )
        )
        self.assertTrue(
            runner.is_erad_slice2_orgid_fallback_retry_mode(
                None,
                runner.DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            )
        )
        self.assertFalse(
            runner.is_erad_slice2_orgid_fallback_retry_mode(
                runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV,
                runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT,
            )
        )

    def test_retry_output_root_blocks_closed_s1(self) -> None:
        ok, err = runner.validate_erad_slice2_orgid_fallback_retry_output_root(
            runner.DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT
        )
        self.assertFalse(ok)
        self.assertEqual(
            err, runner.ERAD_SLICE2_ORGID_FALLBACK_RETRY_CLOSED_ROOT_WRITE_FORBIDDEN
        )

    def test_retry_output_root_allows_isolated_root(self) -> None:
        ok, err = runner.validate_erad_slice2_orgid_fallback_retry_output_root(
            runner.DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT
        )
        self.assertTrue(ok, msg=err)

    def test_retry_universe_size_and_case_ids(self) -> None:
        cases = runner.load_erad_next_scale_slice2_universe(
            runner.DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_UNIVERSE_CSV
        )
        ok, err = runner.validate_erad_slice2_orgid_fallback_retry_universe_size(cases)
        self.assertTrue(ok, msg=err)
        self.assertEqual(
            {c.case_id for c in cases}, runner.ERAD_SLICE2_ORGID_FALLBACK_RETRY_CASE_IDS
        )

    def test_request_cap_is_twelve_for_retry(self) -> None:
        self.assertEqual(
            runner.erad_slice2_request_cap_for_mode(orgid_fallback_retry=True), 12
        )
        self.assertEqual(
            runner.erad_slice2_request_cap_for_mode(orgid_fallback_retry=False),
            runner.ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP,
        )

    def test_full_slice2_rejects_retry_root(self) -> None:
        ok, err = runner.validate_erad_next_scale_slice2_output_root(
            runner.DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT
        )
        self.assertFalse(ok)
        self.assertEqual(err, "orgid_fallback_retry_root_forbidden_for_full_slice2")


if __name__ == "__main__":
    unittest.main()
