# CNINFO D 类 shareholder_data First-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-09_

> **性质：** 命令草案 · D-FM-09 shared live-path 已实现 · offline mock PASS · **CNINFO = 0** · **真实 live 未授权**

## S4 dry-run（CNINFO=0）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --shareholder-data-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_data_first_slice
```

## Live（path ready · NOT authorized this task）

```bash
# DO NOT RUN until controller_execution_allowed=true
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

## Status This Task

| 项 | 状态 |
|----|------|
| `--shareholder-data-first-slice` | **已实现** |
| S4 dry-run | **PASS_OFFLINE（5/5 · shared=1）** |
| live path | **READY_FOR_APPROVAL**（offline mock 4/5） |
| live | **NOT_APPROVED**（无真实执行） |
| CNINFO this task | **0** |
