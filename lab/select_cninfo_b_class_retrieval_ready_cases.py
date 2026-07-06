"""
Select CNINFO B-class retrieval validation ready cases (offline).

Reads known-document and category-sample YAML fixtures, validates ready-case
required fields, writes selection report. Does NOT request CNINFO.

Usage:
    python lab/select_cninfo_b_class_retrieval_ready_cases.py
    python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_KNOWN = os.path.join(
    BASE_DIR, "fixtures", "b_class", "retrieval_validation", "known_document_retrieval_cases.yaml"
)
DEFAULT_CATEGORY = os.path.join(
    BASE_DIR, "fixtures", "b_class", "retrieval_validation", "category_sample_cases.yaml"
)
DEFAULT_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_retrieval_ready_case_report.csv"
)
DEFAULT_MD = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_retrieval_ready_case_summary.md"
)

VALID_CASE_STATUS = frozenset({"placeholder", "ready", "retired"})

KNOWN_READY_REQUIRED = [
    "case_id",
    "case_status",
    "source_id",
    "company_code",
    "company_name",
    "title_pattern",
    "expected_document_type",
    "date_start",
    "date_end",
    "expected_route_to",
    "expected_pdf_url_available",
]

CATEGORY_READY_REQUIRED = [
    "case_id",
    "case_status",
    "source_id",
    "source_category",
    "title_pattern",
    "date_start",
    "date_end",
    "expected_min_results",
    "expected_document_types",
]


def _load_cases(path: str) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return list(data.get("cases") or [])


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    return False


def _check_known_ready(case: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    for field in KNOWN_READY_REQUIRED:
        if field not in case or _is_empty(case.get(field)):
            missing.append(field)
    if case.get("expected_pdf_url_available") is None:
        if "expected_pdf_url_available" not in missing:
            missing.append("expected_pdf_url_available")
    return missing


def _check_category_ready(case: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    for field in CATEGORY_READY_REQUIRED:
        if field not in case or _is_empty(case.get(field)):
            missing.append(field)
    return missing


def _resolve_ready_status(
    case: Dict[str, Any],
    case_type: str,
) -> Tuple[str, List[str]]:
    status = (case.get("case_status") or "placeholder").strip()
    if status not in VALID_CASE_STATUS:
        return "invalid_ready", ["case_status"]

    if status == "placeholder":
        return "placeholder", []
    if status == "retired":
        return "retired", []

    if status == "ready":
        if case_type == "known_document":
            missing = _check_known_ready(case)
        else:
            missing = _check_category_ready(case)
        if missing:
            return "invalid_ready", missing
        return "ready", []

    return "invalid_ready", ["case_status"]


def process_cases(
    cases: List[Dict[str, Any]],
    case_type: str,
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for case in cases:
        case_id = str(case.get("case_id", ""))
        ready_status, missing = _resolve_ready_status(case, case_type)
        rows.append({
            "case_id": case_id,
            "case_type": case_type,
            "case_status": str(case.get("case_status", "placeholder")),
            "source_id": str(case.get("source_id", "")),
            "ready_status": ready_status,
            "missing_fields": ",".join(missing) if missing else "",
            "notes": str(case.get("notes", ""))[:200],
        })
    return rows


def write_csv(path: str, rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = [
        "case_id", "case_type", "case_status", "source_id",
        "ready_status", "missing_fields", "notes",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary_md(
    path: str,
    rows: List[Dict[str, str]],
    known_path: str,
    category_path: str,
    result: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    total = len(rows)
    placeholder = sum(1 for r in rows if r["ready_status"] == "placeholder")
    ready = sum(1 for r in rows if r["ready_status"] == "ready")
    retired = sum(1 for r in rows if r["ready_status"] == "retired")
    invalid = sum(1 for r in rows if r["ready_status"] == "invalid_ready")
    ready_rows = [r for r in rows if r["ready_status"] == "ready"]
    invalid_rows = [r for r in rows if r["ready_status"] == "invalid_ready"]

    lines = [
        "# CNINFO B 类 Retrieval Ready Case Summary",
        "",
        f"_生成时间：{now}（ready-case selector；不请求 CNINFO）_",
        "",
        "## 1. 目的",
        "",
        "筛选 `case_status: ready` 且字段完备的 retrieval validation case。",
        "**不是** live retrieval validation；不下载 PDF；不写 verified。",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| Known-document cases | `{os.path.relpath(known_path, BASE_DIR)}` |",
        f"| Category-sample cases | `{os.path.relpath(category_path, BASE_DIR)}` |",
        f"| 规则 | `plans/cninfo_b_class_retrieval_ready_case_rules.md` |",
        f"| 脚本 | `lab/select_cninfo_b_class_retrieval_ready_cases.py` |",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_cases | **{total}** |",
        f"| placeholder | **{placeholder}** |",
        f"| ready | **{ready}** |",
        f"| retired | **{retired}** |",
        f"| invalid_ready | **{invalid}** |",
        f"| result | **{result}** |",
        "",
        "## 4. Ready case 明细",
        "",
    ]
    if ready_rows:
        for r in ready_rows:
            lines.append(f"- `{r['case_id']}` ({r['case_type']}) → `{r['source_id']}`")
    else:
        lines.append("_当前 **没有** live-ready case（ready=0）。所有 case 仍为 `placeholder`。**")

    lines.extend(["", "## 5. Invalid ready 明细", ""])
    if invalid_rows:
        for r in invalid_rows:
            lines.append(
                f"- `{r['case_id']}`: missing `{r['missing_fields']}`"
            )
    else:
        lines.append("_无 invalid_ready case。_")

    lines.extend([
        "",
        "## 6. 质量边界",
        "",
        "- Ready-case selector **不是** retrieval validation。",
        "- **不代表** CNINFO coverage%。",
        "- **不下载** PDF；**不写 verified**。",
        "- 未来 live 脚本 **只** 应对 `ready_status=ready` 的 case 发起请求。",
        "",
        "## 7. 下一步",
        "",
        "1. 人工补 3–5 条真实 known-document case（company_code + date window + title）。",
        "2. 将审核通过的 case 的 `case_status` 改为 `ready`。",
        "3. 再跑 selector 确认 `invalid_ready=0`。",
        "4. 实现 `validate_cninfo_b_class_corpus_retrieval.py` 仅消费 ready cases。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_b_class_retrieval_ready_case_report.csv](cninfo_b_class_retrieval_ready_case_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select B-class retrieval ready cases")
    parser.add_argument("--known-cases", default=DEFAULT_KNOWN)
    parser.add_argument("--category-cases", default=DEFAULT_CATEGORY)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    known = _load_cases(args.known_cases)
    category = _load_cases(args.category_cases)

    rows = process_cases(known, "known_document")
    rows.extend(process_cases(category, "category_sample"))

    write_csv(args.output_csv, rows)

    invalid = sum(1 for r in rows if r["ready_status"] == "invalid_ready")
    ready = sum(1 for r in rows if r["ready_status"] == "ready")
    placeholder = sum(1 for r in rows if r["ready_status"] == "placeholder")

    if invalid > 0:
        result = "FAIL"
    elif ready == 0:
        result = "NO_READY_CASES"
    else:
        result = "PASS"

    write_summary_md(args.output_md, rows, args.known_cases, args.category_cases, result)

    print(
        f"SUMMARY  total={len(rows)}  placeholder={placeholder}  "
        f"ready={ready}  invalid_ready={invalid}  result={result}"
    )
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")

    if invalid > 0:
        sys.exit(1)
    if args.strict and ready == 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
