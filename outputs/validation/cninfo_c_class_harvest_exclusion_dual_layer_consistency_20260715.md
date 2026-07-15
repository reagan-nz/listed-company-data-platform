# C-FM-03 Harvest / Exclusion / Dual-layer Consistency

_生成时间：2026-07-15T09:08:10Z · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-03** |
| gate | `PASS_OFFLINE` |
| layer `dual_layer_cohort` | `PASS_OFFLINE` |
| layer `harvest_863_structural` | `PASS_OFFLINE` |
| layer `harvest_exclusion_family` | `PASS_OFFLINE` |
| layer `manifest_reconcile` | `PASS_OFFLINE` |
| fail_count | **0** / 39 |
| mock output | `outputs/validation/_mock_c_fm03_cli_test_tmp` |
| 863 fingerprint | `b25006b906a7ad14a96c703a896dd7fc18741d2c3e03886e87c01b898ba76278` |

## Capability

1. 家族感知 harvest↔exclusion（partial7=`partial` · empty3=`complete` 但出 pool）
2. dual-layer cohort 工具：empty3+partial7 索引并集 = caveat10 · coverage 10/10
3. manifest↔reconcile：holdout9 不膨胀 slice1 排除集
4. 更大 mock：863 harvest ledger 只读结构核验 + 隔离指纹

## Inputs (read-only)

| 输入 | 路径 |
|------|------|
| `slice1_harvest_status` | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/company_harvest_status.csv` |
| `harvest_863_status` | `outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv` |
| `exclusion_manifest` | `outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv` |
| `exclusion_reconcile` | `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv` |
| `empty3_index` | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_evidence_index.csv` |
| `partial7_index` | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_evidence_index_partial7.csv` |
| `cohort_coverage` | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_cohort_coverage.csv` |

## Wall

```
c_fm_03_harvest_exclusion_dual_layer_consistency_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
ready_for_commit = true
```

## Artifacts

- [outputs/validation/_mock_c_fm03_cli_test_tmp/consistency_matrix.csv](_mock_c_fm03_cli_test_tmp/consistency_matrix.csv)
- [outputs/validation/cninfo_c_class_harvest_exclusion_dual_layer_consistency/consistency_matrix.csv](cninfo_c_class_harvest_exclusion_dual_layer_consistency/consistency_matrix.csv)
- [outputs/validation/cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json](cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json)
