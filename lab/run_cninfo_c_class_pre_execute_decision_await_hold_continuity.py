#!/usr/bin/env python3
"""
CNINFO C-class — Pre-EXECUTE decision-await hold continuity runner（离线 · C-FM-11）。

Usage:
    python3 lab/run_cninfo_c_class_pre_execute_decision_await_hold_continuity.py
    python3 lab/run_cninfo_c_class_pre_execute_decision_await_hold_continuity.py \\
      --output-root outputs/validation/_mock_c_fm11_pre_execute_decision_await_hold_continuity
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
from cninfo_c_class_pre_execute_decision_await_hold_continuity import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    TASK_ID,
    DecisionAwaitContinuityPaths,
    run_pre_execute_decision_await_hold_continuity,
)

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_pre_execute_decision_await_hold_continuity"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_decision_await_hold_continuity_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_decision_await_hold_continuity_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/"
    "cninfo_c_class_fm11_pre_execute_decision_await_hold_continuity_20260715.md"
)


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def write_reports(payload: Dict[str, Any]) -> Dict[str, str]:
    os.makedirs(_abs(REPORT_ROOT_REL), exist_ok=True)
    os.makedirs(os.path.dirname(_abs(REPORT_MD_REL)), exist_ok=True)

    matrix_src = _abs(payload["matrix_path"])
    matrix_dst_rel = f"{REPORT_ROOT_REL}/continuity_matrix.csv"
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
        "battery_path": payload["battery_path"],
        "continuity_packet_path": payload["continuity_packet_path"],
        "continuity_packet": payload["continuity_packet"],
        "seal_packet_path": payload["seal_packet_path"],
        "seal_packet": payload["seal_packet"],
        "frozen_wall_fingerprint_sha256": payload[
            "frozen_wall_fingerprint_sha256"
        ],
        "frozen_exclusion_fingerprint_sha256": payload[
            "frozen_exclusion_fingerprint_sha256"
        ],
        "frozen_boundary_fingerprint_sha256": payload[
            "frozen_boundary_fingerprint_sha256"
        ],
        "frozen_attestation_fingerprint_sha256": payload[
            "frozen_attestation_fingerprint_sha256"
        ],
        "frozen_readiness_fingerprint_sha256": payload[
            "frozen_readiness_fingerprint_sha256"
        ],
        "recomputed_readiness_fingerprint": payload[
            "recomputed_readiness_fingerprint"
        ],
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
        "# C-FM-11 Pre-EXECUTE Decision-Await Hold Continuity",
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
        f"| frozen readiness sha | `{payload['frozen_readiness_fingerprint_sha256']}` |",
        f"| recomputed readiness sha | `{payload['recomputed_readiness_fingerprint'].get('fingerprint_sha256', '')}` |",
        f"| drift | **{'no' if not payload['seal_packet'].get('drift_detected') else 'YES'}** |",
        f"| ready_for_commit | **{str(payload['continuity_packet'].get('ready_for_commit')).lower()}** |",
        f"| ready_for_execute | **false** |",
        f"| hold | `{payload['continuity_packet'].get('hold_recommendation')}` |",
        f"| decision_status | `{payload['continuity_packet'].get('decision_status')}` |",
        f"| idle_not_required | **{str(payload['continuity_packet'].get('idle_not_required_while_awaiting')).lower()}** |",
        "",
        "## Capability",
        "",
        "1. FM-01..10 gate battery 只读聚合（含 FM-10 human decision readiness）",
        "2. C-FM-10 MOCK12 冻结产物存在性",
        "3. readiness 指纹零漂移复核（不覆盖 MOCK12）",
        "4. MOCK8–12 seal-chain 连续性",
        "5. decision-await hold seal：KEEP_EXECUTE_FALSE · AWAITING · idle_not_required",
        "6. protected CSV：MOCK3–13 + AUTH1",
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
            f"c_fm_11_pre_execute_decision_await_hold_continuity_gate = {payload['gate']}",
            "execute_production_snapshot_rebuild = false",
            "approved_for_snapshot_rebuild = false",
            "cninfo_calls = 0",
            f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
            "ready_for_execute = false",
            "hold_recommendation = KEEP_EXECUTE_FALSE",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "idle_not_required_while_awaiting = true",
            "```",
            "",
            "## Artifacts",
            "",
            f"- [{payload['matrix_path']}]({os.path.relpath(_abs(payload['matrix_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{matrix_dst_rel}]({os.path.relpath(matrix_dst, os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{REPORT_JSON_REL}]({os.path.basename(REPORT_JSON_REL)})",
            f"- [{payload['seal_packet_path']}]({os.path.relpath(_abs(payload['seal_packet_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            "",
        ]
    )
    with open(_abs(REPORT_MD_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    task_lines = [
        "# C-FM-11 — Pre-EXECUTE Decision-Await Hold Continuity",
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
        "在 C-FM-10 已 commit 且 AWAITING_HUMAN_EXECUTE_DECISION 之上，补齐 "
        "**Pre-EXECUTE decision-await hold continuity / readiness 漂移复核**："
        "FM-01..10 gate battery、MOCK12 冻结产物、readiness 指纹零漂移、"
        "MOCK8–12 seal-chain、decision-await hold seal（不得仅因 awaiting 而 IDLE）；"
        "产物写入隔离 mock cohort（不覆盖 MOCK8–12）。",
        "",
        "## Capability gain",
        "",
        "1. `cninfo_c_class_pre_execute_decision_await_hold_continuity`：六层 continuity matrix",
        "2. FM-01..10 PASS_OFFLINE battery（含 FM-10 readiness ledger gate）",
        "3. 冻结 readiness 指纹锚点复核：MOCK12 SHA256 零漂移",
        "4. seal-chain 连续性：墙/exclusion/boundary/attestation/readiness 跨 MOCK8–12",
        "5. decision-await hold seal：KEEP_EXECUTE_FALSE · AWAITING · idle_not_required",
        "6. protected CSV：MOCK3–13 + AUTH1 注册一致性",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_pre_execute_decision_await_hold_continuity.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_pre_execute_decision_await_hold_continuity.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_pre_execute_decision_await_hold_continuity.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK13 |",
        f"| `{payload['output_root']}/` | 隔离 decision-await continuity 产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* continuity 矩阵 / 指纹 / battery / seal 包 | 生产 snapshot EXECUTE |",
        "| 只读 FM gate JSON / MOCK8–12 seal 链 / protected CSV | CNINFO live |",
        "| offline QA · readiness 指纹重算（不覆盖 MOCK8–12） | 覆盖 MOCK8 / MOCK9 / MOCK10 / MOCK11 / MOCK12 |",
        "| | 覆盖权威 dual-layer 索引 |",
        "| | commit/push（本包未执行） |",
        "| | verified / production_ready 声称 |",
        "| | 翻转 approved_for_snapshot_rebuild |",
        "| | 仅因 AWAITING 而 IDLE |",
        "",
        "## Wall / gate",
        "",
        "```",
        f"c_fm_11_pre_execute_decision_await_hold_continuity_gate = {payload['gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "ready_for_execute = false",
        "hold_recommendation = KEEP_EXECUTE_FALSE",
        "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
        "idle_not_required_while_awaiting = true",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包（decision-await hold continuity only）",
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
                    "# C-FM-11 mock pre-EXECUTE decision-await hold continuity root",
                    "",
                    f"gate: `{payload['gate']}`",
                    "execute_production_snapshot_rebuild: false",
                    "approved_for_snapshot_rebuild: false",
                    "decision_status: AWAITING_HUMAN_EXECUTE_DECISION",
                    "decision_option_a: HOLD_KEEP_EXECUTE_FALSE",
                    "idle_not_required_while_awaiting: true",
                    "does_not_overwrite: _mock_c_fm06.._mock_c_fm10",
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
            "C-FM-11 pre-EXECUTE decision-await hold continuity (offline)"
        )
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        help="隔离 mock 写根（须 validation/_mock_*，不得覆盖 MOCK8–12）",
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

    paths = DecisionAwaitContinuityPaths(output_root_rel=args.output_root)
    payload = run_pre_execute_decision_await_hold_continuity(paths=paths)
    paths_written = write_reports(payload)
    print(f"task_id: {payload['task_id']}")
    print(f"gate: {payload['gate']}")
    for k, v in sorted(payload["layer_gates"].items()):
        print(f"layer_{k}: {v}")
    print(f"fail_count: {payload['fail_count']}")
    print(f"cninfo_calls: {payload['cninfo_calls']}")
    print("execute_production_snapshot_rebuild: false")
    print("approved_for_snapshot_rebuild: false")
    print(f"drift_detected: {payload['seal_packet'].get('drift_detected')}")
    print(
        f"decision_status: {payload['continuity_packet'].get('decision_status')}"
    )
    print(
        "idle_not_required_while_awaiting: "
        f"{payload['continuity_packet'].get('idle_not_required_while_awaiting')}"
    )
    print(f"output_root: {payload['output_root']}")
    print(f"report_md: {paths_written['report_md']}")
    print(
        f"ready_for_commit: "
        f"{'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}"
    )
    return 0 if payload["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
