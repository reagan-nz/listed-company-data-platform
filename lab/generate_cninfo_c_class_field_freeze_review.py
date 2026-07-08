#!/usr/bin/env python3
"""
CNINFO C-class Field Freeze Review 离线生成（Era C Phase 4）。

仅读取现有 inventory / promotion / policy / quality 产物，生成冻结评审文档。
不修改 field_inventory · 不请求 CNINFO · 不重跑 harvest。
"""

from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INVENTORY_CSV = os.path.join(BASE_DIR, "outputs/validation/cninfo_c_class_field_inventory.csv")
PROMOTION_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_review_later_promotion_candidate_approval_after_patch.csv",
)
RAW_ONLY_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_raw_only_field_policy_review.csv"
)
SOURCE_QUALITY_CSV = os.path.join(
    BASE_DIR, "outputs/harvest/cninfo_c_class/quality/source_quality.csv"
)

OUT_CATALOG = os.path.join(BASE_DIR, "outputs/validation/cninfo_c_class_final_field_catalog.csv")
OUT_SUMMARY = os.path.join(BASE_DIR, "outputs/validation/cninfo_c_class_field_freeze_summary.md")
OUT_PLAN = os.path.join(BASE_DIR, "plans/cninfo_c_class_field_freeze_v1.md")
OUT_MATRIX = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_profile_coverage_matrix.csv"
)

CATALOG_FIELDS = [
    "field_name",
    "normalized_field_name",
    "source_id",
    "logical_name",
    "current_status",
    "final_layer",
    "data_type",
    "description",
    "source_available",
    "quality_status",
    "promotion_status",
    "notes",
]

# promotion 批准映射：(source_id, normalized_field_name, raw_field_name)
APPROVED_KEYS: Set[Tuple[str, str, str]] = {
    ("cninfo_executive_profile", "education_candidate", "F017V"),
    ("cninfo_top_shareholders_profile", "shareholder_type_candidate", "F006V"),
    ("cninfo_top_float_shareholders_profile", "shareholder_type_candidate", "F006V"),
    ("cninfo_company_basic_profile", "establishment_date", "F010D"),
}
APPROVED_SOURCE_STATUS_SOURCES = {
    "cninfo_company_basic_profile",
    "cninfo_executive_profile",
    "cninfo_share_capital_profile",
    "cninfo_top_shareholders_profile",
    "cninfo_top_float_shareholders_profile",
    "cninfo_dividend_financing_profile",
}

# 复判建议降级为 raw_only
DOWNGRADE_RAW_KEYS: Set[Tuple[str, str]] = {
    ("cninfo_share_capital_profile", "unrestricted_share_candidate"),
    ("cninfo_share_capital_profile", "total_capital_candidate"),
}

# 模块 → normalized_field_name 列表（冻结评审覆盖矩阵）
MODULE_FIELDS: Dict[str, List[str]] = {
    "company_identity": [
        "company_code", "company_name", "legal_name", "english_name",
        "establishment_date", "listing_date", "org_id", "exchange", "listed_board",
        "legal_representative",
    ],
    "business_profile": [
        "main_business_summary", "business_scope", "company_profile_text",
        "registered_address", "office_address", "company_website",
    ],
    "industry": ["industry", "index_or_plate_labels", "listed_board"],
    "financial": [
        "registered_capital", "compensation_candidate", "total_share_capital",
        "float_share_capital", "restricted_share_capital", "holding_shares", "holding_ratio",
    ],
    "technology": [],
    "organization": [
        "person_name", "position", "gender_candidate", "birth_year_candidate",
        "board_secretary_candidate", "contact_phone", "contact_email",
    ],
    "shareholder": [
        "shareholder_name", "shareholder_type_candidate", "rank", "report_period",
    ],
    "governance": [
        "person_name", "position", "education_candidate",
        "shareholding_quantity_candidate", "term_start_candidate", "term_end_candidate",
    ],
    "capital_action": [
        "dividend_plan_text", "report_period", "cash_dividend_per_share",
        "total_share_capital", "change_reason_or_source", "change_amount_candidate",
        "announcement_date_candidate", "ex_right_dividend_date_candidate",
        "dividend_payment_date_candidate",
    ],
    "risk": [],
    "event_timeline": [
        "dividend_plan_text", "announcement_date_candidate", "report_date",
    ],
    "market_behavior": [
        "security_code", "trading_status_code", "listing_age_years_candidate",
        "is_delisted", "shanghai_hong_kong_connect_candidate",
    ],
    "investor_relation": [
        "contact_email", "contact_phone", "contact_fax", "company_website",
        "board_secretary_candidate",
    ],
    "document_evidence": ["raw_record_json", "raw_record_hash"],
    "quality_status": ["source_status", "field_confidence", "establishment_date_parse_status"],
}

PROFILE_MODULES = {
    "identity": "company_identity",
    "business": "business_profile",
    "industry": "industry",
    "financial": "financial",
    "R&D": "technology",
    "employees": "organization",
    "shareholder": "shareholder",
    "executive": "governance",
    "dividend": "capital_action",
    "risk": "risk",
    "event": "event_timeline",
    "document evidence": "document_evidence",
    "quality": "quality_status",
}


def _logical_name(source_id: str, record_level: str) -> str:
    if source_id == "cninfo_company_contact_profile":
        return "contact"
    if source_id == "cninfo_company_business_scope":
        return "business"
    if source_id == "cninfo_company_industry_profile":
        return "industry"
    if source_id == "cninfo_dividend_financing_profile":
        return "dividend_history"
    return record_level or "company"


def _is_approved_candidate(source_id: str, norm: str, raw: str) -> bool:
    if (source_id, norm, raw) in APPROVED_KEYS:
        return True
    if raw == "(lineage)" and norm == "source_status":
        return source_id in APPROVED_SOURCE_STATUS_SOURCES
    return False


def _current_status(row: Dict[str, str]) -> str:
    source_id = row["source_id"]
    source_type = row["source_type"]
    include = row["include_in_normalized_snapshot"]
    raw = row["raw_field_name"]
    norm = row["normalized_field_name"]

    if source_id == "cninfo_company_security_profile" and source_type == "observe_only":
        if raw.startswith("(lineage)") and norm in {"source_status", "field_confidence"}:
            return "review_later"
        if not raw.startswith("(lineage)"):
            return "observe_only"

    if (source_id, norm) in DOWNGRADE_RAW_KEYS:
        return "raw_only"

    if include == "yes":
        return "normalized_core"

    if include == "no":
        return "raw_only"

    if include == "review":
        if _is_approved_candidate(source_id, norm, raw):
            return "approved_as_candidate"
        return "review_later"

    return "review_later"


def _final_layer(status: str) -> str:
    if status == "normalized_core":
        return "normalized"
    if status == "approved_as_candidate":
        return "candidate"
    if status == "review_later":
        return "candidate"
    if status == "raw_only":
        return "raw"
    if status == "observe_only":
        return "observe"
    return "raw"


def _promotion_status(row: Dict[str, str], status: str) -> str:
    if status != "approved_as_candidate":
        return "not_promoted"
    raw = row["raw_field_name"]
    if raw == "F010D":
        return "approved_as_candidate_after_patch"
    return "approved_as_candidate"


def _quality_status(row: Dict[str, str]) -> str:
    ss = row.get("source_status", "")
    caveat = row.get("caveat", "")
    if ss == "observe_only":
        return "observe_only"
    if ss == "source_partial":
        return "source_partial"
    if ss == "derived_no_separate_fetch":
        return "derived_ok"
    if "empty_but_valid" in caveat:
        return "empty_but_valid_policy"
    if ss == "proceed_testing_with_caveat":
        return "proceed_with_caveat"
    if ss == "proceed_testing":
        return "proceed_testing"
    return ss or "unknown"


def _load_promotion_notes() -> Dict[Tuple[str, str, str], str]:
    notes: Dict[Tuple[str, str, str], str] = {}
    if not os.path.isfile(PROMOTION_CSV):
        return notes
    with open(PROMOTION_CSV, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row["source_id"], row["normalized_field_name"], row["field_name"])
            notes[key] = row.get("notes", "")
    return notes


def _load_raw_only_notes() -> Dict[Tuple[str, str, str], str]:
    notes: Dict[Tuple[str, str, str], str] = {}
    with open(RAW_ONLY_CSV, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row["source_id"], row["normalized_field_name"], row["field_name"])
            notes[key] = row.get("recommended_policy", "")
    return notes


def _load_source_quality() -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not os.path.isfile(SOURCE_QUALITY_CSV):
        return out
    with open(SOURCE_QUALITY_CSV, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = row["source_status_key"]
            source_id = key.split(":")[0]
            out.setdefault(source_id, key.split(":", 1)[1])
    return out


def build_catalog_rows() -> List[Dict[str, str]]:
    promo_notes = _load_promotion_notes()
    raw_notes = _load_raw_only_notes()
    rows: List[Dict[str, str]] = []

    with open(INVENTORY_CSV, encoding="utf-8") as fh:
        for inv in csv.DictReader(fh):
            status = _current_status(inv)
            raw = inv["raw_field_name"]
            norm = inv["normalized_field_name"]
            source_id = inv["source_id"]
            key = (source_id, norm, raw)

            note_parts: List[str] = []
            if key in promo_notes:
                note_parts.append(promo_notes[key])
            if key in raw_notes:
                note_parts.append(f"raw_policy={raw_notes[key]}")
            if inv.get("caveat"):
                note_parts.append(inv["caveat"])

            rows.append({
                "field_name": raw,
                "normalized_field_name": norm,
                "source_id": source_id,
                "logical_name": _logical_name(source_id, inv["record_level"]),
                "current_status": status,
                "final_layer": _final_layer(status),
                "data_type": inv["field_type"],
                "description": inv["chinese_label"],
                "source_available": "yes" if inv["source_status"] != "observe_only" else "observe_only",
                "quality_status": _quality_status(inv),
                "promotion_status": _promotion_status(inv, status),
                "notes": "; ".join(note_parts),
            })
    return rows


def write_catalog(rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(OUT_CATALOG), exist_ok=True)
    with open(OUT_CATALOG, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CATALOG_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _status_counts(rows: List[Dict[str, str]]) -> Counter:
    return Counter(r["current_status"] for r in rows)


def _source_coverage(rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    by_source: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for r in rows:
        by_source[r["source_id"]].append(r)

    result = []
    for source_id in sorted(by_source):
        items = by_source[source_id]
        sc = Counter(i["current_status"] for i in items)
        result.append({
            "source_id": source_id,
            "field_count": len(items),
            "normalized_count": sc.get("normalized_core", 0),
            "candidate_count": sc.get("approved_as_candidate", 0) + sc.get("review_later", 0),
            "review_count": sc.get("review_later", 0),
            "raw_only_count": sc.get("raw_only", 0),
            "observe_only_count": sc.get("observe_only", 0),
        })
    return result


def _module_status(rows: List[Dict[str, str]], module: str) -> str:
    field_set = set(MODULE_FIELDS.get(module, []))
    if not field_set:
        return "not_modeled"

    by_norm = {r["normalized_field_name"]: r["current_status"] for r in rows}
    matched = [by_norm[f] for f in field_set if f in by_norm]
    if not matched:
        return "not_modeled"

    normalized = sum(1 for s in matched if s == "normalized_core")
    candidate = sum(1 for s in matched if s in {"approved_as_candidate", "review_later"})
    if normalized >= len(matched) * 0.6:
        return "available"
    if normalized + candidate > 0:
        return "partial"
    return "partial"


def build_coverage_matrix(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    by_norm: Dict[str, str] = {r["normalized_field_name"]: r["current_status"] for r in rows}
    matrix: List[Dict[str, str]] = []

    for module, fields in MODULE_FIELDS.items():
        norm_fields = [f for f in fields if f in by_norm]
        norm_count = sum(1 for f in norm_fields if by_norm[f] == "normalized_core")
        cand_count = sum(
            1 for f in norm_fields
            if by_norm[f] in {"approved_as_candidate", "review_later"}
        )
        raw_count = sum(1 for f in norm_fields if by_norm[f] in {"raw_only", "observe_only"})

        if not fields:
            status = "not_modeled"
        elif norm_count >= len(fields) * 0.5 and norm_count > 0:
            status = "available"
        elif norm_count + cand_count > 0:
            status = "partial"
        else:
            status = "not_modeled" if not norm_fields else "partial"

        matrix.append({
            "module": module,
            "field_count": str(len(fields)),
            "normalized_fields": str(norm_count),
            "candidate_fields": str(cand_count),
            "raw_fields": str(raw_count),
            "status": status,
        })
    return matrix


def write_matrix(matrix: List[Dict[str, str]]) -> None:
    fields = ["module", "field_count", "normalized_fields", "candidate_fields", "raw_fields", "status"]
    os.makedirs(os.path.dirname(OUT_MATRIX), exist_ok=True)
    with open(OUT_MATRIX, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(matrix)


def write_summary(rows: List[Dict[str, str]], source_cov: List[Dict[str, Any]]) -> None:
    sc = _status_counts(rows)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    observe_field_count = sc.get("observe_only", 0)

    profile_lines = []
    for label, module in PROFILE_MODULES.items():
        status = _module_status(rows, module)
        profile_lines.append(f"| {label} | **{status}** |")

    lines = [
        "# CNINFO C-Class Field Freeze Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 Field Freeze Review。**无 CNINFO** · **无 harvest 重跑** · **field inventory 未修改**",
        "",
        "**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`",
        "",
        "# 1. Field Overview",
        "",
        "| status | count |",
        "|--------|-------|",
        f"| normalized_core | **{sc.get('normalized_core', 0)}** |",
        f"| approved_as_candidate | **{sc.get('approved_as_candidate', 0)}** |",
        f"| review_later | **{sc.get('review_later', 0)}** |",
        f"| raw_only | **{sc.get('raw_only', 0)}** |",
        f"| observe_only | **{observe_field_count}** |",
        f"| **total fields** | **{len(rows)}** |",
        "",
        "# 2. Source Coverage",
        "",
        "| source_id | field_count | normalized_count | candidate_count | review_count | raw_only_count | observe_only_count |",
        "|-----------|-------------|------------------|-----------------|--------------|----------------|---------------------|",
    ]
    for s in source_cov:
        lines.append(
            f"| {s['source_id']} | {s['field_count']} | {s['normalized_count']} | "
            f"{s['candidate_count']} | {s['review_count']} | {s['raw_only_count']} | "
            f"{s['observe_only_count']} |"
        )

    lines.extend([
        "",
        "# 3. Company Profile Coverage",
        "",
        "一个上市公司当前可覆盖的模块（基于 863 harvest normalized + raw 证据）：",
        "",
        "| module | coverage |",
        "|--------|----------|",
    ])
    lines.extend(profile_lines)

    lines.extend([
        "",
        "# 4. Known Limitations",
        "",
        "- **company_snapshot 未实现** — 尚无跨源聚合 snapshot 产物；当前为分源 normalized 文件。",
        "- **security observe-only** — `cninfo_company_security_profile` 不纳入主 company profile gate。",
        "- **BSE/abnormal side track 未覆盖** — 863 universe 不含 hold/BSE legacy/abnormal 侧轨公司。",
        "- **registry backfill 未执行** — YAML registry 未因 harvest 结果批量回填。",
        "- **review_later 未全部升级** — 13 字段仍待 mapper patch / 定义 / 产品规则。",
        "- **raw_only 未进入 normalized** — 25 字段仅保留 raw 证据或 observe 侧轨。",
        "- **10 promotion candidates 未 inventory 升格** — candidate approval 已完成，inventory `include` 列未改。",
        "- **dividend manual review queue** — 10 条 needs_review 事件待人工复核；002019/002060 parser patch 待实施。",
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO · 未重跑 harvest live",
        "- raw / normalized / field_inventory **未修改**",
        "- 未写 verified · 未升级 testing_stable_sample",
        "- 未入库 / MinIO / RAG · 未 registry backfill",
        "",
        f"详见 [cninfo_c_class_final_field_catalog.csv](cninfo_c_class_final_field_catalog.csv) · "
        f"[cninfo_c_class_field_freeze_v1.md](../../plans/cninfo_c_class_field_freeze_v1.md)。",
    ])

    os.makedirs(os.path.dirname(OUT_SUMMARY), exist_ok=True)
    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_freeze_plan(rows: List[Dict[str, str]]) -> None:
    sc = _status_counts(rows)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def field_list(status: str, limit: int = 30) -> List[str]:
        items = [r for r in rows if r["current_status"] == status]
        labels = [f"`{r['normalized_field_name']}` ({r['source_id']})" for r in items]
        if len(labels) > limit:
            return labels[:limit] + [f"... 共 {len(labels)} 项"]
        return labels

    lines = [
        "# CNINFO C-Class Field Freeze v1",
        "",
        f"_生成时间：{now}_",
        "",
        "> **Field Freeze Review** — 基于 863 harvest、QA、promotion、raw_only policy、quality rules 的字段状态冻结说明。",
        "> **不写 verified** · **不升级 testing_stable_sample** · **field inventory 未修改**。",
        "",
        "**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`",
        "",
        "---",
        "",
        "## Frozen Fields",
        "",
        f"当前已经可以作为标准字段（**{sc.get('normalized_core', 0)}** 项）：",
        "",
        "**normalized_core** — 已进入 normalized harvest 产物，可作为公司档案标准展示字段。",
        "",
    ]
    for item in field_list("normalized_core", 40):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "---",
        "",
        "## Candidate Fields",
        "",
        f"未来可能进入 normalized（**{sc.get('approved_as_candidate', 0)}** 项 approved · "
        f"**{sc.get('review_later', 0)}** 项 review queue）：",
        "",
        "### approved_as_candidate",
        "",
        "已通过 promotion candidate approval（含 establishment_date after patch），待 inventory 升格：",
        "",
    ])
    for item in field_list("approved_as_candidate"):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "---",
        "",
        "## Review Queue",
        "",
        f"等待进一步判断（**{sc.get('review_later', 0)}** 项）：",
        "",
        "**review_later** — mapper 未覆盖、语义待定义、或与 derived 源重复待产品决策。",
        "",
    ])
    for item in field_list("review_later"):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "---",
        "",
        "## Raw Evidence Only",
        "",
        f"保留原始证据（**{sc.get('raw_only', 0)}** 项）：",
        "",
        "**raw_only** — 不进主 snapshot；由 `raw_record_json` 或专用 raw 文件追溯。",
        "",
    ])
    for item in field_list("raw_only", 30):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "---",
        "",
        "## Observe Only",
        "",
        f"仅观察（**{sc.get('observe_only', 0)}** 项 · security 源）：",
        "",
        "**observe_only** — `cninfo_company_security_profile` 侧轨数据，不绑定主 harvest gate。",
        "",
    ])
    for item in field_list("observe_only"):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "---",
        "",
        "## 冻结边界",
        "",
        "| 项 | 状态 |",
        "|----|------|",
        "| field_inventory.csv | **未修改**（本冻结为评审产物） |",
        "| inventory 升格 | **未执行** |",
        "| company_snapshot | **未实现** |",
        "| harvest rerun | **不需要** |",
        "",
        "## 推荐下一步",
        "",
        "1. **field inventory 升格执行**（10 approved candidates）",
        "2. **company_snapshot planning**",
        "3. **security observe 决策** + BSE/abnormal 侧轨文档化",
        "",
    ])

    os.makedirs(os.path.dirname(OUT_PLAN), exist_ok=True)
    with open(OUT_PLAN, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    rows = build_catalog_rows()
    write_catalog(rows)
    source_cov = _source_coverage(rows)
    write_summary(rows, source_cov)
    write_freeze_plan(rows)
    write_matrix(build_coverage_matrix(rows))

    sc = _status_counts(rows)
    print("Field Freeze Review generated.")
    print(f"  catalog: {OUT_CATALOG} ({len(rows)} rows)")
    print(f"  summary: {OUT_SUMMARY}")
    print(f"  plan:    {OUT_PLAN}")
    print(f"  matrix:  {OUT_MATRIX}")
    print(f"  counts:  {dict(sc)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
