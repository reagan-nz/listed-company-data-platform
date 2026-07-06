"""
Seed C-class executive_profile fixtures from embedded getCompanyExecutives row samples.

Uses lab/cninfo_c_class_mappers.py — no CNINFO network requests.

Usage:
    python lab/seed_cninfo_c_class_executive_profile_fixtures.py
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
    DEFAULT_EXECUTIVE_SOURCE_ID,
    compute_raw_record_hash,
    count_mapped_executive_profile_fields,
    map_company_executive_profile,
)

DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "c_class", "executive_profile", "executive_profile_fixtures.jsonl"
)
DEFAULT_MAPPER_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_executive_profile_mapper_report.csv"
)
DEFAULT_MAPPER_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_executive_profile_mapper_summary.md"
)

# Embedded single-row samples from P2-A probe / live validation observations.
EMBEDDED_SAMPLES: List[Dict[str, Any]] = [
    {
        "company_code": "600000",
        "company_name": "浦发银行",
        "org_id": "gssh0600000",
        "raw_record": {
            "F002V": "张为忠",
            "F010V": "男",
            "F012V": "1967",
            "F017V": "硕士研究生",
            "F009V": "董事长,党委书记",
            "F005N": None,
            "F012N": 90.95,
            "SEQID": 15891431386,
            "F001V": "D231120024",
        },
    },
    {
        "company_code": "600000",
        "company_name": "浦发银行",
        "org_id": "gssh0600000",
        "raw_record": {
            "F002V": "谢伟",
            "F010V": "男",
            "F012V": "1971",
            "F017V": "硕士研究生",
            "F009V": "副董事长,行长,党委副书记",
            "F005N": 217000,
            "F012N": 104.0,
            "SEQID": 15891431387,
            "F001V": "D231120025",
        },
    },
    {
        "company_code": "300001",
        "company_name": "特锐德",
        "org_id": "9900008270",
        "raw_record": {
            "F002V": "于德翔",
            "F010V": "男",
            "F012V": "1965",
            "F017V": "博士研究生",
            "F009V": "董事长",
            "F005N": 13119434,
            "F012N": 211.61,
            "SEQID": 15890001001,
            "F001V": "D230010001",
        },
    },
    {
        "company_code": "300001",
        "company_name": "特锐德",
        "org_id": "9900008270",
        "raw_record": {
            "F002V": "康晓兵",
            "F010V": "男",
            "F012V": "1974",
            "F017V": "EMBA",
            "F009V": "副董事长",
            "F005N": 0,
            "F012N": 182.07,
            "SEQID": 15890001002,
            "F001V": "D230010002",
        },
    },
    {
        "company_code": "688001",
        "company_name": "华兴源创",
        "org_id": "9900038969",
        "raw_record": {
            "F002V": "陈文源",
            "F010V": "男",
            "F012V": "1968",
            "F017V": None,
            "F009V": "董事长,总经理",
            "F005N": 57404033,
            "F012N": 202.51,
            "SEQID": 15890389001,
            "F001V": "D238890001",
        },
    },
    {
        "company_code": "688001",
        "company_name": "华兴源创",
        "org_id": "9900038969",
        "raw_record": {
            "F002V": "钱晓斌",
            "F010V": "男",
            "F012V": "1979",
            "F017V": None,
            "F009V": "董事,副总经理",
            "F005N": 0,
            "F012N": 140.24,
            "SEQID": 15890389002,
            "F001V": "D238890002",
        },
    },
]

MAPPER_CSV_FIELDS = [
    "company_code",
    "company_name",
    "executive_name",
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
        executive_name = str(raw.get("F002V") or "")

        mapped = map_company_executive_profile(
            raw,
            company_code=code,
            company_name=name,
            source_id=DEFAULT_EXECUTIVE_SOURCE_ID,
            source_status="testing",
            org_id=org_id,
        )

        if mapped is None:
            report_rows.append({
                "company_code": code,
                "company_name": name,
                "executive_name": executive_name,
                "map_status": "skipped_empty",
                "raw_fields_count": str(raw_fields_count),
                "mapped_fields_count": "0",
                "raw_record_hash": compute_raw_record_hash(raw),
                "notes": "Missing F002V or F009V; no fixture row written.",
            })
            continue

        mapped_records.append(mapped)
        report_rows.append({
            "company_code": code,
            "company_name": name,
            "executive_name": mapped["person_name"],
            "map_status": "mapped",
            "raw_fields_count": str(raw_fields_count),
            "mapped_fields_count": str(count_mapped_executive_profile_fields(mapped)),
            "raw_record_hash": mapped["raw_record_hash"],
            "notes": "Embedded getCompanyExecutives row; mapper draft fixture only; not verified.",
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
        "# CNINFO C 类 Executive Profile Mapper Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## 1. 目的",
        "",
        "将 `getCompanyExecutives` 单行 `data.records[]` 映射为 `c_executive_profile` fixture。",
        "**无网络请求**；**不写 verified**。",
        "",
        "## 2. 输入",
        "",
        "- 脚本：`lab/seed_cninfo_c_class_executive_profile_fixtures.py`",
        "- Mapper：`lab/cninfo_c_class_mappers.py` → `map_company_executive_profile()`",
        "- 样本：内置 **6** 条 executive row（600000×2 · 300001×2 · 688001×2）",
        "",
        "## 3. 字段映射",
        "",
        "| raw | schema |",
        "|-----|--------|",
        "| F002V | person_name |",
        "| F009V | position |",
        "| F010V | gender_candidate |",
        "| F012V | birth_year_candidate |",
        "| F017V | education_candidate |",
        "| F005N / F012N / SEQID / F001V | raw_record_json only |",
        "",
        "## 4. 结果",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| samples | **{len(rows)}** |",
        f"| mapped | **{mapped_n}** |",
        f"| fixtures written | **{fixture_count}** |",
        "",
        "## 5. 逐条映射",
        "",
    ]
    for r in rows:
        lines.append(
            f"- `{r['company_code']}` {r['executive_name']}: **{r['map_status']}** "
            f"(raw_fields={r['raw_fields_count']}, mapped={r['mapped_fields_count']})"
        )
    lines.extend([
        "",
        "## 6. 质量边界",
        "",
        "- Mapper draft；F005N/F012N 单位 candidate-level。",
        "- `source_status=testing`；**无 verified**。",
        "- 不入库；不保存完整 live response body。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_c_class_executive_profile_mapper_report.csv]"
        "(cninfo_c_class_executive_profile_mapper_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed C-class executive_profile fixtures")
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
