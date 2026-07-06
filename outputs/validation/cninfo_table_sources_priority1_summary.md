# CNINFO Era C Phase 2 D 类固定表格 Priority-1 验证总结

- 生成时间：2026-07-05（离线整理）
- 探测计划：[cninfo_table_sources_phase2_plan.md](cninfo_table_sources_phase2_plan.md)
- 配置：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)
- 验证脚本：`lab/validate_cninfo_table_sources.py`
- 逐次跑次摘要：[cninfo_table_sources_validation_summary.md](cninfo_table_sources_validation_summary.md)
- Phase 1 收口：[cninfo_report_phase1_final_summary.md](cninfo_report_phase1_final_summary.md)
- 分层口径：[plans/cninfo_data_source_layered_inventory.md](../../plans/cninfo_data_source_layered_inventory.md)（D 类）

---

## 1. 阶段目标

**Era C Phase 2** 验证 CNINFO **D 类固定表格 / 市场行为**数据源：公开 endpoint 是否存在、返回是否结构化、字段是否可盘点、是否适合后续工程化。

**本轮 priority-1** 范围：

- 只做 **小样本 endpoint discovery + 字段盘点**；
- 每个 source 单独 live 验证（`--source-id`）；
- **不做**全量抓取、不入库、不生产化；
- **不写 verified**。

---

## 2. 总体结果

| 指标 | 数值 |
|------|------|
| **已验证 priority-1 source** | **5** |
| **testing** | **5** |
| **blocked** | **0** |
| **partial** | **0** |
| **candidate（其余未验证）** | **5**（szse_calendar、equity_pledge、shareholder_change、executive_shareholding、ipo_query） |
| **verified** | **0**（不允许写 verified） |

共性结论（5 个 priority-1 source）：

- 均已发现 **公开 JSON endpoint**；
- live 小样本 **HTTP 200**、`validation_status=sample_ok`；
- **requires_login / requires_captcha / requires_paid_permission = no**；
- **recommended_status = testing**。

### Priority-1 汇总表

| source_id | 中文名称 | api_url | sample_rows | observed_total_rows | field_count | recommended_status | validation_status |
|-----------|----------|---------|-------------|---------------------|-------------|-------------------|-------------------|
| disclosure_schedule | 预约披露 | `.../getPrbookInfo` | 20 | 5493 | 10 | testing | sample_ok |
| restricted_shares_unlock | 限售解禁 | `.../liftBan/detail` | 6 | 6 | 7 | testing | sample_ok |
| block_trade | 大宗交易 | `.../ints/statistics` | 60 | 60 | 7 | testing | sample_ok |
| margin_trading | 融资融券 | `.../marginTrading/detailList` | 4374 | 4374 | 15 | testing | sample_ok |
| abnormal_trading | 公开信息 / 异常交易 | `.../getMarketStatisticsData` | 30 | 151 | 9 | testing | sample_ok |

> 注：各 source 经独立 `--source-id` live 跑验证；`cninfo_table_sources_validation.csv` 最近一次批量跑可能仅保留最后一次 live 行的 `sample_ok` 明细，本表 consolidates 五次验证结论。

---

## 3. disclosure_schedule 预约披露

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/new/information/getPrbookInfo` |
| **method** | POST（`params_location: form`） |
| **params** | `sectionTime=2025-12-31`, `market=szsh`, `pagesize=20`, `pagenum=1` |
| **sample_rows** | **20** |
| **observed_total_rows** | **5493** |
| **key fields** | `seccode`, `secname`, `orgId`, `f001d_0102`, `f002d_0102`, `f006d_0102`（及 f003/f004/f005 变更日期字段） |
| **value** | 公司代码、简称、orgId、报告期、预约披露日期 |
| **caveat** | `f002d_0102` / `f006d_0102` / `f003d_0102` 等字段语义仍需确认 |

---

## 4. restricted_shares_unlock 限售解禁

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/data20/liftBan/detail` |
| **method** | POST（`params_location: query`） |
| **sample** | `tdate=2026-06-08` |
| **sample_rows** | **6** |
| **observed_total_rows** | **6** |
| **key fields** | `SECCODE`, `SECNAME`, `DECLAREDATE`, `F003D`, `F004N`, `F005N`, `F008N` |
| **value** | 解禁日期、解禁股份数量、比例等事件型数据 |
| **caveat** | `F004N` / `F005N` / `F008N` 精确定义仍需确认 |

---

## 5. block_trade 大宗交易

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/data20/ints/statistics` |
| **method** | POST（`params_location: query`） |
| **sample** | `tdate=2026-07-03` |
| **sample_rows** | **60** |
| **observed_total_rows** | **60** |
| **key fields** | `SECCODE`, `SECNAME`, `TRADEDATE`, `F001N`, `F002N`, `F003N`, `F004N` |
| **value** | 公司级大宗交易笔数/成交量/成交额/均价候选字段 |
| **caveat** | `F001N`–`F004N` 精确单位仍需确认；样本中 F003N/F002N ≈ F004N |

---

## 6. margin_trading 融资融券

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/data20/marginTrading/detailList` |
| **method** | POST（`params_location: none`，empty body） |
| **sample_rows** | **4374** |
| **observed_total_rows** | **4374** |
| **key fields** | `TRADEDATE`, `SECCODE`, `SECNAME`, `F001N`–`F009N`, `F010V`, `F011V`, `F012V`, `MEMO` |
| **value** | 个股融资融券日度明细 |
| **caveat** | `F001N`–`F009N` 含义与单位待确认；`marginTrading/market?tdate=...` 为市场汇总，**不作**本 task 主 source |

---

## 7. abnormal_trading 公开信息 / 异常交易

| 项 | 内容 |
|----|------|
| **endpoint** | `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData` |
| **method** | POST（`params_location: query`） |
| **sample** | `sdate=edate=2026-07-03`, `page=1`, `rows=30` |
| **sample_rows** | **30** |
| **observed_total_rows** | **151** |
| **observed_total_pages** | **6** |
| **key fields** | `secCode`, `secName`, `tradeTime`, `type`, `buyTotal`, `sellTotal`, `buyPercent`, `sellPercent`, `detail` |
| **nested_detail_available** | **yes** |
| **value** | 异常交易类型、公开交易信息、营业部买卖明细（`detail` 嵌套） |
| **caveat** | `type` 分类、`buyTotal`/`sellTotal`、detail 内金额字段仍需确认 |

---

## 8. 与 Phase 1 A 类的关系

| 维度 | Phase 1 A 类 | Phase 2 D 类（本轮） |
|------|--------------|----------------------|
| 数据形态 | 定期报告 **PDF 文档流** | **固定表格 JSON** / 市场行为 |
| 验证口径 | per-company **coverage%** | 入口稳定性 + **字段可得性** |
| 典型用途 | document / report retrieval | **event / market table** |
| 结论 | P1 **749/796 = 94.10%**，testing/usable candidate | 5 个 priority-1 **testing** |

两者 **互补**：A 类解决「报告 PDF 能否检索」；D 类补充披露日程、解禁、大宗交易、融资融券、异常交易等 **结构化事件/市场数据**。本轮已证明 CNINFO **不只有公告 PDF**，也存在多个 **公开 JSON 表格入口**。

---

## 9. 当前 recommended_status

| 结论 | 说明 |
|------|------|
| **5 个 priority-1 source** | 均为 **testing** |
| **verified** | **不写** |
| **testing 含义** | 公开 endpoint + 小样本 `sample_ok` + 无需登录/验证码/付费 |
| **未确认项** | 大量 `F00xN` / `f00xd` 字段 **语义与单位** |
| **非含义** | 不代表全量生产稳定、不代表全市场 accuracy |

---

## 10. 边界

- 只做 **小样本**（单日 / 单页 / 默认 detailList 一次请求）；
- **未**全量翻页、**未**循环日期；
- **未**入库；**未**下载/解析 PDF；**未**计算 hash；
- **未**使用 BrowserUser；
- **未**绕过登录 / 验证码 / 权限；
- 结论仅代表 **priority-1 五次小样本探测**，非全市场。

---

## 11. 下一步建议

1. **字段语义确认表** — 统一整理 `F001N` 等字段含义与单位（尤其 margin / block / unlock）；
2. **稳定性复测** — 对 5 个 testing source 各选 2–3 个日期做小样本复测；
3. **第二批 source**（priority-2，仍小样本）：
   - `shareholder_change`
   - `equity_pledge`
   - `executive_shareholding`
   - `ipo_query`
   - `szse_calendar`
4. **暂不全量抓取**；**暂不入库**；
5. 若后续生产化，再设计 **table schema / event schema**（与 storage 设计分离）。

---

## 12. 产物索引

| 文件 | 用途 |
|------|------|
| [cninfo_table_sources_phase2_plan.md](cninfo_table_sources_phase2_plan.md) | Phase 2 探测计划 |
| [config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml) | D 类 source 配置（10 个） |
| `lab/validate_cninfo_table_sources.py` | config 驱动验证脚本 |
| [cninfo_table_sources_validation.csv](cninfo_table_sources_validation.csv) | 逐 source 验证行 |
| [cninfo_table_sources_validation_summary.md](cninfo_table_sources_validation_summary.md) | 跑次摘要（含各 source §12–§16） |
| **本文档** | **Priority-1 五次验证 consolidated 总结** |
| [cninfo_report_phase1_final_summary.md](cninfo_report_phase1_final_summary.md) | Phase 1 A 类收口 |

### Priority-1 一句话

**CNINFO D 类 priority-1 五个固定表格入口（预约披露、限售解禁、大宗交易、融资融券、公开信息）均已发现公开 JSON API、小样本 sample_ok、无需权限，评为 testing；字段语义待确认，不写 verified，下一步做语义表与 priority-2 扩展。**
