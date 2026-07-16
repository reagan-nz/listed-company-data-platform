# CNINFO D 类 executive_shareholding Further-Scale Dry-run Summary

_生成时间：2026-07-16 02:43:54 UTC_

> **性质：** executive_shareholding further-scale dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **50** |
| planned_ok | **50/50** |
| planned_shared_cninfo_requests | **1** |
| planned_request_budget_total | **50** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data20/leader/detail`
- query mode: **timeMark_threeMonth_varyType_b**
- shared probe: **timeMark=threeMonth** · **varyType=b**
- forbidden sole found timeMark: **oneMonth**
- company filter: **offline SECCODE**
- isolated root: **cninfo_d_class_executive_shareholding_further_scale**
- frozen: ESH next-slice DES101–105 / first-slice / AT / SC / EP / RSU / FIA

## Gates

```text
d_class_executive_shareholding_further_scale_runner_extension_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_further_scale_live_path_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_further_scale_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance / excellence: ≥48/50 acceptable (≥95%) · fail/http=0 → PASS_WITH_CAVEAT / excellence candidate**

