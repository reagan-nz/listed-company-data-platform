# CNINFO D 类 restricted_shares_unlock First-Slice — Closure Review

_生成时间：2026-07-10_

> **性质：** 离线 closure review only · **无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **无 commit 执行**

**关联 gate：** `d_class_restricted_shares_unlock_first_slice_execution_gate = PASS_WITH_CAVEAT`

---

## 1. Objective

对 isolated restricted_shares_unlock first-slice live 结果进行正式离线收口评审，确认 5-case universe 稀疏日 `empty_but_valid` 语义、登记 track-level caveat、产出 closure metrics / effective result，并为 commit boundary 提供人工决策输入。

**本评审不：** 重跑 DRU001–DRU005 · 重开 closed D tracks · 将 `empty_but_valid` 升级为 `found` / `captured_normal` · 标记 verified / production_ready · 执行 commit。

---

## 2. Live Result Recap

| 项 | 值 |
|----|-----|
| mode | `--restricted-shares-unlock-first-slice --live` |
| approval | **I approve D-class restricted_shares_unlock first-slice live validation.** |
| universe | [universe draft](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv)（**5 rows** · DRU001–DRU005） |
| output root | `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/` |
| component | **restricted_shares_unlock** only |
| endpoint | `liftBan/detail` |
| anchor_tdate | **2026-06-08** |
| total CNINFO（prior live） | **15** |
| request cap | **≤ 20** |
| PDF/OCR/extraction | **0** |
| DB/MinIO/RAG | **0** |

| case_id | company | market | requests | retrieval | records | acceptable |
|---------|---------|--------|----------|-----------|---------|------------|
| DRU001 | 300009 安科生物 | chinext | 3 | empty_but_valid | 0 | **yes** |
| DRU002 | 000895 双汇发展 | szse_main | 3 | empty_but_valid | 0 | **yes** |
| DRU003 | 600000 浦发银行 | sse_main | 3 | empty_but_valid | 0 | **yes** |
| DRU004 | 002415 海康威视 | szse_main | 3 | empty_but_valid | 0 | **yes** |
| DRU005 | 688981 中芯国际 | star | 3 | empty_but_valid | 0 | **yes** |

**汇总：** acceptable **5/5** · empty_but_valid **5** · found **0** · failed **0** · needs_review **0** · unresolved blocking **0**

报告（只读输入）：[live report](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/reports/d_class_restricted_shares_unlock_first_slice_live_report.csv) · [execution summary](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_live_execution_summary.md) · [outcome ledger](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_per_case_outcome_ledger.csv)

---

## 3. Sparse-Day Semantics

Anchor **`tdate=2026-06-08`** 上全宇宙公司级零行，multi-probe 各耗尽 **3** 请求后仍为 `empty_but_valid`。

| 项 | 结论 |
|----|------|
| endpoint failure | **no** — 一致合法空态 |
| treat as failure | **no** |
| expectation mix | 已吸收 block_trade DBT002 教训（无 sole `captured_normal_candidate`） |
| denser-day rerun | **deferred** — 非 closure blocker |

---

## 4. Scope Confirmation

| 约束 | 状态 |
|------|------|
| component = restricted_shares_unlock only | **yes** |
| metadata / structured-table scoped | **yes** |
| 688671 excluded | **yes** |
| 301259 excluded | **yes** |
| known-event / margin_trading / disclosure_schedule / block_trade closed | **yes** |
| no DLC003R / DLC006R rerun | **yes** |
| no disclosure→captured_normal | **yes** |
| no verified / production_ready | **yes** |

---

## 5. Closure Decision Preview

**CLOSE with caveat — NOW.**

```text
d_class_restricted_shares_unlock_first_slice_closure_gate = PASS_WITH_CAVEAT
```

**NOT bare PASS** · **NOT verified**

---

## 6. Artifacts

| 项 | 路径 |
|----|------|
| closure metrics | [cninfo_d_class_restricted_shares_unlock_first_slice_closure_metrics.csv](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_closure_metrics.csv) |
| effective result | [cninfo_d_class_restricted_shares_unlock_first_slice_effective_result.csv](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_effective_result.csv) |
| caveat ledger | [cninfo_d_class_restricted_shares_unlock_first_slice_final_caveat_ledger.csv](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_final_caveat_ledger.csv) |
| closure decision | [cninfo_d_class_restricted_shares_unlock_first_slice_closure_decision.md](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_closure_decision.md) |
