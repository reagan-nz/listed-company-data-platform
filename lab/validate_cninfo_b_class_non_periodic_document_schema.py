"""
CNINFO B-class non-periodic document offline schema validation + seed summary.

Validates non_periodic_document_fixtures.jsonl against b_document.schema.json.
Writes validation CSV and combined seed + validation summary MD.

Does NOT request CNINFO, does NOT modify fixtures.

Usage:
    python lab/validate_cninfo_b_class_non_periodic_document_schema.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_SCHEMA = os.path.join(BASE_DIR, "schemas", "b_class", "b_document.schema.json")
DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "non_periodic_document_fixtures.jsonl"
)
DEFAULT_SEED_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_non_periodic_document_seed_report.csv"
)
DEFAULT_BENCHMARK = os.path.join(
    BASE_DIR, "fixtures", "b_class", "known_documents", "known_document_benchmark.yaml"
)
DEFAULT_VALIDATION_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_non_periodic_document_schema_validation_report.csv"
)
DEFAULT_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_non_periodic_document_schema_validation_summary.md"
)

try:
    from jsonschema import Draft7Validator
except ImportError:
    Draft7Validator = None  # type: ignore


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    if not os.path.isfile(path):
        return []
    records: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_schema(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_seed_report(path: str) -> List[Dict[str, str]]:
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate_record(record: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    if Draft7Validator is None:
        return False, ["jsonschema package not installed"]
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
    messages = []
    for err in errors:
        path = ".".join(str(p) for p in err.path) if err.path else "(root)"
        messages.append(f"{path}: {err.message}")
    return len(messages) == 0, messages


def run_validation(
    fixtures_path: str,
    schema_path: str,
) -> List[Dict[str, str]]:
    schema = load_schema(schema_path)
    records = load_jsonl(fixtures_path)
    rows: List[Dict[str, str]] = []

    for idx, record in enumerate(records):
        ok, errors = validate_record(record, schema)
        rows.append({
            "fixture_index": str(idx),
            "document_id": str(record.get("document_id", "")),
            "benchmark_id": str(
                (record.get("raw_metadata_json") or {})
                .get("benchmark_row", {})
                .get("benchmark_id", "")
            ),
            "source_id": str(record.get("source_id", "")),
            "document_type": str(record.get("document_type", "")),
            "title": str(record.get("title", "")),
            "validation_status": "pass" if ok else "fail",
            "error_message": "; ".join(errors) if errors else "",
            "notes": "offline title fixture; no pdf_url",
        })
    return rows


def write_validation_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "fixture_index", "document_id", "benchmark_id", "source_id",
        "document_type", "title", "validation_status", "error_message", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(
    path: str,
    seed_rows: List[Dict[str, str]],
    validation_rows: List[Dict[str, str]],
    benchmark_path: str,
    fixtures_path: str,
    schema_path: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    benchmark_total = len(seed_rows)
    seeded = sum(1 for r in seed_rows if r.get("seed_status") == "seeded")
    skipped_periodic = sum(1 for r in seed_rows if r.get("seed_status") == "skipped_periodic")
    schema_pass = sum(1 for r in validation_rows if r["validation_status"] == "pass")
    schema_fail = len(validation_rows) - schema_pass
    raw_file_seeded = 0

    by_source = Counter(
        r.get("source_id", "") for r in seed_rows if r.get("seed_status") == "seeded"
    )
    by_doc_type = Counter(
        r.get("document_type", "") for r in seed_rows if r.get("seed_status") == "seeded"
    )

    doc_types_order = [
        "inquiry_reply", "regulatory_inquiry", "meeting_notice",
        "investor_relations_activity", "board_resolution",
        "shareholder_meeting_material", "announcement", "other",
    ]
    sources_order = [
        "cninfo_inquiry_reply_pdf",
        "cninfo_meeting_notice_pdf",
        "cninfo_general_announcement_pdf",
    ]

    lines = [
        "# CNINFO B 类 Non-periodic Document Fixture Seed Summary",
        "",
        f"_生成时间：{now}（offline known-document benchmark → non-periodic metadata）_",
        "",
        "## 1. 目的",
        "",
        "从 offline **known-document benchmark** 派生非定期公告 `b_document` metadata fixture。",
        "**不代表真实 CNINFO retrieval coverage**；无 `pdf_url`；不请求 CNINFO。",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| Known-document benchmark | `{os.path.relpath(benchmark_path, BASE_DIR)}` |",
        f"| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |",
        f"| Category routing | `config/cninfo_announcement_categories.yaml` |",
        f"| Schema | `{os.path.relpath(schema_path, BASE_DIR)}` |",
        f"| Seed 脚本 | `lab/seed_cninfo_b_class_non_periodic_document_fixtures.py` |",
        f"| Validation 脚本 | `lab/validate_cninfo_b_class_non_periodic_document_schema.py` |",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| benchmark_total | **{benchmark_total}** |",
        f"| seeded_non_periodic | **{seeded}** |",
        f"| skipped_periodic | **{skipped_periodic}** |",
        f"| schema_pass | **{schema_pass}** |",
        f"| schema_fail | **{schema_fail}** |",
        f"| raw_file_seeded | **{raw_file_seeded}** |",
        "",
        "## 4. 按 source_id 统计",
        "",
    ]
    for sid in sources_order:
        lines.append(f"- `{sid}`: **{by_source.get(sid, 0)}**")
    lines.extend(["", "## 5. 按 document_type 统计", ""])
    for dt in doc_types_order:
        lines.append(f"- `{dt}`: **{by_doc_type.get(dt, 0)}**")

    lines.extend([
        "",
        f"Document fixture：`{os.path.relpath(fixtures_path, BASE_DIR)}`",
        "",
        "## 6. 质量边界",
        "",
        "- 这些是 **offline title fixtures**，不是 CNINFO corpus parsing 结果。",
        "- **没有真实 CNINFO retrieval**；`retrieval_status=found` 仅表示 benchmark 路由命中，非 Phase 1 式 coverage。",
        "- **没有 `pdf_url`**；不能代表 retrieval coverage%。",
        "- `source_confidence=candidate`；**未升级**为 `testing_stable_sample`。",
        "- **不写 verified**。",
        "",
        "### raw_file",
        "",
        "Non-periodic fixtures 为 **title-only metadata**，无 `pdf_url`，**不生成** `b_raw_file` fixture。",
        "`non_periodic_raw_file_fixtures.jsonl` 为空文件；待后续小样本 CNINFO 请求补 URL 后再派生 raw_file。",
        "",
        "## 7. 下一步",
        "",
        "1. 后续用真实 known-document benchmark 替换离线标题样例。",
        "2. 允许小样本请求后再补 `pdf_url`。",
        "3. 有 `pdf_url` 后再派生 `b_raw_file`。",
        "4. **暂不解析 PDF。**",
        "",
        "## 附录",
        "",
        "- [cninfo_b_class_non_periodic_document_seed_report.csv](cninfo_b_class_non_periodic_document_seed_report.csv)",
        "- [cninfo_b_class_non_periodic_document_schema_validation_report.csv](cninfo_b_class_non_periodic_document_schema_validation_report.csv)",
        "",
    ])

    fail_rows = [r for r in validation_rows if r["validation_status"] == "fail"]
    if fail_rows:
        lines.extend(["### Schema 错误", ""])
        for r in fail_rows:
            lines.append(f"- `{r['document_id']}`: {r['error_message']}")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate non-periodic B-class document fixtures")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    parser.add_argument("--fixtures", default=DEFAULT_FIXTURES)
    parser.add_argument("--seed-csv", default=DEFAULT_SEED_CSV)
    parser.add_argument("--benchmark", default=DEFAULT_BENCHMARK)
    parser.add_argument("--output-csv", default=DEFAULT_VALIDATION_CSV)
    parser.add_argument("--output-md", default=DEFAULT_SUMMARY_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validation_rows = run_validation(args.fixtures, args.schema)
    seed_rows = load_seed_report(args.seed_csv)

    write_validation_csv(args.output_csv, validation_rows)
    write_summary_md(
        args.output_md,
        seed_rows,
        validation_rows,
        args.benchmark,
        args.fixtures,
        args.schema,
    )

    passed = sum(1 for r in validation_rows if r["validation_status"] == "pass")
    failed = len(validation_rows) - passed
    print(f"SUMMARY  validated={len(validation_rows)}  pass={passed}  fail={failed}")
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
