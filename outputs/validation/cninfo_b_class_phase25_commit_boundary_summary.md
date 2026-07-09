# CNINFO B 类 Phase 2.5 Full-Track — Commit Boundary Summary

_生成时间：2026-07-09_

> **性质：** B-class Phase 1 → Phase 2 → Phase 2.5 expansion + failed retry **git milestone** · **无 CNINFO** · **不是 verified**

---

## Gate

```text
b_class_phase25_commit_boundary_gate = READY_TO_COMMIT
```

**NOT PASS** · **NOT verified** · **NOT production_ready** · **NOT testing_stable_sample**

---

## Phase 1 Recap（prior commits）

| 项 | 值 |
|----|-----|
| closure gate | `b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT` |
| cases | **5** · resolved **5** |
| TLC002 | isolated retry recovered |
| endpoints | EP001 · EP002 · EP004 · EP005 |
| PDF / DB / MinIO / RAG | **0** |

---

## Phase 2 Recap（prior commits）

| 项 | 值 |
|----|-----|
| closure gate | `b_class_phase2_expansion_closure_gate = PASS_WITH_CAVEAT` |
| cases | **20** · acceptable **20** |
| CNINFO requests | **40** |
| endpoint hits | EP001 **20** · EP002 **20** · EP004 **12** · EP005 **8** |
| PDF / DB / MinIO / RAG | **0** |

---

## Phase 2.5 Expansion Recap（this commit)

| 项 | 值 |
|----|-----|
| universe | B25E001–B25E050（**50** 家） |
| execution gate | `b_class_phase25_expansion_execution_gate = PASS_WITH_CAVEAT` |
| closure gate | `b_class_phase25_expansion_closure_gate = PASS_WITH_CAVEAT` |
| acceptable | **45/50** |
| failed | **5**（network/proxy/orgId） |
| CNINFO requests | **93** |
| PDF download / parse | **0** |

---

## Failed-Case Retry Recap（this commit)

| 项 | 值 |
|----|-----|
| retry cases | **5** only（B25E003/008/032/039/040） |
| execution gate | `b_class_phase25_failed_retry_execution_gate = PASS_WITH_CAVEAT` |
| closure gate | `b_class_phase25_failed_retry_closure_gate = PASS_WITH_CAVEAT` |
| retry acceptable | **5/5** |
| CNINFO requests | **10** |
| successful 45 not rerun | **yes** |

---

## Final Effective 50/50 Coverage

| 指标 | 值 |
|------|-----|
| accepted_original_success | **45** |
| accepted_retry_recovered | **5** |
| **effective_coverage** | **50/50** |
| unresolved | **0** |

Artifact: [cninfo_b_class_phase25_effective_merged_result.csv](cninfo_b_class_phase25_effective_merged_result.csv)

---

## Endpoint Coverage

| Endpoint | Phase 2.5 original | Retry | Combined role |
|----------|-------------------|-------|---------------|
| EP001 | **45** | **5** | hisAnnouncement/query |
| EP002 | **48** | **5** | topSearch orgId |
| EP004 | **25** | **2** | periodic_report lineage |
| EP005 | **25** | **3** | general_announcement lineage |

---

## URL Lineage Result

| 指标 | 值 |
|------|-----|
| pdf_url_present（effective 50） | **50/50** |
| adjunct_url_present（effective 50） | **50/50** |
| quality_status pass | **50** |
| lineage_status discovered | **50** |

---

## PDF Boundary Confirmation

| 项 | 值 |
|----|-----|
| PDF download | **0** |
| PDF parse | **0** |
| OCR | **0** |
| section extraction | **0** |
| `.pdf` files committed | **0** |

metadata + URL lineage only — **边界保持**

---

## DB / MinIO / RAG Boundary Confirmation

| 项 | 值 |
|----|-----|
| DB write | **0** |
| MinIO write | **0** |
| RAG run | **0** |

---

## Caveat Wording

- Original batch **45/50** — not perfect first-pass
- **5** failures were transient network/proxy/orgId — **not schema failure**
- Isolated retry discipline（TLC002 先例）恢复 **5/5**
- Phase 2.5 still **limited expansion**（50 家）— insufficient for production readiness statistics
- Use **PASS_WITH_CAVEAT** only — never **PASS**

---

## Non-Production Claim

```text
NOT verified
NOT production_ready
NOT testing_stable_sample upgrade
```

---

## Next Recommended Options

| Option | 内容 | 推荐 |
|--------|------|------|
| A | Phase 3 100-company **planning only** | after this commit |
| B | A/B lineage integration design | 可并行 |
| C | title/date matching hardening | 可并行 |

**明确不推荐：** 立即 100-company live expansion

详见 [post-retry next-step recommendation](../../plans/cninfo_b_class_phase25_post_retry_next_step_recommendation.md)

---

## Key Artifacts in This Commit

| 类别 | 代表路径 |
|------|----------|
| planning | `plans/cninfo_b_class_phase25_expansion_plan.md` |
| universe | `outputs/validation/cninfo_b_class_phase25_expansion_universe_draft.csv` |
| runner | `lab/run_cninfo_b_class_phase25_expansion_validation.py` |
| live reports | `outputs/validation/cninfo_b_class_phase25_expansion/reports/` |
| closure | `plans/cninfo_b_class_phase25_expansion_closure_review.md` |
| retry | `outputs/validation/cninfo_b_class_phase25_failed_retry/` |
| merged result | `outputs/validation/cninfo_b_class_phase25_effective_merged_result.csv` |
| status docs | `CURRENT_STATUS.md` · `PROJECT_MAP.md` · `plans/eraC_execution_plan.md` |
