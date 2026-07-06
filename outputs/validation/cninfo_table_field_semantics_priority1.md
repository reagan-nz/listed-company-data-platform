# CNINFO D 类 Priority-1 字段语义确认表

- 生成时间：2026-07-05（离线整理）
- 配置：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)
- Priority-1 验证总结：[cninfo_table_sources_priority1_summary.md](cninfo_table_sources_priority1_summary.md)
- 机器可读映射：[cninfo_table_field_semantics_priority1.csv](cninfo_table_field_semantics_priority1.csv)

---

## 1. 目的

**Era C Phase 2 priority-1** 已验证 5 个 D 类固定表格 source 的 **endpoint 可访问性**（public JSON、HTTP 200、`sample_ok`、`testing`）。

本文档 **不是新抓取**，而是对 `config/cninfo_table_sources.yaml` 中各 source **`expected_fields`** 的 **字段语义整理**：

- 将 **raw_field** 映射到 **standard_field_candidate**；
- 标注 **semantic_confidence** 与 **needs_confirmation**；
- 区分 **较确定** vs **仅候选** vs **未知**；
- **不写 verified**；uncertain 字段不得写成 confirmed。

---

## 2. 总体规则

| semantic_confidence | 含义 |
|-------------------|------|
| **high** | 字段名或值模式非常明确（如 `seccode`、`TRADEDATE`） |
| **medium** | 高度可能，但仍需页面表头或文档确认 |
| **low** | 只能从少量样本猜测 |
| **unknown** | 暂不能判断 |

| needs_confirmation | 含义 |
|--------------------|------|
| **no** | 当前可当作工程映射使用（仍非 verified） |
| **yes** | 必须经 UI 表头 / 算术校验 / 官方说明后再固化 |

| field_role | 用途 |
|------------|------|
| company_identifier / company_name | 公司维度 |
| date | 日期/时间 |
| amount / ratio / count | 数值 |
| category / market_code | 分类/市场 |
| nested_detail | 嵌套结构 |
| unknown | 待定 |

**禁止：** 将 `medium`/`low` 字段在下游 pipeline 中当作 **confirmed schema** 使用；**不写 verified**。

### 统计摘要（48 个 top-level 字段）

| 维度 | 数量 |
|------|------|
| **总字段行** | **48** |
| semantic_confidence **high** | **21** |
| **medium** | **19** |
| **low** | **8** |
| **unknown** | **0** |
| needs_confirmation **yes** | **33** |
| needs_confirmation **no** | **15** |

| source_id | 字段数 | high | medium | low |
|-----------|--------|------|--------|-----|
| disclosure_schedule | 10 | 4 | 3 | 3 |
| restricted_shares_unlock | 7 | 3 | 4 | 0 |
| block_trade | 7 | 3 | 4 | 0 |
| margin_trading | 15 | 6 | 4 | 5 |
| abnormal_trading | 9 | 5 | 4 | 0 |

---

## 3. 各 source 字段语义表

### 3.1 disclosure_schedule（预约披露）

| raw_field | standard_field_candidate | confidence | needs_confirmation | notes |
|-----------|-------------------------|------------|-------------------|-------|
| seccode | company_code | high | no | |
| secname | company_name | high | no | |
| orgId | cninfo_org_id | high | no | |
| f001d_0102 | report_period_section_date | high | yes | 与 `sectionTime` 参数一致 |
| f002d_0102 | scheduled_disclosure_date | medium | yes | 预约披露日 |
| f003d_0102 | disclosure_change_date_candidate | low | yes | 变更日；常空 |
| f004d_0102 | disclosure_change_date_candidate | low | yes | 变更日；常空 |
| f005d_0102 | disclosure_change_date_candidate | low | yes | 变更日；常空 |
| f006d_0102 | current_or_final_disclosure_date | medium | yes | 与 f002d 关系待确认 |
| latest_time | latest_update_time | medium | yes | 样本多为 null |

### 3.2 restricted_shares_unlock（限售解禁）

| raw_field | standard_field_candidate | confidence | needs_confirmation | notes |
|-----------|-------------------------|------------|-------------------|-------|
| SECCODE | company_code | high | no | |
| SECNAME | company_name | high | no | |
| DECLAREDATE | announcement_date | medium | yes | 公告日 vs 解禁日 |
| F003D | unlock_date | high | yes | 与 `tdate` 一致 |
| F004N | unlock_shares | medium | yes | 解禁股数 |
| F005N | unlock_ratio | medium | yes | 解禁比例 |
| F008N | actual_tradable_or_unlock_shares | medium | yes | 与 F004N 样本同值，区分待确认 |

### 3.3 block_trade（大宗交易）

| raw_field | standard_field_candidate | confidence | needs_confirmation | notes |
|-----------|-------------------------|------------|-------------------|-------|
| SECCODE | company_code | high | no | |
| SECNAME | company_name | high | no | |
| TRADEDATE | trade_date | high | no | |
| F001N | block_trade_count | medium | yes | 成交笔数 |
| F002N | trade_volume | medium | yes | 成交量 |
| F003N | trade_amount | medium | yes | 成交金额 |
| F004N | average_trade_price | medium | yes | **算术校验**：F003N/F002N≈F004N（600519 样本） |

### 3.4 margin_trading（融资融券）

| raw_field | standard_field_candidate | confidence | needs_confirmation | notes |
|-----------|-------------------------|------------|-------------------|-------|
| TRADEDATE | trade_date | high | no | |
| SECCODE | company_code | high | no | |
| SECNAME | company_name | high | no | |
| F001N | financing_balance_candidate | medium | yes | 融资余额候选 |
| F002N | financing_buy_amount_candidate | medium | yes | 融资买入候选 |
| F003N | securities_lending_sell_amount_or_volume_candidate | low | yes | 常 null |
| F004N | securities_lending_balance_or_volume_candidate | low | yes | 融券相关 |
| F006N | securities_lending_related_candidate | low | yes | |
| F007N | securities_lending_related_candidate | low | yes | 常 null |
| F008N | securities_lending_related_candidate | low | yes | |
| F009N | margin_trading_balance_candidate | medium | yes | 融资融券余额合计候选 |
| F010V | market_name | high | no | 如「深圳」 |
| F011V | market_or_board_code | medium | yes | 内部代码 |
| F012V | stock_type | high | no | 如「A股」 |
| MEMO | memo | high | yes | 备注；常 null |

**备注：** `marginTrading/market?tdate=...` 为市场汇总接口，字段集不同，**未纳入**本表。

### 3.5 abnormal_trading（公开信息 / 异常交易）

| raw_field | standard_field_candidate | confidence | needs_confirmation | notes |
|-----------|-------------------------|------------|-------------------|-------|
| secCode | company_code | high | no | |
| secName | company_name | high | no | |
| tradeTime | trade_date | high | no | |
| type | abnormal_type | high | yes | 如「退市整理期」 |
| buyTotal | buy_total | medium | yes | 可空 |
| sellTotal | sell_total | medium | yes | 可空 |
| buyPercent | buy_percent | medium | yes | 可空 |
| sellPercent | sell_percent | medium | yes | 可空 |
| detail | broker_detail | high | yes | 嵌套数组 |

#### detail 嵌套子字段（未单独列入 CSV，语义待确认）

| raw_field（detail[]） | standard_field_candidate | confidence | notes |
|----------------------|-------------------------|------------|-------|
| buyOrgName | buyer_broker_name | medium | 买方营业部 |
| buyOrgBuyTotal | buyer_broker_buy_amount | medium | 字符串金额如 `557,829.99` |
| buyOrgSellTotal | buyer_broker_sell_amount | medium | |
| sellOrgName | seller_broker_name | medium | 卖方营业部 |
| sellOrgBuyTotal | seller_broker_buy_amount | medium | |
| sellOrgSellTotal | seller_broker_sell_amount | medium | |

样本（000004 国华退，2026-07-03）：`detail` 含营业部买卖六元组；顶层 `buyTotal`/`sellTotal` 为 null，明细在嵌套层。

---

## 4. 需要后续确认的字段（重点）

| source | 字段 | 原因 |
|--------|------|------|
| **disclosure_schedule** | f002d_0102, f006d_0102, f003d–f005d_0102 | 预约日 vs 最终日 vs 变更日；空值多 |
| **restricted_shares_unlock** | F004N, F005N, F008N | 股数/比例/可流通量区分 |
| **block_trade** | F001N–F004N | 笔数/量/额/均价及单位 |
| **margin_trading** | F001N–F009N | 融资/融券各口径；F003N/F007N 常空 |
| **abnormal_trading** | buyTotal, sellTotal, buyPercent, sellPercent | 顶层常空；与 detail 关系 |
| **abnormal_trading** | detail.* | 营业部金额字段格式与语义 |

---

## 5. 建议确认方法

| 方法 | 适用 |
|------|------|
| **page_label_needed** | 对照 CNINFO 网页表头（DevTools / 人工 UI） |
| **arithmetic_check** | 如 block_trade：`F003N / F002N ≈ F004N` |
| **value_pattern** | 日期格式、代码位数、比例 0–1 |
| **field_name_obvious** | seccode、TRADEDATE 等 |
| **manual_ui_check_needed** | abnormal_trading `detail` 嵌套 |
| **official_doc_needed** | latest_time、MEMO、交易所口径对照 |

**不建议：** 仅凭单一样本或字段编号猜测后写入生产 schema。

---

## 6. 下一步

1. **UI 表头确认** — 优先 disclosure 日期字段、margin F001N–F009N、unlock F004/F008；
2. **算术/交叉校验** — block_trade 均价；margin F009N 与分项之和；
3. **2–3 日期复测** — 5 个 testing source 稳定性；
4. **priority-2 discovery** — shareholder_change、equity_pledge 等；
5. **暂不入库** — 语义未 elevated 前不建生产表。

---

## 7. 边界

- 基于 priority-1 小样本与 DevTools 观察；**非全量统计**；
- **不写 verified**；`high` ≠ 官方确认；
- 未修改 validation CSV / 脚本 / 数据库 schema。
