#!/usr/bin/env python3
"""
CNINFO C-class — Partial7 双层语义审计 dry-run + QA closure 索引。

对 fuller_market_slice1_200 harvest 只读核验 DLVR-P01–P04；
并将结果写入 QA closure 累积双层证据索引 sibling（不覆盖 empty3 索引、
不改写既有 caveat/metrics）。
无 CNINFO · 无 snapshot · 不触碰 harvest ·
execute_production_snapshot_rebuild=false。

Usage:
    python3 lab/run_cninfo_c_class_partial7_dual_layer_present_audit_dryrun.py
    python3 lab/run_cninfo_c_class_partial7_dual_layer_present_audit_dryrun.py \\
      --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200 \\
      --output-root outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit
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

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    assert_safe_erad_audit_write_path,
)
from cninfo_c_class_partial7_dual_layer_present_audit import (  # noqa: E402
    AUDIT_ROW_FIELDS,
    EXPECTED_PARTIAL7_CASE_CODE,
    QA_CLOSURE_COHORT_COVERAGE_FIELDS,
    QA_CLOSURE_METRIC_FIELDS,
    QA_CLOSURE_PARTIAL7_INDEX_FIELDS,
    RULE_CHECK_FIELDS,
    build_qa_closure_partial7_dual_layer_evidence_index,
    load_csv_rows,
    read_empty3_indexed_pass_count,
    run_partial7_dual_layer_present_audit,
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
    "outputs/validation/cninfo_c_class_partial7_offline_qa_matrix_20260714.csv"
)
DEFAULT_DUAL_LAYER_MATRIX = (
    "outputs/validation/cninfo_c_class_dual_layer_rule_matrix_20260714.csv"
)
DEFAULT_OUTPUT_ROOT = (
    "outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit"
)
DEFAULT_QA_INDEX_ROOT = (
    "outputs/validation/"
    "cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index"
)
DEFAULT_EMPTY3_INDEX_CSV = (
    "outputs/validation/"
    "cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/"
    "qa_closure_dual_layer_evidence_index.csv"
)

TASK_ID = "C-R16-03"

ALLOW_LIST = {
    "read": [
        DEFAULT_HARVEST_ROOT,
        DEFAULT_STATUS_CSV,
        DEFAULT_RESUME_AUDIT_CSV,
        DEFAULT_CAVEAT_LEDGER,
        DEFAULT_OFFLINE_MATRIX,
        DEFAULT_DUAL_LAYER_MATRIX,
        DEFAULT_EMPTY3_INDEX_CSV,
        "outputs/validation/cninfo_c_class_dual_layer_validation_rules_20260714.md",
        "outputs/validation/cninfo_c_class_partial7_evidence_completeness_20260714.md",
        "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_metrics.csv",
        "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_summary.md",
    ],
    "write": [
        DEFAULT_OUTPUT_ROOT,
        DEFAULT_QA_INDEX_ROOT,
        "outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit_20260715.md",
        "outputs/validation/"
        "cninfo_c_class_partial7_dual_layer_qa_closure_index_20260715.md",
        "lab/cninfo_c_class_partial7_dual_layer_present_audit.py",
        "lab/run_cninfo_c_class_partial7_dual_layer_present_audit_dryrun.py",
        "lab/test_cninfo_c_class_partial7_dual_layer_present_audit.py",
    ],
    "forbidden": [
        "overwrite qa_closure_dual_layer_evidence_index.csv (empty3)",
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
    coverage_rows: List[Dict[str, str]],
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
        f"{r['raw_http_error_count']} | {r['delisted']} | "
        f"{r['trading_status']} | {r['is_pt_annotated']} | {r['rules_all_pass']} |"
        for r in audit_rows
    ]
    index_lines = [
        f"| {r['case_id']} | {r['company_code']} | {r['index_status']} | "
        f"{r['rules_all_pass']} | {r['ledger_harvest_status']}/"
        f"{r['audit_resume_state']} | {r['is_pt_annotated']} |"
        for r in index_rows
    ]
    coverage_lines = [
        f"| {r['caveat_family']} | {r['expected_count']} | "
        f"{r['indexed_pass_count']} | {r['index_status']} |"
        for r in coverage_rows
    ]
    rule_pass = sum(1 for r in rule_rows if r["result"] == "PASS")
    rule_fail = sum(1 for r in rule_rows if r["result"] != "PASS")

    body_lines = [
        "# CNINFO C 类 — Partial7 双层审计 + QA Closure 索引",
        "",
        f"_生成时间：{metrics['generated_at']} · offline · CNINFO=0_",
        "",
        "> **validation only** · **no snapshot JSON** · "
        "**execute_production_snapshot_rebuild=false** · "
        "**harvest read-only** · **no live** · "
        "**closed caveat/metrics untouched** · "
        "**empty3 index not overwritten**",
        "",
        "## 任务",
        "",
        f"- task_id: `{metrics['task_id']}`",
        "- 目标：机器核验 DLVR-P01–P04，并将 partial7 接入 QA closure "
        "累积双层证据索引；完成 empty3+partial7 共 10 家 caveat 覆盖",
        "- 语义：ledger/audit 双层均为 partial(4/10)；raw 6×http_error/500；"
        "security_observe delisted=true；PT 标的仅注解 tradingStatus=0",
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
        f"| empty3_index_csv | `{metrics['empty3_index_csv']}` |",
        f"| output root | `{output_root_rel}` |",
        f"| qa_index root | `{qa_index_root_rel}` |",
        "",
        "## Metrics",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| partial7 audited | **{metrics['partial7_audited_count']}/7** |",
        f"| rules_all_pass | **{metrics['rules_all_pass_count']}/7** |",
        f"| rule_checks PASS | **{rule_pass}** |",
        f"| rule_checks FAIL | **{rule_fail}** |",
        f"| pt_annotated | **{metrics['pt_annotated_count']}/2** |",
        f"| indexed_pass | **{metrics['indexed_pass_count']}/7** |",
        f"| empty3_indexed_pass (readonly) | **{metrics['empty3_indexed_pass_count']}/3** |",
        f"| full_caveat_cohort | **{metrics['full_caveat_cohort_indexed']}/10** |",
        f"| index_gate | **{metrics['index_gate']}** |",
        f"| wall_time_ms | **{metrics['wall_time_ms']}** |",
        f"| wall_time_index_ms | **{metrics['wall_time_index_ms']}** |",
        f"| CNINFO calls | **0** |",
        f"| capability_gain | **{metrics['capability_gain']}** |",
        f"| ready_for_commit | **{metrics['ready_for_commit']}** |",
        "",
        "## Partial7 rows",
        "",
        "| case_id | code | name | ledger | audit | http_err | delisted | "
        "trading | pt | rules_ok |",
        "|---------|------|------|--------|-------|----------|----------|"
        "---------|----|----------|",
        *row_lines,
        "",
        "## QA closure dual-layer evidence index (partial7)",
        "",
        "| case_id | code | index_status | rules_ok | ledger/audit | pt |",
        "|---------|------|--------------|----------|--------------|----|",
        *index_lines,
        "",
        "## Cohort coverage（empty3 + partial7）",
        "",
        "| family | expected | indexed_pass | status |",
        "|--------|----------|--------------|--------|",
        *coverage_lines,
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
        f"c_class_partial7_dual_layer_present_audit_gate = {metrics['gate']}",
        f"c_class_qa_closure_dual_layer_partial7_index_gate = {metrics['index_gate']}",
        "execute_production_snapshot_rebuild = false",
        "approved_for_snapshot_rebuild = false",
        "cninfo_calls = 0",
        "original_qa_closure_caveat_ledger_mutated = false",
        "empty3_index_overwritten = false",
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
            "C-R16-03：partial7 DLVR-P01–P04 已机器核验并接入 QA closure 累积证据索引；",
            "empty3 索引保持 sibling 只读；closed caveat_ledger / metrics 未改写；",
            "PT 标的仅注解 tradingStatus=0（不发明 termination sidecar）。",
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
    empty3_index_csv_rel: str,
    audit_rows: List[Dict[str, str]],
    rule_rows: List[Dict[str, str]],
    index_rows: List[Dict[str, str]],
    metric_rows: List[Dict[str, str]],
    coverage_rows: List[Dict[str, str]],
    metrics: Dict[str, Any],
) -> Dict[str, str]:
    """写入 audit 产物 + QA closure partial7 sibling 索引（不覆盖 empty3）。"""
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

    # 硬拒绝覆盖 empty3 主索引文件
    empty3_abs = os.path.join(BASE_DIR, empty3_index_csv_rel)
    empty3_mtime_before = (
        os.path.getmtime(empty3_abs) if os.path.isfile(empty3_abs) else None
    )

    audit_path = os.path.join(
        BASE_DIR, output_root_rel, "partial7_dual_layer_present_audit.csv"
    )
    rule_path = os.path.join(
        BASE_DIR, output_root_rel, "dual_layer_rule_check_matrix.csv"
    )
    index_in_audit = os.path.join(
        BASE_DIR, output_root_rel, "qa_closure_dual_layer_evidence_index_partial7.csv"
    )
    meta_path = os.path.join(BASE_DIR, output_root_rel, "run_meta.json")
    summary_path = os.path.join(BASE_DIR, output_root_rel, "evidence_summary.md")
    audit_summary_path = os.path.join(BASE_DIR, output_root_rel, "audit_summary.md")

    index_path = os.path.join(
        BASE_DIR,
        qa_index_root_rel,
        "qa_closure_dual_layer_evidence_index_partial7.csv",
    )
    metrics_path = os.path.join(
        BASE_DIR, qa_index_root_rel, "qa_closure_dual_layer_partial7_metrics.csv"
    )
    coverage_path = os.path.join(
        BASE_DIR, qa_index_root_rel, "qa_closure_dual_layer_cohort_coverage.csv"
    )
    index_meta_path = os.path.join(
        BASE_DIR, qa_index_root_rel, "partial7_run_meta.json"
    )
    index_summary_path = os.path.join(
        BASE_DIR, qa_index_root_rel, "partial7_evidence_summary.md"
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
        (coverage_path, qa_index_root_rel),
        (index_meta_path, qa_index_root_rel),
        (index_summary_path, qa_index_root_rel),
    ):
        assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=root)

    _write_csv(audit_path, AUDIT_ROW_FIELDS, audit_rows)
    _write_csv(rule_path, RULE_CHECK_FIELDS, rule_rows)
    _write_csv(index_in_audit, QA_CLOSURE_PARTIAL7_INDEX_FIELDS, index_rows)
    _write_csv(index_path, QA_CLOSURE_PARTIAL7_INDEX_FIELDS, index_rows)
    _write_csv(metrics_path, QA_CLOSURE_METRIC_FIELDS, metric_rows)
    _write_csv(coverage_path, QA_CLOSURE_COHORT_COVERAGE_FIELDS, coverage_rows)

    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    with open(index_meta_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    if empty3_mtime_before is not None:
        empty3_mtime_after = os.path.getmtime(empty3_abs)
        if empty3_mtime_after != empty3_mtime_before:
            raise RuntimeError(
                "EMPTY3_INDEX_OVERWRITE_FORBIDDEN: "
                f"{empty3_index_csv_rel} mtime changed during C-R16-03"
            )

    artifact_rels = {
        "partial7_dual_layer_present_audit.csv": _rel(audit_path),
        "dual_layer_rule_check_matrix.csv": _rel(rule_path),
        "qa_closure_dual_layer_evidence_index_partial7.csv": _rel(index_path),
        "qa_closure_dual_layer_partial7_metrics.csv": _rel(metrics_path),
        "qa_closure_dual_layer_cohort_coverage.csv": _rel(coverage_path),
        "audit_run_meta.json": _rel(meta_path),
        "partial7_run_meta.json": _rel(index_meta_path),
        "evidence_summary.md": _rel(summary_path),
        "partial7_evidence_summary.md": _rel(index_summary_path),
    }

    text = _render_summary(
        metrics=metrics,
        audit_rows=audit_rows,
        rule_rows=rule_rows,
        index_rows=index_rows,
        coverage_rows=coverage_rows,
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

    if os.path.normpath(output_root_rel) == os.path.normpath(DEFAULT_OUTPUT_ROOT):
        dated_audit = os.path.join(
            BASE_DIR,
            "outputs/validation/"
            "cninfo_c_class_partial7_dual_layer_present_audit_20260715.md",
        )
        dated_index = os.path.join(
            BASE_DIR,
            "outputs/validation/"
            "cninfo_c_class_partial7_dual_layer_qa_closure_index_20260715.md",
        )
        with open(dated_audit, "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(dated_index, "w", encoding="utf-8") as fh:
            fh.write(text)
        artifact_rels["dated_audit_md"] = _rel(dated_audit)
        artifact_rels["dated_index_md"] = _rel(dated_index)

    return artifact_rels


def run_audit(
    *,
    harvest_root: str = DEFAULT_HARVEST_ROOT,
    status_csv: str = DEFAULT_STATUS_CSV,
    resume_audit_csv: str = DEFAULT_RESUME_AUDIT_CSV,
    caveat_ledger: str = DEFAULT_CAVEAT_LEDGER,
    offline_matrix: str = DEFAULT_OFFLINE_MATRIX,
    dual_layer_matrix: str = DEFAULT_DUAL_LAYER_MATRIX,
    output_root: str = DEFAULT_OUTPUT_ROOT,
    qa_index_root: str = DEFAULT_QA_INDEX_ROOT,
    empty3_index_csv: str = DEFAULT_EMPTY3_INDEX_CSV,
    execute_production_snapshot_rebuild: bool = False,
) -> Dict[str, Any]:
    """执行 partial7 双层审计 + QA closure 索引写入。"""
    assert_execute_production_snapshot_rebuild_false(
        execute_production_snapshot_rebuild
    )

    t0 = time.perf_counter()
    result = run_partial7_dual_layer_present_audit(
        harvest_root=harvest_root,
        status_csv=status_csv,
        resume_audit_csv=resume_audit_csv,
        caveat_ledger_csv=caveat_ledger,
        offline_matrix_csv=offline_matrix,
        dual_layer_matrix_csv=dual_layer_matrix,
    )
    wall_audit_ms = int((time.perf_counter() - t0) * 1000)

    t1 = time.perf_counter()
    empty3_pass = read_empty3_indexed_pass_count(empty3_index_csv)
    audit_csv_ref = (
        f"{output_root.rstrip('/')}/partial7_dual_layer_present_audit.csv"
    )
    rule_matrix_ref = f"{output_root.rstrip('/')}/dual_layer_rule_check_matrix.csv"
    index = build_qa_closure_partial7_dual_layer_evidence_index(
        audit_rows=result.rows,
        rule_rows=result.rule_rows,
        caveat_ledger_rows=load_csv_rows(
            os.path.join(BASE_DIR, caveat_ledger)
            if not os.path.isabs(caveat_ledger)
            else caveat_ledger
        ),
        audit_gate=result.gate,
        audit_csv_ref=audit_csv_ref,
        rule_matrix_ref=rule_matrix_ref,
        empty3_indexed_pass_count=empty3_pass,
        empty3_index_csv_ref=empty3_index_csv,
    )
    wall_index_ms = int((time.perf_counter() - t1) * 1000)

    rules_ok = sum(1 for r in result.rows if r["rules_all_pass"] == "yes")
    indexed_pass = sum(1 for r in index.rows if r["index_status"] == "indexed_pass")
    pt_count = sum(1 for r in result.rows if r["is_pt_annotated"] == "yes")
    full_cohort = empty3_pass + indexed_pass

    ready = (
        result.gate == "PASS_OFFLINE"
        and index.gate == "PASS_OFFLINE"
        and rules_ok == 7
        and indexed_pass == 7
        and empty3_pass == 3
        and full_cohort == 10
    )
    metrics: Dict[str, Any] = {
        "task_id": TASK_ID,
        "generated_at": _utc_now_iso(),
        "harvest_root": harvest_root,
        "status_csv": status_csv,
        "resume_audit_csv": resume_audit_csv,
        "caveat_ledger": caveat_ledger,
        "offline_matrix": offline_matrix,
        "dual_layer_matrix": dual_layer_matrix,
        "empty3_index_csv": empty3_index_csv,
        "output_root": output_root,
        "qa_index_root": qa_index_root,
        "partial7_audited_count": len(result.rows),
        "rules_all_pass_count": rules_ok,
        "pt_annotated_count": pt_count,
        "indexed_pass_count": indexed_pass,
        "empty3_indexed_pass_count": empty3_pass,
        "full_caveat_cohort_indexed": full_cohort,
        "gate": result.gate,
        "index_gate": index.gate,
        "checks": result.checks,
        "index_checks": index.checks,
        "wall_time_ms": wall_audit_ms,
        "wall_time_index_ms": wall_index_ms,
        "cninfo_calls": 0,
        "capability_gain": True,
        "ready_for_commit": ready,
        "original_qa_closure_caveat_ledger_mutated": False,
        "empty3_index_overwritten": False,
        "execute_production_snapshot_rebuild": False,
        "approved_for_snapshot_rebuild": False,
        "expected_case_ids": sorted(EXPECTED_PARTIAL7_CASE_CODE.keys()),
        "audit_notes": result.notes,
        "index_notes": index.notes,
    }

    write_outputs(
        output_root_rel=output_root,
        qa_index_root_rel=qa_index_root,
        empty3_index_csv_rel=empty3_index_csv,
        audit_rows=result.rows,
        rule_rows=result.rule_rows,
        index_rows=index.rows,
        metric_rows=index.metric_rows,
        coverage_rows=index.cohort_coverage_rows,
        metrics=metrics,
    )
    return metrics


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "C-R16-03 partial7 dual-layer present audit + QA closure index "
            "(offline · CNINFO=0)"
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
    parser.add_argument("--empty3-index-csv", default=DEFAULT_EMPTY3_INDEX_CSV)
    parser.add_argument(
        "--execute-production-snapshot-rebuild",
        action="store_true",
        default=False,
        help="禁止标志：设置后硬拒绝",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    metrics = run_audit(
        harvest_root=args.harvest_root,
        status_csv=args.status_csv,
        resume_audit_csv=args.resume_audit_csv,
        caveat_ledger=args.caveat_ledger,
        offline_matrix=args.offline_matrix,
        dual_layer_matrix=args.dual_layer_matrix,
        output_root=args.output_root,
        qa_index_root=args.qa_index_root,
        empty3_index_csv=args.empty3_index_csv,
        execute_production_snapshot_rebuild=args.execute_production_snapshot_rebuild,
    )
    print(f"task_id: {metrics['task_id']}")
    print(f"gate: {metrics['gate']}")
    print(f"index_gate: {metrics['index_gate']}")
    print(
        f"partial7: {metrics['rules_all_pass_count']}/7 "
        f"indexed={metrics['indexed_pass_count']}/7 "
        f"full_cohort={metrics['full_caveat_cohort_indexed']}/10"
    )
    print(f"wall_time_ms: {metrics['wall_time_ms']}")
    print(f"wall_time_index_ms: {metrics['wall_time_index_ms']}")
    print(f"cninfo_calls: {metrics['cninfo_calls']}")
    print(f"capability_gain: {metrics['capability_gain']}")
    print(f"ready_for_commit: {metrics['ready_for_commit']}")
    if metrics["gate"] != "PASS_OFFLINE" or metrics["index_gate"] != "PASS_OFFLINE":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
