"""
Seed C-class shareholder_profile fixtures from embedded top-shareholder row samples.

Uses lab/cninfo_c_class_mappers.py — no CNINFO network requests.

Usage:
    python lab/seed_cninfo_c_class_shareholder_profile_fixtures.py
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
    DEFAULT_TOP_FLOAT_SHAREHOLDERS_SOURCE_ID,
    DEFAULT_TOP_SHAREHOLDERS_SOURCE_ID,
    SHAREHOLDER_SCOPE_TOP,
    SHAREHOLDER_SCOPE_TOP_FLOAT,
    compute_raw_record_hash,
    count_mapped_shareholder_profile_fields,
    map_company_shareholder_profile,
)

DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "c_class", "shareholder_profile", "shareholder_profile_fixtures.jsonl"
)
DEFAULT_MAPPER_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_shareholder_profile_mapper_report.csv"
)
DEFAULT_MAPPER_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_shareholder_profile_mapper_summary.md"
)

COMPANY_ROWS: Dict[str, Dict[str, Any]] = {
    "600000": {
        "company_name": "浦发银行",
        "org_id": "gssh0600000",
        "top_ten": [
            {
                "F001D": "2026-03-31",
                "F002V": "上海国际集团有限公司",
                "F003N": 708683.46,
                "F004N": 21.28,
                "F005N": 1,
                "F006V": "流通A股",
                "F007V": "未变",
            },
            {
                "F001D": "2026-03-31",
                "F002V": "中国移动通信集团广东有限公司",
                "F003N": 605349.55,
                "F004N": 18.18,
                "F005N": 2,
                "F006V": "流通A股",
                "F007V": "未变",
            },
        ],
        "top_ten_float": [
            {
                "F001D": "2026-03-31",
                "F002V": "上海国际集团有限公司",
                "F003N": 708683.46,
                "F004N": 21.28,
                "F005N": 1,
                "F006V": "流通A股",
                "F007V": "未变",
            },
            {
                "F001D": "2026-03-31",
                "F002V": "中国移动通信集团广东有限公司",
                "F003N": 605349.55,
                "F004N": 18.18,
                "F005N": 2,
                "F006V": "流通A股",
                "F007V": "未变",
            },
        ],
    },
    "300001": {
        "company_name": "特锐德",
        "org_id": "9900008270",
        "top_ten": [
            {
                "F001D": "2026-03-31",
                "F002V": "青岛德锐投资有限公司",
                "F003N": 33329.04,
                "F004N": 31.58,
                "F005N": 1,
                "F006V": "流通A股",
                "F007V": "未变",
            },
            {
                "F001D": "2026-03-31",
                "F002V": "香港中央结算有限公司",
                "F003N": 3035.93,
                "F004N": 2.88,
                "F005N": 2,
                "F006V": "流通A股",
                "F007V": "未变",
            },
        ],
        "top_ten_float": [
            {
                "F001D": "2026-03-31",
                "F002V": "青岛德锐投资有限公司",
                "F003N": 33329.04,
                "F004N": 31.58,
                "F005N": 1,
                "F006V": "流通A股",
                "F007V": "未变",
            },
            {
                "F001D": "2026-03-31",
                "F002V": "香港中央结算有限公司",
                "F003N": 3035.93,
                "F004N": 2.88,
                "F005N": 2,
                "F006V": "流通A股",
                "F007V": "未变",
            },
        ],
    },
    "688001": {
        "company_name": "华兴源创",
        "org_id": "9900038969",
        "top_ten": [
            {
                "F001D": "2026-03-31",
                "F002V": "苏州源华创兴投资管理有限公司",
                "F003N": 23097.6,
                "F004N": 51.96,
                "F005N": 1,
                "F006V": "流通A股",
                "F007V": "0.100",
            },
            {
                "F001D": "2026-03-31",
                "F002V": "陈文源",
                "F003N": 5740.4,
                "F004N": 12.91,
                "F005N": 2,
                "F006V": "流通A股",
                "F007V": "未变",
            },
        ],
        "top_ten_float": [
            {
                "F001D": "2026-03-31",
                "F002V": "苏州源华创兴投资管理有限公司",
                "F003N": 23097.6,
                "F004N": 51.96,
                "F005N": 1,
                "F006V": "流通A股",
                "F007V": "0.103",
            },
            {
                "F001D": "2026-03-31",
                "F002V": "陈文源",
                "F003N": 5740.4,
                "F004N": 12.92,
                "F005N": 2,
                "F006V": "流通A股",
                "F007V": "未变",
            },
        ],
    },
}

SCOPE_CONFIG = [
    ("top_ten", SHAREHOLDER_SCOPE_TOP, DEFAULT_TOP_SHAREHOLDERS_SOURCE_ID),
    ("top_ten_float", SHAREHOLDER_SCOPE_TOP_FLOAT, DEFAULT_TOP_FLOAT_SHAREHOLDERS_SOURCE_ID),
]

MAPPER_CSV_FIELDS = [
    "company_code",
    "company_name",
    "source_id",
    "shareholder_scope",
    "report_date",
    "rank",
    "shareholder_name",
    "map_status",
    "raw_fields_count",
    "mapped_fields_count",
    "raw_record_hash",
    "notes",
]


def build_embedded_samples() -> List[Dict[str, Any]]:
    samples: List[Dict[str, Any]] = []
    for company_code, meta in COMPANY_ROWS.items():
        for scope_key, shareholder_scope, source_id in SCOPE_CONFIG:
            for raw in meta[scope_key]:
                samples.append({
                    "company_code": company_code,
                    "company_name": meta["company_name"],
                    "org_id": meta["org_id"],
                    "source_id": source_id,
                    "shareholder_scope": shareholder_scope,
                    "raw_record": raw,
                })
    return samples


EMBEDDED_SAMPLES = build_embedded_samples()


def seed_fixtures() -> tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    mapped_records: List[Dict[str, Any]] = []
    report_rows: List[Dict[str, str]] = []

    for sample in EMBEDDED_SAMPLES:
        code = sample["company_code"]
        name = sample["company_name"]
        org_id = sample.get("org_id")
        source_id = sample["source_id"]
        shareholder_scope = sample["shareholder_scope"]
        raw = sample["raw_record"]
        raw_fields_count = len(raw)
        report_date = str(raw.get("F001D") or "")
        rank = str(raw.get("F005N") or "")
        shareholder_name = str(raw.get("F002V") or "")

        mapped = map_company_shareholder_profile(
            raw,
            company_code=code,
            company_name=name,
            source_id=source_id,
            source_status="testing",
            shareholder_scope=shareholder_scope,
            org_id=org_id,
        )

        if mapped is None:
            report_rows.append({
                "company_code": code,
                "company_name": name,
                "source_id": source_id,
                "shareholder_scope": shareholder_scope,
                "report_date": report_date,
                "rank": rank,
                "shareholder_name": shareholder_name,
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
            "source_id": source_id,
            "shareholder_scope": shareholder_scope,
            "report_date": report_date,
            "rank": rank,
            "shareholder_name": shareholder_name,
            "map_status": "mapped",
            "raw_fields_count": str(raw_fields_count),
            "mapped_fields_count": str(count_mapped_shareholder_profile_fields(mapped)),
            "raw_record_hash": mapped["raw_record_hash"],
            "notes": "Embedded top-shareholder row; mapper draft fixture only; not verified.",
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
    top_n = sum(1 for r in rows if r["shareholder_scope"] == SHAREHOLDER_SCOPE_TOP)
    float_n = sum(1 for r in rows if r["shareholder_scope"] == SHAREHOLDER_SCOPE_TOP_FLOAT)
    lines = [
        "# CNINFO C 类 Shareholder Profile Mapper Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## 1. 目的",
        "",
        "将 `getTopTenStockholders` / `getTopTenCirculatingStockholders` 单行 `data.records[]`",
        "映射为 `c_shareholder_profile` fixture。**无网络请求**；**不写 verified**。",
        "",
        "## 2. 字段映射",
        "",
        "| raw | schema |",
        "|-----|--------|",
        "| F001D | report_period |",
        "| F002V | shareholder_name |",
        "| F003N | holding_shares |",
        "| F004N | holding_ratio |",
        "| F005N | rank |",
        "| F006V | shareholder_type_candidate |",
        "| F007V | raw_record_json only |",
        "",
        "**shareholder_scope：** `top_shareholder`（cninfo_top_shareholders_profile）·",
        "`top_float_shareholder`（cninfo_top_float_shareholders_profile）",
        "",
        "## 3. 结果",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| samples | **{len(rows)}** |",
        f"| mapped | **{mapped_n}** |",
        f"| top_shareholder | **{top_n}** |",
        f"| top_float_shareholder | **{float_n}** |",
        f"| fixtures written | **{fixture_count}** |",
        "",
        "## 4. 逐条映射",
        "",
    ]
    for r in rows:
        lines.append(
            f"- `{r['company_code']}` {r['shareholder_scope']} rank={r['rank']} "
            f"{r['shareholder_name']}: **{r['map_status']}** (mapped={r['mapped_fields_count']})"
        )
    lines.extend([
        "",
        "## 5. 质量边界",
        "",
        "- F003N 单位 candidate-level；响应常含多期 × 10 股东。",
        "- `source_status=testing`；**无 verified**。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_c_class_shareholder_profile_mapper_report.csv]"
        "(cninfo_c_class_shareholder_profile_mapper_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed C-class shareholder_profile fixtures")
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
