# CNINFO D 类 shareholder_change Further-Scale S200 Live Summary

_生成时间：2026-07-16 03:19:32 UTC_

> **性质：** shareholder_change further-scale s200 live · **R19 standing bounded** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **200** |
| acceptable | **200/200** |
| acceptable_rate | **100.00%** |
| found | **198** |
| empty_but_valid | **2** |
| failed_or_http_error | **0** |
| shared_cninfo_requests | **9** |
| CNINFO calls | **9** |
| excellence | **YES** |

## Gates

```text
d_class_shareholder_change_further_scale_s200_live_path_gate = READY_FOR_APPROVAL
d_class_shareholder_change_further_scale_s200_live_gate = NOT_APPROVED
d_class_shareholder_change_further_scale_s200_execution_gate = PASS_WITH_CAVEAT
live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Caveats

- denser multi-day type=desc（2026-06-16+2026-06-17+2026-06-18+2026-06-19+2026-06-23+2026-06-24+2026-06-25+2026-06-26+2026-06-27）截面密度 ≠ 全市场增减持覆盖。
- 禁 inc+2026-07-03 sole found 锚。
- SC s50 / next-slice / first-slice / ESH / AT 冻结根未 mutate。

