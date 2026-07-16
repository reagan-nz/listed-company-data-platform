# RSU Further-Scale S50 Command Draft (executed)

```bash
.venv/bin/python lab/run_cninfo_d_class_restricted_shares_unlock_further_scale.py --build-universe-lock
.venv/bin/python lab/run_cninfo_d_class_restricted_shares_unlock_further_scale.py --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_restricted_shares_unlock_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_restricted_shares_unlock_further_scale
.venv/bin/python lab/run_cninfo_d_class_restricted_shares_unlock_further_scale.py --live \
  --approve-d-class-restricted-shares-unlock-further-scale \
  --universe-csv outputs/validation/cninfo_d_class_restricted_shares_unlock_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_restricted_shares_unlock_further_scale
```
