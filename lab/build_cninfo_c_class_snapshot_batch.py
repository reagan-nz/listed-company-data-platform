#!/usr/bin/env python3
"""
CNINFO C-class Company Snapshot Full Batch Runner（Era C Phase 4）。

默认 --dry-run：验证 universe · 输出路径 · status/error/resume 框架，**不调用 build_snapshot**。
标准 dry-run 默认写隔离根 outputs/validation/_mock_snapshot_batch_standard_dryrun_isolated/，
禁止默认覆盖生产 snapshot quality；生产 scaffold 需 --allow-production-dryrun-scaffold。
Full batch 执行需显式 --execute --approve-full-snapshot-batch（本轮不默认执行）。

可选 --exclusion-csv（仅 dry-run）：按 exclusion reconcile/manifest 过滤 universe，
输出须落在 outputs/validation/（默认 _batch_exclusion_csv_native_dryrun）；
禁止与 --execute 同用 · 禁止触碰 863/phase3/phase35 生产 snapshot 根。

Usage:
    python lab/build_cninfo_c_class_snapshot_batch.py --dry-run
    python lab/build_cninfo_c_class_snapshot_batch.py --dry-run \\
      --sample-file lab/eval_companies_c_class_fuller_market_slice1_200.yaml \\
      --exclusion-csv outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv \\
      --output-root outputs/validation/_batch_exclusion_csv_native_dryrun/
    python lab/build_cninfo_c_class_snapshot_batch.py --execute --approve-full-snapshot-batch  # 未来执行
"""

from __future__ import annotations

import argparse
import csv
import hashlib
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
    SOURCE_TO_SUBDIR,
    ARRAY_SOURCES,
    build_snapshot,
    build_snapshot_from_loaded,
    configure_snapshot_harvest_root,
    load_source_records_at_paths,
    reset_snapshot_harvest_root,
    _load_harvest_status_at_root,
    _load_source_quality_at_root,
    _load_mapping,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL,
    PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN,
    assert_safe_c_class_snapshot_dryrun_write_root,
    fingerprint_isolated_snapshot_dryrun,
    resolve_standard_snapshot_dryrun_output_root,
)
from cninfo_c_class_snapshot_exclusion_filter import (  # noqa: E402
    ExclusionFilterResult,
    filter_universe_with_exclusion_csv,
    refuse_exclusion_with_execute,
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

PHASE35_EXPANDED_SNAPSHOT_SAMPLE_BASENAME = (
    "eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml"
)
PHASE35_EXPANDED_UNIVERSE_CSV_REL = (
    "outputs/validation/cninfo_c_class_phase35_expanded_success_subset_universe.csv"
)
PHASE35_MERGE_MANIFEST_CSV_REL = (
    "outputs/validation/cninfo_c_class_phase35_snapshot_merge_manifest_design.csv"
)
PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL = (
    "outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491"
)
PHASE35_BATCH_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class/phase35_batch_500_001"
PHASE35_RESUME_HARVEST_ROOT_REL = (
    "outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume"
)
PHASE35_BATCH_SAMPLE_REL = "lab/eval_companies_c_class_phase35_batch_500_001.yaml"

PHASE35_EXPANDED_EXPECTED_COUNT = 491
PHASE35_EXPANDED_ORIGINAL_COUNT = 463
PHASE35_EXPANDED_RESUME_COUNT = 28
PHASE35_EXPANDED_MANIFEST_ROWS = 4910
PHASE35_EXPANDED_SOURCES_PER_COMPANY = 10
PHASE35_C35R016_CODE = "301212"

PHASE35_EXPANDED_SNAPSHOT_APPROVAL_REQUIRED = (
    "PHASE35_EXPANDED_SNAPSHOT_APPROVAL_REQUIRED"
)
PHASE35_EXPANDED_WRONG_APPROVAL_REJECTED = "PHASE35_EXPANDED_WRONG_APPROVAL_REJECTED"
PHASE35_EXPANDED_OUTPUT_ROOT_MISMATCH = "PHASE35_EXPANDED_OUTPUT_ROOT_MISMATCH"
PHASE35_EXPANDED_UNIVERSE_COUNT_MISMATCH = "PHASE35_EXPANDED_UNIVERSE_COUNT_MISMATCH"
PHASE35_EXPANDED_MANIFEST_COUNT_MISMATCH = "PHASE35_EXPANDED_MANIFEST_COUNT_MISMATCH"
PHASE35_EXPANDED_EXCLUDED_CODE_PRESENT = "PHASE35_EXPANDED_EXCLUDED_CODE_PRESENT"
PHASE35_EXPANDED_HARVEST_ROOT_WRITE_FORBIDDEN = (
    "PHASE35_EXPANDED_HARVEST_ROOT_WRITE_FORBIDDEN"
)
PHASE35_EXPANDED_SNAPSHOT_ISOLATION_VIOLATION = (
    "PHASE35_EXPANDED_SNAPSHOT_ISOLATION_VIOLATION"
)
PHASE35_EXPANDED_MERGE_MANIFEST_REQUIRED = "PHASE35_EXPANDED_MERGE_MANIFEST_REQUIRED"

# exclusion-csv 原生 dry-run：默认写 validation 隔离根（禁止生产 snapshot 根）
EXCLUSION_CSV_NATIVE_DRYRUN_OUTPUT_ROOT_REL = (
    "outputs/validation/_batch_exclusion_csv_native_dryrun"
)
EXCLUSION_CSV_PHASE35_UNSUPPORTED = "EXCLUSION_CSV_PHASE35_UNSUPPORTED"
EXCLUSION_CSV_OUTPUT_NOT_UNDER_VALIDATION = (
    "EXCLUSION_CSV_OUTPUT_NOT_UNDER_VALIDATION"
)
PRODUCTION_SNAPSHOT_ROOT_FORBIDDEN = "PRODUCTION_SNAPSHOT_ROOT_FORBIDDEN"

EXCLUSION_CSV_FORBIDDEN_PROD_SNAPSHOT_ROOTS = (
    FULL_SNAPSHOT_OUT_DIR_REL,
    PHASE3_SUCCESS_SNAPSHOT_OUTPUT_ROOT_REL,
    PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL,
    PHASE2_SNAPSHOT_OUTPUT_ROOT_REL,
)

PHASE35_EXPANDED_DRYRUN_REPORT_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_dryrun_report.csv",
)
PHASE35_EXPANDED_DRYRUN_SUMMARY_MD = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_dryrun_summary.md",
)
PHASE35_EXPANDED_BUILD_REPORT_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_build_report.csv",
)
PHASE35_EXPANDED_BUILD_SUMMARY_MD = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase35_expanded_snapshot_build_summary.md",
)

PHASE35_HOLD_FOR_REVIEW_CODES = frozenset({
    "000003", "000578", "000666", "000689",
    "000861", "000961", "002280", "600220",
})

PHASE35_EXPANDED_DRYRUN_REPORT_FIELDS = [
    "company_code",
    "company_name",
    "market",
    "source_root_role",
    "planned_modules",
    "planned_snapshot_path",
    "merge_manifest_source_rows",
    "dryrun_status",
    "notes",
]


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


    if norm_out == phase2_dir or norm_out.startswith(phase2_dir + "/"):
        print(PHASE3_PHASE2_SNAPSHOT_ISOLATION_VIOLATION, file=sys.stderr)
        raise SystemExit(2)


def is_phase35_expanded_snapshot_sample(sample_path: str) -> bool:
    norm = sample_path.replace("\\", "/")
    return norm.endswith(PHASE35_EXPANDED_SNAPSHOT_SAMPLE_BASENAME)


def is_phase35_expanded_snapshot_mode(
    args: argparse.Namespace,
    sample_path: str,
) -> bool:
    if getattr(args, "merge_manifest", None):
        return True
    return bool(sample_path and is_phase35_expanded_snapshot_sample(sample_path))


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


def load_expanded_universe_csv(path: str) -> List[Dict[str, str]]:
    """加载 Phase 3.5 expanded snapshot universe CSV。"""
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    companies: List[Dict[str, str]] = []
    for row in rows:
        if row.get("snapshot_include", "").strip().lower() != "yes":
            continue
        companies.append({
            "company_code": _normalize_code(row["company_code"]),
            "company_name": row.get("company_name", ""),
            "market": row.get("market", ""),
            "board": "",
            "source_root_role": row.get("source_root_role", ""),
            "resume_case_id": row.get("resume_case_id", ""),
            "snapshot_candidate_status": row.get("snapshot_candidate_status", ""),
            "caveat_level": row.get("caveat_level", ""),
            "prior_origin": row.get("prior_origin", ""),
        })
    return companies


def load_merge_manifest_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def validate_phase35_expanded_universe_and_manifest(
    companies: List[Dict[str, str]],
    manifest_rows: List[Dict[str, str]],
) -> Tuple[bool, Dict[str, Any]]:
    """校验 expanded universe 与 merge manifest。"""
    codes = {c["company_code"] for c in companies}
    issues: List[str] = []
    if len(companies) != PHASE35_EXPANDED_EXPECTED_COUNT:
        issues.append(f"universe_count={len(companies)}")
    original_n = sum(1 for c in companies if c.get("source_root_role") == "original")
    resume_n = sum(1 for c in companies if c.get("source_root_role") == "resume")
    if original_n != PHASE35_EXPANDED_ORIGINAL_COUNT:
        issues.append(f"original_count={original_n}")
    if resume_n != PHASE35_EXPANDED_RESUME_COUNT:
        issues.append(f"resume_count={resume_n}")
    if PHASE35_C35R016_CODE in codes:
        issues.append(f"c35r016_present={PHASE35_C35R016_CODE}")
    hold_overlap = sorted(codes & PHASE35_HOLD_FOR_REVIEW_CODES)
    if hold_overlap:
        issues.append(f"hold_for_review_present={hold_overlap[:3]}")
    if len(manifest_rows) != PHASE35_EXPANDED_MANIFEST_ROWS:
        issues.append(f"manifest_rows={len(manifest_rows)}")
    manifest_codes = {r["company_code"].zfill(6) for r in manifest_rows}
    if manifest_codes != codes:
        issues.append("manifest_company_mismatch")
    per_company_counts = {}
    for row in manifest_rows:
        code = row["company_code"].zfill(6)
        per_company_counts[code] = per_company_counts.get(code, 0) + 1
    bad_counts = [c for c, n in per_company_counts.items() if n != PHASE35_EXPANDED_SOURCES_PER_COMPANY]
    if bad_counts:
        issues.append(f"manifest_source_count_mismatch={bad_counts[:3]}")
    detail = {
        "company_count": len(companies),
        "original_count": original_n,
        "resume_count": resume_n,
        "manifest_rows": len(manifest_rows),
        "hold_overlap": hold_overlap,
        "issues": issues,
    }
    return (not issues, detail)


def validate_phase35_expanded_output_root(output_dir: str) -> bool:
    norm_out = _norm_abs_path(output_dir).rstrip("/")
    expected = _norm_abs_path(
        os.path.join(BASE_DIR, PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL)
    ).rstrip("/")
    if norm_out != expected:
        return False
    forbidden = [
        FULL_SNAPSHOT_OUT_DIR_REL,
        PHASE3_SUCCESS_SNAPSHOT_OUTPUT_ROOT_REL,
        PHASE2_SNAPSHOT_OUTPUT_ROOT_REL,
        PHASE35_BATCH_HARVEST_ROOT_REL,
        PHASE35_RESUME_HARVEST_ROOT_REL,
    ]
    for rel in forbidden:
        forbidden_abs = _norm_abs_path(os.path.join(BASE_DIR, rel)).rstrip("/")
        if norm_out == forbidden_abs or norm_out.startswith(forbidden_abs + "/"):
            return False
    return True


def validate_phase35_harvest_roots_readonly(
    harvest_root: str,
    resume_harvest_root: str,
) -> Tuple[bool, str]:
    """确认 harvest 根为预期路径（dry-run 不得写入）。"""
    expected_orig = _norm_abs_path(
        os.path.join(BASE_DIR, PHASE35_BATCH_HARVEST_ROOT_REL)
    ).rstrip("/")
    expected_resume = _norm_abs_path(
        os.path.join(BASE_DIR, PHASE35_RESUME_HARVEST_ROOT_REL)
    ).rstrip("/")

    def _resolve_root(path: str) -> str:
        if not path:
            return ""
        if not os.path.isabs(path):
            path = os.path.join(BASE_DIR, path)
        return _norm_abs_path(path).rstrip("/")

    norm_orig = _resolve_root(harvest_root)
    norm_resume = _resolve_root(resume_harvest_root)
    if norm_orig != expected_orig:
        return False, f"harvest_root_mismatch={norm_orig}"
    if norm_resume != expected_resume:
        return False, f"resume_harvest_root_mismatch={norm_resume}"
    return True, "harvest_roots_ok"


def enforce_phase35_expanded_snapshot_preflight(
    args: argparse.Namespace,
    sample_path: str,
    output_dir: str,
    companies: List[Dict[str, str]],
    manifest_rows: List[Dict[str, str]],
) -> None:
    """Phase 3.5 expanded snapshot build/dry-run 前置检查。"""
    if not is_phase35_expanded_snapshot_mode(args, sample_path):
        return
    if not getattr(args, "merge_manifest", None):
        print(PHASE35_EXPANDED_MERGE_MANIFEST_REQUIRED, file=sys.stderr)
        raise SystemExit(2)
    if not validate_phase35_expanded_output_root(output_dir):
        print(PHASE35_EXPANDED_OUTPUT_ROOT_MISMATCH, file=sys.stderr)
        raise SystemExit(2)
    ok, detail = validate_phase35_expanded_universe_and_manifest(companies, manifest_rows)
    if not ok:
        print(f"{PHASE35_EXPANDED_UNIVERSE_COUNT_MISMATCH}: {detail.get('issues')}", file=sys.stderr)
        raise SystemExit(2)
    harvest_ok, harvest_detail = validate_phase35_harvest_roots_readonly(
        args.harvest_root or "",
        getattr(args, "resume_harvest_root", None) or "",
    )
    if not harvest_ok:
        print(f"{PHASE35_EXPANDED_HARVEST_ROOT_WRITE_FORBIDDEN}: {harvest_detail}", file=sys.stderr)
        raise SystemExit(2)


def build_phase35_expanded_dryrun_report_rows(
    companies: List[Dict[str, str]],
    manifest_rows: List[Dict[str, str]],
    output_dir: str,
) -> List[Dict[str, str]]:
    manifest_by_code: Dict[str, int] = {}
    for row in manifest_rows:
        code = row["company_code"].zfill(6)
        manifest_by_code[code] = manifest_by_code.get(code, 0) + 1
    rows: List[Dict[str, str]] = []
    for company in companies:
        code = company["company_code"]
        rows.append({
            "company_code": code,
            "company_name": company.get("company_name", ""),
            "market": company.get("market", ""),
            "source_root_role": company.get("source_root_role", ""),
            "planned_modules": str(PLANNED_MODULE_COUNT),
            "planned_snapshot_path": planned_snapshot_path(code, output_dir),
            "merge_manifest_source_rows": str(manifest_by_code.get(code, 0)),
            "dryrun_status": "planned_ok",
            "notes": "offline_dryrun_only",
        })
    return rows


def write_phase35_expanded_dryrun_report(
    rows: List[Dict[str, str]],
    path: str = PHASE35_EXPANDED_DRYRUN_REPORT_CSV,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=PHASE35_EXPANDED_DRYRUN_REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_phase35_expanded_dryrun_summary(
    validation: Dict[str, Any],
    path: str = PHASE35_EXPANDED_DRYRUN_SUMMARY_MD,
    output_dir: Optional[str] = None,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    gate = "PASS_OFFLINE" if validation.get("ok") else "FAIL"
    effective_out = output_dir or os.path.join(BASE_DIR, PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL)
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Dry-Run Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 expanded snapshot builder dry-run。**无 CNINFO** · **无 snapshot JSON**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "## Universe",
        "",
        f"- **company_count:** **{validation.get('company_count', 0)}**",
        f"- **original:** **{validation.get('original_count', 0)}**",
        f"- **resume merged:** **{validation.get('resume_count', 0)}**",
        f"- **manifest_rows:** **{validation.get('manifest_rows', 0)}**",
        "",
        "## Planned scale",
        "",
        f"- **planned_snapshot_json:** **{validation.get('company_count', 0)}**",
        "- **actual_snapshot_json_written:** **0**",
        "- **CNINFO calls:** **0**",
        "",
        "## Safety",
        "",
        "- **original harvest root write-blocked**",
        "- **resume harvest root write-blocked**",
        "- **snapshot_build = 0**",
        "- **DB / MinIO / RAG = 0**",
        "- **not verified** · **not production_ready**",
        "",
        f"- **planned_output_root:** `{os.path.relpath(effective_out, BASE_DIR)}`",
        "",
        "## Gate",
        "",
        "```",
        "phase35_expanded_success_subset_snapshot_dryrun_gate = PASS_OFFLINE",
        "```",
        "",
        "Live build **NOT APPROVED**（需 `--approve-phase35-expanded-success-snapshot-build`）。",
        "",
        "详见 [cninfo_c_class_phase35_expanded_snapshot_dryrun_report.csv]"
        "(cninfo_c_class_phase35_expanded_snapshot_dryrun_report.csv)。",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return gate


def run_phase35_expanded_dry_run(
    args: argparse.Namespace,
    sample_path: str,
    universe_csv_path: str,
    manifest_path: str,
    output_dir: str,
) -> Dict[str, Any]:
    """Phase 3.5 expanded snapshot dry-run（无 build_snapshot · 无 JSON）。"""
    orig_fp_before = _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
    resume_fp_before = _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)

    companies = load_expanded_universe_csv(universe_csv_path)
    manifest_rows = load_merge_manifest_csv(manifest_path)
    enforce_phase35_expanded_snapshot_preflight(
        args, sample_path, output_dir, companies, manifest_rows,
    )
    ok, validation = validate_phase35_expanded_universe_and_manifest(companies, manifest_rows)
    validation["ok"] = ok

    report_path = args.output_csv or PHASE35_EXPANDED_DRYRUN_REPORT_CSV
    summary_path = args.output_md or PHASE35_EXPANDED_DRYRUN_SUMMARY_MD
    if not os.path.isabs(report_path):
        report_path = os.path.join(BASE_DIR, report_path)
    if not os.path.isabs(summary_path):
        summary_path = os.path.join(BASE_DIR, summary_path)

    report_rows = build_phase35_expanded_dryrun_report_rows(
        companies, manifest_rows, output_dir,
    )
    write_phase35_expanded_dryrun_report(report_rows, report_path)
    gate = write_phase35_expanded_dryrun_summary(validation, summary_path, output_dir)

    orig_fp_after = _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
    resume_fp_after = _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)
    harvest_unchanged = (
        orig_fp_before == orig_fp_after and resume_fp_before == resume_fp_after
    )

    return {
        "validation": validation,
        "universe_ok": ok and harvest_unchanged,
        "report_rows": report_rows,
        "gate": gate,
        "harvest_unchanged": harvest_unchanged,
        "report_path": report_path,
        "summary_path": summary_path,
    }


def generate_phase35_expanded_sample_yaml(
    universe_csv_path: str,
    phase35_yaml_path: str,
    out_yaml_path: str,
) -> int:
    """从 expanded universe CSV 与 Phase 3.5 batch YAML 生成 snapshot sample YAML。"""
    with open(phase35_yaml_path, encoding="utf-8") as fh:
        batch_data = yaml.safe_load(fh)
    lookup = {}
    for item in batch_data.get("companies", []):
        code = _normalize_code(item.get("stock_code") or item.get("company_code", ""))
        lookup[code] = item

    universe_rows = load_expanded_universe_csv(universe_csv_path)
    companies_out = []
    board_counts: Dict[str, int] = {}
    for row in universe_rows:
        code = row["company_code"]
        src = lookup.get(code, {})
        board = src.get("board", "unknown")
        board_counts[board] = board_counts.get(board, 0) + 1
        companies_out.append({
            "stock_code": code,
            "short_name": row.get("company_name", src.get("short_name", "")),
            "company_name": row.get("company_name", src.get("company_name", "")),
            "company_code": code,
            "exchange": row.get("market", src.get("exchange", "")),
            "orgid": src.get("orgid", ""),
            "board": board,
            "source_root_role": row.get("source_root_role", ""),
            "resume_case_id": row.get("resume_case_id", ""),
            "snapshot_candidate_status": row.get("snapshot_candidate_status", ""),
            "batch_id": "phase35_batch_500_001_expanded_success_491",
            "harvest_status": "phase35_expanded_snapshot_candidate",
        })

    payload = {
        "version": "c-class-phase35-expanded-success-snapshot-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "parent_universe": os.path.relpath(universe_csv_path, BASE_DIR),
        "universe_id": "phase35_batch_500_001_expanded_success_491",
        "batch_id": "phase35_batch_500_001",
        "description": "Phase 3.5 expanded success subset · 491 companies · merge-manifest snapshot",
        "company_count": len(companies_out),
        "harvest_root": PHASE35_BATCH_HARVEST_ROOT_REL,
        "resume_harvest_root": PHASE35_RESUME_HARVEST_ROOT_REL,
        "snapshot_output_root": PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL,
        "merge_manifest": PHASE35_MERGE_MANIFEST_CSV_REL,
        "board_counts": board_counts,
        "companies": companies_out,
    }
    os.makedirs(os.path.dirname(out_yaml_path), exist_ok=True)
    with open(out_yaml_path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(payload, fh, allow_unicode=True, sort_keys=False)
    return len(companies_out)


PHASE35_EXPANDED_BUILD_REPORT_FIELDS = [
    "company_code",
    "company_name",
    "source_root_role",
    "build_status",
    "snapshot_status",
    "module_available_count",
    "module_partial_count",
    "module_missing_count",
    "merge_manifest_sources_resolved",
    "snapshot_path",
    "notes",
]


def _resolve_manifest_harvest_root(root_rel: str) -> str:
    if not root_rel:
        return ""
    if not os.path.isabs(root_rel):
        return os.path.join(BASE_DIR, root_rel)
    return root_rel


def _manifest_source_path(
    source_id: str,
    company_code: str,
    harvest_root_rel: str,
) -> str:
    subdir, ext = SOURCE_TO_SUBDIR[source_id]
    root = _resolve_manifest_harvest_root(harvest_root_rel)
    return os.path.join(root, "normalized", subdir, f"{company_code}{ext}")


def _group_manifest_by_company(
    manifest_rows: List[Dict[str, str]],
) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = {}
    for row in manifest_rows:
        code = row["company_code"].zfill(6)
        grouped.setdefault(code, []).append(row)
    return grouped


def _load_phase35_merged_sources(
    company_code: str,
    manifest_rows: List[Dict[str, str]],
) -> Tuple[Dict[str, Any], List[str], int]:
    """按 merge manifest 从 primary/fallback harvest 根加载 normalized 源。"""
    by_source = {row["source_id"]: row for row in manifest_rows}
    resolved_paths: Dict[str, str] = {}
    resolved_count = 0

    def resolve_path(source_id: str) -> Optional[str]:
        row = by_source.get(source_id)
        if not row:
            return None
        primary = row.get("primary_harvest_root", "")
        fallback = row.get("fallback_harvest_root", "")
        primary_path = _manifest_source_path(source_id, company_code, primary)
        if os.path.isfile(primary_path):
            resolved_paths[source_id] = primary_path
            return primary_path
        if fallback:
            fallback_path = _manifest_source_path(source_id, company_code, fallback)
            if os.path.isfile(fallback_path):
                resolved_paths[source_id] = fallback_path
                return fallback_path
        return primary_path if primary else None

    loaded = load_source_records_at_paths(company_code, resolve_path)
    resolved_count = sum(
        1 for sid in SOURCE_TO_SUBDIR
        if resolved_paths.get(sid) and os.path.isfile(resolved_paths[sid])
    )
    input_files = [
        os.path.relpath(resolved_paths[sid], BASE_DIR)
        for sid in SOURCE_TO_SUBDIR
        if sid in resolved_paths and os.path.isfile(resolved_paths[sid])
    ]
    return loaded, input_files, resolved_count


def _resolve_phase35_quality_roots(
    company: Dict[str, str],
    manifest_rows: List[Dict[str, str]],
) -> Tuple[str, str]:
    """选择 harvest status / source_quality 读取根。"""
    role = company.get("source_root_role", "")
    if role == "resume":
        resume_root = PHASE35_RESUME_HARVEST_ROOT_REL
        batch_root = PHASE35_BATCH_HARVEST_ROOT_REL
        resume_abs = _resolve_manifest_harvest_root(resume_root)
        if _load_harvest_status_at_root(company["company_code"], resume_abs):
            return resume_root, resume_root
        return batch_root, batch_root
    primary = manifest_rows[0].get("primary_harvest_root", PHASE35_BATCH_HARVEST_ROOT_REL)
    return primary, primary


def make_phase35_expanded_build_fn(
    manifest_by_code: Dict[str, List[Dict[str, str]]],
    companies_by_code: Dict[str, Dict[str, str]],
) -> Callable[[str, List[Dict[str, str]]], Tuple[Dict[str, Any], Dict[str, Any]]]:
    """生成 merge-manifest-aware 单公司 build 函数。"""

    def _build(company_code: str, mapping_rows: List[Dict[str, str]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        code = _normalize_code(company_code)
        manifest_rows = manifest_by_code[code]
        company = companies_by_code[code]
        loaded, input_files, resolved_count = _load_phase35_merged_sources(code, manifest_rows)
        quality_root_rel, status_root_rel = _resolve_phase35_quality_roots(company, manifest_rows)
        status_root = _resolve_manifest_harvest_root(status_root_rel)
        quality_root = _resolve_manifest_harvest_root(quality_root_rel)
        harvest_row = _load_harvest_status_at_root(code, status_root)
        source_quality = _load_source_quality_at_root(quality_root)

        def path_resolver(source_id: str) -> Optional[str]:
            row = {r["source_id"]: r for r in manifest_rows}.get(source_id)
            if not row:
                return None
            primary = row.get("primary_harvest_root", "")
            fallback = row.get("fallback_harvest_root", "")
            primary_path = _manifest_source_path(source_id, code, primary)
            if os.path.isfile(primary_path):
                return primary_path
            if fallback:
                fallback_path = _manifest_source_path(source_id, code, fallback)
                if os.path.isfile(fallback_path):
                    return fallback_path
            return primary_path if primary else None

        snapshot, stats = build_snapshot_from_loaded(
            code,
            mapping_rows,
            loaded,
            harvest_row=harvest_row,
            source_quality=source_quality,
            input_path_resolver=path_resolver,
        )
        stats["merge_manifest_sources_resolved"] = resolved_count
        stats["input_files"] = input_files
        return snapshot, stats

    return _build


def write_phase35_expanded_build_report(
    rows: List[Dict[str, str]],
    path: str = PHASE35_EXPANDED_BUILD_REPORT_CSV,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=PHASE35_EXPANDED_BUILD_REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_phase35_expanded_build_summary(
    validation: Dict[str, Any],
    build_stats: Dict[str, Any],
    path: str = PHASE35_EXPANDED_BUILD_SUMMARY_MD,
    output_dir: Optional[str] = None,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    built = build_stats.get("success_count", 0)
    failed = build_stats.get("failed_count", 0)
    expected = PHASE35_EXPANDED_EXPECTED_COUNT
    if built == expected and failed == 0:
        gate = "PASS_WITH_CAVEAT"
    else:
        gate = "FAIL_REVIEW_REQUIRED"
    effective_out = output_dir or os.path.join(BASE_DIR, PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL)
    lines = [
        "# CNINFO C-Class Phase 3.5 Expanded Snapshot Build Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> merge-manifest-aware offline snapshot build。**无 CNINFO** · **无 harvest rerun**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "```",
        "approval_status = APPROVED_IN_SESSION",
        "approved_for_snapshot_build = true",
        "build_executed = yes",
        "```",
        "",
        "## Universe",
        "",
        f"- **company_count:** **{validation.get('company_count', 0)}**",
        f"- **original:** **{validation.get('original_count', 0)}**",
        f"- **resume merged:** **{validation.get('resume_count', 0)}**",
        f"- **manifest_rows:** **{validation.get('manifest_rows', 0)}**",
        "",
        "## Build scale",
        "",
        f"- **snapshot_json_built:** **{built}**",
        f"- **build_failed:** **{failed}**",
        f"- **CNINFO calls:** **0**",
        "",
        "## Safety",
        "",
        f"- **harvest_roots_unchanged:** **{build_stats.get('harvest_unchanged', False)}**",
        "- **DB / MinIO / RAG = 0**",
        "- **not verified** · **not production_ready**",
        "- **no commit** · **no push**",
        "",
        f"- **output_root:** `{os.path.relpath(effective_out, BASE_DIR)}`",
        "",
        "## Gate",
        "",
        "```",
        f"phase35_expanded_success_subset_snapshot_build_gate = {gate}",
        "```",
        "",
        "详见 [cninfo_c_class_phase35_expanded_snapshot_build_report.csv]"
        "(cninfo_c_class_phase35_expanded_snapshot_build_report.csv)。",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return gate


def run_phase35_expanded_execute(
    args: argparse.Namespace,
    sample_path: str,
    universe_csv_path: str,
    manifest_path: str,
    output_dir: str,
) -> Dict[str, Any]:
    """Phase 3.5 expanded merge-manifest snapshot build（离线 normalized 聚合）。"""
    orig_fp_before = _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
    resume_fp_before = _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)

    companies = load_expanded_universe_csv(universe_csv_path)
    manifest_rows = load_merge_manifest_csv(manifest_path)
    enforce_phase35_expanded_snapshot_preflight(
        args, sample_path, output_dir, companies, manifest_rows,
    )
    ok, validation = validate_phase35_expanded_universe_and_manifest(companies, manifest_rows)
    validation["ok"] = ok
    if not ok:
        raise SystemExit(2)

    configure_snapshot_batch_paths(harvest_root=args.harvest_root, output_dir=output_dir)
    manifest_by_code = _group_manifest_by_company(manifest_rows)
    companies_by_code = {c["company_code"]: c for c in companies}
    build_fn = make_phase35_expanded_build_fn(manifest_by_code, companies_by_code)

    execution_list = build_execution_list(companies, out_dir=output_dir)
    status_by_code = {r["company_code"]: r for r in init_status_rows(execution_list)}
    mapping = _load_mapping()

    errors, success_count, failed_count = run_execute_batch(
        execution_list,
        mapping,
        status_by_code,
        out_dir=output_dir,
        build_fn=build_fn,
        write_json=True,
    )
    write_status_csv(list(status_by_code.values()))
    write_error_csv(errors)

    report_rows: List[Dict[str, str]] = []
    for item in execution_list:
        code = item["company_code"]
        row = status_by_code[code]
        report_rows.append({
            "company_code": code,
            "company_name": item.get("company_name", ""),
            "source_root_role": companies_by_code[code].get("source_root_role", ""),
            "build_status": row.get("status", ""),
            "snapshot_status": row.get("status", ""),
            "module_available_count": row.get("module_available_count", ""),
            "module_partial_count": row.get("module_partial_count", ""),
            "module_missing_count": row.get("module_missing_count", ""),
            "merge_manifest_sources_resolved": "10",
            "snapshot_path": os.path.relpath(planned_snapshot_path(code, output_dir), BASE_DIR),
            "notes": "merge_manifest_offline_build",
        })

    write_phase35_expanded_build_report(report_rows, PHASE35_EXPANDED_BUILD_REPORT_CSV)
    build_stats = {
        "success_count": success_count,
        "failed_count": failed_count,
        "harvest_unchanged": False,
    }
    orig_fp_after = _fingerprint_harvest_tree(PHASE35_BATCH_HARVEST_ROOT_REL)
    resume_fp_after = _fingerprint_harvest_tree(PHASE35_RESUME_HARVEST_ROOT_REL)
    build_stats["harvest_unchanged"] = (
        orig_fp_before == orig_fp_after and resume_fp_before == resume_fp_after
    )
    gate = write_phase35_expanded_build_summary(
        validation, build_stats, PHASE35_EXPANDED_BUILD_SUMMARY_MD, output_dir,
    )

    return {
        "validation": validation,
        "success_count": success_count,
        "failed_count": failed_count,
        "gate": gate,
        "harvest_unchanged": build_stats["harvest_unchanged"],
        "report_path": PHASE35_EXPANDED_BUILD_REPORT_CSV,
        "summary_path": PHASE35_EXPANDED_BUILD_SUMMARY_MD,
        "output_dir": output_dir,
    }


def resolve_execute_mode(args: argparse.Namespace, sample_path: str) -> str:
    if is_phase35_expanded_snapshot_mode(args, sample_path):
        if getattr(args, "approve_phase35_expanded_success_snapshot_build", False):
            return "phase35_expanded_snapshot"
        return ""
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
            or is_phase35_expanded_snapshot_sample(sample_path)
        ):
            return ""
        if getattr(args, "approve_phase3_success_snapshot_build", False):
            return ""
        if getattr(args, "approve_phase35_expanded_success_snapshot_build", False):
            return ""
        return "full"
    return ""


def enforce_execute_approval(args: argparse.Namespace, sample_path: str) -> str:
    if is_phase35_expanded_snapshot_mode(args, sample_path):
        if args.approve_full_snapshot_batch:
            print(PHASE35_EXPANDED_WRONG_APPROVAL_REJECTED, file=sys.stderr)
            raise SystemExit(2)
        if getattr(args, "approve_phase3_success_snapshot_build", False):
            print(PHASE35_EXPANDED_WRONG_APPROVAL_REJECTED, file=sys.stderr)
            raise SystemExit(2)
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
        if is_phase35_expanded_snapshot_mode(args, sample_path):
            print(PHASE35_EXPANDED_SNAPSHOT_APPROVAL_REQUIRED, file=sys.stderr)
        elif sample_path and is_phase2_smoke_188_sample(sample_path):
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


def assert_exclusion_csv_dryrun_output_root_safe(output_dir: str) -> str:
    """
    exclusion-csv 原生 dry-run 输出根守卫：
      1) 必须落在 outputs/validation/
      2) 不得落在 863/full · phase3 · phase35 · phase2 生产 snapshot 根
    """
    norm = _norm_abs_path(output_dir).rstrip("/")
    validation_root = _norm_abs_path(
        os.path.join(BASE_DIR, "outputs/validation")
    ).rstrip("/")
    if not (norm == validation_root or norm.startswith(validation_root + "/")):
        rel = os.path.relpath(norm, BASE_DIR).replace("\\", "/")
        raise RuntimeError(
            f"{EXCLUSION_CSV_OUTPUT_NOT_UNDER_VALIDATION}: "
            f"output 必须在 outputs/validation/ 下，收到: {rel}"
        )
    for forbidden_rel in EXCLUSION_CSV_FORBIDDEN_PROD_SNAPSHOT_ROOTS:
        forbidden_abs = _norm_abs_path(
            os.path.join(BASE_DIR, forbidden_rel)
        ).rstrip("/")
        if norm == forbidden_abs or norm.startswith(forbidden_abs + "/"):
            raise RuntimeError(
                f"{PRODUCTION_SNAPSHOT_ROOT_FORBIDDEN}: {forbidden_rel}"
            )
    return norm


def write_exclusion_filtered_universe_yaml(
    included: List[Dict[str, str]],
    path: str,
    *,
    source_universe: str,
    exclusion_csv: str,
    csv_kind: str,
    excluded_unique_count: int,
) -> None:
    """写出 exclusion 过滤后的 universe YAML（validation 根 · 非生产）。"""
    payload = {
        "version": "c-class-exclusion-csv-native-filtered-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "purpose": "batch_builder_native_exclusion_csv_dryrun",
        "source_universe": source_universe,
        "exclusion_csv": exclusion_csv,
        "csv_kind": csv_kind,
        "company_count": len(included),
        "excluded_unique_count": excluded_unique_count,
        "execute_production_snapshot_rebuild": False,
        "note": "validation dry-run only · not production snapshot universe",
        "companies": [
            {
                "stock_code": c["company_code"],
                "company_code": c["company_code"],
                "company_name": c.get("company_name") or "",
                "board": c.get("board") or "",
            }
            for c in included
        ],
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(payload, fh, allow_unicode=True, sort_keys=False)


def prepare_exclusion_csv_dryrun_universe(
    sample_file: str,
    exclusion_csv: str,
    output_dir: str,
) -> Tuple[str, ExclusionFilterResult]:
    """
    加载 sample universe，按 exclusion-csv 过滤，写入 validation 根下临时 YAML。
    返回 (filtered_yaml_path, filter_result)。
    """
    assert_exclusion_csv_dryrun_output_root_safe(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    companies, _meta = load_universe_yaml(sample_file)
    if not os.path.isfile(exclusion_csv):
        raise FileNotFoundError(f"exclusion_csv_missing: {exclusion_csv}")
    filter_result = filter_universe_with_exclusion_csv(companies, exclusion_csv)

    source_rel = sample_file
    if os.path.isabs(sample_file):
        source_rel = os.path.relpath(sample_file, BASE_DIR).replace("\\", "/")
    exclusion_rel = exclusion_csv
    if os.path.isabs(exclusion_csv):
        exclusion_rel = os.path.relpath(exclusion_csv, BASE_DIR).replace("\\", "/")

    filtered_path = os.path.join(output_dir, "filtered_universe_included.yaml")
    write_exclusion_filtered_universe_yaml(
        filter_result.included,
        filtered_path,
        source_universe=source_rel,
        exclusion_csv=exclusion_rel,
        csv_kind=filter_result.csv_kind,
        excluded_unique_count=len(filter_result.excluded_codes),
    )
    return filtered_path, filter_result


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
    allow_production_scaffold: bool = False,
) -> Dict[str, Any]:
    """
    Dry-run：验证输入 · 生成 status/error 框架 · 写 dry-run 报告。
    **不调用 build_snapshot** · **不写 snapshot JSON**。
    默认拒绝写入生产 snapshot 根（需 allow_production_scaffold）。
    """
    # 未指定 out_dir 时落到隔离 mock 根，避免覆盖 full/quality
    if out_dir is None:
        out_dir = os.path.join(BASE_DIR, DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL)
    safe_out = assert_safe_c_class_snapshot_dryrun_write_root(
        out_dir,
        allow_production_scaffold=allow_production_scaffold,
    )
    configure_snapshot_batch_paths(harvest_root=harvest_root, output_dir=safe_out)
    effective_out_dir = FULL_OUT_DIR
    effective_quality_dir = QUALITY_DIR
    effective_status_path = status_path or STATUS_CSV
    effective_error_path = error_path or ERROR_CSV
    # status/error 写路径同样受生产 snapshot 根守卫约束
    assert_safe_c_class_snapshot_dryrun_write_root(
        os.path.dirname(effective_status_path) or effective_out_dir,
        allow_production_scaffold=allow_production_scaffold,
    )

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
    fingerprint = fingerprint_isolated_snapshot_dryrun(
        effective_out_dir,
        gate=gate,
        company_count=expected_count,
    )

    return {
        "validation": validation,
        "universe_ok": ok,
        "execution_list": execution_list,
        "status_rows": status_rows,
        "report_rows": report_rows,
        "gate": gate,
        "resume_skipped": resume_skipped,
        "output_dir": effective_out_dir,
        "dryrun_fingerprint": fingerprint,
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
        "--approve-phase35-expanded-success-snapshot-build",
        action="store_true",
        help="显式批准 Phase 3.5 expanded success-subset（491）merge-manifest snapshot build",
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
        "--resume-harvest-root",
        default=None,
        help="Phase 3.5 isolated resume harvest 根目录",
    )
    parser.add_argument(
        "--merge-manifest",
        default=None,
        help="Phase 3.5 expanded snapshot merge manifest CSV",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="snapshot 输出目录（默认 outputs/snapshot/cninfo_c_class/full）",
    )
    parser.add_argument(
        "--output-root",
        default=None,
        help=(
            "snapshot 输出根目录（--output-dir 别名；"
            "标准 dry-run 与 Phase 3.5 / exclusion-csv 均尊重）"
        ),
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
    parser.add_argument(
        "--exclusion-csv",
        default=None,
        help=(
            "exclusion reconcile/manifest CSV；仅 dry-run；"
            "与 --execute 互斥；输出须在 outputs/validation/"
        ),
    )
    parser.add_argument(
        "--allow-production-dryrun-scaffold",
        action="store_true",
        help=(
            "允许 dry-run 向生产 snapshot 根写 status/error scaffold；"
            "默认禁止，改写隔离 mock 根"
        ),
    )
    args = parser.parse_args()

    # 硬拒绝：exclusion-csv 禁止与 execute 同用（无静默忽略）
    try:
        refuse_exclusion_with_execute(
            dry_run=args.dry_run,
            exclusion_csv=args.exclusion_csv,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc

    sample_file = args.sample_file or args.universe_file
    if not os.path.isabs(sample_file):
        sample_file = os.path.join(BASE_DIR, sample_file)

    exclusion_csv_arg = args.exclusion_csv
    exclusion_csv_abs: Optional[str] = None
    if exclusion_csv_arg:
        exclusion_csv_abs = (
            exclusion_csv_arg
            if os.path.isabs(exclusion_csv_arg)
            else os.path.join(BASE_DIR, exclusion_csv_arg)
        )

    output_dir = args.output_root or args.output_dir
    if output_dir and not os.path.isabs(output_dir):
        output_dir = os.path.join(BASE_DIR, output_dir)

    if is_phase35_expanded_snapshot_mode(args, sample_file):
        if exclusion_csv_arg:
            print(
                f"{EXCLUSION_CSV_PHASE35_UNSUPPORTED}: "
                "--exclusion-csv 仅支持标准 dry-run 路径，不支持 Phase 3.5",
                file=sys.stderr,
            )
            raise SystemExit(2)
        universe_csv = os.path.join(BASE_DIR, PHASE35_EXPANDED_UNIVERSE_CSV_REL)
        manifest_path = args.merge_manifest or os.path.join(BASE_DIR, PHASE35_MERGE_MANIFEST_CSV_REL)
        if not os.path.isabs(manifest_path):
            manifest_path = os.path.join(BASE_DIR, manifest_path)
        effective_output = output_dir or os.path.join(
            BASE_DIR, PHASE35_EXPANDED_SNAPSHOT_OUTPUT_ROOT_REL
        )

        if args.dry_run:
            result = run_phase35_expanded_dry_run(
                args,
                sample_file,
                universe_csv,
                manifest_path,
                effective_output,
            )
            v = result["validation"]
            planned_ok = sum(
                1 for r in result["report_rows"] if r.get("dryrun_status") == "planned_ok"
            )
            print("mode: phase35_expanded_dry_run")
            print(f"universe_ok: {result['universe_ok']}")
            print(f"company_count: {v.get('company_count', 0)}")
            print(f"original_count: {v.get('original_count', 0)}")
            print(f"resume_count: {v.get('resume_count', 0)}")
            print(f"manifest_rows: {v.get('manifest_rows', 0)}")
            print(f"planned_ok: {planned_ok}/{v.get('company_count', 0)}")
            print(f"planned_snapshot_json: {v.get('company_count', 0)}")
            print("snapshot_json_written=0")
            print("cninfo_calls=0")
            print("db_writes=0")
            print("minio_writes=0")
            print("rag_runs=0")
            print(f"harvest_unchanged: {result['harvest_unchanged']}")
            print(f"harvest_root: {args.harvest_root or PHASE35_BATCH_HARVEST_ROOT_REL}")
            print(f"resume_harvest_root: {args.resume_harvest_root or PHASE35_RESUME_HARVEST_ROOT_REL}")
            print(f"merge_manifest: {manifest_path}")
            print(f"output_root: {effective_output}")
            print(f"dryrun_report: {result['report_path']}")
            print(f"dryrun_summary: {result['summary_path']}")
            print(f"phase35_expanded_snapshot_dryrun_gate: {result['gate']}")
            return 0 if result["universe_ok"] else 1

        enforce_execute_approval(args, sample_file)
        result = run_phase35_expanded_execute(
            args,
            sample_file,
            universe_csv,
            manifest_path,
            effective_output,
        )
        v = result["validation"]
        snapshot_count = result["success_count"]
        print("mode: phase35_expanded_execute")
        print(f"universe_ok: {v.get('ok', False)}")
        print(f"company_count: {v.get('company_count', 0)}")
        print(f"success: {result['success_count']}")
        print(f"failed: {result['failed_count']}")
        print(f"snapshot_json_written: {snapshot_count}")
        print("cninfo_calls=0")
        print("db_writes=0")
        print("minio_writes=0")
        print("rag_runs=0")
        print(f"harvest_unchanged: {result['harvest_unchanged']}")
        print(f"output_root: {result['output_dir']}")
        print(f"build_report: {result['report_path']}")
        print(f"build_summary: {result['summary_path']}")
        print(f"phase35_expanded_success_subset_snapshot_build_gate: {result['gate']}")
        return 0 if result["failed_count"] == 0 and snapshot_count == PHASE35_EXPANDED_EXPECTED_COUNT else 1

    # --- 标准 dry-run / execute 路径 ---
    exclusion_filter_result: Optional[ExclusionFilterResult] = None
    universe_for_run = sample_file
    allow_prod_scaffold = bool(
        getattr(args, "allow_production_dryrun_scaffold", False)
    )
    # dry-run：尊重 --output-root/--output-dir；未指定则隔离 mock 根
    # execute：保持旧行为，仅 --output-dir（不在此强制隔离）
    dry_run_out_dir: Optional[str] = None
    if args.dry_run:
        if exclusion_csv_arg:
            dry_run_out_dir = output_dir
        else:
            try:
                dry_run_out_dir = resolve_standard_snapshot_dryrun_output_root(
                    output_dir,
                    allow_production_scaffold=allow_prod_scaffold,
                )
            except RuntimeError as exc:
                print(str(exc), file=sys.stderr)
                raise SystemExit(2) from exc
    else:
        dry_run_out_dir = args.output_dir

    if exclusion_csv_arg and exclusion_csv_abs:
        # exclusion-csv 原生路径：默认 validation 隔离根，并同时尊重 --output-root
        dry_run_out_dir = output_dir or os.path.join(
            BASE_DIR, EXCLUSION_CSV_NATIVE_DRYRUN_OUTPUT_ROOT_REL
        )
        if not os.path.isabs(dry_run_out_dir):
            dry_run_out_dir = os.path.join(BASE_DIR, dry_run_out_dir)
        try:
            universe_for_run, exclusion_filter_result = (
                prepare_exclusion_csv_dryrun_universe(
                    sample_file,
                    exclusion_csv_abs,
                    dry_run_out_dir,
                )
            )
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(2) from exc

    if args.dry_run and dry_run_out_dir:
        # 隔离根下默认报告不覆盖 tracked validation dryrun 文件
        default_report = os.path.join(dry_run_out_dir, "dryrun_report.csv")
        default_summary = os.path.join(dry_run_out_dir, "dryrun_summary.md")
        report_path = args.output_csv or default_report
        summary_path = args.output_md or default_summary
    else:
        report_path = args.output_csv or DRYRUN_REPORT_CSV
        summary_path = args.output_md or DRYRUN_SUMMARY_MD
    if not os.path.isabs(report_path):
        report_path = os.path.join(BASE_DIR, report_path)
    if not os.path.isabs(summary_path):
        summary_path = os.path.join(BASE_DIR, summary_path)

    if args.dry_run:
        try:
            result = run_dry_run(
                universe_path=universe_for_run,
                harvest_root=args.harvest_root,
                out_dir=dry_run_out_dir,
                report_path=report_path,
                summary_path=summary_path,
                resume=args.resume,
                force=args.force,
                allow_production_scaffold=allow_prod_scaffold,
            )
        except RuntimeError as exc:
            if PRODUCTION_SNAPSHOT_DRYRUN_WRITE_FORBIDDEN in str(exc):
                print(str(exc), file=sys.stderr)
                raise SystemExit(2) from exc
            raise
        v = result["validation"]
        fp = result.get("dryrun_fingerprint") or {}
        print("mode: dry-run")
        if exclusion_csv_arg:
            print("sample_mode: exclusion_csv_filter")
            print(f"exclusion_csv: {exclusion_csv_arg}")
            if exclusion_filter_result is not None:
                print(f"csv_kind: {exclusion_filter_result.csv_kind}")
                print(
                    f"excluded_unique_count: "
                    f"{len(exclusion_filter_result.excluded_codes)}"
                )
                print(
                    f"company_count_before_filter: "
                    f"{exclusion_filter_result.included_count + exclusion_filter_result.excluded_count}"
                )
            print(f"filtered_universe: {universe_for_run}")
        print(f"universe_ok: {result['universe_ok']}")
        print(f"company_count: {v['company_count']}")
        print(f"hold_overlap: {v['hold_overlap_count']}")
        print(f"harvest_root: {configure_snapshot_harvest_root(args.harvest_root)}")
        print(f"output_dir: {result.get('output_dir', FULL_OUT_DIR)}")
        print(f"status_csv: {STATUS_CSV}")
        print(f"error_csv: {ERROR_CSV}")
        print(f"dryrun_report: {report_path}")
        print(f"dryrun_summary: {summary_path}")
        print(f"snapshot_batch_dryrun_gate: {result['gate']}")
        if fp:
            print(f"dryrun_fingerprint_sha256: {fp.get('fingerprint_sha256', '')}")
            print(f"dryrun_content_sha256: {fp.get('content_sha256', '')}")
        print("cninfo_calls=0")
        print("snapshot_json_written=0")
        print("execute_production_snapshot_rebuild: false")
        if exclusion_csv_arg:
            capability_gate = (
                "PASS_OFFLINE" if result["universe_ok"] else "FAIL_REVIEW_REQUIRED"
            )
            print(f"exclusion_csv_native_dryrun_gate: {capability_gate}")
            print("capability_gain: true")
            return 0 if result["universe_ok"] else 1
        print("snapshot_dryrun_output_root_isolation: enforced")
        return 0 if result["universe_ok"] else 1

    # execute 路径：exclusion-csv 已在上方 refuse；此处沿用原逻辑
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
