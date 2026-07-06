# CNINFO C 类 F10 / Company Profile Source Discovery 设计草案

_最后更新：2026-07-05_

> **性质：** 设计草案；本阶段不请求大规模数据、不入库、不写 verified。  
> **权威分层：** [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md) §6  
> **数据模型：** [cninfo_c_class_profile_data_model_draft.md](cninfo_c_class_profile_data_model_draft.md)  
> **边界：** [cninfo_c_vs_b_vs_d_boundary.md](cninfo_c_vs_b_vs_d_boundary.md)  
> **候选配置：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)  
> **既有 P0 脚本（参考，非本阶段扩跑）：** `lab/validate_cninfo_f10_company_profile.py`

---

## 1. 目标

C 类负责 **公司画像型（company profile snapshot）** 数据，服务于 LLM Wiki / company card / 静态事实层，**不是** B 类 document corpus，也 **不是** D 类 fixed-table event row。

**典型画像字段域：**

| 域 | 示例字段 |
|----|----------|
| 基本资料 | 简称、全称、英文名称、上市板块、交易所 |
| 公司简介 | 主营业务叙述、公司概况文本 |
| 所属行业 | 证监会 / 申万 / CNINFO 展示行业 |
| 注册资本 | 注册资本金额、币种 |
| 上市日期 | 首次上市日期 |
| 高管信息 | 董事长、总经理、董秘、董事监事名单 |
| 股本结构 | 总股本、流通股本、限售股本 |
| 十大股东 / 十大流通股东 | 股东名称、持股数、持股比例、排名 |
| 分红融资概况 | 累计分红、融资次数摘要（profile 级，非 event timeline） |
| 经营范围 | 营业执照经营范围文本 |
| 联系方式 | 电话、传真、邮箱、官网、注册 / 办公地址 |

C 类产出的是 **profile snapshot**（某一时刻的公司侧写），不是按日滚动的事件流。

---

## 2. C 类 source 特征

| 特征 | 说明 |
|------|------|
| **数据形态** | 多为 F10 页面型 JSON 或 HTML-backed 表格；部分标签页需 JS 渲染 |
| **更新频率** | 低于 D 类日度指标；高于 A 类年报全文（季度 / 半年 / 事件驱动局部刷新） |
| **入口依赖** | `company_code` + `org_id` mapping（复用 Phase 1 / identity mapping） |
| **下游用途** | company Wiki profile、company card、静态事实查询 |
| **不适合** | 直接作为 event timeline、量化筛选主表、RAG 全文证据（后者属 B 类） |
| **验证单位** | known-company × profile_section × expected_field_set |

与 B 类 PDF 语料、D 类 `data20/*` 表格 API **入口不同、对象不同、验证口径不同**。

---

## 3. 与 A / B / D 的关系

| 层 | 代号 | 核心对象 | 典型入口 | 验证口径 |
|----|------|----------|----------|----------|
| **A** | report retrieval | 定期报告 PDF metadata | `hisAnnouncement/query` | expected-period coverage% |
| **B** | document_corpus | document / chunk / citation | 公告检索 + PDF URL | known-document / category-sample / corpus retrieval |
| **C** | company_profile | profile snapshot | F10 / 公司资料页 | field presence% · known-company profile |
| **D** | fixed-table | event / metric row | `data20/*` 等表格 API | field availability% · endpoint stability |

**依赖关系（设计层，非运行时强耦合）：**

- C 类 **复用** A 类 / identity mapping 的 `org_id`，但 **不** 消费 B 类 parse 结果作为主数据源。
- C 类 **可交叉引用** D 类（如股东人数变化），但 snapshot 与 event row **分表分源**。
- B 类公告 PDF **可补充** C 类缺失字段（如经营范围全文），但不应把 B 类 document 当 C 类 registry source。

---

## 4. 初始候选 source

以下 10 个逻辑 source 写入 [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)（`recommended_status: candidate`，endpoint 待 probe）：

| # | 逻辑 ID | source_category | 说明 |
|---|---------|-----------------|------|
| 1 | `cninfo_company_basic_profile` | `basic_profile` | 基本资料：简称、行业、上市日期、注册资本等 |
| 2 | `cninfo_company_industry_profile` | `industry_profile` | 行业分类、板块归属 |
| 3 | `cninfo_company_business_scope` | `business_scope` | 经营范围、主营业务摘要 |
| 4 | `cninfo_executive_profile` | `executive_profile` | 董事、监事、高管列表 |
| 5 | `cninfo_share_capital_profile` | `share_capital_profile` | 股本结构 snapshot |
| 6 | `cninfo_top_shareholders_profile` | `shareholder_profile` | 十大股东 |
| 7 | `cninfo_top_float_shareholders_profile` | `shareholder_profile` | 十大流通股东 |
| 8 | `cninfo_dividend_financing_profile` | `dividend_financing_profile` | 分红融资概况（profile 摘要） |
| 9 | `cninfo_company_contact_profile` | `contact_profile` | 联系方式、地址、官网 |
| 10 | `cninfo_company_security_profile` | `security_profile` | 证券简称、代码、上市状态、ST 标记等 |

---

## 5. Source discovery 方法

**原则：小样本、可复现、不扩量。**

| 步骤 | 做法 |
|------|------|
| 1. Identity | 复用 `cninfo_report_p1_identity_mapping.csv` / `cninfo_company_identity_mapping.csv` 的 `company_code` + `org_id` |
| 2. 页面观察 | DevTools 打开个股 F10 对应标签页，记录 XHR / fetch endpoint |
| 3. 小样本 | 每个 source **仅 1–3 家** mapped 公司（主板 + 创业板 + 科创板各可选 1） |
| 4. 记录项 | `endpoint` · `method` · `params` · `records_path` · 字段样例 JSON |
| 5. 禁止 | 全市场循环、高频请求、绕过登录 / 验证码 |

**与既有 P0 工作的关系：**

- Issue #84 `validate_cninfo_f10_company_profile.py` 已验证部分基本资料字段（Playwright 22/30，`partial/testing`）。
- 本设计 **不扩跑** 该脚本；下一阶段将按 **per-source** 拆分 probe 记录，写入 candidate YAML 的 `endpoint` 字段（确认前保持 `null`）。

**推荐 probe 样本公司（待正式选定）：**

| company_code | 用途 |
|--------------|------|
| `600000` | SSE 主板基准 |
| `300001` | ChiNext orgId 注意项 |
| `688001` | 科创板 |

---

## 6. Validation 口径

C 类 **不适合** D 类「字段可得性% = 非空列 / 期望列」的全市场表格口径，也 **不适合** B 类 corpus retrieval 的 title-pattern 命中。

**推荐四类验证：**

| 方法 | 说明 | 通过条件（草案） |
|------|------|------------------|
| **known-company profile validation** | 选 3–5 家 mapping 完整公司，逐 source 拉 snapshot | 期望字段非空率 ≥ 阈值（按 source 定义） |
| **field presence validation** | `expected_fields` 在 `raw_record_json` 中可追溯 | 单源字段 presence% |
| **cross-source consistency check** | 基本资料 vs 证券资料 vs 联系人 | `company_name` / `listing_date` 等关键字段不冲突 |
| **snapshot freshness check** | `snapshot_date` vs 页面展示日期 | 标记 `stale_snapshot` flag，不自动 fail |

**禁止作主指标：**

- 随机公司 success rate
- 全市场 F10 抓取覆盖率
- 与 D 类 row_count 混用

---

## 7. Status

沿用 Era C 统一状态机（**禁止 `verified`**）：

| 值 | 含义 |
|----|------|
| `candidate` | 设计 / 候选；endpoint 未确认或未独立验证 |
| `testing` | 小样本 probe 或字段验证进行中 |
| `testing_stable_sample` | 固定小样本可复现（仍非 full-market） |
| `partial` | 部分字段或部分板块可用 |
| `blocked` | 登录 / 验证码 / 结构变更阻塞 |
| `deprecated` | 入口失效，保留审计 |

本阶段全部 candidate YAML 源：**`recommended_status: candidate`**，`verified: false`。

---

## 8. 当前不做

| 项 | 说明 |
|----|------|
| 不入库 | 无 PostgreSQL / MinIO / MongoDB |
| 不写 migration | 无 `database/schema` 变更 |
| 不做全市场 F10 抓取 | 仅 1–3 家 / source probe |
| 不写 verified | 任何 source 不得标 verified |
| 不下载 PDF | C 类非 document corpus |
| 不解析 PDF | 画像字段来自 F10 / API，非 B 类 parse pipeline |

---

## 9. 下一步（设计后）

1. 按 source 逐个 DevTools probe → 回填 `cninfo_c_class_source_candidates.yaml` 的 `endpoint` / `page_url`。
2. 起草 C 类 JSON Schema（`schemas/c_class/`，另任务）。
3. 改造或新增 `lab/validate_cninfo_c_class_profile_sources.py`（known-company only，config 驱动）。
4. 与 [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md) §6 状态列同步。

---

## 参考

| 文档 / 脚本 | 路径 |
|-------------|------|
| A–F 分层表 | [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md) |
| C 类数据模型 | [cninfo_c_class_profile_data_model_draft.md](cninfo_c_class_profile_data_model_draft.md) |
| C / B / D 边界 | [cninfo_c_vs_b_vs_d_boundary.md](cninfo_c_vs_b_vs_d_boundary.md) |
| 候选 YAML | [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) |
| P0 F10 验证 | `lab/validate_cninfo_f10_company_profile.py` |
| Era C 总计划 | [eraC_execution_plan.md](eraC_execution_plan.md) §7 |
