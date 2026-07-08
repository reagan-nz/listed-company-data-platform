# CNINFO C-Class Registry Canonical Identity Approval Summary

_生成时间：2026-07-08_

> **性质：** Canonical identity approval 设计收口摘要。**仅设计** · **Approval ≠ merge** · **未修改 candidate CSV**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**前置 triage gate：** `registry_conflict_triage_gate = READY_FOR_CANONICAL_APPROVAL`

**Approval gate：** `registry_canonical_identity_approval_gate = READY_FOR_MANUAL_SIGNOFF`

---

## 本轮交付

| # | 产出 | 路径 |
|---|------|------|
| 1 | Canonical approval 设计 | [plans/cninfo_c_class_registry_canonical_identity_approval.md](../../plans/cninfo_c_class_registry_canonical_identity_approval.md) |
| 2 | Approval CSV | [cninfo_c_class_registry_canonical_identity_approval.csv](cninfo_c_class_registry_canonical_identity_approval.csv) |
| 3 | 本摘要 | 本文件 |

---

# Overall

| 指标 | 值 |
|------|-----|
| **conflict_total** | **508** |
| **approval CSV 行数** | **508** |
| **design_recommended** | **267** |
| **unresolved** | **241** |

---

# Recommended Distribution

| recommended_action | count | approval_status |
|--------------------|-------|-----------------|
| **approved_canonical_mapping** | **252** | design_recommended |
| **approved_rename_history** | **15** | design_recommended |
| **manual_identity_review** | **241** | unresolved |
| **rejected_mapping** | **0** | — |

---

# BSE Policy

| 项 | 决议 |
|----|------|
| **839729 / 920729** | `approved_canonical_mapping`（设计推荐） |
| **canonical candidate** | **CNINFO_920729** |
| **merge 执行** | **无** |
| **839729 行** | 保持独立 candidate 行 |

---

# Remaining Unresolved

| 项 | 说明 |
|----|------|
| **unresolved 数量** | **241** |
| **政策** | unresolved 冲突**允许存在**；不阻塞 863 C-class 主线 |
| **典型原因** | 同 org_id 多 code · 证据不足 · 跨板块代码对 |
| **下一步** | 人工 signoff 后可选升 `approval_status=approved` |

---

# Canonical Priority（摘要）

1. `org_id`
2. verified company code mapping
3. historical rename evidence
4. company name similarity（**仅辅助**）

**禁止：** 仅用 `company_name` 做 canonical 决策。

---

# Decision

| 项 | 值 |
|----|-----|
| **registry_canonical_identity_approval_gate** | **`READY_FOR_MANUAL_SIGNOFF`** |

---

## Recommended Next Step

**manual identity signoff** — 对 267 条 `design_recommended` 进行人工确认；仍不 merge harvest/snapshot 数据。

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest
- 未修改 registry candidate CSV · 未合并身份
- 非 production registry · 不写 verified

---

## eraC 章节

- 本节对应 **§7ck Registry Canonical Identity Approval Design**
- 上一节 §7cj Registry Conflict Triage Design 已完成
