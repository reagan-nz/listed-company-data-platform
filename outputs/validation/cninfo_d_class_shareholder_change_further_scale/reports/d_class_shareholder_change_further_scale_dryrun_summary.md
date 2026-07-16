# CNINFO D 类 shareholder_change Further-Scale Dry-run Summary

_生成时间：2026-07-16 03:08:06 UTC_

> **性质：** shareholder_change further-scale dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **50** |
| planned_ok | **50/50** |
| planned_shared_cninfo_requests | **2** |
| planned_request_budget_total | **50** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data20/shareholeder/detail`（拼写 shareholeder 保留）
- query mode: **type_desc_multi_day_union**
- shared probe: **type=desc** · **2026-07-01 + 2026-07-14**
- forbidden sole found: **inc+2026-07-03**
- company filter: **offline SECCODE**
- isolated root: **cninfo_d_class_shareholder_change_further_scale**
- frozen: SC next-slice DSC101–105 / first-slice / ESH / AT / EP / RSU / FIA

## Gates

```text
d_class_shareholder_change_further_scale_runner_extension_gate = READY_FOR_APPROVAL
d_class_shareholder_change_further_scale_live_path_gate = READY_FOR_APPROVAL
d_class_shareholder_change_further_scale_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance / excellence: ≥48/50 acceptable (≥95%) · fail/http=0 → PASS_WITH_CAVEAT / excellence candidate**

