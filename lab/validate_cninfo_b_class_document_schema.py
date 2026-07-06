"""
CNINFO B-class offline document schema validation (Era C Phase 3).

Reads fixtures/b_class/document/*.jsonl and validates each line against
schemas/b_class/b_document.schema.json using jsonschema Draft-07.

Does NOT request CNINFO, does NOT download/parse PDF, does NOT modify fixtures.

Usage:
    python lab/validate_cninfo_b_class_document_schema.py
    python lab/validate_cninfo_b_class_document_schema.py --fixtures fixtures/b_class/document/periodic_report_document_fixtures.jsonl
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_SCHEMA = os.path.join(BASE_DIR, "schemas", "b_class", "b_document.schema.json")
DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "periodic_report_document_fixtures.jsonl"
)
DEFAULT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_document_schema_validation_report.csv"
)
DEFAULT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_document_schema_validation_summary.md"
)

try:
    from jsonschema import Draft7Validator
except ImportError:
    Draft7Validator = None  # type: ignore


@dataclass
class ValidationRow:
    fixture_index: int
    document_id: str
    source_id: str
    document_type: str
    company_code: str
    title: str
    validation_status: str
    error_message: str
    notes: str = ""


def load_schema(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                records.append({"_parse_error": f"line {line_no}: {exc}"})
    return records


def validate_record(record: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    if Draft7Validator is None:
        return False, ["jsonschema package not installed"]
    if "_parse_error" in record:
        return False, [record["_parse_error"]]
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
) -> List[ValidationRow]:
    schema = load_schema(schema_path)
    records = load_jsonl(fixtures_path)
    rows: List[ValidationRow] = []

    for idx, record in enumerate(records):
        ok, errors = validate_record(record, schema)
        rows.append(ValidationRow(
            fixture_index=idx,
            document_id=str(record.get("document_id", "")),
            source_id=str(record.get("source_id", "")),
            document_type=str(record.get("document_type", "")),
            company_code=str(record.get("company_code", "")),
            title=str(record.get("title", "")),
            validation_status="pass" if ok else "fail",
            error_message="; ".join(errors) if errors else "",
            notes="metadata fixture; PDF not downloaded",
        ))
    return rows


def write_csv(path: str, rows: List[ValidationRow]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "fixture_index", "document_id", "source_id", "document_type",
        "company_code", "title", "validation_status", "error_message", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "fixture_index": row.fixture_index,
                "document_id": row.document_id,
                "source_id": row.source_id,
                "document_type": row.document_type,
                "company_code": row.company_code,
                "title": row.title,
                "validation_status": row.validation_status,
                "error_message": row.error_message,
                "notes": row.notes,
            })


def write_summary_md(
    path: str,
    rows: List[ValidationRow],
    schema_path: str,
    fixtures_path: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = len(rows)
    passed = sum(1 for r in rows if r.validation_status == "pass")
    failed = total - passed
    by_type = Counter(r.document_type for r in rows if r.validation_status == "pass")
    fail_rows = [r for r in rows if r.validation_status == "fail"]

    lines = [
        "# CNINFO B 类 Document Schema Validation Summary",
        "",
        f"_生成时间：{now}（离线 metadata fixture schema validation）_",
        "",
        "## 1. 目的",
        "",
        "对 B 类 `b_document` logical record 做 **离线 JSON Schema 校验**。",
        "**不下载 PDF、不解析 PDF、不请求 CNINFO、不入库、不写 verified。**",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| Schema | `{os.path.relpath(schema_path, BASE_DIR)}` |",
        f"| Fixture JSONL | `{os.path.relpath(fixtures_path, BASE_DIR)}` |",
        f"| 脚本 | `lab/validate_cninfo_b_class_document_schema.py` |",
        "",
        "其余 7 个 B 类 schema（raw_file / version / section / chunk / citation / parse_run / event_link）已起草，待对应 fixture 后再校验。",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_documents | **{total}** |",
        f"| pass | **{passed}** |",
        f"| fail | **{failed}** |",
        "",
        "### by document_type (pass)",
        "",
    ]
    for dt in sorted(by_type.keys()):
        lines.append(f"- `{dt}`: **{by_type[dt]}**")
    if not by_type:
        lines.append("- _(none)_")

    lines.extend(["", "## 4. 错误案例", ""])
    if fail_rows:
        for r in fail_rows:
            lines.append(f"- index **{r.fixture_index}** `{r.document_id}`: {r.error_message}")
    else:
        lines.append("_无失败记录。_")

    lines.extend([
        "",
        "## 5. 质量边界",
        "",
        "- Fixture 是 **document metadata**，不是 corpus parsing 结果。",
        "- **PDF 未下载**；`pdf_url` 仅为 CNINFO 静态链接登记。",
        "- **PDF 未解析**；chunk / citation / embedding **未生成**。",
        "- **不写 verified**；`source_confidence` 仅表示 registry 证据层级。",
        "",
        "## 6. 下一步",
        "",
        "1. 增加 `b_raw_file` fixture（URL 登记，download_status=not_started）。",
        "2. 设计 parser / chunker plan。",
        "3. Seed inquiry / meeting / general document fixtures。",
        "4. 后续再考虑下载和解析。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_b_class_document_schema_validation_report.csv](cninfo_b_class_document_schema_validation_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate B-class document fixtures against JSON Schema")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    parser.add_argument("--fixtures", default=DEFAULT_FIXTURES)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = run_validation(args.fixtures, args.schema)
    write_csv(args.output_csv, rows)
    write_summary_md(args.output_md, rows, args.schema, args.fixtures)

    passed = sum(1 for r in rows if r.validation_status == "pass")
    failed = len(rows) - passed
    print(f"SUMMARY  total={len(rows)}  pass={passed}  fail={failed}")
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
