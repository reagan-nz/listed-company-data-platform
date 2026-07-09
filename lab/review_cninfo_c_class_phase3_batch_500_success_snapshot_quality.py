#!/usr/bin/env python3
"""
CNINFO C-class Phase 3 Batch 500 Success-Subset Snapshot Quality Review（Era C Phase 4）。

离线只读 phase3_batch_500_001_success snapshot JSON 做 QA 分析。
允许重写 quality/company_snapshot_status.csv（QA 追踪产物）。
不修改 snapshot JSON · normalized · field_inventory · 不请求 CNINFO。

Usage:
    python lab/review_cninfo_c_class_phase3_batch_500_success_snapshot_quality.py
"""

from __future__ import annotations

import csv
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from build_cninfo_c_class_company_snapshot import SNAPSHOT_MODULES  # noqa: E402
from review_cninfo_c_class_snapshot_full_quality import (  # noqa: E402
    BASE_DIR,
    MODULE_MISSING_REASONS,
    detect_quality_flags,
    load_field_mapping,
    load_snapshot,
    list_snapshot_json_paths,
    write_csv,
)

PHASE3_SNAPSHOT_DIR = os.path.join(
    BASE_DIR, "outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success"
)
FULL_SNAPSHOT_DIR = os.path.join(
    BASE_DIR, "outputs/snapshot/cninfo_c_class/full"
)
PHASE2_SNAPSHOT_DIR = os.path.join(
    BASE_DIR, "outputs/snapshot/cninfo_c_class/phase2_smoke_188"
)
STATUS_CSV = os.path.join(
    PHASE3_SNAPSHOT_DIR, "quality/company_snapshot_status.csv"
)

COMPLETENESS_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_completeness_report.csv",
)
MODULE_COVERAGE_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_module_coverage.csv",
)
QUALITY_FLAGS_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_quality_flags.csv",
)
QA_SUMMARY_MD = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_qa_summary.md",
)

EXPECTED_COMPANY_COUNT = 491
EXPECTED_FULL_SNAPSHOT_COUNT = 863
EXPECTED_PHASE2_SNAPSHOT_COUNT = 188

EXCLUDED_CODES = frozenset({
    "600102", "600270", "600317", "600625", "600627",
    "600705", "600840", "601028", "601989",
})

COMPLETENESS_FIELDS = [
    "company_code",
    "company_name",
    "snapshot_status",
    "available_module_count",
    "partial_module_count",
    "not_available_module_count",
    "missing_module_count",
    "quality_flag_count",
    "notes",
]

MODULE_COVERAGE_FIELDS = [
    "module_name",
    "available_count",
    "partial_count",
    "not_available_count",
    "missing_count",
    "module_gate",
    "notes",
]

QUALITY_FLAG_FIELDS = [
    "company_code",
    "company_name",
    "module_name",
    "flag_type",
    "severity",
    "field_name",
    "notes",
]

STATUS_FIELDS = [
    "company_code",
    "company_name",
    "status",
    "snapshot_status",
    "file_exists",
    "qa_review_status",
    "built_at",
    "finished_at",
    "module_available_count",
    "module_partial_count",
    "module_missing_count",
    "error_count",
    "last_error",
    "retry_status",
]

EXPECTED_PARTIAL_MODULES = frozenset({
    "shareholder_profile",
    "capital_action_profile",
    "risk_profile",
    "market_behavior",
    "investor_relation",
    "dividend_profile",
    "executive_profile",
    "financial_snapshot",
    "industry_profile",
    "event_timeline",
})

EXPECTED_NOT_AVAILABLE_MODULES = frozenset({
    "technology_profile",
})


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def count_module_statuses(snap: Dict[str, Any]) -> Tuple[int, int, int, int]:
    """统计单公司模块状态计数。"""
    modules = snap.get("modules") or {}
    avail = partial = not_avail = missing = 0
    for mod in SNAPSHOT_MODULES:
        module = modules.get(mod)
        if module is None:
            missing += 1
            continue
        st = module.get("status", "missing")
        if st == "available":
            avail += 1
        elif st == "partial":
            partial += 1
        elif st in {"not_available", "missing"}:
            not_avail += 1
        else:
            missing += 1
    return avail, partial, not_avail, missing


def load_all_valid_snapshots(
    snapshot_dir: str = PHASE3_SNAPSHOT_DIR,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    """加载全部有效 snapshot，并返回完整性统计。"""
    paths = list_snapshot_json_paths(snapshot_dir)
    path_by_code = {os.path.basename(p)[:-5]: p for p in paths}
    snapshots: Dict[str, Dict[str, Any]] = {}
    stats = {
        "json_count": len(paths),
        "valid_json_count": 0,
        "invalid_json_count": 0,
        "empty_json_count": 0,
        "malformed_json_count": 0,
        "duplicate_company_code_count": 0,
        "excluded_code_present_count": 0,
        "excluded_codes_present": [],
        "full_snapshot_json_count": 0,
        "phase2_snapshot_json_count": 0,
    }

    if len(path_by_code) != len(paths):
        stats["duplicate_company_code_count"] = len(paths) - len(path_by_code)

    for code in sorted(EXCLUDED_CODES):
        if code in path_by_code:
            stats["excluded_code_present_count"] += 1
            stats["excluded_codes_present"].append(code)

    for path in paths:
        code = os.path.basename(path)[:-5]
        snap, err = load_snapshot(path)
        if err == "empty_file":
            stats["empty_json_count"] += 1
            stats["invalid_json_count"] += 1
        elif err:
            stats["malformed_json_count"] += 1
            stats["invalid_json_count"] += 1
        elif snap:
            stats["valid_json_count"] += 1
            snapshots[code] = snap

    if os.path.isdir(FULL_SNAPSHOT_DIR):
        stats["full_snapshot_json_count"] = len(list_snapshot_json_paths(FULL_SNAPSHOT_DIR))
    if os.path.isdir(PHASE2_SNAPSHOT_DIR):
        stats["phase2_snapshot_json_count"] = len(list_snapshot_json_paths(PHASE2_SNAPSHOT_DIR))

    return snapshots, stats


def build_completeness_rows(
    snapshots: Dict[str, Dict[str, Any]],
    flag_count_by_code: Dict[str, int],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for code in sorted(snapshots.keys()):
        snap = snapshots[code]
        avail, partial, not_avail, missing = count_module_statuses(snap)
        notes = ""
        if missing > 0:
            notes = f"missing_modules={missing}"
        rows.append({
            "company_code": code,
            "company_name": str(snap.get("company_name") or ""),
            "snapshot_status": str(snap.get("snapshot_status") or ""),
            "available_module_count": str(avail),
            "partial_module_count": str(partial),
            "not_available_module_count": str(not_avail),
            "missing_module_count": str(missing),
            "quality_flag_count": str(flag_count_by_code.get(code, 0)),
            "notes": notes,
        })
    return rows


def derive_module_gate(
    module_name: str,
    available: int,
    partial: int,
    not_available: int,
    missing: int,
    total: int,
) -> Tuple[str, str]:
    """根据 863 / Phase2 QA 模式推导模块 gate。"""
    if missing > 0:
        return "FAIL", f"missing_in_{missing}_snapshots"
    if module_name in EXPECTED_NOT_AVAILABLE_MODULES:
        if not_available == total:
            return "PASS_WITH_CAVEAT", MODULE_MISSING_REASONS.get(module_name, "expected_not_available")
        return "FAIL", "unexpected_availability_pattern"
    if module_name in EXPECTED_PARTIAL_MODULES:
        if partial > 0 or available > 0:
            return "PASS_WITH_CAVEAT", MODULE_MISSING_REASONS.get(module_name, "expected_partial_mix")
        return "FAIL", "unexpected_all_not_available"
    if available == total:
        return "PASS", ""
    if partial > 0 or not_available > 0:
        return "PASS_WITH_CAVEAT", "partial_or_sparse_expected"
    return "FAIL", "unexpected_coverage"


def build_module_coverage_rows(
    snapshots: Dict[str, Dict[str, Any]],
) -> List[Dict[str, str]]:
    total = len(snapshots)
    counts: Dict[str, Counter] = {m: Counter() for m in SNAPSHOT_MODULES}

    for snap in snapshots.values():
        modules = snap.get("modules") or {}
        for mod in SNAPSHOT_MODULES:
            module = modules.get(mod)
            if module is None:
                counts[mod]["missing"] += 1
            else:
                st = module.get("status", "missing")
                counts[mod][st] += 1

    rows: List[Dict[str, str]] = []
    for mod in SNAPSHOT_MODULES:
        c = counts[mod]
        avail = c.get("available", 0)
        partial = c.get("partial", 0)
        not_avail = c.get("not_available", 0)
        missing = c.get("missing", 0)
        gate, notes = derive_module_gate(mod, avail, partial, not_avail, missing, total)
        rows.append({
            "module_name": mod,
            "available_count": str(avail),
            "partial_count": str(partial),
            "not_available_count": str(not_avail),
            "missing_count": str(missing),
            "module_gate": gate,
            "notes": notes,
        })
    return rows


def adapt_quality_flag_rows(
    snapshots: Dict[str, Dict[str, Any]],
    raw_flags: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for flag in raw_flags:
        code = flag["company_code"]
        snap = snapshots.get(code, {})
        detail = flag.get("flag_detail", "")
        field_name = ""
        if flag["flag_type"] == "field_missing" and "field missing:" in detail:
            field_name = detail.split("field missing:", 1)[-1].strip()
        rows.append({
            "company_code": code,
            "company_name": str(snap.get("company_name") or ""),
            "module_name": flag.get("module", ""),
            "flag_type": flag.get("flag_type", ""),
            "severity": flag.get("severity", ""),
            "field_name": field_name,
            "notes": detail,
        })
    return rows


def regenerate_status_csv(
    snapshots: Dict[str, Dict[str, Any]],
    path: str = STATUS_CSV,
) -> List[Dict[str, str]]:
    """从实际 JSON 输出重写 status 追踪文件。"""
    now = _now_iso()
    rows: List[Dict[str, str]] = []
    for code in sorted(snapshots.keys()):
        snap = snapshots[code]
        avail, partial, not_avail, missing = count_module_statuses(snap)
        snapshot_status = str(snap.get("snapshot_status") or "complete_with_caveat")
        if snapshot_status == "complete":
            status = "complete"
        elif snapshot_status == "failed":
            status = "failed"
        elif snapshot_status == "partial":
            status = "partial"
        else:
            status = "complete_with_caveat"
        rows.append({
            "company_code": code,
            "company_name": str(snap.get("company_name") or ""),
            "status": status,
            "snapshot_status": snapshot_status,
            "file_exists": "true",
            "qa_review_status": "reviewed",
            "built_at": str(snap.get("built_at") or ""),
            "finished_at": now,
            "module_available_count": str(avail),
            "module_partial_count": str(partial),
            "module_missing_count": str(not_avail + missing),
            "error_count": "0",
            "last_error": "",
            "retry_status": "done",
        })

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=STATUS_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def snapshot_status_distribution(
    snapshots: Dict[str, Dict[str, Any]],
) -> Counter:
    return Counter(str(s.get("snapshot_status") or "unknown") for s in snapshots.values())


def derive_qa_gate(stats: Dict[str, Any]) -> str:
    if (
        stats["json_count"] == EXPECTED_COMPANY_COUNT
        and stats["valid_json_count"] == EXPECTED_COMPANY_COUNT
        and stats["invalid_json_count"] == 0
        and stats["duplicate_company_code_count"] == 0
        and stats["excluded_code_present_count"] == 0
        and stats.get("full_snapshot_json_count", 0) == EXPECTED_FULL_SNAPSHOT_COUNT
        and stats.get("phase2_snapshot_json_count", 0) == EXPECTED_PHASE2_SNAPSHOT_COUNT
    ):
        return "PASS_WITH_CAVEAT"
    return "FAIL"


def write_qa_summary(
    stats: Dict[str, Any],
    status_dist: Counter,
    module_rows: List[Dict[str, str]],
    flag_rows: List[Dict[str, str]],
    gate: str,
    path: str = QA_SUMMARY_MD,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    flag_by_severity = Counter(r["severity"] for r in flag_rows)
    flag_by_type = Counter(r["flag_type"] for r in flag_rows)

    lines = [
        "# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot QA Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 snapshot QA review。**无 CNINFO** · **无 harvest rerun** · **无 snapshot rebuild**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "# Snapshot QA Result",
        "",
        f"json_count: **{stats['json_count']}**",
        "",
        f"valid_json_count: **{stats['valid_json_count']}**",
        "",
        f"invalid_json_count: **{stats['invalid_json_count']}**",
        "",
        f"duplicate_company_code_count: **{stats['duplicate_company_code_count']}**",
        "",
        f"excluded_code_present_count: **{stats['excluded_code_present_count']}**",
        "",
        "# Snapshot Status Distribution",
        "",
        f"- complete: **{status_dist.get('complete', 0)}**",
        f"- complete_with_caveat: **{status_dist.get('complete_with_caveat', 0)}**",
        f"- partial: **{status_dist.get('partial', 0)}**",
        f"- failed: **{status_dist.get('failed', 0)}**",
        "",
        "# Module Coverage",
        "",
        "与 863 full / Phase2 smoke 188 模式一致：`technology_profile` 预期 `not_available`；"
        "`shareholder_profile` / `capital_action_profile` / `risk_profile` / `market_behavior` / "
        "`investor_relation` 等多为 `partial` 或 `available` 混合；核心 identity / securities / "
        "business 模块预期 `available`。",
        "",
        "| module | available | partial | not_available | missing | gate |",
        "|--------|-----------|---------|---------------|---------|------|",
    ]
    for row in module_rows:
        lines.append(
            f"| {row['module_name']} | {row['available_count']} | {row['partial_count']} | "
            f"{row['not_available_count']} | {row['missing_count']} | {row['module_gate']} |"
        )

    lines.extend([
        "",
        "# Quality Flags",
        "",
        "## By severity",
        "",
        "| severity | count |",
        "|----------|-------|",
    ])
    for sev, count in flag_by_severity.most_common():
        lines.append(f"| {sev} | **{count}** |")

    lines.extend([
        "",
        "## By flag_type",
        "",
        "| flag_type | count |",
        "|-----------|-------|",
    ])
    for ft, count in flag_by_type.most_common(15):
        lines.append(f"| {ft} | **{count}** |")

    lines.extend([
        "",
        "# Status Tracking Correction",
        "",
        "`outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/quality/company_snapshot_status.csv` "
        "原为 dry-run 遗留（全部 `pending`）。本轮 QA 已从实际 JSON 输出重写：",
        "",
        f"- 行数: **{stats['valid_json_count']}**",
        "- `file_exists=true`",
        "- `qa_review_status=reviewed`",
        "- `snapshot_status` 取自各 JSON",
        "- `retry_status=done`",
        "",
        "# Output Isolation",
        "",
        f"- phase3 snapshot dir: `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/`",
        f"- full snapshot dir JSON count: **{stats.get('full_snapshot_json_count', 0)}**（未写入）",
        f"- phase2 snapshot dir JSON count: **{stats.get('phase2_snapshot_json_count', 0)}**（未写入）",
        "- CNINFO calls: **0**",
        "- harvest rerun: **none**",
        "",
        "# Gate",
        "",
        "```",
        f"phase3_batch_500_success_snapshot_qa_gate = {gate}",
        "```",
        "",
        "# Next Step",
        "",
        "Recommend: **Phase 3 closure review**.",
        "",
        "Do **not** recommend Phase 4 / full expansion until closure review is complete.",
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO · 未 live · 未重跑 harvest · 未 rebuild snapshot",
        "- snapshot JSON / raw / normalized / field_inventory **未修改**（仅 status CSV 校正）",
        "- 未入库 / MinIO / RAG / registry / verified",
    ])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def run_phase3_success_snapshot_quality_review(
    snapshot_dir: str = PHASE3_SNAPSHOT_DIR,
) -> Dict[str, Any]:
    """执行 Phase 3 success-subset snapshot QA review 流水线。"""
    mapping_rows = load_field_mapping()
    snapshots, stats = load_all_valid_snapshots(snapshot_dir)

    raw_flags = detect_quality_flags(snapshots, mapping_rows)
    flag_rows = adapt_quality_flag_rows(snapshots, raw_flags)
    flag_count_by_code = Counter(r["company_code"] for r in flag_rows)

    completeness_rows = build_completeness_rows(snapshots, flag_count_by_code)
    module_rows = build_module_coverage_rows(snapshots)
    status_rows = regenerate_status_csv(snapshots)
    status_dist = snapshot_status_distribution(snapshots)
    gate = derive_qa_gate(stats)

    write_csv(COMPLETENESS_CSV, COMPLETENESS_FIELDS, completeness_rows)
    write_csv(MODULE_COVERAGE_CSV, MODULE_COVERAGE_FIELDS, module_rows)
    write_csv(QUALITY_FLAGS_CSV, QUALITY_FLAG_FIELDS, flag_rows)
    write_qa_summary(stats, status_dist, module_rows, flag_rows, gate)

    return {
        "stats": stats,
        "snapshots": snapshots,
        "completeness_rows": completeness_rows,
        "module_rows": module_rows,
        "flag_rows": flag_rows,
        "status_rows": status_rows,
        "status_dist": status_dist,
        "gate": gate,
    }


def main() -> int:
    result = run_phase3_success_snapshot_quality_review()
    stats = result["stats"]
    print(f"json_count: {stats['json_count']}")
    print(f"valid_json_count: {stats['valid_json_count']}")
    print(f"invalid_json_count: {stats['invalid_json_count']}")
    print(f"excluded_code_present_count: {stats['excluded_code_present_count']}")
    print(f"quality_flags: {len(result['flag_rows'])}")
    print(f"completeness_report: {COMPLETENESS_CSV}")
    print(f"module_coverage: {MODULE_COVERAGE_CSV}")
    print(f"quality_flags_csv: {QUALITY_FLAGS_CSV}")
    print(f"qa_summary: {QA_SUMMARY_MD}")
    print(f"status_csv: {STATUS_CSV}")
    print(f"phase3_batch_500_success_snapshot_qa_gate: {result['gate']}")
    return 0 if result["gate"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
