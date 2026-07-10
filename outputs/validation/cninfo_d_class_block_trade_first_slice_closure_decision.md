# CNINFO D 类 block_trade First-Slice — Closure Decision

_生成时间：2026-07-10_

> **性质：** 离线 closure 决策 · **CNINFO = 0** · **无 live** · **不是 verified**

---

## 1. Primary Decision

**CLOSE the block_trade first-slice track with caveat — NOW.**

| 项 | 决策 |
|----|------|
| closure gate | `d_class_block_trade_first_slice_closure_gate = PASS_WITH_CAVEAT` |
| effective acceptable | **4/5** |
| sparse-day semantics | **confirmed** across all 5 cases on `tdate=2026-07-03` |
| endpoint consistency | **yes** — 0 rows for every case; no http_error / blocked |
| DBT002 | **non-blocking caveat** — expectation-label mismatch only |
| verified / production_ready | **no** |
| bare PASS | **no** |

---

## 2. Rationale

1. Execution gate **`PASS_WITH_CAVEAT`** already met at isolated live（≥3/5 acceptable）。
2. All five cases demonstrate legal **`empty_but_valid`** on a sparse anchor day — consistent with DLC002-style control evidence（DBT001）and quality policy.
3. DBT002 failure is **`expectation_mismatch_on_sparse_day`**, not endpoint failure. The case was tagged `captured_normal_candidate` while the shared anchor returned zero rows for every company.
4. No unresolved blocking cases remain for first-slice sign-off. Ledger entry retained for audit.

---

## 3. DBT002 Disposition

| 项 | 值 |
|----|-----|
| failure_class | `expectation_mismatch_on_sparse_day` |
| closure disposition | **accept_with_caveat** |
| blocking closure | **no** |
| ledger | [unresolved_case_ledger.csv](cninfo_d_class_block_trade_first_slice_unresolved_case_ledger.csv) |

---

## 4. Optional Later Actions（NOT in this task）

以下选项 **不在本任务执行** · **不自动运行** · 需单独批准：

### a) Offline retag DBT002 `expected_behavior`

| 项 | 内容 |
|----|------|
| action | 将 DBT002 从 `captured_normal_candidate` 改为 `captured_normal_or_empty_but_valid` 或 `empty_but_valid` |
| scope | universe CSV + offline docs only |
| prerequisite | 人工决策 · 无 CNINFO |
| apply to production runners | **only if separately approved** |

### b) Separate approved probe on known nonzero block_trade tdate

| 项 | 内容 |
|----|------|
| action | 在已知有 block_trade 记录的 tdate 上执行单独批准的小探针 |
| scope | 新 slice / 新 approval phrase · 非 first-slice rerun |
| prerequisite | 人工批准 · 独立 task |
| recommendation now | **deferred** — not required for first-slice closure |

**Closure decision:** optional nonzero-tdate probe is **deferred**, not recommended for immediate execution.

---

## 5. Frozen Tracks（保持 closed）

- known-event replacement / targeted probe
- margin_trading first-slice（commit **`116f875`**）
- disclosure_schedule first-slice（commit **`d37ce0a`**）
- A/B/C live roots

---

## 6. Gate Sign-Off

```text
d_class_block_trade_first_slice_closure_gate = PASS_WITH_CAVEAT
d_class_block_trade_first_slice_execution_gate = PASS_WITH_CAVEAT
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

---

## 7. Next Step

见 [post-closure next-step recommendation](cninfo_d_class_block_trade_first_slice_post_closure_next_step_recommendation.md)。
