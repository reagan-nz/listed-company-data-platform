# CNINFO D 类 shareholder_change Further-Scale S200 Dry-run Summary

_生成时间：2026-07-16 03:19:20 UTC_

> **性质：** shareholder_change further-scale s200 dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **200** |
| planned_ok | **200/200** |
| planned_shared_cninfo_requests | **9** |
| planned_request_budget_total | **200** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data20/shareholeder/detail`（拼写 shareholeder 保留）
- query mode: **type_desc_multi_day_union**
- shared probe: **type=desc** · **2026-06-16 + 2026-06-17 + 2026-06-18 + 2026-06-19 + 2026-06-23 + 2026-06-24 + 2026-06-25 + 2026-06-26 + 2026-06-27**
- forbidden sole found: **inc+2026-07-03**
- company filter: **offline SECCODE**
- isolated root: **cninfo_d_class_shareholder_change_further_scale_s200**
- frozen: SC s50 / next-slice / first-slice / ESH / AT / EP / RSU / FIA

## Gates

```text
d_class_shareholder_change_further_scale_s200_runner_extension_gate = READY_FOR_APPROVAL
d_class_shareholder_change_further_scale_s200_live_path_gate = READY_FOR_APPROVAL
d_class_shareholder_change_further_scale_s200_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance / excellence: ≥190/200 acceptable (≥95%) · fail/http=0 → PASS_WITH_CAVEAT / excellence candidate**

