# CNINFO D 类 abnormal_trading Further-Scale — Command Draft

_生成时间：2026-07-16 · D-FM-03_

> runner **已实现** · universe lock **已锁** · S4 dry-run **PASS_OFFLINE** · bounded live **已执行**（50/50）· **不是 verified**

## Universe cite（已执行 · CNINFO=1）

```bash
cd listed_company_data_collector
.venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale.py \
  --build-universe-lock
```

## Dry-run（已执行 · CNINFO=0）

```bash
.venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale.py \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_further_scale
```

## Live（已执行 · CNINFO=1 · R19 standing）

```bash
.venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale.py \
  --live \
  --approve-d-class-abnormal-trading-further-scale \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_further_scale
```

## Status

| 项 | 状态 |
|----|------|
| cohort | DAT201–DAT250 · **50** |
| dry-run | **PASS_OFFLINE** · CNINFO=0 |
| live | **PASS_WITH_CAVEAT** · 50/50 · found=48 · empty=2 · CNINFO=1 |
| package CNINFO | **2**（cite+live） |
| frozen AT/ESH/SC/EP/RSU/FIA roots | **未 mutate** |
