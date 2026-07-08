#!/usr/bin/env python3
"""
CNINFO C-class company_basic_profile 离线 re-map（Era C Phase 4）。

仅读取 raw/basic_profile，重写 normalized/company_basic_profile。
不请求 CNINFO · 不修改 raw · 不重跑 harvest live。

Usage:
    python lab/remap_cninfo_c_class_basic_profile_offline.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_mappers import map_company_basic_profile  # noqa: E402
from harvest_cninfo_c_class import (  # noqa: E402
    BASE_DIR,
    HARVEST_OUTPUT_ROOT,
    SOURCE_HARVEST_META,
)

RAW_BASIC_REL = f"{HARVEST_OUTPUT_ROOT}/raw/basic_profile"
NORM_BASIC_REL = f"{HARVEST_OUTPUT_ROOT}/normalized/company_basic_profile"
SUMMARY_REL = "outputs/validation/cninfo_c_class_establishment_date_remap_summary.md"
REPORT_REL = "outputs/validation/cninfo_c_class_establishment_date_remap_report.csv"

REPORT_FIELDS = [
    "company_code",
    "company_name",
    "raw_file",
    "normalized_file",
    "before_establishment_date",
    "after_establishment_date",
    "establishment_date_parse_status",
    "file_changed",
    "mapper_returned_none",
]


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def _establishment_signature(record: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not record:
        return {}
    keys = (
        "establishment_date",
        "establishment_date_parse_status",
        "establishment_date_field_quality",
    )
    return {k: record.get(k) for k in keys if k in record}


def _load_before_norm(norm_path: str) -> Optional[Dict[str, Any]]:
    if not os.path.isfile(norm_path):
        return None
    return _load_json(norm_path)


def _remap_company(raw_path: str, norm_path: str, source_status: str) -> Dict[str, Any]:
    before = _load_before_norm(norm_path)
    wrapper = _load_json(raw_path)
    company_code = str(wrapper.get("company_code") or os.path.basename(raw_path).split(".")[0])
    company_name = wrapper.get("company_name") or ""
    org_id = wrapper.get("org_id")
    raw_records = wrapper.get("raw_records")
    if not isinstance(raw_records, dict):
        raw_records = {}

    mapped = map_company_basic_profile(
        raw_records,
        company_code,
        company_name,
        source_status=source_status,
        org_id=org_id,
    )
    mapper_none = mapped is None
    if mapped is None:
        mapped = {
            "company_code": company_code,
            "company_name": company_name,
            "source_id": "cninfo_company_basic_profile",
            "source_status": source_status,
            "record_count": 0,
        }
        if before and before.get("retrieval_status"):
            mapped["retrieval_status"] = before["retrieval_status"]
    else:
        if before and before.get("retrieval_status") and "retrieval_status" not in mapped:
            mapped["retrieval_status"] = before["retrieval_status"]

    _write_json(norm_path, mapped)

    before_sig = _establishment_signature(before)
    after_sig = _establishment_signature(mapped)
    file_changed = before_sig != after_sig

    parse_status = mapped.get("establishment_date_parse_status", "")
    if not parse_status and not mapper_none:
        parse_status = "not_present"

    return {
        "company_code": company_code,
        "company_name": company_name,
        "raw_file": os.path.relpath(raw_path, BASE_DIR),
        "normalized_file": os.path.relpath(norm_path, BASE_DIR),
        "before_establishment_date": before.get("establishment_date") if before else "",
        "after_establishment_date": mapped.get("establishment_date"),
        "establishment_date_parse_status": parse_status,
        "file_changed": "yes" if file_changed else "no",
        "mapper_returned_none": "yes" if mapper_none else "no",
    }


def run_remap(
    *,
    raw_dir: Optional[str] = None,
    norm_dir: Optional[str] = None,
    summary_path: Optional[str] = None,
    report_path: Optional[str] = None,
) -> Dict[str, Any]:
    raw_dir = raw_dir or _abs(RAW_BASIC_REL)
    norm_dir = norm_dir or _abs(NORM_BASIC_REL)
    summary_path = summary_path or _abs(SUMMARY_REL)
    report_path = report_path or _abs(REPORT_REL)

    source_status = SOURCE_HARVEST_META["cninfo_company_basic_profile"]["source_status"]
    raw_files = sorted(f for f in os.listdir(raw_dir) if f.endswith(".json"))

    report_rows: List[Dict[str, Any]] = []
    for name in raw_files:
        raw_path = os.path.join(raw_dir, name)
        code = name.rsplit(".", 1)[0]
        norm_path = os.path.join(norm_dir, f"{code}.json")
        report_rows.append(_remap_company(raw_path, norm_path, source_status))

    parse_counter = Counter(r["establishment_date_parse_status"] for r in report_rows)
    present_count = parse_counter.get("parsed", 0)
    null_count = parse_counter.get("null_but_valid", 0)
    invalid_count = parse_counter.get("needs_review", 0)
    not_present_count = parse_counter.get("not_present", 0)

    stats = {
        "input_raw_basic_files": len(raw_files),
        "output_normalized_basic_files": len(raw_files),
        "establishment_date_present_count": present_count,
        "establishment_date_null_count": null_count,
        "establishment_date_invalid_count": invalid_count,
        "establishment_date_not_present_count": not_present_count,
        "changed_files_count": sum(1 for r in report_rows if r["file_changed"] == "yes"),
        "cninfo_requests": 0,
        "parse_status_breakdown": dict(parse_counter),
    }

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        for row in report_rows:
            writer.writerow({k: row[k] for k in REPORT_FIELDS})

    _write_summary_md(summary_path, stats, report_rows)
    return stats


def _write_summary_md(
    path: str,
    stats: Dict[str, Any],
    report_rows: List[Dict[str, Any]],
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# CNINFO C-Class establishment_date Offline Re-map Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 re-map：仅读 `raw/basic_profile` · 仅写 `normalized/company_basic_profile`。"
        "**无 CNINFO** · **无 live** · **raw 未修改**",
        "",
        "## Counts",
        "",
        "| metric | value |",
        "|--------|-------|",
        f"| input raw basic files | **{stats['input_raw_basic_files']}** |",
        f"| output normalized basic files | **{stats['output_normalized_basic_files']}** |",
        f"| establishment_date present (parsed) | **{stats['establishment_date_present_count']}** |",
        f"| establishment_date null | **{stats['establishment_date_null_count']}** |",
        f"| establishment_date invalid / nonstandard | **{stats['establishment_date_invalid_count']}** |",
        f"| establishment_date not present | **{stats['establishment_date_not_present_count']}** |",
        f"| changed files count | **{stats['changed_files_count']}** |",
        f"| CNINFO requests | **{stats['cninfo_requests']}** |",
        "",
        "## parse_status breakdown",
        "",
    ]
    for status, count in sorted(stats["parse_status_breakdown"].items()):
        lines.append(f"- `{status}`: **{count}**")

    invalid_rows = [
        r for r in report_rows if r["establishment_date_parse_status"] == "needs_review"
    ]
    lines.extend([
        "",
        "## invalid / nonstandard sample（前 20）",
        "",
        "| company_code | establishment_date |",
        "|--------------|-------------------|",
    ])
    for row in invalid_rows[:20]:
        lines.append(f"| {row['company_code']} | {row['after_establishment_date']} |")

    lines.extend([
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO",
        "- 未重跑 harvest live",
        "- raw 数据未修改",
        "- 未写 verified / 未入库 / MinIO / RAG",
        "",
        f"详见 [cninfo_c_class_establishment_date_remap_report.csv](cninfo_c_class_establishment_date_remap_report.csv)。",
    ])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="离线 re-map company_basic_profile（establishment_date patch）")
    parser.parse_args()
    stats = run_remap()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
