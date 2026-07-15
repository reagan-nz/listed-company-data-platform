# C-FM-29 Scale Partial Promote/Reclass + Resume Lift + Coverage Invariant

_生成时间：2026-07-15T14:18:27Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-29** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| union_status | **2134/106/9** |
| surface_harvest_delta | **2** (000037,000055) |
| resume_same | **1** (301212) |
| partial_risk_bands | **p35_heavy=75 · p3_mid=14 · p2_mid=12 · fu_light=5** |
| residual_safety_coverage | **117** (9+2+106) |
| surface_unique | **2251** |
| fail_count | **0** |
| matrix_rows | **138** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm29_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety` |

## Layer gates

| layer | gate |
|-------|------|
| layer `coverage_invariant_lock` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm28_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `partial_promote_reclass_denial` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `residual_lift_denial` | `PASS_OFFLINE` |
| layer `resume_same_hold_write_boundary` | `PASS_OFFLINE` |

## Scale / safety gain

- FM28 连续：unique=**2249** · status=**2134/106/9** · delta=**2** · coverage=**117** · membership/write-boundary fps
- partial promote/reclass denial：**106** 码 · promote→complete 与跨带 reclass 拒绝
- resume-same hold write-boundary：**301212** · harvest/force_improve/promote 拒绝
- residual lift denial：**9+2** · quarantine/fence lift 拒绝
- coverage invariant lock：**9+2+106=117** · mutation_allowed=false
- MOCK3–30 冻结 · MOCK31 放行

## Hold

```
c_fm_29_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm29_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety/scale_matrix.csv](_mock_c_fm29_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety_20260715.json](cninfo_c_class_scale_partial_promote_reclass_resume_lift_coverage_invariant_safety_20260715.json)
