# CNINFO D 类 Source Registry 设计草案

_最后更新：2026-07-05_

> **性质：** 设计草案，不是生产数据库。  
> **前置：** [cninfo_table_sources_phase2_current_final_summary.md](../outputs/validation/cninfo_table_sources_phase2_current_final_summary.md)  
> **关联：** [cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md) · [cninfo_d_class_ingestion_status_model.md](cninfo_d_class_ingestion_status_model.md)  
> **配置来源：** [config/cninfo_table_sources.yaml](../config/cninfo_table_sources.yaml)

---

## 1. 设计目标

**Era C Phase 2** 已证明 CNINFO 存在 **10 个** `testing_stable_sample` 的 D 类固定表格 JSON source（blocked=0、schema_changed=0、verified=0）。

Phase 3 设计阶段需要一份 **Source Registry** 来统一管理：

| 管理维度 | 说明 |
|----------|------|
| source 类型与分层 | company event / metric / schedule / industry aggregate |
| 技术入口 | api_url、method、params、records_path |
| 查询模式 | inc/desc、timeMark/varyType 等多参数组合 |
| 字段语义 | UI confirmed vs candidate vs internal |
| 稳定性与边界 | 小样本稳定性结论、权限、空日行为 |
| 验证血缘 | 指向 validation CSV / summary 产物 |

Registry 是 **逻辑元数据层**，未来可映射为 `d_source_registry` 逻辑表（见 schema draft），**当前不入库、不写 migration**。

---

## 2. Source 分层

### 2.1 company-level（8）

| source_id | 中文名称 |
|-----------|----------|
| restricted_shares_unlock | 限售解禁 |
| block_trade | 大宗交易 |
| margin_trading | 融资融券 |
| abnormal_trading | 公开信息 / 异常交易 |
| equity_pledge | 股权质押 |
| shareholder_change | 股东增减持 |
| executive_shareholding | 高管持股 |
| shareholder_data | 股东数据 |

### 2.2 schedule / disclosure（1）

| source_id | 中文名称 |
|-----------|----------|
| disclosure_schedule | 预约披露 |

### 2.3 industry-level aggregate（1）

| source_id | 中文名称 |
|-----------|----------|
| fund_industry_allocation | 基金行业配置 |

**重要：** `fund_industry_allocation` **不进入** company event schema；无 `SECCODE`，按行业编码聚合。

### 2.4 config candidate（未纳入 registry 主表）

| source_id | 状态 |
|-----------|------|
| ipo_query | candidate，api_url 待 DevTools |
| szse_calendar | candidate，api_url 待 DevTools |

---

## 3. Registry 核心字段

以下为 **逻辑 registry 记录** 建议字段（YAML / JSON / 未来 DB 均可承载）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `source_id` | string | 唯一标识，与 config 一致 |
| `source_name` | string | 中文展示名 |
| `source_layer` | enum | 见 §4 |
| `source_category` | enum | 见 §5 |
| `api_url` | string | 主 endpoint |
| `page_url` | string | UI 页 / Referer |
| `method` | string | GET / POST |
| `params_location` | enum | `none` / `query` / `form` |
| `default_params` | object | 默认查询参数模板 |
| `supported_modes` | array | 多模式参数组合（见 §6） |
| `records_path` | string | JSON records 路径，如 `data.records`、`prbookinfos` |
| `expected_fields` | array | 配置层期望 raw 字段列表 |
| `confirmed_fields` | array | UI confirmed 字段子集 |
| `candidate_fields` | array | 语义候选、待确认 |
| `not_visible_fields` | array | 接口有、UI 无列 |
| `date_param_type` | enum | `tdate` / `rdate` / `sectionTime` / `sdate_edate` / `none` / `composite` |
| `sample_status` | enum | 最近一次小样本验证结论 |
| `stability_status` | enum | 多日期/多参数稳定性结论 |
| `recommended_status` | enum | 综合推荐状态（见 §8） |
| `requires_login` | bool | 是否需登录 |
| `requires_captcha` | bool | 是否需验证码 |
| `requires_paid_permission` | bool | 是否需付费/商业权限 |
| `field_semantics_confidence` | enum | `high` / `medium` / `low` / `mixed` |
| `last_validated_at` | datetime | 最近一次 live 验证时间（ISO） |
| `validation_artifacts` | array | 关联 CSV / MD 路径 |
| `notes` | string | 人工备注、caveat |

---

## 4. source_layer 定义

`source_layer` 描述 **数据粒度与业务角色**，决定 schema 映射目标表。

| 值 | 含义 | 典型 source |
|----|------|-------------|
| `company_event` | 公司级离散事件（含嵌套 detail） | restricted_shares_unlock, block_trade, abnormal_trading, equity_pledge, shareholder_change, executive_shareholding |
| `company_metric_daily` | 公司 × 交易日指标 | margin_trading |
| `company_metric_periodic` | 公司 × 报告期截面指标 | shareholder_data |
| `disclosure_schedule` | 披露日程 / 预约 | disclosure_schedule |
| `market_behavior` | 保留枚举；当前 10 源中 abnormal_trading 归入 `company_event`（含嵌套营业部行为） | — |
| `industry_aggregate` | 行业级聚合，无 company_code | fund_industry_allocation |

### 10 源 source_layer 分配

| source_id | source_layer |
|-----------|--------------|
| disclosure_schedule | disclosure_schedule |
| restricted_shares_unlock | company_event |
| block_trade | company_event |
| margin_trading | company_metric_daily |
| abnormal_trading | company_event |
| equity_pledge | company_event |
| shareholder_change | company_event |
| executive_shareholding | company_event |
| shareholder_data | company_metric_periodic |
| fund_industry_allocation | industry_aggregate |

---

## 5. source_category 定义

`source_category` 为 **细分类标签**，用于 UI、采集任务分组、event_type 映射。

| source_category | source_id |
|-----------------|-----------|
| report_schedule | disclosure_schedule |
| share_unlock | restricted_shares_unlock |
| block_trade | block_trade |
| margin_trading | margin_trading |
| abnormal_trading | abnormal_trading |
| equity_pledge | equity_pledge |
| shareholder_change | shareholder_change |
| executive_shareholding | executive_shareholding |
| shareholder_structure | shareholder_data |
| fund_industry_allocation | fund_industry_allocation |

---

## 6. supported_modes 设计

部分 source **同一 endpoint** 通过 query 参数切换语义或数据子集。Registry 应显式记录 `supported_modes`，避免采集任务误用参数。

### shareholder_change

| mode_id | params | 说明 |
|---------|--------|------|
| `inc` | `type=inc`, `tdate=<YYYY-MM-DD>` | 增持明细；observed total 随日变化 |
| `desc` | `type=desc` | 减持明细；**可不传** `tdate` |
| `desc_with_tdate` | `type=desc`, `tdate=<YYYY-MM-DD>` | 与 `desc` 无 tdate 样本行数一致（16），结构相同 |

**注意：** 观测参数为 `type=desc`，**不是** `type=dec`。endpoint path：`/shareholeder/detail`（拼写保留）。

### executive_shareholding

| mode_id | params | 说明 |
|---------|--------|------|
| `oneMonth_varyType_b` | `timeMark=oneMonth`, `varyType=b` | UI「增持」筛选项；默认验证模式 |
| `threeMonth_varyType_b` | `timeMark=threeMonth`, `varyType=b` | 更长窗口；行数更多 |
| `oneMonth_varyType_s` | `timeMark=oneMonth`, `varyType=s` | 接口支持；varyType 语义待 UI 确认 |

页面另有 **高管持股变动汇总** tab，**不是**当前主 source；未来可注册为 `executive_shareholding_summary`（candidate）。

### margin_trading

| mode_id | params | 角色 |
|---------|--------|------|
| `detailList_default` | POST empty body，无 query | **主 source**；公司级日度明细 |
| `market_summary` | `GET/POST .../marginTrading/market?tdate=` | **附属**；市场汇总；稳定性复测 HTTP 500；**不作主 source** |

主接口 **不显式传 date**（`params_location=none`）；稳定性判断看两次默认请求结构是否一致。

### 其他 source（单模式为主）

| source_id | date_param_type | default_params 要点 |
|-----------|-----------------|----------------------|
| disclosure_schedule | sectionTime | `sectionTime`, `market=szsh`, `pagesize=20` |
| restricted_shares_unlock | tdate | `tdate=YYYY-MM-DD` |
| block_trade | tdate | `tdate=YYYY-MM-DD` |
| abnormal_trading | sdate_edate | `sdate=edate`, `page=1`, `rows=30` |
| equity_pledge | tdate | `tdate=YYYY-MM-DD` |
| fund_industry_allocation | none / rdate | 默认无参；可选 `rdate=YYYYMMDD` |
| shareholder_data | rdate | `rdate=YYYYMMDD` |

---

## 7. 字段语义状态

不能把 config `expected_fields` 全部当作生产可用字段。Registry 应对每个 raw field 标注语义状态：

| 状态 | 含义 | 可用于标准 schema 映射 |
|------|------|------------------------|
| `ui_confirmed` | 人工 UI 表头对照通过 | 是（仍非 verified） |
| `candidate` | 有候选语义，待 UI 或算术校验 | 仅作候选列 |
| `internal_text` | 接口返回文本，UI 无独立列 | 保留 raw JSON，不映射展示列 |
| `not_visible_on_ui` | 接口有字段，明细 UI 无列 | 保留 raw，谨慎映射 |
| `uncertain` | 多义或样本不足 | 不映射为标准字段 |

**原则：** `confirmed_fields` ⊆ `expected_fields`；生产映射只使用 `ui_confirmed` + 高置信 `candidate`（需人工复核）。

---

## 8. 稳定性状态

### recommended_status 枚举

| 值 | 含义 |
|----|------|
| `candidate` | endpoint 未确认或仅 page 可达 |
| `testing` | 小样本 `sample_ok`，未做多参数稳定性 |
| `testing_stable_sample` | 多日期/多参数稳定性通过 |
| `testing_partial` | 部分用例失败或 field set 不一致 |
| `testing_needs_more_review` | schema_changed 或混合错误需人工复核 |
| `blocked` | 登录/验证码/付费 |
| `deprecated` | CNINFO 改版或 endpoint 废弃 |
| ~~`verified`~~ | **禁止使用**（Era C 红线） |

### 当前 10 源快照

| source_id | sample_status | stability_status | recommended_status |
|-----------|---------------|------------------|-------------------|
| disclosure_schedule | sample_ok | testing_stable_sample | testing_stable_sample |
| restricted_shares_unlock | sample_ok | testing_stable_sample | testing_stable_sample |
| block_trade | sample_ok | testing_stable_sample | testing_stable_sample |
| margin_trading | sample_ok | testing_stable_sample | testing_stable_sample |
| abnormal_trading | sample_ok | testing_stable_sample | testing_stable_sample |
| equity_pledge | sample_ok | testing_stable_sample | testing_stable_sample |
| shareholder_change | sample_ok | testing_stable_sample | testing_stable_sample |
| executive_shareholding | sample_ok | testing_stable_sample | testing_stable_sample |
| fund_industry_allocation | sample_ok | testing_stable_sample | testing_stable_sample |
| shareholder_data | sample_ok | testing_stable_sample | testing_stable_sample |

---

## 9. Registry 示例

### 9.1 block_trade

```yaml
source_id: block_trade
source_name: 大宗交易
source_layer: company_event
source_category: block_trade
api_url: https://www.cninfo.com.cn/data20/ints/statistics
page_url: https://www.cninfo.com.cn/new/commonUrl?url=data/dzjy-zjlx
method: POST
params_location: query
default_params:
  tdate: "2026-07-03"
supported_modes:
  - mode_id: tdate_daily
    params: { tdate: "<YYYY-MM-DD>" }
records_path: data.records
expected_fields: [SECCODE, SECNAME, TRADEDATE, F001N, F002N, F003N, F004N]
confirmed_fields: [F001N, F002N, F003N, F004N]
candidate_fields: []
not_visible_fields: []
date_param_type: tdate
sample_status: sample_ok
stability_status: testing_stable_sample
recommended_status: testing_stable_sample
requires_login: false
requires_captcha: false
requires_paid_permission: false
field_semantics_confidence: high
last_validated_at: "2026-07-05"
validation_artifacts:
  - outputs/validation/cninfo_table_sources_multidate_stability.csv
  - outputs/validation/cninfo_table_field_semantics_ui_check_summary.md
notes: >
  空交易日返回 empty_but_valid_response（records=0）不等于失败。
  F001N-F004N 单位已 UI 确认；可算术校验 F003N/F002N≈F004N。
```

### 9.2 shareholder_change

```yaml
source_id: shareholder_change
source_name: 股东增减持
source_layer: company_event
source_category: shareholder_change
api_url: https://www.cninfo.com.cn/data20/shareholeder/detail
page_url: https://www.cninfo.com.cn/new/commonUrl?url=data/person-stock-data-tables
method: POST
params_location: query
default_params:
  type: inc
  tdate: "2026-07-03"
supported_modes:
  - mode_id: inc
    params: { type: inc, tdate: "<YYYY-MM-DD>" }
  - mode_id: desc
    params: { type: desc }
  - mode_id: desc_with_tdate
    params: { type: desc, tdate: "<YYYY-MM-DD>" }
records_path: data.records
expected_fields: [DECLAREDATE, SECCODE, SECNAME, VARYDATE, F002V, F004N, F005N, F007V]
confirmed_fields: [DECLAREDATE, SECCODE, SECNAME, VARYDATE, F002V, F004N, F005N, F007V]
candidate_fields: []
not_visible_fields: []
date_param_type: composite
sample_status: sample_ok
stability_status: testing_stable_sample
recommended_status: testing_stable_sample
requires_login: false
requires_captcha: false
requires_paid_permission: false
field_semantics_confidence: high
last_validated_at: "2026-07-05"
validation_artifacts:
  - outputs/validation/cninfo_table_sources_priority2_stability.csv
  - outputs/validation/cninfo_table_field_semantics_priority2.csv
notes: >
  type=desc 不是 type=dec。inc/desc 共享 8 字段结构，UI 标签不同（增持日期 vs 减持日期）。
```

### 9.3 fund_industry_allocation

```yaml
source_id: fund_industry_allocation
source_name: 基金行业配置
source_layer: industry_aggregate
source_category: fund_industry_allocation
api_url: https://www.cninfo.com.cn/data20/fund/industry
page_url: https://www.cninfo.com.cn/new/commonUrl?url=data/person-stock-data-tables
method: POST
params_location: none
default_params: {}
supported_modes:
  - mode_id: default
    params: {}
  - mode_id: rdate
    params: { rdate: "<YYYYMMDD>" }
records_path: data.records
expected_fields: [F001V, F002V, ENDDATE, F003N, F004N, F005N]
confirmed_fields: [F001V, F002V, ENDDATE, F003N, F004N, F005N]
candidate_fields: []
not_visible_fields: []
date_param_type: none
sample_status: sample_ok
stability_status: testing_stable_sample
recommended_status: testing_stable_sample
requires_login: false
requires_captcha: false
requires_paid_permission: false
field_semantics_confidence: high
last_validated_at: "2026-07-05"
validation_artifacts:
  - outputs/validation/cninfo_table_sources_priority2_stability.csv
  - outputs/validation/cninfo_table_field_semantics_priority2.csv
notes: >
  industry-level aggregate；无 SECCODE。勿归入 company event schema。
  rdate=20251231 可能 empty_but_valid_response。
```

---

## 10. 后续使用方式

Registry 设计完成后可用于：

| 用途 | 说明 |
|------|------|
| **控制采集任务** | 按 `source_layer` + `supported_modes` 生成 fetch plan，避免错误参数 |
| **生成 validation plan** | 新 source 入网前对照 registry 字段模板做稳定性用例 |
| **决定 schema 映射** | `source_layer` → 逻辑表（见 schema draft §11） |
| **字段漂移检测** | 对比 `expected_fields` / `confirmed_fields` 与 live 响应 key set |
| **source lineage** | `validation_artifacts` + `last_validated_at` 追溯验证代际 |
| **与 A 类联动** | `disclosure_schedule.orgId` + `company_code` 桥接报告 PDF timeline |

**当前阶段：** 仅维护 plans 文档与 config YAML；**不**实例化 registry 数据库。

---

## 11. 边界

- 不入库；不写 migration
- 不写 **verified**
- Registry 内容随新 discovery 增量更新；`ipo_query` / `szse_calendar` 验证通过后再入主表
