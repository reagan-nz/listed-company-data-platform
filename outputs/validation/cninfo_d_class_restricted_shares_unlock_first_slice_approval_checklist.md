# CNINFO D 类 restricted_shares_unlock First-Slice — Approval Checklist

_生成时间：2026-07-10_

> **approval_status = NOT_APPROVED** · **approved_for_live = false** · **approved_for_runner = false** · **不是 verified** · **不是 production_ready**

---

## 1. Prior Planning Complete

- [x] Era D next-component planning refresh reviewed → [refresh summary](cninfo_d_class_erad_next_component_planning_refresh_summary.md)
- [x] human component approval phrase received：**I approve D-class restricted_shares_unlock as the next Era D component.**
- [x] primary recommendation = **restricted_shares_unlock**
- [x] `d_class_erad_next_component_planning_refresh_gate = PASS_WITH_CAVEAT`（human chose RSU）
- [x] Phase1 DLC003 evidence reviewed：**acceptable · empty_but_valid · 0 rows**（300009）
- [x] known-event / margin_trading / disclosure_schedule / block_trade tracks remain **closed**
- [x] block_trade commit **`403472d`** · gate **`PASS_WITH_CAVEAT`** · **NOT verified** · **NOT pushed**

---

## 2. First-Slice Universe

- [x] universe contains exactly **5 rows** → [universe draft](cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv)
- [x] case_id scheme **DRU001–DRU005**
- [x] component = **restricted_shares_unlock** on all rows
- [x] `first_slice_include = yes` on all rows
- [x] **688671**（DLC003R）excluded as primary case
- [x] **301259**（DLC006R）excluded as primary case
- [x] DRU001 references DLC003-style company **300009** with **distinct** case_id
- [x] markets covered：chinext ×1 · szse_main ×2 · sse_main ×1 · star ×1
- [x] single anchor `tdate = 2026-06-08` on all rows（离线文档化 · 非 CNINFO 探测）
- [x] expected_behavior mix：**1** `empty_but_valid` · **0** sole `captured_normal_candidate` · **3** `captured_normal_or_empty_but_valid` · **1** `captured_normal_or_needs_review`

---

## 3. Anchor Date & Request Cap

- [x] query mode = **tdate_daily**
- [x] per-case request budget **≤ 4**（multi-probe · 未来规划值）
- [x] total request cap **≤ 20**
- [x] planned requests **~5–20**
- [x] success criteria **≥ 3/5** acceptable → `PASS_WITH_CAVEAT`
- [x] `empty_but_valid` documented as legitimate outcome
- [x] block_trade DBT002 lesson applied：no sole `captured_normal_candidate` on sparse anchor

---

## 4. Endpoint & Scope

- [x] endpoint = `restricted_shares_unlock/liftBan/detail`（`https://www.cninfo.com.cn/data20/liftBan/detail`）
- [x] layer = `company_event`（metadata / structured-table only）
- [x] allowed outcomes：`found` · `empty_but_valid` · `needs_review`

---

## 5. Safety & Frozen Tracks

- [x] no DLC003R / DLC006R rerun
- [x] no reopen known-event replacement validation
- [x] no margin_trading expansion（commit **`116f875`** closed）
- [x] no disclosure_schedule expansion（commit **`d37ce0a`** closed · DDS004 caveat retained）
- [x] no block_trade expansion（commit **`403472d`** closed · DBT002 caveat · **NOT verified**）
- [x] no disclosure→captured_normal promotion
- [x] no PDF download / parse / OCR / extraction
- [x] no DB / MinIO / RAG
- [x] no verified / production_ready / testing_stable_sample
- [x] `d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT`（保持）
- [x] `d_class_margin_trading_first_slice_closure_gate = PASS_WITH_CAVEAT`（保持）
- [x] `d_class_disclosure_schedule_first_slice_closure_gate = PASS_WITH_CAVEAT`（保持）
- [x] `d_class_block_trade_first_slice_closure_gate = PASS_WITH_CAVEAT`（保持）

---

## 6. Package Artifacts

- [x] [first-slice plan](../plans/cninfo_d_class_restricted_shares_unlock_first_slice_plan.md) prepared
- [x] [command draft](../plans/cninfo_d_class_restricted_shares_unlock_first_slice_command_draft.md) prepared（**NOT APPROVED** · **DO NOT RUN**）
- [x] [approval summary](cninfo_d_class_restricted_shares_unlock_first_slice_approval_summary.md) prepared
- [x] CNINFO calls during package prep = **0**
- [x] runner first-slice mode extension implemented → [extension summary](cninfo_d_class_restricted_shares_unlock_first_slice_runner_extension_summary.md)
- [x] dry-run **5/5 planned_ok** · planned **20** · CNINFO **0**
- [x] live-path offline implementation → [live-path summary](cninfo_d_class_restricted_shares_unlock_first_slice_live_path_summary.md) · tests **22/22 PASS**（mock only）
- [x] isolated live execution = **yes**（§10）

---

## 7. Approval Status

| 项 | 值 |
|----|-----|
| component choice | **human-approved** |
| approval_status | **APPROVED_FOR_THIS_LIVE_ONLY** |
| approved_for_live | **true**（isolated live 2026-07-10） |
| approved_for_runner | **false** |
| approval_gate | `d_class_restricted_shares_unlock_first_slice_approval_gate = READY_FOR_APPROVAL` |
| execution_gate | `d_class_restricted_shares_unlock_first_slice_execution_gate = PASS_WITH_CAVEAT` |

---

## 8. Isolated Live Execution（2026-07-10）

- [x] human live approval phrase：**I approve D-class restricted_shares_unlock first-slice live validation.**
- [x] CNINFO requests = **15**（cap ≤ **20**）
- [x] acceptable = **5/5**
- [x] sparse-day empty **5/5** · no `found` samples
- [x] [execution summary](cninfo_d_class_restricted_shares_unlock_first_slice_live_execution_summary.md)
- [x] [outcome ledger](cninfo_d_class_restricted_shares_unlock_first_slice_per_case_outcome_ledger.csv)

---

## 9. Next Step

**restricted_shares_unlock first-slice closure / commit-boundary package**（offline · CNINFO **0** · **无 commit**）
