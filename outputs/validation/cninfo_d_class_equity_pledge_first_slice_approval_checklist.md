# CNINFO D 类 equity_pledge First-Slice — Approval Checklist

_生成时间：2026-07-10_

> **approval_status = NOT_APPROVED** · **approved_for_live = false** · **approved_for_runner = false** · **不是 verified** · **不是 production_ready**

---

## 1. Prior Planning Complete

- [x] equity_pledge next-component planning reviewed → [planning summary](cninfo_d_class_equity_pledge_next_component_planning_summary.md)
- [x] human component approval phrase received：**I approve D-class equity_pledge as the next Era D component.**
- [x] primary recommendation = **equity_pledge**
- [x] runner-up = **shareholder_change**
- [x] `d_class_equity_pledge_next_component_planning_gate = PASS_WITH_CAVEAT`（human chose equity_pledge）
- [x] Phase1 DLC005 evidence reviewed：**acceptable · empty_but_valid · 0 rows**（688981）
- [x] known-event / margin_trading / disclosure_schedule / block_trade / restricted_shares_unlock tracks remain **closed**
- [x] restricted_shares_unlock commit **`aa087b5`** · gate **`PASS_WITH_CAVEAT`** · **NOT verified** · **NOT pushed**
- [x] block_trade commit **`403472d`** · gate **`PASS_WITH_CAVEAT`** · **NOT verified** · **NOT pushed**

---

## 2. First-Slice Universe

- [x] universe contains exactly **5 rows** → [universe draft](cninfo_d_class_equity_pledge_first_slice_universe_draft.csv)
- [x] case_id scheme **DEP001–DEP005**
- [x] component = **equity_pledge** on all rows
- [x] `first_slice_include = yes` on all rows
- [x] **688671**（DLC003R）excluded as primary case
- [x] **301259**（DLC006R）excluded as primary case
- [x] DEP001 references DLC005-style company **688981** with **distinct** case_id
- [x] markets covered：star ×1 · szse_main ×2 · sse_main ×2
- [x] single anchor `tdate = 2026-07-03` on all rows（离线文档化 · 非 CNINFO 探测）
- [x] expected_behavior mix：**1** `empty_but_valid` · **0** sole `captured_normal_candidate` · **3** `captured_normal_or_empty_but_valid` · **1** `captured_normal_or_needs_review`

---

## 3. Anchor Date & Request Cap

- [x] query mode = **tdate_daily**
- [x] per-case request budget **≤ 4**（单 tdate 预期 1 · 未来规划值）
- [x] total request cap **≤ 20**
- [x] planned requests **~5**
- [x] success criteria **≥ 3/5** acceptable → `PASS_WITH_CAVEAT`
- [x] `empty_but_valid` documented as legitimate outcome
- [x] RSU / block_trade sparse-day lessons applied：no sole `captured_normal_candidate` on sparse anchor

---

## 4. Endpoint & Scope

- [x] endpoint = `equity_pledge/equityPledge/list`（`https://www.cninfo.com.cn/data20/equityPledge/list`）
- [x] layer = `company_event`（metadata / structured-table only）
- [x] allowed outcomes：`found` · `empty_but_valid` · `needs_review`

---

## 5. Safety & Frozen Tracks

- [x] no DLC003R / DLC006R rerun
- [x] no reopen known-event replacement validation
- [x] no margin_trading expansion（commit **`116f875`** closed）
- [x] no disclosure_schedule expansion（commit **`d37ce0a`** closed · DDS004 caveat retained）
- [x] no block_trade expansion（commit **`403472d`** closed · DBT002 caveat · **NOT verified**）
- [x] no restricted_shares_unlock expansion（commit **`aa087b5`** closed · sparse-day **5/5** · **NOT verified**）
- [x] no disclosure→captured_normal promotion
- [x] no PDF download / parse / OCR / extraction
- [x] no DB / MinIO / RAG
- [x] no verified / production_ready / testing_stable_sample
- [x] `d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT`（保持）
- [x] `d_class_margin_trading_first_slice_closure_gate = PASS_WITH_CAVEAT`（保持）
- [x] `d_class_disclosure_schedule_first_slice_closure_gate = PASS_WITH_CAVEAT`（保持）
- [x] `d_class_block_trade_first_slice_closure_gate = PASS_WITH_CAVEAT`（保持）
- [x] `d_class_restricted_shares_unlock_first_slice_closure_gate = PASS_WITH_CAVEAT`（保持）

---

## 6. Package Artifacts

- [x] [first-slice plan](../plans/cninfo_d_class_equity_pledge_first_slice_plan.md) prepared
- [x] [command draft](../plans/cninfo_d_class_equity_pledge_first_slice_command_draft.md) prepared（**NOT APPROVED** · **DO NOT RUN**）
- [x] [approval summary](cninfo_d_class_equity_pledge_first_slice_approval_summary.md) prepared
- [x] CNINFO calls during package prep = **0**
- [x] runner first-slice mode extension implemented → [extension summary](cninfo_d_class_equity_pledge_first_slice_runner_extension_summary.md)
- [x] dry-run **5/5 planned_ok** · planned **5** · CNINFO **0**
- [x] tests **20/20 PASS**
- [x] live-path offline implementation → [live-path summary](cninfo_d_class_equity_pledge_first_slice_live_path_summary.md) · tests **22/22** · mock only
- [x] isolated live execution → [live execution summary](cninfo_d_class_equity_pledge_first_slice_live_execution_summary.md) · CNINFO **5** · acceptable **4/5**
- [x] closure review complete → [closure summary](cninfo_d_class_equity_pledge_first_slice_closure_summary.md) · gate **`PASS_WITH_CAVEAT`**
- [x] commit boundary review complete → [boundary summary](cninfo_d_class_equity_pledge_first_slice_commit_boundary_summary.md) · gate **`READY_FOR_COMMIT_REVIEW`**
- [ ] explicit-path commit → **no**

---

## 7. Approval Status

| 项 | 值 |
|----|-----|
| component choice | **human-approved** |
| approval_status | **APPROVED_FOR_THIS_LIVE_ONLY** |
| approved_for_live | **true** |
| approved_for_runner | **false** |
| approval_gate | `d_class_equity_pledge_first_slice_approval_gate = READY_FOR_APPROVAL` |
| runner_extension_gate | `d_class_equity_pledge_first_slice_runner_extension_gate = READY_FOR_APPROVAL` |
| live_path_gate | `d_class_equity_pledge_first_slice_live_path_gate = READY_FOR_APPROVAL` |
| execution_gate | `d_class_equity_pledge_first_slice_execution_gate = PASS_WITH_CAVEAT` |
| closure_gate | `d_class_equity_pledge_first_slice_closure_gate = PASS_WITH_CAVEAT` |
| commit_boundary_gate | `d_class_equity_pledge_first_slice_commit_boundary_gate = READY_FOR_COMMIT_REVIEW` |
| approval_status_for_commit | **NOT_APPROVED** |

---

## 8. Next Step

**Human approve explicit-path commit** with exact phrase:

> I approve D-class equity_pledge first-slice explicit-path commit.
