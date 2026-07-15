# CNINFO A 类 Era D Next-Scale Slice2 S1 — Live 执行摘要

_生成时间：2026-07-15 09:11:03 UTC_

> **性质：** Era D A-class next-scale slice2 S1 live metadata validation · **无 PDF** · **不是 verified**

## Counts

| 指标 | 值 |
|------|-----|
| mode | erad_a_scale_500_slice2_live |
| universe size | 50 |
| expected case count | 50 |
| acceptable | 50 |
| failed | 0 |
| needs_review | 0 |
| CNINFO requests | 110 (cap ≤ 240) |
| matching_logic | **v2** |
| execution gate | `PASS_WITH_CAVEAT` |
| acceptance threshold | ≥45/50 → PASS_WITH_CAVEAT |

## Isolation

Writes **only** under slice2 S1 root; **does not mutate** scale-200 / slice1 / failed-retry / Phase 3.

## Safety

- metadata only: **yes**
- output isolation: `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s2`
- verified: **no**
- production_ready: **no**

## Gate

```text
a_class_erad_next_scale_slice2_s1_live_path_gate = READY_FOR_APPROVAL
a_class_erad_next_scale_slice2_s1_execution_gate = PASS_WITH_CAVEAT
```

- acceptance threshold: **≥ 45/50** → PASS_WITH_CAVEAT

**不是 PASS** · **不是 verified** · **不是 production_ready**
