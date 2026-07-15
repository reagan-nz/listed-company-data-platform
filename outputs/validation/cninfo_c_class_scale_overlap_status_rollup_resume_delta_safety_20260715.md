# C-FM-25 Scale Overlap Status Rollup + Resume Delta Safety

_生成时间：2026-07-15T13:56:03Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-25** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **7** |
| company_coverage_sum | **3314** |
| harvest_unique_union | **2249** |
| overlap_delta | **12** |
| union_status | **2134/106/9** |
| resume_delta | **28/1/0** |
| surface_unique | **2251** |
| fail_count | **0** |
| matrix_rows | **127** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm25_scale_overlap_status_rollup_resume_delta_safety` |

## Layer gates

| layer | gate |
|-------|------|
| layer `dry863_extra_isolation` | `PASS_OFFLINE` |
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm24_continuity` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `harvest_status_rollup` | `PASS_OFFLINE` |
| layer `output_root_protection` | `PASS_OFFLINE` |
| layer `overlap_code_ledger` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `resume_delta_safety` | `PASS_OFFLINE` |

## Scale / safety gain

- FM24 连续：unique=**2249** · surface=**2251** · resume=**29**
- 精确 overlap 台账：p35∩fu={000003} · p2∩fu=11 码 · Δ12 指纹冻结
- unique status rollup：**2134 complete / 106 partial / 9 failed**
- resume vs base delta：**28 improved / 1 same(301212) / 0 worse** · 写拒绝
- dry863 extras={000037,000055}：不在 harvest · 不在 exclusion · pending
- MOCK3–26 冻结 · MOCK27 放行

## Hold

```
c_fm_25_scale_overlap_status_rollup_resume_delta_safety_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm25_scale_overlap_status_rollup_resume_delta_safety/scale_matrix.csv](_mock_c_fm25_scale_overlap_status_rollup_resume_delta_safety/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety_20260715.json](cninfo_c_class_scale_overlap_status_rollup_resume_delta_safety_20260715.json)
