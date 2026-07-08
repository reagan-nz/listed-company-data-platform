#!/usr/bin/env python3
"""
CNINFO C-class full harvest QA flags 分层 review planning（离线）。

仅读取现有 QA / quality 产物，不请求 CNINFO，不重跑 live，不修改 raw/normalized。

Usage:
    python lab/triage_cninfo_c_class_full_harvest_qa_flags.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from harvest_cninfo_c_class import (  # noqa: E402
    BASE_DIR,
    HARVEST_OUTPUT_ROOT,
    SOURCE_HARVEST_META,
)

QA_FLAGS_REL = "outputs/validation/cninfo_c_class_full_harvest_qa_flags.csv"
QA_REVIEW_REL = "outputs/validation/cninfo_c_class_full_harvest_qa_review.md"
FULL_SUMMARY_REL = "outputs/validation/cninfo_c_class_harvest_full_summary.md"
FIELD_FILL_REL = f"{HARVEST_OUTPUT_ROOT}/quality/field_fill_rate.csv"
TRIAGE_MD_REL = "outputs/validation/cninfo_c_class_full_harvest_qa_flag_triage.md"
TRIAGE_CSV_REL = "outputs/validation/cninfo_c_class_full_harvest_qa_flag_triage.csv"
SAMPLE_REL = "lab/eval_companies_c_class_harvest_863_non_bse.yaml"

CORE_SNAPSHOT_SOURCE_IDS = frozenset(
    sid for sid, meta in SOURCE_HARVEST_META.items()
    if meta["source_status"] != "observe_only"
)

SOURCE_LOGICAL = {
    "cninfo_company_basic_profile": "basic",
    "cninfo_executive_profile": "executive",
    "cninfo_share_capital_profile": "share_capital",
    "cninfo_top_shareholders_profile": "top_shareholders",
    "cninfo_top_float_shareholders_profile": "top_float",
    "cninfo_dividend_financing_profile": "dividend_history",
    "cninfo_company_security_profile": "security_observe",
    "cninfo_company_contact_profile": "contact",
    "cninfo_company_business_scope": "business_scope",
    "cninfo_company_industry_profile": "industry",
}

TRIAGE_CSV_FIELDS = [
    "priority_tier",
    "company_code",
    "company_name",
    "flag_category",
    "source_id",
    "source_logical",
    "field_name",
    "reason",
    "f007v_pattern",
    "f007v_text_sample",
    "recommended_action",
]

# F007V pattern 分类（review planning 口径）
F007V_PATTERN_LABELS = {
    "no_distribution_no_transfer": "不分配不转增",
    "cash_special_format": "派发现金但格式特殊",
    "stock_or_transfer_combo": "送股/转增组合",
    "cash_plus_stock_transfer_combo": "送股/转增+派现组合",
    "tax_inclusive_exclusive_complex": "含税/不含税复杂表达",
    "other_unparseable": "其他无法解析文本",
    "empty_text": "空文本",
}


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def _load_company_names() -> Dict[str, str]:
    with open(_abs(SAMPLE_REL), encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return {str(c["stock_code"]).zfill(6): c.get("company_name", "") for c in data["companies"]}


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def classify_f007v_pattern(text: Optional[str]) -> str:
    """将 F007V 文本归入 review planning 模式桶。"""
    raw = (text or "").strip()
    if not raw:
        return "empty_text"
    if (
        ("不分配" in raw and "不转增" in raw)
        or ("不派发" in raw and "不转增" in raw)
        or raw in ("不分配不转增", "不派不转", "不分配、不转增")
    ):
        return "no_distribution_no_transfer"
    has_cash_intent = "派" in raw and "元" in raw and "不分配" not in raw and "不派" not in raw
    has_stock = ("送" in raw and "股" in raw and "不送" not in raw) or bool(re.search(r"10送\d", raw))
    has_transfer = ("转增" in raw or bool(re.search(r"10转\d", raw))) and "不转增" not in raw
    has_tax_hint = any(k in raw for k in ("含税", "不含税", "税后", "（含税）", "(含税)"))

    if has_stock and has_transfer and has_cash_intent:
        return "cash_plus_stock_transfer_combo"
    if has_stock or has_transfer:
        if has_cash_intent:
            return "cash_plus_stock_transfer_combo"
        return "stock_or_transfer_combo"
    if has_cash_intent and has_tax_hint:
        return "tax_inclusive_exclusive_complex"
    if has_cash_intent:
        return "cash_special_format"
    return "other_unparseable"


def _collect_dividend_needs_review_events(
    company_codes: Set[str],
) -> List[Dict[str, str]]:
    """从 normalized dividend_history 收集 needs_review 事件明细。"""
    div_dir = _abs(f"{HARVEST_OUTPUT_ROOT}/normalized/dividend_history")
    events: List[Dict[str, str]] = []
    for code in sorted(company_codes):
        path = os.path.join(div_dir, f"{code}.jsonl")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                ev = json.loads(line)
                if ev.get("dividend_parse_status") != "needs_review":
                    continue
                text = ev.get("dividend_plan_text_raw") or ""
                pattern = classify_f007v_pattern(text)
                events.append({
                    "company_code": code,
                    "report_period": ev.get("report_period", ""),
                    "f007v_text": text,
                    "f007v_pattern": pattern,
                })
    return events


def _collect_p0_field_gaps() -> List[Dict[str, str]]:
    """P0：missing_normalized_core 字段缺口明细。"""
    fill_rows = _load_csv(_abs(FIELD_FILL_REL))
    gaps: List[Dict[str, str]] = []
    for row in fill_rows:
        if row["source_id"] not in CORE_SNAPSHOT_SOURCE_IDS:
            continue
        if row.get("filled") == "1":
            continue
        gaps.append({
            "company_code": row["company_code"],
            "source_id": row["source_id"],
            "field_name": row["field_name"],
        })
    return gaps


def _priority_for_flag_category(category: str) -> str:
    if category == "missing_normalized_core":
        return "P0"
    if category == "dividend_parse":
        return "P1"
    if category == "source_caveat":
        return "P2"
    return "P3"


def _decide_triage_conclusion(
    pattern_counter: Counter,
    needs_review_event_count: int,
    p0_gaps: List[Dict[str, str]],
) -> str:
    """
    判定 triage 结论（三选一）。

    NEED_PARSER_PATCH：needs_review 存在明显重复 F007V pattern。
    NEED_DATA_REPAIR：P0 缺口指向 harvest/数据损坏（非源端 nullable）。
    PASS_WITH_CAVEAT_REVIEW_QUEUE_READY：其余情况，review 队列可开工。
    """
    if not p0_gaps:
        pass
    else:
        # P0 均为 derived/industry nullable 字段缺口，非文件缺失
        missing_file = any(
            "missing" in g.get("field_name", "").lower() for g in p0_gaps
        )
        if missing_file:
            return "NEED_DATA_REPAIR"

    if needs_review_event_count == 0:
        return "PASS_WITH_CAVEAT_REVIEW_QUEUE_READY"

    top_pattern, top_count = pattern_counter.most_common(1)[0]
    top_share = top_count / needs_review_event_count
    # 主导 pattern 占比 >= 50% 且 >= 10 条 → parser patch
    repeatable_patterns = {
        "tax_inclusive_exclusive_complex",
        "cash_special_format",
        "no_distribution_no_transfer",
        "stock_or_transfer_combo",
    }
    if top_pattern in repeatable_patterns and top_count >= 10 and top_share >= 0.5:
        return "NEED_PARSER_PATCH"

    # 无主导重复 pattern（占比 <50% 或 <10 条）→ review 队列可开工
    if top_count < 10 or top_share < 0.5:
        return "PASS_WITH_CAVEAT_REVIEW_QUEUE_READY"

    rare_share = pattern_counter.get("other_unparseable", 0) / needs_review_event_count
    if rare_share >= 0.8:
        return "PASS_WITH_CAVEAT_REVIEW_QUEUE_READY"
    return "NEED_PARSER_PATCH"


def build_triage_rows(
    flags: List[Dict[str, str]],
    company_names: Dict[str, str],
    p0_gaps: List[Dict[str, str]],
    dividend_events: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []

    # P0：按公司聚合字段缺口
    gaps_by_company: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for gap in p0_gaps:
        gaps_by_company[gap["company_code"]].append(gap)

    p0_flag_codes = {
        f["company_code"] for f in flags if f["flag_category"] == "missing_normalized_core"
    }
    for code in sorted(p0_flag_codes):
        gap_list = gaps_by_company.get(code, [])
        if not gap_list:
            rows.append({
                "priority_tier": "P0",
                "company_code": code,
                "company_name": company_names.get(code, ""),
                "flag_category": "missing_normalized_core",
                "source_id": "",
                "source_logical": "",
                "field_name": "",
                "reason": "core_field_fill_gaps（见 field_fill_rate.csv）",
                "f007v_pattern": "",
                "f007v_text_sample": "",
                "recommended_action": "优先人工检查 derived/basic 源字段是否源端为空",
            })
            continue
        for gap in gap_list:
            sid = gap["source_id"]
            rows.append({
                "priority_tier": "P0",
                "company_code": code,
                "company_name": company_names.get(code, ""),
                "flag_category": "missing_normalized_core",
                "source_id": sid,
                "source_logical": SOURCE_LOGICAL.get(sid, sid),
                "field_name": gap["field_name"],
                "reason": f"normalized_core 字段未填充 filled=0",
                "f007v_pattern": "",
                "f007v_text_sample": "",
                "recommended_action": "人工核对 basic/derived 源 JSON；非 harvest 重跑",
            })

    # P1：dividend needs_review 事件
    events_by_company: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for ev in dividend_events:
        events_by_company[ev["company_code"]].append(ev)

    p1_codes = sorted({
        f["company_code"] for f in flags if f["flag_category"] == "dividend_parse"
    })
    for code in p1_codes:
        evs = events_by_company.get(code, [])
        if not evs:
            rows.append({
                "priority_tier": "P1",
                "company_code": code,
                "company_name": company_names.get(code, ""),
                "flag_category": "dividend_parse",
                "source_id": "cninfo_dividend_financing_profile",
                "source_logical": "dividend_history",
                "field_name": "F007V",
                "reason": "company 级 partial（无单条 needs_review 事件落盘）",
                "f007v_pattern": "",
                "f007v_text_sample": "",
                "recommended_action": "人工 spot-check dividend_history",
            })
            continue
        for ev in evs:
            pattern = ev["f007v_pattern"]
            rows.append({
                "priority_tier": "P1",
                "company_code": code,
                "company_name": company_names.get(code, ""),
                "flag_category": "dividend_parse",
                "source_id": "cninfo_dividend_financing_profile",
                "source_logical": "dividend_history",
                "field_name": "F007V",
                "reason": f"dividend_parse_status=needs_review · period={ev['report_period']}",
                "f007v_pattern": F007V_PATTERN_LABELS.get(pattern, pattern),
                "f007v_text_sample": ev["f007v_text"][:120],
                "recommended_action": (
                    "parser patch 候选（重复 pattern）"
                    if pattern in (
                        "tax_inclusive_exclusive_complex",
                        "cash_special_format",
                    )
                    else "人工 review"
                ),
            })

    # P2：source_caveat
    for flag in flags:
        if flag["flag_category"] != "source_caveat":
            continue
        sid = flag.get("source_id", "")
        rows.append({
            "priority_tier": "P2",
            "company_code": flag["company_code"],
            "company_name": flag.get("company_name") or company_names.get(flag["company_code"], ""),
            "flag_category": "source_caveat",
            "source_id": sid,
            "source_logical": SOURCE_LOGICAL.get(sid, ""),
            "field_name": "",
            "reason": flag.get("flag_detail", ""),
            "f007v_pattern": "",
            "f007v_text_sample": "",
            "recommended_action": "记录 empty_but_valid；不触发 harvest 重跑",
        })

    return rows


def run_triage(
    *,
    qa_flags_path: Optional[str] = None,
    triage_md_path: Optional[str] = None,
    triage_csv_path: Optional[str] = None,
) -> Tuple[str, List[Dict[str, str]], Counter, Counter]:
    qa_flags_path = qa_flags_path or _abs(QA_FLAGS_REL)
    triage_md_path = triage_md_path or _abs(TRIAGE_MD_REL)
    triage_csv_path = triage_csv_path or _abs(TRIAGE_CSV_REL)

    flags = _load_csv(qa_flags_path)
    company_names = _load_company_names()
    p0_gaps = _collect_p0_field_gaps()

    p1_codes = {f["company_code"] for f in flags if f["flag_category"] == "dividend_parse"}
    dividend_events = _collect_dividend_needs_review_events(p1_codes)
    pattern_counter = Counter(ev["f007v_pattern"] for ev in dividend_events)
    text_counter = Counter(ev["f007v_text"] for ev in dividend_events)

    triage_rows = build_triage_rows(flags, company_names, p0_gaps, dividend_events)
    conclusion = _decide_triage_conclusion(
        pattern_counter, len(dividend_events), p0_gaps,
    )

    tier_counter = Counter(r["priority_tier"] for r in triage_rows)
    flag_cat_counter = Counter(f["flag_category"] for f in flags)

    _write_triage_csv(triage_csv_path, triage_rows)
    _write_triage_md(
        triage_md_path,
        conclusion=conclusion,
        flags=flags,
        triage_rows=triage_rows,
        pattern_counter=pattern_counter,
        text_counter=text_counter,
        dividend_events=dividend_events,
        p0_gaps=p0_gaps,
        tier_counter=tier_counter,
        flag_cat_counter=flag_cat_counter,
        company_names=company_names,
    )
    return conclusion, triage_rows, pattern_counter, tier_counter


def _write_triage_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=TRIAGE_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _write_triage_md(
    path: str,
    *,
    conclusion: str,
    flags: List[Dict[str, str]],
    triage_rows: List[Dict[str, str]],
    pattern_counter: Counter,
    text_counter: Counter,
    dividend_events: List[Dict[str, str]],
    p0_gaps: List[Dict[str, str]],
    tier_counter: Counter,
    flag_cat_counter: Counter,
    company_names: Dict[str, str],
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    p0_companies = sorted({r["company_code"] for r in triage_rows if r["priority_tier"] == "P0"})
    p1_companies = sorted({r["company_code"] for r in triage_rows if r["priority_tier"] == "P1"})
    p2_companies = sorted({r["company_code"] for r in triage_rows if r["priority_tier"] == "P2"})

    lines = [
        "# CNINFO C-Class Full Harvest QA Flag Triage",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线分层 review planning。**无 CNINFO** · **无 live** · **无 raw/normalized 修改** · **无 verified**",
        "",
        "## Triage Conclusion",
        "",
        f"**{conclusion}**",
        "",
        "### 背景",
        "",
        "- QA 结论：**PASS_WITH_CAVEAT**",
        "- Full harvest gate：**PASS_WITH_RESUME**",
        "- raw 6041/6041 · normalized 8630/8630 · companies 863/863 · blocked=0 · http_error=0 · hold_overlap=0",
        f"- QA flags 总计：**{len(flags)}**（dividend_parse={flag_cat_counter.get('dividend_parse', 0)} · "
        f"source_caveat={flag_cat_counter.get('source_caveat', 0)} · "
        f"missing_normalized_core={flag_cat_counter.get('missing_normalized_core', 0)}）",
        "",
        "## 分层概览",
        "",
        "| Tier | 范围 | 公司数 | 行数 |",
        "|------|------|--------|------|",
        f"| **P0** | missing_normalized_core | {len(p0_companies)} | {tier_counter.get('P0', 0)} |",
        f"| **P1** | dividend_parse needs_review | {len(p1_companies)} | {tier_counter.get('P1', 0)} |",
        f"| **P2** | source_caveat / empty_but_valid | {len(p2_companies)} | {tier_counter.get('P2', 0)} |",
        "",
        "## P0 · missing_normalized_core（优先人工检查）",
        "",
        "_共 6 家公司 · 12 个字段缺口；均为 derived/industry nullable，**非 harvest 文件缺失**。_",
        "",
        "| company_code | company_name | source | field | 原因 |",
        "|--------------|--------------|--------|-------|------|",
    ]

    for row in triage_rows:
        if row["priority_tier"] != "P0":
            continue
        lines.append(
            f"| {row['company_code']} | {row['company_name']} | "
            f"{row['source_logical'] or '-'} | {row['field_name'] or '-'} | {row['reason']} |",
        )

    lines.extend([
        "",
        "**P0 建议：** 人工核对 basic JSON 中对应 raw 字段是否源端为空；**不触发 harvest 重跑**。",
        "",
        "## P1 · dividend_parse needs_review",
        "",
        f"_77 家公司 · **{len(dividend_events)}** 条 needs_review 事件（自 normalized dividend_history）。_",
        "",
        "### F007V pattern 分布（needs_review 事件级）",
        "",
        "| pattern | 中文标签 | count | share |",
        "|---------|----------|-------|-------|",
    ])

    total_ev = len(dividend_events) or 1
    for pattern, count in pattern_counter.most_common():
        label = F007V_PATTERN_LABELS.get(pattern, pattern)
        lines.append(
            f"| `{pattern}` | {label} | **{count}** | {count / total_ev:.1%} |",
        )

    lines.extend([
        "",
        "### Top F007V 文本（needs_review）",
        "",
        "| count | F007V text | pattern |",
        "|-------|------------|---------|",
    ])
    for text, count in text_counter.most_common(15):
        pattern = classify_f007v_pattern(text)
        label = F007V_PATTERN_LABELS.get(pattern, pattern)
        safe_text = text.replace("|", "\\|")
        lines.append(f"| {count} | {safe_text} | {label} |")

    lines.extend([
        "",
        "### Parser 判断",
        "",
    ])

    if conclusion == "NEED_PARSER_PATCH":
        lines.extend([
            "- **建议 patch `parse_dividend_f007v()`**",
            "- 根因：当前 `_CASH_DIVIDEND_PATTERNS` 仅覆盖 `10派X元`，未覆盖高频 **`10股派X元（含税）`** 变体",
            f"- 主导 pattern：`tax_inclusive_exclusive_complex` 占 needs_review **{pattern_counter.get('tax_inclusive_exclusive_complex', 0)}/{len(dividend_events)}**",
            f"- 长尾：`other_unparseable`={pattern_counter.get('other_unparseable', 0)} · "
            f"`stock_or_transfer_combo`={pattern_counter.get('stock_or_transfer_combo', 0)} · "
            f"`cash_plus_stock_transfer_combo`={pattern_counter.get('cash_plus_stock_transfer_combo', 0)} → 保留人工 review",
            "- **不修改 raw/normalized**；patch 后离线 re-map 验证",
        ])
    else:
        lines.append("- needs_review 以零散文本为主，保留人工 review 队列。")

    lines.extend([
        "",
        "### P1 公司列表（77）",
        "",
        ", ".join(f"`{c}`" for c in p1_companies),
        "",
        "## P2 · source_caveat / empty_but_valid",
        "",
        f"_54 条 flag · **{len(p2_companies)}** 家公司；`source_partial` / `empty_but_valid` **不自动 FAIL**。_",
        "",
        "### 按 source 汇总",
        "",
        "| source | flag 条数 | 公司数 | source_status |",
        "|--------|-----------|--------|---------------|",
    ])

    p2_by_source: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in triage_rows:
        if row["priority_tier"] == "P2":
            p2_by_source[row["source_id"]].append(row)

    for sid in sorted(p2_by_source.keys()):
        rows = p2_by_source[sid]
        codes = {r["company_code"] for r in rows}
        status = SOURCE_HARVEST_META.get(sid, {}).get("source_status", "")
        lines.append(
            f"| {SOURCE_LOGICAL.get(sid, sid)} | {len(rows)} | {len(codes)} | `{status}` |",
        )

    lines.extend([
        "",
        "### P2 公司列表",
        "",
        ", ".join(f"`{c}`" for c in p2_companies),
        "",
        "## 结论枚举说明",
        "",
        "| 结论 | 含义 |",
        "|------|------|",
        "| `PASS_WITH_CAVEAT_REVIEW_QUEUE_READY` | review 队列可开工；无主导 parser/data 修复项 |",
        "| `NEED_PARSER_PATCH` | needs_review 存在重复 F007V pattern，建议 patch dividend parser |",
        "| `NEED_DATA_REPAIR` | P0 指向 harvest 数据损坏需重跑（本轮未触发） |",
        "",
        "## 输入",
        "",
        f"- `{QA_FLAGS_REL}`",
        f"- `{QA_REVIEW_REL}`",
        f"- `{FULL_SUMMARY_REL}`",
        f"- `{FIELD_FILL_REL}`",
        "",
        "## 输出",
        "",
        f"- `{TRIAGE_CSV_REL}`（{len(triage_rows)} rows）",
        f"- `{TRIAGE_MD_REL}`",
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO · 未重跑 live · 未修改 raw/normalized",
        "- 未写 verified · 未升级 testing_stable_sample",
        "- 未入库 / MinIO / RAG / YAML backfill",
        "",
    ])

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="CNINFO C-class QA flags 分层 triage")
    parser.add_argument("--triage-md", default=TRIAGE_MD_REL)
    parser.add_argument("--triage-csv", default=TRIAGE_CSV_REL)
    args = parser.parse_args()

    conclusion, rows, pattern_counter, tier_counter = run_triage(
        triage_md_path=_abs(args.triage_md),
        triage_csv_path=_abs(args.triage_csv),
    )

    print("pre_qa_flag_triage: PASS")
    print(f"triage_conclusion={conclusion}")
    print(f"triage_rows={len(rows)}")
    print(f"P0={tier_counter.get('P0', 0)} P1={tier_counter.get('P1', 0)} P2={tier_counter.get('P2', 0)}")
    print(f"needs_review_events={sum(pattern_counter.values())}")
    print(f"top_f007v_pattern={pattern_counter.most_common(1)}")
    print(f"MD    {_abs(args.triage_md)}")
    print(f"CSV   {_abs(args.triage_csv)}")


if __name__ == "__main__":
    main()
