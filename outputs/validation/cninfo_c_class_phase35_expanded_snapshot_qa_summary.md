# CNINFO C-Class Phase 3.5 Expanded Snapshot QA Summary

_生成时间：2026-07-10_

> 离线 expanded snapshot QA review。**无 CNINFO** · **无 harvest rerun** · **无 snapshot rebuild**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

# Snapshot QA Result

- **json_count:** **491**
- **valid_json_count:** **491**
- **invalid_json_count:** **0**
- **duplicate_company_code_count:** **0**

# Universe

- **universe_count:** **491**
- **original:** **463**
- **resume merged:** **28**

# Exclusions

- **C35R016 / 301212 present:** **False**
- **hold_for_review present:** **0**
- **holdout ledger rows:** **9** (all `excluded_holdout_confirmed`)

# QA Outcome Buckets

- **qa_ok:** **0**
- **qa_ok_with_caveat:** **491**
- **qa_review_required:** **0**
- **excluded_holdout_confirmed:** **9**

# Snapshot Status Distribution

- complete_with_caveat: **491**
- complete: **0**
- partial: **0**
- failed: **0**

# Merge-Manifest Routing

- **manifest_rows:** **4910**
- resume companies: retried sources from resume root; non-retried from original root
- original companies: all sources from original root
- resume precedence rules sample: `{'original_root_for_non_retried; resume_readonly_fallback': 79, 'resume_root_wins_for_retried_source': 117, 'derived_from_basic; use primary root basic mapped': 84}`

# Module Coverage

| module | available | partial | not_available | missing | gate |
|--------|-----------|---------|---------------|---------|------|
| company_identity | 491 | 0 | 0 | 0 | PASS |
| securities_profile | 491 | 0 | 0 | 0 | PASS |
| business_profile | 491 | 0 | 0 | 0 | PASS |
| industry_profile | 489 | 2 | 0 | 0 | PASS_WITH_CAVEAT |
| financial_snapshot | 482 | 9 | 0 | 0 | PASS_WITH_CAVEAT |
| technology_profile | 0 | 0 | 491 | 0 | PASS_WITH_CAVEAT |
| organization_profile | 489 | 0 | 2 | 0 | PASS_WITH_CAVEAT |
| shareholder_profile | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| executive_profile | 485 | 6 | 0 | 0 | PASS_WITH_CAVEAT |
| governance_profile | 491 | 0 | 0 | 0 | PASS |
| dividend_profile | 474 | 17 | 0 | 0 | PASS_WITH_CAVEAT |
| capital_action_profile | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| risk_profile | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| event_timeline | 489 | 2 | 0 | 0 | PASS_WITH_CAVEAT |
| market_behavior | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| investor_relation | 0 | 491 | 0 | 0 | PASS_WITH_CAVEAT |
| document_evidence | 491 | 0 | 0 | 0 | PASS |
| data_quality | 491 | 0 | 0 | 0 | PASS |

# Safety

- harvest_roots_unchanged: **True**
- CNINFO calls: **0**
- DB / MinIO / RAG: **0**
- not verified · not production_ready
- no commit · no push

# Gate

```
phase35_expanded_success_subset_snapshot_qa_gate = PASS_WITH_CAVEAT
```

build gate unchanged:

```
phase35_expanded_success_subset_snapshot_build_gate = PASS_WITH_CAVEAT
```

# Next Step

Recommend: **Phase 3.5 expanded snapshot closure review**.

Alternative: commit boundary review for C-class Phase 3.5 artifacts.

Optional later: isolated C35R016 executive retry review only if still desired.

Do **not** recommend verified / production_ready / DB / MinIO / RAG / full 500 rerun.
