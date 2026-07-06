"""
Seed C-class security_profile fixtures from embedded marketOverview samples.

Uses lab/cninfo_c_class_mappers.py — no CNINFO network requests.

Usage:
    python lab/seed_cninfo_c_class_security_profile_fixtures.py
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
    DEFAULT_SECURITY_SOURCE_ID,
    compute_raw_record_hash,
    count_mapped_security_profile_fields,
    map_company_security_profile,
)

DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "c_class", "security_profile", "security_profile_fixtures.jsonl"
)
DEFAULT_MAPPER_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_security_profile_mapper_report.csv"
)
DEFAULT_MAPPER_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_security_profile_mapper_summary.md"
)

# Embedded marketOverview root samples (mapper draft fixtures; not full live response dumps).
EMBEDDED_SAMPLES: List[Dict[str, Any]] = [
    {
        "company_code": "600000",
        "company_name": "浦发银行",
        "raw_record": {
            "secCode": "600000",
            "secName": "浦发银行",
            "secType": "001001",
            "tradingStatus": "0",
            "age": "27.12",
            "finance": True,
            "delisted": False,
            "sshk": True,
            "szhk": False,
        },
    },
    {
        "company_code": "300001",
        "company_name": "特锐德",
        "raw_record": {
            "secCode": "300001",
            "secName": "特锐德",
            "secType": "001001",
            "tradingStatus": "0",
            "age": "16.69",
            "finance": True,
            "delisted": False,
            "sshk": False,
            "szhk": True,
        },
    },
    {
        "company_code": "688001",
        "company_name": "华兴源创",
        "raw_record": {
            "secCode": "688001",
            "secName": "华兴源创",
            "secType": "001001",
            "tradingStatus": "0",
            "age": "6.95",
            "finance": False,
            "delisted": False,
            "sshk": True,
            "szhk": False,
        },
    },
]

MAPPER_CSV_FIELDS = [
    "company_code",
    "company_name",
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
        raw = sample["raw_record"]
        raw_fields_count = len(raw)

        mapped = map_company_security_profile(
            raw,
            company_code=code,
            company_name=name,
            source_id=DEFAULT_SECURITY_SOURCE_ID,
            source_status="testing",
        )

        if mapped is None:
            report_rows.append({
                "company_code": code,
                "company_name": name,
                "map_status": "empty_but_valid",
                "raw_fields_count": str(raw_fields_count),
                "mapped_fields_count": "0",
                "raw_record_hash": compute_raw_record_hash(raw),
                "notes": "Empty marketOverview object; no fixture row written.",
            })
            continue

        mapped_records.append(mapped)
        report_rows.append({
            "company_code": code,
            "company_name": name,
            "map_status": "mapped",
            "raw_fields_count": str(raw_fields_count),
            "mapped_fields_count": str(count_mapped_security_profile_fields(mapped)),
            "raw_record_hash": mapped["raw_record_hash"],
            "notes": "Embedded marketOverview sample; mapper draft fixture only; not verified.",
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
        "# CNINFO C 类 Security Profile Mapper Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## 1. 目的",
        "",
        "将 `marketOverview` 根对象映射为 `c_company_security_profile` fixture。"
        "**无网络请求**；**不写 verified**。",
        "",
        "## 2. 输入",
        "",
        "- 脚本：`lab/seed_cninfo_c_class_security_profile_fixtures.py`",
        "- Mapper：`lab/cninfo_c_class_mappers.py` → `map_company_security_profile()`",
        "- 样本：内置 **600000**、**300001**、**688001** marketOverview raw（3 条）",
        "",
        "## 3. 结果",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| samples | **{len(rows)}** |",
        f"| mapped | **{mapped_n}** |",
        f"| fixtures written | **{fixture_count}** |",
        "",
        "## 4. 字段映射",
        "",
        "| raw (marketOverview) | schema 字段 |",
        "|----------------------|-------------|",
        "| secCode | company_code, security_code |",
        "| secName | company_name, stock_short_name |",
        "| secType | security_type_code |",
        "| tradingStatus | trading_status_code |",
        "| age | listing_age_years_candidate |",
        "| finance | is_finance_related_candidate |",
        "| delisted | is_delisted |",
        "| sshk | shanghai_hong_kong_connect_candidate |",
        "| szhk | shenzhen_hong_kong_connect_candidate |",
        "",
        "未映射 YAML expected_fields（listed_board、listing_date 等）保留在 raw_record_json。",
        "",
        "## 5. 逐条映射",
        "",
    ]
    for r in rows:
        lines.append(
            f"- `{r['company_code']}` {r['company_name']}: **{r['map_status']}** "
            f"(raw_fields={r['raw_fields_count']}, mapped={r['mapped_fields_count']})"
        )
    lines.extend([
        "",
        "## 6. 质量边界",
        "",
        "- Mapper draft；secType / tradingStatus / sshk / szhk 语义 candidate-level。",
        "- `source_status=testing`；**无 verified**。",
        "- 不入库；不保存完整 live response body。",
        "- `exchange` 由 company_code 前缀推断（candidate）。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_c_class_security_profile_mapper_report.csv]"
        "(cninfo_c_class_security_profile_mapper_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed C-class security_profile fixtures")
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
