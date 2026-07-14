# CNINFO D 类 shareholder_change — Sample Prep（Offline Fixture Plan）

_生成时间：2026-07-14_

> **性质：** offline sample fixture **plan** only · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 fixture 文件写入** · **无 claim approved** · **无 commit** · **无 push**
>
> **边界：** `READY_FOR_APPROVAL` ≠ **approved** · disclosure ≠ structured capture · **不是 verified** · **不是 production_ready**
>
> **前置（只读引用，本包不重复）：** [schema_prep](cninfo_d_class_shareholder_change_schema_prep_20260714.md) · [event_model CSV](cninfo_d_class_shareholder_change_event_model_20260714.csv) · [prep refresh](cninfo_d_class_shareholder_change_offline_prep_refresh_20260714.md)

---

## 1. Delta vs Prior Artifacts

| 维度 | schema_prep / event_model | prep refresh / checklist | **本包（D-GEN-20260714-05）** |
|------|---------------------------|--------------------------|-------------------------------|
| 焦点 | 三层字段映射 · event taxonomy | gate 重述 · artifact 清点 | **可执行 fixture 分层计划** · 每案 raw/envelope 形态 · 离线验收挂钩 |
| 机器可读 | event_model（field 粒度） | checklist（item/status） | **指向未来 fixture 路径 + validation_rules + evidence_map** |
| 样本 | DC005 一句引用 | DSC001–005 universe sketch | **5 案 synthetic 规格 + 2 个只读 baseline 引用** |
| 产出物 | 无新 fixture | 无新 fixture | **plan only** — 本任务 **不创建** JSON fixture 文件 |

---

## 2. Current Gate（unchanged）

```text
d_class_shareholder_change_next_component_planning_gate = READY_FOR_APPROVAL
approval_queue_id = AQ-D-SC
approval_queue_status = WAITING_APPROVAL
shareholder_change_component_approved = false
schema_prep_blocked_until_level2 = true
```

**本包不升级 gate。**

---

## 3. Fixture Tier Architecture

```text
Tier-0  read-only baseline（已存在 · 只读引用）
    ├── DC005.json          Phase1 freeze v1 · captured_normal 模板
    └── DLC006 calibrated   tiny-live 先例口径 · empty_but_valid 校准

Tier-1  planned synthetic（本包规格 · 待 Level-2 后实现）
    └── fixtures/d_class/shareholder_change_first_slice/DSC00{1-5}_*.json

Tier-2  future live/dry-run output（runner 未实现 · 路径预规划）
    └── outputs/validation/cninfo_d_class_shareholder_change_first_slice/**
```

**证据边界：** Tier-0/Tier-1 均为 **offline synthetic 或历史只读** · **不得** 将 disclosure PDF / 人工复核内容填入 structured 字段 · Tier-2 仅在 **未来 approved live** 后由 pipeline 产生 **captured structured evidence**。

---

## 4. Tier-0 — Read-Only Baseline（cite only）

### 4.1 DC005 — Phase1 captured_normal 模板

| 项 | 值 |
|----|-----|
| 路径 | `fixtures/d_class/phase1/DC005.json` |
| ready_case_id | **DC005** |
| case_type | `captured_normal` |
| cninfo_called | **false**（synthetic） |
| 用途 | first-slice **found** 路径的 envelope + payload 形态对照 · lint/benchmark 基线 |
| 关键字段 | `event_status=captured` · `quality_status=pass` · `shareholder_change.change_type=inc` · lineage `query_mode=type_inc` |
| 与 DSC 关系 | **不** 直接作为 DSC001–005 运行输入 · 仅作 **结构模板** |

### 4.2 DLC006 — tiny-live calibrated precedent（read-only）

| 项 | 值 |
|----|-----|
| 路径 | `outputs/validation/cninfo_d_class_phase1_tiny_live_universe_calibrated.csv`（row DLC006） |
| company | **000550** 江铃汽车 |
| calibrated expected | `empty_but_valid`（human_signed_off · v1_v2_bounded_probe_empty） |
| 与 DSC001 关系 | 同一公司 · **独立 case_id DSC001** · **不是** DLC006R 代理 · **不是** sole `captured_normal_candidate` |
| 用途 | DSC001 expectation mix `captured_normal_or_empty_but_valid` 的 **历史校准参照** · 禁止从 DLC006 结论反推 sparse anchor 必有行 |

### 4.3 永久排除（不得纳入 fixture plan）

| 排除 | 原因 |
|------|------|
| **688671** DLC003R | known-event 主案例 · 不作 first-slice 主案例 |
| **301259** DLC006R | known-event closed · disclosure Option A+C · **永久排除** primary universe |

---

## 5. Tier-1 — Planned Synthetic Fixtures（规格 · 未创建）

**目标目录（planned · blocked until Level-2 + later implementation approval）：**

```text
fixtures/d_class/shareholder_change_first_slice/
├── DSC001_captured_or_empty_synthetic.json
├── DSC002_captured_or_empty_synthetic.json
├── DSC003_captured_or_empty_synthetic.json
├── DSC004_needs_review_synthetic.json
└── DSC005_empty_but_valid_synthetic.json
```

**共享 query contract（所有 Tier-1 fixture）：**

| 参数 | 值 |
|------|-----|
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| method | POST · params in query |
| `type` | `inc` |
| `tdate` | `2026-07-03` |
| records_path | `data.records` |
| company filter | `SECCODE` == universe `company_code` |

### 5.1 Per-Case Fixture Specification

| case_id | company | expected_behavior | fixture 形态 | raw `data.records` | envelope | component payload |
|---------|---------|-------------------|--------------|-------------------|----------|-------------------|
| **DSC001** | 000550 江铃汽车 | captured_normal_or_empty_but_valid | **双态文件** 或 **两个 variant 文件**（`*_found.json` / `*_empty.json`） | found: ≥1 行含 8 字段 · empty: `[]` | found: `captured` · empty: `empty_but_valid` | found: 必填 freeze 字段 · empty: **无** payload 行 |
| **DSC002** | 000895 双汇发展 | captured_normal_or_empty_but_valid | 同 DSC001 双态模式 | 合成 SECCODE=000895 | 同上 | 同上 |
| **DSC003** | 600000 浦发银行 | captured_normal_or_empty_but_valid | 同 DSC001 双态模式 | 合成 SECCODE=600000 | 同上 | 同上 |
| **DSC004** | 002415 海康威视 | captured_normal_or_needs_review | **单态 found** · 故意保留映射疑点 | ≥1 行 · 可选省略 `F005N` 或 `F007V` 边界值 | `captured` + `quality_status=needs_review` | payload 存在 · `change_ratio` nullable |
| **DSC005** | 601988 中国银行 | empty_but_valid | **单态 empty** 控制案 | `[]`（零行） | `empty_but_valid` · `quality_status=pass` | **禁止** payload · **禁止** 伪造 shareholder_name/change_amount |

### 5.2 Synthetic Raw Record Template（found 路径 · inc 模式）

每条 `data.records[]` 行 **必须** 含 registry 确认的 8 字段（与 inc/desc 同形）：

```json
{
  "SECCODE": "<universe company_code>",
  "SECNAME": "<universe company_name>",
  "DECLAREDATE": "2026-07-03",
  "VARYDATE": "2026-07-10",
  "F002V": "合成股东名称",
  "F004N": 500000.0,
  "F005N": 0.12,
  "F007V": "12.50"
}
```

| 字段 | 合成规则 |
|------|----------|
| SECCODE | 必须等于 fixture 对应 universe `company_code` |
| VARYDATE | 主事件日 · 映射 `change_date` / `event_time` |
| F002V | 非空字符串 · 参与 `event_id` hash |
| F004N | 正数 shares · `primary_amount_unit=shares` |
| F005N | 可省略（DSC004 needs_review 边界） |
| F007V | 可省略（first-slice optional） |
| DECLAREDATE | recommended · 可等于或晚于 VARYDATE |

**lineage 必填（captured 行）：** 完整 raw 对象写入 `lineage.raw_record_json` · `raw_record_hash` 对 raw 对象稳定 hash · `cninfo_called=false` 标记 synthetic。

### 5.3 Envelope + Payload Contract（per fixture file）

每个 Tier-1 JSON **建议结构**（对齐 DC005 · Phase1 event object schema）：

```json
{
  "_fixture_meta": {
    "purpose": "D-class shareholder_change first-slice offline synthetic",
    "case_id": "DSC00X",
    "component": "shareholder_change",
    "scenario": "captured|empty_but_valid|needs_review",
    "cninfo_called": false,
    "synthetic": true,
    "query_params": { "type": "inc", "tdate": "2026-07-03" }
  },
  "market_event": { },
  "shareholder_change": { }
}
```

| scenario | `market_event.event_status` | `shareholder_change` 键 |
|----------|----------------------------|-------------------------|
| captured | `captured` | **存在** · freeze required 字段齐全 |
| empty_but_valid | `empty_but_valid` | **省略** 整个键 |
| needs_review | `captured` | **存在** · `quality_status=needs_review` |

**一致性：** `event_time` ≡ `shareholder_change.change_date` · 信封与 payload `company_code` / `quality_status` 必须一致。

---

## 6. Tier-2 — Future Output Root Layout（planned · not created）

参照 equity_pledge first-slice 已验证布局 · shareholder_change 预规划：

```text
outputs/validation/cninfo_d_class_shareholder_change_first_slice/
├── reports/
│   ├── d_class_shareholder_change_first_slice_dryrun_report.csv
│   ├── d_class_shareholder_change_first_slice_dryrun_summary.md
│   ├── d_class_shareholder_change_first_slice_live_report.csv
│   ├── d_class_shareholder_change_first_slice_quality_report.csv
│   └── d_class_shareholder_change_first_slice_live_summary.md
├── live_snapshots/
│   └── {case_id}_shareholder_change.json
└── planned_snapshots/          # dry-run only（若 runner 实现）
    └── {case_id}_shareholder_change.json
```

**live_snapshot 最小字段（future）：** `case_id` · `company_code` · `component` · `endpoint` · `params{type,tdate}` · `http_status` · `record_count` · `sample_records[]`（含 8 字段 raw 行）· `cninfo_called` · `db_write=false` · `minio_write=false` · `rag_run=false`

**本任务不创建上述目录或文件。**

---

## 7. Offline Validation Harness Hooks（read-only · 不执行）

| 钩子 | 路径 | 与 fixture 关系 |
|------|------|-----------------|
| Phase1 freeze lint | `lab/lint_cninfo_d_class_phase1_freeze_v1.py` | DC005.json 已注册 · Tier-1 实现后需扩展 case registry |
| Ready-case benchmark | `lab/run_cninfo_d_class_phase1_ready_case_benchmark.py` | DC005 benchmark row · Tier-1 **不** 替代 DC005 |
| Mapper 离线引用 | `lab/cninfo_d_class_mappers.py` → `_map_shareholder_change` | Tier-1 raw template 应用 mapper 做 offline round-trip 校验（未来） |
| First-slice acceptance | [validation_rules](cninfo_d_class_shareholder_change_validation_rules_20260714.md) | Tier-1 fixture 实现后逐条 VR 对照 |
| Evidence path 对照 | [offline_evidence_map CSV](cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv) | raw 字段 → artifact pattern |

---

## 8. Implementation Sequence（blocked）

| 步骤 | 触发条件 | 动作 | 状态 |
|------|----------|------|------|
| S1 | Level-2 组件短语落档 | Controller 审阅本 sample plan | **blocked** |
| S2 | first-slice approval package | 锁定 formal universe DSC001–005 | **blocked** |
| S3 | offline implementation approval | 创建 Tier-1 synthetic JSON（5+ variants） | **blocked** |
| S4 | runner extension approval | dry-run 写入 Tier-2 planned_snapshots | **blocked** |
| S5 | live approval | CNINFO → live_snapshots · outcome ledger | **blocked** |

---

## 9. Safety Zeros

| 项 | 本包 |
|----|------|
| CNINFO calls | **0** |
| fixture 文件创建 | **0**（plan only） |
| live / runner | **no** |
| gate upgrade | **no** |
| commit / push | **no** |
| disclosure → structured promotion | **no** |

---

## 10. Summary Block

```text
phase = shareholder_change_sample_prep_20260714
delta = tiered_fixture_plan + per_case_synthetic_spec + future_output_layout
tier0_readonly = DC005.json + DLC006_calibrated_row
tier1_planned = fixtures/d_class/shareholder_change_first_slice/DSC001-005_*.json (not created)
tier2_planned = outputs/validation/cninfo_d_class_shareholder_change_first_slice/** (not created)
current_gate = READY_FOR_APPROVAL
cninfo_calls = 0
disclosure_equals_structured = false
```
