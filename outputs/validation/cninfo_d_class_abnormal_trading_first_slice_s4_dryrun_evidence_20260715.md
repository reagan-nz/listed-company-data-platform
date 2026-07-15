# CNINFO D 类 abnormal_trading — S4 Dry-run Evidence

_生成时间：2026-07-15 09:06:30 UTC_

> **task：** D-FM-03 · **CNINFO = 0** · **live = not run** · **NOT verified**

## Command

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --abnormal-trading-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_first_slice
```

## Result

```text
mode=abnormal_trading_first_slice_dry_run cases=5 planned_request_count_total=5 cninfo_calls=0
gate=d_class_abnormal_trading_first_slice_runner_extension_gate=READY_FOR_APPROVAL
```

| 指标 | 值 |
|------|-----|
| cases | 5 |
| planned_ok | 5/5 |
| planned_request_count_total | 5 |
| CNINFO | 0 |
| PDF/OCR/DB/MinIO/RAG | no |

## Gate

```text
d_class_abnormal_trading_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_first_slice_live_gate = NOT_APPROVED
```
