# C-FM-37 Scale Improved/Partial/Surface-Delta Membership + Union Formula

_生成时间：2026-07-15T15:27:39Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-37** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| harvest_additive | **2261** |
| surface_unique | **2251** |
| combined_dryrun_coverage | **1053** |
| surface_harvest_delta_n | **2** |
| union_status | **2134/106/9** |
| overlap_delta | **12** |
| resume_taxonomy | **28/1/0** |
| residual_safety_coverage | **117** |
| residual_formula | **106+9+2=117** |
| union_formula | **2134+106+9=2249** |
| surface_formula | **2249+2=2251** |
| fail_count | **0** |
| matrix_rows | **159** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm37_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm36_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `partial_codes_membership_freeze` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `resume_improved_membership_freeze` | `PASS_OFFLINE` |
| layer `surface_harvest_delta_membership_freeze` | `PASS_OFFLINE` |
| layer `union_partition_formula_identity_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM36 连续：unique=**2249** · dryrun=**1053** · Δ2 · status=**2134/106/9** · resume=**28/1/0** · residual=**117=106+9+2** · failed/same-worse/residual/hold fps
- resume_improved_membership_freeze：基数 **28** · sha256 锁 · inject/drop/sha 拒绝
- partial_codes_membership_freeze：基数 **106** · sha256 锁
- surface_harvest_delta_membership_freeze：精确 **{000037,000055}**
- union_partition_formula_identity_lock：**2249=2134+106+9** · **2251=2249+2**
- MOCK3–38 冻结 · MOCK39 放行

## Hold

```
c_fm_37_scale_improved_partial_surface_delta_union_partition_formula_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm37_cli_test_tmp/scale_matrix.csv](_mock_c_fm37_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_improved_partial_surface_delta_union_partition_formula_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_improved_partial_surface_delta_union_partition_formula_safety_20260715.json](cninfo_c_class_scale_improved_partial_surface_delta_union_partition_formula_safety_20260715.json)
