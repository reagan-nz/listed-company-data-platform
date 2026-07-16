# CNINFO D 类 executive_shareholding Further-Scale S1000 Dry-run Summary

_生成时间：2026-07-16 02:58:09 UTC_

> **性质：** executive_shareholding further-scale S1000 dry-run · **CNINFO calls = 0** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **1000** |
| planned_ok | **1000/1000** |
| planned_shared_cninfo_requests | **1** |
| planned_request_budget_total | **1000** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s1000_universe_lock_20260716.csv` |

## Endpoint

- endpoint: `https://www.cninfo.com.cn/data20/leader/detail`
- query mode: **timeMark_threeMonth_varyType_b**
- shared probe: **timeMark=threeMonth** · **varyType=b**
- forbidden sole found timeMark: **oneMonth**
- company filter: **offline SECCODE**
- isolated root: **cninfo_d_class_executive_shareholding_further_scale_s1000**
- frozen: ESH S200 DES251–450 / S50 DES201–250 / next-slice DES101–105 / first-slice / AT / SC / EP / RSU / FIA

## Gates

```text
d_class_executive_shareholding_further_scale_s1000_runner_extension_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_further_scale_s1000_live_path_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_further_scale_s1000_live_gate = NOT_APPROVED
approval_status = R19_STANDING_SCOPE_BOUNDED
```

**Future acceptance / excellence: ≥950/1000 acceptable (≥95%) · fail/http=0 → PASS_WITH_CAVEAT / excellence candidate**

