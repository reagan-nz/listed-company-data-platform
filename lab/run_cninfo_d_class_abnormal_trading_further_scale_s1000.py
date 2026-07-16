#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 类 abnormal_trading further-scale S1000（~1000）孤立根 runner。

组成策略：多交易日 marketList（多页翻页）并集唯一码作为 found-path，
不足部分用 cite 验证缺席的 empty-control 补齐至 ~1000。
共享探针按「日 × 页」；离线 secCode 过滤。

不写入 AT further_scale S50 / S200 / next_slice / ESH / SC / EP / RSU / FIA 冻结根。

用法：
  .venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale_s1000.py --build-universe-lock
  .venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale_s1000.py --dry-run \\
      --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s1000_universe_lock_20260716.csv \\
      --output-root outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s1000
  .venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale_s1000.py --live \\
      --approve-d-class-abnormal-trading-further-scale-s1000 \\
      --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s1000_universe_lock_20260716.csv \\
      --output-root outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s1000
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

COMPONENT = "abnormal_trading"
# 禁止作为 found 唯一锚点的稀疏日
FORBIDDEN_ANCHOR = "2026-07-03"
# 多日拼合候选（跳过周末 / 已知空窗 / 禁止日）；按密度优先排序在 cite 时再过滤 total=0
COMPOSE_TDATES = [
    "2026-07-15",
    "2026-07-14",
    "2026-07-13",
    "2026-07-10",
    "2026-07-09",
    "2026-07-08",
    "2026-07-07",
    "2026-07-06",
    "2026-07-02",
    "2026-07-01",
    "2026-06-30",
    "2026-06-26",
    "2026-06-25",
    "2026-06-24",
]
PRIMARY_TDATE = "2026-07-02"  # empty-control 锚点日（亦在拼合窗内）
ENDPOINT = "https://www.cninfo.com.cn/data/statis/getMarketStatisticsData"
SHARED_ROWS = 300
MAX_PAGES_PER_DAY = 20
EXPECTED_SIZE = 1000
# excellence：acceptable >= 95% → ≥950/1000
PASS_THRESHOLD = 950
EXCELLENCE_ACCEPTABLE_RATE = 0.95
CASE_ID_START = 501
CASE_ID_END = 1500  # inclusive → 1000 cases
EMPTY_CONTROL_MIN = 10  # 至少保留若干 empty-control 路径

DEFAULT_OUTPUT_ROOT = os.path.join(
    VALIDATION, "cninfo_d_class_abnormal_trading_further_scale_s1000"
)
DEFAULT_UNIVERSE_CSV = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_further_scale_s1000_universe_lock_20260716.csv",
)
MARKETLIST_CITE_JSON = os.path.join(
    VALIDATION,
    "cninfo_d_class_abnormal_trading_further_scale_s1000_marketlist_cite_20260716.json",
)

FORBIDDEN_CODES = {"688671", "301259"}
# 空控种子：优先 S50/S200 已证空控与大盘蓝筹
EMPTY_CONTROL_SEEDS = [
    ("000895", "双汇发展"),
    ("601988", "中国银行"),
    ("600519", "贵州茅台"),
    ("000858", "五粮液"),
    ("601318", "中国平安"),
    ("600036", "招商银行"),
    ("601166", "兴业银行"),
    ("000002", "万科A"),
    ("601398", "工商银行"),
    ("601939", "建设银行"),
    ("601288", "农业银行"),
    ("600000", "浦发银行"),
    ("000001", "平安银行"),
    ("601328", "交通银行"),
    ("600276", "恒瑞医药"),
    ("000568", "泸州老窖"),
    ("000596", "古井贡酒"),
    ("600887", "伊利股份"),
    ("601012", "隆基绿能"),
    ("002415", "海康威视"),
]
EXCLUDED_NEXT_SLICE_CODES = {"000895", "600000", "002415", "000001", "601988"}

FROZEN_BLOCK_ROOTS = (
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_further_scale"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_further_scale_s200"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_abnormal_trading_first_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_next_slice"),
    os.path.join(VALIDATION, "cninfo_d_class_executive_shareholding_first_slice"),
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


def _shared_params(tdate: str, page: int = 1) -> Dict[str, Any]:
    return {
        "sdate": tdate,
        "edate": tdate,
        "platecode": "",
        "orderby": "",
        "page": page,
        "rows": SHARED_ROWS,
    }


def _probe_key(tdate: str, page: int = 1) -> str:
    return f"single_day_paged_{tdate}_rows{SHARED_ROWS}_p{page}"


def _day_probe_key(tdate: str) -> str:
    return f"single_day_multipage_{tdate}_rows{SHARED_ROWS}"


def _normalize_root(path: str) -> str:
    return os.path.abspath(path)


def _looks_like_ashare(code: str) -> bool:
    if len(code) != 6 or not code.isdigit():
        return False
    return code[0] in ("0", "3", "6")


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    root = _normalize_root(output_root)
    expected = _normalize_root(DEFAULT_OUTPUT_ROOT)
    if root != expected:
        return False, (
            "abnormal_trading_further_scale_s1000_output_root_must_be_"
            "cninfo_d_class_abnormal_trading_further_scale_s1000"
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
            f"abnormal_trading_further_scale_s1000_universe_size_must_equal_{EXPECTED_SIZE}:"
            f"got={len(rows)}"
        )
    seen_cases: Set[str] = set()
    seen_codes: Set[str] = set()
    expected_ids = {f"DAT{i}" for i in range(CASE_ID_START, CASE_ID_END + 1)}
    allowed_anchors = set(COMPOSE_TDATES) | {PRIMARY_TDATE}
    for row in rows:
        case_id = row.get("case_id", "").strip()
        code = row.get("company_code", "").strip()
        component = row.get("component", "").strip()
        anchor = row.get("anchor_tdate", "").strip()
        query_mode = row.get("query_mode", "").strip()
        include = row.get("further_scale_include", "").strip().lower()
        if case_id in seen_cases:
            issues.append(f"duplicate_case_id:{case_id}")
        seen_cases.add(case_id)
        if case_id not in expected_ids:
            issues.append(
                f"forbidden_case_id_in_abnormal_trading_further_scale_s1000:{case_id}"
            )
        if code in seen_codes:
            issues.append(f"duplicate_company_code:{code}")
        seen_codes.add(code)
        if code in FORBIDDEN_CODES:
            issues.append(f"forbidden_company_code:{code}")
        if component != COMPONENT:
            issues.append(f"component_must_be_abnormal_trading:{case_id}")
        if anchor not in allowed_anchors:
            issues.append(f"anchor_tdate_not_in_s1000_compose:{case_id}:{anchor}")
        if anchor == FORBIDDEN_ANCHOR:
            issues.append(f"forbidden_anchor_tdate:{case_id}")
        if query_mode != "single_day_paged":
            issues.append(f"query_mode_mismatch:{case_id}")
        if include != "yes":
            issues.append(f"further_scale_include_must_be_yes:{case_id}")
    if seen_cases != expected_ids:
        issues.append("case_id_set_must_be_DAT501_DAT1500")
    return issues


def _extract_code_map(
    records: Sequence[Dict[str, Any]],
    extra_exclude: Optional[Set[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    exclude = set(FORBIDDEN_CODES) | set(EXCLUDED_NEXT_SLICE_CODES)
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


def _fetch_day_all_pages(
    session: requests.Session,
    component_cfg: Dict[str, Any],
    stats: Any,
    tdate: str,
    label_prefix: str,
) -> Dict[str, Any]:
    """单日多页 marketList 拉取；rows=SHARED_ROWS。"""
    all_records: List[Dict[str, Any]] = []
    total: Optional[int] = None
    pages_fetched = 0
    last_http = 0
    last_error = ""
    page_params: List[Dict[str, Any]] = []
    for page in range(1, MAX_PAGES_PER_DAY + 1):
        params = _shared_params(tdate, page=page)
        payload, http_status, last_error = core._cninfo_request(
            session, component_cfg, params, stats, f"{label_prefix}_p{page}"
        )
        last_http = http_status
        page_params.append(params)
        pages_fetched += 1
        if http_status != 200 or last_error:
            break
        if isinstance(payload, dict) and payload.get("total") is not None:
            try:
                total = int(payload.get("total"))
            except (TypeError, ValueError):
                total = total
        records = core._extract_records(payload) if payload is not None else []
        if not records:
            break
        all_records.extend(records)
        if total is not None and len(all_records) >= total:
            break
        if len(records) < SHARED_ROWS:
            break
    return {
        "tdate": tdate,
        "params_pages": page_params,
        "http_status": last_http,
        "last_error": last_error,
        "total": total,
        "record_count": len(all_records),
        "pages_fetched": pages_fetched,
        "records": all_records,
        "by_code": _extract_code_map(all_records),
    }


def _iter_empty_control_candidates(present_union: Set[str]) -> List[Tuple[str, str]]:
    """离线生成 empty-control 候选：种子 + A 股常见号段扫描（不读其他轨文件）。"""
    out: List[Tuple[str, str]] = []
    seen: Set[str] = set()
    for code, name in EMPTY_CONTROL_SEEDS:
        code = code.zfill(6)
        if code in present_union or code in FORBIDDEN_CODES or code in seen:
            continue
        seen.add(code)
        out.append((code, name))
    # 号段扫描补齐（仅 0/3/6 开头）
    for i in range(1, 700000):
        code = f"{i:06d}"
        if not _looks_like_ashare(code):
            continue
        if code in present_union or code in FORBIDDEN_CODES or code in seen:
            continue
        seen.add(code)
        out.append((code, f"empty_control_{code}"))
        if len(out) >= EXPECTED_SIZE:
            break
    return out


def build_universe_lock_from_cite() -> int:
    """多日多页 CNINFO cite → 拼合 DAT501–1500 lock（found 并集 + empty 补齐）。"""
    endpoints = core.load_registry_endpoints()
    source_configs = core.load_table_source_configs()
    component_cfg = copy.deepcopy(source_configs.get(COMPONENT, {}))
    endpoint = endpoints.get(COMPONENT, component_cfg.get("api_url", ENDPOINT))
    component_cfg["api_url"] = endpoint

    session = requests.Session()
    stats = core.LiveStats()

    day_cites: List[Dict[str, Any]] = []
    # code -> (tdate, rec) 首次出现日
    union_first: Dict[str, Tuple[str, Dict[str, Any]]] = {}
    present_union_raw: Set[str] = set()

    for tdate in COMPOSE_TDATES:
        if tdate == FORBIDDEN_ANCHOR:
            continue
        cited = _fetch_day_all_pages(
            session, component_cfg, stats, tdate, f"at_s1000_cite_{tdate}"
        )
        day_cites.append(cited)
        for rec in cited["records"]:
            code = core._company_code_from_record(rec)
            if code:
                present_union_raw.add(code.zfill(6))
        for code, rec in cited["by_code"].items():
            if code not in union_first:
                union_first[code] = (tdate, rec)
        print(
            f"cite_day={tdate} pages={cited['pages_fetched']} total={cited['total']} "
            f"day_unique={len(cited['by_code'])} union={len(union_first)} "
            f"cninfo={stats.cninfo_requests}",
            flush=True,
        )

    # 丢弃完全空窗日（仍计入 cite 证据）
    productive_days = [d for d in day_cites if d["by_code"]]
    if not productive_days:
        print("ERROR: no productive compose days from cite", file=sys.stderr)
        return 2

    empty_candidates = _iter_empty_control_candidates(present_union_raw)
    found_available = sorted(union_first.keys())
    # 保留至少 EMPTY_CONTROL_MIN 个空控
    max_found = EXPECTED_SIZE - EMPTY_CONTROL_MIN
    selected_found_codes = found_available[: min(len(found_available), max_found)]
    empty_needed = EXPECTED_SIZE - len(selected_found_codes)
    if len(empty_candidates) < empty_needed:
        print(
            "ERROR: insufficient empty-control candidates: "
            f"got={len(empty_candidates)} need={empty_needed}",
            file=sys.stderr,
        )
        return 2
    selected_empty = empty_candidates[:empty_needed]

    rows: List[Dict[str, str]] = []
    case_idx = CASE_ID_START
    compose_days_used = sorted({union_first[c][0] for c in selected_found_codes})

    def _append_found(code: str, rec: Dict[str, Any], tdate: str) -> None:
        nonlocal case_idx
        name = str(rec.get("secName") or rec.get("SECNAME") or "").strip() or code
        rows.append(
            {
                "case_id": f"DAT{case_idx}",
                "probe_key": f"at_s1000_shared_{tdate}_{code}",
                "company_code": code,
                "company_name": name,
                "component": COMPONENT,
                "market": _infer_market(code),
                "query_mode": "single_day_paged",
                "anchor_tdate": tdate,
                "further_scale_include": "yes",
                "expected_behavior": "captured_normal",
                "exclude_flags": (
                    "exclude_688671;exclude_301259;"
                    "exclude_sparse_day_20260703_sole_found_anchor;"
                    "exclude_at_next_slice_DAT101_105;"
                    "exclude_at_further_scale_s50_s200_roots;"
                    "detail_nested_deferred"
                ),
                "notes": (
                    f"s1000 found-path from multi_day_multipage cite day={tdate}; "
                    "NOT verified"
                ),
                "evidence_cite": f"D-FM-05_multiday_{tdate.replace('-', '')}",
                "universe_lock_status": "locked",
                "lock_date": "2026-07-16",
                "approval_task_id": "D-FM-05",
                "per_case_request_budget": "1",
                "total_request_cap": str(EXPECTED_SIZE),
                "shared_probe_prefer": "1",
                "shared_rows": str(SHARED_ROWS),
                "dense_day_cite_strength": "multi_day_multipage_compose_plus_empty_pad",
                "compose_source_day": tdate,
            }
        )
        case_idx += 1

    for code in selected_found_codes:
        tdate, rec = union_first[code]
        _append_found(code, rec, tdate)

    for code, name in selected_empty:
        rows.append(
            {
                "case_id": f"DAT{case_idx}",
                "probe_key": f"at_s1000_empty_control_{code}",
                "company_code": code,
                "company_name": name,
                "component": COMPONENT,
                "market": _infer_market(code),
                "query_mode": "single_day_paged",
                "anchor_tdate": PRIMARY_TDATE,
                "further_scale_include": "yes",
                "expected_behavior": "empty_but_valid",
                "exclude_flags": (
                    "exclude_688671;exclude_301259;"
                    "exclude_sparse_day_20260703_sole_found_anchor;"
                    "empty_control_not_in_s1000_compose_marketlist;"
                    "detail_nested_deferred"
                ),
                "notes": (
                    "empty control for s1000 compose; cite-verified absent from "
                    f"compose_days={','.join(compose_days_used)}"
                ),
                "evidence_cite": "D-FM-05_empty_control_compose_pad",
                "universe_lock_status": "locked",
                "lock_date": "2026-07-16",
                "approval_task_id": "D-FM-05",
                "per_case_request_budget": "1",
                "total_request_cap": str(EXPECTED_SIZE),
                "shared_probe_prefer": "1",
                "shared_rows": str(SHARED_ROWS),
                "dense_day_cite_strength": "multi_day_multipage_compose_plus_empty_pad",
                "compose_source_day": PRIMARY_TDATE,
            }
        )
        case_idx += 1

    if len(rows) != EXPECTED_SIZE:
        print(
            f"ERROR: composed universe size mismatch: got={len(rows)} "
            f"expected={EXPECTED_SIZE}",
            file=sys.stderr,
        )
        return 2

    rows_by_id = {r["case_id"]: r for r in rows}
    ordered = [rows_by_id[f"DAT{i}"] for i in range(CASE_ID_START, CASE_ID_END + 1)]
    issues = validate_universe(ordered)
    if issues:
        print(f"ERROR: universe validation failed: {issues}", file=sys.stderr)
        return 2

    os.makedirs(VALIDATION, exist_ok=True)
    cite_days_payload = []
    for d in day_cites:
        cite_days_payload.append(
            {
                "tdate": d["tdate"],
                "params_pages": d["params_pages"],
                "http_status": d["http_status"],
                "last_error": d["last_error"],
                "total": d["total"],
                "record_count": d["record_count"],
                "pages_fetched": d["pages_fetched"],
                "unique_codes_after_exclusions": len(d["by_code"]),
                "sample_records": d["records"][:2],
            }
        )
    cite_payload = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "task_id": "D-FM-05",
        "endpoint": endpoint,
        "cninfo_requests": stats.cninfo_requests,
        "compose_tdates_planned": COMPOSE_TDATES,
        "forbidden_anchor": FORBIDDEN_ANCHOR,
        "primary_empty_anchor": PRIMARY_TDATE,
        "shared_rows": SHARED_ROWS,
        "days": cite_days_payload,
        "compose": {
            "expected_size": EXPECTED_SIZE,
            "found_union_available": len(found_available),
            "selected_found": len(selected_found_codes),
            "empty_controls": len(selected_empty),
            "empty_control_min": EMPTY_CONTROL_MIN,
            "compose_days_used": compose_days_used,
            "case_id_range": f"DAT{CASE_ID_START}-DAT{CASE_ID_END}",
            "pad_note": (
                "empty_controls pad to EXPECTED_SIZE when multi-day union "
                "< found_budget; documented empty_control_not_in_compose_marketlist"
            ),
        },
    }
    with open(MARKETLIST_CITE_JSON, "w", encoding="utf-8") as f:
        json.dump(cite_payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    fieldnames = list(ordered[0].keys())
    with open(DEFAULT_UNIVERSE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered)

    ok_http = all(
        d["http_status"] == 200 and not d["last_error"] for d in day_cites
    )
    print(
        f"mode=abnormal_trading_further_scale_s1000_universe_lock "
        f"cases={len(ordered)} cninfo_calls={stats.cninfo_requests} "
        f"found_union={len(found_available)} selected_found={len(selected_found_codes)} "
        f"empty_controls={len(selected_empty)} compose_days={len(compose_days_used)}"
    )
    print(f"universe_csv={DEFAULT_UNIVERSE_CSV}")
    print(f"marketlist_cite={MARKETLIST_CITE_JSON}")
    print(f"universe_sha256={_sha256_file(DEFAULT_UNIVERSE_CSV)}")
    return 0 if ok_http else 2


def build_dryrun_rows(
    rows: Sequence[Dict[str, str]], output_root: str
) -> List[Dict[str, str]]:
    dry: List[Dict[str, str]] = []
    unique_days = sorted({r["anchor_tdate"] for r in rows})
    for row in rows:
        tdate = row["anchor_tdate"]
        dry.append(
            {
                "case_id": row["case_id"],
                "company_code": row["company_code"],
                "company_name": row["company_name"],
                "component": row["component"],
                "market": row["market"],
                "query_mode": row["query_mode"],
                "anchor_tdate": tdate,
                "further_scale_include": row["further_scale_include"],
                "expected_behavior": row["expected_behavior"],
                "planned_request_count": "1",
                "shared_probe_key": _day_probe_key(tdate),
                "planned_output_root": output_root,
                "planned_endpoint": ENDPOINT,
                "cninfo_call_planned": "shared_per_day_multipage",
                "pdf_download": "no",
                "ocr": "no",
                "extraction": "no",
                "db_write": "no",
                "minio_write": "no",
                "rag_run": "no",
                "dryrun_status": "planned_ok",
                "notes": (
                    f"anchor={tdate}; shared_probe_days={len(unique_days)}; "
                    f"rows={SHARED_ROWS}; multipage=yes; "
                    f"company_filter_offline=secCode; "
                    f"forbidden_anchor={FORBIDDEN_ANCHOR}; "
                    f"compose=multi_day_multipage_plus_empty_pad; "
                    f"detail_nested_deferred=yes"
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
            "anchor_tdate": tdate,
            "query_mode": row["query_mode"],
            "shared_probe_key": _day_probe_key(tdate),
            "planned_requests": [_day_probe_key(tdate)],
            "query_params": _shared_params(tdate, page=1),
            "endpoint": ENDPOINT,
            "records_path": "marketList",
            "shared_request": True,
            "multipage": True,
            "company_filter_offline": True,
            "company_filter_field": "secCode",
            "filter_company_code": row["company_code"],
            "forbidden_sole_found_anchor": FORBIDDEN_ANCHOR,
            "expected_behavior": row["expected_behavior"],
            "cninfo_called": False,
            "detail_nested_deferred": True,
            "compose_note": "multi_day_multipage_plus_empty_pad",
        }
        out = os.path.join(snap_dir, f"{row['case_id']}_abnormal_trading.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")


def write_dryrun_report(
    dry_rows: List[Dict[str, str]], output_paths: Dict[str, str]
) -> str:
    path = os.path.join(
        output_paths["reports"],
        "d_class_abnormal_trading_further_scale_s1000_dryrun_report.csv",
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
    unique_days = sorted({r["anchor_tdate"] for r in dry_rows})
    lines = [
        "# CNINFO D 类 abnormal_trading Further-Scale S1000 Dry-run Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** abnormal_trading further-scale S1000 dry-run · **CNINFO calls = 0** · **NOT verified**",
        "",
        "## Counts",
        "",
        "| 指标 | 值 |",
        "|------|-----|",
        f"| cases | **{len(dry_rows)}** |",
        f"| planned_ok | **{len(dry_rows)}/{len(dry_rows)}** |",
        f"| planned_shared_cninfo_days | **{len(unique_days)}**（按日多页共享） |",
        f"| planned_request_budget_total | **{len(dry_rows)}** |",
        "| CNINFO calls | **0** |",
        f"| universe | `{universe_csv}` |",
        "",
        "## Endpoint",
        "",
        f"- endpoint: `{ENDPOINT}`",
        "- query mode: **single_day_paged**（multi-page per day）",
        f"- compose days planned: `{', '.join(COMPOSE_TDATES)}`",
        f"- shared probes: **{len(unique_days)}** day(s) · rows={SHARED_ROWS} · multipage",
        f"- forbidden sole found anchor: **{FORBIDDEN_ANCHOR}**",
        "- company filter: **offline secCode**",
        "",
        "## Gates",
        "",
        "```text",
        "d_class_abnormal_trading_further_scale_s1000_dryrun_gate = PASS_OFFLINE",
        "d_class_abnormal_trading_further_scale_s1000_live_gate = NOT_APPROVED",
        "approval_status = R19_STANDING_SCOPE_BOUNDED",
        "```",
        "",
        f"**Future acceptance threshold: ≥{PASS_THRESHOLD}/{EXPECTED_SIZE} "
        f"acceptable (≥{int(EXCELLENCE_ACCEPTABLE_RATE*100)}%) → PASS_WITH_CAVEAT / excellence candidate**",
        "",
    ]
    path = os.path.join(
        output_paths["reports"],
        "d_class_abnormal_trading_further_scale_s1000_dryrun_summary.md",
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
        f"shared_probe={_day_probe_key(tdate)}",
        "company_filter=secCode",
        f"anchor={tdate}",
        f"rows={SHARED_ROWS}",
        "multipage=yes",
        "detail_nested_deferred=yes",
        "compose=multi_day_multipage_plus_empty_pad",
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
        notes.append("marketList zero rows after secCode filter")
    else:
        retrieval_status = "found"
        quality_status = "pass"
        lineage_status = "discovered"
        empty_but_valid = "no"
        notes.append(f"found {record_count} row(s)")

    return {
        "case_id": row["case_id"],
        "company_code": row["company_code"],
        "company_name": row["company_name"],
        "component": row["component"],
        "market": row["market"],
        "query_mode": row["query_mode"],
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
                "anchor_tdate": row["anchor_tdate"],
                "retrieval_status": summary.get("retrieval_status", ""),
                "quality_status": summary.get("quality_status", ""),
                "lineage_status": summary.get("lineage_status", ""),
                "record_count": summary.get("record_count", "0"),
                "endpoint_used": summary.get("endpoint_used", ""),
                "query_params": summary.get("_used_params") or {},
                "sample_records": summary.get("_sample_records") or [],
                "shared_probe": _day_probe_key(row["anchor_tdate"]),
                "cninfo_called": True,
                "detail_nested_deferred": True,
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


def excellence_metrics(
    live_rows: Sequence[Dict[str, str]],
) -> Dict[str, Any]:
    n = len(live_rows)
    acceptable = sum(1 for r in live_rows if r["acceptable"] == "yes")
    failed = sum(
        1
        for r in live_rows
        if r["retrieval_status"] in ("http_error", "blocked")
        or r.get("failure_type") == "transport_or_http_error"
    )
    http_error = sum(1 for r in live_rows if r["retrieval_status"] == "http_error")
    rate = (acceptable / n) if n else 0.0
    excellent = (
        rate >= EXCELLENCE_ACCEPTABLE_RATE and failed == 0 and http_error == 0
    )
    return {
        "cases": n,
        "acceptable": acceptable,
        "acceptable_rate": rate,
        "failed_or_http_error": failed,
        "http_error": http_error,
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

    # 按日多页共享探针
    day_payloads: Dict[str, Tuple[List[Dict[str, Any]], int, str, Dict[str, Any], int]] = {}
    unique_days = sorted({r["anchor_tdate"] for r in universe_rows})
    planned_pages = 0
    for tdate in unique_days:
        cited = _fetch_day_all_pages(
            session, component_cfg, stats, tdate, f"at_s1000_live_{tdate}"
        )
        planned_pages += cited["pages_fetched"]
        params0 = (
            cited["params_pages"][0]
            if cited["params_pages"]
            else _shared_params(tdate, page=1)
        )
        day_payloads[tdate] = (
            cited["records"],
            cited["http_status"],
            cited["last_error"],
            params0,
            cited["pages_fetched"],
        )

    live_rows: List[Dict[str, str]] = []
    summaries: Dict[str, Dict[str, str]] = {}
    for row in sorted(universe_rows, key=lambda r: r["case_id"]):
        tdate = row["anchor_tdate"]
        all_records, http_status, last_error, params, _pages = day_payloads[tdate]
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

    if stats.cninfo_requests != planned_pages:
        print(
            f"ERROR: shared_cninfo_plan_mismatch:got={stats.cninfo_requests}"
            f":expected_pages={planned_pages}",
            file=sys.stderr,
        )
        return 2

    gate = compute_gate(universe_rows, summaries)
    excel = excellence_metrics(live_rows)
    live_path = os.path.join(
        output_paths["reports"],
        "d_class_abnormal_trading_further_scale_s1000_live_report.csv",
    )
    with open(live_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LIVE_REPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(live_rows)

    quality_rows = [{k: r[k] for k in QUALITY_COLUMNS} for r in live_rows]
    quality_path = os.path.join(
        output_paths["reports"],
        "d_class_abnormal_trading_further_scale_s1000_quality_report.csv",
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
        "d_class_abnormal_trading_further_scale_s1000_live_summary.md",
    )
    lines = [
        "# CNINFO D 类 abnormal_trading Further-Scale S1000 Live Summary",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        "> **性质：** abnormal_trading further-scale S1000 live · **R19 standing bounded** · **NOT verified**",
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
        f"| unique_anchor_days | **{len(unique_days)}** |",
        f"| excellence | **{'YES' if excel['excellent'] else 'NO'}** |",
        "",
        "## Gates",
        "",
        "```text",
        f"d_class_abnormal_trading_further_scale_s1000_execution_gate = {gate}",
        "live_authority = R19_STANDING_SCOPE_BOUNDED",
        f"excellence_gated = {str(excel['excellent']).lower()}",
        "```",
        "",
        "**NOT verified** · **NOT production_ready** · **NOT bare PASS**",
        "",
        "## Caveats",
        "",
        "- multi_day_multipage_compose_not_full_market：多日并集 + empty pad，"
        "非全市场 abnormal_trading 覆盖。",
        "- empty_control_pad_documented：found 并集不足时以 cite 验证缺席码补齐。",
        "- detail_nested_deferred：仅 marketList 元数据路径。",
        "",
    ]
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(
        f"mode=abnormal_trading_further_scale_s1000_live cases={len(live_rows)} "
        f"cninfo_calls={stats.cninfo_requests} acceptable={acceptable}/{len(live_rows)} "
        f"rate={excel['acceptable_rate']*100:.2f}% found={found} empty={empty} "
        f"excellent={excel['excellent']}"
    )
    print(f"gate=d_class_abnormal_trading_further_scale_s1000_execution_gate={gate}")
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
    unique_days = sorted({r["anchor_tdate"] for r in dry_rows})
    print(
        f"mode=abnormal_trading_further_scale_s1000_dry_run cases={len(dry_rows)} "
        f"planned_shared_days={len(unique_days)} cninfo_calls=0"
    )
    print("gate=d_class_abnormal_trading_further_scale_s1000_dryrun_gate=PASS_OFFLINE")
    print(f"dryrun_report={report_path}")
    print(f"dryrun_summary={summary_path}")
    return 0


def run_live(args: argparse.Namespace) -> int:
    if not args.approve_d_class_abnormal_trading_further_scale_s1000:
        print(
            "ERROR: approve_d_class_abnormal_trading_further_scale_s1000_required",
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
        description="D-class abnormal_trading further-scale S1000 (~1000) runner"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build-universe-lock", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--live", action="store_true")
    parser.add_argument(
        "--approve-d-class-abnormal-trading-further-scale-s1000",
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
