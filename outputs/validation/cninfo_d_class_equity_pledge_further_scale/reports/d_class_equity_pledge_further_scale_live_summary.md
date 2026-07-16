# CNINFO D 类 equity_pledge Further-Scale Live Summary

_生成时间：2026-07-16 03:32:49 UTC_

> **性质：** equity_pledge further-scale live · **R19 standing bounded** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **50** |
| acceptable | **50/50** |
| acceptable_rate | **100.00%** |
| found | **48** |
| empty_but_valid | **2** |
| failed_or_http_error | **0** |
| shared_cninfo_requests | **2** |
| CNINFO calls | **2** |
| excellence | **YES** |

## Gates

```text
d_class_equity_pledge_further_scale_live_path_gate = READY_FOR_APPROVAL
d_class_equity_pledge_further_scale_live_gate = NOT_APPROVED
d_class_equity_pledge_further_scale_execution_gate = PASS_WITH_CAVEAT
live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Caveats

- denser multi-day tdate_daily（2026-07-02+2026-07-01）截面密度 ≠ 全市场股权质押覆盖。
- 禁 2026-07-03 sole found 锚。
- EP next-slice DEP101–105 / first-slice / SC / ESH / AT 冻结根未 mutate。

