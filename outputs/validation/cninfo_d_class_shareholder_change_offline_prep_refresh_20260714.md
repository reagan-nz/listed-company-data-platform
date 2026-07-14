# CNINFO D 类 shareholder_change — Offline Prep Refresh

_生成时间：2026-07-14_

> **性质：** offline component preparation refresh only · **CNINFO calls = 0** · **无 live** · **无 runner execute** · **无 claim approved** · **无 commit** · **无 push**
>
> **边界：** `READY_FOR_APPROVAL` ≠ **approved** · disclosure ≠ structured capture · **不是 verified** · **不是 production_ready**

---

## 1. Component Goal（toward full-market shareholder/capital coverage）

| 项 | 内容 |
|----|------|
| Track | D-class · Era D company_event slice chain |
| Mission lane | **full-market shareholder/capital**（见 `plans/controller_execution_cycle_policy_v2.md` Track D 定义） |
| Component | `shareholder_change`（股东增减持） |
| Source layer | `company_event` |
| Target logical table | `d_company_event`（metadata / structured-table only） |
| Endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail`（CNINFO 注册拼写 **`shareholeder`** · **不修正**） |
| Query mode（first-slice sketch） | `type=inc` + shared `tdate` |
| Coverage path | **first-slice（5-case sketch）** → approval package → runner extension → bounded dry-run/live → closure · **本包仅刷新 offline prep** · **不 claim 全市场覆盖增益** |
| Prior slice context | equity_pledge historically committed **`85abad0`** · gate **`PASS_WITH_CAVEAT`** · DEP004 caveat retained · **NOT verified** · **NOT pushed** · **不得重开** |
| Primary rank | post-`85abad0` Era D next-component **primary**（runner-up: `executive_shareholding`） |

**全市场方向陈述：** shareholder_change 是 D 轨「股东/资本类公司事件」覆盖链的下一顺位组件；registry/schema 已就绪，DLC006（000550）提供 Phase1 tiny-live 先例口径。当前阶段目标为 **完成组件级人工批准前的 offline 准备收口**，而非执行采集或宣称 structured capture 已覆盖全市场。

---

## 2. Current Gate

```text
d_class_shareholder_change_next_component_planning_gate = READY_FOR_APPROVAL
approval_queue_id = AQ-D-SC
approval_queue_status = WAITING_APPROVAL
shareholder_change_component_approved = false
READY_FOR_APPROVAL_neq_approved = true
```

| 判定 | 状态 |
|------|------|
| planning package | **PRESENT**（见第 3 节清单） |
| planning gate | **`READY_FOR_APPROVAL`** |
| human Level-2 component approval | **NOT approved**（exact phrase **未**落档为 granted） |
| first-slice approval / runner / live | **NOT approved** · **未实现** |
| verified / production_ready | **no** |

**强制语义：** `READY_FOR_APPROVAL` ≠ approved ≠ live_approved ≠ verified。

---

## 3. Planning Artifact Inventory

| # | 路径 | 类型 | 说明 |
|---|------|------|------|
| 1 | `plans/cninfo_d_class_shareholder_change_next_component_planning.md` | plan | next-component 主规划 · primary 确认 · sparse-day 教训 · DLC006R 政策 |
| 2 | `plans/cninfo_d_class_shareholder_change_first_slice_plan_draft.md` | plan | first-slice 草案 · endpoint · universe · success criteria |
| 3 | `outputs/validation/cninfo_d_class_shareholder_change_next_component_planning_summary.md` | validation | planning 摘要 |
| 4 | `outputs/validation/cninfo_d_class_shareholder_change_next_component_recommendation.md` | validation | primary / runner-up 推荐 |
| 5 | `outputs/validation/cninfo_d_class_shareholder_change_next_component_next_step_recommendation.md` | validation | 下一步推荐（组件批准 → first-slice approval package） |
| 6 | `outputs/validation/cninfo_d_class_shareholder_change_next_component_candidate_matrix.csv` | validation | 候选组件矩阵 · rank=1 |
| 7 | `outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_draft_sketch.csv` | validation | DSC001–DSC005 universe sketch |
| 8 | `outputs/validation/cninfo_d_class_autonomous_batch_v1_shareholder_change_gate.md` | validation | autonomous batch v1 gate 文档 · HEAD **`3b0c7ce`** 口径 |
| 9 | `config/cninfo_d_class_source_registry_draft.yaml` | config | `shareholder_change` registry · `default_params.type=inc` · `tdate=2026-07-03` |
| 10 | `outputs/validation/controller_approval_queue_20260714.md` | controller | AQ-D-SC · **WAITING_APPROVAL** |
| 11 | `outputs/validation/cninfo_d_class_shareholder_change_offline_prep_refresh_20260714.md` | validation | **本文件** · offline prep refresh |
| 12 | `outputs/validation/cninfo_d_class_shareholder_change_offline_prep_checklist_20260714.csv` | validation | offline prep checklist（item/status/evidence） |

---

## 4. Readiness Checklist for Human Level-2 Approval

人工 Level-2 决策（AQ-D-SC）前，Controller / human 应确认以下项。**本包不将任何项标记为已批准。**

### 4.1 Human must say / decide

| # | 决策项 | 状态 | 说明 |
|---|--------|------|------|
| H1 | **组件级批准短语** | **pending** | 人工须落档 exact phrase（见 4.2）· Controller **不得**代为 grant |
| H2 | 确认 `shareholder_change` 为 Era D **primary** next component | **pending** | 规划已推荐 · 须人工确认 |
| H3 | 接受 first-slice sketch 参数（5-case · DSC001–DSC005 · `tdate=2026-07-03` · `type=inc`） | **pending** | sketch only · formal universe 锁定于后续 approval package |
| H4 | 接受 sparse-day / expectation mix 政策 | **pending** | `empty_but_valid` 合法 · 禁止 sole `captured_normal_candidate` · DEP004/DBT002 教训 |
| H5 | 确认 DLC006R / 301259 **永久排除** · known-event **不重开** | **pending** | disclosure ≠ structured capture |
| H6 | 确认 closed tracks **不重开**（equity_pledge **`85abad0`** 等） | **pending** | 见第 6 节 |
| H7 | 明确 **不** 在本决策中授权 runner / live / CNINFO / commit / push | **pending** | 组件批准仅解锁 offline first-slice approval package 链 |

### 4.2 Exact approval phrase（human Level-2 · NOT granted）

> I approve D-class shareholder_change as the next Era D component.

| 项 | 内容 |
|----|------|
| phrase status | **NOT recorded as granted** |
| does not authorize | runner · live · CNINFO · commit · push · verified · production_ready |
| unlocks（若人工落档） | offline **shareholder_change first-slice approval package** only（universe formalize · checklist · command draft · **无 CNINFO**） |

### 4.3 Offline prep already ready（供人工审阅）

| # | 就绪项 | evidence |
|---|--------|----------|
| R1 | next-component planning complete | `plans/cninfo_d_class_shareholder_change_next_component_planning.md` |
| R2 | first-slice plan draft | `plans/cninfo_d_class_shareholder_change_first_slice_plan_draft.md` |
| R3 | candidate matrix rank=1 | `outputs/validation/cninfo_d_class_shareholder_change_next_component_candidate_matrix.csv` |
| R4 | universe sketch DSC001–DSC005 | `outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_draft_sketch.csv` |
| R5 | registry / schema draft | `config/cninfo_d_class_source_registry_draft.yaml` · `shareholder_change` |
| R6 | DLC006（000550）先例口径 documented | planning + first-slice draft · distinct DSC case_id |
| R7 | autonomous batch v1 gate doc | `outputs/validation/cninfo_d_class_autonomous_batch_v1_shareholder_change_gate.md` |
| R8 | approval queue entry AQ-D-SC | `outputs/validation/controller_approval_queue_20260714.md` |
| R9 | offline prep refresh（本包） | 本文件 + checklist CSV |

---

## 5. Blocked Actions Until Approval

在 **H1 组件级批准短语落档之前**，以下动作 **全部禁止**：

| # | 禁止动作 | 原因 |
|---|----------|------|
| B1 | CNINFO 调用 / probe / dry-run / live | 无 live approval · planning gate only |
| B2 | runner 实现或 `--shareholder-change-first-slice` 执行 | 无 runner approval · flag 未实现 |
| B3 | 将 `READY_FOR_APPROVAL` 解读为 approved / PASS / verified | governance 红线 |
| B4 | first-slice formal universe 锁定（approval package） | 须先组件批准 |
| B5 | commit / push / git add / stage | 本任务授权边界 |
| B6 | PROJECT_CONTROL / CURRENT_STATUS / PROJECT_MAP gate flip | 无 Controller 授权 |
| B7 | disclosure → `captured_normal` promotion | DLC006R / evidence boundary |
| B8 | 重开 equity_pledge / known-event / DLC006R / DLC003R | closed tracks |
| B9 | PDF / OCR / extraction / DB / MinIO / RAG | D-class default scope |
| B10 | claim verified / production_ready / testing_stable_sample | evidence owner 非 executor |

**短语落档后仍禁止（须后续分步批准）：** live · CNINFO · runner execute · commit · push · verified。

---

## 6. Closed Tracks（unchanged · 不得重开）

| Track | Commit / Gate | Notes |
|-------|---------------|-------|
| equity_pledge | **`85abad0`** · `PASS_WITH_CAVEAT` | DEP004 caveat · **NOT verified** · **NOT pushed** |
| restricted_shares_unlock | **`aa087b5`** · `PASS_WITH_CAVEAT` | **NOT verified** · **NOT pushed** |
| block_trade | **`403472d`** · `PASS_WITH_CAVEAT` | DBT002 caveat · **NOT verified** · **NOT pushed** |
| margin_trading | **`116f875`** · closed | 不得扩展 |
| disclosure_schedule | **`d37ce0a`** · closed | DDS004 caveat retained |
| known-event / DLC006R | **`389cd9c`** · closed | 301259 excluded · no rerun |

---

## 7. Evidence Boundary（preserve）

```text
disclosure_evidence  ≠  captured_structured_evidence
separate_disclosure_lineage_only  不得  promote  为  captured_normal
DLC006R_closed = true
DLC006R_reopen = forbidden
301259_excluded_from_primary_universe = true
DLC006_000550 = distinct_DSC_precedent_only
```

---

## 8. Safe Offline Prep Completed by This Package

本 refresh 包完成的 **安全 offline 工作**（无 CNINFO · 无 live · 无 runner · 无 gate upgrade）：

| # | 完成项 |
|---|--------|
| P1 | 重述 shareholder_change 朝向 full-market shareholder/capital 的组件目标与 coverage path |
| P2 | 清点并交叉引用现有 planning / validation / gate / registry artifacts（第 3 节） |
| P3 | 编制 human Level-2 approval readiness checklist（第 4 节 · **不 grant 短语**） |
| P4 | 明确 approval 前 blocked actions（第 5 节） |
| P5 | 保留 closed tracks · DLC006R · disclosure boundary 政策 |
| P6 | 产出 structured checklist CSV（`cninfo_d_class_shareholder_change_offline_prep_checklist_20260714.csv`） |
| P7 | 维持 gate = **`READY_FOR_APPROVAL`** / AQ-D-SC = **`WAITING_APPROVAL`** |

**不 claim：** 全市场覆盖百分比增益 · structured capture 完成 · verified · production_ready。

---

## 9. Next Safe Step（after human phrase only）

人工落档组件批准短语后，唯一安全下一步：

**offline shareholder_change first-slice approval package**（formal universe · approval checklist · command draft · **无 CNINFO** · **无 live** · **无 runner**）

---

## 10. Safety Zeros

| 项 | 本包 |
|----|------|
| CNINFO calls | **0** |
| live execution | **no** |
| runner execute | **no** |
| claim approved | **no** |
| PDF / OCR / extraction | **no** |
| DB / MinIO / RAG | **no** |
| commit / push / git add | **no** |
| PROJECT_CONTROL flip | **no** |
| source / tests / runners modified | **no** |
| other tracks affected | **no** |
| verified / production_ready claimed | **no** |

---

## 11. Summary Block

```text
phase = shareholder_change_offline_prep_refresh_20260714
repo_root = listed_company_data_collector (main)
track = D-class
current_gate = d_class_shareholder_change_next_component_planning_gate = READY_FOR_APPROVAL
approval_queue = AQ-D-SC · WAITING_APPROVAL
shareholder_change_approved = false
READY_FOR_APPROVAL_neq_approved = true
required_human_decision = I approve D-class shareholder_change as the next Era D component. (NOT granted)
equity_pledge_lineage = 85abad0 · no_reopen
cninfo_calls = 0
live = no
runner_execute = no
commit = not_performed
push = not_performed
disclosure_equals_structured = false
```
