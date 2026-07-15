# C-FM-22 Scale Harvest-Exclusion Repro Fingerprint

_生成时间：2026-07-15T13:36:04Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-22** |
| gate | **PASS_OFFLINE** |
| scale_tier_count | **4** |
| company_coverage_sum | **2414** |
| fail_count | **0** |
| matrix_rows | **105** |
| cninfo_calls | **0** |
| mock output | `outputs/validation/_mock_c_fm22_scale_harvest_exclusion_repro_fingerprint` |

## Layer gates

| layer | gate |
|-------|------|
| layer `execute_hold_seal` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `multi_cohort_repro_fingerprint` | `PASS_OFFLINE` |
| layer `output_root_protection_hardening` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `scale_harvest_exclusion_dual_layer` | `PASS_OFFLINE` |
| layer `scale_lineage_registry` | `PASS_OFFLINE` |

## Scale jump

- dual-layer：slice1(200) → **phase35×500** family 交叉
- repro：**863 + 190 + 861 + 500** 四层指纹零漂移
- coverage_sum：**2414**（可计量 registry/scale jump）
- protection：MOCK3–23 冻结 · MOCK24 放行 · phase35/863 harvest 写拒绝

## Hold

```
c_fm_22_scale_harvest_exclusion_repro_fingerprint_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm22_scale_harvest_exclusion_repro_fingerprint/scale_matrix.csv](_mock_c_fm22_scale_harvest_exclusion_repro_fingerprint/scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_harvest_exclusion_repro_fingerprint/scale_matrix.csv](scale_matrix.csv)
- [outputs/validation/cninfo_c_class_scale_harvest_exclusion_repro_fingerprint_20260715.json](cninfo_c_class_scale_harvest_exclusion_repro_fingerprint_20260715.json)
