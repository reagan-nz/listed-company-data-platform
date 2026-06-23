# 数据库 Schema

本文档包含两部分：**年报抽取字段定义**（当前 pipeline 输出）与 **关系型数据库存储方案 v1**（Issue #7）。

---

## 一、数据库存储方案 v1

### 设计目标

- 将分散在 `company_profile.json` / `eval_results.json` 中的结果**结构化入库**，便于查询、导出与跨批次对比。
- **v1 已实现 SQLite 原型**：`lab/db_init.py` 建表、`lab/db_import.py` 从 eval 产物导入小样本；JSON 仍为抽取主输出，数据库为聚合查询层。

### 表关系概览

```
company_basic (1) ──< report_source (N)
       │                    │
       └──────< extracted_field (N)  [company_code + report_year + field_name]
       
evaluation_result (N)  ── 关联 run_name + company_code + report_year + field_name（评估快照，可选 strict 结果）
```

### 1. `company_basic` — 公司主数据

| 列名 | 类型 | 说明 |
|---|---|---|
| `company_code` | TEXT PK | 股票代码，如 `600031` |
| `company_name` | TEXT | 公司简称或全称 |
| `exchange` | TEXT | `SSE` / `SZSE` / `BSE` |
| `board` | TEXT | `sse_main` / `star` / `chinext` / `szse_main` / `bse` |
| `is_financial` | INTEGER | 0/1，是否金融类（银行/券商/保险等） |
| `listing_status` | TEXT | `listed` / `delisted` / `st` 等（可选，后续扩展） |
| `created_at` | TEXT | ISO8601，首次入库时间 |
| `updated_at` | TEXT | ISO8601，最后更新时间 |

**来源映射**：`lab/eval_companies_1000.yaml`、`eval_results.json` 中的 `stock_code`、`short_name`、`exchange`、`financial`。

### 2. `report_source` — 年报来源与解析状态

| 列名 | 类型 | 说明 |
|---|---|---|
| `company_code` | TEXT | FK → company_basic |
| `report_year` | INTEGER | 报告年度，如 `2024` |
| `report_title` | TEXT | 公告标题（如「2024年年度报告」） |
| `source_url` | TEXT | 巨潮静态 PDF URL |
| `pdf_sha256` | TEXT NULL | PDF 哈希（有则填，来自 `company_profile.source`） |
| `download_status` | TEXT | `ok` / `no_announcement` / `error` / `skipped_cached` |
| `parse_status` | TEXT | `ok` / `no_text_layer` / `error` |
| `text_layer_ok` | INTEGER | 0/1，是否有可用文本层 |
| `created_at` | TEXT | ISO8601 |
| `updated_at` | TEXT | ISO8601 |

**主键建议**：`(company_code, report_year)`。

**来源映射**：`<code>/meta.json`、`eval_results.json` 的 `status`、`picked_title`、`source_url`、`page_count` / `text_len`。

### 3. `extracted_field` — 抽取字段（核心事实表）

| 列名 | 类型 | 说明 |
|---|---|---|
| `company_code` | TEXT | FK → company_basic |
| `report_year` | INTEGER | 与 report_source 一致 |
| `field_name` | TEXT | 字段 key，如 `mda`、`rnd_investment` |
| `field_label_cn` | TEXT | 中文标签 |
| `value` | TEXT | JSON 字符串（table/numeric/concentration 等复杂结构统一序列化） |
| `status` | TEXT | `found` / `partial` / `not_found` |
| `page` | INTEGER NULL | PDF 页码 |
| `evidence_sentence` | TEXT | 证据句（≤200 字符） |
| `source_url` | TEXT | 与 report_source 一致，便于单条追溯 |
| `in_region` | INTEGER NULL | 0/1，是否在 preferred region（MD&A/附注）内 |
| `anchor_matched` | TEXT NULL | 匹配到的锚点文本 |
| `extraction_version` | TEXT | 抽取器/git 版本或日期标签，如 `20260618` |
| `updated_at` | TEXT | ISO8601 |

**主键建议**：`(company_code, report_year, field_name, extraction_version)`；若只保留最新版，可对 `(company_code, report_year, field_name)` 做 UPSERT。

**来源映射**：`company_profile.json` → `fields[]`。

**value 存储说明**：与下方「各类型 value 格式」一致；入库前 `json.dumps(value, ensure_ascii=False)`。

### 4. `evaluation_result` — 评估与审计快照

| 列名 | 类型 | 说明 |
|---|---|---|
| `run_name` | TEXT | 评估批次，如 `eval1000`、`eval200` |
| `company_code` | TEXT | 公司代码 |
| `report_year` | INTEGER | 报告年度，与 report_source 一致 |
| `field_name` | TEXT | 字段 key |
| `proxy_plausible` | INTEGER | 0/1，自动 plausible 代理 |
| `strict_audit_result` | TEXT NULL | 严格审计结论：`PASS` / `FAIL` / `EYES` / `NA`（有则填） |
| `notes` | TEXT NULL | 备注（如 MISSED、FP 原因） |
| `created_at` | TEXT | ISO8601 |

**主键建议**：`(run_name, company_code, report_year, field_name)`。

**来源映射**：`eval_results.json` 各 field 的 `plausible`；严格审计结果来自离线审计脚本输出（当前未持久化为单文件，可后续导入）。

### SQLite vs PostgreSQL

| 维度 | SQLite | PostgreSQL |
|---|---|---|
| 部署 | 单文件，零配置 | 需独立服务与账号 |
| 适用阶段 | **本地原型、小团队、可复现** | 生产、多用户、大规模 |
| 并发写入 | 单写为主，够用 | 多连接、高并发 |
| 分享协作 | 复制 `.db` 文件即可 | 需托管实例与备份策略 |
| 迁移成本 | 后期可 pgloader / 自定义脚本迁 PG | — |
| 与当前产物 | 与 eval JSON 体量（946×11 行）匹配良好 | 全 A 股后仍适用 |

### SQLite 导入里程碑

| run_name | 导入时间 | company_basic | report_source | extracted_field | 说明 |
|---|---|---:|---:|---:|---|
| `eval1000` | 2026-06-18 | 1020 | 1020 | 10417 | baseline；cached validation 已验证 |
| `eval1000_v2` | 2026-06-22 | 1020 | 1020 | 10428 | 同 cohort 重跑，rules v2，PASS |
| `eval1000_independent_20260623` | 2026-06-23 | 1000 | 1000 | 10112 | 独立 cohort，泛化验证，PASS |
| `full_market_2024` | 待做 | ~5300 | ~5300 | ~55000–58000 | **下一大规模导入测试** |

### 推荐路线

**先用 SQLite 做原型与可复现验证**（例如 `outputs/db/listed_companies_v1.db`）：

1. 表结构稳定，三批次导入（eval1000 / v2 / independent）均已通过；
2. 团队内共享单文件数据库 + 文档即可复现查询；
3. full_market_2024 导入（~55000 行）将是首次大规模规模测试；
4. 待 full_market_2024 稳定、字段 schema 迭代完成后，**再迁移 PostgreSQL** 支撑全 A 股与多用户访问。

**原型实现**（Issue #8）：`lab/db_init.py` + `lab/db_import.py`，默认写入 `outputs/db/listed_companies_v1.db`（gitignore）。连接启用 `PRAGMA foreign_keys = ON`；导入支持单公司 profile 失败容错、审计字段 `in_region`/`anchor_matched` 入库。不修改 `extract_annual_report.py` / `field_schema.py`。

---

## 二、年报抽取字段（11 项）

当前 pipeline 从年报 PDF 抽取以下 11 项基础字段，适用于工业/制造业/科技类 A 股上市公司。

| # | key | 中文名 | 抽取方式 | 期望位置 |
|---|---|---|---|---|
| 1 | `mda` | 管理层讨论与分析 | section_snippet | 第三节 |
| 2 | `industry_discussion` | 所处行业情况 | section_snippet | MD&A 行业分析 |
| 3 | `main_business_segments` | 主营业务/业务板块 | section_snippet | MD&A 业务概述 |
| 4 | `major_products` | 主要产品及服务 | section_snippet | MD&A 产品描述/产品表 |
| 5 | `revenue_by_segment` | 营业收入构成-分行业/分产品 | table | MD&A 分行业/分产品表 |
| 6 | `revenue_by_region` | 营业收入构成-分地区 | table | MD&A 分地区表 |
| 7 | `top_customers` | 前五名客户 | concentration | MD&A 前五名客户 |
| 8 | `top_suppliers` | 前五名供应商 | concentration | MD&A 前五名供应商 |
| 9 | `rnd_investment` | 研发投入 | numeric | MD&A 研发投入表 |
| 10 | `major_subsidiaries` | 主要控股参股公司 | section_snippet | 附注或 MD&A |
| 11 | `risk_factors` | 风险因素 | section_snippet | MD&A 风险/展望 |

字段定义源码：[lab/field_schema.py](../lab/field_schema.py) 中的 `FIELD_SPECS`。

## 统一证据结构

每个字段输出应包含以下属性（已在 `company_profile.json` 中实现）：

| 属性 | 类型 | 说明 |
|---|---|---|
| `field` | string | 字段 key |
| `label_cn` | string | 中文标签 |
| `status` | string | `found` / `partial` / `not_found` |
| `in_region` | bool | 是否在 preferred region（MD&A/附注）内 |
| `value` | varies | 抽取值（见下方各类型） |
| `evidence_sentence` | string | 含锚点的原文句子（≤200 字符） |
| `page` | int | PDF 页码 |
| `anchor_matched` | string | 匹配到的锚点文本 |
| `source_url` | string | 官方 PDF URL |

### status 语义

| status | 含义 |
|---|---|
| `found` | 在 preferred region 内 + heading boundary 命中 + 有实质内容 |
| `partial` | 定位到相关区域但 confidence 不足（out-of-region、非 heading、表格 fallback 等） |
| `not_found` | 未找到该字段（含 genuinely N/A 的情况） |

## 各类型 value 格式

### section_snippet

```json
"value": "报告期内公司从事的主要业务 公司创业50多年来，专门致力于..."
```

文本片段，≥25 字符视为 plausible。

### table

```json
"value": {
  "table_page": 14,
  "rows": [["分地区", "营业收入", "..."], ["国内销售", "11,030,604,426.10", "..."]],
  "n_rows": 11,
  "match_hits": 2,
  "preview_from_row": 8
}
```

`match_hits ≥ 1` 且 rows 含数据行视为 plausible。

### numeric

```json
"value": {
  "labeled": [
    {"label": "研发投入", "value": "519,908,441.44"},
    {"label": "占营业收入", "value": "4.04%"}
  ],
  "context": "研发投入金额（元） 519,908,441.44 ..."
}
```

至少一个 labeled value 含数字视为 plausible（**当前规则过松，严格审计要求 TOTAL 标签 + 实质金额**）。

### concentration

```json
"value": {
  "amount": "200,469.22万元",
  "ratio": "25.87%",
  "sentence": "前五名供应商采购额200,469.22万元，占年度采购总额25.87%；"
}
```

`ratio` 或 `amount` 非空视为 plausible。

## 金融公司说明

当前 schema 按工业/制造业设计。金融公司（银行/券商/保险）的以下字段通常 N/A：

- `major_products`：无产品概念
- `revenue_by_segment` / `revenue_by_region`：按业务线/地区划分方式不同
- `top_customers` / `top_suppliers`：通常不披露
- `rnd_investment`：无研发投入表

这些字段返回 `not_found` 是**正确行为**，不应视为抽取失败。eval 中对金融公司单独统计。

## 未来 schema 扩展

- **金融 schema**：独立的字段集（业务条线、贷款结构、不良率等）→ 可增 `extracted_field.field_schema` 或独立表
- **BrowserUser 补充字段**：投资者问答等 → 新 `field_name` + `source_type` 列（v2）
- **跨年度字段**：同一公司多年 `report_year` 对比，依赖 `extracted_field` + `report_source` 时间序列

详见 [ROADMAP.md](../ROADMAP.md) 第二阶段与第三阶段。
