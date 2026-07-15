#!/usr/bin/env python3
"""
CNINFO C-class — 规模 complete_codes membership freeze + overlap_delta
membership freeze + additive_formula identity lock + tier_coverage_formula
identity lock runner（离线 · C-FM-38）。

Usage:
    python3 lab/run_cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety.py
    python3 lab/run_cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety.py \\
      --output-root outputs/validation/_mock_c_fm38_scale_complete_overlap_additive_tier_formula_safety
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

from cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    TASK_ID,
    CompleteOverlapAdditiveTierFormulaPaths,
    run_scale_complete_overlap_additive_tier_formula_safety,
)
from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402

REPORT_ROOT_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/"
    "cninfo_c_class_fm38_scale_complete_overlap_additive_tier_formula_safety_20260715.md"
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
        ("complete_codes_path", "complete_codes_membership_freeze_ledger.json"),
        ("overlap_delta_path", "overlap_delta_membership_freeze_ledger.json"),
        ("additive_formula_path", "additive_formula_identity_lock_ledger.json"),
        ("tier_coverage_path", "tier_coverage_formula_identity_lock_ledger.json"),
    ):
        src_path = _abs(payload[key])
        dst_path = _abs(f"{REPORT_ROOT_REL}/{name}")
        with open(src_path, encoding="utf-8") as src, open(
            dst_path, "w", encoding="utf-8"
        ) as dst:
            dst.write(src.read())

    bands = payload["partial_risk_bands"]
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
        "combined_dryrun_coverage": payload["combined_dryrun_coverage"],
        "union_complete": payload["union_complete"],
        "union_partial": payload["union_partial"],
        "union_failed": payload["union_failed"],
        "resume_total": payload["resume_total"],
        "resume_improved": payload["resume_improved"],
        "resume_same": payload["resume_same"],
        "resume_worse": payload["resume_worse"],
        "surface_harvest_delta_n": payload["surface_harvest_delta_n"],
        "dry863_extras": payload["dry863_extras"],
        "failed_codes": payload["failed_codes"],
        "resume_same_codes": payload["resume_same_codes"],
        "partial_risk_bands": bands,
        "residual_safety_coverage": payload["residual_safety_coverage"],
        "complete_codes_sha256": payload["complete_codes_sha256"],
        "partial_codes_sha256": payload["partial_codes_sha256"],
        "failed_codes_sha256": payload["failed_codes_sha256"],
        "winner_map_sha256": payload["winner_map_sha256"],
        "improved_codes_sha256": payload["improved_codes_sha256"],
        "same_codes_sha256": payload["same_codes_sha256"],
        "worse_codes_sha256": payload["worse_codes_sha256"],
        "overlap_codes_sha256": payload["overlap_codes_sha256"],
        "batch_priority": payload["batch_priority"],
        "residual_formula": payload["residual_formula"],
        "union_formula": payload["union_formula"],
        "surface_formula": payload["surface_formula"],
        "additive_formula": payload["additive_formula"],
        "tier_coverage_formula": payload["tier_coverage_formula"],
        "output_root": payload["output_root"],
        "matrix_path": payload["matrix_path"],
        "fingerprint_path": payload["fingerprint_path"],
        "fingerprint": payload["fingerprint"],
        "complete_codes_path": payload["complete_codes_path"],
        "overlap_delta_path": payload["overlap_delta_path"],
        "additive_formula_path": payload["additive_formula_path"],
        "tier_coverage_path": payload["tier_coverage_path"],
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
        "# C-FM-38 Scale Complete/Overlap Membership + Additive/Tier Formula",
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
        f"| harvest_additive | **{payload['harvest_additive']}** |",
        f"| surface_unique | **{payload['surface_unique']}** |",
        f"| combined_dryrun_coverage | **{payload['combined_dryrun_coverage']}** |",
        f"| surface_harvest_delta_n | **{payload['surface_harvest_delta_n']}** |",
        f"| union_status | **{payload['union_complete']}/"
        f"{payload['union_partial']}/{payload['union_failed']}** |",
        f"| overlap_delta | **{payload['overlap_delta']}** |",
        f"| resume_taxonomy | **{payload['resume_improved']}/"
        f"{payload['resume_same']}/{payload['resume_worse']}** |",
        f"| residual_safety_coverage | **{payload['residual_safety_coverage']}** |",
        f"| residual_formula | **{payload['residual_formula']}** |",
        f"| union_formula | **{payload['union_formula']}** |",
        f"| surface_formula | **{payload['surface_formula']}** |",
        f"| additive_formula | **{payload['additive_formula']}** |",
        f"| tier_coverage_formula | **{payload['tier_coverage_formula']}** |",
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
        "- FM37 连续：unique=**2249** · dryrun=**1053** · Δ2 · status=**2134/106/9** · "
        "resume=**28/1/0** · residual=**117=106+9+2** · union/surface formulas · "
        "improved/partial/delta/union fps",
        "- complete_codes_membership_freeze：基数 **2134** · sha256 锁 · inject/drop/sha 拒绝",
        "- overlap_delta_membership_freeze：精确 **Δ12**（p35∩fu={000003}+p2∩fu=11）",
        "- additive_formula_identity_lock：**2261=2249+12**",
        "- tier_coverage_formula_identity_lock：**tiers=7 · coverage_sum=3314**",
        "- MOCK3–39 冻结 · MOCK40 放行",
        "",
        "## Hold",
        "",
        "```",
        f"c_fm_38_scale_complete_overlap_additive_tier_formula_safety_gate = "
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
        f"- [{payload['matrix_path']}]"
        f"({os.path.relpath(_abs(payload['matrix_path']), _abs('outputs/validation'))})",
        f"- [{matrix_dst_rel}]({os.path.basename(matrix_dst_rel)})",
        f"- [{REPORT_JSON_REL}]({os.path.basename(REPORT_JSON_REL)})",
        "",
    ]
    with open(_abs(REPORT_MD_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    task_lines = [
        "# C-FM-38 — Scale Complete/Overlap Membership + Additive/Tier Formula",
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
        "在 C-FM-37 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** "
        "规模/安全能力（非 extension↔drift / seal-chain）：**complete_codes membership "
        "freeze（2134）**、**overlap_delta membership freeze（Δ12）**、"
        "**additive_formula identity lock（2261=2249+12）**、**tier_coverage_formula "
        "identity lock（7/3314）**、**FM37 连续 + MOCK40 隔离**；"
        "产物写入隔离 MOCK40（不覆盖 MOCK3–39）。",
        "",
        "## Capability gain",
        "",
        "1. FM37 packet/fingerprint/gate/ledger 零漂移连续（unique=2249 · 1053 · "
        "Δ2 · 2134/106/9 · resume 28/1/0 · residual 117=106+9+2 · risk 75/14/12/5 · "
        "union/surface formulas）",
        "2. complete_codes_membership_freeze：基数 2134 · sha256 锁 · inject/drop/sha 拒绝",
        "3. overlap_delta_membership_freeze：Δ12={000003}+11 p2∩fu · inject/drop/replace 拒绝",
        "4. additive_formula_identity_lock：2261=2249+12 · 公式变异拒绝",
        "5. tier_coverage_formula_identity_lock：tiers=7 · coverage_sum=3314 · 公式变异拒绝",
        "6. output-root：MOCK3–39 冻结 · MOCK40 放行；harvest/resume 写拒绝",
        "7. FM-01..05 + FM-12..37 gate battery（跳过 seal FM06–11）",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_scale_complete_overlap_additive_tier_formula_safety.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK40 + C-ROOT-002 说明 |",
        f"| `{payload['output_root']}/` | 隔离 scale 产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* complete/overlap membership / additive/tier formula ledger / battery / packet | 生产 snapshot EXECUTE |",
        "| 只读 FM01–05 / FM12–37 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |",
        "| offline QA · complete/overlap membership / additive/tier formula 重算（不覆盖 MOCK3–39） | 覆盖 MOCK3–39 |",
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
        f"c_fm_38_scale_complete_overlap_additive_tier_formula_safety_gate = "
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
        f"harvest_additive = {payload['harvest_additive']}",
        f"surface_unique = {payload['surface_unique']}",
        f"combined_dryrun_coverage = {payload['combined_dryrun_coverage']}",
        f"union_complete = {payload['union_complete']}",
        f"union_partial = {payload['union_partial']}",
        f"union_failed = {payload['union_failed']}",
        f"overlap_delta = {payload['overlap_delta']}",
        f"resume_improved = {payload['resume_improved']}",
        f"resume_same = {payload['resume_same']}",
        f"resume_worse = {payload['resume_worse']}",
        f"surface_harvest_delta_n = {payload['surface_harvest_delta_n']}",
        f"residual_safety_coverage = {payload['residual_safety_coverage']}",
        f"residual_formula = {payload['residual_formula']}",
        f"union_formula = {payload['union_formula']}",
        f"surface_formula = {payload['surface_formula']}",
        f"additive_formula = {payload['additive_formula']}",
        f"tier_coverage_formula = {payload['tier_coverage_formula']}",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包（complete/overlap membership + "
        "additive/tier formula only）",
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
                    "# C-FM-38 mock scale complete/overlap/additive/tier formula safety root",
                    "",
                    f"gate: `{payload['gate']}`",
                    "seal_chain_extended: false",
                    f"scale_tier_count: {payload['scale_tier_count']}",
                    f"company_coverage_sum: {payload['company_coverage_sum']}",
                    f"harvest_unique_union: {payload['harvest_unique_union']}",
                    f"combined_dryrun_coverage: {payload['combined_dryrun_coverage']}",
                    f"surface_harvest_delta_n: {payload['surface_harvest_delta_n']}",
                    f"union_status: {payload['union_complete']}/"
                    f"{payload['union_partial']}/{payload['union_failed']}",
                    f"overlap_delta: {payload['overlap_delta']}",
                    f"residual_safety_coverage: {payload['residual_safety_coverage']}",
                    f"residual_formula: {payload['residual_formula']}",
                    f"union_formula: {payload['union_formula']}",
                    f"surface_formula: {payload['surface_formula']}",
                    f"additive_formula: {payload['additive_formula']}",
                    f"tier_coverage_formula: {payload['tier_coverage_formula']}",
                    f"resume_taxonomy: {payload['resume_improved']}/"
                    f"{payload['resume_same']}/{payload['resume_worse']}",
                    "does_not_overwrite: _mock_c_fm02.._mock_c_fm37 / standard dryrun",
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
        description=(
            "C-FM-38 scale complete/overlap membership + "
            "additive/tier formula safety (offline)"
        )
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
            "C-FM-38 is offline QA only; KEEP_EXECUTE_FALSE",
            file=sys.stderr,
        )
        return 2

    payload = run_scale_complete_overlap_additive_tier_formula_safety(
        paths=CompleteOverlapAdditiveTierFormulaPaths(
            output_root_rel=args.output_root
        )
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
                "harvest_additive": payload["harvest_additive"],
                "surface_unique": payload["surface_unique"],
                "combined_dryrun_coverage": payload["combined_dryrun_coverage"],
                "surface_harvest_delta_n": payload["surface_harvest_delta_n"],
                "union_complete": payload["union_complete"],
                "union_partial": payload["union_partial"],
                "union_failed": payload["union_failed"],
                "overlap_delta": payload["overlap_delta"],
                "resume_improved": payload["resume_improved"],
                "resume_same": payload["resume_same"],
                "resume_worse": payload["resume_worse"],
                "scale_tier_count": payload["scale_tier_count"],
                "company_coverage_sum": payload["company_coverage_sum"],
                "residual_safety_coverage": payload["residual_safety_coverage"],
                "residual_formula": payload["residual_formula"],
                "union_formula": payload["union_formula"],
                "surface_formula": payload["surface_formula"],
                "additive_formula": payload["additive_formula"],
                "tier_coverage_formula": payload["tier_coverage_formula"],
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
