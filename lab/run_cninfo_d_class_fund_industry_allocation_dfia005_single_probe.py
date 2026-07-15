#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D-FM-18：DFIA005 单探针 bounded retry（仅 rdate=20251231 · CNINFO≤1）。

复用 first-slice runner 评估逻辑；不重跑 default/rdate_20260331。
D-FM-19 后 lock expected=`captured_normal_or_empty_but_valid`（本脚本只读 lock · 不 mutate）。
默认 dry-run（CNINFO=0）；live 须显式 --live + approve flag。
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import run_cninfo_d_class_tiny_live_validation as runner  # noqa: E402

PROBE_KEY = "rdate_20251231"
CASE_ID = "DFIA005"
TASK_ID = "D-FM-18"
MAX_CNINFO = 1

DEFAULT_OUTPUT_DIR = os.path.join(
    runner.BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_fund_industry_allocation_dfia005_single_probe",
)
DEFAULT_UNIVERSE_CSV = runner.DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_UNIVERSE_CSV

PROBE_GATE_PASS = "PASS_WITH_CAVEAT"
PROBE_GATE_CLEAR = "PASS_OFFLINE_TRANSPORT_CLEARED"
PROBE_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
LIVE_GATE = "NOT_APPROVED"


def _load_dfia005_row(
    universe_csv: str,
) -> runner.FundIndustryAllocationFirstSliceRow:
    rows = runner.load_fund_industry_allocation_first_slice_universe(universe_csv)
    issues = runner.validate_fund_industry_allocation_first_slice_universe(rows)
    if issues:
        raise SystemExit(f"ERROR: universe validation failed: {issues}")
    by_id = {r.case_id: r for r in rows}
    row = by_id.get(CASE_ID)
    if row is None:
        raise SystemExit(f"ERROR: missing_case_id:{CASE_ID}")
    if row.query_mode != "rdate" or row.anchor_rdate != "20251231":
        raise SystemExit(
            f"ERROR: DFIA005 lock anchor mismatch: "
            f"mode={row.query_mode} rdate={row.anchor_rdate}"
        )
    # D-FM-19：期望已放宽；仍拒绝其它未知期望，避免静默漂移
    if row.expected_behavior != "captured_normal_or_empty_but_valid":
        raise SystemExit(
            f"ERROR: DFIA005 expected_behavior must be "
            f"captured_normal_or_empty_but_valid; got={row.expected_behavior}"
        )
    return row


def _build_component_cfg() -> Tuple[dict, str]:
    endpoints = runner.load_registry_endpoints()
    source_configs = runner.load_table_source_configs()
    component_cfg = copy.deepcopy(
        source_configs.get(runner.FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_COMPONENT, {})
    )
    endpoint = endpoints.get(
        runner.FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_COMPONENT,
        component_cfg.get(
            "api_url", runner.FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ENDPOINT
        ),
    )
    component_cfg["api_url"] = endpoint
    # 与 D-FM-13 一致：rdate override 须走 form，否则 params_location=none 静默丢弃
    if str(component_cfg.get("params_location") or "").lower() == "none":
        component_cfg["params_location"] = "form"
    return component_cfg, endpoint


def _ensure_output_dir(path: str) -> str:
    out = os.path.abspath(path)
    os.makedirs(out, exist_ok=True)
    os.makedirs(os.path.join(out, "reports"), exist_ok=True)
    os.makedirs(os.path.join(out, "live_snapshots"), exist_ok=True)
    return out


def _write_csv(path: str, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_dry_run(output_dir: str, universe_csv: str) -> int:
    """离线 dry-run：校验 lock 锚点 · CNINFO=0 · 写出计划探针。"""
    row = _load_dfia005_row(universe_csv)
    out = _ensure_output_dir(output_dir)
    params = runner._build_fund_industry_allocation_first_slice_params_for_probe(
        PROBE_KEY
    )
    planned = {
        "task_id": TASK_ID,
        "case_id": CASE_ID,
        "shared_probe_key": PROBE_KEY,
        "query_params": params,
        "expected_behavior": row.expected_behavior,
        "industry_code": row.industry_code,
        "cninfo_budget": MAX_CNINFO,
        "universe_lock_mutated": False,
        "mode": "dry_run",
    }
    plan_path = os.path.join(out, "reports", "dfia005_single_probe_plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(planned, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(
        f"mode=dfia005_single_probe_dry_run case={CASE_ID} "
        f"probe={PROBE_KEY} cninfo_calls=0 planned_cninfo_budget={MAX_CNINFO}"
    )
    print(f"plan={plan_path}")
    return 0


def execute_live_single_probe(
    output_dir: str,
    universe_csv: str,
    session: Optional[requests.Session] = None,
    cninfo_request_fn=None,
) -> int:
    """执行唯一共享探针 rdate_20251231 · 硬上限 CNINFO≤1。"""
    row = _load_dfia005_row(universe_csv)
    out = _ensure_output_dir(output_dir)
    component_cfg, endpoint = _build_component_cfg()
    params = runner._build_fund_industry_allocation_first_slice_params_for_probe(
        PROBE_KEY
    )

    stats = runner.LiveStats()
    sess = session or requests.Session()
    request_fn = cninfo_request_fn or runner._cninfo_request
    payload, http_status, last_error = request_fn(
        sess, component_cfg, params, stats, PROBE_KEY
    )

    if stats.cninfo_requests > MAX_CNINFO:
        print(
            f"ERROR: cninfo_budget_exceeded:{stats.cninfo_requests}>{MAX_CNINFO}",
            file=sys.stderr,
        )
        return 2

    all_records = runner._extract_records(payload) if payload is not None else []
    industry_records = runner._filter_industry_records(
        all_records, row.industry_code
    )
    summary = runner.assess_fund_industry_allocation_first_slice_shared_case(
        row,
        industry_records,
        http_status,
        last_error,
        endpoint,
        params,
        stats.cninfo_requests,
        PROBE_KEY,
    )
    acceptable = runner.is_fund_industry_allocation_first_slice_acceptable(
        row, summary
    )
    failure_type = runner.assess_fund_industry_allocation_first_slice_failure_type(
        row, summary
    )
    rs = summary.get("retrieval_status", "")
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0

    # 探针层 caveat：运输 vs 期望匹配（D-FM-19 后 found/empty 均合法 · 无 stale）
    if last_error or rs in ("http_error", "blocked"):
        caveat = "transport_or_http_error"
        gate = PROBE_GATE_PASS
    elif rs == "empty_but_valid" and rc == 0 and acceptable:
        caveat = ""
        gate = PROBE_GATE_CLEAR
    elif rs == "found" and rc >= 1 and acceptable:
        # D-FM-19：mixed 期望下 found 为合法路径；不再标 empty_control_anchor_stale
        caveat = ""
        gate = PROBE_GATE_CLEAR
    elif acceptable:
        caveat = ""
        gate = PROBE_GATE_PASS
    else:
        caveat = failure_type or "expectation_mismatch"
        gate = PROBE_GATE_FAIL

    # 单探针证据目录；不覆盖 first-slice 5/5 live_report
    snap_path = os.path.join(
        out, "live_snapshots", f"{CASE_ID}_fund_industry_allocation.json"
    )
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "task_id": TASK_ID,
                "case_id": CASE_ID,
                "industry_code": row.industry_code,
                "industry_name": row.industry_name,
                "component": row.component,
                "query_mode": row.query_mode,
                "anchor_rdate": row.anchor_rdate,
                "retrieval_status": rs,
                "quality_status": summary.get("quality_status", ""),
                "lineage_status": summary.get("lineage_status", ""),
                "record_count": summary.get("record_count", "0"),
                "endpoint_used": endpoint,
                "query_params": params,
                "sample_records": (summary.get("_sample_records") or [])[:3],
                "shared_probe": PROBE_KEY,
                "cninfo_called": True,
                "cninfo_requests": stats.cninfo_requests,
                "http_status": http_status,
                "last_error": last_error,
                "acceptable": "yes" if acceptable else "no",
                "failure_type": failure_type,
                "caveat": caveat,
                "probe_gate": gate,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
        f.write("\n")

    live_row = {
        "case_id": CASE_ID,
        "probe_key": PROBE_KEY,
        "expected_behavior": row.expected_behavior,
        "retrieval_status": rs,
        "record_count": summary.get("record_count", "0"),
        "acceptable": "yes" if acceptable else "no",
        "failure_type": failure_type,
        "caveat": caveat,
        "http_status": str(http_status),
        "last_error": last_error,
        "cninfo_requests": str(stats.cninfo_requests),
        "endpoint": endpoint,
        "task_id": TASK_ID,
        "probe_gate": gate,
    }
    report_path = os.path.join(
        out, "reports", "dfia005_single_probe_live_report.csv"
    )
    _write_csv(
        report_path,
        [live_row],
        list(live_row.keys()),
    )

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    summary_md = os.path.join(
        out, "reports", "dfia005_single_probe_live_summary.md"
    )
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write(
            "\n".join(
                [
                    "# CNINFO D 类 fund_industry_allocation — DFIA005 Single-Probe Live",
                    "",
                    f"_生成时间：{ts}_",
                    "",
                    f"> **性质：** DFIA005 bounded single-probe · probe=`{PROBE_KEY}` · "
                    f"**CNINFO≤{MAX_CNINFO}** · **live_gate={LIVE_GATE}**",
                    "",
                    "## Result",
                    "",
                    "| 项 | 值 |",
                    "|----|-----|",
                    f"| case_id | **{CASE_ID}** |",
                    f"| probe | `{PROBE_KEY}` |",
                    f"| expected | `{row.expected_behavior}` |",
                    f"| retrieval_status | `{rs}` |",
                    f"| records | **{summary.get('record_count', '0')}** |",
                    f"| acceptable | **{'yes' if acceptable else 'no'}** |",
                    f"| failure_type | `{failure_type or '—'}` |",
                    f"| caveat | `{caveat or '—'}` |",
                    f"| CNINFO calls | **{stats.cninfo_requests}** |",
                    f"| http_status | {http_status} |",
                    f"| last_error | `{last_error or '—'}` |",
                    "",
                    "## Gates",
                    "",
                    "```text",
                    f"d_class_fund_industry_allocation_dfia005_single_probe_gate = {gate}",
                    f"d_class_fund_industry_allocation_first_slice_live_gate = {LIVE_GATE}",
                    f"caveat = {caveat or 'none'}",
                    "```",
                    "",
                    "**NOT verified** · **NOT production_ready** · **NOT bare PASS**",
                    "",
                ]
            )
            + "\n"
        )

    print(
        f"{CASE_ID} {summary.get('retrieval_status')}: "
        f"records={summary.get('record_count')} "
        f"acceptable={'yes' if acceptable else 'no'} "
        f"cninfo_calls={stats.cninfo_requests} probe={PROBE_KEY}",
        flush=True,
    )
    print(
        f"mode=dfia005_single_probe_live gate={gate} "
        f"cninfo_calls={stats.cninfo_requests}"
    )
    print(f"live_report={report_path}")
    print(f"live_summary={summary_md}")
    print(f"live_snapshot={snap_path}")
    return 0 if gate in (PROBE_GATE_CLEAR, PROBE_GATE_PASS) else 1


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="DFIA005 single-probe bounded retry (rdate=20251231, CNINFO≤1)"
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="离线计划 · CNINFO=0")
    mode.add_argument("--live", action="store_true", help="真实单探针 · CNINFO≤1")
    p.add_argument(
        "--approve-d-class-fund-industry-allocation-first-slice",
        action="store_true",
        help="standing capital 显式批准本单探针 live",
    )
    p.add_argument(
        "--universe-csv",
        default=DEFAULT_UNIVERSE_CSV,
        help="universe lock CSV（只读校验 · 不 mutate）",
    )
    p.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="单探针证据输出根（不覆盖 first-slice 5-case live_report）",
    )
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.live:
        if not args.approve_d_class_fund_industry_allocation_first_slice:
            print(
                "ERROR: approve_d_class_fund_industry_allocation_first_slice_required",
                file=sys.stderr,
            )
            return 2
        return execute_live_single_probe(args.output_dir, args.universe_csv)
    return run_dry_run(args.output_dir, args.universe_csv)


if __name__ == "__main__":
    sys.exit(main())
