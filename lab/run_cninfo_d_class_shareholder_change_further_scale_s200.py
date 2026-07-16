#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 shareholder_change further-scale S200（~200）孤立根 runner。

denser 策略：type=desc 多交易日并集（候选日自适应 cite 至 found=198）共享探针 + 离线 SECCODE 过滤。
禁止 type=inc+2026-07-03 作 sole found 锚；不写入 SC s50 / next-slice / first-slice / ESH / AT 冻结根。

用法：
  .venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s200.py --build-universe-lock
  .venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s200.py --dry-run \\
      --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_universe_lock_20260716.csv \\
      --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200
  .venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s200.py --live \\
      --approve-d-class-shareholder-change-further-scale-s200 \\
      --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_universe_lock_20260716.csv \\
      --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200
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
# S50 两日保留为候选；S200 需扩展更多 denser 交易日以凑满 ~198 found
COMPOSE_CANDIDATE_TDATES = (
    "2026-06-16",
    "2026-06-17",
    "2026-06-18",
    "2026-06-19",
    "2026-06-23",
    "2026-06-24",
    "2026-06-25",
    "2026-06-26",
    "2026-06-27",
    "2026-06-30",
    "2026-07-01",
    "2026-07-02",
    "2026-07-04",
    "2026-07-07",
    "2026-07-08",
    "2026-07-09",
    "2026-07-10",
    "2026-07-11",
    "2026-07-14",
    "2026-07-15",
)
FORBIDDEN_SPARSE_TDATE = "2026-07-03"
QUERY_MODE = "type_desc_multi_day_union"
ENDPOINT = "https://www.cninfo.com.cn/data20/shareholeder/detail"
EXPECTED_SIZE = 200
# excellence：acceptable >= 95% → ≥190/200；且 fail/http=0
PASS_THRESHOLD = 190
EXCELLENCE_ACCEPTABLE_RATE = 0.95
CASE_ID_START = 301
CASE_ID_END = 500
FOUND_SLOTS = 198
EMPTY_CONTROL_TARGET = 2
MAX_COMPOSE_DAYS = 12

DEFAULT_OUTPUT_ROOT = os.path.join(
    VALIDATION, "cninfo_d_class_shareholder_change_further_scale_s200"
)
DEFAULT_UNIVERSE_CSV = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_further_scale_s200_universe_lock_20260716.csv",
)
SHAREHOLDER_DETAIL_CITE_JSON = os.path.join(
    VALIDATION,
    "cninfo_d_class_shareholder_change_further_scale_s200_shareholder_detail_cite_20260716.json",
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
# D-FM-09 S50 found 槽公司码：不得再入 S200 found 槽（空控可复用）
EXCLUDED_S50_FOUND_CODES = {
    "000402",
    "000688",
    "000813",
    "000892",
    "002097",
    "002115",
    "002617",
    "002702",
    "002735",
    "002976",
    "003003",
    "300102",
    "300200",
    "300211",
    "300321",
    "300334",
    "300358",
    "300457",
    "300493",
    "300519",
    "300540",
    "300552",
    "300590",
    "300802",
    "300876",
    "300917",
    "300931",
    "300959",
    "300966",
    "300980",
    "301026",
    "301046",
    "301158",
    "301161",
    "301273",
    "301333",
    "301429",
    "301617",
    "600545",
    "600803",
    "603303",
    "603680",
    "605198",
    "688002",
    "688158",
    "688262",
    "688378",
    "688702",
}
EMPTY_CONTROL_CANDIDATES = [
    ("000895", "双汇发展"),
    ("601988", "中国银行"),
    ("600519", "贵州茅台"),
    ("000858", "五粮液"),
]

FROZEN_BLOCK_ROOTS = (
    os.path.join(VALIDATION, "cninfo_d_class_shareholder_change_further_scale"),
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


def _shared_probe_key(compose_days: Sequence[str]) -> str:
    return "type_desc_union_" + "_".join(compose_days)

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
            "shareholder_change_further_scale_s200_output_root_must_be_"
            "cninfo_d_class_shareholder_change_further_scale_s200"
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
            f"shareholder_change_further_scale_s200_universe_size_must_equal_{EXPECTED_SIZE}:"
            f"got={len(rows)}"
        )
    seen_cases: Set[str] = set()
    seen_codes: Set[str] = set()
    expected_ids = {f"DSC{i}" for i in range(CASE_ID_START, CASE_ID_END + 1)}
    allowed_anchors = set(COMPOSE_CANDIDATE_TDATES)
    found_codes: Set[str] = set()
    for row in rows:
        case_id = row.get("case_id", "").strip()
        code = row.get("company_code", "").strip()
        component = row.get("component", "").strip()
        query_mode = row.get("query_mode", "").strip()
        query_type = row.get("query_type", "").strip()
        anchor = row.get("anchor_tdate", "").strip()
        include = row.get("further_scale_include", "").strip().lower()
        expected_behavior = row.get("expected_behavior", "").strip()
        if case_id in seen_cases:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_cases.add(case_id)
        if case_id not in expected_ids:
            issues.append(
                f"forbidden_case_id_in_shareholder_change_further_scale_s200:{case_id}"
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
            issues.append(f"anchor_tdate_not_in_sc_fs_s200_compose:{case_id}:{anchor}")
        if include != "yes":
            issues.append(f"further_scale_include_must_be_yes:{case_id}")
        if expected_behavior == "captured_normal":
            found_codes.add(code)
            if code in EXCLUDED_PRIOR_SLICE_CODES:
                issues.append(f"found_slot_reuses_prior_slice_code:{code}")
            if code in EXCLUDED_S50_FOUND_CODES:
                issues.append(f"found_slot_reuses_s50_found_code:{code}")
    if seen_cases != expected_ids:
        issues.append("case_id_set_must_be_DSC301_DSC500")
    if len(found_codes) != FOUND_SLOTS:
        issues.append(
            f"found_slot_count_must_equal_{FOUND_SLOTS}:got={len(found_codes)}"
        )
    return issues


def _extract_code_map(
    records: Sequence[Dict[str, Any]],
    extra_exclude: Optional[Set[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    exclude = (
        set(FORBIDDEN_CODES)
        | set(EXCLUDED_PRIOR_SLICE_CODES)
        | set(EXCLUDED_S50_FOUND_CODES)
    )
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
    """多日 type=desc denser cite（自适应至 found=198）→ DSC301–500 lock。"""
    endpoints = core.load_registry_endpoints()
    source_configs = core.load_table_source_configs()
    component_cfg = copy.deepcopy(source_configs.get(COMPONENT, {}))
    endpoint = endpoints.get(COMPONENT, component_cfg.get("api_url", ENDPOINT))
    component_cfg["api_url"] = endpoint

    session = requests.Session()
    stats = core.LiveStats()

    day_cites: List[Dict[str, Any]] = []
    selected_found: List[Tuple[str, Dict[str, Any], str]] = []
    seen_found: Set[str] = set()
    present_union: Set[str] = set()
    compose_days: List[str] = []

    def _raw_codes(records: Sequence[Dict[str, Any]]) -> Set[str]:
        out: Set[str] = set()
        for rec in records:
            code = core._company_code_from_record(rec)
            if code:
                out.add(code.zfill(6))
        return out

    for tdate in COMPOSE_CANDIDATE_TDATES:
        if len(compose_days) >= MAX_COMPOSE_DAYS:
            break
        if len(selected_found) >= FOUND_SLOTS:
            break
        cite = _cite_day(
            session, component_cfg, stats, tdate, f"sc_fs_s200_cite_{tdate}"
        )
        day_cites.append(cite)
        if cite["http_status"] != 200 or cite["last_error"]:
            print(
                f"ERROR: cite_day_failed:{tdate} http={cite['http_status']} "
                f"err={cite['last_error']}",
                file=sys.stderr,
            )
            return 2
        if cite["record_count"] == 0:
            continue
        present_union |= _raw_codes(cite["records"])
        new_codes = sorted(c for c in cite["by_code"].keys() if c not in seen_found)
        if not new_codes:
            continue
        compose_days.append(tdate)
        for code in new_codes:
            if len(selected_found) >= FOUND_SLOTS:
                break
            selected_found.append((code, cite["by_code"][code], tdate))
            seen_found.add(code)

    if len(selected_found) < FOUND_SLOTS:
        print(
            "ERROR: multi-day cite too thin for found slots: "
            f"got={len(selected_found)} need={FOUND_SLOTS} "
            f"compose_days={compose_days}",
            file=sys.stderr,
        )
        return 2

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

    selected_found = selected_found[:FOUND_SLOTS]
    # 仅保留选中 found 实际用到的 compose 日（保持 cite 顺序）
    used_set = {tdate for _, _, tdate in selected_found}
    used_days = [d for d in compose_days if d in used_set]
    shared_key = _shared_probe_key(used_days)

    rows: List[Dict[str, str]] = []
    case_idx = CASE_ID_START

    for code, rec, tdate in selected_found:
        name = str(rec.get("SECNAME") or rec.get("secName") or "").strip() or code
        rows.append(
            {
                "case_id": f"DSC{case_idx}",
                "probe_key": f"sc_fs_s200_shared_desc_{tdate}_{code}",
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
                    "exclude_sc_fs_s50_DSC201_250_found;"
                    "exclude_dlc006r;exclude_ess_h3_h4"
                ),
                "notes": (
                    f"further-scale s200 found-path from type=desc cite day {tdate}; "
                    "NOT verified"
                ),
                "evidence_cite": f"D-FM-10_compose_{tdate.replace('-', '')}",
                "universe_lock_status": "locked",
                "lock_date": "2026-07-16",
                "approval_task_id": "D-FM-10",
                "per_case_request_budget": "1",
                "total_request_cap": str(EXPECTED_SIZE),
                "shared_probe_prefer": "1",
                "dense_mode_cite_strength": "multi_day_compose_adaptive_union",
                "compose_source_day": tdate,
                "shared_probe_key": shared_key,
            }
        )
        case_idx += 1

    empty_anchor = used_days[0]
    for code, name in selected_empty:
        rows.append(
            {
                "case_id": f"DSC{case_idx}",
                "probe_key": f"sc_fs_s200_empty_control_{code}",
                "company_code": code,
                "company_name": name,
                "component": COMPONENT,
                "market": _infer_market(code),
                "query_mode": QUERY_MODE,
                "query_type": QUERY_TYPE,
                "anchor_tdate": empty_anchor,
                "further_scale_include": "yes",
                "expected_behavior": "empty_but_valid",
                "exclude_flags": (
                    "exclude_688671;exclude_301259;"
                    "exclude_sparse_inc_20260703_sole_found_anchor;"
                    "empty_control_not_in_sc_fs_s200_compose;"
                    "exclude_dlc006r;exclude_ess_h3_h4"
                ),
                "notes": (
                    "empty control retained; absent from denser multi-day "
                    f"type=desc union {'+'.join(used_days)}"
                ),
                "evidence_cite": "D-FM-10_empty_control_absent_from_compose",
                "universe_lock_status": "locked",
                "lock_date": "2026-07-16",
                "approval_task_id": "D-FM-10",
                "per_case_request_budget": "1",
                "total_request_cap": str(EXPECTED_SIZE),
                "shared_probe_prefer": "1",
                "dense_mode_cite_strength": "multi_day_compose_adaptive_union",
                "compose_source_day": "union",
                "shared_probe_key": shared_key,
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
    cite_days_payload = []
    for cite in day_cites:
        if cite["tdate"] not in used_days and cite["record_count"] == 0:
            continue
        cite_days_payload.append(
            {
                "tdate": cite["tdate"],
                "params": cite["params"],
                "http_status": cite["http_status"],
                "last_error": cite["last_error"],
                "total": cite["total"],
                "record_count": cite["record_count"],
                "unique_codes_after_exclusions": len(cite["by_code"]),
                "selected": cite["tdate"] in used_days,
                "sample_records": cite["records"][:2],
            }
        )
    cite_payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "task_id": "D-FM-10",
        "endpoint": endpoint,
        "query_type": QUERY_TYPE,
        "forbidden_query_type": FORBIDDEN_QUERY_TYPE,
        "forbidden_sparse_tdate": FORBIDDEN_SPARSE_TDATE,
        "compose_candidate_tdates": list(COMPOSE_CANDIDATE_TDATES),
        "compose_used_tdates": used_days,
        "shared_probe_key": shared_key,
        "cninfo_requests": stats.cninfo_requests,
        "days": cite_days_payload,
        "selected_found_count": len(selected_found),
        "empty_control_codes": [c for c, _ in selected_empty],
        "excluded_prior_slice_codes": sorted(EXCLUDED_PRIOR_SLICE_CODES),
        "excluded_s50_found_codes": sorted(EXCLUDED_S50_FOUND_CODES),
    }
    with open(SHAREHOLDER_DETAIL_CITE_JSON, "w", encoding="utf-8") as f:
        json.dump(cite_payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    fieldnames = list(ordered[0].keys())
    with open(DEFAULT_UNIVERSE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered)

    print(
        f"mode=shareholder_change_further_scale_s200_universe_lock "
        f"cases={len(ordered)} cninfo_calls={stats.cninfo_requests} "
        f"compose_days={len(used_days)} selected_found={FOUND_SLOTS} "
        f"empty_controls={len(selected_empty)}"
    )
    print(f"compose_used_tdates={','.join(used_days)}")
    print(f"universe_csv={DEFAULT_UNIVERSE_CSV}")
    print(f"shareholder_detail_cite={SHAREHOLDER_DETAIL_CITE_JSON}")
    print(f"universe_sha256={_sha256_file(DEFAULT_UNIVERSE_CSV)}")
    return 0


def _compose_days_from_rows(rows: Sequence[Dict[str, str]]) -> List[str]:
    days = sorted(
        {
            r["anchor_tdate"].strip()
            for r in rows
            if r.get("expected_behavior") == "captured_normal"
            and r.get("anchor_tdate", "").strip()
        }
    )
    return days


def build_dryrun_rows(
    rows: Sequence[Dict[str, str]], output_root: str
) -> List[Dict[str, str]]:
    compose_days = _compose_days_from_rows(rows)
    shared_key = _shared_probe_key(compose_days)
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
                "shared_probe_key": shared_key,
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
                    f"shared_probes={len(compose_days)}; query_mode={QUERY_MODE}; "
                    f"query_type={QUERY_TYPE}; "
                    f"compose={'+'.join(compose_days)}; "
                    f"company_filter_offline=SECCODE; "
                    f"forbidden_sparse={FORBIDDEN_QUERY_TYPE}+{FORBIDDEN_SPARSE_TDATE}; "
                    f"exclude_sc_fs_s50_found=yes"
                ),
            }
        )
    return dry


def write_planned_snapshots(
    rows: Sequence[Dict[str, str]], output_paths: Dict[str, str]
) -> None:
    snap_dir = os.path.join(output_paths["root"], "planned_snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    compose_days = _compose_days_from_rows(rows)
    shared_key = _shared_probe_key(compose_days)
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
            "shared_probe_key": shared_key,
            "planned_requests": [_probe_key(d) for d in compose_days],
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
        "d_class_shareholder_change_further_scale_s200_dryrun_report.csv",
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
    compose_days = _compose_days_from_rows(dry_rows)
    lines = [
        "# CNINFO D 类 shareholder_change Further-Scale S200 Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** shareholder_change further-scale s200 dry-run · **CNINFO calls = 0** · **NOT verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_shared_cninfo_requests | **{len(compose_days)}** |",
        f"| planned_request_budget_total | **{len(dry_rows)}** |",
        "| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        f"- endpoint: `{ENDPOINT}`（拼写 shareholeder 保留）",
        f"- query mode: **{QUERY_MODE}**",
        f"- shared probe: **type={QUERY_TYPE}** · "
        f"**{' + '.join(compose_days)}**",
        f"- forbidden sole found: **{FORBIDDEN_QUERY_TYPE}+{FORBIDDEN_SPARSE_TDATE}**",
        "- company filter: **offline SECCODE**",
        "- isolated root: **cninfo_d_class_shareholder_change_further_scale_s200**",
        "- frozen: SC s50 / next-slice / first-slice / ESH / AT / EP / RSU / FIA",
        "",
        "## Gates",
        "",
        "```text",
        "d_class_shareholder_change_further_scale_s200_runner_extension_gate = READY_FOR_APPROVAL",
        "d_class_shareholder_change_further_scale_s200_live_path_gate = READY_FOR_APPROVAL",
        "d_class_shareholder_change_further_scale_s200_live_gate = NOT_APPROVED",
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
        "d_class_shareholder_change_further_scale_s200_dryrun_summary.md",
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
        f"shared_probe={_shared_probe_key(_compose_days_from_rows([row]))}",
        "company_filter=SECCODE",
        f"query_mode={row['query_mode']}",
        f"query_type={row['query_type']}",
        f"anchor={tdate}",
        f"compose_source_day={row.get('compose_source_day', tdate)}",
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
                "shared_probe": row.get("shared_probe_key")
                or _probe_key(row["anchor_tdate"]),
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

    compose_days = _compose_days_from_rows(universe_rows)
    shared_key = _shared_probe_key(compose_days)

    # 按日共享探针：每个 compose 日 1 次
    day_payloads: Dict[str, Tuple[List[Dict[str, Any]], int, str, Dict[str, Any]]] = {}
    for tdate in compose_days:
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
    for tdate in compose_days:
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
                "tdates": compose_days,
            }
        else:
            tdate = row["anchor_tdate"]
            all_records, http_status, last_error, params = day_payloads[tdate]
        company_records = core._filter_company_records(
            all_records, row["company_code"]
        )
        # 注入 shared_probe_key 供 snapshot
        row = {**row, "shared_probe_key": shared_key}
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

    if stats.cninfo_requests != len(compose_days):
        print(
            f"ERROR: shared_cninfo_plan_mismatch:got={stats.cninfo_requests} "
            f"need={len(compose_days)}",
            file=sys.stderr,
        )
        return 2

    gate = compute_gate(universe_rows, summaries)
    excel = excellence_metrics(live_rows)
    live_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_further_scale_s200_live_report.csv",
    )
    with open(live_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(live_rows)

    quality_rows = [{k: r[k] for k in QUALITY_COLUMNS} for r in live_rows]
    quality_path = os.path.join(
        output_paths["reports"],
        "d_class_shareholder_change_further_scale_s200_quality_report.csv",
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
        "d_class_shareholder_change_further_scale_s200_live_summary.md",
    )
    lines = [
        "# CNINFO D 类 shareholder_change Further-Scale S200 Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** shareholder_change further-scale s200 live · **R19 standing bounded** · **NOT verified**",
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
        "d_class_shareholder_change_further_scale_s200_live_path_gate = READY_FOR_APPROVAL",
        "d_class_shareholder_change_further_scale_s200_live_gate = NOT_APPROVED",
        f"d_class_shareholder_change_further_scale_s200_execution_gate = {gate}",
        "live_authority = R19_STANDING_SCOPE_BOUNDED",
        f"excellence_gated = {str(excel['excellent']).lower()}",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT bare PASS**",
        "",
        "## Caveats",
        "",
        f"- denser multi-day type=desc（{'+'.join(compose_days)}）截面密度 ≠ 全市场增减持覆盖。",
        f"- 禁 {FORBIDDEN_QUERY_TYPE}+{FORBIDDEN_SPARSE_TDATE} sole found 锚。",
        "- SC s50 / next-slice / first-slice / ESH / AT 冻结根未 mutate。",
        "",
    ]
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(
        f"mode=shareholder_change_further_scale_s200_live cases={len(live_rows)} "
        f"cninfo_calls={stats.cninfo_requests} acceptable={acceptable}/{len(live_rows)} "
        f"found={found} empty={empty} excellence={'YES' if excel['excellent'] else 'NO'}"
    )
    print(
        f"gate=d_class_shareholder_change_further_scale_s200_execution_gate={gate}"
    )
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
        f"mode=shareholder_change_further_scale_s200_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total={len(_compose_days_from_rows(rows))} cninfo_calls=0"
    )
    print(
        "gate=d_class_shareholder_change_further_scale_s200_runner_extension_gate="
        "READY_FOR_APPROVAL"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0


def run_live(args: argparse.Namespace) -> int:
    if not args.approve_d_class_shareholder_change_further_scale_s200:
        print(
            "ERROR: approve_d_class_shareholder_change_further_scale_s200_required",
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
        description="D-class shareholder_change further-scale S200 (~200) runner"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build-universe-lock", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument(
        "--approve-d-class-shareholder-change-further-scale-s200",
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
