"""
Seed B-class periodic report document metadata fixtures from Phase 1 found rows.

Reads Phase 1 coverage CSV (read-only), joins identity mapping for org_id,
applies title guard, writes JSONL fixtures + seed report CSV/MD.

Does NOT modify Phase 1 CSV, does NOT request CNINFO, does NOT download/parse PDF.

Usage:
    python lab/seed_cninfo_b_class_document_fixtures.py
    python lab/seed_cninfo_b_class_document_fixtures.py --max-per-type 5
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_COVERAGE_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_report_p1_coverage_validation.csv"
)
DEFAULT_IDENTITY_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_report_p1_identity_mapping.csv"
)
DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "periodic_report_document_fixtures.jsonl"
)
DEFAULT_SEED_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_document_seed_report.csv"
)
DEFAULT_SEED_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_document_seed_summary.md"
)

SOURCE_ID = "cninfo_periodic_report_pdf"
CREATED_FROM = "phase1_report_retrieval"
MAX_TOTAL_DEFAULT = 20

REPORT_TYPES = (
    "annual_report",
    "semi_annual_report",
    "quarterly_report_q1",
    "quarterly_report_q3",
)

DOCUMENT_TYPE_MAP = {
    "annual_report": "annual_report",
    "semi_annual_report": "semi_annual_report",
    "quarterly_report_q1": "quarterly_report_q1",
    "quarterly_report_q3": "quarterly_report_q3",
}

TITLE_GUARD_PATTERNS = [
    "披露提示性公告",
    "提示性公告",
    "摘要",
    "问询函",
    "回复公告",
    "说明会",
    "延期披露",
]


def _strip_html(title: str) -> str:
    return re.sub(r"<[^>]+>", "", title or "").strip()


def _title_guard_hit(title: str) -> Optional[str]:
    clean = _strip_html(title)
    for p in sorted(TITLE_GUARD_PATTERNS, key=len, reverse=True):
        if p in clean:
            return p
    return None


def _load_identity_map(path: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = (row.get("company_code") or "").strip()
            org_id = (row.get("cninfo_org_id") or "").strip()
            if code and org_id:
                mapping[code] = org_id
    return mapping


def _normalize_report_period(expected_period: str, report_type: str) -> str:
    ep = (expected_period or "").strip()
    if report_type == "annual_report" and re.fullmatch(r"\d{4}", ep):
        return f"{ep}-12-31"
    if report_type == "semi_annual_report" and ep.endswith("H1"):
        return f"{ep[:-2]}-06-30"
    if report_type == "quarterly_report_q1" and ep.endswith("Q1"):
        return f"{ep[:-2]}-03-31"
    if report_type == "quarterly_report_q3" and ep.endswith("Q3"):
        return f"{ep[:-2]}-09-30"
    return ep


def _announcement_date(publish_time: str) -> Optional[str]:
    if not publish_time:
        return None
    m = re.match(r"(\d{4}-\d{2}-\d{2})", publish_time)
    return m.group(1) if m else None


def _document_id(company_code: str, report_type: str, expected_period: str, pdf_url: str) -> str:
    key = f"{SOURCE_ID}|{company_code}|{report_type}|{expected_period}|{pdf_url}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]


def _seed_id(company_code: str, report_type: str, expected_period: str) -> str:
    return f"{company_code}_{report_type}_{expected_period}".replace("/", "-")


def select_candidates(
    rows: List[Dict[str, str]],
    max_per_type: int,
    max_total: int,
) -> List[Dict[str, str]]:
    by_type: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        if (row.get("found") or "").lower() != "yes":
            continue
        rt = row.get("report_type", "")
        if rt in REPORT_TYPES:
            by_type[rt].append(row)

    selected: List[Dict[str, str]] = []
    for rt in REPORT_TYPES:
        pool = sorted(by_type.get(rt, []), key=lambda r: r.get("company_code", ""))
        selected.extend(pool[:max_per_type])
        if len(selected) >= max_total:
            break
    return selected[:max_total]


def build_document_record(
    row: Dict[str, str],
    org_id: Optional[str],
) -> Dict[str, Any]:
    company_code = (row.get("company_code") or "").strip()
    report_type = row.get("report_type", "")
    expected_period = row.get("expected_period", "")
    title = _strip_html(row.get("matched_title", ""))
    pdf_url = (row.get("pdf_url") or "").strip()
    document_type = DOCUMENT_TYPE_MAP[report_type]

    raw_metadata = {
        "phase1_row": {
            k: row.get(k, "")
            for k in (
                "company_code", "company_name", "exchange", "board", "mapping_status",
                "cninfo_announcement_query_code", "report_type", "expected_period",
                "found", "matched_title", "publish_time", "parsed_report_period",
                "pdf_url", "matched_strategy", "http_status_code", "failure_reason",
                "crawl_time", "notes",
            )
        }
    }

    return {
        "document_id": _document_id(company_code, report_type, expected_period, pdf_url),
        "source_id": SOURCE_ID,
        "company_code": company_code,
        "company_name": row.get("company_name", ""),
        "org_id": org_id or None,
        "title": title,
        "document_type": document_type,
        "report_period": _normalize_report_period(expected_period, report_type),
        "announcement_date": _announcement_date(row.get("publish_time", "")),
        "pdf_url": pdf_url,
        "retrieval_status": "found",
        "classification_status": "classified_correctly",
        "classification_confidence": "high",
        "source_confidence": "testing_stable_sample",
        "raw_metadata_json": raw_metadata,
        "created_from": CREATED_FROM,
        "notes": "Offline metadata seed from Phase 1 effective found row; PDF not downloaded.",
    }


def process_row(
    row: Dict[str, str],
    identity_map: Dict[str, str],
) -> Tuple[Optional[Dict[str, Any]], Dict[str, str]]:
    company_code = (row.get("company_code") or "").strip()
    report_type = row.get("report_type", "")
    expected_period = row.get("expected_period", "")
    title_raw = row.get("matched_title", "")
    title_clean = _strip_html(title_raw)
    pdf_url = (row.get("pdf_url") or "").strip()

    seed_row = {
        "seed_id": _seed_id(company_code, report_type, expected_period),
        "company_code": company_code,
        "company_name": row.get("company_name", ""),
        "report_type": report_type,
        "report_period": _normalize_report_period(expected_period, report_type),
        "title": title_clean,
        "document_type": DOCUMENT_TYPE_MAP.get(report_type, ""),
        "pdf_url_available": "yes" if pdf_url else "no",
        "retrieval_status": "found",
        "classification_status": "classified_correctly",
        "seed_status": "seeded",
        "notes": "",
    }

    guard = _title_guard_hit(title_raw)
    if guard:
        seed_row["retrieval_status"] = "title_excluded"
        seed_row["classification_status"] = "title_excluded_from_periodic_but_routed"
        seed_row["seed_status"] = "skipped_title_excluded"
        seed_row["notes"] = f"excluded by Phase 1 title guard ({guard})"
        return None, seed_row

    if not pdf_url:
        seed_row["seed_status"] = "skipped_missing_pdf_url"
        seed_row["notes"] = "missing pdf_url"
        return None, seed_row

    if not company_code or not report_type or not title_clean:
        seed_row["seed_status"] = "skipped_missing_required_field"
        seed_row["notes"] = "missing company_code, report_type, or title"
        return None, seed_row

    org_id = identity_map.get(company_code)
    doc = build_document_record(row, org_id)
    if not org_id:
        doc["notes"] += " org_id not found in identity mapping."

    return doc, seed_row


def write_jsonl(path: str, records: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_seed_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "seed_id", "company_code", "company_name", "report_type", "report_period",
        "title", "document_type", "pdf_url_available", "retrieval_status",
        "classification_status", "seed_status", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(
    path: str,
    seed_rows: List[Dict[str, str]],
    fixtures_path: str,
    coverage_csv: str,
    identity_csv: str,
    max_per_type: int,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = len(seed_rows)
    seeded = sum(1 for r in seed_rows if r["seed_status"] == "seeded")
    skipped_title = sum(1 for r in seed_rows if r["seed_status"] == "skipped_title_excluded")
    skipped_pdf = sum(1 for r in seed_rows if r["seed_status"] == "skipped_missing_pdf_url")
    skipped_req = sum(1 for r in seed_rows if r["seed_status"] == "skipped_missing_required_field")

    by_doc_type = Counter(r["document_type"] for r in seed_rows if r["seed_status"] == "seeded")

    lines = [
        "# CNINFO B 类 Periodic Report Document Seed Summary",
        "",
        f"_生成时间：{now}（离线 Phase 1 → B 类 document metadata seed）_",
        "",
        "## 1. 目的",
        "",
        "从 Phase 1 A 类 **effective found** 报告 retrieval 行离线生成 B 类 `document` metadata fixture。",
        "**不下载 PDF、不解析 PDF、不请求 CNINFO、不入库、不写 verified。**",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| Phase 1 coverage CSV | `{os.path.relpath(coverage_csv, BASE_DIR)}` |",
        f"| P1 identity mapping | `{os.path.relpath(identity_csv, BASE_DIR)}` |",
        f"| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |",
        f"| Category routing | `config/cninfo_announcement_categories.yaml` |",
        f"| 脚本 | `lab/seed_cninfo_b_class_document_fixtures.py` |",
        "",
        f"抽样策略：每 `report_type` 最多 **{max_per_type}** 条（按 `company_code` 排序），总数 ≤ **{MAX_TOTAL_DEFAULT}**。",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_candidates | **{total}** |",
        f"| seeded | **{seeded}** |",
        f"| skipped_title_excluded | **{skipped_title}** |",
        f"| skipped_missing_pdf_url | **{skipped_pdf}** |",
        f"| skipped_missing_required_field | **{skipped_req}** |",
        "",
        "### by document_type (seeded)",
        "",
    ]
    for dt in REPORT_TYPES:
        mapped = DOCUMENT_TYPE_MAP[dt]
        lines.append(f"- `{mapped}`: **{by_doc_type.get(mapped, 0)}**")
    lines.extend([
        "",
        f"Fixture 输出：`{os.path.relpath(fixtures_path, BASE_DIR)}`",
        "",
        "## 4. Fixture 字段说明",
        "",
        "| 字段 | 说明 |",
        "|------|------|",
        "| document_id | SHA256 派生逻辑主键 |",
        "| source_id | `cninfo_periodic_report_pdf` |",
        "| company_code / company_name / org_id | 公司标识（org_id 来自 P1 identity mapping） |",
        "| title | Phase 1 `matched_title`（去 HTML 标签） |",
        "| document_type | annual / semi / Q1 / Q3 |",
        "| report_period | 由 `expected_period` 归一化为日期 |",
        "| announcement_date | 来自 `publish_time` 日期部分 |",
        "| pdf_url | Phase 1 检索 URL（未下载） |",
        "| retrieval_status | `found` |",
        "| classification_status | `classified_correctly` |",
        "| source_confidence | `testing_stable_sample`（非 verified） |",
        "| raw_metadata_json | 完整 Phase 1 行快照 |",
        "| created_from | `phase1_report_retrieval` |",
        "",
        "## 5. 质量边界",
        "",
        "- 这是 **metadata fixture**，不是 corpus parsing 结果。",
        "- **不代表** PDF 已下载、已解析或已生成 embedding。",
        "- Phase 1 effective found 已做 title filter；本脚本 **二次 title guard** 防止误入 periodic seed。",
        "- **不写 verified**；`source_confidence=testing_stable_sample` 仅表示 retrieval 机制证据层级。",
        "",
        "## 6. 下一步",
        "",
        "1. 起草 B 类 `document` JSON Schema（`schemas/b_class/`）。",
        "2. 对 fixture 做 schema validation。",
        "3. 后续才考虑 parser / chunker 设计。",
        "4. **暂不下载 PDF。**",
        "",
        "## 附录",
        "",
        "详见 [cninfo_b_class_document_seed_report.csv](cninfo_b_class_document_seed_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed B-class document fixtures from Phase 1 found rows")
    parser.add_argument("--coverage-csv", default=DEFAULT_COVERAGE_CSV)
    parser.add_argument("--identity-csv", default=DEFAULT_IDENTITY_CSV)
    parser.add_argument("--output-jsonl", default=DEFAULT_FIXTURES)
    parser.add_argument("--output-csv", default=DEFAULT_SEED_CSV)
    parser.add_argument("--output-md", default=DEFAULT_SEED_MD)
    parser.add_argument("--max-per-type", type=int, default=5)
    parser.add_argument("--max-total", type=int, default=MAX_TOTAL_DEFAULT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    with open(args.coverage_csv, encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))

    identity_map = _load_identity_map(args.identity_csv)
    candidates = select_candidates(all_rows, args.max_per_type, args.max_total)

    documents: List[Dict[str, Any]] = []
    seed_report: List[Dict[str, str]] = []

    for row in candidates:
        doc, seed_row = process_row(row, identity_map)
        seed_report.append(seed_row)
        if doc is not None:
            documents.append(doc)

    write_jsonl(args.output_jsonl, documents)
    write_seed_csv(args.output_csv, seed_report)
    write_summary_md(
        args.output_md,
        seed_report,
        args.output_jsonl,
        args.coverage_csv,
        args.identity_csv,
        args.max_per_type,
    )

    seeded = sum(1 for r in seed_report if r["seed_status"] == "seeded")
    print(
        f"SUMMARY  candidates={len(candidates)}  seeded={seeded}  "
        f"skipped={len(candidates) - seeded}"
    )
    print(f"JSONL {args.output_jsonl}")
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")

    sys.exit(0)


if __name__ == "__main__":
    main()
