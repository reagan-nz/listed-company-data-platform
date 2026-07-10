# CNINFO D 类 block_trade First-Slice Dry-run Summary

_生成时间：2026-07-10 07:51:57 UTC_

> **性质：** block_trade first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_request_count_total | **5** |
| CNINFO calls | **0** |
| universe | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv` |

## Endpoint

- component: **block_trade**
- endpoint: `https://www.cninfo.com.cn/data20/ints/statistics`
- query mode: **tdate_daily**
- anchor_tdate: **2026-07-03**

## Gates

```text
d_class_block_trade_first_slice_runner_extension_gate = READY_FOR_APPROVAL
approval_status = NOT_APPROVED
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

