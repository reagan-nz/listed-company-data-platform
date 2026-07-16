# D-FM-07 / ESH Further-Scale S200 Command Draft

_生成时间：2026-07-16 · 复跑参考 · 本轮已执行_

## Worktree

```bash
cd listed_company_data_collector-worktrees/d-class
```

## Universe cite（CNINFO=1）

```bash
.venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale_s200.py \
  --build-universe-lock
```

## Dry-run（CNINFO=0）

```bash
.venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale_s200.py \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200
```

## Bounded live（CNINFO=1）

```bash
.venv/bin/python lab/run_cninfo_d_class_executive_shareholding_further_scale_s200.py \
  --live \
  --approve-d-class-executive-shareholding-further-scale-s200 \
  --universe-csv outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_executive_shareholding_further_scale_s200
```

## Tests

```bash
.venv/bin/python lab/test_cninfo_d_class_executive_shareholding_further_scale_s200_runner.py
```

## Safety

- 输出根必须为 `cninfo_d_class_executive_shareholding_further_scale_s200`
- 禁止写入 S50 / next-slice / first-slice / AT / SC / EP / RSU / FIA 冻结根
- 无 PDF / OCR / DB / MinIO / RAG
