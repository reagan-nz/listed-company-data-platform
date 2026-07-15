# C-FM-39 Scale Risk-Band Membership + Combined-Dryrun/Resume Formula

_生成时间：2026-07-15T15:44:47Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-39** |
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
| fail_count | **0** |
| matrix_rows | **166** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm39_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `combined_dryrun_coverage_identity_lock` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm38_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `partial_risk_band_membership_freeze` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `resume_formula_identity_lock` | `PASS_OFFLINE` |
| layer `risk_band_formula_identity_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM38 连续：unique=**2249** · dryrun=**1053** · Δ2 · status=**2134/106/9** · resume=**28/1/0** · residual=**117=106+9+2** · additive/tier formulas · complete/overlap/additive/tier fps
- partial_risk_band_membership_freeze：**75/14/12/5** · membership sha256 锁 · inject/drop/reclass 拒绝
- combined_dryrun_coverage_identity_lock：**1053** · inflate/deflate 拒绝
- risk_band_formula_identity_lock：**75+14+12+5=106**
- resume_formula_identity_lock：**28+1+0=29**
- MOCK3–40 冻结 · MOCK41 放行

## Hold

```
c_fm_39_scale_risk_band_combined_dryrun_resume_formula_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm39_cli_test_tmp/scale_matrix.csv](_mock_c_fm39_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_risk_band_combined_dryrun_resume_formula_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_risk_band_combined_dryrun_resume_formula_safety_20260715.json](cninfo_c_class_scale_risk_band_combined_dryrun_resume_formula_safety_20260715.json)
