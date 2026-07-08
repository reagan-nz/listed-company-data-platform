# CNINFO C-Class Company Snapshot Architecture Plan

_生成时间：2026-07-08_

> **性质：** Company Snapshot 总体架构规划（Era C Phase 4）。**仅规划** · **不实现 DB/API** · **不写 verified**。

**依据：** [final field catalog](../outputs/validation/cninfo_c_class_final_field_catalog.csv) · [field freeze v1](cninfo_c_class_field_freeze_v1.md) · [product quality rules](cninfo_c_class_product_quality_rules_draft.md) · 863 harvest quality 产物

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

---

## 1. 设计目标

| 项 | 说明 |
|----|------|
| **是什么** | 以 **上市公司（company object）** 为中心的逻辑档案，聚合多源 normalized + raw evidence + quality metadata |
| **不是什么** | 按 CNINFO endpoint/source 分文件夹的 harvest 视图；不是 verified 全市场稳定层 |
| **当前输入** | 863 家 C-class harvest：`normalized/` 分源文件 + `raw/` 证据 + `quality/` 统计 |
| **输出形态（未来）** | 单公司 JSON/YAML snapshot + 模块级 quality rollup |

### 设计原则

1. **按 company object 分模块**，不按 `source_id` 分模块。
2. **normalized_core 进主槽**；review/raw/observe 走侧车策略。
3. **raw lineage 永远可追溯**（`document_evidence`）。
4. **quality 与业务字段解耦**（`data_quality` 模块）。
5. **多源冲突预留**（当前仅 cninfo_f10 已 harvest；年报/公告为 future Era B/D 接口）。

---

## 2. Snapshot 顶层结构

```json
{
  "snapshot_id": "sha256(company_code|as_of)",
  "company_code": "000009",
  "company_name": "中国宝安",
  "as_of": "2026-07-08T00:00:00Z",
  "snapshot_version": "v1_planning",
  "modules": {
    "company_identity": {},
    "securities_profile": {},
    "business_profile": {},
    "industry_profile": {},
    "financial_snapshot": {},
    "technology_profile": {},
    "organization_profile": {},
    "shareholder_profile": {},
    "executive_profile": {},
    "governance_profile": {},
    "dividend_profile": {},
    "capital_action_profile": {},
    "risk_profile": {},
    "event_timeline": {},
    "market_behavior": {},
    "investor_relation": {},
    "document_evidence": {},
    "data_quality": {}
  },
  "snapshot_status": "complete_with_caveat"
}
```

---

## 3. 一级模块定义（18）

### 3.1 `company_identity`

**用途：** 公司法定身份与基础识别信息。

| 字段示例 | 来源（当前） | 状态 |
|----------|-------------|------|
| company_code, company_name, legal_name, english_name | basic profile | normalized_core |
| establishment_date, listing_date | basic profile | normalized_core |
| registered_address, office_address | basic / contact derived | normalized_core |
| listing_sponsor | basic raw | raw_only（侧车） |

**模块状态（863）：** available（partial 地址类 caveat）

---

### 3.2 `securities_profile`

**用途：** 证券层面信息（代码、板块、上市状态）。

| 字段示例 | 来源 | 状态 |
|----------|------|------|
| listed_board, exchange | basic / industry derived | normalized_core |
| security_code, trading_status, listing_status | security profile | observe_only |

**策略：** 主 snapshot 使用 basic 的 `listed_board`/`exchange`；security observe 数据进侧轨 `observe_sidecar`。

---

### 3.3 `business_profile`

**用途：** 主营业务与经营描述。

| 字段 | 来源 | 状态 |
|------|------|------|
| business_scope, main_business_summary, company_profile_text | business_scope derived | normalized_core |
| basic 同名字段 | basic | review_later（避免重复，derived 优先） |

---

### 3.4 `industry_profile`

**用途：** 行业与板块标签。

| 字段 | 来源 | 状态 |
|------|------|------|
| industry, listed_board | industry derived | normalized_core |
| index_or_plate_labels | industry / basic | review_later |

**caveat：** 非完整行业分类体系；observed-only 语义。

---

### 3.5 `financial_snapshot`

**用途：** 资本与财务相关结构化字段（非完整财报）。

| 字段 | 来源 | 状态 |
|------|------|------|
| registered_capital | basic | normalized_core |
| total_share_capital, float_share_capital, restricted_share_capital | share_capital | normalized_core |
| compensation_candidate | executive | review_later |

**未来：** annual_report / quarterly_report 接入后升格为完整 financial 模块。

---

### 3.6 `technology_profile`

**用途：** 研发、专利、技术方向。

**当前：** **not_modeled** — C-class harvest 无独立 R&D 源。

**未来：** annual_report 技术研发章节 + 公告披露。

---

### 3.7 `organization_profile`

**用途：** 组织与联系信息（非高管个人维度）。

| 字段 | 来源 | 状态 |
|------|------|------|
| contact_email, contact_phone, contact_fax, company_website, postal_code | contact derived | normalized_core |
| board_secretary_candidate | contact / governance 交叉 | normalized_core |

---

### 3.8 `shareholder_profile`

**用途：** 股东持股结构（前十 / 前十流通）。

| 字段 | 来源 | 状态 |
|------|------|------|
| shareholder_name, holding_shares, holding_ratio, rank, report_period | top_sh / top_float | normalized_core |
| shareholder_type_candidate | top_sh / top_float | normalized_core |

**聚合：** `array_top_n_by_report_period`；scope=`top_shareholder` + `top_float_shareholder` 分子数组。

---

### 3.9 `executive_profile`

**用途：** 高管人员列表（一人一行）。

| 字段 | 来源 | 状态 |
|------|------|------|
| person_name, position, gender_candidate, birth_year_candidate, education_candidate | executive | normalized_core |
| shareholding_quantity_candidate, compensation_candidate | executive | review_later |

**聚合：** `array_merge_by_person_key`

---

### 3.10 `governance_profile`

**用途：** 治理结构与关键职务。

| 字段 | 来源 | 状态 |
|------|------|------|
| legal_representative | basic | normalized_core |
| board_secretary_candidate | contact | normalized_core |
| term_start_candidate, term_end_candidate | executive schema | review_later（源无字段） |

---

### 3.11 `dividend_profile`

**用途：** 分红历史与方案。

| 字段 | 来源 | 状态 |
|------|------|------|
| dividend_plan_text, report_period, payment/ex_date | dividend_history | normalized_core |

**caveat：** 10 条 manual review queue；002019/002060 parser patch 待实施。

---

### 3.12 `capital_action_profile`

**用途：** 股本变动与资本动作。

| 字段 | 来源 | 状态 |
|------|------|------|
| report_date, total/float/restricted share_capital | share_capital | normalized_core |
| change_reason_or_source, change_amount_candidate | share_capital | review_later |

**caveat：** share_capital `source_partial`（8 家 empty_but_valid）。

---

### 3.13 `risk_profile`

**用途：** 风险与异常状态标志。

| 字段 | 来源 | 状态 |
|------|------|------|
| is_delisted, is_st_candidate | security observe | observe_only |

**当前：** 侧轨观察；主 snapshot 不绑定 gate。

---

### 3.14 `event_timeline`

**用途：** 时间线事件（公告日、除权日等）。

| 字段 | 来源 | 状态 |
|------|------|------|
| announcement_date_candidate, ex_right_dividend_date_candidate | dividend | normalized_core |

**未来：** announcement（Era B）为主源。

---

### 3.15 `market_behavior`

**用途：** 市场交易行为侧轨（沪港通、上市年限等）。

| 字段 | 来源 | 状态 |
|------|------|------|
| sshk, szhk, listing_age_years, trading_status | security observe | observe_only |

---

### 3.16 `investor_relation`

**用途：** 投资者关系联系方式。

| 字段 | 来源 | 状态 |
|------|------|------|
| contact_email, contact_phone, contact_fax, company_website | contact derived | normalized_core |

---

### 3.17 `document_evidence`

**用途：** 原始证据与 lineage。

| 字段 | 来源 | 状态 |
|------|------|------|
| raw_record_json, raw_record_hash | 各源 lineage | normalized_core |

**规则：** raw 永远最高优先级；snapshot 必须保留 per-source evidence 指针。

---

### 3.18 `data_quality`

**用途：** 模块/字段级质量 rollup。

| 字段 | 来源 | 状态 |
|------|------|------|
| source_status | 各源 lineage | normalized_core |
| field_confidence | 各源 lineage | review_later |
| company_harvest_status, module_status, field_status | 计算 derived | future |

---

## 4. 模块与 harvest 源映射（参考）

| snapshot 模块 | 主要 normalized 输入源 |
|---------------|------------------------|
| company_identity | basic, contact |
| securities_profile | basic, industry, security(observe) |
| business_profile | business_scope |
| industry_profile | industry |
| financial_snapshot | basic, share_capital, executive |
| shareholder_profile | top_sh, top_float |
| executive_profile | executive |
| dividend_profile | dividend_history |
| capital_action_profile | share_capital |
| investor_relation | contact |
| document_evidence | 全部源 raw lineage |
| data_quality | 全部源 + quality/ |

---

## 5. Snapshot 构建流程（规划）

```
1. 读取 company_harvest_status（gate 前置）
2. 按模块加载 normalized 分源文件
3. 应用 field_mapping + source_priority
4. 冲突解析（conflict_resolution）
5. 附加 document_evidence
6. 计算 data_quality rollup
7. 输出 snapshot_status（quality_model）
```

**本轮不实现 builder** — 仅架构与映射规划。

---

## 6. 已知限制

- company_snapshot **未实现**（无 builder / 无 DB）
- security **observe-only** 不进主 gate
- technology / risk 模块 **not_modeled** 或仅侧轨
- BSE/abnormal 侧轨公司未纳入 863 universe
- 多源（年报/公告）尚未接入，priority 规则为 **forward-looking**

---

## 7. Gate

```
company_snapshot_architecture_plan_gate = PASS
```

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

**禁止：** completed · verified · testing_stable_sample

---

## 8. 相关产物

- [field mapping CSV](../outputs/validation/cninfo_c_class_company_snapshot_field_mapping.csv)
- [source priority rules](cninfo_c_class_snapshot_source_priority_rules.md)
- [conflict resolution](cninfo_c_class_snapshot_conflict_resolution.md)
- [quality model](cninfo_c_class_snapshot_quality_model.md)
- [planning summary](../outputs/validation/cninfo_c_class_company_snapshot_planning_summary.md)

---

## 9. 未来 PostgreSQL / API 逻辑结构（仅规划）

> **不创建数据库。** 以下为逻辑模型，供未来 Era D+ 接入参考。

### 9.1 逻辑表 / 文档结构

```json
{
  "company_snapshot": {
    "company_id": "gssz0000009",
    "company_code": "000009",
    "as_of": "2026-07-08",
    "identity": {},
    "securities": {},
    "business": {},
    "industry": {},
    "financial": {},
    "technology": null,
    "organization": {},
    "shareholders": [],
    "executives": [],
    "governance": {},
    "dividends": [],
    "capital_actions": [],
    "risk": {},
    "events": [],
    "market_behavior": {},
    "investor_relation": {},
    "evidence": {},
    "quality": {}
  }
}
```

### 9.2 字段来源分层

| 层级 | 说明 | 示例 |
|------|------|------|
| **normalized layer** | C-class harvest `normalized/` 映射字段 | company_name, industry, dividend_history[] |
| **raw evidence** | `raw/` + `raw_record_json` lineage | 全源原始 JSON、hash |
| **derived computation** | snapshot builder 计算 | snapshot_status, module rollup, conflict_resolution 结果 |

### 9.3 API 资源（规划）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/companies/{code}/snapshot` | GET | 完整 snapshot |
| `/companies/{code}/snapshot/modules/{module}` | GET | 单模块 |
| `/companies/{code}/snapshot/quality` | GET | 质量 rollup |
| `/companies/{code}/snapshot/evidence/{source_id}` | GET | raw 证据指针 |

### 9.4 索引候选（PostgreSQL 规划）

- `company_code` (PK lookup)
- `as_of` (时间旅行)
- `snapshot_status` (筛选 complete_with_caveat)
- GIN on `modules` JSONB（模块级查询）

**本轮不建表、不 migration。**

