#!/usr/bin/env python3
"""
CNINFO C-class — Partial7 × Wave1 filtered_universe 离线 QA 审计 dry-run。

消费 Wave 1 `filtered_universe_included.yaml`，对照 caveat ledger ·
exclusion reconcile · offline QA matrix，硬化 partial7 原因对账证据。

无 CNINFO · 无 snapshot · 不触碰 harvest ·
execute_production_snapshot_rebuild=false。

Usage:
    python3 lab/run_cninfo_c_class_partial7_filtered_universe_qa_audit_dryrun.py
    python3 lab/run_cninfo_c_class_partial7_filtered_universe_qa_audit_dryrun.py \\
      --filtered-universe outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml \\
      --output-root outputs/validation/cninfo_c_class_erad_partial7_filtered_universe_qa_audit/
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    assert_safe_erad_audit_write_path,
)
from cninfo_c_class_partial7_filtered_universe_qa_audit import (  # noqa: E402
    AUDIT_ROW_FIELDS,
    EXPECTED_PARTIAL7_CASE_CODE,
    build_hardened_qa_matrix_rows,
    hardened_qa_matrix_fieldnames,
    load_csv_rows,
    run_partial7_filtered_universe_audit,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    assert_execute_production_snapshot_rebuild_false,
)

DEFAULT_FILTERED_UNIVERSE = (
    "outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/"
    "filtered_universe_included.yaml"
)
DEFAULT_CAVEAT_LEDGER = (
    "outputs/validation/"
    "cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv"
)
DEFAULT_EXCLUSION_RECONCILE = (
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv"
)
DEFAULT_QA_MATRIX = (
    "outputs/validation/cninfo_c_class_partial7_offline_qa_matrix_20260714.csv"
)
DEFAULT_OUTPUT_ROOT = (
    "outputs/validation/cninfo_c_class_erad_partial7_filtered_universe_qa_audit"
)


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
    hardened_rows: List[Dict[str, str]],
    hardened_fields: List[str],
    metrics: Dict[str, Any],
) -> Dict[str, str]:
    """写入 validation 产物（仅允许 audit 根）。"""
    assert_safe_erad_audit_write_path(
        os.path.join(BASE_DIR, output_root_rel),
        allowed_audit_root_rel=output_root_rel,
    )
    os.makedirs(os.path.join(BASE_DIR, output_root_rel), exist_ok=True)

    reconcile_path = os.path.join(
        BASE_DIR, output_root_rel, "partial7_reason_reconcile.csv"
    )
    matrix_path = os.path.join(
        BASE_DIR, output_root_rel, "partial7_offline_qa_matrix_hardened.csv"
    )
    meta_path = os.path.join(BASE_DIR, output_root_rel, "run_meta.json")
    summary_path = os.path.join(BASE_DIR, output_root_rel, "audit_summary.md")

    for path in (reconcile_path, matrix_path, meta_path, summary_path):
        assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=output_root_rel)

    with open(reconcile_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=AUDIT_ROW_FIELDS)
        writer.writeheader()
        writer.writerows(audit_rows)

    with open(matrix_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=hardened_fields)
        writer.writeheader()
        writer.writerows(hardened_rows)

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
        f"{r['in_filtered_included']} | {r['ledger_caveat_class']} | "
        f"{r['reason_reconcile_ok']} |"
        for r in audit_rows
    ]
    lines = [
        "# CNINFO C 类 — Partial7 × Wave1 Filtered Universe QA 审计",
        "",
        f"_生成时间：{metrics['generated_at']} · offline · CNINFO=0_",
        "",
        "> **validation only** · **no snapshot JSON** · "
        "**execute_production_snapshot_rebuild=false** · "
        "**harvest untouched** · **no live**",
        "",
        "## Inputs（read-only）",
        "",
        "| 项 | 路径 |",
        "|----|------|",
        f"| filtered_universe | `{metrics['filtered_universe']}` |",
        f"| caveat_ledger | `{metrics['caveat_ledger']}` |",
        f"| exclusion_reconcile | `{metrics['exclusion_reconcile']}` |",
        f"| offline_qa_matrix | `{metrics['offline_qa_matrix']}` |",
        f"| output root | `{output_root_rel}` |",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| filtered included | **{metrics['filtered_company_count']}** |",
        f"| partial7 audited | **{metrics['partial7_audited_count']}/7** |",
        f"| reason_reconcile_ok | **{metrics['reason_reconcile_ok_count']}/7** |",
        f"| leaked into filtered | **{metrics['leaked_into_filtered_count']}** |",
        "",
        "## Partial7 rows",
        "",
        "| case_id | code | name | in_filtered | caveat_class | reason_ok |",
        "|---------|------|------|-------------|--------------|-----------|",
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
        f"c_class_erad_partial7_filtered_universe_qa_audit_gate = {metrics['gate']}",
        "execute_production_snapshot_rebuild = false",
        "cninfo_calls = 0",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute",
        "",
        "## Artifacts",
        "",
        f"- [{_rel(reconcile_path)}]({os.path.basename(reconcile_path)})",
        f"- [{_rel(matrix_path)}]({os.path.basename(matrix_path)})",
        f"- [{_rel(meta_path)}]({os.path.basename(meta_path)})",
        f"- [{_rel(summary_path)}]({os.path.basename(summary_path)})",
        "",
        "## Capability note",
        "",
        "Wave 1 `filtered_universe_included.yaml` 现可被本离线审计消费：",
        "验证 partial7 不泄漏进 included 池，并对齐 caveat ledger / reconcile / QA matrix 原因字段。",
        "",
    ]
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
        fh.write("\n")

    return {
        "partial7_reason_reconcile.csv": _rel(reconcile_path),
        "partial7_offline_qa_matrix_hardened.csv": _rel(matrix_path),
        "run_meta.json": _rel(meta_path),
        "audit_summary.md": _rel(summary_path),
    }


def run_audit(
    *,
    filtered_universe: str,
    caveat_ledger: str,
    exclusion_reconcile: str,
    offline_qa_matrix: str,
    output_root: str,
    execute_production_snapshot_rebuild: bool = False,
) -> Dict[str, Any]:
    """执行审计并写 validation 产物。"""
    assert_execute_production_snapshot_rebuild_false(
        execute_production_snapshot_rebuild
    )

    result = run_partial7_filtered_universe_audit(
        filtered_universe_yaml=filtered_universe,
        caveat_ledger_csv=caveat_ledger,
        exclusion_reconcile_csv=exclusion_reconcile,
        offline_qa_matrix_csv=offline_qa_matrix,
    )
    qa_rows = load_csv_rows(
        offline_qa_matrix
        if os.path.isabs(offline_qa_matrix)
        else os.path.join(BASE_DIR, offline_qa_matrix)
    )
    hardened_rows = build_hardened_qa_matrix_rows(result.rows, qa_rows)
    hardened_fields = hardened_qa_matrix_fieldnames(hardened_rows)

    ok_count = sum(1 for r in result.rows if r["reason_reconcile_ok"] == "yes")
    leaked_count = sum(1 for r in result.rows if r["in_filtered_included"] == "yes")

    metrics: Dict[str, Any] = {
        "generated_at": _utc_now_iso(),
        "filtered_universe": filtered_universe,
        "caveat_ledger": caveat_ledger,
        "exclusion_reconcile": exclusion_reconcile,
        "offline_qa_matrix": offline_qa_matrix,
        "filtered_company_count": result.filtered_company_count,
        "partial7_audited_count": len(EXPECTED_PARTIAL7_CASE_CODE),
        "reason_reconcile_ok_count": ok_count,
        "leaked_into_filtered_count": leaked_count,
        "checks": result.checks,
        "gate": result.gate,
        "notes": result.notes,
        "cninfo_calls": 0,
        "snapshot_json_writes": 0,
        "execute_production_snapshot_rebuild": False,
        "production_roots_mutated": False,
        "harvest_mutated": False,
    }

    artifacts = write_outputs(
        output_root_rel=output_root,
        audit_rows=result.rows,
        hardened_rows=hardened_rows,
        hardened_fields=hardened_fields,
        metrics=metrics,
    )
    metrics["artifacts"] = artifacts
    return metrics


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="C-class partial7 × Wave1 filtered_universe offline QA audit"
    )
    parser.add_argument(
        "--filtered-universe",
        default=DEFAULT_FILTERED_UNIVERSE,
        help="Wave 1 filtered_universe_included.yaml",
    )
    parser.add_argument(
        "--caveat-ledger",
        default=DEFAULT_CAVEAT_LEDGER,
        help="slice1 QA closure caveat ledger CSV",
    )
    parser.add_argument(
        "--exclusion-reconcile",
        default=DEFAULT_EXCLUSION_RECONCILE,
        help="Run 11 exclusion_reconcile.csv",
    )
    parser.add_argument(
        "--offline-qa-matrix",
        default=DEFAULT_QA_MATRIX,
        help="partial7 offline QA matrix CSV",
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT,
        help="validation output root",
    )
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
        filtered_universe=args.filtered_universe,
        caveat_ledger=args.caveat_ledger,
        exclusion_reconcile=args.exclusion_reconcile,
        offline_qa_matrix=args.offline_qa_matrix,
        output_root=args.output_root,
        execute_production_snapshot_rebuild=args.execute_production_snapshot_rebuild,
    )
    print(
        json.dumps(
            {
                "gate": metrics["gate"],
                "filtered_company_count": metrics["filtered_company_count"],
                "reason_reconcile_ok_count": metrics["reason_reconcile_ok_count"],
                "leaked_into_filtered_count": metrics["leaked_into_filtered_count"],
                "cninfo_calls": 0,
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
