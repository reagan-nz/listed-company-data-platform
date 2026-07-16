# CNINFO D 类 equity_pledge Further-Scale S1000 Live Summary

_生成时间：2026-07-16 03:41:15 UTC_

> **性质：** equity_pledge further-scale s1000 live · **R19 standing bounded** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **1000** |
| acceptable | **1000/1000** |
| acceptable_rate | **100.00%** |
| found | **133** |
| empty_but_valid | **867** |
| failed_or_http_error | **0** |
| shared_cninfo_requests | **10** |
| CNINFO calls | **10** |
| excellence | **YES** |

## Gates

```text
d_class_equity_pledge_further_scale_s1000_live_path_gate = READY_FOR_APPROVAL
d_class_equity_pledge_further_scale_s1000_live_gate = NOT_APPROVED
d_class_equity_pledge_further_scale_s1000_execution_gate = PASS_WITH_CAVEAT
live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Caveats

- denser multi-day tdate_daily（2026-06-30+2026-07-01+2026-07-04+2026-07-07+2026-07-08+2026-07-09+2026-07-10+2026-07-11+2026-07-14+2026-07-15）截面密度 ≠ 全市场增减持覆盖。
- 禁 2026-07-03 sole found 锚。
- EP s50/s200 / next-slice / first-slice / SC / ESH / AT 冻结根未 mutate。

