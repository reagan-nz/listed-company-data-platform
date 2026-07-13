# CNINFO D 类 equity_pledge First-Slice — Closure Review

_生成时间：2026-07-10_

> **性质：** 离线 closure review only · **无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **无 commit 执行**

**关联 gate：** `d_class_equity_pledge_first_slice_execution_gate = PASS_WITH_CAVEAT`

---

## 1. Objective

对 isolated equity_pledge first-slice live 结果进行正式离线收口评审，确认 5-case universe 稀疏日 `empty_but_valid` 语义、登记 DEP004 track-level caveat、产出 closure metrics / effective result，并为 commit boundary 提供人工决策输入。

**本评审不：** 重跑 DEP001–DEP005 · 重开 closed D tracks · 将 `empty_but_valid` 升级为 `found` / `captured_normal` · 标记 verified / production_ready · 执行 commit。

---

## 2. Live Result Recap

| 项 | 值 |
|----|-----|
| mode | `--equity-pledge-first-slice --live` |
| approval | **I approve D-class equity_pledge first-slice live validation.** |
| universe | [universe draft](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft.csv)（**5 rows** · DEP001–DEP005） |
| output root | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/` |
| component | **equity_pledge** only |
| endpoint | `equityPledge/list` |
| anchor_tdate | **2026-07-03** |
| total CNINFO（prior live） | **5** |
| request cap | **≤ 20** |
| PDF/OCR/extraction | **0** |
| DB/MinIO/RAG | **0** |

| case_id | company | market | requests | retrieval | records | acceptable |
|---------|---------|--------|----------|-----------|---------|------------|
| DEP001 | 688981 中芯国际 | star | 1 | empty_but_valid | 0 | **yes** |
| DEP002 | 000895 双汇发展 | szse_main | 1 | empty_but_valid | 0 | **yes** |
| DEP003 | 600000 浦发银行 | sse_main | 1 | empty_but_valid | 0 | **yes** |
| DEP004 | 002415 海康威视 | szse_main | 1 | empty_but_valid | 0 | **no** |
| DEP005 | 601988 中国银行 | sse_main | 1 | empty_but_valid | 0 | **yes** |

**汇总：** acceptable **4/5** · empty_but_valid **5** · found **0** · failed **0** · needs_review **0** · unresolved blocking **0**

报告（只读输入）：[live report](../outputs/validation/cninfo_d_class_equity_pledge_first_slice/reports/d_class_equity_pledge_first_slice_live_report.csv) · [execution summary](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_execution_summary.md) · [outcome ledger](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_outcome_ledger.csv)

---

## 3. Sparse-Day Semantics

Anchor **`tdate=2026-07-03`** 上全宇宙公司级零行，单 tdate 探针后均为 `empty_but_valid`。

| 项 | 结论 |
|----|------|
| endpoint failure | **no** — 一致合法空态 |
| treat empty_but_valid as failure | **no** |
| expectation mix | 已吸收 block_trade DBT002 / RSU 教训（无 sole `captured_normal_candidate`） |
| denser-day rerun | **deferred** — 非 closure blocker |

---

## 4. DEP004 Caveat

| 项 | 内容 |
|----|------|
| failure_class | `expectation_mismatch_on_sparse_day` |
| root cause | **expectation-label mismatch**, not endpoint failure |
| evidence | DEP004 tagged `captured_normal_or_needs_review` but anchor day returned 0 rows like all other cases |
| disposition | **accept_with_caveat** at closure · ledger entry retained |
| blocking | **no** — execution gate already `PASS_WITH_CAVEAT` at 4/5 |

---

## 5. Scope Confirmation

| 约束 | 状态 |
|------|------|
| component = equity_pledge only | **yes** |
| metadata / structured-table scoped | **yes** |
| 688671 excluded | **yes** |
| 301259 excluded | **yes** |
| known-event / margin_trading / disclosure_schedule / block_trade / RSU closed | **yes** |
| no DLC003R / DLC006R rerun | **yes** |
| no disclosure→captured_normal | **yes** |
| no verified / production_ready | **yes** |

---

## 6. Closure Decision Preview

**CLOSE with caveat — NOW.**

```text
d_class_equity_pledge_first_slice_closure_gate = PASS_WITH_CAVEAT
```

**NOT bare PASS** · **NOT verified**

---

## 7. Artifacts

| 项 | 路径 |
|----|------|
| closure metrics | [cninfo_d_class_equity_pledge_first_slice_closure_metrics.csv](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_closure_metrics.csv) |
| effective result | [cninfo_d_class_equity_pledge_first_slice_effective_result.csv](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_effective_result.csv) |
| caveat ledger | [cninfo_d_class_equity_pledge_first_slice_final_caveat_ledger.csv](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_final_caveat_ledger.csv) |
| closure decision | [cninfo_d_class_equity_pledge_first_slice_closure_decision.md](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_closure_decision.md) |
