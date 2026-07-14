# CNINFO A 类 Era D Next-Scale Slice1 — Live Execution Summary

_生成时间：2026-07-13 01:48:38 UTC_

> **isolated live metadata validation** · **CNINFO 637** · **无 PDF** · **不是 verified** · **不是 production_ready**

## Approval

| 项 | 值 |
|----|-----|
| approval phrase | **I approve A-class Era D next-scale slice1 live metadata validation.** |
| approval_status | **APPROVED**（this session） |
| approved_for_live | **true**（executed） |

## Combined Execution Result（300 cases · 2 sessions）

| 指标 | Session 1 | Session 2 | Combined |
|------|-----------|-----------|----------|
| case range | AD2E201–350 | AD2E351–500 | AD2E201–500 |
| executed | 150 | 150 | **300** |
| acceptable | 145/150 | 149/150 | **294/300** |
| CNINFO requests | 312 | 325 | **637**（cap ≤ **720**） |
| found | — | — | **294** |
| failed / unresolved | 5 | 1 | **6** |
| needs_review | — | — | **6** |
| pdf_downloaded | 0 | 0 | **0** |
| pdf_parsed | 0 | 0 | **0** |
| matching_logic | v2 | v2 | **v2** |

## Execution Gate

```text
a_class_erad_next_scale_slice1_execution_gate = PASS_WITH_CAVEAT
```

Threshold: ≥270/300 acceptable → **PASS_WITH_CAVEAT**（294 ≥ 270）

**不是 PASS** · **不是 verified** · **不是 production_ready**

## Unresolved / Network Cases（6）

| case_id | company_code | session | retrieval_status | failure_class |
|---------|--------------|---------|------------------|---------------|
| AD2E216 | 601206 | session1 | not_found | not_found_or_matching_miss |
| AD2E270 | 603262 | session1 | not_found | not_found_or_matching_miss |
| AD2E284 | 603400 | session1 | not_found | not_found_or_matching_miss |
| AD2E308 | 603698 | session1 | not_found | not_found_or_matching_miss |
| AD2E323 | 000559 | session1 | network_error | network_or_empty_response |
| AD2E373 | 002710 | session2 | not_found | not_found_or_matching_miss |

Ledger: `outputs/validation/cninfo_a_class_erad_next_scale_slice1/reports/a_class_erad_next_scale_slice1_unresolved_ledger.csv`

## Output Artifacts

| 产物 | 路径 |
|------|------|
| combined live report | `cninfo_a_class_erad_next_scale_slice1/reports/a_class_erad_next_scale_slice1_live_report.csv` |
| combined quality report | `cninfo_a_class_erad_next_scale_slice1/reports/a_class_erad_next_scale_slice1_live_quality_report.csv` |
| session1 reports | `.../reports/session1/` |
| session2 reports | `.../reports/session2/` |
| raw metadata | `cninfo_a_class_erad_next_scale_slice1/raw_metadata/AD2E*.json`（**300** files） |

## Safety Confirmations

| 检查项 | 状态 |
|--------|------|
| scale-200 / failed_retry production roots | **untouched** |
| Phase 3 / A3M017 production roots | **untouched** |
| AD2E001–200 rerun | **no** |
| 8 scale-200 unresolved rerun | **no** |
| commit / push | **no** |
