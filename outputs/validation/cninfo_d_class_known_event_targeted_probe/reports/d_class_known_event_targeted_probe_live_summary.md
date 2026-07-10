# CNINFO D 类 Known Event Targeted Probe Live Summary

_生成时间：2026-07-10 01:18:43 UTC_

> **性质：** known-event targeted probe live · **无 DB/MinIO/RAG/PDF/OCR** · **不是 verified**

## Counts

| 指标 | 值 |
|------|-----|
| DLC003R-T01 CNINFO requests | **1** |
| DLC006R-T01 CNINFO requests | **12** |
| Total CNINFO requests | **13** |
| DB writes | **0** |
| MinIO writes | **0** |
| RAG runs | **0** |

## Probe Results

| targeted_probe_id | anchor | retrieval | records | requests | acceptable | failure_type |
|-------------------|--------|-----------|---------|----------|------------|--------------|
| DLC003R-T01 | 2024-02-19 | found | 1 | 1 | yes |  |
| DLC006R-T01 | 2024-07-16 | empty_but_valid | 0 | 12 | no | empty_but_valid_after_budget |

## Gate

```text
d_class_known_event_targeted_probe_execution_gate = FAIL_REVIEW_REQUIRED
approval_status = NOT_APPROVED
```

**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**

