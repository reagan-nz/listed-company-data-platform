# CNINFO D 类 shareholder_data Next-Slice Dry-run Summary

_生成时间：2026-07-15 14:27:41 UTC_

> **性质：** shareholder_data next-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for live**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_shared_cninfo_requests | **2** |
| planned_request_budget_total | **5** |
| planned_request_count_total | **2** |
| CNINFO calls | **0** |
| universe | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_d_class_shareholder_data_next_slice_universe_lock_20260715.csv` |

## Endpoint

- component: **shareholder_data**
- endpoint: `https://www.cninfo.com.cn/data20/shareholeder/data`
- query mode: **rdate_report_period**
- shared probes: **rdate=20260331** · **rdate=20251231**
- records_path: **data.records**
- company filter: offline SECCODE
- multi-rdate: **allowed next-slice only** (does not rewrite first-slice VR-008)
- `20251231` live found-path: **NOT_PROVEN**
- fixture root: `fixtures/d_class/shareholder_data_next_slice/`

## Gates

```text
d_class_shareholder_data_next_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_shareholder_data_next_slice_live_path_gate = READY_FOR_APPROVAL
d_class_shareholder_data_next_slice_live_gate = NOT_APPROVED
approval_status = STANDING_SCOPE_AUTHORIZED_OFFLINE
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

