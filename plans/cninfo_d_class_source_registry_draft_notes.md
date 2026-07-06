# CNINFO D 类 Source Registry YAML Draft Notes

_最后更新：2026-07-05_

> **YAML 文件：** [config/cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml)  
> **设计权威：** [cninfo_d_class_source_registry_design.md](cninfo_d_class_source_registry_design.md)  
> **映射审查：** [cninfo_d_class_source_to_schema_mapping_review.md](cninfo_d_class_source_to_schema_mapping_review.md)

---

## 1. 目的

本 YAML 是 **Era C Phase 3** 产出的 **registry 设计草案**，将 Phase 2 已验证的 **10** 个 `testing_stable_sample` source 整理为机器可读配置，供未来：

- 采集任务编排；
- validation plan 生成；
- schema 映射与 ETL 设计；
- 字段漂移检测。

**性质：**

| 是 | 不是 |
|----|------|
| 设计草案（`status: design_only`） | 生产 runtime 配置 |
| Phase 2 验证结论的结构化沉淀 | 数据库 migration |
| 与 `cninfo_table_sources.yaml` 互补 | `verified` 状态声明 |

**红线：** 不入库、不写 migration、**不写 verified**（YAML 中 `verified: false` 仅为显式禁止标记）。

---

## 2. 覆盖范围

### 2.1 已纳入（10）

| source_id | source_layer | target_logical_table |
|-----------|--------------|----------------------|
| disclosure_schedule | disclosure_schedule | d_disclosure_schedule |
| restricted_shares_unlock | company_event | d_company_event |
| block_trade | company_event | d_company_event |
| margin_trading | company_metric_daily | d_company_metric_daily |
| abnormal_trading | company_event | d_company_event |
| equity_pledge | company_event | d_company_event |
| shareholder_change | company_event | d_company_event |
| executive_shareholding | company_event | d_company_event |
| shareholder_data | company_metric_periodic | d_company_metric_periodic |
| fund_industry_allocation | industry_aggregate | d_industry_aggregate |

### 2.2 未纳入（config candidate）

| source_id | 原因 |
|-----------|------|
| ipo_query | api_url 待 DevTools |
| szse_calendar | api_url 待 DevTools |

### 2.3 source_layer 分布

| source_layer | 数量 | source |
|--------------|------|--------|
| company_event | **6** | restricted_shares_unlock, block_trade, abnormal_trading, equity_pledge, shareholder_change, executive_shareholding |
| company_metric_daily | **1** | margin_trading |
| company_metric_periodic | **1** | shareholder_data |
| disclosure_schedule | **1** | disclosure_schedule |
| industry_aggregate | **1** | fund_industry_allocation |

### 2.4 target_logical_table 分布

| target_logical_table | 数量 |
|----------------------|------|
| d_company_event | 6 |
| d_company_metric_daily | 1 |
| d_company_metric_periodic | 1 |
| d_disclosure_schedule | 1 |
| d_industry_aggregate | 1 |

---

## 3. 关键设计选择

### 3.1 Registry 与 schema 分离

- **Registry YAML** — source 元数据、API、模式、字段置信度、验证血缘；
- **Schema draft** — 逻辑表形状（`d_company_event` 等）；
- **映射审查** — 逐 source 标准列 vs raw_only 决策。

三者通过 `source_id` + `target_logical_table` + `mapping.standard_fields` 关联。

### 3.2 raw_record_json 必须保留

所有 10 源均设 `mapping.raw_record_required: true`。

原因：

- `d_company_event` 通用列无法覆盖 executive 职务、质押说明、异常交易 detail[] 等；
- 单位与多列度量（block_trade 四列）需 raw 回溯；
- 字段漂移检测需对比 live key set 与 registry `fields`。

### 3.3 不硬标准化 uncertain / not_visible 字段

| 类别 | 处理 |
|------|------|
| `fields.confirmed` | 可映射标准列 |
| `fields.raw_only` | 仅保留在 raw JSON |
| `fields.not_visible_on_ui` | 不进入生产标准列 |
| `fields.uncertain` | 禁止自动标准化（如 F005N、F008N） |

### 3.4 fund_industry_allocation 单独处理

- `source_layer: industry_aggregate`
- `company_code_available: false`
- `mapping.exclude_from_schemas: [d_company_event, d_company_metric_periodic]`
- 主键维度：industry_code + report_period

---

## 4. supported_modes 说明

### 4.1 shareholder_change

| mode_id | params | 含义 |
|---------|--------|------|
| `type_inc` | `type=inc`, `tdate=` | 增持明细 |
| `type_desc` | `type=desc` | 减持明细（**不是** `type=dec`） |
| `type_desc_with_tdate` | `type=desc`, `tdate=` | 带日期的减持 |

`event_subtype`：`increase` / `decrease`，写入 `d_company_event.event_subtype`。

### 4.2 executive_shareholding

| mode_id | 稳定性 | 说明 |
|---------|--------|------|
| `oneMonth_varyType_b` | tested | 默认；UI「增持」 |
| `threeMonth_varyType_b` | tested | 更长窗口 |
| `oneMonth_varyType_s` | tested | varyType 语义待 UI 确认 |
| `other_timeMark_varyType` | pending | 其他组合待确认 |

### 4.3 margin_trading

| mode_id | role | 说明 |
|---------|------|------|
| `detailList_default` | **primary** | POST empty body；**不显式传 date** |
| `market_summary` | auxiliary_observation_only | `marginTrading/market?tdate=`；**不作主 source**；复测 HTTP 500 |

### 4.4 其他单模式 source

- **tdate 类：** restricted_shares_unlock, block_trade, equity_pledge
- **rdate 类：** shareholder_data；fund_industry_allocation（可选）
- **sdate/edate 分页：** abnormal_trading
- **form 分页：** disclosure_schedule

---

## 5. 字段置信度处理

YAML `fields` 五类与 ingestion status model 对齐：

| YAML 键 | confirmation_status | 能否进标准 schema 列 |
|---------|---------------------|----------------------|
| `confirmed` | ui_confirmed | 是（仍非 verified） |
| `candidate` | candidate | 仅候选，需复核 |
| `raw_only` | internal_text 或刻意保留 | 否，仅 raw JSON |
| `not_visible_on_ui` | not_visible_on_ui | 否 |
| `uncertain` | uncertain | 否 |

**当前 10 源字段统计（约）：**

| source | confirmed | raw_only | not_visible | uncertain |
|--------|-----------|----------|-------------|-----------|
| disclosure_schedule | 9 | 1 | 1 | 0 |
| restricted_shares_unlock | 7 | 0 | 0 | 0 |
| block_trade | 7 | 0 | 0 | 0 |
| margin_trading | 8 | 6 | 6 | 1 |
| abnormal_trading | 11 | 5 | 4 | 0 |
| equity_pledge | 9 | 1 | 1 | 0 |
| shareholder_change | 8 | 0 | 0 | 0 |
| executive_shareholding | 10 | 5 | 5 | 1 |
| shareholder_data | 9 | 0 | 0 | 0 |
| fund_industry_allocation | 6 | 0 | 0 | 0 |

---

## 6. 与 cninfo_table_sources.yaml 的关系

| 文件 | 角色 |
|------|------|
| `cninfo_table_sources.yaml` | Phase 2 **验证脚本**驱动配置（endpoint discovery、小样本跑） |
| `cninfo_d_class_source_registry_draft.yaml` | Phase 3 **设计/registry** 草案（分层、映射、字段置信度、稳定性血缘） |

未来可合并或由 lint 脚本校验两者 `source_id` / `api.url` 一致性；**当前保持双文件**，避免改动验证脚本依赖。

---

## 7. 剩余 caveat

| 项 | 说明 |
|----|------|
| margin_trading | F003N/F007N/F008N/F010V–F012V/MEMO 未标准化；market summary 非主源 |
| abnormal_trading | buyTotal/sellTotal 等顶层字段 raw_only；detail[] 待 d_event_party_detail |
| executive_shareholding | 通用 event 列不足；F005N uncertain；其他 varyType 待确认 |
| equity_pledge | F008V internal text |
| disclosure_schedule | latest_time raw_only |
| block_trade / equity_pledge / fund_industry | 部分日期 empty_but_valid_response |
| 全源 | `testing_stable_sample` ≠ 生产就绪 ≠ verified |

---

## 8. 下一步

1. **JSON Schema draft** — 按逻辑表定义 record JSON shape（非 DB）；
2. **Registry lint 脚本设计** — 校验 YAML 与 mapping review / cninfo_table_sources.yaml 一致性；
3. **可选** — 将 registry draft 转为 `d_source_registry` 行（仍不入生产库）；
4. **暂不入库、不写 migration、不写 verified**。

---

## 9. 产物索引

| 文件 | 说明 |
|------|------|
| [cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml) | 本 YAML 草案 |
| [cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md) | 逻辑表定义 |
| [cninfo_d_class_ingestion_status_model.md](cninfo_d_class_ingestion_status_model.md) | 状态枚举 |
| [cninfo_table_sources_phase2_current_final_summary.md](../outputs/validation/cninfo_table_sources_phase2_current_final_summary.md) | Phase 2 验证总结 |
