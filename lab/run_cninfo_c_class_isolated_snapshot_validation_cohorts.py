#!/usr/bin/env python3
"""
CNINFO C-class — 隔离 snapshot 校验 cohort + lineage 自动化 runner（离线）。

Usage:
    python3 lab/run_cninfo_c_class_isolated_snapshot_validation_cohorts.py
    python3 lab/run_cninfo_c_class_isolated_snapshot_validation_cohorts.py \\
      --skip-standard-isolated
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402
from cninfo_c_class_isolated_snapshot_validation_cohorts import (  # noqa: E402
    COHORT_CAVEAT10_NEG,
    COHORT_SLICE1_190,
    COHORT_STANDARD_ISOLATED,
    run_all_validation_cohorts,
)

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_isolated_snapshot_validation_cohorts"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/cninfo_c_class_fm02_isolated_validation_cohorts_20260715.md"
)


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def write_reports(payload: Dict[str, Any]) -> Dict[str, str]:
    """写出 JSON / MD / task 报告。"""
    report_root = _abs(REPORT_ROOT_REL)
    os.makedirs(report_root, exist_ok=True)

    # 拷贝矩阵到报告根（若存在）
    slice1 = payload.get("slice1_190") or {}
    matrix_src = slice1.get("matrix_path") or ""
    matrix_dst_rel = f"{REPORT_ROOT_REL}/cohort_lineage_matrix.csv"
    if matrix_src:
        src_abs = (
            matrix_src
            if os.path.isabs(matrix_src)
            else os.path.join(BASE_DIR, matrix_src)
        )
        if os.path.isfile(src_abs):
            dst_abs = _abs(matrix_dst_rel)
            with open(src_abs, "rb") as fh_in, open(dst_abs, "wb") as fh_out:
                fh_out.write(fh_in.read())

    json_path = _abs(REPORT_JSON_REL)
    # 精简 JSON：去掉巨大 matrix_rows
    json_payload = {
        "generated_at": payload["generated_at"],
        "task_id": payload["task_id"],
        "gate": payload["gate"],
        "cohort_gates": payload["cohort_gates"],
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "slice1_190": {
            k: v
            for k, v in slice1.items()
            if k not in ("matrix_rows",)
        },
        "standard_isolated": payload.get("standard_isolated"),
    }
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(json_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    std = payload.get("standard_isolated") or {}
    checks = slice1.get("checks") or {}
    check_lines = [
        f"| `{k}` | **{'PASS' if v else 'FAIL'}** |" for k, v in checks.items()
    ]
    fp = slice1.get("fingerprint") or {}
    std_fp = (std.get("fingerprint") or {}) if std else {}

    md_lines = [
        "# CNINFO C 类 — 隔离 Snapshot 校验 Cohort + Lineage",
        "",
        f"_生成时间：{payload['generated_at']} · executor: c-class-executor · "
        "offline · CNINFO=0_",
        "",
        "| 字段 | 值 |",
        "|------|-----|",
        "| task_id | **C-FM-02** |",
        f"| gate | `{payload['gate']}` |",
        f"| cohort `{COHORT_SLICE1_190}` | `{payload['cohort_gates'].get(COHORT_SLICE1_190)}` |",
        f"| cohort `{COHORT_CAVEAT10_NEG}` | `{payload['cohort_gates'].get(COHORT_CAVEAT10_NEG)}` |",
        f"| cohort `{COHORT_STANDARD_ISOLATED}` | "
        f"`{payload['cohort_gates'].get(COHORT_STANDARD_ISOLATED, 'skipped')}` |",
        "| cninfo_calls | **0** |",
        "| execute_production_snapshot_rebuild | **false** |",
        "",
        "## Slice1 190 included cohort",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| output_root | `{slice1.get('output_root')}` |",
        f"| included_count | **{slice1.get('included_count')}** |",
        f"| excluded_control_count | **{slice1.get('excluded_control_count')}** |",
        f"| fingerprint_reproducible | **{slice1.get('reproducible')}** |",
        f"| fingerprint_sha256 | `{fp.get('fingerprint_sha256', '')}` |",
        f"| builder_gate | `{slice1.get('builder_gate')}` |",
        f"| lineage_matrix | `{slice1.get('matrix_path')}` |",
        "",
        "## Checks",
        "",
        "| check | result |",
        "|-------|--------|",
        *check_lines,
        "",
        "## Standard isolated fingerprint cohort (C-FM-01 artifact)",
        "",
    ]
    if std:
        std_checks = std.get("checks") or {}
        std_check_lines = [
            f"| `{k}` | **{'PASS' if v else 'FAIL'}** |"
            for k, v in std_checks.items()
        ]
        md_lines.extend(
            [
                f"- output_root: `{std.get('output_root')}`",
                f"- status_rows: **{std.get('status_rows')}**",
                f"- fingerprint_sha256: `{std_fp.get('fingerprint_sha256', '')}`",
                f"- gate: `{std.get('gate')}`",
                "",
                "| check | result |",
                "|-------|--------|",
                *std_check_lines,
                "",
            ]
        )
    else:
        md_lines.append("_skipped_\n")

    md_lines.extend(
        [
            "## Gate",
            "",
            "```",
            f"c_fm_02_isolated_snapshot_validation_cohorts_gate = {payload['gate']}",
            "execute_production_snapshot_rebuild = false",
            "cninfo_calls = 0",
            "```",
            "",
            "**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute",
            "",
            "## Artifacts",
            "",
            f"- [{REPORT_JSON_REL}]({os.path.basename(REPORT_JSON_REL)})",
            f"- [{matrix_dst_rel}]({os.path.basename(matrix_dst_rel)})",
            f"- [{slice1.get('output_root')}/]({slice1.get('output_root')}/)",
            "",
        ]
    )
    md_path = _abs(REPORT_MD_REL)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines) + "\n")

    task_lines = [
        "# C-FM-02 — 隔离 Snapshot 校验 Cohort + Dry-run Lineage",
        "",
        f"_生成时间：{payload['generated_at']} · executor: c-class-executor · "
        "offline · CNINFO=0_",
        "",
        "| 字段 | 值 |",
        "|------|-----|",
        "| task_id | **C-FM-02** |",
        "| track | C |",
        f"| result | **{'DONE' if payload['gate'] == 'PASS_OFFLINE' else 'FAIL'}** |",
        "| CNINFO live | **0** |",
        "| prod snapshot EXECUTE | **not invoked** |",
        "| commit / push | **无**（待 controller） |",
        f"| ready_for_commit | **{'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}** |",
        "",
        "## Task",
        "",
        "在 C-FM-01 隔离 dry-run / 指纹能力之上，新增 **隔离 snapshot 校验 cohort** "
        "与 **dry-run lineage 自动化**：universe ↔ status ↔ harvest ledger ↔ "
        "exclusion reconcile；含 caveat10 负对照与标准隔离根只读指纹核验。",
        "",
        "## Capability gain",
        "",
        "1. `cninfo_c_class_isolated_snapshot_validation_cohorts`：多 cohort 规格 + lineage 矩阵",
        "2. slice1_190 included 隔离 dry-run（validation/_mock_*）+ 双次指纹可复现",
        "3. caveat10 负对照：排除码不得泄漏进 included dry-run status",
        "4. harvest ledger / exclusion pool_decision 交叉 lineage 检查",
        "5. C-FM-01 标准隔离根只读指纹复算（不重跑 863）",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_isolated_snapshot_validation_cohorts.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_isolated_snapshot_validation_cohorts.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_isolated_snapshot_validation_cohorts.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK4 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        f"| `{slice1.get('output_root')}/` | 隔离 cohort 产物 |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* dry-run / lineage | 生产 snapshot EXECUTE |",
        "| 只读 harvest ledger / exclusion | CNINFO live |",
        "| offline QA / fingerprint | commit/push（本包未执行） |",
        "| | verified / production_ready 声称 |",
        "",
        "## Wall / gate",
        "",
        "```",
        f"c_fm_02_isolated_snapshot_validation_cohorts_gate = {payload['gate']}",
        "execute_production_snapshot_rebuild = false",
        "cninfo_calls = 0",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包",
        "- 生产 snapshot EXECUTE 仍 human-gated",
        "",
    ]
    task_path = _abs(TASK_REPORT_REL)
    with open(task_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(task_lines) + "\n")

    # 报告根 summary
    root_summary = os.path.join(report_root, "README.md")
    with open(root_summary, "w", encoding="utf-8") as fh:
        fh.write(
            "\n".join(
                [
                    "# Isolated Snapshot Validation Cohorts",
                    "",
                    f"gate: `{payload['gate']}`",
                    f"see: [../{os.path.basename(REPORT_MD_REL)}]"
                    f"(../{os.path.basename(REPORT_MD_REL)})",
                    "",
                ]
            )
        )

    return {
        "report_md": REPORT_MD_REL,
        "report_json": REPORT_JSON_REL,
        "task_report": TASK_REPORT_REL,
        "matrix": matrix_dst_rel,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="C-FM-02 isolated snapshot validation cohorts (offline)"
    )
    parser.add_argument(
        "--skip-standard-isolated",
        action="store_true",
        help="跳过 C-FM-01 标准隔离根只读指纹核验",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="禁止：生产 EXECUTE（硬拒绝）",
    )
    args = parser.parse_args()
    if args.execute:
        raise RuntimeError(
            "C_FM02_EXECUTE_FORBIDDEN: 本 runner 仅离线 cohort/lineage，禁止 --execute"
        )

    payload = run_all_validation_cohorts(
        include_standard_isolated=not args.skip_standard_isolated
    )
    paths = write_reports(payload)

    print(f"gate: {payload['gate']}")
    print(f"cohort_gates: {payload['cohort_gates']}")
    slice1 = payload["slice1_190"]
    print(f"slice1_190_output_root: {slice1.get('output_root')}")
    print(f"included_count: {slice1.get('included_count')}")
    print(f"excluded_control_count: {slice1.get('excluded_control_count')}")
    print(f"reproducible: {slice1.get('reproducible')}")
    fp = slice1.get("fingerprint") or {}
    print(f"fingerprint_sha256: {fp.get('fingerprint_sha256', '')}")
    print(f"report_md: {paths['report_md']}")
    print(f"task_report: {paths['task_report']}")
    print("cninfo_calls=0")
    print("execute_production_snapshot_rebuild: false")
    return 0 if payload["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
