# CNINFO C-Class Registry Identity Signoff Summary

_生成时间：2026-07-08T09:57:34Z_

> **性质：** BSE legacy + duplicate identity 决策账本摘要。**不合并** · **未修改 registry candidate**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Gate：** `registry_identity_signoff_gate = PASS`

---

## Overall

| 指标 | 值 |
|------|-----|
| BSE legacy total | **251** |
| BSE approved_canonical_mapping | **248** |
| BSE manual_identity_review | **3** |
| duplicate identity signoff | **1** |
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
| BSE legacy（251） | 本节 · **248** approved · **3** manual |
| duplicate identity（1） | 本节 · 1 approved |

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · **无 identity merge**
- 未修改 raw / normalized / field_inventory · 不写 verified

---

## eraC 章节

- 本节对应 **§7co Registry BSE Legacy + Duplicate Identity Signoff**
- 上一节 §7cn Registry Rename History Signoff 已完成
