# CNINFO D 类 executive_shareholding_summary — Endpoint Probe Live

_生成时间：2026-07-15 13:24:06 UTC · D-FM-22_

> **性质：** bounded H1→H2 endpoint probe · **CNINFO≤2** · **live_gate=NOT_APPROVED** · **NOT verified** · **NOT production_ready**

## Result

| 项 | 值 |
|----|-----|
| final_hyp | **H2** |
| final_url | `https://www.cninfo.com.cn/data20/leader/statistics` |
| classification | `rejected` |
| endpoint_status | **unconfirmed_probe_failed** |
| records | **0** |
| records_path | `—` |
| sample_keys | `—` |
| CNINFO calls | **2** |
| stop_reason | `stop_after_H2_rejected` |
| caveat | `H1_and_or_H2_rejected_or_invalid; optional_DevTools` |

## Attempts
- **H1** `https://www.cninfo.com.cn/data20/leader/summary` · http=404 · `rejected` · records=0 · path=`—`
- **H2** `https://www.cninfo.com.cn/data20/leader/statistics` · http=404 · `rejected` · records=0 · path=`—`

## Gates

```text
d_class_executive_shareholding_summary_endpoint_probe_gate = FAIL_REVIEW_REQUIRED
endpoint_status = unconfirmed_probe_failed
cninfo_calls = 2
live_gate = NOT_APPROVED
```

## Explicit Non-Claims

- 不 claim verified / production_ready / bare PASS
- 不写入 registry `testing_stable_sample`
- 不 mutate FIA / ES detail / AT / SD live 根
- 不 reopen DLC006R

