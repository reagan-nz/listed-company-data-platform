# CNINFO D 类 margin_trading First-Slice — Approval Summary

_生成时间：2026-07-10_

> **性质：** 离线 approval package 摘要 · **CNINFO calls = 0** · **无 live** · **NOT APPROVED**

---

## Executive Summary

D-class **margin_trading** first-slice approval package prepared offline after known-event replacement track closure.

| 项 | 值 |
|----|-----|
| component | `margin_trading` |
| layer | `company_metric_daily` |
| universe draft | **5** rows（DMT001–DMT005） |
| request cap (future) | **≤ 20** |
| success criteria (future) | **≥ 3/5** acceptable |
| approval_status | **NOT_APPROVED** |
| approved_for_live | **false** |

---

## Why margin_trading

- Phase1 DLC001 **acceptable · found · 1 row**
- `company_metric_daily` — 正交于已收口 known-event **event** 轨道
- P0 readiness · registry endpoint `margin_trading/detailList` 已文档化
- base runner 已含 Phase1 path · first-slice extension **后续**

---

## Universe Draft

| case_id | company_code | company_name | market |
|---------|--------------|--------------|--------|
| DMT001 | 000895 | 双汇发展 | szse_main |
| DMT002 | 600000 | 浦发银行 | sse_main |
| DMT003 | 601988 | 中国银行 | sse_main |
| DMT004 | 002415 | 海康威视 | szse_main |
| DMT005 | 688981 | 中芯国际 | star |

**Excluded as primary cases：** **688671**（DLC003R）· **301259**（DLC006R）

---

## Known-Event Track (frozen)

```text
d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT
DLC003R = captured_normal_structured_evidence
DLC006R = accepted_component_gap_with_separate_disclosure_evidence
DLC006R captured_normal_allowed = no
```

- **No DLC003R / DLC006R rerun**
- **No disclosure→captured_normal promotion**
- Track remains **closed with caveat**

---

## Gates

```text
d_class_margin_trading_first_slice_approval_gate = READY_FOR_APPROVAL
d_class_next_component_planning_gate = READY_FOR_HUMAN_DECISION
d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT
d_class_known_event_replacement_push_gate = READY_FOR_HUMAN_DECISION
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## Safety Confirmations

| 项 | 状态 |
|----|------|
| CNINFO calls | **0** |
| live | **0** |
| runner extension implemented | **no** |
| commit / push | **0** |

---

## Artifacts

| 文档 | 路径 |
|------|------|
| first-slice plan | [cninfo_d_class_margin_trading_first_slice_plan.md](../plans/cninfo_d_class_margin_trading_first_slice_plan.md) |
| universe draft | [cninfo_d_class_margin_trading_first_slice_universe_draft.csv](cninfo_d_class_margin_trading_first_slice_universe_draft.csv) |
| approval checklist | [cninfo_d_class_margin_trading_first_slice_approval_checklist.md](cninfo_d_class_margin_trading_first_slice_approval_checklist.md) |
| command draft | [cninfo_d_class_margin_trading_first_slice_command_draft.md](../plans/cninfo_d_class_margin_trading_first_slice_command_draft.md) |

---

## Next Recommended D-Class Task

1. 人工决策是否批准 `d_class_margin_trading_first_slice_approval_gate`
2. 若批准 → **runner first-slice extension design + dry-run**（offline first · **无 live**）
3. **不** reopen known-event track · **不** DLC006R rerun
