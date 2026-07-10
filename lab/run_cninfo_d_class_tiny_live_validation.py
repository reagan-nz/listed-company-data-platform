"""
CNINFO D-class Phase 1 tiny live metadata validation runner.

默认 dry-run：校验 universe · 输出隔离 · 质量规则，**不请求 CNINFO**。
--live 须 --approve-d-class-tiny-live-validation；仅 event/metadata 探针 · 无 DB/MinIO/RAG。

Usage:
    python lab/run_cninfo_d_class_tiny_live_validation.py
    python lab/run_cninfo_d_class_tiny_live_validation.py --dry-run
    python lab/run_cninfo_d_class_tiny_live_validation.py --live \\
        --approve-d-class-tiny-live-validation
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import os
import sys
import time
from dataclasses import dataclass, field
import calendar
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import requests
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_phase1_tiny_live_universe.csv",
)
DEFAULT_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class_tiny_live_validation"
)
DEFAULT_V2_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_d_class_tiny_live_validation_v2"
)
DEFAULT_V2_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv",
)
V1_LIVE_REPORT_CSV = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "d_class_tiny_live_report.csv"
)
DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "d_class_tiny_live_dryrun_report.csv"
)
DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "d_class_tiny_live_dryrun_summary.md"
)
V2_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_V2_OUTPUT_ROOT,
    "reports",
    "d_class_tiny_live_v2_bounded_probe_dryrun_report.csv",
)
V2_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_V2_OUTPUT_ROOT,
    "reports",
    "d_class_tiny_live_v2_bounded_probe_dryrun_summary.md",
)
DEFAULT_REPLACEMENT_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_known_event_replacement_validation",
)
DEFAULT_REPLACEMENT_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_tiny_live_replacement_universe_filled.csv",
)
CALIBRATED_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_phase1_tiny_live_universe_calibrated.csv",
)
REPLACEMENT_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_REPLACEMENT_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_replacement_dryrun_report.csv",
)
REPLACEMENT_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_REPLACEMENT_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_replacement_dryrun_summary.md",
)
DEFAULT_TARGETED_PROBE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_known_event_targeted_probe",
)
DEFAULT_TARGETED_PROBE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_known_event_targeted_probe_universe_draft.csv",
)
TARGETED_PROBE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_TARGETED_PROBE_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_targeted_probe_dryrun_report.csv",
)
TARGETED_PROBE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_TARGETED_PROBE_OUTPUT_ROOT,
    "reports",
    "d_class_known_event_targeted_probe_dryrun_summary.md",
)
V2_COMPARISON_REPORT_CSV = os.path.join(
    DEFAULT_V2_OUTPUT_ROOT,
    "reports",
    "d_class_tiny_live_v2_comparison_report.csv",
)
TABLE_SOURCES_YAML = os.path.join(BASE_DIR, "config", "cninfo_table_sources.yaml")
REGISTRY_YAML = os.path.join(BASE_DIR, "config", "cninfo_d_class_source_registry_draft.yaml")
QUALITY_POLICY = os.path.join(BASE_DIR, "plans", "cninfo_d_class_event_quality_policy.md")

SLEEP_SECONDS = 0.6
REQUEST_TIMEOUT = 10

AJAX_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
        "ListedCompanyDataCollector/d-class-tiny-live"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.cninfo.com.cn/",
}

RUNNER_GATE = "READY_FOR_APPROVAL"
V2_RUNNER_GATE = "READY_FOR_APPROVAL"
EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
EXECUTION_GATE_FAIL = "FAIL"
V2_PROBE_CASE_IDS: Set[str] = {"DLC003", "DLC006"}
V2_BASELINE_CASE_IDS: Set[str] = {"DLC001", "DLC002", "DLC004", "DLC005", "DLC007"}
V2_DLC003_MAX_CAP = 24
V2_DLC006_MAX_CAP = 20
V2_TOTAL_MAX_CAP = 44
V2_REFERENCE_DATE = date(2026, 7, 9)
EXPECTED_UNIVERSE_SIZE = 7
ALLOWED_CASE_IDS: Set[str] = {f"DLC{i:03d}" for i in range(1, 8)}

ALLOWED_COMPONENTS: Set[str] = {
    "margin_trading",
    "block_trade",
    "restricted_shares_unlock",
    "disclosure_schedule",
    "equity_pledge",
    "shareholder_change",
    "executive_shareholding",
}

TINY_LIVE_APPROVAL_REQUIRED = "approve_d_class_tiny_live_validation_required"
WRONG_APPROVAL_FLAG = "wrong_approval_flag_not_allowed_for_d_class_tiny_live"
OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_d_class_tiny_live_validation"
UNIVERSE_SIZE_MISMATCH = "universe_size_must_equal_7"
NON_DLC_CASE = "only_dlc001_dlc007_allowed"
COMPONENT_NOT_ALLOWED = "component_not_in_phase1_scope"
DB_WRITE_BLOCKED = "db_write_not_allowed"
MINIO_WRITE_BLOCKED = "minio_write_not_allowed"
RAG_RUN_BLOCKED = "rag_run_not_allowed"
VERIFIED_BLOCKED = "verified_status_not_allowed"
PRODUCTION_READY_BLOCKED = "production_ready_not_allowed"
V2_OUTPUT_ROOT_REQUIRED = "v2_output_root_must_be_cninfo_d_class_tiny_live_validation_v2"
V1_OUTPUT_ROOT_WRITE_BLOCKED = "v1_output_root_write_blocked_for_bounded_probe_v2"
V2_APPROVAL_REQUIRED = "approve_d_class_tiny_live_v2_bounded_probe_required"
V2_WRONG_APPROVAL_FLAG = "wrong_approval_flag_for_bounded_probe_v2"
V2_PROBE_CASE_ONLY = "only_dlc003_dlc006_may_execute_bounded_probes"
V2_DLC003_CAP_EXCEEDED = "dlc003_request_cap_exceeded"
V2_DLC006_CAP_EXCEEDED = "dlc006_request_cap_exceeded"
V2_TOTAL_CAP_EXCEEDED = "v2_total_request_cap_exceeded"
V2_INVENTED_COMPANY_CODE = "invented_or_placeholder_company_code_not_allowed"
V2_MIXED_MODE_BLOCKED = "bounded_probe_v2_incompatible_with_v1_live_approval"

REPLACEMENT_RUNNER_GATE = "READY_FOR_APPROVAL"
REPLACEMENT_PROBE_CASE_IDS: Set[str] = {"DLC003R", "DLC006R"}
REPLACEMENT_BASELINE_CASE_IDS: Set[str] = {"DLC001", "DLC002", "DLC004", "DLC005", "DLC007"}
REPLACEMENT_ALLOWED_CASE_IDS: Set[str] = REPLACEMENT_PROBE_CASE_IDS | REPLACEMENT_BASELINE_CASE_IDS
REPLACEMENT_PLACEHOLDER_CASE_IDS: Set[str] = {
    "DLC003R_CANDIDATE_REQUIRED",
    "DLC006R_CANDIDATE_REQUIRED",
}
REPLACEMENT_FORBIDDEN_ORIGINAL_CASE_IDS: Set[str] = {"DLC003", "DLC006"}
REPLACEMENT_DLC003R_COMPANY_CODE = "688671"
REPLACEMENT_DLC006R_COMPANY_CODE = "301259"
REPLACEMENT_CANDIDATE_VALIDATED = "HUMAN_CANDIDATE_VALIDATED"
REPLACEMENT_DLC003R_MAX_CAP = 24
REPLACEMENT_DLC006R_MAX_CAP = 20
REPLACEMENT_TOTAL_MAX_CAP = 44

REPLACEMENT_APPROVAL_REQUIRED = "approve_d_class_known_event_replacement_validation_required"
REPLACEMENT_WRONG_APPROVAL_FLAG = "wrong_approval_flag_for_known_event_replacement"
REPLACEMENT_MIXED_MODE_BLOCKED = "known_event_replacement_incompatible_with_other_modes"
REPLACEMENT_UNIVERSE_CSV_REQUIRED = "known_event_replacement_requires_explicit_universe_csv"
REPLACEMENT_OUTPUT_ROOT_REQUIRED = (
    "replacement_output_root_must_be_cninfo_d_class_known_event_replacement_validation"
)
REPLACEMENT_V1_OUTPUT_ROOT_WRITE_BLOCKED = "v1_output_root_write_blocked_for_known_event_replacement"
REPLACEMENT_V2_OUTPUT_ROOT_WRITE_BLOCKED = "v2_output_root_write_blocked_for_known_event_replacement"
REPLACEMENT_CALIBRATED_UNIVERSE_WRITE_BLOCKED = (
    "calibrated_universe_write_blocked_for_known_event_replacement"
)
REPLACEMENT_ORIGINAL_UNIVERSE_WRITE_BLOCKED = (
    "original_v1_universe_write_blocked_for_known_event_replacement"
)
REPLACEMENT_PLACEHOLDER_ROW_REJECTED = "placeholder_replacement_row_not_allowed"
REPLACEMENT_ORIGINAL_CASE_IN_UNIVERSE = "original_dlc003_dlc006_not_allowed_in_replacement_universe"
REPLACEMENT_WRONG_COMPANY_CODE = "replacement_company_code_mismatch"
REPLACEMENT_INVALID_CANDIDATE_STATUS = "replacement_candidate_validation_status_invalid"
REPLACEMENT_PROBE_CASE_ONLY = "only_dlc003r_dlc006r_may_execute_replacement_probes"
REPLACEMENT_LIVE_IMPLEMENTATION_GATE = "READY_FOR_APPROVAL"
REPLACEMENT_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
REPLACEMENT_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
REPLACEMENT_DLC003R_CAP_EXCEEDED = "dlc003r_request_cap_exceeded"
REPLACEMENT_DLC006R_CAP_EXCEEDED = "dlc006r_request_cap_exceeded"
REPLACEMENT_TOTAL_CAP_EXCEEDED = "replacement_total_request_cap_exceeded"
PDF_DOWNLOAD_BLOCKED = "pdf_download_not_allowed"
OCR_BLOCKED = "ocr_not_allowed"
EXTRACTION_BLOCKED = "extraction_not_allowed"

TARGETED_PROBE_RUNNER_GATE = "READY_FOR_APPROVAL"
TARGETED_PROBE_EXPECTED_UNIVERSE_SIZE = 2
TARGETED_PROBE_ALLOWED_IDS: Set[str] = {"DLC003R-T01", "DLC006R-T01"}
TARGETED_PROBE_REPLACEMENT_IDS: Set[str] = {"DLC003R", "DLC006R"}
TARGETED_PROBE_FORBIDDEN_ORIGINAL_IDS: Set[str] = {"DLC003", "DLC006"}
TARGETED_PROBE_FORBIDDEN_BASELINE_IDS: Set[str] = {
    "DLC001",
    "DLC002",
    "DLC004",
    "DLC005",
    "DLC007",
}
TARGETED_PROBE_DLC003R_T01_COMPANY_CODE = "688671"
TARGETED_PROBE_DLC006R_T01_COMPANY_CODE = "301259"
TARGETED_PROBE_DLC003R_T01_COMPONENT = "restricted_shares_unlock"
TARGETED_PROBE_DLC006R_T01_COMPONENT = "shareholder_change"
TARGETED_PROBE_DLC003R_T01_ANCHOR_DATE = "2024-02-19"
TARGETED_PROBE_DLC006R_T01_ANCHOR_DATE = "2024-07-16"
TARGETED_PROBE_PER_ROW_MAX_CAP = 12
TARGETED_PROBE_TOTAL_MAX_CAP = 24

TARGETED_PROBE_APPROVAL_REQUIRED = "approve_d_class_known_event_targeted_probe_required"
TARGETED_PROBE_WRONG_APPROVAL_FLAG = "wrong_approval_flag_for_known_event_targeted_probe"
TARGETED_PROBE_MIXED_MODE_BLOCKED = "known_event_targeted_probe_incompatible_with_other_modes"
TARGETED_PROBE_UNIVERSE_CSV_REQUIRED = "known_event_targeted_probe_requires_explicit_universe_csv"
TARGETED_PROBE_OUTPUT_ROOT_REQUIRED = (
    "targeted_probe_output_root_must_be_cninfo_d_class_known_event_targeted_probe"
)
TARGETED_PROBE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_known_event_targeted_probe"
)
TARGETED_PROBE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_known_event_targeted_probe"
)
TARGETED_PROBE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_live_output_root_write_blocked_for_known_event_targeted_probe"
)
TARGETED_PROBE_CALIBRATED_UNIVERSE_WRITE_BLOCKED = (
    "calibrated_universe_write_blocked_for_known_event_targeted_probe"
)
TARGETED_PROBE_ORIGINAL_UNIVERSE_WRITE_BLOCKED = (
    "original_v1_universe_write_blocked_for_known_event_targeted_probe"
)
TARGETED_PROBE_UNIVERSE_SIZE_MISMATCH = "targeted_probe_universe_size_must_equal_2"
TARGETED_PROBE_FORBIDDEN_CASE_ID = "forbidden_case_id_in_targeted_probe_universe"
TARGETED_PROBE_ORIGINAL_CASE_IN_UNIVERSE = "original_dlc003_dlc006_not_allowed_in_targeted_probe_universe"
TARGETED_PROBE_BASELINE_CASE_IN_UNIVERSE = "baseline_case_not_allowed_in_targeted_probe_universe"
TARGETED_PROBE_WRONG_COMPANY_CODE = "targeted_probe_company_code_mismatch"
TARGETED_PROBE_WRONG_COMPONENT = "targeted_probe_component_mismatch"
TARGETED_PROBE_WRONG_ANCHOR_DATE = "targeted_probe_anchor_date_mismatch"
TARGETED_PROBE_INCLUDE_REQUIRED = "targeted_probe_include_must_be_yes"
TARGETED_PROBE_ROW_CAP_EXCEEDED = "targeted_probe_row_request_cap_exceeded"
TARGETED_PROBE_TOTAL_CAP_EXCEEDED = "targeted_probe_total_request_cap_exceeded"
TARGETED_PROBE_LIVE_IMPLEMENTATION_GATE = "READY_FOR_APPROVAL"
TARGETED_PROBE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
TARGETED_PROBE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"

TARGETED_PROBE_LIVE_REPORT_COLUMNS = [
    "targeted_probe_id",
    "replacement_case_id",
    "company_code",
    "company_name",
    "component",
    "anchor_date",
    "expected_behavior",
    "request_cap",
    "cninfo_request_count",
    "retrieval_status",
    "record_count",
    "quality_status",
    "lineage_status",
    "acceptable",
    "failure_type",
    "endpoint_used",
    "structured_record_evidence",
    "pdf_download",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "notes",
]

TARGETED_PROBE_QUALITY_REPORT_COLUMNS = [
    "targeted_probe_id",
    "replacement_case_id",
    "component",
    "anchor_date",
    "expected_behavior",
    "retrieval_status",
    "record_count",
    "quality_status",
    "acceptable",
    "failure_type",
    "structured_record_evidence",
    "cninfo_request_count",
    "notes",
]

TARGETED_PROBE_DRYRUN_REPORT_COLUMNS = [
    "targeted_probe_id",
    "replacement_case_id",
    "company_code",
    "company_name",
    "component",
    "anchor_date",
    "human_event_evidence_type",
    "human_event_evidence_description",
    "previous_replacement_live_status",
    "previous_record_count",
    "targeted_probe_include",
    "targeted_probe_strategy",
    "request_cap",
    "expected_behavior",
    "planned_request_count",
    "planned_output_root",
    "cninfo_call_planned",
    "pdf_download",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "dryrun_status",
    "notes",
]

DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_margin_trading_first_slice",
)
DEFAULT_MARGIN_TRADING_FIRST_SLICE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_margin_trading_first_slice_universe_draft.csv",
)
MARGIN_TRADING_FIRST_SLICE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_margin_trading_first_slice_dryrun_report.csv",
)
MARGIN_TRADING_FIRST_SLICE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_margin_trading_first_slice_dryrun_summary.md",
)

MARGIN_TRADING_FIRST_SLICE_RUNNER_GATE = "READY_FOR_APPROVAL"
MARGIN_TRADING_FIRST_SLICE_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
MARGIN_TRADING_FIRST_SLICE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
MARGIN_TRADING_FIRST_SLICE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
MARGIN_TRADING_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE = 5
MARGIN_TRADING_FIRST_SLICE_ALLOWED_CASE_IDS: Set[str] = {
    "DMT001",
    "DMT002",
    "DMT003",
    "DMT004",
    "DMT005",
}
MARGIN_TRADING_FIRST_SLICE_EXPECTED_COMPANY_CODES: Dict[str, str] = {
    "DMT001": "000895",
    "DMT002": "600000",
    "DMT003": "601988",
    "DMT004": "002415",
    "DMT005": "688981",
}
MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODES: Set[str] = {"688671", "301259"}
MARGIN_TRADING_FIRST_SLICE_COMPONENT = "margin_trading"
MARGIN_TRADING_FIRST_SLICE_ANCHOR_TDATE = "2026-07-08"
MARGIN_TRADING_FIRST_SLICE_ENDPOINT = (
    "https://www.cninfo.com.cn/data20/marginTrading/detailList"
)
MARGIN_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS = 4
MARGIN_TRADING_FIRST_SLICE_TOTAL_MAX_REQUESTS = 20

MARGIN_TRADING_FIRST_SLICE_APPROVAL_REQUIRED = (
    "approve_d_class_margin_trading_first_slice_required"
)
MARGIN_TRADING_FIRST_SLICE_WRONG_APPROVAL_FLAG = (
    "wrong_approval_flag_for_margin_trading_first_slice"
)
MARGIN_TRADING_FIRST_SLICE_MIXED_MODE_BLOCKED = (
    "margin_trading_first_slice_incompatible_with_other_modes"
)
MARGIN_TRADING_FIRST_SLICE_UNIVERSE_CSV_REQUIRED = (
    "margin_trading_first_slice_requires_explicit_universe_csv"
)
MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT_REQUIRED = (
    "margin_trading_first_slice_output_root_must_be_cninfo_d_class_margin_trading_first_slice"
)
MARGIN_TRADING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_margin_trading_first_slice"
)
MARGIN_TRADING_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_margin_trading_first_slice"
)
MARGIN_TRADING_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_output_root_write_blocked_for_margin_trading_first_slice"
)
MARGIN_TRADING_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "targeted_probe_output_root_write_blocked_for_margin_trading_first_slice"
)
MARGIN_TRADING_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH = (
    "margin_trading_first_slice_universe_size_must_equal_5"
)
MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_CASE_ID = (
    "forbidden_case_id_in_margin_trading_first_slice_universe"
)
MARGIN_TRADING_FIRST_SLICE_WRONG_COMPONENT = (
    "margin_trading_first_slice_component_must_be_margin_trading"
)
MARGIN_TRADING_FIRST_SLICE_INCLUDE_REQUIRED = (
    "first_slice_include_must_be_yes"
)
MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE = (
    "forbidden_company_code_in_margin_trading_first_slice_universe"
)
MARGIN_TRADING_FIRST_SLICE_WRONG_COMPANY_CODE = (
    "margin_trading_first_slice_company_code_mismatch"
)
MARGIN_TRADING_FIRST_SLICE_WRONG_ANCHOR_TDATE = (
    "margin_trading_first_slice_anchor_tdate_mismatch"
)
MARGIN_TRADING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED = (
    "margin_trading_first_slice_per_case_request_cap_exceeded"
)
MARGIN_TRADING_FIRST_SLICE_TOTAL_CAP_EXCEEDED = (
    "margin_trading_first_slice_total_request_cap_exceeded"
)
MARGIN_TRADING_FIRST_SLICE_LIVE_NOT_IMPLEMENTED = (
    "margin_trading_first_slice_live_not_implemented"
)

MARGIN_TRADING_FIRST_SLICE_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "anchor_tdate",
    "first_slice_include",
    "expected_behavior",
    "planned_request_count",
    "planned_output_root",
    "planned_endpoint",
    "cninfo_call_planned",
    "pdf_download",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "dryrun_status",
    "notes",
]

MARGIN_TRADING_FIRST_SLICE_LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "anchor_tdate",
    "expected_behavior",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "record_count",
    "empty_but_valid",
    "needs_review",
    "endpoint_used",
    "cninfo_request_count",
    "early_stop_triggered",
    "acceptable",
    "failure_type",
    "pdf_download",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "notes",
]

MARGIN_TRADING_FIRST_SLICE_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "component",
    "anchor_tdate",
    "expected_behavior",
    "retrieval_status",
    "record_count",
    "quality_status",
    "acceptable",
    "failure_type",
    "cninfo_request_count",
    "notes",
]

REPLACEMENT_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "expected_behavior",
    "replacement_for",
    "candidate_validation_status",
    "planned_request_count",
    "planned_output_root",
    "cninfo_call_planned",
    "pdf_download",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "dryrun_status",
    "notes",
]

REPLACEMENT_LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "expected_behavior",
    "replacement_for",
    "candidate_validation_status",
    "probe_budget",
    "cninfo_request_count",
    "retrieval_status",
    "record_count",
    "quality_status",
    "lineage_status",
    "acceptable",
    "failure_type",
    "endpoint_used",
    "pdf_download",
    "ocr",
    "extraction",
    "db_write",
    "minio_write",
    "rag_run",
    "notes",
]

REPLACEMENT_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "component",
    "expected_behavior",
    "replacement_for",
    "retrieval_status",
    "record_count",
    "quality_status",
    "acceptable",
    "failure_type",
    "cninfo_request_count",
    "notes",
]

DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "expected_behavior",
    "planned_endpoint",
    "planned_output",
    "cninfo_call_planned",
    "db_write",
    "minio_write",
    "rag_run",
    "dryrun_status",
    "notes",
]

LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "expected_behavior",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "record_count",
    "empty_but_valid",
    "needs_review",
    "endpoint_used",
    "cninfo_request_count",
    "db_write",
    "minio_write",
    "rag_run",
    "notes",
]

QUALITY_REPORT_COLUMNS = [
    "case_id",
    "component",
    "expected_behavior",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "acceptable",
    "notes",
]

V2_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "component",
    "company_code",
    "company_name",
    "probe_type",
    "probe_dimension",
    "planned_probe_value",
    "planned_endpoint",
    "request_index",
    "max_request_count",
    "early_stop_enabled",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

V2_COMPARISON_REPORT_COLUMNS = [
    "case_id",
    "component",
    "v1_retrieval_status",
    "v2_retrieval_status",
    "v1_cninfo_request_count",
    "v2_cninfo_request_count",
    "expectation_met_v1",
    "expectation_met_v2",
    "probe_extension_applied",
    "notes",
]

V2_LIVE_REPORT_COLUMNS = [
    "case_id",
    "component",
    "company_code",
    "company_name",
    "probe_type",
    "probe_dimension",
    "probe_value",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "record_count",
    "empty_but_valid",
    "needs_review",
    "endpoint_used",
    "request_index",
    "max_request_count",
    "early_stop_triggered",
    "cninfo_request_count",
    "db_write",
    "minio_write",
    "rag_run",
    "notes",
]

V2_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "component",
    "expected_behavior",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "record_count",
    "acceptable",
    "cninfo_request_count",
    "early_stop_triggered",
    "notes",
]


@dataclass
class ProbePlanEntry:
    case_id: str
    component: str
    company_code: str
    company_name: str
    probe_type: str
    probe_dimension: str
    planned_probe_value: str
    planned_endpoint: str
    request_index: int
    max_request_count: int
    early_stop_enabled: str
    cninfo_call_planned: str
    dryrun_status: str
    notes: str

    def to_row(self) -> Dict[str, str]:
        return {
            "case_id": self.case_id,
            "component": self.component,
            "company_code": self.company_code,
            "company_name": self.company_name,
            "probe_type": self.probe_type,
            "probe_dimension": self.probe_dimension,
            "planned_probe_value": self.planned_probe_value,
            "planned_endpoint": self.planned_endpoint,
            "request_index": str(self.request_index),
            "max_request_count": str(self.max_request_count),
            "early_stop_enabled": self.early_stop_enabled,
            "cninfo_call_planned": self.cninfo_call_planned,
            "dryrun_status": self.dryrun_status,
            "notes": self.notes,
        }


@dataclass
class ReplacementUniverseRow:
    case_id: str
    replaces_case_id: str
    replacement_for: str
    component: str
    company_code: str
    company_name: str
    expected_behavior: str
    candidate_source: str
    candidate_validation_status: str
    candidate_status: str
    include_in_future_validation: str
    notes: str


@dataclass
class TargetedProbeUniverseRow:
    targeted_probe_id: str
    replacement_case_id: str
    company_code: str
    company_name: str
    component: str
    anchor_date: str
    human_event_evidence_type: str
    human_event_evidence_description: str
    previous_replacement_live_status: str
    previous_record_count: str
    targeted_probe_include: str
    targeted_probe_strategy: str
    request_cap: str
    expected_behavior: str
    notes: str


@dataclass
class MarginTradingFirstSliceRow:
    case_id: str
    company_code: str
    company_name: str
    component: str
    market: str
    anchor_tdate: str
    first_slice_include: str
    expected_behavior: str
    reason: str
    dlc001_reference: str


@dataclass
class UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    component: str
    market: str
    risk_level: str
    expected_behavior: str
    reason: str


@dataclass
class LiveStats:
    cninfo_requests: int = 0
    db_writes: int = 0
    minio_writes: int = 0
    rag_runs: int = 0
    case_request_counts: Dict[str, int] = field(default_factory=dict)


def _normalize_output_root(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, OUTPUT_ROOT_VIOLATION


def validate_v2_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    v2_allowed = _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT)
    v1_root = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    if root == v1_root or root.startswith(v1_root + os.sep):
        return False, V1_OUTPUT_ROOT_WRITE_BLOCKED
    if root == v2_allowed or root.startswith(v2_allowed + os.sep):
        return True, ""
    return False, V2_OUTPUT_ROOT_REQUIRED


def load_replacement_universe(path: str) -> List[ReplacementUniverseRow]:
    rows: List[ReplacementUniverseRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                ReplacementUniverseRow(
                    case_id=str(row.get("case_id", "")).strip(),
                    replaces_case_id=str(row.get("replaces_case_id", "")).strip(),
                    replacement_for=str(row.get("replacement_for", "")).strip(),
                    component=str(row.get("component", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    expected_behavior=str(row.get("expected_behavior", "")).strip(),
                    candidate_source=str(row.get("candidate_source", "")).strip(),
                    candidate_validation_status=str(
                        row.get("candidate_validation_status", "")
                    ).strip(),
                    candidate_status=str(row.get("candidate_status", "")).strip(),
                    include_in_future_validation=str(
                        row.get("include_in_future_validation", "")
                    ).strip(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return rows


def validate_replacement_universe(rows: List[ReplacementUniverseRow]) -> List[str]:
    issues: List[str] = []
    if len(rows) != EXPECTED_UNIVERSE_SIZE:
        issues.append(f"{UNIVERSE_SIZE_MISMATCH}:got={len(rows)}")
    seen_ids: Set[str] = set()
    for row in rows:
        if row.case_id in REPLACEMENT_PLACEHOLDER_CASE_IDS:
            issues.append(f"{REPLACEMENT_PLACEHOLDER_ROW_REJECTED}:{row.case_id}")
        if row.case_id in REPLACEMENT_FORBIDDEN_ORIGINAL_CASE_IDS:
            issues.append(f"{REPLACEMENT_ORIGINAL_CASE_IN_UNIVERSE}:{row.case_id}")
        if row.case_id not in REPLACEMENT_ALLOWED_CASE_IDS:
            issues.append(f"{NON_DLC_CASE}:{row.case_id}")
        if row.case_id in seen_ids:
            issues.append(f"duplicate_case_id:{row.case_id}")
        seen_ids.add(row.case_id)
        if row.component not in ALLOWED_COMPONENTS:
            issues.append(f"{COMPONENT_NOT_ALLOWED}:{row.component}")
    if "DLC003R" not in seen_ids:
        issues.append("missing_case:DLC003R")
    if "DLC006R" not in seen_ids:
        issues.append("missing_case:DLC006R")
    for row in rows:
        if row.case_id == "DLC003R":
            if row.company_code != REPLACEMENT_DLC003R_COMPANY_CODE:
                issues.append(
                    f"{REPLACEMENT_WRONG_COMPANY_CODE}:DLC003R={row.company_code}"
                )
            if row.expected_behavior != "captured_normal":
                issues.append(f"expected_behavior_mismatch:DLC003R={row.expected_behavior}")
            if row.candidate_validation_status != REPLACEMENT_CANDIDATE_VALIDATED:
                issues.append(
                    f"{REPLACEMENT_INVALID_CANDIDATE_STATUS}:DLC003R="
                    f"{row.candidate_validation_status}"
                )
        if row.case_id == "DLC006R":
            if row.company_code != REPLACEMENT_DLC006R_COMPANY_CODE:
                issues.append(
                    f"{REPLACEMENT_WRONG_COMPANY_CODE}:DLC006R={row.company_code}"
                )
            if row.expected_behavior != "captured_normal":
                issues.append(f"expected_behavior_mismatch:DLC006R={row.expected_behavior}")
            if row.candidate_validation_status != REPLACEMENT_CANDIDATE_VALIDATED:
                issues.append(
                    f"{REPLACEMENT_INVALID_CANDIDATE_STATUS}:DLC006R="
                    f"{row.candidate_validation_status}"
                )
    return issues


def validate_replacement_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    replacement_allowed = _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT)
    v1_root = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v2_root = _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT)
    calibrated = _normalize_output_root(CALIBRATED_UNIVERSE_CSV)
    original = _normalize_output_root(DEFAULT_UNIVERSE_CSV)
    if root == v1_root or root.startswith(v1_root + os.sep):
        return False, REPLACEMENT_V1_OUTPUT_ROOT_WRITE_BLOCKED
    if root == v2_root or root.startswith(v2_root + os.sep):
        return False, REPLACEMENT_V2_OUTPUT_ROOT_WRITE_BLOCKED
    if root == calibrated or root.startswith(calibrated + os.sep):
        return False, REPLACEMENT_CALIBRATED_UNIVERSE_WRITE_BLOCKED
    if root == original or root.startswith(original + os.sep):
        return False, REPLACEMENT_ORIGINAL_UNIVERSE_WRITE_BLOCKED
    if root == replacement_allowed or root.startswith(replacement_allowed + os.sep):
        return True, ""
    return False, REPLACEMENT_OUTPUT_ROOT_REQUIRED


def enforce_replacement_write_block_targets(output_paths: Dict[str, str]) -> None:
    """确保输出路径不指向受保护的历史产物。"""
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(f"ERROR: {REPLACEMENT_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}", file=sys.stderr)
                sys.exit(2)


def parse_replacement_cases_filter(raw: str) -> Set[str]:
    return {part.strip() for part in raw.split(",") if part.strip()}


def validate_replacement_case_selection(selected: Set[str]) -> List[str]:
    issues: List[str] = []
    if not selected:
        issues.append("empty_case_selection")
    for case_id in selected:
        if case_id not in REPLACEMENT_PROBE_CASE_IDS:
            issues.append(f"{REPLACEMENT_PROBE_CASE_ONLY}:{case_id}")
    return issues


def enforce_replacement_forbidden_options(args: argparse.Namespace) -> None:
    enforce_forbidden_options(args)
    if args.known_event_replacement and args.bounded_probe_v2:
        print(f"ERROR: {REPLACEMENT_MIXED_MODE_BLOCKED}:bounded_probe_v2", file=sys.stderr)
        sys.exit(2)
    if args.known_event_replacement and args.approve_d_class_tiny_live_validation:
        print(
            f"ERROR: {REPLACEMENT_WRONG_APPROVAL_FLAG}:approve_d_class_tiny_live_validation",
            file=sys.stderr,
        )
        sys.exit(2)
    if args.known_event_replacement and args.approve_d_class_tiny_live_v2_bounded_probe:
        print(
            f"ERROR: {REPLACEMENT_WRONG_APPROVAL_FLAG}:approve_d_class_tiny_live_v2_bounded_probe",
            file=sys.stderr,
        )
        sys.exit(2)
    if not args.known_event_replacement and args.approve_d_class_known_event_replacement_validation:
        print(
            f"ERROR: {REPLACEMENT_WRONG_APPROVAL_FLAG}:replacement_flag_without_mode",
            file=sys.stderr,
        )
        sys.exit(2)
    for flag_name in ("pdf_download", "ocr", "extraction"):
        if getattr(args, flag_name, False):
            token = {
                "pdf_download": PDF_DOWNLOAD_BLOCKED,
                "ocr": OCR_BLOCKED,
                "extraction": EXTRACTION_BLOCKED,
            }[flag_name]
            print(f"ERROR: {token}", file=sys.stderr)
            sys.exit(2)


def enforce_replacement_live_approval_gate(args: argparse.Namespace) -> None:
    if args.mode == "live" and args.known_event_replacement:
        if not args.approve_d_class_known_event_replacement_validation:
            print(f"ERROR: {REPLACEMENT_APPROVAL_REQUIRED}", file=sys.stderr)
            sys.exit(2)


def build_replacement_dryrun_rows(
    rows: List[ReplacementUniverseRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    for row in rows:
        is_probe = row.case_id in REPLACEMENT_PROBE_CASE_IDS
        if is_probe:
            planned_requests = (
                REPLACEMENT_DLC003R_MAX_CAP
                if row.case_id == "DLC003R"
                else REPLACEMENT_DLC006R_MAX_CAP
            )
            cninfo_planned = "yes" if row.include_in_future_validation.lower() == "true" else "no"
            notes = (
                f"replacement probe planned; max_requests={planned_requests}; "
                "early stop on company-level hit"
            )
        else:
            planned_requests = 0
            cninfo_planned = "no"
            notes = "baseline reference only; no replacement validation CNINFO"
        dry_rows.append(
            {
                "case_id": row.case_id,
                "company_code": row.company_code,
                "company_name": row.company_name,
                "component": row.component,
                "expected_behavior": row.expected_behavior,
                "replacement_for": row.replacement_for or row.replaces_case_id,
                "candidate_validation_status": row.candidate_validation_status or "na",
                "planned_request_count": str(planned_requests),
                "planned_output_root": output_root,
                "cninfo_call_planned": cninfo_planned,
                "pdf_download": "no",
                "ocr": "no",
                "extraction": "no",
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
                "dryrun_status": "planned_ok",
                "notes": notes,
            }
        )
    return dry_rows


def write_replacement_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "d_class_known_event_replacement_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REPLACEMENT_DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_replacement_dryrun_summary(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    probe_rows = [r for r in rows if r["case_id"] in REPLACEMENT_PROBE_CASE_IDS]
    baseline_rows = [r for r in rows if r["case_id"] in REPLACEMENT_BASELINE_CASE_IDS]
    planned_ok = sum(1 for r in rows if r["dryrun_status"] == "planned_ok")
    lines = [
        "# CNINFO D 类 Known Event Replacement Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** known-event replacement dry-run only · **CNINFO calls = 0** · **NOT APPROVED**",
        "",
        "## Result",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| universe_csv | `{universe_csv}` |",
        f"| total_rows | {len(rows)} |",
        f"| planned_ok | {planned_ok}/{len(rows)} |",
        f"| replacement_probe_cases | {len(probe_rows)} |",
        f"| baseline_reference_cases | {len(baseline_rows)} |",
        "| CNINFO calls | **0** |",
        "| PDF / OCR / extraction | **0** |",
        "| DB / MinIO / RAG | **0** |",
        "",
        "## Gate",
        "",
        "```text",
        f"d_class_known_event_replacement_runner_extension_gate = {REPLACEMENT_RUNNER_GATE}",
        "approval_status = NOT_APPROVED",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"], "d_class_known_event_replacement_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def replacement_row_to_universe_case(row: ReplacementUniverseRow) -> UniverseCase:
    """将 replacement universe 行转为探测用 UniverseCase。"""
    return UniverseCase(
        case_id=row.case_id,
        company_code=row.company_code,
        company_name=row.company_name,
        component=row.component,
        market="",
        risk_level="",
        expected_behavior=row.expected_behavior,
        reason=row.notes,
    )


def build_replacement_probe_plan(
    case_id: str, max_requests: int
) -> List[Tuple[str, Dict[str, Any]]]:
    """复用既有 D-class bounded probe 策略。"""
    if case_id == "DLC003R":
        return build_bounded_probe_plan_dlc003(max_requests)
    if case_id == "DLC006R":
        return build_bounded_probe_plan_dlc006(max_requests)
    return []


def validate_replacement_request_caps(stats: LiveStats) -> List[str]:
    issues: List[str] = []
    dlc003r_used = stats.case_request_counts.get("DLC003R", 0)
    dlc006r_used = stats.case_request_counts.get("DLC006R", 0)
    if dlc003r_used > REPLACEMENT_DLC003R_MAX_CAP:
        issues.append(f"{REPLACEMENT_DLC003R_CAP_EXCEEDED}:{dlc003r_used}")
    if dlc006r_used > REPLACEMENT_DLC006R_MAX_CAP:
        issues.append(f"{REPLACEMENT_DLC006R_CAP_EXCEEDED}:{dlc006r_used}")
    if dlc003r_used + dlc006r_used > REPLACEMENT_TOTAL_MAX_CAP:
        issues.append(f"{REPLACEMENT_TOTAL_CAP_EXCEEDED}:{dlc003r_used + dlc006r_used}")
    return issues


def assess_replacement_probe_outcome(row: Dict[str, str]) -> Tuple[bool, str]:
    """replacement 探针结果评估；返回 (acceptable, failure_type)。"""
    rs = row.get("retrieval_status", "")
    qs = row.get("quality_status", "")
    notes = row.get("notes", "")
    try:
        rc = int(row.get("record_count", "0"))
    except ValueError:
        rc = 0

    if rs in ("http_error", "blocked") or qs == "blocked":
        if "network_error" in notes:
            return False, "network_error"
        if "invalid_json" in notes or rs == "http_error":
            return False, "schema_error"
        return False, "network_error"
    if rs == "found" and rc >= 1:
        return True, ""
    if qs == "needs_review" and rc >= 1:
        return True, ""
    if rs == "empty_but_valid" and rc == 0:
        return False, "empty_but_valid_after_budget"
    return False, "schema_error"


def is_replacement_case_acceptable(row: Dict[str, str]) -> bool:
    acceptable, _ = assess_replacement_probe_outcome(row)
    return acceptable


def compute_replacement_execution_gate(
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """replacement live 执行 gate；永不返回 PASS。"""
    outcomes = []
    for case_id in sorted(REPLACEMENT_PROBE_CASE_IDS):
        summary = case_summaries.get(case_id, {})
        acceptable, _ = assess_replacement_probe_outcome(summary)
        outcomes.append(acceptable)
    if all(outcomes):
        return REPLACEMENT_EXECUTION_GATE_PASS
    return REPLACEMENT_EXECUTION_GATE_FAIL


def build_replacement_baseline_reference_row(
    row: ReplacementUniverseRow,
) -> Dict[str, str]:
    return {
        "case_id": row.case_id,
        "company_code": row.company_code,
        "company_name": row.company_name,
        "component": row.component,
        "expected_behavior": row.expected_behavior,
        "replacement_for": row.replacement_for or row.replaces_case_id,
        "candidate_validation_status": row.candidate_validation_status or "na",
        "probe_budget": "0",
        "cninfo_request_count": "0",
        "retrieval_status": "reference_only",
        "record_count": "0",
        "quality_status": "na",
        "lineage_status": "na",
        "acceptable": "na",
        "failure_type": "",
        "endpoint_used": "",
        "pdf_download": "no",
        "ocr": "no",
        "extraction": "no",
        "db_write": "no",
        "minio_write": "no",
        "rag_run": "no",
        "notes": "baseline reference only; no replacement validation CNINFO",
    }


def build_replacement_probe_live_row(
    repl_row: ReplacementUniverseRow,
    summary: Dict[str, str],
    probe_budget: int,
) -> Dict[str, str]:
    acceptable, failure_type = assess_replacement_probe_outcome(summary)
    return {
        "case_id": repl_row.case_id,
        "company_code": repl_row.company_code,
        "company_name": repl_row.company_name,
        "component": repl_row.component,
        "expected_behavior": repl_row.expected_behavior,
        "replacement_for": repl_row.replacement_for or repl_row.replaces_case_id,
        "candidate_validation_status": repl_row.candidate_validation_status,
        "probe_budget": str(probe_budget),
        "cninfo_request_count": summary.get("cninfo_request_count", "0"),
        "retrieval_status": summary.get("retrieval_status", ""),
        "record_count": summary.get("record_count", "0"),
        "quality_status": summary.get("quality_status", ""),
        "lineage_status": summary.get("lineage_status", ""),
        "acceptable": "yes" if acceptable else "no",
        "failure_type": failure_type,
        "endpoint_used": summary.get("endpoint_used", ""),
        "pdf_download": "no",
        "ocr": "no",
        "extraction": "no",
        "db_write": "no",
        "minio_write": "no",
        "rag_run": "no",
        "notes": summary.get("notes", ""),
    }


def write_replacement_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "d_class_known_event_replacement_live_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REPLACEMENT_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_replacement_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    quality_rows = [
        {
            "case_id": row["case_id"],
            "component": row["component"],
            "expected_behavior": row["expected_behavior"],
            "replacement_for": row["replacement_for"],
            "retrieval_status": row["retrieval_status"],
            "record_count": row["record_count"],
            "quality_status": row["quality_status"],
            "acceptable": row["acceptable"],
            "failure_type": row["failure_type"],
            "cninfo_request_count": row["cninfo_request_count"],
            "notes": row["notes"],
        }
        for row in rows
        if row["case_id"] in REPLACEMENT_PROBE_CASE_IDS
    ]
    path = os.path.join(
        output_paths["reports"], "d_class_known_event_replacement_quality_report.csv"
    )
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REPLACEMENT_QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(quality_rows)
    return path


def write_replacement_live_summary(
    live_rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    probe_rows = [r for r in live_rows if r["case_id"] in REPLACEMENT_PROBE_CASE_IDS]
    lines = [
        "# CNINFO D 类 Known Event Replacement Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** known-event replacement live · **无 DB/MinIO/RAG/PDF/OCR** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| DLC003R CNINFO requests | **{stats.case_request_counts.get('DLC003R', 0)}** |",
        f"| DLC006R CNINFO requests | **{stats.case_request_counts.get('DLC006R', 0)}** |",
        f"| Total CNINFO requests | **{stats.cninfo_requests}** |",
        f"| DB writes | **{stats.db_writes}** |",
        f"| MinIO writes | **{stats.minio_writes}** |",
        f"| RAG runs | **{stats.rag_runs}** |",
        "",
        "## Probe Results",
        "",
        "| case_id | retrieval | records | requests | acceptable | failure_type |",
        "|---------|-----------|---------|----------|------------|--------------|",
    ]
    for row in probe_rows:
        lines.append(
            f"| {row['case_id']} | {row['retrieval_status']} | {row['record_count']} | "
            f"{row['cninfo_request_count']} | {row['acceptable']} | {row['failure_type']} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "```text",
            f"d_class_known_event_replacement_validation_execution_gate = {gate}",
            "approval_status = NOT_APPROVED",
            "```",
            "",
            "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
            "",
        ]
    )
    summary_path = os.path.join(
        output_paths["reports"], "d_class_known_event_replacement_live_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_known_event_replacement_live(
    args: argparse.Namespace,
    universe_rows: List[ReplacementUniverseRow],
    selected: Set[str],
    output_paths: Dict[str, str],
) -> int:
    """known-event replacement live 探针；仅 DLC003R/DLC006R 调用 CNINFO。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    probe_row_map = {r.case_id: r for r in universe_rows if r.case_id in REPLACEMENT_PROBE_CASE_IDS}

    probe_specs = [
        ("DLC003R", "tdate", REPLACEMENT_DLC003R_MAX_CAP),
        ("DLC006R", "mode_date", REPLACEMENT_DLC006R_MAX_CAP),
    ]

    for case_id, _, max_cap in probe_specs:
        if case_id not in selected:
            continue
        plan = build_replacement_probe_plan(case_id, max_cap)
        if len(plan) > max_cap:
            print(f"ERROR: {REPLACEMENT_DLC003R_CAP_EXCEEDED if case_id == 'DLC003R' else REPLACEMENT_DLC006R_CAP_EXCEEDED}:planned={len(plan)}", file=sys.stderr)
            return 2

    session = requests.Session()
    stats = LiveStats()
    case_summaries: Dict[str, Dict[str, str]] = {}
    early_stop_count = 0

    for case_id, probe_type, max_cap in probe_specs:
        if case_id not in selected:
            continue
        repl_row = probe_row_map[case_id]
        case = replacement_row_to_universe_case(repl_row)
        plan = build_replacement_probe_plan(case_id, max_cap)
        source_cfg = source_configs.get(case.component, {})
        endpoint = endpoints.get(case.component, source_cfg.get("api_url", ""))
        _, summary, stopped = execute_v2_bounded_probe_case(
            case,
            plan,
            probe_type,
            max_cap,
            source_cfg,
            endpoint,
            session,
            stats,
            output_paths,
        )
        case_summaries[case_id] = summary
        if stopped:
            early_stop_count += 1
        print(
            f"{case_id} {summary['retrieval_status']}: records={summary['record_count']} "
            f"requests={summary['cninfo_request_count']} early_stop={summary['early_stop_triggered']}",
            flush=True,
        )

    cap_issues = validate_replacement_request_caps(stats)
    if cap_issues:
        print(f"ERROR: replacement request cap validation failed: {cap_issues}", file=sys.stderr)
        return 2

    gate = compute_replacement_execution_gate(case_summaries)
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = REPLACEMENT_EXECUTION_GATE_FAIL

    live_rows: List[Dict[str, str]] = []
    for row in universe_rows:
        if row.case_id in REPLACEMENT_BASELINE_CASE_IDS:
            live_rows.append(build_replacement_baseline_reference_row(row))
        elif row.case_id in REPLACEMENT_PROBE_CASE_IDS and row.case_id in case_summaries:
            max_cap = (
                REPLACEMENT_DLC003R_MAX_CAP
                if row.case_id == "DLC003R"
                else REPLACEMENT_DLC006R_MAX_CAP
            )
            live_rows.append(
                build_replacement_probe_live_row(
                    row, case_summaries[row.case_id], max_cap
                )
            )

    report_path = write_replacement_live_report(live_rows, output_paths)
    quality_path = write_replacement_quality_report(live_rows, output_paths)
    summary_path = write_replacement_live_summary(live_rows, stats, gate, output_paths)

    print(
        f"mode=known_event_replacement_live dlc003r_requests="
        f"{stats.case_request_counts.get('DLC003R', 0)} "
        f"dlc006r_requests={stats.case_request_counts.get('DLC006R', 0)} "
        f"total_requests={stats.cninfo_requests} early_stop_count={early_stop_count}"
    )
    print(f"gate=d_class_known_event_replacement_validation_execution_gate={gate}")
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == REPLACEMENT_EXECUTION_GATE_PASS else 1


def run_known_event_replacement(args: argparse.Namespace) -> int:
    enforce_replacement_forbidden_options(args)
    enforce_replacement_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(f"ERROR: {REPLACEMENT_UNIVERSE_CSV_REQUIRED}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_replacement_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_replacement_universe(args.universe_csv)
    universe_issues = validate_replacement_universe(universe_rows)
    if universe_issues:
        print(f"ERROR: replacement universe validation failed: {universe_issues}", file=sys.stderr)
        return 2

    selected = parse_replacement_cases_filter(args.cases)
    selection_issues = validate_replacement_case_selection(selected)
    if selection_issues:
        print(f"ERROR: replacement case selection failed: {selection_issues}", file=sys.stderr)
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_replacement_write_block_targets(output_paths)

    if args.mode != "live":
        dry_rows = build_replacement_dryrun_rows(universe_rows, output_root)
        report_path = write_replacement_dryrun_report(dry_rows, output_paths)
        summary_path = write_replacement_dryrun_summary(
            dry_rows, output_paths, args.universe_csv
        )
        probe_planned = sum(
            int(r["planned_request_count"])
            for r in dry_rows
            if r["case_id"] in REPLACEMENT_PROBE_CASE_IDS
        )
        print(
            f"mode=known_event_replacement_dry_run cases={len(dry_rows)} "
            f"probe_planned_requests={probe_planned} cninfo_calls=0"
        )
        print(
            f"gate=d_class_known_event_replacement_runner_extension_gate={REPLACEMENT_RUNNER_GATE}"
        )
        print(f"dryrun_report={report_path}")
        print(f"dryrun_summary={summary_path}")
        return 0

    return execute_known_event_replacement_live(
        args, universe_rows, selected, output_paths
    )


def load_targeted_probe_universe(path: str) -> List[TargetedProbeUniverseRow]:
    rows: List[TargetedProbeUniverseRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                TargetedProbeUniverseRow(
                    targeted_probe_id=str(row.get("targeted_probe_id", "")).strip(),
                    replacement_case_id=str(row.get("replacement_case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    component=str(row.get("component", "")).strip(),
                    anchor_date=str(row.get("anchor_date", "")).strip(),
                    human_event_evidence_type=str(
                        row.get("human_event_evidence_type", "")
                    ).strip(),
                    human_event_evidence_description=str(
                        row.get("human_event_evidence_description", "")
                    ).strip(),
                    previous_replacement_live_status=str(
                        row.get("previous_replacement_live_status", "")
                    ).strip(),
                    previous_record_count=str(
                        row.get("previous_record_count", "")
                    ).strip(),
                    targeted_probe_include=str(
                        row.get("targeted_probe_include", "")
                    ).strip(),
                    targeted_probe_strategy=str(
                        row.get("targeted_probe_strategy", "")
                    ).strip(),
                    request_cap=str(row.get("request_cap", "")).strip(),
                    expected_behavior=str(row.get("expected_behavior", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return rows


def _targeted_probe_row_cap(row: TargetedProbeUniverseRow) -> int:
    try:
        return int(row.request_cap)
    except ValueError:
        return -1


def validate_targeted_probe_universe(rows: List[TargetedProbeUniverseRow]) -> List[str]:
    issues: List[str] = []
    if len(rows) != TARGETED_PROBE_EXPECTED_UNIVERSE_SIZE:
        issues.append(f"{TARGETED_PROBE_UNIVERSE_SIZE_MISMATCH}:got={len(rows)}")
    seen_ids: Set[str] = set()
    total_cap = 0
    for row in rows:
        probe_id = row.targeted_probe_id
        repl_id = row.replacement_case_id
        if probe_id in TARGETED_PROBE_FORBIDDEN_ORIGINAL_IDS:
            issues.append(f"{TARGETED_PROBE_ORIGINAL_CASE_IN_UNIVERSE}:{probe_id}")
        if repl_id in TARGETED_PROBE_FORBIDDEN_ORIGINAL_IDS:
            issues.append(f"{TARGETED_PROBE_ORIGINAL_CASE_IN_UNIVERSE}:{repl_id}")
        if probe_id in TARGETED_PROBE_FORBIDDEN_BASELINE_IDS:
            issues.append(f"{TARGETED_PROBE_BASELINE_CASE_IN_UNIVERSE}:{probe_id}")
        if repl_id in TARGETED_PROBE_FORBIDDEN_BASELINE_IDS:
            issues.append(f"{TARGETED_PROBE_BASELINE_CASE_IN_UNIVERSE}:{repl_id}")
        if probe_id not in TARGETED_PROBE_ALLOWED_IDS:
            issues.append(f"{TARGETED_PROBE_FORBIDDEN_CASE_ID}:{probe_id}")
        if repl_id not in TARGETED_PROBE_REPLACEMENT_IDS:
            issues.append(f"{TARGETED_PROBE_FORBIDDEN_CASE_ID}:replacement={repl_id}")
        if probe_id in seen_ids:
            issues.append(f"duplicate_targeted_probe_id:{probe_id}")
        seen_ids.add(probe_id)
        if row.targeted_probe_include.lower() != "yes":
            issues.append(f"{TARGETED_PROBE_INCLUDE_REQUIRED}:{probe_id}")
        if row.component not in ALLOWED_COMPONENTS:
            issues.append(f"{COMPONENT_NOT_ALLOWED}:{row.component}")
        row_cap = _targeted_probe_row_cap(row)
        if row_cap < 0:
            issues.append(f"invalid_request_cap:{probe_id}")
        elif row_cap > TARGETED_PROBE_PER_ROW_MAX_CAP:
            issues.append(f"{TARGETED_PROBE_ROW_CAP_EXCEEDED}:{probe_id}={row_cap}")
        else:
            total_cap += row_cap
        if probe_id == "DLC003R-T01":
            if row.replacement_case_id != "DLC003R":
                issues.append(f"replacement_mismatch:{probe_id}={row.replacement_case_id}")
            if row.company_code != TARGETED_PROBE_DLC003R_T01_COMPANY_CODE:
                issues.append(
                    f"{TARGETED_PROBE_WRONG_COMPANY_CODE}:DLC003R-T01={row.company_code}"
                )
            if row.component != TARGETED_PROBE_DLC003R_T01_COMPONENT:
                issues.append(
                    f"{TARGETED_PROBE_WRONG_COMPONENT}:DLC003R-T01={row.component}"
                )
            if row.anchor_date != TARGETED_PROBE_DLC003R_T01_ANCHOR_DATE:
                issues.append(
                    f"{TARGETED_PROBE_WRONG_ANCHOR_DATE}:DLC003R-T01={row.anchor_date}"
                )
        if probe_id == "DLC006R-T01":
            if row.replacement_case_id != "DLC006R":
                issues.append(f"replacement_mismatch:{probe_id}={row.replacement_case_id}")
            if row.company_code != TARGETED_PROBE_DLC006R_T01_COMPANY_CODE:
                issues.append(
                    f"{TARGETED_PROBE_WRONG_COMPANY_CODE}:DLC006R-T01={row.company_code}"
                )
            if row.component != TARGETED_PROBE_DLC006R_T01_COMPONENT:
                issues.append(
                    f"{TARGETED_PROBE_WRONG_COMPONENT}:DLC006R-T01={row.component}"
                )
            if row.anchor_date != TARGETED_PROBE_DLC006R_T01_ANCHOR_DATE:
                issues.append(
                    f"{TARGETED_PROBE_WRONG_ANCHOR_DATE}:DLC006R-T01={row.anchor_date}"
                )
    if "DLC003R-T01" not in seen_ids:
        issues.append("missing_targeted_probe:DLC003R-T01")
    if "DLC006R-T01" not in seen_ids:
        issues.append("missing_targeted_probe:DLC006R-T01")
    if total_cap > TARGETED_PROBE_TOTAL_MAX_CAP:
        issues.append(f"{TARGETED_PROBE_TOTAL_CAP_EXCEEDED}:{total_cap}")
    return issues


def validate_targeted_probe_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    targeted_allowed = _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT)
    v1_root = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v2_root = _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT)
    replacement_root = _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT)
    calibrated = _normalize_output_root(CALIBRATED_UNIVERSE_CSV)
    original = _normalize_output_root(DEFAULT_UNIVERSE_CSV)
    if root == v1_root or root.startswith(v1_root + os.sep):
        return False, TARGETED_PROBE_V1_OUTPUT_ROOT_WRITE_BLOCKED
    if root == v2_root or root.startswith(v2_root + os.sep):
        return False, TARGETED_PROBE_V2_OUTPUT_ROOT_WRITE_BLOCKED
    if root == replacement_root or root.startswith(replacement_root + os.sep):
        return False, TARGETED_PROBE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED
    if root == calibrated or root.startswith(calibrated + os.sep):
        return False, TARGETED_PROBE_CALIBRATED_UNIVERSE_WRITE_BLOCKED
    if root == original or root.startswith(original + os.sep):
        return False, TARGETED_PROBE_ORIGINAL_UNIVERSE_WRITE_BLOCKED
    if root == targeted_allowed or root.startswith(targeted_allowed + os.sep):
        return True, ""
    return False, TARGETED_PROBE_OUTPUT_ROOT_REQUIRED


def enforce_targeted_probe_write_block_targets(output_paths: Dict[str, str]) -> None:
    """确保 targeted probe 输出路径不指向受保护的历史产物。"""
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {TARGETED_PROBE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_targeted_probe_forbidden_options(args: argparse.Namespace) -> None:
    enforce_forbidden_options(args)
    if args.known_event_targeted_probe and args.known_event_replacement:
        print(
            f"ERROR: {TARGETED_PROBE_MIXED_MODE_BLOCKED}:known_event_replacement",
            file=sys.stderr,
        )
        sys.exit(2)
    if args.known_event_targeted_probe and args.bounded_probe_v2:
        print(
            f"ERROR: {TARGETED_PROBE_MIXED_MODE_BLOCKED}:bounded_probe_v2",
            file=sys.stderr,
        )
        sys.exit(2)
    wrong_flags = [
        ("approve_d_class_tiny_live_validation", args.approve_d_class_tiny_live_validation),
        (
            "approve_d_class_tiny_live_v2_bounded_probe",
            args.approve_d_class_tiny_live_v2_bounded_probe,
        ),
        (
            "approve_d_class_known_event_replacement_validation",
            args.approve_d_class_known_event_replacement_validation,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.known_event_targeted_probe and enabled:
            print(f"ERROR: {TARGETED_PROBE_WRONG_APPROVAL_FLAG}:{name}", file=sys.stderr)
            sys.exit(2)
    if (
        not args.known_event_targeted_probe
        and args.approve_d_class_known_event_targeted_probe
    ):
        print(
            f"ERROR: {TARGETED_PROBE_WRONG_APPROVAL_FLAG}:targeted_probe_flag_without_mode",
            file=sys.stderr,
        )
        sys.exit(2)
    for flag_name in ("pdf_download", "ocr", "extraction"):
        if getattr(args, flag_name, False):
            token = {
                "pdf_download": PDF_DOWNLOAD_BLOCKED,
                "ocr": OCR_BLOCKED,
                "extraction": EXTRACTION_BLOCKED,
            }[flag_name]
            print(f"ERROR: {token}", file=sys.stderr)
            sys.exit(2)


def enforce_targeted_probe_live_approval_gate(args: argparse.Namespace) -> None:
    if args.mode == "live" and args.known_event_targeted_probe:
        if not args.approve_d_class_known_event_targeted_probe:
            print(f"ERROR: {TARGETED_PROBE_APPROVAL_REQUIRED}", file=sys.stderr)
            sys.exit(2)


def build_targeted_probe_plan_dlc003r(
    anchor_date: str, max_requests: int
) -> List[Tuple[str, Dict[str, Any]]]:
    """以 anchor_date 为中心的 liftBan/tdate 探针计划。"""
    anchor = date.fromisoformat(anchor_date)
    base = dict(
        load_table_source_configs()
        .get("restricted_shares_unlock", {})
        .get("params_template") or {}
    )
    items: List[Tuple[str, Dict[str, Any]]] = []
    items.append(("anchor_exact", {**base, "tdate": anchor_date}))
    for offset in range(-7, 8):
        if offset == 0:
            continue
        tdate = (anchor + timedelta(days=offset)).strftime("%Y-%m-%d")
        items.append(("anchor_pm7d", {**base, "tdate": tdate}))
    for offset in (-30, 30):
        tdate = (anchor + timedelta(days=offset)).strftime("%Y-%m-%d")
        items.append(("anchor_pm30d", {**base, "tdate": tdate}))
    prev_month = anchor.replace(day=1) - timedelta(days=1)
    month_candidates = [
        (anchor.year, anchor.month),
        (prev_month.year, prev_month.month),
    ]
    if anchor.month == 12:
        month_candidates.append((anchor.year + 1, 1))
    else:
        month_candidates.append((anchor.year, anchor.month + 1))
    for year, month in month_candidates:
        items.append(
            ("month_end_nearby", {**base, "tdate": _month_end_date(year, month)})
        )
    deduped = _dedupe_param_list(items)
    return deduped[:max_requests]


def build_targeted_probe_plan_dlc006r(
    anchor_date: str, max_requests: int
) -> List[Tuple[str, Dict[str, Any]]]:
    """以 anchor_date 为中心的 shareholeder/type+tdate 探针计划。"""
    anchor = date.fromisoformat(anchor_date)
    items: List[Tuple[str, Dict[str, Any]]] = []
    for offset in range(-7, 8):
        tdate = (anchor + timedelta(days=offset)).strftime("%Y-%m-%d")
        items.append(("anchor_pm7d_inc", {"type": "inc", "tdate": tdate}))
        items.append(("anchor_pm7d_desc", {"type": "desc", "tdate": tdate}))
    deduped = _dedupe_param_list(items)
    return deduped[:max_requests]


def compute_targeted_probe_planned_requests(row: TargetedProbeUniverseRow) -> int:
    row_cap = _targeted_probe_row_cap(row)
    if row_cap < 0:
        return 0
    if row.targeted_probe_id == "DLC003R-T01":
        plan = build_targeted_probe_plan_dlc003r(row.anchor_date, row_cap)
    elif row.targeted_probe_id == "DLC006R-T01":
        plan = build_targeted_probe_plan_dlc006r(row.anchor_date, row_cap)
    else:
        return 0
    return min(len(plan), row_cap)


def build_targeted_probe_dryrun_rows(
    rows: List[TargetedProbeUniverseRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    for row in rows:
        planned_requests = compute_targeted_probe_planned_requests(row)
        cninfo_planned = (
            "yes" if row.targeted_probe_include.lower() == "yes" else "no"
        )
        dry_rows.append(
            {
                "targeted_probe_id": row.targeted_probe_id,
                "replacement_case_id": row.replacement_case_id,
                "company_code": row.company_code,
                "company_name": row.company_name,
                "component": row.component,
                "anchor_date": row.anchor_date,
                "human_event_evidence_type": row.human_event_evidence_type,
                "human_event_evidence_description": row.human_event_evidence_description,
                "previous_replacement_live_status": row.previous_replacement_live_status,
                "previous_record_count": row.previous_record_count,
                "targeted_probe_include": row.targeted_probe_include,
                "targeted_probe_strategy": row.targeted_probe_strategy,
                "request_cap": row.request_cap,
                "expected_behavior": row.expected_behavior,
                "planned_request_count": str(planned_requests),
                "planned_output_root": output_root,
                "cninfo_call_planned": cninfo_planned,
                "pdf_download": "no",
                "ocr": "no",
                "extraction": "no",
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
                "dryrun_status": "planned_ok",
                "notes": (
                    f"anchor={row.anchor_date}; strategy={row.targeted_probe_strategy}; "
                    f"max_requests={row.request_cap}; early stop on company-level hit"
                ),
            }
        )
    return dry_rows


def write_targeted_probe_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_known_event_targeted_probe_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TARGETED_PROBE_DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_targeted_probe_dryrun_summary(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    planned_ok = sum(1 for r in rows if r["dryrun_status"] == "planned_ok")
    planned_total = sum(int(r["planned_request_count"]) for r in rows)
    lines = [
        "# CNINFO D 类 Known Event Targeted Probe Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** known-event targeted probe dry-run only · **CNINFO calls = 0** · **NOT APPROVED**",
        "",
        "## Result",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| universe_csv | `{universe_csv}` |",
        f"| total_rows | {len(rows)} |",
        f"| planned_ok | {planned_ok}/{len(rows)} |",
        f"| planned_request_count_total | {planned_total} |",
        "| CNINFO calls | **0** |",
        "| PDF / OCR / extraction | **0** |",
        "| DB / MinIO / RAG | **0** |",
        "",
        "## Gate",
        "",
        "```text",
        f"d_class_known_event_targeted_probe_runner_extension_gate = {TARGETED_PROBE_RUNNER_GATE}",
        "approval_status = NOT_APPROVED",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_known_event_targeted_probe_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def run_known_event_targeted_probe(args: argparse.Namespace) -> int:
    enforce_targeted_probe_forbidden_options(args)
    enforce_targeted_probe_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(f"ERROR: {TARGETED_PROBE_UNIVERSE_CSV_REQUIRED}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_targeted_probe_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_targeted_probe_universe(args.universe_csv)
    universe_issues = validate_targeted_probe_universe(universe_rows)
    if universe_issues:
        print(
            f"ERROR: targeted probe universe validation failed: {universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_targeted_probe_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_known_event_targeted_probe_live(universe_rows, output_paths)

    dry_rows = build_targeted_probe_dryrun_rows(universe_rows, output_root)
    report_path = write_targeted_probe_dryrun_report(dry_rows, output_paths)
    summary_path = write_targeted_probe_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    print(
        f"mode=known_event_targeted_probe_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={planned_total} cninfo_calls=0"
    )
    print(
        f"gate=d_class_known_event_targeted_probe_runner_extension_gate="
        f"{TARGETED_PROBE_RUNNER_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0


def load_margin_trading_first_slice_universe(
    path: str,
) -> List[MarginTradingFirstSliceRow]:
    rows: List[MarginTradingFirstSliceRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                MarginTradingFirstSliceRow(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    component=str(row.get("component", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    anchor_tdate=str(row.get("anchor_tdate", "")).strip(),
                    first_slice_include=str(
                        row.get("first_slice_include", "")
                    ).strip(),
                    expected_behavior=str(
                        row.get("expected_behavior", "")
                    ).strip(),
                    reason=str(row.get("reason", "")).strip(),
                    dlc001_reference=str(row.get("dlc001_reference", "")).strip(),
                )
            )
    return rows


def build_margin_trading_first_slice_plan(
    anchor_tdate: str, max_requests: int = MARGIN_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS
) -> List[str]:
    """margin_trading 第一切片 dry-run 请求计划（仅计数，不执行）。"""
    anchor = date.fromisoformat(anchor_tdate)
    steps = ["detailList_primary"]
    for offset in (-1, 1):
        probe_date = (anchor + timedelta(days=offset)).strftime("%Y-%m-%d")
        steps.append(f"optional_tdate_probe_{probe_date}")
    while len(steps) < max_requests:
        steps.append("budget_reserve")
    return steps[:max_requests]


def compute_margin_trading_first_slice_planned_requests(
    row: MarginTradingFirstSliceRow,
) -> int:
    plan = build_margin_trading_first_slice_plan(row.anchor_tdate)
    return len(plan)


def validate_margin_trading_first_slice_universe(
    rows: List[MarginTradingFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    if len(rows) != MARGIN_TRADING_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE:
        issues.append(
            f"{MARGIN_TRADING_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH}:got={len(rows)}"
        )
    seen_ids: Set[str] = set()
    total_planned = 0
    for row in rows:
        case_id = row.case_id
        if case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_ids.add(case_id)
        if case_id not in MARGIN_TRADING_FIRST_SLICE_ALLOWED_CASE_IDS:
            issues.append(f"{MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_CASE_ID}:{case_id}")
        if row.company_code in MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODES:
            issues.append(
                f"{MARGIN_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE}:{row.company_code}"
            )
        expected_code = MARGIN_TRADING_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(case_id)
        if expected_code and row.company_code != expected_code:
            issues.append(
                f"{MARGIN_TRADING_FIRST_SLICE_WRONG_COMPANY_CODE}:{case_id}={row.company_code}"
            )
        if row.component != MARGIN_TRADING_FIRST_SLICE_COMPONENT:
            issues.append(f"{MARGIN_TRADING_FIRST_SLICE_WRONG_COMPONENT}:{case_id}")
        if row.first_slice_include.lower() != "yes":
            issues.append(f"{MARGIN_TRADING_FIRST_SLICE_INCLUDE_REQUIRED}:{case_id}")
        if row.anchor_tdate != MARGIN_TRADING_FIRST_SLICE_ANCHOR_TDATE:
            issues.append(
                f"{MARGIN_TRADING_FIRST_SLICE_WRONG_ANCHOR_TDATE}:{case_id}={row.anchor_tdate}"
            )
        planned = compute_margin_trading_first_slice_planned_requests(row)
        if planned > MARGIN_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{MARGIN_TRADING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:{case_id}={planned}"
            )
        total_planned += planned
    for required_id in sorted(MARGIN_TRADING_FIRST_SLICE_ALLOWED_CASE_IDS):
        if required_id not in seen_ids:
            issues.append(f"missing_case_id:{required_id}")
    if total_planned > MARGIN_TRADING_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{MARGIN_TRADING_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{total_planned}"
        )
    return issues


def validate_margin_trading_first_slice_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT)
    v1_root = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v2_root = _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT)
    replacement_root = _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT)
    targeted_root = _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT)
    if root == v1_root or root.startswith(v1_root + os.sep):
        return False, MARGIN_TRADING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED
    if root == v2_root or root.startswith(v2_root + os.sep):
        return False, MARGIN_TRADING_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED
    if root == replacement_root or root.startswith(replacement_root + os.sep):
        return False, MARGIN_TRADING_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED
    if root == targeted_root or root.startswith(targeted_root + os.sep):
        return False, MARGIN_TRADING_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT_REQUIRED


def enforce_margin_trading_first_slice_write_block_targets(
    output_paths: Dict[str, str],
) -> None:
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {MARGIN_TRADING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_margin_trading_first_slice_forbidden_options(
    args: argparse.Namespace,
) -> None:
    enforce_forbidden_options(args)
    mixed_modes = [
        ("known_event_replacement", args.known_event_replacement),
        ("known_event_targeted_probe", args.known_event_targeted_probe),
        ("bounded_probe_v2", args.bounded_probe_v2),
    ]
    for name, enabled in mixed_modes:
        if args.margin_trading_first_slice and enabled:
            print(
                f"ERROR: {MARGIN_TRADING_FIRST_SLICE_MIXED_MODE_BLOCKED}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    wrong_flags = [
        ("approve_d_class_tiny_live_validation", args.approve_d_class_tiny_live_validation),
        (
            "approve_d_class_tiny_live_v2_bounded_probe",
            args.approve_d_class_tiny_live_v2_bounded_probe,
        ),
        (
            "approve_d_class_known_event_replacement_validation",
            args.approve_d_class_known_event_replacement_validation,
        ),
        (
            "approve_d_class_known_event_targeted_probe",
            args.approve_d_class_known_event_targeted_probe,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.margin_trading_first_slice and enabled:
            print(
                f"ERROR: {MARGIN_TRADING_FIRST_SLICE_WRONG_APPROVAL_FLAG}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    if (
        not args.margin_trading_first_slice
        and args.approve_d_class_margin_trading_first_slice
    ):
        print(
            f"ERROR: {MARGIN_TRADING_FIRST_SLICE_WRONG_APPROVAL_FLAG}:"
            "margin_trading_first_slice_flag_without_mode",
            file=sys.stderr,
        )
        sys.exit(2)
    for flag_name in ("pdf_download", "ocr", "extraction"):
        if getattr(args, flag_name, False):
            token = {
                "pdf_download": PDF_DOWNLOAD_BLOCKED,
                "ocr": OCR_BLOCKED,
                "extraction": EXTRACTION_BLOCKED,
            }[flag_name]
            print(f"ERROR: {token}", file=sys.stderr)
            sys.exit(2)


def enforce_margin_trading_first_slice_live_approval_gate(
    args: argparse.Namespace,
) -> None:
    if args.mode == "live" and args.margin_trading_first_slice:
        if not args.approve_d_class_margin_trading_first_slice:
            print(
                f"ERROR: {MARGIN_TRADING_FIRST_SLICE_APPROVAL_REQUIRED}",
                file=sys.stderr,
            )
            sys.exit(2)


def build_margin_trading_first_slice_dryrun_rows(
    rows: List[MarginTradingFirstSliceRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    for row in rows:
        planned_requests = compute_margin_trading_first_slice_planned_requests(row)
        plan = build_margin_trading_first_slice_plan(row.anchor_tdate)
        dry_rows.append(
            {
                "case_id": row.case_id,
                "company_code": row.company_code,
                "company_name": row.company_name,
                "component": row.component,
                "market": row.market,
                "anchor_tdate": row.anchor_tdate,
                "first_slice_include": row.first_slice_include,
                "expected_behavior": row.expected_behavior,
                "planned_request_count": str(planned_requests),
                "planned_output_root": output_root,
                "planned_endpoint": MARGIN_TRADING_FIRST_SLICE_ENDPOINT,
                "cninfo_call_planned": (
                    "yes" if row.first_slice_include.lower() == "yes" else "no"
                ),
                "pdf_download": "no",
                "ocr": "no",
                "extraction": "no",
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
                "dryrun_status": "planned_ok",
                "notes": (
                    f"anchor={row.anchor_tdate}; plan={','.join(plan)}; "
                    f"max_per_case={MARGIN_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS}"
                ),
            }
        )
    return dry_rows


def write_margin_trading_first_slice_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_margin_trading_first_slice_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=MARGIN_TRADING_FIRST_SLICE_DRYRUN_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_margin_trading_first_slice_dryrun_summary(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    planned_ok = sum(1 for r in rows if r["dryrun_status"] == "planned_ok")
    planned_total = sum(int(r["planned_request_count"]) for r in rows)
    lines = [
        "# CNINFO D 类 margin_trading First-Slice Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** margin_trading first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED**",
        "",
        "## Result",
        "",
        f"| 项 | 值 |",
        f"|----|-----|",
        f"| cases | **{len(rows)}** |",
        f"| planned_ok | **{planned_ok}/{len(rows)}** |",
        f"| planned_request_count_total | **{planned_total}** |",
        f"| CNINFO calls | **0** |",
        f"| universe_csv | `{universe_csv}` |",
        "",
        "## Gate",
        "",
        "```text",
        f"d_class_margin_trading_first_slice_runner_extension_gate = {MARGIN_TRADING_FIRST_SLICE_RUNNER_GATE}",
        "approval_status = NOT_APPROVED",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "## Known-Event Track",
        "",
        "known-event replacement track **remains closed** · no DLC003R/DLC006R rerun",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_margin_trading_first_slice_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def margin_trading_first_slice_row_to_universe_case(
    row: MarginTradingFirstSliceRow,
) -> UniverseCase:
    """将 margin_trading 第一切片 universe 行转为探测用 UniverseCase。"""
    return UniverseCase(
        case_id=row.case_id,
        company_code=row.company_code,
        company_name=row.company_name,
        component=row.component,
        market=row.market,
        risk_level="",
        expected_behavior=row.expected_behavior,
        reason=row.reason,
    )


def build_margin_trading_first_slice_live_probe_plan(
    anchor_tdate: str,
) -> List[Tuple[str, Dict[str, Any]]]:
    """margin_trading 第一切片 live 探测计划（detailList + 可选邻近探测占位）。"""
    items: List[Tuple[str, Dict[str, Any]]] = []
    for step in build_margin_trading_first_slice_plan(anchor_tdate):
        if step == "budget_reserve":
            continue
        items.append((step, {}))
    return items[:MARGIN_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS]


def is_margin_trading_first_slice_acceptable(
    row: MarginTradingFirstSliceRow,
    summary: Dict[str, str],
) -> bool:
    """第一切片 acceptable 判定；禁止 disclosure-only 升级为 captured_normal。"""
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if rs in ("http_error", "blocked") or qs == "blocked":
        return False
    if qs == "verified":
        return False
    if "disclosure" in row.reason.lower() and rs != "found":
        return False
    if rs == "found" and rc >= 1:
        return True
    if rs == "empty_but_valid" and rc == 0:
        return True
    if qs == "needs_review" and rc >= 0:
        return True
    return False


def assess_margin_trading_first_slice_failure_type(
    row: MarginTradingFirstSliceRow,
    summary: Dict[str, str],
) -> str:
    if is_margin_trading_first_slice_acceptable(row, summary):
        return ""
    rs = summary.get("retrieval_status", "")
    if rs in ("http_error", "blocked"):
        return "network_or_http_error"
    if rs == "empty_but_valid":
        return "empty_but_valid_only"
    return "expectation_mismatch"


def validate_margin_trading_first_slice_request_caps(stats: LiveStats) -> List[str]:
    issues: List[str] = []
    for case_id in sorted(MARGIN_TRADING_FIRST_SLICE_ALLOWED_CASE_IDS):
        cnt = stats.case_request_counts.get(case_id, 0)
        if cnt > MARGIN_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{MARGIN_TRADING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:{case_id}={cnt}"
            )
    if stats.cninfo_requests > MARGIN_TRADING_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{MARGIN_TRADING_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{stats.cninfo_requests}"
        )
    return issues


def compute_margin_trading_first_slice_execution_gate(
    universe_rows: List[MarginTradingFirstSliceRow],
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """margin_trading 第一切片 live 执行 gate；≥3/5 acceptable → PASS_WITH_CAVEAT。"""
    acceptable = sum(
        1
        for row in universe_rows
        if is_margin_trading_first_slice_acceptable(
            row, case_summaries.get(row.case_id, {})
        )
    )
    if acceptable >= 3:
        return MARGIN_TRADING_FIRST_SLICE_EXECUTION_GATE_PASS
    return MARGIN_TRADING_FIRST_SLICE_EXECUTION_GATE_FAIL


def build_margin_trading_first_slice_live_row(
    row: MarginTradingFirstSliceRow,
    summary: Dict[str, str],
) -> Dict[str, str]:
    acceptable = is_margin_trading_first_slice_acceptable(row, summary)
    failure_type = assess_margin_trading_first_slice_failure_type(row, summary)
    return {
        "case_id": row.case_id,
        "company_code": row.company_code,
        "company_name": row.company_name,
        "component": row.component,
        "market": row.market,
        "anchor_tdate": row.anchor_tdate,
        "expected_behavior": row.expected_behavior,
        "retrieval_status": summary.get("retrieval_status", ""),
        "quality_status": summary.get("quality_status", ""),
        "lineage_status": summary.get("lineage_status", ""),
        "record_count": summary.get("record_count", "0"),
        "empty_but_valid": summary.get("empty_but_valid", "no"),
        "needs_review": summary.get("needs_review", "no"),
        "endpoint_used": summary.get("endpoint_used", ""),
        "cninfo_request_count": summary.get("cninfo_request_count", "0"),
        "early_stop_triggered": summary.get("early_stop_triggered", "no"),
        "acceptable": "yes" if acceptable else "no",
        "failure_type": failure_type,
        "pdf_download": "no",
        "ocr": "no",
        "extraction": "no",
        "db_write": "no",
        "minio_write": "no",
        "rag_run": "no",
        "notes": summary.get("notes", ""),
    }


def write_margin_trading_first_slice_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_margin_trading_first_slice_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=MARGIN_TRADING_FIRST_SLICE_LIVE_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_margin_trading_first_slice_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    quality_rows = [
        {
            "case_id": row["case_id"],
            "component": row["component"],
            "anchor_tdate": row["anchor_tdate"],
            "expected_behavior": row["expected_behavior"],
            "retrieval_status": row["retrieval_status"],
            "record_count": row["record_count"],
            "quality_status": row["quality_status"],
            "acceptable": row["acceptable"],
            "failure_type": row["failure_type"],
            "cninfo_request_count": row["cninfo_request_count"],
            "notes": row["notes"],
        }
        for row in rows
    ]
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_margin_trading_first_slice_quality_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=MARGIN_TRADING_FIRST_SLICE_QUALITY_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_margin_trading_first_slice_live_summary(
    rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    acceptable = sum(1 for r in rows if r.get("acceptable") == "yes")
    lines = [
        "# CNINFO D 类 margin_trading First-Slice Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** margin_trading first-slice live summary · **NOT APPROVED for production**",
        "",
        "## Result",
        "",
        f"| 项 | 值 |",
        f"|----|-----|",
        f"| cases | **{len(rows)}** |",
        f"| acceptable | **{acceptable}/{len(rows)}** |",
        f"| CNINFO requests | **{stats.cninfo_requests}** |",
        f"| execution gate | **{gate}** |",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_margin_trading_first_slice_live_path_gate = {MARGIN_TRADING_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_margin_trading_first_slice_execution_gate = {gate}",
        "approval_status = NOT_APPROVED",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_margin_trading_first_slice_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_margin_trading_first_slice_live(
    universe_rows: List[MarginTradingFirstSliceRow],
    output_paths: Dict[str, str],
) -> int:
    """margin_trading 第一切片 live 探针；仅 DMT001–DMT005 调用 CNINFO。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    component_cfg = source_configs.get(MARGIN_TRADING_FIRST_SLICE_COMPONENT, {})
    endpoint = endpoints.get(
        MARGIN_TRADING_FIRST_SLICE_COMPONENT,
        component_cfg.get("api_url", MARGIN_TRADING_FIRST_SLICE_ENDPOINT),
    )

    for row in universe_rows:
        plan = build_margin_trading_first_slice_live_probe_plan(row.anchor_tdate)
        if len(plan) > MARGIN_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            print(
                f"ERROR: {MARGIN_TRADING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"planned={len(plan)}",
                file=sys.stderr,
            )
            return 2

    session = requests.Session()
    stats = LiveStats()
    case_summaries: Dict[str, Dict[str, str]] = {}
    early_stop_count = 0

    for row in sorted(universe_rows, key=lambda r: r.case_id):
        case = margin_trading_first_slice_row_to_universe_case(row)
        plan = build_margin_trading_first_slice_live_probe_plan(row.anchor_tdate)
        _, summary, stopped = execute_v2_bounded_probe_case(
            case,
            plan,
            "margin_trading_first_slice",
            MARGIN_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS,
            component_cfg,
            endpoint,
            session,
            stats,
            output_paths,
        )
        case_summaries[row.case_id] = summary
        if stopped:
            early_stop_count += 1
        print(
            f"{row.case_id} {summary['retrieval_status']}: "
            f"records={summary['record_count']} "
            f"requests={summary['cninfo_request_count']} "
            f"early_stop={summary['early_stop_triggered']}",
            flush=True,
        )

    cap_issues = validate_margin_trading_first_slice_request_caps(stats)
    if cap_issues:
        print(
            "ERROR: margin_trading first-slice request cap validation failed: "
            f"{cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_margin_trading_first_slice_execution_gate(
        universe_rows, case_summaries
    )
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = MARGIN_TRADING_FIRST_SLICE_EXECUTION_GATE_FAIL

    live_rows = [
        build_margin_trading_first_slice_live_row(row, case_summaries[row.case_id])
        for row in sorted(universe_rows, key=lambda r: r.case_id)
        if row.case_id in case_summaries
    ]

    report_path = write_margin_trading_first_slice_live_report(live_rows, output_paths)
    quality_path = write_margin_trading_first_slice_quality_report(
        live_rows, output_paths
    )
    summary_path = write_margin_trading_first_slice_live_summary(
        live_rows, stats, gate, output_paths
    )

    print(
        f"mode=margin_trading_first_slice_live cases={len(live_rows)} "
        f"acceptable={sum(1 for r in live_rows if r['acceptable'] == 'yes')} "
        f"total_requests={stats.cninfo_requests} early_stop_count={early_stop_count}"
    )
    print(f"gate=d_class_margin_trading_first_slice_execution_gate={gate}")
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == MARGIN_TRADING_FIRST_SLICE_EXECUTION_GATE_PASS else 1


def run_margin_trading_first_slice(args: argparse.Namespace) -> int:
    enforce_margin_trading_first_slice_forbidden_options(args)
    enforce_margin_trading_first_slice_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(
            f"ERROR: {MARGIN_TRADING_FIRST_SLICE_UNIVERSE_CSV_REQUIRED}",
            file=sys.stderr,
        )
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_margin_trading_first_slice_output_root(
        args.output_root
    )
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_margin_trading_first_slice_universe(args.universe_csv)
    universe_issues = validate_margin_trading_first_slice_universe(universe_rows)
    if universe_issues:
        print(
            "ERROR: margin_trading first-slice universe validation failed: "
            f"{universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_margin_trading_first_slice_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_margin_trading_first_slice_live(universe_rows, output_paths)

    dry_rows = build_margin_trading_first_slice_dryrun_rows(universe_rows, output_root)
    report_path = write_margin_trading_first_slice_dryrun_report(
        dry_rows, output_paths
    )
    summary_path = write_margin_trading_first_slice_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    print(
        f"mode=margin_trading_first_slice_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={planned_total} cninfo_calls=0"
    )
    print(
        "gate=d_class_margin_trading_first_slice_runner_extension_gate="
        f"{MARGIN_TRADING_FIRST_SLICE_RUNNER_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0


def targeted_probe_row_to_universe_case(row: TargetedProbeUniverseRow) -> UniverseCase:
    """将 targeted probe universe 行转为探测用 UniverseCase。"""
    return UniverseCase(
        case_id=row.targeted_probe_id,
        company_code=row.company_code,
        company_name=row.company_name,
        component=row.component,
        market="",
        risk_level="",
        expected_behavior=row.expected_behavior,
        reason=row.notes,
    )


def build_targeted_probe_probe_plan(
    row: TargetedProbeUniverseRow,
) -> Tuple[str, List[Tuple[str, Dict[str, Any]]]]:
    """返回 (probe_type, plan)。"""
    row_cap = _targeted_probe_row_cap(row)
    if row.targeted_probe_id == "DLC003R-T01":
        return "tdate", build_targeted_probe_plan_dlc003r(row.anchor_date, row_cap)
    if row.targeted_probe_id == "DLC006R-T01":
        return "mode_date", build_targeted_probe_plan_dlc006r(row.anchor_date, row_cap)
    return "", []


def assess_targeted_probe_outcome(
    summary: Dict[str, str],
) -> Tuple[bool, str, str]:
    """targeted probe 结果评估；返回 (acceptable, failure_type, structured_record_evidence)。"""
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    notes = summary.get("notes", "")
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0

    if rs in ("http_error", "blocked") or qs == "blocked":
        if "network_error" in notes:
            return False, "network_error", "no"
        if "invalid_json" in notes or rs == "http_error":
            return False, "schema_error", "no"
        return False, "network_error", "no"
    if rs == "found" and rc >= 1:
        return True, "", "yes"
    if qs == "needs_review" and rc >= 1:
        return True, "", "yes"
    if rs == "empty_but_valid" and rc == 0:
        return False, "empty_but_valid_after_budget", "no"
    return False, "schema_error", "no"


def compute_targeted_probe_execution_gate(
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """targeted probe live 执行 gate；永不返回 PASS。"""
    outcomes = []
    for probe_id in sorted(TARGETED_PROBE_ALLOWED_IDS):
        summary = case_summaries.get(probe_id, {})
        acceptable, _, _ = assess_targeted_probe_outcome(summary)
        outcomes.append(acceptable)
    if all(outcomes):
        return TARGETED_PROBE_EXECUTION_GATE_PASS
    return TARGETED_PROBE_EXECUTION_GATE_FAIL


def validate_targeted_probe_request_caps(stats: LiveStats) -> List[str]:
    issues: List[str] = []
    dlc003 = stats.case_request_counts.get("DLC003R-T01", 0)
    dlc006 = stats.case_request_counts.get("DLC006R-T01", 0)
    if dlc003 > TARGETED_PROBE_PER_ROW_MAX_CAP:
        issues.append(f"{TARGETED_PROBE_ROW_CAP_EXCEEDED}:DLC003R-T01={dlc003}")
    if dlc006 > TARGETED_PROBE_PER_ROW_MAX_CAP:
        issues.append(f"{TARGETED_PROBE_ROW_CAP_EXCEEDED}:DLC006R-T01={dlc006}")
    if dlc003 + dlc006 > TARGETED_PROBE_TOTAL_MAX_CAP:
        issues.append(f"{TARGETED_PROBE_TOTAL_CAP_EXCEEDED}:{dlc003 + dlc006}")
    return issues


def build_targeted_probe_live_row(
    probe_row: TargetedProbeUniverseRow,
    summary: Dict[str, str],
    request_cap: int,
) -> Dict[str, str]:
    acceptable, failure_type, structured_evidence = assess_targeted_probe_outcome(summary)
    return {
        "targeted_probe_id": probe_row.targeted_probe_id,
        "replacement_case_id": probe_row.replacement_case_id,
        "company_code": probe_row.company_code,
        "company_name": probe_row.company_name,
        "component": probe_row.component,
        "anchor_date": probe_row.anchor_date,
        "expected_behavior": probe_row.expected_behavior,
        "request_cap": str(request_cap),
        "cninfo_request_count": summary.get("cninfo_request_count", "0"),
        "retrieval_status": summary.get("retrieval_status", ""),
        "record_count": summary.get("record_count", "0"),
        "quality_status": summary.get("quality_status", ""),
        "lineage_status": summary.get("lineage_status", ""),
        "acceptable": "yes" if acceptable else "no",
        "failure_type": failure_type,
        "endpoint_used": summary.get("endpoint_used", ""),
        "structured_record_evidence": structured_evidence,
        "pdf_download": "no",
        "ocr": "no",
        "extraction": "no",
        "db_write": "no",
        "minio_write": "no",
        "rag_run": "no",
        "notes": summary.get("notes", ""),
    }


def write_targeted_probe_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_known_event_targeted_probe_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TARGETED_PROBE_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_targeted_probe_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    quality_rows = [
        {
            "targeted_probe_id": row["targeted_probe_id"],
            "replacement_case_id": row["replacement_case_id"],
            "component": row["component"],
            "anchor_date": row["anchor_date"],
            "expected_behavior": row["expected_behavior"],
            "retrieval_status": row["retrieval_status"],
            "record_count": row["record_count"],
            "quality_status": row["quality_status"],
            "acceptable": row["acceptable"],
            "failure_type": row["failure_type"],
            "structured_record_evidence": row["structured_record_evidence"],
            "cninfo_request_count": row["cninfo_request_count"],
            "notes": row["notes"],
        }
        for row in rows
    ]
    path = os.path.join(
        output_paths["reports"],
        "d_class_known_event_targeted_probe_quality_report.csv",
    )
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TARGETED_PROBE_QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(quality_rows)
    return path


def write_targeted_probe_live_summary(
    live_rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    lines = [
        "# CNINFO D 类 Known Event Targeted Probe Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** known-event targeted probe live · **无 DB/MinIO/RAG/PDF/OCR** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| DLC003R-T01 CNINFO requests | **{stats.case_request_counts.get('DLC003R-T01', 0)}** |",
        f"| DLC006R-T01 CNINFO requests | **{stats.case_request_counts.get('DLC006R-T01', 0)}** |",
        f"| Total CNINFO requests | **{stats.cninfo_requests}** |",
        f"| DB writes | **{stats.db_writes}** |",
        f"| MinIO writes | **{stats.minio_writes}** |",
        f"| RAG runs | **{stats.rag_runs}** |",
        "",
        "## Probe Results",
        "",
        "| targeted_probe_id | anchor | retrieval | records | requests | acceptable | failure_type |",
        "|-------------------|--------|-----------|---------|----------|------------|--------------|",
    ]
    for row in live_rows:
        lines.append(
            f"| {row['targeted_probe_id']} | {row['anchor_date']} | {row['retrieval_status']} | "
            f"{row['record_count']} | {row['cninfo_request_count']} | {row['acceptable']} | "
            f"{row['failure_type']} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "```text",
            f"d_class_known_event_targeted_probe_execution_gate = {gate}",
            "approval_status = NOT_APPROVED",
            "```",
            "",
            "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
            "",
        ]
    )
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_known_event_targeted_probe_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_known_event_targeted_probe_live(
    universe_rows: List[TargetedProbeUniverseRow],
    output_paths: Dict[str, str],
) -> int:
    """known-event targeted probe live 探针；仅 DLC003R-T01/DLC006R-T01 调用 CNINFO。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    probe_row_map = {r.targeted_probe_id: r for r in universe_rows}

    for row in universe_rows:
        _, plan = build_targeted_probe_probe_plan(row)
        row_cap = _targeted_probe_row_cap(row)
        if len(plan) > row_cap:
            print(
                f"ERROR: {TARGETED_PROBE_ROW_CAP_EXCEEDED}:planned={len(plan)}",
                file=sys.stderr,
            )
            return 2

    session = requests.Session()
    stats = LiveStats()
    case_summaries: Dict[str, Dict[str, str]] = {}
    early_stop_count = 0

    for row in universe_rows:
        case = targeted_probe_row_to_universe_case(row)
        probe_type, plan = build_targeted_probe_probe_plan(row)
        row_cap = _targeted_probe_row_cap(row)
        source_cfg = source_configs.get(case.component, {})
        endpoint = endpoints.get(case.component, source_cfg.get("api_url", ""))
        _, summary, stopped = execute_v2_bounded_probe_case(
            case,
            plan,
            probe_type,
            row_cap,
            source_cfg,
            endpoint,
            session,
            stats,
            output_paths,
        )
        case_summaries[row.targeted_probe_id] = summary
        if stopped:
            early_stop_count += 1
        print(
            f"{row.targeted_probe_id} {summary['retrieval_status']}: "
            f"records={summary['record_count']} "
            f"requests={summary['cninfo_request_count']} "
            f"early_stop={summary['early_stop_triggered']}",
            flush=True,
        )

    cap_issues = validate_targeted_probe_request_caps(stats)
    if cap_issues:
        print(
            f"ERROR: targeted probe request cap validation failed: {cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_targeted_probe_execution_gate(case_summaries)
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = TARGETED_PROBE_EXECUTION_GATE_FAIL

    live_rows = [
        build_targeted_probe_live_row(
            probe_row_map[probe_id],
            case_summaries[probe_id],
            _targeted_probe_row_cap(probe_row_map[probe_id]),
        )
        for probe_id in sorted(TARGETED_PROBE_ALLOWED_IDS)
        if probe_id in case_summaries
    ]

    report_path = write_targeted_probe_live_report(live_rows, output_paths)
    quality_path = write_targeted_probe_quality_report(live_rows, output_paths)
    summary_path = write_targeted_probe_live_summary(live_rows, stats, gate, output_paths)

    print(
        f"mode=known_event_targeted_probe_live dlc003r_t01_requests="
        f"{stats.case_request_counts.get('DLC003R-T01', 0)} "
        f"dlc006r_t01_requests={stats.case_request_counts.get('DLC006R-T01', 0)} "
        f"total_requests={stats.cninfo_requests} early_stop_count={early_stop_count}"
    )
    print(f"gate=d_class_known_event_targeted_probe_execution_gate={gate}")
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == TARGETED_PROBE_EXECUTION_GATE_PASS else 1


def _params_key(params: Dict[str, Any]) -> str:
    return json.dumps(params, sort_keys=True, ensure_ascii=False)


def _format_probe_value(params: Dict[str, Any]) -> str:
    if "tdate" in params and "type" in params:
        return f"type={params['type']};tdate={params['tdate']}"
    if "tdate" in params:
        return f"tdate={params['tdate']}"
    if "type" in params:
        return f"type={params['type']}"
    return json.dumps(params, ensure_ascii=False, sort_keys=True)


def _month_end_date(year: int, month: int) -> str:
    last_day = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-{last_day:02d}"


def _month_end_dates(count: int, ref: date) -> List[str]:
    dates: List[str] = []
    year, month = ref.year, ref.month
    for _ in range(count):
        dates.append(_month_end_date(year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return dates


def _quarter_end_dates(count: int, ref: date) -> List[str]:
    """从参考日所在季度向前回溯季末日。"""
    quarter_ends = [(3, 31), (6, 30), (9, 30), (12, 31)]
    q_idx = next(i for i, (m, _) in enumerate(quarter_ends) if ref.month <= m)
    year = ref.year
    month, day = quarter_ends[q_idx]
    dates: List[str] = []
    for _ in range(count):
        dates.append(f"{year:04d}-{month:02d}-{day:02d}")
        q_idx -= 1
        if q_idx < 0:
            q_idx = 3
            year -= 1
        month, day = quarter_ends[q_idx]
    return dates


def _dlc003_v1_baseline_tdates() -> List[str]:
    return [
        "2026-06-08",
        "2026-07-03",
        "2025-12-31",
        "2025-06-30",
        "2024-12-31",
        "2024-06-28",
        "2023-12-29",
        "2023-06-30",
    ]


def _dlc006_v1_baseline_params() -> List[Dict[str, Any]]:
    return [
        {"type": "desc"},
        {"type": "inc", "tdate": "2026-07-03"},
        {"type": "inc", "tdate": "2025-12-31"},
        {"type": "inc", "tdate": "2025-06-30"},
        {"type": "desc", "tdate": "2026-07-03"},
    ]


def _dedupe_param_list(
    items: List[Tuple[str, Dict[str, Any]]],
) -> List[Tuple[str, Dict[str, Any]]]:
    seen: Set[str] = set()
    out: List[Tuple[str, Dict[str, Any]]] = []
    for dimension, params in items:
        key = _params_key(params)
        if key in seen:
            continue
        seen.add(key)
        out.append((dimension, params))
    return out


def build_bounded_probe_plan_dlc003(max_requests: int) -> List[Tuple[str, Dict[str, Any]]]:
    base = dict(load_table_source_configs().get("restricted_shares_unlock", {}).get("params_template") or {})
    items: List[Tuple[str, Dict[str, Any]]] = []
    for tdate in _dlc003_v1_baseline_tdates():
        items.append(("v1_baseline_replay", {**base, "tdate": tdate}))
    for tdate in _month_end_dates(12, V2_REFERENCE_DATE):
        items.append(("recent_12m_monthly", {**base, "tdate": tdate}))
    for tdate in _quarter_end_dates(8, V2_REFERENCE_DATE):
        items.append(("recent_24m_quarterly", {**base, "tdate": tdate}))
        items.append(("reporting_window_quarterly", {**base, "tdate": tdate}))
    deduped = _dedupe_param_list(items)
    return deduped[:max_requests]


def build_bounded_probe_plan_dlc006(max_requests: int) -> List[Tuple[str, Dict[str, Any]]]:
    items: List[Tuple[str, Dict[str, Any]]] = []
    for params in _dlc006_v1_baseline_params():
        items.append(("v1_baseline_replay", dict(params)))
    quarter_4 = _quarter_end_dates(4, V2_REFERENCE_DATE)
    for tdate in quarter_4:
        items.append(("recent_12m_quarterly_inc", {"type": "inc", "tdate": tdate}))
    quarter_8 = _quarter_end_dates(8, V2_REFERENCE_DATE)
    for tdate in quarter_8:
        items.append(("recent_24m_quarterly_both", {"type": "inc", "tdate": tdate}))
        items.append(("recent_24m_quarterly_both", {"type": "desc", "tdate": tdate}))
    for params in _dlc006_v1_baseline_params():
        items.append(("v1_modes_expanded_dates", dict(params)))
    deduped = _dedupe_param_list(items)
    return deduped[:max_requests]


def load_v1_probe_cases() -> Dict[str, UniverseCase]:
    cases = load_universe(DEFAULT_UNIVERSE_CSV)
    return {c.case_id: c for c in cases if c.case_id in V2_PROBE_CASE_IDS}


def load_v1_live_report_rows(path: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    report_path = path or V1_LIVE_REPORT_CSV
    if not os.path.isfile(report_path):
        return {}
    with open(report_path, newline="", encoding="utf-8") as f:
        return {row["case_id"]: row for row in csv.DictReader(f)}


def parse_cases_filter(cases_arg: Optional[str]) -> Set[str]:
    if not cases_arg or cases_arg.strip().lower() == "all":
        return set(V2_PROBE_CASE_IDS)
    selected = {c.strip() for c in cases_arg.split(",") if c.strip()}
    return selected


def validate_v2_case_selection(selected: Set[str]) -> List[str]:
    issues: List[str] = []
    if not selected:
        issues.append(f"{V2_PROBE_CASE_ONLY}:empty_selection")
    extra = selected - V2_PROBE_CASE_IDS
    if extra:
        issues.append(f"{V2_PROBE_CASE_ONLY}:{','.join(sorted(extra))}")
    return issues


def validate_v2_request_caps(dlc003_max: int, dlc006_max: int) -> List[str]:
    issues: List[str] = []
    if dlc003_max > V2_DLC003_MAX_CAP:
        issues.append(f"{V2_DLC003_CAP_EXCEEDED}:{dlc003_max}>{V2_DLC003_MAX_CAP}")
    if dlc006_max > V2_DLC006_MAX_CAP:
        issues.append(f"{V2_DLC006_CAP_EXCEEDED}:{dlc006_max}>{V2_DLC006_MAX_CAP}")
    if dlc003_max + dlc006_max > V2_TOTAL_MAX_CAP:
        issues.append(
            f"{V2_TOTAL_CAP_EXCEEDED}:{dlc003_max}+{dlc006_max}>{V2_TOTAL_MAX_CAP}"
        )
    return issues


def validate_v2_probe_cases(cases: Dict[str, UniverseCase]) -> List[str]:
    issues: List[str] = []
    for case_id in sorted(V2_PROBE_CASE_IDS):
        case = cases.get(case_id)
        if case is None:
            issues.append(f"missing_probe_case:{case_id}")
            continue
        if not case.company_code:
            issues.append(f"{V2_INVENTED_COMPANY_CODE}:{case_id}")
        if "CANDIDATE_REQUIRED" in case.case_id:
            issues.append(f"{V2_INVENTED_COMPANY_CODE}:{case.case_id}")
    return issues


def build_v2_probe_plan_rows(
    probe_cases: Dict[str, UniverseCase],
    endpoints: Dict[str, str],
    dlc003_max: int,
    dlc006_max: int,
) -> List[ProbePlanEntry]:
    rows: List[ProbePlanEntry] = []
    if "DLC003" in probe_cases:
        case = probe_cases["DLC003"]
        endpoint = endpoints.get(case.component, "")
        plan = build_bounded_probe_plan_dlc003(dlc003_max)
        for idx, (dimension, params) in enumerate(plan, start=1):
            rows.append(
                ProbePlanEntry(
                    case_id=case.case_id,
                    component=case.component,
                    company_code=case.company_code,
                    company_name=case.company_name,
                    probe_type="tdate",
                    probe_dimension=dimension,
                    planned_probe_value=_format_probe_value(params),
                    planned_endpoint=endpoint,
                    request_index=idx,
                    max_request_count=dlc003_max,
                    early_stop_enabled="yes",
                    cninfo_call_planned="yes",
                    dryrun_status="planned",
                    notes="early stop on first company-level hit; no event-date guessing",
                )
            )
    if "DLC006" in probe_cases:
        case = probe_cases["DLC006"]
        endpoint = endpoints.get(case.component, "")
        plan = build_bounded_probe_plan_dlc006(dlc006_max)
        for idx, (dimension, params) in enumerate(plan, start=1):
            rows.append(
                ProbePlanEntry(
                    case_id=case.case_id,
                    component=case.component,
                    company_code=case.company_code,
                    company_name=case.company_name,
                    probe_type="mode_date",
                    probe_dimension=dimension,
                    planned_probe_value=_format_probe_value(params),
                    planned_endpoint=endpoint,
                    request_index=idx,
                    max_request_count=dlc006_max,
                    early_stop_enabled="yes",
                    cninfo_call_planned="yes",
                    dryrun_status="planned",
                    notes="early stop on first company-level hit; no event-date guessing",
                )
            )
    return rows


def build_v2_comparison_plan_rows(
    probe_cases: Dict[str, UniverseCase],
    plan_rows: List[ProbePlanEntry],
    v1_rows: Dict[str, Dict[str, str]],
) -> List[Dict[str, str]]:
    planned_counts: Dict[str, int] = {}
    for row in plan_rows:
        planned_counts[row.case_id] = planned_counts.get(row.case_id, 0) + 1

    v1_cases = {c.case_id: c for c in load_universe(DEFAULT_UNIVERSE_CSV)}
    comparison: List[Dict[str, str]] = []
    all_case_ids = sorted(V2_PROBE_CASE_IDS | V2_BASELINE_CASE_IDS)
    for case_id in all_case_ids:
        v1 = v1_rows.get(case_id, {})
        v1_rs = v1.get("retrieval_status", "v1_reference_missing")
        v1_cnt = v1.get("cninfo_request_count", "0")
        if case_id in V2_PROBE_CASE_IDS:
            case = probe_cases[case_id]
            exp_v1 = "yes" if v1 and is_case_acceptable(case, v1) else ("no" if v1 else "unknown")
            comparison.append(
                {
                    "case_id": case_id,
                    "component": case.component,
                    "v1_retrieval_status": v1_rs,
                    "v2_retrieval_status": "planned",
                    "v1_cninfo_request_count": v1_cnt,
                    "v2_cninfo_request_count": str(planned_counts.get(case_id, 0)),
                    "expectation_met_v1": exp_v1,
                    "expectation_met_v2": "planned",
                    "probe_extension_applied": "yes",
                    "notes": "bounded probe extension planned; live not executed",
                }
            )
        else:
            case = v1_cases.get(case_id)
            exp_v1 = (
                "yes"
                if case and v1 and is_case_acceptable(case, v1)
                else ("no" if v1 else "unknown")
            )
            comparison.append(
                {
                    "case_id": case_id,
                    "component": case.component if case else v1.get("component", ""),
                    "v1_retrieval_status": v1_rs,
                    "v2_retrieval_status": "v1_baseline_reference",
                    "v1_cninfo_request_count": v1_cnt,
                    "v2_cninfo_request_count": "0",
                    "expectation_met_v1": exp_v1,
                    "expectation_met_v2": "na",
                    "probe_extension_applied": "no",
                    "notes": "baseline reference only; no v2 CNINFO",
                }
            )
    return comparison


def write_v2_dryrun_report(rows: List[ProbePlanEntry], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "d_class_tiny_live_v2_bounded_probe_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=V2_DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(row.to_row() for row in rows)
    return report_path


def write_v2_comparison_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "d_class_tiny_live_v2_comparison_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=V2_COMPARISON_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_v2_dryrun_summary(
    plan_rows: List[ProbePlanEntry],
    comparison_rows: List[Dict[str, str]],
    dlc003_max: int,
    dlc006_max: int,
    output_paths: Dict[str, str],
) -> str:
    dlc003_planned = sum(1 for r in plan_rows if r.case_id == "DLC003")
    dlc006_planned = sum(1 for r in plan_rows if r.case_id == "DLC006")
    total_planned = len(plan_rows)
    caps_ok = (
        dlc003_planned <= dlc003_max <= V2_DLC003_MAX_CAP
        and dlc006_planned <= dlc006_max <= V2_DLC006_MAX_CAP
        and total_planned <= V2_TOTAL_MAX_CAP
    )
    lines = [
        "# CNINFO D 类 Tiny Live V2 Bounded Probe Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** v2 bounded probe dry-run only · **CNINFO calls = 0** · **NOT APPROVED**",
        "",
        "## Planned Request Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| DLC003 planned | **{dlc003_planned}** |",
        f"| DLC006 planned | **{dlc006_planned}** |",
        f"| Total planned | **{total_planned}** |",
        f"| DLC003 cap | **{dlc003_max}** (max {V2_DLC003_MAX_CAP}) |",
        f"| DLC006 cap | **{dlc006_max}** (max {V2_DLC006_MAX_CAP}) |",
        f"| Total cap | **{V2_TOTAL_MAX_CAP}** |",
        f"| Caps respected | **{'yes' if caps_ok else 'no'}** |",
        "",
        "## Safety",
        "",
        "| 项 | 状态 |",
        "|----|------|",
        "| Output root isolated (v2) | **yes** |",
        "| v1 output untouched | **yes** |",
        "| CNINFO calls | **0** |",
        "| DB / MinIO / RAG | **0** |",
        "| verified / production_ready | **no** |",
        "",
        "## Comparison Plan",
        "",
        f"| comparison rows | {len(comparison_rows)} |",
        "",
        "## Gate",
        "",
        "```text",
        f"d_class_tiny_live_v2_bounded_probe_runner_gate = {V2_RUNNER_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"], "d_class_tiny_live_v2_bounded_probe_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def enforce_v2_forbidden_options(args: argparse.Namespace) -> None:
    enforce_forbidden_options(args)
    if args.bounded_probe_v2 and args.approve_d_class_tiny_live_validation and args.mode == "live":
        print(f"ERROR: {V2_MIXED_MODE_BLOCKED}", file=sys.stderr)
        sys.exit(2)
    if args.bounded_probe_v2 and args.approve_d_class_tiny_live_validation:
        print(f"ERROR: {V2_WRONG_APPROVAL_FLAG}:approve_d_class_tiny_live_validation", file=sys.stderr)
        sys.exit(2)
    if not args.bounded_probe_v2 and args.approve_d_class_tiny_live_v2_bounded_probe:
        print(f"ERROR: {V2_WRONG_APPROVAL_FLAG}:v2_flag_without_bounded_probe_v2", file=sys.stderr)
        sys.exit(2)


def enforce_v2_live_approval_gate(args: argparse.Namespace) -> None:
    if args.mode == "live" and args.bounded_probe_v2:
        if not args.approve_d_class_tiny_live_v2_bounded_probe:
            print(f"ERROR: {V2_APPROVAL_REQUIRED}", file=sys.stderr)
            sys.exit(2)


def _assess_v2_probe_row(
    case: UniverseCase,
    err: str,
    company_records: List[Dict[str, Any]],
) -> Tuple[str, str, str, str, str, str, List[str]]:
    """单探测行状态评估。"""
    notes_parts: List[str] = []
    record_count = len(company_records)
    empty_but_valid = "no"
    needs_review = "no"

    if err in ("rate_limited",) or err.startswith("network_error"):
        retrieval_status = "http_error" if err.startswith("network_error") else "blocked"
        quality_status = "blocked"
        lineage_status = "needs_review"
        notes_parts.append(err)
    elif err.startswith("http_") or err == "invalid_json":
        retrieval_status = "http_error"
        quality_status = "blocked"
        lineage_status = "needs_review"
        notes_parts.append(err)
    elif record_count == 0:
        retrieval_status = "empty_but_valid"
        quality_status = "pass"
        lineage_status = "discovered"
        empty_but_valid = "yes"
        notes_parts.append("company-level zero rows; legal empty per quality policy")
    else:
        retrieval_status = "found"
        quality_status = "pass"
        lineage_status = "discovered"
        notes_parts.append(f"found {record_count} row(s) for company")

    return (
        retrieval_status,
        quality_status,
        lineage_status,
        str(record_count),
        empty_but_valid,
        needs_review,
        notes_parts,
    )


def execute_v2_bounded_probe_case(
    case: UniverseCase,
    plan: List[Tuple[str, Dict[str, Any]]],
    probe_type: str,
    max_request_count: int,
    source_cfg: dict,
    endpoint: str,
    session: requests.Session,
    stats: LiveStats,
    output_paths: Dict[str, str],
) -> Tuple[List[Dict[str, str]], Dict[str, str], bool]:
    """执行 v2 有界探测；返回逐探测行、case 汇总、是否 early stop。"""
    probe_rows: List[Dict[str, str]] = []
    all_records: List[Dict[str, Any]] = []
    used_params: Dict[str, Any] = {}
    http_status = 0
    case_early_stop = False
    last_error = ""

    for idx, (dimension, params) in enumerate(plan, start=1):
        payload, http_status, err = _cninfo_request(
            session, source_cfg, params, stats, case.case_id
        )
        used_params = params
        records = _extract_records(payload) if payload is not None and not err else []
        company_records = _filter_company_records(records, case.company_code)
        if err:
            last_error = err

        (
            retrieval_status,
            quality_status,
            lineage_status,
            record_count,
            empty_but_valid,
            needs_review,
            notes_parts,
        ) = _assess_v2_probe_row(case, err, company_records)

        row_early_stop = "no"
        if company_records and not err:
            all_records = company_records
            case_early_stop = True
            row_early_stop = "yes"
            notes_parts.append("early stop triggered on company-level hit")

        probe_rows.append(
            {
                "case_id": case.case_id,
                "component": case.component,
                "company_code": case.company_code,
                "company_name": case.company_name,
                "probe_type": probe_type,
                "probe_dimension": dimension,
                "probe_value": _format_probe_value(params),
                "retrieval_status": retrieval_status,
                "quality_status": quality_status,
                "lineage_status": lineage_status,
                "record_count": record_count,
                "empty_but_valid": empty_but_valid,
                "needs_review": needs_review,
                "endpoint_used": endpoint,
                "request_index": str(idx),
                "max_request_count": str(max_request_count),
                "early_stop_triggered": row_early_stop,
                "cninfo_request_count": str(stats.case_request_counts.get(case.case_id, 0)),
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
                "notes": "; ".join(notes_parts),
            }
        )

        if case_early_stop:
            break
        if err and not (err.startswith("http_") or err == "invalid_json"):
            break
        if err in ("invalid_json",) or err.startswith("http_"):
            last_error = err
            continue

    final_count = len(all_records)
    if case_early_stop:
        summary_rs = "found"
        summary_qs = "pass"
        summary_ls = "discovered"
        summary_empty = "no"
        summary_notes = f"early stop after {stats.case_request_counts.get(case.case_id, 0)} requests; found {final_count} row(s)"
    elif last_error and not all_records:
        summary_rs, summary_qs, summary_ls, _, summary_empty, _, note_parts = _assess_v2_probe_row(
            case, last_error, []
        )
        summary_notes = "; ".join(note_parts)
    else:
        summary_rs = "empty_but_valid"
        summary_qs = "pass"
        summary_ls = "discovered"
        summary_empty = "yes"
        summary_notes = (
            f"exhausted bounded probe cap ({stats.case_request_counts.get(case.case_id, 0)} requests); "
            "company-level zero rows; legal empty per quality policy"
        )

    snapshot_path = os.path.join(
        output_paths["live_snapshots"],
        f"{case.case_id}_{case.component}.json",
    )
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "case_id": case.case_id,
                "company_code": case.company_code,
                "component": case.component,
                "endpoint": endpoint,
                "params": used_params,
                "http_status": http_status,
                "record_count": final_count,
                "sample_records": all_records[:3],
                "cninfo_called": True,
                "early_stop": case_early_stop,
                "bounded_probe_v2": True,
                "db_write": False,
                "minio_write": False,
                "rag_run": False,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    case_summary = {
        "case_id": case.case_id,
        "component": case.component,
        "expected_behavior": case.expected_behavior,
        "retrieval_status": summary_rs,
        "quality_status": summary_qs,
        "lineage_status": summary_ls,
        "record_count": str(final_count),
        "empty_but_valid": summary_empty,
        "needs_review": "no",
        "endpoint_used": endpoint,
        "cninfo_request_count": str(stats.case_request_counts.get(case.case_id, 0)),
        "early_stop_triggered": "yes" if case_early_stop else "no",
        "db_write": "no",
        "minio_write": "no",
        "rag_run": "no",
        "notes": summary_notes,
    }
    return probe_rows, case_summary, case_early_stop


def build_v2_comparison_live_rows(
    probe_cases: Dict[str, UniverseCase],
    case_summaries: Dict[str, Dict[str, str]],
    v1_rows: Dict[str, Dict[str, str]],
    stats: LiveStats,
) -> List[Dict[str, str]]:
    v1_cases = {c.case_id: c for c in load_universe(DEFAULT_UNIVERSE_CSV)}
    comparison: List[Dict[str, str]] = []
    for case_id in sorted(V2_PROBE_CASE_IDS | V2_BASELINE_CASE_IDS):
        v1 = v1_rows.get(case_id, {})
        v1_rs = v1.get("retrieval_status", "v1_reference_missing")
        v1_cnt = v1.get("cninfo_request_count", "0")
        if case_id in V2_PROBE_CASE_IDS:
            case = probe_cases[case_id]
            v2 = case_summaries[case_id]
            v2_cnt = str(stats.case_request_counts.get(case_id, 0))
            exp_v1 = "yes" if v1 and is_case_acceptable(case, v1) else ("no" if v1 else "unknown")
            exp_v2 = "yes" if is_case_acceptable(case, v2) else "no"
            comparison.append(
                {
                    "case_id": case_id,
                    "component": case.component,
                    "v1_retrieval_status": v1_rs,
                    "v2_retrieval_status": v2.get("retrieval_status", ""),
                    "v1_cninfo_request_count": v1_cnt,
                    "v2_cninfo_request_count": v2_cnt,
                    "expectation_met_v1": exp_v1,
                    "expectation_met_v2": exp_v2,
                    "probe_extension_applied": "yes",
                    "notes": v2.get("notes", ""),
                }
            )
        else:
            case = v1_cases.get(case_id)
            exp_v1 = (
                "yes"
                if case and v1 and is_case_acceptable(case, v1)
                else ("no" if v1 else "unknown")
            )
            comparison.append(
                {
                    "case_id": case_id,
                    "component": case.component if case else v1.get("component", ""),
                    "v1_retrieval_status": v1_rs,
                    "v2_retrieval_status": "v1_baseline_reference",
                    "v1_cninfo_request_count": v1_cnt,
                    "v2_cninfo_request_count": "0",
                    "expectation_met_v1": exp_v1,
                    "expectation_met_v2": "na",
                    "probe_extension_applied": "no",
                    "notes": "baseline reference only; no v2 CNINFO",
                }
            )
    return comparison


def compute_v2_execution_gate(
    stats: LiveStats,
    dlc003_max: int,
    dlc006_max: int,
) -> str:
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        return EXECUTION_GATE_FAIL
    dlc003_used = stats.case_request_counts.get("DLC003", 0)
    dlc006_used = stats.case_request_counts.get("DLC006", 0)
    if dlc003_used > dlc003_max or dlc006_used > dlc006_max:
        return EXECUTION_GATE_FAIL
    if dlc003_used + dlc006_used > V2_TOTAL_MAX_CAP:
        return EXECUTION_GATE_FAIL
    return EXECUTION_GATE_PASS


def write_v2_live_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "d_class_tiny_live_v2_bounded_probe_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=V2_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_v2_quality_report(
    summaries: List[Dict[str, str]],
    probe_cases: Dict[str, UniverseCase],
    output_paths: Dict[str, str],
) -> str:
    quality_rows = []
    for row in summaries:
        case = probe_cases[row["case_id"]]
        quality_rows.append(
            {
                "case_id": row["case_id"],
                "component": row["component"],
                "expected_behavior": row["expected_behavior"],
                "retrieval_status": row["retrieval_status"],
                "quality_status": row["quality_status"],
                "lineage_status": row["lineage_status"],
                "record_count": row["record_count"],
                "acceptable": "yes" if is_case_acceptable(case, row) else "no",
                "cninfo_request_count": row["cninfo_request_count"],
                "early_stop_triggered": row["early_stop_triggered"],
                "notes": row["notes"],
            }
        )
    path = os.path.join(
        output_paths["reports"], "d_class_tiny_live_v2_bounded_probe_quality_report.csv"
    )
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=V2_QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(quality_rows)
    return path


def write_v2_live_summary(
    case_summaries: Dict[str, Dict[str, str]],
    comparison_rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    early_stop_count: int,
    output_paths: Dict[str, str],
) -> str:
    dlc003 = case_summaries.get("DLC003", {})
    dlc006 = case_summaries.get("DLC006", {})
    lines = [
        "# CNINFO D 类 Tiny Live V2 Bounded Probe 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** v2 bounded probe live · **无 DB/MinIO/RAG** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| DLC003 CNINFO requests | **{stats.case_request_counts.get('DLC003', 0)}** |",
        f"| DLC006 CNINFO requests | **{stats.case_request_counts.get('DLC006', 0)}** |",
        f"| Total CNINFO requests | **{stats.cninfo_requests}** |",
        f"| Early stop count | **{early_stop_count}** |",
        f"| DB writes | **{stats.db_writes}** |",
        f"| MinIO writes | **{stats.minio_writes}** |",
        f"| RAG runs | **{stats.rag_runs}** |",
        "",
        "## Case Results",
        "",
        "| case_id | retrieval | records | requests | early_stop |",
        "|---------|-----------|---------|----------|------------|",
        f"| DLC003 | {dlc003.get('retrieval_status', '')} | {dlc003.get('record_count', '')} | "
        f"{dlc003.get('cninfo_request_count', '')} | {dlc003.get('early_stop_triggered', '')} |",
        f"| DLC006 | {dlc006.get('retrieval_status', '')} | {dlc006.get('record_count', '')} | "
        f"{dlc006.get('cninfo_request_count', '')} | {dlc006.get('early_stop_triggered', '')} |",
        "",
        "## Gate",
        "",
        "```text",
        f"d_class_tiny_live_v2_bounded_probe_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
        "## Parallel Safety",
        "",
        "- v1 outputs: **unchanged**",
        "- baseline cases DLC001/002/004/005/007: **v1 reference only**",
        "- C-class: **`SNAPSHOT_GENERATED_QA_REVIEW`**（不变）",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"], "d_class_tiny_live_v2_bounded_probe_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def run_bounded_probe_v2(args: argparse.Namespace) -> int:
    enforce_v2_forbidden_options(args)
    enforce_v2_live_approval_gate(args)

    ok_root, root_err = validate_v2_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    cap_issues = validate_v2_request_caps(args.dlc003_max_requests, args.dlc006_max_requests)
    if cap_issues:
        print(f"ERROR: cap validation failed: {cap_issues}", file=sys.stderr)
        return 2

    selected = parse_cases_filter(args.cases)
    selection_issues = validate_v2_case_selection(selected)
    if selection_issues:
        print(f"ERROR: case selection failed: {selection_issues}", file=sys.stderr)
        return 2

    probe_cases_all = load_v1_probe_cases()
    probe_cases = {k: v for k, v in probe_cases_all.items() if k in selected}
    case_issues = validate_v2_probe_cases(probe_cases)
    if case_issues:
        print(f"ERROR: probe case validation failed: {case_issues}", file=sys.stderr)
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()

    plan_rows = build_v2_probe_plan_rows(
        probe_cases,
        endpoints,
        args.dlc003_max_requests,
        args.dlc006_max_requests,
    )
    dlc003_planned = sum(1 for r in plan_rows if r.case_id == "DLC003")
    dlc006_planned = sum(1 for r in plan_rows if r.case_id == "DLC006")
    if dlc003_planned > args.dlc003_max_requests:
        print(f"ERROR: {V2_DLC003_CAP_EXCEEDED}:planned={dlc003_planned}", file=sys.stderr)
        return 2
    if dlc006_planned > args.dlc006_max_requests:
        print(f"ERROR: {V2_DLC006_CAP_EXCEEDED}:planned={dlc006_planned}", file=sys.stderr)
        return 2
    if dlc003_planned + dlc006_planned > V2_TOTAL_MAX_CAP:
        print(f"ERROR: {V2_TOTAL_CAP_EXCEEDED}:planned={dlc003_planned + dlc006_planned}", file=sys.stderr)
        return 2

    if args.mode != "live":
        v1_rows = load_v1_live_report_rows(args.v1_report_path)
        comparison_rows = build_v2_comparison_plan_rows(probe_cases, plan_rows, v1_rows)
        report_path = write_v2_dryrun_report(plan_rows, output_paths)
        comparison_path = write_v2_comparison_report(comparison_rows, output_paths)
        summary_path = write_v2_dryrun_summary(
            plan_rows,
            comparison_rows,
            args.dlc003_max_requests,
            args.dlc006_max_requests,
            output_paths,
        )
        print(
            f"mode=bounded_probe_v2_dry_run dlc003_planned={dlc003_planned} "
            f"dlc006_planned={dlc006_planned} total_planned={len(plan_rows)} cninfo_calls=0"
        )
        print(f"gate=d_class_tiny_live_v2_bounded_probe_runner_gate={V2_RUNNER_GATE}")
        print(f"dryrun_report={report_path}")
        print(f"comparison_report={comparison_path}")
        print(f"dryrun_summary={summary_path}")
        return 0

    session = requests.Session()
    stats = LiveStats()
    all_probe_rows: List[Dict[str, str]] = []
    case_summaries: Dict[str, Dict[str, str]] = {}
    early_stop_count = 0

    probe_specs = [
        ("DLC003", "tdate", build_bounded_probe_plan_dlc003(args.dlc003_max_requests)),
        ("DLC006", "mode_date", build_bounded_probe_plan_dlc006(args.dlc006_max_requests)),
    ]
    for case_id, probe_type, plan in probe_specs:
        if case_id not in probe_cases:
            continue
        case = probe_cases[case_id]
        source_cfg = source_configs.get(case.component, {})
        endpoint = endpoints.get(case.component, source_cfg.get("api_url", ""))
        max_cap = (
            args.dlc003_max_requests if case_id == "DLC003" else args.dlc006_max_requests
        )
        probe_rows, summary, stopped = execute_v2_bounded_probe_case(
            case,
            plan,
            probe_type,
            max_cap,
            source_cfg,
            endpoint,
            session,
            stats,
            output_paths,
        )
        all_probe_rows.extend(probe_rows)
        case_summaries[case_id] = summary
        if stopped:
            early_stop_count += 1
        print(
            f"{case_id} {summary['retrieval_status']}: records={summary['record_count']} "
            f"requests={summary['cninfo_request_count']} early_stop={summary['early_stop_triggered']}",
            flush=True,
        )

    gate = compute_v2_execution_gate(
        stats, args.dlc003_max_requests, args.dlc006_max_requests
    )
    v1_rows = load_v1_live_report_rows(args.v1_report_path)
    comparison_rows = build_v2_comparison_live_rows(
        probe_cases, case_summaries, v1_rows, stats
    )
    report_path = write_v2_live_report(all_probe_rows, output_paths)
    quality_path = write_v2_quality_report(
        list(case_summaries.values()), probe_cases, output_paths
    )
    comparison_path = write_v2_comparison_report(comparison_rows, output_paths)
    summary_path = write_v2_live_summary(
        case_summaries,
        comparison_rows,
        stats,
        gate,
        early_stop_count,
        output_paths,
    )

    print(
        f"mode=bounded_probe_v2_live dlc003_requests={stats.case_request_counts.get('DLC003', 0)} "
        f"dlc006_requests={stats.case_request_counts.get('DLC006', 0)} "
        f"total_requests={stats.cninfo_requests} early_stop_count={early_stop_count}"
    )
    print(f"gate=d_class_tiny_live_v2_bounded_probe_execution_gate={gate}")
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"comparison_report={comparison_path}")
    print(f"summary={summary_path}")
    return 0 if gate == EXECUTION_GATE_PASS else 1


def ensure_output_layout(output_root: str, mode: str) -> Dict[str, str]:
    paths = {
        "root": output_root,
        "reports": os.path.join(output_root, "reports"),
        "planned_snapshots": os.path.join(output_root, "planned_snapshots"),
        "live_snapshots": os.path.join(output_root, "live_snapshots"),
    }
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    return paths


def load_table_source_configs() -> Dict[str, dict]:
    with open(TABLE_SOURCES_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {s["source_id"]: s for s in data.get("sources", []) if s.get("source_id")}


def load_registry_endpoints() -> Dict[str, str]:
    with open(REGISTRY_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    out: Dict[str, str] = {}
    for src in data.get("sources", []):
        sid = src.get("source_id")
        url = (src.get("api") or {}).get("url")
        if sid and url:
            out[sid] = url
    return out


def load_universe(path: str) -> List[UniverseCase]:
    cases: List[UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(
                UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    component=str(row.get("component", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    risk_level=str(row.get("risk_level", "")).strip(),
                    expected_behavior=str(row.get("expected_behavior", "")).strip(),
                    reason=str(row.get("reason", "")).strip(),
                )
            )
    return cases


def validate_universe_batch(cases: List[UniverseCase]) -> List[str]:
    issues: List[str] = []
    if len(cases) != EXPECTED_UNIVERSE_SIZE:
        issues.append(f"{UNIVERSE_SIZE_MISMATCH}:got={len(cases)}")
    seen_ids: Set[str] = set()
    seen_components: Set[str] = set()
    for case in cases:
        if case.case_id not in ALLOWED_CASE_IDS:
            issues.append(f"{NON_DLC_CASE}:{case.case_id}")
        if case.case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case.case_id}")
        seen_ids.add(case.case_id)
        if case.component not in ALLOWED_COMPONENTS:
            issues.append(f"{COMPONENT_NOT_ALLOWED}:{case.component}")
        if case.component in seen_components:
            issues.append(f"duplicate_component:{case.component}")
        seen_components.add(case.component)
        if not case.company_code:
            issues.append(f"missing_company_code:{case.case_id}")
        if not case.expected_behavior:
            issues.append(f"missing_expected_behavior:{case.case_id}")
    if len(seen_components) != len(ALLOWED_COMPONENTS):
        missing = sorted(ALLOWED_COMPONENTS - seen_components)
        issues.append(f"missing_components:{','.join(missing)}")
    return issues


def enforce_forbidden_options(args: argparse.Namespace) -> None:
    if args.db_write:
        print(f"ERROR: {DB_WRITE_BLOCKED}", file=sys.stderr)
        sys.exit(2)
    if args.minio_write:
        print(f"ERROR: {MINIO_WRITE_BLOCKED}", file=sys.stderr)
        sys.exit(2)
    if args.rag_run:
        print(f"ERROR: {RAG_RUN_BLOCKED}", file=sys.stderr)
        sys.exit(2)
    if args.mark_verified:
        print(f"ERROR: {VERIFIED_BLOCKED}", file=sys.stderr)
        sys.exit(2)
    if args.production_ready:
        print(f"ERROR: {PRODUCTION_READY_BLOCKED}", file=sys.stderr)
        sys.exit(2)
    wrong_flags = [
        ("approve_b_class_tiny_live_validation", args.approve_b_class_tiny_live_validation),
        ("approve_full_harvest", args.approve_full_harvest),
        ("approve_phase2_smoke_harvest", args.approve_phase2_smoke_harvest),
        ("approve_phase3_batch_500_harvest", args.approve_phase3_batch_500_harvest),
        ("approve_a_class_tiny_live_validation", args.approve_a_class_tiny_live_validation),
    ]
    for name, enabled in wrong_flags:
        if enabled:
            print(f"ERROR: {WRONG_APPROVAL_FLAG}:{name}", file=sys.stderr)
            sys.exit(2)


def enforce_live_approval_gate(args: argparse.Namespace) -> None:
    if args.mode == "live" and not args.approve_d_class_tiny_live_validation:
        print(f"ERROR: {TINY_LIVE_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def _extract_records(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("records", "marketList", "data", "list", "result", "prbookinfos", "content"):
        val = payload.get(key)
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]
        if isinstance(val, dict):
            for sub in ("records", "list", "data"):
                subval = val.get(sub)
                if isinstance(subval, list):
                    return [x for x in subval if isinstance(x, dict)]
    return []


def _company_code_from_record(rec: Dict[str, Any]) -> str:
    for key in ("SECCODE", "seccode", "secCode", "stockCode", "stockcode"):
        val = rec.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return ""


def _filter_company_records(records: List[Dict[str, Any]], company_code: str) -> List[Dict[str, Any]]:
    matched = []
    for rec in records:
        code = _company_code_from_record(rec)
        if code == company_code:
            matched.append(rec)
        elif not code and company_code in json.dumps(rec, ensure_ascii=False):
            matched.append(rec)
    return matched


def _cninfo_request(
    session: requests.Session,
    source_cfg: dict,
    params_override: Optional[Dict[str, Any]],
    stats: LiveStats,
    case_id: str,
) -> Tuple[Optional[Any], int, str]:
    api_url = str(source_cfg.get("api_url") or "")
    page_url = str(source_cfg.get("page_url") or "")
    method = str(source_cfg.get("method") or "POST").upper()
    params_location = str(source_cfg.get("params_location") or "form").lower()
    params = dict(source_cfg.get("params_template") or {})
    if params_override:
        params.update(params_override)

    headers = dict(AJAX_HEADERS)
    if page_url:
        headers["Referer"] = page_url

    try:
        if method == "GET":
            resp = session.get(api_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        elif params_location == "query":
            post_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
            resp = session.post(api_url, params=params, headers=post_headers, timeout=REQUEST_TIMEOUT)
        elif params_location == "none":
            post_headers = {k: v for k, v in headers.items() if k != "Content-Type"}
            resp = session.post(api_url, headers=post_headers, timeout=REQUEST_TIMEOUT)
        else:
            resp = session.post(api_url, data=params, headers=headers, timeout=REQUEST_TIMEOUT)

        stats.cninfo_requests += 1
        stats.case_request_counts[case_id] = stats.case_request_counts.get(case_id, 0) + 1
        time.sleep(SLEEP_SECONDS)

        if resp.status_code == 429:
            return None, resp.status_code, "rate_limited"
        if resp.status_code != 200:
            return None, resp.status_code, f"http_{resp.status_code}"
        try:
            return resp.json(), resp.status_code, ""
        except json.JSONDecodeError:
            return None, resp.status_code, "invalid_json"
    except requests.RequestException as exc:
        return None, 0, f"network_error:{exc}"


def _assess_executive_needs_review(records: List[Dict[str, Any]]) -> bool:
    for rec in records:
        pos_a = rec.get("F001V")
        pos_b = rec.get("F002V")
        if pos_a and pos_b and str(pos_a).strip() != str(pos_b).strip():
            return True
        if not rec.get("F004N") and not rec.get("F005N") and not rec.get("F006N"):
            return True
    return False


def _build_live_params(case: UniverseCase, source_cfg: dict) -> List[Dict[str, Any]]:
    """返回按优先级排列的请求参数列表（用于需要多参数探测的组件）。"""
    base = dict(source_cfg.get("params_template") or {})
    if case.component == "disclosure_schedule":
        p = copy.deepcopy(base)
        p["stockCode"] = case.company_code
        return [p]
    if case.component == "restricted_shares_unlock":
        return [{**base, "tdate": d} for d in (
            "2026-06-08", "2026-07-03", "2025-12-31", "2025-06-30", "2024-12-31",
            "2024-06-28", "2023-12-29", "2023-06-30",
        )]
    if case.component == "shareholder_change":
        return [
            {"type": "desc"},
            {"type": "inc", "tdate": "2026-07-03"},
            {"type": "inc", "tdate": "2025-12-31"},
            {"type": "inc", "tdate": "2025-06-30"},
            {"type": "desc", "tdate": "2026-07-03"},
        ]
    if case.component == "executive_shareholding":
        return [
            {"timeMark": "threeMonth", "varyType": "b"},
            {"timeMark": "oneYear", "varyType": "b"},
            {"timeMark": "oneMonth", "varyType": "b"},
        ]
    return [copy.deepcopy(base)]


def execute_live_case(
    case: UniverseCase,
    source_cfg: dict,
    endpoint: str,
    session: requests.Session,
    stats: LiveStats,
    output_paths: Dict[str, str],
) -> Dict[str, str]:
    param_list = _build_live_params(case, source_cfg)
    all_records: List[Dict[str, Any]] = []
    last_error = ""
    http_status = 0
    used_params: Dict[str, Any] = {}

    multi_probe = case.component in (
        "restricted_shares_unlock",
        "shareholder_change",
        "executive_shareholding",
    )

    for params in param_list:
        payload, http_status, err = _cninfo_request(session, source_cfg, params, stats, case.case_id)
        used_params = params
        if err:
            last_error = err
            if multi_probe and (err.startswith("http_") or err == "invalid_json"):
                continue
            break
        records = _extract_records(payload) if payload is not None else []
        company_records = _filter_company_records(records, case.company_code)
        if company_records:
            all_records = company_records
            break
        if not multi_probe:
            all_records = company_records
            break
        if records:
            last_error = "no_company_match_on_date"

    record_count = len(all_records)
    empty_but_valid = "no"
    needs_review = "no"
    notes_parts: List[str] = []

    if last_error in ("rate_limited",) or last_error.startswith("network_error"):
        retrieval_status = "http_error" if last_error.startswith("network_error") else "blocked"
        quality_status = "blocked"
        lineage_status = "needs_review"
        notes_parts.append(last_error)
    elif last_error.startswith("http_") or last_error == "invalid_json":
        retrieval_status = "http_error"
        quality_status = "blocked"
        lineage_status = "needs_review"
        notes_parts.append(last_error)
    elif record_count == 0:
        retrieval_status = "empty_but_valid"
        quality_status = "pass"
        lineage_status = "discovered"
        empty_but_valid = "yes"
        notes_parts.append("company-level zero rows; legal empty per quality policy")
    else:
        retrieval_status = "found"
        lineage_status = "discovered"
        quality_status = "pass"
        if case.component == "executive_shareholding" and _assess_executive_needs_review(all_records):
            needs_review = "yes"
            quality_status = "needs_review"
            lineage_status = "needs_review"
            notes_parts.append("executive position/amount mapping medium confidence")
        elif case.expected_behavior == "needs_review_candidate":
            needs_review = "yes"
            quality_status = "needs_review"
            lineage_status = "needs_review"
            notes_parts.append("needs_review candidate; varyType/position review")
        else:
            notes_parts.append(f"found {record_count} row(s) for company")

    snapshot_path = os.path.join(
        output_paths["live_snapshots"],
        f"{case.case_id}_{case.component}.json",
    )
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "case_id": case.case_id,
                "company_code": case.company_code,
                "component": case.component,
                "endpoint": endpoint,
                "params": used_params,
                "http_status": http_status,
                "record_count": record_count,
                "sample_records": all_records[:3],
                "cninfo_called": True,
                "db_write": False,
                "minio_write": False,
                "rag_run": False,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "component": case.component,
        "expected_behavior": case.expected_behavior,
        "retrieval_status": retrieval_status,
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "record_count": str(record_count),
        "empty_but_valid": empty_but_valid,
        "needs_review": needs_review,
        "endpoint_used": endpoint,
        "cninfo_request_count": str(stats.case_request_counts.get(case.case_id, 0)),
        "db_write": "no",
        "minio_write": "no",
        "rag_run": "no",
        "notes": "; ".join(notes_parts),
    }


def is_case_acceptable(case: UniverseCase, row: Dict[str, str]) -> bool:
    rs = row.get("retrieval_status", "")
    qs = row.get("quality_status", "")
    try:
        rc = int(row.get("record_count", "0"))
    except ValueError:
        rc = 0
    if rs in ("http_error", "blocked") or qs == "blocked":
        return False
    if qs == "verified":
        return False
    exp = case.expected_behavior
    if exp == "captured_normal":
        return rs == "found" and rc >= 1 and qs in ("pass", "caveat")
    if exp == "empty_but_valid":
        return rs == "empty_but_valid" and rc == 0 and qs in ("pass", "caveat")
    if exp == "needs_review_candidate":
        return qs == "needs_review" and row.get("needs_review") == "yes"
    return False


def compute_execution_gate(rows: List[Dict[str, str]], cases: List[UniverseCase], stats: LiveStats) -> str:
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        return EXECUTION_GATE_FAIL
    case_map = {c.case_id: c for c in cases}
    acceptable = sum(1 for r in rows if is_case_acceptable(case_map[r["case_id"]], r))
    if acceptable >= 5:
        return EXECUTION_GATE_PASS
    return EXECUTION_GATE_FAIL


def _planned_quality_notes(expected_behavior: str) -> str:
    if expected_behavior == "empty_but_valid":
        return "validate retrieval_status=empty_but_valid; quality_status=pass|caveat"
    if expected_behavior == "needs_review_candidate":
        return "validate quality_status=needs_review; lineage_status=needs_review if mapping ambiguous"
    return "validate retrieval_status=found; required fields mapped; quality_status=pass|caveat"


def build_dryrun_row(
    case: UniverseCase,
    endpoint: str,
    output_paths: Dict[str, str],
    universe_ok: bool,
) -> Dict[str, str]:
    planned_output = os.path.join(
        output_paths["planned_snapshots"],
        f"{case.case_id}_{case.component}.json",
    )
    if universe_ok:
        dryrun_status = "planned"
        notes = _planned_quality_notes(case.expected_behavior)
    else:
        dryrun_status = "universe_validation_failed"
        notes = "universe batch validation failed"
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "component": case.component,
        "expected_behavior": case.expected_behavior,
        "planned_endpoint": endpoint,
        "planned_output": planned_output,
        "cninfo_call_planned": "no",
        "db_write": "no",
        "minio_write": "no",
        "rag_run": "no",
        "dryrun_status": dryrun_status,
        "notes": notes,
    }


def write_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(output_paths["reports"], "d_class_tiny_live_dryrun_report.csv")
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DRYRUN_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_dryrun_summary(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    lines = [
        "# CNINFO D 类 Tiny Live Validation Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** dry-run only · **CNINFO calls = 0**",
        "",
        f"| Total cases | {len(rows)} |",
        "",
        "```text",
        f"d_class_tiny_live_runner_gate = {RUNNER_GATE}",
        "```",
        "",
    ]
    summary_path = os.path.join(output_paths["reports"], "d_class_tiny_live_dryrun_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def write_live_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(output_paths["reports"], "d_class_tiny_live_report.csv")
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_quality_report(
    rows: List[Dict[str, str]], cases: List[UniverseCase], output_paths: Dict[str, str]
) -> str:
    case_map = {c.case_id: c for c in cases}
    quality_rows = []
    for row in rows:
        case = case_map[row["case_id"]]
        quality_rows.append(
            {
                "case_id": row["case_id"],
                "component": row["component"],
                "expected_behavior": row["expected_behavior"],
                "retrieval_status": row["retrieval_status"],
                "quality_status": row["quality_status"],
                "lineage_status": row["lineage_status"],
                "acceptable": "yes" if is_case_acceptable(case, row) else "no",
                "notes": row["notes"],
            }
        )
    path = os.path.join(output_paths["reports"], "d_class_tiny_live_quality_report.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUALITY_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(quality_rows)
    return path


def write_live_summary(
    rows: List[Dict[str, str]],
    cases: List[UniverseCase],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    case_map = {c.case_id: c for c in cases}
    acceptable = sum(1 for r in rows if is_case_acceptable(case_map[r["case_id"]], r))
    failed = len(rows) - acceptable
    empty_count = sum(1 for r in rows if r.get("empty_but_valid") == "yes")
    review_count = sum(1 for r in rows if r.get("needs_review") == "yes")

    lines = [
        "# CNINFO D 类 Tiny Live Validation 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** isolated tiny live event/metadata validation · **无 DB/MinIO/RAG** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| Total cases | {len(rows)} |",
        f"| Acceptable | {acceptable} |",
        f"| Failed | {failed} |",
        f"| empty_but_valid | {empty_count} |",
        f"| needs_review | {review_count} |",
        f"| CNINFO requests | **{stats.cninfo_requests}** |",
        f"| DB writes | **{stats.db_writes}** |",
        f"| MinIO writes | **{stats.minio_writes}** |",
        f"| RAG runs | **{stats.rag_runs}** |",
        "",
        "## Case Results",
        "",
        "| case_id | component | expected | retrieval | quality | lineage | records | acceptable |",
        "|---------|-----------|----------|-----------|---------|---------|---------|------------|",
    ]
    for row in rows:
        case = case_map[row["case_id"]]
        ok = "yes" if is_case_acceptable(case, row) else "no"
        lines.append(
            f"| {row['case_id']} | {row['component']} | {row['expected_behavior']} | "
            f"{row['retrieval_status']} | {row['quality_status']} | {row['lineage_status']} | "
            f"{row['record_count']} | {ok} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "```text",
            f"d_class_tiny_live_execution_gate = {gate}",
            "d_class_phase1_tiny_live_validation_gate = READY_FOR_APPROVAL",
            "```",
            "",
            "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
            "",
            "## Parallel Safety",
            "",
            "- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**（不变）",
            "- A-class / B-class outputs: **unchanged**",
            "- No harvest · No DB · No MinIO · No RAG",
            "",
        ]
    )
    summary_path = os.path.join(output_paths["reports"], "d_class_tiny_live_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CNINFO D-class Phase1 tiny live metadata validation（dry-run default）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")

    parser.add_argument("--universe-csv", "--universe", dest="universe_csv", default=DEFAULT_UNIVERSE_CSV)
    parser.add_argument("--output-root", default=None)
    parser.add_argument(
        "--approve-d-class-tiny-live-validation",
        action="store_true",
        help="显式批准 D-class Phase 1 tiny live metadata validation",
    )
    parser.add_argument("--approve-b-class-tiny-live-validation", action="store_true")
    parser.add_argument("--approve-a-class-tiny-live-validation", action="store_true")
    parser.add_argument("--approve-full-harvest", action="store_true")
    parser.add_argument("--approve-phase2-smoke-harvest", action="store_true")
    parser.add_argument("--approve-phase3-batch-500-harvest", action="store_true")
    parser.add_argument("--db-write", action="store_true")
    parser.add_argument("--minio-write", action="store_true")
    parser.add_argument("--rag-run", action="store_true")
    parser.add_argument("--mark-verified", action="store_true")
    parser.add_argument("--production-ready", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--bounded-probe-v2",
        action="store_true",
        help="启用 v2 bounded probe 模式（仅 DLC003/DLC006）",
    )
    parser.add_argument(
        "--approve-d-class-tiny-live-v2-bounded-probe",
        action="store_true",
        help="显式批准 v2 bounded probe live（当前 offline 回合仍不执行）",
    )
    parser.add_argument(
        "--dlc003-max-requests",
        type=int,
        default=V2_DLC003_MAX_CAP,
        help="DLC003 请求硬顶（最大 24）",
    )
    parser.add_argument(
        "--dlc006-max-requests",
        type=int,
        default=V2_DLC006_MAX_CAP,
        help="DLC006 请求硬顶（最大 20）",
    )
    parser.add_argument(
        "--cases",
        default="DLC003,DLC006",
        help="v2 bounded probe case 过滤（仅允许 DLC003,DLC006）",
    )
    parser.add_argument(
        "--v1-report-path",
        default=V1_LIVE_REPORT_CSV,
        help="只读 v1 live 报告路径（comparison 用）",
    )
    parser.add_argument(
        "--known-event-replacement",
        action="store_true",
        help="启用 known-event replacement validation 模式（仅 DLC003R/DLC006R）",
    )
    parser.add_argument(
        "--approve-d-class-known-event-replacement-validation",
        action="store_true",
        help="显式批准 known-event replacement live（本扩展 live 尚未实现）",
    )
    parser.add_argument(
        "--pdf-download",
        action="store_true",
        help="禁止：replacement 模式不允许 PDF 下载",
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="禁止：replacement 模式不允许 OCR",
    )
    parser.add_argument(
        "--extraction",
        action="store_true",
        help="禁止：replacement / targeted probe 模式不允许 extraction",
    )
    parser.add_argument(
        "--known-event-targeted-probe",
        action="store_true",
        help="启用 known-event targeted probe 模式（仅 DLC003R-T01/DLC006R-T01）",
    )
    parser.add_argument(
        "--approve-d-class-known-event-targeted-probe",
        action="store_true",
        help="显式批准 known-event targeted probe live（本扩展 live 尚未实现）",
    )
    parser.add_argument(
        "--margin-trading-first-slice",
        action="store_true",
        help="启用 margin_trading 第一切片模式（仅 DMT001–DMT005）",
    )
    parser.add_argument(
        "--approve-d-class-margin-trading-first-slice",
        action="store_true",
        help="显式批准 margin_trading first-slice live（须人工批准 · 本任务不执行 live）",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.margin_trading_first_slice:
        if args.output_root is None:
            args.output_root = DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT
        return run_margin_trading_first_slice(args)

    if args.known_event_targeted_probe:
        if args.output_root is None:
            args.output_root = DEFAULT_TARGETED_PROBE_OUTPUT_ROOT
        return run_known_event_targeted_probe(args)

    if args.known_event_replacement:
        if args.output_root is None:
            args.output_root = DEFAULT_REPLACEMENT_OUTPUT_ROOT
        if args.cases == "DLC003,DLC006":
            args.cases = "DLC003R,DLC006R"
        return run_known_event_replacement(args)

    if args.bounded_probe_v2:
        if args.output_root is None:
            args.output_root = DEFAULT_V2_OUTPUT_ROOT
        return run_bounded_probe_v2(args)

    if args.output_root is None:
        args.output_root = DEFAULT_OUTPUT_ROOT

    enforce_forbidden_options(args)
    enforce_live_approval_gate(args)

    ok_root, root_err = validate_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    if not os.path.isfile(QUALITY_POLICY):
        print(f"ERROR: quality policy not found: {QUALITY_POLICY}", file=sys.stderr)
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    cases = load_universe(args.universe_csv)
    if args.limit is not None:
        cases = cases[: args.limit]

    universe_issues = validate_universe_batch(cases)
    if universe_issues:
        print(f"ERROR: universe validation failed: {universe_issues}", file=sys.stderr)
        return 2

    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    stats = LiveStats()

    if args.mode == "dry_run":
        dry_rows = []
        for case in cases:
            endpoint = endpoints.get(case.component, "")
            dry_rows.append(build_dryrun_row(case, endpoint, output_paths, True))
        report_path = write_dryrun_report(dry_rows, output_paths)
        summary_path = write_dryrun_summary(dry_rows, output_paths)
        print(f"mode=dry_run cases={len(cases)} cninfo_calls=0")
        print(f"gate=d_class_tiny_live_runner_gate={RUNNER_GATE}")
        print(f"dryrun_report={report_path}")
        print(f"dryrun_summary={summary_path}")
        return 0

    session = requests.Session()
    live_rows: List[Dict[str, str]] = []
    for case in cases:
        source_cfg = source_configs.get(case.component, {})
        endpoint = endpoints.get(case.component, source_cfg.get("api_url", ""))
        row = execute_live_case(case, source_cfg, endpoint, session, stats, output_paths)
        live_rows.append(row)
        mark = "OK" if is_case_acceptable(case, row) else "FAIL"
        print(
            f"{case.case_id} {mark}: {row['retrieval_status']} records={row['record_count']} "
            f"quality={row['quality_status']}",
            flush=True,
        )

    gate = compute_execution_gate(live_rows, cases, stats)
    report_path = write_live_report(live_rows, output_paths)
    quality_path = write_quality_report(live_rows, cases, output_paths)
    summary_path = write_live_summary(live_rows, cases, stats, gate, output_paths)

    acceptable = sum(1 for r in live_rows if is_case_acceptable(
        next(c for c in cases if c.case_id == r["case_id"]), r
    ))
    print(f"mode=live cases={len(cases)} cninfo_calls={stats.cninfo_requests}")
    print(f"acceptable={acceptable} failed={len(cases) - acceptable}")
    print(f"gate=d_class_tiny_live_execution_gate={gate}")
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"summary={summary_path}")
    return 0 if gate == EXECUTION_GATE_PASS else 1


if __name__ == "__main__":
    sys.exit(main())
