# CNINFO D 类 shareholder_data First-Slice Dry-run Summary

_生成时间：2026-07-15 10:12:47 UTC_

> **性质：** shareholder_data first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for live**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_shared_cninfo_requests | **1** |
| planned_request_budget_total | **5** |
| planned_request_count_total | **1** |
| CNINFO calls | **0** |
| universe | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv` |

## Endpoint

- component: **shareholder_data**
- endpoint: `https://www.cninfo.com.cn/data20/shareholeder/data`
- query mode: **rdate_report_period**
- anchor_rdate: **20260331**
- records_path: **data.records**
- shared market-wide rdate request · offline SECCODE filter
- fixture root: `fixtures/d_class/shareholder_data_first_slice/`

## Gates

```text
d_class_shareholder_data_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_shareholder_data_first_slice_live_gate = NOT_APPROVED
approval_status = STANDING_SCOPE_AUTHORIZED_OFFLINE
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

