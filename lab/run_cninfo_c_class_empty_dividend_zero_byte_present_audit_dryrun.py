#!/usr/bin/env python3
"""
CNINFO C-class — Empty-dividend 零字节 present 双层语义审计 dry-run。

对 fuller_market_slice1_200 harvest 只读核验 DLVR-E01–E05；
输出 validation 产物。无 CNINFO · 无 snapshot · 不触碰 harvest ·
execute_production_snapshot_rebuild=false。

Usage:
    python3 lab/run_cninfo_c_class_empty_dividend_zero_byte_present_audit_dryrun.py
    python3 lab/run_cninfo_c_class_empty_dividend_zero_byte_present_audit_dryrun.py \\
      --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200 \\
      --output-root outputs/validation/cninfo_c_class_empty_dividend_zero_byte_present_audit
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_empty_dividend_zero_byte_present_audit import (  # noqa: E402
    AUDIT_ROW_FIELDS,
    EXPECTED_EMPTY_DIVIDEND_CASE_CODE,
    RULE_CHECK_FIELDS,
    run_empty_dividend_zero_byte_present_audit,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    assert_safe_erad_audit_write_path,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    assert_execute_production_snapshot_rebuild_false,
)

DEFAULT_HARVEST_ROOT = (
    "outputs/harvest/cninfo_c_class/fuller_market_slice1_200"
)
DEFAULT_STATUS_CSV = (
    "outputs/harvest/cninfo_c_class/fuller_market_slice1_200/"
    "quality/company_harvest_status.csv"
)
DEFAULT_RESUME_AUDIT_CSV = (
    "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/"
    "reports/c_class_erad_harvest_resume_audit_report.csv"
)
DEFAULT_CAVEAT_LEDGER = (
    "outputs/validation/"
    "cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv"
)
DEFAULT_OFFLINE_MATRIX = (
    "outputs/validation/cninfo_c_class_empty_dividend_offline_matrix_20260714.csv"
)
DEFAULT_DUAL_LAYER_MATRIX = (
    "outputs/validation/cninfo_c_class_dual_layer_rule_matrix_20260714.csv"
)
DEFAULT_OUTPUT_ROOT = (
    "outputs/validation/cninfo_c_class_empty_dividend_zero_byte_present_audit"
)

# 本任务允许读写的路径白名单（只读源 + validation 输出）
ALLOW_LIST = {
    "read": [
        DEFAULT_HARVEST_ROOT,
        DEFAULT_STATUS_CSV,
        DEFAULT_RESUME_AUDIT_CSV,
        DEFAULT_CAVEAT_LEDGER,
        DEFAULT_OFFLINE_MATRIX,
        DEFAULT_DUAL_LAYER_MATRIX,
        "outputs/validation/cninfo_c_class_dual_layer_validation_rules_20260714.md",
        "outputs/validation/cninfo_c_class_empty_dividend_evidence_20260714.md",
    ],
    "write": [
        DEFAULT_OUTPUT_ROOT,
        "outputs/validation/cninfo_c_class_empty_dividend_zero_byte_present_audit_20260715.md",
        "lab/cninfo_c_class_empty_dividend_zero_byte_present_audit.py",
        "lab/run_cninfo_c_class_empty_dividend_zero_byte_present_audit_dryrun.py",
        "lab/test_cninfo_c_class_empty_dividend_zero_byte_present_audit.py",
    ],
    "forbidden": [
        "build_cninfo_c_class_snapshot_batch.py --execute",
        "execute_production_snapshot_rebuild=true",
        "CNINFO live",
        "commit",
        "push",
        "harvest mutation",
    ],
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: str) -> str:
    if not os.path.isabs(path):
        return path.replace("\\", "/")
    return os.path.relpath(path, BASE_DIR).replace("\\", "/")


def write_outputs(
    *,
    output_root_rel: str,
    audit_rows: List[Dict[str, str]],
    rule_rows: List[Dict[str, str]],
    metrics: Dict[str, Any],
) -> Dict[str, str]:
    """写入 validation 产物（仅允许 audit 根）。"""
    assert_safe_erad_audit_write_path(
        os.path.join(BASE_DIR, output_root_rel),
        allowed_audit_root_rel=output_root_rel,
    )
    os.makedirs(os.path.join(BASE_DIR, output_root_rel), exist_ok=True)

    audit_path = os.path.join(
        BASE_DIR, output_root_rel, "empty_dividend_zero_byte_present_audit.csv"
    )
    rule_path = os.path.join(
        BASE_DIR, output_root_rel, "dual_layer_rule_check_matrix.csv"
    )
    meta_path = os.path.join(BASE_DIR, output_root_rel, "run_meta.json")
    summary_path = os.path.join(BASE_DIR, output_root_rel, "evidence_summary.md")
    audit_summary_path = os.path.join(BASE_DIR, output_root_rel, "audit_summary.md")

    for path in (audit_path, rule_path, meta_path, summary_path, audit_summary_path):
        assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=output_root_rel)

    with open(audit_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=AUDIT_ROW_FIELDS)
        writer.writeheader()
        writer.writerows(audit_rows)

    with open(rule_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=RULE_CHECK_FIELDS)
        writer.writeheader()
        writer.writerows(rule_rows)

    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    checks = metrics["checks"]
    check_lines = [
        f"| `{k}` | **{'PASS' if v else 'FAIL'}** |"
        for k, v in checks.items()
    ]
    row_lines = [
        f"| {r['case_id']} | {r['company_code']} | {r['company_name']} | "
        f"{r['ledger_harvest_status']}/{r['ledger_sources_present_existence']} | "
        f"{r['resume_state_csv']}/{r['audit_sources_present_content']} | "
        f"{r['dividend_byte_size']} | {r['rules_all_pass']} |"
        for r in audit_rows
    ]
    rule_pass = sum(1 for r in rule_rows if r["result"] == "PASS")
    rule_fail = sum(1 for r in rule_rows if r["result"] != "PASS")

    body_lines = [
        "# CNINFO C 类 — Empty-Dividend 零字节 Present 双层语义审计",
        "",
        f"_生成时间：{metrics['generated_at']} · offline · CNINFO=0_",
        "",
        "> **validation only** · **no snapshot JSON** · "
        "**execute_production_snapshot_rebuild=false** · "
        "**harvest read-only** · **no live**",
        "",
        "## 任务",
        "",
        f"- task_id: `{metrics['task_id']}`",
        "- 目标：将 DLVR-E01–E05 对 slice1 empty-dividend3 做成机器可核验",
        "- 语义：ledger 文件存在（含 0 字节）计 present；"
        "audit 内容非空才计 present → 合法双层分歧",
        "",
        "## Inputs（read-only）",
        "",
        "| 项 | 路径 |",
        "|----|------|",
        f"| harvest_root | `{metrics['harvest_root']}` |",
        f"| status_csv | `{metrics['status_csv']}` |",
        f"| resume_audit_csv | `{metrics['resume_audit_csv']}` |",
        f"| caveat_ledger | `{metrics['caveat_ledger']}` |",
        f"| offline_matrix | `{metrics['offline_matrix']}` |",
        f"| dual_layer_matrix | `{metrics['dual_layer_matrix']}` |",
        f"| output root | `{output_root_rel}` |",
        "",
        "## Metrics",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| empty3 audited | **{metrics['empty3_audited_count']}/3** |",
        f"| rules_all_pass | **{metrics['rules_all_pass_count']}/3** |",
        f"| rule_checks PASS | **{rule_pass}** |",
        f"| rule_checks FAIL | **{rule_fail}** |",
        f"| disk zero-byte dividend | **{metrics['disk_zero_byte_count']}** |",
        f"| wall_time_ms | **{metrics['wall_time_ms']}** |",
        f"| CNINFO calls | **0** |",
        f"| capability_gain | **{metrics['capability_gain']}** |",
        f"| ready_for_commit | **{metrics['ready_for_commit']}** |",
        "",
        "## Empty-dividend3 rows",
        "",
        "| case_id | code | name | ledger | audit | div_bytes | rules_ok |",
        "|---------|------|------|--------|-------|-----------|----------|",
        *row_lines,
        "",
        "## Checks",
        "",
        "| check | result |",
        "|-------|--------|",
        *check_lines,
        "",
        "## Gate",
        "",
        "```",
        f"c_class_empty_dividend_zero_byte_present_audit_gate = {metrics['gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute",
        "",
        "## Artifacts",
        "",
        f"- [{_rel(audit_path)}]({os.path.basename(audit_path)})",
        f"- [{_rel(rule_path)}]({os.path.basename(rule_path)})",
        f"- [{_rel(meta_path)}]({os.path.basename(meta_path)})",
        f"- [{_rel(summary_path)}]({os.path.basename(summary_path)})",
        f"- [{_rel(audit_summary_path)}]({os.path.basename(audit_summary_path)})",
        "",
        "## Capability note",
        "",
        "DLVR-E01–E05 现可对 fuller_market_slice1_200 harvest 只读机器核验：",
        "确认 3 家零字节 dividend 的 ledger complete / audit needs_review 合法分歧，",
        "并排除未登记的额外零字节文件。",
        "",
        "## Allow-list",
        "",
        "| 类别 | 路径/动作 |",
        "|------|-----------|",
    ]
    for path in ALLOW_LIST["read"]:
        body_lines.append(f"| read | `{path}` |")
    for path in ALLOW_LIST["write"]:
        body_lines.append(f"| write | `{path}` |")
    for path in ALLOW_LIST["forbidden"]:
        body_lines.append(f"| forbidden | `{path}` |")
    body_lines.append("")

    text = "\n".join(body_lines) + "\n"
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(audit_summary_path, "w", encoding="utf-8") as fh:
        fh.write(text)

    artifacts = {
        "empty_dividend_zero_byte_present_audit.csv": _rel(audit_path),
        "dual_layer_rule_check_matrix.csv": _rel(rule_path),
        "run_meta.json": _rel(meta_path),
        "evidence_summary.md": _rel(summary_path),
        "audit_summary.md": _rel(audit_summary_path),
    }

    # 仅在正式 output root 下写 dated 证据索引，避免 mock 测试覆盖正式摘要
    if os.path.normpath(output_root_rel) == os.path.normpath(DEFAULT_OUTPUT_ROOT):
        dated_summary = os.path.join(
            BASE_DIR,
            "outputs/validation/"
            "cninfo_c_class_empty_dividend_zero_byte_present_audit_20260715.md",
        )
        with open(dated_summary, "w", encoding="utf-8") as fh:
            fh.write(text)
        artifacts["dated_evidence_summary.md"] = _rel(dated_summary)

    return artifacts


def run_audit(
    *,
    harvest_root: str,
    status_csv: str,
    resume_audit_csv: str,
    caveat_ledger: str,
    offline_matrix: str,
    dual_layer_matrix: str,
    output_root: str,
    execute_production_snapshot_rebuild: bool = False,
) -> Dict[str, Any]:
    """执行审计并写 validation 产物。"""
    assert_execute_production_snapshot_rebuild_false(
        execute_production_snapshot_rebuild
    )

    t0 = time.perf_counter()
    result = run_empty_dividend_zero_byte_present_audit(
        harvest_root=harvest_root,
        status_csv=status_csv,
        resume_audit_csv=resume_audit_csv,
        caveat_ledger_csv=caveat_ledger,
        offline_matrix_csv=offline_matrix,
        dual_layer_matrix_csv=dual_layer_matrix,
    )
    wall_ms = int((time.perf_counter() - t0) * 1000)

    ok_count = sum(1 for r in result.rows if r["rules_all_pass"] == "yes")
    gate = result.gate
    ready = gate == "PASS_OFFLINE"

    metrics: Dict[str, Any] = {
        "generated_at": _utc_now_iso(),
        "task_id": "C-R16-01",
        "harvest_root": harvest_root,
        "status_csv": status_csv,
        "resume_audit_csv": resume_audit_csv,
        "caveat_ledger": caveat_ledger,
        "offline_matrix": offline_matrix,
        "dual_layer_matrix": dual_layer_matrix,
        "empty3_audited_count": len(EXPECTED_EMPTY_DIVIDEND_CASE_CODE),
        "rules_all_pass_count": ok_count,
        "disk_zero_byte_count": len(result.disk_zero_byte_codes),
        "disk_zero_byte_codes": sorted(result.disk_zero_byte_codes),
        "checks": result.checks,
        "gate": gate,
        "notes": result.notes,
        "wall_time_ms": wall_ms,
        "cninfo_calls": 0,
        "snapshot_json_writes": 0,
        "execute_production_snapshot_rebuild": False,
        "production_roots_mutated": False,
        "harvest_mutated": False,
        "capability_gain": True,
        "ready_for_commit": ready,
        "allow_list": ALLOW_LIST,
    }

    artifacts = write_outputs(
        output_root_rel=output_root,
        audit_rows=result.rows,
        rule_rows=result.rule_rows,
        metrics=metrics,
    )
    metrics["artifacts"] = artifacts
    return metrics


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="C-class empty-dividend zero-byte present dual-layer offline audit"
    )
    parser.add_argument("--harvest-root", default=DEFAULT_HARVEST_ROOT)
    parser.add_argument("--status-csv", default=DEFAULT_STATUS_CSV)
    parser.add_argument("--resume-audit-csv", default=DEFAULT_RESUME_AUDIT_CSV)
    parser.add_argument("--caveat-ledger", default=DEFAULT_CAVEAT_LEDGER)
    parser.add_argument("--offline-matrix", default=DEFAULT_OFFLINE_MATRIX)
    parser.add_argument("--dual-layer-matrix", default=DEFAULT_DUAL_LAYER_MATRIX)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--execute-production-snapshot-rebuild",
        action="store_true",
        default=False,
        help="FORBIDDEN；设置则硬拒绝",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    metrics = run_audit(
        harvest_root=args.harvest_root,
        status_csv=args.status_csv,
        resume_audit_csv=args.resume_audit_csv,
        caveat_ledger=args.caveat_ledger,
        offline_matrix=args.offline_matrix,
        dual_layer_matrix=args.dual_layer_matrix,
        output_root=args.output_root,
        execute_production_snapshot_rebuild=args.execute_production_snapshot_rebuild,
    )
    print(
        json.dumps(
            {
                "gate": metrics["gate"],
                "empty3_audited_count": metrics["empty3_audited_count"],
                "rules_all_pass_count": metrics["rules_all_pass_count"],
                "disk_zero_byte_count": metrics["disk_zero_byte_count"],
                "wall_time_ms": metrics["wall_time_ms"],
                "cninfo_calls": 0,
                "capability_gain": metrics["capability_gain"],
                "ready_for_commit": metrics["ready_for_commit"],
                "execute_production_snapshot_rebuild": False,
                "artifacts": metrics.get("artifacts"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if metrics["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
