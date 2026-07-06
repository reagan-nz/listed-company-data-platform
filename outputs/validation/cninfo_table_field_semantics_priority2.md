# CNINFO D 类 Priority-2 字段语义与 UI 对照表

- 生成时间：2026-07-05（含 fund_industry_allocation / shareholder_data 回填）
- 配置：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)
- 验证摘要：[cninfo_table_sources_validation_summary.md](cninfo_table_sources_validation_summary.md)
- 机器可读映射：[cninfo_table_field_semantics_priority2.csv](cninfo_table_field_semantics_priority2.csv)
- Priority-1 对照：[cninfo_table_field_semantics_ui_check_summary.md](cninfo_table_field_semantics_ui_check_summary.md)

---

## 1. 目的

**Era C Phase 2 priority-2** 在 endpoint discovery 与小样本 `sample_ok` 之后，对 D 类 source 的 raw 字段进行 **人工 UI 表头对照**，产出 `confirmed_standard_field` 与 `semantic_confidence_after`。

- **不写 verified**；`confirmed` / `high` 仅表示人工 UI 对照通过。
- 未确认字段不得进入生产标准 schema。

---

## 2. 总体进度

| source_id | query_mode | confirmed | not_visible_on_ui | uncertain |
|-----------|------------|-----------|-------------------|-----------|
| equity_pledge | — | **9** | **1** (F008V) | 0 |
| shareholder_change | inc | **8** | 0 | 0 |
| shareholder_change | desc | **8** | 0 | 0 |
| executive_shareholding | detail_varyType_b | **11** | **5** | **1** (F005N) |
| fund_industry_allocation | — | **6** | 0 | 0 |
| shareholder_data | rdate_20260331 | **9** | 0 | 0 |
| **合计** | | **51** | **6** | **1** |

**priority-2 testing source 总数：5**（equity_pledge、shareholder_change、executive_shareholding、fund_industry_allocation、shareholder_data）。

---

## 3. equity_pledge（股权质押）

- **page_url**：`url=data/person-stock-data-tables`（股权质押 tab）
- **api**：`POST .../equityPledge/list?tdate=`
- **UI 对照状态**：9 confirmed + 1 not_visible_on_ui

| raw_field | ui_label_observed | confirmed_standard_field | status | confidence |
|-----------|-------------------|--------------------------|--------|------------|
| SECCODE | 股票代码 | `company_code` | confirmed | high |
| SECNAME | 股票简称 | `company_name` | confirmed | high |
| DECLAREDATE | 公告日期 | `announcement_date` | confirmed | high |
| F018N | 累计质押率(%) | `cumulative_pledge_ratio_percent` | confirmed | high |
| F001V | 出质人 | `pledgor` | confirmed | high |
| F003V | 质权人 | `pledgee` | confirmed | high |
| F006N | 质押数量(万股) | `pledged_shares_10k_shares` | confirmed | high |
| F007N | 占总股本比例(%) | `pledge_ratio_to_total_share_capital_percent` | confirmed | high |
| F012N | 质押解除数量(万股) | `released_pledge_shares_10k_shares` | confirmed | high |
| F008V | — | `pledge_description_text` | not_visible_on_ui | medium |

---

## 4. shareholder_change（股东增减持）

- **api**：`POST .../shareholeder/detail?type=`（**shareholeder** 拼写）
- **双模式**：`type=inc` 增持 / `type=desc` 减持（不是 `type=dec`）
- 各模式 8 字段 confirmed / high（见 CSV `query_mode` inc/desc）

---

## 5. executive_shareholding（高管持股）

- **page_url**：`url=data/person-stock-data-tables`（高管持股 tab）
- **api**：`POST .../leader/detail?timeMark=oneMonth&varyType=b`
- **query_mode**：`detail_varyType_b`（明细表；`varyType=b` 对应 UI「增持」筛选项）
- **小样本**：sample_rows=842，field_count=16，records path=`data.records`
- **recommended_status**：**testing**（不写 verified）

### 5.1 变动明细 UI 表头（已对照）

页面明细列包括：证券代码、证券简称、变动日期、股份变动人、变动数量、成交均价、董监高姓名、职务、变动人与董监高的关系、变动原因。

| raw_field | ui_label_observed | confirmed_standard_field | status | confidence |
|-----------|-------------------|--------------------------|--------|------------|
| SECCODE | 证券代码 | `company_code` | confirmed | high |
| SECNAME | 证券简称 | `company_name` | confirmed | high |
| ENDDATE | 变动日期 | `shareholding_change_date` | confirmed | high |
| HUMANNAME | 董监高姓名 | `executive_name` | confirmed | high |
| F001V | 股份变动人 | `share_change_person` | confirmed | high |
| F002V | 职务 | `executive_position` | confirmed | high |
| F003V | 变动人与董监高的关系 | `relationship_to_executive` | confirmed | high |
| F006N | 变动数量 | `changed_shares` | confirmed | high |
| F008N | 成交均价 | `average_transaction_price` | confirmed | high |
| F010V | 变动原因 | `change_reason` | confirmed | high |
| DECLAREDATE | — | `announcement_date` | not_visible_on_ui | medium |
| F004N | — | — | not_visible_on_ui | low |
| F005N | — | `transaction_amount_candidate` | uncertain | medium |
| F007N | — | — | not_visible_on_ui | low |
| F009N | — | — | not_visible_on_ui | low |
| F011V | — | `information_source_or_announcement_type_candidate` | not_visible_on_ui | medium |

**说明：** `F001V`（股份变动人）与 `HUMANNAME`（董监高姓名）样本中常相同，但 UI 为独立列，语义应区分保留。

### 5.2 高管持股变动汇总 tab（非主 source）

页面还存在 **「高管持股变动汇总」** tab，UI 表头包括：

- 变动统计区间
- 证券代码
- 证券简称
- 变动类型
- 高管持股变动数量合计(万股)

该汇总表 **不是** 当前 `leader/detail` 主 source 的验证对象。后续如抓到独立 Network endpoint，可拆为 `executive_shareholding_summary` source。

---

## 6. fund_industry_allocation（基金行业配置）

- **page_url**：`url=data/person-stock-data-tables`（基金行业配置 tab）
- **api**：`POST .../fund/industry`（无 query params，empty body）
- **层级**：**industry-level aggregate**，不是 company-level source；后续不要归入 company event
- **小样本**：sample_rows=**19**，observed_total_rows=**19**，field_count=**6**，records path=`data.records`
- **recommended_status**：**testing**（不写 verified）

| raw_field | ui_label_observed | confirmed_standard_field | status | confidence |
|-----------|-------------------|--------------------------|--------|------------|
| F001V | 行业编码 | `industry_code` | confirmed | high |
| F002V | 所属行业名称 | `industry_name` | confirmed | high |
| ENDDATE | 报告期 | `report_period` | confirmed | high |
| F003N | 基金覆盖家数(只) | `fund_coverage_count` | confirmed | high |
| F004N | 行业规模(亿元) | `industry_scale_100m_yuan` | confirmed | high |
| F005N | 占净资产比例(%) | `net_asset_ratio_percent` | confirmed | high |

**维度可得性：** `company_code_available` = **no**；`date_available` = **yes**；`amount_available` = **yes**

---

## 7. shareholder_data（股东数据）

- **page_url**：`url=data/person-stock-data-tables`（股东数据 tab）
- **api**：`POST .../shareholeder/data?rdate=20260331`（**shareholeder** 拼写）
- **层级**：company-level periodic shareholder structure data
- **小样本**：sample_rows=**5255**，observed_total_rows=**5255**，field_count=**9**，records path=`data.records`
- **recommended_status**：**testing**（不写 verified）

| raw_field | ui_label_observed | confirmed_standard_field | status | confidence |
|-----------|-------------------|--------------------------|--------|------------|
| SECCODE | 股票代码 | `company_code` | confirmed | high |
| SECNAME | 股票简称 | `company_name` | confirmed | high |
| ENDDATE | 变动日期 | `shareholder_report_date` | confirmed | high |
| F001N | 本期股东人数 | `current_shareholder_count` | confirmed | high |
| F002N | 上期股东人数 | `previous_shareholder_count` | confirmed | high |
| F003N | 股东人数增幅(%) | `shareholder_count_change_percent` | confirmed | high |
| F004N | 本期人均持股数量(股) | `current_avg_shares_per_holder` | confirmed | high |
| F005N | 上期人均持股数量(股) | `previous_avg_shares_per_holder` | confirmed | high |
| F006N | 人均持股数量增幅(%) | `avg_shares_per_holder_change_percent` | confirmed | high |

**维度可得性：** `company_code_available` = **yes**；`date_available` = **yes**；`amount_available` = **yes**

---

## 8. 结论

- **equity_pledge**：UI 对照已收口（9 confirmed）。
- **shareholder_change**：inc + desc 双模式 UI 对照已收口（各 8 confirmed）。
- **executive_shareholding**：明细核心字段 UI 对照已完成（**11 confirmed**）；DECLAREDATE / F004N / F005N / F007N / F009N / F011V 保留为 not_visible_on_ui 或 candidate。
- **fund_industry_allocation**：6 字段全部 UI confirmed；**industry-level aggregate**，非 company event。
- **shareholder_data**：9 字段全部 UI confirmed；company-level 定期股东结构数据。
- **varyType=b** 当前对应 UI「增持」；其他 varyType 后续可测。
- **不写 verified**。

---

## 9. 下一步

1. 测试 executive_shareholding 其他 `varyType` / `timeMark` 组合。
2. 继续 priority-2：`ipo_query` / `szse_calendar` / `fund_holding` endpoint discovery。
3. 可选：高管持股变动汇总 tab 独立 endpoint 探测（`executive_shareholding_summary`）。
4. 可选：priority-2 多日期稳定性小样本复测（含 fund_industry_allocation / shareholder_data）。
