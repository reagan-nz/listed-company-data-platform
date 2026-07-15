# C-FM-30 Scale Complete Demotion + Partition + Winner + Overlap Freeze

_生成时间：2026-07-15T14:24:49Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-30** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| union_status | **2134/106/9** |
| overlap_delta | **12** (additive=2261) |
| surface_harvest_delta | **2** (000037,000055) |
| resume_same | **1** (301212) |
| residual_safety_coverage | **117** (9+2+106) |
| complete_codes_sha256 | `45beb7732efff04f…` |
| winner_map_sha256 | `ff2c6a28b361498b…` |
| fail_count | **0** |
| matrix_rows | **144** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm30_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety` |

## Layer gates

| layer | gate |
|-------|------|
| layer `complete_demotion_denial` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm29_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `overlap_delta_surface_injection_freeze` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `status_partition_invariant_lock` | `PASS_OFFLINE` |
| layer `winner_provenance_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM29 连续：unique=**2249** · status=**2134/106/9** · delta=**2** · coverage=**117** · promote/resume/lift/coverage fps
- complete demotion denial：**2134** 码 · demote→partial/failed 拒绝
- status partition invariant：**2134+106+9=2249** · mutation_allowed=false
- winner provenance lock：**2249** 码 · winning-batch reassign 拒绝
- overlap-delta / surface-injection freeze：**Δ12** · dry863 extras 注入 harvest 拒绝
- MOCK3–31 冻结 · MOCK32 放行

## Hold

```
c_fm_30_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm30_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety/scale_matrix.csv](_mock_c_fm30_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety_20260715.json](cninfo_c_class_scale_complete_demotion_partition_winner_provenance_overlap_freeze_safety_20260715.json)
