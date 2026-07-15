#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNINFO D 类 AT/SD — D-FM-36 dual-track post-closure readiness offline 测试。

离线 only · 无 CNINFO · 无 live · 无 dry-run 重写 · 不 claim verified。

运行：
    .venv/bin/python lab/test_cninfo_d_class_at_sd_post_closure_readiness_offline.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
VALIDATION = BASE_DIR / "outputs" / "validation"

READINESS_LEDGER = (
    VALIDATION / "cninfo_d_class_at_sd_next_slice_post_closure_readiness_ledger.csv"
)
FREEZE_ATTESTATION = (
    VALIDATION / "cninfo_d_class_at_sd_next_slice_post_closure_freeze_attestation.csv"
)
CAVEAT_UNION = (
    VALIDATION / "cninfo_d_class_at_sd_next_slice_post_closure_caveat_union.csv"
)
READINESS_MATRIX = (
    VALIDATION / "cninfo_d_class_at_sd_dfm36_post_closure_readiness_matrix_20260715.csv"
)
READINESS_METRICS = (
    VALIDATION / "cninfo_d_class_at_sd_next_slice_post_closure_readiness_metrics.csv"
)
READINESS_DECISION = (
    VALIDATION / "cninfo_d_class_at_sd_next_slice_post_closure_readiness_decision.md"
)
READINESS_SUMMARY = (
    VALIDATION / "cninfo_d_class_at_sd_next_slice_post_closure_readiness_summary.md"
)
READINESS_EVIDENCE = (
    VALIDATION / "cninfo_d_class_at_sd_dfm36_post_closure_readiness_ledger_20260715.md"
)
NEXT_STEP = (
    VALIDATION
    / "cninfo_d_class_at_sd_next_slice_post_closure_next_step_recommendation.md"
)

AT_DRYRUN_REPORT = (
    VALIDATION
    / "cninfo_d_class_abnormal_trading_next_slice"
    / "reports"
    / "d_class_abnormal_trading_next_slice_dryrun_report.csv"
)
AT_DRYRUN_SUMMARY = (
    VALIDATION
    / "cninfo_d_class_abnormal_trading_next_slice"
    / "reports"
    / "d_class_abnormal_trading_next_slice_dryrun_summary.md"
)
SD_DRYRUN_REPORT = (
    VALIDATION
    / "cninfo_d_class_shareholder_data_next_slice"
    / "reports"
    / "d_class_shareholder_data_next_slice_dryrun_report.csv"
)
SD_DRYRUN_SUMMARY = (
    VALIDATION
    / "cninfo_d_class_shareholder_data_next_slice"
    / "reports"
    / "d_class_shareholder_data_next_slice_dryrun_summary.md"
)
AT_NEXT_LIVE = (
    VALIDATION
    / "cninfo_d_class_abnormal_trading_next_slice"
    / "reports"
    / "d_class_abnormal_trading_next_slice_live_report.csv"
)
SD_NEXT_LIVE = (
    VALIDATION
    / "cninfo_d_class_shareholder_data_next_slice"
    / "reports"
    / "d_class_shareholder_data_next_slice_live_report.csv"
)

LOCK_PATHS = {
    "lock_at_next": VALIDATION
    / "cninfo_d_class_abnormal_trading_next_slice_universe_lock_20260715.csv",
    "lock_sd_next": VALIDATION
    / "cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv",
    "lock_at_first": VALIDATION
    / "cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv",
    "lock_sd_first": VALIDATION
    / "cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv",
    "lock_fia_first": VALIDATION
    / "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv",
    "lock_fia_next": VALIDATION
    / "cninfo_d_class_fund_industry_allocation_next_slice_universe_lock_20260715.csv",
}

# D-FM-34/35 冻结值；D-FM-36 只读 attestation，不得漂移
EXPECTED_SHA256 = {
    "at_next_dryrun_report": (
        "51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497"
    ),
    "at_next_dryrun_summary": (
        "7fae1ccaacf31cbb254e51fc4b5a139554f40185eacd29ed692b1ce9320bb624"
    ),
    "sd_next_dryrun_report": (
        "2b74aac55299bc844e7df49725ad9ccf1f9c4dfbfc7db403f026412faf177362"
    ),
    "sd_next_dryrun_summary": (
        "86ffa6df3b59a5aa0ee8573a109947998f42aca879a7d7f0fddb2e8f1e8d38dc"
    ),
    "lock_at_next": (
        "4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6"
    ),
    "lock_sd_next": (
        "c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f"
    ),
    "lock_at_first": (
        "d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2"
    ),
    "lock_sd_first": (
        "06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5"
    ),
    "lock_fia_first": (
        "49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c"
    ),
    "lock_fia_next": (
        "c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515"
    ),
}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


class TestAtSdPostClosureReadinessDfm36(unittest.TestCase):
    """D-FM-36 AT+SD dual-track post-closure readiness：只读复核（无 CNINFO · 无 live）。"""

    def test_readiness_artifacts_present_and_gates(self) -> None:
        for path in (
            READINESS_LEDGER,
            FREEZE_ATTESTATION,
            CAVEAT_UNION,
            READINESS_MATRIX,
            READINESS_METRICS,
            READINESS_DECISION,
            READINESS_SUMMARY,
            READINESS_EVIDENCE,
            NEXT_STEP,
        ):
            self.assertTrue(path.is_file(), msg=str(path))

        with READINESS_METRICS.open(newline="", encoding="utf-8") as f:
            metrics = {r["metric_name"]: r["value"] for r in csv.DictReader(f)}
        self.assertEqual(metrics["dual_track_post_closure_readiness_gate"], "PASS_OFFLINE")
        self.assertEqual(metrics["CNINFO_during_dfm36_readiness"], "0")
        self.assertEqual(metrics["at_live_gate"], "NOT_APPROVED")
        self.assertEqual(metrics["sd_live_gate"], "NOT_APPROVED")
        self.assertEqual(metrics["at_execution_gate"], "NOT_APPLICABLE")
        self.assertEqual(metrics["sd_execution_gate"], "NOT_APPLICABLE")
        self.assertEqual(metrics["at_next_live_flipped"], "false")
        self.assertEqual(metrics["sd_next_live_flipped"], "false")
        self.assertEqual(metrics["controller_execution_allowed"], "false")
        self.assertEqual(metrics["commit_boundary_gate"], "READY_FOR_COMMIT_REVIEW")
        self.assertEqual(metrics["at_planned_ok"], "5/5")
        self.assertEqual(metrics["sd_planned_ok"], "5/5")
        self.assertEqual(metrics["at_shared_probe_prefer"], "1")
        self.assertEqual(metrics["sd_shared_probe_prefer"], "2")

        with READINESS_MATRIX.open(newline="", encoding="utf-8") as f:
            matrix = {r["track"]: r for r in csv.DictReader(f)}
        self.assertEqual(matrix["AT"]["live_flipped"], "false")
        self.assertEqual(matrix["SD"]["live_flipped"], "false")
        self.assertEqual(matrix["BOTH"]["cninfo_this_task"], "0")
        self.assertEqual(matrix["BOTH"]["s4_dryrun_closure_gate"], "PASS_OFFLINE")
        self.assertEqual(matrix["AT"]["freeze_attestation"], "MATCH")
        self.assertEqual(matrix["SD"]["freeze_attestation"], "MATCH")

        with CAVEAT_UNION.open(newline="", encoding="utf-8") as f:
            caveats = {c["caveat_id"]: c for c in csv.DictReader(f)}
        self.assertIn("CAV-ATSD-PC-07", caveats)
        self.assertEqual(caveats["CAV-ATSD-PC-07"]["caveat_type"], "at_sd_live_not_flipped")
        self.assertEqual(caveats["CAV-ATSD-PC-07"]["blocking_live"], "yes")
        self.assertEqual(caveats["CAV-ATSD-PC-09"]["caveat_type"], "dlc006r_closed")
        self.assertEqual(caveats["CAV-ATSD-PC-10"]["caveat_type"], "ess_paused")
        self.assertIn("bare PASS", caveats["CAV-ATSD-PC-11"]["forbidden_interpretation"])

        with READINESS_LEDGER.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows), 20)
        dual = [
            r
            for r in rows
            if r["item"] == "dual_track_post_closure" and r["track"] == "BOTH"
        ]
        self.assertEqual(len(dual), 1)
        self.assertEqual(dual[0]["gate_or_value"], "PASS_OFFLINE")
        live_flip = [
            r for r in rows if r["item"] == "live_flip" and r["track"] == "BOTH"
        ]
        self.assertEqual(live_flip[0]["status"], "blocked")
        self.assertEqual(live_flip[0]["blocking_live"], "yes")

    def test_freeze_attestation_match_and_live_absent(self) -> None:
        self.assertFalse(AT_NEXT_LIVE.is_file())
        self.assertFalse(SD_NEXT_LIVE.is_file())

        path_by_role = {
            "at_next_dryrun_report": AT_DRYRUN_REPORT,
            "at_next_dryrun_summary": AT_DRYRUN_SUMMARY,
            "sd_next_dryrun_report": SD_DRYRUN_REPORT,
            "sd_next_dryrun_summary": SD_DRYRUN_SUMMARY,
            **LOCK_PATHS,
        }
        for role, expected in EXPECTED_SHA256.items():
            path = path_by_role[role]
            self.assertTrue(path.is_file(), msg=str(path))
            self.assertEqual(_sha256_file(path), expected, msg=role)

        with FREEZE_ATTESTATION.open(newline="", encoding="utf-8") as f:
            att = {r["artifact_role"]: r for r in csv.DictReader(f)}
        for role, expected in EXPECTED_SHA256.items():
            self.assertEqual(att[role]["sha256"], expected, msg=role)
            self.assertEqual(att[role]["attestation_status"], "MATCH", msg=role)
            self.assertEqual(att[role]["freeze_policy"], "frozen_read_only", msg=role)
        self.assertEqual(att["at_next_live_report"]["attestation_status"], "ABSENT_OK")
        self.assertEqual(att["sd_next_live_report"]["attestation_status"], "ABSENT_OK")

    def test_evidence_language_and_red_lines(self) -> None:
        evidence = READINESS_EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("dual_track_post_closure_readiness_gate = PASS_OFFLINE", evidence)
        self.assertIn("cninfo_calls = 0", evidence)
        self.assertIn("at_next_live_flipped = false", evidence)
        self.assertIn("sd_next_live_flipped = false", evidence)
        self.assertIn("controller_execution_allowed = false", evidence)
        self.assertIn("NOT verified", evidence)
        self.assertIn("NOT production_ready", evidence)
        self.assertIn("不使用：** bare PASS", evidence)
        self.assertIn("ready_for_commit = true", evidence)
        self.assertIn("DLC006R", evidence)
        self.assertIn("ESS H3/H4", evidence)
        # 禁止暗示 live 已批
        self.assertNotIn("live_gate = APPROVED", evidence)
        self.assertNotIn("production_ready = true", evidence)

        decision = READINESS_DECISION.read_text(encoding="utf-8")
        self.assertIn("CLOSE_DUAL_TRACK_POST_CLOSURE_READINESS_NOW", decision)
        self.assertIn("controller_execution_allowed = false", decision)

        next_step = NEXT_STEP.read_text(encoding="utf-8")
        self.assertIn(
            "primary_recommendation = controller_commit_boundary_dfm36_at_sd_post_closure_readiness",
            next_step,
        )
        self.assertIn("blocked_until_explicit_approve", next_step)
        self.assertIn("paused_pending_devtools", next_step)


if __name__ == "__main__":
    unittest.main()
