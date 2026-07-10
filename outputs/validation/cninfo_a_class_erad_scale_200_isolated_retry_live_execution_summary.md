# CNINFO A 类 Era D ~200 — Isolated Retry Live Execution Summary

_生成时间：2026-07-10_

> **isolated failed-retry live** · **CNINFO 21** · **无 PDF** · **不是 verified** · **不是 production_ready**

---

## Approval

| 项 | 值 |
|----|-----|
| approval phrase | **I approve A-class Era D scale-200 isolated retry live for the triage-recommended not_found cases.** |
| approval_status | **APPROVED**（executed） |
| approved_for_live | **true** |

---

## Execution Result

| 指标 | 值 |
|------|-----|
| mode | `erad_a_scale_200_failed_retry_live` |
| universe | **7**（triage-recommended · AD2E146 excluded） |
| acceptable | **0/7** |
| recovered | **0** |
| failed (`not_found`) | **7** |
| needs_review | **7** |
| CNINFO requests | **21**（cap ≤ **24** · planned **14**） |
| matching_logic | **v2** |
| pdf_downloaded | **0** |
| pdf_parsed | **0** |
| runtime | ~**30 s** |
| exit code | **1** |

---

## Execution Gate

```text
a_class_erad_scale_200_isolated_retry_execution_gate = FAIL_REVIEW_REQUIRED
```

Threshold: ≥6/7 acceptable → **PASS_WITH_CAVEAT**（0 < 6 → **FAIL_REVIEW_REQUIRED**）

**不是 PASS** · **不是 verified** · **不是 production_ready**

---

## Per-Case Outcomes（7）

| case_id | company_code | company_name | report_type | expected_period | retrieval_status | likely_cause | retry_strategy | records | notes |
|---------|--------------|--------------|-------------|-----------------|------------------|--------------|----------------|---------|-------|
| AD2E066 | 600930 | 华电新能 | annual_report | 2024-12-31 | not_found | network_or_empty_response | broadened_date_window_v2_requery | 0 | no v2 matching periodic report |
| AD2E088 | 001393 | 维通利 | annual_report | 2024-12-31 | not_found | network_or_empty_response | broadened_date_window_v2_requery | 0 | no v2 matching periodic report |
| AD2E119 | 603370 | 华新精科 | annual_report | 2024-12-31 | not_found | network_or_empty_response | broadened_date_window_v2_requery | 0 | no v2 matching periodic report |
| AD2E121 | 603737 | 三棵树 | annual_report | 2024-12-31 | not_found | matching_logic_miss | v2_rematch_annual_title_period_expanded_candidates | 16 | no v2 matching periodic report |
| AD2E122 | 688636 | 智明达 | annual_report | 2024-12-31 | not_found | matching_logic_miss | v2_rematch_annual_title_period_expanded_candidates | 12 | no v2 matching periodic report |
| AD2E185 | 600849 | 上海医药 | quarterly_report_q1 | 2024-03-31 | not_found | matching_logic_miss | v2_rematch_q1_title_period_expanded_candidates | 2 | no v2 matching periodic report |
| AD2E190 | 603409 | 汇通控股 | quarterly_report_q1 | 2024-03-31 | not_found | network_or_empty_response | broadened_date_window_v2_requery | 0 | no v2 matching periodic report |

**AD2E146 excluded**（688755 · annual_report · `true_not_found` · deferred · not in retry universe）

---

## Merge View vs Main 192/200

| 指标 | 值 |
|------|-----|
| main live acceptable | **192/200** |
| main execution gate | **`PASS_WITH_CAVEAT`** |
| retry recovered | **0** |
| still unresolved（7 retry cases） | **7** |
| deferred unresolved（AD2E146） | **1** |
| **effective accepted if merged** | **192/200** |
| conceptual cap（AD2E146 out） | **199/200** |
| total unresolved if merged | **8** |

Retry did **not** improve main Era D acceptance count.

---

## Output Artifacts

| 产物 | 路径 |
|------|------|
| live report | `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_live_report.csv` |
| quality report | `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_live_quality_report.csv` |
| live summary | `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_live_summary.md` |
| raw metadata | `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/raw_metadata/AD2E*.json`（**7** files） |

---

## Safety Confirmations

| 检查项 | 状态 |
|--------|------|
| Phase 3 / A3M017 production roots | **untouched** |
| main Era D root `cninfo_a_class_erad_scale_200/` | **untouched** |
| B/C/D / harvest roots | **untouched** |
| PDF / OCR / extraction | **none** |
| DB / MinIO / RAG | **none** |
| verified / production_ready | **no** |
| commit / push | **no** |
| amend bbc15c3 / cb9f3fc | **no** |

---

## Next Recommended A-Class Task

**Merge closure review（offline）** — fold retry outcomes into Era D effective ledger vs main 192/200 · then **commit boundary review**（explicit-path · separate approval）
