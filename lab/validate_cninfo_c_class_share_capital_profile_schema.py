"""
CNINFO C-class share_capital_profile fixture schema validation (Era C Phase 4).

Validates fixtures/c_class/share_capital_profile/share_capital_profile_fixtures.jsonl
against schemas/c_class/c_share_capital_profile.schema.json.

No network, no database, no verified.

Usage:
    python lab/validate_cninfo_c_class_share_capital_profile_schema.py
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

DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "c_class", "share_capital_profile", "share_capital_profile_fixtures.jsonl"
)
DEFAULT_SCHEMA = os.path.join(
    BASE_DIR, "schemas", "c_class", "c_share_capital_profile.schema.json"
)
DEFAULT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_share_capital_profile_schema_validation_report.csv"
)
DEFAULT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_share_capital_profile_schema_validation_summary.md"
)

try:
    from jsonschema import Draft7Validator
except ImportError:
    Draft7Validator = None  # type: ignore

CSV_FIELDS = [
    "fixture_index",
    "company_code",
    "report_date",
    "source_id",
    "validation_status",
    "error_message",
    "notes",
]


def load_schema(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                rows.append({"_parse_error": f"line {line_no}: {exc}"})
    return rows


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


def run_validation(fixtures_path: str, schema_path: str) -> List[Dict[str, str]]:
    schema = load_schema(schema_path)
    records = load_jsonl(fixtures_path)
    out: List[Dict[str, str]] = []

    for idx, record in enumerate(records):
        ok, errors = validate_record(record, schema)
        out.append({
            "fixture_index": str(idx),
            "company_code": str(record.get("company_code", "")),
            "report_date": str(record.get("report_date", "")),
            "source_id": str(record.get("source_id", "")),
            "validation_status": "pass" if ok else "fail",
            "error_message": "; ".join(errors) if errors else "",
            "notes": "mapper draft fixture; source_status=testing; not verified",
        })
    return out


def write_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(
    path: str,
    rows: List[Dict[str, str]],
    fixtures_path: str,
    schema_path: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = len(rows)
    passed = sum(1 for r in rows if r["validation_status"] == "pass")
    failed = total - passed
    result = "PASS" if failed == 0 else "FAIL"

    lines = [
        "# CNINFO C 类 Share Capital Profile Schema Validation Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## 3. 总体结果",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| total_fixtures | **{total}** |",
        f"| pass_count | **{passed}** |",
        f"| fail_count | **{failed}** |",
        f"| result | **{result}** |",
        "",
        "## 4. 错误案例",
        "",
    ]
    fail_rows = [r for r in rows if r["validation_status"] == "fail"]
    if fail_rows:
        for r in fail_rows:
            lines.append(
                f"- idx={r['fixture_index']} `{r['company_code']}` "
                f"{r['report_date']}: {r['error_message']}"
            )
    else:
        lines.append("_无 fail。_")

    lines.extend([
        "",
        "## 5. Schema 说明",
        "",
        "- 使用既有 `c_share_capital_profile.schema.json`（未修改）。",
        "- F002V/F024N/F028N/F003N 保留在 `raw_record_json`。",
        "",
        "## 6. 下一步",
        "",
        "1. top_shareholders_profile mapper draft.",
        "2. top_float_shareholders_profile mapper draft.",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate C-class share_capital_profile fixtures")
    parser.add_argument("--fixtures", default=DEFAULT_FIXTURES)
    parser.add_argument("--schema", default=DEFAULT_SCHEMA)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = run_validation(args.fixtures, args.schema)
    write_csv(args.output_csv, rows)
    write_summary_md(args.output_md, rows, args.fixtures, args.schema)

    passed = sum(1 for r in rows if r["validation_status"] == "pass")
    failed = len(rows) - passed
    result = "PASS" if failed == 0 else "FAIL"

    print(f"SUMMARY  total={len(rows)}  pass={passed}  fail={failed}  result={result}")
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")

    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
