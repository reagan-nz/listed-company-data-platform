# CNINFO Era C Phase 2 D 类固定表格 Source 当前总总结

- 生成时间：2026-07-05（离线整理）
- 配置：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)
- Phase 1 A 类收口：[cninfo_report_phase1_final_summary.md](cninfo_report_phase1_final_summary.md)
- Priority-1 分源总结：[cninfo_table_sources_priority1_summary.md](cninfo_table_sources_priority1_summary.md)
- Priority-2 分源总结：[cninfo_table_sources_priority2_current_summary.md](cninfo_table_sources_priority2_current_summary.md)
- Priority-1 稳定性：[cninfo_table_sources_multidate_stability_summary.md](cninfo_table_sources_multidate_stability_summary.md)
- Priority-2 稳定性：[cninfo_table_sources_priority2_stability_summary.md](cninfo_table_sources_priority2_stability_summary.md)

---

## 1. 阶段目标

**Era C Phase 2** 的目标是验证 CNINFO 是否存在可 **公开访问**、**结构稳定** 的 **D 类固定表格 / 市场行为 / 股东行为** 数据源：

- 通过 DevTools 发现 JSON endpoint；
- 小样本 live 验证（`sample_ok`）；
- 人工 UI 表头对照字段语义；
- 多日期 / 多参数轻量稳定性复测（`testing_stable_sample`）。

**非目标**：全量抓取、入库、生产 schema、长期监控、写 **verified**。

---

## 2. 总体结论

| 指标 | 数值 |
|------|------|
| **当前已验证 source 总数** | **10** |
| **testing_stable_sample** | **10** |
| **blocked** | **0** |
| **schema_changed** | **0** |
| **verified** | **0**（不允许写） |
| **config 中 candidate（未验证）** | **2**（`szse_calendar`、`ipo_query`） |

**结论：** CNINFO **不只有公告 PDF**。在 Phase 1 A 类证明报告 PDF 可检索之外，Phase 2 已确认 **10 个公开 JSON fixed-table source**，覆盖披露日程、市场行为、股东行为、高管交易、行业聚合等结构化数据入口；endpoint 可达、无需登录/验证码/付费，小样本多日期/多参数下字段结构稳定。

---

## 3. Source 分层

### 3.1 company-level source

以 **公司代码（SECCODE）** 为主键或核心维度的 source：

| source_id | 中文名称 |
|-----------|----------|
| restricted_shares_unlock | 限售解禁 |
| block_trade | 大宗交易 |
| margin_trading | 融资融券 |
| abnormal_trading | 公开信息 / 异常交易 |
| equity_pledge | 股权质押 |
| shareholder_change | 股东增减持 |
| executive_shareholding | 高管持股 |
| shareholder_data | 股东数据 |

### 3.2 schedule / disclosure source

| source_id | 中文名称 |
|-----------|----------|
| disclosure_schedule | 预约披露 / 定期报告预约披露 |

以披露日程、报告期、预约日期为核心；含 `orgId`，适合与 A 类报告 PDF 联动。

### 3.3 industry-level aggregate source

| source_id | 中文名称 |
|-----------|----------|
| fund_industry_allocation | 基金行业配置 |

**行业级聚合表**，按行业编码（`F001V`）聚合，**无** `SECCODE`。**不要**归入 company event schema；后续 event timeline / company schema 设计应单独处理。

---

## 4. Priority-1 结果摘要

| source_id | 中文名称 | sample_rows | stability_cases | records_path | field_count | status | 主要价值 | 主要 caveat |
|-----------|----------|-------------|-----------------|--------------|-------------|--------|----------|-------------|
| disclosure_schedule | 预约披露 | 20 | 2 | `prbookinfos` | 10 | testing_stable_sample | 公司代码、报告期、预约/变更披露日期、`orgId` | `latest_time` 待确认；部分 `f00xd` 变更日期语义 |
| restricted_shares_unlock | 限售解禁 | 6 | 3 | `data.records` | 7 | testing_stable_sample | 解禁日期、解禁股数/比例事件 | `F004N`/`F005N`/`F008N` 股数区分曾待确认（UI 已大部分确认） |
| block_trade | 大宗交易 | 60 | 3 | `data.records` | 7 | testing_stable_sample | 公司级大宗交易笔数/量/额/均价 | 空交易日 `empty_but_valid_response`；单位已 UI 确认 |
| margin_trading | 融资融券 | 4374 | 2（主） | `data.records` | 15 | testing_stable_sample | 个股融资融券日度明细 | `F003N`/`F007N`/`F008N`/`F010V`/`F011V`/`F012V` 等待确认；`detailList` 不传 date；`market` 附属接口 HTTP 500 |
| abnormal_trading | 公开信息 / 异常交易 | 30 | 3 | `marketList` | 9 | testing_stable_sample | 异常交易类型、买卖汇总、`detail` 嵌套营业部明细 | `type` 分类码；detail 内金额字段 |

> Priority-1 各 source 经独立 `--source-id` live 验证 + 多日期复测；`cninfo_table_sources_validation.csv` 可能仅保留最近一次批量跑的 live 行，本表 consolidates 历史结论。

---

## 5. Priority-2 结果摘要

| source_id | 中文名称 | sample_rows | stability_cases | records_path | field_count | status | 主要价值 | 主要 caveat |
|-----------|----------|-------------|-----------------|--------------|-------------|--------|----------|-------------|
| equity_pledge | 股权质押 | 17 | 3 | `data.records` | 10 | testing_stable_sample | 质押方/质权人、质押数量/比例、累计质押率 | `F008V` 接口 internal text，UI 无列；`tdate=2026-07-03` 空日 |
| shareholder_change | 股东增减持 | 3 (inc) / 16 (desc) | 3 | `data.records` | 8 | testing_stable_sample | 增持/减持明细（股东、数量、比例、价格） | **`type=inc` / `type=desc`**（勿用 `dec`）；desc 可不传 `tdate` |
| executive_shareholding | 高管持股 | 842 | 3 | `data.records` | 16 | testing_stable_sample | 高管/变动人、职务、变动数量、成交均价、变动原因 | **`timeMark` / `varyType`** 参数；5 字段 not_visible + 1 uncertain |
| fund_industry_allocation | 基金行业配置 | 19 | 3 | `data.records` | 6 | testing_stable_sample | 行业覆盖家数、行业规模、占净资产比例 | **industry aggregate**；无 company_code；`rdate=20251231` 空 |
| shareholder_data | 股东数据 | 5255 | 3 | `data.records` | 9 | testing_stable_sample | 股东人数、人均持股、环比增幅 | 定期报告期 `rdate`；endpoint 拼写 **shareholeder** |

### 特别说明

- **shareholder_change**：同一 endpoint `/shareholeder/detail`，通过 `type=inc`（增持）与 `type=desc`（减持）切换；raw 字段结构相同，UI 标签不同（增持日期 vs 减持日期等）。
- **executive_shareholding**：`/leader/detail` 支持 `timeMark`（oneMonth / threeMonth）与 `varyType`（b / s 等）；稳定性复测三种组合均通过，但 `varyType` 语义仍需 UI 逐项确认。
- **fund_industry_allocation**：行业级聚合，**不是** company-level event；勿与 equity_pledge / shareholder_change 混在同一 event schema。
- **shareholder_data**：company-level 定期股东结构（人数 + 人均持股），按 `rdate` 报告期末查询全市场截面。

---

## 6. 字段语义确认情况

### 6.1 已完成工作

- **Priority-1**：48 个 top-level 字段语义候选表 + 38 行 UI 对照 checklist；**28 confirmed**、8 not_visible_on_ui、1 uncertain、1 pending（`MEMO`）。
- **Priority-2**：51 行字段语义 + UI 对照（含 `query_mode`）；**51 confirmed**（equity_pledge 9 + shareholder_change 16 + executive 16 + fund 6 + shareholder_data 9，含 inc/desc 双模式）。
- 大多数 **核心展示列** 已 **UI confirmed / high**。
- **不写 verified**；`confirmed` 仅表示人工 UI 对照通过。

### 6.2 仍待确认字段

| source | 字段 | 状态 / 说明 |
|--------|------|-------------|
| **margin_trading** | F003N, F007N, F008N | 融券相关；样本常空，语义低置信 |
| **margin_trading** | F010V, F011V, F012V | 市场名/内部码/股票类型；部分 obvious 但未全 UI confirmed |
| **margin_trading** | MEMO | pending；备注列样本常空 |
| **executive_shareholding** | DECLAREDATE, F004N, F007N, F009N, F011V | not_visible_on_ui；接口有值但明细 UI 无列 |
| **executive_shareholding** | F005N | **uncertain**；可能与成交金额相关 |
| **equity_pledge** | F008V | not_visible_on_ui；质押说明 internal text |
| **disclosure_schedule** | latest_time | official_doc_needed；样本多为 null |

---

## 7. 稳定性复测结论

### Priority-1（多日期）

| 指标 | 数值 |
|------|------|
| total_test_cases | **15**（含 2 个 margin_trading 附属 market 观察） |
| sample_ok | **12** |
| empty_but_valid_response | **1**（block_trade `tdate=2026-07-03`） |
| http_error | **2**（margin_trading `market` 附属，非主 source） |
| schema_changed | **0** |
| blocked | **0** |
| testing_stable_sample | **5 / 5** |

### Priority-2（多参数）

| 指标 | 数值 |
|------|------|
| total_test_cases | **15** |
| sample_ok | **13** |
| empty_but_valid_response | **2**（equity_pledge `tdate=2026-07-03`；fund_industry `rdate=20251231`） |
| schema_changed | **0** |
| blocked | **0** |
| testing_stable_sample | **5 / 5** |

**说明：** `empty_but_valid_response` **不等于失败**。表示 HTTP 200 + JSON 可解析 + records path 稳定，仅该日期/参数下无数据（如非交易日、无质押事件、报告期未发布）。

---

## 8. 与 Phase 1 A 类报告 PDF 的关系

| 维度 | Phase 1 A 类 | Phase 2 D 类 |
|------|--------------|--------------|
| 数据形态 | 定期报告 **PDF 文档流** | **固定表格 JSON** / 市场行为 |
| 验证口径 | per-company **coverage%**（P1 749/796 = 94.10%） | 入口稳定性 + 字段可得性 + 多参数稳定性 |
| 典型用途 | document / report retrieval | event table / metric table / market behavior |
| 状态 | testing / usable candidate | testing_stable_sample（10 源） |

**互补关系：**

- **A 类**解决「报告 PDF 能否按公司 × 报告期检索」；
- **D 类**补充披露日程、解禁、大宗交易、融资融券、异常交易、质押、增减持、高管持股、股东结构、行业基金配置等 **结构化事件/指标表**。

后续产品可同时支持 **report timeline**（A 类）+ **structured event timeline**（D 类），例如：预约披露日 → 报告 PDF 发布 → 股东人数变化 → 高管增持。

---

## 9. 当前边界

必须明确以下限制：

- **未**全量抓取；各 source 仅小样本（单日 / 单页 / 默认一次请求 / 2–3 个日期或参数）；
- **未**长期监控；结论不代表接口长期可用性或 CNINFO 改版免疫；
- **未**入库；无 PostgreSQL / MinIO / MongoDB 接入；
- **未**做生产 schema；仅有字段语义候选与 UI confirmed 命名；
- **未**下载 / 解析 PDF；
- **未**绕过登录 / 验证码 / 付费权限；
- **未**写 **verified**；
- **testing_stable_sample** 仅表示小样本多日期/多参数下 endpoint、records path、字段集合稳定，**不是**全市场 accuracy 或生产就绪。

---

## 10. 下一步建议

1. **Phase 2 当前 10 源可阶段性收口**；状态统一为 `testing_stable_sample`，不写 verified。
2. **下一批 discovery（可选）**：
   - `ipo_query`
   - `szse_calendar`
   - `executive_shareholding_summary`（高管持股变动汇总 tab，独立 endpoint）
   - `fund_stock_holding`（基金持股）
3. **在继续扩 source 前**，可开始设计 **D 类 source registry / event schema draft**（区分 company-level / schedule / industry aggregate 三层）。
4. **暂不入库、不全量抓取**。
5. **若要生产化**，需额外做：长期监控、限速策略、字段漂移检测、空日/空报告期处理、错误恢复、与 A 类 `orgId` / 公司主数据映射。

---

## 11. 产物索引

### 总总结与分源

| 文件 | 说明 |
|------|------|
| **本文档** | Phase 2 十源 consolidated 总总结 |
| [cninfo_table_sources_priority1_summary.md](cninfo_table_sources_priority1_summary.md) | Priority-1 五源 discovery + 小样本 |
| [cninfo_table_sources_priority2_current_summary.md](cninfo_table_sources_priority2_current_summary.md) | Priority-2 五源 discovery + UI 对照 |
| [cninfo_table_sources_multidate_stability_summary.md](cninfo_table_sources_multidate_stability_summary.md) | Priority-1 多日期稳定性（15 cases） |
| [cninfo_table_sources_priority2_stability_summary.md](cninfo_table_sources_priority2_stability_summary.md) | Priority-2 多参数稳定性（15 cases） |
| [cninfo_table_sources_validation_summary.md](cninfo_table_sources_validation_summary.md) | 逐次跑次验证摘要 |

### 字段语义

| 文件 | 说明 |
|------|------|
| [cninfo_table_field_semantics_priority1.md](cninfo_table_field_semantics_priority1.md) | Priority-1 字段语义候选 |
| [cninfo_table_field_semantics_ui_check_summary.md](cninfo_table_field_semantics_ui_check_summary.md) | Priority-1 UI 对照收口 |
| [cninfo_table_field_semantics_priority2.md](cninfo_table_field_semantics_priority2.md) | Priority-2 字段语义 + UI 对照 |

### CSV / 配置 / 脚本

| 文件 | 说明 |
|------|------|
| [config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml) | D 类 source 配置（12 条：10 testing + 2 candidate） |
| [cninfo_table_sources_validation.csv](cninfo_table_sources_validation.csv) | 逐 source 单次验证行 |
| [cninfo_table_sources_multidate_stability.csv](cninfo_table_sources_multidate_stability.csv) | Priority-1 稳定性明细 |
| [cninfo_table_sources_priority2_stability.csv](cninfo_table_sources_priority2_stability.csv) | Priority-2 稳定性明细 |
| `lab/validate_cninfo_table_sources.py` | config 驱动单 source 验证 |
| `lab/validate_cninfo_table_sources_multidate.py` | Priority-1 多日期稳定性 |
| `lab/validate_cninfo_table_sources_priority2_stability.py` | Priority-2 多参数稳定性 |

### Phase 2 一句话

**CNINFO D 类 Phase 2 已验证 10 个公开 JSON fixed-table source（priority-1 五源 + priority-2 五源），均达 testing_stable_sample；blocked=0、schema_changed=0、verified=0；CNINFO 除公告 PDF 外存在大量结构化表格入口，可与 A 类报告检索互补；当前批次可收口，下一步可选扩源或设计 D 类 registry / event schema draft。**
