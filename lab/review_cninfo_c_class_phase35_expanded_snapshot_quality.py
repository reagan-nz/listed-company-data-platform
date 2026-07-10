#!/usr/bin/env python3
"""
CNINFO C-class Phase 3.5 Expanded Success-Subset Snapshot Quality Review（Era C Phase 4）。

离线只读 phase35 expanded 491 snapshot JSON 做 QA 分析。
允许重写 quality/company_snapshot_status.csv（QA 追踪产物）。
不修改 snapshot JSON · harvest 根 · 不请求 CNINFO。

Usage:
    python lab/review_cninfo_c_class_phase35_expanded_snapshot_quality.py
"""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from build_cninfo_c_class_company_snapshot import SNAPSHOT_MODULES  # noqa: E402
from review_cninfo_c_class_phase3_batch_500_success_snapshot_quality import (  # noqa: E402
    EXPECTED_NOT_AVAILABLE_MODULES,
    EXPECTED_PARTIAL_MODULES,
    MODULE_MISSING_REASONS,
    adapt_quality_flag_rows,
    build_module_coverage_rows,
    count_module_statuses,
    derive_module_gate,
    snapshot_status_distribution,
)
from review_cninfo_c_class_snapshot_full_quality import (  # noqa: E402
    BASE_DIR,
    detect_quality_flags,
    load_field_mapping,
    load_snapshot,
    list_snapshot_json_paths,
    write_csv,
)

PHASE35_SNAPSHOT_DIR = os.path.join(
    BASE_DIR, "outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491"
)
STATUS_CSV = os.path.join(PHASE35_SNAPSHOT_DIR, "quality/company_snapshot_status.csv")

UNIVERSE_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_success_subset_universe.csv"
)
MERGE_MANIFEST_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_snapshot_merge_manifest_design.csv"
)
HOLDOUT_LEDGER_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_holdout_ledger.csv"
)
BUILD_REPORT_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_build_report.csv"
)

QA_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_summary.md"
)
QA_METRICS_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_metrics.csv"
)
QA_CASE_LEDGER_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_case_ledger.csv"
)
QA_HOLDOUT_CONFIRMATION_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_holdout_confirmation.csv"
)

PHASE35_BATCH_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class/phase35_batch_500_001"
PHASE35_RESUME_HARVEST_ROOT_REL = (
    "outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume"
)

EXPECTED_COMPANY_COUNT = 491
EXPECTED_ORIGINAL_COUNT = 463
EXPECTED_RESUME_COUNT = 28
EXPECTED_MANIFEST_ROWS = 4910
C35R016_CODE = "301212"

HOLD_FOR_REVIEW_CODES = frozenset({
    "000003", "000578", "000666", "000689",
    "000861", "000961", "002280", "600220",
})

HOLDBACK_CODES = HOLD_FOR_REVIEW_CODES | {C35R016_CODE}

METRICS_FIELDS = [
    "metric_name",
    "metric_value",
    "notes",
]

CASE_LEDGER_FIELDS = [
    "company_code",
    "company_name",
    "source_root_role",
    "snapshot_candidate_status",
    "caveat_level",
    "qa_outcome",
    "snapshot_status",
    "snapshot_file_exists",
    "available_module_count",
    "partial_module_count",
    "not_available_module_count",
    "missing_module_count",
    "quality_flag_count",
    "merge_manifest_sources_resolved",
    "merge_routing_notes",
    "notes",
]

HOLDOUT_CONFIRMATION_FIELDS = [
    "company_code",
    "company_name",
    "holdout_reason",
    "resume_case_id",
    "resume_qa_classification",
    "snapshot_include",
    "snapshot_json_present",
    "qa_outcome",
    "recommended_next_action",
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _normalize_code(code: str) -> str:
    return str(code).strip().zfill(6)


def _fingerprint_harvest_tree(root_rel: str) -> str:
    h = hashlib.sha256()
    for sub in ("raw", "normalized", "quality"):
        base = os.path.join(BASE_DIR, root_rel, sub)
        if not os.path.isdir(base):
            continue
        for dirpath, _dn, files in os.walk(base):
            for name in sorted(files):
                path = os.path.join(dirpath, name)
                h.update(path.encode())
                with open(path, "rb") as fh:
                    h.update(fh.read())
    return h.hexdigest()


def load_universe_rows(path: str = UNIVERSE_CSV) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out: List[Dict[str, str]] = []
    for row in rows:
        if row.get("snapshot_include", "").strip().lower() != "yes":
            continue
        out.append({
            "company_code": _normalize_code(row["company_code"]),
            "company_name": row.get("company_name", ""),
            "source_root_role": row.get("source_root_role", ""),
            "snapshot_candidate_status": row.get("snapshot_candidate_status", ""),
            "caveat_level": row.get("caveat_level", ""),
            "resume_case_id": row.get("resume_case_id", ""),
        })
    return out


def load_holdout_rows(path: str = HOLDOUT_LEDGER_CSV) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_build_report(path: str = BUILD_REPORT_CSV) -> Dict[str, Dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {_normalize_code(r["company_code"]): r for r in rows}


def load_merge_manifest_summary(
    path: str = MERGE_MANIFEST_CSV,
    universe_rows: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    universe = universe_rows or load_universe_rows()
    role_by_code = {r["company_code"]: r["source_root_role"] for r in universe}
    universe_codes = set(role_by_code.keys())
    resume_rules: Counter = Counter()
    original_rules: Counter = Counter()
    for row in rows:
        code = _normalize_code(row["company_code"])
        if code not in universe_codes:
            continue
        rule = row.get("precedence_rule", "")
        role = role_by_code.get(code, "")
        if role == "resume":
            resume_rules[rule] += 1
        elif role == "original":
            original_rules[rule] += 1
    return {
        "manifest_rows": len(rows),
        "resume_precedence_rules": dict(resume_rules),
        "original_precedence_rules": dict(original_rules),
    }


def load_all_valid_snapshots(
    snapshot_dir: str = PHASE35_SNAPSHOT_DIR,
    excluded_codes: Optional[Set[str]] = None,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    """加载全部有效 snapshot，并返回完整性统计。"""
    excluded = excluded_codes or HOLDBACK_CODES
    paths = list_snapshot_json_paths(snapshot_dir)
    path_by_code = {os.path.basename(p)[:-5]: p for p in paths}
    snapshots: Dict[str, Dict[str, Any]] = {}
    stats: Dict[str, Any] = {
        "json_count": len(paths),
        "valid_json_count": 0,
        "invalid_json_count": 0,
        "empty_json_count": 0,
        "malformed_json_count": 0,
        "duplicate_company_code_count": 0,
        "c35r016_present": False,
        "hold_for_review_present_count": 0,
        "hold_for_review_present": [],
        "excluded_holdout_present_count": 0,
    }

    if len(path_by_code) != len(paths):
        stats["duplicate_company_code_count"] = len(paths) - len(path_by_code)

    snapshot_codes = set(path_by_code.keys())
    if C35R016_CODE in snapshot_codes:
        stats["c35r016_present"] = True
        stats["excluded_holdout_present_count"] += 1

    hold_overlap = sorted(snapshot_codes & HOLD_FOR_REVIEW_CODES)
    if hold_overlap:
        stats["hold_for_review_present_count"] = len(hold_overlap)
        stats["hold_for_review_present"] = hold_overlap
        stats["excluded_holdout_present_count"] += len(hold_overlap)

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

    return snapshots, stats


def classify_company_qa_outcome(
    universe_row: Dict[str, str],
    snap: Optional[Dict[str, Any]],
    flag_count: int,
    build_row: Optional[Dict[str, str]],
) -> Tuple[str, str]:
    """分类单公司 QA outcome。"""
    code = universe_row["company_code"]
    if snap is None:
        return "qa_review_required", "snapshot_json_missing"

    avail, partial, not_avail, missing = count_module_statuses(snap)
    if missing > 0:
        return "qa_review_required", f"missing_modules={missing}"

    merge_resolved = int(build_row.get("merge_manifest_sources_resolved", "0") or "0") if build_row else 0
    if merge_resolved < 10:
        return "qa_review_required", f"merge_sources_resolved={merge_resolved}"

    caveat_level = universe_row.get("caveat_level", "none")
    candidate_status = universe_row.get("snapshot_candidate_status", "")
    routing_notes = ""
    if universe_row.get("source_root_role") == "resume":
        routing_notes = "resume_merged; merge_manifest_primary/fallback routing applied"

    if flag_count > 0 or caveat_level not in {"", "none"} or candidate_status == "included_with_caveat":
        notes = routing_notes or "documented_caveat_or_quality_flags"
        return "qa_ok_with_caveat", notes

    if str(snap.get("snapshot_status", "")) == "complete_with_caveat":
        return "qa_ok_with_caveat", routing_notes or "complete_with_caveat_expected"

    return "qa_ok", routing_notes or "snapshot_complete"


def build_case_ledger_rows(
    universe_rows: List[Dict[str, str]],
    snapshots: Dict[str, Dict[str, Any]],
    flag_count_by_code: Dict[str, int],
    build_report: Dict[str, Dict[str, str]],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for urow in sorted(universe_rows, key=lambda r: r["company_code"]):
        code = urow["company_code"]
        snap = snapshots.get(code)
        build_row = build_report.get(code)
        outcome, notes = classify_company_qa_outcome(
            urow, snap, flag_count_by_code.get(code, 0), build_row,
        )
        if snap:
            avail, partial, not_avail, missing = count_module_statuses(snap)
        else:
            avail = partial = not_avail = missing = 0
        rows.append({
            "company_code": code,
            "company_name": urow.get("company_name", ""),
            "source_root_role": urow.get("source_root_role", ""),
            "snapshot_candidate_status": urow.get("snapshot_candidate_status", ""),
            "caveat_level": urow.get("caveat_level", ""),
            "qa_outcome": outcome,
            "snapshot_status": str(snap.get("snapshot_status", "")) if snap else "",
            "snapshot_file_exists": "true" if snap else "false",
            "available_module_count": str(avail),
            "partial_module_count": str(partial),
            "not_available_module_count": str(not_avail),
            "missing_module_count": str(missing),
            "quality_flag_count": str(flag_count_by_code.get(code, 0)),
            "merge_manifest_sources_resolved": (
                build_row.get("merge_manifest_sources_resolved", "") if build_row else ""
            ),
            "merge_routing_notes": notes if urow.get("source_root_role") == "resume" else "",
            "notes": notes,
        })
    return rows


def build_holdout_confirmation_rows(
    holdout_rows: List[Dict[str, str]],
    snapshot_codes: Set[str],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for row in holdout_rows:
        code = _normalize_code(row["company_code"])
        present = code in snapshot_codes
        classification = row.get("resume_qa_classification", "")
        if classification == "still_partial" or code == C35R016_CODE:
            outcome = "excluded_holdout_confirmed"
            notes = "C35R016 not promoted; still_partial holdout"
        elif classification == "hold_for_review":
            outcome = "excluded_holdout_confirmed"
            notes = "hold_for_review excluded; not silently promoted"
        else:
            outcome = "excluded_holdout_confirmed"
            notes = row.get("notes", "holdout_excluded")
        rows.append({
            "company_code": code,
            "company_name": row.get("company_name", ""),
            "holdout_reason": row.get("holdout_reason", ""),
            "resume_case_id": row.get("resume_case_id", ""),
            "resume_qa_classification": classification,
            "snapshot_include": row.get("snapshot_include", "no"),
            "snapshot_json_present": "true" if present else "false",
            "qa_outcome": outcome,
            "recommended_next_action": row.get("recommended_next_action", ""),
            "notes": notes,
        })
    return rows


def build_metrics_rows(
    stats: Dict[str, Any],
    universe_rows: List[Dict[str, str]],
    case_rows: List[Dict[str, str]],
    holdout_rows: List[Dict[str, str]],
    module_rows: List[Dict[str, str]],
    flag_rows: List[Dict[str, str]],
    manifest_summary: Dict[str, Any],
    harvest_unchanged: bool,
) -> List[Dict[str, str]]:
    outcome_counts = Counter(r["qa_outcome"] for r in case_rows)
    original_n = sum(1 for r in universe_rows if r["source_root_role"] == "original")
    resume_n = sum(1 for r in universe_rows if r["source_root_role"] == "resume")
    status_dist = Counter(r["snapshot_status"] for r in case_rows if r["snapshot_file_exists"] == "true")

    metrics: List[Tuple[str, str, str]] = [
        ("snapshot_json_count", str(stats["json_count"]), "under expanded output root"),
        ("valid_json_count", str(stats["valid_json_count"]), ""),
        ("invalid_json_count", str(stats["invalid_json_count"]), ""),
        ("universe_company_count", str(len(universe_rows)), "expected 491"),
        ("universe_original_count", str(original_n), "expected 463"),
        ("universe_resume_count", str(resume_n), "expected 28"),
        ("universe_coverage_pct", f"{100.0 * stats['valid_json_count'] / EXPECTED_COMPANY_COUNT:.1f}", ""),
        ("c35r016_present", str(stats["c35r016_present"]).lower(), "must be false"),
        ("hold_for_review_present_count", str(stats["hold_for_review_present_count"]), "must be 0"),
        ("holdout_ledger_rows", str(len(holdout_rows)), "expected 9"),
        ("holdout_all_excluded_confirmed", str(all(
            r["snapshot_json_present"] == "false"
            for r in build_holdout_confirmation_rows(holdout_rows, {
                r["company_code"] for r in case_rows if r["snapshot_file_exists"] == "true"
            })
        )).lower(), ""),
        ("merge_manifest_rows", str(manifest_summary.get("manifest_rows", 0)), "expected 4910"),
        ("qa_ok_count", str(outcome_counts.get("qa_ok", 0)), ""),
        ("qa_ok_with_caveat_count", str(outcome_counts.get("qa_ok_with_caveat", 0)), ""),
        ("qa_review_required_count", str(outcome_counts.get("qa_review_required", 0)), ""),
        ("excluded_holdout_confirmed_count", str(len(holdout_rows)), ""),
        ("quality_flag_total", str(len(flag_rows)), ""),
        ("snapshot_complete_with_caveat", str(status_dist.get("complete_with_caveat", 0)), ""),
        ("harvest_roots_unchanged", str(harvest_unchanged).lower(), ""),
        ("cninfo_calls", "0", "offline QA only"),
        ("db_writes", "0", ""),
        ("minio_writes", "0", ""),
        ("rag_runs", "0", ""),
    ]
    for mod_row in module_rows:
        metrics.append((
            f"module_{mod_row['module_name']}_gate",
            mod_row["module_gate"],
            mod_row.get("notes", ""),
        ))
    return [
        {"metric_name": n, "metric_value": v, "notes": note}
        for n, v, note in metrics
    ]


def derive_qa_gate(
    stats: Dict[str, Any],
    universe_rows: List[Dict[str, str]],
    case_rows: List[Dict[str, str]],
    holdout_confirm_rows: List[Dict[str, str]],
) -> str:
    review_required = sum(1 for r in case_rows if r["qa_outcome"] == "qa_review_required")
    universe_codes = {r["company_code"] for r in universe_rows}
    snapshot_codes = {
        r["company_code"] for r in case_rows if r["snapshot_file_exists"] == "true"
    }
    original_n = sum(1 for r in universe_rows if r["source_root_role"] == "original")
    resume_n = sum(1 for r in universe_rows if r["source_root_role"] == "resume")

    material_defect = (
        stats["json_count"] != EXPECTED_COMPANY_COUNT
        or stats["valid_json_count"] != EXPECTED_COMPANY_COUNT
        or stats["invalid_json_count"] > 0
        or stats["duplicate_company_code_count"] > 0
        or stats["c35r016_present"]
        or stats["hold_for_review_present_count"] > 0
        or len(universe_rows) != EXPECTED_COMPANY_COUNT
        or original_n != EXPECTED_ORIGINAL_COUNT
        or resume_n != EXPECTED_RESUME_COUNT
        or universe_codes != snapshot_codes
        or review_required > 0
        or any(r["snapshot_json_present"] == "true" for r in holdout_confirm_rows)
    )
    if material_defect:
        return "FAIL_REVIEW_REQUIRED"
    return "PASS_WITH_CAVEAT"


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
        status = (
            "complete" if snapshot_status == "complete"
            else "failed" if snapshot_status == "failed"
            else "partial" if snapshot_status == "partial"
            else "complete_with_caveat"
        )
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


def write_qa_summary(
    stats: Dict[str, Any],
    universe_rows: List[Dict[str, str]],
    case_rows: List[Dict[str, str]],
    holdout_rows: List[Dict[str, str]],
    module_rows: List[Dict[str, str]],
    flag_rows: List[Dict[str, str]],
    manifest_summary: Dict[str, Any],
    gate: str,
    harvest_unchanged: bool,
    path: str = QA_SUMMARY_MD,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    outcome_counts = Counter(r["qa_outcome"] for r in case_rows)
    status_dist = snapshot_status_distribution({
        r["company_code"]: {"snapshot_status": r["snapshot_status"]}
        for r in case_rows if r["snapshot_file_exists"] == "true"
    })
    original_n = sum(1 for r in universe_rows if r["source_root_role"] == "original")
    resume_n = sum(1 for r in universe_rows if r["source_root_role"] == "resume")

    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot QA Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 expanded snapshot QA review。**无 CNINFO** · **无 harvest rerun** · **无 snapshot rebuild**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "# Snapshot QA Result",
        "",
        f"- **json_count:** **{stats['json_count']}**",
        f"- **valid_json_count:** **{stats['valid_json_count']}**",
        f"- **invalid_json_count:** **{stats['invalid_json_count']}**",
        f"- **duplicate_company_code_count:** **{stats['duplicate_company_code_count']}**",
        "",
        "# Universe",
        "",
        f"- **universe_count:** **{len(universe_rows)}**",
        f"- **original:** **{original_n}**",
        f"- **resume merged:** **{resume_n}**",
        "",
        "# Exclusions",
        "",
        f"- **C35R016 / 301212 present:** **{stats['c35r016_present']}**",
        f"- **hold_for_review present:** **{stats['hold_for_review_present_count']}**",
        f"- **holdout ledger rows:** **{len(holdout_rows)}** (all `excluded_holdout_confirmed`)",
        "",
        "# QA Outcome Buckets",
        "",
        f"- **qa_ok:** **{outcome_counts.get('qa_ok', 0)}**",
        f"- **qa_ok_with_caveat:** **{outcome_counts.get('qa_ok_with_caveat', 0)}**",
        f"- **qa_review_required:** **{outcome_counts.get('qa_review_required', 0)}**",
        f"- **excluded_holdout_confirmed:** **{len(holdout_rows)}**",
        "",
        "# Snapshot Status Distribution",
        "",
        f"- complete_with_caveat: **{status_dist.get('complete_with_caveat', 0)}**",
        f"- complete: **{status_dist.get('complete', 0)}**",
        f"- partial: **{status_dist.get('partial', 0)}**",
        f"- failed: **{status_dist.get('failed', 0)}**",
        "",
        "# Merge-Manifest Routing",
        "",
        f"- **manifest_rows:** **{manifest_summary.get('manifest_rows', 0)}**",
        "- resume companies: retried sources from resume root; non-retried from original root",
        "- original companies: all sources from original root",
        f"- resume precedence rules sample: `{manifest_summary.get('resume_precedence_rules', {})}`",
        "",
        "# Module Coverage",
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
        "# Safety",
        "",
        f"- harvest_roots_unchanged: **{harvest_unchanged}**",
        "- CNINFO calls: **0**",
        "- DB / MinIO / RAG: **0**",
        "- not verified · not production_ready",
        "- no commit · no push",
        "",
        "# Gate",
        "",
        "```",
        f"phase35_expanded_success_subset_snapshot_qa_gate = {gate}",
        "```",
        "",
        "build gate unchanged:",
        "",
        "```",
        "phase35_expanded_success_subset_snapshot_build_gate = PASS_WITH_CAVEAT",
        "```",
        "",
        "# Next Step",
        "",
        "Recommend: **Phase 3.5 expanded snapshot closure review**.",
        "",
        "Alternative: commit boundary review for C-class Phase 3.5 artifacts.",
        "",
        "Optional later: isolated C35R016 executive retry review only if still desired.",
        "",
        "Do **not** recommend verified / production_ready / DB / MinIO / RAG / full 500 rerun.",
    ])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def run_phase35_expanded_snapshot_quality_review(
    snapshot_dir: str = PHASE35_SNAPSHOT_DIR,
) -> Dict[str, Any]:
    """执行 Phase 3.5 expanded snapshot QA review 流水线。"""
    orig_fp_before = _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
    resume_fp_before = _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)

    universe_rows = load_universe_rows()
    holdout_rows = load_holdout_rows()
    build_report = load_build_report()
    manifest_summary = load_merge_manifest_summary(universe_rows=universe_rows)

    mapping_rows = load_field_mapping()
    snapshots, stats = load_all_valid_snapshots(snapshot_dir)

    raw_flags = detect_quality_flags(snapshots, mapping_rows)
    flag_rows = adapt_quality_flag_rows(snapshots, raw_flags)
    flag_count_by_code = Counter(r["company_code"] for r in flag_rows)

    case_rows = build_case_ledger_rows(
        universe_rows, snapshots, flag_count_by_code, build_report,
    )
    holdout_confirm_rows = build_holdout_confirmation_rows(
        holdout_rows, set(snapshots.keys()),
    )
    module_rows = build_module_coverage_rows(snapshots)
    status_rows = regenerate_status_csv(snapshots)

    orig_fp_after = _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
    resume_fp_after = _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)
    harvest_unchanged = (
        orig_fp_before == orig_fp_after and resume_fp_before == resume_fp_after
    )

    metrics_rows = build_metrics_rows(
        stats, universe_rows, case_rows, holdout_rows,
        module_rows, flag_rows, manifest_summary, harvest_unchanged,
    )
    gate = derive_qa_gate(stats, universe_rows, case_rows, holdout_confirm_rows)

    write_csv(QA_METRICS_CSV, METRICS_FIELDS, metrics_rows)
    write_csv(QA_CASE_LEDGER_CSV, CASE_LEDGER_FIELDS, case_rows)
    write_csv(QA_HOLDOUT_CONFIRMATION_CSV, HOLDOUT_CONFIRMATION_FIELDS, holdout_confirm_rows)
    write_qa_summary(
        stats, universe_rows, case_rows, holdout_rows,
        module_rows, flag_rows, manifest_summary, gate, harvest_unchanged,
    )

    outcome_counts = Counter(r["qa_outcome"] for r in case_rows)
    return {
        "stats": stats,
        "snapshots": snapshots,
        "case_rows": case_rows,
        "holdout_confirm_rows": holdout_confirm_rows,
        "metrics_rows": metrics_rows,
        "module_rows": module_rows,
        "flag_rows": flag_rows,
        "status_rows": status_rows,
        "gate": gate,
        "harvest_unchanged": harvest_unchanged,
        "outcome_counts": outcome_counts,
    }


def main() -> int:
    result = run_phase35_expanded_snapshot_quality_review()
    stats = result["stats"]
    oc = result["outcome_counts"]
    print(f"json_count: {stats['json_count']}")
    print(f"valid_json_count: {stats['valid_json_count']}")
    print(f"c35r016_present: {stats['c35r016_present']}")
    print(f"hold_for_review_present_count: {stats['hold_for_review_present_count']}")
    print(f"qa_ok: {oc.get('qa_ok', 0)}")
    print(f"qa_ok_with_caveat: {oc.get('qa_ok_with_caveat', 0)}")
    print(f"qa_review_required: {oc.get('qa_review_required', 0)}")
    print(f"harvest_unchanged: {result['harvest_unchanged']}")
    print(f"cninfo_calls=0")
    print(f"db_writes=0")
    print(f"minio_writes=0")
    print(f"rag_runs=0")
    print(f"qa_metrics: {QA_METRICS_CSV}")
    print(f"qa_case_ledger: {QA_CASE_LEDGER_CSV}")
    print(f"qa_holdout_confirmation: {QA_HOLDOUT_CONFIRMATION_CSV}")
    print(f"qa_summary: {QA_SUMMARY_MD}")
    print(f"status_csv: {STATUS_CSV}")
    print(f"phase35_expanded_success_subset_snapshot_qa_gate: {result['gate']}")
    return 0 if result["gate"] != "FAIL_REVIEW_REQUIRED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
