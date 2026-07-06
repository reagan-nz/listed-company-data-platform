# CNINFO D 类 Priority-2 当前阶段总结

- 生成时间：2026-07-05（含 fund_industry_allocation / shareholder_data）
- 配置：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)
- Priority-1 收口：[cninfo_table_sources_priority1_summary.md](cninfo_table_sources_priority1_summary.md)
- 字段语义 UI 对照：[cninfo_table_field_semantics_priority2.md](cninfo_table_field_semantics_priority2.md)

---

## 1. 阶段目标

**Era C Phase 2 priority-2** 在 priority-1 五个 `testing_stable_sample` source 之后，继续扩展 **公司事件 / 股东行为 / 高管交易** 类 D 类固定表格 source：

- 通过 DevTools 发现公开 JSON endpoint；
- 单 source 小样本 `sample_ok` 验证（不翻页、不全量）；
- 人工 UI 表头对照，产出 `confirmed_standard_field`。

**不写 verified**；当前结论仅代表小样本探测与 UI 对照，不代表全市场或长期稳定。

---

## 2. 当前总览

| source_id | 中文名称 | api_url | params | sample_rows | observed_total_rows | field_count | recommended_status | validation_status | UI confirmed | remaining caveats |
|-----------|----------|---------|--------|-------------|---------------------|-------------|-------------------|-------------------|--------------|-------------------|
| equity_pledge | 股权质押 | `.../equityPledge/list` | `tdate=2026-07-03` | 17 | 17 | 10 | testing | sample_ok | **9** | F008V 接口文本，UI 无独立列 |
| shareholder_change | 股东增减持 | `.../shareholeder/detail` | `type=inc` + `tdate=2026-07-03` | 3 | 3 | 8 | testing | sample_ok | **8** (inc) | 勿用 type=dec，实为 type=desc |
| shareholder_change | 股东增减持 | `.../shareholeder/detail` | `type=desc` | 16 | 16 | 8 | testing | sample_ok | **8** (desc) | desc 请求可不传 tdate |
| executive_shareholding | 高管持股 | `.../leader/detail` | `timeMark=oneMonth`, `varyType=b` | 842 | 842 | 16 | testing | sample_ok | **11** | 5 not_visible + 1 uncertain；其他 varyType 待测 |
| fund_industry_allocation | 基金行业配置 | `.../fund/industry` | 无 params，empty body | 19 | 19 | 6 | testing | sample_ok | **6** | **industry-level aggregate**，非 company-level |
| shareholder_data | 股东数据 | `.../shareholeder/data` | `rdate=20260331` | 5255 | 5255 | 9 | testing | sample_ok | **9** | company-level 定期股东结构 |

| 指标 | 数值 |
|------|------|
| **priority-2 testing source** | **5** |
| **全库 testing source** | **10**（priority-1 五源 + priority-2 五源） |
| **verified** | **0**（不允许写） |
| **priority-2 stable_sample** | **0**（尚未多日期复测） |

共性：五个 source 均为 **HTTP 200**、**sample_ok**；records path 均为 **`data.records`**。`fund_industry_allocation` 无 `company_code`（industry aggregate）；其余四个 company-level source 的 `company_code_available` / `date_available` / `amount_available` = **yes**。

---

## 3. equity_pledge（股权质押）

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/data20/equityPledge/list` |
| **params** | POST query `tdate=2026-07-03`，empty body |
| **page** | `url=data/person-stock-data-tables`（股权质押 tab） |
| **sample_rows** | **17** |
| **field_count** | **10** |

**UI confirmed 字段（9）：**

| raw_field | UI 标签 |
|-----------|---------|
| SECCODE | 股票代码 |
| SECNAME | 股票简称 |
| DECLAREDATE | 公告日期 |
| F018N | 累计质押率(%) |
| F001V | 出质人 |
| F003V | 质权人 |
| F006N | 质押数量(万股) |
| F007N | 占总股本比例(%) |
| F012N | 质押解除数量(万股) |

**Caveat：** `F008V` 为接口质押说明文本，UI 无独立列 → **not_visible_on_ui**，保留为 internal text。

---

## 4. shareholder_change（股东增减持）

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| **path 拼写** | **shareholeder**（勿改为 shareholder） |
| **双模式** | `type=inc` 增持 / `type=desc` 减持 |

### type=inc（增持明细）

- **params**：`type=inc`, `tdate=2026-07-03`
- **sample_rows**：**3**；**field_count**：**8**
- **UI confirmed**：**8** 字段

### type=desc（减持明细）

- **params**：`type=desc`（DevTools 未显式带 tdate）
- **sample_rows**：**16**；**field_count**：**8**
- **UI confirmed**：**8** 字段

**同 raw 字段、不同 UI 标签（inc / desc）：**

| raw_field | inc UI | desc UI |
|-----------|--------|---------|
| VARYDATE | 增持日期 | 减持日期 |
| F004N | 增持数量(股) | 减持数量(股) |
| F005N | 增持比例(%) | 减持比例(%) |
| F007V | 增持价格 | 减持价格 |

共用：DECLAREDATE=公告日期，SECCODE=证券代码，SECNAME=证券简称，F002V=股东名称。

**Caveat：** 早期猜测 `type=dec` **错误**；观测参数为 **`type=desc`**。

---

## 5. executive_shareholding（高管持股）

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/data20/leader/detail` |
| **params** | `timeMark=oneMonth`, `varyType=b` |
| **query_mode** | `detail_varyType_b` |
| **sample_rows** | **842** |
| **field_count** | **16** |

**UI confirmed 字段（11）：**

| raw_field | UI 标签 |
|-----------|---------|
| SECCODE | 证券代码 |
| SECNAME | 证券简称 |
| ENDDATE | 变动日期 |
| HUMANNAME | 董监高姓名 |
| F001V | 股份变动人 |
| F002V | 职务 |
| F003V | 变动人与董监高的关系 |
| F006N | 变动数量 |
| F008N | 成交均价 |
| F010V | 变动原因 |

**Caveats：**

| 字段 | 状态 | 说明 |
|------|------|------|
| DECLAREDATE | not_visible_on_ui | 接口有公告日期，明细 UI 无列 |
| F004N | not_visible_on_ui | 变动前持股，样本常空 |
| F005N | **uncertain** | 可能与成交金额相关，UI 无列 |
| F007N | not_visible_on_ui | 变动比例，UI 无列 |
| F009N | not_visible_on_ui | 变动后持股，样本常空 |
| F011V | not_visible_on_ui | 候选公告来源/类型（如「临时公告」） |

- **`varyType=b`** 当前对应 UI「增持」筛选项；其他 varyType / timeMark **待测**。
- 页面另有 **「高管持股变动汇总」** tab（非当前主 source）；后续可拆 `executive_shareholding_summary`。

---

## 6. fund_industry_allocation（基金行业配置）

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/data20/fund/industry` |
| **params** | POST，无 query params，empty body |
| **page** | `url=data/person-stock-data-tables`（基金行业配置 tab） |
| **sample_rows** | **19** |
| **field_count** | **6** |
| **层级** | **industry-level aggregate** — 不是 company-level source |

**UI confirmed 字段（6）：** F001V=行业编码，F002V=所属行业名称，ENDDATE=报告期，F003N=基金覆盖家数(只)，F004N=行业规模(亿元)，F005N=占净资产比例(%)。

---

## 7. shareholder_data（股东数据）

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/data20/shareholeder/data` |
| **path 拼写** | **shareholeder**（勿改为 shareholder） |
| **params** | POST query `rdate=20260331`，empty body |
| **sample_rows** | **5255** |
| **field_count** | **9** |
| **层级** | company-level periodic shareholder structure |

**UI confirmed 字段（9）：** SECCODE=股票代码，SECNAME=股票简称，ENDDATE=变动日期，F001N=本期股东人数，F002N=上期股东人数，F003N=股东人数增幅(%)，F004N=本期人均持股数量(股)，F005N=上期人均持股数量(股)，F006N=人均持股数量增幅(%)。

---

## 8. 当前质量判断

| 维度 | 判断 |
|------|------|
| **可用性** | 五个 source 均可作为 **testing candidates**；endpoint 可达、JSON 结构化 |
| **字段语义** | **equity_pledge** / **shareholder_change** / **fund_industry_allocation** / **shareholder_data** UI 对照已收口 |
| **fund_industry_allocation** | industry aggregate；无 company_code；勿归入 company event |
| **executive_shareholding** | 核心明细列可用（11 confirmed），仍有若干 **internal / candidate** 字段 |
| **稳定性** | **尚未** priority-2 多日期复测 → **不是** `testing_stable_sample` |
| **verified** | **0** — 禁止写入 |

---

## 9. 下一步建议

1. **priority-2 轻量多日期复测**（equity_pledge / shareholder_change inc+desc / executive_shareholding / fund_industry_allocation / shareholder_data）。
2. 测试 **executive_shareholding** 其他 `varyType` / `timeMark` 组合。
3. 下一批 **source discovery**：
   - fund_holding
   - ipo_query
   - szse_calendar
4. **暂不入库、不全量抓取**；不写 verified。

---

## 10. 产物索引

| 文件 | 说明 |
|------|------|
| [cninfo_table_sources_validation.csv](cninfo_table_sources_validation.csv) | 逐 source 验证行（最近批量跑可能仅末次 live 为 sample_ok） |
| [cninfo_table_sources_validation_summary.md](cninfo_table_sources_validation_summary.md) | 验证摘要与各 source 小节 |
| [cninfo_table_field_semantics_priority2.csv](cninfo_table_field_semantics_priority2.csv) | priority-2 字段语义 + UI 对照（含 query_mode） |
| [cninfo_table_field_semantics_priority2.md](cninfo_table_field_semantics_priority2.md) | priority-2 字段语义说明 |
| [cninfo_table_sources_priority2_current_summary.md](cninfo_table_sources_priority2_current_summary.md) | 本文件 |
