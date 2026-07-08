# CNINFO C-Class Registry Identity Review Queue Summary

_生成时间：2026-07-08T09:19:18Z_

> **性质：** 身份 review 队列摘要。**不批准** · **不合并** · **未修改 candidate CSV**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**前置 gate：** `registry_canonical_identity_approval_gate = READY_FOR_MANUAL_SIGNOFF`

---

# Total

| 指标 | 值 |
|------|-----|
| **conflict total** | **508** |
| **high priority（P0+P1+P3）** | **493** |
| **review_status** | 全部 **pending** |

---

# Queue Distribution

| 队列 | 行数 |
|------|------|
| possible_legacy_mapping（bse_legacy_mapping_review.csv） | **251** |
| possible_rename（rename_history_review.csv） | **15** |
| duplicate_identity（duplicate_identity_review.csv） | **1** |
| manual_review_high_risk | **241** |
| manual_review_low_risk | **0** |

### Priority 分布

| priority | count |
|----------|-------|
| P0 | **1** |
| P1 | **251** |
| P2 | **15** |
| P3 | **241** |
| P4 | **0** |

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
