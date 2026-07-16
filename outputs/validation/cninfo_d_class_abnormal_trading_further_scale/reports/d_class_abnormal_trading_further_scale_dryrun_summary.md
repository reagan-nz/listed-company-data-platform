# CNINFO D 类 abnormal_trading Further-Scale Dry-run Summary

_生成时间：2026-07-16 02:16:41 UTC_

> **性质：** abnormal_trading further-scale dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **50** |
| planned_ok | **50/50** |
| planned_shared_cninfo_requests | **1** |
| planned_request_budget_total | **50** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData`
- query mode: **single_day_paged**
- shared probe: **sdate=edate=2026-07-02** · page=1 · rows=200
- forbidden sole found anchor: **2026-07-03**
- company filter: **offline secCode**

## Gates

```text
d_class_abnormal_trading_further_scale_runner_extension_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_further_scale_live_path_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_further_scale_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance threshold: ≥40/50 acceptable → PASS_WITH_CAVEAT**

