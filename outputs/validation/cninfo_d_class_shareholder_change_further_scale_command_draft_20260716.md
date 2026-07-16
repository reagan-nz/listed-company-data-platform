# CNINFO D 类 shareholder_change Further-Scale — Command Draft

_生成时间：2026-07-16 · D-FM-09_

```bash
cd listed_company_data_collector-worktrees/d-class

.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale.py --build-universe-lock

.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale.py --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale

.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale.py --live \
  --approve-d-class-shareholder-change-further-scale \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale

.venv/bin/python lab/test_cninfo_d_class_shareholder_change_further_scale_runner.py
```

| 阶段 | CNINFO |
|------|--------|
| build-universe-lock | 2 |
| dry-run | 0 |
| live | 2 |
| tests | 0 |
