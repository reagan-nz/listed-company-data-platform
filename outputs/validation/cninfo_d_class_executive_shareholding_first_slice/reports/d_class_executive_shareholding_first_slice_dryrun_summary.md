# CNINFO D 类 executive_shareholding First-Slice Dry-run Summary

_生成时间：2026-07-15 08:50:38 UTC_

> **性质：** executive_shareholding first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED for production**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_request_count_total | **5** |
| tier1_fixture_refs | **8** |
| CNINFO calls | **0** |
| universe | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv` |

## Endpoint

- component: **executive_shareholding**
- endpoint: `https://www.cninfo.com.cn/data20/leader/detail`
- query mode: **timeMark=oneMonth + varyType=b**（禁止 threeMonth/oneYear/s）
- time_mark: **oneMonth**
- vary_type: **b**

## Tier-1 Fixtures

- fixture root: `fixtures/d_class/executive_shareholding_first_slice/`
- wired into planned_snapshots for DES001–DES005

## Gates

```text
d_class_executive_shareholding_first_slice_runner_extension_gate = READY_FOR_APPROVAL
approval_status = NOT_APPROVED_FOR_PRODUCTION
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

