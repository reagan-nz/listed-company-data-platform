# CNINFO D 类 abnormal_trading Further-Scale S200 — Command Draft

_生成时间：2026-07-16 · D-FM-04_

## Universe cite

```bash
.venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale_s200.py \
  --build-universe-lock
```

## Dry-run（CNINFO=0）

```bash
.venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale_s200.py \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200
```

## Bounded live（CNINFO=2 · 按日共享）

```bash
.venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale_s200.py \
  --live \
  --approve-d-class-abnormal-trading-further-scale-s200 \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s200
```

## Package facts

| 项 | 值 |
|----|-----|
| cohort | DAT301–DAT500 · **200** |
| compose | primary 2026-07-02 · 156 + adjacent 2026-07-01 · 39 + empty · 5 |
| dry-run CNINFO | 0 |
| live CNINFO | 2 |
| acceptable | 200/200 |
| excellence | YES |
