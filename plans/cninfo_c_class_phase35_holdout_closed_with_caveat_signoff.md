# CNINFO C-Class Phase 3.5 Holdout Closed-with-Caveat Signoff

_生成时间：2026-07-10_

> **性质：** offline signoff documentation only · **Option 1 accepted** · **无 CNINFO** · **无 live** · **无 commit** · **无 push**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## 1. Human Decision Recorded

| 决策项 | 记录 |
|--------|------|
| Triage Option | **Option 1 accepted** |
| Holdout disposition | **All 9 → closed-with-caveat** |
| 491 expanded track | **Remains closed-with-caveat**（commit `8662eaa` · 491 local JSON unchanged） |
| C35R016 executive retry | **Not opened now** · optional later with separate planning + approval |
| Live / CNINFO | **Not opened** |

**Signoff authority:** in-session human approval to formalize Option 1 from [holdout triage next-step recommendation](../outputs/validation/cninfo_c_class_phase35_holdout_triage_next_step_recommendation.md).

---

## 2. Explicit Records

### 2.1 Eight hold_for_review → closed_with_caveat

| company_code | company_name | final_disposition |
|--------------|--------------|-------------------|
| 000003 | PT金田A | closed_with_caveat |
| 000578 | 盐湖集团 | closed_with_caveat |
| 000666 | 经纬纺机 | closed_with_caveat |
| 000689 | ST宏业 | closed_with_caveat |
| 000861 | 海印股份 | closed_with_caveat |
| 000961 | ST中南 | closed_with_caveat |
| 002280 | ST联络 | closed_with_caveat |
| 600220 | ST阳光 | closed_with_caveat |

- **No silent promotion** into 491 success subset
- **No live** opened for identity review in this signoff
- Future identity review only if **separately requested**（review-only package · no auto-promotion）

### 2.2 C35R016 / 301212 → closed_with_caveat_still_partial

| 字段 | 值 |
|------|-----|
| resume_case_id | `C35R016` |
| company_code | `301212` |
| company_name | 联盛化学 |
| final_disposition | **`closed_with_caveat_still_partial`** |
| remaining issue | `cninfo_executive_profile` http_error（post-resume） |
| promoted to 491 | **no** |
| snapshot_json_present | **false** |

- **No silent promotion**
- **No live** opened now
- Future **isolated executive-only retry** requires **separate planning + approval**（not implementation in this task）

---

## 3. 491 Success-Subset Unchanged

| 指标 | 值 |
|------|-----|
| expanded snapshot commit | `8662eaa` |
| committed tooling/docs | **40 files** |
| snapshot JSON on disk | **491 / 491**（local only） |
| snapshot JSON in git | **no** |
| holdout in 491 root | **0** |
| rebuild | **0** |
| promotion this signoff | **0** |

---

## 4. Safety / Red Lines（本任务）

| 项 | 状态 |
|----|------|
| CNINFO | **0** |
| live harvest | **0** |
| snapshot rebuild | **0** |
| harvest root mutation | **0** |
| DB / MinIO / RAG / PDF | **0** |
| verified / production_ready / testing_stable_sample | **not set** |
| commit / push | **no** |

---

## 5. Gates

```
phase35_holdout_closed_with_caveat_signoff_gate = PASS_WITH_CAVEAT
```

```
phase35_holdout_c35r016_triage_planning_gate = READY_FOR_HUMAN_DECISION
  → Option 1 accepted per this signoff (§7dqn)
```

**Preserved:**

```
phase35_expanded_success_subset_snapshot_commit_review_gate = READY_FOR_HUMAN_DECISION
phase35_expanded_success_subset_snapshot_commit_boundary_review_gate = READY_FOR_COMMIT_REVIEW
phase35_expanded_success_subset_snapshot_closure_gate = PASS_WITH_CAVEAT
phase35_expanded_success_subset_snapshot_qa_gate = PASS_WITH_CAVEAT
phase35_expanded_success_subset_snapshot_build_gate = PASS_WITH_CAVEAT
```

**不是 bare PASS** · **不是 verified** · **不是 production_ready**

---

## 6. Artifacts

| 路径 | 说明 |
|------|------|
| [closed-with-caveat ledger](../outputs/validation/cninfo_c_class_phase35_holdout_closed_with_caveat_ledger.csv) | 9-row final disposition |
| [signoff summary](../outputs/validation/cninfo_c_class_phase35_holdout_closed_with_caveat_summary.md) | execution summary |
| [triage plan](cninfo_c_class_phase35_holdout_c35r016_triage_plan.md) | prior triage package（read-only input） |

---

## 7. Next-Step Recommendation

**Primary:** **Stop C-class Phase 3.5 holdout work** — leave all 9 as closed-with-caveat; 491 track remains closed.

**Optional later（not started here）:**

1. C35R016 isolated executive retry **planning only** — if newly requested
2. Push decision for committed C-class docs（`8662eaa`）— if separately requested

详见 [signoff summary](../outputs/validation/cninfo_c_class_phase35_holdout_closed_with_caveat_summary.md)。
