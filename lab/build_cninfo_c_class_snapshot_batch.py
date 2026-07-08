#!/usr/bin/env python3
"""
CNINFO C-class Company Snapshot Full Batch Runner（Era C Phase 4）。

默认 --dry-run：验证 universe · 输出路径 · status/error/resume 框架，**不调用 build_snapshot**。
Full batch 执行需显式 --execute --approve-full-snapshot-batch（本轮不默认执行）。

Usage:
    python lab/build_cninfo_c_class_snapshot_batch.py --dry-run
    python lab/build_cninfo_c_class_snapshot_batch.py --execute --approve-full-snapshot-batch  # 未来执行
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import yaml  # noqa: E402

from build_cninfo_c_class_company_snapshot import (  # noqa: E402
    SNAPSHOT_MODULES,
    build_snapshot,
    _load_mapping,
)

BASE_DIR = os.path.dirname(_LAB_DIR)

UNIVERSE_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
HOLD_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml")

FULL_OUT_DIR = os.path.join(BASE_DIR, "outputs/snapshot/cninfo_c_class/full")
QUALITY_DIR = os.path.join(FULL_OUT_DIR, "quality")
STATUS_CSV = os.path.join(QUALITY_DIR, "company_snapshot_status.csv")
ERROR_CSV = os.path.join(QUALITY_DIR, "company_snapshot_error.csv")

DRYRUN_REPORT_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_snapshot_batch_dryrun_report.csv"
)
DRYRUN_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_snapshot_batch_dryrun_summary.md"
)

EXPECTED_COMPANY_COUNT = 863
HOLD_COUNT = 26
PLANNED_MODULE_COUNT = len(SNAPSHOT_MODULES)

FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED = "FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED"

STATUS_FIELDS = [
    "company_code",
    "company_name",
    "status",
    "started_at",
    "finished_at",
    "module_available_count",
    "module_partial_count",
    "module_missing_count",
    "error_count",
    "last_error",
    "retry_status",
]

ERROR_FIELDS = [
    "company_code",
    "module",
    "error_type",
    "error_message",
    "retry_possible",
]

DRYRUN_REPORT_FIELDS = [
    "company_code",
    "company_name",
    "board",
    "planned_modules",
    "planned_output",
    "status",
]

TERMINAL_STATUSES = {"complete", "complete_with_caveat", "failed"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_code(code: str) -> str:
    return str(code).strip().zfill(6)


def load_universe_yaml(path: str = UNIVERSE_YAML) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """加载 863 harvest universe。"""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    companies: List[Dict[str, str]] = []
    for item in data.get("companies", []):
        companies.append({
            "company_code": _normalize_code(item["stock_code"]),
            "company_name": item.get("company_name") or item.get("short_name", ""),
            "board": item.get("board", ""),
        })
    return companies, data


def load_hold_codes(path: str = HOLD_YAML) -> Set[str]:
    """加载 26 all6 hold 代码集合。"""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return {_normalize_code(c["stock_code"]) for c in data.get("companies", [])}


def validate_universe(
    companies: List[Dict[str, str]],
    hold_codes: Set[str],
    expected_count: int = EXPECTED_COMPANY_COUNT,
) -> Tuple[bool, Dict[str, Any]]:
    """校验 universe 规模与 hold 无重叠。"""
    codes = [c["company_code"] for c in companies]
    universe_set = set(codes)
    overlap = sorted(universe_set & hold_codes)
    detail = {
        "company_count": len(companies),
        "expected_count": expected_count,
        "hold_overlap": overlap,
        "hold_overlap_count": len(overlap),
        "duplicate_codes": sorted({c for c in codes if codes.count(c) > 1}),
    }
    ok = (
        len(companies) == expected_count
        and len(overlap) == 0
        and not detail["duplicate_codes"]
    )
    return ok, detail


def planned_snapshot_path(company_code: str, out_dir: str = FULL_OUT_DIR) -> str:
    rel = os.path.join(
        "outputs/snapshot/cninfo_c_class/full",
        f"{_normalize_code(company_code)}.json",
    )
    return os.path.join(out_dir, f"{_normalize_code(company_code)}.json")


def build_execution_list(
    companies: List[Dict[str, str]],
    out_dir: str = FULL_OUT_DIR,
) -> List[Dict[str, str]]:
    """生成 batch 执行清单（dry-run / execute 共用）。"""
    rows: List[Dict[str, str]] = []
    for item in companies:
        code = item["company_code"]
        rows.append({
            "company_code": code,
            "company_name": item["company_name"],
            "board": item["board"],
            "snapshot_status": "pending",
            "planned_output_path": planned_snapshot_path(code, out_dir),
        })
    return rows


def init_status_rows(execution_list: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """初始化 status CSV 行（全部 pending）。"""
    rows: List[Dict[str, Any]] = []
    for item in execution_list:
        rows.append({
            "company_code": item["company_code"],
            "company_name": item["company_name"],
            "status": "pending",
            "started_at": "",
            "finished_at": "",
            "module_available_count": "",
            "module_partial_count": "",
            "module_missing_count": "",
            "error_count": "0",
            "last_error": "",
            "retry_status": "none",
        })
    return rows


def read_status_csv(path: str = STATUS_CSV) -> Dict[str, Dict[str, str]]:
    """读取已有 status；不存在则返回空 dict。"""
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return {row["company_code"]: row for row in csv.DictReader(fh)}


def write_status_csv(rows: List[Dict[str, Any]], path: str = STATUS_CSV) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=STATUS_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_error_csv(rows: List[Dict[str, str]], path: str = ERROR_CSV) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=ERROR_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def append_error_record(
    errors: List[Dict[str, str]],
    company_code: str,
    module: str,
    error_type: str,
    error_message: str,
    retry_possible: str = "yes",
) -> None:
    errors.append({
        "company_code": _normalize_code(company_code),
        "module": module,
        "error_type": error_type,
        "error_message": error_message,
        "retry_possible": retry_possible,
    })


def filter_resume_targets(
    execution_list: List[Dict[str, str]],
    status_by_code: Dict[str, Dict[str, str]],
    force: bool = False,
) -> List[Dict[str, str]]:
    """Resume：跳过已终态公司（除非 force）。"""
    if force:
        return list(execution_list)
    targets: List[Dict[str, str]] = []
    for item in execution_list:
        code = item["company_code"]
        existing = status_by_code.get(code)
        if existing and existing.get("status") in TERMINAL_STATUSES:
            continue
        targets.append(item)
    return targets


def run_single_company_safe(
    company_code: str,
    mapping_rows: List[Dict[str, str]],
    build_fn: Callable[[str, List[Dict[str, str]]], Tuple[Dict[str, Any], Dict[str, Any]]],
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[Exception]]:
    """单公司构建；异常隔离，不向上抛出。"""
    try:
        snapshot, stats = build_fn(company_code, mapping_rows)
        return snapshot, stats, None
    except Exception as exc:  # noqa: BLE001 — batch 需捕获所有构建异常
        return None, None, exc


def _stats_module_counts(stats: Dict[str, Any]) -> Tuple[int, int, int]:
    ms = stats.get("module_status", {})
    avail = sum(1 for s in ms.values() if s == "available")
    partial = sum(1 for s in ms.values() if s == "partial")
    missing = sum(1 for s in ms.values() if s == "not_available")
    return avail, partial, missing


def run_execute_batch(
    targets: List[Dict[str, str]],
    mapping_rows: List[Dict[str, str]],
    status_rows_by_code: Dict[str, Dict[str, Any]],
    out_dir: str = FULL_OUT_DIR,
    build_fn: Callable[
        [str, List[Dict[str, str]]],
        Tuple[Dict[str, Any], Dict[str, Any]],
    ] = build_snapshot,
    write_json: bool = True,
) -> Tuple[List[Dict[str, str]], int, int]:
    """
    执行 batch（需显式批准）；单公司失败不影响其他公司。
    返回 (error_rows, success_count, failed_count)。
    """
    import json

    errors: List[Dict[str, str]] = []
    success_count = 0
    failed_count = 0
    os.makedirs(out_dir, exist_ok=True)

    for item in targets:
        code = item["company_code"]
        row = status_rows_by_code[code]
        started = _now_iso()
        row["status"] = "running"
        row["started_at"] = started
        row["retry_status"] = "none"

        snapshot, stats, exc = run_single_company_safe(code, mapping_rows, build_fn)
        finished = _now_iso()

        if exc is not None:
            failed_count += 1
            err_count = int(row.get("error_count") or "0") + 1
            row.update({
                "status": "failed",
                "finished_at": finished,
                "error_count": str(err_count),
                "last_error": f"{type(exc).__name__}: {exc}",
                "retry_status": "pending",
            })
            append_error_record(
                errors,
                code,
                "__build__",
                type(exc).__name__,
                str(exc),
                "yes",
            )
            continue

        assert snapshot is not None and stats is not None
        avail, partial, missing = _stats_module_counts(stats)
        snap_status = snapshot.get("snapshot_status", "complete_with_caveat")
        final_status = (
            "complete" if snap_status == "complete" else "complete_with_caveat"
        )
        row.update({
            "status": final_status,
            "finished_at": finished,
            "module_available_count": str(avail),
            "module_partial_count": str(partial),
            "module_missing_count": str(missing),
            "error_count": row.get("error_count") or "0",
            "last_error": "",
            "retry_status": "done",
        })
        success_count += 1

        if write_json:
            out_path = planned_snapshot_path(code, out_dir)
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(snapshot, fh, ensure_ascii=False, indent=2)
                fh.write("\n")

    return errors, success_count, failed_count


def build_dryrun_report_rows(execution_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for item in execution_list:
        rows.append({
            "company_code": item["company_code"],
            "company_name": item["company_name"],
            "board": item["board"],
            "planned_modules": str(PLANNED_MODULE_COUNT),
            "planned_output": item["planned_output_path"],
            "status": "pending",
        })
    return rows


def write_dryrun_report(rows: List[Dict[str, str]], path: str = DRYRUN_REPORT_CSV) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=DRYRUN_REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_dryrun_summary(
    validation: Dict[str, Any],
    universe_meta: Dict[str, Any],
    resume_skipped: int = 0,
    path: str = DRYRUN_SUMMARY_MD,
) -> str:
    """写入 dry-run summary；返回 gate。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    gate = "PASS" if validation["ok"] else "FAIL"
    if gate == "PASS":
        gate = "PASS_WITH_CAVEAT"

    board_counts = universe_meta.get("board_counts") or {}
    lines = [
        "# CNINFO C-Class Snapshot Batch Dry-Run Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 batch runner dry-run。**无 CNINFO** · **未调用 build_snapshot** · **未生成 snapshot JSON**",
        "",
        "**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`",
        "",
        "# Batch Universe",
        "",
        f"company_count: **{validation['company_count']}**",
        "",
        f"hold_count: **{HOLD_COUNT}**（all6 hold 已排除）",
        "",
        f"hold_overlap: **{validation['hold_overlap_count']}**",
        "",
        "## 板块分布",
        "",
        "| board | count |",
        "|-------|-------|",
    ]
    for board, count in sorted(board_counts.items()):
        lines.append(f"| {board} | **{count}** |")

    lines.extend([
        "",
        "# Output Design",
        "",
        f"snapshot_path: `{os.path.relpath(FULL_OUT_DIR, BASE_DIR)}/{{company_code}}.json`",
        "",
        f"quality_path: `{os.path.relpath(QUALITY_DIR, BASE_DIR)}/`",
        "",
        f"planned_modules: **{PLANNED_MODULE_COUNT}**",
        "",
        "# Resume Design",
        "",
        f"- status file: `{os.path.relpath(STATUS_CSV, BASE_DIR)}`",
        f"- terminal statuses: {', '.join(sorted(TERMINAL_STATUSES))}",
        f"- resume skips terminal rows unless `--force`",
        f"- dry-run resume_skipped: **{resume_skipped}**",
        "",
        "# Error Handling",
        "",
        f"- error file: `{os.path.relpath(ERROR_CSV, BASE_DIR)}`",
        "- 单公司 `try/except` 隔离；失败写入 error CSV，继续下一家",
        "- dry-run 仅初始化空 error CSV（header only）",
        "",
        "# Estimated Scale",
        "",
        f"- companies: **{EXPECTED_COMPANY_COUNT}**",
        f"- snapshot JSON: **{EXPECTED_COMPANY_COUNT}**（执行阶段）",
        "- estimated disk: **500–900 MB**",
        "- estimated runtime: **15–45 min**（离线单进程粗估）",
        "",
        "# Gate",
        "",
        "```",
        f"snapshot_batch_dryrun_gate = {gate}",
        "```",
        "",
        "## Validation",
        "",
        f"- universe_ok: **{validation['ok']}**",
        f"- expected_count: **{validation['expected_count']}**",
        f"- hold_overlap_count: **{validation['hold_overlap_count']}**",
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO · 未重跑 harvest",
        "- raw / normalized / field_inventory **未修改**",
        "- **未生成** `full/*.json` snapshot",
        "- 未入库 / MinIO / RAG · 未写 verified",
        "",
        f"详见 [cninfo_c_class_snapshot_batch_dryrun_report.csv](cninfo_c_class_snapshot_batch_dryrun_report.csv)。",
    ])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return gate


def run_dry_run(
    universe_path: str = UNIVERSE_YAML,
    hold_path: str = HOLD_YAML,
    out_dir: str = FULL_OUT_DIR,
    status_path: str = STATUS_CSV,
    error_path: str = ERROR_CSV,
    report_path: str = DRYRUN_REPORT_CSV,
    summary_path: str = DRYRUN_SUMMARY_MD,
    resume: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Dry-run：验证输入 · 生成 status/error 框架 · 写 dry-run 报告。
    **不调用 build_snapshot** · **不写 snapshot JSON**。
    """
    companies, universe_meta = load_universe_yaml(universe_path)
    hold_codes = load_hold_codes(hold_path)
    ok, validation = validate_universe(companies, hold_codes)
    validation["ok"] = ok

    execution_list = build_execution_list(companies, out_dir=out_dir)
    existing_status = read_status_csv(status_path) if resume else {}
    resume_skipped = 0
    if resume and existing_status:
        before = len(execution_list)
        execution_list = filter_resume_targets(execution_list, existing_status, force=force)
        resume_skipped = before - len(execution_list)

    if resume and existing_status and not force:
        status_rows = list(existing_status.values())
        known = {r["company_code"] for r in status_rows}
        for item in companies:
            code = item["company_code"]
            if code not in known:
                status_rows.append(init_status_rows([{
                    "company_code": code,
                    "company_name": item["company_name"],
                }])[0])
    else:
        status_rows = init_status_rows(
            build_execution_list(companies, out_dir=out_dir)
        )

    write_status_csv(status_rows, path=status_path)
    write_error_csv([], path=error_path)

    report_rows = build_dryrun_report_rows(
        build_execution_list(companies, out_dir=out_dir)
    )
    write_dryrun_report(report_rows, path=report_path)
    gate = write_dryrun_summary(
        validation,
        universe_meta,
        resume_skipped=resume_skipped,
        path=summary_path,
    )

    return {
        "validation": validation,
        "universe_ok": ok,
        "execution_list": execution_list,
        "status_rows": status_rows,
        "report_rows": report_rows,
        "gate": gate,
        "resume_skipped": resume_skipped,
    }


def enforce_execute_approval(args: argparse.Namespace) -> None:
    """无批准标志时拒绝 execute。"""
    if not args.dry_run and not args.approve_full_snapshot_batch:
        print(FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED, file=sys.stderr)
        raise SystemExit(2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CNINFO C-class snapshot full batch runner（dry-run default）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        default=True,
        help="默认：验证框架，不构建 snapshot",
    )
    mode.add_argument(
        "--execute",
        dest="dry_run",
        action="store_false",
        help="执行 full batch（需 --approve-full-snapshot-batch）",
    )
    parser.add_argument(
        "--approve-full-snapshot-batch",
        action="store_true",
        help="显式批准 863 snapshot full batch 执行",
    )
    parser.add_argument(
        "--universe-file",
        default=UNIVERSE_YAML,
        help="universe YAML 路径",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="跳过 status 中已终态公司",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="忽略 resume 跳过，重建全部",
    )
    args = parser.parse_args()

    if args.dry_run:
        result = run_dry_run(
            universe_path=args.universe_file,
            resume=args.resume,
            force=args.force,
        )
        v = result["validation"]
        print(f"mode: dry-run")
        print(f"universe_ok: {result['universe_ok']}")
        print(f"company_count: {v['company_count']}")
        print(f"hold_overlap: {v['hold_overlap_count']}")
        print(f"status_csv: {STATUS_CSV}")
        print(f"error_csv: {ERROR_CSV}")
        print(f"dryrun_report: {DRYRUN_REPORT_CSV}")
        print(f"dryrun_summary: {DRYRUN_SUMMARY_MD}")
        print(f"snapshot_batch_dryrun_gate: {result['gate']}")
        return 0 if result["universe_ok"] else 1

    enforce_execute_approval(args)

    companies, _ = load_universe_yaml(args.universe_file)
    hold_codes = load_hold_codes(HOLD_YAML)
    ok, validation = validate_universe(companies, hold_codes)
    validation["ok"] = ok
    if not ok:
        print(f"universe validation failed: {validation}", file=sys.stderr)
        return 1

    execution_list = build_execution_list(companies)
    existing = read_status_csv(STATUS_CSV)
    if existing and args.resume:
        status_by_code = existing
        init_rows = list(existing.values())
    else:
        init_rows = init_status_rows(execution_list)
        status_by_code = {r["company_code"]: r for r in init_rows}

    targets = filter_resume_targets(execution_list, status_by_code, force=args.force)
    mapping = _load_mapping()
    errors, success, failed = run_execute_batch(
        targets,
        mapping,
        status_by_code,
        write_json=True,
    )
    write_status_csv(list(status_by_code.values()))
    write_error_csv(errors)
    print(f"mode: execute")
    print(f"success: {success}")
    print(f"failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
