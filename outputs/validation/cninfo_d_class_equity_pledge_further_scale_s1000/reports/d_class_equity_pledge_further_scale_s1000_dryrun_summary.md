# CNINFO D 类 equity_pledge Further-Scale S1000 Dry-run Summary

_生成时间：2026-07-16 03:40:54 UTC_

> **性质：** equity_pledge further-scale s1000 dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **1000** |
| planned_ok | **1000/1000** |
| planned_shared_cninfo_requests | **10** |
| planned_request_budget_total | **1000** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_equity_pledge_further_scale_s1000_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data20/equityPledge/list`
- query mode: **tdate_daily_multi_day_union**
- shared probe: **tdate_daily** · **2026-06-30 + 2026-07-01 + 2026-07-04 + 2026-07-07 + 2026-07-08 + 2026-07-09 + 2026-07-10 + 2026-07-11 + 2026-07-14 + 2026-07-15**
- forbidden sole found: **2026-07-03**
- company filter: **offline SECCODE**
- isolated root: **cninfo_d_class_equity_pledge_further_scale_s1000**
- frozen: EP s50/s200 / next-slice / first-slice / SC / ESH / AT / RSU / FIA

## Gates

```text
d_class_equity_pledge_further_scale_s1000_runner_extension_gate = READY_FOR_APPROVAL
d_class_equity_pledge_further_scale_s1000_live_path_gate = READY_FOR_APPROVAL
d_class_equity_pledge_further_scale_s1000_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance / excellence: ≥950/1000 acceptable (≥95%) · fail/http=0 → PASS_WITH_CAVEAT / excellence candidate**

