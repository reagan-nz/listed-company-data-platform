#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速清洗 portrait catalog：可读 slug + C catalog 深度对账（offline）。"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "outputs" / "validation"

# 中文名 → 稳定英文 slug（覆盖 M01/M07/M08/M09 及常见字段）
ZH_SLUG: dict[str, str] = {
    "公司代码": "company_code",
    "股票简称": "stock_short_name",
    "公司全称": "legal_name",
    "英文名称": "english_name",
    "曾用名": "former_name",
    "统一社会信用代码": "unified_social_credit_code",
    "组织机构代码": "organization_code",
    "公司内部唯一编号": "internal_company_id",
    "交易所内部编号": "exchange_internal_id",
    "信息披露编号": "disclosure_id",
    "简称变更历史": "short_name_change_history",
    "代码变更历史": "code_change_history",
    "法定代表人": "legal_representative",
    "注册资本": "registered_capital",
    "实缴资本": "paid_in_capital",
    "成立日期": "establishment_date",
    "营业期限": "business_term",
    "注册地址": "registered_address",
    "办公地址": "office_address",
    "登记机关": "registration_authority",
    "企业性质": "enterprise_nature",
    "经营状态": "operating_status",
    "公司类型": "company_type",
    "公司设立方式": "incorporation_method",
    "公司前身": "predecessor",
    "股份制改造历史": "shareholding_reform_history",
    "工商变更历史": "business_registration_change_history",
    "上市日期": "listing_date",
    "交易所": "exchange",
    "上市板块": "listed_board",
    "证券类别": "security_category",
    "股票类别": "stock_category",
    "发行价格": "ipo_price",
    "发行数量": "ipo_shares",
    "首发募资金额": "ipo_proceeds",
    "上市状态": "listing_status",
    "交易状态": "trading_status",
    "停牌复牌": "suspension_resumption",
    "特别处理": "special_treatment",
    "退市风险警示": "delisting_risk_warning",
    "退市": "delisting",
    "转板": "board_transfer",
    "指数成分": "index_constituent",
    "融资融券标的": "margin_trading_target",
    "沪深港通标的": "stock_connect_target",
    "公司官网": "company_website",
    "电话": "contact_phone",
    "传真": "contact_fax",
    "邮箱": "contact_email",
    "投资者关系电话": "ir_phone",
    "投资者关系邮箱": "ir_email",
    "董秘联系方式": "board_secretary_contact",
    "证券事务代表": "securities_affairs_representative",
    "邮编": "postal_code",
    "指定信息披露媒体": "designated_disclosure_media",
    "公告披露网站": "announcement_website",
    "互动平台链接": "interactive_platform_url",
    "官方公众号": "official_wechat_account",
    "主营业务": "main_business_summary",
    "经营范围": "business_scope",
    "所属行业": "industry",
    "总股本": "total_share_capital",
    "流通股本": "float_share_capital",
    "限售股本": "restricted_share_capital",
    "无限售流通股": "unrestricted_float_shares",
    "A 股": "a_shares",
    "B 股": "b_shares",
    "H 股": "h_shares",
    "优先股": "preferred_shares",
    "股本变动": "share_capital_change",
    "送股": "stock_dividend",
    "转增": "capitalization_issue",
    "配股": "rights_issue",
    "增发": "seasoned_equity_offering",
    "回购注销": "buyback_cancellation",
    "可转债转股": "convertible_bond_conversion",
    "前十大股东": "top_ten_shareholders",
    "前十大流通股东": "top_ten_float_shareholders",
    "机构股东": "institutional_shareholders",
    "自然人股东": "individual_shareholders",
    "国有股东": "state_owned_shareholders",
    "外资股东": "foreign_shareholders",
    "基金持股": "fund_holdings",
    "社保持股": "social_security_holdings",
    "养老金持股": "pension_fund_holdings",
    "香港中央结算持股": "hk_clearing_holdings",
    "持股数量": "holding_shares",
    "持股比例": "holding_ratio",
    "股份性质": "share_nature",
    "控股股东": "controlling_shareholder",
    "实际控制人": "actual_controller",
    "最终受益人": "ultimate_beneficiary",
    "控制链条": "control_chain",
    "间接持股": "indirect_holding",
    "一致行动人": "concert_party",
    "表决权委托": "voting_rights_entrustment",
    "控制权变更": "control_change",
    "无实际控制人": "no_actual_controller",
    "国资背景": "state_owned_background",
    "民营背景": "private_background",
    "股东增持": "shareholder_increase",
    "股东减持": "shareholder_decrease",
    "股权质押": "share_pledge",
    "股权冻结": "share_freeze",
    "限售解禁": "restricted_shares_unlock",
    "股份回购": "share_buyback",
    "员工持股计划": "employee_stock_ownership_plan",
    "股权激励": "equity_incentive",
    "控制权争夺": "control_contest",
    "董事长": "chairman",
    "总经理": "general_manager",
    "董事": "director",
    "独立董事": "independent_director",
    "监事": "supervisor",
    "高级管理人员": "senior_management",
    "董事会秘书": "board_secretary",
    "姓名": "person_name",
    "性别": "gender",
    "年龄": "age",
    "学历": "education",
    "任职时间": "appointment_date",
    "任期": "term_of_office",
    "职务": "position",
    "简历": "biography",
    "薪酬": "compensation",
    "兼职": "concurrent_positions",
    "离任": "resignation",
    "变动原因": "change_reason",
    "董事会成员": "board_members",
    "独立董事比例": "independent_director_ratio",
    "审计委员会": "audit_committee",
    "薪酬委员会": "compensation_committee",
    "提名委员会": "nomination_committee",
    "战略委员会": "strategy_committee",
    "委员会成员": "committee_members",
    "会议次数": "meeting_count",
    "表决情况": "voting_outcome",
    "公司治理制度": "governance_system",
    "内部控制评价": "internal_control_evaluation",
    "内部控制审计": "internal_control_audit",
    "治理缺陷": "governance_defects",
    "关联交易制度": "related_party_transaction_policy",
    "信息披露制度": "disclosure_policy",
    "投资者保护": "investor_protection",
    "独立性": "independence",
    "同业竞争": "horizontal_competition",
    "资金占用": "fund_occupation",
    "违规担保": "illegal_guarantee",
    "分红年度": "dividend_year",
    "分红方案": "dividend_plan_text",
    "每股派息": "cash_dividend_per_share",
    "每股送股": "stock_dividend_per_share",
    "每股转增": "transfer_per_share",
    "现金分红金额": "cash_dividend_amount",
    "股权登记日": "record_date",
    "除权除息日": "ex_dividend_date",
    "派息日": "payment_date",
    "未分红原因": "no_dividend_reason",
    "利润分配政策": "profit_distribution_policy",
    "累计分红": "cumulative_dividends",
    "股息率": "dividend_yield",
    "分红稳定性": "dividend_stability",
    "首次公开发行": "ipo",
    "定向增发": "private_placement",
    "公开增发": "public_offering",
    "可转债": "convertible_bond",
    "公司债": "corporate_bond",
    "短期融资券": "short_term_financing_bond",
    "中期票据": "medium_term_note",
    "银行授信": "bank_credit_line",
    "资产证券化": "asset_securitization",
    "募集资金用途": "proceeds_usage",
    "募投项目": "fundraising_project",
    "募集资金使用进度": "proceeds_usage_progress",
    "募集资金变更": "proceeds_usage_change",
    "重大资产重组": "major_asset_restructuring",
    "资产收购": "asset_acquisition",
    "资产出售": "asset_disposal",
    "对外投资": "external_investment",
    "设立子公司": "subsidiary_establishment",
    "股权转让": "equity_transfer",
    "重大项目投资": "major_project_investment",
    "投资金额": "investment_amount",
    "交易对方": "counterparty",
    "交易进展": "transaction_progress",
    "业绩承诺": "performance_commitment",
    "商誉形成": "goodwill_formation",
    "年报披露": "annual_report_disclosure",
    "半年报披露": "semi_annual_report_disclosure",
    "一季报披露": "q1_report_disclosure",
    "三季报披露": "q3_report_disclosure",
    "业绩预告": "earnings_forecast",
    "业绩快报": "earnings_flash",
    "业绩说明会": "earnings_briefing",
    "融资融券": "margin_trading",
    "大宗交易": "block_trade",
    "营业收入": "revenue",
    "净利润": "net_profit",
    "归母净利润": "net_profit_attributable",
    "扣非净利润": "net_profit_ex_nonrecurring",
    "总资产": "total_assets",
    "总负债": "total_liabilities",
    "净资产": "net_assets",
    "资产负债率": "debt_to_asset_ratio",
    "每股收益": "eps",
    "每股净资产": "bps",
    "净资产收益率": "roe",
    "来源名称": "source_name",
    "来源链接": "source_url",
    "披露日期": "disclosure_date",
    "下载时间": "fetched_at",
    "文件哈希": "file_hash",
    "字段是否存在": "field_exists",
    "最后更新时间": "last_updated_at",
    "邮政编码": "postal_code",
    "联系邮箱": "contact_email",
    "联系电话": "contact_phone",
    "公司网址": "company_website",
    "法定名称": "legal_name",
    "证券简称": "stock_short_name",
    "证券代码": "company_code",
}


def slugify(name_zh: str) -> str:
    name = name_zh.strip()
    if name in ZH_SLUG:
        return ZH_SLUG[name]
    # 轻度规范化后再查
    for key, slug in ZH_SLUG.items():
        if key.replace(" ", "") == name.replace(" ", ""):
            return slug
    ascii_slug = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    if ascii_slug and not ascii_slug.startswith("field_"):
        return ascii_slug
    # 拼音不可用时用可读拼音式占位：zh_ + 稳定短 hash
    import hashlib

    return "zh_" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_c_name_index() -> dict[str, list[str]]:
    """中文描述 / normalized_name → existing_field_ref 列表。"""
    rows = load_csv(VALIDATION / "cninfo_c_class_final_field_catalog.csv")
    index: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        if row.get("field_name") == "(lineage)":
            continue
        ref = f"{row['source_id']}:{row['field_name']}"
        for key in (
            row.get("description", "").strip(),
            row.get("normalized_field_name", "").strip(),
        ):
            if key and ref not in index[key]:
                index[key].append(ref)
        # 英文 normalized 也挂中文常见别名
        norm = row.get("normalized_field_name", "").strip()
        desc = row.get("description", "").strip()
        if norm and desc:
            index[desc].append(ref) if ref not in index[desc] else None
    return index


# portrait 中文 → 额外 C 映射（描述不完全一致时）
EXTRA_ZH_TO_C: dict[str, str] = {
    "公司代码": "cninfo_company_basic_profile:ASECCODE",
    "股票简称": "cninfo_company_basic_profile:ASECNAME",
    "公司全称": "cninfo_company_basic_profile:ORGNAME",
    "英文名称": "cninfo_company_basic_profile:F001V",
    "法定代表人": "cninfo_company_basic_profile:F003V",
    "注册地址": "cninfo_company_basic_profile:F004V",
    "办公地址": "cninfo_company_basic_profile:F005V",
    "上市日期": "cninfo_company_basic_profile:F006D",
    "注册资本": "cninfo_company_basic_profile:F007N",
    "公司官网": "cninfo_company_basic_profile:F011V",
    "经营范围": "cninfo_company_basic_profile:F016V",
    "所属行业": "cninfo_company_basic_profile:F032V",
    "上市板块": "cninfo_company_basic_profile:MARKET",
    "交易所": "cninfo_company_basic_profile:(derived)",
    "主营业务": "cninfo_company_basic_profile:F015V",
    "成立日期": "cninfo_company_basic_profile:F010D",
    "邮编": "cninfo_company_contact_profile:F006V",
    "邮箱": "cninfo_company_contact_profile:F012V",
    "电话": "cninfo_company_contact_profile:F013V",
    "传真": "cninfo_company_contact_profile:F014V",
    "董秘联系方式": "cninfo_company_contact_profile:F018V",
    "总股本": "cninfo_share_capital_profile:F021N",
    "流通股本": "cninfo_share_capital_profile:F022N",
    "限售股本": "cninfo_share_capital_profile:F023N",
    "无限售流通股": "cninfo_share_capital_profile:F024N",
    "股本变动": "cninfo_share_capital_profile:F002V",
    "前十大股东": "cninfo_top_shareholders_profile:F002V",
    "前十大流通股东": "cninfo_top_float_shareholders_profile:F002V",
    "持股数量": "cninfo_top_shareholders_profile:F003N|cninfo_executive_profile:F005N",
    "持股比例": "cninfo_top_shareholders_profile:F004N",
    "姓名": "cninfo_executive_profile:F002V",
    "职务": "cninfo_executive_profile:F009V",
    "性别": "cninfo_executive_profile:F010V",
    "学历": "cninfo_executive_profile:F017V",
    "薪酬": "cninfo_executive_profile:F012N",
    "董事会秘书": "cninfo_executive_profile:F009V",
    "证券事务代表": "cninfo_company_contact_profile:F018V",
    "分红年度": "cninfo_dividend_financing_profile:F001V",
    "分红方案": "cninfo_dividend_financing_profile:F007V",
    "除权除息日": "cninfo_dividend_financing_profile:F020D",
    "派息日": "cninfo_dividend_financing_profile:F023D",
    "交易状态": "cninfo_company_security_profile:tradingStatus",
    "退市": "cninfo_company_security_profile:delisted",
    "沪深港通标的": "cninfo_company_security_profile:sshk|cninfo_company_security_profile:szhk",
}


def status_for_mapped(module_id: str, existing: str) -> str:
    if not existing:
        return ""
    if module_id in ("M01", "M03"):
        return "partial"
    if module_id in ("M07", "M08", "M09"):
        return "testing"
    if module_id == "M04":
        return "partial"
    return "candidate"


def main() -> None:
    catalog_path = VALIDATION / "company_portrait_field_catalog_v0.csv"
    matrix_path = VALIDATION / "company_portrait_coverage_matrix_v0.csv"
    rename_path = VALIDATION / "company_portrait_field_id_rename_v0_1.csv"
    summary_path = VALIDATION / "company_portrait_catalog_cleanup_summary.md"

    catalog = load_csv(catalog_path)
    matrix = {r["field_id"]: r for r in load_csv(matrix_path)}
    c_index = build_c_name_index()

    rename_rows: list[dict[str, str]] = []
    new_catalog: list[dict[str, str]] = []
    new_matrix: list[dict[str, str]] = []
    used_ids: set[str] = set()
    hash_fixed = 0
    mapped_new = 0

    for row in catalog:
        old_id = row["field_id"]
        module_id = row["module_id"]
        subgroup = row["subgroup"]
        name_zh = row["field_name_zh"]
        old_slug = old_id.split(".")[-1]
        new_slug = slugify(name_zh)
        new_id = f"{module_id}.{subgroup}.{new_slug}"

        # 冲突时加序号
        base_id = new_id
        n = 2
        while new_id in used_ids:
            new_id = f"{base_id}_{n}"
            n += 1
        used_ids.add(new_id)

        alias_of = row.get("alias_of", "")
        if new_id != old_id:
            rename_rows.append(
                {
                    "old_field_id": old_id,
                    "new_field_id": new_id,
                    "field_name_zh": name_zh,
                    "module_id": module_id,
                }
            )
            if old_slug.startswith("field_") or old_slug.startswith("zh_"):
                hash_fixed += 1
            # 旧 id 保留为别名行
            alias_row = dict(row)
            alias_row["alias_of"] = new_id
            new_catalog.append(alias_row)

        # 深度对账
        existing = row.get("existing_field_ref", "") or ""
        if not existing:
            if name_zh in EXTRA_ZH_TO_C:
                existing = EXTRA_ZH_TO_C[name_zh]
            elif name_zh in c_index:
                existing = "|".join(dict.fromkeys(c_index[name_zh]))
            elif name_zh.replace(" ", "") in c_index:
                existing = "|".join(dict.fromkeys(c_index[name_zh.replace(" ", "")]))
            if existing:
                mapped_new += 1

        out = dict(row)
        out["field_id"] = new_id
        out["existing_field_ref"] = existing
        out["alias_of"] = alias_of
        new_catalog.append(out)

        # 覆盖矩阵
        m = dict(matrix.get(old_id, {
            "field_id": old_id,
            "module_id": module_id,
            "primary_track": row.get("primary_track", ""),
            "existing_catalog_ref": "",
            "existing_schema_ref": "",
            "coverage_status": "not_modeled",
            "evidence_root_hint": "",
            "gap_reason": "",
        }))
        m["field_id"] = new_id
        if existing:
            m["existing_catalog_ref"] = existing
            if not m.get("existing_schema_ref"):
                if "basic" in existing or "contact" in existing or "industry" in existing or "business" in existing:
                    m["existing_schema_ref"] = "schemas/c_class/c_company_basic_profile.schema.json"
                elif "share_capital" in existing:
                    m["existing_schema_ref"] = "schemas/c_class/c_share_capital_profile.schema.json"
                elif "shareholder" in existing:
                    m["existing_schema_ref"] = "schemas/c_class/c_shareholder_profile.schema.json"
                elif "executive" in existing:
                    m["existing_schema_ref"] = "schemas/c_class/c_executive_profile.schema.json"
                elif "dividend" in existing:
                    m["existing_schema_ref"] = "schemas/c_class/c_company_profile_snapshot.schema.json"
                elif "security" in existing:
                    m["existing_schema_ref"] = "schemas/c_class/c_company_security_profile.schema.json"
            if m.get("coverage_status") in ("not_modeled", "defer", ""):
                m["coverage_status"] = status_for_mapped(module_id, existing) or "candidate"
                m["gap_reason"] = ""
            if not m.get("evidence_root_hint") and "cninfo_" in existing:
                if "share_capital" in existing:
                    m["evidence_root_hint"] = "outputs/harvest/cninfo_c_class/normalized/share_capital_profile/"
                elif "shareholder" in existing:
                    m["evidence_root_hint"] = "outputs/harvest/cninfo_c_class/normalized/top_shareholders_profile/"
                elif "executive" in existing:
                    m["evidence_root_hint"] = "outputs/harvest/cninfo_c_class/normalized/executive_profile/"
                elif "dividend" in existing:
                    m["evidence_root_hint"] = "outputs/harvest/cninfo_c_class/normalized/dividend_history/"
                else:
                    m["evidence_root_hint"] = "outputs/harvest/cninfo_c_class/normalized/"
        new_matrix.append(m)

        # 旧 id 矩阵行保留为 alias 指向
        if new_id != old_id and old_id in matrix:
            old_m = dict(matrix[old_id])
            old_m["gap_reason"] = f"renamed_to:{new_id}"
            # 不重复写入旧矩阵主键冲突；改写为注释性保留在 rename ledger 即可

    # 写 catalog：主行在前，alias 行也在
    cat_fields = [
        "field_id",
        "module_id",
        "subgroup",
        "field_name_zh",
        "value_shape",
        "needs_as_of",
        "primary_track",
        "fill_priority",
        "teacher_coverage_mark",
        "existing_field_ref",
        "alias_of",
    ]
    write_csv(catalog_path, new_catalog, cat_fields)
    write_csv(
        matrix_path,
        new_matrix,
        [
            "field_id",
            "module_id",
            "primary_track",
            "existing_catalog_ref",
            "existing_schema_ref",
            "coverage_status",
            "evidence_root_hint",
            "gap_reason",
        ],
    )
    write_csv(
        rename_path,
        rename_rows,
        ["old_field_id", "new_field_id", "field_name_zh", "module_id"],
    )

    # 刷新覆盖率 summary
    by_module: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in new_matrix:
        by_module[row["module_id"]][row["coverage_status"]] += 1
    primary_rows = [r for r in new_catalog if not r.get("alias_of")]
    mapped_primary = sum(1 for r in primary_rows if r.get("existing_field_ref"))
    hash_left = sum(
        1
        for r in primary_rows
        if r["field_id"].split(".")[-1].startswith("field_")
        or r["field_id"].split(".")[-1].startswith("zh_")
    )

    lines = [
        "# 公司画像 Catalog 清洗摘要 v0.1",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        "## 结果",
        "",
        f"- 主字段行：**{len(primary_rows)}**",
        f"- 重命名（含 alias 保留）：**{len(rename_rows)}**",
        f"- hash/field_* 已清洗：**{hash_fixed}**",
        f"- 主字段剩余 hash/zh_ slug：**{hash_left}**",
        f"- existing_field_ref 已映射主字段：**{mapped_primary}**（本轮新挂 **{mapped_new}**）",
        "",
        "## 按模块覆盖（主矩阵）",
        "",
        "| 模块 | testing | partial | candidate | not_modeled | defer | 已有源占比 |",
        "|------|---------|---------|-----------|-------------|-------|------------|",
    ]
    for mid in sorted(by_module):
        c = by_module[mid]
        total = sum(c.values())
        has = c.get("testing", 0) + c.get("partial", 0) + c.get("candidate", 0)
        pct = round(has / total * 100, 1) if total else 0
        lines.append(
            f"| {mid} | {c.get('testing',0)} | {c.get('partial',0)} | {c.get('candidate',0)} | "
            f"{c.get('not_modeled',0)} | {c.get('defer',0)} | {pct}% |"
        )
    lines.extend(
        [
            "",
            "## 产物",
            "",
            "- `company_portrait_field_catalog_v0.csv`（已更新）",
            "- `company_portrait_coverage_matrix_v0.csv`（已更新）",
            "- `company_portrait_field_id_rename_v0_1.csv`",
            "",
            "旧 hash field_id 以 `alias_of` 行保留，保证可追溯。",
            "",
        ]
    )
    summary_path.write_text("\n".join(lines), encoding="utf-8")

    # 同步 coverage_summary.md 核心数字
    cov_summary = VALIDATION / "company_portrait_coverage_summary.md"
    cov_summary.write_text(
        "\n".join(
            [
                "# 公司画像覆盖矩阵汇总 v0.1",
                "",
                f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
                "",
                "## 总览",
                "",
                f"- 主字段数：**{len(primary_rows)}**",
                f"- 已映射 existing_field_ref：**{mapped_primary}**",
                f"- 剩余不可读 slug：**{hash_left}**",
                "",
                "## 按模块覆盖率",
                "",
                "| 模块 | testing | partial | candidate | not_modeled | defer | 已有源占比 |",
                "|------|---------|---------|-----------|-------------|-------|------------|",
            ]
            + [
                f"| {mid} | {by_module[mid].get('testing',0)} | {by_module[mid].get('partial',0)} | "
                f"{by_module[mid].get('candidate',0)} | {by_module[mid].get('not_modeled',0)} | "
                f"{by_module[mid].get('defer',0)} | "
                f"{round((by_module[mid].get('testing',0)+by_module[mid].get('partial',0)+by_module[mid].get('candidate',0))/max(sum(by_module[mid].values()),1)*100,1)}% |"
                for mid in sorted(by_module)
            ]
            + [
                "",
                "## 说明",
                "",
                "- v0.1 完成 slug 清洗 + C catalog 深度对账；「已有源」= testing/partial/candidate。",
                "- 不等于已全市场回填；试点仍见 `company_portrait_pilot_fill_summary.md`。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(
        f"primary={len(primary_rows)} renamed={len(rename_rows)} "
        f"hash_fixed={hash_fixed} hash_left={hash_left} mapped={mapped_primary}"
    )


if __name__ == "__main__":
    main()
