# C-FM-23 Scale Multi-Batch Repro Lineage Hardening

_生成时间：2026-07-15T13:42:09Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-23** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| combined_dryrun_coverage | **1053** |
| fail_count | **0** |
| matrix_rows | **141** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm23_scale_multi_batch_repro_lineage_hardening` |

## Layer gates

| layer | gate |
|-------|------|
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `isolated_combined_dryrun_scale` | `PASS_OFFLINE` |
| layer `multi_batch_harvest_exclusion_dual_layer` | `PASS_OFFLINE` |
| layer `multi_cohort_repro_fingerprint` | `PASS_OFFLINE` |
| layer `output_root_protection_hardening` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `scale_lineage_hardening` | `PASS_OFFLINE` |
| layer `scale_lineage_registry` | `PASS_OFFLINE` |

## Scale jump

- repro：**863 + 190 + 861 + 500 + 500 + 200 + 200** 七层指纹零漂移
- coverage_sum：**3314**（相对 FM22 的 2414 可计量 +900）
- combined dryrun：**863+190=1053** 隔离合标指纹（不 EXECUTE）
- lineage：FM22 packet 连续 + 跨 batch 不相交 / 已知小交集
- protection：MOCK3–24 冻结 · MOCK25 放行 · phase3/phase2/fuller 写拒绝 · C-ROOT-011

## Hold

```
c_fm_23_scale_multi_batch_repro_lineage_hardening_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm23_scale_multi_batch_repro_lineage_hardening/scale_matrix.csv](_mock_c_fm23_scale_multi_batch_repro_lineage_hardening/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_multi_batch_repro_lineage_hardening/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_multi_batch_repro_lineage_hardening_20260715.json](cninfo_c_class_scale_multi_batch_repro_lineage_hardening_20260715.json)
