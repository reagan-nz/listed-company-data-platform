"""
Seed C-class share_capital_profile fixtures from embedded getStockStructure row samples.

Uses lab/cninfo_c_class_mappers.py — no CNINFO network requests.

Usage:
    python lab/seed_cninfo_c_class_share_capital_profile_fixtures.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_DIR = os.path.join(BASE_DIR, "lab")
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

from cninfo_c_class_mappers import (  # noqa: E402
    DEFAULT_SHARE_CAPITAL_SOURCE_ID,
    compute_raw_record_hash,
    count_mapped_share_capital_profile_fields,
    map_company_share_capital_profile,
)

DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "c_class", "share_capital_profile", "share_capital_profile_fixtures.jsonl"
)
DEFAULT_MAPPER_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_share_capital_profile_mapper_report.csv"
)
DEFAULT_MAPPER_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_share_capital_profile_mapper_summary.md"
)

EMBEDDED_SAMPLES: List[Dict[str, Any]] = [
    {
        "company_code": "600000",
        "company_name": "浦发银行",
        "org_id": "gssh0600000",
        "raw_record": {
            "VARYDATE": "2025-12-31",
            "F002V": "定期报告",
            "F021N": 3330583.83,
            "F022N": 3330583.83,
            "F023N": None,
            "F024N": None,
            "F028N": None,
            "F003N": 3330583.83,
        },
    },
    {
        "company_code": "600000",
        "company_name": "浦发银行",
        "org_id": "gssh0600000",
        "raw_record": {
            "VARYDATE": "2025-10-27",
            "F002V": "可转债转股",
            "F021N": 3330583.83,
            "F022N": 3330583.83,
            "F023N": None,
            "F024N": None,
            "F028N": 0.0,
            "F003N": 3330583.83,
        },
    },
    {
        "company_code": "300001",
        "company_name": "特锐德",
        "org_id": "9900008270",
        "raw_record": {
            "VARYDATE": "2026-06-03",
            "F002V": "股份回购,股权激励",
            "F021N": 102682.8548,
            "F022N": 102682.8548,
            "F023N": None,
            "F024N": None,
            "F028N": 2870.9165,
            "F003N": 105553.7713,
        },
    },
    {
        "company_code": "300001",
        "company_name": "特锐德",
        "org_id": "9900008270",
        "raw_record": {
            "VARYDATE": "2025-12-31",
            "F002V": "定期报告",
            "F021N": 103490.0763,
            "F022N": 103490.0763,
            "F023N": None,
            "F024N": None,
            "F028N": None,
            "F003N": 103490.0763,
        },
    },
    {
        "company_code": "688001",
        "company_name": "华兴源创",
        "org_id": "9900038969",
        "raw_record": {
            "VARYDATE": "2026-05-18",
            "F002V": "可转债转股",
            "F021N": 47156.5619,
            "F022N": 47156.5619,
            "F023N": None,
            "F024N": None,
            "F028N": 0.0,
            "F003N": 47156.5619,
        },
    },
    {
        "company_code": "688001",
        "company_name": "华兴源创",
        "org_id": "9900038969",
        "raw_record": {
            "VARYDATE": "2025-12-31",
            "F002V": "定期报告",
            "F021N": 44537.7843,
            "F022N": 44537.7843,
            "F023N": None,
            "F024N": None,
            "F028N": None,
            "F003N": 44537.7843,
        },
    },
]

MAPPER_CSV_FIELDS = [
    "company_code",
    "company_name",
    "vary_date",
    "map_status",
    "raw_fields_count",
    "mapped_fields_count",
    "raw_record_hash",
    "notes",
]


def seed_fixtures() -> tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    mapped_records: List[Dict[str, Any]] = []
    report_rows: List[Dict[str, str]] = []

    for sample in EMBEDDED_SAMPLES:
        code = sample["company_code"]
        name = sample["company_name"]
        org_id = sample.get("org_id")
        raw = sample["raw_record"]
        raw_fields_count = len(raw)
        vary_date = str(raw.get("VARYDATE") or "")

        mapped = map_company_share_capital_profile(
            raw,
            company_code=code,
            company_name=name,
            source_id=DEFAULT_SHARE_CAPITAL_SOURCE_ID,
            source_status="testing",
            org_id=org_id,
        )

        if mapped is None:
            report_rows.append({
                "company_code": code,
                "company_name": name,
                "vary_date": vary_date,
                "map_status": "skipped_empty",
                "raw_fields_count": str(raw_fields_count),
                "mapped_fields_count": "0",
                "raw_record_hash": compute_raw_record_hash(raw),
                "notes": "Empty raw_record; no fixture row written.",
            })
            continue

        mapped_records.append(mapped)
        report_rows.append({
            "company_code": code,
            "company_name": name,
            "vary_date": vary_date,
            "map_status": "mapped",
            "raw_fields_count": str(raw_fields_count),
            "mapped_fields_count": str(count_mapped_share_capital_profile_fields(mapped)),
            "raw_record_hash": mapped["raw_record_hash"],
            "notes": "Embedded getStockStructure row; mapper draft fixture only; not verified.",
        })

    return mapped_records, report_rows


def write_jsonl(path: str, records: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_mapper_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MAPPER_CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_mapper_md(path: str, rows: List[Dict[str, str]], fixture_count: int) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mapped_n = sum(1 for r in rows if r["map_status"] == "mapped")
    lines = [
        "# CNINFO C 类 Share Capital Profile Mapper Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## 1. 目的",
        "",
        "将 `getStockStructure` 单行 `data.records[]` 映射为 `c_share_capital_profile` fixture。",
        "**无网络请求**；**不写 verified**。",
        "",
        "## 2. 字段映射",
        "",
        "| raw | schema |",
        "|-----|--------|",
        "| VARYDATE | report_date |",
        "| F021N | total_share_capital |",
        "| F022N | float_share_capital |",
        "| F023N | restricted_share_capital |",
        "| F002V / F024N / F028N / F003N | raw_record_json only |",
        "",
        "## 3. 结果",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| samples | **{len(rows)}** |",
        f"| mapped | **{mapped_n}** |",
        f"| fixtures written | **{fixture_count}** |",
        "",
        "## 4. 逐条映射",
        "",
    ]
    for r in rows:
        lines.append(
            f"- `{r['company_code']}` {r['vary_date']}: **{r['map_status']}** "
            f"(mapped={r['mapped_fields_count']})"
        )
    lines.extend([
        "",
        "## 5. 质量边界",
        "",
        "- FxxxN 单位 candidate-level；行可能为定期报告或股本变动事件。",
        "- `source_status=testing`；**无 verified**。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_c_class_share_capital_profile_mapper_report.csv]"
        "(cninfo_c_class_share_capital_profile_mapper_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed C-class share_capital_profile fixtures")
    parser.add_argument("--output-fixtures", default=DEFAULT_FIXTURES)
    parser.add_argument("--output-mapper-csv", default=DEFAULT_MAPPER_CSV)
    parser.add_argument("--output-mapper-md", default=DEFAULT_MAPPER_MD)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records, report_rows = seed_fixtures()
    write_jsonl(args.output_fixtures, records)
    write_mapper_csv(args.output_mapper_csv, report_rows)
    write_mapper_md(args.output_mapper_md, report_rows, len(records))

    print(f"SUMMARY  fixtures={len(records)}  mapped={len(records)}  samples={len(report_rows)}")
    print(f"JSONL {args.output_fixtures}")
    print(f"CSV   {args.output_mapper_csv}")
    print(f"MD    {args.output_mapper_md}")


if __name__ == "__main__":
    main()
