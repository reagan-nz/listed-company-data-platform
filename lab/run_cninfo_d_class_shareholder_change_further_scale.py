#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 shareholder_change further-scale（~50）孤立根 runner。

denser 策略：type=desc 多日并集（2026-07-01 + 2026-07-14）共享探针 + 离线 SECCODE 过滤。
禁止 type=inc+2026-07-03 作 sole found 锚；不写入 SC next-slice / first-slice / ESH / AT 冻结根。

用法：
  .venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale.py --build-universe-lock
  .venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale.py --dry-run \\
      --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_universe_lock_20260716.csv \\
      --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale
  .venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale.py --live \\
      --approve-d-class-shareholder-change-further-scale \\
      --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_universe_lock_20260716.csv \\
      --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import requests

import run_cninfo_d_class_tiny_live_validation as core  # noqa: E402

BASE_DIR = core.BASE_DIR
VALIDATION = os.path.join(BASE_DIR, "outputs", "validation")

COMPONENT = "shareholder_change"
QUERY_TYPE = "desc"
FORBIDDEN_QUERY_TYPE = "inc"
PRIMARY_TDATE = "2026-07-01"
ADJACENT_TDATE = "2026-07-14"
FORBIDDEN_SPARSE_TDATE = "2026-07-03"
QUERY_MODE = "type_desc_multi_day_union"
ENDPOINT = "https://www.cninfo.com.cn/data20/shareholeder/detail"
SHARED_PROBE_KEY = "type_desc_union_2026-07-01_2026-07-14"
EXPECTED_SIZE = 50
# excellence：acceptable >= 95% → ≥48/50；且 fail/http=0
PASS_THRESHOLD = 48
EXCELLENCE_ACCEPTABLE_RATE = 0.95
CASE_ID_START = 201
CASE_ID_END = 250
FOUND_SLOTS = 48
EMPTY_CONTROL_TARGET = 2

DEFAULT_OUTPUT_ROOT = os.path.join(
    VALIDATION, "cninfo_d_class_shareholder_change_further_scale"
)
DEFAULT_UNIVERSE_CSV = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_further_scale_universe_lock_20260716.csv",
)
SHAREHOLDER_DETAIL_CITE_JSON = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_further_scale_shareholder_detail_cite_20260716.json",
)

FORBIDDEN_CODES = {"688671", "301259"}
# next-slice / first-slice 已锁公司码：不得再入 found 槽
EXCLUDED_PRIOR_SLICE_CODES = {
    "000550",
    "000895",
    "600000",
    "002415",
    "601988",
}
EMPTY_CONTROL_CANDIDATES = [
    ("000895", "双汇发展"),
    ("601988", "中国银行"),
    ("600519", "贵州茅台"),
    ("000858", "五粮液"),
]

FROZEN_BLOCK_ROOTS = (
    os.path.join(VALIDATION, "cninfo_d_class_shareholder_change_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_shareholder_change_first_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_further_scale"),
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_further_scale_s200"),
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_further_scale_s1000"),
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_first_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_further_scale"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_further_scale_s200"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_further_scale_s1000"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_first_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_equity_pledge_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_restricted_shares_unlock_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_fund_industry_allocation_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_fund_industry_allocation_first_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_fund_industry_allocation_further_scale"),
    os.path.join(VALIDATION, "cninfo_d_class_shareholder_data_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_shareholder_data_first_slice"),
)

LIVE_REPORT_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "query_mode",
    "query_type",
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
QUALITY_COLUMNS = [
    "case_id",
    "component",
    "query_mode",
    "query_type",
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
DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "query_mode",
    "query_type",
    "anchor_tdate",
    "further_scale_include",
    "expected_behavior",
    "planned_request_count",
    "shared_probe_key",
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


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _infer_market(code: str) -> str:
    if code.startswith(("6", "9")):
        return "sse_main"
    if code.startswith(("0", "3")):
        return "szse_main"
    return "unknown"


def _shared_params(tdate: str) -> Dict[str, Any]:
    return {
        "type": QUERY_TYPE,
        "tdate": tdate,
    }


def _probe_key(tdate: str) -> str:
    return f"type_desc_tdate_daily_{tdate}"


def _normalize_root(path: str) -> str:
    return os.path.abspath(path)


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_root(output_root)
    expected = _normalize_root(DEFAULT_OUTPUT_ROOT)
    if root != expected:
        return False, (
            "shareholder_change_further_scale_output_root_must_be_"
            "cninfo_d_class_shareholder_change_further_scale"
        )
    for blocked in FROZEN_BLOCK_ROOTS:
        blocked_abs = _normalize_root(blocked)
        if root == blocked_abs or root.startswith(blocked_abs + os.sep):
            return False, f"frozen_root_write_blocked:{blocked_abs}"
    return True, ""


def enforce_write_block(output_paths: Dict[str, str]) -> None:
    root = _normalize_root(output_paths["root"])
    ok, err = validate_output_root(root)
    if not ok:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(2)


def load_universe(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows


def validate_universe(rows: Sequence[Dict[str, str]]) -> List[str]:
    issues: List[str] = []
    if len(rows) != EXPECTED_SIZE:
        issues.append(
            f"shareholder_change_further_scale_universe_size_must_equal_{EXPECTED_SIZE}:"
            f"got={len(rows)}"
        )
    seen_cases: Set[str] = set()
    seen_codes: Set[str] = set()
    expected_ids = {f"DSC{i}" for i in range(CASE_ID_START, CASE_ID_END + 1)}
    allowed_anchors = {PRIMARY_TDATE, ADJACENT_TDATE}
    for row in rows:
        case_id = row.get("case_id", "").strip()
        code = row.get("company_code", "").strip()
        component = row.get("component", "").strip()
        query_mode = row.get("query_mode", "").strip()
        query_type = row.get("query_type", "").strip()
        anchor = row.get("anchor_tdate", "").strip()
        include = row.get("further_scale_include", "").strip().lower()
        if case_id in seen_cases:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_cases.add(case_id)
        if case_id not in expected_ids:
            issues.append(
                f"forbidden_case_id_in_shareholder_change_further_scale:{case_id}"
            )
        if code in seen_codes:
            issues.append(f"duplicate_company_code:{code}")
        seen_codes.add(code)
        if code in FORBIDDEN_CODES:
            issues.append(f"forbidden_company_code:{code}")
        if component != COMPONENT:
            issues.append(f"component_must_be_shareholder_change:{case_id}")
        if query_mode != QUERY_MODE:
            issues.append(f"query_mode_mismatch:{case_id}")
        if query_type == FORBIDDEN_QUERY_TYPE:
            issues.append(f"forbidden_query_type_inc:{case_id}")
        if query_type != QUERY_TYPE:
            issues.append(f"query_type_must_be_desc:{case_id}")
        if anchor == FORBIDDEN_SPARSE_TDATE:
            issues.append(f"forbidden_sparse_anchor_tdate:{case_id}")
        if anchor not in allowed_anchors:
            issues.append(f"anchor_tdate_not_in_sc_fs_compose:{case_id}:{anchor}")
        if include != "yes":
            issues.append(f"further_scale_include_must_be_yes:{case_id}")
    if seen_cases != expected_ids:
        issues.append("case_id_set_must_be_DSC201_DSC250")
    return issues


def _extract_code_map(
    records: Sequence[Dict[str, Any]],
    extra_exclude: Optional[Set[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    exclude = set(FORBIDDEN_CODES) | set(EXCLUDED_PRIOR_SLICE_CODES)
    if extra_exclude:
        exclude |= set(extra_exclude)
    by_code: Dict[str, Dict[str, Any]] = {}
    for rec in records:
        code = core._company_code_from_record(rec)
        if not code:
            continue
        code = code.zfill(6)
        if code in exclude:
            continue
        if code not in by_code:
            by_code[code] = rec
    return by_code


def _cite_day(
    session: requests.Session,
    component_cfg: Dict[str, Any],
    stats: Any,
    tdate: str,
    label: str,
) -> Dict[str, Any]:
    params = _shared_params(tdate)
    payload, http_status, last_error = core._cninfo_request(
        session, component_cfg, params, stats, label
    )
    records = core._extract_records(payload) if payload is not None else []
    total = None
    if isinstance(payload, dict):
        total = payload.get("total")
        if total is None and isinstance(payload.get("data"), dict):
            total = payload["data"].get("total")
    return {
        "tdate": tdate,
        "params": params,
        "http_status": http_status,
        "last_error": last_error,
        "total": total,
        "record_count": len(records),
        "records": records,
        "by_code": _extract_code_map(records),
    }


def build_universe_lock_from_cite() -> int:
    """两次 CNINFO denser-day cite（desc）→ DSC201–250 lock。"""
    endpoints = core.load_registry_endpoints()
    source_configs = core.load_table_source_configs()
    component_cfg = copy.deepcopy(source_configs.get(COMPONENT, {}))
    endpoint = endpoints.get(COMPONENT, component_cfg.get("api_url", ENDPOINT))
    component_cfg["api_url"] = endpoint

    session = requests.Session()
    stats = core.LiveStats()
    primary = _cite_day(
        session, component_cfg, stats, PRIMARY_TDATE, "sc_fs_cite_primary"
    )
    adjacent = _cite_day(
        session, component_cfg, stats, ADJACENT_TDATE, "sc_fs_cite_adjacent"
    )

    primary_codes = sorted(primary["by_code"].keys())
    adjacent_only = sorted(
        c for c in adjacent["by_code"].keys() if c not in primary["by_code"]
    )

    def _raw_codes(records: Sequence[Dict[str, Any]]) -> Set[str]:
        out: Set[str] = set()
        for rec in records:
            code = core._company_code_from_record(rec)
            if code:
                out.add(code.zfill(6))
        return out

    present_union = _raw_codes(primary["records"]) | _raw_codes(adjacent["records"])

    selected_empty: List[Tuple[str, str]] = []
    for code, name in EMPTY_CONTROL_CANDIDATES:
        if code in present_union:
            continue
        selected_empty.append((code, name))
        if len(selected_empty) >= EMPTY_CONTROL_TARGET:
            break
    if len(selected_empty) < EMPTY_CONTROL_TARGET:
        print(
            "ERROR: insufficient verified-absent empty controls: "
            f"got={len(selected_empty)} need={EMPTY_CONTROL_TARGET}",
            file=sys.stderr,
        )
        return 2

    found_budget = EXPECTED_SIZE - len(selected_empty)
    if found_budget != FOUND_SLOTS:
        print(
            f"ERROR: found_budget_mismatch:got={found_budget} need={FOUND_SLOTS}",
            file=sys.stderr,
        )
        return 2
    if len(primary_codes) + len(adjacent_only) < found_budget:
        print(
            "ERROR: multi-day cite too thin for found slots: "
            f"primary={len(primary_codes)} adjacent_only={len(adjacent_only)} "
            f"need={found_budget}",
            file=sys.stderr,
        )
        return 2

    selected_primary = primary_codes[: min(len(primary_codes), found_budget)]
    remain = found_budget - len(selected_primary)
    selected_adjacent = adjacent_only[:remain]

    rows: List[Dict[str, str]] = []
    case_idx = CASE_ID_START

    def _append_found(
        code: str, rec: Dict[str, Any], tdate: str, cite_tag: str
    ) -> None:
        nonlocal case_idx
        name = str(rec.get("SECNAME") or rec.get("secName") or "").strip() or code
        rows.append(
            {
                "case_id": f"DSC{case_idx}",
                "probe_key": f"sc_fs_shared_desc_{tdate}_{code}",
                "company_code": code,
                "company_name": name,
                "component": COMPONENT,
                "market": _infer_market(code),
                "query_mode": QUERY_MODE,
                "query_type": QUERY_TYPE,
                "anchor_tdate": tdate,
                "further_scale_include": "yes",
                "expected_behavior": "captured_normal",
                "exclude_flags": (
                    "exclude_688671;exclude_301259;"
                    "exclude_sparse_inc_20260703_sole_found_anchor;"
                    "exclude_sc_next_slice_DSC101_105;"
                    "exclude_sc_first_slice_DSC001_005;"
                    "exclude_dlc006r;exclude_ess_h3_h4"
                ),
                "notes": (
                    f"further-scale found-path from {cite_tag} type=desc cite; "
                    "NOT verified"
                ),
                "evidence_cite": f"D-FM-09_{cite_tag}_{tdate.replace('-', '')}",
                "universe_lock_status": "locked",
                "lock_date": "2026-07-16",
                "approval_task_id": "D-FM-09",
                "per_case_request_budget": "1",
                "total_request_cap": str(EXPECTED_SIZE),
                "shared_probe_prefer": "1",
                "dense_mode_cite_strength": "multi_day_compose_primary_plus_adjacent",
                "compose_source_day": tdate,
            }
        )
        case_idx += 1

    for code in selected_primary:
        _append_found(code, primary["by_code"][code], PRIMARY_TDATE, "primary_dense")
    for code in selected_adjacent:
        _append_found(code, adjacent["by_code"][code], ADJACENT_TDATE, "adjacent")

    for code, name in selected_empty:
        rows.append(
            {
                "case_id": f"DSC{case_idx}",
                "probe_key": f"sc_fs_empty_control_{code}",
                "company_code": code,
                "company_name": name,
                "component": COMPONENT,
                "market": _infer_market(code),
                "query_mode": QUERY_MODE,
                "query_type": QUERY_TYPE,
                "anchor_tdate": PRIMARY_TDATE,
                "further_scale_include": "yes",
                "expected_behavior": "empty_but_valid",
                "exclude_flags": (
                    "exclude_688671;exclude_301259;"
                    "exclude_sparse_inc_20260703_sole_found_anchor;"
                    "empty_control_not_in_sc_fs_compose;"
                    "exclude_dlc006r;exclude_ess_h3_h4"
                ),
                "notes": (
                    "empty control retained; absent from denser multi-day "
                    f"type=desc union {PRIMARY_TDATE}+{ADJACENT_TDATE}"
                ),
                "evidence_cite": "D-FM-09_empty_control_absent_from_compose",
                "universe_lock_status": "locked",
                "lock_date": "2026-07-16",
                "approval_task_id": "D-FM-09",
                "per_case_request_budget": "1",
                "total_request_cap": str(EXPECTED_SIZE),
                "shared_probe_prefer": "1",
                "dense_mode_cite_strength": "multi_day_compose_primary_plus_adjacent",
                "compose_source_day": "union",
            }
        )
        case_idx += 1

    rows_by_id = {r["case_id"]: r for r in rows}
    ordered = [rows_by_id[f"DSC{i}"] for i in range(CASE_ID_START, CASE_ID_END + 1)]
    issues = validate_universe(ordered)
    if issues:
        print(f"ERROR: universe validation failed: {issues}", file=sys.stderr)
        return 2

    os.makedirs(VALIDATION, exist_ok=True)
    cite_payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "task_id": "D-FM-09",
        "endpoint": endpoint,
        "query_type": QUERY_TYPE,
        "forbidden_query_type": FORBIDDEN_QUERY_TYPE,
        "forbidden_sparse_tdate": FORBIDDEN_SPARSE_TDATE,
        "primary_tdate": PRIMARY_TDATE,
        "adjacent_tdate": ADJACENT_TDATE,
        "cninfo_requests": stats.cninfo_requests,
        "primary": {
            "params": primary["params"],
            "http_status": primary["http_status"],
            "last_error": primary["last_error"],
            "total": primary["total"],
            "record_count": primary["record_count"],
            "unique_codes_after_exclusions": len(primary_codes),
            "sample_records": primary["records"][:3],
        },
        "adjacent": {
            "params": adjacent["params"],
            "http_status": adjacent["http_status"],
            "last_error": adjacent["last_error"],
            "total": adjacent["total"],
            "record_count": adjacent["record_count"],
            "unique_codes_after_exclusions": len(adjacent["by_code"]),
            "adjacent_only_count": len(adjacent_only),
            "sample_records": adjacent["records"][:3],
        },
        "selected_primary_codes": selected_primary,
        "selected_adjacent_codes": selected_adjacent,
        "empty_control_codes": [c for c, _ in selected_empty],
        "excluded_prior_slice_codes": sorted(EXCLUDED_PRIOR_SLICE_CODES),
    }
    with open(SHAREHOLDER_DETAIL_CITE_JSON, "w", encoding="utf-8") as f:
        json.dump(cite_payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    fieldnames = list(ordered[0].keys())
    with open(DEFAULT_UNIVERSE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered)

    ok_http = (
        primary["http_status"] == 200
        and adjacent["http_status"] == 200
        and not primary["last_error"]
        and not adjacent["last_error"]
    )
    print(
        f"mode=shareholder_change_further_scale_universe_lock "
        f"cases={len(ordered)} cninfo_calls={stats.cninfo_requests} "
        f"primary_total={primary['total']} adjacent_total={adjacent['total']} "
        f"selected_found={found_budget} empty_controls={len(selected_empty)}"
    )
    print(f"universe_csv={DEFAULT_UNIVERSE_CSV}")
    print(f"shareholder_detail_cite={SHAREHOLDER_DETAIL_CITE_JSON}")
    print(f"universe_sha256={_sha256_file(DEFAULT_UNIVERSE_CSV)}")
    return 0 if ok_http else 2


def build_dryrun_rows(
    rows: Sequence[Dict[str, str]], output_root: str
) -> List[Dict[str, str]]:
    dry: List[Dict[str, str]] = []
    for row in rows:
        dry.append(
            {
                "case_id": row["case_id"],
                "company_code": row["company_code"],
                "company_name": row["company_name"],
                "component": row["component"],
                "market": row["market"],
                "query_mode": row["query_mode"],
                "query_type": row["query_type"],
                "anchor_tdate": row["anchor_tdate"],
                "further_scale_include": row["further_scale_include"],
                "expected_behavior": row["expected_behavior"],
                "planned_request_count": "1",
                "shared_probe_key": SHARED_PROBE_KEY,
                "planned_output_root": output_root,
                "planned_endpoint": ENDPOINT,
                "cninfo_call_planned": "shared",
                "pdf_download": "no",
                "ocr": "no",
                "extraction": "no",
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
                "dryrun_status": "planned_ok",
                "notes": (
                    f"shared_probes=2; query_mode={QUERY_MODE}; "
                    f"query_type={QUERY_TYPE}; "
                    f"compose={PRIMARY_TDATE}+{ADJACENT_TDATE}; "
                    f"company_filter_offline=SECCODE; "
                    f"forbidden_sparse={FORBIDDEN_QUERY_TYPE}+{FORBIDDEN_SPARSE_TDATE}; "
                    f"exclude_sc_next_slice_DSC101_105=yes"
                ),
            }
        )
    return dry


def write_planned_snapshots(
    rows: Sequence[Dict[str, str]], output_paths: Dict[str, str]
) -> None:
    snap_dir = os.path.join(output_paths["root"], "planned_snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    for row in rows:
        tdate = row["anchor_tdate"]
        payload = {
            "case_id": row["case_id"],
            "company_code": row["company_code"],
            "company_name": row["company_name"],
            "component": row["component"],
            "query_mode": row["query_mode"],
            "query_type": row["query_type"],
            "anchor_tdate": tdate,
            "shared_probe_key": SHARED_PROBE_KEY,
            "planned_requests": [
                _probe_key(PRIMARY_TDATE),
                _probe_key(ADJACENT_TDATE),
            ],
            "query_params": _shared_params(tdate),
            "endpoint": ENDPOINT,
            "records_path": "data.records",
            "shared_request": True,
            "company_filter_offline": True,
            "company_filter_field": "SECCODE",
            "filter_company_code": row["company_code"],
            "forbidden_sole_found": f"{FORBIDDEN_QUERY_TYPE}+{FORBIDDEN_SPARSE_TDATE}",
            "expected_behavior": row["expected_behavior"],
            "compose_source_day": row.get("compose_source_day", tdate),
            "cninfo_called": False,
        }
        out = os.path.join(snap_dir, f"{row['case_id']}_shareholder_change.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")


def write_dryrun_report(
    dry_rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_further_scale_dryrun_report.csv",
    )
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=DRYRUN_COLUMNS)
        writer.writeheader()
        writer.writerows(dry_rows)
    return path


def write_dryrun_summary(
    dry_rows: List[Dict[str, str]],
    output_paths: Dict[str, str],
    universe_csv: str,
) -> str:
    lines = [
        "# CNINFO D 类 shareholder_change Further-Scale Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** shareholder_change further-scale dry-run · **CNINFO calls = 0** · **NOT verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        "| planned_shared_cninfo_requests | **2** |",
        f"| planned_request_budget_total | **{len(dry_rows)}** |",
        "| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        f"- endpoint: `{ENDPOINT}`（拼写 shareholeder 保留）",
        f"- query mode: **{QUERY_MODE}**",
        f"- shared probe: **type={QUERY_TYPE}** · "
        f"**{PRIMARY_TDATE} + {ADJACENT_TDATE}**",
        f"- forbidden sole found: **{FORBIDDEN_QUERY_TYPE}+{FORBIDDEN_SPARSE_TDATE}**",
        "- company filter: **offline SECCODE**",
        "- isolated root: **cninfo_d_class_shareholder_change_further_scale**",
        "- frozen: SC next-slice DSC101–105 / first-slice / ESH / AT / EP / RSU / FIA",
        "",
        "## Gates",
        "",
        "```text",
        "d_class_shareholder_change_further_scale_runner_extension_gate = READY_FOR_APPROVAL",
        "d_class_shareholder_change_further_scale_live_path_gate = READY_FOR_APPROVAL",
        "d_class_shareholder_change_further_scale_live_gate = NOT_APPROVED",
        "approval_status = R19_STANDING_SCOPE_BOUNDED",
        "```",
        "",
        f"**Future acceptance / excellence: ≥{PASS_THRESHOLD}/{EXPECTED_SIZE} "
        f"acceptable (≥{int(EXCELLENCE_ACCEPTABLE_RATE * 100)}%) · fail/http=0 → "
        f"PASS_WITH_CAVEAT / excellence candidate**",
        "",
    ]
    path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_further_scale_dryrun_summary.md",
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def is_acceptable(row: Dict[str, str], summary: Dict[str, str]) -> bool:
    rs = summary.get("retrieval_status", "")
    qs = summary.get("quality_status", "")
    eb = row.get("expected_behavior", "")
    try:
        rc = int(summary.get("record_count", "0"))
    except ValueError:
        rc = 0
    if eb == "empty_but_valid":
        return rs == "empty_but_valid" and rc == 0
    if eb == "captured_normal":
        return rs == "found" and rc >= 1 and qs in ("pass", "needs_review", "")
    if "captured_normal_or_empty_but_valid" in eb:
        return (rs == "found" and rc >= 1) or (rs == "empty_but_valid" and rc == 0)
    return False


def assess_case(
    row: Dict[str, str],
    company_records: List[Dict[str, Any]],
    http_status: int,
    last_error: str,
    endpoint: str,
    used_params: Dict[str, Any],
    shared_cninfo_requests: int,
) -> Dict[str, Any]:
    record_count = len(company_records)
    tdate = row["anchor_tdate"]
    notes = [
        f"shared_probe={SHARED_PROBE_KEY}",
        "company_filter=SECCODE",
        f"query_mode={row['query_mode']}",
        f"query_type={row['query_type']}",
        f"anchor={tdate}",
        f"compose={PRIMARY_TDATE}+{ADJACENT_TDATE}",
    ]
    if last_error in ("rate_limited",) or last_error.startswith("network_error"):
        retrieval_status = (
            "http_error" if last_error.startswith("network_error") else "blocked"
        )
        quality_status = "blocked"
        lineage_status = "needs_review"
        empty_but_valid = "no"
        notes.append(last_error)
    elif last_error.startswith("http_") or last_error == "invalid_json":
        retrieval_status = "http_error"
        quality_status = "blocked"
        lineage_status = "needs_review"
        empty_but_valid = "no"
        notes.append(last_error)
    elif record_count == 0:
        retrieval_status = "empty_but_valid"
        quality_status = "pass"
        lineage_status = "discovered"
        empty_but_valid = "yes"
        notes.append(
            "shareholeder/detail zero rows after SECCODE filter; "
            "legal empty per quality policy"
        )
    else:
        retrieval_status = "found"
        quality_status = "pass"
        lineage_status = "discovered"
        empty_but_valid = "no"
        notes.append(f"found {record_count} row(s) for SECCODE filter")

    return {
        "case_id": row["case_id"],
        "company_code": row["company_code"],
        "company_name": row["company_name"],
        "component": row["component"],
        "market": row["market"],
        "query_mode": row["query_mode"],
        "query_type": row["query_type"],
        "anchor_tdate": tdate,
        "expected_behavior": row["expected_behavior"],
        "retrieval_status": retrieval_status,
        "quality_status": quality_status,
        "lineage_status": lineage_status,
        "record_count": str(record_count),
        "empty_but_valid": empty_but_valid,
        "needs_review": "no",
        "endpoint_used": endpoint,
        "cninfo_request_count": str(shared_cninfo_requests),
        "notes": "; ".join(notes),
        "_http_status": str(http_status),
        "_used_params": used_params,
        "_sample_records": company_records[:3],
    }


def write_live_snapshot(
    row: Dict[str, str], summary: Dict[str, Any], output_paths: Dict[str, str]
) -> None:
    path = os.path.join(
        output_paths["live_snapshots"],
        f"{row['case_id']}_{COMPONENT}.json",
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "case_id": row["case_id"],
                "company_code": row["company_code"],
                "company_name": row["company_name"],
                "component": COMPONENT,
                "query_mode": row["query_mode"],
                "query_type": row["query_type"],
                "anchor_tdate": row["anchor_tdate"],
                "retrieval_status": summary.get("retrieval_status", ""),
                "quality_status": summary.get("quality_status", ""),
                "lineage_status": summary.get("lineage_status", ""),
                "record_count": summary.get("record_count", "0"),
                "endpoint_used": summary.get("endpoint_used", ""),
                "query_params": summary.get("_used_params") or {},
                "sample_records": summary.get("_sample_records") or [],
                "shared_probe": SHARED_PROBE_KEY,
                "cninfo_called": True,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
        f.write("\n")


def compute_gate(
    universe_rows: Sequence[Dict[str, str]], summaries: Dict[str, Dict[str, str]]
) -> str:
    acceptable = 0
    for row in universe_rows:
        if is_acceptable(row, summaries.get(row["case_id"], {})):
            acceptable += 1
    if acceptable >= PASS_THRESHOLD:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"


def excellence_metrics(live_rows: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    n = len(live_rows)
    acceptable = sum(1 for r in live_rows if r.get("acceptable") == "yes")
    failed = sum(1 for r in live_rows if r.get("acceptable") != "yes")
    http_error = sum(
        1
        for r in live_rows
        if r.get("retrieval_status") in ("http_error", "blocked")
        or r.get("failure_type") == "transport_or_http_error"
    )
    rate = (acceptable / n) if n else 0.0
    # excellence：rate>=95% 且 fail/http=0（failed 计数含 expectation_mismatch）
    excellent = rate >= EXCELLENCE_ACCEPTABLE_RATE and failed == 0 and http_error == 0
    return {
        "acceptable": acceptable,
        "failed_or_http_error": failed,
        "http_error": http_error,
        "acceptable_rate": rate,
        "excellent": excellent,
    }


def execute_live(
    universe_rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> int:
    endpoints = core.load_registry_endpoints()
    source_configs = core.load_table_source_configs()
    component_cfg = copy.deepcopy(source_configs.get(COMPONENT, {}))
    endpoint = endpoints.get(COMPONENT, component_cfg.get("api_url", ENDPOINT))
    component_cfg["api_url"] = endpoint

    session = requests.Session()
    stats = core.LiveStats()

    # 按日共享探针：compose 两日各 1 次
    day_payloads: Dict[str, Tuple[List[Dict[str, Any]], int, str, Dict[str, Any]]] = {}
    for tdate in (PRIMARY_TDATE, ADJACENT_TDATE):
        params = _shared_params(tdate)
        payload, http_status, last_error = core._cninfo_request(
            session, component_cfg, params, stats, _probe_key(tdate)
        )
        records = core._extract_records(payload) if payload is not None else []
        day_payloads[tdate] = (records, http_status, last_error, params)

    # 空控对并集过滤；found 对 compose_source_day 过滤
    union_records: List[Dict[str, Any]] = []
    union_http = 200
    union_err = ""
    for tdate in (PRIMARY_TDATE, ADJACENT_TDATE):
        recs, http_status, last_error, _ = day_payloads[tdate]
        union_records.extend(recs)
        if http_status != 200 or last_error:
            union_http = http_status
            union_err = last_error or f"http_{http_status}"

    live_rows: List[Dict[str, str]] = []
    summaries: Dict[str, Dict[str, str]] = {}
    for row in sorted(universe_rows, key=lambda r: r["case_id"]):
        compose = row.get("compose_source_day", row["anchor_tdate"]).strip()
        if row.get("expected_behavior") == "empty_but_valid" or compose == "union":
            all_records = union_records
            http_status = union_http
            last_error = union_err
            params = {
                "type": QUERY_TYPE,
                "tdates": [PRIMARY_TDATE, ADJACENT_TDATE],
            }
        else:
            tdate = row["anchor_tdate"]
            all_records, http_status, last_error, params = day_payloads[tdate]
        company_records = core._filter_company_records(
            all_records, row["company_code"]
        )
        summary = assess_case(
            row,
            company_records,
            http_status,
            last_error,
            endpoint,
            params,
            stats.cninfo_requests,
        )
        write_live_snapshot(row, summary, output_paths)
        public = {k: v for k, v in summary.items() if not k.startswith("_")}
        summaries[row["case_id"]] = public
        ok = is_acceptable(row, public)
        failure_type = ""
        if not ok:
            failure_type = (
                "transport_or_http_error"
                if public["retrieval_status"] in ("http_error", "blocked")
                else "expectation_mismatch"
            )
        live_rows.append(
            {
                **public,
                "acceptable": "yes" if ok else "no",
                "failure_type": failure_type,
                "pdf_download": "no",
                "ocr": "no",
                "extraction": "no",
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
            }
        )
        print(
            f"{row['case_id']} {public['retrieval_status']}: "
            f"records={public['record_count']} acceptable={'yes' if ok else 'no'}",
            flush=True,
        )

    if stats.cninfo_requests != 2:
        print(
            f"ERROR: shared_cninfo_plan_mismatch:got={stats.cninfo_requests} need=2",
            file=sys.stderr,
        )
        return 2

    gate = compute_gate(universe_rows, summaries)
    excel = excellence_metrics(live_rows)
    live_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_further_scale_live_report.csv",
    )
    with open(live_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(live_rows)

    quality_rows = [{k: r[k] for k in QUALITY_COLUMNS} for r in live_rows]
    quality_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_further_scale_quality_report.csv",
    )
    with open(quality_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUALITY_COLUMNS)
        writer.writeheader()
        writer.writerows(quality_rows)

    acceptable = excel["acceptable"]
    found = sum(1 for r in live_rows if r["retrieval_status"] == "found")
    empty = sum(1 for r in live_rows if r["retrieval_status"] == "empty_but_valid")
    summary_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_further_scale_live_summary.md",
    )
    lines = [
        "# CNINFO D 类 shareholder_change Further-Scale Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** shareholder_change further-scale live · **R19 standing bounded** · **NOT verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(live_rows)}** |",
        f"| acceptable | **{acceptable}/{len(live_rows)}** |",
        f"| acceptable_rate | **{excel['acceptable_rate'] * 100:.2f}%** |",
        f"| found | **{found}** |",
        f"| empty_but_valid | **{empty}** |",
        f"| failed_or_http_error | **{excel['failed_or_http_error']}** |",
        f"| shared_cninfo_requests | **{stats.cninfo_requests}** |",
        f"| CNINFO calls | **{stats.cninfo_requests}** |",
        f"| excellence | **{'YES' if excel['excellent'] else 'NO'}** |",
        "",
        "## Gates",
        "",
        "```text",
        "d_class_shareholder_change_further_scale_live_path_gate = READY_FOR_APPROVAL",
        "d_class_shareholder_change_further_scale_live_gate = NOT_APPROVED",
        f"d_class_shareholder_change_further_scale_execution_gate = {gate}",
        "live_authority = R19_STANDING_SCOPE_BOUNDED",
        f"excellence_gated = {str(excel['excellent']).lower()}",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT bare PASS**",
        "",
        "## Caveats",
        "",
        f"- denser multi-day type=desc（{PRIMARY_TDATE}+{ADJACENT_TDATE}）截面密度 ≠ 全市场增减持覆盖。",
        f"- 禁 {FORBIDDEN_QUERY_TYPE}+{FORBIDDEN_SPARSE_TDATE} sole found 锚。",
        "- SC next-slice DSC101–105 / first-slice / ESH / AT 冻结根未 mutate。",
        "",
    ]
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(
        f"mode=shareholder_change_further_scale_live cases={len(live_rows)} "
        f"cninfo_calls={stats.cninfo_requests} acceptable={acceptable}/{len(live_rows)} "
        f"found={found} empty={empty} excellence={'YES' if excel['excellent'] else 'NO'}"
    )
    print(f"gate=d_class_shareholder_change_further_scale_execution_gate={gate}")
    print(f"live_report={live_path}")
    print(f"quality_report={quality_path}")
    print(f"live_summary={summary_path}")
    return 0 if gate == "PASS_WITH_CAVEAT" else 1


def run_dry_run(args: argparse.Namespace) -> int:
    ok_root, root_err = validate_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2
    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2
    rows = load_universe(args.universe_csv)
    issues = validate_universe(rows)
    if issues:
        print(f"ERROR: universe validation failed: {issues}", file=sys.stderr)
        return 2
    output_root = core._normalize_output_root(args.output_root)
    output_paths = core.ensure_output_layout(output_root, "dry-run")
    enforce_write_block(output_paths)
    dry_rows = build_dryrun_rows(rows, output_root)
    write_planned_snapshots(rows, output_paths)
    report_path = write_dryrun_report(dry_rows, output_paths)
    summary_path = write_dryrun_summary(dry_rows, output_paths, args.universe_csv)
    print(
        f"mode=shareholder_change_further_scale_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total=2 cninfo_calls=0"
    )
    print(
        "gate=d_class_shareholder_change_further_scale_runner_extension_gate="
        "READY_FOR_APPROVAL"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0


def run_live(args: argparse.Namespace) -> int:
    if not args.approve_d_class_shareholder_change_further_scale:
        print(
            "ERROR: approve_d_class_shareholder_change_further_scale_required",
            file=sys.stderr,
        )
        return 2
    ok_root, root_err = validate_output_root(args.output_root)
    if not ok_root:
        print(f"ERROR: {root_err}", file=sys.stderr)
        return 2
    if not os.path.isfile(args.universe_csv):
        print(f"ERROR: universe not found: {args.universe_csv}", file=sys.stderr)
        return 2
    rows = load_universe(args.universe_csv)
    issues = validate_universe(rows)
    if issues:
        print(f"ERROR: universe validation failed: {issues}", file=sys.stderr)
        return 2
    output_root = core._normalize_output_root(args.output_root)
    output_paths = core.ensure_output_layout(output_root, "live")
    enforce_write_block(output_paths)
    return execute_live(rows, output_paths)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="D-class shareholder_change further-scale (~50) runner"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build-universe-lock", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument(
        "--approve-d-class-shareholder-change-further-scale",
        action="store_true",
    )
    parser.add_argument("--universe-csv", default=DEFAULT_UNIVERSE_CSV)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.build_universe_lock:
        return build_universe_lock_from_cite()
    if args.dry_run:
        return run_dry_run(args)
    if args.live:
        return run_live(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
