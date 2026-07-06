# CNINFO D 类 Schema Draft

_最后更新：2026-07-05_

> **性质：** 逻辑 schema 草案，**不是**真实建表文件、SQL migration 或 ORM 模型。  
> **前置：** [cninfo_d_class_source_registry_design.md](cninfo_d_class_source_registry_design.md)  
> **状态模型：** [cninfo_d_class_ingestion_status_model.md](cninfo_d_class_ingestion_status_model.md)  
> **Phase 2 验证：** [cninfo_table_sources_phase2_current_final_summary.md](../outputs/validation/cninfo_table_sources_phase2_current_final_summary.md)

---

## 1. 设计目标

在 Phase 2 已确认 **10 个** `testing_stable_sample` source 的前提下，设计 **可演进** 的 D 类结构化数据逻辑 schema，用于：

- 区分 event / metric / schedule / industry aggregate 不同数据形态；
- 保留 **raw_record_json** 与字段置信度，避免过早过度标准化；
- 为未来入库（若发生）提供映射蓝图。

**当前不做：** 建库、migration、ORM、全量抓取、production schema 锁定。

---

## 2. 不建议一表装所有 source

CNINFO D 类 source 数据结构差异显著：

| 差异维度 | 示例 |
|----------|------|
| 主键粒度 | 公司 × 事件日 vs 公司 × 交易日 vs 行业 × 报告期 |
| 时间语义 | `tdate` 交易日、`rdate` 报告期末、`sectionTime` 报告期 |
| 嵌套结构 | abnormal_trading 的 `detail[]` 营业部明细 |
| 多模式 | shareholder_change inc/desc；executive_shareholding timeMark/varyType |
| 无 company_code | fund_industry_allocation |

**反模式：** 将所有 source 强行塞进单一 `d_company_event` 宽表，会导致：

- industry aggregate 无法表达；
- margin_trading / shareholder_data 等 metric 被误标为 event；
- 大量 NULL 列与语义漂移。

**原则：** 按 `source_layer` 分流到不同逻辑表；跨表通过 `source_id` + `company_code` / `industry_code` + 时间维度关联。

---

## 3. 建议逻辑表

| # | 逻辑表 | 用途 |
|---|--------|------|
| 1 | `d_source_registry` | source 元数据（registry 持久化形态） |
| 2 | `d_source_validation_run` | 每次 validation / stability 跑次记录 |
| 3 | `d_field_semantics` | raw_field → standard_field 映射与置信度 |
| 4 | `d_company_event` | 公司级离散事件 |
| 5 | `d_company_metric_daily` | 公司 × 交易日指标 |
| 6 | `d_company_metric_periodic` | 公司 × 报告期截面指标 |
| 7 | `d_disclosure_schedule` | 预约披露日程 |
| 8 | `d_industry_aggregate` | 行业级聚合 |
| 9 | `d_raw_record_snapshot` | 可选：fetch 级原始 JSON 快照与 lineage |
| 10 | `d_event_party_detail` | **建议新增（逻辑层）**：event 参与方明细，如 abnormal_trading `detail[]` |

表之间关系（逻辑）：

```
d_source_registry ──< d_source_validation_run
d_source_registry ──< d_field_semantics
d_source_registry ──< d_company_event
d_source_registry ──< d_company_metric_daily
d_source_registry ──< d_company_metric_periodic
d_source_registry ──< d_disclosure_schedule
d_source_registry ──< d_industry_aggregate
d_company_event ──< d_event_party_detail
d_raw_record_snapshot ──> (任意业务表 via raw_record_hash)
```

> **JSON Schema：** [schemas/d_class/](../schemas/d_class/) · [cninfo_d_class_json_schema_draft_notes.md](cninfo_d_class_json_schema_draft_notes.md)  
> **映射审查：** 逐 source 标准列 / raw_only 明细见 [cninfo_d_class_source_to_schema_mapping_review.md](cninfo_d_class_source_to_schema_mapping_review.md)。

---

## 4. d_company_event

### 适用 source

| source_id | event 子类型备注 |
|-----------|------------------|
| restricted_shares_unlock | 解禁事件 |
| block_trade | 日度大宗交易汇总行（事件化存储） |
| abnormal_trading | 含 `detail` 嵌套时可拆子行或 JSON 内嵌 |
| equity_pledge | 质押/解除质押 |
| shareholder_change | inc / desc 用 `event_subtype` 区分 |
| executive_shareholding | varyType / timeMark 记入 query_mode 或 event_subtype |

### 核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_id` | string | 逻辑主键（建议：hash(source_id, mode, company_code, event_date, raw_keys…)） |
| `source_id` | string | FK → registry |
| `query_mode` | string | 如 `inc` / `desc` / `oneMonth_varyType_b` |
| `company_code` | string | SECCODE / seccode |
| `company_name` | string | 简称 |
| `event_date` | date | 事件日：VARYDATE / TRADEDATE / ENDDATE / F003D 等 |
| `announcement_date` | date | DECLAREDATE 等 |
| `event_type` | string | source_category 级 |
| `event_subtype` | string | inc/desc、异常交易 type 码等 |
| `primary_amount` | decimal | 数量/金额候选（标准化列，可空） |
| `primary_ratio` | decimal | 比例候选 |
| `primary_price` | decimal | 价格候选 |
| `actor_name` | string | 股东/高管/出质人等 |
| `counterparty_name` | string | 质权人等 |
| `raw_record_hash` | string | 原始行 hash |
| `raw_record_json` | json | **完整保留** CNINFO 原始行 |
| `field_confidence` | enum | `high` / `mixed` / `low` |
| `source_status` | enum | 采集时 source recommended_status 快照 |
| `created_at` | datetime | 入库时间（未来） |

**设计说明：**

- 不是所有 source 都能填满 `primary_*`；未确认字段 **只进 raw_record_json**。
- abnormal_trading 的 `detail[]` 可： (a) 子表扩展，或 (b) `raw_record_json` 内嵌 + 下游解析。
- block_trade 同时含 metric 特征；默认进 event 表，metric 列可由 ETL 二次抽取到 `d_company_metric_daily`（可选）。

---

## 5. d_company_metric_daily

### 适用 source

| source_id | 说明 |
|-----------|------|
| margin_trading | 主归属：个股融资融券日度明细 |
| block_trade | **可选**：若产品需要纯 metric 视图，可从 event 行抽取 F001N–F004N |

### 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `metric_id` | string | 逻辑主键 |
| `source_id` | string | |
| `company_code` | string | |
| `company_name` | string | |
| `trade_date` | date | TRADEDATE |
| `metric_name` | string | 标准指标名，如 `financing_balance` |
| `metric_value` | decimal | |
| `unit` | string | 元、万股、% 等 |
| `raw_field` | string | 来源 raw 字段名，如 F001N |
| `raw_record_hash` | string | |
| `raw_record_json` | json | |
| `field_confidence` | enum | |
| `created_at` | datetime | |

**margin_trading 映射示例：** 一行 CNINFO record → 多行 metric（F001N 融资余额、F002N 融资买入额…），仅 `ui_confirmed` 字段进入 `metric_name` 映射。

---

## 6. d_company_metric_periodic

### 适用 source

| source_id | 说明 |
|-----------|------|
| shareholder_data | 股东人数、人均持股、环比增幅 |

### 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `metric_id` | string | |
| `source_id` | string | |
| `company_code` | string | |
| `company_name` | string | |
| `report_period` | date | ENDDATE / rdate 对应报告期末 |
| `metric_name` | string | 如 `current_shareholder_count` |
| `metric_value` | decimal | |
| `unit` | string | 人、股、% |
| `raw_field` | string | F001N 等 |
| `raw_record_hash` | string | |
| `raw_record_json` | json | |
| `field_confidence` | enum | |
| `created_at` | datetime | |

**特点：** 按 `rdate` 拉取全市场截面；同一公司多指标拆多行（窄表）优于宽表，便于扩展。

---

## 7. d_disclosure_schedule

### 适用 source

| source_id |
|-----------|
| disclosure_schedule |

### 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `schedule_id` | string | |
| `source_id` | string | |
| `company_code` | string | seccode |
| `company_name` | string | secname |
| `org_id` | string | orgId；桥接 A 类 PDF |
| `report_period` | date | f001d_0102 |
| `first_scheduled_date` | date | f002d_0102 |
| `first_changed_date` | date | f003d_0102 |
| `second_changed_date` | date | f004d_0102 |
| `third_changed_date` | date | f005d_0102 |
| `actual_disclosure_date` | date | f006d_0102 |
| `latest_time_candidate` | datetime | latest_time；待确认 |
| `raw_record_json` | json | |
| `field_confidence` | enum | |
| `created_at` | datetime | |

**records_path：** `prbookinfos`（非 `data.records`）。

---

## 8. d_industry_aggregate

### 适用 source

| source_id |
|-----------|
| fund_industry_allocation |

### 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `aggregate_id` | string | |
| `source_id` | string | |
| `industry_code` | string | F001V |
| `industry_name` | string | F002V |
| `report_period` | date | ENDDATE |
| `metric_name` | string | fund_coverage_count / industry_scale_100m_yuan / net_asset_ratio_percent |
| `metric_value` | decimal | |
| `unit` | string | 只、亿元、% |
| `raw_field` | string | F003N 等 |
| `raw_record_json` | json | |
| `field_confidence` | enum | |
| `created_at` | datetime | |

**无 company_code**；禁止写入 `d_company_event`。

---

## 9. d_field_semantics

跨 source 的字段语义注册表（与 priority-1/2 CSV 对齐）。

| 字段 | 类型 | 说明 |
|------|------|------|
| `source_id` | string | |
| `query_mode` | string | inc/desc、varyType 模式等；无则空 |
| `raw_field` | string | F001N、detail.buyOrgName |
| `standard_field` | string | 标准命名候选 |
| `ui_label` | string | 观测到的中文表头 |
| `field_role` | enum | `identifier` / `date` / `amount` / `ratio` / `text` / `category` |
| `unit` | string | |
| `confidence` | enum | high / medium / low |
| `confirmation_status` | enum | ui_confirmed / candidate / not_visible_on_ui / uncertain / internal_text |
| `notes` | string | |

**数据源：** `cninfo_table_field_semantics_priority1.csv`、`cninfo_table_field_semantics_priority2.csv`。

---

## 10. raw_record_hash / lineage

每条结构化记录应保留：

| 元数据 | 说明 |
|--------|------|
| `source_id` | 来源 |
| `query_params` | 实际请求参数（含 mode） |
| `fetch_time` | 抓取时间 |
| `http_status` | |
| `records_path` | |
| `raw_record_json` | 完整原始行 |
| `raw_record_hash` | 稳定 hash（建议 canonical JSON + source_id + mode） |

`d_raw_record_snapshot`（可选逻辑表）在 fetch 级保存整包响应片段，便于：

- 字段漂移回溯；
- 重放映射逻辑而不重新请求 CNINFO。

**当前阶段不实现** storage / hash 计算流水线。

---

## 11. source → schema 映射表

| source_id | 主逻辑表 | 次要/可选 | source_layer |
|-----------|----------|-----------|--------------|
| disclosure_schedule | d_disclosure_schedule | — | disclosure_schedule |
| restricted_shares_unlock | d_company_event | — | company_event |
| block_trade | d_company_event | d_company_metric_daily（可选） | company_event |
| margin_trading | d_company_metric_daily | — | company_metric_daily |
| abnormal_trading | d_company_event | detail 子结构在 JSON 内 | company_event |
| equity_pledge | d_company_event | — | company_event |
| shareholder_change | d_company_event | 按 query_mode 分行 | company_event |
| executive_shareholding | d_company_event | 按 query_mode 分行 | company_event |
| shareholder_data | d_company_metric_periodic | — | company_metric_periodic |
| fund_industry_allocation | d_industry_aggregate | — | industry_aggregate |

**元数据表（全部 source）：** `d_source_registry`、`d_field_semantics`、`d_source_validation_run`。

**详细映射审查（标准列 vs raw_only、confidence）：** [cninfo_d_class_source_to_schema_mapping_review.md](cninfo_d_class_source_to_schema_mapping_review.md)

---

## 11b. d_event_party_detail（建议新增 · 逻辑层）

### 适用场景

| source_id | 嵌套结构 |
|-----------|----------|
| abnormal_trading | `detail[]` 营业部买卖明细 |

### 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `party_detail_id` | string | 逻辑主键 |
| `event_id` | string | FK → `d_company_event` |
| `source_id` | string | |
| `party_role` | enum | `buy_side` / `sell_side` |
| `broker_name` | string | |
| `buy_amount_yuan` | decimal | 可空 |
| `sell_amount_yuan` | decimal | 可空 |
| `raw_record_json` | json | 单条 detail 元素 |
| `field_confidence` | enum | |
| `created_at` | datetime | |

**Phase 3 原则：** 主 `d_company_event` 行 **仍保留完整** `raw_record_json`（含 `detail[]`）；本表为未来查询优化预留，**不**写 migration。

---

## 12. 当前不做的事情

| 不做 | 原因 |
|------|------|
| 写 SQL migration | Era C 设计阶段 |
| 创建数据库 | 红线：不接 PostgreSQL / MongoDB |
| 接 ORM | 无生产库 |
| 全量抓取 | 仅小样本验证完成 |
| production schema 锁定 | 仍有 candidate / uncertain 字段 |
| 写 **verified** | Era C 红线 |

---

## 13. 与 A 类 / B 类的关系

| 层 | 关系 |
|----|------|
| **A 类** | `d_disclosure_schedule.org_id` + `company_code` → 报告 PDF retrieval timeline |
| **B 类** | 公告 PDF 事件流；与 D 类 `d_company_event` 互补（公告 vs 固定表） |
| **产品** | report timeline + structured event/metric timeline 可并列展示 |
