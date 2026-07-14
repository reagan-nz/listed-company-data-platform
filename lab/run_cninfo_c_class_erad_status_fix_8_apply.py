#!/usr/bin/env python3
"""
CNINFO C-class Era D — 将 status-fix-8 proposed rows 安全写入生产 company_harvest_status.csv。

须人批短语。仅允许写入该 CSV（+ 备份）；无 CNINFO · 无 normalized/snapshot 变更。

Usage:
    python lab/run_cninfo_c_class_erad_status_fix_8_apply.py \\
      --approve-status-fix-8-apply
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from cninfo_c_class_erad_cleanup_guard import BASE_DIR, assert_safe_erad_audit_write_path  # noqa: E402
from run_cninfo_c_class_erad_status_fix_8_scan import TARGET_CODES  # noqa: E402

STATUS_FIX_8_APPLY_APPROVAL_REQUIRED = (
    "C_CLASS_ERAD_STATUS_FIX_8_APPLY_APPROVAL_REQUIRED"
)

PRODUCTION_STATUS_CSV_REL = "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"
PROPOSED_ROWS_REL = (
    "outputs/validation/cninfo_c_class_erad_status_fix_8/reports/"
    "status_fix_8_proposed_status_rows.csv"
)
DEFAULT_APPLY_OUTPUT_REL = "outputs/validation/cninfo_c_class_erad_status_fix_8_apply"

STATUS_FIELDS = [
    "company_code",
    "company_name",
    "harvest_status",
    "sources_attempted",
    "sources_http_success",
    "sources_failed",
    "last_updated",
]


def _utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _assert_apply_output_root(output_root_rel: str) -> str:
    norm = os.path.normpath(os.path.join(BASE_DIR, output_root_rel))
    assert_safe_erad_audit_write_path(norm, allowed_audit_root_rel=output_root_rel)
    reports = os.path.join(norm, "reports")
    assert_safe_erad_audit_write_path(reports, allowed_audit_root_rel=output_root_rel)
    os.makedirs(reports, exist_ok=True)
    return norm


def _load_proposed_rows(path_rel: str) -> List[Dict[str, str]]:
    path = os.path.join(BASE_DIR, path_rel)
    rows: List[Dict[str, str]] = []
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            code = (row.get("company_code") or "").strip()
            if code in TARGET_CODES:
                rows.append(row)
    rows.sort(key=lambda r: r["company_code"])
    if len(rows) != len(TARGET_CODES):
        raise SystemExit(f"proposed row count mismatch: {len(rows)} != {len(TARGET_CODES)}")
    return rows


def _read_status_csv(path: str) -> Tuple[List[str], List[Dict[str, str]]]:
    with open(path, encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or STATUS_FIELDS)
        rows = [dict(r) for r in reader]
    return fieldnames, rows


def _write_status_csv(path: str, fieldnames: List[str], rows: List[Dict[str, str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _row_to_status(proposed: Dict[str, str]) -> Dict[str, str]:
    return {
        "company_code": proposed["company_code"],
        "company_name": proposed["company_name"],
        "harvest_status": proposed["harvest_status"],
        "sources_attempted": proposed["sources_attempted"],
        "sources_http_success": proposed["sources_http_success"],
        "sources_failed": proposed["sources_failed"],
        "last_updated": _utc_now_iso(),
    }


def apply_status_fix_8(*, approve: bool, output_root_rel: str = DEFAULT_APPLY_OUTPUT_REL) -> Dict[str, Any]:
    if not approve:
        print(STATUS_FIX_8_APPLY_APPROVAL_REQUIRED, file=sys.stderr)
        raise SystemExit(2)

    status_path = os.path.join(BASE_DIR, PRODUCTION_STATUS_CSV_REL)
    if not os.path.isfile(status_path):
        raise SystemExit(f"production status CSV not found: {status_path}")

    proposed = _load_proposed_rows(PROPOSED_ROWS_REL)
    apply_root = _assert_apply_output_root(output_root_rel)

    ts = _utc_now_compact()
    backup_name = f"company_harvest_status.csv.bak_erad_status_fix_8_{ts}"
    backup_path = os.path.join(os.path.dirname(status_path), backup_name)
    shutil.copy2(status_path, backup_path)

    fieldnames, existing_rows = _read_status_csv(status_path)
    by_code: Dict[str, Dict[str, str]] = {
        (r.get("company_code") or "").strip(): r for r in existing_rows
    }

    ledger: List[Dict[str, str]] = []
    appended = 0
    already_present = 0

    for prop in proposed:
        code = prop["company_code"]
        before = by_code.get(code, {})
        before_status = before.get("harvest_status", "")

        if code in by_code:
            action = "already_present"
            after_status = before_status
            ok = before_status == prop["harvest_status"]
            already_present += 1
        else:
            new_row = _row_to_status(prop)
            existing_rows.append(new_row)
            by_code[code] = new_row
            action = "appended"
            after_status = new_row["harvest_status"]
            ok = after_status == prop["harvest_status"]
            appended += 1

        ledger.append({
            "company_code": code,
            "action": action,
            "before_status": before_status,
            "after_status": after_status,
            "ok": "yes" if ok else "no",
            "expected_status": prop["harvest_status"],
        })

    _write_status_csv(status_path, fieldnames, existing_rows)

    # 事后验证
    _, verify_rows = _read_status_csv(status_path)
    verify_map = {(r.get("company_code") or "").strip(): r for r in verify_rows}
    for entry in ledger:
        code = entry["company_code"]
        present = code in verify_map
        entry["post_verify_present"] = "yes" if present else "no"
        if present:
            entry["post_verify_status"] = verify_map[code].get("harvest_status", "")
            entry["post_verify_ok"] = (
                "yes" if verify_map[code].get("harvest_status") == entry["expected_status"] else "no"
            )
        else:
            entry["post_verify_status"] = ""
            entry["post_verify_ok"] = "no"

    reports_dir = os.path.join(apply_root, "reports")
    backup_note = os.path.join(reports_dir, "status_fix_8_apply_backup_path.txt")
    ledger_path = os.path.join(reports_dir, "status_fix_8_apply_ledger.csv")
    meta_path = os.path.join(apply_root, "run_meta.json")

    ledger_fields = [
        "company_code", "action", "before_status", "after_status", "expected_status",
        "ok", "post_verify_present", "post_verify_status", "post_verify_ok",
    ]

    assert_safe_erad_audit_write_path(backup_note, allowed_audit_root_rel=output_root_rel)
    with open(backup_note, "w", encoding="utf-8") as fh:
        fh.write(f"backup_path={backup_path}\n")
        fh.write(f"production_csv={status_path}\n")
        fh.write(f"timestamp={ts}\n")

    assert_safe_erad_audit_write_path(ledger_path, allowed_audit_root_rel=output_root_rel)
    with open(ledger_path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=ledger_fields, extrasaction="ignore")
        writer.writeheader()
        for row in ledger:
            writer.writerow(row)

    all_ok = all(r["post_verify_ok"] == "yes" for r in ledger)
    meta = {
        "generated_at": _utc_now_iso(),
        "backup_path": backup_path,
        "production_status_csv": PRODUCTION_STATUS_CSV_REL,
        "appended": appended,
        "already_present": already_present,
        "all_post_verify_ok": all_ok,
        "cninfo_calls": 0,
        "ledger": ledger_path,
    }
    assert_safe_erad_audit_write_path(meta_path, allowed_audit_root_rel=output_root_rel)
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"status_fix_8_apply_complete appended={appended} already_present={already_present} all_ok={all_ok}")
    print(f"backup={backup_path}")
    return meta


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Apply status-fix-8 proposed rows")
    p.add_argument(
        "--approve-status-fix-8-apply",
        action="store_true",
        help="explicit human approval for production status CSV write",
    )
    p.add_argument("--output-root", default=DEFAULT_APPLY_OUTPUT_REL)
    return p


def main(argv: Optional[List[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    apply_status_fix_8(approve=args.approve_status_fix_8_apply, output_root_rel=args.output_root)


if __name__ == "__main__":
    main()
