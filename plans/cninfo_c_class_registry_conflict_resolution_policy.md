# CNINFO C-Class Registry Conflict Resolution Policy

_生成时间：2026-07-08_

> **性质：** registry 身份冲突处置政策（Era C Phase 4）。**仅政策** · **不执行合并** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：** [conflict triage design](cninfo_c_class_registry_conflict_triage_design.md) · [conflict triage CSV](../outputs/validation/cninfo_c_class_registry_conflict_triage.csv)

---

## 政策原则

1. **保守优先：** 宁可保留重复行，不可错误合并
2. **证据驱动：** 无证据不升级 confidence、不合并
3. **分层处置：** legacy / rename / manual / duplicate 分队列
4. **可追溯：** 每次决策写入 `notes` + `review_status`

---

## Automatic Allowed（未来轮次，须证据）

以下动作可在**有明确证据**时自动执行，且**仍不合并 harvest 历史**：

| 场景 | 允许动作 | 前置证据 |
|------|----------|----------|
| **confirmed legacy code mapping** | 920 行填 `previous_code` / `legacy_code`；83/87 行标 `duplicate_drop` | 同 org_id + BSE 策略文档 + probe PASS |
| **confirmed rename history** | 写入 `rename_history` 数组 | 公告解析或官方更名记录 |

**限制：** 自动动作仅更新 registry 元数据字段；**不**迁移 harvest/snapshot 文件。

---

## Manual Review Required

以下场景**必须**人工 review 后方可决策：

| 场景 | 原因 | 建议动作 |
|------|------|----------|
| **duplicate org_id + different active securities** | 可能借壳或并行上市 | `manual_review_no_auto_merge` |
| **conflicting company identity** | 同名不同 org_id 或异名同 org_id 非已知案例 | 核对 Era B/C YAML |
| **missing evidence** | 无公告 / 无 probe | defer · 保持 `unresolved` |
| **possible_rename（15 例）** | 名称变更无日期 | `candidate_rename_history` + 人工补日期 |
| **needs_manual_review（241 例）** | 自动规则无法分类 | 分优先级工单 |

---

## Never Automatic Merge

以下情况**永不**自动合并：

| 数据域 | 风险 |
|--------|------|
| **financial history** | 财务数据串线不可恢复 |
| **events** | 公司事件时间线错乱 |
| **shareholders** | 股东结构污染 |
| **snapshots** | 863 已生成 snapshot 不可覆盖合并 |

**说明：** 即使 `org_id` 相同，也仅通过 `company_id`（`CNINFO_{code}`）保持行级隔离，直到 canonical identity approval 明确授权。

---

## Resolution Actions 枚举

| action | 含义 | 是否合并 |
|--------|------|----------|
| `candidate_mapping` | 记录 legacy→current 映射候选 | **否** |
| `candidate_rename_history` | 记录更名历史候选 | **否** |
| `manual_review_no_auto_merge` | 人工审核，保持双行 | **否** |
| `manual_decision_required` | 高概率重复，人工决定去留 | **否**（默认） |
| `canonical_approved` | 未来：canonical 决策完成 | 仅元数据层 |
| `drop_duplicate_row` | 未来：人工确认后标记重复行 | 不删 harvest 数据 |

---

## BSE Legacy 专项政策

| 项 | 政策 |
|----|------|
| 839729 / 920729 | `candidate_mapping`；canonical code = **920729** |
| 83/87 legacy 行 | 保持 `hold_flag=true` · `unsupported` |
| 映射 probe | **defer**；无 probe 不升 `confirmed` |

---

## Review Status 生命周期

```
unresolved → in_review → candidate_approved → canonical_approved
                      ↘ deferred
                      ↘ rejected_merge
```

**本轮：** 全部 **508** 条为 `unresolved`。

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest
- 不修改 registry candidate CSV
- 不自动合并身份
- 不写 verified · 不入库

**下一步：** canonical identity approval
