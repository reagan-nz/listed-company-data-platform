# CNINFO D 类 abnormal_trading Further-Scale S1000 Dry-run Summary

_生成时间：2026-07-16 02:36:56 UTC_

> **性质：** abnormal_trading further-scale S1000 dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **1000** |
| planned_ok | **1000/1000** |
| planned_shared_cninfo_days | **14**（按日多页共享） |
| planned_request_budget_total | **1000** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s1000_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData`
- query mode: **single_day_paged**（multi-page per day）
- compose days planned: `2026-07-15, 2026-07-14, 2026-07-13, 2026-07-10, 2026-07-09, 2026-07-08, 2026-07-07, 2026-07-06, 2026-07-02, 2026-07-01, 2026-06-30, 2026-06-26, 2026-06-25, 2026-06-24`
- shared probes: **14** day(s) · rows=300 · multipage
- forbidden sole found anchor: **2026-07-03**
- company filter: **offline secCode**

## Gates

```text
d_class_abnormal_trading_further_scale_s1000_dryrun_gate = PASS_OFFLINE
d_class_abnormal_trading_further_scale_s1000_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance threshold: ≥950/1000 acceptable (≥95%) → PASS_WITH_CAVEAT / excellence candidate**

