# C-FM-33 Scale Union Partition + Overlap + Residual + Resume Same/Worse

_生成时间：2026-07-15T14:53:12Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-33** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| harvest_additive | **2261** |
| surface_unique | **2251** |
| union_status | **2134/106/9** |
| overlap_delta | **12** |
| resume_taxonomy | **28/1/0** |
| residual_safety_coverage | **117** |
| fail_count | **0** |
| matrix_rows | **147** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm33_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm32_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `overlap_delta_cardinality_freeze` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `residual_safety_coverage_lock` | `PASS_OFFLINE` |
| layer `resume_same_worse_write_boundary` | `PASS_OFFLINE` |
| layer `union_status_partition_cardinality_freeze` | `PASS_OFFLINE` |

## Scale / safety gain

- FM32 连续：unique=**2249** · status=**2134/106/9** · surface=**2251** · additive=**2261** · tier=**7/3314** · resume-improved/surface/additive/tier fps
- union status partition cardinality freeze：**2134/106/9** · partition mutation 拒绝
- overlap_delta cardinality freeze：**12** · inflate/deflate 拒绝
- residual_safety_coverage lock：**117** · mutation_allowed=false
- resume_same/worse write-boundary：**1/0**（301212）· force_improve/reclass/inject_worse 拒绝
- MOCK3–34 冻结 · MOCK35 放行

## Hold

```
c_fm_33_scale_union_partition_overlap_residual_resume_same_worse_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm33_cli_test_tmp/scale_matrix.csv](_mock_c_fm33_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety_20260715.json](cninfo_c_class_scale_union_partition_overlap_residual_resume_same_worse_safety_20260715.json)
