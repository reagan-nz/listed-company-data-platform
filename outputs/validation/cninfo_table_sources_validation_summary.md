# CNINFO D 类固定表格数据源验证摘要

- 生成时间：2026-07-05T07:25:30Z
- 配置：config/cninfo_table_sources.yaml
- 脚本：`lab/validate_cninfo_table_sources.py`
- 计划：[cninfo_table_sources_phase2_plan.md](cninfo_table_sources_phase2_plan.md)
- 模式：**live 小样本**

---

## 1. 本次验证范围

- **层级**：D 类固定表格 / 市场行为
- **目标**：入口探测、字段盘点、可用性分类
- **非目标**：全量抓取、入库、生产化

## 2. source 总数

- **配置 source 数**：**12**

## 3. recommended_status 分布

| recommended_status | 数量 |
|--------------------|------|
| testing | 10 |
| candidate | 2 |
| partial | 0 |
| blocked | 0 |
| unknown | 0 |

## 4. validation_status 分布

| validation_status | 数量 |
|-------------------|------|
| dry_run | 8 |
| needs_manual_endpoint_discovery | 2 |
| sample_ok | 2 |

## 5. api_url 配置情况

- **已配置 api_url**：10
- **api_url 为空（待 DevTools）**：2

已有 api_url 的 source：
- `disclosure_schedule` → `https://www.cninfo.com.cn/new/information/getPrbookInfo`
- `margin_trading` → `https://www.cninfo.com.cn/data20/marginTrading/detailList`
- `block_trade` → `https://www.cninfo.com.cn/data20/ints/statistics`
- `restricted_shares_unlock` → `https://www.cninfo.com.cn/data20/liftBan/detail`
- `abnormal_trading` → `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData`
- `equity_pledge` → `https://www.cninfo.com.cn/data20/equityPledge/list`
- `shareholder_change` → `https://www.cninfo.com.cn/data20/shareholeder/detail`
- `executive_shareholding` → `https://www.cninfo.com.cn/data20/leader/detail`
- `fund_industry_allocation` → `https://www.cninfo.com.cn/data20/fund/industry`
- `shareholder_data` → `https://www.cninfo.com.cn/data20/shareholeder/data`

## 6. 需手工 DevTools endpoint discovery

- **szse_calendar**（深市日历）— page: `https://www.cninfo.com.cn/new/commonUrl?url=disclosure/szse-calendar`
- **ipo_query**（IPO 查询）— page: `https://www.cninfo.com.cn/new/commonUrl?url=disclosure/ipo`

## 7. blocked source

- 本次 **未发现** blocked source（或未执行 live 验证）。

## 8. 各 source 字段价值（来自配置 expected_fields）

| source_id | 中文名 | 关键维度 | 配置 priority | recommended_status |
|-----------|--------|----------|---------------|-------------------|
| disclosure_schedule | 预约披露 / 定期报告预约披露 | 见 config expected_fields | — | testing |
| margin_trading | 融资融券 | 见 config expected_fields | — | testing |
| block_trade | 大宗交易 | 见 config expected_fields | — | testing |
| restricted_shares_unlock | 限售解禁 / 解除限售 | 见 config expected_fields | — | testing |
| abnormal_trading | 公开信息 / 异常交易 | 见 config expected_fields | — | testing |
| szse_calendar | 深市日历 | 见 config expected_fields | — | candidate |
| equity_pledge | 股权质押 | 见 config expected_fields | — | testing |
| shareholder_change | 股东增减持 | 见 config expected_fields | — | testing |
| executive_shareholding | 高管持股 | 见 config expected_fields | — | testing |
| fund_industry_allocation | 基金行业配置 | 见 config expected_fields | — | testing |
| shareholder_data | 股东数据 | 见 config expected_fields | — | testing |
| ipo_query | IPO 查询 | 见 config expected_fields | — | candidate |

## 9. 逐 source 结果

| source_id | validation_status | access_status | http_status | sample_rows | recommended_status |
|-----------|-------------------|---------------|-------------|-------------|-------------------|
| disclosure_schedule | dry_run | dry_run | — | — | testing |
| margin_trading | dry_run | dry_run | — | — | testing |
| block_trade | dry_run | dry_run | — | — | testing |
| restricted_shares_unlock | dry_run | dry_run | — | — | testing |
| abnormal_trading | dry_run | dry_run | — | — | testing |
| szse_calendar | needs_manual_endpoint_discovery | dry_run | — | — | candidate |
| equity_pledge | dry_run | dry_run | — | — | testing |
| shareholder_change | dry_run | dry_run | — | — | testing |
| executive_shareholding | dry_run | dry_run | — | — | testing |
| fund_industry_allocation | sample_ok | ok | 200 | 19 | testing |
| shareholder_data | sample_ok | ok | 200 | 5255 | testing |
| ipo_query | needs_manual_endpoint_discovery | dry_run | — | — | candidate |

## 10. 本次 live 验证（fund_industry_allocation + shareholder_data）

运行：`python lab/validate_cninfo_table_sources.py --source-id fund_industry_allocation --source-id shareholder_data`

### fund_industry_allocation（基金行业配置）

| 项 | 值 |
|----|-----|
| HTTP status | **200** |
| sample_rows | **19** |
| observed_total_rows | **19** |
| field_count | **6** |
| records path | `data.records` |
| company_code_available | **no** |
| date_available | **yes** |
| amount_available | **yes** |
| recommended_status | **testing** |

**注意：** industry-level aggregate，不是 company-level source；后续不要归入 company event。

### shareholder_data（股东数据）

| 项 | 值 |
|----|-----|
| HTTP status | **200** |
| sample_rows | **5255** |
| observed_total_rows | **5255** |
| field_count | **9** |
| records path | `data.records` |
| company_code_available | **yes** |
| date_available | **yes** |
| amount_available | **yes** |
| recommended_status | **testing** |

### 计数

| 指标 | 数值 |
|------|------|
| priority-2 testing source | **5** |
| 全库 testing source | **10** |
| verified | **0** |

## 11. 下一步建议

1. **DevTools 抓 XHR**（priority-2）：`szse_calendar` / `equity_pledge` / `shareholder_change` 等
2. **回填** `config/cninfo_table_sources.yaml` 的 `api_url` 与 `params_template`
3. **本地小样本 live 跑**：`python lab/validate_cninfo_table_sources.py --source-id <id>`
4. 遇登录 / 验证码 / 付费 → 标 `blocked`，不绕过
5. 字段可得性达标后，将 D 类状态从 `candidate` 提升至 `testing`
6. **暂缓全市场**；Phase 1 A 类 BSE residual 作为 later improvement

## 12. 边界

- 不登录；不绕过权限；不大规模请求；不入库
- 不写 **verified**
- 仅代表配置与小样本探测，非全市场结论
