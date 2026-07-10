# CNINFO B 类 Phase 3 100 Retry v2 — Live Execution Summary

_生成时间：2026-07-10 05:46:17 UTC_

> **性质：** Phase 3 retry_v2 live · **无 PDF 下载/解析** · **不是 verified**

## Counts

| 指标 | 值 |
|------|-----|
| mode | phase3_retry_v2_live |
| retry_v2 universe size | 91 |
| CNINFO requests | 182 |
| found | 91 |
| discovered (lineage) | 91 |
| acceptable | 91 |
| failed | 0 |
| needs_review | 0 |
| empty_but_valid | 0 |
| PDF downloaded | **0** |
| PDF parsed | **0** |
| OCR | **0** |
| extraction | **0** |
| DB / MinIO / RAG | **0** |

## Endpoint usage

- EP001: 91
- EP002: 91
- EP004: 42
- EP005: 49

## Safety

- successful hold case B3E087 not rerun: **yes**
- 8 recovered cases not rerun: **yes**
- Phase 3 expansion baseline untouched: **yes**
- Phase 3 failed retry baseline untouched: **yes**
- EP002 precheck baseline untouched: **yes**
- Phase 2.5 expansion baseline untouched: **yes**
- Phase 2.5 failed retry baseline untouched: **yes**
- metadata and pdf URL lineage only: **yes**
- approval_status: **NOT_APPROVED** (until explicit human approval)
- verified: **no**
- production_ready: **no**

## Gate

```text
b_class_phase3_100_retry_v2_execution_gate = PASS_WITH_CAVEAT
```

- acceptance threshold: **≥ 82/91** → PASS_WITH_CAVEAT

**不是 PASS** · **不是 verified** · **不是 production_ready**

