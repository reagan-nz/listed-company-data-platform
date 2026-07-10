"""
CNINFO B-class Phase 3 EP002/orgId reachability precheck runner.

默认 dry-run：校验 candidates · 输出隔离 · 生成规划报告，**不请求 CNINFO**。
--live 须 --approve-b-class-phase3-100-ep002-reachability-precheck；仅 EP002 orgId 可达性 · 无 metadata retry · 无 PDF。

Usage:
    python lab/run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py --dry-run \\
        --candidates-csv outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv \\
        --output-root outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_DIR = os.path.join(BASE_DIR, "lab")
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

import run_cninfo_b_class_tiny_live_validation as tiny_live  # noqa: E402

DEFAULT_PRECHECK_CANDIDATES_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv",
)
DEFAULT_PRECHECK_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase3_100_ep002_reachability_precheck",
)
PHASE3_EXPANSION_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase3_100_expansion"
)
PHASE3_FAILED_RETRY_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase3_100_failed_retry"
)
PHASE25_EXPANSION_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase25_expansion"
)
PHASE25_FAILED_RETRY_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase25_failed_retry"
)
RETRY_V2_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase3_100_failed_retry_v2_universe.csv",
)

REQUIRED_CANDIDATE_COUNT = 8
MAX_PRECHECK_REQUEST_CAP = 16
REQUESTS_PER_CANDIDATE = 1

ALLOWED_PRECHECK_IDS: Set[str] = {
    "B3EP001",
    "B3EP002",
    "B3EP003",
    "B3EP004",
    "B3EP005",
    "B3EP006",
    "B3EP007",
    "B3EP008",
}
ALLOWED_CASE_IDS: Set[str] = {
    "B3E001",
    "B3E018",
    "B3E035",
    "B3E051",
    "B3E074",
    "B3E091",
    "B3E096",
    "B3E100",
}
HOLD_CASE_ID = "B3E087"
RECOVERED_CASE_IDS: Set[str] = {
    "B3E003",
    "B3E004",
    "B3E005",
    "B3E006",
    "B3E007",
    "B3E008",
    "B3E009",
    "B3E011",
}
PRIOR_PHASE_CASE_ID_PATTERN = re.compile(r"^B(1|2|25)E\d{3}$")
ACCEPTED_CHECK_TYPES: Set[str] = {"ep002_orgid_reachability"}

PRECHECK_RUNNER_GATE = "READY_FOR_APPROVAL"
PRECHECK_APPROVAL_REQUIRED = (
    "approve_b_class_phase3_100_ep002_reachability_precheck_required"
)
PRECHECK_WRONG_APPROVAL = (
    "approve_b_class_phase3_100_ep002_reachability_precheck_wrong_flag"
)
PRECHECK_OUTPUT_ROOT_VIOLATION = (
    "output_root_must_be_under_cninfo_b_class_phase3_100_ep002_reachability_precheck"
)
PHASE3_EXPANSION_WRITE_FORBIDDEN = "phase3_expansion_baseline_write_forbidden"
PHASE3_FAILED_RETRY_WRITE_FORBIDDEN = "phase3_failed_retry_baseline_write_forbidden"
PHASE25_EXPANSION_WRITE_FORBIDDEN = "phase25_expansion_baseline_write_forbidden"
PHASE25_FAILED_RETRY_WRITE_FORBIDDEN = "phase25_failed_retry_baseline_write_forbidden"
RETRY_V2_UNIVERSE_FORBIDDEN = "retry_v2_universe_creation_forbidden"
CANDIDATES_CSV_REQUIRED = "candidates_csv_required"
CANDIDATES_CSV_NOT_FOUND = "candidates_csv_not_found"
PRECHECK_CANDIDATE_COUNT_VIOLATION = "precheck_candidate_count_must_equal_8"
PRECHECK_ID_NOT_ALLOWED = "precheck_id_not_allowed"
PRECHECK_CASE_NOT_ALLOWED = "precheck_case_id_not_allowed"
HOLD_CASE_IN_PRECHECK_FORBIDDEN = "hold_case_in_precheck_forbidden"
RECOVERED_CASE_IN_PRECHECK_FORBIDDEN = "recovered_case_in_precheck_forbidden"
PRIOR_PHASE_CASE_IN_PRECHECK_FORBIDDEN = "prior_phase_case_in_precheck_forbidden"
PRECHECK_CANDIDATE_OUT_OF_UNIVERSE = "precheck_candidate_out_of_universe"
PRECHECK_CHECK_TYPE_UNSUPPORTED = "precheck_check_type_unsupported"
PRECHECK_INCLUDE_REQUIRED = "precheck_include_must_be_yes"
PRECHECK_REQUEST_CAP_EXCEEDED = "precheck_request_cap_exceeded"
PRECHECK_BOUNDARY_VIOLATION = "precheck_boundary_violation"

EP001_VALIDATION_REQUESTED_NOT_ALLOWED = "ep001_validation_not_allowed"
EP004_VALIDATION_REQUESTED_NOT_ALLOWED = "ep004_validation_not_allowed"
EP005_VALIDATION_REQUESTED_NOT_ALLOWED = "ep005_validation_not_allowed"
PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED = "pdf_download_not_allowed"
PDF_PARSE_REQUESTED_NOT_ALLOWED = "pdf_parse_not_allowed"
OCR_REQUESTED_NOT_ALLOWED = "ocr_not_allowed"
EXTRACTION_REQUESTED_NOT_ALLOWED = "extraction_not_allowed"
DB_WRITE_REQUESTED_NOT_ALLOWED = "db_write_not_allowed"
MINIO_WRITE_REQUESTED_NOT_ALLOWED = "minio_write_not_allowed"
RAG_REQUESTED_NOT_ALLOWED = "rag_not_allowed"
VERIFIED_STATUS_REQUESTED_NOT_ALLOWED = "verified_status_not_allowed"
PRODUCTION_READY_REQUESTED_NOT_ALLOWED = "production_ready_not_allowed"

DRYRUN_REPORT_NAME = (
    "b_class_phase3_100_ep002_reachability_precheck_dryrun_report.csv"
)
DRYRUN_SUMMARY_NAME = (
    "b_class_phase3_100_ep002_reachability_precheck_dryrun_summary.md"
)
LIVE_REPORT_NAME = "b_class_phase3_100_ep002_reachability_precheck_report.csv"
LIVE_SUMMARY_NAME = "b_class_phase3_100_ep002_reachability_precheck_summary.md"
LIVE_QUALITY_REPORT_NAME = (
    "b_class_phase3_100_ep002_reachability_precheck_quality_report.csv"
)
PRECHECK_ORGID_SUCCESS_THRESHOLD_RATIO = 0.60

DRYRUN_COLUMNS = [
    "precheck_id",
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "persistent_failure_stage",
    "original_phase3_status",
    "failed_retry_status",
    "planned_check_type",
    "precheck_include",
    "planned_request_count",
    "planned_output_root",
    "cninfo_call_planned",
    "pdf_download",
    "pdf_parse",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "dryrun_status",
    "notes",
]

LIVE_REPORT_COLUMNS = [
    "precheck_id",
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "persistent_failure_stage",
    "original_phase3_status",
    "failed_retry_status",
    "planned_check_type",
    "precheck_include",
    "orgid_resolution_status",
    "resolved_org_id",
    "cninfo_request_count",
    "failure_type",
    "reachability_status",
    "quality_status",
    "notes",
]

LIVE_QUALITY_COLUMNS = [
    "precheck_id",
    "case_id",
    "company_code",
    "market",
    "announcement_type",
    "reachability_status",
    "orgid_resolution_status",
    "resolved_org_id",
    "failure_type",
    "quality_status",
    "cninfo_request_count",
    "notes",
]


@dataclass
class PrecheckCandidate:
    precheck_id: str
    case_id: str
    company_code: str
    company_name: str
    market: str
    announcement_type: str
    target_endpoint: str
    persistent_failure_stage: str
    original_phase3_status: str
    failed_retry_status: str
    precheck_include: str
    precheck_reason: str
    planned_check_type: str
    notes: str


def _normalize_output_root(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def validate_precheck_output_root(output_root: str) -> Tuple[bool, str]:
    """precheck 输出仅允许 precheck 隔离根；禁止写入 Phase 3 / failed retry / Phase 2.5 基线。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_PRECHECK_OUTPUT_ROOT)
    phase3 = _normalize_output_root(PHASE3_EXPANSION_ROOT)
    phase3_retry = _normalize_output_root(PHASE3_FAILED_RETRY_ROOT)
    phase25 = _normalize_output_root(PHASE25_EXPANSION_ROOT)
    phase25_retry = _normalize_output_root(PHASE25_FAILED_RETRY_ROOT)

    if "retry_v2" in root.lower():
        return False, RETRY_V2_UNIVERSE_FORBIDDEN
    if root == phase3 or root.startswith(phase3 + os.sep):
        return False, PHASE3_EXPANSION_WRITE_FORBIDDEN
    if root == phase3_retry or root.startswith(phase3_retry + os.sep):
        return False, PHASE3_FAILED_RETRY_WRITE_FORBIDDEN
    if root == phase25 or root.startswith(phase25 + os.sep):
        return False, PHASE25_EXPANSION_WRITE_FORBIDDEN
    if root == phase25_retry or root.startswith(phase25_retry + os.sep):
        return False, PHASE25_FAILED_RETRY_WRITE_FORBIDDEN
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, PRECHECK_OUTPUT_ROOT_VIOLATION


def load_precheck_candidates(path: str) -> List[PrecheckCandidate]:
    candidates: List[PrecheckCandidate] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append(
                PrecheckCandidate(
                    precheck_id=str(row.get("precheck_id", "")).strip(),
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    announcement_type=str(row.get("announcement_type", "")).strip(),
                    target_endpoint=str(row.get("target_endpoint", "")).strip(),
                    persistent_failure_stage=str(
                        row.get("persistent_failure_stage", "")
                    ).strip(),
                    original_phase3_status=str(
                        row.get("original_phase3_status", "")
                    ).strip(),
                    failed_retry_status=str(
                        row.get("failed_retry_status", "")
                    ).strip(),
                    precheck_include=str(row.get("precheck_include", "")).strip().lower(),
                    precheck_reason=str(row.get("precheck_reason", "")).strip(),
                    planned_check_type=str(row.get("planned_check_type", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return candidates


def validate_precheck_candidate(candidate: PrecheckCandidate) -> List[str]:
    issues: List[str] = []
    if candidate.precheck_id not in ALLOWED_PRECHECK_IDS:
        issues.append(f"{PRECHECK_ID_NOT_ALLOWED}:{candidate.precheck_id}")
    if candidate.case_id == HOLD_CASE_ID:
        issues.append(f"{HOLD_CASE_IN_PRECHECK_FORBIDDEN}:{candidate.case_id}")
    elif candidate.case_id in RECOVERED_CASE_IDS:
        issues.append(
            f"{RECOVERED_CASE_IN_PRECHECK_FORBIDDEN}:{candidate.case_id}"
        )
    elif PRIOR_PHASE_CASE_ID_PATTERN.match(candidate.case_id):
        issues.append(
            f"{PRIOR_PHASE_CASE_IN_PRECHECK_FORBIDDEN}:{candidate.case_id}"
        )
    elif candidate.case_id not in ALLOWED_CASE_IDS:
        issues.append(f"{PRECHECK_CASE_NOT_ALLOWED}:{candidate.case_id}")
    if candidate.precheck_include != "yes":
        issues.append(PRECHECK_INCLUDE_REQUIRED)
    if candidate.planned_check_type not in ACCEPTED_CHECK_TYPES:
        issues.append(
            f"{PRECHECK_CHECK_TYPE_UNSUPPORTED}:{candidate.planned_check_type}"
        )
    return issues


def validate_precheck_candidates(candidates: List[PrecheckCandidate]) -> List[str]:
    issues: List[str] = []
    included = [c for c in candidates if c.precheck_include == "yes"]
    if len(included) != REQUIRED_CANDIDATE_COUNT:
        issues.append(
            f"{PRECHECK_CANDIDATE_COUNT_VIOLATION}: got {len(included)} expected "
            f"{REQUIRED_CANDIDATE_COUNT}"
        )
    if len(candidates) != REQUIRED_CANDIDATE_COUNT:
        issues.append(
            f"{PRECHECK_CANDIDATE_COUNT_VIOLATION}: csv_rows={len(candidates)} "
            f"expected {REQUIRED_CANDIDATE_COUNT}"
        )

    precheck_ids = {c.precheck_id for c in included}
    case_ids = {c.case_id for c in included}
    if precheck_ids != ALLOWED_PRECHECK_IDS:
        issues.append(f"{PRECHECK_ID_NOT_ALLOWED}: set={sorted(precheck_ids)}")
    if case_ids != ALLOWED_CASE_IDS:
        issues.append(f"{PRECHECK_CASE_NOT_ALLOWED}: set={sorted(case_ids)}")

    for candidate in candidates:
        issues.extend(validate_precheck_candidate(candidate))
    return issues


def compute_planned_request_total(candidates: List[PrecheckCandidate]) -> int:
    included = [c for c in candidates if c.precheck_include == "yes"]
    return len(included) * REQUESTS_PER_CANDIDATE


def validate_request_cap(planned_total: int, request_cap: int) -> Tuple[bool, str]:
    cap = min(request_cap, MAX_PRECHECK_REQUEST_CAP)
    if cap > MAX_PRECHECK_REQUEST_CAP:
        return (
            False,
            f"{PRECHECK_REQUEST_CAP_EXCEEDED}: cap={cap} max={MAX_PRECHECK_REQUEST_CAP}",
        )
    if planned_total > cap:
        return (
            False,
            f"{PRECHECK_REQUEST_CAP_EXCEEDED}: planned={planned_total} cap={cap}",
        )
    return True, ""


def ensure_output_layout(output_root: str) -> Dict[str, str]:
    reports_dir = os.path.join(output_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    return {
        "output_root": output_root,
        "reports_dir": reports_dir,
        "dryrun_report": os.path.join(reports_dir, DRYRUN_REPORT_NAME),
        "dryrun_summary": os.path.join(reports_dir, DRYRUN_SUMMARY_NAME),
        "live_report": os.path.join(reports_dir, LIVE_REPORT_NAME),
        "live_summary": os.path.join(reports_dir, LIVE_SUMMARY_NAME),
        "live_quality_report": os.path.join(reports_dir, LIVE_QUALITY_REPORT_NAME),
    }


def enforce_forbidden_options(args: argparse.Namespace) -> None:
    checks = (
        (args.run_ep001_validation, EP001_VALIDATION_REQUESTED_NOT_ALLOWED),
        (args.run_ep004_validation, EP004_VALIDATION_REQUESTED_NOT_ALLOWED),
        (args.run_ep005_validation, EP005_VALIDATION_REQUESTED_NOT_ALLOWED),
        (args.download_pdf, PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
        (args.parse_pdf, PDF_PARSE_REQUESTED_NOT_ALLOWED),
        (args.enable_ocr, OCR_REQUESTED_NOT_ALLOWED),
        (args.enable_extraction, EXTRACTION_REQUESTED_NOT_ALLOWED),
        (args.write_db, DB_WRITE_REQUESTED_NOT_ALLOWED),
        (args.write_minio, MINIO_WRITE_REQUESTED_NOT_ALLOWED),
        (args.run_rag, RAG_REQUESTED_NOT_ALLOWED),
        (args.mark_verified, VERIFIED_STATUS_REQUESTED_NOT_ALLOWED),
        (args.mark_production_ready, PRODUCTION_READY_REQUESTED_NOT_ALLOWED),
        (args.create_retry_v2_universe, RETRY_V2_UNIVERSE_FORBIDDEN),
    )
    for enabled, err in checks:
        if enabled:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(2)


def enforce_precheck_approval_gate(args: argparse.Namespace) -> None:
    wrong_flags = (
        (args.approve_b_class_phase3_100_expansion, PRECHECK_WRONG_APPROVAL),
        (args.approve_b_class_phase3_100_failed_retry, PRECHECK_WRONG_APPROVAL),
        (args.approve_b_class_phase25_expansion, PRECHECK_WRONG_APPROVAL),
        (args.approve_b_class_phase25_failed_retry, PRECHECK_WRONG_APPROVAL),
        (args.approve_b_class_tiny_live_validation, PRECHECK_WRONG_APPROVAL),
        (args.approve_full_harvest, PRECHECK_WRONG_APPROVAL),
        (args.approve_phase2_smoke_harvest, PRECHECK_WRONG_APPROVAL),
        (args.approve_phase3_batch_500_harvest, PRECHECK_WRONG_APPROVAL),
        (args.approve_a_class_phase2_cninfo_reachability_precheck, PRECHECK_WRONG_APPROVAL),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    if (
        args.mode == "live"
        and not args.approve_b_class_phase3_100_ep002_reachability_precheck
    ):
        print(f"ERROR: {PRECHECK_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def build_dryrun_row(
    candidate: PrecheckCandidate,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    candidate_issues = [
        i for i in issues if candidate.precheck_id in i or candidate.case_id in i
    ]
    row_issues = validate_precheck_candidate(candidate) + [
        i for i in issues if i.startswith(PRECHECK_CANDIDATE_COUNT_VIOLATION)
    ]
    all_issues = list(dict.fromkeys(candidate_issues + row_issues))
    status = "planned_ok" if not all_issues else "universe_invalid"
    notes = (
        "dry-run; CNINFO not called; EP002 orgId reachability only; not retry_v2 universe"
        if not all_issues
        else "; ".join(all_issues)
    )
    return {
        "precheck_id": candidate.precheck_id,
        "case_id": candidate.case_id,
        "company_code": candidate.company_code,
        "company_name": candidate.company_name,
        "market": candidate.market,
        "announcement_type": candidate.announcement_type,
        "target_endpoint": candidate.target_endpoint,
        "persistent_failure_stage": candidate.persistent_failure_stage,
        "original_phase3_status": candidate.original_phase3_status,
        "failed_retry_status": candidate.failed_retry_status,
        "planned_check_type": candidate.planned_check_type,
        "precheck_include": candidate.precheck_include,
        "planned_request_count": str(REQUESTS_PER_CANDIDATE if not all_issues else 0),
        "planned_output_root": output_root,
        "cninfo_call_planned": "0",
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "db_write": "0",
        "minio_write": "0",
        "rag_run": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def process_dry_run(
    candidates: List[PrecheckCandidate],
    output_root: str,
    universe_issues: List[str],
) -> List[Dict[str, str]]:
    return [
        build_dryrun_row(candidate, universe_issues, output_root)
        for candidate in candidates
    ]


def write_dryrun_report(rows: List[Dict[str, str]], paths: Dict[str, str]) -> str:
    report_path = paths["dryrun_report"]
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_dryrun_summary(
    paths: Dict[str, str],
    candidates: List[PrecheckCandidate],
    universe_issues: List[str],
    planned_total: int,
    request_cap: int,
) -> str:
    included = [c for c in candidates if c.precheck_include == "yes"]
    planned_ok = sum(
        1
        for row in process_dry_run(candidates, paths["output_root"], universe_issues)
        if row["dryrun_status"] == "planned_ok"
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# CNINFO B 类 Phase 3 EP002 Reachability Precheck Dry-run 摘要",
        "",
        f"_生成时间：{now}_",
        "",
        "> **性质：** precheck dry-run · **无 CNINFO** · **无 live** · **不是 verified**",
        "",
        "## 摘要",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        "| mode | precheck_dry_run |",
        f"| candidates | **{len(included)}** |",
        f"| planned_ok | **{planned_ok}/{len(included)}** |",
        f"| planned_request_count_total | **{planned_total}** |",
        f"| request_cap | **≤ {min(request_cap, MAX_PRECHECK_REQUEST_CAP)}** |",
        "| CNINFO calls | **0** |",
        "| PDF / OCR / extraction / DB / MinIO / RAG | **0** |",
        f"| runner gate | **`b_class_phase3_100_ep002_reachability_precheck_runner_gate = {PRECHECK_RUNNER_GATE}`** |",
        "",
        "## Universe",
        "",
        f"- precheck_ids: {', '.join(sorted(ALLOWED_PRECHECK_IDS))}",
        f"- case_ids: {', '.join(sorted(ALLOWED_CASE_IDS))}",
        f"- B3E087 excluded: **yes**",
        f"- 8 recovered cases excluded: **yes**",
        f"- prior B-class phases excluded: **yes**",
        f"- retry_v2 universe: **not created**",
        "",
        "## Gate",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe Issues", ""])
        for issue in universe_issues:
            lines.append(f"- {issue}")
        lines.append("")
    summary_path = paths["dryrun_summary"]
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def compute_precheck_execution_gate(rows: List[Dict[str, str]]) -> str:
    """至少 60% 候选 orgId 解析成功 → PASS_WITH_CAVEAT，否则 FAIL_REVIEW_REQUIRED。"""
    if not rows:
        return "FAIL_REVIEW_REQUIRED"
    success_count = sum(
        1 for row in rows if row.get("orgid_resolution_status") == "resolved"
    )
    threshold = int(len(rows) * PRECHECK_ORGID_SUCCESS_THRESHOLD_RATIO + 0.999999)
    if success_count >= threshold:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def process_live_precheck(
    candidates: List[PrecheckCandidate],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], str]:
    """live precheck：仅 EP002 orgId resolution 可达性（批准后执行）。"""
    rows: List[Dict[str, str]] = []
    for candidate in candidates:
        if candidate.precheck_include != "yes":
            continue
        before = stats.cninfo_requests
        org_id, org_err = tiny_live.resolve_orgid(candidate.company_code, stats)
        request_delta = stats.cninfo_requests - before
        if org_id:
            reachability_status = "reachable"
            orgid_resolution_status = "resolved"
            failure_type = ""
            quality_status = "orgid_resolved"
        else:
            reachability_status = "unreachable"
            orgid_resolution_status = "failed"
            failure_type = org_err or "network_error"
            quality_status = "unresolved_network_caveat"
        rows.append(
            {
                "precheck_id": candidate.precheck_id,
                "case_id": candidate.case_id,
                "company_code": candidate.company_code,
                "company_name": candidate.company_name,
                "market": candidate.market,
                "announcement_type": candidate.announcement_type,
                "target_endpoint": candidate.target_endpoint,
                "persistent_failure_stage": candidate.persistent_failure_stage,
                "original_phase3_status": candidate.original_phase3_status,
                "failed_retry_status": candidate.failed_retry_status,
                "planned_check_type": candidate.planned_check_type,
                "precheck_include": candidate.precheck_include,
                "orgid_resolution_status": orgid_resolution_status,
                "resolved_org_id": org_id,
                "cninfo_request_count": str(request_delta),
                "failure_type": failure_type,
                "reachability_status": reachability_status,
                "quality_status": quality_status,
                "notes": (
                    f"live precheck; EP002 orgId only; not metadata retry; "
                    f"not retry_v2; err={org_err}"
                ),
            }
        )
    gate = compute_precheck_execution_gate(rows)
    return rows, gate


def write_live_report(rows: List[Dict[str, str]], paths: Dict[str, str]) -> str:
    report_path = paths["live_report"]
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_live_quality_report(rows: List[Dict[str, str]], paths: Dict[str, str]) -> str:
    report_path = paths["live_quality_report"]
    quality_rows = [
        {
            "precheck_id": row["precheck_id"],
            "case_id": row["case_id"],
            "company_code": row["company_code"],
            "market": row["market"],
            "announcement_type": row["announcement_type"],
            "reachability_status": row["reachability_status"],
            "orgid_resolution_status": row["orgid_resolution_status"],
            "resolved_org_id": row["resolved_org_id"],
            "failure_type": row["failure_type"],
            "quality_status": row["quality_status"],
            "cninfo_request_count": row["cninfo_request_count"],
            "notes": row["notes"],
        }
        for row in rows
    ]
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_live_summary(
    paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    gate: str,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    reachable = sum(1 for row in rows if row["reachability_status"] == "reachable")
    resolved = sum(1 for row in rows if row["orgid_resolution_status"] == "resolved")
    failed = len(rows) - resolved
    lines = [
        "# CNINFO B 类 Phase 3 EP002 Reachability Precheck Live 摘要",
        "",
        f"_生成时间：{now}_",
        "",
        "> **性质：** live precheck · EP002 orgId only · **不是 verified** · **不是 retry_v2**",
        "",
        "## 摘要",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        "| mode | precheck_live |",
        f"| candidates | **{len(rows)}** |",
        f"| orgId resolved | **{resolved}** |",
        f"| orgId failed | **{failed}** |",
        f"| reachable | **{reachable}** |",
        f"| CNINFO requests | **{stats.cninfo_requests}** |",
        "| PDF / OCR / extraction / DB / MinIO / RAG | **0** |",
        (
            f"| execution gate | "
            f"**`b_class_phase3_100_ep002_reachability_precheck_execution_gate = {gate}`** |"
        ),
        "",
        "## Per-Candidate",
        "",
    ]
    for row in rows:
        lines.append(
            f"- {row['precheck_id']} {row['case_id']} ({row['market']}): "
            f"reachability={row['reachability_status']} · "
            f"orgId={row['orgid_resolution_status']}"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if gate == "PASS_WITH_CAVEAT":
        lines.append(
            "- CNINFO/EP002 orgId reachability **partially recovered** (≥60% resolved)"
        )
        lines.append(
            "- Next: retry_v2 isolated **planning** only (**NOT APPROVED**)"
        )
    else:
        lines.append("- Infrastructure **still unstable** (<60% orgId resolved)")
        lines.append("- Do **not** create retry_v2 live package yet")
    lines.extend(
        [
            "",
            "**不是 PASS** · **不是 verified** · **不是 production_ready**",
            "",
        ]
    )
    summary_path = paths["live_summary"]
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CNINFO B-class Phase3 EP002 reachability precheck（dry-run default）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")

    parser.add_argument("--candidates-csv", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument(
        "--request-cap",
        type=int,
        default=MAX_PRECHECK_REQUEST_CAP,
        help="live CNINFO 请求硬上限（最大 16）",
    )
    parser.add_argument(
        "--approve-b-class-phase3-100-ep002-reachability-precheck",
        action="store_true",
        help="显式批准 live precheck",
    )
    parser.add_argument(
        "--approve-b-class-phase3-100-expansion",
        action="store_true",
    )
    parser.add_argument(
        "--approve-b-class-phase3-100-failed-retry",
        action="store_true",
    )
    parser.add_argument("--approve-b-class-phase25-expansion", action="store_true")
    parser.add_argument("--approve-b-class-phase25-failed-retry", action="store_true")
    parser.add_argument("--approve-b-class-tiny-live-validation", action="store_true")
    parser.add_argument("--approve-full-harvest", action="store_true")
    parser.add_argument("--approve-phase2-smoke-harvest", action="store_true")
    parser.add_argument("--approve-phase3-batch-500-harvest", action="store_true")
    parser.add_argument(
        "--approve-a-class-phase2-cninfo-reachability-precheck",
        action="store_true",
    )
    parser.add_argument("--run-ep001-validation", action="store_true")
    parser.add_argument("--run-ep004-validation", action="store_true")
    parser.add_argument("--run-ep005-validation", action="store_true")
    parser.add_argument("--create-retry-v2-universe", action="store_true")
    parser.add_argument("--download-pdf", action="store_true")
    parser.add_argument("--parse-pdf", action="store_true")
    parser.add_argument("--enable-ocr", action="store_true")
    parser.add_argument("--enable-extraction", action="store_true")
    parser.add_argument("--write-db", action="store_true")
    parser.add_argument("--write-minio", action="store_true")
    parser.add_argument("--run-rag", action="store_true")
    parser.add_argument("--mark-verified", action="store_true")
    parser.add_argument("--mark-production-ready", action="store_true")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    enforce_forbidden_options(args)

    if not args.candidates_csv:
        print(f"ERROR: {CANDIDATES_CSV_REQUIRED}", file=sys.stderr)
        return 2

    if args.output_root is None:
        args.output_root = DEFAULT_PRECHECK_OUTPUT_ROOT

    if args.mode == "live":
        enforce_precheck_approval_gate(args)

    ok_root, root_err = validate_precheck_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.candidates_csv):
        print(
            f"ERROR: {CANDIDATES_CSV_NOT_FOUND}: {args.candidates_csv}",
            file=sys.stderr,
        )
        return 2

    normalized_root = _normalize_output_root(args.output_root)
    paths = ensure_output_layout(normalized_root)

    candidates = load_precheck_candidates(args.candidates_csv)
    universe_issues = validate_precheck_candidates(candidates)
    planned_total = compute_planned_request_total(candidates)

    if args.request_cap > MAX_PRECHECK_REQUEST_CAP:
        print(
            f"ERROR: {PRECHECK_REQUEST_CAP_EXCEEDED}: cap={args.request_cap} "
            f"max={MAX_PRECHECK_REQUEST_CAP}",
            file=sys.stderr,
        )
        return 2

    ok_cap, cap_err = validate_request_cap(planned_total, args.request_cap)
    if not ok_cap:
        print(f"ERROR: {cap_err}", file=sys.stderr)
        return 2

    if args.mode == "live":
        if universe_issues:
            for issue in universe_issues:
                print(f"ERROR: {issue}", file=sys.stderr)
            return 2
        stats = tiny_live.LiveStats()
        rows, gate = process_live_precheck(candidates, stats)
        if stats.cninfo_requests > min(args.request_cap, MAX_PRECHECK_REQUEST_CAP):
            print(f"ERROR: {PRECHECK_REQUEST_CAP_EXCEEDED}", file=sys.stderr)
            return 2
        report_path = write_live_report(rows, paths)
        quality_path = write_live_quality_report(rows, paths)
        summary_path = write_live_summary(paths, stats, rows, gate)
        resolved_count = sum(
            1 for row in rows if row["orgid_resolution_status"] == "resolved"
        )
        print(f"mode=precheck_live cases={len(rows)} cninfo_calls={stats.cninfo_requests}")
        print(
            f"orgid_resolved={resolved_count} orgid_failed={len(rows) - resolved_count}"
        )
        print(
            "gate=b_class_phase3_100_ep002_reachability_precheck_execution_gate="
            f"{gate}"
        )
        print(f"report={report_path}")
        print(f"quality={quality_path}")
        print(f"summary={summary_path}")
        if gate == "FAIL_REVIEW_REQUIRED":
            return 1
        return 0

    rows = process_dry_run(candidates, normalized_root, universe_issues)
    report_path = write_dryrun_report(rows, paths)
    summary_path = write_dryrun_summary(
        paths, candidates, universe_issues, planned_total, args.request_cap
    )
    planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
    included = [c for c in candidates if c.precheck_include == "yes"]
    print(
        f"mode=precheck_dry_run cases={len(included)} "
        f"planned_ok={planned_ok} planned_requests={planned_total} cninfo_calls=0"
    )
    print(
        "gate=b_class_phase3_100_ep002_reachability_precheck_runner_gate="
        f"{PRECHECK_RUNNER_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    if universe_issues:
        for issue in universe_issues:
            print(f"universe_issue={issue}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
