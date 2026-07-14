# CNINFO B 类 Cross-Slice ER-VAL Index

_生成时间：2026-07-14 · offline index/consolidate · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** cross-slice mission-level index for `empty_response` acceptable_edge · **NOT verified** · **NOT production_ready**

---

## 1. Scope & Task

| 项 | 值 |
|----|-----|
| task_id | **B-GEN-20260714-04** |
| cohort | `next_scale_slice1` + `fuller_next_slice2` |
| edge universe | **16** `empty_response` · `acceptable_edge` |
| taxonomy family | **ER-VAL**（Valid Empty Corpus） |
| excluded | **BD2E624**（`network_error` · deferred）— cite only · 不重做 triage |
| excluded | slice1 **BD2E201**（`not_found`）— 非 `empty_response` · 不在本 index |
| ledger | [cross-slice ER-VAL ledger](cninfo_b_class_cross_slice_erval_ledger_20260714.csv)（**16 rows**） |

**边界：** 本包仅索引/consolidate 两 slice 共 16 例 `empty_response`；不升级 gate · 不 force-resolve · 不触发 live · 不重做 slice2-only taxonomy（B-GEN-20260714-03）。

---

## 2. Source Lineage

| slice | cohort | source artifact | rows |
|-------|--------|-----------------|------|
| slice1 | `next_scale_slice1` | [edge-case triage ledger](cninfo_b_class_erad_next_scale_slice1_edge_case_triage_ledger.csv) rows 3–10 | **8** |
| slice1 | — | [effective accepted ledger](cninfo_b_class_erad_next_scale_slice1_effective_accepted_ledger.csv)（EP004/EP005 端点映射） | taxonomy 派生 |
| slice1 | — | [merge closure decision](cninfo_b_class_erad_next_scale_slice1_merge_closure_decision.md) §Edge-Case Disposition | rationale |
| slice2 | `fuller_next_slice2` | [empty_response edge ledger](cninfo_b_class_empty_response_edge_ledger_20260714.csv) | **8** |
| slice2 | — | [empty_response edge taxonomy](cninfo_b_class_empty_response_edge_taxonomy_20260714.md)（B-GEN-20260714-03） | taxonomy 定义 |

---

## 3. Taxonomy（引用 run3 · 不重复分类）

根类 **ER-VAL**：`retrieval_status=empty_response` · EP001 orgId 成功 · 目标端点 HTTP 成功但公告列表为空 · `empty_but_valid` → `accept_with_caveat`。

| taxonomy_tag | 条件 | slice1 | slice2 | **total** |
|--------------|------|--------|--------|-----------|
| **ER-VAL-EP004-PERIODIC** | EP004 空列表 · `periodic_report` | **6** | **6** | **12** |
| **ER-VAL-EP005-GENERAL** | EP005 空列表 · `general_announcement` | **2** | **2** | **4** |
| **合计** | | **8** | **8** | **16** |

两 slice 子类比例一致（75% EP004 / 25% EP005），支持跨 slice 可复现模式信号。

---

## 4. Cross-Slice Ledger（摘要）

### 4.1 next_scale_slice1（8）

| case_id | company_code | taxonomy_tag | disposition | live_required |
|---------|--------------|--------------|-------------|---------------|
| BD2E203 | 000562 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E204 | 000569 | ER-VAL-EP005-GENERAL | accept_with_caveat | no |
| BD2E245 | 001233 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E249 | 001285 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E377 | 600253 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E388 | 600357 | ER-VAL-EP005-GENERAL | accept_with_caveat | no |
| BD2E445 | 600842 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E463 | 601026 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |

### 4.2 fuller_next_slice2（8）

| case_id | company_code | taxonomy_tag | disposition | live_required |
|---------|--------------|--------------|-------------|---------------|
| BD2E537 | 002710 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E725 | 301449 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E738 | 301583 | ER-VAL-EP005-GENERAL | accept_with_caveat | no |
| BD2E739 | 301584 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E743 | 301638 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E745 | 301669 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |
| BD2E746 | 301687 | ER-VAL-EP005-GENERAL | accept_with_caveat | no |
| BD2E751 | 601206 | ER-VAL-EP004-PERIODIC | accept_with_caveat | no |

完整机器可读行见 [ledger CSV](cninfo_b_class_cross_slice_erval_ledger_20260714.csv)。

---

## 5. Disposition Summary（跨 slice 统一）

| 字段 | 16 例共性 |
|------|-----------|
| classification | `acceptable_edge` |
| disposition | `accept_with_caveat` |
| live_required | **no**（16/16） |
| retry_again | **no**（两 slice merge closure 均已收口） |
| quality_status | `needs_review` |
| lineage_status | `needs_review` |
| gate role | 计入 acceptable · **非 failed blocker** |

### 5.1 Deferred / Out-of-Scope（cite only）

| case_id | slice | 状态 | 与本 index 关系 |
|---------|-------|------|-----------------|
| BD2E624 | fuller_next_slice2 | `network_error` · EP002 · deferred | **EP002-NET** 族 · 与 ER-VAL 互斥 · 见 [bd2e624 triage](cninfo_b_class_bd2e624_offline_triage_20260714.md) |
| BD2E201 | next_scale_slice1 | `not_found` · accept_with_caveat | **非** `empty_response` · 不在本 16 行内 |

---

## 6. Counts

```text
total_empty_response_edges     = 16
slice1_count                   = 8
slice2_count                   = 8
ER-VAL-EP004-PERIODIC          = 12  (slice1=6, slice2=6)
ER-VAL-EP005-GENERAL           = 4   (slice1=2, slice2=2)
accept_with_caveat             = 16
live_required_yes              = 0
live_required_no               = 16
deferred_blocker_cited         = BD2E624
excluded_not_found             = BD2E201
cninfo_calls_this_package      = 0
live_calls_this_package        = 0
```

---

## 7. Gate & Labels（本包）

```text
b_class_cross_slice_erval_index_gate = PASS_OFFLINE
taxonomy_family = ER-VAL
ledger_rows = 16
cninfo_calls_this_package = 0
live_calls_this_package = 0
```

**NOT verified** · **NOT production_ready** · **NOT approved for live** · **NOT committed** · **NOT pushed**

---

## 8. Progress Impact

本包将 next-scale slice1 与 fuller slice2 各 8 例 `empty_response` 合并为单一跨 slice **ER-VAL** 索引（共 **16** 行），统一 taxonomy_tag（`ER-VAL-EP004-PERIODIC` ×12 · `ER-VAL-EP005-GENERAL` ×4）与 disposition（16/16 `accept_with_caveat` · `live_required=no`）。两 slice 子类比例一致，表明空语料边缘在 Era D 扩规模中可复现，宜作为 mission event quality 的长期 caveat 类而非单 slice 噪声。BD2E624（EP002 network_error）与 BD2E201（not_found）保持 out-of-scope；本包不阻塞既有 `PASS_WITH_CAVEAT` gate，亦不触发任何 CNINFO 调用。Controller 可据此 index 做 mission 级边缘台账引用，日后若 human 批准 isolated requery，须按 slice 分组、隔离 output root，不得与 BD2E624 retry 混批。
