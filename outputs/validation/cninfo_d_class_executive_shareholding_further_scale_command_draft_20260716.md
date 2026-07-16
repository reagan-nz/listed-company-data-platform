# D-FM-06 / ESH Further-Scale S50 Command Draft

## Universe lock（cite · CNINFO=1）

```bash
.venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale.py \
  --build-universe-lock
```

## Dry-run（CNINFO=0）

```bash
.venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale.py \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_further_scale
```

## Tests

```bash
.venv/bin/python lab/test_cninfo_d_class_executive_shareholding_further_scale_runner.py
```

## Live（bounded · CNINFO=1 shared）

```bash
.venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale.py \
  --live \
  --approve-d-class-executive-shareholding-further-scale \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_further_scale
```

## Result (executed)

| stage | CNINFO | result |
|-------|--------|--------|
| universe cite | 1 | lock DES201–250 · total=2123 |
| dry-run | 0 | planned_ok 50/50 |
| live | 1 | acceptable 50/50 · excellence YES |
