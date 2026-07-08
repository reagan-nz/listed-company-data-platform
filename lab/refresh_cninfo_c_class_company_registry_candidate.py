#!/usr/bin/env python3
"""
CNINFO C-class company_registry_candidate 离线 refresh 脚本。

基于 Phase 0 reconciliation 结果刷新 candidate 元数据层。
默认 dry-run · --write 才写入产物 · 无 CNINFO · 无 merge。
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CANDIDATE_DRAFT_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_draft.csv"
)
RECONCILIATION_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_full_market_universe_reconciliation_result.csv"
)
LEDGER_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_identity_decision_ledger.csv"
)
ACTION_MATRIX_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_candidate_refresh_action_matrix.csv"
)

REFRESHED_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_refreshed.csv"
)
SUMMARY_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_refresh_summary.md"
)

BASE_COLUMNS = [
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

EXTENSION_COLUMNS = [
    "reconciliation_classification",
    "refresh_action",
    "refresh_confidence",
    "requires_manual_review",
    "lineage_note",
]

OUTPUT_COLUMNS = BASE_COLUMNS + EXTENSION_COLUMNS

# classification → refresh 规则（与 action matrix 一致）
REFRESH_RULES: Dict[str, Dict[str, Any]] = {
    "matched_active": {
        "refresh_action": "full_market_active_candidate",
        "refresh_confidence": "low",
        "requires_manual_review": "false",
        "harvest_support_status": "candidate_supported",
        "snapshot_support_status": "not_built",
        "hold_flag": "false",
    },
    "already_in_c_class": {
        "refresh_action": "preserve_high_confidence",
        "refresh_confidence": "high",
        "requires_manual_review": "false",
        "harvest_support_status": "supported",
        "snapshot_support_status": "supported",
        "hold_flag": "false",
    },
    "matched_hold": {
        "refresh_action": "preserve_hold",
        "refresh_confidence": "medium",
        "requires_manual_review": "false",
        "harvest_support_status": "hold",
        "snapshot_support_status": "hold",
        "hold_flag": "true",
    },
    "matched_bse_supported_candidate": {
        "refresh_action": "bse_supported_candidate",
        "refresh_confidence": "medium",
        "requires_manual_review": "false",
        "harvest_support_status": "candidate_supported",
        "snapshot_support_status": "not_built",
        "hold_flag": "false",
    },
    "matched_bse_legacy_hold": {
        "refresh_action": "preserve_legacy_hold",
        "refresh_confidence": "medium",
        "requires_manual_review": "false",
        "harvest_support_status": "legacy_hold",
        "snapshot_support_status": "hold",
        "hold_flag": "false",
    },
    "identity_conflict": {
        "refresh_action": "conflict_review_required",
        "refresh_confidence": "review",
        "requires_manual_review": "true",
        "harvest_support_status": "manual_review",
        "snapshot_support_status": "manual_review",
        "hold_flag": "false",
    },
    "needs_manual_review": {
        "refresh_action": "manual_review_required",
        "refresh_confidence": "review",
        "requires_manual_review": "true",
        "harvest_support_status": "manual_review",
        "snapshot_support_status": "manual_review",
        "hold_flag": "false",
    },
    "not_found_in_cninfo": {
        "refresh_action": "exclude_unresolved",
        "refresh_confidence": "low",
        "requires_manual_review": "true",
        "harvest_support_status": "unsupported_unknown",
        "snapshot_support_status": "not_built",
        "hold_flag": "false",
    },
}


def _normalize_code(code: Any) -> str:
    text = str(code).strip()
    if text.isdigit():
        return text.zfill(6)
    return text


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _bool_str(value: bool) -> str:
    return "true" if value else "false"


def load_action_matrix(path: str = ACTION_MATRIX_CSV) -> Dict[str, Dict[str, str]]:
    """从 action matrix CSV 加载并校验与内置规则一致。"""
    rows = _load_csv(path)
    matrix = {r["classification"]: r for r in rows}
    for cls, rule in REFRESH_RULES.items():
        if cls not in matrix:
            continue
        row = matrix[cls]
        assert row["refresh_action"] == rule["refresh_action"]
        assert row["confidence_after_refresh"] == rule["refresh_confidence"]
    return matrix


def build_reconciliation_index(
    reconciliation_rows: List[Dict[str, str]],
) -> Dict[str, Dict[str, str]]:
    index: Dict[str, Dict[str, str]] = {}
    for row in reconciliation_rows:
        code = _normalize_code(row["company_code"])
        index[code] = row
    return index


def refresh_candidate_row(
    draft_row: Dict[str, str],
    recon_row: Dict[str, str],
) -> Dict[str, str]:
    classification = recon_row.get("classification", "")
    if classification not in REFRESH_RULES:
        raise ValueError(f"未知 reconciliation classification: {classification}")

    rule = REFRESH_RULES[classification]
    out = dict(draft_row)

    out["confidence"] = rule["refresh_confidence"]
    out["harvest_support_status"] = rule["harvest_support_status"]
    out["snapshot_support_status"] = rule["snapshot_support_status"]
    out["hold_flag"] = rule["hold_flag"]

    # already_in_c_class 保持 completed_863 语义
    if classification == "already_in_c_class":
        if out.get("source") == "harvest_863_yaml":
            out["notes"] = (out.get("notes") or "").strip()
        else:
            out["source"] = "harvest_863_yaml"
        out["harvest_support_status"] = "supported"
        out["snapshot_support_status"] = "supported"

    lineage = (
        f"recon={recon_row.get('reconciliation_id', '')}; "
        f"classification={classification}; "
        f"merge_executed=false; "
        f"{recon_row.get('notes', '')}"
    ).strip()

    out["reconciliation_classification"] = classification
    out["refresh_action"] = rule["refresh_action"]
    out["refresh_confidence"] = rule["refresh_confidence"]
    out["requires_manual_review"] = rule["requires_manual_review"]
    out["lineage_note"] = lineage

    return out


def refresh_candidates(
    candidate_draft_csv: str = CANDIDATE_DRAFT_CSV,
    reconciliation_csv: str = RECONCILIATION_CSV,
    ledger_csv: str = LEDGER_CSV,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    load_action_matrix()

    draft_rows = _load_csv(candidate_draft_csv)
    recon_rows = _load_csv(reconciliation_csv)
    ledger_rows = _load_csv(ledger_csv)
    recon_index = build_reconciliation_index(recon_rows)

    refreshed: List[Dict[str, str]] = []
    missing_recon: List[str] = []

    for draft in draft_rows:
        code = _normalize_code(draft["company_code"])
        recon = recon_index.get(code)
        if recon is None:
            missing_recon.append(code)
            recon = {
                "reconciliation_id": "",
                "classification": "not_found_in_cninfo",
                "notes": "reconciliation 无对应行",
            }
        refreshed.append(refresh_candidate_row(draft, recon))

    stats: Dict[str, Any] = {
        "candidate_draft_count": len(draft_rows),
        "reconciliation_result_count": len(recon_rows),
        "identity_decision_count": len(ledger_rows),
        "refreshed_count": len(refreshed),
        "missing_reconciliation_count": len(missing_recon),
        "classification_counts": dict(
            Counter(r["reconciliation_classification"] for r in refreshed)
        ),
        "refresh_action_counts": dict(Counter(r["refresh_action"] for r in refreshed)),
        "refresh_confidence_counts": dict(
            Counter(r["refresh_confidence"] for r in refreshed)
        ),
        "manual_review_required_count": sum(
            1 for r in refreshed if r["requires_manual_review"] == "true"
        ),
    }
    return refreshed, stats


def write_refreshed_csv(rows: List[Dict[str, str]], path: str = REFRESHED_OUT) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(stats: Dict[str, Any], path: str = SUMMARY_OUT) -> None:
    cls_lines = "\n".join(
        f"| {k} | **{stats['classification_counts'].get(k, 0)}** |"
        for k in REFRESH_RULES
    )
    action_lines = "\n".join(
        f"| {k} | **{v}** |" for k, v in sorted(stats["refresh_action_counts"].items())
    )
    conf_lines = "\n".join(
        f"| {k} | **{v}** |"
        for k, v in sorted(stats["refresh_confidence_counts"].items())
    )

    content = f"""# CNINFO C-Class Company Registry Candidate Refresh Summary

_生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_

> 离线 registry candidate refresh 摘要。**validation artifact only** · **无 CNINFO** · **无 merge**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Input Counts

| 输入 | count |
|------|-------|
| candidate_draft_count | **{stats['candidate_draft_count']}** |
| reconciliation_result_count | **{stats['reconciliation_result_count']}** |
| identity_decision_count | **{stats['identity_decision_count']}** |

---

# Refresh Counts

## classification counts

| classification | count |
|----------------|-------|
{cls_lines}

## refresh_action counts

| refresh_action | count |
|----------------|-------|
{action_lines}

## refresh_confidence counts

| refresh_confidence | count |
|--------------------|-------|
{conf_lines}

## manual_review_required

| 指标 | count |
|------|-------|
| requires_manual_review=true | **{stats['manual_review_required_count']}** |

---

# Safety

| 项 | 值 |
|----|-----|
| CNINFO called | **false** |
| merge executed | **false** |
| registry implemented | **false** |

---

# Gate

**`registry_candidate_refresh_dryrun_gate = PASS_WITH_CAVEAT`**

**C-class 状态保持：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# 产物

- [refreshed candidate](cninfo_c_class_company_registry_candidate_refreshed.csv) · **{stats['refreshed_count']}** 行
- refreshed CSV 为 **validation artifact only** · registry implementation **deferred**
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CNINFO C-class registry candidate 离线 refresh（默认 dry-run）"
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="写入 refreshed CSV 与 summary",
    )
    parser.add_argument("--candidate-draft", default=CANDIDATE_DRAFT_CSV)
    parser.add_argument("--reconciliation", default=RECONCILIATION_CSV)
    parser.add_argument("--ledger", default=LEDGER_CSV)
    parser.add_argument("--output", default=REFRESHED_OUT)
    parser.add_argument("--summary-out", default=SUMMARY_OUT)
    args = parser.parse_args()

    rows, stats = refresh_candidates(
        candidate_draft_csv=args.candidate_draft,
        reconciliation_csv=args.reconciliation,
        ledger_csv=args.ledger,
    )

    print(f"candidate_draft={stats['candidate_draft_count']}")
    print(f"reconciliation={stats['reconciliation_result_count']}")
    print(f"refreshed={stats['refreshed_count']}")
    for cls in REFRESH_RULES:
        print(f"  {cls}: {stats['classification_counts'].get(cls, 0)}")
    print(f"manual_review_required={stats['manual_review_required_count']}")

    if args.write:
        write_refreshed_csv(rows, args.output)
        write_summary(stats, args.summary_out)
        print(f"wrote {args.output}")
        print(f"wrote {args.summary_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
