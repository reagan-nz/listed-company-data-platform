# CNINFO D 类 equity_pledge Further-Scale S200 Dry-run Summary

_生成时间：2026-07-16 03:34:29 UTC_

> **性质：** equity_pledge further-scale s200 dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **200** |
| planned_ok | **200/200** |
| planned_shared_cninfo_requests | **10** |
| planned_request_budget_total | **200** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_equity_pledge_further_scale_s200_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data20/equityPledge/list`
- query mode: **tdate_daily_multi_day_union**
- shared probe: **type=desc** · **2026-06-16 + 2026-06-17 + 2026-06-18 + 2026-06-19 + 2026-06-23 + 2026-06-24 + 2026-06-25 + 2026-06-26 + 2026-06-27 + 2026-06-30**
- forbidden sole found: **2026-07-03**
- company filter: **offline SECCODE**
- isolated root: **cninfo_d_class_equity_pledge_further_scale_s200**
- frozen: EP s50 / next-slice / first-slice / ESH / AT / EP / RSU / FIA

## Gates

```text
d_class_equity_pledge_further_scale_s200_runner_extension_gate = READY_FOR_APPROVAL
d_class_equity_pledge_further_scale_s200_live_path_gate = READY_FOR_APPROVAL
d_class_equity_pledge_further_scale_s200_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance / excellence: ≥190/200 acceptable (≥95%) · fail/http=0 → PASS_WITH_CAVEAT / excellence candidate**

