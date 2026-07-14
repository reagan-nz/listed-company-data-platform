#!/usr/bin/env python3
"""
CNINFO C-class Era D — 6 家 partial-source 离线 human-review 扫描（只读）。

无 CNINFO · 无生产写入 · 输出仅 validation 子树。

Usage:
    python lab/run_cninfo_c_class_erad_partial6_human_review_scan.py
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

import yaml  # noqa: E402

from build_cninfo_c_class_company_snapshot import SOURCE_TO_SUBDIR  # noqa: E402
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    BASE_DIR,
    assert_safe_erad_audit_write_path,
)
from harvest_cninfo_c_class import HARVEST_MATRIX_SOURCE_ORDER  # noqa: E402

TARGET_CODES: Tuple[str, ...] = (
    "002267", "002710", "301333", "301583", "601206", "688688",
)

DEFAULT_HARVEST_ROOT_REL = "outputs/harvest/cninfo_c_class"
DEFAULT_SNAPSHOT_ROOT_REL = "outputs/snapshot/cninfo_c_class/full"
DEFAULT_OUTPUT_ROOT_REL = "outputs/validation/cninfo_c_class_erad_partial6_human_review"
DEFAULT_UNIVERSE_YAML = "lab/eval_companies_c_class_harvest_863_non_bse.yaml"
STATUS_CSV_REL = "outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv"

SOURCES_EXPECTED = len(HARVEST_MATRIX_SOURCE_ORDER)

# 常见「空但合法」源 — 缺失文件可能是 empty_but_valid 而非 harvest gap
EMPTY_BUT_VALID_PRONE = frozenset({
    "cninfo_dividend_financing_profile",
    "cninfo_executive_profile",
    "cninfo_share_capital_profile",
    "cninfo_top_shareholders_profile",
    "cninfo_top_float_shareholders_profile",
})


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_universe(yaml_rel: str) -> Dict[str, Dict[str, str]]:
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
    if os.path.isfile(path):
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


def _snapshot_present(snapshot_root: str, company_code: str) -> str:
    path = os.path.join(snapshot_root, f"{company_code}.json")
    if os.path.isfile(path) and os.path.getsize(path) > 2:
        return "yes"
    if not os.path.isdir(snapshot_root):
        return "unknown"
    return "no"


def _classify_gap(
    present: List[str],
    missing: List[str],
    status_row: Optional[Dict[str, str]],
) -> Tuple[str, str]:
    """返回 (likely_gap_class, recommendation)。"""
    csv_status = (status_row or {}).get("harvest_status", "")
    all_missing_empty_prone = missing and all(m in EMPTY_BUT_VALID_PRONE for m in missing)
    basic_present = "cninfo_company_basic_profile" in present

    if not basic_present:
        return "true_harvest_gap", "needs_live_resume"

    if csv_status == "complete" and missing and all_missing_empty_prone:
        return "status_ledger_only", "accept_with_caveat"

    if missing and all(m in EMPTY_BUT_VALID_PRONE for m in missing):
        return "mapper_drop", "offline_remap_only"

    if csv_status == "complete" and len(present) >= 6:
        return "status_ledger_only", "accept_with_caveat"

    if missing:
        return "other", "defer"

    return "other", "accept_with_caveat"


def _company_section_md(
    code: str,
    name: str,
    present: List[str],
    missing: List[str],
    gap_class: str,
    recommendation: str,
    status_row: Optional[Dict[str, str]],
    snapshot: str,
) -> List[str]:
    csv_status = (status_row or {}).get("harvest_status", "absent")
    lines = [
        f"### {code} — {name}",
        "",
        f"- **status_row:** present · `harvest_status={csv_status}`",
        f"- **normalized:** {len(present)}/10 present",
        f"- **snapshot (863 full):** {snapshot}",
        f"- **present:** {', '.join(present) if present else '(none)'}",
        f"- **missing:** {', '.join(missing) if missing else '(none)'}",
        f"- **likely_gap_class:** `{gap_class}`",
        f"- **recommendation:** `{recommendation}`",
        "",
    ]
    if gap_class == "status_ledger_only":
        lines.append(
            "磁盘缺 4 个 normalized 文件，但 status CSV 标 complete；"
            "与 Era C empty_but_valid / derived 语义一致，非 proven live 缺口。"
        )
    elif gap_class == "mapper_drop":
        lines.append("缺失源多为 array/optional profile；可考虑 offline remap，不需 live。")
    lines.append("")
    return lines


def scan_partial6(
    *,
    harvest_root_rel: str = DEFAULT_HARVEST_ROOT_REL,
    snapshot_root_rel: str = DEFAULT_SNAPSHOT_ROOT_REL,
    output_root_rel: str = DEFAULT_OUTPUT_ROOT_REL,
    universe_yaml: str = DEFAULT_UNIVERSE_YAML,
    status_csv_rel: str = STATUS_CSV_REL,
) -> Dict[str, Any]:
    harvest_root = os.path.join(BASE_DIR, harvest_root_rel)
    snapshot_root = os.path.join(BASE_DIR, snapshot_root_rel)
    output_root = os.path.join(BASE_DIR, output_root_rel)
    assert_safe_erad_audit_write_path(output_root, allowed_audit_root_rel=output_root_rel)
    reports_dir = os.path.join(output_root, "reports")
    assert_safe_erad_audit_write_path(reports_dir, allowed_audit_root_rel=output_root_rel)
    os.makedirs(reports_dir, exist_ok=True)

    universe = _load_universe(universe_yaml)
    status_map = _load_status_map(status_csv_rel)

    presence_rows: List[Dict[str, str]] = []
    matrix_rows: List[Dict[str, str]] = []
    packet_sections: List[str] = [
        "# C-Class Era D — Partial-6 Human-Review Packet",
        "",
        f"_generated_at: {_utc_now_iso()}_",
        "",
        "> offline read-only · CNINFO = 0 · no auto-fix",
        "",
    ]

    gap_counts: Counter = Counter()
    rec_counts: Counter = Counter()
    live_resume_count = 0

    for code in TARGET_CODES:
        meta = universe.get(code, {"company_name": "", "board": ""})
        name = meta["company_name"] or status_map.get(code, {}).get("company_name", "")
        present: List[str] = []
        missing: List[str] = []

        for sid in HARVEST_MATRIX_SOURCE_ORDER:
            ok = _source_present(harvest_root, sid, code)
            rel = os.path.relpath(_normalized_path(harvest_root, sid, code), BASE_DIR)
            matrix_rows.append({
                "company_code": code,
                "source_id": sid,
                "file_exists": "yes" if ok else "no",
                "normalized_path": rel,
            })
            if ok:
                present.append(sid)
            else:
                missing.append(sid)

        status_row = status_map.get(code)
        snap = _snapshot_present(snapshot_root, code)
        gap_class, recommendation = _classify_gap(present, missing, status_row)
        gap_counts[gap_class] += 1
        rec_counts[recommendation] += 1
        if recommendation == "needs_live_resume":
            live_resume_count += 1

        presence_rows.append({
            "company_code": code,
            "company_name": name,
            "normalized_source_count": str(len(present)),
            "sources_expected": str(SOURCES_EXPECTED),
            "present_sources": ";".join(present),
            "missing_sources": ";".join(missing),
            "status_row_present": "yes" if status_row else "no",
            "status_harvest_status": (status_row or {}).get("harvest_status", ""),
            "snapshot_present": snap,
            "likely_gap_class": gap_class,
            "recommendation": recommendation,
            "notes": "read_only_scan_863_primary",
        })

        packet_sections.extend(_company_section_md(
            code, name, present, missing, gap_class, recommendation, status_row, snap,
        ))

    # write CSVs
    presence_path = os.path.join(reports_dir, "partial6_source_presence_ledger.csv")
    matrix_path = os.path.join(reports_dir, "partial6_missing_source_matrix.csv")
    packet_path = os.path.join(output_root, "partial6_human_review_packet.md")
    meta_path = os.path.join(output_root, "run_meta.json")

    presence_fields = [
        "company_code", "company_name", "normalized_source_count", "sources_expected",
        "present_sources", "missing_sources", "status_row_present", "status_harvest_status",
        "snapshot_present", "likely_gap_class", "recommendation", "notes",
    ]
    matrix_fields = ["company_code", "source_id", "file_exists", "normalized_path"]

    for path, fields, rows in (
        (presence_path, presence_fields, presence_rows),
        (matrix_path, matrix_fields, matrix_rows),
    ):
        assert_safe_erad_audit_write_path(path, allowed_audit_root_rel=output_root_rel)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    assert_safe_erad_audit_write_path(packet_path, allowed_audit_root_rel=output_root_rel)
    with open(packet_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(packet_sections))

    meta = {
        "generated_at": _utc_now_iso(),
        "target_codes": list(TARGET_CODES),
        "gap_class_counts": dict(gap_counts),
        "recommendation_counts": dict(rec_counts),
        "needs_live_resume_count": live_resume_count,
        "cninfo_calls": 0,
        "production_write": False,
    }
    assert_safe_erad_audit_write_path(meta_path, allowed_audit_root_rel=output_root_rel)
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"partial6_scan_complete live_resume_recommended={live_resume_count}")
    print(f"gap_classes={dict(gap_counts)}")
    return meta


def main(argv: Optional[List[str]] = None) -> None:
    scan_partial6()


if __name__ == "__main__":
    main()
