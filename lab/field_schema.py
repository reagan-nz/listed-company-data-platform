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
# Financial sub-schemas (bank / broker / insurer / other_financial).
# Industrial FIELD_SPECS above is unchanged. Auto-selection of financial
# profiles during eval remains opt-in via company `financial: true` flag.
# ---------------------------------------------------------------------------

FIN_MDA = FieldSpec(
    key="mda",
    label_cn="管理层讨论与分析",
    definition="Management discussion & analysis overview.",
    anchors=("管理层讨论与分析", "经营情况讨论与分析", "经营情况的讨论与分析", "管理层讨论及分析"),
    expected_location="MD&A chapter",
    extraction="section_snippet",
    region="mda",
)

FIN_MAJOR_SUBSIDIARIES = FieldSpec(
    key="major_subsidiaries",
    label_cn="主要控股参股公司",
    definition="Major subsidiaries / controlled entities.",
    anchors=("主要子公司", "主要控股参股公司", "附属公司", "主要控股公司", "纳入合并范围"),
    expected_location="财务报表附注 or MD&A subsidiary list",
    extraction="section_snippet",
    region="any",
    avoid=("在职员工", "员工的数量", "专业构成"),
)

BANK_FIELD_SPECS: list[FieldSpec] = [
    FIN_MDA,
    FieldSpec(
        key="industry_discussion",
        label_cn="所处行业/经营环境",
        definition="Industry, macro, and regulatory environment discussion.",
        anchors=("所处行业情况", "经营环境", "宏观经济", "行业格局", "行业发展", "监管政策"),
        expected_location="MD&A industry/environment section",
        extraction="section_snippet",
        region="mda",
    ),
    FieldSpec(
        key="risk_factors",
        label_cn="风险因素",
        definition="Principal risks including credit, market, liquidity, and operational risk.",
        anchors=("可能面对的风险", "主要风险", "风险因素", "风险管理", "面临的风险",
                 "信用风险", "市场风险", "流动性风险", "操作风险"),
        expected_location="MD&A risk section / 风险管理",
        extraction="section_snippet",
        region="mda",
        avoid=("详见", "请见", "参见", "敬请"),
    ),
    FIN_MAJOR_SUBSIDIARIES,
    FieldSpec(
        key="main_business_segments",
        label_cn="主营业务/业务分部",
        definition="Business lines / reporting segments (retail, corporate, treasury, etc.).",
        anchors=("主要业务分部", "业务分部", "经营分部", "零售金融", "公司金融", "金融市场"),
        expected_location="MD&A business-segment overview",
        extraction="section_snippet",
        region="mda",
        avoid=("持股比例", "注册资本"),
    ),
    FieldSpec(
        key="net_interest_income",
        label_cn="利息净收入",
        definition="Net interest income.",
        anchors=("利息净收入", "净利息收入", "利息收入合计"),
        expected_location="MD&A or income-statement summary",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="non_interest_income",
        label_cn="非利息收入",
        definition="Non-interest income (fee and commission income, etc.).",
        anchors=("非利息收入", "手续费及佣金净收入", "中间业务收入"),
        expected_location="MD&A revenue composition",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="loan_structure",
        label_cn="贷款结构",
        definition="Loan portfolio breakdown (corporate, retail, bill discount, etc.).",
        anchors=("发放贷款", "贷款总额", "公司贷款", "个人贷款", "票据贴现"),
        expected_location="MD&A or notes '发放贷款及垫款'",
        extraction="table",
        region="mda",
        table_match=("贷款", "公司", "个人", "票据"),
        table_require=("贷款", "金额", "比例", "余额"),
    ),
    FieldSpec(
        key="deposit_structure",
        label_cn="存款结构",
        definition="Deposit breakdown (corporate vs personal deposits).",
        anchors=("吸收存款", "存款总额", "对公存款", "个人存款", "公司存款"),
        expected_location="MD&A or notes '吸收存款'",
        extraction="table",
        region="mda",
        table_match=("存款", "对公", "个人", "公司"),
        table_require=("存款", "金额", "比例", "余额"),
    ),
    FieldSpec(
        key="npl_ratio",
        label_cn="不良贷款率",
        definition="Non-performing loan ratio (%).",
        anchors=("不良贷款率", "不良率", "不良贷款比例"),
        expected_location="MD&A asset quality / risk management",
        extraction="numeric",
        region="mda",
        avoid=("变化", "上升", "下降"),
    ),
    FieldSpec(
        key="capital_adequacy_ratio",
        label_cn="资本充足率",
        definition="Capital adequacy ratio (%).",
        anchors=("资本充足率", "核心一级资本充足率", "一级资本充足率"),
        expected_location="MD&A capital management",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="provision_coverage_ratio",
        label_cn="拨备覆盖率",
        definition="Provision coverage ratio for loan loss reserves (%).",
        anchors=("拨备覆盖率", "贷款损失准备覆盖率"),
        expected_location="MD&A asset quality",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="regional_distribution",
        label_cn="地区分布",
        definition="Geographic revenue or asset distribution by region.",
        anchors=("地区分部", "分地区", "按地区", "长三角", "环渤海"),
        expected_location="MD&A geographic segment table (large banks)",
        extraction="table",
        region="mda",
        table_match=("地区", "境内", "境外", "长三角", "环渤海"),
        table_require=("收入", "营业", "利润", "资产"),
    ),
]

BROKER_FIELD_SPECS: list[FieldSpec] = [
    FIN_MDA,
    FieldSpec(
        key="industry_discussion",
        label_cn="所处行业/经营环境",
        definition="Industry, macro, and regulatory environment discussion.",
        anchors=("所处行业情况", "经营环境", "宏观经济", "行业格局", "行业发展", "监管政策"),
        expected_location="MD&A industry/environment section",
        extraction="section_snippet",
        region="mda",
    ),
    FieldSpec(
        key="risk_factors",
        label_cn="风险因素",
        definition="Principal risks and risk management.",
        anchors=("可能面对的风险", "主要风险", "风险因素", "风险管理", "面临的风险"),
        expected_location="MD&A risk section",
        extraction="section_snippet",
        region="mda",
        avoid=("详见", "请见", "参见", "敬请"),
    ),
    FIN_MAJOR_SUBSIDIARIES,
    FieldSpec(
        key="main_business_segments",
        label_cn="主营业务/业务分部",
        definition="Business lines (brokerage, IB, asset management, proprietary trading).",
        anchors=("主要业务分部", "业务分部", "经纪业务", "投资银行业务", "资产管理业务", "自营业务"),
        expected_location="MD&A business-segment overview",
        extraction="section_snippet",
        region="mda",
        avoid=("持股比例", "注册资本"),
    ),
    FieldSpec(
        key="brokerage_income",
        label_cn="经纪业务收入",
        definition="Brokerage / securities trading commission income.",
        anchors=("经纪业务", "经纪业务收入", "证券经纪"),
        expected_location="MD&A segment operating results",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="investment_banking_income",
        label_cn="投资银行业务收入",
        definition="Investment banking income.",
        anchors=("投资银行业务", "投行业务", "承销保荐"),
        expected_location="MD&A segment operating results",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="asset_management_income",
        label_cn="资产管理业务收入",
        definition="Asset management fee income.",
        anchors=("资产管理业务", "资管业务", "受托客户资产管理"),
        expected_location="MD&A segment operating results",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="proprietary_trading_income",
        label_cn="自营/投资收入",
        definition="Proprietary trading / investment income.",
        anchors=("自营业务", "投资收益", "公允价值变动损益"),
        expected_location="MD&A or income-statement summary",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="margin_lending_balance",
        label_cn="融资融券余额",
        definition="Margin financing and securities lending balance.",
        anchors=("融资融券", "融出资金", "融券"),
        expected_location="MD&A credit business",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="risk_control_indicators",
        label_cn="风险控制指标",
        definition="Net capital and regulatory risk-control ratios.",
        anchors=("净资本", "净资本与净资产", "风险覆盖率", "流动性覆盖率"),
        expected_location="MD&A risk-control indicators table",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="revenue_by_segment",
        label_cn="营业收入构成-分业务",
        definition="Revenue/profit by business segment.",
        anchors=("分部信息", "分业务", "营业收入构成", "手续费及佣金"),
        expected_location="MD&A segment operating table",
        extraction="table",
        region="mda",
        table_match=("分部", "经纪", "投行", "资管", "自营", "手续费"),
        table_require=("收入", "利润", "营业"),
    ),
]

INSURER_FIELD_SPECS: list[FieldSpec] = [
    FIN_MDA,
    FieldSpec(
        key="industry_discussion",
        label_cn="所处行业/经营环境",
        definition="Industry, macro, and regulatory environment discussion.",
        anchors=("所处行业情况", "经营环境", "宏观经济", "行业格局", "行业发展", "监管政策"),
        expected_location="MD&A industry/environment section",
        extraction="section_snippet",
        region="mda",
    ),
    FieldSpec(
        key="risk_factors",
        label_cn="风险因素",
        definition="Principal risks and risk management.",
        anchors=("可能面对的风险", "主要风险", "风险因素", "风险管理", "面临的风险"),
        expected_location="MD&A risk section",
        extraction="section_snippet",
        region="mda",
        avoid=("详见", "请见", "参见", "敬请"),
    ),
    FIN_MAJOR_SUBSIDIARIES,
    FieldSpec(
        key="main_business_segments",
        label_cn="主营业务/业务分部",
        definition="Insurance business lines (life, property, health, reinsurance).",
        anchors=("主要业务分部", "业务分部", "寿险", "产险", "健康险", "财产保险", "人身保险"),
        expected_location="MD&A business-segment overview",
        extraction="section_snippet",
        region="mda",
        avoid=("持股比例", "注册资本"),
    ),
    FieldSpec(
        key="premium_income",
        label_cn="保费/已赚保费",
        definition="Earned premium / gross written premium.",
        anchors=("已赚保费", "保险业务收入", "原保险保费收入"),
        expected_location="MD&A or income-statement summary",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="investment_income",
        label_cn="投资收益",
        definition="Investment income from insurance funds.",
        anchors=("投资收益", "净投资收益", "投资资产"),
        expected_location="MD&A investment business",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="claims_expense",
        label_cn="赔付/给付支出",
        definition="Claims and benefit payments.",
        anchors=("赔付支出", "给付支出", "退保金"),
        expected_location="MD&A or income-statement summary",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="solvency_ratio",
        label_cn="偿付能力充足率",
        definition="Solvency adequacy ratio (%).",
        anchors=("偿付能力充足率", "综合偿付能力", "核心偿付能力"),
        expected_location="MD&A solvency section",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="combined_ratio",
        label_cn="综合成本率",
        definition="Combined ratio (property insurers, optional).",
        anchors=("综合成本率", "赔付率", "费用率"),
        expected_location="MD&A operating metrics",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="embedded_value",
        label_cn="内含价值",
        definition="Embedded value (life insurers, optional).",
        anchors=("内含价值", "有效业务价值", "一年新业务价值"),
        expected_location="MD&A embedded value disclosure",
        extraction="numeric",
        region="mda",
    ),
    FieldSpec(
        key="revenue_by_segment",
        label_cn="营业收入构成-分险种",
        definition="Premium/income by insurance segment.",
        anchors=("分险种", "寿险", "产险", "保险业务收入", "分部信息"),
        expected_location="MD&A segment operating table",
        extraction="table",
        region="mda",
        table_match=("寿险", "产险", "险种", "分部"),
        table_require=("收入", "保费", "保险"),
    ),
]

OTHER_FINANCIAL_FIELD_SPECS: list[FieldSpec] = [
    FIN_MDA,
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
        key="risk_factors",
        label_cn="风险因素",
        definition="Principal risks / risk management.",
        anchors=("可能面对的风险", "主要风险", "风险因素", "风险管理", "面临的风险"),
        expected_location="MD&A risk section / 风险管理",
        extraction="section_snippet",
        region="mda",
        avoid=("详见", "请见", "参见", "敬请"),
    ),
    FIN_MAJOR_SUBSIDIARIES,
    FieldSpec(
        key="main_business_segments",
        label_cn="主营业务/业务分部",
        definition="Business lines / reporting segments of a financial institution.",
        anchors=("主要业务分部", "业务分部", "经营分部", "主营业务", "主要业务", "业务概要"),
        expected_location="MD&A business-segment overview",
        extraction="section_snippet",
        region="mda",
        avoid=("持股比例", "注册资本"),
    ),
    FieldSpec(
        key="revenue_by_segment",
        label_cn="营业收入构成-分部",
        definition="Revenue/profit by business segment.",
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
        expected_location="geographic segment table",
        extraction="table",
        region="mda",
        table_match=("地区", "境内", "境外", "长三角", "环渤海"),
        table_require=("收入", "营业", "利润"),
    ),
    FieldSpec(
        key="top_customers",
        label_cn="客户集中度",
        definition="Customer concentration, if disclosed.",
        anchors=("最大十家客户", "最大单一客户", "前五名客户", "客户集中度", "前十大客户"),
        expected_location="customer-concentration disclosure",
        extraction="concentration",
        region="mda",
    ),
]

# Backward-compatible alias for --profile financial
FINANCIAL_FIELD_SPECS = OTHER_FINANCIAL_FIELD_SPECS

PROFILE_FIELD_MAP: dict[str, list[FieldSpec]] = {
    "industrial": FIELD_SPECS,
    "bank": BANK_FIELD_SPECS,
    "broker": BROKER_FIELD_SPECS,
    "insurer": INSURER_FIELD_SPECS,
    "other_financial": OTHER_FINANCIAL_FIELD_SPECS,
    "financial": OTHER_FINANCIAL_FIELD_SPECS,
}

FINANCIAL_PROFILES = frozenset({"bank", "broker", "insurer", "other_financial", "financial"})

# Name-based hints (generic, not company-specific).
_BANK_NAME_KW = ("银行",)
_BROKER_NAME_KW = ("证券",)
_INSURER_NAME_KW = ("保险", "人寿", "财险", "再保险")
_FUTURES_NAME_KW = ("期货",)

# Text-based scoring terms for subtype detection.
BANK_TEXT_TERMS = ("利息净收入", "吸收存款", "发放贷款", "不良贷款", "资本充足率", "净息差")
BROKER_TEXT_TERMS = ("经纪业务", "投资银行业务", "资产管理业务", "手续费及佣金净收入", "融资融券", "净资本")
INSURER_TEXT_TERMS = ("已赚保费", "保险业务收入", "偿付能力", "赔付支出", "内含价值", "寿险", "产险")

# Legacy combined terms (used when subtype scores are inconclusive).
FINANCIAL_TERMS = BANK_TEXT_TERMS + BROKER_TEXT_TERMS + INSURER_TEXT_TERMS + (
    "银行卡", "保户", "信托",
)


def is_financial_profile(profile: str) -> bool:
    return profile in FINANCIAL_PROFILES


def _profile_from_name(name: str) -> str | None:
    """Return a financial subtype from company short name, or None if unclear."""
    n = (name or "").strip()
    if not n:
        return None
    if any(k in n for k in _INSURER_NAME_KW):
        return "insurer"
    if any(k in n for k in _BROKER_NAME_KW):
        return "broker"
    if any(k in n for k in _FUTURES_NAME_KW):
        return "other_financial"
    if any(k in n for k in _BANK_NAME_KW):
        return "bank"
    return None


def _profile_from_text(text: str) -> str | None:
    """Score report text for bank / broker / insurer subtype."""
    scores = {
        "bank": sum(1 for t in BANK_TEXT_TERMS if t in text),
        "broker": sum(1 for t in BROKER_TEXT_TERMS if t in text),
        "insurer": sum(1 for t in INSURER_TEXT_TERMS if t in text),
    }
    best = max(scores, key=scores.get)
    if scores[best] >= 2:
        return best
    if sum(scores.values()) >= 3:
        return "other_financial"
    return None


def detect_profile(
    pages: list[str],
    scan_pages: int = 80,
    *,
    short_name: str = "",
    industry: str = "",
    financial: bool = False,
) -> str:
    """Return industrial or a financial subtype (bank/broker/insurer/other_financial).

    Name hints (short_name / industry) take priority over text scoring.
    When ``financial`` is True but subtype is unclear, returns other_financial.
    """
    by_name = _profile_from_name(short_name) or _profile_from_name(industry)
    if by_name:
        return by_name
    text = " ".join(pages[:scan_pages]) if pages else ""
    if text:
        by_text = _profile_from_text(text)
        if by_text:
            return by_text
    if financial:
        return "other_financial"
    if text and sum(1 for t in FINANCIAL_TERMS if t in text) >= 3:
        return "other_financial"
    return "industrial"


def resolve_profile(
    pages: list[str] | None = None,
    *,
    short_name: str = "",
    industry: str = "",
    financial: bool = False,
    explicit: str = "auto",
) -> str:
    """Resolve schema profile from CLI flag, company metadata, and/or report text."""
    if explicit and explicit not in ("auto", ""):
        p = explicit
        return "other_financial" if p == "financial" else p
    if financial:
        return detect_profile(pages or [], short_name=short_name, industry=industry, financial=True)
    return "industrial"


def get_field_specs(profile: str) -> list[FieldSpec]:
    return PROFILE_FIELD_MAP.get(profile, FIELD_SPECS)


def keys(profile: str = "industrial") -> list[str]:
    return [f.key for f in get_field_specs(profile)]


def profile_field_count(profile: str) -> int:
    return len(get_field_specs(profile))

