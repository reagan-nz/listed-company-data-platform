# CNINFO B 类 Era D ~200 Expansion — Live Execution Summary

_生成时间：2026-07-10 08:00:27 UTC_

> **性质：** Era D scale-200 live metadata validation · **无 PDF 下载/解析** · **不是 verified**

## Counts

| 指标 | 值 |
|------|-----|
| mode | erad_scale_200_live |
| universe size | 200 |
| retained cohort | 100 |
| new cohort | 100 |
| CNINFO requests | 397 |
| found | 198 |
| discovered (lineage) | 198 |
| acceptable | 198 |
| failed | 2 |
| needs_review | 2 |
| empty_but_valid | 0 |
| PDF downloaded | **0** |
| PDF parsed | **0** |
| OCR | **0** |
| extraction | **0** |
| DB / MinIO / RAG | **0** |

## Retained cohort live behavior

- BD2E001–100：`retained_evidence_mode=live_refresh`（CNINFO metadata refresh）
- `phase3_source_case_id` 仅作谱系引用；快照/报告**仅**写 Era D 隔离根
- Phase 3 expansion / failed-retry / retry_v2 生产根：**不写入**

## Endpoint usage

- EP001: 198
- EP002: 199
- EP004: 100
- EP005: 100

## Safety

- Phase 3 expansion baseline untouched: **yes**
- Phase 3 failed retry baseline untouched: **yes**
- Phase 3 retry_v2 baseline untouched: **yes**
- EP002 precheck baseline untouched: **yes**
- A/C/D live roots untouched: **yes**
- metadata and pdf URL lineage only: **yes**
- approval_status: **APPROVED**（human phrase recorded 2026-07-10）
- approved_for_live: **true**（execution complete）
- verified: **no**
- production_ready: **no**

## Gate

```text
b_class_erad_scale_200_execution_gate = PASS_WITH_CAVEAT
```

- acceptance threshold: **≥ 180/200** → PASS_WITH_CAVEAT

**不是 PASS** · **不是 verified** · **不是 production_ready**

