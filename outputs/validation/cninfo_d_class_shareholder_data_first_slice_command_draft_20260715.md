# CNINFO D 类 shareholder_data First-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-14 更新_

> **性质：** runner **已实现** · S4 dry-run **已跑** · bounded live **已执行**（D-FM-14 · CNINFO counted=1 · 5/5 PASS_WITH_CAVEAT）

## S4 dry-run（CNINFO=0）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --shareholder-data-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_data_first_slice
```

## Live（D-FM-14 已执行 · 勿无界重跑）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --shareholder-data-first-slice \
  --approve-d-class-shareholder-data-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_data_first_slice
```

## Request Model（locked contract）

| 项 | 值 |
|----|-----|
| query_mode | `rdate_report_period` |
| rdate | `20260331` |
| prefer | **1 shared** CNINFO 全市场截面 · 离线按 SECCODE 过滤 DSD001–DSD005 |
| total cap | ≤ **5** |
| planned / live shared | **1**（`SHARED_RDATE`） |
| params_location | registry `query`（rdate 正常发出） |

## Status This Task（D-FM-14）

| 项 | 状态 |
|----|------|
| `--shareholder-data-first-slice` | **已实现** |
| S4 dry-run | **PASS_OFFLINE（5/5 · shared=1）** |
| live path | **READY_FOR_APPROVAL** |
| bounded live | **EXECUTED** · counted CNINFO=**1** · acceptable=**5/5** · `PASS_WITH_CAVEAT` |
| live_gate | **NOT_APPROVED**（常量） |
