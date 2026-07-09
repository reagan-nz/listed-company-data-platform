# CNINFO D 类 Phase 1 Schema Freeze v1 — 批准摘要

_生成时间：2026-07-09_

> **性质：** 人工 signoff 摘要；**本轮不执行 implementation** · **CNINFO calls = 0** · **gate 不是 PASS**。

---

## Gate

```text
d_class_phase1_schema_freeze_gate = READY_FOR_APPROVAL
```

批准包已准备；**待人工 signoff**。Signoff 后下一 gate 建议：

```text
d_class_phase1_schema_freeze_signoff_gate = READY_FOR_IMPLEMENTATION
```

（本文件**不**将 freeze gate 改为 PASS。）

---

## Frozen Scope（提议）

Phase 1 v1 冻结：

- 统一 **market_event** 信封（8 required + lineage recommended）
- **7** 个市场行为组件 payload 字段契约
- **quality / retrieval / lineage** 状态口径（见 [event quality policy](../../plans/cninfo_d_class_event_quality_policy.md)）
- 离线 fixture + lint 验证路径

**不包含：** live · harvest · PDF · DB · MinIO · RAG · verified · testing_stable_sample 升级。

---

## Component List（7）

| # | component（产品名） | source_id | 逻辑表 |
|---|---------------------|-----------|--------|
| 1 | margin_trading | `margin_trading` | d_company_metric_daily |
| 2 | block_trade | `block_trade` | d_company_event |
| 3 | restricted_unlock | `restricted_shares_unlock` | d_company_event |
| 4 | disclosure_schedule | `disclosure_schedule` | d_disclosure_schedule |
| 5 | equity_pledge | `equity_pledge` | d_company_event |
| 6 | shareholder_change | `shareholder_change` | d_company_event |
| 7 | executive_shareholding | `executive_shareholding` | d_company_event |

> `restricted_unlock` 为产品简称；registry / fixture 键名为 `restricted_shares_unlock`。

---

## Field Counts

| 级别 | 数量 | 说明 |
|------|------|------|
| **required** | **49** | Phase 1 normalized 契约必填 |
| **recommended** | **25** | 可有缺失；不阻塞 capture |
| **future** | **3** | buyer · seller · pledge_status |
| **removed** | **2** | verified_flag · testing_stable_sample_flag |
| **matrix rows** | **79** | 含 market_event 信封与跨组件字段 |

### Required 分布（payload + 信封）

| 组件 | required |
|------|----------|
| market_event 信封 | 8 |
| margin_trading | 8 |
| block_trade | 7 |
| restricted_shares_unlock | 5 |
| disclosure_schedule | 4 |
| equity_pledge | 5 |
| shareholder_change | 6 |
| executive_shareholding | 5 |

---

## Offline Validation Status

| 项 | 结果 |
|----|------|
| lint | **10/10 PASS** |
| fixtures | **3/7**（合成示例） |
| registry YAML | **未修改** |
| schemas/d_class | **未修改** |

---

## Key Risks（signoff 时确认）

1. block_trade 无 buyer/seller — **future**
2. margin_trading 单位语义 medium — 允许 `caveat`
3. equity_pledge pledge_status — **future**
4. 仅 3 组件 fixture — implementation 扩 4 组件
5. 合法空态须按 [quality policy](../../plans/cninfo_d_class_event_quality_policy.md) 标注 `empty_but_valid`

---

## Approval Package Artifacts

| 交付物 | 路径 |
|--------|------|
| 本摘要 | `cninfo_d_class_phase1_schema_freeze_approval_summary.md` |
| 检查清单 | [cninfo_d_class_phase1_schema_freeze_approval_checklist.md](cninfo_d_class_phase1_schema_freeze_approval_checklist.md) |
| Implementation plan | [cninfo_d_class_phase1_freeze_v1_implementation_plan.md](../../plans/cninfo_d_class_phase1_freeze_v1_implementation_plan.md) |
| Quality policy | [cninfo_d_class_event_quality_policy.md](../../plans/cninfo_d_class_event_quality_policy.md) |
| Freeze review | [cninfo_d_class_phase1_schema_freeze_review.md](../../plans/cninfo_d_class_phase1_schema_freeze_review.md) |
| Field matrix | [cninfo_d_class_phase1_field_decision_matrix.csv](cninfo_d_class_phase1_field_decision_matrix.csv) |

---

## Parallel State（不变）

| 线 | 状态 |
|----|------|
| C-class | **`SNAPSHOT_GENERATED_QA_REVIEW`** |
| B-class | tiny live **`PASS_WITH_CAVEAT`**（本包未修改 B 类产物） |
| A-class | schema freeze track（本包未修改 A 类产物） |
| D-class live | **NOT EXECUTED** |

---

## Recommended Signoff Outcome

**建议：** `APPROVE_WITH_CAVEAT` — 接受 7 组件字段 freeze + 3 future 字段 + 3/7 fixture 缺口；批准后进入 [implementation plan](../../plans/cninfo_d_class_phase1_freeze_v1_implementation_plan.md)（仍无 live）。

---

## Red Lines

- **CNINFO calls = 0**
- **no live / harvest / PDF / DB / MinIO / RAG**
- **no verified / testing_stable_sample**
- **A/B/C outputs untouched**
