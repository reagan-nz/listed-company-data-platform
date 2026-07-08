#!/usr/bin/env python3
"""
CNINFO C-class Phase 2 expansion smoke universe 离线选股脚本。

从 refreshed candidate 分层抽取 200 家 matched_active 公司。
默认 dry-run · --write 才写入 YAML/matrix/summary · 无 CNINFO · 无 harvest。
"""

from __future__ import annotations

import argparse
import csv
import os
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REFRESHED_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_refreshed.csv"
)
SMOKE_YAML = os.path.join(BASE_DIR, "lab/eval_companies_c_class_phase2_smoke_200.yaml")
MATRIX_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase2_smoke_200_selection_matrix.csv"
)
SUMMARY_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_phase2_smoke_200_selection_summary.md"
)

TARGET_SIZE = 200
SAMPLING_SEED = 20260708

EXCLUDED_CLASSIFICATIONS = {
    "already_in_c_class",
    "matched_hold",
    "matched_bse_supported_candidate",
    "matched_bse_legacy_hold",
    "identity_conflict",
    "needs_manual_review",
    "not_found_in_cninfo",
}

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


def _is_eligible_base(row: Dict[str, str]) -> bool:
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
    if row.get("reconciliation_classification") in EXCLUDED_CLASSIFICATIONS:
        return False
    return True


def _is_eligible_non_bse(row: Dict[str, str]) -> bool:
    if not _is_eligible_base(row):
        return False
    if str(row.get("board", "")).strip().lower() == "bse":
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

    # 最大余数法补齐
    ranked = sorted(raw.keys(), key=lambda k: (raw[k] - quotas[k]), reverse=True)
    for key in ranked:
        if remainder <= 0:
            break
        if quotas[key] < len(strata[key]):
            quotas[key] += 1
            remainder -= 1

    # 若仍不足（极小 strata 被截断为 0），从有余量的 strata 借
    while sum(quotas.values()) < target:
        for key in sorted(strata.keys(), key=lambda k: len(strata[k]) - quotas[k], reverse=True):
            if quotas[key] < len(strata[key]):
                quotas[key] += 1
                if sum(quotas.values()) >= target:
                    break

    # 若超出，从最大 quota 减
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


def select_smoke_universe(
    refreshed_csv: str = REFRESHED_CSV,
    target_size: int = TARGET_SIZE,
    seed: int = SAMPLING_SEED,
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]], Dict[str, Any]]:
    all_rows = _load_csv(refreshed_csv)
    refreshed_count = len(all_rows)
    matched_active_count = sum(
        1 for r in all_rows if r.get("reconciliation_classification") == "matched_active"
    )

    eligible_base = [r for r in all_rows if _is_eligible_base(r)]
    eligible_non_bse = [r for r in eligible_base if str(r.get("board", "")).lower() != "bse"]
    bse_excluded = [r for r in eligible_base if str(r.get("board", "")).lower() == "bse"]

    strata: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in eligible_non_bse:
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

    # 去重 company_id
    ids = [r.get("company_id", "") for r in selected if r.get("company_id")]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate company_id in selection")

    matrix_rows: List[Dict[str, str]] = []
    selected_set = selected_codes

    for row in all_rows:
        code = _normalize_code(row["company_code"])
        bucket = _stratum_key(row) if _is_eligible_non_bse(row) else "ineligible"
        if code in selected_set:
            reason = "stratified_pick"
        elif str(row.get("board", "")).lower() == "bse" and _is_eligible_base(row):
            reason = "excluded_board_bse"
        elif not _is_eligible_base(row):
            reason = f"excluded_{row.get('reconciliation_classification', 'unknown')}"
        else:
            reason = "pool_not_selected"

        matrix_rows.append(
            {
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
            }
        )

    stats: Dict[str, Any] = {
        "refreshed_candidate_count": refreshed_count,
        "matched_active_count": matched_active_count,
        "eligible_before_bse_exclusion": len(eligible_base),
        "eligible_non_bse_count": len(eligible_non_bse),
        "bse_excluded_count": len(bse_excluded),
        "target_size": target_size,
        "selected_count": len(selected),
        "seed": seed,
        "selected_codes": sorted(selected_codes),
        "exchange_dist": dict(Counter(r.get("exchange", "") for r in selected)),
        "board_dist": dict(Counter(r.get("board", "") for r in selected)),
        "listing_status_dist": dict(Counter(r.get("listing_status", "") for r in selected)),
        "security_type_dist": dict(Counter(_field_value(r, "security_type") for r in selected)),
        "prefix_dist": dict(Counter(_code_prefix(r["company_code"]) for r in selected)),
        "exclusion_check": _exclusion_check(selected, all_rows),
    }
    return selected, matrix_rows, stats


def _exclusion_check(selected: List[Dict[str, str]], all_rows: List[Dict[str, str]]) -> Dict[str, int]:
    codes = {_normalize_code(r["company_code"]) for r in selected}
    era_c = sum(1 for c in codes if any(
        _normalize_code(r["company_code"]) == c
        and r.get("reconciliation_classification") == "already_in_c_class"
        for r in all_rows
    ))
    return {
        "already_in_c_class_included": sum(
            1 for r in selected if r.get("reconciliation_classification") == "already_in_c_class"
        ),
        "hold_included": sum(
            1 for r in selected if r.get("reconciliation_classification") == "matched_hold"
        ),
        "bse_included": sum(1 for r in selected if str(r.get("board", "")).lower() == "bse"),
        "identity_conflict_included": sum(
            1 for r in selected if r.get("reconciliation_classification") == "identity_conflict"
        ),
        "manual_review_included": sum(
            1 for r in selected
            if r.get("reconciliation_classification") == "needs_manual_review"
            or str(r.get("requires_manual_review", "")).lower() == "true"
        ),
        "duplicate_company_code": len(selected) - len({_normalize_code(r["company_code"]) for r in selected}),
    }


def write_smoke_yaml(
    selected: List[Dict[str, str]],
    stats: Dict[str, Any],
    path: str = SMOKE_YAML,
) -> None:
    board_counts = dict(Counter(r.get("board", "") for r in selected))
    companies = []
    for row in sorted(selected, key=lambda r: _normalize_code(r["company_code"])):
        code = _normalize_code(row["company_code"])
        name = row.get("company_name", "")
        companies.append(
            {
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
                "harvest_status": "phase2_smoke_candidate",
            }
        )

    payload = {
        "version": "c-class-phase2-smoke-200-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "parent_pool": "outputs/validation/cninfo_c_class_company_registry_candidate_refreshed.csv",
        "universe_id": "phase2_smoke_200_non_bse",
        "description": "Phase 2 expansion smoke · matched_active stratified sample · non-BSE",
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
    content = f"""# CNINFO C-Class Phase 2 Smoke 200 Selection Summary

_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_

> Phase 2 smoke universe 离线选股摘要。**无 CNINFO** · **harvest not started**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Input Pool

| 指标 | count |
|------|-------|
| refreshed_candidate_count | **{stats['refreshed_candidate_count']}** |
| matched_active_count | **{stats['matched_active_count']}** |
| eligible_non_bse_count | **{stats['eligible_non_bse_count']}** |
| eligible_before_bse_exclusion | **{stats['eligible_before_bse_exclusion']}** |
| bse_excluded_from_pool | **{stats['bse_excluded_count']}** |

---

# Selection

| 项 | 值 |
|----|-----|
| target_size | **{stats['target_size']}** |
| selected_count | **{stats['selected_count']}** |
| seed | **{stats['seed']}** |

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
| hold included | **{exc['hold_included']}** |
| BSE included | **{exc['bse_included']}** |
| identity_conflict included | **{exc['identity_conflict_included']}** |
| manual_review included | **{exc['manual_review_included']}** |
| duplicate company_code | **{exc['duplicate_company_code']}** |

---

# Expected Future Harvest Size

**200 companies × 7 live source calls = 1400 planned cases**

Security source remains observe-only.

---

# Gate

**`phase2_smoke_universe_selection_gate = PASS`**

---

# Execution Status

Harvest not started.

Snapshot not started.

---

# 产物

- [smoke YAML](../../lab/eval_companies_c_class_phase2_smoke_200.yaml)
- [selection matrix](cninfo_c_class_phase2_smoke_200_selection_matrix.csv)
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CNINFO C-class Phase 2 smoke universe 离线选股（默认 dry-run）"
    )
    parser.add_argument("--write", action="store_true", help="写入 YAML / matrix / summary")
    parser.add_argument("--refreshed", default=REFRESHED_CSV)
    parser.add_argument("--target-size", type=int, default=TARGET_SIZE)
    parser.add_argument("--seed", type=int, default=SAMPLING_SEED)
    parser.add_argument("--yaml-out", default=SMOKE_YAML)
    parser.add_argument("--matrix-out", default=MATRIX_OUT)
    parser.add_argument("--summary-out", default=SUMMARY_OUT)
    args = parser.parse_args()

    selected, matrix_rows, stats = select_smoke_universe(
        refreshed_csv=args.refreshed,
        target_size=args.target_size,
        seed=args.seed,
    )

    print(f"eligible_non_bse={stats['eligible_non_bse_count']}")
    print(f"selected={stats['selected_count']}")
    print(f"seed={stats['seed']}")
    print(f"exchange={stats['exchange_dist']}")
    print(f"board={stats['board_dist']}")

    if args.write:
        write_smoke_yaml(selected, stats, args.yaml_out)
        write_matrix(matrix_rows, args.matrix_out)
        write_summary(stats, args.summary_out)
        print(f"wrote {args.yaml_out}")
        print(f"wrote {args.matrix_out}")
        print(f"wrote {args.summary_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
