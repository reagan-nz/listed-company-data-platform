"""
CNINFO B-class offline title category routing validation (Era C Phase 3).

Reads config/cninfo_announcement_categories.yaml and known-document benchmark fixtures,
applies routing rules from plans/cninfo_b_class_category_routing_rules.md, writes CSV + MD.

Does NOT request CNINFO, does NOT download/parse PDF, does NOT write verified.

Usage:
    python lab/validate_cninfo_b_class_category_routing.py
    python lab/validate_cninfo_b_class_category_routing.py --benchmark fixtures/b_class/known_documents/known_document_benchmark.yaml
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CATEGORIES = os.path.join(BASE_DIR, "config", "cninfo_announcement_categories.yaml")
DEFAULT_BENCHMARK = os.path.join(
    BASE_DIR, "fixtures", "b_class", "known_documents", "known_document_benchmark.yaml"
)
DEFAULT_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_b_class_category_routing_report.csv")
DEFAULT_MD = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_b_class_category_routing_summary.md")

FALSE_POSITIVE_REASONS = {
    "summary": "summary",
    "delayed_disclosure_notice": "delayed_disclosure_notice",
    "inquiry_reply_as_report": "inquiry_reply_as_report",
    "meeting_notice_as_report": "meeting_notice_as_report",
    "announcement_preview": "announcement_preview",
    "wrong_company": "wrong_company",
}

# 本公司报告期提示：「关于披露第一季度报告…」——非交叉披露
_OWN_PERIOD_AFTER_GUANYU = re.compile(
    r"关于披露"
    r"(?:20\d{2}年)?"
    r"(?:第?[一二三四]季度|一季度|三季度|半年度?|年度|"
    r"年报|半年报|季度报告|"
    r"第一季度报告|第三季度报告|半年度报告|年度报告)"
)

# 交叉披露他司报告：「关于披露冀东水泥半年报…」「关于披露某某股份…年度报告」
_CROSS_ENTITY_REPORT = re.compile(
    r"关于披露"
    r"(.+?)"
    r"(?:年报|半年报|半年度报告|年度报告|第一季度报告|第三季度报告|"
    r"一季度报告|三季度报告|季度报告|报告)"
)


@dataclass
class RouteResult:
    predicted_route_to: str
    predicted_document_type: str
    predicted_classification: str
    classification_status: str
    false_positive_reason: str = ""
    matched_patterns: List[str] = field(default_factory=list)
    notes: str = ""


def _sorted_patterns(patterns: List[str]) -> List[str]:
    return sorted(patterns, key=len, reverse=True)


def _match_any(title: str, patterns: List[str]) -> List[str]:
    return [p for p in _sorted_patterns(patterns) if p in title]


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _inquiry_document_type(title: str) -> str:
    reply_markers = ["回复公告", "回复函", "回复的公告", "问询函回复", "关注函回复"]
    inquiry_markers = ["问询函", "监管问询函", "关注函", "年报问询函"]
    reply_hits = _match_any(title, reply_markers)
    inquiry_hits = _match_any(title, inquiry_markers)
    if reply_hits:
        return "inquiry_reply"
    return "regulatory_inquiry"


def _filter_meeting_hits(title: str, hits: List[str]) -> List[str]:
    """股东大会通知（非说明会）归 general，见 routing rules §6 example 9."""
    if not hits:
        return hits
    if "说明会" in title or "投资者关系活动记录表" in title:
        return hits
    if "股东大会" in title and "通知" in title:
        return [h for h in hits if "股东大会" not in h]
    return hits


def _periodic_blocked(title: str) -> bool:
    """非定期报告全文 blocker（routing rules example 5 等）。"""
    blockers = ["补充公告", "补充的", "更正公告", "取消"]
    return any(b in title for b in blockers)


def _is_wrong_company_cross_disclosure(title: str) -> bool:
    """Phase 1 wrong_company：交叉披露他司报告（与本公司 announcement_preview 相邻但语义不同）。

    例：
    - 关于披露冀东水泥半年报的提示性公告 → True
    - 关于披露他司报告的提示性公告 → True
    - 关于披露第一季度报告的提示性公告 → False（本公司报告期提示）
    - 关于延期披露… → False（延期披露优先；且「关于披露」是其子串）
    """
    if not title:
        return False
    # 「关于延期披露」含子串「关于披露」，须先排除
    if "延期披露" in title:
        return False
    if "他司" in title or "其他公司" in title:
        return True
    if "关于披露" not in title:
        return False
    if _OWN_PERIOD_AFTER_GUANYU.search(title):
        return False
    m = _CROSS_ENTITY_REPORT.search(title)
    if not m:
        return False
    entity = m.group(1)
    return bool(entity and not re.fullmatch(r"[\d年月日\s的]*", entity))


def _excluded_false_positive_reason(
    hits: List[str],
    *,
    block_key: str = "",
    title: str = "",
) -> str:
    """将 excluded_from_periodic 命中映射到 validation_design §7 false_positive 类型。"""
    joined = "".join(hits)
    haystack = joined + title
    if block_key == "delayed_disclosure" or "延期披露" in haystack:
        return FALSE_POSITIVE_REASONS["delayed_disclosure_notice"]
    # wrong_company 优先于 announcement_preview（交叉披露标题常同时含「提示性公告」）
    if block_key == "wrong_company" or _is_wrong_company_cross_disclosure(title):
        return FALSE_POSITIVE_REASONS["wrong_company"]
    if block_key == "announcement_preview" or any(
        p in haystack for p in ("披露提示性公告", "提示性公告", "预告公告")
    ):
        return FALSE_POSITIVE_REASONS["announcement_preview"]
    if block_key == "report_summary" or any(p in haystack for p in ("摘要", "解读")):
        return FALSE_POSITIVE_REASONS["summary"]
    return ""


def _meeting_document_type(title: str) -> str:
    if "投资者关系活动记录表" in title:
        return "investor_relations_activity"
    return "meeting_notice"


def _periodic_document_type(title: str, positive: Dict[str, List[str]]) -> Optional[str]:
    best: Optional[Tuple[int, str]] = None
    for doc_type, patterns in positive.items():
        for p in _sorted_patterns(patterns):
            if p in title:
                if best is None or len(p) > best[0]:
                    best = (len(p), doc_type)
    return best[1] if best else None


def _general_document_type(title: str, patterns: List[str]) -> str:
    if "董事会" in title and "决议" in title:
        return "board_resolution"
    if "股东大会" in title and "通知" in title:
        return "shareholder_meeting_material"
    if "监事会" in title:
        return "announcement"
    if _match_any(title, patterns):
        return "announcement"
    return "other"


def route_title(title: str, config: Dict[str, Any]) -> RouteResult:
    categories = config.get("categories") or {}
    excluded_cfg = config.get("excluded_from_periodic_routing") or {}

    inquiry_cat = categories.get("inquiry_reply") or {}
    meeting_cat = categories.get("meeting_notice") or {}
    periodic_cat = categories.get("periodic_report") or {}
    general_cat = categories.get("general_announcement") or {}

    inquiry_patterns = inquiry_cat.get("positive_patterns") or []
    meeting_patterns = meeting_cat.get("positive_patterns") or []
    periodic_positive = periodic_cat.get("positive_patterns") or {}
    periodic_exclusions = periodic_cat.get("exclusion_patterns") or []
    general_patterns = general_cat.get("positive_patterns") or []

    inquiry_hits = _match_any(title, inquiry_patterns)
    meeting_hits = _filter_meeting_hits(title, _match_any(title, meeting_patterns))
    periodic_exclusion_hits = _match_any(title, periodic_exclusions)
    periodic_doc_type = _periodic_document_type(title, periodic_positive)
    if _periodic_blocked(title):
        periodic_doc_type = None
        if not periodic_exclusion_hits:
            periodic_exclusion_hits = ["补充/更正类公告"]

    matched: List[str] = []
    excluded_from_periodic = False

    # Priority 1: inquiry / reply
    if inquiry_hits and meeting_hits:
        return RouteResult(
            predicted_route_to=general_cat.get("route_to", {}).get("source_id", "cninfo_general_announcement_pdf"),
            predicted_document_type="other",
            predicted_classification="ambiguous",
            classification_status="ambiguous",
            matched_patterns=inquiry_hits + meeting_hits,
            notes="Both inquiry and meeting patterns matched",
        )

    if inquiry_hits:
        matched.extend(inquiry_hits)
        doc_type = _inquiry_document_type(title)
        return RouteResult(
            predicted_route_to=inquiry_cat.get("route_to", {}).get("source_id", "cninfo_inquiry_reply_pdf"),
            predicted_document_type=doc_type,
            predicted_classification="inquiry_reply",
            classification_status="classified_correctly",
            false_positive_reason="inquiry_reply_as_report" if periodic_doc_type and not periodic_exclusion_hits else "",
            matched_patterns=matched,
        )

    # Priority 2: meeting / IR
    if meeting_hits:
        matched.extend(meeting_hits)
        return RouteResult(
            predicted_route_to=meeting_cat.get("route_to", {}).get("source_id", "cninfo_meeting_notice_pdf"),
            predicted_document_type=_meeting_document_type(title),
            predicted_classification="meeting_notice",
            classification_status="classified_correctly",
            false_positive_reason="meeting_notice_as_report" if periodic_doc_type else "",
            matched_patterns=matched,
        )

    # Priority 3: periodic (only if positive match and no exclusion)
    if periodic_doc_type and not periodic_exclusion_hits:
        matched.append(periodic_doc_type)
        return RouteResult(
            predicted_route_to=periodic_cat.get("route_to", {}).get("source_id", "cninfo_periodic_report_pdf"),
            predicted_document_type=periodic_doc_type,
            predicted_classification="periodic_report",
            classification_status="classified_correctly",
            matched_patterns=matched,
        )

    if periodic_exclusion_hits:
        excluded_from_periodic = True
        matched.extend(periodic_exclusion_hits)

    # Priority 4: excluded_from_periodic_routing (delayed / summary / preview / wrong_company)
    for key, block in excluded_cfg.items():
        if not isinstance(block, dict):
            continue
        hits = _match_any(title, block.get("positive_patterns") or [])
        if hits:
            matched.extend(hits)
            suggested = (block.get("suggested_document_types") or ["announcement"])[0]
            reason = _excluded_false_positive_reason(hits, block_key=str(key), title=title)
            return RouteResult(
                predicted_route_to=block.get("route_to", {}).get("source_id", "cninfo_general_announcement_pdf"),
                predicted_document_type=suggested,
                predicted_classification="excluded_from_periodic_but_routed",
                classification_status="title_excluded_from_periodic_but_routed",
                false_positive_reason=reason,
                matched_patterns=matched,
                notes="Routed via excluded_from_periodic_routing",
            )

    # Priority 5: general fallback
    general_hits = _match_any(title, general_patterns)
    if general_hits or excluded_from_periodic:
        if general_hits:
            matched.extend(general_hits)
        doc_type = _general_document_type(title, general_patterns)
        status = "title_excluded_from_periodic_but_routed" if excluded_from_periodic else "classified_correctly"
        classification = "excluded_from_periodic_but_routed" if excluded_from_periodic else "general_announcement"
        fp_reason = (
            _excluded_false_positive_reason(matched, title=title)
            if excluded_from_periodic
            else ""
        )
        return RouteResult(
            predicted_route_to=general_cat.get("route_to", {}).get("source_id", "cninfo_general_announcement_pdf"),
            predicted_document_type=doc_type,
            predicted_classification=classification,
            classification_status=status,
            false_positive_reason=fp_reason,
            matched_patterns=matched,
        )

    return RouteResult(
        predicted_route_to=general_cat.get("route_to", {}).get("source_id", "cninfo_general_announcement_pdf"),
        predicted_document_type="other",
        predicted_classification="general_announcement",
        classification_status="classified_correctly",
        notes="No pattern hit; general fallback",
    )


def _normalize_classification(value: Optional[str]) -> str:
    if not value:
        return ""
    v = value.strip()
    if v == "excluded_from_periodic_but_routed":
        return "title_excluded_from_periodic_but_routed"
    return v


def evaluate_benchmark(
    doc: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    title = doc.get("title", "")
    result = route_title(title, config)

    expected_route = doc.get("expected_route_to", "")
    expected_doc_type = doc.get("expected_document_type", "")
    expected_class = _normalize_classification(doc.get("expected_classification", ""))

    predicted_class = result.predicted_classification
    if result.classification_status == "title_excluded_from_periodic_but_routed":
        predicted_class_norm = "title_excluded_from_periodic_but_routed"
    elif result.classification_status == "ambiguous":
        predicted_class_norm = "ambiguous"
    else:
        predicted_class_norm = predicted_class

    route_match = result.predicted_route_to == expected_route
    doc_type_match = result.predicted_document_type == expected_doc_type

    class_match = True
    if expected_class:
        if expected_class == "title_excluded_from_periodic_but_routed":
            class_match = result.classification_status == "title_excluded_from_periodic_but_routed"
        elif expected_class == "ambiguous":
            class_match = result.classification_status == "ambiguous"
        else:
            class_match = result.predicted_classification == expected_class

    # 可选：锁定 false_positive_reason（disclosure/event 边缘分类 lineage）
    expected_fp = doc.get("expected_false_positive_reason")
    if expected_fp is None:
        fp_match = True
    else:
        fp_match = result.false_positive_reason == expected_fp

    return {
        "benchmark_id": doc.get("benchmark_id", ""),
        "title": title,
        "expected_route_to": expected_route,
        "predicted_route_to": result.predicted_route_to,
        "expected_document_type": expected_doc_type,
        "predicted_document_type": result.predicted_document_type,
        "expected_classification": doc.get("expected_classification", ""),
        "predicted_classification": result.predicted_classification,
        "route_match": "PASS" if route_match else "FAIL",
        "document_type_match": "PASS" if doc_type_match else "FAIL",
        "classification_status": result.classification_status,
        "false_positive_reason": result.false_positive_reason,
        "notes": doc.get("notes", "") or result.notes,
        "benchmark_group": doc.get("benchmark_group", ""),
        "overall_pass": route_match and doc_type_match and class_match and fp_match,
    }


def write_csv(path: str, rows: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "benchmark_id", "title", "expected_route_to", "predicted_route_to",
        "expected_document_type", "predicted_document_type",
        "expected_classification", "predicted_classification",
        "route_match", "document_type_match", "classification_status",
        "false_positive_reason", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(
    path: str,
    rows: List[Dict[str, Any]],
    categories_path: str,
    benchmark_path: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = len(rows)
    route_pass = sum(1 for r in rows if r["route_match"] == "PASS")
    doc_pass = sum(1 for r in rows if r["document_type_match"] == "PASS")
    ambiguous = sum(1 for r in rows if r["classification_status"] == "ambiguous")
    fp_rows = [r for r in rows if r.get("benchmark_group") == "false_positive_guard"]
    fp_caught = sum(
        1 for r in fp_rows
        if r["route_match"] == "PASS"
        and r["predicted_route_to"] != "cninfo_periodic_report_pdf"
    )

    mismatches = [r for r in rows if r["route_match"] == "FAIL" or r["document_type_match"] == "FAIL"]

    groups = ("periodic_report", "inquiry_reply", "meeting_notice", "general_announcement", "false_positive_guard")
    group_stats: Dict[str, Dict[str, int]] = {g: {"total": 0, "route_pass": 0} for g in groups}

    for r in rows:
        g = r.get("benchmark_group") or "other"
        if g not in group_stats:
            group_stats[g] = {"total": 0, "route_pass": 0}
        group_stats[g]["total"] += 1
        if r["route_match"] == "PASS":
            group_stats[g]["route_pass"] += 1

    lines = [
        "# CNINFO B 类 Category Routing Offline Validation Summary",
        "",
        f"_生成时间：{now}（离线 title routing validation）_",
        "",
        "## 1. 目的",
        "",
        "本次为 **离线 title routing validation**：根据 `cninfo_announcement_categories.yaml` 规则",
        "对 benchmark 标题做 `route_to` / `document_type` 预测，**不请求 CNINFO**，**不代表** corpus coverage。",
        "**不写 verified。**",
        "",
        "## 2. 输入",
        "",
        f"| 文件 | 路径 |",
        f"|------|------|",
        f"| Category routing YAML | `{os.path.relpath(categories_path, BASE_DIR)}` |",
        f"| Known-document benchmark | `{os.path.relpath(benchmark_path, BASE_DIR)}` |",
        f"| 脚本 | `lab/validate_cninfo_b_class_category_routing.py` |",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_benchmarks | **{total}** |",
        f"| route_match_count | **{route_pass}** |",
        f"| route_mismatch_count | **{total - route_pass}** |",
        f"| document_type_match_count | **{doc_pass}** |",
        f"| ambiguous_count | **{ambiguous}** |",
        f"| periodic_false_positive_caught_count | **{fp_caught}** / **{len(fp_rows)}** |",
        "",
        f"**总体结论：** {'**PASS**' if not mismatches else '**FAIL**'}",
        "",
        "## 4. 分类型结果",
        "",
    ]

    for g in groups:
        st = group_stats.get(g, {"total": 0, "route_pass": 0})
        if st["total"] == 0:
            continue
        lines.extend([
            f"### `{g}`",
            "",
            f"- total: **{st['total']}**",
            f"- route_match: **{st['route_pass']}** / **{st['total']}**",
            "",
        ])

    lines.extend([
        "## 5. 错误案例",
        "",
    ])
    if not mismatches:
        lines.append("_无 route_mismatch 或 document_type_mismatch。_")
    else:
        for r in mismatches:
            lines.append(
                f"- `{r['benchmark_id']}`: expected `{r['expected_route_to']}` / `{r['expected_document_type']}` "
                f"→ got `{r['predicted_route_to']}` / `{r['predicted_document_type']}`"
            )
    lines.extend([
        "",
        "## 6. 结论",
        "",
        "- 新 routing 规则 **可用于** B 类 corpus title classification 草案（离线 benchmark 层面）。",
        "- 这 **不是** CNINFO retrieval coverage，**不**代表 PDF 可下载或语料非空。",
        "- **不写 verified**；`category_code` 仍为 null。",
        "",
        "## 7. 下一步",
        "",
        "1. 加真实 known-document benchmark（公司代码 + 日期，仍可不联网先做结构）。",
        "2. Probe 官方 CNINFO `category` code 填入 YAML。",
        "3. Seed Phase 1 found reports 为 B 类 document fixtures。",
        "4. 后续再做 corpus retrieval validation（known-document + category-sample）。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_b_class_category_routing_report.csv](cninfo_b_class_category_routing_report.csv)。",
        "",
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CNINFO B-class offline category routing validation")
    parser.add_argument("--categories", default=DEFAULT_CATEGORIES)
    parser.add_argument("--benchmark", default=DEFAULT_BENCHMARK)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    categories_path = os.path.abspath(args.categories)
    benchmark_path = os.path.abspath(args.benchmark)

    config = _load_yaml(categories_path)
    benchmark_data = _load_yaml(benchmark_path)
    documents = benchmark_data.get("documents") or []

    rows: List[Dict[str, Any]] = []
    for doc in documents:
        row = evaluate_benchmark(doc, config)
        rows.append(row)

    write_csv(args.output_csv, rows)
    write_summary_md(args.output_md, rows, categories_path, benchmark_path)

    route_pass = sum(1 for r in rows if r["route_match"] == "PASS")
    doc_pass = sum(1 for r in rows if r["document_type_match"] == "PASS")
    fail_n = sum(1 for r in rows if not r.get("overall_pass", False))

    print(
        f"SUMMARY  benchmarks={len(rows)}  route_pass={route_pass}  "
        f"doc_type_pass={doc_pass}  fail={fail_n}"
    )
    print(f"CSV  {args.output_csv}")
    print(f"MD   {args.output_md}")

    sys.exit(1 if fail_n else 0)


if __name__ == "__main__":
    main()
