"""Financial-only automated strict audit for full_market_2024.

Read-only over outputs; does not modify profiles, eval_results, PDFs, or extraction.
Separate from non-financial 11-field strict headline (9.43/11).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.extract_annual_report import (  # noqa: E402
    _numeric_magnitude,
    _table_row_is_data_row,
    revenue_table_plausible,
    rnd_investment_plausible,
)
from lab.field_schema import FieldSpec, get_field_specs  # noqa: E402

DEFAULT_OUT = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
DEFAULT_YAML = os.path.join(_PROJECT_ROOT, "lab", "eval_companies_full_market_2024.yaml")

SUBTYPE_CAVEAT_CODES = frozenset({"000402", "600816", "600318"})

POINTER_KW = ("详见", "参见", "请见", "见下文", "见本报告", "见上述", "见附注")
FIN_BOILER_KW = (
    "金融工具", "公允价值", "《企业会计准则", "法律法规", "监管要求", "套期保值",
    "免责声明", "本报告内容", "备查文件",
)
LEGAL_DISCLAIMER_KW = ("不承担", "不构成投资建议", "投资者应当")

RATIO_FIELDS = frozenset({
    "npl_ratio", "capital_adequacy_ratio", "provision_coverage_ratio",
    "solvency_ratio", "combined_ratio",
})

AMOUNT_NOISE_LABELS = (
    "页码", "单位", "币种", "人民币", "百万元", "千元", "附注",
)

# Wrong-line-item labels for specific fields (numeric noise).
FIELD_REJECT_LABELS: dict[str, tuple[str, ...]] = {
    "net_interest_income": ("营业收入", "营业总收入", "利润总额"),
    "non_interest_income": ("营业收入", "营业成本"),
    "brokerage_income": ("营业收入", "营业总收入"),
    "premium_income": ("营业总收入", "净利润"),
    "npl_ratio": (
        "拨备", "覆盖率", "资本充足", "合计", "总额", "金额", "余额", "占比",
        "不良率增减", "较上年", "制造业", "房地产业", "批发和零售", "建筑业",
        "长江三角洲", "珠江三角洲", "环渤海", "中部地区", "西部地区", "东北地区",
        "长三角", "京津冀", "成渝",
    ),
    "capital_adequacy_ratio": ("不良", "拨备", "优先股", "转为", "触发"),
    "provision_coverage_ratio": ("不良", "资本充足", "优先股"),
}

# #30b: ratio context that indicates industry narrative or wrong semantic source.
_RATIO_INDUSTRY_NARRATIVE = (
    "银行业运行", "商业银行正积极", "主要风险指标处于合理区间",
    "整体而言，2024 年银行业", "银行要发挥好主力军", "全球经济延续低增长",
    "全面加强风险内控管理", "为经济社会发展提供高质量金融服务",
)
_RATIO_PREFERRED_SHARE_TRIGGER = (
    "优先股", "转为A股", "转为 a 股", "强制转股", "则境内优先",
    "核心一级资本充足率降至", "促使核心一级资本充足率恢复",
)
_NPL_WRONG_LABELS = (
    "合计", "总额", "金额", "余额", "占比", "不良率增减", "较上年",
)
_REGIONAL_NPL_LABELS = (
    "长江三角洲", "珠江三角洲", "环渤海", "中部地区", "西部地区", "东北地区",
    "长三角", "京津冀", "成渝", "制造业", "房地产业", "批发和零售", "建筑业",
    "电力、热力", "交通运输", "采矿业", "农、林、牧",
)

# #30b: major_subsidiaries section routing.
_MAJOR_SUBSIDIARY_VOCAB = (
    "子公司", "控股", "参股", "持股比例", "注册资本", "主要子公司", "主要控股",
    "附属公司", "主要子公司情况", "参股公司情况",
)
_MAJOR_SUBSIDIARY_WRONG_SECTION = (
    "在职员工", "在職員工", "员工数量", "业务资格", "专业构成", "專業構成",
    "学历类别", "學歷", "离退休", "離退休", "人均创收", "员工情况", "需承担费用的离退休",
)
_MAJOR_SUBSIDIARY_TABLE_HEADERS = (
    "主要子公司", "主要控股参股", "子公司名称", "主要子公司情况", "附属公司",
    "参股公司情况", "主要控股参股公司情况",
)

# #30b: financial table reject/plausibility vocabulary.
_LOAN_TABLE_REJECT = (
    "利息收入", "利息净收入", "存放中央银行", "拆出资金", "存放同业",
    "金融投资", "现金及存放中央银行", "资产总额", "报告期，集团实现利息",
    "到期日", "到期期限", "剩余期限", "到期时间", "逾期", "现金流量",
)
_LOAN_TABLE_REQUIRE = (
    "贷款结构", "按产品", "按担保", "按行业", "五级分类", "公司贷款", "个人贷款",
    "票据贴现", "垫款", "信用贷款", "保证贷款", "抵押贷款", "质押贷款",
    "发放贷款和垫款",
)
_DEPOSIT_TABLE_REJECT = (
    "长期股权投资", "应付职工薪酬", "应交税费", "现金流量", "利息支出",
    "卖出回购", "应付债券", "向中央银行借款", "同业及其他金融机构存放",
    "负债合计", "负债总额", "负债结构", "到期日", "到期期限",
)
_REGIONAL_TABLE_REJECT = (
    "营业网点", "分支机构数量", "机构数量", "证券持仓", "债券投资", "持有至到期",
    "可供出售", "股权投资", "地址：", "邮编：", "电话：",
    "营业网点及分公司", "分行", "支行", "营业部", "网点分布",
)
_REVENUE_TABLE_REJECT = (
    "现金流量", "经营活动", "收取利息", "投资活动", "筹资活动",
    "业务及管理费", "税金及附加", "减值损失", "其他业务成本",
    "EV", "敏感性", "变动分析", "风险限额", "母公司利润表", "合并利润表",
    "手续费及佣金的现金", "代理买卖证券", "拆入资金", "回购业务",
    "利息净收入", "利息支出", "投资收益（损", "公允价值变动",
    "营业总支出", "股票价格", "上升5%", "下降5%", "敏感性测试",
)
_REVENUE_TABLE_REQUIRE = (
    "营业收入", "营业总收入", "分部报告", "主营业务分", "分行业", "分产品", "分地区",
    "期货经纪", "财富管理", "资产管理", "投资银行", "证券经纪", "营业总收入",
)

# #30f: insurer-specific semantic guards (n=2, keep narrow).
_INSURER_NUMERIC_FIELDS = frozenset({
    "premium_income", "investment_income", "claims_expense",
    "solvency_ratio", "combined_ratio", "embedded_value",
})
_INSURER_SENSITIVITY_KW = (
    "敏感性测试", "内含价值敏感性", "情景", "赔付率提高", "费用率提高", "费用率降低",
    "死亡率提高", "死亡率降低", "退保率提高", "退保率降低",
)
_INSURER_COMBINED_STRONG = ("综合成本率",)
_INSURER_CLAIMS_ACCEPT = (
    "赔付支出", "赔款支出", "赔付及给付", "赔付及给付支出", "赔款及给付",
)
_INSURER_CLAIMS_REJECT = (
    "退保金", "保单红利", "提取保险责任准备金", "手续费",
    "产品", "渠道", "标准保费",
)
_INSURER_INVESTMENT_ACCEPT = ("总投资收益", "净投资收益", "投资收益")
_INSURER_SOLVENCY_ACCEPT = (
    "综合偿付能力充足率", "综合偿付能力", "核心偿付能力充足率",
    "核心偿付能力", "偿付能力充足率",
)
_INSURER_SEGMENT_LABELS = (
    "寿险业务", "健康险业务", "意外险业务", "保险业务", "年金业务",
)
_INSURER_SEGMENT_VALUE_KW = (
    "已赚保费", "保险业务收入", "原保险保费收入", "总保费", "首年业务", "续期业务",
)

# Broker numeric fields use stricter PDF missed-disclosure checks (#30a).
BROKER_NUMERIC_FIELDS = frozenset({
    "brokerage_income",
    "investment_banking_income",
    "asset_management_income",
    "proprietary_trading_income",
    "margin_lending_balance",
    "risk_control_indicators",
})

# Strong line-item / table labels — anchor + nearby digit alone is insufficient.
BROKER_MISSED_STRONG_LABELS: dict[str, tuple[str, ...]] = {
    "brokerage_income": (
        "经纪业务收入",
        "证券经纪业务收入",
        "经纪业务手续费净收入",
        "经纪业务净收入",
        "证券经纪业务净收入",
    ),
    "investment_banking_income": (
        "投资银行业务收入",
        "投资银行业务净收入",
        "投行业务净收入",
        "投资银行业务手续费净收入",
        "承销保荐业务收入",
        "投资银行类业务收入",
    ),
    "asset_management_income": (
        "资产管理业务收入",
        "资管业务收入",
        "资产管理业务净收入",
        "受托客户资产管理业务净收入",
    ),
    "proprietary_trading_income": (
        "自营业务收入",
        "自营业务净收入",
        "证券自营业务收入",
        "证券投资业务收入",
    ),
    "margin_lending_balance": (
        "融资融券余额",
    ),
    "risk_control_indicators": (
        "净资本",
        "核心净资本",
        "风险覆盖率",
        "资本杠杆率",
        "流动性覆盖率",
        "净稳定资金率",
    ),
}

# Generic anchors too weak to justify not_found_missed on their own.
BROKER_MISSED_WEAK_ONLY: dict[str, tuple[str, ...]] = {
    "proprietary_trading_income": ("投资收益", "公允价值变动损益"),
    "brokerage_income": ("经纪业务", "证券经纪"),
    "investment_banking_income": ("承销保荐",),
    "asset_management_income": ("受托客户资产管理",),
    "margin_lending_balance": ("融资融券", "融券"),
    "risk_control_indicators": ("净资本与净资产",),
}

_FIN_NUM_RE = re.compile(
    r"[%％]|(?:万元|亿元|百万元|千元)|\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d{2,}"
)
_BROKER_BALANCE_NUM_RE = re.compile(
    r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d{4,}(?:\.\d+)?"
)
_BROKER_RATIO_NUM_RE = re.compile(r"\d+(?:\.\d+)?\s*[%％]")
_BROKER_COMMA_AMOUNT_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?")
_BROKER_ASSET_COMPOSITION_RE = re.compile(
    r"融出\s*资\s*金\s+"
    r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?)\s+(\d+\.\d{2})\s+"
    r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?)\s+(\d+\.\d{2})\s+(\d+\.\d{2})"
)
_BROKER_SEGMENT_SECTION_MARKERS = (
    "主营业务分行业",
    "主营业务分产品",
    "分行业情况",
    "分产品情况",
    "收入和成本分析",
)
_BROKER_WEAK_WINDOW_MARKERS = (
    "学历", "简历", "董事", "监事", "总裁", "副总经理", "首席财务",
    "是指向客户出借", "业务是运用", "业务是通过", "主要从事",
    "奖", "论坛", "证券时报", "每日经济新闻", "中国基金报",
    "注册资本", "总资产", "净资产", "上年年末", "报告期末",
    "利息收入", "利息支出", "净增加额", "净减少额", "净增加现金",
    "万亿", "全行业", "市场累计", "较上年末增长",
    "账户规范", "管理制度", "合规风险", "盯市监控",
    "监管要求", "符合监管", "指标情况，优化", "指标情况，优化设定",
    "日均余额", "同比增幅", "规范管理情况",
    "代理承销证券", "代理买卖证券款",
    "A 股", "A股 指",
)
_BROKER_DEEP_IB_NET_LABELS = (
    "投资银行业务净收入",
    "投行业务净收入",
)
_BROKER_DEEP_IB_MIN_MAGNITUDE = 1_000_000_000


@dataclass
class FinAuditRow:
    code: str
    name: str
    board: str
    schema_profile: str
    field: str
    extraction_type: str
    status: str
    proxy_plausible: bool
    strict_label: str
    reason: str
    value_preview: str
    evidence_sentence: str
    page: str
    source_url: str
    subtype_caveat_flag: bool


def _load_meta(yaml_path: str) -> dict[str, dict]:
    data = yaml.safe_load(open(yaml_path, encoding="utf-8")) or {}
    return {str(c["stock_code"]): c for c in data.get("companies", [])}


def _profile_path(out_dir: str, code: str, board: str) -> str | None:
    for rel in (f"{code}/company_profile.json", f"{board}/{code}/company_profile.json"):
        p = os.path.join(out_dir, rel)
        if os.path.isfile(p):
            return p
    return None


def _pdf_path(out_dir: str, code: str, board: str) -> str | None:
    p = os.path.join(out_dir, board, code, f"{code}.pdf")
    return p if os.path.isfile(p) else None


def _field_map(profile: dict) -> dict[str, dict]:
    return {f["field"]: f for f in profile.get("fields", [])}


def _is_pointer_only(text: str) -> bool:
    t = (text or "").strip()
    if len(t) >= 80:
        return False
    return any(p in t for p in POINTER_KW)


def value_preview(field: dict, limit: int = 160) -> str:
    v = field.get("value")
    if v is None:
        return ""
    if isinstance(v, str):
        text = v
    elif isinstance(v, dict) and "labeled" in v:
        pairs = "; ".join(f"{p.get('label')}={p.get('value')}" for p in v.get("labeled", [])[:4])
        text = pairs or v.get("context", "")
    elif isinstance(v, dict) and "ratio" in v:
        text = f"amount={v.get('amount') or 'n/a'} ratio={v.get('ratio') or 'n/a'}"
    elif isinstance(v, dict) and "rows" in v:
        rows = v.get("rows", [])
        head = " / ".join(" | ".join(str(c) for c in r) for r in rows[:2])
        text = f"[table p.{v.get('table_page')} hits={v.get('match_hits')}] {head}"
    else:
        text = str(v)
    text = " ".join(text.split())
    return text[:limit] + ("..." if len(text) > limit else "")


def field_plausible(f: dict) -> bool:
    if f.get("status") != "found":
        return False
    ex = f.get("extraction")
    v = f.get("value")
    if ex == "section_snippet":
        return isinstance(v, str) and len(v) >= 25
    if ex == "numeric":
        if f.get("field") == "rnd_investment":
            return rnd_investment_plausible(v)
        return isinstance(v, dict) and any(
            any(c.isdigit() for c in (x.get("value") or "")) for x in v.get("labeled", [])
        )
    if ex == "concentration":
        return isinstance(v, dict) and bool(v.get("ratio") or v.get("amount"))
    if ex == "table":
        fk = f.get("field")
        if fk in ("revenue_by_region", "revenue_by_segment"):
            return revenue_table_plausible(v)
        return isinstance(v, dict) and bool(v.get("rows")) and v.get("match_hits", 0) >= 1
    return False


def _looks_like_ratio_value(val: str) -> bool:
    s = (val or "").strip()
    if not s or not any(c.isdigit() for c in s):
        return False
    if re.search(r"[%％]", s):
        return True
    mag = _numeric_magnitude(s)
    if mag is None:
        return False
    if mag >= 1_000_000:
        return False
    if any(u in s for u in ("万元", "亿元", "千元", "百万元")):
        return False
    return 0 <= mag <= 500


def _looks_like_amount_value(val: str) -> bool:
    s = (val or "").strip()
    if not s or not any(c.isdigit() for c in s):
        return False
    mag = _numeric_magnitude(s)
    if mag is None:
        return False
    if re.search(r"[%％]", s) and mag <= 100:
        return False
    return mag >= 100 or any(u in s for u in ("万元", "亿元", "千元", "百万元", "元"))


def _anchor_in_text(text: str, anchors: tuple[str, ...]) -> bool:
    t = text or ""
    return any(a in t for a in anchors)


def _is_year_token(val: str) -> bool:
    s = re.sub(r"[^\d]", "", val or "")
    return len(s) == 4 and s.startswith("20")


def _is_insurer_numeric_field(fk: str, spec: FieldSpec) -> bool:
    return fk in _INSURER_NUMERIC_FIELDS


def _insurer_has_sensitivity(ctx: str, ev: str = "") -> bool:
    combined = (ctx or "") + " " + (ev or "")
    return any(k in combined for k in _INSURER_SENSITIVITY_KW)


def _insurer_business_line_snippet(text: str) -> bool:
    t = text or ""
    if sum(1 for k in _INSURER_SEGMENT_LABELS if k in t) < 2:
        return False
    if not any(k in t for k in _INSURER_SEGMENT_VALUE_KW):
        return False
    return bool(re.search(r"\d{2,3}(?:,\d{3})+|\d{4,}", t))


def _insurer_ratio_from_context(labels: tuple[str, ...], ctx: str, ev: str = "") -> str | None:
    text = (ctx or "") + " " + (ev or "")
    for lab in labels:
        m = re.search(re.escape(lab) + r".{0,20}?(\d+(?:\.\d+)?\s*[%％])", text)
        if m:
            return m.group(1).strip()
    return None


def _evaluate_insurer_numeric(
    fk: str,
    labeled: list,
    ctx: str,
    ev: str,
    spec: FieldSpec,
) -> tuple[str, str] | None:
    combined = (ctx or "") + " " + (ev or "")

    if fk == "combined_ratio":
        if _insurer_has_sensitivity(ctx, ev):
            return "wrong", "insurer sensitivity/EV page, not combined ratio"
        for item in labeled:
            lab = (item.get("label") or "").strip()
            num = (item.get("value") or "").strip()
            if any(k in lab for k in _INSURER_COMBINED_STRONG) and _looks_like_ratio_value(num):
                return "usable", f"insurer combined ratio '{lab}' value={num}"
        return "wrong", "missing exact insurer combined-ratio label"

    if fk == "claims_expense":
        if _insurer_has_sensitivity(ctx, ev):
            return "wrong", "insurer sensitivity page, not claims expense"
        saw_reject = False
        for item in labeled:
            lab = (item.get("label") or "").strip()
            num = (item.get("value") or "").strip()
            if any(k in lab for k in _INSURER_CLAIMS_REJECT) or any(k in combined for k in _INSURER_CLAIMS_REJECT):
                saw_reject = True
                continue
            if any(k in lab for k in _INSURER_CLAIMS_ACCEPT) and _looks_like_amount_value(num) and not _is_year_token(num):
                return "usable", f"insurer claims label '{lab}' value={num}"
        if saw_reject:
            return "wrong", "insurer claims field hit surrender/dividend/reserve/product context"
        return "wrong", "missing exact insurer claims-expense label"

    if fk == "investment_income":
        if _insurer_has_sensitivity(ctx, ev):
            return "wrong", "insurer sensitivity/EV page, not investment income"
        ranked: list[tuple[int, float, str, str]] = []
        for item in labeled:
            lab = (item.get("label") or "").strip()
            num = (item.get("value") or "").strip()
            mag = _numeric_magnitude(num)
            if _is_year_token(num) or mag is None:
                continue
            if any(k in lab for k in _INSURER_INVESTMENT_ACCEPT):
                if not _looks_like_amount_value(num) or mag < 1000:
                    continue
                rank = 3 if "总投资收益" in combined else (2 if "净投资收益" in combined else 1)
                ranked.append((rank, mag, lab, num))
        if ranked:
            ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
            _, _, lab, num = ranked[0]
            return "usable", f"insurer investment label '{lab}' value={num}"
        return "wrong", "insurer investment field only has year/tiny fragment values"

    if fk == "solvency_ratio":
        for item in labeled:
            lab = (item.get("label") or "").strip()
            num = (item.get("value") or "").strip()
            if any(k in lab for k in _INSURER_SOLVENCY_ACCEPT) and _looks_like_ratio_value(num) and not _is_year_token(num):
                mag = _numeric_magnitude(num)
                if mag is not None and mag >= 10:
                    return "usable", f"insurer solvency label '{lab}' value={num}"
        ratio = _insurer_ratio_from_context(_INSURER_SOLVENCY_ACCEPT, ctx, ev)
        if ratio:
            return "usable", f"insurer solvency ratio from context value={ratio}"
        return "wrong", "missing insurer solvency ratio value"

    return None


def _pdf_anchor_with_number(pdf_path: str | None, anchors: tuple[str, ...], max_pages: int = 80) -> bool:
    """Conservative missed-disclosure check: anchor + financial-looking number nearby."""
    if not pdf_path or not os.path.isfile(pdf_path):
        return False
    try:
        import fitz
    except ImportError:
        return False
    try:
        doc = fitz.open(pdf_path)
        n = min(len(doc), max_pages)
        for i in range(n):
            text = doc[i].get_text()
            for a in anchors:
                pos = 0
                while True:
                    idx = text.find(a, pos)
                    if idx < 0:
                        break
                    window = text[idx : idx + 100]
                    if _FIN_NUM_RE.search(window):
                        doc.close()
                        return True
                    pos = idx + max(len(a), 1)
        doc.close()
    except Exception:
        return False
    return False


def _window_has_fin_number(window: str, *, ratio_ok: bool = True, balance_ok: bool = True) -> bool:
    if ratio_ok and _BROKER_RATIO_NUM_RE.search(window):
        return True
    if balance_ok and _BROKER_BALANCE_NUM_RE.search(window):
        return True
    return bool(_FIN_NUM_RE.search(window))


def _window_has_comma_amount(window: str) -> bool:
    return bool(_BROKER_COMMA_AMOUNT_RE.search(window))


def _page_has_segment_operating_section(text: str) -> bool:
    return any(m in text for m in _BROKER_SEGMENT_SECTION_MARKERS)


def _page_is_fee_commission_note(text: str) -> bool:
    return any(
        m in text
        for m in ("手续费及佣金净收入", "手续费及佣金", "按收入类别列示")
    )


def _page_is_main_financial_items(text: str) -> bool:
    return any(
        m in text
        for m in (
            "主要财务指标",
            "主要项目",
            "合并财务报表主要项目",
            "母公司财务报表主要项目",
            "增减幅度（%）",
            "增减幅度(%)",
        )
    )


def _find_spaced_keyword(text: str, keyword: str) -> int:
    pattern = r"\s*".join(re.escape(ch) for ch in keyword)
    match = re.search(pattern, text)
    return match.start() if match else -1


def _iter_spaced_keyword_positions(text: str, keyword: str):
    pattern = r"\s*".join(re.escape(ch) for ch in keyword)
    for match in re.finditer(pattern, text):
        yield match.start(), match.group(0)


def _keyword_match_has_internal_break(matched: str, keyword: str) -> bool:
    normalized = re.sub(r"\s+", "", matched)
    return normalized == keyword and matched != keyword


def _window_is_weak_broker_evidence(field_key: str, window: str, page_text: str) -> bool:
    if any(m in window for m in _BROKER_WEAK_WINDOW_MARKERS):
        return True
    if field_key != "proprietary_trading_income":
        if "投资收益" in window or "公允价值变动损益" in window:
            return True
    if field_key == "margin_lending_balance":
        if any(m in window for m in ("利息", "净增加", "净减少", "减值", "万亿")):
            return True
        if _page_is_main_financial_items(page_text):
            return True
    if field_key == "risk_control_indicators":
        return True
    if _page_is_fee_commission_note(page_text) and field_key in {
        "brokerage_income",
        "asset_management_income",
        "proprietary_trading_income",
    }:
        return True
    return False


def _pdf_strong_label_with_number(
    text: str,
    labels: tuple[str, ...],
    *,
    window_extra: int = 80,
    ratio_ok: bool = True,
    balance_ok: bool = True,
    comma_only: bool = False,
) -> bool:
    for lab in labels:
        pos = 0
        while True:
            idx = text.find(lab, pos)
            if idx < 0:
                break
            window = text[idx : idx + len(lab) + window_extra]
            if comma_only and not _window_has_comma_amount(window):
                pos = idx + max(len(lab), 1)
                continue
            if _window_has_fin_number(
                window, ratio_ok=ratio_ok, balance_ok=balance_ok,
            ):
                return True
            pos = idx + max(len(lab), 1)
    return False


def _pdf_broker_segment_operating_evidence(
    text: str,
    segment_kw: tuple[str, ...],
    *,
    field_key: str = "",
    require_internal_label_break: bool = False,
) -> bool:
    """MD&A segment operating row: section header + segment + comma amount + margin/YoY."""
    if not _page_has_segment_operating_section(text):
        return False
    metric_markers = ("百分点", "毛利率", "营业成本", "比上年", "同比")
    income_phrases = (
        "实现收入",
        "业务收入",
        "业务净收入",
        "手续费净收入",
        "净收入",
    )
    for seg in segment_kw:
        for idx, matched in _iter_spaced_keyword_positions(text, seg):
            if require_internal_label_break and not _keyword_match_has_internal_break(
                matched, seg,
            ):
                continue
            window = text[idx : idx + 140]
            if not _window_has_comma_amount(window):
                continue
            if not (
                any(m in window for m in metric_markers)
                or any(p in window for p in income_phrases)
            ):
                continue
            if _window_is_weak_broker_evidence(field_key, window, text):
                continue
            return True
    return False


def _pdf_broker_strong_label_in_segment(text: str, labels: tuple[str, ...]) -> bool:
    if not _page_has_segment_operating_section(text):
        return False
    if _page_is_fee_commission_note(text):
        return False
    return _pdf_strong_label_with_number(
        text, labels, comma_only=True, ratio_ok=False, balance_ok=False,
    )


def _pdf_broker_deep_ib_net_income_evidence(
    pdf_path: str,
    *,
    start_page: int = 80,
    max_pages: int = 350,
) -> bool:
    """Large-broker IB net income in financial statement notes (600030-style)."""
    try:
        import fitz
    except ImportError:
        return False
    try:
        doc = fitz.open(pdf_path)
        n = min(len(doc), max_pages)
        for i in range(start_page, n):
            text = doc[i].get_text()
            if not (
                _page_is_fee_commission_note(text)
                or "年度财务报表" in text
            ):
                continue
            for lab in _BROKER_DEEP_IB_NET_LABELS:
                pos = 0
                while True:
                    idx = text.find(lab, pos)
                    if idx < 0:
                        break
                    window = text[idx : idx + len(lab) + 60]
                    match = _BROKER_COMMA_AMOUNT_RE.search(window)
                    if match:
                        mag = _numeric_magnitude(match.group(0))
                        if mag is not None and mag >= _BROKER_DEEP_IB_MIN_MAGNITUDE:
                            doc.close()
                            return True
                    pos = idx + max(len(lab), 1)
        doc.close()
    except Exception:
        return False
    return False


def _pdf_broker_margin_balance_evidence(text: str) -> bool:
    """MD&A asset composition 融出资金 row — not main-fin items or cash-flow noise."""
    if _page_is_main_financial_items(text):
        return False
    if "(二) 非主营业务" not in text:
        return False
    if not _BROKER_ASSET_COMPOSITION_RE.search(text.replace("\n", " ")):
        return False
    noise = (
        "净增加额", "净减少额", "利息收入", "利息支出", "减值", "现金流量",
        "预期信用", "坏账准备", "万亿",
    )
    for match in _BROKER_ASSET_COMPOSITION_RE.finditer(text.replace("\n", " ")):
        window = match.group(0)
        if not any(n in window for n in noise):
            return True
    return False


def _pdf_broker_proprietary_trading_evidence(text: str) -> bool:
    labels = BROKER_MISSED_STRONG_LABELS["proprietary_trading_income"]
    if _pdf_strong_label_with_number(
        text, labels, comma_only=True, ratio_ok=False, balance_ok=False,
    ):
        return True
    return _pdf_broker_segment_operating_evidence(
        text, ("自营业务", "证券自营业务", "证券投资业务"),
        field_key="proprietary_trading_income",
    )


def _pdf_broker_field_missed_evidence(
    pdf_path: str | None,
    field_key: str,
    spec: FieldSpec,
    profile_fields: dict[str, dict] | None = None,
    max_pages: int = 350,
) -> bool:
    """Stricter broker missed-disclosure check (#30a).

    Generic anchor + digit is insufficient. Field-specific table/segment rows only.
    """
    if not pdf_path or not os.path.isfile(pdf_path) or field_key not in BROKER_NUMERIC_FIELDS:
        return False

    if field_key in {"risk_control_indicators", "brokerage_income"}:
        return False

    if field_key == "asset_management_income":
        brokerage = (profile_fields or {}).get("brokerage_income") or {}
        if brokerage.get("status") == "found":
            return False

    try:
        import fitz
    except ImportError:
        return False

    try:
        doc = fitz.open(pdf_path)
        n = min(len(doc), max_pages)
        for i in range(n):
            text = doc[i].get_text()

            if field_key == "brokerage_income":
                pass  # handled above — no PDF promotion (#30a over-call guard)

            elif field_key == "investment_banking_income":
                if _pdf_broker_segment_operating_evidence(
                    text,
                    ("投资银行业务", "投行业务", "投资银行类业务"),
                    field_key="investment_banking_income",
                    require_internal_label_break=True,
                ):
                    doc.close()
                    return True
                if _pdf_broker_strong_label_in_segment(
                    text, BROKER_MISSED_STRONG_LABELS["investment_banking_income"],
                ):
                    doc.close()
                    return True

            elif field_key == "asset_management_income":
                if _pdf_broker_segment_operating_evidence(
                    text, ("资产管理业务", "资管业务"), field_key="asset_management_income",
                ):
                    doc.close()
                    return True
                if _pdf_broker_strong_label_in_segment(
                    text, BROKER_MISSED_STRONG_LABELS["asset_management_income"],
                ):
                    doc.close()
                    return True

            elif field_key == "proprietary_trading_income":
                if _pdf_broker_proprietary_trading_evidence(text):
                    doc.close()
                    return True

            elif field_key == "margin_lending_balance":
                if _pdf_broker_margin_balance_evidence(text):
                    doc.close()
                    return True

        doc.close()
    except Exception:
        return False

    if field_key == "investment_banking_income":
        return _pdf_broker_deep_ib_net_income_evidence(pdf_path, max_pages=max_pages)
    return False


def _pdf_not_found_missed_evidence(
    pdf_path: str | None,
    field_key: str,
    spec: FieldSpec,
    profile_fields: dict[str, dict] | None = None,
) -> bool:
    if field_key in BROKER_NUMERIC_FIELDS and spec.extraction == "numeric":
        return _pdf_broker_field_missed_evidence(
            pdf_path, field_key, spec, profile_fields=profile_fields,
        )
    return _pdf_anchor_with_number(pdf_path, spec.anchors)


def _ratio_context_industry_narrative(ctx: str, ev: str = "") -> bool:
    combined = (ctx or "") + (ev or "")
    return any(m in combined for m in _RATIO_INDUSTRY_NARRATIVE)


def _ratio_context_preferred_share_trigger(ctx: str, ev: str = "") -> bool:
    combined = (ctx or "") + (ev or "")
    return any(m in combined for m in _RATIO_PREFERRED_SHARE_TRIGGER)


def _npl_label_is_wrong_line_item(label: str) -> bool:
    lab = (label or "").strip()
    if not lab:
        return True
    if any(r in lab for r in _NPL_WRONG_LABELS):
        return True
    if any(r in lab for r in _REGIONAL_NPL_LABELS):
        return True
    if lab in ("不良率",) and "不良贷款率" not in lab:
        return True
    return False


def _major_subsidiaries_wrong_section(combined: str) -> bool:
    return any(m in combined for m in _MAJOR_SUBSIDIARY_WRONG_SECTION)


def _major_subsidiaries_structured_only(combined: str) -> bool:
    if "结构化主体" not in combined:
        return False
    if any(h in combined for h in _MAJOR_SUBSIDIARY_TABLE_HEADERS):
        return False
    if re.search(r"子公司名称|主要子公司情况|主要控股参股公司", combined):
        return False
    return True


def _major_subsidiaries_table_substantive(combined: str) -> bool:
    if len(combined) < 80:
        return False
    if not any(v in combined for v in _MAJOR_SUBSIDIARY_VOCAB):
        return False
    if not any(h in combined for h in _MAJOR_SUBSIDIARY_TABLE_HEADERS):
        if not re.search(r"子公司名称|参股公司情况|附属公司", combined):
            return False
    has_table_nums = bool(
        re.search(r"注册资本|持股比例|总资产|净资产|净利润", combined)
        and re.search(r"\d{1,3}(?:,\d{3})+|\d{4,}", combined)
    )
    return has_table_nums or (
        "注册资本" in combined and any(c.isdigit() for c in combined)
    )


def _evaluate_ratio_numeric(
    fk: str,
    labeled: list,
    ctx: str,
    ev: str,
    spec: FieldSpec,
) -> tuple[str, str]:
    """Shared ratio evaluation for found/partial numeric fields (#30b)."""
    reject = FIELD_REJECT_LABELS.get(fk, ())
    best: tuple[str, str] | None = None
    for item in labeled:
        lab = (item.get("label") or "").strip()
        num = (item.get("value") or "").strip()
        if not num or not any(c.isdigit() for c in num):
            continue
        if fk == "npl_ratio" and _npl_label_is_wrong_line_item(lab):
            best = best or ("wrong", f"npl wrong-line-item label '{lab}'")
            continue
        if any(r in lab for r in reject):
            best = best or ("wrong", f"wrong-line-item label '{lab}'")
            continue
        if any(r in lab for r in AMOUNT_NOISE_LABELS):
            continue
        anchor_ok = _anchor_in_text(lab, spec.anchors) or _anchor_in_text(ctx + ev, spec.anchors)
        if not anchor_ok:
            best = best or ("wrong", f"orphan numeric without field anchor (label='{lab}')")
            continue
        if fk == "capital_adequacy_ratio" and _ratio_context_preferred_share_trigger(ctx, ev):
            return "wrong", "preferred-share trigger threshold, not company capital ratio"
        if fk in ("capital_adequacy_ratio", "provision_coverage_ratio"):
            if _ratio_context_industry_narrative(ctx, ev):
                return "wrong", "industry-level banking narrative, not company ratio"
            if not _looks_like_ratio_value(num):
                if re.fullmatch(r"20\d{2}", num):
                    return "wrong", f"capital ratio narrative year token '{num}'"
                best = best or ("wrong", f"ratio field with non-ratio value '{num}'")
                continue
        if not _looks_like_ratio_value(num):
            best = best or ("wrong", f"ratio field with non-ratio value '{num}'")
            continue
        return "usable", f"ratio label '{lab}' value={num}"
    if best:
        return best
    if _anchor_in_text(ctx + ev, spec.anchors) and any(c.isdigit() for c in ctx):
        if fk in ("capital_adequacy_ratio", "provision_coverage_ratio"):
            if _ratio_context_industry_narrative(ctx, ev):
                return "wrong", "industry-level banking narrative, not company ratio"
        return "partial", "context-only numbers without labeled pairs"
    return "wrong", "empty labeled list"


def strict_section_snippet(f: dict, spec: FieldSpec) -> tuple[str, str]:
    fk = f.get("field") or spec.key
    st = f.get("status", "not_found")
    if st == "not_found":
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        v = f.get("value") if isinstance(f.get("value"), str) else ""
        if fk == "major_subsidiaries" and v and len(v) >= 25:
            combined = v + (f.get("evidence_sentence") or "")
            if _major_subsidiaries_wrong_section(combined):
                return "wrong", "subsidiary field hit employee/qualifications section"
            if _major_subsidiaries_structured_only(combined):
                return "wrong", "structured-entity note, not major subsidiaries table"
        if v and len(v) >= 25:
            return "partial", "status=partial with some content"
        return "partial", "status=partial low confidence"
    v = f.get("value")
    if not isinstance(v, str):
        return "wrong", "expected string snippet"
    ev = f.get("evidence_sentence") or ""
    combined = v + ev
    if fk == "main_business_segments" and "insurance business lines" in (spec.definition or "").lower():
        if _insurer_has_sensitivity(v, ev):
            return "wrong", "insurer main-business field hit EV/sensitivity section"
        if _insurer_business_line_snippet(combined) and f.get("in_region"):
            return "usable", f"insurer business-line snippet substantive (len={len(v)})"
    if fk == "major_subsidiaries":
        if _major_subsidiaries_wrong_section(combined):
            return "wrong", "subsidiary field hit employee/qualifications section"
        if _major_subsidiaries_structured_only(combined):
            return "wrong", "structured-entity note, not major subsidiaries table"
        if _is_pointer_only(v) or (_is_pointer_only(ev) and len(v) < 80):
            return "wrong", "pointer-only reference"
        anchor_hit = _anchor_in_text(combined, spec.anchors)
        if _major_subsidiaries_table_substantive(combined) and anchor_hit:
            return (
                "usable",
                f"subsidiary table/snippet substantive (out-of-region ok, len={len(v)})",
            )
    if _is_pointer_only(v) or (_is_pointer_only(ev) and len(v) < 80):
        return "wrong", "pointer-only reference"
    if fk != "major_subsidiaries" and any(b in combined for b in FIN_BOILER_KW):
        return "wrong", "financial/legal boilerplate"
    if any(b in combined for b in LEGAL_DISCLAIMER_KW):
        return "wrong", "legal disclaimer text"
    anchor_hit = _anchor_in_text(combined, spec.anchors)
    in_reg = f.get("in_region")
    if len(v) >= 80 and in_reg and anchor_hit:
        return "usable", f"substantive in-region snippet with anchor (len={len(v)})"
    if len(v) >= 80 and in_reg:
        return "partial", f"substantive in-region but weak anchor match (len={len(v)})"
    if len(v) >= 80 and not in_reg:
        return "partial", f"substantive but out-of-region (len={len(v)})"
    if len(v) >= 25 and anchor_hit:
        return "partial", f"short snippet with anchor (len={len(v)})"
    if len(v) >= 25:
        return "partial", f"short generic snippet (len={len(v)})"
    return "wrong", f"too short (len={len(v)})"


def strict_financial_numeric(
    f: dict,
    spec: FieldSpec,
    pdf_path: str | None,
    profile_fields: dict[str, dict] | None = None,
) -> tuple[str, str]:
    st = f.get("status", "not_found")
    fk = f.get("field") or spec.key
    if st == "not_found":
        if _pdf_not_found_missed_evidence(
            pdf_path, fk, spec, profile_fields=profile_fields,
        ):
            if fk in BROKER_NUMERIC_FIELDS:
                return (
                    "not_found_missed",
                    "PDF broker field-specific numeric evidence found but extractor not_found",
                )
            return "not_found_missed", "PDF anchor+digit found but extractor not_found"
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        if fk in RATIO_FIELDS:
            val = f.get("value")
            if isinstance(val, dict):
                labeled = val.get("labeled") or []
                ctx = val.get("context") or ""
                ev = f.get("evidence_sentence") or ""
                if labeled or ctx:
                    return _evaluate_ratio_numeric(fk, labeled, ctx, ev, spec)
        return "partial", "status=partial"
    val = f.get("value")
    if not isinstance(val, dict):
        return "wrong", "missing numeric value dict"
    labeled = val.get("labeled") or []
    ctx = val.get("context") or ""
    ev = f.get("evidence_sentence") or ""
    if fk in RATIO_FIELDS:
        if _is_insurer_numeric_field(fk, spec):
            insurer = _evaluate_insurer_numeric(fk, labeled, ctx, ev, spec)
            if insurer:
                return insurer
        return _evaluate_ratio_numeric(fk, labeled, ctx, ev, spec)
    if _is_insurer_numeric_field(fk, spec):
        insurer = _evaluate_insurer_numeric(fk, labeled, ctx, ev, spec)
        if insurer:
            return insurer
    if not labeled:
        if _anchor_in_text(ctx + ev, spec.anchors) and any(c.isdigit() for c in ctx):
            return "partial", "context-only numbers without labeled pairs"
        return "wrong", "empty labeled list"
    reject = FIELD_REJECT_LABELS.get(fk, ())
    best: tuple[str, str] | None = None
    for item in labeled:
        lab = (item.get("label") or "").strip()
        num = (item.get("value") or "").strip()
        if not num or not any(c.isdigit() for c in num):
            continue
        if any(r in lab for r in reject):
            best = best or ("wrong", f"wrong-line-item label '{lab}'")
            continue
        if any(r in lab for r in AMOUNT_NOISE_LABELS) and fk not in RATIO_FIELDS:
            continue
        anchor_ok = _anchor_in_text(lab, spec.anchors) or _anchor_in_text(ctx + ev, spec.anchors)
        if not anchor_ok:
            best = best or ("wrong", f"orphan numeric without field anchor (label='{lab}')")
            continue
        if fk == "risk_control_indicators":
            if _looks_like_ratio_value(num) or _looks_like_amount_value(num):
                return "usable", f"risk indicator '{lab}' value={num}"
            best = best or ("partial", f"risk indicator weak value '{num}'")
            continue
        if _looks_like_amount_value(num):
            if _anchor_in_text(lab, spec.anchors):
                return "usable", f"amount label '{lab}' value={num}"
            return "partial", f"amount with indirect anchor (label='{lab}')"
        if _looks_like_ratio_value(num) and fk not in RATIO_FIELDS:
            best = best or ("wrong", f"amount field with ratio-only value '{num}'")
            continue
        best = best or ("partial", f"numeric present but weak semantics (label='{lab}')")
    if best:
        return best
    return "wrong", "no substantive labeled numeric"


def _table_text_blob(val: dict) -> str:
    rows = val.get("rows") or []
    return " ".join(" ".join(str(c) for c in row) for row in rows)


def _financial_table_plausible(
    fk: str,
    val: dict,
    *,
    evidence: str = "",
) -> tuple[bool, str]:
    if not isinstance(val, dict):
        return False, "missing table dict"
    rows = val.get("rows") or []
    if not rows:
        return False, "empty rows"
    if val.get("match_hits", 0) < 1 and fk not in ("regional_distribution",):
        return False, "match_hits<1"
    blob = _table_text_blob(val)
    combined = blob + " " + (evidence or "")

    if fk == "loan_structure":
        if any(k in combined for k in _LOAN_TABLE_REJECT):
            return False, "loan table looks like interest income or asset composition"
        if not any(k in combined for k in ("贷款", "垫款", "票据")):
            return False, "missing loan vocabulary"
        if "发放贷款和垫款" in combined and not any(k in combined for k in _LOAN_TABLE_REQUIRE):
            return False, "loan table is total-only without structure breakdown"
        if not any(k in combined for k in _LOAN_TABLE_REQUIRE):
            if "发放贷款和垫款" in combined and any(
                k in combined for k in ("金融投资", "存放中央银行", "拆出资金")
            ):
                return False, "loan table mixed with non-loan balance-sheet lines"
            if len([r for r in rows if _table_row_is_data_row(r)]) <= 1:
                return False, "loan table lacks breakdown categories"

    elif fk == "deposit_structure":
        if any(k in combined for k in _DEPOSIT_TABLE_REJECT):
            return False, "deposit table looks like liability/cash-flow summary"
        if not any(k in combined for k in ("存款", "吸收存款")):
            return False, "missing deposit vocabulary"
        if "长期股权投资" in combined or "应付职工薪酬" in combined:
            return False, "deposit table looks like liability summary"
        if "吸收存款" in combined and not any(
            k in combined for k in ("公司存款", "个人存款", "活期存款", "定期存款", "保证金存款")
        ):
            if len([r for r in rows if _table_row_is_data_row(r)]) <= 1:
                return False, "deposit table is total-only without deposit breakdown"

    elif fk in ("regional_distribution", "revenue_by_region"):
        if any(k in combined for k in _REGIONAL_TABLE_REJECT):
            return False, "regional table looks like branch roster or holdings"
        if not any(k in combined for k in ("地区", "境内", "境外", "区域", "长三角", "环渤海")):
            return False, "missing region vocabulary"
        if any(k in combined for k in ("分行", "支行", "营业部", "地址", "邮编")):
            return False, "regional table looks like branch roster"

    elif fk == "revenue_by_segment":
        if any(k in combined for k in _REVENUE_TABLE_REJECT):
            return False, "segment table looks like cash-flow/cost/income-statement page"
        segment_markers = ("分部", "主营业务分", "分行业", "分产品", "分地区情况")
        if "利息净收入" in combined and "利息支出" in combined:
            if not any(k in combined for k in segment_markers):
                return False, "mother-company income statement, not segment table"
        if not any(k in combined for k in _REVENUE_TABLE_REQUIRE):
            return False, "missing segment revenue vocabulary"
        cost_heavy = sum(
            1 for r in rows
            if _table_row_is_data_row(r)
            and any(k in " ".join(str(c) for c in r) for k in ("业务及管理费", "减值损失", "其他业务成本"))
        )
        rev_rows = sum(
            1 for r in rows
            if _table_row_is_data_row(r)
            and any(k in " ".join(str(c) for c in r) for k in ("收入", "营业收入", "手续费"))
        )
        if cost_heavy >= 2 and rev_rows == 0:
            return False, "segment table is business-cost allocation, not revenue"
        if rev_rows == 0 and any(
            k in combined for k in ("业务及管理费", "税金及附加", "减值损失", "营业总支出")
        ):
            return False, "segment table is cost-only without revenue rows"

    data_rows = [r for r in rows if _table_row_is_data_row(r)]
    if len(data_rows) >= 2:
        return True, f"{len(data_rows)} data rows"
    if len(data_rows) == 1:
        return True, "single data row"
    return False, "no data rows in preview"


def _revenue_table_plausible_strict(val: dict | None, evidence: str = "") -> tuple[bool, str]:
    if not revenue_table_plausible(val):
        return False, "fails revenue_table_plausible"
    ok, detail = _financial_table_plausible(
        "revenue_by_segment", val if isinstance(val, dict) else {}, evidence=evidence,
    )
    if not ok:
        return False, detail
    return True, "revenue_table_plausible"


def strict_financial_table(f: dict, spec: FieldSpec, pdf_path: str | None) -> tuple[str, str]:
    st = f.get("status", "not_found")
    fk = f.get("field") or spec.key
    ev = f.get("evidence_sentence") or ""
    insurer_segment = (
        fk == "revenue_by_segment"
        and "insurance segment" in (spec.definition or "").lower()
    )
    if st == "not_found":
        if _pdf_anchor_with_number(pdf_path, spec.anchors):
            return "not_found_missed", "PDF table anchor found but extractor not_found"
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        if insurer_segment:
            val = f.get("value")
            if isinstance(val, dict) and val.get("snippet"):
                snippet = str(val.get("snippet") or "")
                if _insurer_has_sensitivity(snippet, ev):
                    return "wrong", "insurer segment field hit EV/sensitivity page"
                if _insurer_business_line_snippet(snippet + " " + ev):
                    return "partial", "insurer line-of-business snippet"
        if fk in ("loan_structure", "deposit_structure", "regional_distribution",
                  "revenue_by_segment", "revenue_by_region"):
            val = f.get("value")
            if isinstance(val, dict) and (val.get("rows") or val.get("snippet")):
                ok, detail = _financial_table_plausible(
                    fk if fk != "revenue_by_region" else "regional_distribution",
                    val,
                    evidence=ev or str(val.get("snippet") or ""),
                )
                if not ok:
                    return "wrong", detail
        return "partial", "status=partial"
    val = f.get("value")
    if insurer_segment and isinstance(val, dict) and val.get("snippet"):
        snippet = str(val.get("snippet") or "")
        if _insurer_has_sensitivity(snippet, ev):
            return "wrong", "insurer segment field hit EV/sensitivity page"
        if _insurer_business_line_snippet(snippet + " " + ev):
            return "partial", "insurer line-of-business snippet"
    if fk in ("revenue_by_region", "revenue_by_segment"):
        ok, detail = _revenue_table_plausible_strict(val, evidence=ev)
    else:
        ok, detail = _financial_table_plausible(
            fk, val if isinstance(val, dict) else {}, evidence=ev,
        )
    if not ok:
        return "wrong", detail
    rows = (val or {}).get("rows") or []
    data_rows = [r for r in rows if _table_row_is_data_row(r)]
    if len(data_rows) >= 2:
        return "usable", detail
    if len(data_rows) == 1:
        return "partial", f"single data row ({detail})"
    return "wrong", detail


def strict_concentration(f: dict, spec: FieldSpec, pdf_path: str | None) -> tuple[str, str]:
    st = f.get("status", "not_found")
    if st == "not_found":
        if _pdf_anchor_with_number(pdf_path, spec.anchors):
            return "not_found_missed", "PDF concentration anchor found but extractor not_found"
        return "not_found_unverified", "status=not_found (unverified by automation)"
    if st == "partial":
        return "partial", "status=partial"
    val = f.get("value")
    if not isinstance(val, dict):
        return "wrong", "missing concentration dict"
    ev = f.get("evidence_sentence") or val.get("sentence") or ""
    has_val = bool(val.get("ratio") or val.get("amount"))
    if not has_val:
        return "wrong", "empty ratio/amount"
    if _anchor_in_text(ev, spec.anchors):
        return "usable", "concentration with anchor in evidence"
    return "partial", "ratio/amount without clear anchor keyword"


def strict_audit_field(
    f: dict,
    spec: FieldSpec,
    pdf_path: str | None,
    profile_fields: dict[str, dict] | None = None,
) -> tuple[str, str]:
    ex = f.get("extraction") or spec.extraction
    if ex == "section_snippet":
        return strict_section_snippet(f, spec)
    if ex == "numeric":
        return strict_financial_numeric(f, spec, pdf_path, profile_fields=profile_fields)
    if ex == "table":
        return strict_financial_table(f, spec, pdf_path)
    if ex == "concentration":
        return strict_concentration(f, spec, pdf_path)
    return "wrong", f"unknown extraction type {ex}"


def _strict_cell_score(label: str, lenient: bool = False) -> float:
    if label == "usable":
        return 1.0
    if label == "partial":
        return 1.0 if lenient else 0.5
    return 0.0


def write_population_csv(path: str, rows: list[FinAuditRow]) -> None:
    fields = [
        "code", "name", "board", "schema_profile", "field", "extraction_type",
        "status", "proxy_plausible", "strict_label", "reason", "value_preview",
        "evidence_sentence", "page", "source_url", "subtype_caveat_flag",
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "code": r.code,
                "name": r.name,
                "board": r.board,
                "schema_profile": r.schema_profile,
                "field": r.field,
                "extraction_type": r.extraction_type,
                "status": r.status,
                "proxy_plausible": r.proxy_plausible,
                "strict_label": r.strict_label,
                "reason": r.reason,
                "value_preview": r.value_preview,
                "evidence_sentence": r.evidence_sentence,
                "page": r.page,
                "source_url": r.source_url,
                "subtype_caveat_flag": r.subtype_caveat_flag,
            })


def write_summary(
    path: str,
    rows: list[FinAuditRow],
    eval_fin_ok: list[dict],
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    by_sub: dict[str, list[FinAuditRow]] = defaultdict(list)
    for r in rows:
        by_sub[r.schema_profile].append(r)

    lines: list[str] = []
    a = lines.append
    a("# full_market_2024 Financial Strict Audit Summary")
    a("")
    a(f"_Generated: {ts} | automated financial-only audit (Phase 1A)_")
    a("")
    a("## 1. Population breakdown")
    a("")
    a("| scope | companies | field-cells |")
    a("|---|---:|---:|")
    n_co = len({r.code for r in rows})
    a(f"| ok financial (audited) | {n_co} | {len(rows)} |")
    for sub in ("bank", "broker", "insurer", "other_financial"):
        sub_rows = by_sub.get(sub, [])
        if not sub_rows:
            continue
        n = len({r.code for r in sub_rows})
        a(f"| `{sub}` | {n} | {len(sub_rows)} |")
    not_ok = [r for r in eval_fin_ok if r.get("status") != "ok"]
    if not_ok:
        a("")
        a(f"Excluded from audit: {len(not_ok)} financial company(ies) not ok "
          f"({', '.join(r['stock_code'] for r in not_ok)}).")
    a("")
    a("## 2. Strict usable / lenient by subtype")
    a("")
    a("| subtype | fields/co | strict usable | strict lenient | proxy plausible |")
    a("|---|---:|---:|---:|---:|")
    for sub in ("bank", "broker", "insurer", "other_financial"):
        sub_rows = by_sub.get(sub, [])
        if not sub_rows:
            continue
        n = len({r.code for r in sub_rows})
        ft = len(sub_rows) / n if n else 0
        strict_u = statistics.mean(_strict_cell_score(r.strict_label) for r in sub_rows)
        strict_l = statistics.mean(_strict_cell_score(r.strict_label, lenient=True) for r in sub_rows)
        proxy = statistics.mean(1.0 if r.proxy_plausible else 0.0 for r in sub_rows)
        a(f"| `{sub}` | {ft:.1f} | **{strict_u * ft:.2f} / {ft:.0f}** | "
          f"{strict_l * ft:.2f} / {ft:.0f} | {proxy * ft:.2f} / {ft:.0f} |")
    a("")
    a("## 3. Proxy vs strict gap by subtype")
    a("")
    a("| subtype | proxy cell-rate | strict usable cell-rate | gap |")
    a("|---|---:|---:|---:|")
    for sub in ("bank", "broker", "insurer", "other_financial"):
        sub_rows = by_sub.get(sub, [])
        if not sub_rows:
            continue
        proxy = statistics.mean(1.0 if r.proxy_plausible else 0.0 for r in sub_rows)
        strict_u = statistics.mean(_strict_cell_score(r.strict_label) for r in sub_rows)
        a(f"| `{sub}` | {proxy:.1%} | {strict_u:.1%} | **{proxy - strict_u:.1%}** |")
    a("")
    a("## 4. Top weak fields by subtype")
    a("")
    for sub in ("bank", "broker", "insurer", "other_financial"):
        sub_rows = by_sub.get(sub, [])
        if not sub_rows:
            continue
        by_field: dict[str, Counter] = defaultdict(Counter)
        for r in sub_rows:
            by_field[r.field][r.strict_label] += 1
        weak = []
        for fk, cnt in by_field.items():
            n = sum(cnt.values())
            bad = cnt.get("wrong", 0) + cnt.get("partial", 0)
            weak.append((bad / n, fk, cnt))
        weak.sort(reverse=True)
        a(f"### {sub}")
        a("")
        a("| field | usable | partial | wrong | not_found* |")
        a("|---|---:|---:|---:|---:|")
        for rate, fk, cnt in weak[:8]:
            nf = cnt.get("not_found_unverified", 0) + cnt.get("not_found_missed", 0)
            a(f"| `{fk}` | {cnt.get('usable', 0)} | {cnt.get('partial', 0)} | "
              f"{cnt.get('wrong', 0)} | {nf} |")
        a("")
    a("*not_found = not_found_unverified + not_found_missed")
    a("")
    a("## 5. Top suspicious companies")
    a("")
    by_co: dict[str, list[FinAuditRow]] = defaultdict(list)
    for r in rows:
        by_co[r.code].append(r)
    co_scores = []
    for code, crows in by_co.items():
        strict_u = statistics.mean(_strict_cell_score(r.strict_label) for r in crows)
        proxy = statistics.mean(1.0 if r.proxy_plausible else 0.0 for r in crows)
        co_scores.append((strict_u, proxy, code, crows[0].name, crows[0].schema_profile, crows))
    co_scores.sort(key=lambda x: (x[0], x[1]))
    a("| code | name | subtype | strict usable / fields | proxy / fields | caveat |")
    a("|---|---|---|---:|---:|---|")
    for strict_u, proxy, code, name, sub, crows in co_scores[:12]:
        ft = len(crows)
        caveat = "yes" if code in SUBTYPE_CAVEAT_CODES else ""
        a(f"| {code} | {name} | {sub} | {strict_u * ft:.1f}/{ft} | "
          f"{proxy * ft:.1f}/{ft} | {caveat} |")
    a("")
    a("## 6. Subtype caveat companies (stored schema; manual review in Phase 1B)")
    a("")
    a("| code | name | stored schema | note |")
    a("|---|---|---|---|")
    a("| 000402 | 金融街 | broker | Likely real-estate / REIT / developer; not a securities broker |")
    a("| 600816 | 建元信托 | bank | Trust company; likely should be other_financial |")
    a("| 600318 | 新力金融 | bank | Financial holding; subtype unclear |")
    a("")
    a("Automated audit uses **stored** `schema_profile`; caveat flags are informational only.")
    a("")
    a("## 7. Financial audit caveats")
    a("")
    a("- **Not full manual validation** — automated adversarial recheck over stored values.")
    a("- **Not mixed into non-financial headline** — industrial strict usable remains **9.43/11** "
      "(5621 companies); this report is financial-only.")
    a("- **Numeric/table noise likely** — financial fields use generic extractors; strict rules "
      "flag wrong-line-item and orphan numerics but cannot eliminate all false positives.")
    a("- **Phase 1B** — stratified manual PDF calibration worksheet is the next step.")
    a("- **`not_found_missed`** — only assigned when PDF anchor search finds anchor+digit; "
      "conservative to avoid overclaiming.")
    a("")
    a("## 8. Phase 1B manual calibration recommendation")
    a("")
    a("Proceed with worksheet generation. Suggested 30-company sample:")
    a("")
    a("- **Force-include:** 601963, 601375, 601377, 601878, 000402, 600816, 600318")
    a("- **bank (12):** 601398, 601939, 601988, 601328, 601825, 002807, 001227, 601997, "
      "601963, 600318, 601166, 600816")
    a("- **broker (12):** 601901, 002500, 600999, 000776, 601375, 601377, 601878, 600958, "
      "601162, 600030, 002736, 601108")
    a("- **insurer (2):** 601336, 601628 (both)")
    a("- **other_financial (4):** 600927, 001236, 002961, 603093 (all)")
    a("")
    a("Review numeric fields (`net_interest_income`, `npl_ratio`, broker income lines) and "
      "table fields first; treat 000402 as tag review, not broker control.")
    a("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def run_audit(out_dir: str, yaml_path: str) -> tuple[list[FinAuditRow], list[dict]]:
    meta = _load_meta(yaml_path)
    with open(os.path.join(out_dir, "eval_results.json"), encoding="utf-8") as fh:
        eval_rows = json.load(fh)

    fin_eval = [r for r in eval_rows if r.get("financial")]
    fin_ok = [r for r in fin_eval if r.get("status") == "ok"]

    audit_rows: list[FinAuditRow] = []
    spec_cache: dict[str, dict[str, FieldSpec]] = {}

    for er in fin_ok:
        code = str(er["stock_code"])
        yc = meta.get(code, {})
        board = yc.get("board") or er.get("board", "")
        name = er.get("short_name") or yc.get("short_name", "")
        schema = er.get("schema_profile") or "unknown"
        pp = _profile_path(out_dir, code, board)
        if not pp:
            continue
        profile = json.load(open(pp, encoding="utf-8"))
        schema = profile.get("schema_profile") or schema
        source_url = (profile.get("source") or {}).get("source_url") or er.get("source_url", "")
        pdf_path = _pdf_path(out_dir, code, board)
        fmap = _field_map(profile)

        if schema not in spec_cache:
            spec_cache[schema] = {s.key: s for s in get_field_specs(schema)}
        specs = spec_cache[schema]

        caveat = code in SUBTYPE_CAVEAT_CODES
        eval_fields = er.get("fields") or {}

        for fk, spec in specs.items():
            f = fmap.get(fk)
            if not f:
                f = {
                    "field": fk,
                    "status": "not_found",
                    "extraction": spec.extraction,
                    "value": None,
                }
            proxy = bool((eval_fields.get(fk) or {}).get("plausible"))
            if not eval_fields and f.get("status") == "found":
                proxy = field_plausible(f)
            label, reason = strict_audit_field(f, spec, pdf_path, profile_fields=fmap)
            audit_rows.append(
                FinAuditRow(
                    code=code,
                    name=name,
                    board=board,
                    schema_profile=schema,
                    field=fk,
                    extraction_type=f.get("extraction") or spec.extraction,
                    status=f.get("status", "not_found"),
                    proxy_plausible=proxy,
                    strict_label=label,
                    reason=reason,
                    value_preview=value_preview(f),
                    evidence_sentence=(f.get("evidence_sentence") or "")[:200],
                    page=str(f.get("page") or ""),
                    source_url=source_url,
                    subtype_caveat_flag=caveat,
                )
            )
    return audit_rows, fin_eval


def main() -> int:
    ap = argparse.ArgumentParser(description="Financial-only strict audit (read-only)")
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--companies-yaml", default=DEFAULT_YAML)
    args = ap.parse_args()

    rows, fin_eval = run_audit(args.out_dir, args.companies_yaml)
    pop_csv = os.path.join(args.out_dir, "financial_audit_population.csv")
    summary_md = os.path.join(args.out_dir, "financial_audit_summary.md")
    write_population_csv(pop_csv, rows)
    write_summary(summary_md, rows, fin_eval)

    print(f"[financial_audit] population rows: {len(rows)}")
    print(f"[financial_audit] wrote {pop_csv}")
    print(f"[financial_audit] wrote {summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
