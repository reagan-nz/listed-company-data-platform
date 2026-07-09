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
from datetime import date, datetime, timezone
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
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

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
