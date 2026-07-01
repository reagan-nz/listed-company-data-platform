# CNINFO P0 小样本验证最终总结

> Issue #81–#84 汇总 · 验证阶段：2026-07 · **小样本验证已完成，部分可用，部分仍需后续映射 / 稳定性处理**

## 1. 验证范围

本轮 CNINFO P0 小样本验证覆盖以下四个对象（对应 GitHub Issue #81–#84）：

| Issue | 验证对象 | 主要产物 |
|---|---|---|
| #81 | 样本公司清单 | `cninfo_p0_sample_companies.csv` |
| #82 | 最新公告列表 | `cninfo_latest_announcement_validation.csv` |
| #83 | 公告 PDF 元数据 | `cninfo_pdf_metadata_validation.csv` |
| #84 | 个股 F10 / 公司资料 | `cninfo_f10_validation_final_summary.md` 等 |

**边界强调：**

- 本轮为 **P0 小样本验证**（40 家公司），**不是**全量采集，**不是**生产 pipeline。
- **不做** PostgreSQL / MongoDB / MinIO 数据库接入。
- **未使用** BrowserUser；不绕过登录 / 验证码 / 权限。
- 结论**只代表当前小样本验证结果**，不代表 CNINFO 栏目长期稳定可用。

---

## 2. 样本公司

基于 #81 结果（`cninfo_p0_sample_company_summary.md`）：

| 指标 | 数值 |
|---|---|
| 样本公司数 | 40 |
| 覆盖板块 | 主板（20）、创业板（7）、科创板（7）、北交所（6） |

**说明：**

- 样本来自本地 `full_market_2024` 输出，覆盖不同交易所与板块。
- 部分辅助字段如 `industry`、`listing_status`、`market_cap_group`、`announcement_frequency_group` 仍为 `unknown`，**不影响**第一轮页面可达性、字段可得性与失败原因记录。

---

## 3. 最新公告列表验证结果

基于 #82 结果（`cninfo_latest_announcement_validation_summary.md`）：

| 指标 | 数值 |
|---|---|
| 样本公司数 | 40 |
| 成功公司数 | 34 |
| partial | 0 |
| 失败公司数 | 6 |
| 输出记录数 | 108 |
| 成功公告记录 | 102 |

**字段可得性（按行计数）：**

| 字段 | 可得 / 总数 |
|---|---|
| announcement_title | 102 / 108 |
| publish_time | 102 / 108 |
| source_url | 102 / 108 |
| pdf_url | 102 / 108 |
| announcement_type | 102 / 108 |

**主要问题：**

- 6 家失败公司均为北交所 **430 开头旧代码**（430017、430047、430090、430139、430198、430300），失败原因 `no_announcements_returned`。
- 脚本已尝试 430→920 映射回退，本次仍未返回公告；**不代表**公司无公告，更可能是代码映射 / 查询口径问题。
- 后续在 #84 F10 验证中已确认 BSE **430→920 + 人工 orgId** 映射方向；公告列表侧仍需类似映射机制。

**recommended_status：`testing / partial`**

- 整体可用性较好（34/40 公司成功），但 BSE old code 映射问题未解决。
- 不写 `verified`（未覆盖全部板块样本成功）。

---

## 4. 公告 PDF 元数据验证结果

基于 #83 结果（`cninfo_pdf_metadata_validation_summary.md`）：

| 指标 | 数值 |
|---|---|
| 候选 PDF | 100 |
| 实际验证 | 100 |
| success | 100 |
| partial | 0 |
| failed | 0 |

**字段可得性：**

| 字段 | 可得 / 总数 |
|---|---|
| http_status_code = 200 | 100 / 100 |
| content_hash | 100 / 100 |
| file_size | 100 / 100 |
| mime_type | 100 / 100 |

**要点：**

- `content_hash` 使用 **sha256**，基于 PDF **原始二进制内容**计算，不基于 URL / 标题 / 文本。
- **未保存** PDF 原件，**未上传** MinIO，**未解析**正文。
- 样本来自 #82 成功公告记录的 `pdf_url`。

**recommended_status：`testing`**

- P0 四项验证中**表现最好**，可作为后续 `raw_file` / `document` / MinIO 接入的**候选依据**。
- 仍不代表长期稳定可用；object_key / 去重规则尚未设计。

---

## 5. 个股 F10 / 公司资料验证结果

基于 #84 完整验证链（详见 `cninfo_f10_validation_final_summary.md`）：

### 5.1 入口与映射

- 旧接口 `/new/information/topSearch/detailOfQuery` **不适合**作为 F10 / 公司资料入口（40/40 failed）。
- 正确入口：`/new/disclosure/stock?stockCode=...&orgId=...#companyProfile`
- 页面依赖 **stockCode + orgId**；`company_code` 不能直接替代。

### 5.2 页面可达性（reachability）

| 指标 | 数值 |
|---|---|
| entry mapping 总数 | 40 |
| success | 23 |
| partial | 7 |
| failed | 10 |
| HTTP 200 | 30 / 40 |

- BSE 6 家人工映射后：**6/6 reachability success**
- STAR / 688 7 家人工 orgId 映射后：**7/7 reachability success**
- 仍有 **10 家** `needs_orgid_mapping`（000 深交所主板）

### 5.3 静态 HTML 字段验证

| 指标 | 数值 |
|---|---|
| 输入（reachability success 页面） | 23 |
| success / partial / failed | 0 / 0 / 23 |
| 各目标字段可得性 | **0 / 23** |

**结论：静态 HTML 不足以支持 F10 / 公司资料字段抽取。**

### 5.4 Playwright 字段验证

| 指标 | 数值 |
|---|---|
| 实际验证 | 30 |
| success | 22 |
| partial | 1 |
| failed | 7 |

**可提取字段（22–23 / 30）：**

- industry、company_profile、main_business_summary
- registered_address、office_address
- contact_phone、contact_email、board_secretary

**暂未提取到：**

- stock_short_name、listing_status、website（0 / 30）

**按 profile_url_rule：**

| rule | Playwright 结果 |
|---|---|
| manual_bse_430_to_920_orgid_mapping | 6 success / 0 failed |
| manual_star_orgid_mapping | 6 success / 1 partial / 0 failed |
| manual_rule_600_300_gssh0 | 10 success / 7 failed |

**最大阻塞：stockCode + orgId 映射自动化**（非页面本身不存在）。

**recommended_status：`partial / testing`**

- 数据源**有价值**，Playwright 可提取核心公司资料字段。
- **不写** `verified`（mapping 未完成、600/300 仍有 7 failed、10 家缺 orgId）。
- **不写** `rejected`。

---

## 6. 分层存储影响

> 以下仅为**后续数据库接入的设计依据**，**不代表已接入数据库**。

| 数据类型 | 建议未来落点 | 当前阶段 |
|---|---|---|
| PDF 原件 | MinIO | 未接入；#83 仅验证元数据 |
| PDF 元数据、公告 document 元数据 | PostgreSQL `document` / `raw_file` | 未接入；#83 100/100 success 为候选依据 |
| F10 公司资料字段 | `company_profile` 候选表或字段池 | 未接入；Playwright 已证明字段存在 |
| 低置信 / 未映射 / JS 失败 / orgId 缺失 | 候选层或验证报告 | 保留在 CSV / summary，不进正式库 |

**当前阶段不做 PostgreSQL / MongoDB / MinIO 接入。**

---

## 7. 当前 recommended_status 总结

| P0 对象 | 小样本结果 | recommended_status | 主要问题 |
|---|---|---|---|
| 样本公司清单 | 40 家，覆盖四板块 | —（输入基础） | industry 等辅助字段 unknown |
| 最新公告列表 | 34/40 公司成功；102/108 公告记录 | `testing / partial` | BSE 430 old code 6 家失败；需映射回退 |
| 公告 PDF 元数据 | 100/100 success | `testing` | 表现最好；未设计 MinIO / object_key |
| 个股 F10 / 公司资料 | reachability 23 success；Playwright 22/30 success | `partial / testing` | orgId 映射；静态 HTML 不足；需 Playwright |

> 所有 `recommended_status` 仅代表当前 P0 小样本结论，**不代表长期稳定 verified**。

---

## 8. 后续建议

1. **建立 `cninfo_stock_code` / `cninfo_org_id` 映射机制**（含 BSE 430→920、STAR 688 人工表扩展与自动化解析）。
2. **继续补 000 / remaining `needs_orgid_mapping` 10 家样本** orgId。
3. **对公告列表加入 BSE / old code 映射回退**（与 F10 BSE 映射方向对齐）。
4. **PDF 元数据进入 MinIO / raw_file 前**：设计 `object_key`、`sha256` 去重规则。
5. **对 F10 Playwright 字段抽取做稳定性测试**（含 reachability_partial 7 家全 failed、website 等未提取字段）。
6. **暂不进行全量 Playwright 抓取**（mapping 与规则未稳定）。
7. **后续再进入数据库接入设计**（`company_profile` schema、document 流等）。

---

## 9. 边界说明

- **未做**全量采集；**未做**生产爬虫。
- **未使用** BrowserUser。
- **未做** PostgreSQL / MongoDB / MinIO 数据库接入。
- **未上传** MinIO。
- **未将** CNINFO P0 数据源写成长期稳定 `verified`。
- 结论**只代表当前小样本验证结果**（40 家公司、100 份 PDF、F10 多轮验证链）。
- 撰写本文档时：**未联网、未运行新验证、未修改验证结果 CSV**。

---

## 附录：验证产物索引

| 阶段 | 文件 |
|---|---|
| #81 样本 | `cninfo_p0_sample_companies.csv`、`cninfo_p0_sample_company_summary.md` |
| #82 公告列表 | `cninfo_latest_announcement_validation.csv`、`_summary.md` |
| #83 PDF 元数据 | `cninfo_pdf_metadata_validation.csv`、`_summary.md` |
| #84 F10 | `cninfo_f10_validation_final_summary.md`、`cninfo_f10_orgid_mapping_analysis.md` 等 |

详细 F10 验证链路见 [cninfo_f10_validation_final_summary.md](cninfo_f10_validation_final_summary.md)。
