#!/usr/bin/env python3
"""
CNINFO C-class company_registry_candidate 离线派生脚本。

仅读取现有 YAML / CSV / snapshot 元数据，不请求 CNINFO、不 live、不 harvest。
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ACTIVE_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_harvest_863_non_bse.yaml")
HOLD_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_889_rerun_all6_hold.yaml")
BSE_920_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_920_active.yaml")
BSE_LEGACY_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_smoke_195_bse_legacy_hold.yaml")
FULL_MARKET_YAML = os.path.join(BASE_DIR, "lab/eval_companies_full_market_2024.yaml")
SNAPSHOT_DIR = os.path.join(BASE_DIR, "outputs/snapshot/cninfo_c_class/full")
SNAPSHOT_STATUS_CSV = os.path.join(SNAPSHOT_DIR, "quality/company_snapshot_status.csv")

DEFAULT_CSV_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_draft.csv"
)
DEFAULT_SUMMARY_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_summary.md"
)

CSV_COLUMNS = [
    "company_id",
    "company_code",
    "company_name",
    "company_full_name",
    "english_name",
    "exchange",
    "board",
    "security_type",
    "listing_status",
    "active_status",
    "org_id",
    "legacy_code",
    "previous_code",
    "rename_history",
    "org_id_conflict_flag",
    "st_flag",
    "delisted_flag",
    "suspended_flag",
    "hold_flag",
    "harvest_support_status",
    "snapshot_support_status",
    "source",
    "confidence",
    "notes",
]

# BSE 策略文档中的 org_id 配对（839729 -> 920729）
BSE_ORG_ID_LEGACY_TO_CURRENT: Dict[str, str] = {
    "gfbj0839729": "920729",
}

SOURCE_PRIORITY = {
    "harvest_863_yaml": 5,
    "hold_26_yaml": 4,
    "bse_920_yaml": 3,
    "bse_legacy_yaml": 2,
    "full_market_2024": 1,
}


def _normalize_code(code: Any) -> str:
    return str(code).strip().zfill(6) if str(code).strip().isdigit() else str(code).strip()


def _load_yaml_companies(path: str) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return list(data.get("companies") or [])


def _company_name_from_entry(entry: Dict[str, Any]) -> str:
    return str(entry.get("short_name") or entry.get("company_name") or "").strip()


def _detect_st_flag(name: str) -> bool:
    if not name:
        return False
    upper = name.upper()
    return upper.startswith("*ST") or upper.startswith("ST") or "*ST" in upper


def _detect_delisted_flag(name: str) -> bool:
    return "退" in (name or "")


def _make_company_id(company_code: str) -> str:
    return f"CNINFO_{_normalize_code(company_code)}"


def _load_snapshot_enrichment(snapshot_dir: str) -> Dict[str, Dict[str, str]]:
    """按 company_code 加载 snapshot 身份 enrichment。"""
    result: Dict[str, Dict[str, str]] = {}
    if not os.path.isdir(snapshot_dir):
        return result
    for fname in os.listdir(snapshot_dir):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(snapshot_dir, fname)
        try:
            with open(path, encoding="utf-8") as f:
                snap = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        code = _normalize_code(snap.get("company_code") or fname.replace(".json", ""))
        identity = (snap.get("modules") or {}).get("company_identity", {}).get("fields") or {}
        securities = (snap.get("modules") or {}).get("securities_profile", {}).get("fields") or {}
        result[code] = {
            "company_full_name": str(identity.get("legal_name") or ""),
            "english_name": str(identity.get("english_name") or ""),
            "security_type": str(securities.get("security_type_code") or ""),
            "snapshot_status": str(snap.get("snapshot_status") or ""),
        }
    return result


def _load_snapshot_status_csv(path: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    if not os.path.isfile(path):
        return result
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = _normalize_code(row.get("company_code", ""))
            if code:
                result[code] = str(row.get("status") or "")
    return result


def _build_bse_legacy_map(legacy_companies: List[Dict[str, Any]]) -> Dict[str, str]:
    """legacy_code -> current_code（来自 duplicate_of 与策略文档）。"""
    mapping: Dict[str, str] = {}
    for entry in legacy_companies:
        legacy = _normalize_code(entry.get("stock_code", ""))
        duplicate_of = entry.get("duplicate_of")
        if duplicate_of:
            mapping[legacy] = _normalize_code(duplicate_of)
    for org_id, current in BSE_ORG_ID_LEGACY_TO_CURRENT.items():
        for entry in legacy_companies:
            if str(entry.get("orgid", "")) == org_id:
                mapping[_normalize_code(entry.get("stock_code", ""))] = _normalize_code(current)
    return mapping


def _build_bse_current_to_legacy(legacy_map: Dict[str, str]) -> Dict[str, str]:
    return {current: legacy for legacy, current in legacy_map.items()}


def _row_from_yaml_entry(
    entry: Dict[str, Any],
    source: str,
    *,
    hold_flag: bool = False,
    harvest_support_status: str = "unsupported",
    snapshot_support_status: str = "unsupported",
    confidence: str = "medium",
    active_status: str = "active",
    legacy_code: str = "",
    previous_code: str = "",
    notes: str = "",
) -> Dict[str, str]:
    code = _normalize_code(entry.get("stock_code", ""))
    name = _company_name_from_entry(entry)
    org_id = str(entry.get("orgid") or "")
    delisted = _detect_delisted_flag(name)
    listing = "delisted" if delisted else "listed"
    return {
        "company_id": _make_company_id(code),
        "company_code": code,
        "company_name": name,
        "company_full_name": "",
        "english_name": "",
        "exchange": str(entry.get("exchange") or ""),
        "board": str(entry.get("board") or ""),
        "security_type": "",
        "listing_status": listing,
        "active_status": active_status,
        "org_id": org_id,
        "legacy_code": legacy_code,
        "previous_code": previous_code,
        "rename_history": "[]",
        "org_id_conflict_flag": "false",
        "st_flag": "true" if _detect_st_flag(name) else "false",
        "delisted_flag": "true" if delisted else "false",
        "suspended_flag": "false",
        "hold_flag": "true" if hold_flag else "false",
        "harvest_support_status": harvest_support_status,
        "snapshot_support_status": snapshot_support_status,
        "source": source,
        "confidence": confidence,
        "notes": notes,
    }


def _apply_snapshot_enrichment(
    row: Dict[str, str],
    enrichment: Dict[str, Dict[str, str]],
    status_map: Dict[str, str],
) -> None:
    code = row["company_code"]
    snap = enrichment.get(code)
    if snap:
        if snap.get("company_full_name"):
            row["company_full_name"] = snap["company_full_name"]
        if snap.get("english_name"):
            row["english_name"] = snap["english_name"]
        if snap.get("security_type"):
            row["security_type"] = snap["security_type"]
        snap_status = snap.get("snapshot_status") or status_map.get(code, "")
        if snap_status and snap_status != "failed":
            row["snapshot_support_status"] = "completed_863"
            if row["source"] == "harvest_863_yaml":
                row["confidence"] = "high"
    elif status_map.get(code):
        if status_map[code] != "failed":
            row["snapshot_support_status"] = "completed_863"


def derive_registry_candidates(
    active_yaml: str = ACTIVE_YAML,
    hold_yaml: str = HOLD_YAML,
    bse_920_yaml: str = BSE_920_YAML,
    bse_legacy_yaml: str = BSE_LEGACY_YAML,
    full_market_yaml: str = FULL_MARKET_YAML,
    snapshot_dir: str = SNAPSHOT_DIR,
    snapshot_status_csv: str = SNAPSHOT_STATUS_CSV,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    """离线派生 registry candidate 行。"""
    enrichment = _load_snapshot_enrichment(snapshot_dir)
    status_map = _load_snapshot_status_csv(snapshot_status_csv)

    active_companies = _load_yaml_companies(active_yaml)
    hold_companies = _load_yaml_companies(hold_yaml)
    bse_920_companies = _load_yaml_companies(bse_920_yaml)
    bse_legacy_companies = _load_yaml_companies(bse_legacy_yaml)
    full_market_companies = _load_yaml_companies(full_market_yaml)

    legacy_to_current = _build_bse_legacy_map(bse_legacy_companies)
    current_to_legacy = _build_bse_current_to_legacy(legacy_to_current)

    rows_by_code: Dict[str, Dict[str, str]] = {}

    def _upsert(row: Dict[str, str]) -> None:
        code = row["company_code"]
        existing = rows_by_code.get(code)
        if existing is None:
            rows_by_code[code] = row
            return
        old_pri = SOURCE_PRIORITY.get(existing["source"], 0)
        new_pri = SOURCE_PRIORITY.get(row["source"], 0)
        if new_pri >= old_pri:
            rows_by_code[code] = row

    # 1. 863 active
    for entry in active_companies:
        row = _row_from_yaml_entry(
            entry,
            "harvest_863_yaml",
            harvest_support_status="completed_863",
            snapshot_support_status="unsupported",
            confidence="medium",
            active_status="active",
        )
        _apply_snapshot_enrichment(row, enrichment, status_map)
        _upsert(row)

    # 2. hold
    for entry in hold_companies:
        notes_parts = []
        if entry.get("hold_reason"):
            notes_parts.append(str(entry["hold_reason"]))
        if entry.get("notes"):
            notes_parts.append(str(entry["notes"]))
        if entry.get("failed_source_count") is not None:
            notes_parts.append(f"failed_source_count={entry['failed_source_count']}")
        row = _row_from_yaml_entry(
            entry,
            "hold_26_yaml",
            hold_flag=True,
            harvest_support_status="hold",
            snapshot_support_status="unsupported",
            confidence="medium",
            active_status="active",
            notes="; ".join(notes_parts),
        )
        _upsert(row)

    # 3. BSE 920
    for entry in bse_920_companies:
        code = _normalize_code(entry.get("stock_code", ""))
        legacy = current_to_legacy.get(code, "")
        row = _row_from_yaml_entry(
            entry,
            "bse_920_yaml",
            harvest_support_status="supported",
            snapshot_support_status="unsupported",
            confidence="medium",
            active_status="active",
            legacy_code=legacy,
            previous_code=legacy,
            notes="BSE 920 active candidate",
        )
        _upsert(row)

    # 4. BSE legacy
    for entry in bse_legacy_companies:
        code = _normalize_code(entry.get("stock_code", ""))
        duplicate_of = entry.get("duplicate_of")
        active_status = "duplicate_code" if duplicate_of else "legacy_code"
        notes_parts = [str(entry.get("hold_reason") or "legacy_code_incompatible")]
        if duplicate_of:
            notes_parts.append(f"duplicate_of={duplicate_of}")
        if entry.get("note"):
            notes_parts.append(str(entry["note"]))
        row = _row_from_yaml_entry(
            entry,
            "bse_legacy_yaml",
            hold_flag=True,
            harvest_support_status="unsupported",
            snapshot_support_status="unsupported",
            confidence="medium",
            active_status=active_status,
            legacy_code=code,
            notes="; ".join(notes_parts),
        )
        _upsert(row)

    # 5. Era B baseline 填充
    for entry in full_market_companies:
        code = _normalize_code(entry.get("stock_code", ""))
        if code in rows_by_code:
            continue
        row = _row_from_yaml_entry(
            entry,
            "full_market_2024",
            harvest_support_status="unsupported",
            snapshot_support_status="unsupported",
            confidence="low",
            active_status="active",
            notes="Era B baseline fill",
        )
        _upsert(row)

    # org_id 冲突检测（不自动合并）
    org_id_to_codes: Dict[str, Set[str]] = {}
    for row in rows_by_code.values():
        org_id = row.get("org_id", "")
        if not org_id:
            continue
        org_id_to_codes.setdefault(org_id, set()).add(row["company_code"])

    conflict_org_ids = {oid for oid, codes in org_id_to_codes.items() if len(codes) > 1}
    for row in rows_by_code.values():
        org_id = row.get("org_id", "")
        if org_id in conflict_org_ids:
            row["org_id_conflict_flag"] = "true"
            if not row.get("notes"):
                row["notes"] = "org_id conflict requires review"
            elif "org_id conflict" not in row["notes"]:
                row["notes"] = row["notes"] + "; org_id conflict requires review"

    candidates = sorted(rows_by_code.values(), key=lambda r: r["company_code"])

    stats = _compute_stats(
        candidates,
        active_count=len(active_companies),
        hold_count=len(hold_companies),
        bse_920_count=len(bse_920_companies),
        bse_legacy_count=len(bse_legacy_companies),
        full_market_count=len(full_market_companies),
        conflict_org_ids=conflict_org_ids,
    )
    return candidates, stats


def _compute_stats(
    candidates: List[Dict[str, str]],
    *,
    active_count: int,
    hold_count: int,
    bse_920_count: int,
    bse_legacy_count: int,
    full_market_count: int,
    conflict_org_ids: Set[str],
) -> Dict[str, Any]:
    confidence_dist = Counter(row["confidence"] for row in candidates)
    hold_rows = sum(1 for row in candidates if row["hold_flag"] == "true")
    legacy_rows = sum(
        1
        for row in candidates
        if row["legacy_code"] or row["active_status"] in ("legacy_code", "duplicate_code")
    )
    conflict_rows = sum(1 for row in candidates if row["org_id_conflict_flag"] == "true")
    source_dist = Counter(row["source"] for row in candidates)
    return {
        "candidate_count": len(candidates),
        "active_universe_count": active_count,
        "hold_universe_count": hold_count,
        "bse_universe_count": bse_920_count + bse_legacy_count,
        "bse_920_count": bse_920_count,
        "bse_legacy_count": bse_legacy_count,
        "era_b_baseline_count": full_market_count,
        "identity_conflict_count": len(conflict_org_ids),
        "identity_conflict_row_count": conflict_rows,
        "hold_row_count": hold_rows,
        "legacy_code_row_count": legacy_rows,
        "confidence_high": confidence_dist.get("high", 0),
        "confidence_medium": confidence_dist.get("medium", 0),
        "confidence_low": confidence_dist.get("low", 0),
        "source_distribution": dict(source_dist),
    }


def write_candidate_csv(path: str, candidates: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(candidates)


def write_summary_md(path: str, stats: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    source_lines = "\n".join(
        f"| `{k}` | {v} |"
        for k, v in sorted(stats.get("source_distribution", {}).items(), key=lambda x: -x[1])
    )
    content = f"""# CNINFO C-Class Company Registry Candidate Summary

_生成时间：{now}_

> **性质：** `company_registry_candidate` 离线派生摘要。**非 production registry**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## Universe

| 切片 | 输入规模 |
|------|----------|
| active universe（863 harvest） | **{stats['active_universe_count']}** |
| hold universe（26 all6 hold） | **{stats['hold_universe_count']}** |
| BSE universe（920 + legacy） | **{stats['bse_universe_count']}**（920={stats['bse_920_count']} · legacy={stats['bse_legacy_count']}） |
| Era B baseline（6124） | **{stats['era_b_baseline_count']}** |

---

## Candidate statistics

| 指标 | 值 |
|------|-----|
| candidate 行数 | **{stats['candidate_count']}** |
| identity conflict（org_id 组） | **{stats['identity_conflict_count']}** |
| identity conflict 行数 | **{stats['identity_conflict_row_count']}** |
| hold 行数 | **{stats['hold_row_count']}** |
| legacy code 相关行数 | **{stats['legacy_code_row_count']}** |

### source 分布

| source | 行数 |
|--------|------|
{source_lines}

---

## Confidence distribution

| confidence | 行数 |
|------------|------|
| high | **{stats['confidence_high']}** |
| medium | **{stats['confidence_medium']}** |
| low | **{stats['confidence_low']}** |

---

## Caveats

- rename_history 未填充（默认 `[]`）
- BSE legacy 映射未 probe 验证（仅文档与 YAML duplicate_of）
- org_id conflict 须人工 review（不自动合并）
- 无 CNINFO 在线 enrichment

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · 无 snapshot rebuild
- 未修改 raw / normalized / field_inventory / snapshot JSON
- 非 production registry · 不写 verified
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="离线派生 company_registry_candidate draft")
    parser.add_argument("--csv-out", default=DEFAULT_CSV_OUT)
    parser.add_argument("--summary-out", default=DEFAULT_SUMMARY_OUT)
    parser.add_argument("--active-yaml", default=ACTIVE_YAML)
    parser.add_argument("--hold-yaml", default=HOLD_YAML)
    parser.add_argument("--bse-920-yaml", default=BSE_920_YAML)
    parser.add_argument("--bse-legacy-yaml", default=BSE_LEGACY_YAML)
    parser.add_argument("--full-market-yaml", default=FULL_MARKET_YAML)
    parser.add_argument("--snapshot-dir", default=SNAPSHOT_DIR)
    parser.add_argument("--snapshot-status-csv", default=SNAPSHOT_STATUS_CSV)
    args = parser.parse_args()

    candidates, stats = derive_registry_candidates(
        active_yaml=args.active_yaml,
        hold_yaml=args.hold_yaml,
        bse_920_yaml=args.bse_920_yaml,
        bse_legacy_yaml=args.bse_legacy_yaml,
        full_market_yaml=args.full_market_yaml,
        snapshot_dir=args.snapshot_dir,
        snapshot_status_csv=args.snapshot_status_csv,
    )
    write_candidate_csv(args.csv_out, candidates)
    write_summary_md(args.summary_out, stats)

    print(f"candidate rows: {stats['candidate_count']}")
    print(f"conflicts: {stats['identity_conflict_count']}")
    print(f"hold rows: {stats['hold_row_count']}")
    print(f"csv: {args.csv_out}")
    print(f"summary: {args.summary_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
