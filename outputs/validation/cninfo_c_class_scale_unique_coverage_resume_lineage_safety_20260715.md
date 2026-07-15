# C-FM-24 Scale Unique-Coverage + Resume Lineage Safety

_生成时间：2026-07-15T13:49:48Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-24** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| harvest_additive | **2261** |
| overlap_delta | **12** |
| surface_unique | **2251** |
| resume_total | **29** |
| fail_count | **0** |
| matrix_rows | **135** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm24_scale_unique_coverage_resume_lineage_safety` |

## Layer gates

| layer | gate |
|-------|------|
| layer `dryrun_surface_unique` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm23_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `resume_lineage_safety` | `PASS_OFFLINE` |
| layer `seven_tier_repro_reaffirm` | `PASS_OFFLINE` |
| layer `unique_coverage_reconciliation` | `PASS_OFFLINE` |

## Scale / safety gain

- unique vs additive：**2249 unique** · **2261 additive** · **delta=12**
- pairwise 交集矩阵指纹冻结；四 batch union **1388** 连续
- dryrun∪harvest 表面 unique：**2251**（dry863 多出 000037/000055）
- phase35 resume：**29 ⊆ p35** · complete=28/partial=1 · 写拒绝
- FM23 连续：coverage_sum=3314 · tiers=7 · MOCK25 冻结 · MOCK26 放行

## Hold

```
c_fm_24_scale_unique_coverage_resume_lineage_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm24_scale_unique_coverage_resume_lineage_safety/scale_matrix.csv](_mock_c_fm24_scale_unique_coverage_resume_lineage_safety/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_unique_coverage_resume_lineage_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_unique_coverage_resume_lineage_safety_20260715.json](cninfo_c_class_scale_unique_coverage_resume_lineage_safety_20260715.json)
