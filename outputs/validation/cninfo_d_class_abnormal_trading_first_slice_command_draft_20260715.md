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

## Live（path implemented · NOT authorized this task · controller_execution_allowed=false）

```bash
# DO NOT RUN until controller_execution_allowed
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --abnormal-trading-first-slice \
  --approve-d-class-abnormal-trading-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_first_slice
```

Live path 已实现（D-FM-05）；无批准拒绝；有批准将发 CNINFO（≤5）。本任务仅 offline mock，**未**跑真实 live。
