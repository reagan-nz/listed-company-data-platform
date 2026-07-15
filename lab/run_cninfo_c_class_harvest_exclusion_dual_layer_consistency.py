#!/usr/bin/env python3
"""
CNINFO C-class — harvest/exclusion/dual-layer 一致性 QA runner（离线 · C-FM-03）。

Usage:
    python3 lab/run_cninfo_c_class_harvest_exclusion_dual_layer_consistency.py
    python3 lab/run_cninfo_c_class_harvest_exclusion_dual_layer_consistency.py \\
      --output-root outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency
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
from cninfo_c_class_harvest_exclusion_dual_layer_consistency import (  # noqa: E402
    ConsistencyPaths,
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    TASK_ID,
    run_harvest_exclusion_dual_layer_consistency,
)

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_harvest_exclusion_dual_layer_consistency"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/cninfo_c_class_fm03_harvest_exclusion_dual_layer_20260715.md"
)


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def write_reports(payload: Dict[str, Any]) -> Dict[str, str]:
    os.makedirs(_abs(REPORT_ROOT_REL), exist_ok=True)
    os.makedirs(os.path.dirname(_abs(REPORT_MD_REL)), exist_ok=True)

    # 复制矩阵到报告根（便于索引；权威仍在 mock 根）
    matrix_src = _abs(payload["matrix_path"])
    matrix_dst_rel = f"{REPORT_ROOT_REL}/consistency_matrix.csv"
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
        "fail_count": payload["fail_count"],
        "matrix_rows": payload["matrix_rows"],
        "output_root": payload["output_root"],
        "matrix_path": payload["matrix_path"],
        "fingerprint_863_path": payload["fingerprint_863_path"],
        "fingerprint_863": payload["fingerprint_863"],
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
        "# C-FM-03 Harvest / Exclusion / Dual-layer Consistency",
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
        f"| 863 fingerprint | `{payload['fingerprint_863'].get('fingerprint_sha256', '')}` |",
        "",
        "## Capability",
        "",
        "1. 家族感知 harvest↔exclusion（partial7=`partial` · empty3=`complete` 但出 pool）",
        "2. dual-layer cohort 工具：empty3+partial7 索引并集 = caveat10 · coverage 10/10",
        "3. manifest↔reconcile：holdout9 不膨胀 slice1 排除集",
        "4. 更大 mock：863 harvest ledger 只读结构核验 + 隔离指纹",
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
            f"c_fm_03_harvest_exclusion_dual_layer_consistency_gate = {payload['gate']}",
            "execute_production_snapshot_rebuild = false",
            "cninfo_calls = 0",
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

    # 任务包摘要（controller 用）
    task_lines = [
        "# C-FM-03 — Harvest/Exclusion/Dual-layer 一致性 + 863 结构 Mock",
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
        "在 C-FM-02 lineage 之上，新增 **家族感知 harvest/exclusion 一致性**、"
        "**dual-layer cohort 交叉核验**、**manifest↔reconcile（holdout9 不膨胀）**、"
        "以及 **863 harvest ledger 更大 mock 结构指纹**。",
        "",
        "## Capability gain",
        "",
        "1. `cninfo_c_class_harvest_exclusion_dual_layer_consistency`：四层 consistency matrix",
        "2. partial7/empty3 家族 ↔ ledger status ↔ pool_decision 机器核验",
        "3. dual-layer empty3+partial7 索引并集 = caveat10 · coverage 10/10（只读，不覆盖权威索引）",
        "4. holdout9 隔离于 slice1（除 partial 重叠 000003）",
        "5. 863 ledger 861 complete 结构指纹写入 validation/_mock_*",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_harvest_exclusion_dual_layer_consistency.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_harvest_exclusion_dual_layer_consistency.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_harvest_exclusion_dual_layer_consistency.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK5 |",
        f"| `{payload['output_root']}/` | 隔离一致性产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* 一致性矩阵 / 指纹 | 生产 snapshot EXECUTE |",
        "| 只读 harvest / exclusion / dual-layer 索引 | CNINFO live |",
        "| offline QA | 覆盖 empty3/partial7 权威索引 |",
        "| | commit/push（本包未执行） |",
        "| | verified / production_ready 声称 |",
        "",
        "## Wall / gate",
        "",
        "```",
        f"c_fm_03_harvest_exclusion_dual_layer_consistency_gate = {payload['gate']}",
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
    with open(_abs(TASK_REPORT_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(task_lines))

    readme = _abs(f"{payload['output_root']}/README.md")
    os.makedirs(os.path.dirname(readme), exist_ok=True)
    with open(readme, "w", encoding="utf-8") as fh:
        fh.write(
            "\n".join(
                [
                    "# C-FM-03 mock consistency root",
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
        description="C-FM-03 harvest/exclusion/dual-layer consistency (offline)"
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        help="隔离 mock 写根（须含 _mock_*）",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="禁止：生产 EXECUTE（硬拒绝）",
    )
    args = parser.parse_args()
    if args.execute:
        raise RuntimeError(
            "C_FM03_EXECUTE_FORBIDDEN: 本 runner 仅离线一致性 QA，禁止 --execute"
        )

    payload = run_harvest_exclusion_dual_layer_consistency(
        paths=ConsistencyPaths(output_root_rel=args.output_root)
    )
    paths = write_reports(payload)

    print(f"gate: {payload['gate']}")
    print(f"layer_gates: {payload['layer_gates']}")
    print(f"fail_count: {payload['fail_count']}/{payload['matrix_rows']}")
    print(f"output_root: {payload['output_root']}")
    print(f"matrix_path: {payload['matrix_path']}")
    print(
        "fingerprint_863: "
        f"{(payload.get('fingerprint_863') or {}).get('fingerprint_sha256', '')}"
    )
    print(f"report_md: {paths['report_md']}")
    print(f"task_report: {paths['task_report']}")
    print("cninfo_calls=0")
    print("execute_production_snapshot_rebuild: false")
    return 0 if payload["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
