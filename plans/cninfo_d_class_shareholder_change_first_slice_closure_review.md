# CNINFO D 类 shareholder_change First-Slice — Closure Review

_生成时间：2026-07-15_

> **性质：** 离线 closure review only · **无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **无 commit 执行**

**关联 gate：** `d_class_shareholder_change_first_slice_execution_gate = PASS_WITH_CAVEAT`

---

## 1. Objective

对 isolated shareholder_change first-slice live（S5）结果进行正式离线收口评审，确认 5-case universe 稀疏日 `empty_but_valid` 语义、登记 DSC004 track-level caveat、产出 closure metrics / effective result，并为 commit boundary 提供人工决策输入。

**本评审不：** 重跑 DSC001–DSC005 · 重开 DLC006R / closed D tracks · 将 `empty_but_valid` 升级为 `found` / `captured_normal` · 标记 verified / production_ready · 执行 commit / push。

---

## 2. Live Result Recap（只读）

| 项 | 值 |
|----|-----|
| mode | `--shareholder-change-first-slice --live` |
| approval | `--approve-d-class-shareholder-change-first-slice` |
| universe | DSC001–DSC005（**5**）· lock sha256 `49e6ece0…a3c402` |
| output root | `outputs/validation/cninfo_d_class_shareholder_change_first_slice/` |
| component | **shareholder_change** only |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| query | **type=inc** + **tdate=2026-07-03** |
| total CNINFO（prior live） | **5** |
| request cap | **≤ 20** |
| PDF/OCR/extraction | **0** |
| DB/MinIO/RAG | **0** |

| case_id | company | market | requests | retrieval | records | acceptable | failure_type |
|---------|---------|--------|----------|-----------|---------|------------|--------------|
| DSC001 | 000550 江铃汽车 | szse_main | 1 | empty_but_valid | 0 | **yes** | — |
| DSC002 | 000895 双汇发展 | szse_main | 1 | empty_but_valid | 0 | **yes** | — |
| DSC003 | 600000 浦发银行 | sse_main | 1 | empty_but_valid | 0 | **yes** | — |
| DSC004 | 002415 海康威视 | szse_main | 1 | empty_but_valid | 0 | **no** | expectation_mismatch |
| DSC005 | 601988 中国银行 | sse_main | 1 | empty_but_valid | 0 | **yes** | — |

**汇总：** acceptable **4/5** · empty_but_valid **5** · found **0** · failed **0** · needs_review **0** · unresolved blocking **0**

只读输入：[live report](../outputs/validation/cninfo_d_class_shareholder_change_first_slice/reports/d_class_shareholder_change_first_slice_live_report.csv) · [quality report](../outputs/validation/cninfo_d_class_shareholder_change_first_slice/reports/d_class_shareholder_change_first_slice_quality_report.csv) · [outcome ledger](../outputs/validation/cninfo_d_class_shareholder_change_first_slice_live_outcome_ledger.csv) · [S5 live evidence](../outputs/validation/cninfo_d_class_shareholder_change_s5_live_20260715.md)

---

## 3. Sparse-Day Semantics

Anchor **`tdate=2026-07-03`** 上全宇宙公司级零行，单 `type=inc` tdate 探针后均为 `empty_but_valid`。

| 项 | 结论 |
|----|------|
| endpoint failure | **no** — 一致合法空态（http_status=200 · record_count=0） |
| treat empty_but_valid as failure | **no**（当 expectation 允许 empty） |
| expectation mix | DSC001–003 允许 empty；DSC005 为 empty control；DSC004 不允许 empty |
| denser-day rerun | **deferred** — 非 closure blocker |

---

## 4. DSC004 Caveat（诚实登记）

| 项 | 内容 |
|----|------|
| failure_class | `expectation_mismatch_on_sparse_day` |
| root cause | **expectation-label mismatch**, not endpoint failure |
| evidence | DSC004 tagged `captured_normal_or_needs_review` but anchor day returned 0 rows like all other cases |
| quality policy | 合法 `empty_but_valid`（**未**伪升级为 found / captured_normal） |
| disposition | **accept_with_caveat** at closure · ledger entry retained |
| blocking | **no** — execution gate already `PASS_WITH_CAVEAT` at 4/5（阈值 ≥3/5） |

---

## 5. Scope Confirmation

| 约束 | 状态 |
|------|------|
| component = shareholder_change only | **yes** |
| metadata / structured-table scoped | **yes** |
| 688671 excluded | **yes** |
| 301259 / DLC006R excluded · **未重开** | **yes** |
| equity_pledge / block_trade / RSU closed | **yes** |
| no DLC003R / DLC006R rerun | **yes** |
| no disclosure→captured_normal | **yes** |
| no verified / production_ready | **yes** |
| CNINFO this round | **0** |

---

## 6. Closure Decision Preview

**CLOSE with caveat — NOW.**

```text
d_class_shareholder_change_first_slice_closure_gate = PASS_WITH_CAVEAT
```

**NOT bare PASS** · **NOT verified** · **NOT production_ready**

---

## 7. Artifacts

| 项 | 路径 |
|----|------|
| S5 closure evidence | [cninfo_d_class_shareholder_change_s5_closure_20260715.md](../outputs/validation/cninfo_d_class_shareholder_change_s5_closure_20260715.md) |
| closure matrix | [cninfo_d_class_shareholder_change_s5_closure_matrix_20260715.csv](../outputs/validation/cninfo_d_class_shareholder_change_s5_closure_matrix_20260715.csv) |
| closure metrics | [cninfo_d_class_shareholder_change_first_slice_closure_metrics.csv](../outputs/validation/cninfo_d_class_shareholder_change_first_slice_closure_metrics.csv) |
| effective result | [cninfo_d_class_shareholder_change_first_slice_effective_result.csv](../outputs/validation/cninfo_d_class_shareholder_change_first_slice_effective_result.csv) |
| caveat ledger | [cninfo_d_class_shareholder_change_first_slice_final_caveat_ledger.csv](../outputs/validation/cninfo_d_class_shareholder_change_first_slice_final_caveat_ledger.csv) |
| closure decision | [cninfo_d_class_shareholder_change_first_slice_closure_decision.md](../outputs/validation/cninfo_d_class_shareholder_change_first_slice_closure_decision.md) |
