# CNINFO A 类 Phase 2 Network Recovery Retry v2 — Live 执行摘要

_生成时间：2026-07-09 09:38:06 UTC_

> **性质：** retry v2 live · **8 unresolved cases only** · **无 PDF** · **不是 verified**

## Counts

| 指标 | 值 |
|------|-----|
| mode | retry_v2_live |
| retry_v2 cases | 8 |
| retry_v2 acceptable | 0 |
| retry_v2 failed | 8 |
| needs_review | 8 |
| wrong report-type | 0 |
| title mismatch | 0 |
| period mismatch | 0 |
| CNINFO requests | 0 |
| PDF downloaded | **0** |
| PDF parsed | **0** |
| OCR / extraction | **0** |
| DB / MinIO / RAG | **0** |
| matching_logic | **v2** |

## Safety

- successful 12 cases not rerun: **yes**
- Phase 2 expansion reports untouched: **yes**
- retry v1 reports untouched: **yes**
- verified: **no**
- production_ready: **no**

## Gate

```text
a_class_phase2_network_recovery_retry_v2_execution_gate = FAIL_REVIEW_REQUIRED
a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED (unchanged)
a_class_phase2_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED (unchanged)
a_class_phase2_metadata_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED (unchanged)
```

**不是 PASS** · **不是 verified** · **不是 production_ready**
