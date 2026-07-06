# CNINFO D 类 Schema Validation Plan

_最后更新：2026-07-05_

> **前置：** [cninfo_d_class_registry_lint_design.md](cninfo_d_class_registry_lint_design.md) · [schemas/d_class/](../schemas/d_class/)  
> **Registry：** [config/cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml)

---

## 1. 目的

在 Phase 3 完成 **registry YAML** 与 **JSON Schema draft** 之后，需要一套 **离线 schema validation 计划**，用 Phase 2 已有小样本 record **fixture** 验证：

- 逻辑 record shape 是否符合 JSON Schema；
- registry → mapper → schema 链路是否闭合；
- `raw_record_json` lineage 字段是否齐全。

**当前阶段：** 仅计划与设计；**不**重新请求 CNINFO；**不**入库；**不写 verified**。

---

## 2. 验证对象

| # | JSON Schema 文件 | 逻辑表 |
|---|------------------|--------|
| 1 | `d_source_registry.schema.json` | d_source_registry |
| 2 | `d_source_validation_run.schema.json` | d_source_validation_run |
| 3 | `d_field_semantics.schema.json` | d_field_semantics |
| 4 | `d_company_event.schema.json` | d_company_event |
| 5 | `d_company_metric_daily.schema.json` | d_company_metric_daily |
| 6 | `d_company_metric_periodic.schema.json` | d_company_metric_periodic |
| 7 | `d_disclosure_schedule.schema.json` | d_disclosure_schedule |
| 8 | `d_industry_aggregate.schema.json` | d_industry_aggregate |
| 9 | `d_event_party_detail.schema.json` | d_event_party_detail |
| 10 | `d_raw_record_snapshot.schema.json` | d_raw_record_snapshot |

**JSON Schema 版本：** draft-07。

---

## 3. Fixture 来源

### 3.1 原则

- Fixture **来自 Phase 2 已观测样本**，不重新抓取 CNINFO。
- 可从以下来源 **手工摘录或脚本离线生成**（未来）：
  - `outputs/validation/cninfo_table_sources_multidate_stability.csv` 对应时期的 raw 样本（若已保存）；
  - DevTools 保存的 JSON 片段（文档化）；
  - 人工构造的 **最小合法 object**（仅 schema 形状测试）。

### 3.2 建议目录结构（未来）

```
fixtures/d_class/
  disclosure_schedule/
    sample_prbookinfo_001.json          # raw CNINFO row
    transformed_schedule_001.json       # d_disclosure_schedule record
  margin_trading/
    sample_record_001.json
    transformed_metric_daily_F001N.json
  ...
  _meta/
    fixture_manifest.yaml               # source_id, schema, query_mode
```

**当前：** 已建立 `fixtures/d_class/`（11 fixture）；见 [cninfo_d_class_schema_validation_summary.md](../outputs/validation/cninfo_d_class_schema_validation_summary.md)。

### 3.3 每 source 最少 fixture 数（建议）

| 类型 | 建议数 |
|------|--------|
| 有数据 sample_ok | 1 raw + 1 transformed |
| empty_but_valid_response | 1 raw snapshot（records=[]） |
| 多模式 source（shareholder_change） | inc + desc 各 1 |
| executive_shareholding | 至少 1 个 varyType 模式 |

---

## 4. 验证策略

### 4.1 Registry validation（Phase 3a — 当前 lint）

**工具：** `lab/lint_cninfo_d_class_registry.py`

**做法：**

1. 读取 YAML `sources[]`；
2. 对每个 source 构造与 `d_source_registry.schema.json` 对齐的 JSON 对象（去掉 YAML 注释-only 顶层键）；
3. 可选：使用 `jsonschema` 库校验（lint 草案先检查必填与 enum，完整 validate 为下一步）。

**通过标准：** 无 FAIL 级 lint finding。

### 4.2 Transformed record validation（Phase 3b — 待实现）

**工具：** `lab/validate_cninfo_d_class_schema.py`

**流程：**

```
raw_record (fixture)
    → mapper(source_id, registry.mapping)
    → logical record(s)   # event 1:1; metric 1:N
    → jsonschema.validate(record, target_schema)
```

**Mapper 职责：**

| source | 输出 schema | 备注 |
|--------|-------------|------|
| margin_trading | N × `d_company_metric_daily` | 每 confirmed metric 一行 |
| shareholder_data | N × `d_company_metric_periodic` | 6 metrics |
| fund_industry_allocation | N × `d_industry_aggregate` | 3 metrics |
| 其余 event | 1 × `d_company_event` | 保留 raw_record_json |

**不校验：** `uncertain` / `not_visible_on_ui` 字段是否填入标准列（应留在 raw）。

### 4.3 Raw snapshot validation（Phase 3c — 待实现）

**目标 schema：** `d_raw_record_snapshot.schema.json`

**输入：**

- `raw_record_json`（或完整 response 片段）；
- `query_params`、`request_url`、`records_path`；
- `fetch_status`、`http_status`（来自 validation CSV 元数据，非新请求）。

用于验证 **lineage 层** 可独立存储、可重放映射。

### 4.4 Party detail validation（Phase 3d — 可选）

**目标 schema：** `d_event_party_detail.schema.json`

**输入：** `abnormal_trading` fixture 中 `detail[]` 每个元素 + 父 `event_id`。

**当前：** schema 已定义；mapper **未实现**。

---

## 5. 每类 source 的 schema target

| source_id | 主 schema | 次要 / 可选 | query_mode 注意 |
|-----------|-----------|---------------|-----------------|
| disclosure_schedule | d_disclosure_schedule | — | section_time_paged |
| restricted_shares_unlock | d_company_event | — | tdate_daily |
| block_trade | d_company_event | d_company_metric_daily（可选 ETL） | tdate_daily |
| margin_trading | d_company_metric_daily | — | detailList_default |
| abnormal_trading | d_company_event | d_event_party_detail | single_day_paged |
| equity_pledge | d_company_event | — | tdate_daily |
| shareholder_change | d_company_event | — | type_inc / type_desc |
| executive_shareholding | d_company_event | — | timeMark + varyType |
| shareholder_data | d_company_metric_periodic | — | rdate_report_period |
| fund_industry_allocation | d_industry_aggregate | — | default / rdate |

---

## 6. 不做的事

| 不做 | 原因 |
|------|------|
| 抓取新 CNINFO 数据 | Phase 2 已小样本验证；避免大规模请求 |
| 入库 | Era C 红线 |
| 写 SQL migration | 设计阶段 |
| 把 testing_stable_sample 升级为 verified | 禁止 verified |
| 强行校验 uncertain 字段为标准列 | 如 F005N、F008N、buyTotal |
| 全量 10 源 × 全历史日期 | 仅 fixture 级离线验证 |

---

## 7. 预期输出（未来）

| 文件 | 内容 |
|------|------|
| `outputs/validation/cninfo_d_class_schema_validation_report.csv` | 每 fixture 一行：source_id, schema, pass/fail, errors |
| `outputs/validation/cninfo_d_class_schema_validation_summary.md` | 汇总 pass rate、失败规则、缺口 |

**v1 已生成**（2026-07-05）：11 fixture PASS，22 logical records。

---

## 8. 实施顺序（下一步）

| 步骤 | 内容 | 状态 |
|------|------|------|
| 1 | **Registry lint** — `lab/lint_cninfo_d_class_registry.py` | **完成**（PASS） |
| 2 | 建立 `fixtures/d_class/` 每源 1–2 个 raw JSON | **完成**（11 fixture） |
| 3 | Mapper 草案 — raw → logical record（按 registry.mapping） | **完成**（v1） |
| 4 | `validate_cninfo_d_class_schema.py` + jsonschema | **完成**（11/11 PASS） |
| 5 | party detail / metric 拆行测试 | 部分（metric 全量；party detail deferred） |

---

## 9. 与 lint 的协作

```
cninfo_d_class_source_registry_draft.yaml
        │
        ├─► lint_cninfo_d_class_registry.py  (结构 / 枚举 / 映射)
        │
        └─► fixtures + mapper + jsonschema   (record shape)
```

Lint **必须先于** schema validation 通过，再投入 fixture 建设。

---

## 10. 边界

- 不写 **verified**
- schema validation pass **不等于** 生产 schema 锁定
- 仍保留 `raw_record_json` 为权威溯源
