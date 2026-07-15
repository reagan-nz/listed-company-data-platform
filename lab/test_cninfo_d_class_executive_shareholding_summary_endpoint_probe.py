#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 executive_shareholding_summary — D-FM-22 endpoint probe smoke。

覆盖：
  - dry-run 计划产物（CNINFO=0）
  - 硬顶 / H1→H2 序列常量
  - 受保护 live 根拒绝写入
  - 分类逻辑（无网络）
  - 本模块无静默 fallback 到 ES detail URL

用法：
    .venv/bin/python lab/test_cninfo_d_class_executive_shareholding_summary_endpoint_probe.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

MODULE_PATH = os.path.join(
    _LAB_DIR,
    "run_cninfo_d_class_executive_shareholding_summary_endpoint_probe.py",
)


def _load_mod():
    spec = importlib.util.spec_from_file_location("ess_endpoint_probe", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestEssEndpointProbeOffline(unittest.TestCase):
    """D-FM-22：ESS endpoint probe 离线结构校验。"""

    @classmethod
    def setUpClass(cls):
        cls.mod = _load_mod()

    def test_constants_hard_cap_and_urls(self):
        m = self.mod
        self.assertEqual(m.MAX_CNINFO, 2)
        self.assertEqual(m.HARD_CAP, 2)
        self.assertTrue(m.H1_URL.endswith("/data20/leader/summary"))
        self.assertTrue(m.H2_URL.endswith("/data20/leader/statistics"))
        self.assertNotIn("leader/detail", m.H1_URL)
        self.assertNotIn("leader/detail", m.H2_URL)
        self.assertEqual(m.DEFAULT_PARAMS["timeMark"], "oneMonth")
        self.assertEqual(m.DEFAULT_PARAMS["varyType"], "b")

    def test_dry_run_writes_plan_cninfo_zero(self):
        m = self.mod
        with tempfile.TemporaryDirectory() as tmp:
            rc = m.run_dry_run(tmp)
            self.assertEqual(rc, 0)
            plan_path = os.path.join(tmp, "reports", "ess_endpoint_probe_plan.json")
            self.assertTrue(os.path.isfile(plan_path))
            with open(plan_path, encoding="utf-8") as f:
                plan = json.load(f)
            self.assertEqual(plan["task_id"], "D-FM-22")
            self.assertEqual(plan["cninfo_budget"], 2)
            self.assertEqual(plan["probe_sequence"][0]["hyp_id"], "H1")
            self.assertEqual(plan["probe_sequence"][1]["hyp_id"], "H2")
            self.assertFalse(plan["registry_write"])
            self.assertFalse(plan["verified_claim"])

    def test_refuse_protected_live_root(self):
        m = self.mod
        protected = os.path.join(
            _BASE_DIR,
            "outputs",
            "validation",
            "cninfo_d_class_executive_shareholding_first_slice",
        )
        with self.assertRaises(SystemExit) as ctx:
            m._ensure_output_dir(protected)
        self.assertIn("refuse_write_protected_live_root", str(ctx.exception))

    def test_classify_confirmed_with_records(self):
        m = self.mod
        payload = {
            "data": {
                "records": [
                    {"SECCODE": "000001", "SECNAME": "示例", "F001N": 1.2},
                ]
            }
        }
        cls, n, path, keys = m._classify_response(200, payload, "")
        self.assertEqual(cls, "confirmed_with_records")
        self.assertEqual(n, 1)
        self.assertEqual(path, "data.records")
        self.assertIn("SECCODE", keys)

    def test_classify_confirmed_empty(self):
        m = self.mod
        payload = {"data": {"records": []}}
        cls, n, path, _keys = m._classify_response(200, payload, "")
        self.assertEqual(cls, "confirmed_empty_valid")
        self.assertEqual(n, 0)
        self.assertEqual(path, "data.records")

    def test_classify_404_rejected(self):
        m = self.mod
        cls, n, path, _keys = m._classify_response(404, None, "http_404")
        self.assertEqual(cls, "rejected")
        self.assertEqual(n, 0)
        self.assertEqual(path, "")

    def test_classify_shape_review(self):
        m = self.mod
        payload = {"code": "0", "msg": "ok", "result": []}
        cls, n, path, keys = m._classify_response(200, payload, "")
        self.assertEqual(cls, "reachable_shape_review")
        self.assertEqual(n, 0)
        self.assertEqual(path, "")
        self.assertIn("code", keys)

    def test_live_requires_approve_flag(self):
        m = self.mod
        rc = m.main(["--live"])
        self.assertEqual(rc, 2)

    def test_mock_live_h1_success_stops_without_h2(self):
        m = self.mod

        class _Resp:
            status_code = 200
            text = '{"data":{"records":[{"SECCODE":"1"}]}}'

            def json(self):
                return {"data": {"records": [{"SECCODE": "1"}]}}

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(m.time, "sleep", return_value=None):
                sess = mock.Mock()
                sess.post.return_value = _Resp()
                rc = m.execute_live_probe(tmp, session=sess)
            self.assertEqual(rc, 0)
            self.assertEqual(sess.post.call_count, 1)
            called_url = sess.post.call_args[0][0]
            self.assertEqual(called_url, m.H1_URL)
            result_path = os.path.join(tmp, "reports", "ess_endpoint_probe_live_result.json")
            with open(result_path, encoding="utf-8") as f:
                result = json.load(f)
            self.assertEqual(result["cninfo_calls"], 1)
            self.assertEqual(result["final_hyp"], "H1")
            self.assertEqual(result["final_classification"], "confirmed_with_records")
            self.assertFalse(result["registry_write"])

    def test_mock_live_h1_fail_then_h2(self):
        m = self.mod

        class _Resp404:
            status_code = 404
            text = "not found"

            def json(self):
                raise ValueError("no json")

        class _Resp200:
            status_code = 200
            text = '{"data":{"records":[]}}'

            def json(self):
                return {"data": {"records": []}}

        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(m.time, "sleep", return_value=None):
                sess = mock.Mock()
                sess.post.side_effect = [_Resp404(), _Resp200()]
                rc = m.execute_live_probe(tmp, session=sess)
            self.assertEqual(rc, 0)
            self.assertEqual(sess.post.call_count, 2)
            result_path = os.path.join(tmp, "reports", "ess_endpoint_probe_live_result.json")
            with open(result_path, encoding="utf-8") as f:
                result = json.load(f)
            self.assertEqual(result["cninfo_calls"], 2)
            self.assertEqual(result["final_hyp"], "H2")
            self.assertEqual(result["final_classification"], "confirmed_empty_valid")

    def test_module_source_excludes_detail_live_mutation(self):
        with open(MODULE_PATH, encoding="utf-8") as f:
            src = f.read()
        self.assertIn("leader/summary", src)
        self.assertIn("leader/statistics", src)
        self.assertIn("refuse_write_protected_live_root", src)
        self.assertIn("cninfo_d_class_executive_shareholding_first_slice", src)
        # 禁止把 detail 当作本探针目标 URL 常量
        self.assertNotIn(
            'H1_URL = "https://www.cninfo.com.cn/data20/leader/detail"',
            src,
        )


if __name__ == "__main__":
    unittest.main()
