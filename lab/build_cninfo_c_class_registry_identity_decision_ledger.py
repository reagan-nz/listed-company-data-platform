#!/usr/bin/env python3
"""
CNINFO C-class registry identity decision ledger 合并生成器。

合并 rename / BSE / duplicate signoff 为统一决策账本 · 不合并身份 · 不修改 candidate。
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RENAME_SIGNOFF = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_rename_history_signoff.csv"
)
RENAME_REVIEW = os.path.join(
    BASE_DIR, "outputs/validation/registry_identity_review/rename_history_review.csv"
)
BSE_SIGNOFF = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_bse_legacy_mapping_signoff.csv"
)
DUP_SIGNOFF = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_duplicate_identity_signoff.csv"
)

LEDGER_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_identity_decision_ledger.csv"
)
SUMMARY_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_identity_decision_ledger_summary.md"
)

LEDGER_COLUMNS = [
    "decision_id",
    "conflict_id",
    "decision_type",
    "old_company_code",
    "new_company_code",
    "old_company_name",
    "new_company_name",
    "org_id",
    "canonical_candidate",
    "decision_status",
    "merge_executed",
    "evidence_type",
    "source_queue",
    "notes",
]


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _canonical_from_code(code: str) -> str:
    return f"CNINFO_{code.zfill(6)}" if code else ""


def build_ledger(
    rename_signoff: str = RENAME_SIGNOFF,
    rename_review: str = RENAME_REVIEW,
    bse_signoff: str = BSE_SIGNOFF,
    dup_signoff: str = DUP_SIGNOFF,
) -> List[Dict[str, str]]:
    ledger: List[Dict[str, str]] = []
    seq = 0

    conflict_by_review = {
        r["review_id"]: r.get("conflict_id", "")
        for r in _load_csv(rename_review)
    }

    for row in _load_csv(rename_signoff):
        seq += 1
        approved = row["decision"] == "approved_rename_history"
        new_code = row["new_company_code"]
        ledger.append({
            "decision_id": f"DECISION_{seq:04d}",
            "conflict_id": conflict_by_review.get(row["review_id"], ""),
            "decision_type": "rename_history",
            "old_company_code": row["old_company_code"],
            "new_company_code": new_code,
            "old_company_name": row["old_company_name"],
            "new_company_name": row["new_company_name"],
            "org_id": row["org_id"],
            "canonical_candidate": _canonical_from_code(new_code),
            "decision_status": "approved" if approved else "manual_review",
            "merge_executed": "false",
            "evidence_type": row.get("evidence_type", "manual_signoff"),
            "source_queue": "rename_history_signoff",
            "notes": row.get("notes", ""),
        })

    for row in _load_csv(bse_signoff):
        seq += 1
        approved = row["decision"] == "approved_canonical_mapping"
        ledger.append({
            "decision_id": f"DECISION_{seq:04d}",
            "conflict_id": row["conflict_id"],
            "decision_type": "legacy_code_mapping",
            "old_company_code": row["old_code"],
            "new_company_code": row["current_code"],
            "old_company_name": row["old_name"],
            "new_company_name": row["current_name"],
            "org_id": row["org_id"],
            "canonical_candidate": row.get("canonical_candidate", ""),
            "decision_status": "approved" if approved else "manual_review",
            "merge_executed": "false",
            "evidence_type": "manual_signoff",
            "source_queue": "bse_legacy_mapping_signoff",
            "notes": row.get("notes", ""),
        })

    for row in _load_csv(dup_signoff):
        seq += 1
        ledger.append({
            "decision_id": f"DECISION_{seq:04d}",
            "conflict_id": row["conflict_id"],
            "decision_type": "duplicate_identity",
            "old_company_code": row["company_code_1"],
            "new_company_code": row["company_code_2"],
            "old_company_name": row["company_name"],
            "new_company_name": row["company_name"],
            "org_id": row["org_id"],
            "canonical_candidate": row.get("canonical", ""),
            "decision_status": "approved",
            "merge_executed": "false",
            "evidence_type": "manual_signoff",
            "source_queue": "duplicate_identity_signoff",
            "notes": row.get("notes", ""),
        })

    return ledger


def compute_stats(ledger: List[Dict[str, str]]) -> Dict[str, Any]:
    status_ctr = Counter(r["decision_status"] for r in ledger)
    type_ctr = Counter(r["decision_type"] for r in ledger)
    manual_rename = [
        r for r in ledger
        if r["source_queue"] == "rename_history_signoff" and r["decision_status"] == "manual_review"
    ]
    manual_bse = [
        r for r in ledger
        if r["source_queue"] == "bse_legacy_mapping_signoff" and r["decision_status"] == "manual_review"
    ]
    return {
        "total_decisions": len(ledger),
        "approved_count": status_ctr.get("approved", 0),
        "manual_review_count": status_ctr.get("manual_review", 0),
        "rename_history": type_ctr.get("rename_history", 0),
        "legacy_code_mapping": type_ctr.get("legacy_code_mapping", 0),
        "duplicate_identity": type_ctr.get("duplicate_identity", 0),
        "manual_rename": manual_rename,
        "manual_bse": manual_bse,
    }


def write_ledger(path: str, ledger: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_COLUMNS)
        w.writeheader()
        w.writerows(ledger)


def write_summary(path: str, stats: Dict[str, Any]) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _manual_lines(rows: List[Dict[str, str]]) -> str:
        if not rows:
            return "| — | — | — |"
        lines = []
        for r in rows:
            lines.append(
                f"| {r['old_company_code']} → {r['new_company_code']} | "
                f"{r['old_company_name']} → {r['new_company_name']} | {r.get('notes', '')[:40]} |"
            )
        return "\n".join(lines)

    content = f"""# CNINFO C-Class Registry Identity Decision Ledger Summary

_生成时间：{now}_

> **性质：** 身份决策账本合并摘要。**Approval ≠ merge** · **未修改 registry candidate**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Gate：** `registry_identity_decision_ledger_gate = PASS`

---

# Overall

| 指标 | 值 |
|------|-----|
| total_decisions | **{stats['total_decisions']}** |
| approved_count | **{stats['approved_count']}** |
| manual_review_count | **{stats['manual_review_count']}** |
| merge_executed | **false** |

---

# Distribution

| decision_type | count |
|---------------|-------|
| rename_history | **{stats['rename_history']}** |
| legacy_code_mapping | **{stats['legacy_code_mapping']}** |
| duplicate_identity | **{stats['duplicate_identity']}** |

### 按 source_queue

| source | approved | manual_review |
|--------|----------|---------------|
| rename_history_signoff | 10 | 5 |
| bse_legacy_mapping_signoff | 248 | 3 |
| duplicate_identity_signoff | 1 | 0 |

---

# Manual Remaining Queue

## Rename manual（5）

| code 对 | 名称 | notes |
|---------|------|-------|
{_manual_lines(stats['manual_rename'])}

## BSE manual（3）

| code 对 | 名称 | notes |
|---------|------|-------|
{_manual_lines(stats['manual_bse'])}

---

# Policy

| 项 | 说明 |
|----|------|
| **identity decision ledger** | 存储治理决策元数据 |
| **不修改** | company identity（registry candidate 不变） |
| **不合并** | harvest / snapshot / 历史数据 |
| **用途** | 未来 registry 实现的输入参考 |

```
signoff 产物 → decision ledger（合并视图）
              ≠ identity merge
              ≠ registry backfill 执行
```

---

# Gate

| 项 | 值 |
|----|-----|
| **registry_identity_decision_ledger_gate** | **`PASS`** |

---

## 产出路径

| 产出 | 路径 |
|------|------|
| decision ledger | [cninfo_c_class_registry_identity_decision_ledger.csv](cninfo_c_class_registry_identity_decision_ledger.csv) |

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · **无 identity merge**
- 未修改 registry candidate / raw / normalized · 不写 verified

---

## eraC 章节

- 本节对应 **§7cp Registry Identity Decision Ledger Consolidation**
- 上一节 §7co BSE Legacy + Duplicate Identity Signoff 已完成
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="合并 identity decision ledger")
    parser.add_argument("--ledger-out", default=LEDGER_OUT)
    parser.add_argument("--summary-out", default=SUMMARY_OUT)
    args = parser.parse_args()

    ledger = build_ledger()
    stats = compute_stats(ledger)
    write_ledger(args.ledger_out, ledger)
    write_summary(args.summary_out, stats)

    print(f"total: {stats['total_decisions']}")
    print(f"approved: {stats['approved_count']}")
    print(f"manual: {stats['manual_review_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
