# CNINFO D 类 Source → Schema 映射审查

_最后更新：2026-07-05_

> **性质：** 映射审查与缺口清单，不是 migration、不是生产 schema 锁定。  
> **前置：** [cninfo_d_class_source_registry_design.md](cninfo_d_class_source_registry_design.md) · [cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md) · [cninfo_d_class_ingestion_status_model.md](cninfo_d_class_ingestion_status_model.md)  
> **验证：** [cninfo_table_sources_phase2_current_final_summary.md](../outputs/validation/cninfo_table_sources_phase2_current_final_summary.md)

---

## 1. 目的

- **Phase 2** 已验证 **10** 个 `testing_stable_sample` source（blocked=0、schema_changed=0、verified=0）。
- **Phase 3** 已有 registry、逻辑 schema、ingestion status model 三份设计草案。
- **本文档** 逐 source 审查 **source → 逻辑表** 映射，明确：
  - 进入哪张逻辑表；
  - 哪些字段进入 **标准列**（仅 `ui_confirmed` / 高置信）；
  - 哪些字段 **只保留** `raw_record_json`；
  - 哪些 source 需 **event / metric 拆分**；
  - 哪些字段 **仍不能标准化**。

**目标：** 避免把 schedule、industry aggregate、metric 截面与 company event 混入同一张宽表。

---

## 2. 总体映射表

| source_id | source_layer | source_category | target_logical_table | event_or_metric | standardized_fields（摘要） | raw_only_fields（摘要） | mapping_confidence | notes |
|-----------|--------------|-----------------|----------------------|-----------------|---------------------------|-------------------------|-------------------|-------|
| disclosure_schedule | disclosure_schedule | report_schedule | **d_disclosure_schedule** | schedule | company_code, org_id, report_period, 各披露日期 | latest_time | **high** | records_path=`prbookinfos` |
| restricted_shares_unlock | company_event | share_unlock | **d_company_event** | event | unlock_date, unlock_shares, unlock_ratio, tradable_shares | — | **high** | 7 字段基本 UI confirmed |
| block_trade | company_event | block_trade | **d_company_event**（主） | event + optional daily metric | trade_date, count/volume/amount/avg_price | — | **high** | 可选同步 **d_company_metric_daily** |
| margin_trading | company_metric_daily | margin_trading | **d_company_metric_daily** | metric | 5 个融资/融券核心指标（窄表多行） | F003N,F007N,F008N,F010V–F012V,MEMO | **medium** | 一行 raw → 多 metric 行 |
| abnormal_trading | company_event | abnormal_trading | **d_company_event**（主） | event | trade_date, reason, 顶层标识 | buyTotal,sellTotal,detail[]→未来子表 | **medium** | detail 不宜硬塞主 event 列 |
| equity_pledge | company_event | equity_pledge | **d_company_event** | event | pledgor, pledgee, pledged/released shares & ratios | F008V | **high** | F008V=internal_text |
| shareholder_change | company_event | shareholder_change | **d_company_event** | event | inc/desc 标准 event 列 | — | **high** | event_subtype=increase/decrease |
| executive_shareholding | company_event | executive_shareholding | **d_company_event** | event | 11 个 UI confirmed 列（含职务/关系） | DECLAREDATE,F004N,F005N,F007N,F009N,F011V | **medium** | 通用 event 列不足以表达全部语义 |
| shareholder_data | company_metric_periodic | shareholder_structure | **d_company_metric_periodic** | metric | 6 个股东结构指标（窄表多行） | — | **high** | 按 rdate 全市场截面 |
| fund_industry_allocation | industry_aggregate | fund_industry_allocation | **d_industry_aggregate** | metric（行业） | industry_code, 3 个行业指标 | — | **high** | **无** company_code；不进 event |

**mapping_confidence 说明：**

| 值 | 含义 |
|----|------|
| **high** | 主表选择明确；标准字段均 ui_confirmed |
| **medium** | 主表明确，但存在 raw_only / 子结构 / 通用列不足 |
| **low** | 存在重大语义缺口（当前 10 源无 low） |

---

## 3. company event source 审查

### 3.1 restricted_shares_unlock

| 项 | 内容 |
|----|------|
| **target** | `d_company_event` |
| **event_type** | `restricted_shares_unlock` |
| **records_path** | `data.records` |

**标准字段映射（→ d_company_event 或同行 raw 拆列）：**

| raw_field | standard_field | 映射到通用列 |
|-----------|----------------|--------------|
| SECCODE | `company_code` | `company_code` |
| SECNAME | `company_name` | `company_name` |
| DECLAREDATE | `announcement_date` | `announcement_date` |
| F003D | `actual_unlock_date` | `event_date` |
| F004N | `actual_unlock_shares` | `primary_amount`（单位：股） |
| F005N | `actual_unlock_ratio_percent` | `primary_ratio` |
| F008N | `actual_tradable_shares` | 扩展：建议保留 raw + 可选 `secondary_amount` 候选 |

**raw_only：** 无必须 raw_only 字段；F008N 与 F004N 样本曾同值，UI 已区分，映射 confidence **high**。

**不能标准化：** 无 blocking 缺口。

---

### 3.2 block_trade

| 项 | 内容 |
|----|------|
| **target（主）** | `d_company_event` |
| **target（可选）** | `d_company_metric_daily` — 时间序列指标视图 |
| **event_type** | `block_trade` |

**设计选择：**

| 方案 | 说明 |
|------|------|
| **A. d_company_event（当前采纳）** | 每日每公司一行大宗交易汇总作为 market_behavior event |
| **B. d_company_metric_daily** | 将 F001N–F004N 拆为窄表 metric，便于时序分析 |

**建议：** Phase 3 **先** 入主 event 表；`primary_amount` / `primary_ratio` 不足以表达四列语义，**标准列 + raw_record_json 并存**。若产品需要 metric 看板，ETL 二次写入 `d_company_metric_daily`（不重复请求 CNINFO）。

**标准字段：**

| raw_field | standard_field | 通用列 |
|-----------|----------------|--------|
| SECCODE / SECNAME | company_code / company_name | ✓ |
| TRADEDATE | trade_date | `event_date` |
| F001N | `block_trade_count` | 扩展列或 raw |
| F002N | `trade_volume_10k_shares` | `primary_amount`（万股） |
| F003N | `trade_amount_10k_yuan` | 扩展列 |
| F004N | `average_trade_price_yuan_per_share` | `primary_price` |

**raw_only：** 无；四列均已 UI confirmed。

**event / metric 拆分：** **可选** 双写；非必须。

**mapping_confidence：** **high**

---

### 3.3 abnormal_trading

| 项 | 内容 |
|----|------|
| **target** | `d_company_event` |
| **event_type** | `abnormal_trading` |
| **records_path** | `marketList` |

**标准字段（主 event 行）：**

| raw_field | standard_field | 通用列 |
|-----------|----------------|--------|
| secCode / secName | company_code / company_name | ✓ |
| tradeTime | trade_date | `event_date` |
| type | `public_information_reason` | `event_subtype` |

**raw_only / 不强行标准化：**

| raw_field | 原因 |
|-----------|------|
| buyTotal, sellTotal | not_visible_on_ui；顶层汇总未在 UI 主表展示 |
| buyPercent, sellPercent | 同上 |
| detail[] | **嵌套数组**；每元素含营业部买卖 — 见 §7 `d_event_party_detail` |

**detail 处理原则：**

- 主 `d_company_event` 行：`raw_record_json` **完整保留** `detail[]`；
- 未来若需营业部级查询：拆 `d_event_party_detail`，**不**在 Phase 3 建物理表。

**mapping_confidence：** **medium**（主表 OK，party 子结构待扩展表）

---

### 3.4 equity_pledge

| 项 | 内容 |
|----|------|
| **target** | `d_company_event` |
| **event_type** | `equity_pledge` |

**标准字段：**

| raw_field | standard_field | 通用列 |
|-----------|----------------|--------|
| SECCODE / SECNAME | company_code / company_name | ✓ |
| DECLAREDATE | announcement_date | `announcement_date` |
| F001V | pledgor | `actor_name` |
| F003V | pledgee | `counterparty_name` |
| F006N | pledged_shares_10k_shares | `primary_amount` |
| F007N | pledge_ratio_to_total_share_capital_percent | `primary_ratio` |
| F012N | released_pledge_shares_10k_shares | 扩展列（解除质押） |
| F018N | cumulative_pledge_ratio_percent | 扩展列（累计质押率） |

**raw_only：**

| raw_field | 状态 |
|-----------|------|
| F008V | `pledge_description_text` — **internal_text**，仅 raw |

**不能标准化：** F008V 不进入标准列。

**mapping_confidence：** **high**

---

### 3.5 shareholder_change

| 项 | 内容 |
|----|------|
| **target** | `d_company_event` |
| **event_type** | `shareholder_change` |
| **query_mode** | `type=inc` → `event_subtype=increase`；`type=desc` → `decrease` |

**标准字段：**

| raw_field | standard_field | 通用列 |
|-----------|----------------|--------|
| SECCODE / SECNAME | company_code / company_name | ✓ |
| DECLAREDATE | announcement_date | `announcement_date` |
| VARYDATE | share_increase_date / share_decrease_date | `event_date` |
| F002V | shareholder_name | `actor_name` |
| F004N | increased_shares / decreased_shares | `primary_amount` |
| F005N | increase_ratio_percent / decrease_ratio_percent | `primary_ratio` |
| F007V | increase_price / decrease_price | `primary_price`（可为区间文本） |

**raw_only：** 无（8 字段均 ui_confirmed）。

**supported_modes：** registry 已记录 inc/desc；映射时 **必须** 带 `query_mode` / `event_subtype`。

**mapping_confidence：** **high**

---

### 3.6 executive_shareholding

| 项 | 内容 |
|----|------|
| **target** | `d_company_event` |
| **event_type** | `executive_shareholding_change` |
| **query_mode** | `timeMark` + `varyType`（如 `oneMonth_varyType_b`） |

**标准字段（ui_confirmed → 标准列或 source 扩展）：**

| raw_field | standard_field | 建议落点 |
|-----------|----------------|----------|
| SECCODE / SECNAME | company_code / company_name | 通用列 |
| ENDDATE | shareholding_change_date | `event_date` |
| HUMANNAME | executive_name | **source 扩展**（通用列无此字段） |
| F001V | share_change_person | `actor_name` |
| F002V | executive_position | **source 扩展** |
| F003V | relationship_to_executive | **source 扩展** |
| F006N | changed_shares | `primary_amount` |
| F008N | average_transaction_price | `primary_price` |
| F010V | change_reason | `event_subtype` 或扩展文本 |

**raw_only / candidate（不进标准列）：**

| raw_field | 状态 |
|-----------|------|
| DECLAREDATE | not_visible_on_ui |
| F004N | not_visible_on_ui |
| F005N | **uncertain** |
| F007N | not_visible_on_ui |
| F009N | not_visible_on_ui |
| F011V | not_visible_on_ui（候选公告来源） |

**缺口：** `d_company_event` 通用列 **无法** 表达 executive_name / position / relationship；**必须** 保留 `raw_record_json`，或未来 `d_company_event_extension`（§8）。

**mapping_confidence：** **medium**

---

## 4. company metric source 审查

### 4.1 margin_trading

| 项 | 内容 |
|----|------|
| **target** | `d_company_metric_daily` **唯一主表** |
| **不应** | `d_company_event`（日度指标非离散事件） |

**一行 CNINFO record → 多行 metric（窄表）：**

| raw_field | metric_name | unit | UI |
|-----------|-------------|------|-----|
| TRADEDATE | — | — | 作为 `trade_date` |
| SECCODE / SECNAME | — | — | 维度列 |
| F001N | `financing_balance_yuan` | 元 | confirmed |
| F002N | `financing_buy_amount_yuan` | 元 | confirmed |
| F004N | `securities_lending_balance_shares` | 股 | confirmed |
| F006N | `securities_lending_sell_volume_shares` | 股 | confirmed |
| F009N | `margin_trading_balance_yuan` | 元 | confirmed |

**raw_only（不进 metric_name 映射）：**

| raw_field | 状态 |
|-----------|------|
| F003N | not_visible_on_ui |
| F007N | not_visible_on_ui |
| F008N | uncertain |
| F010V, F011V, F012V | not_visible_on_ui |
| MEMO | pending |

**不能标准化：** 上表字段在语义明确前 **不得** 进入 `d_company_metric_daily.metric_name`。

**附属 source：** `marginTrading/market` 非主 source；若未来注册，应单独 `source_id`，**禁止**与 detailList 混映射。

**mapping_confidence：** **medium**（核心 5 指标 high，余下 raw_only）

---

### 4.2 shareholder_data

| 项 | 内容 |
|----|------|
| **target** | `d_company_metric_periodic` |
| **date 维度** | `report_period` ← ENDDATE / 请求 `rdate` |

**一行 → 多行 metric：**

| raw_field | metric_name | unit |
|-----------|-------------|------|
| F001N | `current_shareholder_count` | 人 |
| F002N | `previous_shareholder_count` | 人 |
| F003N | `shareholder_count_change_percent` | % |
| F004N | `current_avg_shares_per_holder` | 股 |
| F005N | `previous_avg_shares_per_holder` | 股 |
| F006N | `avg_shares_per_holder_change_percent` | % |

**raw_only：** 无（9 字段均 ui_confirmed）。

**mapping_confidence：** **high**

---

## 5. schedule source 审查

### disclosure_schedule

| 项 | 内容 |
|----|------|
| **target** | `d_disclosure_schedule`（**不是** d_company_event） |
| **records_path** | `prbookinfos` |

**标准字段：**

| raw_field | standard_field |
|-----------|----------------|
| seccode | company_code |
| secname | company_name |
| orgId | org_id |
| f001d_0102 | report_period |
| f002d_0102 | first_scheduled_disclosure_date |
| f003d_0102 | first_changed_disclosure_date |
| f004d_0102 | second_changed_disclosure_date |
| f005d_0102 | third_changed_disclosure_date |
| f006d_0102 | actual_disclosure_date |

**raw_only：**

| raw_field | 原因 |
|-----------|------|
| latest_time | not_visible_on_ui；`latest_update_time` 仅 candidate |

**与 A 类联动：** `org_id` + `company_code` + `report_period` → 报告 PDF timeline。

**mapping_confidence：** **high**

---

## 6. industry aggregate source 审查

### fund_industry_allocation

| 项 | 内容 |
|----|------|
| **target** | `d_industry_aggregate` |
| **禁止** | `d_company_event`、`d_company_metric_periodic`（无 company 维度） |

**一行 → 最多 3 行 metric（窄表）：**

| raw_field | standard_field / metric_name | unit |
|-----------|------------------------------|------|
| F001V | industry_code | — |
| F002V | industry_name | — |
| ENDDATE | report_period | 日期 |
| F003N | fund_coverage_count | 只 |
| F004N | industry_scale_100m_yuan | 亿元 |
| F005N | net_asset_ratio_percent | % |

**raw_only：** 无。

**说明：** 不需要 `company_code`；registry `source_layer=industry_aggregate`。

**mapping_confidence：** **high**

---

## 7. 需要新增的逻辑表建议

### 7.1 d_event_party_detail（建议新增，Phase 3+ 逻辑层）

**用途：** `abnormal_trading.detail[]` 营业部买卖明细；未来类似「多方参与」事件。

| 字段 | 说明 |
|------|------|
| party_detail_id | 逻辑主键 |
| event_id | FK → d_company_event |
| source_id | abnormal_trading |
| party_role | buy_side / sell_side |
| broker_name | detail.buyOrgName / sellOrgName |
| buy_amount_yuan | 对应 buyTotal 类字段 |
| sell_amount_yuan | 对应 sellTotal 类字段 |
| raw_record_json | 单条 detail 元素 |
| field_confidence | |

**当前阶段：** 仅在逻辑 schema 中 **登记**；不建物理表、不写 migration。主 event 行 **必须** 保留完整 `raw_record_json`。

**结论：** **建议新增** 逻辑表定义；**暂不** 实现 ETL。

### 7.2 d_source_query_mode（暂不必单独建表）

`shareholder_change`（inc/desc）、`executive_shareholding`（timeMark/varyType）的多模式已由：

- registry `supported_modes`；
- `d_company_event.query_mode` / `event_subtype`；
- `d_field_semantics.query_mode`

覆盖。**结论：** 暂不单独建 `d_source_query_mode` 表。

---

## 8. 标准字段不足问题

`d_company_event` 通用列（`primary_amount`、`actor_name` 等）**无法** 覆盖所有 source 语义：

| 缺口类型 | 涉及 source | 示例 |
|----------|-------------|------|
| 角色多方 | equity_pledge | pledgor / pledgee |
| 人与职务 | executive_shareholding | executive_name, position, relationship |
| 多金额列 | block_trade | 笔数 / 量 / 额 / 价 四列 |
| 累计 vs 单次 | equity_pledge | cumulative_pledge_ratio vs pledged_shares |
| 营业部明细 | abnormal_trading | detail[] |
| 价格区间文本 | shareholder_change | F007V 可能为区间 |

**建议策略：**

1. **通用列** 只映射各 source **最核心** 1–2 个度量 + 身份 + 日期；
2. **ui_confirmed 但无通用列** 的字段 → `raw_record_json` + 可选 `d_field_semantics` 索引；
3. **未来** 若需查询性能：按 source 建 `d_company_event_extension_{source}` 或 JSON 列 + GIN（不在本阶段）；
4. **单位** 必须在 `d_field_semantics.unit` 或 metric 行 `unit` 中显式记录，禁止静默换算。

---

## 9. 当前不建议做的事情

| 不建议 | 原因 |
|--------|------|
| 为每个 source 单独建实体表 | 10 源可收敛到 5 类逻辑表 + 扩展 |
| 把 fund_industry_allocation 放入 company_event | 无 company_code，语义错误 |
| 把 unknown / uncertain 字段硬标准化 | 如 F005N、F008N、buyTotal |
| 把 testing_stable_sample 写成 verified | Era C 红线 |
| 写 SQL migration / 建库 | 当前仅设计阶段 |
| 丢弃 raw_record_json | source 差异大，通用列必然信息损失 |

---

## 10. 结论

| 结论项 | 判断 |
|--------|------|
| schema draft 方向 | **合理** — 五类逻辑表分流正确 |
| d_company_event | **必须** 保留 `raw_record_json` 以兼容 source 差异 |
| abnormal_trading | 未来需要 **d_event_party_detail**（逻辑层先登记） |
| block_trade | 具备 **event + daily metric** 双重属性；主路径 event，metric 可选二次 ETL |
| margin_trading | **仅** metric_daily；禁止标为 event |
| executive_shareholding | 通用 event 列不足；11 confirmed 字段中 3+ 需扩展或 raw |
| 10 源 mapping_confidence | 6× high、3× medium、0× low |

### Phase 3 下一步建议

1. 将本审查表回填 registry 示例的 `confirmed_fields` / `raw_only_fields` 列表；
2. 产出 **registry YAML draft**（10 源机器可读，仍不入库）；
3. 产出 **JSON Schema draft**（按逻辑表定义 record 形状，非 DB）；
4. 为 `abnormal_trading` 在 [cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md) 补充 `d_event_party_detail` 逻辑表节；
5. **暂不** 全量抓取、**不写** verified。

---

## 11. 产物索引

| 文件 | 关系 |
|------|------|
| [cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md) | 逻辑表定义；§11 映射表由本文档细化 |
| [cninfo_table_field_semantics_priority1.md](../outputs/validation/cninfo_table_field_semantics_priority1.md) | P1 标准字段来源 |
| [cninfo_table_field_semantics_priority2.md](../outputs/validation/cninfo_table_field_semantics_priority2.md) | P2 标准字段来源 |
| [cninfo_table_field_semantics_ui_check_summary.md](../outputs/validation/cninfo_table_field_semantics_ui_check_summary.md) | UI confirmed 权威列表 |
