# CNINFO D 类 executive_shareholding — Sample Prep（Offline Fixture Plan）

_生成时间：2026-07-15_

> **性质：** offline sample fixture **plan** only · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 fixture 文件写入** · **无 claim approved** · **无 commit** · **无 push**
>
> **任务 ID：** D-R16-01
>
> **边界：** `READY_FOR_APPROVAL` ≠ **approved** · `component_approved=false` · disclosure ≠ structured capture · **不是 verified** · **不是 production_ready**
>
> **Tier-0 仅允许引用：** **DC006** · **DLC007**（本包 **不** 引入其他 Phase1 ready-case / tiny-live 行作为 baseline）

---

## 1. Delta vs Run 15 Stub

| 维度 | Run 15 stub（ESH-STUB-03） | **本包（D-R16-01）** |
|------|---------------------------|----------------------|
| 状态 | `blocked_until_approval` · cite DC006/DLC007 only | **plan promoted** · 仍 **不创建** JSON fixture |
| 焦点 | 一句占位 | **可执行 fixture 分层计划** · 每案形态 · Tier-0 仅 DC006/DLC007 |
| 产出物 | n/a | **plan only** — 本任务 **不创建** Tier-1 JSON |

---

## 2. Current Gate（unchanged）

```text
d_class_executive_shareholding_next_component_planning_gate = READY_FOR_APPROVAL
executive_shareholding_component_approved = false
schema_prep_blocked_until_level2 = true
```

**本包不升级 gate。**

---

## 3. Fixture Tier Architecture

```text
Tier-0  read-only baseline（已存在 · 只读引用 · 仅 DC006 + DLC007）
    ├── DC006.json          Phase1 freeze v1 · captured_normal 模板
    └── DLC007 calibrated   tiny-live needs_review_candidate 先例

Tier-1  planned synthetic（本包规格 · 待后续 implementation approval）
    └── fixtures/d_class/executive_shareholding_first_slice/DES00{1-5}_*.json

Tier-2  future live/dry-run output（runner 未实现 · 路径预规划）
    └── outputs/validation/cninfo_d_class_executive_shareholding_first_slice/**
```

**证据边界：** Tier-0/Tier-1 均为 **offline synthetic 或历史只读** · **不得** 将 disclosure PDF / 人工复核内容填入 structured 字段 · Tier-2 仅在 **未来 approved live** 后由 pipeline 产生 **captured structured evidence**。

---

## 4. Tier-0 — Read-Only Baseline（cite DC006 / DLC007 only）

### 4.1 DC006 — Phase1 captured_normal 模板

| 项 | 值 |
|----|-----|
| 路径 | `fixtures/d_class/phase1/DC006.json` |
| ready_case_id | **DC006** |
| case_type | `captured_normal` |
| cninfo_called | **false**（synthetic） |
| 用途 | first-slice **found** 路径的 envelope + payload 形态对照 · lint/benchmark 基线 |
| 关键字段 | `event_status=captured` · `quality_status=pass` · `executive_shareholding.change_type` · lineage `registry_source_id=executive_shareholding` |
| 与 DES 关系 | **不** 直接作为 DES001–005 运行输入 · 仅作 **结构模板** |

### 4.2 DLC007 — tiny-live calibrated precedent（read-only）

| 项 | 值 |
|----|-----|
| 路径 | `outputs/validation/cninfo_d_class_phase1_tiny_live_universe_calibrated.csv`（row **DLC007**） |
| company | **002415** 海康威视 |
| calibrated expected | `needs_review_candidate`（position/amount medium confidence · **不** forced pass） |
| 补充证据（只读） | Phase1 tiny-live quality：found · 2 rows · `quality_status=needs_review` |
| 与 DES001 关系 | 同一公司 · **独立 case_id DES001** · **不是** DDS004 代理 · **不是** sole `captured_normal_candidate` |
| 用途 | DES001 expectation `captured_normal_or_needs_review` 的 **历史校准参照** · 禁止从 DLC007 结论反推 first-slice 必 forced pass |

### 4.3 永久排除（不得纳入 fixture plan）

| 排除 | 原因 |
|------|------|
| **688671** DLC003R | known-event 主案例 · 不作 first-slice 主案例 |
| **301259** DLC006R | known-event closed · disclosure Option A+C · **永久排除** primary universe |
| 其他 Phase1 DC/DLC（非 DC006/DLC007） | **本包不允许** 作为 executive_shareholding Tier-0 baseline 引用 |

---

## 5. Tier-1 — Planned Synthetic Fixtures（规格 · 未创建）

**目标目录（planned · blocked until later implementation approval）：**

```text
fixtures/d_class/executive_shareholding_first_slice/
├── DES001_needs_review_synthetic.json
├── DES002_captured_or_empty_synthetic.json   # 或 *_found.json / *_empty.json 双态
├── DES003_captured_or_empty_synthetic.json
├── DES004_captured_or_empty_synthetic.json
└── DES005_empty_but_valid_synthetic.json
```

**共享 query contract（所有 Tier-1 fixture）：**

| 参数 | 值 |
|------|-----|
| endpoint | `https://www.cninfo.com.cn/data20/leader/detail` |
| method | POST · params in query |
| `timeMark` | `oneMonth` |
| `varyType` | `b` |
| records_path | `data.records` |
| company filter | `SECCODE` == universe `company_code` |

### 5.1 Per-Case Fixture Specification

| case_id | company | expected_behavior | fixture 形态 | raw `data.records` | envelope | component payload |
|---------|---------|-------------------|--------------|-------------------|----------|-------------------|
| **DES001** | 002415 海康威视 | captured_normal_or_needs_review | **单态 found** · 故意保留映射疑点（对齐 DLC007） | ≥1 行 · position/amount medium confidence 边界 | `captured` + `quality_status=needs_review` | payload 存在 · **不** forced pass |
| **DES002** | 000895 双汇发展 | captured_normal_or_empty_but_valid | **双态** found/empty | 合成 SECCODE=000895 | found: `captured` · empty: `empty_but_valid` | found: freeze 必填 · empty: **无** payload |
| **DES003** | 600000 浦发银行 | captured_normal_or_empty_but_valid | 同 DES002 双态 | 合成 SECCODE=600000 | 同上 | 同上 |
| **DES004** | 000550 江铃汽车 | captured_normal_or_empty_but_valid | 同 DES002 双态 | 合成 SECCODE=000550 | 同上 | 同上 |
| **DES005** | 601988 中国银行 | empty_but_valid | **单态 empty** 控制案 | `[]`（零行） | `empty_but_valid` · `quality_status=pass` | **禁止** payload · **禁止** 伪造 executive_name/change_amount |

### 5.2 Synthetic Raw Record Template（found 路径）

每条 `data.records[]` 行建议含 registry 确认核心字段：

```json
{
  "SECCODE": "<universe company_code>",
  "SECNAME": "<universe company_name>",
  "ENDDATE": "2026-06-15",
  "HUMANNAME": "合成高管姓名",
  "F001V": "合成变动人",
  "F002V": "董事",
  "F003V": "本人",
  "F006N": 10000.0,
  "F008N": 12.50,
  "F010V": "二级市场买卖"
}
```

| 字段 | 合成规则 |
|------|----------|
| SECCODE | 必须等于 fixture 对应 universe `company_code` |
| ENDDATE | 主事件日 · 映射 `change_date` / `event_time` |
| HUMANNAME | 非空字符串 · 参与 `event_id` hash |
| F006N | 正数 shares · `change_amount` |
| F002V | position · DES001 可保留歧义以触发 needs_review |
| F005N | **uncertain** · 可省略 · 不得 forced fill |
| DECLAREDATE / F004N / F007N / F009N / F011V | raw_only · 可省略 |

**lineage 必填（captured 行）：** 完整 raw 对象写入 `lineage.raw_record_json` · `raw_record_hash` 对 raw 对象稳定 hash · `cninfo_called=false` 标记 synthetic。

### 5.3 Envelope + Payload Contract（per fixture file）

每个 Tier-1 JSON **建议结构**（对齐 DC006 · Phase1 event object schema）：

```json
{
  "_fixture_meta": {
    "purpose": "D-class executive_shareholding first-slice offline synthetic",
    "case_id": "DES00X",
    "component": "executive_shareholding",
    "scenario": "captured|empty_but_valid|needs_review",
    "cninfo_called": false,
    "synthetic": true,
    "query_params": { "timeMark": "oneMonth", "varyType": "b" }
  },
  "market_event": { },
  "executive_shareholding": { }
}
```

| scenario | `market_event.event_status` | `executive_shareholding` 键 |
|----------|----------------------------|-----------------------------|
| captured | `captured` | **存在** · freeze required 字段齐全 |
| empty_but_valid | `empty_but_valid` | **省略** 整个键 |
| needs_review | `captured` | **存在** · `quality_status=needs_review` |

**一致性：** `event_time` ≡ `executive_shareholding.change_date` · 信封与 payload `company_code` / `quality_status` 必须一致。

---

## 6. Tier-2 — Future Output Root Layout（planned · package dir may hold offline docs only）

```text
outputs/validation/cninfo_d_class_executive_shareholding_first_slice/
├── reports/                    # future dry-run / live
│   ├── d_class_executive_shareholding_first_slice_dryrun_report.csv
│   ├── d_class_executive_shareholding_first_slice_dryrun_summary.md
│   ├── d_class_executive_shareholding_first_slice_live_report.csv
│   ├── d_class_executive_shareholding_first_slice_quality_report.csv
│   └── d_class_executive_shareholding_first_slice_live_summary.md
├── live_snapshots/             # future live only
│   └── {case_id}_executive_shareholding.json
└── planned_snapshots/          # future dry-run only
    └── {case_id}_executive_shareholding.json
```

**live_snapshot 最小字段（future）：** `case_id` · `company_code` · `component` · `endpoint` · `params{timeMark,varyType}` · `http_status` · `record_count` · `sample_records[]` · `cninfo_called` · `db_write=false` · `minio_write=false` · `rag_run=false`

**本任务不创建** reports / live_snapshots / planned_snapshots · **不** 写入 live JSON。

---

## 7. Offline Validation Harness Hooks（read-only · 不执行）

| 钩子 | 路径 | 与 fixture 关系 |
|------|------|-----------------|
| Phase1 freeze lint | `lab/lint_cninfo_d_class_phase1_freeze_v1.py` | DC006.json 已注册 · Tier-1 实现后需扩展 case registry |
| Ready-case benchmark | `lab/run_cninfo_d_class_phase1_ready_case_benchmark.py` | DC006 benchmark row · Tier-1 **不** 替代 DC006 |
| First-slice acceptance | [validation_rules](cninfo_d_class_executive_shareholding_validation_rules_20260715.md) | Tier-1 fixture 实现后逐条 VR 对照 |
| Tier-0 cite | DC006.json · DLC007 calibrated row | **仅此二者** |

---

## 8. Implementation Sequence（blocked）

| 步骤 | 触发条件 | 动作 | 状态 |
|------|----------|------|------|
| S1 | human component phrase | Controller 审阅本 sample plan + approval package | **waiting_human** |
| S2 | first-slice approval package（本包） | 锁定 formal universe DES001–005 | **DONE**（universe lock · 本任务） |
| S3 | offline implementation approval | 创建 Tier-1 synthetic JSON（DES001–005 variants） | **blocked** |
| S4 | runner extension approval | dry-run 写入 Tier-2 planned_snapshots | **blocked** · **forbidden this round** |
| S5 | live approval | CNINFO → live_snapshots · outcome ledger | **blocked** · **forbidden this round** |

---

## 9. Safety Zeros

| 项 | 本包 |
|----|------|
| CNINFO calls | **0** |
| fixture 文件创建 | **0**（plan only · cite DC006/DLC007 only） |
| live / runner | **no** |
| gate upgrade | **no** |
| commit / push | **no** |
| disclosure → structured promotion | **no** |
| component_approved | **false** |

---

## 10. Summary Block

```text
task_id = D-R16-01
phase = executive_shareholding_sample_prep_20260715
delta = tiered_fixture_plan + per_case_synthetic_spec + future_output_layout
tier0_readonly = DC006.json + DLC007_calibrated_row (ONLY)
tier1_planned = fixtures/d_class/executive_shareholding_first_slice/DES001-005_*.json (not created)
tier2_planned = outputs/validation/cninfo_d_class_executive_shareholding_first_slice/** (reports not created)
current_gate = READY_FOR_APPROVAL
component_approved = false
cninfo_calls = 0
disclosure_equals_structured = false
```
