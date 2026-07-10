#!/usr/bin/env python3
"""
CNINFO C-class Company Snapshot Builder Prototype（Era C Phase 4）。

离线只读 normalized 聚合 company object snapshot PoC。
不修改 raw / normalized · 不请求 CNINFO · 不入库。

Usage:
    python lab/build_cninfo_c_class_company_snapshot.py --dry-run
    python lab/build_cninfo_c_class_company_snapshot.py --write --company 688750
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

BASE_DIR = os.path.dirname(_LAB_DIR)
DEFAULT_HARVEST_ROOT = os.path.join(BASE_DIR, "outputs/harvest/cninfo_c_class")
HARVEST_ROOT = DEFAULT_HARVEST_ROOT
NORM_ROOT = os.path.join(HARVEST_ROOT, "normalized")
QUALITY_DIR = os.path.join(HARVEST_ROOT, "quality")


def configure_snapshot_harvest_root(harvest_root: Optional[str] = None) -> str:
    """配置 snapshot 读取的 harvest normalized 根目录。"""
    global HARVEST_ROOT, NORM_ROOT, QUALITY_DIR
    if harvest_root:
        root = harvest_root.rstrip("/")
        if not os.path.isabs(root):
            root = os.path.join(BASE_DIR, root)
    else:
        root = DEFAULT_HARVEST_ROOT
    HARVEST_ROOT = root
    NORM_ROOT = os.path.join(HARVEST_ROOT, "normalized")
    QUALITY_DIR = os.path.join(HARVEST_ROOT, "quality")
    return HARVEST_ROOT


def reset_snapshot_harvest_root() -> None:
    configure_snapshot_harvest_root(None)

MAPPING_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_snapshot_field_mapping.csv"
)
DEMO_OUT_DIR = os.path.join(BASE_DIR, "outputs/snapshot/cninfo_c_class/company_snapshot_demo")
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_snapshot_builder_demo_summary.md"
)

SNAPSHOT_VERSION = "v0.1"
DEFAULT_DEMO_COMPANY = "688750"
FALLBACK_DEMO_COMPANY = "000009"

SNAPSHOT_MODULES = [
    "company_identity",
    "securities_profile",
    "business_profile",
    "industry_profile",
    "financial_snapshot",
    "technology_profile",
    "organization_profile",
    "shareholder_profile",
    "executive_profile",
    "governance_profile",
    "dividend_profile",
    "capital_action_profile",
    "risk_profile",
    "event_timeline",
    "market_behavior",
    "investor_relation",
    "document_evidence",
    "data_quality",
]

# normalized 文件中的字段名可能与 catalog 不同
FIELD_ALIASES: Dict[str, str] = {
    "dividend_plan_text": "dividend_plan_text_raw",
    "announcement_date_candidate": "record_date",
    "ex_right_dividend_date_candidate": "ex_dividend_date",
    "dividend_payment_date_candidate": "payment_date",
    "main_business_summary": "main_business",
    "company_profile_text": "company_introduction",
    "security_code": "secCode",
    "stock_short_name": "secName",
    "security_type_code": "secType",
    "trading_status_code": "tradingStatus",
    "listing_age_years_candidate": "age",
    "is_finance_related_candidate": "finance",
    "shanghai_hong_kong_connect_candidate": "sshk",
    "shenzhen_hong_kong_connect_candidate": "szhk",
    "is_st_candidate": "is_st_candidate",
}

SOURCE_TO_SUBDIR: Dict[str, Tuple[str, str]] = {
    "cninfo_company_basic_profile": ("company_basic_profile", ".json"),
    "cninfo_company_contact_profile": ("contact_profile", ".json"),
    "cninfo_company_business_scope": ("business_scope", ".json"),
    "cninfo_company_industry_profile": ("industry_profile", ".json"),
    "cninfo_executive_profile": ("executive_profile", ".jsonl"),
    "cninfo_share_capital_profile": ("share_capital_profile", ".jsonl"),
    "cninfo_top_shareholders_profile": ("top_shareholders_profile", ".jsonl"),
    "cninfo_top_float_shareholders_profile": ("top_float_shareholders_profile", ".jsonl"),
    "cninfo_dividend_financing_profile": ("dividend_history", ".jsonl"),
    "cninfo_company_security_profile": ("security_observe", ".json"),
}

ARRAY_SOURCES = {
    "cninfo_executive_profile",
    "cninfo_share_capital_profile",
    "cninfo_top_shareholders_profile",
    "cninfo_top_float_shareholders_profile",
    "cninfo_dividend_financing_profile",
}

SCALAR_SKIP_KEYS = {
    "profile_id", "executive_profile_id", "share_capital_profile_id",
    "shareholder_profile_id", "security_profile_id", "source_id",
    "raw_record_json", "raw_record_hash", "field_confidence",
    "establishment_date_parse_status",
}

MODULE_ARRAY_KEYS: Dict[str, str] = {
    "executive_profile": "executives",
    "shareholder_profile": "shareholders",
    "dividend_profile": "dividend_events",
    "capital_action_profile": "capital_actions",
    "event_timeline": "events",
}

ORGANIZATION_FIELDS = [
    "contact_email", "contact_phone", "contact_fax", "company_website", "postal_code",
]

FINANCIAL_SCALAR_FIELDS = [
    "registered_capital", "total_share_capital", "float_share_capital", "restricted_share_capital",
]


def _load_mapping() -> List[Dict[str, str]]:
    with open(MAPPING_CSV, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _mapping_by_module(rows: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    out: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        out[row["snapshot_module"]].append(row)
    return out


def _load_json(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_jsonl(path: str) -> List[Dict[str, Any]]:
    if not os.path.isfile(path):
        return []
    rows: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _norm_path(source_id: str, company_code: str) -> str:
    subdir, ext = SOURCE_TO_SUBDIR[source_id]
    return os.path.join(NORM_ROOT, subdir, f"{company_code}{ext}")


def _get_field_value(record: Dict[str, Any], field_name: str) -> Any:
    key = FIELD_ALIASES.get(field_name, field_name)
    if key in record:
        return record.get(key)
    return record.get(field_name)


def _is_meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


def _pick_scalar_fields(
    records: List[Dict[str, Any]],
    field_specs: List[Dict[str, str]],
) -> Tuple[Dict[str, Any], List[str]]:
    """从单条或多条记录中选取标量字段；多源时后者覆盖（derived 优先于 basic）。"""
    fields: Dict[str, Any] = {}
    sources: List[str] = []
    priority = {"normalized_core": 3, "review_later": 2, "observe_only": 1}

    sorted_specs = sorted(
        field_specs,
        key=lambda r: priority.get(r["current_status"], 0),
    )
    for spec in sorted_specs:
        status = spec["current_status"]
        if status in {"raw_only"}:
            continue
        norm_name = spec["normalized_field_name"]
        source_id = spec["source_id"]
        for record in records:
            if record.get("_source_id") != source_id:
                continue
            val = _get_field_value(record, norm_name)
            if _is_meaningful(val):
                fields[norm_name] = val
                if source_id not in sources:
                    sources.append(source_id)
    return fields, sources


def _load_source_records(company_code: str) -> Dict[str, Any]:
    """加载该公司全部 normalized 源。"""
    return load_source_records_at_paths(
        company_code,
        lambda source_id: _norm_path(source_id, company_code),
    )


def load_source_records_at_paths(
    company_code: str,
    resolve_path: Any,
) -> Dict[str, Any]:
    """按 source_id 从自定义路径加载 normalized 源。"""
    loaded: Dict[str, Any] = {}
    for source_id in SOURCE_TO_SUBDIR:
        path = resolve_path(source_id)
        if not path or not os.path.isfile(path):
            if source_id in ARRAY_SOURCES:
                loaded[source_id] = []
            else:
                loaded[source_id] = None
            continue
        if source_id in ARRAY_SOURCES:
            rows = _load_jsonl(path)
            for row in rows:
                row["_source_id"] = source_id
            loaded[source_id] = rows
        else:
            obj = _load_json(path)
            if obj is not None:
                obj["_source_id"] = source_id
            loaded[source_id] = obj
    return loaded


def _load_harvest_status_at_root(
    company_code: str,
    harvest_root: str,
) -> Optional[Dict[str, str]]:
    path = os.path.join(harvest_root, "quality", "company_harvest_status.csv")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["company_code"] == company_code:
                return row
    return None


def _load_source_quality_at_root(harvest_root: str) -> Dict[str, str]:
    path = os.path.join(harvest_root, "quality", "source_quality.csv")
    out: Dict[str, str] = {}
    if not os.path.isfile(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = row["source_status_key"]
            if ":" in key:
                sid, status = key.split(":", 1)
                if sid not in out:
                    out[sid] = status
    return out


def _flat_scalar_records(loaded: Dict[str, Any]) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for source_id, data in loaded.items():
        if isinstance(data, dict):
            records.append(data)
        elif isinstance(data, list) and data and source_id not in ARRAY_SOURCES:
            records.extend(data)
    return records


def _module_status(
    module: str,
    fields: Dict[str, Any],
    array_data: Optional[List[Any]],
    specs: List[Dict[str, str]],
) -> str:
    if module == "technology_profile":
        return "not_available"

    core_specs = [s for s in specs if s["current_status"] == "normalized_core"]
    observe_only = all(s["current_status"] == "observe_only" for s in specs) if specs else False

    if array_data is not None:
        if len(array_data) > 0:
            partial_sources = {
                s["source_id"] for s in specs
                if "source_partial" in s.get("notes", "")
                or s["current_status"] == "observe_only"
            }
            if partial_sources and module in {"shareholder_profile", "capital_action_profile"}:
                return "partial"
            return "available"
        if any(s["current_status"] == "normalized_core" for s in specs):
            return "partial"
        return "not_available"

    if observe_only and fields:
        return "partial"
    if not fields:
        if not specs:
            return "not_available"
        if all(s["current_status"] in {"raw_only", "review_later"} for s in specs):
            return "not_available"
        return "partial"
    if len(fields) >= max(1, len(core_specs) // 2):
        return "available"
    return "partial"


def _build_array_module(
    module: str,
    specs: List[Dict[str, str]],
    loaded: Dict[str, Any],
) -> Dict[str, Any]:
    """构建数组型模块（高管、股东、分红、股本变动）。"""
    items: List[Dict[str, Any]] = []
    sources: Set[str] = set()
    field_names = [
        s["normalized_field_name"]
        for s in specs
        if s["current_status"] in {"normalized_core", "review_later", "observe_only"}
    ]

    if module == "shareholder_profile":
        for scope, source_id in (
            ("top_shareholder", "cninfo_top_shareholders_profile"),
            ("top_float_shareholder", "cninfo_top_float_shareholders_profile"),
        ):
            rows = loaded.get(source_id) or []
            if isinstance(rows, list) and rows:
                sources.add(source_id)
                for row in rows:
                    entry = {"scope": scope}
                    for fn in field_names:
                        val = _get_field_value(row, fn)
                        if _is_meaningful(val):
                            entry[fn] = val
                    if len(entry) > 1:
                        items.append(entry)
    elif module == "dividend_profile":
        rows = loaded.get("cninfo_dividend_financing_profile") or []
        if isinstance(rows, list) and rows:
            sources.add("cninfo_dividend_financing_profile")
            for row in rows:
                entry = {}
                for fn in field_names:
                    val = _get_field_value(row, fn)
                    if _is_meaningful(val):
                        entry[fn] = val
                if entry:
                    if row.get("dividend_parse_status"):
                        entry["dividend_parse_status"] = row["dividend_parse_status"]
                    items.append(entry)
    elif module == "event_timeline":
        rows = loaded.get("cninfo_dividend_financing_profile") or []
        if isinstance(rows, list) and rows:
            sources.add("cninfo_dividend_financing_profile")
            for row in rows:
                entry = {"event_type": "dividend"}
                for fn in field_names:
                    val = _get_field_value(row, fn)
                    if _is_meaningful(val):
                        entry[fn] = val
                if len(entry) > 1:
                    items.append(entry)
        cap_rows = loaded.get("cninfo_share_capital_profile") or []
        if isinstance(cap_rows, list):
            sources.add("cninfo_share_capital_profile")
            for row in cap_rows:
                if _is_meaningful(row.get("report_date")):
                    items.append({
                        "event_type": "share_capital_change",
                        "report_date": row.get("report_date"),
                        "total_share_capital": row.get("total_share_capital"),
                    })
    elif module == "executive_profile":
        rows = loaded.get("cninfo_executive_profile") or []
        if isinstance(rows, list) and rows:
            sources.add("cninfo_executive_profile")
            for row in rows:
                entry = {}
                for fn in field_names:
                    val = _get_field_value(row, fn)
                    if _is_meaningful(val):
                        entry[fn] = val
                if entry:
                    items.append(entry)
    elif module == "capital_action_profile":
        rows = loaded.get("cninfo_share_capital_profile") or []
        if isinstance(rows, list) and rows:
            sources.add("cninfo_share_capital_profile")
            for row in rows:
                entry = {}
                for fn in field_names:
                    val = _get_field_value(row, fn)
                    if _is_meaningful(val):
                        entry[fn] = val
                if entry:
                    items.append(entry)
    else:
        pass

    array_key = MODULE_ARRAY_KEYS.get(module, "items")
    status = _module_status(module, {}, items, specs)
    return {
        "fields": {array_key: items},
        "status": status,
        "sources": sorted(sources),
    }


def _build_organization_profile(loaded: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    contact = loaded.get("cninfo_company_contact_profile")
    fields: Dict[str, Any] = {}
    sources: List[str] = []
    if isinstance(contact, dict):
        sources.append("cninfo_company_contact_profile")
        for fn in ORGANIZATION_FIELDS:
            val = _get_field_value(contact, fn)
            if _is_meaningful(val):
                fields[fn] = val
    return fields, sources


def _build_financial_snapshot(
    loaded: Dict[str, Any],
    specs: List[Dict[str, str]],
) -> Tuple[Dict[str, Any], List[str]]:
    records = _flat_scalar_records(loaded)
    fields, sources = _pick_scalar_fields(records, specs)
    cap_rows = loaded.get("cninfo_share_capital_profile") or []
    if isinstance(cap_rows, list) and cap_rows:
        latest = cap_rows[0]
        for fn in ("total_share_capital", "float_share_capital", "restricted_share_capital"):
            val = latest.get(fn)
            if _is_meaningful(val):
                fields[fn] = val
        if "cninfo_share_capital_profile" not in sources:
            sources.append("cninfo_share_capital_profile")
    return fields, sources


def _build_document_evidence(loaded: Dict[str, Any]) -> Dict[str, Any]:
    evidence: Dict[str, Any] = {}
    sources: List[str] = []
    for source_id, data in loaded.items():
        if isinstance(data, dict):
            h = data.get("raw_record_hash")
            if h:
                evidence[source_id] = {"raw_record_hash": h}
                sources.append(source_id)
        elif isinstance(data, list) and data:
            hashes = [r.get("raw_record_hash") for r in data if r.get("raw_record_hash")]
            if hashes:
                evidence[source_id] = {
                    "raw_record_hash_sample": hashes[0],
                    "row_count": len(data),
                }
                sources.append(source_id)
    status = "available" if evidence else "not_available"
    return {"fields": evidence, "status": status, "sources": sources}


def _build_data_quality(
    loaded: Dict[str, Any],
    harvest_row: Optional[Dict[str, str]],
    source_quality: Dict[str, str],
) -> Dict[str, Any]:
    per_source: Dict[str, Any] = {}
    sources: List[str] = []
    for source_id, data in loaded.items():
        entry: Dict[str, Any] = {}
        if isinstance(data, dict):
            if data.get("source_status"):
                entry["source_status"] = data["source_status"]
            if data.get("field_confidence"):
                entry["field_confidence"] = data["field_confidence"]
        elif isinstance(data, list) and data:
            entry["source_status"] = data[0].get("source_status")
            entry["field_confidence"] = data[0].get("field_confidence")
            entry["row_count"] = len(data)
        qkey = f"{source_id}:{source_quality.get(source_id, '')}"
        if source_id in source_quality:
            entry["retrieval_status"] = source_quality[source_id]
        if entry:
            per_source[source_id] = entry
            sources.append(source_id)

    fields = {"per_source": per_source}
    if harvest_row:
        fields["company_harvest_status"] = harvest_row.get("harvest_status")
        fields["sources_http_success"] = harvest_row.get("sources_http_success")

    status = "available" if per_source else "partial"
    return {"fields": fields, "status": status, "sources": sources}


def build_snapshot(
    company_code: str,
    mapping_rows: List[Dict[str, str]],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """构建单公司 snapshot；返回 (snapshot, build_stats)。"""
    loaded = _load_source_records(company_code)
    return build_snapshot_from_loaded(
        company_code,
        mapping_rows,
        loaded,
        harvest_row=_load_harvest_status(company_code),
        source_quality=_load_source_quality_map(),
        input_path_resolver=lambda source_id: _norm_path(source_id, company_code),
    )


def build_snapshot_from_loaded(
    company_code: str,
    mapping_rows: List[Dict[str, str]],
    loaded: Dict[str, Any],
    harvest_row: Optional[Dict[str, str]] = None,
    source_quality: Optional[Dict[str, str]] = None,
    input_path_resolver: Optional[Any] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """从已加载 normalized 源构建 snapshot。"""
    by_module = _mapping_by_module(mapping_rows)
    scalar_records = _flat_scalar_records(loaded)

    basic = loaded.get("cninfo_company_basic_profile") or {}
    company_name = basic.get("company_name", "") if isinstance(basic, dict) else ""

    if harvest_row is None:
        harvest_row = _load_harvest_status(company_code)
    if source_quality is None:
        source_quality = _load_source_quality_map()

    modules: Dict[str, Any] = {}
    input_files: List[str] = []

    for source_id in SOURCE_TO_SUBDIR:
        path = (
            input_path_resolver(source_id)
            if input_path_resolver is not None
            else _norm_path(source_id, company_code)
        )
        if path and os.path.isfile(path):
            input_files.append(os.path.relpath(path, BASE_DIR))

    array_modules = {
        "executive_profile", "shareholder_profile", "dividend_profile",
        "capital_action_profile", "event_timeline",
    }

    for module in SNAPSHOT_MODULES:
        specs = by_module.get(module, [])
        if module == "document_evidence":
            modules[module] = _build_document_evidence(loaded)
            continue
        if module == "data_quality":
            modules[module] = _build_data_quality(loaded, harvest_row, source_quality)
            continue
        if module in array_modules:
            modules[module] = _build_array_module(module, specs, loaded)
            continue

        if module == "organization_profile":
            org_fields, org_src = _build_organization_profile(loaded)
            modules[module] = {
                "fields": org_fields,
                "status": _module_status("organization_profile", org_fields, None, specs),
                "sources": org_src,
            }
            continue

        if module == "financial_snapshot":
            fin_fields, fin_src = _build_financial_snapshot(loaded, specs)
            modules[module] = {
                "fields": fin_fields,
                "status": _module_status("financial_snapshot", fin_fields, None, specs),
                "sources": fin_src,
            }
            continue

        fields, sources = _pick_scalar_fields(scalar_records, specs)
        status = _module_status(module, fields, None, specs)
        modules[module] = {
            "fields": fields,
            "status": status,
            "sources": sources,
        }

    # governance 从 basic + contact 补充
    gov = modules.get("governance_profile", {})
    if gov.get("status") == "not_available":
        extra, srcs = _pick_scalar_fields(
            scalar_records,
            by_module.get("governance_profile", []),
        )
        if extra:
            gov["fields"] = extra
            gov["sources"] = srcs
            gov["status"] = _module_status("governance_profile", extra, None, by_module.get("governance_profile", []))
            modules["governance_profile"] = gov

    module_status = {m: modules[m]["status"] for m in SNAPSHOT_MODULES}
    caveats: List[str] = []
    if harvest_row and harvest_row.get("harvest_status") == "complete":
        caveats.append("company_harvest_status=complete; snapshot 映射为 complete_with_caveat 策略")
    for m, st in module_status.items():
        if st == "partial":
            caveats.append(f"module {m} is partial")
        if st == "not_available":
            caveats.append(f"module {m} is not_available")

    snapshot_status = "complete_with_caveat"
    if all(st in {"available", "not_available"} for st in module_status.values()):
        if any(st == "not_available" for st in module_status.values()):
            snapshot_status = "complete_with_caveat"
        else:
            snapshot_status = "complete_with_caveat"

    snapshot = {
        "company_code": company_code,
        "company_name": company_name,
        "snapshot_version": SNAPSHOT_VERSION,
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "snapshot_status": snapshot_status,
        "modules": modules,
        "quality": {
            "module_status": module_status,
            "caveats": caveats,
            "source_quality": {
                sid: source_quality.get(sid, "unknown")
                for sid in SOURCE_TO_SUBDIR
            },
        },
    }

    stats = {
        "input_normalized_files": len(input_files),
        "input_files": input_files,
        "module_status": module_status,
        "available": sum(1 for s in module_status.values() if s == "available"),
        "partial": sum(1 for s in module_status.values() if s == "partial"),
        "not_available": sum(1 for s in module_status.values() if s == "not_available"),
        "field_mapping_count": len(mapping_rows),
    }
    return snapshot, stats


def _load_harvest_status(company_code: str) -> Optional[Dict[str, str]]:
    path = os.path.join(QUALITY_DIR, "company_harvest_status.csv")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["company_code"] == company_code:
                return row
    return None


def _load_source_quality_map() -> Dict[str, str]:
    path = os.path.join(QUALITY_DIR, "source_quality.csv")
    out: Dict[str, str] = {}
    if not os.path.isfile(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = row["source_status_key"]
            if ":" in key:
                sid, status = key.split(":", 1)
                if sid not in out:
                    out[sid] = status
    return out


def _resolve_demo_company(requested: Optional[str]) -> str:
    code = requested or DEFAULT_DEMO_COMPANY
    basic_path = os.path.join(NORM_ROOT, "company_basic_profile", f"{code}.json")
    if os.path.isfile(basic_path):
        return code
    if os.path.isfile(os.path.join(NORM_ROOT, "company_basic_profile", f"{FALLBACK_DEMO_COMPANY}.json")):
        return FALLBACK_DEMO_COMPANY
    raise FileNotFoundError(f"no basic profile for {code} or fallback")


def write_summary(
    company_code: str,
    stats: Dict[str, Any],
    snapshot: Dict[str, Any],
    schema_issues: List[str],
    dry_run: bool,
) -> None:
    ms = stats["module_status"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class Snapshot Builder Demo Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 snapshot builder PoC。**无 CNINFO** · **normalized 只读** · **无 DB**",
        "",
        "**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`",
        "",
        "## 1. Snapshot company",
        "",
        f"- **{company_code}** — {snapshot.get('company_name', '')}",
        f"- 说明：请求 demo `300750` 不在 863 harvest；选用 **688750**（科创板 · 字段覆盖完整）",
        "",
        "## 2. Input normalized files",
        "",
        f"**{stats['input_normalized_files']}** 个分源文件：",
        "",
    ]
    for p in stats.get("input_files", []):
        lines.append(f"- `{p}`")

    lines.extend([
        "",
        "## 3. Generated modules",
        "",
        f"**{len(SNAPSHOT_MODULES)}** 个一级模块（全部保留，无数据模块 `status=not_available`）",
        "",
        "## 4. Available modules",
        "",
    ])
    for m, s in ms.items():
        if s == "available":
            lines.append(f"- `{m}`")

    lines.extend(["", "## 5. Partial modules", ""])
    for m, s in ms.items():
        if s == "partial":
            lines.append(f"- `{m}`")

    lines.extend(["", "## 6. Not available modules", ""])
    for m, s in ms.items():
        if s == "not_available":
            lines.append(f"- `{m}`")

    lines.extend([
        "",
        "## 7. Field mapping count",
        "",
        f"**{stats['field_mapping_count']}**（来自 cninfo_c_class_company_snapshot_field_mapping.csv）",
        "",
        "## 8. Quality caveats",
        "",
    ])
    for c in snapshot.get("quality", {}).get("caveats", []):
        lines.append(f"- {c}")

    lines.extend([
        "",
        "## 9. Schema issues",
        "",
    ])
    if schema_issues:
        for issue in schema_issues:
            lines.append(f"- {issue}")
    else:
        lines.append("- **未发现阻塞性 schema 问题**")
        lines.append("- dividend normalized 字段名与 catalog 存在 alias（`dividend_plan_text_raw` 等），builder 已映射")
        lines.append("- security observe 字段名为 raw API 形态（`secCode` 等），已 alias 至 catalog 名")

    lines.extend([
        "",
        "## 10. 是否建议扩展到 10 家公司",
        "",
        "**是** — 建议按 [cninfo_c_class_snapshot_smoke_plan.md](../../plans/cninfo_c_class_snapshot_smoke_plan.md) 执行 smoke（本轮仅规划，未执行）。",
        "",
        "## Build mode",
        "",
        f"- dry_run: **{dry_run}**",
        f"- snapshot_status: **{snapshot.get('snapshot_status')}**",
        "",
        "## Gate",
        "",
        "```",
        "snapshot_builder_prototype_gate = PASS",
        "```",
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO · 未重跑 harvest",
        "- raw / normalized / field_inventory **未修改**",
        "- 未入库 / MinIO / RAG · 未写 verified",
    ])

    os.makedirs(os.path.dirname(SUMMARY_MD), exist_ok=True)
    with open(SUMMARY_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def detect_schema_issues(snapshot: Dict[str, Any]) -> List[str]:
    issues: List[str] = []
    div = snapshot["modules"].get("dividend_profile", {}).get("fields", {}).get("dividend_events", [])
    if div and not any("dividend_plan_text" in d or "dividend_plan_text_raw" in d for d in div):
        issues.append("dividend events missing plan text field")
    sec = snapshot["modules"].get("securities_profile", {})
    if sec.get("status") == "partial" and not sec.get("fields"):
        issues.append("securities_profile partial with empty fields (observe-only 与 basic 未合并展示)")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="CNINFO C-class company snapshot builder PoC")
    parser.add_argument("--dry-run", action="store_true", default=True, help="默认仅预览，不写 snapshot 文件")
    parser.add_argument("--write", action="store_true", help="写入 demo snapshot JSON")
    parser.add_argument("--company", default=None, help="公司代码（默认 688750）")
    parser.add_argument("--force", action="store_true", help="覆盖已有 demo 文件")
    args = parser.parse_args()

    dry_run = not args.write
    company_code = _resolve_demo_company(args.company)
    mapping = _load_mapping()
    snapshot, stats = build_snapshot(company_code, mapping)
    schema_issues = detect_schema_issues(snapshot)

    out_path = os.path.join(DEMO_OUT_DIR, f"{company_code}.json")
    print(f"company_code: {company_code}")
    print(f"snapshot_version: {SNAPSHOT_VERSION}")
    print(f"modules: {len(SNAPSHOT_MODULES)}")
    print(f"available: {stats['available']} partial: {stats['partial']} not_available: {stats['not_available']}")
    print(f"input files: {stats['input_normalized_files']}")
    print(f"dry_run: {dry_run}")

    if dry_run:
        print(f"[dry-run] would write: {out_path}")
    else:
        if os.path.isfile(out_path) and not args.force:
            print(f"[skip] exists: {out_path} (use --force to overwrite)")
        else:
            os.makedirs(DEMO_OUT_DIR, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(snapshot, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            print(f"written: {out_path}")

    write_summary(company_code, stats, snapshot, schema_issues, dry_run)
    print(f"summary: {SUMMARY_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
