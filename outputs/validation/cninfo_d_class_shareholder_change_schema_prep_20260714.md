# CNINFO D 类 shareholder_change — Schema Prep（Offline）

_生成时间：2026-07-14_

> **性质：** offline schema + ownership-event model preparation only · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 claim approved** · **无 commit** · **无 push**
>
> **边界：** `READY_FOR_APPROVAL` ≠ **approved** · **disclosure ≠ structured capture** · **不是 verified** · **不是 production_ready**
>
> **前置：** [cninfo_d_class_shareholder_change_offline_prep_refresh_20260714.md](cninfo_d_class_shareholder_change_offline_prep_refresh_20260714.md)（artifact inventory + checklist）· 本包在其之上增加 **schema/event-model delta**，不重复清点。

---

## 1. Delta vs Prep Refresh

| 维度 | prep refresh（D-D1-run2） | 本包（D-GEN-20260714-03） |
|------|---------------------------|---------------------------|
| 产出 | gate 重述 · artifact 清单 · H1–H7 checklist | **三层字段映射** · **ownership-event 分类** · **first-slice 字段契约** |
| 结构化建模 | 引用 registry / phase1 freeze | **显式 delta**：raw → `d_company_event` → `market_event`+payload |
| event types | 仅提及 `type=inc` sketch | **increase/decrease 子类型** · first-slice 仅 inc · desc 标 blocked |
| 证据边界 | 政策保留 | **字段级 lineage 规则** · disclosure 字段 **不得** 进入 structured payload |
| 机器可读 | checklist CSV（item/status） | **[event_model CSV](cninfo_d_class_shareholder_change_event_model_20260714.csv)**（field/event 粒度） |

---

## 2. Current Gate（unchanged）

```text
d_class_shareholder_change_next_component_planning_gate = READY_FOR_APPROVAL
approval_queue_id = AQ-D-SC
approval_queue_status = WAITING_APPROVAL
shareholder_change_component_approved = false
schema_prep_blocked_until_level2 = true
```

**本包不升级 gate。** 所有 schema/event-model 条目在人工 Level-2 短语落档前均为 **draft / blocked for implementation**。

---

## 3. Ownership-Event Model（proposed）

### 3.1 在 D 轨 ownership/capital 链中的位置

```text
full-market shareholder/capital coverage
    │
    ├── equity_pledge          [closed · 85abad0 · no reopen]
    ├── restricted_shares_unlock [closed · aa087b5 · no reopen]
    ├── block_trade            [closed · 403472d · no reopen]
    ├── shareholder_change     [THIS · primary next · schema prep]
    └── executive_shareholding [runner-up · partial schema]
```

`shareholder_change` 建模为 **company-level ownership transfer event**（股东增减持），与质押/解禁/大宗正交；**不**与 `executive_shareholding`（高管持股变动）合并 event_type。

### 3.2 Event type 分类

| event_type | event_subtype | query_mode | first-slice | 说明 |
|------------|---------------|------------|-------------|------|
| `shareholder_change` | `increase` | `type_inc` | **yes** | `type=inc` · UI「增持明细」 |
| `shareholder_change` | `decrease` | `type_desc` | **no** | `type=desc`（**不是** `dec`）· first-slice 单模式 inc · 留待扩展 |

**event_subtype 来源：** `query_params.type` → registry `event_subtype_mode: query_param_type`（inc→increase · desc→decrease）。**不得**从公告标题或 disclosure 文本推断 subtype。

### 3.3 逻辑表与信封

| 层 | 目标 | 说明 |
|----|------|------|
| CNINFO raw row | `data.records[]` | 8 字段结构（inc/desc 同形） |
| 逻辑表 | `d_company_event` | [schemas/d_class/d_company_event.schema.json](../../schemas/d_class/d_company_event.schema.json) |
| Phase1 信封 | `market_event` + `shareholder_change` payload | [cninfo_d_class_event_object_schema.md](../../plans/cninfo_d_class_event_object_schema.md) |

**record_kind：** `event`（非 metric_daily · 非 schedule）。

---

## 4. Three-Layer Field Mapping（proposed）

### 4.1 CNINFO raw → `d_company_event`（registry confirmed · mapping_confidence=high）

| raw | standard (registry) | d_company_event property | unit / notes |
|-----|---------------------|--------------------------|--------------|
| SECCODE | company_code | `company_code` | 公司过滤键 |
| SECNAME | company_name | `company_name` | recommended |
| DECLAREDATE | announcement_date | `announcement_date` | 公告日 |
| VARYDATE | share_change_date | `event_date` | **主事件日** · 对应 payload `change_date` |
| F002V | shareholder_name | `actor_name` | 股东名称 · event_id 组分 |
| F004N | share_change_amount | `primary_amount` | `primary_amount_unit=shares` |
| F005N | share_change_ratio_percent | `primary_ratio` | `primary_ratio_unit=percent` |
| F007V | share_change_price | `primary_price` | optional · `yuan_per_share` · desc 模式可能为空/区间 |

**固定信封字段（mapper 已实现 · 离线引用）：**

- `event_type` = `shareholder_change`
- `event_subtype` = `increase` | `decrease`（由 query `type` 派生）
- `event_id` = hash(`source_id`, `query_mode`, `company_code`, `event_date`, `F002V`)
- `raw_record_json` / `raw_record_hash` = **必填**（lineage 保留）
- `query_params` = 含 `type` · `tdate`（first-slice 共享 `2026-07-03`）

参考实现（**不执行**）：`lab/cninfo_d_class_mappers.py` → `_map_shareholder_change`。

### 4.2 `d_company_event` → Phase1 `market_event` + component payload

| market_event 字段 | shareholder_change payload 字段 | first-slice required | 来源 |
|-------------------|--------------------------------|----------------------|------|
| `event_id` | — | yes | 逻辑主键 |
| `company_code` | `company_code` | yes | SECCODE |
| `event_type` | — | yes | `shareholder_change` |
| `event_time` | `change_date` | yes | VARYDATE |
| `source_endpoint` | `source_endpoint` | recommended | registry API url |
| `source_record_id` | — | yes | raw 行稳定 hash |
| `event_status` | — | yes | `captured` · `empty_but_valid` · … |
| `quality_status` | `quality_status` | yes | pass / caveat / needs_review |
| `lineage.registry_source_id` | — | yes | `shareholder_change` |
| `lineage.query_mode` | — | yes | `type_inc`（first-slice） |
| `lineage.query_params` | `change_type` | yes | `change_type` = query `type` 值 |
| — | `shareholder_name` | yes | F002V |
| — | `change_amount` | yes | F004N |
| — | `change_ratio` | recommended | F005N |
| — | `company_name` | recommended | SECNAME |

**一致性规则（Phase1）：** `event_time` ≡ `change_date` · 信封与 payload `company_code` / `quality_status` 必须一致（见 event object schema §5）。

### 4.3 phase1_freeze_v1 对齐

registry `phase1_freeze_v1` / [field_catalog](../../outputs/validation/cninfo_d_class_phase1_freeze_v1_field_catalog.csv) 已冻结 shareholder_change 必填集；本 prep **不修改 freeze**，仅文档化 first-slice 子集：

| field_ref | freeze tier | first-slice |
|-----------|-------------|-------------|
| company_code | required | yes |
| shareholder_name | required | yes |
| change_type | required | yes（固定 `inc`） |
| change_amount | required | yes（found 时） |
| change_date | required | yes（found 时） |
| quality_status | required | yes |
| change_ratio | recommended | yes（nullable_if_missing） |
| company_name | recommended | yes |
| source_endpoint | recommended | yes |

**empty_but_valid 案例：** DSC005 等零行时 **无** component payload 行 · 仅 envelope `event_status=empty_but_valid` · **不得** 伪造 shareholder_name/change_amount。

---

## 5. First-Slice Query Contract（sketch · blocked until approval）

| 参数 | first-slice 值 | 状态 |
|------|----------------|------|
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` | draft（registry confirmed） |
| method | POST · params in query | draft |
| `type` | `inc` | draft |
| `tdate` | `2026-07-03` | draft（离线文档化 · **非 CNINFO 探测**） |
| records_path | `data.records` | draft |
| company filter | `SECCODE` == universe `company_code` | draft |

**per-case 预期：** 1 请求/案 · total cap ≤ 20 · 见 first-slice plan draft。

---

## 6. Retrieval / Quality Semantics（first-slice）

| 语义 | envelope `event_status` | 合法场景 |
|------|-------------------------|----------|
| 命中 ≥1 行 | `captured` | DSC001–004 found |
| 零行 · 稀疏日 | `empty_but_valid` | DSC005 控制案例 · RSU/equity_pledge 教训 |
| 映射不确定 | `captured` + `quality_status=needs_review` | DSC004 混排 |
| HTTP/结构失败 | `failed` | 非 first-slice 默认期望 |

**禁止：** sole `captured_normal_candidate` 绑定单一 anchor（DBT002）· fragile 单标签混排（DEP004）。

---

## 7. Evidence Boundary（mandatory）

```text
disclosure_evidence  ≠  captured_structured_evidence
separate_disclosure_lineage_only  不得  promote  为  captured_normal
```

| 层级 | shareholder_change 适用 |
|------|-------------------------|
| retrieval evidence | endpoint 返回公司级行（或合法空列表） |
| disclosure evidence | 公告 PDF/人工复核 · **不** 填入 F002V/F004N 等 structured 字段 |
| structured component evidence | 仅当 pipeline 捕获 raw 行并保留 `raw_record_json` |

**DLC006R / 301259：** known-event closed · disclosure Option A+C **不得** 升级为 structured capture · 301259 **永久排除** primary universe。

**DLC006（000550）：** Phase1 先例口径 · 独立 DSC001 case_id · **不** 等同 DLC006R 代理。

---

## 8. Blocked Until Level-2 Approval

在人工短语 **「I approve D-class shareholder_change as the next Era D component.」** 落档前，以下 **全部 blocked**（本包仅 draft 建模）：

| # | blocked 项 | 原因 |
|---|-----------|------|
| B1 | 本 schema prep 的 **implementation binding**（runner · mapper live · schema JSON amend） | 无组件批准 |
| B2 | `type_desc` / decrease 模式 first-slice 启用 | first-slice 单 inc 政策 |
| B3 | formal universe 锁定 · first-slice approval package | 须先 H1 |
| B4 | CNINFO 探测 / dry-run / live | 无 live approval |
| B5 | `d_company_event.schema.json` 变更提交 | 无 commit 授权 |
| B6 | disclosure → structured 字段回填 | evidence boundary |
| B7 | B-class `event_document_link` · `lineage_status=linked` | Phase1 不实现 |
| B8 | verified / production_ready / testing_stable_sample claim | governance 红线 |

**短语落档后仍 blocked：** live · CNINFO · runner execute · commit · push · verified。

---

## 9. Artifacts Produced by This Package

| 路径 | 说明 |
|------|------|
| 本文件 | schema prep · 三层映射 · ownership-event 分类 · boundary |
| [cninfo_d_class_shareholder_change_event_model_20260714.csv](cninfo_d_class_shareholder_change_event_model_20260714.csv) | event/field 粒度 · draft/blocked 状态 |

**不修改：** registry yaml · mappers · runners · tests · PROJECT_CONTROL。

---

## 10. Safety Zeros

| 项 | 本包 |
|----|------|
| CNINFO calls | **0** |
| live / runner | **no** |
| claim approved | **no** |
| gate upgrade | **no**（维持 READY_FOR_APPROVAL / WAITING_APPROVAL） |
| commit / push | **no** |
| disclosure → structured promotion | **no** |

---

## 11. Summary Block

```text
phase = shareholder_change_schema_prep_20260714
delta = three_layer_field_mapping + ownership_event_taxonomy + event_model_csv
current_gate = READY_FOR_APPROVAL
approval_queue = AQ-D-SC · WAITING_APPROVAL
schema_prep_blocked_until_level2 = true
target_logical_table = d_company_event
event_types_proposed = shareholder_change.increase (first-slice) · shareholder_change.decrease (deferred)
cninfo_calls = 0
disclosure_equals_structured = false
```
