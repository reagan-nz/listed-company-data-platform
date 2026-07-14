# CNINFO B 类 BD2E624 — Offline Validation Rules & Acceptance Pack

_生成时间：2026-07-14 · offline validation rules only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** future isolated-retry acceptance rules · **NOT verified** · **NOT production_ready** · **NOT approved for live**

**前置（cite only · 不重做 triage）：** [BD2E624 offline triage](cninfo_b_class_bd2e624_offline_triage_20260714.md)

**对比源（network_error ≠ empty_response）：**
- [empty_response edge taxonomy](cninfo_b_class_empty_response_edge_taxonomy_20260714.md)（B-GEN-20260714-03）
- [cross-slice ER-VAL index](cninfo_b_class_cross_slice_erval_index_20260714.md)（B-GEN-20260714-04）
- [edge-case classification](cninfo_b_class_erad_fuller_next_slice2_edge_case_classification.csv)（rows 2–10）

---

## 1. Scope & Case Anchor

| 字段 | 值 | 证据 |
|------|-----|------|
| task_id | **B-GEN-20260714-05** | controller task queue |
| case_id | **BD2E624** | unresolved ledger（1 row） |
| company_code | **300778**（新城市） | live report row 125 |
| cohort | `fuller_next_slice2` | candidate universe row 125 |
| session（原始） | Session 1 | session1 live log |
| baseline retrieval_status | `network_error` | unresolved ledger · live report |
| root_cause_family | **EP002-NET** · `ep002_orgid_network_error` | edge-case classification row 10 |
| baseline disposition | `unresolved_failed` · **deferred** | triage · merge closure |
| taxonomy 族 | **EP002-NET** | 与 **ER-VAL**（`empty_response`）**互斥** |

**边界：** 本包仅定义 **日后 human 批准 isolated retry 后** 的验收规则与 gate 判定；不执行 retry · 不修改 slice2 主 merge closure · 不 offline force-resolve。

---

## 2. Status Taxonomy — network_error vs empty_response（强制对比）

### 2.1 判定树（retry 后 parser 须保留）

```text
EP002 orgId resolution
├── FAIL（network/timeout/HTTP error）→ retrieval_status = network_error
│   └── root_cause_family = ep002_orgid_network_error · EP002-NET 族
│   └── disposition = unresolved_failed · NOT acceptable
│
└── SUCCESS → EP001 成功 → 目标端点 EP004/EP005
    ├── HTTP 成功 · 公告列表非空 → retrieval_status = found
    │   └── disposition = accepted_effective · counts toward acceptable
    │
    └── HTTP 成功 · 公告列表为空 → retrieval_status = empty_response
        └── root_cause_family = ER-VAL（EP004-PERIODIC 或 EP005-GENERAL）
        └── disposition = acceptable_edge · accept_with_caveat · counts toward acceptable
        └── 见 slice2 八例 ER-VAL（如 BD2E537）— 非 failed blocker
```

### 2.2 互斥规则（misclassification guard）

| 规则 ID | 条件 | 禁止 | 正确分类 |
|---------|------|------|----------|
| **VR-MIS-01** | EP002 未成功 · notes 含 `EP002 orgId resolution failed` | 不得标 `empty_response` | `network_error` · EP002-NET |
| **VR-MIS-02** | EP001 成功 · 目标端点空列表 · notes 含 `no announcements in response` | 不得标 `network_error` | `empty_response` · ER-VAL |
| **VR-MIS-03** | retry 结果为 `empty_response` | 不得沿用 EP002-NET deferred 标签 | 迁移至 ER-VAL · `acceptable_edge` |
| **VR-MIS-04** | retry 仍为 EP002 失败 | 不得归入 ER-VAL ledger / cross-slice index | 保留 EP002-NET · `unresolved_failed` |
| **VR-MIS-05** | 任意结果 | 不得与 16 例 ER-VAL requery 混批 | BD2E624 独立 universe · 独立 output root |

### 2.3 对比锚点（slice2 同 cohort）

| case_id | company_code | retrieval_status | 族 | closure 角色 | 证据 |
|---------|--------------|------------------|-----|--------------|------|
| **BD2E624** | 300778 | `network_error` | EP002-NET | **unresolved_failed** · 不计 acceptable | edge-case row 10 · live report |
| BD2E537 | 002710 | `empty_response` | ER-VAL-EP004-PERIODIC | **acceptable_edge** · 计入 299 | edge-case row 2 · session1 report |
| BD2E625 | 300782 | `found` | — | accepted_effective | session1 live log（BD2E624 邻接 case · 同 session 成功对照） |

**关键差异：** BD2E624 失败于 **EP002 orgId 解析阶段**（未到达 EP004/EP005 空列表语义）；BD2E537 等八例 **EP001 已成功**，空列表为有效语料信号。

---

## 3. Retry Execution Acceptance Rules

> 适用对象：`bd2e624_isolated_retry_execution_gate`（**仅** isolated retry run · 不影响 slice2 主 gate  retroactively）

### 3.1 PASS_WITH_CAVEAT（retry 执行验收通过）

须 **同时** 满足：

| # | 条件 | 说明 |
|---|------|------|
| 1 | universe = **1/1** BD2E624 | 无扩 universe · 无混批 |
| 2 | isolated output root 写入成功 | 不得 mutate slice2 主 report / quality / merge closure |
| 3 | CNINFO request count ≤ 批准 cap（建议 ≤ **2**） | 单 case EP002→EP001 链 |
| 4 | `retrieval_status ∈ {found, empty_response}` | EP002 orgId **已成功** |
| 5 | `failure_type` 为空或非 network_error | 无 EP002 持久失败 |
| 6 | notes **不含** `EP002 orgId resolution failed` | 与 baseline 对比须显式变化 |
| 7 | PDF/OCR/DB/MinIO/RAG = **0** | metadata only |
| 8 | 未升级 verified / production_ready | 治理红线 |

**子情形：**

| retrieval_status | quality 期望 | retry disposition | cumulative 影响 |
|------------------|--------------|-------------------|-----------------|
| `found` | `needs_review` 或 `pass`（按 runner 规则） | **recovered** · 移出 unresolved | acceptable +1 → **300/300** · staged fuller **797→798** |
| `empty_response` | `needs_review` | **recovered_as_edge** · ER-VAL 子类 | acceptable +1（与八例 ER-VAL 同口径）· caveat 保留 |

### 3.2 FAIL_REVIEW_REQUIRED（retry 执行验收失败）

任一触发即 **fail**（retry 轨 · 非 slice2 主 gate 降级）：

| # | 条件 | 后续 disposition |
|---|------|------------------|
| F1 | `retrieval_status = network_error` | 保留 deferred · EP002-NET · 入 retry_vN side-track ledger |
| F2 | notes 仍含 `EP002 orgId resolution failed` | 同 F1 |
| F3 | `failure_type = network_error` | 同 F1 |
| F4 | universe ≠ 1/1 或 case_id 非 BD2E624 | **abort** · 越权 scope |
| F5 | 写入 slice2 主 output root / scale-200 / slice1 / Phase3 根 | **abort** · write-block 违规 |
| F6 | CNINFO > 批准 cap | **abort** · cap 违规 |
| F7 | `retrieval_status ∈ {not_found, universe_validation_failed, unresolved}` 且非 empty_response | **needs_review** · 不得 auto-promote 为 acceptable |
| F8 | misclassification（§2.2 VR-MIS-* 任一违反） | **fail** · 须人工 reclassify 后重判 |

**F1–F3 仍失败时：** slice2 主 merge closure gate **保持** `PASS_WITH_CAVEAT`（299/300 acceptable 不变）· BD2E624 仍 deferred。

### 3.3 禁止 bare PASS

| 场景 | 判定 |
|------|------|
| retry 成功（found 或 empty_response） | retry execution → `PASS_WITH_CAVEAT`（非 bare PASS） |
| retry 失败（network_error） | retry execution → `FAIL_REVIEW_REQUIRED` |
| slice2 主 gate | **不因 retry 成功 alone 升为 bare PASS**（8 ER-VAL caveat 仍保留） |
| 全局 | **never** verified · **never** production_ready |

---

## 4. Retry Merge / Closure Rules（separate task · post-live only）

> 仅当 §3.1 PASS_WITH_CAVEAT 成立后，由 **separate merge closure task** 执行；本包不执行。

| 规则 ID | 动作 | 条件 |
|---------|------|------|
| **VR-MRG-01** | 更新 unresolved ledger | 移除 BD2E624 行 **仅当** retry PASS |
| **VR-MRG-02** | 更新 edge-case classification row 10 | network_error → found 或 empty_response + 新 disposition |
| **VR-MRG-03** | cumulative fuller 计数 | 797 → **798**（found 或 empty_response 均 +1 acceptable） |
| **VR-MRG-04** | 不得 retroactive 修改 slice2 主 merge closure summary | 新 closure 包独立编号 |
| **VR-MRG-05** | empty_response 恢复 | 追加 ER-VAL taxonomy_tag · 可纳入 cross-slice index（separate index task） |
| **VR-MRG-06** | 仍 network_error | unresolved ledger **不变** · retry_vN ledger 追加一行 · 主 gate 不变 |

---

## 5. Offline Precheck Gate（本包）

执行 isolated retry live **之前**，[precheck checklist CSV](cninfo_b_class_bd2e624_offline_precheck_checklist_20260714.csv) 中 `required_before_retry=yes` 且 `status=ready` 的项须全部满足；任一 `blocked` → **禁止 live**。

---

## 6. Package Labels

```text
b_class_bd2e624_offline_validation_rules_gate = PASS_OFFLINE
bd2e624_retry_acceptance_rules_ready = yes
bd2e624_retry_approved = no
cninfo_calls_this_package = 0
live_calls_this_package = 0
```

**NOT verified** · **NOT production_ready** · **NOT approved for live** · **NOT committed** · **NOT pushed**

---

## 7. Evidence Lineage（read-only refs）

| artifact | path |
|----------|------|
| triage | `outputs/validation/cninfo_b_class_bd2e624_offline_triage_20260714.md` |
| unresolved ledger | `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_unresolved_case_ledger.csv` |
| live report | `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_report.csv` |
| quality JSON | `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/quality/BD2E624.json` |
| session1 log | `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_session1_live.log` |
| merge closure | `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_merge_closure_summary.md` |
| ER-VAL contrast | `outputs/validation/cninfo_b_class_empty_response_edge_taxonomy_20260714.md` |
| cross-slice index | `outputs/validation/cninfo_b_class_cross_slice_erval_index_20260714.md` |
| precheck checklist | `outputs/validation/cninfo_b_class_bd2e624_offline_precheck_checklist_20260714.csv` |
