# CNINFO D 类 executive_shareholding Further-Scale S1000 Live Summary

_生成时间：2026-07-16 02:58:14 UTC_

> **性质：** executive_shareholding further-scale S1000 live · **R19 standing bounded** · **NOT verified**

## Counts

| 指标 | 值 |
|------|-----|
| cases | **1000** |
| acceptable | **1000/1000** |
| acceptable_rate | **100.00%** |
| found | **167** |
| empty_but_valid | **833** |
| failed_or_http_error | **0** |
| shared_cninfo_requests | **1** |
| CNINFO calls | **1** |
| excellence | **YES** |

## Gates

```text
d_class_executive_shareholding_further_scale_s1000_live_path_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_further_scale_s1000_live_gate = NOT_APPROVED
d_class_executive_shareholding_further_scale_s1000_execution_gate = PASS_WITH_CAVEAT
live_authority = R19_STANDING_SCOPE_BOUNDED
excellence_gated = true
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Caveats

- denser-mode market-section density ≠ 全市场高管持股变动覆盖。
- 仅 leader/detail 元数据路径；禁 oneMonth+b sole found 锚。
- ESH S200 DES251–450 / S50 DES201–250 / next-slice DES101–105 冻结根未 mutate。
- denser-mode 剩余 found 不足时以文档化 empty-control pad 补齐至 ~1000。

