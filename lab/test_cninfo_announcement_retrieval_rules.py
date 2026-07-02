"""
CNINFO 公告检索规则回放 + 可选 LLM 复核（Sub Issue 4）。

功能：
- 基于已有公告验证结果（不重新访问 CNINFO）做规则分类匹配。
- 对低置信、多标签或语义不足的记录，可选调用 LLM 复核（需显式传参 --use-llm 且配置 API Key）。

输入：
- outputs/validation/cninfo_announcement_category_validation.csv  （已有公告结果）
- config/cninfo_announcement_retrieval_strategies.yaml            （规则与关键词）

输出（运行后生成）：
- outputs/validation/cninfo_announcement_retrieval_rule_test.csv
- outputs/validation/cninfo_announcement_retrieval_rule_test_summary.md

运行示例（默认不调用 LLM）：
    python lab/test_cninfo_announcement_retrieval_rules.py

调用 DeepSeek：
    DEEPSEEK_API_KEY=xxx python lab/test_cninfo_announcement_retrieval_rules.py --use-llm --llm-provider deepseek

调用 Agnes：
    AGNES_API_KEY=xxx python lab/test_cninfo_announcement_retrieval_rules.py --use-llm --llm-provider agnes

边界：
- 不联网抓 CNINFO；不修改原始 CSV；不改原配置。
- 不下载/解析 PDF，不做数据库/MinIO 接入，不使用 BrowserUser。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests  # only for LLM HTTP if enabled
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")

ANN_CSV = os.path.join(OUT_DIR, "cninfo_announcement_category_validation.csv")
STRATEGY_YAML = os.path.join(BASE_DIR, "config", "cninfo_announcement_retrieval_strategies.yaml")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_announcement_retrieval_rule_test.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_announcement_retrieval_rule_test_summary.md")

CATEGORIES = [
    "semi_annual_report",
    "quarterly_report",
    "performance_forecast",
    "dividend_distribution",
    "shareholder_meeting",
    "board_meeting",
    "supervisory_board",
    "regulatory_inquiry",
    "penalty_litigation",
    "share_repurchase",
    "private_placement",
    "major_asset_restructuring",
    "equity_incentive",
    "share_unlock",
    "unknown",
]

CSV_FIELDS = [
    "company_code",
    "company_name",
    "announcement_title",
    "publish_time",
    "pdf_url",
    "original_category_key",
    "predicted_category_key",
    "predicted_category_name_cn",
    "retrieval_strategy",
    "matched_must_keywords",
    "matched_optional_keywords",
    "matched_exclude_keywords",
    "rule_confidence",
    "llm_review_needed",
    "llm_provider",
    "llm_final_category",
    "llm_final_confidence",
    "llm_reason",
    "final_category",
    "final_confidence",
    "match_reason",
]


@dataclass
class Strategy:
    key: str
    name_cn: str
    strategy: str
    must: List[str]
    optional: List[str]
    exclude: List[str]
    llm_policy: str
    notes: str = ""


def load_strategies() -> List[Strategy]:
    with open(STRATEGY_YAML, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or []
    strategies: List[Strategy] = []
    for item in data:
        strategies.append(
            Strategy(
                key=item.get("category_key", ""),
                name_cn=item.get("category_name_cn", ""),
                strategy=item.get("retrieval_strategy", ""),
                must=item.get("must_any") or [],
                optional=item.get("optional_any") or [],
                exclude=item.get("exclude_any") or [],
                llm_policy=item.get("llm_review_policy", "never"),
                notes=item.get("notes", ""),
            )
        )
    return strategies


def load_announcements() -> List[Dict]:
    rows: List[Dict] = []
    with open(ANN_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            if not (r.get("announcement_title") or "").strip():
                continue
            rows.append(r)
    return rows


def normalize(s: str) -> str:
    return (s or "").strip().lower()


def match_title(title: str, words: List[str]) -> List[str]:
    t = title.lower()
    hits = []
    for w in words:
        w_norm = (w or "").strip().lower()
        if not w_norm:
            continue
        if w_norm in t:
            hits.append(w)
    return hits


def need_llm(rule_confidence: str, multi_label: bool, strategy: Strategy) -> bool:
    if multi_label:
        return True
    if strategy.strategy == "semantic_later":
        return True
    if rule_confidence in ("low", "none"):
        return True
    if strategy.llm_policy == "never":
        return False
    if strategy.llm_policy == "low_confidence_only":
        return rule_confidence in ("low", "none")
    if strategy.llm_policy == "multi_match_only":
        return multi_label
    if strategy.llm_policy == "later":
        return False
    return False


def call_llm(provider: str, title: str, candidate_keys: List[str], api_key: str | None) -> Tuple[str, str, str]:
    """Return (final_category, confidence, reason). If provider unavailable, return ('','unknown','provider_not_available')."""
    if not api_key:
        return "", "unknown", "provider_not_available"

    url = ""
    headers = {}
    payload = {}
    if provider == "deepseek":
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        prompt = (
            "你是一个公告分类助手。只根据公告标题判断最可能的分类，分类必须从候选列表中选择，可以多选。"
            "如果无法判断，返回 unknown。\n"
            f"标题：{title}\n"
            f"候选分类：{', '.join(candidate_keys)}\n"
            "请输出 JSON：{\"final_categories\": [..], \"confidence\": \"high|medium|low|unknown\", \"reason\": \"简短中文理由\"}"
        )
        payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "stream": False}
    elif provider == "agnes":
        url = "https://api.agnes.com/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        prompt = (
            "你是一个公告分类助手。只根据公告标题判断最可能的分类，分类必须从候选列表中选择，可以多选。"
            "如果无法判断，返回 unknown。\n"
            f"标题：{title}\n"
            f"候选分类：{', '.join(candidate_keys)}\n"
            "请输出 JSON：{\"final_categories\": [..], \"confidence\": \"high|medium|low|unknown\", \"reason\": \"简短中文理由\"}"
        )
        payload = {"model": "agnes-chat", "messages": [{"role": "user", "content": prompt}], "stream": False}
    else:
        return "", "unknown", "provider_not_available"

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        if resp.status_code != 200:
            return "", "unknown", f"provider_http_{resp.status_code}"
        data = resp.json()
        content = ""
        if provider == "deepseek":
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        elif provider == "agnes":
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            parsed = json.loads(content)
            cats = parsed.get("final_categories") or []
            conf = parsed.get("confidence") or "unknown"
            reason = parsed.get("reason") or ""
            if not isinstance(cats, list) or not cats:
                return "", conf, reason
            # choose first as final when multi; keep list for reason
            return ",".join(cats), conf, reason
        except Exception:
            return "", "unknown", "parse_error"
    except Exception as exc:
        return "", "unknown", f"provider_error:{exc}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-llm", action="store_true", help="Enable optional LLM review")
    parser.add_argument("--llm-provider", choices=["deepseek", "agnes"], default="deepseek")
    args = parser.parse_args()

    strategies = load_strategies()
    ann_rows = load_announcements()

    rows_out: List[Dict] = []

    for row in ann_rows:
        title = row.get("announcement_title", "")
        orig_cat = row.get("category_key", "")
        matches: List[Tuple[Strategy, List[str], List[str], List[str], str]] = []

        for stg in strategies:
            must_hits = match_title(title, stg.must)
            opt_hits = match_title(title, stg.optional)
            excl_hits = match_title(title, stg.exclude)
            if excl_hits:
                matches.append((stg, must_hits, opt_hits, excl_hits, "low"))
                continue
            if not must_hits:
                continue
            if must_hits and opt_hits:
                conf = "high"
            else:
                conf = "medium"
            matches.append((stg, must_hits, opt_hits, excl_hits, conf))

        if not matches:
            rows_out.append(
                {
                    "company_code": row.get("company_code", ""),
                    "company_name": row.get("company_name", ""),
                    "announcement_title": title,
                    "publish_time": row.get("publish_time", ""),
                    "pdf_url": row.get("pdf_url", ""),
                    "original_category_key": orig_cat,
                    "predicted_category_key": "unknown",
                    "predicted_category_name_cn": "",
                    "retrieval_strategy": "",
                    "matched_must_keywords": "",
                    "matched_optional_keywords": "",
                    "matched_exclude_keywords": "",
                    "rule_confidence": "none",
                    "llm_review_needed": "yes",
                    "llm_provider": "not_used",
                    "llm_final_category": "",
                    "llm_final_confidence": "",
                    "llm_reason": "",
                    "final_category": "unknown",
                    "final_confidence": "none",
                    "match_reason": "no_match",
                }
            )
            continue

        multi_label = len([m for m in matches if m[4] != "low"]) > 1
        for stg, must_hits, opt_hits, excl_hits, conf in matches:
            llm_needed = need_llm(conf, multi_label, stg)
            llm_provider = "not_used"
            llm_cat = ""
            llm_conf = ""
            llm_reason = ""
            final_cat = stg.key
            final_conf = conf
            match_reason = "multi_label_candidate" if multi_label else "rule_match"

            if llm_needed and args.use_llm:
                provider = args.llm_provider
                api_key = os.getenv("DEEPSEEK_API_KEY") if provider == "deepseek" else os.getenv("AGNES_API_KEY")
                cand_list = [m[0].key for m in matches if m[4] != "low"] or CATEGORIES
                llm_cat, llm_conf, llm_reason = call_llm(provider, title, cand_list, api_key)
                llm_provider = provider if api_key else "not_available"
                if llm_cat:
                    final_cat = llm_cat
                    final_conf = llm_conf or conf
                else:
                    final_conf = conf
            elif llm_needed:
                llm_provider = "not_used"
            else:
                llm_provider = "not_used"

            if conf == "high" and not multi_label and not llm_needed:
                final_cat = stg.key
                final_conf = "high"
                llm_provider = "not_used"

            rows_out.append(
                {
                    "company_code": row.get("company_code", ""),
                    "company_name": row.get("company_name", ""),
                    "announcement_title": title,
                    "publish_time": row.get("publish_time", ""),
                    "pdf_url": row.get("pdf_url", ""),
                    "original_category_key": orig_cat,
                    "predicted_category_key": stg.key,
                    "predicted_category_name_cn": stg.name_cn,
                    "retrieval_strategy": stg.strategy,
                    "matched_must_keywords": ";".join(must_hits),
                    "matched_optional_keywords": ";".join(opt_hits),
                    "matched_exclude_keywords": ";".join(excl_hits),
                    "rule_confidence": conf if excl_hits else conf,
                    "llm_review_needed": "yes" if llm_needed else "no",
                    "llm_provider": llm_provider,
                    "llm_final_category": llm_cat,
                    "llm_final_confidence": llm_conf,
                    "llm_reason": llm_reason,
                    "final_category": final_cat,
                    "final_confidence": final_conf,
                    "match_reason": match_reason,
                }
            )

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows_out:
            writer.writerow(r)

    summarize(rows_out, ann_rows, args.use_llm, args.llm_provider)
    print(f"Wrote {len(rows_out)} rows -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")


def summarize(rows_out: List[Dict], ann_rows: List[Dict], use_llm: bool, provider: str) -> None:
    status_counter = Counter(r.get("rule_confidence", "") for r in rows_out)
    final_counter = Counter(r.get("final_category", "") for r in rows_out)
    llm_needed = sum(1 for r in rows_out if r.get("llm_review_needed") == "yes")
    llm_called = sum(1 for r in rows_out if r.get("llm_provider") in ("deepseek", "agnes"))
    llm_skipped = llm_needed - llm_called
    multi_label = sum(1 for r in rows_out if r.get("match_reason") == "multi_label_candidate")

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO 公告检索规则回放摘要\n\n")
        fh.write("## 输入\n")
        fh.write(f"- 公告结果：{os.path.relpath(ANN_CSV, BASE_DIR)}\n")
        fh.write(f"- 策略配置：{os.path.relpath(STRATEGY_YAML, BASE_DIR)}\n\n")

        fh.write("## 数量概览\n")
        fh.write(f"- 输入公告标题数：{len(ann_rows)}\n")
        fh.write(f"- 输出匹配行数：{len(rows_out)}\n")
        fh.write(f"- 规则置信度：high {status_counter.get('high',0)} / medium {status_counter.get('medium',0)} / low {status_counter.get('low',0)} / none {status_counter.get('none',0)}\n")
        fh.write(f"- 需要 LLM 复核：{llm_needed}\n")
        fh.write(f"- 实际调用 LLM：{llm_called}（provider={provider if use_llm else 'not_used'}）\n")
        fh.write(f"- LLM skipped：{llm_skipped}\n")
        fh.write(f"- multi-label 公告：{multi_label}\n\n")

        fh.write("## 按最终分类计数\n")
        for cat, cnt in final_counter.most_common():
            fh.write(f"- {cat}: {cnt}\n")
        fh.write("\n")

        fh.write("## 当前结论\n")
        fh.write("- 规则优先，LLM 仅在低置信/多标签/semantic_later 时使用（需显式 --use-llm）。\n")
        fh.write("- 本摘要需在实际运行脚本后更新具体数值。\n\n")

        fh.write("## 边界确认\n")
        fh.write("- 未联网抓取 CNINFO；未修改原始验证 CSV；未修改原配置。\n")
        fh.write("- 未下载/解析 PDF，未做 OCR；未做数据库/MinIO 接入；未使用 BrowserUser。\n")
        fh.write("- LLM 仅在提供参数和 API Key 时调用；否则标记为 skipped/not_available。\n")


if __name__ == "__main__":
    main()
