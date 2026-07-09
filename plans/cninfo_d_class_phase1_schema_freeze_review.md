# CNINFO D 类 Phase 1 Schema Freeze Review

_最后更新：2026-07-09_

> **性质：** 离线设计评审；不调用 CNINFO；不 live；不 harvest；不写 verified；不升级 testing_stable_sample。  
> **输入：** [cninfo_d_class_market_data_architecture_plan.md](cninfo_d_class_market_data_architecture_plan.md) · [cninfo_d_class_source_discovery_plan.md](cninfo_d_class_source_discovery_plan.md) · [cninfo_d_class_readiness_matrix.csv](../outputs/validation/cninfo_d_class_readiness_matrix.csv) · [cninfo_d_class_event_object_schema.md](cninfo_d_class_event_object_schema.md)

---

## 1. Purpose

本评审冻结 D-class **Phase 1 市场行为事件 schema v1**：覆盖 **7** 个市场行为组件的产品字段契约与统一 `market_event` 信封，不冻结 harvest runner、数据库、MinIO 或全市场采集。

Phase 1 要回答：

- 每个市场行为组件的 **required / recommended / future** 字段是什么？
- 统一 `market_event` 信封如何承载 `event_id`、lineage、`quality_status`？
- 组件 payload 如何映射到既有 `schemas/d_class/` 逻辑表？

Phase 1 **不**回答：全量历史回填、B-class PDF 证据自动挂接、verified 升级、testing_stable_sample 变更。

---

## 2. Frozen Components Overview

| # | component | source_id | 逻辑表 | Phase 2 状态 |
|---|-----------|-----------|--------|----------------|
| 1 | margin_trading | `margin_trading` | `d_company_metric_daily` | testing_stable_sample（**不升级**） |
| 2 | block_trade | `block_trade` | `d_company_event` | testing_stable_sample |
| 3 | restricted_shares_unlock | `restricted_shares_unlock` | `d_company_event` | testing_stable_sample |
| 4 | disclosure_schedule | `disclosure_schedule` | `d_disclosure_schedule` | testing_stable_sample |
| 5 | equity_pledge | `equity_pledge` | `d_company_event` | testing_stable_sample |
| 6 | shareholder_change | `shareholder_change` | `d_company_event` | testing_stable_sample |
| 7 | executive_shareholding | `executive_shareholding` | `d_company_event` | testing_stable_sample |

字段决策明细见 [cninfo_d_class_phase1_field_decision_matrix.csv](../outputs/validation/cninfo_d_class_phase1_field_decision_matrix.csv)。

---

## 3. Component Field Freeze

### 3.1 margin_trading — 融资融券行为

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| company_code | **required** | 证券代码 |
| company_name | recommended | 简称；可缺失 |
| trade_date | **required** | 交易日 |
| financing_balance | **required** | 融资余额 |
| financing_buy_amount | recommended | 融资买入额 |
| margin_balance | **required** | 融券余额 |
| margin_sell_amount | recommended | 融券卖出量 |
| total_margin_balance | **required** | 融资融券余额合计 |
| source_endpoint | **required** | `data20/marginTrading/detailList` |
| retrieval_time | **required** | 抓取时间 ISO8601 |
| quality_status | **required** | pass / caveat / blocked / needs_review |

**Caveat：** F00xN 单位语义 medium confidence；harvest 须保留 `raw_record_json`。

---

### 3.2 block_trade — 大宗交易事件

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| company_code | **required** | 证券代码 |
| company_name | recommended | 简称 |
| trade_date | **required** | 交易日期 |
| transaction_price | **required** | 成交均价 |
| transaction_volume | **required** | 成交量 |
| transaction_amount | **required** | 成交金额 |
| buyer | **future** | Phase 2 endpoint 无买卖双方明细 |
| seller | **future** | 同上 |
| source_endpoint | **required** | `data20/ints/statistics` |
| quality_status | **required** | QA 门控 |

---

### 3.3 restricted_shares_unlock — 限售解禁事件

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| company_code | **required** | 证券代码 |
| company_name | recommended | 简称 |
| announcement_date | recommended | 公告日期 |
| unlock_date | **required** | 解禁日期 |
| unlock_amount | **required** | 解禁数量 |
| unlock_ratio | **required** | 解禁比例 |
| tradable_amount | recommended | 可流通数量；F008N 语义 medium |
| quality_status | **required** | QA 门控 |

---

### 3.4 disclosure_schedule — 预约披露 / 信息披露日历

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| company_code | **required** | 证券代码 |
| company_name | recommended | 简称 |
| report_type | **required** | 报告类型 / 报告期 |
| planned_date | **required** | 首次预约披露日 |
| actual_date | recommended | 实际披露日 |
| change_history | recommended | f003/f004/f005 变更日序列 |
| quality_status | **required** | QA 门控 |

---

### 3.5 equity_pledge — 股权质押风险

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| company_code | **required** | 证券代码 |
| company_name | recommended | 简称 |
| pledge_date | **required** | 质押日期 |
| pledged_shares | **required** | 质押股数 |
| pledge_ratio | **required** | 质押比例 |
| pledgee | recommended | 质权人 |
| pledge_status | **future** | 状态字段映射未 freeze |
| quality_status | **required** | QA 门控 |

---

### 3.6 shareholder_change — 股东增减持

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| company_code | **required** | 证券代码 |
| company_name | recommended | 简称 |
| shareholder_name | **required** | 股东名称 |
| change_type | **required** | inc / desc |
| change_amount | **required** | 变动数量 |
| change_ratio | recommended | 变动比例 |
| change_date | **required** | 变动日期 |
| quality_status | **required** | QA 门控 |

---

### 3.7 executive_shareholding — 高管持股变化

| 字段 | Phase 1 级别 | 说明 |
|------|-------------|------|
| company_code | **required** | 证券代码 |
| executive_name | **required** | 高管姓名 |
| position | recommended | 职务 |
| change_type | **required** | 变动类型 |
| change_amount | **required** | 变动数量 |
| change_date | **required** | 变动日期 |
| quality_status | **required** | QA 门控 |

---

## 4. Unified market_event Envelope

所有组件在 Phase 1 输出中须包裹统一信封（见 [cninfo_d_class_event_object_schema.md](cninfo_d_class_event_object_schema.md)）：

| 字段 | Phase 1 级别 |
|------|-------------|
| event_id | **required** |
| company_code | **required** |
| event_type | **required** |
| event_time | **required** |
| source_endpoint | **required** |
| source_record_id | **required** |
| event_status | **required** |
| quality_status | **required** |
| lineage | recommended |

---

## 5. Registry / Schema Alignment

| component | registry source_id | target_logical_table | 本轮 registry YAML |
|-----------|-------------------|----------------------|-------------------|
| margin_trading | margin_trading | d_company_metric_daily | **未修改** |
| block_trade | block_trade | d_company_event | **未修改** |
| restricted_shares_unlock | restricted_shares_unlock | d_company_event | **未修改** |
| disclosure_schedule | disclosure_schedule | d_disclosure_schedule | **未修改** |
| equity_pledge | equity_pledge | d_company_event | **未修改** |
| shareholder_change | shareholder_change | d_company_event | **未修改** |
| executive_shareholding | executive_shareholding | d_company_event | **未修改** |

既有 `schemas/d_class/*.schema.json` **未修改**；Phase 1 freeze 为产品层字段契约，通过 field matrix + phase1 fixtures + lint 校验。

---

## 6. Phase 1 Fixtures（schema examples only）

| 文件 | 路径 |
|------|------|
| margin_trading | [fixtures/d_class/phase1/margin_trading_fixture.json](../fixtures/d_class/phase1/margin_trading_fixture.json) |
| block_trade | [fixtures/d_class/phase1/block_trade_fixture.json](../fixtures/d_class/phase1/block_trade_fixture.json) |
| restricted_unlock | [fixtures/d_class/phase1/restricted_unlock_fixture.json](../fixtures/d_class/phase1/restricted_unlock_fixture.json) |

合成示例数据；**非** CNINFO 真值；**无** live 抓取。

---

## 7. Offline Lint

脚本：[lab/lint_cninfo_d_class_phase1_schema.py](../lab/lint_cninfo_d_class_phase1_schema.py)

校验项：required 字段存在 · event 信封关系 · source endpoint 映射 · quality_status 枚举。

---

## 8. Risks & Deferrals

| 风险 | 影响 | Phase 1 处理 |
|------|------|--------------|
| block_trade 无 buyer/seller | 产品字段缺口 | 标 **future**；汇总字段仍 required |
| margin_trading 无日期参数 | 全量快照 | harvest 架构延后 |
| equity_pledge pledge_status | 映射不确定 | 标 **future** |
| executive varyType 枚举 | change_type 口径 | recommended 文档化 |
| disclosure change_history 结构 | 数组 vs 扁平 | recommended JSON array |

---

## 9. Red Lines（本轮）

- **No CNINFO** · **No live** · **No harvest** · **No PDF**
- **No DB** · **No MinIO** · **No RAG**
- **No verified** · **No testing_stable_sample upgrade**
- **No A/B/C-class output modification**

---

## Gate

```text
d_class_phase1_schema_freeze_gate = READY_FOR_APPROVAL
```

**不是 PASS** — 须人工批准后方可进入 Phase 1 implementation / tiny harvest 规划。
