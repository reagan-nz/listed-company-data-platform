# CNINFO C-Class Phase 3.5 Holdout + C35R016 Triage Plan

_生成时间：2026-07-10_

> **性质：** offline triage planning only · **无 CNINFO** · **无 live** · **无 commit** · **无 push**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## 1. Context

Phase 3.5 expanded snapshot track is **committed**（`8662eaa` · **40 files**）and **closed-with-caveat**:

- snapshot JSON on disk: **491 / 491**（local · not in git）
- holdout remaining: **9** = **8** `hold_for_review` + **1** `still_partial`（C35R016 / 301212）
- all 9 confirmed absent from expanded snapshot root

This plan triages the 9 holdouts **without** promoting any into the 491 success subset.

---

## 2. Holdout Inventory

| # | company_code | company_name | category | QA class |
|---|--------------|--------------|----------|----------|
| 1 | 000003 | PT金田A | hold_for_review | hold_for_review |
| 2 | 000578 | 盐湖集团 | hold_for_review | hold_for_review |
| 3 | 000666 | 经纬纺机 | hold_for_review | hold_for_review |
| 4 | 000689 | ST宏业 | hold_for_review | hold_for_review |
| 5 | 000861 | 海印股份 | hold_for_review | hold_for_review |
| 6 | 000961 | ST中南 | hold_for_review | hold_for_review |
| 7 | 002280 | ST联络 | hold_for_review | hold_for_review |
| 8 | 600220 | ST阳光 | hold_for_review | hold_for_review |
| 9 | 301212 | 联盛化学 | C35R016 still_partial | still_partial |

Full matrix: [cninfo_c_class_phase35_holdout_triage_matrix.csv](../outputs/validation/cninfo_c_class_phase35_holdout_triage_matrix.csv)

---

## 3. Triage Categories

### 3.1 Eight hold_for_review（identity-blocked）

**Source:** [hold_for_review decision note](cninfo_c_class_phase35_hold_for_review_decision_note.md)

Common pattern:

- harvest_status: `partial`
- failed sources: `basic;dividend;executive;share_capital;top_holders;top_float_holders`
- sources_http_success: **1** / 7
- recommended_action: `identity_review_needed`
- **not** in isolated resume universe（by design）

**Treatment:**

```
hold_as_caveat
identity_review_needed
do_not_resume_automatically
do_not_snapshot_yet
promotion_allowed_now = no
```

These cases are **not** network-resume candidates. Automatic live retry risks masking PT/ST/delist identity issues.

### 3.2 C35R016 / 301212（technical residual）

**Source:** [C35R016 case brief](../outputs/validation/cninfo_c_class_phase35_c35r016_case_brief.md)

- post-resume status: `still_partial`
- remaining failure: `cninfo_executive_profile` http_error（count=1）
- human_review_required: yes
- promotion_allowed_now: **no**

Distinct from hold_for_review: identity is not the primary blocker; **one executive source** failed after otherwise successful resume.

---

## 4. Relationship to 491 Committed Track

| 规则 | 状态 |
|------|------|
| 491 snapshot track | **closed-with-caveat** · commit `8662eaa` |
| holdout promotion | **forbidden** in this planning task |
| 491 rebuild | **forbidden** |
| harvest root mutation | **forbidden**（`phase35_batch_500_001` · `_resume` read-only） |
| snapshot JSON commit | **forbidden** |

Holdout triage **does not reopen** expanded snapshot closure. Any future inclusion requires a **new approved track** with explicit human signoff.

---

## 5. Decision Options（for human）

| Option | 描述 | live | CNINFO |
|--------|------|------|--------|
| **A** | Hold all 9 closed-with-caveat; 491 track stays closed | no | no |
| **B** | Prepare isolated C35R016 executive retry **planning package only** | no | no |
| **C** | Prepare broader 8 hold_for_review **review-only identity package** | no | no |

**Primary recommendation:** **Option A**（see [next-step recommendation](../outputs/validation/cninfo_c_class_phase35_holdout_triage_next_step_recommendation.md)）

---

## 6. Safety / Red Lines

- CNINFO calls（this task）: **0**
- live harvest: **0**
- snapshot rebuild: **0**
- promotion: **0**
- DB / MinIO / RAG / PDF: **0**
- verified / production_ready / testing_stable_sample: **not set**
- commit / push: **no**

---

## 7. Gate

```
phase35_holdout_c35r016_triage_planning_gate = READY_FOR_HUMAN_DECISION
```

**Preserved gates:**

```
phase35_expanded_success_subset_snapshot_commit_review_gate = READY_FOR_HUMAN_DECISION
phase35_expanded_success_subset_snapshot_commit_boundary_review_gate = READY_FOR_COMMIT_REVIEW
phase35_expanded_success_subset_snapshot_closure_gate = PASS_WITH_CAVEAT
phase35_expanded_success_subset_snapshot_qa_gate = PASS_WITH_CAVEAT
phase35_expanded_success_subset_snapshot_build_gate = PASS_WITH_CAVEAT
```

---

## 8. Artifacts

| 路径 | 说明 |
|------|------|
| [holdout triage matrix](../outputs/validation/cninfo_c_class_phase35_holdout_triage_matrix.csv) | 9-row triage matrix |
| [C35R016 case brief](../outputs/validation/cninfo_c_class_phase35_c35r016_case_brief.md) | 301212 special brief |
| [planning summary](../outputs/validation/cninfo_c_class_phase35_holdout_triage_planning_summary.md) | execution summary |
| [next-step recommendation](../outputs/validation/cninfo_c_class_phase35_holdout_triage_next_step_recommendation.md) | primary option |
