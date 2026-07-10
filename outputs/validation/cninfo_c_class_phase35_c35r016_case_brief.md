# CNINFO C-Class Phase 3.5 C35R016 Case Brief — 301212 联盛化学

_生成时间：2026-07-10_

> **性质：** offline holdout triage case brief · **无 CNINFO** · **无 live** · **无 promotion**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## Case Identity

| 字段 | 值 |
|------|-----|
| resume_case_id | `C35R016` |
| company_code | `301212` |
| company_name | 联盛化学 |
| market | SZSE |
| holdout_category | `retry_before_snapshot` → **`still_partial`** |

---

## Current Status: still_partial

After Phase 3.5 isolated resume live（CNINFO **120** · complete **28** · partial **1**）:

- **resume_harvest_status:** `partial`
- **resume_qa_classification:** `still_partial`
- **promote_to_success_subset:** `no`
- **human_review_required:** `yes`
- **snapshot_include:** `no`
- **snapshot_json_present:** `false`

C35R016 is the **only** company that did not reach `recovered_complete` among the 29-case isolated resume universe.

---

## Failed Source History

### Prior Phase 3.5 original harvest（partial）

From [partial company QA ledger](cninfo_c_class_phase35_partial_company_qa_ledger.csv):

- harvest_status: `partial`
- failed sources: `basic;dividend;executive`
- sources_http_success: **4** / 7
- triage: `retry_before_snapshot` · `isolated_resume_candidate`

### After isolated resume

From [isolated resume case triage](cninfo_c_class_phase35_isolated_resume_case_triage.csv):

| 指标 | 值 |
|------|-----|
| http_error_count | **1** |
| empty_but_valid_count | **0** |
| failed_sources_after_resume | **`cninfo_executive_profile`** |

Interpretation: resume **recovered** prior basic/dividend gaps; **one executive-profile http_error** remains. This is a **narrow, source-specific** residual — not an all-source identity failure like the 8 `hold_for_review` cases.

HTTP error class context: 301212 appeared in [http error analysis](cninfo_c_class_phase35_http_error_analysis.csv) under `ssl_error` cluster（SSL EOF / 连接中断）— consistent with transient network, not schema break.

---

## Why Not Silently Promoted

1. **Explicit policy:** merge planning and expanded snapshot planning both require `do_not_silent_promote` for C35R016.
2. **Classification:** `still_partial` ≠ `recovered_complete`; promotion would violate resume QA gate semantics.
3. **Human review flag:** `human_review_required=yes` on case triage row.
4. **Closure / commit boundary:** C35R016 excluded from 491 expanded snapshot root; QA holdout confirmation `excluded_holdout_confirmed`.
5. **Committed 491 track:** commit `8662eaa` closed the 491-case track; silent promotion would reopen closure without approval.

---

## Is Future Isolated Executive-Only Retry Justified?

**Conditional yes — planning only, not execution.**

| 支持 | 反对 |
|------|------|
| Single-source gap (`cninfo_executive_profile` only) | 491 track already closed-with-caveat and committed |
| Other 6 sources recovered after resume | Retry success still does **not** auto-qualify for 491 promotion |
| http_error pattern matches ssl/transient cluster | Requires separate approval + runner design |
| Narrow scope vs full company rerun | May remain partial if executive endpoint persistently empty |

**Verdict for planning:** justified **only** as an **optional, separately approved** micro-track — not as reopening the 491 success subset.

---

## Request Cap Proposal（Future Isolated Executive Retry）

If human later approves executive-only retry planning:

| 约束 | 提案值 |
|------|--------|
| companies | **1**（301212 only） |
| sources | **`cninfo_executive_profile` only** |
| max CNINFO requests | **≤ 3**（1 primary + up to 2 bounded retries） |
| output root | **new isolated root**（e.g. `phase35_c35r016_executive_retry`）— **不得** mutate `phase35_batch_500_001` or `_resume` |
| full company rerun | **forbidden** |
| 491 snapshot rebuild | **forbidden** without separate expanded-track approval |
| success-subset promotion | **forbidden** in retry task itself; requires post-retry QA + human decision |
| DB / MinIO / RAG / PDF | **forbidden** |

---

## Explicit Non-Goals（本 planning 任务）

- **No** full company rerun
- **No** 491 expanded snapshot rebuild
- **No** success-subset promotion（491 remains **491**）
- **No** silent inclusion of 301212 into committed track
- **No** live / CNINFO in this planning task

---

## Cross-References

- [holdout ledger](cninfo_c_class_phase35_expanded_snapshot_holdout_ledger.csv)
- [QA holdout confirmation](cninfo_c_class_phase35_expanded_snapshot_qa_holdout_confirmation.csv)
- [resume merge planning](cninfo_c_class_phase35_resume_merge_planning.md)
- [expanded closure summary](cninfo_c_class_phase35_expanded_snapshot_closure_summary.md)
