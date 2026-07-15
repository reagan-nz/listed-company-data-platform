# CNINFO C 类 — Filtered Universe Mock-Root Dry-Run

_生成时间：2026-07-15T06:48:43Z · offline · CNINFO=0_

> **validation/_mock_* only** · **no snapshot JSON** · **execute_production_snapshot_rebuild=false** · **863/phase3/phase35 production snapshot roots untouched** · **batch builder --execute not invoked**

## Inputs

| 项 | 值 |
|----|-----|
| sample mode | `wave1_filtered_universe` |
| sample file | `outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml` |
| exclusion CSV | `(n/a · Wave1 filtered)` |
| harvest root (read-only) | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/` |
| mock output root | `outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun` |

## Counts

| 指标 | 值 |
|------|-----|
| company_count | **190** |
| execution_list | **190** |
| status rows | **190** |
| snapshot JSON writes | **0** |
| builder dry-run gate | `PASS_WITH_CAVEAT` |

## Checks

| check | result |
|-------|--------|
| `universe_ok` | **PASS** |
| `company_count_190` | **PASS** |
| `included_matches_expected` | **PASS** |
| `no_partial7_in_execution` | **PASS** |
| `no_empty_dividend3_in_execution` | **PASS** |
| `no_slice1_excluded_in_execution` | **PASS** |
| `hold_overlap_0` | **PASS** |
| `snapshot_json_writes_0` | **PASS** |
| `status_csv_written` | **PASS** |
| `error_csv_written` | **PASS** |
| `status_row_count_matches` | **PASS** |
| `mock_root_under_validation` | **PASS** |
| `batch_builder_execute_not_invoked` | **PASS** |
| `production_roots_untouched` | **PASS** |

## Gate

```
c_class_erad_filtered_universe_mock_root_dryrun_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
batch_builder_execute_invoked = false
```

**NOT verified** · **NOT production_ready** · **NOT** production snapshot execute

## Documented dry-run command（本轮实际执行 · 程序化 API）

```text
python3 lab/run_cninfo_c_class_filtered_universe_mock_root_dryrun.py \
  --filtered-universe outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
  --output-root outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/
```

内部等价于调用 `run_dry_run(universe_path=..., out_dir=<mock>, ...)`；
不经由会忽略 `--output-root` 的 batch CLI 非 phase35 入口。

## Artifacts

- [outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/dryrun_report.csv](dryrun_report.csv)
- [outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/dryrun_summary.md](dryrun_summary.md)
- [outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/mock_root_dryrun_capability_summary.md](mock_root_dryrun_capability_summary.md)
- [outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/run_meta.json](run_meta.json)
- [outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/quality/company_snapshot_status.csv](quality/company_snapshot_status.csv)

## Capability note

Wave 1 `filtered_universe_included.yaml` / `--exclusion-csv` 语义现可被
**真实 batch `run_dry_run`** 消费，产物仅落在 `outputs/validation/_mock_*`。
