# CNINFO D 类 fund_industry_allocation First-Slice Dry-run Summary

_生成时间：2026-07-15 12:35:04 UTC_

> **性质：** fund_industry_allocation first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for live**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_shared_cninfo_requests | **3** |
| planned_request_budget_total | **5** |
| planned_request_count_total | **3** |
| CNINFO calls | **0** |
| universe | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv` |

## Endpoint

- component: **fund_industry_allocation**
- endpoint: `https://www.cninfo.com.cn/data20/fund/industry`
- query modes: **default** · **rdate**
- shared probes: **default** · **rdate=20260331** · **rdate=20251231**
- records_path: **data.records**
- schema: **d_industry_aggregate** · offline F001V industry filter · **no company_code**
- fixture root: `fixtures/d_class/fund_industry_allocation_first_slice/`

## Gates

```text
d_class_fund_industry_allocation_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_first_slice_live_gate = NOT_APPROVED
approval_status = STANDING_SCOPE_AUTHORIZED_OFFLINE
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

