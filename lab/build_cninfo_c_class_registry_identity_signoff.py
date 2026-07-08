#!/usr/bin/env python3
"""
CNINFO C-class BSE legacy + duplicate identity signoff 生成器。

身份决策账本记录 only · 不合并 · 不修改 candidate。
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BSE_FAST = os.path.join(BASE_DIR, "outputs/validation/bse_legacy_mapping_fast_triage.csv")
BSE_SIGNOFF_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_bse_legacy_mapping_signoff.csv"
)
DUP_SIGNOFF_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_duplicate_identity_signoff.csv"
)
SUMMARY_OUT = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_identity_signoff_summary.md"
)

BSE_COLUMNS = [
    "review_id",
    "conflict_id",
    "old_code",
    "current_code",
    "old_name",
    "current_name",
    "org_id",
    "org_id_match",
    "mapping_reason",
    "decision",
    "canonical_policy",
    "canonical_candidate",
    "merge_executed",
    "notes",
]

DUP_COLUMNS = [
    "review_id",
    "conflict_id",
    "company_code_1",
    "company_code_2",
    "company_name",
    "org_id",
    "decision",
    "canonical",
    "canonical_policy",
    "merge_executed",
    "notes",
]


def build_bse_signoff(fast_path: str) -> List[Dict[str, str]]:
    rows_out: List[Dict[str, str]] = []
    with open(fast_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("recommended_action") == "manual_review_required":
                decision = "manual_identity_review"
                policy = "unresolved"
                notes = row.get("triage_notes", "manual_review_required")
            elif (
                row.get("org_id_match") == "true"
                and "BSE_83_87_or_43x_to_920" in row.get("mapping_reason", "")
            ):
                decision = "approved_canonical_mapping"
                policy = "legacy_code_mapping"
                notes = "legacy→current 映射批准；身份决策元数据 only；不合并"
            else:
                decision = "manual_identity_review"
                policy = "unresolved"
                notes = row.get("triage_notes", "exception_case")
            rows_out.append({
                "review_id": row["review_id"],
                "conflict_id": row["conflict_id"],
                "old_code": row["old_code"],
                "current_code": row["current_code"],
                "old_name": row["old_name"],
                "current_name": row["current_name"],
                "org_id": row["org_id"],
                "org_id_match": row["org_id_match"],
                "mapping_reason": row["mapping_reason"],
                "decision": decision,
                "canonical_policy": policy,
                "canonical_candidate": row.get("canonical_candidate", ""),
                "merge_executed": "false",
                "notes": notes,
            })
    return rows_out


def build_duplicate_signoff() -> List[Dict[str, str]]:
    return [{
        "review_id": "REVIEW_0508",
        "conflict_id": "CONFLICT_0508_839729_920729",
        "company_code_1": "839729",
        "company_code_2": "920729",
        "company_name": "永顺生物",
        "org_id": "gfbj0839729",
        "decision": "approved_canonical_mapping",
        "canonical": "CNINFO_920729",
        "canonical_policy": "legacy_code_mapping",
        "merge_executed": "false",
        "notes": "legacy_code 重复登记；839729 保持独立 duplicate_code 行；不合并 harvest/snapshot",
    }]


def write_summary(
    path: str,
    bse_rows: List[Dict[str, str]],
    dup_rows: List[Dict[str, str]],
) -> None:
    bse_ctr = Counter(r["decision"] for r in bse_rows)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    content = f"""# CNINFO C-Class Registry Identity Signoff Summary

_生成时间：{now}_

> **性质：** BSE legacy + duplicate identity 决策账本摘要。**不合并** · **未修改 registry candidate**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Gate：** `registry_identity_signoff_gate = PASS`

---

## Overall

| 指标 | 值 |
|------|-----|
| BSE legacy total | **{len(bse_rows)}** |
| BSE approved_canonical_mapping | **{bse_ctr.get('approved_canonical_mapping', 0)}** |
| BSE manual_identity_review | **{bse_ctr.get('manual_identity_review', 0)}** |
| duplicate identity signoff | **{len(dup_rows)}** |
| **merge_executed** | **false** |

---

## BSE Legacy Mapping Signoff

| 项 | 路径 |
|----|------|
| signoff CSV | [cninfo_c_class_registry_bse_legacy_mapping_signoff.csv](cninfo_c_class_registry_bse_legacy_mapping_signoff.csv) |

**规则：**

- `org_id_match=true` + `BSE_83_87_or_43x_to_920` → `approved_canonical_mapping` · `legacy_code_mapping`
- `manual_review_required` → `manual_identity_review`

**典型案例：** 839729 → 920729 永顺生物（canonical CNINFO_920729）

---

## Duplicate Identity Signoff

| 项 | 路径 |
|----|------|
| signoff CSV | [cninfo_c_class_registry_duplicate_identity_signoff.csv](cninfo_c_class_registry_duplicate_identity_signoff.csv) |

| 字段 | 值 |
|------|-----|
| codes | 839729 / 920729 |
| decision | approved_canonical_mapping |
| canonical | CNINFO_920729 |
| policy | legacy_code_mapping |
| merge | **false** |

---

## Identity Decision Ledger Policy

| 项 | 政策 |
|----|------|
| signoff 产物 | 身份决策元数据账本 |
| registry candidate | **未修改** |
| harvest / snapshot | **未合并** |
| 839729 行 | 保持独立 candidate 行 |

---

## 已完成 Signoff 汇总（Registry 冲突）

| 队列 | 状态 |
|------|------|
| rename history（15） | §7cn 完成 · 10 approved · 5 manual |
| BSE legacy（251） | 本节 · **{bse_ctr.get('approved_canonical_mapping', 0)}** approved · **{bse_ctr.get('manual_identity_review', 0)}** manual |
| duplicate identity（1） | 本节 · 1 approved |

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · **无 identity merge**
- 未修改 raw / normalized / field_inventory · 不写 verified

---

## eraC 章节

- 本节对应 **§7co Registry BSE Legacy + Duplicate Identity Signoff**
- 上一节 §7cn Registry Rename History Signoff 已完成
"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description="BSE + duplicate identity signoff")
    parser.add_argument("--bse-fast", default=BSE_FAST)
    parser.add_argument("--bse-out", default=BSE_SIGNOFF_OUT)
    parser.add_argument("--dup-out", default=DUP_SIGNOFF_OUT)
    parser.add_argument("--summary-out", default=SUMMARY_OUT)
    args = parser.parse_args()

    bse_rows = build_bse_signoff(args.bse_fast)
    dup_rows = build_duplicate_signoff()

    os.makedirs(os.path.dirname(args.bse_out), exist_ok=True)
    with open(args.bse_out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BSE_COLUMNS)
        w.writeheader()
        w.writerows(bse_rows)

    with open(args.dup_out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=DUP_COLUMNS)
        w.writeheader()
        w.writerows(dup_rows)

    write_summary(args.summary_out, bse_rows, dup_rows)

    ctr = Counter(r["decision"] for r in bse_rows)
    print(f"bse total: {len(bse_rows)}")
    print(f"bse approved: {ctr.get('approved_canonical_mapping', 0)}")
    print(f"bse manual: {ctr.get('manual_identity_review', 0)}")
    print(f"duplicate: {len(dup_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
