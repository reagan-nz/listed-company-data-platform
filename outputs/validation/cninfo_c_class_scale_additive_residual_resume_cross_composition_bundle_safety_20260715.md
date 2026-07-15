# C-FM-41 Scale Additive/Residual/Resume/Cross-Composition-Bundle

_生成时间：2026-07-15T16:13:19Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-41** |
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
| additive_formula | **2249+12=2261** |
| tier_coverage_formula | **tiers=7;coverage_sum=3314** |
| risk_band_formula | **75+14+12+5=106** |
| resume_formula | **28+1+0=29** |
| cross_composition_bundle_sha256 | `bfcd48460cdb75a1…` |
| fail_count | **0** |
| matrix_rows | **172** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm41_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `additive_composition_identity_lock` | `PASS_OFFLINE` |
| layer `cross_composition_bundle_identity_lock` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm40_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `residual_composition_identity_lock` | `PASS_OFFLINE` |
| layer `resume_composition_identity_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM40 连续：unique=**2249** · dryrun=**1053** · Δ2 · status=**2134/106/9** · resume=**28/1/0** · residual=**117=106+9+2** · cross_formula_bundle
- additive_composition_identity_lock：**2261=2249+12**
- residual_composition_identity_lock：**117=106+9+2**
- resume_composition_identity_lock：**29=28+1+0**
- cross_composition_bundle_identity_lock：五组成捆绑身份锁
- MOCK3–42 冻结 · MOCK43 放行

## Hold

```
c_fm_41_scale_additive_residual_resume_cross_composition_bundle_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm41_cli_test_tmp/scale_matrix.csv](_mock_c_fm41_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_additive_residual_resume_cross_composition_bundle_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_additive_residual_resume_cross_composition_bundle_safety_20260715.json](cninfo_c_class_scale_additive_residual_resume_cross_composition_bundle_safety_20260715.json)
