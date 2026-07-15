# CNINFO D 类 fund_industry_allocation — DFIA005 Single-Probe Live

_生成时间：2026-07-15 12:38:59 UTC_

> **性质：** DFIA005 bounded single-probe · probe=`rdate_20251231` · **CNINFO≤1** · **live_gate=NOT_APPROVED**

## Result

| 项 | 值 |
|----|-----|
| case_id | **DFIA005** |
| probe | `rdate_20251231` |
| expected | `empty_but_valid` |
| retrieval_status | `found` |
| records | **19** |
| acceptable | **yes** |
| failure_type | `empty_control_anchor_stale` |
| caveat | `empty_control_anchor_stale` |
| CNINFO calls | **1** |
| http_status | 200 |
| last_error | `—` |

## Gates

```text
d_class_fund_industry_allocation_dfia005_single_probe_gate = PASS_WITH_CAVEAT
d_class_fund_industry_allocation_first_slice_live_gate = NOT_APPROVED
caveat = empty_control_anchor_stale
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

