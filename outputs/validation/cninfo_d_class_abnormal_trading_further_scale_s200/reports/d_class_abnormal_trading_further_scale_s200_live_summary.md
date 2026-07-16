# CNINFO D 类 abnormal_trading Further-Scale S200 Live Summary

_生成时间：2026-07-16 02:27:16 UTC_

> **性质：** abnormal_trading further-scale S200 live · **R19 standing bounded** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **200** |
| acceptable | **200/200** |
| acceptable_rate | **100.00%** |
| found | **195** |
| empty_but_valid | **5** |
| failed_or_http_error | **0** |
| shared_cninfo_requests | **2** |
| CNINFO calls | **2** |
| excellence | **YES** |

## Gates

```text
d_class_abnormal_trading_further_scale_s200_execution_gate = PASS_WITH_CAVEAT
live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Caveats

- multi_day_compose_not_full_market：primary `2026-07-02` + adjacent `2026-07-01` 拼合子集，非全市场 abnormal_trading 覆盖。
- detail_nested_deferred：仅 marketList 元数据路径。

