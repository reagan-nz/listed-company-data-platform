# CNINFO D 类 executive_shareholding Next-Slice Dry-run Summary

_生成时间：2026-07-16 02:03:12 UTC_

> **性质：** executive_shareholding next-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for live**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_shared_cninfo_requests | **1** |
| planned_request_budget_total | **5** |
| planned_request_count_total | **1** |
| CNINFO calls | **0** |
| universe | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_d_class_executive_shareholding_next_slice_universe_lock_20260716.csv` |

## Endpoint

- component: **executive_shareholding**
- endpoint: `https://www.cninfo.com.cn/data20/leader/detail`
- query mode: **timeMark_threeMonth_varyType_b**
- timeMark: **threeMonth**
- varyType: **b**
- shared probe: **timeMark=threeMonth** · **varyType=b** · method POST
- forbidden sole found: **timeMark=oneMonth** + **varyType=b**
- records_path: **data.records**
- company filter: **offline SECCODE**
- fixture root: `fixtures/d_class/executive_shareholding_next_slice/`
- company filter field: **SECCODE**

## Gates

```text
d_class_executive_shareholding_next_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_next_slice_live_path_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_next_slice_live_gate = NOT_APPROVED
approval_status = STANDING_SCOPE_AUTHORIZED_OFFLINE
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

