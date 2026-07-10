# CNINFO B 类 Phase 3 100-Company — Failed Case Triage Review

_生成时间：2026-07-09_

> **性质：** 离线失败分类评审；**无 CNINFO** · **无 live** · **无 retry** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

对 Phase 3 100-company live metadata validation 的 **99** 例失败进行离线分类，明确：

- 失败模式是否为 transient network / EP002 orgId resolution 问题
- 是否构成 schema / endpoint model 失败
- 是否应对 **B3E087**（唯一成功 case）进行 isolated retry
- 是否应准备 **99-case isolated retry** 批准包（**本回合不执行**）

---

## 2. Live Execution Recap

| 项 | 值 |
|----|-----|
| execution gate | `b_class_phase3_100_execution_gate = FAIL_REVIEW_REQUIRED` |
| universe | B3E001–B3E100（**100** 家） |
| CNINFO requests | **3** |
| acceptable | **1** |
| failed | **99** |
| needs_review | **99** |
| empty_but_valid | **0** |
| PDF download / parse | **0** |
| OCR / extraction / DB / MinIO / RAG | **0** |

**报告：** [b_class_phase3_100_report.csv](../outputs/validation/cninfo_b_class_phase3_100_expansion/reports/b_class_phase3_100_report.csv)

---

## 3. Preflight Recap

执行前 **15/15** preflight checks 全部通过：

- universe size = **100** · case IDs B3E001–B3E100
- phase3_include = yes · prior_phase_overlap = no
- duplicate company_code = **0** · prior-phase overlap = **0**
- output root isolated · Phase 2.5 roots write-blocked
- PDF / OCR / extraction / DB / MinIO / RAG disabled
- no staged files before execution

Preflight 通过说明 universe 与 runner 边界正确；失败不应归因于 universe 设计错误。

---

## 4. Acceptable Case Recap

| case_id | company | code | retrieval | quality | lineage | PDF URL lineage |
|---------|---------|------|-----------|---------|---------|-----------------|
| B3E087 | 北新建材 | 000786 | found | pass | discovered | present |

**1/100 acceptable** — 低于 **90** 阈值，触发 `FAIL_REVIEW_REQUIRED`。

---

## 5. Failed Case Pattern

| 指标 | 值 |
|------|-----|
| failed count | **99** |
| dominant retrieval_status | `network_error` (**99**) |
| dominant failure_stage | `EP002_topSearch_orgId` |
| dominant notes | `EP002 orgId resolution failed` |
| EP001 reached | **1** case only（B3E087） |

**分类结论：** 失败高度集中于 EP002 orgId 解析阶段；EP001 announcement query 对 **98** 例未执行。

---

## 6. EP002 orgId Resolution Failure Analysis

1. **执行路径：** `execute_live_case` 对所有 case 先调用 `resolve_orgid`（EP002 topSearch），orgId 失败则直接返回 `network_error`，不进入 EP001。
2. **CNINFO 请求仅 3 次：** 说明绝大多数 case 在 EP002 阶段快速失败（网络/代理异常），未产生有效 HTTP 往返计数或请求在异常路径提前终止。
3. **与 Phase 2.5 模式一致：** Phase 2.5 亦有 **5/50** `network_error` / EP002 相关失败，后由 isolated retry **5/5** 恢复。
4. **与 Phase 1 TLC002 模式一致：** TLC002 亦为 EP002 orgId resolution 失败后 isolated retry 恢复。

**interpretation：** 高度可能为 transient CNINFO / proxy / orgId-resolution 环境故障，**非** schema 字段缺失或 endpoint 模型错误。

---

## 7. Why This Is Not Currently a Schema Failure

| 证据 | 说明 |
|------|------|
| B3E087 success | 同一 runner · 同一 schema · 同一 endpoint 模型下 **1** 例 full `found/pass/discovered` |
| failure_stage 一致 | **99** 例均在 EP002 阶段失败，非 EP001 字段映射或 quality lint 失败 |
| schema_impact | **none**（无 required field 系统性缺失证据） |
| phase1_freeze_v1 | **未变更** |
| universe | **未变更** |

**不修改：** schema · endpoint model · universe draft

---

## 8. Why B3E087 Must Not Be Rerun

- B3E087 已达 `found` / `pass` / `discovered`，PDF URL lineage present
- rerun 将重复 CNINFO 调用并可能污染 isolated retry 统计
- 应记入 [success hold ledger](../outputs/validation/cninfo_b_class_phase3_100_success_hold_ledger.csv)，合并入最终 effective result
- `rerun_allowed = no`

---

## 9. Why Prior Phases Must Not Be Rerun

| Phase | 原因 |
|-------|------|
| Phase 1（5） | 已收口 · closure gate PASS_WITH_CAVEAT |
| Phase 2（20） | 已收口 · 20/20 acceptable |
| Phase 2.5（50） | 已收口 · 50/50 effective |
| Phase 2.5 retry（5） | 已收口 · 5/5 recovered |

Retry universe **仅** 包含 Phase 3 原始 batch 中 **99** 例失败 case（B3E001–B3E100 除 B3E087）。

---

## 10. Red-Line Confirmations

| 红线 | 本回合 |
|------|--------|
| CNINFO | **0** |
| live / retry | **0** |
| B3E087 rerun | **no** |
| prior-phase rerun | **no** |
| universe mutation | **no** |
| expansion beyond 100 | **no** |
| PDF / OCR / extraction | **0** |
| DB / MinIO / RAG | **0** |
| verified / production_ready | **no** |

---

## 11. Recommended Retry Strategy

1. **Isolated retry batch：** **99** cases only（exclude B3E087）
2. **Output root：** `outputs/validation/cninfo_b_class_phase3_100_failed_retry/`
3. **Approval flag（未来）：** `--approve-b-class-phase3-100-failed-retry`
4. **Runner flag（未来）：** `--phase3-100-failed-retry`（**本回合不实现**）
5. **Acceptance threshold：** retry acceptable **>= 90/99** → `PASS_WITH_CAVEAT`；否则 `FAIL_REVIEW_REQUIRED`
6. **Merge model：** 1 accepted original + N retry recovered → effective coverage（未来 closure 回合）

---

## Gate

```text
b_class_phase3_100_failed_case_triage_gate = READY_FOR_REVIEW
```

**NOT PASS** · **NOT verified** · **NOT production_ready**
