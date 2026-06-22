# 数据库字段 Schema

## 目标字段（11 项）

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

- **金融 schema**：独立的字段集（业务条线、贷款结构、不良率等）
- **BrowserUser 补充字段**：投资者问答、官网业务描述、专利数量等
- **跨年度字段**：同一公司多年年报的字段变化追踪

详见 [ROADMAP.md](../ROADMAP.md) 第三阶段。
