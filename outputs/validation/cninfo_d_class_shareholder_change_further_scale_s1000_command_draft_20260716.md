# CNINFO D 类 shareholder_change Further-Scale S1000 — Command Draft

_生成时间：2026-07-16 · D-FM-11_

```bash
cd listed_company_data_collector-worktrees/d-class

# 1) universe lock（CNINFO cite；自适应 found + empty pad）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s1000.py --build-universe-lock

# 2) dry-run（CNINFO=0）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s1000.py --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000

# 3) bounded live（CNINFO=shared compose days）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s1000.py --live \
  --approve-d-class-shareholder-change-further-scale-s1000 \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000

# 4) offline tests
.venv/bin/python lab/test_cninfo_d_class_shareholder_change_further_scale_s1000_runner.py
```

约束：

- 输出根必须是 `cninfo_d_class_shareholder_change_further_scale_s1000`
- 禁止写入 SC s50 / s200 / next-slice / first-slice / ESH / AT 冻结根
- 禁止 ESH inflate · 禁止 A/B/C · 禁止 commit/push（executor）
