# CNINFO D 类 abnormal_trading First-Slice — Command Draft

_生成时间：2026-07-15 · D-FM-03_

## S4 dry-run（authorized this task · CNINFO=0）

```bash
cd listed_company_data_collector
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --abnormal-trading-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_first_slice
```

## Live（NOT authorized · controller_execution_allowed=false）

```bash
# DO NOT RUN
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --abnormal-trading-first-slice \
  --approve-d-class-abnormal-trading-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_first_slice
```

Live path 本任务为 **`abnormal_trading_first_slice_live_not_implemented`**（批准后仍拒绝 CNINFO）。
