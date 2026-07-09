# CNINFO B 类 Phase 2 Expansion — 批准检查清单

_生成时间：2026-07-09_

> **性质：** 未来 Phase 2 live expansion 执行前的批准包；**本轮不执行 live** · **NOT APPROVED**

**前置：** [cninfo_b_class_phase2_expansion_plan.md](../../plans/cninfo_b_class_phase2_expansion_plan.md) · Phase 1 closure gate **`PASS_WITH_CAVEAT`**

---

## Preconditions

| # | 条件 | 要求 | 当前状态 |
|---|------|------|----------|
| 1 | Phase 1 closure | `b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT` · **5/5 resolved** | **PASS_WITH_CAVEAT** |
| 2 | Phase 1 schema | phase1_freeze_v1 **不变** | **unchanged** |
| 3 | TLC002 retry | failure + isolated retry 已审阅 | **documented** |
| 4 | output isolation | 产物仅写入 `outputs/validation/cninfo_b_class_phase2_expansion/` | **已定义** |
| 5 | planning gate | `b_class_phase2_expansion_planning_gate = READY_FOR_APPROVAL` | **READY_FOR_APPROVAL** |

### 并行安全（执行前再确认）

- [ ] C-class Phase 3 live harvest **未在并发运行**
- [ ] `outputs/harvest/cninfo_c_class/` **未被读写**
- [ ] C-class status 保持 **`SNAPSHOT_GENERATED_QA_REVIEW`**
- [ ] A-class / D-class 输出 **未被修改**

---

## Phase 1 Closure Reviewed

- [ ] [closure review](../../plans/cninfo_b_class_phase1_tiny_live_closure_review.md) 已读
- [ ] [final metrics](cninfo_b_class_phase1_tiny_live_final_metrics.csv) 已读（**5/5 resolved**）
- [ ] [closure summary](cninfo_b_class_phase1_tiny_live_closure_summary.md) 已读
- [ ] Phase 1 **不是 verified** · **不是 production_ready** 已确认

---

## TLC002 Retry Understood

- [ ] [failure analysis](cninfo_b_class_tlc002_failure_analysis.md) 已读
- [ ] [decision summary](cninfo_b_class_tlc002_failure_decision_summary.md) 已读（**retry_candidate**）
- [ ] [retry execution summary](cninfo_b_class_tlc002_retry_execution_summary.md) 已读（**failure recovered**）
- [ ] Phase 2 retry 策略：主批次不 inline retry · isolated retry 须单独批准

---

## Output Root Isolated

- [ ] 输出根 = `outputs/validation/cninfo_b_class_phase2_expansion/`
- [ ] **禁止**写入 `cninfo_b_class_tiny_live_validation/`
- [ ] **禁止**写入 `cninfo_b_class_tlc002_retry/`
- [ ] **禁止**写入 `outputs/harvest/`

---

## Sample Size Approved

- [ ] [candidate universe design](cninfo_b_class_phase2_candidate_universe_design.csv) 已审阅
- [ ] [20-company universe draft](cninfo_b_class_phase2_expansion_universe_draft.csv) 已审阅
- [ ] 样本规模已人工选定：
  - [ ] Option A：**20**
  - [ ] Option B：**50**
  - [ ] Option C：**100**
- [ ] 无 ST / *ST / 退市 / BSE legacy / manual identity review 样本
- [ ] 活跃上市公司 only

---

## Metadata Only — No PDF

- [ ] **无 PDF download**
- [ ] **无 PDF parse**
- [ ] **无 OCR / text extraction**
- [ ] pdf URL lineage only（`adjunct_url` / `pdf_url` 登记）

---

## No DB / MinIO / RAG

- [ ] **无 DB 写入**
- [ ] **无 MinIO 写入**
- [ ] **无 RAG / embeddings / vector index**

---

## Explicit User Approval Required

- [ ] [command draft](../../plans/cninfo_b_class_phase2_expansion_command_draft.md) 已审阅
- [ ] `--approve-b-class-phase2-expansion` flag 已实现（**未来回合**）
- [ ] runner 扩展已完成（**未来回合**）
- [ ] 用户 **显式书面批准** live execution（本清单勾选 + 批准摘要 signoff）

---

## Gate Status

```text
b_class_phase2_expansion_planning_gate = READY_FOR_APPROVAL
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## Red Lines

- No CNINFO in this planning round
- No live execution until explicit approval
- No TLC002 retry in Phase 2 planning round
- No verified · No production_ready · No testing_stable_sample upgrade
