# CNINFO D 类 block_trade First-Slice — Approval Summary

_生成时间：2026-07-10_

> **性质：** 离线 approval package 摘要 · **CNINFO calls = 0** · **无 live** · **NOT APPROVED**

---

## Executive Summary

D-class **block_trade** first-slice approval package prepared offline after Era D next-component planning (`block_trade` primary).

| 项 | 值 |
|----|-----|
| component | `block_trade` |
| endpoint | `data20/ints/statistics` |
| query mode | `tdate_daily` |
| anchor `tdate` | **2026-07-03**（全宇宙共享 · 离线固定） |
| universe draft | **5** rows（DBT001–DBT005） |
| request cap (future) | **≤ 20**（planned **~5**） |
| success criteria (future) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| approval_status | **NOT_APPROVED** |
| approved_for_live | **false** |

---

## Why block_trade

- Era D primary recommendation from [next-component planning](../plans/cninfo_d_class_erad_next_component_planning.md)
- Phase1 DLC002 **acceptable · empty_but_valid**（601988）
- Orthogonal to closed margin_trading（`116f875`）and disclosure_schedule（`d37ce0a`）
- ~1 CNINFO/case · low implementation cost vs restricted_shares_unlock

---

## Universe Draft

| case_id | company_code | company_name | expected_behavior |
|---------|--------------|--------------|-------------------|
| DBT001 | 601988 | 中国银行 | empty_but_valid（DLC002-style control） |
| DBT002 | 000895 | 双汇发展 | captured_normal_candidate |
| DBT003 | 600000 | 浦发银行 | captured_normal_or_empty_but_valid |
| DBT004 | 002415 | 海康威视 | captured_normal_or_empty_but_valid |
| DBT005 | 688981 | 中芯国际 | captured_normal_or_empty_but_valid |

**Excluded as primary cases：** **688671** · **301259**

---

## Closed Tracks (frozen)

| Track | Gate | Commit |
|-------|------|--------|
| known-event | `PASS_WITH_CAVEAT` | `389cd9c` |
| margin_trading | `PASS_WITH_CAVEAT` | `116f875` |
| disclosure_schedule | `PASS_WITH_CAVEAT` | `d37ce0a`（DDS004 caveat retained） |

- **No** DLC003R / DLC006R rerun
- **No** disclosure→captured_normal promotion

---

## Gates

```text
d_class_block_trade_first_slice_approval_gate = READY_FOR_APPROVAL
d_class_erad_next_component_planning_gate = READY_FOR_APPROVAL
d_class_margin_trading_first_slice_closure_gate = PASS_WITH_CAVEAT
d_class_disclosure_schedule_first_slice_closure_gate = PASS_WITH_CAVEAT
d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## Safety Confirmations

| 项 | 状态 |
|----|------|
| CNINFO calls | **0** |
| live | **no** |
| runner extension implemented | **no** |
| commit / push | **no** |

---

## Artifacts

| 文档 | 路径 |
|------|------|
| first-slice plan | [cninfo_d_class_block_trade_first_slice_plan.md](../plans/cninfo_d_class_block_trade_first_slice_plan.md) |
| universe draft | [cninfo_d_class_block_trade_first_slice_universe_draft.csv](cninfo_d_class_block_trade_first_slice_universe_draft.csv) |
| approval checklist | [cninfo_d_class_block_trade_first_slice_approval_checklist.md](cninfo_d_class_block_trade_first_slice_approval_checklist.md) |
| command draft | [cninfo_d_class_block_trade_first_slice_command_draft.md](../plans/cninfo_d_class_block_trade_first_slice_command_draft.md) |

---

## Next Recommended D-Class Task

**block_trade first-slice runner extension + dry-run**（offline · CNINFO **0** · **无 live**）
