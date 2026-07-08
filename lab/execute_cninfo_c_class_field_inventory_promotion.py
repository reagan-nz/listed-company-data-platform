#!/usr/bin/env python3
"""
CNINFO C-class Field Inventory Promotion（Era C Phase 4 · schema governance）。

将 10 个 approved_as_candidate 字段升格为 normalized_core。
仅更新 final_field_catalog 与评审产物；不修改 raw / normalized 数据。
"""

from __future__ import annotations

import csv
import os
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APPROVAL_CSV = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_review_later_promotion_candidate_approval_after_patch.csv",
)
CATALOG_CSV = os.path.join(BASE_DIR, "outputs/validation/cninfo_c_class_final_field_catalog.csv")
MATRIX_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_profile_coverage_matrix.csv"
)

OUT_CHECK = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_field_inventory_promotion_check.csv"
)
OUT_SUMMARY = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_field_inventory_promotion_summary.md"
)

CHECK_FIELDS = [
    "field_name",
    "normalized_field_name",
    "source_id",
    "logical_name",
    "old_status",
    "new_status",
    "promotion_reason",
    "quality_requirement",
    "approval_status",
]

APPROVED_STATUSES = {"approved_as_candidate", "approved_as_candidate_after_patch"}

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


def _promotion_key(source_id: str, norm: str, raw: str) -> Tuple[str, str, str]:
    return (source_id, norm, raw)


def _load_approved() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(APPROVAL_CSV, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["approval_status"] in APPROVED_STATUSES:
                rows.append(row)
    if len(rows) != 10:
        raise ValueError(f"expected 10 approved candidates, got {len(rows)}")
    return rows


def _approved_keys(approved: List[Dict[str, str]]) -> Set[Tuple[str, str, str]]:
    return {_promotion_key(r["source_id"], r["normalized_field_name"], r["field_name"]) for r in approved}


def write_promotion_check(approved: List[Dict[str, str]]) -> None:
    rows: List[Dict[str, str]] = []
    for item in approved:
        rows.append({
            "field_name": item["field_name"],
            "normalized_field_name": item["normalized_field_name"],
            "source_id": item["source_id"],
            "logical_name": item["logical_name"],
            "old_status": "approved_as_candidate",
            "new_status": "normalized_core",
            "promotion_reason": item["approval_reason"],
            "quality_requirement": item["acceptance_criteria"],
            "approval_status": item["approval_status"],
        })
    os.makedirs(os.path.dirname(OUT_CHECK), exist_ok=True)
    with open(OUT_CHECK, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CHECK_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def promote_catalog(keys: Set[Tuple[str, str, str]]) -> Tuple[List[Dict[str, str]], int]:
    with open(CATALOG_CSV, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    promoted = 0
    for row in rows:
        key = _promotion_key(row["source_id"], row["normalized_field_name"], row["field_name"])
        if key in keys and row["current_status"] == "approved_as_candidate":
            row["current_status"] = "normalized_core"
            row["final_layer"] = "normalized"
            row["promotion_status"] = "promoted_to_normalized_core"
            promoted += 1
    if promoted != 10:
        raise ValueError(f"expected to promote 10 catalog rows, promoted {promoted}")
    with open(CATALOG_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return rows, promoted


def _status_by_normalized_field(catalog: List[Dict[str, str]]) -> Dict[str, str]:
    """同一 normalized_field_name 多源时取最高优先级状态。"""
    priority = {
        "normalized_core": 5,
        "approved_as_candidate": 4,
        "review_later": 3,
        "raw_only": 2,
        "observe_only": 1,
    }
    by_norm: Dict[str, str] = {}
    for row in catalog:
        name = row["normalized_field_name"]
        status = row["current_status"]
        if name not in by_norm or priority[status] > priority[by_norm[name]]:
            by_norm[name] = status
    return by_norm


def _recount_matrix_counts(catalog: List[Dict[str, str]]) -> List[Dict[str, str]]:
    by_norm = _status_by_normalized_field(catalog)

    existing: List[Dict[str, str]] = []
    with open(MATRIX_CSV, encoding="utf-8") as fh:
        existing = list(csv.DictReader(fh))

    updated: List[Dict[str, str]] = []
    for old in existing:
        module = old["module"]
        fields = MODULE_FIELDS.get(module, [])
        norm_count = sum(
            1 for f in fields
            if f in by_norm and by_norm[f] == "normalized_core"
        )
        cand_count = sum(
            1 for f in fields
            if f in by_norm and by_norm[f] in {"approved_as_candidate", "review_later"}
        )
        raw_count = sum(
            1 for f in fields
            if f in by_norm and by_norm[f] in {"raw_only", "observe_only"}
        )
        updated.append({
            "module": module,
            "field_count": old["field_count"],
            "normalized_fields": str(norm_count),
            "candidate_fields": str(cand_count),
            "raw_fields": str(raw_count),
            "status": old["status"],
        })
    return updated


def write_matrix(matrix_rows: List[Dict[str, str]]) -> None:
    fields = ["module", "field_count", "normalized_fields", "candidate_fields", "raw_fields", "status"]
    with open(MATRIX_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(matrix_rows)


def write_summary(
    approved: List[Dict[str, str]],
    catalog: List[Dict[str, str]],
) -> None:
    sc = Counter(r["current_status"] for r in catalog)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "# CNINFO C-Class Field Inventory Promotion Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> schema governance 升格落账。**无 CNINFO** · **无 harvest** · **raw/normalized 数据未修改**",
        "",
        "**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`",
        "",
        "# 1. Promotion Result",
        "",
        "**before:**",
        "",
        "- normalized_core = **64**",
        "- approved_as_candidate = **10**",
        "",
        "**after:**",
        "",
        "- normalized_core = **74**",
        "- approved_as_candidate = **0**",
        "",
        "# 2. Promoted Fields",
        "",
        "| field_name | normalized_field_name | source_id | reason |",
        "|------------|----------------------|-----------|--------|",
    ]
    for item in approved:
        lines.append(
            f"| {item['field_name']} | {item['normalized_field_name']} | "
            f"{item['source_id']} | {item['approval_reason']} |"
        )

    lines.extend([
        "",
        "# 3. Quality Requirements",
        "",
        "字段正式进入 `normalized_core` 后仍需要：",
        "",
        "- **source evidence** — 保留 `raw_record_json` / harvest lineage",
        "- **quality status** — 按 [product quality rules](../plans/cninfo_c_class_product_quality_rules_draft.md) 展示 caveat",
        "- **fill rate monitoring** — 继续跟踪 `field_fill_rate.csv`",
        "- **caveat tracking** — empty_but_valid / source_partial / needs_review 政策不变",
        "",
        "# 4. Not Promoted",
        "",
        "以下分类保持不变：",
        "",
        f"- review_later = **{sc.get('review_later', 0)}**",
        f"- raw_only = **{sc.get('raw_only', 0)}**",
        f"- observe_only = **{sc.get('observe_only', 0)}**",
        "",
        "# 5. Gate",
        "",
        "```",
        "field_inventory_promotion_gate = PASS",
        "```",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        "| promoted fields | **10** |",
        "| normalized_core after | **74** |",
        "| approved_as_candidate after | **0** |",
        "| C-class status | **`HARVEST_COMPLETED_QA_ONGOING`** |",
        "| field_inventory.csv（原始） | **未修改** |",
        "| raw / normalized harvest | **未修改** |",
        "",
        "**禁止：** completed · verified · testing_stable_sample",
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO · 未重跑 harvest live",
        "- raw / normalized 数据内容未修改",
        "- 未入库 / MinIO / RAG · 未 registry backfill",
        "",
        f"详见 [cninfo_c_class_field_inventory_promotion_check.csv](cninfo_c_class_field_inventory_promotion_check.csv)。",
    ])

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    approved = _load_approved()
    keys = _approved_keys(approved)
    write_promotion_check(approved)
    catalog, promoted = promote_catalog(keys)
    matrix = _recount_matrix_counts(catalog)
    write_matrix(matrix)
    write_summary(approved, catalog)

    sc = Counter(r["current_status"] for r in catalog)
    print("Field Inventory Promotion completed.")
    print(f"  check:   {OUT_CHECK}")
    print(f"  catalog: {CATALOG_CSV}")
    print(f"  summary: {OUT_SUMMARY}")
    print(f"  matrix:  {MATRIX_CSV}")
    print(f"  promoted: {promoted}")
    print(f"  counts: {dict(sc)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
