# C-FM-13 Non-seal Cross-FM Mock Cohort Integrity Extension

_生成时间：2026-07-15T12:16:13Z · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-13** |
| gate | `PASS_OFFLINE` |
| layer `fingerprint_chain` | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `frozen_mock_isolation` | `PASS_OFFLINE` |
| layer `harvest_exclusion_consistency` | `PASS_OFFLINE` |
| layer `nonseal_cohort_registry` | `PASS_OFFLINE` |
| layer `protected_csv_registry` | `PASS_OFFLINE` |
| layer `protected_write_guard` | `PASS_OFFLINE` |
| fail_count | **0** / 69 |
| mock output | `outputs/validation/_mock_c_fm13_nonseal_cross_fm_mock_cohort_extension` |
| extension fingerprint | `3d9354e2571b46b5d67787b43aada270882d827bf00d7f91f8d3154c6da5d8ff` |

## Capability

1. 非 seal mock cohort 注册表扩展（FM-01..05 + FM-12）
2. 指纹链只读核验（含 FM-05 integrity / FM-12 isolation）
3. 冻结 mock 写隔离（MOCK3–14 拒绝；MOCK15 / ephemeral 放行）
4. harvest/exclusion dual-layer 一致性（FM-03）
5. protected CSV MOCK15 注册一致性
6. FM-01..05 + FM-12 gate battery（跳过 seal FM06–11）

## Inputs (read-only)

| 输入 | 路径 |
|------|------|
| `fm01_gate_json` | `outputs/validation/cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.json` |
| `fm02_gate_json` | `outputs/validation/cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json` |
| `fm03_gate_json` | `outputs/validation/cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json` |
| `fm04_gate_json` | `outputs/validation/cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.json` |
| `fm05_gate_json` | `outputs/validation/cninfo_c_class_cross_fm_mock_cohort_integrity_20260715.json` |
| `fm12_gate_json` | `outputs/validation/cninfo_c_class_dryrun_fingerprint_lineage_isolation_20260715.json` |
| `protected_roots_csv` | `outputs/validation/cninfo_c_class_erad_protected_output_roots.csv` |
| `harvest_863_status` | `outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv` |
| `fm03_mock_root` | `outputs/validation/_mock_c_fm03_harvest_exclusion_dual_layer_consistency` |
| `fm05_mock_root` | `outputs/validation/_mock_c_fm05_cross_fm_mock_cohort_integrity` |
| `fm12_mock_root` | `outputs/validation/_mock_c_fm12_dryrun_fingerprint_lineage_isolation` |

## Wall

```
c_fm_13_nonseal_cross_fm_mock_cohort_extension_gate = PASS_OFFLINE
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

- [outputs/validation/_mock_c_fm13_nonseal_cross_fm_mock_cohort_extension/extension_matrix.csv](_mock_c_fm13_nonseal_cross_fm_mock_cohort_extension/extension_matrix.csv)
- [outputs/validation/cninfo_c_class_nonseal_cross_fm_mock_cohort_extension/extension_matrix.csv](cninfo_c_class_nonseal_cross_fm_mock_cohort_extension/extension_matrix.csv)
- [outputs/validation/cninfo_c_class_nonseal_cross_fm_mock_cohort_extension_20260715.json](cninfo_c_class_nonseal_cross_fm_mock_cohort_extension_20260715.json)
