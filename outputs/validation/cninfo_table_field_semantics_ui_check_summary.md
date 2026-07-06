# CNINFO D 类 Priority-1 字段语义 UI 对照总结

- 生成时间：2026-07-05（离线整理）
- 前置：5 个 testing source、48 个 top-level 字段语义候选
- 输入清单：[cninfo_table_field_semantics_ui_checklist.csv](cninfo_table_field_semantics_ui_checklist.csv)
- 检查说明：[cninfo_table_field_semantics_ui_checklist.md](cninfo_table_field_semantics_ui_checklist.md)
- 语义候选表：[cninfo_table_field_semantics_priority1.csv](cninfo_table_field_semantics_priority1.csv) / [cninfo_table_field_semantics_priority1.md](cninfo_table_field_semantics_priority1.md)
- Source 验证：[cninfo_table_sources_priority1_summary.md](cninfo_table_sources_priority1_summary.md)

---

## 1. 阶段目标

本阶段在 **Era C Phase 2 priority-1**（endpoint 可达、`sample_ok`、`testing`）之上，通过 **人工截图对照 CNINFO 网页 UI 表头 / 筛选项 / 详情展开列**，将接口 **raw field**（如 `F001N`、`f002d_0102`、`detail.buyOrgName`）与可观测中文标签对齐，从而：

- 提升字段语义可信度（`semantic_confidence_after`）；
- 产出 `confirmed_standard_field` 标准命名候选；
- 区分 **UI 已确认**、**UI 不可见**、**仍不确定** 三类，避免将猜测字段误作生产 schema。

**不写 verified**；`confirmed` 仅表示人工 UI 对照通过，不等于全市场或长期稳定。

---

## 2. 总体进度

### 2.1 Checklist 规模

| 维度 | 数量 | 说明 |
|------|------|------|
| 设计 checklist 行数 | **39** | semantics `needs_confirmation=yes` 33 行 + abnormal_trading `detail.*` 嵌套 6 行 |
| CSV 实际数据行 | **38** | `secCode` / `secName` / `tradeTime` 三字段在 semantics 表中为 high、未单独占 checklist 行（§3.5 仍记为已确认） |
| top-level 语义候选（priority-1） | **48** | 见 [cninfo_table_field_semantics_priority1.md](cninfo_table_field_semantics_priority1.md) |

### 2.2 Checklist 对照状态（CSV 38 行）

| confirmation_status | 行数 |
|---------------------|------|
| **confirmed** | **28** |
| **not_visible_on_ui** | **8** |
| **uncertain** | **1** |
| **pending** | **1** |
| **合计** | **38** |

按 source 拆分 **confirmed**：

| source_id | confirmed |
|-----------|-----------|
| block_trade | 4 |
| restricted_shares_unlock | 5 |
| disclosure_schedule | 6 |
| margin_trading | 5 |
| abnormal_trading | 8（`type` + `detail` + 6 嵌套） |
| **合计** | **28** |

### 2.3 仍 pending 的字段

| source_id | raw_field | 说明 |
|-----------|-----------|------|
| margin_trading | `MEMO` | 备注列；样本常空，尚未截图确认是否在 UI 展示 |

---

## 3. 已确认 source

以下字段均为 **confirmation_status = confirmed**、**semantic_confidence_after = high**（`latest_time` 除外，见 disclosure_schedule）。

### block_trade

| raw_field | UI 标签 | confirmed_standard_field |
|-----------|---------|--------------------------|
| F001N | 成交笔数 | `block_trade_count` |
| F002N | 成交数量(万股) | `trade_volume_10k_shares` |
| F003N | 成交金额(万元) | `trade_amount_10k_yuan` |
| F004N | 成交均价(元/股) | `average_trade_price_yuan_per_share` |

单位已明确；可用 **成交金额(万元) / 成交数量(万股) ≈ 成交均价(元/股)** 交叉验证。

### restricted_shares_unlock

| raw_field | UI 标签 | confirmed_standard_field |
|-----------|---------|--------------------------|
| DECLAREDATE | 公告日期 | `announcement_date` |
| F003D | 实际解除限售日期 | `actual_unlock_date` |
| F004N | 实际解除限售数量(股) | `actual_unlock_shares` |
| F005N | 实际解除限售比例(%) | `actual_unlock_ratio_percent` |
| F008N | 实际可流通数量(股) | `actual_tradable_shares` |

### disclosure_schedule

| raw_field | UI 标签 | confirmed_standard_field | 备注 |
|-----------|---------|--------------------------|------|
| f001d_0102 | 报告期（页面筛选项） | `report_period` | 非表格列，为筛选项语义 |
| f002d_0102 | 首次预约 | `first_scheduled_disclosure_date` | |
| f003d_0102 | 初次变更 | `first_changed_disclosure_date` | |
| f004d_0102 | 二次变更 | `second_changed_disclosure_date` | |
| f005d_0102 | 三次变更 | `third_changed_disclosure_date` | |
| f006d_0102 | 实际披露 | `actual_disclosure_date` | |
| latest_time | — | `latest_update_time` | **not_visible_on_ui**；表头未显示，保留 **medium** |

### abnormal_trading

主表（含 semantics 高置信字段，后三者在 checklist 外单独确认）：

| raw_field | UI 标签 | confirmed_standard_field |
|-----------|---------|--------------------------|
| secCode | 证券代码 | `company_code` |
| secName | 证券简称 | `company_name` |
| type | 信息公开原因 | `public_information_reason` |
| tradeTime | 交易日 | `trade_date` |
| detail | 详情展开营业部买卖明细 | `broker_branch_trading_detail` |
| detail.buyOrgName | 营业部（买入） | `buy_broker_branch_name` |
| detail.buyOrgBuyTotal | 买入金额（买入侧，元） | `buy_side_buy_amount_yuan` |
| detail.buyOrgSellTotal | 卖出金额（买入侧，元） | `buy_side_sell_amount_yuan` |
| detail.sellOrgName | 营业部（卖出） | `sell_broker_branch_name` |
| detail.sellOrgBuyTotal | 买入金额（卖出侧，元） | `sell_side_buy_amount_yuan` |
| detail.sellOrgSellTotal | 卖出金额（卖出侧，元） | `sell_side_sell_amount_yuan` |

**说明：** `buyTotal` / `sellTotal` / `buyPercent` / `sellPercent` 为顶层汇总字段，当前 **主表与详情展开均未直接显示**，标记为 **not_visible_on_ui**，不强行确认。

### margin_trading

个股明细（`detailList`）已确认核心列：

| raw_field | UI 标签 | confirmed_standard_field |
|-----------|---------|--------------------------|
| F001N | 融资余额(元) | `financing_balance_yuan` |
| F002N | 融资买入额(元) | `financing_buy_amount_yuan` |
| F004N | 融券余量(股) | `securities_lending_balance_shares` |
| F006N | 融券卖出量(股) | `securities_lending_sell_volume_shares` |
| F009N | 融资融券余额(元) | `margin_trading_balance_yuan` |

**说明：** 页面上方存在 **融资融券交易总量** 汇总表（market summary，非 `detailList` 主 source），同 raw 字段名但单位为 **亿元**、语义不同；后续可拆为 `margin_trading_market_summary`。

以下字段 **仍为 not_visible_on_ui 或 uncertain**，未进入 confirmed：

| raw_field | 状态 | 备注 |
|-----------|------|------|
| F003N | not_visible_on_ui | 个股明细 UI 未显示；样本常空 |
| F007N | not_visible_on_ui | 同上 |
| F008N | uncertain | 候选 `securities_lending_balance_amount_candidate`；F009N ≈ F001N + F008N 待算术验证 |
| F010V | not_visible_on_ui | 候选 `market_name`；值如「深圳」，非表格列 |
| F011V | not_visible_on_ui | 候选 `market_or_board_code_candidate` |
| F012V | not_visible_on_ui | 候选 `stock_type`；值如「A股」，非表格列 |

---

## 4. 仍未完全确认字段

| 类别 | 字段 | 状态 | 建议 |
|------|------|------|------|
| margin_trading | F003N / F007N | not_visible_on_ui | 查 market summary 或接口文档；勿作生产标准字段 |
| margin_trading | F008N | uncertain | F001N + F008N ≈ F009N 算术验证 |
| margin_trading | F010V / F011V / F012V | not_visible_on_ui | 保留为 internal / candidate |
| margin_trading | MEMO | **pending** | 补截图确认备注列 |
| abnormal_trading | buyTotal / sellTotal / buyPercent / sellPercent | not_visible_on_ui | 顶层汇总 UI 不可见；仅保留接口 raw |
| disclosure_schedule | latest_time | not_visible_on_ui (medium) | 疑为接口更新时间 |

---

## 5. 结论

- **UI 对照显著提高了 priority-1 字段语义质量**：28 行 checklist 字段 + abnormal_trading 主表三字段（secCode/secName/tradeTime）已形成 **confirmed / high** 映射，覆盖五个 source 的核心业务列（日期、数量、金额、比例、营业部明细等）。
- **多数核心业务字段已 confirmed / high**；原先 `medium`/`low` 的 `F00xN`、`f00xd_0102` 等经 UI 对照后置信度普遍上调。
- **仍不写 verified**：未做多日期稳定性复测、未全市场抽样、未官方文档背书。
- **未确认字段不得进入生产标准字段**：`not_visible_on_ui`、`uncertain`、`pending` 字段只能作为 **candidate** 或 **internal field** 保留在采集层，下游 pipeline 不得当作 confirmed schema 使用。

---

## 6. 下一步

1. **priority-1 多日期小样本稳定性复测**
   - 每个 testing source 选 **2–3 个日期**；
   - 不翻页、不全量抓取；
   - 验证：**endpoint 是否稳定**、**字段 key 是否稳定**、**records JSON path 是否稳定**。
2. 复测通过后再进入 **priority-2 source discovery**（shareholder_change、equity_pledge、executive_shareholding、ipo_query、szse_calendar）。
3. 可选收尾：`MEMO` 补截图；`F008N` 算术验证；将 confirmed 行回写 semantics CSV（另次任务）；拆分 `margin_trading_market_summary`。

**暂不全量抓取、暂不入库、不写 verified。**
