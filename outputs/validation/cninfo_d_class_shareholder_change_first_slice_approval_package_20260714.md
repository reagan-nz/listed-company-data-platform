# CNINFO D 类 shareholder_change First-Slice — Approval Package

_生成时间：2026-07-14_

> **性质：** Era D 离线 first-slice approval package · **CNINFO calls = 0** · **无 live** · **无 runner 执行** · **无 commit** · **无 push**
>
> **任务 ID：** D-GEN-20260714-06
>
> **边界：** 组件 **APPROVED** · first-slice live **NOT auto-approved** · **不是 verified** · **不是 production_ready**

---

## 1. Human Approval Record

| 项 | 值 |
|----|-----|
| approval_queue_id | **AQ-D-SC** |
| decision type | D-class **component** Level-2 approval |
| exact phrase received | **I approve D-class shareholder_change as the next Era D component.** |
| approval date | 2026-07-14 |
| approval scope | 确认 `shareholder_change` 为 Era D 下一主组件 · **不** 授权 live · **不** 授权 runner · **不** 授权 CNINFO |
| does not authorize | first-slice live · dry-run execution · runner extension · CNINFO · commit · push · verified · production_ready |

---

## 2. Executive Summary

| 项 | 值 |
|----|-----|
| component | `shareholder_change` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event`（metadata only） |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| registry path | `shareholder_change/shareholeder/detail`（拼写 **shareholeder** 保留） |
| query mode | **`type_inc` + `tdate_daily`** · first-slice 仅 `type=inc` |
| date_param | **`tdate`**（公告日锚点 · 全宇宙共享 `2026-07-03`） |
| type_param | **`type=inc`**（增持模式 · `desc` 留待扩展） |
| universe | **5** rows · case_id **DSC001–DSC005**（**locked**） |
| request cap (future live) | per-case **≤ 4** · total **≤ 20** · planned **~5** |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` · **不是 bare PASS** |
| component approval | **APPROVED**（human phrase 已落档） |
| first-slice live approval | **NOT APPROVED** |
| runner approval | **NOT APPROVED**（`--shareholder-change-first-slice` **未实现**） |
| CNINFO calls (this package) | **0** |

---

## 3. Gate Status（post AQ-D-SC）

```text
d_class_shareholder_change_next_component_planning_gate = COMPONENT_APPROVED
approval_queue_id = AQ-D-SC
approval_queue_status = APPROVED_COMPONENT_ONLY
shareholder_change_component_approved = true
shareholder_change_first_slice_approval_gate = READY_FOR_NEXT_STEP
shareholder_change_first_slice_live_gate = NOT_APPROVED
shareholder_change_first_slice_runner_gate = NOT_APPROVED
shareholder_change_first_slice_execution_gate = NOT_APPLICABLE
schema_prep_blocked_until_level2 = false
```

| 判定 | 状态 |
|------|------|
| component choice | **human-approved** |
| planning gate | **COMPONENT_APPROVED**（自 `READY_FOR_APPROVAL` 升级 · 仅组件级） |
| first-slice universe | **locked**（本包） |
| first-slice live | **NOT auto-approved** |
| runner extension | **NOT approved** · **未实现** |
| verified / production_ready | **no** |

**强制语义：** `COMPONENT_APPROVED` ≠ live_approved ≠ runner_approved ≠ verified ≠ production_ready。

---

## 4. Universe Lock（DSC001–DSC005）

**正式锁定文件：** [cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv](cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv)

**来源草案（只读引用 · 不修改）：** [cninfo_d_class_shareholder_change_first_slice_universe_draft_sketch.csv](cninfo_d_class_shareholder_change_first_slice_universe_draft_sketch.csv)

| case_id | company_code | company_name | market | expected_behavior | notes |
|---------|--------------|--------------|--------|-------------------|-------|
| DSC001 | 000550 | 江铃汽车 | szse_main | captured_normal_or_empty_but_valid | DLC006 precedent · distinct DSC case_id · not DLC006R |
| DSC002 | 000895 | 双汇发展 | szse_main | captured_normal_or_empty_but_valid | SZSE active · cross-slice reuse |
| DSC003 | 600000 | 浦发银行 | sse_main | captured_normal_or_empty_but_valid | SSE financial |
| DSC004 | 002415 | 海康威视 | szse_main | captured_normal_or_needs_review | field mapping review if found |
| DSC005 | 601988 | 中国银行 | sse_main | empty_but_valid | sparse-day control · board diversity |

### Anchor & Query Contract（locked）

| 参数 | 锁定值 |
|------|--------|
| `anchor_tdate` | **2026-07-03**（全案共享 · 离线文档化 · 本包未 CNINFO 探测） |
| `query_type` | **inc**（first-slice 单模式 · VR-007/008） |
| `first_slice_include` | **yes**（全案） |
| per-case request budget | **≤ 4** |
| total request cap | **≤ 20** |
| planned requests (5-case) | **~5**（单 type+tdate 预期 1 请求/案） |

### Permanent Exclusions

| 排除 | 原因 |
|------|------|
| **688671**（DLC003R 碧兴物联） | known-event 主案例 · **不作 first-slice 主案例** |
| **301259**（DLC006R 艾布鲁） | known-event closed · disclosure Option A+C · **永久排除** primary universe |

**VR-004 · VR-040 合规：** exclude_flags 含 `exclude_688671;exclude_301259` · 无对应 universe 行。

---

## 5. Validation Rules Cross-Reference（VR-001–VR-042）

**只读引用（本包不修改）：** [cninfo_d_class_shareholder_change_validation_rules_20260714.md](cninfo_d_class_shareholder_change_validation_rules_20260714.md)

| 类别 | 规则 ID | 本包挂钩 |
|------|---------|----------|
| A — Universe & Query | VR-001 – VR-008 | universe lock 5 行 · DSC001–005 · 锚点/预算/排除 · inc-only |
| B — Raw Retrieval | VR-009 – VR-014 | expectation mix · empty_but_valid 合法 · 无 fragile anchor |
| C — Field Mapping | VR-015 – VR-024 | 8 字段 raw → payload · event_id hash · optional F005N/F007V |
| D — Envelope & Quality | VR-025 – VR-032 | captured/empty_but_valid · freeze v1 · ≥3/5 threshold |
| E — Lineage | VR-033 – VR-037 | raw_record_json · query_mode=type_inc · discovered only |
| F — Evidence Boundary | VR-038 – VR-040 | disclosure 隔离 · 301259/DLC006R 永久排除 |
| G — Governance | VR-041 – VR-042 | 组件已批 · live 未批 · 无 verified/production_ready |

**Per-case VR 重点子集：**

| case_id | expected_behavior | VR 重点 |
|---------|-------------------|---------|
| DSC001 | captured_normal_or_empty_but_valid | VR-012·013·025·026 |
| DSC002 | captured_normal_or_empty_but_valid | VR-012·013·025·026 |
| DSC003 | captured_normal_or_empty_but_valid | VR-012·013·025·026 |
| DSC004 | captured_normal_or_needs_review | VR-014·030 |
| DSC005 | empty_but_valid | VR-012·026·027 |

**本包执行状态：** VR 清单为 **offline draft** · 本包 **不执行** live/synthetic 验收 · 仅落档 cross-ref。

---

## 6. Tier-0 / Tier-1 / Tier-2 Path Architecture

### Tier-0 — Read-Only Baseline（cite only）

| 路径 | 用途 |
|------|------|
| [fixtures/d_class/phase1/DC005.json](../../fixtures/d_class/phase1/DC005.json) | Phase1 freeze v1 · `captured_normal` 结构模板 · cninfo_called=false |
| [cninfo_d_class_phase1_tiny_live_universe_calibrated.csv](cninfo_d_class_phase1_tiny_live_universe_calibrated.csv)#DLC006 | 000550 公司 · calibrated `empty_but_valid` · DSC001 历史参照（**非** DLC006R 代理） |

### Tier-1 — Synthetic Fixtures（本任务 S3 离线实现 · CNINFO=0）

**规格来源（只读引用）：** [cninfo_d_class_shareholder_change_sample_prep_20260714.md](cninfo_d_class_shareholder_change_sample_prep_20260714.md)

```text
fixtures/d_class/shareholder_change_first_slice/
├── DSC001_found.json / DSC001_empty.json      [created]
├── DSC002_found.json / DSC002_empty.json      [created]
├── DSC003_found.json / DSC003_empty.json      [created]
├── DSC004_needs_review_synthetic.json         [created]
└── DSC005_empty_but_valid_synthetic.json      [created]
```

**状态：** 8 个 synthetic JSON 已创建 · `cninfo_called=false` · 供离线 VR 对照 · **不** 替代 Tier-2 live/dry-run 输出。

**证据映射（只读引用）：** [cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv](cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv)

### Tier-2 — Isolated Output Root（planned · not created）

```text
outputs/validation/cninfo_d_class_shareholder_change_first_slice/
├── reports/
│   ├── d_class_shareholder_change_first_slice_dryrun_report.csv
│   ├── d_class_shareholder_change_first_slice_dryrun_summary.md
│   ├── d_class_shareholder_change_first_slice_live_report.csv
│   ├── d_class_shareholder_change_first_slice_quality_report.csv
│   ├── d_class_shareholder_change_first_slice_live_summary.md
│   └── d_class_shareholder_change_first_slice_live_outcome_ledger.csv
├── live_snapshots/
│   └── {case_id}_shareholder_change.json
└── planned_snapshots/
    └── {case_id}_shareholder_change.json
```

**禁止写入：** equity_pledge · restricted_shares_unlock · block_trade · margin_trading · disclosure_schedule · known-event · tiny_live v1/v2 等已关闭轨输出根。

---

## 7. Prior Artifact Citations（read-only · not mutated）

| # | 路径 | 角色 |
|---|------|------|
| 1 | [cninfo_d_class_shareholder_change_schema_prep_20260714.md](cninfo_d_class_shareholder_change_schema_prep_20260714.md) | 三层字段映射 · ownership-event 分类 |
| 2 | [cninfo_d_class_shareholder_change_event_model_20260714.csv](cninfo_d_class_shareholder_change_event_model_20260714.csv) | 机器可读 event/field model |
| 3 | [cninfo_d_class_shareholder_change_sample_prep_20260714.md](cninfo_d_class_shareholder_change_sample_prep_20260714.md) | Tier-0/1/2 fixture 分层计划 |
| 4 | [cninfo_d_class_shareholder_change_validation_rules_20260714.md](cninfo_d_class_shareholder_change_validation_rules_20260714.md) | VR-001–VR-042 验收规则 |
| 5 | [cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv](cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv) | raw 字段 → artifact pattern |
| 6 | [plans/cninfo_d_class_shareholder_change_first_slice_plan_draft.md](../plans/cninfo_d_class_shareholder_change_first_slice_plan_draft.md) | first-slice 草案 |
| 7 | [fixtures/d_class/phase1/DC005.json](../../fixtures/d_class/phase1/DC005.json) | Phase1 captured_normal baseline |
| 8 | [cninfo_d_class_autonomous_batch_v1_shareholder_change_gate.md](cninfo_d_class_autonomous_batch_v1_shareholder_change_gate.md) | autonomous batch gate 文档 |

---

## 8. Expected Behavior Mix（lessons applied）

| 语义 | 说明 |
|------|------|
| `empty_but_valid` | 公司级零行 · 稀疏查询日合法空态（DSC005 控制案） |
| `captured_normal_or_empty_but_valid` | **默认推荐** — found 或 empty 均可 acceptable（DSC001–003） |
| `captured_normal_or_needs_review` | found 可接受；字段映射不确定时 `needs_review`（DSC004） |

**禁止：**

- sole `captured_normal_candidate` 绑定稀疏 anchor（DBT002 教训）
- 单独 fragile `captured_normal_or_needs_review` 无混排（DEP004 教训）
- disclosure-only 证据升级为 captured_normal（DLC006R 教训）

**Expected mix：** 1 `empty_but_valid` · 3 `captured_normal_or_empty_but_valid` · 1 `captured_normal_or_needs_review` · **0** sole `captured_normal_candidate`

---

## 9. CNINFO Request Cap（future live only）

| 项 | 值 |
|----|-----|
| per-case requests | **≤ 4** |
| total cap | **≤ 20** |
| planned (5-case) | **~5** |
| sleep default | 0.6s（与 prior slices 一致 · 未来 live 规划值） |
| early_stop | per-case 命中公司行后停止（若 runner 实现） |

**本包 CNINFO calls = 0。** 上表仅供未来 live 审批后参照。

---

## 10. Closed Tracks（frozen · no reopen）

| Track | Gate | Commit |
|-------|------|--------|
| equity_pledge | `PASS_WITH_CAVEAT` | `85abad0` · **NOT pushed** |
| restricted_shares_unlock | `PASS_WITH_CAVEAT` | `aa087b5` · **NOT pushed** |
| block_trade | `PASS_WITH_CAVEAT` · **NOT verified** | `403472d` · **NOT pushed** |
| margin_trading | `PASS_WITH_CAVEAT` | `116f875` |
| disclosure_schedule | `PASS_WITH_CAVEAT` | `d37ce0a` |
| known-event | `PASS_WITH_CAVEAT` | `389cd9c` |

- **No** DLC003R / DLC006R rerun
- **No** disclosure→captured_normal promotion
- **No** PDF/OCR/DB/MinIO/RAG

---

## 11. Safety Confirmations

| 项 | 本包 |
|----|------|
| CNINFO calls | **0** |
| live execution | **no** |
| runner execution | **no** |
| commit / push | **no** |
| schema_prep / event_model / sample_prep / validation_rules / evidence_map 原位修改 | **no**（仅引用） |
| gate upgrade beyond component | **no**（live/runner 仍 NOT_APPROVED） |
| verified / production_ready / testing_stable_sample | **no** |

---

## 12. Package Artifacts（this task）

| 文档 | 路径 |
|------|------|
| approval package | [cninfo_d_class_shareholder_change_first_slice_approval_package_20260714.md](cninfo_d_class_shareholder_change_first_slice_approval_package_20260714.md)（本文件） |
| universe lock | [cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv](cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv) |
| command draft | [cninfo_d_class_shareholder_change_first_slice_command_draft_20260714.md](cninfo_d_class_shareholder_change_first_slice_command_draft_20260714.md) |

---

## 13. Next Steps（separately gated）

| 步骤 | 触发条件 | 动作 | 当前状态 |
|------|----------|------|----------|
| **S3** | offline implementation approval（或 Controller 路由） | 创建 Tier-1 synthetic JSON（DSC001–005 variants） | **DONE**（本任务 · 8 files · CNINFO=0） |
| **S4** | runner extension approval | 实现 `--shareholder-change-first-slice` · dry-run → Tier-2 planned_snapshots | **blocked** · runner 未实现 |
| **S5** | explicit live approval | CNINFO ≤20 → live_snapshots · outcome ledger · gate 提议 `PASS_WITH_CAVEAT` | **blocked** · live 未批 |

**S3/S4/S5 均需独立人工批准短语。** 本包 **不** 将组件批准延伸为 live/runner 自动授权。

---

## 14. Summary Block

```text
task_id = D-GEN-20260714-06
phase = shareholder_change_first_slice_approval_package_20260714
component = shareholder_change
universe = DSC001-DSC005 locked
anchor = tdate=2026-07-03 type=inc
validation_rules = VR-001 to VR-042 cross-ref (read-only)
tier0 = DC005.json + DLC006 calibrated row (cite only)
tier1_planned = fixtures/d_class/shareholder_change_first_slice/
tier2_planned = outputs/validation/cninfo_d_class_shareholder_change_first_slice/
component_gate = COMPONENT_APPROVED (post AQ-D-SC)
first_slice_live_gate = NOT_APPROVED
cninfo_calls = 0
verified = false
production_ready = false
```
