"""
CNINFO B-class offline raw_file schema validation (Era C Phase 3).

Reads document fixtures for skip stats, validates raw_file JSONL against
schemas/b_class/b_raw_file.schema.json. Does NOT download PDF or request CNINFO.

Usage:
    python lab/validate_cninfo_b_class_raw_file_schema.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_DOCUMENT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "periodic_report_document_fixtures.jsonl"
)
DEFAULT_RAW_FILE_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "b_class", "raw_file", "periodic_report_raw_file_fixtures.jsonl"
)
DEFAULT_SCHEMA = os.path.join(BASE_DIR, "schemas", "b_class", "b_raw_file.schema.json")
DEFAULT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_raw_file_schema_validation_report.csv"
)
DEFAULT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_raw_file_schema_validation_summary.md"
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
    document_fixtures_path: str,
    raw_file_fixtures_path: str,
    schema_path: str,
) -> Tuple[List[Dict[str, str]], int, int]:
    documents = load_jsonl(document_fixtures_path)
    raw_files = load_jsonl(raw_file_fixtures_path)
    schema = load_schema(schema_path)

    skipped = sum(1 for d in documents if not (d.get("pdf_url") or "").strip())
    rows: List[Dict[str, str]] = []

    for idx, record in enumerate(raw_files):
        ok, errors = validate_record(record, schema)
        rows.append({
            "fixture_index": str(idx),
            "raw_file_id": str(record.get("raw_file_id", "")),
            "document_id": str(record.get("document_id", "")),
            "source_url_available": "yes" if record.get("source_url") else "no",
            "download_status": str(record.get("download_status", "")),
            "validation_status": "pass" if ok else "fail",
            "error_message": "; ".join(errors) if errors else "",
            "notes": str(record.get("notes", "")),
        })

    return rows, len(documents), skipped


def write_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "fixture_index", "raw_file_id", "document_id", "source_url_available",
        "download_status", "validation_status", "error_message", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(
    path: str,
    rows: List[Dict[str, str]],
    total_documents: int,
    skipped: int,
    document_fixtures_path: str,
    raw_file_fixtures_path: str,
    schema_path: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seeded = len(rows)
    passed = sum(1 for r in rows if r["validation_status"] == "pass")
    failed = seeded - passed
    fail_rows = [r for r in rows if r["validation_status"] == "fail"]

    lines = [
        "# CNINFO B 类 Raw File Fixture Seed & Schema Validation Summary",
        "",
        f"_生成时间：{now}（离线 document → raw_file metadata seed + schema validation）_",
        "",
        "## 1. 目的",
        "",
        "从 B 类 `b_document` metadata fixture 派生 `b_raw_file` metadata fixture，",
        "并做离线 JSON Schema 校验。**不下载 PDF、不请求 CNINFO、不计算真实 sha256。**",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| Document fixture | `{os.path.relpath(document_fixtures_path, BASE_DIR)}` |",
        f"| Raw file fixture | `{os.path.relpath(raw_file_fixtures_path, BASE_DIR)}` |",
        f"| Schema | `{os.path.relpath(schema_path, BASE_DIR)}` |",
        f"| Seed 脚本 | `lab/seed_cninfo_b_class_raw_file_fixtures.py` |",
        f"| Validation 脚本 | `lab/validate_cninfo_b_class_raw_file_schema.py` |",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_documents | **{total_documents}** |",
        f"| raw_file_seeded | **{seeded}** |",
        f"| skipped_missing_source_url | **{skipped}** |",
        f"| schema_pass | **{passed}** |",
        f"| schema_fail | **{failed}** |",
        "",
        "## 4. 字段说明",
        "",
        "| 字段 | 当前值 | 说明 |",
        "|------|--------|------|",
        "| `download_status` | `not_started` | PDF 尚未下载 |",
        "| `sha256_candidate` | `null` | 未计算 hash |",
        "| `file_size_candidate` | `null` | 未确认文件大小 |",
        "| `storage_uri_candidate` | `null` | 未写入对象存储 |",
        "| `fetch_time` | `null` | 无下载时间 |",
        "| `mime_type` | `application/pdf` | 预期类型（未验证） |",
        "| `created_from` | `b_document_fixture_seed` | 派生来源标记 |",
        "",
        "## 5. 质量边界",
        "",
        "- **PDF 未下载**；`source_url` 仅为 CNINFO 静态链接登记。",
        "- **sha256 未计算**；`storage_uri` 未生成；`file_size` 未确认。",
        "- **不写 verified**；这是 metadata-only fixture。",
        "- 不接 MinIO / MongoDB / PostgreSQL。",
        "",
        "## 6. 下一步",
        "",
        "1. 起草 parser / chunker plan。",
        "2. 若后续允许下载，再更新 `download_status` / `sha256_candidate` / `storage_uri_candidate`。",
        "3. **暂不进入真实 storage。**",
        "",
        "## 附录",
        "",
    ]
    if fail_rows:
        lines.extend(["### 错误案例", ""])
        for r in fail_rows:
            lines.append(f"- `{r['raw_file_id']}`: {r['error_message']}")
        lines.append("")

    lines.append(
        "详见 [cninfo_b_class_raw_file_schema_validation_report.csv]"
        "(cninfo_b_class_raw_file_schema_validation_report.csv)。"
    )
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate B-class raw_file fixtures against JSON Schema")
    parser.add_argument("--document-fixtures", default=DEFAULT_DOCUMENT_FIXTURES)
    parser.add_argument("--raw-file-fixtures", default=DEFAULT_RAW_FILE_FIXTURES)
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows, total_documents, skipped = run_validation(
        args.document_fixtures,
        args.raw_file_fixtures,
        args.schema,
    )
    write_csv(args.output_csv, rows)
    write_summary_md(
        args.output_md,
        rows,
        total_documents,
        skipped,
        args.document_fixtures,
        args.raw_file_fixtures,
        args.schema,
    )

    passed = sum(1 for r in rows if r["validation_status"] == "pass")
    failed = len(rows) - passed
    print(
        f"SUMMARY  total_documents={total_documents}  seeded={len(rows)}  "
        f"skipped={skipped}  pass={passed}  fail={failed}"
    )
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
