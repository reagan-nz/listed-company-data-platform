# CNINFO D 类 equity_pledge First-Slice Dry-run Summary

_生成时间：2026-07-10 10:04:28 UTC_

> **性质：** equity_pledge first-slice dry-run only · **CNINFO calls = 0** · **NOT APPROVED**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **5** |
| planned_ok | **5/5** |
| planned_request_count_total | **5** |
| CNINFO calls | **0** |
| universe | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft.csv` |

## Endpoint

- component: **equity_pledge**
- endpoint: `https://www.cninfo.com.cn/data20/equityPledge/list`
- query mode: **tdate_daily**
- anchor_tdate: **2026-07-03**

## Gates

```text
d_class_equity_pledge_first_slice_runner_extension_gate = READY_FOR_APPROVAL
approval_status = NOT_APPROVED
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold: **≥3/5 acceptable → PASS_WITH_CAVEAT**

