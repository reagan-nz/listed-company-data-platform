# CNINFO A 类 Era D ~200 — Merge Closure Summary

_生成时间：2026-07-10_

> **性质：** offline merge closure review · **CNINFO 0** · **无 live** · **无 further retry** · **不是 verified** · **不是 production_ready**

---

## Effective State

| 指标 | 值 |
|------|-----|
| universe total | **200** |
| main live acceptable | **192/200** |
| isolated retry acceptable | **0/7** |
| retry recovered | **0** |
| **effective accepted final** | **192/200** |
| **unresolved final** | **8** |
| effective acceptance rate | **96%** |
| CNINFO（main live，已发生） | **423** |
| CNINFO（isolated retry live，已发生） | **21** |
| closure review CNINFO | **0** |

---

## Merge Logic

| 来源 | 结果 | 并入 effective |
|------|------|----------------|
| main live `found` + `pass` | **192** | **accepted_effective** |
| isolated retry recovered | **0** | — |
| unresolved（8） | 不变 | **caveat retained** |

Retry live **did not change** effective accepted count. Main live remains authoritative for accepted cases.

---

## Cohort Split

| Cohort | Total | Effective accepted | Unresolved |
|--------|-------|-------------------|------------|
| retained_phase3（AD2E001–050 · lineage only） | **50** | **50** | **0** |
| new_erad（AD2E051–200） | **150** | **142** | **8** |

All **8 unresolved** are **new_erad** only. Retained Phase 3 cohort **50/50** holds.

---

## Unresolved Final（8）

| case_id | company_code | report_type | period | attempts | likely_cause | final_disposition |
|---------|--------------|-------------|--------|----------|--------------|-------------------|
| AD2E066 | 600930 | annual_report | 2024-12-31 | main+retry | network_or_empty_response | accept_unresolved_with_caveat |
| AD2E088 | 001393 | annual_report | 2024-12-31 | main+retry | network_or_empty_response | accept_unresolved_with_caveat |
| AD2E119 | 603370 | annual_report | 2024-12-31 | main+retry | network_or_empty_response | accept_unresolved_with_caveat |
| AD2E121 | 603737 | annual_report | 2024-12-31 | main+retry | matching_logic_miss | matching_logic_followup_later |
| AD2E122 | 688636 | annual_report | 2024-12-31 | main+retry | matching_logic_miss | matching_logic_followup_later |
| AD2E185 | 600849 | quarterly_report_q1 | 2024-03-31 | main+retry | matching_logic_miss | matching_logic_followup_later |
| AD2E190 | 603409 | quarterly_report_q1 | 2024-03-31 | main+retry | network_or_empty_response | accept_unresolved_with_caveat |
| AD2E146 | 688755 | annual_report | 2024-12-31 | main | true_not_found | defer_filing_delay |

详见 [unresolved final ledger](cninfo_a_class_erad_scale_200_unresolved_final_ledger.csv)。

---

## Closure Decision

**Close Era D ~200 track with caveat NOW** at **192/200 effective accepted**.

- **Do NOT** schedule another live retry in this package
- **Do NOT** claim verified or production_ready
- Optional later（separate scope）：offline matching-logic investigation for AD2E121 / AD2E122 / AD2E185 using retry `raw_metadata`

见 [merge closure decision](cninfo_a_class_erad_scale_200_merge_closure_decision.md)。

---

## Artifacts

| 产物 | 路径 |
|------|------|
| effective accepted ledger | [cninfo_a_class_erad_scale_200_effective_accepted_ledger.csv](cninfo_a_class_erad_scale_200_effective_accepted_ledger.csv)（**192** rows · `accepted_effective`） |
| unresolved final ledger | [cninfo_a_class_erad_scale_200_unresolved_final_ledger.csv](cninfo_a_class_erad_scale_200_unresolved_final_ledger.csv)（**8** rows） |
| main live report（authoritative accepted source） | [a_class_erad_scale_200_live_report.csv](cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_report.csv) |
| main execution summary | [cninfo_a_class_erad_scale_200_execution_summary.md](cninfo_a_class_erad_scale_200_execution_summary.md) |
| retry live execution summary | [cninfo_a_class_erad_scale_200_isolated_retry_live_execution_summary.md](cninfo_a_class_erad_scale_200_isolated_retry_live_execution_summary.md) |
| failed-case triage ledger | [cninfo_a_class_erad_scale_200_failed_case_triage_ledger.csv](cninfo_a_class_erad_scale_200_failed_case_triage_ledger.csv) |

---

## Isolation & Red Lines

| 检查项 | 状态 |
|--------|------|
| Phase 3 / A3M017 production roots | **untouched** |
| B/C/D / harvest roots | **untouched** |
| PDF / OCR / extraction / DB / MinIO / RAG | **0** |
| verified / production_ready | **no** |
| commit / push | **no** |
| amend bbc15c3 / cb9f3fc | **no** |

---

## Gates

```text
a_class_erad_scale_200_merge_closure_gate = PASS_WITH_CAVEAT
a_class_erad_scale_200_execution_gate = PASS_WITH_CAVEAT          (historical · preserved)
a_class_erad_scale_200_isolated_retry_execution_gate = FAIL_REVIEW_REQUIRED  (historical · preserved)
```

**NOT bare PASS** · **NOT verified** · **NOT production_ready**

---

## Next Recommended A-Class Task

**Commit boundary review**（explicit-path · offline）for Era D ~200 + retry artifacts — exclude bulk `raw_metadata/` unless separately scoped.
