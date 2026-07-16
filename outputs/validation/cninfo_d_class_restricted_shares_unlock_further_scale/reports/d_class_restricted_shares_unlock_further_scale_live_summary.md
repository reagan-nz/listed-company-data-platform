# CNINFO D 类 restricted_shares_unlock Further-Scale S50 Live Summary

_生成时间：2026-07-16 03:48:05 UTC_

> **性质：** restricted_shares_unlock further-scale (~50) live · **R19 standing bounded** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **50** |
| acceptable | **50/50** |
| acceptable_rate | **100.00%** |
| found | **48** |
| empty_but_valid | **2** |
| failed_or_http_error | **0** |
| shared_cninfo_requests | **6** |
| CNINFO calls | **6** |
| excellence | **YES** |

## Gates

```text
d_class_restricted_shares_unlock_further_scale_live_path_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_further_scale_live_gate = NOT_APPROVED
d_class_restricted_shares_unlock_further_scale_execution_gate = PASS_WITH_CAVEAT
live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Caveats

- denser multi-day tdate_daily（2026-06-25+2026-06-26+2026-06-30+2026-07-01+2026-07-02+2026-07-03）截面密度 ≠ 全市场限售解禁覆盖。
- 禁 2026-06-08 sole found 锚。
- RSU next-slice / first-slice / EP / SC / ESH / AT 冻结根未 mutate。

