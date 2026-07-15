# CNINFO D 类 restricted_shares_unlock Next-Slice Dry-run Summary

_生成时间：2026-07-15 16:09:56 UTC_

> **性质：** restricted_shares_unlock next-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for live**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_shared_cninfo_requests | **1** |
| planned_request_budget_total | **5** |
| planned_request_count_total | **1** |
| CNINFO calls | **0** |
| universe | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv` |

## Endpoint

- component: **restricted_shares_unlock**
- endpoint: `https://www.cninfo.com.cn/data20/liftBan/detail`
- query mode: **tdate_daily**
- shared probe: **tdate=2026-07-03** · method POST
- forbidden sole found anchor: **2026-06-08**
- records_path: **data.records**
- company filter: **offline SECCODE**
- fixture root: `fixtures/d_class/restricted_shares_unlock_next_slice/`
- company filter field: **SECCODE**

## Gates

```text
d_class_restricted_shares_unlock_next_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_next_slice_live_path_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_next_slice_live_gate = NOT_APPROVED
approval_status = STANDING_SCOPE_AUTHORIZED_OFFLINE
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

