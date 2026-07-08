#!/usr/bin/env python3
"""
CNINFO C-class dividend_history 离线 re-map（Era C Phase 4）。

仅读取 raw/dividend_history，重写 normalized/dividend_history。
不请求 CNINFO · 不修改 raw · 不重跑 harvest live。

Usage:
    python lab/remap_cninfo_c_class_dividend_history_offline.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_mappers import (  # noqa: E402
    _aggregate_dividend_parse_status,
    map_dividend_history,
)
from harvest_cninfo_c_class import (  # noqa: E402
    BASE_DIR,
    HARVEST_OUTPUT_ROOT,
    SOURCE_HARVEST_META,
)

RAW_DIVIDEND_REL = f"{HARVEST_OUTPUT_ROOT}/raw/dividend_history"
NORM_DIVIDEND_REL = f"{HARVEST_OUTPUT_ROOT}/normalized/dividend_history"
SUMMARY_REL = "outputs/validation/cninfo_c_class_dividend_history_remap_summary.md"
REPORT_REL = "outputs/validation/cninfo_c_class_dividend_history_remap_report.csv"

PUBLIC_EVENT_FIELDS = (
    "dividend_year",
    "report_period",
    "record_date",
    "ex_dividend_date",
    "payment_date",
    "cash_dividend_per_share",
    "stock_dividend_ratio",
    "transfer_ratio",
    "dividend_method",
    "dividend_plan_text_raw",
    "dividend_parse_status",
)

REPORT_FIELDS = [
    "company_code",
    "company_name",
    "raw_file",
    "normalized_file",
    "event_count",
    "before_needs_review_events",
    "after_needs_review_events",
    "before_company_parse_status",
    "after_company_parse_status",
    "file_changed",
]


def _abs(rel: str) -> str:
    return os.path.join(BASE_DIR, rel)


def _load_raw_wrapper(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _load_normalized_events(path: str) -> List[Dict[str, Any]]:
    if not os.path.isfile(path):
        return []
    events: List[Dict[str, Any]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def _event_parse_signature(events: List[Dict[str, Any]]) -> List[Tuple[str, str, Any]]:
    sig: List[Tuple[str, str, Any]] = []
    for ev in events:
        sig.append((
            ev.get("report_period") or "",
            ev.get("dividend_plan_text_raw") or "",
            ev.get("dividend_parse_status"),
        ))
    return sig


def _count_event_statuses(events: List[Dict[str, Any]]) -> Counter:
    ctr: Counter = Counter()
    for ev in events:
        ctr[ev.get("dividend_parse_status", "unknown")] += 1
    return ctr


def _company_parse_status(events: List[Dict[str, Any]]) -> str:
    statuses = [ev.get("dividend_parse_status", "needs_review") for ev in events]
    return _aggregate_dividend_parse_status(statuses)


def _write_normalized_jsonl(path: str, events: List[Dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for ev in events:
            public = {k: ev.get(k) for k in PUBLIC_EVENT_FIELDS}
            fh.write(json.dumps(public, ensure_ascii=False) + "\n")


def _remap_company(
    raw_path: str,
    norm_path: str,
    source_status: str,
) -> Dict[str, Any]:
    before_events = _load_normalized_events(norm_path)
    wrapper = _load_raw_wrapper(raw_path)
    company_code = str(wrapper.get("company_code") or os.path.basename(raw_path).split(".")[0])
    company_name = wrapper.get("company_name") or ""
    raw_records = wrapper.get("raw_records")
    if not isinstance(raw_records, list):
        raw_records = []

    mapped = map_dividend_history(
        raw_records,
        company_code,
        company_name,
        source_status=source_status,
    )
    after_events = mapped.get("dividend_history") or []
    _write_normalized_jsonl(norm_path, after_events)

    before_sig = _event_parse_signature(before_events)
    after_sig = _event_parse_signature(after_events)
    file_changed = before_sig != after_sig or len(before_events) != len(after_events)

    return {
        "company_code": company_code,
        "company_name": company_name,
        "raw_file": os.path.relpath(raw_path, BASE_DIR),
        "normalized_file": os.path.relpath(norm_path, BASE_DIR),
        "event_count": len(after_events),
        "before_needs_review_events": sum(
            1 for ev in before_events if ev.get("dividend_parse_status") == "needs_review"
        ),
        "after_needs_review_events": sum(
            1 for ev in after_events if ev.get("dividend_parse_status") == "needs_review"
        ),
        "before_company_parse_status": _company_parse_status(before_events),
        "after_company_parse_status": mapped.get("dividend_parse_status", ""),
        "file_changed": "yes" if file_changed else "no",
        "before_event_status": _count_event_statuses(before_events),
        "after_event_status": _count_event_statuses(after_events),
    }


def _aggregate_status_counts(rows: List[Dict[str, Any]], key: str) -> Counter:
    total: Counter = Counter()
    for row in rows:
        for status, count in row[key].items():
            total[status] += count
    return total


def run_remap(
    *,
    raw_dir: Optional[str] = None,
    norm_dir: Optional[str] = None,
    summary_path: Optional[str] = None,
    report_path: Optional[str] = None,
) -> Dict[str, Any]:
    raw_dir = raw_dir or _abs(RAW_DIVIDEND_REL)
    norm_dir = norm_dir or _abs(NORM_DIVIDEND_REL)
    summary_path = summary_path or _abs(SUMMARY_REL)
    report_path = report_path or _abs(REPORT_REL)

    source_status = SOURCE_HARVEST_META["cninfo_dividend_financing_profile"]["source_status"]
    raw_files = sorted(
        f for f in os.listdir(raw_dir)
        if f.endswith(".jsonl") or f.endswith(".json")
    )

    report_rows: List[Dict[str, Any]] = []
    for name in raw_files:
        raw_path = os.path.join(raw_dir, name)
        code = name.rsplit(".", 1)[0]
        norm_path = os.path.join(norm_dir, f"{code}.jsonl")
        report_rows.append(_remap_company(raw_path, norm_path, source_status))

    before_events = _aggregate_status_counts(report_rows, "before_event_status")
    after_events = _aggregate_status_counts(report_rows, "after_event_status")

    before_company = Counter(r["before_company_parse_status"] for r in report_rows)
    after_company = Counter(r["after_company_parse_status"] for r in report_rows)

    stats = {
        "input_raw_files": len(raw_files),
        "output_normalized_files": len(raw_files),
        "before_needs_review_events": before_events.get("needs_review", 0),
        "after_needs_review_events": after_events.get("needs_review", 0),
        "before_parsed_events": before_events.get("parsed", 0),
        "after_parsed_events": after_events.get("parsed", 0),
        "before_partial_events": before_events.get("partial", 0),
        "after_partial_events": after_events.get("partial", 0),
        "empty_but_valid_companies": after_company.get("empty_but_valid", 0),
        "changed_files_count": sum(1 for r in report_rows if r["file_changed"] == "yes"),
        "before_company_parse": dict(before_company),
        "after_company_parse": dict(after_company),
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
        "# CNINFO C-Class dividend_history Offline Re-map Summary",
        "",
        f"_生成时间：{now}_",
        "",
        "> 离线 re-map：仅读 raw/dividend_history · 仅写 normalized/dividend_history。"
        "**无 CNINFO** · **无 live** · **raw 未修改**",
        "",
        "## Counts",
        "",
        f"| metric | value |",
        f"|--------|-------|",
        f"| input raw dividend files | **{stats['input_raw_files']}** |",
        f"| output normalized dividend files | **{stats['output_normalized_files']}** |",
        f"| before needs_review (events) | **{stats['before_needs_review_events']}** |",
        f"| after needs_review (events) | **{stats['after_needs_review_events']}** |",
        f"| parsed events before | **{stats['before_parsed_events']}** |",
        f"| parsed events after | **{stats['after_parsed_events']}** |",
        f"| partial events before | **{stats['before_partial_events']}** |",
        f"| partial events after | **{stats['after_partial_events']}** |",
        f"| empty_but_valid companies | **{stats['empty_but_valid_companies']}** |",
        f"| changed files count | **{stats['changed_files_count']}** |",
        "",
        "## Company-level parse status",
        "",
        "### before",
        "",
    ]
    for status, count in sorted(stats["before_company_parse"].items()):
        lines.append(f"- `{status}`: **{count}**")
    lines.extend(["", "### after", ""])
    for status, count in sorted(stats["after_company_parse"].items()):
        lines.append(f"- `{status}`: **{count}**")

    changed = [r for r in report_rows if r["file_changed"] == "yes"]
    lines.extend([
        "",
        "## Changed files sample（前 20）",
        "",
        "| company_code | before_nr | after_nr | before_company | after_company |",
        "|--------------|-----------|----------|----------------|---------------|",
    ])
    for row in changed[:20]:
        lines.append(
            f"| {row['company_code']} | {row['before_needs_review_events']} | "
            f"{row['after_needs_review_events']} | {row['before_company_parse_status']} | "
            f"{row['after_company_parse_status']} |",
        )

    lines.extend([
        "",
        "## 红线确认",
        "",
        "- 未请求 CNINFO",
        "- 未重跑 harvest live",
        "- raw 数据未修改",
        "- 未写 verified / 未入库 / MinIO / RAG",
        "",
        f"详见 [cninfo_c_class_dividend_history_remap_report.csv](cninfo_c_class_dividend_history_remap_report.csv)。",
        "",
    ])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description="dividend_history 离线 re-map")
    parser.add_argument("--summary", default=SUMMARY_REL)
    parser.add_argument("--report", default=REPORT_REL)
    args = parser.parse_args()

    stats = run_remap(
        summary_path=_abs(args.summary),
        report_path=_abs(args.report),
    )
    print("pre_dividend_remap: PASS")
    print(f"input_raw_files={stats['input_raw_files']}")
    print(f"needs_review_before={stats['before_needs_review_events']}")
    print(f"needs_review_after={stats['after_needs_review_events']}")
    print(f"parsed_before={stats['before_parsed_events']}")
    print(f"parsed_after={stats['after_parsed_events']}")
    print(f"changed_files={stats['changed_files_count']}")
    print(f"MD    {_abs(args.summary)}")
    print(f"CSV   {_abs(args.report)}")


if __name__ == "__main__":
    main()
