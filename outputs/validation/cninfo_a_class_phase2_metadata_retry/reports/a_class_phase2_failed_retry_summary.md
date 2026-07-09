# CNINFO A 类 Phase 2 Failed Retry — Live 执行摘要

_生成时间：2026-07-09 08:04:19 UTC_

> **性质：** isolated retry live · **8 failed cases only** · **无 PDF** · **不是 verified**

## Counts

| 指标 | 值 |
|------|-----|
| mode | retry_live |
| retry cases | 8 |
| retry correct | 0 |
| success (found) | 0 |
| failure | 8 |
| wrong report-type | 0 |
| title mismatch | 0 |
| period mismatch | 0 |
| CNINFO requests | 0 |
| PDF downloaded | **0** |
| PDF parsed | **0** |
| OCR / extraction | **0** |
| matching_logic | **v2** |

## Safety

- successful 12 cases not rerun: **yes**
- Phase 2 expansion reports untouched: **yes**
- Phase 1 baseline untouched: **yes**
- verified: **no**
- production_ready: **no**

## Gate

```text
a_class_phase2_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED
a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED (unchanged)
```

**不是 PASS** · **不是 verified** · **不是 production_ready**
