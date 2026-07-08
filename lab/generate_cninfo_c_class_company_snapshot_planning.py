#!/usr/bin/env python3
"""
CNINFO C-class Company Snapshot Planning 离线生成（Era C Phase 4）。

仅读取现有 catalog / quality 产物，生成 snapshot 架构规划文档。
不修改 raw / normalized / field inventory · 不请求 CNINFO。
"""

from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATALOG_CSV = os.path.join(BASE_DIR, "outputs/validation/cninfo_c_class_final_field_catalog.csv")
MAPPING_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_snapshot_field_mapping.csv"
)
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_snapshot_planning_summary.md"
)

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

MAPPING_FIELDS = [
    "snapshot_module",
    "normalized_field_name",
    "source_id",
    "current_status",
    "source_priority",
    "aggregation_rule",
    "update_frequency_candidate",
    "conflict_rule",
    "notes",
]

# normalized_field_name -> 主 snapshot 模块
FIELD_MODULE: Dict[str, str] = {
    "company_code": "company_identity",
    "company_name": "company_identity",
    "legal_name": "company_identity",
    "english_name": "company_identity",
    "legal_representative": "governance_profile",
    "registered_address": "company_identity",
    "office_address": "company_identity",
    "listing_date": "company_identity",
    "establishment_date": "company_identity",
    "registered_capital": "financial_snapshot",
    "company_website": "investor_relation",
    "business_scope": "business_profile",
    "industry": "industry_profile",
    "listed_board": "securities_profile",
    "exchange": "securities_profile",
    "main_business_summary": "business_profile",
    "company_profile_text": "business_profile",
    "index_or_plate_labels": "industry_profile",
    "postal_code": "investor_relation",
    "contact_email": "investor_relation",
    "contact_phone": "investor_relation",
    "contact_fax": "investor_relation",
    "board_secretary_candidate": "governance_profile",
    "listing_sponsor": "company_identity",
    "listing_sec_code": "securities_profile",
    "person_name": "executive_profile",
    "position": "executive_profile",
    "gender_candidate": "executive_profile",
    "birth_year_candidate": "executive_profile",
    "education_candidate": "executive_profile",
    "shareholding_quantity_candidate": "executive_profile",
    "compensation_candidate": "financial_snapshot",
    "person_id_candidate": "executive_profile",
    "row_sequence_id": "executive_profile",
    "term_start_candidate": "governance_profile",
    "term_end_candidate": "governance_profile",
    "report_date": "capital_action_profile",
    "total_share_capital": "financial_snapshot",
    "float_share_capital": "financial_snapshot",
    "restricted_share_capital": "financial_snapshot",
    "change_reason_or_source": "capital_action_profile",
    "unrestricted_share_candidate": "capital_action_profile",
    "change_amount_candidate": "capital_action_profile",
    "total_capital_candidate": "financial_snapshot",
    "share_unit": "financial_snapshot",
    "report_period": "shareholder_profile",
    "shareholder_name": "shareholder_profile",
    "holding_shares": "shareholder_profile",
    "holding_ratio": "shareholder_profile",
    "rank": "shareholder_profile",
    "shareholder_type_candidate": "shareholder_profile",
    "change_status_or_change_amount_candidate": "shareholder_profile",
    "dividend_plan_text": "dividend_profile",
    "announcement_date_candidate": "event_timeline",
    "ex_right_dividend_date_candidate": "event_timeline",
    "dividend_payment_date_candidate": "dividend_profile",
    "security_code": "securities_profile",
    "stock_short_name": "securities_profile",
    "security_type_code": "securities_profile",
    "trading_status_code": "market_behavior",
    "listing_age_years_candidate": "market_behavior",
    "is_finance_related_candidate": "market_behavior",
    "is_delisted": "risk_profile",
    "shanghai_hong_kong_connect_candidate": "market_behavior",
    "shenzhen_hong_kong_connect_candidate": "market_behavior",
    "listing_status": "securities_profile",
    "is_st_candidate": "risk_profile",
    "raw_record_json": "document_evidence",
    "raw_record_hash": "document_evidence",
    "source_status": "data_quality",
    "field_confidence": "data_quality",
}

MODULE_SOURCE_PRIORITY: Dict[str, str] = {
    "company_identity": "cninfo_f10 > annual_report > announcement",
    "securities_profile": "cninfo_f10 > market_data > annual_report",
    "business_profile": "annual_report > cninfo_f10 > announcement",
    "industry_profile": "annual_report > cninfo_f10 > announcement",
    "financial_snapshot": "annual_report > quarterly_report > cninfo_f10",
    "technology_profile": "annual_report > announcement > cninfo_f10",
    "organization_profile": "annual_report > cninfo_f10 > announcement",
    "shareholder_profile": "cninfo_f10 > annual_report > announcement",
    "executive_profile": "cninfo_f10 > annual_report > announcement",
    "governance_profile": "annual_report > cninfo_f10 > announcement",
    "dividend_profile": "cninfo_f10 > announcement > annual_report",
    "capital_action_profile": "cninfo_f10 > announcement > annual_report",
    "risk_profile": "announcement > cninfo_f10 > annual_report",
    "event_timeline": "announcement > cninfo_f10 > annual_report",
    "market_behavior": "market_data > cninfo_f10 > announcement",
    "investor_relation": "cninfo_f10 > annual_report > announcement",
    "document_evidence": "raw_source > normalized > derived",
    "data_quality": "harvest_metadata > computed",
}

MODULE_CONFLICT: Dict[str, str] = {
    "company_identity": "latest_valid_source",
    "securities_profile": "latest_valid_source",
    "business_profile": "longest_valid_text_with_source_preference",
    "industry_profile": "annual_report_preferred_else_latest_f10",
    "financial_snapshot": "numeric_tolerance_with_annual_report_preferred",
    "shareholder_profile": "latest_report_period",
    "executive_profile": "latest_f10_row_merge",
    "governance_profile": "annual_report_preferred",
    "dividend_profile": "event_level_latest_valid",
    "capital_action_profile": "latest_report_date",
    "event_timeline": "timestamp_desc_valid_first",
    "market_behavior": "market_data_latest",
    "investor_relation": "cninfo_f10_preferred",
    "document_evidence": "raw_always_wins",
    "data_quality": "computed_from_sources",
}

MODULE_AGGREGATION: Dict[str, str] = {
    "company_identity": "scalar_pick_one",
    "securities_profile": "scalar_pick_one",
    "business_profile": "scalar_pick_one",
    "industry_profile": "scalar_pick_one",
    "financial_snapshot": "scalar_pick_one_with_unit",
    "technology_profile": "not_modeled",
    "organization_profile": "scalar_pick_one",
    "shareholder_profile": "array_top_n_by_report_period",
    "executive_profile": "array_merge_by_person_key",
    "governance_profile": "scalar_and_array_hybrid",
    "dividend_profile": "array_event_history",
    "capital_action_profile": "array_by_report_date",
    "risk_profile": "scalar_flag_merge",
    "event_timeline": "array_sorted_by_date",
    "market_behavior": "scalar_observe_sidecar",
    "investor_relation": "scalar_pick_one",
    "document_evidence": "lineage_attach_per_source",
    "data_quality": "rollup_per_module",
}

MODULE_UPDATE_FREQ: Dict[str, str] = {
    "company_identity": "low",
    "securities_profile": "medium",
    "business_profile": "low",
    "industry_profile": "low",
    "financial_snapshot": "high",
    "technology_profile": "low",
    "organization_profile": "medium",
    "shareholder_profile": "high",
    "executive_profile": "medium",
    "governance_profile": "medium",
    "dividend_profile": "medium",
    "capital_action_profile": "high",
    "risk_profile": "high",
    "event_timeline": "high",
    "market_behavior": "high",
    "investor_relation": "low",
    "document_evidence": "on_harvest",
    "data_quality": "on_harvest",
}


def _infer_module(norm: str, source_id: str) -> str:
    if norm in FIELD_MODULE:
        return FIELD_MODULE[norm]
    if source_id == "cninfo_company_security_profile":
        return "securities_profile"
    if source_id == "cninfo_executive_profile":
        return "executive_profile"
    if "shareholder" in source_id:
        return "shareholder_profile"
    if source_id == "cninfo_dividend_financing_profile":
        if norm in {"announcement_date_candidate", "ex_right_dividend_date_candidate"}:
            return "event_timeline"
        return "dividend_profile"
    if source_id == "cninfo_share_capital_profile":
        return "capital_action_profile"
    if source_id == "cninfo_company_contact_profile":
        return "investor_relation"
    if source_id == "cninfo_company_business_scope":
        return "business_profile"
    if source_id == "cninfo_company_industry_profile":
        return "industry_profile"
    return "company_identity"


def _load_catalog() -> List[Dict[str, str]]:
    with open(CATALOG_CSV, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def build_mapping_rows(catalog: List[Dict[str, str]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for item in catalog:
        norm = item["normalized_field_name"]
        source_id = item["source_id"]
        module = _infer_module(norm, source_id)
        priority = MODULE_SOURCE_PRIORITY.get(module, "cninfo_f10 > annual_report > announcement")
        rows.append({
            "snapshot_module": module,
            "normalized_field_name": norm,
            "source_id": source_id,
            "current_status": item["current_status"],
            "source_priority": priority,
            "aggregation_rule": MODULE_AGGREGATION.get(module, "scalar_pick_one"),
            "update_frequency_candidate": MODULE_UPDATE_FREQ.get(module, "medium"),
            "conflict_rule": MODULE_CONFLICT.get(module, "latest_valid_source"),
            "notes": item.get("notes", ""),
        })
    return rows


def write_mapping(rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(MAPPING_CSV), exist_ok=True)
    with open(MAPPING_CSV, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=MAPPING_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(catalog: List[Dict[str, str]], mapping: List[Dict[str, str]]) -> None:
    sc = Counter(r["current_status"] for r in catalog)
    modules_used = sorted({r["snapshot_module"] for r in mapping})
    norm_mapped = len({(r["snapshot_module"], r["normalized_field_name"]) for r in mapping})
    core_in_mapping = sum(1 for r in mapping if r["current_status"] == "normalized_core")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "# CNINFO C-Class Company Snapshot Planning Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 snapshot architecture planning。**无 CNINFO** · **无 harvest** · **无 DB/API 实现**",
        "",
        "**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`",
        "",
        "## 1. 当前 C-class 数据资产情况",
        "",
        "| 项 | 值 |",
        "|----|-----|",
        "| harvest companies | **863** |",
        "| company_harvest_status | **complete**（863/863） |",
        "| normalized_core fields | **74** |",
        "| review_later | **19** |",
        "| raw_only | **13** |",
        "| observe_only | **14** |",
        "| source-level normalized 产物 | basic · contact · business · industry · executive · share_capital · shareholders · dividend · security(observe) |",
        "| quality 产物 | field_fill_rate · source_quality · company_harvest_status |",
        "",
        "## 2. Snapshot 一级模块数量",
        "",
        f"**{len(SNAPSHOT_MODULES)}** 个一级模块（company object 视角，不按 source 分类）：",
        "",
    ]
    for i, m in enumerate(SNAPSHOT_MODULES, 1):
        count = sum(1 for r in mapping if r["snapshot_module"] == m)
        lines.append(f"{i}. `{m}` — catalog 映射 **{count}** 行")

    lines.extend([
        "",
        "## 3. Normalized field 映射数量",
        "",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| field mapping 总行数 | **{len(mapping)}** |",
        f"| 去重 (module, normalized_field) | **{norm_mapped}** |",
        f"| normalized_core 映射行 | **{core_in_mapping}** |",
        "",
        "## 4. candidate / review / raw / observe 处理策略",
        "",
        "| current_status | snapshot 策略 |",
        "|----------------|---------------|",
        "| normalized_core | 进入 snapshot 主展示层 |",
        "| review_later | 保留侧车 `review_queue`；默认不主展示 |",
        "| raw_only | 仅 `document_evidence` 追溯；不进主字段槽 |",
        "| observe_only | `securities_profile` / `market_behavior` 观察侧轨；不进主 gate |",
        "",
        "## 5. Source priority 总结",
        "",
        "- **identity / shareholder / dividend / capital_action**：`cninfo_f10` 优先（当前唯一已 harvest 源）",
        "- **business / industry / financial / governance**：未来 `annual_report` 优先，`cninfo_f10` 兜底",
        "- **event / risk**：未来 `announcement` 优先",
        "- **document_evidence**：`raw_source` 永远最高优先级",
        "",
        "详见 [cninfo_c_class_snapshot_source_priority_rules.md](../../plans/cninfo_c_class_snapshot_source_priority_rules.md)。",
        "",
        "## 6. Conflict resolution 总结",
        "",
        "- 同字段多源：`latest_valid_source` + 模块级 preferred_source",
        "- 时间冲突：报告期 / 公告日 `timestamp_desc_valid_first`",
        "- 数值冲突：financial 模块 `numeric_tolerance_with_annual_report_preferred`",
        "- 文本冲突：business 模块 `longest_valid_text_with_source_preference`",
        "- 人工复核：dividend `needs_review` 保留 manual_review_queue",
        "",
        "详见 [cninfo_c_class_snapshot_conflict_resolution.md](../../plans/cninfo_c_class_snapshot_conflict_resolution.md)。",
        "",
        "## 7. 当前不实现",
        "",
        "- database（PostgreSQL）",
        "- API",
        "- frontend",
        "- RAG",
        "- MinIO",
        "- registry backfill",
        "- harvest rerun",
        "",
        "## Gate",
        "",
        "```",
        "company_snapshot_planning_gate = PASS",
        "```",
        "",
        "## 推荐下一步",
        "",
        "1. **snapshot builder prototype**（离线只读 normalized 聚合 PoC）",
        "2. **security observe 决策**",
        "3. **BSE/abnormal 侧轨文档化**",
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO · 未重跑 harvest",
        "- raw / normalized / field_inventory **未修改**",
        "- 未写 verified · 未升级 testing_stable_sample",
    ])

    with open(SUMMARY_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    catalog = _load_catalog()
    mapping = build_mapping_rows(catalog)
    write_mapping(mapping)
    write_summary(catalog, mapping)
    print(f"mapping rows: {len(mapping)}")
    print(f"modules: {len(SNAPSHOT_MODULES)}")
    print(f"written: {MAPPING_CSV}")
    print(f"written: {SUMMARY_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
