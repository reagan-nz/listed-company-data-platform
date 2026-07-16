# CNINFO D 类 executive_shareholding Further-Scale S200 Live Summary

_生成时间：2026-07-16 02:49:13 UTC_

> **性质：** executive_shareholding further-scale S200 live · **R19 standing bounded** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **200** |
| acceptable | **200/200** |
| acceptable_rate | **100.00%** |
| found | **198** |
| empty_but_valid | **2** |
| failed_or_http_error | **0** |
| shared_cninfo_requests | **1** |
| CNINFO calls | **1** |
| excellence | **YES** |

## Gates

```text
d_class_executive_shareholding_further_scale_s200_live_path_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_further_scale_s200_live_gate = NOT_APPROVED
d_class_executive_shareholding_further_scale_s200_execution_gate = PASS_WITH_CAVEAT
live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Caveats

- denser-mode market-section density ≠ 全市场高管持股变动覆盖。
- 仅 leader/detail 元数据路径；禁 oneMonth+b sole found 锚。
- ESH S50 DES201–250 与 next-slice DES101–105 冻结根未 mutate。

