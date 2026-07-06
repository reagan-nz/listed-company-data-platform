# CNINFO Era C Phase 2 D 类固定表格入口探测计划

- 生成时间：2026-07-05（离线整理）
- 权威分层：[plans/cninfo_data_source_layered_inventory.md](../../plans/cninfo_data_source_layered_inventory.md)（D 类）
- Phase 1 收口：[cninfo_report_phase1_final_summary.md](cninfo_report_phase1_final_summary.md)
- 配置草案：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)
- 验证脚本：`lab/validate_cninfo_table_sources.py`
- 验证产物：[cninfo_table_sources_validation_summary.md](cninfo_table_sources_validation_summary.md)

---

## 1. 阶段目标

**Era C Phase 2** 验证 CNINFO **D 类固定表格 / 市场行为数据**入口，判断：

- 哪些数据源能 **稳定公开访问**；
- 返回是否为 **结构化表格**（JSON / HTML table / Excel 等）；
- **字段是否可盘点**，是否适合后续工程化为 company event / market table。

**本阶段只做：**

- 入口探测；
- 字段盘点；
- 可用性分类（`recommended_status`）。

**本阶段不做：**

- 全量抓取；
- 入库（PostgreSQL / MinIO / MongoDB）；
- 生产化 pipeline；
- PDF 下载 / 解析。

**边界：** 不写 `verified`；不绕过登录 / 验证码 / 付费 / 权限。

---

## 2. 为什么做 D 类

| 维度 | A 类（已阶段性收口） | D 类（本阶段） |
|------|------------------------|----------------|
| 数据形态 | 定期报告 **PDF 文档流** | **固定表格** / 日期型列表 |
| 典型用途 | 年报、季报全文检索 | 披露日程、融资融券、大宗交易、解禁、增减持等 |
| 稳定性 | 高（per-company coverage 94.10%） | **较高**（列名相对固定，按交易日或计划更新） |
| 验证口径 | coverage% | **字段可得性%** + 入口稳定性 |

A 类能提供 **年度 / 季度文档**；D 类可补充 **更动态的结构化公司事件与市场行为**。若入口稳定、字段清楚，可作为后续 `scheduled_disclosure`、`share_unlock`、`margin_snapshot` 等表的候选来源。

---

## 3. 候选数据源清单

| source_id | 中文名称 | 数据类型 | 可能字段 | 可能用途 | 预期难度 | recommended_status（初始） |
|-----------|----------|----------|----------|----------|----------|---------------------------|
| `disclosure_schedule` | 预约披露 | 表格 / 日期型 | 公司代码、简称、报告类型、预约披露日 | 披露日历、`scheduled_disclosure` 事件 | 中（需抓 XHR） | `unknown` |
| `margin_trading` | 融资融券 | 表格 / 日频 | 融资余额、融资买入额、融券余量、融券余额 | 市场行为指标、杠杆观察 | 中 | `unknown` |
| `block_trade` | 大宗交易 | 表格 / 日频 | 成交价、成交量、买卖营业部、折溢价 | 大宗交易事件 | 中 | `unknown` |
| `restricted_shares_unlock` | 限售解禁 | 表格 / 事件型 | 解禁日期、解禁数量、占总股本比例、股东 | `share_unlock` 事件 | 中 | `unknown` |
| `abnormal_trading` | 公开信息 / 异常交易 | 表格 | 公司代码、公开原因、公开起止日 | 异常交易 / 风险线索 | 中 | `unknown` |
| `szse_calendar` | 深市日历 | 日历型 | 股东会、分红登记日、除权除息日、停复牌 | 深市公司日程 | 中高（日历聚合） | `unknown` |
| `equity_pledge` | 股权质押 | 表格 / 查询 | 质押股数、质押比例、质押方、公告日 | 质押风险线索 | 中高 | `unknown` |
| `shareholder_change` | 股东增减持 | 表格 / 查询 | 增减持主体、变动数量、比例、日期 | 股东变动事件 | 中高 | `unknown` |
| `executive_shareholding` | 高管持股 | 表格 / 查询 | 高管姓名、职务、持股数量、变动日期 | 治理 / 激励线索 | 中高 | `unknown` |
| `ipo_query` | IPO 查询 | 表格 / 查询 | IPO 公司、审核阶段、发行信息、披露日 | 发行事件、与 A 类招股书联动 | 中 | `unknown` |

---

## 4. 验证口径

每个 `source_id` 至少验证以下 8 项：

| # | 验证项 | 记录字段 |
|---|--------|----------|
| 1 | 页面是否可打开 | `page_url`、`http_status`、`access_status` |
| 2 | 是否存在公开接口 | `api_url`（DevTools / 文档确认，**不猜测**） |
| 3 | 是否需要登录 / 权限 / 验证码 | `requires_login`、`requires_captcha`、`requires_paid_permission` |
| 4 | 返回形态 | `response_type`（json / html_table / excel / pdf / unknown） |
| 5 | 能否获取字段名 | `field_count`、`key_fields` |
| 6 | 能否拿到小样本行 | `sample_rows`（默认 ≤ 10 行） |
| 7 | 关键维度是否可得 | `company_code_available`、`date_available`、`amount_available` |
| 8 | 是否适合后续工程化 | `validation_status`、`recommended_status`、`notes` |

**成功指标（D 类）：**

- **字段可得性%** = 期望字段中非空且可解析数 / 期望字段数；
- 可选：**row_count > 0** 比例（小样本探测）。

---

## 5. recommended_status 标准

| 状态 | 定义 |
|------|------|
| **testing** | 公开可访问；返回结构化数据；小样本可取；字段清楚 |
| **candidate** | 页面可访问；字段有价值；但接口或参数还需确认 |
| **partial** | 部分可访问；字段不完整或返回不稳定 |
| **blocked** | 需要登录 / 权限 / 验证码 / 付费服务；**不绕过，暂不继续** |
| **unknown** | 尚未确认（初始默认） |

**不允许写 `verified`。**

---

## 6. 输出格式

验证脚本产出：

| 文件 | 说明 |
|------|------|
| `outputs/validation/cninfo_table_sources_validation.csv` | 逐 source 验证行 |
| `outputs/validation/cninfo_table_sources_validation_summary.md` | 汇总 + 下一步 |

### CSV 字段建议

`source_id`, `source_name`, `page_url`, `api_url`, `http_status`, `access_status`, `requires_login`, `requires_captcha`, `requires_paid_permission`, `response_type`, `sample_rows`, `field_count`, `key_fields`, `company_code_available`, `date_available`, `amount_available`, `validation_status`, `recommended_status`, `notes`

---

## 7. 边界

- **不登录**；遇权限 / 验证码 / 付费 → 标 `blocked`，不绕过。
- **不大规模请求**；小样本（默认每 source ≤ 1 次 API 请求、≤ 10 行）。
- 请求间 **sleep**（默认 0.6s）。
- **不入库**；不接 PostgreSQL / MinIO / MongoDB。
- **不下载 / 解析 PDF**；不使用 BrowserUser。
- **不写 verified**。

---

## 8. 执行顺序（建议）

1. **配置草案** — `config/cninfo_table_sources.yaml`（`api_url` 未知则 `null`）
2. **脚本骨架** — `lab/validate_cninfo_table_sources.py`（`--dry-run` 先跑通）
3. **手工 DevTools** — 按优先级抓 XHR：`disclosure_schedule` → `margin_trading` / `block_trade` / `restricted_shares_unlock` / `abnormal_trading`
4. **回填 config** — 写入确认后的 `api_url`、`params_template`
5. **小样本验证** — 本地合规环境跑脚本（关 VPN 按需）
6. **更新 summary** — 回填分层表 D 类 `recommended_status`

**不要与 Phase 1 大改并行；不要同时展开 B/C/E/F Phase。**
