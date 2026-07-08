#!/usr/bin/env python3
"""
CNINFO C-class registry conflict fast triage batch（设计/分析 only）。

不合并身份 · 不修改 candidate · 不请求 CNINFO。
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

REVIEW_DIR = os.path.join(BASE_DIR, "outputs/validation/registry_identity_review")
CANDIDATE_CSV = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_company_registry_candidate_draft.csv"
)

BSE_FAST_OUT = os.path.join(
    BASE_DIR, "outputs/validation/bse_legacy_mapping_fast_triage.csv"
)
RENAME_FAST_OUT = os.path.join(
    BASE_DIR, "outputs/validation/rename_history_fast_triage.csv"
)
MANUAL_FAST_OUT = os.path.join(
    BASE_DIR, "outputs/validation/manual_high_risk_fast_triage.csv"
)
DUP_DECISION_MD = os.path.join(
    BASE_DIR, "outputs/validation/duplicate_identity_decision.md"
)
SUMMARY_MD = os.path.join(
    BASE_DIR, "outputs/validation/cninfo_c_class_registry_conflict_fast_triage_summary.md"
)


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_candidate_index() -> Dict[str, Dict[str, str]]:
    return {r["company_code"]: r for r in _load_csv(CANDIDATE_CSV)}


def _is_st(name: str) -> bool:
    u = (name or "").upper()
    return "*ST" in u or u.startswith("ST")


def _is_delisted(name: str) -> bool:
    return "退" in (name or "")


def _name_similar(n1: str, n2: str) -> bool:
    if n1 == n2:
        return True
    def norm(n: str) -> str:
        return re.sub(r"\*?ST", "", n or "").strip()
    return bool(norm(n1) and norm(n1) == norm(n2))


def _code_migration(old: str, new: str) -> bool:
    if old == new:
        return False
    if new.startswith("920") and not old.startswith("920"):
        return True
    if old.startswith(("83", "87", "43")) and new.startswith("920"):
        return True
    return False


def _org_pair(cand: Dict[str, Dict[str, str]], c1: str, c2: str) -> Tuple[str, str, bool]:
    o1 = cand.get(c1, {}).get("org_id", "")
    o2 = cand.get(c2, {}).get("org_id", "")
    same = bool(o1 and o2 and o1 == o2)
    return o1, o2, same


def triage_bse_legacy(
    rows: List[Dict[str, str]], cand: Dict[str, Dict[str, str]]
) -> List[Dict[str, str]]:
    out = []
    for r in rows:
        old, new = r["old_code"], r["current_code"]
        o1, o2, same_org = _org_pair(cand, old, new)
        has_code = _code_migration(old, new)
        has_name = _name_similar(r["old_name"], r["current_name"])
        if same_org and has_code and has_name:
            action = "approved_mapping_candidate"
            reason = "same_org_id;code_migration;same_or_similar_name"
        else:
            action = "manual_review_required"
            parts = []
            if not same_org:
                parts.append("org_id_missing_or_mismatch")
            if not has_code:
                parts.append("no_clear_code_migration")
            if not has_name:
                parts.append("name_mismatch")
            reason = ";".join(parts) or "insufficient_evidence"
        out.append({
            "review_id": r["review_id"],
            "conflict_id": r["conflict_id"],
            "old_code": old,
            "current_code": new,
            "old_name": r["old_name"],
            "current_name": r["current_name"],
            "org_id": o1 if same_org else (o1 or o2),
            "org_id_match": "true" if same_org else "false",
            "mapping_reason": r.get("mapping_reason", ""),
            "recommended_action": action,
            "canonical_candidate": r.get("canonical_candidate", ""),
            "triage_notes": reason,
        })
    return out


def triage_rename(
    rows: List[Dict[str, str]], cand: Dict[str, Dict[str, str]]
) -> List[Dict[str, str]]:
    out = []
    for r in rows:
        c1, c2 = r["company_code_1"], r["company_code_2"]
        o1, o2, same_org = _org_pair(cand, c1, c2)
        n1, n2 = r["old_name"], r["new_name"]
        high_risk = (
            _is_delisted(n1) or _is_delisted(n2)
            or (n1 != n2 and not same_org)
            or (c1 != c2 and n1 == n2)
        )
        if same_org and not high_risk and n1 != n2:
            action = "rename_candidate"
            notes = "same_org_id;name_change_evidence"
        else:
            action = "manual_review_required"
            notes_parts = []
            if not same_org:
                notes_parts.append("org_id_missing_or_mismatch")
            if _is_delisted(n1) or _is_delisted(n2):
                notes_parts.append("delisted_involved")
            if c1 != c2 and n1 == n2:
                notes_parts.append("same_name_code_change")
            if _is_st(n1) or _is_st(n2):
                notes_parts.append("st_status_change")
            notes = ";".join(notes_parts) or "complex_rename_or_restructure"
        out.append({
            "review_id": r["review_id"],
            "conflict_id": r["conflict_id"],
            "old_name": n1,
            "new_name": n2,
            "company_code_1": c1,
            "company_code_2": c2,
            "org_id": o1 if same_org else (o1 or o2),
            "recommended_action": action,
            "triage_notes": notes,
        })
    return out


def triage_manual_high(
    rows: List[Dict[str, str]], cand: Dict[str, Dict[str, str]]
) -> List[Dict[str, str]]:
    out = []
    for r in rows:
        c1, c2 = r["company_code_1"], r["company_code_2"]
        n1, n2 = r["company_name_1"], r["company_name_2"]
        o1, o2, same_org = _org_pair(cand, c1, c2)
        if n1 != n2:
            bucket = "identity_risk_high"
            notes = "different_company_name;same_or_diff_org"
        elif not same_org:
            bucket = "evidence_missing"
            notes = "same_name;org_id_missing_or_mismatch"
        elif _code_migration(c1, c2) or (c1 != c2 and same_org):
            bucket = "likely_safe_later"
            notes = "same_name_same_org;code_migration_pattern"
        elif _is_st(n1) or _is_delisted(n1):
            bucket = "identity_risk_high"
            notes = "st_or_delisted_flag"
        else:
            bucket = "evidence_missing"
            notes = "insufficient_offline_evidence"
        out.append({
            "review_id": r["review_id"],
            "conflict_id": r["conflict_id"],
            "company_code_1": c1,
            "company_code_2": c2,
            "company_name_1": n1,
            "company_name_2": n2,
            "org_id": o1 if same_org else (o1 or o2),
            "risk_bucket": bucket,
            "triage_notes": notes,
        })
    return out


def write_duplicate_decision(path: str, dup_rows: List[Dict[str, str]]) -> None:
    r = dup_rows[0] if dup_rows else {}
    content = f"""# Duplicate Identity Decision（设计 · 未执行）

_生成时间：{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}_

> **性质：** duplicate_identity 快速分诊决策备忘。**不合并** · **不修改 candidate**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## 案例

| 项 | 值 |
|----|-----|
| review_id | {r.get('review_id', '')} |
| conflict_id | {r.get('conflict_id', '')} |
| company_code_1 | {r.get('company_code_1', '')} |
| company_code_2 | {r.get('company_code_2', '')} |
| company_name | {r.get('company_name_1', '')} |
| conflict_reason | {r.get('conflict_reason', '')} |
| canonical_candidate | {r.get('canonical_candidate', '')} |

---

## 设计决策（未执行）

| 项 | 决议 |
|----|------|
| **关系** | 同一公司 legacy_code 重复登记（839729 / 920729） |
| **recommended_action** | `approved_mapping_candidate`（与 BSE legacy 队列一致） |
| **canonical** | **CNINFO_920729** |
| **839729 行** | 保持独立 · 标 `duplicate_code` |
| **merge** | **禁止** |
| **review_status** | **pending**（待 manual signoff） |

---

## 红线

- 不合并 harvest / snapshot 数据
- 不修改 registry candidate CSV
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def run_fast_triage() -> Dict[str, Any]:
    cand = _load_candidate_index()
    bse_rows = _load_csv(os.path.join(REVIEW_DIR, "bse_legacy_mapping_review.csv"))
    rename_rows = _load_csv(os.path.join(REVIEW_DIR, "rename_history_review.csv"))
    dup_rows = _load_csv(os.path.join(REVIEW_DIR, "duplicate_identity_review.csv"))
    manual_rows = _load_csv(os.path.join(REVIEW_DIR, "manual_review_high_risk.csv"))

    bse_out = triage_bse_legacy(bse_rows, cand)
    rename_out = triage_rename(rename_rows, cand)
    manual_out = triage_manual_high(manual_rows, cand)

    bse_ctr = Counter(r["recommended_action"] for r in bse_out)
    rename_ctr = Counter(r["recommended_action"] for r in rename_out)
    manual_ctr = Counter(r["risk_bucket"] for r in manual_out)

    # remaining manual = not auto-actionable
    remaining = (
        bse_ctr.get("manual_review_required", 0)
        + rename_ctr.get("manual_review_required", 0)
        + 1  # duplicate still pending signoff
        + manual_ctr.get("identity_risk_high", 0)
        + manual_ctr.get("evidence_missing", 0)
    )
    # likely_safe_later deferred not counted as remaining urgent manual

    stats = {
        "total_conflicts": 508,
        "bse_approved": bse_ctr.get("approved_mapping_candidate", 0),
        "bse_manual": bse_ctr.get("manual_review_required", 0),
        "rename_candidate": rename_ctr.get("rename_candidate", 0),
        "rename_manual": rename_ctr.get("manual_review_required", 0),
        "duplicate_count": len(dup_rows),
        "manual_identity_risk_high": manual_ctr.get("identity_risk_high", 0),
        "manual_evidence_missing": manual_ctr.get("evidence_missing", 0),
        "manual_likely_safe_later": manual_ctr.get("likely_safe_later", 0),
        "remaining_manual_queue": remaining,
        "actionable_candidates": (
            bse_ctr.get("approved_mapping_candidate", 0)
            + rename_ctr.get("rename_candidate", 0)
            + 1
        ),
    }
    return {
        "bse_out": bse_out,
        "rename_out": rename_out,
        "manual_out": manual_out,
        "dup_rows": dup_rows,
        "stats": stats,
    }


def _write_csv(path: str, columns: List[str], rows: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def write_summary(path: str, stats: Dict[str, Any]) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    s = stats
    content = f"""# CNINFO C-Class Registry Conflict Fast Triage Summary

_生成时间：{now}_

> **性质：** 508 冲突快速分桶摘要。**设计/分析 only** · **不合并** · **不修改 candidate**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Gate：** `registry_conflict_fast_triage_gate = READY_FOR_MANUAL_SIGNOFF`

---

## Total

| 指标 | 值 |
|------|-----|
| conflict total | **{s['total_conflicts']}** |
| actionable candidates（设计层） | **{s['actionable_candidates']}** |
| remaining manual queue（优先处理） | **{s['remaining_manual_queue']}** |
| deferred（likely_safe_later） | **{s['manual_likely_safe_later']}** |

---

## Fast Triage Distribution

### BSE legacy mapping（251）

| recommended_action | count |
|--------------------|-------|
| approved_mapping_candidate | **{s['bse_approved']}** |
| manual_review_required | **{s['bse_manual']}** |

### Rename history（15）

| recommended_action | count |
|--------------------|-------|
| rename_candidate | **{s['rename_candidate']}** |
| manual_review_required | **{s['rename_manual']}** |

### Duplicate identity（1）

| 项 | 值 |
|----|-----|
| cases | **{s['duplicate_count']}** |
| decision | 见 [duplicate_identity_decision.md](duplicate_identity_decision.md) |

### Manual high risk（241）

| risk_bucket | count |
|-------------|-------|
| identity_risk_high | **{s['manual_identity_risk_high']}** |
| evidence_missing | **{s['manual_evidence_missing']}** |
| likely_safe_later | **{s['manual_likely_safe_later']}** |

---

## Recommended Review Order

1. **P0** duplicate_identity（1）
2. **P1** BSE manual_review_required（{s['bse_manual']}）
3. **P2** rename manual_review_required（{s['rename_manual']}）
4. **P3** manual identity_risk_high（{s['manual_identity_risk_high']}）
5. **P4** manual evidence_missing（{s['manual_evidence_missing']}）
6. **Defer** likely_safe_later（{s['manual_likely_safe_later']}）

---

## Important Rule

**Fast triage ≠ identity merge.** 所有 `approved_mapping_candidate` / `rename_candidate` 仅为设计层分桶，须 manual signoff 后方可写入 identity decision ledger。

---

## Recommended Next Action

**manual identity signoff** — 优先处理 remaining manual queue **{s['remaining_manual_queue']}** 条；`likely_safe_later` **{s['manual_likely_safe_later']}** 条可延后。

---

## 产出路径

| 产出 | 路径 |
|------|------|
| BSE fast triage | [bse_legacy_mapping_fast_triage.csv](bse_legacy_mapping_fast_triage.csv) |
| Rename fast triage | [rename_history_fast_triage.csv](rename_history_fast_triage.csv) |
| Manual fast triage | [manual_high_risk_fast_triage.csv](manual_high_risk_fast_triage.csv) |
| Duplicate decision | [duplicate_identity_decision.md](duplicate_identity_decision.md) |

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · 无 identity merge
- 未修改 registry candidate CSV
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> int:
    result = run_fast_triage()
    stats = result["stats"]

    _write_csv(
        BSE_FAST_OUT,
        ["review_id", "conflict_id", "old_code", "current_code", "old_name", "current_name",
         "org_id", "org_id_match", "mapping_reason", "recommended_action",
         "canonical_candidate", "triage_notes"],
        result["bse_out"],
    )
    _write_csv(
        RENAME_FAST_OUT,
        ["review_id", "conflict_id", "old_name", "new_name", "company_code_1",
         "company_code_2", "org_id", "recommended_action", "triage_notes"],
        result["rename_out"],
    )
    _write_csv(
        MANUAL_FAST_OUT,
        ["review_id", "conflict_id", "company_code_1", "company_code_2",
         "company_name_1", "company_name_2", "org_id", "risk_bucket", "triage_notes"],
        result["manual_out"],
    )
    write_duplicate_decision(DUP_DECISION_MD, result["dup_rows"])
    write_summary(SUMMARY_MD, stats)

    print(f"bse approved: {stats['bse_approved']}")
    print(f"remaining manual: {stats['remaining_manual_queue']}")
    print(f"summary: {SUMMARY_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
