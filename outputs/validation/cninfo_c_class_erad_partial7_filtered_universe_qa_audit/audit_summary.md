# CNINFO C 类 — Partial7 × Wave1 Filtered Universe QA 审计

_生成时间：2026-07-15T06:37:27Z · offline · CNINFO=0_

> **validation only** · **no snapshot JSON** · **execute_production_snapshot_rebuild=false** · **harvest untouched** · **no live**

## Inputs（read-only）

| 项 | 路径 |
|----|------|
| filtered_universe | `outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml` |
| caveat_ledger | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv` |
| exclusion_reconcile | `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv` |
| offline_qa_matrix | `outputs/validation/cninfo_c_class_partial7_offline_qa_matrix_20260714.csv` |
| output root | `outputs/validation/cninfo_c_class_erad_partial7_filtered_universe_qa_audit` |

## Counts

| 指标 | 值 |
|------|-----|
| filtered included | **190** |
| partial7 audited | **7/7** |
| reason_reconcile_ok | **7/7** |
| leaked into filtered | **0** |

## Partial7 rows

| case_id | code | name | in_filtered | caveat_class | reason_ok |
|---------|------|------|-------------|--------------|-----------|
| CE1E002 | 600001 | 邯郸钢铁 | no | delisted_or_merged_partial_normalized | yes |
| CE1E003 | 600005 | 武钢股份 | no | delisted_or_merged_partial_normalized | yes |
| CE1E034 | 600068 | 葛洲坝 | no | delisted_or_merged_partial_normalized | yes |
| CE1E061 | 000003 | PT金田A | no | delisted_or_merged_partial_normalized | yes |
| CE1E067 | 000015 | PT中浩A | no | delisted_or_merged_partial_normalized | yes |
| CE1E070 | 000022 | 深赤湾A | no | delisted_or_merged_partial_normalized | yes |
| CE1E071 | 000024 | 招商地产 | no | delisted_or_merged_partial_normalized | yes |

## Checks

| check | result |
|-------|--------|
| `filtered_universe_count_190` | **PASS** |
| `partial7_none_in_filtered_included` | **PASS** |
| `partial7_all_reason_reconcile_ok` | **PASS** |
| `qa_matrix_covers_partial7` | **PASS** |
| `ledger_covers_partial7` | **PASS** |
| `no_execute_flag` | **PASS** |
| `cninfo_calls_zero` | **PASS** |

## Gate

```
c_class_erad_partial7_filtered_universe_qa_audit_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
```

**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute

## Artifacts

- [outputs/validation/cninfo_c_class_erad_partial7_filtered_universe_qa_audit/partial7_reason_reconcile.csv](partial7_reason_reconcile.csv)
- [outputs/validation/cninfo_c_class_erad_partial7_filtered_universe_qa_audit/partial7_offline_qa_matrix_hardened.csv](partial7_offline_qa_matrix_hardened.csv)
- [outputs/validation/cninfo_c_class_erad_partial7_filtered_universe_qa_audit/run_meta.json](run_meta.json)
- [outputs/validation/cninfo_c_class_erad_partial7_filtered_universe_qa_audit/audit_summary.md](audit_summary.md)

## Capability note

Wave 1 `filtered_universe_included.yaml` 现可被本离线审计消费：
验证 partial7 不泄漏进 included 池，并对齐 caveat ledger / reconcile / QA matrix 原因字段。

