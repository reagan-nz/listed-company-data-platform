"""Plan B: explicit field schema for annual-report extraction.

The moat is NOT long context; it is clear field definitions + stable parsing +
evidence linking + quality verification. This module is the "clear field
definitions" part: each target field has a definition, the anchor headings used
to locate it, where it is expected in a CN annual report, and how we extract it.

This schema is SOURCE/DOMAIN knowledge about CN annual reports. It contains NO
company-specific values; the company, stock code, and source_url are supplied at
runtime via CLI.

Generalization-hardening fields (all generic, template-driven, not per-company):
  - `region`      preferred doc region ("mda" | "notes" | "any")
  - `avoid`       substrings that, if they immediately follow an anchor match,
                  signal the WRONG occurrence (e.g. a table column or the
                  employee-count line) and are penalized during location
  - `table_match` tokens used to pick the RIGHT table among several on a page
                  (e.g. region vs segment)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label_cn: str
    definition: str
    anchors: tuple[str, ...]          # headings/keywords used to locate the section
    expected_location: str            # human note on where it usually appears
    extraction: str                   # "section_snippet" | "table" | "numeric" | "concentration"
    region: str = "any"               # preferred doc region: "mda" | "notes" | "any"
    avoid: tuple[str, ...] = ()        # negative context tokens right after the anchor
    table_match: tuple[str, ...] = ()  # tokens used to pick the right table (>=1 required if set)
    table_require: tuple[str, ...] = ()  # tokens a candidate table MUST contain (context guard)
    fallback_anchors: tuple[str, ...] = ()  # sibling-section anchors to retry when the
    #                                         primary anchor is missing or doesn't land
    #                                         in-region at a heading (e.g. a field that is
    #                                         often described inside another section)


# Table-header / column tokens that indicate an anchor matched a TABLE column or
# a tabular row rather than the narrative we want (used as `avoid` context).
TABLE_CONTEXT = ("持股比例", "注册资本", "营业成本", "毛利率", "分行业", "分产品",
                 "生产量", "销售量", "库存量", "总资产", "净资产")

FIELD_SPECS: list[FieldSpec] = [
    FieldSpec(
        key="main_business_segments",
        label_cn="主营业务/业务板块",
        definition="The company's principal lines of business / reporting segments.",
        anchors=("报告期内公司从事的主要业务", "公司从事的主要业务", "业务概要", "公司主要从事", "主要业务", "主营业务"),
        expected_location="第三节 管理层讨论与分析 (MD&A), business overview narrative",
        extraction="section_snippet",
        region="mda",
        avoid=TABLE_CONTEXT,
    ),
    FieldSpec(
        key="major_products",
        label_cn="主要产品及服务",
        definition="Major products and services offered by the company.",
        anchors=("主要产品及其用途", "主要产品和服务", "主要产品及服务", "主要产品", "产品及用途"),
        expected_location="MD&A business overview / product table",
        extraction="section_snippet",
        region="mda",
        avoid=("注册资本", "持股比例", "总资产", "净资产"),
        # Many reports have no dedicated 主要产品 heading; products are described
        # inside the business-overview narrative. Fall back to that section so we
        # still locate an evidence-linked, in-region snippet.
        fallback_anchors=("报告期内公司从事的主要业务", "公司从事的主要业务",
                          "公司主要从事", "主营业务", "业务概要", "主要业务"),
    ),
    FieldSpec(
        key="revenue_by_segment",
        label_cn="营业收入构成-分行业/分产品",
        definition="Revenue broken down by industry/product segment.",
        anchors=("主营业务分行业", "主营业务分产品", "营业收入构成", "分行业", "分产品", "分部信息"),
        expected_location="MD&A '主营业务分行业、分产品' table",
        extraction="table",
        region="mda",
        table_match=("分行业", "分产品"),
        table_require=("营业收入", "营业成本", "毛利率"),
    ),
    FieldSpec(
        key="revenue_by_region",
        label_cn="营业收入构成-分地区",
        definition="Revenue broken down by geographic region (domestic/overseas).",
        # NOTE: bare "境内"/"境外" are intentionally NOT anchors - they mislocate
        # to "境外资产情况" / overseas-asset disclosures. They remain in
        # `table_match` (guarded by `table_require`) only to score the right table.
        anchors=("主营业务分地区", "分地区", "地区分布", "按地区"),
        expected_location="MD&A '主营业务分地区' table",
        extraction="table",
        region="mda",
        table_match=("分地区", "境内", "境外", "地区"),
        table_require=("营业收入", "营业成本", "毛利率"),
    ),
    FieldSpec(
        key="top_customers",
        label_cn="前五名客户",
        definition="Top-5 customers and their share of revenue, if disclosed.",
        anchors=("前五名客户合计", "前五名客户", "前五大客户", "主要客户"),
        expected_location="MD&A '前五名客户' - often disclosed as a narrative sentence",
        extraction="concentration",
        region="mda",
    ),
    FieldSpec(
        key="top_suppliers",
        label_cn="前五名供应商",
        definition="Top-5 suppliers and their share of purchases, if disclosed.",
        anchors=("前五名供应商合计", "前五名供应商", "前五大供应商", "主要供应商"),
        expected_location="MD&A '前五名供应商' - often disclosed as a narrative sentence",
        extraction="concentration",
        region="mda",
    ),
    FieldSpec(
        key="rnd_investment",
        label_cn="研发投入",
        definition="R&D expenditure amount and/or as a percentage of revenue.",
        anchors=("研发投入金额", "研发投入总额", "研发投入合计", "研发费用", "研发投入"),
        expected_location="MD&A '研发投入' table/paragraph (not the income-statement 研发费用 line)",
        extraction="numeric",
        region="mda",
        avoid=("占营业收入", "比重", "研发人员", "不适用", "变化的原因"),
    ),
    FieldSpec(
        key="major_subsidiaries",
        label_cn="主要控股参股公司",
        definition="Major holding/affiliated subsidiaries and their role.",
        anchors=("主要子公司情况", "主要控股参股公司", "主要控股、参股公司", "重要控股参股公司", "主要子公司"),
        expected_location="财务报表附注 '主要子公司情况' OR MD&A '主要控股参股公司分析' (both valid)",
        extraction="section_snippet",
        region="any",  # subsidiary data legitimately lives in MD&A OR notes; don't penalize either
        avoid=("在职员工", "员工的数量", "专业构成"),
    ),
    FieldSpec(
        key="risk_factors",
        label_cn="风险因素",
        definition="Risks the company may face going forward.",
        # Specific headings first (higher anchor priority). Reports vary widely:
        # "可能面对的风险" (展望 subsection), "（三）面临的风险和应对措施", "面临的
        # 主要风险", etc. `avoid` penalizes cross-reference pointers ("详见/请见
        # 本报告...重要提示") so the real risk section wins over a pointer sentence.
        anchors=("可能面对的风险", "可能面临的风险", "面临的风险和应对措施",
                 "面临的主要风险", "面临的风险", "风险因素", "公司面临的风险",
                 "风险提示", "应对措施"),
        expected_location="第三节 MD&A '公司未来发展的展望 - 可能面对的风险'",
        extraction="section_snippet",
        region="mda",
        avoid=("详见", "请见", "参见", "敬请"),
    ),
    FieldSpec(
        key="industry_discussion",
        label_cn="所处行业情况",
        definition="Discussion of the industry the company operates in.",
        anchors=("所处行业情况", "公司所处行业", "行业格局", "行业发展", "行业地位"),
        expected_location="第三节 MD&A '公司所处行业情况'",
        extraction="section_snippet",
        region="mda",
    ),
    FieldSpec(
        key="mda",
        label_cn="管理层讨论与分析",
        definition="Management discussion & analysis overview.",
        anchors=("管理层讨论与分析", "经营情况讨论与分析", "经营情况的讨论与分析"),
        expected_location="第三节",
        extraction="section_snippet",
        region="mda",
    ),
]


# ---------------------------------------------------------------------------
# Financial-firm profile (banks / insurers / brokers).
#
# EXPERIMENTAL / OPT-IN ONLY (via --profile financial). It is NOT auto-selected:
# on the held-out set a single generic financial profile regressed (it helped the
# insurer but hurt the broker, and auto-detection false-positived on firms with
# finance subsidiaries such as 贵州茅台). A production version needs separate
# bank / insurer / broker sub-schemas - tracked as future work.
#
# The industrial schema is the wrong shape for financials: there is no
# 主营业务分行业/分产品 table, no 前五名供应商, no product output table; segments
# are business lines (零售/批发金融, 寿险/产险, 经纪/投行/资管) and revenue is
# 利息净收入 / 手续费及佣金 / 已赚保费. Keys are kept IDENTICAL to the industrial
# profile so downstream output/aggregation is stable; inapplicable fields will
# simply come back not_found (no invented data).
# ---------------------------------------------------------------------------
FINANCIAL_FIELD_SPECS: list[FieldSpec] = [
    FieldSpec(
        key="main_business_segments",
        label_cn="主营业务/业务分部",
        definition="Business lines / reporting segments of a financial institution.",
        anchors=("主要业务分部", "业务分部", "经营分部", "主营业务", "主要业务", "业务概要"),
        expected_location="MD&A business-segment overview (零售/批发金融, 寿险/产险, 经纪/投行/资管)",
        extraction="section_snippet",
        region="mda",
        avoid=("持股比例", "注册资本"),
    ),
    FieldSpec(
        key="major_products",
        label_cn="主要产品及服务",
        definition="Principal financial products/services (often N/A as a discrete section).",
        anchors=("主要产品及服务", "产品和服务", "经营范围", "主要业务种类"),
        expected_location="business overview (may be N/A for financials)",
        extraction="section_snippet",
        region="mda",
        avoid=("持股比例", "注册资本"),
    ),
    FieldSpec(
        key="revenue_by_segment",
        label_cn="营业收入构成-分部",
        definition="Revenue/profit by business segment (interest/fee/insurance).",
        anchors=("分部业绩", "业务分部", "营业收入构成", "分部信息", "利息净收入"),
        expected_location="MD&A segment table or 营业收入构成",
        extraction="table",
        region="mda",
        table_match=("分部", "零售", "批发", "利息净收入", "手续费"),
        table_require=("收入", "利润", "营业"),
    ),
    FieldSpec(
        key="revenue_by_region",
        label_cn="营业收入构成-分地区",
        definition="Revenue/business by geographic region, if disclosed.",
        anchors=("地区分部", "按地区", "分地区", "境内", "境外"),
        expected_location="geographic segment table (large banks)",
        extraction="table",
        region="mda",
        table_match=("地区", "境内", "境外", "长三角", "环渤海"),
        table_require=("收入", "营业", "利润"),
    ),
    FieldSpec(
        key="top_customers",
        label_cn="客户集中度",
        definition="Customer concentration (e.g. largest-10-borrowers for banks).",
        anchors=("最大十家客户", "最大单一客户", "前五名客户", "客户集中度", "前十大客户"),
        expected_location="loan-concentration / customer-concentration disclosure",
        extraction="concentration",
        region="mda",
    ),
    FieldSpec(
        key="top_suppliers",
        label_cn="前五名供应商",
        definition="Top suppliers (generally N/A for financial institutions).",
        anchors=("前五名供应商", "主要供应商"),
        expected_location="usually N/A for financials",
        extraction="concentration",
        region="mda",
    ),
    FieldSpec(
        key="rnd_investment",
        label_cn="研发/科技投入",
        definition="R&D / fintech investment, if disclosed.",
        anchors=("研发投入", "科技投入", "信息科技投入", "金融科技投入"),
        expected_location="may be disclosed as 科技投入 (often N/A)",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="major_subsidiaries",
        label_cn="主要子公司",
        definition="Major subsidiaries / controlled entities.",
        anchors=("主要子公司", "主要控股参股公司", "附属公司", "主要控股公司", "纳入合并范围"),
        expected_location="财务报表附注 or MD&A subsidiary list",
        extraction="section_snippet",
        region="any",
        avoid=("在职员工", "员工的数量", "专业构成"),
    ),
    FieldSpec(
        key="risk_factors",
        label_cn="风险因素",
        definition="Principal risks / risk management.",
        anchors=("可能面对的风险", "主要风险", "风险因素", "风险管理", "面临的风险"),
        expected_location="MD&A risk section / 风险管理",
        extraction="section_snippet",
        region="mda",
    ),
    FieldSpec(
        key="industry_discussion",
        label_cn="所处行业/经营环境",
        definition="Industry / macro / operating-environment discussion.",
        anchors=("所处行业情况", "经营环境", "宏观经济", "行业格局", "行业发展"),
        expected_location="MD&A industry/environment section",
        extraction="section_snippet",
        region="mda",
    ),
    FieldSpec(
        key="mda",
        label_cn="管理层讨论与分析",
        definition="Management discussion & analysis overview.",
        anchors=("管理层讨论与分析", "经营情况讨论与分析", "经营情况的讨论与分析", "管理层讨论及分析"),
        expected_location="MD&A chapter",
        extraction="section_snippet",
        region="mda",
    ),
]

# Terms that signal a financial institution (bank/insurer/broker). Used to
# auto-select the profile from the report text - generic, not a company list.
FINANCIAL_TERMS = ("利息净收入", "吸收存款", "发放贷款", "已赚保费", "保险业务收入",
                   "手续费及佣金净收入", "经纪业务", "投资银行业务", "资产管理业务",
                   "净息差", "不良贷款", "偿付能力", "银行卡", "保户")


def detect_profile(pages: list[str], scan_pages: int = 80) -> str:
    """Return 'financial' or 'industrial' based on sector terms in the report."""
    text = " ".join(pages[:scan_pages])
    hits = sum(1 for t in FINANCIAL_TERMS if t in text)
    return "financial" if hits >= 3 else "industrial"


def get_field_specs(profile: str) -> list[FieldSpec]:
    return FINANCIAL_FIELD_SPECS if profile == "financial" else FIELD_SPECS


def keys() -> list[str]:
    return [f.key for f in FIELD_SPECS]

