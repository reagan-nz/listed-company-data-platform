#!/usr/bin/env python3
"""
CNINFO C-class — 非 seal Cross-FM 扩展 post-commit 漂移复核 runner（离线 · C-FM-14）。

Usage:
    python3 lab/run_cninfo_c_class_nonseal_extension_post_commit_drift_recheck.py
    python3 lab/run_cninfo_c_class_nonseal_extension_post_commit_drift_recheck.py \\
      --output-root outputs/validation/_mock_c_fm14_nonseal_extension_post_commit_drift_recheck
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
from cninfo_c_class_nonseal_extension_post_commit_drift_recheck import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    DriftRecheckPaths,
    TASK_ID,
    run_nonseal_extension_post_commit_drift_recheck,
)

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_nonseal_extension_post_commit_drift_recheck"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_post_commit_drift_recheck_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_post_commit_drift_recheck_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/"
    "cninfo_c_class_fm14_nonseal_extension_post_commit_drift_recheck_20260715.md"
)


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def write_reports(payload: Dict[str, Any]) -> Dict[str, str]:
    os.makedirs(_abs(REPORT_ROOT_REL), exist_ok=True)
    os.makedirs(os.path.dirname(_abs(REPORT_MD_REL)), exist_ok=True)

    matrix_src = _abs(payload["matrix_path"])
    matrix_dst_rel = f"{REPORT_ROOT_REL}/drift_matrix.csv"
    matrix_dst = _abs(matrix_dst_rel)
    with open(matrix_src, encoding="utf-8") as src, open(
        matrix_dst, "w", encoding="utf-8"
    ) as dst:
        dst.write(src.read())

    json_payload = {
        "generated_at": payload["generated_at"],
        "task_id": payload["task_id"],
        "gate": payload["gate"],
        "layer_gates": payload["layer_gates"],
        "cninfo_calls": payload["cninfo_calls"],
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "ready_for_execute": False,
        "hold_recommendation": payload["hold_recommendation"],
        "decision_status": payload["decision_status"],
        "idle_not_required_while_awaiting": True,
        "fail_count": payload["fail_count"],
        "matrix_rows": payload["matrix_rows"],
        "output_root": payload["output_root"],
        "matrix_path": payload["matrix_path"],
        "fingerprint_path": payload["fingerprint_path"],
        "fingerprint": payload["fingerprint"],
        "battery_path": payload["battery_path"],
        "seal_packet_path": payload["seal_packet_path"],
        "frozen_extension_fp_sha256": payload["frozen_extension_fp_sha256"],
        "recomputed_extension_fp_sha256": payload[
            "recomputed_extension_fp_sha256"
        ],
        "drift_detected": payload["drift_detected"],
        "inputs": payload["inputs"],
        "mock_root_is_isolated": payload["mock_root_is_isolated"],
        "seal_chain_extended": False,
    }
    with open(_abs(REPORT_JSON_REL), "w", encoding="utf-8") as fh:
        json.dump(json_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    layer_lines = [
        f"| layer `{k}` | `{v}` |" for k, v in sorted(payload["layer_gates"].items())
    ]
    md_lines = [
        "# C-FM-14 Non-seal Extension Post-Commit Drift Recheck",
        "",
        f"_生成时间：{payload['generated_at']} · offline · CNINFO=0_",
        "",
        "| 字段 | 值 |",
        "|------|-----|",
        f"| task_id | **{payload['task_id']}** |",
        f"| gate | `{payload['gate']}` |",
        *layer_lines,
        f"| fail_count | **{payload['fail_count']}** / {payload['matrix_rows']} |",
        f"| mock output | `{payload['output_root']}` |",
        f"| frozen extension fp | `{payload['frozen_extension_fp_sha256']}` |",
        f"| recomputed extension fp | `{payload['recomputed_extension_fp_sha256']}` |",
        f"| drift_detected | **{payload['drift_detected']}** |",
        f"| drift fingerprint | `{payload['fingerprint'].get('fingerprint_sha256', '')}` |",
        "",
        "## Capability",
        "",
        "1. FM-01..05 + FM-12 + FM-13 gate battery（跳过 seal FM06–11）",
        "2. C-FM-13 MOCK15 冻结产物存在性",
        "3. 扩展矩阵指纹零漂移（冻结常量 · gate JSON · 矩阵文件 · 重算）",
        "4. 冻结 mock 写隔离（MOCK3–15 拒绝；MOCK16 / ephemeral 放行）",
        "5. harvest/exclusion dual-layer 一致性（FM-03）",
        "6. EXECUTE hold seal（KEEP_EXECUTE_FALSE · AWAITING · idle_not_required）",
        "7. protected CSV MOCK16 注册一致性",
        "",
        "## Inputs (read-only)",
        "",
        "| 输入 | 路径 |",
        "|------|------|",
    ]
    for k, v in payload["inputs"].items():
        md_lines.append(f"| `{k}` | `{v}` |")
    md_lines.extend(
        [
            "",
            "## Wall",
            "",
            "```",
            f"c_fm_14_nonseal_extension_post_commit_drift_recheck_gate = {payload['gate']}",
            "execute_production_snapshot_rebuild = false",
            "approved_for_snapshot_rebuild = false",
            "cninfo_calls = 0",
            "ready_for_execute = false",
            "hold_recommendation = KEEP_EXECUTE_FALSE",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "idle_not_required_while_awaiting = true",
            "seal_chain_extended = false",
            f"drift_detected = {str(payload['drift_detected']).lower()}",
            f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
            "```",
            "",
            "## Artifacts",
            "",
            f"- [{payload['matrix_path']}]({os.path.relpath(_abs(payload['matrix_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{matrix_dst_rel}]({os.path.relpath(matrix_dst, os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{REPORT_JSON_REL}]({os.path.basename(REPORT_JSON_REL)})",
            "",
        ]
    )
    with open(_abs(REPORT_MD_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    task_lines = [
        "# C-FM-14 — Non-seal Extension Post-Commit Drift Recheck",
        "",
        f"_生成时间：{payload['generated_at']} · executor: c-class-executor · offline · CNINFO=0_",
        "",
        "| 字段 | 值 |",
        "|------|-----|",
        f"| task_id | **{TASK_ID}** |",
        "| track | C |",
        f"| result | **{'DONE' if payload['gate'] == 'PASS_OFFLINE' else 'FAIL'}** |",
        "| CNINFO live | **0** |",
        "| prod snapshot EXECUTE | **not invoked** |",
        "| commit / push | **无**（待 controller） |",
        f"| ready_for_commit | **{'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}** |",
        "",
        "## Task",
        "",
        "在 C-FM-13 已 commit 且 EXECUTE 仍 human-held 之上，补齐 **非 seal-chain** 能力："
        "**Cross-FM mock cohort 扩展 post-commit 漂移复核**、"
        "**MOCK15 冻结产物零漂移**、**MOCK3–15 写隔离**；"
        "产物写入隔离 MOCK16（不覆盖 MOCK3–15；不新增 seal 层）。",
        "",
        "## Capability gain",
        "",
        "1. FM-01..05 + FM-12 + FM-13 gate battery（显式跳过 seal FM06–11）",
        "2. MOCK15 冻结产物存在性（matrix / fingerprint / registry / battery / packet）",
        "3. 扩展指纹零漂移：常量 · gate JSON · 冻结矩阵 · builder 重算对齐",
        "4. 冻结写隔离扩展至 MOCK15；本任务 MOCK16 放行",
        "5. harvest/exclusion FM-03 一致性层",
        "6. EXECUTE hold seal（不得因 AWAITING 而 IDLE）",
        "7. protected CSV：MOCK16 注册",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_nonseal_extension_post_commit_drift_recheck.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_nonseal_extension_post_commit_drift_recheck.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_nonseal_extension_post_commit_drift_recheck.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK16 |",
        f"| `{payload['output_root']}/` | 隔离 drift 产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* drift 矩阵 / 指纹 / battery / seal packet | 生产 snapshot EXECUTE |",
        "| 只读 FM01–05 / FM12 / FM13 gate JSON / MOCK15 产物 / harvest / protected CSV | CNINFO live |",
        "| offline QA · 扩展指纹重算（不覆盖 MOCK3–15） | 覆盖 MOCK3–15 |",
        "| | 覆盖权威 dual-layer 索引 |",
        "| | commit/push（本包未执行） |",
        "| | verified / production_ready 声称 |",
        "| | 翻转 approved_for_snapshot_rebuild |",
        "| | 新增 seal-chain MOCK 层 |",
        "| | 仅因 AWAITING 而 IDLE |",
        "",
        "## Wall / gate",
        "",
        "```",
        f"c_fm_14_nonseal_extension_post_commit_drift_recheck_gate = {payload['gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        "ready_for_execute = false",
        "hold_recommendation = KEEP_EXECUTE_FALSE",
        "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting = true",
        "seal_chain_extended = false",
        f"drift_detected = {str(payload['drift_detected']).lower()}",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包（non-seal post-commit drift recheck only）",
        "- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）",
        "- Human 仍可用 C-FM-10 checklist 做 EXECUTE 决策（本包不翻转 approved）",
        "",
    ]
    with open(_abs(TASK_REPORT_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(task_lines))

    readme = _abs(f"{payload['output_root']}/README.md")
    os.makedirs(os.path.dirname(readme), exist_ok=True)
    with open(readme, "w", encoding="utf-8") as fh:
        fh.write(
            "\n".join(
                [
                    "# C-FM-14 mock non-seal extension post-commit drift recheck root",
                    "",
                    f"gate: `{payload['gate']}`",
                    "seal_chain_extended: false",
                    "does_not_overwrite: _mock_c_fm02.._mock_c_fm13 / standard dryrun",
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
        "matrix_copy": matrix_dst_rel,
    }


def main(argv: Any = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "C-FM-14 non-seal extension post-commit drift recheck QA (offline)"
        )
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        help="隔离 mock 写根（须 validation/_mock_*；不得覆盖 MOCK3–15）",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="硬拒绝：本 runner 禁止 production EXECUTE",
    )
    args = parser.parse_args(argv)
    if args.execute:
        print("EXECUTE_PRODUCTION_SNAPSHOT_REBUILD_FORBIDDEN", file=sys.stderr)
        return 2

    paths = DriftRecheckPaths(output_root_rel=args.output_root)
    payload = run_nonseal_extension_post_commit_drift_recheck(paths=paths)
    paths_written = write_reports(payload)
    print(f"task_id: {payload['task_id']}")
    print(f"gate: {payload['gate']}")
    for k, v in sorted(payload["layer_gates"].items()):
        print(f"layer_{k}: {v}")
    print(f"fail_count: {payload['fail_count']}")
    print(f"cninfo_calls: {payload['cninfo_calls']}")
    print("execute_production_snapshot_rebuild: false")
    print("seal_chain_extended: false")
    print(f"drift_detected: {payload['drift_detected']}")
    print(f"hold_recommendation: {payload['hold_recommendation']}")
    print(f"output_root: {payload['output_root']}")
    print(f"report_md: {paths_written['report_md']}")
    print(
        f"ready_for_commit: "
        f"{'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}"
    )
    return 0 if payload["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
