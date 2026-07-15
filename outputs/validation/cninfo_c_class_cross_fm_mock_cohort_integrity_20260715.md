# C-FM-05 Cross-FM Mock Cohort Integrity

_生成时间：2026-07-15T09:31:20Z · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-05** |
| gate | `PASS_OFFLINE` |
| layer `fingerprint_chain` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `mock_cohort_registry` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `protected_write_guard` | `PASS_OFFLINE` |
| fail_count | **0** / 33 |
| mock output | `outputs/validation/_mock_c_fm05_cross_fm_mock_cohort_integrity` |
| integrity fingerprint | `b11a394ede6071e1ba60e5ee1e1f518f91789e31364b48d14a300bf485c54d4b` |

## Capability

1. FM-01..04 mock cohort 注册表（存在 · 隔离 · 必要产物）
2. 指纹链只读核验（dry-run / 863 / lineage；不重跑 dry-run）
3. 保护根写守卫 battery（harvest / snapshot / 权威 dual-layer）
4. protected_output_roots.csv 注册一致性（MOCK3–7 · AUTH1）
5. FM-01..04 gate battery 只读聚合

## Inputs (read-only)

| 输入 | 路径 |
|------|------|
| `fm01_gate_json` | `outputs/validation/cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.json` |
| `fm02_gate_json` | `outputs/validation/cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json` |
| `fm03_gate_json` | `outputs/validation/cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json` |
| `fm04_gate_json` | `outputs/validation/cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.json` |
| `protected_roots_csv` | `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` |
| `harvest_863_status` | `outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv` |

## Wall

```
c_fm_05_cross_fm_mock_cohort_integrity_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
ready_for_commit = true
```

## Artifacts

- [outputs/validation/_mock_c_fm05_cross_fm_mock_cohort_integrity/integrity_matrix.csv](_mock_c_fm05_cross_fm_mock_cohort_integrity/integrity_matrix.csv)
- [outputs/validation/cninfo_c_class_cross_fm_mock_cohort_integrity/integrity_matrix.csv](cninfo_c_class_cross_fm_mock_cohort_integrity/integrity_matrix.csv)
- [outputs/validation/cninfo_c_class_cross_fm_mock_cohort_integrity_20260715.json](cninfo_c_class_cross_fm_mock_cohort_integrity_20260715.json)
