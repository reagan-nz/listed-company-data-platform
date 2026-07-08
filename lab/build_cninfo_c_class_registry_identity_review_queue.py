#!/usr/bin/env python3
"""
CNINFO C-class registry identity review queue 离线生成器。

从 triage / approval CSV 派生人工 review 队列；不批准、不合并、不修改 candidate。
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRIAGE_CSV = os.path.join(BASE_DIR, "outputs/validation/cninfo_c_class_registry_conflict_triage.csv")
APPROVAL_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_canonical_identity_approval.csv"
)

QUEUE_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_identity_review_queue.csv"
)
REVIEW_DIR = os.path.join(BASE_DIR, "outputs/validation/registry_identity_review")
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_identity_review_queue_summary.md"
)

QUEUE_COLUMNS = [
    "review_id",
    "conflict_id",
    "conflict_type",
    "priority",
    "company_id_1",
    "company_id_2",
    "company_code_1",
    "company_code_2",
    "company_name_1",
    "company_name_2",
    "org_id",
    "canonical_candidate",
    "current_recommendation",
    "evidence_available",
    "evidence_required",
    "review_status",
    "notes",
]


def _code_from_cid(cid: str) -> str:
    return cid.replace("CNINFO_", "") if cid else ""


def _is_st(name: str) -> bool:
    if not name:
        return False
    u = name.upper()
    return "*ST" in u or u.startswith("ST")


def _is_delisted(name: str) -> bool:
    return "退" in (name or "")


def _priority_for(conflict_type: str, high_risk_manual: bool) -> str:
    if conflict_type == "duplicate_identity":
        return "P0"
    if conflict_type == "possible_legacy_mapping":
        return "P1"
    if conflict_type == "possible_rename":
        return "P2"
    if conflict_type == "needs_manual_review":
        return "P3" if high_risk_manual else "P4"
    return "P4"


def _is_high_risk_manual(row: Dict[str, str]) -> bool:
    n1 = row.get("company_name_1", "")
    n2 = row.get("company_name_2", "")
    c1 = row.get("company_code_1", "")
    c2 = row.get("company_code_2", "")
    org_id = row.get("org_id", "")

    if not org_id:
        return True
    if n1 != n2:
        return True
    if c1 != c2:
        return True
    if _is_st(n1) or _is_st(n2):
        return True
    if _is_delisted(n1) or _is_delisted(n2):
        return True
    return False


def _mapping_reason(row: Dict[str, str]) -> str:
    c1, c2 = row["company_code_1"], row["company_code_2"]
    if c2.startswith("920") and not c1.startswith("920"):
        return "BSE_83_87_or_43x_to_920"
    if c1.startswith("83") or c1.startswith("87"):
        return "BSE_legacy_to_current"
    if c1 != c2:
        return "code_migration_same_org_id"
    return "legacy_mapping"


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _merge_rows(triage: List[Dict[str, str]], approval: List[Dict[str, str]]) -> List[Dict[str, str]]:
    approval_by_conflict = {r["conflict_id"]: r for r in approval}
    merged = []
    for t in triage:
        a = approval_by_conflict.get(t["conflict_id"], {})
        merged.append({**t, **{k: v for k, v in a.items() if k not in t or k in (
            "canonical_candidate", "recommended_action", "approval_status", "review_notes"
        )}})
    return merged


def build_review_queue(
    triage_csv: str = TRIAGE_CSV,
    approval_csv: str = APPROVAL_CSV,
) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    triage = _load_csv(triage_csv)
    approval = _load_csv(approval_csv)
    merged = _merge_rows(triage, approval)

    queue: List[Dict[str, str]] = []
    for i, row in enumerate(merged, 1):
        ct = row.get("conflict_type", "")
        cid1 = row.get("company_id_1", "")
        cid2 = row.get("company_id_2", "")
        c1 = _code_from_cid(cid1)
        c2 = _code_from_cid(cid2)
        n1 = row.get("company_name_1", "")
        n2 = row.get("company_name_2", "")
        org_id = row.get("org_id", "") or row.get("evidence", "")

        base = {
            "company_code_1": c1,
            "company_code_2": c2,
            "company_name_1": n1,
            "company_name_2": n2,
            "org_id": org_id,
        }
        high_risk = ct == "needs_manual_review" and _is_high_risk_manual({**base, "org_id": org_id})
        priority = _priority_for(ct, high_risk)

        if ct == "possible_legacy_mapping":
            ev_avail = "org_id;triage_notes;BSE_policy_doc"
            ev_req = "code_migration_confirmation;optional_probe"
        elif ct == "possible_rename":
            ev_avail = "org_id;name_pair"
            ev_req = "rename_date;announcement_reference"
        elif ct == "duplicate_identity":
            ev_avail = "legacy_code_duplicate_evidence"
            ev_req = "manual_dedup_decision"
        else:
            ev_avail = "org_id" if org_id else "minimal"
            ev_req = "manual_identity_verification;source_cross_check"

        queue.append({
            "review_id": f"REVIEW_{i:04d}",
            "conflict_id": row.get("conflict_id", ""),
            "conflict_type": ct,
            "priority": priority,
            "company_id_1": cid1,
            "company_id_2": cid2,
            "company_code_1": c1,
            "company_code_2": c2,
            "company_name_1": n1,
            "company_name_2": n2,
            "org_id": org_id,
            "canonical_candidate": row.get("canonical_candidate", ""),
            "current_recommendation": row.get("recommended_action", row.get("recommended_action", "")),
            "evidence_available": ev_avail,
            "evidence_required": ev_req,
            "review_status": "pending",
            "notes": row.get("review_notes", row.get("notes", "")),
        })

    stats = _compute_stats(queue)
    return queue, stats


def _compute_stats(queue: List[Dict[str, str]]) -> Dict[str, Any]:
    high_risk_manual = [
        r for r in queue
        if r["conflict_type"] == "needs_manual_review" and r["priority"] == "P3"
    ]
    low_risk_manual = [
        r for r in queue
        if r["conflict_type"] == "needs_manual_review" and r["priority"] == "P4"
    ]
    return {
        "total": len(queue),
        "possible_legacy_mapping": sum(1 for r in queue if r["conflict_type"] == "possible_legacy_mapping"),
        "possible_rename": sum(1 for r in queue if r["conflict_type"] == "possible_rename"),
        "duplicate_identity": sum(1 for r in queue if r["conflict_type"] == "duplicate_identity"),
        "manual_review_high_risk": len(high_risk_manual),
        "manual_review_low_risk": len(low_risk_manual),
        "high_priority_count": sum(1 for r in queue if r["priority"] in ("P0", "P1", "P3")),
        "priority_dist": dict(Counter(r["priority"] for r in queue)),
    }


def write_main_queue(path: str, queue: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=QUEUE_COLUMNS)
        w.writeheader()
        w.writerows(queue)


def write_split_queues(review_dir: str, queue: List[Dict[str, str]]) -> None:
    os.makedirs(review_dir, exist_ok=True)

    # 1. BSE legacy mapping
    bse_rows = []
    for r in queue:
        if r["conflict_type"] != "possible_legacy_mapping":
            continue
        old_code, new_code = r["company_code_1"], r["company_code_2"]
        if new_code.startswith("920") and not old_code.startswith("920"):
            old_c, cur_c = old_code, new_code
            old_n, cur_n = r["company_name_1"], r["company_name_2"]
        elif old_code.startswith("920"):
            old_c, cur_c = new_code, old_code
            old_n, cur_n = r["company_name_2"], r["company_name_1"]
        else:
            old_c, cur_c = old_code, new_code
            old_n, cur_n = r["company_name_1"], r["company_name_2"]
        bse_rows.append({
            "review_id": r["review_id"],
            "conflict_id": r["conflict_id"],
            "old_code": old_c,
            "current_code": cur_c,
            "old_name": old_n,
            "current_name": cur_n,
            "org_id": r["org_id"],
            "mapping_reason": _mapping_reason(r),
            "confidence": "medium",
            "canonical_candidate": r["canonical_candidate"],
            "review_status": "pending",
        })
    _write_csv(
        os.path.join(review_dir, "bse_legacy_mapping_review.csv"),
        ["review_id", "conflict_id", "old_code", "current_code", "old_name", "current_name",
         "org_id", "mapping_reason", "confidence", "canonical_candidate", "review_status"],
        bse_rows,
    )

    # 2. rename history
    rename_rows = []
    for r in queue:
        if r["conflict_type"] != "possible_rename":
            continue
        rename_rows.append({
            "review_id": r["review_id"],
            "conflict_id": r["conflict_id"],
            "old_name": r["company_name_1"],
            "new_name": r["company_name_2"],
            "company_code_1": r["company_code_1"],
            "company_code_2": r["company_code_2"],
            "org_id": r["org_id"],
            "rename_candidate": f"{r['company_name_1']} -> {r['company_name_2']}",
            "evidence_required": "rename_date;announcement",
            "canonical_candidate": r["canonical_candidate"],
            "review_status": "pending",
        })
    _write_csv(
        os.path.join(review_dir, "rename_history_review.csv"),
        ["review_id", "conflict_id", "old_name", "new_name", "company_code_1", "company_code_2",
         "org_id", "rename_candidate", "evidence_required", "canonical_candidate", "review_status"],
        rename_rows,
    )

    # 3. duplicate identity
    dup_rows = []
    for r in queue:
        if r["conflict_type"] != "duplicate_identity":
            continue
        dup_rows.append({
            "review_id": r["review_id"],
            "conflict_id": r["conflict_id"],
            "company_id_1": r["company_id_1"],
            "company_id_2": r["company_id_2"],
            "company_code_1": r["company_code_1"],
            "company_code_2": r["company_code_2"],
            "company_name_1": r["company_name_1"],
            "company_name_2": r["company_name_2"],
            "org_id": r["org_id"],
            "canonical_candidate": r["canonical_candidate"],
            "conflict_reason": "legacy_code_duplicate",
            "manual_priority": "HIGH",
            "review_status": "pending",
        })
    _write_csv(
        os.path.join(review_dir, "duplicate_identity_review.csv"),
        ["review_id", "conflict_id", "company_id_1", "company_id_2", "company_code_1",
         "company_code_2", "company_name_1", "company_name_2", "org_id", "canonical_candidate",
         "conflict_reason", "manual_priority", "review_status"],
        dup_rows,
    )

    # 4 & 5. manual review high / low
    high_rows, low_rows = [], []
    for r in queue:
        if r["conflict_type"] != "needs_manual_review":
            continue
        entry = {
            "review_id": r["review_id"],
            "conflict_id": r["conflict_id"],
            "priority": r["priority"],
            "company_id_1": r["company_id_1"],
            "company_id_2": r["company_id_2"],
            "company_code_1": r["company_code_1"],
            "company_code_2": r["company_code_2"],
            "company_name_1": r["company_name_1"],
            "company_name_2": r["company_name_2"],
            "org_id": r["org_id"],
            "evidence_required": r["evidence_required"],
            "review_status": "pending",
            "notes": r["notes"],
        }
        if r["priority"] == "P3":
            high_rows.append(entry)
        else:
            low_rows.append(entry)

    manual_cols = [
        "review_id", "conflict_id", "priority", "company_id_1", "company_id_2",
        "company_code_1", "company_code_2", "company_name_1", "company_name_2",
        "org_id", "evidence_required", "review_status", "notes",
    ]
    _write_csv(os.path.join(review_dir, "manual_review_high_risk.csv"), manual_cols, high_rows)
    _write_csv(os.path.join(review_dir, "manual_review_low_risk.csv"), manual_cols, low_rows)


def _write_csv(path: str, columns: List[str], rows: List[Dict[str, str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def write_summary(path: str, stats: Dict[str, Any]) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pri = stats.get("priority_dist", {})
    content = f"""# CNINFO C-Class Registry Identity Review Queue Summary

_生成时间：{now}_

> **性质：** 身份 review 队列摘要。**不批准** · **不合并** · **未修改 candidate CSV**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**前置 gate：** `registry_canonical_identity_approval_gate = READY_FOR_MANUAL_SIGNOFF`

---

# Total

| 指标 | 值 |
|------|-----|
| **conflict total** | **{stats['total']}** |
| **high priority（P0+P1+P3）** | **{stats['high_priority_count']}** |
| **review_status** | 全部 **pending** |

---

# Queue Distribution

| 队列 | 行数 |
|------|------|
| possible_legacy_mapping（bse_legacy_mapping_review.csv） | **{stats['possible_legacy_mapping']}** |
| possible_rename（rename_history_review.csv） | **{stats['possible_rename']}** |
| duplicate_identity（duplicate_identity_review.csv） | **{stats['duplicate_identity']}** |
| manual_review_high_risk | **{stats['manual_review_high_risk']}** |
| manual_review_low_risk | **{stats['manual_review_low_risk']}** |

### Priority 分布

| priority | count |
|----------|-------|
| P0 | **{pri.get('P0', 0)}** |
| P1 | **{pri.get('P1', 0)}** |
| P2 | **{pri.get('P2', 0)}** |
| P3 | **{pri.get('P3', 0)}** |
| P4 | **{pri.get('P4', 0)}** |

---

# Recommended Review Order

| 顺序 | 队列 | 说明 |
|------|------|------|
| **P0** | duplicate_identity | 高概率重复实体 |
| **P1** | BSE legacy mapping | 83/87/43x → 920 代码迁移 |
| **P2** | rename history | 更名历史补证 |
| **P3** | high risk manual review | 异名 / ST / 退市 / 多证券 |
| **P4** | low risk manual review | 同名同 org_id 代码对 |

---

# Important Rule

**Identity review ≠ identity merge.**

所有决策保持 **pending**，直至 manual signoff；review 队列仅组织人工工单，不执行 canonical 批准或数据合并。

---

## 产出路径

| 产出 | 路径 |
|------|------|
| 主队列 | [cninfo_c_class_registry_identity_review_queue.csv](cninfo_c_class_registry_identity_review_queue.csv) |
| 分模块队列 | [registry_identity_review/](registry_identity_review/) |

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · 无 identity merge
- 未修改 registry candidate · 非 production registry · 不写 verified
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 registry identity review 队列")
    parser.add_argument("--triage-csv", default=TRIAGE_CSV)
    parser.add_argument("--approval-csv", default=APPROVAL_CSV)
    parser.add_argument("--queue-out", default=QUEUE_CSV)
    parser.add_argument("--review-dir", default=REVIEW_DIR)
    parser.add_argument("--summary-out", default=SUMMARY_MD)
    args = parser.parse_args()

    queue, stats = build_review_queue(args.triage_csv, args.approval_csv)
    write_main_queue(args.queue_out, queue)
    write_split_queues(args.review_dir, queue)
    write_summary(args.summary_out, stats)

    print(f"total: {stats['total']}")
    print(f"high_priority: {stats['high_priority_count']}")
    print(f"legacy: {stats['possible_legacy_mapping']}")
    print(f"rename: {stats['possible_rename']}")
    print(f"duplicate: {stats['duplicate_identity']}")
    print(f"manual_high: {stats['manual_review_high_risk']}")
    print(f"manual_low: {stats['manual_review_low_risk']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
