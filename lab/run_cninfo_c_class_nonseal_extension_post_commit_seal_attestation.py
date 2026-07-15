#!/usr/bin/env python3
"""
CNINFO C-class — 非 seal Cross-FM 扩展 post-commit seal attestation runner（离线 · C-FM-16）。

Usage:
    python3 lab/run_cninfo_c_class_nonseal_extension_post_commit_seal_attestation.py
    python3 lab/run_cninfo_c_class_nonseal_extension_post_commit_seal_attestation.py \\
      --output-root outputs/validation/_mock_c_fm16_nonseal_extension_post_commit_seal_attestation
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
from cninfo_c_class_nonseal_extension_post_commit_seal_attestation import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    NonsealPostCommitAttestationPaths,
    TASK_ID,
    run_nonseal_extension_post_commit_seal_attestation,
)

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_nonseal_extension_post_commit_seal_attestation"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_post_commit_seal_attestation_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_nonseal_extension_post_commit_seal_attestation_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/"
    "cninfo_c_class_fm16_nonseal_extension_post_commit_seal_attestation_20260715.md"
)


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def write_reports(payload: Dict[str, Any]) -> Dict[str, str]:
    os.makedirs(_abs(REPORT_ROOT_REL), exist_ok=True)
    os.makedirs(os.path.dirname(_abs(REPORT_MD_REL)), exist_ok=True)

    matrix_src = _abs(payload["matrix_path"])
    matrix_dst_rel = f"{REPORT_ROOT_REL}/attestation_matrix.csv"
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
        "handoff_packet_path": payload["handoff_packet_path"],
        "handoff_packet": payload["handoff_packet"],
        "seal_packet_path": payload["seal_packet_path"],
        "seal_packet": payload["seal_packet"],
        "frozen_extension_fp_sha256": payload["frozen_extension_fp_sha256"],
        "frozen_drift_fp_sha256": payload["frozen_drift_fp_sha256"],
        "frozen_boundary_fp_sha256": payload["frozen_boundary_fp_sha256"],
        "inputs": payload["inputs"],
        "mock_root_is_isolated": payload["mock_root_is_isolated"],
        "seal_chain_extended": False,
        "drift_detected": False,
    }
    with open(_abs(REPORT_JSON_REL), "w", encoding="utf-8") as fh:
        json.dump(json_payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    layer_lines = [
        f"| layer `{k}` | `{v}` |" for k, v in sorted(payload["layer_gates"].items())
    ]
    md_lines = [
        "# C-FM-16 Non-seal Extension Post-Commit Seal Attestation",
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
        f"| frozen drift fp | `{payload['frozen_drift_fp_sha256']}` |",
        f"| frozen boundary fp | `{payload['frozen_boundary_fp_sha256']}` |",
        f"| ready_for_commit | **{str(payload['handoff_packet'].get('ready_for_commit')).lower()}** |",
        f"| ready_for_execute | **false** |",
        f"| hold | `{payload['handoff_packet'].get('hold_recommendation')}` |",
        f"| drift_detected | **false** |",
        "",
        "## Capability",
        "",
        "1. FM-01..05 + FM-12 + FM-13 + FM-14 + FM-15 gate battery（跳过 seal FM06–11）",
        "2. MOCK15 扩展 + MOCK16 漂移 + MOCK17 boundary 零漂移连续性",
        "3. 三层 EXECUTE hold seal：KEEP_EXECUTE_FALSE · AWAITING · idle_not_required",
        "4. 冻结 mock 写隔离（MOCK3–17 拒绝；MOCK18 / ephemeral 放行）",
        "5. Human EXECUTE decision handoff packet",
        "6. protected CSV MOCK18 注册一致性",
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
            f"c_fm_16_nonseal_extension_post_commit_seal_attestation_gate = {payload['gate']}",
            "execute_production_snapshot_rebuild = false",
            "approved_for_snapshot_rebuild = false",
            "cninfo_calls = 0",
            "ready_for_execute = false",
            "hold_recommendation = KEEP_EXECUTE_FALSE",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "idle_not_required_while_awaiting = true",
            "seal_chain_extended = false",
            "drift_detected = false",
            f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
            "```",
            "",
            "## Artifacts",
            "",
            f"- [{payload['matrix_path']}]({os.path.relpath(_abs(payload['matrix_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{matrix_dst_rel}]({os.path.relpath(matrix_dst, os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{REPORT_JSON_REL}]({os.path.basename(REPORT_JSON_REL)})",
            f"- [{payload['handoff_packet_path']}]({os.path.relpath(_abs(payload['handoff_packet_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{payload['seal_packet_path']}]({os.path.relpath(_abs(payload['seal_packet_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            "",
        ]
    )
    with open(_abs(REPORT_MD_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    task_lines = [
        "# C-FM-16 — Non-seal Extension Post-Commit Seal Attestation",
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
        "在 C-FM-15 已 commit 且 EXECUTE 仍 human-held 之上，补齐 **非 seal-chain** 能力："
        "**Cross-FM mock cohort 扩展 post-commit seal attestation**、"
        "**MOCK17 boundary 零漂移**、**MOCK3–17 写隔离**；"
        "产物写入隔离 MOCK18（不覆盖 MOCK3–17；不新增 seal 层）。",
        "",
        "## Capability gain",
        "",
        "1. FM-01..05 + FM-12 + FM-13 + FM-14 + FM-15 gate battery（显式跳过 seal FM06–11）",
        "2. MOCK15 扩展 + MOCK16 漂移 + MOCK17 boundary 指纹连续性锚点与零漂移重算",
        "3. 三层 EXECUTE hold seal（FM13 packet · FM14 drift seal · FM15 boundary packet）",
        "4. Human decision handoff：ready_for_commit ≠ ready_for_execute",
        "5. 冻结写隔离扩展至 MOCK17；本任务 MOCK18 放行",
        "6. protected CSV：MOCK18 注册",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_nonseal_extension_post_commit_seal_attestation.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_nonseal_extension_post_commit_seal_attestation.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_nonseal_extension_post_commit_seal_attestation.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK18 |",
        f"| `{payload['output_root']}/` | 隔离 post-commit attestation 产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* attestation 矩阵 / 指纹 / battery / handoff / seal 包 | 生产 snapshot EXECUTE |",
        "| 只读 FM01–05 / FM12–15 gate JSON / MOCK15–17 产物 / protected CSV | CNINFO live |",
        "| offline QA · nonseal-chain 只读核验（不覆盖 MOCK3–17） | 覆盖 MOCK3–17 |",
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
        f"c_fm_16_nonseal_extension_post_commit_seal_attestation_gate = {payload['gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        "ready_for_execute = false",
        "hold_recommendation = KEEP_EXECUTE_FALSE",
        "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting = true",
        "seal_chain_extended = false",
        "drift_detected = false",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包（non-seal post-commit seal attestation only）",
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
                    "# C-FM-16 mock non-seal extension post-commit seal attestation root",
                    "",
                    f"gate: `{payload['gate']}`",
                    "seal_chain_extended: false",
                    "drift_detected: false",
                    "does_not_overwrite: _mock_c_fm02.._mock_c_fm15 / standard dryrun",
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
            "C-FM-16 non-seal extension post-commit seal attestation QA (offline)"
        )
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        help="隔离 mock 写根（须 validation/_mock_*；不得覆盖 MOCK3–17）",
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

    paths = NonsealPostCommitAttestationPaths(output_root_rel=args.output_root)
    payload = run_nonseal_extension_post_commit_seal_attestation(paths=paths)
    paths_written = write_reports(payload)
    print(f"task_id: {payload['task_id']}")
    print(f"gate: {payload['gate']}")
    for k, v in sorted(payload["layer_gates"].items()):
        print(f"layer_{k}: {v}")
    print(f"fail_count: {payload['fail_count']}")
    print(f"cninfo_calls: {payload['cninfo_calls']}")
    print("execute_production_snapshot_rebuild: false")
    print("seal_chain_extended: false")
    print("drift_detected: false")
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
