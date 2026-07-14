#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从老师 docx 生成公司画像 ontology catalog 与覆盖矩阵（offline）。"""

from __future__ import annotations

import argparse
import csv
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_VALIDATION = ROOT / "outputs" / "validation"
PLANS = ROOT / "plans"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"

CN_NUM_TO_MODULE = {
    "一": "M01",
    "二": "M02",
    "三": "M03",
    "四": "M04",
    "五": "M05",
    "六": "M06",
    "七": "M07",
    "八": "M08",
    "九": "M09",
    "十": "M10",
    "十一": "M11",
    "十二": "M12",
    "十三": "M13",
    "十四": "M14",
    "十五": "M15",
    "十六": "M16",
    "十七": "M17",
    "十八": "M18",
}

MODULE_NAMES = {
    "M01": "公司身份与基础档案",
    "M02": "业务与商业模式",
    "M03": "行业与竞争格局",
    "M04": "财务与经营表现",
    "M05": "研发、技术与知识产权",
    "M06": "组织、人力与集团结构",
    "M07": "股权、股东与控制权",
    "M08": "治理结构与管理层",
    "M09": "资本运作与分红融资",
    "M10": "客户、供应商与合同订单",
    "M11": "资产、产能与项目建设",
    "M12": "风险、合规与争议",
    "M13": "公告事件与时间线",
    "M14": "市场表现与交易行为",
    "M15": "投资者关系与外部沟通",
    "M16": "文档证据与知识库",
    "M17": "数据质量与更新状态",
    "M18": "公司画像总结与标签",
}

MODULE_PRIMARY_TRACK = {
    "M01": "C",
    "M02": "none",
    "M03": "C",
    "M04": "A",
    "M05": "none",
    "M06": "none",
    "M07": "C",
    "M08": "C",
    "M09": "C",
    "M10": "none",
    "M11": "none",
    "M12": "B",
    "M13": "B",
    "M14": "D",
    "M15": "none",
    "M16": "multi",
    "M17": "multi",
    "M18": "none",
}

MODULE_FILL_PRIORITY = {
    "M01": "P0",
    "M02": "defer",
    "M03": "P2",
    "M04": "P1",
    "M05": "defer",
    "M06": "defer",
    "M07": "P0",
    "M08": "P1",
    "M09": "P1",
    "M10": "defer",
    "M11": "defer",
    "M12": "defer",
    "M13": "P1",
    "M14": "P1",
    "M15": "defer",
    "M16": "P0",
    "M17": "P0",
    "M18": "defer",
}

SUBGROUP_SLUGS = {
    "公司主身份": "primary_identity",
    "法律与工商身份": "legal_registry",
    "证券与上市身份": "listing_identity",
    "联系方式与披露渠道": "contact_disclosure",
    "主营业务": "main_business",
    "产品与服务": "products_services",
    "商业模式": "business_model",
    "经营区域与市场布局": "regional_market",
    "产业链位置": "supply_chain_position",
    "行业分类": "industry_classification",
    "行业环境": "industry_environment",
    "竞争地位": "competitive_position",
    "财务摘要": "finance_summary",
    "成长能力": "growth_capability",
    "盈利能力": "profitability",
    "现金流质量": "cashflow_quality",
    "资产质量": "asset_quality",
    "偿债与流动性": "solvency_liquidity",
    "研发投入": "rd_investment",
    "核心技术": "core_technology",
    "知识产权": "intellectual_property",
    "员工结构": "workforce_structure",
    "组织架构": "org_structure",
    "子公司与参股公司": "subsidiaries_investments",
    "股本结构": "share_capital_structure",
    "股东结构": "shareholder_structure",
    "控股股东与实际控制人": "control_chain",
    "股权稳定性与资本行为": "equity_stability",
    "董监高信息": "executive_board",
    "董事会与专门委员会": "board_committees",
    "公司治理与内部控制": "governance_internal_control",
    "分红与利润分配": "dividend_distribution",
    "融资行为": "financing_actions",
    "并购重组与重大投资": "ma_major_investment",
    "客户结构": "customer_structure",
    "供应商结构": "supplier_structure",
    "重大合同与订单": "major_contracts_orders",
    "生产基地与产能": "production_capacity",
    "重大资产": "major_assets",
    "重大项目": "major_projects",
    "经营风险": "operational_risk",
    "财务风险": "financial_risk",
    "技术与产品风险": "technology_product_risk",
    "合规处罚与监管风险": "compliance_regulatory_risk",
    "诉讼与仲裁": "litigation_arbitration",
    "定期报告事件": "periodic_report_events",
    "治理事件": "governance_events",
    "资本事件": "capital_market_events",
    "经营事件": "operating_events",
    "风险事件": "risk_events",
    "行情表现": "market_performance",
    "市场交易事件": "market_trading_events",
    "机构持仓与市场关注": "institutional_attention",
    "投资者问答": "investor_qa",
    "机构调研": "institutional_research",
    "业绩说明与路演": "earnings_roadshow",
    "原始文档": "source_documents",
    "证据链": "evidence_chain",
    "文本知识库": "text_knowledge_base",
    "字段质量": "field_quality",
    "模块状态": "module_status",
    "更新状态": "update_status",
    "冲突与版本管理": "conflict_versioning",
    "公司简介总结": "company_summary",
    "标签体系": "tag_system",
    "用户问答辅助信息": "qa_assist",
}

FIELD_NAME_SLUGS = {
    "公司代码": "company_code",
    "股票简称": "stock_short_name",
    "公司全称": "legal_name",
    "英文名称": "english_name",
    "曾用名": "former_name",
    "统一社会信用代码": "unified_social_credit_code",
    "组织机构代码": "organization_code",
    "法定代表人": "legal_representative",
    "注册资本": "registered_capital",
    "实缴资本": "paid_in_capital",
    "成立日期": "establishment_date",
    "注册地址": "registered_address",
    "办公地址": "office_address",
    "公司官网": "company_website",
    "电话": "contact_phone",
    "传真": "contact_fax",
    "邮箱": "contact_email",
    "上市日期": "listing_date",
    "交易所": "exchange",
    "上市板块": "listed_board",
    "主营业务": "main_business_summary",
    "经营范围": "business_scope",
    "所属行业": "industry",
    "总股本": "total_share_capital",
    "流通股本": "float_share_capital",
    "限售股本": "restricted_share_capital",
    "前十大股东": "top_ten_shareholders",
    "持股比例": "holding_ratio",
    "持股数量": "holding_shares",
    "董事长": "chairman",
    "总经理": "general_manager",
    "董事": "director",
    "独立董事": "independent_director",
    "监事": "supervisor",
    "高级管理人员": "senior_management",
    "董事会秘书": "board_secretary",
    "姓名": "person_name",
    "职务": "position",
    "学历": "education",
    "薪酬": "compensation",
    "分红年度": "dividend_year",
    "分红方案": "dividend_plan_text",
    "每股派息": "cash_dividend_per_share",
    "股权登记日": "record_date",
    "除权除息日": "ex_dividend_date",
    "派息日": "payment_date",
    "年报披露": "annual_report_disclosure",
    "半年报披露": "semi_annual_report_disclosure",
    "融资融券": "margin_trading",
    "大宗交易": "block_trade",
    "营业收入": "revenue",
    "净利润": "net_profit",
    "归母净利润": "net_profit_attributable",
    "总资产": "total_assets",
    "净资产": "net_assets",
    "资产负债率": "debt_to_asset_ratio",
    "每股收益": "eps",
    "净资产收益率": "roe",
    "来源名称": "source_name",
    "来源链接": "source_url",
    "披露日期": "disclosure_date",
    "下载时间": "fetched_at",
    "文件哈希": "file_hash",
    "字段是否存在": "field_exists",
    "最后更新时间": "last_updated_at",
}

RED_COLORS = {"FF0000", "C00000", "EE0000", "D00000", "E60000"}

SKIP_LINES = {
    "完整模块清单",
    "上市公司完整属性体系说明稿",
}

TABLE_HEADER_LINES = {
    "子模块",
    "可以包含的典型属性",
    "设计意义",
}

MODULE_HEADER_RE = re.compile(
    r"^([一二三四五六七八九十]+)、(.+)$"
)


@dataclass
class PortraitField:
    field_id: str
    module_id: str
    subgroup: str
    field_name_zh: str
    value_shape: str
    needs_as_of: str
    primary_track: str
    fill_priority: str
    teacher_coverage_mark: str
    existing_field_ref: str = ""
    alias_of: str = ""
    design_intent: str = ""


@dataclass
class PortraitModule:
    module_id: str
    module_name_zh: str
    submodules: list[str] = field(default_factory=list)
    design_intent: str = ""


def parse_docx_paragraphs(docx_path: Path) -> list[tuple[str, bool]]:
    """解析 docx 段落文本与标红标记。"""
    with zipfile.ZipFile(docx_path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    paragraphs: list[tuple[str, bool]] = []
    for para in root.iter(f"{W}p"):
        parts: list[str] = []
        highlighted = False
        for run in para.iter(f"{W}r"):
            color_el = run.find(f"{W}rPr/{W}color")
            if color_el is not None:
                color_val = (color_el.get(f"{W}val") or "").upper()
                if color_val in RED_COLORS:
                    highlighted = True
            text_el = run.find(f"{W}t")
            if text_el is not None and text_el.text:
                parts.append(text_el.text)
        line = "".join(parts).strip()
        if line:
            paragraphs.append((line, highlighted))
    return paragraphs


def slugify_field_name(name_zh: str) -> str:
    """将中文字段名转为稳定 slug。"""
    cleaned = name_zh.strip().rstrip("。").strip()
    if cleaned in FIELD_NAME_SLUGS:
        return FIELD_NAME_SLUGS[cleaned]
    # 去除常见后缀再查表
    for suffix in ("风险", "历史", "变化", "记录", "情况", "进展", "结果"):
        base = cleaned.replace(suffix, "")
        if base in FIELD_NAME_SLUGS:
            return FIELD_NAME_SLUGS[base] + "_" + suffix
    # 回退：保留中文语义片段的拼音首字母式简化不可行，用规范化 ASCII slug
    ascii_slug = re.sub(r"[^a-zA-Z0-9]+", "_", cleaned).strip("_").lower()
    if ascii_slug:
        return ascii_slug
    # 最终回退：unicode 名 hash 前缀 + 序号式（保证唯一）
    return "field_" + format(abs(hash(cleaned)) % 100000, "05d")


def subgroup_slug(name_zh: str, module_id: str, index: int) -> str:
    if name_zh in SUBGROUP_SLUGS:
        return SUBGROUP_SLUGS[name_zh]
    return f"subgroup_{index:02d}"


def infer_value_shape(field_name_zh: str, subgroup: str) -> str:
    event_keywords = ("事件", "披露", "变更", "会议", "处罚", "诉讼", "停牌", "复牌", "回购", "增发")
    timeseries_keywords = ("增长率", "率", "收入", "利润", "现金流", "余额", "数量", "金额", "占比")
    document_keywords = ("PDF", "公告", "年报", "半年报", "季报", "文本", "文档", "纪要")
    if any(k in field_name_zh for k in event_keywords) or subgroup.endswith("_events"):
        return "event"
    if any(k in field_name_zh for k in document_keywords):
        return "document"
    if any(k in field_name_zh for k in timeseries_keywords):
        return "timeseries"
    return "scalar"


def needs_as_of_flag(value_shape: str, field_name_zh: str) -> str:
    if value_shape in ("timeseries", "event"):
        return "yes"
    if any(k in field_name_zh for k in ("日期", "时间", "年度", "报告期")):
        return "yes"
    return "no"


def split_field_tokens(text: str) -> list[str]:
    text = text.rstrip("。").strip()
    parts = re.split(r"[、，,；;]", text)
    return [p.strip() for p in parts if p.strip()]


def parse_modules_and_fields(paragraphs: list[tuple[str, bool]]) -> tuple[list[PortraitModule], list[PortraitField]]:
    modules: list[PortraitModule] = []
    fields: list[PortraitField] = []
    current_module: PortraitModule | None = None
    current_subgroup_name = ""
    current_subgroup_slug = ""
    subgroup_index = 0
    state = "intro"  # intro | subgroup | fields | intent

    for line, highlighted in paragraphs:
        if line in SKIP_LINES:
            continue
        if line.startswith("下面按公司画像"):
            continue

        module_match = MODULE_HEADER_RE.match(line)
        if module_match:
            cn_num, module_title = module_match.groups()
            module_id = CN_NUM_TO_MODULE[cn_num]
            current_module = PortraitModule(
                module_id=module_id,
                module_name_zh=module_title.strip(),
                design_intent="",
            )
            modules.append(current_module)
            subgroup_index = 0
            state = "intro"
            current_subgroup_name = ""
            current_subgroup_slug = ""
            continue

        if current_module is None:
            continue

        if line in TABLE_HEADER_LINES:
            if line == "子模块":
                state = "subgroup"
            continue

        if state == "intro":
            if not current_module.design_intent:
                current_module.design_intent = line
            else:
                current_module.design_intent += " " + line
            continue

        if state == "subgroup":
            subgroup_index += 1
            current_subgroup_name = line
            current_subgroup_slug = subgroup_slug(line, current_module.module_id, subgroup_index)
            if current_subgroup_name not in current_module.submodules:
                current_module.submodules.append(current_subgroup_name)
            state = "fields"
            continue

        if state == "fields":
            mark = "highlighted" if highlighted else "plain"
            for token in split_field_tokens(line):
                slug = slugify_field_name(token)
                field_id = f"{current_module.module_id}.{current_subgroup_slug}.{slug}"
                value_shape = infer_value_shape(token, current_subgroup_slug)
                fields.append(
                    PortraitField(
                        field_id=field_id,
                        module_id=current_module.module_id,
                        subgroup=current_subgroup_slug,
                        field_name_zh=token,
                        value_shape=value_shape,
                        needs_as_of=needs_as_of_flag(value_shape, token),
                        primary_track=MODULE_PRIMARY_TRACK[current_module.module_id],
                        fill_priority=MODULE_FILL_PRIORITY[current_module.module_id],
                        teacher_coverage_mark=mark,
                    )
                )
            state = "intent"
            continue

        if state == "intent":
            # 设计意义行；下一段若非模块头则进入下一子模块
            state = "subgroup"
            continue

    return modules, fields


def dedupe_fields(fields: list[PortraitField]) -> list[PortraitField]:
    """同 module+subgroup+中文名去重，保留首条。"""
    seen: set[tuple[str, str, str]] = set()
    result: list[PortraitField] = []
    for item in fields:
        key = (item.module_id, item.subgroup, item.field_name_zh)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def load_c_catalog() -> list[dict[str, str]]:
    path = OUT_VALIDATION / "cninfo_c_class_final_field_catalog.csv"
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_a_catalog() -> list[dict[str, str]]:
    path = OUT_VALIDATION / "cninfo_a_class_phase1_freeze_v1_field_catalog.csv"
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_b_catalog() -> list[dict[str, str]]:
    path = OUT_VALIDATION / "cninfo_b_class_phase1_freeze_v1_field_catalog.csv"
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_d_catalog() -> list[dict[str, str]]:
    path = OUT_VALIDATION / "cninfo_d_class_phase1_freeze_v1_field_catalog.csv"
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# portrait field_id -> (catalog_ref, schema_ref, coverage_status, evidence_root_hint)
PORTRAIT_TO_EXISTING: dict[str, tuple[str, str, str, str]] = {
    "M01.primary_identity.company_code": (
        "cninfo_company_basic_profile:ASECCODE",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.primary_identity.stock_short_name": (
        "cninfo_company_basic_profile:ASECNAME",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.primary_identity.legal_name": (
        "cninfo_company_basic_profile:ORGNAME",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.primary_identity.english_name": (
        "cninfo_company_basic_profile:F001V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.legal_registry.legal_representative": (
        "cninfo_company_basic_profile:F003V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.legal_registry.registered_capital": (
        "cninfo_company_basic_profile:F007N",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.legal_registry.establishment_date": (
        "cninfo_company_basic_profile:F010D",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.legal_registry.registered_address": (
        "cninfo_company_basic_profile:F004V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.legal_registry.office_address": (
        "cninfo_company_basic_profile:F005V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.listing_identity.listing_date": (
        "cninfo_company_basic_profile:F006D",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.listing_identity.listed_board": (
        "cninfo_company_basic_profile:MARKET",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.listing_identity.exchange": (
        "cninfo_company_basic_profile:(derived)exchange",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.contact_disclosure.company_website": (
        "cninfo_company_contact_profile:F011V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.contact_disclosure.contact_phone": (
        "cninfo_company_contact_profile:F013V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "candidate",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M01.contact_disclosure.contact_email": (
        "cninfo_company_contact_profile:F012V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "candidate",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M02.main_business.main_business_summary": (
        "cninfo_company_business_scope:F015V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M02.main_business.business_scope": (
        "cninfo_company_business_scope:F016V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M03.industry_classification.industry": (
        "cninfo_company_industry_profile:F032V",
        "schemas/c_class/c_company_basic_profile.schema.json",
        "partial",
        "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
    ),
    "M07.share_capital_structure.total_share_capital": (
        "cninfo_share_capital_profile:F021N",
        "schemas/c_class/c_share_capital_profile.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/share_capital_profile/",
    ),
    "M07.share_capital_structure.float_share_capital": (
        "cninfo_share_capital_profile:F022N",
        "schemas/c_class/c_share_capital_profile.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/share_capital_profile/",
    ),
    "M07.share_capital_structure.restricted_share_capital": (
        "cninfo_share_capital_profile:F023N",
        "schemas/c_class/c_share_capital_profile.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/share_capital_profile/",
    ),
    "M07.shareholder_structure.holding_shares": (
        "cninfo_top_shareholders_profile:F003N",
        "schemas/c_class/c_shareholder_profile.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/top_shareholders_profile/",
    ),
    "M07.shareholder_structure.holding_ratio": (
        "cninfo_top_shareholders_profile:F004N",
        "schemas/c_class/c_shareholder_profile.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/top_shareholders_profile/",
    ),
    "M08.executive_board.person_name": (
        "cninfo_executive_profile:F002V",
        "schemas/c_class/c_executive_profile.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/executive_profile/",
    ),
    "M08.executive_board.position": (
        "cninfo_executive_profile:F009V",
        "schemas/c_class/c_executive_profile.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/executive_profile/",
    ),
    "M09.dividend_distribution.dividend_year": (
        "cninfo_dividend_financing_profile:F001V",
        "schemas/c_class/c_company_profile_snapshot.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/dividend_history/",
    ),
    "M09.dividend_distribution.dividend_plan_text": (
        "cninfo_dividend_financing_profile:F007V",
        "schemas/c_class/c_company_profile_snapshot.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/dividend_history/",
    ),
    "M09.dividend_distribution.cash_dividend_per_share": (
        "cninfo_dividend_financing_profile:derived_cash_dividend_per_share",
        "schemas/c_class/c_company_profile_snapshot.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/dividend_history/",
    ),
    "M09.dividend_distribution.ex_dividend_date": (
        "cninfo_dividend_financing_profile:F020D",
        "schemas/c_class/c_company_profile_snapshot.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/dividend_history/",
    ),
    "M09.dividend_distribution.payment_date": (
        "cninfo_dividend_financing_profile:F023D",
        "schemas/c_class/c_company_profile_snapshot.schema.json",
        "testing",
        "outputs/harvest/cninfo_c_class/normalized/dividend_history/",
    ),
    "M04.finance_summary.revenue": (
        "cninfo_a_class:report_document",
        "schemas/a_class/ (lineage only)",
        "not_modeled",
        "outputs/validation/cninfo_a_class_*/raw_metadata/",
    ),
    "M13.periodic_report_events.annual_report_disclosure": (
        "cninfo_b_class:announcement_record",
        "schemas/b_class/b_document.schema.json",
        "partial",
        "outputs/validation/cninfo_b_class_*/raw_metadata/",
    ),
    "M14.market_trading_events.margin_trading": (
        "cninfo_d_class:margin_trading",
        "schemas/d_class/d_company_metric_daily.schema.json",
        "testing",
        "outputs/validation/cninfo_d_class_margin_trading_first_slice/",
    ),
    "M14.market_trading_events.block_trade": (
        "cninfo_d_class:block_trade",
        "schemas/d_class/d_company_event.schema.json",
        "candidate",
        "outputs/validation/cninfo_d_class_block_trade_first_slice/",
    ),
    "M16.evidence_chain.source_url": (
        "cninfo_b_class:pdf_url",
        "schemas/b_class/b_document.schema.json",
        "partial",
        "outputs/validation/cninfo_b_class_*/raw_metadata/",
    ),
    "M16.evidence_chain.file_hash": (
        "cninfo_a_class:raw_hash",
        "schemas/a_class/ (lineage)",
        "partial",
        "outputs/validation/cninfo_a_class_*/raw_metadata/",
    ),
    "M17.field_quality.field_exists": (
        "portrait_meta:field_quality",
        "schemas/portrait/fact_record.schema.json",
        "candidate",
        "outputs/portrait/companies/",
    ),
}


def default_coverage_for_field(field: PortraitField) -> tuple[str, str, str, str, str]:
    if field.field_id in PORTRAIT_TO_EXISTING:
        cat, schema, status, root = PORTRAIT_TO_EXISTING[field.field_id]
        return cat, schema, status, root, ""

    module = field.module_id
    if module in ("M02", "M05", "M06", "M10", "M11", "M12", "M15", "M18"):
        return "", "", "defer", "", "依赖年报正文/IR/外部源，本阶段不建模"
    if module == "M04" and field.value_shape == "timeseries":
        return "", "", "not_modeled", "", "财报数值需 PDF 解析闸门，A 类仅 metadata lineage"
    if module == "M04":
        return (
            "cninfo_a_class:report_document",
            "schemas/a_class/ (metadata only)",
            "partial",
            "",
            "A 类仅 URL/metadata lineage，无数值抽取",
        )
    if module == "M13":
        return (
            "cninfo_b_class:announcement_record",
            "schemas/b_class/b_document.schema.json",
            "candidate",
            "outputs/validation/cninfo_b_class_*/raw_metadata/",
            "事件壳可建，结构化类型待补",
        )
    if module == "M14":
        return (
            "cninfo_d_class:market_event",
            "schemas/d_class/d_company_event.schema.json",
            "not_modeled",
            "outputs/validation/cninfo_d_class_*/",
            "D 类组件待扩样",
        )
    if module in ("M16", "M17"):
        return (
            "portrait_meta:cross_cutting",
            "schemas/portrait/",
            "candidate",
            "outputs/portrait/companies/",
            "横切规范，随试点落地",
        )
    if module == "M03":
        return (
            "cninfo_company_industry_profile:F032V",
            "schemas/c_class/c_company_basic_profile.schema.json",
            "partial",
            "outputs/harvest/cninfo_c_class/normalized/company_basic_profile/",
            "仅单一行业字段，非完整分类体系",
        )
    return "", "", "not_modeled", "", "尚无采集映射"


def write_module_index(modules: list[PortraitModule], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["module_id", "module_name_zh", "submodules", "design_intent"],
        )
        writer.writeheader()
        for mod in modules:
            writer.writerow(
                {
                    "module_id": mod.module_id,
                    "module_name_zh": mod.module_name_zh,
                    "submodules": "|".join(mod.submodules),
                    "design_intent": mod.design_intent,
                }
            )


def write_field_catalog(fields: list[PortraitField], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
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
            ],
        )
        writer.writeheader()
        for item in fields:
            existing_ref = ""
            if item.field_id in PORTRAIT_TO_EXISTING:
                existing_ref = PORTRAIT_TO_EXISTING[item.field_id][0]
            writer.writerow(
                {
                    "field_id": item.field_id,
                    "module_id": item.module_id,
                    "subgroup": item.subgroup,
                    "field_name_zh": item.field_name_zh,
                    "value_shape": item.value_shape,
                    "needs_as_of": item.needs_as_of,
                    "primary_track": item.primary_track,
                    "fill_priority": item.fill_priority,
                    "teacher_coverage_mark": item.teacher_coverage_mark,
                    "existing_field_ref": existing_ref,
                    "alias_of": item.alias_of,
                }
            )


def write_coverage_matrix(fields: list[PortraitField], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
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
        writer.writeheader()
        for item in fields:
            cat, schema, status, root, gap = default_coverage_for_field(item)
            writer.writerow(
                {
                    "field_id": item.field_id,
                    "module_id": item.module_id,
                    "primary_track": item.primary_track,
                    "existing_catalog_ref": cat,
                    "existing_schema_ref": schema,
                    "coverage_status": status,
                    "evidence_root_hint": root,
                    "gap_reason": gap,
                }
            )


def write_coverage_summary(fields: list[PortraitField], matrix_path: Path, path: Path) -> None:
    by_module: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    with matrix_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            by_module[row["module_id"]][row["coverage_status"]] += 1

    lines = [
        "# 公司画像覆盖矩阵汇总 v0",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        "## 总览",
        "",
        f"- 字段总数：**{len(fields)}**",
        f"- 模块数：**{len(MODULE_NAMES)}**",
        "",
        "## 按模块覆盖率",
        "",
        "| 模块 | 字段数 | testing | partial | candidate | not_modeled | defer | blocked | empty_ok | 已有源占比 |",
        "|------|--------|---------|---------|-----------|-------------|-------|---------|----------|------------|",
    ]
    for module_id in sorted(MODULE_NAMES):
        counts = by_module.get(module_id, {})
        total = sum(counts.values())
        if total == 0:
            continue
        has_source = (
            counts.get("testing", 0)
            + counts.get("partial", 0)
            + counts.get("candidate", 0)
        )
        pct = round(has_source / total * 100, 1) if total else 0.0
        lines.append(
            f"| {module_id} {MODULE_NAMES[module_id]} | {total} | "
            f"{counts.get('testing', 0)} | {counts.get('partial', 0)} | "
            f"{counts.get('candidate', 0)} | {counts.get('not_modeled', 0)} | "
            f"{counts.get('defer', 0)} | {counts.get('blocked', 0)} | "
            f"{counts.get('empty_ok', 0)} | {pct}% |"
        )

    lines.extend(
        [
            "",
            "## Era D 下一刀建议（按缺口）",
            "",
            "1. **M01 身份**：补 `company_basic_profile` harvest 覆盖（对齐 orgId / basic empty 敏感样本）",
            "2. **M07/M08/M09**：沿用 C 类 normalized 产物扩映射表，不阻塞 live",
            "3. **M04 财务数值**：保持 `not_modeled`，A 类仅 metadata lineage",
            "4. **M13/M14**：B 事件壳 + D 组件扩样并行",
            "",
            "## 红线",
            "",
            "无 DB/MinIO · 无 PDF 解析默认 · 无 `verified`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_ontology_plan(
    modules: list[PortraitModule],
    fields: list[PortraitField],
    path: Path,
    *,
    docx_path: Path,
) -> None:
    highlighted = sum(1 for f in fields if f.teacher_coverage_mark == "highlighted")
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 公司画像 Ontology 计划（工程映射总说明）",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
        "## 来源",
        "",
        f"- 老师文档：`{docx_path}`",
        "- 本文件为 **目标 ontology**；A/B/C/D 为 **填数管道**",
        "",
        "## 三层模型",
        "",
        "| 层 | 本阶段 | 说明 |",
        "|----|--------|------|",
        "| 证据层 | 只建指针 | `outputs/harvest|validation|snapshot` 只读引用 |",
        "| 事实层 | schema + 试点 | `outputs/portrait/companies/<code>/facts.jsonl` |",
        "| 画像层 | 延后 | M18 仅占位 |",
        "",
        "## field_id 规范",
        "",
        "```text",
        "<module_id>.<subgroup>.<field_slug>",
        "```",
        "",
        "- 只增不改；改名走 `alias_of`",
        "- 与现有 catalog 用 `existing_field_ref` 对账，不重造字段",
        "",
        "## 标红抽取说明",
        "",
        f"- docx run 颜色解析：命中红色字段 **{highlighted}** 条",
    ]
    if highlighted == 0:
        lines.append(
            "- **解析结果：无可靠标红元数据**（`teacher_coverage_mark=plain/unknown`）；"
            "按模块 `fill_priority` 人工标 P0/P1/defer"
        )
    lines.extend(["", "## 18 模块映射", "", "| 模块 | 名称 | 主轨道 | 优先级 | 子模块数 | 字段数 |", "|------|------|--------|--------|----------|--------|"])
    field_counts = defaultdict(int)
    for f in fields:
        field_counts[f.module_id] += 1
    for mod in modules:
        lines.append(
            f"| {mod.module_id} | {mod.module_name_zh} | "
            f"{MODULE_PRIMARY_TRACK[mod.module_id]} | "
            f"{MODULE_FILL_PRIORITY[mod.module_id]} | "
            f"{len(mod.submodules)} | {field_counts[mod.module_id]} |"
        )
    lines.extend(
        [
            "",
            "## 与四线关系",
            "",
            "| 线 | 贡献模块 |",
            "|----|----------|",
            "| C | M01/M07/M08/M09 主源 |",
            "| A | M04/M13 证据入口（非财报数值） |",
            "| B | M13 事件壳 + 文档证据 |",
            "| D | M14 及部分资本事件 |",
            "",
            "## Gate",
            "",
            "- `portrait_p0_catalog_gate` — 本步骤产出",
            "- `portrait_p1_coverage_gate` — 覆盖矩阵 v0",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="从老师 docx 生成公司画像 ontology catalog（offline · 无绝对本机默认路径）"
    )
    parser.add_argument(
        "--docx",
        required=True,
        type=Path,
        help="老师属性体系 docx 路径（必须显式传入，不绑定本机 Downloads）",
    )
    args = parser.parse_args(argv)
    docx_path = args.docx.expanduser().resolve()
    if not docx_path.is_file():
        raise SystemExit(f"docx not found: {docx_path}")

    paragraphs = parse_docx_paragraphs(docx_path)
    modules, fields = parse_modules_and_fields(paragraphs)
    fields = dedupe_fields(fields)

    module_index_path = OUT_VALIDATION / "company_portrait_module_index.csv"
    field_catalog_path = OUT_VALIDATION / "company_portrait_field_catalog_v0.csv"
    coverage_matrix_path = OUT_VALIDATION / "company_portrait_coverage_matrix_v0.csv"
    coverage_summary_path = OUT_VALIDATION / "company_portrait_coverage_summary.md"
    ontology_plan_path = PLANS / "company_portrait_ontology_plan.md"

    write_module_index(modules, module_index_path)
    write_field_catalog(fields, field_catalog_path)
    write_coverage_matrix(fields, coverage_matrix_path)
    write_coverage_summary(fields, coverage_matrix_path, coverage_summary_path)
    write_ontology_plan(modules, fields, ontology_plan_path, docx_path=docx_path)

    print(f"modules={len(modules)} fields={len(fields)}")
    print(f"wrote {module_index_path}")
    print(f"wrote {field_catalog_path}")
    print(f"wrote {coverage_matrix_path}")
    print(f"wrote {coverage_summary_path}")
    print(f"wrote {ontology_plan_path}")


if __name__ == "__main__":
    main()
