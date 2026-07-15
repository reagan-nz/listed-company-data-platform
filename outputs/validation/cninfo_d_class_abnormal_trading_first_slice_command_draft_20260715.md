# CNINFO D 类 abnormal_trading First-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-15 更新_

> **性质：** runner **已实现** · S4 dry-run **已跑** · bounded live **已执行**（D-FM-15 · CNINFO counted=5 · 4/5 PASS_WITH_CAVEAT）

## S4 dry-run（CNINFO=0）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --abnormal-trading-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_first_slice
```

## Live（D-FM-15 已执行 · 勿无界重跑）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --abnormal-trading-first-slice \
  --approve-d-class-abnormal-trading-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_first_slice
```

## Request Model（locked contract）

| 项 | 值 |
|----|-----|
| query_mode | `single_day_paged` |
| anchor_tdate | `2026-07-03`（sdate=edate） |
| records_path | `marketList` · 公司过滤 |
| prefer | **5** 独立 per-case 请求 · per-case ≤1 · total ≤20 |
| planned / live counted | **5** |
| detail[] nested | **deferred** |

## Status This Task（D-FM-15）

| 项 | 状态 |
|----|------|
| `--abnormal-trading-first-slice` | **已实现** |
| S4 dry-run | **PASS_OFFLINE（5/5 planned）** |
| live path | **READY_FOR_APPROVAL** |
| bounded live | **EXECUTED** · counted CNINFO=**5** · acceptable=**4/5** · `PASS_WITH_CAVEAT` |
| live_gate | **NOT_APPROVED**（常量） |
| DAT001 caveat | sparse-day `expectation_mismatch`（空行 vs captured_normal_or_needs_review） |
