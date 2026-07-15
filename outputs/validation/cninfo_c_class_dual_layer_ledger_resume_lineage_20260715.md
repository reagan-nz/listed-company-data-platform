# C-FM-04 Ledger / Resume-audit Dual-layer Lineage

_生成时间：2026-07-15T09:14:10Z · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-04** |
| gate | `PASS_OFFLINE` |
| layer `fm_gate_battery` | `PASS_OFFLINE` |
| layer `index_write_isolation` | `PASS_OFFLINE` |
| layer `ledger_resume_caveat` | `PASS_OFFLINE` |
| layer `resume_aggregate` | `PASS_OFFLINE` |
| fail_count | **0** / 21 |
| mock output | `outputs/validation/_mock_c_fm04_dual_layer_ledger_resume_lineage` |
| lineage fingerprint | `96d6fcaa48cc101f17c4f29fd597520c9e71e7c88593919d93b92d4d0aac601c` |

## Capability

1. ledger↔resume-audit 双层语义（empty3 合法分歧 · partial7 双层一致）
2. resume↔dual-layer index↔exclusion pool 交叉 lineage
3. 权威 dual-layer 索引写隔离硬化
4. FM-01/02/03 gate battery 只读聚合
5. mock cohort：lineage 矩阵 + 指纹

## Inputs (read-only)

| 输入 | 路径 |
|------|------|
| `harvest_root` | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200` |
| `resume_audit_report` | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/reports/c_class_erad_harvest_resume_audit_report.csv` |
| `resume_audit_metrics` | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/reports/c_class_erad_harvest_resume_audit_metrics.csv` |
| `exclusion_reconcile` | `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv` |
| `empty3_index` | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_evidence_index.csv` |
| `partial7_index` | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_evidence_index_partial7.csv` |
| `fm01_gate_json` | `outputs/validation/cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.json` |
| `fm02_gate_json` | `outputs/validation/cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json` |
| `fm03_gate_json` | `outputs/validation/cninfo_c_class_harvest_exclusion_dual_layer_consistency_20260715.json` |

## Wall

```
c_fm_04_dual_layer_ledger_resume_lineage_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
ready_for_commit = true
```

## Artifacts

- [outputs/validation/_mock_c_fm04_dual_layer_ledger_resume_lineage/lineage_matrix.csv](_mock_c_fm04_dual_layer_ledger_resume_lineage/lineage_matrix.csv)
- [outputs/validation/cninfo_c_class_dual_layer_ledger_resume_lineage/lineage_matrix.csv](cninfo_c_class_dual_layer_ledger_resume_lineage/lineage_matrix.csv)
- [outputs/validation/cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.json](cninfo_c_class_dual_layer_ledger_resume_lineage_20260715.json)
