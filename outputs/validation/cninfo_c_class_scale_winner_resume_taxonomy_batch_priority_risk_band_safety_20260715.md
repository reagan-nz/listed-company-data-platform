# C-FM-35 Scale Winner + Resume-Taxonomy + Batch-Priority + Risk-Band

_生成时间：2026-07-15T15:12:52Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-35** |
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
| fail_count | **0** |
| matrix_rows | **153** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm35_cli_test_tmp` |

## Layer gates

| layer | gate |
|-------|------|
| layer `batch_priority_order_freeze` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm34_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `partial_risk_band_cardinality_freeze` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `resume_taxonomy_codeset_sha256_lock` | `PASS_OFFLINE` |
| layer `winner_map_sha256_lock` | `PASS_OFFLINE` |

## Scale / safety gain

- FM34 连续：unique=**2249** · dryrun=**1053** · Δ2 · status=**2134/106/9** · resume=**28/1/0** · dry863/combined/cross/partition fps
- winner_map_sha256_lock：mutation 拒绝
- resume_taxonomy_codeset_sha256_lock：**28/1/0** · improved/same/worse SHA256
- batch_priority_order_freeze：h863>p35>p3>p2>fu · reorder/inject/drop 拒绝
- partial_risk_band_cardinality_freeze：**75/14/12/5**（sum=106）
- MOCK3–36 冻结 · MOCK37 放行

## Hold

```
c_fm_35_scale_winner_resume_taxonomy_batch_priority_risk_band_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm35_cli_test_tmp/scale_matrix.csv](_mock_c_fm35_cli_test_tmp/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety_20260715.json](cninfo_c_class_scale_winner_resume_taxonomy_batch_priority_risk_band_safety_20260715.json)
