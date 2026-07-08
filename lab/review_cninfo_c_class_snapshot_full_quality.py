#!/usr/bin/env python3
"""
CNINFO C-class Snapshot Full Quality Review（Era C Phase 4）。

离线只读 full snapshot JSON 做 QA 分析。
不修改 snapshot / normalized / field_inventory · 不请求 CNINFO。

Usage:
    python lab/review_cninfo_c_class_snapshot_full_quality.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from build_cninfo_c_class_company_snapshot import SNAPSHOT_MODULES  # noqa: E402

BASE_DIR = os.path.dirname(_LAB_DIR)
FULL_DIR = os.path.join(BASE_DIR, "outputs/snapshot/cninfo_c_class/full")
STATUS_CSV = os.path.join(FULL_DIR, "quality/company_snapshot_status.csv")
MAPPING_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_snapshot_field_mapping.csv"
)

COMPLETENESS_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_snapshot_full_completeness_report.csv"
)
MODULE_COVERAGE_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_snapshot_full_module_coverage.csv"
)
FIELD_COVERAGE_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_snapshot_full_field_coverage.csv"
)
QUALITY_FLAGS_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_snapshot_full_quality_flags.csv"
)
QUALITY_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_snapshot_full_quality_summary.md"
)

EXPECTED_COMPANY_COUNT = 863

COMPLETENESS_FIELDS = [
    "company_code",
    "company_name",
    "json_exists",
    "json_valid",
    "module_count",
    "snapshot_status",
    "error_type",
    "notes",
]

MODULE_COVERAGE_FIELDS = [
    "module",
    "available_count",
    "partial_count",
    "not_available_count",
    "coverage_rate",
    "common_missing_reason",
]

FIELD_COVERAGE_FIELDS = [
    "field_name",
    "module",
    "available_count",
    "null_count",
    "missing_rate",
    "source_count",
]

QUALITY_FLAG_FIELDS = [
    "company_code",
    "module",
    "flag_type",
    "flag_detail",
    "severity",
]

ARRAY_MODULE_KEYS = {
    "executive_profile": "executives",
    "shareholder_profile": "shareholders",
    "dividend_profile": "dividend_events",
    "capital_action_profile": "capital_actions",
    "event_timeline": "events",
}

MODULE_MISSING_REASONS = {
    "technology_profile": "not_modeled_no_rd_source",
    "market_behavior": "security_observe_only",
    "investor_relation": "overlaps_organization_profile",
    "risk_profile": "security_observe_only",
    "shareholder_profile": "source_partial_top_n",
    "capital_action_profile": "share_capital_source_partial",
    "executive_profile": "empty_but_valid_or_sparse",
    "dividend_profile": "dividend_valid_empty_or_parse_partial",
    "financial_snapshot": "share_capital_empty_but_valid",
    "event_timeline": "derived_from_dividend_share_capital",
}


def _is_meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


def load_field_mapping(path: str = MAPPING_CSV) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_status_csv(path: str = STATUS_CSV) -> Dict[str, Dict[str, str]]:
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return {row["company_code"]: row for row in csv.DictReader(fh)}


def list_snapshot_json_paths(snapshot_dir: str = FULL_DIR) -> List[str]:
    if not os.path.isdir(snapshot_dir):
        return []
    paths = [
        os.path.join(snapshot_dir, fn)
        for fn in os.listdir(snapshot_dir)
        if fn.endswith(".json")
    ]
    return sorted(paths)


def load_snapshot(path: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        with open(path, encoding="utf-8") as fh:
            content = fh.read().strip()
        if not content:
            return None, "empty_file"
        return json.loads(content), None
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc}"
    except OSError as exc:
        return None, f"os_error:{exc}"


def extract_module_field_keys(module_name: str, module: Dict[str, Any]) -> Set[str]:
    """提取模块字段键集合（含数组 item 键）。"""
    keys: Set[str] = set()
    fields = module.get("fields") or {}
    array_key = ARRAY_MODULE_KEYS.get(module_name)
    if array_key and isinstance(fields.get(array_key), list):
        for item in fields[array_key]:
            if isinstance(item, dict):
                keys.update(item.keys())
    for key, val in fields.items():
        if key == array_key:
            continue
        if isinstance(val, dict):
            keys.update(val.keys())
        else:
            keys.add(key)
    return keys


def field_present_in_module(
    module_name: str,
    module: Dict[str, Any],
    field_name: str,
) -> bool:
    fields = module.get("fields") or {}
    array_key = ARRAY_MODULE_KEYS.get(module_name)
    if array_key and isinstance(fields.get(array_key), list):
        for item in fields[array_key]:
            if isinstance(item, dict) and _is_meaningful(item.get(field_name)):
                return True
    val = fields.get(field_name)
    if _is_meaningful(val):
        return True
    if isinstance(val, dict):
        return any(_is_meaningful(v) for v in val.values())
    return False


def count_sources(module: Dict[str, Any]) -> int:
    return len(module.get("sources") or [])


def run_completeness_check(
    snapshot_dir: str = FULL_DIR,
    status_by_code: Optional[Dict[str, Dict[str, str]]] = None,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    status_by_code = status_by_code or load_status_csv()
    paths = list_snapshot_json_paths(snapshot_dir)
    path_by_code = {os.path.basename(p)[:-5]: p for p in paths}

    all_codes: Set[str] = set(status_by_code.keys()) | set(path_by_code.keys())
    rows: List[Dict[str, str]] = []
    stats = {
        "snapshot_json_count": len(paths),
        "company_count": len(all_codes),
        "duplicate_company_codes": [],
        "empty_snapshot_count": 0,
        "malformed_json_count": 0,
        "valid_json_count": 0,
    }

    if len(path_by_code) != len(paths):
        seen: Dict[str, int] = defaultdict(int)
        for code in path_by_code:
            seen[code] += 1
        stats["duplicate_company_codes"] = sorted(c for c, n in seen.items() if n > 1)

    for code in sorted(all_codes):
        status_row = status_by_code.get(code, {})
        company_name = status_row.get("company_name", "")
        path = path_by_code.get(code)
        json_exists = path is not None and os.path.isfile(path)
        json_valid = "no"
        module_count = ""
        snapshot_status = ""
        error_type = ""
        notes = ""

        if not json_exists:
            error_type = "json_missing"
            notes = "snapshot JSON not found"
        else:
            snap, err = load_snapshot(path)
            if err == "empty_file":
                stats["empty_snapshot_count"] += 1
                error_type = "empty_snapshot"
                notes = "file is empty"
            elif err:
                stats["malformed_json_count"] += 1
                error_type = "malformed_json"
                notes = err
            elif snap:
                stats["valid_json_count"] += 1
                json_valid = "yes"
                modules = snap.get("modules") or {}
                module_count = str(len(modules))
                snapshot_status = snap.get("snapshot_status", "")
                company_name = company_name or snap.get("company_name", "")
                if len(modules) != len(SNAPSHOT_MODULES):
                    notes = f"module_count={len(modules)} expected={len(SNAPSHOT_MODULES)}"

        rows.append({
            "company_code": code,
            "company_name": company_name,
            "json_exists": "yes" if json_exists else "no",
            "json_valid": json_valid,
            "module_count": module_count,
            "snapshot_status": snapshot_status,
            "error_type": error_type,
            "notes": notes,
        })

    return rows, stats


def run_module_coverage(
    snapshots: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    total = len(snapshots)
    module_status_counts: Dict[str, Counter] = {
        m: Counter() for m in SNAPSHOT_MODULES
    }

    for snap in snapshots.values():
        modules = snap.get("modules") or {}
        for mod in SNAPSHOT_MODULES:
            st = (modules.get(mod) or {}).get("status", "missing")
            module_status_counts[mod][st] += 1

    rows: List[Dict[str, Any]] = []
    for mod in SNAPSHOT_MODULES:
        c = module_status_counts[mod]
        avail = c.get("available", 0)
        partial = c.get("partial", 0)
        na = c.get("not_available", 0) + c.get("missing", 0)
        coverage_rate = round((avail + partial) / total, 4) if total else 0.0
        reason = MODULE_MISSING_REASONS.get(mod, "")
        if partial > 0 and not reason:
            reason = "partial_data_expected"
        if na == total:
            reason = reason or "all_not_available"
        rows.append({
            "module": mod,
            "available_count": avail,
            "partial_count": partial,
            "not_available_count": na,
            "coverage_rate": coverage_rate,
            "common_missing_reason": reason,
        })
    return rows


def run_field_coverage(
    snapshots: Dict[str, Dict[str, Any]],
    mapping_rows: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    total = len(snapshots)
    field_meta: Dict[Tuple[str, str], Dict[str, Any]] = {}

    for row in mapping_rows:
        mod = row["snapshot_module"]
        fn = row["normalized_field_name"]
        key = (mod, fn)
        if key not in field_meta:
            field_meta[key] = {
                "field_name": fn,
                "module": mod,
                "available_count": 0,
                "null_count": 0,
                "source_count": 0,
            }

    for snap in snapshots.values():
        modules = snap.get("modules") or {}
        for (mod, fn), meta in field_meta.items():
            module = modules.get(mod) or {}
            if field_present_in_module(mod, module, fn):
                meta["available_count"] += 1
                meta["source_count"] += count_sources(module)
            else:
                meta["null_count"] += 1

    rows: List[Dict[str, Any]] = []
    for meta in sorted(field_meta.values(), key=lambda r: (r["module"], r["field_name"])):
        missing = meta["null_count"]
        rows.append({
            "field_name": meta["field_name"],
            "module": meta["module"],
            "available_count": meta["available_count"],
            "null_count": missing,
            "missing_rate": round(missing / total, 4) if total else 0.0,
            "source_count": meta["source_count"],
        })
    return rows


def detect_schema_drift(
    snapshots: Dict[str, Dict[str, Any]],
) -> List[Dict[str, str]]:
    """跨公司模块字段键漂移检测。"""
    flags: List[Dict[str, str]] = []
    module_keys: Dict[str, List[Tuple[str, Set[str]]]] = defaultdict(list)

    for code, snap in snapshots.items():
        for mod in SNAPSHOT_MODULES:
            module = (snap.get("modules") or {}).get(mod) or {}
            keys = extract_module_field_keys(mod, module)
            if keys:
                module_keys[mod].append((code, keys))

    for mod, entries in module_keys.items():
        if len(entries) < 2:
            continue
        union: Set[str] = set()
        for _, keys in entries:
            union |= keys
        ref_code, ref_keys = max(entries, key=lambda x: len(x[1]))
        for code, keys in entries:
            if keys and keys != union and len(union - keys) > 2:
                missing = sorted(union - keys)[:8]
                flags.append({
                    "company_code": code,
                    "module": mod,
                    "flag_type": "schema_drift",
                    "flag_detail": f"missing_keys={missing} ref={ref_code}",
                    "severity": "info",
                })
                break
    return flags


def detect_quality_flags(
    snapshots: Dict[str, Dict[str, Any]],
    mapping_rows: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    flags: List[Dict[str, str]] = []
    core_fields = [
        (r["snapshot_module"], r["normalized_field_name"])
        for r in mapping_rows
        if r["current_status"] == "normalized_core"
    ]

    for code, snap in snapshots.items():
        modules = snap.get("modules") or {}

        if not _is_meaningful(snap.get("company_code")):
            flags.append({
                "company_code": code,
                "module": "__snapshot__",
                "flag_type": "unexpected_value",
                "flag_detail": "company_code empty or missing",
                "severity": "high",
            })

        for mod in SNAPSHOT_MODULES:
            module = modules.get(mod) or {}
            st = module.get("status", "missing")
            fields = module.get("fields") or {}
            sources = module.get("sources") or []

            if st in {"available", "partial"} and not fields and mod not in ARRAY_MODULE_KEYS:
                flags.append({
                    "company_code": code,
                    "module": mod,
                    "flag_type": "empty_module",
                    "flag_detail": f"status={st} but fields empty",
                    "severity": "medium",
                })

            array_key = ARRAY_MODULE_KEYS.get(mod)
            if st in {"available", "partial"} and array_key:
                items = fields.get(array_key) or []
                if not items:
                    flags.append({
                        "company_code": code,
                        "module": mod,
                        "flag_type": "empty_module",
                        "flag_detail": f"status={st} but {array_key}=[]",
                        "severity": "info",
                    })

            if st in {"available", "partial"} and not sources:
                flags.append({
                    "company_code": code,
                    "module": mod,
                    "flag_type": "source_missing",
                    "flag_detail": f"status={st} but sources=[]",
                    "severity": "medium",
                })

        for mod, fn in core_fields:
            module = modules.get(mod) or {}
            if module.get("status") == "not_available":
                continue
            if not field_present_in_module(mod, module, fn):
                flags.append({
                    "company_code": code,
                    "module": mod,
                    "flag_type": "field_missing",
                    "flag_detail": f"normalized_core field missing: {fn}",
                    "severity": "info",
                })

    flags.extend(detect_schema_drift(snapshots))
    return flags


def load_all_valid_snapshots(snapshot_dir: str = FULL_DIR) -> Dict[str, Dict[str, Any]]:
    snapshots: Dict[str, Dict[str, Any]] = {}
    for path in list_snapshot_json_paths(snapshot_dir):
        code = os.path.basename(path)[:-5]
        snap, err = load_snapshot(path)
        if snap and not err:
            snapshots[code] = snap
    return snapshots


def write_csv(path: str, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_quality_summary(
    completeness_stats: Dict[str, Any],
    module_rows: List[Dict[str, Any]],
    field_rows: List[Dict[str, Any]],
    flag_rows: List[Dict[str, str]],
    path: str = QUALITY_SUMMARY_MD,
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    flag_by_type = Counter(r["flag_type"] for r in flag_rows)
    top_missing = sorted(field_rows, key=lambda r: r["missing_rate"], reverse=True)[:20]

    lines = [
        "# CNINFO C-Class Snapshot Full Quality Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 full snapshot QA review。**无 CNINFO** · **只读 snapshot JSON** · **不修改产物**",
        "",
        "**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`",
        "",
        "# 1. Overall",
        "",
        f"snapshot_count: **{completeness_stats['snapshot_json_count']}**",
        f"valid_json_count: **{completeness_stats['valid_json_count']}**",
        f"invalid_json_count: **{completeness_stats['malformed_json_count'] + completeness_stats['empty_snapshot_count']}**",
        "",
        f"duplicate_company_code: **{len(completeness_stats.get('duplicate_company_codes', []))}**",
        "",
        "# 2. Module Coverage",
        "",
        "| module | available | partial | not_available | coverage_rate |",
        "|--------|-----------|---------|---------------|---------------|",
    ]
    for row in module_rows:
        lines.append(
            f"| {row['module']} | {row['available_count']} | "
            f"{row['partial_count']} | {row['not_available_count']} | "
            f"{row['coverage_rate']} |"
        )

    lines.extend([
        "",
        "# 3. Top Missing Fields",
        "",
        "| field | module | missing_rate | available_count |",
        "|-------|--------|--------------|-----------------|",
    ])
    for row in top_missing:
        lines.append(
            f"| {row['field_name']} | {row['module']} | {row['missing_rate']} | "
            f"{row['available_count']} |"
        )

    lines.extend([
        "",
        "# 4. Top Quality Issues",
        "",
        "| flag_type | count |",
        "|-----------|-------|",
    ])
    for ft, count in flag_by_type.most_common():
        lines.append(f"| {ft} | **{count}** |")

    rare_fields = [r for r in field_rows if 0 < r["available_count"] < 50]
    lines.extend([
        "",
        f"rare_fields (available < 50 companies): **{len(rare_fields)}**",
        "",
        "# 5. Current Status",
        "",
        "```",
        "C-class status = SNAPSHOT_GENERATED_QA_REVIEW",
        "```",
        "",
        "- snapshot 863 家已生成",
        "- QA review 完成；**非** completed / verified / testing_stable_sample",
        "",
        "# 6. Recommended Next Step",
        "",
    ])

    # 根据分析结果生成建议
    tech = next(r for r in module_rows if r["module"] == "technology_profile")
    schema_count = flag_by_type.get("schema_drift", 0)
    field_missing_count = flag_by_type.get("field_missing", 0)

    recs: List[str] = []
    if schema_count > 0 or field_missing_count > 100:
        recs.append("- **company_snapshot schema adjustment**：记录 schema_drift / field_missing；优先文档化，非阻塞 patch")
    else:
        recs.append("- **company_snapshot schema adjustment**：暂无阻塞；18 模块结构稳定")
    recs.append("- **security observe decision**：market_behavior / risk_profile 为 observe_only partial；建议单独产品决策")
    recs.append("- **BSE / abnormal side track**：26 all6 hold 未纳入 863；维持 HOLD 文档化")
    if tech["not_available_count"] == completeness_stats["valid_json_count"]:
        recs.append("- **product layer**：可进入 product layer 规划（caveat 层）；technology_profile 待 future 源")
    else:
        recs.append("- **product layer**：待 module coverage 复核后进入 product layer")

    lines.extend(recs)
    lines.extend([
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO · 未重跑 harvest",
        "- snapshot / normalized / field_inventory **未修改**",
        "- 未入库 / MinIO / RAG · 未写 verified",
    ])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def run_full_quality_review(snapshot_dir: str = FULL_DIR) -> Dict[str, Any]:
    """执行完整 QA review 流水线。"""
    mapping_rows = load_field_mapping()
    completeness_rows, completeness_stats = run_completeness_check(snapshot_dir)
    snapshots = load_all_valid_snapshots(snapshot_dir)
    module_rows = run_module_coverage(snapshots)
    field_rows = run_field_coverage(snapshots, mapping_rows)
    flag_rows = detect_quality_flags(snapshots, mapping_rows)

    write_csv(COMPLETENESS_CSV, COMPLETENESS_FIELDS, completeness_rows)
    write_csv(MODULE_COVERAGE_CSV, MODULE_COVERAGE_FIELDS, module_rows)
    write_csv(FIELD_COVERAGE_CSV, FIELD_COVERAGE_FIELDS, field_rows)
    write_csv(QUALITY_FLAGS_CSV, QUALITY_FLAG_FIELDS, flag_rows)
    write_quality_summary(completeness_stats, module_rows, field_rows, flag_rows)

    return {
        "completeness_stats": completeness_stats,
        "completeness_rows": completeness_rows,
        "module_rows": module_rows,
        "field_rows": field_rows,
        "flag_rows": flag_rows,
        "snapshot_count": len(snapshots),
    }


def main() -> int:
    result = run_full_quality_review()
    stats = result["completeness_stats"]
    print(f"snapshot_json_count: {stats['snapshot_json_count']}")
    print(f"valid_json_count: {stats['valid_json_count']}")
    print(f"quality_flags: {len(result['flag_rows'])}")
    print(f"completeness_report: {COMPLETENESS_CSV}")
    print(f"module_coverage: {MODULE_COVERAGE_CSV}")
    print(f"field_coverage: {FIELD_COVERAGE_CSV}")
    print(f"quality_flags_csv: {QUALITY_FLAGS_CSV}")
    print(f"quality_summary: {QUALITY_SUMMARY_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
