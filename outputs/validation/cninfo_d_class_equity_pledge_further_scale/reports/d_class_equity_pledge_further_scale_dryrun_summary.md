# CNINFO D 类 equity_pledge Further-Scale Dry-run Summary

_生成时间：2026-07-16 03:32:45 UTC_

> **性质：** equity_pledge further-scale dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **50** |
| planned_ok | **50/50** |
| planned_shared_cninfo_requests | **2** |
| planned_request_budget_total | **50** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_equity_pledge_further_scale_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data20/equityPledge/list`
- query mode: **tdate_daily_multi_day_union**
- shared probe: **tdate=2026-07-02 + 2026-07-01**
- forbidden sole found: **2026-07-03**
- company filter: **offline SECCODE**
- isolated root: **cninfo_d_class_equity_pledge_further_scale**
- frozen: EP next-slice DEP101–105 / first-slice / SC / ESH / AT

## Gates

```text
d_class_equity_pledge_further_scale_runner_extension_gate = READY_FOR_APPROVAL
d_class_equity_pledge_further_scale_live_path_gate = READY_FOR_APPROVAL
d_class_equity_pledge_further_scale_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance / excellence: ≥48/50 acceptable (≥95%) · fail/http=0 → PASS_WITH_CAVEAT / excellence candidate**

