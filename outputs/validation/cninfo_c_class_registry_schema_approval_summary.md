# CNINFO C-Class Company Registry Schema Approval Summary

_生成时间：2026-07-08_

> **性质：** Schema 审批收口摘要。**仅文档** · **不生成 registry 数据**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**审批 gate：** `registry_schema_approval_gate = PASS`

---

## 1. 本轮交付

| # | 产出 | 路径 |
|---|------|------|
| 1 | Schema 审批清单 | [plans/cninfo_c_class_company_registry_schema_approval_checklist.md](../../plans/cninfo_c_class_company_registry_schema_approval_checklist.md) |
| 2 | 本摘要 | 本文件 |

---

## 2. Schema 审批结果

| 项 | 值 |
|----|-----|
| **Schema 字段数** | **24** |
| **approved** | **18** |
| **approved_with_caveat** | **6** |
| **pending** | **0** |
| **rejected** | **0** |
| **Gate** | **`registry_schema_approval_gate = PASS`** |

### approved_with_caveat 字段

`active_status` · `legacy_code` · `previous_code` · `rename_history` · `org_id_conflict_flag` · `suspended_flag`

---

## 3. Schema 目的确认

`company_registry` 作为**身份治理层**，解决：

- 公司身份统一
- 证券代码变更与 BSE legacy 映射
- 更名历史保留
- org_id 冲突标记与 canonical 指向
- 退市 / ST / hold / 暂停上市状态管理

**确认：** registry 是**未来身份层**，**不是** harvest/snapshot 输出，**不立即替代** YAML universe 文件。

---

## 4. BSE Identity Decision

| 项 | 决议 |
|----|------|
| **920 active** | future supported candidate（独立子轨） |
| **83/87 legacy** | legacy_hold · unsupported |
| **839729 / 920729** | 同 org_id `gfbj0839729` |
| **canonical identity** | **920729** |
| **probe / endpoint** | **本轮不执行** |

---

## 5. 剩余 Blocker

| blocker | 状态 |
|---------|------|
| registry implementation not started | 未启动 |
| universe reconciliation not started | 未启动 |
| BSE mapping execution not started | 未启动（政策已批准） |

以上 blocker **不阻塞** schema 批准；阻塞的是 registry 数据派生与 harvest 扩展。

---

## 6. 红线确认

- 无 CNINFO · 无 live · 无 harvest · 无 registry build
- 无 registry 数据 · 无 raw/normalized/snapshot 修改
- 无 DB · MinIO · RAG · verified · testing_stable_sample

---

## 7. 推荐下一步

1. **`derive_cninfo_c_class_company_registry_draft.py` 派生脚本设计**（仍不执行 backfill）
2. **universe reconciliation 规则落地**（6124 + 863 + hold 26 合并）
3. **product layer / security observe 决策**（与 registry 并行）

---

## 8. eraC 章节

- 本节对应 **§7cf Company Registry Schema Approval**
- 上一节 §7ce Company Registry Draft Design 已完成
