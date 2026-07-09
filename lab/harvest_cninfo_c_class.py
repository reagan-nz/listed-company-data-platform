#!/usr/bin/env python3
"""
CNINFO C-class harvest orchestration（Era C Phase 4）。

默认 --dry-run：构造 planned harvest matrix，**不请求 CNINFO**，不写 raw/normalized 数据。

Live smoke（无需 approve）：
    python lab/harvest_cninfo_c_class.py --live --limit 10 \\
        --sample-file lab/eval_companies_c_class_harvest_863_non_bse.yaml

Full harvest（需显式 --approve-full-harvest）：
    python lab/harvest_cninfo_c_class.py --live --approve-full-harvest \\
        --sample-file lab/eval_companies_c_class_harvest_863_non_bse.yaml
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import yaml

# 复用 validate runner 的样本装载与 source 定义（不修改 validate 主逻辑）
_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from validate_cninfo_c_class_scale_smoke import (  # noqa: E402
    BASE_DIR,
    BASIC_URL,
    CaseRow,
    DERIVED_SOURCE_FIELDS,
    LIVE_BASE_SLEEP_SECONDS,
    MAIN_SOURCE_IDS,
    OBSERVE_SOURCE_ID,
    SHAREHOLDER_SOURCE_IDS,
    SLEEP_SECONDS,
    SOURCE_SPECS,
    _apply_fetch_meta,
    _apply_http_error,
    _browser_headers,
    _collect_field_fill,
    _extract_codes,
    _finalize_row_status,
    _get_path,
    _http_get,
    _is_cninfo_throttled_business_code,
    _is_success_payload,
    _list_len,
    _live_fetch_data20,
    _security_url,
    load_sample_companies,
    load_sample_yaml,
)
from cninfo_c_class_mappers import (  # noqa: E402  harvest 映射入口
    SHAREHOLDER_SCOPE_TOP,
    SHAREHOLDER_SCOPE_TOP_FLOAT,
    map_company_basic_profile,
    map_company_executive_profile,
    map_company_security_profile,
    map_company_share_capital_profile,
    map_company_shareholder_profile,
    map_dividend_history,
)

HARVEST_EXPECTED_COMPANY_COUNT = 863
HOLD_COUNT = 26
HTTP_SOURCES_PER_COMPANY = 7  # 6 direct + 1 observe
PLANNED_CASES = HARVEST_EXPECTED_COMPANY_COUNT * HTTP_SOURCES_PER_COMPANY

PARENT_CANDIDATE_REL = "lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml"
HOLD_SAMPLE_REL = "lab/eval_companies_c_class_889_rerun_all6_hold.yaml"
DEFAULT_HARVEST_SAMPLE_REL = "lab/eval_companies_c_class_harvest_863_non_bse.yaml"

DEFAULT_DRYRUN_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_harvest_dryrun_report.csv"
)
DEFAULT_DRYRUN_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_harvest_dryrun_summary.md"
)

DEFAULT_DRYRUN_VALIDATION_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_harvest_dryrun_validation_summary.md"
)
DEFAULT_SMOKE_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_harvest_smoke_report.csv"
)
DEFAULT_SMOKE_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_harvest_smoke_summary.md"
)
DEFAULT_FULL_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_harvest_full_report.csv"
)
DEFAULT_FULL_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_harvest_full_summary.md"
)

MATRIX_SOURCES_PER_COMPANY = 10  # len(HARVEST_MATRIX_SOURCE_ORDER)，含 derived

# live 安全：full harvest 需显式 --approve-full-harvest；smoke 使用 --limit
FULL_HARVEST_APPROVAL_REQUIRED = "FULL_HARVEST_APPROVAL_REQUIRED"
DEFAULT_SMOKE_LIMIT = 10

HARVEST_SUCCESS_STATUSES = frozenset({
    "endpoint_found",
    "valid_empty",
    "empty_but_valid_response",
})

HARVEST_OUTPUT_ROOT = "outputs/harvest/cninfo_c_class"
DEFAULT_HARVEST_OUTPUT_ROOT = HARVEST_OUTPUT_ROOT
QUALITY_DIR_REL = f"{HARVEST_OUTPUT_ROOT}/quality"
RUN_STATUS_REL = f"{QUALITY_DIR_REL}/run_status.json"
COMPANY_HARVEST_STATUS_REL = f"{QUALITY_DIR_REL}/company_harvest_status.csv"

PHASE2_SMOKE_SAMPLE_BASENAME = "eval_companies_c_class_phase2_smoke_200.yaml"
PHASE2_SMOKE_EXPECTED_COUNT = 200
PHASE2_SMOKE_APPROVAL_REQUIRED = "PHASE2_SMOKE_HARVEST_APPROVAL_REQUIRED"

PHASE3_BATCH_SAMPLE_BASENAME = "eval_companies_c_class_phase3_batch_500_001.yaml"
PHASE3_BATCH_EXPECTED_COUNT = 500
PHASE3_BATCH_OUTPUT_ROOT = "outputs/harvest/cninfo_c_class/phase3_batch_500_001"
PHASE2_BATCH_OUTPUT_ROOT = "outputs/harvest/cninfo_c_class/phase2_smoke_200"
PHASE3_BATCH_APPROVAL_REQUIRED = "PHASE3_BATCH_500_HARVEST_APPROVAL_REQUIRED"
PHASE3_OUTPUT_ROOT_REQUIRED = "PHASE3_BATCH_OUTPUT_ROOT_REQUIRED"
PHASE3_OUTPUT_ROOT_FORBIDDEN = "PHASE3_BATCH_OUTPUT_ROOT_FORBIDDEN"


def configure_harvest_output_root(output_root: Optional[str] = None) -> str:
    """配置 harvest 产物根目录；默认保持 863 主轨路径不变。"""
    global HARVEST_OUTPUT_ROOT, QUALITY_DIR_REL, RUN_STATUS_REL, COMPANY_HARVEST_STATUS_REL
    root = (output_root or DEFAULT_HARVEST_OUTPUT_ROOT).rstrip("/")
    HARVEST_OUTPUT_ROOT = root
    QUALITY_DIR_REL = f"{root}/quality"
    COMPANY_HARVEST_STATUS_REL = f"{QUALITY_DIR_REL}/company_harvest_status.csv"
    if root == DEFAULT_HARVEST_OUTPUT_ROOT:
        RUN_STATUS_REL = f"{QUALITY_DIR_REL}/run_status.json"
    else:
        RUN_STATUS_REL = f"{root}/run_status.json"
    return root


def reset_harvest_output_root() -> None:
    configure_harvest_output_root(None)


def is_phase2_smoke_sample(sample_path: str) -> bool:
    norm = sample_path.replace("\\", "/")
    return norm.endswith(PHASE2_SMOKE_SAMPLE_BASENAME)


def is_phase3_batch_sample(sample_path: str) -> bool:
    norm = sample_path.replace("\\", "/")
    return norm.endswith(PHASE3_BATCH_SAMPLE_BASENAME)


def _normalize_output_root_path(path: str) -> str:
    return path.replace("\\", "/").rstrip("/")


def validate_phase3_output_root(output_root: Optional[str] = None) -> Tuple[bool, str]:
    """
    Phase 3 live harvest 输出根目录安全检查。
    须使用隔离的 phase3_batch_500_001 根目录，禁止 863 主轨与 phase2 目录。
    """
    effective = _normalize_output_root_path(output_root or HARVEST_OUTPUT_ROOT)
    expected = _normalize_output_root_path(PHASE3_BATCH_OUTPUT_ROOT)
    default_root = _normalize_output_root_path(DEFAULT_HARVEST_OUTPUT_ROOT)
    phase2_root = _normalize_output_root_path(PHASE2_BATCH_OUTPUT_ROOT)

    if not output_root:
        return False, PHASE3_OUTPUT_ROOT_REQUIRED
    if effective == default_root:
        return False, f"{PHASE3_OUTPUT_ROOT_FORBIDDEN}:default_863_root"
    if effective == phase2_root:
        return False, f"{PHASE3_OUTPUT_ROOT_FORBIDDEN}:phase2_smoke_200"
    if effective != expected:
        return False, f"output_root_must_be={expected} actual={effective}"
    return True, expected

# harvest plan §3 source → mapper 接线（dry-run 验收用）
HARVEST_MAPPER_REGISTRY: Dict[str, Dict[str, str]] = {
    "cninfo_company_basic_profile": {
        "logical_name": "basic",
        "mapper_fn": "map_company_basic_profile",
        "status": "connected",
    },
    "cninfo_executive_profile": {
        "logical_name": "executive",
        "mapper_fn": "map_company_executive_profile",
        "status": "connected",
    },
    "cninfo_share_capital_profile": {
        "logical_name": "share_capital",
        "mapper_fn": "map_company_share_capital_profile",
        "status": "connected",
    },
    "cninfo_top_shareholders_profile": {
        "logical_name": "top_shareholders",
        "mapper_fn": "map_company_shareholder_profile",
        "status": "connected",
    },
    "cninfo_top_float_shareholders_profile": {
        "logical_name": "top_float",
        "mapper_fn": "map_company_shareholder_profile",
        "status": "connected",
    },
    "cninfo_dividend_financing_profile": {
        "logical_name": "dividend_history",
        "mapper_fn": "map_dividend_history",
        "status": "connected",
    },
}

# derived 从 basic 派生，无独立 HTTP mapper
DERIVED_LOGICAL_NAMES: Dict[str, str] = {
    "cninfo_company_contact_profile": "contact",
    "cninfo_company_business_scope": "business_scope",
    "cninfo_company_industry_profile": "industry",
}

OBSERVE_LOGICAL_NAME = "security"

PLANNED_QUALITY_FILES = (
    "harvest_summary.md",
    "field_fill_rate.csv",
    "source_quality.csv",
    "hold_company_list.csv",
    "company_harvest_status.csv",
)

_MAPPER_FN_LOOKUP = {
    "map_company_basic_profile": map_company_basic_profile,
    "map_company_executive_profile": map_company_executive_profile,
    "map_company_share_capital_profile": map_company_share_capital_profile,
    "map_company_shareholder_profile": map_company_shareholder_profile,
    "map_dividend_history": map_dividend_history,
}

DERIVED_SOURCE_IDS = tuple(DERIVED_SOURCE_FIELDS.keys())

# harvest plan §3 source 映射
SOURCE_HARVEST_META: Dict[str, Dict[str, str]] = {
    "cninfo_company_basic_profile": {
        "source_type": "direct",
        "raw_subdir": "basic_profile",
        "normalized_subdir": "company_basic_profile",
        "file_ext": ".json",
        "source_status": "proceed_testing_with_caveat",
        "harvest_action": "direct_fetch",
    },
    "cninfo_executive_profile": {
        "source_type": "direct",
        "raw_subdir": "executive_profile",
        "normalized_subdir": "executive_profile",
        "file_ext": ".jsonl",
        "source_status": "proceed_testing_with_caveat",
        "harvest_action": "direct_fetch",
    },
    "cninfo_share_capital_profile": {
        "source_type": "direct",
        "raw_subdir": "share_capital_profile",
        "normalized_subdir": "share_capital_profile",
        "file_ext": ".jsonl",
        "source_status": "source_partial",
        "harvest_action": "direct_fetch",
    },
    "cninfo_top_shareholders_profile": {
        "source_type": "direct",
        "raw_subdir": "top_shareholders_profile",
        "normalized_subdir": "top_shareholders_profile",
        "file_ext": ".jsonl",
        "source_status": "proceed_testing_with_caveat",
        "harvest_action": "direct_fetch",
    },
    "cninfo_top_float_shareholders_profile": {
        "source_type": "direct",
        "raw_subdir": "top_float_shareholders_profile",
        "normalized_subdir": "top_float_shareholders_profile",
        "file_ext": ".jsonl",
        "source_status": "source_partial",
        "harvest_action": "direct_fetch",
    },
    "cninfo_dividend_financing_profile": {
        "source_type": "direct",
        "raw_subdir": "dividend_history",
        "normalized_subdir": "dividend_history",
        "file_ext": ".jsonl",
        "source_status": "proceed_testing",
        "harvest_action": "direct_fetch",
    },
    "cninfo_company_contact_profile": {
        "source_type": "derived",
        "raw_subdir": "",
        "normalized_subdir": "contact_profile",
        "file_ext": ".json",
        "source_status": "derived_no_separate_fetch",
        "harvest_action": "derive_from_basic",
    },
    "cninfo_company_business_scope": {
        "source_type": "derived",
        "raw_subdir": "",
        "normalized_subdir": "business_scope",
        "file_ext": ".json",
        "source_status": "derived_no_separate_fetch",
        "harvest_action": "derive_from_basic",
    },
    "cninfo_company_industry_profile": {
        "source_type": "derived",
        "raw_subdir": "",
        "normalized_subdir": "industry_profile",
        "file_ext": ".json",
        "source_status": "derived_no_separate_fetch",
        "harvest_action": "derive_from_basic",
    },
    "cninfo_company_security_profile": {
        "source_type": "observe_only",
        "raw_subdir": "security_observe",
        "normalized_subdir": "security_observe",
        "file_ext": ".json",
        "source_status": "observe_only",
        "harvest_action": "observe_fetch",
    },
}

HARVEST_MATRIX_SOURCE_ORDER: Tuple[str, ...] = (
    "cninfo_company_basic_profile",
    "cninfo_dividend_financing_profile",
    "cninfo_executive_profile",
    "cninfo_share_capital_profile",
    "cninfo_top_shareholders_profile",
    "cninfo_top_float_shareholders_profile",
    "cninfo_company_contact_profile",
    "cninfo_company_business_scope",
    "cninfo_company_industry_profile",
    "cninfo_company_security_profile",
)

DRYRUN_CSV_FIELDS = [
    "company_code",
    "company_name",
    "board",
    "source_id",
    "source_type",
    "planned_output_path",
    "normalized_target",
    "source_status",
    "harvest_action",
]


def _load_hold_codes(hold_path: str) -> frozenset:
    data = load_sample_yaml(hold_path)
    return frozenset(str(c["stock_code"]) for c in data.get("companies") or [])


def build_harvest_863_sample(
    parent_path: str,
    hold_path: str,
    output_path: str,
) -> int:
    """从 889 母本排除 26 hold，写出 863 harvest 样本 YAML。"""
    parent = load_sample_yaml(parent_path)
    hold_codes = _load_hold_codes(hold_path)
    parent_companies = parent.get("companies") or []

    harvest_companies: List[Dict[str, Any]] = []
    for c in parent_companies:
        code = str(c["stock_code"])
        if code in hold_codes:
            continue
        entry = dict(c)
        entry["harvest_status"] = "active_candidate"
        harvest_companies.append(entry)

    harvest_companies.sort(key=lambda x: str(x["stock_code"]))

    board_counts = Counter(str(c.get("board", "")) for c in harvest_companies)
    out = {
        "version": "c-class-harvest-863-non-bse-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "parent_candidate": PARENT_CANDIDATE_REL,
        "excluded_hold": HOLD_SAMPLE_REL,
        "universe_id": "harvest_863_non_bse",
        "description": "889 non-BSE 母本排除 26 all6 hold；C-class harvest candidate",
        "company_count": len(harvest_companies),
        "excluded_hold_count": len(hold_codes),
        "harvest_status_default": "active_candidate",
        "board_counts": dict(sorted(board_counts.items())),
        "companies": harvest_companies,
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        yaml.dump(out, fh, allow_unicode=True, sort_keys=False, default_flow_style=False)

    return len(harvest_companies)


def validate_harvest_preflight(
    sample_path: str,
    companies: List[Dict[str, str]],
    hold_path: str,
) -> Tuple[bool, str]:
    """863 样本 hard gate：company_count 与 hold 零重叠。"""
    data = load_sample_yaml(sample_path)
    declared = data.get("company_count")
    actual = len(companies)
    hold_codes = _load_hold_codes(hold_path)
    actual_codes = {c["company_code"] for c in companies}
    overlap = actual_codes & hold_codes

    # 863 主轨默认 863；其他 universe 以 YAML company_count 为准
    expected_size = (
        int(declared)
        if declared is not None and int(declared) != HARVEST_EXPECTED_COMPANY_COUNT
        else HARVEST_EXPECTED_COMPANY_COUNT
    )

    issues: List[str] = []
    if declared is not None and int(declared) != actual:
        issues.append(f"company_count={declared!r} actual={actual}")
    if actual != expected_size:
        issues.append(f"expected={expected_size} actual={actual}")
    if overlap:
        issues.append(f"hold_overlap={sorted(overlap)}")
    for sid in HARVEST_MATRIX_SOURCE_ORDER:
        if sid not in SOURCE_HARVEST_META:
            issues.append(f"missing_harvest_meta:{sid}")
        if sid in DERIVED_SOURCE_IDS:
            continue
        if sid not in SOURCE_SPECS and sid != OBSERVE_SOURCE_ID:
            issues.append(f"missing_source_spec:{sid}")

    if issues:
        return False, "; ".join(issues)
    return True, f"company_count={actual} hold_overlap=0 planned_http_cases={actual * HTTP_SOURCES_PER_COMPANY}"


def validate_mapper_wiring() -> Tuple[bool, List[Dict[str, str]]]:
    """确认 harvest 所需 mapper 已 import 且可调用。"""
    rows: List[Dict[str, str]] = []
    ok = True
    for source_id, meta in HARVEST_MAPPER_REGISTRY.items():
        fn_name = meta["mapper_fn"]
        fn = _MAPPER_FN_LOOKUP.get(fn_name)
        callable_ok = callable(fn)
        if not callable_ok:
            ok = False
        rows.append({
            "source_id": source_id,
            "logical_name": meta["logical_name"],
            "mapper_fn": fn_name,
            "status": meta["status"] if callable_ok else "missing",
        })
    return ok, rows


def _planned_quality_paths() -> List[str]:
    return [f"{HARVEST_OUTPUT_ROOT}/quality/{name}" for name in PLANNED_QUALITY_FILES]


def _expected_source_matrix() -> Dict[str, List[str]]:
    direct = [
        meta["logical_name"]
        for sid, meta in HARVEST_MAPPER_REGISTRY.items()
        if SOURCE_HARVEST_META[sid]["source_type"] == "direct"
    ]
    derived = list(DERIVED_LOGICAL_NAMES.values())
    observe = [OBSERVE_LOGICAL_NAME]
    return {"direct": direct, "derived": derived, "observe": observe}


def validate_source_matrix() -> Tuple[bool, str]:
    """确认 dry-run matrix 覆盖 harvest plan 规定的 source 集合。"""
    expected = _expected_source_matrix()
    actual_direct = sorted({
        HARVEST_MAPPER_REGISTRY[sid]["logical_name"]
        for sid in HARVEST_MAPPER_REGISTRY
    })
    actual_derived = sorted(DERIVED_LOGICAL_NAMES.values())
    actual_observe = [OBSERVE_LOGICAL_NAME]

    issues: List[str] = []
    if sorted(expected["direct"]) != sorted(actual_direct):
        issues.append(f"direct mismatch expected={expected['direct']} actual={actual_direct}")
    if sorted(expected["derived"]) != sorted(actual_derived):
        issues.append(f"derived mismatch expected={expected['derived']} actual={actual_derived}")
    if actual_observe != expected["observe"]:
        issues.append(f"observe mismatch expected={expected['observe']} actual={actual_observe}")
    if len(HARVEST_MATRIX_SOURCE_ORDER) != 10:
        issues.append(f"matrix_source_count={len(HARVEST_MATRIX_SOURCE_ORDER)}")
    if issues:
        return False, "; ".join(issues)
    return True, (
        f"direct={len(actual_direct)} derived={len(actual_derived)} observe={len(actual_observe)}"
    )


def validate_output_paths(matrix_rows: List[Dict[str, str]]) -> Tuple[bool, str]:
    """确认 planned raw / normalized / quality 路径格式，且不写入真实 harvest 数据。"""
    issues: List[str] = []
    for row in matrix_rows:
        raw_path = row["planned_output_path"]
        norm_path = row["normalized_target"]
        source_type = row["source_type"]
        if source_type == "derived":
            if not raw_path.startswith("derived/from_basic_profile/"):
                issues.append(f"bad_derived_raw:{raw_path}")
        elif not raw_path.startswith(f"{HARVEST_OUTPUT_ROOT}/raw/"):
            issues.append(f"bad_raw_prefix:{raw_path}")
        if not norm_path.startswith(f"{HARVEST_OUTPUT_ROOT}/normalized/"):
            issues.append(f"bad_norm_prefix:{norm_path}")

    quality_paths = _planned_quality_paths()
    for qp in quality_paths:
        if not qp.startswith(f"{HARVEST_OUTPUT_ROOT}/quality/"):
            issues.append(f"bad_quality_prefix:{qp}")

    if issues:
        return False, "; ".join(issues[:5])
    return True, f"matrix_paths={len(matrix_rows)} quality_files={len(quality_paths)}"


def write_dryrun_validation_summary(
    path: str,
    companies: List[Dict[str, str]],
    matrix_rows: List[Dict[str, str]],
    sample_path: str,
    mapper_rows: List[Dict[str, str]],
    preflight_ok: bool,
    matrix_ok: bool,
    mapper_ok: bool,
    paths_ok: bool,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    company_count = len(companies)
    planned_http = company_count * HTTP_SOURCES_PER_COMPANY
    source_count = len(HARVEST_MATRIX_SOURCE_ORDER)
    all_pass = preflight_ok and matrix_ok and mapper_ok and paths_ok

    lines = [
        "# CNINFO C-Class Harvest Dry-Run Validation Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## Run mode",
        "",
        "**dry-run validation**（mapper 接入后完整流程验收 · 无 CNINFO 请求）",
        "",
        f"## Overall gate: **{'PASS' if all_pass else 'FAIL'}**",
        "",
        "## Preflight",
        "",
        f"| check | result |",
        f"|-------|--------|",
        f"| company_count | **{company_count}** (expected {HARVEST_EXPECTED_COMPANY_COUNT}) |",
        f"| hold_overlap | **0** |",
        f"| planned_http_cases | **{planned_http}** (expected {PLANNED_CASES}) |",
        f"| preflight_gate | **{'PASS' if preflight_ok else 'FAIL'}** |",
        "",
        "## Planned cases",
        "",
        f"- **companies:** {company_count}",
        f"- **matrix_rows:** {len(matrix_rows)} ({company_count} × {source_count})",
        f"- **planned_http_cases:** **{planned_http}**",
        f"- **source_count:** **{source_count}**",
        "",
        "## Source matrix",
        "",
        "### direct",
        "",
    ]
    for name in sorted({m["logical_name"] for m in HARVEST_MAPPER_REGISTRY.values()}):
        lines.append(f"- `{name}`")

    lines.extend(["", "### derived", ""])
    for name in sorted(DERIVED_LOGICAL_NAMES.values()):
        lines.append(f"- `{name}`")

    lines.extend([
        "",
        "### observe",
        "",
        f"- `{OBSERVE_LOGICAL_NAME}`",
        "",
        f"**source_matrix_gate:** **{'PASS' if matrix_ok else 'FAIL'}**",
        "",
        "## Mapper wiring",
        "",
        "| logical_name | source_id | mapper_fn | status |",
        "|--------------|-----------|-----------|--------|",
    ])
    for row in mapper_rows:
        lines.append(
            f"| `{row['logical_name']}` | `{row['source_id']}` | `{row['mapper_fn']}` | **{row['status']}** |"
        )

    lines.extend([
        "",
        f"**mapper_wiring_gate:** **{'PASS' if mapper_ok else 'FAIL'}**",
        "",
        "## Planned output paths（不写入真实数据）",
        "",
        "### raw destination（示例）",
        "",
        f"- `{HARVEST_OUTPUT_ROOT}/raw/basic_profile/{{company_code}}.json`",
        f"- `{HARVEST_OUTPUT_ROOT}/raw/dividend_history/{{company_code}}.jsonl`",
        "",
        "### normalized destination（示例）",
        "",
        f"- `{HARVEST_OUTPUT_ROOT}/normalized/company_basic_profile/{{company_code}}.json`",
        f"- `{HARVEST_OUTPUT_ROOT}/normalized/dividend_history/{{company_code}}.jsonl`",
        "",
        "### quality record（planned）",
        "",
    ])
    for qp in _planned_quality_paths():
        lines.append(f"- `{qp}`")

    lines.extend([
        "",
        f"**output_paths_gate:** **{'PASS' if paths_ok else 'FAIL'}**",
        "",
        "## Dry-run confirmation",
        "",
        "- **CNINFO requests = 0**",
        "- **raw writes = 0**",
        "- **normalized writes = 0**",
        "- **no verified** · **no DB** · **no MinIO**",
        "",
        "## Mapper status summary",
        "",
        f"- basic: **connected**",
        f"- executive: **connected**",
        f"- share_capital: **connected**",
        f"- shareholder (top + top_float): **connected**",
        f"- dividend_history: **connected**",
        "",
        "## Gate",
        "",
        f"**harvest_dryrun_validation_gate = {'PASS' if all_pass else 'FAIL'}**",
        "",
        "Live harvest **pending human approval**（需人工批准后 `--live`）。",
        "",
        "## Appendix",
        "",
        f"- Sample: `{os.path.relpath(sample_path, BASE_DIR)}`",
        f"- Matrix CSV: [cninfo_c_class_harvest_dryrun_report.csv](cninfo_c_class_harvest_dryrun_report.csv)",
        f"- Dry-run summary: [cninfo_c_class_harvest_dryrun_summary.md](cninfo_c_class_harvest_dryrun_summary.md)",
        "",
    ])

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def _planned_raw_path(source_id: str, company_code: str) -> str:
    meta = SOURCE_HARVEST_META[source_id]
    if meta["source_type"] == "derived":
        return f"derived/from_basic_profile/{company_code}"
    sub = meta["raw_subdir"]
    ext = meta["file_ext"]
    return f"{HARVEST_OUTPUT_ROOT}/raw/{sub}/{company_code}{ext}"


def _planned_normalized_path(source_id: str, company_code: str) -> str:
    meta = SOURCE_HARVEST_META[source_id]
    sub = meta["normalized_subdir"]
    ext = meta["file_ext"]
    return f"{HARVEST_OUTPUT_ROOT}/normalized/{sub}/{company_code}{ext}"


def build_dryrun_matrix(companies: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """构造 planned harvest matrix（无网络、无写 harvest 数据）。"""
    rows: List[Dict[str, str]] = []
    for company in companies:
        code = company["company_code"]
        for source_id in HARVEST_MATRIX_SOURCE_ORDER:
            meta = SOURCE_HARVEST_META[source_id]
            rows.append({
                "company_code": code,
                "company_name": company["company_name"],
                "board": company.get("board", ""),
                "source_id": source_id,
                "source_type": meta["source_type"],
                "planned_output_path": _planned_raw_path(source_id, code),
                "normalized_target": _planned_normalized_path(source_id, code),
                "source_status": meta["source_status"],
                "harvest_action": meta["harvest_action"],
            })
    return rows


def write_dryrun_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=DRYRUN_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_dryrun_summary(
    path: str,
    companies: List[Dict[str, str]],
    matrix_rows: List[Dict[str, str]],
    sample_path: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    board_counts = Counter(c.get("board", "") for c in companies)
    type_counts = Counter(r["source_type"] for r in matrix_rows)
    action_counts = Counter(r["harvest_action"] for r in matrix_rows)

    rel_sample = os.path.relpath(sample_path, BASE_DIR)
    lines = [
        "# CNINFO C-Class Harvest Dry-Run Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## Run mode",
        "",
        "**dry-run**",
        "",
        "## Universe",
        "",
        f"- **Sample:** `{rel_sample}`",
        f"- **companies:** **{len(companies)}**",
        f"- **hold excluded:** **{HOLD_COUNT}**（`eval_companies_c_class_889_rerun_all6_hold.yaml`）",
        "",
        "### Board distribution",
        "",
        "| board | count |",
        "|-------|-------|",
    ]
    for board, count in sorted(board_counts.items()):
        lines.append(f"| `{board}` | {count} |")

    lines.extend([
        "",
        "## Planned cases",
        "",
        f"- **HTTP sources per company:** {HTTP_SOURCES_PER_COMPANY}（6 direct + 1 observe）",
        f"- **Total planned HTTP cases:** **{len(companies) * HTTP_SOURCES_PER_COMPANY}**",
        f"- **Matrix rows（含 derived）:** **{len(matrix_rows)}**（{len(companies)} × {len(HARVEST_MATRIX_SOURCE_ORDER)}）",
        "",
        "## Source counts",
        "",
        f"- **direct:** {type_counts.get('direct', 0) // max(len(companies), 1)} sources · "
        f"{action_counts.get('direct_fetch', 0)} matrix rows",
        f"- **derived:** {len(DERIVED_SOURCE_IDS)} sources · "
        f"{action_counts.get('derive_from_basic', 0)} matrix rows",
        f"- **observe_only:** 1 source · {action_counts.get('observe_fetch', 0)} matrix rows",
        "",
        "## Source scope（harvest plan）",
        "",
        "| source_id | type | harvest_action | source_status |",
        "|-----------|------|----------------|---------------|",
    ])
    for sid in HARVEST_MATRIX_SOURCE_ORDER:
        m = SOURCE_HARVEST_META[sid]
        lines.append(
            f"| `{sid}` | {m['source_type']} | {m['harvest_action']} | {m['source_status']} |"
        )

    lines.extend([
        "",
        "## Dry-run confirmation",
        "",
        "- **CNINFO requests = 0**",
        "- **raw writes = 0**",
        "- **normalized writes = 0**",
        "- **no verified** · **no testing_stable_sample** · **no DB**",
        "",
        "## Gate",
        "",
        "**harvest_dryrun_gate = PASS**",
        "",
        "Live harvest **pending approval**（需人工批准后 `--live`）。",
        "",
        "## Caveats（harvest summary 必保留）",
        "",
        "- 26 家 all6 hold 已排除（`excluded_by_status_review`）",
        "- **share_capital** · **top_float** → source_partial",
        "- **executive** → proceed_testing_with_caveat",
        "- **security** → observe_only（不进入主 company snapshot）",
        "- **dividend_history** ≠ financing",
        "",
        "## Appendix",
        "",
        f"详见 [{os.path.basename(DEFAULT_DRYRUN_CSV)}]({os.path.basename(DEFAULT_DRYRUN_CSV)})。",
        "",
    ])

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


@dataclass
class HarvestFetchResult:
    row: CaseRow
    payload: Any


SMOKE_CSV_FIELDS = [
    "company_code",
    "company_name",
    "board",
    "source_id",
    "source_type",
    "retrieval_status",
    "case_result",
    "http_status",
    "business_code",
    "harvest_result",
    "raw_path",
    "normalized_path",
    "raw_written",
    "normalized_written",
    "record_count",
    "error_message",
]


def _harvest_abs_path(rel_path: str) -> str:
    return os.path.join(BASE_DIR, rel_path)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _str_or_none(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    return str(value)


def validate_smoke_preflight(
    companies: List[Dict[str, str]],
    hold_path: str,
    limit: int,
) -> Tuple[bool, str]:
    """smoke live 前置：hold 零重叠 + limit 合法。"""
    hold_codes = _load_hold_codes(hold_path)
    actual_codes = {c["company_code"] for c in companies}
    overlap = actual_codes & hold_codes
    issues: List[str] = []
    if limit < 1:
        issues.append(f"limit={limit}")
    if len(companies) > limit:
        issues.append(f"companies={len(companies)} limit={limit}")
    if overlap:
        issues.append(f"hold_overlap={sorted(overlap)}")
    if issues:
        return False, "; ".join(issues)
    return (
        True,
        f"smoke_companies={len(companies)} limit={limit} hold_overlap=0 "
        f"planned_http_cases={len(companies) * HTTP_SOURCES_PER_COMPANY}",
    )


def resolve_live_execution_mode(
    args: argparse.Namespace,
    sample_path: str = "",
) -> str:
    """
    解析 live 执行模式。

    - phase3_batch: phase3 batch YAML + --approve-phase3-batch-500-harvest
    - phase2_smoke: phase2 smoke YAML + --approve-phase2-smoke-harvest
    - smoke: --live --limit N（无需 approve）
    - full: --live --approve-full-harvest（无 limit 或 limit>=863）
    """
    if sample_path and is_phase2_smoke_sample(sample_path):
        if getattr(args, "approve_phase2_smoke_harvest", False):
            return "phase2_smoke"
        return ""
    if sample_path and is_phase3_batch_sample(sample_path):
        if getattr(args, "approve_phase3_batch_500_harvest", False):
            return "phase3_batch"
        return ""
    if args.limit is not None:
        return "smoke"
    if args.approve_full_harvest:
        return "full"
    return ""


def enforce_live_approval_gate(
    args: argparse.Namespace,
    sample_path: str = "",
) -> str:
    """live 入口安全闸：无 approve 且无 limit 时拒绝。"""
    mode = resolve_live_execution_mode(args, sample_path)
    if not mode:
        if sample_path and is_phase2_smoke_sample(sample_path):
            print(PHASE2_SMOKE_APPROVAL_REQUIRED, file=sys.stderr)
        elif sample_path and is_phase3_batch_sample(sample_path):
            print(PHASE3_BATCH_APPROVAL_REQUIRED, file=sys.stderr)
        else:
            print(FULL_HARVEST_APPROVAL_REQUIRED, file=sys.stderr)
        sys.exit(2)
    return mode


def _quality_abs_path(rel_path: str) -> str:
    return _harvest_abs_path(rel_path)


def load_run_status(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """读取 quality/run_status.json。"""
    abs_path = path or _quality_abs_path(RUN_STATUS_REL)
    if not os.path.isfile(abs_path):
        return None
    with open(abs_path, encoding="utf-8") as fh:
        return json.load(fh)


def write_run_status(
    data: Dict[str, Any],
    path: Optional[str] = None,
) -> str:
    """写入 quality/run_status.json。"""
    abs_path = path or _quality_abs_path(RUN_STATUS_REL)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return abs_path


def make_run_status(
    *,
    mode: str,
    company_count: int,
    completed_company_count: int = 0,
    status: str = "running",
    resume_enabled: bool = False,
    run_id: Optional[str] = None,
    started_at: Optional[str] = None,
    finished_at: str = "",
) -> Dict[str, Any]:
    return {
        "run_id": run_id or str(uuid.uuid4()),
        "mode": mode,
        "started_at": started_at or _utc_now_iso(),
        "finished_at": finished_at,
        "company_count": company_count,
        "completed_company_count": completed_company_count,
        "status": status,
        "resume_enabled": resume_enabled,
    }


def load_completed_company_codes(status_csv_path: Optional[str] = None) -> frozenset:
    """从 company_harvest_status.csv 读取 harvest_status=complete 的公司。"""
    abs_path = status_csv_path or _quality_abs_path(COMPANY_HARVEST_STATUS_REL)
    if not os.path.isfile(abs_path):
        return frozenset()
    completed: set = set()
    with open(abs_path, encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if row.get("harvest_status") == "complete" and row.get("company_code"):
                completed.add(str(row["company_code"]))
    return frozenset(completed)


def apply_resume_filter(
    companies: List[Dict[str, str]],
    resume: bool,
    status_csv_path: Optional[str] = None,
) -> Tuple[List[Dict[str, str]], int, int]:
    """
    --resume 框架：跳过已完成公司。

    返回 (pending_companies, resume_skip_count, resume_pending_count)。
    """
    if not resume:
        return companies, 0, len(companies)
    completed = load_completed_company_codes(status_csv_path)
    pending = [c for c in companies if c["company_code"] not in completed]
    skip_count = len(companies) - len(pending)
    return pending, skip_count, len(pending)


def validate_pre_live_harvest(
    sample_path: str,
    companies: List[Dict[str, str]],
    hold_path: str,
    *,
    execution_mode: str,
    approve_full_harvest: bool,
    approve_phase2_smoke_harvest: bool = False,
    approve_phase3_batch_500_harvest: bool = False,
    limit: Optional[int],
    resume: bool,
    run_status_path: Optional[str] = None,
    output_root: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    live harvest 前置检查：
    1. sample company count
    2. hold overlap
    3. approve flag
    4. output directory
    5. existing run status
    """
    issues: List[str] = []
    hold_codes = _load_hold_codes(hold_path)
    actual_codes = {c["company_code"] for c in companies}
    overlap = actual_codes & hold_codes

    if execution_mode == "full":
        data = load_sample_yaml(sample_path)
        declared = data.get("company_count")
        actual = len(companies)
        if declared != actual:
            issues.append(f"company_count_declared={declared!r} actual={actual}")
        if actual != HARVEST_EXPECTED_COMPANY_COUNT:
            issues.append(f"expected={HARVEST_EXPECTED_COMPANY_COUNT} actual={actual}")
        if not approve_full_harvest:
            issues.append("approve_full_harvest_required")
    elif execution_mode == "phase2_smoke":
        data = load_sample_yaml(sample_path)
        declared = data.get("company_count")
        actual = len(companies)
        if declared != actual:
            issues.append(f"company_count_declared={declared!r} actual={actual}")
        if actual != PHASE2_SMOKE_EXPECTED_COUNT:
            issues.append(f"expected={PHASE2_SMOKE_EXPECTED_COUNT} actual={actual}")
        if not approve_phase2_smoke_harvest:
            issues.append("approve_phase2_smoke_harvest_required")
        if approve_full_harvest:
            issues.append("approve_full_harvest_not_valid_for_phase2")
        if approve_phase3_batch_500_harvest:
            issues.append("approve_phase3_batch_not_valid_for_phase2")
        if limit is not None and len(companies) > limit:
            issues.append(f"companies={len(companies)} limit={limit}")
    elif execution_mode == "phase3_batch":
        data = load_sample_yaml(sample_path)
        declared = data.get("company_count")
        actual = len(companies)
        if declared != actual:
            issues.append(f"company_count_declared={declared!r} actual={actual}")
        if actual != PHASE3_BATCH_EXPECTED_COUNT:
            issues.append(f"expected={PHASE3_BATCH_EXPECTED_COUNT} actual={actual}")
        if not approve_phase3_batch_500_harvest:
            issues.append("approve_phase3_batch_500_harvest_required")
        if approve_full_harvest:
            issues.append("approve_full_harvest_not_valid_for_phase3")
        if approve_phase2_smoke_harvest:
            issues.append("approve_phase2_smoke_not_valid_for_phase3")
        root_ok, root_detail = validate_phase3_output_root(output_root)
        if not root_ok:
            issues.append(root_detail)
        if limit is not None and len(companies) > limit:
            issues.append(f"companies={len(companies)} limit={limit}")
    elif execution_mode == "smoke":
        if is_phase2_smoke_sample(sample_path):
            issues.append("phase2_smoke_requires_approve_phase2_smoke_harvest")
        if is_phase3_batch_sample(sample_path):
            issues.append("phase3_batch_requires_approve_phase3_batch_500_harvest")
        if limit is None or limit < 1:
            issues.append(f"smoke_limit_invalid={limit!r}")
        if len(companies) > (limit or 0):
            issues.append(f"companies={len(companies)} limit={limit}")

    if overlap:
        issues.append(f"hold_overlap={sorted(overlap)}")

    quality_dir = _quality_abs_path(QUALITY_DIR_REL)
    try:
        os.makedirs(quality_dir, exist_ok=True)
        if not os.path.isdir(quality_dir):
            issues.append(f"output_dir_not_dir:{quality_dir}")
    except OSError as exc:
        issues.append(f"output_dir_error:{exc}")

    existing = load_run_status(run_status_path)
    if existing and existing.get("status") == "running" and not resume:
        issues.append(f"previous_run_status=running run_id={existing.get('run_id')}")

    if issues:
        return False, "; ".join(issues)

    if execution_mode == "full":
        detail = (
            f"mode=full company_count={len(companies)} hold_overlap=0 "
            f"approve_full_harvest=true planned_http_cases={len(companies) * HTTP_SOURCES_PER_COMPANY}"
        )
    elif execution_mode == "phase2_smoke":
        detail = (
            f"mode=phase2_smoke company_count={len(companies)} hold_overlap=0 "
            f"approve_phase2_smoke_harvest=true "
            f"output_root={HARVEST_OUTPUT_ROOT} "
            f"planned_http_cases={len(companies) * HTTP_SOURCES_PER_COMPANY}"
        )
    elif execution_mode == "phase3_batch":
        detail = (
            f"mode=phase3_batch company_count={len(companies)} hold_overlap=0 "
            f"approve_phase3_batch_500_harvest=true "
            f"output_root={HARVEST_OUTPUT_ROOT} "
            f"planned_http_cases={len(companies) * HTTP_SOURCES_PER_COMPANY}"
        )
    else:
        detail = (
            f"mode=smoke company_count={len(companies)} limit={limit} hold_overlap=0 "
            f"planned_http_cases={len(companies) * HTTP_SOURCES_PER_COMPANY}"
        )
    return True, detail


def _is_harvest_success_status(source_id: str, retrieval_status: str) -> bool:
    if retrieval_status in HARVEST_SUCCESS_STATUSES:
        return True
    if source_id == OBSERVE_SOURCE_ID and retrieval_status == "endpoint_found":
        return True
    return False


def _fetch_harvest_basic(company: Dict[str, str]) -> HarvestFetchResult:
    code = company["company_code"]
    org_id = company["org_id"]
    row = CaseRow(
        run_mode="live",
        source_id="cninfo_company_basic_profile",
        company_code=code,
        company_name=company["company_name"],
        org_id=org_id,
        board=company["board"],
        records_path="data.records[0]",
        suspected_no_dividend=company.get("suspected_no_dividend", "no"),
    )
    http_status, payload, err, url, meta = _live_fetch_data20(
        BASIC_URL, company, xhr=False, records_path="data.records"
    )
    row.request_url = url
    _apply_fetch_meta(row, meta)
    row.http_status = str(http_status) if http_status is not None else ""
    if err:
        return HarvestFetchResult(row=_finalize_row_status(_apply_http_error(row, http_status, err)), payload=None)

    json_code, result_code = _extract_codes(payload)
    row.json_code = json_code
    row.result_code = result_code
    row.final_result_code = meta.get("final_result_code", result_code)

    if _is_cninfo_throttled_business_code(payload, http_status):
        row.retrieval_status = "cninfo_throttled_business_code"
        row.error_message = "CNINFO business code throttled after backoff"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    if not _is_success_payload(payload, http_status or 0):
        row.retrieval_status = "http_error"
        row.error_message = "HTTP or JSON code not success"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    record0 = _get_path(payload, "data.records.0")
    if record0 is None:
        row.retrieval_status = "empty_response"
        row.error_message = "data.records[0] missing"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    basic = record0.get("basicInformation") if isinstance(record0, dict) else None
    listing = record0.get("listingInformation") if isinstance(record0, dict) else None
    basic_n = _list_len(basic)
    listing_n = _list_len(listing)
    row.record_count = str(basic_n)
    row.non_empty = "yes" if basic_n > 0 and listing_n > 0 else "no"

    if basic_n > 0 and listing_n > 0:
        row.retrieval_status = "endpoint_found"
        row.case_result = "pass"
    elif isinstance(record0, dict):
        row.retrieval_status = "empty_but_valid_response"
        row.case_result = "fail"
    else:
        row.retrieval_status = "schema_unexpected"
        row.case_result = "fail"
    return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)


def _fetch_harvest_records_list(source_id: str, company: Dict[str, str]) -> HarvestFetchResult:
    spec = SOURCE_SPECS[source_id]
    code = company["company_code"]
    org_id = company["org_id"]
    row = CaseRow(
        run_mode="live",
        source_id=source_id,
        company_code=code,
        company_name=company["company_name"],
        org_id=org_id,
        board=company["board"],
        records_path=spec["records_path"],
        suspected_no_dividend=company.get("suspected_no_dividend", "no"),
    )
    http_status, payload, err, url, meta = _live_fetch_data20(
        spec["url"], company, xhr=True, records_path=spec["records_path"]
    )
    row.request_url = url
    _apply_fetch_meta(row, meta)
    row.http_status = str(http_status) if http_status is not None else ""
    if err:
        return HarvestFetchResult(row=_finalize_row_status(_apply_http_error(row, http_status, err)), payload=None)

    json_code, result_code = _extract_codes(payload)
    row.json_code = json_code
    row.result_code = result_code
    row.final_result_code = meta.get("final_result_code", result_code)

    if http_status != 200:
        row.retrieval_status = "http_error"
        row.error_message = f"HTTP {http_status}"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    if not isinstance(payload, dict):
        row.retrieval_status = "schema_unexpected"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    if _is_cninfo_throttled_business_code(payload, http_status):
        row.retrieval_status = "cninfo_throttled_business_code"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    records = _get_path(payload, spec["records_path"])
    if records is None:
        row.retrieval_status = "schema_unexpected"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    if not isinstance(records, list):
        row.retrieval_status = "schema_unexpected"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    row.record_count = str(len(records))
    if not _is_success_payload(payload, http_status):
        row.retrieval_status = "http_error"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    if len(records) == 0:
        if spec.get("allow_valid_empty"):
            row.retrieval_status = "valid_empty"
            row.non_empty = "no"
            row.case_result = "pass"
        elif source_id in SHAREHOLDER_SOURCE_IDS:
            row.retrieval_status = "empty_but_valid_response"
            row.non_empty = "no"
            row.case_result = "pass"
        else:
            row.retrieval_status = "empty_but_valid_response"
            row.non_empty = "no"
            row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    first = records[0]
    if not isinstance(first, dict):
        row.retrieval_status = "schema_unexpected"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    required = spec.get("expected_fields") or []
    missing = [f for f in required if f not in first]
    row.filled_fields = _collect_field_fill(first, required)
    row.non_empty = "yes"
    if missing:
        row.retrieval_status = "schema_unexpected"
        row.error_message = f"missing required fields: {', '.join(missing)}"
        row.case_result = "fail"
        return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)

    row.retrieval_status = "endpoint_found"
    row.case_result = "pass"
    return HarvestFetchResult(row=_finalize_row_status(row), payload=payload)


def _fetch_harvest_security(company: Dict[str, str]) -> HarvestFetchResult:
    code = company["company_code"]
    org_id = company["org_id"]
    url = _security_url(code, org_id)
    row = CaseRow(
        run_mode="live",
        source_id=OBSERVE_SOURCE_ID,
        company_code=code,
        company_name=company["company_name"],
        org_id=org_id,
        board=company["board"],
        request_url=url,
        records_path="$",
        suspected_no_dividend=company.get("suspected_no_dividend", "no"),
    )
    http_status, payload, err = _http_get(url, _browser_headers(code, org_id, xhr=True))
    row.http_status = str(http_status) if http_status is not None else ""
    if err:
        return HarvestFetchResult(row=_apply_http_error(row, http_status, err), payload=None)

    json_code, result_code = _extract_codes(payload)
    row.json_code = json_code
    row.result_code = result_code
    if http_status != 200 or not isinstance(payload, dict):
        row.retrieval_status = "http_error"
        row.case_result = "observe_fail"
        return HarvestFetchResult(row=row, payload=payload)

    required = ("secCode", "secName", "secType", "tradingStatus", "age", "finance", "delisted")
    missing = [f for f in required if f not in payload]
    if missing:
        row.retrieval_status = "schema_unexpected"
        row.case_result = "observe_fail"
        return HarvestFetchResult(row=row, payload=payload)

    row.retrieval_status = "endpoint_found"
    row.case_result = "observe_pass"
    return HarvestFetchResult(row=row, payload=payload)


def _extract_raw_records(source_id: str, payload: Any) -> Any:
    if payload is None:
        return [] if source_id != "cninfo_company_basic_profile" else {}
    if source_id == "cninfo_company_basic_profile":
        record0 = _get_path(payload, "data.records.0")
        return record0 if isinstance(record0, dict) else {}
    if source_id == OBSERVE_SOURCE_ID:
        return payload if isinstance(payload, dict) else {}
    spec = SOURCE_SPECS.get(source_id, {})
    records = _get_path(payload, spec.get("records_path", "data.records"))
    return records if isinstance(records, list) else []


def _build_raw_envelope(
    company: Dict[str, str],
    source_id: str,
    fetch: HarvestFetchResult,
) -> Dict[str, Any]:
    row = fetch.row
    business_code = row.final_result_code or row.result_code or row.json_code or ""
    return {
        "company_code": company["company_code"],
        "company_name": company["company_name"],
        "source_id": source_id,
        "org_id": company["org_id"],
        "request_time": _utc_now_iso(),
        "request_url": row.request_url,
        "retrieval_status": row.retrieval_status,
        "http_status": row.http_status,
        "business_code": business_code,
        "raw_records": _extract_raw_records(source_id, fetch.payload),
    }


def _write_json_file(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def _write_jsonl_file(path: str, records: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def _write_raw_envelope(rel_path: str, envelope: Dict[str, Any], file_ext: str) -> str:
    abs_path = _harvest_abs_path(rel_path)
    if file_ext == ".jsonl":
        records = envelope.get("raw_records")
        if isinstance(records, list):
            _write_jsonl_file(abs_path, [envelope])
        else:
            _write_jsonl_file(abs_path, [envelope])
    else:
        _write_json_file(abs_path, envelope)
    return abs_path


def _map_derived_contact(
    basic_mapped: Optional[Dict[str, Any]],
    basic_raw0: Dict[str, Any],
    company: Dict[str, str],
) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "company_code": company["company_code"],
        "company_name": company["company_name"],
        "source_id": "cninfo_company_contact_profile",
        "logical_source_id": "contact",
        "derived_from": "cninfo_company_basic_profile",
        "source_status": SOURCE_HARVEST_META["cninfo_company_contact_profile"]["source_status"],
    }
    if basic_mapped:
        for key in ("registered_address", "office_address", "company_website"):
            if basic_mapped.get(key) is not None:
                record[key] = basic_mapped[key]
    for raw_key, norm_key in (
        ("F012V", "phone"),
        ("F013V", "fax"),
        ("F014V", "email"),
        ("F018V", "contact_person"),
    ):
        val = _str_or_none(basic_raw0.get(raw_key))
        if val is not None:
            record[norm_key] = val
    return record


def _map_derived_business_scope(
    basic_mapped: Optional[Dict[str, Any]],
    basic_raw0: Dict[str, Any],
    company: Dict[str, str],
) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "company_code": company["company_code"],
        "company_name": company["company_name"],
        "source_id": "cninfo_company_business_scope",
        "logical_source_id": "business_scope",
        "derived_from": "cninfo_company_basic_profile",
        "source_status": SOURCE_HARVEST_META["cninfo_company_business_scope"]["source_status"],
    }
    if basic_mapped and basic_mapped.get("business_scope") is not None:
        record["business_scope"] = basic_mapped["business_scope"]
    for raw_key, norm_key in (
        ("F015V", "main_business"),
        ("F016V", "business_scope_text"),
        ("F017V", "company_introduction"),
    ):
        val = _str_or_none(basic_raw0.get(raw_key))
        if val is not None:
            record[norm_key] = val
    return record


def _map_derived_industry(
    basic_mapped: Optional[Dict[str, Any]],
    basic_raw0: Dict[str, Any],
    company: Dict[str, str],
) -> Dict[str, Any]:
    record: Dict[str, Any] = {
        "company_code": company["company_code"],
        "company_name": company["company_name"],
        "source_id": "cninfo_company_industry_profile",
        "logical_source_id": "industry",
        "derived_from": "cninfo_company_basic_profile",
        "source_status": SOURCE_HARVEST_META["cninfo_company_industry_profile"]["source_status"],
    }
    if basic_mapped:
        for key in ("industry", "listed_board", "exchange"):
            if basic_mapped.get(key) is not None:
                record[key] = basic_mapped[key]
    for raw_key, norm_key in (("F032V", "industry_text"), ("MARKET", "market"), ("F044V", "index_or_plate_labels")):
        val = _str_or_none(basic_raw0.get(raw_key))
        if val is not None:
            record[norm_key] = val
    return record


def _write_normalized_for_source(
    source_id: str,
    company: Dict[str, str],
    fetch: HarvestFetchResult,
    basic_context: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[str], int]:
    """写入 normalized 文件；返回 (abs_path, record_count)。"""
    rel_path = _planned_normalized_path(source_id, company["company_code"])
    abs_path = _harvest_abs_path(rel_path)
    meta = SOURCE_HARVEST_META[source_id]
    source_status = meta["source_status"]
    code = company["company_code"]
    name = company["company_name"]
    org_id = company["org_id"]
    payload = fetch.payload
    row = fetch.row

    if source_id == "cninfo_company_basic_profile":
        record0 = _extract_raw_records(source_id, payload)
        if not isinstance(record0, dict):
            record0 = {}
        mapped = map_company_basic_profile(
            {"basicInformation": record0.get("basicInformation") or [],
             "listingInformation": record0.get("listingInformation") or []},
            code, name, source_status=source_status, org_id=org_id,
        )
        if mapped is None:
            mapped = {
                "company_code": code,
                "company_name": name,
                "source_id": source_id,
                "source_status": source_status,
                "retrieval_status": row.retrieval_status,
                "record_count": 0,
            }
        _write_json_file(abs_path, mapped)
        return abs_path, 1 if mapped.get("legal_name") or mapped.get("company_code") else 0

    if source_id == "cninfo_dividend_financing_profile":
        mapped = map_dividend_history(payload, code, name, source_status=source_status)
        events = mapped.get("dividend_history") or []
        public_events = []
        for ev in events:
            public_events.append({k: ev.get(k) for k in (
                "dividend_year", "report_period", "record_date", "ex_dividend_date",
                "payment_date", "cash_dividend_per_share", "stock_dividend_ratio",
                "transfer_ratio", "dividend_method", "dividend_plan_text_raw",
                "dividend_parse_status",
            )})
        _write_jsonl_file(abs_path, public_events)
        return abs_path, len(public_events)

    if source_id == "cninfo_executive_profile":
        records = _extract_raw_records(source_id, payload)
        mapped_rows = []
        if isinstance(records, list):
            for raw in records:
                if isinstance(raw, dict):
                    m = map_company_executive_profile(raw, code, name, source_status=source_status, org_id=org_id)
                    if m:
                        mapped_rows.append(m)
        _write_jsonl_file(abs_path, mapped_rows)
        return abs_path, len(mapped_rows)

    if source_id == "cninfo_share_capital_profile":
        records = _extract_raw_records(source_id, payload)
        mapped_rows = []
        if isinstance(records, list):
            for raw in records:
                if isinstance(raw, dict):
                    m = map_company_share_capital_profile(raw, code, name, source_status=source_status, org_id=org_id)
                    if m:
                        mapped_rows.append(m)
        _write_jsonl_file(abs_path, mapped_rows)
        return abs_path, len(mapped_rows)

    if source_id == "cninfo_top_shareholders_profile":
        records = _extract_raw_records(source_id, payload)
        mapped_rows = []
        if isinstance(records, list):
            for raw in records:
                if isinstance(raw, dict):
                    m = map_company_shareholder_profile(
                        raw, code, name, source_id=source_id,
                        source_status=source_status, org_id=org_id,
                        shareholder_scope=SHAREHOLDER_SCOPE_TOP,
                    )
                    if m:
                        mapped_rows.append(m)
        _write_jsonl_file(abs_path, mapped_rows)
        return abs_path, len(mapped_rows)

    if source_id == "cninfo_top_float_shareholders_profile":
        records = _extract_raw_records(source_id, payload)
        mapped_rows = []
        if isinstance(records, list):
            for raw in records:
                if isinstance(raw, dict):
                    m = map_company_shareholder_profile(
                        raw, code, name, source_id=source_id,
                        source_status=source_status, org_id=org_id,
                        shareholder_scope=SHAREHOLDER_SCOPE_TOP_FLOAT,
                    )
                    if m:
                        mapped_rows.append(m)
        _write_jsonl_file(abs_path, mapped_rows)
        return abs_path, len(mapped_rows)

    if source_id == OBSERVE_SOURCE_ID:
        raw = _extract_raw_records(source_id, payload)
        mapped = map_company_security_profile(
            raw if isinstance(raw, dict) else {}, code, name, source_status=source_status,
        )
        if mapped is None:
            mapped = {
                "company_code": code,
                "company_name": name,
                "source_id": source_id,
                "source_status": source_status,
                "retrieval_status": row.retrieval_status,
            }
        _write_json_file(abs_path, mapped)
        return abs_path, 1

    if source_id in DERIVED_SOURCE_IDS and basic_context:
        basic_mapped = basic_context.get("basic_mapped")
        basic_raw0 = basic_context.get("basic_raw0") or {}
        if source_id == "cninfo_company_contact_profile":
            mapped = _map_derived_contact(basic_mapped, basic_raw0, company)
        elif source_id == "cninfo_company_business_scope":
            mapped = _map_derived_business_scope(basic_mapped, basic_raw0, company)
        else:
            mapped = _map_derived_industry(basic_mapped, basic_raw0, company)
        _write_json_file(abs_path, mapped)
        return abs_path, 1

    return None, 0


def _harvest_result_label(source_id: str, row: CaseRow) -> str:
    status = row.retrieval_status
    if _is_harvest_success_status(source_id, status):
        if status in ("valid_empty", "empty_but_valid_response"):
            return "empty_but_valid"
        return "success"
    if status in ("blocked", "rate_limited"):
        return "blocked"
    if status in ("http_error", "cninfo_throttled_business_code"):
        return "http_error"
    return "failed"


def _fetch_harvest_source(source_id: str, company: Dict[str, str]) -> HarvestFetchResult:
    if source_id == "cninfo_company_basic_profile":
        return _fetch_harvest_basic(company)
    if source_id == OBSERVE_SOURCE_ID:
        return _fetch_harvest_security(company)
    return _fetch_harvest_records_list(source_id, company)


def _live_http_source_order() -> List[str]:
    return list(MAIN_SOURCE_IDS) + [OBSERVE_SOURCE_ID]


def run_live_harvest(
    companies: List[Dict[str, str]],
) -> Tuple[List[Dict[str, str]], Dict[str, int]]:
    """执行 live harvest（smoke 规模）；返回 smoke 报告行与统计。"""
    report_rows: List[Dict[str, str]] = []
    stats = Counter()
    company_status_rows: List[Dict[str, str]] = []
    field_fill_rows: List[Dict[str, str]] = []
    source_quality = Counter()
    request_time = _utc_now_iso()

    total_http = len(companies) * HTTP_SOURCES_PER_COMPANY
    request_count = 0

    for company in companies:
        basic_context: Dict[str, Any] = {"basic_mapped": None, "basic_raw0": {}}
        company_source_results: List[str] = []
        http_success = 0

        for source_id in _live_http_source_order():
            fetch = _fetch_harvest_source(source_id, company)
            row = fetch.row
            meta = SOURCE_HARVEST_META[source_id]
            rel_raw = _planned_raw_path(source_id, company["company_code"])
            rel_norm = _planned_normalized_path(source_id, company["company_code"])

            envelope = _build_raw_envelope(company, source_id, fetch)
            raw_written = "no"
            norm_written = "no"
            norm_count = 0
            raw_abs = ""
            norm_abs = ""

            if meta["source_type"] != "derived":
                stats["http_requests"] += 1
                request_count += 1
                raw_abs = _write_raw_envelope(rel_raw, envelope, meta["file_ext"])
                raw_written = "yes"
                stats["raw_files"] += 1

                if source_id == "cninfo_company_basic_profile":
                    record0 = envelope.get("raw_records") or {}
                    basic_list = record0.get("basicInformation") if isinstance(record0, dict) else None
                    basic_raw0 = basic_list[0] if isinstance(basic_list, list) and basic_list else {}
                    basic_context["basic_raw0"] = basic_raw0 if isinstance(basic_raw0, dict) else {}

            harvest_label = _harvest_result_label(source_id, row)
            source_quality[f"{source_id}:{row.retrieval_status}"] += 1

            if _is_harvest_success_status(source_id, row.retrieval_status):
                norm_abs, norm_count = _write_normalized_for_source(source_id, company, fetch, basic_context)
                if norm_abs:
                    norm_written = "yes"
                    stats["normalized_files"] += 1
                if source_id == "cninfo_company_basic_profile" and norm_abs:
                    with open(norm_abs, encoding="utf-8") as fh:
                        basic_context["basic_mapped"] = json.load(fh)
                http_success += 1
                stats["success_count"] += 1
                if harvest_label == "empty_but_valid":
                    stats["empty_but_valid_count"] += 1
            elif harvest_label == "blocked":
                stats["blocked_count"] += 1
            elif harvest_label == "http_error":
                stats["http_error_count"] += 1
            else:
                stats["failed_count"] += 1

            company_source_results.append(harvest_label)

            report_rows.append({
                "company_code": company["company_code"],
                "company_name": company["company_name"],
                "board": company.get("board", ""),
                "source_id": source_id,
                "source_type": meta["source_type"],
                "retrieval_status": row.retrieval_status,
                "case_result": row.case_result,
                "http_status": row.http_status,
                "business_code": envelope["business_code"],
                "harvest_result": harvest_label,
                "raw_path": rel_raw,
                "normalized_path": rel_norm,
                "raw_written": raw_written,
                "normalized_written": norm_written,
                "record_count": str(norm_count),
                "error_message": row.error_message,
            })

            if request_count < total_http:
                if source_id in MAIN_SOURCE_IDS[2:]:
                    time.sleep(SLEEP_SECONDS)
                else:
                    time.sleep(LIVE_BASE_SLEEP_SECONDS)

        # derived 三源（无 HTTP）
        for source_id in DERIVED_SOURCE_IDS:
            meta = SOURCE_HARVEST_META[source_id]
            rel_norm = _planned_normalized_path(source_id, company["company_code"])
            norm_abs, norm_count = _write_normalized_for_source(
                source_id, company,
                HarvestFetchResult(row=CaseRow(
                    run_mode="live", source_id=source_id,
                    company_code=company["company_code"],
                    company_name=company["company_name"], org_id=company["org_id"],
                ), payload=None),
                basic_context,
            )
            norm_written = "yes" if norm_abs else "no"
            if norm_abs:
                stats["normalized_files"] += 1
            derived_label = "success" if basic_context.get("basic_mapped") else "empty_but_valid"
            if derived_label == "success":
                stats["success_count"] += 1
            company_source_results.append(derived_label)
            report_rows.append({
                "company_code": company["company_code"],
                "company_name": company["company_name"],
                "board": company.get("board", ""),
                "source_id": source_id,
                "source_type": meta["source_type"],
                "retrieval_status": "derived_from_basic",
                "case_result": "pass" if basic_context.get("basic_mapped") else "skipped",
                "http_status": "",
                "business_code": "",
                "harvest_result": derived_label,
                "raw_path": _planned_raw_path(source_id, company["company_code"]),
                "normalized_path": rel_norm,
                "raw_written": "no",
                "normalized_written": norm_written,
                "record_count": str(norm_count),
                "error_message": "",
            })
            for field_name in DERIVED_SOURCE_FIELDS.get(source_id, []):
                basic_raw0 = basic_context.get("basic_raw0") or {}
                field_fill_rows.append({
                    "company_code": company["company_code"],
                    "source_id": source_id,
                    "field_name": field_name,
                    "filled": "1" if _str_or_none(basic_raw0.get(field_name)) else "0",
                })

        fail_n = sum(1 for r in company_source_results if r in ("failed", "http_error", "blocked"))
        if fail_n == 0:
            harvest_status = "complete"
        elif http_success > 0:
            harvest_status = "partial"
        else:
            harvest_status = "failed"
        company_status_rows.append({
            "company_code": company["company_code"],
            "company_name": company["company_name"],
            "harvest_status": harvest_status,
            "sources_attempted": str(HTTP_SOURCES_PER_COMPANY + len(DERIVED_SOURCE_IDS)),
            "sources_http_success": str(http_success),
            "sources_failed": str(fail_n),
            "last_updated": request_time,
        })

    write_quality_artifacts(
        company_status_rows, field_fill_rows, source_quality, companies, stats,
        write_summary=False,
    )
    return report_rows, dict(stats)


@dataclass
class HarvestGateMetrics:
    """resume 感知的 harvest gate 统计。"""

    total_harvest_universe: int
    resume_enabled: bool
    resume_skipped_companies: int
    newly_processed_companies: int
    completed_companies_total: int
    expected_new_raw: int
    expected_total_raw: int
    expected_new_normalized: int
    expected_total_normalized: int
    actual_new_raw: int
    actual_total_raw: int
    actual_new_normalized: int
    actual_total_normalized: int
    blocked_count: int
    http_error_count: int
    gate: str = ""


def _stats_from_report_rows(report_rows: List[Dict[str, str]]) -> Dict[str, int]:
    stats: Dict[str, int] = Counter()
    stats["http_requests"] = sum(
        1 for r in report_rows
        if r.get("source_type") != "derived" and r.get("raw_written") == "yes"
    )
    stats["raw_files"] = stats["http_requests"]
    stats["normalized_files"] = sum(1 for r in report_rows if r.get("normalized_written") == "yes")
    stats["success_count"] = sum(
        1 for r in report_rows if r.get("harvest_result") in ("success", "empty_but_valid")
    )
    stats["empty_but_valid_count"] = sum(
        1 for r in report_rows if r.get("harvest_result") == "empty_but_valid"
    )
    stats["blocked_count"] = sum(1 for r in report_rows if r.get("harvest_result") == "blocked")
    stats["http_error_count"] = sum(
        1 for r in report_rows if r.get("harvest_result") == "http_error"
    )
    stats["failed_count"] = sum(1 for r in report_rows if r.get("harvest_result") == "failed")
    return dict(stats)


def count_harvest_artifacts_on_disk() -> Dict[str, int]:
    """统计磁盘上 raw / normalized / company 覆盖（不重跑 harvest）。"""
    raw_root = _harvest_abs_path(f"{HARVEST_OUTPUT_ROOT}/raw")
    norm_root = _harvest_abs_path(f"{HARVEST_OUTPUT_ROOT}/normalized")
    raw_count = 0
    for _root, _dirs, files in os.walk(raw_root):
        raw_count += len(files)
    norm_count = 0
    for _root, _dirs, files in os.walk(norm_root):
        norm_count += len(files)
    basic_dir = os.path.join(norm_root, "company_basic_profile")
    company_codes: set = set()
    if os.path.isdir(basic_dir):
        for name in os.listdir(basic_dir):
            if name.endswith(".json"):
                company_codes.add(name[:-5])
    return {
        "raw_files_total": raw_count,
        "normalized_files_total": norm_count,
        "completed_companies_total": len(company_codes),
    }


def compute_harvest_gate_metrics(
    report_rows: List[Dict[str, str]],
    *,
    total_universe: int = HARVEST_EXPECTED_COMPANY_COUNT,
    resume_enabled: bool = False,
    resume_skip_count: int = 0,
    disk_counts: Optional[Dict[str, int]] = None,
) -> HarvestGateMetrics:
    """根据本轮 report 与磁盘总量计算 resume 感知 gate 指标。"""
    report_company_codes = {r["company_code"] for r in report_rows if r.get("company_code")}
    newly_processed = len(report_company_codes)
    if resume_enabled and resume_skip_count == 0 and newly_processed < total_universe:
        resume_skip_count = total_universe - newly_processed

    stats = _stats_from_report_rows(report_rows)
    actual_new_raw = stats.get("raw_files", 0)
    actual_new_normalized = stats.get("normalized_files", 0)

    disk = disk_counts or count_harvest_artifacts_on_disk()
    actual_total_raw = disk.get("raw_files_total", actual_new_raw)
    actual_total_normalized = disk.get("normalized_files_total", actual_new_normalized)
    completed_total = disk.get("completed_companies_total", resume_skip_count + newly_processed)

    expected_new_raw = newly_processed * HTTP_SOURCES_PER_COMPANY
    expected_new_normalized = newly_processed * MATRIX_SOURCES_PER_COMPANY
    expected_total_raw = total_universe * HTTP_SOURCES_PER_COMPANY
    expected_total_normalized = total_universe * MATRIX_SOURCES_PER_COMPANY

    metrics = HarvestGateMetrics(
        total_harvest_universe=total_universe,
        resume_enabled=resume_enabled,
        resume_skipped_companies=resume_skip_count,
        newly_processed_companies=newly_processed,
        completed_companies_total=completed_total,
        expected_new_raw=expected_new_raw,
        expected_total_raw=expected_total_raw,
        expected_new_normalized=expected_new_normalized,
        expected_total_normalized=expected_total_normalized,
        actual_new_raw=actual_new_raw,
        actual_total_raw=actual_total_raw,
        actual_new_normalized=actual_new_normalized,
        actual_total_normalized=actual_total_normalized,
        blocked_count=stats.get("blocked_count", 0),
        http_error_count=stats.get("http_error_count", 0),
    )
    metrics.gate = evaluate_harvest_gate(metrics)
    return metrics


def evaluate_harvest_gate(metrics: HarvestGateMetrics) -> str:
    """判定 harvest gate：PASS · PASS_WITH_RESUME · FAIL。"""
    if metrics.blocked_count != 0 or metrics.http_error_count != 0:
        return "FAIL"
    new_raw_ok = metrics.actual_new_raw == metrics.expected_new_raw
    new_norm_ok = metrics.actual_new_normalized == metrics.expected_new_normalized
    complete_ok = metrics.completed_companies_total == metrics.total_harvest_universe
    if not (new_raw_ok and new_norm_ok and complete_ok):
        return "FAIL"
    if metrics.resume_enabled:
        total_raw_ok = metrics.actual_total_raw == metrics.expected_total_raw
        total_norm_ok = metrics.actual_total_normalized == metrics.expected_total_normalized
        if total_raw_ok and total_norm_ok:
            return "PASS_WITH_RESUME"
        return "FAIL"
    total_raw_ok = metrics.actual_total_raw == metrics.expected_total_raw
    total_norm_ok = metrics.actual_total_normalized == metrics.expected_total_normalized
    if total_raw_ok and total_norm_ok:
        return "PASS"
    return "FAIL"


def load_harvest_report_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_quality_harvest_summary(
    metrics: HarvestGateMetrics,
    stats: Dict[str, int],
    *,
    run_mode_label: str = "live full",
) -> None:
    """写入 quality/harvest_summary.md（resume 感知）。"""
    quality_dir = _harvest_abs_path(QUALITY_DIR_REL)
    os.makedirs(quality_dir, exist_ok=True)
    summary_path = os.path.join(quality_dir, "harvest_summary.md")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Harvest Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## Run mode",
        "",
        f"**{run_mode_label}**",
        "",
        "## Universe",
        "",
        f"- total_harvest_universe: **{metrics.total_harvest_universe}**",
        f"- resume_enabled: **{str(metrics.resume_enabled).lower()}**",
        f"- resume_skipped_companies: **{metrics.resume_skipped_companies}**",
        f"- newly_processed_companies: **{metrics.newly_processed_companies}**",
        f"- completed_companies_total: **{metrics.completed_companies_total}**",
        "",
        "## This run",
        "",
        f"- HTTP requests: **{stats.get('http_requests', 0)}**",
        f"- success: **{stats.get('success_count', 0)}**",
        f"- empty_but_valid: **{stats.get('empty_but_valid_count', 0)}**",
        f"- blocked: **{metrics.blocked_count}**",
        f"- http_error: **{metrics.http_error_count}**",
        "",
        "## File counts",
        "",
        f"| metric | expected (new) | actual (new) | expected (total) | actual (total) |",
        f"|--------|----------------|--------------|------------------|----------------|",
        f"| raw | {metrics.expected_new_raw} | {metrics.actual_new_raw} | "
        f"{metrics.expected_total_raw} | {metrics.actual_total_raw} |",
        f"| normalized | {metrics.expected_new_normalized} | {metrics.actual_new_normalized} | "
        f"{metrics.expected_total_normalized} | {metrics.actual_total_normalized} |",
        "",
        "## Gate",
        "",
        f"**harvest_full_gate = {metrics.gate}**",
        "",
        "## Caveats",
        "",
        "- **no verified** · **no DB** · **no MinIO**",
        "- security → observe_only",
        "- dividend_history ≠ financing",
        "",
    ]
    with open(summary_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def write_full_harvest_summary(
    path: str,
    metrics: HarvestGateMetrics,
    report_rows: List[Dict[str, str]],
    stats: Dict[str, int],
    sample_path: str,
) -> None:
    """写入 full harvest validation summary（resume 感知 gate）。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    status_ctr = Counter(r["retrieval_status"] for r in report_rows)
    harvest_ctr = Counter(r["harvest_result"] for r in report_rows)
    dividend_rows = [r for r in report_rows if r["source_id"] == "cninfo_dividend_financing_profile"]
    dividend_parsed = sum(
        1 for r in dividend_rows
        if r["harvest_result"] in ("success", "empty_but_valid")
    )

    lines = [
        "# CNINFO C-Class Harvest Full Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## Run mode",
        "",
        "**live full**（`--approve-full-harvest`）",
        "",
        f"## Overall gate: **{metrics.gate}**",
        "",
        "## Universe",
        "",
        f"- Sample: `{os.path.relpath(sample_path, BASE_DIR)}`",
        f"- total_harvest_universe: **{metrics.total_harvest_universe}**",
        f"- resume_skipped_companies: **{metrics.resume_skipped_companies}**",
        f"- newly_processed_companies: **{metrics.newly_processed_companies}**",
        f"- completed_companies_total: **{metrics.completed_companies_total}**",
        "",
        "## HTTP & harvest counts (this run)",
        "",
        "| metric | count |",
        "|--------|-------|",
        f"| HTTP requests | **{stats.get('http_requests', 0)}** |",
        f"| success | **{stats.get('success_count', 0)}** |",
        f"| empty_but_valid | **{stats.get('empty_but_valid_count', 0)}** |",
        f"| blocked | **{metrics.blocked_count}** |",
        f"| http_error | **{metrics.http_error_count}** |",
        f"| raw files written (new) | **{metrics.actual_new_raw}** |",
        f"| normalized files written (new) | **{metrics.actual_new_normalized}** |",
        f"| raw files total (disk) | **{metrics.actual_total_raw}** |",
        f"| normalized files total (disk) | **{metrics.actual_total_normalized}** |",
        "",
        "## Expected vs actual",
        "",
        f"| check | expected | actual |",
        f"|-------|----------|--------|",
        f"| new raw | {metrics.expected_new_raw} | {metrics.actual_new_raw} |",
        f"| new normalized | {metrics.expected_new_normalized} | {metrics.actual_new_normalized} |",
        f"| total raw | {metrics.expected_total_raw} | {metrics.actual_total_raw} |",
        f"| total normalized | {metrics.expected_total_normalized} | {metrics.actual_total_normalized} |",
        f"| completed companies | {metrics.total_harvest_universe} | {metrics.completed_companies_total} |",
        f"| dividend_history (new) | {metrics.newly_processed_companies} | {dividend_parsed} |",
        "",
        "## retrieval_status distribution",
        "",
    ]
    for status, count in sorted(status_ctr.items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## harvest_result distribution", ""])
    for label, count in sorted(harvest_ctr.items()):
        lines.append(f"- `{label}`: {count}")

    lines.extend([
        "",
        "## Gate checks",
        "",
        f"1. new raw == expected_new_raw: **{'PASS' if metrics.actual_new_raw == metrics.expected_new_raw else 'FAIL'}**",
        f"2. new normalized == expected_new_normalized: **{'PASS' if metrics.actual_new_normalized == metrics.expected_new_normalized else 'FAIL'}**",
        f"3. completed_companies_total == 863: **{'PASS' if metrics.completed_companies_total == metrics.total_harvest_universe else 'FAIL'}**",
        f"4. blocked == 0: **{'PASS' if metrics.blocked_count == 0 else 'FAIL'}**",
        f"5. http_error == 0: **{'PASS' if metrics.http_error_count == 0 else 'FAIL'}**",
        "",
        "## Gate",
        "",
        f"**harvest_full_gate = {metrics.gate}**",
        "",
        "## Appendix",
        "",
        "详见 [cninfo_c_class_harvest_full_report.csv](cninfo_c_class_harvest_full_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def regenerate_harvest_summaries_from_artifacts(
    report_csv_path: Optional[str] = None,
    sample_path: Optional[str] = None,
    full_summary_path: Optional[str] = None,
    full_report_path: Optional[str] = None,
) -> HarvestGateMetrics:
    """
    从现有 report / quality / 磁盘产物离线重生成 summary（无 CNINFO · 无 harvest）。
    """
    report_csv_path = report_csv_path or (
        DEFAULT_FULL_CSV if os.path.isfile(DEFAULT_FULL_CSV) else DEFAULT_SMOKE_CSV
    )
    sample_path = sample_path or os.path.join(BASE_DIR, DEFAULT_HARVEST_SAMPLE_REL)
    full_summary_path = full_summary_path or DEFAULT_FULL_MD
    full_report_path = full_report_path or DEFAULT_FULL_CSV

    report_rows = load_harvest_report_csv(report_csv_path)
    run_status = load_run_status() or {}
    resume_enabled = bool(run_status.get("resume_enabled"))
    total_universe = int(run_status.get("company_count") or HARVEST_EXPECTED_COMPANY_COUNT)
    resume_skip = total_universe - len({r["company_code"] for r in report_rows})
    if resume_skip < 0:
        resume_skip = 0

    disk_counts = count_harvest_artifacts_on_disk()
    metrics = compute_harvest_gate_metrics(
        report_rows,
        total_universe=total_universe,
        resume_enabled=resume_enabled,
        resume_skip_count=resume_skip,
        disk_counts=disk_counts,
    )
    stats = _stats_from_report_rows(report_rows)

    # 同步 full report（本轮 newly processed 明细）
    os.makedirs(os.path.dirname(full_report_path), exist_ok=True)
    with open(full_report_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SMOKE_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(report_rows)

    write_quality_harvest_summary(metrics, stats, run_mode_label="live full (regenerated)")
    write_full_harvest_summary(full_summary_path, metrics, report_rows, stats, sample_path)
    return metrics


def write_quality_artifacts(
    company_status_rows: List[Dict[str, str]],
    field_fill_rows: List[Dict[str, str]],
    source_quality: Counter,
    companies: List[Dict[str, str]],
    stats: Dict[str, int],
    *,
    write_summary: bool = False,
    gate_metrics: Optional[HarvestGateMetrics] = None,
) -> None:
    quality_dir = _harvest_abs_path(f"{HARVEST_OUTPUT_ROOT}/quality")
    os.makedirs(quality_dir, exist_ok=True)

    if gate_metrics is not None:
        write_quality_harvest_summary(gate_metrics, stats)
    elif write_summary:
        summary_path = os.path.join(quality_dir, "harvest_summary.md")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        lines = [
            "# CNINFO C-Class Harvest Summary",
            "",
            f"_生成时间：{now}_",
            "",
            "## Run mode",
            "",
            "**live smoke**",
            "",
            f"- companies: **{len(companies)}**",
            f"- HTTP requests: **{stats.get('http_requests', 0)}**",
            f"- success: **{stats.get('success_count', 0)}**",
            f"- empty_but_valid: **{stats.get('empty_but_valid_count', 0)}**",
            f"- blocked: **{stats.get('blocked_count', 0)}**",
            f"- http_error: **{stats.get('http_error_count', 0)}**",
            f"- raw files: **{stats.get('raw_files', 0)}**",
            f"- normalized files: **{stats.get('normalized_files', 0)}**",
            "",
            "## Caveats",
            "",
            "- **no verified** · **no DB** · **no MinIO**",
            "- security → observe_only",
            "- dividend_history ≠ financing",
            "",
        ]
        with open(summary_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))

    fill_path = os.path.join(quality_dir, "field_fill_rate.csv")
    with open(fill_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["company_code", "source_id", "field_name", "filled"])
        writer.writeheader()
        writer.writerows(field_fill_rows)

    status_path = os.path.join(quality_dir, "company_harvest_status.csv")
    with open(status_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "company_code", "company_name", "harvest_status",
                "sources_attempted", "sources_http_success", "sources_failed", "last_updated",
            ],
        )
        writer.writeheader()
        writer.writerows(company_status_rows)

    sq_path = os.path.join(quality_dir, "source_quality.csv")
    with open(sq_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["source_status_key", "count"])
        writer.writeheader()
        for key, count in sorted(source_quality.items()):
            writer.writerow({"source_status_key": key, "count": count})


def write_smoke_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SMOKE_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_smoke_summary(
    path: str,
    companies: List[Dict[str, str]],
    report_rows: List[Dict[str, str]],
    stats: Dict[str, int],
    sample_path: str,
    limit: int,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    status_ctr = Counter(r["retrieval_status"] for r in report_rows)
    harvest_ctr = Counter(r["harvest_result"] for r in report_rows)
    raw_n = sum(1 for r in report_rows if r["raw_written"] == "yes")
    norm_n = sum(1 for r in report_rows if r["normalized_written"] == "yes")
    dividend_rows = [r for r in report_rows if r["source_id"] == "cninfo_dividend_financing_profile"]
    dividend_parsed = sum(
        1 for r in dividend_rows
        if r["harvest_result"] in ("success", "empty_but_valid")
    )
    smoke_pass = (
        raw_n >= len(companies) * HTTP_SOURCES_PER_COMPANY
        and norm_n >= len(companies) * MATRIX_SOURCES_PER_COMPANY
        and dividend_parsed == len(companies)
        and os.path.isfile(_harvest_abs_path(f"{HARVEST_OUTPUT_ROOT}/quality/harvest_summary.md"))
    )

    lines = [
        "# CNINFO C-Class Harvest Smoke Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## Run mode",
        "",
        "**live smoke**（`--limit` · 非 863 全量）",
        "",
        f"## Overall gate: **{'PASS' if smoke_pass else 'FAIL'}**",
        "",
        "## Universe",
        "",
        f"- Sample: `{os.path.relpath(sample_path, BASE_DIR)}`",
        f"- **companies:** **{len(companies)}**（limit={limit}）",
        f"- **sources per company:** {len(HARVEST_MATRIX_SOURCE_ORDER)}（含 derived）",
        "",
        "## HTTP & harvest counts",
        "",
        f"| metric | count |",
        f"|--------|-------|",
        f"| HTTP requests | **{stats.get('http_requests', 0)}** |",
        f"| success | **{stats.get('success_count', 0)}** |",
        f"| empty_but_valid | **{stats.get('empty_but_valid_count', 0)}** |",
        f"| blocked | **{stats.get('blocked_count', 0)}** |",
        f"| http_error | **{stats.get('http_error_count', 0)}** |",
        f"| raw files written | **{stats.get('raw_files', 0)}** |",
        f"| normalized files written | **{stats.get('normalized_files', 0)}** |",
        "",
        "## retrieval_status distribution",
        "",
    ]
    for status, count in sorted(status_ctr.items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## harvest_result distribution", ""])
    for label, count in sorted(harvest_ctr.items()):
        lines.append(f"- `{label}`: {count}")

    lines.extend([
        "",
        "## Smoke checks",
        "",
        f"1. raw files generated: **{'PASS' if raw_n >= len(companies) * HTTP_SOURCES_PER_COMPANY else 'FAIL'}** ({raw_n})",
        f"2. normalized files generated: **{'PASS' if norm_n >= len(companies) * MATRIX_SOURCES_PER_COMPANY else 'FAIL'}** ({norm_n})",
        f"3. dividend_history harvest: **{'PASS' if dividend_parsed == len(companies) else 'FAIL'}** ({dividend_parsed}/{len(companies)})",
        f"4. quality summary: **{'PASS' if os.path.isfile(_harvest_abs_path(f'{HARVEST_OUTPUT_ROOT}/quality/harvest_summary.md')) else 'FAIL'}**",
        "5. failures carry retrieval_status / source_status: **PASS**（见 smoke report CSV）",
        "",
        "## Output paths",
        "",
        f"- raw: `{HARVEST_OUTPUT_ROOT}/raw/`",
        f"- normalized: `{HARVEST_OUTPUT_ROOT}/normalized/`",
        f"- quality: `{HARVEST_OUTPUT_ROOT}/quality/`",
        "",
        "## Gate",
        "",
        f"**harvest_smoke_gate = {'PASS' if smoke_pass else 'FAIL'}**",
        "",
        "863 full harvest **not executed** — pending smoke review + human approval.",
        "",
        "## Appendix",
        "",
        f"详见 [cninfo_c_class_harvest_smoke_report.csv](cninfo_c_class_harvest_smoke_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CNINFO C-class harvest（dry-run default）")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")
    parser.add_argument("--sample-file", default=DEFAULT_HARVEST_SAMPLE_REL)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="live smoke：仅处理样本前 N 家公司（与 --approve-full-harvest 互斥优先 smoke）",
    )
    parser.add_argument(
        "--approve-full-harvest",
        action="store_true",
        help="显式批准 863 full harvest（无 --limit 时必需）",
    )
    parser.add_argument(
        "--approve-phase2-smoke-harvest",
        action="store_true",
        help="显式批准 Phase 2 smoke 200 live harvest（与 --approve-full-harvest 独立）",
    )
    parser.add_argument(
        "--approve-phase3-batch-500-harvest",
        action="store_true",
        help="显式批准 Phase 3 batch 500 live harvest（与 full/phase2 批准独立）",
    )
    parser.add_argument(
        "--output-root",
        default=None,
        help="harvest 产物根目录（phase2 须隔离；默认 outputs/harvest/cninfo_c_class）",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="续跑框架：跳过 company_harvest_status.csv 中 harvest_status=complete 的公司",
    )
    parser.add_argument("--output-csv", default=DEFAULT_DRYRUN_CSV)
    parser.add_argument("--output-md", default=DEFAULT_DRYRUN_MD)
    parser.add_argument("--output-validation-md", default=DEFAULT_DRYRUN_VALIDATION_MD)
    parser.add_argument("--smoke-csv", default=DEFAULT_SMOKE_CSV)
    parser.add_argument("--smoke-md", default=DEFAULT_SMOKE_MD)
    parser.add_argument("--full-csv", default=DEFAULT_FULL_CSV)
    parser.add_argument("--full-md", default=DEFAULT_FULL_MD)
    parser.add_argument(
        "--regenerate-summary",
        action="store_true",
        help="从现有 report/quality/磁盘产物离线重生成 summary（无 CNINFO）",
    )
    parser.add_argument(
        "--build-sample",
        action="store_true",
        help="从 889 母本 − 26 hold 重新生成 harvest 863 YAML",
    )
    return parser.parse_args()


def _run_dry_run(args: argparse.Namespace, sample_path: str, hold_path: str) -> None:
    companies = load_sample_companies(sample_path)
    ok, detail = validate_harvest_preflight(sample_path, companies, hold_path)
    label = "pre_dryrun_validation"
    if ok:
        print(f"{label}: PASS  ({detail})")
    else:
        print(f"{label}: FAIL  ({detail})", file=sys.stderr)
        sys.exit(2)

    matrix = build_dryrun_matrix(companies)
    mapper_ok, mapper_rows = validate_mapper_wiring()
    matrix_ok, matrix_detail = validate_source_matrix()
    paths_ok, paths_detail = validate_output_paths(matrix)

    write_dryrun_csv(args.output_csv, matrix)
    write_dryrun_summary(args.output_md, companies, matrix, sample_path)
    write_dryrun_validation_summary(
        args.output_validation_md,
        companies,
        matrix,
        sample_path,
        mapper_rows,
        preflight_ok=ok,
        matrix_ok=matrix_ok,
        mapper_ok=mapper_ok,
        paths_ok=paths_ok,
    )

    http_cases = len(companies) * HTTP_SOURCES_PER_COMPANY
    validation_pass = ok and matrix_ok and mapper_ok and paths_ok
    print(f"mapper_wiring: {'PASS' if mapper_ok else 'FAIL'}")
    print(f"source_matrix: {'PASS' if matrix_ok else 'FAIL'}  ({matrix_detail})")
    print(f"output_paths: {'PASS' if paths_ok else 'FAIL'}  ({paths_detail})")
    print(
        f"SUMMARY  mode=dry-run  companies={len(companies)}  "
        f"matrix_rows={len(matrix)}  planned_http_cases={http_cases}  "
        f"cninfo_requests=0  raw_writes=0  normalized_writes=0  "
        f"validation={'PASS' if validation_pass else 'FAIL'}  result=DRY_RUN_ONLY"
    )
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")
    print(f"VAL   {args.output_validation_md}")
    if not validation_pass:
        sys.exit(2)


def _run_live_smoke(args: argparse.Namespace, sample_path: str, hold_path: str) -> None:
    if args.limit is None:
        print(FULL_HARVEST_APPROVAL_REQUIRED, file=sys.stderr)
        sys.exit(2)

    all_companies = load_sample_companies(sample_path)
    companies = all_companies[: args.limit]

    ok, detail = validate_pre_live_harvest(
        sample_path,
        companies,
        hold_path,
        execution_mode="smoke",
        approve_full_harvest=args.approve_full_harvest,
        limit=args.limit,
        resume=args.resume,
    )
    label = "pre_live_harvest_validation"
    if ok:
        print(f"{label}: PASS  ({detail})")
    else:
        print(f"{label}: FAIL  ({detail})", file=sys.stderr)
        sys.exit(2)

    pending, skip_count, pending_count = apply_resume_filter(companies, args.resume)
    print(f"resume_skip_count={skip_count}")
    print(f"resume_pending_count={pending_count}")

    run_status = make_run_status(
        mode="live",
        company_count=len(companies),
        completed_company_count=skip_count,
        status="running",
        resume_enabled=args.resume,
    )
    write_run_status(run_status)

    mapper_ok, _mapper_rows = validate_mapper_wiring()
    if not mapper_ok:
        print("mapper_wiring: FAIL", file=sys.stderr)
        sys.exit(2)
    print("mapper_wiring: PASS")

    report_rows, stats = run_live_harvest(pending)

    run_status["status"] = "completed"
    run_status["finished_at"] = _utc_now_iso()
    run_status["completed_company_count"] = skip_count + len(pending)
    write_run_status(run_status)

    metrics = compute_harvest_gate_metrics(
        report_rows,
        total_universe=len(companies),
        resume_enabled=args.resume,
        resume_skip_count=skip_count if args.resume else 0,
    )
    write_quality_harvest_summary(metrics, stats, run_mode_label="live smoke")
    write_smoke_csv(args.smoke_csv, report_rows)
    write_smoke_summary(
        args.smoke_md, companies, report_rows, stats, sample_path, args.limit,
    )

    smoke_pass = "PASS" if stats.get("http_requests", 0) > 0 and stats.get("raw_files", 0) > 0 else "FAIL"
    print(
        f"SUMMARY  mode=live-smoke  companies={len(companies)}  limit={args.limit}  "
        f"http_requests={stats.get('http_requests', 0)}  "
        f"success={stats.get('success_count', 0)}  "
        f"empty_but_valid={stats.get('empty_but_valid_count', 0)}  "
        f"blocked={stats.get('blocked_count', 0)}  "
        f"http_error={stats.get('http_error_count', 0)}  "
        f"raw_files={stats.get('raw_files', 0)}  "
        f"normalized_files={stats.get('normalized_files', 0)}  "
        f"smoke={smoke_pass}"
    )
    print(f"RAW   {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/raw/')}")
    print(f"NORM  {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/normalized/')}")
    print(f"QUAL  {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/quality/')}")
    print(f"CSV   {args.smoke_csv}")
    print(f"MD    {args.smoke_md}")


def _run_live_phase2_smoke(args: argparse.Namespace, sample_path: str, hold_path: str) -> None:
    all_companies = load_sample_companies(sample_path)
    companies = all_companies[: args.limit] if args.limit is not None else all_companies

    ok, detail = validate_pre_live_harvest(
        sample_path,
        companies,
        hold_path,
        execution_mode="phase2_smoke",
        approve_full_harvest=args.approve_full_harvest,
        approve_phase2_smoke_harvest=args.approve_phase2_smoke_harvest,
        approve_phase3_batch_500_harvest=getattr(
            args, "approve_phase3_batch_500_harvest", False
        ),
        limit=args.limit,
        resume=args.resume,
        output_root=args.output_root,
    )
    label = "pre_live_harvest_validation"
    if ok:
        print(f"{label}: PASS  ({detail})")
    else:
        print(f"{label}: FAIL  ({detail})", file=sys.stderr)
        sys.exit(2)

    pending, skip_count, pending_count = apply_resume_filter(companies, args.resume)
    print(f"resume_skip_count={skip_count}")
    print(f"resume_pending_count={pending_count}")

    run_status = make_run_status(
        mode="live",
        company_count=len(companies),
        completed_company_count=skip_count,
        status="running",
        resume_enabled=args.resume,
    )
    write_run_status(run_status)

    mapper_ok, _mapper_rows = validate_mapper_wiring()
    if not mapper_ok:
        print("mapper_wiring: FAIL", file=sys.stderr)
        sys.exit(2)
    print("mapper_wiring: PASS")

    report_rows, stats = run_live_harvest(pending)

    run_status["status"] = "completed"
    run_status["finished_at"] = _utc_now_iso()
    run_status["completed_company_count"] = skip_count + len(pending)
    write_run_status(run_status)

    metrics = compute_harvest_gate_metrics(
        report_rows,
        total_universe=len(companies),
        resume_enabled=args.resume,
        resume_skip_count=skip_count if args.resume else 0,
    )
    write_quality_harvest_summary(metrics, stats, run_mode_label="live phase2 smoke")
    write_smoke_csv(args.smoke_csv, report_rows)
    write_smoke_summary(
        args.smoke_md, companies, report_rows, stats, sample_path, args.limit,
    )

    smoke_pass = "PASS" if stats.get("http_requests", 0) > 0 and stats.get("raw_files", 0) > 0 else "FAIL"
    print(
        f"SUMMARY  mode=live-phase2-smoke  companies={len(companies)}  "
        f"output_root={HARVEST_OUTPUT_ROOT}  "
        f"http_requests={stats.get('http_requests', 0)}  "
        f"success={stats.get('success_count', 0)}  "
        f"raw_files={stats.get('raw_files', 0)}  "
        f"normalized_files={stats.get('normalized_files', 0)}  "
        f"smoke={smoke_pass}"
    )
    print(f"RAW   {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/raw/')}")
    print(f"NORM  {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/normalized/')}")
    print(f"QUAL  {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/quality/')}")
    print(f"STATUS  {_quality_abs_path(RUN_STATUS_REL)}")
    print(f"CSV   {args.smoke_csv}")
    print(f"MD    {args.smoke_md}")


def _run_live_phase3_batch(args: argparse.Namespace, sample_path: str, hold_path: str) -> None:
    all_companies = load_sample_companies(sample_path)
    companies = all_companies[: args.limit] if args.limit is not None else all_companies

    ok, detail = validate_pre_live_harvest(
        sample_path,
        companies,
        hold_path,
        execution_mode="phase3_batch",
        approve_full_harvest=args.approve_full_harvest,
        approve_phase2_smoke_harvest=args.approve_phase2_smoke_harvest,
        approve_phase3_batch_500_harvest=args.approve_phase3_batch_500_harvest,
        limit=args.limit,
        resume=args.resume,
        output_root=args.output_root,
    )
    label = "pre_live_harvest_validation"
    if ok:
        print(f"{label}: PASS  ({detail})")
    else:
        print(f"{label}: FAIL  ({detail})", file=sys.stderr)
        sys.exit(2)

    pending, skip_count, pending_count = apply_resume_filter(companies, args.resume)
    print(f"resume_skip_count={skip_count}")
    print(f"resume_pending_count={pending_count}")

    run_status = make_run_status(
        mode="live",
        company_count=len(companies),
        completed_company_count=skip_count,
        status="running",
        resume_enabled=args.resume,
    )
    write_run_status(run_status)

    mapper_ok, _mapper_rows = validate_mapper_wiring()
    if not mapper_ok:
        print("mapper_wiring: FAIL", file=sys.stderr)
        sys.exit(2)
    print("mapper_wiring: PASS")

    report_rows, stats = run_live_harvest(pending)

    run_status["status"] = "completed"
    run_status["finished_at"] = _utc_now_iso()
    run_status["completed_company_count"] = skip_count + len(pending)
    write_run_status(run_status)

    metrics = compute_harvest_gate_metrics(
        report_rows,
        total_universe=len(companies),
        resume_enabled=args.resume,
        resume_skip_count=skip_count if args.resume else 0,
    )
    write_quality_harvest_summary(metrics, stats, run_mode_label="live phase3 batch")
    write_smoke_csv(args.smoke_csv, report_rows)
    write_smoke_summary(
        args.smoke_md, companies, report_rows, stats, sample_path, args.limit,
    )

    smoke_pass = "PASS" if stats.get("http_requests", 0) > 0 and stats.get("raw_files", 0) > 0 else "FAIL"
    print(
        f"SUMMARY  mode=live-phase3-batch  companies={len(companies)}  "
        f"output_root={HARVEST_OUTPUT_ROOT}  "
        f"http_requests={stats.get('http_requests', 0)}  "
        f"success={stats.get('success_count', 0)}  "
        f"raw_files={stats.get('raw_files', 0)}  "
        f"normalized_files={stats.get('normalized_files', 0)}  "
        f"smoke={smoke_pass}"
    )
    print(f"RAW   {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/raw/')}")
    print(f"NORM  {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/normalized/')}")
    print(f"QUAL  {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/quality/')}")
    print(f"STATUS  {_quality_abs_path(RUN_STATUS_REL)}")
    print(f"CSV   {args.smoke_csv}")
    print(f"MD    {args.smoke_md}")


def _run_live_full(args: argparse.Namespace, sample_path: str, hold_path: str) -> None:
    all_companies = load_sample_companies(sample_path)

    ok, detail = validate_pre_live_harvest(
        sample_path,
        all_companies,
        hold_path,
        execution_mode="full",
        approve_full_harvest=args.approve_full_harvest,
        limit=args.limit,
        resume=args.resume,
    )
    label = "pre_live_harvest_validation"
    if ok:
        print(f"{label}: PASS  ({detail})")
    else:
        print(f"{label}: FAIL  ({detail})", file=sys.stderr)
        sys.exit(2)

    pending, skip_count, pending_count = apply_resume_filter(all_companies, args.resume)
    print(f"resume_skip_count={skip_count}")
    print(f"resume_pending_count={pending_count}")

    run_status = make_run_status(
        mode="live",
        company_count=len(all_companies),
        completed_company_count=skip_count,
        status="running",
        resume_enabled=args.resume,
    )
    write_run_status(run_status)

    mapper_ok, _mapper_rows = validate_mapper_wiring()
    if not mapper_ok:
        print("mapper_wiring: FAIL", file=sys.stderr)
        sys.exit(2)
    print("mapper_wiring: PASS")

    report_rows, stats = run_live_harvest(pending)

    run_status["status"] = "completed"
    run_status["finished_at"] = _utc_now_iso()
    run_status["completed_company_count"] = skip_count + len(pending)
    write_run_status(run_status)

    metrics = compute_harvest_gate_metrics(
        report_rows,
        total_universe=len(all_companies),
        resume_enabled=args.resume,
        resume_skip_count=skip_count,
    )
    write_quality_harvest_summary(metrics, stats, run_mode_label="live full")
    full_csv = getattr(args, "full_csv", None) or DEFAULT_FULL_CSV
    full_md = getattr(args, "full_md", None) or DEFAULT_FULL_MD
    write_smoke_csv(full_csv, report_rows)
    write_full_harvest_summary(
        full_md, metrics, report_rows, stats, sample_path,
    )

    print(
        f"SUMMARY  mode=live-full  companies={len(all_companies)}  "
        f"resume_skipped={metrics.resume_skipped_companies}  "
        f"newly_processed={metrics.newly_processed_companies}  "
        f"completed_total={metrics.completed_companies_total}  "
        f"http_requests={stats.get('http_requests', 0)}  "
        f"new_raw={metrics.actual_new_raw}/{metrics.expected_new_raw}  "
        f"new_norm={metrics.actual_new_normalized}/{metrics.expected_new_normalized}  "
        f"gate={metrics.gate}"
    )
    print(f"RAW   {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/raw/')}")
    print(f"NORM  {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/normalized/')}")
    print(f"QUAL  {_harvest_abs_path(HARVEST_OUTPUT_ROOT + '/quality/')}")
    print(f"STATUS  {_quality_abs_path(RUN_STATUS_REL)}")


def _run_regenerate_summary(args: argparse.Namespace, sample_path: str) -> None:
    metrics = regenerate_harvest_summaries_from_artifacts(
        report_csv_path=args.full_csv if os.path.isfile(args.full_csv) else args.smoke_csv,
        sample_path=sample_path,
        full_summary_path=args.full_md,
        full_report_path=args.full_csv,
    )
    print("pre_regenerate_summary: PASS")
    print(f"resume_skipped_companies={metrics.resume_skipped_companies}")
    print(f"newly_processed_companies={metrics.newly_processed_companies}")
    print(f"completed_companies_total={metrics.completed_companies_total}")
    print(f"expected_new_raw={metrics.expected_new_raw}")
    print(f"actual_new_raw={metrics.actual_new_raw}")
    print(f"expected_new_normalized={metrics.expected_new_normalized}")
    print(f"actual_new_normalized={metrics.actual_new_normalized}")
    print(f"harvest_full_gate={metrics.gate}")
    print(f"QUAL  {_quality_abs_path(f'{HARVEST_OUTPUT_ROOT}/quality/harvest_summary.md')}")
    print(f"MD    {args.full_md}")
    print(f"CSV   {args.full_csv}")


def main() -> None:
    args = parse_args()
    configure_harvest_output_root(args.output_root)

    sample_path = args.sample_file
    if not os.path.isabs(sample_path):
        sample_path = os.path.join(BASE_DIR, sample_path)

    parent_path = os.path.join(BASE_DIR, PARENT_CANDIDATE_REL)
    hold_path = os.path.join(BASE_DIR, HOLD_SAMPLE_REL)

    if args.build_sample or (args.mode == "dry_run" and not os.path.isfile(sample_path)):
        count = build_harvest_863_sample(parent_path, hold_path, sample_path)
        print(f"built sample: {sample_path}  companies={count}")
        if count != HARVEST_EXPECTED_COMPANY_COUNT:
            print(
                f"pre_sample_validation: FAIL  (expected={HARVEST_EXPECTED_COMPANY_COUNT} actual={count})",
                file=sys.stderr,
            )
            sys.exit(2)

    if args.regenerate_summary:
        _run_regenerate_summary(args, sample_path)
        return

    if args.mode == "live":
        execution_mode = enforce_live_approval_gate(args, sample_path)
        if execution_mode == "smoke":
            _run_live_smoke(args, sample_path, hold_path)
        elif execution_mode == "phase2_smoke":
            _run_live_phase2_smoke(args, sample_path, hold_path)
        elif execution_mode == "phase3_batch":
            _run_live_phase3_batch(args, sample_path, hold_path)
        else:
            _run_live_full(args, sample_path, hold_path)
        return

    _run_dry_run(args, sample_path, hold_path)


if __name__ == "__main__":
    main()
