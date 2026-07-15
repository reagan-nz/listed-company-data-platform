#!/usr/bin/env python3
"""
CNINFO C-class — Empty-dividend 零字节 present 双层语义审计 dry-run + QA closure 索引。

对 fuller_market_slice1_200 harvest 只读核验 DLVR-E01–E05；
并将结果写入 QA closure 累积双层证据索引（不改写既有 caveat/metrics）。
无 CNINFO · 无 snapshot · 不触碰 harvest ·
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
    QA_CLOSURE_INDEX_FIELDS,
    QA_CLOSURE_METRIC_FIELDS,
    RULE_CHECK_FIELDS,
    build_qa_closure_dual_layer_evidence_index,
    load_csv_rows,
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
# QA closure 累积索引包（sibling；不改写 closed caveat/metrics）
DEFAULT_QA_INDEX_ROOT = (
    "outputs/validation/"
    "cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index"
)

TASK_ID = "C-R16-02"

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
        "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_metrics.csv",
        "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_summary.md",
    ],
    "write": [
        DEFAULT_OUTPUT_ROOT,
        DEFAULT_QA_INDEX_ROOT,
        "outputs/validation/cninfo_c_class_empty_dividend_zero_byte_present_audit_20260715.md",
        "outputs/validation/"
        "cninfo_c_class_empty_dividend_zero_byte_qa_closure_index_20260715.md",
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
        "mutate qa_closure_caveat_ledger.csv",
        "mutate qa_closure_metrics.csv",
    ],
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: str) -> str:
    if not os.path.isabs(path):
        return path.replace("\\", "/")
    return os.path.relpath(path, BASE_DIR).replace("\\", "/")


def _write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _render_summary(
    *,
    metrics: Dict[str, Any],
    audit_rows: List[Dict[str, str]],
    rule_rows: List[Dict[str, str]],
    index_rows: List[Dict[str, str]],
    output_root_rel: str,
    qa_index_root_rel: str,
    artifact_rels: Dict[str, str],
) -> str:
    checks = metrics["checks"]
    index_checks = metrics["index_checks"]
    check_lines = [
        f"| `{k}` | **{'PASS' if v else 'FAIL'}** |" for k, v in checks.items()
    ]
    index_check_lines = [
        f"| `{k}` | **{'PASS' if v else 'FAIL'}** |" for k, v in index_checks.items()
    ]
    row_lines = [
        f"| {r['case_id']} | {r['company_code']} | {r['company_name']} | "
        f"{r['ledger_harvest_status']}/{r['ledger_sources_present_existence']} | "
        f"{r['resume_state_csv']}/{r['audit_sources_present_content']} | "
        f"{r['dividend_byte_size']} | {r['rules_all_pass']} |"
        for r in audit_rows
    ]
    index_lines = [
        f"| {r['case_id']} | {r['company_code']} | {r['index_status']} | "
        f"{r['rules_all_pass']} | {r['dividend_byte_size']} | "
        f"{r['ledger_dividend_present']}/{r['audit_dividend_present']} |"
        for r in index_rows
    ]
    rule_pass = sum(1 for r in rule_rows if r["result"] == "PASS")
    rule_fail = sum(1 for r in rule_rows if r["result"] != "PASS")

    body_lines = [
        "# CNINFO C 类 — Empty-Dividend 零字节 Present 双层审计 + QA Closure 索引",
        "",
        f"_生成时间：{metrics['generated_at']} · offline · CNINFO=0_",
        "",
        "> **validation only** · **no snapshot JSON** · "
        "**execute_production_snapshot_rebuild=false** · "
        "**harvest read-only** · **no live** · "
        "**closed caveat/metrics untouched**",
        "",
        "## 任务",
        "",
        f"- task_id: `{metrics['task_id']}`",
        "- 目标：将 C-R16-01 双层审计结果接入 QA closure 累积证据索引，"
        "并硬化 content-empty / CLI execute 边缘",
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
        f"| qa_index root | `{qa_index_root_rel}` |",
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
        f"| indexed_pass | **{metrics['indexed_pass_count']}/3** |",
        f"| index_gate | **{metrics['index_gate']}** |",
        f"| wall_time_ms | **{metrics['wall_time_ms']}** |",
        f"| wall_time_index_ms | **{metrics['wall_time_index_ms']}** |",
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
        "## QA closure dual-layer evidence index",
        "",
        "| case_id | code | index_status | rules_ok | div_bytes | ledger/audit div |",
        "|---------|------|--------------|----------|-----------|------------------|",
        *index_lines,
        "",
        "## Checks（present audit）",
        "",
        "| check | result |",
        "|-------|--------|",
        *check_lines,
        "",
        "## Checks（QA closure index）",
        "",
        "| check | result |",
        "|-------|--------|",
        *index_check_lines,
        "",
        "## Gate",
        "",
        "```",
        f"c_class_empty_dividend_zero_byte_present_audit_gate = {metrics['gate']}",
        f"c_class_qa_closure_dual_layer_index_gate = {metrics['index_gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        "original_qa_closure_caveat_ledger_mutated = false",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute",
        "",
        "## Artifacts",
        "",
    ]
    for key, rel in artifact_rels.items():
        body_lines.append(f"- `{key}`: [{rel}]({os.path.basename(rel)})")
    body_lines.extend(
        [
            "",
            "## Capability note",
            "",
            "C-R16-02：empty-dividend 双层审计结果已接入 QA closure 累积证据索引；",
            "closed caveat_ledger / metrics 保持未改写；content-empty 与零字节 cohort 对齐核验。",
            "",
            "## Allow-list",
            "",
            "| 类别 | 路径/动作 |",
            "|------|-----------|",
        ]
    )
    for path in ALLOW_LIST["read"]:
        body_lines.append(f"| read | `{path}` |")
    for path in ALLOW_LIST["write"]:
        body_lines.append(f"| write | `{path}` |")
    for path in ALLOW_LIST["forbidden"]:
        body_lines.append(f"| forbidden | `{path}` |")
    body_lines.append("")
    return "\n".join(body_lines) + "\n"


def write_outputs(
    *,
    output_root_rel: str,
    qa_index_root_rel: str,
    audit_rows: List[Dict[str, str]],
    rule_rows: List[Dict[str, str]],
    index_rows: List[Dict[str, str]],
    metric_rows: List[Dict[str, str]],
    metrics: Dict[str, Any],
) -> Dict[str, str]:
    """写入 audit 产物 + QA closure 累积索引包。"""
    assert_safe_erad_audit_write_path(
        os.path.join(BASE_DIR, output_root_rel),
        allowed_audit_root_rel=output_root_rel,
    )
    assert_safe_erad_audit_write_path(
        os.path.join(BASE_DIR, qa_index_root_rel),
        allowed_audit_root_rel=qa_index_root_rel,
    )
    os.makedirs(os.path.join(BASE_DIR, output_root_rel), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, qa_index_root_rel), exist_ok=True)

    audit_path = os.path.join(
        BASE_DIR, output_root_rel, "empty_dividend_zero_byte_present_audit.csv"
    )
    rule_path = os.path.join(
        BASE_DIR, output_root_rel, "dual_layer_rule_check_matrix.csv"
    )
    index_in_audit = os.path.join(
        BASE_DIR, output_root_rel, "qa_closure_dual_layer_evidence_index.csv"
    )
    meta_path = os.path.join(BASE_DIR, output_root_rel, "run_meta.json")
    summary_path = os.path.join(BASE_DIR, output_root_rel, "evidence_summary.md")
    audit_summary_path = os.path.join(BASE_DIR, output_root_rel, "audit_summary.md")

    index_path = os.path.join(
        BASE_DIR, qa_index_root_rel, "qa_closure_dual_layer_evidence_index.csv"
    )
    metrics_path = os.path.join(
        BASE_DIR, qa_index_root_rel, "qa_closure_dual_layer_metrics.csv"
    )
    index_meta_path = os.path.join(BASE_DIR, qa_index_root_rel, "run_meta.json")
    index_summary_path = os.path.join(
        BASE_DIR, qa_index_root_rel, "evidence_summary.md"
    )

    for path, root in (
        (audit_path, output_root_rel),
        (rule_path, output_root_rel),
        (index_in_audit, output_root_rel),
        (meta_path, output_root_rel),
        (summary_path, output_root_rel),
        (audit_summary_path, output_root_rel),
        (index_path, qa_index_root_rel),
        (metrics_path, qa_index_root_rel),
        (index_meta_path, qa_index_root_rel),
        (index_summary_path, qa_index_root_rel),
    ):
        assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=root)

    _write_csv(audit_path, AUDIT_ROW_FIELDS, audit_rows)
    _write_csv(rule_path, RULE_CHECK_FIELDS, rule_rows)
    _write_csv(index_in_audit, QA_CLOSURE_INDEX_FIELDS, index_rows)
    _write_csv(index_path, QA_CLOSURE_INDEX_FIELDS, index_rows)
    _write_csv(metrics_path, QA_CLOSURE_METRIC_FIELDS, metric_rows)

    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(index_meta_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    artifact_rels = {
        "empty_dividend_zero_byte_present_audit.csv": _rel(audit_path),
        "dual_layer_rule_check_matrix.csv": _rel(rule_path),
        "qa_closure_dual_layer_evidence_index.csv": _rel(index_path),
        "qa_closure_dual_layer_metrics.csv": _rel(metrics_path),
        "audit_run_meta.json": _rel(meta_path),
        "index_run_meta.json": _rel(index_meta_path),
        "evidence_summary.md": _rel(summary_path),
        "index_evidence_summary.md": _rel(index_summary_path),
    }

    text = _render_summary(
        metrics=metrics,
        audit_rows=audit_rows,
        rule_rows=rule_rows,
        index_rows=index_rows,
        output_root_rel=output_root_rel,
        qa_index_root_rel=qa_index_root_rel,
        artifact_rels=artifact_rels,
    )
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(audit_summary_path, "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(index_summary_path, "w", encoding="utf-8") as fh:
        fh.write(text)

    # 正式根下写 dated 证据索引
    if os.path.normpath(output_root_rel) == os.path.normpath(DEFAULT_OUTPUT_ROOT):
        dated_audit = os.path.join(
            BASE_DIR,
            "outputs/validation/"
            "cninfo_c_class_empty_dividend_zero_byte_present_audit_20260715.md",
        )
        dated_index = os.path.join(
            BASE_DIR,
            "outputs/validation/"
            "cninfo_c_class_empty_dividend_zero_byte_qa_closure_index_20260715.md",
        )
        with open(dated_audit, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(dated_index, "w", encoding="utf-8") as fh:
            fh.write(text)
        artifact_rels["dated_audit_evidence.md"] = _rel(dated_audit)
        artifact_rels["dated_index_evidence.md"] = _rel(dated_index)

    return artifact_rels


def run_audit(
    *,
    harvest_root: str,
    status_csv: str,
    resume_audit_csv: str,
    caveat_ledger: str,
    offline_matrix: str,
    dual_layer_matrix: str,
    output_root: str,
    qa_index_root: str = DEFAULT_QA_INDEX_ROOT,
    execute_production_snapshot_rebuild: bool = False,
) -> Dict[str, Any]:
    """执行审计 + QA closure 索引并写 validation 产物。"""
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
    wall_audit_ms = int((time.perf_counter() - t0) * 1000)

    audit_csv_ref = (
        f"{output_root}/empty_dividend_zero_byte_present_audit.csv"
    ).replace("\\", "/")
    rule_ref = f"{output_root}/dual_layer_rule_check_matrix.csv".replace("\\", "/")

    t1 = time.perf_counter()
    caveat_abs = (
        caveat_ledger
        if os.path.isabs(caveat_ledger)
        else os.path.join(BASE_DIR, caveat_ledger)
    )
    index_result = build_qa_closure_dual_layer_evidence_index(
        audit_rows=result.rows,
        rule_rows=result.rule_rows,
        caveat_ledger_rows=load_csv_rows(caveat_abs),
        audit_gate=result.gate,
        audit_csv_ref=audit_csv_ref,
        rule_matrix_ref=rule_ref,
    )
    wall_index_ms = int((time.perf_counter() - t1) * 1000)
    wall_ms = wall_audit_ms + wall_index_ms

    ok_count = sum(1 for r in result.rows if r["rules_all_pass"] == "yes")
    indexed_pass = sum(
        1 for r in index_result.rows if r["index_status"] == "indexed_pass"
    )
    gate = result.gate
    index_gate = index_result.gate
    ready = gate == "PASS_OFFLINE" and index_gate == "PASS_OFFLINE"

    metrics: Dict[str, Any] = {
        "generated_at": _utc_now_iso(),
        "task_id": TASK_ID,
        "harvest_root": harvest_root,
        "status_csv": status_csv,
        "resume_audit_csv": resume_audit_csv,
        "caveat_ledger": caveat_ledger,
        "offline_matrix": offline_matrix,
        "dual_layer_matrix": dual_layer_matrix,
        "output_root": output_root,
        "qa_index_root": qa_index_root,
        "empty3_audited_count": len(EXPECTED_EMPTY_DIVIDEND_CASE_CODE),
        "rules_all_pass_count": ok_count,
        "disk_zero_byte_count": len(result.disk_zero_byte_codes),
        "disk_zero_byte_codes": sorted(result.disk_zero_byte_codes),
        "indexed_pass_count": indexed_pass,
        "checks": result.checks,
        "index_checks": index_result.checks,
        "gate": gate,
        "index_gate": index_gate,
        "notes": result.notes,
        "index_notes": index_result.notes,
        "wall_time_ms": wall_ms,
        "wall_time_audit_ms": wall_audit_ms,
        "wall_time_index_ms": wall_index_ms,
        "cninfo_calls": 0,
        "snapshot_json_writes": 0,
        "execute_production_snapshot_rebuild": False,
        "production_roots_mutated": False,
        "harvest_mutated": False,
        "original_qa_closure_caveat_ledger_mutated": False,
        "original_qa_closure_metrics_mutated": False,
        "capability_gain": True,
        "ready_for_commit": ready,
        "allow_list": ALLOW_LIST,
    }

    artifacts = write_outputs(
        output_root_rel=output_root,
        qa_index_root_rel=qa_index_root,
        audit_rows=result.rows,
        rule_rows=result.rule_rows,
        index_rows=index_result.rows,
        metric_rows=index_result.metric_rows,
        metrics=metrics,
    )
    metrics["artifacts"] = artifacts
    return metrics


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "C-class empty-dividend zero-byte present dual-layer offline audit "
            "+ QA closure evidence index"
        )
    )
    parser.add_argument("--harvest-root", default=DEFAULT_HARVEST_ROOT)
    parser.add_argument("--status-csv", default=DEFAULT_STATUS_CSV)
    parser.add_argument("--resume-audit-csv", default=DEFAULT_RESUME_AUDIT_CSV)
    parser.add_argument("--caveat-ledger", default=DEFAULT_CAVEAT_LEDGER)
    parser.add_argument("--offline-matrix", default=DEFAULT_OFFLINE_MATRIX)
    parser.add_argument("--dual-layer-matrix", default=DEFAULT_DUAL_LAYER_MATRIX)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--qa-index-root", default=DEFAULT_QA_INDEX_ROOT)
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
        qa_index_root=args.qa_index_root,
        execute_production_snapshot_rebuild=args.execute_production_snapshot_rebuild,
    )
    print(
        json.dumps(
            {
                "task_id": metrics["task_id"],
                "gate": metrics["gate"],
                "index_gate": metrics["index_gate"],
                "empty3_audited_count": metrics["empty3_audited_count"],
                "rules_all_pass_count": metrics["rules_all_pass_count"],
                "indexed_pass_count": metrics["indexed_pass_count"],
                "disk_zero_byte_count": metrics["disk_zero_byte_count"],
                "wall_time_ms": metrics["wall_time_ms"],
                "wall_time_audit_ms": metrics["wall_time_audit_ms"],
                "wall_time_index_ms": metrics["wall_time_index_ms"],
                "cninfo_calls": 0,
                "capability_gain": metrics["capability_gain"],
                "ready_for_commit": metrics["ready_for_commit"],
                "execute_production_snapshot_rebuild": False,
                "original_qa_closure_caveat_ledger_mutated": False,
                "artifacts": metrics.get("artifacts"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    ok = (
        metrics["gate"] == "PASS_OFFLINE"
        and metrics["index_gate"] == "PASS_OFFLINE"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
