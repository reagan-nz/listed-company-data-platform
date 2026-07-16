#!/usr/bin/env python3
"""
CNINFO C-class — 规模 full_market_unique_union composition identity lock +
combined_dryrun_cohort composition identity lock + company_coverage_scale
composition identity lock + cross_full_market_scale_repro_wall_meta_bundle
identity lock runner（离线 · C-FM-47）。

Usage:
    python3 lab/run_cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety.py
    python3 lab/run_cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety.py \\
      --output-root outputs/validation/_mock_c_fm47_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety
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

from cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    TASK_ID,
    FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths,
    run_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety,
)
from cninfo_c_class_erad_cleanup_guard import BASE_DIR  # noqa: E402

REPORT_ROOT_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety_20260716.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety_20260716.json"
)
TASK_REPORT_REL = (
    "outputs/validation/"
    "cninfo_c_class_fm47_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety_20260716.md"
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
        (
            "full_market_unique_union_path",
            "full_market_unique_union_composition_identity_lock_ledger.json",
        ),
        (
            "combined_dryrun_cohort_path",
            "combined_dryrun_cohort_composition_identity_lock_ledger.json",
        ),
        (
            "company_coverage_scale_path",
            "company_coverage_scale_composition_identity_lock_ledger.json",
        ),
        (
            "cross_full_market_scale_repro_wall_meta_bundle_path",
            "cross_full_market_scale_repro_wall_meta_bundle_identity_lock_ledger.json",
        ),
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
        "combined_dryrun_coverage": payload["combined_dryrun_coverage"],
        "union_complete": payload["union_complete"],
        "union_partial": payload["union_partial"],
        "union_failed": payload["union_failed"],
        "resume_total": payload["resume_total"],
        "resume_improved": payload["resume_improved"],
        "resume_same": payload["resume_same"],
        "resume_worse": payload["resume_worse"],
        "surface_harvest_delta_n": payload["surface_harvest_delta_n"],
        "partial_risk_bands": payload["partial_risk_bands"],
        "residual_safety_coverage": payload["residual_safety_coverage"],
        "full_market_unique_union_composition_sha256": payload[
            "full_market_unique_union_composition_sha256"
        ],
        "combined_dryrun_cohort_composition_sha256": payload[
            "combined_dryrun_cohort_composition_sha256"
        ],
        "company_coverage_scale_composition_sha256": payload[
            "company_coverage_scale_composition_sha256"
        ],
        "cross_full_market_scale_repro_wall_meta_bundle_sha256": payload[
            "cross_full_market_scale_repro_wall_meta_bundle_sha256"
        ],
        "cross_unique_surface_additive_tier_dryrun_wall_meta_bundle_sha256": payload.get(
            "cross_unique_surface_additive_tier_dryrun_wall_meta_bundle_sha256"
        ),
        "full_market_unique_union_formula": payload["full_market_unique_union_formula"],
        "combined_dryrun_cohort_formula": payload["combined_dryrun_cohort_formula"],
        "company_coverage_scale_formula": payload["company_coverage_scale_formula"],
        "residual_formula": payload["residual_formula"],
        "resume_taxonomy_formula": payload["resume_taxonomy_formula"],
        "risk_band_status_formula": payload["risk_band_status_formula"],
        "coverage_formula": payload["coverage_formula"],
        "union_formula": payload["union_formula"],
        "union_status_formula": payload["union_status_formula"],
        "surface_formula": payload["surface_formula"],
        "additive_formula": payload["additive_formula"],
        "tier_coverage_formula": payload["tier_coverage_formula"],
        "risk_band_formula": payload["risk_band_formula"],
        "resume_formula": payload["resume_formula"],
        "output_root": payload["output_root"],
        "matrix_path": payload["matrix_path"],
        "fingerprint_path": payload["fingerprint_path"],
        "fingerprint": payload["fingerprint"],
        "full_market_unique_union_path": payload["full_market_unique_union_path"],
        "combined_dryrun_cohort_path": payload["combined_dryrun_cohort_path"],
        "company_coverage_scale_path": payload["company_coverage_scale_path"],
        "cross_full_market_scale_repro_wall_meta_bundle_path": payload[
            "cross_full_market_scale_repro_wall_meta_bundle_path"
        ],
        "battery_path": payload["battery_path"],
        "packet_path": payload["packet_path"],
        "observed_fps": payload["observed_fps"],
        "inputs": payload["inputs"],
        "seal_chain_extended": False,
    }
    with open(_abs(REPORT_JSON_REL), "w", encoding="utf-8") as fh:
        json.dump(json_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    layer_lines = [
        f"| layer `{k}` | `{v}` |" for k, v in sorted(payload["layer_gates"].items())
    ]
    md_lines = [
        "# C-FM-47 Scale Lineage/Drift/Protected/Repro-Wall-Meta-Bundle",
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
        f"| full_market_unique_union_formula | **{payload['full_market_unique_union_formula']}** |",
        f"| combined_dryrun_cohort_formula | **{payload['combined_dryrun_cohort_formula']}** |",
        f"| company_coverage_scale_formula | **{payload['company_coverage_scale_formula']}** |",
        f"| residual_safety_coverage | **{payload['residual_safety_coverage']}** |",
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
        "- FM46 连续：unique=**2249** · dryrun=**1053** · residual=**117** · "
        "resume=**28/1/0** · risk=**75/14/12/5** · coverage_wall_meta",
        "- full_market_unique_union_composition_identity_lock：**overlap_delta=12**",
        "- combined_dryrun_cohort_composition_identity_lock：**dry863=2**",
        "- company_coverage_scale_composition_identity_lock：**h863>p35>p3>p2>fu**",
        "- cross_full_market_scale_repro_wall_meta_bundle_identity_lock："
        "unique/dryrun/coverage/repro 墙元捆绑身份锁",
        "- MOCK3–48 冻结 · MOCK49 放行",
        "",
        "## Hold",
        "",
        "```",
        f"c_fm_47_scale_lineage_drift_protected_repro_wall_meta_bundle_safety_gate = "
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
        "# C-FM-47 — Scale Lineage/Drift/Protected/Repro-Wall-Meta-Bundle",
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
        "在 C-FM-46 已 commit 且 EXECUTE 仍 human-held 之上，继续 **非 seal** "
        "规模/安全能力（非 extension↔drift / seal-chain）：**full_market_unique_union "
        "composition identity lock（overlap_delta=12）**、**combined_dryrun_cohort composition "
        "identity lock（dry863=2）**、**company_coverage_scale composition identity "
        "lock（h863>p35>p3>p2>fu）**、**cross_full_market_scale_repro_wall_meta_bundle "
        "identity lock（unique/dryrun/coverage/repro 墙元捆绑）**、**FM46 连续 + MOCK49 隔离**；"
        "产物写入隔离 MOCK49（不覆盖 MOCK3–48）。",
        "",
        "## Capability gain",
        "",
        "1. FM46 packet/fingerprint/gate/ledger 零漂移连续（unique=2249 · 1053 · "
        "residual 117 · resume 28/1/0 · risk 75/14/12/5 · coverage_wall_meta）",
        "2. full_market_unique_union_composition_identity_lock：overlap_delta=12 · 组成身份锁",
        "3. combined_dryrun_cohort_composition_identity_lock：dry863=2 · 组成身份锁",
        "4. company_coverage_scale_composition_identity_lock：h863>p35>p3>p2>fu · 组成身份锁",
        "5. cross_full_market_scale_repro_wall_meta_bundle_identity_lock："
        "unique/dryrun/coverage/repro 墙元捆绑 · 组成变异拒绝",
        "6. output-root：MOCK3–48 冻结 · MOCK49 放行；harvest/resume 写拒绝",
        "7. FM-01..05 + FM-12..46 gate battery（跳过 seal FM06–11）",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK49 + C-ROOT-002 说明 |",
        f"| `{DEFAULT_MOCK_OUTPUT_ROOT_REL}/` | 隔离 scale 产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* unique/dryrun/coverage/repro-wall ledger / battery / packet | 生产 snapshot EXECUTE |",
        "| 只读 FM01–05 / FM12–46 gate JSON / harvest / resume / dryrun / exclusion | CNINFO live |",
        "| offline QA · unique/dryrun/coverage/repro-wall 重算（不覆盖 MOCK3–48） | 覆盖 MOCK3–48 |",
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
        f"c_fm_47_scale_lineage_drift_protected_repro_wall_meta_bundle_safety_gate = "
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
        f"full_market_unique_union_formula = {payload['full_market_unique_union_formula']}",
        f"combined_dryrun_cohort_formula = {payload['combined_dryrun_cohort_formula']}",
        f"company_coverage_scale_formula = {payload['company_coverage_scale_formula']}",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包（unique/dryrun/coverage/repro-wall-meta-bundle only）",
        "- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）",
        "- Human 仍可用既有 checklist 做 EXECUTE 决策（本包不翻转 approved）",
        "",
    ]
    with open(_abs(TASK_REPORT_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(task_lines))

    return {
        "report_md": REPORT_MD_REL,
        "report_json": REPORT_JSON_REL,
        "task_report": TASK_REPORT_REL,
        "matrix_copy": matrix_dst_rel,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "C-FM-47 scale unique/dryrun/coverage/repro-wall-meta-bundle "
            "safety (offline)"
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
            "C-FM-47 is offline QA only; KEEP_EXECUTE_FALSE",
            file=sys.stderr,
        )
        return 2

    payload = run_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety(
        paths=FullMarketUniqueDryrunCoverageReproWallMetaBundlePaths(
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
                "full_market_unique_union_formula": payload[
                    "full_market_unique_union_formula"
                ],
                "combined_dryrun_cohort_formula": payload[
                    "combined_dryrun_cohort_formula"
                ],
                "company_coverage_scale_formula": payload[
                    "company_coverage_scale_formula"
                ],
                "full_market_unique_union_composition_sha256": payload[
                    "full_market_unique_union_composition_sha256"
                ],
                "combined_dryrun_cohort_composition_sha256": payload[
                    "combined_dryrun_cohort_composition_sha256"
                ],
                "company_coverage_scale_composition_sha256": payload[
                    "company_coverage_scale_composition_sha256"
                ],
                "cross_full_market_scale_repro_wall_meta_bundle_sha256": payload[
                    "cross_full_market_scale_repro_wall_meta_bundle_sha256"
                ],
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
