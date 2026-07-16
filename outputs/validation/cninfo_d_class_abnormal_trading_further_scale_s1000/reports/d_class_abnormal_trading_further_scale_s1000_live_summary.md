# CNINFO D 类 abnormal_trading Further-Scale S1000 Live Summary

_生成时间：2026-07-16 02:37:46 UTC_

> **性质：** abnormal_trading further-scale S1000 live · **R19 standing bounded** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **1000** |
| acceptable | **1000/1000** |
| acceptable_rate | **100.00%** |
| found | **752** |
| empty_but_valid | **248** |
| failed_or_http_error | **0** |
| shared_cninfo_requests | **14** |
| CNINFO calls | **14** |
| unique_anchor_days | **14** |
| excellence | **YES** |

## Gates

```text
d_class_abnormal_trading_further_scale_s1000_execution_gate = PASS_WITH_CAVEAT
live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Caveats

- multi_day_multipage_compose_not_full_market：多日并集 + empty pad，非全市场 abnormal_trading 覆盖。
- empty_control_pad_documented：found 并集不足时以 cite 验证缺席码补齐。
- detail_nested_deferred：仅 marketList 元数据路径。

