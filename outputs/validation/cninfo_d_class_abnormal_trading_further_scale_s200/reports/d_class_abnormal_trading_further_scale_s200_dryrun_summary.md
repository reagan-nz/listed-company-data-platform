# CNINFO D 类 abnormal_trading Further-Scale S200 Dry-run Summary

_生成时间：2026-07-16 02:27:11 UTC_

> **性质：** abnormal_trading further-scale S200 dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **200** |
| planned_ok | **200/200** |
| planned_shared_cninfo_requests | **2**（按日共享） |
| planned_request_budget_total | **200** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData`
- query mode: **single_day_paged**
- compose: primary=`2026-07-02` + adjacent=`2026-07-01`
- shared probes: **2** day(s) · page=1 · rows=300
- forbidden sole found anchor: **2026-07-03**
- company filter: **offline secCode**

## Gates

```text
d_class_abnormal_trading_further_scale_s200_dryrun_gate = PASS_OFFLINE
d_class_abnormal_trading_further_scale_s200_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance threshold: ≥190/200 acceptable (≥95%) → PASS_WITH_CAVEAT / excellence candidate**

