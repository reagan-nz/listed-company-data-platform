# C-FM-31 Scale Failed Promotion + Partial Demotion + Batch Priority + Resume Taxonomy

_生成时间：2026-07-15T14:32:36Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-31** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| union_status | **2134/106/9** |
| overlap_delta | **12** (additive=2261) |
| resume_taxonomy | **28/1/0** |
| batch_priority | **h863>p35>p3>p2>fu** |
| residual_safety_coverage | **117** |
| fail_count | **0** |
| matrix_rows | **147** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm31_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety` |

## Layer gates

| layer | gate |
|-------|------|
| layer `batch_priority_order_freeze` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `failed_promotion_denial` | `PASS_OFFLINE` |
| layer `fm30_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `partial_demotion_to_failed_denial` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `resume_delta_taxonomy_freeze` | `PASS_OFFLINE` |

## Scale / safety gain

- FM30 连续：unique=**2249** · status=**2134/106/9** · Δ12 · complete/partition/winner/overlap fps
- failed promotion denial：**9** 码 · promote→partial/complete 拒绝
- partial demotion-to-failed denial：**106** 码 · demote→failed 拒绝
- batch-priority order freeze：**h863>p35>p3>p2>fu** · reorder 拒绝
- resume-delta taxonomy freeze：**28/1/0** · reclass/mutation 拒绝
- MOCK3–32 冻结 · MOCK33 放行

## Hold

```
c_fm_31_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm31_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety/scale_matrix.csv](_mock_c_fm31_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety_20260715.json](cninfo_c_class_scale_failed_promotion_partial_demotion_batch_priority_resume_taxonomy_safety_20260715.json)
