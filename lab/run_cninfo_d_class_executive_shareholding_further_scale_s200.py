#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 executive_shareholding further-scale S200（~200）孤立根 runner。

共享 denser-mode 探针 timeMark=threeMonth + varyType=b；离线 SECCODE 过滤。
不写入 ESH next-slice（DES101–105）/ first-slice / AT / SC / EP / RSU / FIA 冻结根。

用法：
  .venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale_s200.py --build-universe-lock
  .venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale_s200.py --dry-run \\
      --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_universe_lock_20260716.csv \\
      --output-root outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200
  .venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale_s200.py --live \\
      --approve-d-class-executive-shareholding-further-scale-s200 \\
      --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_universe_lock_20260716.csv \\
      --output-root outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200
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

COMPONENT = "executive_shareholding"
TIME_MARK = "threeMonth"
VARY_TYPE = "b"
QUERY_MODE = "timeMark_threeMonth_varyType_b"
FORBIDDEN_TIME_MARK = "oneMonth"
ENDPOINT = "https://www.cninfo.com.cn/data20/leader/detail"
SHARED_PROBE_KEY = "timeMark_threeMonth_varyType_b"
EXPECTED_SIZE = 200
CASE_ID_START = 251
CASE_ID_END = 450
FOUND_SLOT_COUNT = 198  # 200 - 2 empty controls
# excellence：acceptable >= 95% → ≥190/200；且 fail/http=0
PASS_THRESHOLD = 190
EXCELLENCE_ACCEPTABLE_RATE = 0.95

DEFAULT_OUTPUT_ROOT = os.path.join(
    VALIDATION, "cninfo_d_class_executive_shareholding_further_scale_s200"
)
DEFAULT_UNIVERSE_CSV = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_further_scale_s200_universe_lock_20260716.csv",
)
LEADER_DETAIL_CITE_JSON = os.path.join(
    VALIDATION,
    "cninfo_d_class_executive_shareholding_further_scale_s200_leader_detail_cite_20260716.json",
)

FORBIDDEN_CODES = {"688671", "301259"}
# next-slice / first-slice 已锁公司码：不得再入 found 槽
EXCLUDED_PRIOR_SLICE_CODES = {
    "002415",
    "000895",
    "600000",
    "000550",
    "601988",
}
# D-FM-06 S50 found 槽公司码：不得再入 S200 found 槽（空控可复用）
EXCLUDED_S50_FOUND_CODES = {
    "000078",
    "000338",
    "000403",
    "000404",
    "000409",
    "000516",
    "000656",
    "000677",
    "000766",
    "000800",
    "000801",
    "000829",
    "000902",
    "000915",
    "000925",
    "000975",
    "001299",
    "002024",
    "002083",
    "002096",
    "002146",
    "002152",
    "002179",
    "002196",
    "002217",
    "002252",
    "002258",
    "002262",
    "002301",
    "002311",
    "002318",
    "002333",
    "002345",
    "002353",
    "002372",
    "002385",
    "002416",
    "002430",
    "002442",
    "002444",
    "002454",
    "002475",
    "002480",
    "002517",
    "002557",
    "002560",
    "002568",
    "002597",
}
# next-slice live 已证在 denser threeMonth+b 截面内为空
EMPTY_CONTROL_CODES = [
    ("000895", "双汇发展"),
    ("601988", "中国银行"),
]

FROZEN_BLOCK_ROOTS = (
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_further_scale"),
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_first_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_first_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_further_scale"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_further_scale_s200"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_further_scale_s1000"),
    os.path.join(VALIDATION, "cninfo_d_class_shareholder_change_next_slice"),
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
QUALITY_COLUMNS = [
    "case_id",
    "component",
    "query_mode",
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
DRYRUN_COLUMNS = [
    "case_id",
    "company_code",
    "company_name",
    "component",
    "market",
    "query_mode",
    "time_mark",
    "vary_type",
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


def _shared_params() -> Dict[str, Any]:
    return {
        "timeMark": TIME_MARK,
        "varyType": VARY_TYPE,
    }


def _normalize_root(path: str) -> str:
    return os.path.abspath(path)


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_root(output_root)
    expected = _normalize_root(DEFAULT_OUTPUT_ROOT)
    if root != expected:
        return False, (
            "executive_shareholding_further_scale_s200_output_root_must_be_"
            "cninfo_d_class_executive_shareholding_further_scale_s200"
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
            f"executive_shareholding_further_scale_s200_universe_size_must_equal_{EXPECTED_SIZE}:"
            f"got={len(rows)}"
        )
    seen_cases: Set[str] = set()
    seen_codes: Set[str] = set()
    expected_ids = {f"DES{i}" for i in range(CASE_ID_START, CASE_ID_END + 1)}
    for row in rows:
        case_id = row.get("case_id", "").strip()
        code = row.get("company_code", "").strip()
        component = row.get("component", "").strip()
        query_mode = row.get("query_mode", "").strip()
        time_mark = row.get("time_mark", "").strip()
        vary_type = row.get("vary_type", "").strip()
        include = row.get("further_scale_include", "").strip().lower()
        eb = row.get("expected_behavior", "").strip()
        if case_id in seen_cases:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_cases.add(case_id)
        if case_id not in expected_ids:
            issues.append(
                f"forbidden_case_id_in_executive_shareholding_further_scale_s200:{case_id}"
            )
        if code in seen_codes:
            issues.append(f"duplicate_company_code:{code}")
        seen_codes.add(code)
        if code in FORBIDDEN_CODES:
            issues.append(f"forbidden_company_code:{code}")
        if eb == "captured_normal" and code in EXCLUDED_S50_FOUND_CODES:
            issues.append(f"s50_found_code_reuse_forbidden:{code}")
        if eb == "captured_normal" and code in EXCLUDED_PRIOR_SLICE_CODES:
            issues.append(f"prior_slice_code_reuse_forbidden:{code}")
        if component != COMPONENT:
            issues.append(f"component_must_be_executive_shareholding:{case_id}")
        if query_mode != QUERY_MODE:
            issues.append(f"query_mode_mismatch:{case_id}")
        if time_mark == FORBIDDEN_TIME_MARK:
            issues.append(f"forbidden_time_mark_oneMonth:{case_id}")
        if time_mark != TIME_MARK:
            issues.append(f"time_mark_mismatch:{case_id}")
        if vary_type != VARY_TYPE:
            issues.append(f"vary_type_mismatch:{case_id}")
        if include != "yes":
            issues.append(f"further_scale_include_must_be_yes:{case_id}")
    if seen_cases != expected_ids:
        issues.append("case_id_set_must_be_DES251_DES450")
    return issues


def build_universe_lock_from_cite() -> int:
    """一次 CNINFO denser-mode cite → leader/detail 快照 + DES201–250 lock。"""
    endpoints = core.load_registry_endpoints()
    source_configs = core.load_table_source_configs()
    component_cfg = copy.deepcopy(source_configs.get(COMPONENT, {}))
    endpoint = endpoints.get(COMPONENT, component_cfg.get("api_url", ENDPOINT))
    component_cfg["api_url"] = endpoint

    session = requests.Session()
    stats = core.LiveStats()
    params = _shared_params()
    payload, http_status, last_error = core._cninfo_request(
        session, component_cfg, params, stats, "esh_fs_s200_leader_detail_cite"
    )
    records = core._extract_records(payload) if payload is not None else []
    total = None
    if isinstance(payload, dict):
        total = payload.get("total")
        if total is None and isinstance(payload.get("data"), dict):
            total = payload["data"].get("total")

    by_code: Dict[str, Dict[str, Any]] = {}
    for rec in records:
        code = core._company_code_from_record(rec)
        if not code:
            continue
        code = code.zfill(6)
        if (
            code in FORBIDDEN_CODES
            or code in EXCLUDED_PRIOR_SLICE_CODES
            or code in EXCLUDED_S50_FOUND_CODES
        ):
            continue
        if code not in by_code:
            by_code[code] = rec

    found_codes = sorted(by_code.keys())
    if len(found_codes) < FOUND_SLOT_COUNT:
        print(
            f"ERROR: denser-mode cite too thin for {FOUND_SLOT_COUNT} found slots: "
            f"got={len(found_codes)}",
            file=sys.stderr,
        )
        return 2

    selected_found = found_codes[:FOUND_SLOT_COUNT]
    rows: List[Dict[str, str]] = []
    for offset, code in enumerate(selected_found):
        idx = CASE_ID_START + offset
        rec = by_code[code]
        name = (
            str(rec.get("SECNAME") or rec.get("secName") or rec.get("SECNAME") or "")
            .strip()
            or code
        )
        rows.append(
            {
                "case_id": f"DES{idx}",
                "probe_key": f"esh_fs_s200_shared_threeMonth_b_{code}",
                "company_code": code,
                "company_name": name,
                "component": COMPONENT,
                "market": _infer_market(code),
                "query_mode": QUERY_MODE,
                "time_mark": TIME_MARK,
                "vary_type": VARY_TYPE,
                "further_scale_include": "yes",
                "expected_behavior": "captured_normal",
                "exclude_flags": (
                    "exclude_688671;exclude_301259;"
                    "exclude_sparse_oneMonth_b_sole_found_anchor;"
                    "exclude_esh_next_slice_DES101_105;"
                    "exclude_esh_first_slice_DES001_005;"
                    "exclude_esh_further_scale_s50_DES201_250;"
                    "exclude_dlc006r;exclude_ess_h3_h4"
                ),
                "notes": (
                    "further-scale S200 found-path candidate from denser-mode "
                    "leader/detail cite; NOT verified"
                ),
                "evidence_cite": "D-FM-07_leader_detail_cite_threeMonth_b",
                "universe_lock_status": "locked",
                "lock_date": "2026-07-16",
                "approval_task_id": "D-FM-07",
                "per_case_request_budget": "1",
                "total_request_cap": str(EXPECTED_SIZE),
                "shared_probe_prefer": "1",
                "dense_mode_cite_strength": "live_leader_detail_cite_total_rows",
            }
        )

    empty_start = CASE_ID_END - len(EMPTY_CONTROL_CODES) + 1
    for j, (code, name) in enumerate(EMPTY_CONTROL_CODES):
        case_id = f"DES{empty_start + j}"  # DES449, DES450
        rows.append(
            {
                "case_id": case_id,
                "probe_key": f"esh_fs_s200_empty_control_{code}",
                "company_code": code,
                "company_name": name,
                "component": COMPONENT,
                "market": _infer_market(code),
                "query_mode": QUERY_MODE,
                "time_mark": TIME_MARK,
                "vary_type": VARY_TYPE,
                "further_scale_include": "yes",
                "expected_behavior": "empty_but_valid",
                "exclude_flags": (
                    "exclude_688671;exclude_301259;"
                    "exclude_sparse_oneMonth_b_sole_found_anchor;"
                    "empty_control_from_esh_next_slice_DES102_105_live;"
                    "exclude_esh_further_scale_s50_DES201_250_mutation;"
                    "exclude_dlc006r;exclude_ess_h3_h4"
                ),
                "notes": (
                    "empty control retained; prior next-slice live proved absent "
                    "from denser-mode threeMonth+b after SECCODE filter"
                ),
                "evidence_cite": "D-FM-01_esh_next_slice_live_empty_control",
                "universe_lock_status": "locked",
                "lock_date": "2026-07-16",
                "approval_task_id": "D-FM-07",
                "per_case_request_budget": "1",
                "total_request_cap": str(EXPECTED_SIZE),
                "shared_probe_prefer": "1",
                "dense_mode_cite_strength": "live_leader_detail_cite_total_rows",
            }
        )

    rows_by_id = {r["case_id"]: r for r in rows}
    ordered = [rows_by_id[f"DES{i}"] for i in range(CASE_ID_START, CASE_ID_END + 1)]
    issues = validate_universe(ordered)
    if issues:
        print(f"ERROR: universe validation failed: {issues}", file=sys.stderr)
        return 2

    os.makedirs(VALIDATION, exist_ok=True)
    cite_payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "task_id": "D-FM-07",
        "endpoint": endpoint,
        "params": params,
        "http_status": http_status,
        "last_error": last_error,
        "cninfo_requests": stats.cninfo_requests,
        "total": total,
        "record_count": len(records),
        "unique_codes_after_exclusions": len(found_codes),
        "selected_found_codes": selected_found,
        "excluded_s50_found_codes": sorted(EXCLUDED_S50_FOUND_CODES),
        "case_id_range": f"DES{CASE_ID_START}-DES{CASE_ID_END}",
        "empty_control_codes": [c for c, _ in EMPTY_CONTROL_CODES],
        "excluded_prior_slice_codes": sorted(EXCLUDED_PRIOR_SLICE_CODES),
        "sample_records": records[:5],
    }
    with open(LEADER_DETAIL_CITE_JSON, "w", encoding="utf-8") as f:
        json.dump(cite_payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    fieldnames = list(ordered[0].keys())
    with open(DEFAULT_UNIVERSE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered)

    print(
        f"mode=executive_shareholding_further_scale_s200_universe_lock "
        f"cases={len(ordered)} cninfo_calls={stats.cninfo_requests} "
        f"leader_detail_total={total} selected_found={FOUND_SLOT_COUNT} empty_controls={len(EMPTY_CONTROL_CODES)}"
    )
    print(f"universe_csv={DEFAULT_UNIVERSE_CSV}")
    print(f"leader_detail_cite={LEADER_DETAIL_CITE_JSON}")
    print(f"universe_sha256={_sha256_file(DEFAULT_UNIVERSE_CSV)}")
    return 0 if not last_error and http_status == 200 else 2


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
                "time_mark": row["time_mark"],
                "vary_type": row["vary_type"],
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
                    f"shared_probes=1; query_mode={QUERY_MODE}; "
                    f"time_mark={TIME_MARK}; vary_type={VARY_TYPE}; "
                    f"company_filter_offline=SECCODE; "
                    f"forbidden_time_mark={FORBIDDEN_TIME_MARK}; "
                    f"exclude_esh_next_slice_DES101_105=yes; exclude_esh_further_scale_s50_DES201_250=yes"
                ),
            }
        )
    return dry


def write_planned_snapshots(
    rows: Sequence[Dict[str, str]], output_paths: Dict[str, str]
) -> None:
    snap_dir = os.path.join(output_paths["root"], "planned_snapshots")
    os.makedirs(snap_dir, exist_ok=True)
    params = _shared_params()
    for row in rows:
        payload = {
            "case_id": row["case_id"],
            "company_code": row["company_code"],
            "company_name": row["company_name"],
            "component": row["component"],
            "query_mode": row["query_mode"],
            "time_mark": row["time_mark"],
            "vary_type": row["vary_type"],
            "shared_probe_key": SHARED_PROBE_KEY,
            "planned_requests": [SHARED_PROBE_KEY],
            "query_params": params,
            "endpoint": ENDPOINT,
            "records_path": "data.records",
            "shared_request": True,
            "company_filter_offline": True,
            "company_filter_field": "SECCODE",
            "filter_company_code": row["company_code"],
            "forbidden_sole_found_time_mark": FORBIDDEN_TIME_MARK,
            "expected_behavior": row["expected_behavior"],
            "cninfo_called": False,
        }
        out = os.path.join(snap_dir, f"{row['case_id']}_executive_shareholding.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")


def write_dryrun_report(
    dry_rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    path = os.path.join(
        output_paths["reports"],
        "d_class_executive_shareholding_further_scale_s200_dryrun_report.csv",
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
        "# CNINFO D 类 executive_shareholding Further-Scale S200 Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** executive_shareholding further-scale S200 dry-run · **CNINFO calls = 0** · **NOT verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        "| planned_shared_cninfo_requests | **1** |",
        f"| planned_request_budget_total | **{len(dry_rows)}** |",
        "| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        f"- endpoint: `{ENDPOINT}`",
        f"- query mode: **{QUERY_MODE}**",
        f"- shared probe: **timeMark={TIME_MARK}** · **varyType={VARY_TYPE}**",
        f"- forbidden sole found timeMark: **{FORBIDDEN_TIME_MARK}**",
        "- company filter: **offline SECCODE**",
        "- isolated root: **cninfo_d_class_executive_shareholding_further_scale_s200**",
        "- frozen: ESH S50 DES201–250 / next-slice DES101–105 / first-slice / AT / SC / EP / RSU / FIA",
        "",
        "## Gates",
        "",
        "```text",
        "d_class_executive_shareholding_further_scale_s200_runner_extension_gate = READY_FOR_APPROVAL",
        "d_class_executive_shareholding_further_scale_s200_live_path_gate = READY_FOR_APPROVAL",
        "d_class_executive_shareholding_further_scale_s200_live_gate = NOT_APPROVED",
        "approval_status = R19_STANDING_SCOPE_BOUNDED",
        "```",
        "",
        f"**Future acceptance / excellence: ≥{PASS_THRESHOLD}/{EXPECTED_SIZE} "
        f"acceptable (≥{int(EXCELLENCE_ACCEPTABLE_RATE*100)}%) · fail/http=0 → "
        f"PASS_WITH_CAVEAT / excellence candidate**",
        "",
    ]
    path = os.path.join(
        output_paths["reports"],
        "d_class_executive_shareholding_further_scale_s200_dryrun_summary.md",
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
    notes = [
        f"shared_probe={SHARED_PROBE_KEY}",
        "company_filter=SECCODE",
        f"query_mode={row['query_mode']}",
        f"time_mark={row['time_mark']}",
        f"vary_type={row['vary_type']}",
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
            "leader/detail zero rows after SECCODE filter; legal empty per quality policy"
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
        "time_mark": row["time_mark"],
        "vary_type": row["vary_type"],
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
                "time_mark": row["time_mark"],
                "vary_type": row["vary_type"],
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
    params = _shared_params()
    payload, http_status, last_error = core._cninfo_request(
        session, component_cfg, params, stats, SHARED_PROBE_KEY
    )
    all_records = core._extract_records(payload) if payload is not None else []

    live_rows: List[Dict[str, str]] = []
    summaries: Dict[str, Dict[str, str]] = {}
    for row in sorted(universe_rows, key=lambda r: r["case_id"]):
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

    if stats.cninfo_requests != 1:
        print(
            f"ERROR: shared_cninfo_plan_mismatch:got={stats.cninfo_requests}",
            file=sys.stderr,
        )
        return 2

    gate = compute_gate(universe_rows, summaries)
    excel = excellence_metrics(live_rows)
    live_path = os.path.join(
        output_paths["reports"],
        "d_class_executive_shareholding_further_scale_s200_live_report.csv",
    )
    with open(live_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(live_rows)

    quality_rows = [{k: r[k] for k in QUALITY_COLUMNS} for r in live_rows]
    quality_path = os.path.join(
        output_paths["reports"],
        "d_class_executive_shareholding_further_scale_s200_quality_report.csv",
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
        "d_class_executive_shareholding_further_scale_s200_live_summary.md",
    )
    lines = [
        "# CNINFO D 类 executive_shareholding Further-Scale S200 Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** executive_shareholding further-scale S200 live · **R19 standing bounded** · **NOT verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(live_rows)}** |",
        f"| acceptable | **{acceptable}/{len(live_rows)}** |",
        f"| acceptable_rate | **{excel['acceptable_rate']*100:.2f}%** |",
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
        "d_class_executive_shareholding_further_scale_s200_live_path_gate = READY_FOR_APPROVAL",
        "d_class_executive_shareholding_further_scale_s200_live_gate = NOT_APPROVED",
        f"d_class_executive_shareholding_further_scale_s200_execution_gate = {gate}",
        "live_authority = R19_STANDING_SCOPE_BOUNDED",
        f"excellence_gated = {str(excel['excellent']).lower()}",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT bare PASS**",
        "",
        "## Caveats",
        "",
        "- denser-mode market-section density ≠ 全市场高管持股变动覆盖。",
        "- 仅 leader/detail 元数据路径；禁 oneMonth+b sole found 锚。",
        "- ESH S50 DES201–250 与 next-slice DES101–105 冻结根未 mutate。",
        "",
    ]
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(
        f"mode=executive_shareholding_further_scale_s200_live cases={len(live_rows)} "
        f"cninfo_calls={stats.cninfo_requests} acceptable={acceptable}/{len(live_rows)} "
        f"found={found} empty={empty} excellence={'YES' if excel['excellent'] else 'NO'}"
    )
    print(f"gate=d_class_executive_shareholding_further_scale_s200_execution_gate={gate}")
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
        f"mode=executive_shareholding_further_scale_s200_dry_run cases={len(dry_rows)} "
        f"planned_request_count_total=1 cninfo_calls=0"
    )
    print(
        "gate=d_class_executive_shareholding_further_scale_s200_runner_extension_gate="
        "READY_FOR_APPROVAL"
    )
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0


def run_live(args: argparse.Namespace) -> int:
    if not args.approve_d_class_executive_shareholding_further_scale_s200:
        print(
            "ERROR: approve_d_class_executive_shareholding_further_scale_s200_required",
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
        description="D-class executive_shareholding further-scale S200 (~200) runner"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build-universe-lock", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument(
        "--approve-d-class-executive-shareholding-further-scale-s200",
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
