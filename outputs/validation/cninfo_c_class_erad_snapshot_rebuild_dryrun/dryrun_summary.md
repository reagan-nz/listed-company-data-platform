# CNINFO C 类 — Snapshot Exclusion Reconcile Dry-Run

_生成时间：2026-07-15T06:13:35Z · offline · CNINFO=0_

> **validation only** · **no snapshot JSON** · **execute_production_snapshot_rebuild=false** · **863/phase3/phase35 production snapshot roots untouched**

## Inputs（read-only）

| 项 | 路径 |
|----|------|
| universe | `lab/eval_companies_c_class_fuller_market_slice1_200.yaml` |
| exclusion CSV | `outputs/validation/cninfo_c_class_snapshot_progression_exclusion_universe_20260714.csv` |
| status ledger | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/company_harvest_status.csv` |
| output root | `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun` |

## Counts

| 指标 | 值 |
|------|-----|
| universe | **200** |
| exclusion CSV rows | **19** |
| exclusion rows applicable | **11** |
| exclusion unique in universe | **10** |
| excluded (unique) | **10** |
| partial7 excluded | **7/7** |
| empty_dividend3 excluded | **3/3** |
| included_complete_pool | **190** |
| included_non_complete | **0** |
| missing_ledger | **0** |

## Checks

| check | result |
|-------|--------|
| `universe_count_200` | **PASS** |
| `exclusion_csv_rows_19` | **PASS** |
| `partial7_all_excluded` | **PASS** |
| `empty_dividend3_all_excluded` | **PASS** |
| `excluded_unique_10` | **PASS** |
| `complete_pool_190` | **PASS** |
| `no_promotion_yes` | **PASS** |
| `all_rows_reconcile_ok` | **PASS** |
| `no_non_complete_leaks` | **PASS** |
| `no_missing_ledger` | **PASS** |

## Gate

```
c_class_erad_snapshot_rebuild_dryrun_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
```

**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute

## Artifacts

- [outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv](exclusion_reconcile.csv)
- [outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/run_meta.json](run_meta.json)
- [outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/dryrun_summary.md](dryrun_summary.md)

## Capability note

本工具补齐 mock rebuild plan 中的 `exclusion_reconcile.csv` 离线对账路径；
不向 `build_cninfo_c_class_snapshot_batch.py` 写入生产执行能力，
亦不启用 `--execute` / 生产 snapshot 根。
