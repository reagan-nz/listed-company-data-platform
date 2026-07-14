#!/usr/bin/env python3
"""
从 fuller-market slice1 universe draft CSV 构建 eval YAML（离线 · CNINFO=0）。

输入：slice1 draft CSV + full_market 母本 + 863/hold 排除集。
输出：lab/eval_companies_c_class_fuller_market_slice1_200.yaml + overlap 复验产物。
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.normpath(os.path.join(_LAB_DIR, ".."))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from validate_cninfo_c_class_scale_smoke import load_sample_yaml  # noqa: E402

SLICE1_EXPECTED_COUNT = 200
SLICE1_CASE_ID_PREFIX = "CE1E"
DEFAULT_DRAFT_CSV_REL = (
    "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_universe_draft.csv"
)
DEFAULT_PARENT_YAML_REL = "lab/eval_companies_full_market_2024.yaml"
DEFAULT_EXCLUDE_863_REL = "lab/eval_companies_c_class_harvest_863_non_bse.yaml"
DEFAULT_HOLD_REL = "lab/eval_companies_c_class_889_rerun_all6_hold.yaml"
DEFAULT_OUTPUT_YAML_REL = "lab/eval_companies_c_class_fuller_market_slice1_200.yaml"
DEFAULT_OVERLAP_MD_REL = (
    "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_overlap_recheck.md"
)
DEFAULT_OVERLAP_CSV_REL = (
    "outputs/validation/cninfo_c_class_erad_fuller_market_slice1_overlap_recheck.csv"
)

PHASE3_SAMPLE_REL = "lab/eval_companies_c_class_phase3_batch_500_001.yaml"
PHASE35_SAMPLE_REL = "lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml"


@dataclass
class OverlapReport:
    """overlap 复验结果汇总。"""

    company_count: int = 0
    overlap_863: Set[str] = field(default_factory=set)
    overlap_hold: Set[str] = field(default_factory=set)
    overlap_phase3: Set[str] = field(default_factory=set)
    overlap_phase35: Set[str] = field(default_factory=set)
    bse_codes: Set[str] = field(default_factory=set)
    st_or_delist_codes: Set[str] = field(default_factory=set)
    missing_parent: List[str] = field(default_factory=list)
    case_id_mismatch: List[str] = field(default_factory=list)
    duplicate_codes: Set[str] = field(default_factory=set)

    @property
    def pass_offline(self) -> bool:
        return (
            self.company_count == SLICE1_EXPECTED_COUNT
            and not self.overlap_863
            and not self.overlap_hold
            and not self.overlap_phase3
            and not self.overlap_phase35
            and not self.bse_codes
            and not self.st_or_delist_codes
            and not self.missing_parent
            and not self.case_id_mismatch
            and not self.duplicate_codes
        )


def _abs(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(BASE_DIR, rel)


def _load_codes_from_yaml(path: str) -> Set[str]:
    data = load_sample_yaml(path)
    return {str(c["stock_code"]).zfill(6) for c in data.get("companies") or []}


def _load_parent_index(path: str) -> Dict[str, Dict[str, Any]]:
    data = load_sample_yaml(path)
    index: Dict[str, Dict[str, Any]] = {}
    for c in data.get("companies") or []:
        code = str(c["stock_code"]).zfill(6)
        index[code] = dict(c)
    return index


def _load_draft_rows(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append({
                "case_id": row["case_id"].strip(),
                "company_code": str(row["company_code"]).zfill(6),
                "cohort": row.get("cohort", "").strip(),
                "prior_in_863": row.get("prior_in_863", "").strip(),
                "include_reason": row.get("include_reason", "").strip(),
            })
    return rows


def _is_st_or_delist(name: str) -> bool:
    upper = name.upper()
    if "ST" in upper and ("*ST" in upper or "ST" in name):
        return True
    if "退" in name:
        return True
    return False


def _expected_case_id(index: int) -> str:
    return f"{SLICE1_CASE_ID_PREFIX}{index:03d}"


def validate_slice_companies(
    draft_rows: List[Dict[str, str]],
    parent_index: Dict[str, Dict[str, Any]],
    exclude_863: Set[str],
    exclude_hold: Set[str],
    exclude_phase3: Set[str],
    exclude_phase35: Set[str],
) -> Tuple[List[Dict[str, Any]], OverlapReport]:
    """构建公司列表并收集 overlap 违规。"""
    report = OverlapReport()
    report.company_count = len(draft_rows)
    companies_out: List[Dict[str, Any]] = []
    seen_codes: Set[str] = set()

    for i, row in enumerate(draft_rows, start=1):
        code = row["company_code"]
        expected_cid = _expected_case_id(i)
        if row["case_id"] != expected_cid:
            report.case_id_mismatch.append(f"{row['case_id']}!={expected_cid}")

        if code in seen_codes:
            report.duplicate_codes.add(code)
        seen_codes.add(code)

        if code in exclude_863:
            report.overlap_863.add(code)
        if code in exclude_hold:
            report.overlap_hold.add(code)
        if code in exclude_phase3:
            report.overlap_phase3.add(code)
        if code in exclude_phase35:
            report.overlap_phase35.add(code)

        parent = parent_index.get(code)
        if parent is None:
            report.missing_parent.append(code)
            continue

        board = str(parent.get("board", ""))
        name = str(parent.get("short_name") or parent.get("company_name") or "")
        if board == "bse":
            report.bse_codes.add(code)
        if _is_st_or_delist(name):
            report.st_or_delist_codes.add(code)

        entry = dict(parent)
        entry["stock_code"] = code
        entry["company_name"] = name
        entry["harvest_status"] = "active_candidate"
        entry["case_id"] = row["case_id"]
        entry["cohort"] = row["cohort"]
        companies_out.append(entry)

    return companies_out, report


def build_slice_yaml(
    draft_csv: str,
    parent_yaml: str,
    exclude_863_yaml: str,
    hold_yaml: str,
    output_yaml: str,
    overlap_md: str,
    overlap_csv: str,
) -> Tuple[int, OverlapReport]:
    """主构建流程：YAML + overlap 复验产物。"""
    draft_rows = _load_draft_rows(draft_csv)
    parent_index = _load_parent_index(parent_yaml)
    exclude_863 = _load_codes_from_yaml(exclude_863_yaml)
    exclude_hold = _load_codes_from_yaml(hold_yaml)

    exclude_phase3: Set[str] = set()
    phase3_path = _abs(PHASE3_SAMPLE_REL)
    if os.path.isfile(phase3_path):
        exclude_phase3 = _load_codes_from_yaml(phase3_path)

    exclude_phase35: Set[str] = set()
    phase35_path = _abs(PHASE35_SAMPLE_REL)
    if os.path.isfile(phase35_path):
        exclude_phase35 = _load_codes_from_yaml(phase35_path)

    companies, report = validate_slice_companies(
        draft_rows, parent_index, exclude_863, exclude_hold, exclude_phase3, exclude_phase35,
    )

    if not report.pass_offline:
        raise SystemExit(f"slice1 overlap validation FAIL: {report}")

    board_counts = Counter(str(c.get("board", "")) for c in companies)
    out_doc = {
        "version": "c-class-fuller-market-slice1-200-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "parent_universe": os.path.relpath(parent_yaml, BASE_DIR).replace("\\", "/"),
        "excluded_863": os.path.relpath(exclude_863_yaml, BASE_DIR).replace("\\", "/"),
        "excluded_hold": os.path.relpath(hold_yaml, BASE_DIR).replace("\\", "/"),
        "draft_csv": os.path.relpath(draft_csv, BASE_DIR).replace("\\", "/"),
        "universe_id": "fuller_market_slice1",
        "description": "Era D fuller-market slice1 +200；CE1E001–CE1E200；零 overlap 863/hold",
        "company_count": len(companies),
        "case_id_range": f"{SLICE1_CASE_ID_PREFIX}001–{SLICE1_CASE_ID_PREFIX}{SLICE1_EXPECTED_COUNT:03d}",
        "harvest_status_default": "active_candidate",
        "board_counts": dict(sorted(board_counts.items())),
        "companies": companies,
    }

    os.makedirs(os.path.dirname(output_yaml) or ".", exist_ok=True)
    with open(output_yaml, "w", encoding="utf-8") as fh:
        yaml.dump(out_doc, fh, allow_unicode=True, sort_keys=False, default_flow_style=False)

    _write_overlap_artifacts(report, overlap_md, overlap_csv, draft_rows)
    return len(companies), report


def _write_overlap_artifacts(
    report: OverlapReport,
    md_path: str,
    csv_path: str,
    draft_rows: List[Dict[str, str]],
) -> None:
    """写出 overlap 复验 MD + CSV。"""
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    gate = "PASS_OFFLINE" if report.pass_offline else "FAIL"

    lines = [
        "# CNINFO C 类 Era D — Fuller-Market Slice1 Overlap Recheck",
        "",
        f"_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_",
        "",
        "> **offline only** · **CNINFO = 0**",
        "",
        "## Summary",
        "",
        f"| check | result |",
        f"|-------|--------|",
        f"| company_count | **{report.company_count}** (expected **{SLICE1_EXPECTED_COUNT}**) |",
        f"| overlap_863 | **{len(report.overlap_863)}** |",
        f"| overlap_hold_26 | **{len(report.overlap_hold)}** |",
        f"| overlap_phase3 | **{len(report.overlap_phase3)}** |",
        f"| overlap_phase35 | **{len(report.overlap_phase35)}** |",
        f"| bse | **{len(report.bse_codes)}** |",
        f"| st_or_delist | **{len(report.st_or_delist_codes)}** |",
        f"| missing_parent | **{len(report.missing_parent)}** |",
        f"| case_id_mismatch | **{len(report.case_id_mismatch)}** |",
        f"| duplicate_codes | **{len(report.duplicate_codes)}** |",
        f"| **gate** | **`{gate}`** |",
        "",
    ]
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    with open(csv_path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=["case_id", "company_code", "check_name", "status", "notes"],
        )
        w.writeheader()
        for row in draft_rows:
            code = row["company_code"]
            checks = [
                ("overlap_863", code not in report.overlap_863),
                ("overlap_hold", code not in report.overlap_hold),
                ("overlap_phase3", code not in report.overlap_phase3),
                ("overlap_phase35", code not in report.overlap_phase35),
                ("bse", code not in report.bse_codes),
                ("st_or_delist", code not in report.st_or_delist_codes),
                ("parent_found", code not in report.missing_parent),
            ]
            for check_name, ok in checks:
                w.writerow({
                    "case_id": row["case_id"],
                    "company_code": code,
                    "check_name": check_name,
                    "status": "pass" if ok else "fail",
                    "notes": "",
                })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="构建 fuller-market slice1 eval YAML")
    parser.add_argument("--draft-csv", default=DEFAULT_DRAFT_CSV_REL)
    parser.add_argument("--parent-yaml", default=DEFAULT_PARENT_YAML_REL)
    parser.add_argument("--exclude-yaml", default=DEFAULT_EXCLUDE_863_REL)
    parser.add_argument("--hold-yaml", default=DEFAULT_HOLD_REL)
    parser.add_argument("--output-yaml", default=DEFAULT_OUTPUT_YAML_REL)
    parser.add_argument("--overlap-md", default=DEFAULT_OVERLAP_MD_REL)
    parser.add_argument("--overlap-csv", default=DEFAULT_OVERLAP_CSV_REL)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    count, report = build_slice_yaml(
        _abs(args.draft_csv),
        _abs(args.parent_yaml),
        _abs(args.exclude_yaml),
        _abs(args.hold_yaml),
        _abs(args.output_yaml),
        _abs(args.overlap_md),
        _abs(args.overlap_csv),
    )
    print(
        f"SUMMARY  built={args.output_yaml}  companies={count}  "
        f"overlap_863={len(report.overlap_863)}  overlap_hold={len(report.overlap_hold)}  "
        f"gate={'PASS_OFFLINE' if report.pass_offline else 'FAIL'}"
    )


if __name__ == "__main__":
    main()
