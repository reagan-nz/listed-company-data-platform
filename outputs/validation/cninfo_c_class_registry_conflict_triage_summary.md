# CNINFO C-Class Registry Conflict Triage Summary

_生成时间：2026-07-08_

> **性质：** 冲突 triage 设计收口摘要。**仅设计** · **不合并身份** · **未修改 candidate CSV**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**前置 QA gate：** `registry_candidate_quality_gate = PASS_WITH_CAVEAT`

**Triage gate：** `registry_conflict_triage_gate = READY_FOR_CANONICAL_APPROVAL`

---

## 本轮交付

| # | 产出 | 路径 |
|---|------|------|
| 1 | Conflict triage 设计 | [plans/cninfo_c_class_registry_conflict_triage_design.md](../../plans/cninfo_c_class_registry_conflict_triage_design.md) |
| 2 | Triage 分类 CSV | [cninfo_c_class_registry_conflict_triage.csv](cninfo_c_class_registry_conflict_triage.csv) |
| 3 | Resolution policy | [plans/cninfo_c_class_registry_conflict_resolution_policy.md](../../plans/cninfo_c_class_registry_conflict_resolution_policy.md) |
| 4 | 本摘要 | 本文件 |

---

## Conflict Total

| 指标 | 值 |
|------|-----|
| **duplicate findings（QA）** | **508** |
| **triage CSV 行数** | **508** |
| **unresolved** | **508** |
| **resolved** | **0** |

---

## Classification

| conflict_type | count | recommended_action |
|---------------|-------|-------------------|
| possible_legacy_mapping | **251** | candidate_mapping |
| needs_manual_review | **241** | manual_review_no_auto_merge |
| possible_rename | **15** | candidate_rename_history |
| duplicate_identity | **1** | manual_decision_required |

---

## 典型案例

**BSE legacy mapping（possible_legacy_mapping）：**

| code_1 | code_2 | org_id | 名称 |
|--------|--------|--------|------|
| 839729 | 920729 | gfbj0839729 | 永顺生物 |

**possible_rename 示例：**

| code_1 | code_2 | name_1 | name_2 |
|--------|--------|--------|--------|
| 601313 | 601360 | 江南嘉捷 | 三六零 |
| 300114 | 302132 | 中航电测 | 中航成飞 |

---

## Policy 摘要

| 类别 | 自动合并 |
|------|----------|
| Automatic allowed（有证据） | mapping / rename **元数据 only** |
| Manual review required | **241 + 15 + 1** 须人工 |
| Never automatic merge | financial / events / shareholders / snapshots |

---

## Decision

| 项 | 值 |
|----|-----|
| **registry_conflict_triage_gate** | **`READY_FOR_CANONICAL_APPROVAL`** |

---

## Recommended Next Step

**canonical identity approval** — 对 508 条 unresolved 冲突分队列审批；仍不自动合并 harvest/snapshot 数据。

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest
- 未修改 registry candidate CSV · 未合并身份
- 非 production registry · 不写 verified

---

## eraC 章节

- 本节对应 **§7cj Registry Conflict Triage Design**
- 上一节 §7ci Registry Candidate QA Review 已完成
