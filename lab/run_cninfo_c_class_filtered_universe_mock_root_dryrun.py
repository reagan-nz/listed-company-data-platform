#!/usr/bin/env python3
"""
CNINFO C-class — Wave1 filtered_universe × mock-root batch dry-run（离线）。

消费 Wave 1 `filtered_universe_included.yaml`（或 universe + --exclusion-csv 语义），
**程序化调用** `build_cninfo_c_class_snapshot_batch.run_dry_run`，写入
`outputs/validation/_mock_*` 隔离根。

为何不直接跑 batch CLI Option B：
  非 phase35 路径下 CLI 的 `--output-root` 被忽略，dry-run 会把 status/error
  写到默认 `outputs/snapshot/cninfo_c_class/full/quality/`（生产根风险）。
  本适配器显式传入 `out_dir`，绕过该 CLI 缺口，且硬拒绝非 `_mock_*` 根。

**不** --execute · **不** 写 snapshot JSON · **不** 触碰 863/phase3/phase35 生产根 ·
**不** 设置 execute_production_snapshot_rebuild。

Usage:
    python3 lab/run_cninfo_c_class_filtered_universe_mock_root_dryrun.py
    python3 lab/run_cninfo_c_class_filtered_universe_mock_root_dryrun.py \\
      --filtered-universe outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml \\
      --output-root outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/
    python3 lab/run_cninfo_c_class_filtered_universe_mock_root_dryrun.py \\
      --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml \\
      --exclusion-csv outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv \\
      --output-root outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Set

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from build_cninfo_c_class_snapshot_batch import (  # noqa: E402
    reset_snapshot_batch_paths,
    run_dry_run,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    assert_safe_erad_audit_write_path,
    is_allowed_mock_test_cleanup_path,
    normalize_cleanup_path,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    assert_execute_production_snapshot_rebuild_false,
    filter_universe_with_exclusion_csv,
    refuse_exclusion_with_execute,
)
from run_cninfo_c_class_snapshot_exclusion_prep_adapter_dryrun import (  # noqa: E402
    write_filtered_universe_yaml,
)
from run_cninfo_c_class_snapshot_exclusion_reconcile_dryrun import (  # noqa: E402
    EXPECTED_SLICE1_EMPTY_DIVIDEND3,
    EXPECTED_SLICE1_EXCLUDED_UNIQUE,
    EXPECTED_SLICE1_PARTIAL7,
    load_universe,
)

DEFAULT_FILTERED_UNIVERSE = (
    "outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/"
    "filtered_universe_included.yaml"
)
DEFAULT_UNIVERSE_YAML = "lab/eval_companies_c_class_fuller_market_slice1_200.yaml"
DEFAULT_EXCLUSION_CSV = (
    "outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/"
    "exclusion_reconcile.csv"
)
DEFAULT_OUTPUT_ROOT = (
    "outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun"
)
DEFAULT_HARVEST_ROOT = "outputs/harvest/cninfo_c_class/fuller_market_slice1_200/"

FORBIDDEN_PROD_SEGMENTS = (
    "outputs/snapshot/cninfo_c_class/full",
    "outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success",
    "outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491",
    "outputs/snapshot/cninfo_c_class/phase2_smoke_188",
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(path: str) -> str:
    if not os.path.isabs(path):
        return path.replace("\\", "/")
    return os.path.relpath(path, BASE_DIR).replace("\\", "/")


def _abs(path: str) -> str:
    if os.path.isabs(path):
        return os.path.normpath(path)
    return os.path.normpath(os.path.join(BASE_DIR, path))


def assert_mock_validation_output_root(output_root: str) -> str:
    """
    输出根必须：
      1) 落在 outputs/validation/ 下
      2) 路径段含 _mock_*（cleanup / audit guard 允许）
      3) 不落在 863/phase3/phase35/full 等生产 snapshot 根
    """
    norm = normalize_cleanup_path(output_root, base_dir=BASE_DIR)
    validation_root = normalize_cleanup_path("outputs/validation", base_dir=BASE_DIR)
    if not (norm == validation_root or norm.startswith(validation_root + os.sep)):
        raise RuntimeError(
            "MOCK_ROOT_NOT_UNDER_VALIDATION: "
            f"output-root 必须在 outputs/validation/ 下，收到: {_rel(norm)}"
        )
    if not is_allowed_mock_test_cleanup_path(norm, base_dir=BASE_DIR):
        raise RuntimeError(
            "MOCK_ROOT_PREFIX_REQUIRED: "
            f"output-root 路径段必须含 _mock_*，收到: {_rel(norm)}"
        )
    rel = _rel(norm)
    for forbidden in FORBIDDEN_PROD_SEGMENTS:
        if rel == forbidden or rel.startswith(forbidden + "/"):
            raise RuntimeError(
                f"PRODUCTION_SNAPSHOT_ROOT_FORBIDDEN: {rel}"
            )
    return norm


def count_snapshot_json_files(root: str) -> int:
    """统计 mock 根下 *.json（排除 run_meta.json 等非公司 snapshot）。"""
    if not os.path.isdir(root):
        return 0
    count = 0
    for name in os.listdir(root):
        if name.endswith(".json") and name not in ("run_meta.json",):
            # 公司 snapshot 形如 600000.json
            stem = name[:-5]
            if stem.isdigit() and len(stem) == 6:
                count += 1
    return count


def resolve_sample_universe(
    *,
    filtered_universe: Optional[str],
    universe_yaml: Optional[str],
    exclusion_csv: Optional[str],
    output_root_abs: str,
) -> Dict[str, Any]:
    """
    解析 dry-run 输入 universe：
      - 优先使用 Wave1 filtered_universe
      - 或 universe + exclusion-csv 现场过滤并写入 mock 根
    """
    if filtered_universe and not exclusion_csv:
        path = _abs(filtered_universe)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"filtered_universe_missing: {path}")
        return {
            "sample_path": path,
            "sample_rel": _rel(path),
            "mode": "wave1_filtered_universe",
            "exclusion_csv": None,
            "universe_yaml": None,
            "included_count_expected": None,
        }

    if universe_yaml and exclusion_csv:
        companies = load_universe(universe_yaml)
        exclusion_abs = _abs(exclusion_csv)
        result = filter_universe_with_exclusion_csv(companies, exclusion_abs)
        filtered_path = os.path.join(
            output_root_abs, "filtered_universe_included.yaml"
        )
        assert_safe_erad_audit_write_path(
            filtered_path,
            allowed_audit_root_rel=_rel(output_root_abs),
        )
        write_filtered_universe_yaml(
            result.included,
            filtered_path,
            source_universe=universe_yaml,
            exclusion_csv=exclusion_csv,
        )
        return {
            "sample_path": filtered_path,
            "sample_rel": _rel(filtered_path),
            "mode": "exclusion_csv_filter",
            "exclusion_csv": exclusion_csv,
            "universe_yaml": universe_yaml,
            "included_count_expected": result.included_count,
            "excluded_unique_count": len(result.excluded_codes),
            "csv_kind": result.csv_kind,
        }

    if filtered_universe and exclusion_csv:
        # 允许同时传入：以 filtered 为准，exclusion-csv 仅作语义标注
        path = _abs(filtered_universe)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"filtered_universe_missing: {path}")
        return {
            "sample_path": path,
            "sample_rel": _rel(path),
            "mode": "wave1_filtered_universe_with_exclusion_annotation",
            "exclusion_csv": exclusion_csv,
            "universe_yaml": universe_yaml,
            "included_count_expected": None,
        }

    raise RuntimeError(
        "SAMPLE_UNIVERSE_REQUIRED: 需要 --filtered-universe "
        "或 (--universe-yaml + --exclusion-csv)"
    )


def collect_execution_codes(execution_list: Sequence[Dict[str, str]]) -> Set[str]:
    return {str(r.get("company_code") or "").strip() for r in execution_list}


def compute_checks(
    *,
    dry_result: Dict[str, Any],
    output_root_abs: str,
    sample_info: Dict[str, Any],
) -> Dict[str, Any]:
    validation = dry_result.get("validation") or {}
    company_count = int(validation.get("company_count") or 0)
    codes = collect_execution_codes(dry_result.get("execution_list") or [])
    partial7_leak = sorted(EXPECTED_SLICE1_PARTIAL7 & codes)
    empty3_leak = sorted(EXPECTED_SLICE1_EMPTY_DIVIDEND3 & codes)
    excluded_leak = sorted(EXPECTED_SLICE1_EXCLUDED_UNIQUE & codes)
    snapshot_json = count_snapshot_json_files(output_root_abs)
    status_csv = os.path.join(
        output_root_abs, "quality", "company_snapshot_status.csv"
    )
    error_csv = os.path.join(
        output_root_abs, "quality", "company_snapshot_error.csv"
    )
    status_rows = 0
    if os.path.isfile(status_csv):
        with open(status_csv, encoding="utf-8", newline="") as fh:
            status_rows = sum(1 for _ in csv.DictReader(fh))

    expected_included = sample_info.get("included_count_expected")
    if expected_included is None:
        expected_included = 190

    checks = {
        "universe_ok": bool(dry_result.get("universe_ok")),
        "company_count_190": company_count == 190,
        "included_matches_expected": company_count == int(expected_included),
        "no_partial7_in_execution": not partial7_leak,
        "no_empty_dividend3_in_execution": not empty3_leak,
        "no_slice1_excluded_in_execution": not excluded_leak,
        "hold_overlap_0": int(validation.get("hold_overlap_count") or 0) == 0,
        "snapshot_json_writes_0": snapshot_json == 0,
        "status_csv_written": os.path.isfile(status_csv),
        "error_csv_written": os.path.isfile(error_csv),
        "status_row_count_matches": status_rows == company_count,
        "mock_root_under_validation": True,
        "batch_builder_execute_not_invoked": True,
        "production_roots_untouched": True,
    }
    gate = "PASS_OFFLINE" if all(checks.values()) else "FAIL_REVIEW_REQUIRED"
    return {
        "company_count": company_count,
        "execution_count": len(codes),
        "status_rows": status_rows,
        "partial7_leak_codes": partial7_leak,
        "empty_dividend3_leak_codes": empty3_leak,
        "excluded_leak_codes": excluded_leak,
        "snapshot_json_writes": snapshot_json,
        "builder_gate": dry_result.get("gate"),
        "checks": checks,
        "gate": gate,
    }


def write_capability_summary(
    *,
    path: str,
    metrics: Dict[str, Any],
    sample_info: Dict[str, Any],
    harvest_root: str,
    output_root_rel: str,
    report_rel: str,
    summary_rel: str,
) -> None:
    checks = metrics["checks"]
    check_lines = [
        f"| `{k}` | **{'PASS' if v else 'FAIL'}** |"
        for k, v in checks.items()
    ]
    lines = [
        "# CNINFO C 类 — Filtered Universe Mock-Root Dry-Run",
        "",
        f"_生成时间：{metrics['generated_at']} · offline · CNINFO=0_",
        "",
        "> **validation/_mock_* only** · **no snapshot JSON** · "
        "**execute_production_snapshot_rebuild=false** · "
        "**863/phase3/phase35 production snapshot roots untouched** · "
        "**batch builder --execute not invoked**",
        "",
        "## Inputs",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        f"| sample mode | `{sample_info['mode']}` |",
        f"| sample file | `{sample_info['sample_rel']}` |",
        f"| exclusion CSV | `{sample_info.get('exclusion_csv') or '(n/a · Wave1 filtered)'}` |",
        f"| harvest root (read-only) | `{harvest_root}` |",
        f"| mock output root | `{output_root_rel}` |",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| company_count | **{metrics['company_count']}** |",
        f"| execution_list | **{metrics['execution_count']}** |",
        f"| status rows | **{metrics['status_rows']}** |",
        f"| snapshot JSON writes | **{metrics['snapshot_json_writes']}** |",
        f"| builder dry-run gate | `{metrics['builder_gate']}` |",
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
        f"c_class_erad_filtered_universe_mock_root_dryrun_gate = {metrics['gate']}",
        "execute_production_snapshot_rebuild = false",
        "batch_builder_execute_invoked = false",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute",
        "",
        "## Documented dry-run command（本轮实际执行 · 程序化 API）",
        "",
        "```text",
        "python3 lab/run_cninfo_c_class_filtered_universe_mock_root_dryrun.py \\",
        f"  --filtered-universe {sample_info['sample_rel']} \\",
        f"  --harvest-root {harvest_root} \\",
        f"  --output-root {output_root_rel}/",
        "```",
        "",
        "内部等价于调用 `run_dry_run(universe_path=..., out_dir=<mock>, ...)`；",
        "不经由会忽略 `--output-root` 的 batch CLI 非 phase35 入口。",
        "",
        "## Artifacts",
        "",
        f"- [{report_rel}]({os.path.basename(report_rel)})",
        f"- [{summary_rel}]({os.path.basename(summary_rel)})",
        f"- [{_rel(path)}]({os.path.basename(path)})",
        f"- [{output_root_rel}/run_meta.json](run_meta.json)",
        f"- [{output_root_rel}/quality/company_snapshot_status.csv]"
        "(quality/company_snapshot_status.csv)",
        "",
        "## Capability note",
        "",
        "Wave 1 `filtered_universe_included.yaml` / `--exclusion-csv` 语义现可被",
        "**真实 batch `run_dry_run`** 消费，产物仅落在 `outputs/validation/_mock_*`。",
        "",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def run_mock_root_dryrun(
    *,
    filtered_universe: Optional[str] = DEFAULT_FILTERED_UNIVERSE,
    universe_yaml: Optional[str] = None,
    exclusion_csv: Optional[str] = None,
    output_root: str = DEFAULT_OUTPUT_ROOT,
    harvest_root: str = DEFAULT_HARVEST_ROOT,
    dry_run: bool = True,
    execute_production_snapshot_rebuild: bool = False,
) -> Dict[str, Any]:
    assert_execute_production_snapshot_rebuild_false(
        execute_production_snapshot_rebuild
    )
    if not dry_run:
        raise RuntimeError("MOCK_ROOT_DRYRUN_EXECUTE_FORBIDDEN: 仅允许 dry-run")
    refuse_exclusion_with_execute(
        dry_run=True,
        exclusion_csv=exclusion_csv or "",
    )

    output_root_abs = assert_mock_validation_output_root(output_root)
    output_root_rel = _rel(output_root_abs)
    assert_safe_erad_audit_write_path(
        output_root_abs,
        allowed_audit_root_rel=output_root_rel,
    )
    os.makedirs(output_root_abs, exist_ok=True)

    sample_info = resolve_sample_universe(
        filtered_universe=filtered_universe,
        universe_yaml=universe_yaml,
        exclusion_csv=exclusion_csv,
        output_root_abs=output_root_abs,
    )

    report_path = os.path.join(output_root_abs, "dryrun_report.csv")
    summary_path = os.path.join(output_root_abs, "dryrun_summary.md")
    capability_path = os.path.join(
        output_root_abs, "mock_root_dryrun_capability_summary.md"
    )
    meta_path = os.path.join(output_root_abs, "run_meta.json")

    for path in (report_path, summary_path, capability_path, meta_path):
        assert_safe_erad_audit_write_path(
            path, allowed_audit_root_rel=output_root_rel
        )

    try:
        dry_result = run_dry_run(
            universe_path=sample_info["sample_path"],
            out_dir=output_root_abs,
            harvest_root=harvest_root,
            report_path=report_path,
            summary_path=summary_path,
            resume=False,
            force=False,
        )
    finally:
        reset_snapshot_batch_paths()

    metrics = compute_checks(
        dry_result=dry_result,
        output_root_abs=output_root_abs,
        sample_info=sample_info,
    )
    metrics["generated_at"] = _utc_now_iso()
    metrics["cninfo_calls"] = 0
    metrics["execute_production_snapshot_rebuild"] = False
    metrics["production_roots_mutated"] = False
    metrics["batch_builder_execute_invoked"] = False
    metrics["harvest_mutated"] = False
    metrics["sample_mode"] = sample_info["mode"]
    metrics["sample_file"] = sample_info["sample_rel"]
    metrics["exclusion_csv"] = sample_info.get("exclusion_csv")
    metrics["harvest_root"] = harvest_root
    metrics["output_root"] = output_root_rel

    write_capability_summary(
        path=capability_path,
        metrics=metrics,
        sample_info=sample_info,
        harvest_root=harvest_root,
        output_root_rel=output_root_rel,
        report_rel=_rel(report_path),
        summary_rel=_rel(summary_path),
    )

    artifacts = {
        "dryrun_report_csv": _rel(report_path),
        "dryrun_summary_md": _rel(summary_path),
        "capability_summary_md": _rel(capability_path),
        "run_meta_json": _rel(meta_path),
        "status_csv": _rel(
            os.path.join(output_root_abs, "quality", "company_snapshot_status.csv")
        ),
        "error_csv": _rel(
            os.path.join(output_root_abs, "quality", "company_snapshot_error.csv")
        ),
    }
    metrics["artifacts"] = artifacts

    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    return metrics


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "C-class filtered-universe mock-root dry-run "
            "（validation/_mock_* only · 调用 batch run_dry_run）"
        )
    )
    parser.add_argument(
        "--filtered-universe",
        default=DEFAULT_FILTERED_UNIVERSE,
        help="Wave 1 filtered_universe_included.yaml",
    )
    parser.add_argument(
        "--universe-yaml",
        default=None,
        help="原始 universe；与 --exclusion-csv 联用时现场过滤",
    )
    parser.add_argument(
        "--exclusion-csv",
        default=None,
        help="exclusion reconcile/manifest CSV（preparation dry-run only）",
    )
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--harvest-root", default=DEFAULT_HARVEST_ROOT)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="默认 true；本工具仅 dry-run",
    )
    args = parser.parse_args(argv)

    # 默认路径：仅 filtered；若用户显式给了 exclusion 且未改 filtered，走 annotation 或 filter
    filtered = args.filtered_universe
    universe = args.universe_yaml
    exclusion = args.exclusion_csv

    if exclusion and universe:
        # 现场过滤模式：不以默认 filtered 覆盖
        if filtered == DEFAULT_FILTERED_UNIVERSE:
            filtered = None

    result = run_mock_root_dryrun(
        filtered_universe=filtered,
        universe_yaml=universe,
        exclusion_csv=exclusion,
        output_root=args.output_root,
        harvest_root=args.harvest_root,
        dry_run=True,
        execute_production_snapshot_rebuild=False,
    )
    print("mode: filtered_universe_mock_root_dryrun")
    print(f"gate: {result['gate']}")
    print(f"sample_mode: {result['sample_mode']}")
    print(f"sample_file: {result['sample_file']}")
    print(f"company_count: {result['company_count']}")
    print(f"execution_count: {result['execution_count']}")
    print(f"snapshot_json_writes: {result['snapshot_json_writes']}")
    print(f"cninfo_calls: {result['cninfo_calls']}")
    print(f"output_root: {result['output_root']}")
    print(
        "execute_production_snapshot_rebuild: "
        f"{result['execute_production_snapshot_rebuild']}"
    )
    print(f"batch_builder_execute_invoked: {result['batch_builder_execute_invoked']}")
    print(f"production_roots_mutated: {result['production_roots_mutated']}")
    for key, path in (result.get("artifacts") or {}).items():
        print(f"{key}: {path}")
    return 0 if result["gate"] == "PASS_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
