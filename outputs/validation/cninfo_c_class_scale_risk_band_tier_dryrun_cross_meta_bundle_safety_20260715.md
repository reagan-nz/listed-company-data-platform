# C-FM-42 Scale Risk-Band/Tier/Dryrun/Cross-Meta-Bundle

_生成时间：2026-07-15T16:26:26Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-42** |
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
| cross_formula_composition_meta_bundle_sha256 | `1a95681ad0542103…` |
| fail_count | **0** |
| matrix_rows | **175** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm42_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `combined_dryrun_composition_identity_lock` | `PASS_OFFLINE` |
| layer `cross_formula_composition_meta_bundle_identity_lock` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm41_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `risk_band_composition_identity_lock` | `PASS_OFFLINE` |
| layer `tier_coverage_composition_identity_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM41 连续：unique=**2249** · dryrun=**1053** · Δ2 · status=**2134/106/9** · resume=**28/1/0** · residual=**117=106+9+2** · cross_composition_bundle
- risk_band_composition_identity_lock：**75+14+12+5=106**
- tier_coverage_composition_identity_lock：**tiers=7;coverage_sum=3314**
- combined_dryrun_composition_identity_lock：**combined_dryrun=1053**
- cross_formula_composition_meta_bundle_identity_lock：五组成元捆绑身份锁
- MOCK3–43 冻结 · MOCK44 放行

## Hold

```
c_fm_42_scale_risk_band_tier_dryrun_cross_meta_bundle_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm42_cli_test_tmp/scale_matrix.csv](_mock_c_fm42_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_risk_band_tier_dryrun_cross_meta_bundle_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_risk_band_tier_dryrun_cross_meta_bundle_safety_20260715.json](cninfo_c_class_scale_risk_band_tier_dryrun_cross_meta_bundle_safety_20260715.json)
