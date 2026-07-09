# CNINFO B 类 Phase 1 Ready-case Benchmark 离线执行摘要

_生成时间：2026-07-09 03:49:08 UTC_

> **性质：** 离线 fixture 执行；**无 CNINFO**；**无 live**；**无 PDF 下载**。

## Counts

| 指标 | 值 |
|------|-----|
| Total cases | 5 |
| Passed | 5 |
| Failed | 0 |
| Schema version | phase1_freeze_v1 |
| Executed endpoints | **NONE** |

## Case Results

| case_id | actual_result | passed | notes |
|---------|---------------|--------|-------|
| RC001 | PASS | yes | required complete; pdf lineage present; quality_status=pass; lineage_status=discovered |
| RC002 | PASS | yes | general metadata shape ok; required complete; category present |
| RC003 | PASS | yes | missing pdf lineage; quality_status=needs_review; not verified |
| RC004 | PASS | yes | duplicate detected; candidates preserved; dedup required; no auto merge |
| RC005 | PASS | yes | unknown category preserved; category_status=review_later; no forced mapping |

## Gate

```text
b_class_ready_case_benchmark_execution_gate = PASS_OFFLINE
```

**不是 PASS**（production）· **不是 live approved**。

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`: **untouched**
- CNINFO calls: **0**

