# D-FM-05 / S1000 Command Draft

_生成时间：2026-07-16 · 仅记录已执行命令；executor 不 commit/push_

```bash
cd listed_company_data_collector-worktrees/d-class

# 1) universe cite + lock（CNINFO=14）
.venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale_s1000.py \
  --build-universe-lock

# 2) dry-run（CNINFO=0）
.venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale_s1000.py \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s1000_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s1000

# 3) tests（offline）
.venv/bin/python lab/test_cninfo_d_class_abnormal_trading_further_scale_s1000_runner.py
.venv/bin/python lab/test_cninfo_d_class_abnormal_trading_further_scale_s200_runner.py
.venv/bin/python lab/test_cninfo_d_class_abnormal_trading_further_scale_runner.py

# 4) bounded live（CNINFO=14）
.venv/bin/python lab/run_cninfo_d_class_abnormal_trading_further_scale_s1000.py \
  --live \
  --approve-d-class-abnormal-trading-further-scale-s1000 \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s1000_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_further_scale_s1000
```

## Observed

| 阶段 | CNINFO | 结果 |
|------|--------|------|
| cite/lock | 14 | 752 found + 248 empty → DAT501–1500 |
| dry-run | 0 | planned_ok 1000/1000 |
| live | 14 | acceptable 1000/1000 · excellence YES |
