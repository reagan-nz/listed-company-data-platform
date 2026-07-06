# CNINFO C 类 JSON Schema Draft Notes

_最后更新：2026-07-05_

> **性质：** 逻辑 schema 草案；**不是**数据库 migration；不写 verified。  
> **上级：** [cninfo_c_class_profile_data_model_draft.md](cninfo_c_class_profile_data_model_draft.md) · [cninfo_c_class_f10_source_discovery_design.md](cninfo_c_class_f10_source_discovery_design.md)  
> **边界：** [cninfo_c_vs_b_vs_d_boundary.md](cninfo_c_vs_b_vs_d_boundary.md)

---

## 1. 目的

为 C 类 **company profile snapshot** 建立与 B 类 `schemas/b_class/`、D 类 `schemas/d_class/` 同级的 **JSON Schema draft-07** 逻辑记录形状，用于：

- 约束未来 known-company profile fixture 与 probe 产出；
- 支撑 field presence validation 与 cross-source consistency check；
- 与 [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) 对齐，但不替代 candidate YAML。

**当前阶段：** 仅 schema draft；**不请求 CNINFO**、不 probe endpoint、不入库。

---

## 2. Schema 覆盖范围

| Schema 文件 | 逻辑对象 | 用途 |
|-------------|----------|------|
| `c_company_profile_snapshot.schema.json` | 顶层 profile snapshot | 通用快照行；`profile_section` 分区 |
| `c_company_basic_profile.schema.json` | 基本资料归一化 | F10 基本资料字段 |
| `c_executive_profile.schema.json` | 高管 / 董事名单 | 一人一行；非 D 类 management event |
| `c_share_capital_profile.schema.json` | 股本结构 snapshot | 总股本 / 流通 / 限售 |
| `c_shareholder_profile.schema.json` | 十大股东 / 十大流通股东 | `shareholder_scope` 区分 |
| `c_profile_raw_snapshot.schema.json` | 抓取层 raw JSON | probe / fetch lineage；含 `endpoint`、`fetch_status` |

目录：`schemas/c_class/`（**6** 个 `.schema.json`）。

**与 10 个 candidate source 的映射（草案）：**

| source_id | 主要 schema |
|-----------|-------------|
| `cninfo_company_basic_profile` | `c_company_basic_profile` + snapshot |
| `cninfo_company_industry_profile` | snapshot (`industry_profile`) |
| `cninfo_company_business_scope` | snapshot (`business_scope`) |
| `cninfo_executive_profile` | `c_executive_profile` |
| `cninfo_share_capital_profile` | `c_share_capital_profile` |
| `cninfo_top_shareholders_profile` | `c_shareholder_profile` (`top_shareholder`) |
| `cninfo_top_float_shareholders_profile` | `c_shareholder_profile` (`top_float_shareholder`) |
| `cninfo_dividend_financing_profile` | snapshot (`dividend_financing_profile`) |
| `cninfo_company_contact_profile` | snapshot (`contact_profile`) |
| `cninfo_company_security_profile` | snapshot (`security_profile`) |

---

## 3. 与 B / D 类 schema 的区别

| 维度 | B 类 | C 类 | D 类 |
|------|------|------|------|
| 核心对象 | `b_document`、chunk、citation | `c_company_profile_snapshot`、profile 子表 | `d_company_event`、metric、schedule |
| 数据来源 | 公告 PDF metadata + 全文 | F10 / profile API / HTML 表格 | 固定表格 `data20/*` JSON |
| raw 层 | `b_raw_file`（PDF URL） | `c_profile_raw_snapshot` | `d_raw_record_snapshot` |
| 时间语义 | `announcement_date`、报告期 | `snapshot_date`、`report_period` | `event_date`、`trade_date` |
| 下游 | RAG、citation | company Wiki、company card | timeline、alerts、screening |
| 验证口径 | corpus retrieval | field presence%、known-company | field availability% |

C 类 schema **不复制** B 类 `document_type` / `pdf_url`；**不复制** D 类 event 字段。

---

## 4. Required 字段原则

1. **核心闭包：** 所有 profile 记录 **必须** 保留 `source_id`、`company_code`、`raw_record_json`、`raw_record_hash`（lineage 不可丢）。
2. **identity 键：** 各子表 required 含逻辑主键（`profile_id`、`executive_profile_id` 等）。
3. **不确定字段不 required：** `org_id`、`listing_date`、`holding_shares`、`endpoint` 等 probe 前可为 null 或缺失。
4. **endpoint 未 probe 前：** `c_profile_raw_snapshot.endpoint` **非 required**；`fetch_status: not_started` 合法。
5. **executive / shareholder 特例：** `person_name`+`position` 或 `shareholder_scope` 在对应子表 required，因行语义依赖这些键。
6. **无 verified enum：** `source_status` 最高 `testing_stable_sample`；**不出现** `verified`。

---

## 5. 当前 caveat

| 项 | 状态 |
|----|------|
| endpoint | **全部 null**（candidate YAML）；schema 允许 null |
| 字段语义 | 尚未 UI / DevTools 逐字段验证 |
| candidate source | 10 个均为 `recommended_status: candidate` |
| fixture | **尚无** C 类 JSONL fixture |
| validation 脚本 | **尚未**实现 `validate_cninfo_c_class_profile_schema.py` |
| verified | **禁止**写入任何 enum 或 status |

---

## 6. 下一步

1. 建立 C 类 registry lint（对齐 candidate YAML ↔ schema `source_id` / `profile_section`）。
2. 建立 known-company profile fixture 草案（`fixtures/c_class/`，offline / dry-run）。
3. 实现 `lab/validate_cninfo_c_class_profile_schema.py`（fixture 驱动，无 CNINFO 请求）。
4. per-source DevTools probe（1–3 家 / source）→ 回填 `endpoint` 与 `records_path`。
5. 与 [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md) §6 状态列同步。

---

## 参考

| 文档 | 路径 |
|------|------|
| C 类数据模型 | [cninfo_c_class_profile_data_model_draft.md](cninfo_c_class_profile_data_model_draft.md) |
| Candidate YAML | [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) |
| B 类 schema notes（对照） | [cninfo_b_class_json_schema_draft_notes.md](cninfo_b_class_json_schema_draft_notes.md) |
| D 类 raw snapshot（对照） | [schemas/d_class/d_raw_record_snapshot.schema.json](../schemas/d_class/d_raw_record_snapshot.schema.json) |
