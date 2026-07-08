# CNINFO C-Class Registry Identity Decision Ledger Summary

_生成时间：2026-07-08T10:06:20Z_

> **性质：** 身份决策账本合并摘要。**Approval ≠ merge** · **未修改 registry candidate**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Gate：** `registry_identity_decision_ledger_gate = PASS`

---

# Overall

| 指标 | 值 |
|------|-----|
| total_decisions | **267** |
| approved_count | **259** |
| manual_review_count | **8** |
| merge_executed | **false** |

---

# Distribution

| decision_type | count |
|---------------|-------|
| rename_history | **15** |
| legacy_code_mapping | **251** |
| duplicate_identity | **1** |

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
| 600087 → 601975 | 退市长油 → 招商南油 | 退市后重新上市过渡；不解析为普通 rename |
| 688287 → 832317 | 退市观典 → 观典防务 | 科创板与北交所跨市场过渡；须 security identity review |
| 839680 → 920680 | *ST广道 → 广道退 | 退市状态变更；非普通 rename_history |
| 600631 → 600827 | 百联股份 → 百联股份 | 同名不同 org_id；须 security identity review |
| 600637 → 600832 | 东方明珠 → 东方明珠 | 同名不同 org_id；须 security identity review |

## BSE manual（3）

| code 对 | 名称 | notes |
|---------|------|-------|
| 301192 → 833874 | 泰祥股份 → 泰祥股份 | no_clear_code_migration |
| 301321 → 833994 | 翰博高新 → 翰博高新 | no_clear_code_migration |
| 600849 → 601607 | 上海医药 → 上海医药 | no_clear_code_migration |

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
