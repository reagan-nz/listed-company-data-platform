#!/usr/bin/env python3
"""
CNINFO C-class — Pre-EXECUTE human decision readiness ledger runner（离线 · C-FM-10）。

Usage:
    python3 lab/run_cninfo_c_class_pre_execute_human_decision_readiness_ledger.py
    python3 lab/run_cninfo_c_class_pre_execute_human_decision_readiness_ledger.py \\
      --output-root outputs/validation/_mock_c_fm10_pre_execute_human_decision_readiness_ledger
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
from cninfo_c_class_pre_execute_human_decision_readiness_ledger import (  # noqa: E402
    DEFAULT_MOCK_OUTPUT_ROOT_REL,
    TASK_ID,
    HumanDecisionReadinessPaths,
    run_pre_execute_human_decision_readiness_ledger,
)

REPORT_ROOT_REL = (
    "outputs/validation/cninfo_c_class_pre_execute_human_decision_readiness_ledger"
)
REPORT_MD_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_human_decision_readiness_ledger_20260715.md"
)
REPORT_JSON_REL = (
    "outputs/validation/"
    "cninfo_c_class_pre_execute_human_decision_readiness_ledger_20260715.json"
)
TASK_REPORT_REL = (
    "outputs/validation/"
    "cninfo_c_class_fm10_pre_execute_human_decision_readiness_ledger_20260715.md"
)


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def write_reports(payload: Dict[str, Any]) -> Dict[str, str]:
    os.makedirs(_abs(REPORT_ROOT_REL), exist_ok=True)
    os.makedirs(os.path.dirname(_abs(REPORT_MD_REL)), exist_ok=True)

    matrix_src = _abs(payload["matrix_path"])
    matrix_dst_rel = f"{REPORT_ROOT_REL}/readiness_matrix.csv"
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
        "readiness_packet_path": payload["readiness_packet_path"],
        "readiness_packet": payload["readiness_packet"],
        "checklist_path": payload["checklist_path"],
        "checklist": payload["checklist"],
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
        "# C-FM-10 Pre-EXECUTE Human Decision Readiness Ledger",
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
        f"| frozen wall sha | `{payload['frozen_wall_fingerprint_sha256']}` |",
        f"| frozen attestation sha | `{payload['frozen_attestation_fingerprint_sha256']}` |",
        f"| ready_for_commit | **{str(payload['readiness_packet'].get('ready_for_commit')).lower()}** |",
        f"| ready_for_execute | **false** |",
        f"| hold | `{payload['readiness_packet'].get('hold_recommendation')}` |",
        f"| decision_status | `{payload['readiness_packet'].get('decision_status')}` |",
        f"| option_a | `{payload['readiness_packet'].get('decision_option_a')}` |",
        "",
        "## Capability",
        "",
        "1. FM-01..09 gate battery 只读聚合（含 FM-09 post-commit attestation）",
        "2. MOCK8/9/10/11 seal-chain 连续性 + MOCK11 attestation 零漂移",
        "3. 四层 EXECUTE hold seal：KEEP_EXECUTE_FALSE",
        "4. Human EXECUTE decision readiness ledger + checklist",
        "5. protected CSV：MOCK3–12 + AUTH1",
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
            f"c_fm_10_pre_execute_human_decision_readiness_ledger_gate = {payload['gate']}",
            "execute_production_snapshot_rebuild = false",
            "approved_for_snapshot_rebuild = false",
            "cninfo_calls = 0",
            f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
            "ready_for_execute = false",
            "hold_recommendation = KEEP_EXECUTE_FALSE",
            "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
            "decision_option_a = HOLD_KEEP_EXECUTE_FALSE",
            "```",
            "",
            "## Artifacts",
            "",
            f"- [{payload['matrix_path']}]({os.path.relpath(_abs(payload['matrix_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{matrix_dst_rel}]({os.path.relpath(matrix_dst, os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{REPORT_JSON_REL}]({os.path.basename(REPORT_JSON_REL)})",
            f"- [{payload['readiness_packet_path']}]({os.path.relpath(_abs(payload['readiness_packet_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{payload['checklist_path']}]({os.path.relpath(_abs(payload['checklist_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            f"- [{payload['seal_packet_path']}]({os.path.relpath(_abs(payload['seal_packet_path']), os.path.dirname(_abs(REPORT_MD_REL)))})",
            "",
        ]
    )
    with open(_abs(REPORT_MD_REL), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    task_lines = [
        "# C-FM-10 — Pre-EXECUTE Human Decision Readiness Ledger",
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
        "在 C-FM-09 已 commit 之上，补齐 **Pre-EXECUTE human decision readiness ledger / "
        "FM01–09 锁链**：FM-01..09 gate battery、MOCK8/9/10/11 seal-chain 零漂移、"
        "四层 KEEP_EXECUTE_FALSE、human decision readiness checklist（Option A HOLD "
        "推荐 · Option B APPROVE 仍人批）；产物写入隔离 mock cohort（不覆盖 MOCK8/9/10/11）。",
        "",
        "## Capability gain",
        "",
        "1. `cninfo_c_class_pre_execute_human_decision_readiness_ledger`：五层 readiness matrix",
        "2. FM-01..09 PASS_OFFLINE battery（含 FM-09 post-commit attestation gate）",
        "3. seal-chain 连续性：墙/exclusion/boundary/attestation 指纹跨 MOCK8–11 对齐 · zero-drift",
        "4. 四层 EXECUTE hold seal：KEEP_EXECUTE_FALSE · approved=false",
        "5. human decision readiness：Option A HOLD 推荐 · Option B APPROVE 仍人批 · "
        "AWAITING_HUMAN_EXECUTE_DECISION",
        "6. protected CSV：MOCK3–12 + AUTH1 注册一致性",
        "",
        "## Files",
        "",
        "| 路径 | 变更 |",
        "|------|------|",
        "| `lab/cninfo_c_class_pre_execute_human_decision_readiness_ledger.py` | **新增** 核心 |",
        "| `lab/run_cninfo_c_class_pre_execute_human_decision_readiness_ledger.py` | **新增** runner |",
        "| `lab/test_cninfo_c_class_pre_execute_human_decision_readiness_ledger.py` | **新增** 测试 |",
        "| `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` | C-ROOT-MOCK12 |",
        f"| `{payload['output_root']}/` | 隔离 human decision readiness 产物 |",
        f"| `{REPORT_MD_REL}` | 报告 |",
        f"| `{REPORT_JSON_REL}` | 报告 JSON |",
        "",
        "## Allow-list",
        "",
        "| 允许 | 禁止 |",
        "|------|------|",
        "| validation/_mock_* readiness 矩阵 / 指纹 / battery / checklist / seal 包 | 生产 snapshot EXECUTE |",
        "| 只读 FM gate JSON / MOCK8–11 seal 链 / protected CSV | CNINFO live |",
        "| offline QA · seal-chain 只读核验（不覆盖 MOCK8/9/10/11） | 覆盖 MOCK8 / MOCK9 / MOCK10 / MOCK11 |",
        "| | 覆盖权威 dual-layer 索引 |",
        "| | commit/push（本包未执行） |",
        "| | verified / production_ready 声称 |",
        "| | 翻转 approved_for_snapshot_rebuild |",
        "",
        "## Wall / gate",
        "",
        "```",
        f"c_fm_10_pre_execute_human_decision_readiness_ledger_gate = {payload['gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        f"ready_for_commit = {'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}",
        "ready_for_execute = false",
        "hold_recommendation = KEEP_EXECUTE_FALSE",
        "decision_status = AWAITING_HUMAN_EXECUTE_DECISION",
        "decision_option_a = HOLD_KEEP_EXECUTE_FALSE",
        "```",
        "",
        "## Next",
        "",
        "- Controller 可 commit 本包（human decision readiness ledger only）",
        "- 生产 snapshot EXECUTE 仍 human-gated（本包明确 KEEP_EXECUTE_FALSE）",
        "- Human 可用 checklist + readiness packet 做 EXECUTE 决策（本包不翻转 approved）",
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
                    "# C-FM-10 mock pre-EXECUTE human decision readiness ledger root",
                    "",
                    f"gate: `{payload['gate']}`",
                    "execute_production_snapshot_rebuild: false",
                    "approved_for_snapshot_rebuild: false",
                    "ready_for_execute: false",
                    "decision_status: AWAITING_HUMAN_EXECUTE_DECISION",
                    "decision_option_a: HOLD_KEEP_EXECUTE_FALSE",
                    "does_not_overwrite: _mock_c_fm06_pre_execute_safe_snapshot_wall",
                    "does_not_overwrite: _mock_c_fm07_pre_execute_wall_freeze_drift_recheck",
                    "does_not_overwrite: _mock_c_fm08_pre_execute_controller_commit_boundary",
                    "does_not_overwrite: _mock_c_fm09_pre_execute_post_commit_seal_attestation",
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
            "C-FM-10 pre-EXECUTE human decision readiness ledger (offline)"
        )
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_MOCK_OUTPUT_ROOT_REL,
        help="隔离 mock 写根（须 validation/_mock_*，不得覆盖 MOCK8/9/10/11）",
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

    paths = HumanDecisionReadinessPaths(output_root_rel=args.output_root)
    payload = run_pre_execute_human_decision_readiness_ledger(paths=paths)
    paths_written = write_reports(payload)
    print(f"task_id: {payload['task_id']}")
    print(f"gate: {payload['gate']}")
    for k, v in sorted(payload["layer_gates"].items()):
        print(f"layer_{k}: {v}")
    print(f"fail_count: {payload['fail_count']}")
    print(f"cninfo_calls: {payload['cninfo_calls']}")
    print("execute_production_snapshot_rebuild: false")
    print("approved_for_snapshot_rebuild: false")
    print(
        f"ready_for_commit: "
        f"{'true' if payload['gate'] == 'PASS_OFFLINE' else 'false'}"
    )
    print("ready_for_execute: false")
    print(
        f"hold_recommendation: "
        f"{payload['readiness_packet'].get('hold_recommendation')}"
    )
    print(
        f"decision_status: "
        f"{payload['readiness_packet'].get('decision_status')}"
    )
    print(
        f"decision_option_a: "
        f"{payload['readiness_packet'].get('decision_option_a')}"
    )
    print(f"output_root: {payload['output_root']}")
    print(f"report_md: {paths_written['report_md']}")
    return 0 if payload["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
