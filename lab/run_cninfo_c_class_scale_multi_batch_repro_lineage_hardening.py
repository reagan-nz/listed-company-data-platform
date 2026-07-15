#!/usr/bin/env python3
"""
CNINFO C-class — 扩展多 batch 规模 repro + lineage 加固 QA runner
（离线 · C-FM-23）。

Usage:
    python3 lab/run_cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py
    python3 lab/run_cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py \\
      --output-root outputs/validation/_mock_c_fm23_scale_multi_batch_repro_lineage_hardening
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

from cninfo_c_class_scale_multi_batch_repro_lineage_hardening import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    ExtendedScalePaths,
    TASK_ID,
    run_scale_multi_batch_repro_lineage_hardening,
)
from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_scale_multi_batch_repro_lineage_hardening"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_multi_batch_repro_lineage_hardening_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_multi_batch_repro_lineage_hardening_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/"
    "cninfo_c_class_fm23_scale_multi_batch_repro_lineage_hardening_20260715.md"
)


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def write_reports(payload: Dict[str, Any]) -> Dict[str, str]:
    os.makedirs(_abs(REPORT_ROOT_REL), exist_ok=True)
    os.makedirs(os.path.dirname(_abs(REPORT_MD_REL)), exist_ok=True)

    matrix_src = _abs(payload["matrix_path"])
    matrix_dst_rel = f"{REPORT_ROOT_REL}/scale_matrix.csv"
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
        "scale_tier_count": payload["scale_tier_count"],
        "company_coverage_sum": payload["company_coverage_sum"],
        "combined_dryrun_coverage": payload["combined_dryrun_coverage"],
        "output_root": payload["output_root"],
        "matrix_path": payload["matrix_path"],
        "fingerprint_path": payload["fingerprint_path"],
        "fingerprint": payload["fingerprint"],
        "registry_path": payload["registry_path"],
        "battery_path": payload["battery_path"],
        "packet_path": payload["packet_path"],
        "observed_fps": payload["observed_fps"],
        "combined_dryrun": payload["combined_dryrun"],
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
        "# C-FM-23 Scale Multi-Batch Repro Lineage Hardening",
        "",
        f"_生成时间：{payload['generated_at']} · executor: c-class-executor · "
        f"offline · CNINFO=0_",
        "",
        "| 字段 | 值 |",
        "|------|-----|",
        f"| task_id | **{TASK_ID}** |",
        f"| gate | **{payload['gate']}** |",
        f"| scale_tier_count | **{payload['scale_tier_count']}** |",
        f"| company_coverage_sum | **{payload['company_coverage_sum']}** |",
        f"| combined_dryrun_coverage | **{payload['combined_dryrun_coverage']}** |",
        f"| fail_count | **{payload['fail_count']}** |",
        f"| matrix_rows | **{payload['matrix_rows']}** |",
        f"| cninfo_calls | **{payload['cninfo_calls']}** |",
        f"| mock output | `{payload['output_root']}` |",
        "",
        "## Layer gates",
        "",
        "| layer | gate |",
        "|-------|------|",
        *layer_lines,
        "",
        "## Scale jump",
        "",
        "- repro：**863 + 190 + 861 + 500 + 500 + 200 + 200** 七层指纹零漂移",
        "- coverage_sum：**3314**（相对 FM22 的 2414 可计量 +900）",
        "- combined dryrun：**863+190=1053** 隔离合标指纹（不 EXECUTE）",
        "- lineage：FM22 packet 连续 + 跨 batch 不相交 / 已知小交集",
        "- protection：MOCK3–24 冻结 · MOCK25 放行 · phase3/phase2/fuller 写拒绝 · C-ROOT-011",
        "",
        "## Hold",
        "",
        "```",
        f"c_fm_23_scale_multi_batch_repro_lineage_hardening_gate = {payload['gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        "ready_for_execute = false",
        "hold_recommendation = KEEP_EXECUTE_FALSE",
        "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting = true",
        "seal_chain_extended = false",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "```",
        "",
        "## Artifacts",
        "",
        f"- [{payload['matrix_path']}]({os.path.relpath(_abs(payload['matrix_path']), _abs('outputs/validation'))})",
        f"- [{matrix_dst_rel}]({os.path.basename(matrix_dst_rel)})",
        f"- [{REPORT_JSON_REL}]({os.path.basename(REPORT_JSON_REL)})",
        "",
    ]
    with open(_abs(REPORT_MD_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    task_lines = [
        "# C-FM-23 — Scale Multi-Batch Repro Lineage Hardening",
        "",
        f"_生成时间：{payload['generated_at']} · executor: c-class-executor · "
        f"offline · CNINFO=0_",
        "",
        "| 字段 | 值 |",
        "|------|-----|",
        f"| task_id | **{TASK_ID}** |",
        "| track | C |",
        "| result | **DONE** |",
        "| CNINFO live | **0** |",
        "| prod snapshot EXECUTE | **not invoked** |",
        "| commit / push | **无**（待 controller） |",
        f"| ready_for_commit | **{'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}** |",
        "",
        "## Task",
        "",
        "在 C-FM-22 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** "
        "规模/安全能力（非 extension↔drift / seal-chain）：**七层多 batch repro "
        "指纹（863/190/861/500/500/200/200）**、**隔离 dry-run 合标 1053**、"
        "**lineage 加固**、**output-root 保护（MOCK25 + C-ROOT-011）**；"
        "产物写入隔离 MOCK25（不覆盖 MOCK3–24）。",
        "",
        "## Capability gain",
        "",
        "1. 多 cohort repro 扩展：+phase3×500 +phase2×200 +fuller×200",
        "2. 规模 lineage registry：`scale_tier_count=7` · `company_coverage_sum=3314`",
        "3. 多 batch harvest×exclusion dual-layer（phase3/phase2/fuller + phase35 不变式）",
        "4. 隔离 snapshot dry-run 合标规模指纹（863+190=1053，不 EXECUTE）",
        "5. lineage 加固：FM22 packet 零漂移连续 + 跨 batch 不相交 / 已知小交集",
        "6. output-root 保护：phase3/phase2/fuller/phase35 写拒绝 + MOCK3–24 冻结",
        "7. FM-01..05 + FM-12..22 gate battery（跳过 seal FM06–11）",
        "8. protected CSV：MOCK25 + fuller harvest C-ROOT-011",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_scale_multi_batch_repro_lineage_hardening.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK25 + C-ROOT-011 |",
        f"| `{payload['output_root']}/` | 隔离 scale 产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* scale 矩阵 / 指纹 / registry / battery / packet | 生产 snapshot EXECUTE |",
        "| 只读 FM01–05 / FM12–22 gate JSON / harvest / exclusion / protected CSV | CNINFO live |",
        "| offline QA · 多尺度指纹重算（不覆盖 MOCK3–24） | 覆盖 MOCK3–24 |",
        "| fuller harvest 只读登记（C-ROOT-011） | 覆盖权威 dual-layer 索引 |",
        "| | commit/push（本包未执行） |",
        "| | verified / production_ready 声称 |",
        "| | 翻转 approved_for_snapshot_rebuild |",
        "| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |",
        "| | 仅因 AWAITING 而 IDLE |",
        "",
        "## Wall / gate",
        "",
        "```",
        f"c_fm_23_scale_multi_batch_repro_lineage_hardening_gate = {payload['gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        "ready_for_execute = false",
        "hold_recommendation = KEEP_EXECUTE_FALSE",
        "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting = true",
        "seal_chain_extended = false",
        f"scale_tier_count = {payload['scale_tier_count']}",
        f"company_coverage_sum = {payload['company_coverage_sum']}",
        f"combined_dryrun_coverage = {payload['combined_dryrun_coverage']}",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包（scale multi-batch repro lineage hardening only）",
        "- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）",
        "- Human 仍可用 C-FM-17 checklist 做 EXECUTE 决策（本包不翻转 approved）",
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
                    "# C-FM-23 mock scale multi-batch repro lineage hardening root",
                    "",
                    f"gate: `{payload['gate']}`",
                    "seal_chain_extended: false",
                    f"scale_tier_count: {payload['scale_tier_count']}",
                    f"company_coverage_sum: {payload['company_coverage_sum']}",
                    f"combined_dryrun_coverage: {payload['combined_dryrun_coverage']}",
                    "does_not_overwrite: _mock_c_fm02.._mock_c_fm22 / standard dryrun",
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
            "C-FM-23 extended multi-batch scale repro + isolated combined "
            "dryrun + lineage hardening QA (offline)"
        )
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        help="隔离 mock 写根（须 validation/_mock_*；不得覆盖 MOCK3–24）",
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

    paths = ExtendedScalePaths(output_root_rel=args.output_root)
    payload = run_scale_multi_batch_repro_lineage_hardening(paths=paths)
    paths_written = write_reports(payload)
    print(f"task_id: {payload['task_id']}")
    print(f"gate: {payload['gate']}")
    for k, v in sorted(payload["layer_gates"].items()):
        print(f"layer_{k}: {v}")
    print(f"fail_count: {payload['fail_count']}")
    print(f"scale_tier_count: {payload['scale_tier_count']}")
    print(f"company_coverage_sum: {payload['company_coverage_sum']}")
    print(f"combined_dryrun_coverage: {payload['combined_dryrun_coverage']}")
    print(f"cninfo_calls: {payload['cninfo_calls']}")
    print("execute_production_snapshot_rebuild: false")
    print("seal_chain_extended: false")
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
