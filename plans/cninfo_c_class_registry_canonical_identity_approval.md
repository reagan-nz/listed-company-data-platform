# CNINFO C-Class Registry Canonical Identity Approval 设计

_生成时间：2026-07-08_

> **性质：** canonical identity 审批设计（Era C Phase 4）。**仅设计** · **Approval ≠ merge** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**前置 gate：** `registry_conflict_triage_gate = READY_FOR_CANONICAL_APPROVAL`

**依据：** [conflict triage design](cninfo_c_class_registry_conflict_triage_design.md) · [resolution policy](cninfo_c_class_registry_conflict_resolution_policy.md) · [approval CSV](../outputs/validation/cninfo_c_class_registry_canonical_identity_approval.csv)

---

# 1. Purpose

Canonical identity approval 决定：

- **哪些冲突组**可认定为同一 canonical company identity（元数据层）
- **哪些冲突**必须保持 unresolved

## 1.1 Approval ≠ Merge

| 概念 | 含义 |
|------|------|
| **Approval** | 创建身份决策**元数据**（canonical_candidate · rename_history 候选） |
| **Merge** | 合并 harvest / snapshot / 事件 / 股东 / 财务数据 — **本轮禁止** |

```mermaid
flowchart LR
    Conflict[508 conflicts]
    Approval[Canonical Identity Approval 元数据]
    Candidate[registry candidate 行保持不变]
    Conflict --> Approval
    Approval -.->|不修改| Candidate
```

**政策：** 审批仅写入 approval CSV / 未来 identity decision ledger；**不修改** `company_registry_candidate_draft.csv`。

---

# 2. Approval Taxonomy

## A. approved_canonical_mapping

**适用：** legacy 证券代码迁移（旧 code → 新 code）。

**示例：**

```
839729  ──→  920729
  └─ org_id: gfbj0839729 ─┘
```

**要求：**

| # | 要求 |
|---|------|
| 1 | 同 `org_id` |
| 2 | 同一公司身份证据（同名或 BSE 策略文档） |
| 3 | 代码迁移关系可解释（83/87/43x → 920） |
| 4 | 无冲突的 active 第三方公司 |

**动作：**

- `approved_canonical = true`（设计层）
- `canonical_candidate` = 新 code 对应 `company_id`
- **不合并** harvest / snapshot 数据

**本轮推荐规模：** **252**（251 possible_legacy_mapping + 1 duplicate_identity）

---

## B. approved_rename_history

**适用：** 公司更名（同法人，名称变更）。

**要求：**

| # | 要求 |
|---|------|
| 1 | 同 `company_code` 或同 `org_id` |
| 2 | 历史名称证据 |
| 3 | `rename_date` 可获取（未来轮次） |

**动作：**

- 添加 `rename_history` 候选
- **不合并**实体行

**本轮推荐规模：** **15**

---

## C. manual_identity_review

**适用：** 无法自动判定。

**示例：**

- 同 org_id 但名称关系不明
- 多证券并行
- 历史不完整
- 疑似不同公司共 org_id

**动作：** 保持 `unresolved` · 双行独立身份

**本轮规模：** **241**

---

## D. rejected_mapping

**适用：** 证据表明为**不同公司**。

**动作：** 保持分离身份 · 标记 `rejected_mapping`

**本轮推荐规模：** **0**（设计轮次无足够离线证据自动拒绝；留待人工 signoff）

---

# 3. Approval Artifact

| 产出 | 路径 |
|------|------|
| Approval 清单 | [cninfo_c_class_registry_canonical_identity_approval.csv](../outputs/validation/cninfo_c_class_registry_canonical_identity_approval.csv) |

**列说明：**

| 列 | 用途 |
|----|------|
| `approval_id` | 审批记录编号 |
| `conflict_id` | 关联 triage 冲突 |
| `canonical_candidate` | 推荐 canonical `company_id` |
| `approval_status` | `design_recommended` · `unresolved` · 未来 `approved`/`rejected` |
| `review_notes` | 审批理由 |

---

# 4. Canonical Decision Rules

## Canonical Priority

冲突裁决时，按以下优先级使用证据（**永不单独使用 company_name**）：

| 优先级 | 证据类型 | 用途 |
|--------|----------|------|
| **1** | `org_id` | 法人实体关联主键 |
| **2** | verified company code mapping | BSE 83/87/43x → 920；官方代码变更 |
| **3** | historical rename evidence | 更名链；公告 / 重组文件 |
| **4** | company name similarity | **仅作辅助**，须与 1–3 交叉验证 |

### 禁止规则

| 禁止 | 原因 |
|------|------|
| **仅用 company_name 合并** | 同名不同司 · 借壳 · 重组高发 |
| **无 org_id 自动 canonical** | 身份不可验证 |
| **自动迁移 harvest 数据** | 历史数据不可覆盖 |

### canonical_candidate 选择规则（设计）

```
IF conflict_type = possible_legacy_mapping:
    IF code_2 starts with "920" AND code_1 does not:
        canonical_candidate = company_id_2
    ELSE:
        canonical_candidate = numerically higher active code
IF conflict_type = possible_rename:
    canonical_candidate = current active code (较高编号或现行上市代码)
IF manual_identity_review:
    canonical_candidate = empty (unresolved)
```

---

# 5. BSE Policy

| 项 | 政策 |
|----|------|
| **839729 / 920729** | `approved_canonical_mapping` |
| **canonical candidate** | **CNINFO_920729** |
| **839729 行** | 保持独立 candidate 行 · `duplicate_code` / hold |
| **merge** | **未执行** |
| **probe** | 仍 defer；设计层基于同 org_id + 策略文档 |

---

# 6. Remaining Unresolved

| 项 | 说明 |
|----|------|
| **unresolved 允许** | 241 条 `manual_identity_review` 可长期保持 unresolved |
| **不影响 863 主线** | 863 harvest / snapshot 已完成，不依赖全市场 canonical |
| **future signoff** | 人工审批后可升 `approval_status=approved` |

---

# 7. 红线确认

- 无 CNINFO · 无 live · 无 harvest
- **不修改** registry candidate CSV
- **不自动合并**身份
- 不建 production registry
- 不写 verified · 不入库

**下一步：** [approval summary](../outputs/validation/cninfo_c_class_registry_canonical_identity_approval_summary.md) · manual identity signoff（未来）
