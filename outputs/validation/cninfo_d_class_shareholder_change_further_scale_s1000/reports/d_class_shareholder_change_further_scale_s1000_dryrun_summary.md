# CNINFO D 类 shareholder_change Further-Scale S1000 Dry-run Summary

_生成时间：2026-07-16 03:26:53 UTC_

> **性质：** shareholder_change further-scale s1000 dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **1000** |
| planned_ok | **1000/1000** |
| planned_shared_cninfo_requests | **11** |
| planned_request_budget_total | **1000** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data20/shareholeder/detail`（拼写 shareholeder 保留）
- query mode: **type_desc_multi_day_union**
- shared probe: **type=desc** · **2026-06-27 + 2026-06-30 + 2026-07-02 + 2026-07-04 + 2026-07-07 + 2026-07-08 + 2026-07-09 + 2026-07-10 + 2026-07-11 + 2026-07-14 + 2026-07-15**
- forbidden sole found: **inc+2026-07-03**
- company filter: **offline SECCODE**
- isolated root: **cninfo_d_class_shareholder_change_further_scale_s1000**
- frozen: SC s50/s200 / next-slice / first-slice / ESH / AT / EP / RSU / FIA

## Gates

```text
d_class_shareholder_change_further_scale_s1000_runner_extension_gate = READY_FOR_APPROVAL
d_class_shareholder_change_further_scale_s1000_live_path_gate = READY_FOR_APPROVAL
d_class_shareholder_change_further_scale_s1000_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance / excellence: ≥950/1000 acceptable (≥95%) · fail/http=0 → PASS_WITH_CAVEAT / excellence candidate**

