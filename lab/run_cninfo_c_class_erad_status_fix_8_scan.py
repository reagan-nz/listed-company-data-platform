#!/usr/bin/env python3
"""
CNINFO C-class Era D — 8 家 missing_status_row 离线 source 扫描与 proposed status 行生成。

只读生产 harvest；写入仅允许 validation 子树 outputs/validation/cninfo_c_class_erad_status_fix_8/。
不修改生产 company_harvest_status.csv · 无 CNINFO。

Usage:
    python lab/run_cninfo_c_class_erad_status_fix_8_scan.py
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

import yaml  # noqa: E402

from build_cninfo_c_class_company_snapshot import SOURCE_TO_SUBDIR  # noqa: E402
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    assert_safe_erad_audit_write_path,
    is_protected_c_class_production_root,
    normalize_cleanup_path,
)
from harvest_cninfo_c_class import HARVEST_MATRIX_SOURCE_ORDER  # noqa: E402

TARGET_CODES: Tuple[str, ...] = (
    "000009", "000011", "000021", "000034",
    "000050", "000069", "000155", "000166",
)

DEFAULT_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class"
DEFAULT_OUTPUT_ROOT_REL = "outputs/validation/cninfo_c_class_erad_status_fix_8"
DEFAULT_UNIVERSE_YAML = "lab/eval_companies_c_class_harvest_863_non_bse.yaml"
STATUS_CSV_REL = "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"

PRESENCE_LEDGER_NAME = "status_fix_8_source_presence_ledger.csv"
PROPOSED_ROWS_NAME = "status_fix_8_proposed_status_rows.csv"
RUN_META_NAME = "run_meta.json"

SOURCES_EXPECTED = len(HARVEST_MATRIX_SOURCE_ORDER)
HTTP_SOURCES_PER_COMPANY = 7  # 与现有 status CSV 行对齐


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_universe_names(yaml_rel: str) -> Dict[str, Dict[str, str]]:
    path = os.path.join(BASE_DIR, yaml_rel)
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    out: Dict[str, Dict[str, str]] = {}
    for c in data.get("companies") or []:
        code = str(c["stock_code"])
        out[code] = {
            "company_name": str(c.get("company_name") or c.get("short_name") or ""),
            "board": str(c.get("board") or ""),
        }
    return out


def _load_status_map(status_csv_rel: str) -> Dict[str, Dict[str, str]]:
    path = os.path.join(BASE_DIR, status_csv_rel)
    rows: Dict[str, Dict[str, str]] = {}
    if not os.path.isfile(path):
        return rows
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = (row.get("company_code") or "").strip()
            if code:
                rows[code] = dict(row)
    return rows


def _normalized_path(harvest_root: str, source_id: str, company_code: str) -> str:
    subdir, ext = SOURCE_TO_SUBDIR[source_id]
    return os.path.join(harvest_root, "normalized", subdir, f"{company_code}{ext}")


def _source_present(harvest_root: str, source_id: str, company_code: str) -> bool:
    path = _normalized_path(harvest_root, source_id, company_code)
    if not os.path.isfile(path):
        return False
    if path.endswith(".json"):
        return os.path.getsize(path) > 2
    if path.endswith(".jsonl"):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    return True
        return False
    return True


def _assert_output_root(output_root_rel: str) -> str:
    norm = normalize_cleanup_path(output_root_rel)
    assert_safe_erad_audit_write_path(norm, allowed_audit_root_rel=output_root_rel)
    reports = os.path.join(norm, "reports")
    assert_safe_erad_audit_write_path(reports, allowed_audit_root_rel=output_root_rel)
    os.makedirs(reports, exist_ok=True)
    return norm


def _write_csv(path: str, fields: List[str], rows: List[Dict[str, str]], *, allowed_root_rel: str) -> None:
    assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=allowed_root_rel)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def scan_status_fix_8(
    *,
    harvest_root_rel: str = DEFAULT_HARVEST_ROOT_REL,
    output_root_rel: str = DEFAULT_OUTPUT_ROOT_REL,
    universe_yaml: str = DEFAULT_UNIVERSE_YAML,
    status_csv_rel: str = STATUS_CSV_REL,
) -> Dict[str, Any]:
    harvest_root = normalize_cleanup_path(harvest_root_rel)
    if is_protected_c_class_production_root(harvest_root):
        pass  # 只读扫描允许

    output_root = _assert_output_root(output_root_rel)
    universe = _load_universe_names(universe_yaml)
    status_map = _load_status_map(status_csv_rel)

    presence_rows: List[Dict[str, str]] = []
    proposed_rows: List[Dict[str, str]] = []
    all_ten_of_ten = True

    for code in TARGET_CODES:
        meta = universe.get(code, {"company_name": "", "board": ""})
        present_paths: List[str] = []
        missing_sources: List[str] = []

        for sid in HARVEST_MATRIX_SOURCE_ORDER:
            rel = os.path.relpath(
                _normalized_path(harvest_root, sid, code),
                BASE_DIR,
            )
            if _source_present(harvest_root, sid, code):
                present_paths.append(rel)
            else:
                missing_sources.append(sid)

        count = len(present_paths)
        status_before = "yes" if code in status_map else "no"
        ten_ok = count == SOURCES_EXPECTED and not missing_sources
        if not ten_ok:
            all_ten_of_ten = False

        proposed_status = "complete" if ten_ok else "needs_review"
        evidence = ";".join(present_paths)

        presence_rows.append({
            "company_code": code,
            "company_name": meta["company_name"],
            "normalized_source_count": str(count),
            "sources_expected": str(SOURCES_EXPECTED),
            "ten_of_ten_confirmed": "yes" if ten_ok else "no",
            "missing_sources": ";".join(missing_sources),
            "status_row_present_before": status_before,
            "proposed_status": proposed_status,
            "evidence_paths": evidence,
            "scan_mode": "read_only_production_harvest",
        })

        if ten_ok and status_before == "no":
            proposed_rows.append({
                "company_code": code,
                "company_name": meta["company_name"],
                "harvest_status": "complete",
                "sources_attempted": "10",
                "sources_http_success": str(HTTP_SOURCES_PER_COMPANY),
                "sources_failed": "0",
                "last_updated": _utc_now_iso(),
                "proposed_action": "append_row",
                "target_csv": status_csv_rel,
                "apply_status": "NOT_APPLIED_validation_only",
                "notes": "era_d_offline_status_backfill_missing_status_row;10_of_10_normalized_present",
            })

    reports_dir = os.path.join(output_root, "reports")
    presence_path = os.path.join(reports_dir, PRESENCE_LEDGER_NAME)
    proposed_path = os.path.join(reports_dir, PROPOSED_ROWS_NAME)
    meta_path = os.path.join(output_root, RUN_META_NAME)

    presence_fields = [
        "company_code", "company_name", "normalized_source_count", "sources_expected",
        "ten_of_ten_confirmed", "missing_sources", "status_row_present_before",
        "proposed_status", "evidence_paths", "scan_mode",
    ]
    proposed_fields = [
        "company_code", "company_name", "harvest_status", "sources_attempted",
        "sources_http_success", "sources_failed", "last_updated", "proposed_action",
        "target_csv", "apply_status", "notes",
    ]

    _write_csv(presence_path, presence_fields, presence_rows, allowed_root_rel=output_root_rel)
    _write_csv(proposed_path, proposed_fields, proposed_rows, allowed_root_rel=output_root_rel)

    meta = {
        "generated_at": _utc_now_iso(),
        "target_codes": list(TARGET_CODES),
        "harvest_root": harvest_root_rel,
        "output_root": output_root_rel,
        "status_csv": status_csv_rel,
        "ten_of_ten_all_confirmed": all_ten_of_ten,
        "proposed_row_count": len(proposed_rows),
        "production_harvest_write": False,
        "cninfo_calls": 0,
        "presence_ledger": presence_path,
        "proposed_rows": proposed_path,
    }
    assert_safe_erad_audit_write_path(meta_path, allowed_audit_root_rel=output_root_rel)
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"status_fix_8_scan_complete ten_of_ten_all={all_ten_of_ten} proposed={len(proposed_rows)}")
    print(f"presence_ledger={presence_path}")
    return meta


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Era D status-fix-8 offline scan")
    p.add_argument("--harvest-root", default=DEFAULT_HARVEST_ROOT_REL)
    p.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT_REL)
    p.add_argument("--universe-yaml", default=DEFAULT_UNIVERSE_YAML)
    p.add_argument("--status-csv", default=STATUS_CSV_REL)
    return p


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    scan_status_fix_8(
        harvest_root_rel=args.harvest_root,
        output_root_rel=args.output_root,
        universe_yaml=args.universe_yaml,
        status_csv_rel=args.status_csv,
    )


if __name__ == "__main__":
    main()
