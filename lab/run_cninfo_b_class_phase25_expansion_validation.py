"""
CNINFO B-class Phase 2.5 / Phase 3 expansion metadata validation runner.

默认 dry-run：校验 universe · 输出隔离 · 生成规划报告，**不请求 CNINFO**。
--live 须 --approve-b-class-phase25-expansion；仅 metadata · 无 PDF 下载/解析。
--retry-failed-only 模式：5-case isolated retry；dry-run 默认；live 须 --approve-b-class-phase25-failed-retry。
--phase3-100 模式：100-case Phase 3 expansion；dry-run 默认；live 须 --approve-b-class-phase3-100-expansion。
--phase3-100-failed-retry 模式：99-case isolated failed retry；dry-run 默认；live 须 --approve-b-class-phase3-100-failed-retry。
--phase3-100-retry-v2 模式：91-case isolated retry v2；dry-run 默认；live 须 --approve-b-class-phase3-100-retry-v2。

Usage:
    python lab/run_cninfo_b_class_phase25_expansion_validation.py
    python lab/run_cninfo_b_class_phase25_expansion_validation.py --live \\
        --approve-b-class-phase25-expansion
    python lab/run_cninfo_b_class_phase25_expansion_validation.py --retry-failed-only --dry-run
    python lab/run_cninfo_b_class_phase25_expansion_validation.py --phase3-100 --dry-run
    python lab/run_cninfo_b_class_phase25_expansion_validation.py --phase3-100-failed-retry --dry-run
    python lab/run_cninfo_b_class_phase25_expansion_validation.py --phase3-100-retry-v2 --dry-run
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
    "cninfo_b_class_phase25_expansion_universe_draft.csv",
)
DEFAULT_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase25_expansion"
)
DEFAULT_RETRY_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase25_failed_retry_universe.csv",
)
DEFAULT_RETRY_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase25_failed_retry"
)
DEFAULT_PHASE3_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase3_100_universe_draft.csv",
)
DEFAULT_PHASE3_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase3_100_expansion"
)
DEFAULT_PHASE3_RETRY_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase3_100_failed_retry_universe.csv",
)
DEFAULT_PHASE3_RETRY_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase3_100_failed_retry"
)
DEFAULT_PHASE3_RETRY_V2_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase3_100_retry_v2_universe.csv",
)
DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase3_100_retry_v2"
)
DEFAULT_EP002_PRECHECK_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase3_100_ep002_reachability_precheck",
)
PERSISTENT_FAILURE_LEDGER_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase3_100_persistent_failure_ledger.csv",
)
PHASE25_UNIVERSE_CSV = DEFAULT_UNIVERSE_CSV
PHASE1_TINY_LIVE_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tiny_live_validation"
)
TLC002_RETRY_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tlc002_retry"
)
PHASE2_EXPANSION_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase2_expansion"
)
PHASE3_FORBIDDEN_ROOT = os.path.join(
    BASE_DIR, "outputs", "harvest", "cninfo_c_class", "phase3_batch_500_001"
)
PHASE1_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase1_tiny_live_validation_universe.csv",
)
PHASE2_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase2_expansion_universe_draft.csv",
)
CATEGORIES_YAML = os.path.join(BASE_DIR, "config", "cninfo_announcement_categories.yaml")

DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "b_class_phase25_expansion_dryrun_report.csv"
)
DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "b_class_phase25_expansion_dryrun_summary.md"
)
RETRY_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_RETRY_OUTPUT_ROOT, "reports", "b_class_phase25_failed_retry_dryrun_report.csv"
)
RETRY_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_RETRY_OUTPUT_ROOT, "reports", "b_class_phase25_failed_retry_dryrun_summary.md"
)
PHASE3_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_PHASE3_OUTPUT_ROOT, "reports", "b_class_phase3_100_dryrun_report.csv"
)
PHASE3_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_PHASE3_OUTPUT_ROOT, "reports", "b_class_phase3_100_dryrun_summary.md"
)
PHASE3_RETRY_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_PHASE3_RETRY_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_failed_retry_dryrun_report.csv",
)
PHASE3_RETRY_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_PHASE3_RETRY_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_failed_retry_dryrun_summary.md",
)
PHASE3_RETRY_LIVE_REPORT_CSV = os.path.join(
    DEFAULT_PHASE3_RETRY_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_failed_retry_report.csv",
)
PHASE3_RETRY_LIVE_SUMMARY_MD = os.path.join(
    DEFAULT_PHASE3_RETRY_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_failed_retry_summary.md",
)
PHASE3_RETRY_QUALITY_REPORT_CSV = os.path.join(
    DEFAULT_PHASE3_RETRY_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_failed_retry_quality_report.csv",
)
PHASE3_RETRY_V2_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_retry_v2_dryrun_report.csv",
)
PHASE3_RETRY_V2_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_retry_v2_dryrun_summary.md",
)
PHASE3_RETRY_V2_LIVE_REPORT_CSV = os.path.join(
    DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_retry_v2_report.csv",
)
PHASE3_RETRY_V2_LIVE_SUMMARY_MD = os.path.join(
    DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_retry_v2_summary.md",
)
PHASE3_RETRY_V2_QUALITY_REPORT_CSV = os.path.join(
    DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT,
    "reports",
    "b_class_phase3_100_retry_v2_quality_report.csv",
)
MAX_PHASE3_RETRY_CNINFO_REQUESTS = 198
MAX_PHASE3_RETRY_V2_CNINFO_REQUESTS = 182

REQUIRED_UNIVERSE_SIZE = 50
REQUIRED_RETRY_UNIVERSE_SIZE = 5
REQUIRED_PHASE3_UNIVERSE_SIZE = 100
REQUIRED_PHASE3_RETRY_UNIVERSE_SIZE = 99
REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE = 91
PHASE3_SUCCESS_HOLD_CASE_ID = "B3E087"
RECOVERED_PHASE3_CASE_IDS: Set[str] = {
    "B3E003",
    "B3E004",
    "B3E005",
    "B3E006",
    "B3E007",
    "B3E008",
    "B3E009",
    "B3E011",
}
ALLOWED_RETRY_CASE_IDS: Set[str] = {
    "B25E003", "B25E008", "B25E032", "B25E039", "B25E040",
}
ALLOWED_PHASE3_CASE_IDS: Set[str] = {f"B3E{i:03d}" for i in range(1, 101)}
ALLOWED_PHASE3_RETRY_CASE_IDS: Set[str] = ALLOWED_PHASE3_CASE_IDS - {PHASE3_SUCCESS_HOLD_CASE_ID}
ALLOWED_RETRY_V2_ORIGINAL_CASE_IDS: Set[str] = (
    ALLOWED_PHASE3_CASE_IDS - {PHASE3_SUCCESS_HOLD_CASE_ID} - RECOVERED_PHASE3_CASE_IDS
)
ALLOWED_RETRY_V2_CASE_IDS: Set[str] = {
    f"B3R2_{i:03d}" for i in range(1, REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE + 1)
}
RETRY_V2_CASE_ID_PATTERN = re.compile(r"^B3R2_\d{3}$")
PHASE25_CASE_ID_PATTERN = re.compile(r"^B25E\d{3}$")
PHASE3_CASE_ID_PATTERN = re.compile(r"^B3E\d{3}$")
PRIOR_PHASE_CASE_ID_PATTERN = re.compile(r"^B(1|2|25)E\d{3}$")

PHASE25_APPROVAL_REQUIRED = "approve_b_class_phase25_expansion_required"
OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_b_class_phase25_expansion"
UNIVERSE_SIZE_VIOLATION = "universe_size_must_equal_50"
NON_PHASE25_CASE_REJECTED = "non_phase25_case_not_allowed"
PHASE25_INCLUDE_REQUIRED = "phase25_include_must_be_yes"
PHASE1_OVERLAP_REJECTED = "phase1_overlap_not_allowed"
PHASE2_OVERLAP_REJECTED = "phase2_overlap_not_allowed"
PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED = "pdf_download_not_allowed"
PDF_PARSE_REQUESTED_NOT_ALLOWED = "pdf_parse_not_allowed"
DB_WRITE_REQUESTED_NOT_ALLOWED = "db_write_not_allowed"
MINIO_WRITE_REQUESTED_NOT_ALLOWED = "minio_write_not_allowed"
RAG_REQUESTED_NOT_ALLOWED = "rag_not_allowed"
VERIFIED_STATUS_REQUESTED_NOT_ALLOWED = "verified_status_not_allowed"
PRODUCTION_READY_REQUESTED_NOT_ALLOWED = "production_ready_not_allowed"
PHASE2_APPROVAL_WRONG = "approve_b_class_phase2_expansion_not_valid_for_phase25"
TINY_LIVE_APPROVAL_WRONG = "approve_b_class_tiny_live_validation_not_valid_for_phase25"
TLC002_RETRY_APPROVAL_WRONG = "approve_b_class_tlc002_retry_not_valid_for_phase25"
PHASE1_BASELINE_WRITE_FORBIDDEN = "phase1_tiny_live_baseline_write_forbidden"
TLC002_BASELINE_WRITE_FORBIDDEN = "tlc002_retry_baseline_write_forbidden"
PHASE2_BASELINE_WRITE_FORBIDDEN = "phase2_expansion_baseline_write_forbidden"
PHASE25_BASELINE_WRITE_FORBIDDEN = "phase25_expansion_baseline_write_forbidden"
RETRY_OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_b_class_phase25_failed_retry"
RETRY_UNIVERSE_SIZE_VIOLATION = "retry_universe_size_must_equal_5"
PHASE25_FAILED_RETRY_APPROVAL_REQUIRED = "approve_b_class_phase25_failed_retry_required"
PHASE25_EXPANSION_APPROVAL_WRONG_FOR_RETRY = "approve_b_class_phase25_expansion_not_valid_for_failed_retry"
SUCCESSFUL_CASE_RETRY_REJECTED = "successful_phase25_case_excluded_from_retry"
NON_RETRY_CASE_REJECTED = "case_not_in_failed_retry_allowlist"
RETRY_INCLUDE_REQUIRED = "retry_include_must_be_yes"
OCR_REQUESTED_NOT_ALLOWED = "ocr_not_allowed"
EXTRACTION_REQUESTED_NOT_ALLOWED = "extraction_not_allowed"
PHASE3_APPROVAL_REQUIRED = "approve_b_class_phase3_100_expansion_required"
PHASE3_OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_b_class_phase3_100_expansion"
PHASE3_UNIVERSE_SIZE_VIOLATION = "universe_size_must_equal_100"
PHASE3_UNIVERSE_CSV_REQUIRED = "phase3_100_universe_csv_required"
NON_PHASE3_CASE_REJECTED = "non_phase3_case_not_allowed"
PHASE3_INCLUDE_REQUIRED = "phase3_include_must_be_yes"
PRIOR_PHASE_OVERLAP_REJECTED = "prior_phase_overlap_not_allowed"
PRIOR_PHASE_COMPANY_CODE_OVERLAP_REJECTED = "prior_phase_company_code_overlap_not_allowed"
DUPLICATE_COMPANY_CODE_REJECTED = "duplicate_company_code_not_allowed"
PHASE25_EXPANSION_APPROVAL_WRONG_FOR_PHASE3 = "approve_b_class_phase25_expansion_not_valid_for_phase3"
PHASE25_RETRY_APPROVAL_WRONG_FOR_PHASE3 = "approve_b_class_phase25_failed_retry_not_valid_for_phase3"
PHASE2_APPROVAL_WRONG_FOR_PHASE3 = "approve_b_class_phase2_expansion_not_valid_for_phase3"
RETRY_BASELINE_WRITE_FORBIDDEN = "phase25_failed_retry_baseline_write_forbidden"
PHASE3_ACCEPTABLE_THRESHOLD = 90
PHASE3_RETRY_ACCEPTABLE_THRESHOLD = 90
PHASE3_RETRY_V2_ACCEPTABLE_THRESHOLD = 82

PHASE3_RETRY_UNIVERSE_CSV_REQUIRED = "phase3_100_failed_retry_universe_csv_required"
PHASE3_RETRY_OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_b_class_phase3_100_failed_retry"
PHASE3_RETRY_UNIVERSE_SIZE_VIOLATION = "retry_universe_size_must_equal_99"
PHASE3_RETRY_APPROVAL_REQUIRED = "approve_b_class_phase3_100_failed_retry_required"
SUCCESSFUL_PHASE3_CASE_RETRY_REJECTED = "successful_phase3_case_excluded_from_retry"
NON_PHASE3_RETRY_CASE_REJECTED = "case_not_in_phase3_failed_retry_allowlist"
PRIOR_PHASE_CASE_ID_REJECTED = "prior_phase_case_id_not_allowed"
PRIOR_PHASE_COMPANY_CODE_RETRY_REJECTED = "prior_phase_company_code_not_allowed_in_retry"
PHASE3_EXPANSION_BASELINE_WRITE_FORBIDDEN = "phase3_expansion_baseline_write_forbidden"
PHASE25_EXPANSION_APPROVAL_WRONG_FOR_PHASE3_RETRY = "approve_b_class_phase25_expansion_not_valid_for_phase3_retry"
PHASE25_RETRY_APPROVAL_WRONG_FOR_PHASE3_RETRY = "approve_b_class_phase25_failed_retry_not_valid_for_phase3_retry"
PHASE3_EXPANSION_APPROVAL_WRONG_FOR_PHASE3_RETRY = "approve_b_class_phase3_100_expansion_not_valid_for_phase3_retry"

PHASE3_RETRY_V2_UNIVERSE_CSV_REQUIRED = "phase3_100_retry_v2_universe_csv_required"
PHASE3_RETRY_V2_OUTPUT_ROOT_VIOLATION = (
    "output_root_must_be_under_cninfo_b_class_phase3_100_retry_v2"
)
PHASE3_RETRY_V2_UNIVERSE_SIZE_VIOLATION = "retry_v2_universe_size_must_equal_91"
PHASE3_RETRY_V2_APPROVAL_REQUIRED = "approve_b_class_phase3_100_retry_v2_required"
RETRY_V2_WRONG_APPROVAL = "approve_b_class_phase3_100_retry_v2_wrong_flag"
RETRY_V2_CASE_ID_NOT_ALLOWED = "retry_v2_case_id_not_allowed"
NON_RETRY_V2_ORIGINAL_CASE_REJECTED = "case_not_in_retry_v2_persistent_allowlist"
RECOVERED_CASE_IN_RETRY_V2_FORBIDDEN = "recovered_case_in_retry_v2_forbidden"
REPLACEMENT_CASE_IN_RETRY_V2_FORBIDDEN = "replacement_case_in_retry_v2_forbidden"
RETRY_V2_INCLUDE_REQUIRED = "retry_v2_include_must_be_yes"
RETRY_V2_FINAL_STATUS_INVALID = "final_effective_status_before_retry_v2_invalid"
RETRY_V2_FAILURE_STAGE_INVALID = "persistent_failure_stage_invalid"
RETRY_V2_SCHEMA_IMPACT_INVALID = "schema_impact_must_be_none"
EP002_PRECHECK_BASELINE_WRITE_FORBIDDEN = "ep002_precheck_baseline_write_forbidden"
PHASE3_FAILED_RETRY_BASELINE_WRITE_FORBIDDEN = "phase3_failed_retry_baseline_write_forbidden"
PHASE3_RETRY_V2_LIVE_NOT_IMPLEMENTED = "retry_v2_live_not_implemented_in_this_runner"
PHASE25_EXPANSION_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2 = (
    "approve_b_class_phase25_expansion_not_valid_for_phase3_retry_v2"
)
PHASE25_RETRY_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2 = (
    "approve_b_class_phase25_failed_retry_not_valid_for_phase3_retry_v2"
)
PHASE3_EXPANSION_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2 = (
    "approve_b_class_phase3_100_expansion_not_valid_for_phase3_retry_v2"
)
PHASE3_RETRY_V1_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2 = (
    "approve_b_class_phase3_100_failed_retry_not_valid_for_phase3_retry_v2"
)
EP002_PRECHECK_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2 = (
    "approve_b_class_phase3_100_ep002_reachability_precheck_not_valid_for_phase3_retry_v2"
)

PHASE3_REPORT_COLUMNS = [
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
    "announcement_date",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "ocr_enabled",
    "extraction_enabled",
    "endpoint_used",
    "cninfo_request_count",
    "failure_type",
    "notes",
]

PHASE3_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "pdf_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "failure_type",
    "notes",
]

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
    "planned_ep001",
    "planned_ep002",
    "planned_ep004",
    "planned_ep005",
    "planned_request_count",
    "planned_output",
    "pdf_download",
    "pdf_parse",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

RETRY_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "original_failure_type",
    "retry_priority",
    "planned_request_count",
    "planned_output",
    "pdf_download",
    "pdf_parse",
    "ocr",
    "extraction",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

PHASE3_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "phase3_include",
    "prior_phase_overlap",
    "planned_endpoint_ep001",
    "planned_endpoint_ep002",
    "planned_endpoint_ep004",
    "planned_endpoint_ep005",
    "planned_request_count",
    "planned_output_root",
    "pdf_download",
    "pdf_parse",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

PHASE3_RETRY_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "original_phase3_status",
    "original_failure_type",
    "original_failure_stage",
    "retry_include",
    "planned_endpoint_ep001",
    "planned_endpoint_ep002",
    "planned_endpoint_ep004",
    "planned_endpoint_ep005",
    "planned_request_count",
    "planned_output_root",
    "pdf_download",
    "pdf_parse",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

PHASE3_RETRY_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "original_phase3_status",
    "original_failure_type",
    "original_failure_stage",
    "retry_retrieval_status",
    "quality_status",
    "lineage_status",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "announcement_date",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "ocr_enabled",
    "extraction_enabled",
    "endpoint_used",
    "cninfo_request_count",
    "failure_type",
    "notes",
]

PHASE3_RETRY_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "original_phase3_status",
    "original_failure_type",
    "original_failure_stage",
    "retry_retrieval_status",
    "quality_status",
    "lineage_status",
    "pdf_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "failure_type",
    "notes",
]

PHASE3_RETRY_V2_DRYRUN_REPORT_COLUMNS = [
    "retry_v2_case_id",
    "original_case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "original_phase3_status",
    "failed_retry_status",
    "final_effective_status_before_retry_v2",
    "persistent_failure_stage",
    "schema_impact",
    "quality_impact",
    "ep002_precheck_signal",
    "retry_v2_include",
    "planned_request_count",
    "planned_output_root",
    "pdf_download",
    "pdf_parse",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

PHASE3_RETRY_V2_REPORT_COLUMNS = [
    "retry_v2_case_id",
    "original_case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "original_phase3_status",
    "failed_retry_status",
    "final_effective_status_before_retry_v2",
    "persistent_failure_stage",
    "ep002_precheck_signal",
    "retry_v2_include",
    "retry_retrieval_status",
    "quality_status",
    "lineage_status",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "announcement_date",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "ocr_enabled",
    "extraction_enabled",
    "endpoint_used",
    "cninfo_request_count",
    "failure_type",
    "notes",
]

PHASE3_RETRY_V2_QUALITY_REPORT_COLUMNS = [
    "retry_v2_case_id",
    "original_case_id",
    "company_code",
    "original_phase3_status",
    "failed_retry_status",
    "persistent_failure_stage",
    "ep002_precheck_signal",
    "retry_retrieval_status",
    "quality_status",
    "lineage_status",
    "pdf_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "failure_type",
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

ACCEPTABLE_THRESHOLD = 45
RETRY_ACCEPTABLE_THRESHOLD = 3

RETRY_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "announcement_type",
    "target_endpoint",
    "original_failure_type",
    "retry_retrieval_status",
    "quality_status",
    "lineage_status",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "ocr_enabled",
    "extraction_enabled",
    "endpoint_used",
    "cninfo_request_count",
    "notes",
]

RETRY_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "original_failure_type",
    "retry_retrieval_status",
    "quality_status",
    "lineage_status",
    "pdf_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "notes",
]


@dataclass
class Phase25UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    announcement_type: str
    target_endpoint: List[str]
    expected_lineage_type: str
    risk_level: str
    phase1_overlap: str
    phase2_overlap: str
    phase25_include: str
    reason: str


@dataclass
class RetryUniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    announcement_type: str
    target_endpoint: List[str]
    original_failure_type: str
    original_failure_stage: str
    retry_priority: str
    retry_include: str
    retry_strategy: str
    notes: str


@dataclass
class Phase3UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    announcement_type: str
    target_endpoint: List[str]
    phase3_include: str
    selection_reason: str
    expected_behavior: str
    prior_phase_overlap: str
    notes: str


@dataclass
class Phase3RetryUniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    announcement_type: str
    target_endpoint: List[str]
    original_phase3_status: str
    original_failure_type: str
    original_failure_stage: str
    retry_include: str
    retry_strategy: str
    notes: str


@dataclass
class Phase3RetryV2UniverseCase:
    retry_v2_case_id: str
    original_case_id: str
    company_code: str
    company_name: str
    market: str
    announcement_type: str
    target_endpoint: List[str]
    original_phase3_status: str
    failed_retry_status: str
    final_effective_status_before_retry_v2: str
    persistent_failure_stage: str
    schema_impact: str
    quality_impact: str
    ep002_precheck_signal: str
    retry_v2_include: str
    retry_v2_reason: str
    risk_note: str
    notes: str


def _load_persistent_original_case_codes() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    if not os.path.isfile(PERSISTENT_FAILURE_LEDGER_CSV):
        return mapping
    with open(PERSISTENT_FAILURE_LEDGER_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            case_id = str(row.get("case_id", "")).strip()
            company_code = str(row.get("company_code", "")).strip()
            if case_id and company_code:
                mapping[case_id] = company_code
    return mapping


PERSISTENT_ORIGINAL_CASE_CODES = _load_persistent_original_case_codes()


def _load_company_codes(path: str) -> Set[str]:
    codes: Set[str] = set()
    if not os.path.isfile(path):
        return codes
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = str(row.get("company_code", "")).strip()
            if code:
                codes.add(code)
    return codes


PHASE1_COMPANY_CODES = _load_company_codes(PHASE1_UNIVERSE_CSV)
PHASE2_COMPANY_CODES = _load_company_codes(PHASE2_UNIVERSE_CSV)
PHASE25_COMPANY_CODES = _load_company_codes(PHASE25_UNIVERSE_CSV)
PRIOR_B_CLASS_COMPANY_CODES = PHASE1_COMPANY_CODES | PHASE2_COMPANY_CODES | PHASE25_COMPANY_CODES


def _normalize_output_root(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    for forbidden_root, err in (
        (PHASE1_TINY_LIVE_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (TLC002_RETRY_ROOT, TLC002_BASELINE_WRITE_FORBIDDEN),
        (PHASE2_EXPANSION_ROOT, PHASE2_BASELINE_WRITE_FORBIDDEN),
        (PHASE3_FORBIDDEN_ROOT, "phase3_batch_500_output_root_forbidden"),
    ):
        norm = _normalize_output_root(forbidden_root)
        if root == norm or root.startswith(norm + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, OUTPUT_ROOT_VIOLATION


def validate_retry_output_root(output_root: str) -> Tuple[bool, str]:
    """retry 输出仅允许 failed_retry 隔离根；禁止写入 Phase 2.5 主 batch。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_RETRY_OUTPUT_ROOT)
    phase25 = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    if root == phase25 or root.startswith(phase25 + os.sep):
        return False, PHASE25_BASELINE_WRITE_FORBIDDEN
    for forbidden_root, err in (
        (PHASE1_TINY_LIVE_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (TLC002_RETRY_ROOT, TLC002_BASELINE_WRITE_FORBIDDEN),
        (PHASE2_EXPANSION_ROOT, PHASE2_BASELINE_WRITE_FORBIDDEN),
        (PHASE3_FORBIDDEN_ROOT, "phase3_batch_500_output_root_forbidden"),
    ):
        norm = _normalize_output_root(forbidden_root)
        if root == norm or root.startswith(norm + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, RETRY_OUTPUT_ROOT_VIOLATION


def validate_phase3_output_root(output_root: str) -> Tuple[bool, str]:
    """Phase 3 输出仅允许 phase3_100_expansion 隔离根；禁止写入 Phase 1/2/2.5/retry 基线。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_PHASE3_OUTPUT_ROOT)
    for forbidden_root, err in (
        (DEFAULT_OUTPUT_ROOT, PHASE25_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_BASELINE_WRITE_FORBIDDEN),
        (PHASE1_TINY_LIVE_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (TLC002_RETRY_ROOT, TLC002_BASELINE_WRITE_FORBIDDEN),
        (PHASE2_EXPANSION_ROOT, PHASE2_BASELINE_WRITE_FORBIDDEN),
        (PHASE3_FORBIDDEN_ROOT, "phase3_batch_500_output_root_forbidden"),
    ):
        norm = _normalize_output_root(forbidden_root)
        if root == norm or root.startswith(norm + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, PHASE3_OUTPUT_ROOT_VIOLATION


def validate_phase3_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_PHASE3_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, PHASE3_UNIVERSE_CSV_REQUIRED
    return True, ""


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


def load_universe(path: str) -> List[Phase25UniverseCase]:
    cases: List[Phase25UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            endpoints = [
                s.strip() for s in (row.get("target_endpoint") or "").split(";") if s.strip()
            ]
            cases.append(
                Phase25UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    announcement_type=str(row.get("announcement_type", "")).strip(),
                    target_endpoint=endpoints,
                    expected_lineage_type=str(row.get("expected_lineage_type", "")).strip(),
                    risk_level=str(row.get("risk_level", "")).strip(),
                    phase1_overlap=str(row.get("phase1_overlap", "")).strip().lower(),
                    phase2_overlap=str(row.get("phase2_overlap", "")).strip().lower(),
                    phase25_include=str(row.get("phase25_include", "")).strip().lower(),
                    reason=str(row.get("reason", "")).strip(),
                )
            )
    return cases


def load_retry_universe(path: str) -> List[RetryUniverseCase]:
    cases: List[RetryUniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            endpoints = [
                s.strip() for s in (row.get("target_endpoint") or "").split(";") if s.strip()
            ]
            cases.append(
                RetryUniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    announcement_type=str(row.get("announcement_type", "")).strip(),
                    target_endpoint=endpoints,
                    original_failure_type=str(row.get("original_failure_type", "")).strip(),
                    original_failure_stage=str(row.get("original_failure_stage", "")).strip(),
                    retry_priority=str(row.get("retry_priority", "")).strip(),
                    retry_include=str(row.get("retry_include", "")).strip().lower(),
                    retry_strategy=str(row.get("retry_strategy", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return cases


def load_phase3_universe(path: str) -> List[Phase3UniverseCase]:
    cases: List[Phase3UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            endpoints = [
                s.strip() for s in (row.get("target_endpoint") or "").split(";") if s.strip()
            ]
            cases.append(
                Phase3UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    announcement_type=str(row.get("announcement_type", "")).strip(),
                    target_endpoint=endpoints,
                    phase3_include=str(row.get("phase3_include", "")).strip().lower(),
                    selection_reason=str(row.get("selection_reason", "")).strip(),
                    expected_behavior=str(row.get("expected_behavior", "")).strip(),
                    prior_phase_overlap=str(row.get("prior_phase_overlap", "")).strip().lower(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return cases


def retry_to_phase25_case(case: RetryUniverseCase) -> Phase25UniverseCase:
    return Phase25UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        announcement_type=case.announcement_type,
        target_endpoint=list(case.target_endpoint),
        expected_lineage_type=ANNOUNCEMENT_TYPE_SOURCE.get(case.announcement_type, ""),
        risk_level="low",
        phase1_overlap="no",
        phase2_overlap="no",
        phase25_include="yes",
        reason=case.notes,
    )


def phase3_to_phase25_case(case: Phase3UniverseCase) -> Phase25UniverseCase:
    return Phase25UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        announcement_type=case.announcement_type,
        target_endpoint=list(case.target_endpoint),
        expected_lineage_type=ANNOUNCEMENT_TYPE_SOURCE.get(case.announcement_type, ""),
        risk_level="low",
        phase1_overlap="no",
        phase2_overlap="no",
        phase25_include="yes",
        reason=case.selection_reason,
    )


def validate_retry_case(case: RetryUniverseCase) -> List[str]:
    issues: List[str] = []
    if case.case_id not in ALLOWED_RETRY_CASE_IDS:
        if PHASE25_CASE_ID_PATTERN.match(case.case_id or ""):
            issues.append(SUCCESSFUL_CASE_RETRY_REJECTED)
        else:
            issues.append(NON_RETRY_CASE_REJECTED)
    if case.retry_include != "yes":
        issues.append(RETRY_INCLUDE_REQUIRED)
    p25 = retry_to_phase25_case(case)
    issues.extend(validate_phase25_case(p25))
    return issues


def validate_retry_universe_size(cases: List[RetryUniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.retry_include == "yes"]
    if len(included) != REQUIRED_RETRY_UNIVERSE_SIZE:
        return False, f"{RETRY_UNIVERSE_SIZE_VIOLATION}: got {len(included)} expected {REQUIRED_RETRY_UNIVERSE_SIZE}"
    allowed_ids = {c.case_id for c in included}
    if allowed_ids != ALLOWED_RETRY_CASE_IDS:
        return False, f"{RETRY_UNIVERSE_SIZE_VIOLATION}: unexpected case set {sorted(allowed_ids)}"
    return True, ""


def validate_phase25_case(case: Phase25UniverseCase) -> List[str]:
    issues: List[str] = []
    if not PHASE25_CASE_ID_PATTERN.match(case.case_id or ""):
        issues.append(NON_PHASE25_CASE_REJECTED)
    if case.phase25_include != "yes":
        issues.append(PHASE25_INCLUDE_REQUIRED)
    if case.phase1_overlap == "yes" or case.company_code in PHASE1_COMPANY_CODES:
        issues.append(PHASE1_OVERLAP_REJECTED)
    if case.phase2_overlap == "yes" or case.company_code in PHASE2_COMPANY_CODES:
        issues.append(PHASE2_OVERLAP_REJECTED)
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


def validate_phase3_case(case: Phase3UniverseCase) -> List[str]:
    issues: List[str] = []
    if case.case_id not in ALLOWED_PHASE3_CASE_IDS:
        issues.append(NON_PHASE3_CASE_REJECTED)
    if case.phase3_include != "yes":
        issues.append(PHASE3_INCLUDE_REQUIRED)
    if case.prior_phase_overlap == "yes":
        issues.append(PRIOR_PHASE_OVERLAP_REJECTED)
    if case.company_code in PRIOR_B_CLASS_COMPANY_CODES:
        issues.append(PRIOR_PHASE_COMPANY_CODE_OVERLAP_REJECTED)
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


def validate_phase3_universe_size(cases: List[Phase3UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.phase3_include == "yes"]
    if len(included) != REQUIRED_PHASE3_UNIVERSE_SIZE:
        return False, f"{PHASE3_UNIVERSE_SIZE_VIOLATION}: got {len(included)} expected {REQUIRED_PHASE3_UNIVERSE_SIZE}"
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_PHASE3_CASE_IDS:
        return False, f"{NON_PHASE3_CASE_REJECTED}: unexpected case set"
    return True, ""


def validate_phase3_duplicate_codes(cases: List[Phase3UniverseCase]) -> List[str]:
    issues: List[str] = []
    seen: Dict[str, str] = {}
    for case in cases:
        if case.phase3_include != "yes":
            continue
        if case.company_code in seen:
            issues.append(f"{case.case_id}:{DUPLICATE_COMPANY_CODE_REJECTED}")
        else:
            seen[case.company_code] = case.case_id
    return issues


def load_phase3_retry_universe(path: str) -> List[Phase3RetryUniverseCase]:
    cases: List[Phase3RetryUniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            endpoints = [
                s.strip() for s in (row.get("target_endpoint") or "").split(";") if s.strip()
            ]
            cases.append(
                Phase3RetryUniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    announcement_type=str(row.get("announcement_type", "")).strip(),
                    target_endpoint=endpoints,
                    original_phase3_status=str(row.get("original_phase3_status", "")).strip(),
                    original_failure_type=str(row.get("original_failure_type", "")).strip(),
                    original_failure_stage=str(row.get("original_failure_stage", "")).strip(),
                    retry_include=str(row.get("retry_include", "")).strip().lower(),
                    retry_strategy=str(row.get("retry_strategy", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return cases


def phase3_retry_to_phase25_case(case: Phase3RetryUniverseCase) -> Phase25UniverseCase:
    return Phase25UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        announcement_type=case.announcement_type,
        target_endpoint=list(case.target_endpoint),
        expected_lineage_type=ANNOUNCEMENT_TYPE_SOURCE.get(case.announcement_type, ""),
        risk_level="low",
        phase1_overlap="no",
        phase2_overlap="no",
        phase25_include="yes",
        reason=case.notes,
    )


def validate_phase3_retry_case(case: Phase3RetryUniverseCase) -> List[str]:
    issues: List[str] = []
    if case.case_id == PHASE3_SUCCESS_HOLD_CASE_ID:
        issues.append(SUCCESSFUL_PHASE3_CASE_RETRY_REJECTED)
    if PRIOR_PHASE_CASE_ID_PATTERN.match(case.case_id or ""):
        issues.append(PRIOR_PHASE_CASE_ID_REJECTED)
    if case.case_id not in ALLOWED_PHASE3_RETRY_CASE_IDS:
        issues.append(NON_PHASE3_RETRY_CASE_REJECTED)
    if case.retry_include != "yes":
        issues.append(RETRY_INCLUDE_REQUIRED)
    if case.company_code in PRIOR_B_CLASS_COMPANY_CODES:
        issues.append(PRIOR_PHASE_COMPANY_CODE_RETRY_REJECTED)
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


def validate_phase3_retry_universe_size(cases: List[Phase3RetryUniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.retry_include == "yes"]
    if len(included) != REQUIRED_PHASE3_RETRY_UNIVERSE_SIZE:
        return (
            False,
            f"{PHASE3_RETRY_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_PHASE3_RETRY_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_PHASE3_RETRY_CASE_IDS:
        return False, f"{NON_PHASE3_RETRY_CASE_REJECTED}: unexpected case set"
    return True, ""


def validate_phase3_retry_duplicate_codes(cases: List[Phase3RetryUniverseCase]) -> List[str]:
    issues: List[str] = []
    seen: Dict[str, str] = {}
    for case in cases:
        if case.retry_include != "yes":
            continue
        if case.company_code in seen:
            issues.append(f"{case.case_id}:{DUPLICATE_COMPANY_CODE_REJECTED}")
        else:
            seen[case.company_code] = case.case_id
    return issues


def validate_phase3_retry_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_PHASE3_RETRY_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, PHASE3_RETRY_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_phase3_retry_output_root(output_root: str) -> Tuple[bool, str]:
    """Phase 3 failed retry 输出仅允许 failed_retry 隔离根；禁止写入 Phase 3 expansion / 2.5 基线。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_PHASE3_RETRY_OUTPUT_ROOT)
    for forbidden_root, err in (
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_EXPANSION_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE25_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_BASELINE_WRITE_FORBIDDEN),
        (PHASE1_TINY_LIVE_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (TLC002_RETRY_ROOT, TLC002_BASELINE_WRITE_FORBIDDEN),
        (PHASE2_EXPANSION_ROOT, PHASE2_BASELINE_WRITE_FORBIDDEN),
        (PHASE3_FORBIDDEN_ROOT, "phase3_batch_500_output_root_forbidden"),
    ):
        norm = _normalize_output_root(forbidden_root)
        if root == norm or root.startswith(norm + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, PHASE3_RETRY_OUTPUT_ROOT_VIOLATION


def load_phase3_retry_v2_universe(path: str) -> List[Phase3RetryV2UniverseCase]:
    cases: List[Phase3RetryV2UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            endpoints = [
                s.strip() for s in (row.get("target_endpoint") or "").split(";") if s.strip()
            ]
            cases.append(
                Phase3RetryV2UniverseCase(
                    retry_v2_case_id=str(row.get("retry_v2_case_id", "")).strip(),
                    original_case_id=str(row.get("original_case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    announcement_type=str(row.get("announcement_type", "")).strip(),
                    target_endpoint=endpoints,
                    original_phase3_status=str(
                        row.get("original_phase3_status", "")
                    ).strip(),
                    failed_retry_status=str(row.get("failed_retry_status", "")).strip(),
                    final_effective_status_before_retry_v2=str(
                        row.get("final_effective_status_before_retry_v2", "")
                    ).strip(),
                    persistent_failure_stage=str(
                        row.get("persistent_failure_stage", "")
                    ).strip(),
                    schema_impact=str(row.get("schema_impact", "")).strip(),
                    quality_impact=str(row.get("quality_impact", "")).strip(),
                    ep002_precheck_signal=str(
                        row.get("ep002_precheck_signal", "")
                    ).strip(),
                    retry_v2_include=str(row.get("retry_v2_include", "")).strip().lower(),
                    retry_v2_reason=str(row.get("retry_v2_reason", "")).strip(),
                    risk_note=str(row.get("risk_note", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return cases


def phase3_retry_v2_to_phase25_case(case: Phase3RetryV2UniverseCase) -> Phase25UniverseCase:
    return Phase25UniverseCase(
        case_id=case.original_case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        announcement_type=case.announcement_type,
        target_endpoint=list(case.target_endpoint),
        expected_lineage_type=ANNOUNCEMENT_TYPE_SOURCE.get(case.announcement_type, ""),
        risk_level="low",
        phase1_overlap="no",
        phase2_overlap="no",
        phase25_include="yes",
        reason=case.notes,
    )


def validate_phase3_retry_v2_case(case: Phase3RetryV2UniverseCase) -> List[str]:
    issues: List[str] = []
    if case.retry_v2_case_id not in ALLOWED_RETRY_V2_CASE_IDS:
        issues.append(f"{RETRY_V2_CASE_ID_NOT_ALLOWED}:{case.retry_v2_case_id}")
    if case.original_case_id == PHASE3_SUCCESS_HOLD_CASE_ID:
        issues.append(SUCCESSFUL_PHASE3_CASE_RETRY_REJECTED)
    if case.original_case_id in RECOVERED_PHASE3_CASE_IDS:
        issues.append(f"{RECOVERED_CASE_IN_RETRY_V2_FORBIDDEN}:{case.original_case_id}")
    if PRIOR_PHASE_CASE_ID_PATTERN.match(case.original_case_id or ""):
        issues.append(PRIOR_PHASE_CASE_ID_REJECTED)
    if case.original_case_id not in ALLOWED_RETRY_V2_ORIGINAL_CASE_IDS:
        issues.append(f"{NON_RETRY_V2_ORIGINAL_CASE_REJECTED}:{case.original_case_id}")
    expected_code = PERSISTENT_ORIGINAL_CASE_CODES.get(case.original_case_id)
    if expected_code and case.company_code != expected_code:
        issues.append(f"{REPLACEMENT_CASE_IN_RETRY_V2_FORBIDDEN}:{case.original_case_id}")
    if case.retry_v2_include != "yes":
        issues.append(RETRY_V2_INCLUDE_REQUIRED)
    if (
        case.final_effective_status_before_retry_v2
        != "unresolved_ep002_orgid_network_failure"
    ):
        issues.append(RETRY_V2_FINAL_STATUS_INVALID)
    if case.persistent_failure_stage != "EP002_topSearch_orgId":
        issues.append(RETRY_V2_FAILURE_STAGE_INVALID)
    if case.schema_impact != "none":
        issues.append(RETRY_V2_SCHEMA_IMPACT_INVALID)
    if case.company_code in PRIOR_B_CLASS_COMPANY_CODES:
        issues.append(PRIOR_PHASE_COMPANY_CODE_RETRY_REJECTED)
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


def validate_phase3_retry_v2_universe_size(
    cases: List[Phase3RetryV2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.retry_v2_include == "yes"]
    if len(included) != REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE:
        return (
            False,
            f"{PHASE3_RETRY_V2_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE}",
        )
    retry_v2_ids = {c.retry_v2_case_id for c in included}
    original_ids = {c.original_case_id for c in included}
    if retry_v2_ids != ALLOWED_RETRY_V2_CASE_IDS:
        return False, f"{RETRY_V2_CASE_ID_NOT_ALLOWED}: unexpected retry_v2 set"
    if original_ids != ALLOWED_RETRY_V2_ORIGINAL_CASE_IDS:
        return False, f"{NON_RETRY_V2_ORIGINAL_CASE_REJECTED}: unexpected original set"
    return True, ""


def validate_phase3_retry_v2_duplicate_codes(
    cases: List[Phase3RetryV2UniverseCase],
) -> List[str]:
    issues: List[str] = []
    seen: Dict[str, str] = {}
    for case in cases:
        if case.retry_v2_include != "yes":
            continue
        if case.company_code in seen:
            issues.append(f"{case.retry_v2_case_id}:{DUPLICATE_COMPANY_CODE_REJECTED}")
        else:
            seen[case.company_code] = case.retry_v2_case_id
    return issues


def validate_phase3_retry_v2_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_PHASE3_RETRY_V2_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, PHASE3_RETRY_V2_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_phase3_retry_v2_output_root(output_root: str) -> Tuple[bool, str]:
    """Phase 3 retry v2 输出仅允许 retry_v2 隔离根；禁止写入 Phase 3 / failed retry / EP002 precheck / 2.5 基线。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT)
    for forbidden_root, err in (
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_EXPANSION_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_RETRY_OUTPUT_ROOT, PHASE3_FAILED_RETRY_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_EP002_PRECHECK_ROOT, EP002_PRECHECK_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE25_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_BASELINE_WRITE_FORBIDDEN),
        (PHASE1_TINY_LIVE_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (TLC002_RETRY_ROOT, TLC002_BASELINE_WRITE_FORBIDDEN),
        (PHASE2_EXPANSION_ROOT, PHASE2_BASELINE_WRITE_FORBIDDEN),
        (PHASE3_FORBIDDEN_ROOT, "phase3_batch_500_output_root_forbidden"),
    ):
        norm = _normalize_output_root(forbidden_root)
        if root == norm or root.startswith(norm + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, PHASE3_RETRY_V2_OUTPUT_ROOT_VIOLATION


def enforce_phase3_retry_v2_approval_gate(args: argparse.Namespace) -> None:
    wrong_flags = (
        (args.approve_b_class_phase25_expansion, PHASE25_EXPANSION_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2),
        (args.approve_b_class_phase25_failed_retry, PHASE25_RETRY_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2),
        (args.approve_b_class_phase3_100_expansion, PHASE3_EXPANSION_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2),
        (args.approve_b_class_phase3_100_failed_retry, PHASE3_RETRY_V1_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2),
        (
            getattr(args, "approve_b_class_phase3_100_ep002_reachability_precheck", False),
            EP002_PRECHECK_APPROVAL_WRONG_FOR_PHASE3_RETRY_V2,
        ),
        (args.approve_b_class_phase2_expansion, PHASE2_APPROVAL_WRONG_FOR_PHASE3),
        (args.approve_b_class_tiny_live_validation, TINY_LIVE_APPROVAL_WRONG),
        (args.approve_b_class_tlc002_retry, TLC002_RETRY_APPROVAL_WRONG),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    for flag, err in (
        (args.approve_full_harvest, tiny_live.FORBIDDEN_APPROVE_FULL_HARVEST),
        (args.approve_phase2_smoke_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE2),
        (args.approve_phase3_batch_500_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE3),
    ):
        if flag:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not args.approve_b_class_phase3_100_retry_v2:
        print(f"ERROR: {PHASE3_RETRY_V2_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def validate_universe_size(cases: List[Phase25UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.phase25_include == "yes"]
    if len(included) != REQUIRED_UNIVERSE_SIZE:
        return False, f"{UNIVERSE_SIZE_VIOLATION}: got {len(included)} expected {REQUIRED_UNIVERSE_SIZE}"
    return True, ""


def enforce_forbidden_options(args: argparse.Namespace) -> None:
    checks = (
        (args.download_pdf, PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
        (args.parse_pdf, PDF_PARSE_REQUESTED_NOT_ALLOWED),
        (getattr(args, "run_ocr", False), OCR_REQUESTED_NOT_ALLOWED),
        (getattr(args, "extract_sections", False), EXTRACTION_REQUESTED_NOT_ALLOWED),
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


def enforce_phase3_approval_gate(args: argparse.Namespace) -> None:
    if args.approve_b_class_phase25_expansion:
        print(f"ERROR: {PHASE25_EXPANSION_APPROVAL_WRONG_FOR_PHASE3}", file=sys.stderr)
        sys.exit(2)
    if args.approve_b_class_phase25_failed_retry:
        print(f"ERROR: {PHASE25_RETRY_APPROVAL_WRONG_FOR_PHASE3}", file=sys.stderr)
        sys.exit(2)
    if args.approve_b_class_phase3_100_failed_retry:
        print(f"ERROR: {PHASE3_EXPANSION_APPROVAL_WRONG_FOR_PHASE3_RETRY}", file=sys.stderr)
        sys.exit(2)
    if args.approve_b_class_phase2_expansion:
        print(f"ERROR: {PHASE2_APPROVAL_WRONG_FOR_PHASE3}", file=sys.stderr)
        sys.exit(2)
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
    if args.mode == "live" and not args.approve_b_class_phase3_100_expansion:
        print(f"ERROR: {PHASE3_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def enforce_live_approval_gate(args: argparse.Namespace) -> None:
    if args.approve_b_class_phase2_expansion:
        print(f"ERROR: {PHASE2_APPROVAL_WRONG}", file=sys.stderr)
        sys.exit(2)
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
    if args.mode == "live" and not args.approve_b_class_phase25_expansion:
        print(f"ERROR: {PHASE25_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def enforce_retry_approval_gate(args: argparse.Namespace) -> None:
    if args.approve_b_class_phase25_expansion:
        print(f"ERROR: {PHASE25_EXPANSION_APPROVAL_WRONG_FOR_RETRY}", file=sys.stderr)
        sys.exit(2)
    if args.approve_b_class_phase2_expansion:
        print(f"ERROR: {PHASE2_APPROVAL_WRONG}", file=sys.stderr)
        sys.exit(2)
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
    if args.mode == "live" and not args.approve_b_class_phase25_failed_retry:
        print(f"ERROR: {PHASE25_FAILED_RETRY_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def enforce_phase3_retry_approval_gate(args: argparse.Namespace) -> None:
    if args.approve_b_class_phase25_expansion:
        print(f"ERROR: {PHASE25_EXPANSION_APPROVAL_WRONG_FOR_PHASE3_RETRY}", file=sys.stderr)
        sys.exit(2)
    if args.approve_b_class_phase25_failed_retry:
        print(f"ERROR: {PHASE25_RETRY_APPROVAL_WRONG_FOR_PHASE3_RETRY}", file=sys.stderr)
        sys.exit(2)
    if args.approve_b_class_phase3_100_expansion:
        print(f"ERROR: {PHASE3_EXPANSION_APPROVAL_WRONG_FOR_PHASE3_RETRY}", file=sys.stderr)
        sys.exit(2)
    if getattr(args, "approve_b_class_phase3_100_retry_v2", False):
        print(f"ERROR: {RETRY_V2_WRONG_APPROVAL}", file=sys.stderr)
        sys.exit(2)
    if args.approve_b_class_phase2_expansion:
        print(f"ERROR: {PHASE2_APPROVAL_WRONG}", file=sys.stderr)
        sys.exit(2)
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
    if args.mode == "live" and not args.approve_b_class_phase3_100_failed_retry:
        print(f"ERROR: {PHASE3_RETRY_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def to_tiny_live_case(case: Phase25UniverseCase) -> tiny_live.UniverseCase:
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


def _planned_endpoint_flags(case: Phase25UniverseCase) -> Tuple[str, str, str, str, int]:
    ep001 = "1" if "EP001" in case.target_endpoint else "0"
    ep002 = "1" if "EP002" in case.target_endpoint else "0"
    ep004 = "1" if "EP004" in case.target_endpoint else "0"
    ep005 = "1" if "EP005" in case.target_endpoint else "0"
    # live 执行：EP002 orgId + EP001 公告检索（与 Phase 2 runner 一致）
    request_count = 2
    return ep001, ep002, ep004, ep005, request_count


def build_dryrun_row(case: Phase25UniverseCase, issues: List[str]) -> Dict[str, str]:
    primary = SOURCE_TYPE_PRIMARY_ENDPOINT[ANNOUNCEMENT_TYPE_SOURCE[case.announcement_type]]
    planned_output = os.path.join("raw_metadata", f"{case.case_id}_{primary}.json")
    status = "planned_ok" if not issues else "validation_failed"
    notes = "dry-run; CNINFO not called; metadata and pdf URL lineage only"
    if issues:
        notes = f"{notes}; {';'.join(issues)}"
    ep001, ep002, ep004, ep005, req_count = _planned_endpoint_flags(case)
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "announcement_type": case.announcement_type,
        "target_endpoint": ";".join(case.target_endpoint),
        "planned_ep001": ep001,
        "planned_ep002": ep002,
        "planned_ep004": ep004,
        "planned_ep005": ep005,
        "planned_request_count": str(req_count),
        "planned_output": planned_output,
        "pdf_download": "0",
        "pdf_parse": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def write_dryrun_snapshot(
    case: Phase25UniverseCase,
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
    cases: List[Phase25UniverseCase],
    output_paths: Dict[str, str],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.phase25_include != "yes":
            continue
        issues = validate_phase25_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        write_dryrun_snapshot(case, output_paths, issues)
        rows.append(build_dryrun_row(case, issues))
    return rows, universe_issues


def build_retry_dryrun_row(case: RetryUniverseCase, issues: List[str]) -> Dict[str, str]:
    p25 = retry_to_phase25_case(case)
    primary = SOURCE_TYPE_PRIMARY_ENDPOINT[ANNOUNCEMENT_TYPE_SOURCE[case.announcement_type]]
    planned_output = os.path.join("raw_metadata", f"{case.case_id}_{primary}.json")
    status = "planned_ok" if not issues else "validation_failed"
    notes = "retry dry-run; CNINFO not called; metadata and pdf URL lineage only"
    if issues:
        notes = f"{notes}; {';'.join(issues)}"
    _ep001, _ep002, _ep004, _ep005, req_count = _planned_endpoint_flags(p25)
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "announcement_type": case.announcement_type,
        "target_endpoint": ";".join(case.target_endpoint),
        "original_failure_type": case.original_failure_type,
        "retry_priority": case.retry_priority,
        "planned_request_count": str(req_count),
        "planned_output": planned_output,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def write_retry_dryrun_snapshot(
    case: RetryUniverseCase,
    output_paths: Dict[str, str],
    issues: List[str],
) -> None:
    p25 = retry_to_phase25_case(case)
    write_dryrun_snapshot(p25, output_paths, issues)


def process_retry_dry_run(
    cases: List[RetryUniverseCase],
    output_paths: Dict[str, str],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = validate_retry_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        write_retry_dryrun_snapshot(case, output_paths, issues)
        rows.append(build_retry_dryrun_row(case, issues))
    return rows, universe_issues


def build_phase3_dryrun_row(
    case: Phase3UniverseCase,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    status = "planned_ok" if not issues else "validation_failed"
    notes = "phase3 dry-run; CNINFO not called; metadata and pdf URL lineage only"
    if issues:
        notes = f"{notes}; {';'.join(issues)}"
    ep001, ep002, ep004, ep005, req_count = _planned_endpoint_flags(phase3_to_phase25_case(case))
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "announcement_type": case.announcement_type,
        "target_endpoint": ";".join(case.target_endpoint),
        "phase3_include": case.phase3_include,
        "prior_phase_overlap": case.prior_phase_overlap,
        "planned_endpoint_ep001": ep001,
        "planned_endpoint_ep002": ep002,
        "planned_endpoint_ep004": ep004,
        "planned_endpoint_ep005": ep005,
        "planned_request_count": str(req_count),
        "planned_output_root": output_root,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "db_write": "0",
        "minio_write": "0",
        "rag_run": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def write_phase3_dryrun_snapshot(
    case: Phase3UniverseCase,
    output_paths: Dict[str, str],
    issues: List[str],
) -> None:
    write_dryrun_snapshot(phase3_to_phase25_case(case), output_paths, issues)


def process_phase3_dry_run(
    cases: List[Phase3UniverseCase],
    output_paths: Dict[str, str],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = list(validate_phase3_duplicate_codes(cases))
    seen_codes: Set[str] = set()
    for case in cases:
        if case.phase3_include != "yes":
            continue
        issues = list(validate_phase3_case(case))
        if case.company_code in seen_codes:
            if DUPLICATE_COMPANY_CODE_REJECTED not in issues:
                issues.append(DUPLICATE_COMPANY_CODE_REJECTED)
        else:
            seen_codes.add(case.company_code)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        write_phase3_dryrun_snapshot(case, output_paths, issues)
        rows.append(build_phase3_dryrun_row(case, issues, output_paths["root"]))
    return rows, universe_issues


def write_phase3_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    path = os.path.join(output_paths["reports"], "b_class_phase3_100_dryrun_report.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_phase3_dryrun_summary(
    output_paths: Dict[str, str],
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    planned_ok = sum(1 for r in rows if r.get("dryrun_status") == "planned_ok")
    total_planned = sum(int(r.get("planned_request_count", "0")) for r in rows)
    ep004 = sum(1 for r in rows if r.get("planned_endpoint_ep004") == "1")
    ep005 = sum(1 for r in rows if r.get("planned_endpoint_ep005") == "1")
    ep002 = sum(1 for r in rows if r.get("planned_endpoint_ep002") == "1")
    lines = [
        "# CNINFO B 类 Phase 3 100-Company Expansion — Dry-Run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 3 100-company expansion runner dry-run · **无 CNINFO** · **无 PDF 下载/解析**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | phase3_dry_run |",
        f"| universe size | {len(rows)} |",
        f"| planned_ok | {planned_ok} |",
        f"| total planned_request_count | {total_planned} |",
        "| CNINFO calls (dry-run) | **0** |",
        f"| planned EP004 cases | {ep004} |",
        f"| planned EP005 cases | {ep005} |",
        f"| planned EP002 in target | {ep002} |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB | **0** |",
        "| MinIO | **0** |",
        "| RAG | **0** |",
        "",
        "## Output isolation",
        "",
        "```text",
        f"{output_paths['root']}",
        "```",
        "",
        "## Safety",
        "",
        "- prior-phase overlap: **0**",
        "- Phase 2.5 expansion baseline write-blocked: **yes**",
        "- Phase 2.5 failed retry baseline write-blocked: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase3_100_runner_extension_gate = {gate}",
        "```",
        "",
        "**NOT APPROVED** · **NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    path = os.path.join(output_paths["reports"], "b_class_phase3_100_dryrun_summary.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def compute_phase3_runner_gate(universe_issues: List[str], case_count: int) -> str:
    if universe_issues or case_count != REQUIRED_PHASE3_UNIVERSE_SIZE:
        return "FAIL"
    return "READY_FOR_APPROVAL"


def build_phase3_retry_dryrun_row(
    case: Phase3RetryUniverseCase,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    status = "planned_ok" if not issues else "validation_failed"
    notes = "phase3 failed retry dry-run; CNINFO not called; metadata and pdf URL lineage only"
    if issues:
        notes = f"{notes}; {';'.join(issues)}"
    ep001, ep002, ep004, ep005, req_count = _planned_endpoint_flags(
        phase3_retry_to_phase25_case(case)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "announcement_type": case.announcement_type,
        "target_endpoint": ";".join(case.target_endpoint),
        "original_phase3_status": case.original_phase3_status,
        "original_failure_type": case.original_failure_type,
        "original_failure_stage": case.original_failure_stage,
        "retry_include": case.retry_include,
        "planned_endpoint_ep001": ep001,
        "planned_endpoint_ep002": ep002,
        "planned_endpoint_ep004": ep004,
        "planned_endpoint_ep005": ep005,
        "planned_request_count": str(req_count),
        "planned_output_root": output_root,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "db_write": "0",
        "minio_write": "0",
        "rag_run": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def write_phase3_retry_dryrun_snapshot(
    case: Phase3RetryUniverseCase,
    output_paths: Dict[str, str],
    issues: List[str],
) -> None:
    write_dryrun_snapshot(phase3_retry_to_phase25_case(case), output_paths, issues)


def process_phase3_retry_dry_run(
    cases: List[Phase3RetryUniverseCase],
    output_paths: Dict[str, str],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = list(validate_phase3_retry_duplicate_codes(cases))
    seen_codes: Set[str] = set()
    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = list(validate_phase3_retry_case(case))
        if case.company_code in seen_codes:
            if DUPLICATE_COMPANY_CODE_REJECTED not in issues:
                issues.append(DUPLICATE_COMPANY_CODE_REJECTED)
        else:
            seen_codes.add(case.company_code)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        write_phase3_retry_dryrun_snapshot(case, output_paths, issues)
        rows.append(build_phase3_retry_dryrun_row(case, issues, output_paths["root"]))
    return rows, universe_issues


def write_phase3_retry_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_failed_retry_dryrun_report.csv"
    )
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_RETRY_DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_phase3_retry_dryrun_summary(
    output_paths: Dict[str, str],
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    planned_ok = sum(1 for r in rows if r.get("dryrun_status") == "planned_ok")
    total_planned = sum(int(r.get("planned_request_count", "0")) for r in rows)
    ep002 = sum(1 for r in rows if r.get("planned_endpoint_ep002") == "1")
    lines = [
        "# CNINFO B 类 Phase 3 100 Failed-Case Isolated Retry — Dry-Run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 3 failed-case isolated retry dry-run · **无 CNINFO** · **无 PDF 下载/解析**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | phase3_failed_retry_dry_run |",
        f"| retry universe size | {len(rows)} |",
        f"| planned_ok | {planned_ok} |",
        f"| total planned_request_count | {total_planned} |",
        f"| EP002 planned cases | {ep002} |",
        "| CNINFO calls (dry-run) | **0** |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB write | **0** |",
        "| MinIO write | **0** |",
        "| RAG | **0** |",
        "",
        "## Output isolation",
        "",
        "```text",
        f"{output_paths['root']}",
        "```",
        "",
        "## Safety",
        "",
        f"- successful hold case {PHASE3_SUCCESS_HOLD_CASE_ID} excluded: **yes**",
        "- Phase 3 expansion baseline write-blocked: **yes**",
        "- Phase 2.5 expansion baseline write-blocked: **yes**",
        "- Phase 2.5 failed retry baseline write-blocked: **yes**",
        "- approval_status: **NOT_APPROVED**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase3_100_failed_retry_runner_extension_gate = {gate}",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_failed_retry_dryrun_summary.md"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def compute_phase3_retry_runner_gate(universe_issues: List[str], case_count: int) -> str:
    if universe_issues or case_count != REQUIRED_PHASE3_RETRY_UNIVERSE_SIZE:
        return "FAIL"
    return "READY_FOR_APPROVAL"


def build_phase3_retry_v2_dryrun_row(
    case: Phase3RetryV2UniverseCase,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    status = "planned_ok" if not issues else "validation_failed"
    notes = "phase3 retry_v2 dry-run; CNINFO not called; metadata and pdf URL lineage only"
    if issues:
        notes = f"{notes}; {';'.join(issues)}"
    _, _, _, _, req_count = _planned_endpoint_flags(phase3_retry_v2_to_phase25_case(case))
    return {
        "retry_v2_case_id": case.retry_v2_case_id,
        "original_case_id": case.original_case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "announcement_type": case.announcement_type,
        "target_endpoint": ";".join(case.target_endpoint),
        "original_phase3_status": case.original_phase3_status,
        "failed_retry_status": case.failed_retry_status,
        "final_effective_status_before_retry_v2": case.final_effective_status_before_retry_v2,
        "persistent_failure_stage": case.persistent_failure_stage,
        "schema_impact": case.schema_impact,
        "quality_impact": case.quality_impact,
        "ep002_precheck_signal": case.ep002_precheck_signal,
        "retry_v2_include": case.retry_v2_include,
        "planned_request_count": str(req_count if not issues else 0),
        "planned_output_root": output_root,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "db_write": "0",
        "minio_write": "0",
        "rag_run": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def write_phase3_retry_v2_dryrun_snapshot(
    case: Phase3RetryV2UniverseCase,
    output_paths: Dict[str, str],
    issues: List[str],
) -> None:
    write_dryrun_snapshot(phase3_retry_v2_to_phase25_case(case), output_paths, issues)


def process_phase3_retry_v2_dry_run(
    cases: List[Phase3RetryV2UniverseCase],
    output_paths: Dict[str, str],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = list(validate_phase3_retry_v2_duplicate_codes(cases))
    seen_codes: Set[str] = set()
    for case in cases:
        if case.retry_v2_include != "yes":
            continue
        issues = list(validate_phase3_retry_v2_case(case))
        if case.company_code in seen_codes:
            if DUPLICATE_COMPANY_CODE_REJECTED not in issues:
                issues.append(DUPLICATE_COMPANY_CODE_REJECTED)
        else:
            seen_codes.add(case.company_code)
        if issues:
            universe_issues.append(f"{case.retry_v2_case_id}:{';'.join(issues)}")
        write_phase3_retry_v2_dryrun_snapshot(case, output_paths, issues)
        rows.append(build_phase3_retry_v2_dryrun_row(case, issues, output_paths["root"]))
    return rows, universe_issues


def write_phase3_retry_v2_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_retry_v2_dryrun_report.csv"
    )
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_RETRY_V2_DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_phase3_retry_v2_dryrun_summary(
    output_paths: Dict[str, str],
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    planned_ok = sum(1 for r in rows if r.get("dryrun_status") == "planned_ok")
    total_planned = sum(int(r.get("planned_request_count", "0")) for r in rows)
    lines = [
        "# CNINFO B 类 Phase 3 100 Retry v2 — Dry-Run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 3 retry_v2 dry-run · **无 CNINFO** · **无 PDF 下载/解析**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | phase3_retry_v2_dry_run |",
        f"| retry_v2 universe size | {len(rows)} |",
        f"| planned_ok | {planned_ok} |",
        f"| total planned_request_count | {total_planned} |",
        "| CNINFO calls (dry-run) | **0** |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB write | **0** |",
        "| MinIO write | **0** |",
        "| RAG | **0** |",
        "",
        "## Output isolation",
        "",
        "```text",
        f"{output_paths['root']}",
        "```",
        "",
        "## Safety",
        "",
        f"- successful hold case {PHASE3_SUCCESS_HOLD_CASE_ID} excluded: **yes**",
        "- 8 recovered cases excluded: **yes**",
        "- prior B-class phases excluded: **yes**",
        "- Phase 3 expansion baseline write-blocked: **yes**",
        "- Phase 3 failed retry baseline write-blocked: **yes**",
        "- EP002 precheck baseline write-blocked: **yes**",
        "- Phase 2.5 expansion baseline write-blocked: **yes**",
        "- Phase 2.5 failed retry baseline write-blocked: **yes**",
        "- approval_status: **NOT_APPROVED**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase3_100_retry_v2_runner_extension_gate = {gate}",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_retry_v2_dryrun_summary.md"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def compute_phase3_retry_v2_runner_gate(
    universe_issues: List[str], case_count: int
) -> str:
    if universe_issues or case_count != REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE:
        return "FAIL"
    return "READY_FOR_APPROVAL"


def write_retry_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    path = os.path.join(
        output_paths["reports"], "b_class_phase25_failed_retry_dryrun_report.csv"
    )
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_retry_dryrun_summary(
    output_paths: Dict[str, str],
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    planned_ok = sum(1 for r in rows if r.get("dryrun_status") == "planned_ok")
    total_planned = sum(int(r.get("planned_request_count", "0")) for r in rows)
    lines = [
        "# CNINFO B 类 Phase 2.5 Failed-case Isolated Retry — Dry-Run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2.5 failed-case retry dry-run · **无 CNINFO** · **无 PDF 下载/解析**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | retry_dry_run |",
        f"| retry universe size | {len(rows)} |",
        f"| planned_ok | {planned_ok} |",
        f"| total planned_request_count | {total_planned} |",
        "| CNINFO calls (dry-run) | **0** |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "",
        "## Output isolation",
        "",
        "```text",
        f"{output_paths['root']}",
        "```",
        "",
        "## Safety",
        "",
        "- successful 45 cases excluded: **yes**",
        "- Phase 2.5 expansion baseline write-blocked: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase25_failed_retry_package_gate = {gate}",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    path = os.path.join(
        output_paths["reports"], "b_class_phase25_failed_retry_dryrun_summary.md"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def compute_retry_package_gate(universe_issues: List[str], case_count: int) -> str:
    if universe_issues or case_count != REQUIRED_RETRY_UNIVERSE_SIZE:
        return "FAIL"
    return "READY_FOR_APPROVAL"


def process_retry_live(
    cases: List[RetryUniverseCase],
    output_paths: Dict[str, str],
    categories_config: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], tiny_live.LiveStats, List[str]]:
    report_records: List[Dict[str, Any]] = []
    universe_issues: List[str] = []
    stats = tiny_live.LiveStats()

    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = validate_retry_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            continue
        p25 = retry_to_phase25_case(case)
        tl_case = to_tiny_live_case(p25)
        stats.companies_executed += 1
        record = tiny_live.execute_live_case(tl_case, categories_config, stats)
        record["notes"] = f"phase25 failed retry live; {record.get('notes', '')}"
        record["_phase25_case"] = p25
        record["_retry_case"] = case
        primary = record.get("endpoint_id") or SOURCE_TYPE_PRIMARY_ENDPOINT[tl_case.source_type]
        snap_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}_{primary}.json")
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": "retry_live",
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
        report_records.append(record)
        print(
            f"case_id={case.case_id} company_code={case.company_code} "
            f"retrieval_status={record.get('retrieval_status')}",
            flush=True,
        )
    return report_records, stats, universe_issues


def process_live(
    cases: List[Phase25UniverseCase],
    output_paths: Dict[str, str],
    categories_config: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], tiny_live.LiveStats, List[str]]:
    report_records: List[Dict[str, Any]] = []
    universe_issues: List[str] = []
    stats = tiny_live.LiveStats()

    for case in cases:
        if case.phase25_include != "yes":
            continue
        issues = validate_phase25_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            continue
        tl_case = to_tiny_live_case(case)
        stats.companies_executed += 1
        record = tiny_live.execute_live_case(tl_case, categories_config, stats)
        record["notes"] = f"phase25 expansion live; {record.get('notes', '')}"
        record["_phase25_case"] = case
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
        report_records.append(record)
        print(
            f"case_id={case.case_id} company_code={case.company_code} "
            f"retrieval_status={record.get('retrieval_status')}",
            flush=True,
        )
    return report_records, stats, universe_issues


def process_phase3_live(
    cases: List[Phase3UniverseCase],
    output_paths: Dict[str, str],
    categories_config: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], tiny_live.LiveStats, List[str]]:
    report_records: List[Dict[str, Any]] = []
    universe_issues: List[str] = []
    stats = tiny_live.LiveStats()

    for case in cases:
        if case.phase3_include != "yes":
            continue
        issues = validate_phase3_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            continue
        p25 = phase3_to_phase25_case(case)
        tl_case = to_tiny_live_case(p25)
        stats.companies_executed += 1
        record = tiny_live.execute_live_case(tl_case, categories_config, stats)
        record["notes"] = f"phase3 expansion live; {record.get('notes', '')}"
        record["_phase3_case"] = case
        record["_phase25_case"] = p25
        primary = record.get("endpoint_id") or SOURCE_TYPE_PRIMARY_ENDPOINT[tl_case.source_type]
        snap_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}_{primary}.json")
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": "phase3_live",
                    "cninfo_called": True,
                    "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                    "pdf_parse_enabled": PDF_PARSE_ENABLED,
                    "record": {k: record.get(k) for k in tiny_live.REPORT_COLUMNS},
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
        report_records.append(record)
        print(
            f"case_id={case.case_id} company_code={case.company_code} "
            f"retrieval_status={record.get('retrieval_status')}",
            flush=True,
        )
    return report_records, stats, universe_issues


def process_phase3_retry_live(
    cases: List[Phase3RetryUniverseCase],
    output_paths: Dict[str, str],
    categories_config: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], tiny_live.LiveStats, List[str]]:
    report_records: List[Dict[str, Any]] = []
    universe_issues: List[str] = []
    stats = tiny_live.LiveStats()

    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = validate_phase3_retry_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            continue
        p25 = phase3_retry_to_phase25_case(case)
        tl_case = to_tiny_live_case(p25)
        stats.companies_executed += 1
        record = tiny_live.execute_live_case(tl_case, categories_config, stats)
        if stats.cninfo_requests > MAX_PHASE3_RETRY_CNINFO_REQUESTS:
            universe_issues.append(
                f"cninfo_request_cap_exceeded:{stats.cninfo_requests}>{MAX_PHASE3_RETRY_CNINFO_REQUESTS}"
            )
            break
        record["notes"] = f"phase3 failed retry live; {record.get('notes', '')}"
        record["_phase3_retry_case"] = case
        record["_phase25_case"] = p25
        primary = record.get("endpoint_id") or SOURCE_TYPE_PRIMARY_ENDPOINT[tl_case.source_type]
        snap_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}_{primary}.json")
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": "phase3_failed_retry_live",
                    "cninfo_called": True,
                    "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                    "pdf_parse_enabled": PDF_PARSE_ENABLED,
                    "record": {k: record.get(k) for k in tiny_live.REPORT_COLUMNS},
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
        report_records.append(record)
        print(
            f"case_id={case.case_id} company_code={case.company_code} "
            f"retry_retrieval_status={record.get('retrieval_status')}",
            flush=True,
        )
    return report_records, stats, universe_issues


def _extract_announcement_date(announcement_time: Any) -> str:
    text = str(announcement_time or "").strip()
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    return ""


def _extract_failure_type(record: Dict[str, Any]) -> str:
    rs = str(record.get("retrieval_status") or "")
    err = str(record.get("error_type") or "").strip()
    if err:
        return err
    if rs in ("network_error", "not_found", "empty_response", "universe_validation_failed"):
        return rs
    return ""


def build_phase3_report_row(record: Dict[str, Any]) -> Dict[str, str]:
    case: Phase3UniverseCase = record["_phase3_case"]
    pdf_url = record.get("pdf_url") or ""
    adjunct_url = record.get("adjunct_url") or ""
    endpoint_used = record.get("endpoint_id") or ""
    announcement_time = str(record.get("announcement_time") or "")
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
        "announcement_time": announcement_time,
        "announcement_date": _extract_announcement_date(announcement_time),
        "pdf_url_present": "1" if _is_present(pdf_url) else "0",
        "adjunct_url_present": "1" if _is_present(adjunct_url) else "0",
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "endpoint_used": endpoint_used,
        "cninfo_request_count": str(record.get("_case_cninfo_requests", 0)),
        "failure_type": _extract_failure_type(record),
        "notes": str(record.get("notes") or ""),
    }


def compute_phase3_execution_gate(phase3_rows: List[Dict[str, str]]) -> str:
    if any(classify_case_acceptability(r) == "red_line_violation" for r in phase3_rows):
        return "FAIL_REVIEW_REQUIRED"
    acceptable = sum(
        1 for r in phase3_rows
        if classify_case_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    if acceptable >= PHASE3_ACCEPTABLE_THRESHOLD and len(phase3_rows) == REQUIRED_PHASE3_UNIVERSE_SIZE:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def write_live_phase3_reports(
    report_records: List[Dict[str, Any]],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    universe_issues: List[str],
) -> Tuple[str, str, str, str]:
    phase3_rows = [build_phase3_report_row(r) for r in report_records]
    gate = compute_phase3_execution_gate(phase3_rows)

    report_path = os.path.join(output_paths["reports"], "b_class_phase3_100_report.csv")
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(phase3_rows)

    quality_path = os.path.join(output_paths["reports"], "b_class_phase3_100_quality_report.csv")
    with open(quality_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        for row in phase3_rows:
            writer.writerow({k: row.get(k, "") for k in PHASE3_QUALITY_REPORT_COLUMNS})

    acceptable = sum(
        1 for r in phase3_rows
        if classify_case_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    failed = sum(1 for r in phase3_rows if classify_case_acceptability(r) == "failed")
    needs_review = sum(1 for r in phase3_rows if r.get("quality_status") == "needs_review")
    empty_but_valid = sum(
        1 for r in phase3_rows if classify_case_acceptability(r) == "empty_but_valid"
    )
    found = sum(1 for r in phase3_rows if r.get("retrieval_status") == "found")
    discovered = sum(1 for r in phase3_rows if r.get("lineage_status") == "discovered")

    summary_path = os.path.join(output_paths["reports"], "b_class_phase3_100_summary.md")
    lines = [
        "# CNINFO B 类 Phase 3 100-Company Expansion — Live Execution Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 3 100-company live metadata validation · **无 PDF 下载/解析** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | phase3_live |",
        f"| universe size | {len(phase3_rows)} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| found | {found} |",
        f"| discovered (lineage) | {discovered} |",
        f"| acceptable | {acceptable} |",
        f"| failed | {failed} |",
        f"| needs_review | {needs_review} |",
        f"| empty_but_valid | {empty_but_valid} |",
        "| PDF downloaded | **0** |",
        "| PDF parsed | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB / MinIO / RAG | **0** |",
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
        "- prior-phase cases not rerun: **yes**",
        "- Phase 2.5 expansion baseline untouched: **yes**",
        "- Phase 2.5 failed retry baseline untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase3_100_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ])
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_path, summary_path, quality_path, gate


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def build_expansion_report_row(record: Dict[str, Any]) -> Dict[str, str]:
    case: Phase25UniverseCase = record["_phase25_case"]
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


def build_retry_report_row(record: Dict[str, Any]) -> Dict[str, str]:
    case: RetryUniverseCase = record["_retry_case"]
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
        "original_failure_type": case.original_failure_type,
        "retry_retrieval_status": str(record.get("retrieval_status") or ""),
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": str(record.get("announcement_time") or ""),
        "pdf_url_present": "1" if _is_present(pdf_url) else "0",
        "adjunct_url_present": "1" if _is_present(adjunct_url) else "0",
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "endpoint_used": endpoint_used,
        "cninfo_request_count": str(record.get("_case_cninfo_requests", 0)),
        "notes": str(record.get("notes") or ""),
    }


def classify_retry_acceptability(row: Dict[str, str]) -> str:
    """retry 可接受性分类；使用 retry_retrieval_status 字段。"""
    adapted = dict(row)
    adapted["retrieval_status"] = row.get("retry_retrieval_status", "")
    return classify_case_acceptability(adapted)


def compute_retry_execution_gate(retry_rows: List[Dict[str, str]]) -> str:
    if any(classify_retry_acceptability(r) == "red_line_violation" for r in retry_rows):
        return "FAIL_REVIEW_REQUIRED"
    acceptable = sum(
        1 for r in retry_rows
        if classify_retry_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    if acceptable >= RETRY_ACCEPTABLE_THRESHOLD and len(retry_rows) == REQUIRED_RETRY_UNIVERSE_SIZE:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def build_phase3_retry_report_row(record: Dict[str, Any]) -> Dict[str, str]:
    case: Phase3RetryUniverseCase = record["_phase3_retry_case"]
    pdf_url = record.get("pdf_url") or ""
    adjunct_url = record.get("adjunct_url") or ""
    endpoint_used = record.get("endpoint_id") or ""
    announcement_time = str(record.get("announcement_time") or "")
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "announcement_type": case.announcement_type,
        "target_endpoint": ";".join(case.target_endpoint),
        "original_phase3_status": case.original_phase3_status,
        "original_failure_type": case.original_failure_type,
        "original_failure_stage": case.original_failure_stage,
        "retry_retrieval_status": str(record.get("retrieval_status") or ""),
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": announcement_time,
        "announcement_date": _extract_announcement_date(announcement_time),
        "pdf_url_present": "1" if _is_present(pdf_url) else "0",
        "adjunct_url_present": "1" if _is_present(adjunct_url) else "0",
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "endpoint_used": endpoint_used,
        "cninfo_request_count": str(record.get("_case_cninfo_requests", 0)),
        "failure_type": _extract_failure_type(record),
        "notes": str(record.get("notes") or ""),
    }


def classify_phase3_retry_acceptability(row: Dict[str, str]) -> str:
    """Phase 3 retry 可接受性分类；使用 retry_retrieval_status 字段。"""
    adapted = dict(row)
    adapted["retrieval_status"] = row.get("retry_retrieval_status", "")
    return classify_case_acceptability(adapted)


def compute_phase3_retry_execution_gate(retry_rows: List[Dict[str, str]]) -> str:
    if any(classify_phase3_retry_acceptability(r) == "red_line_violation" for r in retry_rows):
        return "FAIL_REVIEW_REQUIRED"
    acceptable = sum(
        1 for r in retry_rows
        if classify_phase3_retry_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    if (
        acceptable >= PHASE3_RETRY_ACCEPTABLE_THRESHOLD
        and len(retry_rows) == REQUIRED_PHASE3_RETRY_UNIVERSE_SIZE
    ):
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def compute_phase3_retry_max_planned_requests(cases: List[Phase3RetryUniverseCase]) -> int:
    total = 0
    for case in cases:
        if case.retry_include != "yes":
            continue
        _, _, _, _, req_count = _planned_endpoint_flags(phase3_retry_to_phase25_case(case))
        total += req_count
    return total


def write_live_phase3_retry_reports(
    report_records: List[Dict[str, Any]],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    universe_issues: List[str],
) -> Tuple[str, str, str, str]:
    retry_rows = [build_phase3_retry_report_row(r) for r in report_records]
    gate = compute_phase3_retry_execution_gate(retry_rows)

    report_path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_failed_retry_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_RETRY_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(retry_rows)

    quality_path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_failed_retry_quality_report.csv"
    )
    with open(quality_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_RETRY_QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        for row in retry_rows:
            writer.writerow({k: row.get(k, "") for k in PHASE3_RETRY_QUALITY_REPORT_COLUMNS})

    acceptable = sum(
        1 for r in retry_rows
        if classify_phase3_retry_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    failed = sum(1 for r in retry_rows if classify_phase3_retry_acceptability(r) == "failed")
    needs_review = sum(1 for r in retry_rows if r.get("quality_status") == "needs_review")
    empty_but_valid = sum(
        1 for r in retry_rows if classify_phase3_retry_acceptability(r) == "empty_but_valid"
    )
    found = sum(1 for r in retry_rows if r.get("retry_retrieval_status") == "found")
    discovered = sum(1 for r in retry_rows if r.get("lineage_status") == "discovered")

    summary_path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_failed_retry_summary.md"
    )
    lines = [
        "# CNINFO B 类 Phase 3 100 Failed-Case Isolated Retry — Live Execution Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 3 failed-case isolated retry live · **无 PDF 下载/解析** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | phase3_failed_retry_live |",
        f"| retry universe size | {len(retry_rows)} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| found | {found} |",
        f"| discovered (lineage) | {discovered} |",
        f"| acceptable | {acceptable} |",
        f"| failed | {failed} |",
        f"| needs_review | {needs_review} |",
        f"| empty_but_valid | {empty_but_valid} |",
        "| PDF downloaded | **0** |",
        "| PDF parsed | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB / MinIO / RAG | **0** |",
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
        f"- successful hold case {PHASE3_SUCCESS_HOLD_CASE_ID} not rerun: **yes**",
        "- Phase 3 expansion baseline untouched: **yes**",
        "- Phase 2.5 expansion baseline untouched: **yes**",
        "- Phase 2.5 failed retry baseline untouched: **yes**",
        "- metadata and pdf URL lineage only: **yes**",
        "- approval_status: **NOT_APPROVED** (until explicit human approval)",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase3_100_failed_retry_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ])
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_path, summary_path, quality_path, gate


def process_phase3_retry_v2_live(
    cases: List[Phase3RetryV2UniverseCase],
    output_paths: Dict[str, str],
    categories_config: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], tiny_live.LiveStats, List[str]]:
    report_records: List[Dict[str, Any]] = []
    universe_issues: List[str] = []
    stats = tiny_live.LiveStats()

    for case in cases:
        if case.retry_v2_include != "yes":
            continue
        issues = validate_phase3_retry_v2_case(case)
        if issues:
            universe_issues.append(f"{case.retry_v2_case_id}:{';'.join(issues)}")
            continue
        p25 = phase3_retry_v2_to_phase25_case(case)
        tl_case = to_tiny_live_case(p25)
        stats.companies_executed += 1
        record = tiny_live.execute_live_case(tl_case, categories_config, stats)
        if stats.cninfo_requests > MAX_PHASE3_RETRY_V2_CNINFO_REQUESTS:
            universe_issues.append(
                f"cninfo_request_cap_exceeded:{stats.cninfo_requests}>{MAX_PHASE3_RETRY_V2_CNINFO_REQUESTS}"
            )
            break
        record["notes"] = f"phase3 retry_v2 live; {record.get('notes', '')}"
        record["_phase3_retry_v2_case"] = case
        record["_phase25_case"] = p25
        primary = record.get("endpoint_id") or SOURCE_TYPE_PRIMARY_ENDPOINT[tl_case.source_type]
        snap_path = os.path.join(
            output_paths["raw_metadata"], f"{case.original_case_id}_{primary}.json"
        )
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "retry_v2_case_id": case.retry_v2_case_id,
                    "original_case_id": case.original_case_id,
                    "case": {
                        "retry_v2_case_id": case.retry_v2_case_id,
                        "original_case_id": case.original_case_id,
                        "company_code": case.company_code,
                        "company_name": case.company_name,
                        "market": case.market,
                        "announcement_type": case.announcement_type,
                        "target_endpoint": case.target_endpoint,
                        "original_phase3_status": case.original_phase3_status,
                        "failed_retry_status": case.failed_retry_status,
                        "final_effective_status_before_retry_v2": (
                            case.final_effective_status_before_retry_v2
                        ),
                        "persistent_failure_stage": case.persistent_failure_stage,
                        "ep002_precheck_signal": case.ep002_precheck_signal,
                        "retry_v2_include": case.retry_v2_include,
                        "notes": case.notes,
                    },
                    "mode": "phase3_retry_v2_live",
                    "cninfo_called": True,
                    "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                    "pdf_parse_enabled": PDF_PARSE_ENABLED,
                    "record": {k: record.get(k) for k in tiny_live.REPORT_COLUMNS},
                    "raw_announcement": record.get("raw_announcement"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        qpath = os.path.join(output_paths["quality"], f"{case.original_case_id}.json")
        with open(qpath, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "retry_v2_case_id": case.retry_v2_case_id,
                    "original_case_id": case.original_case_id,
                    "quality_status": record.get("quality_status"),
                    "lineage_status": record.get("lineage_status"),
                    "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                    "pdf_parse_enabled": PDF_PARSE_ENABLED,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        report_records.append(record)
        print(
            f"retry_v2_case_id={case.retry_v2_case_id} original_case_id={case.original_case_id} "
            f"company_code={case.company_code} "
            f"retry_retrieval_status={record.get('retrieval_status')}",
            flush=True,
        )
    return report_records, stats, universe_issues


def build_phase3_retry_v2_report_row(record: Dict[str, Any]) -> Dict[str, str]:
    case: Phase3RetryV2UniverseCase = record["_phase3_retry_v2_case"]
    pdf_url = record.get("pdf_url") or ""
    adjunct_url = record.get("adjunct_url") or ""
    endpoint_used = record.get("endpoint_id") or ""
    announcement_time = str(record.get("announcement_time") or "")
    return {
        "retry_v2_case_id": case.retry_v2_case_id,
        "original_case_id": case.original_case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "announcement_type": case.announcement_type,
        "target_endpoint": ";".join(case.target_endpoint),
        "original_phase3_status": case.original_phase3_status,
        "failed_retry_status": case.failed_retry_status,
        "final_effective_status_before_retry_v2": case.final_effective_status_before_retry_v2,
        "persistent_failure_stage": case.persistent_failure_stage,
        "ep002_precheck_signal": case.ep002_precheck_signal,
        "retry_v2_include": case.retry_v2_include,
        "retry_retrieval_status": str(record.get("retrieval_status") or ""),
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": announcement_time,
        "announcement_date": _extract_announcement_date(announcement_time),
        "pdf_url_present": "1" if _is_present(pdf_url) else "0",
        "adjunct_url_present": "1" if _is_present(adjunct_url) else "0",
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "endpoint_used": endpoint_used,
        "cninfo_request_count": str(record.get("_case_cninfo_requests", 0)),
        "failure_type": _extract_failure_type(record),
        "notes": str(record.get("notes") or ""),
    }


def classify_phase3_retry_v2_acceptability(row: Dict[str, str]) -> str:
    adapted = dict(row)
    adapted["retrieval_status"] = row.get("retry_retrieval_status", "")
    return classify_case_acceptability(adapted)


def compute_phase3_retry_v2_execution_gate(retry_rows: List[Dict[str, str]]) -> str:
    if any(classify_phase3_retry_v2_acceptability(r) == "red_line_violation" for r in retry_rows):
        return "FAIL_REVIEW_REQUIRED"
    acceptable = sum(
        1 for r in retry_rows
        if classify_phase3_retry_v2_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    if (
        acceptable >= PHASE3_RETRY_V2_ACCEPTABLE_THRESHOLD
        and len(retry_rows) == REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE
    ):
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def compute_phase3_retry_v2_max_planned_requests(
    cases: List[Phase3RetryV2UniverseCase],
) -> int:
    total = 0
    for case in cases:
        if case.retry_v2_include != "yes":
            continue
        _, _, _, _, req_count = _planned_endpoint_flags(phase3_retry_v2_to_phase25_case(case))
        total += req_count
    return total


def write_live_phase3_retry_v2_reports(
    report_records: List[Dict[str, Any]],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    universe_issues: List[str],
) -> Tuple[str, str, str, str]:
    retry_rows = [build_phase3_retry_v2_report_row(r) for r in report_records]
    gate = compute_phase3_retry_v2_execution_gate(retry_rows)

    report_path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_retry_v2_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_RETRY_V2_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(retry_rows)

    quality_path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_retry_v2_quality_report.csv"
    )
    with open(quality_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_RETRY_V2_QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        for row in retry_rows:
            writer.writerow({k: row.get(k, "") for k in PHASE3_RETRY_V2_QUALITY_REPORT_COLUMNS})

    acceptable = sum(
        1 for r in retry_rows
        if classify_phase3_retry_v2_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    failed = sum(1 for r in retry_rows if classify_phase3_retry_v2_acceptability(r) == "failed")
    needs_review = sum(1 for r in retry_rows if r.get("quality_status") == "needs_review")
    empty_but_valid = sum(
        1 for r in retry_rows if classify_phase3_retry_v2_acceptability(r) == "empty_but_valid"
    )
    found = sum(1 for r in retry_rows if r.get("retry_retrieval_status") == "found")
    discovered = sum(1 for r in retry_rows if r.get("lineage_status") == "discovered")

    summary_path = os.path.join(
        output_paths["reports"], "b_class_phase3_100_retry_v2_summary.md"
    )
    lines = [
        "# CNINFO B 类 Phase 3 100 Retry v2 — Live Execution Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 3 retry_v2 live · **无 PDF 下载/解析** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | phase3_retry_v2_live |",
        f"| retry_v2 universe size | {len(retry_rows)} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| found | {found} |",
        f"| discovered (lineage) | {discovered} |",
        f"| acceptable | {acceptable} |",
        f"| failed | {failed} |",
        f"| needs_review | {needs_review} |",
        f"| empty_but_valid | {empty_but_valid} |",
        "| PDF downloaded | **0** |",
        "| PDF parsed | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB / MinIO / RAG | **0** |",
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
        f"- successful hold case {PHASE3_SUCCESS_HOLD_CASE_ID} not rerun: **yes**",
        "- 8 recovered cases not rerun: **yes**",
        "- Phase 3 expansion baseline untouched: **yes**",
        "- Phase 3 failed retry baseline untouched: **yes**",
        "- EP002 precheck baseline untouched: **yes**",
        "- Phase 2.5 expansion baseline untouched: **yes**",
        "- Phase 2.5 failed retry baseline untouched: **yes**",
        "- metadata and pdf URL lineage only: **yes**",
        "- approval_status: **NOT_APPROVED** (until explicit human approval)",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase3_100_retry_v2_execution_gate = {gate}",
        "```",
        "",
        f"- acceptance threshold: **≥ {PHASE3_RETRY_V2_ACCEPTABLE_THRESHOLD}/{REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE}** → PASS_WITH_CAVEAT",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ])
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_path, summary_path, quality_path, gate


def write_live_retry_reports(
    report_records: List[Dict[str, Any]],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    universe_issues: List[str],
) -> Tuple[str, str, str, str]:
    retry_rows = [build_retry_report_row(r) for r in report_records]
    gate = compute_retry_execution_gate(retry_rows)

    report_path = os.path.join(
        output_paths["reports"], "b_class_phase25_failed_retry_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(retry_rows)

    quality_path = os.path.join(
        output_paths["reports"], "b_class_phase25_failed_retry_quality_report.csv"
    )
    with open(quality_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        for row in retry_rows:
            writer.writerow({k: row.get(k, "") for k in RETRY_QUALITY_REPORT_COLUMNS})

    acceptable = sum(
        1 for r in retry_rows
        if classify_retry_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    failed = sum(1 for r in retry_rows if classify_retry_acceptability(r) == "failed")
    needs_review = sum(1 for r in retry_rows if r.get("quality_status") == "needs_review")
    empty_but_valid = sum(
        1 for r in retry_rows if classify_retry_acceptability(r) == "empty_but_valid"
    )
    found = sum(1 for r in retry_rows if r.get("retry_retrieval_status") == "found")

    summary_path = os.path.join(
        output_paths["reports"], "b_class_phase25_failed_retry_summary.md"
    )
    lines = [
        "# CNINFO B 类 Phase 2.5 Failed-case Isolated Retry — Live Execution Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2.5 failed-case isolated retry live · **无 PDF 下载/解析** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | retry_live |",
        f"| retry universe size | {len(retry_rows)} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| found | {found} |",
        f"| acceptable | {acceptable} |",
        f"| failed | {failed} |",
        f"| needs_review | {needs_review} |",
        f"| empty_but_valid | {empty_but_valid} |",
        "| PDF downloaded | **0** |",
        "| PDF parsed | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
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
        "- successful 45 cases not rerun: **yes**",
        "- Phase 2.5 expansion baseline untouched: **yes**",
        "- metadata and pdf URL lineage only: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase25_failed_retry_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ])
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_path, summary_path, quality_path, gate


def compute_execution_gate(expansion_rows: List[Dict[str, str]]) -> str:
    if any(classify_case_acceptability(r) == "red_line_violation" for r in expansion_rows):
        return "FAIL"
    acceptable = sum(
        1 for r in expansion_rows
        if classify_case_acceptability(r) in (
            "acceptable", "needs_review_acceptable", "empty_but_valid"
        )
    )
    if acceptable >= ACCEPTABLE_THRESHOLD and len(expansion_rows) == REQUIRED_UNIVERSE_SIZE:
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

    report_path = os.path.join(output_paths["reports"], "b_class_phase25_expansion_report.csv")
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPANSION_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(expansion_rows)

    quality_path = os.path.join(
        output_paths["reports"], "b_class_phase25_expansion_quality_report.csv"
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

    summary_path = os.path.join(output_paths["reports"], "b_class_phase25_expansion_summary.md")
    lines = [
        "# CNINFO B 类 Phase 2.5 Expansion — Live Execution Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2.5 expansion live metadata validation · **无 PDF 下载/解析** · **不是 verified**",
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
        "- phase1_overlap: **0**",
        "- phase2_overlap: **0**",
        "- Phase 1 tiny live baseline untouched: **yes**",
        "- Phase 2 expansion baseline untouched: **yes**",
        "- C-class harvest untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase25_expansion_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready** · Phase 2.5 limited expansion only",
        "",
    ])
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return report_path, summary_path, quality_path, gate


def write_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    path = os.path.join(output_paths["reports"], "b_class_phase25_expansion_dryrun_report.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_dryrun_summary(
    output_paths: Dict[str, str],
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    planned_ok = sum(1 for r in rows if r.get("dryrun_status") == "planned_ok")
    total_planned_requests = sum(int(r.get("planned_request_count", "0")) for r in rows)
    ep004 = sum(1 for r in rows if r.get("planned_ep004") == "1")
    ep005 = sum(1 for r in rows if r.get("planned_ep005") == "1")
    ep002 = sum(1 for r in rows if r.get("planned_ep002") == "1")

    lines = [
        "# CNINFO B 类 Phase 2.5 Expansion — Dry-Run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2.5 expansion runner dry-run · **无 CNINFO** · **无 PDF 下载/解析**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| mode | dry_run |",
        f"| universe size | {len(rows)} |",
        f"| planned_ok | {planned_ok} |",
        f"| total planned_request_count | {total_planned_requests} |",
        f"| CNINFO calls (dry-run) | **0** |",
        f"| planned EP004 cases | {ep004} |",
        f"| planned EP005 cases | {ep005} |",
        f"| planned EP002 in target | {ep002} |",
        f"| PDF download | **0** |",
        f"| PDF parse | **0** |",
        "",
        "## Output isolation",
        "",
        f"```text",
        f"{output_paths['root']}",
        f"```",
        "",
        "## Safety",
        "",
        "- phase1_overlap: **0**",
        "- phase2_overlap: **0**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"b_class_phase25_expansion_runner_gate = {gate}",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues])
    path = os.path.join(output_paths["reports"], "b_class_phase25_expansion_dryrun_summary.md")
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
        description="CNINFO B-class Phase2.5 expansion metadata validation（dry-run default）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")

    parser.add_argument("--universe-csv", default=DEFAULT_UNIVERSE_CSV)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--approve-b-class-phase25-expansion",
        action="store_true",
        help="显式批准 B-class Phase 2.5 expansion live metadata validation",
    )
    parser.add_argument("--approve-b-class-phase2-expansion", action="store_true")
    parser.add_argument("--approve-b-class-tiny-live-validation", action="store_true")
    parser.add_argument("--approve-b-class-tlc002-retry", action="store_true")
    parser.add_argument("--approve-full-harvest", action="store_true")
    parser.add_argument("--approve-phase2-smoke-harvest", action="store_true")
    parser.add_argument("--approve-phase3-batch-500-harvest", action="store_true")
    parser.add_argument("--download-pdf", action="store_true")
    parser.add_argument("--parse-pdf", action="store_true")
    parser.add_argument("--run-ocr", dest="run_ocr", action="store_true")
    parser.add_argument("--extract-sections", dest="extract_sections", action="store_true")
    parser.add_argument("--write-db", action="store_true")
    parser.add_argument("--write-minio", action="store_true")
    parser.add_argument("--run-rag", action="store_true")
    parser.add_argument("--mark-verified", action="store_true")
    parser.add_argument("--mark-production-ready", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--retry-failed-only",
        action="store_true",
        help="5-case isolated failed retry 模式（dry-run 默认）",
    )
    parser.add_argument(
        "--approve-b-class-phase25-failed-retry",
        action="store_true",
        help="显式批准 B-class Phase 2.5 failed-case isolated retry live",
    )
    parser.add_argument(
        "--phase3-100",
        action="store_true",
        help="100-case Phase 3 expansion 模式（dry-run 默认）",
    )
    parser.add_argument(
        "--approve-b-class-phase3-100-expansion",
        action="store_true",
        help="显式批准 B-class Phase 3 100-company expansion live",
    )
    parser.add_argument(
        "--phase3-100-failed-retry",
        action="store_true",
        help="99-case Phase 3 failed-case isolated retry 模式（dry-run 默认）",
    )
    parser.add_argument(
        "--approve-b-class-phase3-100-failed-retry",
        action="store_true",
        help="显式批准 B-class Phase 3 100 failed-case isolated retry live",
    )
    parser.add_argument(
        "--phase3-100-retry-v2",
        action="store_true",
        help="91-case Phase 3 retry v2 模式（dry-run 默认）",
    )
    parser.add_argument(
        "--approve-b-class-phase3-100-retry-v2",
        action="store_true",
        help="显式批准 B-class Phase 3 100 retry v2 live",
    )
    parser.add_argument(
        "--approve-b-class-phase3-100-ep002-reachability-precheck",
        action="store_true",
        help="EP002 precheck 批准 flag（retry_v2 模式下为 wrong approval）",
    )
    return parser


def _run_phase3_retry_v2_mode(args: argparse.Namespace) -> int:
    if args.mode == "live":
        enforce_phase3_retry_v2_approval_gate(args)

    ok_csv, csv_err = validate_phase3_retry_v2_universe_csv_path(args.universe_csv)
    if not ok_csv:
        print(f"ERROR: {csv_err}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_phase3_retry_v2_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    if args.limit is not None and args.limit != REQUIRED_PHASE3_RETRY_V2_UNIVERSE_SIZE:
        print(
            f"ERROR: {PHASE3_RETRY_V2_UNIVERSE_SIZE_VIOLATION}: limit={args.limit}",
            file=sys.stderr,
        )
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))
    cases = load_phase3_retry_v2_universe(args.universe_csv)
    included = [c for c in cases if c.retry_v2_include == "yes"]
    if args.limit is not None:
        included = included[: args.limit]

    ok_size, size_err = validate_phase3_retry_v2_universe_size(included)
    if not ok_size:
        print(f"ERROR: {size_err}", file=sys.stderr)
        return 2

    if args.mode == "dry_run":
        dryrun_rows, universe_issues = process_phase3_retry_v2_dry_run(
            included, output_paths
        )
        report_path = write_phase3_retry_v2_dryrun_report(dryrun_rows, output_paths)
        gate = compute_phase3_retry_v2_runner_gate(universe_issues, len(included))
        summary_path = write_phase3_retry_v2_dryrun_summary(
            output_paths, dryrun_rows, universe_issues, gate
        )
        total_planned = sum(int(r.get("planned_request_count", "0")) for r in dryrun_rows)
        print(
            f"mode=phase3_retry_v2_dry_run cases={len(included)} "
            f"planned_ok={sum(1 for r in dryrun_rows if r['dryrun_status']=='planned_ok')} "
            f"cninfo_calls=0"
        )
        print(f"planned_request_count_total={total_planned}")
        print(f"gate=b_class_phase3_100_retry_v2_runner_extension_gate={gate}")
        print(f"dryrun_report={report_path}")
        print(f"dryrun_summary={summary_path}")
        if universe_issues:
            print(f"universe_issues={len(universe_issues)}", file=sys.stderr)
            return 1
        return 0

    with open(CATEGORIES_YAML, encoding="utf-8") as f:
        categories_config = yaml.safe_load(f) or {}
    report_records, stats, universe_issues = process_phase3_retry_v2_live(
        included, output_paths, categories_config
    )
    if stats.cninfo_requests > MAX_PHASE3_RETRY_V2_CNINFO_REQUESTS:
        universe_issues.append(
            f"cninfo_request_cap_exceeded:{stats.cninfo_requests}>{MAX_PHASE3_RETRY_V2_CNINFO_REQUESTS}"
        )
    report_path, summary_path, quality_path, gate = write_live_phase3_retry_v2_reports(
        report_records, output_paths, stats, universe_issues
    )
    print(
        f"mode=phase3_retry_v2_live cases={len(included)} "
        f"executed={len(report_records)} cninfo_calls={stats.cninfo_requests}"
    )
    print(f"gate=b_class_phase3_100_retry_v2_execution_gate={gate}")
    print(f"report={report_path}")
    print(f"summary={summary_path}")
    print(f"quality={quality_path}")
    if universe_issues:
        return 1
    if gate == "FAIL_REVIEW_REQUIRED":
        return 1
    return 0


def _run_phase3_retry_mode(args: argparse.Namespace) -> int:
    if args.mode == "live":
        enforce_phase3_retry_approval_gate(args)

    ok_csv, csv_err = validate_phase3_retry_universe_csv_path(args.universe_csv)
    if not ok_csv:
        print(f"ERROR: {csv_err}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_phase3_retry_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    if args.limit is not None and args.limit != REQUIRED_PHASE3_RETRY_UNIVERSE_SIZE:
        print(
            f"ERROR: {PHASE3_RETRY_UNIVERSE_SIZE_VIOLATION}: limit={args.limit}",
            file=sys.stderr,
        )
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))
    cases = load_phase3_retry_universe(args.universe_csv)
    included = [c for c in cases if c.retry_include == "yes"]
    if args.limit is not None:
        included = included[: args.limit]

    ok_size, size_err = validate_phase3_retry_universe_size(included)
    if not ok_size:
        print(f"ERROR: {size_err}", file=sys.stderr)
        return 2

    if args.mode == "dry_run":
        dryrun_rows, universe_issues = process_phase3_retry_dry_run(included, output_paths)
        report_path = write_phase3_retry_dryrun_report(dryrun_rows, output_paths)
        gate = compute_phase3_retry_runner_gate(universe_issues, len(included))
        summary_path = write_phase3_retry_dryrun_summary(
            output_paths, dryrun_rows, universe_issues, gate
        )
        total_planned = sum(int(r.get("planned_request_count", "0")) for r in dryrun_rows)
        print(
            f"mode=phase3_failed_retry_dry_run cases={len(included)} "
            f"planned_ok={sum(1 for r in dryrun_rows if r['dryrun_status']=='planned_ok')} "
            f"cninfo_calls=0"
        )
        print(f"planned_request_count_total={total_planned}")
        print(f"gate=b_class_phase3_100_failed_retry_runner_extension_gate={gate}")
        print(f"dryrun_report={report_path}")
        print(f"dryrun_summary={summary_path}")
        if universe_issues:
            print(f"universe_issues={len(universe_issues)}", file=sys.stderr)
            return 1
        return 0

    with open(CATEGORIES_YAML, encoding="utf-8") as f:
        categories_config = yaml.safe_load(f) or {}
    report_records, stats, universe_issues = process_phase3_retry_live(
        included, output_paths, categories_config
    )
    if stats.cninfo_requests > MAX_PHASE3_RETRY_CNINFO_REQUESTS:
        universe_issues.append(
            f"cninfo_request_cap_exceeded:{stats.cninfo_requests}>{MAX_PHASE3_RETRY_CNINFO_REQUESTS}"
        )
    report_path, summary_path, quality_path, gate = write_live_phase3_retry_reports(
        report_records, output_paths, stats, universe_issues
    )
    print(
        f"mode=phase3_failed_retry_live cases={len(included)} "
        f"executed={len(report_records)} cninfo_calls={stats.cninfo_requests}"
    )
    print(f"gate=b_class_phase3_100_failed_retry_execution_gate={gate}")
    print(f"report={report_path}")
    print(f"summary={summary_path}")
    print(f"quality={quality_path}")
    if universe_issues:
        return 1
    if gate == "FAIL_REVIEW_REQUIRED":
        return 1
    return 0


def _run_phase3_mode(args: argparse.Namespace) -> int:
    if args.mode == "live":
        enforce_phase3_approval_gate(args)

    ok_csv, csv_err = validate_phase3_universe_csv_path(args.universe_csv)
    if not ok_csv:
        print(f"ERROR: {csv_err}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_phase3_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    if args.limit is not None and args.limit != REQUIRED_PHASE3_UNIVERSE_SIZE:
        print(f"ERROR: {PHASE3_UNIVERSE_SIZE_VIOLATION}: limit={args.limit}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))
    cases = load_phase3_universe(args.universe_csv)
    included = [c for c in cases if c.phase3_include == "yes"]
    if args.limit is not None:
        included = included[: args.limit]

    ok_size, size_err = validate_phase3_universe_size(included)
    if not ok_size:
        print(f"ERROR: {size_err}", file=sys.stderr)
        return 2

    if args.mode == "dry_run":
        dryrun_rows, universe_issues = process_phase3_dry_run(included, output_paths)
        report_path = write_phase3_dryrun_report(dryrun_rows, output_paths)
        gate = compute_phase3_runner_gate(universe_issues, len(included))
        summary_path = write_phase3_dryrun_summary(
            output_paths, dryrun_rows, universe_issues, gate
        )
        total_planned = sum(int(r.get("planned_request_count", "0")) for r in dryrun_rows)
        print(
            f"mode=phase3_dry_run cases={len(included)} "
            f"planned_ok={sum(1 for r in dryrun_rows if r['dryrun_status']=='planned_ok')} cninfo_calls=0"
        )
        print(f"planned_request_count_total={total_planned}")
        print(f"gate=b_class_phase3_100_runner_extension_gate={gate}")
        print(f"dryrun_report={report_path}")
        print(f"dryrun_summary={summary_path}")
        if universe_issues:
            print(f"universe_issues={len(universe_issues)}", file=sys.stderr)
            return 1
        return 0

    with open(CATEGORIES_YAML, encoding="utf-8") as f:
        categories_config = yaml.safe_load(f) or {}
    report_records, stats, universe_issues = process_phase3_live(
        included, output_paths, categories_config
    )
    report_path, summary_path, quality_path, gate = write_live_phase3_reports(
        report_records, output_paths, stats, universe_issues
    )
    print(f"mode=phase3_live cases={len(included)} cninfo_calls={stats.cninfo_requests}")
    print(f"gate=b_class_phase3_100_execution_gate={gate}")
    print(f"report={report_path}")
    print(f"summary={summary_path}")
    print(f"quality={quality_path}")
    if universe_issues:
        return 1
    if gate == "FAIL_REVIEW_REQUIRED":
        return 1
    return 0


def _run_retry_mode(args: argparse.Namespace) -> int:
    if args.mode == "live":
        enforce_retry_approval_gate(args)

    ok_root, root_err = validate_retry_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    if args.limit is not None and args.limit != REQUIRED_RETRY_UNIVERSE_SIZE:
        print(f"ERROR: {RETRY_UNIVERSE_SIZE_VIOLATION}: limit={args.limit}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))
    cases = load_retry_universe(args.universe_csv)
    included = [c for c in cases if c.retry_include == "yes"]
    if args.limit is not None:
        included = included[: args.limit]

    ok_size, size_err = validate_retry_universe_size(included)
    if not ok_size:
        print(f"ERROR: {size_err}", file=sys.stderr)
        return 2

    if args.mode == "dry_run":
        dryrun_rows, universe_issues = process_retry_dry_run(included, output_paths)
        report_path = write_retry_dryrun_report(dryrun_rows, output_paths)
        gate = compute_retry_package_gate(universe_issues, len(included))
        summary_path = write_retry_dryrun_summary(
            output_paths, dryrun_rows, universe_issues, gate
        )
        total_planned = sum(int(r.get("planned_request_count", "0")) for r in dryrun_rows)
        print(
            f"mode=retry_dry_run cases={len(included)} "
            f"planned_ok={sum(1 for r in dryrun_rows if r['dryrun_status']=='planned_ok')} cninfo_calls=0"
        )
        print(f"planned_request_count_total={total_planned}")
        print(f"gate=b_class_phase25_failed_retry_package_gate={gate}")
        print(f"dryrun_report={report_path}")
        print(f"dryrun_summary={summary_path}")
        if universe_issues:
            print(f"universe_issues={len(universe_issues)}", file=sys.stderr)
            return 1
        return 0

    with open(CATEGORIES_YAML, encoding="utf-8") as f:
        categories_config = yaml.safe_load(f) or {}
    report_records, stats, universe_issues = process_retry_live(
        included, output_paths, categories_config
    )
    report_path, summary_path, quality_path, gate = write_live_retry_reports(
        report_records, output_paths, stats, universe_issues
    )
    live_report = os.path.join(
        output_paths["reports"], "b_class_phase25_failed_retry_live_report.csv"
    )
    with open(live_report, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        for record in report_records:
            writer.writerow({k: str(record.get(k, "")) for k in LIVE_REPORT_COLUMNS})
    print(f"mode=retry_live cases={len(included)} cninfo_calls={stats.cninfo_requests}")
    print(f"gate=b_class_phase25_failed_retry_execution_gate={gate}")
    print(f"report={report_path}")
    print(f"summary={summary_path}")
    print(f"quality={quality_path}")
    if universe_issues:
        return 1
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.phase3_100_retry_v2:
        if args.universe_csv == DEFAULT_UNIVERSE_CSV:
            args.universe_csv = DEFAULT_PHASE3_RETRY_V2_UNIVERSE_CSV
        if args.output_root == DEFAULT_OUTPUT_ROOT:
            args.output_root = DEFAULT_PHASE3_RETRY_V2_OUTPUT_ROOT
        enforce_forbidden_options(args)
        return _run_phase3_retry_v2_mode(args)

    if args.phase3_100_failed_retry:
        if args.universe_csv == DEFAULT_UNIVERSE_CSV:
            args.universe_csv = DEFAULT_PHASE3_RETRY_UNIVERSE_CSV
        if args.output_root == DEFAULT_OUTPUT_ROOT:
            args.output_root = DEFAULT_PHASE3_RETRY_OUTPUT_ROOT
        enforce_forbidden_options(args)
        return _run_phase3_retry_mode(args)

    if args.phase3_100:
        if args.universe_csv == DEFAULT_UNIVERSE_CSV:
            args.universe_csv = DEFAULT_PHASE3_UNIVERSE_CSV
        if args.output_root == DEFAULT_OUTPUT_ROOT:
            args.output_root = DEFAULT_PHASE3_OUTPUT_ROOT
        enforce_forbidden_options(args)
        return _run_phase3_mode(args)

    if args.retry_failed_only:
        if args.universe_csv == DEFAULT_UNIVERSE_CSV:
            args.universe_csv = DEFAULT_RETRY_UNIVERSE_CSV
        if args.output_root == DEFAULT_OUTPUT_ROOT:
            args.output_root = DEFAULT_RETRY_OUTPUT_ROOT
        enforce_forbidden_options(args)
        return _run_retry_mode(args)

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
    included = [c for c in cases if c.phase25_include == "yes"]
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
        summary_path = write_dryrun_summary(output_paths, dryrun_rows, universe_issues, gate)
        total_planned = sum(int(r.get("planned_request_count", "0")) for r in dryrun_rows)
        print(f"mode=dry_run cases={len(included)} planned_ok={sum(1 for r in dryrun_rows if r['dryrun_status']=='planned_ok')} cninfo_calls=0")
        print(f"planned_request_count_total={total_planned}")
        print(f"gate=b_class_phase25_expansion_runner_gate={gate}")
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
    live_report = os.path.join(output_paths["reports"], "b_class_phase25_expansion_live_report.csv")
    with open(live_report, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        for record in report_records:
            writer.writerow({k: str(record.get(k, "")) for k in LIVE_REPORT_COLUMNS})
    print(f"mode=live cases={len(included)} cninfo_calls={stats.cninfo_requests}")
    print(f"gate=b_class_phase25_expansion_execution_gate={gate}")
    print(f"report={report_path}")
    print(f"summary={summary_path}")
    print(f"quality={quality_path}")
    if universe_issues or gate == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
