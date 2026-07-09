"""
CNINFO B-class Phase 2 expansion metadata validation runner.

默认 dry-run：校验 universe · 输出隔离 · 生成规划报告，**不请求 CNINFO**。
--live 须 --approve-b-class-phase2-expansion；仅 metadata · 无 PDF 下载/解析。

Usage:
    python lab/run_cninfo_b_class_phase2_expansion_validation.py
    python lab/run_cninfo_b_class_phase2_expansion_validation.py --live \\
        --approve-b-class-phase2-expansion
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_DIR = os.path.join(BASE_DIR, "lab")
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

import run_cninfo_b_class_tiny_live_validation as tiny_live  # noqa: E402

DEFAULT_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase2_expansion_universe_draft.csv",
)
DEFAULT_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase2_expansion"
)
PHASE1_TINY_LIVE_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tiny_live_validation"
)
TLC002_RETRY_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tlc002_retry"
)
PHASE3_FORBIDDEN_ROOT = os.path.join(
    BASE_DIR, "outputs", "harvest", "cninfo_c_class", "phase3_batch_500_001"
)
CATEGORIES_YAML = os.path.join(BASE_DIR, "config", "cninfo_announcement_categories.yaml")

DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "b_class_phase2_expansion_dryrun_report.csv"
)
DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "b_class_phase2_expansion_dryrun_summary.md"
)

REQUIRED_UNIVERSE_SIZE = 20
PHASE2_CASE_ID_PATTERN = re.compile(r"^B2E\d{3}$")

PHASE2_APPROVAL_REQUIRED = "approve_b_class_phase2_expansion_required"
OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_b_class_phase2_expansion"
UNIVERSE_SIZE_VIOLATION = "universe_size_must_equal_20"
NON_PHASE2_CASE_REJECTED = "non_phase2_case_not_allowed"
PHASE2_INCLUDE_REQUIRED = "phase2_include_must_be_yes"
PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED = "pdf_download_not_allowed"
PDF_PARSE_REQUESTED_NOT_ALLOWED = "pdf_parse_not_allowed"
DB_WRITE_REQUESTED_NOT_ALLOWED = "db_write_not_allowed"
MINIO_WRITE_REQUESTED_NOT_ALLOWED = "minio_write_not_allowed"
RAG_REQUESTED_NOT_ALLOWED = "rag_not_allowed"
VERIFIED_STATUS_REQUESTED_NOT_ALLOWED = "verified_status_not_allowed"
PRODUCTION_READY_REQUESTED_NOT_ALLOWED = "production_ready_not_allowed"
TINY_LIVE_APPROVAL_WRONG = "approve_b_class_tiny_live_validation_not_valid_for_phase2"
TLC002_RETRY_APPROVAL_WRONG = "approve_b_class_tlc002_retry_not_valid_for_phase2"
PHASE1_BASELINE_WRITE_FORBIDDEN = "phase1_tiny_live_baseline_write_forbidden"
TLC002_BASELINE_WRITE_FORBIDDEN = "tlc002_retry_baseline_write_forbidden"

ALLOWED_ENDPOINTS: Set[str] = {"EP001", "EP002", "EP004", "EP005"}
BLOCKED_ENDPOINTS: Set[str] = {"EP003", "EP006", "EP007"}
ANNOUNCEMENT_TYPE_SOURCE = {
    "periodic_report": "cninfo_periodic_report_pdf",
    "general_announcement": "cninfo_general_announcement_pdf",
}
SOURCE_TYPE_PRIMARY_ENDPOINT = {
    "cninfo_periodic_report_pdf": "EP004",
    "cninfo_general_announcement_pdf": "EP005",
}

PDF_DOWNLOAD_ENABLED = False
PDF_PARSE_ENABLED = False

DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "planned_request_type",
    "planned_output",
    "pdf_download",
    "pdf_parse",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

LIVE_REPORT_COLUMNS = tiny_live.REPORT_COLUMNS

EXPANSION_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "endpoint_used",
    "cninfo_request_count",
    "notes",
]

QUALITY_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "pdf_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "notes",
]


@dataclass
class Phase2UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    announcement_type: str
    target_endpoint: List[str]
    risk_level: str
    reason: str
    phase2_include: str


def _normalize_output_root(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    """输出仅允许 Phase 2 expansion 隔离根；禁止写入 Phase 1 / TLC002 / C-class harvest。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    phase1 = _normalize_output_root(PHASE1_TINY_LIVE_ROOT)
    tlc002 = _normalize_output_root(TLC002_RETRY_ROOT)
    phase3 = _normalize_output_root(PHASE3_FORBIDDEN_ROOT)

    if root == phase1 or root.startswith(phase1 + os.sep):
        return False, PHASE1_BASELINE_WRITE_FORBIDDEN
    if root == tlc002 or root.startswith(tlc002 + os.sep):
        return False, TLC002_BASELINE_WRITE_FORBIDDEN
    if root == phase3 or root.startswith(phase3 + os.sep):
        return False, "phase3_batch_500_output_root_forbidden"
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, OUTPUT_ROOT_VIOLATION


def ensure_output_layout(output_root: str) -> Dict[str, str]:
    paths = {
        "root": output_root,
        "raw_metadata": os.path.join(output_root, "raw_metadata"),
        "quality": os.path.join(output_root, "quality"),
        "reports": os.path.join(output_root, "reports"),
    }
    for p in paths.values():
        os.makedirs(p, exist_ok=True)
    return paths


def load_universe(path: str) -> List[Phase2UniverseCase]:
    cases: List[Phase2UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            endpoints = [
                s.strip() for s in (row.get("target_endpoint") or "").split(";") if s.strip()
            ]
            cases.append(
                Phase2UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    announcement_type=str(row.get("announcement_type", "")).strip(),
                    target_endpoint=endpoints,
                    risk_level=str(row.get("risk_level", "")).strip(),
                    reason=str(row.get("reason", "")).strip(),
                    phase2_include=str(row.get("phase2_include", "")).strip().lower(),
                )
            )
    return cases


def validate_phase2_case(case: Phase2UniverseCase) -> List[str]:
    issues: List[str] = []
    if not PHASE2_CASE_ID_PATTERN.match(case.case_id or ""):
        issues.append(NON_PHASE2_CASE_REJECTED)
    if case.phase2_include != "yes":
        issues.append(PHASE2_INCLUDE_REQUIRED)
    if not case.company_code:
        issues.append("company_code_missing")
    if case.announcement_type not in ANNOUNCEMENT_TYPE_SOURCE:
        issues.append(f"unsupported_announcement_type:{case.announcement_type}")
    if not case.target_endpoint:
        issues.append("target_endpoint_empty")
    for ep in case.target_endpoint:
        if ep in BLOCKED_ENDPOINTS:
            issues.append(f"endpoint_blocked:{ep}")
        if ep not in ALLOWED_ENDPOINTS:
            issues.append(f"endpoint_not_allowed:{ep}")
    if "EP001" not in case.target_endpoint:
        issues.append("EP001_required_in_target_endpoint")
    source_type = ANNOUNCEMENT_TYPE_SOURCE.get(case.announcement_type, "")
    primary = SOURCE_TYPE_PRIMARY_ENDPOINT.get(source_type, "")
    if primary and primary not in case.target_endpoint:
        issues.append(f"primary_endpoint_missing:{primary}")
    return issues


def validate_universe_size(cases: List[Phase2UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.phase2_include == "yes"]
    if len(included) != REQUIRED_UNIVERSE_SIZE:
        return False, f"{UNIVERSE_SIZE_VIOLATION}: got {len(included)} expected {REQUIRED_UNIVERSE_SIZE}"
    return True, ""


def enforce_forbidden_options(args: argparse.Namespace) -> None:
    checks = (
        (args.download_pdf, PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
        (args.parse_pdf, PDF_PARSE_REQUESTED_NOT_ALLOWED),
        (args.write_db, DB_WRITE_REQUESTED_NOT_ALLOWED),
        (args.write_minio, MINIO_WRITE_REQUESTED_NOT_ALLOWED),
        (args.run_rag, RAG_REQUESTED_NOT_ALLOWED),
        (args.mark_verified, VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
        (args.mark_production_ready, PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
    )
    for enabled, err in checks:
        if enabled:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(2)


def enforce_live_approval_gate(args: argparse.Namespace) -> None:
    if args.approve_b_class_tiny_live_validation:
        print(f"ERROR: {TINY_LIVE_APPROVAL_WRONG}", file=sys.stderr)
        sys.exit(2)
    if args.approve_b_class_tlc002_retry:
        print(f"ERROR: {TLC002_RETRY_APPROVAL_WRONG}", file=sys.stderr)
        sys.exit(2)
    for flag, err in (
        (args.approve_full_harvest, tiny_live.FORBIDDEN_APPROVE_FULL_HARVEST),
        (args.approve_phase2_smoke_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE2),
        (args.approve_phase3_batch_500_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE3),
    ):
        if flag:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not args.approve_b_class_phase2_expansion:
        print(f"ERROR: {PHASE2_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def to_tiny_live_case(case: Phase2UniverseCase) -> tiny_live.UniverseCase:
    source_type = ANNOUNCEMENT_TYPE_SOURCE[case.announcement_type]
    return tiny_live.UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        source_type=source_type,
        endpoint_scope=list(case.target_endpoint),
        expected_fields="phase1_freeze_v1_required_15",
        risk_level=case.risk_level,
        reason=case.reason,
    )


def build_planned_request_types(case: Phase2UniverseCase) -> str:
    parts: List[str] = []
    if "EP002" in case.target_endpoint:
        parts.append("EP002_topSearch_orgId")
    parts.append("EP001_hisAnnouncement_query")
    primary = SOURCE_TYPE_PRIMARY_ENDPOINT[ANNOUNCEMENT_TYPE_SOURCE[case.announcement_type]]
    if primary == "EP004":
        parts.append("EP004_periodic_report_metadata_lineage")
    elif primary == "EP005":
        parts.append("EP005_general_announcement_metadata_lineage")
    return ";".join(parts)


def build_dryrun_row(case: Phase2UniverseCase, issues: List[str]) -> Dict[str, str]:
    primary = SOURCE_TYPE_PRIMARY_ENDPOINT[ANNOUNCEMENT_TYPE_SOURCE[case.announcement_type]]
    planned_output = os.path.join("raw_metadata", f"{case.case_id}_{primary}.json")
    status = "planned_ok" if not issues else "validation_failed"
    notes = "dry-run; CNINFO not called; metadata and pdf URL lineage only"
    if issues:
        notes = f"{notes}; {';'.join(issues)}"
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "announcement_type": case.announcement_type,
        "target_endpoint": ";".join(case.target_endpoint),
        "planned_request_type": build_planned_request_types(case),
        "planned_output": planned_output,
        "pdf_download": "0",
        "pdf_parse": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def write_dryrun_snapshot(
    case: Phase2UniverseCase,
    output_paths: Dict[str, str],
    issues: List[str],
) -> None:
    primary = SOURCE_TYPE_PRIMARY_ENDPOINT[ANNOUNCEMENT_TYPE_SOURCE[case.announcement_type]]
    snap_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}_{primary}.json")
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "case": case.__dict__,
                "mode": "dry_run",
                "cninfo_called": False,
                "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                "pdf_parse_enabled": PDF_PARSE_ENABLED,
                "planned_endpoints": case.target_endpoint,
                "validation_issues": issues,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    qpath = os.path.join(output_paths["quality"], f"{case.case_id}.json")
    with open(qpath, "w", encoding="utf-8") as f:
        json.dump(
            {
                "case_id": case.case_id,
                "quality_status": "not_retrieved",
                "lineage_status": "not_retrieved",
                "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                "pdf_parse_enabled": PDF_PARSE_ENABLED,
                "dry_run": True,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def process_dry_run(
    cases: List[Phase2UniverseCase],
    output_paths: Dict[str, str],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.phase2_include != "yes":
            continue
        issues = validate_phase2_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        write_dryrun_snapshot(case, output_paths, issues)
        rows.append(build_dryrun_row(case, issues))
    return rows, universe_issues


def process_live(
    cases: List[Phase2UniverseCase],
    output_paths: Dict[str, str],
    categories_config: Dict[str, Any],
) -> Tuple[List[Dict[str, str]], tiny_live.LiveStats, List[str]]:
    report_rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    stats = tiny_live.LiveStats()

    for case in cases:
        if case.phase2_include != "yes":
            continue
        issues = validate_phase2_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            continue
        tl_case = to_tiny_live_case(case)
        stats.companies_executed += 1
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, categories_config, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        record["notes"] = f"phase2 expansion live; {record.get('notes', '')}"
        record["_case_cninfo_requests"] = case_cninfo_requests
        record["_phase2_case"] = case
        primary = record.get("endpoint_id") or SOURCE_TYPE_PRIMARY_ENDPOINT[tl_case.source_type]
        snap_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}_{primary}.json")
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": "live",
                    "cninfo_called": True,
                    "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                    "pdf_parse_enabled": PDF_PARSE_ENABLED,
                    "record": {k: record.get(k) for k in LIVE_REPORT_COLUMNS},
                    "raw_announcement": record.get("raw_announcement"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        qpath = os.path.join(output_paths["quality"], f"{case.case_id}.json")
        with open(qpath, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case_id": case.case_id,
                    "quality_status": record.get("quality_status"),
                    "lineage_status": record.get("lineage_status"),
                    "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                    "pdf_parse_enabled": PDF_PARSE_ENABLED,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        report_rows.append(record)
        print(
            f"case_id={case.case_id} company_code={case.company_code} "
            f"retrieval_status={record.get('retrieval_status')}",
            flush=True,
        )
    return report_rows, stats, universe_issues


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def build_expansion_report_row(record: Dict[str, Any]) -> Dict[str, str]:
    case: Phase2UniverseCase = record["_phase2_case"]
    pdf_url = record.get("pdf_url") or ""
    adjunct_url = record.get("adjunct_url") or ""
    endpoint_used = record.get("endpoint_id") or ""
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "announcement_type": case.announcement_type,
        "target_endpoint": ";".join(case.target_endpoint),
        "retrieval_status": str(record.get("retrieval_status") or ""),
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": str(record.get("announcement_time") or ""),
        "pdf_url_present": "1" if _is_present(pdf_url) else "0",
        "adjunct_url_present": "1" if _is_present(adjunct_url) else "0",
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "endpoint_used": endpoint_used,
        "cninfo_request_count": str(record.get("_case_cninfo_requests", 0)),
        "notes": str(record.get("notes") or ""),
    }


def classify_case_acceptability(row: Dict[str, str]) -> str:
    """返回 acceptable / failed / needs_review_acceptable / empty_but_valid。"""
    rs = row.get("retrieval_status", "")
    qs = row.get("quality_status", "")
    ls = row.get("lineage_status", "")
    notes = row.get("notes", "")

    if row.get("pdf_downloaded") == "1" or row.get("pdf_parsed") == "1":
        return "red_line_violation"
    if qs == "verified":
        return "red_line_violation"

    if rs == "found" and ls in ("discovered", "pass"):
        return "acceptable"
    if rs == "found" and qs in ("pass", "needs_review", "caveat"):
        return "acceptable"
    if rs == "empty_response" and notes:
        return "empty_but_valid"
    if rs in ("network_error", "universe_validation_failed"):
        return "failed"
    if qs == "needs_review" and notes:
        return "needs_review_acceptable"
    if rs == "not_found" and qs == "needs_review":
        return "needs_review_acceptable"
    if rs in ("empty_response", "not_found"):
        return "needs_review_acceptable"
    return "failed"


def compute_execution_gate(expansion_rows: List[Dict[str, str]]) -> str:
    if any(classify_case_acceptability(r) == "red_line_violation" for r in expansion_rows):
        return "FAIL"
    acceptable = sum(
        1 for r in expansion_rows
        if classify_case_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    if acceptable >= 16 and len(expansion_rows) == REQUIRED_UNIVERSE_SIZE:
        return "PASS_WITH_CAVEAT"
    return "FAIL"


def write_live_expansion_reports(
    report_records: List[Dict[str, Any]],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    universe_issues: List[str],
) -> Tuple[str, str, str, str]:
    expansion_rows = [build_expansion_report_row(r) for r in report_records]
    gate = compute_execution_gate(expansion_rows)

    report_path = os.path.join(output_paths["reports"], "b_class_phase2_expansion_report.csv")
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPANSION_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(expansion_rows)

    quality_path = os.path.join(
        output_paths["reports"], "b_class_phase2_expansion_quality_report.csv"
    )
    with open(quality_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        for row in expansion_rows:
            writer.writerow({k: row.get(k, "") for k in QUALITY_REPORT_COLUMNS})

    acceptable = sum(
        1 for r in expansion_rows
        if classify_case_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    failed = sum(1 for r in expansion_rows if classify_case_acceptability(r) == "failed")
    needs_review = sum(1 for r in expansion_rows if r.get("quality_status") == "needs_review")
    empty_but_valid = sum(
        1 for r in expansion_rows if classify_case_acceptability(r) == "empty_but_valid"
    )
    found = sum(1 for r in expansion_rows if r.get("retrieval_status") == "found")

    summary_path = os.path.join(output_paths["reports"], "b_class_phase2_expansion_summary.md")
    lines = [
        "# CNINFO B 类 Phase 2 Expansion — Live Execution Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2 expansion live metadata validation · **无 PDF 下载/解析** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| mode | live |",
        f"| universe size | {len(expansion_rows)} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| found | {found} |",
        f"| acceptable | {acceptable} |",
        f"| failed | {failed} |",
        f"| needs_review | {needs_review} |",
        f"| empty_but_valid | {empty_but_valid} |",
        f"| PDF downloaded | **0** |",
        f"| PDF parsed | **0** |",
        "",
        "## Endpoint usage",
        "",
    ]
    for ep in ("EP001", "EP002", "EP004", "EP005"):
        lines.append(f"- {ep}: {stats.endpoint_hits.get(ep, 0)}")
    lines.extend([
        "",
        "## Safety",
        "",
        "- metadata and pdf URL lineage only: **yes**",
        "- Phase 1 tiny live baseline untouched: **yes**",
        "- TLC002 retry baseline untouched: **yes**",
        "- C-class harvest untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase2_expansion_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready** · Phase 2 limited expansion only",
        "",
    ])
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_path, summary_path, quality_path, gate


def write_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    path = os.path.join(output_paths["reports"], "b_class_phase2_expansion_dryrun_report.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_dryrun_summary(
    output_paths: Dict[str, str],
    case_count: int,
    universe_issues: List[str],
    gate: str,
) -> str:
    lines = [
        "# CNINFO B 类 Phase 2 Expansion — Dry-Run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2 expansion runner dry-run · **无 CNINFO** · **无 PDF 下载/解析**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| mode | dry_run |",
        f"| universe size | {case_count} |",
        f"| CNINFO calls | **0** |",
        f"| PDF download | **0** |",
        f"| PDF parse | **0** |",
        f"| DB / MinIO / RAG | **0** |",
        "",
        "## Output isolation",
        "",
        f"```text",
        f"{output_paths['root']}",
        f"```",
        "",
        "## Safety",
        "",
        "- metadata and pdf URL lineage only: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "- Phase 1 tiny live baseline untouched: **yes**",
        "- TLC002 retry baseline untouched: **yes**",
        "- C-class harvest untouched: **yes**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase2_expansion_runner_gate = {gate}",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    path = os.path.join(output_paths["reports"], "b_class_phase2_expansion_dryrun_summary.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def compute_runner_gate(mode: str, case_count: int, universe_issues: List[str]) -> str:
    if mode != "dry_run":
        return "NOT_EVALUATED_IN_THIS_ROUND"
    if universe_issues or case_count != REQUIRED_UNIVERSE_SIZE:
        return "FAIL"
    return "READY_FOR_APPROVAL"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CNINFO B-class Phase2 expansion metadata validation（dry-run default）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")

    parser.add_argument("--universe-csv", default=DEFAULT_UNIVERSE_CSV)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--approve-b-class-phase2-expansion",
        action="store_true",
        help="显式批准 B-class Phase 2 expansion live metadata validation",
    )
    parser.add_argument("--approve-b-class-tiny-live-validation", action="store_true")
    parser.add_argument("--approve-b-class-tlc002-retry", action="store_true")
    parser.add_argument("--approve-full-harvest", action="store_true")
    parser.add_argument("--approve-phase2-smoke-harvest", action="store_true")
    parser.add_argument("--approve-phase3-batch-500-harvest", action="store_true")
    parser.add_argument("--download-pdf", action="store_true")
    parser.add_argument("--parse-pdf", action="store_true")
    parser.add_argument("--write-db", action="store_true")
    parser.add_argument("--write-minio", action="store_true")
    parser.add_argument("--run-rag", action="store_true")
    parser.add_argument("--mark-verified", action="store_true")
    parser.add_argument("--mark-production-ready", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    enforce_forbidden_options(args)
    if args.mode == "live":
        enforce_live_approval_gate(args)

    ok_root, root_err = validate_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    if args.limit is not None and args.limit != REQUIRED_UNIVERSE_SIZE:
        print(f"ERROR: {UNIVERSE_SIZE_VIOLATION}: limit={args.limit}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))
    cases = load_universe(args.universe_csv)
    included = [c for c in cases if c.phase2_include == "yes"]
    if args.limit is not None:
        included = included[: args.limit]

    ok_size, size_err = validate_universe_size(included)
    if not ok_size:
        print(f"ERROR: {size_err}", file=sys.stderr)
        return 2

    if args.mode == "dry_run":
        dryrun_rows, universe_issues = process_dry_run(included, output_paths)
        report_path = write_dryrun_report(dryrun_rows, output_paths)
        gate = compute_runner_gate("dry_run", len(included), universe_issues)
        summary_path = write_dryrun_summary(output_paths, len(included), universe_issues, gate)
        print(f"mode=dry_run cases={len(included)} cninfo_calls=0")
        print(f"gate=b_class_phase2_expansion_runner_gate={gate}")
        print(f"dryrun_report={report_path}")
        print(f"dryrun_summary={summary_path}")
        if universe_issues:
            print(f"universe_issues={len(universe_issues)}", file=sys.stderr)
            return 1
        return 0

    with open(CATEGORIES_YAML, encoding="utf-8") as f:
        categories_config = yaml.safe_load(f) or {}
    report_records, stats, universe_issues = process_live(included, output_paths, categories_config)
    report_path, summary_path, quality_path, gate = write_live_expansion_reports(
        report_records, output_paths, stats, universe_issues
    )
    live_report = os.path.join(output_paths["reports"], "b_class_phase2_expansion_live_report.csv")
    with open(live_report, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        for record in report_records:
            writer.writerow({k: str(record.get(k, "")) for k in LIVE_REPORT_COLUMNS})
    print(f"mode=live cases={len(included)} cninfo_calls={stats.cninfo_requests}")
    print(f"gate=b_class_phase2_expansion_execution_gate={gate}")
    print(f"report={report_path}")
    print(f"summary={summary_path}")
    print(f"quality={quality_path}")
    if universe_issues or gate == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
