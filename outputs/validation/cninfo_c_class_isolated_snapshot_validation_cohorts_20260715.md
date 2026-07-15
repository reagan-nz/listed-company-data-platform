# CNINFO C 类 — 隔离 Snapshot 校验 Cohort + Lineage

_生成时间：2026-07-15T09:01:28Z · executor: c-class-executor · offline · CNINFO=0_

| 字段 | 值 |
|------|-----|
| task_id | **C-FM-02** |
| gate | `PASS_OFFLINE` |
| cohort `slice1_190_included` | `PASS_OFFLINE` |
| cohort `slice1_caveat10_negative_control` | `PASS_OFFLINE` |
| cohort `standard_isolated_fingerprint` | `PASS_OFFLINE` |
| cninfo_calls | **0** |
| execute_production_snapshot_rebuild | **false** |

## Slice1 190 included cohort

| 指标 | 值 |
|------|-----|
| output_root | `outputs/validation/_mock_c_fm02_slice1_190_validation_cohort` |
| included_count | **190** |
| excluded_control_count | **10** |
| fingerprint_reproducible | **True** |
| fingerprint_sha256 | `6dc30af0fe8e8ade2f10da8599891005fde0158e324c9a1273112a461f04971c` |
| builder_gate | `PASS_WITH_CAVEAT` |
| lineage_matrix | `outputs/validation/_mock_c_fm02_slice1_190_validation_cohort/cohort_lineage_matrix.csv` |

## Checks

| check | result |
|-------|--------|
| `included_count_matches` | **PASS** |
| `included_lineage_all_ok` | **PASS** |
| `excluded_negative_control_all_ok` | **PASS** |
| `excluded_count_matches` | **PASS** |
| `no_lineage_failures` | **PASS** |
| `partial7_covered` | **PASS** |
| `empty_dividend3_covered` | **PASS** |
| `fingerprint_reproducible` | **PASS** |
| `dryrun_universe_ok` | **PASS** |
| `source_universe_200` | **PASS** |
| `excluded_codes_match_filter` | **PASS** |

## Standard isolated fingerprint cohort (C-FM-01 artifact)

- output_root: `outputs/validation/_mock_snapshot_batch_standard_dryrun_isolated`
- status_rows: **863**
- fingerprint_sha256: `1e27691bb0f1204e285def02510b07c282c86267cd292f5cfaaf167bcc272392`
- gate: `PASS_OFFLINE`

| check | result |
|-------|--------|
| `artifacts_present` | **PASS** |
| `status_rows_positive` | **PASS** |
| `fingerprint_nonempty` | **PASS** |
| `content_sha256_nonempty` | **PASS** |
| `cninfo_calls_zero` | **PASS** |
| `execute_flag_false` | **PASS** |

## Gate

```
c_fm_02_isolated_snapshot_validation_cohorts_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
```

**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute

## Artifacts

- [outputs/validation/cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json](cninfo_c_class_isolated_snapshot_validation_cohorts_20260715.json)
- [outputs/validation/cninfo_c_class_isolated_snapshot_validation_cohorts/cohort_lineage_matrix.csv](cohort_lineage_matrix.csv)
- [outputs/validation/_mock_c_fm02_slice1_190_validation_cohort/](outputs/validation/_mock_c_fm02_slice1_190_validation_cohort/)

