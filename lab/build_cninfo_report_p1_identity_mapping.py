"""
为 P1 扩展样本构建 CNINFO identity mapping（离线）。

主表：cninfo_report_p1_sample_companies.csv（200 家）
优先合并 P0 identity mapping；其余从 eval_companies_full_market_2024.yaml 读取 orgid。
不联网、不访问 CNINFO、不伪造 orgId。

用法：
    python lab/build_cninfo_report_p1_identity_mapping.py
"""

from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML required: pip install pyyaml") from exc

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")

P1_SAMPLE_CSV = os.path.join(OUT_DIR, "cninfo_report_p1_sample_companies.csv")
P0_MAPPING_CSV = os.path.join(OUT_DIR, "cninfo_company_identity_mapping.csv")
FULL_MARKET_YAML = os.path.join(BASE_DIR, "lab", "eval_companies_full_market_2024.yaml")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_report_p1_identity_mapping.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_report_p1_identity_mapping_summary.md")

CSV_FIELDS = [
    "company_code",
    "company_name",
    "exchange",
    "board",
    "sample_layer",
    "is_p0_overlap",
    "cninfo_stock_code",
    "cninfo_org_id",
    "cninfo_profile_url",
    "cninfo_announcement_query_code",
    "mapping_status",
    "mapping_source",
    "mapping_confidence",
    "needs_manual_review",
    "source_file",
    "notes",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_code(code: str) -> str:
    s = str(code or "").strip()
    if not s:
        return ""
    return s.zfill(6) if s.isdigit() else s


def is_valid_orgid(orgid: str) -> bool:
    o = (orgid or "").strip()
    return bool(o) and o.lower() != "unknown"


def build_profile_url(query_code: str, orgid: str) -> str:
    if not query_code or not is_valid_orgid(orgid):
        return ""
    return (
        f"https://www.cninfo.com.cn/new/disclosure/stock?"
        f"stockCode={query_code}&orgId={orgid}#companyProfile"
    )


def load_p1_sample() -> List[Dict]:
    with open(P1_SAMPLE_CSV, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_p0_mapping() -> Dict[str, Dict]:
    if not os.path.isfile(P0_MAPPING_CSV):
        return {}
    out: Dict[str, Dict] = {}
    with open(P0_MAPPING_CSV, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = normalize_code(row.get("company_code", ""))
            if code:
                out[code] = row
    return out


def load_yaml_index() -> Tuple[Dict[str, Dict], Dict[str, str]]:
    """返回 (code→record, legacy_430→920 当 orgId 一致时)."""
    with open(FULL_MARKET_YAML, encoding="utf-8") as fh:
        companies = yaml.safe_load(fh).get("companies") or []

    by_code: Dict[str, Dict] = {}
    org_by_code: Dict[str, str] = {}
    for c in companies:
        code = normalize_code(c.get("stock_code", ""))
        if not code:
            continue
        by_code[code] = c
        org = (c.get("orgid") or c.get("orgId") or c.get("org_id") or "").strip()
        if org:
            org_by_code[code] = org

    legacy_to_920: Dict[str, str] = {}
    for code, org in org_by_code.items():
        if code.startswith("430") and len(code) >= 6:
            cand_920 = "92" + code[2:]
            if org_by_code.get(cand_920) == org:
                legacy_to_920[code] = cand_920
    return by_code, legacy_to_920


def resolve_bse_query_codes(
    company_code: str,
    p0_row: Optional[Dict],
    legacy_to_920: Dict[str, str],
) -> Tuple[str, str, str]:
    """返回 (cninfo_stock_code, announcement_query_code, notes_suffix)."""
    notes_parts: List[str] = []
    if p0_row:
        stock = (p0_row.get("cninfo_stock_code") or "").strip()
        query = (p0_row.get("cninfo_announcement_query_code") or "").strip()
        if stock and query:
            return stock, query, "BSE codes from P0 identity mapping"

    code = normalize_code(company_code)
    if code.startswith("920"):
        return code, code, ""

    if code in legacy_to_920:
        q = legacy_to_920[code]
        return q, q, f"BSE legacy {code} → query code {q} (YAML orgId match)"

    if code.startswith(("430", "83", "87")):
        notes_parts.append(f"BSE old/new code needs review; using company_code {code} for query")
        return code, code, "; ".join(notes_parts)

    return code, code, ""


def row_from_p0(sample: Dict, p0: Dict) -> Dict:
    company_code = normalize_code(sample.get("company_code", ""))
    orgid = (p0.get("cninfo_org_id") or "").strip()
    stock = (p0.get("cninfo_stock_code") or company_code).strip()
    query = (p0.get("cninfo_announcement_query_code") or stock or company_code).strip()
    profile = (p0.get("cninfo_profile_url") or "").strip() or build_profile_url(query, orgid)
    status = (p0.get("mapping_status") or "").strip()
    if is_valid_orgid(orgid):
        status = "mapped"
    else:
        status = "needs_orgid_mapping"

    source = "p0_identity_mapping"
    confidence = "high" if status == "mapped" else "low"

    return {
        "company_code": company_code,
        "company_name": sample.get("company_name", p0.get("company_name", "")),
        "exchange": sample.get("exchange", p0.get("exchange", "")),
        "board": sample.get("board", p0.get("board", "")),
        "sample_layer": sample.get("sample_layer", ""),
        "is_p0_overlap": sample.get("is_p0_overlap", "no"),
        "cninfo_stock_code": stock,
        "cninfo_org_id": orgid,
        "cninfo_profile_url": profile,
        "cninfo_announcement_query_code": query,
        "mapping_status": status,
        "mapping_source": source,
        "mapping_confidence": confidence,
        "needs_manual_review": (p0.get("needs_manual_review") or "no").strip() or "no",
        "source_file": os.path.relpath(P0_MAPPING_CSV, BASE_DIR),
        "notes": (p0.get("notes") or "").strip() or "merged from P0 identity mapping",
    }


def row_from_yaml(
    sample: Dict,
    yaml_rec: Dict,
    legacy_to_920: Dict[str, str],
) -> Dict:
    company_code = normalize_code(sample.get("company_code", ""))
    orgid = (
        (yaml_rec.get("orgid") or yaml_rec.get("orgId") or yaml_rec.get("org_id") or "")
        .strip()
    )
    layer = sample.get("sample_layer", "")

    stock = company_code
    query = company_code
    extra_notes = ""

    if layer == "bse":
        stock, query, extra_notes = resolve_bse_query_codes(company_code, None, legacy_to_920)
    elif not orgid:
        pass
    else:
        stock = company_code
        query = company_code

    profile = build_profile_url(query, orgid)
    if is_valid_orgid(orgid):
        status = "mapped"
        source = "full_market_yaml"
        confidence = "high"
        review = "no"
        notes = f"orgId from {os.path.relpath(FULL_MARKET_YAML, BASE_DIR)}"
    else:
        status = "needs_orgid_mapping"
        source = "inferred_code_only"
        confidence = "low"
        review = "yes"
        notes = "no orgId in full_market_yaml; needs manual mapping"

    if extra_notes:
        notes = f"{notes}; {extra_notes}" if notes else extra_notes

    if layer == "chinext" and is_valid_orgid(orgid):
        notes += "; chinext: prefer numeric orgId from YAML over F10 gssh rule"

    return {
        "company_code": company_code,
        "company_name": sample.get("company_name", yaml_rec.get("short_name", "")),
        "exchange": sample.get("exchange", yaml_rec.get("exchange", "")),
        "board": sample.get("board", ""),
        "sample_layer": layer,
        "is_p0_overlap": sample.get("is_p0_overlap", "no"),
        "cninfo_stock_code": stock,
        "cninfo_org_id": orgid if is_valid_orgid(orgid) else "",
        "cninfo_profile_url": profile,
        "cninfo_announcement_query_code": query,
        "mapping_status": status,
        "mapping_source": source,
        "mapping_confidence": confidence,
        "needs_manual_review": review,
        "source_file": os.path.relpath(FULL_MARKET_YAML, BASE_DIR),
        "notes": notes,
    }


def row_missing_yaml(sample: Dict) -> Dict:
    company_code = normalize_code(sample.get("company_code", ""))
    return {
        "company_code": company_code,
        "company_name": sample.get("company_name", ""),
        "exchange": sample.get("exchange", ""),
        "board": sample.get("board", ""),
        "sample_layer": sample.get("sample_layer", ""),
        "is_p0_overlap": sample.get("is_p0_overlap", "no"),
        "cninfo_stock_code": company_code,
        "cninfo_org_id": "",
        "cninfo_profile_url": "",
        "cninfo_announcement_query_code": company_code,
        "mapping_status": "needs_orgid_mapping",
        "mapping_source": "unknown",
        "mapping_confidence": "low",
        "needs_manual_review": "yes",
        "source_file": "",
        "notes": "company_code not found in full_market_yaml",
    }


def build_mapping_rows() -> List[Dict]:
    samples = load_p1_sample()
    p0_map = load_p0_mapping()
    yaml_by_code, legacy_to_920 = load_yaml_index()

    rows: List[Dict] = []
    for sample in samples:
        code = normalize_code(sample.get("company_code", ""))
        if code in p0_map:
            rows.append(row_from_p0(sample, p0_map[code]))
        elif code in yaml_by_code:
            rows.append(row_from_yaml(sample, yaml_by_code[code], legacy_to_920))
        else:
            rows.append(row_missing_yaml(sample))

    rows.sort(key=lambda r: (r.get("sample_layer", ""), r.get("company_code", "")))
    return rows


def write_csv(rows: List[Dict]) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_summary(rows: List[Dict]) -> None:
    total = len(rows)
    mapped = [r for r in rows if r.get("mapping_status") == "mapped"]
    unmapped = [r for r in rows if r.get("mapping_status") != "mapped"]
    by_layer_mapped: Dict[str, Counter] = defaultdict(Counter)
    by_exchange_mapped: Counter = Counter()
    by_board_mapped: Counter = Counter()
    source_counter = Counter(r.get("mapping_source", "") for r in rows)

    for r in rows:
        layer = r.get("sample_layer", "")
        by_layer_mapped[layer]["total"] += 1
        if r.get("mapping_status") == "mapped":
            by_layer_mapped[layer]["mapped"] += 1
        by_exchange_mapped[r.get("exchange", "")] += 1 if r.get("mapping_status") == "mapped" else 0
        by_board_mapped[r.get("board", "")] += 1 if r.get("mapping_status") == "mapped" else 0

    expected_if_all_mapped = len(mapped) * 4
    ready = len(mapped) >= 1

    lines = [
        "# CNINFO A 类报告 P1 identity mapping 摘要",
        "",
        f"- 生成时间：{now_iso()}",
        f"- 脚本：`lab/build_cninfo_report_p1_identity_mapping.py`",
        f"- 计划文档：[cninfo_report_p1_expansion_plan.md](cninfo_report_p1_expansion_plan.md)",
        "",
        "## 1. 输入文件",
        "",
        f"- P1 样本：`{os.path.relpath(P1_SAMPLE_CSV, BASE_DIR)}`",
        f"- P0 mapping：`{os.path.relpath(P0_MAPPING_CSV, BASE_DIR)}`",
        f"- 全市场 YAML：`{os.path.relpath(FULL_MARKET_YAML, BASE_DIR)}`",
        "",
        "## 2. 样本与 mapping 规模",
        "",
        f"- P1 样本总数：**{total}**",
        f"- **mapped**：**{len(mapped)}**",
        f"- **needs_orgid_mapping**：**{len(unmapped)}**",
        f"- 若全部 mapped 运行 coverage，expected rows ≈ {expected_if_all_mapped}（mapped × 4 report_type）",
        "",
        "## 3. 按 sample_layer（mapped / 层内总数）",
        "",
        "| sample_layer | mapped | total |",
        "|--------------|--------|-------|",
    ]
    for layer in sorted(by_layer_mapped.keys()):
        c = by_layer_mapped[layer]
        lines.append(f"| {layer} | {c['mapped']} | {c['total']} |")

    lines.extend(["", "## 4. 按 exchange / board（mapped 家数）", ""])
    lines.append("### exchange")
    lines.append("")
    ex_total = Counter(r.get("exchange", "") for r in rows)
    for ex in sorted(ex_total.keys()):
        m = sum(1 for r in rows if r.get("exchange") == ex and r.get("mapping_status") == "mapped")
        lines.append(f"- {ex}：{m}/{ex_total[ex]} mapped")
    lines.extend(["", "### board", ""])
    bd_total = Counter(r.get("board", "") for r in rows)
    for bd in sorted(bd_total.keys()):
        m = sum(1 for r in rows if r.get("board") == bd and r.get("mapping_status") == "mapped")
        lines.append(f"- {bd}：{m}/{bd_total[bd]} mapped")

    lines.extend(
        [
            "",
            "## 5. mapping_source 分布",
            "",
        ]
    )
    for src, cnt in source_counter.most_common():
        lines.append(f"- {src or '(empty)'}：{cnt}")

    lines.extend(
        [
            "",
            "## 6. 来源统计",
            "",
            f"- 来自 P0 identity mapping：**{source_counter.get('p0_identity_mapping', 0)}**",
            f"- 来自 full_market_yaml：**{source_counter.get('full_market_yaml', 0)}**",
            f"- inferred_code_only / unknown：**{source_counter.get('inferred_code_only', 0) + source_counter.get('unknown', 0)}**",
            "",
            "## 7. 仍 needs_orgid_mapping 的公司",
            "",
        ]
    )
    if unmapped:
        lines.append("| company_code | company_name | sample_layer | mapping_source | notes |")
        lines.append("|--------------|--------------|--------------|----------------|-------|")
        for r in unmapped:
            lines.append(
                f"| {r.get('company_code', '')} | {r.get('company_name', '')} | "
                f"{r.get('sample_layer', '')} | {r.get('mapping_source', '')} | "
                f"{(r.get('notes') or '')[:60]} |"
            )
    else:
        lines.append("- （无）")

    lines.extend(
        [
            "",
            "## 8. 是否足够运行 P1 coverage",
            "",
        ]
    )
    if len(mapped) == total:
        lines.append(
            f"- **可以运行 P1 coverage**：{len(mapped)}/{total} 家均已 mapped；"
            f"expected rows = **{expected_if_all_mapped}**。"
        )
    elif ready:
        lines.append(
            f"- **可以部分运行 P1 coverage**：{len(mapped)}/{total} 家 mapped，"
            f"expected rows = **{len(mapped) * 4}**；skipped = {len(unmapped) * 4} 行。"
        )
    else:
        lines.append("- **尚不可运行 P1 coverage**：无 mapped 公司。")

    lines.extend(
        [
            "",
            "## 9. 下一步运行命令",
            "",
            "```bash",
            "python lab/validate_cninfo_report_coverage.py \\",
            "  --input-mapping outputs/validation/cninfo_report_p1_identity_mapping.csv \\",
            "  --output-prefix outputs/validation/cninfo_report_p1_coverage \\",
            "  --sample-csv outputs/validation/cninfo_report_p1_sample_companies.csv",
            "```",
            "",
            "## 10. 边界",
            "",
            "- 未联网；未访问 CNINFO；未伪造 orgId",
            "- 未修改 P0 mapping / P1 sample CSV",
            "- BSE 430→920 仅在 YAML 中 orgId 一致时自动提升 query code",
            "- 创业板 numeric orgId 来自 YAML；P0 重叠公司仍保留 P0 mapping",
            "- **不写 verified**",
            "",
        ]
    )

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    rows = build_mapping_rows()
    write_csv(rows)
    write_summary(rows)
    mapped = sum(1 for r in rows if r.get("mapping_status") == "mapped")
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    print(f"mapped={mapped}, needs_orgid_mapping={len(rows) - mapped}")
    print(f"Summary -> {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
