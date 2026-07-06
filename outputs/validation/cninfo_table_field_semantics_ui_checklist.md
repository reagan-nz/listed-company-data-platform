# CNINFO D 类 Priority-1 字段语义 UI 对照检查清单

- 生成时间：2026-07-05（离线整理）
- 语义候选表：[cninfo_table_field_semantics_priority1.csv](cninfo_table_field_semantics_priority1.csv)
- 语义说明：[cninfo_table_field_semantics_priority1.md](cninfo_table_field_semantics_priority1.md)
- Priority-1 验证：[cninfo_table_sources_priority1_summary.md](cninfo_table_sources_priority1_summary.md)
- **人工填写清单（CSV）**：[cninfo_table_field_semantics_ui_checklist.csv](cninfo_table_field_semantics_ui_checklist.csv)

---

## 1. 目的

Priority-1 五个 D 类 source 的 **endpoint 与字段可得性** 已验证（`testing`，`sample_ok`），但大量 raw 字段（`F001N`、`f002d_0102` 等）的 **标准语义仍是候选**。

本清单用于 **人工对照 CNINFO 网页表头 / UI 列名**：

- 不自动抓取 UI label；
- 不自动确认语义；
- **不写 verified**；
- 填写结果回写 CSV 的 `ui_label_observed`、`confirmation_status`、`confirmed_standard_field`。

---

## 2. 检查方法

1. 打开对应 **ui_page_url**（见 CSV 或下文 §3）。
2. 在页面上设置与 **sample_query_params** 一致的日期/市场/分页（或与 API 小样本相同条件）。
3. 找到与 **raw_field** 对应的表格列或展开明细列。
4. 将网页上看到的 **中文列名** 填入 `ui_label_observed`。
5. 可选填 `ui_column_order`（从左到右列序号，从 1 开始）。
6. 更新 `confirmation_status`：
   - `confirmed` — UI 标签与 `standard_field_candidate` 一致；
   - `corrected` — 需改用 `confirmed_standard_field`；
   - `uncertain` — 仍无法判断；
   - `not_visible_on_ui` — 页面上无对应列；
   - `pending` — 未检查（默认）。
7. 若确认或修正，更新 `semantic_confidence_after`（high / medium / low / unknown）。

**禁止：** 未看 UI 即批量标 `confirmed`。

---

## 3. 各 source 检查项

### 3.1 disclosure_schedule（预约披露）

| 项 | 内容 |
|----|------|
| **导航** | 资讯 → 预约披露 / 定期报告预约披露 |
| **ui_page_url** | `https://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice` |
| **sample_query_params** | `sectionTime=2025-12-31`; `market=szsh`; `pagesize=20`; `pagenum=1` |
| **待确认字段数** | **7** |
| **重点字段** | `f002d_0102`, `f006d_0102`, `f003d_0102`, `f004d_0102`, `f005d_0102` |

对照预约披露列表列名，重点区分：**报告期**、**首次预约**、**初次/二次/三次变更**、**实际披露**。

**UI 对照进度（2026-07-05）：** `f001d_0102`–`f006d_0102` 均已 **confirmed**（6 行）；`latest_time` 为 **not_visible_on_ui**（表头未显示，疑为接口更新时间）。

### 3.2 restricted_shares_unlock（限售解禁）

| 项 | 内容 |
|----|------|
| **导航** | 数据 → 限售解禁 |
| **ui_page_url** | `https://www.cninfo.com.cn/new/commonUrl?url=data/restricted-shares` |
| **sample_query_params** | `tdate=2026-06-08` |
| **待确认字段数** | **5** |
| **重点字段** | `F004N`, `F005N`, `F008N` |

样本：300992 泰福泵业；注意 **股数单位** 与 **F004N vs F008N** 列名差异。

**UI 对照进度（2026-07-05）：** `DECLAREDATE`、`F003D`、`F004N`、`F005N`、`F008N` 均已 **confirmed**（5 行）；单位已明确：股、%。

### 3.3 block_trade（大宗交易）

| 项 | 内容 |
|----|------|
| **导航** | 数据 → 大宗交易 |
| **ui_page_url** | `https://www.cninfo.com.cn/new/commonUrl?url=data/dzjy` |
| **sample_query_params** | `tdate=2026-07-03` |
| **待确认字段数** | **4** |
| **重点字段** | `F001N`, `F002N`, `F003N`, `F004N` |

样本：600519 贵州茅台；确认列名后可用 **成交金额(万元)/成交数量(万股)≈成交均价(元/股)** 做算术交叉验证。

**UI 对照进度（2026-07-05）：** `F001N`–`F004N` 均已 **confirmed**（4 行）；单位已明确：万股、万元、元/股。

### 3.4 margin_trading（融资融券）

| 项 | 内容 |
|----|------|
| **导航** | 数据 → 融资融券 |
| **ui_page_url** | `https://www.cninfo.com.cn/new/commonUrl?url=data/rzrq-zjlx` |
| **sample_query_params** | 默认最新交易日明细（小样本 observed `TRADEDATE=2026-07-02`）；API 为 empty body POST `detailList` |
| **待确认字段数** | **10** |
| **重点字段** | `F001N`–`F009N`（含常空 `F003N`/`F007N`） |

字段最多；建议对照 UI 从左到右记录 `ui_column_order`。`MEMO`、`F011V` 次优先。

**UI 对照进度（2026-07-05）：**

| 状态 | 字段 |
|------|------|
| **confirmed**（5） | `F001N` 融资余额(元)、`F002N` 融资买入额(元)、`F004N` 融券余量(股)、`F006N` 融券卖出量(股)、`F009N` 融资融券余额(元) |
| **not_visible_on_ui**（3） | `F003N`、`F007N`、`F011V` |
| **uncertain**（1） | `F008N`（候选：融券余量金额；F009N ≈ F001N + F008N） |
| **pending**（1） | `MEMO` |

页面上方 **融资融券交易总量** 汇总表（market summary，非 `detailList` 主 source）列语义不同：`F001N`=融资余额(亿元)、`F002N`=融资买入额(亿元)、`F003N`=融券余量金额(亿元)、`F004N`=融资融券余额(亿元)。后续可拆成 `margin_trading_market_summary`。

### 3.5 abnormal_trading（公开信息 / 异常交易）

| 项 | 内容 |
|----|------|
| **导航** | 数据 → 公开信息 |
| **ui_page_url** | `https://www.cninfo.com.cn/new/commonUrl?url=data/public-information` |
| **sample_query_params** | `sdate=2026-07-03`; `edate=2026-07-03`; `page=1`; `rows=30` |
| **待确认字段数** | **12**（含 6 个 `detail.*` 嵌套行） |
| **重点字段** | `buyTotal`, `sellTotal`, `buyPercent`, `sellPercent`, `detail` 及嵌套子字段 |

样本：000004 国华退（退市整理期）；顶层金额列可能为空，需 **展开行/弹窗** 对照 `detail.*` 营业部六列。

**UI 对照进度（2026-07-05）：**

| 状态 | 字段 |
|------|------|
| **confirmed**（8） | 主表 `type`（信息公开原因）；`detail` 及嵌套 6 列：营业部（买入/卖出）、买入金额、卖出金额 |
| **not_visible_on_ui**（4） | `buyTotal`、`sellTotal`、`buyPercent`、`sellPercent`（主表与详情均未显示顶层汇总） |

说明：`secCode`、`secName`、`tradeTime` 在 semantics 表中为 high confidence，但未纳入本 checklist（若需可另补行）。

---

## 4. 完成后的统计方式

对 [cninfo_table_field_semantics_ui_checklist.csv](cninfo_table_field_semantics_ui_checklist.csv) 汇总：

| 指标 | 计算 |
|------|------|
| **confirmed** | `confirmation_status=confirmed` 行数 |
| **corrected** | `confirmation_status=corrected` 行数 |
| **uncertain** | `confirmation_status=uncertain` 行数 |
| **not_visible_on_ui** | `confirmation_status=not_visible_on_ui` 行数 |
| **pending** | 未完成行数 |
| **confidence upgrade** | `semantic_confidence_after` 高于 `semantic_confidence_before` |
| **confidence downgrade** | `semantic_confidence_after` 低于 before |

### 4.1 当前进度（2026-07-05，人工截图回填后）

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
| abnormal_trading | 8（含 `detail` + 6 嵌套） |
| **合计** | **28** |

**仍未确认 / 需后续处理：**

| 类别 | 字段 |
|------|------|
| **pending** | `margin_trading.MEMO` |
| **uncertain** | `margin_trading.F008N` |
| **not_visible_on_ui** | `disclosure_schedule.latest_time`；`margin_trading.F003N` / `F007N` / `F011V`；`abnormal_trading.buyTotal` / `sellTotal` / `buyPercent` / `sellPercent` |

**阶段性结论：** D 类 priority-1 UI 对照已基本完成；剩余 **1 行 pending**、**1 行 uncertain**、**8 行 not_visible_on_ui**。下一步可选：补 `MEMO` 截图；对 `F008N` 做 F001N+F008N≈F009N 算术验证；或将 confirmed 行回写 semantics 表（另次任务）。

完成后可将 `confirmed` / `corrected` 行回写 [cninfo_table_field_semantics_priority1.csv](cninfo_table_field_semantics_priority1.csv)（另次任务，本清单不自动改）。

---

## 5. 待确认规模（初始 → 当前）

| 来源 | 清单行数 | 说明 |
|------|----------|------|
| semantics 表 `needs_confirmation=yes` | 33 | 直接筛选 |
| abnormal_trading `detail.*` 嵌套 | +6 | 补充嵌套子字段 |
| **设计合计** | **39** | 清单 CSV 实际 **38** 数据行（`secCode`/`secName`/`tradeTime` 未入清单） |

| source_id | 清单行数 | confirmed | not_visible / uncertain / pending |
|-----------|----------|-----------|-------------------------------------|
| disclosure_schedule | 7 | 6 | 1 not_visible (`latest_time`) |
| restricted_shares_unlock | 5 | 5 | — |
| block_trade | 4 | 4 | — |
| margin_trading | 10 | 5 | 3 not_visible + 1 uncertain + 1 pending |
| abnormal_trading | 12 | 8 | 4 not_visible |
| **合计** | **38** | **28** | 8 + 1 + 1 |

---

## 6. 建议人工确认顺序（已完成 → 收尾）

1. ~~**block_trade**~~ — **done**（4 confirmed）
2. ~~**restricted_shares_unlock**~~ — **done**（5 confirmed）
3. ~~**disclosure_schedule**~~ — **done**（6 confirmed + 1 not_visible）
4. ~~**abnormal_trading**~~ — **done**（8 confirmed + 4 not_visible）
5. ~~**margin_trading** 主列~~ — **mostly done**（5 confirmed）；收尾：`MEMO`、`F008N` 算术验证、market summary 拆分

---

## 7. 边界

- **不联网自动抓** UI；不跑脚本；
- **不写 verified**；`confirmed` 仅表示人工 UI 对照通过；
- 本清单为 **人工任务模板**；`ui_label_observed` 默认留空；
- 不修改 validation CSV、Phase 1、database schema。
