#!/usr/bin/env python3
"""
CNINFO C-class — snapshot dry-run 输出根隔离与可复现指纹测试（无 CNINFO）。

覆盖：
  - 生产 snapshot 根默认拒绝
  - 默认隔离 mock 根可写
  - --allow-production-dryrun-scaffold 显式放行
  - 连续两次隔离 dry-run 指纹一致

运行：
    python3 lab/test_cninfo_c_class_snapshot_dryrun_output_root_isolation.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from build_cninfo_c_class_snapshot_batch import (  # noqa: E402
    BASE_DIR,
    DEFAULT_OUTPUT_DIR_REL,
    PHASE2_SNAPSHOT_OUTPUT_ROOT_REL,
    PHASE3_SUCCESS_SNAPSHOT_OUTPUT_ROOT_REL,
    PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN,
    reset_snapshot_batch_paths,
    run_dry_run,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL,
    assert_safe_c_class_snapshot_dryrun_write_root,
    fingerprint_isolated_snapshot_dryrun,
    is_protected_c_class_production_snapshot_root,
    resolve_standard_snapshot_dryrun_output_root,
    safe_cleanup_temp_output_root,
)

RUNNER = os.path.join(_LAB_DIR, "build_cninfo_c_class_snapshot_batch.py")
SUMMARY_PATH = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_snapshot_dryrun_output_root_isolation_test_summary_20260715.md",
)
UNIVERSE_YAML = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml"
)
HOLD_YAML = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml"
)


def _run_runner(argv: list) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, RUNNER] + argv,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        check=False,
    )


class TestSnapshotDryrunOutputRootIsolation(unittest.TestCase):
    def tearDown(self) -> None:
        reset_snapshot_batch_paths()

    def test_case1_production_full_root_refused(self) -> None:
        target = os.path.join(BASE_DIR, DEFAULT_OUTPUT_DIR_REL)
        self.assertTrue(is_protected_c_class_production_snapshot_root(target))
        with self.assertRaisesRegex(
            RuntimeError, PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN
        ):
            assert_safe_c_class_snapshot_dryrun_write_root(target)

    def test_case2_phase3_and_phase2_roots_refused(self) -> None:
        for rel in (
            PHASE3_SUCCESS_SNAPSHOT_OUTPUT_ROOT_REL,
            PHASE2_SNAPSHOT_OUTPUT_ROOT_REL,
        ):
            target = os.path.join(BASE_DIR, rel)
            with self.assertRaisesRegex(
                RuntimeError, PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN
            ):
                resolve_standard_snapshot_dryrun_output_root(target)

    def test_case3_default_resolves_to_isolated_mock(self) -> None:
        resolved = resolve_standard_snapshot_dryrun_output_root(None)
        self.assertTrue(
            resolved.replace("\\", "/").endswith(
                DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL
            )
        )

    def test_case4_cli_refuse_production_without_allow(self) -> None:
        proc = _run_runner(
            [
                "--dry-run",
                "--output-dir",
                DEFAULT_OUTPUT_DIR_REL,
            ]
        )
        self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
        self.assertIn(PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN, proc.stderr)

    def test_case5_cli_allow_production_scaffold(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="_mock_iso_dry_",
            dir=os.path.join(BASE_DIR, "outputs/validation"),
        ) as tmp:
            # 用隔离根验证 allow 路径可达；生产根 allow 仅测守卫函数，避免污染
            out_rel = os.path.relpath(tmp, BASE_DIR).replace("\\", "/")
            proc = _run_runner(
                [
                    "--dry-run",
                    "--output-root",
                    out_rel,
                    "--sample-file",
                    "lab/eval_companies_c_class_harvest_863_non_bse.yaml",
                ]
            )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("snapshot_dryrun_output_root_isolation: enforced", proc.stdout)
        self.assertIn("dryrun_fingerprint_sha256:", proc.stdout)

        allowed = assert_safe_c_class_snapshot_dryrun_write_root(
            os.path.join(BASE_DIR, DEFAULT_OUTPUT_DIR_REL),
            allow_production_scaffold=True,
        )
        self.assertTrue(allowed)

    def test_case6_isolated_dryrun_fingerprint_reproducible(self) -> None:
        parent = os.path.join(
            BASE_DIR, "outputs/validation/_mock_snapshot_dryrun_repro_test"
        )
        os.makedirs(parent, exist_ok=True)
        tmp = tempfile.mkdtemp(prefix="repro_", dir=parent)
        try:
            result1 = run_dry_run(
                universe_path=UNIVERSE_YAML,
                hold_path=HOLD_YAML,
                out_dir=tmp,
                report_path=os.path.join(tmp, "dryrun_report.csv"),
                summary_path=os.path.join(tmp, "dryrun_summary.md"),
            )
            fp1 = result1["dryrun_fingerprint"]["fingerprint_sha256"]
            content1 = result1["dryrun_fingerprint"]["content_sha256"]

            result2 = run_dry_run(
                universe_path=UNIVERSE_YAML,
                hold_path=HOLD_YAML,
                out_dir=tmp,
                report_path=os.path.join(tmp, "dryrun_report.csv"),
                summary_path=os.path.join(tmp, "dryrun_summary.md"),
            )
            fp2 = result2["dryrun_fingerprint"]["fingerprint_sha256"]
            content2 = result2["dryrun_fingerprint"]["content_sha256"]

            self.assertEqual(content1, content2)
            self.assertEqual(fp1, fp2)
            self.assertEqual(result1["gate"], result2["gate"])
            # 指纹函数独立复算
            recomputed = fingerprint_isolated_snapshot_dryrun(
                tmp,
                gate=result2["gate"],
                company_count=result2["validation"]["company_count"],
            )
            self.assertEqual(recomputed["content_sha256"], content2)
        finally:
            safe_cleanup_temp_output_root(tmp)
            if os.path.isdir(parent) and not os.listdir(parent):
                os.rmdir(parent)

    def test_case7_cninfo_not_called(self) -> None:
        with mock.patch("requests.get") as get_mock, mock.patch(
            "requests.post"
        ) as post_mock:
            with tempfile.TemporaryDirectory() as tmp:
                run_dry_run(
                    universe_path=UNIVERSE_YAML,
                    hold_path=HOLD_YAML,
                    out_dir=tmp,
                    report_path=os.path.join(tmp, "dryrun_report.csv"),
                    summary_path=os.path.join(tmp, "dryrun_summary.md"),
                )
        get_mock.assert_not_called()
        post_mock.assert_not_called()


def _write_summary(result: unittest.TestResult) -> None:
    lines = [
        "# CNINFO C 类 — Snapshot Dry-run 输出根隔离测试摘要",
        "",
        f"_生成时间：2026-07-15 · 离线 · tests={result.testsRun} · "
        f"failures={len(result.failures)} · errors={len(result.errors)}_",
        "",
        "覆盖：生产根拒绝 · 默认隔离 mock · allow scaffold · 指纹可复现 · CNINFO=0。",
        "",
        f"结果：**{'PASS' if result.wasSuccessful() else 'FAIL'}**",
        "",
        "gate: `PASS_OFFLINE`",
        "execute_production_snapshot_rebuild: false",
        "cninfo_calls: 0",
        "",
    ]
    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    _write_summary(result)
    raise SystemExit(0 if result.wasSuccessful() else 1)
