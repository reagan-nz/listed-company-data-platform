# CNINFO B 类 Phase 3 100-Company Expansion Plan

_生成时间：2026-07-09_

> **性质：** Phase 2.5（50/50 effective）收口后的 100 家扩大样本规划；**离线 only** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**Phase 2.5 commit：** `812ad54`（Close B-class Phase 2.5 metadata retry track）

---

## 1. Objective

在 **phase1_freeze_v1 schema 不变** 的前提下，将 B-class live metadata validation 规划扩大至 **100** 家公司：

- **50** EP004 periodic-report oriented cases
- **50** EP005 general-announcement oriented cases
- **EP001** announcement query：全 **100** case
- **EP002** company/orgId resolution：金融样本按需启用
- 使用 **独立输出根** `outputs/validation/cninfo_b_class_phase3_100_expansion/`
- **metadata + pdf URL lineage only**
- **不**标 verified · **不**宣称 production_ready · **不**升级 testing_stable_sample

---

## 2. Why Phase 3 Is Planning-Only Now

1. **Phase 2.5 刚完成 commit boundary**（`812ad54`）：需先完成离线 universe 设计与批准包，再进入 runner 扩展与 live。
2. **100 家规模风险上升**：Phase 2.5 已出现 **5/50 network_error**（后由 isolated retry 恢复）；100 家需更严格 bucket 设计与 rate limit 预案。
3. **runner 尚未支持 `--phase3-100`**：当前 `run_cninfo_b_class_phase25_expansion_validation.py` 仅支持 Phase 2.5 expansion 与 failed retry 模式。
4. **红线约束**：本任务 **不调用 CNINFO**、**不 live**、**不 PDF/OCR/extraction/DB/MinIO/RAG**。

---

## 3. Phase 1 / Phase 2 / Phase 2.5 Evidence Recap

### Phase 1 Tiny Live

| 项 | 值 |
|----|-----|
| closure gate | `b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT` |
| cases | **5** · resolved **5** · failed **0** |
| TLC002 | EP002 `network_error` → isolated retry recovered |
| endpoints | EP001 · EP002 · EP004 · EP005 |
| PDF / DB / MinIO / RAG | **0** |

### Phase 2 Expansion

| 项 | 值 |
|----|-----|
| execution gate | `b_class_phase2_expansion_execution_gate = PASS_WITH_CAVEAT` |
| closure gate | `b_class_phase2_expansion_closure_gate = PASS_WITH_CAVEAT` |
| cases | **20** · acceptable **20** · failed **0** |
| CNINFO requests | **40** |
| endpoint hits | EP001 **20** · EP002 **20** · EP004 **12** · EP005 **8** |
| PDF download / parse | **0** |

### Phase 2.5 Expansion + Failed Retry

| 项 | 值 |
|----|-----|
| expansion execution gate | `b_class_phase25_expansion_execution_gate = PASS_WITH_CAVEAT` |
| expansion closure gate | `b_class_phase25_expansion_closure_gate = PASS_WITH_CAVEAT` |
| failed retry execution gate | `b_class_phase25_failed_retry_execution_gate = PASS_WITH_CAVEAT` |
| failed retry closure gate | `b_class_phase25_failed_retry_closure_gate = PASS_WITH_CAVEAT` |
| original success | **45/50** acceptable |
| retry recovered | **5/5** found |
| **effective coverage** | **50/50** · unresolved **0** |
| CNINFO（expansion + retry） | **93 + 10 = 103** |
| PDF / OCR / extraction / DB / MinIO / RAG | **0** |

Phase 2.5 证明 50 家批次可在 metadata-only 边界内达到 **100% effective coverage**（含 isolated retry）；仍不足以支撑全市场失败率统计或长期批次稳定性结论，但为 Phase 3 100 家提供了可复用 playbook。

---

## 4. Endpoint Scope

| Endpoint | 角色 | Phase 3 覆盖 |
|----------|------|-------------|
| EP001 | announcement query 主检索 | **100/100** |
| EP002 | company/orgId resolution | 金融样本按需（约 **4** case） |
| EP004 | periodic-report metadata | **50** case |
| EP005 | general-announcement metadata | **50** case |

**禁止：** PDF download · PDF parse · OCR · section extraction · DB · MinIO · RAG

---

## 5. Sampling Design

| 项 | 值 |
|----|-----|
| sample size | **100** |
| case ID | B3E001–B3E100 |
| overlap Phase 1 | **0** |
| overlap Phase 2 | **0** |
| overlap Phase 2.5 | **0** |
| periodic_report（EP004） | **50** |
| general_announcement（EP005） | **50** |
| 市场分布（draft） | SSE主板 **50** · SZSE主板 **40** · 创业板 **5** · 科创板 **5** |

**候选池来源：** `lab/eval_companies_full_market_2024.yaml`（`full_market_2024` registry）

**bucket 设计：** 见 [cninfo_b_class_phase3_100_candidate_universe_design.csv](../outputs/validation/cninfo_b_class_phase3_100_candidate_universe_design.csv)

**universe draft：** [cninfo_b_class_phase3_100_universe_draft.csv](../outputs/validation/cninfo_b_class_phase3_100_universe_draft.csv)

---

## 6. Exclusion Rules

1. 排除 Phase 1 tiny live universe（**5** codes）
2. 排除 Phase 2 expansion universe（**20** codes）
3. 排除 Phase 2.5 expansion universe（**50** codes）
4. 排除 Phase 2.5 failed retry 重复（retry 为 expansion 子集，主 universe 已去重）
5. 排除 ST / *ST / 退市公司
6. 默认排除 BSE（北交所），除非未来显式允许
7. 避免已知未解决 identity 映射问题
8. universe 内 `company_code` 不得重复

---

## 7. Risk Controls

| 风险 | 控制措施 |
|------|----------|
| network transient error | 沿用 Phase 2.5 isolated retry playbook；100 家需预留 retry budget |
| rate limit / HTTP 429 | `--sleep-seconds 0.6`；并发 **1**；429 全局停止 |
| output root 污染 | 强制 `cninfo_b_class_phase3_100_expansion/`；禁止写入 Phase 1/2/2.5 根 |
| scope creep | metadata only；PDF/OCR/extraction/DB/MinIO/RAG 红线 |
| prior-phase overlap | universe draft 离线校验 **0 overlap** |
| runner 误用 | 需 `--approve-b-class-phase3-100-expansion` + `--phase3-100`（未来实现） |

---

## 8. Expected Outputs（未来 live 回合）

| 输出 | 路径 |
|------|------|
| dry-run report | `outputs/validation/cninfo_b_class_phase3_100_expansion/reports/` |
| live expansion report | 同上 |
| quality report | 同上 |
| closure metrics | `outputs/validation/` |

**本回合仅产出规划包，不创建上述 live 输出。**

---

## 9. Approval Requirements

1. [universe draft](../outputs/validation/cninfo_b_class_phase3_100_universe_draft.csv) 人工审阅（**100** 行）
2. [candidate design](../outputs/validation/cninfo_b_class_phase3_100_candidate_universe_design.csv) 审阅
3. [approval checklist](../outputs/validation/cninfo_b_class_phase3_100_approval_checklist.md) 逐项确认
4. [command draft](cninfo_b_class_phase3_100_command_draft.md) 审阅
5. runner 扩展（`--phase3-100` + approval flag）**未来回合**
6. 用户 **显式书面批准** live execution

---

## 10. Red Lines

- No CNINFO in this planning round
- No live until explicit approval
- No PDF download / parse / OCR / extraction
- No DB / MinIO / RAG
- No verified · No production_ready · No testing_stable_sample upgrade
- No commit in this task

---

## 11. No Live Execution In This Task

本任务 **仅** 产出离线规划包：

- planning document
- candidate universe design CSV
- universe draft CSV（100 rows）
- approval checklist
- command draft
- planning summary
- status doc updates

**CNINFO calls = 0** · **live execution = 0**

---

## Gate Status

```text
b_class_phase3_100_planning_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** · **NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**
