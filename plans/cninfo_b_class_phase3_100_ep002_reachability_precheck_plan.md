# CNINFO B 类 Phase 3 EP002/orgId Reachability Precheck 规划

_生成时间：2026-07-09_

> **性质：** 离线规划 only · **无 CNINFO** · **无 live** · **无 precheck 执行** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在任意 **retry_v2** live 批准之前，准备一套 **轻量级 EP002/orgId 可达性 precheck** 规划包，用于验证 CNINFO topSearch orgId 解析路径是否恢复，避免对 **91** 例 persistent failure 再次执行无效 metadata retry。

**前置 closure gate：** `b_class_phase3_100_failed_retry_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED`

**本规划 gate：** `b_class_phase3_100_ep002_reachability_precheck_planning_gate = READY_FOR_APPROVAL`

---

## 2. Why Precheck Is Needed Before retry_v2

| 轮次 | 结果 | CNINFO requests |
|------|------|-----------------|
| Phase 3 original live | **1/100** acceptable | **3** |
| Phase 3 failed retry live | **8/99** recovered · **91** failed | **18** |
| Combined effective | **9/100** accepted · **91** unresolved | — |

original 与 failed retry 均在 **EP002_topSearch_orgId** 阶段大规模失败。8 例 retry 恢复证明 metadata pipeline 在 orgId 可用时正常，但 **91/100** 仍 unresolved。直接批准 retry_v2 将重复无效 CNINFO 消耗。

Precheck 目的：

- 在 **最小请求预算**（≤ **16**）内探测 EP002 orgId 路径是否可达
- 为 retry_v2 人工批准提供 **基础设施 go/no-go** 信号
- **不** 执行 metadata retry · **不** 调用 EP001/EP004/EP005 · **不** 下载 PDF

---

## 3. Original Phase 3 Live Recap

| 指标 | 值 |
|------|-----|
| cases | **100** |
| acceptable | **1**（B3E087 hold） |
| failed | **99** |
| CNINFO requests | **3** |
| dominant failure | `network_error` at **EP002_topSearch_orgId** |
| gate | `b_class_phase3_100_execution_gate = FAIL_REVIEW_REQUIRED` |

---

## 4. Failed Retry Live Recap

| 指标 | 值 |
|------|-----|
| retry universe | **99**（B3E087 excluded） |
| recovered | **8** |
| persistent failed | **91** |
| CNINFO requests | **18** |
| gate | `b_class_phase3_100_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED` |

---

## 5. Effective Merged Result Recap

| 来源 | 数量 | final_effective_status |
|------|------|------------------------|
| original hold（B3E087） | **1** | `accepted_original_success` |
| retry recovered | **8** | `accepted_retry_recovered` |
| persistent unresolved | **91** | `unresolved_ep002_orgid_network_failure` |
| **effective accepted** | **9/100** | |

详见 [effective merged result](../outputs/validation/cninfo_b_class_phase3_100_effective_merged_result.csv)

---

## 6. Ninety-One Persistent EP002/orgId Failure Recap

| 指标 | 值 |
|------|-----|
| count | **91** |
| failure stage | **EP002_topSearch_orgId** |
| schema_impact | **none** |
| quality_impact | **unresolved_network_caveat** |
| recommended_action | `hold_until_ep002_reachability_precheck` |

详见 [persistent failure ledger](../outputs/validation/cninfo_b_class_phase3_100_persistent_failure_ledger.csv)

---

## 7. Why Immediate Full Retry Is Not Recommended

1. **91/100** unresolved — full retry 预期重复 EP002 failure 模式
2. isolated retry 仅恢复 **8/99** — 未达 **90/99** threshold
3. 8 例恢复证明 **非 schema failure** — 问题在 orgId 可达性
4. B3E087 hold — 不得纳入任何 rerun batch
5. Phase 3 scope 固定 **100** — 不得扩展 universe

---

## 8. Why This Is Infrastructure-Focused

| 证据 | 含义 |
|------|------|
| 8 retry recoveries with `found/pass/discovered` | metadata pipeline 可用 |
| failure at EP002 only | 早于 EP001/EP004/EP005 |
| schema_impact = **none** | 不改 schema |
| CNINFO requests << planned cap | early-exit network failure |
| same failure type original + retry | transient/persistent reachability |

Precheck 仅验证 **EP002 orgId resolution 可达性**，不重新裁定 metadata 质量。

---

## 9. Candidate Selection Strategy

从 **91** 例 persistent failure ledger 中选取 **5–8** 例代表性候选：

| 维度 | 覆盖要求 |
|------|----------|
| markets | SSE主板 · SZSE主板 · 创业板 · 科创板（≥ 2 markets） |
| announcement types | `periodic_report`（EP004）· `general_announcement`（EP005） |
| universe position | early · mid · late case_id |
| failure consistency | original Phase 3 + failed retry 均 `network_error` |

**排除：**

- B3E087（hold）
- 8 recovered retry cases（B3E003–B3E011 subset）
- prior B-class Phase 1 / 2 / 2.5 cases

**选定 8 例：** 见 [precheck candidates](../outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv)

---

## 10. Request Cap

| 项 | 值 |
|----|-----|
| precheck 候选数 | **8** |
| 每候选 planned check | **1** × `ep002_orgid_reachability` |
| 未来 live 请求上限 | **≤ 16**（含可选 1 次全局 topSearch probe） |
| 估算 planned requests | **8**（dry-run） |

---

## 11. Output Isolation

**专用 precheck 输出根：**

```text
outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/
```

**Write-blocked：**

- `outputs/validation/cninfo_b_class_phase3_100_expansion/`
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry/`
- `outputs/validation/cninfo_b_class_phase25_expansion/`
- `outputs/validation/cninfo_b_class_phase25_failed_retry/`

---

## 12. Approval Requirements

| 项 | 要求 |
|----|------|
| approval flag | `--approve-b-class-phase3-100-ep002-reachability-precheck` |
| approval_status | **NOT_APPROVED** |
| explicit human approval | required before live precheck |
| runner | **design only** — 本回合不实现 |

---

## 13. Interpretation Rules

| precheck 结果 | 含义 |
|---------------|------|
| orgId resolved | EP002 路径当前可达；可考虑 retry_v2 规划 |
| orgId not resolved | 基础设施仍不可用；hold with caveat |
| ≥ 60% candidates resolve | `PASS_WITH_CAVEAT` execution gate |
| < 60% candidates resolve | `FAIL_REVIEW_REQUIRED` execution gate |

**Never：** `PASS` · `verified` · `production_ready`

---

## 14. Red Lines

| 项 | 状态 |
|----|------|
| CNINFO calls（本回合） | **0** |
| live / precheck execution | **0** |
| retry_v2 package | **not created** |
| B3E087 rerun | **no** |
| 8 recovered cases rerun | **no** |
| 91 persistent full retry | **no** |
| schema / endpoint model change | **no** |
| PDF / OCR / DB / MinIO / RAG | **disabled** |
| verified / production_ready | **no** |

---

## 15. Next Step After Precheck

1. **若 PASS_WITH_CAVEAT（≥ 60% orgId resolve）：** 准备 retry_v2 planning package（仍须独立批准 · 非 automatic）
2. **若 FAIL_REVIEW_REQUIRED：** hold Phase 3 with network caveat（Option B）或 offline orgId fallback design（Option C）
3. **无论结果：** 不自动扩展 beyond approved Phase 3 scope

---

## Artifacts

| 项 | 路径 |
|----|------|
| candidates | [cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv](../outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv) |
| approval checklist | [cninfo_b_class_phase3_100_ep002_reachability_precheck_approval_checklist.md](../outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_approval_checklist.md) |
| command draft | [cninfo_b_class_phase3_100_ep002_reachability_precheck_command_draft.md](cninfo_b_class_phase3_100_ep002_reachability_precheck_command_draft.md) |
| runner design | [cninfo_b_class_phase3_100_ep002_reachability_precheck_runner_design.md](cninfo_b_class_phase3_100_ep002_reachability_precheck_runner_design.md) |
| planning summary | [cninfo_b_class_phase3_100_ep002_reachability_precheck_planning_summary.md](../outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_planning_summary.md) |
