"""
Seed C-class basic_profile fixtures from embedded getCompanyIntroduction samples.

Uses lab/cninfo_c_class_mappers.py — no CNINFO network requests.

Usage:
    python lab/seed_cninfo_c_class_basic_profile_fixtures.py
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
    DEFAULT_BASIC_SOURCE_ID,
    compute_raw_record_hash,
    count_mapped_standard_fields,
    map_company_basic_profile,
)

DEFAULT_FIXTURES = os.path.join(
    BASE_DIR, "fixtures", "c_class", "basic_profile", "basic_profile_fixtures.jsonl"
)
DEFAULT_MAPPER_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_basic_profile_mapper_report.csv"
)
DEFAULT_MAPPER_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_c_class_basic_profile_mapper_summary.md"
)

# Simplified non-empty samples (mapper draft fixtures; not full live response dumps).
EMBEDDED_SAMPLES: List[Dict[str, Any]] = [
    {
        "company_code": "300001",
        "company_name": "特锐德",
        "org_id": "9900008270",
        "raw_record": {
            "basicInformation": [
                {
                    "ASECCODE": "300001",
                    "ASECNAME": "特锐德",
                    "ORGNAME": "青岛特锐德电气股份有限公司",
                    "F001V": "TGOOD Electric Co., Ltd.",
                    "F003V": "于德翔",
                    "F004V": "山东省青岛市崂山区松岭路336号",
                    "F005V": "山东省青岛市崂山区松岭路336号",
                    "F006D": "2009-10-30",
                    "F006V": "266104",
                    "F007N": "1055390000",
                    "F010D": "2004-03-09",
                    "F011V": "http://www.tgood.cn",
                    "F012V": "investor@tgood.cn",
                    "F013V": "0532-88938628",
                    "F014V": "0532-88938628",
                    "F015V": "电动汽车充电设备、箱式变电站等",
                    "F016V": "电动汽车充电设备、箱式变电站研发制造销售",
                    "F017V": "公司专注于电动汽车充电领域。",
                    "F018V": "王军",
                    "F032V": "电气机械和器材制造业",
                    "MARKET": "深交所创业板",
                    "F044V": "创业板",
                }
            ],
            "listingInformation": [
                {
                    "SECCODE": "300001",
                    "F007N": "1",
                    "F028N": "3360",
                    "F008N": "23.80",
                    "F047V": "中信证券股份有限公司",
                }
            ],
        },
    },
    {
        "company_code": "688001",
        "company_name": "华兴源创",
        "org_id": "9900038969",
        "raw_record": {
            "basicInformation": [
                {
                    "ASECCODE": "688001",
                    "ASECNAME": "华兴源创",
                    "ORGNAME": "苏州华兴源创科技股份有限公司",
                    "F001V": "Suzhou HYC Technology Co., Ltd.",
                    "F003V": "陈文源",
                    "F004V": "苏州工业园区青丘街8号",
                    "F005V": "苏州工业园区青丘街8号",
                    "F006D": "2019-07-22",
                    "F007N": "441984000",
                    "F010D": "2005-06-24",
                    "F011V": "http://www.hyc.cn",
                    "F015V": "检测设备、自动化设备",
                    "F016V": "工业自动控制系统装置制造",
                    "F017V": "公司主要从事检测设备研发制造。",
                    "F032V": "专用设备制造业",
                    "MARKET": "上交所科创板",
                    "F044V": "科创板",
                }
            ],
            "listingInformation": [
                {
                    "SECCODE": "688001",
                    "F028N": "4010",
                    "F008N": "24.26",
                    "F047V": "华泰联合证券有限责任公司",
                }
            ],
        },
    },
]

MAPPER_CSV_FIELDS = [
    "company_code",
    "company_name",
    "map_status",
    "raw_basic_fields_count",
    "raw_listing_fields_count",
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
        basic_list = raw.get("basicInformation") or []
        listing_list = raw.get("listingInformation") or []
        basic_n = len(basic_list[0]) if basic_list and isinstance(basic_list[0], dict) else 0
        listing_n = len(listing_list[0]) if listing_list and isinstance(listing_list[0], dict) else 0

        mapped = map_company_basic_profile(
            raw,
            company_code=code,
            company_name=name,
            source_id=DEFAULT_BASIC_SOURCE_ID,
            source_status="testing",
            org_id=org_id,
        )

        if mapped is None:
            report_rows.append({
                "company_code": code,
                "company_name": name,
                "map_status": "empty_but_valid",
                "raw_basic_fields_count": str(basic_n),
                "raw_listing_fields_count": str(listing_n),
                "mapped_fields_count": "0",
                "raw_record_hash": compute_raw_record_hash(raw),
                "notes": "Both sections empty; no fixture row written.",
            })
            continue

        mapped_records.append(mapped)
        report_rows.append({
            "company_code": code,
            "company_name": name,
            "map_status": "mapped",
            "raw_basic_fields_count": str(basic_n),
            "raw_listing_fields_count": str(listing_n),
            "mapped_fields_count": str(count_mapped_standard_fields(mapped)),
            "raw_record_hash": mapped["raw_record_hash"],
            "notes": "Embedded simplified sample; mapper draft fixture only; not verified.",
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
        "# CNINFO C 类 Basic Profile Mapper Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "## 1. 目的",
        "",
        "将 `getCompanyIntroduction` 的 basicInformation/listingInformation "
        "映射为 `c_company_basic_profile` fixture。**无网络请求**；**不写 verified**。",
        "",
        "## 2. 输入",
        "",
        "- 脚本：`lab/seed_cninfo_c_class_basic_profile_fixtures.py`",
        "- Mapper：`lab/cninfo_c_class_mappers.py`",
        "- 样本：内置 **300001**、**688001** 简化 raw_record（2 条非空）",
        "",
        "## 3. 结果",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| samples | **{len(rows)}** |",
        f"| mapped | **{mapped_n}** |",
        f"| fixtures written | **{fixture_count}** |",
        "",
        "**说明：** 600000 无保存的完整 raw body，本轮 fixture 仅用 2 家非空样本。",
        "",
        "## 4. 逐条映射",
        "",
    ]
    for r in rows:
        lines.append(
            f"- `{r['company_code']}` {r['company_name']}: **{r['map_status']}** "
            f"(basic_fields={r['raw_basic_fields_count']}, "
            f"listing_fields={r['raw_listing_fields_count']}, "
            f"mapped={r['mapped_fields_count']})"
        )
    lines.extend([
        "",
        "## 5. 质量边界",
        "",
        "- Mapper draft；字段语义 candidate-level。",
        "- `source_status=testing`；**无 verified**。",
        "- 不入库；不保存完整 live response body。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_c_class_basic_profile_mapper_report.csv]"
        "(cninfo_c_class_basic_profile_mapper_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed C-class basic_profile fixtures")
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
