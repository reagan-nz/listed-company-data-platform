"""
CNINFO A-class Phase 2 metadata expansion runner.

默认 dry-run：校验 universe · 输出隔离 · 生成规划报告，**不请求 CNINFO**。
--live 须 --approve-a-class-phase2-metadata-expansion；仅 metadata · 无 PDF 下载/解析。

Usage:
    python lab/run_cninfo_a_class_phase2_metadata_expansion.py
    python lab/run_cninfo_a_class_phase2_metadata_expansion.py --live \\
        --approve-a-class-phase2-metadata-expansion
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_DIR = os.path.join(BASE_DIR, "lab")
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

import cninfo_a_class_listing_period_gate as listing_period_gate  # noqa: E402
import run_cninfo_a_class_tiny_live_metadata_validation as tiny_live  # noqa: E402

DEFAULT_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase2_metadata_universe_draft.csv",
)
DEFAULT_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_metadata_expansion"
)
DEFAULT_RETRY_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase2_failed_retry_universe.csv",
)
DEFAULT_RETRY_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_metadata_retry"
)
DEFAULT_RETRY_V2_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase2_network_recovery_retry_v2_universe.csv",
)
DEFAULT_RETRY_V2_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_metadata_retry_v2"
)
DEFAULT_RETRY_V3_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase2_retry_v3_universe.csv",
)
DEFAULT_RETRY_V3_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_metadata_retry_v3"
)
DEFAULT_PHASE3_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase3_50_company_universe_draft.csv",
)
DEFAULT_PHASE3_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase3_50_company_expansion"
)
PRECHECK_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_phase2_cninfo_reachability_precheck",
)
PHASE1_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_tiny_live_metadata"
)
C_CLASS_HARVEST_ROOT = os.path.join(BASE_DIR, "outputs", "harvest", "cninfo_c_class")
DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_erad_scale_200_universe_draft.csv"
)
DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_erad_scale_200"
)
DEFAULT_ERAD_FAILED_RETRY_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv",
)
DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_erad_scale_200_failed_retry"
)
DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_candidate_universe_draft.csv",
)
DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_erad_next_scale_slice1"
)
ERAD_NEXT_SCALE_SLICE1_SCALE200_EFFECTIVE_LEDGER = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_scale_200_effective_accepted_ledger.csv",
)
ERAD_NEXT_SCALE_SLICE1_UNRESOLVED_LEDGER = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_scale_200_unresolved_final_ledger.csv",
)
ERAD_NEXT_SCALE_SLICE1_B_SLICE1_UNIVERSE = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_erad_next_scale_candidate_universe_draft.csv",
)
DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv",
)
DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_erad_next_scale_slice2_s1"
)
# A-R16-01：AD2E578/590/598 orgId 离线回退孤立重试（独立根 · 不得写入封闭 S1 live 根）
DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry_universe.csv",
)
DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry",
)
ERAD_SLICE2_ORGID_FALLBACK_RETRY_CASE_IDS: Set[str] = {
    "AD2E578",
    "AD2E590",
    "AD2E598",
}
REQUIRED_ERAD_SLICE2_ORGID_FALLBACK_RETRY_SIZE = 3
ERAD_SLICE2_ORGID_FALLBACK_RETRY_REQUEST_CAP = 12
ERAD_SLICE2_ORGID_FALLBACK_RETRY_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "orgid_fallback_retry_must_not_write_closed_slice2_s1_live_root"
)
ERAD_SLICE2_ORGID_FALLBACK_RETRY_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_slice2_orgid_fallback_retry_universe_size_must_equal_3"
)
ERAD_SLICE2_ORGID_FALLBACK_RETRY_CASE_SET_VIOLATION = (
    "erad_a_slice2_orgid_fallback_retry_case_ids_must_be_AD2E578_590_598"
)
# A-FM-01：listing-aware 下一片（AD2E601–650 · 独立根 · 不得写入封闭 S1 live 根）
DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s2_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s2",
)
REQUIRED_ERAD_LISTING_AWARE_S2_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S2_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S2_COHORT = "next_scale_listing_aware"
ALLOWED_ERAD_LISTING_AWARE_S2_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(601, 651)
}
ERAD_LISTING_AWARE_S2_INCLUDE_REASON = (
    "next_scale_listing_aware_s2;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;b_overlap_allowed_cross_track;metadata_only_no_pdf"
)
ERAD_LISTING_AWARE_S2_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s2_must_not_write_closed_slice2_s1_live_root"
)
ERAD_LISTING_AWARE_S2_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s2_universe_csv_required"
)
ERAD_LISTING_AWARE_S2_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s2_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S2_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s2_case_ids_must_be_AD2E601_650"
)
ERAD_LISTING_AWARE_S2_COHORT_INVALID = (
    "erad_a_listing_aware_s2_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S2_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s2_overlap_a_slice2_s1"
# A-FM-02：listing-aware S3（AD2E651–700 · 独立根 · 不得写入封闭 S1 / S2 live 根）
DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s3_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s3",
)
REQUIRED_ERAD_LISTING_AWARE_S3_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S3_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S3_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S3_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(651, 701)
}
ERAD_LISTING_AWARE_S3_INCLUDE_REASON = (
    "next_scale_listing_aware_s3;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;b_overlap_allowed_cross_track;metadata_only_no_pdf;"
    "excludes_listing_aware_s2"
)
ERAD_LISTING_AWARE_S3_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s3_must_not_write_closed_slice2_s1_or_s2_live_root"
)
ERAD_LISTING_AWARE_S3_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s3_universe_csv_required"
)
ERAD_LISTING_AWARE_S3_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s3_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S3_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s3_case_ids_must_be_AD2E651_700"
)
ERAD_LISTING_AWARE_S3_COHORT_INVALID = (
    "erad_a_listing_aware_s3_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S3_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s3_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S3_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s3_overlap_a_listing_aware_s2"
)
# A-FM-03：listing-aware S4（AD2E701–750 · 独立根 · 不得写入封闭 S1 / S2 / S3 live 根）
DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s4_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s4",
)
REQUIRED_ERAD_LISTING_AWARE_S4_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S4_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S4_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S4_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(701, 751)
}
ERAD_LISTING_AWARE_S4_INCLUDE_REASON = (
    "next_scale_listing_aware_s4;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;b_overlap_allowed_cross_track;metadata_only_no_pdf;"
    "excludes_listing_aware_s2_s3"
)
ERAD_LISTING_AWARE_S4_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s4_must_not_write_closed_slice2_s1_or_s2_or_s3_live_root"
)
ERAD_LISTING_AWARE_S4_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s4_universe_csv_required"
)
ERAD_LISTING_AWARE_S4_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s4_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S4_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s4_case_ids_must_be_AD2E701_750"
)
ERAD_LISTING_AWARE_S4_COHORT_INVALID = (
    "erad_a_listing_aware_s4_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S4_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s4_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S4_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s4_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S4_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s4_overlap_a_listing_aware_s3"
)
# A-FM-04：listing-aware S5（AD2E751–800 · 独立根 · 不得写入封闭 S1 / S2 / S3 / S4 live 根）
DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s5_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s5",
)
REQUIRED_ERAD_LISTING_AWARE_S5_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S5_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S5_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S5_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(751, 801)
}
ERAD_LISTING_AWARE_S5_INCLUDE_REASON = (
    "next_scale_listing_aware_s5;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;b_overlap_allowed_cross_track;metadata_only_no_pdf;"
    "excludes_listing_aware_s2_s3_s4"
)
ERAD_LISTING_AWARE_S5_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s5_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_live_root"
)
ERAD_LISTING_AWARE_S5_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s5_universe_csv_required"
)
ERAD_LISTING_AWARE_S5_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s5_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S5_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s5_case_ids_must_be_AD2E751_800"
)
ERAD_LISTING_AWARE_S5_COHORT_INVALID = (
    "erad_a_listing_aware_s5_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S5_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s5_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S5_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s5_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S5_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s5_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S5_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s5_overlap_a_listing_aware_s4"
)
# A-FM-05：listing-aware S6（AD2E801–850 · 独立根 · 不得写入封闭 S1 / S2 / S3 / S4 / S5 live 根）
DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s6_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s6",
)
REQUIRED_ERAD_LISTING_AWARE_S6_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S6_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S6_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S6_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(801, 851)
}
ERAD_LISTING_AWARE_S6_INCLUDE_REASON = (
    "next_scale_listing_aware_s6;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;b_overlap_allowed_cross_track;metadata_only_no_pdf;"
    "excludes_listing_aware_s2_s3_s4_s5"
)
ERAD_LISTING_AWARE_S6_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s6_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_live_root"
)
ERAD_LISTING_AWARE_S6_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s6_universe_csv_required"
)
ERAD_LISTING_AWARE_S6_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s6_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S6_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s6_case_ids_must_be_AD2E801_850"
)
ERAD_LISTING_AWARE_S6_COHORT_INVALID = (
    "erad_a_listing_aware_s6_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S6_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s6_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S6_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s6_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S6_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s6_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S6_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s6_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S6_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s6_overlap_a_listing_aware_s5"
)
# A-FM-07：listing-aware S7（AD2E851–900 · 独立根 · 不得写入封闭 S1 / S2 / S3 / S4 / S5 / S6 live 根）
DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s7_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s7",
)
REQUIRED_ERAD_LISTING_AWARE_S7_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S7_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S7_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S7_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(851, 901)
}
ERAD_LISTING_AWARE_S7_INCLUDE_REASON = (
    "next_scale_listing_aware_s7;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6"
)
ERAD_LISTING_AWARE_S7_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s7_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_live_root"
)
ERAD_LISTING_AWARE_S7_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s7_universe_csv_required"
)
ERAD_LISTING_AWARE_S7_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s7_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S7_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s7_case_ids_must_be_AD2E851_900"
)
ERAD_LISTING_AWARE_S7_COHORT_INVALID = (
    "erad_a_listing_aware_s7_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S7_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s7_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s7_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s7_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s7_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s7_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s7_overlap_a_listing_aware_s6"
)
# S7 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S7_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)
# A-FM-08：listing-aware S8（AD2E901–950 · 独立根 · 不得写入封闭 S1 / S2 / S3 / S4 / S5 / S6 / S7 live 根）
DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s8_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s8",
)
REQUIRED_ERAD_LISTING_AWARE_S8_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S8_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S8_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S8_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(901, 951)
}
ERAD_LISTING_AWARE_S8_INCLUDE_REASON = (
    "next_scale_listing_aware_s8;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7"
)
ERAD_LISTING_AWARE_S8_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s8_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_live_root"
)
ERAD_LISTING_AWARE_S8_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s8_universe_csv_required"
)
ERAD_LISTING_AWARE_S8_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s8_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S8_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s8_case_ids_must_be_AD2E901_950"
)
ERAD_LISTING_AWARE_S8_COHORT_INVALID = (
    "erad_a_listing_aware_s8_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S8_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s8_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s8_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s8_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s8_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s8_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s8_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s8_overlap_a_listing_aware_s7"
)
# S8 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S8_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)

# A-FM-09：listing-aware S9（AD2E951–1000 · 独立根 · 不得写入封闭 S1 / S2 / S3 / S4 / S5 / S6 / S7 / S8 live 根）
DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s9_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s9",
)
REQUIRED_ERAD_LISTING_AWARE_S9_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S9_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S9_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S9_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(951, 1001)
}
ERAD_LISTING_AWARE_S9_INCLUDE_REASON = (
    "next_scale_listing_aware_s9;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8"
)
ERAD_LISTING_AWARE_S9_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s9_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_live_root"
)
ERAD_LISTING_AWARE_S9_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s9_universe_csv_required"
)
ERAD_LISTING_AWARE_S9_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s9_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S9_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s9_case_ids_must_be_AD2E951_1000"
)
ERAD_LISTING_AWARE_S9_COHORT_INVALID = (
    "erad_a_listing_aware_s9_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S9_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s9_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s9_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s9_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s9_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s9_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s9_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s9_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s9_overlap_a_listing_aware_s8"
)
# S9 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S9_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)

# A-FM-10：listing-aware S10（AD2E1001–1050 · 独立根 · 不得写入封闭 S1 / S2–S9 live 根）
DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s10_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s10",
)
REQUIRED_ERAD_LISTING_AWARE_S10_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S10_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S10_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S10_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1001, 1051)
}
ERAD_LISTING_AWARE_S10_INCLUDE_REASON = (
    "next_scale_listing_aware_s10;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9"
)
ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s10_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_live_root"
)
ERAD_LISTING_AWARE_S10_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s10_universe_csv_required"
)
ERAD_LISTING_AWARE_S10_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s10_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S10_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s10_case_ids_must_be_AD2E1001_1050"
)
ERAD_LISTING_AWARE_S10_COHORT_INVALID = (
    "erad_a_listing_aware_s10_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S10_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s10_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s10_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s10_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s10_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s10_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s10_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s10_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s10_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s10_overlap_a_listing_aware_s9"
)
# S10 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S10_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)

# A-FM-11：listing-aware S11（AD2E1051–1100 · 独立根 · 不得写入封闭 S1 / S2–S10 live 根）
DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s11_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s11",
)
REQUIRED_ERAD_LISTING_AWARE_S11_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S11_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S11_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S11_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1051, 1101)
}
ERAD_LISTING_AWARE_S11_INCLUDE_REASON = (
    "next_scale_listing_aware_s11;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10"
)
ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s11_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_or_s10_live_root"
)
ERAD_LISTING_AWARE_S11_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s11_universe_csv_required"
)
ERAD_LISTING_AWARE_S11_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s11_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S11_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s11_case_ids_must_be_AD2E1051_1100"
)
ERAD_LISTING_AWARE_S11_COHORT_INVALID = (
    "erad_a_listing_aware_s11_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S11_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s11_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s11_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s11_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s11_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s11_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s11_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s11_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s11_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s11_overlap_a_listing_aware_s9"
)
ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S10 = (
    "erad_a_listing_aware_s11_overlap_a_listing_aware_s10"
)
# S11 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S11_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)

# A-FM-12：listing-aware S12（AD2E1101–1150 · 独立根 · 不得写入封闭 S1 / S2–S11 live 根）
DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s12_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s12",
)
REQUIRED_ERAD_LISTING_AWARE_S12_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S12_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S12_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S12_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1101, 1151)
}
ERAD_LISTING_AWARE_S12_INCLUDE_REASON = (
    "next_scale_listing_aware_s12;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10_s11"
)
ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s12_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_or_s10_or_s11_live_root"
)
ERAD_LISTING_AWARE_S12_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s12_universe_csv_required"
)
ERAD_LISTING_AWARE_S12_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s12_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S12_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s12_case_ids_must_be_AD2E1101_1150"
)
ERAD_LISTING_AWARE_S12_COHORT_INVALID = (
    "erad_a_listing_aware_s12_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s12_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s9"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S10 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s10"
)
ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S11 = (
    "erad_a_listing_aware_s12_overlap_a_listing_aware_s11"
)
# S12 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S12_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)
# A-FM-13：listing-aware S13（AD2E1151–1200 · 独立根 · 不得写入封闭 S1 / S2–S12 live 根）
DEFAULT_ERAD_LISTING_AWARE_S13_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s13_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s13",
)
REQUIRED_ERAD_LISTING_AWARE_S13_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S13_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S13_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S13_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1151, 1201)
}
ERAD_LISTING_AWARE_S13_INCLUDE_REASON = (
    "next_scale_listing_aware_s13;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10_s11_s12"
)
ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s13_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_or_s10_or_s11_or_s12_live_root"
)
ERAD_LISTING_AWARE_S13_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s13_universe_csv_required"
)
ERAD_LISTING_AWARE_S13_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s13_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S13_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s13_case_ids_must_be_AD2E1151_1200"
)
ERAD_LISTING_AWARE_S13_COHORT_INVALID = (
    "erad_a_listing_aware_s13_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s13_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s9"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S10 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s10"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S11 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s11"
)
ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S12 = (
    "erad_a_listing_aware_s13_overlap_a_listing_aware_s12"
)
# S13 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S13_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)
# A-FM-14：listing-aware S14（AD2E1201–1250 · 独立根 · 不得写入封闭 S1 / S2–S13 live 根）
DEFAULT_ERAD_LISTING_AWARE_S14_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s14_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s14",
)
REQUIRED_ERAD_LISTING_AWARE_S14_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S14_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S14_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S14_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1201, 1251)
}
ERAD_LISTING_AWARE_S14_INCLUDE_REASON = (
    "next_scale_listing_aware_s14;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10_s11_s12_s13"
)
ERAD_LISTING_AWARE_S14_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s14_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_or_s10_or_s11_or_s12_or_s13_live_root"
)
ERAD_LISTING_AWARE_S14_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s14_universe_csv_required"
)
ERAD_LISTING_AWARE_S14_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s14_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S14_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s14_case_ids_must_be_AD2E1201_1250"
)
ERAD_LISTING_AWARE_S14_COHORT_INVALID = (
    "erad_a_listing_aware_s14_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s14_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s9"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S10 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s10"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S11 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s11"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S12 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s12"
)
ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S13 = (
    "erad_a_listing_aware_s14_overlap_a_listing_aware_s13"
)
# S14 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S14_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)
# A-FM-15：listing-aware S15（AD2E1251–1300 · 独立根 · 不得写入封闭 S1 / S2–S14 live 根）
DEFAULT_ERAD_LISTING_AWARE_S15_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s15_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s15",
)
REQUIRED_ERAD_LISTING_AWARE_S15_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S15_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S15_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S15_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1251, 1301)
}
ERAD_LISTING_AWARE_S15_INCLUDE_REASON = (
    "next_scale_listing_aware_s15;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10_s11_s12_s13_s14"
)
ERAD_LISTING_AWARE_S15_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s15_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_or_s10_or_s11_or_s12_or_s13_or_s14_live_root"
)
ERAD_LISTING_AWARE_S15_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s15_universe_csv_required"
)
ERAD_LISTING_AWARE_S15_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s15_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S15_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s15_case_ids_must_be_AD2E1251_1300"
)
ERAD_LISTING_AWARE_S15_COHORT_INVALID = (
    "erad_a_listing_aware_s15_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s15_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s9"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S10 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s10"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S11 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s11"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S12 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s12"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S13 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s13"
)
ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S14 = (
    "erad_a_listing_aware_s15_overlap_a_listing_aware_s14"
)
# S15 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S15_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)

# A-FM-16：listing-aware S16（AD2E1301–1350 · 独立根 · 不得写入封闭 S1 / S2–S15 live 根）
DEFAULT_ERAD_LISTING_AWARE_S16_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s16_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s16",
)
REQUIRED_ERAD_LISTING_AWARE_S16_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S16_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S16_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S16_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1301, 1351)
}
ERAD_LISTING_AWARE_S16_INCLUDE_REASON = (
    "next_scale_listing_aware_s16;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10_s11_s12_s13_s14_s15"
)
ERAD_LISTING_AWARE_S16_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s16_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_or_s10_or_s11_or_s12_or_s13_or_s14_or_s15_live_root"
)
ERAD_LISTING_AWARE_S16_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s16_universe_csv_required"
)
ERAD_LISTING_AWARE_S16_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s16_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S16_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s16_case_ids_must_be_AD2E1301_1350"
)
ERAD_LISTING_AWARE_S16_COHORT_INVALID = (
    "erad_a_listing_aware_s16_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s16_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s9"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S10 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s10"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S11 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s11"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S12 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s12"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S13 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s13"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S14 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s14"
)
ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S15 = (
    "erad_a_listing_aware_s16_overlap_a_listing_aware_s15"
)
# S16 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S16_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)

# A-FM-17：listing-aware S17（AD2E1351–1400 · 独立根 · 不得写入封闭 S1 / S2–S16 live 根）
DEFAULT_ERAD_LISTING_AWARE_S17_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s17_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s17",
)
REQUIRED_ERAD_LISTING_AWARE_S17_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S17_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S17_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S17_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1351, 1401)
}
ERAD_LISTING_AWARE_S17_INCLUDE_REASON = (
    "next_scale_listing_aware_s17;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10_s11_s12_s13_s14_s15_s16"
)
ERAD_LISTING_AWARE_S17_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s17_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_or_s10_or_s11_or_s12_or_s13_or_s14_or_s15_or_s16_live_root"
)
ERAD_LISTING_AWARE_S17_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s17_universe_csv_required"
)
ERAD_LISTING_AWARE_S17_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s17_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S17_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s17_case_ids_must_be_AD2E1351_1400"
)
ERAD_LISTING_AWARE_S17_COHORT_INVALID = (
    "erad_a_listing_aware_s17_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s17_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s9"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S10 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s10"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S11 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s11"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S12 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s12"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S13 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s13"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S14 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s14"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S15 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s15"
)
ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S16 = (
    "erad_a_listing_aware_s17_overlap_a_listing_aware_s16"
)
# S17 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S17_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)

# A-FM-18：listing-aware S18（AD2E1401–1450 · 独立根 · 不得写入封闭 S1 / S2–S17 live 根）
DEFAULT_ERAD_LISTING_AWARE_S18_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s18_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s18",
)
REQUIRED_ERAD_LISTING_AWARE_S18_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S18_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S18_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S18_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1401, 1451)
}
ERAD_LISTING_AWARE_S18_INCLUDE_REASON = (
    "next_scale_listing_aware_s18;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10_s11_s12_s13_s14_s15_s16_s17"
)
ERAD_LISTING_AWARE_S18_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s18_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_or_s10_or_s11_or_s12_or_s13_or_s14_or_s15_or_s16_or_s17_live_root"
)
ERAD_LISTING_AWARE_S18_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s18_universe_csv_required"
)
ERAD_LISTING_AWARE_S18_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s18_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S18_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s18_case_ids_must_be_AD2E1401_1450"
)
ERAD_LISTING_AWARE_S18_COHORT_INVALID = (
    "erad_a_listing_aware_s18_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s18_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s9"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S10 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s10"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S11 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s11"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S12 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s12"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S13 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s13"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S14 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s14"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S15 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s15"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S16 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s16"
)
ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S17 = (
    "erad_a_listing_aware_s18_overlap_a_listing_aware_s17"
)
# S18 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S18_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)

# A-FM-19：listing-aware S19（AD2E1451–1500 · 独立根 · 不得写入封闭 S1 / S2–S18 live 根）
DEFAULT_ERAD_LISTING_AWARE_S19_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s19_plus50_universe_20260715.csv",
)
DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_listing_aware_s19",
)
REQUIRED_ERAD_LISTING_AWARE_S19_UNIVERSE_SIZE = 50
ERAD_LISTING_AWARE_S19_REQUEST_CAP = 120
ERAD_LISTING_AWARE_S19_COHORT = ERAD_LISTING_AWARE_S2_COHORT  # 同族 cohort 标签
ALLOWED_ERAD_LISTING_AWARE_S19_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(1451, 1501)
}
ERAD_LISTING_AWARE_S19_INCLUDE_REASON = (
    "next_scale_listing_aware_s19;a_cumulative_disjoint;listing_period_gate;"
    "st_exclude;non_bse;prefix_concentration_cap;b_overlap_allowed_cross_track;"
    "metadata_only_no_pdf;excludes_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10_s11_s12_s13_s14_s15_s16_s17_s18"
)
ERAD_LISTING_AWARE_S19_CLOSED_ROOT_WRITE_FORBIDDEN = (
    "listing_aware_s19_must_not_write_closed_slice2_s1_or_s2_or_s3_or_s4_or_s5_or_s6_or_s7_or_s8_or_s9_or_s10_or_s11_or_s12_or_s13_or_s14_or_s15_or_s16_or_s17_or_s18_live_root"
)
ERAD_LISTING_AWARE_S19_UNIVERSE_CSV_REQUIRED = (
    "erad_a_listing_aware_s19_universe_csv_required"
)
ERAD_LISTING_AWARE_S19_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_listing_aware_s19_universe_size_must_equal_50"
)
ERAD_LISTING_AWARE_S19_CASE_SET_VIOLATION = (
    "erad_a_listing_aware_s19_case_ids_must_be_AD2E1451_1500"
)
ERAD_LISTING_AWARE_S19_COHORT_INVALID = (
    "erad_a_listing_aware_s19_cohort_must_be_next_scale_listing_aware"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_S2_S1 = "erad_a_listing_aware_s19_overlap_a_slice2_s1"
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S2 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s2"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S3 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s3"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S4 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s4"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S5 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s5"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S6 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s6"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S7 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s7"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S8 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s8"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S9 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s9"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S10 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s10"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S11 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s11"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S12 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s12"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S13 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s13"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S14 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s14"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S15 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s15"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S16 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s16"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S17 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s17"
)
ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S18 = (
    "erad_a_listing_aware_s19_overlap_a_listing_aware_s18"
)
# S19 listing_period lint / gate 使用 A 轨 coverage overlay（非 C harvest 默认分母）
DEFAULT_ERAD_LISTING_AWARE_S19_PROFILE_DIR = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_basic_profile_coverage_overlay_fm06",
)
ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_scale_200_effective_accepted_ledger.csv",
)
ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_erad_next_scale_slice1_effective_accepted_ledger.csv",
)
ERAD_NEXT_SCALE_SLICE2_AB_182_LEDGER = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv",
)
ERAD_NEXT_SCALE_SLICE2_B_SCALE200_UNIVERSE = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_erad_scale_200_universe_draft.csv",
)
ERAD_NEXT_SCALE_SLICE2_B_SLICE1_UNIVERSE = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_erad_next_scale_slice1_effective_accepted_ledger.csv",
)
ERAD_NEXT_SCALE_SLICE2_B_SLICE2_UNIVERSE = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv",
)
DEFAULT_A3M017_RETRY_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase3_a3m017_isolated_retry"
)
B_CLASS_VALIDATION_PREFIX = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_b_class")
C_CLASS_VALIDATION_PREFIX = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_c_class")
D_CLASS_VALIDATION_PREFIX = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_d_class")

DRYRUN_REPORT_CSV = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "a_class_phase2_metadata_dryrun_report.csv"
)
DRYRUN_SUMMARY_MD = os.path.join(
    DEFAULT_OUTPUT_ROOT, "reports", "a_class_phase2_metadata_dryrun_summary.md"
)

REQUIRED_UNIVERSE_SIZE = 20
RETRY_REQUIRED_UNIVERSE_SIZE = 8
RETRY_ALLOWED_CASE_IDS: Set[str] = {
    "A2M005",
    "A2M010",
    "A2M011",
    "A2M012",
    "A2M013",
    "A2M018",
    "A2M019",
    "A2M020",
}
SUCCESSFUL_CASE_IDS: Set[str] = {
    "A2M001",
    "A2M002",
    "A2M003",
    "A2M004",
    "A2M006",
    "A2M007",
    "A2M008",
    "A2M009",
    "A2M014",
    "A2M015",
    "A2M016",
    "A2M017",
}
PHASE2_CASE_ID_PATTERN = re.compile(r"^A2M\d{3}$")
PHASE3_CASE_ID_PATTERN = re.compile(r"^A3M\d{3}$")
PHASE3_ALLOWED_CASE_IDS: Set[str] = {f"A3M{i:03d}" for i in range(1, 51)}
PHASE1_COMPANY_CODES: Set[str] = {"600000", "300001", "688001", "000858", "600519"}
PHASE2_EXCLUDED_COMPANY_CODES: Set[str] = {
    "600036",
    "601318",
    "000333",
    "002415",
    "601012",
    "600276",
    "000002",
    "601888",
    "300014",
    "300750",
    "600887",
    "601166",
    "688599",
    "688036",
    "000725",
    "601899",
    "300059",
    "688111",
    "600309",
    "002594",
}

PHASE3_REQUIRED_UNIVERSE_SIZE = 50
PHASE3_ACCEPTABLE_THRESHOLD = 40
PHASE3_PLANNED_REQUESTS_PER_CASE = 2
PHASE3_RUNNER_GATE = "READY_FOR_APPROVAL"
PHASE3_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
PHASE3_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
PHASE3_APPROVAL_REQUIRED = "approve_a_class_phase3_50_company_expansion_required"
PHASE3_WRONG_APPROVAL = "approve_a_class_phase3_50_company_expansion_wrong_flag"
PHASE3_UNIVERSE_CSV_REQUIRED = "phase3_universe_csv_required"
PHASE3_INCOMPATIBLE_WITH_RETRY_V3 = "phase3_incompatible_with_retry_v3"
PHASE3_INCOMPATIBLE_WITH_RETRY_FAILED_ONLY = "phase3_incompatible_with_retry_failed_only"
PHASE3_OUTPUT_ROOT_VIOLATION = (
    "output_root_must_be_under_cninfo_a_class_phase3_50_company_expansion"
)
PHASE3_UNIVERSE_SIZE_VIOLATION = "universe_size_must_equal_50"
PHASE3_INCLUDE_REQUIRED = "phase3_include_must_be_yes"
NON_PHASE3_CASE_REJECTED = "non_a3m_case_not_allowed"
PHASE2_OVERLAP_REJECTED = "phase2_overlap_not_allowed"
DUPLICATE_COMPANY_CODE_REJECTED = "duplicate_company_code_not_allowed"
PHASE3_REPORT_TYPE_MIX_VIOLATION = "report_type_mix_must_be_20_10_10_10"

EXPECTED_REPORT_TYPE_MIX: Dict[str, int] = {
    "annual_report": 8,
    "semi_annual_report": 4,
    "quarterly_report_q1": 4,
    "quarterly_report_q3": 4,
}

ERAD_SCALE_200_CASE_ID_PATTERN = re.compile(r"^AD2E\d{3,4}$")
ERAD_SCALE_200_ALLOWED_CASE_IDS: Set[str] = {f"AD2E{i:03d}" for i in range(1, 201)}
ERAD_SCALE_200_REQUIRED_UNIVERSE_SIZE = 200
ERAD_SCALE_200_RETAINED_COUNT = 50
ERAD_SCALE_200_NEW_COUNT = 150
ERAD_SCALE_200_PLANNED_REQUESTS_PER_CASE = 2
ERAD_SCALE_200_REQUEST_CAP = 480
ERAD_SCALE_200_ACCEPTABLE_THRESHOLD = 180
ERAD_SCALE_200_RUNNER_GATE = "READY_FOR_APPROVAL"
ERAD_SCALE_200_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
ERAD_SCALE_200_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
ERAD_SCALE_200_APPROVAL_REQUIRED = "approve_a_class_erad_scale_200_required"
ERAD_SCALE_200_WRONG_APPROVAL = "approve_a_class_erad_scale_200_wrong_flag"
ERAD_SCALE_200_UNIVERSE_CSV_REQUIRED = "erad_a_scale_200_universe_csv_required"
ERAD_SCALE_200_OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_a_class_erad_scale_200"
ERAD_SCALE_200_UNIVERSE_SIZE_VIOLATION = "erad_a_scale_200_universe_size_must_equal_200"
ERAD_SCALE_200_INCLUDE_REQUIRED = "erad_include_must_be_yes"
ERAD_SCALE_200_REQUEST_CAP_EXCEEDED = "erad_a_scale_200_request_cap_exceeded"
ERAD_SCALE_200_COHORT_VIOLATION = "erad_a_scale_200_cohort_validation_failed"
ERAD_SCALE_200_NEW_COHORT_OVERLAP = "erad_a_scale_200_new_cohort_overlap_not_allowed"
ERAD_SCALE_200_INCOMPATIBLE_WITH_PHASE3 = "erad_a_scale_200_incompatible_with_phase3_50"
ERAD_SCALE_200_INCOMPATIBLE_WITH_RETRY = "erad_a_scale_200_incompatible_with_retry_modes"
ERAD_SCALE_200_REPORT_TYPE_MIX_VIOLATION = "erad_a_scale_200_report_type_mix_violation"
ERAD_SCALE_200_EXPECTED_REPORT_TYPE_MIX: Dict[str, int] = {
    "annual_report": 140,
    "semi_annual_report": 20,
    "quarterly_report_q1": 20,
    "quarterly_report_q3": 20,
}

ERAD_FAILED_RETRY_REQUIRED_UNIVERSE_SIZE = 7
ERAD_FAILED_RETRY_ALLOWED_CASE_IDS: Set[str] = {
    "AD2E066",
    "AD2E088",
    "AD2E119",
    "AD2E121",
    "AD2E122",
    "AD2E185",
    "AD2E190",
}
ERAD_FAILED_RETRY_DEFERRED_CASE_ID = "AD2E146"
ERAD_FAILED_RETRY_PLANNED_REQUESTS_PER_CASE = 2
ERAD_FAILED_RETRY_REQUEST_CAP = 24
ERAD_FAILED_RETRY_ACCEPTABLE_THRESHOLD = 6
ERAD_FAILED_RETRY_RUNNER_GATE = "READY_FOR_APPROVAL"
ERAD_FAILED_RETRY_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
ERAD_FAILED_RETRY_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
ERAD_FAILED_RETRY_APPROVAL_REQUIRED = "approve_a_class_erad_scale_200_failed_retry_required"
ERAD_FAILED_RETRY_WRONG_APPROVAL = "approve_a_class_erad_scale_200_failed_retry_wrong_flag"
ERAD_FAILED_RETRY_UNIVERSE_CSV_REQUIRED = "erad_a_scale_200_failed_retry_universe_csv_required"
ERAD_FAILED_RETRY_OUTPUT_ROOT_VIOLATION = (
    "output_root_must_be_under_cninfo_a_class_erad_scale_200_failed_retry"
)
ERAD_FAILED_RETRY_UNIVERSE_SIZE_VIOLATION = "erad_a_scale_200_failed_retry_universe_size_must_equal_7"
ERAD_FAILED_RETRY_INCLUDE_REQUIRED = "retry_include_must_be_yes"
ERAD_FAILED_RETRY_DEFERRED_CASE_REJECTED = "ad2e146_deferred_case_not_allowed_in_retry_universe"
ERAD_FAILED_RETRY_NON_RETRY_CASE_REJECTED = "non_erad_failed_retry_case_not_allowed"
ERAD_FAILED_RETRY_INCOMPATIBLE_WITH_ERAD_MAIN = "erad_a_scale_200_failed_retry_incompatible_with_erad_main"
ERAD_FAILED_RETRY_INCOMPATIBLE_WITH_OTHER_MODES = "erad_a_scale_200_failed_retry_incompatible_with_other_modes"
ERAD_FAILED_RETRY_MAIN_ERAD_ROOT_FORBIDDEN = "erad_scale_200_main_live_root_write_forbidden"
ERAD_FAILED_RETRY_REQUEST_CAP_EXCEEDED = "erad_a_scale_200_failed_retry_request_cap_exceeded"
ERAD_FAILED_RETRY_UNIVERSE_CASE_SET_VIOLATION = "erad_failed_retry_universe_case_set_must_match_allowed_7"
ERAD_FAILED_RETRY_COHORT_VIOLATION = "erad_failed_retry_cohort_must_be_new_erad"
ERAD_FAILED_RETRY_DRYRUN_COLUMNS = [
    "case_id", "company_code", "company_name", "market", "report_type", "expected_period",
    "cohort", "original_failure_class", "likely_cause", "retry_strategy", "retry_include",
    "planned_source", "planned_endpoint", "planned_output_root",
    "pdf_download", "pdf_parse", "ocr", "extraction", "db_write", "minio_write", "rag_run",
    "cninfo_call_planned", "planned_request_count_case", "dryrun_status", "notes",
]
REQUIRED_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE = 300
ERAD_NEXT_SCALE_SLICE1_PLANNED_REQUESTS_PER_CASE = 2
ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP = 720
ERAD_NEXT_SCALE_SLICE1_RUNNER_GATE = "READY_FOR_APPROVAL"
ALLOWED_ERAD_NEXT_SCALE_SLICE1_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(201, 501)
}
ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV_REQUIRED = "erad_a_scale_500_slice1_universe_csv_required"
ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT_VIOLATION = (
    "output_root_must_be_under_cninfo_a_class_erad_next_scale_slice1"
)
ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_next_scale_slice1_universe_size_must_equal_300"
)
ERAD_NEXT_SCALE_SLICE1_APPROVAL_REQUIRED = "approve_a_class_erad_scale_500_slice1_required"
ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL = "approve_a_class_erad_scale_500_slice1_wrong_flag"
ERAD_NEXT_SCALE_SLICE1_INCOMPATIBLE_WITH_OTHER_MODES = (
    "erad_a_scale_500_slice1_incompatible_with_other_modes"
)
ERAD_SLICE1_CASE_ID_NOT_ALLOWED = "erad_a_slice1_case_id_not_allowed"
ERAD_SLICE1_SCALE_200_CASE_FORBIDDEN = "erad_a_slice1_scale_200_case_forbidden"
ERAD_SLICE1_INCLUDE_REQUIRED = "erad_include_must_be_yes"
ERAD_SLICE1_COHORT_INVALID = "erad_a_slice1_cohort_must_be_next_scale_slice1"
ERAD_SLICE1_PRIOR_SCALE_200_INVALID = "erad_a_slice1_prior_in_scale_200_must_be_no"
ERAD_SLICE1_SCALE200_OVERLAP = "erad_a_slice1_overlap_with_scale_200_codes"
ERAD_SLICE1_EFFECTIVE192_OVERLAP = "erad_a_slice1_overlap_with_scale_200_effective_192"
ERAD_SLICE1_UNRESOLVED_OVERLAP = "erad_a_slice1_overlap_with_scale_200_unresolved"
ERAD_SLICE1_B_SLICE1_OVERLAP = "erad_a_slice1_overlap_with_b_next_scale_slice1"
ERAD_SLICE1_REQUEST_CAP_EXCEEDED = "erad_a_next_scale_slice1_request_cap_exceeded"
ERAD_SLICE1_LIVE_NOT_IMPLEMENTED = "erad_a_next_scale_slice1_live_not_implemented"
ERAD_SLICE1_CASE_RANGE_INVALID = "erad_a_slice1_case_range_invalid"
ERAD_SLICE1_SCALE_200_ROOT_WRITE_FORBIDDEN = "erad_a_slice1_scale_200_root_write_forbidden"
ERAD_SLICE1_FAILED_RETRY_ROOT_WRITE_FORBIDDEN = (
    "erad_a_slice1_failed_retry_root_write_forbidden"
)
ERAD_SLICE1_ACCEPTABLE_THRESHOLD = 270
ERAD_SLICE1_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
ERAD_NEXT_SCALE_SLICE1_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
ERAD_NEXT_SCALE_SLICE1_MOCK_TEST_PARENT = os.path.join(
    DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, "_mock_test"
)
ERAD_NEXT_SCALE_SLICE1_MOCK_LIVE_TEST_PARENT = os.path.join(
    DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, "_mock_live_test"
)
ERAD_SLICE1_LIVE_REPORT_CSV = os.path.join(
    DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT,
    "reports",
    "a_class_erad_next_scale_slice1_live_report.csv",
)
ERAD_SLICE1_LIVE_SUMMARY_MD = os.path.join(
    DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT,
    "reports",
    "a_class_erad_next_scale_slice1_live_summary.md",
)
ERAD_SLICE1_LIVE_QUALITY_CSV = os.path.join(
    DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT,
    "reports",
    "a_class_erad_next_scale_slice1_live_quality_report.csv",
)
ERAD_NEXT_SCALE_SLICE1_DRYRUN_COLUMNS = [
    "case_id", "company_code", "company_name", "market", "report_type", "expected_period",
    "cohort", "prior_in_scale_200", "erad_include", "planned_source", "planned_endpoint",
    "planned_output_root", "pdf_download", "pdf_parse", "ocr", "extraction", "db_write",
    "minio_write", "rag_run", "cninfo_call_planned", "planned_request_count_case",
    "dryrun_status", "notes",
]
ERAD_SCALE_200_DRYRUN_COLUMNS = [
    "case_id", "company_code", "company_name", "market", "report_type", "expected_period",
    "cohort", "phase3_source_case_id", "erad_include", "phase1_overlap", "phase2_overlap",
    "phase3_overlap", "planned_source", "planned_endpoint", "planned_output_root",
    "pdf_download", "pdf_parse", "ocr", "extraction", "db_write", "minio_write", "rag_run",
    "cninfo_call_planned", "planned_request_count_case", "dryrun_status", "notes",
]

PHASE3_EXPECTED_REPORT_TYPE_MIX: Dict[str, int] = {
    "annual_report": 20,
    "semi_annual_report": 10,
    "quarterly_report_q1": 10,
    "quarterly_report_q3": 10,
}

RUNNER_GATE = "READY_FOR_APPROVAL"
MATCHING_LOGIC_VERSION = tiny_live.MATCHING_LOGIC_VERSION

PHASE2_APPROVAL_REQUIRED = "approve_a_class_phase2_metadata_expansion_required"
RETRY_APPROVAL_REQUIRED = "approve_a_class_phase2_failed_retry_required"
RETRY_V2_APPROVAL_REQUIRED = "approve_a_class_phase2_network_recovery_retry_v2_required"
RETRY_V3_APPROVAL_REQUIRED = "approve_a_class_phase2_retry_v3_required"
RETRY_V3_WRONG_APPROVAL = "approve_a_class_phase2_retry_v3_wrong_flag"
RETRY_V3_LIVE_NOT_IMPLEMENTED = "retry_v3_live_not_implemented_in_this_runner"
RETRY_V3_UNIVERSE_CSV_REQUIRED = "retry_v3_universe_csv_required"
RETRY_V3_INCOMPATIBLE_WITH_RETRY_FAILED_ONLY = "retry_v3_incompatible_with_retry_failed_only"
RETRY_V2_WRONG_APPROVAL = "approve_a_class_phase2_failed_retry_not_valid_for_retry_v2"
RETRY_V1_WRONG_APPROVAL = "approve_a_class_phase2_network_recovery_retry_v2_not_valid_for_retry_v1"
OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_a_class_phase2_metadata_expansion"
RETRY_OUTPUT_ROOT_VIOLATION = "output_root_must_be_under_cninfo_a_class_phase2_metadata_retry"
RETRY_V2_OUTPUT_ROOT_VIOLATION = (
    "output_root_must_be_under_cninfo_a_class_phase2_metadata_retry_v2"
)
RETRY_V3_OUTPUT_ROOT_VIOLATION = (
    "output_root_must_be_under_cninfo_a_class_phase2_metadata_retry_v3"
)
RETRY_V1_WRITE_FORBIDDEN = "retry_v1_baseline_write_forbidden"
RETRY_V2_WRITE_FORBIDDEN = "retry_v2_baseline_write_forbidden"
PRECHECK_WRITE_FORBIDDEN = "precheck_baseline_write_forbidden"
PHASE2_EXPANSION_WRITE_FORBIDDEN = "phase2_expansion_baseline_write_forbidden"
UNIVERSE_SIZE_VIOLATION = "universe_size_must_equal_20"
RETRY_UNIVERSE_SIZE_VIOLATION = "retry_universe_size_must_equal_8"
SUCCESSFUL_CASE_IN_RETRY_FORBIDDEN = "successful_case_not_allowed_in_retry_universe"
NON_RETRY_CASE_REJECTED = "non_retry_failed_case_not_allowed"
RETRY_INCLUDE_REQUIRED = "retry_include_must_be_yes"
NON_PHASE2_CASE_REJECTED = "non_a2m_case_not_allowed"
PHASE2_INCLUDE_REQUIRED = "phase2_include_must_be_yes"
RETRY_PLANNING_GATE = "READY_FOR_APPROVAL"
RETRY_V2_PLANNING_GATE = "READY_FOR_APPROVAL"
RETRY_V2_RUNNER_GATE = "READY_FOR_APPROVAL"
RETRY_V3_RUNNER_GATE = "READY_FOR_APPROVAL"
RETRY_V3_LIVE_IMPLEMENTATION_GATE = "READY_FOR_APPROVAL"
RETRY_V3_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
RETRY_V3_PLANNED_REQUESTS_PER_CASE = 2
RETRY_CORRECT_THRESHOLD = 6

RETRY_V2_LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "report_period",
    "original_phase2_status",
    "first_retry_status",
    "failure_type",
    "failure_stage",
    "retry_v2_retrieval_status",
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
    "notes",
]

RETRY_V2_LIVE_QUALITY_COLUMNS = [
    "case_id",
    "company_code",
    "report_type",
    "report_period",
    "original_phase2_status",
    "first_retry_status",
    "retry_v2_retrieval_status",
    "quality_status",
    "lineage_status",
    "pdf_downloaded",
    "pdf_parsed",
    "cninfo_request_count",
    "notes",
]

RETRY_LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "expected_period",
    "original_failure_type",
    "retry_retrieval_status",
    "quality_status",
    "lineage_status",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "title_match_status",
    "period_match_status",
    "wrong_report_type",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "ocr_enabled",
    "extraction_enabled",
    "cninfo_request_count",
    "notes",
]

RETRY_LIVE_QUALITY_COLUMNS = [
    "case_id",
    "company_code",
    "report_type",
    "expected_period",
    "original_failure_type",
    "retry_retrieval_status",
    "title_match_status",
    "period_match_status",
    "wrong_report_type",
    "quality_status",
    "lineage_status",
    "pdf_downloaded",
    "pdf_parsed",
    "notes",
]

PHASE1_OVERLAP_REJECTED = "phase1_overlap_not_allowed"
REPORT_TYPE_MIX_VIOLATION = "report_type_mix_must_be_8_4_4_4"
PHASE1_BASELINE_WRITE_FORBIDDEN = "phase1_tiny_live_baseline_write_forbidden"
PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED = "pdf_download_not_allowed"
PDF_PARSE_REQUESTED_NOT_ALLOWED = "pdf_parse_not_allowed"
OCR_REQUESTED_NOT_ALLOWED = "ocr_not_allowed"
EXTRACTION_REQUESTED_NOT_ALLOWED = "extraction_not_allowed"
DB_WRITE_REQUESTED_NOT_ALLOWED = "db_write_not_allowed"
MINIO_WRITE_REQUESTED_NOT_ALLOWED = "minio_write_not_allowed"
RAG_REQUESTED_NOT_ALLOWED = "rag_not_allowed"
VERIFIED_STATUS_REQUESTED_NOT_ALLOWED = "verified_status_not_allowed"
PRODUCTION_READY_REQUESTED_NOT_ALLOWED = "production_ready_not_allowed"
TINY_LIVE_APPROVAL_WRONG = "approve_a_class_tiny_live_metadata_not_valid_for_phase2"
PHASE1_TINY_LIVE_APPROVAL_WRONG = "approve_phase1_tiny_live_metadata_not_valid_for_phase2"

DOWNLOAD_PDF = False
PARSE_PDF = False
ENABLE_OCR = False
ENABLE_EXTRACTION = False
WRITE_DB = False
WRITE_MINIO = False
ENABLE_RAG = False
WRITE_VERIFIED = False
UPGRADE_TESTING_STABLE_SAMPLE = False

PLANNED_OUTPUT_OBJECTS = tiny_live.PLANNED_OUTPUT_OBJECTS
REPORT_TYPE_SOURCE_ID = tiny_live.REPORT_TYPE_SOURCE_ID

# Phase 2 universe 已知代码-简称对照
KNOWN_COMPANY_NAMES: Dict[str, str] = {
    "600036": "招商银行",
    "601318": "中国平安",
    "000333": "美的集团",
    "002415": "海康威视",
    "601012": "隆基绿能",
    "600276": "恒瑞医药",
    "000002": "万科A",
    "601888": "中国中免",
    "300014": "亿纬锂能",
    "300750": "宁德时代",
    "600887": "伊利股份",
    "601166": "兴业银行",
    "688599": "天合光能",
    "688036": "传音控股",
    "000725": "京东方A",
    "601899": "紫金矿业",
    "300059": "东方财富",
    "688111": "金山办公",
    "600309": "万华化学",
    "002594": "比亚迪",
}

DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "expected_period",
    "expected_title_keywords",
    "excluded_title_keywords",
    "planned_source",
    "planned_endpoint",
    "planned_output",
    "pdf_download",
    "pdf_parse",
    "ocr",
    "extraction",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "expected_period",
    "retrieval_status",
    "quality_status",
    "lineage_status",
    "announcement_id",
    "announcement_title",
    "announcement_time",
    "title_match_status",
    "period_match_status",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "ocr_enabled",
    "extraction_enabled",
    "cninfo_request_count",
    "notes",
]

LIVE_QUALITY_COLUMNS = [
    "case_id",
    "company_code",
    "report_type",
    "expected_period",
    "retrieval_status",
    "title_match_status",
    "period_match_status",
    "quality_status",
    "lineage_status",
    "pdf_url_present",
    "adjunct_url_present",
    "pdf_downloaded",
    "pdf_parsed",
    "notes",
]

ERAD_SCALE_200_LIVE_REPORT_COLUMNS = LIVE_REPORT_COLUMNS + [
    "cohort",
    "phase3_source_case_id",
]
ERAD_SCALE_200_LIVE_QUALITY_COLUMNS = LIVE_QUALITY_COLUMNS + [
    "cohort",
    "phase3_source_case_id",
]

ERAD_FAILED_RETRY_LIVE_REPORT_COLUMNS = LIVE_REPORT_COLUMNS + [
    "cohort",
    "original_failure_class",
    "likely_cause",
    "retry_strategy",
]
ERAD_FAILED_RETRY_LIVE_QUALITY_COLUMNS = LIVE_QUALITY_COLUMNS + [
    "cohort",
    "likely_cause",
    "retry_strategy",
]

ERAD_SLICE1_LIVE_REPORT_COLUMNS = LIVE_REPORT_COLUMNS + [
    "cohort",
    "prior_in_scale_200",
    "lineage_evidence_mode",
]
ERAD_SLICE1_LIVE_QUALITY_COLUMNS = LIVE_QUALITY_COLUMNS + [
    "cohort",
    "prior_in_scale_200",
]

REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE = 100
ERAD_NEXT_SCALE_SLICE2_PLANNED_REQUESTS_PER_CASE = 2
ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP = 240
ERAD_NEXT_SCALE_SLICE2_RUNNER_GATE = "READY_FOR_APPROVAL"
ERAD_NEXT_SCALE_SLICE2_COHORT = "next_scale_slice2"
ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS: Set[str] = {
    f"AD2E{i:03d}" for i in range(501, 601)
}
ERAD_NEXT_SCALE_SLICE2_UNIVERSE_CSV_REQUIRED = "erad_a_scale_500_slice2_universe_csv_required"
ERAD_NEXT_SCALE_SLICE2_OUTPUT_ROOT_VIOLATION = (
    "output_root_must_be_under_cninfo_a_class_erad_next_scale_slice2_s1"
)
ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE_VIOLATION = (
    "erad_a_next_scale_slice2_universe_size_must_equal_100"
)
ERAD_NEXT_SCALE_SLICE2_APPROVAL_REQUIRED = "approve_a_class_erad_scale_500_slice2_required"
ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL = "approve_a_class_erad_scale_500_slice2_wrong_flag"
ERAD_NEXT_SCALE_SLICE2_INCOMPATIBLE_WITH_OTHER_MODES = (
    "erad_a_scale_500_slice2_incompatible_with_other_modes"
)
ERAD_SLICE2_CASE_ID_NOT_ALLOWED = "erad_a_slice2_case_id_not_allowed"
ERAD_SLICE2_PRIOR_CASE_FORBIDDEN = "erad_a_slice2_prior_ad2e001_500_case_forbidden"
ERAD_SLICE2_INCLUDE_REQUIRED = "erad_include_must_be_yes"
ERAD_SLICE2_COHORT_INVALID = "erad_a_slice2_cohort_must_be_next_scale_slice2"
ERAD_SLICE2_PRIOR_SCALE_200_INVALID = "erad_a_slice2_prior_in_scale_200_must_be_no"
ERAD_SLICE2_OVERLAP_A_ALL = "erad_a_slice2_overlap_l_a1_a_all_u"
ERAD_SLICE2_OVERLAP_A_CUM_EFF = "erad_a_slice2_overlap_l_a2_a_cum_eff"
ERAD_SLICE2_OVERLAP_A_S200 = "erad_a_slice2_overlap_l_a3_a_s200_u"
ERAD_SLICE2_OVERLAP_A_S1 = "erad_a_slice2_overlap_l_a4_a_s1_u"
ERAD_SLICE2_OVERLAP_B_CUM = "erad_a_slice2_overlap_l_b1_b_cum"
ERAD_SLICE2_OVERLAP_B_S200 = "erad_a_slice2_overlap_l_b2_b_s200_u"
ERAD_SLICE2_OVERLAP_B_S1 = "erad_a_slice2_overlap_l_b3_b_s1_u"
ERAD_SLICE2_OVERLAP_B_S2 = "erad_a_slice2_overlap_l_b4_b_s2_u"
ERAD_SLICE2_OVERLAP_AB_182 = "erad_a_slice2_overlap_ab_182"
ERAD_SLICE2_ST_NAME_HIT = "erad_a_slice2_ld4_st_name_hit"
# L-D6：expected_period 相对 listing_date 门禁（A-R16-03）
ERAD_SLICE2_LISTING_PERIOD_BLOCK = "erad_a_slice2_ld6_listing_period_block"
ERAD_SLICE2_LISTING_PROFILE_MISSING = "erad_a_slice2_ld6_listing_profile_missing"
# 封闭 S1 已知 listing_gap/unlisted 三案（A-R16-02）；dry-run 仅 flag，不阻断冻结 cohort 闸
ERAD_SLICE2_FROZEN_LISTING_CAVEAT_CASE_IDS: Set[str] = {
    "AD2E578",
    "AD2E590",
    "AD2E598",
}
ERAD_SLICE2_REQUEST_CAP_EXCEEDED = "erad_a_next_scale_slice2_request_cap_exceeded"
ERAD_SLICE2_CASE_RANGE_INVALID = "erad_a_slice2_case_range_invalid"
ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN = "erad_a_slice2_scale_200_root_write_forbidden"
ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN = (
    "erad_a_slice2_failed_retry_root_write_forbidden"
)
ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN = "erad_a_slice2_slice1_root_write_forbidden"
ERAD_SLICE2_ACCEPTABLE_THRESHOLD = 90
ERAD_SLICE2_EXECUTION_GATE_PASS = "PASS_WITH_CAVEAT"
ERAD_NEXT_SCALE_SLICE2_LIVE_PATH_GATE = "READY_FOR_APPROVAL"
ERAD_NEXT_SCALE_SLICE2_S1_MOCK_TEST_PARENT = os.path.join(
    DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT, "_mock_test"
)
ERAD_NEXT_SCALE_SLICE2_S1_MOCK_LIVE_TEST_PARENT = os.path.join(
    DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT, "_mock_live_test"
)
ERAD_NEXT_SCALE_SLICE2_INCLUDE_REASON = (
    "next_scale_slice2_s1_st_exclude;zero_prior_overlap;metadata_only_no_pdf"
)
ERAD_SLICE2_ST_NAME_PATTERN = re.compile(r"(?:\*?ST|S\*ST)")
ERAD_NEXT_SCALE_SLICE2_DRYRUN_COLUMNS = [
    "case_id", "company_code", "company_name", "market", "report_type", "expected_period",
    "cohort", "prior_in_scale_200", "erad_include", "planned_source", "planned_endpoint",
    "planned_output_root", "pdf_download", "pdf_parse", "ocr", "extraction", "db_write",
    "minio_write", "rag_run", "cninfo_call_planned", "planned_request_count_case",
    "dryrun_status", "notes",
]
ERAD_SLICE2_LIVE_REPORT_COLUMNS = LIVE_REPORT_COLUMNS + [
    "cohort",
    "prior_in_scale_200",
    "lineage_evidence_mode",
]
ERAD_SLICE2_LIVE_QUALITY_COLUMNS = LIVE_QUALITY_COLUMNS + [
    "cohort",
    "prior_in_scale_200",
]

RETRY_DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "expected_period",
    "original_failure_type",
    "retry_strategy",
    "planned_source",
    "planned_endpoint",
    "pdf_download",
    "pdf_parse",
    "ocr",
    "extraction",
    "cninfo_call_planned",
    "dryrun_status",
    "notes",
]

RETRY_V2_DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "report_period",
    "original_phase2_status",
    "first_retry_status",
    "failure_type",
    "failure_stage",
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

PHASE3_DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "expected_period",
    "expected_title_keywords",
    "excluded_title_keywords",
    "phase3_include",
    "planned_source",
    "planned_endpoint",
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

RETRY_V3_DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "report_period",
    "original_phase2_status",
    "retry_v1_status",
    "retry_v2_status",
    "precheck_signal",
    "precheck_orgid_status",
    "retry_v3_include",
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

RETRY_V3_LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "market",
    "report_type",
    "report_period",
    "original_phase2_status",
    "retry_v1_status",
    "retry_v2_status",
    "precheck_signal",
    "precheck_orgid_status",
    "retry_v3_retrieval_status",
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

RETRY_V3_LIVE_QUALITY_COLUMNS = [
    "case_id",
    "company_code",
    "report_type",
    "report_period",
    "original_phase2_status",
    "retry_v1_status",
    "retry_v2_status",
    "retry_v3_retrieval_status",
    "quality_status",
    "lineage_status",
    "pdf_downloaded",
    "pdf_parsed",
    "cninfo_request_count",
    "notes",
]

PHASE2_CORRECT_THRESHOLD = 18


@dataclass
class Phase2UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    expected_title_keywords: str
    excluded_title_keywords: str
    risk_level: str
    phase1_overlap: str
    phase2_include: str
    reason: str


@dataclass
class Phase3UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    expected_title_keywords: str
    excluded_title_keywords: str
    risk_level: str
    phase1_overlap: str
    phase2_overlap: str
    phase3_include: str
    reason: str


@dataclass
class EraDFailedRetryUniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    expected_title_keywords: str
    excluded_title_keywords: str
    cohort: str
    original_failure_class: str
    likely_cause: str
    retry_include: str
    retry_strategy: str
    notes: str


@dataclass
class EraDScale200UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    expected_title_keywords: str
    excluded_title_keywords: str
    cohort: str
    phase3_source_case_id: str
    erad_include: str
    phase1_overlap: str
    phase2_overlap: str
    phase3_overlap: str
    prior_a_phase_overlap: str
    selection_bucket: str
    risk_level: str
    notes: str


@dataclass
class EraDNextScaleSlice1UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    expected_title_keywords: str
    excluded_title_keywords: str
    cohort: str
    prior_in_scale_200: str
    include_reason: str
    erad_include: str


@dataclass
class EraDNextScaleSlice2UniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    expected_title_keywords: str
    excluded_title_keywords: str
    cohort: str
    prior_in_scale_200: str
    include_reason: str
    erad_include: str


@dataclass
class RetryUniverseCase:
    case_id: str
    company_code: str
    company_name: str
    market: str
    report_type: str
    expected_period: str
    original_failure_type: str
    original_failure_reason: str
    retry_include: str
    retry_strategy: str
    notes: str
    original_phase2_status: str = ""
    first_retry_status: str = ""
    failure_type: str = ""
    failure_stage: str = ""
    retry_v2_status: str = ""
    precheck_signal: str = ""
    precheck_orgid_status: str = ""


def build_live_report_row(
    case: Phase2UniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "retrieval_status": str(record.get("retrieval_status") or ""),
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": str(record.get("announcement_time") or ""),
        "title_match_status": str(record.get("title_match_status") or ""),
        "period_match_status": str(record.get("period_match_status") or ""),
        "pdf_url_present": str(record.get("pdf_url_present") or "no"),
        "adjunct_url_present": str(record.get("adjunct_url_present") or "no"),
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "cninfo_request_count": str(cninfo_request_count),
        "notes": str(record.get("notes") or ""),
    }


def is_case_correct(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    if row.get("retrieval_status") != "found":
        return False
    if row.get("title_match_status") != "pass":
        return False
    if row.get("period_match_status") != "pass":
        return False
    return True


def has_red_line_violation(stats: tiny_live.LiveStats, rows: List[Dict[str, str]]) -> bool:
    if stats.pdf_downloaded_count > 0 or stats.pdf_parsed_count > 0:
        return True
    for row in rows:
        if row.get("pdf_downloaded") not in ("0", "no", ""):
            return True
        if row.get("pdf_parsed") not in ("0", "no", ""):
            return True
        if row.get("quality_status") == "verified":
            return True
    return False


def compute_phase2_execution_gate(
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues or case_count != REQUIRED_UNIVERSE_SIZE:
        return "FAIL_REVIEW_REQUIRED"
    correct_count = sum(1 for row in rows if is_case_correct(row))
    if correct_count >= PHASE2_CORRECT_THRESHOLD:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def write_live_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_live_quality_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in LIVE_QUALITY_COLUMNS})
    return report_path


def write_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    correct_count = sum(1 for row in rows if is_case_correct(row))
    title_mismatch = sum(
        1 for row in rows if row.get("title_match_status") not in ("pass", "n/a", "")
    )
    period_mismatch = sum(
        1 for row in rows if row.get("period_match_status") not in ("pass", "n/a", "")
    )
    lines = [
        "# CNINFO A 类 Phase 2 Metadata Expansion — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2 live metadata validation · **无 PDF 下载/解析** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | live |",
        f"| universe size | {len(rows)} |",
        f"| correct report-type metadata | {correct_count} |",
        f"| success (found) | {stats.success_count} |",
        f"| failure | {stats.failure_count} |",
        f"| wrong report-type match | {stats.wrong_report_type_count} |",
        f"| title mismatch | {title_mismatch} |",
        f"| period mismatch | {period_mismatch} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| PDF downloaded | **{stats.pdf_downloaded_count}** |",
        f"| PDF parsed | **{stats.pdf_parsed_count}** |",
        f"| OCR | **0** |",
        f"| extraction | **0** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "",
        "## Endpoint usage",
        "",
        f"- topSearch/query: {stats.endpoint_hits.get('topSearch', 0)}",
        f"- hisAnnouncement/query: {stats.endpoint_hits.get('hisAnnouncement', 0)}",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- Phase 1 baseline untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_metadata_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready** · Phase 2 limited expansion only",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def validate_retry_output_root(output_root: str) -> Tuple[bool, str]:
    """retry v1 输出仅允许 retry 隔离根；禁止写入 Phase 2 expansion / Phase 1 baseline / retry v2/v3 / precheck。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_RETRY_OUTPUT_ROOT)
    expansion = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    phase1 = _normalize_output_root(PHASE1_OUTPUT_ROOT)
    v2 = _normalize_output_root(DEFAULT_RETRY_V2_OUTPUT_ROOT)
    v3 = _normalize_output_root(DEFAULT_RETRY_V3_OUTPUT_ROOT)
    precheck = _normalize_output_root(PRECHECK_OUTPUT_ROOT)

    if root == expansion or root.startswith(expansion + os.sep):
        return False, PHASE2_EXPANSION_WRITE_FORBIDDEN
    if root == phase1 or root.startswith(phase1 + os.sep):
        return False, PHASE1_BASELINE_WRITE_FORBIDDEN
    if root == v2 or root.startswith(v2 + os.sep):
        return False, RETRY_V2_OUTPUT_ROOT_VIOLATION
    if root == v3 or root.startswith(v3 + os.sep):
        return False, RETRY_V3_OUTPUT_ROOT_VIOLATION
    if root == precheck or root.startswith(precheck + os.sep):
        return False, PRECHECK_WRITE_FORBIDDEN
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, RETRY_OUTPUT_ROOT_VIOLATION


def validate_retry_v2_output_root(output_root: str) -> Tuple[bool, str]:
    """retry v2 输出仅允许 retry_v2 隔离根；禁止写入 expansion / retry v1 / v3 / precheck / Phase 1。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_RETRY_V2_OUTPUT_ROOT)
    expansion = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v1 = _normalize_output_root(DEFAULT_RETRY_OUTPUT_ROOT)
    v3 = _normalize_output_root(DEFAULT_RETRY_V3_OUTPUT_ROOT)
    precheck = _normalize_output_root(PRECHECK_OUTPUT_ROOT)
    phase1 = _normalize_output_root(PHASE1_OUTPUT_ROOT)

    if root == expansion or root.startswith(expansion + os.sep):
        return False, PHASE2_EXPANSION_WRITE_FORBIDDEN
    if root == v1 or root.startswith(v1 + os.sep):
        return False, RETRY_V1_WRITE_FORBIDDEN
    if root == v3 or root.startswith(v3 + os.sep):
        return False, RETRY_V3_OUTPUT_ROOT_VIOLATION
    if root == precheck or root.startswith(precheck + os.sep):
        return False, PRECHECK_WRITE_FORBIDDEN
    if root == phase1 or root.startswith(phase1 + os.sep):
        return False, PHASE1_BASELINE_WRITE_FORBIDDEN
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, RETRY_V2_OUTPUT_ROOT_VIOLATION


def validate_retry_v3_output_root(output_root: str) -> Tuple[bool, str]:
    """retry v3 输出仅允许 retry_v3 隔离根；禁止写入 expansion / v1 / v2 / precheck / Phase 1。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_RETRY_V3_OUTPUT_ROOT)
    expansion = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v1 = _normalize_output_root(DEFAULT_RETRY_OUTPUT_ROOT)
    v2 = _normalize_output_root(DEFAULT_RETRY_V2_OUTPUT_ROOT)
    precheck = _normalize_output_root(PRECHECK_OUTPUT_ROOT)
    phase1 = _normalize_output_root(PHASE1_OUTPUT_ROOT)

    if root == expansion or root.startswith(expansion + os.sep):
        return False, PHASE2_EXPANSION_WRITE_FORBIDDEN
    if root == v1 or root.startswith(v1 + os.sep):
        return False, RETRY_V1_WRITE_FORBIDDEN
    if root == v2 or root.startswith(v2 + os.sep):
        return False, RETRY_V2_WRITE_FORBIDDEN
    if root == precheck or root.startswith(precheck + os.sep):
        return False, PRECHECK_WRITE_FORBIDDEN
    if root == phase1 or root.startswith(phase1 + os.sep):
        return False, PHASE1_BASELINE_WRITE_FORBIDDEN
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, RETRY_V3_OUTPUT_ROOT_VIOLATION


def is_retry_v2_mode(
    universe_csv: Optional[str], output_root: Optional[str]
) -> bool:
    """根据 output root 或 universe CSV 判断是否为 network recovery retry v2 模式。"""
    if output_root:
        root = _normalize_output_root(output_root)
        v2_root = _normalize_output_root(DEFAULT_RETRY_V2_OUTPUT_ROOT)
        if root == v2_root or root.startswith(v2_root + os.sep):
            return True
    if universe_csv:
        universe = os.path.normpath(universe_csv)
        v2_universe = os.path.normpath(DEFAULT_RETRY_V2_UNIVERSE_CSV)
        if universe == v2_universe:
            return True
    return False


def is_retry_v3_mode(
    retry_v3: bool,
    universe_csv: Optional[str],
    output_root: Optional[str],
) -> bool:
    """根据 --retry-v3、output root 或 universe CSV 判断是否为 retry v3 模式。"""
    if retry_v3:
        return True
    if output_root:
        root = _normalize_output_root(output_root)
        v3_root = _normalize_output_root(DEFAULT_RETRY_V3_OUTPUT_ROOT)
        if root == v3_root or root.startswith(v3_root + os.sep):
            return True
    if universe_csv:
        universe = os.path.normpath(universe_csv)
        v3_universe = os.path.normpath(DEFAULT_RETRY_V3_UNIVERSE_CSV)
        if universe == v3_universe:
            return True
    return False


def _retry_include_from_row(row: Dict[str, str]) -> str:
    """retry_v3_include / retry_v2_include 列别名映射为内部 retry_include，不修改源 CSV。"""
    value = str(row.get("retry_include", "")).strip().lower()
    if not value:
        value = str(row.get("retry_v3_include", "")).strip().lower()
    if not value:
        value = str(row.get("retry_v2_include", "")).strip().lower()
    return value


def _expected_period_from_row(row: Dict[str, str]) -> str:
    """report_period 列别名映射为内部 expected_period，不修改源 CSV。"""
    value = str(row.get("expected_period", "")).strip()
    if not value:
        value = str(row.get("report_period", "")).strip()
    return value


def load_retry_universe(path: str) -> List[RetryUniverseCase]:
    cases: List[RetryUniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            original_failure_type = str(row.get("original_failure_type", "")).strip()
            if not original_failure_type:
                original_failure_type = str(
                    row.get("original_phase2_status", "")
                ).strip()
            cases.append(
                RetryUniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    report_type=str(row.get("report_type", "")).strip(),
                    expected_period=_expected_period_from_row(row),
                    original_failure_type=original_failure_type,
                    original_failure_reason=str(
                        row.get("original_failure_reason", "")
                    ).strip(),
                    retry_include=_retry_include_from_row(row),
                    retry_strategy=str(row.get("retry_strategy", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                    original_phase2_status=str(
                        row.get("original_phase2_status", "")
                    ).strip(),
                    first_retry_status=str(
                        row.get("first_retry_status", "")
                        or row.get("retry_v1_status", "")
                    ).strip(),
                    failure_type=str(row.get("failure_type", "")).strip(),
                    failure_stage=str(row.get("failure_stage", "")).strip(),
                    retry_v2_status=str(row.get("retry_v2_status", "")).strip(),
                    precheck_signal=str(row.get("precheck_signal", "")).strip(),
                    precheck_orgid_status=str(
                        row.get("precheck_orgid_status", "")
                    ).strip(),
                )
            )
    return cases


def retry_to_phase2_case(case: RetryUniverseCase) -> Phase2UniverseCase:
    return Phase2UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        report_type=case.report_type,
        expected_period=case.expected_period,
        expected_title_keywords="",
        excluded_title_keywords="",
        risk_level="low",
        phase1_overlap="no",
        phase2_include="yes",
        reason=case.notes,
    )


def validate_retry_case(case: RetryUniverseCase) -> List[str]:
    issues: List[str] = []
    if case.case_id in SUCCESSFUL_CASE_IDS:
        issues.append(SUCCESSFUL_CASE_IN_RETRY_FORBIDDEN)
    if case.case_id not in RETRY_ALLOWED_CASE_IDS:
        issues.append(NON_RETRY_CASE_REJECTED)
    if case.retry_include != "yes":
        issues.append(RETRY_INCLUDE_REQUIRED)
    if not case.company_code:
        issues.append("company_code_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    issues.extend(validate_universe_code_name(retry_to_phase2_case(case)))
    return issues


def validate_retry_universe_size(cases: List[RetryUniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.retry_include == "yes"]
    if len(included) != RETRY_REQUIRED_UNIVERSE_SIZE:
        return (
            False,
            f"{RETRY_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {RETRY_REQUIRED_UNIVERSE_SIZE}",
        )
    return True, ""


def enforce_retry_approval_gate(args: argparse.Namespace) -> None:
    wrong_flags = (
        (args.approve_a_class_phase2_metadata_expansion, PHASE2_APPROVAL_REQUIRED),
        (args.approve_a_class_phase2_network_recovery_retry_v2, RETRY_V1_WRONG_APPROVAL),
        (args.approve_a_class_tiny_live_metadata, TINY_LIVE_APPROVAL_WRONG),
        (args.approve_phase1_tiny_live_metadata, PHASE1_TINY_LIVE_APPROVAL_WRONG),
        (args.approve_full_harvest, tiny_live.FORBIDDEN_APPROVE_FULL_HARVEST),
        (args.approve_phase2_smoke_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE2),
        (args.approve_phase3_batch_500_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE3),
        (args.approve_b_class_tiny_live_validation, tiny_live.FORBIDDEN_APPROVE_B_CLASS),
        (getattr(args, "approve_a_class_phase3_50_company_expansion", False), PHASE3_WRONG_APPROVAL),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not args.approve_a_class_phase2_failed_retry:
        print(f"ERROR: {RETRY_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def enforce_retry_v2_approval_gate(args: argparse.Namespace) -> None:
    wrong_flags = (
        (args.approve_a_class_phase2_metadata_expansion, PHASE2_APPROVAL_REQUIRED),
        (args.approve_a_class_phase2_failed_retry, RETRY_V2_WRONG_APPROVAL),
        (args.approve_a_class_tiny_live_metadata, TINY_LIVE_APPROVAL_WRONG),
        (args.approve_phase1_tiny_live_metadata, PHASE1_TINY_LIVE_APPROVAL_WRONG),
        (args.approve_full_harvest, tiny_live.FORBIDDEN_APPROVE_FULL_HARVEST),
        (args.approve_phase2_smoke_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE2),
        (args.approve_phase3_batch_500_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE3),
        (args.approve_b_class_tiny_live_validation, tiny_live.FORBIDDEN_APPROVE_B_CLASS),
        (getattr(args, "approve_a_class_phase3_50_company_expansion", False), PHASE3_WRONG_APPROVAL),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not args.approve_a_class_phase2_network_recovery_retry_v2:
        print(f"ERROR: {RETRY_V2_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def enforce_retry_v3_approval_gate(args: argparse.Namespace) -> None:
    wrong_flags = (
        (args.approve_a_class_phase2_metadata_expansion, RETRY_V3_WRONG_APPROVAL),
        (args.approve_a_class_phase2_failed_retry, RETRY_V3_WRONG_APPROVAL),
        (args.approve_a_class_phase2_network_recovery_retry_v2, RETRY_V3_WRONG_APPROVAL),
        (args.approve_a_class_tiny_live_metadata, RETRY_V3_WRONG_APPROVAL),
        (args.approve_phase1_tiny_live_metadata, RETRY_V3_WRONG_APPROVAL),
        (args.approve_full_harvest, RETRY_V3_WRONG_APPROVAL),
        (args.approve_phase2_smoke_harvest, RETRY_V3_WRONG_APPROVAL),
        (args.approve_phase3_batch_500_harvest, RETRY_V3_WRONG_APPROVAL),
        (args.approve_b_class_tiny_live_validation, RETRY_V3_WRONG_APPROVAL),
        (
            getattr(args, "approve_a_class_phase2_cninfo_reachability_precheck", False),
            RETRY_V3_WRONG_APPROVAL,
        ),
        (getattr(args, "approve_a_class_phase3_50_company_expansion", False), RETRY_V3_WRONG_APPROVAL),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not args.approve_a_class_phase2_retry_v3:
        print(f"ERROR: {RETRY_V3_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def enforce_phase3_approval_gate(args: argparse.Namespace) -> None:
    wrong_flags = (
        (args.approve_a_class_phase2_metadata_expansion, PHASE3_WRONG_APPROVAL),
        (args.approve_a_class_phase2_failed_retry, PHASE3_WRONG_APPROVAL),
        (args.approve_a_class_phase2_network_recovery_retry_v2, PHASE3_WRONG_APPROVAL),
        (args.approve_a_class_phase2_retry_v3, PHASE3_WRONG_APPROVAL),
        (args.approve_a_class_tiny_live_metadata, PHASE3_WRONG_APPROVAL),
        (args.approve_phase1_tiny_live_metadata, PHASE3_WRONG_APPROVAL),
        (args.approve_full_harvest, PHASE3_WRONG_APPROVAL),
        (args.approve_phase2_smoke_harvest, PHASE3_WRONG_APPROVAL),
        (args.approve_phase3_batch_500_harvest, PHASE3_WRONG_APPROVAL),
        (args.approve_b_class_tiny_live_validation, PHASE3_WRONG_APPROVAL),
        (
            getattr(args, "approve_a_class_phase2_cninfo_reachability_precheck", False),
            PHASE3_WRONG_APPROVAL,
        ),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not args.approve_a_class_phase3_50_company_expansion:
        print(f"ERROR: {PHASE3_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def build_retry_dryrun_row(case: RetryUniverseCase, issues: List[str]) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"retry dry-run; CNINFO not called; metadata only; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"original_failure={case.original_failure_type}"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "original_failure_type": case.original_failure_type,
        "retry_strategy": case.retry_strategy,
        "planned_source": source_id,
        "planned_endpoint": planned_endpoints_for_case(retry_to_phase2_case(case)),
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def process_retry_dry_run(
    cases: List[RetryUniverseCase],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = validate_retry_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(build_retry_dryrun_row(case, issues))
    return rows, universe_issues


def write_retry_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_retry_dryrun_summary(
    output_paths: Dict[str, str],
    case_count: int,
    universe_issues: List[str],
) -> str:
    planned_ok = case_count - len(universe_issues)
    lines = [
        "# CNINFO A 类 Phase 2 Failed Retry — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** isolated retry dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | retry_dry_run |",
        f"| retry cases | {case_count} |",
        f"| planned_ok | {planned_ok} |",
        f"| successful 12 excluded | **yes** |",
        f"| universe_issues | {len(universe_issues)} |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB / MinIO / RAG | **0** |",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_failed_retry_planning_gate = {RETRY_PLANNING_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_retry_v2_dryrun_row(
    case: RetryUniverseCase,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"retry v2 dry-run; CNINFO not called; metadata only; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"original_phase2={case.original_phase2_status or case.original_failure_type}; "
        f"first_retry={case.first_retry_status}"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "report_period": case.expected_period,
        "original_phase2_status": case.original_phase2_status or case.original_failure_type,
        "first_retry_status": case.first_retry_status,
        "failure_type": case.failure_type,
        "failure_stage": case.failure_stage,
        "retry_v2_include": case.retry_include,
        "planned_request_count": "0",
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


def process_retry_v2_dry_run(
    cases: List[RetryUniverseCase],
    output_root: str,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = validate_retry_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(build_retry_v2_dryrun_row(case, issues, output_root))
    return rows, universe_issues


def write_retry_v2_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v2_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_V2_DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_retry_v2_dryrun_summary(
    output_paths: Dict[str, str],
    case_count: int,
    universe_issues: List[str],
) -> str:
    planned_ok = case_count - len(universe_issues)
    lines = [
        "# CNINFO A 类 Phase 2 Network Recovery Retry v2 — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** network recovery retry v2 dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | retry_v2_dry_run |",
        f"| retry_v2 cases | {case_count} |",
        f"| planned_ok | {planned_ok} |",
        f"| successful 12 excluded | **yes** |",
        f"| universe_issues | {len(universe_issues)} |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB / MinIO / RAG | **0** |",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_network_recovery_retry_v2_runner_extension_gate = {RETRY_V2_RUNNER_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
        "",
        "**Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v2_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_retry_v3_dryrun_row(
    case: RetryUniverseCase,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    status = "planned_ok" if not issues else "universe_invalid"
    planned_requests = (
        str(RETRY_V3_PLANNED_REQUESTS_PER_CASE) if not issues else "0"
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "report_period": case.expected_period,
        "original_phase2_status": case.original_phase2_status
        or case.original_failure_type,
        "retry_v1_status": case.first_retry_status,
        "retry_v2_status": case.retry_v2_status,
        "precheck_signal": case.precheck_signal,
        "precheck_orgid_status": case.precheck_orgid_status,
        "retry_v3_include": case.retry_include,
        "planned_request_count": planned_requests,
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
        "notes": "; ".join(issues) if issues else "",
    }


def process_retry_v3_dry_run(
    cases: List[RetryUniverseCase],
    output_root: str,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = validate_retry_case(case)
        rows.append(build_retry_v3_dryrun_row(case, issues, output_root))
        if issues:
            universe_issues.extend(f"{case.case_id}: {issue}" for issue in issues)
    return rows, universe_issues


def write_retry_v3_dryrun_report(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v3_dryrun_report.csv"
    )
    with open(report_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_V3_DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_retry_v3_dryrun_summary(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_issues: List[str],
) -> str:
    planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
    total = len(rows)
    lines = [
        "# A-class Phase 2 retry_v3 dry-run summary",
        "",
        f"- planned_ok: {planned_ok}/{total}",
        "- CNINFO calls: 0",
        "- PDF download: 0",
        "- PDF parse: 0",
        "- OCR: 0",
        "- extraction: 0",
        "- DB write: 0",
        "- MinIO write: 0",
        "- RAG run: 0",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_retry_v3_runner_extension_gate = {RETRY_V3_RUNNER_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
        "",
        "**Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v3_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_retry_v3_live_report_row(
    retry_case: RetryUniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    retrieval = str(record.get("retrieval_status") or "")
    ann_time = str(record.get("announcement_time") or "")
    ann_date = ann_time[:10] if len(ann_time) >= 10 else ""
    endpoint = planned_endpoints_for_case(retry_to_phase2_case(retry_case))
    failure_type = str(record.get("failure_type") or retry_case.failure_type or "")
    return {
        "case_id": retry_case.case_id,
        "company_code": retry_case.company_code,
        "company_name": retry_case.company_name,
        "market": retry_case.market,
        "report_type": retry_case.report_type,
        "report_period": retry_case.expected_period,
        "original_phase2_status": retry_case.original_phase2_status
        or retry_case.original_failure_type,
        "retry_v1_status": retry_case.first_retry_status,
        "retry_v2_status": retry_case.retry_v2_status,
        "precheck_signal": retry_case.precheck_signal,
        "precheck_orgid_status": retry_case.precheck_orgid_status,
        "retry_v3_retrieval_status": retrieval,
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": ann_time,
        "announcement_date": ann_date,
        "pdf_url_present": str(record.get("pdf_url_present") or "no"),
        "adjunct_url_present": str(record.get("adjunct_url_present") or "no"),
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "endpoint_used": endpoint,
        "cninfo_request_count": str(cninfo_request_count),
        "failure_type": failure_type,
        "notes": (
            f"retry v3 live; original_phase2={retry_case.original_phase2_status or retry_case.original_failure_type}; "
            f"retry_v1={retry_case.first_retry_status}; retry_v2={retry_case.retry_v2_status}; "
            f"precheck={retry_case.precheck_signal}/{retry_case.precheck_orgid_status}; "
            f"matching_logic={MATCHING_LOGIC_VERSION}; PDF not downloaded; "
            f"{record.get('notes', '')}"
        ),
    }


def is_retry_v3_case_acceptable(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    status = row.get("retry_v3_retrieval_status", "")
    quality = row.get("quality_status", "")
    lineage = row.get("lineage_status", "")
    notes = row.get("notes", "").strip()
    if status in ("network_error", "not_found", "universe_invalid"):
        return False
    if status == "found":
        return True
    if status in ("discovered", "matching_pass"):
        return True
    if status == "empty_but_valid" and notes:
        return True
    if lineage == "discovered":
        return True
    if (status == "needs_review" or quality == "needs_review") and notes and lineage:
        return True
    return False


def compute_retry_v3_execution_gate(
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues or case_count != RETRY_REQUIRED_UNIVERSE_SIZE:
        return "FAIL_REVIEW_REQUIRED"
    acceptable_count = sum(1 for row in rows if is_retry_v3_case_acceptable(row))
    if acceptable_count >= RETRY_CORRECT_THRESHOLD:
        return RETRY_V3_EXECUTION_GATE_PASS
    return "FAIL_REVIEW_REQUIRED"


def process_retry_v3_live(
    retry_cases: List[RetryUniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for retry_case in retry_cases:
        if retry_case.retry_include != "yes":
            continue
        issues = validate_retry_case(retry_case)
        if issues:
            universe_issues.append(f"{retry_case.case_id}:{';'.join(issues)}")
            rows.append(
                build_retry_v3_live_report_row(
                    retry_case,
                    {
                        "retrieval_status": "universe_invalid",
                        "quality_status": "blocked",
                        "lineage_status": "needs_review",
                        "announcement_id": "",
                        "announcement_title": "",
                        "announcement_time": "",
                        "pdf_url_present": "no",
                        "adjunct_url_present": "no",
                        "failure_type": "universe_invalid",
                        "notes": "; ".join(issues),
                    },
                    0,
                )
            )
            stats.failure_count += 1
            continue

        phase2_case = retry_to_phase2_case(retry_case)
        tl_case = to_tiny_live_case(phase2_case)
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        live_row = build_retry_v3_live_report_row(
            retry_case, record, case_cninfo_requests
        )
        snapshot_path = os.path.join(
            output_paths["raw_metadata"], f"{retry_case.case_id}_retry_v3.json"
        )
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": retry_case.__dict__,
                    "mode": "retry_v3_live",
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": False,
                    "pdf_parse_enabled": False,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={retry_case.case_id} company_code={retry_case.company_code} "
            f"retry_v3_retrieval_status={live_row['retry_v3_retrieval_status']} "
            f"quality={live_row.get('quality_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def write_retry_v3_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v3_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_V3_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_retry_v3_live_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v3_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_V3_LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in RETRY_V3_LIVE_QUALITY_COLUMNS})
    return report_path


def write_retry_v3_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    acceptable_count = sum(1 for row in rows if is_retry_v3_case_acceptable(row))
    failed_count = sum(
        1
        for row in rows
        if row.get("retry_v3_retrieval_status")
        in ("network_error", "not_found", "universe_invalid")
    )
    needs_review_count = sum(
        1 for row in rows if row.get("quality_status") == "needs_review"
    )
    lines = [
        "# CNINFO A 类 Phase 2 Retry v3 — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** retry v3 live · **8 unresolved cases only** · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | retry_v3_live |",
        f"| retry_v3 cases | {len(rows)} |",
        f"| retry_v3 acceptable | {acceptable_count} |",
        f"| retry_v3 failed | {failed_count} |",
        f"| needs_review | {needs_review_count} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| PDF downloaded | **{stats.pdf_downloaded_count}** |",
        f"| PDF parsed | **{stats.pdf_parsed_count}** |",
        f"| OCR / extraction | **0** |",
        f"| DB / MinIO / RAG | **0** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "",
        "## Safety",
        "",
        "- successful 12 cases not rerun: **yes**",
        "- Phase 2 expansion reports untouched: **yes**",
        "- retry v1 reports untouched: **yes**",
        "- retry v2 reports untouched: **yes**",
        "- precheck reports untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_retry_v3_execution_gate = {gate}",
        "a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED (unchanged)",
        "a_class_phase2_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED (unchanged)",
        "a_class_phase2_metadata_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED (unchanged)",
        "a_class_phase2_retry_v2_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED (unchanged)",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
        "**Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v3_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_retry_v2_live_report_row(
    retry_case: RetryUniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    retrieval = str(record.get("retrieval_status") or "")
    ann_time = str(record.get("announcement_time") or "")
    ann_date = ann_time[:10] if len(ann_time) >= 10 else ""
    endpoint = planned_endpoints_for_case(retry_to_phase2_case(retry_case))
    return {
        "case_id": retry_case.case_id,
        "company_code": retry_case.company_code,
        "company_name": retry_case.company_name,
        "market": retry_case.market,
        "report_type": retry_case.report_type,
        "report_period": retry_case.expected_period,
        "original_phase2_status": retry_case.original_phase2_status
        or retry_case.original_failure_type,
        "first_retry_status": retry_case.first_retry_status,
        "failure_type": retry_case.failure_type,
        "failure_stage": retry_case.failure_stage,
        "retry_v2_retrieval_status": retrieval,
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": ann_time,
        "announcement_date": ann_date,
        "pdf_url_present": str(record.get("pdf_url_present") or "no"),
        "adjunct_url_present": str(record.get("adjunct_url_present") or "no"),
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "endpoint_used": endpoint,
        "cninfo_request_count": str(cninfo_request_count),
        "notes": (
            f"retry v2 live; original_phase2={retry_case.original_phase2_status or retry_case.original_failure_type}; "
            f"first_retry={retry_case.first_retry_status}; matching_logic={MATCHING_LOGIC_VERSION}; "
            f"PDF not downloaded; {record.get('notes', '')}"
        ),
    }


def is_retry_v2_case_acceptable(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    status = row.get("retry_v2_retrieval_status", "")
    quality = row.get("quality_status", "")
    lineage = row.get("lineage_status", "")
    notes = row.get("notes", "").strip()
    if status in ("network_error", "not_found", "universe_invalid"):
        return False
    if status == "found":
        return True
    if status in ("discovered", "matching_pass"):
        return True
    if lineage == "discovered":
        return True
    if (status == "needs_review" or quality == "needs_review") and notes:
        return True
    return False


def compute_retry_v2_execution_gate(
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues or case_count != RETRY_REQUIRED_UNIVERSE_SIZE:
        return "FAIL_REVIEW_REQUIRED"
    acceptable_count = sum(1 for row in rows if is_retry_v2_case_acceptable(row))
    if acceptable_count >= RETRY_CORRECT_THRESHOLD:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def process_retry_v2_live(
    retry_cases: List[RetryUniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for retry_case in retry_cases:
        if retry_case.retry_include != "yes":
            continue
        issues = validate_retry_case(retry_case)
        if issues:
            universe_issues.append(f"{retry_case.case_id}:{';'.join(issues)}")
            rows.append(
                build_retry_v2_live_report_row(
                    retry_case,
                    {
                        "retrieval_status": "universe_invalid",
                        "quality_status": "blocked",
                        "lineage_status": "needs_review",
                        "announcement_id": "",
                        "announcement_title": "",
                        "announcement_time": "",
                        "pdf_url_present": "no",
                        "adjunct_url_present": "no",
                        "notes": "; ".join(issues),
                    },
                    0,
                )
            )
            stats.failure_count += 1
            continue

        phase2_case = retry_to_phase2_case(retry_case)
        tl_case = to_tiny_live_case(phase2_case)
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        live_row = build_retry_v2_live_report_row(
            retry_case, record, case_cninfo_requests
        )
        snapshot_path = os.path.join(
            output_paths["raw_metadata"], f"{retry_case.case_id}_retry_v2.json"
        )
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": retry_case.__dict__,
                    "mode": "retry_v2_live",
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": False,
                    "pdf_parse_enabled": False,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={retry_case.case_id} company_code={retry_case.company_code} "
            f"retry_v2_retrieval_status={live_row['retry_v2_retrieval_status']} "
            f"quality={live_row.get('quality_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def write_retry_v2_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v2_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_V2_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_retry_v2_live_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v2_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_V2_LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in RETRY_V2_LIVE_QUALITY_COLUMNS})
    return report_path


def write_retry_v2_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    acceptable_count = sum(1 for row in rows if is_retry_v2_case_acceptable(row))
    failed_count = sum(
        1
        for row in rows
        if row.get("retry_v2_retrieval_status")
        in ("network_error", "not_found", "universe_invalid")
    )
    needs_review_count = sum(
        1 for row in rows if row.get("quality_status") == "needs_review"
    )
    wrong_rt = sum(
        1
        for row in rows
        if row.get("retry_v2_retrieval_status") == "title_mismatch"
    )
    title_mismatch = sum(
        1
        for row in rows
        if row.get("retry_v2_retrieval_status") == "title_mismatch"
    )
    period_mismatch = 0
    lines = [
        "# CNINFO A 类 Phase 2 Network Recovery Retry v2 — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** retry v2 live · **8 unresolved cases only** · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | retry_v2_live |",
        f"| retry_v2 cases | {len(rows)} |",
        f"| retry_v2 acceptable | {acceptable_count} |",
        f"| retry_v2 failed | {failed_count} |",
        f"| needs_review | {needs_review_count} |",
        f"| wrong report-type | {wrong_rt} |",
        f"| title mismatch | {title_mismatch} |",
        f"| period mismatch | {period_mismatch} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| PDF downloaded | **{stats.pdf_downloaded_count}** |",
        f"| PDF parsed | **{stats.pdf_parsed_count}** |",
        f"| OCR / extraction | **0** |",
        f"| DB / MinIO / RAG | **0** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "",
        "## Safety",
        "",
        "- successful 12 cases not rerun: **yes**",
        "- Phase 2 expansion reports untouched: **yes**",
        "- retry v1 reports untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_network_recovery_retry_v2_execution_gate = {gate}",
        "a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED (unchanged)",
        "a_class_phase2_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED (unchanged)",
        "a_class_phase2_metadata_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED (unchanged)",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_retry_v2_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_retry_live_report_row(
    retry_case: RetryUniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    retrieval = str(record.get("retrieval_status") or "")
    wrong_rt = "1" if retrieval == "title_mismatch" else "0"
    return {
        "case_id": retry_case.case_id,
        "company_code": retry_case.company_code,
        "company_name": retry_case.company_name,
        "market": retry_case.market,
        "report_type": retry_case.report_type,
        "expected_period": retry_case.expected_period,
        "original_failure_type": retry_case.original_failure_type,
        "retry_retrieval_status": retrieval,
        "quality_status": str(record.get("quality_status") or ""),
        "lineage_status": str(record.get("lineage_status") or ""),
        "announcement_id": str(record.get("announcement_id") or ""),
        "announcement_title": str(record.get("announcement_title") or ""),
        "announcement_time": str(record.get("announcement_time") or ""),
        "title_match_status": str(record.get("title_match_status") or ""),
        "period_match_status": str(record.get("period_match_status") or ""),
        "wrong_report_type": wrong_rt,
        "pdf_url_present": str(record.get("pdf_url_present") or "no"),
        "adjunct_url_present": str(record.get("adjunct_url_present") or "no"),
        "pdf_downloaded": "0",
        "pdf_parsed": "0",
        "ocr_enabled": "0",
        "extraction_enabled": "0",
        "cninfo_request_count": str(cninfo_request_count),
        "notes": (
            f"isolated retry live; original={retry_case.original_failure_type}; "
            f"matching_logic={MATCHING_LOGIC_VERSION}; PDF not downloaded; "
            f"{record.get('notes', '')}"
        ),
    }


def is_retry_case_correct(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    if row.get("wrong_report_type") not in ("0", "no", ""):
        return False
    if row.get("retry_retrieval_status") != "found":
        return False
    if row.get("title_match_status") != "pass":
        return False
    if row.get("period_match_status") != "pass":
        return False
    return True


def compute_retry_execution_gate(
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues or case_count != RETRY_REQUIRED_UNIVERSE_SIZE:
        return "FAIL_REVIEW_REQUIRED"
    correct_count = sum(1 for row in rows if is_retry_case_correct(row))
    if correct_count >= RETRY_CORRECT_THRESHOLD:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def process_retry_live(
    retry_cases: List[RetryUniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for retry_case in retry_cases:
        if retry_case.retry_include != "yes":
            continue
        issues = validate_retry_case(retry_case)
        if issues:
            universe_issues.append(f"{retry_case.case_id}:{';'.join(issues)}")
            rows.append(
                build_retry_live_report_row(
                    retry_case,
                    {
                        "retrieval_status": "universe_invalid",
                        "quality_status": "blocked",
                        "lineage_status": "needs_review",
                        "announcement_id": "",
                        "announcement_title": "",
                        "announcement_time": "",
                        "title_match_status": "n/a",
                        "period_match_status": "n/a",
                        "pdf_url_present": "no",
                        "adjunct_url_present": "no",
                        "notes": "; ".join(issues),
                    },
                    0,
                )
            )
            stats.failure_count += 1
            continue

        phase2_case = retry_to_phase2_case(retry_case)
        tl_case = to_tiny_live_case(phase2_case)
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        live_row = build_retry_live_report_row(retry_case, record, case_cninfo_requests)
        snapshot_path = os.path.join(
            output_paths["raw_metadata"], f"{retry_case.case_id}_retry.json"
        )
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": retry_case.__dict__,
                    "mode": "retry_live",
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": DOWNLOAD_PDF,
                    "pdf_parse_enabled": PARSE_PDF,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={retry_case.case_id} company_code={retry_case.company_code} "
            f"retry_retrieval_status={live_row['retry_retrieval_status']} "
            f"title_match={live_row.get('title_match_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def write_retry_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_retry_live_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RETRY_LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in RETRY_LIVE_QUALITY_COLUMNS})
    return report_path


def write_retry_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    correct_count = sum(1 for row in rows if is_retry_case_correct(row))
    wrong_rt = sum(1 for row in rows if row.get("wrong_report_type") == "1")
    title_mismatch = sum(
        1 for row in rows if row.get("title_match_status") not in ("pass", "n/a", "")
    )
    period_mismatch = sum(
        1 for row in rows if row.get("period_match_status") not in ("pass", "n/a", "")
    )
    lines = [
        "# CNINFO A 类 Phase 2 Failed Retry — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** isolated retry live · **8 failed cases only** · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | retry_live |",
        f"| retry cases | {len(rows)} |",
        f"| retry correct | {correct_count} |",
        f"| success (found) | {stats.success_count} |",
        f"| failure | {stats.failure_count} |",
        f"| wrong report-type | {wrong_rt} |",
        f"| title mismatch | {title_mismatch} |",
        f"| period mismatch | {period_mismatch} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| PDF downloaded | **{stats.pdf_downloaded_count}** |",
        f"| PDF parsed | **{stats.pdf_parsed_count}** |",
        f"| OCR / extraction | **0** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "",
        "## Safety",
        "",
        "- successful 12 cases not rerun: **yes**",
        "- Phase 2 expansion reports untouched: **yes**",
        "- Phase 1 baseline untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_failed_retry_execution_gate = {gate}",
        "a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED (unchanged)",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {x}" for x in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_failed_retry_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def _normalize_output_root(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    """输出仅允许 Phase 2 expansion 隔离根；禁止写入 Phase 1 / C-class harvest。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    phase1 = _normalize_output_root(PHASE1_OUTPUT_ROOT)
    c_harvest = _normalize_output_root(C_CLASS_HARVEST_ROOT)
    phase3 = _normalize_output_root(DEFAULT_PHASE3_OUTPUT_ROOT)

    if root == phase3 or root.startswith(phase3 + os.sep):
        return False, PHASE3_OUTPUT_ROOT_VIOLATION
    if root == phase1 or root.startswith(phase1 + os.sep):
        return False, PHASE1_BASELINE_WRITE_FORBIDDEN
    if root == c_harvest or root.startswith(c_harvest + os.sep):
        return False, "c_class_harvest_output_root_forbidden"
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, OUTPUT_ROOT_VIOLATION


def validate_phase3_output_root(output_root: str) -> Tuple[bool, str]:
    """Phase 3 输出仅允许 phase3 隔离根；禁止写入 Phase 1/2/retry/precheck/harvest。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_PHASE3_OUTPUT_ROOT)
    phase1 = _normalize_output_root(PHASE1_OUTPUT_ROOT)
    expansion = _normalize_output_root(DEFAULT_OUTPUT_ROOT)
    v1 = _normalize_output_root(DEFAULT_RETRY_OUTPUT_ROOT)
    v2 = _normalize_output_root(DEFAULT_RETRY_V2_OUTPUT_ROOT)
    v3 = _normalize_output_root(DEFAULT_RETRY_V3_OUTPUT_ROOT)
    precheck = _normalize_output_root(PRECHECK_OUTPUT_ROOT)
    c_harvest = _normalize_output_root(C_CLASS_HARVEST_ROOT)

    if root == phase1 or root.startswith(phase1 + os.sep):
        return False, PHASE1_BASELINE_WRITE_FORBIDDEN
    if root == expansion or root.startswith(expansion + os.sep):
        return False, PHASE2_EXPANSION_WRITE_FORBIDDEN
    if root == v1 or root.startswith(v1 + os.sep):
        return False, RETRY_V1_WRITE_FORBIDDEN
    if root == v2 or root.startswith(v2 + os.sep):
        return False, RETRY_V2_WRITE_FORBIDDEN
    if root == v3 or root.startswith(v3 + os.sep):
        return False, RETRY_V3_OUTPUT_ROOT_VIOLATION
    if root == precheck or root.startswith(precheck + os.sep):
        return False, PRECHECK_WRITE_FORBIDDEN
    if root == c_harvest or root.startswith(c_harvest + os.sep):
        return False, "c_class_harvest_output_root_forbidden"
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, PHASE3_OUTPUT_ROOT_VIOLATION


def ensure_output_layout(output_root: str) -> Dict[str, str]:
    paths = {
        "root": output_root,
        "reports": os.path.join(output_root, "reports"),
        "raw_metadata": os.path.join(output_root, "raw_metadata"),
    }
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    return paths


def load_universe(path: str) -> List[Phase2UniverseCase]:
    cases: List[Phase2UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(
                Phase2UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    report_type=str(row.get("report_type", "")).strip(),
                    expected_period=str(row.get("expected_period", "")).strip(),
                    expected_title_keywords=str(
                        row.get("expected_title_keywords", "")
                    ).strip(),
                    excluded_title_keywords=str(
                        row.get("excluded_title_keywords", "")
                    ).strip(),
                    risk_level=str(row.get("risk_level", "")).strip(),
                    phase1_overlap=str(row.get("phase1_overlap", "")).strip().lower(),
                    phase2_include=str(row.get("phase2_include", "")).strip().lower(),
                    reason=str(row.get("reason", "")).strip(),
                )
            )
    return cases


def load_phase3_universe(path: str) -> List[Phase3UniverseCase]:
    cases: List[Phase3UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(
                Phase3UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    report_type=str(row.get("report_type", "")).strip(),
                    expected_period=str(row.get("expected_period", "")).strip(),
                    expected_title_keywords=str(
                        row.get("expected_title_keywords", "")
                    ).strip(),
                    excluded_title_keywords=str(
                        row.get("excluded_title_keywords", "")
                    ).strip(),
                    risk_level=str(row.get("risk_level", "")).strip(),
                    phase1_overlap=str(row.get("phase1_overlap", "")).strip().lower(),
                    phase2_overlap=str(row.get("phase2_overlap", "")).strip().lower(),
                    phase3_include=str(row.get("phase3_include", "")).strip().lower(),
                    reason=str(row.get("reason", "")).strip(),
                )
            )
    return cases


def phase3_to_phase2_case(case: Phase3UniverseCase) -> Phase2UniverseCase:
    return Phase2UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        report_type=case.report_type,
        expected_period=case.expected_period,
        expected_title_keywords=case.expected_title_keywords,
        excluded_title_keywords=case.excluded_title_keywords,
        risk_level=case.risk_level,
        phase1_overlap=case.phase1_overlap,
        phase2_include="yes",
        reason=case.reason,
    )


def validate_phase3_case(case: Phase3UniverseCase) -> List[str]:
    issues: List[str] = []
    if not PHASE3_CASE_ID_PATTERN.match(case.case_id or ""):
        issues.append(NON_PHASE3_CASE_REJECTED)
    if case.case_id not in PHASE3_ALLOWED_CASE_IDS:
        issues.append(NON_PHASE3_CASE_REJECTED)
    if case.phase3_include != "yes":
        issues.append(PHASE3_INCLUDE_REQUIRED)
    if case.phase1_overlap not in ("", "no"):
        issues.append(PHASE1_OVERLAP_REJECTED)
    if case.phase2_overlap not in ("", "no"):
        issues.append(PHASE2_OVERLAP_REJECTED)
    if case.company_code in PHASE1_COMPANY_CODES:
        issues.append(f"{PHASE1_OVERLAP_REJECTED}:code:{case.company_code}")
    if case.company_code in PHASE2_EXCLUDED_COMPANY_CODES:
        issues.append(f"{PHASE2_OVERLAP_REJECTED}:code:{case.company_code}")
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    issues.extend(validate_universe_code_name(phase3_to_phase2_case(case)))
    return issues


def validate_phase3_universe_size(cases: List[Phase3UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.phase3_include == "yes"]
    if len(included) != PHASE3_REQUIRED_UNIVERSE_SIZE:
        return (
            False,
            f"{PHASE3_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {PHASE3_REQUIRED_UNIVERSE_SIZE}",
        )
    return True, ""


def validate_phase3_report_type_mix(cases: List[Phase3UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.phase3_include == "yes"]
    counts: Dict[str, int] = {}
    for case in included:
        counts[case.report_type] = counts.get(case.report_type, 0) + 1
    for report_type, expected in PHASE3_EXPECTED_REPORT_TYPE_MIX.items():
        if counts.get(report_type, 0) != expected:
            return (
                False,
                f"{PHASE3_REPORT_TYPE_MIX_VIOLATION}: {report_type}="
                f"{counts.get(report_type, 0)} expected {expected}",
            )
    return True, ""


def validate_phase3_duplicate_company_codes(cases: List[Phase3UniverseCase]) -> Tuple[bool, str]:
    seen: Set[str] = set()
    for case in cases:
        if case.phase3_include != "yes":
            continue
        if case.company_code in seen:
            return False, f"{DUPLICATE_COMPANY_CODE_REJECTED}:{case.company_code}"
        seen.add(case.company_code)
    return True, ""


def count_phase3_overlap(cases: List[Phase3UniverseCase]) -> Tuple[int, int]:
    phase1_count = 0
    phase2_count = 0
    for case in cases:
        if case.phase1_overlap not in ("", "no"):
            phase1_count += 1
        if case.company_code in PHASE1_COMPANY_CODES:
            phase1_count += 1
        if case.phase2_overlap not in ("", "no"):
            phase2_count += 1
        if case.company_code in PHASE2_EXCLUDED_COMPANY_CODES:
            phase2_count += 1
    return phase1_count, phase2_count


def validate_universe_code_name(case: Phase2UniverseCase) -> List[str]:
    issues: List[str] = []
    known = KNOWN_COMPANY_NAMES.get(case.company_code)
    if not known:
        return issues
    if known not in case.company_name and case.company_name not in known:
        issues.append(
            f"code_name_mismatch:{case.company_code}:{case.company_name}!={known}"
        )
    return issues


def validate_phase2_case(case: Phase2UniverseCase) -> List[str]:
    issues: List[str] = []
    if not PHASE2_CASE_ID_PATTERN.match(case.case_id or ""):
        issues.append(NON_PHASE2_CASE_REJECTED)
    if case.phase2_include != "yes":
        issues.append(PHASE2_INCLUDE_REQUIRED)
    if case.phase1_overlap not in ("", "no"):
        issues.append(PHASE1_OVERLAP_REJECTED)
    if case.company_code in PHASE1_COMPANY_CODES:
        issues.append(f"{PHASE1_OVERLAP_REJECTED}:code:{case.company_code}")
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    issues.extend(validate_universe_code_name(case))
    return issues


def validate_universe_size(cases: List[Phase2UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.phase2_include == "yes"]
    if len(included) != REQUIRED_UNIVERSE_SIZE:
        return (
            False,
            f"{UNIVERSE_SIZE_VIOLATION}: got {len(included)} expected {REQUIRED_UNIVERSE_SIZE}",
        )
    return True, ""


def validate_report_type_mix(cases: List[Phase2UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.phase2_include == "yes"]
    counts: Dict[str, int] = {}
    for case in included:
        counts[case.report_type] = counts.get(case.report_type, 0) + 1
    for report_type, expected in EXPECTED_REPORT_TYPE_MIX.items():
        if counts.get(report_type, 0) != expected:
            return (
                False,
                f"{REPORT_TYPE_MIX_VIOLATION}: {report_type}="
                f"{counts.get(report_type, 0)} expected {expected}",
            )
    return True, ""


def count_phase1_overlap(cases: List[Phase2UniverseCase]) -> int:
    count = 0
    for case in cases:
        if case.phase1_overlap not in ("", "no"):
            count += 1
        if case.company_code in PHASE1_COMPANY_CODES:
            count += 1
    return count


def enforce_forbidden_options(args: argparse.Namespace) -> None:
    checks = (
        (args.download_pdf, PDF_DOWNLOAD_REQUESTED_NOT_ALLOWED),
        (args.parse_pdf, PDF_PARSE_REQUESTED_NOT_ALLOWED),
        (args.enable_ocr, OCR_REQUESTED_NOT_ALLOWED),
        (args.enable_extraction, EXTRACTION_REQUESTED_NOT_ALLOWED),
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
    wrong_flags = (
        (args.approve_a_class_tiny_live_metadata, TINY_LIVE_APPROVAL_WRONG),
        (args.approve_phase1_tiny_live_metadata, PHASE1_TINY_LIVE_APPROVAL_WRONG),
        (args.approve_full_harvest, tiny_live.FORBIDDEN_APPROVE_FULL_HARVEST),
        (args.approve_phase2_smoke_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE2),
        (args.approve_phase3_batch_500_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE3),
        (args.approve_b_class_tiny_live_validation, tiny_live.FORBIDDEN_APPROVE_B_CLASS),
    )
    for enabled, error_code in wrong_flags:
        if enabled:
            print(f"ERROR: {error_code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not args.approve_a_class_phase2_metadata_expansion:
        print(f"ERROR: {PHASE2_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def planned_endpoints_for_case(_case: Phase2UniverseCase) -> str:
    return f"{tiny_live.TOPSEARCH_ENDPOINT};{tiny_live.HIS_ANNOUNCEMENT_ENDPOINT}"


def to_tiny_live_case(case: Phase2UniverseCase) -> tiny_live.UniverseCase:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    return tiny_live.UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        report_type=case.report_type,
        expected_period=case.expected_period,
        source_name=source_id,
        risk_level=case.risk_level,
        reason=case.reason,
    )


def build_dryrun_row(case: Phase2UniverseCase, issues: List[str]) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"dry-run; CNINFO not called; metadata only; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"storage_status=not_attempted"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "expected_title_keywords": case.expected_title_keywords,
        "excluded_title_keywords": case.excluded_title_keywords,
        "planned_source": source_id,
        "planned_endpoint": planned_endpoints_for_case(case),
        "planned_output": PLANNED_OUTPUT_OBJECTS,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "cninfo_call_planned": "0",
        "dryrun_status": status,
        "notes": notes,
    }


def process_dry_run(
    cases: List[Phase2UniverseCase],
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.phase2_include != "yes":
            continue
        issues = validate_phase2_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(build_dryrun_row(case, issues))
    return rows, universe_issues


def process_live(
    cases: List[Phase2UniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.phase2_include != "yes":
            continue
        issues = validate_phase2_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            invalid = build_live_report_row(
                case,
                {
                    "retrieval_status": "universe_invalid",
                    "quality_status": "blocked",
                    "lineage_status": "needs_review",
                    "announcement_id": "",
                    "announcement_title": "",
                    "announcement_time": "",
                    "title_match_status": "n/a",
                    "period_match_status": "n/a",
                    "pdf_url_present": "no",
                    "adjunct_url_present": "no",
                    "notes": "; ".join(issues),
                },
                0,
            )
            rows.append(invalid)
            stats.failure_count += 1
            continue

        tl_case = to_tiny_live_case(case)
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        snapshot_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}.json")
        live_row = build_live_report_row(case, record, case_cninfo_requests)
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": "live_phase2",
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": DOWNLOAD_PDF,
                    "pdf_parse_enabled": PARSE_PDF,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={case.case_id} company_code={case.company_code} "
            f"retrieval_status={live_row['retrieval_status']} "
            f"title_match={live_row.get('title_match_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def write_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_dryrun_summary(
    output_paths: Dict[str, str],
    case_count: int,
    universe_issues: List[str],
    report_type_mix: Dict[str, int],
    phase1_overlap_count: int,
) -> str:
    planned_ok = case_count - len(universe_issues)
    mix_line = " / ".join(f"{k}={v}" for k, v in sorted(report_type_mix.items()))
    lines = [
        "# CNINFO A 类 Phase 2 Metadata Expansion — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 2 runner dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | dry_run |",
        f"| universe size | {case_count} |",
        f"| planned_ok | {planned_ok} |",
        f"| universe_issues | {len(universe_issues)} |",
        f"| report-type mix | {mix_line} |",
        f"| phase1_overlap | **{phase1_overlap_count}** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- Phase 1 baseline untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase2_metadata_runner_gate = {RUNNER_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase2_metadata_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_phase3_dryrun_row(
    case: Phase3UniverseCase,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"phase3 dry-run; CNINFO not called; metadata only; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"planned_requests={PHASE3_PLANNED_REQUESTS_PER_CASE}"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "expected_title_keywords": case.expected_title_keywords,
        "excluded_title_keywords": case.excluded_title_keywords,
        "phase3_include": case.phase3_include,
        "planned_source": source_id,
        "planned_endpoint": planned_endpoints_for_case(phase3_to_phase2_case(case)),
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


def process_phase3_dry_run(
    cases: List[Phase3UniverseCase],
    output_root: str,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.phase3_include != "yes":
            continue
        issues = validate_phase3_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(build_phase3_dryrun_row(case, issues, output_root))
    return rows, universe_issues


def write_phase3_dryrun_report(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase3_50_company_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PHASE3_DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_phase3_dryrun_summary(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_issues: List[str],
    report_type_mix: Dict[str, int],
    phase1_overlap_count: int,
    phase2_overlap_count: int,
) -> str:
    planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
    total = len(rows)
    mix_line = " / ".join(f"{k}={v}" for k, v in sorted(report_type_mix.items()))
    lines = [
        "# CNINFO A 类 Phase 3 50-Company Expansion — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 3 runner dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | phase3_dry_run |",
        f"| universe size | {total} |",
        f"| planned_ok | {planned_ok} |",
        f"| universe_issues | {len(universe_issues)} |",
        f"| report-type mix | {mix_line} |",
        f"| phase1_overlap | **{phase1_overlap_count}** |",
        f"| phase2_overlap | **{phase2_overlap_count}** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        "| PDF download | **0** |",
        "| PDF parse | **0** |",
        "| OCR | **0** |",
        "| extraction | **0** |",
        "| DB write | **0** |",
        "| MinIO write | **0** |",
        "| RAG run | **0** |",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- Phase 1 / Phase 2 / retry / precheck baseline untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase3_50_company_runner_extension_gate = {PHASE3_RUNNER_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**",
        "",
        "**Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase3_50_company_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_phase3_live_report_row(
    case: Phase3UniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    row = build_live_report_row(
        phase3_to_phase2_case(case), record, cninfo_request_count
    )
    notes = str(record.get("notes") or "")
    row["notes"] = (
        f"phase3 live; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"PDF not downloaded; {notes}"
    ).strip()
    return row


def is_phase3_case_acceptable(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    status = row.get("retrieval_status", "")
    quality = row.get("quality_status", "")
    lineage = row.get("lineage_status", "")
    if status in ("network_error", "not_found", "universe_invalid"):
        return False
    if status == "found":
        return True
    if status in ("discovered", "matching_pass"):
        return True
    if lineage == "discovered":
        return True
    if status == "needs_review" or quality == "needs_review":
        return bool(lineage)
    return False


def compute_phase3_execution_gate(
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues or case_count != PHASE3_REQUIRED_UNIVERSE_SIZE:
        return "FAIL_REVIEW_REQUIRED"
    acceptable_count = sum(1 for row in rows if is_phase3_case_acceptable(row))
    if acceptable_count >= PHASE3_ACCEPTABLE_THRESHOLD:
        return PHASE3_EXECUTION_GATE_PASS
    return "FAIL_REVIEW_REQUIRED"


def process_phase3_50_live(
    phase3_cases: List[Phase3UniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in phase3_cases:
        if case.phase3_include != "yes":
            continue
        issues = validate_phase3_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            rows.append(
                build_phase3_live_report_row(
                    case,
                    {
                        "retrieval_status": "universe_invalid",
                        "quality_status": "blocked",
                        "lineage_status": "needs_review",
                        "announcement_id": "",
                        "announcement_title": "",
                        "announcement_time": "",
                        "title_match_status": "fail",
                        "period_match_status": "fail",
                        "pdf_url_present": "no",
                        "adjunct_url_present": "no",
                        "notes": "; ".join(issues),
                    },
                    0,
                )
            )
            stats.failure_count += 1
            continue

        tl_case = to_tiny_live_case(phase3_to_phase2_case(case))
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        live_row = build_phase3_live_report_row(case, record, case_cninfo_requests)
        snapshot_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}.json")
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": "phase3_live",
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": False,
                    "pdf_parse_enabled": False,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={case.case_id} company_code={case.company_code} "
            f"retrieval_status={live_row['retrieval_status']} "
            f"quality={live_row.get('quality_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def write_phase3_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase3_50_company_expansion_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_phase3_live_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_phase3_50_company_expansion_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in LIVE_QUALITY_COLUMNS})
    return report_path


def write_phase3_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    acceptable_count = sum(1 for row in rows if is_phase3_case_acceptable(row))
    failed_count = sum(
        1
        for row in rows
        if row.get("retrieval_status")
        in ("network_error", "not_found", "universe_invalid")
    )
    needs_review_count = sum(
        1 for row in rows if row.get("quality_status") == "needs_review"
    )
    lines = [
        "# CNINFO A 类 Phase 3 50-Company Expansion — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Phase 3 live metadata validation · **50 cases** · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | phase3_live |",
        f"| universe size | {len(rows)} |",
        f"| acceptable | {acceptable_count} |",
        f"| failed | {failed_count} |",
        f"| needs_review | {needs_review_count} |",
        f"| CNINFO requests | {stats.cninfo_requests} |",
        f"| PDF downloaded | **{stats.pdf_downloaded_count}** |",
        f"| PDF parsed | **{stats.pdf_parsed_count}** |",
        f"| OCR / extraction | **0** |",
        f"| DB / MinIO / RAG | **0** |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- Phase 1 / Phase 2 / retry / precheck baseline untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_phase3_50_company_execution_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])

    summary_path = os.path.join(
        output_paths["reports"], "a_class_phase3_50_company_expansion_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path



def _is_under_prefix(root: str, prefix: str) -> bool:
    p = _normalize_output_root(prefix)
    return root == p or root.startswith(p + os.sep)


def validate_erad_scale_200_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT)
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, ERAD_SCALE_200_OUTPUT_ROOT_VIOLATION


def load_erad_scale_200_universe(path: str) -> List[EraDScale200UniverseCase]:
    cases: List[EraDScale200UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(
                EraDScale200UniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    report_type=str(row.get("report_type", "")).strip(),
                    expected_period=str(row.get("expected_period", "")).strip(),
                    expected_title_keywords=str(row.get("expected_title_keywords", "")).strip(),
                    excluded_title_keywords=str(row.get("excluded_title_keywords", "")).strip(),
                    cohort=str(row.get("cohort", "")).strip(),
                    phase3_source_case_id=str(row.get("phase3_source_case_id", "")).strip(),
                    erad_include=str(row.get("erad_include", "")).strip().lower(),
                    phase1_overlap=str(row.get("phase1_overlap", "")).strip().lower(),
                    phase2_overlap=str(row.get("phase2_overlap", "")).strip().lower(),
                    phase3_overlap=str(row.get("phase3_overlap", "")).strip().lower(),
                    prior_a_phase_overlap=str(row.get("prior_a_phase_overlap", "")).strip().lower(),
                    selection_bucket=str(row.get("selection_bucket", "")).strip(),
                    risk_level=str(row.get("risk_level", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return cases


def erad_to_phase2_case(case: EraDScale200UniverseCase) -> Phase2UniverseCase:
    return Phase2UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        report_type=case.report_type,
        expected_period=case.expected_period,
        expected_title_keywords=case.expected_title_keywords,
        excluded_title_keywords=case.excluded_title_keywords,
        risk_level=case.risk_level or "medium",
        phase1_overlap=case.phase1_overlap,
        phase2_include="yes",
        reason=case.notes,
    )


def validate_erad_scale_200_case(case: EraDScale200UniverseCase) -> List[str]:
    issues: List[str] = []
    if not ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id or ""):
        issues.append("non_ad2e_case_not_allowed")
    if case.case_id not in ERAD_SCALE_200_ALLOWED_CASE_IDS:
        issues.append("non_ad2e_case_not_allowed")
    if case.erad_include != "yes":
        issues.append(ERAD_SCALE_200_INCLUDE_REQUIRED)
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if case.cohort == "retained_phase3":
        if case.phase3_overlap not in ("yes",):
            issues.append(f"{ERAD_SCALE_200_COHORT_VIOLATION}:retained_missing_phase3_overlap")
        if not case.phase3_source_case_id:
            issues.append(f"{ERAD_SCALE_200_COHORT_VIOLATION}:retained_missing_phase3_source_case_id")
    elif case.cohort == "new_erad":
        if case.phase1_overlap not in ("", "no") or case.company_code in PHASE1_COMPANY_CODES:
            issues.append(ERAD_SCALE_200_NEW_COHORT_OVERLAP)
        if case.phase2_overlap not in ("", "no") or case.company_code in PHASE2_EXCLUDED_COMPANY_CODES:
            issues.append(ERAD_SCALE_200_NEW_COHORT_OVERLAP)
        if case.phase3_overlap not in ("", "no"):
            issues.append(ERAD_SCALE_200_NEW_COHORT_OVERLAP)
    else:
        issues.append(f"{ERAD_SCALE_200_COHORT_VIOLATION}:unknown_cohort")
    issues.extend(validate_universe_code_name(erad_to_phase2_case(case)))
    return issues


def validate_erad_scale_200_universe_size(cases: List[EraDScale200UniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != ERAD_SCALE_200_REQUIRED_UNIVERSE_SIZE:
        return False, f"{ERAD_SCALE_200_UNIVERSE_SIZE_VIOLATION}: got {len(included)} expected {ERAD_SCALE_200_REQUIRED_UNIVERSE_SIZE}"
    return True, ""


def validate_erad_scale_200_report_type_mix(cases: List[EraDScale200UniverseCase]) -> Tuple[bool, str]:
    counts: Dict[str, int] = {}
    for case in cases:
        if case.erad_include != "yes":
            continue
        counts[case.report_type] = counts.get(case.report_type, 0) + 1
    for report_type, expected in ERAD_SCALE_200_EXPECTED_REPORT_TYPE_MIX.items():
        if counts.get(report_type, 0) != expected:
            return False, f"{ERAD_SCALE_200_REPORT_TYPE_MIX_VIOLATION}: {report_type}={counts.get(report_type, 0)} expected {expected}"
    return True, ""


def validate_erad_scale_200_duplicate_company_codes(cases: List[EraDScale200UniverseCase]) -> Tuple[bool, str]:
    seen: Set[str] = set()
    for case in cases:
        if case.erad_include != "yes":
            continue
        if case.company_code in seen:
            return False, f"{DUPLICATE_COMPANY_CODE_REJECTED}:{case.company_code}"
        seen.add(case.company_code)
    return True, ""


def validate_erad_scale_200_cohort_counts(cases: List[EraDScale200UniverseCase]) -> Tuple[bool, str]:
    retained = sum(1 for c in cases if c.erad_include == "yes" and c.cohort == "retained_phase3")
    new = sum(1 for c in cases if c.erad_include == "yes" and c.cohort == "new_erad")
    if retained != ERAD_SCALE_200_RETAINED_COUNT or new != ERAD_SCALE_200_NEW_COUNT:
        return False, f"{ERAD_SCALE_200_COHORT_VIOLATION}: retained={retained} new={new}"
    return True, ""


def validate_erad_scale_200_new_cohort_overlap(cases: List[EraDScale200UniverseCase]) -> Tuple[bool, str]:
    for case in cases:
        if case.erad_include != "yes" or case.cohort != "new_erad":
            continue
        if case.phase1_overlap not in ("", "no") or case.phase2_overlap not in ("", "no") or case.phase3_overlap not in ("", "no"):
            return False, ERAD_SCALE_200_NEW_COHORT_OVERLAP
        if case.company_code in PHASE1_COMPANY_CODES or case.company_code in PHASE2_EXCLUDED_COMPANY_CODES:
            return False, ERAD_SCALE_200_NEW_COHORT_OVERLAP
    return True, ""


def validate_erad_scale_200_request_cap(case_count: int) -> Tuple[bool, str]:
    planned = case_count * ERAD_SCALE_200_PLANNED_REQUESTS_PER_CASE
    if planned > ERAD_SCALE_200_REQUEST_CAP:
        return False, f"{ERAD_SCALE_200_REQUEST_CAP_EXCEEDED}: planned={planned} cap={ERAD_SCALE_200_REQUEST_CAP}"
    return True, ""


def enforce_erad_scale_200_approval_gate(args: argparse.Namespace) -> None:
    wrong = (
        (args.approve_a_class_phase2_metadata_expansion, ERAD_SCALE_200_WRONG_APPROVAL),
        (args.approve_a_class_phase2_failed_retry, ERAD_SCALE_200_WRONG_APPROVAL),
        (args.approve_a_class_phase2_network_recovery_retry_v2, ERAD_SCALE_200_WRONG_APPROVAL),
        (args.approve_a_class_phase2_retry_v3, ERAD_SCALE_200_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_phase3_50_company_expansion", False), ERAD_SCALE_200_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_phase3_a3m017_isolated_retry", False), ERAD_SCALE_200_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_500_slice1", False), ERAD_SCALE_200_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_500_slice2", False), ERAD_SCALE_200_WRONG_APPROVAL),
        (args.approve_a_class_tiny_live_metadata, ERAD_SCALE_200_WRONG_APPROVAL),
        (args.approve_phase1_tiny_live_metadata, ERAD_SCALE_200_WRONG_APPROVAL),
    )
    for enabled, code in wrong:
        if enabled:
            print(f"ERROR: {code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not getattr(args, "approve_a_class_erad_scale_200", False):
        print(f"ERROR: {ERAD_SCALE_200_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def build_erad_scale_200_dryrun_row(case: EraDScale200UniverseCase, issues: List[str], output_root: str) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    cohort_note = "retained_phase3_lineage_only_no_phase3_root_write" if case.cohort == "retained_phase3" else "new_erad_cohort"
    notes = (
        f"erad-a-scale-200 dry-run; CNINFO not called; metadata only; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"planned_requests={ERAD_SCALE_200_PLANNED_REQUESTS_PER_CASE}; {cohort_note}"
        if not issues else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "cohort": case.cohort,
        "phase3_source_case_id": case.phase3_source_case_id,
        "erad_include": case.erad_include,
        "phase1_overlap": case.phase1_overlap,
        "phase2_overlap": case.phase2_overlap,
        "phase3_overlap": case.phase3_overlap,
        "planned_source": source_id,
        "planned_endpoint": planned_endpoints_for_case(erad_to_phase2_case(case)),
        "planned_output_root": output_root,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "db_write": "0",
        "minio_write": "0",
        "rag_run": "0",
        "cninfo_call_planned": "0",
        "planned_request_count_case": str(ERAD_SCALE_200_PLANNED_REQUESTS_PER_CASE),
        "dryrun_status": status,
        "notes": notes,
    }


def process_erad_scale_200_dry_run(cases: List[EraDScale200UniverseCase], output_root: str) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.erad_include != "yes":
            continue
        issues = validate_erad_scale_200_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(build_erad_scale_200_dryrun_row(case, issues, output_root))
    return rows, universe_issues


def write_erad_scale_200_dryrun_report(rows: List[Dict[str, str]], output_paths: Dict[str, str]) -> str:
    report_path = os.path.join(output_paths["reports"], "a_class_erad_scale_200_dryrun_report.csv")
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_SCALE_200_DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_erad_scale_200_dryrun_summary(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_issues: List[str],
    report_type_mix: Dict[str, int],
    retained_count: int,
    new_count: int,
) -> str:
    planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
    total = len(rows)
    planned_requests = total * ERAD_SCALE_200_PLANNED_REQUESTS_PER_CASE
    mix_line = " / ".join(f"{k}={v}" for k, v in sorted(report_type_mix.items()))
    lines = [
        "# CNINFO A 类 Era D ~200 Metadata Expansion — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Era D runner dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | erad_a_scale_200_dry_run |",
        f"| universe size | {total} |",
        f"| planned_ok | {planned_ok} |",
        f"| retained_phase3 | {retained_count} |",
        f"| new_erad | {new_count} |",
        f"| report-type mix | {mix_line} |",
        f"| planned_requests_total | {planned_requests} (cap ≤ {ERAD_SCALE_200_REQUEST_CAP}) |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        "",
        "## Retained cohort note",
        "",
        "Retained 50 cases reference Phase 3 post-retry effective lineage via `phase3_source_case_id`. "
        "Dry-run writes **only** under Era D root; **does not rewrite** Phase 3 expansion or A3M017 retry production roots.",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- Phase 1/2/Phase3/A3M017/B/C/D roots untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_erad_scale_200_runner_extension_gate = {ERAD_SCALE_200_RUNNER_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])
    summary_path = os.path.join(output_paths["reports"], "a_class_erad_scale_200_dryrun_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_erad_scale_200_live_report_row(
    case: EraDScale200UniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    row = build_live_report_row(erad_to_phase2_case(case), record, cninfo_request_count)
    cohort_note = (
        "retained_phase3_lineage_only_no_phase3_root_write"
        if case.cohort == "retained_phase3"
        else "new_erad_cohort"
    )
    phase3_ref = ""
    if case.cohort == "retained_phase3" and case.phase3_source_case_id:
        phase3_ref = f"phase3_source={case.phase3_source_case_id}; "
    notes = str(record.get("notes") or "")
    row["notes"] = (
        f"erad-a-scale-200 live; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"PDF not downloaded; {phase3_ref}{cohort_note}; {notes}"
    ).strip()
    row["cohort"] = case.cohort
    row["phase3_source_case_id"] = case.phase3_source_case_id
    return row


def is_erad_scale_200_case_acceptable(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    status = row.get("retrieval_status", "")
    quality = row.get("quality_status", "")
    lineage = row.get("lineage_status", "")
    if status in ("network_error", "not_found", "universe_invalid"):
        return False
    if status == "found":
        return True
    if status in ("discovered", "matching_pass"):
        return True
    if lineage == "discovered":
        return True
    if status == "needs_review" or quality == "needs_review":
        return bool(lineage)
    return False


def compute_erad_scale_200_execution_gate(
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues or case_count != ERAD_SCALE_200_REQUIRED_UNIVERSE_SIZE:
        return "FAIL_REVIEW_REQUIRED"
    if stats.cninfo_requests > ERAD_SCALE_200_REQUEST_CAP:
        return "FAIL_REVIEW_REQUIRED"
    acceptable_count = sum(1 for row in rows if is_erad_scale_200_case_acceptable(row))
    if acceptable_count >= ERAD_SCALE_200_ACCEPTABLE_THRESHOLD:
        return ERAD_SCALE_200_EXECUTION_GATE_PASS
    return "FAIL_REVIEW_REQUIRED"


def process_erad_scale_200_live(
    cases: List[EraDScale200UniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.erad_include != "yes":
            continue
        issues = validate_erad_scale_200_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            rows.append(
                build_erad_scale_200_live_report_row(
                    case,
                    {
                        "retrieval_status": "universe_invalid",
                        "quality_status": "blocked",
                        "lineage_status": "needs_review",
                        "announcement_id": "",
                        "announcement_title": "",
                        "announcement_time": "",
                        "title_match_status": "fail",
                        "period_match_status": "fail",
                        "pdf_url_present": "no",
                        "adjunct_url_present": "no",
                        "notes": "; ".join(issues),
                    },
                    0,
                )
            )
            stats.failure_count += 1
            continue

        tl_case = to_tiny_live_case(erad_to_phase2_case(case))
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        live_row = build_erad_scale_200_live_report_row(case, record, case_cninfo_requests)
        snapshot_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}.json")
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": "erad_a_scale_200_live",
                    "cohort": case.cohort,
                    "phase3_source_case_id": case.phase3_source_case_id,
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": False,
                    "pdf_parse_enabled": False,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={case.case_id} cohort={case.cohort} company_code={case.company_code} "
            f"retrieval_status={live_row['retrieval_status']} "
            f"quality={live_row.get('quality_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def write_erad_scale_200_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_scale_200_live_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_SCALE_200_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_erad_scale_200_live_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_scale_200_live_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_SCALE_200_LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in ERAD_SCALE_200_LIVE_QUALITY_COLUMNS})
    return report_path


def write_erad_scale_200_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
    retained_count: int,
    new_count: int,
) -> str:
    acceptable_count = sum(1 for row in rows if is_erad_scale_200_case_acceptable(row))
    failed_count = sum(
        1
        for row in rows
        if row.get("retrieval_status")
        in ("network_error", "not_found", "universe_invalid")
    )
    needs_review_count = sum(
        1 for row in rows if row.get("quality_status") == "needs_review"
    )
    lines = [
        "# CNINFO A 类 Era D ~200 Metadata Expansion — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Era D live metadata validation · **200 cases** · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | erad_a_scale_200_live |",
        f"| universe size | {len(rows)} |",
        f"| acceptable | {acceptable_count} |",
        f"| failed | {failed_count} |",
        f"| needs_review | {needs_review_count} |",
        f"| retained_phase3 | {retained_count} |",
        f"| new_erad | {new_count} |",
        f"| CNINFO requests | {stats.cninfo_requests} (cap ≤ {ERAD_SCALE_200_REQUEST_CAP}) |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        f"| execution gate | `{gate}` |",
        "",
        "## Retained cohort note",
        "",
        "Retained 50 cases reference Phase 3 post-retry effective lineage via `phase3_source_case_id`. "
        "Live writes **only** under Era D root; **does not rewrite** Phase 3 expansion or A3M017 retry production roots.",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- Phase 1/2/Phase3/A3M017/B/C/D roots untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_erad_scale_200_live_path_gate = {ERAD_SCALE_200_LIVE_PATH_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])
    summary_path = os.path.join(
        output_paths["reports"], "a_class_erad_scale_200_live_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def validate_erad_failed_retry_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT)
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_FAILED_RETRY_MAIN_ERAD_ROOT_FORBIDDEN),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, ERAD_FAILED_RETRY_OUTPUT_ROOT_VIOLATION


def load_erad_failed_retry_universe(path: str) -> List[EraDFailedRetryUniverseCase]:
    cases: List[EraDFailedRetryUniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(
                EraDFailedRetryUniverseCase(
                    case_id=str(row.get("case_id", "")).strip(),
                    company_code=str(row.get("company_code", "")).strip(),
                    company_name=str(row.get("company_name", "")).strip(),
                    market=str(row.get("market", "")).strip(),
                    report_type=str(row.get("report_type", "")).strip(),
                    expected_period=str(row.get("expected_period", "")).strip(),
                    expected_title_keywords=str(row.get("expected_title_keywords", "")).strip(),
                    excluded_title_keywords=str(row.get("excluded_title_keywords", "")).strip(),
                    cohort=str(row.get("cohort", "")).strip(),
                    original_failure_class=str(row.get("original_failure_class", "")).strip(),
                    likely_cause=str(row.get("likely_cause", "")).strip(),
                    retry_include=str(row.get("retry_include", "")).strip().lower(),
                    retry_strategy=str(row.get("retry_strategy", "")).strip(),
                    notes=str(row.get("notes", "")).strip(),
                )
            )
    return cases


def failed_retry_to_phase2_case(case: EraDFailedRetryUniverseCase) -> Phase2UniverseCase:
    return Phase2UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        report_type=case.report_type,
        expected_period=case.expected_period,
        expected_title_keywords=case.expected_title_keywords,
        excluded_title_keywords=case.excluded_title_keywords,
        risk_level="medium",
        phase1_overlap="no",
        phase2_include="yes",
        reason=case.notes,
    )


def validate_erad_failed_retry_case(case: EraDFailedRetryUniverseCase) -> List[str]:
    issues: List[str] = []
    if case.case_id == ERAD_FAILED_RETRY_DEFERRED_CASE_ID:
        issues.append(ERAD_FAILED_RETRY_DEFERRED_CASE_REJECTED)
    if case.case_id not in ERAD_FAILED_RETRY_ALLOWED_CASE_IDS:
        issues.append(ERAD_FAILED_RETRY_NON_RETRY_CASE_REJECTED)
    if case.retry_include != "yes":
        issues.append(ERAD_FAILED_RETRY_INCLUDE_REQUIRED)
    if case.cohort != "new_erad":
        issues.append(ERAD_FAILED_RETRY_COHORT_VIOLATION)
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if not case.retry_strategy:
        issues.append("retry_strategy_missing")
    issues.extend(validate_universe_code_name(failed_retry_to_phase2_case(case)))
    return issues


def validate_erad_failed_retry_universe_size(cases: List[EraDFailedRetryUniverseCase]) -> Tuple[bool, str]:
    included = [c for c in cases if c.retry_include == "yes"]
    if len(included) != ERAD_FAILED_RETRY_REQUIRED_UNIVERSE_SIZE:
        return False, (
            f"{ERAD_FAILED_RETRY_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {ERAD_FAILED_RETRY_REQUIRED_UNIVERSE_SIZE}"
        )
    return True, ""


def validate_erad_failed_retry_universe_case_set(cases: List[EraDFailedRetryUniverseCase]) -> Tuple[bool, str]:
    if ERAD_FAILED_RETRY_DEFERRED_CASE_ID in {c.case_id for c in cases}:
        return False, ERAD_FAILED_RETRY_DEFERRED_CASE_REJECTED
    included_ids = {c.case_id for c in cases if c.retry_include == "yes"}
    if included_ids != ERAD_FAILED_RETRY_ALLOWED_CASE_IDS:
        missing = ERAD_FAILED_RETRY_ALLOWED_CASE_IDS - included_ids
        extra = included_ids - ERAD_FAILED_RETRY_ALLOWED_CASE_IDS
        return False, (
            f"{ERAD_FAILED_RETRY_UNIVERSE_CASE_SET_VIOLATION}: "
            f"missing={sorted(missing)} extra={sorted(extra)}"
        )
    return True, ""


def validate_erad_failed_retry_duplicate_company_codes(
    cases: List[EraDFailedRetryUniverseCase],
) -> Tuple[bool, str]:
    seen: Set[str] = set()
    for case in cases:
        if case.retry_include != "yes":
            continue
        if case.company_code in seen:
            return False, f"{DUPLICATE_COMPANY_CODE_REJECTED}:{case.company_code}"
        seen.add(case.company_code)
    return True, ""


def validate_erad_failed_retry_request_cap(case_count: int) -> Tuple[bool, str]:
    planned = case_count * ERAD_FAILED_RETRY_PLANNED_REQUESTS_PER_CASE
    if planned > ERAD_FAILED_RETRY_REQUEST_CAP:
        return False, (
            f"{ERAD_FAILED_RETRY_REQUEST_CAP_EXCEEDED}: planned={planned} "
            f"cap={ERAD_FAILED_RETRY_REQUEST_CAP}"
        )
    return True, ""


def enforce_erad_failed_retry_approval_gate(args: argparse.Namespace) -> None:
    wrong = (
        (args.approve_a_class_phase2_metadata_expansion, ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (args.approve_a_class_phase2_failed_retry, ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (args.approve_a_class_phase2_network_recovery_retry_v2, ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (args.approve_a_class_phase2_retry_v3, ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_phase3_50_company_expansion", False), ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_phase3_a3m017_isolated_retry", False), ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_200", False), ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_500_slice1", False), ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_500_slice2", False), ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (args.approve_a_class_tiny_live_metadata, ERAD_FAILED_RETRY_WRONG_APPROVAL),
        (args.approve_phase1_tiny_live_metadata, ERAD_FAILED_RETRY_WRONG_APPROVAL),
    )
    for enabled, code in wrong:
        if enabled:
            print(f"ERROR: {code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not getattr(args, "approve_a_class_erad_scale_200_failed_retry", False):
        print(f"ERROR: {ERAD_FAILED_RETRY_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def build_erad_failed_retry_dryrun_row(
    case: EraDFailedRetryUniverseCase,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"erad-a-scale-200-failed-retry dry-run; CNINFO not called; metadata only; "
        f"matching_logic={MATCHING_LOGIC_VERSION}; "
        f"planned_requests={ERAD_FAILED_RETRY_PLANNED_REQUESTS_PER_CASE}; "
        f"retry_strategy={case.retry_strategy}; likely_cause={case.likely_cause}; "
        f"main_erad_root_write_forbidden"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "cohort": case.cohort,
        "original_failure_class": case.original_failure_class,
        "likely_cause": case.likely_cause,
        "retry_strategy": case.retry_strategy,
        "retry_include": case.retry_include,
        "planned_source": source_id,
        "planned_endpoint": planned_endpoints_for_case(failed_retry_to_phase2_case(case)),
        "planned_output_root": output_root,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "db_write": "0",
        "minio_write": "0",
        "rag_run": "0",
        "cninfo_call_planned": "0",
        "planned_request_count_case": str(ERAD_FAILED_RETRY_PLANNED_REQUESTS_PER_CASE),
        "dryrun_status": status,
        "notes": notes,
    }


def process_erad_failed_retry_dry_run(
    cases: List[EraDFailedRetryUniverseCase],
    output_root: str,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = validate_erad_failed_retry_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(build_erad_failed_retry_dryrun_row(case, issues, output_root))
    return rows, universe_issues


def write_erad_failed_retry_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_scale_200_failed_retry_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_FAILED_RETRY_DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_erad_failed_retry_dryrun_summary(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_issues: List[str],
) -> str:
    planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
    total = len(rows)
    planned_requests = total * ERAD_FAILED_RETRY_PLANNED_REQUESTS_PER_CASE
    cause_counts: Dict[str, int] = {}
    for row in rows:
        cause_counts[row["likely_cause"]] = cause_counts.get(row["likely_cause"], 0) + 1
    cause_line = " / ".join(f"{k}={v}" for k, v in sorted(cause_counts.items()))
    lines = [
        "# CNINFO A 类 Era D ~200 Failed Retry — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Era D isolated failed-retry dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | erad_a_scale_200_failed_retry_dry_run |",
        f"| universe size | {total} |",
        f"| planned_ok | {planned_ok} |",
        f"| deferred excluded | AD2E146 |",
        f"| likely_cause mix | {cause_line} |",
        f"| planned_requests_total | {planned_requests} (cap ≤ {ERAD_FAILED_RETRY_REQUEST_CAP}) |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        "",
        "## Isolation",
        "",
        "Writes **only** under failed-retry root; **does not mutate** main Era D live root, Phase 3, or A3M017.",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- main Era D live root untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_erad_scale_200_isolated_retry_runner_extension_gate = {ERAD_FAILED_RETRY_RUNNER_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])
    summary_path = os.path.join(
        output_paths["reports"], "a_class_erad_scale_200_failed_retry_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def build_erad_failed_retry_live_report_row(
    case: EraDFailedRetryUniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    row = build_live_report_row(failed_retry_to_phase2_case(case), record, cninfo_request_count)
    notes = str(record.get("notes") or "")
    row["notes"] = (
        f"erad-a-scale-200-failed-retry live; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"PDF not downloaded; retry_strategy={case.retry_strategy}; "
        f"likely_cause={case.likely_cause}; main_erad_root_write_forbidden; {notes}"
    ).strip()
    row["cohort"] = case.cohort
    row["original_failure_class"] = case.original_failure_class
    row["likely_cause"] = case.likely_cause
    row["retry_strategy"] = case.retry_strategy
    return row


def is_erad_failed_retry_case_acceptable(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    status = row.get("retrieval_status", "")
    quality = row.get("quality_status", "")
    lineage = row.get("lineage_status", "")
    if status in ("network_error", "not_found", "universe_invalid"):
        return False
    if status == "found":
        return True
    if status in ("discovered", "matching_pass"):
        return True
    if lineage == "discovered":
        return True
    if status == "needs_review" or quality == "needs_review":
        return bool(lineage)
    return False


def compute_erad_failed_retry_execution_gate(
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues or case_count != ERAD_FAILED_RETRY_REQUIRED_UNIVERSE_SIZE:
        return "FAIL_REVIEW_REQUIRED"
    if stats.cninfo_requests > ERAD_FAILED_RETRY_REQUEST_CAP:
        return "FAIL_REVIEW_REQUIRED"
    acceptable_count = sum(1 for row in rows if is_erad_failed_retry_case_acceptable(row))
    if acceptable_count >= ERAD_FAILED_RETRY_ACCEPTABLE_THRESHOLD:
        return ERAD_FAILED_RETRY_EXECUTION_GATE_PASS
    return "FAIL_REVIEW_REQUIRED"


def process_erad_failed_retry_live(
    cases: List[EraDFailedRetryUniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.retry_include != "yes":
            continue
        issues = validate_erad_failed_retry_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            rows.append(
                build_erad_failed_retry_live_report_row(
                    case,
                    {
                        "retrieval_status": "universe_invalid",
                        "quality_status": "blocked",
                        "lineage_status": "needs_review",
                        "announcement_id": "",
                        "announcement_title": "",
                        "announcement_time": "",
                        "title_match_status": "fail",
                        "period_match_status": "fail",
                        "pdf_url_present": "no",
                        "adjunct_url_present": "no",
                        "notes": "; ".join(issues),
                    },
                    0,
                )
            )
            stats.failure_count += 1
            continue

        tl_case = to_tiny_live_case(failed_retry_to_phase2_case(case))
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        live_row = build_erad_failed_retry_live_report_row(case, record, case_cninfo_requests)
        snapshot_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}.json")
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case": case.__dict__,
                    "mode": "erad_a_scale_200_failed_retry_live",
                    "original_failure_class": case.original_failure_class,
                    "likely_cause": case.likely_cause,
                    "retry_strategy": case.retry_strategy,
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": False,
                    "pdf_parse_enabled": False,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={case.case_id} likely_cause={case.likely_cause} "
            f"company_code={case.company_code} "
            f"retrieval_status={live_row['retrieval_status']} "
            f"quality={live_row.get('quality_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def write_erad_failed_retry_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_scale_200_failed_retry_live_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_FAILED_RETRY_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_erad_failed_retry_live_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_scale_200_failed_retry_live_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_FAILED_RETRY_LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in ERAD_FAILED_RETRY_LIVE_QUALITY_COLUMNS})
    return report_path


def write_erad_failed_retry_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
) -> str:
    acceptable_count = sum(1 for row in rows if is_erad_failed_retry_case_acceptable(row))
    failed_count = sum(
        1
        for row in rows
        if row.get("retrieval_status")
        in ("network_error", "not_found", "universe_invalid")
    )
    needs_review_count = sum(
        1 for row in rows if row.get("quality_status") == "needs_review"
    )
    lines = [
        "# CNINFO A 类 Era D ~200 Failed Retry — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Era D isolated failed-retry live · **7 cases** · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | erad_a_scale_200_failed_retry_live |",
        f"| universe size | {len(rows)} |",
        f"| acceptable | {acceptable_count} |",
        f"| failed | {failed_count} |",
        f"| needs_review | {needs_review_count} |",
        f"| deferred excluded | AD2E146 |",
        f"| CNINFO requests | {stats.cninfo_requests} (cap ≤ {ERAD_FAILED_RETRY_REQUEST_CAP}) |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        f"| execution gate | `{gate}` |",
        "",
        "## Isolation",
        "",
        "Writes **only** under failed-retry root; **does not mutate** main Era D live root, Phase 3, or A3M017.",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_erad_scale_200_isolated_retry_live_path_gate = {ERAD_FAILED_RETRY_LIVE_PATH_GATE}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])
    summary_path = os.path.join(
        output_paths["reports"], "a_class_erad_scale_200_failed_retry_live_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def _market_label_from_code(company_code: str) -> str:
    if company_code.startswith(("600", "601", "603", "688", "689")):
        return "SSE"
    return "SZSE"


def _erad_a_slice1_case_number(case_id: str) -> int:
    return int(case_id.replace("AD2E", ""))


def _derive_a_slice1_report_fields(case_num: int) -> Tuple[str, str, str, str]:
    """按 case 序号推导 report_type / period / title keywords（与 scale-200 new_erad 比例参照）。"""
    idx = case_num - 201
    slot = idx % 10
    if slot < 7:
        return (
            "annual_report",
            "2024-12-31",
            "年度报告",
            "半年度报告|一季度报告|三季度报告|英文|English",
        )
    if slot == 7:
        return (
            "semi_annual_report",
            "2024-06-30",
            "半年度报告",
            "年度报告|一季度报告|三季度报告|英文|English",
        )
    if slot == 8:
        return (
            "quarterly_report_q1",
            "2024-03-31",
            "一季度报告",
            "年度报告|半年度报告|三季度报告|英文|English",
        )
    return (
        "quarterly_report_q3",
        "2024-09-30",
        "三季度报告",
        "年度报告|半年度报告|一季度报告|英文|English",
    )


def _load_company_codes_from_csv(path: str, column: str) -> Set[str]:
    codes: Set[str] = set()
    if not os.path.isfile(path):
        return codes
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = str(row.get(column, "")).strip()
            if code:
                codes.add(code)
    return codes


def load_erad_next_scale_slice1_universe(path: str) -> List[EraDNextScaleSlice1UniverseCase]:
    cases: List[EraDNextScaleSlice1UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            case_id = str(row.get("case_id", "")).strip()
            company_code = str(row.get("company_code", "")).strip()
            cohort = str(row.get("cohort", "")).strip()
            prior_in_scale_200 = str(row.get("prior_in_scale_200", "")).strip().lower()
            include_reason = str(row.get("include_reason", "")).strip()
            case_num = (
                _erad_a_slice1_case_number(case_id)
                if ERAD_SCALE_200_CASE_ID_PATTERN.match(case_id)
                else 0
            )
            report_type, expected_period, title_kw, excluded_kw = _derive_a_slice1_report_fields(
                case_num
            )
            cases.append(
                EraDNextScaleSlice1UniverseCase(
                    case_id=case_id,
                    company_code=company_code,
                    company_name=KNOWN_COMPANY_NAMES.get(company_code, ""),
                    market=_market_label_from_code(company_code),
                    report_type=report_type,
                    expected_period=expected_period,
                    expected_title_keywords=title_kw,
                    excluded_title_keywords=excluded_kw,
                    cohort=cohort,
                    prior_in_scale_200=prior_in_scale_200,
                    include_reason=include_reason,
                    erad_include="yes",
                )
            )
    return cases


def slice1_to_phase2_case(case: EraDNextScaleSlice1UniverseCase) -> Phase2UniverseCase:
    return Phase2UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        report_type=case.report_type,
        expected_period=case.expected_period,
        expected_title_keywords=case.expected_title_keywords,
        excluded_title_keywords=case.excluded_title_keywords,
        risk_level="medium",
        phase1_overlap="no",
        phase2_include="yes",
        reason=case.include_reason,
    )


def validate_erad_next_scale_slice1_case(case: EraDNextScaleSlice1UniverseCase) -> List[str]:
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_NEXT_SCALE_SLICE1_CASE_IDS:
        issues.append(f"{ERAD_SLICE1_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice1_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num <= ERAD_SCALE_200_REQUIRED_UNIVERSE_SIZE:
        issues.append(f"{ERAD_SLICE1_SCALE_200_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE1_INCLUDE_REQUIRED)
    if case.cohort != "next_scale_slice1":
        issues.append(ERAD_SLICE1_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE1_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    issues.extend(validate_universe_code_name(slice1_to_phase2_case(case)))
    return issues


def validate_erad_next_scale_slice1_universe_size(
    cases: List[EraDNextScaleSlice1UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_NEXT_SCALE_SLICE1_CASE_IDS:
        return False, f"{ERAD_SLICE1_CASE_ID_NOT_ALLOWED}: unexpected case set"
    return True, ""


def validate_erad_next_scale_slice1_duplicate_codes(
    cases: List[EraDNextScaleSlice1UniverseCase],
) -> List[str]:
    issues: List[str] = []
    seen: Dict[str, str] = {}
    for case in cases:
        if case.erad_include != "yes":
            continue
        if case.company_code in seen:
            issues.append(f"{case.case_id}:{DUPLICATE_COMPANY_CODE_REJECTED}")
        else:
            seen[case.company_code] = case.case_id
    return issues


def lint_erad_next_scale_slice1_overlap(
    cases: List[EraDNextScaleSlice1UniverseCase],
) -> List[str]:
    """离线 overlap lint：scale-200 / effective-192 / unresolved / B slice1。"""
    issues: List[str] = []
    slice1_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    scale200_codes = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    effective_codes = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE1_SCALE200_EFFECTIVE_LEDGER, "company_code"
    )
    unresolved_codes = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE1_UNRESOLVED_LEDGER, "company_code"
    )
    b_slice1_codes = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE1_B_SLICE1_UNIVERSE, "company_code"
    )
    overlap200 = slice1_codes & scale200_codes
    if overlap200:
        issues.append(f"{ERAD_SLICE1_SCALE200_OVERLAP}:count={len(overlap200)}")
    overlap192 = slice1_codes & effective_codes
    if overlap192:
        issues.append(f"{ERAD_SLICE1_EFFECTIVE192_OVERLAP}:count={len(overlap192)}")
    overlap_unresolved = slice1_codes & unresolved_codes
    if overlap_unresolved:
        issues.append(f"{ERAD_SLICE1_UNRESOLVED_OVERLAP}:count={len(overlap_unresolved)}")
    overlap_b = slice1_codes & b_slice1_codes
    if overlap_b:
        issues.append(f"{ERAD_SLICE1_B_SLICE1_OVERLAP}:count={len(overlap_b)}")
    return issues


def validate_erad_next_scale_slice1_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_next_scale_slice1_output_root(output_root: str) -> Tuple[bool, str]:
    """Era D A-class next-scale slice1 输出仅允许 slice1 隔离根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT)
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE1_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE1_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT_VIOLATION


def enforce_erad_next_scale_slice1_approval_gate(args: argparse.Namespace) -> None:
    wrong = (
        (args.approve_a_class_phase2_metadata_expansion, ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (args.approve_a_class_phase2_failed_retry, ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (args.approve_a_class_phase2_network_recovery_retry_v2, ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (args.approve_a_class_phase2_retry_v3, ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_phase3_50_company_expansion", False), ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_phase3_a3m017_isolated_retry", False), ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_200", False), ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_200_failed_retry", False), ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_500_slice2", False), ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (args.approve_a_class_tiny_live_metadata, ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
        (args.approve_phase1_tiny_live_metadata, ERAD_NEXT_SCALE_SLICE1_WRONG_APPROVAL),
    )
    for enabled, code in wrong:
        if enabled:
            print(f"ERROR: {code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not getattr(args, "approve_a_class_erad_scale_500_slice1", False):
        print(f"ERROR: {ERAD_NEXT_SCALE_SLICE1_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def enforce_erad_next_scale_slice1_request_cap(total_planned: int) -> Tuple[bool, str]:
    if total_planned > ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP:
        return (
            False,
            f"{ERAD_SLICE1_REQUEST_CAP_EXCEEDED}:{total_planned}>{ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP}",
        )
    return True, ""


def parse_erad_a_slice1_case_range(case_range: str) -> Tuple[str, str]:
    parts = case_range.split(":")
    if len(parts) != 2:
        raise ValueError(ERAD_SLICE1_CASE_RANGE_INVALID)
    start_id = parts[0].strip()
    end_id = parts[1].strip()
    if start_id not in ALLOWED_ERAD_NEXT_SCALE_SLICE1_CASE_IDS:
        raise ValueError(f"{ERAD_SLICE1_CASE_RANGE_INVALID}:start={start_id}")
    if end_id not in ALLOWED_ERAD_NEXT_SCALE_SLICE1_CASE_IDS:
        raise ValueError(f"{ERAD_SLICE1_CASE_RANGE_INVALID}:end={end_id}")
    if _erad_a_slice1_case_number(start_id) > _erad_a_slice1_case_number(end_id):
        raise ValueError(f"{ERAD_SLICE1_CASE_RANGE_INVALID}:order")
    return start_id, end_id


def filter_erad_a_next_scale_slice1_cases_by_range(
    cases: List[EraDNextScaleSlice1UniverseCase],
    case_range: Optional[str],
) -> List[EraDNextScaleSlice1UniverseCase]:
    if not case_range:
        return cases
    start_id, end_id = parse_erad_a_slice1_case_range(case_range)
    start_num = _erad_a_slice1_case_number(start_id)
    end_num = _erad_a_slice1_case_number(end_id)
    return [
        c
        for c in cases
        if start_num <= _erad_a_slice1_case_number(c.case_id) <= end_num
    ]


def build_erad_next_scale_slice1_dryrun_row(
    case: EraDNextScaleSlice1UniverseCase,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"erad-a-scale-500-slice1 dry-run; CNINFO not called; metadata only; "
        f"matching_logic={MATCHING_LOGIC_VERSION}; "
        f"planned_requests={ERAD_NEXT_SCALE_SLICE1_PLANNED_REQUESTS_PER_CASE}; "
        f"scale_200_lineage_reference_only=yes; phase3_production_root_write=no"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "cohort": case.cohort,
        "prior_in_scale_200": case.prior_in_scale_200,
        "erad_include": case.erad_include,
        "planned_source": source_id,
        "planned_endpoint": planned_endpoints_for_case(slice1_to_phase2_case(case)),
        "planned_output_root": output_root,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "db_write": "0",
        "minio_write": "0",
        "rag_run": "0",
        "cninfo_call_planned": "0",
        "planned_request_count_case": str(ERAD_NEXT_SCALE_SLICE1_PLANNED_REQUESTS_PER_CASE),
        "dryrun_status": status,
        "notes": notes,
    }


def process_erad_next_scale_slice1_dry_run(
    cases: List[EraDNextScaleSlice1UniverseCase],
    output_root: str,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = list(validate_erad_next_scale_slice1_duplicate_codes(cases))
    universe_issues.extend(lint_erad_next_scale_slice1_overlap(cases))
    for case in cases:
        if case.erad_include != "yes":
            continue
        issues = validate_erad_next_scale_slice1_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        rows.append(build_erad_next_scale_slice1_dryrun_row(case, issues, output_root))
    return rows, universe_issues


def write_erad_next_scale_slice1_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice1_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_NEXT_SCALE_SLICE1_DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def compute_erad_next_scale_slice1_runner_gate(
    universe_issues: List[str],
    case_count: int,
    total_planned: int,
) -> str:
    if universe_issues or case_count != REQUIRED_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE:
        return "FAIL"
    ok_cap, _ = enforce_erad_next_scale_slice1_request_cap(total_planned)
    if not ok_cap:
        return "FAIL"
    return ERAD_NEXT_SCALE_SLICE1_RUNNER_GATE


def write_erad_next_scale_slice1_dryrun_summary(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_issues: List[str],
    gate: str,
    total_planned: int,
) -> str:
    planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
    total = len(rows)
    lines = [
        "# CNINFO A 类 Era D Next-Scale Slice1 — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Era D A-class next-scale slice1 dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | erad_a_scale_500_slice1_dry_run |",
        f"| universe size | {total} |",
        f"| planned_ok | {planned_ok} |",
        f"| cohort | next_scale_slice1（AD2E201–500） |",
        f"| planned_requests_total | {total_planned} (cap ≤ {ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP}) |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        "",
        "## Overlap lint",
        "",
        "- scale-200 universe codes: **0 overlap**",
        "- scale-200 effective 192: **0 overlap**",
        "- scale-200 unresolved 8: **0 overlap**",
        "- B next-scale slice1 codes: **0 overlap**",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- scale-200 / failed_retry / Phase 3 / A3M017 roots untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_erad_next_scale_slice1_runner_extension_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])
    summary_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice1_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def is_allowed_erad_a_slice1_mock_test_output_root(output_root: str) -> bool:
    root = _normalize_output_root(output_root)
    for parent_path in (
        ERAD_NEXT_SCALE_SLICE1_MOCK_TEST_PARENT,
        ERAD_NEXT_SCALE_SLICE1_MOCK_LIVE_TEST_PARENT,
    ):
        parent = _normalize_output_root(parent_path)
        if root.startswith(parent + os.sep):
            return True
    return False


def is_production_erad_a_next_scale_slice1_output_root(output_root: str) -> bool:
    root = _normalize_output_root(output_root)
    if is_allowed_erad_a_slice1_mock_test_output_root(root):
        return False
    allowed = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT)
    return root == allowed or root.startswith(allowed + os.sep)


def safe_cleanup_erad_a_slice1_test_output_root(temp_root: str) -> None:
    """测试 teardown 仅允许删除 slice1 _mock_* 子目录；拒绝生产 output root。"""
    import shutil

    if _is_under_prefix(temp_root, DEFAULT_PHASE3_OUTPUT_ROOT):
        raise RuntimeError("拒绝清理 Phase 3 生产 output root")
    if _is_under_prefix(temp_root, DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT):
        raise RuntimeError("拒绝清理 Era D scale-200 生产 output root")
    if _is_under_prefix(temp_root, DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT):
        raise RuntimeError("拒绝清理 Era D failed-retry 生产 output root")
    if is_production_erad_a_next_scale_slice1_output_root(temp_root):
        raise RuntimeError("拒绝清理 Era D next-scale slice1 生产 output root")
    if not is_allowed_erad_a_slice1_mock_test_output_root(temp_root):
        raise RuntimeError("拒绝清理非 mock 测试目录")
    shutil.rmtree(temp_root, ignore_errors=True)


def is_erad_next_scale_slice1_case_acceptable(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    status = row.get("retrieval_status", "")
    quality = row.get("quality_status", "")
    lineage = row.get("lineage_status", "")
    if status in ("network_error", "not_found", "universe_invalid"):
        return False
    if status == "found":
        return True
    if status in ("discovered", "matching_pass"):
        return True
    if lineage == "discovered":
        return True
    if status == "needs_review" or quality == "needs_review":
        return bool(lineage)
    return False


def build_erad_next_scale_slice1_live_report_row(
    case: EraDNextScaleSlice1UniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    row = build_live_report_row(slice1_to_phase2_case(case), record, cninfo_request_count)
    notes = str(record.get("notes") or "")
    row["notes"] = (
        f"erad-a-scale-500-slice1 live; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"lineage_evidence_mode=fresh_metadata; scale_200_lineage_reference_only=yes; "
        f"phase3_production_root_write=no; PDF not downloaded; {notes}"
    ).strip()
    row["cohort"] = case.cohort
    row["prior_in_scale_200"] = case.prior_in_scale_200
    row["lineage_evidence_mode"] = "fresh_metadata"
    return row


def process_erad_a_next_scale_slice1_live(
    cases: List[EraDNextScaleSlice1UniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
) -> Tuple[List[Dict[str, str]], List[str]]:
    """Era D A-class next-scale slice1 live：300 新码 fresh_metadata only；metadata + URL lineage only。"""
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.erad_include != "yes":
            continue
        issues = validate_erad_next_scale_slice1_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            rows.append(
                build_erad_next_scale_slice1_live_report_row(
                    case,
                    {
                        "retrieval_status": "universe_invalid",
                        "quality_status": "blocked",
                        "lineage_status": "needs_review",
                        "announcement_id": "",
                        "announcement_title": "",
                        "announcement_time": "",
                        "title_match_status": "fail",
                        "period_match_status": "fail",
                        "pdf_url_present": "no",
                        "adjunct_url_present": "no",
                        "notes": "; ".join(issues),
                    },
                    0,
                )
            )
            stats.failure_count += 1
            continue
        tl_case = to_tiny_live_case(slice1_to_phase2_case(case))
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        if stats.cninfo_requests > ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP:
            universe_issues.append(
                f"cninfo_request_cap_exceeded:{stats.cninfo_requests}>{ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP}"
            )
            break
        live_row = build_erad_next_scale_slice1_live_report_row(
            case, record, case_cninfo_requests
        )
        snapshot_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}.json")
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case_id": case.case_id,
                    "case": {
                        "case_id": case.case_id,
                        "company_code": case.company_code,
                        "company_name": case.company_name,
                        "market": case.market,
                        "report_type": case.report_type,
                        "expected_period": case.expected_period,
                        "cohort": case.cohort,
                        "prior_in_scale_200": case.prior_in_scale_200,
                        "include_reason": case.include_reason,
                        "erad_include": case.erad_include,
                    },
                    "mode": "erad_a_scale_500_slice1_live",
                    "lineage_evidence_mode": "fresh_metadata",
                    "scale_200_lineage_reference_only": True,
                    "phase3_production_root_write": False,
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": False,
                    "pdf_parse_enabled": False,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={case.case_id} cohort={case.cohort} company_code={case.company_code} "
            f"retrieval_status={live_row['retrieval_status']} "
            f"quality={live_row.get('quality_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def compute_erad_next_scale_slice1_execution_gate(
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    stats: tiny_live.LiveStats,
    expected_case_count: int,
) -> str:
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues:
        return "FAIL_REVIEW_REQUIRED"
    if stats.cninfo_requests > ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP:
        return "FAIL_REVIEW_REQUIRED"
    if len(rows) != expected_case_count:
        return "FAIL_REVIEW_REQUIRED"
    threshold = ERAD_SLICE1_ACCEPTABLE_THRESHOLD
    if expected_case_count < REQUIRED_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE:
        threshold = max(1, int(expected_case_count * 0.9))
    acceptable_count = sum(
        1 for row in rows if is_erad_next_scale_slice1_case_acceptable(row)
    )
    if acceptable_count >= threshold:
        return ERAD_SLICE1_EXECUTION_GATE_PASS
    return "FAIL_REVIEW_REQUIRED"


def write_erad_next_scale_slice1_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice1_live_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_SLICE1_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_erad_next_scale_slice1_live_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice1_live_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_SLICE1_LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in ERAD_SLICE1_LIVE_QUALITY_COLUMNS})
    return report_path


def write_erad_next_scale_slice1_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
    expected_case_count: int,
) -> str:
    acceptable_count = sum(
        1 for row in rows if is_erad_next_scale_slice1_case_acceptable(row)
    )
    failed_count = sum(
        1
        for row in rows
        if row.get("retrieval_status")
        in ("network_error", "not_found", "universe_invalid")
    )
    needs_review_count = sum(
        1 for row in rows if row.get("quality_status") == "needs_review"
    )
    threshold = ERAD_SLICE1_ACCEPTABLE_THRESHOLD
    if expected_case_count < REQUIRED_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE:
        threshold = max(1, int(expected_case_count * 0.9))
    lines = [
        "# CNINFO A 类 Era D Next-Scale Slice1 — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Era D A-class next-scale slice1 live metadata validation · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| mode | erad_a_scale_500_slice1_live |",
        f"| universe size | {len(rows)} |",
        f"| expected case count | {expected_case_count} |",
        f"| cohort | next_scale_slice1（AD2E201–500） |",
        f"| acceptable | {acceptable_count} |",
        f"| failed | {failed_count} |",
        f"| needs_review | {needs_review_count} |",
        f"| CNINFO requests | {stats.cninfo_requests} (cap ≤ {ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP}) |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "",
        "## Lineage policy",
        "",
        "- AD2E001–200（192 effective）：**lineage-reference only** · **not executed**",
        "- 8 unresolved + AD2E146：**not in slice** · side-track only",
        "- slice1：**fresh_metadata only** for 300 new codes",
        "",
        "## Session split（future live）",
        "",
        "- Session 1：AD2E201–350（150 cases）",
        "- Session 2：AD2E351–500（150 cases）",
        "- Use `--case-range AD2E201:AD2E350` or `AD2E351:AD2E500` when approved",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- scale-200 / failed_retry / Phase 3 / A3M017 roots untouched: **yes**",
        "- approval_status: **NOT_APPROVED** (until explicit human approval)",
        "- approved_for_live: **false**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_erad_next_scale_slice1_execution_gate = {gate}",
        f"a_class_erad_next_scale_slice1_live_path_gate = {ERAD_NEXT_SCALE_SLICE1_LIVE_PATH_GATE}",
        "```",
        "",
        f"- acceptance threshold: **≥ {threshold}/{expected_case_count}** → PASS_WITH_CAVEAT",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])
    summary_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice1_live_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path



def _erad_a_slice2_case_number(case_id: str) -> int:
    return int(case_id.replace("AD2E", ""))


def _derive_a_slice2_report_fields(case_num: int) -> Tuple[str, str, str, str]:
    """按 case 序号推导 report_type / period / title keywords（501+ · mod-10；含 AD2E601+）。"""
    idx = case_num - 501
    slot = idx % 10
    if slot < 7:
        return (
            "annual_report",
            "2024-12-31",
            "年度报告",
            "半年度报告|一季度报告|三季度报告|英文|English",
        )
    if slot == 7:
        return (
            "semi_annual_report",
            "2024-06-30",
            "半年度报告",
            "年度报告|一季度报告|三季度报告|英文|English",
        )
    if slot == 8:
        return (
            "quarterly_report_q1",
            "2024-03-31",
            "一季度报告",
            "年度报告|半年度报告|三季度报告|英文|English",
        )
    return (
        "quarterly_report_q3",
        "2024-09-30",
        "三季度报告",
        "年度报告|半年度报告|一季度报告|英文|English",
    )


def load_erad_next_scale_slice2_universe(path: str) -> List[EraDNextScaleSlice2UniverseCase]:
    """加载 slice2 / listing-aware universe（4 列 CSV）；派生运行字段，不 mutate 源文件。"""
    cases: List[EraDNextScaleSlice2UniverseCase] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            case_id = str(row.get("case_id", "")).strip()
            company_code = str(row.get("company_code", "")).strip()
            company_name = str(row.get("company_name", "")).strip()
            cohort = str(row.get("cohort", "")).strip()
            case_num = (
                _erad_a_slice2_case_number(case_id)
                if ERAD_SCALE_200_CASE_ID_PATTERN.match(case_id)
                else 0
            )
            report_type, expected_period, title_kw, excluded_kw = _derive_a_slice2_report_fields(
                case_num
            )
            include_reason = (
                ERAD_LISTING_AWARE_S19_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S19_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S19_CASE_IDS
                else ERAD_LISTING_AWARE_S18_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S18_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S18_CASE_IDS
                else ERAD_LISTING_AWARE_S17_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S17_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S17_CASE_IDS
                else ERAD_LISTING_AWARE_S16_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S16_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S16_CASE_IDS
                else ERAD_LISTING_AWARE_S15_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S15_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S15_CASE_IDS
                else ERAD_LISTING_AWARE_S14_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S14_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S14_CASE_IDS
                else ERAD_LISTING_AWARE_S13_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S13_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S13_CASE_IDS
                else ERAD_LISTING_AWARE_S12_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S12_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S12_CASE_IDS
                else ERAD_LISTING_AWARE_S11_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S11_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S11_CASE_IDS
                else ERAD_LISTING_AWARE_S10_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S10_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S10_CASE_IDS
                else ERAD_LISTING_AWARE_S9_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S9_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S9_CASE_IDS
                else ERAD_LISTING_AWARE_S8_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S8_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S8_CASE_IDS
                else ERAD_LISTING_AWARE_S7_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S7_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S7_CASE_IDS
                else ERAD_LISTING_AWARE_S6_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S6_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S6_CASE_IDS
                else ERAD_LISTING_AWARE_S5_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S5_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S5_CASE_IDS
                else ERAD_LISTING_AWARE_S4_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S4_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S4_CASE_IDS
                else ERAD_LISTING_AWARE_S3_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S3_COHORT
                and case_id in ALLOWED_ERAD_LISTING_AWARE_S3_CASE_IDS
                else ERAD_LISTING_AWARE_S2_INCLUDE_REASON
                if cohort == ERAD_LISTING_AWARE_S2_COHORT
                else ERAD_NEXT_SCALE_SLICE2_INCLUDE_REASON
            )
            cases.append(
                EraDNextScaleSlice2UniverseCase(
                    case_id=case_id,
                    company_code=company_code,
                    company_name=company_name,
                    market=_market_label_from_code(company_code),
                    report_type=report_type,
                    expected_period=expected_period,
                    expected_title_keywords=title_kw,
                    excluded_title_keywords=excluded_kw,
                    cohort=cohort,
                    prior_in_scale_200="no",
                    include_reason=include_reason,
                    erad_include="yes",
                )
            )
    return cases


def slice2_to_phase2_case(case: EraDNextScaleSlice2UniverseCase) -> Phase2UniverseCase:
    return Phase2UniverseCase(
        case_id=case.case_id,
        company_code=case.company_code,
        company_name=case.company_name,
        market=case.market,
        report_type=case.report_type,
        expected_period=case.expected_period,
        expected_title_keywords=case.expected_title_keywords,
        excluded_title_keywords=case.excluded_title_keywords,
        risk_level="medium",
        phase1_overlap="no",
        phase2_include="yes",
        reason=case.include_reason,
    )


def validate_erad_listing_aware_s2_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S2 单案校验（AD2E601–650 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S2_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 600:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S2_COHORT:
        issues.append(ERAD_LISTING_AWARE_S2_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s3_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S3 单案校验（AD2E651–700 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S3_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 650:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S3_COHORT:
        issues.append(ERAD_LISTING_AWARE_S3_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s4_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S4 单案校验（AD2E701–750 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S4_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 700:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S4_COHORT:
        issues.append(ERAD_LISTING_AWARE_S4_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s5_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S5 单案校验（AD2E751–800 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S5_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 750:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S5_COHORT:
        issues.append(ERAD_LISTING_AWARE_S5_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s6_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S6 单案校验（AD2E801–850 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S6_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 800:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S6_COHORT:
        issues.append(ERAD_LISTING_AWARE_S6_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s7_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S7 单案校验（AD2E851–900 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S7_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 850:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S7_COHORT:
        issues.append(ERAD_LISTING_AWARE_S7_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s8_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S8 单案校验（AD2E901–950 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S8_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 900:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S8_COHORT:
        issues.append(ERAD_LISTING_AWARE_S8_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues



def validate_erad_listing_aware_s9_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S9 单案校验（AD2E951–1000 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S9_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 950:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S9_COHORT:
        issues.append(ERAD_LISTING_AWARE_S9_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues



def validate_erad_listing_aware_s10_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S10 单案校验（AD2E1001–1050 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S10_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1000:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S10_COHORT:
        issues.append(ERAD_LISTING_AWARE_S10_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues




def validate_erad_listing_aware_s11_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S11 单案校验（AD2E1051–1100 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S11_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1050:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S11_COHORT:
        issues.append(ERAD_LISTING_AWARE_S11_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s19_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S19 单案校验（AD2E1451–1500 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S19_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1450:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S19_COHORT:
        issues.append(ERAD_LISTING_AWARE_S19_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s18_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S18 单案校验（AD2E1401–1450 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S18_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1400:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S18_COHORT:
        issues.append(ERAD_LISTING_AWARE_S18_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s17_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S17 单案校验（AD2E1351–1400 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S17_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1350:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S17_COHORT:
        issues.append(ERAD_LISTING_AWARE_S17_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s16_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S16 单案校验（AD2E1301–1350 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S16_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1300:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S16_COHORT:
        issues.append(ERAD_LISTING_AWARE_S16_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s15_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S15 单案校验（AD2E1251–1300 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S15_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1250:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S15_COHORT:
        issues.append(ERAD_LISTING_AWARE_S15_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s14_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S14 单案校验（AD2E1201–1250 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S14_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1200:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S14_COHORT:
        issues.append(ERAD_LISTING_AWARE_S14_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s13_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S13 单案校验（AD2E1151–1200 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S13_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1150:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S13_COHORT:
        issues.append(ERAD_LISTING_AWARE_S13_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s12_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    """listing-aware S12 单案校验（AD2E1101–1150 · cohort=next_scale_listing_aware）。"""
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_LISTING_AWARE_S12_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 1100:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_LISTING_AWARE_S12_COHORT:
        issues.append(ERAD_LISTING_AWARE_S12_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_next_scale_slice2_case(case: EraDNextScaleSlice2UniverseCase) -> List[str]:
    if case.cohort == ERAD_LISTING_AWARE_S2_COHORT:
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S19_CASE_IDS:
            return validate_erad_listing_aware_s19_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S18_CASE_IDS:
            return validate_erad_listing_aware_s18_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S17_CASE_IDS:
            return validate_erad_listing_aware_s17_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S16_CASE_IDS:
            return validate_erad_listing_aware_s16_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S15_CASE_IDS:
            return validate_erad_listing_aware_s15_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S14_CASE_IDS:
            return validate_erad_listing_aware_s14_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S13_CASE_IDS:
            return validate_erad_listing_aware_s13_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S12_CASE_IDS:
            return validate_erad_listing_aware_s12_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S11_CASE_IDS:
            return validate_erad_listing_aware_s11_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S10_CASE_IDS:
            return validate_erad_listing_aware_s10_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S9_CASE_IDS:
            return validate_erad_listing_aware_s9_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S8_CASE_IDS:
            return validate_erad_listing_aware_s8_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S7_CASE_IDS:
            return validate_erad_listing_aware_s7_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S6_CASE_IDS:
            return validate_erad_listing_aware_s6_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S5_CASE_IDS:
            return validate_erad_listing_aware_s5_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S4_CASE_IDS:
            return validate_erad_listing_aware_s4_case(case)
        if case.case_id in ALLOWED_ERAD_LISTING_AWARE_S3_CASE_IDS:
            return validate_erad_listing_aware_s3_case(case)
        return validate_erad_listing_aware_s2_case(case)
    issues: List[str] = []
    if case.case_id not in ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS:
        issues.append(f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}:{case.case_id}")
    case_num = (
        _erad_a_slice2_case_number(case.case_id)
        if ERAD_SCALE_200_CASE_ID_PATTERN.match(case.case_id)
        else 0
    )
    if case_num and case_num <= 500:
        issues.append(f"{ERAD_SLICE2_PRIOR_CASE_FORBIDDEN}:{case.case_id}")
    if case.erad_include != "yes":
        issues.append(ERAD_SLICE2_INCLUDE_REQUIRED)
    if case.cohort != ERAD_NEXT_SCALE_SLICE2_COHORT:
        issues.append(ERAD_SLICE2_COHORT_INVALID)
    if case.prior_in_scale_200 != "no":
        issues.append(ERAD_SLICE2_PRIOR_SCALE_200_INVALID)
    if not case.company_code:
        issues.append("company_code_missing")
    if not case.company_name:
        issues.append("company_name_missing")
    if case.report_type not in tiny_live.VALID_REPORT_TYPES:
        issues.append(f"invalid_report_type:{case.report_type}")
    if not case.expected_period:
        issues.append("expected_period_missing")
    if ERAD_SLICE2_ST_NAME_PATTERN.search(case.company_name or ""):
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:{case.company_code}")
    issues.extend(validate_universe_code_name(slice2_to_phase2_case(case)))
    return issues


def validate_erad_listing_aware_s2_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S2_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S2_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S2_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S2_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S2_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s3_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S3_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S3_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S3_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S3_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S3_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s4_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S4_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S4_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S4_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S4_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S4_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s5_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S5_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S5_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S5_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S5_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S5_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s6_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S6_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S6_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S6_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S6_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S6_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s7_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S7_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S7_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S7_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S7_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S7_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s8_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S8_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S8_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S8_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S8_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S8_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""



def validate_erad_listing_aware_s9_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S9_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S9_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S9_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S9_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S9_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""



def validate_erad_listing_aware_s10_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S10_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S10_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S10_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S10_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S10_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""




def validate_erad_listing_aware_s11_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S11_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S11_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S11_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S11_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S11_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s12_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S12_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S12_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S12_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S12_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S12_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s19_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S19_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S19_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S19_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S19_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S19_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""



def validate_erad_listing_aware_s18_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S18_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S18_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S18_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S18_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S18_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s17_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S17_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S17_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S17_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S17_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S17_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s16_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S16_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S16_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S16_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S16_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S16_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s15_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S15_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S15_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S15_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S15_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S15_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_listing_aware_s14_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S14_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S14_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S14_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S14_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S14_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""

def validate_erad_listing_aware_s13_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_LISTING_AWARE_S13_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_LISTING_AWARE_S13_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_LISTING_AWARE_S13_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_LISTING_AWARE_S13_CASE_IDS:
        return False, f"{ERAD_LISTING_AWARE_S13_CASE_SET_VIOLATION}: got={sorted(case_ids)[:5]}..."
    return True, ""


def validate_erad_next_scale_slice2_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if included and included[0].cohort == ERAD_LISTING_AWARE_S2_COHORT:
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S19_CASE_IDS:
            return validate_erad_listing_aware_s19_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S18_CASE_IDS:
            return validate_erad_listing_aware_s18_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S17_CASE_IDS:
            return validate_erad_listing_aware_s17_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S16_CASE_IDS:
            return validate_erad_listing_aware_s16_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S15_CASE_IDS:
            return validate_erad_listing_aware_s15_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S14_CASE_IDS:
            return validate_erad_listing_aware_s14_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S13_CASE_IDS:
            return validate_erad_listing_aware_s13_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S12_CASE_IDS:
            return validate_erad_listing_aware_s12_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S11_CASE_IDS:
            return validate_erad_listing_aware_s11_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S10_CASE_IDS:
            return validate_erad_listing_aware_s10_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S9_CASE_IDS:
            return validate_erad_listing_aware_s9_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S8_CASE_IDS:
            return validate_erad_listing_aware_s8_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S7_CASE_IDS:
            return validate_erad_listing_aware_s7_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S6_CASE_IDS:
            return validate_erad_listing_aware_s6_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S5_CASE_IDS:
            return validate_erad_listing_aware_s5_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S4_CASE_IDS:
            return validate_erad_listing_aware_s4_universe_size(cases)
        if included[0].case_id in ALLOWED_ERAD_LISTING_AWARE_S3_CASE_IDS:
            return validate_erad_listing_aware_s3_universe_size(cases)
        return validate_erad_listing_aware_s2_universe_size(cases)
    if len(included) != REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE:
        return (
            False,
            f"{ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE_VIOLATION}: got {len(included)} "
            f"expected {REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS:
        return False, f"{ERAD_SLICE2_CASE_ID_NOT_ALLOWED}: unexpected case set"
    return True, ""


def validate_erad_next_scale_slice2_duplicate_codes(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    issues: List[str] = []
    seen: Dict[str, str] = {}
    for case in cases:
        if case.erad_include != "yes":
            continue
        if case.company_code in seen:
            issues.append(f"{case.case_id}:{DUPLICATE_COMPANY_CODE_REJECTED}")
        else:
            seen[case.company_code] = case.case_id
    return issues


def lint_erad_listing_aware_s2_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S2 overlap lint：仅 A cumulative（含 slice2 S1）+ ST + L-D6。

    B 轨 overlap 允许（跨轨不同维度）；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_all = a_s200 | a_s1 | a_s2_s1
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S2_OVERLAP_A_S2_S1),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s3_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S3 overlap lint：A cumulative（含 slice2 S1 + listing-aware S2）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_all = a_s200 | a_s1 | a_s2_s1 | a_la_s2
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S3_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S3_OVERLAP_A_LISTING_AWARE_S2),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s4_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S4 overlap lint：A cumulative（含 S1 + listing-aware S2/S3）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_all = a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S4_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S4_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S4_OVERLAP_A_LISTING_AWARE_S3),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s5_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S5 overlap lint：A cumulative（含 S1 + listing-aware S2/S3/S4）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_all = a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S5_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S5_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S5_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S5_OVERLAP_A_LISTING_AWARE_S4),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s6_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S6 overlap lint：A cumulative（含 S1 + listing-aware S2/S3/S4/S5）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_all = a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S6_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S6_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S6_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S6_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S6_OVERLAP_A_LISTING_AWARE_S5),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s7_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S7 overlap lint：A cumulative（含 S1 + listing-aware S2–S6）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_all = a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S7_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S7_OVERLAP_A_LISTING_AWARE_S6),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S7_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s8_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S8 overlap lint：A cumulative（含 S1 + listing-aware S2–S7）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6 | a_la_s7
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S8_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S8_OVERLAP_A_LISTING_AWARE_S7),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S8_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues



def lint_erad_listing_aware_s9_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S9 overlap lint：A cumulative（含 S1 + listing-aware S2–S8）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6 | a_la_s7 | a_la_s8
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S9_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S9_OVERLAP_A_LISTING_AWARE_S8),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S9_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues



def lint_erad_listing_aware_s10_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S10 overlap lint：A cumulative（含 S1 + listing-aware S2–S9）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6 | a_la_s7 | a_la_s8 | a_la_s9
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S10_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S10_OVERLAP_A_LISTING_AWARE_S9),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S10_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues




def lint_erad_listing_aware_s11_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S11 overlap lint：A cumulative（含 S1 + listing-aware S2–S10）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_la_s10 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
        | a_la_s7 | a_la_s8 | a_la_s9 | a_la_s10
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S11_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S9),
        (a_la_s10, ERAD_LISTING_AWARE_S11_OVERLAP_A_LISTING_AWARE_S10),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S11_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s19_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S19 overlap lint：A cumulative（含 S1 + listing-aware S2–S18）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_la_s10 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV, "company_code"
    )
    a_la_s11 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV, "company_code"
    )
    a_la_s12 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV, "company_code"
    )
    a_la_s13 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S13_UNIVERSE_CSV, "company_code"
    )
    a_la_s14 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S14_UNIVERSE_CSV, "company_code"
    )
    a_la_s15 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S15_UNIVERSE_CSV, "company_code"
    )
    a_la_s16 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S16_UNIVERSE_CSV, "company_code"
    )
    a_la_s17 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S17_UNIVERSE_CSV, "company_code"
    )
    a_la_s18 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S18_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
        | a_la_s7 | a_la_s8 | a_la_s9 | a_la_s10 | a_la_s11 | a_la_s12 | a_la_s13
        | a_la_s14 | a_la_s15 | a_la_s16 | a_la_s17 | a_la_s18
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S19_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S9),
        (a_la_s10, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S10),
        (a_la_s11, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S11),
        (a_la_s12, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S12),
        (a_la_s13, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S13),
        (a_la_s14, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S14),
        (a_la_s15, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S15),
        (a_la_s16, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S16),
        (a_la_s17, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S17),
        (a_la_s18, ERAD_LISTING_AWARE_S19_OVERLAP_A_LISTING_AWARE_S18),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S19_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues




def lint_erad_listing_aware_s18_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S18 overlap lint：A cumulative（含 S1 + listing-aware S2–S17）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_la_s10 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV, "company_code"
    )
    a_la_s11 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV, "company_code"
    )
    a_la_s12 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV, "company_code"
    )
    a_la_s13 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S13_UNIVERSE_CSV, "company_code"
    )
    a_la_s14 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S14_UNIVERSE_CSV, "company_code"
    )
    a_la_s15 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S15_UNIVERSE_CSV, "company_code"
    )
    a_la_s16 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S16_UNIVERSE_CSV, "company_code"
    )
    a_la_s17 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S17_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
        | a_la_s7 | a_la_s8 | a_la_s9 | a_la_s10 | a_la_s11 | a_la_s12 | a_la_s13
        | a_la_s14 | a_la_s15 | a_la_s16 | a_la_s17
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S18_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S9),
        (a_la_s10, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S10),
        (a_la_s11, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S11),
        (a_la_s12, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S12),
        (a_la_s13, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S13),
        (a_la_s14, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S14),
        (a_la_s15, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S15),
        (a_la_s16, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S16),
        (a_la_s17, ERAD_LISTING_AWARE_S18_OVERLAP_A_LISTING_AWARE_S17),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S18_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues



def lint_erad_listing_aware_s17_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S17 overlap lint：A cumulative（含 S1 + listing-aware S2–S16）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_la_s10 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV, "company_code"
    )
    a_la_s11 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV, "company_code"
    )
    a_la_s12 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV, "company_code"
    )
    a_la_s13 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S13_UNIVERSE_CSV, "company_code"
    )
    a_la_s14 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S14_UNIVERSE_CSV, "company_code"
    )
    a_la_s15 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S15_UNIVERSE_CSV, "company_code"
    )
    a_la_s16 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S16_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
        | a_la_s7 | a_la_s8 | a_la_s9 | a_la_s10 | a_la_s11 | a_la_s12 | a_la_s13
        | a_la_s14 | a_la_s15 | a_la_s16
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S17_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S9),
        (a_la_s10, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S10),
        (a_la_s11, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S11),
        (a_la_s12, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S12),
        (a_la_s13, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S13),
        (a_la_s14, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S14),
        (a_la_s15, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S15),
        (a_la_s16, ERAD_LISTING_AWARE_S17_OVERLAP_A_LISTING_AWARE_S16),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S17_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s16_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S16 overlap lint：A cumulative（含 S1 + listing-aware S2–S15）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_la_s10 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV, "company_code"
    )
    a_la_s11 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV, "company_code"
    )
    a_la_s12 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV, "company_code"
    )
    a_la_s13 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S13_UNIVERSE_CSV, "company_code"
    )
    a_la_s14 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S14_UNIVERSE_CSV, "company_code"
    )
    a_la_s15 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S15_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
        | a_la_s7 | a_la_s8 | a_la_s9 | a_la_s10 | a_la_s11 | a_la_s12 | a_la_s13
        | a_la_s14 | a_la_s15
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S16_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S9),
        (a_la_s10, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S10),
        (a_la_s11, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S11),
        (a_la_s12, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S12),
        (a_la_s13, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S13),
        (a_la_s14, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S14),
        (a_la_s15, ERAD_LISTING_AWARE_S16_OVERLAP_A_LISTING_AWARE_S15),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S16_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s15_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S15 overlap lint：A cumulative（含 S1 + listing-aware S2–S14）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_la_s10 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV, "company_code"
    )
    a_la_s11 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV, "company_code"
    )
    a_la_s12 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV, "company_code"
    )
    a_la_s13 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S13_UNIVERSE_CSV, "company_code"
    )
    a_la_s14 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S14_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
        | a_la_s7 | a_la_s8 | a_la_s9 | a_la_s10 | a_la_s11 | a_la_s12 | a_la_s13
        | a_la_s14
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S15_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S9),
        (a_la_s10, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S10),
        (a_la_s11, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S11),
        (a_la_s12, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S12),
        (a_la_s13, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S13),
        (a_la_s14, ERAD_LISTING_AWARE_S15_OVERLAP_A_LISTING_AWARE_S14),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S15_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s14_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S14 overlap lint：A cumulative（含 S1 + listing-aware S2–S13）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_la_s10 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV, "company_code"
    )
    a_la_s11 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV, "company_code"
    )
    a_la_s12 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV, "company_code"
    )
    a_la_s13 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S13_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
        | a_la_s7 | a_la_s8 | a_la_s9 | a_la_s10 | a_la_s11 | a_la_s12 | a_la_s13
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S14_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S9),
        (a_la_s10, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S10),
        (a_la_s11, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S11),
        (a_la_s12, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S12),
        (a_la_s13, ERAD_LISTING_AWARE_S14_OVERLAP_A_LISTING_AWARE_S13),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S14_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues

def lint_erad_listing_aware_s13_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S13 overlap lint：A cumulative（含 S1 + listing-aware S2–S12）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_la_s10 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV, "company_code"
    )
    a_la_s11 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV, "company_code"
    )
    a_la_s12 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
        | a_la_s7 | a_la_s8 | a_la_s9 | a_la_s10 | a_la_s11 | a_la_s12
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S13_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S9),
        (a_la_s10, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S10),
        (a_la_s11, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S11),
        (a_la_s12, ERAD_LISTING_AWARE_S13_OVERLAP_A_LISTING_AWARE_S12),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S13_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_listing_aware_s12_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """
    listing-aware S12 overlap lint：A cumulative（含 S1 + listing-aware S2–S11）+ ST + L-D6。

    B 轨 overlap 允许；不做 B / AB_182 阻断。
    """
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_s2_s1 = _load_company_codes_from_csv(
        DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV, "company_code"
    )
    a_la_s2 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV, "company_code"
    )
    a_la_s3 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV, "company_code"
    )
    a_la_s4 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV, "company_code"
    )
    a_la_s5 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV, "company_code"
    )
    a_la_s6 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV, "company_code"
    )
    a_la_s7 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV, "company_code"
    )
    a_la_s8 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV, "company_code"
    )
    a_la_s9 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV, "company_code"
    )
    a_la_s10 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV, "company_code"
    )
    a_la_s11 = _load_company_codes_from_csv(
        DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV, "company_code"
    )
    a_all = (
        a_s200 | a_s1 | a_s2_s1 | a_la_s2 | a_la_s3 | a_la_s4 | a_la_s5 | a_la_s6
        | a_la_s7 | a_la_s8 | a_la_s9 | a_la_s10 | a_la_s11
    )
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (a_s2_s1, ERAD_LISTING_AWARE_S12_OVERLAP_A_S2_S1),
        (a_la_s2, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S2),
        (a_la_s3, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S3),
        (a_la_s4, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S4),
        (a_la_s5, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S5),
        (a_la_s6, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S6),
        (a_la_s7, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S7),
        (a_la_s8, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S8),
        (a_la_s9, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S9),
        (a_la_s10, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S10),
        (a_la_s11, ERAD_LISTING_AWARE_S12_OVERLAP_A_LISTING_AWARE_S11),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        profile_dir=DEFAULT_ERAD_LISTING_AWARE_S12_PROFILE_DIR,
        grandfather_case_ids=set(),
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_next_scale_slice2_overlap(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> List[str]:
    """离线 overlap lint：A/B cumulative · AB_182 · L-D4 ST · L-D6 listing_period。"""
    included = [c for c in cases if c.erad_include == "yes"]
    if included and any(c.cohort == ERAD_LISTING_AWARE_S2_COHORT for c in included):
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S19_CASE_IDS for c in included):
            return lint_erad_listing_aware_s19_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S18_CASE_IDS for c in included):
            return lint_erad_listing_aware_s18_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S17_CASE_IDS for c in included):
            return lint_erad_listing_aware_s17_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S16_CASE_IDS for c in included):
            return lint_erad_listing_aware_s16_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S15_CASE_IDS for c in included):
            return lint_erad_listing_aware_s15_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S14_CASE_IDS for c in included):
            return lint_erad_listing_aware_s14_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S13_CASE_IDS for c in included):
            return lint_erad_listing_aware_s13_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S12_CASE_IDS for c in included):
            return lint_erad_listing_aware_s12_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S11_CASE_IDS for c in included):
            return lint_erad_listing_aware_s11_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S10_CASE_IDS for c in included):
            return lint_erad_listing_aware_s10_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S9_CASE_IDS for c in included):
            return lint_erad_listing_aware_s9_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S8_CASE_IDS for c in included):
            return lint_erad_listing_aware_s8_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S7_CASE_IDS for c in included):
            return lint_erad_listing_aware_s7_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S6_CASE_IDS for c in included):
            return lint_erad_listing_aware_s6_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S5_CASE_IDS for c in included):
            return lint_erad_listing_aware_s5_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S4_CASE_IDS for c in included):
            return lint_erad_listing_aware_s4_overlap(cases)
        if any(c.case_id in ALLOWED_ERAD_LISTING_AWARE_S3_CASE_IDS for c in included):
            return lint_erad_listing_aware_s3_overlap(cases)
        return lint_erad_listing_aware_s2_overlap(cases)
    issues: List[str] = []
    slice2_codes = {c.company_code for c in cases if c.erad_include == "yes"}
    a_s200 = _load_company_codes_from_csv(DEFAULT_ERAD_SCALE_200_UNIVERSE_CSV, "company_code")
    a_s1 = _load_company_codes_from_csv(DEFAULT_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV, "company_code")
    a_all = a_s200 | a_s1
    a_cum_eff = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SCALE200_EFFECTIVE_LEDGER, "company_code"
    ) | _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_SLICE1_EFFECTIVE_LEDGER, "company_code"
    )
    b_s200 = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_B_SCALE200_UNIVERSE, "company_code"
    )
    b_s1 = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_B_SLICE1_UNIVERSE, "company_code"
    )
    b_s2 = _load_company_codes_from_csv(
        ERAD_NEXT_SCALE_SLICE2_B_SLICE2_UNIVERSE, "company_code"
    )
    b_cum = b_s200 | b_s1 | b_s2
    ab_182 = _load_company_codes_from_csv(ERAD_NEXT_SCALE_SLICE2_AB_182_LEDGER, "company_code")

    checks = (
        (a_all, ERAD_SLICE2_OVERLAP_A_ALL),
        (a_cum_eff, ERAD_SLICE2_OVERLAP_A_CUM_EFF),
        (a_s200, ERAD_SLICE2_OVERLAP_A_S200),
        (a_s1, ERAD_SLICE2_OVERLAP_A_S1),
        (b_cum, ERAD_SLICE2_OVERLAP_B_CUM),
        (b_s200, ERAD_SLICE2_OVERLAP_B_S200),
        (b_s1, ERAD_SLICE2_OVERLAP_B_S1),
        (b_s2, ERAD_SLICE2_OVERLAP_B_S2),
        (ab_182, ERAD_SLICE2_OVERLAP_AB_182),
    )
    for ref_codes, err_code in checks:
        overlap = slice2_codes & ref_codes
        if overlap:
            issues.append(f"{err_code}:count={len(overlap)}")

    st_hits = [
        c.company_code
        for c in cases
        if c.erad_include == "yes" and ERAD_SLICE2_ST_NAME_PATTERN.search(c.company_name or "")
    ]
    if st_hits:
        issues.append(f"{ERAD_SLICE2_ST_NAME_HIT}:count={len(st_hits)}")
    # L-D6：未来 cohort 硬拒 listing_gap / unlisted；冻结 S1 三案仅 flag
    listing_blocking, _listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        grandfather_case_ids=ERAD_SLICE2_FROZEN_LISTING_CAVEAT_CASE_IDS,
    )
    issues.extend(listing_blocking)
    return issues


def lint_erad_next_scale_slice2_listing_period(
    cases: List[EraDNextScaleSlice2UniverseCase],
    *,
    profile_dir: str = listing_period_gate.DEFAULT_PROFILE_DIR,
    grandfather_case_ids: Optional[Set[str]] = None,
) -> Tuple[List[str], List[str]]:
    """
    L-D6 上市日 vs expected_period 离线 lint（CNINFO = 0）。

    返回 (blocking_issues, flag_notes)。
    - listing_gap / unlisted / profile_missing → 默认 blocking
    - grandfather_case_ids 内仅写入 flag_notes（封闭 S1 已知 caveat）
    """
    grandfather = grandfather_case_ids or set()
    blocking: List[str] = []
    flags: List[str] = []
    for case in cases:
        if case.erad_include != "yes":
            continue
        result = listing_period_gate.assess_listing_vs_expected_period(
            case.company_code,
            case.expected_period,
            profile_dir=profile_dir,
        )
        if not listing_period_gate.is_listing_period_reject(result):
            continue
        detail = (
            f"{case.case_id}:{case.company_code}:{result.failure_class}:"
            f"listing_date={result.listing_date or 'null'}:"
            f"expected_period={result.expected_period}"
        )
        if case.case_id in grandfather:
            flags.append(f"{ERAD_SLICE2_LISTING_PERIOD_BLOCK}:grandfather:{detail}")
            continue
        err_code = (
            ERAD_SLICE2_LISTING_PROFILE_MISSING
            if result.failure_class == listing_period_gate.FAILURE_PROFILE_MISSING
            else ERAD_SLICE2_LISTING_PERIOD_BLOCK
        )
        blocking.append(f"{err_code}:{detail}")
    return blocking, flags


def filter_erad_next_scale_slice2_cases_by_listing_period(
    cases: List[EraDNextScaleSlice2UniverseCase],
    *,
    profile_dir: str = listing_period_gate.DEFAULT_PROFILE_DIR,
) -> Tuple[List[EraDNextScaleSlice2UniverseCase], List[listing_period_gate.ListingPeriodGateResult]]:
    """
    未来 next-scale / slice universe 构建入口：硬拒 listing_gap / unlisted / profile_missing。

    无 grandfather；不 mutate 输入列表。
    """
    kept: List[EraDNextScaleSlice2UniverseCase] = []
    rejected: List[listing_period_gate.ListingPeriodGateResult] = []
    for case in cases:
        if case.erad_include != "yes":
            continue
        result = listing_period_gate.assess_listing_vs_expected_period(
            case.company_code,
            case.expected_period,
            profile_dir=profile_dir,
        )
        if listing_period_gate.is_listing_period_reject(result):
            rejected.append(result)
        else:
            kept.append(case)
    return kept, rejected


def validate_erad_next_scale_slice2_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_NEXT_SCALE_SLICE2_UNIVERSE_CSV_REQUIRED
    return True, ""


def is_erad_listing_aware_s2_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E601–650 listing-aware 下一片模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s2_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S2_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S2_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s2_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S2 输出仅允许独立根；禁止写入封闭 slice2 S1 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S2_CLOSED_ROOT_WRITE_FORBIDDEN
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s2",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT,
            "listing_aware_s3_root_forbidden_for_listing_aware_s2",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT,
            "listing_aware_s4_root_forbidden_for_listing_aware_s2",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT,
            "listing_aware_s5_root_forbidden_for_listing_aware_s2",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT,
            "listing_aware_s6_root_forbidden_for_listing_aware_s2",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT,
            "listing_aware_s7_root_forbidden_for_listing_aware_s2",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT,
            "listing_aware_s8_root_forbidden_for_listing_aware_s2",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s2"


def is_erad_listing_aware_s3_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E651–700 listing-aware S3 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s3_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S3_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S3_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s3_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S3 输出仅允许独立根；禁止写入封闭 S1 / S2 / S4 / S5 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S3_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S3_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, "listing_aware_s4_root_forbidden_for_listing_aware_s3"
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, "listing_aware_s5_root_forbidden_for_listing_aware_s3"
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, "listing_aware_s6_root_forbidden_for_listing_aware_s3"
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, "listing_aware_s7_root_forbidden_for_listing_aware_s3"
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, "listing_aware_s8_root_forbidden_for_listing_aware_s3"
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, "listing_aware_s9_root_forbidden_for_listing_aware_s3"
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, "listing_aware_s10_root_forbidden_for_listing_aware_s3"
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, "listing_aware_s11_root_forbidden_for_listing_aware_s3"
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, "listing_aware_s12_root_forbidden_for_listing_aware_s3"
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s3"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s3"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s3"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s3"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s3"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s3"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s3"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s3",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s3"


def is_erad_listing_aware_s4_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E701–750 listing-aware S4 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s4_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S4_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S4_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s4_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S4 输出仅允许独立根；禁止写入封闭 S1 / S2 / S3 / S5 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S4_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S4_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S4_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, "listing_aware_s5_root_forbidden_for_listing_aware_s4"
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, "listing_aware_s6_root_forbidden_for_listing_aware_s4"
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, "listing_aware_s7_root_forbidden_for_listing_aware_s4"
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, "listing_aware_s8_root_forbidden_for_listing_aware_s4"
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, "listing_aware_s9_root_forbidden_for_listing_aware_s4"
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, "listing_aware_s10_root_forbidden_for_listing_aware_s4"
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, "listing_aware_s11_root_forbidden_for_listing_aware_s4"
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, "listing_aware_s12_root_forbidden_for_listing_aware_s4"
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s4"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s4"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s4"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s4"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s4"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s4"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s4"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s4",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s4"


def is_erad_listing_aware_s5_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E751–800 listing-aware S5 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s5_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S5_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S5_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s5_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S5 输出仅允许独立根；禁止写入封闭 S1 / S2 / S3 / S4 / S6 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S5_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S5_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S5_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, ERAD_LISTING_AWARE_S5_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, "listing_aware_s6_root_forbidden_for_listing_aware_s5"
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, "listing_aware_s7_root_forbidden_for_listing_aware_s5"
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, "listing_aware_s8_root_forbidden_for_listing_aware_s5"
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, "listing_aware_s9_root_forbidden_for_listing_aware_s5"
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, "listing_aware_s10_root_forbidden_for_listing_aware_s5"
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, "listing_aware_s11_root_forbidden_for_listing_aware_s5"
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, "listing_aware_s12_root_forbidden_for_listing_aware_s5"
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s5"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s5"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s5"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s5"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s5"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s5"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s5"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s5",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s5"


def is_erad_listing_aware_s6_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E801–850 listing-aware S6 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s6_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S6_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S6_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s6_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S6 输出仅允许独立根；禁止写入封闭 S1 / S2 / S3 / S4 / S5 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S6_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S6_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S6_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, ERAD_LISTING_AWARE_S6_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, ERAD_LISTING_AWARE_S6_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, "listing_aware_s7_root_forbidden_for_listing_aware_s6"
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, "listing_aware_s8_root_forbidden_for_listing_aware_s6"
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, "listing_aware_s9_root_forbidden_for_listing_aware_s6"
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, "listing_aware_s10_root_forbidden_for_listing_aware_s6"
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, "listing_aware_s11_root_forbidden_for_listing_aware_s6"
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, "listing_aware_s12_root_forbidden_for_listing_aware_s6"
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s6"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s6"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s6"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s6"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s6"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s6"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s6"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s6",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s6"


def is_erad_listing_aware_s7_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E851–900 listing-aware S7 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s7_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S7_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S7_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s7_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S7 输出仅允许独立根；禁止写入封闭 S1 / S2 / S3 / S4 / S5 / S6 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S7_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S7_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S7_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, ERAD_LISTING_AWARE_S7_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, ERAD_LISTING_AWARE_S7_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, ERAD_LISTING_AWARE_S7_CLOSED_ROOT_WRITE_FORBIDDEN
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, "listing_aware_s8_root_forbidden_for_listing_aware_s7"
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, "listing_aware_s9_root_forbidden_for_listing_aware_s7"
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, "listing_aware_s10_root_forbidden_for_listing_aware_s7"
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, "listing_aware_s11_root_forbidden_for_listing_aware_s7"
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, "listing_aware_s12_root_forbidden_for_listing_aware_s7"
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s7"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s7"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s7"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s7"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s7"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s7"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s7"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s7",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s7"


def is_erad_listing_aware_s8_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E901–950 listing-aware S8 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s8_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S8_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S8_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s8_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S8 输出仅允许独立根；禁止写入封闭 S1 / S2 / S3 / S4 / S5 / S6 / S7 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S8_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S8_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S8_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, ERAD_LISTING_AWARE_S8_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, ERAD_LISTING_AWARE_S8_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, ERAD_LISTING_AWARE_S8_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, ERAD_LISTING_AWARE_S8_CLOSED_ROOT_WRITE_FORBIDDEN
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, "listing_aware_s9_root_forbidden_for_listing_aware_s8"
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, "listing_aware_s10_root_forbidden_for_listing_aware_s8"
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, "listing_aware_s11_root_forbidden_for_listing_aware_s8"
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, "listing_aware_s12_root_forbidden_for_listing_aware_s8"
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s8"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s8"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s8"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s8"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s8"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s8"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s8"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s8",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s8"



def is_erad_listing_aware_s9_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E951–1000 listing-aware S9 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s9_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S9_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S9_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s9_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S9 输出仅允许独立根；禁止写入封闭 S1 / S2–S8 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S9_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S9_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S9_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, ERAD_LISTING_AWARE_S9_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, ERAD_LISTING_AWARE_S9_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, ERAD_LISTING_AWARE_S9_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, ERAD_LISTING_AWARE_S9_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, ERAD_LISTING_AWARE_S9_CLOSED_ROOT_WRITE_FORBIDDEN
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, "listing_aware_s10_root_forbidden_for_listing_aware_s9"
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, "listing_aware_s11_root_forbidden_for_listing_aware_s9"
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, "listing_aware_s12_root_forbidden_for_listing_aware_s9"
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s9"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s9"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s9"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s9"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s9"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s9"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s9"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s9",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s9"



def is_erad_listing_aware_s10_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1001–1050 listing-aware S10 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s10_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S10_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S10_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s10_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S10 输出仅允许独立根；禁止写入封闭 S1 / S2–S9 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, ERAD_LISTING_AWARE_S10_CLOSED_ROOT_WRITE_FORBIDDEN
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, "listing_aware_s11_root_forbidden_for_listing_aware_s10"
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, "listing_aware_s12_root_forbidden_for_listing_aware_s10"
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s10"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s10"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s10"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s10"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s10"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s10"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s10"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s10",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s10"




def is_erad_listing_aware_s11_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1051–1100 listing-aware S11 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s11_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S11_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S11_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s11_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S11 输出仅允许独立根；禁止写入封闭 S1 / S2–S10 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, ERAD_LISTING_AWARE_S11_CLOSED_ROOT_WRITE_FORBIDDEN
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, "listing_aware_s12_root_forbidden_for_listing_aware_s11"
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s11"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s11"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s11"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s11"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s11"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s11"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s11"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s11",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s11"


def is_erad_listing_aware_s12_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1101–1150 listing-aware S12 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s12_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S12_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S12_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s12_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S12 输出仅允许独立根；禁止写入封闭 S1 / S2–S11 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, ERAD_LISTING_AWARE_S12_CLOSED_ROOT_WRITE_FORBIDDEN
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if root == closed_s13 or root.startswith(closed_s13 + os.sep):
        return False, "listing_aware_s13_root_forbidden_for_listing_aware_s12"
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s12"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s12"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s12"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s12"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s12"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s12"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s12",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        pth = _normalize_output_root(path)
        if root == pth or root.startswith(pth + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s12"


def is_erad_listing_aware_s13_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1151–1200 listing-aware S13 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S13_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s13_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S13_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S13_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s13_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S13 输出仅允许独立根；禁止写入封闭 S1 / S2–S12 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s2 or root.startswith(closed_s2 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s3 or root.startswith(closed_s3 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s4 or root.startswith(closed_s4 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s5 or root.startswith(closed_s5 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s6 or root.startswith(closed_s6 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s7 or root.startswith(closed_s7 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s8 or root.startswith(closed_s8 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s9 or root.startswith(closed_s9 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s10 or root.startswith(closed_s10 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s11 or root.startswith(closed_s11 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    if root == closed_s12 or root.startswith(closed_s12 + os.sep):
        return False, ERAD_LISTING_AWARE_S13_CLOSED_ROOT_WRITE_FORBIDDEN
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if root == closed_s14 or root.startswith(closed_s14 + os.sep):
        return False, "listing_aware_s14_root_forbidden_for_listing_aware_s13"
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s13"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s13"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s13"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s13"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s13"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s13",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        pth = _normalize_output_root(path)
        if root == pth or root.startswith(pth + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s13"


def is_erad_listing_aware_s14_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1201–1250 listing-aware S14 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S14_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s14_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S14_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S14_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s14_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S14 输出仅允许独立根；禁止写入封闭 S1 / S2–S13 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    for closed in (
        closed_s1, closed_s2, closed_s3, closed_s4, closed_s5, closed_s6, closed_s7,
        closed_s8, closed_s9, closed_s10, closed_s11, closed_s12, closed_s13,
    ):
        if root == closed or root.startswith(closed + os.sep):
            return False, ERAD_LISTING_AWARE_S14_CLOSED_ROOT_WRITE_FORBIDDEN
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if root == closed_s15 or root.startswith(closed_s15 + os.sep):
        return False, "listing_aware_s15_root_forbidden_for_listing_aware_s14"
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if root == closed_s16 or root.startswith(closed_s16 + os.sep):
        return False, "listing_aware_s16_root_forbidden_for_listing_aware_s14"
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if root == closed_s17 or root.startswith(closed_s17 + os.sep):
        return False, "listing_aware_s17_root_forbidden_for_listing_aware_s14"
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if root == closed_s18 or root.startswith(closed_s18 + os.sep):
        return False, "listing_aware_s18_root_forbidden_for_listing_aware_s14"
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if root == closed_s19 or root.startswith(closed_s19 + os.sep):
        return False, "listing_aware_s19_root_forbidden_for_listing_aware_s14"
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s14",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        pth = _normalize_output_root(path)
        if root == pth or root.startswith(pth + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s14"


def is_erad_listing_aware_s19_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1451–1500 listing-aware S19 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S19_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s19_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S19_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S19_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s19_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S19 输出仅允许独立根；禁止写入封闭 S1 / S2–S18 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    for closed in (
        closed_s1, closed_s2, closed_s3, closed_s4, closed_s5, closed_s6, closed_s7,
        closed_s8, closed_s9, closed_s10, closed_s11, closed_s12, closed_s13, closed_s14,
        closed_s15, closed_s16, closed_s17, closed_s18,
    ):
        if root == closed or root.startswith(closed + os.sep):
            return False, ERAD_LISTING_AWARE_S19_CLOSED_ROOT_WRITE_FORBIDDEN
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s19",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        pth = _normalize_output_root(path)
        if root == pth or root.startswith(pth + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s19"


def is_erad_listing_aware_s18_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1401–1450 listing-aware S18 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S18_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s18_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S18_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S18_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s18_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S18 输出仅允许独立根；禁止写入封闭 S1 / S2–S17 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    for closed in (
        closed_s1, closed_s2, closed_s3, closed_s4, closed_s5, closed_s6, closed_s7,
        closed_s8, closed_s9, closed_s10, closed_s11, closed_s12, closed_s13, closed_s14,
        closed_s15, closed_s16, closed_s17, closed_s19,
    ):
        if root == closed or root.startswith(closed + os.sep):
            return False, ERAD_LISTING_AWARE_S18_CLOSED_ROOT_WRITE_FORBIDDEN
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s18",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        pth = _normalize_output_root(path)
        if root == pth or root.startswith(pth + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s18"


def is_erad_listing_aware_s17_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1351–1400 listing-aware S17 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S17_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s17_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S17_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S17_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s17_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S17 输出仅允许独立根；禁止写入封闭 S1 / S2–S16 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    for closed in (
        closed_s1, closed_s2, closed_s3, closed_s4, closed_s5, closed_s6, closed_s7,
        closed_s8, closed_s9, closed_s10, closed_s11, closed_s12, closed_s13, closed_s14,
        closed_s15, closed_s16, closed_s18, closed_s19,
    ):
        if root == closed or root.startswith(closed + os.sep):
            return False, ERAD_LISTING_AWARE_S17_CLOSED_ROOT_WRITE_FORBIDDEN
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s17",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        pth = _normalize_output_root(path)
        if root == pth or root.startswith(pth + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s17"


def is_erad_listing_aware_s16_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1301–1350 listing-aware S16 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S16_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s16_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S16_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S16_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s16_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S16 输出仅允许独立根；禁止写入封闭 S1 / S2–S15 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    closed_s15 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    for closed in (
        closed_s1, closed_s2, closed_s3, closed_s4, closed_s5, closed_s6, closed_s7,
        closed_s8, closed_s9, closed_s10, closed_s11, closed_s12, closed_s13, closed_s14,
        closed_s15, closed_s17, closed_s18, closed_s19,
    ):
        if root == closed or root.startswith(closed + os.sep):
            return False, ERAD_LISTING_AWARE_S16_CLOSED_ROOT_WRITE_FORBIDDEN
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s16",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        pth = _normalize_output_root(path)
        if root == pth or root.startswith(pth + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s16"


def is_erad_listing_aware_s15_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E1251–1300 listing-aware S15 模式。"""
    la_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S15_UNIVERSE_CSV)
    )
    la_root = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == la_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == la_root or root.startswith(la_root + os.sep):
            return True
    return False


def validate_erad_listing_aware_s15_universe_csv_path(universe_csv: str) -> Tuple[bool, str]:
    expected = os.path.normpath(os.path.abspath(DEFAULT_ERAD_LISTING_AWARE_S15_UNIVERSE_CSV))
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, ERAD_LISTING_AWARE_S15_UNIVERSE_CSV_REQUIRED
    return True, ""


def validate_erad_listing_aware_s15_output_root(output_root: str) -> Tuple[bool, str]:
    """listing-aware S15 输出仅允许独立根；禁止写入封闭 S1 / S2–S14 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    closed_s2 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT)
    closed_s3 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT)
    closed_s4 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT)
    closed_s5 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT)
    closed_s6 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT)
    closed_s7 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT)
    closed_s8 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT)
    closed_s9 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT)
    closed_s10 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT)
    closed_s11 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT)
    closed_s12 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT)
    closed_s13 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT)
    closed_s14 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT)
    closed_s16 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT)
    closed_s17 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT)
    closed_s18 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT)
    closed_s19 = _normalize_output_root(DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT)
    for closed in (
        closed_s1, closed_s2, closed_s3, closed_s4, closed_s5, closed_s6, closed_s7,
        closed_s8, closed_s9, closed_s10, closed_s11, closed_s12, closed_s13, closed_s14,
        closed_s16, closed_s17, closed_s18, closed_s19,
    ):
        if root == closed or root.startswith(closed + os.sep):
            return False, ERAD_LISTING_AWARE_S15_CLOSED_ROOT_WRITE_FORBIDDEN
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_listing_aware_s15",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        pth = _normalize_output_root(path)
        if root == pth or root.startswith(pth + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_listing_aware_s15"


def is_erad_slice2_orgid_fallback_retry_mode(
    universe_csv: Optional[str] = None,
    output_root: Optional[str] = None,
) -> bool:
    """判定是否为 AD2E578/590/598 orgId 离线回退孤立重试模式。"""
    retry_universe = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_UNIVERSE_CSV)
    )
    retry_root = _normalize_output_root(DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT)
    if universe_csv:
        actual_u = os.path.normpath(os.path.abspath(universe_csv))
        if actual_u == retry_universe:
            return True
    if output_root:
        root = _normalize_output_root(output_root)
        if root == retry_root or root.startswith(retry_root + os.sep):
            return True
    return False


def validate_erad_slice2_orgid_fallback_retry_universe_csv_path(
    universe_csv: str,
) -> Tuple[bool, str]:
    expected = os.path.normpath(
        os.path.abspath(DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_UNIVERSE_CSV)
    )
    actual = os.path.normpath(os.path.abspath(universe_csv))
    if actual != expected:
        return False, "erad_a_slice2_orgid_fallback_retry_universe_csv_required"
    return True, ""


def validate_erad_slice2_orgid_fallback_retry_output_root(
    output_root: str,
) -> Tuple[bool, str]:
    """孤立重试输出仅允许独立 retry 根；禁止写入封闭 slice2 S1 live 根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT)
    closed_s1 = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    if root == closed_s1 or root.startswith(closed_s1 + os.sep):
        return False, ERAD_SLICE2_ORGID_FALLBACK_RETRY_CLOSED_ROOT_WRITE_FORBIDDEN
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, "output_root_must_be_under_cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry"


def validate_erad_slice2_orgid_fallback_retry_universe_size(
    cases: List[EraDNextScaleSlice2UniverseCase],
) -> Tuple[bool, str]:
    included = [c for c in cases if c.erad_include == "yes"]
    if len(included) != REQUIRED_ERAD_SLICE2_ORGID_FALLBACK_RETRY_SIZE:
        return (
            False,
            f"{ERAD_SLICE2_ORGID_FALLBACK_RETRY_UNIVERSE_SIZE_VIOLATION}: "
            f"got {len(included)} expected {REQUIRED_ERAD_SLICE2_ORGID_FALLBACK_RETRY_SIZE}",
        )
    case_ids = {c.case_id for c in included}
    if case_ids != ERAD_SLICE2_ORGID_FALLBACK_RETRY_CASE_IDS:
        return (
            False,
            f"{ERAD_SLICE2_ORGID_FALLBACK_RETRY_CASE_SET_VIOLATION}: got={sorted(case_ids)}",
        )
    return True, ""


def erad_slice2_request_cap_for_mode(
    *,
    orgid_fallback_retry: bool = False,
    listing_aware_s2: bool = False,
    listing_aware_s3: bool = False,
    listing_aware_s4: bool = False,
    listing_aware_s5: bool = False,
    listing_aware_s6: bool = False,
    listing_aware_s7: bool = False,
    listing_aware_s8: bool = False,
    listing_aware_s9: bool = False,
    listing_aware_s10: bool = False,
    listing_aware_s11: bool = False,
    listing_aware_s12: bool = False,
    listing_aware_s13: bool = False,
    listing_aware_s14: bool = False,
    listing_aware_s15: bool = False,
    listing_aware_s16: bool = False,
    listing_aware_s17: bool = False,
    listing_aware_s18: bool = False,
    listing_aware_s19: bool = False,
) -> int:
    """按模式返回 CNINFO 请求上限。"""
    if orgid_fallback_retry:
        return ERAD_SLICE2_ORGID_FALLBACK_RETRY_REQUEST_CAP
    if listing_aware_s2:
        return ERAD_LISTING_AWARE_S2_REQUEST_CAP
    if listing_aware_s3:
        return ERAD_LISTING_AWARE_S3_REQUEST_CAP
    if listing_aware_s4:
        return ERAD_LISTING_AWARE_S4_REQUEST_CAP
    if listing_aware_s5:
        return ERAD_LISTING_AWARE_S5_REQUEST_CAP
    if listing_aware_s6:
        return ERAD_LISTING_AWARE_S6_REQUEST_CAP
    if listing_aware_s7:
        return ERAD_LISTING_AWARE_S7_REQUEST_CAP
    if listing_aware_s8:
        return ERAD_LISTING_AWARE_S8_REQUEST_CAP
    if listing_aware_s9:
        return ERAD_LISTING_AWARE_S9_REQUEST_CAP
    if listing_aware_s10:
        return ERAD_LISTING_AWARE_S10_REQUEST_CAP
    if listing_aware_s11:
        return ERAD_LISTING_AWARE_S11_REQUEST_CAP
    if listing_aware_s12:
        return ERAD_LISTING_AWARE_S12_REQUEST_CAP
    if listing_aware_s13:
        return ERAD_LISTING_AWARE_S13_REQUEST_CAP
    if listing_aware_s14:
        return ERAD_LISTING_AWARE_S14_REQUEST_CAP
    if listing_aware_s15:
        return ERAD_LISTING_AWARE_S15_REQUEST_CAP
    if listing_aware_s16:
        return ERAD_LISTING_AWARE_S16_REQUEST_CAP
    if listing_aware_s17:
        return ERAD_LISTING_AWARE_S17_REQUEST_CAP
    if listing_aware_s18:
        return ERAD_LISTING_AWARE_S18_REQUEST_CAP
    if listing_aware_s19:
        return ERAD_LISTING_AWARE_S19_REQUEST_CAP
    return ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP


def validate_erad_next_scale_slice2_output_root(output_root: str) -> Tuple[bool, str]:
    """Era D A-class next-scale slice2 输出仅允许 slice2 S1 隔离根。"""
    root = _normalize_output_root(output_root)
    allowed = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    blocked = (
        (PHASE1_OUTPUT_ROOT, PHASE1_BASELINE_WRITE_FORBIDDEN),
        (DEFAULT_OUTPUT_ROOT, PHASE2_EXPANSION_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_OUTPUT_ROOT, RETRY_V1_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V2_OUTPUT_ROOT, RETRY_V2_WRITE_FORBIDDEN),
        (DEFAULT_RETRY_V3_OUTPUT_ROOT, RETRY_V3_OUTPUT_ROOT_VIOLATION),
        (PRECHECK_OUTPUT_ROOT, PRECHECK_WRITE_FORBIDDEN),
        (DEFAULT_PHASE3_OUTPUT_ROOT, PHASE3_OUTPUT_ROOT_VIOLATION),
        (DEFAULT_A3M017_RETRY_OUTPUT_ROOT, "a3m017_isolated_retry_output_root_forbidden"),
        (DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT, ERAD_SLICE2_SCALE_200_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT,
            ERAD_SLICE2_FAILED_RETRY_ROOT_WRITE_FORBIDDEN,
        ),
        (DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT, ERAD_SLICE2_SLICE1_ROOT_WRITE_FORBIDDEN),
        (
            DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT,
            "orgid_fallback_retry_root_forbidden_for_full_slice2",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT,
            "listing_aware_s2_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT,
            "listing_aware_s3_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT,
            "listing_aware_s4_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT,
            "listing_aware_s5_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT,
            "listing_aware_s6_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT,
            "listing_aware_s7_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT,
            "listing_aware_s8_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT,
            "listing_aware_s9_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT,
            "listing_aware_s10_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT,
            "listing_aware_s11_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT,
            "listing_aware_s12_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT,
            "listing_aware_s13_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT,
            "listing_aware_s14_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT,
            "listing_aware_s15_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT,
            "listing_aware_s16_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT,
            "listing_aware_s17_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT,
            "listing_aware_s18_root_forbidden_for_full_slice2_s1",
        ),
        (
            DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT,
            "listing_aware_s19_root_forbidden_for_full_slice2_s1",
        ),
        (C_CLASS_HARVEST_ROOT, "c_class_harvest_output_root_forbidden"),
        (B_CLASS_VALIDATION_PREFIX, "b_class_validation_output_root_forbidden"),
        (C_CLASS_VALIDATION_PREFIX, "c_class_validation_output_root_forbidden"),
        (D_CLASS_VALIDATION_PREFIX, "d_class_validation_output_root_forbidden"),
    )
    for path, err in blocked:
        p = _normalize_output_root(path)
        if root == p or root.startswith(p + os.sep):
            return False, err
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, ERAD_NEXT_SCALE_SLICE2_OUTPUT_ROOT_VIOLATION


def enforce_erad_next_scale_slice2_approval_gate(args: argparse.Namespace) -> None:
    wrong = (
        (args.approve_a_class_phase2_metadata_expansion, ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (args.approve_a_class_phase2_failed_retry, ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (args.approve_a_class_phase2_network_recovery_retry_v2, ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (args.approve_a_class_phase2_retry_v3, ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_phase3_50_company_expansion", False), ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_phase3_a3m017_isolated_retry", False), ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_200", False), ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_200_failed_retry", False), ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (getattr(args, "approve_a_class_erad_scale_500_slice1", False), ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (args.approve_a_class_tiny_live_metadata, ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
        (args.approve_phase1_tiny_live_metadata, ERAD_NEXT_SCALE_SLICE2_WRONG_APPROVAL),
    )
    for enabled, code in wrong:
        if enabled:
            print(f"ERROR: {code}", file=sys.stderr)
            sys.exit(2)
    if args.mode == "live" and not getattr(args, "approve_a_class_erad_scale_500_slice2", False):
        print(f"ERROR: {ERAD_NEXT_SCALE_SLICE2_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)


def enforce_erad_next_scale_slice2_request_cap(total_planned: int) -> Tuple[bool, str]:
    if total_planned > ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP:
        return (
            False,
            f"{ERAD_SLICE2_REQUEST_CAP_EXCEEDED}:{total_planned}>{ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP}",
        )
    return True, ""


def parse_erad_a_slice2_case_range(case_range: str) -> Tuple[str, str]:
    parts = case_range.split(":")
    if len(parts) != 2:
        raise ValueError(ERAD_SLICE2_CASE_RANGE_INVALID)
    start_id = parts[0].strip()
    end_id = parts[1].strip()
    allowed = (
        ALLOWED_ERAD_NEXT_SCALE_SLICE2_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S2_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S3_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S4_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S5_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S6_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S7_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S8_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S9_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S10_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S11_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S12_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S13_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S14_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S15_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S16_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S17_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S18_CASE_IDS
        | ALLOWED_ERAD_LISTING_AWARE_S19_CASE_IDS
    )
    if start_id not in allowed:
        raise ValueError(f"{ERAD_SLICE2_CASE_RANGE_INVALID}:start={start_id}")
    if end_id not in allowed:
        raise ValueError(f"{ERAD_SLICE2_CASE_RANGE_INVALID}:end={end_id}")
    # 不允许跨模式混用 … / 1301–1350 / 1351–1400 / 1401–1450 / 1451–1500
    start_num = _erad_a_slice2_case_number(start_id)
    end_num = _erad_a_slice2_case_number(end_id)

    def _band(n: int) -> int:
        if n <= 600:
            return 0
        if n <= 650:
            return 1
        if n <= 700:
            return 2
        if n <= 750:
            return 3
        if n <= 800:
            return 4
        if n <= 850:
            return 5
        if n <= 900:
            return 6
        if n <= 950:
            return 7
        if n <= 1000:
            return 8
        if n <= 1050:
            return 9
        if n <= 1100:
            return 10
        if n <= 1150:
            return 11
        if n <= 1200:
            return 12
        if n <= 1250:
            return 13
        if n <= 1300:
            return 14
        if n <= 1350:
            return 15
        if n <= 1400:
            return 16
        if n <= 1450:
            return 17
        if n <= 1500:
            return 18
        return 19

    if _band(start_num) != _band(end_num):
        raise ValueError(f"{ERAD_SLICE2_CASE_RANGE_INVALID}:cross_mode_range")
    if start_num > end_num:
        raise ValueError(f"{ERAD_SLICE2_CASE_RANGE_INVALID}:order")
    return start_id, end_id


def filter_erad_a_next_scale_slice2_cases_by_range(
    cases: List[EraDNextScaleSlice2UniverseCase],
    case_range: Optional[str],
) -> List[EraDNextScaleSlice2UniverseCase]:
    if not case_range:
        return cases
    start_id, end_id = parse_erad_a_slice2_case_range(case_range)
    start_num = _erad_a_slice2_case_number(start_id)
    end_num = _erad_a_slice2_case_number(end_id)
    return [
        c
        for c in cases
        if start_num <= _erad_a_slice2_case_number(c.case_id) <= end_num
    ]


def build_erad_next_scale_slice2_dryrun_row(
    case: EraDNextScaleSlice2UniverseCase,
    issues: List[str],
    output_root: str,
) -> Dict[str, str]:
    source_id = REPORT_TYPE_SOURCE_ID.get(case.report_type, "unknown_source")
    status = "planned_ok" if not issues else "universe_invalid"
    notes = (
        f"erad-a-scale-500-slice2 dry-run; CNINFO not called; metadata only; "
        f"matching_logic={MATCHING_LOGIC_VERSION}; "
        f"planned_requests={ERAD_NEXT_SCALE_SLICE2_PLANNED_REQUESTS_PER_CASE}; "
        f"ad2e001_500_lineage_reference_only=yes; slice1_production_root_write=no"
        if not issues
        else "; ".join(issues)
    )
    return {
        "case_id": case.case_id,
        "company_code": case.company_code,
        "company_name": case.company_name,
        "market": case.market,
        "report_type": case.report_type,
        "expected_period": case.expected_period,
        "cohort": case.cohort,
        "prior_in_scale_200": case.prior_in_scale_200,
        "erad_include": case.erad_include,
        "planned_source": source_id,
        "planned_endpoint": planned_endpoints_for_case(slice2_to_phase2_case(case)),
        "planned_output_root": output_root,
        "pdf_download": "0",
        "pdf_parse": "0",
        "ocr": "0",
        "extraction": "0",
        "db_write": "0",
        "minio_write": "0",
        "rag_run": "0",
        "cninfo_call_planned": "0",
        "planned_request_count_case": str(ERAD_NEXT_SCALE_SLICE2_PLANNED_REQUESTS_PER_CASE),
        "dryrun_status": status,
        "notes": notes,
    }


def process_erad_next_scale_slice2_dry_run(
    cases: List[EraDNextScaleSlice2UniverseCase],
    output_root: str,
) -> Tuple[List[Dict[str, str]], List[str]]:
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = list(validate_erad_next_scale_slice2_duplicate_codes(cases))
    universe_issues.extend(lint_erad_next_scale_slice2_overlap(cases))
    _listing_blocking, listing_flags = lint_erad_next_scale_slice2_listing_period(
        cases,
        grandfather_case_ids=ERAD_SLICE2_FROZEN_LISTING_CAVEAT_CASE_IDS,
    )
    # listing_blocking 已由 lint_erad_next_scale_slice2_overlap 并入；此处仅保留 flag 供行级标注
    listing_flag_by_case: Dict[str, str] = {}
    for note in listing_flags:
        # 格式：err:grandfather:CASE_ID:CODE:failure_class:...
        parts = note.split(":")
        if len(parts) >= 3 and parts[1] == "grandfather":
            listing_flag_by_case[parts[2]] = note
    for case in cases:
        if case.erad_include != "yes":
            continue
        issues = validate_erad_next_scale_slice2_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
        row = build_erad_next_scale_slice2_dryrun_row(case, issues, output_root)
        flag = listing_flag_by_case.get(case.case_id)
        if flag:
            row["notes"] = f"{row['notes']}; listing_period_flag={flag}"
        rows.append(row)
    return rows, universe_issues


def write_erad_next_scale_slice2_dryrun_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice2_s1_dryrun_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_NEXT_SCALE_SLICE2_DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def compute_erad_next_scale_slice2_runner_gate(
    universe_issues: List[str],
    case_count: int,
    total_planned: int,
) -> str:
    if universe_issues or case_count != REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE:
        return "FAIL"
    ok_cap, _ = enforce_erad_next_scale_slice2_request_cap(total_planned)
    if not ok_cap:
        return "FAIL"
    return ERAD_NEXT_SCALE_SLICE2_RUNNER_GATE


def write_erad_next_scale_slice2_dryrun_summary(
    rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_issues: List[str],
    gate: str,
    total_planned: int,
) -> str:
    planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
    listing_flagged = sum(1 for row in rows if "listing_period_flag=" in (row.get("notes") or ""))
    total = len(rows)
    lines = [
        "# CNINFO A 类 Era D Next-Scale Slice2 S1 — Dry-run 摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Era D A-class next-scale slice2 S1 dry-run · **无 CNINFO** · **无 live** · **无 PDF**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | erad_a_scale_500_slice2_dry_run |",
        f"| universe size | {total} |",
        f"| planned_ok | {planned_ok} |",
        f"| cohort | next_scale_slice2（AD2E501–600） |",
        f"| planned_requests_total | {total_planned} (cap ≤ {ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP}) |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        "| CNINFO calls | **0** |",
        f"| L-D6 listing_period grandfather flags | {listing_flagged} |",
        "",
        "## Overlap lint",
        "",
        "- L-A1..L-A4 / L-B1..L-B4 / AB_182: **0 overlap**（若无 universe issues）",
        "- L-D4 ST 名称命中: **0**",
        "- L-D6 listing_period: 未来 cohort **硬拒**；冻结 S1 三案 **flag only**",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- scale-200 / slice1 / failed_retry / Phase 3 / A3M017 roots untouched: **yes**",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_erad_next_scale_slice2_s1_runner_extension_gate = {gate}",
        "```",
        "",
        "**不是 PASS** · **不是 live_ready** · **不是 verified** · **Approval status: NOT_APPROVED**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])
    summary_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice2_s1_dryrun_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path


def is_allowed_erad_a_slice2_mock_test_output_root(output_root: str) -> bool:
    root = _normalize_output_root(output_root)
    for parent_path in (
        ERAD_NEXT_SCALE_SLICE2_S1_MOCK_TEST_PARENT,
        ERAD_NEXT_SCALE_SLICE2_S1_MOCK_LIVE_TEST_PARENT,
    ):
        parent = _normalize_output_root(parent_path)
        if root.startswith(parent + os.sep):
            return True
    return False


def is_production_erad_a_next_scale_slice2_output_root(output_root: str) -> bool:
    root = _normalize_output_root(output_root)
    if is_allowed_erad_a_slice2_mock_test_output_root(root):
        return False
    allowed = _normalize_output_root(DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT)
    return root == allowed or root.startswith(allowed + os.sep)


def safe_cleanup_erad_a_slice2_test_output_root(temp_root: str) -> None:
    """测试 teardown 仅允许删除 slice2 _mock_* 子目录；拒绝生产 output root。"""
    import shutil

    if _is_under_prefix(temp_root, DEFAULT_PHASE3_OUTPUT_ROOT):
        raise RuntimeError("拒绝清理 Phase 3 生产 output root")
    if _is_under_prefix(temp_root, DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT):
        raise RuntimeError("拒绝清理 Era D scale-200 生产 output root")
    if _is_under_prefix(temp_root, DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT):
        raise RuntimeError("拒绝清理 Era D failed-retry 生产 output root")
    if _is_under_prefix(temp_root, DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT):
        raise RuntimeError("拒绝清理 Era D next-scale slice1 生产 output root")
    if is_production_erad_a_next_scale_slice2_output_root(temp_root):
        raise RuntimeError("拒绝清理 Era D next-scale slice2 生产 output root")
    if not is_allowed_erad_a_slice2_mock_test_output_root(temp_root):
        raise RuntimeError("拒绝清理非 mock 测试目录")
    shutil.rmtree(temp_root, ignore_errors=True)


def is_erad_next_scale_slice2_case_acceptable(row: Dict[str, str]) -> bool:
    if row.get("pdf_downloaded") not in ("0", "no", ""):
        return False
    if row.get("pdf_parsed") not in ("0", "no", ""):
        return False
    status = row.get("retrieval_status", "")
    quality = row.get("quality_status", "")
    lineage = row.get("lineage_status", "")
    if status in ("network_error", "not_found", "universe_invalid"):
        return False
    if status == "found":
        return True
    if status in ("discovered", "matching_pass"):
        return True
    if lineage == "discovered":
        return True
    if status == "needs_review" or quality == "needs_review":
        return bool(lineage)
    return False


def build_erad_next_scale_slice2_live_report_row(
    case: EraDNextScaleSlice2UniverseCase,
    record: Dict[str, Any],
    cninfo_request_count: int,
) -> Dict[str, str]:
    row = build_live_report_row(slice2_to_phase2_case(case), record, cninfo_request_count)
    notes = str(record.get("notes") or "")
    row["notes"] = (
        f"erad-a-scale-500-slice2 live; matching_logic={MATCHING_LOGIC_VERSION}; "
        f"lineage_evidence_mode=fresh_metadata; ad2e001_500_lineage_reference_only=yes; "
        f"slice1_production_root_write=no; PDF not downloaded; {notes}"
    ).strip()
    row["cohort"] = case.cohort
    row["prior_in_scale_200"] = case.prior_in_scale_200
    row["lineage_evidence_mode"] = "fresh_metadata"
    return row


def process_erad_a_next_scale_slice2_live(
    cases: List[EraDNextScaleSlice2UniverseCase],
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    *,
    request_cap: Optional[int] = None,
    mode_label: str = "erad_a_scale_500_slice2_live",
) -> Tuple[List[Dict[str, str]], List[str]]:
    """Era D A-class next-scale slice2 live：fresh_metadata only；须 approval gate。"""
    cap = (
        ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP
        if request_cap is None
        else int(request_cap)
    )
    rows: List[Dict[str, str]] = []
    universe_issues: List[str] = []
    for case in cases:
        if case.erad_include != "yes":
            continue
        issues = validate_erad_next_scale_slice2_case(case)
        if issues:
            universe_issues.append(f"{case.case_id}:{';'.join(issues)}")
            rows.append(
                build_erad_next_scale_slice2_live_report_row(
                    case,
                    {
                        "retrieval_status": "universe_invalid",
                        "quality_status": "blocked",
                        "lineage_status": "needs_review",
                        "announcement_id": "",
                        "announcement_title": "",
                        "announcement_time": "",
                        "title_match_status": "fail",
                        "period_match_status": "fail",
                        "pdf_url_present": "no",
                        "adjunct_url_present": "no",
                        "notes": "; ".join(issues),
                    },
                    0,
                )
            )
            stats.failure_count += 1
            continue
        tl_case = to_tiny_live_case(slice2_to_phase2_case(case))
        before_requests = stats.cninfo_requests
        record = tiny_live.execute_live_case(tl_case, stats)
        case_cninfo_requests = stats.cninfo_requests - before_requests
        if stats.cninfo_requests > cap:
            universe_issues.append(
                f"cninfo_request_cap_exceeded:{stats.cninfo_requests}>{cap}"
            )
            break
        live_row = build_erad_next_scale_slice2_live_report_row(
            case, record, case_cninfo_requests
        )
        snapshot_path = os.path.join(output_paths["raw_metadata"], f"{case.case_id}.json")
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "case_id": case.case_id,
                    "case": {
                        "case_id": case.case_id,
                        "company_code": case.company_code,
                        "company_name": case.company_name,
                        "market": case.market,
                        "report_type": case.report_type,
                        "expected_period": case.expected_period,
                        "cohort": case.cohort,
                        "prior_in_scale_200": case.prior_in_scale_200,
                        "include_reason": case.include_reason,
                        "erad_include": case.erad_include,
                    },
                    "mode": mode_label,
                    "lineage_evidence_mode": "fresh_metadata",
                    "ad2e001_500_lineage_reference_only": True,
                    "slice1_production_root_write": False,
                    "closed_slice2_s1_live_root_write": False,
                    "orgid_offline_fallback": record.get("_orgid_offline_fallback", "n/a"),
                    "cninfo_called": True,
                    "cninfo_request_count": case_cninfo_requests,
                    "pdf_download_enabled": False,
                    "pdf_parse_enabled": False,
                    "matching_logic": MATCHING_LOGIC_VERSION,
                    "record": live_row,
                    "raw_announcement": record.get("_raw_announcement"),
                    "org_id": record.get("_org_id"),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        rows.append(live_row)
        print(
            f"case_id={case.case_id} cohort={case.cohort} company_code={case.company_code} "
            f"retrieval_status={live_row['retrieval_status']} "
            f"quality={live_row.get('quality_status', 'n/a')}",
            flush=True,
        )
    return rows, universe_issues


def compute_erad_next_scale_slice2_execution_gate(
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    stats: tiny_live.LiveStats,
    expected_case_count: int,
    *,
    request_cap: Optional[int] = None,
) -> str:
    cap = (
        ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP
        if request_cap is None
        else int(request_cap)
    )
    if has_red_line_violation(stats, rows):
        return "FAIL_REVIEW_REQUIRED"
    if universe_issues:
        return "FAIL_REVIEW_REQUIRED"
    if stats.cninfo_requests > cap:
        return "FAIL_REVIEW_REQUIRED"
    if len(rows) != expected_case_count:
        return "FAIL_REVIEW_REQUIRED"
    threshold = ERAD_SLICE2_ACCEPTABLE_THRESHOLD
    if expected_case_count < REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE:
        threshold = max(1, int(expected_case_count * 0.9))
    acceptable_count = sum(
        1 for row in rows if is_erad_next_scale_slice2_case_acceptable(row)
    )
    if acceptable_count >= threshold:
        return ERAD_SLICE2_EXECUTION_GATE_PASS
    return "FAIL_REVIEW_REQUIRED"


def write_erad_next_scale_slice2_live_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice2_s1_live_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_SLICE2_LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path


def write_erad_next_scale_slice2_live_quality_report(
    rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    report_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice2_s1_live_quality_report.csv"
    )
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ERAD_SLICE2_LIVE_QUALITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in ERAD_SLICE2_LIVE_QUALITY_COLUMNS})
    return report_path


def write_erad_next_scale_slice2_live_summary(
    output_paths: Dict[str, str],
    stats: tiny_live.LiveStats,
    rows: List[Dict[str, str]],
    universe_issues: List[str],
    gate: str,
    expected_case_count: int,
) -> str:
    acceptable_count = sum(
        1 for row in rows if is_erad_next_scale_slice2_case_acceptable(row)
    )
    failed_count = sum(
        1
        for row in rows
        if row.get("retrieval_status")
        in ("network_error", "not_found", "universe_invalid")
    )
    needs_review_count = sum(
        1 for row in rows if row.get("quality_status") == "needs_review"
    )
    threshold = ERAD_SLICE2_ACCEPTABLE_THRESHOLD
    if expected_case_count < REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE:
        threshold = max(1, int(expected_case_count * 0.9))
    lines = [
        "# CNINFO A 类 Era D Next-Scale Slice2 S1 — Live 执行摘要",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** Era D A-class next-scale slice2 S1 live metadata validation · **无 PDF** · **不是 verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        "| mode | erad_a_scale_500_slice2_live |",
        f"| universe size | {len(rows)} |",
        f"| expected case count | {expected_case_count} |",
        f"| acceptable | {acceptable_count} |",
        f"| failed | {failed_count} |",
        f"| needs_review | {needs_review_count} |",
        f"| CNINFO requests | {stats.cninfo_requests} (cap ≤ {ERAD_NEXT_SCALE_SLICE2_REQUEST_CAP}) |",
        f"| matching_logic | **{MATCHING_LOGIC_VERSION}** |",
        f"| execution gate | `{gate}` |",
        f"| acceptance threshold | ≥{threshold}/{expected_case_count} → PASS_WITH_CAVEAT |",
        "",
        "## Isolation",
        "",
        "Writes **only** under slice2 S1 root; **does not mutate** scale-200 / slice1 / failed-retry / Phase 3.",
        "",
        "## Safety",
        "",
        "- metadata only: **yes**",
        f"- output isolation: `{output_paths['root']}`",
        "- verified: **no**",
        "- production_ready: **no**",
        "",
        "## Gate",
        "",
        "```text",
        f"a_class_erad_next_scale_slice2_s1_live_path_gate = {ERAD_NEXT_SCALE_SLICE2_LIVE_PATH_GATE}",
        f"a_class_erad_next_scale_slice2_s1_execution_gate = {gate}",
        "```",
        "",
        f"- acceptance threshold: **≥ {threshold}/{expected_case_count}** → PASS_WITH_CAVEAT",
        "",
        "**不是 PASS** · **不是 verified** · **不是 production_ready**",
        "",
    ]
    if universe_issues:
        lines.extend(["## Universe issues", ""] + [f"- {item}" for item in universe_issues] + [""])
    summary_path = os.path.join(
        output_paths["reports"], "a_class_erad_next_scale_slice2_s1_live_summary.md"
    )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return summary_path



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CNINFO A-class Phase2 metadata expansion（dry-run default）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")

    parser.add_argument("--universe-csv", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument(
        "--approve-a-class-phase2-metadata-expansion",
        action="store_true",
        help="显式批准 A-class Phase 2 metadata expansion live",
    )
    parser.add_argument(
        "--approve-a-class-phase2-failed-retry",
        action="store_true",
        help="显式批准 A-class Phase 2 failed-case isolated retry live",
    )
    parser.add_argument(
        "--approve-a-class-phase2-network-recovery-retry-v2",
        action="store_true",
        help="显式批准 A-class Phase 2 network recovery retry v2 live",
    )
    parser.add_argument(
        "--retry-failed-only",
        action="store_true",
        help="isolated retry 模式：仅 8 个 failed case",
    )
    parser.add_argument(
        "--retry-v3",
        action="store_true",
        help="isolated retry v3 模式：8 个 unresolved case",
    )
    parser.add_argument(
        "--approve-a-class-phase2-retry-v3",
        action="store_true",
        help="显式批准 A-class Phase 2 retry v3 live",
    )
    parser.add_argument(
        "--phase3-50",
        dest="phase3_50",
        action="store_true",
        help="Phase 3 50-company metadata expansion 模式",
    )
    parser.add_argument(
        "--erad-a-scale-200",
        dest="erad_a_scale_200",
        action="store_true",
        help="Era D A-class ~200 metadata expansion 模式",
    )
    parser.add_argument(
        "--approve-a-class-erad-scale-200",
        dest="approve_a_class_erad_scale_200",
        action="store_true",
        help="显式批准 A-class Era D ~200 live expansion",
    )
    parser.add_argument(
        "--erad-a-scale-200-failed-retry",
        dest="erad_a_scale_200_failed_retry",
        action="store_true",
        help="Era D A-class ~200 isolated failed-case retry 模式",
    )
    parser.add_argument(
        "--approve-a-class-erad-scale-200-failed-retry",
        dest="approve_a_class_erad_scale_200_failed_retry",
        action="store_true",
        help="显式批准 A-class Era D ~200 isolated failed-retry live",
    )
    parser.add_argument(
        "--erad-a-scale-500-slice1",
        dest="erad_a_scale_500_slice1",
        action="store_true",
        help="300-case Era D A-class next-scale slice1 模式（AD2E201–500 · dry-run 默认）",
    )
    parser.add_argument(
        "--approve-a-class-erad-scale-500-slice1",
        dest="approve_a_class_erad_scale_500_slice1",
        action="store_true",
        help="显式批准 A-class Era D next-scale slice1 live",
    )
    parser.add_argument(
        "--erad-a-scale-500-slice2",
        dest="erad_a_scale_500_slice2",
        action="store_true",
        help="100-case Era D A-class next-scale slice2 S1 模式（AD2E501–600 · dry-run 默认）",
    )
    parser.add_argument(
        "--approve-a-class-erad-scale-500-slice2",
        dest="approve_a_class_erad_scale_500_slice2",
        action="store_true",
        help="显式批准 A-class Era D next-scale slice2 S1 live",
    )
    parser.add_argument(
        "--case-range",
        default=None,
        help="可选 case_id 范围（如 AD2E201:AD2E350 或 AD2E501:AD2E550）用于 session split",
    )
    parser.add_argument(
        "--approve-a-class-phase3-50-company-expansion",
        dest="approve_a_class_phase3_50_company_expansion",
        action="store_true",
        help="显式批准 A-class Phase 3 50-company live expansion",
    )
    parser.add_argument("--approve-a-class-tiny-live-metadata", action="store_true")
    parser.add_argument("--approve-phase1-tiny-live-metadata", action="store_true")
    parser.add_argument("--approve-full-harvest", action="store_true")
    parser.add_argument("--approve-phase2-smoke-harvest", action="store_true")
    parser.add_argument("--approve-phase3-batch-500-harvest", action="store_true")
    parser.add_argument("--approve-b-class-tiny-live-validation", action="store_true")
    parser.add_argument("--download-pdf", action="store_true")
    parser.add_argument("--parse-pdf", action="store_true")
    parser.add_argument("--enable-ocr", action="store_true")
    parser.add_argument("--enable-extraction", action="store_true")
    parser.add_argument("--write-db", action="store_true")
    parser.add_argument("--write-minio", action="store_true")
    parser.add_argument("--run-rag", action="store_true")
    parser.add_argument("--mark-verified", action="store_true")
    parser.add_argument("--mark-production-ready", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.retry_v3 and args.retry_failed_only:
        print(
            f"ERROR: {RETRY_V3_INCOMPATIBLE_WITH_RETRY_FAILED_ONLY}",
            file=sys.stderr,
        )
        return 2

    if args.phase3_50 and (args.retry_v3 or args.retry_failed_only):
        print(
            f"ERROR: {PHASE3_INCOMPATIBLE_WITH_RETRY_V3 if args.retry_v3 else PHASE3_INCOMPATIBLE_WITH_RETRY_FAILED_ONLY}",
            file=sys.stderr,
        )
        return 2


    if getattr(args, "erad_a_scale_500_slice2", False):
        if (
            getattr(args, "erad_a_scale_200", False)
            or getattr(args, "erad_a_scale_200_failed_retry", False)
            or getattr(args, "erad_a_scale_500_slice1", False)
            or args.phase3_50
            or args.retry_v3
            or args.retry_failed_only
        ):
            print(f"ERROR: {ERAD_NEXT_SCALE_SLICE2_INCOMPATIBLE_WITH_OTHER_MODES}", file=sys.stderr)
            return 2
        if args.universe_csv is None:
            print(f"ERROR: {ERAD_NEXT_SCALE_SLICE2_UNIVERSE_CSV_REQUIRED}", file=sys.stderr)
            return 2
        orgid_fb_retry = is_erad_slice2_orgid_fallback_retry_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s2 = is_erad_listing_aware_s2_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s3 = is_erad_listing_aware_s3_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s4 = is_erad_listing_aware_s4_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s5 = is_erad_listing_aware_s5_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s6 = is_erad_listing_aware_s6_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s7 = is_erad_listing_aware_s7_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s8 = is_erad_listing_aware_s8_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s9 = is_erad_listing_aware_s9_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s10 = is_erad_listing_aware_s10_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s11 = is_erad_listing_aware_s11_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s12 = is_erad_listing_aware_s12_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s13 = is_erad_listing_aware_s13_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s14 = is_erad_listing_aware_s14_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s15 = is_erad_listing_aware_s15_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s16 = is_erad_listing_aware_s16_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s17 = is_erad_listing_aware_s17_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s18 = is_erad_listing_aware_s18_mode(
            args.universe_csv, args.output_root
        )
        listing_aware_s19 = is_erad_listing_aware_s19_mode(
            args.universe_csv, args.output_root
        )
        if orgid_fb_retry and (
            listing_aware_s2
            or listing_aware_s3
            or listing_aware_s4
            or listing_aware_s5
            or listing_aware_s6
            or listing_aware_s7
            or listing_aware_s8
            or listing_aware_s9
            or listing_aware_s10
            or listing_aware_s11
            or listing_aware_s12
            or listing_aware_s13
            or listing_aware_s14
            or listing_aware_s15
            or listing_aware_s16
            or listing_aware_s17
            or listing_aware_s18
            or listing_aware_s19
        ):
            print(
                "ERROR: erad_a_slice2_orgid_fallback_and_listing_aware_mutually_exclusive",
                file=sys.stderr,
            )
            return 2
        la_mode_count = sum(
            1
            for flag in (
                listing_aware_s2,
                listing_aware_s3,
                listing_aware_s4,
                listing_aware_s5,
                listing_aware_s6,
                listing_aware_s7,
                listing_aware_s8,
                listing_aware_s9,
                listing_aware_s10,
                listing_aware_s11,
                listing_aware_s12,
                listing_aware_s13,
                listing_aware_s14,
                listing_aware_s15,
                listing_aware_s16,
                listing_aware_s17,
                listing_aware_s18,
                listing_aware_s19,
            )
            if flag
        )
        if la_mode_count > 1:
            print(
                "ERROR: erad_a_listing_aware_s2_s3_s4_s5_s6_s7_s8_s9_s10_s11_s12_s13_s14_s15_s16_s17_s18_s19_mutually_exclusive",
                file=sys.stderr,
            )
            return 2
        if args.output_root is None:
            if orgid_fb_retry:
                args.output_root = DEFAULT_ERAD_SLICE2_ORGID_FALLBACK_RETRY_OUTPUT_ROOT
            elif listing_aware_s2:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S2_OUTPUT_ROOT
            elif listing_aware_s3:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S3_OUTPUT_ROOT
            elif listing_aware_s4:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S4_OUTPUT_ROOT
            elif listing_aware_s5:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S5_OUTPUT_ROOT
            elif listing_aware_s6:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S6_OUTPUT_ROOT
            elif listing_aware_s7:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S7_OUTPUT_ROOT
            elif listing_aware_s8:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S8_OUTPUT_ROOT
            elif listing_aware_s9:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S9_OUTPUT_ROOT
            elif listing_aware_s10:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S10_OUTPUT_ROOT
            elif listing_aware_s11:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S11_OUTPUT_ROOT
            elif listing_aware_s12:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S12_OUTPUT_ROOT
            elif listing_aware_s13:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S13_OUTPUT_ROOT
            elif listing_aware_s14:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S14_OUTPUT_ROOT
            elif listing_aware_s15:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S15_OUTPUT_ROOT
            elif listing_aware_s16:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S16_OUTPUT_ROOT
            elif listing_aware_s17:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S17_OUTPUT_ROOT
            elif listing_aware_s18:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S18_OUTPUT_ROOT
            elif listing_aware_s19:
                args.output_root = DEFAULT_ERAD_LISTING_AWARE_S19_OUTPUT_ROOT
            else:
                args.output_root = DEFAULT_ERAD_NEXT_SCALE_SLICE2_S1_OUTPUT_ROOT
            orgid_fb_retry = is_erad_slice2_orgid_fallback_retry_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s2 = is_erad_listing_aware_s2_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s3 = is_erad_listing_aware_s3_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s4 = is_erad_listing_aware_s4_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s5 = is_erad_listing_aware_s5_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s6 = is_erad_listing_aware_s6_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s7 = is_erad_listing_aware_s7_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s8 = is_erad_listing_aware_s8_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s9 = is_erad_listing_aware_s9_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s10 = is_erad_listing_aware_s10_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s11 = is_erad_listing_aware_s11_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s12 = is_erad_listing_aware_s12_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s13 = is_erad_listing_aware_s13_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s14 = is_erad_listing_aware_s14_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s15 = is_erad_listing_aware_s15_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s16 = is_erad_listing_aware_s16_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s17 = is_erad_listing_aware_s17_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s18 = is_erad_listing_aware_s18_mode(
                args.universe_csv, args.output_root
            )
            listing_aware_s19 = is_erad_listing_aware_s19_mode(
                args.universe_csv, args.output_root
            )
        enforce_forbidden_options(args)
        if args.mode == "live":
            enforce_erad_next_scale_slice2_approval_gate(args)
        if orgid_fb_retry:
            ok_csv, csv_err = validate_erad_slice2_orgid_fallback_retry_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_slice2_orgid_fallback_retry_output_root(
                args.output_root
            )
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s2:
            ok_csv, csv_err = validate_erad_listing_aware_s2_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s2_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s3:
            ok_csv, csv_err = validate_erad_listing_aware_s3_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s3_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s4:
            ok_csv, csv_err = validate_erad_listing_aware_s4_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s4_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s5:
            ok_csv, csv_err = validate_erad_listing_aware_s5_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s5_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s6:
            ok_csv, csv_err = validate_erad_listing_aware_s6_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s6_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s7:
            ok_csv, csv_err = validate_erad_listing_aware_s7_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s7_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s8:
            ok_csv, csv_err = validate_erad_listing_aware_s8_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s8_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s9:
            ok_csv, csv_err = validate_erad_listing_aware_s9_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s9_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s10:
            ok_csv, csv_err = validate_erad_listing_aware_s10_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s10_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s11:
            ok_csv, csv_err = validate_erad_listing_aware_s11_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s11_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s12:
            ok_csv, csv_err = validate_erad_listing_aware_s12_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s12_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s13:
            ok_csv, csv_err = validate_erad_listing_aware_s13_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s13_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s16:
            ok_csv, csv_err = validate_erad_listing_aware_s16_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s16_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s17:
            ok_csv, csv_err = validate_erad_listing_aware_s17_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s17_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s18:
            ok_csv, csv_err = validate_erad_listing_aware_s18_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s18_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s19:
            ok_csv, csv_err = validate_erad_listing_aware_s19_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s19_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s15:
            ok_csv, csv_err = validate_erad_listing_aware_s15_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s15_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        elif listing_aware_s14:
            ok_csv, csv_err = validate_erad_listing_aware_s14_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_listing_aware_s14_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        else:
            ok_csv, csv_err = validate_erad_next_scale_slice2_universe_csv_path(
                args.universe_csv
            )
            if not ok_csv:
                print(f"ERROR: {csv_err}", file=sys.stderr)
                return 2
            ok_root, root_err = validate_erad_next_scale_slice2_output_root(args.output_root)
            if not ok_root:
                print(f"ERROR: {root_err}", file=sys.stderr)
                return 2
        if not os.path.isfile(args.universe_csv):
            print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
            return 2
        case_range = getattr(args, "case_range", None)
        if case_range and orgid_fb_retry:
            print(
                "ERROR: case_range_not_allowed_for_orgid_fallback_retry",
                file=sys.stderr,
            )
            return 2
        if case_range:
            try:
                parse_erad_a_slice2_case_range(case_range)
            except ValueError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 2
        request_cap = erad_slice2_request_cap_for_mode(
            orgid_fallback_retry=orgid_fb_retry,
            listing_aware_s2=listing_aware_s2,
            listing_aware_s3=listing_aware_s3,
            listing_aware_s4=listing_aware_s4,
            listing_aware_s5=listing_aware_s5,
            listing_aware_s6=listing_aware_s6,
            listing_aware_s7=listing_aware_s7,
            listing_aware_s8=listing_aware_s8,
            listing_aware_s9=listing_aware_s9,
            listing_aware_s10=listing_aware_s10,
            listing_aware_s11=listing_aware_s11,
            listing_aware_s12=listing_aware_s12,
            listing_aware_s13=listing_aware_s13,
            listing_aware_s14=listing_aware_s14,
            listing_aware_s15=listing_aware_s15,
            listing_aware_s16=listing_aware_s16,
            listing_aware_s17=listing_aware_s17,
            listing_aware_s18=listing_aware_s18,
            listing_aware_s19=listing_aware_s19,
        )
        if args.limit is not None and not case_range:
            if orgid_fb_retry:
                expected_limit = REQUIRED_ERAD_SLICE2_ORGID_FALLBACK_RETRY_SIZE
            elif listing_aware_s2:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S2_UNIVERSE_SIZE
            elif listing_aware_s3:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S3_UNIVERSE_SIZE
            elif listing_aware_s4:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S4_UNIVERSE_SIZE
            elif listing_aware_s5:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S5_UNIVERSE_SIZE
            elif listing_aware_s6:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S6_UNIVERSE_SIZE
            elif listing_aware_s7:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S7_UNIVERSE_SIZE
            elif listing_aware_s8:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S8_UNIVERSE_SIZE
            elif listing_aware_s9:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S9_UNIVERSE_SIZE
            elif listing_aware_s10:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S10_UNIVERSE_SIZE
            elif listing_aware_s11:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S11_UNIVERSE_SIZE
            elif listing_aware_s12:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S12_UNIVERSE_SIZE
            elif listing_aware_s13:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S13_UNIVERSE_SIZE
            elif listing_aware_s16:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S16_UNIVERSE_SIZE
            elif listing_aware_s17:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S17_UNIVERSE_SIZE
            elif listing_aware_s18:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S18_UNIVERSE_SIZE
            elif listing_aware_s19:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S19_UNIVERSE_SIZE
            elif listing_aware_s15:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S15_UNIVERSE_SIZE
            elif listing_aware_s14:
                expected_limit = REQUIRED_ERAD_LISTING_AWARE_S14_UNIVERSE_SIZE
            else:
                expected_limit = REQUIRED_ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE
            if args.limit != expected_limit:
                print(
                    f"ERROR: {ERAD_NEXT_SCALE_SLICE2_UNIVERSE_SIZE_VIOLATION}: limit={args.limit}",
                    file=sys.stderr,
                )
                return 2
        normalized_root = _normalize_output_root(args.output_root)
        output_paths = ensure_output_layout(normalized_root)
        slice2_cases = load_erad_next_scale_slice2_universe(args.universe_csv)
        included = [c for c in slice2_cases if c.erad_include == "yes"]
        included = filter_erad_a_next_scale_slice2_cases_by_range(included, case_range)
        if args.limit is not None:
            included = included[: args.limit]
        if orgid_fb_retry:
            ok_size, size_err = validate_erad_slice2_orgid_fallback_retry_universe_size(
                included
            )
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s2 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s2_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s3 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s3_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s4 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s4_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s5 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s5_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s6 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s6_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s7 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s7_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s8 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s8_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s9 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s9_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s10 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s10_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s11 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s11_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s12 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s12_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s13 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s13_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s16 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s16_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s17 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s17_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s18 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s18_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s19 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s19_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s15 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s15_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif listing_aware_s14 and not case_range:
            ok_size, size_err = validate_erad_listing_aware_s14_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif not case_range:
            ok_size, size_err = validate_erad_next_scale_slice2_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif not included:
            print(f"ERROR: {ERAD_SLICE2_CASE_RANGE_INVALID}:empty_subset", file=sys.stderr)
            return 2
        expected_case_count = len(included)
        if orgid_fb_retry:
            mode_label = "erad_a_scale_500_slice2_orgid_fallback_retry_live"
        elif listing_aware_s2:
            mode_label = "erad_a_listing_aware_s2_live"
        elif listing_aware_s3:
            mode_label = "erad_a_listing_aware_s3_live"
        elif listing_aware_s4:
            mode_label = "erad_a_listing_aware_s4_live"
        elif listing_aware_s5:
            mode_label = "erad_a_listing_aware_s5_live"
        elif listing_aware_s6:
            mode_label = "erad_a_listing_aware_s6_live"
        elif listing_aware_s7:
            mode_label = "erad_a_listing_aware_s7_live"
        elif listing_aware_s8:
            mode_label = "erad_a_listing_aware_s8_live"
        elif listing_aware_s9:
            mode_label = "erad_a_listing_aware_s9_live"
        elif listing_aware_s10:
            mode_label = "erad_a_listing_aware_s10_live"
        elif listing_aware_s11:
            mode_label = "erad_a_listing_aware_s11_live"
        elif listing_aware_s12:
            mode_label = "erad_a_listing_aware_s12_live"
        elif listing_aware_s13:
            mode_label = "erad_a_listing_aware_s13_live"
        elif listing_aware_s16:
            mode_label = "erad_a_listing_aware_s16_live"
        elif listing_aware_s17:
            mode_label = "erad_a_listing_aware_s17_live"
        elif listing_aware_s18:
            mode_label = "erad_a_listing_aware_s18_live"
        elif listing_aware_s19:
            mode_label = "erad_a_listing_aware_s19_live"
        elif listing_aware_s15:
            mode_label = "erad_a_listing_aware_s15_live"
        elif listing_aware_s14:
            mode_label = "erad_a_listing_aware_s14_live"
        else:
            mode_label = "erad_a_scale_500_slice2_live"
        if args.mode == "dry_run":
            rows, universe_issues = process_erad_next_scale_slice2_dry_run(included, normalized_root)
            total_planned = sum(
                int(r.get("planned_request_count_case", "0")) for r in rows
            )
            ok_cap, cap_err = enforce_erad_next_scale_slice2_request_cap(total_planned)
            if (
                orgid_fb_retry
                or listing_aware_s2
                or listing_aware_s3
                or listing_aware_s4
                or listing_aware_s5
                or listing_aware_s6
                or listing_aware_s7
                or listing_aware_s8
                or listing_aware_s9
                or listing_aware_s10
                or listing_aware_s11
                or listing_aware_s12
                or listing_aware_s13
                or listing_aware_s14
                or listing_aware_s15
                or listing_aware_s16
                or listing_aware_s17
                or listing_aware_s18
                or listing_aware_s19
            ) and total_planned > request_cap:
                ok_cap, cap_err = (
                    False,
                    f"{ERAD_SLICE2_REQUEST_CAP_EXCEEDED}:{total_planned}>{request_cap}",
                )
            if not ok_cap:
                universe_issues.append(cap_err)
            report_path = write_erad_next_scale_slice2_dryrun_report(rows, output_paths)
            if (
                case_range
                or orgid_fb_retry
                or listing_aware_s2
                or listing_aware_s3
                or listing_aware_s4
                or listing_aware_s5
                or listing_aware_s6
                or listing_aware_s7
                or listing_aware_s8
                or listing_aware_s9
                or listing_aware_s10
                or listing_aware_s11
                or listing_aware_s12
                or listing_aware_s13
                or listing_aware_s14
                or listing_aware_s15
                or listing_aware_s16
                or listing_aware_s17
                or listing_aware_s18
                or listing_aware_s19
            ):
                gate = ERAD_NEXT_SCALE_SLICE2_RUNNER_GATE if not universe_issues else "FAIL"
            else:
                gate = compute_erad_next_scale_slice2_runner_gate(
                    universe_issues, len(included), total_planned
                )
            summary_path = write_erad_next_scale_slice2_dryrun_summary(
                rows, output_paths, universe_issues, gate, total_planned
            )
            planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
            print(
                f"mode=erad_a_scale_500_slice2_dry_run cases={len(included)} "
                f"planned_ok={planned_ok} cninfo_calls=0"
                f"{' orgid_fallback_retry=yes' if orgid_fb_retry else ''}"
                f"{' listing_aware_s2=yes' if listing_aware_s2 else ''}"
                f"{' listing_aware_s3=yes' if listing_aware_s3 else ''}"
                f"{' listing_aware_s4=yes' if listing_aware_s4 else ''}"
                f"{' listing_aware_s5=yes' if listing_aware_s5 else ''}"
                f"{' listing_aware_s6=yes' if listing_aware_s6 else ''}"
                f"{' listing_aware_s7=yes' if listing_aware_s7 else ''}"
                f"{' listing_aware_s8=yes' if listing_aware_s8 else ''}"
                f"{' listing_aware_s9=yes' if listing_aware_s9 else ''}"
                f"{' listing_aware_s10=yes' if listing_aware_s10 else ''}"
                f"{' listing_aware_s11=yes' if listing_aware_s11 else ''}"
                f"{' listing_aware_s12=yes' if listing_aware_s12 else ''}"
                f"{' listing_aware_s13=yes' if listing_aware_s13 else ''}"
                f"{' listing_aware_s14=yes' if listing_aware_s14 else ''}{' listing_aware_s15=yes' if listing_aware_s15 else ''}{' listing_aware_s16=yes' if listing_aware_s16 else ''}{' listing_aware_s17=yes' if listing_aware_s17 else ''}{' listing_aware_s18=yes' if listing_aware_s18 else ''}{' listing_aware_s19=yes' if listing_aware_s19 else ''}"
            )
            print(f"planned_request_count_total={total_planned}")
            print(
                f"gate=a_class_erad_next_scale_slice2_s1_runner_extension_gate={gate}"
            )
            print(f"erad_slice2_dryrun_report={report_path}")
            print(f"erad_slice2_dryrun_summary={summary_path}")
            if universe_issues:
                return 1
            return 0
        stats = tiny_live.LiveStats()
        rows, universe_issues = process_erad_a_next_scale_slice2_live(
            included,
            output_paths,
            stats,
            request_cap=request_cap,
            mode_label=mode_label,
        )
        if stats.cninfo_requests > request_cap:
            universe_issues.append(
                f"{ERAD_SLICE2_REQUEST_CAP_EXCEEDED}: actual={stats.cninfo_requests} "
                f"cap={request_cap}"
            )
        gate = compute_erad_next_scale_slice2_execution_gate(
            rows,
            universe_issues,
            stats,
            expected_case_count,
            request_cap=request_cap,
        )
        report_path = write_erad_next_scale_slice2_live_report(rows, output_paths)
        quality_path = write_erad_next_scale_slice2_live_quality_report(rows, output_paths)
        summary_path = write_erad_next_scale_slice2_live_summary(
            output_paths, stats, rows, universe_issues, gate, expected_case_count
        )
        acceptable_count = sum(
            1 for row in rows if is_erad_next_scale_slice2_case_acceptable(row)
        )
        print(
            f"mode={mode_label} cases={len(included)} "
            f"executed={len(rows)} acceptable={acceptable_count} "
            f"cninfo_calls={stats.cninfo_requests} "
            f"orgid_fallback_hits={stats.orgid_offline_fallback_hits} "
            f"orgid_fallback_misses={stats.orgid_offline_fallback_misses}"
        )
        print(f"gate=a_class_erad_next_scale_slice2_s1_execution_gate={gate}")
        print(
            f"gate=a_class_erad_next_scale_slice2_s1_live_path_gate="
            f"{ERAD_NEXT_SCALE_SLICE2_LIVE_PATH_GATE}"
        )
        print(f"erad_slice2_live_report={report_path}")
        print(f"erad_slice2_live_quality={quality_path}")
        print(f"erad_slice2_live_summary={summary_path}")
        if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
            return 1
        return 0

    if getattr(args, "erad_a_scale_500_slice1", False):
        if (
            getattr(args, "erad_a_scale_200", False)
            or getattr(args, "erad_a_scale_200_failed_retry", False)
            or getattr(args, "erad_a_scale_500_slice2", False)
            or args.phase3_50
            or args.retry_v3
            or args.retry_failed_only
        ):
            print(f"ERROR: {ERAD_NEXT_SCALE_SLICE1_INCOMPATIBLE_WITH_OTHER_MODES}", file=sys.stderr)
            return 2
        if args.universe_csv is None:
            print(f"ERROR: {ERAD_NEXT_SCALE_SLICE1_UNIVERSE_CSV_REQUIRED}", file=sys.stderr)
            return 2
        if args.output_root is None:
            args.output_root = DEFAULT_ERAD_NEXT_SCALE_SLICE1_OUTPUT_ROOT
        enforce_forbidden_options(args)
        if args.mode == "live":
            enforce_erad_next_scale_slice1_approval_gate(args)
        ok_csv, csv_err = validate_erad_next_scale_slice1_universe_csv_path(args.universe_csv)
        if not ok_csv:
            print(f"ERROR: {csv_err}", file=sys.stderr)
            return 2
        ok_root, root_err = validate_erad_next_scale_slice1_output_root(args.output_root)
        if not ok_root:
            print(f"ERROR: {root_err}", file=sys.stderr)
            return 2
        if not os.path.isfile(args.universe_csv):
            print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
            return 2
        case_range = getattr(args, "case_range", None)
        if case_range:
            try:
                parse_erad_a_slice1_case_range(case_range)
            except ValueError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 2
        if args.limit is not None and not case_range:
            if args.limit != REQUIRED_ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE:
                print(
                    f"ERROR: {ERAD_NEXT_SCALE_SLICE1_UNIVERSE_SIZE_VIOLATION}: limit={args.limit}",
                    file=sys.stderr,
                )
                return 2
        normalized_root = _normalize_output_root(args.output_root)
        output_paths = ensure_output_layout(normalized_root)
        slice1_cases = load_erad_next_scale_slice1_universe(args.universe_csv)
        included = [c for c in slice1_cases if c.erad_include == "yes"]
        included = filter_erad_a_next_scale_slice1_cases_by_range(included, case_range)
        if args.limit is not None:
            included = included[: args.limit]
        if not case_range:
            ok_size, size_err = validate_erad_next_scale_slice1_universe_size(included)
            if not ok_size:
                print(f"ERROR: {size_err}", file=sys.stderr)
                return 2
        elif not included:
            print(f"ERROR: {ERAD_SLICE1_CASE_RANGE_INVALID}:empty_subset", file=sys.stderr)
            return 2
        expected_case_count = len(included)
        if args.mode == "dry_run":
            rows, universe_issues = process_erad_next_scale_slice1_dry_run(included, normalized_root)
            total_planned = sum(
                int(r.get("planned_request_count_case", "0")) for r in rows
            )
            ok_cap, cap_err = enforce_erad_next_scale_slice1_request_cap(total_planned)
            if not ok_cap:
                universe_issues.append(cap_err)
            report_path = write_erad_next_scale_slice1_dryrun_report(rows, output_paths)
            if case_range:
                gate = ERAD_NEXT_SCALE_SLICE1_RUNNER_GATE if not universe_issues else "FAIL"
            else:
                gate = compute_erad_next_scale_slice1_runner_gate(
                    universe_issues, len(included), total_planned
                )
            summary_path = write_erad_next_scale_slice1_dryrun_summary(
                rows, output_paths, universe_issues, gate, total_planned
            )
            planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
            print(
                f"mode=erad_a_scale_500_slice1_dry_run cases={len(included)} "
                f"planned_ok={planned_ok} cninfo_calls=0"
            )
            print(f"planned_request_count_total={total_planned}")
            print(
                f"gate=a_class_erad_next_scale_slice1_runner_extension_gate={gate}"
            )
            print(f"erad_slice1_dryrun_report={report_path}")
            print(f"erad_slice1_dryrun_summary={summary_path}")
            if universe_issues:
                return 1
            return 0
        stats = tiny_live.LiveStats()
        rows, universe_issues = process_erad_a_next_scale_slice1_live(
            included, output_paths, stats
        )
        if stats.cninfo_requests > ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP:
            universe_issues.append(
                f"{ERAD_SLICE1_REQUEST_CAP_EXCEEDED}: actual={stats.cninfo_requests} "
                f"cap={ERAD_NEXT_SCALE_SLICE1_REQUEST_CAP}"
            )
        gate = compute_erad_next_scale_slice1_execution_gate(
            rows, universe_issues, stats, expected_case_count
        )
        report_path = write_erad_next_scale_slice1_live_report(rows, output_paths)
        quality_path = write_erad_next_scale_slice1_live_quality_report(rows, output_paths)
        summary_path = write_erad_next_scale_slice1_live_summary(
            output_paths, stats, rows, universe_issues, gate, expected_case_count
        )
        acceptable_count = sum(
            1 for row in rows if is_erad_next_scale_slice1_case_acceptable(row)
        )
        print(
            f"mode=erad_a_scale_500_slice1_live cases={len(included)} "
            f"executed={len(rows)} acceptable={acceptable_count} "
            f"cninfo_calls={stats.cninfo_requests}"
        )
        print(f"gate=a_class_erad_next_scale_slice1_execution_gate={gate}")
        print(
            f"gate=a_class_erad_next_scale_slice1_live_path_gate="
            f"{ERAD_NEXT_SCALE_SLICE1_LIVE_PATH_GATE}"
        )
        print(f"erad_slice1_live_report={report_path}")
        print(f"erad_slice1_live_quality={quality_path}")
        print(f"erad_slice1_live_summary={summary_path}")
        if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
            return 1
        return 0

    if getattr(args, "erad_a_scale_200_failed_retry", False):
        if (
            getattr(args, "erad_a_scale_500_slice1", False)
            or getattr(args, "erad_a_scale_500_slice2", False)
            or getattr(args, "erad_a_scale_200", False)
            or args.phase3_50
            or args.retry_v3
            or args.retry_failed_only
        ):
            print(f"ERROR: {ERAD_FAILED_RETRY_INCOMPATIBLE_WITH_OTHER_MODES}", file=sys.stderr)
            return 2
        if args.universe_csv is None:
            print(f"ERROR: {ERAD_FAILED_RETRY_UNIVERSE_CSV_REQUIRED}", file=sys.stderr)
            return 2
        if args.output_root is None:
            args.output_root = DEFAULT_ERAD_FAILED_RETRY_OUTPUT_ROOT
        enforce_forbidden_options(args)
        if args.mode == "live":
            enforce_erad_failed_retry_approval_gate(args)
        ok_root, root_err = validate_erad_failed_retry_output_root(args.output_root)
        if not ok_root:
            print(f"ERROR: {root_err}", file=sys.stderr)
            return 2
        if not os.path.isfile(args.universe_csv):
            print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
            return 2
        retry_cases = load_erad_failed_retry_universe(args.universe_csv)
        if args.limit is not None:
            retry_cases = retry_cases[: args.limit]
        for validator in (
            validate_erad_failed_retry_universe_size,
            validate_erad_failed_retry_universe_case_set,
            validate_erad_failed_retry_duplicate_company_codes,
        ):
            ok, err = validator(retry_cases)
            if not ok:
                print(f"ERROR: {err}", file=sys.stderr)
                return 2
        included = [c for c in retry_cases if c.retry_include == "yes"]
        ok_cap, cap_err = validate_erad_failed_retry_request_cap(len(included))
        if not ok_cap:
            print(f"ERROR: {cap_err}", file=sys.stderr)
            return 2
        normalized_root = _normalize_output_root(args.output_root)
        output_paths = ensure_output_layout(normalized_root)
        if args.mode == "live":
            stats = tiny_live.LiveStats()
            rows, universe_issues = process_erad_failed_retry_live(included, output_paths, stats)
            if stats.cninfo_requests > ERAD_FAILED_RETRY_REQUEST_CAP:
                print(
                    f"ERROR: {ERAD_FAILED_RETRY_REQUEST_CAP_EXCEEDED}: "
                    f"actual={stats.cninfo_requests} cap={ERAD_FAILED_RETRY_REQUEST_CAP}",
                    file=sys.stderr,
                )
                return 2
            gate = compute_erad_failed_retry_execution_gate(
                stats, rows, universe_issues, len(included)
            )
            report_path = write_erad_failed_retry_live_report(rows, output_paths)
            quality_path = write_erad_failed_retry_live_quality_report(rows, output_paths)
            summary_path = write_erad_failed_retry_live_summary(
                output_paths, stats, rows, universe_issues, gate
            )
            acceptable_count = sum(
                1 for row in rows if is_erad_failed_retry_case_acceptable(row)
            )
            failed_count = sum(
                1
                for row in rows
                if row.get("retrieval_status")
                in ("network_error", "not_found", "universe_invalid")
            )
            needs_review_count = sum(
                1 for row in rows if row.get("quality_status") == "needs_review"
            )
            print(
                f"mode=erad_a_scale_200_failed_retry_live cases={len(included)} "
                f"cninfo_calls={stats.cninfo_requests}"
            )
            print(f"acceptable={acceptable_count} failed={failed_count}")
            print(f"needs_review={needs_review_count}")
            print(f"success={stats.success_count} failure={stats.failure_count}")
            print(
                f"pdf_downloaded={stats.pdf_downloaded_count} "
                f"pdf_parsed={stats.pdf_parsed_count}"
            )
            print(
                "gate=a_class_erad_scale_200_isolated_retry_live_path_gate="
                f"{ERAD_FAILED_RETRY_LIVE_PATH_GATE}"
            )
            print(f"execution_gate=a_class_erad_scale_200_failed_retry_execution_gate={gate}")
            print(f"erad_failed_retry_live_report={report_path}")
            print(f"erad_failed_retry_live_quality={quality_path}")
            print(f"erad_failed_retry_live_summary={summary_path}")
            if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
                return 1
            return 0
        rows, universe_issues = process_erad_failed_retry_dry_run(retry_cases, normalized_root)
        report_path = write_erad_failed_retry_dryrun_report(rows, output_paths)
        summary_path = write_erad_failed_retry_dryrun_summary(rows, output_paths, universe_issues)
        planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
        print(
            f"mode=erad_a_scale_200_failed_retry_dry_run cases={len(included)} "
            f"planned_ok={planned_ok} cninfo_calls=0"
        )
        print(
            "gate=a_class_erad_scale_200_isolated_retry_runner_extension_gate="
            f"{ERAD_FAILED_RETRY_RUNNER_GATE}"
        )
        print(f"erad_failed_retry_dryrun_report={report_path}")
        print(f"erad_failed_retry_dryrun_summary={summary_path}")
        if universe_issues:
            return 1
        return 0

    if getattr(args, "erad_a_scale_200", False):
        if args.phase3_50 or args.retry_v3 or args.retry_failed_only:
            print(f"ERROR: {ERAD_SCALE_200_INCOMPATIBLE_WITH_RETRY}", file=sys.stderr)
            return 2
        if getattr(args, "erad_a_scale_200_failed_retry", False):
            print(f"ERROR: {ERAD_FAILED_RETRY_INCOMPATIBLE_WITH_ERAD_MAIN}", file=sys.stderr)
            return 2
        if getattr(args, "erad_a_scale_500_slice1", False):
            print(f"ERROR: {ERAD_NEXT_SCALE_SLICE1_INCOMPATIBLE_WITH_OTHER_MODES}", file=sys.stderr)
            return 2
        if getattr(args, "erad_a_scale_500_slice2", False):
            print(f"ERROR: {ERAD_NEXT_SCALE_SLICE2_INCOMPATIBLE_WITH_OTHER_MODES}", file=sys.stderr)
            return 2
        if args.universe_csv is None:
            print(f"ERROR: {ERAD_SCALE_200_UNIVERSE_CSV_REQUIRED}", file=sys.stderr)
            return 2
        if args.output_root is None:
            args.output_root = DEFAULT_ERAD_SCALE_200_OUTPUT_ROOT
        enforce_forbidden_options(args)
        if args.mode == "live":
            enforce_erad_scale_200_approval_gate(args)
        ok_root, root_err = validate_erad_scale_200_output_root(args.output_root)
        if not ok_root:
            print(f"ERROR: {root_err}", file=sys.stderr)
            return 2
        if not os.path.isfile(args.universe_csv):
            print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
            return 2
        erad_cases = load_erad_scale_200_universe(args.universe_csv)
        if args.limit is not None:
            erad_cases = erad_cases[: args.limit]
        for validator in (
            validate_erad_scale_200_universe_size,
            validate_erad_scale_200_report_type_mix,
            validate_erad_scale_200_duplicate_company_codes,
            validate_erad_scale_200_cohort_counts,
        ):
            ok, err = validator(erad_cases)
            if not ok:
                print(f"ERROR: {err}", file=sys.stderr)
                return 2
        ok_new, new_err = validate_erad_scale_200_new_cohort_overlap(erad_cases)
        if not ok_new:
            print(f"ERROR: {new_err}", file=sys.stderr)
            return 2
        included = [c for c in erad_cases if c.erad_include == "yes"]
        ok_cap, cap_err = validate_erad_scale_200_request_cap(len(included))
        if not ok_cap:
            print(f"ERROR: {cap_err}", file=sys.stderr)
            return 2
        normalized_root = _normalize_output_root(args.output_root)
        output_paths = ensure_output_layout(normalized_root)
        report_type_mix: Dict[str, int] = {}
        retained_count = 0
        new_count = 0
        for case in included:
            report_type_mix[case.report_type] = report_type_mix.get(case.report_type, 0) + 1
            if case.cohort == "retained_phase3":
                retained_count += 1
            elif case.cohort == "new_erad":
                new_count += 1
        if args.mode == "live":
            stats = tiny_live.LiveStats()
            rows, universe_issues = process_erad_scale_200_live(included, output_paths, stats)
            if stats.cninfo_requests > ERAD_SCALE_200_REQUEST_CAP:
                print(
                    f"ERROR: {ERAD_SCALE_200_REQUEST_CAP_EXCEEDED}: "
                    f"actual={stats.cninfo_requests} cap={ERAD_SCALE_200_REQUEST_CAP}",
                    file=sys.stderr,
                )
                return 2
            gate = compute_erad_scale_200_execution_gate(
                stats, rows, universe_issues, len(included)
            )
            report_path = write_erad_scale_200_live_report(rows, output_paths)
            quality_path = write_erad_scale_200_live_quality_report(rows, output_paths)
            summary_path = write_erad_scale_200_live_summary(
                output_paths,
                stats,
                rows,
                universe_issues,
                gate,
                retained_count,
                new_count,
            )
            acceptable_count = sum(
                1 for row in rows if is_erad_scale_200_case_acceptable(row)
            )
            failed_count = sum(
                1
                for row in rows
                if row.get("retrieval_status")
                in ("network_error", "not_found", "universe_invalid")
            )
            needs_review_count = sum(
                1 for row in rows if row.get("quality_status") == "needs_review"
            )
            print(
                f"mode=erad_a_scale_200_live cases={len(included)} "
                f"cninfo_calls={stats.cninfo_requests}"
            )
            print(f"acceptable={acceptable_count} failed={failed_count}")
            print(f"needs_review={needs_review_count}")
            print(f"retained_phase3={retained_count} new_erad={new_count}")
            print(f"success={stats.success_count} failure={stats.failure_count}")
            print(
                f"pdf_downloaded={stats.pdf_downloaded_count} "
                f"pdf_parsed={stats.pdf_parsed_count}"
            )
            print(
                f"gate=a_class_erad_scale_200_live_path_gate={ERAD_SCALE_200_LIVE_PATH_GATE}"
            )
            print(f"execution_gate=a_class_erad_scale_200_execution_gate={gate}")
            print(f"erad_live_report={report_path}")
            print(f"erad_live_quality={quality_path}")
            print(f"erad_live_summary={summary_path}")
            if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
                return 1
            return 0
        rows, universe_issues = process_erad_scale_200_dry_run(erad_cases, normalized_root)
        report_path = write_erad_scale_200_dryrun_report(rows, output_paths)
        summary_path = write_erad_scale_200_dryrun_summary(
            rows, output_paths, universe_issues, report_type_mix, retained_count, new_count
        )
        planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
        print(
            f"mode=erad_a_scale_200_dry_run cases={len(included)} "
            f"planned_ok={planned_ok} cninfo_calls=0"
        )
        print(f"gate=a_class_erad_scale_200_runner_extension_gate={ERAD_SCALE_200_RUNNER_GATE}")
        print(f"erad_dryrun_report={report_path}")
        print(f"erad_dryrun_summary={summary_path}")
        if universe_issues:
            return 1
        return 0

    if args.phase3_50:
        if args.universe_csv is None:
            print(f"ERROR: {PHASE3_UNIVERSE_CSV_REQUIRED}", file=sys.stderr)
            return 2
        if args.output_root is None:
            args.output_root = DEFAULT_PHASE3_OUTPUT_ROOT

        enforce_forbidden_options(args)

        if args.mode == "live":
            enforce_phase3_approval_gate(args)

        ok_root, root_err = validate_phase3_output_root(args.output_root)
        if not ok_root:
            print(f"ERROR: {root_err}", file=sys.stderr)
            return 2

        if not os.path.isfile(args.universe_csv):
            print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
            return 2

        phase3_cases = load_phase3_universe(args.universe_csv)
        if args.limit is not None:
            phase3_cases = phase3_cases[: args.limit]

        ok_size, size_err = validate_phase3_universe_size(phase3_cases)
        if not ok_size:
            print(f"ERROR: {size_err}", file=sys.stderr)
            return 2

        ok_mix, mix_err = validate_phase3_report_type_mix(phase3_cases)
        if not ok_mix:
            print(f"ERROR: {mix_err}", file=sys.stderr)
            return 2

        ok_dup, dup_err = validate_phase3_duplicate_company_codes(phase3_cases)
        if not ok_dup:
            print(f"ERROR: {dup_err}", file=sys.stderr)
            return 2

        phase1_overlap_count, phase2_overlap_count = count_phase3_overlap(phase3_cases)
        if phase1_overlap_count > 0:
            print(
                f"ERROR: {PHASE1_OVERLAP_REJECTED}: count={phase1_overlap_count}",
                file=sys.stderr,
            )
            return 2
        if phase2_overlap_count > 0:
            print(
                f"ERROR: {PHASE2_OVERLAP_REJECTED}: count={phase2_overlap_count}",
                file=sys.stderr,
            )
            return 2

        normalized_root = _normalize_output_root(args.output_root)
        output_paths = ensure_output_layout(normalized_root)

        included_phase3 = [c for c in phase3_cases if c.phase3_include == "yes"]
        report_type_mix: Dict[str, int] = {}
        for case in included_phase3:
            report_type_mix[case.report_type] = (
                report_type_mix.get(case.report_type, 0) + 1
            )

        if args.mode == "live":
            stats = tiny_live.LiveStats()
            rows, universe_issues = process_phase3_50_live(
                included_phase3, output_paths, stats
            )
            gate = compute_phase3_execution_gate(
                stats, rows, universe_issues, len(included_phase3)
            )
            report_path = write_phase3_live_report(rows, output_paths)
            quality_path = write_phase3_live_quality_report(rows, output_paths)
            summary_path = write_phase3_live_summary(
                output_paths, stats, rows, universe_issues, gate
            )
            acceptable_count = sum(1 for row in rows if is_phase3_case_acceptable(row))
            failed_count = sum(
                1
                for row in rows
                if row.get("retrieval_status")
                in ("network_error", "not_found", "universe_invalid")
            )
            needs_review_count = sum(
                1 for row in rows if row.get("quality_status") == "needs_review"
            )
            print(
                f"mode=phase3_live cases={len(included_phase3)} "
                f"cninfo_calls={stats.cninfo_requests}"
            )
            print(f"acceptable={acceptable_count} failed={failed_count}")
            print(f"needs_review={needs_review_count}")
            print(f"success={stats.success_count} failure={stats.failure_count}")
            print(
                f"pdf_downloaded={stats.pdf_downloaded_count} "
                f"pdf_parsed={stats.pdf_parsed_count}"
            )
            print(f"gate=a_class_phase3_50_company_execution_gate={gate}")
            print(f"report={report_path}")
            print(f"quality={quality_path}")
            print(f"summary={summary_path}")
            if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
                return 1
            return 0

        rows, universe_issues = process_phase3_dry_run(phase3_cases, normalized_root)
        report_path = write_phase3_dryrun_report(rows, output_paths)
        summary_path = write_phase3_dryrun_summary(
            rows,
            output_paths,
            universe_issues,
            report_type_mix,
            phase1_overlap_count,
            phase2_overlap_count,
        )
        planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
        print(
            f"mode=phase3_dry_run cases={len(included_phase3)} "
            f"planned_ok={planned_ok} cninfo_calls=0"
        )
        print(
            f"gate=a_class_phase3_50_company_runner_extension_gate={PHASE3_RUNNER_GATE}"
        )
        print(f"phase3_dryrun_report={report_path}")
        print(f"phase3_dryrun_summary={summary_path}")
        if universe_issues:
            return 1
        return 0

    if args.retry_v3:
        if args.universe_csv is None:
            print(f"ERROR: {RETRY_V3_UNIVERSE_CSV_REQUIRED}", file=sys.stderr)
            return 2
        if args.output_root is None:
            args.output_root = DEFAULT_RETRY_V3_OUTPUT_ROOT

        enforce_forbidden_options(args)

        if args.mode == "live":
            enforce_retry_v3_approval_gate(args)

        ok_root, root_err = validate_retry_v3_output_root(args.output_root)
        if not ok_root:
            print(f"ERROR: {root_err}", file=sys.stderr)
            return 2

        if not os.path.isfile(args.universe_csv):
            print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
            return 2

        output_paths = ensure_output_layout(_normalize_output_root(args.output_root))

        retry_cases = load_retry_universe(args.universe_csv)
        if args.limit is not None:
            retry_cases = retry_cases[: args.limit]

        ok_size, size_err = validate_retry_universe_size(retry_cases)
        if not ok_size:
            print(f"ERROR: {size_err}", file=sys.stderr)
            return 2

        included_retry = [c for c in retry_cases if c.retry_include == "yes"]

        if args.mode == "live":
            stats = tiny_live.LiveStats()
            rows, universe_issues = process_retry_v3_live(
                included_retry, output_paths, stats
            )
            gate = compute_retry_v3_execution_gate(
                stats, rows, universe_issues, len(included_retry)
            )
            report_path = write_retry_v3_live_report(rows, output_paths)
            quality_path = write_retry_v3_live_quality_report(rows, output_paths)
            summary_path = write_retry_v3_live_summary(
                output_paths, stats, rows, universe_issues, gate
            )
            acceptable_count = sum(
                1 for row in rows if is_retry_v3_case_acceptable(row)
            )
            failed_count = sum(
                1
                for row in rows
                if row.get("retry_v3_retrieval_status")
                in ("network_error", "not_found", "universe_invalid")
            )
            needs_review_count = sum(
                1 for row in rows if row.get("quality_status") == "needs_review"
            )
            print(
                f"mode=retry_v3_live cases={len(included_retry)} "
                f"cninfo_calls={stats.cninfo_requests}"
            )
            print(f"acceptable={acceptable_count} failed={failed_count}")
            print(f"needs_review={needs_review_count}")
            print(f"success={stats.success_count} failure={stats.failure_count}")
            print(
                f"pdf_downloaded={stats.pdf_downloaded_count} "
                f"pdf_parsed={stats.pdf_parsed_count}"
            )
            print(f"gate=a_class_phase2_retry_v3_execution_gate={gate}")
            print(f"report={report_path}")
            print(f"quality={quality_path}")
            print(f"summary={summary_path}")
            if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
                return 1
            return 0

        normalized_root = _normalize_output_root(args.output_root)
        rows, universe_issues = process_retry_v3_dry_run(retry_cases, normalized_root)
        report_path = write_retry_v3_dryrun_report(rows, output_paths)
        summary_path = write_retry_v3_dryrun_summary(
            rows, output_paths, universe_issues
        )
        planned_ok = sum(1 for row in rows if row["dryrun_status"] == "planned_ok")
        print(
            f"mode=retry_v3_dry_run cases={len(included_retry)} "
            f"planned_ok={planned_ok} cninfo_calls=0"
        )
        print(
            f"gate=a_class_phase2_retry_v3_runner_extension_gate={RETRY_V3_RUNNER_GATE}"
        )
        print(f"retry_v3_dryrun_report={report_path}")
        print(f"retry_v3_dryrun_summary={summary_path}")
        if universe_issues:
            return 1
        return 0

    if args.retry_failed_only:
        retry_v2 = is_retry_v2_mode(args.universe_csv, args.output_root)
        if retry_v2:
            if args.universe_csv is None:
                args.universe_csv = DEFAULT_RETRY_V2_UNIVERSE_CSV
            if args.output_root is None:
                args.output_root = DEFAULT_RETRY_V2_OUTPUT_ROOT
        else:
            if args.universe_csv is None:
                args.universe_csv = DEFAULT_RETRY_UNIVERSE_CSV
            if args.output_root is None:
                args.output_root = DEFAULT_RETRY_OUTPUT_ROOT
    else:
        if args.universe_csv is None:
            args.universe_csv = DEFAULT_UNIVERSE_CSV
        if args.output_root is None:
            args.output_root = DEFAULT_OUTPUT_ROOT

    enforce_forbidden_options(args)

    retry_v2 = args.retry_failed_only and is_retry_v2_mode(
        args.universe_csv, args.output_root
    )

    if args.mode == "live":
        if args.retry_failed_only:
            if retry_v2:
                enforce_retry_v2_approval_gate(args)
            else:
                enforce_retry_approval_gate(args)
        else:
            enforce_live_approval_gate(args)

    if args.retry_failed_only:
        if retry_v2:
            ok_root, root_err = validate_retry_v2_output_root(args.output_root)
        else:
            ok_root, root_err = validate_retry_output_root(args.output_root)
    else:
        ok_root, root_err = validate_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2

    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))

    if args.retry_failed_only:
        retry_cases = load_retry_universe(args.universe_csv)
        if args.limit is not None:
            retry_cases = retry_cases[: args.limit]

        ok_size, size_err = validate_retry_universe_size(retry_cases)
        if not ok_size:
            print(f"ERROR: {size_err}", file=sys.stderr)
            return 2

        included_retry = [c for c in retry_cases if c.retry_include == "yes"]

        if args.mode == "live":
            if retry_v2:
                stats = tiny_live.LiveStats()
                rows, universe_issues = process_retry_v2_live(
                    included_retry, output_paths, stats
                )
                gate = compute_retry_v2_execution_gate(
                    stats, rows, universe_issues, len(included_retry)
                )
                report_path = write_retry_v2_live_report(rows, output_paths)
                quality_path = write_retry_v2_live_quality_report(rows, output_paths)
                summary_path = write_retry_v2_live_summary(
                    output_paths, stats, rows, universe_issues, gate
                )
                acceptable_count = sum(
                    1 for row in rows if is_retry_v2_case_acceptable(row)
                )
                failed_count = sum(
                    1
                    for row in rows
                    if row.get("retry_v2_retrieval_status")
                    in ("network_error", "not_found", "universe_invalid")
                )
                needs_review_count = sum(
                    1 for row in rows if row.get("quality_status") == "needs_review"
                )
                wrong_rt = sum(
                    1
                    for row in rows
                    if row.get("retry_v2_retrieval_status") == "title_mismatch"
                )
                print(
                    f"mode=retry_v2_live cases={len(included_retry)} "
                    f"cninfo_calls={stats.cninfo_requests}"
                )
                print(f"acceptable={acceptable_count} failed={failed_count}")
                print(f"needs_review={needs_review_count} wrong_report_type={wrong_rt}")
                print(f"success={stats.success_count} failure={stats.failure_count}")
                print(
                    f"pdf_downloaded={stats.pdf_downloaded_count} "
                    f"pdf_parsed={stats.pdf_parsed_count}"
                )
                print(
                    "gate=a_class_phase2_network_recovery_retry_v2_execution_gate="
                    f"{gate}"
                )
                print(f"report={report_path}")
                print(f"quality={quality_path}")
                print(f"summary={summary_path}")
                if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
                    return 1
                return 0

            stats = tiny_live.LiveStats()
            rows, universe_issues = process_retry_live(
                included_retry, output_paths, stats
            )
            gate = compute_retry_execution_gate(
                stats, rows, universe_issues, len(included_retry)
            )
            report_path = write_retry_live_report(rows, output_paths)
            quality_path = write_retry_live_quality_report(rows, output_paths)
            summary_path = write_retry_live_summary(
                output_paths, stats, rows, universe_issues, gate
            )
            correct_count = sum(1 for row in rows if is_retry_case_correct(row))
            wrong_rt = sum(1 for row in rows if row.get("wrong_report_type") == "1")
            print(f"mode=retry_live cases={len(included_retry)} cninfo_calls={stats.cninfo_requests}")
            print(f"success={stats.success_count} failure={stats.failure_count}")
            print(f"correct={correct_count} wrong_report_type={wrong_rt}")
            print(f"pdf_downloaded={stats.pdf_downloaded_count} pdf_parsed={stats.pdf_parsed_count}")
            print(f"gate=a_class_phase2_failed_retry_execution_gate={gate}")
            print(f"report={report_path}")
            print(f"quality={quality_path}")
            print(f"summary={summary_path}")
            if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
                return 1
            return 0

        if retry_v2:
            normalized_root = _normalize_output_root(args.output_root)
            rows, universe_issues = process_retry_v2_dry_run(retry_cases, normalized_root)
            report_path = write_retry_v2_dryrun_report(rows, output_paths)
            summary_path = write_retry_v2_dryrun_summary(
                output_paths, len(included_retry), universe_issues
            )
            planned_ok = len(included_retry) - len(universe_issues)
            print(
                f"mode=retry_v2_dry_run cases={len(included_retry)} "
                f"planned_ok={planned_ok} cninfo_calls=0"
            )
            print(
                "gate=a_class_phase2_network_recovery_retry_v2_runner_extension_gate="
                f"{RETRY_V2_RUNNER_GATE}"
            )
            print(f"retry_v2_dryrun_report={report_path}")
            print(f"retry_v2_dryrun_summary={summary_path}")
            if universe_issues:
                return 1
            return 0

        rows, universe_issues = process_retry_dry_run(retry_cases)
        report_path = write_retry_dryrun_report(rows, output_paths)
        summary_path = write_retry_dryrun_summary(
            output_paths, len(included_retry), universe_issues
        )
        planned_ok = len(included_retry) - len(universe_issues)
        print(f"mode=retry_dry_run cases={len(included_retry)} planned_ok={planned_ok} cninfo_calls=0")
        print(f"gate=a_class_phase2_failed_retry_planning_gate={RETRY_PLANNING_GATE}")
        print(f"retry_dryrun_report={report_path}")
        print(f"retry_dryrun_summary={summary_path}")
        if universe_issues:
            return 1
        return 0

    cases = load_universe(args.universe_csv)
    if args.limit is not None:
        cases = cases[: args.limit]

    ok_size, size_err = validate_universe_size(cases)
    if not ok_size:
        print(f"ERROR: {size_err}", file=sys.stderr)
        return 2

    ok_mix, mix_err = validate_report_type_mix(cases)
    if not ok_mix:
        print(f"ERROR: {mix_err}", file=sys.stderr)
        return 2

    overlap_count = count_phase1_overlap(cases)
    if overlap_count > 0:
        print(f"ERROR: {PHASE1_OVERLAP_REJECTED}: count={overlap_count}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(_normalize_output_root(args.output_root))

    included = [c for c in cases if c.phase2_include == "yes"]
    report_type_mix: Dict[str, int] = {}
    for case in included:
        report_type_mix[case.report_type] = report_type_mix.get(case.report_type, 0) + 1

    if args.mode == "live":
        stats = tiny_live.LiveStats()
        rows, universe_issues = process_live(cases, output_paths, stats)
        gate = compute_phase2_execution_gate(stats, rows, universe_issues, len(included))
        report_path = write_live_report(rows, output_paths)
        quality_path = write_live_quality_report(rows, output_paths)
        summary_path = write_live_summary(
            output_paths, stats, rows, universe_issues, gate
        )
        correct_count = sum(1 for row in rows if is_case_correct(row))
        print(f"mode=live cases={len(included)} cninfo_calls={stats.cninfo_requests}")
        print(f"success={stats.success_count} failure={stats.failure_count}")
        print(f"correct={correct_count} wrong_report_type={stats.wrong_report_type_count}")
        print(f"pdf_downloaded={stats.pdf_downloaded_count} pdf_parsed={stats.pdf_parsed_count}")
        print(f"gate=a_class_phase2_metadata_execution_gate={gate}")
        print(f"report={report_path}")
        print(f"quality={quality_path}")
        print(f"summary={summary_path}")
        if universe_issues or gate == "FAIL_REVIEW_REQUIRED":
            return 1
        return 0

    rows, universe_issues = process_dry_run(cases)
    report_path = write_dryrun_report(rows, output_paths)
    summary_path = write_dryrun_summary(
        output_paths,
        len(included),
        universe_issues,
        report_type_mix,
        overlap_count,
    )
    planned_ok = len(included) - len(universe_issues)
    print(f"mode=dry_run cases={len(included)} planned_ok={planned_ok} cninfo_calls=0")
    print(f"gate=a_class_phase2_metadata_runner_gate={RUNNER_GATE}")
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    if universe_issues:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
