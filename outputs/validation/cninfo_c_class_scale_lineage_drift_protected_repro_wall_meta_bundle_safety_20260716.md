# C-FM-46 Scale Lineage/Drift/Protected/Repro-Wall-Meta-Bundle

_生成时间：2026-07-16T02:02:18Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-46** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| harvest_additive | **2261** |
| surface_unique | **2251** |
| combined_dryrun_coverage | **1053** |
| lineage_winner_provenance_formula | **winner/complete** |
| partition_codeset_formula | **complete/partial/failed** |
| protected_root_registry_formula | **MOCK3-47+MOCK48+resume+auth** |
| residual_safety_coverage | **117** |
| fail_count | **0** |
| matrix_rows | **183** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm46_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `cross_lineage_drift_protected_repro_wall_meta_bundle_identity_lock` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm45_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `lineage_winner_provenance_composition_identity_lock` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `partition_codeset_composition_identity_lock` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `protected_root_registry_composition_identity_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM45 连续：unique=**2249** · dryrun=**1053** · residual=**117** · resume=**28/1/0** · risk=**75/14/12/5** · coverage_wall_meta
- lineage_winner_provenance_composition_identity_lock：**winner/complete**
- partition_codeset_composition_identity_lock：**complete/partial/failed**
- protected_root_registry_composition_identity_lock：**MOCK3-47+MOCK48+resume+auth**
- cross_lineage_drift_protected_repro_wall_meta_bundle_identity_lock：lineage/drift/protected/repro 墙元捆绑身份锁
- MOCK3–47 冻结 · MOCK48 放行

## Hold

```
c_fm_46_scale_lineage_drift_protected_repro_wall_meta_bundle_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm46_cli_test_tmp/scale_matrix.csv](_mock_c_fm46_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_lineage_drift_protected_repro_wall_meta_bundle_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_lineage_drift_protected_repro_wall_meta_bundle_safety_20260716.json](cninfo_c_class_scale_lineage_drift_protected_repro_wall_meta_bundle_safety_20260716.json)
