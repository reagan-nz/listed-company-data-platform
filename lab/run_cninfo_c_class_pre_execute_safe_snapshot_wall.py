#!/usr/bin/env python3
"""
CNINFO C-class — Pre-EXECUTE 安全 snapshot 墙冻结 runner（离线 · C-FM-06）。

Usage:
    python3 lab/run_cninfo_c_class_pre_execute_safe_snapshot_wall.py
    python3 lab/run_cninfo_c_class_pre_execute_safe_snapshot_wall.py \\
      --output-root outputs/validation/_mock_c_fm06_pre_execute_safe_snapshot_wall
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
from cninfo_c_class_pre_execute_safe_snapshot_wall import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    TASK_ID,
    WallPaths,
    run_pre_execute_safe_snapshot_wall,
)

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_pre_execute_safe_snapshot_wall"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_safe_snapshot_wall_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_safe_snapshot_wall_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/cninfo_c_class_fm06_pre_execute_safe_snapshot_wall_20260715.md"
)
TEST_SUMMARY_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_safe_snapshot_wall_test_summary_20260715.md"
)


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def write_reports(payload: Dict[str, Any]) -> Dict[str, str]:
    os.makedirs(_abs(REPORT_ROOT_REL), exist_ok=True)
    os.makedirs(os.path.dirname(_abs(REPORT_MD_REL)), exist_ok=True)

    matrix_src = _abs(payload["matrix_path"])
    matrix_dst_rel = f"{REPORT_ROOT_REL}/wall_matrix.csv"
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
        "fail_count": payload["fail_count"],
        "matrix_rows": payload["matrix_rows"],
        "output_root": payload["output_root"],
        "matrix_path": payload["matrix_path"],
        "fingerprint_path": payload["fingerprint_path"],
        "fingerprint": payload["fingerprint"],
        "exclusion_fingerprint": payload["exclusion_fingerprint"],
        "exclusion_fingerprint_path": payload["exclusion_fingerprint_path"],
        "battery_path": payload["battery_path"],
        "human_approval_packet_path": payload["human_approval_packet_path"],
        "human_approval_packet": payload["human_approval_packet"],
        "inputs": payload["inputs"],
        "mock_root_is_isolated": payload["mock_root_is_isolated"],
    }
    with open(_abs(REPORT_JSON_REL), "w", encoding="utf-8") as fh:
        json.dump(json_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    layer_lines = [
        f"| layer `{k}` | `{v}` |" for k, v in sorted(payload["layer_gates"].items())
    ]
    md_lines = [
        "# C-FM-06 Pre-EXECUTE Safe Snapshot Wall Freeze",
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
        f"| wall fingerprint | `{payload['fingerprint'].get('fingerprint_sha256', '')}` |",
        f"| exclusion fingerprint | `{payload['exclusion_fingerprint'].get('fingerprint_sha256', '')}` |",
        "| approved_for_snapshot_rebuild | **false** |",
        "",
        "## Capability",
        "",
        "1. FM-01..05 gate battery 只读聚合（含 FM-05）",
        "2. exclusion universe 结构冻结（19 行 · 18 唯一 · 7+3+9 · 无 promotion）",
        "3. dual-layer QA closure 冻结（coverage 10/10 · 索引集合）",
        "4. EXECUTE 硬墙（execute=false · 生产写拒绝 · 不翻转人批）",
        "5. protected_output_roots.csv 注册一致性（MOCK3–8 · AUTH1）",
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
            f"c_fm_06_pre_execute_safe_snapshot_wall_gate = {payload['gate']}",
            "execute_production_snapshot_rebuild = false",
            "approved_for_snapshot_rebuild = false",
            "cninfo_calls = 0",
            f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
            "```",
            "",
            "## Artifacts",
            "",
            f"- [{payload['matrix_path']}]({os.path.relpath(_abs(payload['matrix_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{matrix_dst_rel}]({os.path.relpath(matrix_dst, os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{REPORT_JSON_REL}]({os.path.basename(REPORT_JSON_REL)})",
            f"- [{payload['human_approval_packet_path']}]({os.path.relpath(_abs(payload['human_approval_packet_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            "",
        ]
    )
    with open(_abs(REPORT_MD_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    task_lines = [
        "# C-FM-06 — Pre-EXECUTE Safe Snapshot Wall Freeze",
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
        "在 C-FM-05 之上，补齐 **Pre-EXECUTE 安全 snapshot 墙冻结**：FM-01..05 gate battery、"
        "exclusion universe 结构指纹、dual-layer QA closure 10/10 冻结、EXECUTE 硬墙与人批冻结包；"
        "产物写入隔离 mock cohort。",
        "",
        "## Capability gain",
        "",
        "1. `cninfo_c_class_pre_execute_safe_snapshot_wall`：五层墙冻结 matrix",
        "2. FM-01..05 PASS_OFFLINE battery（含 FM-05 完整性 gate）",
        "3. exclusion universe 冻结：19 行 · 18 唯一码 · 家族 7+3+9 · promotion=0",
        "4. dual-layer QA closure 冻结：coverage 10/10 · empty3/partial7 索引集合",
        "5. EXECUTE 硬墙：execute=false · 生产写拒绝 · approved_for_snapshot_rebuild 保持 false",
        "6. protected CSV：MOCK3–8 + AUTH1 注册一致性",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_pre_execute_safe_snapshot_wall.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_pre_execute_safe_snapshot_wall.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_pre_execute_safe_snapshot_wall.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK8 |",
        f"| `{payload['output_root']}/` | 隔离墙冻结产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* 墙矩阵 / 指纹 / battery / 人批包 | 生产 snapshot EXECUTE |",
        "| 只读 FM gate JSON / exclusion / dual-layer 索引 / protected CSV | CNINFO live |",
        "| offline QA | 覆盖权威 dual-layer 索引 |",
        "| | commit/push（本包未执行） |",
        "| | verified / production_ready 声称 |",
        "| | 翻转 approved_for_snapshot_rebuild |",
        "",
        "## Wall / gate",
        "",
        "```",
        f"c_fm_06_pre_execute_safe_snapshot_wall_gate = {payload['gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包",
        "- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）",
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
                    "# C-FM-06 mock pre-EXECUTE wall cohort root",
                    "",
                    f"gate: `{payload['gate']}`",
                    "execute_production_snapshot_rebuild: false",
                    "approved_for_snapshot_rebuild: false",
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
        description="C-FM-06 pre-EXECUTE safe snapshot wall freeze (offline)"
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        help="隔离 mock 写根（须 validation/_mock_*）",
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

    paths = WallPaths(output_root_rel=args.output_root)
    payload = run_pre_execute_safe_snapshot_wall(paths=paths)
    paths_written = write_reports(payload)
    print(f"task_id: {payload['task_id']}")
    print(f"gate: {payload['gate']}")
    for k, v in sorted(payload["layer_gates"].items()):
        print(f"layer_{k}: {v}")
    print(f"fail_count: {payload['fail_count']}")
    print(f"cninfo_calls: {payload['cninfo_calls']}")
    print("execute_production_snapshot_rebuild: false")
    print("approved_for_snapshot_rebuild: false")
    print(f"output_root: {payload['output_root']}")
    print(f"report_md: {paths_written['report_md']}")
    print(f"ready_for_commit: {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}")
    return 0 if payload["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
