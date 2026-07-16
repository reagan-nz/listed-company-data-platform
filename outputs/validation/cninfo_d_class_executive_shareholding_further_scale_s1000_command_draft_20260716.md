# ESH Further-Scale S1000 Command Draft（D-FM-08）

Worktree: `listed_company_data_collector-worktrees/d-class`

```bash
cd listed_company_data_collector-worktrees/d-class

.venv/bin/python lab/test_cninfo_d_class_executive_shareholding_further_scale_s1000_runner.py

.venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale_s1000.py --build-universe-lock

.venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale_s1000.py --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s1000_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s1000

.venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale_s1000.py --live \
  --approve-d-class-executive-shareholding-further-scale-s1000 \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s1000_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s1000
```

CNINFO budget: cite=1 · dry-run=0 · live=1 · package_total=2
