# CNINFO C-Class Phase 3 Next-Step Recommendation

_生成时间：2026-07-09_

> 规划建议 only。**不执行** · **无 CNINFO** · **无 live**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**前置 gate：** `phase3_batch_500_closure_gate = PASS_WITH_CAVEAT`

---

# Context

Phase 3 batch 500 已完成：

- **500** input · **9** identity caveat excluded · **491** snapshot JSON
- harvest / build / QA 全链路 `PASS` 或 `PASS_WITH_CAVEAT`
- **非 verified** · **非 production_ready** · **非 full-market**

---

# Option A — Phase 3.5 Another 500-Company Batch

| 项 | 说明 |
|----|------|
| scope | 再选 **500** 家 matched_active 候选 |
| exclusions | already_in_c_class · hold · BSE · identity_conflict · delisted/inactive caveat |
| safeguards | output-root isolation · dry-run · explicit approval · identity triage before snapshot |
| deliverable | `phase3_batch_500_002` planning + universe selection |
| pros | 延续已验证 pipeline；增量扩源；风险可控 |
| cons | 仍非 full-market；identity caveat 可能重复出现 |

---

# Option B — Phase 4 1000-Company Expansion

| 项 | 说明 |
|----|------|
| scope | 单次 **1000** 家 batch |
| prerequisites | registry refresh · stronger delisted pre-filter · harvest runner capacity review |
| pros | 更快接近 matched_active 池规模 |
| cons | 失败面更大；identity caveat 成本更高；**不推荐在 closure 后立即执行** |

---

# Option C — Identity Caveat Cleanup Before Expansion

| 项 | 说明 |
|----|------|
| scope | 处理 Phase 3 **9** 家 + Phase 2 **12** 家 + registry candidate refresh |
| focus | `manual_identity_review`（`600705` · `601028`）· delisted_or_reorganized 标记强化 |
| deliverable | registry candidate refresh execution plan update |
| pros | 降低下一 batch identity noise |
| cons | 不直接增加 snapshot 数量；需 registry 政策决策 |

---

# Option D — Begin A/B/D Integration Planning

| 项 | 说明 |
|----|------|
| scope | C-class snapshot 与 A-class report metadata · B-class announcement · D-class market behavior 集成规划 |
| focus | 离线 schema alignment · readiness matrix · 无 live |
| pros | 为多类数据源协同铺路；不急于扩 C-class 规模 |
| cons | 不直接产生新 C-class snapshot |

---

# Recommended Next

**Primary recommendation：** **Option A**（Phase 3.5 another 500-company batch planning）

**Parallel recommendation：** **Option D**（A/B/D integration planning）

**Rationale：**

1. Phase 3 pipeline 已验证；下一 batch 可复用 safeguards
2. **491** snapshot 仍非 full-market；Option A 以可控步长继续扩源
3. A/B/D 并行规划不阻塞 C-class 扩源，且为长期集成必要
4. Option B（1000 家）风险过高，**不推荐在 closure 后立即启动**
5. Option C 可作为 Option A 前置增强，但非阻塞项

**Do not recommend yet：**

- Phase 4 / 1000-company live execution
- full-market harvest authorization
- verified / testing_stable_sample upgrade
- production_ready declaration

---

# Sequencing Suggestion

| 顺序 | 任务 | 类型 |
|------|------|------|
| 1 | Phase 3.5 batch 500 planning（universe selection design） | offline planning |
| 2 | A/B/D integration planning kickoff | offline planning |
| 3 | Identity caveat registry refresh review（Option C 子集） | offline review |
| 4 | Phase 3.5 live harvest approval package | approval prep only |

---

# Red Lines（所有选项共用）

- **no CNINFO**（除非未来显式批准 live batch）
- **no verified**
- **no production_ready**
- **no testing_stable_sample**
- **no DB / MinIO / RAG**
- **no full snapshot overwrite**
