"""
CNINFO B-class parse_run dry-run offline schema validation.

Validates document_parse_run_dry_run_fixtures.jsonl against b_document_parse_run.schema.json.
Writes validation CSV + summary MD. Does NOT parse PDF.

Usage:
    python lab/validate_cninfo_b_class_parse_run_schema.py
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

DEFAULT_SCHEMA = os.path.join(BASE_DIR, "schemas", "b_class", "b_document_parse_run.schema.json")
DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "b_class", "parse_run", "document_parse_run_dry_run_fixtures.jsonl"
)
DEFAULT_DRY_RUN_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_parse_run_dry_run_report.csv"
)
DEFAULT_PERIODIC_DOCS = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "periodic_report_document_fixtures.jsonl"
)
DEFAULT_NON_PERIODIC_DOCS = os.path.join(
    BASE_DIR, "fixtures", "b_class", "document", "non_periodic_document_fixtures.jsonl"
)
DEFAULT_VALIDATION_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_parse_run_schema_validation_report.csv"
)
DEFAULT_SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_parse_run_schema_validation_summary.md"
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


def load_dry_run_report(path: str) -> List[Dict[str, str]]:
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


def run_validation(fixtures_path: str, schema_path: str) -> List[Dict[str, str]]:
    schema = load_schema(schema_path)
    records = load_jsonl(fixtures_path)
    rows: List[Dict[str, str]] = []

    for idx, record in enumerate(records):
        ok, errors = validate_record(record, schema)
        rows.append({
            "fixture_index": str(idx),
            "parse_run_id": str(record.get("parse_run_id", "")),
            "document_id": str(record.get("document_id", "")),
            "parse_status": str(record.get("parse_status", "")),
            "raw_file_id": str(record.get("raw_file_id") or ""),
            "validation_status": "pass" if ok else "fail",
            "error_message": "; ".join(errors) if errors else "",
            "notes": "dry-run; parser not executed",
        })
    return rows


def write_validation_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "fixture_index", "parse_run_id", "document_id", "parse_status",
        "raw_file_id", "validation_status", "error_message", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(
    path: str,
    dry_run_rows: List[Dict[str, str]],
    validation_rows: List[Dict[str, str]],
    periodic_docs_path: str,
    non_periodic_docs_path: str,
    raw_files_path: str,
    fixtures_path: str,
    schema_path: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    total_documents = len(load_jsonl(periodic_docs_path)) + len(load_jsonl(non_periodic_docs_path))
    parse_run_seeded = len(validation_rows)
    periodic_count = sum(1 for r in dry_run_rows if r.get("document_group") == "periodic" and r.get("seed_status") == "seeded")
    non_periodic_count = sum(1 for r in dry_run_rows if r.get("document_group") == "non_periodic" and r.get("seed_status") == "seeded")
    schema_pass = sum(1 for r in validation_rows if r["validation_status"] == "pass")
    schema_fail = len(validation_rows) - schema_pass
    status_dist = Counter(r.get("parse_status", "") for r in dry_run_rows if r.get("seed_status") == "seeded")

    lines = [
        "# CNINFO B 类 Parse Run Dry-run Fixture Summary",
        "",
        f"_生成时间：{now}（parse_run dry-run metadata；parser 未执行）_",
        "",
        "## 1. 目的",
        "",
        "为已有 B 类 `b_document` fixture 生成 **`b_document_parse_run` dry-run** 记录，",
        "打通 parse_run schema validation 链路。**不解析 PDF、不下载 PDF。**",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| Periodic documents | `{os.path.relpath(periodic_docs_path, BASE_DIR)}` |",
        f"| Non-periodic documents | `{os.path.relpath(non_periodic_docs_path, BASE_DIR)}` |",
        f"| Periodic raw_file | `{os.path.relpath(raw_files_path, BASE_DIR)}` |",
        f"| Schema | `{os.path.relpath(schema_path, BASE_DIR)}` |",
        f"| Seed 脚本 | `lab/seed_cninfo_b_class_parse_run_dry_run_fixtures.py` |",
        f"| Validation 脚本 | `lab/validate_cninfo_b_class_parse_run_schema.py` |",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_documents | **{total_documents}** |",
        f"| parse_run_seeded | **{parse_run_seeded}** |",
        f"| periodic_parse_run | **{periodic_count}** |",
        f"| non_periodic_parse_run | **{non_periodic_count}** |",
        f"| schema_pass | **{schema_pass}** |",
        f"| schema_fail | **{schema_fail}** |",
        "",
        "## 4. Parse status 分布",
        "",
        f"- `not_started`: **{status_dist.get('not_started', 0)}**（periodic；有 raw_file metadata）",
        f"- `skipped`: **{status_dist.get('skipped', 0)}**（non-periodic；无 pdf_url）",
        "",
        f"Fixture 输出：`{os.path.relpath(fixtures_path, BASE_DIR)}`",
        "",
        "## 5. 质量边界",
        "",
        "- **PDF 未下载**；`parser_name=dry_run_no_parser`，parser **未运行**。",
        "- `page_count` / `text_length` / `error_message` 为 **null** 是预期行为。",
        "- **没有** section / chunk / citation 产出。",
        "- **不代表** corpus 已解析；仅为 schema 链路 dry-run。",
        "- **不写 verified**。",
        "",
        "## 6. 下一步",
        "",
        "1. 后续允许下载 PDF 后，更新 periodic `parse_status`（`not_started` → 真实解析状态）。",
        "2. 有真实 parser 后再生成 section / chunk fixture。",
        "3. 可做 B 类 registry lint 或 corpus retrieval validation 小样本。",
        "4. **暂不解析 PDF。**",
        "",
        "## 附录",
        "",
        "- [cninfo_b_class_parse_run_dry_run_report.csv](cninfo_b_class_parse_run_dry_run_report.csv)",
        "- [cninfo_b_class_parse_run_schema_validation_report.csv](cninfo_b_class_parse_run_schema_validation_report.csv)",
        "",
    ]

    fail_rows = [r for r in validation_rows if r["validation_status"] == "fail"]
    if fail_rows:
        lines.extend(["### Schema 错误", ""])
        for r in fail_rows:
            lines.append(f"- `{r['parse_run_id']}`: {r['error_message']}")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate parse_run dry-run fixtures")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    parser.add_argument("--fixtures", default=DEFAULT_FIXTURES)
    parser.add_argument("--dry-run-csv", default=DEFAULT_DRY_RUN_CSV)
    parser.add_argument("--periodic-documents", default=DEFAULT_PERIODIC_DOCS)
    parser.add_argument("--non-periodic-documents", default=DEFAULT_NON_PERIODIC_DOCS)
    parser.add_argument("--periodic-raw-files", default=os.path.join(
        BASE_DIR, "fixtures", "b_class", "raw_file", "periodic_report_raw_file_fixtures.jsonl"
    ))
    parser.add_argument("--output-csv", default=DEFAULT_VALIDATION_CSV)
    parser.add_argument("--output-md", default=DEFAULT_SUMMARY_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validation_rows = run_validation(args.fixtures, args.schema)
    dry_run_rows = load_dry_run_report(args.dry_run_csv)

    write_validation_csv(args.output_csv, validation_rows)
    write_summary_md(
        args.output_md,
        dry_run_rows,
        validation_rows,
        args.periodic_documents,
        args.non_periodic_documents,
        args.periodic_raw_files,
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
