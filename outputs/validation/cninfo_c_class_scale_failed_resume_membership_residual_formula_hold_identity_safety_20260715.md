# C-FM-36 Scale Failed/Resume Membership + Residual Formula + Hold Identity

_生成时间：2026-07-15T15:20:49Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-36** |
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
| fail_count | **0** |
| matrix_rows | **156** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm36_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `failed_codes_membership_freeze` | `PASS_OFFLINE` |
| layer `fm35_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `hold_decision_identity_lock` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `residual_formula_identity_lock` | `PASS_OFFLINE` |
| layer `resume_same_worse_membership_freeze` | `PASS_OFFLINE` |

## Scale / safety gain

- FM35 连续：unique=**2249** · dryrun=**1053** · Δ2 · status=**2134/106/9** · resume=**28/1/0** · winner/resume-taxonomy/batch/risk fps
- failed_codes_membership_freeze：精确 **9** 码 · inject/drop/replace 拒绝
- resume_same_worse_membership_freeze：same=**{301212}** · worse=**∅**
- residual_formula_identity_lock：**117=106+9+2**
- hold_decision_identity_lock：KEEP_EXECUTE_FALSE + AWAITING + approved=false
- MOCK3–37 冻结 · MOCK38 放行

## Hold

```
c_fm_36_scale_failed_resume_membership_residual_formula_hold_identity_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm36_cli_test_tmp/scale_matrix.csv](_mock_c_fm36_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_failed_resume_membership_residual_formula_hold_identity_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_failed_resume_membership_residual_formula_hold_identity_safety_20260715.json](cninfo_c_class_scale_failed_resume_membership_residual_formula_hold_identity_safety_20260715.json)
