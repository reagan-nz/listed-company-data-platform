"""
CNINFO C-class offline profile schema validation (Era C Phase 4).

Reads fixtures/c_class/known_company_profile_fixtures.jsonl and validates each
record against schemas/c_class/*.schema.json using jsonschema Draft-07.

Does NOT request CNINFO, does NOT probe endpoint, does NOT modify fixtures.

Usage:
    python lab/validate_cninfo_c_class_profile_schema.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_FIXTURES = os.path.join(BASE_DIR, "fixtures", "c_class", "known_company_profile_fixtures.jsonl")
DEFAULT_SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas", "c_class")
DEFAULT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_profile_schema_validation_report.csv"
)
DEFAULT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_profile_schema_validation_summary.md"
)

try:
    from jsonschema import Draft7Validator
except ImportError:
    Draft7Validator = None  # type: ignore


@dataclass
class ValidationRow:
    fixture_index: int
    schema_name: str
    record_type: str
    company_code: str
    source_id: str
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


def run_validation(fixtures_path: str, schemas_dir: str) -> List[ValidationRow]:
    wrappers = load_jsonl(fixtures_path)
    rows: List[ValidationRow] = []

    for idx, wrapper in enumerate(wrappers):
        if "_parse_error" in wrapper:
            rows.append(ValidationRow(
                fixture_index=idx,
                schema_name="",
                record_type="",
                company_code="",
                source_id="",
                validation_status="fail",
                error_message=wrapper["_parse_error"],
                notes="JSONL parse error",
            ))
            continue

        schema_name = str(wrapper.get("schema_name", ""))
        record_type = str(wrapper.get("record_type", ""))
        record = wrapper.get("record") or {}
        schema_path = os.path.join(schemas_dir, schema_name)

        if not schema_name or not os.path.isfile(schema_path):
            rows.append(ValidationRow(
                fixture_index=idx,
                schema_name=schema_name,
                record_type=record_type,
                company_code=str(record.get("company_code", "")),
                source_id=str(record.get("source_id", "")),
                validation_status="fail",
                error_message=f"schema not found: {schema_name}",
                notes="offline fixture",
            ))
            continue

        schema = load_schema(schema_path)
        ok, errors = validate_record(record, schema)
        wrapper_notes = str(
            wrapper.get("notes", "")
            or record.get("notes", "")
            or "offline fixture; endpoint not probed"
        )
        rows.append(ValidationRow(
            fixture_index=idx,
            schema_name=schema_name,
            record_type=record_type,
            company_code=str(record.get("company_code", "")),
            source_id=str(record.get("source_id", "")),
            validation_status="pass" if ok else "fail",
            error_message="; ".join(errors) if errors else "",
            notes=wrapper_notes,
        ))
    return rows


def write_csv(path: str, rows: List[ValidationRow]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "fixture_index", "schema_name", "record_type", "company_code",
        "source_id", "validation_status", "error_message", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "fixture_index": row.fixture_index,
                "schema_name": row.schema_name,
                "record_type": row.record_type,
                "company_code": row.company_code,
                "source_id": row.source_id,
                "validation_status": row.validation_status,
                "error_message": row.error_message,
                "notes": row.notes,
            })


def write_summary_md(
    path: str,
    rows: List[ValidationRow],
    fixtures_path: str,
    schemas_dir: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = len(rows)
    passed = sum(1 for r in rows if r.validation_status == "pass")
    failed = total - passed
    by_schema = Counter(
        r.schema_name for r in rows if r.validation_status == "pass"
    )
    fail_rows = [r for r in rows if r.validation_status == "fail"]

    lines = [
        "# CNINFO C 类 Profile Schema Validation Summary",
        "",
        f"_生成时间：{now}（offline known-company fixture schema validation）_",
        "",
        "## 1. 目的",
        "",
        "对 C 类 company profile logical record 做 **离线 JSON Schema 校验**。",
        "**不请求 CNINFO、不 probe endpoint、不入库、不写 verified。**",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| Fixture JSONL | `{os.path.relpath(fixtures_path, BASE_DIR)}` |",
        f"| Schemas | `{os.path.relpath(schemas_dir, BASE_DIR)}/` |",
        f"| 脚本 | `lab/validate_cninfo_c_class_profile_schema.py` |",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_fixtures | **{total}** |",
        f"| pass | **{passed}** |",
        f"| fail | **{failed}** |",
        f"| result | **{'PASS' if failed == 0 else 'FAIL'}** |",
        "",
        "### by schema_name (pass)",
        "",
    ]
    for name, count in sorted(by_schema.items()):
        lines.append(f"- `{name}`: **{count}**")
    if not by_schema:
        lines.append("_none_")

    lines.extend([
        "",
        "## 4. 错误案例",
        "",
    ])
    if fail_rows:
        for r in fail_rows:
            lines.append(
                f"- idx={r.fixture_index} `{r.schema_name}` `{r.record_type}` "
                f"({r.company_code}): {r.error_message}"
            )
    else:
        lines.append("_无 fail。_")

    lines.extend([
        "",
        "## 5. 质量边界",
        "",
        "- fixture 仅为 **offline shape test**；不代表 CNINFO 实际返回。",
        "- **endpoint 未 probe**；`fetch_status=not_started` 合法。",
        "- **不写 verified**；不代表 source 可用。",
        "",
        "## 6. 下一步",
        "",
        "1. per-source DevTools probe。",
        "2. 回填 endpoint / records_path。",
        "3. 建立 C 类 known-company profile validation 脚本（小样本 live）。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_c_class_profile_schema_validation_report.csv](cninfo_c_class_profile_schema_validation_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate C-class profile fixtures against JSON Schema")
    parser.add_argument("--fixtures", default=DEFAULT_FIXTURES)
    parser.add_argument("--schemas-dir", default=DEFAULT_SCHEMAS_DIR)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = run_validation(args.fixtures, args.schemas_dir)
    write_csv(args.output_csv, rows)
    write_summary_md(args.output_md, rows, args.fixtures, args.schemas_dir)

    total = len(rows)
    passed = sum(1 for r in rows if r.validation_status == "pass")
    failed = total - passed
    result = "PASS" if failed == 0 else "FAIL"

    print(f"SUMMARY  total={total}  pass={passed}  fail={failed}  result={result}")
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")

    if failed > 0:
        sys.exit(1)
    if args.strict and total == 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
