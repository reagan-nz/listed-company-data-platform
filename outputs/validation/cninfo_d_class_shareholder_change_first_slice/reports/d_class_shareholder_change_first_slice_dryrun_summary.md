# CNINFO D 类 shareholder_change First-Slice Dry-run Summary

_生成时间：2026-07-15 06:13:32 UTC_

> **性质：** shareholder_change first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_request_count_total | **5** |
| CNINFO calls | **0** |
| universe | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv` |

## Endpoint

- component: **shareholder_change**
- endpoint: `https://www.cninfo.com.cn/data20/shareholeder/detail`
- query mode: **type_inc + tdate_daily**（禁止 desc / multi-tdate）
- anchor_tdate: **2026-07-03**
- query_type: **inc**

## Gates

```text
d_class_shareholder_change_first_slice_runner_extension_gate = READY_FOR_APPROVAL
approval_status = NOT_APPROVED
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

