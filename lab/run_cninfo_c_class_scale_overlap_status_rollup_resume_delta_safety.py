#!/usr/bin/env python3
"""
CNINFO C-class — 规模 overlap 台账 + status rollup + resume delta 安全 runner
（离线 · C-FM-25）。

Usage:
    python3 lab/run_cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety.py
    python3 lab/run_cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety.py \\
      --output-root outputs/validation/_mock_c_fm25_scale_overlap_status_rollup_resume_delta_safety
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

from cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    TASK_ID,
    OverlapStatusPaths,
    run_scale_overlap_status_rollup_resume_delta_safety,
)
from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/"
    "cninfo_c_class_fm25_scale_overlap_status_rollup_resume_delta_safety_20260715.md"
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

    for key, name in (
        ("overlap_ledger_path", "overlap_code_ledger.json"),
        ("status_rollup_path", "harvest_status_rollup.json"),
        ("resume_delta_path", "resume_delta_ledger.json"),
    ):
        src_path = _abs(payload[key])
        dst_path = _abs(f"{REPORT_ROOT_REL}/{name}")
        with open(src_path, encoding="utf-8") as src, open(
            dst_path, "w", encoding="utf-8"
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
        "harvest_unique_union": payload["harvest_unique_union"],
        "harvest_additive": payload["harvest_additive"],
        "overlap_delta": payload["overlap_delta"],
        "surface_unique": payload["surface_unique"],
        "union_complete": payload["union_complete"],
        "union_partial": payload["union_partial"],
        "union_failed": payload["union_failed"],
        "resume_total": payload["resume_total"],
        "resume_improved": payload["resume_improved"],
        "resume_same": payload["resume_same"],
        "resume_worse": payload["resume_worse"],
        "dry863_extras": payload["dry863_extras"],
        "output_root": payload["output_root"],
        "matrix_path": payload["matrix_path"],
        "fingerprint_path": payload["fingerprint_path"],
        "fingerprint": payload["fingerprint"],
        "overlap_ledger_path": payload["overlap_ledger_path"],
        "status_rollup_path": payload["status_rollup_path"],
        "resume_delta_path": payload["resume_delta_path"],
        "battery_path": payload["battery_path"],
        "packet_path": payload["packet_path"],
        "observed_fps": payload["observed_fps"],
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
        "# C-FM-25 Scale Overlap Status Rollup + Resume Delta Safety",
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
        f"| harvest_unique_union | **{payload['harvest_unique_union']}** |",
        f"| overlap_delta | **{payload['overlap_delta']}** |",
        f"| union_status | **{payload['union_complete']}/"
        f"{payload['union_partial']}/{payload['union_failed']}** |",
        f"| resume_delta | **{payload['resume_improved']}/"
        f"{payload['resume_same']}/{payload['resume_worse']}** |",
        f"| surface_unique | **{payload['surface_unique']}** |",
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
        "## Scale / safety gain",
        "",
        "- FM24 连续：unique=**2249** · surface=**2251** · resume=**29**",
        "- 精确 overlap 台账：p35∩fu={000003} · p2∩fu=11 码 · Δ12 指纹冻结",
        "- unique status rollup：**2134 complete / 106 partial / 9 failed**",
        "- resume vs base delta：**28 improved / 1 same(301212) / 0 worse** · 写拒绝",
        "- dry863 extras={000037,000055}：不在 harvest · 不在 exclusion · pending",
        "- MOCK3–26 冻结 · MOCK27 放行",
        "",
        "## Hold",
        "",
        "```",
        f"c_fm_25_scale_overlap_status_rollup_resume_delta_safety_gate = "
        f"{payload['gate']}",
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
        "# C-FM-25 — Scale Overlap Status Rollup + Resume Delta Safety",
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
        "在 C-FM-24 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** "
        "规模/安全能力（非 extension↔drift / seal-chain）：**精确 overlap 代码台账"
        "（Δ12）**、**unique-union status rollup（2134/106/9）**、**resume vs base "
        "delta（28/1/0）**、**dry863 extras 隔离**、**FM24 连续 + MOCK27 隔离**；"
        "产物写入隔离 MOCK27（不覆盖 MOCK3–26）。",
        "",
        "## Capability gain",
        "",
        "1. FM24 packet/fingerprint 零漂移连续（unique=2249 · surface=2251）",
        "2. 精确 overlap 台账：p35∩fu={000003} · p2∩fu=11 码冻结指纹",
        "3. harvest unique status rollup：complete=2134 · partial=106 · failed=9",
        "4. resume vs base delta：improved=28 · same=1(301212) · worse=0 · 写拒绝",
        "5. dry863 extras={000037,000055} 相对 harvest/exclusion 隔离（pending）",
        "6. output-root：MOCK3–26 冻结 · MOCK27 放行；harvest/resume 写拒绝",
        "7. FM-01..05 + FM-12..24 gate battery（跳过 seal FM06–11）",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK27 + C-ROOT-002 说明 |",
        f"| `{payload['output_root']}/` | 隔离 scale 产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* overlap/status/resume-delta ledger / battery / packet | 生产 snapshot EXECUTE |",
        "| 只读 FM01–05 / FM12–24 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |",
        "| offline QA · overlap/status/delta 重算（不覆盖 MOCK3–26） | 覆盖 MOCK3–26 |",
        "| resume/phase35 harvest 只读加固（C-ROOT-002） | 覆盖权威 dual-layer 索引 |",
        "| | commit/push（本包未执行） |",
        "| | verified / production_ready 声称 |",
        "| | 翻转 approved_for_snapshot_rebuild |",
        "| | 新增 seal-chain / decision-await / commit-boundary MOCK 层 |",
        "| | 仅因 AWAITING 而 IDLE |",
        "",
        "## Wall / gate",
        "",
        "```",
        f"c_fm_25_scale_overlap_status_rollup_resume_delta_safety_gate = "
        f"{payload['gate']}",
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
        f"harvest_unique_union = {payload['harvest_unique_union']}",
        f"union_complete = {payload['union_complete']}",
        f"union_partial = {payload['union_partial']}",
        f"union_failed = {payload['union_failed']}",
        f"resume_improved = {payload['resume_improved']}",
        f"resume_same = {payload['resume_same']}",
        f"surface_unique = {payload['surface_unique']}",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包（overlap ledger + status rollup + resume delta only）",
        "- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）",
        "- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）",
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
                    "# C-FM-25 mock scale overlap status rollup resume delta safety root",
                    "",
                    f"gate: `{payload['gate']}`",
                    "seal_chain_extended: false",
                    f"scale_tier_count: {payload['scale_tier_count']}",
                    f"company_coverage_sum: {payload['company_coverage_sum']}",
                    f"harvest_unique_union: {payload['harvest_unique_union']}",
                    f"union_status: {payload['union_complete']}/"
                    f"{payload['union_partial']}/{payload['union_failed']}",
                    f"resume_delta: {payload['resume_improved']}/"
                    f"{payload['resume_same']}/{payload['resume_worse']}",
                    "does_not_overwrite: _mock_c_fm02.._mock_c_fm24 / standard dryrun",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="C-FM-25 scale overlap/status/resume-delta safety (offline)"
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        help="隔离 validation/_mock_* 写根",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="禁止：生产 snapshot EXECUTE（本 runner 拒绝）",
    )
    args = parser.parse_args(argv)
    if args.execute:
        print(
            "EXECUTE_PRODUCTION_SNAPSHOT_REBUILD_FORBIDDEN: "
            "C-FM-25 is offline QA only; KEEP_EXECUTE_FALSE",
            file=sys.stderr,
        )
        return 2

    payload = run_scale_overlap_status_rollup_resume_delta_safety(
        paths=OverlapStatusPaths(output_root_rel=args.output_root)
    )
    reports = write_reports(payload)
    print(
        json.dumps(
            {
                "task_id": payload["task_id"],
                "gate": payload["gate"],
                "cninfo_calls": payload["cninfo_calls"],
                "fail_count": payload["fail_count"],
                "harvest_unique_union": payload["harvest_unique_union"],
                "union_complete": payload["union_complete"],
                "union_partial": payload["union_partial"],
                "union_failed": payload["union_failed"],
                "resume_improved": payload["resume_improved"],
                "resume_same": payload["resume_same"],
                "approved_for_snapshot_rebuild": False,
                "hold_recommendation": payload["hold_recommendation"],
                "output_root": payload["output_root"],
                "reports": reports,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if payload["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
