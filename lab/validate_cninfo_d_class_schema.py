"""
CNINFO D-class offline schema validation (Era C Phase 3).

Reads fixtures/d_class/*/sample_raw.json, maps to logical records via cninfo_d_class_mappers,
validates against schemas/d_class/*.schema.json using jsonschema.

Does NOT request CNINFO, does NOT connect to a database.

Usage:
    python lab/validate_cninfo_d_class_schema.py
    python lab/validate_cninfo_d_class_schema.py --fixtures-dir fixtures/d_class
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# Allow running as script from repo root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from lab.cninfo_d_class_mappers import (  # noqa: E402
    map_to_company_event,
    map_to_company_metric_daily,
    map_to_company_metric_periodic,
    map_to_disclosure_schedule,
    map_to_industry_aggregate,
    map_to_raw_record_snapshot,
)

try:
    import jsonschema
    from jsonschema import Draft7Validator
except ImportError:
    jsonschema = None  # type: ignore
    Draft7Validator = None  # type: ignore

DEFAULT_FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures", "d_class")
DEFAULT_SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas", "d_class")
DEFAULT_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_d_class_schema_validation_report.csv")
DEFAULT_MD = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_d_class_schema_validation_summary.md")

DEFERRED_NOTES = {
    "abnormal_trading": "detail[] → d_event_party_detail deferred; main event validated only",
    "block_trade": "optional d_company_metric_daily ETL not implemented in v1",
    "margin_trading": "validates all 5 confirmed metric rows per raw record",
    "shareholder_data": "validates all 6 confirmed metric rows per raw record",
    "fund_industry_allocation": "validates all 3 confirmed metric rows per raw record",
}


@dataclass
class ValidationRow:
    fixture_path: str
    source_id: str
    query_mode: str
    target_schema: str
    record_kind: str
    record_index: int
    result: str
    error_count: int
    errors: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class FixtureSummary:
    fixture_path: str
    source_id: str
    query_mode: str
    target_schema: str
    result: str
    logical_record_count: int
    snapshot_result: str
    notes: str = ""


def load_schema(schemas_dir: str, table_name: str) -> Dict[str, Any]:
    path = os.path.join(schemas_dir, f"{table_name}.schema.json")
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


def discover_fixtures(fixtures_dir: str) -> List[str]:
    paths: List[str] = []
    for name in sorted(os.listdir(fixtures_dir)):
        candidate = os.path.join(fixtures_dir, name, "sample_raw.json")
        if os.path.isfile(candidate):
            paths.append(candidate)
    return paths


def map_fixture(fixture: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
    source_id = fixture["source_id"]
    raw = fixture["raw_record"]
    query_mode = fixture.get("query_mode", "default")
    query_params = fixture.get("query_params", {})
    table = fixture["expected_logical_table"]

    if table == "d_disclosure_schedule":
        return table, [map_to_disclosure_schedule(raw, query_mode=query_mode, query_params=query_params)]
    if table == "d_company_event":
        return table, [map_to_company_event(raw, source_id=source_id, query_mode=query_mode, query_params=query_params)]
    if table == "d_company_metric_daily":
        return table, map_to_company_metric_daily(raw, query_mode=query_mode, query_params=query_params)
    if table == "d_company_metric_periodic":
        return table, map_to_company_metric_periodic(raw, query_mode=query_mode, query_params=query_params)
    if table == "d_industry_aggregate":
        return table, map_to_industry_aggregate(raw, query_mode=query_mode, query_params=query_params)
    raise ValueError(f"Unsupported expected_logical_table: {table}")


def run_validation(
    fixtures_dir: str,
    schemas_dir: str,
) -> Tuple[List[ValidationRow], List[FixtureSummary]]:
    rows: List[ValidationRow] = []
    summaries: List[FixtureSummary] = []

    for fixture_path in discover_fixtures(fixtures_dir):
        rel_path = os.path.relpath(fixture_path, BASE_DIR)
        with open(fixture_path, encoding="utf-8") as f:
            fixture = json.load(f)

        source_id = fixture["source_id"]
        query_mode = fixture.get("query_mode", "default")
        table, logical_records = map_fixture(fixture)
        schema = load_schema(schemas_dir, table)

        fixture_fail = False
        for idx, record in enumerate(logical_records):
            ok, errors = validate_record(record, schema)
            result = "PASS" if ok else "FAIL"
            if not ok:
                fixture_fail = True
            rows.append(ValidationRow(
                fixture_path=rel_path,
                source_id=source_id,
                query_mode=query_mode,
                target_schema=table,
                record_kind="logical",
                record_index=idx,
                result=result,
                error_count=len(errors),
                errors=errors,
                notes=DEFERRED_NOTES.get(source_id, ""),
            ))

        snapshot_schema = load_schema(schemas_dir, "d_raw_record_snapshot")
        snapshot = map_to_raw_record_snapshot(fixture)
        snap_ok, snap_errors = validate_record(snapshot, snapshot_schema)
        snap_result = "PASS" if snap_ok else "FAIL"
        if not snap_ok:
            fixture_fail = True
        rows.append(ValidationRow(
            fixture_path=rel_path,
            source_id=source_id,
            query_mode=query_mode,
            target_schema="d_raw_record_snapshot",
            record_kind="snapshot",
            record_index=0,
            result=snap_result,
            error_count=len(snap_errors),
            errors=snap_errors,
        ))

        notes = DEFERRED_NOTES.get(source_id, "")
        if source_id == "abnormal_trading" and fixture.get("raw_record", {}).get("detail"):
            notes = DEFERRED_NOTES["abnormal_trading"]

        summaries.append(FixtureSummary(
            fixture_path=rel_path,
            source_id=source_id,
            query_mode=query_mode,
            target_schema=table,
            result="FAIL" if fixture_fail else "PASS",
            logical_record_count=len(logical_records),
            snapshot_result=snap_result,
            notes=notes,
        ))

    return rows, summaries


def write_csv(path: str, rows: List[ValidationRow]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "fixture_path", "source_id", "query_mode", "target_schema", "record_kind",
            "record_index", "result", "error_count", "errors", "notes",
        ])
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "fixture_path": row.fixture_path,
                "source_id": row.source_id,
                "query_mode": row.query_mode,
                "target_schema": row.target_schema,
                "record_kind": row.record_kind,
                "record_index": row.record_index,
                "result": row.result,
                "error_count": row.error_count,
                "errors": " | ".join(row.errors),
                "notes": row.notes,
            })


def write_summary_md(path: str, summaries: List[FixtureSummary], rows: List[ValidationRow]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    fixture_count = len(summaries)
    source_ids = sorted({s.source_id for s in summaries})
    schemas_used = sorted({s.target_schema for s in summaries} | {"d_raw_record_snapshot"})

    pass_fixtures = sum(1 for s in summaries if s.result == "PASS")
    fail_fixtures = sum(1 for s in summaries if s.result == "FAIL")
    skipped = 0
    logical_records = sum(s.logical_record_count for s in summaries)

    lines = [
        "# CNINFO D 类 Schema Validation Summary",
        "",
        f"_生成时间：{now}（离线 fixture validation）_",
        "",
        "## 1. 目的",
        "",
        "本次为 **离线 fixture schema validation**：使用 Phase 2 文档摘录的小样本 raw record，",
        "经 mapper 草案转换为逻辑 record 后，用 `schemas/d_class/` JSON Schema 校验。",
        "**不请求 CNINFO、不入库、不写 verified。**",
        "",
        "## 2. 覆盖范围",
        "",
        f"| 项 | 数值 |",
        f"|----|------|",
        f"| fixture 数量 | **{fixture_count}** |",
        f"| source 数量 | **{len(source_ids)}** |",
        f"| 逻辑 schema 数量 | **{len(schemas_used) - 1}** |",
        f"| 含 snapshot schema | **{len(schemas_used)}** |",
        "",
        "Sources: " + ", ".join(f"`{s}`" for s in source_ids),
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_fixtures | **{fixture_count}** |",
        f"| pass | **{pass_fixtures}** |",
        f"| fail | **{fail_fixtures}** |",
        f"| skipped | **{skipped}** |",
        f"| generated_logical_records | **{logical_records}** |",
        "",
        f"**总体结论：** {'**PASS**' if fail_fixtures == 0 else '**FAIL**'}",
        "",
        "## 4. 分 source 结果",
        "",
    ]

    for s in summaries:
        lines.extend([
            f"### `{s.source_id}` — `{s.query_mode}`",
            "",
            f"| 项 | 值 |",
            f"|----|-----|",
            f"| fixture path | `{s.fixture_path}` |",
            f"| target schema | `{s.target_schema}` |",
            f"| validation result | **{s.result}** |",
            f"| generated logical records | **{s.logical_record_count}** |",
            f"| raw snapshot | **{s.snapshot_result}** |",
            f"| notes | {s.notes or '—'} |",
            "",
        ])

    lines.extend([
        "## 5. 已知限制",
        "",
        "- fixtures 只是 Phase 2 文档摘录样本，**不代表全量**或长期稳定；",
        "- mapper 为 **草案**，仅做最小字段转换；",
        "- `abnormal_trading` 的 `detail[]` → `d_event_party_detail` **未实现**（deferred）；",
        "- `block_trade` 可选 `d_company_metric_daily` ETL **未做**，仅验证 `d_company_event`；",
        "- `margin_trading` / `shareholder_data` / `fund_industry_allocation` 从一个 raw row 拆多 metric，本版 **全部 confirmed 指标均校验**；",
        "- **不写 verified**；schema pass 不等于生产 schema 锁定。",
        "",
        "## 6. 下一步",
        "",
        "1. 扩充 fixture（empty_but_valid、多 query_mode）；",
        "2. 完善 mapper（party detail、block_trade metric ETL）；",
        "3. 加入 CI：`lint_cninfo_d_class_registry.py` + `validate_cninfo_d_class_schema.py`；",
        "4. 后续如入库，再由 schema draft 推 SQL migration。",
        "",
        "## 附录：逐 record 明细",
        "",
        "详见 [cninfo_d_class_schema_validation_report.csv](cninfo_d_class_schema_validation_report.csv)。",
        "",
    ])

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CNINFO D-class offline schema validation")
    parser.add_argument("--fixtures-dir", default=DEFAULT_FIXTURES_DIR)
    parser.add_argument("--schemas-dir", default=DEFAULT_SCHEMAS_DIR)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    return parser.parse_args()


def main() -> None:
    if jsonschema is None:
        print("ERROR: jsonschema package required. pip install jsonschema", file=sys.stderr)
        sys.exit(2)

    args = parse_args()
    fixtures_dir = os.path.abspath(args.fixtures_dir)
    schemas_dir = os.path.abspath(args.schemas_dir)

    rows, summaries = run_validation(fixtures_dir, schemas_dir)
    write_csv(args.output_csv, rows)
    write_summary_md(args.output_md, summaries, rows)

    fail_n = sum(1 for s in summaries if s.result == "FAIL")
    pass_n = len(summaries) - fail_n
    logical_n = sum(s.logical_record_count for s in summaries)
    print(f"SUMMARY  fixtures={len(summaries)}  pass={pass_n}  fail={fail_n}  logical_records={logical_n}")
    print(f"CSV  {args.output_csv}")
    print(f"MD   {args.output_md}")

    sys.exit(1 if fail_n else 0)


if __name__ == "__main__":
    main()
