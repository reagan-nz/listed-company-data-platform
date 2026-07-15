# CNINFO C 类 — Partial7 双层审计 + QA Closure 索引

_生成时间：2026-07-15T08:15:58Z · offline · CNINFO=0_

> **validation only** · **no snapshot JSON** · **execute_production_snapshot_rebuild=false** · **harvest read-only** · **no live** · **closed caveat/metrics untouched** · **empty3 index not overwritten**

## 任务

- task_id: `C-R16-03`
- 目标：机器核验 DLVR-P01–P04，并将 partial7 接入 QA closure 累积双层证据索引；完成 empty3+partial7 共 10 家 caveat 覆盖
- 语义：ledger/audit 双层均为 partial(4/10)；raw 6×http_error/500；security_observe delisted=true；PT 标的仅注解 tradingStatus=0

## Inputs（read-only）

| 项 | 路径 |
|----|------|
| harvest_root | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200` |
| status_csv | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/company_harvest_status.csv` |
| resume_audit_csv | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/reports/c_class_erad_harvest_resume_audit_report.csv` |
| caveat_ledger | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv` |
| offline_matrix | `outputs/validation/cninfo_c_class_partial7_offline_qa_matrix_20260714.csv` |
| dual_layer_matrix | `outputs/validation/cninfo_c_class_dual_layer_rule_matrix_20260714.csv` |
| empty3_index_csv | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_evidence_index.csv` |
| output root | `outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit` |
| qa_index root | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index` |

## Metrics

| 指标 | 值 |
|------|-----|
| partial7 audited | **7/7** |
| rules_all_pass | **7/7** |
| rule_checks PASS | **28** |
| rule_checks FAIL | **0** |
| pt_annotated | **2/2** |
| indexed_pass | **7/7** |
| empty3_indexed_pass (readonly) | **3/3** |
| full_caveat_cohort | **10/10** |
| index_gate | **PASS_OFFLINE** |
| wall_time_ms | **10** |
| wall_time_index_ms | **0** |
| CNINFO calls | **0** |
| capability_gain | **True** |
| ready_for_commit | **True** |

## Partial7 rows

| case_id | code | name | ledger | audit | http_err | delisted | trading | pt | rules_ok |
|---------|------|------|--------|-------|----------|----------|---------|----|----------|
| CE1E002 | 600001 | 邯郸钢铁 | partial/4 | partial/4 | 6 | true | 1 | no | yes |
| CE1E003 | 600005 | 武钢股份 | partial/4 | partial/4 | 6 | true | 1 | no | yes |
| CE1E034 | 600068 | 葛洲坝 | partial/4 | partial/4 | 6 | true | 1 | no | yes |
| CE1E061 | 000003 | PT金田A | partial/4 | partial/4 | 6 | true | 0 | yes | yes |
| CE1E067 | 000015 | PT中浩A | partial/4 | partial/4 | 6 | true | 0 | yes | yes |
| CE1E070 | 000022 | 深赤湾A | partial/4 | partial/4 | 6 | true | 1 | no | yes |
| CE1E071 | 000024 | 招商地产 | partial/4 | partial/4 | 6 | true | 1 | no | yes |

## QA closure dual-layer evidence index (partial7)

| case_id | code | index_status | rules_ok | ledger/audit | pt |
|---------|------|--------------|----------|--------------|----|
| CE1E002 | 600001 | indexed_pass | yes | partial/partial | no |
| CE1E003 | 600005 | indexed_pass | yes | partial/partial | no |
| CE1E034 | 600068 | indexed_pass | yes | partial/partial | no |
| CE1E061 | 000003 | indexed_pass | yes | partial/partial | yes |
| CE1E067 | 000015 | indexed_pass | yes | partial/partial | yes |
| CE1E070 | 000022 | indexed_pass | yes | partial/partial | no |
| CE1E071 | 000024 | indexed_pass | yes | partial/partial | no |

## Cohort coverage（empty3 + partial7）

| family | expected | indexed_pass | status |
|--------|----------|--------------|--------|
| empty_dividend | 3 | 3 | indexed_pass |
| partial | 7 | 7 | indexed_pass |
| all_caveats | 10 | 10 | indexed_pass |

## Checks（present audit）

| check | result |
|-------|--------|
| `partial7_all_rules_pass` | **PASS** |
| `offline_matrix_covers_partial7` | **PASS** |
| `caveat_ledger_covers_partial7` | **PASS** |
| `dual_layer_matrix_covers_dlvr_p01_p04` | **PASS** |
| `pt_two_annotated_trading_status_0` | **PASS** |
| `no_non_pt_trading_status_0` | **PASS** |
| `no_execute_flag` | **PASS** |
| `cninfo_calls_zero` | **PASS** |
| `harvest_read_only` | **PASS** |

## Checks（QA closure index）

| check | result |
|-------|--------|
| `index_covers_partial7` | **PASS** |
| `all_indexed_pass` | **PASS** |
| `caveat_partial7_match_expected` | **PASS** |
| `no_orphan_audit_rows` | **PASS** |
| `no_orphan_caveat_partial_rows` | **PASS** |
| `audit_gate_pass_offline` | **PASS** |
| `empty3_index_preserved_readable` | **PASS** |
| `full_10_caveat_cohort_indexed` | **PASS** |
| `cninfo_calls_zero` | **PASS** |
| `original_caveat_ledger_unmutated` | **PASS** |
| `empty3_index_file_not_overwritten` | **PASS** |

## Gate

```
c_class_partial7_dual_layer_present_audit_gate = PASS_OFFLINE
c_class_qa_closure_dual_layer_partial7_index_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
approved_for_snapshot_rebuild = false
cninfo_calls = 0
original_qa_closure_caveat_ledger_mutated = false
empty3_index_overwritten = false
```

**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute

## Artifacts

- `partial7_dual_layer_present_audit.csv`: [outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit/partial7_dual_layer_present_audit.csv](partial7_dual_layer_present_audit.csv)
- `dual_layer_rule_check_matrix.csv`: [outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit/dual_layer_rule_check_matrix.csv](dual_layer_rule_check_matrix.csv)
- `qa_closure_dual_layer_evidence_index_partial7.csv`: [outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_evidence_index_partial7.csv](qa_closure_dual_layer_evidence_index_partial7.csv)
- `qa_closure_dual_layer_partial7_metrics.csv`: [outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_partial7_metrics.csv](qa_closure_dual_layer_partial7_metrics.csv)
- `qa_closure_dual_layer_cohort_coverage.csv`: [outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_cohort_coverage.csv](qa_closure_dual_layer_cohort_coverage.csv)
- `audit_run_meta.json`: [outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit/run_meta.json](run_meta.json)
- `partial7_run_meta.json`: [outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/partial7_run_meta.json](partial7_run_meta.json)
- `evidence_summary.md`: [outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit/evidence_summary.md](evidence_summary.md)
- `partial7_evidence_summary.md`: [outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/partial7_evidence_summary.md](partial7_evidence_summary.md)

## Capability note

C-R16-03：partial7 DLVR-P01–P04 已机器核验并接入 QA closure 累积证据索引；
empty3 索引保持 sibling 只读；closed caveat_ledger / metrics 未改写；
PT 标的仅注解 tradingStatus=0（不发明 termination sidecar）。

## Allow-list

| 类别 | 路径/动作 |
|------|-----------|
| read | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200` |
| read | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/company_harvest_status.csv` |
| read | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/reports/c_class_erad_harvest_resume_audit_report.csv` |
| read | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv` |
| read | `outputs/validation/cninfo_c_class_partial7_offline_qa_matrix_20260714.csv` |
| read | `outputs/validation/cninfo_c_class_dual_layer_rule_matrix_20260714.csv` |
| read | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index/qa_closure_dual_layer_evidence_index.csv` |
| read | `outputs/validation/cninfo_c_class_dual_layer_validation_rules_20260714.md` |
| read | `outputs/validation/cninfo_c_class_partial7_evidence_completeness_20260714.md` |
| read | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_metrics.csv` |
| read | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_summary.md` |
| write | `outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit` |
| write | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_dual_layer_index` |
| write | `outputs/validation/cninfo_c_class_partial7_dual_layer_present_audit_20260715.md` |
| write | `outputs/validation/cninfo_c_class_partial7_dual_layer_qa_closure_index_20260715.md` |
| write | `lab/cninfo_c_class_partial7_dual_layer_present_audit.py` |
| write | `lab/run_cninfo_c_class_partial7_dual_layer_present_audit_dryrun.py` |
| write | `lab/test_cninfo_c_class_partial7_dual_layer_present_audit.py` |
| forbidden | `overwrite qa_closure_dual_layer_evidence_index.csv (empty3)` |
| forbidden | `build_cninfo_c_class_snapshot_batch.py --execute` |
| forbidden | `execute_production_snapshot_rebuild=true` |
| forbidden | `CNINFO live` |
| forbidden | `commit` |
| forbidden | `push` |
| forbidden | `harvest mutation` |
| forbidden | `mutate qa_closure_caveat_ledger.csv` |
| forbidden | `mutate qa_closure_metrics.csv` |

