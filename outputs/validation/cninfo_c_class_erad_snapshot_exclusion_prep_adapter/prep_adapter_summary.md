# CNINFO C 类 — Snapshot Exclusion Prep Adapter Dry-Run

_生成时间：2026-07-15T06:28:10Z · offline · CNINFO=0_

> **validation only** · **no snapshot JSON** · **execute_production_snapshot_rebuild=false** · **863/phase3/phase35 production snapshot roots untouched** · **batch builder --execute not invoked**

## Inputs（read-only）

| 项 | 路径 |
|----|------|
| universe | `lab/eval_companies_c_class_fuller_market_slice1_200.yaml` |
| exclusion CSV | `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv` |
| csv_kind | `exclusion_reconcile` |
| output root | `outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter` |

## Counts

| 指标 | 值 |
|------|-----|
| universe | **200** |
| exclusion source rows | **200** |
| excluded (unique) | **10** |
| included (filtered) | **190** |
| partial7 excluded | **7/7** |
| empty_dividend3 excluded | **3/3** |

## Checks

| check | result |
|-------|--------|
| `universe_count_200` | **PASS** |
| `csv_kind_recognized` | **PASS** |
| `partial7_all_excluded` | **PASS** |
| `empty_dividend3_all_excluded` | **PASS** |
| `excluded_unique_10` | **PASS** |
| `included_190` | **PASS** |
| `no_execute_flag` | **PASS** |
| `production_roots_untouched` | **PASS** |

## Gate

```
c_class_erad_snapshot_exclusion_prep_adapter_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
batch_builder_execute_invoked = false
```

**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute

## Artifacts

- [outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/exclusion_filter_report.csv](exclusion_filter_report.csv)
- [outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml](filtered_universe_included.yaml)
- [outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/builder_command_draft.sh](builder_command_draft.sh)
- [outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/run_meta.json](run_meta.json)
- [outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/prep_adapter_summary.md](prep_adapter_summary.md)

## Capability note

Run 11 `exclusion_reconcile.csv` 可直接作为 `--exclusion-csv` 输入喂入本适配器，
产出 filtered universe 与带 `--exclusion-csv` 的 builder dry-run 命令草案。
未向 `build_cninfo_c_class_snapshot_batch.py` 注入生产 execute 能力。
