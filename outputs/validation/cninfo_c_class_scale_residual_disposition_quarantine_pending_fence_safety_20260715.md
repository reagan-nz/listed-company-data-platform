# C-FM-27 Scale Residual Disposition Quarantine + Pending Fence Safety

_生成时间：2026-07-15T14:06:25Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-27** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| union_status | **2134/106/9** |
| surface_harvest_delta | **2** (000037,000055) |
| resume_same | **1** (301212) |
| partial_risk_bands | **p35_heavy=75 · p3_mid=14 · p2_mid=12 · fu_light=5** |
| surface_unique | **2251** |
| fail_count | **0** |
| matrix_rows | **127** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm27_scale_residual_disposition_quarantine_pending_fence_safety` |

## Layer gates

| layer | gate |
|-------|------|
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `failed_residual_disposition_quarantine` | `PASS_OFFLINE` |
| layer `fm26_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `partial_risk_band_rollup` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `surface_delta_pending_fence` | `PASS_OFFLINE` |

## Scale / safety gain

- FM26 连续：unique=**2249** · status=**2134/106/9** · delta=**2** · same=**1**
- failed disposition quarantine：**9** 码 · promote→complete 禁止
- surface-delta pending fence：**{000037,000055}** · 禁止吸入 harvest/exclusion
- partial risk-band：**p35_heavy=75 · p3_mid=14 · p2_mid=12 · fu_light=5**
- MOCK3–28 冻结 · MOCK29 放行

## Hold

```
c_fm_27_scale_residual_disposition_quarantine_pending_fence_safety_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
approved_for_snapshot_rebuild = false
cninfo_calls = 0
ready_for_execute = false
hold_recommendation = KEEP_EXECUTE_FALSE
decision_status = AWAITING_HUMAN_EXECUTE_DECISION
idle_not_required_while_awaiting = true
seal_chain_extended = false
ready_for_commit = true
```

## Artifacts

- [outputs/validation/_mock_c_fm27_scale_residual_disposition_quarantine_pending_fence_safety/scale_matrix.csv](_mock_c_fm27_scale_residual_disposition_quarantine_pending_fence_safety/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_residual_disposition_quarantine_pending_fence_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_residual_disposition_quarantine_pending_fence_safety_20260715.json](cninfo_c_class_scale_residual_disposition_quarantine_pending_fence_safety_20260715.json)
