# CNINFO A 类 Era D ~200 Failed Retry — Live 执行摘要

_生成时间：2026-07-10 16:50 UTC+8_

> **性质：** Era D isolated failed-retry live · **7 cases** · **无 PDF** · **不是 verified**

## Approval

| 项 | 值 |
|----|-----|
| approval phrase | **I approve A-class Era D scale-200 isolated retry live for the triage-recommended not_found cases.** |
| approval_status | **APPROVED**（executed） |
| approved_for_live | **true** |

## Counts

| 指标 | 值 |
|------|-----|
| mode | `erad_a_scale_200_failed_retry_live` |
| universe size | **7** |
| acceptable | **0/7** |
| failed | **7** |
| needs_review | **7** |
| recovered | **0** |
| deferred excluded | **AD2E146** |
| CNINFO requests | **21**（cap ≤ **24**） |
| matching_logic | **v2** |
| pdf_downloaded | **0** |
| pdf_parsed | **0** |
| exit code | **1** |

## Execution Gate

```text
a_class_erad_scale_200_isolated_retry_execution_gate = FAIL_REVIEW_REQUIRED
```

Threshold: ≥6/7 acceptable → **PASS_WITH_CAVEAT**（0 < 6）

**不是 PASS** · **不是 verified** · **不是 production_ready**

## Per-Case Outcomes

| case_id | company_code | report_type | expected_period | retrieval_status | likely_cause | CNINFO | records |
|---------|--------------|-------------|-----------------|------------------|--------------|--------|---------|
| AD2E066 | 600930 | annual_report | 2024-12-31 | not_found | network_or_empty_response | 3 | 0 |
| AD2E088 | 001393 | annual_report | 2024-12-31 | not_found | network_or_empty_response | 3 | 0 |
| AD2E119 | 603370 | annual_report | 2024-12-31 | not_found | network_or_empty_response | 3 | 0 |
| AD2E121 | 603737 | annual_report | 2024-12-31 | not_found | matching_logic_miss | 3 | 16 |
| AD2E122 | 688636 | annual_report | 2024-12-31 | not_found | matching_logic_miss | 3 | 12 |
| AD2E185 | 600849 | quarterly_report_q1 | 2024-03-31 | not_found | matching_logic_miss | 3 | 2 |
| AD2E190 | 603409 | quarterly_report_q1 | 2024-03-31 | not_found | network_or_empty_response | 3 | 0 |

## Merge View vs Main 192/200

| 指标 | 值 |
|------|-----|
| main acceptable | **192/200** |
| retry recovered | **0** |
| still unresolved（retry cohort） | **7** |
| deferred（AD2E146） | **1** |
| effective accepted if merged | **192/200**（conceptual cap **199/200** with AD2E146 excluded） |
| total unresolved if merged | **8** |

## Isolation

Writes **only** under failed-retry root; **does not mutate** main Era D live root, Phase 3, or A3M017.

## Safety

- metadata only: **yes**
- output isolation: `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/`
- Phase 3 / A3M017: **untouched**
- verified: **no**
- production_ready: **no**
- commit / push: **no**
