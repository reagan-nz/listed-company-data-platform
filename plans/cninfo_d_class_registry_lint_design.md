# CNINFO D 类 Registry Lint 设计

_最后更新：2026-07-05_

> **脚本草案：** `lab/lint_cninfo_d_class_registry.py`  
> **Registry YAML：** [config/cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml)  
> **JSON Schema：** [schemas/d_class/](../schemas/d_class/)  
> **Schema 验证计划：** [cninfo_d_class_schema_validation_plan.md](cninfo_d_class_schema_validation_plan.md)

---

## 1. 目的

Phase 3 已将 10 个 `testing_stable_sample` source 沉淀为：

- machine-readable **registry YAML**；
- **JSON Schema** 逻辑 record shape；
- **mapping review** 与 **ingestion status model** 文档。

**Registry lint** 用于在 **本地、离线、无 CNINFO 请求** 前提下，检查 registry YAML 与 schema / mapping / status model 是否 **内部一致**，避免：

- `source_layer` 与 `target_logical_table` 错配；
- `verified` 误写入；
- `supported_modes` 遗漏（如 `type=dec`）；
- 字段分组重复或 `raw_record_required` 遗漏。

Lint **不**替代 Phase 2 live 验证；**不**入库；**不写 verified**。

---

## 2. Lint 输入

| 输入 | 路径 | 用途 |
|------|------|------|
| Registry YAML | `config/cninfo_d_class_source_registry_draft.yaml` | 主检查对象 |
| JSON Schema | `schemas/d_class/*.schema.json` | enum / 结构对照（如 `source_status`） |
| Mapping review | `plans/cninfo_d_class_source_to_schema_mapping_review.md` | 人工规则来源（layer→table） |
| Status model | `plans/cninfo_d_class_ingestion_status_model.md` | `source_status` / `fetch_status` 枚举 |
| Phase 2 config（可选） | `config/cninfo_table_sources.yaml` | 交叉检查 `api.url` 一致性（WARN） |

**不读取：** validation CSV、数据库、网络。

---

## 3. Lint 检查项

每条规则有唯一 `rule_id`、固定 `severity`、可机器解析输出。

### 3.1 source_id 唯一性 — `R001`

- `sources[].source_id` 不得重复。
- **FAIL** 若重复。

### 3.2 必填 registry 字段 — `R002`

每个 source 必须存在且非空：

| 字段路径 |
|----------|
| `source_id` |
| `source_name` |
| `source_layer` |
| `source_category` |
| `target_logical_table` |
| `api.url` |
| `api.method` |
| `api.records_path` |
| `status.recommended_status` |
| `status.verified` |
| `mapping.raw_record_required` |

- **FAIL** 若缺失。

### 3.3 禁止 verified — `R003` / `R004` / `R005`

| rule_id | 检查 |
|---------|------|
| R003 | `status.verified` 必须为 `false` |
| R004 | `status.recommended_status` 不得为 `verified` |
| R005 | registry 全文不得出现 `recommended_status: verified` 或独立 token `verified` 作为状态值（注释行除外） |

- **FAIL** 若违反。

### 3.4 source_layer 合法值 — `R006`

只允许：

- `company_event`
- `company_metric_daily`
- `company_metric_periodic`
- `disclosure_schedule`
- `industry_aggregate`

- **FAIL** 若非法。

### 3.5 target_logical_table 合法值 — `R007`

只允许：

- `d_company_event`
- `d_company_metric_daily`
- `d_company_metric_periodic`
- `d_disclosure_schedule`
- `d_industry_aggregate`

（`optional_target_logical_table` 另允许 `d_event_party_detail`、`d_company_metric_daily`。）

- **FAIL** 若主表非法。

### 3.6 layer ↔ table 映射一致性 — `R008`

| source_layer | 必须 target_logical_table |
|--------------|---------------------------|
| company_event | d_company_event |
| company_metric_daily | d_company_metric_daily |
| company_metric_periodic | d_company_metric_periodic |
| disclosure_schedule | d_disclosure_schedule |
| industry_aggregate | d_industry_aggregate |

- **FAIL** 若错配。

### 3.7 records_path — `R009` / `R010`

| rule_id | 检查 |
|---------|------|
| R009 | 除 `disclosure_schedule` 外，主 path 应为 `data.records` 或 `marketList`（abnormal_trading） |
| R010 | `disclosure_schedule` 应为 `prbookinfos` |

- **WARN** 若与 Phase 2 观测不一致。

### 3.8 supported_modes — `R011`–`R014`

| rule_id | source | 检查 |
|---------|--------|------|
| R011 | shareholder_change | 必须含 `type=inc` 与 `type=desc` 模式 |
| R012 | shareholder_change | 不得含 `type=dec` 或 `type: dec` |
| R013 | executive_shareholding | 必须含 `timeMark` 与 `varyType` 参数的模式 |
| R014 | margin_trading | 必须含 `detailList_default` 主模式；若含 market 模式须标 `auxiliary` / `observation` |

- **FAIL** 对 R011–R012；**WARN** 对 R013–R014 缺 notes。

### 3.9 field groups — `R015` / `R016`

| rule_id | 检查 |
|---------|------|
| R015 | `fields.confirmed` / `raw_only` / `uncertain` 的 `raw` 字段名跨组不重复 |
| R016 | `mapping.raw_record_required` 必须为 `true` |

- **FAIL** 若 R016 为 false；**WARN** 若 R015 重复。

### 3.10 company_code_available — `R017` / `R018`

| rule_id | 检查 |
|---------|------|
| R017 | `fund_industry_allocation` 必须为 `false` |
| R018 | 其他 9 个 source 应为 `true` |

- **FAIL** 若违反。

### 3.11 覆盖范围 — `R019`

- Registry 必须恰好包含 Phase 2 十个 `testing_stable_sample` source_id。
- **FAIL** 若缺源或多出未记录源（相对期望列表）。

### 3.12 recommended_status — `R020`

- 十个 source 的 `status.recommended_status` 应为 `testing_stable_sample`。
- **WARN** 若其他合法值（设计阶段允许文档化例外）。

### 3.13 JSON Schema 文件存在 — `R021`

- 每个 `target_logical_table` 应对应 `schemas/d_class/<table>.schema.json` 存在。
- **FAIL** 若缺失。

### 3.14 api.method — `R022`

- `api.method` 应为 `POST` 或 `GET`。
- **FAIL** 若非法。

### 3.15 fund_industry_allocation 隔离 — `R023`

- `mapping.exclude_from_schemas` 应包含 `d_company_event`（若字段存在）。
- **WARN** 若缺失。

**规则合计：23 条（R001–R023）。**

---

## 4. Lint 输出

### 4.1 单条 finding 格式

```
<VERDICT>  <rule_id>  <source_id|->  <severity>  <message>  [suggested_fix=...]
```

| 字段 | 说明 |
|------|------|
| VERDICT | `PASS`（仅汇总行）/ 隐含于 FAIL·WARN·INFO 前缀 |
| rule_id | R001–R023 |
| source_id | 相关 source；全局规则用 `-` |
| severity | FAIL / WARN / INFO |
| message | 人类可读说明 |
| suggested_fix | 可选修复建议 |

### 4.2 汇总行

```
SUMMARY  sources=N  fail=F  warn=W  info=I  result=PASS|FAIL
```

- **result=FAIL** 若任一 `severity=FAIL`。
- `--strict` 时 WARN 也计为失败退出码。

### 4.3 未来扩展（当前不写文件）

- `outputs/validation/cninfo_d_class_registry_lint.csv`
- `outputs/validation/cninfo_d_class_registry_lint_summary.md`

**当前脚本默认只 stdout，不修改任何文件。**

---

## 5. severity 设计

| severity | 含义 | 示例 |
|----------|------|------|
| **FAIL** | 明显错误，必须修复 | 重复 source_id、verified=true、layer/table 错配 |
| **WARN** | 不一致或文档缺口 | 缺 exclude_from_schemas、字段跨组重复 |
| **INFO** | 可选改进 | 缺 notes 字段、optional_target 未文档化 |

---

## 6. 脚本草案

### 6.1 命令

```bash
python lab/lint_cninfo_d_class_registry.py
python lab/lint_cninfo_d_class_registry.py --registry config/cninfo_d_class_source_registry_draft.yaml
python lab/lint_cninfo_d_class_registry.py --schemas-dir schemas/d_class --strict
```

### 6.2 参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `--registry` | `config/cninfo_d_class_source_registry_draft.yaml` | Registry YAML 路径 |
| `--schemas-dir` | `schemas/d_class` | JSON Schema 目录 |
| `--strict` | off | WARN 也导致 exit code 1 |

### 6.3 行为边界

- 只读本地 YAML / JSON；
- **不**请求 CNINFO；
- **不**写文件；
- **不**连接数据库；
- exit `0` = 无 FAIL（非 strict 时 WARN 可存在）；exit `1` = 有 FAIL 或 strict 下有 WARN。

### 6.4 与 schema validation 关系

| 阶段 | 工具 |
|------|------|
| 1（当前） | registry lint — YAML 内部 + 与 schema 文件存在性 |
| 2（计划） | fixture + JSON Schema validate — 见 validation plan |

---

## 7. 边界

- 不写 **verified**
- 不入库、不写 migration
- lint 通过 **不等于** 生产就绪

---

## 8. 产物索引

| 文件 | 说明 |
|------|------|
| [cninfo_d_class_schema_validation_plan.md](cninfo_d_class_schema_validation_plan.md) | 下一阶段 fixture 验证 |
| [cninfo_d_class_json_schema_draft_notes.md](cninfo_d_class_json_schema_draft_notes.md) | Schema 说明 |
