# CNINFO D 类 restricted_shares_unlock First-Slice — Approval Summary

_生成时间：2026-07-10_

> **性质：** 离线 approval package 摘要 · **CNINFO calls = 0** · **无 live** · **NOT APPROVED for live**

---

## Executive Summary

D-class **restricted_shares_unlock** first-slice approval package prepared offline after human component approval and Era D planning refresh.

| 项 | 值 |
|----|-----|
| component | `restricted_shares_unlock` |
| endpoint | `data20/liftBan/detail` |
| query mode | `tdate_daily` |
| anchor `tdate` | **2026-06-08**（全宇宙共享 · 离线固定） |
| universe draft | **5** rows（DRU001–DRU005） |
| request cap (future) | **≤ 20**（planned **~5–20** · multi-probe） |
| success criteria (future) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| human component approval | **yes**（exact phrase received） |
| approval_status | **NOT_APPROVED** |
| approved_for_live | **false** |
| approved_for_runner | **false** |

---

## Why restricted_shares_unlock

- Era D planning refresh primary recommendation
- Human-approved component choice（2026-07-10）
- Phase1 DLC003 **acceptable · empty_but_valid**（300009）
- P0 registry · `liftBan/detail` · multi-probe anchor logic exists in base runner
- Orthogonal to closed margin_trading（`116f875`）· disclosure_schedule（`d37ce0a`）· block_trade（`403472d` · **NOT verified**）

---

## Universe Draft

| case_id | company_code | company_name | expected_behavior |
|---------|--------------|--------------|-------------------|
| DRU001 | 300009 | 安科生物 | empty_but_valid（DLC003-style control） |
| DRU002 | 000895 | 双汇发展 | captured_normal_or_empty_but_valid |
| DRU003 | 600000 | 浦发银行 | captured_normal_or_empty_but_valid |
| DRU004 | 002415 | 海康威视 | captured_normal_or_needs_review |
| DRU005 | 688981 | 中芯国际 | captured_normal_or_empty_but_valid |

**Expected behavior mix：** 1 `empty_but_valid` · 3 `captured_normal_or_empty_but_valid` · 1 `captured_normal_or_needs_review` · **0** sole `captured_normal_candidate`

**Excluded as primary cases：** **688671** · **301259**

---

## Closed Tracks (frozen)

| Track | Gate | Commit |
|-------|------|--------|
| known-event | `PASS_WITH_CAVEAT` | `389cd9c` |
| margin_trading | `PASS_WITH_CAVEAT` | `116f875` |
| disclosure_schedule | `PASS_WITH_CAVEAT` | `d37ce0a`（DDS004 caveat retained） |
| block_trade | `PASS_WITH_CAVEAT` · **NOT verified** | `403472d`（**NOT pushed**） |

- **No** DLC003R / DLC006R rerun
- **No** disclosure→captured_normal promotion

---

## Gates

```text
d_class_restricted_shares_unlock_first_slice_approval_gate = READY_FOR_APPROVAL
d_class_erad_next_component_planning_refresh_gate = PASS_WITH_CAVEAT
d_class_margin_trading_first_slice_closure_gate = PASS_WITH_CAVEAT
d_class_disclosure_schedule_first_slice_closure_gate = PASS_WITH_CAVEAT
d_class_block_trade_first_slice_closure_gate = PASS_WITH_CAVEAT
d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT
```

**NOT PASS live** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## Safety Confirmations

| 项 | 状态 |
|----|------|
| CNINFO calls | **0** |
| live | **no** |
| runner extension implemented | **yes**（dry-run only） |
| commit / push | **no** |

---

## Artifacts

| 文档 | 路径 |
|------|------|
| first-slice plan | [cninfo_d_class_restricted_shares_unlock_first_slice_plan.md](../plans/cninfo_d_class_restricted_shares_unlock_first_slice_plan.md) |
| universe draft | [cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv](cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv) |
| approval checklist | [cninfo_d_class_restricted_shares_unlock_first_slice_approval_checklist.md](cninfo_d_class_restricted_shares_unlock_first_slice_approval_checklist.md) |
| command draft | [cninfo_d_class_restricted_shares_unlock_first_slice_command_draft.md](../plans/cninfo_d_class_restricted_shares_unlock_first_slice_command_draft.md) |

---

## Next Recommended D-Class Task

**Human approve isolated live** with exact phrase（see [next-step recommendation](cninfo_d_class_restricted_shares_unlock_first_slice_next_step_recommendation.md)）
