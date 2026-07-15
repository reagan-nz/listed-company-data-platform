# CNINFO D 类 abnormal_trading First-Slice Dry-run Summary

_生成时间：2026-07-15 09:07:04 UTC_

> **性质：** abnormal_trading first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for production**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_request_count_total | **5** |
| CNINFO calls | **0** |
| universe | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv` |

## Endpoint

- component: **abnormal_trading**
- endpoint: `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData`
- query mode: **single_day_paged**
- anchor_tdate: **2026-07-03**
- records_path: **marketList**
- fixture root: `fixtures/d_class/abnormal_trading_first_slice/`
- detail[]: **deferred** (d_event_party_detail)

## Gates

```text
d_class_abnormal_trading_first_slice_runner_extension_gate = READY_FOR_APPROVAL
approval_status = STANDING_SCOPE_AUTHORIZED_OFFLINE
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

