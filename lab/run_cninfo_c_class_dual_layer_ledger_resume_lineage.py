#!/usr/bin/env python3
"""
CNINFO C-class — ledger↔resume-audit dual-layer lineage QA runner（离线 · C-FM-04）。

Usage:
    python3 lab/run_cninfo_c_class_dual_layer_ledger_resume_lineage.py
    python3 lab/run_cninfo_c_class_dual_layer_ledger_resume_lineage.py \\
      --output-root outputs/validation/_mock_c_fm04_dual_layer_ledger_resume_lineage
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

from cninfo_c_class_dual_layer_ledger_resume_lineage import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    LineagePaths,
    TASK_ID,
    run_dual_layer_ledger_resume_lineage,
)
from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_dual_layer_ledger_resume_lineage"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/cninfo_c_class_fm04_dual_layer_ledger_resume_lineage_20260715.md"
)


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def write_reports(payload: Dict[str, Any]) -> Dict[str, str]:
    os.makedirs(_abs(REPORT_ROOT_REL), exist_ok=True)
    os.makedirs(os.path.dirname(_abs(REPORT_MD_REL)), exist_ok=True)

    matrix_src = _abs(payload["matrix_path"])
    matrix_dst_rel = f"{REPORT_ROOT_REL}/lineage_matrix.csv"
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
        "fingerprint_path": payload["fingerprint_path"],
        "fingerprint": payload["fingerprint"],
        "battery_path": payload["battery_path"],
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
        "# C-FM-04 Ledger / Resume-audit Dual-layer Lineage",
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
        f"| lineage fingerprint | `{payload['fingerprint'].get('fingerprint_sha256', '')}` |",
        "",
        "## Capability",
        "",
        "1. ledger↔resume-audit 双层语义（empty3 合法分歧 · partial7 双层一致）",
        "2. resume↔dual-layer index↔exclusion pool 交叉 lineage",
        "3. 权威 dual-layer 索引写隔离硬化",
        "4. FM-01/02/03 gate battery 只读聚合",
        "5. mock cohort：lineage 矩阵 + 指纹",
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
            f"c_fm_04_dual_layer_ledger_resume_lineage_gate = {payload['gate']}",
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

    task_lines = [
        "# C-FM-04 — Ledger↔Resume-audit Dual-layer Lineage + Index Isolation + FM Battery",
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
        "在 C-FM-03 之上，补齐 **status-ledger ↔ resume-audit** 双层语义 lineage、"
        "**权威 dual-layer 索引写隔离**、以及 **FM-01/02/03 gate battery** 只读聚合；"
        "产物写入隔离 mock cohort。",
        "",
        "## Capability gain",
        "",
        "1. `cninfo_c_class_dual_layer_ledger_resume_lineage`：四层 lineage matrix",
        "2. empty3：ledger=complete / resume=needs_review / sources_present=9（合法分歧）",
        "3. partial7：ledger=partial / resume=partial / live=deferred_targeted_live_after_approval",
        "4. resume 聚合 190/7/3 + needs_review≡empty3 + holdout9 不膨胀",
        "5. `assert_authoritative_dual_layer_index_write_forbidden` 硬化",
        "6. FM-01/02/03 PASS_OFFLINE battery（不重跑 dry-run）",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_dual_layer_ledger_resume_lineage.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_dual_layer_ledger_resume_lineage.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_dual_layer_ledger_resume_lineage.py` | **新增** 测试 |",
        "| `lab/cninfo_c_class_erad_cleanup_guard.py` | 权威 dual-layer 索引写拒绝 |",
        "| `lab/test_cninfo_c_class_erad_cleanup_hardening.py` | case9 索引隔离 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK6 · C-ROOT-AUTH1 |",
        f"| `{payload['output_root']}/` | 隔离 lineage 产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* lineage / 指纹 / battery | 生产 snapshot EXECUTE |",
        "| 只读 harvest / resume-audit / dual-layer 索引 / 既有 FM gate JSON | CNINFO live |",
        "| offline QA | 覆盖权威 dual-layer 索引 |",
        "| | commit/push（本包未执行） |",
        "| | verified / production_ready 声称 |",
        "",
        "## Wall / gate",
        "",
        "```",
        f"c_fm_04_dual_layer_ledger_resume_lineage_gate = {payload['gate']}",
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
                    "# C-FM-04 mock lineage cohort root",
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
        "matrix_copy": matrix_dst_rel,
    }


def main(argv: Any = None) -> int:
    parser = argparse.ArgumentParser(
        description="C-FM-04 dual-layer ledger↔resume lineage QA (offline)"
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

    paths = LineagePaths(output_root_rel=args.output_root)
    payload = run_dual_layer_ledger_resume_lineage(paths=paths)
    paths_written = write_reports(payload)
    print(f"task_id: {payload['task_id']}")
    print(f"gate: {payload['gate']}")
    for k, v in sorted(payload["layer_gates"].items()):
        print(f"layer_{k}: {v}")
    print(f"fail_count: {payload['fail_count']}")
    print(f"cninfo_calls: {payload['cninfo_calls']}")
    print("execute_production_snapshot_rebuild: false")
    print(f"output_root: {payload['output_root']}")
    print(f"report_md: {paths_written['report_md']}")
    print(f"ready_for_commit: {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}")
    return 0 if payload["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
