# C-FM-45 Scale Unique/Surface/Additive/Tier/Dryrun-Wall-Meta-Bundle

_生成时间：2026-07-15T17:04:03Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-45** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| harvest_additive | **2261** |
| surface_unique | **2251** |
| combined_dryrun_coverage | **1053** |
| unique_surface_additive_formula | **2249/2251/2261** |
| tier_coverage_status_formula | **7/3314** |
| combined_dryrun_status_formula | **dryrun=1053** |
| residual_safety_coverage | **117** |
| fail_count | **0** |
| matrix_rows | **180** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm45_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `combined_dryrun_status_composition_identity_lock` | `PASS_OFFLINE` |
| layer `cross_unique_surface_additive_tier_dryrun_wall_meta_bundle_identity_lock` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm44_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `tier_coverage_status_composition_identity_lock` | `PASS_OFFLINE` |
| layer `unique_surface_additive_composition_identity_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM44 连续：unique=**2249** · dryrun=**1053** · residual=**117** · resume=**28/1/0** · risk=**75/14/12/5** · coverage_wall_meta
- unique_surface_additive_composition_identity_lock：**2249/2251/2261**
- tier_coverage_status_composition_identity_lock：**7/3314**
- combined_dryrun_status_composition_identity_lock：**dryrun=1053**
- cross_unique_surface_additive_tier_dryrun_wall_meta_bundle_identity_lock：unique/surface/additive/tier/dryrun 墙元捆绑身份锁
- MOCK3–46 冻结 · MOCK47 放行

## Hold

```
c_fm_45_scale_unique_surface_additive_tier_dryrun_wall_meta_bundle_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm45_cli_test_tmp/scale_matrix.csv](_mock_c_fm45_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_unique_surface_additive_tier_dryrun_wall_meta_bundle_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_unique_surface_additive_tier_dryrun_wall_meta_bundle_safety_20260715.json](cninfo_c_class_scale_unique_surface_additive_tier_dryrun_wall_meta_bundle_safety_20260715.json)
