# CNINFO A 类 Era D ~200 Metadata Expansion — Dry-run 摘要

_生成时间：2026-07-10 07:07:34 UTC_

> **性质：** Era D runner dry-run · **无 CNINFO** · **无 live** · **无 PDF**

## Counts

| 指标 | 值 |
|------|-----|
| mode | erad_a_scale_200_dry_run |
| universe size | 200 |
| planned_ok | 200 |
| retained_phase3 | 50 |
| new_erad | 150 |
| report-type mix | annual_report=140 / quarterly_report_q1=20 / quarterly_report_q3=20 / semi_annual_report=20 |
| planned_requests_total | 400 (cap ≤ 480) |
| matching_logic | **v2** |
| CNINFO calls | **0** |

## Retained cohort note

Retained 50 cases reference Phase 3 post-retry effective lineage via `phase3_source_case_id`. Dry-run writes **only** under Era D root; **does not rewrite** Phase 3 expansion or A3M017 retry production roots.

## Safety

- metadata only: **yes**
- output isolation: `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_a_class_erad_scale_200`
- Phase 1/2/Phase3/A3M017/B/C/D roots untouched: **yes**
- verified: **no**
- production_ready: **no**

## Gate

```text
a_class_erad_scale_200_runner_extension_gate = READY_FOR_APPROVAL
```

**不是 PASS** · **不是 live_ready** · **不是 verified** · **Approval status: NOT_APPROVED**
