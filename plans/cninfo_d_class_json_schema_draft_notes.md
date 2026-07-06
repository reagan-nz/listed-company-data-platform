# CNINFO D 类 JSON Schema Draft Notes

_最后更新：2026-07-05_

> **Schema 目录：** [schemas/d_class/](../schemas/d_class/)  
> **逻辑表设计：** [cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md)  
> **Registry YAML：** [config/cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml)  
> **映射审查：** [cninfo_d_class_source_to_schema_mapping_review.md](cninfo_d_class_source_to_schema_mapping_review.md)

---

## 1. 目的

本目录下的 JSON Schema 文件定义 **CNINFO D 类逻辑表的 record shape**（字段类型、枚举、最小必填集、lineage 字段），用于：

- 文档化「入库前」结构化记录长什么样；
- 未来 validation / lint / ETL 契约测试；
- 从逻辑模型 **反推** SQL migration（**当前不做**）。

**性质：** 设计草案；**不是**数据库 migration；**不入库**；**不写 verified**。

**JSON Schema 版本：** [JSON Schema draft-07](https://json-schema.org/draft-07/schema)（`$schema: http://json-schema.org/draft-07/schema#`）。选用 draft-07 因其工具链成熟；未使用 2020-12 以避免 `$defs` 命名差异。

---

## 2. Schema 覆盖范围

| # | 文件 | 逻辑表 | 主要用途 |
|---|------|--------|----------|
| 1 | `d_source_registry.schema.json` | d_source_registry | 单条 source registry 条目（对齐 YAML `sources[]` 元素） |
| 2 | `d_source_validation_run.schema.json` | d_source_validation_run | 单次 validation / stability test case |
| 3 | `d_field_semantics.schema.json` | d_field_semantics | raw_field → standard_field 语义行 |
| 4 | `d_company_event.schema.json` | d_company_event | 6 个 company event source |
| 5 | `d_company_metric_daily.schema.json` | d_company_metric_daily | margin_trading（block_trade 可选 ETL） |
| 6 | `d_company_metric_periodic.schema.json` | d_company_metric_periodic | shareholder_data |
| 7 | `d_disclosure_schedule.schema.json` | d_disclosure_schedule | disclosure_schedule |
| 8 | `d_industry_aggregate.schema.json` | d_industry_aggregate | fund_industry_allocation |
| 9 | `d_event_party_detail.schema.json` | d_event_party_detail | abnormal_trading detail[]（逻辑层，ETL 未实现） |
| 10 | `d_raw_record_snapshot.schema.json` | d_raw_record_snapshot | fetch 级原始 JSON 快照 |

**共 10 个 schema 文件**，对应 schema draft 中的 10 张逻辑表。

---

## 3. 设计原则

| 原则 | 说明 |
|------|------|
| **raw_record_json 必须保留** | 所有业务 record schema 均含 `raw_record_json: object`；多数为 required |
| **不确定字段不 required** | executive F005N、margin F003N 等不进 required |
| **source-specific 优先 raw** | 标准列只映射 ui_confirmed；其余留在 raw |
| **分表不分源** | event / metric_daily / metric_periodic / schedule / industry_aggregate 各用独立 schema |
| **不写 verified** | `source_status` enum **无** verified；registry schema 中 `verified` 仅允许 `const: false` |
| **additionalProperties: false** | 业务表 schema 禁止未声明字段（扩展走 raw_record_json 或新版本 schema） |

---

## 4. Required 字段原则

### 4.1 全表共性（lineage）

以下字段在 **业务 record** schema 中 **声明为 property**；是否 required 因表而异：

| 字段 | 典型 required |
|------|----------------|
| `source_id` | 是 |
| `raw_record_json` | 业务表：是 |
| `raw_record_hash` | 业务表：是 |
| `query_params` | 否（validation_run：是） |
| `fetch_time` | 否 |
| `source_status` | 否 |
| `field_confidence` | 否 |
| `created_at` | 否 |

### 4.2 各表 required 摘要

| Schema | 逻辑 id | 其他 required |
|--------|---------|----------------|
| d_company_event | event_id | source_id, **company_code**, event_type, raw_* |
| d_company_metric_daily | metric_id | source_id, company_code, trade_date, metric_name, metric_value, raw_* |
| d_company_metric_periodic | metric_id | source_id, company_code, report_period, metric_name, metric_value, raw_* |
| d_disclosure_schedule | schedule_id | source_id, company_code, raw_* |
| d_industry_aggregate | aggregate_id | source_id, industry_code, report_period, metric_name, metric_value, raw_* — **无 company_code** |
| d_event_party_detail | party_detail_id | event_id, source_id, raw_* |
| d_source_validation_run | run_id | source_id, fetch_status, query_params, fetch_time |
| d_raw_record_snapshot | snapshot_id | source_id, raw_*, fetch_time, fetch_status |
| d_field_semantics | — | source_id, raw_field, confirmation_status |
| d_source_registry | source_id | source_name, source_layer, target_logical_table, api, status, mapping |

### 4.3 company_code on d_company_event

**required：** 是。

**理由：** 当前六个 event source（restricted_shares_unlock、block_trade、abnormal_trading、equity_pledge、shareholder_change、executive_shareholding）均含 `SECCODE` / `secCode`；Phase 2 验证 `company_code_available=yes`。行业 aggregate **不**使用本 schema。

---

## 5. 与 source registry 的关系

```
config/cninfo_d_class_source_registry_draft.yaml
        │
        │  d_source_registry.schema.json validates each sources[] entry
        │
        ├── target_logical_table ──► 选择业务 JSON Schema
        │         d_company_event
        │         d_company_metric_daily
        │         d_company_metric_periodic
        │         d_disclosure_schedule
        │         d_industry_aggregate
        │
        ├── fields.confirmed ──► 可映射到标准列
        ├── fields.raw_only / uncertain ──► 仅 raw_record_json
        └── mapping.standard_fields ──► ETL 字段名对照
```

| source_id | target_logical_table | JSON Schema |
|-----------|----------------------|-------------|
| disclosure_schedule | d_disclosure_schedule | d_disclosure_schedule.schema.json |
| restricted_shares_unlock | d_company_event | d_company_event.schema.json |
| block_trade | d_company_event (+ optional metric) | d_company_event.schema.json |
| margin_trading | d_company_metric_daily | d_company_metric_daily.schema.json |
| abnormal_trading | d_company_event (+ party detail) | d_company_event.schema.json |
| equity_pledge | d_company_event | d_company_event.schema.json |
| shareholder_change | d_company_event | d_company_event.schema.json |
| executive_shareholding | d_company_event | d_company_event.schema.json |
| shareholder_data | d_company_metric_periodic | d_company_metric_periodic.schema.json |
| fund_industry_allocation | d_industry_aggregate | d_industry_aggregate.schema.json |

---

## 6. 仍未解决的问题

| 问题 | 说明 |
|------|------|
| **event source-specific extension** | executive_name / position / relationship 无通用 event 列；靠 raw 或未来 extension 表 |
| **abnormal_trading detail 子表** | `d_event_party_detail` 已定义 schema，ETL 未实现；主 event 仍保留完整 detail[] |
| **block_trade 双归属** | 主路径 `d_company_event`；可选 ETL 至 `d_company_metric_daily` |
| **margin_trading 无显式 date** | trade_date 来自 record `TRADEDATE`，非 query param |
| **executive_shareholding 部分 raw** | DECLAREDATE、F004N、F005N(uncertain) 等不映射标准列 |
| **narrow metric 表** | 一行 raw 拆多行 metric；schema 描述的是 **拆后** 单行 |
| **registry vs runtime** | YAML draft 与 `cninfo_table_sources.yaml` 双文件；需未来 lint 对齐 |

---

## 7. 枚举对照（ingestion status model）

| 概念 | Schema 位置 |
|------|-------------|
| source_status | 业务表 `definitions.source_status` |
| fetch_status | validation_run、raw_record_snapshot |
| field_confidence | 业务表 `definitions.field_confidence` |
| confirmation_status | d_field_semantics |

**禁止：** `verified` 不作为任何 enum 值。

---

## 8. 下一步

1. **Registry lint 脚本设计** — 校验 YAML 条目符合 `d_source_registry.schema.json`；`target_logical_table` 与 `mapping` 一致；
2. **Schema validation plan** — 用 Phase 2 小样本 record 实例做 draft-07 校验（离线 fixture，不联网）；
3. **入库时** — 从 JSON Schema 反推 SQL migration（**当前不做**）；
4. **暂不入库、不写 migration、不写 verified**。

---

## 9. 产物索引

| 路径 | 说明 |
|------|------|
| [schemas/d_class/](../schemas/d_class/) | 10 个 `.schema.json` |
| [cninfo_d_class_json_schema_draft_notes.md](cninfo_d_class_json_schema_draft_notes.md) | 本文件 |
| [cninfo_d_class_source_registry_draft_notes.md](cninfo_d_class_source_registry_draft_notes.md) | Registry YAML 说明 |
