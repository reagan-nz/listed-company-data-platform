# CNINFO A 类 Phase 2 Metadata Expansion — Live 执行摘要

_生成时间：2026-07-09 07:52:09 UTC_

> **性质：** Phase 2 live metadata validation · **无 PDF 下载/解析** · **不是 verified**

## Counts

| 指标 | 值 |
|------|-----|
| mode | live |
| universe size | 20 |
| correct report-type metadata | 12 |
| success (found) | 12 |
| failure | 8 |
| wrong report-type match | 0 |
| title mismatch | 2 |
| period mismatch | 0 |
| CNINFO requests | 28 |
| PDF downloaded | **0** |
| PDF parsed | **0** |
| OCR | **0** |
| extraction | **0** |
| matching_logic | **v2** |

## Endpoint usage

- topSearch/query: 14
- hisAnnouncement/query: 14

## Safety

- metadata only: **yes**
- output isolation: `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_a_class_phase2_metadata_expansion`
- Phase 1 baseline untouched: **yes**
- verified: **no**
- production_ready: **no**

## Gate

```text
a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED
```

**不是 PASS** · **不是 verified** · **不是 production_ready** · Phase 2 limited expansion only
