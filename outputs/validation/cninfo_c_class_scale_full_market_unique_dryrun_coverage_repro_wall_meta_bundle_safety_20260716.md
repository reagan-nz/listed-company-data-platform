# C-FM-47 Scale Lineage/Drift/Protected/Repro-Wall-Meta-Bundle

_生成时间：2026-07-16T02:22:59Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-47** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| harvest_additive | **2261** |
| surface_unique | **2251** |
| combined_dryrun_coverage | **1053** |
| full_market_unique_union_formula | **unique=2249** |
| combined_dryrun_cohort_formula | **combined_dryrun=1053** |
| company_coverage_scale_formula | **tiers=7;coverage_sum=3314** |
| residual_safety_coverage | **117** |
| fail_count | **0** |
| matrix_rows | **186** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm47_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `combined_dryrun_cohort_composition_identity_lock` | `PASS_OFFLINE` |
| layer `company_coverage_scale_composition_identity_lock` | `PASS_OFFLINE` |
| layer `cross_full_market_scale_repro_wall_meta_bundle_identity_lock` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm46_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `full_market_unique_union_composition_identity_lock` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |

## Scale / safety gain

- FM46 连续：unique=**2249** · dryrun=**1053** · residual=**117** · resume=**28/1/0** · risk=**75/14/12/5** · coverage_wall_meta
- full_market_unique_union_composition_identity_lock：**overlap_delta=12**
- combined_dryrun_cohort_composition_identity_lock：**dry863=2**
- company_coverage_scale_composition_identity_lock：**h863>p35>p3>p2>fu**
- cross_full_market_scale_repro_wall_meta_bundle_identity_lock：unique/dryrun/coverage/repro 墙元捆绑身份锁
- MOCK3–48 冻结 · MOCK49 放行

## Hold

```
c_fm_47_scale_lineage_drift_protected_repro_wall_meta_bundle_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm47_cli_test_tmp/scale_matrix.csv](_mock_c_fm47_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety_20260716.json](cninfo_c_class_scale_full_market_unique_dryrun_coverage_repro_wall_meta_bundle_safety_20260716.json)
