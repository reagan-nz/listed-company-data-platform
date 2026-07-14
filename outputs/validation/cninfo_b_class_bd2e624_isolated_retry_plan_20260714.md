# CNINFO B 类 BD2E624 — Isolated Retry Plan

_生成时间：2026-07-14 · task **B-GEN-20260714-06** · offline prep only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** isolated retry 离线准备包 · **NOT verified** · **NOT production_ready** · **NOT approved for live CNINFO**

**Human 批准（本轨）：** B-class BD2E624 next-step validation/retry work（prep 阶段 · 不含 live 执行）

**前置证据（cite only · 只读保留 · 不得删除）：**

| 工件 | 路径 |
|------|------|
| offline triage | [cninfo_b_class_bd2e624_offline_triage_20260714.md](cninfo_b_class_bd2e624_offline_triage_20260714.md) |
| validation rules | [cninfo_b_class_bd2e624_offline_validation_rules_20260714.md](cninfo_b_class_bd2e624_offline_validation_rules_20260714.md) |
| precheck checklist | [cninfo_b_class_bd2e624_offline_precheck_checklist_20260714.csv](cninfo_b_class_bd2e624_offline_precheck_checklist_20260714.csv) |
| precheck status（本包更新） | [cninfo_b_class_bd2e624_isolated_retry_precheck_status_20260714.csv](cninfo_b_class_bd2e624_isolated_retry_precheck_status_20260714.csv) |
| unresolved ledger | [cninfo_b_class_erad_fuller_next_slice2_unresolved_case_ledger.csv](cninfo_b_class_erad_fuller_next_slice2_unresolved_case_ledger.csv) |
| live report row 125 | [cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_report.csv](cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_report.csv) |
| quality JSON | [cninfo_b_class_erad_fuller_next_slice2/quality/BD2E624.json](cninfo_b_class_erad_fuller_next_slice2/quality/BD2E624.json) |
| session1 log | [cninfo_b_class_erad_fuller_next_slice2_session1_live.log](cninfo_b_class_erad_fuller_next_slice2_session1_live.log) |
| edge-case row 10 | [cninfo_b_class_erad_fuller_next_slice2_edge_case_classification.csv](cninfo_b_class_erad_fuller_next_slice2_edge_case_classification.csv) |
| merge closure | [cninfo_b_class_erad_fuller_next_slice2_merge_closure_summary.md](cninfo_b_class_erad_fuller_next_slice2_merge_closure_summary.md) |
| ER-VAL 对比 | [cninfo_b_class_empty_response_edge_taxonomy_20260714.md](cninfo_b_class_empty_response_edge_taxonomy_20260714.md) |
| cross-slice index | [cninfo_b_class_cross_slice_erval_index_20260714.md](cninfo_b_class_cross_slice_erval_index_20260714.md) |

**参照模式：** [plans/cninfo_b_class_tlc002_isolated_retry_plan.md](../../plans/cninfo_b_class_tlc002_isolated_retry_plan.md) · [plans/cninfo_b_class_erad_fuller_next_slice_command_draft.md](../../plans/cninfo_b_class_erad_fuller_next_slice_command_draft.md)

---

## 1. Case Anchor

| 字段 | 值 | 证据 |
|------|-----|------|
| task_id | **B-GEN-20260714-06** | controller task |
| case_id | **BD2E624** | unresolved ledger（1 row） |
| company_code | **300778**（新城市） | live report row 125 |
| cohort | `fuller_next_slice2` | candidate universe row 125 |
| session（原始） | Session 1 | session1 live log |
| baseline retrieval_status | `network_error` | unresolved ledger · live report |
| root_cause_family | **EP002-NET** · `ep002_orgid_network_error` | edge-case classification row 10 |
| baseline disposition | `unresolved_failed` · **deferred** | triage · merge closure |
| slice2 主 gate | **`PASS_WITH_CAVEAT`** · 299/300 acceptable | merge closure · validation rules §3.2 F1–F3 |
| integration commit | `f0bff3a` · post-integration **HOLD** | CURRENT_STATUS.md · PROJECT_CONTROL.md |

### 1.1 邻接对照（同 session）

| case_id | company_code | retrieval_status | 说明 |
|---------|--------------|------------------|------|
| BD2E624 | 300778 | `network_error` | EP002 orgId 解析失败 · **本 retry 目标** |
| BD2E625 | 300782 | `found` | 同 session 成功 · 非结构性缺陷信号 |
| BD2E537 | 002710 | `empty_response` | ER-VAL 族 · **非** network_error · 验收对照 |

---

## 2. Retry Reason

1. **瞬态 EP002 orgId 网络失败** — 同 session 邻接 case BD2E625 `found`；根因族 EP002-NET，非 schema/endpoint 结构性缺陷（triage §2）。
2. **slice2 收口已满足** — 299/300 acceptable · unresolved 1 ≤ 30 · BD2E624 defer 不阻塞主 gate `PASS_WITH_CAVEAT`（merge closure §Gate Judgment）。
3. **Human 已批准 next-step validation/retry work** — 允许本离线 prep 包；**live CNINFO 仍须 separate phrase + precheck 全绿**。
4. **不得 offline force-resolve** — baseline `network_error` 保留至 live 完成（validation rules §3 · precheck PC-BD2E-022）。

---

## 3. Retry Scope

| 约束 | 值 |
|------|-----|
| universe | **1/1** — 仅 BD2E624 / 300778 |
| universe CSV | [cninfo_b_class_bd2e624_isolated_retry_universe_20260714.csv](cninfo_b_class_bd2e624_isolated_retry_universe_20260714.csv) |
| case-range | `BD2E624:BD2E624` |
| endpoint chain | **EP002 → EP001**（orgId 解析 → 目标端点 EP004/EP005） |
| CNINFO cap（live） | **≤ 2**（1×EP002 + 1×EP001） |
| 混批 | **禁止** — 不得与 16 例 ER-VAL requery 混批（VR-MIS-05 · PC-BD2E-012） |
| 重跑 BD2E001–800 其他 case | **禁止** |
| PDF / OCR / DB / MinIO / RAG | **禁止** |
| verified / production_ready | **禁止** |
| slice2 主根 mutate | **禁止** |

---

## 4. Output Isolation

**专用隔离根（强制）：**

```text
outputs/validation/cninfo_b_class_erad_fuller_next_slice2_bd2e624_retry/
├── raw_metadata/
├── quality/
│   └── BD2E624.json
└── reports/
    ├── b_class_erad_fuller_next_slice2_bd2e624_retry_report.csv
    ├── b_class_erad_fuller_next_slice2_bd2e624_retry_quality_report.csv
    └── b_class_erad_fuller_next_slice2_bd2e624_retry_summary.md
```

### 4.1 Write-Block（不得写入）

| 路径 | 原因 |
|------|------|
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/` | slice2 主 harvest 根 · 只读保留失败证据 |
| `outputs/validation/cninfo_b_class_erad_scale_200/` | scale-200 lineage-reference only |
| `outputs/validation/cninfo_b_class_erad_next_scale_slice1/` | slice1 lineage-reference only |
| `outputs/validation/cninfo_b_class_phase3_100_*` | Phase3 根 untouched |
| A/C/D validation / harvest / snapshot production roots | 跨轨写保护 |

**红线：** 不得 retroactive 修改 slice2 主 merge closure summary（VR-MRG-04）。

---

## 5. Endpoint Chain — EP002 → EP001

```text
EP002 topSearch/query（orgId 解析）
├── FAIL（network/timeout/HTTP）→ retrieval_status = network_error
│   └── EP002-NET · unresolved_failed · FAIL_REVIEW_REQUIRED
│
└── SUCCESS → EP001 hisAnnouncement/query → EP004/EP005
    ├── 公告列表非空 → retrieval_status = found
    │   └── PASS_WITH_CAVEAT（retry execution）· recovered
    │
    └── 公告列表为空 → retrieval_status = empty_response
        └── ER-VAL 子类 · acceptable_edge · PASS_WITH_CAVEAT（retry execution）
```

**Misclassification guards（验收时强制核对）：**

| 规则 | 禁止 | 正确 |
|------|------|------|
| VR-MIS-01 | EP002 失败标 `empty_response` | `network_error` · EP002-NET |
| VR-MIS-02 | EP001 成功空列表标 `network_error` | `empty_response` · ER-VAL |
| VR-MIS-03 | retry `empty_response` 沿用 EP002-NET | 迁移 ER-VAL · `acceptable_edge` |
| VR-MIS-04 | retry 仍 EP002 失败归入 ER-VAL | 保留 EP002-NET · `unresolved_failed` |
| VR-MIS-05 | 与 ER-VAL requery 混批 | 独立 universe · 独立 output root |

---

## 6. Acceptance Rules（cite validation_rules）

> 适用 gate：`bd2e624_isolated_retry_execution_gate`（**仅** isolated retry run · 不影响 slice2 主 gate retroactively）

### 6.1 PASS_WITH_CAVEAT（retry 执行验收通过）

须同时满足 validation rules §3.1 全部条件，核心摘要：

| # | 条件 |
|---|------|
| 1 | universe = 1/1 BD2E624 |
| 2 | 写入隔离 output root 成功 |
| 3 | CNINFO ≤ 批准 cap（≤ **2**） |
| 4 | `retrieval_status ∈ {found, empty_response}` |
| 5 | notes **不含** `EP002 orgId resolution failed` |
| 6 | PDF/OCR/DB/MinIO/RAG = 0 |

| retrieval_status | retry disposition | cumulative 影响（separate merge closure） |
|------------------|-------------------|-------------------------------------------|
| `found` | recovered | acceptable +1 → 300/300 · fuller 797→798 |
| `empty_response` | recovered_as_edge · ER-VAL | acceptable +1 · caveat 保留 |

### 6.2 FAIL_REVIEW_REQUIRED（retry 执行验收失败）

| 触发 | 后续 |
|------|------|
| `retrieval_status = network_error` | 保留 deferred · EP002-NET · retry_vN side-track ledger |
| notes 仍含 `EP002 orgId resolution failed` | 同上 |
| misclassification（VR-MIS-* 违反） | fail · 须人工 reclassify |
| write-block / scope / cap 违规 | abort |

**仍失败时：** slice2 主 merge closure gate **保持** `PASS_WITH_CAVEAT`（299/300 不变）· 不得隐藏 unresolved。

### 6.3 禁止 bare PASS

- retry 成功 → `PASS_WITH_CAVEAT`（非 bare PASS）
- retry 失败 → `FAIL_REVIEW_REQUIRED`
- slice2 主 gate 不因 retry alone 升为 bare PASS（8 ER-VAL caveat 仍保留）

---

## 7. Merge Closure — Deferred Separate Task

> **本包不执行 merge closure。** live 验收 PASS_WITH_CAVEAT 后，由 **separate merge closure task** 执行 VR-MRG-01..06：

| 规则 | 动作 |
|------|------|
| VR-MRG-01 | 移除 unresolved ledger BD2E624 行（仅 retry PASS） |
| VR-MRG-02 | 更新 edge-case classification row 10 |
| VR-MRG-03 | cumulative fuller 797 → 798 |
| VR-MRG-04 | 不得 retroactive 修改 slice2 主 merge closure |
| VR-MRG-05 | empty_response 恢复 → 追加 ER-VAL taxonomy_tag |
| VR-MRG-06 | 仍 network_error → unresolved ledger 不变 · retry_vN 追加 |

---

## 8. Approval Workflow

| 步骤 | 状态 | 说明 |
|------|------|------|
| 1 | **done** | offline triage（B-GEN-20260714-04 前置） |
| 2 | **done** | validation rules（B-GEN-20260714-05） |
| 3 | **done** | 本 prep 包（B-GEN-20260714-06） |
| 4 | **pending** | runner dry-run 1/1 planned_ok（PC-BD2E-013 · CNINFO=0） |
| 5 | **blocked** | post-integration HOLD 解除（PC-BD2E-005） |
| 6 | **partial** | human live 执行短语（PC-BD2E-006 · prep 已批 · live phrase 待补） |
| 7 | **blocked** | controller approval queue 条目（PC-BD2E-007） |
| 8 | **pending** | isolated retry live（separate task · CNINFO ≤ 2） |
| 9 | **deferred** | merge closure（separate task · post-live only） |

**Live 批准短语（示意 · 须 human 显式发出）：**

```text
I approve B-class BD2E624 isolated retry live metadata validation.
```

---

## 9. Deliverables（本包）

| 工件 | 路径 |
|------|------|
| retry plan | `outputs/validation/cninfo_b_class_bd2e624_isolated_retry_plan_20260714.md`（本文件） |
| universe CSV | `outputs/validation/cninfo_b_class_bd2e624_isolated_retry_universe_20260714.csv` |
| command draft | `outputs/validation/cninfo_b_class_bd2e624_isolated_retry_command_draft_20260714.md` |
| precheck status | `outputs/validation/cninfo_b_class_bd2e624_isolated_retry_precheck_status_20260714.csv` |

---

## 10. Gate & Labels

```text
task_id = B-GEN-20260714-06
b_class_bd2e624_isolated_retry_prep_gate = PASS_OFFLINE
bd2e624_disposition = deferred_unresolved_failed（baseline 不变）
bd2e624_retry_approved_for_live = no
slice2_main_gate = PASS_WITH_CAVEAT（保持不变）
cninfo_calls_this_package = 0
live_calls_this_package = 0
```

**NOT verified** · **NOT production_ready** · **NOT approved for live CNINFO** · **NOT committed** · **NOT pushed**
