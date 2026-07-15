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

DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_block_trade_first_slice",
)
DEFAULT_BLOCK_TRADE_FIRST_SLICE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_block_trade_first_slice_universe_draft.csv",
)
DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_disclosure_schedule_first_slice",
)
BLOCK_TRADE_FIRST_SLICE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_block_trade_first_slice_dryrun_report.csv",
)
BLOCK_TRADE_FIRST_SLICE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_block_trade_first_slice_dryrun_summary.md",
)

BLOCK_TRADE_FIRST_SLICE_RUNNER_GATE = "READY_FOR_APPROVAL"
BLOCK_TRADE_FIRST_SLICE_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
BLOCK_TRADE_FIRST_SLICE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
BLOCK_TRADE_FIRST_SLICE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
BLOCK_TRADE_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE = 5
BLOCK_TRADE_FIRST_SLICE_ALLOWED_CASE_IDS: Set[str] = {
    "DBT001",
    "DBT002",
    "DBT003",
    "DBT004",
    "DBT005",
}
BLOCK_TRADE_FIRST_SLICE_EXPECTED_COMPANY_CODES: Dict[str, str] = {
    "DBT001": "601988",
    "DBT002": "000895",
    "DBT003": "600000",
    "DBT004": "002415",
    "DBT005": "688981",
}
BLOCK_TRADE_FIRST_SLICE_FORBIDDEN_COMPANY_CODES: Set[str] = {"688671", "301259"}
BLOCK_TRADE_FIRST_SLICE_COMPONENT = "block_trade"
BLOCK_TRADE_FIRST_SLICE_ANCHOR_TDATE = "2026-07-03"
BLOCK_TRADE_FIRST_SLICE_ENDPOINT = (
    "https://www.cninfo.com.cn/data20/ints/statistics"
)
BLOCK_TRADE_FIRST_SLICE_PER_CASE_MAX_REQUESTS = 1
BLOCK_TRADE_FIRST_SLICE_TOTAL_MAX_REQUESTS = 20

BLOCK_TRADE_FIRST_SLICE_APPROVAL_REQUIRED = (
    "approve_d_class_block_trade_first_slice_required"
)
BLOCK_TRADE_FIRST_SLICE_WRONG_APPROVAL_FLAG = (
    "wrong_approval_flag_for_block_trade_first_slice"
)
BLOCK_TRADE_FIRST_SLICE_MIXED_MODE_BLOCKED = (
    "block_trade_first_slice_incompatible_with_other_modes"
)
BLOCK_TRADE_FIRST_SLICE_UNIVERSE_CSV_REQUIRED = (
    "block_trade_first_slice_requires_explicit_universe_csv"
)
BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT_REQUIRED = (
    "block_trade_first_slice_output_root_must_be_cninfo_d_class_block_trade_first_slice"
)
BLOCK_TRADE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_block_trade_first_slice"
)
BLOCK_TRADE_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_block_trade_first_slice"
)
BLOCK_TRADE_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_output_root_write_blocked_for_block_trade_first_slice"
)
BLOCK_TRADE_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "targeted_probe_output_root_write_blocked_for_block_trade_first_slice"
)
BLOCK_TRADE_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED = (
    "margin_trading_first_slice_output_root_write_blocked_for_block_trade_first_slice"
)
BLOCK_TRADE_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "disclosure_schedule_first_slice_output_root_write_blocked_for_block_trade_first_slice"
)
BLOCK_TRADE_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH = (
    "block_trade_first_slice_universe_size_must_equal_5"
)
BLOCK_TRADE_FIRST_SLICE_FORBIDDEN_CASE_ID = (
    "forbidden_case_id_in_block_trade_first_slice_universe"
)
BLOCK_TRADE_FIRST_SLICE_WRONG_COMPONENT = (
    "block_trade_first_slice_component_must_be_block_trade"
)
BLOCK_TRADE_FIRST_SLICE_INCLUDE_REQUIRED = "first_slice_include_must_be_yes"
BLOCK_TRADE_FIRST_SLICE_FORBIDDEN_COMPANY_CODE = (
    "forbidden_company_code_in_block_trade_first_slice_universe"
)
BLOCK_TRADE_FIRST_SLICE_WRONG_COMPANY_CODE = (
    "block_trade_first_slice_company_code_mismatch"
)
BLOCK_TRADE_FIRST_SLICE_WRONG_ANCHOR_TDATE = (
    "block_trade_first_slice_anchor_tdate_mismatch"
)
BLOCK_TRADE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED = (
    "block_trade_first_slice_per_case_request_cap_exceeded"
)
BLOCK_TRADE_FIRST_SLICE_TOTAL_CAP_EXCEEDED = (
    "block_trade_first_slice_total_request_cap_exceeded"
)
BLOCK_TRADE_FIRST_SLICE_LIVE_NOT_IMPLEMENTED = (
    "block_trade_first_slice_live_not_implemented"
)
BLOCK_TRADE_DISCLOSURE_CAPTURED_NORMAL_BLOCKED = (
    "disclosure_only_captured_normal_upgrade_blocked"
)

DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_restricted_shares_unlock_first_slice",
)
DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv",
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_restricted_shares_unlock_first_slice_dryrun_report.csv",
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_restricted_shares_unlock_first_slice_dryrun_summary.md",
)

RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_RUNNER_GATE = "READY_FOR_APPROVAL"
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE = 5
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ALLOWED_CASE_IDS: Set[str] = {
    "DRU001",
    "DRU002",
    "DRU003",
    "DRU004",
    "DRU005",
}
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXPECTED_COMPANY_CODES: Dict[str, str] = {
    "DRU001": "300009",
    "DRU002": "000895",
    "DRU003": "600000",
    "DRU004": "002415",
    "DRU005": "688981",
}
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_FORBIDDEN_COMPANY_CODES: Set[str] = {
    "688671",
    "301259",
}
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_COMPONENT = "restricted_shares_unlock"
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ANCHOR_TDATE = "2026-06-08"
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ENDPOINT = (
    "https://www.cninfo.com.cn/data20/liftBan/detail"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_MAX_REQUESTS = 4
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TOTAL_MAX_REQUESTS = 20

RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_APPROVAL_REQUIRED = (
    "approve_d_class_restricted_shares_unlock_first_slice_required"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_APPROVAL_FLAG = (
    "wrong_approval_flag_for_restricted_shares_unlock_first_slice"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_MIXED_MODE_BLOCKED = (
    "restricted_shares_unlock_first_slice_incompatible_with_other_modes"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_UNIVERSE_CSV_REQUIRED = (
    "restricted_shares_unlock_first_slice_requires_explicit_universe_csv"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT_REQUIRED = (
    "restricted_shares_unlock_first_slice_output_root_must_be_cninfo_d_class_restricted_shares_unlock_first_slice"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_restricted_shares_unlock_first_slice"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_restricted_shares_unlock_first_slice"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_output_root_write_blocked_for_restricted_shares_unlock_first_slice"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "targeted_probe_output_root_write_blocked_for_restricted_shares_unlock_first_slice"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED = (
    "margin_trading_first_slice_output_root_write_blocked_for_restricted_shares_unlock_first_slice"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "disclosure_schedule_first_slice_output_root_write_blocked_for_restricted_shares_unlock_first_slice"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "block_trade_first_slice_output_root_write_blocked_for_restricted_shares_unlock_first_slice"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH = (
    "restricted_shares_unlock_first_slice_universe_size_must_equal_5"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_FORBIDDEN_CASE_ID = (
    "forbidden_case_id_in_restricted_shares_unlock_first_slice_universe"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_COMPONENT = (
    "restricted_shares_unlock_first_slice_component_must_be_restricted_shares_unlock"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_INCLUDE_REQUIRED = "first_slice_include_must_be_yes"
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_FORBIDDEN_COMPANY_CODE = (
    "forbidden_company_code_in_restricted_shares_unlock_first_slice_universe"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_COMPANY_CODE = (
    "restricted_shares_unlock_first_slice_company_code_mismatch"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_ANCHOR_TDATE = (
    "restricted_shares_unlock_first_slice_anchor_tdate_mismatch"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_CAP_EXCEEDED = (
    "restricted_shares_unlock_first_slice_per_case_request_cap_exceeded"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TOTAL_CAP_EXCEEDED = (
    "restricted_shares_unlock_first_slice_total_request_cap_exceeded"
)
RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_LIVE_NOT_IMPLEMENTED = (
    "restricted_shares_unlock_first_slice_live_not_implemented"
)

RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_DRYRUN_REPORT_COLUMNS = [
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

RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_LIVE_REPORT_COLUMNS = [
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

RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_QUALITY_REPORT_COLUMNS = [
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

DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_equity_pledge_first_slice",
)
DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_equity_pledge_first_slice_universe_draft.csv",
)
EQUITY_PLEDGE_FIRST_SLICE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_equity_pledge_first_slice_dryrun_report.csv",
)
EQUITY_PLEDGE_FIRST_SLICE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_equity_pledge_first_slice_dryrun_summary.md",
)

EQUITY_PLEDGE_FIRST_SLICE_RUNNER_GATE = "READY_FOR_APPROVAL"
EQUITY_PLEDGE_FIRST_SLICE_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
EQUITY_PLEDGE_FIRST_SLICE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
EQUITY_PLEDGE_FIRST_SLICE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
EQUITY_PLEDGE_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE = 5
EQUITY_PLEDGE_FIRST_SLICE_ALLOWED_CASE_IDS: Set[str] = {
    "DEP001",
    "DEP002",
    "DEP003",
    "DEP004",
    "DEP005",
}
EQUITY_PLEDGE_FIRST_SLICE_EXPECTED_COMPANY_CODES: Dict[str, str] = {
    "DEP001": "688981",
    "DEP002": "000895",
    "DEP003": "600000",
    "DEP004": "002415",
    "DEP005": "601988",
}
EQUITY_PLEDGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODES: Set[str] = {"688671", "301259"}
EQUITY_PLEDGE_FIRST_SLICE_COMPONENT = "equity_pledge"
EQUITY_PLEDGE_FIRST_SLICE_ANCHOR_TDATE = "2026-07-03"
EQUITY_PLEDGE_FIRST_SLICE_ENDPOINT = (
    "https://www.cninfo.com.cn/data20/equityPledge/list"
)
EQUITY_PLEDGE_FIRST_SLICE_PER_CASE_MAX_REQUESTS = 1
EQUITY_PLEDGE_FIRST_SLICE_TOTAL_MAX_REQUESTS = 20

EQUITY_PLEDGE_FIRST_SLICE_APPROVAL_REQUIRED = (
    "approve_d_class_equity_pledge_first_slice_required"
)
EQUITY_PLEDGE_FIRST_SLICE_WRONG_APPROVAL_FLAG = (
    "wrong_approval_flag_for_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_MIXED_MODE_BLOCKED = (
    "equity_pledge_first_slice_incompatible_with_other_modes"
)
EQUITY_PLEDGE_FIRST_SLICE_UNIVERSE_CSV_REQUIRED = (
    "equity_pledge_first_slice_requires_explicit_universe_csv"
)
EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT_REQUIRED = (
    "equity_pledge_first_slice_output_root_must_be_cninfo_d_class_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_output_root_write_blocked_for_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "targeted_probe_output_root_write_blocked_for_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED = (
    "margin_trading_first_slice_output_root_write_blocked_for_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "disclosure_schedule_first_slice_output_root_write_blocked_for_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "block_trade_first_slice_output_root_write_blocked_for_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED = (
    "restricted_shares_unlock_first_slice_output_root_write_blocked_for_equity_pledge_first_slice"
)
EQUITY_PLEDGE_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH = (
    "equity_pledge_first_slice_universe_size_must_equal_5"
)
EQUITY_PLEDGE_FIRST_SLICE_FORBIDDEN_CASE_ID = (
    "forbidden_case_id_in_equity_pledge_first_slice_universe"
)
EQUITY_PLEDGE_FIRST_SLICE_WRONG_COMPONENT = (
    "equity_pledge_first_slice_component_must_be_equity_pledge"
)
EQUITY_PLEDGE_FIRST_SLICE_INCLUDE_REQUIRED = "first_slice_include_must_be_yes"
EQUITY_PLEDGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODE = (
    "forbidden_company_code_in_equity_pledge_first_slice_universe"
)
EQUITY_PLEDGE_FIRST_SLICE_WRONG_COMPANY_CODE = (
    "equity_pledge_first_slice_company_code_mismatch"
)
EQUITY_PLEDGE_FIRST_SLICE_WRONG_ANCHOR_TDATE = (
    "equity_pledge_first_slice_anchor_tdate_mismatch"
)
EQUITY_PLEDGE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED = (
    "equity_pledge_first_slice_per_case_request_cap_exceeded"
)
EQUITY_PLEDGE_FIRST_SLICE_TOTAL_CAP_EXCEEDED = (
    "equity_pledge_first_slice_total_request_cap_exceeded"
)
EQUITY_PLEDGE_FIRST_SLICE_LIVE_NOT_IMPLEMENTED = (
    "equity_pledge_first_slice_live_not_implemented"
)

EQUITY_PLEDGE_FIRST_SLICE_DRYRUN_REPORT_COLUMNS = [
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

EQUITY_PLEDGE_FIRST_SLICE_LIVE_REPORT_COLUMNS = [
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

EQUITY_PLEDGE_FIRST_SLICE_QUALITY_REPORT_COLUMNS = [
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


DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_shareholder_change_first_slice",
)
DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv",
)
SHAREHOLDER_CHANGE_FIRST_SLICE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_shareholder_change_first_slice_dryrun_report.csv",
)
SHAREHOLDER_CHANGE_FIRST_SLICE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_shareholder_change_first_slice_dryrun_summary.md",
)

SHAREHOLDER_CHANGE_FIRST_SLICE_RUNNER_GATE = "READY_FOR_APPROVAL"
SHAREHOLDER_CHANGE_FIRST_SLICE_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
SHAREHOLDER_CHANGE_FIRST_SLICE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
SHAREHOLDER_CHANGE_FIRST_SLICE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
SHAREHOLDER_CHANGE_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE = 5
SHAREHOLDER_CHANGE_FIRST_SLICE_ALLOWED_CASE_IDS: Set[str] = {
    "DSC001",
    "DSC002",
    "DSC003",
    "DSC004",
    "DSC005",
}
SHAREHOLDER_CHANGE_FIRST_SLICE_EXPECTED_COMPANY_CODES: Dict[str, str] = {
    "DSC001": "000550",
    "DSC002": "000895",
    "DSC003": "600000",
    "DSC004": "002415",
    "DSC005": "601988",
}
SHAREHOLDER_CHANGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODES: Set[str] = {
    "688671",
    "301259",
}
SHAREHOLDER_CHANGE_FIRST_SLICE_COMPONENT = "shareholder_change"
SHAREHOLDER_CHANGE_FIRST_SLICE_ANCHOR_TDATE = "2026-07-03"
SHAREHOLDER_CHANGE_FIRST_SLICE_QUERY_TYPE = "inc"
SHAREHOLDER_CHANGE_FIRST_SLICE_ENDPOINT = (
    "https://www.cninfo.com.cn/data20/shareholeder/detail"
)
# 计划每案 1 请求；live 硬顶 per-case<=4 · total<=20
SHAREHOLDER_CHANGE_FIRST_SLICE_PER_CASE_MAX_REQUESTS = 4
SHAREHOLDER_CHANGE_FIRST_SLICE_TOTAL_MAX_REQUESTS = 20

SHAREHOLDER_CHANGE_FIRST_SLICE_APPROVAL_REQUIRED = (
    "approve_d_class_shareholder_change_first_slice_required"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_APPROVAL_FLAG = (
    "wrong_approval_flag_for_shareholder_change_first_slice"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_MIXED_MODE_BLOCKED = (
    "shareholder_change_first_slice_incompatible_with_other_modes"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_UNIVERSE_CSV_REQUIRED = (
    "shareholder_change_first_slice_requires_explicit_universe_csv"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT_REQUIRED = (
    "shareholder_change_first_slice_output_root_must_be_cninfo_d_class_shareholder_change_first_slice"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_shareholder_change_first_slice"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_shareholder_change_first_slice"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_output_root_write_blocked_for_shareholder_change_first_slice"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "targeted_probe_output_root_write_blocked_for_shareholder_change_first_slice"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "equity_pledge_first_slice_output_root_write_blocked"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED = (
    "margin_trading_first_slice_output_root_write_blocked"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "disclosure_schedule_first_slice_output_root_write_blocked"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "block_trade_first_slice_output_root_write_blocked"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED = (
    "rsu_first_slice_output_root_write_blocked"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH = (
    "shareholder_change_first_slice_universe_size_must_equal_5"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_FORBIDDEN_CASE_ID = (
    "forbidden_case_id_in_shareholder_change_first_slice_universe"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_COMPONENT = (
    "shareholder_change_first_slice_component_must_be_shareholder_change"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_INCLUDE_REQUIRED = "first_slice_include_must_be_yes"
SHAREHOLDER_CHANGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODE = (
    "forbidden_company_code_in_shareholder_change_first_slice_universe"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_COMPANY_CODE = (
    "shareholder_change_first_slice_company_code_mismatch"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_ANCHOR_TDATE = (
    "shareholder_change_first_slice_anchor_tdate_mismatch"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_QUERY_TYPE = (
    "shareholder_change_first_slice_query_type_must_be_inc"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED = (
    "shareholder_change_first_slice_per_case_request_cap_exceeded"
)
SHAREHOLDER_CHANGE_FIRST_SLICE_TOTAL_CAP_EXCEEDED = (
    "shareholder_change_first_slice_total_request_cap_exceeded"
)

SHAREHOLDER_CHANGE_FIRST_SLICE_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "anchor_tdate",
    "query_type",
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

SHAREHOLDER_CHANGE_FIRST_SLICE_LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "anchor_tdate",
    "query_type",
    "expected_behavior",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "record_count",
    "empty_but_valid",
    "needs_review",
    "endpoint_used",
    "cninfo_request_count",
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

SHAREHOLDER_CHANGE_FIRST_SLICE_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "component",
    "anchor_tdate",
    "query_type",
    "expected_behavior",
    "retrieval_status",
    "record_count",
    "quality_status",
    "acceptable",
    "failure_type",
    "cninfo_request_count",
    "notes",
]


DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_executive_shareholding_first_slice",
)
DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv",
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FIXTURE_DIR = os.path.join(
    BASE_DIR,
    "fixtures",
    "d_class",
    "executive_shareholding_first_slice",
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_executive_shareholding_first_slice_dryrun_report.csv",
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_executive_shareholding_first_slice_dryrun_summary.md",
)

EXECUTIVE_SHAREHOLDING_FIRST_SLICE_RUNNER_GATE = "READY_FOR_APPROVAL"
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE = 5
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ALLOWED_CASE_IDS: Set[str] = {
    "DES001",
    "DES002",
    "DES003",
    "DES004",
    "DES005",
}
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXPECTED_COMPANY_CODES: Dict[str, str] = {
    "DES001": "002415",
    "DES002": "000895",
    "DES003": "600000",
    "DES004": "000550",
    "DES005": "601988",
}
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FORBIDDEN_COMPANY_CODES: Set[str] = {
    "688671",
    "301259",
}
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_COMPONENT = "executive_shareholding"
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TIME_MARK = "oneMonth"
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_VARY_TYPE = "b"
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ENDPOINT = (
    "https://www.cninfo.com.cn/data20/leader/detail"
)
# 计划每案 1 请求（oneMonth+b）；live 硬顶 per-case<=4 · total<=20
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_PER_CASE_MAX_REQUESTS = 4
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TOTAL_MAX_REQUESTS = 20

# Tier-1 synthetic fixtures（DES001–DES005）· dry-run planned_snapshots 接线
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_CASE_FIXTURES: Dict[str, Tuple[str, ...]] = {
    "DES001": ("DES001_needs_review_synthetic.json",),
    "DES002": ("DES002_found.json", "DES002_empty.json"),
    "DES003": ("DES003_found.json", "DES003_empty.json"),
    "DES004": ("DES004_found.json", "DES004_empty.json"),
    "DES005": ("DES005_empty_but_valid_synthetic.json",),
}

EXECUTIVE_SHAREHOLDING_FIRST_SLICE_APPROVAL_REQUIRED = (
    "approve_d_class_executive_shareholding_first_slice_required"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_APPROVAL_FLAG = (
    "wrong_approval_flag_for_executive_shareholding_first_slice"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_MIXED_MODE_BLOCKED = (
    "executive_shareholding_first_slice_incompatible_with_other_modes"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_UNIVERSE_CSV_REQUIRED = (
    "executive_shareholding_first_slice_requires_explicit_universe_csv"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT_REQUIRED = (
    "executive_shareholding_first_slice_output_root_must_be_cninfo_d_class_executive_shareholding_first_slice"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_executive_shareholding_first_slice"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_executive_shareholding_first_slice"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_output_root_write_blocked_for_executive_shareholding_first_slice"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "targeted_probe_output_root_write_blocked_for_executive_shareholding_first_slice"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_SHAREHOLDER_CHANGE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "shareholder_change_first_slice_output_root_write_blocked"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "equity_pledge_first_slice_output_root_write_blocked"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED = (
    "margin_trading_first_slice_output_root_write_blocked"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "disclosure_schedule_first_slice_output_root_write_blocked"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "block_trade_first_slice_output_root_write_blocked"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED = (
    "rsu_first_slice_output_root_write_blocked"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH = (
    "executive_shareholding_first_slice_universe_size_must_equal_5"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FORBIDDEN_CASE_ID = (
    "forbidden_case_id_in_executive_shareholding_first_slice_universe"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_COMPONENT = (
    "executive_shareholding_first_slice_component_must_be_executive_shareholding"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_INCLUDE_REQUIRED = "first_slice_include_must_be_yes"
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE = (
    "forbidden_company_code_in_executive_shareholding_first_slice_universe"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_COMPANY_CODE = (
    "executive_shareholding_first_slice_company_code_mismatch"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_TIME_MARK = (
    "executive_shareholding_first_slice_time_mark_must_be_oneMonth"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_VARY_TYPE = (
    "executive_shareholding_first_slice_vary_type_must_be_b"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED = (
    "executive_shareholding_first_slice_per_case_request_cap_exceeded"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TOTAL_CAP_EXCEEDED = (
    "executive_shareholding_first_slice_total_request_cap_exceeded"
)
EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FIXTURE_MISSING = (
    "executive_shareholding_first_slice_tier1_fixture_missing"
)

EXECUTIVE_SHAREHOLDING_FIRST_SLICE_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "time_mark",
    "vary_type",
    "first_slice_include",
    "expected_behavior",
    "planned_request_count",
    "planned_output_root",
    "planned_endpoint",
    "fixture_refs",
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

EXECUTIVE_SHAREHOLDING_FIRST_SLICE_LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "time_mark",
    "vary_type",
    "expected_behavior",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "record_count",
    "empty_but_valid",
    "needs_review",
    "endpoint_used",
    "cninfo_request_count",
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

EXECUTIVE_SHAREHOLDING_FIRST_SLICE_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "component",
    "time_mark",
    "vary_type",
    "expected_behavior",
    "retrieval_status",
    "record_count",
    "quality_status",
    "acceptable",
    "failure_type",
    "cninfo_request_count",
    "notes",
]


DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_abnormal_trading_first_slice",
)
DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv",
)
ABNORMAL_TRADING_FIRST_SLICE_FIXTURE_DIR = os.path.join(
    BASE_DIR,
    "fixtures",
    "d_class",
    "abnormal_trading_first_slice",
)
ABNORMAL_TRADING_FIRST_SLICE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_abnormal_trading_first_slice_dryrun_report.csv",
)
ABNORMAL_TRADING_FIRST_SLICE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_abnormal_trading_first_slice_dryrun_summary.md",
)

ABNORMAL_TRADING_FIRST_SLICE_RUNNER_GATE = "READY_FOR_APPROVAL"
ABNORMAL_TRADING_FIRST_SLICE_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
ABNORMAL_TRADING_FIRST_SLICE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
ABNORMAL_TRADING_FIRST_SLICE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
ABNORMAL_TRADING_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE = 5
ABNORMAL_TRADING_FIRST_SLICE_ALLOWED_CASE_IDS: Set[str] = {
    "DAT001",
    "DAT002",
    "DAT003",
    "DAT004",
    "DAT005",
}
ABNORMAL_TRADING_FIRST_SLICE_EXPECTED_COMPANY_CODES: Dict[str, str] = {
    "DAT001": "000004",
    "DAT002": "000895",
    "DAT003": "600000",
    "DAT004": "002415",
    "DAT005": "601988",
}
ABNORMAL_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODES: Set[str] = {
    "688671",
    "301259",
}
ABNORMAL_TRADING_FIRST_SLICE_COMPONENT = "abnormal_trading"
ABNORMAL_TRADING_FIRST_SLICE_ANCHOR_TDATE = "2026-07-03"
ABNORMAL_TRADING_FIRST_SLICE_ENDPOINT = (
    "https://www.cninfo.com.cn/data/statis/getMarketStatisticsData"
)
ABNORMAL_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS = 1
ABNORMAL_TRADING_FIRST_SLICE_TOTAL_MAX_REQUESTS = 20
ABNORMAL_TRADING_FIRST_SLICE_CASE_FIXTURES: Dict[str, Tuple[str, ...]] = {
    "DAT001": ("DAT001_needs_review_synthetic.json",),
    "DAT002": ("DAT002_found.json", "DAT002_empty.json"),
    "DAT003": ("DAT003_found.json", "DAT003_empty.json"),
    "DAT004": ("DAT004_found.json", "DAT004_empty.json"),
    "DAT005": ("DAT005_empty_but_valid_synthetic.json",),
}

ABNORMAL_TRADING_FIRST_SLICE_APPROVAL_REQUIRED = (
    "approve_d_class_abnormal_trading_first_slice_required"
)
ABNORMAL_TRADING_FIRST_SLICE_WRONG_APPROVAL_FLAG = (
    "wrong_approval_flag_for_abnormal_trading_first_slice"
)
ABNORMAL_TRADING_FIRST_SLICE_MIXED_MODE_BLOCKED = (
    "abnormal_trading_first_slice_incompatible_with_other_modes"
)
ABNORMAL_TRADING_FIRST_SLICE_UNIVERSE_CSV_REQUIRED = (
    "abnormal_trading_first_slice_requires_explicit_universe_csv"
)
ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT_REQUIRED = (
    "abnormal_trading_first_slice_output_root_must_be_cninfo_d_class_abnormal_trading_first_slice"
)
ABNORMAL_TRADING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_abnormal_trading_first_slice"
)
ABNORMAL_TRADING_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_abnormal_trading_first_slice"
)
ABNORMAL_TRADING_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_output_root_write_blocked_for_abnormal_trading_first_slice"
)
ABNORMAL_TRADING_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "targeted_probe_output_root_write_blocked_for_abnormal_trading_first_slice"
)
ABNORMAL_TRADING_FIRST_SLICE_EXECUTIVE_SHAREHOLDING_OUTPUT_ROOT_WRITE_BLOCKED = (
    "executive_shareholding_first_slice_output_root_write_blocked"
)
ABNORMAL_TRADING_FIRST_SLICE_SHAREHOLDER_CHANGE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "shareholder_change_first_slice_output_root_write_blocked"
)
ABNORMAL_TRADING_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "equity_pledge_first_slice_output_root_write_blocked"
)
ABNORMAL_TRADING_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED = (
    "margin_trading_first_slice_output_root_write_blocked"
)
ABNORMAL_TRADING_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "disclosure_schedule_first_slice_output_root_write_blocked"
)
ABNORMAL_TRADING_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "block_trade_first_slice_output_root_write_blocked"
)
ABNORMAL_TRADING_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED = (
    "restricted_shares_unlock_first_slice_output_root_write_blocked"
)
ABNORMAL_TRADING_FIRST_SLICE_SHAREHOLDER_DATA_OUTPUT_ROOT_WRITE_BLOCKED = (
    "shareholder_data_first_slice_output_root_write_blocked"
)
ABNORMAL_TRADING_FIRST_SLICE_FUND_INDUSTRY_ALLOCATION_OUTPUT_ROOT_WRITE_BLOCKED = (
    "fund_industry_allocation_first_slice_output_root_write_blocked"
)
ABNORMAL_TRADING_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH = (
    "abnormal_trading_first_slice_universe_size_must_equal_5"
)
ABNORMAL_TRADING_FIRST_SLICE_FORBIDDEN_CASE_ID = (
    "forbidden_case_id_in_abnormal_trading_first_slice_universe"
)
ABNORMAL_TRADING_FIRST_SLICE_WRONG_COMPONENT = (
    "abnormal_trading_first_slice_component_must_be_abnormal_trading"
)
ABNORMAL_TRADING_FIRST_SLICE_INCLUDE_REQUIRED = "first_slice_include_must_be_yes"
ABNORMAL_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE = (
    "forbidden_company_code_in_abnormal_trading_first_slice_universe"
)
ABNORMAL_TRADING_FIRST_SLICE_WRONG_COMPANY_CODE = (
    "abnormal_trading_first_slice_company_code_mismatch"
)
ABNORMAL_TRADING_FIRST_SLICE_WRONG_ANCHOR_TDATE = (
    "abnormal_trading_first_slice_anchor_tdate_mismatch"
)
ABNORMAL_TRADING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED = (
    "abnormal_trading_first_slice_per_case_request_cap_exceeded"
)
ABNORMAL_TRADING_FIRST_SLICE_TOTAL_CAP_EXCEEDED = (
    "abnormal_trading_first_slice_total_request_cap_exceeded"
)
ABNORMAL_TRADING_FIRST_SLICE_FIXTURE_MISSING = (
    "abnormal_trading_first_slice_tier1_fixture_missing"
)
ABNORMAL_TRADING_FIRST_SLICE_LIVE_NOT_IMPLEMENTED = (
    "abnormal_trading_first_slice_live_not_implemented"
)

ABNORMAL_TRADING_FIRST_SLICE_DRYRUN_REPORT_COLUMNS = [
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
    "fixture_refs",
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

ABNORMAL_TRADING_FIRST_SLICE_LIVE_REPORT_COLUMNS = [
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

ABNORMAL_TRADING_FIRST_SLICE_QUALITY_REPORT_COLUMNS = [
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


DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_shareholder_data_first_slice",
)
DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv",
)
SHAREHOLDER_DATA_FIRST_SLICE_FIXTURE_DIR = os.path.join(
    BASE_DIR,
    "fixtures",
    "d_class",
    "shareholder_data_first_slice",
)
SHAREHOLDER_DATA_FIRST_SLICE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_shareholder_data_first_slice_dryrun_report.csv",
)
SHAREHOLDER_DATA_FIRST_SLICE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_shareholder_data_first_slice_dryrun_summary.md",
)

SHAREHOLDER_DATA_FIRST_SLICE_RUNNER_GATE = "READY_FOR_APPROVAL"
SHAREHOLDER_DATA_FIRST_SLICE_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
SHAREHOLDER_DATA_FIRST_SLICE_LIVE_GATE = "NOT_APPROVED"
SHAREHOLDER_DATA_FIRST_SLICE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
SHAREHOLDER_DATA_FIRST_SLICE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
SHAREHOLDER_DATA_FIRST_SLICE_SHARED_REQUEST_CASE_ID = "SHARED_RDATE"
SHAREHOLDER_DATA_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE = 5
SHAREHOLDER_DATA_FIRST_SLICE_ALLOWED_CASE_IDS: Set[str] = {
    "DSD001",
    "DSD002",
    "DSD003",
    "DSD004",
    "DSD005",
}
SHAREHOLDER_DATA_FIRST_SLICE_EXPECTED_COMPANY_CODES: Dict[str, str] = {
    "DSD001": "000001",
    "DSD002": "000895",
    "DSD003": "600000",
    "DSD004": "002415",
    "DSD005": "000004",
}
SHAREHOLDER_DATA_FIRST_SLICE_FORBIDDEN_COMPANY_CODES: Set[str] = {
    "688671",
    "301259",
}
SHAREHOLDER_DATA_FIRST_SLICE_COMPONENT = "shareholder_data"
SHAREHOLDER_DATA_FIRST_SLICE_ANCHOR_RDATE = "20260331"
SHAREHOLDER_DATA_FIRST_SLICE_QUERY_MODE = "rdate_report_period"
SHAREHOLDER_DATA_FIRST_SLICE_ENDPOINT = (
    "https://www.cninfo.com.cn/data20/shareholeder/data"
)
SHAREHOLDER_DATA_FIRST_SLICE_RECORDS_PATH = "data.records"
SHAREHOLDER_DATA_FIRST_SLICE_PER_CASE_MAX_REQUESTS = 1
SHAREHOLDER_DATA_FIRST_SLICE_TOTAL_MAX_REQUESTS = 5
SHAREHOLDER_DATA_FIRST_SLICE_PLANNED_SHARED_REQUESTS = 1
SHAREHOLDER_DATA_FIRST_SLICE_CASE_FIXTURES: Dict[str, Tuple[str, ...]] = {
    "DSD001": ("DSD001_found.json",),
    "DSD002": ("DSD002_found.json", "DSD002_empty.json"),
    "DSD003": (
        "DSD003_found.json",
        "DSD003_empty.json",
        "DSD003_records_filtered_empty.json",
    ),
    "DSD004": ("DSD004_found.json", "DSD004_empty.json"),
    "DSD005": ("DSD005_empty_but_valid_synthetic.json",),
}

SHAREHOLDER_DATA_FIRST_SLICE_APPROVAL_REQUIRED = (
    "approve_d_class_shareholder_data_first_slice_required"
)
SHAREHOLDER_DATA_FIRST_SLICE_WRONG_APPROVAL_FLAG = (
    "wrong_approval_flag_for_shareholder_data_first_slice"
)
SHAREHOLDER_DATA_FIRST_SLICE_MIXED_MODE_BLOCKED = (
    "shareholder_data_first_slice_incompatible_with_other_modes"
)
SHAREHOLDER_DATA_FIRST_SLICE_UNIVERSE_CSV_REQUIRED = (
    "shareholder_data_first_slice_requires_explicit_universe_csv"
)
SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT_REQUIRED = (
    "shareholder_data_first_slice_output_root_must_be_cninfo_d_class_shareholder_data_first_slice"
)
SHAREHOLDER_DATA_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_shareholder_data_first_slice"
)
SHAREHOLDER_DATA_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_shareholder_data_first_slice"
)
SHAREHOLDER_DATA_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_output_root_write_blocked_for_shareholder_data_first_slice"
)
SHAREHOLDER_DATA_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "targeted_probe_output_root_write_blocked_for_shareholder_data_first_slice"
)
SHAREHOLDER_DATA_FIRST_SLICE_EXECUTIVE_SHAREHOLDING_OUTPUT_ROOT_WRITE_BLOCKED = (
    "executive_shareholding_first_slice_output_root_write_blocked"
)
SHAREHOLDER_DATA_FIRST_SLICE_SHAREHOLDER_CHANGE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "shareholder_change_first_slice_output_root_write_blocked"
)
SHAREHOLDER_DATA_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "equity_pledge_first_slice_output_root_write_blocked"
)
SHAREHOLDER_DATA_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED = (
    "margin_trading_first_slice_output_root_write_blocked"
)
SHAREHOLDER_DATA_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "disclosure_schedule_first_slice_output_root_write_blocked"
)
SHAREHOLDER_DATA_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "block_trade_first_slice_output_root_write_blocked"
)
SHAREHOLDER_DATA_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED = (
    "restricted_shares_unlock_first_slice_output_root_write_blocked"
)
SHAREHOLDER_DATA_FIRST_SLICE_ABNORMAL_TRADING_OUTPUT_ROOT_WRITE_BLOCKED = (
    "abnormal_trading_first_slice_output_root_write_blocked"
)
SHAREHOLDER_DATA_FIRST_SLICE_FUND_INDUSTRY_ALLOCATION_OUTPUT_ROOT_WRITE_BLOCKED = (
    "fund_industry_allocation_first_slice_output_root_write_blocked"
)
SHAREHOLDER_DATA_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH = (
    "shareholder_data_first_slice_universe_size_must_equal_5"
)
SHAREHOLDER_DATA_FIRST_SLICE_FORBIDDEN_CASE_ID = (
    "forbidden_case_id_in_shareholder_data_first_slice_universe"
)
SHAREHOLDER_DATA_FIRST_SLICE_WRONG_COMPONENT = (
    "shareholder_data_first_slice_component_must_be_shareholder_data"
)
SHAREHOLDER_DATA_FIRST_SLICE_INCLUDE_REQUIRED = "first_slice_include_must_be_yes"
SHAREHOLDER_DATA_FIRST_SLICE_FORBIDDEN_COMPANY_CODE = (
    "forbidden_company_code_in_shareholder_data_first_slice_universe"
)
SHAREHOLDER_DATA_FIRST_SLICE_WRONG_COMPANY_CODE = (
    "shareholder_data_first_slice_company_code_mismatch"
)
SHAREHOLDER_DATA_FIRST_SLICE_WRONG_ANCHOR_RDATE = (
    "shareholder_data_first_slice_anchor_rdate_mismatch"
)
SHAREHOLDER_DATA_FIRST_SLICE_PER_CASE_CAP_EXCEEDED = (
    "shareholder_data_first_slice_per_case_request_cap_exceeded"
)
SHAREHOLDER_DATA_FIRST_SLICE_TOTAL_CAP_EXCEEDED = (
    "shareholder_data_first_slice_total_request_cap_exceeded"
)
SHAREHOLDER_DATA_FIRST_SLICE_SHARED_PLAN_MISMATCH = (
    "shareholder_data_first_slice_shared_plan_must_equal_1"
)
SHAREHOLDER_DATA_FIRST_SLICE_FIXTURE_MISSING = (
    "shareholder_data_first_slice_tier1_fixture_missing"
)
SHAREHOLDER_DATA_FIRST_SLICE_LIVE_NOT_IMPLEMENTED = (
    "shareholder_data_first_slice_live_not_implemented"
)
SHAREHOLDER_DATA_FIRST_SLICE_SHARED_REQUEST_REQUIRED = (
    "shareholder_data_first_slice_shared_request_required"
)

SHAREHOLDER_DATA_FIRST_SLICE_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "anchor_rdate",
    "first_slice_include",
    "expected_behavior",
    "planned_request_count",
    "planned_output_root",
    "planned_endpoint",
    "fixture_refs",
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

SHAREHOLDER_DATA_FIRST_SLICE_LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "anchor_rdate",
    "expected_behavior",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "record_count",
    "empty_but_valid",
    "needs_review",
    "endpoint_used",
    "cninfo_request_count",
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

SHAREHOLDER_DATA_FIRST_SLICE_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "component",
    "anchor_rdate",
    "expected_behavior",
    "retrieval_status",
    "record_count",
    "quality_status",
    "acceptable",
    "failure_type",
    "cninfo_request_count",
    "notes",
]



DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_fund_industry_allocation_first_slice",
)
DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv",
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FIXTURE_DIR = os.path.join(
    BASE_DIR,
    "fixtures",
    "d_class",
    "fund_industry_allocation_first_slice",
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_fund_industry_allocation_first_slice_dryrun_report.csv",
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT,
    "reports",
    "d_class_fund_industry_allocation_first_slice_dryrun_summary.md",
)

FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_RUNNER_GATE = "READY_FOR_APPROVAL"
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_GATE = "NOT_APPROVED"
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXECUTION_GATE_FAIL = "FAIL_REVIEW_REQUIRED"
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE = 5
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ALLOWED_CASE_IDS: Set[str] = {
    "DFIA001",
    "DFIA002",
    "DFIA003",
    "DFIA004",
    "DFIA005",
}
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXPECTED_INDUSTRY_CODES: Dict[str, str] = {
    "DFIA001": "C26",
    "DFIA002": "*",
    "DFIA003": "*",
    "DFIA004": "C26",
    "DFIA005": "*",
}
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXPECTED_QUERY_MODES: Dict[str, str] = {
    "DFIA001": "default",
    "DFIA002": "default",
    "DFIA003": "rdate",
    "DFIA004": "rdate",
    "DFIA005": "rdate",
}
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXPECTED_ANCHOR_RDATES: Dict[str, str] = {
    "DFIA001": "",
    "DFIA002": "",
    "DFIA003": "20260331",
    "DFIA004": "20260331",
    "DFIA005": "20251231",
}
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FORBIDDEN_COMPANY_CODES: Set[str] = {
    "688671",
    "301259",
}
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_COMPONENT = "fund_industry_allocation"
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ENDPOINT = (
    "https://www.cninfo.com.cn/data20/fund/industry"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_RECORDS_PATH = "data.records"
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PER_CASE_MAX_REQUESTS = 1
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TOTAL_MAX_REQUESTS = 5
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PLANNED_SHARED_REQUESTS = 3
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_PROBE_KEYS: Tuple[str, ...] = (
    "default",
    "rdate_20260331",
    "rdate_20251231",
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_CASE_FIXTURES: Dict[str, Tuple[str, ...]] = {
    "DFIA001": ("DFIA001_found.json",),
    "DFIA002": ("DFIA002_found.json",),
    "DFIA003": ("DFIA003_found.json",),
    "DFIA004": (
        "DFIA004_found.json",
        "DFIA004_empty.json",
        "DFIA004_industry_filtered_empty.json",
    ),
    "DFIA005": ("DFIA005_empty_but_valid_synthetic.json",),
}

FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_APPROVAL_REQUIRED = (
    "approve_d_class_fund_industry_allocation_first_slice_required"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_APPROVAL_FLAG = (
    "wrong_approval_flag_for_fund_industry_allocation_first_slice"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_MIXED_MODE_BLOCKED = (
    "fund_industry_allocation_first_slice_incompatible_with_other_modes"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_UNIVERSE_CSV_REQUIRED = (
    "fund_industry_allocation_first_slice_requires_explicit_universe_csv"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT_REQUIRED = (
    "fund_industry_allocation_first_slice_output_root_must_be_cninfo_d_class_fund_industry_allocation_first_slice"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v1_output_root_write_blocked_for_fund_industry_allocation_first_slice"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED = (
    "v2_output_root_write_blocked_for_fund_industry_allocation_first_slice"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED = (
    "replacement_output_root_write_blocked_for_fund_industry_allocation_first_slice"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "targeted_probe_output_root_write_blocked_for_fund_industry_allocation_first_slice"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXECUTIVE_SHAREHOLDING_OUTPUT_ROOT_WRITE_BLOCKED = (
    "executive_shareholding_first_slice_output_root_write_blocked"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHAREHOLDER_CHANGE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "shareholder_change_first_slice_output_root_write_blocked"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "equity_pledge_first_slice_output_root_write_blocked"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED = (
    "margin_trading_first_slice_output_root_write_blocked"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "disclosure_schedule_first_slice_output_root_write_blocked"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED = (
    "block_trade_first_slice_output_root_write_blocked"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED = (
    "restricted_shares_unlock_first_slice_output_root_write_blocked"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ABNORMAL_TRADING_OUTPUT_ROOT_WRITE_BLOCKED = (
    "abnormal_trading_first_slice_output_root_write_blocked"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHAREHOLDER_DATA_OUTPUT_ROOT_WRITE_BLOCKED = (
    "shareholder_data_first_slice_output_root_write_blocked"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH = (
    "fund_industry_allocation_first_slice_universe_size_must_equal_5"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FORBIDDEN_CASE_ID = (
    "forbidden_case_id_in_fund_industry_allocation_first_slice_universe"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_COMPONENT = (
    "fund_industry_allocation_first_slice_component_must_be_fund_industry_allocation"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_INCLUDE_REQUIRED = "first_slice_include_must_be_yes"
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FORBIDDEN_COMPANY_CODE = (
    "forbidden_company_code_in_fund_industry_allocation_first_slice_universe"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_INDUSTRY_CODE = (
    "fund_industry_allocation_first_slice_industry_code_mismatch"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_QUERY_MODE = (
    "fund_industry_allocation_first_slice_query_mode_mismatch"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_ANCHOR_RDATE = (
    "fund_industry_allocation_first_slice_anchor_rdate_mismatch"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PER_CASE_CAP_EXCEEDED = (
    "fund_industry_allocation_first_slice_per_case_request_cap_exceeded"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TOTAL_CAP_EXCEEDED = (
    "fund_industry_allocation_first_slice_total_request_cap_exceeded"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_PLAN_MISMATCH = (
    "fund_industry_allocation_first_slice_shared_plan_must_equal_3"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FIXTURE_MISSING = (
    "fund_industry_allocation_first_slice_tier1_fixture_missing"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_REQUEST_REQUIRED = (
    "fund_industry_allocation_first_slice_shared_request_required"
)
FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_COMPANY_CODE_FORBIDDEN = (
    "fund_industry_allocation_first_slice_company_code_field_forbidden"
)

FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_DRYRUN_REPORT_COLUMNS = [
    "case_id",
    "industry_code",
    "industry_name",
    "component",
    "query_mode",
    "anchor_rdate",
    "first_slice_include",
    "expected_behavior",
    "planned_request_count",
    "shared_probe_key",
    "planned_output_root",
    "planned_endpoint",
    "fixture_refs",
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

FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_REPORT_COLUMNS = [
    "case_id",
    "industry_code",
    "industry_name",
    "component",
    "query_mode",
    "anchor_rdate",
    "expected_behavior",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "record_count",
    "empty_but_valid",
    "needs_review",
    "endpoint_used",
    "cninfo_request_count",
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

FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_QUALITY_REPORT_COLUMNS = [
    "case_id",
    "component",
    "query_mode",
    "anchor_rdate",
    "expected_behavior",
    "retrieval_status",
    "record_count",
    "quality_status",
    "acceptable",
    "failure_type",
    "cninfo_request_count",
    "notes",
]


BLOCK_TRADE_FIRST_SLICE_DRYRUN_REPORT_COLUMNS = [
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

BLOCK_TRADE_FIRST_SLICE_LIVE_REPORT_COLUMNS = [
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

BLOCK_TRADE_FIRST_SLICE_QUALITY_REPORT_COLUMNS = [
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
class BlockTradeFirstSliceRow:
    case_id: str
    company_code: str
    company_name: str
    component: str
    market: str
    anchor_tdate: str
    first_slice_include: str
    expected_behavior: str
    reason: str
    dlc002_reference: str


@dataclass
class RestrictedSharesUnlockFirstSliceRow:
    case_id: str
    company_code: str
    company_name: str
    component: str
    market: str
    anchor_tdate: str
    first_slice_include: str
    expected_behavior: str
    exclude_flags: str
    notes: str
    dlc003_reference: str


@dataclass
class EquityPledgeFirstSliceRow:
    case_id: str
    company_code: str
    company_name: str
    component: str
    market: str
    anchor_tdate: str
    first_slice_include: str
    expected_behavior: str
    exclude_flags: str
    notes: str
    dlc005_reference: str


@dataclass
class ShareholderChangeFirstSliceRow:
    case_id: str
    company_code: str
    company_name: str
    component: str
    market: str
    anchor_tdate: str
    query_type: str
    first_slice_include: str
    expected_behavior: str
    exclude_flags: str
    notes: str
    dlc006_reference: str


@dataclass
class ExecutiveShareholdingFirstSliceRow:
    case_id: str
    company_code: str
    company_name: str
    component: str
    market: str
    time_mark: str
    vary_type: str
    first_slice_include: str
    expected_behavior: str
    exclude_flags: str
    notes: str
    dlc007_reference: str



@dataclass
class AbnormalTradingFirstSliceRow:
    case_id: str
    company_code: str
    company_name: str
    component: str
    market: str
    anchor_tdate: str
    first_slice_include: str
    expected_behavior: str
    exclude_flags: str
    notes: str
    sample_raw_reference: str


@dataclass
class ShareholderDataFirstSliceRow:
    case_id: str
    company_code: str
    company_name: str
    component: str
    market: str
    anchor_rdate: str
    first_slice_include: str
    expected_behavior: str
    exclude_flags: str
    notes: str
    sample_raw_reference: str



@dataclass
class FundIndustryAllocationFirstSliceRow:
    case_id: str
    probe_key: str
    industry_code: str
    industry_name: str
    component: str
    query_mode: str
    anchor_rdate: str
    first_slice_include: str
    expected_behavior: str
    exclude_flags: str
    notes: str
    sample_raw_reference: str


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
        ("block_trade_first_slice", args.block_trade_first_slice),
        ("restricted_shares_unlock_first_slice", args.restricted_shares_unlock_first_slice),
        ("equity_pledge_first_slice", args.equity_pledge_first_slice),
        ("shareholder_change_first_slice", args.shareholder_change_first_slice),
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
        (
            "approve_d_class_block_trade_first_slice",
            args.approve_d_class_block_trade_first_slice,
        ),
        (
            "approve_d_class_restricted_shares_unlock_first_slice",
            args.approve_d_class_restricted_shares_unlock_first_slice,
        ),
        (
            "approve_d_class_equity_pledge_first_slice",
            args.approve_d_class_equity_pledge_first_slice,
        ),
        (
            "approve_d_class_shareholder_change_first_slice",
            args.approve_d_class_shareholder_change_first_slice,
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


def load_block_trade_first_slice_universe(path: str) -> List[BlockTradeFirstSliceRow]:
    rows: List[BlockTradeFirstSliceRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                BlockTradeFirstSliceRow(
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
                    dlc002_reference=str(row.get("dlc002_reference", "")).strip(),
                )
            )
    return rows


def build_block_trade_first_slice_plan(
    anchor_tdate: str,
    max_requests: int = BLOCK_TRADE_FIRST_SLICE_PER_CASE_MAX_REQUESTS,
) -> List[str]:
    """block_trade 第一切片 dry-run 请求计划（tdate_daily · 仅计数）。"""
    return [f"tdate_daily_{anchor_tdate}"][:max_requests]


def compute_block_trade_first_slice_planned_requests(
    row: BlockTradeFirstSliceRow,
) -> int:
    plan = build_block_trade_first_slice_plan(row.anchor_tdate)
    return len(plan)


def validate_block_trade_first_slice_universe(
    rows: List[BlockTradeFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    if len(rows) != BLOCK_TRADE_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE:
        issues.append(
            f"{BLOCK_TRADE_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH}:got={len(rows)}"
        )
    seen_ids: Set[str] = set()
    total_planned = 0
    for row in rows:
        case_id = row.case_id
        if case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_ids.add(case_id)
        if case_id not in BLOCK_TRADE_FIRST_SLICE_ALLOWED_CASE_IDS:
            issues.append(f"{BLOCK_TRADE_FIRST_SLICE_FORBIDDEN_CASE_ID}:{case_id}")
        if row.company_code in BLOCK_TRADE_FIRST_SLICE_FORBIDDEN_COMPANY_CODES:
            issues.append(
                f"{BLOCK_TRADE_FIRST_SLICE_FORBIDDEN_COMPANY_CODE}:{row.company_code}"
            )
        expected_code = BLOCK_TRADE_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(case_id)
        if expected_code and row.company_code != expected_code:
            issues.append(
                f"{BLOCK_TRADE_FIRST_SLICE_WRONG_COMPANY_CODE}:{case_id}={row.company_code}"
            )
        if row.component != BLOCK_TRADE_FIRST_SLICE_COMPONENT:
            issues.append(f"{BLOCK_TRADE_FIRST_SLICE_WRONG_COMPONENT}:{case_id}")
        if row.first_slice_include.lower() != "yes":
            issues.append(f"{BLOCK_TRADE_FIRST_SLICE_INCLUDE_REQUIRED}:{case_id}")
        if row.anchor_tdate != BLOCK_TRADE_FIRST_SLICE_ANCHOR_TDATE:
            issues.append(
                f"{BLOCK_TRADE_FIRST_SLICE_WRONG_ANCHOR_TDATE}:{case_id}={row.anchor_tdate}"
            )
        planned = compute_block_trade_first_slice_planned_requests(row)
        if planned > BLOCK_TRADE_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{BLOCK_TRADE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:{case_id}={planned}"
            )
        total_planned += planned
    for required_id in sorted(BLOCK_TRADE_FIRST_SLICE_ALLOWED_CASE_IDS):
        if required_id not in seen_ids:
            issues.append(f"missing_case_id:{required_id}")
    if total_planned > BLOCK_TRADE_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(f"{BLOCK_TRADE_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{total_planned}")
    return issues


def validate_block_trade_first_slice_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT)
    v1_root = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v2_root = _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT)
    replacement_root = _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT)
    targeted_root = _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT)
    margin_root = _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT)
    disclosure_root = _normalize_output_root(
        DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT
    )
    rsu_root = _normalize_output_root(
        DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
    )
    ep_root = _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT)
    blocked_pairs = [
        (v1_root, BLOCK_TRADE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED),
        (v2_root, BLOCK_TRADE_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED),
        (replacement_root, BLOCK_TRADE_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED),
        (targeted_root, BLOCK_TRADE_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED),
        (margin_root, BLOCK_TRADE_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED),
        (disclosure_root, BLOCK_TRADE_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED),
        (rsu_root, "block_trade_first_slice_output_root_write_blocked_for_restricted_shares_unlock_first_slice"),
        (ep_root, "block_trade_first_slice_output_root_write_blocked_for_equity_pledge_first_slice"),
    ]
    for blocked_root, token in blocked_pairs:
        if root == blocked_root or root.startswith(blocked_root + os.sep):
            return False, token
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT_REQUIRED


def enforce_block_trade_first_slice_write_block_targets(
    output_paths: Dict[str, str],
) -> None:
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {BLOCK_TRADE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_block_trade_first_slice_forbidden_options(
    args: argparse.Namespace,
) -> None:
    enforce_forbidden_options(args)
    mixed_modes = [
        ("known_event_replacement", args.known_event_replacement),
        ("known_event_targeted_probe", args.known_event_targeted_probe),
        ("bounded_probe_v2", args.bounded_probe_v2),
        ("margin_trading_first_slice", args.margin_trading_first_slice),
        ("restricted_shares_unlock_first_slice", args.restricted_shares_unlock_first_slice),
        ("equity_pledge_first_slice", args.equity_pledge_first_slice),
        ("shareholder_change_first_slice", args.shareholder_change_first_slice),
    ]
    for name, enabled in mixed_modes:
        if args.block_trade_first_slice and enabled:
            print(
                f"ERROR: {BLOCK_TRADE_FIRST_SLICE_MIXED_MODE_BLOCKED}:{name}",
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
        (
            "approve_d_class_margin_trading_first_slice",
            args.approve_d_class_margin_trading_first_slice,
        ),
        (
            "approve_d_class_restricted_shares_unlock_first_slice",
            args.approve_d_class_restricted_shares_unlock_first_slice,
        ),
        (
            "approve_d_class_equity_pledge_first_slice",
            args.approve_d_class_equity_pledge_first_slice,
        ),
        (
            "approve_d_class_shareholder_change_first_slice",
            args.approve_d_class_shareholder_change_first_slice,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.block_trade_first_slice and enabled:
            print(
                f"ERROR: {BLOCK_TRADE_FIRST_SLICE_WRONG_APPROVAL_FLAG}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    if (
        not args.block_trade_first_slice
        and args.approve_d_class_block_trade_first_slice
    ):
        print(
            f"ERROR: {BLOCK_TRADE_FIRST_SLICE_WRONG_APPROVAL_FLAG}:"
            "block_trade_first_slice_flag_without_mode",
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


def enforce_block_trade_first_slice_live_approval_gate(
    args: argparse.Namespace,
) -> None:
    if args.mode == "live" and args.block_trade_first_slice:
        if not args.approve_d_class_block_trade_first_slice:
            print(
                f"ERROR: {BLOCK_TRADE_FIRST_SLICE_APPROVAL_REQUIRED}",
                file=sys.stderr,
            )
            sys.exit(2)


def is_block_trade_first_slice_acceptable(
    row: BlockTradeFirstSliceRow,
    summary: Dict[str, str],
) -> bool:
    """第一切片 acceptable 判定；禁止 disclosure-only 升级为 captured_normal。"""
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    eb = row.expected_behavior
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if "disclosure" in row.reason.lower() and rs != "found":
        return False
    if "captured_normal" in eb and rs == "found" and rc >= 1 and qs in (
        "pass",
        "needs_review",
    ):
        return True
    if eb == "empty_but_valid" and rs == "empty_but_valid" and rc == 0:
        return True
    if "empty_but_valid" in eb and rs == "empty_but_valid" and rc == 0:
        return True
    if "captured_normal_or_empty_but_valid" in eb and (
        (rs == "found" and rc >= 1) or (rs == "empty_but_valid" and rc == 0)
    ):
        return qs in ("pass", "needs_review", "")
    if rs == "found" and rc >= 1 and qs in ("pass", "needs_review"):
        return True
    return False


def build_block_trade_first_slice_dryrun_rows(
    rows: List[BlockTradeFirstSliceRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    for row in rows:
        planned_requests = compute_block_trade_first_slice_planned_requests(row)
        plan = build_block_trade_first_slice_plan(row.anchor_tdate)
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
                "planned_endpoint": BLOCK_TRADE_FIRST_SLICE_ENDPOINT,
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
                    f"query_mode=tdate_daily; empty_but_valid_allowed=yes"
                ),
            }
        )
    return dry_rows


def write_block_trade_first_slice_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_block_trade_first_slice_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=BLOCK_TRADE_FIRST_SLICE_DRYRUN_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_block_trade_first_slice_dryrun_summary(
    dry_rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    lines = [
        "# CNINFO D 类 block_trade First-Slice Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** block_trade first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_request_count_total | **{planned_total}** |",
        f"| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        f"- component: **block_trade**",
        f"- endpoint: `{BLOCK_TRADE_FIRST_SLICE_ENDPOINT}`",
        f"- query mode: **tdate_daily**",
        f"- anchor_tdate: **{BLOCK_TRADE_FIRST_SLICE_ANCHOR_TDATE}**",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_block_trade_first_slice_runner_extension_gate = {BLOCK_TRADE_FIRST_SLICE_RUNNER_GATE}",
        "approval_status = NOT_APPROVED",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_block_trade_first_slice_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def block_trade_first_slice_row_to_universe_case(
    row: BlockTradeFirstSliceRow,
) -> UniverseCase:
    """将 block_trade 第一切片 universe 行转为探测用 UniverseCase。"""
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


def assess_block_trade_first_slice_failure_type(
    row: BlockTradeFirstSliceRow,
    summary: Dict[str, str],
) -> str:
    if is_block_trade_first_slice_acceptable(row, summary):
        return ""
    rs = summary.get("retrieval_status", "")
    if rs in ("http_error", "blocked"):
        return "network_or_http_error"
    if rs == "empty_but_valid" and row.expected_behavior == "captured_normal_candidate":
        return "expectation_mismatch"
    return "expectation_mismatch"


def validate_block_trade_first_slice_request_caps(stats: LiveStats) -> List[str]:
    issues: List[str] = []
    for case_id in sorted(BLOCK_TRADE_FIRST_SLICE_ALLOWED_CASE_IDS):
        cnt = stats.case_request_counts.get(case_id, 0)
        if cnt > BLOCK_TRADE_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{BLOCK_TRADE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:{case_id}={cnt}"
            )
    if stats.cninfo_requests > BLOCK_TRADE_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{BLOCK_TRADE_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{stats.cninfo_requests}"
        )
    return issues


def compute_block_trade_first_slice_execution_gate(
    universe_rows: List[BlockTradeFirstSliceRow],
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """block_trade 第一切片 live 执行 gate；≥3/5 acceptable → PASS_WITH_CAVEAT。"""
    acceptable = sum(
        1
        for row in universe_rows
        if is_block_trade_first_slice_acceptable(
            row, case_summaries.get(row.case_id, {})
        )
    )
    if acceptable >= 3:
        return BLOCK_TRADE_FIRST_SLICE_EXECUTION_GATE_PASS
    return BLOCK_TRADE_FIRST_SLICE_EXECUTION_GATE_FAIL


def build_block_trade_first_slice_live_row(
    row: BlockTradeFirstSliceRow,
    summary: Dict[str, str],
) -> Dict[str, str]:
    acceptable = is_block_trade_first_slice_acceptable(row, summary)
    failure_type = assess_block_trade_first_slice_failure_type(row, summary)
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


def write_block_trade_first_slice_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_block_trade_first_slice_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=BLOCK_TRADE_FIRST_SLICE_LIVE_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_block_trade_first_slice_quality_report(
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
        "d_class_block_trade_first_slice_quality_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=BLOCK_TRADE_FIRST_SLICE_QUALITY_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_block_trade_first_slice_live_summary(
    rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    acceptable = sum(1 for r in rows if r.get("acceptable") == "yes")
    lines = [
        "# CNINFO D 类 block_trade First-Slice Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** block_trade first-slice live summary · **NOT APPROVED for production**",
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
        f"d_class_block_trade_first_slice_live_path_gate = {BLOCK_TRADE_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_block_trade_first_slice_execution_gate = {gate}",
        "approval_status = NOT_APPROVED",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_block_trade_first_slice_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_block_trade_first_slice_live(
    universe_rows: List[BlockTradeFirstSliceRow],
    output_paths: Dict[str, str],
) -> int:
    """block_trade 第一切片 live 探针；仅 DBT001–DBT005 调用 CNINFO。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    component_cfg = copy.deepcopy(
        source_configs.get(BLOCK_TRADE_FIRST_SLICE_COMPONENT, {})
    )
    endpoint = endpoints.get(
        BLOCK_TRADE_FIRST_SLICE_COMPONENT,
        component_cfg.get("api_url", BLOCK_TRADE_FIRST_SLICE_ENDPOINT),
    )

    for row in universe_rows:
        planned = compute_block_trade_first_slice_planned_requests(row)
        if planned > BLOCK_TRADE_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            print(
                f"ERROR: {BLOCK_TRADE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"planned={planned}",
                file=sys.stderr,
            )
            return 2

    session = requests.Session()
    stats = LiveStats()
    case_summaries: Dict[str, Dict[str, str]] = {}

    for row in sorted(universe_rows, key=lambda r: r.case_id):
        case = block_trade_first_slice_row_to_universe_case(row)
        row_cfg = copy.deepcopy(component_cfg)
        params_template = dict(row_cfg.get("params_template") or {})
        params_template["tdate"] = row.anchor_tdate
        row_cfg["params_template"] = params_template
        summary = execute_live_case(
            case, row_cfg, endpoint, session, stats, output_paths
        )
        case_summaries[row.case_id] = summary
        print(
            f"{row.case_id} {summary['retrieval_status']}: "
            f"records={summary['record_count']} "
            f"requests={summary['cninfo_request_count']}",
            flush=True,
        )

    cap_issues = validate_block_trade_first_slice_request_caps(stats)
    if cap_issues:
        print(
            "ERROR: block_trade first-slice request cap validation failed: "
            f"{cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_block_trade_first_slice_execution_gate(
        universe_rows, case_summaries
    )
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = BLOCK_TRADE_FIRST_SLICE_EXECUTION_GATE_FAIL

    live_rows = [
        build_block_trade_first_slice_live_row(row, case_summaries[row.case_id])
        for row in sorted(universe_rows, key=lambda r: r.case_id)
        if row.case_id in case_summaries
    ]

    report_path = write_block_trade_first_slice_live_report(live_rows, output_paths)
    quality_path = write_block_trade_first_slice_quality_report(
        live_rows, output_paths
    )
    summary_path = write_block_trade_first_slice_live_summary(
        live_rows, stats, gate, output_paths
    )

    print(
        f"mode=block_trade_first_slice_live cases={len(live_rows)} "
        f"acceptable={sum(1 for r in live_rows if r['acceptable'] == 'yes')}/"
        f"{len(live_rows)} cninfo_calls={stats.cninfo_requests}"
    )
    print(f"gate=d_class_block_trade_first_slice_execution_gate={gate}")
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == BLOCK_TRADE_FIRST_SLICE_EXECUTION_GATE_PASS else 1


def run_block_trade_first_slice(args: argparse.Namespace) -> int:
    enforce_block_trade_first_slice_forbidden_options(args)
    enforce_block_trade_first_slice_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(
            f"ERROR: {BLOCK_TRADE_FIRST_SLICE_UNIVERSE_CSV_REQUIRED}",
            file=sys.stderr,
        )
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_block_trade_first_slice_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_block_trade_first_slice_universe(args.universe_csv)
    universe_issues = validate_block_trade_first_slice_universe(universe_rows)
    if universe_issues:
        print(
            "ERROR: block_trade first-slice universe validation failed: "
            f"{universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_block_trade_first_slice_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_block_trade_first_slice_live(universe_rows, output_paths)

    dry_rows = build_block_trade_first_slice_dryrun_rows(universe_rows, output_root)
    report_path = write_block_trade_first_slice_dryrun_report(dry_rows, output_paths)
    summary_path = write_block_trade_first_slice_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    print(
        f"mode=block_trade_first_slice_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={planned_total} cninfo_calls=0"
    )
    print(
        "gate=d_class_block_trade_first_slice_runner_extension_gate="
        f"{BLOCK_TRADE_FIRST_SLICE_RUNNER_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0


def load_restricted_shares_unlock_first_slice_universe(
    path: str,
) -> List[RestrictedSharesUnlockFirstSliceRow]:
    rows: List[RestrictedSharesUnlockFirstSliceRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                RestrictedSharesUnlockFirstSliceRow(
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
                    exclude_flags=str(row.get("exclude_flags", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                    dlc003_reference=str(
                        row.get("dlc003_reference", "")
                    ).strip(),
                )
            )
    return rows


def build_restricted_shares_unlock_first_slice_plan(
    anchor_tdate: str,
    max_requests: int = RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_MAX_REQUESTS,
) -> List[str]:
    """restricted_shares_unlock 第一切片 dry-run 请求计划（liftBan/detail · multi-probe · 仅计数）。"""
    anchor = date.fromisoformat(anchor_tdate)
    steps = [f"liftBan_detail_primary_{anchor_tdate}"]
    for offset in (-1, 1):
        probe_date = (anchor + timedelta(days=offset)).strftime("%Y-%m-%d")
        steps.append(f"optional_tdate_probe_{probe_date}")
    while len(steps) < max_requests:
        steps.append("budget_reserve")
    return steps[:max_requests]


def compute_restricted_shares_unlock_first_slice_planned_requests(
    row: RestrictedSharesUnlockFirstSliceRow,
) -> int:
    plan = build_restricted_shares_unlock_first_slice_plan(row.anchor_tdate)
    return len(plan)


def validate_restricted_shares_unlock_first_slice_universe(
    rows: List[RestrictedSharesUnlockFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    if len(rows) != RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE:
        issues.append(
            f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH}:got={len(rows)}"
        )
    seen_ids: Set[str] = set()
    total_planned = 0
    for row in rows:
        case_id = row.case_id
        if case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_ids.add(case_id)
        if case_id not in RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ALLOWED_CASE_IDS:
            issues.append(
                f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_FORBIDDEN_CASE_ID}:{case_id}"
            )
        if row.company_code in RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_FORBIDDEN_COMPANY_CODES:
            issues.append(
                f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_FORBIDDEN_COMPANY_CODE}:{row.company_code}"
            )
        expected_code = RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(
            case_id
        )
        if expected_code and row.company_code != expected_code:
            issues.append(
                f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_COMPANY_CODE}:{case_id}={row.company_code}"
            )
        if row.component != RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_COMPONENT:
            issues.append(
                f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_COMPONENT}:{case_id}"
            )
        if row.first_slice_include.lower() != "yes":
            issues.append(
                f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_INCLUDE_REQUIRED}:{case_id}"
            )
        if row.anchor_tdate != RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ANCHOR_TDATE:
            issues.append(
                f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_ANCHOR_TDATE}:{case_id}={row.anchor_tdate}"
            )
        planned = compute_restricted_shares_unlock_first_slice_planned_requests(row)
        if planned > RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:{case_id}={planned}"
            )
        total_planned += planned
    for required_id in sorted(RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ALLOWED_CASE_IDS):
        if required_id not in seen_ids:
            issues.append(f"missing_case_id:{required_id}")
    if total_planned > RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{total_planned}"
        )
    return issues


def validate_restricted_shares_unlock_first_slice_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(
        DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
    )
    v1_root = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v2_root = _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT)
    replacement_root = _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT)
    targeted_root = _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT)
    margin_root = _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT)
    disclosure_root = _normalize_output_root(
        DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT
    )
    block_trade_root = _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT)
    ep_root = _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT)
    blocked_pairs = [
        (v1_root, RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED),
        (v2_root, RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED),
        (
            replacement_root,
            RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            targeted_root,
            RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            margin_root,
            RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            disclosure_root,
            RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            block_trade_root,
            RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            ep_root,
            "restricted_shares_unlock_first_slice_output_root_write_blocked_for_equity_pledge_first_slice",
        ),
    ]
    for blocked_root, token in blocked_pairs:
        if root == blocked_root or root.startswith(blocked_root + os.sep):
            return False, token
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT_REQUIRED


def enforce_restricted_shares_unlock_first_slice_write_block_targets(
    output_paths: Dict[str, str],
) -> None:
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_restricted_shares_unlock_first_slice_forbidden_options(
    args: argparse.Namespace,
) -> None:
    enforce_forbidden_options(args)
    mixed_modes = [
        ("known_event_replacement", args.known_event_replacement),
        ("known_event_targeted_probe", args.known_event_targeted_probe),
        ("bounded_probe_v2", args.bounded_probe_v2),
        ("margin_trading_first_slice", args.margin_trading_first_slice),
        ("block_trade_first_slice", args.block_trade_first_slice),
        ("equity_pledge_first_slice", args.equity_pledge_first_slice),
        ("shareholder_change_first_slice", args.shareholder_change_first_slice),
    ]
    for name, enabled in mixed_modes:
        if args.restricted_shares_unlock_first_slice and enabled:
            print(
                f"ERROR: {RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_MIXED_MODE_BLOCKED}:{name}",
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
        (
            "approve_d_class_margin_trading_first_slice",
            args.approve_d_class_margin_trading_first_slice,
        ),
        (
            "approve_d_class_block_trade_first_slice",
            args.approve_d_class_block_trade_first_slice,
        ),
        (
            "approve_d_class_equity_pledge_first_slice",
            args.approve_d_class_equity_pledge_first_slice,
        ),
        (
            "approve_d_class_shareholder_change_first_slice",
            args.approve_d_class_shareholder_change_first_slice,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.restricted_shares_unlock_first_slice and enabled:
            print(
                f"ERROR: {RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_APPROVAL_FLAG}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    if (
        not args.restricted_shares_unlock_first_slice
        and args.approve_d_class_restricted_shares_unlock_first_slice
    ):
        print(
            f"ERROR: {RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_WRONG_APPROVAL_FLAG}:"
            "restricted_shares_unlock_first_slice_flag_without_mode",
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


def enforce_restricted_shares_unlock_first_slice_live_approval_gate(
    args: argparse.Namespace,
) -> None:
    if args.mode == "live" and args.restricted_shares_unlock_first_slice:
        if not args.approve_d_class_restricted_shares_unlock_first_slice:
            print(
                f"ERROR: {RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_APPROVAL_REQUIRED}",
                file=sys.stderr,
            )
            sys.exit(2)


def is_restricted_shares_unlock_first_slice_acceptable(
    row: RestrictedSharesUnlockFirstSliceRow,
    summary: Dict[str, str],
) -> bool:
    """第一切片 acceptable 判定；禁止 disclosure-only 升级为 captured_normal。"""
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    eb = row.expected_behavior
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if "disclosure" in row.notes.lower() and rs != "found":
        return False
    if eb == "empty_but_valid" and rs == "empty_but_valid" and rc == 0:
        return True
    if "empty_but_valid" in eb and rs == "empty_but_valid" and rc == 0:
        return True
    if "captured_normal_or_empty_but_valid" in eb and (
        (rs == "found" and rc >= 1) or (rs == "empty_but_valid" and rc == 0)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal_or_needs_review" in eb and rs == "found" and rc >= 1:
        return qs in ("pass", "needs_review")
    if "captured_normal_or_needs_review" in eb and rs == "empty_but_valid" and rc == 0:
        return True
    if rs == "found" and rc >= 1 and qs in ("pass", "needs_review"):
        return True
    return False


def build_restricted_shares_unlock_first_slice_dryrun_rows(
    rows: List[RestrictedSharesUnlockFirstSliceRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    for row in rows:
        planned_requests = compute_restricted_shares_unlock_first_slice_planned_requests(
            row
        )
        plan = build_restricted_shares_unlock_first_slice_plan(row.anchor_tdate)
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
                "planned_endpoint": RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ENDPOINT,
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
                    f"query_mode=tdate_daily; empty_but_valid_allowed=yes; "
                    f"max_per_case={RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_MAX_REQUESTS}"
                ),
            }
        )
    return dry_rows


def write_restricted_shares_unlock_first_slice_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_restricted_shares_unlock_first_slice_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_DRYRUN_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_restricted_shares_unlock_first_slice_dryrun_summary(
    dry_rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    lines = [
        "# CNINFO D 类 restricted_shares_unlock First-Slice Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** restricted_shares_unlock first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_request_count_total | **{planned_total}** |",
        f"| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        "- component: **restricted_shares_unlock**",
        f"- endpoint: `{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ENDPOINT}`",
        "- query mode: **tdate_daily**",
        f"- anchor_tdate: **{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ANCHOR_TDATE}**",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_restricted_shares_unlock_first_slice_runner_extension_gate = {RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_RUNNER_GATE}",
        "approval_status = NOT_APPROVED",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_restricted_shares_unlock_first_slice_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def restricted_shares_unlock_first_slice_row_to_universe_case(
    row: RestrictedSharesUnlockFirstSliceRow,
) -> UniverseCase:
    """将 restricted_shares_unlock 第一切片 universe 行转为探测用 UniverseCase。"""
    return UniverseCase(
        case_id=row.case_id,
        company_code=row.company_code,
        company_name=row.company_name,
        component=row.component,
        market=row.market,
        risk_level="",
        expected_behavior=row.expected_behavior,
        reason=row.notes,
    )


def build_restricted_shares_unlock_first_slice_live_probe_plan(
    anchor_tdate: str,
) -> List[Tuple[str, Dict[str, Any]]]:
    """restricted_shares_unlock 第一切片 live 探测计划（liftBan/detail · multi-probe）。"""
    items: List[Tuple[str, Dict[str, Any]]] = []
    anchor = date.fromisoformat(anchor_tdate)
    items.append(("liftBan_detail_primary", {"tdate": anchor_tdate}))
    for offset in (-1, 1):
        probe_date = (anchor + timedelta(days=offset)).strftime("%Y-%m-%d")
        items.append((f"optional_tdate_probe_{probe_date}", {"tdate": probe_date}))
    return items[:RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_MAX_REQUESTS]


def assess_restricted_shares_unlock_first_slice_failure_type(
    row: RestrictedSharesUnlockFirstSliceRow,
    summary: Dict[str, str],
) -> str:
    if is_restricted_shares_unlock_first_slice_acceptable(row, summary):
        return ""
    rs = summary.get("retrieval_status", "")
    if rs in ("http_error", "blocked"):
        return "network_or_http_error"
    if rs == "empty_but_valid" and "captured_normal_candidate" in row.expected_behavior:
        return "expectation_mismatch_on_sparse_day"
    return "expectation_mismatch"


def validate_restricted_shares_unlock_first_slice_request_caps(
    stats: LiveStats,
) -> List[str]:
    issues: List[str] = []
    for case_id in sorted(RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ALLOWED_CASE_IDS):
        cnt = stats.case_request_counts.get(case_id, 0)
        if cnt > RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:{case_id}={cnt}"
            )
    if stats.cninfo_requests > RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{stats.cninfo_requests}"
        )
    return issues


def compute_restricted_shares_unlock_first_slice_execution_gate(
    universe_rows: List[RestrictedSharesUnlockFirstSliceRow],
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """restricted_shares_unlock 第一切片 live 执行 gate；≥3/5 acceptable → PASS_WITH_CAVEAT。"""
    acceptable = sum(
        1
        for row in universe_rows
        if is_restricted_shares_unlock_first_slice_acceptable(
            row, case_summaries.get(row.case_id, {})
        )
    )
    if acceptable >= 3:
        return RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXECUTION_GATE_PASS
    return RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXECUTION_GATE_FAIL


def build_restricted_shares_unlock_first_slice_live_row(
    row: RestrictedSharesUnlockFirstSliceRow,
    summary: Dict[str, str],
) -> Dict[str, str]:
    acceptable = is_restricted_shares_unlock_first_slice_acceptable(row, summary)
    failure_type = assess_restricted_shares_unlock_first_slice_failure_type(row, summary)
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


def write_restricted_shares_unlock_first_slice_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_restricted_shares_unlock_first_slice_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_LIVE_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_restricted_shares_unlock_first_slice_quality_report(
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
        "d_class_restricted_shares_unlock_first_slice_quality_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_QUALITY_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_restricted_shares_unlock_first_slice_live_summary(
    rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    acceptable = sum(1 for r in rows if r.get("acceptable") == "yes")
    lines = [
        "# CNINFO D 类 restricted_shares_unlock First-Slice Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** restricted_shares_unlock first-slice live summary · **NOT APPROVED for production**",
        "",
        "## Result",
        "",
        "| 项 | 值 |",
        "|------|-----|",
        f"| cases | **{len(rows)}** |",
        f"| acceptable | **{acceptable}/{len(rows)}** |",
        f"| CNINFO requests | **{stats.cninfo_requests}** |",
        f"| execution gate | **{gate}** |",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_restricted_shares_unlock_first_slice_live_path_gate = {RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_restricted_shares_unlock_first_slice_execution_gate = {gate}",
        "approval_status = NOT_APPROVED",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_restricted_shares_unlock_first_slice_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_restricted_shares_unlock_first_slice_live(
    universe_rows: List[RestrictedSharesUnlockFirstSliceRow],
    output_paths: Dict[str, str],
) -> int:
    """restricted_shares_unlock 第一切片 live 探针；仅 DRU001–DRU005 调用 CNINFO。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    component_cfg = copy.deepcopy(
        source_configs.get(RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_COMPONENT, {})
    )
    endpoint = endpoints.get(
        RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_COMPONENT,
        component_cfg.get("api_url", RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_ENDPOINT),
    )

    for row in universe_rows:
        plan = build_restricted_shares_unlock_first_slice_live_probe_plan(
            row.anchor_tdate
        )
        if len(plan) > RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            print(
                f"ERROR: {RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"planned={len(plan)}",
                file=sys.stderr,
            )
            return 2

    session = requests.Session()
    stats = LiveStats()
    case_summaries: Dict[str, Dict[str, str]] = {}
    early_stop_count = 0

    for row in sorted(universe_rows, key=lambda r: r.case_id):
        case = restricted_shares_unlock_first_slice_row_to_universe_case(row)
        row_cfg = copy.deepcopy(component_cfg)
        params_template = dict(row_cfg.get("params_template") or {})
        params_template["tdate"] = row.anchor_tdate
        row_cfg["params_template"] = params_template
        plan = build_restricted_shares_unlock_first_slice_live_probe_plan(
            row.anchor_tdate
        )
        _, summary, stopped = execute_v2_bounded_probe_case(
            case,
            plan,
            "restricted_shares_unlock_first_slice",
            RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_PER_CASE_MAX_REQUESTS,
            row_cfg,
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

    cap_issues = validate_restricted_shares_unlock_first_slice_request_caps(stats)
    if cap_issues:
        print(
            "ERROR: restricted_shares_unlock first-slice request cap exceeded: "
            f"{cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_restricted_shares_unlock_first_slice_execution_gate(
        universe_rows, case_summaries
    )

    live_rows = [
        build_restricted_shares_unlock_first_slice_live_row(
            row, case_summaries[row.case_id]
        )
        for row in sorted(universe_rows, key=lambda r: r.case_id)
    ]

    report_path = write_restricted_shares_unlock_first_slice_live_report(
        live_rows, output_paths
    )
    quality_path = write_restricted_shares_unlock_first_slice_quality_report(
        live_rows, output_paths
    )
    summary_path = write_restricted_shares_unlock_first_slice_live_summary(
        live_rows, stats, gate, output_paths
    )

    print(
        f"mode=restricted_shares_unlock_first_slice_live cases={len(live_rows)} "
        f"acceptable={sum(1 for r in live_rows if r['acceptable'] == 'yes')}/"
        f"{len(live_rows)} cninfo_calls={stats.cninfo_requests} "
        f"early_stop_count={early_stop_count}"
    )
    print(
        f"gate=d_class_restricted_shares_unlock_first_slice_execution_gate={gate}"
    )
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return (
        0
        if gate == RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_EXECUTION_GATE_PASS
        else 1
    )


def run_restricted_shares_unlock_first_slice(args: argparse.Namespace) -> int:
    enforce_restricted_shares_unlock_first_slice_forbidden_options(args)
    enforce_restricted_shares_unlock_first_slice_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(
            f"ERROR: {RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_UNIVERSE_CSV_REQUIRED}",
            file=sys.stderr,
        )
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_restricted_shares_unlock_first_slice_output_root(
        args.output_root
    )
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_restricted_shares_unlock_first_slice_universe(
        args.universe_csv
    )
    universe_issues = validate_restricted_shares_unlock_first_slice_universe(
        universe_rows
    )
    if universe_issues:
        print(
            "ERROR: restricted_shares_unlock first-slice universe validation failed: "
            f"{universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_restricted_shares_unlock_first_slice_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_restricted_shares_unlock_first_slice_live(
            universe_rows, output_paths
        )

    dry_rows = build_restricted_shares_unlock_first_slice_dryrun_rows(
        universe_rows, output_root
    )
    report_path = write_restricted_shares_unlock_first_slice_dryrun_report(
        dry_rows, output_paths
    )
    summary_path = write_restricted_shares_unlock_first_slice_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    print(
        f"mode=restricted_shares_unlock_first_slice_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={planned_total} cninfo_calls=0"
    )
    print(
        "gate=d_class_restricted_shares_unlock_first_slice_runner_extension_gate="
        f"{RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_RUNNER_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0


def load_equity_pledge_first_slice_universe(path: str) -> List[EquityPledgeFirstSliceRow]:
    rows: List[EquityPledgeFirstSliceRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                EquityPledgeFirstSliceRow(
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
                    exclude_flags=str(row.get("exclude_flags", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                    dlc005_reference=str(
                        row.get("dlc005_reference", "")
                    ).strip(),
                )
            )
    return rows


def build_equity_pledge_first_slice_plan(
    anchor_tdate: str,
    max_requests: int = EQUITY_PLEDGE_FIRST_SLICE_PER_CASE_MAX_REQUESTS,
) -> List[str]:
    """equity_pledge 第一切片 dry-run 请求计划（tdate_daily · 仅计数）。"""
    return [f"tdate_daily_{anchor_tdate}"][:max_requests]


def compute_equity_pledge_first_slice_planned_requests(
    row: EquityPledgeFirstSliceRow,
) -> int:
    plan = build_equity_pledge_first_slice_plan(row.anchor_tdate)
    return len(plan)


def validate_equity_pledge_first_slice_universe(
    rows: List[EquityPledgeFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    if len(rows) != EQUITY_PLEDGE_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE:
        issues.append(
            f"{EQUITY_PLEDGE_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH}:got={len(rows)}"
        )
    seen_ids: Set[str] = set()
    total_planned = 0
    for row in rows:
        case_id = row.case_id
        if case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_ids.add(case_id)
        if case_id not in EQUITY_PLEDGE_FIRST_SLICE_ALLOWED_CASE_IDS:
            issues.append(f"{EQUITY_PLEDGE_FIRST_SLICE_FORBIDDEN_CASE_ID}:{case_id}")
        if row.company_code in EQUITY_PLEDGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODES:
            issues.append(
                f"{EQUITY_PLEDGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODE}:{row.company_code}"
            )
        expected_code = EQUITY_PLEDGE_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(case_id)
        if expected_code and row.company_code != expected_code:
            issues.append(
                f"{EQUITY_PLEDGE_FIRST_SLICE_WRONG_COMPANY_CODE}:{case_id}={row.company_code}"
            )
        if row.component != EQUITY_PLEDGE_FIRST_SLICE_COMPONENT:
            issues.append(f"{EQUITY_PLEDGE_FIRST_SLICE_WRONG_COMPONENT}:{case_id}")
        if row.first_slice_include.lower() != "yes":
            issues.append(f"{EQUITY_PLEDGE_FIRST_SLICE_INCLUDE_REQUIRED}:{case_id}")
        if row.anchor_tdate != EQUITY_PLEDGE_FIRST_SLICE_ANCHOR_TDATE:
            issues.append(
                f"{EQUITY_PLEDGE_FIRST_SLICE_WRONG_ANCHOR_TDATE}:{case_id}={row.anchor_tdate}"
            )
        planned = compute_equity_pledge_first_slice_planned_requests(row)
        if planned > EQUITY_PLEDGE_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{EQUITY_PLEDGE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:{case_id}={planned}"
            )
        total_planned += planned
    for required_id in sorted(EQUITY_PLEDGE_FIRST_SLICE_ALLOWED_CASE_IDS):
        if required_id not in seen_ids:
            issues.append(f"missing_case_id:{required_id}")
    if total_planned > EQUITY_PLEDGE_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{EQUITY_PLEDGE_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{total_planned}"
        )
    return issues


def validate_equity_pledge_first_slice_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT)
    v1_root = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v2_root = _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT)
    replacement_root = _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT)
    targeted_root = _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT)
    margin_root = _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT)
    disclosure_root = _normalize_output_root(
        DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT
    )
    block_trade_root = _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT)
    rsu_root = _normalize_output_root(
        DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
    )
    sc_root = _normalize_output_root(
        DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT
    )
    blocked_pairs = [
        (v1_root, EQUITY_PLEDGE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED),
        (v2_root, EQUITY_PLEDGE_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED),
        (
            replacement_root,
            EQUITY_PLEDGE_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            targeted_root,
            EQUITY_PLEDGE_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (margin_root, EQUITY_PLEDGE_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED),
        (disclosure_root, EQUITY_PLEDGE_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED),
        (block_trade_root, EQUITY_PLEDGE_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED),
        (rsu_root, EQUITY_PLEDGE_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED),
        (sc_root, "shareholder_change_first_slice_output_root_write_blocked_for_equity_pledge_first_slice"),
    ]
    for blocked_root, token in blocked_pairs:
        if root == blocked_root or root.startswith(blocked_root + os.sep):
            return False, token
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT_REQUIRED


def enforce_equity_pledge_first_slice_write_block_targets(
    output_paths: Dict[str, str],
) -> None:
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {EQUITY_PLEDGE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_equity_pledge_first_slice_forbidden_options(
    args: argparse.Namespace,
) -> None:
    enforce_forbidden_options(args)
    mixed_modes = [
        ("known_event_replacement", args.known_event_replacement),
        ("known_event_targeted_probe", args.known_event_targeted_probe),
        ("bounded_probe_v2", args.bounded_probe_v2),
        ("margin_trading_first_slice", args.margin_trading_first_slice),
        ("block_trade_first_slice", args.block_trade_first_slice),
        ("restricted_shares_unlock_first_slice", args.restricted_shares_unlock_first_slice),
        ("shareholder_change_first_slice", args.shareholder_change_first_slice),
        ("executive_shareholding_first_slice", args.executive_shareholding_first_slice),
    ]
    for name, enabled in mixed_modes:
        if args.equity_pledge_first_slice and enabled:
            print(
                f"ERROR: {EQUITY_PLEDGE_FIRST_SLICE_MIXED_MODE_BLOCKED}:{name}",
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
        (
            "approve_d_class_margin_trading_first_slice",
            args.approve_d_class_margin_trading_first_slice,
        ),
        (
            "approve_d_class_block_trade_first_slice",
            args.approve_d_class_block_trade_first_slice,
        ),
        (
            "approve_d_class_restricted_shares_unlock_first_slice",
            args.approve_d_class_restricted_shares_unlock_first_slice,
        ),
        (
            "approve_d_class_shareholder_change_first_slice",
            args.approve_d_class_shareholder_change_first_slice,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.equity_pledge_first_slice and enabled:
            print(
                f"ERROR: {EQUITY_PLEDGE_FIRST_SLICE_WRONG_APPROVAL_FLAG}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    if (
        not args.equity_pledge_first_slice
        and args.approve_d_class_equity_pledge_first_slice
    ):
        print(
            f"ERROR: {EQUITY_PLEDGE_FIRST_SLICE_WRONG_APPROVAL_FLAG}:"
            "equity_pledge_first_slice_flag_without_mode",
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


def enforce_equity_pledge_first_slice_live_approval_gate(
    args: argparse.Namespace,
) -> None:
    if args.mode == "live" and args.equity_pledge_first_slice:
        if not args.approve_d_class_equity_pledge_first_slice:
            print(
                f"ERROR: {EQUITY_PLEDGE_FIRST_SLICE_APPROVAL_REQUIRED}",
                file=sys.stderr,
            )
            sys.exit(2)


def build_equity_pledge_first_slice_dryrun_rows(
    rows: List[EquityPledgeFirstSliceRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    for row in rows:
        planned_requests = compute_equity_pledge_first_slice_planned_requests(row)
        plan = build_equity_pledge_first_slice_plan(row.anchor_tdate)
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
                "planned_endpoint": EQUITY_PLEDGE_FIRST_SLICE_ENDPOINT,
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
                    f"query_mode=tdate_daily; empty_but_valid_allowed=yes"
                ),
            }
        )
    return dry_rows


def write_equity_pledge_first_slice_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_equity_pledge_first_slice_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=EQUITY_PLEDGE_FIRST_SLICE_DRYRUN_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_equity_pledge_first_slice_dryrun_summary(
    dry_rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    lines = [
        "# CNINFO D 类 equity_pledge First-Slice Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** equity_pledge first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_request_count_total | **{planned_total}** |",
        f"| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        f"- component: **equity_pledge**",
        f"- endpoint: `{EQUITY_PLEDGE_FIRST_SLICE_ENDPOINT}`",
        f"- query mode: **tdate_daily**",
        f"- anchor_tdate: **{EQUITY_PLEDGE_FIRST_SLICE_ANCHOR_TDATE}**",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_equity_pledge_first_slice_runner_extension_gate = {EQUITY_PLEDGE_FIRST_SLICE_RUNNER_GATE}",
        "approval_status = NOT_APPROVED",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_equity_pledge_first_slice_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def equity_pledge_first_slice_row_to_universe_case(
    row: EquityPledgeFirstSliceRow,
) -> UniverseCase:
    """将 equity_pledge 第一切片 universe 行转为探测用 UniverseCase。"""
    return UniverseCase(
        case_id=row.case_id,
        company_code=row.company_code,
        company_name=row.company_name,
        component=row.component,
        market=row.market,
        risk_level="",
        expected_behavior=row.expected_behavior,
        reason=row.notes,
    )


def is_equity_pledge_first_slice_acceptable(
    row: EquityPledgeFirstSliceRow,
    summary: Dict[str, str],
) -> bool:
    """第一切片 acceptable 判定；禁止 disclosure-only 升级为 captured_normal。"""
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    eb = row.expected_behavior
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if "disclosure" in row.notes.lower() and rs != "found":
        return False
    if eb == "empty_but_valid" and rs == "empty_but_valid" and rc == 0:
        return True
    if "empty_but_valid" in eb and rs == "empty_but_valid" and rc == 0:
        return True
    if "captured_normal_or_empty_but_valid" in eb and (
        (rs == "found" and rc >= 1) or (rs == "empty_but_valid" and rc == 0)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal_or_needs_review" in eb and (
        (rs == "found" and rc >= 1) or (rs == "needs_review" and rc >= 1)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal" in eb and rs == "found" and rc >= 1 and qs in (
        "pass",
        "needs_review",
    ):
        return True
    if rs == "found" and rc >= 1 and qs in ("pass", "needs_review"):
        return True
    if rs == "needs_review" and rc >= 1 and qs == "needs_review":
        return "needs_review" in eb or "captured_normal" in eb
    return False


def assess_equity_pledge_first_slice_failure_type(
    row: EquityPledgeFirstSliceRow,
    summary: Dict[str, str],
) -> str:
    if is_equity_pledge_first_slice_acceptable(row, summary):
        return ""
    rs = summary.get("retrieval_status", "")
    if rs in ("http_error", "blocked"):
        return "network_or_http_error"
    if rs == "empty_but_valid" and row.expected_behavior == "captured_normal_candidate":
        return "expectation_mismatch"
    return "expectation_mismatch"


def validate_equity_pledge_first_slice_request_caps(stats: LiveStats) -> List[str]:
    issues: List[str] = []
    for case_id in sorted(EQUITY_PLEDGE_FIRST_SLICE_ALLOWED_CASE_IDS):
        cnt = stats.case_request_counts.get(case_id, 0)
        if cnt > EQUITY_PLEDGE_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{EQUITY_PLEDGE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:{case_id}={cnt}"
            )
    if stats.cninfo_requests > EQUITY_PLEDGE_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{EQUITY_PLEDGE_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{stats.cninfo_requests}"
        )
    return issues


def compute_equity_pledge_first_slice_execution_gate(
    universe_rows: List[EquityPledgeFirstSliceRow],
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """equity_pledge 第一切片 live 执行 gate；≥3/5 acceptable → PASS_WITH_CAVEAT。"""
    acceptable = sum(
        1
        for row in universe_rows
        if is_equity_pledge_first_slice_acceptable(
            row, case_summaries.get(row.case_id, {})
        )
    )
    if acceptable >= 3:
        return EQUITY_PLEDGE_FIRST_SLICE_EXECUTION_GATE_PASS
    return EQUITY_PLEDGE_FIRST_SLICE_EXECUTION_GATE_FAIL


def build_equity_pledge_first_slice_live_row(
    row: EquityPledgeFirstSliceRow,
    summary: Dict[str, str],
) -> Dict[str, str]:
    acceptable = is_equity_pledge_first_slice_acceptable(row, summary)
    failure_type = assess_equity_pledge_first_slice_failure_type(row, summary)
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


def write_equity_pledge_first_slice_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_equity_pledge_first_slice_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=EQUITY_PLEDGE_FIRST_SLICE_LIVE_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_equity_pledge_first_slice_quality_report(
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
        "d_class_equity_pledge_first_slice_quality_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=EQUITY_PLEDGE_FIRST_SLICE_QUALITY_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_equity_pledge_first_slice_live_summary(
    rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    acceptable = sum(1 for r in rows if r.get("acceptable") == "yes")
    lines = [
        "# CNINFO D 类 equity_pledge First-Slice Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** equity_pledge first-slice live summary · **NOT APPROVED for production**",
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
        f"d_class_equity_pledge_first_slice_live_path_gate = {EQUITY_PLEDGE_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_equity_pledge_first_slice_execution_gate = {gate}",
        "approval_status = NOT_APPROVED",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_equity_pledge_first_slice_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_equity_pledge_first_slice_live(
    universe_rows: List[EquityPledgeFirstSliceRow],
    output_paths: Dict[str, str],
) -> int:
    """equity_pledge 第一切片 live 探针；仅 DEP001–DEP005 调用 CNINFO。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    component_cfg = copy.deepcopy(
        source_configs.get(EQUITY_PLEDGE_FIRST_SLICE_COMPONENT, {})
    )
    endpoint = endpoints.get(
        EQUITY_PLEDGE_FIRST_SLICE_COMPONENT,
        component_cfg.get("api_url", EQUITY_PLEDGE_FIRST_SLICE_ENDPOINT),
    )

    for row in universe_rows:
        planned = compute_equity_pledge_first_slice_planned_requests(row)
        if planned > EQUITY_PLEDGE_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            print(
                f"ERROR: {EQUITY_PLEDGE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"planned={planned}",
                file=sys.stderr,
            )
            return 2

    session = requests.Session()
    stats = LiveStats()
    case_summaries: Dict[str, Dict[str, str]] = {}

    for row in sorted(universe_rows, key=lambda r: r.case_id):
        case = equity_pledge_first_slice_row_to_universe_case(row)
        row_cfg = copy.deepcopy(component_cfg)
        params_template = dict(row_cfg.get("params_template") or {})
        params_template["tdate"] = row.anchor_tdate
        row_cfg["params_template"] = params_template
        summary = execute_live_case(
            case, row_cfg, endpoint, session, stats, output_paths
        )
        case_summaries[row.case_id] = summary
        print(
            f"{row.case_id} {summary['retrieval_status']}: "
            f"records={summary['record_count']} "
            f"requests={summary['cninfo_request_count']}",
            flush=True,
        )

    cap_issues = validate_equity_pledge_first_slice_request_caps(stats)
    if cap_issues:
        print(
            "ERROR: equity_pledge first-slice request cap validation failed: "
            f"{cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_equity_pledge_first_slice_execution_gate(
        universe_rows, case_summaries
    )
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = EQUITY_PLEDGE_FIRST_SLICE_EXECUTION_GATE_FAIL

    live_rows = [
        build_equity_pledge_first_slice_live_row(row, case_summaries[row.case_id])
        for row in sorted(universe_rows, key=lambda r: r.case_id)
        if row.case_id in case_summaries
    ]

    report_path = write_equity_pledge_first_slice_live_report(live_rows, output_paths)
    quality_path = write_equity_pledge_first_slice_quality_report(
        live_rows, output_paths
    )
    summary_path = write_equity_pledge_first_slice_live_summary(
        live_rows, stats, gate, output_paths
    )

    print(
        f"mode=equity_pledge_first_slice_live cases={len(live_rows)} "
        f"acceptable={sum(1 for r in live_rows if r['acceptable'] == 'yes')}/"
        f"{len(live_rows)} cninfo_calls={stats.cninfo_requests}"
    )
    print(f"gate=d_class_equity_pledge_first_slice_execution_gate={gate}")
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == EQUITY_PLEDGE_FIRST_SLICE_EXECUTION_GATE_PASS else 1


def run_equity_pledge_first_slice(args: argparse.Namespace) -> int:
    enforce_equity_pledge_first_slice_forbidden_options(args)
    enforce_equity_pledge_first_slice_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(
            f"ERROR: {EQUITY_PLEDGE_FIRST_SLICE_UNIVERSE_CSV_REQUIRED}",
            file=sys.stderr,
        )
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_equity_pledge_first_slice_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_equity_pledge_first_slice_universe(args.universe_csv)
    universe_issues = validate_equity_pledge_first_slice_universe(universe_rows)
    if universe_issues:
        print(
            "ERROR: equity_pledge first-slice universe validation failed: "
            f"{universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_equity_pledge_first_slice_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_equity_pledge_first_slice_live(universe_rows, output_paths)

    dry_rows = build_equity_pledge_first_slice_dryrun_rows(universe_rows, output_root)
    report_path = write_equity_pledge_first_slice_dryrun_report(dry_rows, output_paths)
    summary_path = write_equity_pledge_first_slice_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    print(
        f"mode=equity_pledge_first_slice_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={planned_total} cninfo_calls=0"
    )
    print(
        "gate=d_class_equity_pledge_first_slice_runner_extension_gate="
        f"{EQUITY_PLEDGE_FIRST_SLICE_RUNNER_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0




def load_shareholder_change_first_slice_universe(
    path: str,
) -> List[ShareholderChangeFirstSliceRow]:
    rows: List[ShareholderChangeFirstSliceRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                ShareholderChangeFirstSliceRow(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    component=str(row.get("component", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    anchor_tdate=str(row.get("anchor_tdate", "")).strip(),
                    query_type=str(row.get("query_type", "")).strip(),
                    first_slice_include=str(
                        row.get("first_slice_include", "")
                    ).strip(),
                    expected_behavior=str(
                        row.get("expected_behavior", "")
                    ).strip(),
                    exclude_flags=str(row.get("exclude_flags", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                    dlc006_reference=str(
                        row.get("dlc006_reference", "")
                    ).strip(),
                )
            )
    return rows


def build_shareholder_change_first_slice_plan(
    anchor_tdate: str,
    query_type: str = SHAREHOLDER_CHANGE_FIRST_SLICE_QUERY_TYPE,
) -> List[str]:
    """shareholder_change 第一切片计划：仅 type=inc + 单一 tdate（非 generic multi-probe）。"""
    return [f"type_{query_type}_tdate_{anchor_tdate}"]


def _build_shareholder_change_first_slice_params(
    row: ShareholderChangeFirstSliceRow,
) -> List[Dict[str, Any]]:
    """独立 params builder；禁止复用 generic _build_live_params multi-probe。"""
    return [{"type": "inc", "tdate": row.anchor_tdate}]


def compute_shareholder_change_first_slice_planned_requests(
    row: ShareholderChangeFirstSliceRow,
) -> int:
    plan = build_shareholder_change_first_slice_plan(row.anchor_tdate, row.query_type)
    return len(plan)


def validate_shareholder_change_first_slice_universe(
    rows: List[ShareholderChangeFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    if len(rows) != SHAREHOLDER_CHANGE_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE:
        issues.append(
            f"{SHAREHOLDER_CHANGE_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH}:got={len(rows)}"
        )
    seen_ids: Set[str] = set()
    total_planned = 0
    for row in rows:
        case_id = row.case_id
        if case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_ids.add(case_id)
        if case_id not in SHAREHOLDER_CHANGE_FIRST_SLICE_ALLOWED_CASE_IDS:
            issues.append(
                f"{SHAREHOLDER_CHANGE_FIRST_SLICE_FORBIDDEN_CASE_ID}:{case_id}"
            )
        if row.company_code in SHAREHOLDER_CHANGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODES:
            issues.append(
                f"{SHAREHOLDER_CHANGE_FIRST_SLICE_FORBIDDEN_COMPANY_CODE}:"
                f"{row.company_code}"
            )
        expected_code = SHAREHOLDER_CHANGE_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(
            case_id
        )
        if expected_code and row.company_code != expected_code:
            issues.append(
                f"{SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_COMPANY_CODE}:"
                f"{case_id}={row.company_code}"
            )
        if row.component != SHAREHOLDER_CHANGE_FIRST_SLICE_COMPONENT:
            issues.append(
                f"{SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_COMPONENT}:{case_id}"
            )
        if row.first_slice_include.lower() != "yes":
            issues.append(
                f"{SHAREHOLDER_CHANGE_FIRST_SLICE_INCLUDE_REQUIRED}:{case_id}"
            )
        if row.anchor_tdate != SHAREHOLDER_CHANGE_FIRST_SLICE_ANCHOR_TDATE:
            issues.append(
                f"{SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_ANCHOR_TDATE}:"
                f"{case_id}={row.anchor_tdate}"
            )
        if row.query_type != SHAREHOLDER_CHANGE_FIRST_SLICE_QUERY_TYPE:
            issues.append(
                f"{SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_QUERY_TYPE}:"
                f"{case_id}={row.query_type}"
            )
        planned = compute_shareholder_change_first_slice_planned_requests(row)
        if planned > SHAREHOLDER_CHANGE_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{SHAREHOLDER_CHANGE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"{case_id}={planned}"
            )
        total_planned += planned
    for required_id in sorted(SHAREHOLDER_CHANGE_FIRST_SLICE_ALLOWED_CASE_IDS):
        if required_id not in seen_ids:
            issues.append(f"missing_case_id:{required_id}")
    if total_planned > SHAREHOLDER_CHANGE_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{SHAREHOLDER_CHANGE_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{total_planned}"
        )
    return issues


def validate_shareholder_change_first_slice_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(
        DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT
    )
    v1_root = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v2_root = _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT)
    replacement_root = _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT)
    targeted_root = _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT)
    equity_pledge_root = _normalize_output_root(
        DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT
    )
    margin_root = _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT)
    disclosure_root = _normalize_output_root(
        DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT
    )
    block_trade_root = _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT)
    rsu_root = _normalize_output_root(
        DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
    )
    es_root = _normalize_output_root(
        DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT
    )
    blocked_pairs = [
        (v1_root, SHAREHOLDER_CHANGE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED),
        (v2_root, SHAREHOLDER_CHANGE_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED),
        (
            replacement_root,
            SHAREHOLDER_CHANGE_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            targeted_root,
            SHAREHOLDER_CHANGE_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            equity_pledge_root,
            SHAREHOLDER_CHANGE_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (margin_root, SHAREHOLDER_CHANGE_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED),
        (
            disclosure_root,
            SHAREHOLDER_CHANGE_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            block_trade_root,
            SHAREHOLDER_CHANGE_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (rsu_root, SHAREHOLDER_CHANGE_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED),
        (es_root, "executive_shareholding_first_slice_output_root_write_blocked"),
    ]
    for blocked_root, token in blocked_pairs:
        if root == blocked_root or root.startswith(blocked_root + os.sep):
            return False, token
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT_REQUIRED


def enforce_shareholder_change_first_slice_write_block_targets(
    output_paths: Dict[str, str],
) -> None:
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {SHAREHOLDER_CHANGE_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_shareholder_change_first_slice_forbidden_options(
    args: argparse.Namespace,
) -> None:
    enforce_forbidden_options(args)
    mixed_modes = [
        ("known_event_replacement", args.known_event_replacement),
        ("known_event_targeted_probe", args.known_event_targeted_probe),
        ("bounded_probe_v2", args.bounded_probe_v2),
        ("margin_trading_first_slice", args.margin_trading_first_slice),
        ("block_trade_first_slice", args.block_trade_first_slice),
        ("restricted_shares_unlock_first_slice", args.restricted_shares_unlock_first_slice),
        ("equity_pledge_first_slice", args.equity_pledge_first_slice),
        ("executive_shareholding_first_slice", args.executive_shareholding_first_slice),
    ]
    for name, enabled in mixed_modes:
        if args.shareholder_change_first_slice and enabled:
            print(
                f"ERROR: {SHAREHOLDER_CHANGE_FIRST_SLICE_MIXED_MODE_BLOCKED}:{name}",
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
        (
            "approve_d_class_margin_trading_first_slice",
            args.approve_d_class_margin_trading_first_slice,
        ),
        (
            "approve_d_class_block_trade_first_slice",
            args.approve_d_class_block_trade_first_slice,
        ),
        (
            "approve_d_class_restricted_shares_unlock_first_slice",
            args.approve_d_class_restricted_shares_unlock_first_slice,
        ),
        (
            "approve_d_class_equity_pledge_first_slice",
            args.approve_d_class_equity_pledge_first_slice,
        ),
        (
            "approve_d_class_executive_shareholding_first_slice",
            args.approve_d_class_executive_shareholding_first_slice,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.shareholder_change_first_slice and enabled:
            print(
                f"ERROR: {SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_APPROVAL_FLAG}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    if (
        not args.shareholder_change_first_slice
        and args.approve_d_class_shareholder_change_first_slice
    ):
        print(
            f"ERROR: {SHAREHOLDER_CHANGE_FIRST_SLICE_WRONG_APPROVAL_FLAG}:"
            "shareholder_change_first_slice_flag_without_mode",
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


def enforce_shareholder_change_first_slice_live_approval_gate(
    args: argparse.Namespace,
) -> None:
    if args.mode == "live" and args.shareholder_change_first_slice:
        if not args.approve_d_class_shareholder_change_first_slice:
            print(
                f"ERROR: {SHAREHOLDER_CHANGE_FIRST_SLICE_APPROVAL_REQUIRED}",
                file=sys.stderr,
            )
            sys.exit(2)


def build_shareholder_change_first_slice_dryrun_rows(
    rows: List[ShareholderChangeFirstSliceRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    for row in rows:
        planned_requests = compute_shareholder_change_first_slice_planned_requests(row)
        plan = build_shareholder_change_first_slice_plan(
            row.anchor_tdate, row.query_type
        )
        dry_rows.append(
            {
                "case_id": row.case_id,
                "company_code": row.company_code,
                "company_name": row.company_name,
                "component": row.component,
                "market": row.market,
                "anchor_tdate": row.anchor_tdate,
                "query_type": row.query_type,
                "first_slice_include": row.first_slice_include,
                "expected_behavior": row.expected_behavior,
                "planned_request_count": str(planned_requests),
                "planned_output_root": output_root,
                "planned_endpoint": SHAREHOLDER_CHANGE_FIRST_SLICE_ENDPOINT,
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
                    f"query_mode=type_inc_tdate_daily; "
                    f"empty_but_valid_allowed=yes; not_generic_multi_probe=yes"
                ),
            }
        )
    return dry_rows


def write_shareholder_change_first_slice_planned_snapshots(
    rows: List[ShareholderChangeFirstSliceRow],
    output_paths: Dict[str, str],
) -> None:
    """写入 dry-run planned_snapshots（synthetic · cninfo_called=false）。"""
    for row in rows:
        plan = build_shareholder_change_first_slice_plan(
            row.anchor_tdate, row.query_type
        )
        params = _build_shareholder_change_first_slice_params(row)
        snap_path = os.path.join(
            output_paths["planned_snapshots"],
            f"{row.case_id}_{SHAREHOLDER_CHANGE_FIRST_SLICE_COMPONENT}.json",
        )
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case_id": row.case_id,
                    "company_code": row.company_code,
                    "company_name": row.company_name,
                    "component": row.component,
                    "market": row.market,
                    "anchor_tdate": row.anchor_tdate,
                    "query_type": row.query_type,
                    "expected_behavior": row.expected_behavior,
                    "mode": "dry_run",
                    "endpoint": SHAREHOLDER_CHANGE_FIRST_SLICE_ENDPOINT,
                    "planned_params": params,
                    "planned_request_labels": plan,
                    "cninfo_called": False,
                    "pdf_download": False,
                    "ocr": False,
                    "extraction": False,
                    "db_write": False,
                    "minio_write": False,
                    "rag_run": False,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )


def write_shareholder_change_first_slice_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_first_slice_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=SHAREHOLDER_CHANGE_FIRST_SLICE_DRYRUN_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_shareholder_change_first_slice_dryrun_summary(
    dry_rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    lines = [
        "# CNINFO D 类 shareholder_change First-Slice Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** shareholder_change first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_request_count_total | **{planned_total}** |",
        f"| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        f"- component: **shareholder_change**",
        f"- endpoint: `{SHAREHOLDER_CHANGE_FIRST_SLICE_ENDPOINT}`",
        f"- query mode: **type_inc + tdate_daily**（禁止 desc / multi-tdate）",
        f"- anchor_tdate: **{SHAREHOLDER_CHANGE_FIRST_SLICE_ANCHOR_TDATE}**",
        f"- query_type: **{SHAREHOLDER_CHANGE_FIRST_SLICE_QUERY_TYPE}**",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_shareholder_change_first_slice_runner_extension_gate = {SHAREHOLDER_CHANGE_FIRST_SLICE_RUNNER_GATE}",
        "approval_status = NOT_APPROVED",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_first_slice_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def shareholder_change_first_slice_row_to_universe_case(
    row: ShareholderChangeFirstSliceRow,
) -> UniverseCase:
    """将 shareholder_change 第一切片 universe 行转为探测用 UniverseCase。"""
    return UniverseCase(
        case_id=row.case_id,
        company_code=row.company_code,
        company_name=row.company_name,
        component=row.component,
        market=row.market,
        risk_level="",
        expected_behavior=row.expected_behavior,
        reason=row.notes,
    )


def is_shareholder_change_first_slice_acceptable(
    row: ShareholderChangeFirstSliceRow,
    summary: Dict[str, str],
) -> bool:
    """第一切片 acceptable 判定；禁止 disclosure-only 升级为 captured_normal。"""
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    eb = row.expected_behavior
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if "disclosure" in row.notes.lower() and rs != "found":
        return False
    if eb == "empty_but_valid" and rs == "empty_but_valid" and rc == 0:
        return True
    if "empty_but_valid" in eb and rs == "empty_but_valid" and rc == 0:
        return True
    if "captured_normal_or_empty_but_valid" in eb and (
        (rs == "found" and rc >= 1) or (rs == "empty_but_valid" and rc == 0)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal_or_needs_review" in eb and (
        (rs == "found" and rc >= 1) or (rs == "needs_review" and rc >= 1)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal" in eb and rs == "found" and rc >= 1 and qs in (
        "pass",
        "needs_review",
    ):
        return True
    if rs == "found" and rc >= 1 and qs in ("pass", "needs_review"):
        return True
    if rs == "needs_review" and rc >= 1 and qs == "needs_review":
        return "needs_review" in eb or "captured_normal" in eb
    return False


def assess_shareholder_change_first_slice_failure_type(
    row: ShareholderChangeFirstSliceRow,
    summary: Dict[str, str],
) -> str:
    if is_shareholder_change_first_slice_acceptable(row, summary):
        return ""
    rs = summary.get("retrieval_status", "")
    if rs in ("http_error", "blocked"):
        return "network_or_http_error"
    return "expectation_mismatch"


def validate_shareholder_change_first_slice_request_caps(stats: LiveStats) -> List[str]:
    issues: List[str] = []
    for case_id in sorted(SHAREHOLDER_CHANGE_FIRST_SLICE_ALLOWED_CASE_IDS):
        cnt = stats.case_request_counts.get(case_id, 0)
        if cnt > SHAREHOLDER_CHANGE_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{SHAREHOLDER_CHANGE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:{case_id}={cnt}"
            )
    if stats.cninfo_requests > SHAREHOLDER_CHANGE_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{SHAREHOLDER_CHANGE_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{stats.cninfo_requests}"
        )
    return issues


def compute_shareholder_change_first_slice_execution_gate(
    universe_rows: List[ShareholderChangeFirstSliceRow],
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """shareholder_change 第一切片 live 执行 gate；≥3/5 acceptable → PASS_WITH_CAVEAT。"""
    acceptable = sum(
        1
        for row in universe_rows
        if is_shareholder_change_first_slice_acceptable(
            row, case_summaries.get(row.case_id, {})
        )
    )
    if acceptable >= 3:
        return SHAREHOLDER_CHANGE_FIRST_SLICE_EXECUTION_GATE_PASS
    return SHAREHOLDER_CHANGE_FIRST_SLICE_EXECUTION_GATE_FAIL


def build_shareholder_change_first_slice_live_row(
    row: ShareholderChangeFirstSliceRow,
    summary: Dict[str, str],
) -> Dict[str, str]:
    acceptable = is_shareholder_change_first_slice_acceptable(row, summary)
    failure_type = assess_shareholder_change_first_slice_failure_type(row, summary)
    return {
        "case_id": row.case_id,
        "company_code": row.company_code,
        "company_name": row.company_name,
        "component": row.component,
        "market": row.market,
        "anchor_tdate": row.anchor_tdate,
        "query_type": row.query_type,
        "expected_behavior": row.expected_behavior,
        "retrieval_status": summary.get("retrieval_status", ""),
        "quality_status": summary.get("quality_status", ""),
        "lineage_status": summary.get("lineage_status", ""),
        "record_count": summary.get("record_count", "0"),
        "empty_but_valid": summary.get("empty_but_valid", "no"),
        "needs_review": summary.get("needs_review", "no"),
        "endpoint_used": summary.get("endpoint_used", ""),
        "cninfo_request_count": summary.get("cninfo_request_count", "0"),
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


def write_shareholder_change_first_slice_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_first_slice_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=SHAREHOLDER_CHANGE_FIRST_SLICE_LIVE_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_shareholder_change_first_slice_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    quality_rows = [
        {
            "case_id": row["case_id"],
            "component": row["component"],
            "anchor_tdate": row["anchor_tdate"],
            "query_type": row["query_type"],
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
        "d_class_shareholder_change_first_slice_quality_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=SHAREHOLDER_CHANGE_FIRST_SLICE_QUALITY_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_shareholder_change_first_slice_live_summary(
    rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    acceptable = sum(1 for r in rows if r.get("acceptable") == "yes")
    lines = [
        "# CNINFO D 类 shareholder_change First-Slice Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** shareholder_change first-slice live summary · **NOT APPROVED for production**",
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
        f"d_class_shareholder_change_first_slice_live_path_gate = {SHAREHOLDER_CHANGE_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_shareholder_change_first_slice_execution_gate = {gate}",
        "approval_status = NOT_APPROVED",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_first_slice_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_shareholder_change_first_slice_live(
    universe_rows: List[ShareholderChangeFirstSliceRow],
    output_paths: Dict[str, str],
) -> int:
    """shareholder_change 第一切片 live；仅 DSC001–DSC005 · type=inc+单一 tdate。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    component_cfg = copy.deepcopy(
        source_configs.get(SHAREHOLDER_CHANGE_FIRST_SLICE_COMPONENT, {})
    )
    endpoint = endpoints.get(
        SHAREHOLDER_CHANGE_FIRST_SLICE_COMPONENT,
        component_cfg.get("api_url", SHAREHOLDER_CHANGE_FIRST_SLICE_ENDPOINT),
    )

    for row in universe_rows:
        planned = compute_shareholder_change_first_slice_planned_requests(row)
        if planned > SHAREHOLDER_CHANGE_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            print(
                f"ERROR: {SHAREHOLDER_CHANGE_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"planned={planned}",
                file=sys.stderr,
            )
            return 2

    session = requests.Session()
    stats = LiveStats()
    case_summaries: Dict[str, Dict[str, str]] = {}

    for row in sorted(universe_rows, key=lambda r: r.case_id):
        case = shareholder_change_first_slice_row_to_universe_case(row)
        row_cfg = copy.deepcopy(component_cfg)
        # 独立 params：仅 type=inc + anchor tdate；不走 generic multi-probe
        param_list = _build_shareholder_change_first_slice_params(row)
        summary = execute_live_case(
            case,
            row_cfg,
            endpoint,
            session,
            stats,
            output_paths,
            param_list=param_list,
        )
        case_summaries[row.case_id] = summary
        print(
            f"{row.case_id} {summary['retrieval_status']}: "
            f"records={summary['record_count']} "
            f"requests={summary['cninfo_request_count']}",
            flush=True,
        )

    cap_issues = validate_shareholder_change_first_slice_request_caps(stats)
    if cap_issues:
        print(
            "ERROR: shareholder_change first-slice request cap validation failed: "
            f"{cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_shareholder_change_first_slice_execution_gate(
        universe_rows, case_summaries
    )
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = SHAREHOLDER_CHANGE_FIRST_SLICE_EXECUTION_GATE_FAIL

    live_rows = [
        build_shareholder_change_first_slice_live_row(
            row, case_summaries[row.case_id]
        )
        for row in sorted(universe_rows, key=lambda r: r.case_id)
        if row.case_id in case_summaries
    ]

    report_path = write_shareholder_change_first_slice_live_report(
        live_rows, output_paths
    )
    quality_path = write_shareholder_change_first_slice_quality_report(
        live_rows, output_paths
    )
    summary_path = write_shareholder_change_first_slice_live_summary(
        live_rows, stats, gate, output_paths
    )

    print(
        f"mode=shareholder_change_first_slice_live cases={len(live_rows)} "
        f"acceptable={sum(1 for r in live_rows if r['acceptable'] == 'yes')}/"
        f"{len(live_rows)} cninfo_calls={stats.cninfo_requests}"
    )
    print(
        f"gate=d_class_shareholder_change_first_slice_execution_gate={gate}"
    )
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == SHAREHOLDER_CHANGE_FIRST_SLICE_EXECUTION_GATE_PASS else 1


def run_shareholder_change_first_slice(args: argparse.Namespace) -> int:
    enforce_shareholder_change_first_slice_forbidden_options(args)
    enforce_shareholder_change_first_slice_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(
            f"ERROR: {SHAREHOLDER_CHANGE_FIRST_SLICE_UNIVERSE_CSV_REQUIRED}",
            file=sys.stderr,
        )
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_shareholder_change_first_slice_output_root(
        args.output_root
    )
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_shareholder_change_first_slice_universe(args.universe_csv)
    universe_issues = validate_shareholder_change_first_slice_universe(universe_rows)
    if universe_issues:
        print(
            "ERROR: shareholder_change first-slice universe validation failed: "
            f"{universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_shareholder_change_first_slice_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_shareholder_change_first_slice_live(
            universe_rows, output_paths
        )

    dry_rows = build_shareholder_change_first_slice_dryrun_rows(
        universe_rows, output_root
    )
    write_shareholder_change_first_slice_planned_snapshots(
        universe_rows, output_paths
    )
    report_path = write_shareholder_change_first_slice_dryrun_report(
        dry_rows, output_paths
    )
    summary_path = write_shareholder_change_first_slice_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    print(
        f"mode=shareholder_change_first_slice_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={planned_total} cninfo_calls=0"
    )
    print(
        "gate=d_class_shareholder_change_first_slice_runner_extension_gate="
        f"{SHAREHOLDER_CHANGE_FIRST_SLICE_RUNNER_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0



def load_executive_shareholding_first_slice_universe(
    path: str,
) -> List[ExecutiveShareholdingFirstSliceRow]:
    rows: List[ExecutiveShareholdingFirstSliceRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                ExecutiveShareholdingFirstSliceRow(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    component=str(row.get("component", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    time_mark=str(row.get("time_mark", "")).strip(),
                    vary_type=str(row.get("vary_type", "")).strip(),
                    first_slice_include=str(
                        row.get("first_slice_include", "")
                    ).strip(),
                    expected_behavior=str(
                        row.get("expected_behavior", "")
                    ).strip(),
                    exclude_flags=str(row.get("exclude_flags", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                    dlc007_reference=str(
                        row.get("dlc007_reference", "")
                    ).strip(),
                )
            )
    return rows


def build_executive_shareholding_first_slice_plan(
    time_mark: str = EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TIME_MARK,
    vary_type: str = EXECUTIVE_SHAREHOLDING_FIRST_SLICE_VARY_TYPE,
) -> List[str]:
    """executive_shareholding 第一切片计划：仅 timeMark=oneMonth + varyType=b。"""
    return [f"timeMark_{time_mark}_varyType_{vary_type}"]


def _build_executive_shareholding_first_slice_params(
    row: ExecutiveShareholdingFirstSliceRow,
) -> List[Dict[str, Any]]:
    """独立 params builder；禁止复用 generic multi-probe（threeMonth/oneYear）。"""
    return [{"timeMark": row.time_mark, "varyType": row.vary_type}]


def compute_executive_shareholding_first_slice_planned_requests(
    row: ExecutiveShareholdingFirstSliceRow,
) -> int:
    plan = build_executive_shareholding_first_slice_plan(row.time_mark, row.vary_type)
    return len(plan)


def resolve_executive_shareholding_first_slice_fixture_refs(
    case_id: str,
) -> List[str]:
    names = EXECUTIVE_SHAREHOLDING_FIRST_SLICE_CASE_FIXTURES.get(case_id, ())
    return [
        os.path.join(EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FIXTURE_DIR, name)
        for name in names
    ]


def validate_executive_shareholding_first_slice_fixtures(
    rows: List[ExecutiveShareholdingFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    for row in rows:
        refs = resolve_executive_shareholding_first_slice_fixture_refs(row.case_id)
        if not refs:
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FIXTURE_MISSING}:{row.case_id}"
            )
            continue
        for ref in refs:
            if not os.path.isfile(ref):
                issues.append(
                    f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FIXTURE_MISSING}:"
                    f"{row.case_id}:{os.path.basename(ref)}"
                )
    return issues


def validate_executive_shareholding_first_slice_universe(
    rows: List[ExecutiveShareholdingFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    if len(rows) != EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE:
        issues.append(
            f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH}:got={len(rows)}"
        )
    seen_ids: Set[str] = set()
    total_planned = 0
    for row in rows:
        case_id = row.case_id
        if case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_ids.add(case_id)
        if case_id not in EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ALLOWED_CASE_IDS:
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FORBIDDEN_CASE_ID}:{case_id}"
            )
        if row.company_code in EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FORBIDDEN_COMPANY_CODES:
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE}:"
                f"{row.company_code}"
            )
        expected_code = EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(
            case_id
        )
        if expected_code and row.company_code != expected_code:
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_COMPANY_CODE}:"
                f"{case_id}={row.company_code}"
            )
        if row.component != EXECUTIVE_SHAREHOLDING_FIRST_SLICE_COMPONENT:
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_COMPONENT}:{case_id}"
            )
        if row.first_slice_include.lower() != "yes":
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_INCLUDE_REQUIRED}:{case_id}"
            )
        if row.time_mark != EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TIME_MARK:
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_TIME_MARK}:"
                f"{case_id}={row.time_mark}"
            )
        if row.vary_type != EXECUTIVE_SHAREHOLDING_FIRST_SLICE_VARY_TYPE:
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_VARY_TYPE}:"
                f"{case_id}={row.vary_type}"
            )
        planned = compute_executive_shareholding_first_slice_planned_requests(row)
        if planned > EXECUTIVE_SHAREHOLDING_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"{case_id}={planned}"
            )
        total_planned += planned
    for required_id in sorted(EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ALLOWED_CASE_IDS):
        if required_id not in seen_ids:
            issues.append(f"missing_case_id:{required_id}")
    if total_planned > EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{total_planned}"
        )
    issues.extend(validate_executive_shareholding_first_slice_fixtures(rows))
    return issues


def validate_executive_shareholding_first_slice_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(
        DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT
    )
    v1_root = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v2_root = _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT)
    replacement_root = _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT)
    targeted_root = _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT)
    equity_pledge_root = _normalize_output_root(
        DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT
    )
    margin_root = _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT)
    disclosure_root = _normalize_output_root(
        DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT
    )
    block_trade_root = _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT)
    rsu_root = _normalize_output_root(
        DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
    )
    sc_root = _normalize_output_root(
        DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT
    )
    blocked_pairs = [
        (v1_root, EXECUTIVE_SHAREHOLDING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED),
        (v2_root, EXECUTIVE_SHAREHOLDING_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED),
        (
            replacement_root,
            EXECUTIVE_SHAREHOLDING_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            targeted_root,
            EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            equity_pledge_root,
            EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (margin_root, EXECUTIVE_SHAREHOLDING_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED),
        (
            disclosure_root,
            EXECUTIVE_SHAREHOLDING_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            block_trade_root,
            EXECUTIVE_SHAREHOLDING_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (rsu_root, EXECUTIVE_SHAREHOLDING_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED),
        (
            sc_root,
            EXECUTIVE_SHAREHOLDING_FIRST_SLICE_SHAREHOLDER_CHANGE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
    ]
    for blocked_root, token in blocked_pairs:
        if root == blocked_root or root.startswith(blocked_root + os.sep):
            return False, token
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT_REQUIRED


def enforce_executive_shareholding_first_slice_write_block_targets(
    output_paths: Dict[str, str],
) -> None:
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {EXECUTIVE_SHAREHOLDING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_executive_shareholding_first_slice_forbidden_options(
    args: argparse.Namespace,
) -> None:
    enforce_forbidden_options(args)
    mixed_modes = [
        ("known_event_replacement", args.known_event_replacement),
        ("known_event_targeted_probe", args.known_event_targeted_probe),
        ("bounded_probe_v2", args.bounded_probe_v2),
        ("margin_trading_first_slice", args.margin_trading_first_slice),
        ("block_trade_first_slice", args.block_trade_first_slice),
        ("restricted_shares_unlock_first_slice", args.restricted_shares_unlock_first_slice),
        ("equity_pledge_first_slice", args.equity_pledge_first_slice),
        ("shareholder_change_first_slice", args.shareholder_change_first_slice),
        ("abnormal_trading_first_slice", args.abnormal_trading_first_slice),
        ("shareholder_data_first_slice", args.shareholder_data_first_slice),
        ("fund_industry_allocation_first_slice", args.fund_industry_allocation_first_slice),
    ]
    for name, enabled in mixed_modes:
        if args.executive_shareholding_first_slice and enabled:
            print(
                f"ERROR: {EXECUTIVE_SHAREHOLDING_FIRST_SLICE_MIXED_MODE_BLOCKED}:{name}",
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
        (
            "approve_d_class_margin_trading_first_slice",
            args.approve_d_class_margin_trading_first_slice,
        ),
        (
            "approve_d_class_block_trade_first_slice",
            args.approve_d_class_block_trade_first_slice,
        ),
        (
            "approve_d_class_restricted_shares_unlock_first_slice",
            args.approve_d_class_restricted_shares_unlock_first_slice,
        ),
        (
            "approve_d_class_equity_pledge_first_slice",
            args.approve_d_class_equity_pledge_first_slice,
        ),
        (
            "approve_d_class_shareholder_change_first_slice",
            args.approve_d_class_shareholder_change_first_slice,
        ),
        (
            "approve_d_class_abnormal_trading_first_slice",
            args.approve_d_class_abnormal_trading_first_slice,
        ),
        (
            "approve_d_class_shareholder_data_first_slice",
            args.approve_d_class_shareholder_data_first_slice,
        ),
        (
            "approve_d_class_fund_industry_allocation_first_slice",
            args.approve_d_class_fund_industry_allocation_first_slice,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.executive_shareholding_first_slice and enabled:
            print(
                f"ERROR: {EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_APPROVAL_FLAG}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    if (
        not args.executive_shareholding_first_slice
        and args.approve_d_class_executive_shareholding_first_slice
    ):
        print(
            f"ERROR: {EXECUTIVE_SHAREHOLDING_FIRST_SLICE_WRONG_APPROVAL_FLAG}:"
            "executive_shareholding_first_slice_flag_without_mode",
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


def enforce_executive_shareholding_first_slice_live_approval_gate(
    args: argparse.Namespace,
) -> None:
    if args.mode == "live" and args.executive_shareholding_first_slice:
        if not args.approve_d_class_executive_shareholding_first_slice:
            print(
                f"ERROR: {EXECUTIVE_SHAREHOLDING_FIRST_SLICE_APPROVAL_REQUIRED}",
                file=sys.stderr,
            )
            sys.exit(2)


def build_executive_shareholding_first_slice_dryrun_rows(
    rows: List[ExecutiveShareholdingFirstSliceRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    for row in rows:
        planned_requests = compute_executive_shareholding_first_slice_planned_requests(row)
        plan = build_executive_shareholding_first_slice_plan(
            row.time_mark, row.vary_type
        )
        fixture_refs = resolve_executive_shareholding_first_slice_fixture_refs(row.case_id)
        dry_rows.append(
            {
                "case_id": row.case_id,
                "company_code": row.company_code,
                "company_name": row.company_name,
                "component": row.component,
                "market": row.market,
                "time_mark": row.time_mark,
                "vary_type": row.vary_type,
                "first_slice_include": row.first_slice_include,
                "expected_behavior": row.expected_behavior,
                "planned_request_count": str(planned_requests),
                "planned_output_root": output_root,
                "planned_endpoint": EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ENDPOINT,
                "fixture_refs": ";".join(
                    os.path.basename(p) for p in fixture_refs
                ),
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
                    f"timeMark={row.time_mark}; varyType={row.vary_type}; "
                    f"plan={','.join(plan)}; query_mode=timeMark_varyType_single; "
                    f"empty_but_valid_allowed=yes; not_generic_multi_probe=yes; "
                    f"tier1_fixtures={len(fixture_refs)}"
                ),
            }
        )
    return dry_rows


def write_executive_shareholding_first_slice_planned_snapshots(
    rows: List[ExecutiveShareholdingFirstSliceRow],
    output_paths: Dict[str, str],
) -> None:
    """写入 dry-run planned_snapshots（synthetic · cninfo_called=false · Tier-1 fixture refs）。"""
    for row in rows:
        plan = build_executive_shareholding_first_slice_plan(
            row.time_mark, row.vary_type
        )
        params = _build_executive_shareholding_first_slice_params(row)
        fixture_refs = resolve_executive_shareholding_first_slice_fixture_refs(row.case_id)
        snap_path = os.path.join(
            output_paths["planned_snapshots"],
            f"{row.case_id}_{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_COMPONENT}.json",
        )
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case_id": row.case_id,
                    "company_code": row.company_code,
                    "company_name": row.company_name,
                    "component": row.component,
                    "market": row.market,
                    "time_mark": row.time_mark,
                    "vary_type": row.vary_type,
                    "expected_behavior": row.expected_behavior,
                    "mode": "dry_run",
                    "endpoint": EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ENDPOINT,
                    "planned_params": params,
                    "planned_request_labels": plan,
                    "tier1_fixture_refs": [
                        os.path.relpath(p, BASE_DIR) if p.startswith(BASE_DIR) else p
                        for p in fixture_refs
                    ],
                    "cninfo_called": False,
                    "pdf_download": False,
                    "ocr": False,
                    "extraction": False,
                    "db_write": False,
                    "minio_write": False,
                    "rag_run": False,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )


def write_executive_shareholding_first_slice_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_executive_shareholding_first_slice_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=EXECUTIVE_SHAREHOLDING_FIRST_SLICE_DRYRUN_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_executive_shareholding_first_slice_dryrun_summary(
    dry_rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    fixture_total = sum(
        len(str(r.get("fixture_refs", "")).split(";"))
        for r in dry_rows
        if r.get("fixture_refs")
    )
    lines = [
        "# CNINFO D 类 executive_shareholding First-Slice Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** executive_shareholding first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for production**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_request_count_total | **{planned_total}** |",
        f"| tier1_fixture_refs | **{fixture_total}** |",
        f"| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        f"- component: **executive_shareholding**",
        f"- endpoint: `{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ENDPOINT}`",
        f"- query mode: **timeMark=oneMonth + varyType=b**（禁止 threeMonth/oneYear/s）",
        f"- time_mark: **{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TIME_MARK}**",
        f"- vary_type: **{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_VARY_TYPE}**",
        "",
        "## Tier-1 Fixtures",
        "",
        f"- fixture root: `fixtures/d_class/executive_shareholding_first_slice/`",
        f"- wired into planned_snapshots for DES001–DES005",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_executive_shareholding_first_slice_runner_extension_gate = {EXECUTIVE_SHAREHOLDING_FIRST_SLICE_RUNNER_GATE}",
        "approval_status = NOT_APPROVED_FOR_PRODUCTION",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_executive_shareholding_first_slice_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def executive_shareholding_first_slice_row_to_universe_case(
    row: ExecutiveShareholdingFirstSliceRow,
) -> UniverseCase:
    """将 executive_shareholding 第一切片 universe 行转为探测用 UniverseCase。"""
    return UniverseCase(
        case_id=row.case_id,
        company_code=row.company_code,
        company_name=row.company_name,
        component=row.component,
        market=row.market,
        risk_level="",
        expected_behavior=row.expected_behavior,
        reason=row.notes,
    )


def is_executive_shareholding_first_slice_acceptable(
    row: ExecutiveShareholdingFirstSliceRow,
    summary: Dict[str, str],
) -> bool:
    """第一切片 acceptable 判定；禁止 disclosure-only 升级为 captured_normal。"""
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    eb = row.expected_behavior
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if "disclosure" in row.notes.lower() and rs != "found":
        return False
    if eb == "empty_but_valid" and rs == "empty_but_valid" and rc == 0:
        return True
    if "empty_but_valid" in eb and rs == "empty_but_valid" and rc == 0:
        return True
    if "captured_normal_or_empty_but_valid" in eb and (
        (rs == "found" and rc >= 1) or (rs == "empty_but_valid" and rc == 0)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal_or_needs_review" in eb and (
        (rs == "found" and rc >= 1) or (rs == "needs_review" and rc >= 1)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal" in eb and rs == "found" and rc >= 1 and qs in (
        "pass",
        "needs_review",
    ):
        return True
    if rs == "found" and rc >= 1 and qs in ("pass", "needs_review"):
        return True
    return False


def assess_executive_shareholding_first_slice_failure_type(
    row: ExecutiveShareholdingFirstSliceRow,
    summary: Dict[str, str],
) -> str:
    if is_executive_shareholding_first_slice_acceptable(row, summary):
        return ""
    rs = summary.get("retrieval_status", "")
    if rs in ("http_error", "blocked"):
        return "transport_or_http_error"
    return "expectation_mismatch"


def validate_executive_shareholding_first_slice_request_caps(stats: LiveStats) -> List[str]:
    issues: List[str] = []
    for case_id, count in stats.case_request_counts.items():
        if count > EXECUTIVE_SHAREHOLDING_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"{case_id}={count}"
            )
    if stats.cninfo_requests > EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:"
            f"{stats.cninfo_requests}"
        )
    return issues


def compute_executive_shareholding_first_slice_execution_gate(
    universe_rows: List[ExecutiveShareholdingFirstSliceRow],
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """executive_shareholding 第一切片 live 执行 gate；≥3/5 acceptable → PASS_WITH_CAVEAT。"""
    acceptable = 0
    for row in universe_rows:
        summary = case_summaries.get(row.case_id, {})
        if is_executive_shareholding_first_slice_acceptable(row, summary):
            acceptable += 1
    if acceptable >= 3:
        return EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXECUTION_GATE_PASS
    return EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXECUTION_GATE_FAIL


def build_executive_shareholding_first_slice_live_row(
    row: ExecutiveShareholdingFirstSliceRow,
    summary: Dict[str, str],
) -> Dict[str, str]:
    acceptable = is_executive_shareholding_first_slice_acceptable(row, summary)
    failure_type = assess_executive_shareholding_first_slice_failure_type(row, summary)
    return {
        "case_id": row.case_id,
        "company_code": row.company_code,
        "company_name": row.company_name,
        "component": row.component,
        "market": row.market,
        "time_mark": row.time_mark,
        "vary_type": row.vary_type,
        "expected_behavior": row.expected_behavior,
        "retrieval_status": summary.get("retrieval_status", ""),
        "quality_status": summary.get("quality_status", ""),
        "lineage_status": summary.get("lineage_status", ""),
        "record_count": summary.get("record_count", "0"),
        "empty_but_valid": summary.get("empty_but_valid", "no"),
        "needs_review": summary.get("needs_review", "no"),
        "endpoint_used": summary.get("endpoint_used", EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ENDPOINT),
        "cninfo_request_count": summary.get("cninfo_request_count", "0"),
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


def write_executive_shareholding_first_slice_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_executive_shareholding_first_slice_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=EXECUTIVE_SHAREHOLDING_FIRST_SLICE_LIVE_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_executive_shareholding_first_slice_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    quality_rows = [
        {
            "case_id": r["case_id"],
            "component": r["component"],
            "time_mark": r["time_mark"],
            "vary_type": r["vary_type"],
            "expected_behavior": r["expected_behavior"],
            "retrieval_status": r["retrieval_status"],
            "record_count": r["record_count"],
            "quality_status": r["quality_status"],
            "acceptable": r["acceptable"],
            "failure_type": r["failure_type"],
            "cninfo_request_count": r["cninfo_request_count"],
            "notes": r["notes"],
        }
        for r in rows
    ]
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_executive_shareholding_first_slice_quality_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=EXECUTIVE_SHAREHOLDING_FIRST_SLICE_QUALITY_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_executive_shareholding_first_slice_live_summary(
    live_rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    acceptable = sum(1 for r in live_rows if r["acceptable"] == "yes")
    lines = [
        "# CNINFO D 类 executive_shareholding First-Slice Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** executive_shareholding first-slice live summary · **NOT APPROVED for production**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(live_rows)}** |",
        f"| acceptable | **{acceptable}/{len(live_rows)}** |",
        f"| CNINFO requests | **{stats.cninfo_requests}** |",
        f"| DB writes | **{stats.db_writes}** |",
        f"| MinIO writes | **{stats.minio_writes}** |",
        f"| RAG runs | **{stats.rag_runs}** |",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_executive_shareholding_first_slice_live_path_gate = {EXECUTIVE_SHAREHOLDING_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_executive_shareholding_first_slice_execution_gate = {gate}",
        "```",
        "",
        "**NOT verified** · **NOT production_ready**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_executive_shareholding_first_slice_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_executive_shareholding_first_slice_live(
    universe_rows: List[ExecutiveShareholdingFirstSliceRow],
    output_paths: Dict[str, str],
) -> int:
    """executive_shareholding 第一切片 live；仅 DES001–DES005 · timeMark=oneMonth+varyType=b。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    component_cfg = copy.deepcopy(
        source_configs.get(EXECUTIVE_SHAREHOLDING_FIRST_SLICE_COMPONENT, {})
    )
    endpoint = endpoints.get(
        EXECUTIVE_SHAREHOLDING_FIRST_SLICE_COMPONENT,
        component_cfg.get("api_url", EXECUTIVE_SHAREHOLDING_FIRST_SLICE_ENDPOINT),
    )

    for row in universe_rows:
        planned = compute_executive_shareholding_first_slice_planned_requests(row)
        if planned > EXECUTIVE_SHAREHOLDING_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            print(
                f"ERROR: {EXECUTIVE_SHAREHOLDING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"planned={planned}",
                file=sys.stderr,
            )
            return 2

    session = requests.Session()
    stats = LiveStats()
    case_summaries: Dict[str, Dict[str, str]] = {}

    for row in sorted(universe_rows, key=lambda r: r.case_id):
        case = executive_shareholding_first_slice_row_to_universe_case(row)
        row_cfg = copy.deepcopy(component_cfg)
        # 独立 params：仅 oneMonth+b；不走 generic multi-probe
        param_list = _build_executive_shareholding_first_slice_params(row)
        summary = execute_live_case(
            case,
            row_cfg,
            endpoint,
            session,
            stats,
            output_paths,
            param_list=param_list,
        )
        case_summaries[row.case_id] = summary
        print(
            f"{row.case_id} {summary['retrieval_status']}: "
            f"records={summary['record_count']} "
            f"requests={summary['cninfo_request_count']}",
            flush=True,
        )

    cap_issues = validate_executive_shareholding_first_slice_request_caps(stats)
    if cap_issues:
        print(
            "ERROR: executive_shareholding first-slice request cap validation failed: "
            f"{cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_executive_shareholding_first_slice_execution_gate(
        universe_rows, case_summaries
    )
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXECUTION_GATE_FAIL

    live_rows = [
        build_executive_shareholding_first_slice_live_row(
            row, case_summaries[row.case_id]
        )
        for row in sorted(universe_rows, key=lambda r: r.case_id)
        if row.case_id in case_summaries
    ]

    report_path = write_executive_shareholding_first_slice_live_report(
        live_rows, output_paths
    )
    quality_path = write_executive_shareholding_first_slice_quality_report(
        live_rows, output_paths
    )
    summary_path = write_executive_shareholding_first_slice_live_summary(
        live_rows, stats, gate, output_paths
    )

    print(
        f"mode=executive_shareholding_first_slice_live cases={len(live_rows)} "
        f"acceptable={sum(1 for r in live_rows if r['acceptable'] == 'yes')}/"
        f"{len(live_rows)} cninfo_calls={stats.cninfo_requests}"
    )
    print(
        f"gate=d_class_executive_shareholding_first_slice_execution_gate={gate}"
    )
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == EXECUTIVE_SHAREHOLDING_FIRST_SLICE_EXECUTION_GATE_PASS else 1


def run_executive_shareholding_first_slice(args: argparse.Namespace) -> int:
    enforce_executive_shareholding_first_slice_forbidden_options(args)
    enforce_executive_shareholding_first_slice_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(
            f"ERROR: {EXECUTIVE_SHAREHOLDING_FIRST_SLICE_UNIVERSE_CSV_REQUIRED}",
            file=sys.stderr,
        )
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_executive_shareholding_first_slice_output_root(
        args.output_root
    )
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_executive_shareholding_first_slice_universe(args.universe_csv)
    universe_issues = validate_executive_shareholding_first_slice_universe(universe_rows)
    if universe_issues:
        print(
            "ERROR: executive_shareholding first-slice universe validation failed: "
            f"{universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_executive_shareholding_first_slice_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_executive_shareholding_first_slice_live(
            universe_rows, output_paths
        )

    dry_rows = build_executive_shareholding_first_slice_dryrun_rows(
        universe_rows, output_root
    )
    write_executive_shareholding_first_slice_planned_snapshots(
        universe_rows, output_paths
    )
    report_path = write_executive_shareholding_first_slice_dryrun_report(
        dry_rows, output_paths
    )
    summary_path = write_executive_shareholding_first_slice_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    print(
        f"mode=executive_shareholding_first_slice_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={planned_total} cninfo_calls=0"
    )
    print(
        "gate=d_class_executive_shareholding_first_slice_runner_extension_gate="
        f"{EXECUTIVE_SHAREHOLDING_FIRST_SLICE_RUNNER_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0



def load_abnormal_trading_first_slice_universe(
    path: str,
) -> List[AbnormalTradingFirstSliceRow]:
    rows: List[AbnormalTradingFirstSliceRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                AbnormalTradingFirstSliceRow(
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
                    exclude_flags=str(row.get("exclude_flags", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                    sample_raw_reference=str(
                        row.get("sample_raw_reference", "")
                    ).strip(),
                )
            )
    return rows


def build_abnormal_trading_first_slice_plan(
    anchor_tdate: str = ABNORMAL_TRADING_FIRST_SLICE_ANCHOR_TDATE,
) -> List[str]:
    """abnormal_trading 第一切片计划：单日 marketList · single_day_paged。"""
    return [f"single_day_paged_{anchor_tdate}"]


def _build_abnormal_trading_first_slice_params(
    row: AbnormalTradingFirstSliceRow,
) -> List[Dict[str, Any]]:
    return [
        {
            "sdate": row.anchor_tdate,
            "edate": row.anchor_tdate,
            "platecode": "",
            "orderby": "",
            "page": 1,
            "rows": 30,
        }
    ]


def compute_abnormal_trading_first_slice_planned_requests(
    row: AbnormalTradingFirstSliceRow,
) -> int:
    return len(build_abnormal_trading_first_slice_plan(row.anchor_tdate))


def resolve_abnormal_trading_first_slice_fixture_refs(case_id: str) -> List[str]:
    names = ABNORMAL_TRADING_FIRST_SLICE_CASE_FIXTURES.get(case_id, ())
    return [
        os.path.join(ABNORMAL_TRADING_FIRST_SLICE_FIXTURE_DIR, name) for name in names
    ]


def validate_abnormal_trading_first_slice_fixtures(
    rows: List[AbnormalTradingFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    for row in rows:
        refs = resolve_abnormal_trading_first_slice_fixture_refs(row.case_id)
        if not refs:
            issues.append(
                f"{ABNORMAL_TRADING_FIRST_SLICE_FIXTURE_MISSING}:{row.case_id}"
            )
            continue
        for ref in refs:
            if not os.path.isfile(ref):
                issues.append(
                    f"{ABNORMAL_TRADING_FIRST_SLICE_FIXTURE_MISSING}:"
                    f"{row.case_id}:{os.path.basename(ref)}"
                )
    return issues


def validate_abnormal_trading_first_slice_universe(
    rows: List[AbnormalTradingFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    if len(rows) != ABNORMAL_TRADING_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE:
        issues.append(
            f"{ABNORMAL_TRADING_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH}:got={len(rows)}"
        )
    seen_ids: Set[str] = set()
    total_planned = 0
    for row in rows:
        case_id = row.case_id
        if case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_ids.add(case_id)
        if case_id not in ABNORMAL_TRADING_FIRST_SLICE_ALLOWED_CASE_IDS:
            issues.append(
                f"{ABNORMAL_TRADING_FIRST_SLICE_FORBIDDEN_CASE_ID}:{case_id}"
            )
        if row.company_code in ABNORMAL_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODES:
            issues.append(
                f"{ABNORMAL_TRADING_FIRST_SLICE_FORBIDDEN_COMPANY_CODE}:"
                f"{row.company_code}"
            )
        expected_code = ABNORMAL_TRADING_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(case_id)
        if expected_code and row.company_code != expected_code:
            issues.append(
                f"{ABNORMAL_TRADING_FIRST_SLICE_WRONG_COMPANY_CODE}:"
                f"{case_id}={row.company_code}"
            )
        if row.component != ABNORMAL_TRADING_FIRST_SLICE_COMPONENT:
            issues.append(f"{ABNORMAL_TRADING_FIRST_SLICE_WRONG_COMPONENT}:{case_id}")
        if row.first_slice_include.lower() != "yes":
            issues.append(f"{ABNORMAL_TRADING_FIRST_SLICE_INCLUDE_REQUIRED}:{case_id}")
        if row.anchor_tdate != ABNORMAL_TRADING_FIRST_SLICE_ANCHOR_TDATE:
            issues.append(
                f"{ABNORMAL_TRADING_FIRST_SLICE_WRONG_ANCHOR_TDATE}:"
                f"{case_id}={row.anchor_tdate}"
            )
        planned = compute_abnormal_trading_first_slice_planned_requests(row)
        if planned > ABNORMAL_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{ABNORMAL_TRADING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"{case_id}={planned}"
            )
        total_planned += planned
    for required_id in sorted(ABNORMAL_TRADING_FIRST_SLICE_ALLOWED_CASE_IDS):
        if required_id not in seen_ids:
            issues.append(f"missing_case_id:{required_id}")
    if total_planned > ABNORMAL_TRADING_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{ABNORMAL_TRADING_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{total_planned}"
        )
    issues.extend(validate_abnormal_trading_first_slice_fixtures(rows))
    return issues


def validate_abnormal_trading_first_slice_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT)
    blocked_pairs = [
        (
            _normalize_output_root(DEFAULT_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_EXECUTIVE_SHAREHOLDING_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_SHAREHOLDER_CHANGE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(
                DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
            ),
            ABNORMAL_TRADING_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_SHAREHOLDER_DATA_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT),
            ABNORMAL_TRADING_FIRST_SLICE_FUND_INDUSTRY_ALLOCATION_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
    ]
    for blocked_root, token in blocked_pairs:
        if root == blocked_root or root.startswith(blocked_root + os.sep):
            return False, token
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT_REQUIRED


def enforce_abnormal_trading_first_slice_write_block_targets(
    output_paths: Dict[str, str],
) -> None:
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {ABNORMAL_TRADING_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_abnormal_trading_first_slice_forbidden_options(
    args: argparse.Namespace,
) -> None:
    enforce_forbidden_options(args)
    mixed_modes = [
        ("known_event_replacement", args.known_event_replacement),
        ("known_event_targeted_probe", args.known_event_targeted_probe),
        ("bounded_probe_v2", args.bounded_probe_v2),
        ("margin_trading_first_slice", args.margin_trading_first_slice),
        ("block_trade_first_slice", args.block_trade_first_slice),
        ("restricted_shares_unlock_first_slice", args.restricted_shares_unlock_first_slice),
        ("equity_pledge_first_slice", args.equity_pledge_first_slice),
        ("shareholder_change_first_slice", args.shareholder_change_first_slice),
        ("executive_shareholding_first_slice", args.executive_shareholding_first_slice),
        ("shareholder_data_first_slice", args.shareholder_data_first_slice),
        ("fund_industry_allocation_first_slice", args.fund_industry_allocation_first_slice),
    ]
    for name, enabled in mixed_modes:
        if args.abnormal_trading_first_slice and enabled:
            print(
                f"ERROR: {ABNORMAL_TRADING_FIRST_SLICE_MIXED_MODE_BLOCKED}:{name}",
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
        (
            "approve_d_class_margin_trading_first_slice",
            args.approve_d_class_margin_trading_first_slice,
        ),
        (
            "approve_d_class_block_trade_first_slice",
            args.approve_d_class_block_trade_first_slice,
        ),
        (
            "approve_d_class_restricted_shares_unlock_first_slice",
            args.approve_d_class_restricted_shares_unlock_first_slice,
        ),
        (
            "approve_d_class_equity_pledge_first_slice",
            args.approve_d_class_equity_pledge_first_slice,
        ),
        (
            "approve_d_class_shareholder_change_first_slice",
            args.approve_d_class_shareholder_change_first_slice,
        ),
        (
            "approve_d_class_executive_shareholding_first_slice",
            args.approve_d_class_executive_shareholding_first_slice,
        ),
        (
            "approve_d_class_shareholder_data_first_slice",
            args.approve_d_class_shareholder_data_first_slice,
        ),
        (
            "approve_d_class_fund_industry_allocation_first_slice",
            args.approve_d_class_fund_industry_allocation_first_slice,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.abnormal_trading_first_slice and enabled:
            print(
                f"ERROR: {ABNORMAL_TRADING_FIRST_SLICE_WRONG_APPROVAL_FLAG}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    if (
        not args.abnormal_trading_first_slice
        and args.approve_d_class_abnormal_trading_first_slice
    ):
        print(
            f"ERROR: {ABNORMAL_TRADING_FIRST_SLICE_WRONG_APPROVAL_FLAG}:"
            "abnormal_trading_first_slice_flag_without_mode",
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


def enforce_abnormal_trading_first_slice_live_approval_gate(
    args: argparse.Namespace,
) -> None:
    if args.mode == "live" and args.abnormal_trading_first_slice:
        if not args.approve_d_class_abnormal_trading_first_slice:
            print(
                f"ERROR: {ABNORMAL_TRADING_FIRST_SLICE_APPROVAL_REQUIRED}",
                file=sys.stderr,
            )
            sys.exit(2)


def build_abnormal_trading_first_slice_dryrun_rows(
    rows: List[AbnormalTradingFirstSliceRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    for row in rows:
        planned_requests = compute_abnormal_trading_first_slice_planned_requests(row)
        plan = build_abnormal_trading_first_slice_plan(row.anchor_tdate)
        fixture_refs = resolve_abnormal_trading_first_slice_fixture_refs(row.case_id)
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
                "planned_endpoint": ABNORMAL_TRADING_FIRST_SLICE_ENDPOINT,
                "fixture_refs": ";".join(os.path.basename(r) for r in fixture_refs),
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
                    f"query_mode=single_day_paged; empty_but_valid_allowed=yes; "
                    f"not_generic_multi_probe=yes; detail_nested_deferred=yes; "
                    f"tier1_fixtures={len(fixture_refs)}"
                ),
            }
        )
    return dry_rows


def write_abnormal_trading_first_slice_planned_snapshots(
    rows: List[AbnormalTradingFirstSliceRow],
    output_paths: Dict[str, str],
) -> None:
    snap_dir = os.path.join(output_paths["root"], "planned_snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    for row in rows:
        plan = build_abnormal_trading_first_slice_plan(row.anchor_tdate)
        params = _build_abnormal_trading_first_slice_params(row)
        fixture_refs = resolve_abnormal_trading_first_slice_fixture_refs(row.case_id)
        payload = {
            "case_id": row.case_id,
            "company_code": row.company_code,
            "company_name": row.company_name,
            "component": row.component,
            "anchor_tdate": row.anchor_tdate,
            "query_mode": "single_day_paged",
            "planned_requests": plan,
            "query_params": params,
            "endpoint": ABNORMAL_TRADING_FIRST_SLICE_ENDPOINT,
            "records_path": "marketList",
            "expected_behavior": row.expected_behavior,
            "fixture_refs": [
                os.path.relpath(r, BASE_DIR).replace("\\", "/") for r in fixture_refs
            ],
            "cninfo_called": False,
            "detail_nested_deferred": True,
        }
        out = os.path.join(snap_dir, f"{row.case_id}_abnormal_trading.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")


def write_abnormal_trading_first_slice_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_abnormal_trading_first_slice_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=ABNORMAL_TRADING_FIRST_SLICE_DRYRUN_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_abnormal_trading_first_slice_dryrun_summary(
    dry_rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    lines = [
        "# CNINFO D 类 abnormal_trading First-Slice Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** abnormal_trading first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for production**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_request_count_total | **{planned_total}** |",
        f"| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        "- component: **abnormal_trading**",
        f"- endpoint: `{ABNORMAL_TRADING_FIRST_SLICE_ENDPOINT}`",
        "- query mode: **single_day_paged**",
        f"- anchor_tdate: **{ABNORMAL_TRADING_FIRST_SLICE_ANCHOR_TDATE}**",
        "- records_path: **marketList**",
        "- fixture root: `fixtures/d_class/abnormal_trading_first_slice/`",
        "- detail[]: **deferred** (d_event_party_detail)",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_abnormal_trading_first_slice_runner_extension_gate = {ABNORMAL_TRADING_FIRST_SLICE_RUNNER_GATE}",
        "approval_status = STANDING_SCOPE_AUTHORIZED_OFFLINE",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_abnormal_trading_first_slice_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def abnormal_trading_first_slice_row_to_universe_case(
    row: AbnormalTradingFirstSliceRow,
) -> UniverseCase:
    """将 abnormal_trading 第一切片 universe 行转为探测用 UniverseCase。"""
    return UniverseCase(
        case_id=row.case_id,
        company_code=row.company_code,
        company_name=row.company_name,
        component=row.component,
        market=row.market,
        risk_level="",
        expected_behavior=row.expected_behavior,
        reason=row.notes,
    )


def is_abnormal_trading_first_slice_acceptable(
    row: AbnormalTradingFirstSliceRow,
    summary: Dict[str, str],
) -> bool:
    """第一切片 acceptable 判定；禁止 disclosure-only 升级为 captured_normal。"""
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    eb = row.expected_behavior
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if "disclosure" in row.notes.lower() and rs != "found":
        return False
    if eb == "empty_but_valid" and rs == "empty_but_valid" and rc == 0:
        return True
    if "empty_but_valid" in eb and rs == "empty_but_valid" and rc == 0:
        return True
    if "captured_normal_or_empty_but_valid" in eb and (
        (rs == "found" and rc >= 1) or (rs == "empty_but_valid" and rc == 0)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal_or_needs_review" in eb and (
        (rs == "found" and rc >= 1) or (rs == "needs_review" and rc >= 1)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal" in eb and rs == "found" and rc >= 1 and qs in (
        "pass",
        "needs_review",
    ):
        return True
    if rs == "found" and rc >= 1 and qs in ("pass", "needs_review"):
        return True
    if rs == "needs_review" and rc >= 1 and qs == "needs_review":
        return "needs_review" in eb or "captured_normal" in eb
    return False


def assess_abnormal_trading_first_slice_failure_type(
    row: AbnormalTradingFirstSliceRow,
    summary: Dict[str, str],
) -> str:
    if is_abnormal_trading_first_slice_acceptable(row, summary):
        return ""
    rs = summary.get("retrieval_status", "")
    if rs in ("http_error", "blocked"):
        return "transport_or_http_error"
    return "expectation_mismatch"


def validate_abnormal_trading_first_slice_request_caps(stats: LiveStats) -> List[str]:
    issues: List[str] = []
    for case_id, count in stats.case_request_counts.items():
        if count > ABNORMAL_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{ABNORMAL_TRADING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"{case_id}={count}"
            )
    if stats.cninfo_requests > ABNORMAL_TRADING_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{ABNORMAL_TRADING_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:"
            f"{stats.cninfo_requests}"
        )
    return issues


def compute_abnormal_trading_first_slice_execution_gate(
    universe_rows: List[AbnormalTradingFirstSliceRow],
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """abnormal_trading 第一切片 live 执行 gate；≥3/5 acceptable → PASS_WITH_CAVEAT。"""
    acceptable = 0
    for row in universe_rows:
        summary = case_summaries.get(row.case_id, {})
        if is_abnormal_trading_first_slice_acceptable(row, summary):
            acceptable += 1
    if acceptable >= 3:
        return ABNORMAL_TRADING_FIRST_SLICE_EXECUTION_GATE_PASS
    return ABNORMAL_TRADING_FIRST_SLICE_EXECUTION_GATE_FAIL


def build_abnormal_trading_first_slice_live_row(
    row: AbnormalTradingFirstSliceRow,
    summary: Dict[str, str],
) -> Dict[str, str]:
    acceptable = is_abnormal_trading_first_slice_acceptable(row, summary)
    failure_type = assess_abnormal_trading_first_slice_failure_type(row, summary)
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
        "endpoint_used": summary.get(
            "endpoint_used", ABNORMAL_TRADING_FIRST_SLICE_ENDPOINT
        ),
        "cninfo_request_count": summary.get("cninfo_request_count", "0"),
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


def write_abnormal_trading_first_slice_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_abnormal_trading_first_slice_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=ABNORMAL_TRADING_FIRST_SLICE_LIVE_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_abnormal_trading_first_slice_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    quality_rows = [
        {
            "case_id": r["case_id"],
            "component": r["component"],
            "anchor_tdate": r["anchor_tdate"],
            "expected_behavior": r["expected_behavior"],
            "retrieval_status": r["retrieval_status"],
            "record_count": r["record_count"],
            "quality_status": r["quality_status"],
            "acceptable": r["acceptable"],
            "failure_type": r["failure_type"],
            "cninfo_request_count": r["cninfo_request_count"],
            "notes": r["notes"],
        }
        for r in rows
    ]
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_abnormal_trading_first_slice_quality_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=ABNORMAL_TRADING_FIRST_SLICE_QUALITY_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_abnormal_trading_first_slice_live_summary(
    live_rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    acceptable = sum(1 for r in live_rows if r["acceptable"] == "yes")
    lines = [
        "# CNINFO D 类 abnormal_trading First-Slice Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** abnormal_trading first-slice live summary · **NOT APPROVED for production**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(live_rows)}** |",
        f"| acceptable | **{acceptable}/{len(live_rows)}** |",
        f"| CNINFO requests | **{stats.cninfo_requests}** |",
        f"| DB writes | **{stats.db_writes}** |",
        f"| MinIO writes | **{stats.minio_writes}** |",
        f"| RAG runs | **{stats.rag_runs}** |",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_abnormal_trading_first_slice_live_path_gate = {ABNORMAL_TRADING_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_abnormal_trading_first_slice_execution_gate = {gate}",
        "```",
        "",
        "**NOT verified** · **NOT production_ready**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_abnormal_trading_first_slice_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_abnormal_trading_first_slice_live(
    universe_rows: List[AbnormalTradingFirstSliceRow],
    output_paths: Dict[str, str],
) -> int:
    """abnormal_trading 第一切片 live；DAT001–DAT005 · single_day_paged · marketList 公司过滤。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    component_cfg = copy.deepcopy(
        source_configs.get(ABNORMAL_TRADING_FIRST_SLICE_COMPONENT, {})
    )
    endpoint = endpoints.get(
        ABNORMAL_TRADING_FIRST_SLICE_COMPONENT,
        component_cfg.get("api_url", ABNORMAL_TRADING_FIRST_SLICE_ENDPOINT),
    )

    for row in universe_rows:
        planned = compute_abnormal_trading_first_slice_planned_requests(row)
        if planned > ABNORMAL_TRADING_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            print(
                f"ERROR: {ABNORMAL_TRADING_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"planned={planned}",
                file=sys.stderr,
            )
            return 2

    session = requests.Session()
    stats = LiveStats()
    case_summaries: Dict[str, Dict[str, str]] = {}

    for row in sorted(universe_rows, key=lambda r: r.case_id):
        case = abnormal_trading_first_slice_row_to_universe_case(row)
        row_cfg = copy.deepcopy(component_cfg)
        # 独立 params：仅 single_day_paged；不走 generic multi-probe
        param_list = _build_abnormal_trading_first_slice_params(row)
        summary = execute_live_case(
            case,
            row_cfg,
            endpoint,
            session,
            stats,
            output_paths,
            param_list=param_list,
        )
        case_summaries[row.case_id] = summary
        print(
            f"{row.case_id} {summary['retrieval_status']}: "
            f"records={summary['record_count']} "
            f"requests={summary['cninfo_request_count']}",
            flush=True,
        )

    cap_issues = validate_abnormal_trading_first_slice_request_caps(stats)
    if cap_issues:
        print(
            "ERROR: abnormal_trading first-slice request cap validation failed: "
            f"{cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_abnormal_trading_first_slice_execution_gate(
        universe_rows, case_summaries
    )
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = ABNORMAL_TRADING_FIRST_SLICE_EXECUTION_GATE_FAIL

    live_rows = [
        build_abnormal_trading_first_slice_live_row(
            row, case_summaries[row.case_id]
        )
        for row in sorted(universe_rows, key=lambda r: r.case_id)
        if row.case_id in case_summaries
    ]

    report_path = write_abnormal_trading_first_slice_live_report(
        live_rows, output_paths
    )
    quality_path = write_abnormal_trading_first_slice_quality_report(
        live_rows, output_paths
    )
    summary_path = write_abnormal_trading_first_slice_live_summary(
        live_rows, stats, gate, output_paths
    )

    print(
        f"mode=abnormal_trading_first_slice_live cases={len(live_rows)} "
        f"acceptable={sum(1 for r in live_rows if r['acceptable'] == 'yes')}/"
        f"{len(live_rows)} cninfo_calls={stats.cninfo_requests}"
    )
    print(
        f"gate=d_class_abnormal_trading_first_slice_execution_gate={gate}"
    )
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == ABNORMAL_TRADING_FIRST_SLICE_EXECUTION_GATE_PASS else 1


def run_abnormal_trading_first_slice(args: argparse.Namespace) -> int:
    enforce_abnormal_trading_first_slice_forbidden_options(args)
    enforce_abnormal_trading_first_slice_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(
            f"ERROR: {ABNORMAL_TRADING_FIRST_SLICE_UNIVERSE_CSV_REQUIRED}",
            file=sys.stderr,
        )
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_abnormal_trading_first_slice_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_abnormal_trading_first_slice_universe(args.universe_csv)
    universe_issues = validate_abnormal_trading_first_slice_universe(universe_rows)
    if universe_issues:
        print(
            "ERROR: abnormal_trading first-slice universe validation failed: "
            f"{universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_abnormal_trading_first_slice_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_abnormal_trading_first_slice_live(universe_rows, output_paths)

    dry_rows = build_abnormal_trading_first_slice_dryrun_rows(universe_rows, output_root)
    write_abnormal_trading_first_slice_planned_snapshots(universe_rows, output_paths)
    report_path = write_abnormal_trading_first_slice_dryrun_report(dry_rows, output_paths)
    summary_path = write_abnormal_trading_first_slice_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    planned_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    print(
        f"mode=abnormal_trading_first_slice_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={planned_total} cninfo_calls=0"
    )
    print(
        "gate=d_class_abnormal_trading_first_slice_runner_extension_gate="
        f"{ABNORMAL_TRADING_FIRST_SLICE_RUNNER_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0




def load_shareholder_data_first_slice_universe(
    path: str,
) -> List[ShareholderDataFirstSliceRow]:
    rows: List[ShareholderDataFirstSliceRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                ShareholderDataFirstSliceRow(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    component=str(row.get("component", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    anchor_rdate=str(row.get("anchor_rdate", "")).strip(),
                    first_slice_include=str(
                        row.get("first_slice_include", "")
                    ).strip(),
                    expected_behavior=str(
                        row.get("expected_behavior", "")
                    ).strip(),
                    exclude_flags=str(row.get("exclude_flags", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                    sample_raw_reference=str(
                        row.get("sample_raw_reference", "")
                    ).strip(),
                )
            )
    return rows


def build_shareholder_data_first_slice_plan(
    anchor_rdate: str = SHAREHOLDER_DATA_FIRST_SLICE_ANCHOR_RDATE,
) -> List[str]:
    """shareholder_data 第一切片：共享 rdate 全市场截面 · rdate_report_period。"""
    return [f"rdate_report_period_{anchor_rdate}"]


def _build_shareholder_data_first_slice_params(
    row: ShareholderDataFirstSliceRow,
) -> List[Dict[str, Any]]:
    return [{"rdate": row.anchor_rdate}]


def compute_shareholder_data_first_slice_planned_shared(
    anchor_rdate: str = SHAREHOLDER_DATA_FIRST_SLICE_ANCHOR_RDATE,
) -> int:
    return len(build_shareholder_data_first_slice_plan(anchor_rdate))


def compute_shareholder_data_first_slice_planned_requests(
    row: ShareholderDataFirstSliceRow,
) -> int:
    """每案预算槽位（共享请求按案分摊预算 ≤1）。"""
    return 1


def resolve_shareholder_data_first_slice_fixture_refs(case_id: str) -> List[str]:
    names = SHAREHOLDER_DATA_FIRST_SLICE_CASE_FIXTURES.get(case_id, ())
    return [
        os.path.join(SHAREHOLDER_DATA_FIRST_SLICE_FIXTURE_DIR, name) for name in names
    ]


def validate_shareholder_data_first_slice_fixtures(
    rows: List[ShareholderDataFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    for row in rows:
        refs = resolve_shareholder_data_first_slice_fixture_refs(row.case_id)
        if not refs:
            issues.append(
                f"{SHAREHOLDER_DATA_FIRST_SLICE_FIXTURE_MISSING}:{row.case_id}"
            )
            continue
        for ref in refs:
            if not os.path.isfile(ref):
                issues.append(
                    f"{SHAREHOLDER_DATA_FIRST_SLICE_FIXTURE_MISSING}:"
                    f"{row.case_id}:{os.path.basename(ref)}"
                )
    return issues


def validate_shareholder_data_first_slice_universe(
    rows: List[ShareholderDataFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    if len(rows) != SHAREHOLDER_DATA_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE:
        issues.append(
            f"{SHAREHOLDER_DATA_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH}:got={len(rows)}"
        )
    seen_ids: Set[str] = set()
    budget_total = 0
    for row in rows:
        case_id = row.case_id
        if case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_ids.add(case_id)
        if case_id not in SHAREHOLDER_DATA_FIRST_SLICE_ALLOWED_CASE_IDS:
            issues.append(
                f"{SHAREHOLDER_DATA_FIRST_SLICE_FORBIDDEN_CASE_ID}:{case_id}"
            )
        if row.company_code in SHAREHOLDER_DATA_FIRST_SLICE_FORBIDDEN_COMPANY_CODES:
            issues.append(
                f"{SHAREHOLDER_DATA_FIRST_SLICE_FORBIDDEN_COMPANY_CODE}:"
                f"{row.company_code}"
            )
        expected_code = SHAREHOLDER_DATA_FIRST_SLICE_EXPECTED_COMPANY_CODES.get(case_id)
        if expected_code and row.company_code != expected_code:
            issues.append(
                f"{SHAREHOLDER_DATA_FIRST_SLICE_WRONG_COMPANY_CODE}:"
                f"{case_id}={row.company_code}"
            )
        if row.component != SHAREHOLDER_DATA_FIRST_SLICE_COMPONENT:
            issues.append(f"{SHAREHOLDER_DATA_FIRST_SLICE_WRONG_COMPONENT}:{case_id}")
        if row.first_slice_include.lower() != "yes":
            issues.append(f"{SHAREHOLDER_DATA_FIRST_SLICE_INCLUDE_REQUIRED}:{case_id}")
        if row.anchor_rdate != SHAREHOLDER_DATA_FIRST_SLICE_ANCHOR_RDATE:
            issues.append(
                f"{SHAREHOLDER_DATA_FIRST_SLICE_WRONG_ANCHOR_RDATE}:"
                f"{case_id}={row.anchor_rdate}"
            )
        planned = compute_shareholder_data_first_slice_planned_requests(row)
        if planned > SHAREHOLDER_DATA_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{SHAREHOLDER_DATA_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"{case_id}={planned}"
            )
        budget_total += planned
    for required_id in sorted(SHAREHOLDER_DATA_FIRST_SLICE_ALLOWED_CASE_IDS):
        if required_id not in seen_ids:
            issues.append(f"missing_case_id:{required_id}")
    shared = compute_shareholder_data_first_slice_planned_shared()
    if shared != SHAREHOLDER_DATA_FIRST_SLICE_PLANNED_SHARED_REQUESTS:
        issues.append(
            f"{SHAREHOLDER_DATA_FIRST_SLICE_SHARED_PLAN_MISMATCH}:got={shared}"
        )
    if shared > SHAREHOLDER_DATA_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{SHAREHOLDER_DATA_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{shared}"
        )
    if budget_total > SHAREHOLDER_DATA_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{SHAREHOLDER_DATA_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:budget={budget_total}"
        )
    issues.extend(validate_shareholder_data_first_slice_fixtures(rows))
    return issues


def validate_shareholder_data_first_slice_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT)
    blocked_pairs = [
        (
            _normalize_output_root(DEFAULT_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_EXECUTIVE_SHAREHOLDING_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_SHAREHOLDER_CHANGE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(
                DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
            ),
            SHAREHOLDER_DATA_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_ABNORMAL_TRADING_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT),
            SHAREHOLDER_DATA_FIRST_SLICE_FUND_INDUSTRY_ALLOCATION_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
    ]
    for blocked_root, token in blocked_pairs:
        if root == blocked_root or root.startswith(blocked_root + os.sep):
            return False, token
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT_REQUIRED


def enforce_shareholder_data_first_slice_write_block_targets(
    output_paths: Dict[str, str],
) -> None:
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {SHAREHOLDER_DATA_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_shareholder_data_first_slice_forbidden_options(
    args: argparse.Namespace,
) -> None:
    enforce_forbidden_options(args)
    mixed_modes = [
        ("known_event_replacement", args.known_event_replacement),
        ("known_event_targeted_probe", args.known_event_targeted_probe),
        ("bounded_probe_v2", args.bounded_probe_v2),
        ("margin_trading_first_slice", args.margin_trading_first_slice),
        ("block_trade_first_slice", args.block_trade_first_slice),
        ("restricted_shares_unlock_first_slice", args.restricted_shares_unlock_first_slice),
        ("equity_pledge_first_slice", args.equity_pledge_first_slice),
        ("shareholder_change_first_slice", args.shareholder_change_first_slice),
        ("executive_shareholding_first_slice", args.executive_shareholding_first_slice),
        ("abnormal_trading_first_slice", args.abnormal_trading_first_slice),
        ("fund_industry_allocation_first_slice", args.fund_industry_allocation_first_slice),
    ]
    for name, enabled in mixed_modes:
        if args.shareholder_data_first_slice and enabled:
            print(
                f"ERROR: {SHAREHOLDER_DATA_FIRST_SLICE_MIXED_MODE_BLOCKED}:{name}",
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
        (
            "approve_d_class_margin_trading_first_slice",
            args.approve_d_class_margin_trading_first_slice,
        ),
        (
            "approve_d_class_block_trade_first_slice",
            args.approve_d_class_block_trade_first_slice,
        ),
        (
            "approve_d_class_restricted_shares_unlock_first_slice",
            args.approve_d_class_restricted_shares_unlock_first_slice,
        ),
        (
            "approve_d_class_equity_pledge_first_slice",
            args.approve_d_class_equity_pledge_first_slice,
        ),
        (
            "approve_d_class_shareholder_change_first_slice",
            args.approve_d_class_shareholder_change_first_slice,
        ),
        (
            "approve_d_class_executive_shareholding_first_slice",
            args.approve_d_class_executive_shareholding_first_slice,
        ),
        (
            "approve_d_class_abnormal_trading_first_slice",
            args.approve_d_class_abnormal_trading_first_slice,
        ),
        (
            "approve_d_class_fund_industry_allocation_first_slice",
            args.approve_d_class_fund_industry_allocation_first_slice,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.shareholder_data_first_slice and enabled:
            print(
                f"ERROR: {SHAREHOLDER_DATA_FIRST_SLICE_WRONG_APPROVAL_FLAG}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    if (
        not args.shareholder_data_first_slice
        and args.approve_d_class_shareholder_data_first_slice
    ):
        print(
            f"ERROR: {SHAREHOLDER_DATA_FIRST_SLICE_WRONG_APPROVAL_FLAG}:"
            "shareholder_data_first_slice_flag_without_mode",
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


def enforce_shareholder_data_first_slice_live_approval_gate(
    args: argparse.Namespace,
) -> None:
    if args.mode == "live" and args.shareholder_data_first_slice:
        if not args.approve_d_class_shareholder_data_first_slice:
            print(
                f"ERROR: {SHAREHOLDER_DATA_FIRST_SLICE_APPROVAL_REQUIRED}",
                file=sys.stderr,
            )
            sys.exit(2)


def build_shareholder_data_first_slice_dryrun_rows(
    rows: List[ShareholderDataFirstSliceRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    shared = compute_shareholder_data_first_slice_planned_shared()
    for row in rows:
        planned_requests = compute_shareholder_data_first_slice_planned_requests(row)
        plan = build_shareholder_data_first_slice_plan(row.anchor_rdate)
        fixture_refs = resolve_shareholder_data_first_slice_fixture_refs(row.case_id)
        dry_rows.append(
            {
                "case_id": row.case_id,
                "company_code": row.company_code,
                "company_name": row.company_name,
                "component": row.component,
                "market": row.market,
                "anchor_rdate": row.anchor_rdate,
                "first_slice_include": row.first_slice_include,
                "expected_behavior": row.expected_behavior,
                "planned_request_count": str(planned_requests),
                "planned_output_root": output_root,
                "planned_endpoint": SHAREHOLDER_DATA_FIRST_SLICE_ENDPOINT,
                "fixture_refs": ";".join(os.path.basename(r) for r in fixture_refs),
                "cninfo_call_planned": (
                    "shared" if row.first_slice_include.lower() == "yes" else "no"
                ),
                "pdf_download": "no",
                "ocr": "no",
                "extraction": "no",
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
                "dryrun_status": "planned_ok",
                "notes": (
                    f"anchor_rdate={row.anchor_rdate}; plan={','.join(plan)}; "
                    f"query_mode={SHAREHOLDER_DATA_FIRST_SLICE_QUERY_MODE}; "
                    f"shared_rdate={shared}; seccode_filter_offline=yes; "
                    f"empty_but_valid_allowed=yes; not_generic_multi_probe=yes; "
                    f"tier1_fixtures={len(fixture_refs)}"
                ),
            }
        )
    return dry_rows


def write_shareholder_data_first_slice_planned_snapshots(
    rows: List[ShareholderDataFirstSliceRow],
    output_paths: Dict[str, str],
) -> None:
    snap_dir = os.path.join(output_paths["root"], "planned_snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    for row in rows:
        plan = build_shareholder_data_first_slice_plan(row.anchor_rdate)
        params = _build_shareholder_data_first_slice_params(row)
        fixture_refs = resolve_shareholder_data_first_slice_fixture_refs(row.case_id)
        payload = {
            "case_id": row.case_id,
            "company_code": row.company_code,
            "company_name": row.company_name,
            "component": row.component,
            "anchor_rdate": row.anchor_rdate,
            "query_mode": SHAREHOLDER_DATA_FIRST_SLICE_QUERY_MODE,
            "planned_requests": plan,
            "query_params": params,
            "endpoint": SHAREHOLDER_DATA_FIRST_SLICE_ENDPOINT,
            "records_path": SHAREHOLDER_DATA_FIRST_SLICE_RECORDS_PATH,
            "shared_request": True,
            "seccode_filter_offline": True,
            "filter_seccode": row.company_code,
            "expected_behavior": row.expected_behavior,
            "fixture_refs": [
                os.path.relpath(r, BASE_DIR).replace("\\", "/") for r in fixture_refs
            ],
            "cninfo_called": False,
        }
        out = os.path.join(snap_dir, f"{row.case_id}_shareholder_data.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")


def write_shareholder_data_first_slice_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_data_first_slice_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=SHAREHOLDER_DATA_FIRST_SLICE_DRYRUN_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_shareholder_data_first_slice_dryrun_summary(
    dry_rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    shared = compute_shareholder_data_first_slice_planned_shared()
    budget_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    lines = [
        "# CNINFO D 类 shareholder_data First-Slice Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** shareholder_data first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for live**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_shared_cninfo_requests | **{shared}** |",
        f"| planned_request_budget_total | **{budget_total}** |",
        f"| planned_request_count_total | **{shared}** |",
        f"| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        "- component: **shareholder_data**",
        f"- endpoint: `{SHAREHOLDER_DATA_FIRST_SLICE_ENDPOINT}`",
        f"- query mode: **{SHAREHOLDER_DATA_FIRST_SLICE_QUERY_MODE}**",
        f"- anchor_rdate: **{SHAREHOLDER_DATA_FIRST_SLICE_ANCHOR_RDATE}**",
        f"- records_path: **{SHAREHOLDER_DATA_FIRST_SLICE_RECORDS_PATH}**",
        "- shared market-wide rdate request · offline SECCODE filter",
        "- fixture root: `fixtures/d_class/shareholder_data_first_slice/`",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_shareholder_data_first_slice_runner_extension_gate = {SHAREHOLDER_DATA_FIRST_SLICE_RUNNER_GATE}",
        f"d_class_shareholder_data_first_slice_live_path_gate = {SHAREHOLDER_DATA_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_shareholder_data_first_slice_live_gate = {SHAREHOLDER_DATA_FIRST_SLICE_LIVE_GATE}",
        "approval_status = STANDING_SCOPE_AUTHORIZED_OFFLINE",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_data_first_slice_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def shareholder_data_first_slice_row_to_universe_case(
    row: ShareholderDataFirstSliceRow,
) -> UniverseCase:
    """将 shareholder_data 第一切片 universe 行转为探测用 UniverseCase。"""
    return UniverseCase(
        case_id=row.case_id,
        company_code=row.company_code,
        company_name=row.company_name,
        component=row.component,
        market=row.market,
        risk_level="",
        expected_behavior=row.expected_behavior,
        reason=row.notes,
    )


def is_shareholder_data_first_slice_acceptable(
    row: ShareholderDataFirstSliceRow,
    summary: Dict[str, str],
) -> bool:
    """第一切片 acceptable 判定；禁止 disclosure-only 升级为 captured_normal。"""
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    eb = row.expected_behavior
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if "disclosure" in row.notes.lower() and rs != "found":
        return False
    if eb == "empty_but_valid" and rs == "empty_but_valid" and rc == 0:
        return True
    if "empty_but_valid" in eb and rs == "empty_but_valid" and rc == 0:
        return True
    if "captured_normal_or_empty_but_valid" in eb and (
        (rs == "found" and rc >= 1) or (rs == "empty_but_valid" and rc == 0)
    ):
        return qs in ("pass", "needs_review", "")
    if "captured_normal_or_needs_review" in eb and (
        (rs == "found" and rc >= 1) or (rs == "needs_review" and rc >= 1)
    ):
        return qs in ("pass", "needs_review", "")
    if eb == "captured_normal" and rs == "found" and rc >= 1 and qs in (
        "pass",
        "needs_review",
    ):
        return True
    if "captured_normal" in eb and rs == "found" and rc >= 1 and qs in (
        "pass",
        "needs_review",
    ):
        return True
    if rs == "found" and rc >= 1 and qs in ("pass", "needs_review"):
        return True
    if rs == "needs_review" and rc >= 1 and qs == "needs_review":
        return "needs_review" in eb or "captured_normal" in eb
    return False


def assess_shareholder_data_first_slice_failure_type(
    row: ShareholderDataFirstSliceRow,
    summary: Dict[str, str],
) -> str:
    if is_shareholder_data_first_slice_acceptable(row, summary):
        return ""
    rs = summary.get("retrieval_status", "")
    if rs in ("http_error", "blocked"):
        return "transport_or_http_error"
    return "expectation_mismatch"


def validate_shareholder_data_first_slice_request_caps(stats: LiveStats) -> List[str]:
    issues: List[str] = []
    for case_id, count in stats.case_request_counts.items():
        if count > SHAREHOLDER_DATA_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{SHAREHOLDER_DATA_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"{case_id}={count}"
            )
        # 共享路径：禁止按公司拆出额外 CNINFO 请求
        if (
            case_id != SHAREHOLDER_DATA_FIRST_SLICE_SHARED_REQUEST_CASE_ID
            and count > 0
        ):
            issues.append(
                f"{SHAREHOLDER_DATA_FIRST_SLICE_SHARED_REQUEST_REQUIRED}:"
                f"non_shared_case={case_id}={count}"
            )
    if stats.cninfo_requests > SHAREHOLDER_DATA_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{SHAREHOLDER_DATA_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:"
            f"{stats.cninfo_requests}"
        )
    # prefer 1 shared：超过 planned_shared 即失败
    if stats.cninfo_requests > SHAREHOLDER_DATA_FIRST_SLICE_PLANNED_SHARED_REQUESTS:
        issues.append(
            f"{SHAREHOLDER_DATA_FIRST_SLICE_SHARED_PLAN_MISMATCH}:"
            f"cninfo_requests={stats.cninfo_requests}"
        )
    return issues


def assess_shareholder_data_first_slice_shared_case(
    row: ShareholderDataFirstSliceRow,
    company_records: List[Dict[str, Any]],
    http_status: int,
    last_error: str,
    endpoint: str,
    used_params: Dict[str, Any],
    shared_cninfo_requests: int,
) -> Dict[str, str]:
    """基于共享截面 + SECCODE 过滤结果，生成单案 live summary。"""
    record_count = len(company_records)
    empty_but_valid = "no"
    needs_review = "no"
    notes_parts: List[str] = [
        "shared_rdate_request=1",
        "seccode_filter=yes",
        f"query_mode={SHAREHOLDER_DATA_FIRST_SLICE_QUERY_MODE}",
    ]

    if last_error in ("rate_limited",) or last_error.startswith("network_error"):
        retrieval_status = (
            "http_error" if last_error.startswith("network_error") else "blocked"
        )
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
        notes_parts.append(
            "company-level zero rows after SECCODE filter; legal empty per quality policy"
        )
    else:
        retrieval_status = "found"
        lineage_status = "discovered"
        quality_status = "pass"
        if row.expected_behavior == "needs_review_candidate":
            needs_review = "yes"
            quality_status = "needs_review"
            lineage_status = "needs_review"
            notes_parts.append("needs_review candidate")
        else:
            notes_parts.append(f"found {record_count} row(s) for company")

    return {
        "case_id": row.case_id,
        "company_code": row.company_code,
        "company_name": row.company_name,
        "component": row.component,
        "expected_behavior": row.expected_behavior,
        "retrieval_status": retrieval_status,
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "record_count": str(record_count),
        "empty_but_valid": empty_but_valid,
        "needs_review": needs_review,
        "endpoint_used": endpoint,
        "cninfo_request_count": str(shared_cninfo_requests),
        "db_write": "no",
        "minio_write": "no",
        "rag_run": "no",
        "notes": "; ".join(notes_parts),
        "_http_status": str(http_status),
        "_used_params": used_params,
        "_sample_records": company_records[:3],
    }


def write_shareholder_data_first_slice_live_snapshot(
    row: ShareholderDataFirstSliceRow,
    summary: Dict[str, str],
    output_paths: Dict[str, str],
) -> str:
    snapshot_path = os.path.join(
        output_paths["live_snapshots"],
        f"{row.case_id}_{row.component}.json",
    )
    used_params = summary.get("_used_params") or {}
    sample_records = summary.get("_sample_records") or []
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "case_id": row.case_id,
                "company_code": row.company_code,
                "component": row.component,
                "endpoint": summary.get(
                    "endpoint_used", SHAREHOLDER_DATA_FIRST_SLICE_ENDPOINT
                ),
                "params": used_params,
                "query_mode": SHAREHOLDER_DATA_FIRST_SLICE_QUERY_MODE,
                "shared_request": True,
                "seccode_filter": True,
                "filter_seccode": row.company_code,
                "http_status": int(summary.get("_http_status") or 0),
                "record_count": int(summary.get("record_count") or 0),
                "sample_records": sample_records,
                "cninfo_called": True,
                "db_write": False,
                "minio_write": False,
                "rag_run": False,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
        f.write("\n")
    return snapshot_path


def compute_shareholder_data_first_slice_execution_gate(
    universe_rows: List[ShareholderDataFirstSliceRow],
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    """shareholder_data 第一切片 live 执行 gate；≥3/5 acceptable → PASS_WITH_CAVEAT。"""
    acceptable = 0
    for row in universe_rows:
        summary = case_summaries.get(row.case_id, {})
        if is_shareholder_data_first_slice_acceptable(row, summary):
            acceptable += 1
    if acceptable >= 3:
        return SHAREHOLDER_DATA_FIRST_SLICE_EXECUTION_GATE_PASS
    return SHAREHOLDER_DATA_FIRST_SLICE_EXECUTION_GATE_FAIL


def build_shareholder_data_first_slice_live_row(
    row: ShareholderDataFirstSliceRow,
    summary: Dict[str, str],
) -> Dict[str, str]:
    acceptable = is_shareholder_data_first_slice_acceptable(row, summary)
    failure_type = assess_shareholder_data_first_slice_failure_type(row, summary)
    return {
        "case_id": row.case_id,
        "company_code": row.company_code,
        "company_name": row.company_name,
        "component": row.component,
        "market": row.market,
        "anchor_rdate": row.anchor_rdate,
        "expected_behavior": row.expected_behavior,
        "retrieval_status": summary.get("retrieval_status", ""),
        "quality_status": summary.get("quality_status", ""),
        "lineage_status": summary.get("lineage_status", ""),
        "record_count": summary.get("record_count", "0"),
        "empty_but_valid": summary.get("empty_but_valid", "no"),
        "needs_review": summary.get("needs_review", "no"),
        "endpoint_used": summary.get(
            "endpoint_used", SHAREHOLDER_DATA_FIRST_SLICE_ENDPOINT
        ),
        "cninfo_request_count": summary.get("cninfo_request_count", "0"),
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


def write_shareholder_data_first_slice_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_data_first_slice_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=SHAREHOLDER_DATA_FIRST_SLICE_LIVE_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_shareholder_data_first_slice_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    quality_rows = [
        {
            "case_id": r["case_id"],
            "component": r["component"],
            "anchor_rdate": r["anchor_rdate"],
            "expected_behavior": r["expected_behavior"],
            "retrieval_status": r["retrieval_status"],
            "record_count": r["record_count"],
            "quality_status": r["quality_status"],
            "acceptable": r["acceptable"],
            "failure_type": r["failure_type"],
            "cninfo_request_count": r["cninfo_request_count"],
            "notes": r["notes"],
        }
        for r in rows
    ]
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_data_first_slice_quality_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=SHAREHOLDER_DATA_FIRST_SLICE_QUALITY_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_shareholder_data_first_slice_live_summary(
    live_rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    acceptable = sum(1 for r in live_rows if r["acceptable"] == "yes")
    shared = stats.case_request_counts.get(
        SHAREHOLDER_DATA_FIRST_SLICE_SHARED_REQUEST_CASE_ID, 0
    )
    lines = [
        "# CNINFO D 类 shareholder_data First-Slice Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** shareholder_data first-slice live summary · **NOT APPROVED for production**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(live_rows)}** |",
        f"| acceptable | **{acceptable}/{len(live_rows)}** |",
        f"| shared_cninfo_requests | **{shared}** |",
        f"| CNINFO requests | **{stats.cninfo_requests}** |",
        f"| DB writes | **{stats.db_writes}** |",
        f"| MinIO writes | **{stats.minio_writes}** |",
        f"| RAG runs | **{stats.rag_runs}** |",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_shareholder_data_first_slice_live_path_gate = {SHAREHOLDER_DATA_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_shareholder_data_first_slice_live_gate = {SHAREHOLDER_DATA_FIRST_SLICE_LIVE_GATE}",
        f"d_class_shareholder_data_first_slice_execution_gate = {gate}",
        "```",
        "",
        "**NOT verified** · **NOT production_ready**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_data_first_slice_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_shareholder_data_first_slice_live(
    universe_rows: List[ShareholderDataFirstSliceRow],
    output_paths: Dict[str, str],
) -> int:
    """shareholder_data 第一切片 live：1 次共享 rdate 截面 + 离线 SECCODE 过滤。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    component_cfg = copy.deepcopy(
        source_configs.get(SHAREHOLDER_DATA_FIRST_SLICE_COMPONENT, {})
    )
    endpoint = endpoints.get(
        SHAREHOLDER_DATA_FIRST_SLICE_COMPONENT,
        component_cfg.get("api_url", SHAREHOLDER_DATA_FIRST_SLICE_ENDPOINT),
    )
    component_cfg["api_url"] = endpoint

    for row in universe_rows:
        planned = compute_shareholder_data_first_slice_planned_requests(row)
        if planned > SHAREHOLDER_DATA_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            print(
                f"ERROR: {SHAREHOLDER_DATA_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"planned={planned}",
                file=sys.stderr,
            )
            return 2

    shared_plan = compute_shareholder_data_first_slice_planned_shared(
        universe_rows[0].anchor_rdate if universe_rows else SHAREHOLDER_DATA_FIRST_SLICE_ANCHOR_RDATE
    )
    if shared_plan != SHAREHOLDER_DATA_FIRST_SLICE_PLANNED_SHARED_REQUESTS:
        print(
            f"ERROR: {SHAREHOLDER_DATA_FIRST_SLICE_SHARED_PLAN_MISMATCH}:"
            f"got={shared_plan}",
            file=sys.stderr,
        )
        return 2

    session = requests.Session()
    stats = LiveStats()
    # 全切片共享同一 rdate params（不按公司拆请求）
    shared_params = _build_shareholder_data_first_slice_params(universe_rows[0])[0]
    payload, http_status, last_error = _cninfo_request(
        session,
        component_cfg,
        shared_params,
        stats,
        SHAREHOLDER_DATA_FIRST_SLICE_SHARED_REQUEST_CASE_ID,
    )
    all_records = _extract_records(payload) if payload is not None else []

    case_summaries: Dict[str, Dict[str, str]] = {}
    for row in sorted(universe_rows, key=lambda r: r.case_id):
        company_records = _filter_company_records(all_records, row.company_code)
        summary = assess_shareholder_data_first_slice_shared_case(
            row,
            company_records,
            http_status,
            last_error,
            endpoint,
            shared_params,
            stats.cninfo_requests,
        )
        write_shareholder_data_first_slice_live_snapshot(row, summary, output_paths)
        # 报告字段不含内部辅助键
        public_summary = {
            k: v
            for k, v in summary.items()
            if not k.startswith("_")
        }
        case_summaries[row.case_id] = public_summary
        print(
            f"{row.case_id} {public_summary['retrieval_status']}: "
            f"records={public_summary['record_count']} "
            f"shared_requests={stats.cninfo_requests}",
            flush=True,
        )

    cap_issues = validate_shareholder_data_first_slice_request_caps(stats)
    if cap_issues:
        print(
            "ERROR: shareholder_data first-slice request cap validation failed: "
            f"{cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_shareholder_data_first_slice_execution_gate(
        universe_rows, case_summaries
    )
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = SHAREHOLDER_DATA_FIRST_SLICE_EXECUTION_GATE_FAIL

    live_rows = [
        build_shareholder_data_first_slice_live_row(
            row, case_summaries[row.case_id]
        )
        for row in sorted(universe_rows, key=lambda r: r.case_id)
        if row.case_id in case_summaries
    ]

    report_path = write_shareholder_data_first_slice_live_report(
        live_rows, output_paths
    )
    quality_path = write_shareholder_data_first_slice_quality_report(
        live_rows, output_paths
    )
    summary_path = write_shareholder_data_first_slice_live_summary(
        live_rows, stats, gate, output_paths
    )

    print(
        f"mode=shareholder_data_first_slice_live cases={len(live_rows)} "
        f"acceptable={sum(1 for r in live_rows if r['acceptable'] == 'yes')}/"
        f"{len(live_rows)} cninfo_calls={stats.cninfo_requests} "
        f"shared_request=1"
    )
    print(
        f"gate=d_class_shareholder_data_first_slice_execution_gate={gate}"
    )
    print(
        "live_path_gate=d_class_shareholder_data_first_slice_live_path_gate="
        f"{SHAREHOLDER_DATA_FIRST_SLICE_LIVE_PATH_GATE}"
    )
    print(
        "live_gate=d_class_shareholder_data_first_slice_live_gate="
        f"{SHAREHOLDER_DATA_FIRST_SLICE_LIVE_GATE}"
    )
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == SHAREHOLDER_DATA_FIRST_SLICE_EXECUTION_GATE_PASS else 1


def run_shareholder_data_first_slice(args: argparse.Namespace) -> int:
    enforce_shareholder_data_first_slice_forbidden_options(args)
    enforce_shareholder_data_first_slice_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(
            f"ERROR: {SHAREHOLDER_DATA_FIRST_SLICE_UNIVERSE_CSV_REQUIRED}",
            file=sys.stderr,
        )
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_shareholder_data_first_slice_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_shareholder_data_first_slice_universe(args.universe_csv)
    universe_issues = validate_shareholder_data_first_slice_universe(universe_rows)
    if universe_issues:
        print(
            "ERROR: shareholder_data first-slice universe validation failed: "
            f"{universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_shareholder_data_first_slice_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_shareholder_data_first_slice_live(universe_rows, output_paths)

    dry_rows = build_shareholder_data_first_slice_dryrun_rows(universe_rows, output_root)
    write_shareholder_data_first_slice_planned_snapshots(universe_rows, output_paths)
    report_path = write_shareholder_data_first_slice_dryrun_report(dry_rows, output_paths)
    summary_path = write_shareholder_data_first_slice_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    shared = compute_shareholder_data_first_slice_planned_shared()
    print(
        f"mode=shareholder_data_first_slice_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={shared} cninfo_calls=0"
    )
    print(
        "gate=d_class_shareholder_data_first_slice_runner_extension_gate="
        f"{SHAREHOLDER_DATA_FIRST_SLICE_RUNNER_GATE}"
    )
    print(
        "live_path_gate=d_class_shareholder_data_first_slice_live_path_gate="
        f"{SHAREHOLDER_DATA_FIRST_SLICE_LIVE_PATH_GATE}"
    )
    print(
        "live_gate=d_class_shareholder_data_first_slice_live_gate="
        f"{SHAREHOLDER_DATA_FIRST_SLICE_LIVE_GATE}"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0






def load_fund_industry_allocation_first_slice_universe(
    path: str,
) -> List[FundIndustryAllocationFirstSliceRow]:
    rows: List[FundIndustryAllocationFirstSliceRow] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                FundIndustryAllocationFirstSliceRow(
                    case_id=str(row.get("case_id", "")).strip(),
                    probe_key=str(row.get("probe_key", "")).strip(),
                    industry_code=str(row.get("industry_code", "")).strip(),
                    industry_name=str(row.get("industry_name", "")).strip(),
                    component=str(row.get("component", "")).strip(),
                    query_mode=str(row.get("query_mode", "")).strip(),
                    anchor_rdate=str(row.get("anchor_rdate", "")).strip(),
                    first_slice_include=str(
                        row.get("first_slice_include", "")
                    ).strip(),
                    expected_behavior=str(
                        row.get("expected_behavior", "")
                    ).strip(),
                    exclude_flags=str(row.get("exclude_flags", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                    sample_raw_reference=str(
                        row.get("sample_raw_reference", "")
                    ).strip(),
                )
            )
    return rows


def build_fund_industry_allocation_first_slice_plan() -> List[str]:
    """fund_industry_allocation 第一切片：≤3 共享探针 default / rdate filled / rdate empty。"""
    return list(FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_PROBE_KEYS)


def resolve_fund_industry_allocation_first_slice_shared_probe_key(
    row: FundIndustryAllocationFirstSliceRow,
) -> str:
    if row.query_mode == "default":
        return "default"
    if row.query_mode == "rdate" and row.anchor_rdate:
        return f"rdate_{row.anchor_rdate}"
    return ""


def _build_fund_industry_allocation_first_slice_params_for_probe(
    probe_key: str,
) -> Dict[str, Any]:
    if probe_key == "default":
        return {}
    if probe_key.startswith("rdate_"):
        return {"rdate": probe_key[len("rdate_") :]}
    raise ValueError(f"unknown_shared_probe_key:{probe_key}")


def compute_fund_industry_allocation_first_slice_planned_shared() -> int:
    return len(build_fund_industry_allocation_first_slice_plan())


def compute_fund_industry_allocation_first_slice_planned_requests(
    row: FundIndustryAllocationFirstSliceRow,
) -> int:
    """每案预算槽位（共享请求按案分摊预算 ≤1）。"""
    return 1


def resolve_fund_industry_allocation_first_slice_fixture_refs(
    case_id: str,
) -> List[str]:
    names = FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_CASE_FIXTURES.get(case_id, ())
    return [
        os.path.join(FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FIXTURE_DIR, name)
        for name in names
    ]


def validate_fund_industry_allocation_first_slice_fixtures(
    rows: List[FundIndustryAllocationFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    for row in rows:
        refs = resolve_fund_industry_allocation_first_slice_fixture_refs(row.case_id)
        if not refs:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FIXTURE_MISSING}:{row.case_id}"
            )
            continue
        for ref in refs:
            if not os.path.isfile(ref):
                issues.append(
                    f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FIXTURE_MISSING}:"
                    f"{row.case_id}:{os.path.basename(ref)}"
                )
    return issues


def validate_fund_industry_allocation_first_slice_universe(
    rows: List[FundIndustryAllocationFirstSliceRow],
) -> List[str]:
    issues: List[str] = []
    if len(rows) != FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXPECTED_UNIVERSE_SIZE:
        issues.append(
            f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_UNIVERSE_SIZE_MISMATCH}:"
            f"got={len(rows)}"
        )
    seen_ids: Set[str] = set()
    budget_total = 0
    for row in rows:
        case_id = row.case_id
        if case_id in seen_ids:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_ids.add(case_id)
        if case_id not in FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ALLOWED_CASE_IDS:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FORBIDDEN_CASE_ID}:{case_id}"
            )
        # 行业聚合：禁止 company_code 列语义；exclude_flags 须声明 no_company_code
        if "no_company_code" not in row.exclude_flags:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_COMPANY_CODE_FORBIDDEN}:"
                f"{case_id}"
            )
        for forbidden in FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FORBIDDEN_COMPANY_CODES:
            if f"exclude_{forbidden}" not in row.exclude_flags:
                issues.append(
                    f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_FORBIDDEN_COMPANY_CODE}:"
                    f"missing_exclude_{forbidden}"
                )
        expected_code = FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXPECTED_INDUSTRY_CODES.get(
            case_id
        )
        if expected_code is not None and row.industry_code != expected_code:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_INDUSTRY_CODE}:"
                f"{case_id}={row.industry_code}"
            )
        expected_mode = FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXPECTED_QUERY_MODES.get(
            case_id
        )
        if expected_mode is not None and row.query_mode != expected_mode:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_QUERY_MODE}:"
                f"{case_id}={row.query_mode}"
            )
        expected_rdate = FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXPECTED_ANCHOR_RDATES.get(
            case_id
        )
        if expected_rdate is not None and row.anchor_rdate != expected_rdate:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_ANCHOR_RDATE}:"
                f"{case_id}={row.anchor_rdate}"
            )
        if row.component != FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_COMPONENT:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_COMPONENT}:{case_id}"
            )
        if row.first_slice_include.lower() != "yes":
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_INCLUDE_REQUIRED}:{case_id}"
            )
        probe_key = resolve_fund_industry_allocation_first_slice_shared_probe_key(row)
        if probe_key not in FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_PROBE_KEYS:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_PLAN_MISMATCH}:"
                f"{case_id}={probe_key}"
            )
        planned = compute_fund_industry_allocation_first_slice_planned_requests(row)
        if planned > FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"{case_id}={planned}"
            )
        budget_total += planned
    for required_id in sorted(FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ALLOWED_CASE_IDS):
        if required_id not in seen_ids:
            issues.append(f"missing_case_id:{required_id}")
    shared = compute_fund_industry_allocation_first_slice_planned_shared()
    if shared != FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PLANNED_SHARED_REQUESTS:
        issues.append(
            f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_PLAN_MISMATCH}:got={shared}"
        )
    if shared > FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:{shared}"
        )
    if budget_total > FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:"
            f"budget={budget_total}"
        )
    issues.extend(validate_fund_industry_allocation_first_slice_fixtures(rows))
    return issues


def validate_fund_industry_allocation_first_slice_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(
        DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT
    )
    blocked_pairs = [
        (
            _normalize_output_root(DEFAULT_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_V2_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_REPLACEMENT_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TARGETED_PROBE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(
                DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT
            ),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXECUTIVE_SHAREHOLDING_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHAREHOLDER_CHANGE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EQUITY_PLEDGE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_MARGIN_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_DISCLOSURE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_BLOCK_TRADE_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(
                DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
            ),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_RSU_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ABNORMAL_TRADING_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
        (
            _normalize_output_root(DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT),
            FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHAREHOLDER_DATA_OUTPUT_ROOT_WRITE_BLOCKED,
        ),
    ]
    for blocked_root, token in blocked_pairs:
        if root == blocked_root or root.startswith(blocked_root + os.sep):
            return False, token
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT_REQUIRED


def enforce_fund_industry_allocation_first_slice_write_block_targets(
    output_paths: Dict[str, str],
) -> None:
    protected = [
        _normalize_output_root(DEFAULT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_V2_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_REPLACEMENT_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_TARGETED_PROBE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_MARGIN_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_DISCLOSURE_SCHEDULE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT),
        _normalize_output_root(CALIBRATED_UNIVERSE_CSV),
        _normalize_output_root(DEFAULT_UNIVERSE_CSV),
    ]
    for key in ("root", "reports"):
        target = _normalize_output_root(output_paths[key])
        for blocked in protected:
            if target == blocked or target.startswith(blocked + os.sep):
                print(
                    f"ERROR: {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_V1_OUTPUT_ROOT_WRITE_BLOCKED}:{key}",
                    file=sys.stderr,
                )
                sys.exit(2)


def enforce_fund_industry_allocation_first_slice_forbidden_options(
    args: argparse.Namespace,
) -> None:
    enforce_forbidden_options(args)
    mixed_modes = [
        ("known_event_replacement", args.known_event_replacement),
        ("known_event_targeted_probe", args.known_event_targeted_probe),
        ("bounded_probe_v2", args.bounded_probe_v2),
        ("margin_trading_first_slice", args.margin_trading_first_slice),
        ("block_trade_first_slice", args.block_trade_first_slice),
        (
            "restricted_shares_unlock_first_slice",
            args.restricted_shares_unlock_first_slice,
        ),
        ("equity_pledge_first_slice", args.equity_pledge_first_slice),
        ("shareholder_change_first_slice", args.shareholder_change_first_slice),
        ("executive_shareholding_first_slice", args.executive_shareholding_first_slice),
        ("abnormal_trading_first_slice", args.abnormal_trading_first_slice),
        ("shareholder_data_first_slice", args.shareholder_data_first_slice),
    ]
    for name, enabled in mixed_modes:
        if args.fund_industry_allocation_first_slice and enabled:
            print(
                f"ERROR: {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_MIXED_MODE_BLOCKED}:{name}",
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
        (
            "approve_d_class_margin_trading_first_slice",
            args.approve_d_class_margin_trading_first_slice,
        ),
        (
            "approve_d_class_block_trade_first_slice",
            args.approve_d_class_block_trade_first_slice,
        ),
        (
            "approve_d_class_restricted_shares_unlock_first_slice",
            args.approve_d_class_restricted_shares_unlock_first_slice,
        ),
        (
            "approve_d_class_equity_pledge_first_slice",
            args.approve_d_class_equity_pledge_first_slice,
        ),
        (
            "approve_d_class_shareholder_change_first_slice",
            args.approve_d_class_shareholder_change_first_slice,
        ),
        (
            "approve_d_class_executive_shareholding_first_slice",
            args.approve_d_class_executive_shareholding_first_slice,
        ),
        (
            "approve_d_class_abnormal_trading_first_slice",
            args.approve_d_class_abnormal_trading_first_slice,
        ),
        (
            "approve_d_class_shareholder_data_first_slice",
            args.approve_d_class_shareholder_data_first_slice,
        ),
    ]
    for name, enabled in wrong_flags:
        if args.fund_industry_allocation_first_slice and enabled:
            print(
                f"ERROR: {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_APPROVAL_FLAG}:{name}",
                file=sys.stderr,
            )
            sys.exit(2)
    if (
        not args.fund_industry_allocation_first_slice
        and args.approve_d_class_fund_industry_allocation_first_slice
    ):
        print(
            f"ERROR: {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_WRONG_APPROVAL_FLAG}:"
            "fund_industry_allocation_first_slice_flag_without_mode",
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


def enforce_fund_industry_allocation_first_slice_live_approval_gate(
    args: argparse.Namespace,
) -> None:
    if args.mode == "live" and args.fund_industry_allocation_first_slice:
        if not args.approve_d_class_fund_industry_allocation_first_slice:
            print(
                f"ERROR: {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_APPROVAL_REQUIRED}",
                file=sys.stderr,
            )
            sys.exit(2)


def build_fund_industry_allocation_first_slice_dryrun_rows(
    rows: List[FundIndustryAllocationFirstSliceRow],
    output_root: str,
) -> List[Dict[str, str]]:
    dry_rows: List[Dict[str, str]] = []
    shared = compute_fund_industry_allocation_first_slice_planned_shared()
    plan = build_fund_industry_allocation_first_slice_plan()
    for row in rows:
        planned_requests = compute_fund_industry_allocation_first_slice_planned_requests(
            row
        )
        probe_key = resolve_fund_industry_allocation_first_slice_shared_probe_key(row)
        fixture_refs = resolve_fund_industry_allocation_first_slice_fixture_refs(
            row.case_id
        )
        dry_rows.append(
            {
                "case_id": row.case_id,
                "industry_code": row.industry_code,
                "industry_name": row.industry_name,
                "component": row.component,
                "query_mode": row.query_mode,
                "anchor_rdate": row.anchor_rdate,
                "first_slice_include": row.first_slice_include,
                "expected_behavior": row.expected_behavior,
                "planned_request_count": str(planned_requests),
                "shared_probe_key": probe_key,
                "planned_output_root": output_root,
                "planned_endpoint": FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ENDPOINT,
                "fixture_refs": ";".join(os.path.basename(r) for r in fixture_refs),
                "cninfo_call_planned": (
                    "shared" if row.first_slice_include.lower() == "yes" else "no"
                ),
                "pdf_download": "no",
                "ocr": "no",
                "extraction": "no",
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
                "dryrun_status": "planned_ok",
                "notes": (
                    f"probe_key={probe_key}; plan={','.join(plan)}; "
                    f"shared_probes={shared}; industry_filter_offline=yes; "
                    f"schema=d_industry_aggregate; no_company_code=yes; "
                    f"empty_but_valid_allowed=yes; tier1_fixtures={len(fixture_refs)}"
                ),
            }
        )
    return dry_rows


def write_fund_industry_allocation_first_slice_planned_snapshots(
    rows: List[FundIndustryAllocationFirstSliceRow],
    output_paths: Dict[str, str],
) -> None:
    snap_dir = os.path.join(output_paths["root"], "planned_snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    plan = build_fund_industry_allocation_first_slice_plan()
    for row in rows:
        probe_key = resolve_fund_industry_allocation_first_slice_shared_probe_key(row)
        params = _build_fund_industry_allocation_first_slice_params_for_probe(probe_key)
        fixture_refs = resolve_fund_industry_allocation_first_slice_fixture_refs(
            row.case_id
        )
        payload = {
            "case_id": row.case_id,
            "probe_key": row.probe_key,
            "industry_code": row.industry_code,
            "industry_name": row.industry_name,
            "component": row.component,
            "query_mode": row.query_mode,
            "anchor_rdate": row.anchor_rdate,
            "shared_probe_key": probe_key,
            "planned_requests": plan,
            "query_params": params,
            "endpoint": FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ENDPOINT,
            "records_path": FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_RECORDS_PATH,
            "shared_request": True,
            "industry_filter_offline": True,
            "filter_industry_code": row.industry_code,
            "expected_logical_table": "d_industry_aggregate",
            "expected_behavior": row.expected_behavior,
            "fixture_refs": [
                os.path.relpath(r, BASE_DIR).replace("\\", "/") for r in fixture_refs
            ],
            "cninfo_called": False,
        }
        out = os.path.join(snap_dir, f"{row.case_id}_fund_industry_allocation.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")


def write_fund_industry_allocation_first_slice_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_fund_industry_allocation_first_slice_dryrun_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_DRYRUN_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_fund_industry_allocation_first_slice_dryrun_summary(
    dry_rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    shared = compute_fund_industry_allocation_first_slice_planned_shared()
    budget_total = sum(int(r["planned_request_count"]) for r in dry_rows)
    lines = [
        "# CNINFO D 类 fund_industry_allocation First-Slice Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** fund_industry_allocation first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for live**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_shared_cninfo_requests | **{shared}** |",
        f"| planned_request_budget_total | **{budget_total}** |",
        f"| planned_request_count_total | **{shared}** |",
        f"| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        "- component: **fund_industry_allocation**",
        f"- endpoint: `{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ENDPOINT}`",
        "- query modes: **default** · **rdate**",
        "- shared probes: **default** · **rdate=20260331** · **rdate=20251231**",
        f"- records_path: **{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_RECORDS_PATH}**",
        "- schema: **d_industry_aggregate** · offline F001V industry filter · **no company_code**",
        "- fixture root: `fixtures/d_class/fund_industry_allocation_first_slice/`",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_fund_industry_allocation_first_slice_runner_extension_gate = {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_RUNNER_GATE}",
        f"d_class_fund_industry_allocation_first_slice_live_path_gate = {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_fund_industry_allocation_first_slice_live_gate = {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_GATE}",
        "approval_status = STANDING_SCOPE_AUTHORIZED_OFFLINE",
        "approved_for_live = false",
        "```",
        "",
        "**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**",
        "",
        "Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_fund_industry_allocation_first_slice_dryrun_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def _filter_industry_records(
    records: List[Dict[str, Any]], industry_code: str
) -> List[Dict[str, Any]]:
    """离线按 F001V 过滤行业；industry_code=* 表示全截面。"""
    if industry_code in ("*", "", "ALL"):
        return list(records)
    matched: List[Dict[str, Any]] = []
    for rec in records:
        code = str(rec.get("F001V") or rec.get("f001v") or "").strip()
        if code == industry_code:
            matched.append(rec)
    return matched


def is_fund_industry_allocation_first_slice_acceptable(
    row: FundIndustryAllocationFirstSliceRow,
    summary: Dict[str, str],
) -> bool:
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    eb = row.expected_behavior
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if eb == "empty_but_valid" and rs == "empty_but_valid" and rc == 0:
        return True
    if "empty_but_valid" in eb and rs == "empty_but_valid" and rc == 0:
        return True
    if "captured_normal_or_empty_but_valid" in eb and (
        (rs == "found" and rc >= 1) or (rs == "empty_but_valid" and rc == 0)
    ):
        return qs in ("pass", "needs_review", "")
    if eb == "captured_normal" and rs == "found" and rc >= 1 and qs in (
        "pass",
        "needs_review",
    ):
        return True
    if "captured_normal" in eb and rs == "found" and rc >= 1 and qs in (
        "pass",
        "needs_review",
    ):
        return True
    if rs == "found" and rc >= 1 and qs in ("pass", "needs_review"):
        return True
    return False


def assess_fund_industry_allocation_first_slice_failure_type(
    row: FundIndustryAllocationFirstSliceRow,
    summary: Dict[str, str],
) -> str:
    if is_fund_industry_allocation_first_slice_acceptable(row, summary):
        return ""
    rs = summary.get("retrieval_status", "")
    if rs in ("http_error", "blocked"):
        return "transport_or_http_error"
    return "expectation_mismatch"


def validate_fund_industry_allocation_first_slice_request_caps(
    stats: LiveStats,
) -> List[str]:
    issues: List[str] = []
    allowed_shared = set(FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_PROBE_KEYS)
    for case_id, count in stats.case_request_counts.items():
        if case_id not in allowed_shared and count > 0:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_REQUEST_REQUIRED}:"
                f"non_shared_case={case_id}={count}"
            )
        if case_id in allowed_shared and count > 1:
            issues.append(
                f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"{case_id}={count}"
            )
    if stats.cninfo_requests > FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TOTAL_MAX_REQUESTS:
        issues.append(
            f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_TOTAL_CAP_EXCEEDED}:"
            f"{stats.cninfo_requests}"
        )
    if stats.cninfo_requests > FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PLANNED_SHARED_REQUESTS:
        issues.append(
            f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_PLAN_MISMATCH}:"
            f"cninfo_requests={stats.cninfo_requests}"
        )
    return issues


def assess_fund_industry_allocation_first_slice_shared_case(
    row: FundIndustryAllocationFirstSliceRow,
    industry_records: List[Dict[str, Any]],
    http_status: int,
    last_error: str,
    endpoint: str,
    used_params: Dict[str, Any],
    shared_cninfo_requests: int,
    probe_key: str,
) -> Dict[str, str]:
    record_count = len(industry_records)
    empty_but_valid = "no"
    needs_review = "no"
    notes_parts: List[str] = [
        f"shared_probe={probe_key}",
        "industry_filter=yes",
        f"query_mode={row.query_mode}",
        "schema=d_industry_aggregate",
    ]

    if last_error in ("rate_limited",) or last_error.startswith("network_error"):
        retrieval_status = (
            "http_error" if last_error.startswith("network_error") else "blocked"
        )
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
        notes_parts.append(
            "industry-level zero rows after F001V filter; legal empty per quality policy"
        )
    else:
        retrieval_status = "found"
        lineage_status = "discovered"
        quality_status = "pass"
        notes_parts.append(f"found {record_count} row(s) for industry filter")

    return {
        "case_id": row.case_id,
        "industry_code": row.industry_code,
        "industry_name": row.industry_name,
        "component": row.component,
        "query_mode": row.query_mode,
        "anchor_rdate": row.anchor_rdate,
        "expected_behavior": row.expected_behavior,
        "retrieval_status": retrieval_status,
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "record_count": str(record_count),
        "empty_but_valid": empty_but_valid,
        "needs_review": needs_review,
        "endpoint_used": endpoint,
        "cninfo_request_count": str(shared_cninfo_requests),
        "db_write": "no",
        "minio_write": "no",
        "rag_run": "no",
        "notes": "; ".join(notes_parts),
        "_http_status": str(http_status),
        "_used_params": used_params,
        "_sample_records": industry_records[:3],
        "_probe_key": probe_key,
    }


def write_fund_industry_allocation_first_slice_live_snapshot(
    row: FundIndustryAllocationFirstSliceRow,
    summary: Dict[str, str],
    output_paths: Dict[str, str],
) -> str:
    snapshot_path = os.path.join(
        output_paths["live_snapshots"],
        f"{row.case_id}_{row.component}.json",
    )
    used_params = summary.get("_used_params") or {}
    sample_records = summary.get("_sample_records") or []
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "case_id": row.case_id,
                "industry_code": row.industry_code,
                "industry_name": row.industry_name,
                "component": row.component,
                "query_mode": row.query_mode,
                "anchor_rdate": row.anchor_rdate,
                "retrieval_status": summary.get("retrieval_status", ""),
                "quality_status": summary.get("quality_status", ""),
                "lineage_status": summary.get("lineage_status", ""),
                "record_count": summary.get("record_count", "0"),
                "endpoint_used": summary.get("endpoint_used", ""),
                "query_params": used_params,
                "sample_records": sample_records,
                "shared_probe": summary.get("_probe_key", ""),
                "cninfo_called": True,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
        f.write("\n")
    return snapshot_path


def compute_fund_industry_allocation_first_slice_execution_gate(
    universe_rows: List[FundIndustryAllocationFirstSliceRow],
    case_summaries: Dict[str, Dict[str, str]],
) -> str:
    acceptable = 0
    for row in universe_rows:
        summary = case_summaries.get(row.case_id, {})
        if is_fund_industry_allocation_first_slice_acceptable(row, summary):
            acceptable += 1
    if acceptable >= 3:
        return FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXECUTION_GATE_PASS
    return FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXECUTION_GATE_FAIL


def build_fund_industry_allocation_first_slice_live_row(
    row: FundIndustryAllocationFirstSliceRow,
    summary: Dict[str, str],
) -> Dict[str, str]:
    acceptable = is_fund_industry_allocation_first_slice_acceptable(row, summary)
    failure_type = assess_fund_industry_allocation_first_slice_failure_type(
        row, summary
    )
    return {
        "case_id": row.case_id,
        "industry_code": row.industry_code,
        "industry_name": row.industry_name,
        "component": row.component,
        "query_mode": row.query_mode,
        "anchor_rdate": row.anchor_rdate,
        "expected_behavior": row.expected_behavior,
        "retrieval_status": summary.get("retrieval_status", ""),
        "quality_status": summary.get("quality_status", ""),
        "lineage_status": summary.get("lineage_status", ""),
        "record_count": summary.get("record_count", "0"),
        "empty_but_valid": summary.get("empty_but_valid", "no"),
        "needs_review": summary.get("needs_review", "no"),
        "endpoint_used": summary.get("endpoint_used", ""),
        "cninfo_request_count": summary.get("cninfo_request_count", "0"),
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


def write_fund_industry_allocation_first_slice_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_fund_industry_allocation_first_slice_live_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_fund_industry_allocation_first_slice_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    quality_rows = [
        {
            "case_id": r["case_id"],
            "component": r["component"],
            "query_mode": r["query_mode"],
            "anchor_rdate": r["anchor_rdate"],
            "expected_behavior": r["expected_behavior"],
            "retrieval_status": r["retrieval_status"],
            "record_count": r["record_count"],
            "quality_status": r["quality_status"],
            "acceptable": r["acceptable"],
            "failure_type": r["failure_type"],
            "cninfo_request_count": r["cninfo_request_count"],
            "notes": r["notes"],
        }
        for r in rows
    ]
    report_path = os.path.join(
        output_paths["reports"],
        "d_class_fund_industry_allocation_first_slice_quality_report.csv",
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_QUALITY_REPORT_COLUMNS
        )
        writer.writeheader()
        writer.writerows(quality_rows)
    return report_path


def write_fund_industry_allocation_first_slice_live_summary(
    live_rows: List[Dict[str, str]],
    stats: LiveStats,
    gate: str,
    output_paths: Dict[str, str],
) -> str:
    acceptable = sum(1 for r in live_rows if r["acceptable"] == "yes")
    lines = [
        "# CNINFO D 类 fund_industry_allocation First-Slice Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** fund_industry_allocation first-slice live path · **live_gate=NOT_APPROVED**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(live_rows)}** |",
        f"| acceptable | **{acceptable}/{len(live_rows)}** |",
        f"| shared_cninfo_requests | **{stats.cninfo_requests}** |",
        f"| CNINFO calls | **{stats.cninfo_requests}** |",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_fund_industry_allocation_first_slice_live_path_gate = {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_PATH_GATE}",
        f"d_class_fund_industry_allocation_first_slice_live_gate = {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_GATE}",
        f"d_class_fund_industry_allocation_first_slice_execution_gate = {gate}",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT bare PASS**",
        "",
    ]
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_fund_industry_allocation_first_slice_live_summary.md",
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return summary_path


def execute_fund_industry_allocation_first_slice_live(
    universe_rows: List[FundIndustryAllocationFirstSliceRow],
    output_paths: Dict[str, str],
) -> int:
    """fund_industry_allocation 第一切片 live：≤3 共享探针 + 离线 F001V 过滤。"""
    endpoints = load_registry_endpoints()
    source_configs = load_table_source_configs()
    component_cfg = copy.deepcopy(
        source_configs.get(FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_COMPONENT, {})
    )
    endpoint = endpoints.get(
        FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_COMPONENT,
        component_cfg.get("api_url", FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_ENDPOINT),
    )
    component_cfg["api_url"] = endpoint

    for row in universe_rows:
        planned = compute_fund_industry_allocation_first_slice_planned_requests(row)
        if planned > FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PER_CASE_MAX_REQUESTS:
            print(
                f"ERROR: {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PER_CASE_CAP_EXCEEDED}:"
                f"planned={planned}",
                file=sys.stderr,
            )
            return 2

    shared_plan = compute_fund_industry_allocation_first_slice_planned_shared()
    if shared_plan != FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PLANNED_SHARED_REQUESTS:
        print(
            f"ERROR: {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_SHARED_PLAN_MISMATCH}:"
            f"got={shared_plan}",
            file=sys.stderr,
        )
        return 2

    session = requests.Session()
    stats = LiveStats()
    probe_payloads: Dict[str, Tuple[Any, int, str, Dict[str, Any]]] = {}
    for probe_key in build_fund_industry_allocation_first_slice_plan():
        params = _build_fund_industry_allocation_first_slice_params_for_probe(probe_key)
        payload, http_status, last_error = _cninfo_request(
            session,
            component_cfg,
            params,
            stats,
            probe_key,
        )
        probe_payloads[probe_key] = (payload, http_status, last_error, params)

    case_summaries: Dict[str, Dict[str, str]] = {}
    for row in sorted(universe_rows, key=lambda r: r.case_id):
        probe_key = resolve_fund_industry_allocation_first_slice_shared_probe_key(row)
        payload, http_status, last_error, used_params = probe_payloads[probe_key]
        all_records = _extract_records(payload) if payload is not None else []
        industry_records = _filter_industry_records(all_records, row.industry_code)
        summary = assess_fund_industry_allocation_first_slice_shared_case(
            row,
            industry_records,
            http_status,
            last_error,
            endpoint,
            used_params,
            stats.cninfo_requests,
            probe_key,
        )
        write_fund_industry_allocation_first_slice_live_snapshot(
            row, summary, output_paths
        )
        public_summary = {
            k: v for k, v in summary.items() if not k.startswith("_")
        }
        case_summaries[row.case_id] = public_summary
        print(
            f"{row.case_id} {public_summary['retrieval_status']}: "
            f"records={public_summary['record_count']} "
            f"shared_requests={stats.cninfo_requests} probe={probe_key}",
            flush=True,
        )

    cap_issues = validate_fund_industry_allocation_first_slice_request_caps(stats)
    if cap_issues:
        print(
            "ERROR: fund_industry_allocation first-slice request cap validation failed: "
            f"{cap_issues}",
            file=sys.stderr,
        )
        return 2

    gate = compute_fund_industry_allocation_first_slice_execution_gate(
        universe_rows, case_summaries
    )
    if stats.db_writes or stats.minio_writes or stats.rag_runs:
        gate = FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXECUTION_GATE_FAIL

    live_rows = [
        build_fund_industry_allocation_first_slice_live_row(
            row, case_summaries[row.case_id]
        )
        for row in sorted(universe_rows, key=lambda r: r.case_id)
        if row.case_id in case_summaries
    ]

    report_path = write_fund_industry_allocation_first_slice_live_report(
        live_rows, output_paths
    )
    quality_path = write_fund_industry_allocation_first_slice_quality_report(
        live_rows, output_paths
    )
    summary_path = write_fund_industry_allocation_first_slice_live_summary(
        live_rows, stats, gate, output_paths
    )

    print(
        f"mode=fund_industry_allocation_first_slice_live cases={len(live_rows)} "
        f"acceptable={sum(1 for r in live_rows if r['acceptable'] == 'yes')}/"
        f"{len(live_rows)} cninfo_calls={stats.cninfo_requests} "
        f"shared_request={FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_PLANNED_SHARED_REQUESTS}"
    )
    print(
        f"gate=d_class_fund_industry_allocation_first_slice_execution_gate={gate}"
    )
    print(
        "live_path_gate=d_class_fund_industry_allocation_first_slice_live_path_gate="
        f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_PATH_GATE}"
    )
    print(
        "live_gate=d_class_fund_industry_allocation_first_slice_live_gate="
        f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_GATE}"
    )
    print(f"live_report={report_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_EXECUTION_GATE_PASS else 1


def run_fund_industry_allocation_first_slice(args: argparse.Namespace) -> int:
    enforce_fund_industry_allocation_first_slice_forbidden_options(args)
    enforce_fund_industry_allocation_first_slice_live_approval_gate(args)

    if args.universe_csv == DEFAULT_UNIVERSE_CSV:
        print(
            f"ERROR: {FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_UNIVERSE_CSV_REQUIRED}",
            file=sys.stderr,
        )
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    ok_root, root_err = validate_fund_industry_allocation_first_slice_output_root(
        args.output_root
    )
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    universe_rows = load_fund_industry_allocation_first_slice_universe(args.universe_csv)
    universe_issues = validate_fund_industry_allocation_first_slice_universe(
        universe_rows
    )
    if universe_issues:
        print(
            "ERROR: fund_industry_allocation first-slice universe validation failed: "
            f"{universe_issues}",
            file=sys.stderr,
        )
        return 2

    output_root = _normalize_output_root(args.output_root)
    output_paths = ensure_output_layout(output_root, args.mode)
    enforce_fund_industry_allocation_first_slice_write_block_targets(output_paths)

    if args.mode == "live":
        return execute_fund_industry_allocation_first_slice_live(
            universe_rows, output_paths
        )

    dry_rows = build_fund_industry_allocation_first_slice_dryrun_rows(
        universe_rows, output_root
    )
    write_fund_industry_allocation_first_slice_planned_snapshots(
        universe_rows, output_paths
    )
    report_path = write_fund_industry_allocation_first_slice_dryrun_report(
        dry_rows, output_paths
    )
    summary_path = write_fund_industry_allocation_first_slice_dryrun_summary(
        dry_rows, output_paths, args.universe_csv
    )
    shared = compute_fund_industry_allocation_first_slice_planned_shared()
    print(
        f"mode=fund_industry_allocation_first_slice_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={shared} cninfo_calls=0"
    )
    print(
        "gate=d_class_fund_industry_allocation_first_slice_runner_extension_gate="
        f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_RUNNER_GATE}"
    )
    print(
        "live_path_gate=d_class_fund_industry_allocation_first_slice_live_path_gate="
        f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_PATH_GATE}"
    )
    print(
        "live_gate=d_class_fund_industry_allocation_first_slice_live_gate="
        f"{FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_LIVE_GATE}"
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
    if case.component == "block_trade":
        p = copy.deepcopy(base)
        if "tdate" not in p:
            p["tdate"] = BLOCK_TRADE_FIRST_SLICE_ANCHOR_TDATE
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
    param_list: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, str]:
    # param_list 显式传入时（如 shareholder_change first-slice）跳过 generic multi-probe
    if param_list is None:
        param_list = _build_live_params(case, source_cfg)
        multi_probe = case.component in (
            "restricted_shares_unlock",
            "shareholder_change",
            "executive_shareholding",
        )
    else:
        multi_probe = False
    all_records: List[Dict[str, Any]] = []
    last_error = ""
    http_status = 0
    used_params: Dict[str, Any] = {}

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
    parser.add_argument(
        "--block-trade-first-slice",
        action="store_true",
        help="启用 block_trade 第一切片模式（仅 DBT001–DBT005）",
    )
    parser.add_argument(
        "--approve-d-class-block-trade-first-slice",
        action="store_true",
        help="显式批准 block_trade first-slice live（须人工批准 · 本任务不执行真实 live）",
    )
    parser.add_argument(
        "--restricted-shares-unlock-first-slice",
        action="store_true",
        help="启用 restricted_shares_unlock 第一切片模式（仅 DRU001–DRU005）",
    )
    parser.add_argument(
        "--approve-d-class-restricted-shares-unlock-first-slice",
        action="store_true",
        help="显式批准 restricted_shares_unlock first-slice live（须人工批准 · 本任务不执行真实 live）",
    )
    parser.add_argument(
        "--equity-pledge-first-slice",
        action="store_true",
        help="启用 equity_pledge 第一切片模式（仅 DEP001–DEP005）",
    )
    parser.add_argument(
        "--approve-d-class-equity-pledge-first-slice",
        action="store_true",
        help="显式批准 equity_pledge first-slice live（须人工批准 · live 尚未实现）",
    )
    parser.add_argument(
        "--shareholder-change-first-slice",
        action="store_true",
        help="启用 shareholder_change 第一切片模式（仅 DSC001–DSC005）",
    )
    parser.add_argument(
        "--approve-d-class-shareholder-change-first-slice",
        action="store_true",
        help="显式批准 shareholder_change first-slice live（须人工批准）",
    )
    parser.add_argument(
        "--executive-shareholding-first-slice",
        action="store_true",
        help="启用 executive_shareholding 第一切片模式（仅 DES001–DES005）",
    )
    parser.add_argument(
        "--approve-d-class-executive-shareholding-first-slice",
        action="store_true",
        help="显式批准 executive_shareholding first-slice live（须人工批准）",
    )
    parser.add_argument(
        "--abnormal-trading-first-slice",
        action="store_true",
        help="启用 abnormal_trading 第一切片模式（仅 DAT001–DAT005）",
    )
    parser.add_argument(
        "--approve-d-class-abnormal-trading-first-slice",
        action="store_true",
        help="显式批准 abnormal_trading first-slice live（须人工批准 · live 尚未实现）",
    )
    parser.add_argument(
        "--shareholder-data-first-slice",
        action="store_true",
        help="启用 shareholder_data 第一切片模式（仅 DSD001–DSD005）",
    )
    parser.add_argument(
        "--approve-d-class-shareholder-data-first-slice",
        action="store_true",
        help="显式批准 shareholder_data first-slice live（须人工批准 · 本任务未授权）",
    )

    parser.add_argument(
        "--fund-industry-allocation-first-slice",
        action="store_true",
        help="启用 fund_industry_allocation 第一切片模式（仅 DFIA001–DFIA005）",
    )
    parser.add_argument(
        "--approve-d-class-fund-industry-allocation-first-slice",
        action="store_true",
        help="显式批准 fund_industry_allocation first-slice live（须人工批准 · 本任务未授权）",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.fund_industry_allocation_first_slice:
        if args.output_root is None:
            args.output_root = DEFAULT_FUND_INDUSTRY_ALLOCATION_FIRST_SLICE_OUTPUT_ROOT
        return run_fund_industry_allocation_first_slice(args)

    if args.shareholder_data_first_slice:
        if args.output_root is None:
            args.output_root = DEFAULT_SHAREHOLDER_DATA_FIRST_SLICE_OUTPUT_ROOT
        return run_shareholder_data_first_slice(args)

    if args.abnormal_trading_first_slice:
        if args.output_root is None:
            args.output_root = DEFAULT_ABNORMAL_TRADING_FIRST_SLICE_OUTPUT_ROOT
        return run_abnormal_trading_first_slice(args)

    if args.executive_shareholding_first_slice:
        if args.output_root is None:
            args.output_root = DEFAULT_EXECUTIVE_SHAREHOLDING_FIRST_SLICE_OUTPUT_ROOT
        return run_executive_shareholding_first_slice(args)

    if args.shareholder_change_first_slice:
        if args.output_root is None:
            args.output_root = DEFAULT_SHAREHOLDER_CHANGE_FIRST_SLICE_OUTPUT_ROOT
        return run_shareholder_change_first_slice(args)

    if args.equity_pledge_first_slice:
        if args.output_root is None:
            args.output_root = DEFAULT_EQUITY_PLEDGE_FIRST_SLICE_OUTPUT_ROOT
        return run_equity_pledge_first_slice(args)

    if args.restricted_shares_unlock_first_slice:
        if args.output_root is None:
            args.output_root = DEFAULT_RESTRICTED_SHARES_UNLOCK_FIRST_SLICE_OUTPUT_ROOT
        return run_restricted_shares_unlock_first_slice(args)

    if args.block_trade_first_slice:
        if args.output_root is None:
            args.output_root = DEFAULT_BLOCK_TRADE_FIRST_SLICE_OUTPUT_ROOT
        return run_block_trade_first_slice(args)

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
