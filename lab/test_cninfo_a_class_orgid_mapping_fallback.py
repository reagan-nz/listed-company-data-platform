"""
A-class 离线 orgId 映射回退单元测试（纯离线 · CNINFO = 0）。

断言 Run 14 三案 AD2E578/590/598 对应证券代码可离线解析到已恢复 orgId。

运行：
    python lab/test_cninfo_a_class_orgid_mapping_fallback.py
"""

from __future__ import annotations

import os
import sys
import unittest

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import cninfo_a_class_orgid_mapping_fallback as fallback  # noqa: E402


class TestCninfoAClassOrgidMappingFallback(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fallback.reset_default_index()
        cls.index = fallback.build_offline_orgid_index()

    def test_cninfo_calls_remain_zero(self) -> None:
        self.assertEqual(self.index.cninfo_calls, 0)
        # 查找路径不得引入 CNINFO 调用计数
        _ = fallback.lookup_orgid("688605", index=self.index)
        self.assertEqual(self.index.cninfo_calls, 0)

    def test_slice2_s1_three_codes_resolve(self) -> None:
        """AD2E578/590/598：topSearch null 时可离线恢复 orgId。"""
        cases = [
            ("688605", "9900059045", "先锋精科"),  # AD2E578
            ("688688", "9900046315", "蚂蚁集团"),  # AD2E590
            ("688758", "9900057459", "赛分科技"),  # AD2E598
        ]
        for code, expected_org, expected_name in cases:
            with self.subTest(code=code):
                result = self.index.lookup(code)
                self.assertTrue(result.found, msg=result.error)
                self.assertEqual(result.org_id, expected_org)
                self.assertEqual(
                    fallback.SLICE2_S1_EXPECTED_ORGIDS[code], expected_org
                )
                if result.company_name:
                    self.assertEqual(result.company_name, expected_name)
                self.assertTrue(result.source)

    def test_verify_helper_matches_expected(self) -> None:
        results = fallback.verify_slice2_s1_recovered_orgids(index=self.index)
        self.assertEqual(len(results), 3)
        for result in results:
            expected = fallback.SLICE2_S1_EXPECTED_ORGIDS[result.company_code]
            self.assertTrue(result.found, msg=result.error)
            self.assertEqual(result.org_id, expected)

    def test_resolve_orgid_returns_string(self) -> None:
        org_id = fallback.resolve_orgid("688605", index=self.index)
        self.assertEqual(org_id, "9900059045")

    def test_missing_code_is_explicit_miss(self) -> None:
        """缺失码必须显式未命中，禁止静默伪造。"""
        result = self.index.lookup("000000")
        self.assertFalse(result.found)
        self.assertEqual(result.org_id, "")
        self.assertTrue(result.error.startswith("offline_orgid_not_found:"))

    def test_missing_code_resolve_raises(self) -> None:
        with self.assertRaises(fallback.OrgIdMappingMissError) as ctx:
            fallback.resolve_orgid("000000", index=self.index)
        self.assertIn("000000", str(ctx.exception))

    def test_empty_code_is_explicit_error(self) -> None:
        result = self.index.lookup("")
        self.assertFalse(result.found)
        self.assertEqual(result.error, "empty_company_code")

    def test_normalize_code_zfill(self) -> None:
        self.assertEqual(fallback.normalize_code("688605"), "688605")
        self.assertEqual(fallback.normalize_code("8605"), "008605")

    def test_recovery_layer_alone_covers_three(self) -> None:
        """仅 recovery CSV 即可覆盖三案（不依赖 YAML/identity）。"""
        idx = fallback.build_offline_orgid_index(
            include_recovery=True,
            include_identity_mapping=False,
            include_full_market_yaml=False,
        )
        self.assertEqual(idx.cninfo_calls, 0)
        for code, expected in fallback.SLICE2_S1_EXPECTED_ORGIDS.items():
            result = idx.lookup(code)
            self.assertTrue(result.found, msg=result.error)
            self.assertEqual(result.org_id, expected)
            self.assertIn("recovery_csv", result.source)

    def test_index_loads_at_least_recovery_sources(self) -> None:
        self.assertGreaterEqual(len(self.index.source_paths), 1)
        self.assertGreaterEqual(len(self.index.entries), 3)


if __name__ == "__main__":
    unittest.main()
