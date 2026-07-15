# CNINFO D 类 shareholder_data First-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-07_

> **性质：** 命令草案 only · **runner 未实现** · **CNINFO = 0** · **无执行**

## S4 dry-run（future · runner 实现后 · CNINFO=0）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --shareholder-data-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_data_first_slice
```

## Live（future · NOT authorized this task）

```bash
# DO NOT RUN until runner + --approve-d-class-shareholder-data-first-slice
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
| planned | **1**（shared） |

## Status This Task

| 项 | 状态 |
|----|------|
| `--shareholder-data-first-slice` | **未实现** |
| S4 dry-run | **blocked_until_runner** |
| live | **NOT_APPROVED** |
| CNINFO this task | **0** |
