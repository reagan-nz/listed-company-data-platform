# CNINFO D 类 shareholder_change Further-Scale S200 — Command Draft

_生成时间：2026-07-16 · D-FM-10_

```bash
cd listed_company_data_collector-worktrees/d-class

.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s200.py --build-universe-lock

.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s200.py --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200

.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s200.py --live \
  --approve-d-class-shareholder-change-further-scale-s200 \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200

.venv/bin/python lab/test_cninfo_d_class_shareholder_change_further_scale_s200_runner.py
```

| 阶段 | CNINFO |
|------|--------|
| build-universe-lock | 9 |
| dry-run | 0 |
| live | 9 |
| tests | 0 |
| package formal total | 18 |
