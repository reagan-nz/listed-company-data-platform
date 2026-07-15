# C-FM-40 Scale Dry863/Unique/Surface/Cross-Formula-Bundle

_生成时间：2026-07-15T16:00:03Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-40** |
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
| cross_formula_bundle_sha256 | `f2561a695dcd567d…` |
| fail_count | **0** |
| matrix_rows | **169** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm40_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `cross_formula_bundle_identity_lock` | `PASS_OFFLINE` |
| layer `dry863_extras_membership_freeze` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm39_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `surface_unique_composition_identity_lock` | `PASS_OFFLINE` |
| layer `unique_union_composition_identity_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM39 连续：unique=**2249** · dryrun=**1053** · Δ2 · status=**2134/106/9** · resume=**28/1/0** · residual=**117=106+9+2** · risk_band/resume formulas
- dry863_extras_membership_freeze：**{000037,000055}** · inject/drop/replace 拒绝
- unique_union_composition_identity_lock：**2249=2134+106+9**
- surface_unique_composition_identity_lock：**2251=2249+2**
- cross_formula_bundle_identity_lock：七公式捆绑身份锁
- MOCK3–41 冻结 · MOCK42 放行

## Hold

```
c_fm_40_scale_dry863_unique_surface_cross_formula_bundle_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm40_cli_test_tmp/scale_matrix.csv](_mock_c_fm40_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety_20260715.json](cninfo_c_class_scale_dry863_unique_surface_cross_formula_bundle_safety_20260715.json)
