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
    configure_snapshot_harvest_root,
    reset_snapshot_harvest_root,
    _load_mapping,
)

BASE_DIR = os.path.dirname(_LAB_DIR)

UNIVERSE_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
HOLD_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml")

DEFAULT_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class"
DEFAULT_OUTPUT_DIR_REL = "outputs/snapshot/cninfo_c_class/full"

FULL_OUT_DIR = os.path.join(BASE_DIR, DEFAULT_OUTPUT_DIR_REL)
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
PHASE2_SMOKE_188_SAMPLE_BASENAME = "eval_companies_c_class_phase2_smoke_188_snapshot.yaml"
PHASE2_SMOKE_188_EXPECTED_COUNT = 188
PHASE2_SMOKE_188_APPROVAL_REQUIRED = "PHASE2_SMOKE_188_SNAPSHOT_APPROVAL_REQUIRED"
PHASE2_SNAPSHOT_OUTPUT_ROOT_REL = "outputs/snapshot/cninfo_c_class/phase2_smoke_188"

PHASE3_SUCCESS_SNAPSHOT_SAMPLE_BASENAME = (
    "eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml"
)
PHASE3_SUCCESS_SNAPSHOT_EXPECTED_COUNT = 491
PHASE3_SUCCESS_SNAPSHOT_OUTPUT_ROOT_REL = (
    "outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success"
)
PHASE3_SUCCESS_SNAPSHOT_HARVEST_ROOT_REL = (
    "outputs/harvest/cninfo_c_class/phase3_batch_500_001"
)
PHASE3_SUCCESS_SNAPSHOT_APPROVAL_REQUIRED = "PHASE3_SUCCESS_SNAPSHOT_APPROVAL_REQUIRED"
PHASE3_FULL_SNAPSHOT_APPROVAL_REJECTED = "PHASE3_FULL_SNAPSHOT_APPROVAL_REJECTED"
PHASE3_OUTPUT_ROOT_MISMATCH = "PHASE3_OUTPUT_ROOT_MISMATCH"
PHASE3_UNIVERSE_COUNT_MISMATCH = "PHASE3_UNIVERSE_COUNT_MISMATCH"
PHASE3_EXCLUDED_CODES_PRESENT = "PHASE3_EXCLUDED_CODES_PRESENT"
PHASE3_FULL_SNAPSHOT_ISOLATION_VIOLATION = "PHASE3_FULL_SNAPSHOT_ISOLATION_VIOLATION"
PHASE3_PHASE2_SNAPSHOT_ISOLATION_VIOLATION = "PHASE3_PHASE2_SNAPSHOT_ISOLATION_VIOLATION"

PHASE3_EXCLUDED_IDENTITY_CAVEAT_CODES = frozenset({
    "600102", "600270", "600317", "600625", "600627",
    "600705", "600840", "601028", "601989",
})

FULL_SNAPSHOT_OUT_DIR_REL = "outputs/snapshot/cninfo_c_class/full"


def configure_snapshot_batch_paths(
    harvest_root: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> Tuple[str, str]:
    """配置 batch runner 的 harvest 输入根与 snapshot 输出目录。"""
    global FULL_OUT_DIR, QUALITY_DIR, STATUS_CSV, ERROR_CSV
    harvest_abs = configure_snapshot_harvest_root(harvest_root)
    if output_dir:
        out = output_dir.rstrip("/")
        if not os.path.isabs(out):
            out = os.path.join(BASE_DIR, out)
    else:
        out = os.path.join(BASE_DIR, DEFAULT_OUTPUT_DIR_REL)
    FULL_OUT_DIR = out
    QUALITY_DIR = os.path.join(FULL_OUT_DIR, "quality")
    STATUS_CSV = os.path.join(QUALITY_DIR, "company_snapshot_status.csv")
    ERROR_CSV = os.path.join(QUALITY_DIR, "company_snapshot_error.csv")
    return harvest_abs, FULL_OUT_DIR


def reset_snapshot_batch_paths() -> None:
    configure_snapshot_batch_paths(None, None)


def is_phase2_smoke_188_sample(sample_path: str) -> bool:
    norm = sample_path.replace("\\", "/")
    return norm.endswith(PHASE2_SMOKE_188_SAMPLE_BASENAME)


def is_phase3_success_snapshot_sample(sample_path: str) -> bool:
    norm = sample_path.replace("\\", "/")
    return norm.endswith(PHASE3_SUCCESS_SNAPSHOT_SAMPLE_BASENAME)


def is_full_snapshot_universe_sample(sample_path: str) -> bool:
    norm = sample_path.replace("\\", "/")
    return norm.endswith(os.path.basename(UNIVERSE_YAML))


def _norm_abs_path(path: str) -> str:
    return os.path.normpath(path).replace("\\", "/")


def enforce_phase3_success_snapshot_preflight(
    sample_path: str,
    output_dir: str,
    companies: List[Dict[str, str]],
) -> None:
    """Phase 3 success-subset build 前隔离与 universe 校验。"""
    if not is_phase3_success_snapshot_sample(sample_path):
        return

    norm_out = _norm_abs_path(output_dir).rstrip("/")
    expected_out = _norm_abs_path(
        os.path.join(BASE_DIR, PHASE3_SUCCESS_SNAPSHOT_OUTPUT_ROOT_REL)
    ).rstrip("/")
    if norm_out != expected_out:
        print(f"{PHASE3_OUTPUT_ROOT_MISMATCH}: {norm_out}", file=sys.stderr)
        raise SystemExit(2)

    if len(companies) != PHASE3_SUCCESS_SNAPSHOT_EXPECTED_COUNT:
        print(
            f"{PHASE3_UNIVERSE_COUNT_MISMATCH}: {len(companies)}",
            file=sys.stderr,
        )
        raise SystemExit(2)

    codes = {c["company_code"] for c in companies}
    overlap = sorted(codes & PHASE3_EXCLUDED_IDENTITY_CAVEAT_CODES)
    if overlap:
        print(f"{PHASE3_EXCLUDED_CODES_PRESENT}: {overlap}", file=sys.stderr)
        raise SystemExit(2)

    full_dir = _norm_abs_path(os.path.join(BASE_DIR, FULL_SNAPSHOT_OUT_DIR_REL)).rstrip("/")
    phase2_dir = _norm_abs_path(
        os.path.join(BASE_DIR, PHASE2_SNAPSHOT_OUTPUT_ROOT_REL)
    ).rstrip("/")
    if norm_out == full_dir or norm_out.startswith(full_dir + "/"):
        print(PHASE3_FULL_SNAPSHOT_ISOLATION_VIOLATION, file=sys.stderr)
        raise SystemExit(2)
    if norm_out == phase2_dir or norm_out.startswith(phase2_dir + "/"):
        print(PHASE3_PHASE2_SNAPSHOT_ISOLATION_VIOLATION, file=sys.stderr)
        raise SystemExit(2)


def resolve_execute_mode(args: argparse.Namespace, sample_path: str) -> str:
    if sample_path and is_phase2_smoke_188_sample(sample_path):
        if getattr(args, "approve_phase2_smoke_188_snapshot", False):
            return "phase2_smoke_188"
        return ""
    if sample_path and is_phase3_success_snapshot_sample(sample_path):
        if getattr(args, "approve_phase3_success_snapshot_build", False):
            return "phase3_success_snapshot"
        return ""
    if args.approve_full_snapshot_batch:
        if sample_path and (
            is_phase3_success_snapshot_sample(sample_path)
            or is_phase2_smoke_188_sample(sample_path)
        ):
            return ""
        if getattr(args, "approve_phase3_success_snapshot_build", False):
            return ""
        return "full"
    return ""


def enforce_execute_approval(args: argparse.Namespace, sample_path: str) -> str:
    if sample_path and is_phase3_success_snapshot_sample(sample_path):
        if args.approve_full_snapshot_batch:
            print(PHASE3_FULL_SNAPSHOT_APPROVAL_REJECTED, file=sys.stderr)
            raise SystemExit(2)
    if sample_path and is_full_snapshot_universe_sample(sample_path):
        if getattr(args, "approve_phase3_success_snapshot_build", False):
            print(FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED, file=sys.stderr)
            raise SystemExit(2)

    mode = resolve_execute_mode(args, sample_path)
    if not mode:
        if sample_path and is_phase2_smoke_188_sample(sample_path):
            print(PHASE2_SMOKE_188_APPROVAL_REQUIRED, file=sys.stderr)
        elif sample_path and is_phase3_success_snapshot_sample(sample_path):
            print(PHASE3_SUCCESS_SNAPSHOT_APPROVAL_REQUIRED, file=sys.stderr)
        else:
            print(FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED, file=sys.stderr)
        raise SystemExit(2)
    return mode

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
    """加载 snapshot universe YAML。"""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    companies: List[Dict[str, str]] = []
    for item in data.get("companies", []):
        raw_code = item.get("stock_code") or item.get("company_code")
        companies.append({
            "company_code": _normalize_code(raw_code),
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
    expected_count: Optional[int] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """校验 universe 规模与 hold 无重叠。"""
    if expected_count is None:
        expected_count = EXPECTED_COMPANY_COUNT
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


def planned_snapshot_path(company_code: str, out_dir: Optional[str] = None) -> str:
    effective = out_dir or FULL_OUT_DIR
    return os.path.join(effective, f"{_normalize_code(company_code)}.json")


def build_execution_list(
    companies: List[Dict[str, str]],
    out_dir: Optional[str] = None,
) -> List[Dict[str, str]]:
    """生成 batch 执行清单（dry-run / execute 共用）。"""
    effective = out_dir or FULL_OUT_DIR
    rows: List[Dict[str, str]] = []
    for item in companies:
        code = item["company_code"]
        rows.append({
            "company_code": code,
            "company_name": item["company_name"],
            "board": item["board"],
            "snapshot_status": "pending",
            "planned_output_path": planned_snapshot_path(code, effective),
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
    out_dir: Optional[str] = None,
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
    effective_out_dir = out_dir or FULL_OUT_DIR
    os.makedirs(effective_out_dir, exist_ok=True)

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
            out_path = planned_snapshot_path(code, effective_out_dir)
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
    out_dir: Optional[str] = None,
    quality_dir: Optional[str] = None,
    expected_company_count: Optional[int] = None,
) -> str:
    """写入 dry-run summary；返回 gate。"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    gate = "PASS" if validation["ok"] else "FAIL"
    if gate == "PASS":
        gate = "PASS_WITH_CAVEAT"
    expected = expected_company_count or validation.get("expected_count") or EXPECTED_COMPANY_COUNT
    effective_out_dir = out_dir or FULL_OUT_DIR
    effective_quality_dir = quality_dir or QUALITY_DIR

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
        f"snapshot_path: `{os.path.relpath(effective_out_dir, BASE_DIR)}/{{company_code}}.json`",
        "",
        f"quality_path: `{os.path.relpath(effective_quality_dir, BASE_DIR)}/`",
        "",
        f"planned_modules: **{PLANNED_MODULE_COUNT}**",
        "",
        "# Resume Design",
        "",
        f"- status file: `{os.path.relpath(os.path.join(effective_quality_dir, 'company_snapshot_status.csv'), BASE_DIR)}`",
        f"- terminal statuses: {', '.join(sorted(TERMINAL_STATUSES))}",
        f"- resume skips terminal rows unless `--force`",
        f"- dry-run resume_skipped: **{resume_skipped}**",
        "",
        "# Error Handling",
        "",
        f"- error file: `{os.path.relpath(os.path.join(effective_quality_dir, 'company_snapshot_error.csv'), BASE_DIR)}`",
        "- 单公司 `try/except` 隔离；失败写入 error CSV，继续下一家",
        "- dry-run 仅初始化空 error CSV（header only）",
        "",
        "# Estimated Scale",
        "",
        f"- companies: **{expected}**",
        f"- snapshot JSON: **{expected}**（执行阶段）",
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
    out_dir: Optional[str] = None,
    harvest_root: Optional[str] = None,
    status_path: Optional[str] = None,
    error_path: Optional[str] = None,
    report_path: str = DRYRUN_REPORT_CSV,
    summary_path: str = DRYRUN_SUMMARY_MD,
    resume: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Dry-run：验证输入 · 生成 status/error 框架 · 写 dry-run 报告。
    **不调用 build_snapshot** · **不写 snapshot JSON**。
    """
    configure_snapshot_batch_paths(harvest_root=harvest_root, output_dir=out_dir)
    effective_out_dir = FULL_OUT_DIR
    effective_quality_dir = QUALITY_DIR
    effective_status_path = status_path or STATUS_CSV
    effective_error_path = error_path or ERROR_CSV

    companies, universe_meta = load_universe_yaml(universe_path)
    hold_codes = load_hold_codes(hold_path)
    declared_count = universe_meta.get("company_count")
    expected_count = declared_count if declared_count is not None else len(companies)
    ok, validation = validate_universe(companies, hold_codes, expected_count=expected_count)
    validation["ok"] = ok

    execution_list = build_execution_list(companies, out_dir=effective_out_dir)
    existing_status = read_status_csv(effective_status_path) if resume else {}
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
            build_execution_list(companies, out_dir=effective_out_dir)
        )

    write_status_csv(status_rows, path=effective_status_path)
    write_error_csv([], path=effective_error_path)

    report_rows = build_dryrun_report_rows(
        build_execution_list(companies, out_dir=effective_out_dir)
    )
    write_dryrun_report(report_rows, path=report_path)
    gate = write_dryrun_summary(
        validation,
        universe_meta,
        resume_skipped=resume_skipped,
        path=summary_path,
        out_dir=effective_out_dir,
        quality_dir=effective_quality_dir,
        expected_company_count=expected_count,
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
        help="执行 snapshot batch（需显式批准）",
    )
    parser.add_argument(
        "--approve-full-snapshot-batch",
        action="store_true",
        help="显式批准 863 snapshot full batch 执行",
    )
    parser.add_argument(
        "--approve-phase2-smoke-188-snapshot",
        action="store_true",
        help="显式批准 Phase 2 smoke 188 snapshot batch 执行",
    )
    parser.add_argument(
        "--approve-phase3-success-snapshot-build",
        action="store_true",
        help="显式批准 Phase 3 batch 500 success-subset（491）snapshot build",
    )
    parser.add_argument(
        "--sample-file",
        default=None,
        help="universe YAML 路径（优先于 --universe-file）",
    )
    parser.add_argument(
        "--universe-file",
        default=UNIVERSE_YAML,
        help="universe YAML 路径（兼容旧参数）",
    )
    parser.add_argument(
        "--harvest-root",
        default=None,
        help="harvest 产物根目录（默认 outputs/harvest/cninfo_c_class）",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="snapshot 输出目录（默认 outputs/snapshot/cninfo_c_class/full）",
    )
    parser.add_argument(
        "--output-csv",
        default=None,
        help="dry-run report CSV 路径",
    )
    parser.add_argument(
        "--output-md",
        default=None,
        help="dry-run summary MD 路径",
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

    sample_file = args.sample_file or args.universe_file
    if not os.path.isabs(sample_file):
        sample_file = os.path.join(BASE_DIR, sample_file)

    report_path = args.output_csv or DRYRUN_REPORT_CSV
    summary_path = args.output_md or DRYRUN_SUMMARY_MD
    if not os.path.isabs(report_path):
        report_path = os.path.join(BASE_DIR, report_path)
    if not os.path.isabs(summary_path):
        summary_path = os.path.join(BASE_DIR, summary_path)

    if args.dry_run:
        result = run_dry_run(
            universe_path=sample_file,
            harvest_root=args.harvest_root,
            out_dir=args.output_dir,
            report_path=report_path,
            summary_path=summary_path,
            resume=args.resume,
            force=args.force,
        )
        v = result["validation"]
        print("mode: dry-run")
        print(f"universe_ok: {result['universe_ok']}")
        print(f"company_count: {v['company_count']}")
        print(f"hold_overlap: {v['hold_overlap_count']}")
        print(f"harvest_root: {configure_snapshot_harvest_root(args.harvest_root)}")
        print(f"output_dir: {FULL_OUT_DIR}")
        print(f"status_csv: {STATUS_CSV}")
        print(f"error_csv: {ERROR_CSV}")
        print(f"dryrun_report: {report_path}")
        print(f"dryrun_summary: {summary_path}")
        print(f"snapshot_batch_dryrun_gate: {result['gate']}")
        return 0 if result["universe_ok"] else 1

    enforce_execute_approval(args, sample_file)
    configure_snapshot_batch_paths(harvest_root=args.harvest_root, output_dir=args.output_dir)

    companies, universe_meta = load_universe_yaml(sample_file)
    enforce_phase3_success_snapshot_preflight(sample_file, FULL_OUT_DIR, companies)
    hold_codes = load_hold_codes(HOLD_YAML)
    declared_count = universe_meta.get("company_count")
    expected_count = declared_count if declared_count is not None else len(companies)
    ok, validation = validate_universe(companies, hold_codes, expected_count=expected_count)
    validation["ok"] = ok
    if not ok:
        print(f"universe validation failed: {validation}", file=sys.stderr)
        return 1

    execution_list = build_execution_list(companies, out_dir=FULL_OUT_DIR)
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
        out_dir=FULL_OUT_DIR,
        write_json=True,
    )
    write_status_csv(list(status_by_code.values()))
    write_error_csv(errors)
    print("mode: execute")
    print(f"success: {success}")
    print(f"failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
