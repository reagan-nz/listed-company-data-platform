# CNINFO D 类 equity_pledge First-Slice — Approval Summary

_生成时间：2026-07-10_

> **性质：** 离线 approval package 摘要 · **CNINFO calls = 0** · **无 live** · **NOT APPROVED for live**

---

## Executive Summary

D-class **equity_pledge** first-slice approval package prepared offline after human component approval and next-component planning.

| 项 | 值 |
|----|-----|
| component | `equity_pledge` |
| endpoint | `data20/equityPledge/list` |
| query mode | `tdate_daily` |
| anchor `tdate` | **2026-07-03**（全宇宙共享 · 离线固定） |
| universe draft | **5** rows（DEP001–DEP005） |
| request cap (future) | **≤ 20**（planned **~5** · 单 tdate / 案） |
| success criteria (future) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| human component approval | **yes**（exact phrase received） |
| approval_status | **NOT_APPROVED** |
| approved_for_live | **false** |
| approved_for_runner | **false** |

---

## Why equity_pledge

- Era D next-component planning primary recommendation（post RSU commit **`aa087b5`**）
- Human-approved component choice（2026-07-10）
- Phase1 DLC005 **acceptable · empty_but_valid**（688981）
- P0 registry · `equityPledge/list` · single `tdate` endpoint · 实施成本低于 RSU multi-probe
- Orthogonal to all closed slices（margin_trading · disclosure_schedule · block_trade · restricted_shares_unlock · known-event）

---

## Universe Draft

| case_id | company_code | company_name | market | expected_behavior |
|---------|--------------|--------------|--------|-------------------|
| DEP001 | 688981 | 中芯国际 | star | empty_but_valid（DLC005-style control） |
| DEP002 | 000895 | 双汇发展 | szse_main | captured_normal_or_empty_but_valid |
| DEP003 | 600000 | 浦发银行 | sse_main | captured_normal_or_empty_but_valid |
| DEP004 | 002415 | 海康威视 | szse_main | captured_normal_or_needs_review |
| DEP005 | 601988 | 中国银行 | sse_main | captured_normal_or_empty_but_valid |

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
| restricted_shares_unlock | `PASS_WITH_CAVEAT` · **NOT verified** | `aa087b5`（**NOT pushed**） |

- **No** DLC003R / DLC006R rerun
- **No** disclosure→captured_normal promotion
- **No** RSU / block_trade verified claim

---

## Gates

```text
d_class_equity_pledge_first_slice_approval_gate = READY_FOR_APPROVAL
d_class_equity_pledge_next_component_planning_gate = PASS_WITH_CAVEAT
d_class_restricted_shares_unlock_first_slice_commit_gate = PASS_WITH_CAVEAT
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
| runner extension implemented | **yes**（dry-run only · live stub） |
| commit / push | **no** |

---

## Artifacts

| 文档 | 路径 |
|------|------|
| first-slice plan | [cninfo_d_class_equity_pledge_first_slice_plan.md](../plans/cninfo_d_class_equity_pledge_first_slice_plan.md) |
| universe draft | [cninfo_d_class_equity_pledge_first_slice_universe_draft.csv](cninfo_d_class_equity_pledge_first_slice_universe_draft.csv) |
| approval checklist | [cninfo_d_class_equity_pledge_first_slice_approval_checklist.md](cninfo_d_class_equity_pledge_first_slice_approval_checklist.md) |
| command draft | [cninfo_d_class_equity_pledge_first_slice_command_draft.md](../plans/cninfo_d_class_equity_pledge_first_slice_command_draft.md) |
| next step | [cninfo_d_class_equity_pledge_first_slice_next_step_recommendation.md](cninfo_d_class_equity_pledge_first_slice_next_step_recommendation.md) |

---

## Next Recommended D-Class Task

**equity_pledge first-slice live-path implementation**（offline · mock only · **无 CNINFO**）
