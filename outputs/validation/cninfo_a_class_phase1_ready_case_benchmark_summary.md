# CNINFO A 类 Phase 1 Ready-case Benchmark 摘要

_生成时间：2026-07-09 06:27:13 UTC_

> **性质：** 离线 fixture benchmark；**无 CNINFO**；**无 live**；**无 PDF 下载**。

## Counts

| 指标 | 值 |
|------|-----|
| Total cases | 5 |
| Passed | 5 |
| Failed | 0 |
| Schema version | a_class_phase1_freeze_v1 |
| CNINFO calls | **0** |

## Case Results

| case_id | object_type | expected_status | actual_status | quality_status | lineage_status | passed |
|---------|-------------|-----------------|---------------|----------------|----------------|--------|
| AC001 | report_document | valid_pass | valid_pass | pass | discovered | yes |
| AC002 | document_lineage | lineage_valid | lineage_valid | pass | linked | yes |
| AC003 | report_document | quality_downgrade | quality_downgrade | needs_review | needs_review | yes |
| AC004 | report_document | dedup_review | dedup_review | caveat | needs_review | yes |
| AC005 | report_document | enum_invalid | enum_invalid | needs_review | needs_review | yes |

## Gate

```text
a_class_ready_case_benchmark_gate = READY_FOR_REVIEW
```

**不是 PASS** · **不是 live_ready** · **不是 verified**.

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**（不变）
- B-class outputs: **unchanged**
- CNINFO calls: **0**

