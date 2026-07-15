#!/usr/bin/env python3
"""
CNINFO C-class — Snapshot exclusion preparation adapter dry-run（离线）。

将 Run 11 exclusion_reconcile.csv（或 exclusion manifest）接入 preparation 过滤，
产出 filtered universe · builder command-draft · 对账摘要。

**不**调用 build_snapshot · **不**写生产 snapshot · **不**设置
execute_production_snapshot_rebuild · **不**触碰 863/phase3/phase35 生产根。

本适配器刻意不修改 build_cninfo_c_class_snapshot_batch.py 的 execute 路径；
仅生成带 --exclusion-csv 的 dry-run 命令草案，供后续人批接线。

Usage:
    python3 lab/run_cninfo_c_class_snapshot_exclusion_prep_adapter_dryrun.py
    python3 lab/run_cninfo_c_class_snapshot_exclusion_prep_adapter_dryrun.py \\
      --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml \\
      --exclusion-csv outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv \\
      --output-root outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import yaml  # noqa: E402

from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    assert_safe_erad_audit_write_path,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    ExclusionFilterResult,
    assert_execute_production_snapshot_rebuild_false,
    filter_universe_with_exclusion_csv,
    refuse_exclusion_with_execute,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
    load_universe,
)

DEFAULT_UNIVERSE_YAML = "lab/eval_companies_c_class_fuller_market_slice1_200.yaml"
DEFAULT_EXCLUSION_CSV = (
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv"
)
DEFAULT_OUTPUT_ROOT = (
    "outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter"
)
DEFAULT_MOCK_OUTPUT_ROOT = (
    "outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_slice1_200_dryrun/"
)
DEFAULT_HARVEST_ROOT = "outputs/harvest/cninfo_c_class/fuller_market_slice1_200/"

FILTER_REPORT_FIELDS = [
    "company_code",
    "company_name",
    "case_id",
    "board",
    "pool_role",
    "exclusion_hit",
    "notes",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: str) -> str:
    if not os.path.isabs(path):
        return path.replace("\\", "/")
    return os.path.relpath(path, BASE_DIR).replace("\\", "/")


def build_filter_report_rows(
    companies: Sequence[Dict[str, str]],
    result: ExclusionFilterResult,
) -> List[Dict[str, str]]:
    excluded_set = set(result.excluded_codes)
    rows: List[Dict[str, str]] = []
    for company in companies:
        code = company["company_code"]
        hit = code in excluded_set
        rows.append({
            "company_code": code,
            "company_name": company.get("company_name") or "",
            "case_id": company.get("case_id") or "",
            "board": company.get("board") or "",
            "pool_role": "excluded" if hit else "included_complete_pool_candidate",
            "exclusion_hit": "yes" if hit else "no",
            "notes": (
                f"csv_kind={result.csv_kind}"
                if hit
                else "eligible_for_prep_dryrun"
            ),
        })
    return rows


def write_filtered_universe_yaml(
    included: Sequence[Dict[str, str]],
    path: str,
    *,
    source_universe: str,
    exclusion_csv: str,
) -> None:
    payload = {
        "meta": {
            "generated_at": _utc_now_iso(),
            "purpose": "c_class_snapshot_exclusion_prep_adapter_filtered_universe",
            "source_universe": source_universe,
            "exclusion_csv": exclusion_csv,
            "company_count": len(included),
            "execute_production_snapshot_rebuild": False,
            "note": "validation/prep only · not production snapshot universe",
        },
        "companies": [
            {
                "stock_code": c["company_code"],
                "company_code": c["company_code"],
                "company_name": c.get("company_name") or "",
                "case_id": c.get("case_id") or "",
                "board": c.get("board") or "",
            }
            for c in included
        ],
    }
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(payload, fh, allow_unicode=True, sort_keys=False)


def build_command_draft(
    *,
    universe_yaml: str,
    filtered_universe_rel: str,
    exclusion_csv: str,
    harvest_root: str,
    mock_output_root: str,
) -> str:
    """生成带 --exclusion-csv 的 batch builder dry-run 命令草案（注释态 · 不执行）。"""
    lines = [
        "# CNINFO C-class — Snapshot exclusion prep · builder command draft",
        "# PLAN ONLY · DO NOT RUN against production snapshot roots",
        "# execute_production_snapshot_rebuild = false",
        "# execute mode FORBIDDEN · exclusion-csv 仅 preparation dry-run",
        "",
        "# --- Option A: 原始 universe + --exclusion-csv（未来 batch builder 接线）---",
        "# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \\",
        f"#   --sample-file {universe_yaml} \\",
        f"#   --harvest-root {harvest_root} \\",
        f"#   --output-root {mock_output_root} \\",
        f"#   --exclusion-csv {exclusion_csv}",
        "",
        "# --- Option B: 本适配器已过滤 universe（当前离线可用 · 无 batch 接线依赖）---",
        "# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \\",
        f"#   --sample-file {filtered_universe_rel} \\",
        f"#   --harvest-root {harvest_root} \\",
        f"#   --output-root {mock_output_root}",
        "",
        "# 安全边界：",
        "# - output-root 必须为 _mock_* 前缀",
        "# - 禁止 863/phase3/phase35 生产 snapshot 根",
        "# - 禁止 execute / approve-* 与本 draft 同用",
        "",
    ]
    return "\n".join(lines)


def compute_metrics(
    companies: Sequence[Dict[str, str]],
    result: ExclusionFilterResult,
) -> Dict[str, Any]:
    excluded_unique = set(result.excluded_codes) & {c["company_code"] for c in companies}
    partial7_hit = EXPECTED_SLICE1_PARTIAL7 & excluded_unique
    empty3_hit = EXPECTED_SLICE1_EMPTY_DIVIDEND3 & excluded_unique
    missing_partial7 = sorted(EXPECTED_SLICE1_PARTIAL7 - excluded_unique)
    missing_empty3 = sorted(EXPECTED_SLICE1_EMPTY_DIVIDEND3 - excluded_unique)
    unexpected = sorted(excluded_unique - EXPECTED_SLICE1_EXCLUDED_UNIQUE)

    checks = {
        "universe_count_200": len(companies) == 200,
        "csv_kind_recognized": result.csv_kind
        in ("exclusion_reconcile", "exclusion_manifest"),
        "partial7_all_excluded": not missing_partial7,
        "empty_dividend3_all_excluded": not missing_empty3,
        "excluded_unique_10": len(excluded_unique) == 10,
        "included_190": result.included_count == 190,
        "no_execute_flag": True,
        "production_roots_untouched": True,
    }
    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"

    return {
        "generated_at": _utc_now_iso(),
        "universe_count": len(companies),
        "csv_kind": result.csv_kind,
        "exclusion_source_rows": result.source_row_count,
        "excluded_unique_count": len(excluded_unique),
        "included_count": result.included_count,
        "partial7_excluded_count": len(partial7_hit),
        "empty_dividend3_excluded_count": len(empty3_hit),
        "missing_partial7_codes": missing_partial7,
        "missing_empty_dividend3_codes": missing_empty3,
        "unexpected_excluded_codes": unexpected,
        "checks": checks,
        "gate": gate,
        "cninfo_calls": 0,
        "snapshot_json_writes": 0,
        "execute_production_snapshot_rebuild": False,
        "production_roots_mutated": False,
        "batch_builder_execute_invoked": False,
    }


def write_outputs(
    *,
    output_root_rel: str,
    companies: Sequence[Dict[str, str]],
    result: ExclusionFilterResult,
    metrics: Dict[str, Any],
    universe_yaml: str,
    exclusion_csv: str,
    harvest_root: str,
    mock_output_root: str,
) -> Dict[str, str]:
    assert_safe_erad_audit_write_path(
        os.path.join(BASE_DIR, output_root_rel),
        allowed_audit_root_rel=output_root_rel,
    )
    os.makedirs(os.path.join(BASE_DIR, output_root_rel), exist_ok=True)

    report_path = os.path.join(BASE_DIR, output_root_rel, "exclusion_filter_report.csv")
    filtered_yaml = os.path.join(
        BASE_DIR, output_root_rel, "filtered_universe_included.yaml"
    )
    draft_path = os.path.join(
        BASE_DIR, output_root_rel, "builder_command_draft.sh"
    )
    summary_path = os.path.join(BASE_DIR, output_root_rel, "prep_adapter_summary.md")
    metrics_path = os.path.join(BASE_DIR, output_root_rel, "run_meta.json")

    for path in (report_path, filtered_yaml, draft_path, summary_path, metrics_path):
        assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=output_root_rel)

    report_rows = build_filter_report_rows(companies, result)
    with open(report_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FILTER_REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(report_rows)

    filtered_rel = _rel(filtered_yaml)
    write_filtered_universe_yaml(
        result.included,
        filtered_yaml,
        source_universe=universe_yaml,
        exclusion_csv=exclusion_csv,
    )

    draft = build_command_draft(
        universe_yaml=universe_yaml,
        filtered_universe_rel=filtered_rel,
        exclusion_csv=exclusion_csv,
        harvest_root=harvest_root,
        mock_output_root=mock_output_root,
    )
    with open(draft_path, "w", encoding="utf-8") as fh:
        fh.write(draft)

    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    checks = metrics["checks"]
    check_lines = [
        f"| `{k}` | **{'PASS' if v else 'FAIL'}** |"
        for k, v in checks.items()
    ]
    lines = [
        "# CNINFO C 类 — Snapshot Exclusion Prep Adapter Dry-Run",
        "",
        f"_生成时间：{metrics['generated_at']} · offline · CNINFO=0_",
        "",
        "> **validation only** · **no snapshot JSON** · "
        "**execute_production_snapshot_rebuild=false** · "
        "**863/phase3/phase35 production snapshot roots untouched** · "
        "**batch builder --execute not invoked**",
        "",
        "## Inputs（read-only）",
        "",
        "| 项 | 路径 |",
        "|----|------|",
        f"| universe | `{universe_yaml}` |",
        f"| exclusion CSV | `{exclusion_csv}` |",
        f"| csv_kind | `{metrics['csv_kind']}` |",
        f"| output root | `{output_root_rel}` |",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| universe | **{metrics['universe_count']}** |",
        f"| exclusion source rows | **{metrics['exclusion_source_rows']}** |",
        f"| excluded (unique) | **{metrics['excluded_unique_count']}** |",
        f"| included (filtered) | **{metrics['included_count']}** |",
        f"| partial7 excluded | **{metrics['partial7_excluded_count']}/7** |",
        f"| empty_dividend3 excluded | **{metrics['empty_dividend3_excluded_count']}/3** |",
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
        f"c_class_erad_snapshot_exclusion_prep_adapter_gate = {metrics['gate']}",
        "execute_production_snapshot_rebuild = false",
        "batch_builder_execute_invoked = false",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute",
        "",
        "## Artifacts",
        "",
        f"- [{_rel(report_path)}]({os.path.basename(report_path)})",
        f"- [{_rel(filtered_yaml)}]({os.path.basename(filtered_yaml)})",
        f"- [{_rel(draft_path)}]({os.path.basename(draft_path)})",
        f"- [{_rel(metrics_path)}]({os.path.basename(metrics_path)})",
        f"- [{_rel(summary_path)}]({os.path.basename(summary_path)})",
        "",
        "## Capability note",
        "",
        "Run 11 `exclusion_reconcile.csv` 可直接作为 `--exclusion-csv` 输入喂入本适配器，",
        "产出 filtered universe 与带 `--exclusion-csv` 的 builder dry-run 命令草案。",
        "未向 `build_cninfo_c_class_snapshot_batch.py` 注入生产 execute 能力。",
        "",
    ]
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    return {
        "filter_report_csv": _rel(report_path),
        "filtered_universe_yaml": filtered_rel,
        "builder_command_draft": _rel(draft_path),
        "summary_md": _rel(summary_path),
        "run_meta_json": _rel(metrics_path),
    }


def run_adapter(
    *,
    universe_yaml: str = DEFAULT_UNIVERSE_YAML,
    exclusion_csv: str = DEFAULT_EXCLUSION_CSV,
    output_root: str = DEFAULT_OUTPUT_ROOT,
    harvest_root: str = DEFAULT_HARVEST_ROOT,
    mock_output_root: str = DEFAULT_MOCK_OUTPUT_ROOT,
    dry_run: bool = True,
    execute_production_snapshot_rebuild: bool = False,
) -> Dict[str, Any]:
    assert_execute_production_snapshot_rebuild_false(
        execute_production_snapshot_rebuild
    )
    refuse_exclusion_with_execute(dry_run=dry_run, exclusion_csv=exclusion_csv)
    if not dry_run:
        raise RuntimeError("PREP_ADAPTER_EXECUTE_FORBIDDEN: 仅允许 dry-run")

    companies = load_universe(universe_yaml)
    exclusion_abs = (
        exclusion_csv
        if os.path.isabs(exclusion_csv)
        else os.path.join(BASE_DIR, exclusion_csv)
    )
    result = filter_universe_with_exclusion_csv(companies, exclusion_abs)
    metrics = compute_metrics(companies, result)
    paths = write_outputs(
        output_root_rel=output_root,
        companies=companies,
        result=result,
        metrics=metrics,
        universe_yaml=universe_yaml,
        exclusion_csv=exclusion_csv,
        harvest_root=harvest_root,
        mock_output_root=mock_output_root,
    )
    metrics["artifacts"] = paths
    return metrics


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="C-class snapshot exclusion prep adapter dry-run（validation only）"
    )
    parser.add_argument("--universe-yaml", default=DEFAULT_UNIVERSE_YAML)
    parser.add_argument("--exclusion-csv", default=DEFAULT_EXCLUSION_CSV)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--harvest-root", default=DEFAULT_HARVEST_ROOT)
    parser.add_argument("--mock-output-root", default=DEFAULT_MOCK_OUTPUT_ROOT)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="默认 true；本工具仅 dry-run",
    )
    args = parser.parse_args(argv)

    result = run_adapter(
        universe_yaml=args.universe_yaml,
        exclusion_csv=args.exclusion_csv,
        output_root=args.output_root,
        harvest_root=args.harvest_root,
        mock_output_root=args.mock_output_root,
        dry_run=True,
        execute_production_snapshot_rebuild=False,
    )
    print("mode: snapshot_exclusion_prep_adapter_dryrun")
    print(f"gate: {result['gate']}")
    print(f"csv_kind: {result['csv_kind']}")
    print(f"universe: {result['universe_count']}")
    print(f"excluded_unique: {result['excluded_unique_count']}")
    print(f"included: {result['included_count']}")
    print(f"cninfo_calls: {result['cninfo_calls']}")
    print(f"snapshot_json_writes: {result['snapshot_json_writes']}")
    print(
        "execute_production_snapshot_rebuild: "
        f"{result['execute_production_snapshot_rebuild']}"
    )
    print(f"batch_builder_execute_invoked: {result['batch_builder_execute_invoked']}")
    for key, path in (result.get("artifacts") or {}).items():
        print(f"{key}: {path}")
    return 0 if result["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
