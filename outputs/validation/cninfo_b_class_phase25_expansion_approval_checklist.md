# CNINFO B 类 Phase 2.5 Expansion — 批准检查清单

_生成时间：2026-07-09_

> **性质：** 未来 Phase 2.5 live expansion 执行前的批准包；**本轮不执行 live** · **NOT APPROVED**

**前置：** [cninfo_b_class_phase25_expansion_plan.md](../../plans/cninfo_b_class_phase25_expansion_plan.md) · Phase 2 closure gate **`PASS_WITH_CAVEAT`**

---

## Phase 2 Closure Reviewed

- [ ] [Phase 2 closure review](../../plans/cninfo_b_class_phase2_expansion_closure_review.md) 已读
- [ ] [closure metrics](cninfo_b_class_phase2_expansion_closure_metrics.csv) 已读（**20/20 acceptable**）
- [ ] [closure summary](cninfo_b_class_phase2_expansion_closure_summary.md) 已读
- [ ] Phase 2 commit `b4a6e6e` 已确认

---

## 50-Company Universe Reviewed

- [ ] [universe draft](cninfo_b_class_phase25_expansion_universe_draft.csv) 已审阅（**50** 家 · B25E001–B25E050）
- [ ] [candidate design](cninfo_b_class_phase25_candidate_universe_design.csv) 已审阅
- [ ] phase1_overlap = **0** · phase2_overlap = **0**
- [ ] 无 ST / *ST / 退市 / BSE legacy

---

## Endpoint Mix Reviewed

- [ ] periodic_report（EP004）：约 **25** case
- [ ] general_announcement（EP005）：约 **25** case
- [ ] EP001：全 case 主检索
- [ ] EP002：金融样本约 **7** case 含 orgId 路径

---

## Output Root Isolated

- [ ] 输出根 = `outputs/validation/cninfo_b_class_phase25_expansion/`
- [ ] **禁止**写入 `cninfo_b_class_phase2_expansion/`
- [ ] **禁止**写入 Phase 1 / TLC002 根
- [ ] **禁止**写入 `outputs/harvest/`

---

## Metadata Only — No PDF

- [ ] **无 PDF download**
- [ ] **无 PDF parse**
- [ ] **无 OCR / section extraction**
- [ ] URL lineage only

---

## No DB / MinIO / RAG

- [ ] **无 DB 写入**
- [ ] **无 MinIO 写入**
- [ ] **无 RAG / embeddings**

---

## Explicit User Approval Required

- [ ] [command draft](../../plans/cninfo_b_class_phase25_expansion_command_draft.md) 已审阅
- [ ] `--approve-b-class-phase25-expansion` 已实现（**未来回合**）
- [ ] runner 扩展已完成（**未来回合**）
- [ ] 用户 **显式书面批准** live execution

---

## Gate Status

```text
b_class_phase25_expansion_planning_gate = READY_FOR_APPROVAL
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## Red Lines

- No CNINFO in this planning round
- No live until explicit approval
- No verified · No production_ready · No testing_stable_sample upgrade
