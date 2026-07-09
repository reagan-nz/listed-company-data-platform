# CNINFO D 类 Phase 1 Freeze v1 Implementation Plan

_最后更新：2026-07-09_

> **性质：** 未来实施计划 only；**须人工 signoff 后执行**；本文件创建时 **NOT STARTED**。  
> **前置批准包：** [approval checklist](../outputs/validation/cninfo_d_class_phase1_schema_freeze_approval_checklist.md) · [approval summary](../outputs/validation/cninfo_d_class_phase1_schema_freeze_approval_summary.md)  
> **Gate 前置：** `d_class_phase1_schema_freeze_signoff_gate = READY_FOR_IMPLEMENTATION`

---

## 1. Purpose

将已 signoff 的 D-class Phase 1 schema（7 组件 · 49 required fields · market_event 信封）落地为可离线验证的 artifacts：

- freeze catalog CSV
- registry draft 注释/字段对齐修订
- 扩全 7 组件 phase1 fixtures
- ready-case benchmark 骨架

**不包含：**

- live endpoint validation
- harvest / market data ingestion
- PDF / DB / MinIO / RAG
- verified / testing_stable_sample 升级
- A/B/C-class 输出修改

---

## 2. Signoff Baseline（不再重新辩论）

### Frozen components

margin_trading · block_trade · restricted_shares_unlock · disclosure_schedule · equity_pledge · shareholder_change · executive_shareholding

### Frozen envelope

`event_id` · `company_code` · `event_type` · `event_time` · `source_endpoint` · `source_record_id` · `event_status` · `quality_status` · `lineage`（recommended）

### Future（Phase 1 不实现）

buyer · seller · pledge_status

---

## 3. Implementation Steps（严格顺序 · signoff 后）

### Step 1 — Freeze catalog

**产物：** `outputs/validation/cninfo_d_class_phase1_freeze_v1_field_catalog.csv`

| 列 | 说明 |
|----|------|
| field_name | 产品字段名 |
| component | 7 组件 + market_event |
| required_level | required / recommended / future / removed |
| registry_raw_field | 对应 F00xN 或 registry mapping |
| target_logical_table | d_company_event 等 |
| notes | caveat |

来源：从 [field decision matrix](../outputs/validation/cninfo_d_class_phase1_field_decision_matrix.csv) 派生；**signoff 后生成**。

### Step 2 — Update registry draft（注释级对齐）

**文件：** `config/cninfo_d_class_source_registry_draft.yaml`

| 动作 | source_id | 内容 |
|------|-----------|------|
| annotate | 7 源 | 补 `phase1_freeze_v1: true` 注释块 |
| align | margin_trading | 产品字段 ↔ confirmed fields 对照注释 |
| align | block_trade | 标注 buyer/seller = phase1_gap |
| align | equity_pledge | 标注 pledge_status = deferred |
| keep | recommended_status | **不升级** testing_stable_sample |

**红线：** 不写 verified；不触发 live 重验。

### Step 3 — Expand fixtures

**目录：** `fixtures/d_class/phase1/`

| 文件 | 状态 | 动作 |
|------|------|------|
| margin_trading_fixture.json | 已有 | 可选补 negative case |
| block_trade_fixture.json | 已有 | 保持 buyer/seller=null |
| restricted_unlock_fixture.json | 已有 | — |
| disclosure_schedule_fixture.json | **新增** | 合成示例 |
| equity_pledge_fixture.json | **新增** | 合成示例 |
| shareholder_change_fixture.json | **新增** | inc + desc 各一（可选） |
| executive_shareholding_fixture.json | **新增** | 合成示例 |
| empty_but_valid_fixture.json | **新增** | 合法空态示例 |

**无 CNINFO**；代码 `999xxx` 合成。

### Step 4 — Extend offline lint

**脚本：** `lab/lint_cninfo_d_class_phase1_schema.py`（扩规则）

新增规则草案：

- R-D-P1-011：7 组件 fixture 均存在
- R-D-P1-012：empty_but_valid fixture 符合 quality policy
- R-D-P1-013：freeze catalog 与 matrix 行数一致

### Step 5 — Ready-case benchmark

**产物：**

| 文件 | 说明 |
|------|------|
| `outputs/validation/cninfo_d_class_phase1_ready_case_benchmark.csv` | DC001–DC007 骨架 |
| `fixtures/d_class/phase1/ready_cases/` | 离线 expected 字段清单 |

| case_id | component | 类型 |
|---------|-----------|------|
| DC001 | margin_trading | known synthetic row |
| DC002 | block_trade | known synthetic row |
| DC003 | restricted_shares_unlock | known synthetic row |
| DC004 | disclosure_schedule | schedule row |
| DC005 | shareholder_change | inc mode |
| DC006 | executive_shareholding | varyType row |
| DC007 | equity_pledge | pledge row |

**不 live 执行**；benchmark runner 留待后续回合。

### Step 6 — Implementation summary

**产物：** `outputs/validation/cninfo_d_class_phase1_freeze_v1_implementation_summary.md`

记录 catalog · registry diff · fixture count · lint pass · gate。

---

## 4. Explicitly Out of Scope

| 项 | 原因 |
|----|------|
| live endpoint validation | 须单独批准包 |
| harvest runner | 须 harvest architecture + 用户批准 |
| market data ingestion | 全市场采集不在 Phase 1 freeze v1 |
| PDF / document parsing | D-class 固定表 JSON only |
| DB / MinIO | Era C 红线 |
| RAG / vector | 非 D-class Phase 1 |
| C-class identity merge | 仅 `company_code` 链接 |

---

## 5. Success Criteria（implementation 完成时）

| gate | 条件 |
|------|------|
| `d_class_phase1_freeze_v1_catalog_gate` | field catalog 生成且与 matrix 一致 |
| `d_class_phase1_freeze_v1_fixture_gate` | 7 组件 + empty_but_valid fixture 存在 |
| `d_class_phase1_freeze_v1_lint_gate` | lint 全 PASS |
| `d_class_phase1_ready_case_benchmark_gate` | CSV + ready_cases 骨架 READY_FOR_REVIEW |

---

## 6. Red Lines

- **No CNINFO** until explicit future approval
- **No harvest**
- **No verified**
- **No testing_stable_sample upgrade**
- **No A/B/C output modification**

---

## 7. Next Task After Implementation

harvest architecture dry-run 规划（**仍无 live**）→ 未来 tiny sample live approval（单独 gate）。
