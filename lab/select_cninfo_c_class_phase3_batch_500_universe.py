#!/usr/bin/env python3
"""
CNINFO C-class Phase 3 batch 500 universe 离线选股脚本。

从 refreshed candidate 分层抽取 500 家干净 matched_active 公司。
默认 dry-run · --write 才写入 YAML/matrix/summary · 无 CNINFO · 无 harvest。
"""

from __future__ import annotations

import argparse
import csv
import os
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REFRESHED_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_refreshed.csv"
)
PHASE2_MATRIX = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase2_smoke_200_selection_matrix.csv"
)
PHASE2_EXCLUDED_LEDGER = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase2_smoke_excluded_company_caveat_ledger.csv",
)

BATCH_YAML = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_phase3_batch_500_001.yaml"
)
MATRIX_OUT = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_matrix.csv",
)
SUMMARY_OUT = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_summary.md",
)

TARGET_SIZE = 500
SAMPLING_SEED = 20260709
BATCH_ID = "phase3_batch_500_001"

EXCLUDED_CLASSIFICATIONS = frozenset({
    "already_in_c_class",
    "matched_hold",
    "matched_bse_supported_candidate",
    "matched_bse_legacy_hold",
    "identity_conflict",
    "needs_manual_review",
    "not_found_in_cninfo",
})

MATRIX_COLUMNS = [
    "company_code",
    "company_name",
    "exchange",
    "board",
    "listing_status",
    "security_type",
    "source_universe",
    "reconciliation_classification",
    "refresh_action",
    "harvest_support_status",
    "snapshot_support_status",
    "requires_manual_review",
    "selection_bucket",
    "selection_reason",
    "batch_id",
]

STRATUM_FIELDS = ("exchange", "board", "listing_status", "security_type")


def _normalize_code(code: Any) -> str:
    text = str(code).strip()
    if text.isdigit():
        return text.zfill(6)
    return text


def _code_prefix(code: str) -> str:
    code = _normalize_code(code)
    if len(code) >= 3:
        return code[:3]
    return code


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _field_value(row: Dict[str, str], field: str) -> str:
    value = str(row.get(field, "")).strip()
    return value if value else "__MISSING__"


def _name_caveat(name: str) -> bool:
    if not name:
        return False
    return ("退" in name) or ("退市" in name) or ("*ST" in name)


def load_phase2_smoke_codes(path: str = PHASE2_MATRIX) -> Set[str]:
    rows = _load_csv(path)
    return {
        _normalize_code(r["company_code"])
        for r in rows
        if r.get("selection_reason") == "stratified_pick"
    }


def load_phase2_failure_codes(path: str = PHASE2_EXCLUDED_LEDGER) -> Set[str]:
    return {_normalize_code(r["company_code"]) for r in _load_csv(path)}


def load_already_in_c_class_codes(rows: List[Dict[str, str]]) -> Set[str]:
    return {
        _normalize_code(r["company_code"])
        for r in rows
        if r.get("reconciliation_classification") == "already_in_c_class"
    }


def _is_primary_pool(row: Dict[str, str]) -> bool:
    if row.get("reconciliation_classification") != "matched_active":
        return False
    if row.get("refresh_action") != "full_market_active_candidate":
        return False
    if row.get("harvest_support_status") != "candidate_supported":
        return False
    if row.get("snapshot_support_status") != "not_built":
        return False
    if str(row.get("requires_manual_review", "")).lower() == "true":
        return False
    if str(row.get("board", "")).strip().lower() == "bse":
        return False
    return True


def _exclusion_reason(
    row: Dict[str, str],
    phase2_smoke: Set[str],
    phase2_failure: Set[str],
    era_c_codes: Set[str],
) -> str:
    code = _normalize_code(row["company_code"])
    cls = row.get("reconciliation_classification", "")
    if cls in EXCLUDED_CLASSIFICATIONS:
        return f"excluded_{cls}"
    if code in era_c_codes:
        return "excluded_already_in_c_class"
    if code in phase2_smoke:
        return "excluded_phase2_smoke_200"
    if code in phase2_failure:
        return "excluded_phase2_all_direct_failure"
    if str(row.get("listing_status", "")).strip().lower() == "delisted":
        return "excluded_delisted"
    if _name_caveat(row.get("company_name", "")):
        return "excluded_delisted_or_inactive_caveat_name"
    if str(row.get("board", "")).strip().lower() == "bse":
        return "excluded_board_bse"
    if not _is_primary_pool(row):
        return f"excluded_{cls or 'ineligible'}"
    return ""


def _is_eligible_main_batch(
    row: Dict[str, str],
    phase2_smoke: Set[str],
    phase2_failure: Set[str],
    era_c_codes: Set[str],
) -> bool:
    if not _is_primary_pool(row):
        return False
    code = _normalize_code(row["company_code"])
    if code in phase2_smoke or code in phase2_failure or code in era_c_codes:
        return False
    if str(row.get("listing_status", "")).strip().lower() == "delisted":
        return False
    if _name_caveat(row.get("company_name", "")):
        return False
    if row.get("reconciliation_classification") in EXCLUDED_CLASSIFICATIONS:
        return False
    return True


def _stratum_key(row: Dict[str, str]) -> str:
    parts = [_field_value(row, f) for f in STRATUM_FIELDS]
    if all(p == "__MISSING__" for p in parts):
        return f"prefix_{_code_prefix(row.get('company_code', ''))}"
    return "|".join(parts)


def _allocate_quotas(strata: Dict[str, List[Dict[str, str]]], target: int) -> Dict[str, int]:
    total = sum(len(v) for v in strata.values())
    if total < target:
        raise ValueError(f"eligible pool {total} < target {target}")

    raw = {k: len(v) / total * target for k, v in strata.items()}
    quotas = {k: int(raw[k]) for k in raw}
    remainder = target - sum(quotas.values())

    ranked = sorted(raw.keys(), key=lambda k: (raw[k] - quotas[k]), reverse=True)
    for key in ranked:
        if remainder <= 0:
            break
        if quotas[key] < len(strata[key]):
            quotas[key] += 1
            remainder -= 1

    while sum(quotas.values()) < target:
        for key in sorted(strata.keys(), key=lambda k: len(strata[k]) - quotas[k], reverse=True):
            if quotas[key] < len(strata[key]):
                quotas[key] += 1
                if sum(quotas.values()) >= target:
                    break

    while sum(quotas.values()) > target:
        key = max(quotas.keys(), key=lambda k: quotas[k])
        if quotas[key] > 0:
            quotas[key] -= 1

    assert sum(quotas.values()) == target
    return quotas


def _pick_from_stratum(
    rows: List[Dict[str, str]], quota: int, seed: int, stratum: str
) -> List[Dict[str, str]]:
    ordered = sorted(rows, key=lambda r: _normalize_code(r["company_code"]))
    rng = random.Random(seed + hash(stratum) % 1_000_000)
    shuffled = ordered[:]
    rng.shuffle(shuffled)
    return shuffled[:quota]


def _dedupe_eligible(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """按 company_code / company_id 去重，保留首行。"""
    seen_codes: Set[str] = set()
    seen_ids: Set[str] = set()
    out: List[Dict[str, str]] = []
    for row in sorted(rows, key=lambda r: _normalize_code(r["company_code"])):
        code = _normalize_code(row["company_code"])
        cid = str(row.get("company_id", "")).strip()
        if code in seen_codes:
            continue
        if cid and cid in seen_ids:
            continue
        seen_codes.add(code)
        if cid:
            seen_ids.add(cid)
        out.append(row)
    return out


def _count_exclusions(
    all_rows: List[Dict[str, str]],
    phase2_smoke: Set[str],
    phase2_failure: Set[str],
    era_c_codes: Set[str],
) -> Dict[str, int]:
    primary = [r for r in all_rows if _is_primary_pool(r)]
    delisted_caveat = [
        r for r in primary
        if str(r.get("listing_status", "")).strip().lower() == "delisted"
        or _name_caveat(r.get("company_name", ""))
    ]
    return {
        "already_in_c_class": sum(
            1 for r in all_rows if r.get("reconciliation_classification") == "already_in_c_class"
        ),
        "phase2_smoke_200": len(phase2_smoke),
        "phase2_all_direct_failure": len(phase2_failure),
        "delisted_or_inactive_caveat_in_primary": len(delisted_caveat),
        "matched_hold": sum(
            1 for r in all_rows if r.get("reconciliation_classification") == "matched_hold"
        ),
        "matched_bse_supported_candidate": sum(
            1 for r in all_rows
            if r.get("reconciliation_classification") == "matched_bse_supported_candidate"
        ),
        "matched_bse_legacy_hold": sum(
            1 for r in all_rows
            if r.get("reconciliation_classification") == "matched_bse_legacy_hold"
        ),
        "identity_conflict": sum(
            1 for r in all_rows if r.get("reconciliation_classification") == "identity_conflict"
        ),
        "needs_manual_review": sum(
            1 for r in all_rows if r.get("reconciliation_classification") == "needs_manual_review"
        ),
        "bse_in_matched_active": sum(
            1 for r in all_rows
            if r.get("reconciliation_classification") == "matched_active"
            and str(r.get("board", "")).strip().lower() == "bse"
        ),
    }


def select_batch_500_universe(
    refreshed_csv: str = REFRESHED_CSV,
    phase2_matrix: str = PHASE2_MATRIX,
    phase2_ledger: str = PHASE2_EXCLUDED_LEDGER,
    target_size: int = TARGET_SIZE,
    seed: int = SAMPLING_SEED,
    batch_id: str = BATCH_ID,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], Dict[str, Any]]:
    all_rows = _load_csv(refreshed_csv)
    phase2_smoke = load_phase2_smoke_codes(phase2_matrix)
    phase2_failure = load_phase2_failure_codes(phase2_ledger)
    era_c_codes = load_already_in_c_class_codes(all_rows)

    refreshed_count = len(all_rows)
    primary_pool = [r for r in all_rows if _is_primary_pool(r)]

    eligible_raw = [
        r for r in all_rows
        if _is_eligible_main_batch(r, phase2_smoke, phase2_failure, era_c_codes)
    ]
    eligible = _dedupe_eligible(eligible_raw)

    strata: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in eligible:
        strata[_stratum_key(row)].append(row)

    quotas = _allocate_quotas(strata, target_size)
    selected: List[Dict[str, str]] = []
    selected_codes: Set[str] = set()

    for stratum, quota in sorted(quotas.items()):
        picks = _pick_from_stratum(strata[stratum], quota, seed, stratum)
        for row in picks:
            code = _normalize_code(row["company_code"])
            if code in selected_codes:
                raise ValueError(f"duplicate selection: {code}")
            selected_codes.add(code)
            selected.append(row)

    if len(selected) != target_size:
        raise ValueError(f"selected {len(selected)} != target {target_size}")

    ids = [r.get("company_id", "") for r in selected if r.get("company_id")]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate company_id in selection")

    matrix_rows: List[Dict[str, str]] = []
    for row in all_rows:
        code = _normalize_code(row["company_code"])
        if code in selected_codes:
            reason = "stratified_pick"
            bucket = _stratum_key(row)
            bid = batch_id
        else:
            reason = _exclusion_reason(row, phase2_smoke, phase2_failure, era_c_codes)
            if not reason and _is_primary_pool(row):
                reason = "pool_not_selected"
            elif not reason:
                reason = f"excluded_{row.get('reconciliation_classification', 'unknown')}"
            bucket = _stratum_key(row) if _is_eligible_main_batch(
                row, phase2_smoke, phase2_failure, era_c_codes
            ) else "ineligible"
            bid = ""

        matrix_rows.append({
            "company_code": code,
            "company_name": row.get("company_name", ""),
            "exchange": row.get("exchange", ""),
            "board": row.get("board", ""),
            "listing_status": row.get("listing_status", ""),
            "security_type": row.get("security_type", ""),
            "source_universe": row.get("source", ""),
            "reconciliation_classification": row.get("reconciliation_classification", ""),
            "refresh_action": row.get("refresh_action", ""),
            "harvest_support_status": row.get("harvest_support_status", ""),
            "snapshot_support_status": row.get("snapshot_support_status", ""),
            "requires_manual_review": row.get("requires_manual_review", ""),
            "selection_bucket": bucket,
            "selection_reason": reason,
            "batch_id": bid,
        })

    stats: Dict[str, Any] = {
        "refreshed_candidate_count": refreshed_count,
        "primary_pool_count": len(primary_pool),
        "eligible_after_exclusions_count": len(eligible),
        "target_size": target_size,
        "selected_count": len(selected),
        "seed": seed,
        "batch_id": batch_id,
        "selected_codes": sorted(selected_codes),
        "phase2_smoke_codes": sorted(phase2_smoke),
        "phase2_failure_codes": sorted(phase2_failure),
        "era_c_codes": sorted(era_c_codes),
        "exchange_dist": dict(Counter(r.get("exchange", "") for r in selected)),
        "board_dist": dict(Counter(r.get("board", "") for r in selected)),
        "listing_status_dist": dict(Counter(r.get("listing_status", "") for r in selected)),
        "security_type_dist": dict(Counter(_field_value(r, "security_type") for r in selected)),
        "prefix_dist": dict(Counter(_code_prefix(r["company_code"]) for r in selected)),
        "exclusion_counts": _count_exclusions(all_rows, phase2_smoke, phase2_failure, era_c_codes),
        "exclusion_check": _exclusion_check(
            selected, phase2_smoke, phase2_failure, era_c_codes
        ),
    }
    return selected, matrix_rows, stats


def _exclusion_check(
    selected: List[Dict[str, str]],
    phase2_smoke: Set[str],
    phase2_failure: Set[str],
    era_c_codes: Set[str],
) -> Dict[str, int]:
    codes = {_normalize_code(r["company_code"]) for r in selected}
    name_caveat_count = sum(1 for r in selected if _name_caveat(r.get("company_name", "")))
    delisted_count = sum(
        1 for r in selected if str(r.get("listing_status", "")).strip().lower() == "delisted"
    )
    return {
        "already_in_c_class_included": len(codes & era_c_codes),
        "phase2_smoke_included": len(codes & phase2_smoke),
        "phase2_failure_included": len(codes & phase2_failure),
        "delisted_included": delisted_count,
        "name_caveat_included": name_caveat_count,
        "bse_included": sum(1 for r in selected if str(r.get("board", "")).lower() == "bse"),
        "hold_included": sum(
            1 for r in selected if r.get("reconciliation_classification") == "matched_hold"
        ),
        "identity_conflict_included": sum(
            1 for r in selected if r.get("reconciliation_classification") == "identity_conflict"
        ),
        "manual_review_included": sum(
            1 for r in selected
            if r.get("reconciliation_classification") == "needs_manual_review"
            or str(r.get("requires_manual_review", "")).lower() == "true"
        ),
        "duplicate_company_code": len(selected) - len(codes),
    }


def write_batch_yaml(
    selected: List[Dict[str, str]],
    stats: Dict[str, Any],
    path: str = BATCH_YAML,
) -> None:
    board_counts = dict(Counter(r.get("board", "") for r in selected))
    companies = []
    for row in sorted(selected, key=lambda r: _normalize_code(r["company_code"])):
        code = _normalize_code(row["company_code"])
        name = row.get("company_name", "")
        companies.append({
            "stock_code": code,
            "short_name": name,
            "company_name": name,
            "company_code": code,
            "exchange": row.get("exchange", ""),
            "orgid": row.get("org_id", ""),
            "board": row.get("board", ""),
            "source_universe": row.get("source", ""),
            "reconciliation_classification": row.get("reconciliation_classification", ""),
            "refresh_action": row.get("refresh_action", ""),
            "listing_status": row.get("listing_status", ""),
            "batch_id": stats["batch_id"],
            "harvest_status": "phase3_batch_500_candidate",
        })

    payload = {
        "version": "c-class-phase3-batch-500-001-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "parent_pool": "outputs/validation/cninfo_c_class_company_registry_candidate_refreshed.csv",
        "universe_id": stats["batch_id"],
        "batch_id": stats["batch_id"],
        "description": "Phase 3 batch 500 · matched_active stratified sample · Phase 2 exclusions applied",
        "company_count": len(companies),
        "sampling_seed": stats["seed"],
        "sampling_strategy": "stratified_exchange_board_listing_status_security_type",
        "board_counts": board_counts,
        "companies": companies,
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=False)


def write_matrix(rows: List[Dict[str, str]], path: str = MATRIX_OUT) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MATRIX_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _dist_table(dist: Dict[str, int]) -> str:
    lines = ["| 值 | count |", "|-----|-------|"]
    for k, v in sorted(dist.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| {k or '(empty)'} | **{v}** |")
    return "\n".join(lines)


def write_summary(stats: Dict[str, Any], path: str = SUMMARY_OUT) -> None:
    exc = stats["exclusion_check"]
    excl = stats["exclusion_counts"]
    content = f"""# CNINFO C-Class Phase 3 Batch 500 Selection Summary

_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_

> Phase 3 batch 500 universe 离线选股摘要。**无 CNINFO** · **harvest not started**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Input Pool

| 指标 | count |
|------|-------|
| refreshed_candidate_count | **{stats['refreshed_candidate_count']}** |
| primary_pool_count | **{stats['primary_pool_count']}** |
| eligible_after_exclusions_count | **{stats['eligible_after_exclusions_count']}** |

---

# Exclusions

| 类别 | count |
|------|-------|
| already_in_c_class | **{excl['already_in_c_class']}** |
| phase2_smoke_200 | **{excl['phase2_smoke_200']}** |
| phase2_all_direct_failure | **{excl['phase2_all_direct_failure']}** |
| delisted_or_inactive_caveat (in primary) | **{excl['delisted_or_inactive_caveat_in_primary']}** |
| matched_hold | **{excl['matched_hold']}** |
| matched_bse_supported_candidate | **{excl['matched_bse_supported_candidate']}** |
| matched_bse_legacy_hold | **{excl['matched_bse_legacy_hold']}** |
| identity_conflict | **{excl['identity_conflict']}** |
| needs_manual_review | **{excl['needs_manual_review']}** |
| BSE in matched_active | **{excl['bse_in_matched_active']}** |

---

# Selection

| 项 | 值 |
|----|-----|
| target_size | **{stats['target_size']}** |
| selected_count | **{stats['selected_count']}** |
| seed | **{stats['seed']}** |
| batch_id | **{stats['batch_id']}** |

---

# Distribution

## exchange

{_dist_table(stats['exchange_dist'])}

## board

{_dist_table(stats['board_dist'])}

## listing_status

{_dist_table(stats['listing_status_dist'])}

## security_type

{_dist_table(stats['security_type_dist'])}

## company_code_prefix

{_dist_table(stats['prefix_dist'])}

---

# Exclusion Check

| 检查项 | count |
|--------|-------|
| already_in_c_class included | **{exc['already_in_c_class_included']}** |
| phase2_smoke included | **{exc['phase2_smoke_included']}** |
| phase2_failure included | **{exc['phase2_failure_included']}** |
| delisted included | **{exc['delisted_included']}** |
| 退 / 退市 / *ST included | **{exc['name_caveat_included']}** |
| BSE included | **{exc['bse_included']}** |
| hold included | **{exc['hold_included']}** |
| identity_conflict included | **{exc['identity_conflict_included']}** |
| manual_review included | **{exc['manual_review_included']}** |
| duplicate company_code | **{exc['duplicate_company_code']}** |

---

# Expected Future Harvest Size

**500 companies × 7 live source calls = 3500 planned cases**

Security source remains observe-only.

---

# Gate

**`phase3_batch_500_001_universe_selection_gate = PASS`**

---

# Execution Status

Harvest not started.

Snapshot not started.

---

# 产物

- [batch YAML](../../lab/eval_companies_c_class_phase3_batch_500_001.yaml)
- [selection matrix](cninfo_c_class_phase3_batch_500_001_selection_matrix.csv)
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CNINFO C-class Phase 3 batch 500 universe 离线选股（默认 dry-run）"
    )
    parser.add_argument("--write", action="store_true", help="写入 YAML / matrix / summary")
    parser.add_argument("--refreshed", default=REFRESHED_CSV)
    parser.add_argument("--phase2-matrix", default=PHASE2_MATRIX)
    parser.add_argument("--phase2-ledger", default=PHASE2_EXCLUDED_LEDGER)
    parser.add_argument("--target-size", type=int, default=TARGET_SIZE)
    parser.add_argument("--seed", type=int, default=SAMPLING_SEED)
    parser.add_argument("--batch-id", default=BATCH_ID)
    parser.add_argument("--yaml-out", default=BATCH_YAML)
    parser.add_argument("--matrix-out", default=MATRIX_OUT)
    parser.add_argument("--summary-out", default=SUMMARY_OUT)
    args = parser.parse_args()

    selected, matrix_rows, stats = select_batch_500_universe(
        refreshed_csv=args.refreshed,
        phase2_matrix=args.phase2_matrix,
        phase2_ledger=args.phase2_ledger,
        target_size=args.target_size,
        seed=args.seed,
        batch_id=args.batch_id,
    )

    print(f"primary_pool={stats['primary_pool_count']}")
    print(f"eligible_after_exclusions={stats['eligible_after_exclusions_count']}")
    print(f"selected={stats['selected_count']}")
    print(f"seed={stats['seed']}")
    print(f"batch_id={stats['batch_id']}")
    print(f"exchange={stats['exchange_dist']}")
    print(f"board={stats['board_dist']}")

    if args.write:
        write_batch_yaml(selected, stats, args.yaml_out)
        write_matrix(matrix_rows, args.matrix_out)
        write_summary(stats, args.summary_out)
        print(f"wrote {args.yaml_out}")
        print(f"wrote {args.matrix_out}")
        print(f"wrote {args.summary_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
