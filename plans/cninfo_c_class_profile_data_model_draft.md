# CNINFO C 类 Company Profile Data Model Draft

_最后更新：2026-07-05_

> **性质：** 逻辑模型草案；**不建表、不入库、不写 migration**。  
> **发现设计：** [cninfo_c_class_f10_source_discovery_design.md](cninfo_c_class_f10_source_discovery_design.md)  
> **边界：** [cninfo_c_vs_b_vs_d_boundary.md](cninfo_c_vs_b_vs_d_boundary.md)

---

## 1. 目标

定义 C 类 **company profile snapshot** 的逻辑对象，用于：

- 统一多 F10 标签页 / JSON 源的字段命名
- 支撑 known-company profile validation
- 为未来 PostgreSQL `company_profile` 候选表提供映射依据（**当前不实现**）

**核心原则：** 一条 snapshot = 一个 `source_id` × 一个 `company_code` × 一个 `profile_section` × 一个 `snapshot_date`（或采集时刻）。

---

## 2. company_profile_snapshot

顶层快照记录（对应未来 ingestion 行；当前仅 fixture / validation 行）。

| 字段 | 类型 | 说明 |
|------|------|------|
| `profile_snapshot_id` | string | 稳定哈希或 UUID；`hash(source_id, company_code, profile_section, snapshot_date)` |
| `source_id` | string | C 类 registry source，如 `cninfo_company_basic_profile` |
| `company_code` | string | 6 位证券代码 |
| `company_name` | string | 采集时简称 / 全称（可空） |
| `org_id` | string | CNINFO orgId；桥接 A 类 mapping |
| `snapshot_date` | date | 页面展示日期或采集 UTC 日期（ISO `YYYY-MM-DD`） |
| `profile_section` | string | 逻辑分区：`basic` / `executive` / `share_capital` / `shareholder` / … |
| `raw_record_json` | object | 源响应原文或裁剪 JSON |
| `raw_record_hash` | string | `raw_record_json` 规范化哈希 |
| `source_status` | string | `candidate` / `testing` / `partial` / `blocked`（**非 verified**） |
| `field_confidence` | string | `high` / `medium` / `low` / `unknown` |
| `created_at` | datetime | 采集时间（UTC ISO） |

**不包含：** `pdf_url`、`document_type`、`chunk_id`（属 B 类）。

---

## 3. company_basic_profile

从 `cninfo_company_basic_profile` / 基本资料标签页归一化。

| 字段 | 类型 | 说明 |
|------|------|------|
| `company_code` | string | PK 组成部分 |
| `company_name` | string | 证券简称 |
| `legal_name` | string | 法定全称 |
| `english_name` | string | 英文名称 |
| `industry` | string | 所属行业（展示用） |
| `listed_board` | string | 主板 / 创业板 / 科创板 / 北交所 |
| `exchange` | string | SSE / SZSE / BSE |
| `listing_date` | date | 上市日期 |
| `registered_capital` | string | 注册资本（保留原文字符串 + 单位） |
| `legal_representative` | string | 法定代表人 |
| `company_website` | string | 公司网址 |
| `business_scope` | string | 经营范围（可与 business_scope source 交叉） |
| `registered_address` | string | 注册地址 |
| `office_address` | string | 办公地址 |

---

## 4. executive_profile

从 `cninfo_executive_profile` / 治理结构标签页归一化。一人一行。

| 字段 | 类型 | 说明 |
|------|------|------|
| `company_code` | string | |
| `person_name` | string | 姓名 |
| `position` | string | 职务 |
| `gender_candidate` | string | 性别（若页面提供） |
| `birth_year_candidate` | string | 出生年份候选 |
| `education_candidate` | string | 学历候选 |
| `term_start_candidate` | date | 任期起始 |
| `term_end_candidate` | date | 任期结束 |
| `raw_record_json` | object | 原始行 |

**注意：** 高管 **持股变动**、**离任公告** 属 D 类 event 或 B 类 document，不写入本表。

---

## 5. share_capital_profile

从 `cninfo_share_capital_profile` 归一化。

| 字段 | 类型 | 说明 |
|------|------|------|
| `company_code` | string | |
| `report_date` | date | 股本数据截止日期 |
| `total_share_capital` | number | 总股本 |
| `float_share_capital` | number | 流通股本 |
| `restricted_share_capital` | number | 限售股本 |
| `share_unit` | string | 股 / 万股 |
| `raw_record_json` | object | |

---

## 6. shareholder_profile

从 `cninfo_top_shareholders_profile` / `cninfo_top_float_shareholders_profile` 归一化。一股东一行。

| 字段 | 类型 | 说明 |
|------|------|------|
| `company_code` | string | |
| `report_period` | string | 报告期或截止日 |
| `shareholder_name` | string | 股东名称 |
| `shareholder_type_candidate` | string | 机构 / 个人 / 国有等 |
| `holding_shares` | number | 持股数量 |
| `holding_ratio` | number | 持股比例（%） |
| `rank` | integer | 排名 |
| `shareholder_scope` | enum | 见下 |
| `raw_record_json` | object | |

**shareholder_scope 枚举：**

| 值 | 说明 |
|----|------|
| `top_shareholder` | 十大股东 |
| `top_float_shareholder` | 十大流通股东 |

**注意：** D 类 `shareholder_data`（股东人数变化）是 **metric event**，不是本 snapshot。

---

## 7. profile quality flags

验证与 ingestion 共用质量标记（不写 verified）。

| flag | 含义 |
|------|------|
| `missing_org_id` | 无 orgId，无法构造 F10 请求 |
| `stale_snapshot` | snapshot_date 明显落后于页面或已知披露 |
| `field_missing` | expected_field 在 raw 中缺失 |
| `inconsistent_company_name` | 跨 source 公司名称冲突 |
| `parse_partial` | HTML / JSON 仅部分字段可解析 |
| `source_blocked` | 登录 / 验证码 / 403 |
| `schema_changed` | 响应结构与 probe 记录不一致 |

---

## 8. 当前不实现

| 项 | 说明 |
|----|------|
| 不建表 | 无 DDL |
| 不入库 | 无 PostgreSQL 写入 |
| 不写 migration | `database/schema` 不动 |
| 不抓全量 | 仅设计 + 小样本 probe 规划 |
| 不写 verified | `source_status` 最高 `testing_stable_sample`（未来） |

---

## 9. 与 B / D 逻辑表对照（简表）

| C 类逻辑对象 | 易混淆的 B / D 对象 |
|--------------|---------------------|
| `company_basic_profile` | B 类年报 PDF 中的公司简介段落（文本证据，非 snapshot API） |
| `executive_profile` | D 类 `management_change` event |
| `shareholder_profile` | D 类 `shareholder_change` / `shareholder_data` |
| `share_capital_profile` | D 类限售解禁 **event**（时点事件，非股本结构表） |

详见 [cninfo_c_vs_b_vs_d_boundary.md](cninfo_c_vs_b_vs_d_boundary.md)。
