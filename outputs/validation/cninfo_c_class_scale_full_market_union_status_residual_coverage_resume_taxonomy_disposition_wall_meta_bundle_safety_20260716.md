# C-FM-49 Scale Union-Status/Residual-Coverage/Resume-Taxonomy-Disposition-Wall-Meta-Bundle

_生成时间：2026-07-16T02:47:14Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-49** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| harvest_additive | **2261** |
| surface_unique | **2251** |
| combined_dryrun_coverage | **1053** |
| union_status_formula | **2134/106/9** |
| residual_coverage_formula | **coverage=117** |
| resume_taxonomy_disposition_formula | **28/1/0** |
| residual_safety_coverage | **117** |
| fail_count | **0** |
| matrix_rows | **192** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm49_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `cross_full_market_union_status_residual_coverage_resume_taxonomy_disposition_wall_meta_bundle_identity_lock` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm48_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `residual_coverage_composition_identity_lock` | `PASS_OFFLINE` |
| layer `resume_taxonomy_disposition_composition_identity_lock` | `PASS_OFFLINE` |
| layer `union_status_composition_identity_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM48 连续：unique=**2249** · dryrun=**1053** · residual=**117** · resume=**28/1/0** · risk=**75/14/12/5** · coverage_wall_meta
- union_status_composition_identity_lock：**2134/106/9**
- residual_coverage_composition_identity_lock：**coverage=117**
- resume_taxonomy_disposition_composition_identity_lock：**28/1/0**
- cross_full_market_union_status_residual_coverage_resume_taxonomy_disposition_wall_meta_bundle_identity_lock：union/residual/resume disposition 墙元捆绑身份锁
- MOCK3–50 冻结 · MOCK51 放行

## Hold

```
c_fm_49_scale_full_market_union_status_residual_coverage_resume_taxonomy_disposition_wall_meta_bundle_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm49_cli_test_tmp/scale_matrix.csv](_mock_c_fm49_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_full_market_union_status_residual_coverage_resume_taxonomy_disposition_wall_meta_bundle_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_full_market_union_status_residual_coverage_resume_taxonomy_disposition_wall_meta_bundle_safety_20260716.json](cninfo_c_class_scale_full_market_union_status_residual_coverage_resume_taxonomy_disposition_wall_meta_bundle_safety_20260716.json)
