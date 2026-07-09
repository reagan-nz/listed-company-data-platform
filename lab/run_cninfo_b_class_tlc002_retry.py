"""
CNINFO B-class TLC002 isolated retry runner.

仅 TLC002（300009 安科生物）· 默认 dry-run · **不请求 CNINFO**。
--live 须 --approve-b-class-tlc002-retry；禁止单独使用 tiny-live approval flag。

Usage:
    python lab/run_cninfo_b_class_tlc002_retry.py
    python lab/run_cninfo_b_class_tlc002_retry.py --live \\
        --approve-b-class-tlc002-retry
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_DIR = os.path.join(BASE_DIR, "lab")
if LAB_DIR not in sys.path:
    sys.path.insert(0, LAB_DIR)

import run_cninfo_b_class_tiny_live_validation as tiny_live  # noqa: E402

ALLOWED_CASE_ID = "TLC002"
ALLOWED_COMPANY_CODE = "300009"

DEFAULT_UNIVERSE_CSV = os.path.join(
    BASE_DIR,
    "outputs",
    "validation",
    "cninfo_b_class_phase1_tiny_live_validation_universe.csv",
)
DEFAULT_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tlc002_retry"
)
TINY_LIVE_BASELINE_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_tiny_live_validation"
)
REPORT_CSV = os.path.join(DEFAULT_OUTPUT_ROOT, "reports", "tlc002_retry_report.csv")
SUMMARY_MD = os.path.join(DEFAULT_OUTPUT_ROOT, "reports", "tlc002_retry_summary.md")

TLC002_RETRY_APPROVAL_REQUIRED = "approve_b_class_tlc002_retry_required"
TINY_LIVE_ALONE_REJECTED = "approve_b_class_tiny_live_validation_alone_not_allowed_for_tlc002_retry"
WRONG_CASE_REJECTED = "only_tlc002_allowed"
OUTPUT_ROOT_VIOLATION = "output_root_must_be_cninfo_b_class_tlc002_retry"
TINY_LIVE_BASELINE_WRITE_FORBIDDEN = "tiny_live_baseline_output_write_forbidden"

REPORT_COLUMNS = tiny_live.REPORT_COLUMNS
PDF_DOWNLOAD_ENABLED = tiny_live.PDF_DOWNLOAD_ENABLED
PDF_PARSE_ENABLED = tiny_live.PDF_PARSE_ENABLED


def validate_output_root(output_root: str) -> Tuple[bool, str]:
    """输出仅允许 TLC002 retry 隔离根；禁止写入 tiny live baseline。"""
    root = os.path.normpath(os.path.abspath(output_root))
    allowed = os.path.normpath(os.path.abspath(DEFAULT_OUTPUT_ROOT))
    baseline = os.path.normpath(os.path.abspath(TINY_LIVE_BASELINE_ROOT))
    if root == baseline or root.startswith(baseline + os.sep):
        return False, TINY_LIVE_BASELINE_WRITE_FORBIDDEN
    if root == allowed or root.startswith(allowed + os.sep):
        return True, ""
    return False, OUTPUT_ROOT_VIOLATION


def ensure_output_layout(output_root: str) -> Dict[str, str]:
    paths = {
        "root": output_root,
        "raw_metadata": os.path.join(output_root, "raw_metadata"),
        "quality": os.path.join(output_root, "quality"),
        "reports": os.path.join(output_root, "reports"),
    }
    for p in paths.values():
        os.makedirs(p, exist_ok=True)
    return paths


def load_tlc002_case(universe_csv: str) -> tiny_live.UniverseCase:
    cases = tiny_live.load_universe(universe_csv)
    for case in cases:
        if case.case_id == ALLOWED_CASE_ID and case.company_code == ALLOWED_COMPANY_CODE:
            return case
    raise ValueError(f"{WRONG_CASE_REJECTED}: TLC002 not in universe")


def validate_tlc002_only(case: tiny_live.UniverseCase) -> List[str]:
    issues: List[str] = []
    if case.case_id != ALLOWED_CASE_ID:
        issues.append(f"case_id_must_be_{ALLOWED_CASE_ID}")
    if case.company_code != ALLOWED_COMPANY_CODE:
        issues.append(f"company_code_must_be_{ALLOWED_COMPANY_CODE}")
    issues.extend(tiny_live.validate_universe_case(case))
    for ep in case.endpoint_scope:
        if ep in tiny_live.BLOCKED_ENDPOINTS:
            issues.append(f"endpoint_blocked:{ep}")
    return issues


def enforce_approval_gate(args: argparse.Namespace) -> None:
    if args.approve_b_class_tiny_live_validation and not args.approve_b_class_tlc002_retry:
        print(f"ERROR: {TINY_LIVE_ALONE_REJECTED}", file=sys.stderr)
        sys.exit(2)
    if args.mode == "live" and not args.approve_b_class_tlc002_retry:
        print(f"ERROR: {TLC002_RETRY_APPROVAL_REQUIRED}", file=sys.stderr)
        sys.exit(2)
    for flag, err in (
        (args.approve_full_harvest, tiny_live.FORBIDDEN_APPROVE_FULL_HARVEST),
        (args.approve_phase2_smoke_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE2),
        (args.approve_phase3_batch_500_harvest, tiny_live.FORBIDDEN_APPROVE_PHASE3),
    ):
        if flag:
            print(f"ERROR: {err}", file=sys.stderr)
            sys.exit(2)


def _print_progress(record: Dict[str, Any]) -> None:
    print(
        f"case_id={record.get('case_id')} endpoint_id={record.get('endpoint_id')} "
        f"company_code={record.get('company_code')} retrieval_status={record.get('retrieval_status')} "
        f"quality_status={record.get('quality_status')}",
        flush=True,
    )


def build_dry_run_record(case: tiny_live.UniverseCase) -> Dict[str, Any]:
    ep = tiny_live.SOURCE_TYPE_PRIMARY_ENDPOINT[case.source_type]
    rec = tiny_live.build_dry_run_record(case, ep)
    rec["notes"] = "tlc002 retry dry-run; CNINFO not called; isolated output"
    rec["retrieval_status"] = "retry_dry_run_planned"
    return rec


def process_dry_run(
    case: tiny_live.UniverseCase,
    output_paths: Dict[str, str],
) -> Dict[str, Any]:
    ep = tiny_live.SOURCE_TYPE_PRIMARY_ENDPOINT[case.source_type]
    record = build_dry_run_record(case)
    qs, ls, et, qnotes = tiny_live.assess_quality_rules(record)
    record["quality_status"] = qs
    record["lineage_status"] = ls
    record["error_type"] = et or record["error_type"]
    if qnotes:
        record["notes"] = f"{record['notes']}; {qnotes}"
    _write_artifacts(case, record, output_paths, mode="dry_run", cninfo_called=False)
    _print_progress(record)
    return record


def process_live(
    case: tiny_live.UniverseCase,
    output_paths: Dict[str, str],
    categories_config: Dict[str, Any],
) -> Tuple[Dict[str, Any], tiny_live.LiveStats]:
    stats = tiny_live.LiveStats()
    record = tiny_live.execute_live_case(case, categories_config, stats)
    record["notes"] = f"tlc002 isolated retry; {record.get('notes', '')}"
    _write_artifacts(case, record, output_paths, mode="live", cninfo_called=True)
    _print_progress(record)
    return record, stats


def _write_artifacts(
    case: tiny_live.UniverseCase,
    record: Dict[str, Any],
    output_paths: Dict[str, str],
    mode: str,
    cninfo_called: bool,
) -> None:
    ep = record.get("endpoint_id") or tiny_live.SOURCE_TYPE_PRIMARY_ENDPOINT[case.source_type]
    snap = os.path.join(output_paths["raw_metadata"], f"{ALLOWED_CASE_ID}_{ep}.json")
    with open(snap, "w", encoding="utf-8") as f:
        json.dump(
            {
                "case": case.__dict__,
                "mode": mode,
                "retry": "tlc002_isolated",
                "cninfo_called": cninfo_called,
                "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                "pdf_parse_enabled": PDF_PARSE_ENABLED,
                "record": {k: record.get(k) for k in REPORT_COLUMNS},
                "raw_announcement": record.get("raw_announcement"),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    qpath = os.path.join(output_paths["quality"], f"{ALLOWED_CASE_ID}.json")
    with open(qpath, "w", encoding="utf-8") as f:
        json.dump(
            {
                "case_id": ALLOWED_CASE_ID,
                "quality_status": record.get("quality_status"),
                "lineage_status": record.get("lineage_status"),
                "error_type": record.get("error_type", ""),
                "pdf_download_enabled": PDF_DOWNLOAD_ENABLED,
                "pdf_parse_enabled": PDF_PARSE_ENABLED,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def write_report(record: Dict[str, Any], output_paths: Dict[str, str]) -> str:
    path = os.path.join(output_paths["reports"], "tlc002_retry_report.csv")
    row = {k: str(record.get(k, "")) for k in REPORT_COLUMNS}
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REPORT_COLUMNS)
        w.writeheader()
        w.writerow(row)
    return path


def write_summary(
    mode: str,
    record: Dict[str, Any],
    stats: Optional[tiny_live.LiveStats],
    output_paths: Dict[str, str],
) -> str:
    cninfo_calls = stats.cninfo_requests if stats else 0
    lines = [
        "# TLC002 Isolated Retry Summary",
        "",
        f"_generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC_",
        "",
        f"| mode | {mode} |",
        f"| case_id | {ALLOWED_CASE_ID} |",
        f"| company_code | {ALLOWED_COMPANY_CODE} |",
        f"| retrieval_status | {record.get('retrieval_status')} |",
        f"| quality_status | {record.get('quality_status')} |",
        f"| CNINFO calls | {cninfo_calls} |",
        f"| PDF download | **disabled** |",
        f"| output root | `{output_paths['root']}` |",
        "",
        "**tiny live baseline untouched**",
        "",
    ]
    with open(SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return SUMMARY_MD


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TLC002 isolated retry（dry-run default）")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry_run")
    mode.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.set_defaults(mode="dry_run")
    parser.add_argument("--universe-csv", default=DEFAULT_UNIVERSE_CSV)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--approve-b-class-tlc002-retry", action="store_true")
    parser.add_argument("--approve-b-class-tiny-live-validation", action="store_true")
    parser.add_argument("--approve-full-harvest", action="store_true")
    parser.add_argument("--approve-phase2-smoke-harvest", action="store_true")
    parser.add_argument("--approve-phase3-batch-500-harvest", action="store_true")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "live":
        enforce_approval_gate(args)

    ok, err = validate_output_root(args.output_root)
    if not ok:
        print(f"ERROR: {err}", file=sys.stderr)
        return 2

    try:
        case = load_tlc002_case(args.universe_csv)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    issues = validate_tlc002_only(case)
    if issues:
        print(f"ERROR: {'; '.join(issues)}", file=sys.stderr)
        return 2

    output_paths = ensure_output_layout(os.path.normpath(os.path.abspath(args.output_root)))
    stats: Optional[tiny_live.LiveStats] = None

    if args.mode == "live":
        with open(tiny_live.CATEGORIES_YAML, encoding="utf-8") as f:
            categories = yaml.safe_load(f) or {}
        record, stats = process_live(case, output_paths, categories)
    else:
        record = process_dry_run(case, output_paths)

    report_path = write_report(record, output_paths)
    summary_path = write_summary(args.mode, record, stats, output_paths)

    cninfo_calls = stats.cninfo_requests if stats else 0
    print(f"mode={args.mode} case_id={ALLOWED_CASE_ID} cninfo_calls={cninfo_calls}")
    print(f"report={report_path}")
    print(f"summary={summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
