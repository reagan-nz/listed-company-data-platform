# CNINFO D 类 Phase 1 Schema Freeze v1 — 批准检查清单

_生成时间：2026-07-09_

> **性质：** 人工 signoff 前检查清单；**本轮不执行 implementation** · **不修改 gate 为 PASS** · **NOT APPROVED**。  
> **前置：** [schema freeze review](../../plans/cninfo_d_class_phase1_schema_freeze_review.md) · [field matrix](cninfo_d_class_phase1_field_decision_matrix.csv) · [event object schema](../../plans/cninfo_d_class_event_object_schema.md) · [lint summary](cninfo_d_class_phase1_schema_lint_summary.md)（**10/10 PASS**）

---

## Preconditions

| # | 条件 | 要求 | 当前状态 |
|---|------|------|----------|
| 1 | Phase 0 planning | `d_class_initial_planning_gate = DESIGN_STARTED` | **PASS** |
| 2 | schema freeze review | 7 组件字段契约已文档化 | **PASS** |
| 3 | offline lint | `d_class_phase1_schema_lint_gate = PASS` · **10/10** | **PASS** |
| 4 | phase1 fixtures | 3 合成示例 fixture 存在 | **PASS** |
| 5 | registry / harvest | **未**启动 live · harvest · DB | **PASS** |

### 并行安全（signoff 前再确认）

- [ ] C-class status 保持 **`SNAPSHOT_GENERATED_QA_REVIEW`**
- [ ] **未修改** `outputs/harvest/cninfo_c_class/` 与 C-class snapshot 产物
- [ ] **未修改** B-class tiny live / retry 输出
- [ ] **未修改** A-class schema freeze 产物
- [ ] **CNINFO calls = 0**（本轮及批准包准备轮）

---

## 1. Event Object Design

参考：[cninfo_d_class_event_object_schema.md](../../plans/cninfo_d_class_event_object_schema.md)

| # | 检查项 | 期望 | 审阅 |
|---|--------|------|------|
| 1.1 | 层级 | `company` → `market_event` → `timeline`（timeline 读模型 Phase 1 不生成） | [ ] |
| 1.2 | 信封必填 | `event_id` · `company_code` · `event_type` · `event_time` · `source_endpoint` · `source_record_id` · `event_status` · `quality_status` | [ ] |
| 1.3 | 组件 payload | 单记录仅一个 `event_type` 键（7 选 1） | [ ] |
| 1.4 | 一致性 | 信封 `company_code` / `event_time` / `quality_status` 与 payload 对齐 | [ ] |
| 1.5 | 逻辑表映射 | margin_trading → `d_company_metric_daily`；其余 6 → event/schedule 表 | [ ] |
| 1.6 | C/B 边界 | 非 profile · 非 document PDF | [ ] |

---

## 2. Field Levels

参考：[cninfo_d_class_phase1_field_decision_matrix.csv](cninfo_d_class_phase1_field_decision_matrix.csv)（**79** 行）

| 级别 | 数量 | 审阅 |
|------|------|------|
| **required** | **49** | [ ] |
| **recommended** | **25** | [ ] |
| **future** | **3** | [ ] |
| **removed** | **2** | [ ] |

| # | 检查项 | 期望 | 审阅 |
|---|--------|------|------|
| 2.1 | 7 组件均含 `quality_status = required` | matrix R-D-P1-002 已 PASS | [ ] |
| 2.2 | 无 `verified` / `testing_stable_sample` 字段 | matrix R-D-P1-003 已 PASS | [ ] |
| 2.3 | future 字段不进入 Phase 1 normalized 必填 | buyer · seller · pledge_status | [ ] |

---

## 3. Required Fields（按组件）

| component | required 数（payload） | 审阅 |
|-----------|---------------------|------|
| margin_trading | 8 | [ ] |
| block_trade | 7 | [ ] |
| restricted_shares_unlock | 5 | [ ] |
| disclosure_schedule | 4 | [ ] |
| equity_pledge | 5 | [ ] |
| shareholder_change | 6 | [ ] |
| executive_shareholding | 5 | [ ] |
| market_event（信封） | 8 | [ ] |

关键 required 抽查：

- [ ] `margin_trading`: `trade_date` · `financing_balance` · `total_margin_balance` · `retrieval_time`
- [ ] `block_trade`: `transaction_price` · `transaction_volume` · `transaction_amount`（无 buyer/seller）
- [ ] `restricted_shares_unlock`: `unlock_date` · `unlock_amount` · `unlock_ratio`
- [ ] `disclosure_schedule`: `report_type` · `planned_date`
- [ ] `shareholder_change`: `shareholder_name` · `change_type` · `change_date`
- [ ] `executive_shareholding`: `executive_name` · `change_type` · `change_amount`

---

## 4. Recommended Fields

| 类别 | 代表字段 | 审阅 |
|------|----------|------|
| 显示增强 | `company_name`（多组件） | [ ] |
| 流水指标 | `financing_buy_amount` · `margin_sell_amount` | [ ] |
| 日程变更 | `change_history` · `actual_date` | [ ] |
| 风险细节 | `tradable_amount` · `pledgee` · `position` | [ ] |
| 血缘扩展 | `lineage` · `raw_record_json` | [ ] |

原则：**recommended 缺失不阻塞 Phase 1 capture**；须在 `quality_status` 或 flags 中可解释。

---

## 5. Future Fields

| field | component | 原因 | 审阅 |
|-------|-----------|------|------|
| buyer | block_trade | statistics endpoint 无买卖双方 | [ ] |
| seller | block_trade | 同上 | [ ] |
| pledge_status | equity_pledge | 状态映射未 freeze | [ ] |

Signoff 确认：Phase 1 **不承诺** 上述字段进入 normalized 输出。

---

## 6. Removed Fields

| field | component | 原因 | 审阅 |
|-------|-----------|------|------|
| verified_flag | market_event | 政策禁止 | [ ] |
| testing_stable_sample_flag | market_event | 禁止升级口径 | [ ] |

---

## 7. Quality Status Design

参考：[cninfo_d_class_event_quality_policy.md](../../plans/cninfo_d_class_event_quality_policy.md)

| 维度 | 枚举 | 审阅 |
|------|------|------|
| `quality_status` | pass · caveat · blocked · needs_review | [ ] |
| `event_status` | captured · empty_but_valid · failed · pending | [ ] |
| `retrieval_status` | found · not_found · empty_but_valid · http_error · blocked | [ ] |
| `lineage_status` | discovered · linked · needs_review · stale | [ ] |

| # | 检查项 | 审阅 |
|---|--------|------|
| 7.1 | 合法空态（无交易/无质押/无增减持/无解禁）→ `empty_but_valid` 非 failed | [ ] |
| 7.2 | 字段语义 medium confidence → 允许 `quality_status=caveat` | [ ] |
| 7.3 | HTTP/权限/结构错误 → `failed` 或 `blocked` | [ ] |
| 7.4 | **不写 verified** | [ ] |

---

## 8. Lineage Design

| 字段 | 级别 | 审阅 |
|------|------|------|
| `registry_source_id` | required（lineage 内） | [ ] |
| `fetch_time` / `retrieval_time` | required | [ ] |
| `raw_record_hash` | required | [ ] |
| `query_mode` · `query_params` | recommended | [ ] |
| `raw_record_json` | recommended（强烈建议） | [ ] |

| # | 检查项 | 审阅 |
|---|--------|------|
| 8.1 | `source_endpoint` 与 registry YAML 一致（7 源） | [ ] lint R-D-P1-010 PASS |
| 8.2 | Phase 1 保留 raw 行，不丢 mapper 审计链 | [ ] |
| 8.3 | 不与 B-class PDF lineage 混用 | [ ] |

---

## 9. Fixtures & Lint

| 产物 | 状态 | 审阅 |
|------|------|------|
| [margin_trading_fixture.json](../../fixtures/d_class/phase1/margin_trading_fixture.json) | 合成示例 | [ ] |
| [block_trade_fixture.json](../../fixtures/d_class/phase1/block_trade_fixture.json) | 合成示例 | [ ] |
| [restricted_unlock_fixture.json](../../fixtures/d_class/phase1/restricted_unlock_fixture.json) | 合成示例 | [ ] |
| [lint_cninfo_d_class_phase1_schema.py](../../lab/lint_cninfo_d_class_phase1_schema.py) | **10/10 PASS** | [ ] |

缺口确认（已知）：仅 **3/7** 组件有 fixture — signoff 后 implementation 扩其余 4 组件。

---

## 10. Signoff Exclusions（批准包不包含）

- [ ] 确认 **无** live endpoint validation
- [ ] 确认 **无** harvest / market data ingestion
- [ ] 确认 **无** PDF / DB / MinIO / RAG
- [ ] 确认 **无** testing_stable_sample 升级
- [ ] 确认 **无** A/B/C-class 输出修改

---

## Human Signoff Block

| 项 | 填写 |
|----|------|
| Reviewer | _待填写_ |
| Review date | _待填写_ |
| Decision | `APPROVE` / `APPROVE_WITH_CAVEAT` / `DEFER` |
| Caveats | _待填写_ |
| Next gate（若批准） | `d_class_phase1_schema_freeze_signoff_gate = READY_FOR_IMPLEMENTATION` |

**当前 gate（不变）：**

```text
d_class_phase1_schema_freeze_gate = READY_FOR_APPROVAL
```

**不是 PASS** — 人工 signoff 前不得启动 implementation。
